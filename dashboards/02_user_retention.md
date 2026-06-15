# User Retention Dashboard

Track user behavior patterns and repeat purchase behavior.

## User Cohorts

```sql
SELECT
    user_cohort,
    COUNT(DISTINCT user_id) as user_count,
    ROUND(AVG(total_orders), 1) as avg_orders_per_user,
    ROUND(AVG(order_span), 1) as avg_order_span,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_users
FROM user_retention
GROUP BY user_cohort
ORDER BY user_count DESC
```

**Insights:**
- User distribution by engagement level
- Activity patterns by cohort
- Churn risk identification

---

## Order Frequency Distribution

```sql
SELECT
    total_orders,
    COUNT(DISTINCT user_id) as user_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_users
FROM user_retention
GROUP BY total_orders
ORDER BY total_orders
LIMIT 30
```

**Insights:**
- Most common order frequencies
- One-time vs. repeat purchasers
- Engagement distribution shape

---

## Days Between Orders

```sql
SELECT
    CASE
        WHEN days_since_prior_order IS NULL THEN 'First Order'
        WHEN days_since_prior_order <= 7 THEN '1-7 days'
        WHEN days_since_prior_order <= 14 THEN '8-14 days'
        WHEN days_since_prior_order <= 30 THEN '15-30 days'
        ELSE '30+ days'
    END as reorder_window,
    COUNT(*) as order_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_orders
FROM fact_orders
GROUP BY reorder_window
ORDER BY
    CASE
        WHEN reorder_window = 'First Order' THEN 1
        WHEN reorder_window = '1-7 days' THEN 2
        WHEN reorder_window = '8-14 days' THEN 3
        WHEN reorder_window = '15-30 days' THEN 4
        ELSE 5
    END
```

**Insights:**
- Optimal replenishment frequency
- Customer purchase cycles
- Freshness expectations

---

## Reorder Rate by User Segment

```sql
SELECT
    user_segment,
    ROUND(AVG(reorder_rate), 3) as avg_reorder_rate,
    COUNT(DISTINCT user_id) as user_count,
    STDDEV(reorder_rate) as reorder_rate_variance
FROM dim_users
GROUP BY user_segment
ORDER BY avg_reorder_rate DESC
```

**Insights:**
- Segment loyalty metrics
- Which segments are most engaged
- Opportunity for conversion programs
