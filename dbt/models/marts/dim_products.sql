{{ config(
    materialized='table',
    tags=['marts', 'dimension']
) }}

with products as (
    select * from {{ ref('stg_products') }}
),

order_products as (
    select * from {{ ref('stg_order_products') }}
),

product_metrics as (
    select
        p.product_id,
        p.product_name,
        p.aisle_id,
        p.department_id,
        count(distinct op.order_id) as total_orders,
        count(case when op.reordered = 1 then 1 end) as reorder_count,
        count(case when op.reordered = 1 then 1 end)::float /
            nullif(count(distinct op.order_id), 0) as reorder_rate
    from products p
    left join order_products op on p.product_id = op.product_id
    group by p.product_id, p.product_name, p.aisle_id, p.department_id
)

select
    pm.product_id,
    pm.product_name,
    pm.aisle_id,
    'Aisle_' || pm.aisle_id as aisle_name,  -- placeholder, join with dim_aisles
    pm.department_id,
    'Department_' || pm.department_id as department_name,  -- placeholder
    pm.reorder_count,
    coalesce(pm.reorder_rate, 0.0) as reorder_rate,
    current_timestamp as created_at,
    current_timestamp as updated_at
from product_metrics pm
