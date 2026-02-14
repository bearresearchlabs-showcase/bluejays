# Database Schema Documentation - db-15

**Created:** 2026-02-04

## Schema Overview

The Electricity Cost and Solar Rebate Database consists of 18 main tables designed to store comprehensive electricity rate data, utility information, solar rebates, and geographic data across the United States.

## Tables

### states
Stores U.S. state information for geographic organization.

**Key Columns:**
- `state_id` (VARCHAR(2), PK) - Two-letter state code (e.g., 'CA', 'NY')
- `state_name` (VARCHAR(100)) - State name
- `state_full_name` (VARCHAR(100)) - Full state name
- `region` (VARCHAR(50)) - Census region ('Northeast', 'South', 'Midwest', 'West')
- `division` (VARCHAR(50)) - Census division
- `timezone` (VARCHAR(50)) - State timezone
- `is_active` (BOOLEAN) - Active state flag

### counties
Stores county information for geographic rate areas.

**Key Columns:**
- `county_id` (VARCHAR(255), PK)
- `state_id` (VARCHAR(2), FK) - References states
- `county_name` (VARCHAR(100)) - County name
- `county_fips_code` (VARCHAR(5)) - 5-digit FIPS code
- `county_seat` (VARCHAR(100)) - County seat city
- `population` (INTEGER) - County population
- `area_sq_miles` (NUMERIC(10, 2)) - County area

### zip_codes
Stores zip code information for location-based rate queries.

**Key Columns:**
- `zip_code` (VARCHAR(10), PK)
- `state_id` (VARCHAR(2), FK) - References states
- `county_id` (VARCHAR(255), FK) - References counties
- `city` (VARCHAR(100)) - City name
- `latitude` (NUMERIC(10, 7)) - WGS84 latitude
- `longitude` (NUMERIC(10, 7)) - WGS84 longitude
- `timezone` (VARCHAR(50)) - Zip code timezone

### utility_companies
Stores electric utility company information (3,700+ utilities).

**Key Columns:**
- `utility_id` (VARCHAR(255), PK)
- `utility_name` (VARCHAR(255)) - Utility company name
- `utility_display_name` (VARCHAR(255)) - Display name
- `utility_type` (VARCHAR(50)) - 'Investor-Owned', 'Municipal', 'Cooperative', 'Federal', 'Power Marketer'
- `state_id` (VARCHAR(2), FK) - References states
- `service_territory_description` (TEXT) - Service area description
- `eia_utility_id` (VARCHAR(50)) - EIA Form 861 utility identifier
- `openei_utility_id` (VARCHAR(50)) - OpenEI utility identifier
- `website_url` (VARCHAR(500)) - Utility website
- `total_customers` (INTEGER) - Total customer count
- `total_mwh_sold` (NUMERIC(15, 2)) - Total MWh sold

### rate_codes
Stores rate code classifications and categories.

**Key Columns:**
- `rate_code_id` (VARCHAR(255), PK)
- `rate_code` (VARCHAR(100)) - Rate code identifier
- `rate_code_description` (TEXT) - Rate code description
- `rate_code_category` (VARCHAR(100)) - 'Residential', 'Commercial', 'Industrial', 'Agricultural', 'Lighting'
- `sector` (VARCHAR(50)) - 'Residential', 'Commercial', 'Industrial', 'Lighting'
- `rate_structure_type` (VARCHAR(100)) - 'Flat', 'Tiered', 'Time-of-Use', 'Demand', 'Hybrid'
- `is_active` (BOOLEAN) - Active rate code flag

### rate_structures
Stores detailed rate structure information.

**Key Columns:**
- `rate_structure_id` (VARCHAR(255), PK)
- `utility_id` (VARCHAR(255), FK) - References utility_companies
- `rate_code_id` (VARCHAR(255), FK) - References rate_codes
- `rate_name` (VARCHAR(255)) - Rate structure name
- `rate_description` (TEXT) - Rate structure description
- `effective_date` (DATE) - Rate effective date
- `expiration_date` (DATE) - Rate expiration date
- `approval_status` (VARCHAR(50)) - 'Approved', 'Pending', 'Proposed', 'Expired'
- `regulatory_authority` (VARCHAR(255)) - State PUC/PSC
- `tariff_filing_number` (VARCHAR(100)) - Tariff filing number
- `is_current` (BOOLEAN) - Current rate flag

### electricity_rates
Core table storing electricity rate pricing information.

