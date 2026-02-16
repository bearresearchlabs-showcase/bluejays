-- Shipping Intelligence Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for shipping intelligence and rate comparison system

-- Shipping Carriers Table
-- Stores carrier information (USPS, UPS, FedEx, etc.)
CREATE TABLE shipping_carriers (
    carrier_id VARCHAR(50) PRIMARY KEY,
    carrier_name VARCHAR(100) NOT NULL,
    carrier_code VARCHAR(10) NOT NULL UNIQUE,  -- 'USPS', 'UPS', 'FEDEX'
    carrier_type VARCHAR(50),  -- 'Postal', 'Courier', 'Freight'
    api_endpoint VARCHAR(500),
    rate_api_version VARCHAR(50),
    tracking_api_version VARCHAR(50),
    commercial_pricing_available BOOLEAN DEFAULT FALSE,
    requires_account BOOLEAN DEFAULT FALSE,
    active_status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Shipping Zones Table
-- Stores zone information for rate calculations (USPS zones, UPS zones)
CREATE TABLE shipping_zones (
    zone_id VARCHAR(255) PRIMARY KEY,
    carrier_id VARCHAR(50) NOT NULL,
    origin_zip_code VARCHAR(10) NOT NULL,
    destination_zip_code VARCHAR(10) NOT NULL,
    zone_number INTEGER NOT NULL,
    zone_type VARCHAR(50),  -- 'Domestic', 'International', 'Alaska', 'Hawaii'
    distance_miles NUMERIC(10, 2),
    transit_days_min INTEGER,
    transit_days_max INTEGER,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (carrier_id) REFERENCES shipping_carriers(carrier_id)
);

-- Shipping Service Types Table
-- Stores available service types (Priority Mail, Ground, Express, etc.)
CREATE TABLE shipping_service_types (
    service_id VARCHAR(255) PRIMARY KEY,
    carrier_id VARCHAR(50) NOT NULL,
    service_code VARCHAR(50) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    service_category VARCHAR(100),  -- 'Express', 'Ground', 'Priority', 'Economy'
    domestic_available BOOLEAN DEFAULT TRUE,
    international_available BOOLEAN DEFAULT FALSE,
    max_weight_lbs NUMERIC(10, 2),
    max_dimensions_length NUMERIC(10, 2),
    max_dimensions_width NUMERIC(10, 2),
    max_dimensions_height NUMERIC(10, 2),
    tracking_included BOOLEAN DEFAULT TRUE,
    insurance_available BOOLEAN DEFAULT FALSE,
    signature_required BOOLEAN DEFAULT FALSE,
    active_status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (carrier_id) REFERENCES shipping_carriers(carrier_id)
);

-- Shipping Rate Tables Table
-- Stores historical and current shipping rates
CREATE TABLE shipping_rates (
    rate_id VARCHAR(255) PRIMARY KEY,
    carrier_id VARCHAR(50) NOT NULL,
    service_id VARCHAR(255) NOT NULL,
    zone_id VARCHAR(255),
    weight_lbs NUMERIC(10, 4) NOT NULL,
    weight_oz NUMERIC(10, 4),
    length_inches NUMERIC(10, 2),
    width_inches NUMERIC(10, 2),
    height_inches NUMERIC(10, 2),
    dimensional_weight_lbs NUMERIC(10, 4),
    cubic_volume_cubic_inches NUMERIC(12, 4),
    rate_amount NUMERIC(10, 2) NOT NULL,
    rate_type VARCHAR(50),  -- 'Retail', 'Commercial', 'Daily', 'Cubic'
    surcharge_amount NUMERIC(10, 2) DEFAULT 0,
    total_rate NUMERIC(10, 2) NOT NULL,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    rate_source VARCHAR(100),  -- 'API', 'Manual', 'Bulk Import'
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (carrier_id) REFERENCES shipping_carriers(carrier_id),
    FOREIGN KEY (service_id) REFERENCES shipping_service_types(service_id),
    FOREIGN KEY (zone_id) REFERENCES shipping_zones(zone_id)
);

-- Packages Table
-- Stores package information for shipments
CREATE TABLE packages (
    package_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    package_reference VARCHAR(255),
    weight_lbs NUMERIC(10, 4) NOT NULL,
    weight_oz NUMERIC(10, 4),
    length_inches NUMERIC(10, 2) NOT NULL,
    width_inches NUMERIC(10, 2) NOT NULL,
    height_inches NUMERIC(10, 2) NOT NULL,
    dimensional_weight_lbs NUMERIC(10, 4),
    cubic_volume_cubic_inches NUMERIC(12, 4),
    package_type VARCHAR(50),  -- 'Envelope', 'Box', 'Tube', 'Flat'
    package_value NUMERIC(10, 2),
    contents_description VARCHAR(500),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Shipments Table
-- Stores shipment records with origin and destination
CREATE TABLE shipments (
    shipment_id VARCHAR(255) PRIMARY KEY,
    package_id VARCHAR(255) NOT NULL,
    carrier_id VARCHAR(50) NOT NULL,
    service_id VARCHAR(255) NOT NULL,
    tracking_number VARCHAR(255),
    origin_name VARCHAR(255),
    origin_address_line1 VARCHAR(255),
    origin_address_line2 VARCHAR(255),
    origin_city VARCHAR(100),
    origin_state VARCHAR(2),
    origin_zip_code VARCHAR(10) NOT NULL,
    origin_country VARCHAR(2) DEFAULT 'US',
    destination_name VARCHAR(255),
    destination_address_line1 VARCHAR(255),
    destination_address_line2 VARCHAR(255),
    destination_city VARCHAR(100),
    destination_state VARCHAR(2),
    destination_zip_code VARCHAR(10) NOT NULL,
    destination_country VARCHAR(2) DEFAULT 'US',
    zone_id VARCHAR(255),
    rate_id VARCHAR(255),
    label_cost NUMERIC(10, 2),
    insurance_cost NUMERIC(10, 2) DEFAULT 0,
    signature_cost NUMERIC(10, 2) DEFAULT 0,
    total_cost NUMERIC(10, 2) NOT NULL,
    shipment_status VARCHAR(50),  -- 'Pending', 'Label Created', 'In Transit', 'Delivered', 'Exception'
    label_created_at TIMESTAMP_NTZ,
    estimated_delivery_date DATE,
    actual_delivery_date DATE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (package_id) REFERENCES packages(package_id),
    FOREIGN KEY (carrier_id) REFERENCES shipping_carriers(carrier_id),
    FOREIGN KEY (service_id) REFERENCES shipping_service_types(service_id),
    FOREIGN KEY (zone_id) REFERENCES shipping_zones(zone_id),
    FOREIGN KEY (rate_id) REFERENCES shipping_rates(rate_id)
);

-- Tracking Events Table
-- Stores tracking events for shipments
CREATE TABLE tracking_events (
    event_id VARCHAR(255) PRIMARY KEY,
    shipment_id VARCHAR(255) NOT NULL,
    tracking_number VARCHAR(255) NOT NULL,
    event_timestamp TIMESTAMP_NTZ NOT NULL,
    event_type VARCHAR(100),  -- 'Label Created', 'In Transit', 'Out for Delivery', 'Delivered', 'Exception'
    event_status VARCHAR(100),
    event_location VARCHAR(255),
    event_city VARCHAR(100),
    event_state VARCHAR(2),
    event_zip_code VARCHAR(10),
    event_country VARCHAR(2),
    event_description VARCHAR(1000),
    carrier_status_code VARCHAR(50),
    raw_event_data VARIANT,  -- JSON data from carrier API
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);

-- Rate Comparison Results Table
-- Stores rate comparison results across carriers
CREATE TABLE rate_comparison_results (
    comparison_id VARCHAR(255) PRIMARY KEY,
    package_id VARCHAR(255) NOT NULL,
    origin_zip_code VARCHAR(10) NOT NULL,
    destination_zip_code VARCHAR(10) NOT NULL,
    comparison_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    cheapest_carrier_id VARCHAR(50),
    cheapest_service_id VARCHAR(255),
    cheapest_rate NUMERIC(10, 2),
    fastest_carrier_id VARCHAR(50),
    fastest_service_id VARCHAR(255),
    fastest_transit_days INTEGER,
    total_options_count INTEGER,
    comparison_metadata VARIANT,  -- JSON with all rate options
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (package_id) REFERENCES packages(package_id),
    FOREIGN KEY (cheapest_carrier_id) REFERENCES shipping_carriers(carrier_id),
    FOREIGN KEY (fastest_carrier_id) REFERENCES shipping_carriers(carrier_id)
);

-- Address Validation Results Table
-- Stores address validation results from USPS Address API
CREATE TABLE address_validation_results (
    validation_id VARCHAR(255) PRIMARY KEY,
    input_address_line1 VARCHAR(255),
    input_address_line2 VARCHAR(255),
    input_city VARCHAR(100),
    input_state VARCHAR(2),
    input_zip_code VARCHAR(10),
    validated_address_line1 VARCHAR(255),
    validated_address_line2 VARCHAR(255),
    validated_city VARCHAR(100),
    validated_state VARCHAR(2),
    validated_zip_code VARCHAR(10),
    validated_zip_plus_4 VARCHAR(10),
    validation_status VARCHAR(50),  -- 'Valid', 'Invalid', 'Corrected', 'Ambiguous'
    delivery_point_code VARCHAR(10),
    carrier_route VARCHAR(10),
    dpv_confirmation VARCHAR(50),
    cmra_flag BOOLEAN,
    vacant_flag BOOLEAN,
    residential_flag BOOLEAN,
    validation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Shipping Adjustments Table
-- Stores shipping adjustments and discrepancies (from USPS Adjustments API)
CREATE TABLE shipping_adjustments (
    adjustment_id VARCHAR(255) PRIMARY KEY,
    shipment_id VARCHAR(255),
    tracking_number VARCHAR(255) NOT NULL,
    adjustment_type VARCHAR(100),  -- 'Weight', 'Dimensions', 'Zone', 'Packaging'
    original_amount NUMERIC(10, 2),
    adjusted_amount NUMERIC(10, 2),
    adjustment_amount NUMERIC(10, 2),
    adjustment_reason VARCHAR(500),
    adjustment_status VARCHAR(50),  -- 'Pending', 'Applied', 'Disputed', 'Resolved'
    adjustment_date DATE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);

-- Bulk Shipping Presets Table
-- Stores preset configurations for bulk shipping
CREATE TABLE bulk_shipping_presets (
    preset_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    preset_name VARCHAR(255) NOT NULL,
    package_type VARCHAR(50),
    default_weight_lbs NUMERIC(10, 4),
    default_length_inches NUMERIC(10, 2),
    default_width_inches NUMERIC(10, 2),
    default_height_inches NUMERIC(10, 2),
    default_service_id VARCHAR(255),
    default_carrier_id VARCHAR(50),
    default_insurance_amount NUMERIC(10, 2),
    default_signature_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (default_service_id) REFERENCES shipping_service_types(service_id),
    FOREIGN KEY (default_carrier_id) REFERENCES shipping_carriers(carrier_id)
);

-- Shipping Analytics Table
-- Stores aggregated shipping analytics and metrics
CREATE TABLE shipping_analytics (
    analytics_id VARCHAR(255) PRIMARY KEY,
    analytics_date DATE NOT NULL,
    carrier_id VARCHAR(50),
    service_id VARCHAR(255),
    total_shipments INTEGER DEFAULT 0,
    total_revenue NUMERIC(12, 2) DEFAULT 0,
    average_rate NUMERIC(10, 2),
    total_packages INTEGER DEFAULT 0,
    total_weight_lbs NUMERIC(12, 4) DEFAULT 0,
    average_transit_days NUMERIC(6, 2),
    on_time_delivery_rate NUMERIC(5, 2),
    exception_rate NUMERIC(5, 2),
    average_package_value NUMERIC(10, 2),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (carrier_id) REFERENCES shipping_carriers(carrier_id),
    FOREIGN KEY (service_id) REFERENCES shipping_service_types(service_id)
);

-- International Shipping Customs Table
-- Stores customs information for international shipments
CREATE TABLE international_customs (
    customs_id VARCHAR(255) PRIMARY KEY,
    shipment_id VARCHAR(255) NOT NULL,
    customs_declaration_number VARCHAR(255),
    customs_value NUMERIC(10, 2) NOT NULL,
    currency_code VARCHAR(3) DEFAULT 'USD',
    contents_description VARCHAR(1000),
    hs_tariff_code VARCHAR(20),
    country_of_origin VARCHAR(2),
    customs_duty_amount NUMERIC(10, 2),
    customs_tax_amount NUMERIC(10, 2),
    customs_fees_amount NUMERIC(10, 2),
    total_customs_amount NUMERIC(10, 2),
    customs_status VARCHAR(50),  -- 'Pending', 'Cleared', 'Held', 'Returned'
    customs_cleared_date DATE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);

-- API Rate Request Log Table
-- Tracks API rate requests for monitoring and optimization
CREATE TABLE api_rate_request_log (
    log_id VARCHAR(255) PRIMARY KEY,
    carrier_id VARCHAR(50) NOT NULL,
    request_type VARCHAR(50),  -- 'Rate', 'Tracking', 'Address Validation'
    origin_zip_code VARCHAR(10),
    destination_zip_code VARCHAR(10),
    weight_lbs NUMERIC(10, 4),
    request_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    response_time_ms INTEGER,
    response_status_code INTEGER,
    rate_returned NUMERIC(10, 2),
    error_message VARCHAR(1000),
    api_endpoint VARCHAR(500),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (carrier_id) REFERENCES shipping_carriers(carrier_id)
);

-- Create indexes for performance
CREATE INDEX idx_shipping_zones_carrier_origin_dest ON shipping_zones(carrier_id, origin_zip_code, destination_zip_code);
CREATE INDEX idx_shipping_rates_carrier_service ON shipping_rates(carrier_id, service_id);
CREATE INDEX idx_shipping_rates_weight ON shipping_rates(weight_lbs);
CREATE INDEX idx_shipments_tracking_number ON shipments(tracking_number);
CREATE INDEX idx_shipments_status ON shipments(shipment_status);
CREATE INDEX idx_shipments_created_at ON shipments(created_at);
CREATE INDEX idx_tracking_events_shipment ON tracking_events(shipment_id);
CREATE INDEX idx_tracking_events_timestamp ON tracking_events(event_timestamp);
CREATE INDEX idx_rate_comparison_package ON rate_comparison_results(package_id);
CREATE INDEX idx_address_validation_zip ON address_validation_results(validated_zip_code);
CREATE INDEX idx_shipping_adjustments_shipment ON shipping_adjustments(shipment_id);
CREATE INDEX idx_shipping_analytics_date ON shipping_analytics(analytics_date);
CREATE INDEX idx_api_rate_request_log_carrier ON api_rate_request_log(carrier_id, request_timestamp);
