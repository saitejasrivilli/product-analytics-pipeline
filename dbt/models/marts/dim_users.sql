{{ config(
    materialized='table',
    tags=['marts', 'dimension']
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

order_products as (
    select * from {{ ref('stg_order_products') }}
),

user_metrics as (
    select
        o.user_id,
        count(distinct o.order_id) as total_orders,
        count(distinct case when op.reordered = 1 then o.order_id end) as orders_with_reorders,
        count(case when op.reordered = 1 then 1 end)::float /
            nullif(count(distinct op.product_id), 0) as reorder_rate,
        round(avg(o.days_since_prior_order)) as avg_days_between_orders,
        max(o.order_number) - min(o.order_number) as days_since_first_order,
        current_timestamp as created_at,
        current_timestamp as updated_at
    from orders o
    left join order_products op on o.order_id = op.order_id
    group by o.user_id
)

select
    user_id,
    total_orders,
    days_since_first_order,
    0 as days_since_last_order,  -- placeholder
    avg_days_between_orders,
    reorder_rate,
    case
        when total_orders >= 10 then 'high_frequency'
        when total_orders >= 5 then 'medium'
        else 'low_frequency'
    end as user_segment,
    created_at,
    updated_at
from user_metrics
