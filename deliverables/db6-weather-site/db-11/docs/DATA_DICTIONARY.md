# Data Dictionary - db-11 Parking Intelligence Database

**Created:** 2026-02-04

## Overview

This data dictionary provides detailed descriptions of all tables and columns in the parking intelligence database.

## Tables by Category

### Geographic and Demographic Data

#### metropolitan_areas
Metropolitan statistical areas (MSAs) with demographics and economic data.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| msa_id | VARCHAR(50) | PRIMARY KEY | Unique identifier for metropolitan statistical area |
| msa_name | VARCHAR(255) | NOT NULL | Name of the metropolitan statistical area |
| msa_type | VARCHAR(50) | NOT NULL | Type: 'MSA', 'CSA', or 'Micropolitan' |
| state_codes | VARCHAR(100) | | Comma-separated state codes within MSA |
| principal_city | VARCHAR(255) | | Principal city of the MSA |
| population_estimate | INTEGER | | Population estimate for the MSA |
| land_area_sq_miles | NUMERIC(12,2) | | Land area in square miles |
| population_density | NUMERIC(10,2) | | Population density per square mile |
| median_household_income | NUMERIC(12,2) | | Median household income in USD |
| gdp_billions | NUMERIC(12,2) | | GDP in billions USD |
| msa_geom | GEOGRAPHY | | Polygon geometry for MSA boundary |
| spatial_extent_west | NUMERIC(10,6) | | Western boundary longitude |
| spatial_extent_south | NUMERIC(10,6) | | Southern boundary latitude |
| spatial_extent_east | NUMERIC(10,6) | | Eastern boundary longitude |
| spatial_extent_north | NUMERIC(10,6) | | Northern boundary latitude |
| data_year | INTEGER | | Year of data |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

#### cities
City-level demographic and economic data.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| city_id | VARCHAR(50) | PRIMARY KEY | Unique identifier for city |
| city_name | VARCHAR(255) | NOT NULL | City name |
| state_code | VARCHAR(2) | NOT NULL | Two-letter state code |
| county_name | VARCHAR(255) | | County name |
| msa_id | VARCHAR(50) | FOREIGN KEY | Reference to metropolitan_areas |
| population | INTEGER | | City population |
| land_area_sq_miles | NUMERIC(10,2) | | Land area in square miles |
| population_density | NUMERIC(10,2) | | Population density per square mile |
| median_household_income | NUMERIC(12,2) | | Median household income in USD |
| median_age | NUMERIC(5,2) | | Median age of population |
| employment_total | INTEGER | | Total employment |
| unemployment_rate | NUMERIC(5,2) | | Unemployment rate percentage |
| city_geom | GEOGRAPHY | | Point geometry for city center |
| city_latitude | NUMERIC(10,7) | | City center latitude |
| city_longitude | NUMERIC(10,7) | | City center longitude |
| timezone | VARCHAR(50) | | Timezone |
| data_year | INTEGER | | Year of data |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

### Transportation Infrastructure

#### airports
Airport information including passenger volumes and parking capacity.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| airport_id | VARCHAR(10) | PRIMARY KEY | IATA airport code |
| airport_name | VARCHAR(255) | NOT NULL | Airport name |
| city_id | VARCHAR(50) | FOREIGN KEY | Reference to cities |
| state_code | VARCHAR(2) | | State code |
| airport_type | VARCHAR(50) | | 'Commercial', 'Cargo', or 'General Aviation' |
| latitude | NUMERIC(10,7) | NOT NULL | Airport latitude |
| longitude | NUMERIC(10,7) | NOT NULL | Airport longitude |
| airport_geom | GEOGRAPHY | | Point geometry for airport location |
| annual_passengers | INTEGER | | Annual passenger volume |
| annual_cargo_tons | INTEGER | | Annual cargo volume in tons |
| parking_spaces_total | INTEGER | | Total parking spaces at airport |
| parking_facilities_count | INTEGER | | Number of parking facilities |
| valet_available | BOOLEAN | | Valet parking available |
| long_term_parking | BOOLEAN | | Long-term parking available |
| short_term_parking | BOOLEAN | | Short-term parking available |
| data_year | INTEGER | | Year of data |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

