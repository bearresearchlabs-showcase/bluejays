---
title: db-6 — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-6
---

# db-6 — Documentation

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

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_6 -f schema.sql
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

- `aws_data_source_log` — (see data dictionary)
- `crs_transformation_parameters` — 'Point-in-Polygon', 'Raster-to-Vector', 'Clip'
- `data_quality_metrics` — 'GDAL', 'PROJ', 'Custom'
- `data_source_statistics` — (see data dictionary)
- `forecast_rate_mapping` — (see data dictionary)
- `geoplatform_dataset_log` — (see data dictionary)
- `grib2_forecasts` — Weather Data Pipeline Database Schema
- `grib2_transformation_log` — GRIB2 Transformation Log Table
- `insurance_claims_history` — (see data dictionary)
- `insurance_policy_areas` — (see data dictionary)
- `insurance_rate_tables` — (see data dictionary)
- `insurance_risk_factors` — (see data dictionary)
- `model_forecast_comparison` — (see data dictionary)
- `nexrad_level2_data` — (see data dictionary)
- `nexrad_radar_sites` — (see data dictionary)
- `nexrad_reflectivity_grid` — (see data dictionary)
- `nexrad_storm_cells` — (see data dictionary)
- `nexrad_transformation_log` — (see data dictionary)
- `nexrad_velocity_grid` — (see data dictionary)
- `nws_api_observation_log` — (see data dictionary)
- `rate_table_comparison` — (see data dictionary)
- `satellite_imagery_grid` — (see data dictionary)
- `satellite_imagery_products` — (see data dictionary)
- `satellite_imagery_sources` — (see data dictionary)
- `satellite_transformation_log` — (see data dictionary)
- `shapefile_boundaries` — Shapefile Boundaries Table
- `shapefile_integration_log` — Shapefile Integration Log Table
- `load_status` — Snowflake Load Status Table
- `spatial_join_results` — Spatial Join Results Table
- `us_wide_composite_products` — (see data dictionary)
- `weather_alerts` — (see data dictionary)
- `weather_forecast_aggregations` — 'Success', 'Failed', 'Partial'
- `weather_observations` — Real-Time Weather Observations Table
- `weather_stations` — Weather Station Metadata Table

---

## Data Dictionary

### `aws_data_source_log`

- `source_name`  
- `source_type`  
- `bucket_name`  
- `file_path`  
- `format`  
- `ingestion_timestamp`  
- `status`  
- `metadata`  
- `file_size_bytes`  
- `forecast_date`  
- `forecast_cycle`  
- `forecast_hour`  

### `crs_transformation_parameters`

- `source_crs`  
- `target_crs`  
- `source_crs_name`  
- `target_crs_name`  
- `transformation_method`  
- `central_meridian`  
- `false_easting`  
- `false_northing`  
- `scale_factor`  
- `latitude_of_origin`  
- `units`  
- `accuracy_meters`  
- `usage_count`  

### `data_quality_metrics`

- `metric_date`  
- `data_source`  
- `files_processed`  
- `files_successful`  
- `files_failed`  
- `success_rate`  
- `total_records`  
- `records_with_errors`  
- `error_rate`  
- `spatial_coverage_km2`  
- `temporal_coverage_hours`  
- `data_freshness_minutes`  
- `calculation_timestamp`  

### `data_source_statistics`

- `source_type`  
- `source_name`  
- `stat_date`  
- `files_ingested`  
- `records_processed`  
- `data_volume_mb`  
- `ingestion_duration_seconds`  
- `success_rate`  
- `avg_latency_seconds`  
- `error_count`  
- `calculation_timestamp`  

### `forecast_rate_mapping`

- `forecast_id`  
- `rate_table_id`  
- `risk_factor_id`  
- `policy_area_id`  
- `forecast_date`  
- `forecast_day`  
- `forecast_time`  
- `parameter_name`  
- `parameter_value`  
- `risk_contribution`  
- `rate_impact`  
- `mapping_timestamp`  

### `geoplatform_dataset_log`

- `title`  
- `description`  
- `url`  
- `search_term`  
- `ingestion_timestamp`  
- `status`  
- `dataset_type`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  

### `grib2_forecasts`

- `parameter_name`  
- `forecast_time`  
- `grid_cell_latitude`  
- `grid_cell_longitude`  
- `grid_cell_geom`  
- `parameter_value`  
- `source_file`  
- `source_crs`  
- `target_crs`  
- `grid_resolution_x`  
- `grid_resolution_y`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  
- `load_timestamp`  
- `transformation_status`  

### `grib2_transformation_log`

