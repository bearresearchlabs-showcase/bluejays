# Data Dictionary - db-15

**Created:** 2026-02-04

## Overview

This data dictionary provides comprehensive column-level documentation for all tables in the Electricity Cost and Solar Rebate Database.

## Tables

### states

Stores U.S. state information for geographic organization.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| state_id | VARCHAR(2) | PRIMARY KEY | Two-letter state code (e.g., 'CA', 'NY', 'TX') |
| state_name | VARCHAR(100) | NOT NULL | State name (e.g., 'California', 'New York') |
| state_full_name | VARCHAR(100) | | Full state name with official designation |
| region | VARCHAR(50) | | Census region ('Northeast', 'South', 'Midwest', 'West') |
| division | VARCHAR(50) | | Census division within region |
| timezone | VARCHAR(50) | | Primary timezone for the state |
| is_active | BOOLEAN | DEFAULT TRUE | Whether state is currently active |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### counties

Stores county information for geographic rate areas.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| county_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for county |
| state_id | VARCHAR(2) | NOT NULL, FK → states | Two-letter state code |
| county_name | VARCHAR(100) | NOT NULL | County name |
| county_fips_code | VARCHAR(5) | | 5-digit FIPS code (state + county) |
| county_seat | VARCHAR(100) | | County seat city name |
| population | INTEGER | | County population (latest census) |
| area_sq_miles | NUMERIC(10, 2) | | County area in square miles |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### zip_codes

Stores zip code information for location-based rate queries.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| zip_code | VARCHAR(10) | PRIMARY KEY | Zip code (5-digit or 9-digit with hyphen) |
| state_id | VARCHAR(2) | NOT NULL, FK → states | Two-letter state code |
| county_id | VARCHAR(255) | FK → counties | County identifier |
| city | VARCHAR(100) | | City name for zip code |
| latitude | NUMERIC(10, 7) | | WGS84 latitude coordinate |
| longitude | NUMERIC(10, 7) | | WGS84 longitude coordinate |
| timezone | VARCHAR(50) | | Timezone for zip code area |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### utility_companies

Stores electric utility company information (3,700+ utilities).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| utility_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for utility |
| utility_name | VARCHAR(255) | NOT NULL | Utility company name |
| utility_display_name | VARCHAR(255) | | Human-readable display name |
| utility_type | VARCHAR(50) | | Utility type ('Investor-Owned', 'Municipal', 'Cooperative', 'Federal', 'Power Marketer') |
| state_id | VARCHAR(2) | NOT NULL, FK → states | Primary state of operation |
| service_territory_description | TEXT | | Description of service territory |
| eia_utility_id | VARCHAR(50) | | EIA Form 861 utility identifier |
| openei_utility_id | VARCHAR(50) | | OpenEI utility identifier |
| website_url | VARCHAR(500) | | Utility company website URL |
| customer_service_phone | VARCHAR(50) | | Customer service phone number |
| total_customers | INTEGER | | Total number of customers |
| total_mwh_sold | NUMERIC(15, 2) | | Total MWh sold annually |
| is_active | BOOLEAN | DEFAULT TRUE | Whether utility is currently active |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### rate_codes

Stores rate code classifications and categories.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| rate_code_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for rate code |
| rate_code | VARCHAR(100) | NOT NULL | Rate code identifier (e.g., 'R-1', 'GS-1', 'E-1') |
| rate_code_description | TEXT | | Detailed description of rate code |
| rate_code_category | VARCHAR(100) | | Category ('Residential', 'Commercial', 'Industrial', 'Agricultural', 'Lighting') |
| sector | VARCHAR(50) | | Sector ('Residential', 'Commercial', 'Industrial', 'Lighting') |
| rate_structure_type | VARCHAR(100) | | Structure type ('Flat', 'Tiered', 'Time-of-Use', 'Demand', 'Hybrid') |
| is_active | BOOLEAN | DEFAULT TRUE | Whether rate code is currently active |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### rate_structures

