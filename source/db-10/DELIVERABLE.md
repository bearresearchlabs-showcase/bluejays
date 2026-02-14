# Database Deliverable: db-10 - Marketing Intelligence Database

**Database:** db-10
**Type:** Marketing Intelligence Database
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

This database implements a comprehensive marketing intelligence system with full Brickseek.com functionality for retail inventory tracking, pricing intelligence, and deal discovery. The database integrates data from U.S. government sources (Census Bureau MRTS, BLS CPI/PPI, FTC consumer data) and other reputable sources, providing real-time pricing comparisons, inventory availability tracking, market trend analysis, and deal alert generation.

### Key Features

- **Product Catalog Management**: Comprehensive product tracking with SKUs, UPCs, categories, brands, and detailed product information
- **Retailer Intelligence**: Multi-retailer tracking with store locations, market coverage, and competitive positioning
- **Pricing Intelligence**: Historical pricing tracking with deal detection, price comparison, and market positioning analysis
- **Inventory Tracking**: Real-time inventory levels by store with stock status and availability metrics
- **Market Intelligence**: Aggregated market data for competitive analysis, market share, and trend forecasting
- **Deal Discovery**: Automated deal detection and alert generation for promotions, sales, and clearance events
- **Government Data Integration**: Census Bureau retail trade data, BLS price indices, and FTC consumer complaint data
- **Spatial Analysis**: Geographic market analysis with store location mapping and market area definitions
- **Data Lineage**: Complete source tracking and data quality scoring for all data sources

### Database Platforms Supported

- **PostgreSQL**: Full support with PostGIS for spatial data (GEOGRAPHY types)
- **Databricks**: Compatible with Delta Lake format and distributed query execution
- **Databricks**: Full support with GEOGRAPHY types and time-series functions

### Business Context

This database powers a marketing intelligence platform sourced from businesses with at least $1M ARR per year. The queries demonstrate production-grade patterns used by:
- **Brickseek.com**: Retail inventory tracking and pricing intelligence
- **Honey**: Price tracking and deal discovery
- **CamelCamelCamel**: Amazon price history and deal alerts
- **RetailMeNot**: Coupon and deal aggregation
- **PriceGrabber**: Price comparison and market intelligence

### Data Sources

- **U.S. Census Bureau**: Monthly Retail Trade Survey (MRTS), Advance Retail Inventories
- **BLS Public Data API**: Consumer Price Index (CPI), Producer Price Index (PPI)
- **Federal Trade Commission**: Consumer complaint data, pricing accuracy studies
- **Data.gov**: Retail datasets, economic indicators, consumer data
- **Retail APIs**: Product catalogs, pricing, inventory data

### Data Volume

- **Target Size**: 1 GB of real data from public sources
- **Products**: ~10,000 products across major categories
- **Retailers**: 20-30 major retailers
- **Stores**: ~5,000 store locations
- **Pricing History**: Daily snapshots for 2 years (~7.3M records)
- **Inventory Data**: Weekly snapshots for 1 year (~2.6M records)
- **Government Data**: Monthly/quarterly data from Census, BLS, FTC

---

## Database Schema Documentation

### Schema Overview

The Marketing Intelligence Database consists of **12 main tables** designed to store products, retailers, stores, inventory, pricing, market intelligence, deals, and government economic data. The database supports spatial analysis with GEOGRAPHY types for store locations and market boundaries.

### Table Groups

1. **Product Management**: `products`
2. **Retailer Management**: `retailers`, `stores`
3. **Inventory & Pricing**: `product_inventory`, `product_pricing`
4. **Market Intelligence**: `market_intelligence`, `deal_alerts`
5. **Government Data**: `census_retail_data`, `bls_price_data`
6. **Geographic Data**: `geographic_markets`
7. **Data Management**: `data_sources`, `pipeline_metadata`

### Entity-Relationship Diagram

