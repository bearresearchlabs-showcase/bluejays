#!/bin/bash
# Data Extraction Runner Script for db-11
# Extracts 1 GB of data from internet sources

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_DIR="$(dirname "$SCRIPT_DIR")"
cd "$DB_DIR"

echo "======================================================================"
echo "Data Extraction - db-11 Parking Intelligence Database"
echo "======================================================================"
echo "Target: 1 GB of data"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Check required packages
echo "Checking Python dependencies..."
python3 -c "import requests, pandas, json" 2>/dev/null || {
    echo "Error: Missing required packages. Install with:"
    echo "  pip install requests pandas geopandas shapely openpyxl"
    exit 1
}

# Create directories
mkdir -p research/extracted_data
mkdir -p metadata

# Run extraction
echo ""
echo "Starting data extraction..."
echo "This may take a while depending on network speed and data size..."
echo ""

python3 scripts/extract_and_transform_data.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "Extraction Complete!"
    echo "======================================================================"
    echo ""
    echo "Next steps:"
    echo "  1. Review extracted data: ls -lh research/extracted_data/"
    echo "  2. Check metadata: cat metadata/data_extraction_metadata.json | jq ."
    echo "  3. Transform and load: python3 scripts/transform_and_load_data.py"
    echo ""
else
    echo ""
    echo "Extraction completed with errors. Check logs above."
    exit $EXIT_CODE
fi
