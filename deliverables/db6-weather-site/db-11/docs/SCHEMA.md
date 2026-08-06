# Database Schema Documentation - db-11

**Created:** 2026-02-04

## Schema Overview

The parking intelligence database consists of 14 main tables designed to store and analyze parking facility data, demographics, traffic patterns, airport statistics, venue information, and market intelligence metrics from government sources.

## ER Diagram

```mermaid
erDiagram
    metropolitan_areas {
        varchar msa_id PK "Primary key"
        varchar msa_name "MSA name"
        varchar msa_type "MSA type"
        integer population_estimate "Population estimate"
        numeric median_household_income "Median household income"
        geography msa_geom SPATIAL "MSA boundary geometry"
    }
    
    cities {
        varchar city_id PK "Primary key"
        varchar city_name "City name"
        varchar state_code "State code"
        varchar msa_id FK "Metropolitan area"
        integer population "Population"
        numeric population_density "Population density"
        numeric median_household_income "Median household income"
        geography city_geom SPATIAL "City center point"
    }
    
    airports {
        varchar airport_id PK "Primary key (IATA code)"
        varchar airport_name "Airport name"
        varchar city_id FK "City"
        integer annual_passengers "Annual passenger volume"
        integer parking_spaces_total "Total parking spaces"
        geography airport_geom SPATIAL "Airport location point"
    }
    
    stadiums_venues {
        varchar venue_id PK "Primary key"
        varchar venue_name "Venue name"
        varchar venue_type "Venue type"
        varchar city_id FK "City"
        integer capacity "Venue capacity"
        integer parking_spaces_total "Total parking spaces"
        geography venue_geom SPATIAL "Venue location point"
    }
    
    parking_facilities {
        varchar facility_id PK "Primary key"
        varchar facility_name "Facility name"
        varchar facility_type "Facility type"
        varchar city_id FK "City"
        integer total_spaces "Total parking spaces"
        varchar airport_id FK "Airport (if applicable)"
        varchar venue_id FK "Venue (if applicable)"
        geography facility_geom SPATIAL "Facility location point"
    }
    
    parking_pricing {
        varchar pricing_id PK "Primary key"
        varchar facility_id FK "Parking facility"
        varchar pricing_type "Pricing type"
        numeric base_rate_hourly "Hourly rate"
        numeric base_rate_daily "Daily rate"
        boolean is_active "Active status"
    }
    
    parking_utilization {
        varchar utilization_id PK "Primary key"
        varchar facility_id FK "Parking facility"
        date utilization_date "Utilization date"
        integer utilization_hour "Hour (0-23)"
        numeric occupancy_rate "Occupancy percentage"
        numeric revenue_generated "Revenue generated"
    }
    
    traffic_volume_data {
        varchar traffic_id PK "Primary key"
        varchar city_id FK "City"
        integer annual_average_daily_traffic "AADT"
        integer peak_hour_volume "Peak hour volume"
        geography location_geom SPATIAL "Traffic monitoring location"
    }
    
    events {
        varchar event_id PK "Primary key"
        varchar event_name "Event name"
        varchar venue_id FK "Venue"
        varchar city_id FK "City"
        date event_date "Event date"
        integer attendance "Attendance"
        numeric parking_demand_multiplier "Demand multiplier"
    }
    
    market_intelligence_metrics {
        varchar metric_id PK "Primary key"
        varchar city_id FK "City"
        varchar msa_id FK "MSA"
        varchar metric_type "Metric type"
        numeric metric_value "Metric value"
        date calculation_date "Calculation date"
    }
    
    competitive_analysis {
        varchar analysis_id PK "Primary key"
        varchar facility_id FK "Facility"
        varchar competitor_facility_id FK "Competitor facility"
        numeric price_difference_pct "Price difference percentage"
        numeric competitive_score "Competitive score"
    }
    
    business_districts {
        varchar district_id PK "Primary key"
        varchar district_name "District name"
        varchar city_id FK "City"
        varchar district_type "District type"
        integer employment_total "Total employment"
        geography district_geom SPATIAL "District boundary"
    }
    
    facility_district_mapping {
        varchar mapping_id PK "Primary key"
        varchar facility_id FK "Facility"
        varchar district_id FK "Business district"
        numeric distance_miles "Distance in miles"
    }
    
    data_source_metadata {
        varchar source_id PK "Primary key"
        varchar source_name "Source name"
        varchar source_type "Source type"
        date extraction_date "Extraction date"
        integer records_extracted "Records extracted"
    }

    metropolitan_areas ||--o{ cities : "contains"
    cities ||--o{ airports : "has"
    cities ||--o{ stadiums_venues : "has"
    cities ||--o{ parking_facilities : "has"
    cities ||--o{ traffic_volume_data : "has"
    cities ||--o{ business_districts : "has"
    airports ||--o{ parking_facilities : "serves"
    stadiums_venues ||--o{ parking_facilities : "serves"
    stadiums_venues ||--o{ events : "hosts"
    parking_facilities ||--o{ parking_pricing : "has"
    parking_facilities ||--o{ parking_utilization : "tracks"
    parking_facilities ||--o{ competitive_analysis : "analyzes"
    parking_facilities ||--o{ facility_district_mapping : "maps_to"
    business_districts ||--o{ facility_district_mapping : "contains"
    cities ||--o{ events : "hosts"
    cities ||--o{ market_intelligence_metrics : "measures"
    metropolitan_areas ||--o{ market_intelligence_metrics : "measures"
```

