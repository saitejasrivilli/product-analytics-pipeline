#!/usr/bin/env python
import duckdb
import sys

MD_TOKEN = input("Paste your MotherDuck token: ").strip()
if not MD_TOKEN:
    print("❌ Token required")
    sys.exit(1)

print("Connecting to local warehouse...")
local = duckdb.connect("data/warehouse.duckdb")

print(f"Connecting to MotherDuck...")
cloud = duckdb.connect(f"md:?motherduck_token={MD_TOKEN}")

cloud.execute("CREATE DATABASE IF NOT EXISTS product_analytics")
cloud.execute("USE product_analytics")

tables = [
    "fact_orders",
    "dim_users",
    "dim_products",
    "dim_departments",
    "product_funnel",
    "user_retention",
    "department_performance"
]

for table in tables:
    try:
        print(f"Migrating {table}...", end=" ")
        df = local.execute(f"SELECT * FROM {table}").df()
        cloud.execute(f"DROP TABLE IF EXISTS {table}")
        cloud.execute(f"CREATE TABLE {table} AS SELECT * FROM df")
        count = cloud.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"✅ {count:,} rows")
    except Exception as e:
        print(f"⚠️ {e}")

print("\nMigration complete. Use this token in Render environment:")
print(f"MOTHERDUCK_TOKEN={MD_TOKEN}")

local.close()
cloud.close()
