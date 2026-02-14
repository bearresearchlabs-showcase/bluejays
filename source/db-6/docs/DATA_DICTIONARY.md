## Data Dictionary

This section provides a comprehensive data dictionary for all tables in the database, including column names, data types, constraints, and descriptions. Tables are organized by functional category for easier navigation.

### Composite Products

#### Table: `us_wide_composite_products`

*US-Wide Composite Products Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `composite_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `product_type` | `VARCHAR(100)` | NOT NULL | - |
| `composite_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `grid_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_geom` | `GEOGRAPHY` | - | - |
| `grid_resolution_km` | `NUMERIC(8, 2)` | DEFAULT 1.0 | NEXRAD contributions |
| `nexrad_reflectivity_dbz` | `NUMERIC(6, 2)` | - | - |
| `nexrad_velocity_ms` | `NUMERIC(6, 2)` | - | - |
| `nexrad_precipitation_rate_mmh` | `NUMERIC(8, 2)` | - | - |
| `nexrad_contribution_weight` | `NUMERIC(5, 3)` | - | Satellite contributions |
| `satellite_brightness_temperature_k` | `NUMERIC(8, 2)` | - | - |
| `satellite_reflectance_percent` | `NUMERIC(6, 2)` | - | - |
| `satellite_cloud_top_height_m` | `NUMERIC(8, 2)` | - | - |
| `satellite_precipitation_rate_mmh` | `NUMERIC(8, 2)` | - | - |
| `satellite_contribution_weight` | `NUMERIC(5, 3)` | - | Composite values |
| `composite_precipitation_rate_mmh` | `NUMERIC(8, 2)` | - | - |
| `composite_cloud_fraction` | `NUMERIC(5, 2)` | - | - |
| `composite_storm_severity` | `VARCHAR(50)` | - | Data quality |
| `data_quality_score` | `NUMERIC(5, 2)` | - | - |
| `coverage_percentage` | `NUMERIC(5, 2)` | - | Source information |
| `nexrad_sites_count` | `INTEGER` | - | - |
| `satellite_sources_count` | `INTEGER` | - | Processing metadata |
| `composite_generation_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `composite_method` | `VARCHAR(100)` | - | 'WeightedAverage' |

### Core Weather Data

#### Table: `grib2_forecasts`

*Stores gridded forecast data from NDFD (National Digital Forecast Database)*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `forecast_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `parameter_name` | `VARCHAR(100)` | NOT NULL | - |
| `forecast_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `grid_cell_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_cell_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_cell_geom` | `GEOGRAPHY` | - | - |
| `parameter_value` | `NUMERIC(10, 2)` | - | - |
| `source_file` | `VARCHAR(500)` | - | - |
| `source_crs` | `VARCHAR(50)` | - | - |
| `target_crs` | `VARCHAR(50)` | - | - |
| `grid_resolution_x` | `NUMERIC(10, 6)` | - | - |
| `grid_resolution_y` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | - |
| `load_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `transformation_status` | `VARCHAR(50)` | - | Stores geographic boundaries (CWA, Fire Zones, Marine Zones, River Basins) |

#### Table: `weather_forecast_aggregations`

*Weather Forecast Aggregations Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `aggregation_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `parameter_name` | `VARCHAR(100)` | NOT NULL | - |
| `forecast_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `boundary_id` | `VARCHAR(255)` | - | - |
| `feature_type` | `VARCHAR(50)` | - | - |
| `feature_name` | `VARCHAR(255)` | - | - |
| `min_value` | `NUMERIC(10, 2)` | - | - |
| `max_value` | `NUMERIC(10, 2)` | - | - |
| `avg_value` | `NUMERIC(10, 2)` | - | - |
| `median_value` | `NUMERIC(10, 2)` | - | - |
| `std_dev_value` | `NUMERIC(10, 2)` | - | - |
| `grid_cells_count` | `INTEGER` | - | - |
| `aggregation_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Metadata about weather observation stations |

#### Table: `weather_observations`

*Stores point observations from NWS API*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `observation_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `station_id` | `VARCHAR(50)` | NOT NULL | - |
| `station_name` | `VARCHAR(255)` | - | - |
| `observation_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `station_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `station_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `station_geom` | `GEOGRAPHY` | - | - |
| `temperature` | `NUMERIC(6, 2)` | - | - |
| `dewpoint` | `NUMERIC(6, 2)` | - | - |
| `humidity` | `NUMERIC(5, 2)` | - | - |
| `wind_speed` | `NUMERIC(6, 2)` | - | - |
| `wind_direction` | `INTEGER` | - | - |
| `pressure` | `NUMERIC(8, 2)` | - | - |
| `visibility` | `NUMERIC(6, 2)` | - | - |
| `sky_cover` | `VARCHAR(50)` | - | - |
| `precipitation_amount` | `NUMERIC(8, 2)` | - | - |
| `data_freshness_minutes` | `INTEGER` | - | - |
| `load_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `data_source` | `VARCHAR(50)` | DEFAULT 'NWS_API' | Tracks GRIB2 file processing and transformation operations |

#### Table: `weather_stations`

