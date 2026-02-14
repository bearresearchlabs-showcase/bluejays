# Marketing Intelligence Database - db-10

**Deliverable:** db-10
**Status:** 🚧 In Progress
**Created:** 2026-02-04

## Overview

Marketing Intelligence Database (db-10) mirrors Brickseek.com functionality for retail inventory tracking, pricing intelligence, and deal discovery. The database integrates data from U.S. government sources (Census Bureau, BLS, FTC) and other reputable sources, targeting approximately 2GB of balanced data coverage.

## Database Schema

The database consists of 12 main tables:
- **products**: Product catalog with SKUs, UPCs, categories, brands
- **retailers**: Retailer information and market coverage
- **stores**: Store locations with geographic data (spatial)
- **product_inventory**: Inventory levels by store
- **product_pricing**: Pricing data with historical tracking
- **market_intelligence**: Aggregated market data for competitive analysis
- **deal_alerts**: Deal tracking and alert generation
- **census_retail_data**: U.S. Census Bureau MRTS data
- **bls_price_data**: BLS CPI/PPI price index data
- **geographic_markets**: Market area definitions with demographics
- **data_sources**: Source tracking for data lineage
- **pipeline_metadata**: ETL pipeline execution tracking

## Structure

```
db-10/
├── queries/
│   ├── queries.md          # 30 extremely complex SQL queries
│   └── queries.json        # Query metadata (extracted)
├── results/
│   └── *.json              # Test results and validation reports
├── docs/
│   ├── README.md           # Documentation overview
│   ├── SCHEMA.md           # Schema documentation with ER diagrams
│   └── DATA_DICTIONARY.md  # Complete data dictionary
├── data/
│   ├── schema.sql          # Database schema (12+ tables)
│   └── data.sql            # Sample data
├── scripts/
│   ├── extract_queries_to_json.py  # Phase 0: Query extraction
│   ├── verify_fixes.py             # Phase 1: Fix verification
│   ├── comprehensive_validator.py  # Phase 2 & 4: Syntax validation
│   ├── execution_tester.py         # Phase 3: Execution testing
│   └── generate_final_report.py    # Phase 5: Report generation
├── research/
│   ├── etl_elt_pipeline.ipynb      # ETL pipeline with API integrations
│   ├── data_resources.json         # Data source documentation
│   └── source_metadata.json        # Source metadata tracking
├── metadata/
│   └── README.md           # Metadata directory documentation
└── README.md               # This file
```

## Contents

- **Queries:** 30 extremely complex SQL queries covering:
  - Pricing intelligence and comparisons
  - Inventory analysis and availability prediction
  - Market analytics and competitive positioning
  - Geographic intelligence and market penetration
  - Deal detection and alert generation
  - Product category trend analysis
  - Store performance ranking
  - Market share analysis

- **Data Sources:** Integration with:
  - U.S. Census Bureau APIs (MRTS, Advance Retail Inventories)
  - BLS Public Data API (CPI, PPI, employment statistics)
  - Federal Trade Commission (FTC) data
  - Data.gov CKAN API (retail datasets)

- **Results:** JSON test results and validation reports
- **Documentation:** Complete schema documentation with ER diagrams and data dictionary
- **Data:** Schema and sample data files

## Data Volume

Target data size: **~2GB** with balanced coverage:
- **Products**: ~10,000 products across major categories
- **Retailers**: 20-30 major retailers
- **Stores**: ~5,000 store locations
- **Pricing History**: Daily snapshots for 2 years (~7.3M records)
- **Inventory Data**: Weekly snapshots for 1 year (~2.6M records)
- **Census Data**: Monthly data for 5 years
- **BLS Data**: Monthly CPI/PPI data for 5 years

## Compatibility

All queries are designed to work across:
- PostgreSQL (with PostGIS for spatial data)
 (Delta Lake)


## Usage

### Running Validation

```bash
cd db-10

# Phase 0: Extract queries to JSON (REQUIRED)
python3 scripts/extract_queries_to_json.py

# Phase 1: Fix verification
python3 scripts/verify_fixes.py

# Phase 2 & 4: Syntax validation and evaluation
python3 scripts/comprehensive_validator.py

# Phase 3: Execution testing
python3 scripts/execution_tester.py

# Phase 5: Generate final report
python3 scripts/generate_final_report.py
```

### ETL Pipeline

The ETL pipeline notebook (`research/etl_elt_pipeline.ipynb`) provides:
- Census Bureau API integration
- BLS API integration
- FTC data extraction
- Data.gov CKAN API integration
- Data transformation and loading
- Quality validation

## Related Documentation

- **Schema Documentation**: See `docs/SCHEMA.md` for complete schema with ER diagrams
- **Data Dictionary**: See `docs/DATA_DICTIONARY.md` for detailed column descriptions
- **Data Sources**: See `research/data_resources.json` for API documentation
- **Source Metadata**: See `research/source_metadata.json` for source tracking

---
**Last Updated:** 2026-02-04