```mermaid
erDiagram
    products {
        varchar product_id PK "Primary key"
        varchar sku UK "Stock Keeping Unit"
        varchar upc UK "Universal Product Code"
        varchar product_name "Product name"
        varchar brand "Brand name"
        varchar category "Product category"
        boolean is_active "Active status"
    }
    
    retailers {
        varchar retailer_id PK "Primary key"
        varchar retailer_name UK "Retailer name"
        varchar retailer_type "Type: big_box, department_store, online"
        varchar market_coverage "Coverage: national, regional, local"
    }
    
    stores {
        varchar store_id PK "Primary key"
        varchar retailer_id FK "Retailer reference"
        varchar store_name "Store name"
        varchar store_address "Store address"
        geography store_geom SPATIAL "Point geometry"
        varchar store_status "Status: open, closed"
    }
    
    product_inventory {
        varchar inventory_id PK "Primary key"
        varchar product_id FK "Product reference"
        varchar store_id FK "Store reference"
        integer stock_level "Current stock level"
        varchar stock_status "Status: in_stock, out_of_stock"
        timestamp last_checked_at "Last inventory check"
    }
    
    product_pricing {
        varchar pricing_id PK "Primary key"
        varchar product_id FK "Product reference"
        varchar retailer_id FK "Retailer reference"
        varchar store_id FK "Store reference (nullable)"
        numeric current_price "Current price"
        numeric original_price "Original price"
        numeric discount_percentage "Discount percentage"
        timestamp price_effective_date "Price effective date"
    }
    
    market_intelligence {
        varchar intelligence_id PK "Primary key"
        varchar product_id FK "Product reference"
        varchar market_area "Market area identifier"
        numeric average_price "Average market price"
        numeric availability_rate "Availability percentage"
        date intelligence_date "Intelligence date"
    }
    
    deal_alerts {
        varchar deal_id PK "Primary key"
        varchar product_id FK "Product reference"
        varchar retailer_id FK "Retailer reference"
        numeric discount_percentage "Discount percentage"
        timestamp deal_start_date "Deal start date"
        timestamp deal_end_date "Deal end date"
    }
    
    census_retail_data {
        varchar census_id PK "Primary key"
        varchar naics_code "NAICS industry code"
        varchar time_period "Time period (YYYY-MM)"
        numeric cell_value "Data value"
        varchar source "Data source"
    }
    
    bls_price_data {
        varchar bls_id PK "Primary key"
        varchar series_id "BLS series identifier"
        integer year "Year"
        varchar period "Period (month)"
        numeric value "Price index value"
    }
    
    geographic_markets {
        varchar market_id PK "Primary key"
        varchar market_type "Type: zip, city, state, msa"
        varchar market_name "Market name"
        geography market_boundary SPATIAL "Polygon geometry"
    }
    
    products ||--o{ product_inventory : "has_inventory"
    products ||--o{ product_pricing : "has_pricing"
    products ||--o{ market_intelligence : "analyzed_in"
    products ||--o{ deal_alerts : "has_deals"
    retailers ||--o{ stores : "operates"
    retailers ||--o{ product_pricing : "sets_pricing"
    retailers ||--o{ deal_alerts : "offers_deals"
    stores ||--o{ product_inventory : "stocks"
    stores ||--o{ product_pricing : "has_pricing"
```

### Tables

#### products
Product catalog with SKUs, UPCs, categories, and brand information.

**Key Columns:**
- `product_id` (VARCHAR, PK): Unique identifier for each product
- `sku` (VARCHAR, UNIQUE): Stock Keeping Unit identifier
- `upc` (VARCHAR, UNIQUE): Universal Product Code (barcode)
- `product_name` (VARCHAR): Product name/title
- `brand` (VARCHAR): Brand name
- `category` (VARCHAR): Product category
- `subcategory` (VARCHAR): Product subcategory
- `is_active` (BOOLEAN): Whether product is currently active

#### retailers
Retailer information including headquarters and market coverage.

**Key Columns:**
- `retailer_id` (VARCHAR, PK): Unique identifier for each retailer
- `retailer_name` (VARCHAR, UNIQUE): Retailer name
- `retailer_type` (VARCHAR): Type: 'big_box', 'department_store', 'online', 'specialty', 'discount'
- `market_coverage` (VARCHAR): Coverage: 'national', 'regional', 'local', 'international'
- `retailer_status` (VARCHAR): Status: 'active', 'inactive', 'bankrupt'

#### stores
Store locations with geographic data for spatial analysis.

