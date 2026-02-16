-- Marketing Intelligence Database Sample Data
-- Production sample data for marketing intelligence and retail inventory tracking system
-- Compatible with PostgreSQL

-- Insert Retailers
INSERT INTO retailers (retailer_id, retailer_name, retailer_type, website_url, headquarters_city, headquarters_state, headquarters_zip, market_coverage, founded_year, employee_count) VALUES
('RTL001', 'Walmart', 'big_box', 'https://www.walmart.com', 'Bentonville', 'AR', '72716', 'national', 1962, 2100000),
('RTL002', 'Target', 'big_box', 'https://www.target.com', 'Minneapolis', 'MN', '55403', 'national', 1902, 450000),
('RTL003', 'Amazon', 'online', 'https://www.amazon.com', 'Seattle', 'WA', '98101', 'international', 1994, 1500000),
('RTL004', 'Home Depot', 'specialty', 'https://www.homedepot.com', 'Atlanta', 'GA', '30339', 'national', 1978, 500000),
('RTL005', 'Lowe''s', 'specialty', 'https://www.lowes.com', 'Mooresville', 'NC', '28117', 'national', 1946, 300000),
('RTL006', 'Best Buy', 'specialty', 'https://www.bestbuy.com', 'Richfield', 'MN', '55423', 'national', 1966, 125000),
('RTL007', 'Costco', 'warehouse', 'https://www.costco.com', 'Issaquah', 'WA', '98027', 'international', 1983, 304000),
('RTL008', 'CVS', 'specialty', 'https://www.cvs.com', 'Woonsocket', 'RI', '02895', 'national', 1963, 300000),
('RTL009', 'Walgreens', 'specialty', 'https://www.walgreens.com', 'Deerfield', 'IL', '60015', 'national', 1901, 315000),
('RTL010', 'Macy''s', 'department_store', 'https://www.macys.com', 'New York', 'NY', '10001', 'national', 1858, 130000);

-- Insert Stores (sample locations across major cities)
INSERT INTO stores (store_id, retailer_id, store_name, store_number, store_address, store_city, store_state, store_zip, store_county, store_latitude, store_longitude, store_type, store_size_sqft, opening_date, store_status) VALUES
('STR001', 'RTL001', 'Walmart Supercenter', '1234', '123 Main Street', 'New York', 'NY', '10001', 'New York', 40.7128, -74.0060, 'supercenter', 180000, '2010-01-15', 'open'),
('STR002', 'RTL001', 'Walmart Supercenter', '5678', '456 Oak Avenue', 'Los Angeles', 'CA', '90001', 'Los Angeles', 34.0522, -118.2437, 'supercenter', 180000, '2012-03-20', 'open'),
('STR003', 'RTL002', 'Target Store', '9012', '789 Pine Road', 'Chicago', 'IL', '60601', 'Cook', 41.8781, -87.6298, 'supercenter', 130000, '2015-06-10', 'open'),
('STR004', 'RTL002', 'Target Store', '3456', '321 Elm Street', 'Houston', 'TX', '77001', 'Harris', 29.7604, -95.3698, 'supercenter', 130000, '2014-09-05', 'open'),
('STR005', 'RTL004', 'Home Depot', '7890', '654 Maple Drive', 'Phoenix', 'AZ', '85001', 'Maricopa', 33.4484, -112.0740, 'supercenter', 105000, '2011-11-12', 'open'),
('STR006', 'RTL005', 'Lowe''s Home Improvement', '2468', '987 Cedar Lane', 'Philadelphia', 'PA', '19101', 'Philadelphia', 39.9526, -75.1652, 'supercenter', 110000, '2013-04-18', 'open'),
('STR007', 'RTL006', 'Best Buy', '1357', '147 Birch Boulevard', 'San Antonio', 'TX', '78201', 'Bexar', 29.4241, -98.4936, 'supercenter', 45000, '2016-08-22', 'open'),
('STR008', 'RTL007', 'Costco Wholesale', '8024', '258 Spruce Way', 'San Diego', 'CA', '92101', 'San Diego', 32.7157, -117.1611, 'warehouse', 150000, '2010-12-03', 'open'),
('STR009', 'RTL008', 'CVS Pharmacy', '4680', '369 Willow Court', 'Dallas', 'TX', '75201', 'Dallas', 32.7767, -96.7970, 'neighborhood', 12000, '2017-02-14', 'open'),
('STR010', 'RTL009', 'Walgreens', '5791', '741 Ash Street', 'San Jose', 'CA', '95101', 'Santa Clara', 37.3382, -121.8863, 'neighborhood', 14000, '2018-05-30', 'open');

