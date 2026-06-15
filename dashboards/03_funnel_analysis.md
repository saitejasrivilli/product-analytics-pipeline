# Funnel Analysis Dashboard

Track the path from user action to conversion and repeat purchase.

## Daily Funnel Metrics

```sql
SELECT
    metric_date,
    daily_users as users,
    daily_orders as orders,
    ROUND(daily_orders::float / daily_users, 2) as conversion_rate,
    ROUND(daily_products_added::float / daily_orders, 2) as avg_items_per_order,
    ROUND(daily_reordered_items::float / daily_products_added, 3) as reorder_rate
FROM product_funnel
ORDER BY metric_date DESC
LIMIT 30
```

**Insights:**
- User-to-order conversion
- Cart composition
- Repeat purchase momentum

---

## Top Reordered Products

```sql
SELECT
    product_id,
    product_name,
    department_name,
    COUNT(DISTINCT order_id) as times_ordered,
    SUM(CASE WHEN reordered = 1 THEN 1 ELSE 0 END) as reorder_count,
    ROUND(SUM(CASE WHEN reordered = 1 THEN 1 ELSE 0 END)::float / COUNT(*), 3) as reorder_rate
FROM fact_orders
GROUP BY product_id, product_name, department_name
HAVING COUNT(DISTINCT order_id) >= 5
ORDER BY reorder_count DESC
LIMIT 25
```

**Insights:**
- Sticky products driving retention
- High-value repeat SKUs
- Cross-category patterns

---

## Department Conversion & Reorder

```sql
SELECT
    department_name,
    COUNT(DISTINCT order_id) as order_count,
    COUNT(DISTINCT user_id) as unique_users,
    ROUND(COUNT(DISTINCT order_id)::float / COUNT(DISTINCT user_id), 2) as orders_per_user,
    ROUND(SUM(CASE WHEN reordered = 1 THEN 1 ELSE 0 END)::float / COUNT(*), 3) as reorder_rate
FROM fact_orders
GROUP BY department_name
ORDER BY order_count DESC
```

**Insights:**
- Department performance vs. traffic
- Loyalty by category
- Expansion opportunities

---

## Cart Composition

```sql
SELECT
    CASE
        WHEN items_per_order = 1 THEN '1 item'
        WHEN items_per_order BETWEEN 2 AND 5 THEN '2-5 items'
        WHEN items_per_order BETWEEN 6 AND 10 THEN '6-10 items'
        WHEN items_per_order BETWEEN 11 AND 20 THEN '11-20 items'
        ELSE '20+ items'
    END as order_size,
    COUNT(*) as order_count,
    ROUND(AVG(reordered_pct), 3) as avg_reorder_rate
FROM (
    SELECT
        order_id,
        COUNT(DISTINCT product_id) as items_per_order,
        ROUND(SUM(CASE WHEN reordered = 1 THEN 1 ELSE 0 END)::float / COUNT(*), 3) as reordered_pct
    FROM fact_orders
    GROUP BY order_id
)
GROUP BY order_size
ORDER BY 
    CASE
        WHEN order_size = '1 item' THEN 1
        WHEN order_size = '2-5 items' THEN 2
        WHEN order_size = '6-10 items' THEN 3
        WHEN order_size = '11-20 items' THEN 4
        ELSE 5
    END
```

**Insights:**
- Basket size distribution
- Larger carts = higher reorder rate?
- Trip purpose segmentation