#### stadiums_venues
Sports stadiums, concert venues, and event facilities.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| venue_id | VARCHAR(50) | PRIMARY KEY | Unique identifier for venue |
| venue_name | VARCHAR(255) | NOT NULL | Venue name |
| venue_type | VARCHAR(50) | | 'Stadium', 'Arena', 'Convention Center', 'Amphitheater' |
| city_id | VARCHAR(50) | FOREIGN KEY | Reference to cities |
| latitude | NUMERIC(10,7) | NOT NULL | Venue latitude |
| longitude | NUMERIC(10,7) | NOT NULL | Venue longitude |
| venue_geom | GEOGRAPHY | | Point geometry for venue location |
| capacity | INTEGER | | Venue capacity |
| parking_spaces_total | INTEGER | | Total parking spaces |
| parking_facilities_count | INTEGER | | Number of parking facilities |
| primary_sport | VARCHAR(100) | | Primary sport: 'NFL', 'MLB', 'NBA', 'NHL', 'Soccer', 'Concert' |
| team_name | VARCHAR(255) | | Team name |
| annual_events_count | INTEGER | | Annual number of events |
| peak_attendance | INTEGER | | Peak attendance |
| data_year | INTEGER | | Year of data |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

### Parking Facilities

#### parking_facilities
Individual parking facilities (lots, garages, structures).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| facility_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for facility |
| facility_name | VARCHAR(255) | | Facility name |
| facility_type | VARCHAR(50) | | 'Surface Lot', 'Garage', 'Structure', 'Valet', 'Street' |
| city_id | VARCHAR(50) | FOREIGN KEY | Reference to cities |
| latitude | NUMERIC(10,7) | NOT NULL | Facility latitude |
| longitude | NUMERIC(10,7) | NOT NULL | Facility longitude |
| facility_geom | GEOGRAPHY | | Point geometry for facility location |
| total_spaces | INTEGER | | Total parking spaces |
| accessible_spaces | INTEGER | | Accessible parking spaces |
| ev_charging_stations | INTEGER | | EV charging stations count |
| covered_spaces | INTEGER | | Covered parking spaces |
| uncovered_spaces | INTEGER | | Uncovered parking spaces |
| height_restriction_feet | NUMERIC(5,2) | | Height restriction in feet |
| operator_name | VARCHAR(255) | | Operator name |
| operator_type | VARCHAR(50) | | 'Public', 'Private', 'Municipal', 'Airport', 'Venue' |
| airport_id | VARCHAR(10) | FOREIGN KEY | Reference to airports (if applicable) |
| venue_id | VARCHAR(50) | FOREIGN KEY | Reference to stadiums_venues (if applicable) |
| is_event_parking | BOOLEAN | DEFAULT FALSE | Event parking available |
| is_monthly_parking | BOOLEAN | DEFAULT FALSE | Monthly parking available |
| is_hourly_parking | BOOLEAN | DEFAULT TRUE | Hourly parking available |
| accepts_reservations | BOOLEAN | DEFAULT FALSE | Accepts reservations |
| payment_methods | VARCHAR(255) | | Comma-separated: 'Cash', 'Credit', 'Mobile', 'App' |
| amenities | VARCHAR(500) | | Comma-separated amenities |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

#### parking_pricing
Pricing information for parking facilities.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| pricing_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for pricing record |
| facility_id | VARCHAR(100) | FOREIGN KEY NOT NULL | Reference to parking_facilities |
| pricing_type | VARCHAR(50) | | 'Hourly', 'Daily', 'Monthly', 'Event', 'Early Bird' |
| base_rate_hourly | NUMERIC(8,2) | | Base hourly rate in USD |
| base_rate_daily | NUMERIC(8,2) | | Base daily rate in USD |
| base_rate_monthly | NUMERIC(8,2) | | Base monthly rate in USD |
| event_rate | NUMERIC(8,2) | | Event parking rate in USD |
| max_daily_rate | NUMERIC(8,2) | | Maximum daily rate in USD |
| currency | VARCHAR(3) | DEFAULT 'USD' | Currency code |
| effective_date | DATE | | Pricing effective date |
| expiration_date | DATE | | Pricing expiration date |
| day_of_week | VARCHAR(20) | | 'Monday', 'Tuesday', etc., or 'All' |
| time_range_start | TIME | | Time range start |
| time_range_end | TIME | | Time range end |
| is_active | BOOLEAN | DEFAULT TRUE | Active pricing status |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

