-- Weather Data Pipeline Database Schema
-- Compatible with PostgreSQL
-- Production schema for weather data pipeline system

-- GRIB2 Forecasts Table
-- Stores gridded forecast data from NDFD (National Digital Forecast Database)
CREATE TABLE grib2_forecasts (
    forecast_id VARCHAR(255) PRIMARY KEY,
    parameter_name VARCHAR(100) NOT NULL,
    forecast_time TIMESTAMP_NTZ NOT NULL,
    grid_cell_latitude NUMERIC(10, 7) NOT NULL,
    grid_cell_longitude NUMERIC(10, 7) NOT NULL,
    grid_cell_geom GEOGRAPHY,  -- Point geometry for grid cell center (PostgreSQL/Databricks)
    parameter_value NUMERIC(10, 2),
    source_file VARCHAR(500),
    source_crs VARCHAR(50),
    target_crs VARCHAR(50),
    grid_resolution_x NUMERIC(10, 6),
    grid_resolution_y NUMERIC(10, 6),
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    load_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    transformation_status VARCHAR(50)
);

-- Shapefile Boundaries Table
-- Stores geographic boundaries (CWA, Fire Zones, Marine Zones, River Basins)
CREATE TABLE shapefile_boundaries (
    boundary_id VARCHAR(255) PRIMARY KEY,
    feature_type VARCHAR(50) NOT NULL,  -- 'CWA', 'FireZone', 'MarineZone', 'RiverBasin', 'County'
    feature_name VARCHAR(255),
    feature_identifier VARCHAR(100),
    boundary_geom GEOGRAPHY,  -- Polygon geometry
    source_shapefile VARCHAR(500),
    source_crs VARCHAR(50),
    target_crs VARCHAR(50),
    feature_count INTEGER,
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    load_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    transformation_status VARCHAR(50),
    state_code VARCHAR(2),
    office_code VARCHAR(10)
);

-- Real-Time Weather Observations Table
-- Stores point observations from NWS API
CREATE TABLE weather_observations (
    observation_id VARCHAR(255) PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL,
    station_name VARCHAR(255),
    observation_time TIMESTAMP_NTZ NOT NULL,
    station_latitude NUMERIC(10, 7) NOT NULL,
    station_longitude NUMERIC(10, 7) NOT NULL,
    station_geom GEOGRAPHY,  -- Point geometry
    temperature NUMERIC(6, 2),
    dewpoint NUMERIC(6, 2),
    humidity NUMERIC(5, 2),
    wind_speed NUMERIC(6, 2),
    wind_direction INTEGER,
    pressure NUMERIC(8, 2),
    visibility NUMERIC(6, 2),
    sky_cover VARCHAR(50),
    precipitation_amount NUMERIC(8, 2),
    data_freshness_minutes INTEGER,
    load_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    data_source VARCHAR(50) DEFAULT 'NWS_API'
);

-- GRIB2 Transformation Log Table
-- Tracks GRIB2 file processing and transformation operations
CREATE TABLE grib2_transformation_log (
    log_id VARCHAR(255) PRIMARY KEY,
    file_name VARCHAR(500) NOT NULL,
    source_path VARCHAR(1000),
    parameter_name VARCHAR(100) NOT NULL,
    forecast_time TIMESTAMP_NTZ,
    source_crs VARCHAR(50),
    target_crs VARCHAR(50),
    gdal_command VARCHAR(2000),
    output_file VARCHAR(1000),
    grid_resolution_x NUMERIC(10, 6),
    grid_resolution_y NUMERIC(10, 6),
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    transformation_status VARCHAR(50),
    target_table VARCHAR(255),
    load_timestamp TIMESTAMP_NTZ,
    processing_duration_seconds INTEGER,
    records_processed INTEGER,
    error_message VARCHAR(2000)
);

-- Shapefile Integration Log Table
-- Tracks shapefile processing and coordinate transformations
CREATE TABLE shapefile_integration_log (
    log_id VARCHAR(255) PRIMARY KEY,
    shapefile_name VARCHAR(500) NOT NULL,
    source_path VARCHAR(1000),
    feature_type VARCHAR(50) NOT NULL,
    feature_count INTEGER,
    source_crs VARCHAR(50),
    target_crs VARCHAR(50),
    ogr2ogr_command VARCHAR(2000),
    transformed_path VARCHAR(1000),
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    transformation_status VARCHAR(50),
    target_table VARCHAR(255),
    load_timestamp TIMESTAMP_NTZ,
    processing_duration_seconds INTEGER,
    error_message VARCHAR(2000)
);

-- Spatial Join Results Table
-- Documents spatial join operations between GRIB2 grid cells and shapefile boundaries
CREATE TABLE spatial_join_results (
    join_id VARCHAR(255) PRIMARY KEY,
    grib_file VARCHAR(500),
    shapefile_name VARCHAR(500),
    join_type VARCHAR(50),  -- 'Point-in-Polygon', 'Raster-to-Vector', 'Clip'
    gdal_command VARCHAR(2000),
    features_matched INTEGER,
    features_total INTEGER,
    match_percentage NUMERIC(5, 2),
    output_file VARCHAR(1000),
    join_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    forecast_id VARCHAR(255),
    boundary_id VARCHAR(255)
);

-- CRS Transformation Parameters Table
-- Documents coordinate reference system transformations and parameters
CREATE TABLE crs_transformation_parameters (
    transformation_id VARCHAR(255) PRIMARY KEY,
    source_crs VARCHAR(50) NOT NULL,
    target_crs VARCHAR(50) NOT NULL,
    source_crs_name VARCHAR(255),
    target_crs_name VARCHAR(255),
    transformation_method VARCHAR(50),  -- 'GDAL', 'PROJ', 'Custom'
    central_meridian NUMERIC(10, 6),
    false_easting NUMERIC(12, 2),
    false_northing NUMERIC(12, 2),
    scale_factor NUMERIC(10, 8),
    latitude_of_origin NUMERIC(10, 6),
    units VARCHAR(50),  -- 'degrees', 'meters', 'feet'
    accuracy_meters NUMERIC(10, 2),
    usage_count INTEGER DEFAULT 0
);

