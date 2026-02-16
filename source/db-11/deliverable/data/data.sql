-- Sample Data for Parking Intelligence Database
-- Compatible with PostgreSQL
-- Production sample data for parking intelligence system

-- Insert sample metropolitan areas
INSERT INTO metropolitan_areas (msa_id, msa_name, msa_type, state_codes, principal_city, population_estimate, land_area_sq_miles, population_density, median_household_income, gdp_billions, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, data_year) VALUES
('msa_001', 'New York-Newark-Jersey City', 'MSA', 'NY,NJ,PA', 'New York', 20153634, 6718.0, 3000.0, 72000.0, 1900.0, -74.5, 40.4, -73.5, 41.0, 2024),
('msa_002', 'Los Angeles-Long Beach-Anaheim', 'MSA', 'CA', 'Los Angeles', 13214799, 4851.0, 2724.0, 71000.0, 1200.0, -118.8, 33.7, -117.5, 34.5, 2024),
('msa_003', 'Chicago-Naperville-Elgin', 'MSA', 'IL,IN,WI', 'Chicago', 9618502, 10874.0, 884.0, 68000.0, 800.0, -88.2, 41.5, -87.3, 42.1, 2024),
('msa_004', 'Dallas-Fort Worth-Arlington', 'MSA', 'TX', 'Dallas', 7614773, 9178.0, 830.0, 65000.0, 600.0, -97.5, 32.5, -96.5, 33.2, 2024),
('msa_005', 'San Francisco-Oakland-Berkeley', 'MSA', 'CA', 'San Francisco', 4700000, 2851.0, 1648.0, 105000.0, 700.0, -122.6, 37.3, -121.8, 38.0, 2024);

-- Insert sample cities
INSERT INTO cities (city_id, city_name, state_code, county_name, msa_id, population, land_area_sq_miles, population_density, median_household_income, median_age, employment_total, unemployment_rate, city_latitude, city_longitude, timezone, data_year) VALUES
('city_001', 'New York', 'NY', 'New York', 'msa_001', 8336817, 302.6, 27550.0, 72000.0, 36.5, 4200000, 5.2, 40.7128, -74.0060, 'America/New_York', 2024),
('city_002', 'Los Angeles', 'CA', 'Los Angeles', 'msa_002', 3898747, 468.7, 8320.0, 71000.0, 35.8, 1900000, 5.8, 34.0522, -118.2437, 'America/Los_Angeles', 2024),
('city_003', 'Chicago', 'IL', 'Cook', 'msa_003', 2693976, 227.6, 11830.0, 68000.0, 34.9, 1300000, 4.8, 41.8781, -87.6298, 'America/Chicago', 2024),
('city_004', 'Dallas', 'TX', 'Dallas', 'msa_004', 1343573, 385.8, 3482.0, 65000.0, 33.2, 700000, 4.2, 32.7767, -96.7970, 'America/Chicago', 2024),
('city_005', 'San Francisco', 'CA', 'San Francisco', 'msa_005', 873965, 46.9, 18635.0, 105000.0, 38.2, 500000, 3.5, 37.7749, -122.4194, 'America/Los_Angeles', 2024);

-- Insert sample airports
INSERT INTO airports (airport_id, airport_name, city_id, state_code, airport_type, latitude, longitude, annual_passengers, annual_cargo_tons, parking_spaces_total, parking_facilities_count, valet_available, long_term_parking, short_term_parking, data_year) VALUES
('JFK', 'John F. Kennedy International', 'city_001', 'NY', 'Commercial', 40.6413, -73.7781, 62000000, 1500000, 15000, 8, TRUE, TRUE, TRUE, 2024),
('LAX', 'Los Angeles International', 'city_002', 'CA', 'Commercial', 33.9416, -118.4085, 88000000, 2100000, 18000, 10, TRUE, TRUE, TRUE, 2024),
('ORD', 'Chicago O''Hare International', 'city_003', 'IL', 'Commercial', 41.9742, -87.9073, 83000000, 1800000, 20000, 12, TRUE, TRUE, TRUE, 2024),
('DFW', 'Dallas/Fort Worth International', 'city_004', 'TX', 'Commercial', 32.8998, -97.0403, 73000000, 800000, 25000, 15, TRUE, TRUE, TRUE, 2024),
('SFO', 'San Francisco International', 'city_005', 'CA', 'Commercial', 37.6213, -122.3790, 55000000, 500000, 12000, 7, TRUE, TRUE, TRUE, 2024);