- `file_name`  
- `source_path`  
- `parameter_name`  
- `forecast_time`  
- `source_crs`  
- `target_crs`  
- `gdal_command`  
- `output_file`  
- `grid_resolution_x`  
- `grid_resolution_y`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  
- `transformation_status`  
- `target_table`  
- `load_timestamp`  
- `processing_duration_seconds`  
- `records_processed`  
- `error_message`  

### `insurance_claims_history`

- `policy_area_id`  
- `claim_date`  
- `loss_date`  
- `policy_type`  
- `coverage_type`  
- `claim_type`  
- `loss_amount`  
- `claim_status`  
- `weather_event_type`  
- `weather_event_date`  
- `temperature_at_loss`  
- `precipitation_at_loss`  
- `wind_speed_at_loss`  
- `forecast_available`  
- `forecast_day`  
- `forecast_error`  
- `created_timestamp`  

### `insurance_policy_areas`

- `boundary_id`  
- `policy_type`  
- `coverage_type`  
- `policy_area_name`  
- `state_code`  
- `county_code`  
- `cwa_code`  
- `risk_zone`  
- `base_rate_factor`  
- `effective_date`  
- `expiration_date`  
- `is_active`  
- `created_timestamp`  
- `updated_timestamp`  

### `insurance_rate_tables`

- `policy_area_id`  
- `policy_type`  
- `coverage_type`  
- `forecast_period_start`  
- `forecast_period_end`  
- `forecast_day`  
- `forecast_date`  
- `base_rate`  
- `base_rate_currency`  
- `risk_adjusted_rate`  
- `risk_multiplier`  
- `base_component`  
- `precipitation_risk_component`  
- `temperature_risk_component`  
- `wind_risk_component`  
- `freeze_risk_component`  
- `flood_risk_component`  
- `extreme_event_component`  
- `rate_tier`  
- `rate_category`  
- `calculation_method`  
- `confidence_level`  
- `effective_date`  
- `expiration_date`  
- `created_timestamp`  
- `updated_timestamp`  

### `insurance_risk_factors`

- `policy_area_id`  
- `forecast_period_start`  
- `forecast_period_end`  
- `forecast_day`  
- `forecast_date`  
- `parameter_name`  
- `extreme_event_probability`  
- `cumulative_precipitation_risk`  
- `wind_damage_risk`  
- `freeze_risk`  
- `flood_risk`  
- `min_forecast_value`  
- `max_forecast_value`  
- `avg_forecast_value`  
- `median_forecast_value`  
- `stddev_forecast_value`  
- `percentile_90_value`  
- `percentile_95_value`  
- `percentile_99_value`  
- `overall_risk_score`  
- `risk_category`  
- `calculation_timestamp`  
- `forecast_model`  
- `data_quality_score`  

### `model_forecast_comparison`

- `forecast_time`  
- `parameter_name`  
- `grid_cell_latitude`  
- `grid_cell_longitude`  
- `gfs_value`  
- `hrrr_value`  
- `rap_value`  
- `gefs_mean_value`  
- `gefs_stddev_value`  
- `observation_value`  
- `observation_time`  
- `gfs_error`  
- `hrrr_error`  
- `rap_error`  
- `best_model`  
- `comparison_timestamp`  

### `nexrad_level2_data`

- `site_id`  
- `scan_time`  
- `volume_scan_number`  
- `elevation_angle`  
- `azimuth_angle`  
- `range_gate`  
- `range_km`  
- `reflectivity_dbz`  
- `reflectivity_geom`  
- `radial_velocity_ms`  
- `velocity_geom`  
- `spectrum_width_ms`  
- `data_quality_flag`  
- `source_file`  
- `aws_bucket`  
- `aws_key`  
- `file_format`  
- `compression_type`  
- `decompression_status`  
- `data_type`  
- `sweep_mode`  
- `pulse_repetition_frequency`  
- `nyquist_velocity_ms`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  
- `ingestion_timestamp`  
- `processing_duration_seconds`  
- `records_processed`  

### `nexrad_radar_sites`

- `site_name`  
- `site_latitude`  
- `site_longitude`  
- `site_geom`  
- `elevation_meters`  
- `state_code`  
- `county_name`  
- `cwa_code`  
- `radar_type`  
- `operational_status`  
- `coverage_radius_km`  
- `first_operational_date`  
- `last_maintenance_date`  
- `update_frequency_minutes`  
- `created_timestamp`  
- `updated_timestamp`  

### `nexrad_reflectivity_grid`

