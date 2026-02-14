-- Marketing Intelligence Database Schema
-- Compatible with PostgreSQL
-- Production schema for marketing intelligence and retail inventory tracking system
-- Integrates data from U.S. Census Bureau, BLS, FTC, Data.gov, and retail sources

-- Products Table
-- Product catalog with SKUs, UPCs, categories, and brand information
CREATE TABLE products (
    product_id VARCHAR(255) PRIMARY KEY,
    sku VARCHAR(100) UNIQUE,
    upc VARCHAR(50) UNIQUE,
    product_name VARCHAR(500) NOT NULL,
    brand VARCHAR(255),
    manufacturer VARCHAR(255),
    model_number VARCHAR(100),
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    product_description VARCHAR(16777216),
    product_image_url VARCHAR(1000),
    weight_lbs NUMERIC(8, 2),
    dimensions_length NUMERIC(8, 2),
    dimensions_width NUMERIC(8, 2),
    dimensions_height NUMERIC(8, 2),
    color VARCHAR(100),
    size VARCHAR(100),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    is_active BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(50) DEFAULT 'MANUAL'
);

-- Retailers Table
-- Retailer information including headquarters and market coverage
CREATE TABLE retailers (
    retailer_id VARCHAR(255) PRIMARY KEY,
    retailer_name VARCHAR(255) NOT NULL UNIQUE,
    retailer_type VARCHAR(50), -- 'big_box', 'department_store', 'online', 'specialty', 'discount'
    website_url VARCHAR(500),
    headquarters_address VARCHAR(500),
    headquarters_city VARCHAR(100),
    headquarters_state VARCHAR(2),
    headquarters_zip VARCHAR(20),
    headquarters_country VARCHAR(2) DEFAULT 'US',
    headquarters_latitude NUMERIC(10, 7),
    headquarters_longitude NUMERIC(10, 7),
    market_coverage VARCHAR(50), -- 'national', 'regional', 'local', 'international'
    retailer_status VARCHAR(50) DEFAULT 'active', -- 'active', 'inactive', 'bankrupt'
    founded_year INTEGER,
    employee_count INTEGER,
    annual_revenue_usd NUMERIC(15, 2),
    data_source VARCHAR(50) DEFAULT 'MANUAL',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Stores Table
-- Store locations with geographic data for spatial analysis
CREATE TABLE stores (
    store_id VARCHAR(255) PRIMARY KEY,
    retailer_id VARCHAR(255) NOT NULL,
    store_name VARCHAR(255),
    store_number VARCHAR(50),
    store_address VARCHAR(500),
    store_city VARCHAR(100),
    store_state VARCHAR(2),
    store_zip VARCHAR(20),
    store_county VARCHAR(100),
    store_country VARCHAR(2) DEFAULT 'US',
    store_latitude NUMERIC(10, 7) NOT NULL,
    store_longitude NUMERIC(10, 7) NOT NULL,
    store_geom GEOGRAPHY, -- Point geometry for store location
    store_type VARCHAR(50), -- 'supercenter', 'neighborhood', 'express', 'warehouse'
    store_size_sqft INTEGER,
    opening_date DATE,
    closing_date DATE,
    phone_number VARCHAR(20),
    store_status VARCHAR(50) DEFAULT 'open', -- 'open', 'closed', 'temporary_closed'
    data_source VARCHAR(50) DEFAULT 'MANUAL',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (retailer_id) REFERENCES retailers(retailer_id)
);

-- Product Inventory Table
-- Inventory levels by store with stock status tracking
CREATE TABLE product_inventory (
    inventory_id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    store_id VARCHAR(255) NOT NULL,
    stock_level INTEGER DEFAULT 0,
    stock_status VARCHAR(50) NOT NULL, -- 'in_stock', 'out_of_stock', 'low_stock', 'limited_availability'
    available_quantity INTEGER,
    reserved_quantity INTEGER DEFAULT 0,
    reorder_point INTEGER,
    last_checked_at TIMESTAMP_NTZ NOT NULL,
    last_restocked_at TIMESTAMP_NTZ,
    data_source VARCHAR(50) NOT NULL, -- 'api', 'scraper', 'manual', 'census'
    confidence_score NUMERIC(5, 2), -- Data quality confidence (0-100)
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

-- Product Pricing Table
-- Pricing data with historical tracking and deal detection
CREATE TABLE product_pricing (
    pricing_id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    retailer_id VARCHAR(255) NOT NULL,
    store_id VARCHAR(255), -- NULL for online-only pricing
    current_price NUMERIC(10, 2) NOT NULL,
    original_price NUMERIC(10, 2),
    sale_price NUMERIC(10, 2),
    discount_percentage NUMERIC(5, 2),
    price_effective_date TIMESTAMP_NTZ NOT NULL,
    price_expiry_date TIMESTAMP_NTZ,
    price_type VARCHAR(50), -- 'regular', 'sale', 'clearance', 'promotional'
    price_source VARCHAR(50) NOT NULL, -- 'api', 'scraper', 'manual', 'census'
    price_confidence_score NUMERIC(5, 2), -- Data quality confidence (0-100)
    currency VARCHAR(3) DEFAULT 'USD',
    is_online_price BOOLEAN DEFAULT FALSE,
    shipping_cost NUMERIC(8, 2),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (retailer_id) REFERENCES retailers(retailer_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

-- Market Intelligence Table
-- Aggregated market data for competitive analysis and trends
CREATE TABLE market_intelligence (
    intelligence_id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    market_area VARCHAR(100), -- ZIP code, city, state, or 'national'
    market_type VARCHAR(50), -- 'zip', 'city', 'state', 'msa', 'national'
    average_price NUMERIC(10, 2),
    price_range_min NUMERIC(10, 2),
    price_range_max NUMERIC(10, 2),
    median_price NUMERIC(10, 2),
    price_std_dev NUMERIC(10, 2),
    availability_rate NUMERIC(5, 2), -- Percentage of stores with product in stock
    market_share NUMERIC(5, 2), -- Market share percentage
    competitor_count INTEGER, -- Number of retailers selling this product
    total_stores_with_product INTEGER,
    total_stores_checked INTEGER,
    intelligence_date DATE NOT NULL,
    data_quality_score NUMERIC(5, 2), -- Overall data quality score (0-100)
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Deal Alerts Table
-- Deal tracking and alert generation for promotions and sales
CREATE TABLE deal_alerts (
    deal_id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    retailer_id VARCHAR(255) NOT NULL,
    store_id VARCHAR(255), -- NULL for online-only deals
    deal_type VARCHAR(50) NOT NULL, -- 'clearance', 'sale', 'promotion', 'flash_sale', 'bogo'
    discount_percentage NUMERIC(5, 2),
    discount_amount NUMERIC(10, 2),
    deal_price NUMERIC(10, 2) NOT NULL,
    original_price NUMERIC(10, 2) NOT NULL,
    deal_start_date TIMESTAMP_NTZ NOT NULL,
    deal_end_date TIMESTAMP_NTZ,
    deal_status VARCHAR(50) DEFAULT 'active', -- 'active', 'expired', 'cancelled'
    deal_description VARCHAR(2000),
    deal_source VARCHAR(50) NOT NULL, -- 'api', 'scraper', 'manual', 'census'
    is_online_deal BOOLEAN DEFAULT FALSE,
    quantity_limit INTEGER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (retailer_id) REFERENCES retailers(retailer_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

-- Census Retail Data Table
-- U.S. Census Bureau Monthly Retail Trade Survey (MRTS) data
CREATE TABLE census_retail_data (
    census_id VARCHAR(255) PRIMARY KEY,
    naics_code VARCHAR(10), -- North American Industry Classification System code
    industry_category VARCHAR(255) NOT NULL,
    month INTEGER NOT NULL, -- 1-12
    year INTEGER NOT NULL,
    retail_sales_amount NUMERIC(15, 2), -- In millions of dollars
    inventory_amount NUMERIC(15, 2), -- In millions of dollars
    store_count INTEGER,
    employment_count INTEGER,
    sales_change_percent NUMERIC(6, 2), -- Month-over-month percentage change
    inventory_change_percent NUMERIC(6, 2),
    data_source VARCHAR(50) DEFAULT 'CENSUS_MRTS',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- BLS Price Data Table
-- Bureau of Labor Statistics Consumer Price Index (CPI) and Producer Price Index (PPI) data
CREATE TABLE bls_price_data (
    bls_id VARCHAR(255) PRIMARY KEY,
    series_id VARCHAR(50) NOT NULL, -- BLS series identifier
    product_category VARCHAR(255) NOT NULL,
    period VARCHAR(10) NOT NULL, -- 'M01' through 'M12' for monthly, 'Q01' through 'Q04' for quarterly
    year INTEGER NOT NULL,
    price_index_value NUMERIC(10, 2),
    percent_change NUMERIC(6, 2), -- Period-over-period percentage change
    percent_change_year_ago NUMERIC(6, 2), -- Year-over-year percentage change
    base_period VARCHAR(20), -- Base period for index (e.g., '1982-84=100')
    index_type VARCHAR(50), -- 'CPI', 'PPI', 'CPI_U', 'CPI_W'
    data_source VARCHAR(50) DEFAULT 'BLS_API',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Geographic Markets Table
-- Market area definitions with geographic boundaries and demographics
CREATE TABLE geographic_markets (
    market_id VARCHAR(255) PRIMARY KEY,
    market_name VARCHAR(255) NOT NULL,
    market_type VARCHAR(50) NOT NULL, -- 'zip', 'city', 'county', 'msa', 'state', 'national'
    market_code VARCHAR(50), -- ZIP code, FIPS code, MSA code, etc.
    market_geom GEOGRAPHY, -- Polygon geometry for market boundaries
    market_boundaries VARCHAR(16777216), -- JSON or text representation of boundaries
    population INTEGER,
    median_income NUMERIC(10, 2),
    market_size NUMERIC(15, 2), -- Market size in square miles or km²
    state_code VARCHAR(2),
    county_name VARCHAR(100),
    msa_code VARCHAR(10), -- Metropolitan Statistical Area code
    data_source VARCHAR(50) DEFAULT 'CENSUS',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Data Sources Table
-- Source tracking for data lineage and quality monitoring
CREATE TABLE data_sources (
    source_id VARCHAR(255) PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL, -- 'api', 'scraper', 'manual', 'census', 'bls', 'ftc'
    api_endpoint VARCHAR(1000),
    api_key_required BOOLEAN DEFAULT FALSE,
    rate_limit_per_hour INTEGER,
    rate_limit_per_day INTEGER,
    last_sync_at TIMESTAMP_NTZ,
    sync_frequency VARCHAR(50), -- 'hourly', 'daily', 'weekly', 'monthly', 'manual'
    data_quality_score NUMERIC(5, 2), -- Overall data quality score (0-100)
    is_active BOOLEAN DEFAULT TRUE,
    notes VARCHAR(2000),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Pipeline Metadata Table
-- ETL pipeline execution tracking and error logging
CREATE TABLE pipeline_metadata (
    pipeline_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,
    extraction_date TIMESTAMP_NTZ NOT NULL,
    pipeline_type VARCHAR(50) NOT NULL, -- 'extract', 'transform', 'load', 'full'
    records_processed INTEGER DEFAULT 0,
    records_successful INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    processing_duration_seconds INTEGER,
    error_log VARCHAR(16777216),
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'success', 'failed', 'partial'
    start_time TIMESTAMP_NTZ NOT NULL,
    end_time TIMESTAMP_NTZ,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id)
);

-- Create indexes for performance optimization
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_upc ON products(upc);
CREATE INDEX idx_products_category ON products(category, subcategory);
CREATE INDEX idx_products_brand ON products(brand);

CREATE INDEX idx_stores_retailer ON stores(retailer_id);
CREATE INDEX idx_stores_location ON stores(store_state, store_city);
CREATE INDEX idx_stores_geom ON stores USING GIST(store_geom);
CREATE INDEX idx_stores_lat_lon ON stores(store_latitude, store_longitude);

CREATE INDEX idx_product_inventory_product_store ON product_inventory(product_id, store_id);
CREATE INDEX idx_product_inventory_status ON product_inventory(stock_status, last_checked_at);
CREATE INDEX idx_product_inventory_product ON product_inventory(product_id);

CREATE INDEX idx_product_pricing_product_retailer ON product_pricing(product_id, retailer_id);
CREATE INDEX idx_product_pricing_store ON product_pricing(store_id);
CREATE INDEX idx_product_pricing_date ON product_pricing(price_effective_date, price_expiry_date);
CREATE INDEX idx_product_pricing_type ON product_pricing(price_type);

CREATE INDEX idx_market_intelligence_product_date ON market_intelligence(product_id, intelligence_date);
CREATE INDEX idx_market_intelligence_market ON market_intelligence(market_area, market_type);

CREATE INDEX idx_deal_alerts_product_retailer ON deal_alerts(product_id, retailer_id);
CREATE INDEX idx_deal_alerts_status_date ON deal_alerts(deal_status, deal_start_date, deal_end_date);
CREATE INDEX idx_deal_alerts_type ON deal_alerts(deal_type);

CREATE INDEX idx_census_retail_year_month ON census_retail_data(year, month);
CREATE INDEX idx_census_retail_naics ON census_retail_data(naics_code);

CREATE INDEX idx_bls_price_year_period ON bls_price_data(year, period);
CREATE INDEX idx_bls_price_category ON bls_price_data(product_category);
CREATE INDEX idx_bls_price_series ON bls_price_data(series_id);

CREATE INDEX idx_geographic_markets_type_code ON geographic_markets(market_type, market_code);
CREATE INDEX idx_geographic_markets_geom ON geographic_markets USING GIST(market_geom);

CREATE INDEX idx_pipeline_metadata_source_date ON pipeline_metadata(source_id, extraction_date);
CREATE INDEX idx_pipeline_metadata_status ON pipeline_metadata(status, start_time);
