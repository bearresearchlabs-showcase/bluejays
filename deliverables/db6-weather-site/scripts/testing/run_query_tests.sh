#!/bin/bash
# Comprehensive SQL Query Testing Script
# Tests all queries from db-1 through db-5 against PostgreSQL

set -e

echo "======================================================================"
echo "COMPREHENSIVE SQL QUERY TESTING"
echo "======================================================================"
echo ""

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import psycopg2" 2>/dev/null || echo "⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary"
echo ""
echo "Environment Variables Required:"
echo "  PostgreSQL:"
echo "    POSTGRES_HOST (default: localhost)"
echo "    POSTGRES_PORT (default: 5432)"
echo "    POSTGRES_DB (default: db{N})"
echo "    POSTGRES_USER (default: postgres)"
echo "    POSTGRES_PASSWORD (default: postgres)"
echo ""

# Run the test script (from repo root)
cd "$(dirname "$0")/../.." && python3 test_queries_postgres.py

echo ""
echo "======================================================================"
echo "Testing complete! Check results/ directories for JSON results files."
echo "======================================================================"
