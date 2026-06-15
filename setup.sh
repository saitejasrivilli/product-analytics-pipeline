#!/bin/bash
# Setup script for product-analytics-pipeline on M2 Mac

set -e

echo "🔨 Setting up product-analytics-pipeline..."

# 1. Create Python venv
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Setup PostgreSQL (if not already running)
echo "🗄️ Setting up PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL not found. Installing via Homebrew..."
    brew install postgresql@15
fi

# Start PostgreSQL if not running
if ! brew services list | grep postgresql@15 | grep -q started; then
    echo "Starting PostgreSQL..."
    brew services start postgresql@15
fi

# Create databases
createdb product_analytics_warehouse 2>/dev/null || echo "Database already exists"
createdb product_analytics_operational 2>/dev/null || echo "Database already exists"

# 4. Initialize dbt project
echo "🌿 Initializing dbt project..."
mkdir -p dbt
cat > dbt/dbt_project.yml << 'EOF'
name: 'product_analytics'
version: '1.0.0'
config-version: 2

profile: 'product_analytics'

model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]
target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  product_analytics:
    staging:
      materialized: view
      tags: ["staging"]
    marts:
      materialized: table
      tags: ["marts"]
EOF

# Create profiles.yml template
cat > dbt/.dbt_profiles_template.yml << 'EOF'
product_analytics:
  outputs:
    duckdb_dev:
      type: duckdb
      path: './data/warehouse.duckdb'
      schema: analytics
      threads: 4
      timeout_seconds: 300

    postgres_operational:
      type: postgres
      host: localhost
      port: 5432
      user: postgres
      pass: password
      dbname: product_analytics_operational
      schema: public
      threads: 4

  target: duckdb_dev
EOF

echo "🔐 Created .dbt_profiles_template.yml. Update with your credentials and save as profiles.yml"

# 5. Create data directories
echo "📁 Creating data directories..."
mkdir -p data/raw data/processed

# 6. Display next steps
echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Download Instacart dataset: python scripts/download_dataset.py"
echo "2. Create dbt profiles: cp dbt/.dbt_profiles_template.yml dbt/profiles.yml && edit as needed"
echo "3. Initialize dbt: cd dbt && dbt debug"
echo "4. Load raw data: python scripts/load_raw_data.py"
echo "5. Run dbt models: dbt run"
echo ""
