#!/usr/bin/env python3
"""
Set up PostgreSQL operational database tables for pipeline tracking.
"""

import psycopg2
from psycopg2 import sql
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)

# PostgreSQL connection parameters (defaults for local)
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "dbname": "product_analytics_operational"
}


def setup_tables():
    """Create operational tables"""
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()

        # Create pipeline_runs table
        logger.info("Creating pipeline_runs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id UUID PRIMARY KEY,
                run_date DATE,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds INT,
                rows_processed INT DEFAULT 0,
                rows_failed INT DEFAULT 0,
                sla_met BOOLEAN,
                quality_score FLOAT,
                status VARCHAR DEFAULT 'pending',
                error_message TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create data_quality_metrics table
        logger.info("Creating data_quality_metrics table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_quality_metrics (
                metric_id UUID PRIMARY KEY,
                run_id UUID NOT NULL REFERENCES pipeline_runs(run_id),
                metric_name VARCHAR,
                table_name VARCHAR,
                column_name VARCHAR,
                metric_value FLOAT,
                expected_value FLOAT,
                actual_value FLOAT,
                passed BOOLEAN,
                anomaly_detected BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        logger.info("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pipeline_runs_date
            ON pipeline_runs(run_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_data_quality_runs
            ON data_quality_metrics(run_id)
        """)

        conn.commit()
        logger.info("✓ Operational tables created successfully")

        cursor.close()
        conn.close()

    except psycopg2.OperationalError as e:
        logger.error(f"Connection error: {e}")
        logger.warning("PostgreSQL not available. Skipping operational DB setup.")
        logger.warning("You can still use the pipeline with DuckDB warehouse.")
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

    return True


if __name__ == "__main__":
    success = setup_tables()
    sys.exit(0 if success else 1)