-- Insert sample stadiums/venues
INSERT INTO stadiums_venues (venue_id, venue_name, venue_type, city_id, latitude, longitude, capacity, parking_spaces_total, parking_facilities_count, primary_sport, team_name, annual_events_count, peak_attendance, data_year) VALUES
('venue_001', 'Yankee Stadium', 'Stadium', 'city_001', 40.8296, -73.9262, 54251, 8000, 5, 'MLB', 'New York Yankees', 81, 54251, 2024),
('venue_002', 'Madison Square Garden', 'Arena', 'city_001', 40.7505, -73.9934, 19812, 5000, 3, 'NBA', 'New York Knicks', 200, 19812, 2024),
('venue_003', 'Staples Center', 'Arena', 'city_002', 34.0430, -118.2673, 19060, 6000, 4, 'NBA', 'Los Angeles Lakers', 180, 19060, 2024),
('venue_004', 'Soldier Field', 'Stadium', 'city_003', 41.8625, -87.6167, 61500, 10000, 6, 'NFL', 'Chicago Bears', 10, 61500, 2024),
('venue_005', 'AT&T Stadium', 'Stadium', 'city_004', 32.7473, -97.0945, 80000, 12000, 8, 'NFL', 'Dallas Cowboys', 10, 80000, 2024);

-- Insert sample parking facilities
INSERT INTO parking_facilities (facility_id, facility_name, facility_type, city_id, latitude, longitude, total_spaces, accessible_spaces, ev_charging_stations, covered_spaces, uncovered_spaces, operator_name, operator_type, is_event_parking, is_monthly_parking, is_hourly_parking, accepts_reservations, payment_methods, amenities) VALUES
('facility_001', 'Downtown Garage A', 'Garage', 'city_001', 40.7128, -74.0060, 500, 25, 10, 500, 0, 'City Parking Authority', 'Municipal', FALSE, TRUE, TRUE, TRUE, 'Credit,Mobile,App', 'Security,Lighting,Elevator'),
('facility_002', 'Airport Long-Term Lot', 'Surface Lot', 'city_001', 40.6413, -73.7781, 3000, 150, 50, 0, 3000, 'JFK Parking', 'Airport', FALSE, FALSE, TRUE, TRUE, 'Credit,Mobile,App', 'Shuttle Service,24/7 Access'),
('facility_003', 'Stadium Event Parking', 'Surface Lot', 'city_001', 40.8296, -73.9262, 2000, 100, 20, 0, 2000, 'Yankee Stadium Parking', 'Venue', TRUE, FALSE, TRUE, TRUE, 'Credit,Cash,Mobile', 'Event Shuttle'),
('facility_004', 'Business District Garage', 'Garage', 'city_002', 34.0522, -118.2437, 800, 40, 15, 800, 0, 'LA Parking Co', 'Private', FALSE, TRUE, TRUE, TRUE, 'Credit,Mobile,App', 'Valet,Car Wash'),
('facility_005', 'Convention Center Parking', 'Structure', 'city_003', 41.8781, -87.6298, 1200, 60, 25, 1200, 0, 'Chicago Parking', 'Municipal', TRUE, FALSE, TRUE, TRUE, 'Credit,Mobile', 'Convention Shuttle');

