# Database Schema Documentation - DB-7 Maritime Shipping Intelligence

## Overview

The Maritime Shipping Intelligence database (db-7) provides comprehensive maritime shipping intelligence including vessel tracking, port schedules, carrier routes, sailings, and port calls. The database integrates data from multiple government sources including NOAA, US Coast Guard, MARAD, and Data.gov.

## Database Structure

The database consists of 13 main tables organized into logical groups:

### Core Reference Tables
- **carriers** - Shipping line/carrier information
- **locations** - Regions, countries, and geographic areas
- **ports** - Port information with UN/LOCODE
- **vessels** - Vessel information with IMO numbers and MMSI

### Route and Service Tables
- **routes** - Shipping routes/services operated by carriers
- **route_ports** - Junction table linking routes to ports
- **port_pairs** - Origin-destination port pairs for carriers

### Operational Tables
- **port_calls** - Scheduled and actual port calls
- **sailings** - Sailing/voyage information between ports
- **voyages** - Complete voyage information
- **voyage_port_calls** - Links voyages to port calls

### Tracking and Analytics Tables
- **vessel_tracking** - AIS tracking data
- **port_statistics** - Aggregated port statistics
- **carrier_performance** - Carrier performance metrics

## Table Details

### carriers

Stores shipping line/carrier information with SCAC codes.

**Key Columns:**
- `carrier_id` (VARCHAR(255), PRIMARY KEY)
- `carrier_name` (VARCHAR(255), NOT NULL)
- `scac_code` (VARCHAR(10), UNIQUE) - Standard Carrier Alpha Code
- `carrier_type` (VARCHAR(50)) - Container, Bulk, RoRo, Tanker, General
- `country` (VARCHAR(100))
- `fleet_size` (INTEGER)
- `total_capacity_teu` (INTEGER)

### ports

Stores port information with UN/LOCODE, coordinates, and characteristics.

**Key Columns:**
- `port_id` (VARCHAR(255), PRIMARY KEY)
- `port_name` (VARCHAR(255), NOT NULL)
- `port_code` (VARCHAR(20), UNIQUE)
- `locode` (VARCHAR(10)) - UN/LOCODE (5 characters: 2 country + 3 location)
- `latitude` (NUMERIC(10, 7), NOT NULL)
- `longitude` (NUMERIC(10, 7), NOT NULL)
- `port_geom` (GEOGRAPHY) - Point geometry for port location
- `port_type` (VARCHAR(50)) - Container, Bulk, RoRo, Tanker, General, Multi-purpose
- `container_capacity_teu` (INTEGER)
- `berth_count` (INTEGER)

### vessels

Stores vessel information with IMO numbers, MMSI, and specifications.

**Key Columns:**
- `vessel_id` (VARCHAR(255), PRIMARY KEY)
- `vessel_name` (VARCHAR(255), NOT NULL)
- `imo_number` (VARCHAR(10), UNIQUE) - International Maritime Organization number
- `mmsi` (VARCHAR(9)) - Maritime Mobile Service Identity
- `carrier_id` (VARCHAR(255)) - Foreign key to carriers
- `vessel_type` (VARCHAR(50)) - Container, Bulk, RoRo, Tanker, General Cargo
- `container_capacity_teu` (INTEGER)
- `length_meters` (NUMERIC(8, 2))
- `beam_meters` (NUMERIC(8, 2))
- `draft_meters` (NUMERIC(8, 2))

### routes

Stores shipping routes/services operated by carriers.

**Key Columns:**
- `route_id` (VARCHAR(255), PRIMARY KEY)
- `route_name` (VARCHAR(255), NOT NULL)
- `route_code` (VARCHAR(100))
- `carrier_id` (VARCHAR(255), NOT NULL) - Foreign key to carriers
- `service_type` (VARCHAR(50)) - Direct, Feeder, Express, Regular
- `frequency_weeks` (INTEGER) - Service frequency in weeks
- `transit_time_days` (INTEGER) - Average transit time

### port_calls

Stores scheduled and actual port calls with vessel and port information.

**Key Columns:**
- `port_call_id` (VARCHAR(255), PRIMARY KEY)
- `vessel_id` (VARCHAR(255), NOT NULL) - Foreign key to vessels
- `port_id` (VARCHAR(255), NOT NULL) - Foreign key to ports
- `voyage_number` (VARCHAR(100))
- `route_id` (VARCHAR(255)) - Foreign key to routes
- `scheduled_arrival` (TIMESTAMP_NTZ)
- `actual_arrival` (TIMESTAMP_NTZ)
- `scheduled_departure` (TIMESTAMP_NTZ)
- `actual_departure` (TIMESTAMP_NTZ)
- `port_call_type` (VARCHAR(50)) - Loading, Discharging, Transshipment, Bunkering, Repair
- `containers_loaded` (INTEGER)
- `containers_discharged` (INTEGER)
- `status` (VARCHAR(50)) - Scheduled, In Progress, Completed, Cancelled

### sailings

Stores sailing/voyage information between ports.

**Key Columns:**
- `sailing_id` (VARCHAR(255), PRIMARY KEY)
- `vessel_id` (VARCHAR(255), NOT NULL) - Foreign key to vessels
- `voyage_number` (VARCHAR(100))
- `route_id` (VARCHAR(255)) - Foreign key to routes
- `origin_port_id` (VARCHAR(255), NOT NULL) - Foreign key to ports
- `destination_port_id` (VARCHAR(255), NOT NULL) - Foreign key to ports
- `scheduled_departure` (TIMESTAMP_NTZ)
- `actual_departure` (TIMESTAMP_NTZ)
- `scheduled_arrival` (TIMESTAMP_NTZ)
- `actual_arrival` (TIMESTAMP_NTZ)
- `transit_days` (INTEGER)
- `distance_nautical_miles` (NUMERIC(10, 2))
- `total_teu` (NUMERIC(10, 2))
- `capacity_utilization_percent` (NUMERIC(5, 2))

