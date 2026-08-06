# Database Schema Documentation - db-10

**Created:** 2026-02-04

## Schema Overview

The marketing intelligence database consists of 12 main tables designed to store and track retail inventory, pricing, market intelligence, and deal data from multiple government and retail sources.

## Tables

### products
Product catalog with SKUs, UPCs, categories, and brand information.

**Key Columns:**
- `product_id` (VARCHAR, PK)
- `sku` (VARCHAR, UNIQUE)
- `upc` (VARCHAR, UNIQUE)
- `product_name` (VARCHAR)
- `brand` (VARCHAR)
- `manufacturer` (VARCHAR)
- `category` (VARCHAR)
- `subcategory` (VARCHAR)
- `is_active` (BOOLEAN)

### retailers
Retailer information including headquarters and market coverage.

**Key Columns:**
- `retailer_id` (VARCHAR, PK)
- `retailer_name` (VARCHAR, UNIQUE)
- `retailer_type` (VARCHAR) - 'big_box', 'department_store', 'online', 'specialty', 'discount'
- `headquarters_city`, `headquarters_state`, `headquarters_zip` (VARCHAR)
- `market_coverage` (VARCHAR) - 'national', 'regional', 'local', 'international'
- `retailer_status` (VARCHAR) - 'active', 'inactive', 'bankrupt'

### stores
Store locations with geographic data for spatial analysis.

**Key Columns:**
- `store_id` (VARCHAR, PK)
- `retailer_id` (VARCHAR, FK -> retailers)
- `store_name`, `store_address` (VARCHAR)
- `store_city`, `store_state`, `store_zip` (VARCHAR)
- `store_latitude`, `store_longitude` (NUMERIC)
- `store_geom` (GEOGRAPHY) - Point geometry for store location
- `store_type` (VARCHAR) - 'supercenter', 'neighborhood', 'express', 'warehouse'
- `store_status` (VARCHAR) - 'open', 'closed', 'temporary_closed'

### product_inventory
Inventory levels by store with stock status tracking.

**Key Columns:**
- `inventory_id` (VARCHAR, PK)
- `product_id` (VARCHAR, FK -> products)
- `store_id` (VARCHAR, FK -> stores)
- `stock_level` (INTEGER)
- `stock_status` (VARCHAR) - 'in_stock', 'out_of_stock', 'low_stock', 'limited_availability'
- `available_quantity` (INTEGER)
- `last_checked_at` (TIMESTAMP_NTZ)
- `last_restocked_at` (TIMESTAMP_NTZ)
- `confidence_score` (NUMERIC) - Data quality confidence (0-100)

### product_pricing
Pricing data with historical tracking and deal detection.

**Key Columns:**
- `pricing_id` (VARCHAR, PK)
- `product_id` (VARCHAR, FK -> products)
- `retailer_id` (VARCHAR, FK -> retailers)
- `store_id` (VARCHAR, FK -> stores, nullable)
- `current_price` (NUMERIC)
- `original_price` (NUMERIC)
- `sale_price` (NUMERIC)
- `discount_percentage` (NUMERIC)
- `price_effective_date` (TIMESTAMP_NTZ)
- `price_expiry_date` (TIMESTAMP_NTZ)
- `price_type` (VARCHAR) - 'regular', 'sale', 'clearance', 'promotional'
- `is_online_price` (BOOLEAN)

### market_intelligence
Aggregated market data for competitive analysis and trends.

**Key Columns:**
- `intelligence_id` (VARCHAR, PK)
- `product_id` (VARCHAR, FK -> products)
- `market_area` (VARCHAR) - ZIP code, city, state, or 'national'
- `market_type` (VARCHAR) - 'zip', 'city', 'state', 'msa', 'national'
- `average_price`, `price_range_min`, `price_range_max` (NUMERIC)
- `availability_rate` (NUMERIC) - Percentage of stores with product in stock
- `market_share` (NUMERIC) - Market share percentage
- `competitor_count` (INTEGER)
- `intelligence_date` (DATE)
- `data_quality_score` (NUMERIC)

### deal_alerts
Deal tracking and alert generation for promotions and sales.

**Key Columns:**
- `deal_id` (VARCHAR, PK)
- `product_id` (VARCHAR, FK -> products)
- `retailer_id` (VARCHAR, FK -> retailers)
- `store_id` (VARCHAR, FK -> stores, nullable)
- `deal_type` (VARCHAR) - 'clearance', 'sale', 'promotion', 'flash_sale', 'bogo'
- `discount_percentage`, `discount_amount` (NUMERIC)
- `deal_price`, `original_price` (NUMERIC)
- `deal_start_date`, `deal_end_date` (TIMESTAMP_NTZ)
- `deal_status` (VARCHAR) - 'active', 'expired', 'cancelled'
- `is_online_deal` (BOOLEAN)