Stores detailed rate structure information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| rate_structure_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for rate structure |
| utility_id | VARCHAR(255) | NOT NULL, FK → utility_companies | Utility company identifier |
| rate_code_id | VARCHAR(255) | NOT NULL, FK → rate_codes | Rate code identifier |
| rate_name | VARCHAR(255) | NOT NULL | Rate structure name |
| rate_description | TEXT | | Detailed rate structure description |
| effective_date | DATE | NOT NULL | Date rate structure becomes effective |
| expiration_date | DATE | | Date rate structure expires (NULL if ongoing) |
| approval_status | VARCHAR(50) | | Status ('Approved', 'Pending', 'Proposed', 'Expired') |
| regulatory_authority | VARCHAR(255) | | State PUC/PSC regulatory authority |
| tariff_filing_number | VARCHAR(100) | | Tariff filing number with regulatory authority |
| is_current | BOOLEAN | DEFAULT TRUE | Whether rate structure is currently active |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### electricity_rates

Core table storing electricity rate pricing information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| rate_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for rate |
| rate_structure_id | VARCHAR(255) | NOT NULL, FK → rate_structures | Rate structure identifier |
| utility_id | VARCHAR(255) | NOT NULL, FK → utility_companies | Utility company identifier |
| rate_code_id | VARCHAR(255) | NOT NULL, FK → rate_codes | Rate code identifier |
| state_id | VARCHAR(2) | NOT NULL, FK → states | State identifier |
| rate_type | VARCHAR(50) | | Rate type ('Residential', 'Commercial', 'Industrial', 'Lighting') |
| billing_period | VARCHAR(50) | | Billing period ('Monthly', 'Daily', 'Hourly') |
| fixed_charge_usd | NUMERIC(10, 4) | | Monthly fixed charge in USD |
| fixed_charge_unit | VARCHAR(50) | | Fixed charge unit ('per_month', 'per_day', 'per_customer') |
| energy_charge_usd_per_kwh | NUMERIC(10, 6) | | Base energy charge per kWh in USD |
| demand_charge_usd_per_kw | NUMERIC(10, 4) | | Demand charge per kW in USD |
| minimum_charge_usd | NUMERIC(10, 4) | | Minimum monthly charge in USD |
| currency | VARCHAR(10) | DEFAULT 'USD' | Currency code |
| effective_date | DATE | NOT NULL | Rate effective date |
| expiration_date | DATE | | Rate expiration date (NULL if ongoing) |
| is_current | BOOLEAN | DEFAULT TRUE | Whether rate is currently active |
| data_source | VARCHAR(100) | | Data source ('openei', 'eia', 'state_commission', 'poweroutage_us') |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### tiered_rate_tiers

Stores tiered rate structure tiers (e.g., Tier 1: 0-500 kWh, Tier 2: 501-1000 kWh).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| tier_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for tier |
| rate_structure_id | VARCHAR(255) | NOT NULL, FK → rate_structures | Rate structure identifier |
| tier_number | INTEGER | NOT NULL | Tier number (1, 2, 3, etc.) |
| tier_name | VARCHAR(100) | | Tier name or description |
| tier_start_kwh | NUMERIC(10, 2) | | Starting kWh for tier (inclusive) |
| tier_end_kwh | NUMERIC(10, 2) | | Ending kWh for tier (NULL for unlimited tier) |
| energy_charge_usd_per_kwh | NUMERIC(10, 6) | NOT NULL | Energy charge per kWh for this tier |
| effective_date | DATE | NOT NULL | Tier effective date |
| expiration_date | DATE | | Tier expiration date |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### time_of_use_periods