## Tables

### metropolitan_areas
Stores metropolitan statistical areas (MSAs) with demographics and economic data.

**Key Columns:**
- `msa_id` (VARCHAR, PK) - Metropolitan statistical area identifier
- `msa_name` (VARCHAR) - MSA name
- `msa_type` (VARCHAR) - 'MSA', 'CSA', 'Micropolitan'
- `population_estimate` (INTEGER) - Population estimate
- `median_household_income` (NUMERIC) - Median household income
- `msa_geom` (GEOGRAPHY) - MSA boundary polygon geometry

### cities
Stores city-level demographic and economic data.

**Key Columns:**
- `city_id` (VARCHAR, PK) - City identifier
- `city_name` (VARCHAR) - City name
- `state_code` (VARCHAR) - State code (2-letter)
- `msa_id` (VARCHAR, FK) - Metropolitan area reference
- `population` (INTEGER) - City population
- `population_density` (NUMERIC) - Population density per square mile
- `median_household_income` (NUMERIC) - Median household income
- `city_geom` (GEOGRAPHY) - City center point geometry

### airports
Stores airport information including passenger volumes and parking capacity.

**Key Columns:**
- `airport_id` (VARCHAR, PK) - Airport IATA code
- `airport_name` (VARCHAR) - Airport name
- `city_id` (VARCHAR, FK) - City reference
- `annual_passengers` (INTEGER) - Annual passenger volume
- `parking_spaces_total` (INTEGER) - Total parking spaces
- `airport_geom` (GEOGRAPHY) - Airport location point

### stadiums_venues
Stores sports stadiums, concert venues, and event facilities.

**Key Columns:**
- `venue_id` (VARCHAR, PK) - Venue identifier
- `venue_name` (VARCHAR) - Venue name
- `venue_type` (VARCHAR) - 'Stadium', 'Arena', 'Convention Center'
- `city_id` (VARCHAR, FK) - City reference
- `capacity` (INTEGER) - Venue capacity
- `parking_spaces_total` (INTEGER) - Total parking spaces
- `venue_geom` (GEOGRAPHY) - Venue location point

### parking_facilities
Stores individual parking facilities (lots, garages, structures).

**Key Columns:**
- `facility_id` (VARCHAR, PK) - Facility identifier
- `facility_name` (VARCHAR) - Facility name
- `facility_type` (VARCHAR) - 'Surface Lot', 'Garage', 'Structure'
- `city_id` (VARCHAR, FK) - City reference
- `total_spaces` (INTEGER) - Total parking spaces
- `airport_id` (VARCHAR, FK) - Airport reference (if applicable)
- `venue_id` (VARCHAR, FK) - Venue reference (if applicable)
- `facility_geom` (GEOGRAPHY) - Facility location point

### parking_pricing
Stores pricing information for parking facilities.

