-- Electricity Cost Intelligence and Solar Rebate Database Schema
-- Compatible with PostgreSQL
-- Production schema for electricity cost intelligence and solar rebate system

-- States Table
-- Stores U.S. state information
CREATE TABLE states (
    state_id VARCHAR(2) PRIMARY KEY,  -- Two-letter state code (e.g., 'CA', 'NY')
    state_name VARCHAR(100) NOT NULL,
    state_full_name VARCHAR(100),
    region VARCHAR(50),  -- 'Northeast', 'South', 'Midwest', 'West'
    division VARCHAR(50),  -- Census division
    timezone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Counties Table
-- Stores county information for geographic rate areas
CREATE TABLE counties (
    county_id VARCHAR(255) PRIMARY KEY,
    state_id VARCHAR(2) NOT NULL,
    county_name VARCHAR(100) NOT NULL,
    county_fips_code VARCHAR(5),  -- 5-digit FIPS code
    county_seat VARCHAR(100),
    population INTEGER,
    area_sq_miles NUMERIC(10, 2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- Zip Codes Table
-- Stores zip code information for location-based rate queries
CREATE TABLE zip_codes (
    zip_code VARCHAR(10) PRIMARY KEY,
    state_id VARCHAR(2) NOT NULL,
    county_id VARCHAR(255),
    city VARCHAR(100),
    latitude NUMERIC(10, 7),  -- WGS84
    longitude NUMERIC(10, 7),  -- WGS84
    timezone VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (county_id) REFERENCES counties(county_id)
);

-- Utility Companies Table
-- Stores electric utility company information
CREATE TABLE utility_companies (
    utility_id VARCHAR(255) PRIMARY KEY,
    utility_name VARCHAR(255) NOT NULL,
    utility_display_name VARCHAR(255),
    utility_type VARCHAR(50),  -- 'Investor-Owned', 'Municipal', 'Cooperative', 'Federal', 'Power Marketer'
    state_id VARCHAR(2) NOT NULL,
    service_territory_description TEXT,
    eia_utility_id VARCHAR(50),  -- EIA Form 861 utility identifier
    openei_utility_id VARCHAR(50),  -- OpenEI utility identifier
    website_url VARCHAR(500),
    customer_service_phone VARCHAR(50),
    total_customers INTEGER,
    total_mwh_sold NUMERIC(15, 2),
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- Rate Codes Table
-- Stores rate code classifications and categories
CREATE TABLE rate_codes (
    rate_code_id VARCHAR(255) PRIMARY KEY,
    rate_code VARCHAR(100) NOT NULL,
    rate_code_description TEXT,
    rate_code_category VARCHAR(100),  -- 'Residential', 'Commercial', 'Industrial', 'Agricultural', 'Lighting'
    sector VARCHAR(50),  -- 'Residential', 'Commercial', 'Industrial', 'Lighting'
    rate_structure_type VARCHAR(100),  -- 'Flat', 'Tiered', 'Time-of-Use', 'Demand', 'Hybrid'
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rate Structures Table
-- Stores detailed rate structure information
CREATE TABLE rate_structures (
    rate_structure_id VARCHAR(255) PRIMARY KEY,
    utility_id VARCHAR(255) NOT NULL,
    rate_code_id VARCHAR(255) NOT NULL,
    rate_name VARCHAR(255) NOT NULL,
    rate_description TEXT,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    approval_status VARCHAR(50),  -- 'Approved', 'Pending', 'Proposed', 'Expired'
    regulatory_authority VARCHAR(255),  -- State PUC/PSC
    tariff_filing_number VARCHAR(100),
    is_current BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utility_id) REFERENCES utility_companies(utility_id),
    FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id)
);

-- Electricity Rates Table
-- Core table storing electricity rate pricing information
CREATE TABLE electricity_rates (
    rate_id VARCHAR(255) PRIMARY KEY,
    rate_structure_id VARCHAR(255) NOT NULL,
    utility_id VARCHAR(255) NOT NULL,
    rate_code_id VARCHAR(255) NOT NULL,
    state_id VARCHAR(2) NOT NULL,
    rate_type VARCHAR(50),  -- 'Residential', 'Commercial', 'Industrial', 'Lighting'
    billing_period VARCHAR(50),  -- 'Monthly', 'Daily', 'Hourly'
    fixed_charge_usd NUMERIC(10, 4),  -- Monthly fixed charge
    fixed_charge_unit VARCHAR(50),  -- 'per_month', 'per_day', 'per_customer'
    energy_charge_usd_per_kwh NUMERIC(10, 6),  -- Base energy charge per kWh
    demand_charge_usd_per_kw NUMERIC(10, 4),  -- Demand charge per kW
    minimum_charge_usd NUMERIC(10, 4),
    currency VARCHAR(10) DEFAULT 'USD',
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(100),  -- 'openei', 'eia', 'state_commission', 'poweroutage_us'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rate_structure_id) REFERENCES rate_structures(rate_structure_id),
    FOREIGN KEY (utility_id) REFERENCES utility_companies(utility_id),
    FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- Tiered Rate Tiers Table
-- Stores tiered rate structure tiers (e.g., Tier 1: 0-500 kWh, Tier 2: 501-1000 kWh)
CREATE TABLE tiered_rate_tiers (
    tier_id VARCHAR(255) PRIMARY KEY,
    rate_structure_id VARCHAR(255) NOT NULL,
    tier_number INTEGER NOT NULL,
    tier_name VARCHAR(100),
    tier_start_kwh NUMERIC(10, 2),
    tier_end_kwh NUMERIC(10, 2),  -- NULL for unlimited tier
    energy_charge_usd_per_kwh NUMERIC(10, 6) NOT NULL,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rate_structure_id) REFERENCES rate_structures(rate_structure_id)
);

-- Time-of-Use Rate Periods Table
-- Stores time-of-use rate periods (e.g., Peak, Off-Peak, Super Off-Peak)
CREATE TABLE time_of_use_periods (
    tou_period_id VARCHAR(255) PRIMARY KEY,
    rate_structure_id VARCHAR(255) NOT NULL,
    period_name VARCHAR(100) NOT NULL,  -- 'Peak', 'Off-Peak', 'Super Off-Peak', 'Mid-Peak'
    period_start_time TIME NOT NULL,
    period_end_time TIME NOT NULL,
    day_of_week VARCHAR(20),  -- 'Monday', 'Weekday', 'Weekend', 'All'
    season VARCHAR(50),  -- 'Summer', 'Winter', 'Spring', 'Fall', 'All'
    energy_charge_usd_per_kwh NUMERIC(10, 6) NOT NULL,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rate_structure_id) REFERENCES rate_structures(rate_structure_id)
);

-- Geographic Rate Areas Table
-- Maps geographic areas to specific rate structures
CREATE TABLE geographic_rate_areas (
    rate_area_id VARCHAR(255) PRIMARY KEY,
    rate_structure_id VARCHAR(255) NOT NULL,
    state_id VARCHAR(2),
    county_id VARCHAR(255),
    zip_code VARCHAR(10),
    service_area_name VARCHAR(255),
    service_area_description TEXT,
    latitude_min NUMERIC(10, 7),  -- Bounding box
    latitude_max NUMERIC(10, 7),
    longitude_min NUMERIC(10, 7),
    longitude_max NUMERIC(10, 7),
    effective_date DATE NOT NULL,
    expiration_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rate_structure_id) REFERENCES rate_structures(rate_structure_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (county_id) REFERENCES counties(county_id),
    FOREIGN KEY (zip_code) REFERENCES zip_codes(zip_code)
);

-- Historical Electricity Rates Table
-- Tracks rate changes over time for trend analysis
CREATE TABLE historical_electricity_rates (
    historical_rate_id VARCHAR(255) PRIMARY KEY,
    rate_id VARCHAR(255) NOT NULL,
    utility_id VARCHAR(255) NOT NULL,
    rate_code_id VARCHAR(255) NOT NULL,
    state_id VARCHAR(2) NOT NULL,
    fixed_charge_usd NUMERIC(10, 4),
    energy_charge_usd_per_kwh NUMERIC(10, 6),
    demand_charge_usd_per_kw NUMERIC(10, 4),
    effective_date DATE NOT NULL,
    change_type VARCHAR(50),  -- 'rate_increase', 'rate_decrease', 'new_rate', 'rate_expired'
    change_percentage NUMERIC(8, 4),
    change_amount NUMERIC(10, 6),
    change_reason TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rate_id) REFERENCES electricity_rates(rate_id),
    FOREIGN KEY (utility_id) REFERENCES utility_companies(utility_id),
    FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- Federal Incentives Table
-- Stores federal solar and renewable energy incentives
CREATE TABLE federal_incentives (
    federal_incentive_id VARCHAR(255) PRIMARY KEY,
    incentive_name VARCHAR(255) NOT NULL,
    incentive_type VARCHAR(50),  -- 'Tax Credit', 'Rebate', 'Grant', 'Loan', 'Performance-Based'
    incentive_description TEXT,
    eligible_technologies TEXT[],  -- Array of eligible technologies
    eligible_sectors TEXT[],  -- Array of eligible sectors
    incentive_amount_usd NUMERIC(15, 2),
    incentive_percentage NUMERIC(5, 2),  -- Percentage-based incentives
    incentive_unit VARCHAR(50),  -- 'per_watt', 'per_system', 'percentage', 'fixed_amount'
    maximum_incentive_usd NUMERIC(15, 2),
    minimum_system_size_kw NUMERIC(10, 2),
    maximum_system_size_kw NUMERIC(10, 2),
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    program_website_url VARCHAR(500),
    program_contact_info TEXT,
    data_source VARCHAR(100),  -- 'doe', 'dsire', 'irs'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- State Incentives Table
-- Stores state-level solar and renewable energy incentives
CREATE TABLE state_incentives (
    state_incentive_id VARCHAR(255) PRIMARY KEY,
    state_id VARCHAR(2) NOT NULL,
    incentive_name VARCHAR(255) NOT NULL,
    incentive_type VARCHAR(50),  -- 'Tax Credit', 'Rebate', 'Grant', 'Loan', 'Performance-Based', 'Property Tax Exemption'
    incentive_description TEXT,
    eligible_technologies TEXT[],
    eligible_sectors TEXT[],
    incentive_amount_usd NUMERIC(15, 2),
    incentive_percentage NUMERIC(5, 2),
    incentive_unit VARCHAR(50),
    maximum_incentive_usd NUMERIC(15, 2),
    minimum_system_size_kw NUMERIC(10, 2),
    maximum_system_size_kw NUMERIC(10, 2),
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    program_website_url VARCHAR(500),
    program_contact_info TEXT,
    regulatory_authority VARCHAR(255),  -- State agency administering program
    data_source VARCHAR(100),  -- 'dsire', 'state_commission', 'state_energy_office'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- Utility Incentives Table
-- Stores utility-level solar and renewable energy incentives
CREATE TABLE utility_incentives (
    utility_incentive_id VARCHAR(255) PRIMARY KEY,
    utility_id VARCHAR(255) NOT NULL,
    state_id VARCHAR(2) NOT NULL,
    incentive_name VARCHAR(255) NOT NULL,
    incentive_type VARCHAR(50),  -- 'Rebate', 'Performance-Based', 'Net Metering', 'Feed-in Tariff', 'Buy-Back Program'
    incentive_description TEXT,
    eligible_technologies TEXT[],
    eligible_sectors TEXT[],
    incentive_amount_usd NUMERIC(15, 2),
    incentive_percentage NUMERIC(5, 2),
    incentive_unit VARCHAR(50),  -- 'per_watt', 'per_kwh', 'percentage', 'fixed_amount'
    maximum_incentive_usd NUMERIC(15, 2),
    minimum_system_size_kw NUMERIC(10, 2),
    maximum_system_size_kw NUMERIC(10, 2),
    net_metering_capacity_limit_kw NUMERIC(10, 2),  -- For net metering programs
    feed_in_tariff_rate_usd_per_kwh NUMERIC(10, 6),  -- For feed-in tariff programs
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    program_website_url VARCHAR(500),
    program_contact_info TEXT,
    data_source VARCHAR(100),  -- 'dsire', 'utility_website', 'state_commission'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utility_id) REFERENCES utility_companies(utility_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- Solar Rebate Aggregations Table
-- Aggregates all available rebates for a given location/utility
CREATE TABLE solar_rebate_aggregations (
    aggregation_id VARCHAR(255) PRIMARY KEY,
    state_id VARCHAR(2) NOT NULL,
    utility_id VARCHAR(255),
    zip_code VARCHAR(10),
    total_federal_incentives_usd NUMERIC(15, 2),
    total_state_incentives_usd NUMERIC(15, 2),
    total_utility_incentives_usd NUMERIC(15, 2),
    total_combined_incentives_usd NUMERIC(15, 2),
    federal_incentive_count INTEGER DEFAULT 0,
    state_incentive_count INTEGER DEFAULT 0,
    utility_incentive_count INTEGER DEFAULT 0,
    total_incentive_count INTEGER DEFAULT 0,
    calculation_date DATE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (utility_id) REFERENCES utility_companies(utility_id),
    FOREIGN KEY (zip_code) REFERENCES zip_codes(zip_code)
);

-- Rate Comparison Matrix Table
-- Compares rates across utilities, states, and rate codes
CREATE TABLE rate_comparison_matrix (
    comparison_id VARCHAR(255) PRIMARY KEY,
    rate_id_1 VARCHAR(255) NOT NULL,
    rate_id_2 VARCHAR(255) NOT NULL,
    comparison_metric VARCHAR(100),  -- 'price_per_kwh', 'total_monthly_cost', 'cost_efficiency'
    usage_kwh_per_month NUMERIC(10, 2),  -- Usage level for comparison
    rate_1_cost_usd NUMERIC(15, 2),
    rate_2_cost_usd NUMERIC(15, 2),
    cost_difference_usd NUMERIC(15, 2),
    cost_difference_percentage NUMERIC(8, 4),
    comparison_date DATE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rate_id_1) REFERENCES electricity_rates(rate_id),
    FOREIGN KEY (rate_id_2) REFERENCES electricity_rates(rate_id)
);

-- Data Extraction Log Table
-- Tracks data extraction operations from various sources
CREATE TABLE data_extraction_log (
    extraction_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(100) NOT NULL,  -- References source_id from data_resources.json
    source_name VARCHAR(255) NOT NULL,
    extraction_type VARCHAR(50),  -- 'api', 'web_scrape', 'file_download', 'manual'
    extraction_status VARCHAR(50),  -- 'success', 'failed', 'partial', 'in_progress'
    records_extracted INTEGER DEFAULT 0,
    records_loaded INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    extraction_start_time TIMESTAMP NOT NULL,
    extraction_end_time TIMESTAMP,
    extraction_duration_seconds INTEGER,
    error_message TEXT,
    extraction_metadata JSON,  -- Additional extraction metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_electricity_rates_utility_id ON electricity_rates(utility_id);
CREATE INDEX idx_electricity_rates_rate_code_id ON electricity_rates(rate_code_id);
CREATE INDEX idx_electricity_rates_state_id ON electricity_rates(state_id);
CREATE INDEX idx_electricity_rates_effective_date ON electricity_rates(effective_date);
CREATE INDEX idx_electricity_rates_is_current ON electricity_rates(is_current);

CREATE INDEX idx_rate_structures_utility_id ON rate_structures(utility_id);
CREATE INDEX idx_rate_structures_rate_code_id ON rate_structures(rate_code_id);
CREATE INDEX idx_rate_structures_effective_date ON rate_structures(effective_date);

CREATE INDEX idx_geographic_rate_areas_state_id ON geographic_rate_areas(state_id);
CREATE INDEX idx_geographic_rate_areas_zip_code ON geographic_rate_areas(zip_code);
CREATE INDEX idx_geographic_rate_areas_rate_structure_id ON geographic_rate_areas(rate_structure_id);

CREATE INDEX idx_utility_companies_state_id ON utility_companies(state_id);
CREATE INDEX idx_utility_companies_eia_utility_id ON utility_companies(eia_utility_id);

CREATE INDEX idx_state_incentives_state_id ON state_incentives(state_id);
CREATE INDEX idx_state_incentives_is_active ON state_incentives(is_active);

CREATE INDEX idx_utility_incentives_utility_id ON utility_incentives(utility_id);
CREATE INDEX idx_utility_incentives_state_id ON utility_incentives(state_id);
CREATE INDEX idx_utility_incentives_is_active ON utility_incentives(is_active);

CREATE INDEX idx_solar_rebate_aggregations_state_id ON solar_rebate_aggregations(state_id);
CREATE INDEX idx_solar_rebate_aggregations_utility_id ON solar_rebate_aggregations(utility_id);
CREATE INDEX idx_solar_rebate_aggregations_zip_code ON solar_rebate_aggregations(zip_code);

CREATE INDEX idx_historical_electricity_rates_rate_id ON historical_electricity_rates(rate_id);
CREATE INDEX idx_historical_electricity_rates_effective_date ON historical_electricity_rates(effective_date);
CREATE INDEX idx_historical_electricity_rates_utility_id ON historical_electricity_rates(utility_id);

CREATE INDEX idx_zip_codes_state_id ON zip_codes(state_id);
CREATE INDEX idx_zip_codes_county_id ON zip_codes(county_id);
CREATE INDEX idx_zip_codes_latitude_longitude ON zip_codes(latitude, longitude);

CREATE INDEX idx_data_extraction_log_source_id ON data_extraction_log(source_id);
CREATE INDEX idx_data_extraction_log_extraction_start_time ON data_extraction_log(extraction_start_time);
