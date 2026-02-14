# Quick Start: Bulk Data Extraction (2-30 GB)

## Prerequisites

```bash
# Install required Python packages
pip install pandas numpy requests sqlalchemy psycopg2-binary

# Optional: Install geopandas for geospatial data (db-7, db-11)
pip install geopandas shapely
```

## Step 1: Set API Keys (Optional but Recommended)

```bash
# Data.gov API key - Get at: https://api.data.gov/signup/
export DATA_GOV_API_KEY="your-api-key-here"

# Census Bureau API key - Get at: https://api.census.gov/data/key_signup.html
export CENSUS_API_KEY="your-api-key-here"
```

## Step 2: Run Extraction

```bash
cd /Users/machine/Documents/AQ/db

# Extract 10 GB for each database (total ~30 GB)
./scripts/run_bulk_extraction.sh

# Or extract individually with custom target size
python3 scripts/bulk_data_extractor.py db-7 --target-gb 10
python3 scripts/bulk_data_extractor.py db-9 --target-gb 10
python3 scripts/bulk_data_extractor.py db-11 --target-gb 10
```

## Step 3: Transform Data

```bash
# Transform extracted data for all databases
for DB in db-7 db-9 db-11; do
    python3 scripts/data_transformer.py $DB
done
```

## Step 4: Verify Results

```bash
# Check extraction sizes
for DB in db-7 db-9 db-11; do
    echo "$DB:"
    cat $DB/data/raw/extraction_metadata.json | jq -r '.total_size_gb' 2>/dev/null || echo "No metadata yet"
done

# Check transformation stats
for DB in db-7 db-9 db-11; do
    echo "$DB:"
    cat $DB/data/transformed/transformation_metadata.json | jq -r '.total_rows_processed' 2>/dev/null || echo "No metadata yet"
done
```

## Expected Output

After extraction, you should have:

- **db-7/data/raw/**: 10-30 GB of maritime shipping data
- **db-9/data/raw/**: 10-30 GB of shipping/logistics data
- **db-11/data/raw/**: 10-30 GB of parking intelligence data

After transformation:

- **db-7/data/transformed/**: Database-ready CSV files
- **db-9/data/transformed/**: Database-ready CSV files
- **db-11/data/transformed/**: Database-ready CSV files

## Scaling to 30 GB

To extract maximum data (30 GB per database):

```bash
# Increase target size
python3 scripts/bulk_data_extractor.py db-7 --target-gb 30
python3 scripts/bulk_data_extractor.py db-9 --target-gb 30
python3 scripts/bulk_data_extractor.py db-11 --target-gb 30
```

## Troubleshooting

**Rate Limiting**: Scripts automatically retry with backoff. API keys increase limits.

**Large Files**: Files are downloaded in chunks automatically.

**Memory Issues**: Processing uses chunked approach (100k rows per chunk).

**Disk Space**: Ensure 100+ GB free space.

## Documentation

- **Detailed Guide**: `scripts/README_BULK_EXTRACTION.md`
- **Summary**: `BULK_DATA_EXTRACTION_SUMMARY.md`
- **Script Help**: `python3 scripts/bulk_data_extractor.py --help`