**Key Columns:**
- `pricing_id` (VARCHAR, PK) - Pricing identifier
- `facility_id` (VARCHAR, FK) - Facility reference
- `pricing_type` (VARCHAR) - 'Hourly', 'Daily', 'Monthly', 'Event'
- `base_rate_hourly` (NUMERIC) - Base hourly rate
- `base_rate_daily` (NUMERIC) - Base daily rate
- `is_active` (BOOLEAN) - Active pricing status

### parking_utilization
Stores parking utilization and occupancy data.

**Key Columns:**
- `utilization_id` (VARCHAR, PK) - Utilization record identifier
- `facility_id` (VARCHAR, FK) - Facility reference
- `utilization_date` (DATE) - Utilization date
- `utilization_hour` (INTEGER) - Hour of day (0-23)
- `occupancy_rate` (NUMERIC) - Occupancy percentage (0-100)
- `revenue_generated` (NUMERIC) - Revenue generated

### traffic_volume_data
Stores traffic volume statistics from FHWA.

**Key Columns:**
- `traffic_id` (VARCHAR, PK) - Traffic monitoring location identifier
- `city_id` (VARCHAR, FK) - City reference
- `annual_average_daily_traffic` (INTEGER) - AADT
- `peak_hour_volume` (INTEGER) - Peak hour traffic volume
- `location_geom` (GEOGRAPHY) - Traffic monitoring location point

### events
Stores event information (sports games, concerts, conventions).

**Key Columns:**
- `event_id` (VARCHAR, PK) - Event identifier
- `event_name` (VARCHAR) - Event name
- `venue_id` (VARCHAR, FK) - Venue reference
- `city_id` (VARCHAR, FK) - City reference
- `event_date` (DATE) - Event date
- `attendance` (INTEGER) - Event attendance
- `parking_demand_multiplier` (NUMERIC) - Parking demand multiplier

### market_intelligence_metrics
Stores calculated marketing intelligence metrics.

**Key Columns:**
- `metric_id` (VARCHAR, PK) - Metric identifier
- `city_id` (VARCHAR, FK) - City reference
- `msa_id` (VARCHAR, FK) - MSA reference
- `metric_type` (VARCHAR) - 'Demand', 'Supply', 'Utilization', 'Revenue'
- `metric_value` (NUMERIC) - Metric value
- `calculation_date` (DATE) - Calculation date

### competitive_analysis
Stores competitive parking facility analysis.

**Key Columns:**
- `analysis_id` (VARCHAR, PK) - Analysis identifier
- `facility_id` (VARCHAR, FK) - Facility reference
- `competitor_facility_id` (VARCHAR, FK) - Competitor facility reference
- `price_difference_pct` (NUMERIC) - Price difference percentage
- `competitive_score` (NUMERIC) - Competitive advantage score

### business_districts
Stores business district and commercial area information.

**Key Columns:**
- `district_id` (VARCHAR, PK) - District identifier
- `district_name` (VARCHAR) - District name
- `city_id` (VARCHAR, FK) - City reference
- `district_type` (VARCHAR) - 'Downtown', 'Financial', 'Retail', 'Entertainment'
- `employment_total` (INTEGER) - Total employment
- `district_geom` (GEOGRAPHY) - District boundary polygon

### facility_district_mapping
Stores mapping between parking facilities and business districts.

**Key Columns:**
- `mapping_id` (VARCHAR, PK) - Mapping identifier
- `facility_id` (VARCHAR, FK) - Facility reference
- `district_id` (VARCHAR, FK) - District reference
- `distance_miles` (NUMERIC) - Distance in miles

### data_source_metadata
Stores data source tracking and extraction metadata.

**Key Columns:**
- `source_id` (VARCHAR, PK) - Source identifier
- `source_name` (VARCHAR) - Source name
- `source_type` (VARCHAR) - 'API', 'CSV', 'Shapefile', 'Database'
- `extraction_date` (DATE) - Extraction date
- `records_extracted` (INTEGER) - Number of records extracted

## Spatial Data Types

The database uses GEOGRAPHY type for spatial data:
- **PostgreSQL**: PostGIS GEOGRAPHY type
- **Databricks**: GEOMETRY type (compatible)
- **Databricks**: GEOGRAPHY type

## Indexes

Spatial indexes are created on geometry columns using GIST indexes for optimal spatial query performance.

---
**Last Updated:** 2026-02-04