### vessel_tracking

Stores AIS (Automatic Identification System) tracking data.

**Key Columns:**
- `tracking_id` (VARCHAR(255), PRIMARY KEY)
- `vessel_id` (VARCHAR(255), NOT NULL) - Foreign key to vessels
- `mmsi` (VARCHAR(9))
- `timestamp` (TIMESTAMP_NTZ, NOT NULL)
- `latitude` (NUMERIC(10, 7), NOT NULL)
- `longitude` (NUMERIC(10, 7), NOT NULL)
- `position_geom` (GEOGRAPHY) - Point geometry for vessel position
- `speed_knots` (NUMERIC(6, 2))
- `course_degrees` (NUMERIC(6, 2))
- `heading_degrees` (NUMERIC(6, 2))
- `navigation_status` (VARCHAR(50)) - Under way, At anchor, Moored, etc.
- `destination` (VARCHAR(255))
- `eta` (TIMESTAMP_NTZ) - Estimated time of arrival
- `data_source` (VARCHAR(100)) - AIS, USCG, NOAA, etc.

### port_statistics

Stores aggregated port statistics and performance metrics.

**Key Columns:**
- `statistic_id` (VARCHAR(255), PRIMARY KEY)
- `port_id` (VARCHAR(255), NOT NULL) - Foreign key to ports
- `statistic_date` (DATE, NOT NULL)
- `statistic_period` (VARCHAR(50)) - Daily, Weekly, Monthly, Yearly
- `total_vessel_calls` (INTEGER)
- `total_container_teu` (NUMERIC(12, 2))
- `containers_loaded` (INTEGER)
- `containers_discharged` (INTEGER)
- `containers_transshipped` (INTEGER)
- `average_vessel_size_teu` (NUMERIC(10, 2))
- `average_dwell_time_hours` (NUMERIC(8, 2))
- `berth_utilization_percent` (NUMERIC(5, 2))

### carrier_performance

Stores carrier performance metrics and KPIs.

**Key Columns:**
- `performance_id` (VARCHAR(255), PRIMARY KEY)
- `carrier_id` (VARCHAR(255), NOT NULL) - Foreign key to carriers
- `evaluation_period_start` (DATE, NOT NULL)
- `evaluation_period_end` (DATE, NOT NULL)
- `total_voyages` (INTEGER)
- `on_time_departures` (INTEGER)
- `on_time_arrivals` (INTEGER)
- `on_time_performance_percent` (NUMERIC(5, 2))
- `average_transit_time_days` (NUMERIC(8, 2))
- `vessel_utilization_percent` (NUMERIC(5, 2))
- `capacity_utilization_percent` (NUMERIC(5, 2))
- `total_teu_carried` (NUMERIC(12, 2))

## Relationships

### Foreign Key Relationships

- `vessels.carrier_id` → `carriers.carrier_id`
- `ports.location_id` → `locations.location_id`
- `routes.carrier_id` → `carriers.carrier_id`
- `route_ports.route_id` → `routes.route_id`
- `route_ports.port_id` → `ports.port_id`
- `port_pairs.origin_port_id` → `ports.port_id`
- `port_pairs.destination_port_id` → `ports.port_id`
- `port_pairs.carrier_id` → `carriers.carrier_id`
- `port_calls.vessel_id` → `vessels.vessel_id`
- `port_calls.port_id` → `ports.port_id`
- `port_calls.route_id` → `routes.route_id`
- `sailings.vessel_id` → `vessels.vessel_id`
- `sailings.origin_port_id` → `ports.port_id`
- `sailings.destination_port_id` → `ports.port_id`
- `voyages.vessel_id` → `vessels.vessel_id`
- `voyages.route_id` → `routes.route_id`
- `voyage_port_calls.voyage_id` → `voyages.voyage_id`
- `voyage_port_calls.port_call_id` → `port_calls.port_call_id`
- `vessel_tracking.vessel_id` → `vessels.vessel_id`
- `port_statistics.port_id` → `ports.port_id`
- `carrier_performance.carrier_id` → `carriers.carrier_id`

## Indexes

The database includes comprehensive indexes for performance optimization:

- Indexes on foreign keys for join performance
- Indexes on timestamp columns for temporal queries
- Indexes on geographic columns for spatial queries
- Composite indexes for common query patterns

## Spatial Data

The database uses GEOGRAPHY data type for spatial operations:
- `ports.port_geom` - Port locations
- `vessel_tracking.position_geom` - Vessel positions
- `locations.location_geom` - Location centers

All spatial data uses WGS84 (EPSG:4326) coordinate reference system.

## Data Sources

The database integrates data from multiple government sources:

- **NOAA**: Vessel traffic data, AIS data
- **US Coast Guard**: NOAD data, AIS static data, vessel tracking
- **MARAD**: U.S.-Flag Fleet data, port statistics
- **Data.gov**: Maritime datasets, port schedules

## Compatibility

The database schema is compatible with:
- PostgreSQL (with PostGIS for spatial operations)
 (Delta Lake)


---
**Last Updated:** 2026-02-04