**Key Columns:**
- `rate_id` (VARCHAR(255), PK)
- `rate_structure_id` (VARCHAR(255), FK) - References rate_structures
- `utility_id` (VARCHAR(255), FK) - References utility_companies
- `rate_code_id` (VARCHAR(255), FK) - References rate_codes
- `state_id` (VARCHAR(2), FK) - References states
- `rate_type` (VARCHAR(50)) - 'Residential', 'Commercial', 'Industrial', 'Lighting'
- `billing_period` (VARCHAR(50)) - 'Monthly', 'Daily', 'Hourly'
- `fixed_charge_usd` (NUMERIC(10, 4)) - Monthly fixed charge
- `energy_charge_usd_per_kwh` (NUMERIC(10, 6)) - Base energy charge per kWh
- `demand_charge_usd_per_kw` (NUMERIC(10, 4)) - Demand charge per kW
- `minimum_charge_usd` (NUMERIC(10, 4)) - Minimum monthly charge
- `currency` (VARCHAR(10)) - Currency code (default 'USD')
- `effective_date` (DATE) - Rate effective date
- `expiration_date` (DATE) - Rate expiration date
- `is_current` (BOOLEAN) - Current rate flag
- `data_source` (VARCHAR(100)) - 'openei', 'eia', 'state_commission', 'poweroutage_us'

### tiered_rate_tiers
Stores tiered rate structure tiers (e.g., Tier 1: 0-500 kWh, Tier 2: 501-1000 kWh).

**Key Columns:**
- `tier_id` (VARCHAR(255), PK)
- `rate_structure_id` (VARCHAR(255), FK) - References rate_structures
- `tier_number` (INTEGER) - Tier number (1, 2, 3, etc.)
- `tier_name` (VARCHAR(100)) - Tier name
- `tier_start_kwh` (NUMERIC(10, 2)) - Tier start kWh
- `tier_end_kwh` (NUMERIC(10, 2)) - Tier end kWh (NULL for unlimited)
- `energy_charge_usd_per_kwh` (NUMERIC(10, 6)) - Energy charge for this tier
- `effective_date` (DATE) - Tier effective date
- `expiration_date` (DATE) - Tier expiration date

### time_of_use_periods
Stores time-of-use rate periods (e.g., Peak, Off-Peak, Super Off-Peak).

**Key Columns:**
- `tou_period_id` (VARCHAR(255), PK)
- `rate_structure_id` (VARCHAR(255), FK) - References rate_structures
- `period_name` (VARCHAR(100)) - 'Peak', 'Off-Peak', 'Super Off-Peak', 'Mid-Peak'
- `period_start_time` (TIME) - Period start time
- `period_end_time` (TIME) - Period end time
- `day_of_week` (VARCHAR(20)) - 'Monday', 'Weekday', 'Weekend', 'All'
- `season` (VARCHAR(50)) - 'Summer', 'Winter', 'Spring', 'Fall', 'All'
- `energy_charge_usd_per_kwh` (NUMERIC(10, 6)) - Energy charge for this period
- `effective_date` (DATE) - Period effective date
- `expiration_date` (DATE) - Period expiration date

### geographic_rate_areas
Maps geographic areas to specific rate structures.

**Key Columns:**
- `rate_area_id` (VARCHAR(255), PK)
- `rate_structure_id` (VARCHAR(255), FK) - References rate_structures
- `state_id` (VARCHAR(2), FK) - References states
- `county_id` (VARCHAR(255), FK) - References counties
- `zip_code` (VARCHAR(10), FK) - References zip_codes
- `service_area_name` (VARCHAR(255)) - Service area name
- `service_area_description` (TEXT) - Service area description
- `latitude_min`, `latitude_max` (NUMERIC(10, 7)) - Bounding box
- `longitude_min`, `longitude_max` (NUMERIC(10, 7)) - Bounding box
- `effective_date` (DATE) - Area effective date
- `expiration_date` (DATE) - Area expiration date

### historical_electricity_rates
Tracks rate changes over time for trend analysis.

**Key Columns:**
- `historical_rate_id` (VARCHAR(255), PK)
- `rate_id` (VARCHAR(255), FK) - References electricity_rates
- `utility_id` (VARCHAR(255), FK) - References utility_companies
- `rate_code_id` (VARCHAR(255), FK) - References rate_codes
- `state_id` (VARCHAR(2), FK) - References states
- `fixed_charge_usd` (NUMERIC(10, 4)) - Historical fixed charge
- `energy_charge_usd_per_kwh` (NUMERIC(10, 6)) - Historical energy charge
- `demand_charge_usd_per_kw` (NUMERIC(10, 4)) - Historical demand charge
- `effective_date` (DATE) - Historical rate effective date
- `change_type` (VARCHAR(50)) - 'rate_increase', 'rate_decrease', 'new_rate', 'rate_expired'
- `change_percentage` (NUMERIC(8, 4)) - Rate change percentage
- `change_amount` (NUMERIC(10, 6)) - Rate change amount
- `change_reason` (TEXT) - Reason for rate change

