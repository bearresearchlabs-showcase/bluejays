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
    temperature_extreme_risk NUMERIC(10, 2),  -- Temperature extreme risk score
    cumulative_precipitation_risk NUMERIC(10, 2),  -- Total precipitation risk score
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
    overall_risk_score NUMERIC(5, 2),  -- Overall risk score (0-100)
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
