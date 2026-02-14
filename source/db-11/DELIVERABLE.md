# Database Deliverable: db-11 - Parking Intelligence Database

**Database:** db-11
**Type:** Parking Intelligence Database
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

This database implements a comprehensive parking intelligence system for marketing analysis, mirroring SpotHero's business model. The database aggregates parking facility data, demographics, traffic patterns, airport statistics, venue information, and market intelligence metrics from government sources to support parking marketplace operations across 400+ cities in North America.

### Key Features

- **Parking Facility Intelligence**: Comprehensive database of parking facilities (lots, garages, structures) with pricing, utilization, and capacity data
- **Market Intelligence**: Calculated metrics for market demand, supply analysis, competitive positioning, and revenue optimization
- **Geographic Coverage**: 400+ cities across USA and Canada with metropolitan area and city-level demographics
- **Event-Based Analysis**: Stadium and venue data with event scheduling and parking demand forecasting
- **Traffic Correlation**: Traffic volume data from FHWA correlated with parking demand patterns
- **Airport Integration**: Top 50 airports by passenger volume with parking capacity and utilization
- **Data Integration**: ETL/ELT pipelines pulling 1+ GB of data from public APIs (Data.gov, Census Bureau, BTS, FAA, FHWA, City Open Data Portals)

### Database Platforms Supported

- **PostgreSQL**: Full support with PostGIS for spatial data (GEOGRAPHY type)
- **Databricks**: Compatible with Delta Lake format and distributed query execution
- **Databricks**: Full support with GEOGRAPHY types and spatial functions

### Business Context

This database powers a parking intelligence platform sourced from businesses with at least $1M ARR per year. The queries demonstrate production-grade patterns used by:
- **SpotHero**: Parking marketplace with dynamic pricing and demand forecasting
- **ParkWhiz**: Parking reservation platform with market intelligence
- **Parkopedia**: Global parking database with utilization analytics
- **BestParking**: Parking search and comparison platform

---

## Database Schema Documentation

### Schema Overview

The Parking Intelligence Database consists of **14 main tables** designed to store parking facility data, demographics, traffic patterns, airport statistics, venue information, and market intelligence metrics from government sources.

### Table Groups

1. **Geographic Data**: `metropolitan_areas`, `cities`, `business_districts`
2. **Transportation**: `airports`, `traffic_volume_data`
3. **Venues**: `stadiums_venues`, `events`
4. **Parking Facilities**: `parking_facilities`, `parking_pricing`, `parking_utilization`
5. **Market Intelligence**: `market_intelligence_metrics`, `competitive_analysis`
6. **Data Management**: `facility_district_mapping`, `data_source_metadata`

### Entity-Relationship Diagram

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
        varchar metric_type "Metric type"
        numeric metric_value "Metric value"
        date metric_date "Metric date"
    }
    
    competitive_analysis {
        varchar analysis_id PK "Primary key"
        varchar facility_id FK "Parking facility"
        varchar competitor_facility_id FK "Competitor facility"
        numeric price_difference "Price difference"
        numeric utilization_difference "Utilization difference"
    }
    
    business_districts {
        varchar district_id PK "Primary key"
        varchar district_name "District name"
        varchar city_id FK "City"
        varchar district_type "District type"
        geography district_geom SPATIAL "District boundary"
    }
    
    facility_district_mapping {
        varchar facility_id PK,FK "Parking facility"
        varchar district_id PK,FK "Business district"
    }
    
    data_source_metadata {
        varchar source_id PK "Primary key"
        varchar source_name "Source name"
        varchar source_type "Source type"
        timestamp last_extracted "Last extraction time"
        integer records_extracted "Records extracted"
    }

    metropolitan_areas ||--o{ cities : "contains"
    cities ||--o{ airports : "has"
    cities ||--o{ stadiums_venues : "has"
    cities ||--o{ parking_facilities : "has"
    cities ||--o{ business_districts : "has"
    cities ||--o{ traffic_volume_data : "has"
    cities ||--o{ market_intelligence_metrics : "has"
    airports ||--o{ parking_facilities : "serves"
    stadiums_venues ||--o{ parking_facilities : "serves"
    stadiums_venues ||--o{ events : "hosts"
    parking_facilities ||--o{ parking_pricing : "has"
    parking_facilities ||--o{ parking_utilization : "tracks"
    parking_facilities ||--o{ competitive_analysis : "analyzes"
    parking_facilities ||--o{ facility_district_mapping : "maps_to"
    business_districts ||--o{ facility_district_mapping : "contains"
```

### Data Sources

#### Government Sources

1. **Data.gov CKAN API** - Parking facility datasets from various cities
2. **Census Bureau API** - Demographics and population data for metropolitan areas
3. **BTS TranStats** - Airport passenger volumes and statistics
4. **FAA Airport Data** - Passenger boarding and cargo statistics
5. **FHWA Traffic Data** - Traffic volume trends and highway statistics
6. **City Open Data Portals** - Real-time parking utilization and pricing data

#### Geographic Coverage

- **400+ cities** across USA and Canada
- **Major metropolitan areas** (MSAs)
- **Top 50 airports** by passenger volume
- **Major sports stadiums** and venues
- **Business districts** and downtown areas

---

## SQL Queries

The database includes 30 extremely complex SQL queries covering:

- Parking facility analysis and optimization
- Market demand and supply analysis
- Competitive intelligence and pricing strategies
- Utilization patterns and revenue optimization
- Event-based parking demand forecasting
- Geographic market expansion analysis
- Demographic targeting and segmentation
- Traffic pattern correlation with parking demand

All queries are designed to work across PostgreSQL (with PostGIS) (Delta Lake).

See `queries/queries.md` for complete query documentation with business context.

---

## Usage Instructions

### Database Setup

1. **Create Database Schema**:
   ```bash
   psql -U postgres -d db_11 -f data/schema.sql
   ```

2. **Load Sample Data** (optional):
   ```bash
   psql -U postgres -d db_11 -f data/data.sql
   ```

### Data Extraction

Run the ETL pipeline to extract data from government sources:

```bash
cd db-11
python3 scripts/extract_and_transform_data.py
python3 scripts/transform_and_load_data.py
```

### Query Execution

Execute queries from `queries/queries.md` using your preferred database client or application.

### Validation

Run the validation suite to verify queries:

```bash
cd db-11
python3 scripts/extract_queries_to_json.py  # Phase 0
python3 scripts/verify_fixes.py              # Phase 1
python3 scripts/comprehensive_validator.py   # Phase 2 & 4
python3 scripts/execution_tester.py          # Phase 3
python3 scripts/generate_final_report.py     # Phase 5
```

---

**Last Updated:** 2026-02-04
