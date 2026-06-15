#!/usr/bin/env python3
"""
Download Instacart Market Basket Analysis dataset from Kaggle.
Requires: kaggle API credentials at ~/.kaggle/kaggle.json

Setup:
1. Create Kaggle account at kaggle.com
2. Go to account settings and download kaggle.json
3. Place at ~/.kaggle/kaggle.json
4. Run: python scripts/download_dataset.py
"""

import os
import sys
from pathlib import Path

def download_dataset():
    try:
        import kaggle
    except ImportError:
        print("❌ kaggle not installed. Run: pip install kaggle")
        sys.exit(1)

    # Check credentials
    kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_config.exists():
        print("❌ Kaggle credentials not found at ~/.kaggle/kaggle.json")
        print("   1. Sign up at kaggle.com")
        print("   2. Download API token from account settings")
        print("   3. Place kaggle.json at ~/.kaggle/kaggle.json")
        sys.exit(1)

    # Download dataset
    download_dir = Path("data/raw")
    download_dir.mkdir(parents=True, exist_ok=True)

    print("📥 Downloading Instacart Market Basket Analysis...")
    kaggle.api.dataset_download_files(
        "c1441346d7c74f38ef6f8f8fa3590874",
        path=download_dir,
        unzip=True
    )
    print(f"✅ Dataset downloaded to {download_dir}")
    print("\nFiles:")
    for f in sorted(download_dir.glob("*.csv")):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name}: {size_mb:.1f} MB")

if __name__ == "__main__":
    download_dataset()