Stores time-of-use rate periods (e.g., Peak, Off-Peak, Super Off-Peak).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| tou_period_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for TOU period |
| rate_structure_id | VARCHAR(255) | NOT NULL, FK → rate_structures | Rate structure identifier |
| period_name | VARCHAR(100) | NOT NULL | Period name ('Peak', 'Off-Peak', 'Super Off-Peak', 'Mid-Peak') |
| period_start_time | TIME | NOT NULL | Period start time |
| period_end_time | TIME | NOT NULL | Period end time |
| day_of_week | VARCHAR(20) | | Day of week ('Monday', 'Weekday', 'Weekend', 'All') |
| season | VARCHAR(50) | | Season ('Summer', 'Winter', 'Spring', 'Fall', 'All') |
| energy_charge_usd_per_kwh | NUMERIC(10, 6) | NOT NULL | Energy charge per kWh for this period |
| effective_date | DATE | NOT NULL | Period effective date |
| expiration_date | DATE | | Period expiration date |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### geographic_rate_areas

Maps geographic areas to specific rate structures.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| rate_area_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for rate area |
| rate_structure_id | VARCHAR(255) | NOT NULL, FK → rate_structures | Rate structure identifier |
| state_id | VARCHAR(2) | FK → states | State identifier |
| county_id | VARCHAR(255) | FK → counties | County identifier |
| zip_code | VARCHAR(10) | FK → zip_codes | Zip code |
| service_area_name | VARCHAR(255) | | Service area name |
| service_area_description | TEXT | | Service area description |
| latitude_min | NUMERIC(10, 7) | | Minimum latitude (bounding box) |
| latitude_max | NUMERIC(10, 7) | | Maximum latitude (bounding box) |
| longitude_min | NUMERIC(10, 7) | | Minimum longitude (bounding box) |
| longitude_max | NUMERIC(10, 7) | | Maximum longitude (bounding box) |
| effective_date | DATE | NOT NULL | Area effective date |
| expiration_date | DATE | | Area expiration date |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### historical_electricity_rates

Tracks rate changes over time for trend analysis.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| historical_rate_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for historical rate |
| rate_id | VARCHAR(255) | NOT NULL, FK → electricity_rates | Current rate identifier |
| utility_id | VARCHAR(255) | NOT NULL, FK → utility_companies | Utility company identifier |
| rate_code_id | VARCHAR(255) | NOT NULL, FK → rate_codes | Rate code identifier |
| state_id | VARCHAR(2) | NOT NULL, FK → states | State identifier |
| fixed_charge_usd | NUMERIC(10, 4) | | Historical fixed charge |
| energy_charge_usd_per_kwh | NUMERIC(10, 6) | | Historical energy charge per kWh |
| demand_charge_usd_per_kw | NUMERIC(10, 4) | | Historical demand charge per kW |
| effective_date | DATE | NOT NULL | Historical rate effective date |
| change_type | VARCHAR(50) | | Change type ('rate_increase', 'rate_decrease', 'new_rate', 'rate_expired') |
| change_percentage | NUMERIC(8, 4) | | Rate change percentage |
| change_amount | NUMERIC(10, 6) | | Rate change amount |
| change_reason | TEXT | | Reason for rate change |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### federal_incentives

Stores federal solar and renewable energy incentives.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| federal_incentive_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for federal incentive |
| incentive_name | VARCHAR(255) | NOT NULL | Incentive name (e.g., 'Solar Investment Tax Credit') |
| incentive_type | VARCHAR(50) | | Incentive type ('Tax Credit', 'Rebate', 'Grant', 'Loan', 'Performance-Based') |
| incentive_description | TEXT | | Detailed incentive description |
| eligible_technologies | TEXT[] | | Array of eligible technologies |
| eligible_sectors | TEXT[] | | Array of eligible sectors |
| incentive_amount_usd | NUMERIC(15, 2) | | Incentive amount in USD |
| incentive_percentage | NUMERIC(5, 2) | | Percentage-based incentive (e.g., 30% for ITC) |
| incentive_unit | VARCHAR(50) | | Incentive unit ('per_watt', 'per_system', 'percentage', 'fixed_amount') |
| maximum_incentive_usd | NUMERIC(15, 2) | | Maximum incentive amount in USD |
| minimum_system_size_kw | NUMERIC(10, 2) | | Minimum system size in kW |
| maximum_system_size_kw | NUMERIC(10, 2) | | Maximum system size in kW |
| effective_date | DATE | NOT NULL | Incentive effective date |
| expiration_date | DATE | | Incentive expiration date |
| is_active | BOOLEAN | DEFAULT TRUE | Whether incentive is currently active |
| program_website_url | VARCHAR(500) | | Program website URL |
| program_contact_info | TEXT | | Program contact information |
| data_source | VARCHAR(100) | | Data source ('doe', 'dsire', 'irs') |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### state_incentives

