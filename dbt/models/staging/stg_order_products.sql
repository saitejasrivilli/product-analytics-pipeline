{{ config(
    materialized='view',
    tags=['staging']
) }}

select
    order_id,
    product_id,
    add_to_cart_order,
    reordered,
    loaded_at
from {{ source('instacart', 'stg_order_products') }}
where order_id is not null
    and product_id is not null