**Key Columns:**
- `store_id` (VARCHAR, PK): Unique identifier for each store
- `retailer_id` (VARCHAR, FK): Reference to retailers table
- `store_name` (VARCHAR): Store name
- `store_address` (VARCHAR): Store address
- `store_city`, `store_state`, `store_zip` (VARCHAR): Location details
- `store_latitude`, `store_longitude` (NUMERIC): Geographic coordinates
- `store_geom` (GEOGRAPHY): Point geometry for store location (spatial)
- `store_type` (VARCHAR): Type: 'supercenter', 'neighborhood', 'express', 'warehouse'
- `store_status` (VARCHAR): Status: 'open', 'closed', 'temporary_closed'

#### product_inventory
Inventory levels by store with stock status tracking.

**Key Columns:**
- `inventory_id` (VARCHAR, PK): Unique identifier for each inventory record
- `product_id` (VARCHAR, FK): Reference to products table
- `store_id` (VARCHAR, FK): Reference to stores table
- `stock_level` (INTEGER): Current stock level
- `stock_status` (VARCHAR): Status: 'in_stock', 'out_of_stock', 'low_stock', 'limited_availability'
- `available_quantity` (INTEGER): Available quantity
- `last_checked_at` (TIMESTAMP_NTZ): Last inventory check timestamp
- `last_restocked_at` (TIMESTAMP_NTZ): Last restock timestamp
- `confidence_score` (NUMERIC): Data quality confidence (0-100)

#### product_pricing
Pricing data with historical tracking and deal detection.

**Key Columns:**
- `pricing_id` (VARCHAR, PK): Unique identifier for each pricing record
- `product_id` (VARCHAR, FK): Reference to products table
- `retailer_id` (VARCHAR, FK): Reference to retailers table
- `store_id` (VARCHAR, FK, nullable): Reference to stores table (null for online-only pricing)
- `current_price` (NUMERIC): Current price
- `original_price` (NUMERIC): Original/regular price
- `sale_price` (NUMERIC): Sale price
- `discount_percentage` (NUMERIC): Discount percentage
- `price_effective_date` (TIMESTAMP_NTZ): Price effective date
- `price_expiry_date` (TIMESTAMP_NTZ): Price expiry date
- `price_type` (VARCHAR): Type: 'regular', 'sale', 'clearance', 'promotional'
- `is_online_price` (BOOLEAN): Whether this is an online price

#### market_intelligence
Aggregated market data for competitive analysis and trends.

**Key Columns:**
- `intelligence_id` (VARCHAR, PK): Unique identifier for each intelligence record
- `product_id` (VARCHAR, FK): Reference to products table
- `market_area` (VARCHAR): Market area identifier (ZIP, city, state, or 'national')
- `market_type` (VARCHAR): Type: 'zip', 'city', 'state', 'msa', 'national'
- `average_price` (NUMERIC): Average market price
- `price_range_min` (NUMERIC): Minimum price in market
- `price_range_max` (NUMERIC): Maximum price in market
- `availability_rate` (NUMERIC): Percentage of stores with product in stock
- `market_share` (NUMERIC): Market share percentage
- `competitor_count` (INTEGER): Number of competitors
- `intelligence_date` (DATE): Intelligence date
- `data_quality_score` (NUMERIC): Data quality score

#### deal_alerts
Deal tracking and alert generation for promotions and sales.

**Key Columns:**
- `deal_id` (VARCHAR, PK): Unique identifier for each deal
- `product_id` (VARCHAR, FK): Reference to products table
- `retailer_id` (VARCHAR, FK): Reference to retailers table
- `store_id` (VARCHAR, FK, nullable): Reference to stores table (null for online deals)
- `discount_percentage` (NUMERIC): Discount percentage
- `deal_start_date` (TIMESTAMP_NTZ): Deal start date
- `deal_end_date` (TIMESTAMP_NTZ): Deal end date
- `deal_type` (VARCHAR): Type: 'sale', 'clearance', 'promotion', 'flash_sale'
- `is_active` (BOOLEAN): Whether deal is currently active

#### census_retail_data
U.S. Census Bureau Monthly Retail Trade Survey (MRTS) data.

**Key Columns:**
- `census_id` (VARCHAR, PK): Unique identifier for each census record
- `naics_code` (VARCHAR): NAICS industry code
- `time_period` (VARCHAR): Time period (YYYY-MM format)
- `cell_value` (NUMERIC): Data value (sales, inventory, etc.)
- `source` (VARCHAR): Data source identifier
- `extracted_date` (TIMESTAMP_NTZ): Data extraction timestamp

