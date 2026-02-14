# Research Directory - db-11

This directory contains research notebooks, experimental analysis, ETL/ELT pipelines, and development work for the Parking Intelligence Database.

## Contents

- `etl_elt_pipeline.ipynb` - Main ETL/ELT pipeline notebook
- `data_resources.json` - Data source documentation and API resources
- `source_metadata.json` - Comprehensive source metadata tracking

## ETL/ELT Pipeline

The `etl_elt_pipeline.ipynb` notebook provides a comprehensive framework for:

### Extract Phase
- **Data.gov CKAN API**: Search and download parking facility datasets
- **Census Bureau API**: Fetch metropolitan area and city demographics
- **BTS TranStats**: Extract airport passenger volumes (web scraping/CSV)
- **FHWA**: Download traffic volume data
- **City Open Data Portals**: Extract real-time parking utilization data

### Transform Phase
- Data cleaning and normalization
- Coordinate validation and geospatial transformations
- Data type conversions and standardization
- Handling missing values and outliers

### Load Phase
- Load data into PostgreSQL (with PostGIS)
- Load data into 
- Handle upserts and incremental loads
- Optimize load performance

### Validate Phase
- Data quality metrics calculation
- Completeness checks
- Consistency validation
- Accuracy verification

### Monitor Phase
- Pipeline execution tracking
- Performance metrics collection
- Error logging and alerting
- Metadata generation and storage

## Data Sources

See `data_resources.json` for detailed documentation of all data sources, including:
- API endpoints and authentication
- Rate limits and usage guidelines
- Data formats and coordinate systems
- Best practices and usage notes

See `source_metadata.json` for comprehensive source tracking including:
- Detailed API endpoint configurations
- Extraction history with timestamps
- Data lineage tracking
- Source system categorization

## Target Data Size

The pipeline is designed to collect **1 GB** of parking intelligence data across:
- 400+ metropolitan areas and cities
- 500+ airports
- 1,000+ stadiums and venues
- 50,000+ parking facilities
- 100,000+ pricing records
- 1,000,000+ utilization records
- 100,000+ market intelligence metrics

## Usage

See `.cursor/rules/research-metadata-directories.mdc` for detailed usage guidelines.

---
**Last Updated:** 2026-02-04
