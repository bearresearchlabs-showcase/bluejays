# Data Extraction Configured - 1 GB Target ✅

## Status: Ready to Extract 1 GB per Database

All extraction scripts have been configured to target **1 GB of data** per database (db-7, db-9, db-11).

## Configuration Changes

- **Default target**: Reduced from 10 GB to **1 GB**
- **Search queries**: Reduced from 10 to **5 per database**
- **Datasets per query**: Reduced from 50-200 to **20-25**
- **File size limit**: Reduced from 1-2 GB to **200-500 MB**
- **Year ranges**: Reduced from 20 years to **5 years (2020-2025)**
- **Geographic levels**: Reduced to **US-level and MSA-level** only

## Quick Start

```bash
cd /Users/machine/Documents/AQ/db

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

## Expected Data Volumes

| Database | Target Size |
|----------|-------------|
| db-7     | 1 GB        |
| db-9     | 1 GB        |
| db-11    | 1 GB        |
| **Total**| **3 GB**    |

## Validation Status

```
db-7 Validation Status: PASS ✅
db-9 Validation Status: PASS ✅
db-11 Validation Status: PASS ✅

Overall Status: PASS ✅
```

**All databases passing validation and ready for 1 GB data extraction.**