#### bls_price_data
BLS Consumer Price Index (CPI) and Producer Price Index (PPI) data.

**Key Columns:**
- `bls_id` (VARCHAR, PK): Unique identifier for each BLS record
- `series_id` (VARCHAR): BLS series identifier
- `year` (INTEGER): Year
- `period` (VARCHAR): Period (month code: M01-M12)
- `value` (NUMERIC): Price index value
- `source` (VARCHAR): Data source identifier
- `extracted_date` (TIMESTAMP_NTZ): Data extraction timestamp

#### geographic_markets
Market area definitions with demographics and spatial boundaries.

**Key Columns:**
- `market_id` (VARCHAR, PK): Unique identifier for each market
- `market_type` (VARCHAR): Type: 'zip', 'city', 'state', 'msa', 'national'
- `market_name` (VARCHAR): Market name
- `market_code` (VARCHAR): Market code (ZIP, city name, state code, etc.)
- `market_boundary` (GEOGRAPHY): Polygon geometry for market boundary (spatial)
- `population` (INTEGER): Market population
- `median_income` (NUMERIC): Median household income
- `demographics_json` (VARCHAR): Additional demographics as JSON

#### data_sources
Source tracking for data lineage and quality management.

**Key Columns:**
- `source_id` (VARCHAR, PK): Unique identifier for each data source
- `source_name` (VARCHAR): Source name
- `source_type` (VARCHAR): Type: 'api', 'scraper', 'manual', 'government'
- `source_url` (VARCHAR): Source URL or endpoint
- `update_frequency` (VARCHAR): Update frequency
- `last_successful_extraction` (TIMESTAMP_NTZ): Last successful extraction timestamp
- `data_quality_score` (NUMERIC): Overall data quality score

#### pipeline_metadata
ETL pipeline execution tracking and performance metrics.

**Key Columns:**
- `pipeline_id` (VARCHAR, PK): Unique identifier for each pipeline run
- `pipeline_name` (VARCHAR): Pipeline name
- `execution_start_time` (TIMESTAMP_NTZ): Execution start timestamp
- `execution_end_time` (TIMESTAMP_NTZ): Execution end timestamp
- `status` (VARCHAR): Status: 'success', 'failed', 'partial'
- `records_processed` (INTEGER): Number of records processed
- `error_message` (VARCHAR): Error message if failed

---

## SQL Queries

The database includes **30 extremely complex SQL queries** covering pricing intelligence, inventory analysis, market analytics, geographic intelligence, deal detection, and competitive analysis. All queries are designed to work across PostgreSQL.

See `queries/queries.md` for complete query documentation with business context, use cases, and technical descriptions.

---

## Usage Instructions

### Database Setup

1. **PostgreSQL Setup:**
   ```bash
   # Create database
   createdb db10
   
   # Load schema
   psql db10 < data/schema.sql
   
   # Load sample data (optional)
   psql db10 < data/data.sql
   ```

2. **Databricks Setup:**
   - Use Delta Lake format
   - Load schema.sql (adapting GEOGRAPHY types as needed)
   - Use Databricks SQL for query execution

3. **Databricks Setup:**
   - Create database and schema
   - Load schema.sql (GEOGRAPHY types supported)
   - Use Databricks SQL for query execution

### Data Extraction

Run the ETL pipeline to extract data from government APIs:

```bash
cd db-10/research
jupyter notebook etl_elt_pipeline.ipynb
```

Or use the bulk download script:

```bash
cd db-10/scripts
python3 smart_bulk_extract.py
```

### Query Execution

All queries are located in `queries/queries.md` and can be executed directly on any supported database platform.

### Validation

Run the validation suite:

```bash
cd db-10
python3 scripts/extract_queries_to_json.py  # Phase 0
python3 scripts/verify_fixes.py             # Phase 1
python3 scripts/comprehensive_validator.py  # Phase 2 & 4
python3 scripts/execution_tester.py         # Phase 3
python3 scripts/generate_final_report.py   # Phase 5
```

Or use the validate command:

```bash
/validate db-10
```

---

**Last Updated:** 2026-02-04