-- Data Quality Metrics Table
-- Tracks data quality metrics for weather products
CREATE TABLE data_quality_metrics (
    metric_id VARCHAR(255) PRIMARY KEY,
    metric_date DATE NOT NULL,
    data_source VARCHAR(50) NOT NULL,  -- 'GRIB2', 'Shapefile', 'API'
    files_processed INTEGER DEFAULT 0,
    files_successful INTEGER DEFAULT 0,
    files_failed INTEGER DEFAULT 0,
    success_rate NUMERIC(5, 2),
    total_records INTEGER DEFAULT 0,
    records_with_errors INTEGER DEFAULT 0,
    error_rate NUMERIC(5, 2),
    spatial_coverage_km2 NUMERIC(15, 2),
    temporal_coverage_hours INTEGER,
    data_freshness_minutes INTEGER,
    calculation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Load Status Table
-- Tracks data loading operations to Databricks
CREATE TABLE load_status (
    load_id VARCHAR(255) PRIMARY KEY,
    source_file VARCHAR(1000),
    target_table VARCHAR(255) NOT NULL,
    load_start_time TIMESTAMP_NTZ NOT NULL,
    load_end_time TIMESTAMP_NTZ,
    load_duration_seconds INTEGER,
    records_loaded INTEGER DEFAULT 0,
    file_size_mb NUMERIC(10, 2),
    load_rate_mb_per_sec NUMERIC(10, 2),
    load_status VARCHAR(50),  -- 'Success', 'Failed', 'Partial'
    error_message VARCHAR(2000),
    warehouse VARCHAR(255),
    data_source_type VARCHAR(50)
);

-- Weather Forecast Aggregations Table
-- Pre-aggregated forecast data for performance
CREATE TABLE weather_forecast_aggregations (
    aggregation_id VARCHAR(255) PRIMARY KEY,
    parameter_name VARCHAR(100) NOT NULL,
    forecast_time TIMESTAMP_NTZ NOT NULL,
    boundary_id VARCHAR(255),
    feature_type VARCHAR(50),
    feature_name VARCHAR(255),
    min_value NUMERIC(10, 2),
    max_value NUMERIC(10, 2),
    avg_value NUMERIC(10, 2),
    median_value NUMERIC(10, 2),
    std_dev_value NUMERIC(10, 2),
    grid_cells_count INTEGER,
    aggregation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Weather Station Metadata Table
-- Metadata about weather observation stations
CREATE TABLE weather_stations (
    station_id VARCHAR(50) PRIMARY KEY,
    station_name VARCHAR(255),
    station_latitude NUMERIC(10, 7) NOT NULL,
    station_longitude NUMERIC(10, 7) NOT NULL,
    station_geom GEOGRAPHY,
    elevation_meters NUMERIC(8, 2),
    state_code VARCHAR(2),
    county_name VARCHAR(100),
    cwa_code VARCHAR(10),
    station_type VARCHAR(50),
    active_status BOOLEAN DEFAULT TRUE,
    first_observation_date DATE,
    last_observation_date DATE,
    update_frequency_minutes INTEGER
);

-- Create indexes for performance
CREATE INDEX idx_grib2_forecasts_parameter_time ON grib2_forecasts(parameter_name, forecast_time);
CREATE INDEX idx_grib2_forecasts_geom ON grib2_forecasts USING GIST(grid_cell_geom);
CREATE INDEX idx_shapefile_boundaries_type ON shapefile_boundaries(feature_type);
CREATE INDEX idx_shapefile_boundaries_geom ON shapefile_boundaries USING GIST(boundary_geom);
CREATE INDEX idx_weather_observations_station_time ON weather_observations(station_id, observation_time);
CREATE INDEX idx_weather_observations_geom ON weather_observations USING GIST(station_geom);
CREATE INDEX idx_spatial_join_forecast_boundary ON spatial_join_results(forecast_id, boundary_id);
CREATE INDEX idx_forecast_aggregations_time ON weather_forecast_aggregations(forecast_time, parameter_name);


--

-- Extended Schema for AWS Open Data, NWS API, and GeoPlatform.gov Integration
-- Compatible with PostgreSQL
-- Production schema extensions for AWS Open Data, NWS API, and GeoPlatform.gov integration

-- AWS Data Source Log Table
-- Tracks data ingestion from AWS Open Data Registry
CREATE TABLE IF NOT EXISTS aws_data_source_log (
    source_id VARCHAR(255) PRIMARY KEY,
    source_name VARCHAR(500) NOT NULL,
    source_type VARCHAR(100) NOT NULL,  -- 'noaa_gfs', 'noaa_hrrr', 'noaa_nexrad', etc.
    bucket_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    format VARCHAR(50),  -- 'grib2', 'netcdf', 'binary', etc.
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    status VARCHAR(50) DEFAULT 'Success',  -- 'Success', 'Failed', 'Pending'
    metadata VARIANT,  -- JSON metadata JSONB (PostgreSQL) - Use OBJECT for cross-database compatibility
    file_size_bytes BIGINT,
    forecast_date DATE,
    forecast_cycle VARCHAR(2),  -- '00', '06', '12', '18'
    forecast_hour INTEGER
);

-- NWS API Observation Log Table
-- Tracks observations ingested from NWS API
CREATE TABLE IF NOT EXISTS nws_api_observation_log (
    log_id VARCHAR(255) PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL,
    observation_time TIMESTAMP_NTZ NOT NULL,
    api_endpoint VARCHAR(500),
    response_status INTEGER,
    data_freshness_minutes INTEGER,
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    status VARCHAR(50) DEFAULT 'Success',
    error_message VARCHAR(2000)
);

-- GeoPlatform Dataset Log Table
-- Tracks geospatial datasets discovered from geoplatform.gov
CREATE TABLE IF NOT EXISTS geoplatform_dataset_log (
    dataset_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500),
    description VARCHAR(2000),
    url VARCHAR(1000),
    search_term VARCHAR(100),
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    status VARCHAR(50) DEFAULT 'Discovered',  -- 'Discovered', 'Ingested', 'Failed'
    dataset_type VARCHAR(100),  -- 'boundary', 'elevation', 'imagery', etc.
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6)
);

