---
title: Weather Data Pipeline System — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-6
---

# Weather Data Pipeline System — Documentation

**Database:** db-6  
**Content:** Installation guide, specifications, schema, data dictionary.

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

Load schema files in order: schema.sql, schema_extensions.sql, nexrad_satellite_schema.sql, insurance_schema.sql.

```bash
psql -U postgres -d db_6 -f schema.sql
```
```bash
psql -U postgres -d db_6 -f schema_extensions.sql
```
```bash
psql -U postgres -d db_6 -f nexrad_satellite_schema.sql
```
```bash
psql -U postgres -d db_6 -f insurance_schema.sql
```

---

### Step 4: Load Data (Optional)

Load sample data from data.sql if available.

```bash
psql -U postgres -d db_6 -f data.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

Standard PostgreSQL. No extensions required unless noted.

---

## Schema Overview

**Total tables:** 34

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
- `aws_data_source_log` — (see data dictionary)
- `nws_api_observation_log` — (see data dictionary)
- `geoplatform_dataset_log` — (see data dictionary)
- `weather_alerts` — (see data dictionary)
- `model_forecast_comparison` — (see data dictionary)
- `data_source_statistics` — (see data dictionary)
- `insurance_policy_areas` — (see data dictionary)
- `insurance_risk_factors` — (see data dictionary)
- `insurance_rate_tables` — (see data dictionary)
- `insurance_claims_history` — (see data dictionary)
- `forecast_rate_mapping` — (see data dictionary)
- `rate_table_comparison` — (see data dictionary)
- `nexrad_radar_sites` — (see data dictionary)
- `nexrad_level2_data` — (see data dictionary)
- `nexrad_reflectivity_grid` — (see data dictionary)
- `nexrad_velocity_grid` — (see data dictionary)
- `nexrad_storm_cells` — (see data dictionary)
- `satellite_imagery_sources` — (see data dictionary)
- `satellite_imagery_products` — (see data dictionary)
- `satellite_imagery_grid` — (see data dictionary)
- `nexrad_transformation_log` — (see data dictionary)
- `satellite_transformation_log` — (see data dictionary)
- `us_wide_composite_products` — (see data dictionary)

---

## Data Dictionary

### `grib2_forecasts`

- `forecast_id` VARCHAR(255) PRIMARY KEY
- `parameter_name` VARCHAR(100) NOT NULL
- `forecast_time` TIMESTAMP NOT NULL
- `grid_cell_latitude` NUMERIC(10, 7) NOT NULL
- `grid_cell_longitude` NUMERIC(10, 7) NOT NULL
- `grid_cell_geom` GEOGRAPHY  — Point geometry for grid cell center (PostgreSQL)
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
- `boundary_geom` GEOGRAPHY  — Polygon geometry
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
- `station_geom` GEOGRAPHY  — Point geometry
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
- `station_geom` GEOGRAPHY 
- `elevation_meters` NUMERIC(8, 2) 
- `state_code` VARCHAR(2) 
- `county_name` VARCHAR(100) 
- `cwa_code` VARCHAR(10) 
- `station_type` VARCHAR(50) 
- `active_status` BOOLEAN 
- `first_observation_date` DATE 
- `last_observation_date` DATE 
- `update_frequency_minutes` INTEGER 

### `aws_data_source_log`

- `source_id` VARCHAR(255) PRIMARY KEY
- `source_name` VARCHAR(500) NOT NULL
- `source_type` VARCHAR(100) NOT NULL — 'noaa_gfs', 'noaa_hrrr', 'noaa_nexrad', etc.
- `bucket_name` VARCHAR(255) NOT NULL
- `file_path` VARCHAR(1000) NOT NULL
- `format` VARCHAR(50)  — 'grib2', 'netcdf', 'binary', etc.
- `ingestion_timestamp` TIMESTAMP 
- `status` VARCHAR(50)  — 'Success', 'Failed', 'Pending'
- `metadata` JSONB  — PostgreSQL JSONB (repo is PostgreSQL-only)
- `file_size_bytes` BIGINT 
- `forecast_date` DATE 
- `forecast_cycle` VARCHAR(2)  — '00', '06', '12', '18'
- `forecast_hour` INTEGER 

### `nws_api_observation_log`

- `log_id` VARCHAR(255) PRIMARY KEY
- `station_id` VARCHAR(50) NOT NULL
- `observation_time` TIMESTAMP NOT NULL
- `api_endpoint` VARCHAR(500) 
- `response_status` INTEGER 
- `data_freshness_minutes` INTEGER 
- `ingestion_timestamp` TIMESTAMP 
- `status` VARCHAR(50) 
- `error_message` VARCHAR(2000) 

### `geoplatform_dataset_log`

- `dataset_id` VARCHAR(255) PRIMARY KEY
- `title` VARCHAR(500) 
- `description` VARCHAR(2000) 
- `url` VARCHAR(1000) 
- `search_term` VARCHAR(100) 
- `ingestion_timestamp` TIMESTAMP 
- `status` VARCHAR(50)  — 'Discovered', 'Ingested', 'Failed'
- `dataset_type` VARCHAR(100)  — 'boundary', 'elevation', 'imagery', etc.
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `ALTER` TABLE 
- `ALTER` TABLE  — 'GFS', 'HRRR', 'RAP', etc.
- `ALTER` TABLE 
- `ALTER` TABLE 
- `ALTER` TABLE  — For ensemble forecasts
- `ALTER` TABLE 
- `ALTER` TABLE 

### `weather_alerts`

- `alert_id` VARCHAR(255) PRIMARY KEY
- `event_type` VARCHAR(100) NOT NULL — 'Tornado Warning', 'Flood Warning', etc.
- `severity` VARCHAR(50)  — 'Extreme', 'Severe', 'Moderate', 'Minor', 'Unknown'
- `urgency` VARCHAR(50)  — 'Immediate', 'Expected', 'Future', 'Past', 'Unknown'
- `certainty` VARCHAR(50)  — 'Observed', 'Likely', 'Possible', 'Unlikely', 'Unknown'
- `headline` VARCHAR(500) 
- `description` TEXT 
- `instruction` TEXT 
- `effective_time` TIMESTAMP 
- `expires_time` TIMESTAMP 
- `onset_time` TIMESTAMP 
- `ends_time` TIMESTAMP 
- `area_description` VARCHAR(1000) 
- `geocode_type` VARCHAR(50)  — 'FIPS', 'UGC', etc.
- `geocode_value` VARCHAR(100) 
- `state_code` VARCHAR(2) 
- `county_code` VARCHAR(5) 
- `cwa_code` VARCHAR(10) 
- `ingestion_timestamp` TIMESTAMP 
- `alert_geometry` GEOGRAPHY  — Polygon geometry for alert area

### `model_forecast_comparison`

- `comparison_id` VARCHAR(255) PRIMARY KEY
- `forecast_time` TIMESTAMP NOT NULL
- `parameter_name` VARCHAR(100) NOT NULL
- `grid_cell_latitude` NUMERIC(10, 7) NOT NULL
- `grid_cell_longitude` NUMERIC(10, 7) NOT NULL
- `gfs_value` NUMERIC(10, 2) 
- `hrrr_value` NUMERIC(10, 2) 
- `rap_value` NUMERIC(10, 2) 
- `gefs_mean_value` NUMERIC(10, 2) 
- `gefs_stddev_value` NUMERIC(10, 2) 
- `observation_value` NUMERIC(10, 2) 
- `observation_time` TIMESTAMP 
- `gfs_error` NUMERIC(10, 2) 
- `hrrr_error` NUMERIC(10, 2) 
- `rap_error` NUMERIC(10, 2) 
- `best_model` VARCHAR(50)  — Model with smallest error
- `comparison_timestamp` TIMESTAMP 

### `data_source_statistics`

- `stat_id` VARCHAR(255) PRIMARY KEY
- `source_type` VARCHAR(100) NOT NULL — 'AWS_GFS', 'NWS_API', 'GEOPLATFORM'
- `source_name` VARCHAR(500) 
- `stat_date` DATE NOT NULL
- `files_ingested` INTEGER 
- `records_processed` INTEGER 
- `data_volume_mb` NUMERIC(15, 2) 
- `ingestion_duration_seconds` INTEGER 
- `success_rate` NUMERIC(5, 2) 
- `avg_latency_seconds` NUMERIC(10, 2) 
- `error_count` INTEGER 
- `calculation_timestamp` TIMESTAMP 

### `insurance_policy_areas`

- `policy_area_id` VARCHAR(255) PRIMARY KEY
- `boundary_id` VARCHAR(255) NOT NULL — References shapefile_boundaries
- `policy_type` VARCHAR(50) NOT NULL — 'Property', 'Crop', 'Auto', 'Marine', 'General Liability'
- `coverage_type` VARCHAR(100)  — 'Homeowners', 'Commercial Property', 'Crop Insurance', etc.
- `policy_area_name` VARCHAR(255) 
- `state_code` VARCHAR(2) 
- `county_code` VARCHAR(5) 
- `cwa_code` VARCHAR(10) 
- `risk_zone` VARCHAR(50)  — 'Low', 'Moderate', 'High', 'Very High'
- `base_rate_factor` NUMERIC(5, 3)  — Multiplier for base rates
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `is_active` BOOLEAN 
- `created_timestamp` TIMESTAMP 
- `updated_timestamp` TIMESTAMP 

### `insurance_risk_factors`

- `risk_factor_id` VARCHAR(255) PRIMARY KEY
- `policy_area_id` VARCHAR(255) NOT NULL — References insurance_policy_areas
- `forecast_period_start` DATE NOT NULL — Start of forecast period (Dec 3, 2025)
- `forecast_period_end` DATE NOT NULL — End of forecast period (Dec 17, 2025)
- `forecast_day` INTEGER NOT NULL — Days ahead: 7, 8, 9, ..., 14
- `forecast_date` DATE NOT NULL — Date when forecast was made
- `parameter_name` VARCHAR(100) NOT NULL — 'Temperature', 'Precipitation', 'WindSpeed', etc.
- `extreme_event_probability` NUMERIC(5, 4)  — Probability of extreme event (0-1)
- `temperature_extreme_risk` NUMERIC(10, 2)  — Temperature extreme risk score
- `cumulative_precipitation_risk` NUMERIC(10, 2)  — Total precipitation risk score
- `wind_damage_risk` NUMERIC(10, 2)  — Wind damage risk score
- `freeze_risk` NUMERIC(10, 2)  — Freeze/frost risk score
- `flood_risk` NUMERIC(10, 2)  — Flood risk score
- `min_forecast_value` NUMERIC(10, 2) 
- `max_forecast_value` NUMERIC(10, 2) 
- `avg_forecast_value` NUMERIC(10, 2) 
- `median_forecast_value` NUMERIC(10, 2) 
- `stddev_forecast_value` NUMERIC(10, 2) 
- `percentile_90_value` NUMERIC(10, 2) 
- `percentile_95_value` NUMERIC(10, 2) 
- `percentile_99_value` NUMERIC(10, 2) 
- `overall_risk_score` NUMERIC(5, 2) 
- `risk_category` VARCHAR(50)  — 'Low', 'Moderate', 'High', 'Very High', 'Extreme'
- `calculation_timestamp` TIMESTAMP 
- `forecast_model` VARCHAR(100)  — 'GFS', 'HRRR', 'Ensemble', etc.
- `data_quality_score` NUMERIC(5, 2) 

### `insurance_rate_tables`

- `rate_table_id` VARCHAR(255) PRIMARY KEY
- `policy_area_id` VARCHAR(255) NOT NULL — References insurance_policy_areas
- `policy_type` VARCHAR(50) NOT NULL
- `coverage_type` VARCHAR(100) 
- `forecast_period_start` DATE NOT NULL — Dec 3, 2025
- `forecast_period_end` DATE NOT NULL — Dec 17, 2025
- `forecast_day` INTEGER NOT NULL — 7-14 days ahead
- `forecast_date` DATE NOT NULL — Date when forecast was made
- `base_rate` NUMERIC(10, 2) 
- `base_rate_currency` VARCHAR(3) 
- `risk_adjusted_rate` NUMERIC(10, 2) 
- `risk_multiplier` NUMERIC(5, 3)  — Multiplier applied to base rate
- `overall_risk_score` NUMERIC(5, 2)  — Overall risk score (0-100)
- `base_component` NUMERIC(10, 2) 
- `precipitation_risk_component` NUMERIC(10, 2) 
- `temperature_risk_component` NUMERIC(10, 2) 
- `wind_risk_component` NUMERIC(10, 2) 
- `freeze_risk_component` NUMERIC(10, 2) 
- `flood_risk_component` NUMERIC(10, 2) 
- `extreme_event_component` NUMERIC(10, 2) 
- `rate_tier` VARCHAR(50)  — 'Standard', 'Preferred', 'Substandard', 'High Risk'
- `rate_category` VARCHAR(50)  — 'Low', 'Moderate', 'High', 'Very High'
- `calculation_method` VARCHAR(100)  — 'Forecast-Based', 'Historical', 'Hybrid'
- `confidence_level` NUMERIC(5, 2)  — Confidence in forecast (0-100)
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `created_timestamp` TIMESTAMP 
- `updated_timestamp` TIMESTAMP 

### `insurance_claims_history`

- `claim_id` VARCHAR(255) PRIMARY KEY
- `policy_area_id` VARCHAR(255)  — References insurance_policy_areas
- `claim_date` DATE NOT NULL
- `loss_date` DATE NOT NULL — Date when loss occurred
- `policy_type` VARCHAR(50) 
- `coverage_type` VARCHAR(100) 
- `claim_type` VARCHAR(100)  — 'Weather', 'Fire', 'Flood', 'Wind', 'Freeze', etc.
- `loss_amount` NUMERIC(12, 2) 
- `claim_status` VARCHAR(50)  — 'Open', 'Closed', 'Denied', 'Pending'
- `weather_event_type` VARCHAR(100)  — 'Hurricane', 'Tornado', 'Flood', 'Freeze', etc.
- `weather_event_date` DATE 
- `temperature_at_loss` NUMERIC(6, 2) 
- `precipitation_at_loss` NUMERIC(8, 2) 
- `wind_speed_at_loss` NUMERIC(6, 2) 
- `forecast_available` BOOLEAN 
- `forecast_day` INTEGER  — Days ahead forecast was made
- `forecast_error` NUMERIC(10, 2)  — Forecast vs actual error
- `created_timestamp` TIMESTAMP 

### `forecast_rate_mapping`

- `mapping_id` VARCHAR(255) PRIMARY KEY
- `forecast_id` VARCHAR(255) NOT NULL — References grib2_forecasts
- `rate_table_id` VARCHAR(255)  — References insurance_rate_tables
- `risk_factor_id` VARCHAR(255)  — References insurance_risk_factors
- `policy_area_id` VARCHAR(255) NOT NULL — References insurance_policy_areas
- `forecast_date` DATE NOT NULL
- `forecast_day` INTEGER NOT NULL — 7-14 days ahead
- `forecast_time` TIMESTAMP NOT NULL
- `parameter_name` VARCHAR(100) NOT NULL
- `parameter_value` NUMERIC(10, 2) 
- `risk_contribution` NUMERIC(10, 4)  — Contribution to overall risk score
- `rate_impact` NUMERIC(10, 4)  — Impact on rate calculation
- `mapping_timestamp` TIMESTAMP 

### `rate_table_comparison`

- `comparison_id` VARCHAR(255) PRIMARY KEY
- `policy_area_id` VARCHAR(255) NOT NULL
- `policy_type` VARCHAR(50) NOT NULL
- `coverage_type` VARCHAR(100)  — 'Homeowners', 'Commercial Property', etc.
- `forecast_period_start` DATE NOT NULL — Dec 3, 2025
- `forecast_period_end` DATE NOT NULL — Dec 17, 2025
- `forecast_date` DATE NOT NULL — Date when forecast was made
- `rate_day_7` NUMERIC(10, 2) 
- `rate_day_8` NUMERIC(10, 2) 
- `rate_day_9` NUMERIC(10, 2) 
- `rate_day_10` NUMERIC(10, 2) 
- `rate_day_11` NUMERIC(10, 2) 
- `rate_day_12` NUMERIC(10, 2) 
- `rate_day_13` NUMERIC(10, 2) 
- `rate_day_14` NUMERIC(10, 2) 
- `min_rate` NUMERIC(10, 2) 
- `max_rate` NUMERIC(10, 2) 
- `avg_rate` NUMERIC(10, 2) 
- `median_rate` NUMERIC(10, 2) 
- `rate_volatility` NUMERIC(10, 4)  — Standard deviation of rates
- `rate_volatility_percent` NUMERIC(10, 4)  — Rate volatility as percentage
- `rate_trend` VARCHAR(50)  — 'Increasing', 'Decreasing', 'Stable'
- `recommended_rate` NUMERIC(10, 2) 
- `recommended_forecast_day` INTEGER  — Which forecast day to use
- `confidence_score` NUMERIC(5, 2) 
- `recommendation_status` VARCHAR(50)  — 'Recommended', 'Alternative', etc.
- `comparison_timestamp` TIMESTAMP 

### `nexrad_radar_sites`

- `site_id` VARCHAR(4) PRIMARY KEY — 4-letter site identifier (e.g., 'KTLX')
- `site_name` VARCHAR(255) NOT NULL
- `site_latitude` NUMERIC(10, 7) NOT NULL
- `site_longitude` NUMERIC(10, 7) NOT NULL
- `site_geom` GEOGRAPHY  — Point geometry
- `elevation_meters` NUMERIC(8, 2) 
- `state_code` VARCHAR(2) 
- `county_name` VARCHAR(100) 
- `cwa_code` VARCHAR(10)  — County Warning Area
- `radar_type` VARCHAR(50)  — Weather Surveillance Radar
- `operational_status` VARCHAR(50)  — 'Operational', 'Maintenance', 'Offline'
- `coverage_radius_km` NUMERIC(8, 2)  — Standard NEXRAD coverage radius
- `first_operational_date` DATE 
- `last_maintenance_date` DATE 
- `update_frequency_minutes` INTEGER  — Typical NEXRAD update frequency
- `created_timestamp` TIMESTAMP 
- `updated_timestamp` TIMESTAMP 

### `nexrad_level2_data`

- `radar_data_id` VARCHAR(255) PRIMARY KEY
- `site_id` VARCHAR(4) NOT NULL — References nexrad_radar_sites
- `scan_time` TIMESTAMP NOT NULL
- `volume_scan_number` INTEGER 
- `elevation_angle` NUMERIC(5, 2)  — Elevation angle in degrees
- `azimuth_angle` NUMERIC(6, 2)  — Azimuth angle in degrees
- `range_gate` INTEGER  — Range gate number
- `range_km` NUMERIC(8, 2)  — Distance from radar in kilometers
- `reflectivity_dbz` NUMERIC(6, 2)  — Reflectivity in dBZ
- `reflectivity_geom` GEOGRAPHY  — Point geometry for reflectivity location
- `radial_velocity_ms` NUMERIC(6, 2)  — Radial velocity in m/s
- `velocity_geom` GEOGRAPHY  — Point geometry for velocity location
- `spectrum_width_ms` NUMERIC(6, 2)  — Spectrum width in m/s
- `data_quality_flag` INTEGER  — Quality flags
- `source_file` VARCHAR(1000)  — Original NEXRAD file path
- `aws_bucket` VARCHAR(255)  — AWS S3 bucket
- `aws_key` VARCHAR(1000)  — AWS S3 key
- `file_format` VARCHAR(50)  — 'Level2', 'Level3'
- `compression_type` VARCHAR(50)  — 'bzip2', 'gzip', 'none'
- `decompression_status` VARCHAR(50)  — 'Success', 'Failed', 'Pending'
- `data_type` VARCHAR(50)  — 'Reflectivity', 'Velocity', 'SpectrumWidth', 'DifferentialReflectivity'
- `sweep_mode` VARCHAR(50)  — 'PPI' (Plan Position Indicator), 'RHI' (Range Height Indicator)
- `pulse_repetition_frequency` INTEGER  — PRF in Hz
- `nyquist_velocity_ms` NUMERIC(6, 2)  — Nyquist velocity in m/s
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `ingestion_timestamp` TIMESTAMP 
- `processing_duration_seconds` INTEGER 
- `records_processed` INTEGER 

### `nexrad_reflectivity_grid`

- `grid_id` VARCHAR(255) PRIMARY KEY
- `site_id` VARCHAR(4) NOT NULL — References nexrad_radar_sites
- `scan_time` TIMESTAMP NOT NULL
- `grid_latitude` NUMERIC(10, 7) NOT NULL
- `grid_longitude` NUMERIC(10, 7) NOT NULL
- `grid_geom` GEOGRAPHY  — Point geometry
- `grid_resolution_km` NUMERIC(6, 2)  — Grid resolution in km
- `max_reflectivity_dbz` NUMERIC(6, 2)  — Maximum reflectivity in grid cell
- `mean_reflectivity_dbz` NUMERIC(6, 2)  — Mean reflectivity in grid cell
- `min_reflectivity_dbz` NUMERIC(6, 2)  — Minimum reflectivity in grid cell
- `reflectivity_count` INTEGER  — Number of observations in grid cell
- `composite_reflectivity_dbz` NUMERIC(6, 2) 
- `height_of_max_reflectivity_m` NUMERIC(8, 2) 
- `precipitation_rate_mmh` NUMERIC(8, 2)  — Precipitation rate in mm/h
- `accumulated_precipitation_mm` NUMERIC(8, 2)  — Accumulated precipitation in mm
- `storm_cell_id` VARCHAR(255)  — Identifier for storm cell tracking
- `storm_severity` VARCHAR(50)  — 'Weak', 'Moderate', 'Strong', 'Severe', 'Extreme'
- `grid_generation_timestamp` TIMESTAMP 
- `grid_method` VARCHAR(100)  — 'NearestNeighbor', 'Bilinear', 'Cressman', etc.

### `nexrad_velocity_grid`

- `grid_id` VARCHAR(255) PRIMARY KEY
- `site_id` VARCHAR(4) NOT NULL — References nexrad_radar_sites
- `scan_time` TIMESTAMP NOT NULL
- `grid_latitude` NUMERIC(10, 7) NOT NULL
- `grid_longitude` NUMERIC(10, 7) NOT NULL
- `grid_geom` GEOGRAPHY  — Point geometry
- `grid_resolution_km` NUMERIC(6, 2) 
- `radial_velocity_ms` NUMERIC(6, 2)  — Radial velocity in m/s
- `velocity_azimuth` NUMERIC(6, 2)  — Azimuth angle in degrees
- `u_wind_component_ms` NUMERIC(6, 2)  — East-west wind component
- `v_wind_component_ms` NUMERIC(6, 2)  — North-south wind component
- `wind_speed_ms` NUMERIC(6, 2)  — Wind speed in m/s
- `wind_direction_deg` NUMERIC(6, 2)  — Wind direction in degrees
- `spectrum_width_ms` NUMERIC(6, 2) 
- `velocity_quality_flag` INTEGER 
- `grid_generation_timestamp` TIMESTAMP 

### `nexrad_storm_cells`

- `storm_cell_id` VARCHAR(255) PRIMARY KEY
- `site_id` VARCHAR(4) NOT NULL — References nexrad_radar_sites
- `first_detection_time` TIMESTAMP NOT NULL
- `last_detection_time` TIMESTAMP 
- `storm_center_latitude` NUMERIC(10, 7) 
- `storm_center_longitude` NUMERIC(10, 7) 
- `storm_center_geom` GEOGRAPHY  — Point geometry
- `storm_polygon_geom` GEOGRAPHY  — Polygon geometry for storm extent
- `max_reflectivity_dbz` NUMERIC(6, 2) 
- `max_velocity_ms` NUMERIC(6, 2) 
- `storm_area_km2` NUMERIC(10, 2) 
- `storm_diameter_km` NUMERIC(8, 2) 
- `storm_perimeter_km` NUMERIC(8, 2) 
- `storm_speed_ms` NUMERIC(6, 2)  — Storm movement speed
- `storm_direction_deg` NUMERIC(6, 2)  — Storm movement direction
- `storm_severity` VARCHAR(50)  — 'Weak', 'Moderate', 'Strong', 'Severe', 'Extreme'
- `storm_type` VARCHAR(50)  — 'Thunderstorm', 'Squall Line', 'Supercell', 'Mesocyclone', etc.
- `track_duration_minutes` INTEGER 
- `scan_count` INTEGER  — Number of scans where storm was detected
- `tracking_status` VARCHAR(50)  — 'Active', 'Dissipated', 'Merged'
- `tracking_timestamp` TIMESTAMP 

### `satellite_imagery_sources`

- `source_id` VARCHAR(255) PRIMARY KEY
- `satellite_name` VARCHAR(100) NOT NULL — 'GOES-16', 'GOES-17', 'GOES-18', etc.
- `satellite_type` VARCHAR(50)  — 'GOES', 'POES', 'MODIS', etc.
- `sensor_name` VARCHAR(100)  — 'ABI' (Advanced Baseline Imager), etc.
- `orbital_position` VARCHAR(50)  — 'GOES-East', 'GOES-West', etc.
- `coverage_area` VARCHAR(100)  — 'CONUS', 'Full Disk', 'Mesoscale', etc.
- `spatial_resolution_km` NUMERIC(8, 2)  — Spatial resolution in kilometers
- `scan_frequency_minutes` INTEGER  — Scan frequency in minutes
- `temporal_resolution_minutes` INTEGER 
- `operational_status` VARCHAR(50) 
- `first_operational_date` DATE 
- `last_update_date` DATE 
- `created_timestamp` TIMESTAMP 
- `updated_timestamp` TIMESTAMP 

### `satellite_imagery_products`

- `product_id` VARCHAR(255) PRIMARY KEY
- `source_id` VARCHAR(255) NOT NULL — References satellite_imagery_sources
- `product_name` VARCHAR(255) NOT NULL — 'ABI L2 Cloud Top Height', 'ABI L2 Cloud Top Temperature', etc.
- `product_type` VARCHAR(100)  — 'Cloud', 'Fire', 'Precipitation', 'Temperature', 'Moisture', etc.
- `band_number` INTEGER  — GOES ABI band number (1-16)
- `band_name` VARCHAR(100)  — 'Visible', 'Near-Infrared', 'Infrared', etc.
- `wavelength_um` NUMERIC(8, 4)  — Wavelength in micrometers
- `scan_start_time` TIMESTAMP NOT NULL
- `scan_end_time` TIMESTAMP 
- `scan_duration_seconds` INTEGER 
- `grid_latitude` NUMERIC(10, 7) NOT NULL
- `grid_longitude` NUMERIC(10, 7) NOT NULL
- `grid_geom` GEOGRAPHY  — Point geometry
- `grid_resolution_km` NUMERIC(8, 2)  — Grid resolution in kilometers
- `pixel_value` NUMERIC(10, 4)  — Raw pixel value
- `calibrated_value` NUMERIC(10, 4)  — Calibrated physical value
- `brightness_temperature_k` NUMERIC(8, 2)  — Brightness temperature in Kelvin (for IR bands)
- `reflectance_percent` NUMERIC(6, 2)  — Reflectance percentage (for visible bands)
- `cloud_top_height_m` NUMERIC(8, 2)  — Cloud top height in meters
- `cloud_top_temperature_k` NUMERIC(8, 2)  — Cloud top temperature in Kelvin
- `cloud_phase` VARCHAR(50)  — 'Liquid', 'Ice', 'Mixed', 'Unknown'
- `cloud_optical_depth` NUMERIC(8, 4)  — Cloud optical depth
- `fire_detection_confidence` NUMERIC(5, 2)  — Fire detection confidence (0-100)
- `fire_temperature_k` NUMERIC(8, 2)  — Fire temperature in Kelvin
- `fire_power_mw` NUMERIC(12, 2)  — Fire radiative power in megawatts
- `precipitation_rate_mmh` NUMERIC(8, 2)  — Precipitation rate in mm/h
- `source_file` VARCHAR(1000)  — Original satellite file path
- `aws_bucket` VARCHAR(255)  — AWS S3 bucket
- `aws_key` VARCHAR(1000)  — AWS S3 key
- `file_format` VARCHAR(50)  — 'NetCDF', 'HDF5', 'GeoTIFF', etc.
- `compression_type` VARCHAR(50)  — Compression type
- `decompression_status` VARCHAR(50) 
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `ingestion_timestamp` TIMESTAMP 
- `processing_duration_seconds` INTEGER 
- `records_processed` INTEGER 

### `satellite_imagery_grid`

- `grid_id` VARCHAR(255) PRIMARY KEY
- `source_id` VARCHAR(255) NOT NULL — References satellite_imagery_sources
- `product_type` VARCHAR(100) NOT NULL
- `scan_time` TIMESTAMP NOT NULL
- `grid_latitude` NUMERIC(10, 7) NOT NULL
- `grid_longitude` NUMERIC(10, 7) NOT NULL
- `grid_geom` GEOGRAPHY  — Point geometry
- `grid_resolution_km` NUMERIC(8, 2)  — Grid resolution
- `min_value` NUMERIC(10, 4) 
- `max_value` NUMERIC(10, 4) 
- `mean_value` NUMERIC(10, 4) 
- `median_value` NUMERIC(10, 4) 
- `stddev_value` NUMERIC(10, 4) 
- `pixel_count` INTEGER 
- `cloud_fraction` NUMERIC(5, 2)  — Cloud fraction (0-100%)
- `cloud_top_height_m` NUMERIC(8, 2) 
- `cloud_top_temperature_k` NUMERIC(8, 2) 
- `fire_count` INTEGER 
- `total_fire_power_mw` NUMERIC(12, 2) 
- `precipitation_rate_mmh` NUMERIC(8, 2) 
- `aggregation_timestamp` TIMESTAMP 
- `aggregation_method` VARCHAR(100)  — 'Mean', 'Max', 'Min', 'Median', etc.

### `nexrad_transformation_log`

- `transformation_id` VARCHAR(255) PRIMARY KEY
- `site_id` VARCHAR(4) NOT NULL
- `source_file` VARCHAR(1000) NOT NULL
- `transformation_type` VARCHAR(100) NOT NULL — 'Decompression', 'Gridding', 'StormTracking', 'Composite'
- `transformation_start_time` TIMESTAMP NOT NULL
- `transformation_end_time` TIMESTAMP 
- `transformation_duration_seconds` INTEGER 
- `input_format` VARCHAR(50) 
- `input_size_bytes` BIGINT 
- `input_records` INTEGER 
- `output_format` VARCHAR(50) 
- `output_size_bytes` BIGINT 
- `output_records` INTEGER 
- `transformation_status` VARCHAR(50)  — 'Success', 'Failed', 'Partial'
- `error_message` VARCHAR(2000) 
- `processing_method` VARCHAR(100)  — 'PyART', 'wradlib', 'Custom', etc.
- `processing_parameters` VARCHAR(2000)  — JSON parameters
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `created_timestamp` TIMESTAMP 

### `satellite_transformation_log`

- `transformation_id` VARCHAR(255) PRIMARY KEY
- `source_id` VARCHAR(255) NOT NULL
- `source_file` VARCHAR(1000) NOT NULL
- `transformation_type` VARCHAR(100) NOT NULL — 'Decompression', 'Reprojection', 'Gridding', 'ProductGeneration'
- `transformation_start_time` TIMESTAMP NOT NULL
- `transformation_end_time` TIMESTAMP 
- `transformation_duration_seconds` INTEGER 
- `input_format` VARCHAR(50) 
- `input_size_bytes` BIGINT 
- `input_bands` INTEGER 
- `input_dimensions` VARCHAR(100)  — 'width x height'
- `output_format` VARCHAR(50) 
- `output_size_bytes` BIGINT 
- `output_records` INTEGER 
- `transformation_status` VARCHAR(50) 
- `error_message` VARCHAR(2000) 
- `processing_method` VARCHAR(100)  — 'xarray', 'rasterio', 'GDAL', 'Custom', etc.
- `processing_parameters` VARCHAR(2000)  — JSON parameters
- `crs_transformation` VARCHAR(100)  — CRS transformation applied
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `created_timestamp` TIMESTAMP 

### `us_wide_composite_products`

- `composite_id` VARCHAR(255) PRIMARY KEY
- `product_type` VARCHAR(100) NOT NULL — 'Precipitation', 'Cloud', 'Storm', 'Fire', 'Temperature'
- `composite_time` TIMESTAMP NOT NULL
- `grid_latitude` NUMERIC(10, 7) NOT NULL
- `grid_longitude` NUMERIC(10, 7) NOT NULL
- `grid_geom` GEOGRAPHY  — Point geometry
- `grid_resolution_km` NUMERIC(8, 2) 
- `nexrad_reflectivity_dbz` NUMERIC(6, 2) 
- `nexrad_velocity_ms` NUMERIC(6, 2) 
- `nexrad_precipitation_rate_mmh` NUMERIC(8, 2) 
- `nexrad_contribution_weight` NUMERIC(5, 3)  — Weight of NEXRAD data in composite
- `satellite_brightness_temperature_k` NUMERIC(8, 2) 
- `satellite_reflectance_percent` NUMERIC(6, 2) 
- `satellite_cloud_top_height_m` NUMERIC(8, 2) 
- `satellite_precipitation_rate_mmh` NUMERIC(8, 2) 
- `satellite_contribution_weight` NUMERIC(5, 3)  — Weight of satellite data in composite
- `composite_precipitation_rate_mmh` NUMERIC(8, 2) 
- `composite_cloud_fraction` NUMERIC(5, 2) 
- `composite_storm_severity` VARCHAR(50) 
- `data_quality_score` NUMERIC(5, 2)  — Overall data quality (0-100)
- `coverage_percentage` NUMERIC(5, 2)  — Percentage of expected data coverage
- `nexrad_sites_count` INTEGER  — Number of NEXRAD sites contributing
- `satellite_sources_count` INTEGER  — Number of satellite sources contributing
- `composite_generation_timestamp` TIMESTAMP 
- `composite_method` VARCHAR(100)  — 'WeightedAverage', 'Maximum', 'Minimum', 'Median', etc.

---

*Generated by documentation workflow. MDX-compatible markdown.*
