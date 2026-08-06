# Data Extraction and Transformation Guide - db-11

## Overview

This guide explains how to extract 1 GB of parking intelligence data from internet sources and transform it for loading into the database.

## Prerequisites

1. **Python Dependencies**: Install required packages
   ```bash
   pip install -r ../scripts/requirements.txt
   pip install requests pandas geopandas shapely openpyxl
   ```

2. **API Keys (Optional but Recommended)**:
   - Data.gov API Key: Sign up at https://api.data.gov/signup/
   - Census API Key: Register at https://api.census.gov/data/key_signup.html
   
   Set environment variables:
   ```bash
   export DATA_GOV_API_KEY='your-key-here'
   export CENSUS_API_KEY='your-key-here'
   ```

3. **Database Setup** (Optional for transformation):
   - PostgreSQL with PostGIS extension
   - Or Databricks connection configured

## Data Extraction Process

### Step 1: Extract Data from Internet Sources

Run the extraction script to pull data from all documented sources:

```bash
cd /Users/machine/Documents/AQ/db/db-11
python3 scripts/extract_and_transform_data.py
```

**What it does:**
- Searches Data.gov CKAN API for parking datasets (target: 100-200 datasets)
- Downloads parking facility data from multiple cities
- Fetches Census Bureau demographic data for MSAs and cities
- Downloads FAA airport passenger statistics
- Extracts data from city open data portals (Seattle, San Francisco, Austin, Philadelphia, etc.)
- Tracks total data size and ensures minimum 1 GB target

**Output:**
- Extracted files saved to `research/extracted_data/`
- Metadata saved to `metadata/data_extraction_metadata.json`
- Total data size tracked and reported

### Step 2: Transform and Load Data

After extraction, transform the raw data into database-ready format:

```bash
python3 scripts/transform_and_load_data.py
```

**What it does:**
- Transforms Data.gov parking data into `parking_facilities` table format
- Transforms Census data into `metropolitan_areas` and `cities` tables
- Transforms airport data into `airports` table format
- Loads transformed data into PostgreSQL (if configured)
- Validates data quality and completeness

## Data Sources and Expected Sizes

### 1. Data.gov Parking Datasets
- **Source**: Data.gov CKAN API
- **Expected Size**: 1-15 GB (depending on number of datasets)
- **Data Types**: CSV, JSON, GeoJSON, Shapefiles
- **Coverage**: 200+ parking datasets from various cities

### 2. Census Bureau Data
- **Source**: Census Bureau API
- **Expected Size**: 100-500 MB
- **Data Types**: JSON
- **Coverage**: All MSAs and cities in USA

### 3. Airport Data
- **Source**: FAA and BTS TranStats
- **Expected Size**: 50-200 MB
- **Data Types**: Excel, CSV
- **Coverage**: Top 50+ airports by passenger volume

### 4. City Open Data Portals
- **Source**: City-specific open data portals
- **Expected Size**: 500 MB - 5 GB
- **Data Types**: JSON, CSV, GeoJSON
- **Coverage**: Major cities (Seattle, San Francisco, Austin, Philadelphia, etc.)

### 5. Traffic Volume Data
- **Source**: FHWA
- **Expected Size**: 100-500 MB
- **Data Types**: CSV, Excel, PDF
- **Coverage**: National traffic monitoring locations

### 6. Additional Sources (for larger datasets)
- **Stadium/Venue Data**: Sports stadiums and event venues
- **Business District Data**: Commercial area boundaries
- **Historical Parking Utilization**: Time-series parking data

## Total Target: 1 GB

The extraction script will continue pulling data until it reaches at least 1 GB target.

## Monitoring Extraction Progress

Check extraction progress:

```bash
# View extraction metadata
cat metadata/data_extraction_metadata.json | jq .

# Check extracted files
ls -lh research/extracted_data/

# Check total size
du -sh research/extracted_data/
```

## Troubleshooting

### Issue: API Rate Limits
**Solution**: 
- Use API keys for higher rate limits
- The script includes automatic retry logic with exponential backoff
- Check rate limit status in extraction metadata

### Issue: Large File Downloads Fail
**Solution**:
- Check available disk space (need 30+ GB free)
- Verify network connection stability
- Script includes timeout handling and retry logic

### Issue: Transformation Errors
**Solution**:
- Check data format compatibility
- Verify required Python packages are installed
- Review transformation logs for specific errors

## Next Steps

After data extraction and transformation:

1. **Validate Data Quality**: Run data quality checks
2. **Load to Database**: Use `transform_and_load_data.py` to load into PostgreSQL/Databricks
3. **Run Queries**: Execute the 30 complex SQL queries in `queries/queries.md`
4. **Monitor Pipeline**: Track pipeline execution in `metadata/pipeline_metadata.json`

## Data Retention

- **Raw Data**: Stored in `research/extracted_data/` (can be archived after transformation)
- **Transformed Data**: Loaded into database tables
- **Metadata**: Tracked in `metadata/` directory for data lineage

## Support

For issues or questions:
- Check `metadata/data_extraction_metadata.json` for extraction details
- Review `research/data_resources.json` for API documentation
- Check logs for specific error messages