-- Enhanced GRIB2 Forecasts Table
-- Extended to support multiple data sources
ALTER TABLE grib2_forecasts ADD COLUMN IF NOT EXISTS data_source VARCHAR(50) DEFAULT 'NDFD';
ALTER TABLE grib2_forecasts ADD COLUMN IF NOT EXISTS model_name VARCHAR(100);  -- 'GFS', 'HRRR', 'RAP', etc.
ALTER TABLE grib2_forecasts ADD COLUMN IF NOT EXISTS aws_bucket VARCHAR(255);
ALTER TABLE grib2_forecasts ADD COLUMN IF NOT EXISTS aws_file_path VARCHAR(1000);
ALTER TABLE grib2_forecasts ADD COLUMN IF NOT EXISTS ensemble_member INTEGER;  -- For ensemble forecasts

-- Enhanced Weather Observations Table
-- Extended to support NWS API data
ALTER TABLE weather_observations ADD COLUMN IF NOT EXISTS api_endpoint VARCHAR(500);
ALTER TABLE weather_observations ADD COLUMN IF NOT EXISTS api_response_status INTEGER;
ALTER TABLE weather_observations ADD COLUMN IF NOT EXISTS observation_value NUMERIC(10, 2);

-- Weather Alerts Table
-- Stores NWS weather alerts and warnings
CREATE TABLE IF NOT EXISTS weather_alerts (
    alert_id VARCHAR(255) PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,  -- 'Tornado Warning', 'Flood Warning', etc.
    severity VARCHAR(50),  -- 'Extreme', 'Severe', 'Moderate', 'Minor', 'Unknown'
    urgency VARCHAR(50),  -- 'Immediate', 'Expected', 'Future', 'Past', 'Unknown'
    certainty VARCHAR(50),  -- 'Observed', 'Likely', 'Possible', 'Unlikely', 'Unknown'
    headline VARCHAR(500),
    description TEXT,
    instruction TEXT,
    effective_time TIMESTAMP_NTZ,
    expires_time TIMESTAMP_NTZ,
    onset_time TIMESTAMP_NTZ,
    ends_time TIMESTAMP_NTZ,
    area_description VARCHAR(1000),
    geocode_type VARCHAR(50),  -- 'FIPS', 'UGC', etc.
    geocode_value VARCHAR(100),
    state_code VARCHAR(2),
    county_code VARCHAR(5),
    cwa_code VARCHAR(10),
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    alert_geometry GEOGRAPHY  -- Polygon geometry for alert area
);

