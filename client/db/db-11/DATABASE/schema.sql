-- PostgreSQL-specific schema file
-- Generated from schema.sql
-- Generated: 2026-02-05 19:10:10
-- Database: db-11
-- 
-- This file contains PostgreSQL-specific SQL syntax.
-- Use this file when setting up the database in PostgreSQL.
--

-- Parking Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for parking data pipeline system

-- Metropolitan Areas Table
-- Stores metropolitan statistical areas (MSAs) and combined statistical areas (CSAs)
-- Enable PostGIS extension for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE metropolitan_areas (
    msa_id VARCHAR(50) PRIMARY KEY,
    msa_name VARCHAR(255) NOT NULL,
    msa_type VARCHAR(50) NOT NULL,  -- 'MSA', 'CSA', 'Micropolitan'
    state_codes VARCHAR(100),  -- Comma-separated state codes
    principal_city VARCHAR(255),
    population_estimate INTEGER,
    land_area_sq_miles NUMERIC(12, 2),
    population_density NUMERIC(10, 2),
    median_household_income NUMERIC(12, 2),
    gdp_billions NUMERIC(12, 2),
    msa_geom GEOGRAPHY,  -- Polygon geometry for MSA boundary
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    data_year INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Cities Table
-- Stores city-level demographic and economic data
CREATE TABLE cities (
    city_id VARCHAR(50) PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    state_code VARCHAR(2) NOT NULL,
    county_name VARCHAR(255),
    msa_id VARCHAR(50),
    population INTEGER,
    land_area_sq_miles NUMERIC(10, 2),
    population_density NUMERIC(10, 2),
    median_household_income NUMERIC(12, 2),
    median_age NUMERIC(5, 2),
    employment_total INTEGER,
    unemployment_rate NUMERIC(5, 2),
    city_geom GEOGRAPHY,  -- Point geometry for city center
    city_latitude NUMERIC(10, 7),
    city_longitude NUMERIC(10, 7),
    timezone VARCHAR(50),
    data_year INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (msa_id) REFERENCES metropolitan_areas(msa_id)
);

-- Airports Table
-- Stores airport information including passenger volumes and parking capacity
CREATE TABLE airports (
    airport_id VARCHAR(10) PRIMARY KEY,  -- IATA code
    airport_name VARCHAR(255) NOT NULL,
    city_id VARCHAR(50),
    state_code VARCHAR(2),
    airport_type VARCHAR(50),  -- 'Commercial', 'Cargo', 'General Aviation'
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    airport_geom GEOGRAPHY,  -- Point geometry
    annual_passengers INTEGER,
    annual_cargo_tons INTEGER,
    parking_spaces_total INTEGER,
    parking_facilities_count INTEGER,
    valet_available BOOLEAN,
    long_term_parking BOOLEAN,
    short_term_parking BOOLEAN,
    data_year INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Stadiums and Venues Table
-- Stores sports stadiums, concert venues, and event facilities
CREATE TABLE stadiums_venues (
    venue_id VARCHAR(50) PRIMARY KEY,
    venue_name VARCHAR(255) NOT NULL,
    venue_type VARCHAR(50),  -- 'Stadium', 'Arena', 'Convention Center', 'Amphitheater'
    city_id VARCHAR(50),
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    venue_geom GEOGRAPHY,  -- Point geometry
    capacity INTEGER,
    parking_spaces_total INTEGER,
    parking_facilities_count INTEGER,
    primary_sport VARCHAR(100),  -- 'NFL', 'MLB', 'NBA', 'NHL', 'Soccer', 'Concert'
    team_name VARCHAR(255),
    annual_events_count INTEGER,
    peak_attendance INTEGER,
    data_year INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Parking Facilities Table
-- Stores individual parking facilities (lots, garages, structures)
CREATE TABLE parking_facilities (
    facility_id VARCHAR(100) PRIMARY KEY,
    facility_name VARCHAR(255),
    facility_type VARCHAR(50),  -- 'Surface Lot', 'Garage', 'Structure', 'Valet', 'Street'
    city_id VARCHAR(50),
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    facility_geom GEOGRAPHY,  -- Point geometry
    total_spaces INTEGER,
    accessible_spaces INTEGER,
    ev_charging_stations INTEGER,
    covered_spaces INTEGER,
    uncovered_spaces INTEGER,
    height_restriction_feet NUMERIC(5, 2),
    operator_name VARCHAR(255),
    operator_type VARCHAR(50),  -- 'Public', 'Private', 'Municipal', 'Airport', 'Venue'
    airport_id VARCHAR(10),
    venue_id VARCHAR(50),
    is_event_parking BOOLEAN DEFAULT FALSE,
    is_monthly_parking BOOLEAN DEFAULT FALSE,
    is_hourly_parking BOOLEAN DEFAULT TRUE,
    accepts_reservations BOOLEAN DEFAULT FALSE,
    payment_methods VARCHAR(255),  -- Comma-separated: 'Cash', 'Credit', 'Mobile', 'App'
    amenities VARCHAR(500),  -- Comma-separated amenities
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (airport_id) REFERENCES airports(airport_id),
    FOREIGN KEY (venue_id) REFERENCES stadiums_venues(venue_id)
);

-- Parking Pricing Table
-- Stores pricing information for parking facilities
CREATE TABLE parking_pricing (
    pricing_id VARCHAR(100) PRIMARY KEY,
    facility_id VARCHAR(100) NOT NULL,
    pricing_type VARCHAR(50),  -- 'Hourly', 'Daily', 'Monthly', 'Event', 'Early Bird'
    base_rate_hourly NUMERIC(8, 2),
    base_rate_daily NUMERIC(8, 2),
    base_rate_monthly NUMERIC(8, 2),
    event_rate NUMERIC(8, 2),
    max_daily_rate NUMERIC(8, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    effective_date DATE,
    expiration_date DATE,
    day_of_week VARCHAR(20),  -- 'Monday', 'Tuesday', etc., or 'All'
    time_range_start TIME,
    time_range_end TIME,
    is_active BOOLEAN DEFAULT TRUE,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(facility_id)
);

-- Traffic Volume Data Table
-- Stores traffic volume statistics from FHWA
CREATE TABLE traffic_volume_data (
    traffic_id VARCHAR(100) PRIMARY KEY,
    location_id VARCHAR(100),
    city_id VARCHAR(50),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    location_geom GEOGRAPHY,  -- Point geometry
    road_name VARCHAR(255),
    road_type VARCHAR(50),  -- 'Highway', 'Arterial', 'Collector', 'Local'
    annual_average_daily_traffic INTEGER,
    peak_hour_volume INTEGER,
    direction VARCHAR(20),  -- 'Northbound', 'Southbound', 'Eastbound', 'Westbound', 'Both'
    data_year INTEGER,
    data_month INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Events Table
-- Stores event information (sports games, concerts, conventions)
CREATE TABLE events (
    event_id VARCHAR(100) PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50),  -- 'Sports', 'Concert', 'Convention', 'Festival', 'Conference'
    venue_id VARCHAR(50),
    city_id VARCHAR(50),
    event_date DATE NOT NULL,
    event_time TIME,
    attendance INTEGER,
    parking_demand_multiplier NUMERIC(5, 2),  -- Multiplier for parking demand
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR(100),  -- 'Weekly', 'Monthly', 'Seasonal'
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (venue_id) REFERENCES stadiums_venues(venue_id),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Market Metrics Table
-- Stores calculated market metrics and analytics
CREATE TABLE market_intelligence_metrics (
    metric_id VARCHAR(100) PRIMARY KEY,
    city_id VARCHAR(50),
    msa_id VARCHAR(50),
    metric_type VARCHAR(50),  -- 'Demand', 'Supply', 'Utilization', 'Revenue', 'Competition'
    metric_name VARCHAR(100),
    metric_value NUMERIC(15, 2),
    metric_unit VARCHAR(50),
    calculation_date DATE,
    time_period VARCHAR(50),  -- 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Annual'
    data_year INTEGER,
    data_month INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (msa_id) REFERENCES metropolitan_areas(msa_id)
);

-- Parking Utilization Table
-- Stores parking utilization and occupancy data
CREATE TABLE parking_utilization (
    utilization_id VARCHAR(100) PRIMARY KEY,
    facility_id VARCHAR(100) NOT NULL,
    utilization_date DATE NOT NULL,
    utilization_hour INTEGER,  -- 0-23
    occupancy_rate NUMERIC(5, 2),  -- Percentage 0-100
    spaces_occupied INTEGER,
    spaces_available INTEGER,
    revenue_generated NUMERIC(10, 2),
    reservation_count INTEGER,
    walk_in_count INTEGER,
    data_source VARCHAR(50),  -- 'Sensor', 'Manual', 'App', 'Estimated'
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(facility_id)
);

-- Competitive Analysis Table
-- Stores competitive parking facility analysis
CREATE TABLE competitive_analysis (
    analysis_id VARCHAR(100) PRIMARY KEY,
    facility_id VARCHAR(100) NOT NULL,
    competitor_facility_id VARCHAR(100),
    analysis_date DATE,
    price_difference_pct NUMERIC(5, 2),
    distance_miles NUMERIC(8, 2),
    utilization_difference_pct NUMERIC(5, 2),
    amenity_comparison VARCHAR(500),
    competitive_score NUMERIC(5, 2),  -- 0-100
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(facility_id),
    FOREIGN KEY (competitor_facility_id) REFERENCES parking_facilities(facility_id)
);

-- Business Districts Table
-- Stores business district and commercial area information
CREATE TABLE business_districts (
    district_id VARCHAR(50) PRIMARY KEY,
    district_name VARCHAR(255) NOT NULL,
    city_id VARCHAR(50),
    district_type VARCHAR(50),  -- 'Downtown', 'Financial', 'Retail', 'Entertainment', 'Airport', 'Medical'
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    district_geom GEOGRAPHY,  -- Polygon geometry
    employment_total INTEGER,
    businesses_count INTEGER,
    parking_demand_score NUMERIC(5, 2),  -- 0-100
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    data_year INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Parking Facility to Business District Mapping
CREATE TABLE facility_district_mapping (
    mapping_id VARCHAR(100) PRIMARY KEY,
    facility_id VARCHAR(100) NOT NULL,
    district_id VARCHAR(50) NOT NULL,
    distance_miles NUMERIC(8, 2),
    is_primary_district BOOLEAN DEFAULT FALSE,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(facility_id),
    FOREIGN KEY (district_id) REFERENCES business_districts(district_id)
);

-- Data Source Metadata Table
-- Tracks data sources and extraction metadata
CREATE TABLE data_source_metadata (
    source_id VARCHAR(100) PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50),  -- 'API', 'CSV', 'Shapefile', 'Database', 'Web Scrape'
    source_url VARCHAR(1000),
    api_endpoint VARCHAR(500),
    extraction_date DATE,
    extraction_timestamp TIMESTAMP,
    records_extracted INTEGER,
    data_quality_score NUMERIC(5, 2),  -- 0-100
    completeness_pct NUMERIC(5, 2),
    error_count INTEGER,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Indexes for performance optimization
CREATE INDEX idx_cities_state ON cities(state_code);
CREATE INDEX idx_cities_msa ON cities(msa_id);
CREATE INDEX idx_parking_facilities_city ON parking_facilities(city_id);
CREATE INDEX idx_parking_facilities_airport ON parking_facilities(airport_id);
CREATE INDEX idx_parking_facilities_venue ON parking_facilities(venue_id);
CREATE INDEX idx_parking_pricing_facility ON parking_pricing(facility_id);
CREATE INDEX idx_parking_utilization_facility_date ON parking_utilization(facility_id, utilization_date);
CREATE INDEX idx_events_venue_date ON events(venue_id, event_date);
CREATE INDEX idx_events_city_date ON events(city_id, event_date);
CREATE INDEX idx_traffic_volume_city ON traffic_volume_data(city_id);
CREATE INDEX idx_market_metrics_city ON market_intelligence_metrics(city_id);
CREATE INDEX idx_market_metrics_msa ON market_intelligence_metrics(msa_id);

-- Spatial indexes (PostgreSQL PostGIS)
-- CREATE INDEX idx_metropolitan_areas_geom ON metropolitan_areas USING GIST(msa_geom);
-- CREATE INDEX idx_cities_geom ON cities USING GIST(city_geom);
-- CREATE INDEX idx_airports_geom ON airports USING GIST(airport_geom);
-- CREATE INDEX idx_stadiums_venues_geom ON stadiums_venues USING GIST(venue_geom);
-- CREATE INDEX idx_parking_facilities_geom ON parking_facilities USING GIST(facility_geom);
-- CREATE INDEX idx_traffic_volume_geom ON traffic_volume_data USING GIST(location_geom);
-- CREATE INDEX idx_business_districts_geom ON business_districts USING GIST(district_geom);