-- Insert Products (sample products across categories)
INSERT INTO products (product_id, sku, upc, product_name, brand, manufacturer, model_number, category, subcategory, product_description, weight_lbs, color, is_active) VALUES
('PRD001', 'SKU-001', '012345678901', '55" 4K Smart TV', 'Samsung', 'Samsung Electronics', 'UN55AU8000FXZA', 'Electronics', 'Televisions', '55-inch 4K UHD Smart TV with HDR', 35.5, 'Black', TRUE),
('PRD002', 'SKU-002', '012345678902', 'iPhone 15 Pro', 'Apple', 'Apple Inc.', 'A2848', 'Electronics', 'Smartphones', '6.1-inch iPhone 15 Pro with A17 Pro chip', 0.4, 'Natural Titanium', TRUE),
('PRD003', 'SKU-003', '012345678903', 'Nike Air Max 270', 'Nike', 'Nike Inc.', 'AH8050-100', 'Apparel', 'Footwear', 'Men''s running shoes with Air Max cushioning', 1.2, 'White/Black', TRUE),
('PRD004', 'SKU-004', '012345678904', 'KitchenAid Stand Mixer', 'KitchenAid', 'Whirlpool Corporation', 'KSM150PSER', 'Home & Kitchen', 'Small Appliances', '5-quart stand mixer with 10 speeds', 26.0, 'Empire Red', TRUE),
('PRD005', 'SKU-005', '012345678905', 'LEGO Star Wars Set', 'LEGO', 'LEGO Group', '75313', 'Toys & Games', 'Building Sets', 'AT-AT Walker building set with 1267 pieces', 4.8, 'Multi-color', TRUE),
('PRD006', 'SKU-006', '012345678906', 'Dyson V15 Detect', 'Dyson', 'Dyson Ltd', '394786-01', 'Home & Kitchen', 'Vacuum Cleaners', 'Cordless vacuum with laser technology', 7.8, 'Yellow/Nickel', TRUE),
('PRD007', 'SKU-007', '012345678907', 'Sony WH-1000XM5 Headphones', 'Sony', 'Sony Corporation', 'WH1000XM5', 'Electronics', 'Audio', 'Wireless noise-canceling headphones', 0.6, 'Black', TRUE),
('PRD008', 'SKU-008', '012345678908', 'Instant Pot Duo', 'Instant Pot', 'Instant Brands', 'DUO60', 'Home & Kitchen', 'Pressure Cookers', '6-quart 7-in-1 pressure cooker', 11.6, 'Stainless Steel', TRUE),
('PRD009', 'SKU-009', '012345678909', 'Nintendo Switch OLED', 'Nintendo', 'Nintendo Co Ltd', 'HEG-001', 'Electronics', 'Gaming Consoles', 'Nintendo Switch with OLED screen', 0.9, 'White', TRUE),
('PRD010', 'SKU-010', '012345678910', 'Yeti Tundra 45 Cooler', 'Yeti', 'Yeti Holdings', 'YETI-45', 'Outdoor', 'Coolers', '45-quart hard cooler with T-Rex lid latches', 23.0, 'Seafoam', TRUE);

-- Insert Product Inventory
INSERT INTO product_inventory (inventory_id, product_id, store_id, stock_level, stock_status, available_quantity, last_checked_at, data_source, confidence_score) VALUES
('INV001', 'PRD001', 'STR001', 15, 'in_stock', 15, CURRENT_TIMESTAMP, 'api', 95.0),
('INV002', 'PRD001', 'STR002', 8, 'low_stock', 8, CURRENT_TIMESTAMP, 'api', 95.0),
('INV003', 'PRD002', 'STR007', 25, 'in_stock', 25, CURRENT_TIMESTAMP, 'api', 98.0),
('INV004', 'PRD002', 'STR001', 0, 'out_of_stock', 0, CURRENT_TIMESTAMP, 'api', 95.0),
('INV005', 'PRD003', 'STR003', 42, 'in_stock', 42, CURRENT_TIMESTAMP, 'scraper', 90.0),
('INV006', 'PRD004', 'STR005', 12, 'in_stock', 12, CURRENT_TIMESTAMP, 'api', 92.0),
('INV007', 'PRD005', 'STR001', 30, 'in_stock', 30, CURRENT_TIMESTAMP, 'api', 95.0),
('INV008', 'PRD006', 'STR004', 5, 'low_stock', 5, CURRENT_TIMESTAMP, 'scraper', 88.0),
('INV009', 'PRD007', 'STR007', 18, 'in_stock', 18, CURRENT_TIMESTAMP, 'api', 98.0),
('INV010', 'PRD008', 'STR005', 20, 'in_stock', 20, CURRENT_TIMESTAMP, 'api', 92.0);