*Weather Station Metadata Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `station_id` | `VARCHAR(50)` | PRIMARY KEY | - |
| `station_name` | `VARCHAR(255)` | - | - |
| `station_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `station_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `station_geom` | `GEOGRAPHY` | - | - |
| `elevation_meters` | `NUMERIC(8, 2)` | - | - |
| `state_code` | `VARCHAR(2)` | - | - |
| `county_name` | `VARCHAR(100)` | - | - |
| `cwa_code` | `VARCHAR(10)` | - | - |
| `station_type` | `VARCHAR(50)` | - | - |
| `active_status` | `BOOLEAN` | DEFAULT TRUE | - |
| `first_observation_date` | `DATE` | - | - |
| `last_observation_date` | `DATE` | - | - |
| `update_frequency_minutes` | `INTEGER` | - | - |

### Data Processing & Logging

#### Table: `aws_data_source_log`

*Tracks data ingestion from AWS Open Data Registry*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `source_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `source_name` | `VARCHAR(500)` | NOT NULL | - |
| `source_type` | `VARCHAR(100)` | NOT NULL | - |
| `bucket_name` | `VARCHAR(255)` | NOT NULL | - |
| `file_path` | `VARCHAR(1000)` | NOT NULL | - |
| `format` | `VARCHAR(50)` | - | - |
| `ingestion_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `status` | `VARCHAR(50)` | DEFAULT 'Success' | - |
| `metadata` | `VARIANT` | - | - |
| `file_size_bytes` | `BIGINT` | - | - |
| `forecast_date` | `DATE` | - | - |
| `forecast_cycle` | `VARCHAR(2)` | - | - |
| `forecast_hour` | `INTEGER` | - | Tracks observations ingested from NWS API |

#### Table: `crs_transformation_parameters`

*CRS Transformation Parameters Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `transformation_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `source_crs` | `VARCHAR(50)` | NOT NULL | - |
| `target_crs` | `VARCHAR(50)` | NOT NULL | - |
| `source_crs_name` | `VARCHAR(255)` | - | - |
| `target_crs_name` | `VARCHAR(255)` | - | - |
| `transformation_method` | `VARCHAR(50)` | - | - |
| `central_meridian` | `NUMERIC(10, 6)` | - | - |
| `false_easting` | `NUMERIC(12, 2)` | - | - |
| `false_northing` | `NUMERIC(12, 2)` | - | - |
| `scale_factor` | `NUMERIC(10, 8)` | - | - |
| `latitude_of_origin` | `NUMERIC(10, 6)` | - | - |
| `units` | `VARCHAR(50)` | - | - |
| `accuracy_meters` | `NUMERIC(10, 2)` | - | - |
| `usage_count` | `INTEGER` | DEFAULT 0 | Tracks data quality metrics for weather products |

#### Table: `data_quality_metrics`

*Tracks data quality metrics for weather products*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `metric_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `metric_date` | `DATE` | NOT NULL | - |
| `data_source` | `VARCHAR(50)` | NOT NULL | - |
| `files_processed` | `INTEGER` | DEFAULT 0 | - |
| `files_successful` | `INTEGER` | DEFAULT 0 | - |
| `files_failed` | `INTEGER` | DEFAULT 0 | - |
| `success_rate` | `NUMERIC(5, 2)` | - | - |
| `total_records` | `INTEGER` | DEFAULT 0 | - |
| `records_with_errors` | `INTEGER` | DEFAULT 0 | - |
| `error_rate` | `NUMERIC(5, 2)` | - | - |
| `spatial_coverage_km2` | `NUMERIC(15, 2)` | - | - |
| `temporal_coverage_hours` | `INTEGER` | - | - |
| `data_freshness_minutes` | `INTEGER` | - | - |
| `calculation_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Tracks data loading operations to Databricks |

#### Table: `geoplatform_dataset_log`

*Tracks geospatial datasets discovered from geoplatform.gov*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `dataset_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `title` | `VARCHAR(500)` | - | - |
| `description` | `VARCHAR(2000)` | - | - |
| `url` | `VARCHAR(1000)` | - | - |
| `search_term` | `VARCHAR(100)` | - | - |
| `ingestion_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `status` | `VARCHAR(50)` | DEFAULT 'Discovered' | - |
| `dataset_type` | `VARCHAR(100)` | - | - |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | Extended to support multiple data sources |
| `ALTER` | `TABLE` | DEFAULT 'NDFD'; | - |
| `ALTER` | `TABLE` | - | 'GFS' |
| `ALTER` | `TABLE` | - | - |
| `ALTER` | `TABLE` | - | - |
| `ALTER` | `TABLE` | - | For ensemble forecasts Extended to support NWS API data |
| `ALTER` | `TABLE` | - | - |
| `ALTER` | `TABLE` | - | Stores NWS weather alerts and warnings |

#### Table: `grib2_transformation_log`

*Tracks GRIB2 file processing and transformation operations*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `log_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `file_name` | `VARCHAR(500)` | NOT NULL | - |
| `source_path` | `VARCHAR(1000)` | - | - |
| `parameter_name` | `VARCHAR(100)` | NOT NULL | - |
| `forecast_time` | `TIMESTAMP_NTZ` | - | - |
| `source_crs` | `VARCHAR(50)` | - | - |
| `target_crs` | `VARCHAR(50)` | - | - |
| `gdal_command` | `VARCHAR(2000)` | - | - |
| `output_file` | `VARCHAR(1000)` | - | - |
| `grid_resolution_x` | `NUMERIC(10, 6)` | - | - |
| `grid_resolution_y` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | - |
| `transformation_status` | `VARCHAR(50)` | - | - |
| `target_table` | `VARCHAR(255)` | - | - |
| `load_timestamp` | `TIMESTAMP_NTZ` | - | - |
| `processing_duration_seconds` | `INTEGER` | - | - |
| `records_processed` | `INTEGER` | - | - |
| `error_message` | `VARCHAR(2000)` | - | Tracks shapefile processing and coordinate transformations |

