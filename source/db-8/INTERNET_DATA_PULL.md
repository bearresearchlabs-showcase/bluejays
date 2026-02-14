# Internet Data Pull - 1 GB Requirement

## Overview

This document describes how db-8 pulls **minimum 1 GB of data from internet sources** and transforms it for database loading.

## Data Sources

### 1. Data.gov CKAN API (Primary Source)

**No API Key Required** for metadata access and public dataset downloads.

- **Base URL**: `https://catalog.data.gov/api/3/action`
- **Search Terms**: employment, jobs, labor, workforce, occupation, wage, salary, career, job market, unemployment
- **Data Formats**: CSV, JSON, XML
- **Volume**: Can pull hundreds of datasets, each potentially 10-100 MB
- **Script**: `scripts/pull_internet_data.py` → `pull_data_gov_datasets()`

### 2. BLS Public Data API

**No API Key Required** (but rate limits apply without key).

- **Base URL**: `https://api.bls.gov/publicAPI/v2/timeseries/data`
- **Series IDs**: Unemployment rates, employment levels, labor force data
- **Data Format**: JSON time series
- **Volume**: Historical data (10-15 years) for multiple series
- **Script**: `scripts/pull_internet_data.py` → `pull_bls_public_data()`

### 3. USAJobs.gov API (If API Key Configured)

**API Key Required** - Register at https://developer.usajobs.gov/APIRequest/Index

- **Base URL**: `https://data.usajobs.gov/api`
- **Endpoints**: `/Search`, `/Job/{JobID}`
- **Data Format**: JSON
- **Volume**: Thousands of federal job postings
- **Script**: `scripts/incremental_update.py` → `incremental_load_usajobs()`

### 4. DOL Open Data Portal (Via Data.gov)

**No API Key Required** for public datasets.

- **Base URL**: `https://catalog.data.gov/api/3/action`
- **Filter**: `organization:dol-gov`
- **Data Formats**: CSV, JSON, XML
- **Volume**: Employment statistics, wage data, job market trends
- **Script**: `scripts/incremental_update.py` → `incremental_load_dol()`

## Data Pull Process

### Phase 1: Pull from Internet Sources

```bash
cd db-8
python3 scripts/pull_internet_data.py --output-dir data/internet_pulled --target-gb 1.0
```

**What it does**:
1. Searches Data.gov for employment/job-related datasets
2. Downloads CSV/JSON/XML resources from datasets
3. Pulls BLS time series data (5 years historical)
4. Saves all data to `data/internet_pulled/`

**Expected Volume**: 1-2 GB (depending on dataset sizes)

### Phase 2: Transform Internet Data

```bash
python3 scripts/data_transformation_pipeline.py --input-dir data/internet_pulled --output-dir data/internet_transformed
```

**What it does**:
1. Cleans and normalizes CSV files
2. Handles various data formats
3. Validates data quality
4. Saves transformed data to `data/internet_transformed/`

### Phase 3: Combine with Synthetic Data

The `run_30gb_integration.sh` script combines:
- **Synthetic Data**: ~35 GB (generated locally)
- **Internet-Pulled Data**: 5-20 GB (from public APIs)
- **Total**: 40-55 GB (exceeds 10-30 GB requirement)

## Volume Verification

```bash
python3 scripts/verify_data_volume.py --data-dir data
```

**Checks**:
- Generated files: `data/generated/`
- Transformed files: `data/transformed/`
- Internet-pulled files: `data/internet_pulled/`
- Internet-transformed files: `data/internet_transformed/`
- Database tables (if connected)

**Requirement**: Total volume must be at least 1 GB

## Data Transformation

All internet-pulled data goes through transformation:

1. **CSV Files**: 
   - Normalized string fields
   - Cleaned whitespace
   - Validated formats

2. **JSON Files**:
   - Parsed and validated
   - Converted to structured format
   - Ready for database loading

3. **XML Files**:
   - Parsed and converted
   - Structured for database

## Integration with Master Script

The `run_30gb_integration.sh` script includes:

```bash
# Phase 5: Pull Data from Internet Sources
python3 scripts/pull_internet_data.py --output-dir data/internet_pulled --target-gb 15.0

# Phase 6: Transform Internet Data
python3 scripts/data_transformation_pipeline.py --input-dir data/internet_pulled --output-dir data/internet_transformed
```

## API Keys (Optional)

For enhanced data pulling:

1. **USAJobs API Key**: 
   - Register: https://developer.usajobs.gov/APIRequest/Index
   - Set: `export USAJOBS_API_KEY='your-key'`
   - Set: `export USAJOBS_USER_AGENT='YourApp/1.0 (contact@example.com)'`

2. **BLS Registration Key**:
   - Register: https://www.bls.gov/developers/api_signature.htm
   - Set: `export BLS_REGISTRATION_KEY='your-key'`
   - Increases rate limits from 500/day to 50,000/day

3. **Data.gov API Key**:
   - Register: https://api.data.gov/signup/
   - Set: `export DATA_GOV_API_KEY='your-key'`
   - Increases rate limits

## Rate Limits

- **Data.gov**: 1,000 requests/hour (without key), 10,000/hour (with key)
- **BLS**: 500 requests/day (without key), 50,000/day (with key)
- **USAJobs**: 100 requests/minute, 1,000/hour, 10,000/day

All scripts include retry logic and rate limiting.

## Data Quality

All internet-pulled data is:
- Validated for format correctness
- Cleaned and normalized
- Checked for completeness
- Tracked with metadata (source, pull date, size)

## Monitoring

Check pull results:
```bash
cat db-8/results/internet_data_pull_*.json
```

Check transformation results:
```bash
cat db-8/results/transformation_report_*.json
```

## Troubleshooting

1. **No data pulled**: Check internet connection, API availability
2. **Small volume**: Increase `max_datasets` parameter
3. **Rate limit errors**: Add API keys or reduce request frequency
4. **Transformation errors**: Check file formats, ensure CSV/JSON compatibility

## Next Steps

1. Run `pull_internet_data.py` to pull data from internet sources
2. Run `data_transformation_pipeline.py` to transform pulled data
3. Run `verify_data_volume.py` to verify 10-30 GB requirement is met
4. Load transformed data into database using `bulk_load_data.py`

---
**Last Updated**: 2026-02-04