#### parking_utilization
Parking utilization and occupancy data.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| utilization_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for utilization record |
| facility_id | VARCHAR(100) | FOREIGN KEY NOT NULL | Reference to parking_facilities |
| utilization_date | DATE | NOT NULL | Utilization date |
| utilization_hour | INTEGER | | Hour of day (0-23) |
| occupancy_rate | NUMERIC(5,2) | | Occupancy percentage (0-100) |
| spaces_occupied | INTEGER | | Number of spaces occupied |
| spaces_available | INTEGER | | Number of spaces available |
| revenue_generated | NUMERIC(10,2) | | Revenue generated in USD |
| reservation_count | INTEGER | | Number of reservations |
| walk_in_count | INTEGER | | Number of walk-ins |
| data_source | VARCHAR(50) | | 'Sensor', 'Manual', 'App', 'Estimated' |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

### Traffic and Events

#### traffic_volume_data
Traffic volume statistics from FHWA.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| traffic_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for traffic monitoring location |
| location_id | VARCHAR(100) | | Location identifier |
| city_id | VARCHAR(50) | FOREIGN KEY | Reference to cities |
| latitude | NUMERIC(10,7) | | Monitoring location latitude |
| longitude | NUMERIC(10,7) | | Monitoring location longitude |
| location_geom | GEOGRAPHY | | Point geometry for monitoring location |
| road_name | VARCHAR(255) | | Road name |
| road_type | VARCHAR(50) | | 'Highway', 'Arterial', 'Collector', 'Local' |
| annual_average_daily_traffic | INTEGER | | Annual average daily traffic (AADT) |
| peak_hour_volume | INTEGER | | Peak hour traffic volume |
| direction | VARCHAR(20) | | 'Northbound', 'Southbound', 'Eastbound', 'Westbound', 'Both' |
| data_year | INTEGER | | Year of data |
| data_month | INTEGER | | Month of data |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

#### events
Event information (sports games, concerts, conventions).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| event_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for event |
| event_name | VARCHAR(255) | NOT NULL | Event name |
| event_type | VARCHAR(50) | | 'Sports', 'Concert', 'Convention', 'Festival', 'Conference' |
| venue_id | VARCHAR(50) | FOREIGN KEY | Reference to stadiums_venues |
| city_id | VARCHAR(50) | FOREIGN KEY | Reference to cities |
| event_date | DATE | NOT NULL | Event date |
| event_time | TIME | | Event time |
| attendance | INTEGER | | Event attendance |
| parking_demand_multiplier | NUMERIC(5,2) | | Multiplier for parking demand |
| is_recurring | BOOLEAN | DEFAULT FALSE | Recurring event flag |
| recurrence_pattern | VARCHAR(100) | | 'Weekly', 'Monthly', 'Seasonal' |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

### Business Intelligence

#### market_intelligence_metrics
Calculated marketing intelligence metrics.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| metric_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for metric |
| city_id | VARCHAR(50) | FOREIGN KEY | Reference to cities |
| msa_id | VARCHAR(50) | FOREIGN KEY | Reference to metropolitan_areas |
| metric_type | VARCHAR(50) | | 'Demand', 'Supply', 'Utilization', 'Revenue', 'Competition' |
| metric_name | VARCHAR(100) | | Metric name |
| metric_value | NUMERIC(15,2) | | Metric value |
| metric_unit | VARCHAR(50) | | Metric unit |
| calculation_date | DATE | | Calculation date |
| time_period | VARCHAR(50) | | 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Annual' |
| data_year | INTEGER | | Year of data |
| data_month | INTEGER | | Month of data |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

#### competitive_analysis
Competitive parking facility analysis.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| analysis_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for analysis |
| facility_id | VARCHAR(100) | FOREIGN KEY NOT NULL | Reference to parking_facilities |
| competitor_facility_id | VARCHAR(100) | FOREIGN KEY | Reference to parking_facilities (competitor) |
| analysis_date | DATE | | Analysis date |
| price_difference_pct | NUMERIC(5,2) | | Price difference percentage |
| distance_miles | NUMERIC(8,2) | | Distance to competitor in miles |
| utilization_difference_pct | NUMERIC(5,2) | | Utilization difference percentage |
| amenity_comparison | VARCHAR(500) | | Amenity comparison |
| competitive_score | NUMERIC(5,2) | | Competitive advantage score (0-100) |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

