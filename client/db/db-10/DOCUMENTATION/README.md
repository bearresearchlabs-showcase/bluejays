---
title: Marketing Intelligence Database — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-10
---

# Marketing Intelligence Database — Documentation

**Database:** db-10  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Purpose

This database supports analytics for marketing intelligence. It models products, retailers, stores, inventory, pricing, market intelligence, deal alerts, census retail data, BLS price data, geographic markets, and pipeline metadata. Queries use aggregations, window functions, and joins for price benchmarking, market share, and data source provenance.

---

## Use Case

Target use cases for db-10:

- **Price benchmarking:** Product pricing across retailers, stores, geographic markets
- **Market intelligence:** Deal alerts, census retail data, BLS price trends
- **Inventory analytics:** Product availability, stock levels, store-level data
- **Pipeline monitoring:** Extraction metadata, data sources, load status

---

## Business Value

Marketing intelligence databases represent high-value domains for text-to-SQL because:

- Queries span products, retailers, pricing, census, and BLS data
- Stakeholders need competitive pricing and market share analytics
- Multi-source integration requires complex joins and aggregations
- Evidence bridges natural-language questions to schema-grounded SQL

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_10
```

---

### Step 3: Load Schema

From the database directory, load `schema.sql` to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_10 -f DATABASE/schema.sql
```

---

### Step 4: Load Data (Optional)

Load sample data from `data.sql` if available.

