# Research Directory - DB-7 Maritime Shipping Intelligence

**Purpose:** This directory contains research notebooks, analysis scripts, and experimental work related to maritime shipping intelligence database db-7.

## Contents

- **etl_elt_pipeline.ipynb**: Comprehensive ETL/ELT pipeline notebook for maritime data extraction, transformation, and loading operations
- **data_resources.json**: Documentation of all government maritime data sources, APIs, and resources
- **source_metadata.json**: Comprehensive source metadata tracking and data lineage

## Government Data Sources

### NOAA (National Oceanic and Atmospheric Administration)
- **AccessAIS Tool**: Interactive vessel traffic data download
- **MarineCadastre.gov**: AIS vessel traffic data (2009-2024)
- **Vessel Traffic Data**: CSV, GeoPackages, GeoTIFFs formats

### US Coast Guard (USCG)
- **National Vessel Movement Center (NVMC)**: Notice of Arrival and Departure (NOAD) data
- **Vessel Information Verification Service (VIVS)**: AIS static data (MMSI, call sign, vessel info)
- **AIS Data Sharing**: Level A (real-time), Level B (filtered), Level C (historical)

### MARAD (Maritime Administration)
- **U.S.-Flag Fleet Data**: Current fleet lists, vessel characteristics, capacities
- **Port Statistics**: Cargo volumes, vessel calls, berth productivity
- **Waterborne Commerce Statistics**: Port performance metrics

### Data.gov
- **Virginia International Gateway Vessel Schedules**: Port of Virginia vessel schedules
- **Port Region Grain Ocean Vessel Activity**: USDA weekly vessel activity data
- **AIS Vessel Tracks**: Commerce Data Hub AIS datasets

## Usage

The ETL/ELT pipeline notebook provides:
1. **Extract**: Load data from government sources (NOAA, USCG, MARAD, Data.gov)
2. **Transform**: Clean, validate, and transform maritime data
3. **Load**: Load transformed data into target databases (PostgreSQL)
4. **Validate**: Verify data quality and completeness
5. **Monitor**: Track pipeline performance and errors

## Notes

- Notebooks in this directory are for research and development purposes
- Results and outputs may be experimental
- See `../metadata/` for pipeline execution metadata
- All government data sources are documented in `data_resources.json`
- Source metadata tracking is maintained in `source_metadata.json`

---
**Last Updated:** 2026-02-04
