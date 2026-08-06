# Data Dictionary - db-10 Marketing Intelligence Database

**Created:** 2026-02-04

## Overview

This data dictionary provides detailed descriptions of all tables and columns in the Marketing Intelligence Database (db-10). The database tracks products, retailers, stores, inventory, pricing, market intelligence, deals, and government economic data.

## Tables by Functional Category

### Product Management

#### products
Product catalog with SKUs, UPCs, categories, and brand information.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| product_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for each product |
| sku | VARCHAR(100) | UNIQUE | Stock Keeping Unit identifier |
| upc | VARCHAR(50) | UNIQUE | Universal Product Code (barcode) |
| product_name | VARCHAR(500) | NOT NULL | Product name/title |
| brand | VARCHAR(255) | | Brand name (e.g., Samsung, Nike, Apple) |
| manufacturer | VARCHAR(255) | | Manufacturer name |
| model_number | VARCHAR(100) | | Product model number |
| category | VARCHAR(100) | NOT NULL | Product category (e.g., Electronics, Apparel) |
| subcategory | VARCHAR(100) | | Product subcategory (e.g., Televisions, Footwear) |
| product_description | VARCHAR(16777216) | | Detailed product description |
| product_image_url | VARCHAR(1000) | | URL to product image |
| weight_lbs | NUMERIC(8, 2) | | Product weight in pounds |
| dimensions_length | NUMERIC(8, 2) | | Product length dimension |
| dimensions_width | NUMERIC(8, 2) | | Product width dimension |
| dimensions_height | NUMERIC(8, 2) | | Product height dimension |
| color | VARCHAR(100) | | Product color |
| size | VARCHAR(100) | | Product size |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |
| is_active | BOOLEAN | DEFAULT TRUE | Whether product is currently active |
| data_source | VARCHAR(50) | DEFAULT 'MANUAL' | Source of product data |

### Retailer Management

#### retailers
Retailer information including headquarters and market coverage.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| retailer_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for each retailer |
| retailer_name | VARCHAR(255) | NOT NULL UNIQUE | Retailer name (e.g., Walmart, Target) |
| retailer_type | VARCHAR(50) | | Type: 'big_box', 'department_store', 'online', 'specialty', 'discount' |
| website_url | VARCHAR(500) | | Retailer website URL |
| headquarters_address | VARCHAR(500) | | Headquarters street address |
| headquarters_city | VARCHAR(100) | | Headquarters city |
| headquarters_state | VARCHAR(2) | | Headquarters state (2-letter code) |
| headquarters_zip | VARCHAR(20) | | Headquarters ZIP code |
| headquarters_country | VARCHAR(2) | DEFAULT 'US' | Headquarters country code |
| headquarters_latitude | NUMERIC(10, 7) | | Headquarters latitude coordinate |
| headquarters_longitude | NUMERIC(10, 7) | | Headquarters longitude coordinate |
| market_coverage | VARCHAR(50) | | Coverage: 'national', 'regional', 'local', 'international' |
| retailer_status | VARCHAR(50) | DEFAULT 'active' | Status: 'active', 'inactive', 'bankrupt' |
| founded_year | INTEGER | | Year retailer was founded |
| employee_count | INTEGER | | Number of employees |
| annual_revenue_usd | NUMERIC(15, 2) | | Annual revenue in USD |
| data_source | VARCHAR(50) | DEFAULT 'MANUAL' | Source of retailer data |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

### Store Management

#### stores
Store locations with geographic data for spatial analysis.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| store_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for each store |
| retailer_id | VARCHAR(255) | NOT NULL, FK -> retailers | Retailer that operates this store |
| store_name | VARCHAR(255) | | Store name/location identifier |
| store_number | VARCHAR(50) | | Store number/code |
| store_address | VARCHAR(500) | | Store street address |
| store_city | VARCHAR(100) | | Store city |
| store_state | VARCHAR(2) | | Store state (2-letter code) |
| store_zip | VARCHAR(20) | | Store ZIP code |
| store_county | VARCHAR(100) | | Store county name |
| store_country | VARCHAR(2) | DEFAULT 'US' | Store country code |
| store_latitude | NUMERIC(10, 7) | NOT NULL | Store latitude coordinate |
| store_longitude | NUMERIC(10, 7) | NOT NULL | Store longitude coordinate |
| store_geom | GEOGRAPHY | | Point geometry for store location (spatial) |
| store_type | VARCHAR(50) | | Type: 'supercenter', 'neighborhood', 'express', 'warehouse' |
| store_size_sqft | INTEGER | | Store size in square feet |
| opening_date | DATE | | Store opening date |
| closing_date | DATE | | Store closing date (if closed) |
| phone_number | VARCHAR(20) | | Store phone number |
| store_status | VARCHAR(50) | DEFAULT 'open' | Status: 'open', 'closed', 'temporary_closed' |
| data_source | VARCHAR(50) | DEFAULT 'MANUAL' | Source of store data |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

