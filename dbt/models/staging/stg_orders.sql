{{ config(
    materialized='view',
    tags=['staging']
) }}

select
    order_id,
    user_id,
    order_number,
    order_dow,
    order_hour_of_day,
    days_since_prior_order,
    loaded_at
from {{ source('instacart', 'stg_orders') }}
where order_id is not null