#### Table: `nexrad_transformation_log`

*Tracks NEXRAD data transformation operations*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `transformation_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `site_id` | `VARCHAR(4)` | NOT NULL | - |
| `source_file` | `VARCHAR(1000)` | NOT NULL | - |
| `transformation_type` | `VARCHAR(100)` | NOT NULL | - |
| `transformation_start_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `transformation_end_time` | `TIMESTAMP_NTZ` | - | - |
| `transformation_duration_seconds` | `INTEGER` | - | Input parameters |
| `input_format` | `VARCHAR(50)` | - | - |
| `input_size_bytes` | `BIGINT` | - | - |
| `input_records` | `INTEGER` | - | Output parameters |
| `output_format` | `VARCHAR(50)` | - | - |
| `output_size_bytes` | `BIGINT` | - | - |
| `output_records` | `INTEGER` | - | Transformation status |
| `transformation_status` | `VARCHAR(50)` | DEFAULT 'Success' | - |
| `error_message` | `VARCHAR(2000)` | - | Processing details |
| `processing_method` | `VARCHAR(100)` | - | - |
| `processing_parameters` | `VARCHAR(2000)` | - | Spatial extent |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | Metadata |
| `created_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Tracks satellite imagery transformation operations |

#### Table: `nws_api_observation_log`

*Tracks observations ingested from NWS API*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `log_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `station_id` | `VARCHAR(50)` | NOT NULL | - |
| `observation_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `api_endpoint` | `VARCHAR(500)` | - | - |
| `response_status` | `INTEGER` | - | - |
| `data_freshness_minutes` | `INTEGER` | - | - |
| `ingestion_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `status` | `VARCHAR(50)` | DEFAULT 'Success' | - |
| `error_message` | `VARCHAR(2000)` | - | Tracks geospatial datasets discovered from geoplatform.gov |

#### Table: `satellite_transformation_log`

*Tracks satellite imagery transformation operations*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `transformation_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `source_id` | `VARCHAR(255)` | NOT NULL | - |
| `source_file` | `VARCHAR(1000)` | NOT NULL | - |
| `transformation_type` | `VARCHAR(100)` | NOT NULL | - |
| `transformation_start_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `transformation_end_time` | `TIMESTAMP_NTZ` | - | - |
| `transformation_duration_seconds` | `INTEGER` | - | Input parameters |
| `input_format` | `VARCHAR(50)` | - | - |
| `input_size_bytes` | `BIGINT` | - | - |
| `input_bands` | `INTEGER` | - | - |
| `input_dimensions` | `VARCHAR(100)` | - | Output parameters |
| `output_format` | `VARCHAR(50)` | - | - |
| `output_size_bytes` | `BIGINT` | - | - |
| `output_records` | `INTEGER` | - | Transformation status |
| `transformation_status` | `VARCHAR(50)` | DEFAULT 'Success' | - |
| `error_message` | `VARCHAR(2000)` | - | Processing details |
| `processing_method` | `VARCHAR(100)` | - | - |
| `processing_parameters` | `VARCHAR(2000)` | - | - |
| `crs_transformation` | `VARCHAR(100)` | - | Spatial extent |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | Metadata |
| `created_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Composite products combining NEXRAD and satellite data across entire US |

#### Table: `shapefile_integration_log`

*Tracks shapefile processing and coordinate transformations*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `log_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `shapefile_name` | `VARCHAR(500)` | NOT NULL | - |
| `source_path` | `VARCHAR(1000)` | - | - |
| `feature_type` | `VARCHAR(50)` | NOT NULL | - |
| `feature_count` | `INTEGER` | - | - |
| `source_crs` | `VARCHAR(50)` | - | - |
| `target_crs` | `VARCHAR(50)` | - | - |
| `ogr2ogr_command` | `VARCHAR(2000)` | - | - |
| `transformed_path` | `VARCHAR(1000)` | - | - |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | - |
| `transformation_status` | `VARCHAR(50)` | - | - |
| `target_table` | `VARCHAR(255)` | - | - |
| `load_timestamp` | `TIMESTAMP_NTZ` | - | - |
| `processing_duration_seconds` | `INTEGER` | - | - |
| `error_message` | `VARCHAR(2000)` | - | Documents spatial join operations between GRIB2 grid cells and shapefile boundaries |

#### Table: `load_status`

*Tracks data loading operations to Databricks*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `load_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `source_file` | `VARCHAR(1000)` | - | - |
| `target_table` | `VARCHAR(255)` | NOT NULL | - |
| `load_start_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `load_end_time` | `TIMESTAMP_NTZ` | - | - |
| `load_duration_seconds` | `INTEGER` | - | - |
| `records_loaded` | `INTEGER` | DEFAULT 0 | - |
| `file_size_mb` | `NUMERIC(10, 2)` | - | - |
| `load_rate_mb_per_sec` | `NUMERIC(10, 2)` | - | - |
| `load_status` | `VARCHAR(50)` | - | - |
| `error_message` | `VARCHAR(2000)` | - | - |
| `warehouse` | `VARCHAR(255)` | - | - |
| `data_source_type` | `VARCHAR(50)` | - | Pre-aggregated forecast data for performance |