Stores state-level solar and renewable energy incentives.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| state_incentive_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for state incentive |
| state_id | VARCHAR(2) | NOT NULL, FK → states | Two-letter state code |
| incentive_name | VARCHAR(255) | NOT NULL | Incentive name |
| incentive_type | VARCHAR(50) | | Incentive type ('Tax Credit', 'Rebate', 'Grant', 'Loan', 'Performance-Based', 'Property Tax Exemption') |
| incentive_description | TEXT | | Detailed incentive description |
| eligible_technologies | TEXT[] | | Array of eligible technologies |
| eligible_sectors | TEXT[] | | Array of eligible sectors |
| incentive_amount_usd | NUMERIC(15, 2) | | Incentive amount in USD |
| incentive_percentage | NUMERIC(5, 2) | | Percentage-based incentive |
| incentive_unit | VARCHAR(50) | | Incentive unit ('per_watt', 'per_system', 'percentage', 'fixed_amount') |
| maximum_incentive_usd | NUMERIC(15, 2) | | Maximum incentive amount in USD |
| minimum_system_size_kw | NUMERIC(10, 2) | | Minimum system size in kW |
| maximum_system_size_kw | NUMERIC(10, 2) | | Maximum system size in kW |
| effective_date | DATE | NOT NULL | Incentive effective date |
| expiration_date | DATE | | Incentive expiration date |
| is_active | BOOLEAN | DEFAULT TRUE | Whether incentive is currently active |
| program_website_url | VARCHAR(500) | | Program website URL |
| program_contact_info | TEXT | | Program contact information |
| regulatory_authority | VARCHAR(255) | | State agency administering program |
| data_source | VARCHAR(100) | | Data source ('dsire', 'state_commission', 'state_energy_office') |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### utility_incentives

Stores utility-level solar and renewable energy incentives.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| utility_incentive_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for utility incentive |
| utility_id | VARCHAR(255) | NOT NULL, FK → utility_companies | Utility company identifier |
| state_id | VARCHAR(2) | NOT NULL, FK → states | State identifier |
| incentive_name | VARCHAR(255) | NOT NULL | Incentive name |
| incentive_type | VARCHAR(50) | | Incentive type ('Rebate', 'Performance-Based', 'Net Metering', 'Feed-in Tariff', 'Buy-Back Program') |
| incentive_description | TEXT | | Detailed incentive description |
| eligible_technologies | TEXT[] | | Array of eligible technologies |
| eligible_sectors | TEXT[] | | Array of eligible sectors |
| incentive_amount_usd | NUMERIC(15, 2) | | Incentive amount in USD |
| incentive_percentage | NUMERIC(5, 2) | | Percentage-based incentive |
| incentive_unit | VARCHAR(50) | | Incentive unit ('per_watt', 'per_kwh', 'percentage', 'fixed_amount') |
| maximum_incentive_usd | NUMERIC(15, 2) | | Maximum incentive amount in USD |
| minimum_system_size_kw | NUMERIC(10, 2) | | Minimum system size in kW |
| maximum_system_size_kw | NUMERIC(10, 2) | | Maximum system size in kW |
| net_metering_capacity_limit_kw | NUMERIC(10, 2) | | Net metering capacity limit in kW |
| feed_in_tariff_rate_usd_per_kwh | NUMERIC(10, 6) | | Feed-in tariff rate per kWh |
| effective_date | DATE | NOT NULL | Incentive effective date |
| expiration_date | DATE | | Incentive expiration date |
| is_active | BOOLEAN | DEFAULT TRUE | Whether incentive is currently active |
| program_website_url | VARCHAR(500) | | Program website URL |
| program_contact_info | TEXT | | Program contact information |
| data_source | VARCHAR(100) | | Data source ('dsire', 'utility_website', 'state_commission') |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### solar_rebate_aggregations

