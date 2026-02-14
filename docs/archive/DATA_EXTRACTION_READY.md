# Data Extraction Ready - 1 GB Target

## ✅ Status: Ready to Extract 1 GB per Database

All systems are ready to extract **1 GB of data** from internet sources for each database (db-7, db-9, db-11).

## Quick Start

```bash
cd /Users/machine/Documents/AQ/db

# Optional: Set API keys for higher rate limits
export DATA_GOV_API_KEY="your-key"  # https://api.data.gov/signup/
export CENSUS_API_KEY="your-key"     # https://api.census.gov/data/key_signup.html

# Extract 1 GB for each database
./scripts/run_bulk_extraction.sh

# Or extract individually
python3 scripts/bulk_data_extractor.py db-7 --target-gb 1
python3 scripts/bulk_data_extractor.py db-9 --target-gb 1
python3 scripts/bulk_data_extractor.py db-11 --target-gb 1

# Transform extracted data
for DB in db-7 db-9 db-11; do
    python3 scripts/data_transformer.py $DB
done

# Verify validation
python3 scripts/validate.py db-7 db-9 db-11
```

## Data Sources (1 GB Target)

### db-7 (Maritime Shipping Intelligence)
- **Data.gov**: Maritime datasets (5 queries, 20 datasets each, up to 500 MB files)
- **Census Bureau**: Trade data (2020-2025, imports)
- **Target**: 1 GB

### db-9 (Shipping Intelligence)
- **Data.gov**: Shipping datasets (5 queries, 20 datasets each, up to 500 MB files)
- **Census Bureau**: Trade data (2020-2025, imports + exports)
- **Target**: 1 GB

### db-11 (Parking Intelligence)
- **Data.gov**: Parking datasets (5 queries, 25 datasets each, up to 200 MB files)
- **Census Bureau**: Demographics (2020-2024, ACS + population estimates)
- **Target**: 1 GB

**Total**: 3 GB across all databases

## Validation Status

```
db-7 Validation Status: PASS ✅
db-9 Validation Status: PASS ✅
db-11 Validation Status: PASS ✅
```

All databases passing validation and ready for data extraction.
