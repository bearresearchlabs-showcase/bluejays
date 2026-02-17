-- Minimal sample data for Docker testing (db-16)
-- 5 rows per table

INSERT INTO fema_flood_zones (zone_id, zone_code, zone_description, base_flood_elevation, community_id, community_name, state_code, county_fips, effective_date, map_panel, source_file, source_crs, target_crs, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status) VALUES
('fz_000001', 'V', 'Flood Zone V', NULL, 'comm_0001', 'Community 1', 'HI', 'HI310', '2020-01-01', 'panel_0001', 'nfhl_HI.shp', 'EPSG:4326', 'EPSG:4326', -157.567282, 21.346660, -157.367282, 21.546660, 'Success'),
('fz_000002', 'VE', 'Flood Zone VE', 13.371811688505407, 'comm_0002', 'Community 2', 'ME', 'ME140', '2020-01-01', 'panel_0002', 'nfhl_ME.shp', 'EPSG:4326', 'EPSG:4326', -69.481482, 44.440874, -69.281482, 44.640874, 'Success'),
('fz_000003', 'AH', 'Flood Zone AH', NULL, 'comm_0003', 'Community 3', 'NJ', 'NJ090', '2020-01-01', 'panel_0003', 'nfhl_NJ.shp', 'EPSG:4326', 'EPSG:4326', -74.877060, 40.164414, -74.677060, 40.364414, 'Success'),
('fz_000004', 'D', 'Flood Zone D', NULL, 'comm_0004', 'Community 4', 'NY', 'NY872', '2020-01-01', 'panel_0004', 'nfhl_NY.shp', 'EPSG:4326', 'EPSG:4326', -73.932072, 40.474866, -73.732072, 40.674866, 'Success'),
('fz_000005', 'D', 'Flood Zone D', NULL, 'comm_0005', 'Community 5', 'WA', 'WA450', '2020-01-01', 'panel_0005', 'nfhl_WA.shp', 'EPSG:4326', 'EPSG:4326', -122.367959, 47.128432, -122.167959, 47.328432, 'Success');

INSERT INTO real_estate_properties (property_id, property_address, property_latitude, property_longitude, property_type, building_value, land_value, total_value, square_footage, year_built, number_of_floors, elevation_feet, state_code, county_fips, city_name, zip_code, portfolio_id, portfolio_name, acquisition_date) VALUES
('prop_000001', '1 Main St, Shreveport, LA 20351', 30.1048881, -90.7357575, 'Industrial', 5782298.10, 1807893.25, 7590191.36, 310036.56, 1931, 7, 145.32, 'LA', 'LA613', 'Shreveport', '85568', 'port_029', 'Portfolio 46', '2010-01-23'),
('prop_000002', '2 Main St, Orlando, FL 73801', 26.0790470, -80.0543963, 'Mixed-Use', 12812911.08, 4949425.81, 17762336.89, 34402.65, 1944, 18, 589.80, 'FL', 'FL114', 'Orlando', '40622', 'port_083', 'Portfolio 97', '2010-01-26'),
('prop_000003', '3 Main St, Virginia Beach, VA 14182', 37.0454432, -78.5636096, 'Residential', 2246133.77, 999495.97, 3245629.75, 3692.60, 1972, 1, 388.74, 'VA', 'VA875', 'Virginia Beach', '76130', 'port_087', 'Portfolio 60', '2023-07-27'),
('prop_000004', '4 Main St, Greensboro, NC 21018', 35.0693517, -78.5114521, 'Mixed-Use', 8204229.76, 2734885.78, 10939115.54, 74366.53, 1988, 8, 552.70, 'NC', 'NC815', 'Greensboro', '19838', 'port_027', 'Portfolio 69', '2016-06-09'),
('prop_000005', '5 Main St, Shreveport, LA 46869', 30.2871523, -91.1960433, 'Industrial', 30723291.87, 8867207.11, 39590498.98, 379234.42, 1988, 5, 10.23, 'LA', 'LA490', 'Shreveport', '58625', 'port_015', 'Portfolio 2', '2020-05-31');

INSERT INTO noaa_sea_level_rise (projection_id, station_id, station_name, station_latitude, station_longitude, projection_year, scenario, sea_level_rise_feet, confidence_level, high_tide_flooding_days, data_source) VALUES
('slr_000001', '8761724', 'New Orleans, LA', 29.9333000, -90.0667000, 2070, 'Low', 20.791, 'Low', 1041, 'NOAA_CO-OPS'),
('slr_000002', '8665530', 'Charleston, SC', 32.7817000, -79.9247000, 2050, 'High', 61.583, 'Low', 3087, 'NOAA_CO-OPS'),
('slr_000003', '8761724', 'New Orleans, LA', 29.9333000, -90.0667000, 2070, 'Intermediate-High', 51.805, 'High', 2595, 'NOAA_CO-OPS'),
('slr_000004', '8724580', 'Miami Beach', 25.7617000, -80.1318000, 2070, 'Intermediate-High', 51.812, 'High', 2593, 'NOAA_CO-OPS'),
('slr_000005', '8724580', 'Miami Beach', 25.7617000, -80.1318000, 2100, 'Intermediate', 41.902, 'High', 2101, 'NOAA_CO-OPS');