Aggregates all available rebates for a given location/utility.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| aggregation_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for aggregation |
| state_id | VARCHAR(2) | NOT NULL, FK → states | State identifier |
| utility_id | VARCHAR(255) | FK → utility_companies | Utility identifier |
| zip_code | VARCHAR(10) | FK → zip_codes | Zip code |
| total_federal_incentives_usd | NUMERIC(15, 2) | | Total federal incentives in USD |
| total_state_incentives_usd | NUMERIC(15, 2) | | Total state incentives in USD |
| total_utility_incentives_usd | NUMERIC(15, 2) | | Total utility incentives in USD |
| total_combined_incentives_usd | NUMERIC(15, 2) | | Total combined incentives in USD |
| federal_incentive_count | INTEGER | DEFAULT 0 | Number of federal incentives |
| state_incentive_count | INTEGER | DEFAULT 0 | Number of state incentives |
| utility_incentive_count | INTEGER | DEFAULT 0 | Number of utility incentives |
| total_incentive_count | INTEGER | DEFAULT 0 | Total incentive count |
| calculation_date | DATE | NOT NULL | Date aggregation was calculated |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### rate_comparison_matrix

Compares rates across utilities, states, and rate codes.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| comparison_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for comparison |
| rate_id_1 | VARCHAR(255) | NOT NULL, FK → electricity_rates | First rate identifier |
| rate_id_2 | VARCHAR(255) | NOT NULL, FK → electricity_rates | Second rate identifier |
| comparison_metric | VARCHAR(100) | | Comparison metric ('price_per_kwh', 'total_monthly_cost', 'cost_efficiency') |
| usage_kwh_per_month | NUMERIC(10, 2) | | Usage level in kWh/month for comparison |
| rate_1_cost_usd | NUMERIC(15, 2) | | Cost for rate 1 in USD |
| rate_2_cost_usd | NUMERIC(15, 2) | | Cost for rate 2 in USD |
| cost_difference_usd | NUMERIC(15, 2) | | Cost difference in USD |
| cost_difference_percentage | NUMERIC(8, 4) | | Cost difference percentage |
| comparison_date | DATE | NOT NULL | Date comparison was performed |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### data_extraction_log

Tracks data extraction operations from various sources.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| extraction_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for extraction |
| source_id | VARCHAR(100) | NOT NULL | Source identifier from data_resources.json |
| source_name | VARCHAR(255) | NOT NULL | Source name |
| extraction_type | VARCHAR(50) | | Extraction type ('api', 'web_scrape', 'file_download', 'manual') |
| extraction_status | VARCHAR(50) | | Extraction status ('success', 'failed', 'partial', 'in_progress') |
| records_extracted | INTEGER | DEFAULT 0 | Number of records extracted |
| records_loaded | INTEGER | DEFAULT 0 | Number of records loaded |
| records_failed | INTEGER | DEFAULT 0 | Number of records failed |
| extraction_start_time | TIMESTAMP_NTZ | NOT NULL | Extraction start timestamp |
| extraction_end_time | TIMESTAMP_NTZ | | Extraction end timestamp |
| extraction_duration_seconds | INTEGER | | Extraction duration in seconds |
| error_message | TEXT | | Error message if extraction failed |
| extraction_metadata | JSON | | Additional extraction metadata |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

---
**Last Updated:** 2026-02-04
