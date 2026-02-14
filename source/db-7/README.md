# Maritime Shipping Intelligence Database - db-7

**Deliverable:** db-7
**Status:** 🚧 In Progress
**Created:** 2026-02-04

## Overview

This database provides comprehensive maritime shipping intelligence including vessel tracking, port schedules, carrier routes, sailings, and port calls. The database integrates data from multiple government sources including NOAA, US Coast Guard, MARAD, and Data.gov to provide a complete maritime intelligence platform matching Linescape API functionality.

## Structure

```
db-7/
├── queries/
│   ├── queries.md          # 30+ extremely complex SQL queries
│   └── queries.json       # Query metadata (REQUIRED - extracted from queries.md)
├── results/
│   └── *.json             # Test results and validation reports (JSON only)
├── docs/
│   ├── README.md          # Database documentation
│   ├── SCHEMA.md          # Schema documentation
│   └── DATA_DICTIONARY.md # Data dictionary
├── data/
│   ├── schema.sql         # Database schema
│   └── data.sql           # Sample data
├── scripts/
│   └── *.py, *.sh         # Utility scripts
├── research/
│   ├── etl_elt_pipeline.ipynb  # ETL/ELT pipeline notebook
│   ├── data_resources.json     # Government data source documentation
│   └── README.md               # Research directory documentation
└── metadata/
    └── README.md          # Metadata directory documentation
```

## Contents

- **Queries:** 30 extremely complex SQL queries in `queries/queries.md`
- **Results:** JSON test results in `results/`
- **Documentation:** Database documentation in `docs/`
- **Data:** Schema and data files in `data/`

## Database Schema

The database includes the following main tables:

### Core Tables
- **carriers** - Shipping line/carrier information with SCAC codes
- **locations** - Regions, countries, and geographic areas
- **ports** - Port information with UN/LOCODE, coordinates, and characteristics
- **vessels** - Vessel information with IMO numbers, MMSI, and specifications

### Route and Service Tables
- **routes** - Shipping routes/services operated by carriers
- **route_ports** - Junction table linking routes to ports
- **port_pairs** - Origin-destination port pairs for carriers

### Operational Tables
- **port_calls** - Scheduled and actual port calls with vessel and port information
- **sailings** - Sailing/voyage information between ports
- **voyages** - Complete voyage information from start port to end port
- **voyage_port_calls** - Links voyages to port calls

### Tracking and Analytics Tables
- **vessel_tracking** - AIS (Automatic Identification System) tracking data
- **port_statistics** - Aggregated port statistics and performance metrics
- **carrier_performance** - Carrier performance metrics and KPIs

## Key Features

- **Vessel Tracking**: AIS-based vessel position tracking with speed, course, and navigation status
- **Port Intelligence**: Comprehensive port information with UN/LOCODE, coordinates, and capacity metrics
- **Route Management**: Shipping routes and services with port sequences and transit times
- **Port Call Tracking**: Scheduled and actual port calls with cargo handling information
- **Sailing Intelligence**: Voyage tracking between ports with transit times and capacity utilization
- **Carrier Analytics**: Carrier performance metrics including on-time performance and vessel utilization
- **Port Statistics**: Aggregated port performance metrics including vessel calls and container throughput
- **Government Data Integration**: Integration with NOAA, USCG, MARAD, and Data.gov maritime datasets

## Government Data Sources

### NOAA (National Oceanic and Atmospheric Administration)
- AccessAIS Tool for vessel traffic data
- MarineCadastre.gov AIS data (2009-2024)
- Vessel traffic datasets in CSV, GeoPackage, GeoTIFF formats

### US Coast Guard (USCG)
- National Vessel Movement Center (NVMC) - NOAD data
- Vessel Information Verification Service (VIVS) - AIS static data
- AIS data sharing (Level A/B/C)

### MARAD (Maritime Administration)
- U.S.-Flag Fleet data and vessel characteristics
- Port statistics and cargo volumes
- Waterborne commerce statistics

### Data.gov
- Virginia International Gateway vessel schedules
- Port region grain ocean vessel activity
- AIS vessel tracks datasets

## Usage

See `queries/queries.md` for SQL queries covering:
- Vessel tracking and position analysis
- Port call scheduling and performance
- Route optimization and transit time analysis
- Carrier performance metrics
- Port statistics and throughput analysis
- Sailing and voyage intelligence
- Multi-port route analysis
- Geographic and spatial queries

See `results/` for test results.
See `docs/SCHEMA.md` for detailed schema documentation.
See `research/` for ETL pipeline and government data integration.

## Compatibility

All queries are designed to work across:
- PostgreSQL (with PostGIS for spatial operations)
 (Delta Lake)


## Related Resources

- **Linescape API**: https://www.linescape.com/api-overview/
- **NOAA Digital Coast**: https://coast.noaa.gov/digitalcoast/
- **USCG NVMC**: https://www.nvmc.uscg.gov/
- **MARAD Data**: https://www.maritime.dot.gov/data-reports
- **Data.gov Maritime**: https://catalog.data.gov/dataset?tags=maritime

---
**Last Updated:** 2026-02-04
