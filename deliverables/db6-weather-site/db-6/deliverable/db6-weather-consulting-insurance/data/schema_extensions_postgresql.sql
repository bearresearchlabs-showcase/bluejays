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
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    observation_time TIMESTAMP NOT NULL,
    api_endpoint VARCHAR(500),
    response_status INTEGER,
    data_freshness_minutes INTEGER,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    effective_time TIMESTAMP,
    expires_time TIMESTAMP,
    onset_time TIMESTAMP,
    ends_time TIMESTAMP,
    area_description VARCHAR(1000),
    geocode_type VARCHAR(50),  -- 'FIPS', 'UGC', etc.
    geocode_value VARCHAR(100),
    state_code VARCHAR(2),
    county_code VARCHAR(5),
    cwa_code VARCHAR(10),
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_geometry TEXT  -- Polygon geometry for alert area
);

-- Model Forecast Comparison Table
-- Compares forecasts from different models
CREATE TABLE IF NOT EXISTS model_forecast_comparison (
    comparison_id VARCHAR(255) PRIMARY KEY,
    forecast_time TIMESTAMP NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    grid_cell_latitude NUMERIC(10, 7) NOT NULL,
    grid_cell_longitude NUMERIC(10, 7) NOT NULL,
    gfs_value NUMERIC(10, 2),
    hrrr_value NUMERIC(10, 2),
    rap_value NUMERIC(10, 2),
    gefs_mean_value NUMERIC(10, 2),
    gefs_stddev_value NUMERIC(10, 2),
    observation_value NUMERIC(10, 2),
    observation_time TIMESTAMP,
    gfs_error NUMERIC(10, 2),
    hrrr_error NUMERIC(10, 2),
    rap_error NUMERIC(10, 2),
    best_model VARCHAR(50),  -- Model with smallest error
    comparison_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    calculation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