-- Insert Product Pricing
INSERT INTO product_pricing (pricing_id, product_id, retailer_id, store_id, current_price, original_price, sale_price, discount_percentage, price_effective_date, price_expiry_date, price_type, price_source, price_confidence_score, is_online_price) VALUES
('PRC001', 'PRD001', 'RTL001', 'STR001', 449.99, 599.99, 449.99, 25.00, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '7 days', 'sale', 'api', 95.0, FALSE),
('PRC002', 'PRD001', 'RTL002', 'STR003', 479.99, 599.99, 479.99, 20.00, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '5 days', 'sale', 'api', 95.0, FALSE),
('PRC003', 'PRD002', 'RTL003', NULL, 999.00, 999.00, NULL, 0.00, CURRENT_TIMESTAMP, NULL, 'regular', 'api', 99.0, TRUE),
('PRC004', 'PRD002', 'RTL006', 'STR007', 999.00, 999.00, NULL, 0.00, CURRENT_TIMESTAMP, NULL, 'regular', 'api', 98.0, FALSE),
('PRC005', 'PRD003', 'RTL002', 'STR003', 119.99, 150.00, 119.99, 20.00, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '10 days', 'sale', 'scraper', 90.0, FALSE),
('PRC006', 'PRD004', 'RTL004', 'STR005', 329.99, 379.99, 329.99, 13.16, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '14 days', 'sale', 'api', 92.0, FALSE),
('PRC007', 'PRD005', 'RTL001', 'STR001', 89.99, 89.99, NULL, 0.00, CURRENT_TIMESTAMP, NULL, 'regular', 'api', 95.0, FALSE),
('PRC008', 'PRD006', 'RTL002', 'STR004', 699.99, 749.99, 699.99, 6.67, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '3 days', 'sale', 'scraper', 88.0, FALSE),
('PRC009', 'PRD007', 'RTL006', 'STR007', 399.99, 399.99, NULL, 0.00, CURRENT_TIMESTAMP, NULL, 'regular', 'api', 98.0, FALSE),
('PRC010', 'PRD008', 'RTL003', NULL, 89.99, 99.99, 89.99, 10.00, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '7 days', 'sale', 'api', 99.0, TRUE);

-- Insert Deal Alerts
INSERT INTO deal_alerts (deal_id, product_id, retailer_id, store_id, deal_type, discount_percentage, discount_amount, deal_price, original_price, deal_start_date, deal_end_date, deal_status, deal_description, deal_source, is_online_deal) VALUES
('DEAL001', 'PRD001', 'RTL001', 'STR001', 'sale', 25.00, 150.00, 449.99, 599.99, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '7 days', 'active', '25% off Samsung 55" 4K Smart TV', 'api', FALSE),
('DEAL002', 'PRD003', 'RTL002', 'STR003', 'sale', 20.00, 30.01, 119.99, 150.00, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '10 days', 'active', '20% off Nike Air Max 270', 'scraper', FALSE),
('DEAL003', 'PRD008', 'RTL003', NULL, 'sale', 10.00, 10.00, 89.99, 99.99, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '7 days', 'active', '10% off Instant Pot Duo', 'api', TRUE),
('DEAL004', 'PRD004', 'RTL004', 'STR005', 'sale', 13.16, 50.00, 329.99, 379.99, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '14 days', 'active', 'Save $50 on KitchenAid Stand Mixer', 'api', FALSE),
('DEAL005', 'PRD006', 'RTL002', 'STR004', 'sale', 6.67, 50.00, 699.99, 749.99, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '3 days', 'active', 'Limited time: $50 off Dyson V15 Detect', 'scraper', FALSE);

-- Insert Census Retail Data (sample monthly data)
INSERT INTO census_retail_data (census_id, naics_code, industry_category, month, year, retail_sales_amount, inventory_amount, store_count, employment_count, sales_change_percent, inventory_change_percent, data_source) VALUES
('CNS001', '441110', 'New Car Dealers', 1, 2024, 125000.00, 45000.00, 16500, 1250000, 2.5, 1.2, 'CENSUS_MRTS'),
('CNS002', '442110', 'Furniture Stores', 1, 2024, 8500.00, 12000.00, 22000, 185000, -1.3, 0.8, 'CENSUS_MRTS'),
('CNS003', '443141', 'Household Appliance Stores', 1, 2024, 3200.00, 2800.00, 15000, 95000, 3.1, 2.5, 'CENSUS_MRTS'),
('CNS004', '451110', 'Sporting Goods Stores', 1, 2024, 4200.00, 5800.00, 18000, 120000, 1.8, 1.1, 'CENSUS_MRTS'),
('CNS005', '452210', 'Department Stores', 1, 2024, 18500.00, 32000.00, 8500, 650000, -0.5, -0.3, 'CENSUS_MRTS');

