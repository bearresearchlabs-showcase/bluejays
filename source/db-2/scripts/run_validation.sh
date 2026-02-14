#!/bin/bash
# Setup and validate db-2 database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_NAME="db2_validation"

echo "=========================================="
echo "Database 2 Validation Setup"
echo "=========================================="

# Get PostgreSQL path
PG_BIN="/opt/homebrew/opt/postgresql@15/bin"
export PATH="$PG_BIN:$PATH"

# Check if PostgreSQL is running
if ! pg_isready -q 2>/dev/null; then
    echo "Starting PostgreSQL service..."
    brew services start postgresql@15 || true
    sleep 3
fi

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "✓ Database $DB_NAME already exists"
else
    echo "⚠ Database $DB_NAME not found"
    echo "Please import db-2 database first:"
    echo "  createdb $DB_NAME"
    echo "  psql -d $DB_NAME -f <dump_file>.sql"
    exit 1
fi

echo ""
echo "Running validation..."
python3 "$SCRIPT_DIR/validate_db2_simple.py"

echo ""
echo "=========================================="
echo "Validation complete!"
echo "=========================================="
echo "Report: $SCRIPT_DIR/validation_report.json"
