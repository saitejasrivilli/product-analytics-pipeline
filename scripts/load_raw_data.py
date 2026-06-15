#!/usr/bin/env python3
"""
Load Instacart CSV files into DuckDB staging tables.
"""

import sys
from pathlib import Path
import pandas as pd
import duckdb

def load_data():
    data_dir = Path("data/raw")

    # Verify CSVs exist
    required_files = [
        "orders.csv",
        "products.csv",
        "aisles.csv",
        "departments.csv",
        "order_products__train.csv"
    ]

    missing = [f for f in required_files if not (data_dir / f).exists()]
    if missing:
        print(f"❌ Missing files: {missing}")
        print("   Run: python scripts/download_dataset.py")
        sys.exit(1)

    # Connect to DuckDB
    conn = duckdb.connect("data/warehouse.duckdb")

    print("📥 Loading raw data into DuckDB staging schema...")

    try:
        # Create schema
        conn.execute("CREATE SCHEMA IF NOT EXISTS staging")

        # Load orders
        print("  Loading orders...")
        conn.execute(f"""
            CREATE OR REPLACE TABLE staging.stg_orders AS
            SELECT
                order_id,
                user_id,
                order_number,
                order_dow,
                order_hour_of_day,
                days_since_prior_order,
                CURRENT_TIMESTAMP as loaded_at
            FROM read_csv_auto('{data_dir}/orders.csv')
        """)
        count = conn.execute("SELECT count(*) FROM staging.stg_orders").fetchall()[0][0]
        print(f"    ✓ {count:,} orders")

        # Load products
        print("  Loading products...")
        conn.execute(f"""
            CREATE OR REPLACE TABLE staging.stg_products AS
            SELECT
                product_id,
                product_name,
                aisle_id,
                department_id,
                CURRENT_TIMESTAMP as loaded_at
            FROM read_csv_auto('{data_dir}/products.csv')
        """)
        count = conn.execute("SELECT count(*) FROM staging.stg_products").fetchall()[0][0]
        print(f"    ✓ {count:,} products")

        # Load aisles
        print("  Loading aisles...")
        conn.execute(f"""
            CREATE OR REPLACE TABLE staging.stg_aisles AS
            SELECT
                aisle_id,
                aisle_name,
                CURRENT_TIMESTAMP as loaded_at
            FROM read_csv_auto('{data_dir}/aisles.csv')
        """)
        count = conn.execute("SELECT count(*) FROM staging.stg_aisles").fetchall()[0][0]
        print(f"    ✓ {count:,} aisles")

        # Load departments
        print("  Loading departments...")
        conn.execute(f"""
            CREATE OR REPLACE TABLE staging.stg_departments AS
            SELECT
                department_id,
                department_name,
                CURRENT_TIMESTAMP as loaded_at
            FROM read_csv_auto('{data_dir}/departments.csv')
        """)
        count = conn.execute("SELECT count(*) FROM staging.stg_departments").fetchall()[0][0]
        print(f"    ✓ {count:,} departments")

        # Load order_products
        print("  Loading order_products...")
        conn.execute(f"""
            CREATE OR REPLACE TABLE staging.stg_order_products AS
            SELECT
                order_id,
                product_id,
                add_to_cart_order,
                reordered,
                CURRENT_TIMESTAMP as loaded_at
            FROM read_csv_auto('{data_dir}/order_products__train.csv')
        """)
        count = conn.execute("SELECT count(*) FROM staging.stg_order_products").fetchall()[0][0]
        print(f"    ✓ {count:,} order-product records")

        print("\n✅ Data loaded successfully to data/warehouse.duckdb")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    load_data()
