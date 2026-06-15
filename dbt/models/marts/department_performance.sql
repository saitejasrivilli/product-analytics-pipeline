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

department_metrics as (
    select
        p.department_id,
        count(distinct o.order_id) as total_orders,
        count(distinct o.user_id) as unique_users,
        count(distinct op.product_id) as unique_products,
        sum(case when op.reordered = 1 then 1 else 0 end) as reordered_items,
        count(distinct op.product_id) as total_items_added,

        -- Rates
        sum(case when op.reordered = 1 then 1 else 0 end)::float / nullif(count(distinct op.product_id), 0) as reorder_rate,
        count(distinct case when op.reordered = 1 then o.order_id end)::float / count(distinct o.order_id) as orders_with_reorders_pct,

        -- Ranking
        dense_rank() over (order by count(distinct o.order_id) desc) as order_volume_rank,
        dense_rank() over (order by sum(case when op.reordered = 1 then 1 else 0 end) desc) as reorder_rank
    from products p
    left join order_products op on p.product_id = op.product_id
    left join orders o on op.order_id = o.order_id
    group by p.department_id
),

-- Add cohort analysis
department_cohorts as (
    select
        p.department_id,
        o.order_dow,
        count(distinct o.user_id) as users_by_dow,
        count(distinct o.order_id) as orders_by_dow,
        sum(case when op.reordered = 1 then 1 else 0 end)::float / count(distinct op.product_id) as reorder_rate_by_dow
    from products p
    left join order_products op on p.product_id = op.product_id
    left join orders o on op.order_id = o.order_id
    group by p.department_id, o.order_dow
)

select
    dm.department_id,
    dm.total_orders,
    dm.unique_users,
    dm.unique_products,
    dm.reordered_items,
    dm.total_items_added,
    coalesce(dm.reorder_rate, 0.0) as reorder_rate,
    coalesce(dm.orders_with_reorders_pct, 0.0) as orders_with_reorders_pct,
    dm.order_volume_rank,
    dm.reorder_rank,
    case
        when dm.order_volume_rank <= 5 then 'top_tier'
        when dm.order_volume_rank <= 10 then 'mid_tier'
        else 'emerging'
    end as performance_tier,
    current_timestamp as created_at
from department_metrics dm
order by dm.order_volume_rank asc
