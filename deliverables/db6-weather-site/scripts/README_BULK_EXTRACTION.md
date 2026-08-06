# Bulk Data Extraction Guide

This guide explains how to extract 2-30 GB of data from internet sources for db-7, db-9, and db-11.

## Overview

The bulk data extraction system pulls large volumes of data from:
- **Data.gov CKAN API**: Federal open data datasets
- **Census Bureau API**: Demographics, trade, and population data
- **NOAA/MARAD**: Maritime shipping data (db-7)
- **City Open Data Portals**: Parking and transportation data (db-11)

## Quick Start

### 1. Set Up API Keys (Optional but Recommended)

```bash
# Data.gov API key (for higher rate limits)
export DATA_GOV_API_KEY="your-api-key-here"
# Get key at: https://api.data.gov/signup/

# Census Bureau API key (for higher rate limits)
export CENSUS_API_KEY="your-api-key-here"
# Get key at: https://api.census.gov/data/key_signup.html
```

### 2. Run Bulk Extraction

```bash
# Extract data for all databases (target: 10 GB each)
cd /Users/machine/Documents/AQ/db
./scripts/run_bulk_extraction.sh

# Or extract for a specific database
python3 scripts/bulk_data_extractor.py db-7 --target-gb 10
python3 scripts/bulk_data_extractor.py db-9 --target-gb 10
python3 scripts/bulk_data_extractor.py db-11 --target-gb 10
```

### 3. Transform Extracted Data

```bash
# Transform data for all databases
for DB in db-7 db-9 db-11; do
    python3 scripts/data_transformer.py $DB
done
```

## Data Sources by Database

### db-7 (Maritime Shipping Intelligence)

**Target: 10-30 GB**

- **Data.gov Maritime Datasets**:
  - Vessel schedules
  - Port statistics
  - AIS vessel tracks
  - Shipping route data

- **Census Bureau Trade Data**:
  - International trade imports/exports (2010-2024)
  - Commodity-level trade statistics
  - Country-level trade patterns

- **NOAA AIS Data** (requires manual download):
  - Vessel traffic data (2009-2024)
  - Quarterly/annual datasets
  - Regional coverage

### db-9 (Shipping Intelligence)

**Target: 10-30 GB**

- **Data.gov Shipping Datasets**:
  - Postal service data
  - Logistics datasets
  - Trade and customs data

- **Census Bureau International Trade**:
  - Import/export statistics (2010-2024)
  - HTSUSA commodity codes
  - Country of origin data
  - Monthly trade data

### db-11 (Parking Intelligence)

**Target: 10-30 GB**

- **Data.gov Parking Datasets**:
  - Parking facility locations (400+ cities)
  - Parking meter data
  - Parking transaction data
  - Transportation datasets

- **Census Bureau Demographics**:
  - ACS 5-year estimates for MSAs
  - Population estimates (2010-2024)
  - Economic data for metropolitan areas

- **BTS TranStats** (airport data):
  - Passenger volumes
  - Airport statistics

## Output Structure

```
db-{N}/
├── data/
│   ├── raw/                    # Raw extracted data
│   │   ├── *.csv               # Extracted CSV files
│   │   ├── *.json              # Extracted JSON files
│   │   └── extraction_metadata.json
│   ├── transformed/            # Transformed data
│   │   ├── transformed_*.csv  # Database-ready CSV files
│   │   └── transformation_metadata.json
│   └── schema.sql             # Database schema
```

## Monitoring Progress

Check extraction metadata:
```bash
cat db-7/data/raw/extraction_metadata.json | jq '.total_size_gb'
cat db-7/data/raw/extraction_metadata.json | jq '.total_files'
```

Check transformation metadata:
```bash
cat db-7/data/transformed/transformation_metadata.json | jq '.total_rows_processed'
```

## Scaling to 30 GB

To extract more data (up to 30 GB):

1. **Increase dataset limits**:
   ```python
   # In bulk_data_extractor.py
   datasets = self.extract_data_gov_datasets(query, limit=200)  # Increase from 100
   ```

2. **Extract more years**:
   ```python
   years=list(range(2000, 2025))  # 25 years instead of 15
   ```

3. **Include more geographic regions**:
   ```python
   geography='state:*'  # All states instead of just MSAs
   ```

4. **Download larger files**:
   ```python
   self.download_data_gov_resources(dataset, max_size_mb=5000)  # 5 GB files
   ```

## Troubleshooting

### Rate Limiting
- Use API keys for higher rate limits
- Scripts include automatic retry logic
- Add delays between requests if needed

### Large Files
- Files are downloaded in chunks
- Progress is logged during download
- Failed downloads are retried automatically

### Memory Issues
- Data is processed in chunks (100k rows)
- Use `--chunk-size` parameter to adjust
- Consider processing files individually

## Next Steps

After extraction and transformation:

1. **Load into Database**:
   ```bash
   # Use database-specific load scripts
   python3 db-7/scripts/load_data.py
   ```

2. **Validate Data Quality**:
   ```bash
   python3 db-7/scripts/validate_data_quality.py
   ```

3. **Generate Reports**:
   ```bash
   python3 db-7/scripts/generate_data_quality_report.py
   ```

## Notes

- **API Keys**: Store in environment variables, never commit to git
- **Rate Limits**: Respect API rate limits, scripts include backoff logic
- **Data Size**: Actual data size depends on available datasets and API responses
- **Storage**: Ensure sufficient disk space (30+ GB recommended)
- **Time**: Large extractions can take several hours
