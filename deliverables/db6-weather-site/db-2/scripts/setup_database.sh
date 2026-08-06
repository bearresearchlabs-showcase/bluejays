#!/bin/bash
# Setup db-2 database from dump file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_NAME="db2_validation"
PG_BIN="/opt/homebrew/opt/postgresql@15/bin"
export PATH="$PG_BIN:$PATH"

echo "=========================================="
echo "Database 2 Setup"
echo "=========================================="

# Check for dump file
DUMP_FILE=""
if [ -f "$SCRIPT_DIR/database.sql" ]; then
    DUMP_FILE="$SCRIPT_DIR/database.sql"
elif [ -f "$SCRIPT_DIR/../db-4/extracted/_SharedAI/DATABASE (2)" ]; then
    # Look for db-2 dump in db-4
    DUMP_FILE=$(find "$SCRIPT_DIR/../db-4" -name "*db-2*.sql" -o -name "*airplane*.sql" -o -name "*seydam*.sql" | head -1)
fi

if [ -z "$DUMP_FILE" ] || [ ! -f "$DUMP_FILE" ]; then
    echo "⚠ Database dump file not found"
    echo ""
    echo "Please provide a database dump file:"
    echo "  1. Place dump file at: $SCRIPT_DIR/database.sql"
    echo "  2. Or update DUMP_FILE in this script"
    echo ""
    echo "Then run: $0"
    exit 1
fi

echo "Found dump file: $DUMP_FILE"

# Check if PostgreSQL is running
if ! pg_isready -q 2>/dev/null; then
    echo "Starting PostgreSQL service..."
    brew services start postgresql@15 || true
    sleep 3
fi

# Create database (drop if exists)
echo "Creating database: $DB_NAME"
dropdb --if-exists "$DB_NAME" 2>/dev/null || true
createdb "$DB_NAME"

# Import dump
echo "Importing database dump..."
echo "This may take a few minutes..."
psql -d "$DB_NAME" -f "$DUMP_FILE" 2>&1 | grep -v "does not exist" | grep -v "extension" | grep -v "pg_graphql" | grep -v "supabase_vault" | grep -v "pg_stat_statements" | grep -v "pgcrypto" | grep -v "pgjwt" | grep -v "uuid-ossp" | tail -20 || true

echo ""
echo "✓ Database imported successfully"
echo ""
echo "You can now run validation:"
echo "  python3 $SCRIPT_DIR/validate_db2_simple.py"
