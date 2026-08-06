# Weather Data Pipeline Database - db-6

**Deliverable:** db-6
**Status:** ✅ Complete (Extended for Insurance Rate Modeling)
**Created:** 2026-02-03
**Extended:** 2026-02-03 (Insurance Rate Modeling)

## Overview

This database contains weather data from NOAA sources including GRIB2 gridded forecasts, shapefile boundaries (CWA, Fire Zones, Marine Zones), real-time observations, transformation logs, spatial joins, CRS transformations, data quality metrics load status.

**Insurance Extension:** The database has been extended to support insurance rate table determination using 7-14 day forecasts from December 3-17, 2025. This enables insurance companies to calculate dynamic rates based on forecasted weather risks.

## Structure

```
db-6/
├── queries/
│   └── queries.md          # 30+ extremely complex SQL queries
├── results/
│   └── *.json              # Test results and validation reports
├── docs/
│   └── *.md                 # Additional documentation
├── data/
│   ├── schema.sql          # Database schema
│   └── data.sql            # Sample data
└── scripts/
    └── *.py, *.sh          # Utility scripts
```

## Contents

- **Queries:** 30 extremely complex SQL queries in `queries/queries.md` (business-oriented use cases)
  - **Queries 1-14:** Weather data pipeline analysis queries (forecast accuracy, spatial analysis, pattern detection)
  - **Queries 15-24:** Insurance rate modeling queries (7-14 day forecasts, Dec 3-17, 2025)
  - **Queries 25-30:** NEXRAD and satellite imagery transformation queries (US-wide composites, storm tracking, fire detection)
- **Results:** JSON test results in `results/`
- **Documentation:** Database documentation in `docs/`
- **Data:** Schema and data files in `data/`
  - **Insurance Schema:** `data/insurance_schema.sql` - Insurance-specific tables and extensions
  - **NEXRAD/Satellite Schema:** `data/nexrad_satellite_schema.sql` - NEXRAD radar and satellite imagery tables

## Database Schema

### Core Weather Data Tables

- `grib2_forecasts` - Gridded forecast data from NDFD
- `shapefile_boundaries` - Geographic boundaries (CWA, Fire Zones, Marine Zones)
- `weather_observations` - Real-time point observations from NWS API
- `grib2_transformation_log` - GRIB2 transformation tracking
- `shapefile_integration_log` - Shapefile transformation tracking
- `spatial_join_results` - Spatial join operations documentation
- `crs_transformation_parameters` - CRS transformation parameters
- `data_quality_metrics` - Data quality tracking
- `load_status`  load operations tracking
- `weather_forecast_aggregations` - Pre-aggregated forecast data
- `weather_stations` - Weather station metadata

### Insurance Rate Modeling Tables

- `insurance_policy_areas` - Maps geographic boundaries to insurance policy coverage areas
- `insurance_risk_factors` - Calculated risk factors based on weather forecasts (7-14 days ahead)
- `insurance_rate_tables` - Calculated rate tables based on forecast risk factors
- `insurance_claims_history` - Historical claims data for validation and comparison
- `forecast_rate_mapping` - Maps specific forecasts to rate calculations
- `rate_table_comparison` - Compares rates across different forecast days (7-14 days)

### NEXRAD and Satellite Imagery Tables

- `nexrad_radar_sites` - NEXRAD radar site metadata (160+ sites across US)
- `nexrad_level2_data` - Decompressed NEXRAD Level II radar data
- `nexrad_reflectivity_grid` - Gridded reflectivity data for spatial analysis
- `nexrad_velocity_grid` - Gridded velocity data for wind analysis
- `nexrad_storm_cells` - Storm cell tracking and movement analysis
- `satellite_imagery_sources` - Satellite source metadata (GOES-16, GOES-17, GOES-18)
- `satellite_imagery_products` - Decompressed satellite imagery products
- `satellite_imagery_grid` - Aggregated satellite imagery data
- `us_wide_composite_products` - Composite products combining NEXRAD and satellite data
- `nexrad_transformation_log` - NEXRAD transformation tracking
- `satellite_transformation_log` - Satellite transformation tracking

## Usage

### Weather Data Pipeline Queries

See `queries/queries.md` for SQL queries 1-14 covering weather data pipeline analysis (forecast accuracy, spatial analysis, pattern detection, extreme events).

### Insurance Rate Modeling Queries

See `queries/queries.md` for SQL queries 15-24 covering insurance rate modeling:

- **Query 15:** Insurance Risk Factor Calculation from 7-14 Day Forecasts
- **Query 16:** Insurance Rate Table Generation from Forecast Risk Factors
- **Query 17:** Rate Table Comparison Across 7-14 Day Forecasts
- **Query 18:** Historical Claims Validation Against Forecast Risk Factors
- **Query 19:** Rate Volatility and Stability Analysis
- **Query 20:** Policy Area Risk Ranking and Comparison
- **Query 21:** Forecast-to-Rate Impact Analysis
- **Query 22:** Multi-Day Forecast Ensemble Rate Analysis
- **Query 23:** Forecast Day Selection Optimization
- **Query 24:** Comprehensive Insurance Rate Modeling Summary

### NEXRAD and Satellite Imagery Queries

See `queries/queries.md` for SQL queries 25-30 covering NEXRAD and satellite transformations:

- **Query 25:** US-Wide NEXRAD Reflectivity Composite Generation
- **Query 26:** NEXRAD Storm Cell Tracking and Movement Analysis
- **Query 27:** US-Wide Satellite Imagery Cloud Composite Generation
- **Query 28:** NEXRAD-Satellite Data Fusion for Precipitation Estimation
- **Query 29:** Satellite Fire Detection and Monitoring Across US
- **Query 30:** US-Wide Composite Product Generation (NEXRAD + Satellite)

### Insurance Rate Modeling Period

All insurance queries (15-24) are designed for:
- **Forecast Period:** December 3-17, 2025
- **Forecast Days:** 7-14 days ahead
- **Purpose:** Determine insurance rate tables based on forecasted weather risks

### Results and Documentation

See `results/` for test results.
See `docs/` for database documentation.
See `data/insurance_schema.sql` for insurance schema extensions.

## Compatibility

All queries are designed to work across:
- PostgreSQL (with PostGIS)
 (Delta Lake)


---
**Last Updated:** 2026-02-03