INSERT INTO usgs_streamflow_observations (observation_id, gauge_id, observation_time, gage_height_feet, discharge_cfs, stage_feet, flood_category, percentile_rank, data_quality_code) VALUES
('obs_usgs_0000001', '4617679', '2023-07-14 11:00:00', 8.73, 42782.71, 8.73, 'Minor', 84.88, 'A'),
('obs_usgs_0000002', '2972934', '2021-11-14 05:00:00', 13.39, 353290.85, 13.39, 'Moderate', 93.03, 'A'),
('obs_usgs_0000003', '5480036', '2023-04-08 04:00:00', 3.07, 5762.26, 3.07, 'None', 54.93, 'A'),
('obs_usgs_0000004', '8621051', '2024-03-11 19:00:00', 10.93, 272725.69, 10.93, 'Moderate', 96.50, 'A'),
('obs_usgs_0000005', '1834115', '2023-12-09 10:00:00', 6.52, 84183.49, 6.52, 'Moderate', 75.90, 'A');

INSERT INTO nasa_flood_models (model_id, model_name, forecast_time, grid_cell_latitude, grid_cell_longitude, inundation_depth_feet, flood_probability, flood_severity, model_resolution_meters, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, source_file) VALUES
('nasa_0000001', 'VIIRS', '2023-02-24 19:00:00', 38.0080088, -88.4355126, 0.36, 3.81, 'Low', 1000, -88.445513, 37.998009, -88.425513, 38.018009, 'viirs_20230224_1900.nc'),
('nasa_0000002', 'LIS', '2022-02-09 18:00:00', 31.2551491, -76.7794191, 5.45, 97.88, 'Extreme', 250, -76.789419, 31.245149, -76.769419, 31.265149, 'lis_20220209_1800.nc'),
('nasa_0000003', 'GFMS', '2020-06-25 12:00:00', 35.4157284, -93.6902661, 0.83, 44.70, 'Low', 1000, -93.700266, 35.405728, -93.680266, 35.425728, 'gfms_20200625_1200.nc'),
('nasa_0000004', 'LIS', '2021-10-20 20:00:00', 45.7706763, -85.6783887, 4.14, 65.25, 'Moderate', 500, -85.688389, 45.760676, -85.668389, 45.780676, 'lis_20211020_2000.nc'),
('nasa_0000005', 'VIIRS', '2024-08-11 02:00:00', 31.3911294, -124.3788953, 5.65, 92.32, 'High', 500, -124.388895, 31.381129, -124.368895, 31.401129, 'viirs_20240811_0200.nc');

INSERT INTO flood_risk_assessments (assessment_id, property_id, assessment_date, assessment_type, time_horizon_years, fema_zone_code, fema_zone_id, base_flood_elevation_feet, flood_zone_risk_score, sea_level_rise_feet, sea_level_rise_scenario, high_tide_flooding_days, sea_level_risk_score, nearest_gauge_id, historical_flood_frequency, flood_probability_percent, streamflow_risk_score, nasa_model_flood_probability, nasa_model_severity, nasa_model_risk_score, overall_risk_score, risk_category, vulnerability_score, exposure_score, estimated_damage_dollars, estimated_annual_loss, insurance_premium_estimate, assessment_methodology, data_sources_used, confidence_level) VALUES
('assess_000001', 'prop_000001', '2022-10-29', '30-Year Projection', 30, 'X', 'fz_000001', NULL, 15.00, 0.550, 'Intermediate', 167, 11.01, '4617679', 43, 13.13, 54.40, 67.93, 'High', 50.12, 28.71, 'Low', 25.84, 24.40, 688522.84, 44941.76, 24142.37, 'Multi-Factor Risk Assessment', 'FEMA NFHL, NOAA SLR, USGS Streamflow, NASA Models', 'High'),
('assess_000002', 'prop_000002', '2023-05-11', 'Current', 0, 'V', 'fz_000002', NULL, 15.00, NULL, NULL, NULL, NULL, '2972934', 30, 12.87, 37.18, 35.97, 'Moderate', 67.82, 37.50, 'Moderate', 33.75, 31.87, 293639.33, 20915.28, 4729.88, 'Multi-Factor Risk Assessment', 'FEMA NFHL, NOAA SLR, USGS Streamflow, NASA Models', 'High'),
('assess_000003', 'prop_000003', '2025-02-18', '5-Year Projection', 5, 'V', 'fz_000003', NULL, 15.00, 0.083, 'Intermediate', 159, 1.67, '5480036', 29, 13.23, 47.69, 15.41, 'High', 47.66, 24.07, 'Low', 21.66, 20.46, 182897.95, 14719.59, 7164.70, 'Multi-Factor Risk Assessment', 'FEMA NFHL, NOAA SLR, USGS Streamflow, NASA Models', 'High'),
('assess_000004', 'prop_000004', '2020-09-24', '20-Year Projection', 20, 'AE', 'fz_000004', 13.64, 70.00, 0.447, 'High', 65, 8.94, '8621051', 50, 11.95, 37.52, 45.80, 'High', 52.99, 41.78, 'Moderate', 37.61, 35.52, 2207067.98, 285073.85, 27383.76, 'Multi-Factor Risk Assessment', 'FEMA NFHL, NOAA SLR, USGS Streamflow, NASA Models', 'High'),
('assess_000005', 'prop_000005', '2025-01-22', '50-Year Projection', 50, 'AH', 'fz_000005', NULL, 15.00, 1.055, 'Intermediate-High', 77, 21.10, '1834115', 17, 6.66, 20.85, 17.83, 'Moderate', 61.43, 27.28, 'Low', 24.56, 23.19, 273568.32, 29084.64, 11908.25, 'Multi-Factor Risk Assessment', 'FEMA NFHL, NOAA SLR, USGS Streamflow, NASA Models', 'High');

