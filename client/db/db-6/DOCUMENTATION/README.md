---
title: Weather Data Pipeline System — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-6
---

# Weather Data Pipeline System — Documentation

**Database:** db-6  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Purpose

This database supports analytics for weather data pipeline systems. It integrates GRIB2 forecasts, shapefile boundaries, weather stations, observations, spatial joins, CRS transformations, and data quality metrics. Queries use PostGIS geography types, spatial operations, and window functions for forecast aggregation, boundary analysis, and pipeline monitoring.

---

## Use Case

Target use cases for db-6:

- **Forecast aggregation:** GRIB2 parameters by boundary, grid cell statistics, spatial joins
- **Weather observations:** Station data, temperature/dewpoint/humidity trends, data freshness
- **Pipeline monitoring:** Transformation logs, load status, data quality metrics
- **Spatial analytics:** Point-in-polygon, distance queries, CRS transformations

---

## Business Value

Weather pipeline databases represent high-value domains for text-to-SQL because:

- Queries require spatial reasoning (geography types, ST_Distance, ST_Within)
- Multi-source integration (GRIB2, shapefiles, API) demands complex CTEs
- Stakeholders need forecast aggregation and pipeline health dashboards
- Evidence bridges natural-language questions to schema-grounded SQL

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_6
```

---

### Step 3: Load Schema

From the database directory, load `schema.sql` to create tables, indexes, and constraints. PostGIS extension required for spatial columns.

```bash
psql -U postgres -d db_6 -f DATABASE/schema.sql
```

---

### Step 4: Load Data (Optional)

Load sample data from `data.sql` if available.

```bash
psql -U postgres -d db_6 -f DATABASE/data.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

PostgreSQL 14+ with PostGIS extension for geography columns. Disk: 500 MB minimum for spatial data.

---

## Schema Overview

**Total tables:** 11

- `grib2_forecasts` — (see data dictionary)
- `shapefile_boundaries` — (see data dictionary)
- `weather_observations` — (see data dictionary)
- `grib2_transformation_log` — (see data dictionary)
- `shapefile_integration_log` — (see data dictionary)
- `spatial_join_results` — (see data dictionary)
- `crs_transformation_parameters` — (see data dictionary)
- `data_quality_metrics` — (see data dictionary)
- `load_status` — (see data dictionary)
- `weather_forecast_aggregations` — (see data dictionary)
- `weather_stations` — (see data dictionary)

---

## Data Dictionary

### `grib2_forecasts`

- `forecast_id` VARCHAR(255) PRIMARY KEY
- `parameter_name` VARCHAR(100) NOT NULL
- `forecast_time` TIMESTAMP NOT NULL
- `grid_cell_latitude` NUMERIC(10, 7) NOT NULL
- `grid_cell_longitude` NUMERIC(10, 7) NOT NULL
- `grid_cell_geom` TEXT  — Point geometry for grid cell center (PostgreSQL)
- `parameter_value` NUMERIC(10, 2) 
- `source_file` VARCHAR(500) 
- `source_crs` VARCHAR(50) 
- `target_crs` VARCHAR(50) 
- `grid_resolution_x` NUMERIC(10, 6) 
- `grid_resolution_y` NUMERIC(10, 6) 
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `load_timestamp` TIMESTAMP 
- `transformation_status` VARCHAR(50) 

### `shapefile_boundaries`

- `boundary_id` VARCHAR(255) PRIMARY KEY
- `feature_type` VARCHAR(50) NOT NULL — 'CWA', 'FireZone', 'MarineZone', 'RiverBasin', 'County'
- `feature_name` VARCHAR(255) 
- `feature_identifier` VARCHAR(100) 
- `boundary_geom` TEXT  — Polygon geometry
- `source_shapefile` VARCHAR(500) 
- `source_crs` VARCHAR(50) 
- `target_crs` VARCHAR(50) 
- `feature_count` INTEGER 
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `load_timestamp` TIMESTAMP 
- `transformation_status` VARCHAR(50) 
- `state_code` VARCHAR(2) 
- `office_code` VARCHAR(10) 

### `weather_observations`

- `observation_id` VARCHAR(255) PRIMARY KEY
- `station_id` VARCHAR(50) NOT NULL
- `station_name` VARCHAR(255) 
- `observation_time` TIMESTAMP NOT NULL
- `station_latitude` NUMERIC(10, 7) NOT NULL
- `station_longitude` NUMERIC(10, 7) NOT NULL
- `station_geom` TEXT  — Point geometry
- `temperature` NUMERIC(6, 2) 
- `dewpoint` NUMERIC(6, 2) 
- `humidity` NUMERIC(5, 2) 
- `wind_speed` NUMERIC(6, 2) 
- `wind_direction` INTEGER 
- `pressure` NUMERIC(8, 2) 
- `visibility` NUMERIC(6, 2) 
- `sky_cover` VARCHAR(50) 
- `precipitation_amount` NUMERIC(8, 2) 
- `data_freshness_minutes` INTEGER 
- `load_timestamp` TIMESTAMP 
- `data_source` VARCHAR(50) 

### `grib2_transformation_log`

- `log_id` VARCHAR(255) PRIMARY KEY
- `file_name` VARCHAR(500) NOT NULL
- `source_path` VARCHAR(1000) 
- `parameter_name` VARCHAR(100) NOT NULL
- `forecast_time` TIMESTAMP 
- `source_crs` VARCHAR(50) 
- `target_crs` VARCHAR(50) 
- `gdal_command` VARCHAR(2000) 
- `output_file` VARCHAR(1000) 
- `grid_resolution_x` NUMERIC(10, 6) 
- `grid_resolution_y` NUMERIC(10, 6) 
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `transformation_status` VARCHAR(50) 
- `target_table` VARCHAR(255) 
- `load_timestamp` TIMESTAMP 
- `processing_duration_seconds` INTEGER 
- `records_processed` INTEGER 
- `error_message` VARCHAR(2000) 

