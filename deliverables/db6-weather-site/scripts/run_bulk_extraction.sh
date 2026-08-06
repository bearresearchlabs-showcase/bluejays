#!/bin/bash
# Bulk Data Extraction Script
# Extracts 1 GB of data from internet sources for db-7

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "======================================================================"
echo "Bulk Data Extraction - db-7 (Maritime Shipping Intelligence)"
echo "Target: 1 GB"
echo "======================================================================"

# Check for API keys
if [ -z "$DATA_GOV_API_KEY" ]; then
    echo "⚠️  DATA_GOV_API_KEY not set (optional but recommended)"
    echo "   Get API key at: https://api.data.gov/signup/"
fi

if [ -z "$CENSUS_API_KEY" ]; then
    echo "⚠️  CENSUS_API_KEY not set (optional but recommended)"
    echo "   Get API key at: https://api.census.gov/data/key_signup.html"
fi

echo ""
echo "======================================================================"
echo "Extracting data for db-7"
echo "Target: 1 GB"
echo "======================================================================"

cd "$DB_DIR/db-7"

# Run extraction with target of 1 GB
python3 "$SCRIPT_DIR/bulk_data_extractor.py" db-7 --target-gb 1

if [ $? -eq 0 ]; then
    echo "✓ Successfully extracted data for db-7"
    echo "  Total extracted: ~1 GB"
else
    echo "✗ Failed to extract data for db-7"
    exit 1
fi

echo ""
echo "======================================================================"
echo "Bulk Data Extraction Complete - db-7"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Review extracted data in db-7/data/raw/"
echo "2. Transform data: python3 scripts/data_transformer.py db-7"
echo "3. Verify validation: python3 scripts/validate.py db-7"
echo ""
