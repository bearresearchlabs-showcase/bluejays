---
title: Maritime Shipping Intelligence Database — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-7
---

# Maritime Shipping Intelligence Database — Documentation

**Database:** db-7  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_7
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_7 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load production data from data_large.sql when available (>= 1GB). No sample data.

```bash
psql -U postgres -d db_7 -f data_large.sql
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

- `carriers` — (see data dictionary)
- `locations` — (see data dictionary)
- `ports` — (see data dictionary)
- `vessels` — (see data dictionary)
- `routes` — (see data dictionary)
- `route_ports` — (see data dictionary)
- `port_pairs` — (see data dictionary)
- `port_calls` — (see data dictionary)
- `sailings` — (see data dictionary)
- `voyages` — (see data dictionary)
- `voyage_port_calls` — (see data dictionary)
- `vessel_tracking` — (see data dictionary)
- `port_statistics` — (see data dictionary)
- `carrier_performance` — (see data dictionary)

---

## Data Dictionary

### `carriers`

- `carrier_id` VARCHAR(255) PRIMARY KEY
- `carrier_name` VARCHAR(255) NOT NULL
- `scac_code` VARCHAR(10) UNIQUE — Standard Carrier Alpha Code
- `carrier_type` VARCHAR(50)  — 'Container', 'Bulk', 'RoRo', 'Tanker', 'General'
- `country` VARCHAR(100) 
- `website` VARCHAR(500) 
- `contact_email` VARCHAR(255) 
- `contact_phone` VARCHAR(50) 
- `status` VARCHAR(50) 
- `fleet_size` INTEGER 
- `total_capacity_teu` INTEGER 
- `established_year` INTEGER 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `locations`

- `location_id` VARCHAR(255) PRIMARY KEY
- `location_name` VARCHAR(255) NOT NULL
- `location_type` VARCHAR(50) NOT NULL — 'Country', 'Region', 'State', 'Province'
- `parent_location_id` VARCHAR(255) 
- `country_code` VARCHAR(3)  — ISO 3166-1 alpha-3
- `region_code` VARCHAR(10) 
- `latitude` NUMERIC(10, 7) 
- `longitude` NUMERIC(10, 7) 
- `location_geom` GEOGRAPHY  — Point geometry for location center
- `spatial_extent_west` NUMERIC(10, 6) 
- `spatial_extent_south` NUMERIC(10, 6) 
- `spatial_extent_east` NUMERIC(10, 6) 
- `spatial_extent_north` NUMERIC(10, 6) 
- `created_at` TIMESTAMP 

### `ports`

- `port_id` VARCHAR(255) PRIMARY KEY
- `port_name` VARCHAR(255) NOT NULL
- `port_code` VARCHAR(20) UNIQUE — UN/LOCODE or port code
- `locode` VARCHAR(10)  — UN/LOCODE (5 characters: 2 country + 3 location)
- `location_id` VARCHAR(255) 
- `country` VARCHAR(100) 
- `country_code` VARCHAR(3) 
- `latitude` NUMERIC(10, 7) NOT NULL
- `longitude` NUMERIC(10, 7) NOT NULL
- `port_geom` GEOGRAPHY  — Point geometry for port location
- `port_type` VARCHAR(50)  — 'Container', 'Bulk', 'RoRo', 'Tanker', 'General', 'Multi-purpose'
- `timezone` VARCHAR(50) 
- `depth_meters` NUMERIC(8, 2) 
- `max_vessel_length_meters` NUMERIC(8, 2) 
- `max_vessel_draft_meters` NUMERIC(8, 2) 
- `container_capacity_teu` INTEGER 
- `berth_count` INTEGER 
- `crane_count` INTEGER 
- `status` VARCHAR(50) 
- `data_source` VARCHAR(100)  — 'MARAD', 'NOAA', 'USCG', 'Linescape', etc.
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `vessels`

- `vessel_id` VARCHAR(255) PRIMARY KEY
- `vessel_name` VARCHAR(255) NOT NULL
- `imo_number` VARCHAR(10) UNIQUE — International Maritime Organization number
- `mmsi` VARCHAR(9)  — Maritime Mobile Service Identity
- `call_sign` VARCHAR(20) 
- `carrier_id` VARCHAR(255) 
- `vessel_type` VARCHAR(50)  — 'Container', 'Bulk', 'RoRo', 'Tanker', 'General Cargo'
- `flag_country` VARCHAR(100) 
- `flag_country_code` VARCHAR(3) 
- `year_built` INTEGER 
- `gross_tonnage` INTEGER 
- `net_tonnage` INTEGER 
- `deadweight_tonnage` INTEGER 
- `length_meters` NUMERIC(8, 2) 
- `beam_meters` NUMERIC(8, 2) 
- `draft_meters` NUMERIC(8, 2) 
- `max_speed_knots` NUMERIC(6, 2) 
- `container_capacity_teu` INTEGER 
- `container_capacity_twenty_foot` INTEGER 
- `container_capacity_forty_foot` INTEGER 
- `status` VARCHAR(50) 
- `data_source` VARCHAR(100)  — 'USCG', 'NOAA', 'MARAD', 'Linescape', etc.
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `routes`

- `route_id` VARCHAR(255) PRIMARY KEY
- `route_name` VARCHAR(255) NOT NULL
- `route_code` VARCHAR(100) 
- `carrier_id` VARCHAR(255) NOT NULL
- `service_type` VARCHAR(50)  — 'Direct', 'Feeder', 'Express', 'Regular'
- `route_type` VARCHAR(50)  — 'Trans-Pacific', 'Trans-Atlantic', 'Asia-Europe', etc.
- `frequency_weeks` INTEGER  — Service frequency in weeks
- `transit_time_days` INTEGER  — Average transit time
- `status` VARCHAR(50) 
- `start_date` DATE 
- `end_date` DATE 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `route_ports`

- `route_port_id` VARCHAR(255) PRIMARY KEY
- `route_id` VARCHAR(255) NOT NULL
- `port_id` VARCHAR(255) NOT NULL
- `port_sequence` INTEGER NOT NULL — Order of port call in route
- `port_role` VARCHAR(50)  — 'Origin', 'Destination', 'Transshipment', 'Intermediate'
- `estimated_days_from_start` INTEGER  — Days from route start
- `created_at` TIMESTAMP 

### `port_pairs`

- `port_pair_id` VARCHAR(255) PRIMARY KEY
- `origin_port_id` VARCHAR(255) NOT NULL
- `destination_port_id` VARCHAR(255) NOT NULL
- `carrier_id` VARCHAR(255) NOT NULL
- `route_id` VARCHAR(255) 
- `direct_service` BOOLEAN  — True if direct service exists
- `transshipment_required` BOOLEAN 
- `average_transit_days` INTEGER 
- `service_frequency_weeks` INTEGER 
- `last_sailing_date` DATE 
- `status` VARCHAR(50) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `port_calls`

- `port_call_id` VARCHAR(255) PRIMARY KEY
- `vessel_id` VARCHAR(255) NOT NULL
- `port_id` VARCHAR(255) NOT NULL
- `voyage_number` VARCHAR(100) 
- `route_id` VARCHAR(255) 
- `scheduled_arrival` TIMESTAMP 
- `actual_arrival` TIMESTAMP 
- `scheduled_departure` TIMESTAMP 
- `actual_departure` TIMESTAMP 
- `port_call_type` VARCHAR(50)  — 'Loading', 'Discharging', 'Transshipment', 'Bunkering', 'Repair'
- `berth_number` VARCHAR(50) 
- `terminal_name` VARCHAR(255) 
- `cargo_type` VARCHAR(100) 
- `containers_loaded` INTEGER 
- `containers_discharged` INTEGER 
- `containers_transshipped` INTEGER 
- `status` VARCHAR(50)  — 'Scheduled', 'In Progress', 'Completed', 'Cancelled'
- `delay_hours` NUMERIC(8, 2) 
- `data_source` VARCHAR(100)  — 'AIS', 'NOAD', 'MARAD', 'Linescape', etc.
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `sailings`

- `sailing_id` VARCHAR(255) PRIMARY KEY
- `vessel_id` VARCHAR(255) NOT NULL
- `voyage_number` VARCHAR(100) 
- `route_id` VARCHAR(255) 
- `origin_port_id` VARCHAR(255) NOT NULL
- `destination_port_id` VARCHAR(255) NOT NULL
- `scheduled_departure` TIMESTAMP 
- `actual_departure` TIMESTAMP 
- `scheduled_arrival` TIMESTAMP 
- `actual_arrival` TIMESTAMP 
- `transit_days` INTEGER 
- `distance_nautical_miles` NUMERIC(10, 2) 
- `average_speed_knots` NUMERIC(6, 2) 
- `cargo_type` VARCHAR(100) 
- `total_containers` INTEGER 
- `total_teu` NUMERIC(10, 2) 
- `capacity_utilization_percent` NUMERIC(5, 2) 
- `transshipment_count` INTEGER 
- `status` VARCHAR(50)  — 'Scheduled', 'In Transit', 'Completed', 'Cancelled'
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `voyages`

- `voyage_id` VARCHAR(255) PRIMARY KEY
- `vessel_id` VARCHAR(255) NOT NULL
- `voyage_number` VARCHAR(100) NOT NULL
- `route_id` VARCHAR(255) 
- `start_port_id` VARCHAR(255) NOT NULL
- `end_port_id` VARCHAR(255) NOT NULL
- `start_date` TIMESTAMP NOT NULL
- `end_date` TIMESTAMP 
- `total_distance_nautical_miles` NUMERIC(10, 2) 
- `total_transit_days` INTEGER 
- `port_call_count` INTEGER 
- `transshipment_count` INTEGER 
- `total_containers` INTEGER 
- `total_teu` NUMERIC(10, 2) 
- `status` VARCHAR(50)  — 'Scheduled', 'In Progress', 'Completed', 'Cancelled'
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `voyage_port_calls`

- `voyage_port_call_id` VARCHAR(255) PRIMARY KEY
- `voyage_id` VARCHAR(255) NOT NULL
- `port_call_id` VARCHAR(255) NOT NULL
- `port_sequence` INTEGER NOT NULL — Order of port call in voyage
- `created_at` TIMESTAMP 

### `vessel_tracking`

- `tracking_id` VARCHAR(255) PRIMARY KEY
- `vessel_id` VARCHAR(255) NOT NULL
- `mmsi` VARCHAR(9) 
- `timestamp` TIMESTAMP NOT NULL
- `latitude` NUMERIC(10, 7) NOT NULL
- `longitude` NUMERIC(10, 7) NOT NULL
- `position_geom` GEOGRAPHY  — Point geometry for vessel position
- `speed_knots` NUMERIC(6, 2) 
- `course_degrees` NUMERIC(6, 2) 
- `heading_degrees` NUMERIC(6, 2) 
- `navigation_status` VARCHAR(50)  — 'Under way', 'At anchor', 'Moored', etc.
- `destination` VARCHAR(255) 
- `eta` TIMESTAMP  — Estimated time of arrival
- `draught_meters` NUMERIC(6, 2) 
- `cargo_type` VARCHAR(100) 
- `data_source` VARCHAR(100)  — 'AIS', 'USCG', 'NOAA', etc.
- `data_quality` VARCHAR(50)  — 'High', 'Medium', 'Low'
- `created_at` TIMESTAMP 

### `port_statistics`

- `statistic_id` VARCHAR(255) PRIMARY KEY
- `port_id` VARCHAR(255) NOT NULL
- `statistic_date` DATE NOT NULL
- `statistic_period` VARCHAR(50)  — 'Daily', 'Weekly', 'Monthly', 'Yearly'
- `total_vessel_calls` INTEGER 
- `total_container_teu` NUMERIC(12, 2) 
- `containers_loaded` INTEGER 
- `containers_discharged` INTEGER 
- `containers_transshipped` INTEGER 
- `average_vessel_size_teu` NUMERIC(10, 2) 
- `average_dwell_time_hours` NUMERIC(8, 2) 
- `berth_utilization_percent` NUMERIC(5, 2) 
- `crane_utilization_percent` NUMERIC(5, 2) 
- `data_source` VARCHAR(100)  — 'MARAD', 'Port Authority', 'Linescape', etc.
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `carrier_performance`

- `performance_id` VARCHAR(255) PRIMARY KEY
- `carrier_id` VARCHAR(255) NOT NULL
- `evaluation_period_start` DATE NOT NULL
- `evaluation_period_end` DATE NOT NULL
- `total_voyages` INTEGER 
- `on_time_departures` INTEGER 
- `on_time_arrivals` INTEGER 
- `on_time_performance_percent` NUMERIC(5, 2) 
- `average_transit_time_days` NUMERIC(8, 2) 
- `vessel_utilization_percent` NUMERIC(5, 2) 
- `capacity_utilization_percent` NUMERIC(5, 2) 
- `total_teu_carried` NUMERIC(12, 2) 
- `port_calls_count` INTEGER 
- `route_coverage_count` INTEGER 
- `customer_satisfaction_score` NUMERIC(5, 2) 
- `created_at` TIMESTAMP 

---

*Generated by documentation workflow. MDX-compatible markdown.*
