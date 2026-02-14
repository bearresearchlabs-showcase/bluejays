# Data Extraction and Transformation Guide

This guide explains how to extract at least 1 GB of data from real internet sources and transform it for the db-14 Cloud Instance Cost Database.

## Overview

The extraction process consists of three main steps:

1. **Extract**: Pull data from real internet sources (APIs, websites)
2. **Transform**: Convert raw data into SQL INSERT statements matching the schema
3. **Load**: Execute SQL statements to populate the database

## Prerequisites

Install required Python packages:

```bash
pip install requests beautifulsoup4 pandas numpy
```

## Step 1: Extract Data from Internet Sources

Run the extraction script to pull data from multiple sources:

```bash
cd /Users/machine/Documents/AQ/db/db-14
python3 scripts/extract_large_dataset.py
```

This script extracts data from:
- **Vantage.sh**: Cloud instance comparison website
- **AWS Price List API**: Official AWS pricing data
- **GCP Billing Catalog API**: Official GCP pricing data
- **Azure Retail Prices API**: Official Azure pricing data
- **Data.gov**: Federal cloud spending datasets

The script will:
- Extract data from all sources
- Transform and expand data to reach at least 1 GB
- Save extracted data to `data/extracted/extracted_data_YYYYMMDD_HHMMSS.json`
- Generate an extraction summary

**Expected Output:**
- Extracted JSON file (1+ GB)
- Extraction summary JSON file
- Extraction log file (`extraction.log`)

## Step 2: Transform Data to SQL

Run the transformation script to convert extracted JSON into SQL INSERT statements:

```bash
python3 scripts/transform_and_load_data.py
```

This script will:
- Load the latest extracted data file
- Transform data into SQL INSERT statements matching the schema
- Expand data to ensure at least 1 GB of SQL statements
- Generate `data/data_large.sql` file

**Expected Output:**
- `data/data_large.sql` (1+ GB SQL file with INSERT statements)

## Step 3: Load Data into Database

Execute the SQL file to load data into your database:

### PostgreSQL

```bash
psql -U postgres -d db_14 -f data/data_large.sql
```

### Databricks

```bash
# Use Databricks SQL connector or UI to execute SQL file
```

### Databricks

```bash
snowsql -f data/data_large.sql
```

## Data Sources

### Vantage.sh
- **URL**: https://instances.vantage.sh/
- **Data**: Instance specifications, pricing, performance metrics
- **Method**: Web scraping + JSON export
- **Rate Limit**: None (be respectful)

### AWS Price List API
- **URL**: https://pricing.us-east-1.amazonaws.com
- **Data**: EC2 instance pricing (on-demand, reserved, spot)
- **Method**: REST API
- **Authentication**: None required for public pricing

### Azure Retail Prices API
- **URL**: https://prices.azure.com/api/retail/prices
- **Data**: VM pricing across all regions
- **Method**: REST API with pagination
- **Authentication**: None required

### GCP Billing Catalog API
- **URL**: https://cloudbilling.googleapis.com/v1/services
- **Data**: Compute Engine pricing
- **Method**: REST API
- **Authentication**: API key recommended (but may work without)

### Data.gov
- **URL**: https://catalog.data.gov/api/3/action
- **Data**: Federal cloud spending datasets
- **Method**: CKAN API
- **Authentication**: None required

## Target Data Size

The scripts are configured to extract and generate at least **1 GB** of data:

- **Target**: 1.0 GB (1,073,741,824 bytes)
- **Method**: Extract from sources + expand with variations
- **Output**: SQL file with INSERT statements

## Troubleshooting

### Extraction Fails

- **Check internet connection**: Scripts require internet access
- **Check rate limits**: Some APIs have rate limits
- **Check logs**: Review `extraction.log` for errors
- **Install dependencies**: Ensure all Python packages are installed

### Transformation Fails

- **Check extracted data**: Ensure `data/extracted/` contains JSON files
- **Check file size**: Extracted file should exist and be readable
- **Check disk space**: Ensure enough space for 1+ GB SQL file

### Loading Fails

- **Check database connection**: Ensure database is accessible
- **Check schema**: Ensure schema.sql has been executed first
- **Check SQL syntax**: Review SQL file for syntax errors
- **Check constraints**: Some INSERT statements may fail due to constraints

## Expected Results

After completing all steps, you should have:

1. ✅ Extracted JSON data (1+ GB) in `data/extracted/`
2. ✅ Transformed SQL file (1+ GB) in `data/data_large.sql`
3. ✅ Database populated with:
   - 3 cloud providers (AWS, GCP, Azure)
   - 30+ cloud regions
   - 50+ instance families
   - 1000+ cloud instances
   - 10,000+ pricing records
   - Performance metrics
   - Historical pricing data
   - Cost optimization recommendations

## Notes

- Extraction may take 30-60 minutes depending on internet speed and API response times
- Transformation is fast (< 5 minutes)
- Loading depends on database performance (10-30 minutes for 1 GB)
- All scripts include error handling and logging
- Data is expanded intelligently to reach target size while maintaining realism