#### Table: `spatial_join_results`

*Spatial Join Results Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `join_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `grib_file` | `VARCHAR(500)` | - | - |
| `shapefile_name` | `VARCHAR(500)` | - | - |
| `join_type` | `VARCHAR(50)` | - | - |
| `gdal_command` | `VARCHAR(2000)` | - | - |
| `features_matched` | `INTEGER` | - | - |
| `features_total` | `INTEGER` | - | - |
| `match_percentage` | `NUMERIC(5, 2)` | - | - |
| `output_file` | `VARCHAR(1000)` | - | - |
| `join_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `forecast_id` | `VARCHAR(255)` | - | - |
| `boundary_id` | `VARCHAR(255)` | - | Documents coordinate reference system transformations and parameters |

### Geographic Boundaries

#### Table: `shapefile_boundaries`

*Stores geographic boundaries (CWA, Fire Zones, Marine Zones, River Basins)*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `boundary_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `feature_type` | `VARCHAR(50)` | NOT NULL | - |
| `feature_name` | `VARCHAR(255)` | - | - |
| `feature_identifier` | `VARCHAR(100)` | - | - |
| `boundary_geom` | `GEOGRAPHY` | - | - |
| `source_shapefile` | `VARCHAR(500)` | - | - |
| `source_crs` | `VARCHAR(50)` | - | - |
| `target_crs` | `VARCHAR(50)` | - | - |
| `feature_count` | `INTEGER` | - | - |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | - |
| `load_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `transformation_status` | `VARCHAR(50)` | - | - |
| `state_code` | `VARCHAR(2)` | - | - |
| `office_code` | `VARCHAR(10)` | - | Stores point observations from NWS API |

### Insurance & Risk Modeling

#### Table: `forecast_rate_mapping`

*Forecast-to-Rate Mapping Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `mapping_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `forecast_id` | `VARCHAR(255)` | NOT NULL | - |
| `rate_table_id` | `VARCHAR(255)` | - | - |
| `risk_factor_id` | `VARCHAR(255)` | - | - |
| `policy_area_id` | `VARCHAR(255)` | NOT NULL | - |
| `forecast_date` | `DATE` | NOT NULL | - |
| `forecast_day` | `INTEGER` | NOT NULL | - |
| `forecast_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `parameter_name` | `VARCHAR(100)` | NOT NULL | - |
| `parameter_value` | `NUMERIC(10, 2)` | - | - |
| `risk_contribution` | `NUMERIC(10, 4)` | - | - |
| `rate_impact` | `NUMERIC(10, 4)` | - | - |
| `mapping_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Compares rates across different forecast days (7-14 days) |

#### Table: `insurance_claims_history`

*Insurance Claims History Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `claim_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `policy_area_id` | `VARCHAR(255)` | - | - |
| `claim_date` | `DATE` | NOT NULL | - |
| `loss_date` | `DATE` | NOT NULL | - |
| `policy_type` | `VARCHAR(50)` | - | - |
| `coverage_type` | `VARCHAR(100)` | - | - |
| `claim_type` | `VARCHAR(100)` | - | - |
| `loss_amount` | `NUMERIC(12, 2)` | - | - |
| `claim_status` | `VARCHAR(50)` | - | - |
| `weather_event_type` | `VARCHAR(100)` | - | - |
| `weather_event_date` | `DATE` | - | Weather conditions at time of loss |
| `temperature_at_loss` | `NUMERIC(6, 2)` | - | - |
| `precipitation_at_loss` | `NUMERIC(8, 2)` | - | - |
| `wind_speed_at_loss` | `NUMERIC(6, 2)` | - | Forecast accuracy (if forecast was available) |
| `forecast_available` | `BOOLEAN` | DEFAULT FALSE | - |
| `forecast_day` | `INTEGER` | - | - |
| `forecast_error` | `NUMERIC(10, 2)` | - | Metadata |
| `created_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Maps specific forecasts to rate calculations |

#### Table: `insurance_policy_areas`

*Insurance Policy Areas Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `policy_area_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `boundary_id` | `VARCHAR(255)` | NOT NULL | - |
| `policy_type` | `VARCHAR(50)` | NOT NULL | - |
| `coverage_type` | `VARCHAR(100)` | - | - |
| `policy_area_name` | `VARCHAR(255)` | - | - |
| `state_code` | `VARCHAR(2)` | - | - |
| `county_code` | `VARCHAR(5)` | - | - |
| `cwa_code` | `VARCHAR(10)` | - | - |
| `risk_zone` | `VARCHAR(50)` | - | - |
| `base_rate_factor` | `NUMERIC(5, 3)` | DEFAULT 1.000 | - |
| `effective_date` | `DATE` | NOT NULL | - |
| `expiration_date` | `DATE` | - | - |
| `is_active` | `BOOLEAN` | DEFAULT TRUE | - |
| `created_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `updated_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Stores calculated risk factors based on weather forecasts |

#### Table: `insurance_rate_tables`