- `site_id`  
- `scan_time`  
- `grid_latitude`  
- `grid_longitude`  
- `grid_geom`  
- `grid_resolution_km`  
- `max_reflectivity_dbz`  
- `mean_reflectivity_dbz`  
- `min_reflectivity_dbz`  
- `reflectivity_count`  
- `composite_reflectivity_dbz`  
- `height_of_max_reflectivity_m`  
- `precipitation_rate_mmh`  
- `accumulated_precipitation_mm`  
- `storm_cell_id`  
- `storm_severity`  
- `grid_generation_timestamp`  
- `grid_method`  

### `nexrad_storm_cells`

- `site_id`  
- `first_detection_time`  
- `last_detection_time`  
- `storm_center_latitude`  
- `storm_center_longitude`  
- `storm_center_geom`  
- `storm_polygon_geom`  
- `max_reflectivity_dbz`  
- `max_velocity_ms`  
- `storm_area_km2`  
- `storm_diameter_km`  
- `storm_perimeter_km`  
- `storm_speed_ms`  
- `storm_direction_deg`  
- `storm_severity`  
- `storm_type`  
- `track_duration_minutes`  
- `scan_count`  
- `tracking_status`  
- `tracking_timestamp`  

### `nexrad_transformation_log`

- `site_id`  
- `source_file`  
- `transformation_type`  
- `transformation_start_time`  
- `transformation_end_time`  
- `transformation_duration_seconds`  
- `input_format`  
- `input_size_bytes`  
- `input_records`  
- `output_format`  
- `output_size_bytes`  
- `output_records`  
- `transformation_status`  
- `error_message`  
- `processing_method`  
- `processing_parameters`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  
- `created_timestamp`  

### `nexrad_velocity_grid`

- `site_id`  
- `scan_time`  
- `grid_latitude`  
- `grid_longitude`  
- `grid_geom`  
- `grid_resolution_km`  
- `radial_velocity_ms`  
- `velocity_azimuth`  
- `u_wind_component_ms`  
- `v_wind_component_ms`  
- `wind_speed_ms`  
- `wind_direction_deg`  
- `spectrum_width_ms`  
- `velocity_quality_flag`  
- `grid_generation_timestamp`  

### `nws_api_observation_log`

- `station_id`  
- `observation_time`  
- `api_endpoint`  
- `response_status`  
- `data_freshness_minutes`  
- `ingestion_timestamp`  
- `status`  
- `error_message`  

### `rate_table_comparison`

- `policy_area_id`  
- `policy_type`  
- `forecast_period_start`  
- `forecast_period_end`  
- `forecast_date`  
- `rate_day_7`  
- `rate_day_8`  
- `rate_day_9`  
- `rate_day_10`  
- `rate_day_11`  
- `rate_day_12`  
- `rate_day_13`  
- `rate_day_14`  
- `min_rate`  
- `max_rate`  
- `avg_rate`  
- `median_rate`  
- `rate_volatility`  
- `rate_trend`  
- `recommended_rate`  
- `recommended_forecast_day`  
- `confidence_score`  
- `comparison_timestamp`  

### `satellite_imagery_grid`

- `source_id`  
- `product_type`  
- `scan_time`  
- `grid_latitude`  
- `grid_longitude`  
- `grid_geom`  
- `grid_resolution_km`  
- `min_value`  
- `max_value`  
- `mean_value`  
- `median_value`  
- `stddev_value`  
- `pixel_count`  
- `cloud_fraction`  
- `cloud_top_height_m`  
- `cloud_top_temperature_k`  
- `fire_count`  
- `total_fire_power_mw`  
- `precipitation_rate_mmh`  
- `aggregation_timestamp`  
- `aggregation_method`  

### `satellite_imagery_products`

- `source_id`  
- `product_name`  
- `product_type`  
- `band_number`  
- `band_name`  
- `wavelength_um`  
- `scan_start_time`  
- `scan_end_time`  
- `scan_duration_seconds`  
- `grid_latitude`  
- `grid_longitude`  
- `grid_geom`  
- `grid_resolution_km`  
- `pixel_value`  
- `calibrated_value`  
- `brightness_temperature_k`  
- `reflectance_percent`  
- `cloud_top_height_m`  
- `cloud_top_temperature_k`  
- `cloud_phase`  
- `cloud_optical_depth`  
- `fire_detection_confidence`  
- `fire_temperature_k`  
- `fire_power_mw`  
- `precipitation_rate_mmh`  
- `source_file`  
- `aws_bucket`  
- `aws_key`  
- `file_format`  
- `compression_type`  
- `decompression_status`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  
- `ingestion_timestamp`  
- `processing_duration_seconds`  
- `records_processed`  

### `satellite_imagery_sources`

- `satellite_name`  
- `satellite_type`  
- `sensor_name`  
- `orbital_position`  
- `coverage_area`  
- `spatial_resolution_km`  
- `scan_frequency_minutes`  
- `temporal_resolution_minutes`  
- `operational_status`  
- `first_operational_date`  
- `last_update_date`  
- `created_timestamp`  
- `updated_timestamp`  