### federal_incentives
Stores federal solar and renewable energy incentives.

**Key Columns:**
- `federal_incentive_id` (VARCHAR(255), PK)
- `incentive_name` (VARCHAR(255)) - Incentive name
- `incentive_type` (VARCHAR(50)) - 'Tax Credit', 'Rebate', 'Grant', 'Loan', 'Performance-Based'
- `incentive_description` (TEXT) - Incentive description
- `eligible_technologies` (TEXT[]) - Array of eligible technologies
- `eligible_sectors` (TEXT[]) - Array of eligible sectors
- `incentive_amount_usd` (NUMERIC(15, 2)) - Incentive amount
- `incentive_percentage` (NUMERIC(5, 2)) - Percentage-based incentive
- `incentive_unit` (VARCHAR(50)) - 'per_watt', 'per_system', 'percentage', 'fixed_amount'
- `maximum_incentive_usd` (NUMERIC(15, 2)) - Maximum incentive amount
- `minimum_system_size_kw` (NUMERIC(10, 2)) - Minimum system size
- `maximum_system_size_kw` (NUMERIC(10, 2)) - Maximum system size
- `effective_date` (DATE) - Incentive effective date
- `expiration_date` (DATE) - Incentive expiration date
- `is_active` (BOOLEAN) - Active incentive flag
- `program_website_url` (VARCHAR(500)) - Program website
- `data_source` (VARCHAR(100)) - 'doe', 'dsire', 'irs'

### state_incentives
Stores state-level solar and renewable energy incentives.

**Key Columns:**
- `state_incentive_id` (VARCHAR(255), PK)
- `state_id` (VARCHAR(2), FK) - References states
- `incentive_name` (VARCHAR(255)) - Incentive name
- `incentive_type` (VARCHAR(50)) - 'Tax Credit', 'Rebate', 'Grant', 'Loan', 'Performance-Based', 'Property Tax Exemption'
- `incentive_description` (TEXT) - Incentive description
- `eligible_technologies` (TEXT[]) - Array of eligible technologies
- `eligible_sectors` (TEXT[]) - Array of eligible sectors
- `incentive_amount_usd` (NUMERIC(15, 2)) - Incentive amount
- `incentive_percentage` (NUMERIC(5, 2)) - Percentage-based incentive
- `incentive_unit` (VARCHAR(50)) - 'per_watt', 'per_system', 'percentage', 'fixed_amount'
- `maximum_incentive_usd` (NUMERIC(15, 2)) - Maximum incentive amount
- `minimum_system_size_kw` (NUMERIC(10, 2)) - Minimum system size
- `maximum_system_size_kw` (NUMERIC(10, 2)) - Maximum system size
- `effective_date` (DATE) - Incentive effective date
- `expiration_date` (DATE) - Incentive expiration date
- `is_active` (BOOLEAN) - Active incentive flag
- `program_website_url` (VARCHAR(500)) - Program website
- `regulatory_authority` (VARCHAR(255)) - State agency administering program
- `data_source` (VARCHAR(100)) - 'dsire', 'state_commission', 'state_energy_office'

### utility_incentives
Stores utility-level solar and renewable energy incentives.

**Key Columns:**
- `utility_incentive_id` (VARCHAR(255), PK)
- `utility_id` (VARCHAR(255), FK) - References utility_companies
- `state_id` (VARCHAR(2), FK) - References states
- `incentive_name` (VARCHAR(255)) - Incentive name
- `incentive_type` (VARCHAR(50)) - 'Rebate', 'Performance-Based', 'Net Metering', 'Feed-in Tariff', 'Buy-Back Program'
- `incentive_description` (TEXT) - Incentive description
- `eligible_technologies` (TEXT[]) - Array of eligible technologies
- `eligible_sectors` (TEXT[]) - Array of eligible sectors
- `incentive_amount_usd` (NUMERIC(15, 2)) - Incentive amount
- `incentive_percentage` (NUMERIC(5, 2)) - Percentage-based incentive
- `incentive_unit` (VARCHAR(50)) - 'per_watt', 'per_kwh', 'percentage', 'fixed_amount'
- `maximum_incentive_usd` (NUMERIC(15, 2)) - Maximum incentive amount
- `minimum_system_size_kw` (NUMERIC(10, 2)) - Minimum system size
- `maximum_system_size_kw` (NUMERIC(10, 2)) - Maximum system size
- `net_metering_capacity_limit_kw` (NUMERIC(10, 2)) - Net metering capacity limit
- `feed_in_tariff_rate_usd_per_kwh` (NUMERIC(10, 6)) - Feed-in tariff rate
- `effective_date` (DATE) - Incentive effective date
- `expiration_date` (DATE) - Incentive expiration date
- `is_active` (BOOLEAN) - Active incentive flag
- `program_website_url` (VARCHAR(500)) - Program website
- `data_source` (VARCHAR(100)) - 'dsire', 'utility_website', 'state_commission'

