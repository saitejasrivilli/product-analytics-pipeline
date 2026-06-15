#!/usr/bin/env python3
"""
SLA Monitoring: Check pipeline completion time against threshold.
Log to pipeline_runs PostgreSQL table.
"""

import logging
from datetime import datetime
import uuid
import psycopg2

logger = logging.getLogger(__name__)

# Config
SLA_THRESHOLD_SECONDS = 30 * 60  # 30 minutes
PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASSWORD = "password"
PG_DB = "product_analytics_operational"


def log_pipeline_run(
    started_at: datetime,
    completed_at: datetime,
    rows_processed: int = 0,
    quality_score: float = 1.0,
    status: str = "success",
    error_message: str = None,
    notes: str = None
):
    """Log pipeline run to PostgreSQL"""

    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            database=PG_DB
        )
        cursor = conn.cursor()

        run_id = str(uuid.uuid4())
        duration = (completed_at - started_at).total_seconds()
        sla_met = duration <= SLA_THRESHOLD_SECONDS
        run_date = started_at.date()

        logger.info(f"Logging pipeline run: {run_id}")
        logger.info(f"  Duration: {duration:.0f}s (SLA: {SLA_THRESHOLD_SECONDS}s)")
        logger.info(f"  SLA Met: {sla_met}")
        logger.info(f"  Quality Score: {quality_score:.2f}")

        cursor.execute(
            """
            INSERT INTO pipeline_runs
            (run_id, run_date, started_at, completed_at, duration_seconds,
             rows_processed, sla_met, quality_score, status, error_message, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                run_id,
                run_date,
                started_at,
                completed_at,
                int(duration),
                rows_processed,
                sla_met,
                quality_score,
                status,
                error_message,
                notes
            )
        )

        conn.commit()

        if not sla_met:
            logger.warning(f"⚠️ SLA BREACHED: {duration:.0f}s > {SLA_THRESHOLD_SECONDS}s")
            send_alert(run_id, duration, SLA_THRESHOLD_SECONDS)

        cursor.close()
        conn.close()

        return {
            "run_id": run_id,
            "duration": int(duration),
            "sla_met": sla_met,
            "quality_score": quality_score
        }

    except Exception as e:
        logger.error(f"Failed to log pipeline run: {e}")
        raise


def send_alert(run_id: str, duration: float, threshold: float):
    """Send email alert for SLA breach"""
    # TODO: Implement email alert
    logger.error(
        f"SLA breach alert (stub): Run {run_id} took {duration:.0f}s > {threshold}s"
    )


def query_sla_compliance(days_back: int = 7):
    """Query SLA compliance over last N days"""

    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            database=PG_DB
        )
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT
                DATE(run_date) as date,
                COUNT(*) as total_runs,
                SUM(CASE WHEN sla_met THEN 1 ELSE 0 END) as sla_met_count,
                ROUND(100.0 * SUM(CASE WHEN sla_met THEN 1 ELSE 0 END) / COUNT(*), 2) as sla_compliance_pct,
                AVG(quality_score) as avg_quality_score
            FROM pipeline_runs
            WHERE run_date >= CURRENT_DATE - INTERVAL '{days_back} days'
            GROUP BY DATE(run_date)
            ORDER BY date DESC
            """
        )

        results = cursor.fetchall()
        cursor.close()
        conn.close()

        logger.info(f"SLA Compliance (last {days_back} days):")
        for row in results:
            logger.info(
                f"  {row[0]}: {row[3]:.1f}% compliance ({row[2]}/{row[1]} runs), "
                f"Quality: {row[4]:.2f}"
            )

        return results

    except Exception as e:
        logger.error(f"Failed to query SLA compliance: {e}")
        raise


if __name__ == "__main__":
    # Example: log a successful run
    import datetime
    start = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    end = datetime.datetime.utcnow()

    result = log_pipeline_run(
        started_at=start,
        completed_at=end,
        rows_processed=3_000_000,
        quality_score=0.98,
        status="success"
    )

    logger.info(f"Logged run: {result}")

    # Query compliance
    query_sla_compliance(days_back=7)
