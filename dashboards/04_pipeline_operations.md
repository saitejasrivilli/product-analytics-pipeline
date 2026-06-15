# Pipeline Operations Dashboard

Monitor data pipeline health, freshness, and quality.

## Latest Run Status

```sql
SELECT
    run_id,
    run_date,
    started_at,
    completed_at,
    duration_seconds,
    sla_met,
    quality_score,
    status,
    notes
FROM pipeline_runs
ORDER BY run_date DESC, started_at DESC
LIMIT 1
```

**Insights:**
- Last pipeline execution status
- Data freshness timestamp
- Quality score snapshot
- Any errors or warnings

---

## SLA Compliance Trend

```sql
SELECT
    run_date,
    COUNT(*) as total_runs,
    SUM(CASE WHEN sla_met THEN 1 ELSE 0 END) as sla_met_count,
    ROUND(100.0 * SUM(CASE WHEN sla_met THEN 1 ELSE 0 END) / COUNT(*), 2) as sla_compliance_pct,
    ROUND(AVG(duration_seconds), 0) as avg_duration_sec,
    ROUND(MAX(duration_seconds), 0) as max_duration_sec
FROM pipeline_runs
GROUP BY run_date
ORDER BY run_date DESC
LIMIT 30
```

**Insights:**
- Daily SLA compliance percentage
- Pipeline performance trend
- Duration spikes or improvements

---

## Quality Score Trend

```sql
SELECT
    run_date,
    COUNT(*) as run_count,
    ROUND(AVG(quality_score), 3) as avg_quality_score,
    ROUND(MIN(quality_score), 3) as min_quality_score,
    ROUND(MAX(quality_score), 3) as max_quality_score
FROM pipeline_runs
GROUP BY run_date
ORDER BY run_date DESC
LIMIT 30
```

**Insights:**
- Data quality over time
- Anomalies or degradation
- Confidence in mart tables

---

## Data Volume Metrics

```sql
SELECT
    run_date,
    SUM(rows_processed) as total_rows_processed,
    COUNT(*) as run_count,
    ROUND(AVG(rows_processed), 0) as avg_rows_per_run
FROM pipeline_runs
WHERE status = 'success'
GROUP BY run_date
ORDER BY run_date DESC
LIMIT 30
```

**Insights:**
- Daily data volume growth
- Ingestion rates
- Anomalous spikes or drops

---

## Fact Table Row Counts

```sql
SELECT
    'fact_orders' as table_name,
    COUNT(*) as row_count,
    ROUND(COUNT(*) / 1000000.0, 2) as millions_of_rows
FROM fact_orders
UNION ALL
SELECT
    'dim_users',
    COUNT(*),
    ROUND(COUNT(*) / 1000000.0, 2)
FROM dim_users
UNION ALL
SELECT
    'dim_products',
    COUNT(*),
    ROUND(COUNT(*) / 1000000.0, 2)
FROM dim_products
ORDER BY row_count DESC
```

**Insights:**
- Current warehouse size
- Growth trajectory
- Model completeness