### Inventory Management

#### product_inventory
Inventory levels by store with stock status tracking.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| inventory_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for inventory record |
| product_id | VARCHAR(255) | NOT NULL, FK -> products | Product identifier |
| store_id | VARCHAR(255) | NOT NULL, FK -> stores | Store identifier |
| stock_level | INTEGER | DEFAULT 0 | Current stock level/quantity |
| stock_status | VARCHAR(50) | NOT NULL | Status: 'in_stock', 'out_of_stock', 'low_stock', 'limited_availability' |
| available_quantity | INTEGER | | Available quantity for sale |
| reserved_quantity | INTEGER | DEFAULT 0 | Reserved/held quantity |
| reorder_point | INTEGER | | Reorder point threshold |
| last_checked_at | TIMESTAMP_NTZ | NOT NULL | Last time inventory was checked |
| last_restocked_at | TIMESTAMP_NTZ | | Last time inventory was restocked |
| data_source | VARCHAR(50) | NOT NULL | Source: 'api', 'scraper', 'manual', 'census' |
| confidence_score | NUMERIC(5, 2) | | Data quality confidence (0-100) |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

### Pricing Management

#### product_pricing
Pricing data with historical tracking and deal detection.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| pricing_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for pricing record |
| product_id | VARCHAR(255) | NOT NULL, FK -> products | Product identifier |
| retailer_id | VARCHAR(255) | NOT NULL, FK -> retailers | Retailer identifier |
| store_id | VARCHAR(255) | FK -> stores | Store identifier (NULL for online-only pricing) |
| current_price | NUMERIC(10, 2) | NOT NULL | Current selling price |
| original_price | NUMERIC(10, 2) | | Original/regular price |
| sale_price | NUMERIC(10, 2) | | Sale price (if on sale) |
| discount_percentage | NUMERIC(5, 2) | | Discount percentage |
| price_effective_date | TIMESTAMP_NTZ | NOT NULL | Date price became effective |
| price_expiry_date | TIMESTAMP_NTZ | | Date price expires (if applicable) |
| price_type | VARCHAR(50) | | Type: 'regular', 'sale', 'clearance', 'promotional' |
| price_source | VARCHAR(50) | NOT NULL | Source: 'api', 'scraper', 'manual', 'census' |
| price_confidence_score | NUMERIC(5, 2) | | Data quality confidence (0-100) |
| currency | VARCHAR(3) | DEFAULT 'USD' | Currency code |
| is_online_price | BOOLEAN | DEFAULT FALSE | Whether this is online-only pricing |
| shipping_cost | NUMERIC(8, 2) | | Shipping cost (if applicable) |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

### Market Intelligence

#### market_intelligence
Aggregated market data for competitive analysis and trends.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| intelligence_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for intelligence record |
| product_id | VARCHAR(255) | NOT NULL, FK -> products | Product identifier |
| market_area | VARCHAR(100) | | Market area: ZIP code, city, state, or 'national' |
| market_type | VARCHAR(50) | | Type: 'zip', 'city', 'state', 'msa', 'national' |
| average_price | NUMERIC(10, 2) | | Average price across market |
| price_range_min | NUMERIC(10, 2) | | Minimum price in market |
| price_range_max | NUMERIC(10, 2) | | Maximum price in market |
| median_price | NUMERIC(10, 2) | | Median price in market |
| price_std_dev | NUMERIC(10, 2) | | Price standard deviation |
| availability_rate | NUMERIC(5, 2) | | Percentage of stores with product in stock |
| market_share | NUMERIC(5, 2) | | Market share percentage |
| competitor_count | INTEGER | | Number of retailers selling this product |
| total_stores_with_product | INTEGER | | Total stores with product available |
| total_stores_checked | INTEGER | | Total stores checked |
| intelligence_date | DATE | NOT NULL | Date of intelligence calculation |
| data_quality_score | NUMERIC(5, 2) | | Overall data quality score (0-100) |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

### Deal Management