*Stores calculated rate tables based on forecast risk factors*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `rate_table_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `policy_area_id` | `VARCHAR(255)` | NOT NULL | - |
| `policy_type` | `VARCHAR(50)` | NOT NULL | - |
| `coverage_type` | `VARCHAR(100)` | - | - |
| `forecast_period_start` | `DATE` | NOT NULL | - |
| `forecast_period_end` | `DATE` | NOT NULL | - |
| `forecast_day` | `INTEGER` | NOT NULL | - |
| `forecast_date` | `DATE` | NOT NULL | Base rates |
| `base_rate` | `NUMERIC(10, 2)` | - | - |
| `base_rate_currency` | `VARCHAR(3)` | DEFAULT 'USD' | Risk-adjusted rates |
| `risk_adjusted_rate` | `NUMERIC(10, 2)` | - | - |
| `risk_multiplier` | `NUMERIC(5, 3)` | - | Rate components |
| `base_component` | `NUMERIC(10, 2)` | - | - |
| `precipitation_risk_component` | `NUMERIC(10, 2)` | - | - |
| `temperature_risk_component` | `NUMERIC(10, 2)` | - | - |
| `wind_risk_component` | `NUMERIC(10, 2)` | - | - |
| `freeze_risk_component` | `NUMERIC(10, 2)` | - | - |
| `flood_risk_component` | `NUMERIC(10, 2)` | - | - |
| `extreme_event_component` | `NUMERIC(10, 2)` | - | Rate tiers |
| `rate_tier` | `VARCHAR(50)` | - | - |
| `rate_category` | `VARCHAR(50)` | - | Metadata |
| `calculation_method` | `VARCHAR(100)` | - | - |
| `confidence_level` | `NUMERIC(5, 2)` | - | - |
| `effective_date` | `DATE` | NOT NULL | - |
| `expiration_date` | `DATE` | - | - |
| `created_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `updated_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Historical claims data for validation and comparison |

#### Table: `insurance_risk_factors`

*Stores calculated risk factors based on weather forecasts*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `risk_factor_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `policy_area_id` | `VARCHAR(255)` | NOT NULL | - |
| `forecast_period_start` | `DATE` | NOT NULL | - |
| `forecast_period_end` | `DATE` | NOT NULL | - |
| `forecast_day` | `INTEGER` | NOT NULL | - |
| `forecast_date` | `DATE` | NOT NULL | - |
| `parameter_name` | `VARCHAR(100)` | NOT NULL | Risk metrics |
| `extreme_event_probability` | `NUMERIC(5, 4)` | - | - |
| `cumulative_precipitation_risk` | `NUMERIC(10, 2)` | - | - |
| `wind_damage_risk` | `NUMERIC(10, 2)` | - | - |
| `freeze_risk` | `NUMERIC(10, 2)` | - | - |
| `flood_risk` | `NUMERIC(10, 2)` | - | Forecast statistics |
| `min_forecast_value` | `NUMERIC(10, 2)` | - | - |
| `max_forecast_value` | `NUMERIC(10, 2)` | - | - |
| `avg_forecast_value` | `NUMERIC(10, 2)` | - | - |
| `median_forecast_value` | `NUMERIC(10, 2)` | - | - |
| `stddev_forecast_value` | `NUMERIC(10, 2)` | - | - |
| `percentile_90_value` | `NUMERIC(10, 2)` | - | - |
| `percentile_95_value` | `NUMERIC(10, 2)` | - | - |
| `percentile_99_value` | `NUMERIC(10, 2)` | - | Risk scores (0-100 scale) |
| `overall_risk_score` | `NUMERIC(5, 2)` | - | - |
| `risk_category` | `VARCHAR(50)` | - | Metadata |
| `calculation_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `forecast_model` | `VARCHAR(100)` | - | - |
| `data_quality_score` | `NUMERIC(5, 2)` | - | Stores calculated rate tables based on forecast risk factors |

#### Table: `rate_table_comparison`

*Rate Table Comparison Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `comparison_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `policy_area_id` | `VARCHAR(255)` | NOT NULL | - |
| `policy_type` | `VARCHAR(50)` | NOT NULL | - |
| `forecast_period_start` | `DATE` | NOT NULL | - |
| `forecast_period_end` | `DATE` | NOT NULL | - |
| `forecast_date` | `DATE` | NOT NULL | Rates by forecast day |
| `rate_day_7` | `NUMERIC(10, 2)` | - | - |
| `rate_day_8` | `NUMERIC(10, 2)` | - | - |
| `rate_day_9` | `NUMERIC(10, 2)` | - | - |
| `rate_day_10` | `NUMERIC(10, 2)` | - | - |
| `rate_day_11` | `NUMERIC(10, 2)` | - | - |
| `rate_day_12` | `NUMERIC(10, 2)` | - | - |
| `rate_day_13` | `NUMERIC(10, 2)` | - | - |
| `rate_day_14` | `NUMERIC(10, 2)` | - | Statistics |
| `min_rate` | `NUMERIC(10, 2)` | - | - |
| `max_rate` | `NUMERIC(10, 2)` | - | - |
| `avg_rate` | `NUMERIC(10, 2)` | - | - |
| `median_rate` | `NUMERIC(10, 2)` | - | - |
| `rate_volatility` | `NUMERIC(10, 4)` | - | - |
| `rate_trend` | `VARCHAR(50)` | - | Recommended rate |
| `recommended_rate` | `NUMERIC(10, 2)` | - | - |
| `recommended_forecast_day` | `INTEGER` | - | - |
| `confidence_score` | `NUMERIC(5, 2)` | - | - |
| `comparison_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |

### NEXRAD Radar Data

#### Table: `nexrad_level2_data`

*Stores decompressed NEXRAD Level II radar data*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `radar_data_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `site_id` | `VARCHAR(4)` | NOT NULL | - |
| `scan_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `volume_scan_number` | `INTEGER` | - | - |
| `elevation_angle` | `NUMERIC(5, 2)` | - | - |
| `azimuth_angle` | `NUMERIC(6, 2)` | - | - |
| `range_gate` | `INTEGER` | - | - |
| `range_km` | `NUMERIC(8, 2)` | - | Reflectivity data |
| `reflectivity_dbz` | `NUMERIC(6, 2)` | - | - |
| `reflectivity_geom` | `GEOGRAPHY` | - | Velocity data |
| `radial_velocity_ms` | `NUMERIC(6, 2)` | - | - |
| `velocity_geom` | `GEOGRAPHY` | - | Spectrum width |
| `spectrum_width_ms` | `NUMERIC(6, 2)` | - | Data quality |
| `data_quality_flag` | `INTEGER` | - | Source file information |
| `source_file` | `VARCHAR(1000)` | - | - |
| `aws_bucket` | `VARCHAR(255)` | - | - |
| `aws_key` | `VARCHAR(1000)` | - | - |
| `file_format` | `VARCHAR(50)` | DEFAULT 'Level2' | - |
| `compression_type` | `VARCHAR(50)` | - | - |
| `decompression_status` | `VARCHAR(50)` | DEFAULT 'Success' | Metadata |
| `data_type` | `VARCHAR(50)` | - | - |
| `sweep_mode` | `VARCHAR(50)` | - | - |
| `pulse_repetition_frequency` | `INTEGER` | - | - |
| `nyquist_velocity_ms` | `NUMERIC(6, 2)` | - | Spatial extent |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | Processing metadata |
| `ingestion_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `processing_duration_seconds` | `INTEGER` | - | - |
| `records_processed` | `INTEGER` | - | Gridded reflectivity data for easier spatial analysis |