### `satellite_transformation_log`

- `source_id`  
- `source_file`  
- `transformation_type`  
- `transformation_start_time`  
- `transformation_end_time`  
- `transformation_duration_seconds`  
- `input_format`  
- `input_size_bytes`  
- `input_bands`  
- `input_dimensions`  
- `output_format`  
- `output_size_bytes`  
- `output_records`  
- `transformation_status`  
- `error_message`  
- `processing_method`  
- `processing_parameters`  
- `crs_transformation`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  
- `created_timestamp`  

### `shapefile_boundaries`

- `feature_type`  
- `feature_name`  
- `feature_identifier`  
- `boundary_geom`  
- `source_shapefile`  
- `source_crs`  
- `target_crs`  
- `feature_count`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  
- `load_timestamp`  
- `transformation_status`  
- `state_code`  
- `office_code`  

### `shapefile_integration_log`

- `shapefile_name`  
- `source_path`  
- `feature_type`  
- `feature_count`  
- `source_crs`  
- `target_crs`  
- `ogr2ogr_command`  
- `transformed_path`  
- `spatial_extent_west`  
- `spatial_extent_south`  
- `spatial_extent_east`  
- `spatial_extent_north`  
- `transformation_status`  
- `target_table`  
- `load_timestamp`  
- `processing_duration_seconds`  
- `error_message`  

### `load_status`

- `source_file`  
- `target_table`  
- `load_start_time`  
- `load_end_time`  
- `load_duration_seconds`  
- `records_loaded`  
- `file_size_mb`  
- `load_rate_mb_per_sec`  
- `load_status`  
- `error_message`  
- `warehouse`  
- `data_source_type`  

### `spatial_join_results`

- `grib_file`  
- `shapefile_name`  
- `join_type`  
- `gdal_command`  
- `features_matched`  
- `features_total`  
- `match_percentage`  
- `output_file`  
- `join_timestamp`  
- `forecast_id`  
- `boundary_id`  

### `us_wide_composite_products`

- `product_type`  
- `composite_time`  
- `grid_latitude`  
- `grid_longitude`  
- `grid_geom`  
- `grid_resolution_km`  
- `nexrad_reflectivity_dbz`  
- `nexrad_velocity_ms`  
- `nexrad_precipitation_rate_mmh`  
- `nexrad_contribution_weight`  
- `satellite_brightness_temperature_k`  
- `satellite_reflectance_percent`  
- `satellite_cloud_top_height_m`  
- `satellite_precipitation_rate_mmh`  
- `satellite_contribution_weight`  
- `composite_precipitation_rate_mmh`  
- `composite_cloud_fraction`  
- `composite_storm_severity`  
- `data_quality_score`  
- `coverage_percentage`  
- `nexrad_sites_count`  
- `satellite_sources_count`  
- `composite_generation_timestamp`  
- `composite_method`  

### `weather_alerts`

- `event_type`  
- `severity`  
- `urgency`  
- `certainty`  
- `headline`  
- `description`  
- `instruction`  
- `effective_time`  
- `expires_time`  
- `onset_time`  
- `ends_time`  
- `area_description`  
- `geocode_type`  
- `geocode_value`  
- `state_code`  
- `county_code`  
- `cwa_code`  
- `ingestion_timestamp`  
- `alert_geometry`  

### `weather_forecast_aggregations`

- `parameter_name`  
- `forecast_time`  
- `boundary_id`  
- `feature_type`  
- `feature_name`  
- `min_value`  
- `max_value`  
- `avg_value`  
- `median_value`  
- `std_dev_value`  
- `grid_cells_count`  
- `aggregation_timestamp`  

### `weather_observations`

- `station_id`  
- `station_name`  
- `observation_time`  
- `station_latitude`  
- `station_longitude`  
- `station_geom`  
- `temperature`  
- `dewpoint`  
- `humidity`  
- `wind_speed`  
- `wind_direction`  
- `pressure`  
- `visibility`  
- `sky_cover`  
- `precipitation_amount`  
- `data_freshness_minutes`  
- `load_timestamp`  
- `data_source`  

### `weather_stations`

- `station_name`  
- `station_latitude`  
- `station_longitude`  
- `station_geom`  
- `elevation_meters`  
- `state_code`  
- `county_name`  
- `cwa_code`  
- `station_type`  
- `active_status`  
- `first_observation_date`  
- `last_observation_date`  
- `update_frequency_minutes`  

---

*Generated by documentation workflow. MDX-compatible markdown.*
