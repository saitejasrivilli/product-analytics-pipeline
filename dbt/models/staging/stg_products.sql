{{ config(
    materialized='view',
    tags=['staging']
) }}

select
    product_id,
    product_name,
    aisle_id,
    department_id,
    loaded_at
from {{ source('instacart', 'stg_products') }}
where product_id is not null
