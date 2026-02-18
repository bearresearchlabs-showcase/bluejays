---
title: Parking Intelligence Database — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-11
---

# Parking Intelligence Database — Documentation

**Database:** db-11  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_11
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_11 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load production data from data_large.sql when available (>= 1GB). No sample data.

```bash
psql -U postgres -d db_11 -f data_large.sql
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

**Total tables:** 14

- `metropolitan_areas` — (see data dictionary)
- `cities` — (see data dictionary)
- `airports` — (see data dictionary)
- `stadiums_venues` — (see data dictionary)
- `parking_facilities` — (see data dictionary)
- `parking_pricing` — (see data dictionary)
- `traffic_volume_data` — (see data dictionary)
- `events` — (see data dictionary)
- `market_intelligence_metrics` — (see data dictionary)
- `parking_utilization` — (see data dictionary)
- `competitive_analysis` — (see data dictionary)
- `business_districts` — (see data dictionary)
- `facility_district_mapping` — (see data dictionary)
- `data_source_metadata` — (see data dictionary)

---

## Data Dictionary

### `metropolitan_areas`

- `msa_id` VARCHAR(50) PRIMARY KEY
- `msa_name` VARCHAR(255) NOT NULL
- `msa_type` VARCHAR(50) NOT NULL — 'MSA', 'CSA', 'Micropolitan'
- `state_codes` VARCHAR(100)  — Comma-separated state codes
- `principal_city` VARCHAR(255) 
- `population_estimate` INTEGER 
- `land_area_sq_miles` NUMERIC(12, 2) 
- `population_density` NUMERIC(10, 2) 
- `median_household_income` NUMERIC(12, 2) 
- `gdp_billions` NUMERIC(12, 2) 
- `msa_geom` GEOGRAPHY  — Polygon geometry for MSA boundary
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `data_year` INTEGER 
- `load_timestamp` TIMESTAMP 

### `cities`

- `city_id` VARCHAR(50) PRIMARY KEY
- `city_name` VARCHAR(255) NOT NULL
- `state_code` VARCHAR(2) NOT NULL
- `county_name` VARCHAR(255) 
- `msa_id` VARCHAR(50) 
- `population` INTEGER 
- `land_area_sq_miles` NUMERIC(10, 2) 
- `population_density` NUMERIC(10, 2) 
- `median_household_income` NUMERIC(12, 2) 
- `median_age` NUMERIC(5, 2) 
- `employment_total` INTEGER 
- `unemployment_rate` NUMERIC(5, 2) 
- `city_geom` GEOGRAPHY  — Point geometry for city center
- `city_latitude` NUMERIC(10, 7) 
- `city_longitude` NUMERIC(10, 7) 
- `timezone` VARCHAR(50) 
- `data_year` INTEGER 
- `load_timestamp` TIMESTAMP 

### `airports`

- `airport_id` VARCHAR(10) PRIMARY KEY — IATA code
- `airport_name` VARCHAR(255) NOT NULL
- `city_id` VARCHAR(50) 
- `state_code` VARCHAR(2) 
- `airport_type` VARCHAR(50)  — 'Commercial', 'Cargo', 'General Aviation'
- `latitude` NUMERIC(10, 7) NOT NULL
- `longitude` NUMERIC(10, 7) NOT NULL
- `airport_geom` GEOGRAPHY  — Point geometry
- `annual_passengers` INTEGER 
- `annual_cargo_tons` INTEGER 
- `parking_spaces_total` INTEGER 
- `parking_facilities_count` INTEGER 
- `valet_available` BOOLEAN 
- `long_term_parking` BOOLEAN 
- `short_term_parking` BOOLEAN 
- `data_year` INTEGER 
- `load_timestamp` TIMESTAMP 

### `stadiums_venues`

- `venue_id` VARCHAR(50) PRIMARY KEY
- `venue_name` VARCHAR(255) NOT NULL
- `venue_type` VARCHAR(50)  — 'Stadium', 'Arena', 'Convention Center', 'Amphitheater'
- `city_id` VARCHAR(50) 
- `latitude` NUMERIC(10, 7) NOT NULL
- `longitude` NUMERIC(10, 7) NOT NULL
- `venue_geom` GEOGRAPHY  — Point geometry
- `capacity` INTEGER 
- `parking_spaces_total` INTEGER 
- `parking_facilities_count` INTEGER 
- `primary_sport` VARCHAR(100)  — 'NFL', 'MLB', 'NBA', 'NHL', 'Soccer', 'Concert'
- `team_name` VARCHAR(255) 
- `annual_events_count` INTEGER 
- `peak_attendance` INTEGER 
- `data_year` INTEGER 
- `load_timestamp` TIMESTAMP 

### `parking_facilities`

- `facility_id` VARCHAR(100) PRIMARY KEY
- `facility_name` VARCHAR(255) 
- `facility_type` VARCHAR(50)  — 'Surface Lot', 'Garage', 'Structure', 'Valet', 'Street'
- `city_id` VARCHAR(50) 
- `latitude` NUMERIC(10, 7) NOT NULL
- `longitude` NUMERIC(10, 7) NOT NULL
- `facility_geom` GEOGRAPHY  — Point geometry
- `total_spaces` INTEGER 
- `accessible_spaces` INTEGER 
- `ev_charging_stations` INTEGER 
- `covered_spaces` INTEGER 
- `uncovered_spaces` INTEGER 
- `height_restriction_feet` NUMERIC(5, 2) 
- `operator_name` VARCHAR(255) 
- `operator_type` VARCHAR(50)  — 'Public', 'Private', 'Municipal', 'Airport', 'Venue'
- `airport_id` VARCHAR(10) 
- `venue_id` VARCHAR(50) 
- `is_event_parking` BOOLEAN 
- `is_monthly_parking` BOOLEAN 
- `is_hourly_parking` BOOLEAN 
- `accepts_reservations` BOOLEAN 
- `payment_methods` VARCHAR(255)  — Comma-separated: 'Cash', 'Credit', 'Mobile', 'App'
- `amenities` VARCHAR(500)  — Comma-separated amenities
- `load_timestamp` TIMESTAMP 

### `parking_pricing`

- `pricing_id` VARCHAR(100) PRIMARY KEY
- `facility_id` VARCHAR(100) NOT NULL
- `pricing_type` VARCHAR(50)  — 'Hourly', 'Daily', 'Monthly', 'Event', 'Early Bird'
- `base_rate_hourly` NUMERIC(8, 2) 
- `base_rate_daily` NUMERIC(8, 2) 
- `base_rate_monthly` NUMERIC(8, 2) 
- `event_rate` NUMERIC(8, 2) 
- `max_daily_rate` NUMERIC(8, 2) 
- `currency` VARCHAR(3) 
- `effective_date` DATE 
- `expiration_date` DATE 
- `day_of_week` VARCHAR(20)  — 'Monday', 'Tuesday', etc., or 'All'
- `time_range_start` TIME 
- `time_range_end` TIME 
- `is_active` BOOLEAN 
- `load_timestamp` TIMESTAMP 

### `traffic_volume_data`

- `traffic_id` VARCHAR(100) PRIMARY KEY
- `location_id` VARCHAR(100) 
- `city_id` VARCHAR(50) 
- `latitude` NUMERIC(10, 7) 
- `longitude` NUMERIC(10, 7) 
- `location_geom` GEOGRAPHY  — Point geometry
- `road_name` VARCHAR(255) 
- `road_type` VARCHAR(50)  — 'Highway', 'Arterial', 'Collector', 'Local'
- `annual_average_daily_traffic` INTEGER 
- `peak_hour_volume` INTEGER 
- `direction` VARCHAR(20)  — 'Northbound', 'Southbound', 'Eastbound', 'Westbound', 'Both'
- `data_year` INTEGER 
- `data_month` INTEGER 
- `load_timestamp` TIMESTAMP 

### `events`

- `event_id` VARCHAR(100) PRIMARY KEY
- `event_name` VARCHAR(255) NOT NULL
- `event_type` VARCHAR(50)  — 'Sports', 'Concert', 'Convention', 'Festival', 'Conference'
- `venue_id` VARCHAR(50) 
- `city_id` VARCHAR(50) 
- `event_date` DATE NOT NULL
- `event_time` TIME 
- `attendance` INTEGER 
- `parking_demand_multiplier` NUMERIC(5, 2)  — Multiplier for parking demand
- `is_recurring` BOOLEAN 
- `recurrence_pattern` VARCHAR(100)  — 'Weekly', 'Monthly', 'Seasonal'
- `load_timestamp` TIMESTAMP 

### `market_intelligence_metrics`

- `metric_id` VARCHAR(100) PRIMARY KEY
- `city_id` VARCHAR(50) 
- `msa_id` VARCHAR(50) 
- `metric_type` VARCHAR(50)  — 'Demand', 'Supply', 'Utilization', 'Revenue', 'Competition'
- `metric_name` VARCHAR(100) 
- `metric_value` NUMERIC(15, 2) 
- `metric_unit` VARCHAR(50) 
- `calculation_date` DATE 
- `time_period` VARCHAR(50)  — 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Annual'
- `data_year` INTEGER 
- `data_month` INTEGER 
- `load_timestamp` TIMESTAMP 

### `parking_utilization`

- `utilization_id` VARCHAR(100) PRIMARY KEY
- `facility_id` VARCHAR(100) NOT NULL
- `utilization_date` DATE NOT NULL
- `utilization_hour` INTEGER  — 0-23
- `occupancy_rate` NUMERIC(5, 2)  — Percentage 0-100
- `spaces_occupied` INTEGER 
- `spaces_available` INTEGER 
- `revenue_generated` NUMERIC(10, 2) 
- `reservation_count` INTEGER 
- `walk_in_count` INTEGER 
- `data_source` VARCHAR(50)  — 'Sensor', 'Manual', 'App', 'Estimated'
- `load_timestamp` TIMESTAMP 

### `competitive_analysis`

- `analysis_id` VARCHAR(100) PRIMARY KEY
- `facility_id` VARCHAR(100) NOT NULL
- `competitor_facility_id` VARCHAR(100) 
- `analysis_date` DATE 
- `price_difference_pct` NUMERIC(5, 2) 
- `distance_miles` NUMERIC(8, 2) 
- `utilization_difference_pct` NUMERIC(5, 2) 
- `amenity_comparison` VARCHAR(500) 
- `competitive_score` NUMERIC(5, 2)  — 0-100
- `load_timestamp` TIMESTAMP 

### `business_districts`

- `district_id` VARCHAR(50) PRIMARY KEY
- `district_name` VARCHAR(255) NOT NULL
- `city_id` VARCHAR(50) 
- `district_type` VARCHAR(50)  — 'Downtown', 'Financial', 'Retail', 'Entertainment', 'Airport', 'Medical'
- `latitude` NUMERIC(10, 7) 
- `longitude` NUMERIC(10, 7) 
- `district_geom` GEOGRAPHY  — Polygon geometry
- `employment_total` INTEGER 
- `businesses_count` INTEGER 
- `parking_demand_score` NUMERIC(5, 2)  — 0-100
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `data_year` INTEGER 
- `load_timestamp` TIMESTAMP 

### `facility_district_mapping`

- `mapping_id` VARCHAR(100) PRIMARY KEY
- `facility_id` VARCHAR(100) NOT NULL
- `district_id` VARCHAR(50) NOT NULL
- `distance_miles` NUMERIC(8, 2) 
- `is_primary_district` BOOLEAN 
- `load_timestamp` TIMESTAMP 

### `data_source_metadata`

- `source_id` VARCHAR(100) PRIMARY KEY
- `source_name` VARCHAR(255) NOT NULL
- `source_type` VARCHAR(50)  — 'API', 'CSV', 'Shapefile', 'Database', 'Web Scrape'
- `source_url` VARCHAR(1000) 
- `api_endpoint` VARCHAR(500) 
- `extraction_date` DATE 
- `extraction_timestamp` TIMESTAMP 
- `records_extracted` INTEGER 
- `data_quality_score` NUMERIC(5, 2)  — 0-100
- `completeness_pct` NUMERIC(5, 2) 
- `error_count` INTEGER 
- `load_timestamp` TIMESTAMP 

---

*Generated by documentation workflow. MDX-compatible markdown.*
