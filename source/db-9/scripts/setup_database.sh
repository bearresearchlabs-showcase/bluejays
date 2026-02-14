#!/bin/bash
# Setup script for db-9 shipping intelligence database
# Compatible with PostgreSQL

set -e

DB_NAME="${DB_NAME:-shipping_intelligence_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo "Setting up db-9 shipping intelligence database..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_DIR="$(dirname "$SCRIPT_DIR")"

# PostgreSQL setup
if command -v psql &> /dev/null; then
    echo "Creating PostgreSQL database..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE IF NOT EXISTS $DB_NAME;" 2>/dev/null || psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "SELECT 1;" -d "$DB_NAME" || true

    echo "Loading schema..."
    if [ -f "$DB_DIR/data/schema.sql" ]; then
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$DB_DIR/data/schema.sql"
        echo "✓ Schema loaded successfully"
    else
        echo "⚠ Schema file not found: $DB_DIR/data/schema.sql"
    fi

    echo "Loading sample data..."
    if [ -f "$DB_DIR/data/data.sql" ]; then
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$DB_DIR/data/data.sql"
        echo "✓ Sample data loaded successfully"
    else
        echo "⚠ Data file not found: $DB_DIR/data/data.sql"
    fi

    echo "PostgreSQL setup complete!"
else
    echo "PostgreSQL not found. Skipping PostgreSQL setup."
fi

# Databricks setup (requires databricks CLI or connection string)
if command -v databricks &> /dev/null; then
    echo "Databricks CLI found. Use databricks-sql-connector for setup."
    echo "See scripts/setup_snowflake.py for Databricks setup example."
else
    echo "Databricks CLI not found. Skipping Databricks setup."
fi

# Snowflake setup (requires snowflake-connector-python)
if python3 -c "import snowflake.connector" 2>/dev/null; then
    echo "Snowflake connector available. Run scripts/setup_snowflake.py for Snowflake setup."
else
    echo "Snowflake connector not available. Skipping Snowflake setup."
fi

echo "Database setup complete!"
echo ""
echo "Next steps:"
echo "1. Verify schema: psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\\dt'"
echo "2. Verify data: psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c 'SELECT COUNT(*) FROM shipping_carriers;'"
echo "3. Run queries: See queries/queries.md for SQL queries"
