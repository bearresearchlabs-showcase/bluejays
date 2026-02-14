-- Flood Risk Assessment Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for physical climate risk assessment system
-- Supports flood risk assessments for real estate investment portfolios

-- FEMA Flood Zones Table
-- Stores FEMA National Flood Hazard Layer (NFHL) flood zone designations
CREATE TABLE fema_flood_zones (
    zone_id VARCHAR(255) PRIMARY KEY,
    zone_code VARCHAR(10) NOT NULL,  -- 'A', 'AE', 'AH', 'AO', 'V', 'VE', 'X', 'D', etc.
    zone_description VARCHAR(255),
    base_flood_elevation NUMERIC(10, 2),  -- BFE in feet above sea level
    zone_geom geography,  -- Polygon geometry for flood zone boundary
    community_id VARCHAR(50),
    community_name VARCHAR(255),
    state_code VARCHAR(2),
    county_fips VARCHAR(5),
    effective_date DATE,
    map_panel VARCHAR(50),
    source_file VARCHAR(500),
    source_crs VARCHAR(50) DEFAULT 'EPSG:4326',
    target_crs VARCHAR(50) DEFAULT 'EPSG:4326',
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transformation_status VARCHAR(50)
);

-- Real Estate Properties Table
-- Stores property locations and characteristics for flood risk assessment
CREATE TABLE real_estate_properties (
    property_id VARCHAR(255) PRIMARY KEY,
    property_address VARCHAR(500),
    property_latitude NUMERIC(10, 7) NOT NULL,
    property_longitude NUMERIC(10, 7) NOT NULL,
    property_geom geography,  -- Point geometry for property location
    property_type VARCHAR(100),  -- 'Residential', 'Commercial', 'Industrial', 'Mixed-Use'
    building_value NUMERIC(15, 2),
    land_value NUMERIC(15, 2),
    total_value NUMERIC(15, 2),
    square_footage NUMERIC(12, 2),
    year_built INTEGER,
    number_of_floors INTEGER,
    elevation_feet NUMERIC(10, 2),  -- Ground elevation above sea level
    state_code VARCHAR(2),
    county_fips VARCHAR(5),
    city_name VARCHAR(255),
    zip_code VARCHAR(10),
    portfolio_id VARCHAR(255),
    portfolio_name VARCHAR(255),
    acquisition_date DATE,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NOAA Sea Level Rise Projections Table
-- Stores sea level rise projections and high tide flooding data
CREATE TABLE noaa_sea_level_rise (
    projection_id VARCHAR(255) PRIMARY KEY,
    station_id VARCHAR(50),
    station_name VARCHAR(255),
    station_latitude NUMERIC(10, 7) NOT NULL,
    station_longitude NUMERIC(10, 7) NOT NULL,
    station_geom geography,  -- Point geometry
    projection_year INTEGER NOT NULL,
    scenario VARCHAR(50),  -- 'Low', 'Intermediate-Low', 'Intermediate', 'Intermediate-High', 'High', 'Extreme'
    sea_level_rise_feet NUMERIC(8, 3),  -- Projected sea level rise in feet
    confidence_level VARCHAR(50),  -- 'Low', 'Medium', 'High'
    high_tide_flooding_days INTEGER,  -- Projected annual high tide flooding days
    data_source VARCHAR(100) DEFAULT 'NOAA_CO-OPS',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USGS Streamflow Gauges Table
-- Stores streamflow gauge locations and flood stage information
CREATE TABLE usgs_streamflow_gauges (
    gauge_id VARCHAR(50) PRIMARY KEY,
    gauge_name VARCHAR(255),
    gauge_latitude NUMERIC(10, 7) NOT NULL,
    gauge_longitude NUMERIC(10, 7) NOT NULL,
    gauge_geom geography,  -- Point geometry
    drainage_area_sq_miles NUMERIC(12, 2),
    flood_stage_feet NUMERIC(8, 2),
    moderate_flood_stage_feet NUMERIC(8, 2),
    major_flood_stage_feet NUMERIC(8, 2),
    state_code VARCHAR(2),
    county_name VARCHAR(100),
    river_name VARCHAR(255),
    active_status BOOLEAN DEFAULT TRUE,
    first_observation_date DATE,
    last_observation_date DATE,
    update_frequency_minutes INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USGS Streamflow Observations Table
-- Stores real-time and historical streamflow measurements
CREATE TABLE usgs_streamflow_observations (
    observation_id VARCHAR(255) PRIMARY KEY,
    gauge_id VARCHAR(50) NOT NULL,
    observation_time TIMESTAMP NOT NULL,
    gage_height_feet NUMERIC(8, 2),
    discharge_cfs NUMERIC(12, 2),  -- Discharge in cubic feet per second
    stage_feet NUMERIC(8, 2),
    flood_category VARCHAR(50),  -- 'None', 'Action', 'Minor', 'Moderate', 'Major'
    percentile_rank NUMERIC(5, 2),  -- Percentile relative to historical records
    data_quality_code VARCHAR(10),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NASA Flood Model Outputs Table
-- Stores NASA flood model predictions and inundation extents
CREATE TABLE nasa_flood_models (
    model_id VARCHAR(255) PRIMARY KEY,
    model_name VARCHAR(100),  -- 'GFMS', 'LIS', 'VIIRS', 'MODIS', 'FloodPlanet'
    forecast_time TIMESTAMP NOT NULL,
    grid_cell_latitude NUMERIC(10, 7) NOT NULL,
    grid_cell_longitude NUMERIC(10, 7) NOT NULL,
    grid_cell_geom geography,  -- Point geometry for grid cell center
    inundation_depth_feet NUMERIC(8, 2),
    flood_probability NUMERIC(5, 2),  -- Probability percentage (0-100)
    flood_severity VARCHAR(50),  -- 'Low', 'Moderate', 'High', 'Extreme'
    model_resolution_meters INTEGER,
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    source_file VARCHAR(500),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flood Risk Assessments Table
-- Stores comprehensive flood risk assessments for properties
CREATE TABLE flood_risk_assessments (
    assessment_id VARCHAR(255) PRIMARY KEY,
    property_id VARCHAR(255) NOT NULL,
    assessment_date DATE NOT NULL,
    assessment_type VARCHAR(50),  -- 'Current', 'Short-Term', 'Intermediate-Term', 'Long-Term'
    time_horizon_years INTEGER,  -- 5, 10, 20, 30, 50, 100
    
    -- FEMA Flood Zone Risk
    fema_zone_code VARCHAR(10),
    fema_zone_id VARCHAR(255),
    base_flood_elevation_feet NUMERIC(10, 2),
    flood_zone_risk_score NUMERIC(5, 2),  -- 0-100 risk score
    
    -- Sea Level Rise Risk
    sea_level_rise_feet NUMERIC(8, 3),
    sea_level_rise_scenario VARCHAR(50),
    high_tide_flooding_days INTEGER,
    sea_level_risk_score NUMERIC(5, 2),  -- 0-100 risk score
    
    -- Streamflow Flood Risk
    nearest_gauge_id VARCHAR(50),
    historical_flood_frequency INTEGER,  -- Number of floods in historical record
    flood_probability_percent NUMERIC(5, 2),
    streamflow_risk_score NUMERIC(5, 2),  -- 0-100 risk score
    
    -- NASA Model Risk
    nasa_model_flood_probability NUMERIC(5, 2),
    nasa_model_severity VARCHAR(50),
    nasa_model_risk_score NUMERIC(5, 2),  -- 0-100 risk score
    
    -- Composite Risk Scores
    overall_risk_score NUMERIC(5, 2),  -- Weighted composite risk score (0-100)
    risk_category VARCHAR(50),  -- 'Low', 'Moderate', 'High', 'Extreme'
    vulnerability_score NUMERIC(5, 2),  -- Property vulnerability to flooding
    exposure_score NUMERIC(5, 2),  -- Exposure to flood hazards
    
    -- Financial Impact Estimates
    estimated_damage_dollars NUMERIC(15, 2),
    estimated_annual_loss NUMERIC(15, 2),  -- Expected annual loss
    insurance_premium_estimate NUMERIC(12, 2),
    
    -- Assessment Metadata
    assessment_methodology VARCHAR(255),
    data_sources_used VARCHAR(500),
    confidence_level VARCHAR(50),
    assessment_notes TEXT,
    created_by VARCHAR(255),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property-Flood Zone Intersections Table
-- Documents spatial relationships between properties and flood zones
CREATE TABLE property_flood_zone_intersections (
    intersection_id VARCHAR(255) PRIMARY KEY,
    property_id VARCHAR(255) NOT NULL,
    zone_id VARCHAR(255) NOT NULL,
    intersection_type VARCHAR(50),  -- 'Within', 'Adjacent', 'Near'
    distance_to_zone_feet NUMERIC(10, 2),
    elevation_difference_feet NUMERIC(10, 2),  -- Property elevation - BFE
    intersection_geom geography,  -- Intersection geometry if applicable
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Historical Flood Events Table
-- Stores historical flood event records for risk analysis
CREATE TABLE historical_flood_events (
    event_id VARCHAR(255) PRIMARY KEY,
    event_name VARCHAR(255),
    event_type VARCHAR(50),  -- 'Riverine', 'Coastal', 'Flash', 'Storm Surge', 'Tidal'
    start_date DATE NOT NULL,
    end_date DATE,
    affected_area_geom geography,  -- Polygon geometry of affected area
    peak_discharge_cfs NUMERIC(12, 2),
    peak_stage_feet NUMERIC(8, 2),
    total_damage_dollars NUMERIC(15, 2),
    fatalities INTEGER,
    properties_affected INTEGER,
    state_code VARCHAR(2),
    county_fips VARCHAR(5),
    data_source VARCHAR(100),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model Performance Metrics Table
-- Tracks flood model accuracy and performance metrics
CREATE TABLE model_performance_metrics (
    metric_id VARCHAR(255) PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    evaluation_date DATE NOT NULL,
    evaluation_period_start DATE,
    evaluation_period_end DATE,
    total_predictions INTEGER,
    true_positives INTEGER,
    true_negatives INTEGER,
    false_positives INTEGER,
    false_negatives INTEGER,
    accuracy NUMERIC(5, 4),  -- 0-1 accuracy score
    precision_score NUMERIC(5, 4),
    recall_score NUMERIC(5, 4),
    f1_score NUMERIC(5, 4),
    roc_auc NUMERIC(5, 4),
    mean_absolute_error NUMERIC(10, 4),
    root_mean_squared_error NUMERIC(10, 4),
    spatial_resolution_meters INTEGER,
    temporal_resolution_hours INTEGER,
    evaluation_notes TEXT,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio Risk Summaries Table
-- Aggregated risk metrics by portfolio
CREATE TABLE portfolio_risk_summaries (
    summary_id VARCHAR(255) PRIMARY KEY,
    portfolio_id VARCHAR(255) NOT NULL,
    portfolio_name VARCHAR(255),
    summary_date DATE NOT NULL,
    total_properties INTEGER,
    properties_at_risk INTEGER,  -- Properties with risk score > threshold
    high_risk_properties INTEGER,  -- Risk score > 70
    moderate_risk_properties INTEGER,  -- Risk score 40-70
    low_risk_properties INTEGER,  -- Risk score < 40
    average_risk_score NUMERIC(5, 2),
    total_property_value NUMERIC(18, 2),
    at_risk_property_value NUMERIC(18, 2),
    estimated_annual_loss NUMERIC(15, 2),
    portfolio_risk_category VARCHAR(50),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data Quality Metrics Table
-- Tracks data quality for flood risk data sources
CREATE TABLE data_quality_metrics (
    metric_id VARCHAR(255) PRIMARY KEY,
    metric_date DATE NOT NULL,
    data_source VARCHAR(50) NOT NULL,  -- 'FEMA', 'NOAA', 'USGS', 'NASA'
    files_processed INTEGER DEFAULT 0,
    files_successful INTEGER DEFAULT 0,
    files_failed INTEGER DEFAULT 0,
    success_rate NUMERIC(5, 2),
    total_records INTEGER DEFAULT 0,
    records_with_errors INTEGER DEFAULT 0,
    error_rate NUMERIC(5, 2),
    spatial_coverage_km2 NUMERIC(15, 2),
    temporal_coverage_days INTEGER,
    data_freshness_hours INTEGER,
    calculation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_fema_flood_zones_code ON fema_flood_zones(zone_code);
CREATE INDEX idx_fema_flood_zones_geom ON fema_flood_zones USING GIST(zone_geom);
CREATE INDEX idx_fema_flood_zones_state_county ON fema_flood_zones(state_code, county_fips);

CREATE INDEX idx_real_estate_properties_portfolio ON real_estate_properties(portfolio_id);
CREATE INDEX idx_real_estate_properties_geom ON real_estate_properties USING GIST(property_geom);
CREATE INDEX idx_real_estate_properties_state_county ON real_estate_properties(state_code, county_fips);

CREATE INDEX idx_noaa_sea_level_rise_station_year ON noaa_sea_level_rise(station_id, projection_year);
CREATE INDEX idx_noaa_sea_level_rise_geom ON noaa_sea_level_rise USING GIST(station_geom);

CREATE INDEX idx_usgs_streamflow_gauges_active ON usgs_streamflow_gauges(active_status);
CREATE INDEX idx_usgs_streamflow_gauges_geom ON usgs_streamflow_gauges USING GIST(gauge_geom);

CREATE INDEX idx_usgs_streamflow_observations_gauge_time ON usgs_streamflow_observations(gauge_id, observation_time);
CREATE INDEX idx_usgs_streamflow_observations_flood_category ON usgs_streamflow_observations(flood_category);

CREATE INDEX idx_nasa_flood_models_time ON nasa_flood_models(forecast_time);
CREATE INDEX idx_nasa_flood_models_geom ON nasa_flood_models USING GIST(grid_cell_geom);

CREATE INDEX idx_flood_risk_assessments_property ON flood_risk_assessments(property_id);
CREATE INDEX idx_flood_risk_assessments_date ON flood_risk_assessments(assessment_date);
CREATE INDEX idx_flood_risk_assessments_risk_score ON flood_risk_assessments(overall_risk_score);

CREATE INDEX idx_property_flood_zone_intersections_property ON property_flood_zone_intersections(property_id);
CREATE INDEX idx_property_flood_zone_intersections_zone ON property_flood_zone_intersections(zone_id);

CREATE INDEX idx_historical_flood_events_date ON historical_flood_events(start_date);
CREATE INDEX idx_historical_flood_events_geom ON historical_flood_events USING GIST(affected_area_geom);

CREATE INDEX idx_model_performance_metrics_model_date ON model_performance_metrics(model_name, evaluation_date);

CREATE INDEX idx_portfolio_risk_summaries_portfolio_date ON portfolio_risk_summaries(portfolio_id, summary_date);
