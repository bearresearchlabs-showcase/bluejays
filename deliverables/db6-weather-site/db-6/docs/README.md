# Weather Data Pipeline Database - Documentation

**Database:** db-6
**Created:** 2026-02-03

## Overview

This database contains weather data from NOAA sources including GRIB2 gridded forecasts, shapefile boundaries (CWA, Fire Zones, Marine Zones), real-time observations, transformation logs, spatial joins, CRS transformations, data quality metrics load status.

## Database Schema

See `../data/schema.sql` for the complete database schema.

### Key Tables

- **grib2_forecasts** - Gridded forecast data from NDFD
- **shapefile_boundaries** - Geographic boundaries (CWA, Fire Zones, Marine Zones)
- **weather_observations** - Real-time point observations from NWS API
- **grib2_transformation_log** - GRIB2 transformation tracking
- **shapefile_integration_log** - Shapefile transformation tracking
- **spatial_join_results** - Spatial join operations documentation
- **crs_transformation_parameters** - CRS transformation parameters
- **data_quality_metrics** - Data quality tracking
- **load_status**  load operations tracking
- **weather_forecast_aggregations** - Pre-aggregated forecast data
- **weather_stations** - Weather station metadata

## Queries

See `../queries/queries.md` for 30 extremely complex SQL queries.

All queries are designed to work across:
- PostgreSQL (with PostGIS)
 (Delta Lake)


## Data Sources

- **GRIB2 Files**: National Digital Forecast Database (NDFD) from tgftp.nws.noaa.gov
- **Shapefiles**: NWS GIS Portal shapefiles from weather.gov/gis
- **Observations**: NWS API (api.weather.gov)

## Usage

1. Load schema: `psql -f data/schema.sql` (PostgreSQL)
2. Load data: `psql -f data/data.sql` (PostgreSQL)
3. Run queries: See `queries/queries.md`

---
**Last Updated:** 2026-02-03