#### deal_alerts
Deal tracking and alert generation for promotions and sales.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| deal_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for deal |
| product_id | VARCHAR(255) | NOT NULL, FK -> products | Product identifier |
| retailer_id | VARCHAR(255) | NOT NULL, FK -> retailers | Retailer identifier |
| store_id | VARCHAR(255) | FK -> stores | Store identifier (NULL for online-only deals) |
| deal_type | VARCHAR(50) | NOT NULL | Type: 'clearance', 'sale', 'promotion', 'flash_sale', 'bogo' |
| discount_percentage | NUMERIC(5, 2) | | Discount percentage |
| discount_amount | NUMERIC(10, 2) | | Discount amount in currency |
| deal_price | NUMERIC(10, 2) | NOT NULL | Deal/offer price |
| original_price | NUMERIC(10, 2) | NOT NULL | Original price before deal |
| deal_start_date | TIMESTAMP_NTZ | NOT NULL | Deal start date/time |
| deal_end_date | TIMESTAMP_NTZ | | Deal end date/time |
| deal_status | VARCHAR(50) | DEFAULT 'active' | Status: 'active', 'expired', 'cancelled' |
| deal_description | VARCHAR(2000) | | Deal description/details |
| deal_source | VARCHAR(50) | NOT NULL | Source: 'api', 'scraper', 'manual', 'census' |
| is_online_deal | BOOLEAN | DEFAULT FALSE | Whether deal is online-only |
| quantity_limit | INTEGER | | Quantity limit per customer (if applicable) |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

### Government Data Sources

#### census_retail_data
U.S. Census Bureau Monthly Retail Trade Survey (MRTS) data.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| census_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for census record |
| naics_code | VARCHAR(10) | | North American Industry Classification System code |
| industry_category | VARCHAR(255) | NOT NULL | Industry category name |
| month | INTEGER | NOT NULL | Month (1-12) |
| year | INTEGER | NOT NULL | Year |
| retail_sales_amount | NUMERIC(15, 2) | | Retail sales amount in millions of dollars |
| inventory_amount | NUMERIC(15, 2) | | Inventory amount in millions of dollars |
| store_count | INTEGER | | Number of stores |
| employment_count | INTEGER | | Employment count |
| sales_change_percent | NUMERIC(6, 2) | | Month-over-month sales change percentage |
| inventory_change_percent | NUMERIC(6, 2) | | Month-over-month inventory change percentage |
| data_source | VARCHAR(50) | DEFAULT 'CENSUS_MRTS' | Data source identifier |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

#### bls_price_data
Bureau of Labor Statistics Consumer Price Index (CPI) and Producer Price Index (PPI) data.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| bls_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for BLS record |
| series_id | VARCHAR(50) | NOT NULL | BLS series identifier |
| product_category | VARCHAR(255) | NOT NULL | Product category name |
| period | VARCHAR(10) | NOT NULL | Period: 'M01' through 'M12' for monthly, 'Q01' through 'Q04' for quarterly |
| year | INTEGER | NOT NULL | Year |
| price_index_value | NUMERIC(10, 2) | | Price index value |
| percent_change | NUMERIC(6, 2) | | Period-over-period percentage change |
| percent_change_year_ago | NUMERIC(6, 2) | | Year-over-year percentage change |
| base_period | VARCHAR(20) | | Base period for index (e.g., '1982-84=100') |
| index_type | VARCHAR(50) | | Type: 'CPI', 'PPI', 'CPI_U', 'CPI_W' |
| data_source | VARCHAR(50) | DEFAULT 'BLS_API' | Data source identifier |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

### Geographic Data

#### geographic_markets
Market area definitions with geographic boundaries and demographics.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| market_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for market |
| market_name | VARCHAR(255) | NOT NULL | Market name |
| market_type | VARCHAR(50) | NOT NULL | Type: 'zip', 'city', 'county', 'msa', 'state', 'national' |
| market_code | VARCHAR(50) | | Market code: ZIP code, FIPS code, MSA code, etc. |
| market_geom | GEOGRAPHY | | Polygon geometry for market boundaries (spatial) |
| market_boundaries | VARCHAR(16777216) | | JSON or text representation of boundaries |
| population | INTEGER | | Market population |
| median_income | NUMERIC(10, 2) | | Median household income |
| market_size | NUMERIC(15, 2) | | Market size in square miles or km² |
| state_code | VARCHAR(2) | | State code (2-letter) |
| county_name | VARCHAR(100) | | County name |
| msa_code | VARCHAR(10) | | Metropolitan Statistical Area code |
| data_source | VARCHAR(50) | DEFAULT 'CENSUS' | Data source identifier |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

