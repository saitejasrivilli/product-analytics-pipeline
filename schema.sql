-- PRODUCT ANALYTICS PIPELINE: STAR SCHEMA DESIGN
-- Dataset: Instacart Market Basket Analysis
--
-- DESIGN DECISIONS:
-- 1. Star schema (not snowflake): Simplicity + query speed for analytics.
--    Single fact table + dimensional tables. Denormalization acceptable.
-- 2. Fact grain: ONE ROW PER ORDER-PRODUCT COMBINATION
--    Allows product-level analysis within orders. Supports funnel metrics.
-- 3. Partitioning strategy: fact_orders partitioned by order_dow (day of week).
--    Improves performance on time-based queries.
-- 4. Slowly-changing dimensions: Track product, department changes over time
--    using effective_date / end_date pattern (for future enhancements).

-- ============================================================================
-- STAGING TABLES (raw data, minimal transformation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS staging.stg_orders (
    order_id INT,
    user_id INT,
    order_number INT,
    order_dow INT,
    order_hour_of_day INT,
    days_since_prior_order INT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_products (
    product_id INT,
    product_name VARCHAR,
    aisle_id INT,
    department_id INT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_aisles (
    aisle_id INT,
    aisle_name VARCHAR,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_departments (
    department_id INT,
    department_name VARCHAR,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_order_products (
    order_id INT,
    product_id INT,
    add_to_cart_order INT,
    reordered INT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS dim_users (
    user_id INT PRIMARY KEY,
    total_orders INT,
    days_since_first_order INT,
    days_since_last_order INT,
    avg_days_between_orders FLOAT,
    reorder_rate FLOAT,
    user_segment VARCHAR,  -- "high_frequency", "medium", "low_frequency"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR,
    aisle_id INT NOT NULL,
    aisle_name VARCHAR,
    department_id INT NOT NULL,
    department_name VARCHAR,
    reorder_count INT DEFAULT 0,
    reorder_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR UNIQUE,
    total_products INT DEFAULT 0,
    total_orders INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_aisles (
    aisle_id INT PRIMARY KEY,
    aisle_name VARCHAR UNIQUE,
    department_id INT NOT NULL REFERENCES dim_departments(department_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_time (
    date_id INT PRIMARY KEY,  -- YYYYMMDD format
    order_date DATE,
    order_hour INT,
    order_dow INT,  -- 0=Monday, 6=Sunday
    day_of_week_name VARCHAR,
    week_of_year INT,
    month INT,
    quarter INT,
    year INT,
    is_weekend INT DEFAULT 0,  -- 1 if Saturday or Sunday
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- FACT TABLE (grain: one row per order-product combination)
-- ============================================================================

CREATE TABLE IF NOT EXISTS fact_orders (
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    department_id INT NOT NULL,
    aisle_id INT NOT NULL,
    order_hour INT,
    order_dow INT,
    days_since_prior_order INT,
    reordered INT,  -- 0 or 1: was this product previously ordered by user?
    add_to_cart_order INT,  -- sequence position in order
    order_date_id INT,  -- FK to dim_time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (user_id) REFERENCES dim_users(user_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (department_id) REFERENCES dim_departments(department_id),
    FOREIGN KEY (aisle_id) REFERENCES dim_aisles(aisle_id),
    FOREIGN KEY (order_date_id) REFERENCES dim_time(date_id)
);

-- Partitioning by order_dow for performance (simulated via indexing)
CREATE INDEX idx_fact_orders_dow ON fact_orders(order_dow);
CREATE INDEX idx_fact_orders_user ON fact_orders(user_id);
CREATE INDEX idx_fact_orders_date ON fact_orders(order_date_id);
CREATE INDEX idx_fact_orders_reordered ON fact_orders(reordered);

-- ============================================================================
-- OPERATIONAL TABLES (pipeline monitoring)
-- ============================================================================

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id UUID PRIMARY KEY,
    run_date DATE,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INT,
    rows_processed INT,
    rows_failed INT DEFAULT 0,
    sla_met BOOLEAN,
    quality_score FLOAT,  -- 0.0 to 1.0
    status VARCHAR,  -- "success", "failed", "partial"
    error_message TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_quality_metrics (
    metric_id UUID PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES pipeline_runs(run_id),
    metric_name VARCHAR,  -- "null_rate", "duplicate_rate", "row_count_change", etc.
    table_name VARCHAR,
    column_name VARCHAR,
    metric_value FLOAT,
    expected_value FLOAT,
    actual_value FLOAT,
    passed BOOLEAN,
    anomaly_detected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipeline_runs_date ON pipeline_runs(run_date);
CREATE INDEX idx_data_quality_runs ON data_quality_metrics(run_id);