-- Insert BLS Price Data (sample CPI data)
INSERT INTO bls_price_data (bls_id, series_id, product_category, period, year, price_index_value, percent_change, percent_change_year_ago, base_period, index_type, data_source) VALUES
('BLS001', 'CUUR0000SA0', 'All Items', 'M01', 2024, 308.417, 0.3, 3.1, '1982-84=100', 'CPI_U', 'BLS_API'),
('BLS002', 'CUUR0000SETB01', 'Televisions', 'M01', 2024, 12.456, -2.1, -8.5, '1997=100', 'CPI_U', 'BLS_API'),
('BLS003', 'CUUR0000SEEE01', 'Smartphones', 'M01', 2024, 45.123, -1.2, -5.3, '1997=100', 'CPI_U', 'BLS_API'),
('BLS004', 'CUUR0000SEGA', 'Apparel', 'M01', 2024, 125.789, 0.5, 1.2, '1982-84=100', 'CPI_U', 'BLS_API'),
('BLS005', 'CUUR0000SEHF', 'Household Furnishings', 'M01', 2024, 98.234, 0.2, 0.8, '1982-84=100', 'CPI_U', 'BLS_API');

-- Insert Geographic Markets
INSERT INTO geographic_markets (market_id, market_name, market_type, market_code, population, median_income, market_size, state_code, county_name, data_source) VALUES
('MKT001', 'New York City', 'city', 'NYC', 8336817, 67240.00, 302.6, 'NY', 'New York', 'CENSUS'),
('MKT002', 'Los Angeles', 'city', 'LA', 3967000, 65000.00, 502.7, 'CA', 'Los Angeles', 'CENSUS'),
('MKT003', '10001', 'zip', '10001', 45000, 85000.00, 0.8, 'NY', 'New York', 'CENSUS'),
('MKT004', '90001', 'zip', '90001', 62000, 42000.00, 1.2, 'CA', 'Los Angeles', 'CENSUS'),
('MKT005', 'New York', 'state', 'NY', 20201249, 72000.00, 54555.0, 'NY', NULL, 'CENSUS');

-- Insert Data Sources
INSERT INTO data_sources (source_id, source_name, source_type, api_endpoint, api_key_required, rate_limit_per_hour, rate_limit_per_day, sync_frequency, data_quality_score, is_active) VALUES
('SRC001', 'Census Bureau MRTS API', 'api', 'http://api.census.gov/data/timeseries/eits/mrts', FALSE, 500, 5000, 'monthly', 98.0, TRUE),
('SRC002', 'BLS Public Data API', 'api', 'https://api.bls.gov/publicAPI/v2', FALSE, 500, 5000, 'monthly', 99.0, TRUE),
('SRC003', 'Data.gov CKAN API', 'api', 'https://catalog.data.gov/api/3/action', FALSE, 1000, 10000, 'daily', 95.0, TRUE),
('SRC004', 'Retailer Web Scraper', 'scraper', NULL, FALSE, 100, 1000, 'daily', 85.0, TRUE),
('SRC005', 'Manual Entry', 'manual', NULL, FALSE, NULL, NULL, 'manual', 100.0, TRUE);

-- Insert Pipeline Metadata (sample execution log)
INSERT INTO pipeline_metadata (pipeline_id, source_id, extraction_date, pipeline_type, records_processed, records_successful, records_failed, processing_duration_seconds, status, start_time, end_time) VALUES
('PIP001', 'SRC001', CURRENT_TIMESTAMP, 'full', 5000, 4950, 50, 120, 'success', CURRENT_TIMESTAMP - INTERVAL '2 minutes', CURRENT_TIMESTAMP),
('PIP002', 'SRC002', CURRENT_TIMESTAMP, 'full', 3000, 3000, 0, 45, 'success', CURRENT_TIMESTAMP - INTERVAL '1 minute', CURRENT_TIMESTAMP),
('PIP003', 'SRC004', CURRENT_TIMESTAMP, 'extract', 10000, 9800, 200, 300, 'partial', CURRENT_TIMESTAMP - INTERVAL '5 minutes', CURRENT_TIMESTAMP);
