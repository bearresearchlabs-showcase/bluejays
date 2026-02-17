---
title: Electricity Cost and Solar Rebate Database — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-15
---

# Electricity Cost and Solar Rebate Database — Documentation

**Database:** db-15  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_15
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_15 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load sample data from data.sql if available.

```bash
psql -U postgres -d db_15 -f data.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

Standard PostgreSQL. No extensions required unless noted.

---

## Schema Overview

**Total tables:** 17

- `states` — (see data dictionary)
- `counties` — (see data dictionary)
- `zip_codes` — (see data dictionary)
- `utility_companies` — (see data dictionary)
- `rate_codes` — (see data dictionary)
- `rate_structures` — (see data dictionary)
- `electricity_rates` — (see data dictionary)
- `tiered_rate_tiers` — (see data dictionary)
- `time_of_use_periods` — (see data dictionary)
- `geographic_rate_areas` — (see data dictionary)
- `historical_electricity_rates` — (see data dictionary)
- `federal_incentives` — (see data dictionary)
- `state_incentives` — (see data dictionary)
- `utility_incentives` — (see data dictionary)
- `solar_rebate_aggregations` — (see data dictionary)
- `rate_comparison_matrix` — (see data dictionary)
- `data_extraction_log` — (see data dictionary)

---

## Data Dictionary

### `states`

- `state_id` VARCHAR(2) PRIMARY KEY — Two-letter state code (e.g., 'CA', 'NY')
- `state_name` VARCHAR(100) NOT NULL
- `state_full_name` VARCHAR(100) 
- `region` VARCHAR(50)  — 'Northeast', 'South', 'Midwest', 'West'
- `division` VARCHAR(50)  — Census division
- `timezone` VARCHAR(50) 
- `is_active` BOOLEAN 
- `last_updated` TIMESTAMP 

### `counties`

- `county_id` VARCHAR(255) PRIMARY KEY
- `state_id` VARCHAR(2) NOT NULL
- `county_name` VARCHAR(100) NOT NULL
- `county_fips_code` VARCHAR(5)  — 5-digit FIPS code
- `county_seat` VARCHAR(100) 
- `population` INTEGER 
- `area_sq_miles` NUMERIC(10 
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (state_id) FOREIGN KEY

### `zip_codes`

- `zip_code` VARCHAR(10) PRIMARY KEY
- `state_id` VARCHAR(2) NOT NULL
- `county_id` VARCHAR(255) 
- `city` VARCHAR(100) 
- `latitude` NUMERIC(10  — WGS84
- `longitude` NUMERIC(10  — WGS84
- `timezone` VARCHAR(50) 
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (state_id) FOREIGN KEY
- `FOREIGN` KEY (county_id) FOREIGN KEY

### `utility_companies`

- `utility_id` VARCHAR(255) PRIMARY KEY
- `utility_name` VARCHAR(255) NOT NULL
- `utility_display_name` VARCHAR(255) 
- `utility_type` VARCHAR(50)  — 'Investor-Owned', 'Municipal', 'Cooperative', 'Federal', 'Power Marketer'
- `state_id` VARCHAR(2) NOT NULL
- `service_territory_description` TEXT 
- `eia_utility_id` VARCHAR(50)  — EIA Form 861 utility identifier
- `openei_utility_id` VARCHAR(50)  — OpenEI utility identifier
- `website_url` VARCHAR(500) 
- `customer_service_phone` VARCHAR(50) 
- `total_customers` INTEGER 
- `total_mwh_sold` NUMERIC(15 
- `is_active` BOOLEAN 
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (state_id) FOREIGN KEY

### `rate_codes`

- `rate_code_id` VARCHAR(255) PRIMARY KEY
- `rate_code` VARCHAR(100) NOT NULL
- `rate_code_description` TEXT 
- `rate_code_category` VARCHAR(100)  — 'Residential', 'Commercial', 'Industrial', 'Agricultural', 'Lighting'
- `sector` VARCHAR(50)  — 'Residential', 'Commercial', 'Industrial', 'Lighting'
- `rate_structure_type` VARCHAR(100)  — 'Flat', 'Tiered', 'Time-of-Use', 'Demand', 'Hybrid'
- `is_active` BOOLEAN 
- `last_updated` TIMESTAMP 

### `rate_structures`

- `rate_structure_id` VARCHAR(255) PRIMARY KEY
- `utility_id` VARCHAR(255) NOT NULL
- `rate_code_id` VARCHAR(255) NOT NULL
- `rate_name` VARCHAR(255) NOT NULL
- `rate_description` TEXT 
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `approval_status` VARCHAR(50)  — 'Approved', 'Pending', 'Proposed', 'Expired'
- `regulatory_authority` VARCHAR(255)  — State PUC/PSC
- `tariff_filing_number` VARCHAR(100) 
- `is_current` BOOLEAN 
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (utility_id) FOREIGN KEY
- `FOREIGN` KEY (rate_code_id) FOREIGN KEY

### `electricity_rates`

- `rate_id` VARCHAR(255) PRIMARY KEY
- `rate_structure_id` VARCHAR(255) NOT NULL
- `utility_id` VARCHAR(255) NOT NULL
- `rate_code_id` VARCHAR(255) NOT NULL
- `state_id` VARCHAR(2) NOT NULL
- `rate_type` VARCHAR(50)  — 'Residential', 'Commercial', 'Industrial', 'Lighting'
- `billing_period` VARCHAR(50)  — 'Monthly', 'Daily', 'Hourly'
- `fixed_charge_usd` NUMERIC(10  — Monthly fixed charge
- `fixed_charge_unit` VARCHAR(50)  — 'per_month', 'per_day', 'per_customer'
- `energy_charge_usd_per_kwh` NUMERIC(10  — Base energy charge per kWh
- `demand_charge_usd_per_kw` NUMERIC(10  — Demand charge per kW
- `minimum_charge_usd` NUMERIC(10 
- `currency` VARCHAR(10) 
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `is_current` BOOLEAN 
- `data_source` VARCHAR(100)  — 'openei', 'eia', 'state_commission', 'poweroutage_us'
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (rate_structure_id) FOREIGN KEY
- `FOREIGN` KEY (utility_id) FOREIGN KEY
- `FOREIGN` KEY (rate_code_id) FOREIGN KEY
- `FOREIGN` KEY (state_id) FOREIGN KEY

### `tiered_rate_tiers`

- `tier_id` VARCHAR(255) PRIMARY KEY
- `rate_structure_id` VARCHAR(255) NOT NULL
- `tier_number` INTEGER NOT NULL
- `tier_name` VARCHAR(100) 
- `tier_start_kwh` NUMERIC(10 
- `tier_end_kwh` NUMERIC(10  — NULL for unlimited tier
- `energy_charge_usd_per_kwh` NUMERIC(10 NOT NULL
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (rate_structure_id) FOREIGN KEY

### `time_of_use_periods`

- `tou_period_id` VARCHAR(255) PRIMARY KEY
- `rate_structure_id` VARCHAR(255) NOT NULL
- `period_name` VARCHAR(100) NOT NULL — 'Peak', 'Off-Peak', 'Super Off-Peak', 'Mid-Peak'
- `period_start_time` TIME NOT NULL
- `period_end_time` TIME NOT NULL
- `day_of_week` VARCHAR(20)  — 'Monday', 'Weekday', 'Weekend', 'All'
- `season` VARCHAR(50)  — 'Summer', 'Winter', 'Spring', 'Fall', 'All'
- `energy_charge_usd_per_kwh` NUMERIC(10 NOT NULL
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (rate_structure_id) FOREIGN KEY

### `geographic_rate_areas`

- `rate_area_id` VARCHAR(255) PRIMARY KEY
- `rate_structure_id` VARCHAR(255) NOT NULL
- `state_id` VARCHAR(2) 
- `county_id` VARCHAR(255) 
- `zip_code` VARCHAR(10) 
- `service_area_name` VARCHAR(255) 
- `service_area_description` TEXT 
- `latitude_min` NUMERIC(10  — Bounding box
- `latitude_max` NUMERIC(10 
- `longitude_min` NUMERIC(10 
- `longitude_max` NUMERIC(10 
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (rate_structure_id) FOREIGN KEY
- `FOREIGN` KEY (state_id) FOREIGN KEY
- `FOREIGN` KEY (county_id) FOREIGN KEY
- `FOREIGN` KEY (zip_code) FOREIGN KEY

### `historical_electricity_rates`

- `historical_rate_id` VARCHAR(255) PRIMARY KEY
- `rate_id` VARCHAR(255) NOT NULL
- `utility_id` VARCHAR(255) NOT NULL
- `rate_code_id` VARCHAR(255) NOT NULL
- `state_id` VARCHAR(2) NOT NULL
- `fixed_charge_usd` NUMERIC(10 
- `energy_charge_usd_per_kwh` NUMERIC(10 
- `demand_charge_usd_per_kw` NUMERIC(10 
- `effective_date` DATE NOT NULL
- `change_type` VARCHAR(50)  — 'rate_increase', 'rate_decrease', 'new_rate', 'rate_expired'
- `change_percentage` NUMERIC(8 
- `change_amount` NUMERIC(10 
- `change_reason` TEXT 
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (rate_id) FOREIGN KEY
- `FOREIGN` KEY (utility_id) FOREIGN KEY
- `FOREIGN` KEY (rate_code_id) FOREIGN KEY
- `FOREIGN` KEY (state_id) FOREIGN KEY

### `federal_incentives`

- `federal_incentive_id` VARCHAR(255) PRIMARY KEY
- `incentive_name` VARCHAR(255) NOT NULL
- `incentive_type` VARCHAR(50)  — 'Tax Credit', 'Rebate', 'Grant', 'Loan', 'Performance-Based'
- `incentive_description` TEXT 
- `eligible_technologies` TEXT[]  — Array of eligible technologies
- `eligible_sectors` TEXT[]  — Array of eligible sectors
- `incentive_amount_usd` NUMERIC(15 
- `incentive_percentage` NUMERIC(5  — Percentage-based incentives
- `incentive_unit` VARCHAR(50)  — 'per_watt', 'per_system', 'percentage', 'fixed_amount'
- `maximum_incentive_usd` NUMERIC(15 
- `minimum_system_size_kw` NUMERIC(10 
- `maximum_system_size_kw` NUMERIC(10 
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `is_active` BOOLEAN 
- `program_website_url` VARCHAR(500) 
- `program_contact_info` TEXT 
- `data_source` VARCHAR(100)  — 'doe', 'dsire', 'irs'
- `last_updated` TIMESTAMP 

### `state_incentives`

- `state_incentive_id` VARCHAR(255) PRIMARY KEY
- `state_id` VARCHAR(2) NOT NULL
- `incentive_name` VARCHAR(255) NOT NULL
- `incentive_type` VARCHAR(50)  — 'Tax Credit', 'Rebate', 'Grant', 'Loan', 'Performance-Based', 'Property Tax Exemption'
- `incentive_description` TEXT 
- `eligible_technologies` TEXT[] 
- `eligible_sectors` TEXT[] 
- `incentive_amount_usd` NUMERIC(15 
- `incentive_percentage` NUMERIC(5 
- `incentive_unit` VARCHAR(50) 
- `maximum_incentive_usd` NUMERIC(15 
- `minimum_system_size_kw` NUMERIC(10 
- `maximum_system_size_kw` NUMERIC(10 
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `is_active` BOOLEAN 
- `program_website_url` VARCHAR(500) 
- `program_contact_info` TEXT 
- `regulatory_authority` VARCHAR(255)  — State agency administering program
- `data_source` VARCHAR(100)  — 'dsire', 'state_commission', 'state_energy_office'
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (state_id) FOREIGN KEY

### `utility_incentives`

- `utility_incentive_id` VARCHAR(255) PRIMARY KEY
- `utility_id` VARCHAR(255) NOT NULL
- `state_id` VARCHAR(2) NOT NULL
- `incentive_name` VARCHAR(255) NOT NULL
- `incentive_type` VARCHAR(50)  — 'Rebate', 'Performance-Based', 'Net Metering', 'Feed-in Tariff', 'Buy-Back Program'
- `incentive_description` TEXT 
- `eligible_technologies` TEXT[] 
- `eligible_sectors` TEXT[] 
- `incentive_amount_usd` NUMERIC(15 
- `incentive_percentage` NUMERIC(5 
- `incentive_unit` VARCHAR(50)  — 'per_watt', 'per_kwh', 'percentage', 'fixed_amount'
- `maximum_incentive_usd` NUMERIC(15 
- `minimum_system_size_kw` NUMERIC(10 
- `maximum_system_size_kw` NUMERIC(10 
- `net_metering_capacity_limit_kw` NUMERIC(10  — For net metering programs
- `feed_in_tariff_rate_usd_per_kwh` NUMERIC(10  — For feed-in tariff programs
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `is_active` BOOLEAN 
- `program_website_url` VARCHAR(500) 
- `program_contact_info` TEXT 
- `data_source` VARCHAR(100)  — 'dsire', 'utility_website', 'state_commission'
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (utility_id) FOREIGN KEY
- `FOREIGN` KEY (state_id) FOREIGN KEY

### `solar_rebate_aggregations`

- `aggregation_id` VARCHAR(255) PRIMARY KEY
- `state_id` VARCHAR(2) NOT NULL
- `utility_id` VARCHAR(255) 
- `zip_code` VARCHAR(10) 
- `total_federal_incentives_usd` NUMERIC(15 
- `total_state_incentives_usd` NUMERIC(15 
- `total_utility_incentives_usd` NUMERIC(15 
- `total_combined_incentives_usd` NUMERIC(15 
- `federal_incentive_count` INTEGER 
- `state_incentive_count` INTEGER 
- `utility_incentive_count` INTEGER 
- `total_incentive_count` INTEGER 
- `calculation_date` DATE NOT NULL
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (state_id) FOREIGN KEY
- `FOREIGN` KEY (utility_id) FOREIGN KEY
- `FOREIGN` KEY (zip_code) FOREIGN KEY

### `rate_comparison_matrix`

- `comparison_id` VARCHAR(255) PRIMARY KEY
- `rate_id_1` VARCHAR(255) NOT NULL
- `rate_id_2` VARCHAR(255) NOT NULL
- `comparison_metric` VARCHAR(100)  — 'price_per_kwh', 'total_monthly_cost', 'cost_efficiency'
- `usage_kwh_per_month` NUMERIC(10  — Usage level for comparison
- `rate_1_cost_usd` NUMERIC(15 
- `rate_2_cost_usd` NUMERIC(15 
- `cost_difference_usd` NUMERIC(15 
- `cost_difference_percentage` NUMERIC(8 
- `comparison_date` DATE NOT NULL
- `last_updated` TIMESTAMP 
- `FOREIGN` KEY (rate_id_1) FOREIGN KEY
- `FOREIGN` KEY (rate_id_2) FOREIGN KEY

### `data_extraction_log`

- `extraction_id` VARCHAR(255) PRIMARY KEY
- `source_id` VARCHAR(100) NOT NULL — References source_id from data_resources.json
- `source_name` VARCHAR(255) NOT NULL
- `extraction_type` VARCHAR(50)  — 'api', 'web_scrape', 'file_download', 'manual'
- `extraction_status` VARCHAR(50)  — 'success', 'failed', 'partial', 'in_progress'
- `records_extracted` INTEGER 
- `records_loaded` INTEGER 
- `records_failed` INTEGER 
- `extraction_start_time` TIMESTAMP NOT NULL
- `extraction_end_time` TIMESTAMP 
- `extraction_duration_seconds` INTEGER 
- `error_message` TEXT 
- `extraction_metadata` JSON  — Additional extraction metadata
- `last_updated` TIMESTAMP 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 

---

*Generated by documentation workflow. MDX-compatible markdown.*
