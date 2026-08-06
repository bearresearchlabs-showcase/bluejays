# Data Dictionary - Maritime Shipping Intelligence Database (db-7)

## Overview

This data dictionary provides detailed descriptions of all tables and columns in the Maritime Shipping Intelligence Database. The database is designed to support maritime schedules, shipping intelligence, vessel tracking, port operations, and carrier performance analysis.

**Database Type:** Maritime Shipping Intelligence  
**Compatibility:** PostgreSQL (with PostGIS) (Delta Lake)  
**Total Tables:** 14  
**Last Updated:** 2026-02-04

---

## Table of Contents

1. [carriers](#carriers)
2. [locations](#locations)
3. [ports](#ports)
4. [vessels](#vessels)
5. [routes](#routes)
6. [route_ports](#route_ports)
7. [port_pairs](#port_pairs)
8. [port_calls](#port_calls)
9. [sailings](#sailings)
10. [voyages](#voyages)
11. [voyage_port_calls](#voyage_port_calls)
12. [vessel_tracking](#vessel_tracking)
13. [port_statistics](#port_statistics)
14. [carrier_performance](#carrier_performance)

---

## carriers

**Purpose:** Stores shipping line and carrier information including company details, fleet statistics, and contact information.

**Business Context:** Carriers are the shipping lines that operate vessels and provide maritime transportation services. This table serves as the master reference for all carriers in the system.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| carrier_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the carrier (e.g., 'MAEU', 'COSCO', 'MSC'). |
| carrier_name | VARCHAR(255) | NOT NULL | Full name of the shipping line/carrier (e.g., 'Maersk Line', 'COSCO Shipping Lines'). |
| scac_code | VARCHAR(10) | NULL | Standard Carrier Alpha Code - unique 4-letter code used in transportation (e.g., 'MAEU', 'COSU'). |
| carrier_type | VARCHAR(50) | NULL | Type of carrier operations: 'Container', 'Bulk', 'RoRo', 'Tanker', 'General'. |
| country | VARCHAR(100) | NULL | Country where the carrier is headquartered (e.g., 'Denmark', 'China'). |
| website | VARCHAR(500) | NULL | Official website URL of the carrier. |
| contact_email | VARCHAR(255) | NULL | Primary contact email address for the carrier. |
| contact_phone | VARCHAR(50) | NULL | Primary contact phone number for the carrier. |
| status | VARCHAR(50) | NULL | Operational status: 'Active', 'Inactive', 'Suspended'. Default: 'Active'. |
| fleet_size | INTEGER | NULL | Total number of vessels in the carrier's fleet. |
| total_capacity_teu | INTEGER | NULL | Total container capacity of the carrier's fleet in TEU (Twenty-foot Equivalent Units). |
| established_year | INTEGER | NULL | Year the carrier was established. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `carrier_id`
- Unique: `scac_code`

**Relationships:**
- One-to-many with `vessels` (carrier_id)
- One-to-many with `routes` (carrier_id)
- One-to-many with `port_pairs` (carrier_id)
- One-to-many with `carrier_performance` (carrier_id)

---

## locations

**Purpose:** Stores geographic location information including countries, regions, states, and provinces with spatial data.

**Business Context:** Locations provide hierarchical geographic organization for ports and other maritime entities. Supports spatial queries and geographic analysis.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| location_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the location. |
| location_name | VARCHAR(255) | NOT NULL | Name of the location (e.g., 'United States', 'California', 'Los Angeles'). |
| location_type | VARCHAR(50) | NOT NULL | Type of location: 'Country', 'Region', 'State', 'Province', 'City'. |
| parent_location_id | VARCHAR(255) | NULL | Foreign key to locations.location_id. Parent location in hierarchy (e.g., state's country). |
| country_code | VARCHAR(3) | NULL | ISO 3166-1 alpha-3 country code (e.g., 'USA', 'CHN', 'DEU'). |
| region_code | VARCHAR(10) | NULL | Regional code (e.g., state code, province code). |
| latitude | NUMERIC(10, 7) | NULL | Latitude coordinate of location center (WGS84, EPSG:4326). |
| longitude | NUMERIC(10, 7) | NULL | Longitude coordinate of location center (WGS84, EPSG:4326). |
| location_geom | GEOGRAPHY | NULL | Point geometry for location center. Spatial data type for geographic queries. |
| spatial_extent_west | NUMERIC(10, 6) | NULL | Western boundary of location bounding box (longitude). |
| spatial_extent_south | NUMERIC(10, 6) | NULL | Southern boundary of location bounding box (latitude). |
| spatial_extent_east | NUMERIC(10, 6) | NULL | Eastern boundary of location bounding box (longitude). |
| spatial_extent_north | NUMERIC(10, 6) | NULL | Northern boundary of location bounding box (latitude). |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `location_id`
- Spatial Index: `location_geom` (GIST index on PostgreSQL PostGIS)

**Relationships:**
- Self-referential: `parent_location_id` → `locations.location_id`
- One-to-many with `ports` (location_id)

**Spatial Data:**
- Uses `GEOGRAPHY` type for spatial operations (ST_DISTANCE, ST_WITHIN, etc.)
- Coordinates in WGS84 (EPSG:4326) format
- Bounding box stored for efficient spatial queries

---

## ports

**Purpose:** Stores comprehensive port information including location, physical characteristics, infrastructure, and operational details.

**Business Context:** Ports are the critical nodes in maritime transportation networks. This table contains detailed information about port facilities, capabilities, and characteristics used for route planning and operations.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| port_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the port. |
| port_name | VARCHAR(255) | NOT NULL | Official name of the port (e.g., 'Port of Los Angeles', 'Port of Shanghai'). |
| port_code | VARCHAR(20) | NULL | Unique port code identifier. May be UN/LOCODE or custom port code. |
| locode | VARCHAR(10) | NULL | UN/LOCODE (United Nations Code for Trade and Transport Locations). 5-character code: 2-letter country code + 3-letter location code (e.g., 'USLAX' for Los Angeles). |
| location_id | VARCHAR(255) | NULL | Foreign key to locations.location_id. Geographic location reference. |
| country | VARCHAR(100) | NULL | Country where the port is located (e.g., 'United States', 'China'). |
| country_code | VARCHAR(3) | NULL | ISO 3166-1 alpha-3 country code (e.g., 'USA', 'CHN'). |
| latitude | NUMERIC(10, 7) | NOT NULL | Latitude coordinate of port location (WGS84, EPSG:4326). |
| longitude | NUMERIC(10, 7) | NOT NULL | Longitude coordinate of port location (WGS84, EPSG:4326). |
| port_geom | GEOGRAPHY | NULL | Point geometry for port location. Spatial data type for geographic queries and distance calculations. |
| port_type | VARCHAR(50) | NULL | Type of port: 'Container', 'Bulk', 'RoRo', 'Tanker', 'General', 'Multi-purpose'. |
| timezone | VARCHAR(50) | NULL | Timezone of the port (e.g., 'America/Los_Angeles', 'Asia/Shanghai'). |
| depth_meters | NUMERIC(8, 2) | NULL | Maximum depth of port in meters. Determines vessel size capacity. |
| max_vessel_length_meters | NUMERIC(8, 2) | NULL | Maximum vessel length that can be accommodated in meters. |
| max_vessel_draft_meters | NUMERIC(8, 2) | NULL | Maximum vessel draft (depth below waterline) in meters. |
| container_capacity_teu | INTEGER | NULL | Annual container handling capacity in TEU (Twenty-foot Equivalent Units). |
| berth_count | INTEGER | NULL | Number of berths available at the port. |
| crane_count | INTEGER | NULL | Number of container cranes available at the port. |
| status | VARCHAR(50) | NULL | Port operational status: 'Active', 'Inactive', 'Under Maintenance'. Default: 'Active'. |
| data_source | VARCHAR(100) | NULL | Source of port data: 'MARAD', 'NOAA', 'USCG', 'Linescape', 'Port Authority', etc. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `port_id`
- Unique: `port_code`
- Index: `idx_ports_location` on `location_id`
- Index: `idx_ports_locode` on `locode`
- Index: `idx_ports_country` on `country_code`
- Spatial Index: `port_geom` (GIST index on PostgreSQL PostGIS)

**Relationships:**
- Many-to-one with `locations` (location_id)
- One-to-many with `route_ports` (port_id)
- One-to-many with `port_pairs` (origin_port_id, destination_port_id)
- One-to-many with `port_calls` (port_id)
- One-to-many with `port_statistics` (port_id)

**Spatial Data:**
- Uses `GEOGRAPHY` type for spatial operations
- Coordinates in WGS84 (EPSG:4326) format
- Used for distance calculations, route optimization, and geographic analysis

---

## vessels

**Purpose:** Stores comprehensive vessel information including identification numbers, physical characteristics, capacity, and operational details.

**Business Context:** Vessels are the physical assets that transport cargo. This table contains detailed vessel specifications used for capacity planning, route assignment, and fleet management.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| vessel_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the vessel. |
| vessel_name | VARCHAR(255) | NOT NULL | Official name of the vessel (e.g., 'MSC OSCAR', 'EVERGREEN ACE'). |
| imo_number | VARCHAR(10) | NULL | International Maritime Organization number. Unique 7-digit identifier assigned to vessels. Format: IMO1234567. |
| mmsi | VARCHAR(9) | NULL | Maritime Mobile Service Identity. 9-digit number used for AIS tracking and communication. |
| call_sign | VARCHAR(20) | NULL | Radio call sign assigned to the vessel for communication. |
| carrier_id | VARCHAR(255) | NULL | Foreign key to carriers.carrier_id. Shipping line that operates the vessel. |
| vessel_type | VARCHAR(50) | NULL | Type of vessel: 'Container', 'Bulk', 'RoRo', 'Tanker', 'General Cargo'. |
| flag_country | VARCHAR(100) | NULL | Country of vessel registration/flag (e.g., 'Panama', 'Liberia', 'Marshall Islands'). |
| flag_country_code | VARCHAR(3) | NULL | ISO 3166-1 alpha-3 country code for flag country. |
| year_built | INTEGER | NULL | Year the vessel was built. Used for age analysis and fleet modernization. |
| gross_tonnage | INTEGER | NULL | Gross tonnage (GT) - total internal volume of the vessel in tons. |
| net_tonnage | INTEGER | NULL | Net tonnage (NT) - usable internal volume of the vessel in tons. |
| deadweight_tonnage | INTEGER | NULL | Deadweight tonnage (DWT) - maximum weight vessel can carry including cargo, fuel, etc. |
| length_meters | NUMERIC(8, 2) | NULL | Overall length of the vessel in meters. |
| beam_meters | NUMERIC(8, 2) | NULL | Width of the vessel at its widest point in meters. |
| draft_meters | NUMERIC(8, 2) | NULL | Depth of vessel below waterline in meters. Determines port accessibility. |
| max_speed_knots | NUMERIC(6, 2) | NULL | Maximum operating speed of the vessel in knots. |
| container_capacity_teu | INTEGER | NULL | Total container capacity in TEU (Twenty-foot Equivalent Units). |
| container_capacity_twenty_foot | INTEGER | NULL | Capacity for 20-foot containers (TEU basis). |
| container_capacity_forty_foot | INTEGER | NULL | Capacity for 40-foot containers (FEU - Forty-foot Equivalent Units). |
| status | VARCHAR(50) | NULL | Vessel operational status: 'Active', 'Inactive', 'Under Repair', 'Scrapped'. Default: 'Active'. |
| data_source | VARCHAR(100) | NULL | Source of vessel data: 'USCG', 'NOAA', 'MARAD', 'Linescape', 'IMO', etc. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `vessel_id`
- Unique: `imo_number`
- Index: `idx_vessels_carrier` on `carrier_id`
- Index: `idx_vessels_imo` on `imo_number`
- Index: `idx_vessels_mmsi` on `mmsi`

**Relationships:**
- Many-to-one with `carriers` (carrier_id)
- One-to-many with `port_calls` (vessel_id)
- One-to-many with `sailings` (vessel_id)
- One-to-many with `voyages` (vessel_id)
- One-to-many with `vessel_tracking` (vessel_id)

**Business Notes:**
- IMO number is the most reliable vessel identifier (permanent, never changes)
- MMSI is used for AIS tracking and real-time vessel monitoring
- Container capacity determines vessel deployment and route assignment

---

## routes

**Purpose:** Stores shipping route/service information including route characteristics, frequency, and operational details.

**Business Context:** Routes define the services operated by carriers between ports. This table contains route specifications used for schedule planning, service analysis, and route optimization.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| route_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the route/service. |
| route_name | VARCHAR(255) | NOT NULL | Name of the route/service (e.g., 'Asia-Europe Express', 'Trans-Pacific Loop 1'). |
| route_code | VARCHAR(100) | NULL | Route code or service code used by the carrier (e.g., 'AE1', 'TP1'). |
| carrier_id | VARCHAR(255) | NOT NULL | Foreign key to carriers.carrier_id. Carrier operating this route. |
| service_type | VARCHAR(50) | NULL | Type of service: 'Direct', 'Feeder', 'Express', 'Regular'. |
| route_type | VARCHAR(50) | NULL | Geographic route type: 'Trans-Pacific', 'Trans-Atlantic', 'Asia-Europe', 'Intra-Asia', 'Coastal', etc. |
| frequency_weeks | INTEGER | NULL | Service frequency in weeks (e.g., 1 = weekly, 2 = bi-weekly). |
| transit_time_days | INTEGER | NULL | Average transit time for the route in days. |
| status | VARCHAR(50) | NULL | Route operational status: 'Active', 'Suspended', 'Discontinued'. Default: 'Active'. |
| start_date | DATE | NULL | Date when the route/service started operations. |
| end_date | DATE | NULL | Date when the route/service ended or is scheduled to end. NULL for active routes. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `route_id`
- Index: `idx_routes_carrier` on `carrier_id`

**Relationships:**
- Many-to-one with `carriers` (carrier_id)
- One-to-many with `route_ports` (route_id)
- One-to-many with `port_pairs` (route_id)
- One-to-many with `port_calls` (route_id)
- One-to-many with `sailings` (route_id)
- One-to-many with `voyages` (route_id)

**Business Notes:**
- Routes define the service pattern but actual sailings may vary
- Frequency determines service schedule and capacity planning
- Route type helps categorize and analyze trade lanes

---

## route_ports

**Purpose:** Junction table linking routes to ports, defining the sequence of port calls in a route.

**Business Context:** Routes consist of multiple port calls in a specific sequence. This table defines which ports are included in each route and their order, enabling route path analysis and port call sequencing.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| route_port_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the route-port relationship. |
| route_id | VARCHAR(255) | NOT NULL | Foreign key to routes.route_id. Route containing this port call. |
| port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Port included in the route. |
| port_sequence | INTEGER | NOT NULL | Order of port call in the route (1 = first port, 2 = second port, etc.). |
| port_role | VARCHAR(50) | NULL | Role of the port in the route: 'Origin', 'Destination', 'Transshipment', 'Intermediate'. |
| estimated_days_from_start | INTEGER | NULL | Estimated number of days from route start to reach this port. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `route_port_id`
- Unique: `(route_id, port_id, port_sequence)`
- Index: `idx_route_ports_route` on `route_id`
- Index: `idx_route_ports_port` on `port_id`

**Relationships:**
- Many-to-one with `routes` (route_id)
- Many-to-one with `ports` (port_id)

**Business Notes:**
- Port sequence determines the order of port calls in a route
- Port role helps identify origin/destination vs. transshipment ports
- Used for route path analysis and multi-port voyage planning

---

## port_pairs

**Purpose:** Stores origin-destination port pair relationships for carriers, including service characteristics.

**Business Context:** Port pairs represent direct service connections between two ports. This table tracks which carriers offer service between specific port pairs, enabling demand analysis and route optimization.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| port_pair_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the port pair. |
| origin_port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Origin port of the pair. |
| destination_port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Destination port of the pair. |
| carrier_id | VARCHAR(255) | NOT NULL | Foreign key to carriers.carrier_id. Carrier offering service on this port pair. |
| route_id | VARCHAR(255) | NULL | Foreign key to routes.route_id. Route that includes this port pair. |
| direct_service | BOOLEAN | NULL | TRUE if carrier offers direct service (no transshipment). FALSE if transshipment required. Default: FALSE. |
| transshipment_required | BOOLEAN | NULL | TRUE if transshipment is required for this port pair. Default: FALSE. |
| average_transit_days | INTEGER | NULL | Average transit time for this port pair in days. |
| service_frequency_weeks | INTEGER | NULL | Service frequency for this port pair in weeks. |
| last_sailing_date | DATE | NULL | Date of the last sailing on this port pair. |
| status | VARCHAR(50) | NULL | Port pair status: 'Active', 'Inactive', 'Discontinued'. Default: 'Active'. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `port_pair_id`
- Unique: `(origin_port_id, destination_port_id, carrier_id)`
- Index: `idx_port_pairs_origin` on `origin_port_id`
- Index: `idx_port_pairs_destination` on `destination_port_id`
- Index: `idx_port_pairs_carrier` on `carrier_id`

**Relationships:**
- Many-to-one with `ports` (origin_port_id)
- Many-to-one with `ports` (destination_port_id)
- Many-to-one with `carriers` (carrier_id)
- Many-to-one with `routes` (route_id)

**Business Notes:**
- Port pairs enable trade flow analysis and demand forecasting
- Direct service flag indicates service quality and transit time
- Used for port pair demand analysis and market opportunity identification

---

## port_calls

**Purpose:** Stores scheduled and actual port call information including arrival/departure times, cargo operations, and operational status.

**Business Context:** Port calls represent vessel visits to ports for loading, discharging, or transshipment. This table tracks actual port operations, enabling port performance analysis, delay tracking, and operational optimization.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| port_call_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the port call. |
| vessel_id | VARCHAR(255) | NOT NULL | Foreign key to vessels.vessel_id. Vessel making the port call. |
| port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Port where the call is made. |
| sailing_id | VARCHAR(255) | NULL | Foreign key to sailings.sailing_id. Sailing associated with this port call. |
| voyage_number | VARCHAR(100) | NULL | Voyage number for the port call. Links to voyage records. |
| route_id | VARCHAR(255) | NULL | Foreign key to routes.route_id. Route associated with this port call. |
| scheduled_arrival | TIMESTAMP_NTZ | NULL | Scheduled arrival time at the port. |
| actual_arrival | TIMESTAMP_NTZ | NULL | Actual arrival time at the port. Used for delay analysis. |
| scheduled_departure | TIMESTAMP_NTZ | NULL | Scheduled departure time from the port. |
| actual_departure | TIMESTAMP_NTZ | NULL | Actual departure time from the port. Used for dwell time calculation. |
| port_call_type | VARCHAR(50) | NULL | Type of port call: 'Loading', 'Discharging', 'Transshipment', 'Bunkering', 'Repair'. |
| berth_number | VARCHAR(50) | NULL | Berth number assigned for the port call. |
| terminal_name | VARCHAR(255) | NULL | Terminal name where the port call is made. |
| cargo_type | VARCHAR(100) | NULL | Type of cargo handled: 'Container', 'Bulk', 'Breakbulk', etc. |
| containers_loaded | INTEGER | NULL | Number of containers loaded during the port call. |
| containers_discharged | INTEGER | NULL | Number of containers discharged during the port call. |
| containers_transshipped | INTEGER | NULL | Number of containers transshipped (transferred to another vessel) during the port call. |
| total_containers | INTEGER | NULL | Total containers handled (loaded + discharged + transshipped). |
| status | VARCHAR(50) | NULL | Port call status: 'Scheduled', 'In Progress', 'Completed', 'Cancelled'. Default: 'Scheduled'. |
| delay_hours | NUMERIC(8, 2) | NULL | Delay in hours from scheduled arrival. Positive = delayed, negative = early. |
| data_source | VARCHAR(100) | NULL | Source of port call data: 'AIS', 'NOAD', 'MARAD', 'Linescape', 'Port Authority', etc. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `port_call_id`
- Index: `idx_port_calls_vessel` on `vessel_id`
- Index: `idx_port_calls_port` on `port_id`
- Index: `idx_port_calls_route` on `route_id`
- Index: `idx_port_calls_arrival` on `(scheduled_arrival, actual_arrival)`

**Relationships:**
- Many-to-one with `vessels` (vessel_id)
- Many-to-one with `ports` (port_id)
- Many-to-one with `sailings` (sailing_id)
- Many-to-one with `routes` (route_id)
- One-to-many with `voyage_port_calls` (port_call_id)

**Business Notes:**
- Actual vs. scheduled times enable delay analysis and on-time performance metrics
- Container counts support throughput analysis and port capacity utilization
- Port call type determines operational requirements and resource allocation

---

## sailings

**Purpose:** Stores sailing/voyage information between origin and destination ports, including schedule, performance, and cargo details.

**Business Context:** Sailings represent individual vessel movements between two ports. This table tracks sailing performance, capacity utilization, and transit times, enabling route analysis and service quality monitoring.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| sailing_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the sailing. |
| vessel_id | VARCHAR(255) | NOT NULL | Foreign key to vessels.vessel_id. Vessel performing the sailing. |
| carrier_id | VARCHAR(255) | NULL | Foreign key to carriers.carrier_id. Carrier operating the sailing. |
| voyage_number | VARCHAR(100) | NULL | Voyage number for the sailing. Links to voyage records. |
| route_id | VARCHAR(255) | NULL | Foreign key to routes.route_id. Route associated with the sailing. |
| origin_port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Origin port of the sailing. |
| destination_port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Destination port of the sailing. |
| scheduled_departure | TIMESTAMP_NTZ | NULL | Scheduled departure time from origin port. |
| actual_departure | TIMESTAMP_NTZ | NULL | Actual departure time from origin port. Used for delay analysis. |
| scheduled_arrival | TIMESTAMP_NTZ | NULL | Scheduled arrival time at destination port. |
| actual_arrival | TIMESTAMP_NTZ | NULL | Actual arrival time at destination port. Used for transit time and delay analysis. |
| transit_days | INTEGER | NULL | Transit time in days (scheduled or actual). |
| distance_nautical_miles | NUMERIC(10, 2) | NULL | Distance traveled in nautical miles. May be great circle distance or actual route distance. |
| average_speed_knots | NUMERIC(6, 2) | NULL | Average speed during the sailing in knots. |
| cargo_type | VARCHAR(100) | NULL | Type of cargo carried: 'Container', 'Bulk', 'Breakbulk', etc. |
| total_containers | INTEGER | NULL | Total number of containers carried. |
| total_teu | NUMERIC(10, 2) | NULL | Total TEU (Twenty-foot Equivalent Units) carried. |
| capacity_utilization_percent | NUMERIC(5, 2) | NULL | Percentage of vessel capacity utilized (0-100). |
| transshipment_count | INTEGER | NULL | Number of transshipment stops during the sailing. Default: 0. |
| status | VARCHAR(50) | NULL | Sailing status: 'Scheduled', 'In Transit', 'Completed', 'Cancelled'. Default: 'Scheduled'. |
| data_source | VARCHAR(100) | NULL | Source of sailing data: 'AIS', 'NOAD', 'MARAD', 'Linescape', etc. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `sailing_id`
- Index: `idx_sailings_vessel` on `vessel_id`
- Index: `idx_sailings_origin` on `origin_port_id`
- Index: `idx_sailings_destination` on `destination_port_id`
- Index: `idx_sailings_departure` on `(scheduled_departure, actual_departure)`

**Relationships:**
- Many-to-one with `vessels` (vessel_id)
- Many-to-one with `carriers` (carrier_id)
- Many-to-one with `routes` (route_id)
- Many-to-one with `ports` (origin_port_id)
- Many-to-one with `ports` (destination_port_id)
- One-to-many with `port_calls` (sailing_id)

**Business Notes:**
- Capacity utilization is a key performance metric for fleet optimization
- Transit time and distance enable route efficiency analysis
- Actual vs. scheduled times support on-time performance tracking

---

## voyages

**Purpose:** Stores complete voyage information from start port to end port, including multi-port voyage details.

**Business Context:** Voyages represent complete vessel journeys that may include multiple port calls. This table aggregates voyage-level metrics for voyage completion analysis and multi-port route optimization.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| voyage_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the voyage. |
| vessel_id | VARCHAR(255) | NOT NULL | Foreign key to vessels.vessel_id. Vessel performing the voyage. |
| voyage_number | VARCHAR(100) | NOT NULL | Voyage number identifier. Unique within carrier/vessel. |
| route_id | VARCHAR(255) | NULL | Foreign key to routes.route_id. Route associated with the voyage. |
| start_port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Starting port of the voyage. |
| end_port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Ending port of the voyage. |
| scheduled_start_date | TIMESTAMP_NTZ | NULL | Scheduled start date/time of the voyage. |
| actual_start_date | TIMESTAMP_NTZ | NULL | Actual start date/time of the voyage. |
| scheduled_end_date | TIMESTAMP_NTZ | NULL | Scheduled end date/time of the voyage. |
| actual_end_date | TIMESTAMP_NTZ | NULL | Actual end date/time of the voyage. |
| total_distance_nautical_miles | NUMERIC(10, 2) | NULL | Total distance traveled during the voyage in nautical miles. |
| total_transit_days | INTEGER | NULL | Total transit time for the voyage in days. |
| port_call_count | INTEGER | NULL | Number of port calls in the voyage. |
| transshipment_count | INTEGER | NULL | Number of transshipment stops during the voyage. Default: 0. |
| total_containers | INTEGER | NULL | Total containers handled during the voyage. |
| total_teu | NUMERIC(10, 2) | NULL | Total TEU handled during the voyage. |
| status | VARCHAR(50) | NULL | Voyage status: 'Scheduled', 'In Progress', 'Completed', 'Cancelled'. Default: 'In Progress'. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `voyage_id`
- Index: `idx_voyages_vessel` on `vessel_id`
- Index: `idx_voyages_route` on `route_id`
- Index: `idx_voyages_start_date` on `scheduled_start_date`

**Relationships:**
- Many-to-one with `vessels` (vessel_id)
- Many-to-one with `routes` (route_id)
- Many-to-one with `ports` (start_port_id)
- Many-to-one with `ports` (end_port_id)
- One-to-many with `voyage_port_calls` (voyage_id)

**Business Notes:**
- Voyages aggregate multiple port calls and sailings
- Port call count indicates voyage complexity
- Used for voyage completion rate analysis and multi-port route optimization

---

## voyage_port_calls

**Purpose:** Junction table linking voyages to port calls, defining the sequence of port calls within a voyage.

**Business Context:** Voyages consist of multiple port calls in sequence. This table links voyage records to individual port calls, enabling voyage path analysis and port call sequencing.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| voyage_port_call_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the voyage-port call relationship. |
| voyage_id | VARCHAR(255) | NOT NULL | Foreign key to voyages.voyage_id. Voyage containing this port call. |
| port_call_id | VARCHAR(255) | NOT NULL | Foreign key to port_calls.port_call_id. Port call included in the voyage. |
| port_sequence | INTEGER | NULL | Order of port call in the voyage (1 = first port, 2 = second port, etc.). |
| scheduled_arrival | TIMESTAMP_NTZ | NULL | Scheduled arrival time for this port call in the voyage context. |
| actual_arrival | TIMESTAMP_NTZ | NULL | Actual arrival time for this port call in the voyage context. |
| scheduled_departure | TIMESTAMP_NTZ | NULL | Scheduled departure time for this port call in the voyage context. |
| actual_departure | TIMESTAMP_NTZ | NULL | Actual departure time for this port call in the voyage context. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `voyage_port_call_id`
- Unique: `(voyage_id, port_call_id)`
- Index: `idx_voyage_port_calls_voyage` on `voyage_id`
- Index: `idx_voyage_port_calls_port_call` on `port_call_id`

**Relationships:**
- Many-to-one with `voyages` (voyage_id)
- Many-to-one with `port_calls` (port_call_id)

**Business Notes:**
- Links voyage-level records to detailed port call records
- Port sequence enables voyage path analysis
- Used for multi-port route optimization and voyage completion tracking

---

## vessel_tracking

**Purpose:** Stores AIS (Automatic Identification System) tracking data for real-time vessel position monitoring.

**Business Context:** Vessel tracking provides real-time vessel positions, speeds, and courses. This table stores AIS data for route deviation detection, speed analysis, and vessel monitoring.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| tracking_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the tracking record. |
| vessel_id | VARCHAR(255) | NOT NULL | Foreign key to vessels.vessel_id. Vessel being tracked. |
| sailing_id | VARCHAR(255) | NULL | Foreign key to sailings.sailing_id. Sailing associated with this tracking point. |
| mmsi | VARCHAR(9) | NULL | Maritime Mobile Service Identity. Used for AIS identification. |
| position_timestamp | TIMESTAMP_NTZ | NOT NULL | Timestamp when the position was recorded. |
| latitude | NUMERIC(10, 7) | NOT NULL | Latitude coordinate of vessel position (WGS84, EPSG:4326). |
| longitude | NUMERIC(10, 7) | NOT NULL | Longitude coordinate of vessel position (WGS84, EPSG:4326). |
| position_geom | GEOGRAPHY | NULL | Point geometry for vessel position. Spatial data type for geographic queries. |
| speed_knots | NUMERIC(6, 2) | NULL | Vessel speed over ground in knots. |
| course_degrees | NUMERIC(6, 2) | NULL | Course over ground in degrees (0-360). |
| heading_degrees | NUMERIC(6, 2) | NULL | Vessel heading in degrees (0-360). May differ from course due to drift. |
| status | VARCHAR(50) | NULL | Navigation status: 'Under way', 'At anchor', 'Moored', 'Aground', etc. |
| destination | VARCHAR(255) | NULL | Reported destination port or location. |
| eta | TIMESTAMP_NTZ | NULL | Estimated time of arrival at destination. |
| draught_meters | NUMERIC(6, 2) | NULL | Vessel draught (depth below waterline) in meters. |
| cargo_type | VARCHAR(100) | NULL | Type of cargo being carried. |
| data_source | VARCHAR(100) | NULL | Source of tracking data: 'AIS', 'USCG', 'NOAA', 'MarineCadastre', etc. Default: 'AIS'. |
| data_quality | VARCHAR(50) | NULL | Quality indicator for the tracking data: 'High', 'Medium', 'Low'. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `tracking_id`
- Index: `idx_vessel_tracking_vessel` on `vessel_id`
- Index: `idx_vessel_tracking_timestamp` on `position_timestamp`
- Index: `idx_vessel_tracking_mmsi` on `mmsi`
- Spatial Index: `position_geom` (GIST index on PostgreSQL PostGIS)

**Relationships:**
- Many-to-one with `vessels` (vessel_id)
- Many-to-one with `sailings` (sailing_id)

**Spatial Data:**
- Uses `GEOGRAPHY` type for spatial operations
- Coordinates in WGS84 (EPSG:4326) format
- Used for route deviation detection, distance calculations, and speed analysis

**Business Notes:**
- High-frequency data enables real-time vessel monitoring
- Position sequences enable route deviation detection
- Speed and course data support operational analysis

---

## port_statistics

**Purpose:** Stores aggregated port statistics and performance metrics for operational analysis.

**Business Context:** Port statistics provide aggregated performance metrics for ports over time periods. This table supports port capacity analysis, throughput monitoring, and operational efficiency evaluation.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| statistic_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the statistic record. |
| port_id | VARCHAR(255) | NOT NULL | Foreign key to ports.port_id. Port for which statistics are recorded. |
| statistic_date | DATE | NOT NULL | Date for which statistics are recorded. |
| statistic_period | VARCHAR(50) | NOT NULL | Period type: 'Daily', 'Weekly', 'Monthly', 'Yearly'. |
| total_vessel_calls | INTEGER | NULL | Total number of vessel calls during the period. |
| total_container_teu | NUMERIC(12, 2) | NULL | Total container throughput in TEU during the period. |
| containers_loaded | INTEGER | NULL | Total containers loaded during the period. |
| containers_discharged | INTEGER | NULL | Total containers discharged during the period. |
| containers_transshipped | INTEGER | NULL | Total containers transshipped during the period. |
| average_vessel_size_teu | NUMERIC(10, 2) | NULL | Average vessel size calling the port in TEU. |
| average_dwell_time_hours | NUMERIC(8, 2) | NULL | Average vessel dwell time (time in port) in hours. |
| berth_utilization_percent | NUMERIC(5, 2) | NULL | Percentage of berth capacity utilized (0-100). |
| crane_utilization_percent | NUMERIC(5, 2) | NULL | Percentage of crane capacity utilized (0-100). |
| data_source | VARCHAR(100) | NULL | Source of statistics: 'MARAD', 'Port Authority', 'Linescape', 'Calculated', etc. |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |
| updated_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was last updated. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `statistic_id`
- Unique: `(port_id, statistic_date, statistic_period)`
- Index: `idx_port_statistics_port` on `port_id`
- Index: `idx_port_statistics_date` on `statistic_date`

**Relationships:**
- Many-to-one with `ports` (port_id)

**Business Notes:**
- Aggregated data enables trend analysis and capacity planning
- Utilization metrics support infrastructure optimization
- Period type enables flexible reporting (daily, weekly, monthly, yearly)

---

## carrier_performance

**Purpose:** Stores carrier performance metrics and KPIs for evaluation periods.

**Business Context:** Carrier performance metrics provide aggregated performance indicators for carriers over evaluation periods. This table supports carrier benchmarking, performance analysis, and service quality evaluation.

| Column Name | Data Type | Nullable | Description |
|------------|-----------|----------|------------|
| performance_id | VARCHAR(255) | NOT NULL | Primary key. Unique identifier for the performance record. |
| carrier_id | VARCHAR(255) | NOT NULL | Foreign key to carriers.carrier_id. Carrier being evaluated. |
| evaluation_period_start | DATE | NOT NULL | Start date of the evaluation period. |
| evaluation_period_end | DATE | NOT NULL | End date of the evaluation period. |
| total_voyages | INTEGER | NULL | Total number of voyages during the evaluation period. |
| on_time_departures | INTEGER | NULL | Number of on-time departures (within tolerance). |
| on_time_arrivals | INTEGER | NULL | Number of on-time arrivals (within tolerance). |
| on_time_performance_percent | NUMERIC(5, 2) | NULL | Overall on-time performance percentage (0-100). |
| average_transit_time_days | NUMERIC(8, 2) | NULL | Average transit time across all voyages in days. |
| vessel_utilization_percent | NUMERIC(5, 2) | NULL | Average vessel utilization percentage (0-100). |
| capacity_utilization_percent | NUMERIC(5, 2) | NULL | Average capacity utilization percentage (0-100). |
| total_teu_carried | NUMERIC(12, 2) | NULL | Total TEU carried during the evaluation period. |
| port_calls_count | INTEGER | NULL | Total number of port calls during the evaluation period. |
| route_coverage_count | INTEGER | NULL | Number of unique routes operated during the evaluation period. |
| customer_satisfaction_score | NUMERIC(5, 2) | NULL | Customer satisfaction score (0-100). |
| created_at | TIMESTAMP_NTZ | NULL | Timestamp when the record was created. Default: CURRENT_TIMESTAMP(). |

**Indexes:**
- Primary Key: `performance_id`
- Index: `idx_carrier_performance_carrier` on `carrier_id`
- Index: `idx_carrier_performance_period` on `(evaluation_period_start, evaluation_period_end)`

**Relationships:**
- Many-to-one with `carriers` (carrier_id)

**Business Notes:**
- Performance metrics enable carrier benchmarking and competitive analysis
- Evaluation periods support periodic performance reviews
- KPIs support carrier selection and service quality monitoring

---

## Data Types Reference

### Standard Data Types

- **VARCHAR(n)**: Variable-length character string (max length n)
- **INTEGER**: 32-bit signed integer
- **NUMERIC(p, s)**: Fixed-point decimal number (p = precision, s = scale)
- **BOOLEAN**: True/false value
- **DATE**: Date value (year, month, day)
- **TIMESTAMP_NTZ**: Timestamp without timezone (compatible across PostgreSQL)

### Spatial Data Types

- **GEOGRAPHY**: Spatial data type for geographic coordinates (WGS84, EPSG:4326)
  - Used for: `ports.port_geom`, `vessels_tracking.position_geom`, `locations.location_geom`
  - Supports spatial operations: ST_DISTANCE, ST_WITHIN, ST_MAKEPOINT, ST_BEARING, etc.
  - Compatible with: PostgreSQL PostGIS

### Spatial Extent Columns

Several tables include spatial extent columns for bounding box representation:
- `spatial_extent_west`: Western boundary (longitude)
- `spatial_extent_south`: Southern boundary (latitude)
- `spatial_extent_east`: Eastern boundary (longitude)
- `spatial_extent_north`: Northern boundary (latitude)

These enable efficient spatial queries without requiring geometry calculations.

---

## Common Status Values

### Carrier Status
- `'Active'`: Carrier is actively operating
- `'Inactive'`: Carrier is temporarily inactive
- `'Suspended'`: Carrier operations are suspended

### Vessel Status
- `'Active'`: Vessel is actively operating
- `'Inactive'`: Vessel is temporarily inactive
- `'Under Repair'`: Vessel is undergoing maintenance
- `'Scrapped'`: Vessel has been scrapped

### Port Status
- `'Active'`: Port is actively operating
- `'Inactive'`: Port is temporarily inactive
- `'Under Maintenance'`: Port is undergoing maintenance

### Route Status
- `'Active'`: Route is actively operating
- `'Suspended'`: Route is temporarily suspended
- `'Discontinued'`: Route has been discontinued

### Sailing/Voyage Status
- `'Scheduled'`: Sailing/voyage is scheduled
- `'In Transit'` / `'In Progress'`: Sailing/voyage is currently in progress
- `'Completed'`: Sailing/voyage has been completed
- `'Cancelled'`: Sailing/voyage has been cancelled

### Port Call Status
- `'Scheduled'`: Port call is scheduled
- `'In Progress'`: Port call is currently in progress
- `'Completed'`: Port call has been completed
- `'Cancelled'`: Port call has been cancelled

---

## Data Sources

The database integrates data from multiple government and commercial sources:

- **MARAD**: U.S. Maritime Administration (port statistics, vessel data)
- **NOAA**: National Oceanic and Atmospheric Administration (AIS data, vessel tracking)
- **USCG**: U.S. Coast Guard (vessel information, port calls)
- **Linescape**: Commercial maritime intelligence API
- **Port Authority**: Direct port authority data
- **AIS**: Automatic Identification System (real-time vessel tracking)
- **NOAD**: Notice of Arrival/Departure (port call data)

---

## Coordinate Reference System

All spatial data uses **WGS84 (EPSG:4326)** coordinate reference system:
- Latitude: -90 to +90 degrees
- Longitude: -180 to +180 degrees
- Format: Decimal degrees (e.g., 34.0522, -118.2437 for Los Angeles)

---

## Foreign Key Relationships Summary

### Primary Relationships

1. **Carriers** → Vessels, Routes, Port Pairs, Carrier Performance
2. **Ports** → Route Ports, Port Pairs, Port Calls, Port Statistics
3. **Vessels** → Port Calls, Sailings, Voyages, Vessel Tracking
4. **Routes** → Route Ports, Port Pairs, Port Calls, Sailings, Voyages
5. **Sailings** → Port Calls
6. **Voyages** → Voyage Port Calls
7. **Port Calls** → Voyage Port Calls
8. **Locations** → Ports (and self-referential hierarchy)

---

## Indexes Summary

The database includes comprehensive indexing for performance:

- **Primary Keys**: All tables have primary key indexes
- **Foreign Keys**: Indexed for join performance
- **Frequently Queried Columns**: Timestamps, status fields, identifiers
- **Spatial Indexes**: GIST indexes on GEOGRAPHY columns (PostgreSQL PostGIS)
- **Composite Indexes**: Multi-column indexes for common query patterns

---

## Notes

- All timestamps use `TIMESTAMP_NTZ` (no timezone) for cross-database compatibility
- Spatial columns use `GEOGRAPHY` type for accurate distance calculations
- Status fields use standardized values for consistency
- Data source tracking enables data lineage and quality assessment
- Unique constraints ensure data integrity (e.g., IMO numbers, port codes)

---

**Last Updated:** 2026-02-04  
**Database Version:** 1.0  
**Schema Version:** 1.0
