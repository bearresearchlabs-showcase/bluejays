# Database Schema Documentation - db-6

**Created:** 2026-02-03

## Schema Overview

The weather data pipeline database consists of 11 main tables designed to store and track weather data from multiple NOAA sources.

## Tables

### grib2_forecasts
Stores gridded forecast data from NDFD (National Digital Forecast Database).

**Key Columns:**
- `forecast_id` (VARCHAR, PK)
- `parameter_name` (VARCHAR) - e.g., 'Temperature', 'Precipitation', 'WindSpeed'
- `forecast_time` (TIMESTAMP_NTZ)
- `grid_cell_latitude`, `grid_cell_longitude` (NUMERIC)
- `grid_cell_geom` (GEOGRAPHY) - Point geometry for grid cell center
- `parameter_value` (NUMERIC)
- `source_file` (VARCHAR)
- `transformation_status` (VARCHAR)

### shapefile_boundaries
Stores geographic boundaries (CWA, Fire Zones, Marine Zones, River Basins).

**Key Columns:**
- `boundary_id` (VARCHAR, PK)
- `feature_type` (VARCHAR) - 'CWA', 'FireZone', 'MarineZone', 'RiverBasin', 'County'
- `feature_name` (VARCHAR)
- `boundary_geom` (GEOGRAPHY) - Polygon geometry
- `state_code` (VARCHAR)
- `office_code` (VARCHAR)

### weather_observations
Stores point observations from NWS API.

**Key Columns:**
- `observation_id` (VARCHAR, PK)
- `station_id` (VARCHAR)
- `observation_time` (TIMESTAMP_NTZ)
- `station_latitude`, `station_longitude` (NUMERIC)
- `station_geom` (GEOGRAPHY) - Point geometry
- `temperature`, `precipitation_amount`, `wind_speed` (NUMERIC)
- `data_freshness_minutes` (INTEGER)

### grib2_transformation_log
Tracks GRIB2 file processing and transformation operations.

**Key Columns:**
- `log_id` (VARCHAR, PK)
- `file_name` (VARCHAR)
- `parameter_name` (VARCHAR)
- `transformation_status` (VARCHAR)
- `processing_duration_seconds` (INTEGER)
- `error_message` (VARCHAR)

### shapefile_integration_log
Tracks shapefile processing and coordinate transformations.

**Key Columns:**
- `log_id` (VARCHAR, PK)
- `shapefile_name` (VARCHAR)
- `feature_type` (VARCHAR)
- `transformation_status` (VARCHAR)
- `processing_duration_seconds` (INTEGER)

### spatial_join_results
Documents spatial join operations between GRIB2 grid cells and shapefile boundaries.

**Key Columns:**
- `join_id` (VARCHAR, PK)
- `join_type` (VARCHAR) - 'Point-in-Polygon', 'Raster-to-Vector', 'Clip'
- `features_matched` (INTEGER)
- `match_percentage` (NUMERIC)

### crs_transformation_parameters
Documents coordinate reference system transformations and parameters.

**Key Columns:**
- `transformation_id` (VARCHAR, PK)
- `source_crs`, `target_crs` (VARCHAR)
- `transformation_method` (VARCHAR) - 'GDAL', 'PROJ', 'Custom'
- `accuracy_meters` (NUMERIC)

### data_quality_metrics
Tracks data quality metrics for weather products.

**Key Columns:**
- `metric_id` (VARCHAR, PK)
- `metric_date` (DATE)
- `data_source` (VARCHAR) - 'GRIB2', 'Shapefile', 'API'
- `files_processed`, `files_successful`, `files_failed` (INTEGER)
- `success_rate` (NUMERIC)

### load_status
Tracks data loading operations to Databricks.

**Key Columns:**
- `load_id` (VARCHAR, PK)
- `target_table` (VARCHAR)
- `load_start_time`, `load_end_time` (TIMESTAMP_NTZ)
- `records_loaded` (INTEGER)
- `load_status` (VARCHAR)

### weather_forecast_aggregations
Pre-aggregated forecast data for performance.

**Key Columns:**
- `aggregation_id` (VARCHAR, PK)
- `parameter_name` (VARCHAR)
- `forecast_time` (TIMESTAMP_NTZ)
- `boundary_id` (VARCHAR)
- `min_value`, `max_value`, `avg_value`, `median_value` (NUMERIC)

### weather_stations
Metadata about weather observation stations.

**Key Columns:**
- `station_id` (VARCHAR, PK)
- `station_name` (VARCHAR)
- `station_latitude`, `station_longitude` (NUMERIC)
- `station_geom` (GEOGRAPHY)
- `cwa_code` (VARCHAR)
- `active_status` (BOOLEAN)

## Spatial Data Types

The database uses GEOGRAPHY type for spatial data:
- **PostgreSQL**: PostGIS GEOGRAPHY type
- **Databricks**: GEOMETRY type (compatible)
- **Databricks**: GEOGRAPHY type

## Indexes

Spatial indexes are created on geometry columns using GIST indexes for optimal spatial query performance.

---
**Last Updated:** 2026-02-03
