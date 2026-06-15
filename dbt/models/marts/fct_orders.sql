{{ config(
    materialized='incremental',
    tags=['marts', 'fact'],
    unique_key=['order_id', 'product_id']
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
    {% if execute and flags.WHICH == 'run' %}
        {% if this.exists and execute %}
            where order_id > (select max(order_id) from {{ this }})
        {% endif %}
    {% endif %}
),

products as (
    select * from {{ ref('stg_products') }}
),

order_products as (
    select * from {{ ref('stg_order_products') }}
),

joined as (
    select
        op.order_id,
        o.user_id,
        op.product_id,
        p.department_id,
        p.aisle_id,
        o.order_hour_of_day as order_hour,
        o.order_dow,
        o.days_since_prior_order,
        op.reordered,
        op.add_to_cart_order,
        cast(replace(cast(o.order_id as varchar), '.', '') as int) as order_date_id,
        current_timestamp as created_at
    from order_products op
    inner join orders o on op.order_id = o.order_id
    inner join products p on op.product_id = p.product_id
)

select * from joined
