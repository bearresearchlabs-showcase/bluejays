-- PostgreSQL-specific schema file
-- Generated from schema.sql
-- Generated: 2026-02-05 19:10:03
-- Database: db-6
-- 
-- This file contains PostgreSQL-specific SQL syntax.
-- Use this file when setting up the database in PostgreSQL.
--

-- Weather Data Pipeline Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for weather data pipeline system

-- GRIB2 Forecasts Table
-- Stores gridded forecast data from NDFD (National Digital Forecast Database)
-- Enable PostGIS extension for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE grib2_forecasts (
    forecast_id VARCHAR(255) PRIMARY KEY,
    parameter_name VARCHAR(100) NOT NULL,
    forecast_time TIMESTAMP NOT NULL,
    grid_cell_latitude NUMERIC(10, 7) NOT NULL,
    grid_cell_longitude NUMERIC(10, 7) NOT NULL,
    grid_cell_geom GEOGRAPHY,  -- Point geometry for grid cell center (PostgreSQL/Snowflake)
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
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
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
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
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
    observation_time TIMESTAMP NOT NULL,
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
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    data_source VARCHAR(50) DEFAULT 'NWS_API'
);

-- GRIB2 Transformation Log Table
-- Tracks GRIB2 file processing and transformation operations
CREATE TABLE grib2_transformation_log (
    log_id VARCHAR(255) PRIMARY KEY,
    file_name VARCHAR(500) NOT NULL,
    source_path VARCHAR(1000),
    parameter_name VARCHAR(100) NOT NULL,
    forecast_time TIMESTAMP,
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
    snowflake_table VARCHAR(255),
    load_timestamp TIMESTAMP,
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
    snowflake_table VARCHAR(255),
    load_timestamp TIMESTAMP,
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
    join_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
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
    calculation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Snowflake Load Status Table
-- Tracks data loading operations to Snowflake
CREATE TABLE snowflake_load_status (
    load_id VARCHAR(255) PRIMARY KEY,
    source_file VARCHAR(1000),
    snowflake_table VARCHAR(255) NOT NULL,
    load_start_time TIMESTAMP NOT NULL,
    load_end_time TIMESTAMP,
    load_duration_seconds INTEGER,
    records_loaded INTEGER DEFAULT 0,
    file_size_mb NUMERIC(10, 2),
    load_rate_mb_per_sec NUMERIC(10, 2),
    load_status VARCHAR(50),  -- 'Success', 'Failed', 'Partial'
    error_message VARCHAR(2000),
    snowflake_warehouse VARCHAR(255),
    data_source_type VARCHAR(50)
);

-- Weather Forecast Aggregations Table
-- Pre-aggregated forecast data for performance
CREATE TABLE weather_forecast_aggregations (
    aggregation_id VARCHAR(255) PRIMARY KEY,
    parameter_name VARCHAR(100) NOT NULL,
    forecast_time TIMESTAMP NOT NULL,
    boundary_id VARCHAR(255),
    feature_type VARCHAR(50),
    feature_name VARCHAR(255),
    min_value NUMERIC(10, 2),
    max_value NUMERIC(10, 2),
    avg_value NUMERIC(10, 2),
    median_value NUMERIC(10, 2),
    std_dev_value NUMERIC(10, 2),
    grid_cells_count INTEGER,
    aggregation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
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
