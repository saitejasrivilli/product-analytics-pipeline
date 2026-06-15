{{ config(
    materialized='table',
    tags=['marts', 'metrics']
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

user_order_counts as (
    select
        user_id,
        count(distinct order_id) as total_orders,
        max(order_number) - min(order_number) as order_span
    from orders
    group by user_id
)

select
    user_id,
    total_orders,
    order_span,
    case
        when total_orders = 1 then 'single_order'
        when total_orders <= 5 then 'light_user'
        when total_orders <= 20 then 'medium_user'
        else 'heavy_user'
    end as user_cohort,
    current_timestamp as created_at
from user_order_counts
order by total_orders desc