-- Insert sample parking pricing
INSERT INTO parking_pricing (pricing_id, facility_id, pricing_type, base_rate_hourly, base_rate_daily, base_rate_monthly, max_daily_rate, currency, effective_date, expiration_date, day_of_week, is_active) VALUES
('price_001', 'facility_001', 'Hourly', 3.50, 25.00, 350.00, 25.00, 'USD', '2024-01-01', '2024-12-31', 'All', TRUE),
('price_002', 'facility_001', 'Monthly', NULL, NULL, 350.00, NULL, 'USD', '2024-01-01', '2024-12-31', 'All', TRUE),
('price_003', 'facility_002', 'Daily', NULL, 18.00, NULL, 18.00, 'USD', '2024-01-01', '2024-12-31', 'All', TRUE),
('price_004', 'facility_003', 'Event', NULL, NULL, NULL, 40.00, 'USD', '2024-01-01', '2024-12-31', 'All', TRUE),
('price_005', 'facility_004', 'Hourly', 4.00, 30.00, 450.00, 30.00, 'USD', '2024-01-01', '2024-12-31', 'All', TRUE);

-- Insert sample parking utilization
INSERT INTO parking_utilization (utilization_id, facility_id, utilization_date, utilization_hour, occupancy_rate, spaces_occupied, spaces_available, revenue_generated, reservation_count, walk_in_count, data_source) VALUES
('util_001', 'facility_001', '2024-02-01', 9, 85.0, 425, 75, 1487.50, 200, 225, 'Sensor'),
('util_002', 'facility_001', '2024-02-01', 12, 95.0, 475, 25, 1662.50, 300, 175, 'Sensor'),
('util_003', 'facility_001', '2024-02-01', 18, 70.0, 350, 150, 1225.00, 150, 200, 'Sensor'),
('util_004', 'facility_002', '2024-02-01', 10, 60.0, 1800, 1200, 3240.00, 800, 1000, 'App'),
('util_005', 'facility_003', '2024-02-01', 19, 100.0, 2000, 0, 8000.00, 1500, 500, 'Manual');

-- Insert sample traffic volume data
INSERT INTO traffic_volume_data (traffic_id, location_id, city_id, latitude, longitude, road_name, road_type, annual_average_daily_traffic, peak_hour_volume, direction, data_year, data_month) VALUES
('traffic_001', 'loc_001', 'city_001', 40.7128, -74.0060, 'Broadway', 'Arterial', 45000, 3500, 'Both', 2024, 2),
('traffic_002', 'loc_002', 'city_002', 34.0522, -118.2437, 'Wilshire Blvd', 'Arterial', 38000, 2800, 'Both', 2024, 2),
('traffic_003', 'loc_003', 'city_003', 41.8781, -87.6298, 'Michigan Ave', 'Arterial', 42000, 3200, 'Both', 2024, 2),
('traffic_004', 'loc_004', 'city_004', 32.7767, -96.7970, 'I-35E', 'Highway', 120000, 8500, 'Both', 2024, 2),
('traffic_005', 'loc_005', 'city_005', 37.7749, -122.4194, 'Market St', 'Arterial', 35000, 2600, 'Both', 2024, 2);

-- Insert sample events
INSERT INTO events (event_id, event_name, event_type, venue_id, city_id, event_date, event_time, attendance, parking_demand_multiplier, is_recurring, recurrence_pattern) VALUES
('event_001', 'Yankees vs Red Sox', 'Sports', 'venue_001', 'city_001', '2024-04-15', '19:00:00', 50000, 0.85, TRUE, 'Seasonal'),
('event_002', 'Knicks vs Lakers', 'Sports', 'venue_002', 'city_001', '2024-03-20', '20:00:00', 19000, 0.90, FALSE, NULL),
('event_003', 'Concert: Taylor Swift', 'Concert', 'venue_003', 'city_002', '2024-05-10', '20:00:00', 19000, 1.20, FALSE, NULL),
('event_004', 'Bears vs Packers', 'Sports', 'venue_004', 'city_003', '2024-09-15', '13:00:00', 60000, 0.95, TRUE, 'Seasonal'),
('event_005', 'Cowboys vs Eagles', 'Sports', 'venue_005', 'city_004', '2024-10-20', '16:00:00', 80000, 1.00, TRUE, 'Seasonal');

