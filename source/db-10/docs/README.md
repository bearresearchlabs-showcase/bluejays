# Marketing Intelligence Database - Documentation

**Database:** db-10
**Created:** 2026-02-04

## Overview

This database contains marketing intelligence data from U.S. Census Bureau, BLS, FTC, Data.gov, and retail sources. It includes products, retailers, stores, inventory levels, pricing data, market intelligence aggregations, deal alerts, census retail data, BLS price indices, and geographic markets.

## Database Schema

See `../data/schema.sql` for the complete database schema.

### Key Tables

- **products** - Product catalog with SKUs, UPCs, categories, and brand information
- **retailers** - Retailer information including headquarters and market coverage
- **stores** - Store locations with geographic data for spatial analysis
- **product_inventory** - Inventory levels by store with stock status tracking
- **product_pricing** - Pricing data with historical tracking and deal detection
- **market_intelligence** - Aggregated market data for competitive analysis and trends
- **deal_alerts** - Deal tracking and alert generation for promotions and sales
- **census_retail_data** - U.S. Census Bureau Monthly Retail Trade Survey (MRTS) data
- **bls_price_data** - Bureau of Labor Statistics CPI and PPI data
- **geographic_markets** - Market area definitions with geographic boundaries
- **data_sources** - Source tracking for data lineage and quality monitoring
- **pipeline_metadata** - ETL pipeline execution tracking and error logging

## Queries

See `../queries/queries.md` for 30 extremely complex SQL queries.

All queries are designed to work across:
- PostgreSQL
 (Delta Lake)


## Data Sources

- **U.S. Census Bureau** - Monthly Retail Trade Survey (MRTS)
- **BLS** - Consumer Price Index, Producer Price Index
- **FTC** - Federal Trade Commission data
- **Data.gov** - Federal open data

## Usage

1. Load schema: `psql -f data/schema.sql` (PostgreSQL)
2. Load data: `psql -f data/data.sql` (PostgreSQL)
3. Run queries: See `queries/queries.md`

---
**Last Updated:** 2026-02-04