### Pipeline Management

#### data_sources
Source tracking for data lineage and quality monitoring.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| source_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for data source |
| source_name | VARCHAR(255) | NOT NULL UNIQUE | Source name (e.g., 'Census Bureau MRTS API') |
| source_type | VARCHAR(50) | NOT NULL | Type: 'api', 'scraper', 'manual', 'census', 'bls', 'ftc' |
| api_endpoint | VARCHAR(1000) | | API endpoint URL |
| api_key_required | BOOLEAN | DEFAULT FALSE | Whether API key is required |
| rate_limit_per_hour | INTEGER | | Rate limit per hour |
| rate_limit_per_day | INTEGER | | Rate limit per day |
| last_sync_at | TIMESTAMP_NTZ | | Last synchronization timestamp |
| sync_frequency | VARCHAR(50) | | Frequency: 'hourly', 'daily', 'weekly', 'monthly', 'manual' |
| data_quality_score | NUMERIC(5, 2) | | Overall data quality score (0-100) |
| is_active | BOOLEAN | DEFAULT TRUE | Whether source is currently active |
| notes | VARCHAR(2000) | | Additional notes about the source |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp |

#### pipeline_metadata
ETL pipeline execution tracking and error logging.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| pipeline_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for pipeline execution |
| source_id | VARCHAR(255) | NOT NULL, FK -> data_sources | Data source identifier |
| extraction_date | TIMESTAMP_NTZ | NOT NULL | Date/time of data extraction |
| pipeline_type | VARCHAR(50) | NOT NULL | Type: 'extract', 'transform', 'load', 'full' |
| records_processed | INTEGER | DEFAULT 0 | Total records processed |
| records_successful | INTEGER | DEFAULT 0 | Records successfully processed |
| records_failed | INTEGER | DEFAULT 0 | Records that failed processing |
| processing_duration_seconds | INTEGER | | Processing duration in seconds |
| error_log | VARCHAR(16777216) | | Error log details |
| status | VARCHAR(50) | DEFAULT 'running' | Status: 'running', 'success', 'failed', 'partial' |
| start_time | TIMESTAMP_NTZ | NOT NULL | Pipeline start time |
| end_time | TIMESTAMP_NTZ | | Pipeline end time |
| created_at | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp |

## Data Types Reference

- **VARCHAR(n)**: Variable-length character string with maximum length n
- **NUMERIC(p, s)**: Numeric data type with precision p and scale s
- **INTEGER**: 32-bit signed integer
- **BOOLEAN**: Boolean true/false value
- **DATE**: Date value (year, month, day)
- **TIMESTAMP_NTZ**: Timestamp without timezone (compatible across PostgreSQL)
- **GEOGRAPHY**: Spatial geography data type for geographic coordinates and geometries

## Foreign Key Relationships

1. **stores.retailer_id** → **retailers.retailer_id**
2. **product_inventory.product_id** → **products.product_id**
3. **product_inventory.store_id** → **stores.store_id**
4. **product_pricing.product_id** → **products.product_id**
5. **product_pricing.retailer_id** → **retailers.retailer_id**
6. **product_pricing.store_id** → **stores.store_id**
7. **market_intelligence.product_id** → **products.product_id**
8. **deal_alerts.product_id** → **products.product_id**
9. **deal_alerts.retailer_id** → **retailers.retailer_id**
10. **deal_alerts.store_id** → **stores.store_id**
11. **pipeline_metadata.source_id** → **data_sources.source_id**

## Indexes

- **products**: Indexes on sku, upc, category, subcategory, brand
- **stores**: Indexes on retailer_id, location (state/city), spatial index on store_geom
- **product_inventory**: Indexes on product_id, store_id, stock_status, last_checked_at
- **product_pricing**: Indexes on product_id, retailer_id, store_id, price_effective_date, price_type
- **market_intelligence**: Indexes on product_id, intelligence_date, market_area
- **deal_alerts**: Indexes on product_id, retailer_id, deal_status, deal_start_date
- **census_retail_data**: Indexes on year, month, naics_code
- **bls_price_data**: Indexes on year, period, product_category, series_id
- **geographic_markets**: Indexes on market_type, market_code, spatial index on market_geom
- **pipeline_metadata**: Indexes on source_id, extraction_date, status

---
**Last Updated:** 2026-02-04