#### Table: `nexrad_radar_sites`

*NEXRAD Radar Sites Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `site_id` | `VARCHAR(4)` | PRIMARY KEY | - |
| `site_name` | `VARCHAR(255)` | NOT NULL | - |
| `site_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `site_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `site_geom` | `GEOGRAPHY` | - | - |
| `elevation_meters` | `NUMERIC(8, 2)` | - | - |
| `state_code` | `VARCHAR(2)` | - | - |
| `county_name` | `VARCHAR(100)` | - | - |
| `cwa_code` | `VARCHAR(10)` | - | - |
| `radar_type` | `VARCHAR(50)` | DEFAULT 'WSR-88D' | - |
| `operational_status` | `VARCHAR(50)` | DEFAULT 'Operational' | - |
| `coverage_radius_km` | `NUMERIC(8, 2)` | DEFAULT 230.0 | - |
| `first_operational_date` | `DATE` | - | - |
| `last_maintenance_date` | `DATE` | - | - |
| `update_frequency_minutes` | `INTEGER` | DEFAULT 5 | - |
| `created_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `updated_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Stores decompressed NEXRAD Level II radar data |

#### Table: `nexrad_reflectivity_grid`

*NEXRAD Reflectivity Grid Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `grid_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `site_id` | `VARCHAR(4)` | NOT NULL | - |
| `scan_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `grid_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_geom` | `GEOGRAPHY` | - | - |
| `grid_resolution_km` | `NUMERIC(6, 2)` | DEFAULT 1.0 | Reflectivity values |
| `max_reflectivity_dbz` | `NUMERIC(6, 2)` | - | - |
| `mean_reflectivity_dbz` | `NUMERIC(6, 2)` | - | - |
| `min_reflectivity_dbz` | `NUMERIC(6, 2)` | - | - |
| `reflectivity_count` | `INTEGER` | - | Composite reflectivity (highest reflectivity at any elevation) |
| `composite_reflectivity_dbz` | `NUMERIC(6, 2)` | - | Height of maximum reflectivity |
| `height_of_max_reflectivity_m` | `NUMERIC(8, 2)` | - | Precipitation estimates |
| `precipitation_rate_mmh` | `NUMERIC(8, 2)` | - | - |
| `accumulated_precipitation_mm` | `NUMERIC(8, 2)` | - | Storm attributes |
| `storm_cell_id` | `VARCHAR(255)` | - | - |
| `storm_severity` | `VARCHAR(50)` | - | Processing metadata |
| `grid_generation_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `grid_method` | `VARCHAR(100)` | - | 'NearestNeighbor' Gridded velocity data for wind analysis |

#### Table: `nexrad_storm_cells`

*Tracks storm cells across multiple scans*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `storm_cell_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `site_id` | `VARCHAR(4)` | NOT NULL | - |
| `first_detection_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `last_detection_time` | `TIMESTAMP_NTZ` | - | - |
| `storm_center_latitude` | `NUMERIC(10, 7)` | - | - |
| `storm_center_longitude` | `NUMERIC(10, 7)` | - | - |
| `storm_center_geom` | `GEOGRAPHY` | - | - |
| `storm_polygon_geom` | `GEOGRAPHY` | - | Storm characteristics |
| `max_reflectivity_dbz` | `NUMERIC(6, 2)` | - | - |
| `max_velocity_ms` | `NUMERIC(6, 2)` | - | - |
| `storm_area_km2` | `NUMERIC(10, 2)` | - | - |
| `storm_diameter_km` | `NUMERIC(8, 2)` | - | - |
| `storm_perimeter_km` | `NUMERIC(8, 2)` | - | Movement |
| `storm_speed_ms` | `NUMERIC(6, 2)` | - | - |
| `storm_direction_deg` | `NUMERIC(6, 2)` | - | Severity classification |
| `storm_severity` | `VARCHAR(50)` | - | - |
| `storm_type` | `VARCHAR(50)` | - | Tracking metadata |
| `track_duration_minutes` | `INTEGER` | - | - |
| `scan_count` | `INTEGER` | - | - |
| `tracking_status` | `VARCHAR(50)` | DEFAULT 'Active' | Processing metadata |
| `tracking_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Metadata for satellite imagery sources (GOES, etc.) |

