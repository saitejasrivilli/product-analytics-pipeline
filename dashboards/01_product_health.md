# Product Health Dashboard

Real-time metrics on order volume, user engagement, and product performance.

## Daily Metrics

```sql
SELECT
    order_dow as day_of_week,
    COUNT(DISTINCT user_id) as daily_active_users,
    COUNT(DISTINCT order_id) as daily_orders,
    COUNT(DISTINCT product_id) as unique_products_ordered,
    ROUND(COUNT(DISTINCT product_id)::float / COUNT(DISTINCT order_id), 2) as avg_items_per_order,
    ROUND(SUM(CASE WHEN reordered = 1 THEN 1 ELSE 0 END)::float / COUNT(*), 2) as reorder_rate
FROM fact_orders
GROUP BY order_dow
ORDER BY order_dow
```

**Insights:**
- Daily active users trend
- Peak order times
- Average basket size
- Reorder rate by day of week

---

## Top Products by Reorder Rate

```sql
SELECT
    product_id,
    product_name,
    COUNT(DISTINCT order_id) as times_ordered,
    ROUND(SUM(CASE WHEN reordered = 1 THEN 1 ELSE 0 END)::float / COUNT(*), 3) as reorder_rate,
    department_name
FROM fact_orders
GROUP BY product_id, product_name, department_name
HAVING COUNT(DISTINCT order_id) >= 10
ORDER BY reorder_rate DESC
LIMIT 20
```

**Insights:**
- High-value repeat purchase products
- Department performance drivers

---

## Department Revenue Share

```sql
SELECT
    dp.department_id,
    dp.department_name,
    COUNT(DISTINCT fo.order_id) as total_orders,
    COUNT(DISTINCT fo.product_id) as unique_products,
    ROUND(100.0 * COUNT(DISTINCT fo.order_id) / SUM(COUNT(DISTINCT fo.order_id)) OVER (), 2) as pct_of_orders
FROM fact_orders fo
JOIN dim_products dp ON fo.product_id = dp.product_id
GROUP BY dp.department_id, dp.department_name
ORDER BY total_orders DESC
```

**Insights:**
- Which departments drive order volume
- Market share by category
- Cross-selling opportunities

---

## User Segments

```sql
SELECT
    user_segment,
    COUNT(DISTINCT user_id) as user_count,
    ROUND(AVG(total_orders), 1) as avg_orders,
    ROUND(AVG(reorder_rate), 3) as avg_reorder_rate,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_of_users
FROM dim_users
GROUP BY user_segment
ORDER BY user_count DESC
```

**Insights:**
- User distribution across segments
- Segment-level engagement metrics
- Retention by segment
