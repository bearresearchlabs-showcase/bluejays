-- PostgreSQL-specific schema file
-- Generated from schema.sql
-- Generated: 2026-02-05 19:10:04
-- Database: db-7
-- 
-- This file contains PostgreSQL-specific SQL syntax.
-- Use this file when setting up the database in PostgreSQL.
--

-- Maritime Shipping Intelligence Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for maritime schedules and shipping intelligence system
-- Based on Linescape API structure with government data integration

-- Carriers Table
-- Stores shipping line/carrier information
-- Enable PostGIS extension for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE carriers (
    carrier_id VARCHAR(255) PRIMARY KEY,
    carrier_name VARCHAR(255) NOT NULL,
    scac_code VARCHAR(10) UNIQUE,  -- Standard Carrier Alpha Code
    carrier_type VARCHAR(50),  -- 'Container', 'Bulk', 'RoRo', 'Tanker', 'General'
    country VARCHAR(100),
    website VARCHAR(500),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Active',
    fleet_size INTEGER,
    total_capacity_teu INTEGER,
    established_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations Table
-- Stores regions, countries, and geographic areas
CREATE TABLE locations (
    location_id VARCHAR(255) PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    location_type VARCHAR(50) NOT NULL,  -- 'Country', 'Region', 'State', 'Province'
    parent_location_id VARCHAR(255),
    country_code VARCHAR(3),  -- ISO 3166-1 alpha-3
    region_code VARCHAR(10),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    location_geom GEOGRAPHY,  -- Point geometry for location center
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ports Table
-- Stores port information and characteristics
CREATE TABLE ports (
    port_id VARCHAR(255) PRIMARY KEY,
    port_name VARCHAR(255) NOT NULL,
    port_code VARCHAR(20) UNIQUE,  -- UN/LOCODE or port code
    locode VARCHAR(10),  -- UN/LOCODE (5 characters: 2 country + 3 location)
    location_id VARCHAR(255),
    country VARCHAR(100),
    country_code VARCHAR(3),
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    port_geom GEOGRAPHY,  -- Point geometry for port location
    port_type VARCHAR(50),  -- 'Container', 'Bulk', 'RoRo', 'Tanker', 'General', 'Multi-purpose'
    timezone VARCHAR(50),
    depth_meters NUMERIC(8, 2),
    max_vessel_length_meters NUMERIC(8, 2),
    max_vessel_draft_meters NUMERIC(8, 2),
    container_capacity_teu INTEGER,
    berth_count INTEGER,
    crane_count INTEGER,
    status VARCHAR(50) DEFAULT 'Active',
    data_source VARCHAR(100),  -- 'MARAD', 'NOAA', 'USCG', 'Linescape', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vessels Table
-- Stores vessel information and characteristics
CREATE TABLE vessels (
    vessel_id VARCHAR(255) PRIMARY KEY,
    vessel_name VARCHAR(255) NOT NULL,
    imo_number VARCHAR(10) UNIQUE,  -- International Maritime Organization number
    mmsi VARCHAR(9),  -- Maritime Mobile Service Identity
    call_sign VARCHAR(20),
    carrier_id VARCHAR(255),
    vessel_type VARCHAR(50),  -- 'Container', 'Bulk', 'RoRo', 'Tanker', 'General Cargo'
    flag_country VARCHAR(100),
    flag_country_code VARCHAR(3),
    year_built INTEGER,
    gross_tonnage INTEGER,
    net_tonnage INTEGER,
    deadweight_tonnage INTEGER,
    length_meters NUMERIC(8, 2),
    beam_meters NUMERIC(8, 2),
    draft_meters NUMERIC(8, 2),
    max_speed_knots NUMERIC(6, 2),
    container_capacity_teu INTEGER,
    container_capacity_twenty_foot INTEGER,
    container_capacity_forty_foot INTEGER,
    status VARCHAR(50) DEFAULT 'Active',
    data_source VARCHAR(100),  -- 'USCG', 'NOAA', 'MARAD', 'Linescape', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Routes Table
-- Stores shipping routes/services operated by carriers
CREATE TABLE routes (
    route_id VARCHAR(255) PRIMARY KEY,
    route_name VARCHAR(255) NOT NULL,
    route_code VARCHAR(100),
    carrier_id VARCHAR(255) NOT NULL,
    service_type VARCHAR(50),  -- 'Direct', 'Feeder', 'Express', 'Regular'
    route_type VARCHAR(50),  -- 'Trans-Pacific', 'Trans-Atlantic', 'Asia-Europe', etc.
    frequency_weeks INTEGER,  -- Service frequency in weeks
    transit_time_days INTEGER,  -- Average transit time
    status VARCHAR(50) DEFAULT 'Active',
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Route Ports Table
-- Junction table linking routes to ports (many-to-many)
CREATE TABLE route_ports (
    route_port_id VARCHAR(255) PRIMARY KEY,
    route_id VARCHAR(255) NOT NULL,
    port_id VARCHAR(255) NOT NULL,
    port_sequence INTEGER NOT NULL,  -- Order of port call in route
    port_role VARCHAR(50),  -- 'Origin', 'Destination', 'Transshipment', 'Intermediate'
    estimated_days_from_start INTEGER,  -- Days from route start
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(route_id, port_id, port_sequence)
);

-- Port Pairs Table
-- Stores origin-destination port pairs for carriers
CREATE TABLE port_pairs (
    port_pair_id VARCHAR(255) PRIMARY KEY,
    origin_port_id VARCHAR(255) NOT NULL,
    destination_port_id VARCHAR(255) NOT NULL,
    carrier_id VARCHAR(255) NOT NULL,
    route_id VARCHAR(255),
    direct_service BOOLEAN DEFAULT FALSE,  -- True if direct service exists
    transshipment_required BOOLEAN DEFAULT FALSE,
    average_transit_days INTEGER,
    service_frequency_weeks INTEGER,
    last_sailing_date DATE,
    status VARCHAR(50) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(origin_port_id, destination_port_id, carrier_id)
);

-- Port Calls Table
-- Stores scheduled and actual port calls
CREATE TABLE port_calls (
    port_call_id VARCHAR(255) PRIMARY KEY,
    vessel_id VARCHAR(255) NOT NULL,
    port_id VARCHAR(255) NOT NULL,
    voyage_number VARCHAR(100),
    route_id VARCHAR(255),
    scheduled_arrival TIMESTAMP,
    actual_arrival TIMESTAMP,
    scheduled_departure TIMESTAMP,
    actual_departure TIMESTAMP,
    port_call_type VARCHAR(50),  -- 'Loading', 'Discharging', 'Transshipment', 'Bunkering', 'Repair'
    berth_number VARCHAR(50),
    terminal_name VARCHAR(255),
    cargo_type VARCHAR(100),
    containers_loaded INTEGER,
    containers_discharged INTEGER,
    containers_transshipped INTEGER,
    status VARCHAR(50) DEFAULT 'Scheduled',  -- 'Scheduled', 'In Progress', 'Completed', 'Cancelled'
    delay_hours NUMERIC(8, 2),
    data_source VARCHAR(100),  -- 'AIS', 'NOAD', 'MARAD', 'Linescape', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sailings Table
-- Stores sailing/voyage information between ports
CREATE TABLE sailings (
    sailing_id VARCHAR(255) PRIMARY KEY,
    vessel_id VARCHAR(255) NOT NULL,
    voyage_number VARCHAR(100),
    route_id VARCHAR(255),
    origin_port_id VARCHAR(255) NOT NULL,
    destination_port_id VARCHAR(255) NOT NULL,
    scheduled_departure TIMESTAMP,
    actual_departure TIMESTAMP,
    scheduled_arrival TIMESTAMP,
    actual_arrival TIMESTAMP,
    transit_days INTEGER,
    distance_nautical_miles NUMERIC(10, 2),
    average_speed_knots NUMERIC(6, 2),
    cargo_type VARCHAR(100),
    total_containers INTEGER,
    total_teu NUMERIC(10, 2),
    capacity_utilization_percent NUMERIC(5, 2),
    transshipment_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Scheduled',  -- 'Scheduled', 'In Transit', 'Completed', 'Cancelled'
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Voyages Table
-- Stores complete voyage information from start port to end port
CREATE TABLE voyages (
    voyage_id VARCHAR(255) PRIMARY KEY,
    vessel_id VARCHAR(255) NOT NULL,
    voyage_number VARCHAR(100) NOT NULL,
    route_id VARCHAR(255),
    start_port_id VARCHAR(255) NOT NULL,
    end_port_id VARCHAR(255) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    total_distance_nautical_miles NUMERIC(10, 2),
    total_transit_days INTEGER,
    port_call_count INTEGER,
    transshipment_count INTEGER DEFAULT 0,
    total_containers INTEGER,
    total_teu NUMERIC(10, 2),
    status VARCHAR(50) DEFAULT 'In Progress',  -- 'Scheduled', 'In Progress', 'Completed', 'Cancelled'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Voyage Port Calls Table
-- Links voyages to port calls (voyage can have multiple port calls)
CREATE TABLE voyage_port_calls (
    voyage_port_call_id VARCHAR(255) PRIMARY KEY,
    voyage_id VARCHAR(255) NOT NULL,
    port_call_id VARCHAR(255) NOT NULL,
    port_sequence INTEGER NOT NULL,  -- Order of port call in voyage
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(voyage_id, port_call_id)
);

-- Vessel Tracking Table
-- Stores AIS (Automatic Identification System) tracking data
CREATE TABLE vessel_tracking (
    tracking_id VARCHAR(255) PRIMARY KEY,
    vessel_id VARCHAR(255) NOT NULL,
    mmsi VARCHAR(9),
    timestamp TIMESTAMP NOT NULL,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    position_geom GEOGRAPHY,  -- Point geometry for vessel position
    speed_knots NUMERIC(6, 2),
    course_degrees NUMERIC(6, 2),
    heading_degrees NUMERIC(6, 2),
    navigation_status VARCHAR(50),  -- 'Under way', 'At anchor', 'Moored', etc.
    destination VARCHAR(255),
    eta TIMESTAMP,  -- Estimated time of arrival
    draught_meters NUMERIC(6, 2),
    cargo_type VARCHAR(100),
    data_source VARCHAR(100) DEFAULT 'AIS',  -- 'AIS', 'USCG', 'NOAA', etc.
    data_quality VARCHAR(50),  -- 'High', 'Medium', 'Low'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Port Statistics Table
-- Stores aggregated port statistics and performance metrics
CREATE TABLE port_statistics (
    statistic_id VARCHAR(255) PRIMARY KEY,
    port_id VARCHAR(255) NOT NULL,
    statistic_date DATE NOT NULL,
    statistic_period VARCHAR(50),  -- 'Daily', 'Weekly', 'Monthly', 'Yearly'
    total_vessel_calls INTEGER,
    total_container_teu NUMERIC(12, 2),
    containers_loaded INTEGER,
    containers_discharged INTEGER,
    containers_transshipped INTEGER,
    average_vessel_size_teu NUMERIC(10, 2),
    average_dwell_time_hours NUMERIC(8, 2),
    berth_utilization_percent NUMERIC(5, 2),
    crane_utilization_percent NUMERIC(5, 2),
    data_source VARCHAR(100),  -- 'MARAD', 'Port Authority', 'Linescape', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(port_id, statistic_date, statistic_period)
);

-- Carrier Performance Table
-- Stores carrier performance metrics and KPIs
CREATE TABLE carrier_performance (
    performance_id VARCHAR(255) PRIMARY KEY,
    carrier_id VARCHAR(255) NOT NULL,
    evaluation_period_start DATE NOT NULL,
    evaluation_period_end DATE NOT NULL,
    total_voyages INTEGER,
    on_time_departures INTEGER,
    on_time_arrivals INTEGER,
    on_time_performance_percent NUMERIC(5, 2),
    average_transit_time_days NUMERIC(8, 2),
    vessel_utilization_percent NUMERIC(5, 2),
    capacity_utilization_percent NUMERIC(5, 2),
    total_teu_carried NUMERIC(12, 2),
    port_calls_count INTEGER,
    route_coverage_count INTEGER,
    customer_satisfaction_score NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_ports_location ON ports(location_id);
CREATE INDEX idx_ports_locode ON ports(locode);
CREATE INDEX idx_ports_country ON ports(country_code);
CREATE INDEX idx_vessels_carrier ON vessels(carrier_id);
CREATE INDEX idx_vessels_imo ON vessels(imo_number);
CREATE INDEX idx_vessels_mmsi ON vessels(mmsi);
CREATE INDEX idx_routes_carrier ON routes(carrier_id);
CREATE INDEX idx_route_ports_route ON route_ports(route_id);
CREATE INDEX idx_route_ports_port ON route_ports(port_id);
CREATE INDEX idx_port_pairs_origin ON port_pairs(origin_port_id);
CREATE INDEX idx_port_pairs_destination ON port_pairs(destination_port_id);
CREATE INDEX idx_port_pairs_carrier ON port_pairs(carrier_id);
CREATE INDEX idx_port_calls_vessel ON port_calls(vessel_id);
CREATE INDEX idx_port_calls_port ON port_calls(port_id);
CREATE INDEX idx_port_calls_route ON port_calls(route_id);
CREATE INDEX idx_port_calls_arrival ON port_calls(scheduled_arrival, actual_arrival);
CREATE INDEX idx_sailings_vessel ON sailings(vessel_id);
CREATE INDEX idx_sailings_origin ON sailings(origin_port_id);
CREATE INDEX idx_sailings_destination ON sailings(destination_port_id);
CREATE INDEX idx_sailings_departure ON sailings(scheduled_departure, actual_departure);
CREATE INDEX idx_voyages_vessel ON voyages(vessel_id);
CREATE INDEX idx_voyages_route ON voyages(route_id);
CREATE INDEX idx_voyages_start_date ON voyages(start_date);
CREATE INDEX idx_voyage_port_calls_voyage ON voyage_port_calls(voyage_id);
CREATE INDEX idx_voyage_port_calls_port_call ON voyage_port_calls(port_call_id);
CREATE INDEX idx_vessel_tracking_vessel ON vessel_tracking(vessel_id);
CREATE INDEX idx_vessel_tracking_timestamp ON vessel_tracking(timestamp);
CREATE INDEX idx_vessel_tracking_mmsi ON vessel_tracking(mmsi);
CREATE INDEX idx_port_statistics_port ON port_statistics(port_id);
CREATE INDEX idx_port_statistics_date ON port_statistics(statistic_date);
CREATE INDEX idx_carrier_performance_carrier ON carrier_performance(carrier_id);
CREATE INDEX idx_carrier_performance_period ON carrier_performance(evaluation_period_start, evaluation_period_end);

-- Spatial indexes (PostgreSQL PostGIS, Snowflake, Databricks)
-- Note: These may need database-specific syntax
-- CREATE INDEX idx_ports_geom ON ports USING GIST(port_geom);
-- CREATE INDEX idx_vessels_tracking_geom ON vessel_tracking USING GIST(position_geom);
-- CREATE INDEX idx_locations_geom ON locations USING GIST(location_geom);