### `shapefile_integration_log`

- `log_id` VARCHAR(255) PRIMARY KEY
- `shapefile_name` VARCHAR(500) NOT NULL
- `source_path` VARCHAR(1000) 
- `feature_type` VARCHAR(50) NOT NULL
- `feature_count` INTEGER 
- `source_crs` VARCHAR(50) 
- `target_crs` VARCHAR(50) 
- `ogr2ogr_command` VARCHAR(2000) 
- `transformed_path` VARCHAR(1000) 
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `transformation_status` VARCHAR(50) 
- `target_table` VARCHAR(255) 
- `load_timestamp` TIMESTAMP 
- `processing_duration_seconds` INTEGER 
- `error_message` VARCHAR(2000) 

### `spatial_join_results`

- `join_id` VARCHAR(255) PRIMARY KEY
- `grib_file` VARCHAR(500) 
- `shapefile_name` VARCHAR(500) 
- `join_type` VARCHAR(50)  — 'Point-in-Polygon', 'Raster-to-Vector', 'Clip'
- `gdal_command` VARCHAR(2000) 
- `features_matched` INTEGER 
- `features_total` INTEGER 
- `match_percentage` NUMERIC(5, 2) 
- `output_file` VARCHAR(1000) 
- `join_timestamp` TIMESTAMP 
- `forecast_id` VARCHAR(255) 
- `boundary_id` VARCHAR(255) 

### `crs_transformation_parameters`

- `transformation_id` VARCHAR(255) PRIMARY KEY
- `source_crs` VARCHAR(50) NOT NULL
- `target_crs` VARCHAR(50) NOT NULL
- `source_crs_name` VARCHAR(255) 
- `target_crs_name` VARCHAR(255) 
- `transformation_method` VARCHAR(50)  — 'GDAL', 'PROJ', 'Custom'
- `central_meridian` NUMERIC(10, 6) 
- `false_easting` NUMERIC(12, 2) 
- `false_northing` NUMERIC(12, 2) 
- `scale_factor` NUMERIC(10, 8) 
- `latitude_of_origin` NUMERIC(10, 6) 
- `units` VARCHAR(50)  — 'degrees', 'meters', 'feet'
- `accuracy_meters` NUMERIC(10, 2) 
- `usage_count` INTEGER 

### `data_quality_metrics`

- `metric_id` VARCHAR(255) PRIMARY KEY
- `metric_date` DATE NOT NULL
- `data_source` VARCHAR(50) NOT NULL — 'GRIB2', 'Shapefile', 'API'
- `files_processed` INTEGER 
- `files_successful` INTEGER 
- `files_failed` INTEGER 
- `success_rate` NUMERIC(5, 2) 
- `total_records` INTEGER 
- `records_with_errors` INTEGER 
- `error_rate` NUMERIC(5, 2) 
- `spatial_coverage_km2` NUMERIC(15, 2) 
- `temporal_coverage_hours` INTEGER 
- `data_freshness_minutes` INTEGER 
- `calculation_timestamp` TIMESTAMP 

### `load_status`

- `load_id` VARCHAR(255) PRIMARY KEY
- `source_file` VARCHAR(1000) 
- `target_table` VARCHAR(255) NOT NULL
- `load_start_time` TIMESTAMP NOT NULL
- `load_end_time` TIMESTAMP 
- `load_duration_seconds` INTEGER 
- `records_loaded` INTEGER 
- `file_size_mb` NUMERIC(10, 2) 
- `load_rate_mb_per_sec` NUMERIC(10, 2) 
- `load_status` VARCHAR(50)  — 'Success', 'Failed', 'Partial'
- `error_message` VARCHAR(2000) 
- `warehouse` VARCHAR(255) 
- `data_source_type` VARCHAR(50) 

### `weather_forecast_aggregations`

- `aggregation_id` VARCHAR(255) PRIMARY KEY
- `parameter_name` VARCHAR(100) NOT NULL
- `forecast_time` TIMESTAMP NOT NULL
- `boundary_id` VARCHAR(255) 
- `feature_type` VARCHAR(50) 
- `feature_name` VARCHAR(255) 
- `min_value` NUMERIC(10, 2) 
- `max_value` NUMERIC(10, 2) 
- `avg_value` NUMERIC(10, 2) 
- `median_value` NUMERIC(10, 2) 
- `std_dev_value` NUMERIC(10, 2) 
- `grid_cells_count` INTEGER 
- `aggregation_timestamp` TIMESTAMP 

### `weather_stations`

- `station_id` VARCHAR(50) PRIMARY KEY
- `station_name` VARCHAR(255) 
- `station_latitude` NUMERIC(10, 7) NOT NULL
- `station_longitude` NUMERIC(10, 7) NOT NULL
- `station_geom` TEXT 
- `elevation_meters` NUMERIC(8, 2) 
- `state_code` VARCHAR(2) 
- `county_name` VARCHAR(100) 
- `cwa_code` VARCHAR(10) 
- `station_type` VARCHAR(50) 
- `active_status` BOOLEAN 
- `first_observation_date` DATE 
- `last_observation_date` DATE 
- `update_frequency_minutes` INTEGER 

---

## Query Documentation

See `QUERIES/queries.md` for 30 production SQL queries with full business context, evidence, and expected output. Queries cover spatial joins, forecast aggregation, weather observations, pipeline monitoring, and CRS transformations.

---

*Generated by documentation workflow. MDX-compatible markdown.*