-- Model Forecast Comparison Table
-- Compares forecasts from different models
CREATE TABLE IF NOT EXISTS model_forecast_comparison (
    comparison_id VARCHAR(255) PRIMARY KEY,
    forecast_time TIMESTAMP_NTZ NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    grid_cell_latitude NUMERIC(10, 7) NOT NULL,
    grid_cell_longitude NUMERIC(10, 7) NOT NULL,
    gfs_value NUMERIC(10, 2),
    hrrr_value NUMERIC(10, 2),
    rap_value NUMERIC(10, 2),
    gefs_mean_value NUMERIC(10, 2),
    gefs_stddev_value NUMERIC(10, 2),
    observation_value NUMERIC(10, 2),
    observation_time TIMESTAMP_NTZ,
    gfs_error NUMERIC(10, 2),
    hrrr_error NUMERIC(10, 2),
    rap_error NUMERIC(10, 2),
    best_model VARCHAR(50),  -- Model with smallest error
    comparison_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Data Source Statistics Table
-- Tracks statistics for each data source
CREATE TABLE IF NOT EXISTS data_source_statistics (
    stat_id VARCHAR(255) PRIMARY KEY,
    source_type VARCHAR(100) NOT NULL,  -- 'AWS_GFS', 'NWS_API', 'GEOPLATFORM'
    source_name VARCHAR(500),
    stat_date DATE NOT NULL,
    files_ingested INTEGER DEFAULT 0,
    records_processed INTEGER DEFAULT 0,
    data_volume_mb NUMERIC(15, 2),
    ingestion_duration_seconds INTEGER,
    success_rate NUMERIC(5, 2),
    avg_latency_seconds NUMERIC(10, 2),
    error_count INTEGER DEFAULT 0,
    calculation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_aws_data_source_log_type_date
    ON aws_data_source_log(source_type, forecast_date, forecast_cycle);
CREATE INDEX IF NOT EXISTS idx_weather_alerts_event_time
    ON weather_alerts(event_type, effective_time);
CREATE INDEX IF NOT EXISTS idx_weather_alerts_geom
    ON weather_alerts USING GIST(alert_geometry);
CREATE INDEX IF NOT EXISTS idx_model_forecast_comparison_time
    ON model_forecast_comparison(forecast_time, parameter_name);
CREATE INDEX IF NOT EXISTS idx_data_source_statistics_date
    ON data_source_statistics(source_type, stat_date);


--

-- Insurance Rate Modeling Schema Extensions
-- Compatible with PostgreSQL
-- Production schema extensions for insurance rate modeling using 7-14 day forecasts
-- Purpose: Extend db-6 for insurance rate table determination using 7-14 day forecasts

-- Insurance Policy Areas Table
-- Maps geographic boundaries to insurance policy coverage areas
CREATE TABLE IF NOT EXISTS insurance_policy_areas (
    policy_area_id VARCHAR(255) PRIMARY KEY,
    boundary_id VARCHAR(255) NOT NULL,  -- References shapefile_boundaries
    policy_type VARCHAR(50) NOT NULL,  -- 'Property', 'Crop', 'Auto', 'Marine', 'General Liability'
    coverage_type VARCHAR(100),  -- 'Homeowners', 'Commercial Property', 'Crop Insurance', etc.
    policy_area_name VARCHAR(255),
    state_code VARCHAR(2),
    county_code VARCHAR(5),
    cwa_code VARCHAR(10),
    risk_zone VARCHAR(50),  -- 'Low', 'Moderate', 'High', 'Very High'
    base_rate_factor NUMERIC(5, 3) DEFAULT 1.000,  -- Multiplier for base rates
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insurance Risk Factors Table
-- Stores calculated risk factors based on weather forecasts
CREATE TABLE IF NOT EXISTS insurance_risk_factors (
    risk_factor_id VARCHAR(255) PRIMARY KEY,
    policy_area_id VARCHAR(255) NOT NULL,  -- References insurance_policy_areas
    forecast_period_start DATE NOT NULL,  -- Start of forecast period (Dec 3, 2025)
    forecast_period_end DATE NOT NULL,  -- End of forecast period (Dec 17, 2025)
    forecast_day INTEGER NOT NULL,  -- Days ahead: 7, 8, 9, ..., 14
    forecast_date DATE NOT NULL,  -- Date when forecast was made
    parameter_name VARCHAR(100) NOT NULL,  -- 'Temperature', 'Precipitation', 'WindSpeed', etc.
    -- Risk metrics
    extreme_event_probability NUMERIC(5, 4),  -- Probability of extreme event (0-1)
    cumulative_precipitation_risk NUMERIC(10, 2),  -- Total precipitation risk score
    temperature_extreme_risk NUMERIC(10, 2),  -- Temperature extreme risk score
    wind_damage_risk NUMERIC(10, 2),  -- Wind damage risk score
    freeze_risk NUMERIC(10, 2),  -- Freeze/frost risk score
    flood_risk NUMERIC(10, 2),  -- Flood risk score
    -- Forecast statistics
    min_forecast_value NUMERIC(10, 2),
    max_forecast_value NUMERIC(10, 2),
    avg_forecast_value NUMERIC(10, 2),
    median_forecast_value NUMERIC(10, 2),
    stddev_forecast_value NUMERIC(10, 2),
    percentile_90_value NUMERIC(10, 2),
    percentile_95_value NUMERIC(10, 2),
    percentile_99_value NUMERIC(10, 2),
    -- Risk scores (0-100 scale)
    overall_risk_score NUMERIC(5, 2),
    risk_category VARCHAR(50),  -- 'Low', 'Moderate', 'High', 'Very High', 'Extreme'
    -- Metadata
    calculation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    forecast_model VARCHAR(100),  -- 'GFS', 'HRRR', 'Ensemble', etc.
    data_quality_score NUMERIC(5, 2)
);

-- Insurance Rate Tables Table
-- Stores calculated rate tables based on forecast risk factors
CREATE TABLE IF NOT EXISTS insurance_rate_tables (
    rate_table_id VARCHAR(255) PRIMARY KEY,
    policy_area_id VARCHAR(255) NOT NULL,  -- References insurance_policy_areas
    policy_type VARCHAR(50) NOT NULL,
    coverage_type VARCHAR(100),
    forecast_period_start DATE NOT NULL,  -- Dec 3, 2025
    forecast_period_end DATE NOT NULL,  -- Dec 17, 2025
    forecast_day INTEGER NOT NULL,  -- 7-14 days ahead
    forecast_date DATE NOT NULL,  -- Date when forecast was made
    -- Base rates
    base_rate NUMERIC(10, 2),
    base_rate_currency VARCHAR(3) DEFAULT 'USD',
    -- Risk-adjusted rates
    risk_adjusted_rate NUMERIC(10, 2),
    risk_multiplier NUMERIC(5, 3),  -- Multiplier applied to base rate
    -- Rate components
    base_component NUMERIC(10, 2),
    precipitation_risk_component NUMERIC(10, 2),
    temperature_risk_component NUMERIC(10, 2),
    wind_risk_component NUMERIC(10, 2),
    freeze_risk_component NUMERIC(10, 2),
    flood_risk_component NUMERIC(10, 2),
    extreme_event_component NUMERIC(10, 2),
    -- Rate tiers
    rate_tier VARCHAR(50),  -- 'Standard', 'Preferred', 'Substandard', 'High Risk'
    rate_category VARCHAR(50),  -- 'Low', 'Moderate', 'High', 'Very High'
    overall_risk_score NUMERIC(5, 2),  -- Overall risk score (0-100)
    -- Metadata
    calculation_method VARCHAR(100),  -- 'Forecast-Based', 'Historical', 'Hybrid'
    confidence_level NUMERIC(5, 2),  -- Confidence in forecast (0-100)
    effective_date DATE NOT NULL,
    expiration_date DATE,
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insurance Claims History Table
-- Historical claims data for validation and comparison
CREATE TABLE IF NOT EXISTS insurance_claims_history (
    claim_id VARCHAR(255) PRIMARY KEY,
    policy_area_id VARCHAR(255),  -- References insurance_policy_areas
    claim_date DATE NOT NULL,
    loss_date DATE NOT NULL,  -- Date when loss occurred
    policy_type VARCHAR(50),
    coverage_type VARCHAR(100),
    claim_type VARCHAR(100),  -- 'Weather', 'Fire', 'Flood', 'Wind', 'Freeze', etc.
    loss_amount NUMERIC(12, 2),
    claim_status VARCHAR(50),  -- 'Open', 'Closed', 'Denied', 'Pending'
    weather_event_type VARCHAR(100),  -- 'Hurricane', 'Tornado', 'Flood', 'Freeze', etc.
    weather_event_date DATE,
    -- Weather conditions at time of loss
    temperature_at_loss NUMERIC(6, 2),
    precipitation_at_loss NUMERIC(8, 2),
    wind_speed_at_loss NUMERIC(6, 2),
    -- Forecast accuracy (if forecast was available)
    forecast_available BOOLEAN DEFAULT FALSE,
    forecast_day INTEGER,  -- Days ahead forecast was made
    forecast_error NUMERIC(10, 2),  -- Forecast vs actual error
    -- Metadata
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Forecast-to-Rate Mapping Table
-- Maps specific forecasts to rate calculations
CREATE TABLE IF NOT EXISTS forecast_rate_mapping (
    mapping_id VARCHAR(255) PRIMARY KEY,
    forecast_id VARCHAR(255) NOT NULL,  -- References grib2_forecasts
    rate_table_id VARCHAR(255),  -- References insurance_rate_tables
    risk_factor_id VARCHAR(255),  -- References insurance_risk_factors
    policy_area_id VARCHAR(255) NOT NULL,  -- References insurance_policy_areas
    forecast_date DATE NOT NULL,
    forecast_day INTEGER NOT NULL,  -- 7-14 days ahead
    forecast_time TIMESTAMP_NTZ NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_value NUMERIC(10, 2),
    risk_contribution NUMERIC(10, 4),  -- Contribution to overall risk score
    rate_impact NUMERIC(10, 4),  -- Impact on rate calculation
    mapping_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Rate Table Comparison Table
-- Compares rates across different forecast days (7-14 days)
CREATE TABLE IF NOT EXISTS rate_table_comparison (
    comparison_id VARCHAR(255) PRIMARY KEY,
    policy_area_id VARCHAR(255) NOT NULL,
    policy_type VARCHAR(50) NOT NULL,
    coverage_type VARCHAR(100),  -- 'Homeowners', 'Commercial Property', 'Crop Insurance', etc.
    forecast_period_start DATE NOT NULL,  -- Dec 3, 2025
    forecast_period_end DATE NOT NULL,  -- Dec 17, 2025
    forecast_date DATE NOT NULL,  -- Date when forecast was made
    -- Rates by forecast day
    rate_day_7 NUMERIC(10, 2),
    rate_day_8 NUMERIC(10, 2),
    rate_day_9 NUMERIC(10, 2),
    rate_day_10 NUMERIC(10, 2),
    rate_day_11 NUMERIC(10, 2),
    rate_day_12 NUMERIC(10, 2),
    rate_day_13 NUMERIC(10, 2),
    rate_day_14 NUMERIC(10, 2),
    -- Statistics
    min_rate NUMERIC(10, 2),
    max_rate NUMERIC(10, 2),
    avg_rate NUMERIC(10, 2),
    median_rate NUMERIC(10, 2),
    rate_volatility NUMERIC(10, 4),  -- Standard deviation of rates
    rate_trend VARCHAR(50),  -- 'Increasing', 'Decreasing', 'Stable'
    -- Recommended rate
    recommended_rate NUMERIC(10, 2),
    recommended_forecast_day INTEGER,  -- Which forecast day to use
    confidence_score NUMERIC(5, 2),
    comparison_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_insurance_policy_areas_boundary
    ON insurance_policy_areas(boundary_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policy_areas_type_active
    ON insurance_policy_areas(policy_type, is_active);
CREATE INDEX IF NOT EXISTS idx_insurance_risk_factors_policy_period
    ON insurance_risk_factors(policy_area_id, forecast_period_start, forecast_period_end);
CREATE INDEX IF NOT EXISTS idx_insurance_risk_factors_day_date
    ON insurance_risk_factors(forecast_day, forecast_date);
CREATE INDEX IF NOT EXISTS idx_insurance_rate_tables_policy_period
    ON insurance_rate_tables(policy_area_id, forecast_period_start, forecast_period_end);
CREATE INDEX IF NOT EXISTS idx_insurance_rate_tables_day_date
    ON insurance_rate_tables(forecast_day, forecast_date);
CREATE INDEX IF NOT EXISTS idx_insurance_claims_history_area_date
    ON insurance_claims_history(policy_area_id, loss_date);
CREATE INDEX IF NOT EXISTS idx_insurance_claims_history_type_date
    ON insurance_claims_history(claim_type, loss_date);
CREATE INDEX IF NOT EXISTS idx_forecast_rate_mapping_forecast
    ON forecast_rate_mapping(forecast_id);
CREATE INDEX IF NOT EXISTS idx_forecast_rate_mapping_rate_table
    ON forecast_rate_mapping(rate_table_id);
CREATE INDEX IF NOT EXISTS idx_rate_table_comparison_policy_period
    ON rate_table_comparison(policy_area_id, forecast_period_start, forecast_period_end);


--

-- NEXRAD Radar and Satellite Imagery Schema Extensions
-- Compatible with PostgreSQL
-- Production schema extensions for NEXRAD Level II radar and satellite imagery data
-- Purpose: Support NEXRAD Level II radar data and decompressed satellite imagery transformations across entire United States

-- NEXRAD Radar Sites Table
-- Metadata for NEXRAD radar sites across the United States
CREATE TABLE IF NOT EXISTS nexrad_radar_sites (
    site_id VARCHAR(4) PRIMARY KEY,  -- 4-letter site identifier (e.g., 'KTLX')
    site_name VARCHAR(255) NOT NULL,
    site_latitude NUMERIC(10, 7) NOT NULL,
    site_longitude NUMERIC(10, 7) NOT NULL,
    site_geom GEOGRAPHY,  -- Point geometry
    elevation_meters NUMERIC(8, 2),
    state_code VARCHAR(2),
    county_name VARCHAR(100),
    cwa_code VARCHAR(10),  -- County Warning Area
    radar_type VARCHAR(50) DEFAULT 'WSR-88D',  -- Weather Surveillance Radar
    operational_status VARCHAR(50) DEFAULT 'Operational',  -- 'Operational', 'Maintenance', 'Offline'
    coverage_radius_km NUMERIC(8, 2) DEFAULT 230.0,  -- Standard NEXRAD coverage radius
    first_operational_date DATE,
    last_maintenance_date DATE,
    update_frequency_minutes INTEGER DEFAULT 5,  -- Typical NEXRAD update frequency
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- NEXRAD Level II Data Table
-- Stores decompressed NEXRAD Level II radar data
CREATE TABLE IF NOT EXISTS nexrad_level2_data (
    radar_data_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,  -- References nexrad_radar_sites
    scan_time TIMESTAMP_NTZ NOT NULL,
    volume_scan_number INTEGER,
    elevation_angle NUMERIC(5, 2),  -- Elevation angle in degrees
    azimuth_angle NUMERIC(6, 2),  -- Azimuth angle in degrees
    range_gate INTEGER,  -- Range gate number
    range_km NUMERIC(8, 2),  -- Distance from radar in kilometers
    -- Reflectivity data
    reflectivity_dbz NUMERIC(6, 2),  -- Reflectivity in dBZ
    reflectivity_geom GEOGRAPHY,  -- Point geometry for reflectivity location
    -- Velocity data
    radial_velocity_ms NUMERIC(6, 2),  -- Radial velocity in m/s
    velocity_geom GEOGRAPHY,  -- Point geometry for velocity location
    -- Spectrum width
    spectrum_width_ms NUMERIC(6, 2),  -- Spectrum width in m/s
    -- Data quality
    data_quality_flag INTEGER,  -- Quality flags
    -- Source file information
    source_file VARCHAR(1000),  -- Original NEXRAD file path
    aws_bucket VARCHAR(255),  -- AWS S3 bucket
    aws_key VARCHAR(1000),  -- AWS S3 key
    file_format VARCHAR(50) DEFAULT 'Level2',  -- 'Level2', 'Level3'
    compression_type VARCHAR(50),  -- 'bzip2', 'gzip', 'none'
    decompression_status VARCHAR(50) DEFAULT 'Success',  -- 'Success', 'Failed', 'Pending'
    -- Metadata
    data_type VARCHAR(50),  -- 'Reflectivity', 'Velocity', 'SpectrumWidth', 'DifferentialReflectivity'
    sweep_mode VARCHAR(50),  -- 'PPI' (Plan Position Indicator), 'RHI' (Range Height Indicator)
    pulse_repetition_frequency INTEGER,  -- PRF in Hz
    nyquist_velocity_ms NUMERIC(6, 2),  -- Nyquist velocity in m/s
    -- Spatial extent
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    -- Processing metadata
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    processing_duration_seconds INTEGER,
    records_processed INTEGER
);

-- NEXRAD Reflectivity Grid Table
-- Gridded reflectivity data for easier spatial analysis
CREATE TABLE IF NOT EXISTS nexrad_reflectivity_grid (
    grid_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,  -- References nexrad_radar_sites
    scan_time TIMESTAMP_NTZ NOT NULL,
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(6, 2) DEFAULT 1.0,  -- Grid resolution in km
    -- Reflectivity values
    max_reflectivity_dbz NUMERIC(6, 2),  -- Maximum reflectivity in grid cell
    mean_reflectivity_dbz NUMERIC(6, 2),  -- Mean reflectivity in grid cell
    min_reflectivity_dbz NUMERIC(6, 2),  -- Minimum reflectivity in grid cell
    reflectivity_count INTEGER,  -- Number of observations in grid cell
    -- Composite reflectivity (highest reflectivity at any elevation)
    composite_reflectivity_dbz NUMERIC(6, 2),
    -- Height of maximum reflectivity
    height_of_max_reflectivity_m NUMERIC(8, 2),
    -- Precipitation estimates
    precipitation_rate_mmh NUMERIC(8, 2),  -- Precipitation rate in mm/h
    accumulated_precipitation_mm NUMERIC(8, 2),  -- Accumulated precipitation in mm
    -- Storm attributes
    storm_cell_id VARCHAR(255),  -- Identifier for storm cell tracking
    storm_severity VARCHAR(50),  -- 'Weak', 'Moderate', 'Strong', 'Severe', 'Extreme'
    -- Processing metadata
    grid_generation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    grid_method VARCHAR(100)  -- 'NearestNeighbor', 'Bilinear', 'Cressman', etc.
);

-- NEXRAD Velocity Grid Table
-- Gridded velocity data for wind analysis
CREATE TABLE IF NOT EXISTS nexrad_velocity_grid (
    grid_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,  -- References nexrad_radar_sites
    scan_time TIMESTAMP_NTZ NOT NULL,
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(6, 2) DEFAULT 1.0,
    -- Velocity values
    radial_velocity_ms NUMERIC(6, 2),  -- Radial velocity in m/s
    velocity_azimuth NUMERIC(6, 2),  -- Azimuth angle in degrees
    -- Wind components (derived)
    u_wind_component_ms NUMERIC(6, 2),  -- East-west wind component
    v_wind_component_ms NUMERIC(6, 2),  -- North-south wind component
    wind_speed_ms NUMERIC(6, 2),  -- Wind speed in m/s
    wind_direction_deg NUMERIC(6, 2),  -- Wind direction in degrees
    -- Spectrum width
    spectrum_width_ms NUMERIC(6, 2),
    -- Velocity quality
    velocity_quality_flag INTEGER,
    -- Processing metadata
    grid_generation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- NEXRAD Storm Cell Tracking Table
-- Tracks storm cells across multiple scans
CREATE TABLE IF NOT EXISTS nexrad_storm_cells (
    storm_cell_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,  -- References nexrad_radar_sites
    first_detection_time TIMESTAMP_NTZ NOT NULL,
    last_detection_time TIMESTAMP_NTZ,
    storm_center_latitude NUMERIC(10, 7),
    storm_center_longitude NUMERIC(10, 7),
    storm_center_geom GEOGRAPHY,  -- Point geometry
    storm_polygon_geom GEOGRAPHY,  -- Polygon geometry for storm extent
    -- Storm characteristics
    max_reflectivity_dbz NUMERIC(6, 2),
    max_velocity_ms NUMERIC(6, 2),
    storm_area_km2 NUMERIC(10, 2),
    storm_diameter_km NUMERIC(8, 2),
    storm_perimeter_km NUMERIC(8, 2),
    -- Movement
    storm_speed_ms NUMERIC(6, 2),  -- Storm movement speed
    storm_direction_deg NUMERIC(6, 2),  -- Storm movement direction
    -- Severity classification
    storm_severity VARCHAR(50),  -- 'Weak', 'Moderate', 'Strong', 'Severe', 'Extreme'
    storm_type VARCHAR(50),  -- 'Thunderstorm', 'Squall Line', 'Supercell', 'Mesocyclone', etc.
    -- Tracking metadata
    track_duration_minutes INTEGER,
    scan_count INTEGER,  -- Number of scans where storm was detected
    tracking_status VARCHAR(50) DEFAULT 'Active',  -- 'Active', 'Dissipated', 'Merged'
    -- Processing metadata
    tracking_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Satellite Imagery Sources Table
-- Metadata for satellite imagery sources (GOES, etc.)
CREATE TABLE IF NOT EXISTS satellite_imagery_sources (
    source_id VARCHAR(255) PRIMARY KEY,
    satellite_name VARCHAR(100) NOT NULL,  -- 'GOES-16', 'GOES-17', 'GOES-18', etc.
    satellite_type VARCHAR(50) DEFAULT 'GOES',  -- 'GOES', 'POES', 'MODIS', etc.
    sensor_name VARCHAR(100),  -- 'ABI' (Advanced Baseline Imager), etc.
    orbital_position VARCHAR(50),  -- 'GOES-East', 'GOES-West', etc.
    -- Spatial coverage
    coverage_area VARCHAR(100) DEFAULT 'CONUS',  -- 'CONUS', 'Full Disk', 'Mesoscale', etc.
    spatial_resolution_km NUMERIC(8, 2),  -- Spatial resolution in kilometers
    scan_frequency_minutes INTEGER,  -- Scan frequency in minutes
    temporal_resolution_minutes INTEGER,
    -- Operational status
    operational_status VARCHAR(50) DEFAULT 'Operational',
    first_operational_date DATE,
    last_update_date DATE,
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Satellite Imagery Products Table
-- Decompressed satellite imagery products
CREATE TABLE IF NOT EXISTS satellite_imagery_products (
    product_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,  -- References satellite_imagery_sources
    product_name VARCHAR(255) NOT NULL,  -- 'ABI L2 Cloud Top Height', 'ABI L2 Cloud Top Temperature', etc.
    product_type VARCHAR(100),  -- 'Cloud', 'Fire', 'Precipitation', 'Temperature', 'Moisture', etc.
    band_number INTEGER,  -- GOES ABI band number (1-16)
    band_name VARCHAR(100),  -- 'Visible', 'Near-Infrared', 'Infrared', etc.
    wavelength_um NUMERIC(8, 4),  -- Wavelength in micrometers
    scan_start_time TIMESTAMP_NTZ NOT NULL,
    scan_end_time TIMESTAMP_NTZ,
    scan_duration_seconds INTEGER,
    -- Spatial information
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(8, 2),  -- Grid resolution in kilometers
    -- Pixel values
    pixel_value NUMERIC(10, 4),  -- Raw pixel value
    calibrated_value NUMERIC(10, 4),  -- Calibrated physical value
    brightness_temperature_k NUMERIC(8, 2),  -- Brightness temperature in Kelvin (for IR bands)
    reflectance_percent NUMERIC(6, 2),  -- Reflectance percentage (for visible bands)
    -- Derived products
    cloud_top_height_m NUMERIC(8, 2),  -- Cloud top height in meters
    cloud_top_temperature_k NUMERIC(8, 2),  -- Cloud top temperature in Kelvin
    cloud_phase VARCHAR(50),  -- 'Liquid', 'Ice', 'Mixed', 'Unknown'
    cloud_optical_depth NUMERIC(8, 4),  -- Cloud optical depth
    -- Fire detection
    fire_detection_confidence NUMERIC(5, 2),  -- Fire detection confidence (0-100)
    fire_temperature_k NUMERIC(8, 2),  -- Fire temperature in Kelvin
    fire_power_mw NUMERIC(12, 2),  -- Fire radiative power in megawatts
    -- Precipitation
    precipitation_rate_mmh NUMERIC(8, 2),  -- Precipitation rate in mm/h
    -- Source file information
    source_file VARCHAR(1000),  -- Original satellite file path
    aws_bucket VARCHAR(255),  -- AWS S3 bucket
    aws_key VARCHAR(1000),  -- AWS S3 key
    file_format VARCHAR(50) DEFAULT 'NetCDF',  -- 'NetCDF', 'HDF5', 'GeoTIFF', etc.
    compression_type VARCHAR(50),  -- Compression type
    decompression_status VARCHAR(50) DEFAULT 'Success',
    -- Spatial extent
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    -- Processing metadata
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    processing_duration_seconds INTEGER,
    records_processed INTEGER
);

-- Satellite Imagery Grid Aggregations Table
-- Aggregated satellite imagery data for spatial analysis
CREATE TABLE IF NOT EXISTS satellite_imagery_grid (
    grid_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,  -- References satellite_imagery_sources
    product_type VARCHAR(100) NOT NULL,
    scan_time TIMESTAMP_NTZ NOT NULL,
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(8, 2),  -- Grid resolution
    -- Aggregated values
    min_value NUMERIC(10, 4),
    max_value NUMERIC(10, 4),
    mean_value NUMERIC(10, 4),
    median_value NUMERIC(10, 4),
    stddev_value NUMERIC(10, 4),
    pixel_count INTEGER,
    -- Cloud properties
    cloud_fraction NUMERIC(5, 2),  -- Cloud fraction (0-100%)
    cloud_top_height_m NUMERIC(8, 2),
    cloud_top_temperature_k NUMERIC(8, 2),
    -- Fire properties
    fire_count INTEGER,
    total_fire_power_mw NUMERIC(12, 2),
    -- Precipitation properties
    precipitation_rate_mmh NUMERIC(8, 2),
    -- Processing metadata
    aggregation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    aggregation_method VARCHAR(100)  -- 'Mean', 'Max', 'Min', 'Median', etc.
);

-- NEXRAD Transformation Log Table
-- Tracks NEXRAD data transformation operations
CREATE TABLE IF NOT EXISTS nexrad_transformation_log (
    transformation_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,
    source_file VARCHAR(1000) NOT NULL,
    transformation_type VARCHAR(100) NOT NULL,  -- 'Decompression', 'Gridding', 'StormTracking', 'Composite'
    transformation_start_time TIMESTAMP_NTZ NOT NULL,
    transformation_end_time TIMESTAMP_NTZ,
    transformation_duration_seconds INTEGER,
    -- Input parameters
    input_format VARCHAR(50),
    input_size_bytes BIGINT,
    input_records INTEGER,
    -- Output parameters
    output_format VARCHAR(50),
    output_size_bytes BIGINT,
    output_records INTEGER,
    -- Transformation status
    transformation_status VARCHAR(50) DEFAULT 'Success',  -- 'Success', 'Failed', 'Partial'
    error_message VARCHAR(2000),
    -- Processing details
    processing_method VARCHAR(100),  -- 'PyART', 'wradlib', 'Custom', etc.
    processing_parameters VARCHAR(2000),  -- JSON parameters
    -- Spatial extent
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    -- Metadata
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Satellite Imagery Transformation Log Table
-- Tracks satellite imagery transformation operations
CREATE TABLE IF NOT EXISTS satellite_transformation_log (
    transformation_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,
    source_file VARCHAR(1000) NOT NULL,
    transformation_type VARCHAR(100) NOT NULL,  -- 'Decompression', 'Reprojection', 'Gridding', 'ProductGeneration'
    transformation_start_time TIMESTAMP_NTZ NOT NULL,
    transformation_end_time TIMESTAMP_NTZ,
    transformation_duration_seconds INTEGER,
    -- Input parameters
    input_format VARCHAR(50),
    input_size_bytes BIGINT,
    input_bands INTEGER,
    input_dimensions VARCHAR(100),  -- 'width x height'
    -- Output parameters
    output_format VARCHAR(50),
    output_size_bytes BIGINT,
    output_records INTEGER,
    -- Transformation status
    transformation_status VARCHAR(50) DEFAULT 'Success',
    error_message VARCHAR(2000),
    -- Processing details
    processing_method VARCHAR(100),  -- 'xarray', 'rasterio', 'GDAL', 'Custom', etc.
    processing_parameters VARCHAR(2000),  -- JSON parameters
    crs_transformation VARCHAR(100),  -- CRS transformation applied
    -- Spatial extent
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    -- Metadata
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- US-Wide Composite Products Table
-- Composite products combining NEXRAD and satellite data across entire US
CREATE TABLE IF NOT EXISTS us_wide_composite_products (
    composite_id VARCHAR(255) PRIMARY KEY,
    product_type VARCHAR(100) NOT NULL,  -- 'Precipitation', 'Cloud', 'Storm', 'Fire', 'Temperature'
    composite_time TIMESTAMP_NTZ NOT NULL,
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(8, 2) DEFAULT 1.0,
    -- NEXRAD contributions
    nexrad_reflectivity_dbz NUMERIC(6, 2),
    nexrad_velocity_ms NUMERIC(6, 2),
    nexrad_precipitation_rate_mmh NUMERIC(8, 2),
    nexrad_contribution_weight NUMERIC(5, 3),  -- Weight of NEXRAD data in composite
    -- Satellite contributions
    satellite_brightness_temperature_k NUMERIC(8, 2),
    satellite_reflectance_percent NUMERIC(6, 2),
    satellite_cloud_top_height_m NUMERIC(8, 2),
    satellite_precipitation_rate_mmh NUMERIC(8, 2),
    satellite_contribution_weight NUMERIC(5, 3),  -- Weight of satellite data in composite
    -- Composite values
    composite_precipitation_rate_mmh NUMERIC(8, 2),
    composite_cloud_fraction NUMERIC(5, 2),
    composite_storm_severity VARCHAR(50),
    -- Data quality
    data_quality_score NUMERIC(5, 2),  -- Overall data quality (0-100)
    coverage_percentage NUMERIC(5, 2),  -- Percentage of expected data coverage
    -- Source information
    nexrad_sites_count INTEGER,  -- Number of NEXRAD sites contributing
    satellite_sources_count INTEGER,  -- Number of satellite sources contributing
    -- Processing metadata
    composite_generation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    composite_method VARCHAR(100)  -- 'WeightedAverage', 'Maximum', 'Minimum', 'Median', etc.
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_nexrad_sites_state_cwa
    ON nexrad_radar_sites(state_code, cwa_code);
CREATE INDEX IF NOT EXISTS idx_nexrad_sites_geom
    ON nexrad_radar_sites USING GIST(site_geom);
CREATE INDEX IF NOT EXISTS idx_nexrad_level2_site_time
    ON nexrad_level2_data(site_id, scan_time);
CREATE INDEX IF NOT EXISTS idx_nexrad_level2_geom
    ON nexrad_level2_data USING GIST(reflectivity_geom);
CREATE INDEX IF NOT EXISTS idx_nexrad_reflectivity_grid_site_time
    ON nexrad_reflectivity_grid(site_id, scan_time);
CREATE INDEX IF NOT EXISTS idx_nexrad_reflectivity_grid_geom
    ON nexrad_reflectivity_grid USING GIST(grid_geom);
CREATE INDEX IF NOT EXISTS idx_nexrad_velocity_grid_site_time
    ON nexrad_velocity_grid(site_id, scan_time);
CREATE INDEX IF NOT EXISTS idx_nexrad_velocity_grid_geom
    ON nexrad_velocity_grid USING GIST(grid_geom);
CREATE INDEX IF NOT EXISTS idx_nexrad_storm_cells_site_time
    ON nexrad_storm_cells(site_id, first_detection_time);
CREATE INDEX IF NOT EXISTS idx_nexrad_storm_cells_geom
    ON nexrad_storm_cells USING GIST(storm_center_geom);
CREATE INDEX IF NOT EXISTS idx_satellite_products_source_time
    ON satellite_imagery_products(source_id, scan_start_time);
CREATE INDEX IF NOT EXISTS idx_satellite_products_geom
    ON satellite_imagery_products USING GIST(grid_geom);
CREATE INDEX IF NOT EXISTS idx_satellite_imagery_grid_source_time
    ON satellite_imagery_grid(source_id, scan_time);
CREATE INDEX IF NOT EXISTS idx_satellite_imagery_grid_geom
    ON satellite_imagery_grid USING GIST(grid_geom);
CREATE INDEX IF NOT EXISTS idx_us_wide_composite_time
    ON us_wide_composite_products(composite_time, product_type);
CREATE INDEX IF NOT EXISTS idx_us_wide_composite_geom
    ON us_wide_composite_products USING GIST(grid_geom);
