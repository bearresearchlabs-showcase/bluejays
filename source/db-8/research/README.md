# Research Directory - db-8

This directory contains research notebooks, experimental analysis, ETL/ELT pipelines, and development work for job market intelligence database.

## Contents

- `etl_elt_pipeline.ipynb` - Main ETL/ELT pipeline notebook for job data ingestion
- `data_resources.json` - Data source documentation and API resources
- `source_metadata.json` - Comprehensive source metadata tracking

## Data Sources

### USAJobs.gov API
- Base URL: `https://api.usajobs.gov`
- Endpoint: `/jobs` - Search federal job listings
- Authentication: API key required
- Documentation: https://developer.usajobs.gov/

### Bureau of Labor Statistics (BLS) Public Data API
- Base URL: `https://api.bls.gov/publicAPI`
- Version 2.0: Requires registration, 500 daily queries
- Data: Employment statistics, job openings, projections
- Documentation: https://www.bls.gov/developers/

### Department of Labor Open Data Portal
- Base URL: `https://data.dol.gov`
- API access with visualization tools
- Documentation: https://data.dol.gov/

## Usage

See `.cursor/rules/research-metadata-directories.mdc` for detailed usage guidelines.

---
**Last Updated:** 2026-02-04
