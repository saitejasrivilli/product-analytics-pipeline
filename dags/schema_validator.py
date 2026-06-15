"""
Schema validation for raw CSV files.
Validates: column presence, type compatibility, row counts, constraints.
"""

import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

# Expected schema for each CSV
SCHEMAS = {
    "orders.csv": {
        "columns": {
            "order_id": "int64",
            "user_id": "int64",
            "order_number": "int64",
            "order_dow": "int64",
            "order_hour_of_day": "int64",
            "days_since_prior_order": "float64",
        },
        "constraints": {
            "order_id": {"min": 1, "unique": True},
            "user_id": {"min": 1},
            "order_dow": {"min": 0, "max": 6},
            "order_hour_of_day": {"min": 0, "max": 23},
        },
        "min_rows": 100000,
    },
    "products.csv": {
        "columns": {
            "product_id": "int64",
            "product_name": "object",
            "aisle_id": "int64",
            "department_id": "int64",
        },
        "constraints": {
            "product_id": {"min": 1, "unique": True},
            "aisle_id": {"min": 1},
            "department_id": {"min": 1},
        },
        "min_rows": 1000,
    },
    "aisles.csv": {
        "columns": {
            "aisle_id": "int64",
            "aisle_name": "object",
        },
        "constraints": {
            "aisle_id": {"unique": True},
        },
        "min_rows": 50,
    },
    "departments.csv": {
        "columns": {
            "department_id": "int64",
            "department_name": "object",
        },
        "constraints": {
            "department_id": {"unique": True},
        },
        "min_rows": 5,
    },
    "order_products__train.csv": {
        "columns": {
            "order_id": "int64",
            "product_id": "int64",
            "add_to_cart_order": "int64",
            "reordered": "int64",
        },
        "constraints": {
            "add_to_cart_order": {"min": 1},
            "reordered": {"values": [0, 1]},
        },
        "min_rows": 100000,
    },
}


def validate_schema(data_dir: Path) -> dict:
    """Validate all CSV files against expected schema"""
    results = {}

    for filename, schema in SCHEMAS.items():
        filepath = data_dir / filename
        results[filename] = validate_file(filepath, schema)

    # Summarize
    passed = sum(1 for r in results.values() if r["passed"])
    total = len(results)

    logger.info(f"Schema validation: {passed}/{total} files passed")

    if passed < total:
        failed = [f for f, r in results.items() if not r["passed"]]
        raise ValueError(f"Schema validation failed for: {failed}")

    return results


def validate_file(filepath: Path, schema: dict) -> dict:
    """Validate single file"""
    logger.info(f"Validating {filepath.name}...")

    try:
        df = pd.read_csv(filepath, nrows=10000)  # Sample for speed
    except Exception as e:
        logger.error(f"  ✗ Failed to read: {e}")
        return {"passed": False, "error": str(e)}

    errors = []

    # Check columns exist
    expected_cols = set(schema["columns"].keys())
    actual_cols = set(df.columns)

    missing = expected_cols - actual_cols
    if missing:
        errors.append(f"Missing columns: {missing}")

    extra = actual_cols - expected_cols
    if extra:
        logger.warning(f"  Extra columns: {extra}")

    # Check types
    for col, expected_type in schema["columns"].items():
        if col not in df.columns:
            continue
        actual_type = str(df[col].dtype)
        if actual_type != expected_type:
            errors.append(f"Column {col}: expected {expected_type}, got {actual_type}")

    # Check constraints
    for col, constraints in schema.get("constraints", {}).items():
        if col not in df.columns:
            continue

        if "min" in constraints:
            if (df[col] < constraints["min"]).any():
                errors.append(f"Column {col}: found values < {constraints['min']}")

        if "max" in constraints:
            if (df[col] > constraints["max"]).any():
                errors.append(f"Column {col}: found values > {constraints['max']}")

        if "unique" in constraints and constraints["unique"]:
            dupes = df[col].duplicated().sum()
            if dupes > 0:
                errors.append(f"Column {col}: {dupes} duplicates found")

        if "values" in constraints:
            invalid = ~df[col].isin(constraints["values"])
            if invalid.any():
                errors.append(f"Column {col}: found invalid values {df[invalid][col].unique()}")

    # Check row count
    if len(df) < schema.get("min_rows", 0):
        errors.append(f"Row count {len(df)} < minimum {schema['min_rows']}")

    if errors:
        logger.warning(f"  ✗ {filepath.name}: {len(errors)} errors")
        for err in errors:
            logger.warning(f"    - {err}")
        return {"passed": False, "errors": errors}

    logger.info(f"  ✓ {filepath.name} OK ({len(df)} rows)")
    return {"passed": True, "rows_sampled": len(df)}
