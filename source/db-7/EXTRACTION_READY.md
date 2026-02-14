# db-7 Data Extraction Ready ✅

## Status: Ready to Extract 1 GB for db-7

All systems configured and validated for **db-7 (Maritime Shipping Intelligence)**.

## Quick Start

```bash
cd /Users/machine/Documents/AQ/db

# Optional: Set API keys for higher rate limits
export DATA_GOV_API_KEY="your-key"  # https://api.data.gov/signup/
export CENSUS_API_KEY="your-key"     # https://api.census.gov/data/key_signup.html

# Extract 1 GB for db-7
./scripts/run_bulk_extraction.sh

# Or run directly
python3 scripts/bulk_data_extractor.py db-7 --target-gb 1

# Transform extracted data
python3 scripts/data_transformer.py db-7

# Verify validation still passes
python3 scripts/validate.py db-7
```

## Data Sources (1 GB Target)

### Data.gov Maritime Datasets
- **5 search queries**: maritime shipping, vessel port, AIS vessel, shipping schedules, port statistics
- **20 datasets per query** (up to 50 results per query)
- **File size limit**: Up to 500 MB per file
- **Total expected**: ~800-900 MB from Data.gov

### Census Bureau Trade Data
- **Dataset**: `timeseries/intltrade/imports`
- **Variables**: I_MKT, I_COMMODITY, I_QTY1, I_VAL_MO
- **Geography**: US-level
- **Years**: 2020-2025 (5 years)
- **Total expected**: ~100-200 MB from Census Bureau

**Total Target**: 1 GB

## Validation Status

```
db-7 Validation Status: PASS ✅

All 30 queries passing validation:
- Query syntax: Valid
- Schema compatibility: Verified
- Cross-database compatibility: PostgreSQL & Databricks ready
```

## Extraction Output

Data will be saved to:
- **Raw data**: `db-7/data/raw/`
- **Transformed data**: `db-7/data/transformed/`
- **Metadata**: `db-7/data/extraction_metadata.json`

## Next Steps

1. **Extract**: Run `./scripts/run_bulk_extraction.sh`
2. **Transform**: Run `python3 scripts/data_transformer.py db-7`
3. **Validate**: Run `python3 scripts/validate.py db-7`
4. **Load**: Load transformed data into PostgreSQL/Databricks (if needed)

## Notes

- Extraction will stop automatically when 1 GB target is reached
- Progress is logged to console
- Failed downloads are retried up to 3 times
- Metadata is saved after extraction completes