#### business_districts
Business district and commercial area information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| district_id | VARCHAR(50) | PRIMARY KEY | Unique identifier for district |
| district_name | VARCHAR(255) | NOT NULL | District name |
| city_id | VARCHAR(50) | FOREIGN KEY | Reference to cities |
| district_type | VARCHAR(50) | | 'Downtown', 'Financial', 'Retail', 'Entertainment', 'Airport', 'Medical' |
| latitude | NUMERIC(10,7) | | District center latitude |
| longitude | NUMERIC(10,7) | | District center longitude |
| district_geom | GEOGRAPHY | | Polygon geometry for district boundary |
| employment_total | INTEGER | | Total employment in district |
| businesses_count | INTEGER | | Number of businesses |
| parking_demand_score | NUMERIC(5,2) | | Parking demand score (0-100) |
| spatial_extent_west | NUMERIC(10,6) | | Western boundary longitude |
| spatial_extent_south | NUMERIC(10,6) | | Southern boundary latitude |
| spatial_extent_east | NUMERIC(10,6) | | Eastern boundary longitude |
| spatial_extent_north | NUMERIC(10,6) | | Northern boundary latitude |
| data_year | INTEGER | | Year of data |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

#### facility_district_mapping
Mapping between parking facilities and business districts.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| mapping_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for mapping |
| facility_id | VARCHAR(100) | FOREIGN KEY NOT NULL | Reference to parking_facilities |
| district_id | VARCHAR(50) | FOREIGN KEY NOT NULL | Reference to business_districts |
| distance_miles | NUMERIC(8,2) | | Distance from facility to district in miles |
| is_primary_district | BOOLEAN | DEFAULT FALSE | Primary district flag |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

### Metadata

#### data_source_metadata
Data source tracking and extraction metadata.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|------------|-------------|
| source_id | VARCHAR(100) | PRIMARY KEY | Unique identifier for data source |
| source_name | VARCHAR(255) | NOT NULL | Source name |
| source_type | VARCHAR(50) | | 'API', 'CSV', 'Shapefile', 'Database', 'Web Scrape' |
| source_url | VARCHAR(1000) | | Source URL |
| api_endpoint | VARCHAR(500) | | API endpoint (if applicable) |
| extraction_date | DATE | | Extraction date |
| extraction_timestamp | TIMESTAMP_NTZ | | Extraction timestamp |
| records_extracted | INTEGER | | Number of records extracted |
| data_quality_score | NUMERIC(5,2) | | Data quality score (0-100) |
| completeness_pct | NUMERIC(5,2) | | Completeness percentage |
| error_count | INTEGER | | Error count |
| load_timestamp | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Data load timestamp |

## Foreign Key Relationships

- `cities.msa_id` → `metropolitan_areas.msa_id`
- `airports.city_id` → `cities.city_id`
- `stadiums_venues.city_id` → `cities.city_id`
- `parking_facilities.city_id` → `cities.city_id`
- `parking_facilities.airport_id` → `airports.airport_id`
- `parking_facilities.venue_id` → `stadiums_venues.venue_id`
- `parking_pricing.facility_id` → `parking_facilities.facility_id`
- `parking_utilization.facility_id` → `parking_facilities.facility_id`
- `traffic_volume_data.city_id` → `cities.city_id`
- `events.venue_id` → `stadiums_venues.venue_id`
- `events.city_id` → `cities.city_id`
- `market_intelligence_metrics.city_id` → `cities.city_id`
- `market_intelligence_metrics.msa_id` → `metropolitan_areas.msa_id`
- `competitive_analysis.facility_id` → `parking_facilities.facility_id`
- `competitive_analysis.competitor_facility_id` → `parking_facilities.facility_id`
- `business_districts.city_id` → `cities.city_id`
- `facility_district_mapping.facility_id` → `parking_facilities.facility_id`
- `facility_district_mapping.district_id` → `business_districts.district_id`

---
**Last Updated:** 2026-02-04