### census_retail_data
U.S. Census Bureau Monthly Retail Trade Survey (MRTS) data.

**Key Columns:**
- `census_id` (VARCHAR, PK)
- `naics_code` (VARCHAR) - North American Industry Classification System code
- `industry_category` (VARCHAR)
- `month` (INTEGER) - 1-12
- `year` (INTEGER)
- `retail_sales_amount` (NUMERIC) - In millions of dollars
- `inventory_amount` (NUMERIC) - In millions of dollars
- `store_count`, `employment_count` (INTEGER)
- `sales_change_percent`, `inventory_change_percent` (NUMERIC)
- `data_source` (VARCHAR) - 'CENSUS_MRTS'

### bls_price_data
Bureau of Labor Statistics Consumer Price Index (CPI) and Producer Price Index (PPI) data.

**Key Columns:**
- `bls_id` (VARCHAR, PK)
- `series_id` (VARCHAR) - BLS series identifier
- `product_category` (VARCHAR)
- `period` (VARCHAR) - 'M01' through 'M12' for monthly
- `year` (INTEGER)
- `price_index_value` (NUMERIC)
- `percent_change` (NUMERIC) - Period-over-period percentage change
- `percent_change_year_ago` (NUMERIC) - Year-over-year percentage change
- `base_period` (VARCHAR) - Base period for index
- `index_type` (VARCHAR) - 'CPI', 'PPI', 'CPI_U', 'CPI_W'
- `data_source` (VARCHAR) - 'BLS_API'

### geographic_markets
Market area definitions with geographic boundaries and demographics.

**Key Columns:**
- `market_id` (VARCHAR, PK)
- `market_name` (VARCHAR)
- `market_type` (VARCHAR) - 'zip', 'city', 'county', 'msa', 'state', 'national'
- `market_code` (VARCHAR) - ZIP code, FIPS code, MSA code, etc.
- `market_geom` (GEOGRAPHY) - Polygon geometry for market boundaries
- `population` (INTEGER)
- `median_income` (NUMERIC)
- `market_size` (NUMERIC) - Market size in square miles or km²
- `state_code` (VARCHAR)
- `county_name` (VARCHAR)
- `msa_code` (VARCHAR) - Metropolitan Statistical Area code

### data_sources
Source tracking for data lineage and quality monitoring.

**Key Columns:**
- `source_id` (VARCHAR, PK)
- `source_name` (VARCHAR, UNIQUE)
- `source_type` (VARCHAR) - 'api', 'scraper', 'manual', 'census', 'bls', 'ftc'
- `api_endpoint` (VARCHAR)
- `rate_limit_per_hour`, `rate_limit_per_day` (INTEGER)
- `last_sync_at` (TIMESTAMP_NTZ)
- `sync_frequency` (VARCHAR) - 'hourly', 'daily', 'weekly', 'monthly', 'manual'
- `data_quality_score` (NUMERIC)
- `is_active` (BOOLEAN)

### pipeline_metadata
ETL pipeline execution tracking and error logging.

**Key Columns:**
- `pipeline_id` (VARCHAR, PK)
- `source_id` (VARCHAR, FK -> data_sources)
- `extraction_date` (TIMESTAMP_NTZ)
- `pipeline_type` (VARCHAR) - 'extract', 'transform', 'load', 'full'
- `records_processed`, `records_successful`, `records_failed` (INTEGER)
- `processing_duration_seconds` (INTEGER)
- `error_log` (VARCHAR)
- `status` (VARCHAR) - 'running', 'success', 'failed', 'partial'
- `start_time`, `end_time` (TIMESTAMP_NTZ)

## Entity-Relationship Diagram