INSERT INTO property_flood_zone_intersections (intersection_id, property_id, zone_id, intersection_type, distance_to_zone_feet, elevation_difference_feet) VALUES
('int_0000001', 'prop_000001', 'fz_000001', 'Within', 0.00, 19.52),
('int_0000002', 'prop_000002', 'fz_000002', 'Within', 0.00, 17.62),
('int_0000003', 'prop_000003', 'fz_000003', 'Near', 343.08, 13.99),
('int_0000004', 'prop_000004', 'fz_000004', 'Near', 710.68, 13.89),
('int_0000005', 'prop_000005', 'fz_000005', 'Within', 0.00, 16.88);

-- Populate geography columns from lat/lon for spatial queries
UPDATE real_estate_properties SET property_geom = ST_SetSRID(ST_MakePoint(property_longitude, property_latitude), 4326)::geography WHERE property_geom IS NULL;
UPDATE fema_flood_zones SET zone_geom = ST_MakeEnvelope(spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, 4326)::geography WHERE zone_geom IS NULL AND spatial_extent_west IS NOT NULL;
UPDATE noaa_sea_level_rise SET station_geom = ST_SetSRID(ST_MakePoint(station_longitude, station_latitude), 4326)::geography WHERE station_geom IS NULL;
UPDATE nasa_flood_models SET grid_cell_geom = ST_SetSRID(ST_MakePoint(grid_cell_longitude, grid_cell_latitude), 4326)::geography WHERE grid_cell_geom IS NULL;

-- Insert usgs_streamflow_gauges for gauge_ids referenced in observations (Query 5 needs this)
INSERT INTO usgs_streamflow_gauges (gauge_id, gauge_name, gauge_latitude, gauge_longitude, gauge_geom, flood_stage_feet, moderate_flood_stage_feet, major_flood_stage_feet, active_status)
SELECT DISTINCT uso.gauge_id, 'Gauge ' || uso.gauge_id, 35.0, -90.0, ST_SetSRID(ST_MakePoint(-90.0, 35.0), 4326)::geography, 10.0, 15.0, 20.0, true
FROM usgs_streamflow_observations uso
ON CONFLICT (gauge_id) DO NOTHING;

-- Minimal historical_flood_events for Query 3 (temporal/geographic analysis)
INSERT INTO historical_flood_events (event_id, event_name, event_type, start_date, end_date, peak_discharge_cfs, peak_stage_feet, total_damage_dollars, fatalities, properties_affected, state_code, county_fips, data_source) VALUES
('evt_000001', 'Louisiana Flood 2020', 'Riverine', '2020-08-15', '2020-08-18', 125000.0, 12.5, 2500000.0, 0, 150, 'LA', 'LA613', 'USGS'),
('evt_000002', 'Florida Coastal 2021', 'Storm Surge', '2021-09-01', '2021-09-03', NULL, 8.2, 1800000.0, 0, 89, 'FL', 'FL114', 'NOAA'),
('evt_000003', 'Virginia Riverine 2022', 'Flash', '2022-07-12', '2022-07-13', 45000.0, 9.1, 850000.0, 0, 42, 'VA', 'VA875', 'USGS');

-- Minimal portfolio_risk_summaries for Query 2
INSERT INTO portfolio_risk_summaries (summary_id, portfolio_id, portfolio_name, summary_date, total_properties, properties_at_risk, high_risk_properties, moderate_risk_properties, low_risk_properties, average_risk_score, total_property_value, at_risk_property_value, estimated_annual_loss, portfolio_risk_category) VALUES
('sum_000001', 'port_029', 'Portfolio 46', '2024-01-15', 5, 2, 1, 1, 2, 45.50, 50000000.0, 15000000.0, 250000.0, 'Moderate');