-- Insert sample business districts
INSERT INTO business_districts (district_id, district_name, city_id, district_type, latitude, longitude, employment_total, businesses_count, parking_demand_score, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, data_year) VALUES
('district_001', 'Manhattan Financial District', 'city_001', 'Financial', 40.7074, -74.0113, 500000, 5000, 95.0, -74.02, 40.70, -74.00, 40.72, 2024),
('district_002', 'Downtown LA', 'city_002', 'Downtown', 34.0522, -118.2437, 250000, 3000, 85.0, -118.25, 34.05, -118.24, 34.06, 2024),
('district_003', 'Chicago Loop', 'city_003', 'Financial', 41.8781, -87.6298, 300000, 4000, 90.0, -87.64, 41.87, -87.62, 41.89, 2024),
('district_004', 'Dallas Uptown', 'city_004', 'Retail', 32.8009, -96.8027, 150000, 2000, 75.0, -96.81, 32.80, -96.79, 32.81, 2024),
('district_005', 'SF Financial District', 'city_005', 'Financial', 37.7946, -122.3998, 200000, 2500, 88.0, -122.41, 37.79, -122.39, 37.80, 2024);

-- Insert sample facility-district mappings
INSERT INTO facility_district_mapping (mapping_id, facility_id, district_id, distance_miles, is_primary_district) VALUES
('mapping_001', 'facility_001', 'district_001', 0.2, TRUE),
('mapping_002', 'facility_004', 'district_002', 0.3, TRUE),
('mapping_003', 'facility_005', 'district_003', 0.1, TRUE);

-- Insert sample market intelligence metrics
INSERT INTO market_intelligence_metrics (metric_id, city_id, msa_id, metric_type, metric_name, metric_value, metric_unit, calculation_date, time_period, data_year, data_month) VALUES
('metric_001', 'city_001', 'msa_001', 'Demand', 'Average Occupancy Rate', 82.5, 'Percentage', '2024-02-01', 'Monthly', 2024, 2),
('metric_002', 'city_001', 'msa_001', 'Revenue', 'Total Monthly Revenue', 1250000.00, 'USD', '2024-02-01', 'Monthly', 2024, 2),
('metric_003', 'city_002', 'msa_002', 'Supply', 'Total Parking Spaces', 50000, 'Spaces', '2024-02-01', 'Monthly', 2024, 2),
('metric_004', 'city_003', 'msa_003', 'Utilization', 'Peak Hour Utilization', 95.0, 'Percentage', '2024-02-01', 'Monthly', 2024, 2),
('metric_005', 'city_004', 'msa_004', 'Competition', 'Average Competitor Rate', 3.75, 'USD', '2024-02-01', 'Monthly', 2024, 2);

-- Insert sample data source metadata
INSERT INTO data_source_metadata (source_id, source_name, source_type, source_url, api_endpoint, extraction_date, extraction_timestamp, records_extracted, data_quality_score, completeness_pct, error_count) VALUES
('source_001', 'Data.gov CKAN API', 'API', 'https://catalog.data.gov/api/3/action', '/package_search', '2024-02-01', '2024-02-01 10:00:00', 5000, 95.0, 98.5, 75),
('source_002', 'Census Bureau API', 'API', 'https://api.census.gov/data', '/2023/acs/acs5', '2024-02-01', '2024-02-01 11:00:00', 400, 98.0, 100.0, 8),
('source_003', 'BTS TranStats', 'CSV', 'https://www.transtats.bts.gov', NULL, '2024-02-01', '2024-02-01 12:00:00', 500, 92.0, 95.0, 40),
('source_004', 'City Open Data Portal', 'API', 'https://data.seattle.gov', '/api/views', '2024-02-01', '2024-02-01 13:00:00', 2000, 90.0, 97.0, 200),
('source_005', 'FHWA Traffic Data', 'CSV', 'https://www.fhwa.dot.gov', NULL, '2024-02-01', '2024-02-01 14:00:00', 1000, 88.0, 94.0, 120);