```mermaid
erDiagram
    products {
        varchar product_id PK "Primary key"
        varchar sku UK "Unique SKU"
        varchar upc UK "Unique UPC"
        varchar product_name "Product name"
        varchar brand "Brand name"
        varchar category "Product category"
        varchar subcategory "Product subcategory"
        boolean is_active "Active status"
    }
    
    retailers {
        varchar retailer_id PK "Primary key"
        varchar retailer_name UK "Unique retailer name"
        varchar retailer_type "Retailer type"
        varchar market_coverage "Market coverage"
        varchar retailer_status "Status"
    }
    
    stores {
        varchar store_id PK "Primary key"
        varchar retailer_id FK "Retailer"
        varchar store_name "Store name"
        varchar store_city "City"
        varchar store_state "State"
        varchar store_zip "ZIP code"
        numeric store_latitude "Latitude"
        numeric store_longitude "Longitude"
        geography store_geom SPATIAL "Point geometry"
        varchar store_status "Status"
    }
    
    product_inventory {
        varchar inventory_id PK "Primary key"
        varchar product_id FK "Product"
        varchar store_id FK "Store"
        integer stock_level "Stock level"
        varchar stock_status "Stock status"
        timestamp last_checked_at "Last checked"
    }
    
    product_pricing {
        varchar pricing_id PK "Primary key"
        varchar product_id FK "Product"
        varchar retailer_id FK "Retailer"
        varchar store_id FK "Store"
        numeric current_price "Current price"
        numeric original_price "Original price"
        numeric discount_percentage "Discount %"
        timestamp price_effective_date "Effective date"
    }
    
    market_intelligence {
        varchar intelligence_id PK "Primary key"
        varchar product_id FK "Product"
        varchar market_area "Market area"
        numeric average_price "Average price"
        numeric market_share "Market share %"
        date intelligence_date "Intelligence date"
    }
    
    deal_alerts {
        varchar deal_id PK "Primary key"
        varchar product_id FK "Product"
        varchar retailer_id FK "Retailer"
        varchar deal_type "Deal type"
        numeric discount_percentage "Discount %"
        timestamp deal_start_date "Start date"
        timestamp deal_end_date "End date"
    }
    
    census_retail_data {
        varchar census_id PK "Primary key"
        varchar naics_code "NAICS code"
        varchar industry_category "Industry"
        integer month "Month"
        integer year "Year"
        numeric retail_sales_amount "Sales amount"
        numeric inventory_amount "Inventory amount"
    }
    
    bls_price_data {
        varchar bls_id PK "Primary key"
        varchar series_id "BLS series ID"
        varchar product_category "Category"
        varchar period "Period"
        integer year "Year"
        numeric price_index_value "Index value"
        numeric percent_change "Percent change"
    }
    
    geographic_markets {
        varchar market_id PK "Primary key"
        varchar market_name "Market name"
        varchar market_type "Market type"
        varchar market_code "Market code"
        geography market_geom SPATIAL "Polygon geometry"
        integer population "Population"
        numeric median_income "Median income"
    }
    
    data_sources {
        varchar source_id PK "Primary key"
        varchar source_name UK "Source name"
        varchar source_type "Source type"
        varchar api_endpoint "API endpoint"
        timestamp last_sync_at "Last sync"
    }
    
    pipeline_metadata {
        varchar pipeline_id PK "Primary key"
        varchar source_id FK "Data source"
        timestamp extraction_date "Extraction date"
        integer records_processed "Records processed"
        varchar status "Status"
    }
    
    products ||--o{ product_inventory : "has"
    products ||--o{ product_pricing : "priced_at"
    products ||--o{ market_intelligence : "analyzed_in"
    products ||--o{ deal_alerts : "has_deals"
    
    retailers ||--o{ stores : "operates"
    retailers ||--o{ product_pricing : "sells_at"
    retailers ||--o{ deal_alerts : "offers"
    
    stores ||--o{ product_inventory : "stocks"
    stores ||--o{ product_pricing : "prices_at"
    
    data_sources ||--o{ pipeline_metadata : "tracked_by"
```

## Spatial Data Types

The database uses GEOGRAPHY type for spatial data:
- **PostgreSQL**: PostGIS GEOGRAPHY type
- **Databricks**: GEOMETRY type (compatible)
- **Databricks**: GEOGRAPHY type

## Indexes

Spatial indexes are created on geometry columns using GIST indexes for optimal spatial query performance. Additional indexes are created on frequently queried columns like product_id, retailer_id, store_id, and date columns.

## Relationships

- **products** → **product_inventory**: One-to-many (product can be in multiple stores)
- **products** → **product_pricing**: One-to-many (product can have multiple prices over time)
- **retailers** → **stores**: One-to-many (retailer operates multiple stores)
- **stores** → **product_inventory**: One-to-many (store stocks multiple products)
- **products** → **market_intelligence**: One-to-many (product analyzed in multiple markets)
- **products** → **deal_alerts**: One-to-many (product can have multiple deals)

---
**Last Updated:** 2026-02-04
