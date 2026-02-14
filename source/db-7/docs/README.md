# Maritime Shipping Intelligence Database - Documentation

**Database:** db-7
**Created:** 2026-02-04

## Overview

This database contains maritime shipping intelligence data including vessel tracking, port schedules, carrier routes, sailings, and port calls. The database integrates data from government sources including NOAA, US Coast Guard, MARAD, and Data.gov.

## Database Schema

See `../data/schema.sql` for the complete database schema.

### Key Tables

- **carriers** - Shipping line/carrier information with SCAC codes
- **locations** - Regions, countries, and geographic areas
- **ports** - Port information with UN/LOCODE
- **vessels** - Vessel information with IMO numbers and MMSI
- **routes** - Shipping routes/services operated by carriers
- **route_ports** - Junction table linking routes to ports
- **port_pairs** - Origin-destination port pairs for carriers
- **port_calls** - Scheduled and actual port calls
- **sailings** - Sailing/voyage information between ports
- **voyages** - Complete voyage information
- **voyage_port_calls** - Links voyages to port calls
- **vessel_tracking** - AIS tracking data
- **port_statistics** - Aggregated port statistics
- **carrier_performance** - Carrier performance metrics

## Queries

See `../queries/queries.md` for 30 extremely complex SQL queries.

All queries are designed to work across:
- PostgreSQL
 (Delta Lake)


## Data Sources

- **NOAA** - Maritime and ocean data
- **US Coast Guard** - Vessel and port data
- **MARAD** - Maritime Administration data
- **Data.gov** - Federal open data

## Usage

1. Load schema: `psql -f data/schema.sql` (PostgreSQL)
2. Load data: `psql -f data/data.sql` (PostgreSQL)
3. Run queries: See `queries/queries.md`

---
**Last Updated:** 2026-02-04
