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
    "analytics.fct_orders",
    "analytics.dim_users",
    "analytics.dim_products",
    "analytics.dim_departments",
    "analytics.product_funnel",
    "analytics.user_retention",
    "analytics.department_performance"
]

for table in tables:
    table_name = table.split(".")[-1]
    try:
        print(f"Migrating {table_name}...", end=" ")
        df = local.execute(f"SELECT * FROM {table}").df()
        cloud.execute(f"DROP TABLE IF EXISTS {table_name}")
        cloud.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        count = cloud.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"✅ {count:,} rows")
    except Exception as e:
        if "does not exist" in str(e):
            print(f"⏭️  skipped (not in local warehouse)")
        else:
            print(f"⚠️ {e}")

print("\nMigration complete. Use this token in Render environment:")
print(f"MOTHERDUCK_TOKEN={MD_TOKEN}")

local.close()
cloud.close()
