-- SCD Type 2: Slowly Changing Dimension for Products
-- Tracks product changes (department reclassifications, name changes) over time
-- Enables point-in-time analysis: "What was product X's department on date Y?"

{{
  config(
    materialized='table',
    indexes=[
      {'columns': ['product_id'], 'type': 'hash'},
      {'columns': ['is_current'], 'type': 'hash'}
    ]
  )
}}

SELECT
    product_id,
    product_name,
    aisle_id,
    department_id,
    CURRENT_DATE as valid_from,
    CAST('9999-12-31' as DATE) as valid_to,
    TRUE as is_current,
    '{{ run_started_at }}' as dbt_updated_at
FROM {{ ref('dim_products') }}

-- In production, this would include:
-- - Historical lookups to detect changes
-- - Previous version marked as is_current = FALSE
-- - Chain of valid_from/valid_to dates
-- For demo: shows SCD Type 2 structure with current snapshot
