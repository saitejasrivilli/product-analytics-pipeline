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

-- Assign users to cohorts based on first order
user_cohorts as (
    select
        o.user_id,
        min(o.order_number) as first_order_number,
        min(cast(o.order_id as date)) as first_order_date,
        extract(year from min(cast(o.order_id as date))) as cohort_year,
        extract(week from min(cast(o.order_id as date))) as cohort_week
    from orders o
    group by o.user_id
),

-- Get order history with cohort assignment
order_history as (
    select
        uc.user_id,
        uc.cohort_year,
        uc.cohort_week,
        uc.first_order_date,
        o.order_number,
        cast(o.order_id as date) as order_date,
        extract(week from cast(o.order_id as date)) - uc.cohort_week as weeks_since_cohort,
        count(distinct op.product_id) as items_in_order,
        sum(case when op.reordered = 1 then 1 else 0 end) as reordered_items_in_order
    from user_cohorts uc
    inner join orders o on uc.user_id = o.user_id
    left join order_products op on o.order_id = op.order_id
    group by uc.user_id, uc.cohort_year, uc.cohort_week, uc.first_order_date, o.order_number, order_date
),

-- Retention metrics by week
retention_by_week as (
    select
        cohort_year,
        cohort_week,
        weeks_since_cohort,
        count(distinct user_id) as retained_users,
        count(distinct order_id) as orders_this_week,
        round(count(distinct user_id)::float / max(count(distinct user_id)) over (partition by cohort_year, cohort_week), 3) as retention_rate
    from (
        select
            oh.cohort_year,
            oh.cohort_week,
            oh.weeks_since_cohort,
            oh.user_id,
            row_number() over (partition by oh.user_id order by oh.order_date) as order_id
        from order_history oh
    )
    group by cohort_year, cohort_week, weeks_since_cohort
)

select
    cohort_year,
    cohort_week,
    weeks_since_cohort,
    retained_users,
    orders_this_week,
    retention_rate,
    current_timestamp as created_at
from retention_by_week
where weeks_since_cohort >= 0
order by cohort_year desc, cohort_week desc, weeks_since_cohort asc