#### Table: `nexrad_velocity_grid`

*NEXRAD Velocity Grid Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `grid_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `site_id` | `VARCHAR(4)` | NOT NULL | - |
| `scan_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `grid_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_geom` | `GEOGRAPHY` | - | - |
| `grid_resolution_km` | `NUMERIC(6, 2)` | DEFAULT 1.0 | Velocity values |
| `radial_velocity_ms` | `NUMERIC(6, 2)` | - | - |
| `velocity_azimuth` | `NUMERIC(6, 2)` | - | Wind components (derived) |
| `u_wind_component_ms` | `NUMERIC(6, 2)` | - | - |
| `v_wind_component_ms` | `NUMERIC(6, 2)` | - | - |
| `wind_speed_ms` | `NUMERIC(6, 2)` | - | - |
| `wind_direction_deg` | `NUMERIC(6, 2)` | - | Spectrum width |
| `spectrum_width_ms` | `NUMERIC(6, 2)` | - | Velocity quality |
| `velocity_quality_flag` | `INTEGER` | - | Processing metadata |
| `grid_generation_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Tracks storm cells across multiple scans |

### Satellite Imagery

#### Table: `satellite_imagery_grid`

*Satellite Imagery Grid Aggregations Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `grid_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `source_id` | `VARCHAR(255)` | NOT NULL | - |
| `product_type` | `VARCHAR(100)` | NOT NULL | - |
| `scan_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `grid_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_geom` | `GEOGRAPHY` | - | - |
| `grid_resolution_km` | `NUMERIC(8, 2)` | - | Aggregated values |
| `min_value` | `NUMERIC(10, 4)` | - | - |
| `max_value` | `NUMERIC(10, 4)` | - | - |
| `mean_value` | `NUMERIC(10, 4)` | - | - |
| `median_value` | `NUMERIC(10, 4)` | - | - |
| `stddev_value` | `NUMERIC(10, 4)` | - | - |
| `pixel_count` | `INTEGER` | - | Cloud properties |
| `cloud_fraction` | `NUMERIC(5, 2)` | - | - |
| `cloud_top_height_m` | `NUMERIC(8, 2)` | - | - |
| `cloud_top_temperature_k` | `NUMERIC(8, 2)` | - | Fire properties |
| `fire_count` | `INTEGER` | - | - |
| `total_fire_power_mw` | `NUMERIC(12, 2)` | - | Precipitation properties |
| `precipitation_rate_mmh` | `NUMERIC(8, 2)` | - | Processing metadata |
| `aggregation_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `aggregation_method` | `VARCHAR(100)` | - | 'Mean' Tracks NEXRAD data transformation operations |

#### Table: `satellite_imagery_products`

