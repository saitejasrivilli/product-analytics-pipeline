"""
PII detection for raw CSV files.
Flags: email addresses, phone numbers, SSN, credit card, IP addresses, etc.
"""

import logging
import re
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

# PII patterns
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}


def check_pii(data_dir: Path) -> dict:
    """Scan CSV files for PII"""
    results = {}

    csv_files = list(data_dir.glob("*.csv"))
    logger.info(f"Scanning {len(csv_files)} CSV files for PII...")

    for filepath in csv_files:
        results[filepath.name] = check_file(filepath)

    # Summarize
    total_pii_found = sum(len(r.get("pii_found", [])) for r in results.values())

    if total_pii_found > 0:
        logger.warning(f"⚠️ Found {total_pii_found} potential PII fields:")
        for filename, result in results.items():
            if result.get("pii_found"):
                logger.warning(f"  {filename}: {result['pii_found']}")
    else:
        logger.info("✓ No PII detected")

    return results


def check_file(filepath: Path) -> dict:
    """Check single file for PII"""
    try:
        df = pd.read_csv(filepath, nrows=1000)
    except Exception as e:
        logger.warning(f"Could not read {filepath.name}: {e}")
        return {"error": str(e)}

    pii_found = []

    for col in df.columns:
        if df[col].dtype == "object":
            col_str = df[col].astype(str).str.lower()

            for pii_type, pattern in PII_PATTERNS.items():
                matches = col_str.str.contains(pattern, regex=True, na=False).sum()

                if matches > 0:
                    pii_found.append(
                        f"{col} ({pii_type}: {matches} matches)"
                    )

    return {
        "file": filepath.name,
        "rows_scanned": len(df),
        "pii_found": pii_found,
        "clean": len(pii_found) == 0,
    }
