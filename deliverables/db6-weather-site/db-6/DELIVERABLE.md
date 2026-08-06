# Database Deliverable: db-6 - Weather Data Pipeline System

**Database:** db-6
**Type:** Weather Data Pipeline System
**Created:** 2026-02-03
**Status:** Complete

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Database Schema Documentation](#database-schema-documentation)
3. [SQL Queries](#sql-queries)
4. [Usage Instructions](#usage-instructions)

---

## Database Overview

### Description

This database contains weather data from NOAA sources including GRIB2 gridded forecasts, shapefile boundaries (CWA, Fire Zones, Marine Zones), real-time observations, transformation logs, spatial joins, CRS transformations, data quality metrics load status. The system is designed for weather forecasting, spatial analysis, and climate risk assessment applications.

### Key Features

- **GRIB2 Forecast Data**: Gridded numerical weather forecasts from NDFD (National Digital Forecast Database)
- **Geographic Boundaries**: Shapefile data for CWAs (County Warning Areas), Fire Zones, Marine Zones, and River Basins
- **Real-Time Observations**: Point observations from NWS API
- **Spatial Operations**: Geospatial joins and transformations using PostGIS/Databricks GEOGRAPHY types
- **Data Quality Tracking**: Comprehensive metrics for data quality monitoring
- **Transformation Logging**: Complete audit trail for data transformations
- **Multi-Source Integration**: Integration of multiple NOAA data sources

### Database Platforms Supported

- **PostgreSQL**: Full support with PostGIS extension for spatial operations
- **Databricks**: Compatible with Delta Lake and GEOMETRY types
- **Databricks**: Full support with GEOGRAPHY types and spatial functions

### Data Sources

- **GRIB2 Files**: National Digital Forecast Database (NDFD) from `tgftp.nws.noaa.gov`
- **Shapefiles**: NWS GIS Portal shapefiles from `weather.gov/gis`
- **Observations**: NWS API (`api.weather.gov`)

---

## Database Schema Documentation

### Schema Overview

The database consists of **11 tables** organized into logical groups:

1. **Forecast Data**: `grib2_forecasts`
2. **Geographic Boundaries**: `shapefile_boundaries`
3. **Observations**: `weather_observations`, `weather_stations`
4. **Transformation Logs**: `grib2_transformation_log`, `shapefile_integration_log`
5. **Spatial Operations**: `spatial_join_results`, `crs_transformation_parameters`
6. **Data Quality**: `data_quality_metrics`
7. **Load Tracking**: `load_status`
8. **Aggregations**: `weather_forecast_aggregations`

### Table Relationships

```
grib2_forecasts (forecast_id)
    ├── spatial_join_results (forecast_id)
    └── weather_forecast_aggregations (via boundary_id)

shapefile_boundaries (boundary_id)
    ├── spatial_join_results (boundary_id)
    ├── weather_forecast_aggregations (boundary_id)
    └── weather_stations (cwa_code)

weather_observations (observation_id)
    └── weather_stations (station_id)

weather_stations (station_id)
    └── weather_observations (station_id)
```

### Entity-Relationship Diagram

```mermaid
erDiagram
    grib2_forecasts {
        varchar forecast_id PK "Primary key - unique forecast identifier"
        varchar parameter_name "Forecast parameter (Temperature, Precipitation, etc.)"
        timestamp forecast_time "Forecast valid time"
        geography grid_cell_geom SPATIAL "Point geometry for grid cell center"
        numeric parameter_value "Forecast parameter value"
        varchar source_file "Source GRIB2 file name"
        varchar transformation_status "Transformation status"
    }

    shapefile_boundaries {
        varchar boundary_id PK "Primary key - unique boundary identifier"
        varchar feature_type "Feature type (CWA, FireZone, MarineZone, etc.)"
        varchar feature_name "Human-readable feature name"
        varchar feature_identifier "Official feature identifier code"
        geography boundary_geom SPATIAL "Polygon geometry for boundary"
        varchar state_code "US state code (2-letter)"
        varchar office_code "NWS office code (CWA identifier)"
        varchar source_shapefile "Source shapefile name"
        varchar transformation_status "Transformation status"
    }

    weather_observations {
        varchar observation_id PK "Primary key - unique observation identifier"
        varchar station_id FK "Weather station"
        varchar station_name "Station name"
        timestamp observation_time "Observation timestamp"
        geography station_geom SPATIAL "Point geometry for station location"
        numeric temperature "Temperature in degrees Fahrenheit"
        numeric precipitation_amount "Precipitation amount in inches"
        numeric wind_speed "Wind speed in knots"
        varchar data_source "Data source identifier"
    }

    weather_stations {
        varchar station_id PK "Primary key - unique station identifier"
        varchar station_name "Station name"
        geography station_geom SPATIAL "Point geometry for station location"
        numeric elevation_meters "Station elevation in meters"
        varchar state_code "US state code"
        varchar county_name "County name"
        varchar cwa_code "County Warning Area code"
        varchar station_type "Station type (ASOS, AWOS, etc.)"
        boolean active_status "Whether station is currently active"
    }

    spatial_join_results {
        varchar join_id PK "Primary key"
        varchar forecast_id FK "Forecast"
        varchar boundary_id FK "Boundary"
        varchar grib_file "GRIB2 file name"
        varchar shapefile_name "Shapefile name"
        varchar join_type "Join type (Point-in-Polygon, Raster-to-Vector, Clip)"
        integer features_matched "Number of features matched"
        integer features_total "Total features"
        numeric match_percentage "Match percentage"
        timestamp join_timestamp "Join timestamp"
    }

    weather_forecast_aggregations {
        varchar aggregation_id PK "Primary key"
        varchar parameter_name "Forecast parameter name"
        timestamp forecast_time "Forecast valid time"
        varchar boundary_id FK "Boundary"
        varchar feature_type "Feature type"
        varchar feature_name "Feature name"
        numeric min_value "Minimum forecast value"
        numeric max_value "Maximum forecast value"
        numeric avg_value "Average forecast value"
        numeric median_value "Median forecast value"
        integer grid_cells_count "Number of grid cells aggregated"
    }

    grib2_transformation_log {
        varchar log_id PK "Primary key"
        varchar file_name "GRIB2 file name"
        varchar parameter_name "Forecast parameter name"
        varchar transformation_status "Status (Success, Failed, Pending)"
        integer processing_duration_seconds "Processing duration"
        integer records_processed "Number of records processed"
        varchar error_message "Error message if failed"
    }

    shapefile_integration_log {
        varchar log_id PK "Primary key"
        varchar shapefile_name "Shapefile name"
        varchar feature_type "Feature type"
        varchar transformation_status "Status"
        integer processing_duration_seconds "Processing duration"
        varchar error_message "Error message"
    }

    crs_transformation_parameters {
        varchar transformation_id PK "Primary key"
        varchar source_crs "Source CRS identifier"
        varchar target_crs "Target CRS identifier"
        varchar transformation_method "Method (GDAL, PROJ, Custom)"
        numeric accuracy_meters "Transformation accuracy"
        integer usage_count "Number of times used"
    }

    data_quality_metrics {
        varchar metric_id PK "Primary key"
        date metric_date "Metric date"
        varchar data_source "Data source (GRIB2, Shapefile, API)"
        integer files_processed "Number of files processed"
        integer files_successful "Number of successful files"
        integer files_failed "Number of failed files"
        numeric success_rate "Success rate percentage"
        integer total_records "Total records processed"
    }

    load_status {
        varchar load_id PK "Primary key"
        varchar source_file "Source file name"
        varchar target_table "Target table"
        timestamp load_start_time "Load start time"
        timestamp load_end_time "Load end time"
        integer records_loaded "Number of records loaded"
        varchar load_status "Status (Success, Failed, Partial)"
    }

    grib2_forecasts ||--o{ spatial_join_results : "forecast"
    shapefile_boundaries ||--o{ spatial_join_results : "boundary"
    shapefile_boundaries ||--o{ weather_forecast_aggregations : "aggregated_by"
    weather_stations ||--o{ weather_observations : "observes"
    grib2_forecasts }o--o{ shapefile_boundaries : "spatially_joins"
```

---

### Detailed Table Documentation

#### 1. `grib2_forecasts`

Stores gridded forecast data from NDFD (National Digital Forecast Database). Each row represents a forecast value for a specific parameter at a grid cell location and time.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `forecast_id` | `VARCHAR(255)` | No | — | Primary key - unique forecast identifier |
| `parameter_name` | `VARCHAR(100)` | No | — | Forecast parameter (Temperature, Precipitation, WindSpeed, etc.) |
| `forecast_time` | `TIMESTAMP_NTZ` | No | — | Forecast valid time |
| `grid_cell_latitude` | `NUMERIC(10, 7)` | No | — | Grid cell center latitude (WGS84) |
| `grid_cell_longitude` | `NUMERIC(10, 7)` | No | — | Grid cell center longitude (WGS84) |
| `grid_cell_geom` | `GEOGRAPHY` | Yes | `NULL` | Point geometry for grid cell center |
| `parameter_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Forecast parameter value |
| `source_file` | `VARCHAR(500)` | Yes | `NULL` | Source GRIB2 file name |
| `source_crs` | `VARCHAR(50)` | Yes | `NULL` | Source coordinate reference system |
| `target_crs` | `VARCHAR(50)` | Yes | `NULL` | Target CRS (typically WGS84/EPSG:4326) |
| `grid_resolution_x` | `NUMERIC(10, 6)` | Yes | `NULL` | Grid resolution in X direction (degrees) |
| `grid_resolution_y` | `NUMERIC(10, 6)` | Yes | `NULL` | Grid resolution in Y direction (degrees) |
| `spatial_extent_west` | `NUMERIC(10, 6)` | Yes | `NULL` | Western boundary of spatial extent |
| `spatial_extent_south` | `NUMERIC(10, 6)` | Yes | `NULL` | Southern boundary of spatial extent |
| `spatial_extent_east` | `NUMERIC(10, 6)` | Yes | `NULL` | Eastern boundary of spatial extent |
| `spatial_extent_north` | `NUMERIC(10, 6)` | Yes | `NULL` | Northern boundary of spatial extent |
| `load_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | When forecast was loaded |
| `transformation_status` | `VARCHAR(50)` | Yes | `NULL` | Transformation status (Success, Failed, Pending) |

**Indexes:**
- Primary Key: `forecast_id`
- Index: `(parameter_name, forecast_time)`
- Spatial Index: `grid_cell_geom` (GIST index)
- Index: `transformation_status`
- Index: `forecast_time`

**Spatial Data:**
- Uses GEOGRAPHY type for WGS84 coordinates
- Grid cells are represented as points
- Supports spatial queries (ST_WITHIN, ST_DISTANCE, etc.)

---

#### 2. `shapefile_boundaries`

Stores geographic boundaries from shapefiles including CWAs, Fire Zones, Marine Zones, River Basins, and Counties.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `boundary_id` | `VARCHAR(255)` | No | — | Primary key - unique boundary identifier |
| `feature_type` | `VARCHAR(50)` | No | — | Feature type (CWA, FireZone, MarineZone, RiverBasin, County) |
| `feature_name` | `VARCHAR(255)` | Yes | `NULL` | Human-readable feature name |
| `feature_identifier` | `VARCHAR(100)` | Yes | `NULL` | Official feature identifier code |
| `boundary_geom` | `GEOGRAPHY` | Yes | `NULL` | Polygon geometry for boundary |
| `source_shapefile` | `VARCHAR(500)` | Yes | `NULL` | Source shapefile name |
| `source_crs` | `VARCHAR(50)` | Yes | `NULL` | Source coordinate reference system |
| `target_crs` | `VARCHAR(50)` | Yes | `NULL` | Target CRS (typically WGS84/EPSG:4326) |
| `feature_count` | `INTEGER` | Yes | `NULL` | Number of features in original shapefile |
| `spatial_extent_west` | `NUMERIC(10, 6)` | Yes | `NULL` | Western boundary of spatial extent |
| `spatial_extent_south` | `NUMERIC(10, 6)` | Yes | `NULL` | Southern boundary of spatial extent |
| `spatial_extent_east` | `NUMERIC(10, 6)` | Yes | `NULL` | Eastern boundary of spatial extent |
| `spatial_extent_north` | `NUMERIC(10, 6)` | Yes | `NULL` | Northern boundary of spatial extent |
| `load_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | When boundary was loaded |
| `transformation_status` | `VARCHAR(50)` | Yes | `NULL` | Transformation status |
| `state_code` | `VARCHAR(2)` | Yes | `NULL` | US state code (2-letter) |
| `office_code` | `VARCHAR(10)` | Yes | `NULL` | NWS office code (CWA identifier) |

**Indexes:**
- Primary Key: `boundary_id`
- Index: `feature_type`
- Spatial Index: `boundary_geom` (GIST index)
- Index: `state_code`
- Index: `office_code`

**Spatial Data:**
- Uses GEOGRAPHY type for polygon boundaries
- Supports spatial operations (ST_WITHIN, ST_INTERSECTS, ST_DISTANCE, etc.)

---

#### 3. `weather_observations`

Stores real-time point observations from NWS API weather stations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `observation_id` | `VARCHAR(255)` | No | — | Primary key - unique observation identifier |
| `station_id` | `VARCHAR(50)` | No | — | Foreign key to `weather_stations.station_id` |
| `station_name` | `VARCHAR(255)` | Yes | `NULL` | Station name |
| `observation_time` | `TIMESTAMP_NTZ` | No | — | Observation timestamp |
| `station_latitude` | `NUMERIC(10, 7)` | No | — | Station latitude (WGS84) |
| `station_longitude` | `NUMERIC(10, 7)` | No | — | Station longitude (WGS84) |
| `station_geom` | `GEOGRAPHY` | Yes | `NULL` | Point geometry for station location |
| `temperature` | `NUMERIC(6, 2)` | Yes | `NULL` | Temperature in degrees Fahrenheit |
| `dewpoint` | `NUMERIC(6, 2)` | Yes | `NULL` | Dewpoint in degrees Fahrenheit |
| `humidity` | `NUMERIC(5, 2)` | Yes | `NULL` | Relative humidity percentage |
| `wind_speed` | `NUMERIC(6, 2)` | Yes | `NULL` | Wind speed in knots |
| `wind_direction` | `INTEGER` | Yes | `NULL` | Wind direction in degrees (0-359) |
| `pressure` | `NUMERIC(8, 2)` | Yes | `NULL` | Barometric pressure in inches of mercury |
| `visibility` | `NUMERIC(6, 2)` | Yes | `NULL` | Visibility in miles |
| `sky_cover` | `VARCHAR(50)` | Yes | `NULL` | Sky cover description |
| `precipitation_amount` | `NUMERIC(8, 2)` | Yes | `NULL` | Precipitation amount in inches |
| `data_freshness_minutes` | `INTEGER` | Yes | `NULL` | Minutes since observation |
| `load_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | When observation was loaded |
| `data_source` | `VARCHAR(50)` | No | `'NWS_API'` | Data source identifier |

**Indexes:**
- Primary Key: `observation_id`
- Foreign Key: `station_id` → `weather_stations.station_id`
- Index: `(station_id, observation_time)`
- Spatial Index: `station_geom` (GIST index)
- Index: `observation_time`
- Index: `data_source`

---

#### 4. `weather_stations`

Stores metadata about weather observation stations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `station_id` | `VARCHAR(50)` | No | — | Primary key - unique station identifier |
| `station_name` | `VARCHAR(255)` | Yes | `NULL` | Station name |
| `station_latitude` | `NUMERIC(10, 7)` | No | — | Station latitude (WGS84) |
| `station_longitude` | `NUMERIC(10, 7)` | No | — | Station longitude (WGS84) |
| `station_geom` | `GEOGRAPHY` | Yes | `NULL` | Point geometry for station location |
| `elevation_meters` | `NUMERIC(8, 2)` | Yes | `NULL` | Station elevation in meters |
| `state_code` | `VARCHAR(2)` | Yes | `NULL` | US state code |
| `county_name` | `VARCHAR(100)` | Yes | `NULL` | County name |
| `cwa_code` | `VARCHAR(10)` | Yes | `NULL` | County Warning Area code |
| `station_type` | `VARCHAR(50)` | Yes | `NULL` | Station type (ASOS, AWOS, etc.) |
| `active_status` | `BOOLEAN` | No | `TRUE` | Whether station is currently active |
| `first_observation_date` | `DATE` | Yes | `NULL` | First observation date |
| `last_observation_date` | `DATE` | Yes | `NULL` | Last observation date |
| `update_frequency_minutes` | `INTEGER` | Yes | `NULL` | Update frequency in minutes |

**Indexes:**
- Primary Key: `station_id`
- Spatial Index: `station_geom` (GIST index)
- Index: `cwa_code`
- Index: `active_status`
- Index: `state_code`

---

#### 5. `grib2_transformation_log`

Tracks GRIB2 file processing and transformation operations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `log_id` | `VARCHAR(255)` | No | — | Primary key |
| `file_name` | `VARCHAR(500)` | No | — | GRIB2 file name |
| `source_path` | `VARCHAR(1000)` | Yes | `NULL` | Source file path |
| `parameter_name` | `VARCHAR(100)` | No | — | Forecast parameter name |
| `forecast_time` | `TIMESTAMP_NTZ` | Yes | `NULL` | Forecast valid time |
| `source_crs` | `VARCHAR(50)` | Yes | `NULL` | Source CRS |
| `target_crs` | `VARCHAR(50)` | Yes | `NULL` | Target CRS |
| `gdal_command` | `VARCHAR(2000)` | Yes | `NULL` | GDAL command used for transformation |
| `output_file` | `VARCHAR(1000)` | Yes | `NULL` | Output file path |
| `grid_resolution_x` | `NUMERIC(10, 6)` | Yes | `NULL` | Grid resolution X |
| `grid_resolution_y` | `NUMERIC(10, 6)` | Yes | `NULL` | Grid resolution Y |
| `spatial_extent_west` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent west |
| `spatial_extent_south` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent south |
| `spatial_extent_east` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent east |
| `spatial_extent_north` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent north |
| `transformation_status` | `VARCHAR(50)` | Yes | `NULL` | Status (Success, Failed, Pending) |
| `target_table` | `VARCHAR(255)` | Yes | `NULL` | Target table |
| `load_timestamp` | `TIMESTAMP_NTZ` | Yes | `NULL` | Load timestamp |
| `processing_duration_seconds` | `INTEGER` | Yes | `NULL` | Processing duration |
| `records_processed` | `INTEGER` | Yes | `NULL` | Number of records processed |
| `error_message` | `VARCHAR(2000)` | Yes | `NULL` | Error message if failed |

**Indexes:**
- Primary Key: `log_id`
- Index: `file_name`
- Index: `transformation_status`
- Index: `load_timestamp`

---

#### 6. `shapefile_integration_log`

Tracks shapefile processing and coordinate transformations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `log_id` | `VARCHAR(255)` | No | — | Primary key |
| `shapefile_name` | `VARCHAR(500)` | No | — | Shapefile name |
| `source_path` | `VARCHAR(1000)` | Yes | `NULL` | Source file path |
| `feature_type` | `VARCHAR(50)` | No | — | Feature type |
| `feature_count` | `INTEGER` | Yes | `NULL` | Number of features |
| `source_crs` | `VARCHAR(50)` | Yes | `NULL` | Source CRS |
| `target_crs` | `VARCHAR(50)` | Yes | `NULL` | Target CRS |
| `ogr2ogr_command` | `VARCHAR(2000)` | Yes | `NULL` | OGR2OGR command used |
| `transformed_path` | `VARCHAR(1000)` | Yes | `NULL` | Transformed file path |
| `spatial_extent_west` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent west |
| `spatial_extent_south` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent south |
| `spatial_extent_east` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent east |
| `spatial_extent_north` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent north |
| `transformation_status` | `VARCHAR(50)` | Yes | `NULL` | Status |
| `target_table` | `VARCHAR(255)` | Yes | `NULL` | Target table |
| `load_timestamp` | `TIMESTAMP_NTZ` | Yes | `NULL` | Load timestamp |
| `processing_duration_seconds` | `INTEGER` | Yes | `NULL` | Processing duration |
| `error_message` | `VARCHAR(2000)` | Yes | `NULL` | Error message |

**Indexes:**
- Primary Key: `log_id`
- Index: `shapefile_name`
- Index: `transformation_status`

---

#### 7. `spatial_join_results`

Documents spatial join operations between GRIB2 grid cells and shapefile boundaries.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `join_id` | `VARCHAR(255)` | No | — | Primary key |
| `grib_file` | `VARCHAR(500)` | Yes | `NULL` | GRIB2 file name |
| `shapefile_name` | `VARCHAR(500)` | Yes | `NULL` | Shapefile name |
| `join_type` | `VARCHAR(50)` | Yes | `NULL` | Join type (Point-in-Polygon, Raster-to-Vector, Clip) |
| `gdal_command` | `VARCHAR(2000)` | Yes | `NULL` | GDAL command used |
| `features_matched` | `INTEGER` | Yes | `NULL` | Number of features matched |
| `features_total` | `INTEGER` | Yes | `NULL` | Total features |
| `match_percentage` | `NUMERIC(5, 2)` | Yes | `NULL` | Match percentage |
| `output_file` | `VARCHAR(1000)` | Yes | `NULL` | Output file path |
| `join_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Join timestamp |
| `forecast_id` | `VARCHAR(255)` | Yes | `NULL` | Foreign key to `grib2_forecasts.forecast_id` |
| `boundary_id` | `VARCHAR(255)` | Yes | `NULL` | Foreign key to `shapefile_boundaries.boundary_id` |

**Indexes:**
- Primary Key: `join_id`
- Index: `(forecast_id, boundary_id)`
- Index: `join_timestamp`

---

#### 8. `crs_transformation_parameters`

Documents coordinate reference system transformations and parameters.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `transformation_id` | `VARCHAR(255)` | No | — | Primary key |
| `source_crs` | `VARCHAR(50)` | No | — | Source CRS identifier |
| `target_crs` | `VARCHAR(50)` | No | — | Target CRS identifier |
| `source_crs_name` | `VARCHAR(255)` | Yes | `NULL` | Source CRS name |
| `target_crs_name` | `VARCHAR(255)` | Yes | `NULL` | Target CRS name |
| `transformation_method` | `VARCHAR(50)` | Yes | `NULL` | Method (GDAL, PROJ, Custom) |
| `central_meridian` | `NUMERIC(10, 6)` | Yes | `NULL` | Central meridian |
| `false_easting` | `NUMERIC(12, 2)` | Yes | `NULL` | False easting |
| `false_northing` | `NUMERIC(12, 2)` | Yes | `NULL` | False northing |
| `scale_factor` | `NUMERIC(10, 8)` | Yes | `NULL` | Scale factor |
| `latitude_of_origin` | `NUMERIC(10, 6)` | Yes | `NULL` | Latitude of origin |
| `units` | `VARCHAR(50)` | Yes | `NULL` | Units (degrees, meters, feet) |
| `accuracy_meters` | `NUMERIC(10, 2)` | Yes | `NULL` | Transformation accuracy |
| `usage_count` | `INTEGER` | No | `0` | Number of times used |

**Indexes:**
- Primary Key: `transformation_id`
- Index: `(source_crs, target_crs)`

---

#### 9. `data_quality_metrics`

Tracks data quality metrics for weather products.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `metric_id` | `VARCHAR(255)` | No | — | Primary key |
| `metric_date` | `DATE` | No | — | Metric date |
| `data_source` | `VARCHAR(50)` | No | — | Data source (GRIB2, Shapefile, API) |
| `files_processed` | `INTEGER` | No | `0` | Number of files processed |
| `files_successful` | `INTEGER` | No | `0` | Number of successful files |
| `files_failed` | `INTEGER` | No | `0` | Number of failed files |
| `success_rate` | `NUMERIC(5, 2)` | Yes | `NULL` | Success rate percentage |
| `total_records` | `INTEGER` | No | `0` | Total records processed |
| `records_with_errors` | `INTEGER` | No | `0` | Records with errors |
| `error_rate` | `NUMERIC(5, 2)` | Yes | `NULL` | Error rate percentage |
| `spatial_coverage_km2` | `NUMERIC(15, 2)` | Yes | `NULL` | Spatial coverage in square kilometers |
| `temporal_coverage_hours` | `INTEGER` | Yes | `NULL` | Temporal coverage in hours |
| `data_freshness_minutes` | `INTEGER` | Yes | `NULL` | Data freshness in minutes |
| `calculation_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Calculation timestamp |

**Indexes:**
- Primary Key: `metric_id`
- Index: `(metric_date, data_source)`
- Index: `metric_date`

---

#### 10. `load_status`

Tracks data loading operations to Databricks.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `load_id` | `VARCHAR(255)` | No | — | Primary key |
| `source_file` | `VARCHAR(1000)` | Yes | `NULL` | Source file name |
| `target_table` | `VARCHAR(255)` | No | — | Target table |
| `load_start_time` | `TIMESTAMP_NTZ` | No | — | Load start time |
| `load_end_time` | `TIMESTAMP_NTZ` | Yes | `NULL` | Load end time |
| `load_duration_seconds` | `INTEGER` | Yes | `NULL` | Load duration |
| `records_loaded` | `INTEGER` | No | `0` | Number of records loaded |
| `file_size_mb` | `NUMERIC(10, 2)` | Yes | `NULL` | File size in MB |
| `load_rate_mb_per_sec` | `NUMERIC(10, 2)` | Yes | `NULL` | Load rate in MB/sec |
| `load_status` | `VARCHAR(50)` | Yes | `NULL` | Status (Success, Failed, Partial) |
| `error_message` | `VARCHAR(2000)` | Yes | `NULL` | Error message |
| `warehouse` | `VARCHAR(255)` | Yes | `NULL` | Warehouse used |
| `data_source_type` | `VARCHAR(50)` | Yes | `NULL` | Data source type |

**Indexes:**
- Primary Key: `load_id`
- Index: `target_table`
- Index: `load_status`
- Index: `load_start_time`

---

#### 11. `weather_forecast_aggregations`

Pre-aggregated forecast data for performance optimization.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `aggregation_id` | `VARCHAR(255)` | No | — | Primary key |
| `parameter_name` | `VARCHAR(100)` | No | — | Forecast parameter name |
| `forecast_time` | `TIMESTAMP_NTZ` | No | — | Forecast valid time |
| `boundary_id` | `VARCHAR(255)` | Yes | `NULL` | Foreign key to `shapefile_boundaries.boundary_id` |
| `feature_type` | `VARCHAR(50)` | Yes | `NULL` | Feature type |
| `feature_name` | `VARCHAR(255)` | Yes | `NULL` | Feature name |
| `min_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Minimum forecast value |
| `max_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Maximum forecast value |
| `avg_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Average forecast value |
| `median_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Median forecast value |
| `std_dev_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Standard deviation |
| `grid_cells_count` | `INTEGER` | Yes | `NULL` | Number of grid cells aggregated |
| `aggregation_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Aggregation timestamp |

**Indexes:**
- Primary Key: `aggregation_id`
- Index: `(forecast_time, parameter_name)`
- Index: `boundary_id`
- Index: `feature_type`

---

## SQL Queries

This database includes **30 extremely complex SQL queries** designed for production use with business-oriented use cases. All queries are:

- **Cross-database compatible**: Work on PostgreSQL (with PostGIS)
- **Production-grade**: Use advanced SQL patterns including CTEs, recursive CTEs, spatial operations, window functions, and complex aggregations
- **Business-focused**: Each query addresses specific client use cases (insurance risk modeling, agriculture, logistics, etc.)
- **Fully runnable**: No placeholders - ready to execute
- **Well-documented**: Each query includes business use case, description, complexity notes, and expected output

### Query List

The complete list of 30 queries is available in `queries/queries.md`. Each query includes:

1. **Query Number and Title**
2. **Business Use Case**: Real-world application scenario
3. **Description**: What the query achieves
4. **Client Deliverable**: What the query produces for clients
5. **Business Value**: Why this query is valuable
6. **Complexity**: Technical details (CTEs, spatial operations, window functions, etc.)
7. **SQL Code**: Complete, runnable SQL
8. **Expected Output**: Description of result set

### Query Categories

The queries cover the following business use cases:

1. **Insurance Risk Modeling** (Queries 1, 6, 11, 16, 21, 26)
   - Forecast accuracy assessment
   - Regional risk analysis
   - Climate risk correlation
   - Extreme weather event detection

2. **Agriculture & Crop Insurance** (Queries 2, 7, 12, 17, 22, 27)
   - Multi-level geographic hierarchy
   - Crop risk assessment
   - Growing season analysis
   - Regional weather patterns

3. **Logistics & Supply Chain** (Queries 4, 9, 14, 19, 24, 29)
   - Route optimization
   - Station coverage analysis
   - Weather impact on logistics
   - Fleet management

4. **Renewable Energy Planning** (Queries 3, 8, 13, 18, 23, 28)
   - Multi-parameter correlation
   - Energy production forecasting
   - Site selection analysis
   - Climate risk assessment

5. **Emergency Management** (Queries 5, 10, 15, 20, 25, 30)
   - Alert system analysis
   - Emergency response planning
   - Real-time monitoring
   - Risk assessment

### Accessing Queries

**Location**: `queries/queries.md`

**Format**: Each query is numbered sequentially (Query 1 through Query 30) and includes:
- Business use case description
- Complete SQL code in code blocks
- Detailed technical descriptions
- Complexity annotations
- Expected output descriptions

**Example Query Structure**:

```markdown
## Query 1: Production-Grade Spatial Weather Forecast Analysis

**Business Use Case:** Custom Weather Impact Modeling - Regional Forecast Accuracy Assessment for Insurance Risk Modeling

**Description:** Enterprise-level spatial weather forecast analysis...

**Client Deliverable:** Forecast accuracy report by geographic boundary...

**Business Value:** Quantifies forecast reliability for specific geographic regions...

**Complexity:** Deep nested CTEs (7+ levels), spatial operations...

```sql
WITH forecast_parameter_cohorts AS (
    -- SQL code here
)
SELECT ...
```

**Expected Output:** Top 100 most recent forecasts with spatial aggregations...
```

---

## Usage Instructions

### For Data Scientists

#### Prerequisites

1. **Database Access**: Ensure you have access to the database instance (PostgreSQL with PostGIS)
2. **Credentials**: Obtain database connection credentials
3. **Schema**: Ensure all tables are created and populated with data
4. **Spatial Extensions**: For PostgreSQL, ensure PostGIS extension is installed:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

#### Running Queries

1. **Open Query File**: Navigate to `queries/queries.md`
2. **Select Query**: Choose the query number you want to execute
3. **Review Business Case**: Understand the use case and expected output
4. **Copy SQL**: Copy the SQL code from the code block
5. **Execute**: Run the query in your database client:
   - **PostgreSQL**: Use `psql` or pgAdmin (ensure PostGIS is enabled)
   - **Databricks**: Use Databricks SQL editor or notebook
   - **Databricks**: Use Databricks web interface or SnowSQL

#### Understanding Results

- Each query includes a "Business Use Case" section explaining the real-world application
- Review the "Client Deliverable" section to understand what the query produces
- Check the "Expected Output" section for result set descriptions
- Spatial queries return geographic data that can be visualized on maps

#### Notebook Integration (Databricks)

If using Databricks notebooks:

1. Create a new notebook
2. Set the language to SQL
3. Copy the query SQL into a cell
4. Add markdown cells above for context:
   ```markdown
   # Query 1: Spatial Weather Forecast Analysis

   **Business Use Case:** Insurance Risk Modeling

   This query analyzes forecast accuracy by geographic boundary...
   ```
5. Execute the cell to run the query
6. Review results and add visualization cells:
   - Use map visualizations for spatial results
   - Create charts for time-series data
   - Generate tables for aggregated metrics

### For Database Administrators

#### Schema Setup

1. **Create Tables**: Execute the schema creation scripts from `data/schema.sql`
2. **Enable Spatial Extensions**: For PostgreSQL:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
3. **Create Indexes**: Ensure all indexes are created, especially spatial indexes (GIST)
4. **Load Data**: Populate tables with weather data:
   - GRIB2 forecast data
   - Shapefile boundaries
   - Weather observations
5. **Verify**: Run validation queries to ensure data integrity

#### Performance Considerations

- **Spatial Indexes**: Critical for spatial query performance (GIST indexes on GEOGRAPHY columns)
- **Partitioning**: Consider partitioning large tables (`grib2_forecasts`, `weather_observations`) by date
- **Aggregations**: Use `weather_forecast_aggregations` table for pre-computed aggregations
- **Monitoring**: Monitor query execution times, especially for spatial joins
- **Optimization**: Review spatial join strategies and consider spatial clustering

#### Cross-Database Compatibility

- **Spatial Types**:
  - PostgreSQL: Uses PostGIS GEOGRAPHY type
  : Uses GEOMETRY type (compatible)
  : Uses GEOGRAPHY type
- **Spatial Functions**: Standard spatial functions (ST_WITHIN, ST_DISTANCE, ST_INTERSECTS) work across all platforms
- **CRS Handling**: All spatial data uses WGS84 (EPSG:4326) for compatibility
- Test queries on your target database before production use

#### Data Loading

1. **GRIB2 Files**: Use transformation scripts to load GRIB2 data
2. **Shapefiles**: Use OGR2OGR or similar tools to transform and load shapefiles
3. **API Data**: Use ETL pipelines to load real-time observations from NWS API
4. **Monitoring**: Track data quality metrics using `data_quality_metrics` table

---

## Additional Resources

- **Schema Documentation**: See `docs/SCHEMA.md` for detailed schema information
- **Data Sources**: See `docs/DATA_SOURCES.md` for information about NOAA data sources
- **Validation Reports**: See `results/` directory for query validation results
- **Query Metadata**: See `queries/queries.json` for programmatic access to queries
- **ETL Pipeline**: See `research/etl_elt_pipeline.ipynb` for data ingestion workflows

---

**Last Updated**: 2026-02-03
**Version**: 1.0