*Satellite Imagery Products Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `product_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `source_id` | `VARCHAR(255)` | NOT NULL | - |
| `product_name` | `VARCHAR(255)` | NOT NULL | - |
| `product_type` | `VARCHAR(100)` | - | - |
| `band_number` | `INTEGER` | - | - |
| `band_name` | `VARCHAR(100)` | - | - |
| `wavelength_um` | `NUMERIC(8, 4)` | - | - |
| `scan_start_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `scan_end_time` | `TIMESTAMP_NTZ` | - | - |
| `scan_duration_seconds` | `INTEGER` | - | Spatial information |
| `grid_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_geom` | `GEOGRAPHY` | - | - |
| `grid_resolution_km` | `NUMERIC(8, 2)` | - | Pixel values |
| `pixel_value` | `NUMERIC(10, 4)` | - | - |
| `calibrated_value` | `NUMERIC(10, 4)` | - | - |
| `brightness_temperature_k` | `NUMERIC(8, 2)` | - | - |
| `reflectance_percent` | `NUMERIC(6, 2)` | - | Derived products |
| `cloud_top_height_m` | `NUMERIC(8, 2)` | - | - |
| `cloud_top_temperature_k` | `NUMERIC(8, 2)` | - | - |
| `cloud_phase` | `VARCHAR(50)` | - | - |
| `cloud_optical_depth` | `NUMERIC(8, 4)` | - | Fire detection |
| `fire_detection_confidence` | `NUMERIC(5, 2)` | - | - |
| `fire_temperature_k` | `NUMERIC(8, 2)` | - | - |
| `fire_power_mw` | `NUMERIC(12, 2)` | - | Precipitation |
| `precipitation_rate_mmh` | `NUMERIC(8, 2)` | - | Source file information |
| `source_file` | `VARCHAR(1000)` | - | - |
| `aws_bucket` | `VARCHAR(255)` | - | - |
| `aws_key` | `VARCHAR(1000)` | - | - |
| `file_format` | `VARCHAR(50)` | DEFAULT 'NetCDF' | - |
| `compression_type` | `VARCHAR(50)` | - | - |
| `decompression_status` | `VARCHAR(50)` | DEFAULT 'Success' | Spatial extent |
| `spatial_extent_west` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_south` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_east` | `NUMERIC(10, 6)` | - | - |
| `spatial_extent_north` | `NUMERIC(10, 6)` | - | Processing metadata |
| `ingestion_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `processing_duration_seconds` | `INTEGER` | - | - |
| `records_processed` | `INTEGER` | - | Aggregated satellite imagery data for spatial analysis |

#### Table: `satellite_imagery_sources`

*Satellite Imagery Sources Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `source_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `satellite_name` | `VARCHAR(100)` | NOT NULL | - |
| `satellite_type` | `VARCHAR(50)` | DEFAULT 'GOES' | - |
| `sensor_name` | `VARCHAR(100)` | - | - |
| `orbital_position` | `VARCHAR(50)` | - | Spatial coverage |
| `coverage_area` | `VARCHAR(100)` | DEFAULT 'CONUS' | - |
| `spatial_resolution_km` | `NUMERIC(8, 2)` | - | - |
| `scan_frequency_minutes` | `INTEGER` | - | - |
| `temporal_resolution_minutes` | `INTEGER` | - | Operational status |
| `operational_status` | `VARCHAR(50)` | DEFAULT 'Operational' | - |
| `first_operational_date` | `DATE` | - | - |
| `last_update_date` | `DATE` | - | - |
| `created_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `updated_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Decompressed satellite imagery products |

### Weather Alerts & Model Comparisons

#### Table: `data_source_statistics`

*Tracks statistics for each data source*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `stat_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `source_type` | `VARCHAR(100)` | NOT NULL | - |
| `source_name` | `VARCHAR(500)` | - | - |
| `stat_date` | `DATE` | NOT NULL | - |
| `files_ingested` | `INTEGER` | DEFAULT 0 | - |
| `records_processed` | `INTEGER` | DEFAULT 0 | - |
| `data_volume_mb` | `NUMERIC(15, 2)` | - | - |
| `ingestion_duration_seconds` | `INTEGER` | - | - |
| `success_rate` | `NUMERIC(5, 2)` | - | - |
| `avg_latency_seconds` | `NUMERIC(10, 2)` | - | - |
| `error_count` | `INTEGER` | DEFAULT 0 | - |
| `calculation_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |

#### Table: `model_forecast_comparison`

*Model Forecast Comparison Table*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `comparison_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `forecast_time` | `TIMESTAMP_NTZ` | NOT NULL | - |
| `parameter_name` | `VARCHAR(100)` | NOT NULL | - |
| `grid_cell_latitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `grid_cell_longitude` | `NUMERIC(10, 7)` | NOT NULL | - |
| `gfs_value` | `NUMERIC(10, 2)` | - | - |
| `hrrr_value` | `NUMERIC(10, 2)` | - | - |
| `rap_value` | `NUMERIC(10, 2)` | - | - |
| `gefs_mean_value` | `NUMERIC(10, 2)` | - | - |
| `gefs_stddev_value` | `NUMERIC(10, 2)` | - | - |
| `observation_value` | `NUMERIC(10, 2)` | - | - |
| `observation_time` | `TIMESTAMP_NTZ` | - | - |
| `gfs_error` | `NUMERIC(10, 2)` | - | - |
| `hrrr_error` | `NUMERIC(10, 2)` | - | - |
| `rap_error` | `NUMERIC(10, 2)` | - | - |
| `best_model` | `VARCHAR(50)` | - | - |
| `comparison_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | Tracks statistics for each data source |

#### Table: `weather_alerts`

*Stores NWS weather alerts and warnings*

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `alert_id` | `VARCHAR(255)` | PRIMARY KEY | - |
| `event_type` | `VARCHAR(100)` | NOT NULL | - |
| `severity` | `VARCHAR(50)` | - | - |
| `urgency` | `VARCHAR(50)` | - | - |
| `certainty` | `VARCHAR(50)` | - | - |
| `headline` | `VARCHAR(500)` | - | - |
| `description` | `TEXT` | - | - |
| `instruction` | `TEXT` | - | - |
| `effective_time` | `TIMESTAMP_NTZ` | - | - |
| `expires_time` | `TIMESTAMP_NTZ` | - | - |
| `onset_time` | `TIMESTAMP_NTZ` | - | - |
| `ends_time` | `TIMESTAMP_NTZ` | - | - |
| `area_description` | `VARCHAR(1000)` | - | - |
| `geocode_type` | `VARCHAR(50)` | - | - |
| `geocode_value` | `VARCHAR(100)` | - | - |
| `state_code` | `VARCHAR(2)` | - | - |
| `county_code` | `VARCHAR(5)` | - | - |
| `cwa_code` | `VARCHAR(10)` | - | - |
| `ingestion_timestamp` | `TIMESTAMP_NTZ` | DEFAULT CURRENT_TIMESTAMP | - |
| `alert_geometry` | `GEOGRAPHY` | - | Polygon geometry for alert area Compares forecasts from different models |

---

