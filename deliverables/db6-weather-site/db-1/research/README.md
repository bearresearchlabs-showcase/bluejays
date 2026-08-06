# Research Directory - DB-1

**Purpose:** This directory contains research notebooks, analysis scripts, and experimental work related to database db-1.

## Contents

- **etl_elt_pipeline.ipynb**: Comprehensive ETL/ELT pipeline notebook for data extraction, transformation, and loading operations
- **data_resources.json**: Documentation of all data sources, APIs, and resources used in ETL pipelines
- **source_metadata.json**: Comprehensive source metadata tracking and data lineage

## Usage

The ETL/ELT pipeline notebook provides:
1. **Extract**: Load data from source systems
   - Local files (CSV, JSON, SQL)
   - **Data.gov API** - Federal open data portal (CKAN API)
   - **National Weather Service API** - Weather forecasts and alerts
   - **GeoPlatform.gov API** - Federal geospatial data platform (FAIR principles)
2. **Transform**: Clean, validate, and transform data
3. **Load**: Load transformed data into target databases (PostgreSQL)
4. **Validate**: Verify data quality and completeness
5. **Monitor**: Track pipeline performance and errors

## Data Sources

### Data.gov Integration

- **CKAN API**: Search and access metadata for federal datasets
  - Base URL: `https://catalog.data.gov/api/3/action`
  - Documentation: https://data.gov/developers/apis/
  - No API key required for metadata access
- **api.data.gov**: Access actual dataset files from federal agencies
  - Base URL: `https://api.data.gov`
  - Requires API key (sign up at https://api.data.gov/signup/)
  - Rate limit: 1,000 requests/hour per API key

### National Weather Service Integration

- **API Base**: `https://api.weather.gov`
- **Documentation**: https://weather-gov.github.io/api/
- **Key Features**:
  - Points endpoint: Get forecast office info for coordinates
  - Gridpoint forecasts: Raw numerical forecast data
  - Active alerts: Weather alerts and warnings
- **Requirements**:
  - User-Agent header required
  - Coordinates must use WGS84 (EPSG:4326)
  - Maximum 4 decimal places precision
- **No API key required**

### GeoPlatform.gov Integration

- **GeoAPI**: Search for geospatial datasets
  - Base URL: `https://geoapi.geoplatform.gov`
  - Documentation: https://geoapi.geoplatform.gov
  - No API key required
- **STAC API**: SpatioTemporal Asset Catalog interface
  - Base URL: `https://stac.geoplatform.gov`
  - Documentation: https://stac.geoplatform.gov
  - Collections endpoint: Get all STAC collections
  - Search endpoint: Search catalog for geospatial items
- **Key Features**:
  - NGDA (National Geospatial Data Assets) across 18 themes
  - Multiple data formats: GeoJSON, GeoPackage, Shapefile, WMS, WFS
  - Artifact Catalog: Automatically converted data files
  - Tile Service Catalog: Map tiles in various formats
  - Map Services Catalog: WMS/WFS services
- **Authority**: Geospatial Data Act of 2018
- **No API key required**

## Resource Documentation

All data sources and API endpoints are documented in two complementary files:

**`data_resources.json`** - Quick reference:
- API endpoints and documentation links
- Configuration requirements
- Usage examples and best practices
- Rate limits and usage guidelines
- Current datasets accessed

**`source_metadata.json`** - Comprehensive tracking:
- Detailed API endpoint configurations
- Authentication methods and requirements
- Data format specifications
- Extraction history with timestamps
- Data lineage tracking
- Source system categorization
- NGDA theme associations

## Notes

- Notebooks in this directory are for research and development purposes
- Results and outputs may be experimental
- See `../metadata/` for pipeline execution metadata
- API keys should be stored as environment variables, not hardcoded
- Respect API rate limits and terms of service

---
**Last Updated:** 2026-02-03
