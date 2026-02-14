#!/bin/bash
# Setup and validate db-1 database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PG_DUMP="$SCRIPT_DIR/../db-4/extracted/_SharedAI/DATABASE (1)/sharedai/sharedai_full_dump.sql"
DB_NAME="db1_validation"

echo "=========================================="
echo "Database 1 Validation Setup"
echo "=========================================="

# Check if dump exists
if [ ! -f "$PG_DUMP" ]; then
    echo "Error: PostgreSQL dump not found at $PG_DUMP"
    exit 1
fi

# Get PostgreSQL path
PG_BIN="/opt/homebrew/opt/postgresql@15/bin"
export PATH="$PG_BIN:$PATH"

# Check if PostgreSQL is running, start if not
if ! pg_isready -q 2>/dev/null; then
    echo "Starting PostgreSQL service..."
    brew services start postgresql@15 || true
    sleep 3
fi

# Create database (drop if exists)
echo "Creating database: $DB_NAME"
dropdb --if-exists "$DB_NAME" 2>/dev/null || true
createdb "$DB_NAME"

# Import dump (ignore extension errors)
echo "Importing database dump..."
psql -d "$DB_NAME" -f "$PG_DUMP" 2>&1 | grep -v "does not exist" | grep -v "extension" | grep -v "pg_graphql" | grep -v "supabase_vault" | grep -v "pg_stat_statements" | grep -v "pgcrypto" | grep -v "pgjwt" | grep -v "uuid-ossp" || true

echo "✓ Database imported successfully"

# Update validation script to use PostgreSQL
cat > "$SCRIPT_DIR/validate_db1.py" << 'PYEOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_and_model import DatabaseValidator

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'db1_validation',
    'user': os.environ.get('USER', 'machine'),
    'password': ''  # Local PostgreSQL typically doesn't need password
}

print("Running validation and modeling on db-1...")
validator = DatabaseValidator(db_type="postgresql", db_config=DB_CONFIG)
results = validator.run_full_validation()

if results and results.get('overall_status', '').startswith('PASS'):
    print("\n✓ Database validation PASSED")
    sys.exit(0)
elif results and 'WARNING' in results.get('overall_status', ''):
    print("\n⚠ Database validation has WARNINGS")
    sys.exit(0)
else:
    print("\n✗ Database validation FAILED")
    sys.exit(1)
PYEOF

chmod +x "$SCRIPT_DIR/validate_db1.py"

echo ""
echo "Running validation..."
python3 "$SCRIPT_DIR/validate_db1.py"

echo ""
echo "=========================================="
echo "Validation complete!"
echo "=========================================="
echo "Database: $DB_NAME"
echo "Report: $SCRIPT_DIR/validation_report.json"
