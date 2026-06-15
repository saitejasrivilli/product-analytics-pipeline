#!/usr/bin/env python3
"""
Generate sample Instacart-like data for local testing.
Creates small CSV files that mimic the real dataset structure.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

def generate_sample_data(output_dir: Path = Path("data/raw")):
    """Generate sample CSVs for testing"""
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating sample data...")

    # 1. Departments
    departments = pd.DataFrame({
        "department_id": range(1, 16),
        "department_name": [
            "produce", "dairy eggs", "deli", "frozen", "bakery",
            "beverages", "snacks", "pantry", "bulk", "canned goods",
            "meat seafood", "international", "alcohol", "personal care", "household"
        ]
    })
    departments.to_csv(output_dir / "departments.csv", index=False)
    print(f"✓ departments.csv: {len(departments)} rows")

    # 2. Aisles
    aisles = pd.DataFrame({
        "aisle_id": range(1, 136),
        "aisle_name": [f"aisle_{i}" for i in range(1, 136)]
    })
    aisles.to_csv(output_dir / "aisles.csv", index=False)
    print(f"✓ aisles.csv: {len(aisles)} rows")

    # 3. Products
    np.random.seed(42)
    n_products = 5000
    products = pd.DataFrame({
        "product_id": range(1, n_products + 1),
        "product_name": [f"product_{i}" for i in range(1, n_products + 1)],
        "aisle_id": np.random.randint(1, 136, n_products),
        "department_id": np.random.randint(1, 16, n_products),
    })
    products.to_csv(output_dir / "products.csv", index=False)
    print(f"✓ products.csv: {len(products)} rows")

    # 4. Orders
    n_orders = 100000
    n_users = 50000
    base_date = datetime(2024, 1, 1)

    orders = pd.DataFrame({
        "order_id": range(1, n_orders + 1),
        "user_id": np.random.randint(1, n_users + 1, n_orders),
        "order_number": np.random.randint(1, 100, n_orders),
        "order_dow": np.random.randint(0, 7, n_orders),
        "order_hour_of_day": np.random.randint(0, 24, n_orders),
        "days_since_prior_order": np.random.randint(0, 30, n_orders),
    })
    # Make order_id mostly unique (90% unique)
    orders = orders.drop_duplicates(subset=['order_id'], keep='first').reset_index(drop=True)
    orders.to_csv(output_dir / "orders.csv", index=False)
    print(f"✓ orders.csv: {len(orders)} rows")

    # 5. Order Products
    n_order_products = 500000
    order_product_data = []

    for _ in range(n_order_products):
        order_id = np.random.randint(1, n_orders + 1)
        product_id = np.random.randint(1, n_products + 1)

        order_product_data.append({
            "order_id": order_id,
            "product_id": product_id,
            "add_to_cart_order": np.random.randint(1, 20),
            "reordered": np.random.randint(0, 2),
        })

    order_products = pd.DataFrame(order_product_data)
    order_products = order_products.drop_duplicates(subset=['order_id', 'product_id'], keep='first')
    order_products.to_csv(output_dir / "order_products__train.csv", index=False)
    print(f"✓ order_products__train.csv: {len(order_products)} rows")

    print(f"\n✅ Sample data generated in {output_dir}")
    print(f"Total size: ~{sum(f.stat().st_size for f in output_dir.glob('*.csv')) / 1e6:.1f} MB")

if __name__ == "__main__":
    generate_sample_data()
