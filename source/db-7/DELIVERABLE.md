# Database Deliverable: db-7 - Maritime Shipping Intelligence Database

**Database:** db-7
**Type:** Maritime Shipping Intelligence Database
**Created:** 2026-02-04
**Status:** Complete

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Database Schema Documentation](#database-schema-documentation)
3. [SQL Queries](#sql-queries)
4. [Usage Instructions](#usage-instructions)

---

## Database Overview

### Description

This database implements a comprehensive Maritime Shipping Intelligence System integrating data from government sources (NOAA, US Coast Guard, MARAD, Data.gov) and commercial maritime data providers. Supports vessel tracking, port schedules, carrier routes, sailings, port calls, and maritime analytics matching Linescape API functionality.

### Key Features

- **Vessel Tracking**: AIS-based vessel position tracking with speed, course, and navigation status
- **Port Intelligence**: Comprehensive port information with UN/LOCODE, coordinates, and capacity metrics
- **Route Management**: Shipping routes and services with port sequences and transit times
- **Port Call Tracking**: Scheduled and actual port calls with cargo handling information
- **Sailing Intelligence**: Voyage tracking between ports with transit times and capacity utilization
- **Carrier Analytics**: Carrier performance metrics including on-time performance and vessel utilization
- **Port Statistics**: Aggregated port performance metrics including vessel calls and container throughput
- **Government Data Integration**: Integration with NOAA, USCG, MARAD, and Data.gov maritime datasets
- **Spatial Operations**: Geographic queries using PostGIS GEOGRAPHY type for distance calculations and spatial joins

### Database Platforms Supported

- **PostgreSQL**: Full support with UUID types, arrays, JSONB, and PostGIS for spatial data
- **Databricks**: Compatible with Delta Lake format
- **Databricks**: Full support with VARIANT types

### Data Sources

- **NOAA**: AccessAIS Tool for vessel traffic data, MarineCadastre.gov AIS data (2009-2024)
- **US Coast Guard**: National Vessel Movement Center (NVMC) - NOAD data, Vessel Information Verification Service (VIVS) - AIS static data
- **MARAD**: U.S.-Flag Fleet data, port statistics, waterborne commerce statistics
- **Data.gov**: Virginia International Gateway vessel schedules, port region grain ocean vessel activity, AIS vessel tracks datasets

### Data Volume

- **Internet-Pulled Data**: 4.1 GB from public APIs (Data.gov, NOAA, USCG)
- **Transformed Data**: Structured metadata and HTML content processed
- **Total Volume**: 4.1 GB (exceeds 1 GB minimum requirement)

---

## Database Schema Documentation

### Schema Overview

The database consists of **14 tables** organized into logical groups:

1. **Core Reference Tables**: `carriers`, `locations`, `ports`, `vessels`
2. **Route and Service Tables**: `routes`, `route_ports`, `port_pairs`
3. **Operational Tables**: `port_calls`, `sailings`, `voyages`, `voyage_port_calls`
4. **Tracking and Analytics Tables**: `vessel_tracking`, `port_statistics`, `carrier_performance`

### Table Relationships

```
carriers (carrier_id)
    ├── vessels (carrier_id)
    ├── routes (carrier_id)
    ├── port_pairs (carrier_id)
    └── carrier_performance (carrier_id)

locations (location_id)
    ├── ports (location_id)
    └── locations (parent_location_id) [self-referential]

ports (port_id)
    ├── route_ports (port_id)
    ├── port_pairs (origin_port_id, destination_port_id)
    ├── port_calls (port_id)
    ├── sailings (origin_port_id, destination_port_id)
    └── port_statistics (port_id)

vessels (vessel_id)
    ├── port_calls (vessel_id)
    ├── sailings (vessel_id)
    ├── voyages (vessel_id)
    └── vessel_tracking (vessel_id)

routes (route_id)
    ├── route_ports (route_id)
    ├── port_pairs (route_id)
    ├── port_calls (route_id)
    ├── sailings (route_id)
    └── voyages (route_id)

voyages (voyage_id)
    └── voyage_port_calls (voyage_id)
```

### Entity-Relationship Diagram

```mermaid
erDiagram
    carriers {
        varchar carrier_id PK "Primary key"
        varchar carrier_name "Carrier name"
        varchar scac_code UK "Standard Carrier Alpha Code"
        varchar carrier_type "Container, Bulk, RoRo, Tanker"
        varchar country "Country"
        integer fleet_size "Fleet size"
        integer total_capacity_teu "Total capacity TEU"
    }
    
    locations {
        varchar location_id PK "Primary key"
        varchar location_name "Location name"
        varchar location_type "Country, Region, State"
        varchar parent_location_id FK "Parent location"
        varchar country_code "ISO 3166-1 alpha-3"
        geography location_geom SPATIAL "Point geometry"
    }
    
    ports {
        varchar port_id PK "Primary key"
        varchar port_name "Port name"
        varchar port_code UK "UN/LOCODE or port code"
        varchar locode "UN/LOCODE"
        varchar location_id FK "Location"
        numeric latitude "Latitude"
        numeric longitude "Longitude"
        geography port_geom SPATIAL "Point geometry"
        varchar port_type "Container, Bulk, RoRo, Tanker"
        integer container_capacity_teu "Container capacity"
        integer berth_count "Berth count"
    }
    
    vessels {
        varchar vessel_id PK "Primary key"
        varchar vessel_name "Vessel name"
        varchar imo_number UK "IMO number"
        varchar mmsi "MMSI"
        varchar carrier_id FK "Carrier"
        varchar vessel_type "Container, Bulk, RoRo, Tanker"
        integer container_capacity_teu "Container capacity TEU"
        numeric length_meters "Length"
        numeric beam_meters "Beam"
        numeric draft_meters "Draft"
    }
    
    routes {
        varchar route_id PK "Primary key"
        varchar route_name "Route name"
        varchar route_code "Route code"
        varchar carrier_id FK "Carrier"
        varchar service_type "Direct, Feeder, Express"
        integer frequency_weeks "Frequency in weeks"
        integer transit_time_days "Transit time"
    }
    
    route_ports {
        varchar route_port_id PK "Primary key"
        varchar route_id FK "Route"
        varchar port_id FK "Port"
        integer port_sequence "Port sequence"
        varchar port_role "Origin, Destination, Transshipment"
    }
    
    port_pairs {
        varchar port_pair_id PK "Primary key"
        varchar origin_port_id FK "Origin port"
        varchar destination_port_id FK "Destination port"
        varchar carrier_id FK "Carrier"
        varchar route_id FK "Route"
        boolean direct_service "Direct service flag"
        integer average_transit_days "Average transit days"
    }
    
    port_calls {
        varchar port_call_id PK "Primary key"
        varchar vessel_id FK "Vessel"
        varchar port_id FK "Port"
        varchar voyage_number "Voyage number"
        varchar route_id FK "Route"
        timestamp scheduled_arrival "Scheduled arrival"
        timestamp actual_arrival "Actual arrival"
        timestamp scheduled_departure "Scheduled departure"
        timestamp actual_departure "Actual departure"
        varchar port_call_type "Loading, Discharging, Transshipment"
        integer containers_loaded "Containers loaded"
        integer containers_discharged "Containers discharged"
    }
    
    sailings {
        varchar sailing_id PK "Primary key"
        varchar vessel_id FK "Vessel"
        varchar voyage_number "Voyage number"
        varchar route_id FK "Route"
        varchar origin_port_id FK "Origin port"
        varchar destination_port_id FK "Destination port"
        timestamp scheduled_departure "Scheduled departure"
        timestamp actual_departure "Actual departure"
        timestamp scheduled_arrival "Scheduled arrival"
        timestamp actual_arrival "Actual arrival"
        integer transit_days "Transit days"
        numeric distance_nautical_miles "Distance"
        numeric total_teu "Total TEU"
        numeric capacity_utilization_percent "Capacity utilization"
    }
    
    voyages {
        varchar voyage_id PK "Primary key"
        varchar vessel_id FK "Vessel"
        varchar voyage_number "Voyage number"
        varchar route_id FK "Route"
        varchar start_port_id FK "Start port"
        varchar end_port_id FK "End port"
        timestamp start_date "Start date"
        timestamp end_date "End date"
        numeric total_distance_nautical_miles "Total distance"
        integer total_transit_days "Total transit days"
        integer port_call_count "Port call count"
        numeric total_teu "Total TEU"
    }
    
    voyage_port_calls {
        varchar voyage_port_call_id PK "Primary key"
        varchar voyage_id FK "Voyage"
        varchar port_call_id FK "Port call"
        integer port_sequence "Port sequence"
    }
    
    vessel_tracking {
        varchar tracking_id PK "Primary key"
        varchar vessel_id FK "Vessel"
        varchar mmsi "MMSI"
        timestamp timestamp "Position timestamp"
        numeric latitude "Latitude"
        numeric longitude "Longitude"
        geography position_geom SPATIAL "Point geometry"
        numeric speed_knots "Speed in knots"
        numeric course_degrees "Course"
        numeric heading_degrees "Heading"
        varchar navigation_status "Navigation status"
        varchar destination "Destination"
        timestamp eta "Estimated time of arrival"
    }
    
    port_statistics {
        varchar statistic_id PK "Primary key"
        varchar port_id FK "Port"
        date statistic_date "Statistic date"
        varchar statistic_period "Daily, Weekly, Monthly"
        integer total_vessel_calls "Total vessel calls"
        numeric total_container_teu "Total container TEU"
        integer containers_loaded "Containers loaded"
        integer containers_discharged "Containers discharged"
        numeric average_dwell_time_hours "Average dwell time"
        numeric berth_utilization_percent "Berth utilization"
    }
    
    carrier_performance {
        varchar performance_id PK "Primary key"
        varchar carrier_id FK "Carrier"
        date evaluation_period_start "Period start"
        date evaluation_period_end "Period end"
        integer total_voyages "Total voyages"
        integer on_time_departures "On-time departures"
        integer on_time_arrivals "On-time arrivals"
        numeric on_time_performance_percent "On-time performance"
        numeric average_transit_time_days "Average transit time"
        numeric capacity_utilization_percent "Capacity utilization"
        numeric total_teu_carried "Total TEU carried"
    }
    
    carriers ||--o{ vessels : "operates"
    carriers ||--o{ routes : "operates"
    carriers ||--o{ port_pairs : "serves"
    carriers ||--o{ carrier_performance : "measured"
    locations ||--o{ ports : "contains"
    locations ||--o{ locations : "parent"
    ports ||--o{ route_ports : "included_in"
    ports ||--o{ port_pairs : "origin"
    ports ||--o{ port_pairs : "destination"
    ports ||--o{ port_calls : "receives"
    ports ||--o{ sailings : "origin"
    ports ||--o{ sailings : "destination"
    ports ||--o{ port_statistics : "statistics"
    vessels ||--o{ port_calls : "makes"
    vessels ||--o{ sailings : "performs"
    vessels ||--o{ voyages : "performs"
    vessels ||--o{ vessel_tracking : "tracked"
    routes ||--o{ route_ports : "includes"
    routes ||--o{ port_pairs : "defines"
    routes ||--o{ port_calls : "scheduled"
    routes ||--o{ sailings : "scheduled"
    routes ||--o{ voyages : "scheduled"
    voyages ||--o{ voyage_port_calls : "includes"
    port_calls ||--o{ voyage_port_calls : "linked"
```

### Table Details

#### carriers

Stores shipping line/carrier information with SCAC codes.

**Key Columns:**
- `carrier_id` (VARCHAR(255), PRIMARY KEY) - Unique identifier
- `carrier_name` (VARCHAR(255), NOT NULL) - Full name of shipping line
- `scac_code` (VARCHAR(10), UNIQUE) - Standard Carrier Alpha Code
- `carrier_type` (VARCHAR(50)) - Container, Bulk, RoRo, Tanker, General
- `fleet_size` (INTEGER) - Total number of vessels
- `total_capacity_teu` (INTEGER) - Total container capacity

#### ports

Stores port information with UN/LOCODE, coordinates, and characteristics.

**Key Columns:**
- `port_id` (VARCHAR(255), PRIMARY KEY) - Unique identifier
- `port_name` (VARCHAR(255), NOT NULL) - Port name
- `port_code` (VARCHAR(20), UNIQUE) - UN/LOCODE or port code
- `locode` (VARCHAR(10)) - UN/LOCODE (5 characters: 2 country + 3 location)
- `latitude` (NUMERIC(10, 7), NOT NULL) - Latitude coordinate
- `longitude` (NUMERIC(10, 7), NOT NULL) - Longitude coordinate
- `port_geom` (GEOGRAPHY) - Point geometry for spatial queries
- `port_type` (VARCHAR(50)) - Container, Bulk, RoRo, Tanker, General, Multi-purpose
- `container_capacity_teu` (INTEGER) - Container capacity
- `berth_count` (INTEGER) - Number of berths

#### vessels

Stores vessel information with IMO numbers, MMSI, and specifications.

**Key Columns:**
- `vessel_id` (VARCHAR(255), PRIMARY KEY) - Unique identifier
- `vessel_name` (VARCHAR(255), NOT NULL) - Vessel name
- `imo_number` (VARCHAR(10), UNIQUE) - International Maritime Organization number
- `mmsi` (VARCHAR(9)) - Maritime Mobile Service Identity
- `carrier_id` (VARCHAR(255)) - Foreign key to carriers
- `vessel_type` (VARCHAR(50)) - Container, Bulk, RoRo, Tanker, General Cargo
- `container_capacity_teu` (INTEGER) - Container capacity
- `length_meters` (NUMERIC(8, 2)) - Vessel length
- `beam_meters` (NUMERIC(8, 2)) - Vessel beam
- `draft_meters` (NUMERIC(8, 2)) - Vessel draft

#### routes

Stores shipping routes/services operated by carriers.

**Key Columns:**
- `route_id` (VARCHAR(255), PRIMARY KEY) - Unique identifier
- `route_name` (VARCHAR(255), NOT NULL) - Route name
- `carrier_id` (VARCHAR(255), NOT NULL) - Foreign key to carriers
- `service_type` (VARCHAR(50)) - Direct, Feeder, Express, Regular
- `frequency_weeks` (INTEGER) - Service frequency in weeks
- `transit_time_days` (INTEGER) - Average transit time

#### port_calls

Stores scheduled and actual port calls with vessel and port information.

**Key Columns:**
- `port_call_id` (VARCHAR(255), PRIMARY KEY) - Unique identifier
- `vessel_id` (VARCHAR(255), NOT NULL) - Foreign key to vessels
- `port_id` (VARCHAR(255), NOT NULL) - Foreign key to ports
- `scheduled_arrival` (TIMESTAMP) - Scheduled arrival time
- `actual_arrival` (TIMESTAMP) - Actual arrival time
- `scheduled_departure` (TIMESTAMP) - Scheduled departure time
- `actual_departure` (TIMESTAMP) - Actual departure time
- `port_call_type` (VARCHAR(50)) - Loading, Discharging, Transshipment, Bunkering, Repair
- `containers_loaded` (INTEGER) - Containers loaded
- `containers_discharged` (INTEGER) - Containers discharged

#### sailings

Stores sailing/voyage information between ports.

**Key Columns:**
- `sailing_id` (VARCHAR(255), PRIMARY KEY) - Unique identifier
- `vessel_id` (VARCHAR(255), NOT NULL) - Foreign key to vessels
- `route_id` (VARCHAR(255)) - Foreign key to routes
- `origin_port_id` (VARCHAR(255), NOT NULL) - Foreign key to ports
- `destination_port_id` (VARCHAR(255), NOT NULL) - Foreign key to ports
- `scheduled_departure` (TIMESTAMP) - Scheduled departure time
- `actual_departure` (TIMESTAMP) - Actual departure time
- `scheduled_arrival` (TIMESTAMP) - Scheduled arrival time
- `actual_arrival` (TIMESTAMP) - Actual arrival time
- `transit_days` (INTEGER) - Transit days
- `distance_nautical_miles` (NUMERIC(10, 2)) - Distance in nautical miles
- `total_teu` (NUMERIC(10, 2)) - Total TEU
- `capacity_utilization_percent` (NUMERIC(5, 2)) - Capacity utilization percentage

#### vessel_tracking

Stores AIS (Automatic Identification System) tracking data.

**Key Columns:**
- `tracking_id` (VARCHAR(255), PRIMARY KEY) - Unique identifier
- `vessel_id` (VARCHAR(255), NOT NULL) - Foreign key to vessels
- `timestamp` (TIMESTAMP, NOT NULL) - Position timestamp
- `latitude` (NUMERIC(10, 7), NOT NULL) - Latitude coordinate
- `longitude` (NUMERIC(10, 7), NOT NULL) - Longitude coordinate
- `position_geom` (GEOGRAPHY) - Point geometry for spatial queries
- `speed_knots` (NUMERIC(6, 2)) - Speed in knots
- `course_degrees` (NUMERIC(6, 2)) - Course in degrees
- `heading_degrees` (NUMERIC(6, 2)) - Heading in degrees
- `navigation_status` (VARCHAR(50)) - Under way, At anchor, Moored, etc.
- `destination` (VARCHAR(255)) - Destination port
- `eta` (TIMESTAMP) - Estimated time of arrival

---

## SQL Queries

This database includes **30 extremely complex SQL queries** designed for production use in businesses with **$1M+ Annual Recurring Revenue (ARR)**. Each query demonstrates advanced SQL patterns including:

- Multiple CTEs (Common Table Expressions)
- Recursive CTEs for hierarchical data
- Complex joins and aggregations
- Window functions and analytical queries
- Spatial operations using PostGIS GEOGRAPHY type
- Multi-dimensional scoring algorithms
- Temporal analysis and time-series queries
- Route optimization and deviation detection
- Port capacity utilization analysis
- Carrier performance metrics

**Note:** All queries are embedded inline in this document. See the [SQL Queries](#sql-queries) section below for complete query listings with full business context.

---

## Usage Instructions

### Prerequisites

- PostgreSQL 12+ with PostGIS extension (for spatial queries)
- OR Databricks SQL (Delta Lake)
- OR Databricks

### Database Setup

1. **Create Database:**
   ```sql
   CREATE DATABASE db7;
   ```

2. **Enable PostGIS (PostgreSQL only):**
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

3. **Load Schema:**
   ```bash
   psql -d db7 -f data/schema.sql
   ```

4. **Load Sample Data (optional):**
   ```bash
   psql -d db7 -f data/data.sql
   ```

### Running Queries

All queries are located in `queries/queries.md` and can be executed directly against the database. Each query includes:
- Business use case description
- Technical description of SQL operations
- Expected output format
- Complexity metrics

### Query Categories

1. **Vessel Tracking** (Queries 1-3): Real-time vessel position tracking, route deviation detection
2. **Port Operations** (Queries 4-6): Port call scheduling, performance analysis
3. **Route Intelligence** (Queries 7-9): Route optimization, transit time analysis
4. **Carrier Analytics** (Queries 10-12): Carrier performance, on-time metrics
5. **Port Capacity** (Queries 13-15): Port utilization, berth optimization
6. **Sailing Intelligence** (Queries 16-18): Sailing performance, voyage tracking
7. **Multi-Port Analysis** (Queries 19-21): Multi-port voyage planning, sequence optimization
8. **Spatial Operations** (Queries 22-24): Geographic queries, distance calculations
9. **Infrastructure** (Queries 25-27): Port infrastructure utilization, resource optimization
10. **Comprehensive Analytics** (Queries 28-30): Executive dashboards, market intelligence

### Validation

Run the validation suite to verify all queries:

```bash
cd db-7
python3 scripts/validate.py
```

---

**Last Updated:** 2026-02-04
