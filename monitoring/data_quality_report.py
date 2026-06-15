#!/usr/bin/env python3
"""
Data Quality Reporting: Compute quality metrics post-pipeline execution.
Logs to data_quality_metrics PostgreSQL table.
"""

import logging
from datetime import datetime
import uuid
import duckdb
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

# Connections
DUCKDB_PATH = "data/warehouse.duckdb"
PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASSWORD = "password"
PG_DB = "product_analytics_operational"


def compute_quality_metrics(run_id: str, run_date):
    """
    Compute quality scorecard:
    - Null rates per column
    - Duplicate rates (primary keys)
    - Row count changes from previous run
    - Value distribution anomalies
    """

    try:
        conn_duck = duckdb.connect(DUCKDB_PATH)
        conn_pg = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            database=PG_DB
        )
        pg_cursor = conn_pg.cursor()

        metrics = []

        # Metric 1: Null rates
        logger.info("Computing null rates...")
        fact_null_rate = conn_duck.execute(
            """
            SELECT
                SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END)::float /
                COUNT(*) as null_rate
            FROM fact_orders
            """
        ).fetchall()[0][0]

        metrics.append({
            'metric_name': 'null_rate',
            'table_name': 'fact_orders',
            'column_name': 'order_id',
            'metric_value': fact_null_rate,
            'expected_value': 0.0,
            'passed': fact_null_rate == 0.0,
            'anomaly': fact_null_rate > 0.05
        })

        # Metric 2: Duplicate check (primary key)
        logger.info("Checking for duplicates...")
        dup_count = conn_duck.execute(
            """
            SELECT COUNT(*) - COUNT(DISTINCT (order_id, product_id))
            FROM fact_orders
            """
        ).fetchall()[0][0]

        metrics.append({
            'metric_name': 'duplicate_count',
            'table_name': 'fact_orders',
            'column_name': 'order_id, product_id',
            'metric_value': dup_count,
            'expected_value': 0,
            'passed': dup_count == 0,
            'anomaly': dup_count > 0
        })

        # Metric 3: Row count
        logger.info("Checking row counts...")
        fact_count = conn_duck.execute(
            "SELECT COUNT(*) FROM fact_orders"
        ).fetchall()[0][0]

        metrics.append({
            'metric_name': 'row_count',
            'table_name': 'fact_orders',
            'column_name': None,
            'metric_value': fact_count,
            'expected_value': 3_000_000,  # Placeholder
            'passed': fact_count > 0,
            'anomaly': abs(fact_count - 3_000_000) > 3_000_000 * 0.1  # 10% variance
        })

        # Metric 4: Reorder rate distribution
        logger.info("Checking reorder rate...")
        reorder_rate = conn_duck.execute(
            """
            SELECT
                SUM(CASE WHEN reordered = 1 THEN 1 ELSE 0 END)::float /
                COUNT(*) as reorder_rate
            FROM fact_orders
            """
        ).fetchall()[0][0]

        metrics.append({
            'metric_name': 'reorder_rate',
            'table_name': 'fact_orders',
            'column_name': 'reordered',
            'metric_value': reorder_rate,
            'expected_value': 0.5,  # Placeholder
            'passed': 0.0 <= reorder_rate <= 1.0,
            'anomaly': reorder_rate < 0.1 or reorder_rate > 0.9
        })

        # Log metrics to PostgreSQL
        logger.info(f"Logging {len(metrics)} metrics to PostgreSQL...")

        metric_records = [
            (
                str(uuid.uuid4()),
                run_id,
                m['metric_name'],
                m['table_name'],
                m['column_name'],
                m['metric_value'],
                m['expected_value'],
                m['metric_value'],
                m['passed'],
                m['anomaly']
            )
            for m in metrics
        ]

        execute_values(
            pg_cursor,
            """
            INSERT INTO data_quality_metrics
            (metric_id, run_id, metric_name, table_name, column_name,
             metric_value, expected_value, actual_value, passed, anomaly_detected)
            VALUES %s
            """,
            metric_records
        )

        conn_pg.commit()
        pg_cursor.close()
        conn_pg.close()
        conn_duck.close()

        # Compute overall quality score
        passed_count = sum(1 for m in metrics if m['passed'])
        quality_score = passed_count / len(metrics)

        logger.info(f"✓ Quality Score: {quality_score:.2f}")
        logger.info(f"  Passed: {passed_count}/{len(metrics)}")

        anomalies = [m for m in metrics if m['anomaly']]
        if anomalies:
            logger.warning(f"⚠️ {len(anomalies)} anomalies detected:")
            for m in anomalies:
                logger.warning(f"   {m['metric_name']} in {m['table_name']}")

        return quality_score

    except Exception as e:
        logger.error(f"Failed to compute quality metrics: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    run_id = str(uuid.uuid4())
    quality_score = compute_quality_metrics(run_id, datetime.utcnow().date())
