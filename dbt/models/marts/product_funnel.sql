{{ config(
    materialized='table',
    tags=['marts', 'metrics']
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

order_products as (
    select * from {{ ref('stg_order_products') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

funnel_data as (
    select
        o.order_dow,
        date_trunc('day', current_timestamp) + interval (o.order_id % 365) day as metric_date,
        count(distinct o.user_id) as daily_users,
        count(distinct o.order_id) as daily_orders,
        count(distinct p.product_id) as daily_products_added,
        sum(case when op.reordered = 1 then 1 else 0 end) as daily_reordered_items,
        count(distinct case when op.reordered = 1 then o.order_id end) as orders_with_reorders,

        -- Metrics
        count(distinct o.order_id)::float / count(distinct o.user_id) as orders_per_user,
        count(distinct p.product_id)::float / count(distinct o.order_id) as avg_items_per_order,
        sum(case when op.reordered = 1 then 1 else 0 end)::float / nullif(count(distinct op.product_id), 0) as reorder_rate
    from orders o
    left join order_products op on o.order_id = op.order_id
    left join products p on op.product_id = p.product_id
    group by o.order_dow, metric_date
)

select
    metric_date,
    order_dow,
    daily_users,
    daily_orders,
    daily_products_added,
    daily_reordered_items,
    orders_with_reorders,
    orders_per_user,
    avg_items_per_order,
    coalesce(reorder_rate, 0.0) as reorder_rate,
    current_timestamp as created_at
from funnel_data
order by metric_date desc
