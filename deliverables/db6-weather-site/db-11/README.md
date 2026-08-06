# Parking Intelligence Database - db-11

**Deliverable:** db-11
**Status:** 🚧 In Progress
**Created:** 2026-02-04

## Overview

This database contains parking intelligence data for marketing analysis, mirroring SpotHero's business model. The database aggregates parking facility data, demographics, traffic patterns, airport statistics, venue information, and market intelligence metrics from government sources to support parking marketplace operations across 400+ cities in North America.

**Target Data Size:** 1 GB of comprehensive parking intelligence data

## Structure

```
db-11/
├── queries/
│   ├── queries.md          # 30+ extremely complex SQL queries
│   └── queries.json        # Query metadata (REQUIRED - extracted from queries.md)
├── results/
│   └── *.json              # Test results and validation reports
├── docs/
│   ├── README.md          # Database documentation
│   ├── SCHEMA.md          # Schema documentation
│   └── DATA_DICTIONARY.md # Data dictionary
├── data/
│   ├── schema.sql         # Database schema SQL file
│   └── data.sql           # Sample data SQL file
├── scripts/
│   ├── extract_queries_to_json.py # Phase 0: Query extraction
│   ├── verify_fixes.py    # Phase 1: Fix verification
│   ├── comprehensive_validator.py # Phase 2 & 4: Syntax validation and evaluation
│   ├── execution_tester.py # Phase 3: Execution testing
│   ├── generate_final_report.py # Phase 5: Final report generation
│   └── requirements.txt    # Python dependencies
├── research/
│   ├── etl_elt_pipeline.ipynb # ETL/ELT pipeline notebook
│   ├── data_resources.json # Data source documentation
│   ├── source_metadata.json # Source metadata tracking
│   └── README.md           # Research directory documentation
├── metadata/
│   ├── pipeline_metadata.json # Pipeline execution logs
│   ├── data_quality_reports.json # Data quality metrics
│   └── schema_metadata.json # Schema evolution tracking
└── deliverable/
    └── db-11.md           # Complete documentation
```

## Contents

- **Queries:** 30 extremely complex SQL queries in `queries/queries.md` for marketing intelligence analysis
- **Results:** JSON test results in `results/`
- **Documentation:** Database documentation in `docs/`
- **Data:** Schema and data files in `data/`
- **Research:** ETL/ELT pipelines and data source documentation in `research/`

## Database Schema

### Core Tables

- **metropolitan_areas** - Metropolitan statistical areas (MSAs) with demographics and economic data
- **cities** - City-level demographic and economic data
- **airports** - Airport information including passenger volumes and parking capacity
- **stadiums_venues** - Sports stadiums, concert venues, and event facilities
- **parking_facilities** - Individual parking facilities (lots, garages, structures)
- **parking_pricing** - Pricing information for parking facilities
- **traffic_volume_data** - Traffic volume statistics from FHWA
- **events** - Event information (sports games, concerts, conventions)
- **market_intelligence_metrics** - Calculated marketing intelligence metrics
- **parking_utilization** - Parking utilization and occupancy data
- **competitive_analysis** - Competitive parking facility analysis
- **business_districts** - Business district and commercial area information
- **facility_district_mapping** - Mapping between parking facilities and business districts
- **data_source_metadata** - Data source tracking and extraction metadata

## Data Sources

### Government Sources

1. **Data.gov CKAN API** - Parking facility datasets from various cities
2. **Census Bureau API** - Demographics and population data for metropolitan areas
3. **BTS TranStats** - Airport passenger volumes and statistics
4. **FAA Airport Data** - Passenger boarding and cargo statistics
5. **FHWA Traffic Data** - Traffic volume trends and highway statistics
6. **City Open Data Portals** - Real-time parking utilization and pricing data

### Geographic Coverage

- **400+ cities** across USA and Canada
- **Major metropolitan areas** (MSAs)
- **Top 50 airports** by passenger volume
- **Major sports stadiums** and venues
- **Business districts** and downtown areas

## Usage

### Marketing Intelligence Queries

See `queries/queries.md` for SQL queries covering:
- Parking facility analysis and optimization
- Market demand and supply analysis
- Competitive intelligence and pricing strategies
- Utilization patterns and revenue optimization
- Event-based parking demand forecasting
- Geographic market expansion analysis
- Demographic targeting and segmentation
- Traffic pattern correlation with parking demand

### ETL Pipeline

See `research/etl_elt_pipeline.ipynb` for:
- Data extraction from government sources
- Data transformation and cleaning
- Data loading into PostgreSQL
- Data quality validation
- Pipeline execution monitoring

## Compatibility

All queries are designed to work across:
- PostgreSQL (with PostGIS for spatial data)
 (Delta Lake)


## Data Collection Strategy

- **Target Data Size:** 1 GB
- **Update Frequency:** Weekly to monthly depending on source
- **Incremental Load:** Date-based filtering and timestamp tracking
- **Data Retention:** Historical data kept for trend analysis

---
**Last Updated:** 2026-02-04