### solar_rebate_aggregations
Aggregates all available rebates for a given location/utility.

**Key Columns:**
- `aggregation_id` (VARCHAR(255), PK)
- `state_id` (VARCHAR(2), FK) - References states
- `utility_id` (VARCHAR(255), FK) - References utility_companies
- `zip_code` (VARCHAR(10), FK) - References zip_codes
- `total_federal_incentives_usd` (NUMERIC(15, 2)) - Total federal incentives
- `total_state_incentives_usd` (NUMERIC(15, 2)) - Total state incentives
- `total_utility_incentives_usd` (NUMERIC(15, 2)) - Total utility incentives
- `total_combined_incentives_usd` (NUMERIC(15, 2)) - Total combined incentives
- `federal_incentive_count` (INTEGER) - Number of federal incentives
- `state_incentive_count` (INTEGER) - Number of state incentives
- `utility_incentive_count` (INTEGER) - Number of utility incentives
- `total_incentive_count` (INTEGER) - Total incentive count
- `calculation_date` (DATE) - Aggregation calculation date

### rate_comparison_matrix
Compares rates across utilities, states, and rate codes.

**Key Columns:**
- `comparison_id` (VARCHAR(255), PK)
- `rate_id_1` (VARCHAR(255), FK) - References electricity_rates
- `rate_id_2` (VARCHAR(255), FK) - References electricity_rates
- `comparison_metric` (VARCHAR(100)) - 'price_per_kwh', 'total_monthly_cost', 'cost_efficiency'
- `usage_kwh_per_month` (NUMERIC(10, 2)) - Usage level for comparison
- `rate_1_cost_usd` (NUMERIC(15, 2)) - Rate 1 cost
- `rate_2_cost_usd` (NUMERIC(15, 2)) - Rate 2 cost
- `cost_difference_usd` (NUMERIC(15, 2)) - Cost difference
- `cost_difference_percentage` (NUMERIC(8, 4)) - Cost difference percentage
- `comparison_date` (DATE) - Comparison date

### data_extraction_log
Tracks data extraction operations from various sources.

**Key Columns:**
- `extraction_id` (VARCHAR(255), PK)
- `source_id` (VARCHAR(100)) - References source_id from data_resources.json
- `source_name` (VARCHAR(255)) - Source name
- `extraction_type` (VARCHAR(50)) - 'api', 'web_scrape', 'file_download', 'manual'
- `extraction_status` (VARCHAR(50)) - 'success', 'failed', 'partial', 'in_progress'
- `records_extracted` (INTEGER) - Records extracted
- `records_loaded` (INTEGER) - Records loaded
- `records_failed` (INTEGER) - Records failed
- `extraction_start_time` (TIMESTAMP_NTZ) - Extraction start time
- `extraction_end_time` (TIMESTAMP_NTZ) - Extraction end time
- `extraction_duration_seconds` (INTEGER) - Extraction duration
- `error_message` (TEXT) - Error message if failed
- `extraction_metadata` (JSON) - Additional extraction metadata

## Indexes

The schema includes comprehensive indexes for performance optimization:

- Indexes on foreign keys (utility_id, rate_code_id, state_id, etc.)
- Indexes on date fields (effective_date, expiration_date)
- Indexes on geographic fields (zip_code, latitude, longitude)
- Indexes on status fields (is_current, is_active)
- Composite indexes for common query patterns

## Relationships

- **States** → **Counties** → **Zip Codes**: Geographic hierarchy
- **States** → **Utility Companies**: Utilities operate in states
- **Utility Companies** → **Rate Structures** → **Electricity Rates**: Rate organization
- **Rate Codes** → **Rate Structures**: Rate code classification
- **Rate Structures** → **Tiered Rate Tiers**: Tiered rate details
- **Rate Structures** → **Time-of-Use Periods**: TOU rate details
- **Geographic Rate Areas** → **Rate Structures**: Geographic mapping
- **Electricity Rates** → **Historical Electricity Rates**: Rate history
- **States** → **State Incentives**: State-level incentives
- **Utility Companies** → **Utility Incentives**: Utility-level incentives
- **Solar Rebate Aggregations**: Aggregates federal, state, and utility incentives

---
**Last Updated:** 2026-02-04