```bash
psql -U postgres -d db_10 -f DATABASE/data.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

Standard PostgreSQL. No extensions required unless noted.

---

## Schema Overview

**Total tables:** 12

- `products` — (see data dictionary)
- `retailers` — (see data dictionary)
- `stores` — (see data dictionary)
- `product_inventory` — (see data dictionary)
- `product_pricing` — (see data dictionary)
- `market_intelligence` — (see data dictionary)
- `deal_alerts` — (see data dictionary)
- `census_retail_data` — (see data dictionary)
- `bls_price_data` — (see data dictionary)
- `geographic_markets` — (see data dictionary)
- `data_sources` — (see data dictionary)
- `pipeline_metadata` — (see data dictionary)

---

## Data Dictionary

### `products`

- `product_id` VARCHAR(255) PRIMARY KEY
- `sku` VARCHAR(100) UNIQUE
- `upc` VARCHAR(50) UNIQUE
- `product_name` VARCHAR(500) NOT NULL
- `brand` VARCHAR(255) 
- `manufacturer` VARCHAR(255) 
- `model_number` VARCHAR(100) 
- `category` VARCHAR(100) NOT NULL
- `subcategory` VARCHAR(100) 
- `product_description` VARCHAR(16777216) 
- `product_image_url` VARCHAR(1000) 
- `weight_lbs` NUMERIC(8, 2) 
- `dimensions_length` NUMERIC(8, 2) 
- `dimensions_width` NUMERIC(8, 2) 
- `dimensions_height` NUMERIC(8, 2) 
- `color` VARCHAR(100) 
- `size` VARCHAR(100) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 
- `is_active` BOOLEAN 
- `data_source` VARCHAR(50) 

### `retailers`

- `retailer_id` VARCHAR(255) PRIMARY KEY
- `retailer_name` VARCHAR(255) UNIQUE, NOT NULL
- `retailer_type` VARCHAR(50)  — 'big_box', 'department_store', 'online', 'specialty', 'discount'
- `website_url` VARCHAR(500) 
- `headquarters_address` VARCHAR(500) 
- `headquarters_city` VARCHAR(100) 
- `headquarters_state` VARCHAR(2) 
- `headquarters_zip` VARCHAR(20) 
- `headquarters_country` VARCHAR(2) 
- `headquarters_latitude` NUMERIC(10, 7) 
- `headquarters_longitude` NUMERIC(10, 7) 
- `market_coverage` VARCHAR(50)  — 'national', 'regional', 'local', 'international'
- `retailer_status` VARCHAR(50)  — 'active', 'inactive', 'bankrupt'
- `founded_year` INTEGER 
- `employee_count` INTEGER 
- `annual_revenue_usd` NUMERIC(15, 2) 
- `data_source` VARCHAR(50) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `stores`

- `store_id` VARCHAR(255) PRIMARY KEY
- `retailer_id` VARCHAR(255) NOT NULL
- `store_name` VARCHAR(255) 
- `store_number` VARCHAR(50) 
- `store_address` VARCHAR(500) 
- `store_city` VARCHAR(100) 
- `store_state` VARCHAR(2) 
- `store_zip` VARCHAR(20) 
- `store_county` VARCHAR(100) 
- `store_country` VARCHAR(2) 
- `store_latitude` NUMERIC(10, 7) NOT NULL
- `store_longitude` NUMERIC(10, 7) NOT NULL
- `store_geom` GEOGRAPHY  — Point geometry for store location
- `store_type` VARCHAR(50)  — 'supercenter', 'neighborhood', 'express', 'warehouse'
- `store_size_sqft` INTEGER 
- `opening_date` DATE 
- `closing_date` DATE 
- `phone_number` VARCHAR(20) 
- `store_status` VARCHAR(50)  — 'open', 'closed', 'temporary_closed'
- `data_source` VARCHAR(50) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `product_inventory`

- `inventory_id` VARCHAR(255) PRIMARY KEY
- `product_id` VARCHAR(255) NOT NULL
- `store_id` VARCHAR(255) NOT NULL
- `stock_level` INTEGER 
- `stock_status` VARCHAR(50) NOT NULL — 'in_stock', 'out_of_stock', 'low_stock', 'limited_availability'
- `available_quantity` INTEGER 
- `reserved_quantity` INTEGER 
- `reorder_point` INTEGER 
- `last_checked_at` TIMESTAMP NOT NULL
- `last_restocked_at` TIMESTAMP 
- `data_source` VARCHAR(50) NOT NULL — 'api', 'scraper', 'manual', 'census'
- `confidence_score` NUMERIC(5, 2)  — Data quality confidence (0-100)
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `product_pricing`

- `pricing_id` VARCHAR(255) PRIMARY KEY
- `product_id` VARCHAR(255) NOT NULL
- `retailer_id` VARCHAR(255) NOT NULL
- `store_id` VARCHAR(255)  — NULL for online-only pricing
- `current_price` NUMERIC(10, 2) NOT NULL
- `original_price` NUMERIC(10, 2) 
- `sale_price` NUMERIC(10, 2) 
- `discount_percentage` NUMERIC(5, 2) 
- `price_effective_date` TIMESTAMP NOT NULL
- `price_expiry_date` TIMESTAMP 
- `price_type` VARCHAR(50)  — 'regular', 'sale', 'clearance', 'promotional'
- `price_source` VARCHAR(50) NOT NULL — 'api', 'scraper', 'manual', 'census'
- `price_confidence_score` NUMERIC(5, 2)  — Data quality confidence (0-100)
- `currency` VARCHAR(3) 
- `is_online_price` BOOLEAN 
- `shipping_cost` NUMERIC(8, 2) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `market_intelligence`

- `intelligence_id` VARCHAR(255) PRIMARY KEY
- `product_id` VARCHAR(255) NOT NULL
- `market_area` VARCHAR(100)  — ZIP code, city, state, or 'national'
- `market_type` VARCHAR(50)  — 'zip', 'city', 'state', 'msa', 'national'
- `average_price` NUMERIC(10, 2) 
- `price_range_min` NUMERIC(10, 2) 
- `price_range_max` NUMERIC(10, 2) 
- `median_price` NUMERIC(10, 2) 
- `price_std_dev` NUMERIC(10, 2) 
- `availability_rate` NUMERIC(5, 2)  — Percentage of stores with product in stock
- `market_share` NUMERIC(5, 2)  — Market share percentage
- `competitor_count` INTEGER  — Number of retailers selling this product
- `total_stores_with_product` INTEGER 
- `total_stores_checked` INTEGER 
- `intelligence_date` DATE NOT NULL
- `data_quality_score` NUMERIC(5, 2)  — Overall data quality score (0-100)
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `deal_alerts`

- `deal_id` VARCHAR(255) PRIMARY KEY
- `product_id` VARCHAR(255) NOT NULL
- `retailer_id` VARCHAR(255) NOT NULL
- `store_id` VARCHAR(255)  — NULL for online-only deals
- `deal_type` VARCHAR(50) NOT NULL — 'clearance', 'sale', 'promotion', 'flash_sale', 'bogo'
- `discount_percentage` NUMERIC(5, 2) 
- `discount_amount` NUMERIC(10, 2) 
- `deal_price` NUMERIC(10, 2) NOT NULL
- `original_price` NUMERIC(10, 2) NOT NULL
- `deal_start_date` TIMESTAMP NOT NULL
- `deal_end_date` TIMESTAMP 
- `deal_status` VARCHAR(50)  — 'active', 'expired', 'cancelled'
- `deal_description` VARCHAR(2000) 
- `deal_source` VARCHAR(50) NOT NULL — 'api', 'scraper', 'manual', 'census'
- `is_online_deal` BOOLEAN 
- `quantity_limit` INTEGER 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `census_retail_data`

- `census_id` VARCHAR(255) PRIMARY KEY
- `naics_code` VARCHAR(10)  — North American Industry Classification System code
- `industry_category` VARCHAR(255) NOT NULL
- `month` INTEGER NOT NULL — 1-12
- `year` INTEGER NOT NULL
- `retail_sales_amount` NUMERIC(15, 2)  — In millions of dollars
- `inventory_amount` NUMERIC(15, 2)  — In millions of dollars
- `store_count` INTEGER 
- `employment_count` INTEGER 
- `sales_change_percent` NUMERIC(6, 2)  — Month-over-month percentage change
- `inventory_change_percent` NUMERIC(6, 2) 
- `data_source` VARCHAR(50) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `bls_price_data`

- `bls_id` VARCHAR(255) PRIMARY KEY
- `series_id` VARCHAR(50) NOT NULL — BLS series identifier
- `product_category` VARCHAR(255) NOT NULL
- `period` VARCHAR(10) NOT NULL — 'M01' through 'M12' for monthly, 'Q01' through 'Q04' for quarterly
- `year` INTEGER NOT NULL
- `price_index_value` NUMERIC(10, 2) 
- `percent_change` NUMERIC(6, 2)  — Period-over-period percentage change
- `percent_change_year_ago` NUMERIC(6, 2)  — Year-over-year percentage change
- `base_period` VARCHAR(20)  — Base period for index (e.g., '1982-84=100')
- `index_type` VARCHAR(50)  — 'CPI', 'PPI', 'CPI_U', 'CPI_W'
- `data_source` VARCHAR(50) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `geographic_markets`

- `market_id` VARCHAR(255) PRIMARY KEY
- `market_name` VARCHAR(255) NOT NULL
- `market_type` VARCHAR(50) NOT NULL — 'zip', 'city', 'county', 'msa', 'state', 'national'
- `market_code` VARCHAR(50)  — ZIP code, FIPS code, MSA code, etc.
- `market_geom` GEOGRAPHY  — Polygon geometry for market boundaries
- `market_boundaries` VARCHAR(16777216)  — JSON or text representation of boundaries
- `population` INTEGER 
- `median_income` NUMERIC(10, 2) 
- `market_size` NUMERIC(15, 2)  — Market size in square miles or km²
- `state_code` VARCHAR(2) 
- `county_name` VARCHAR(100) 
- `msa_code` VARCHAR(10)  — Metropolitan Statistical Area code
- `data_source` VARCHAR(50) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `data_sources`

- `source_id` VARCHAR(255) PRIMARY KEY
- `source_name` VARCHAR(255) UNIQUE, NOT NULL
- `source_type` VARCHAR(50) NOT NULL — 'api', 'scraper', 'manual', 'census', 'bls', 'ftc'
- `api_endpoint` VARCHAR(1000) 
- `api_key_required` BOOLEAN 
- `rate_limit_per_hour` INTEGER 
- `rate_limit_per_day` INTEGER 
- `last_sync_at` TIMESTAMP 
- `sync_frequency` VARCHAR(50)  — 'hourly', 'daily', 'weekly', 'monthly', 'manual'
- `data_quality_score` NUMERIC(5, 2)  — Overall data quality score (0-100)
- `is_active` BOOLEAN 
- `notes` VARCHAR(2000) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `pipeline_metadata`

- `pipeline_id` VARCHAR(255) PRIMARY KEY
- `source_id` VARCHAR(255) NOT NULL
- `extraction_date` TIMESTAMP NOT NULL
- `pipeline_type` VARCHAR(50) NOT NULL — 'extract', 'transform', 'load', 'full'
- `records_processed` INTEGER 
- `records_successful` INTEGER 
- `records_failed` INTEGER 
- `processing_duration_seconds` INTEGER 
- `error_log` VARCHAR(16777216) 
- `status` VARCHAR(50)  — 'running', 'success', 'failed', 'partial'
- `start_time` TIMESTAMP NOT NULL
- `end_time` TIMESTAMP 
- `created_at` TIMESTAMP 

---

## Query Documentation

See `QUERIES/queries.md` for 30 production SQL queries with full business context, evidence, and expected output. Queries cover price benchmarking, market intelligence, inventory analytics, deal alerts, and pipeline metadata.

---

*Generated by documentation workflow. MDX-compatible markdown.*
