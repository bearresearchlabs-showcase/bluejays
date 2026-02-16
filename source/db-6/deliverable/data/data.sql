-- Sample Data for Weather Data Pipeline Database
-- Compatible with PostgreSQL
-- Production sample data for weather data pipeline system

-- Insert sample CRS transformation parameters
INSERT INTO crs_transformation_parameters (transformation_id, source_crs, target_crs, source_crs_name, target_crs_name, transformation_method, units, accuracy_meters, usage_count) VALUES
('tran_001', 'EPSG:4326', 'EPSG:3857', 'WGS84 Geographic', 'Web Mercator', 'GDAL', 'meters', 0.5, 150),
('tran_002', 'EPSG:2227', 'EPSG:4326', 'California State Plane Zone 5', 'WGS84 Geographic', 'PROJ', 'degrees', 1.2, 85),
('tran_003', 'EPSG:4326', 'EPSG:4326', 'WGS84 Geographic', 'WGS84 Geographic', 'GDAL', 'degrees', 0.0, 200);

-- Insert sample shapefile boundaries (CWA - County Warning Areas)
INSERT INTO shapefile_boundaries (boundary_id, feature_type, feature_name, feature_identifier, source_shapefile, source_crs, target_crs, feature_count, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status, state_code, office_code) VALUES
('cwa_001', 'CWA', 'New York City', 'OKX', 'w_18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -74.5, 40.4, -73.5, 41.0, 'Success', 'NY', 'OKX'),
('cwa_002', 'CWA', 'Los Angeles', 'LOX', 'w_18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -118.8, 33.7, -117.5, 34.5, 'Success', 'CA', 'LOX'),
('cwa_003', 'CWA', 'Chicago', 'LOT', 'w_18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -88.2, 41.5, -87.3, 42.1, 'Success', 'IL', 'LOT'),
('cwa_004', 'CWA', 'Miami', 'MFL', 'w_18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -80.5, 25.3, -79.8, 26.2, 'Success', 'FL', 'MFL'),
('cwa_005', 'CWA', 'Seattle', 'SEW', 'w_18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -122.6, 47.3, -121.8, 47.8, 'Success', 'WA', 'SEW');

-- Insert sample shapefile boundaries (Fire Zones)
INSERT INTO shapefile_boundaries (boundary_id, feature_type, feature_name, feature_identifier, source_shapefile, source_crs, target_crs, feature_count, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status, state_code) VALUES
('fz_001', 'FireZone', 'Southern California Fire Zone 1', 'CAZ241', 'fz18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -118.5, 33.8, -117.2, 34.2, 'Success', 'CA'),
('fz_002', 'FireZone', 'Arizona Fire Zone 5', 'AZZ005', 'fz18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -112.2, 33.2, -111.5, 33.8, 'Success', 'AZ'),
('fz_003', 'FireZone', 'Colorado Fire Zone 12', 'COZ012', 'fz18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -105.1, 39.5, -104.5, 40.0, 'Success', 'CO');

-- Insert sample shapefile boundaries (Marine Zones)
INSERT INTO shapefile_boundaries (boundary_id, feature_type, feature_name, feature_identifier, source_shapefile, source_crs, target_crs, feature_count, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status, state_code) VALUES
('mz_001', 'MarineZone', 'New York Harbor', 'ANZ330', 'mz18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -74.2, 40.5, -73.8, 40.8, 'Success', 'NY'),
('mz_002', 'MarineZone', 'San Francisco Bay', 'PZZ530', 'mz18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -122.6, 37.6, -122.2, 37.9, 'Success', 'CA'),
('mz_003', 'MarineZone', 'Puget Sound', 'PZZ131', 'mz18mr25.shp', 'EPSG:4326', 'EPSG:4326', 1, -122.8, 47.4, -122.2, 47.8, 'Success', 'WA');

-- Insert sample weather stations
INSERT INTO weather_stations (station_id, station_name, station_latitude, station_longitude, elevation_meters, state_code, county_name, cwa_code, station_type, active_status, first_observation_date, last_observation_date, update_frequency_minutes) VALUES
('KNYC', 'New York Central Park', 40.785, -73.969, 40.0, 'NY', 'New York', 'OKX', 'ASOS', TRUE, '2020-01-01', '2026-02-03', 5),
('KLAX', 'Los Angeles International', 33.942, -118.408, 38.0, 'CA', 'Los Angeles', 'LOX', 'ASOS', TRUE, '2020-01-01', '2026-02-03', 5),
('KORD', 'Chicago O''Hare', 41.979, -87.907, 203.0, 'IL', 'Cook', 'LOT', 'ASOS', TRUE, '2020-01-01', '2026-02-03', 5),
('KMIA', 'Miami International', 25.795, -80.290, 2.0, 'FL', 'Miami-Dade', 'MFL', 'ASOS', TRUE, '2020-01-01', '2026-02-03', 5),
('KSEA', 'Seattle-Tacoma', 47.449, -122.309, 137.0, 'WA', 'King', 'SEW', 'ASOS', TRUE, '2020-01-01', '2026-02-03', 5);

-- Insert sample GRIB2 forecasts (temperature)
INSERT INTO grib2_forecasts (forecast_id, parameter_name, forecast_time, grid_cell_latitude, grid_cell_longitude, parameter_value, source_file, source_crs, target_crs, grid_resolution_x, grid_resolution_y, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status) VALUES
('grib_temp_001', 'Temperature', '2026-02-03 12:00:00', 40.785, -73.969, 45.5, 'ds.temp.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_temp_002', 'Temperature', '2026-02-03 12:00:00', 33.942, -118.408, 72.3, 'ds.temp.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_temp_003', 'Temperature', '2026-02-03 12:00:00', 41.979, -87.907, 38.2, 'ds.temp.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_temp_004', 'Temperature', '2026-02-03 12:00:00', 25.795, -80.290, 78.9, 'ds.temp.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_temp_005', 'Temperature', '2026-02-03 12:00:00', 47.449, -122.309, 52.1, 'ds.temp.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success');

-- Insert sample GRIB2 forecasts (precipitation)
INSERT INTO grib2_forecasts (forecast_id, parameter_name, forecast_time, grid_cell_latitude, grid_cell_longitude, parameter_value, source_file, source_crs, target_crs, grid_resolution_x, grid_resolution_y, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status) VALUES
('grib_qpf_001', 'Precipitation', '2026-02-03 12:00:00', 40.785, -73.969, 0.15, 'ds.qpf.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_qpf_002', 'Precipitation', '2026-02-03 12:00:00', 33.942, -118.408, 0.0, 'ds.qpf.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_qpf_003', 'Precipitation', '2026-02-03 12:00:00', 41.979, -87.907, 0.08, 'ds.qpf.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_qpf_004', 'Precipitation', '2026-02-03 12:00:00', 25.795, -80.290, 0.25, 'ds.qpf.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_qpf_005', 'Precipitation', '2026-02-03 12:00:00', 47.449, -122.309, 0.12, 'ds.qpf.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success');

-- Insert sample GRIB2 forecasts (wind speed)
INSERT INTO grib2_forecasts (forecast_id, parameter_name, forecast_time, grid_cell_latitude, grid_cell_longitude, parameter_value, source_file, source_crs, target_crs, grid_resolution_x, grid_resolution_y, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status) VALUES
('grib_wspd_001', 'WindSpeed', '2026-02-03 12:00:00', 40.785, -73.969, 12.5, 'ds.wspd.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_wspd_002', 'WindSpeed', '2026-02-03 12:00:00', 33.942, -118.408, 8.3, 'ds.wspd.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_wspd_003', 'WindSpeed', '2026-02-03 12:00:00', 41.979, -87.907, 15.2, 'ds.wspd.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_wspd_004', 'WindSpeed', '2026-02-03 12:00:00', 25.795, -80.290, 10.7, 'ds.wspd.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success'),
('grib_wspd_005', 'WindSpeed', '2026-02-03 12:00:00', 47.449, -122.309, 18.4, 'ds.wspd.bin', 'EPSG:4326', 'EPSG:3857', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success');

-- Insert sample weather observations
INSERT INTO weather_observations (observation_id, station_id, station_name, observation_time, station_latitude, station_longitude, temperature, dewpoint, humidity, wind_speed, wind_direction, pressure, visibility, sky_cover, precipitation_amount, data_freshness_minutes, data_source) VALUES
('obs_001', 'KNYC', 'New York Central Park', '2026-02-03 12:00:00', 40.785, -73.969, 45.2, 42.1, 88.5, 12.3, 270, 1013.2, 10.0, 'Overcast', 0.15, 5, 'NWS_API'),
('obs_002', 'KLAX', 'Los Angeles International', '2026-02-03 12:00:00', 33.942, -118.408, 72.1, 65.3, 78.2, 8.1, 180, 1015.8, 10.0, 'Clear', 0.0, 5, 'NWS_API'),
('obs_003', 'KORD', 'Chicago O''Hare', '2026-02-03 12:00:00', 41.979, -87.907, 38.5, 35.2, 85.1, 15.5, 320, 1012.5, 8.0, 'Partly Cloudy', 0.08, 5, 'NWS_API'),
('obs_004', 'KMIA', 'Miami International', '2026-02-03 12:00:00', 25.795, -80.290, 78.5, 74.2, 90.3, 10.5, 120, 1014.3, 10.0, 'Scattered Clouds', 0.25, 5, 'NWS_API'),
('obs_005', 'KSEA', 'Seattle-Tacoma', '2026-02-03 12:00:00', 47.449, -122.309, 52.3, 48.1, 92.7, 18.2, 250, 1011.9, 7.0, 'Overcast', 0.12, 5, 'NWS_API');

-- Insert sample GRIB2 transformation log entries
INSERT INTO grib2_transformation_log (log_id, file_name, source_path, parameter_name, forecast_time, source_crs, target_crs, gdal_command, output_file, grid_resolution_x, grid_resolution_y, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status, target_table, load_timestamp, processing_duration_seconds, records_processed) VALUES
('log_grib_001', 'ds.temp.bin', '/data/raw/grib2/ds.temp.bin', 'Temperature', '2026-02-03 12:00:00', 'EPSG:4326', 'EPSG:3857', 'gdal_translate -of GTiff -a_srs EPSG:3857', '/data/transformed/grib2/ds.temp_transformed.tif', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success', 'grib2_forecasts', '2026-02-03 12:05:00', 45, 50000),
('log_grib_002', 'ds.qpf.bin', '/data/raw/grib2/ds.qpf.bin', 'Precipitation', '2026-02-03 12:00:00', 'EPSG:4326', 'EPSG:3857', 'gdal_translate -of GTiff -a_srs EPSG:3857', '/data/transformed/grib2/ds.qpf_transformed.tif', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success', 'grib2_forecasts', '2026-02-03 12:05:00', 42, 50000),
('log_grib_003', 'ds.wspd.bin', '/data/raw/grib2/ds.wspd.bin', 'WindSpeed', '2026-02-03 12:00:00', 'EPSG:4326', 'EPSG:3857', 'gdal_translate -of GTiff -a_srs EPSG:3857', '/data/transformed/grib2/ds.wspd_transformed.tif', 0.025, 0.025, -125.0, 24.0, -66.0, 49.0, 'Success', 'grib2_forecasts', '2026-02-03 12:05:00', 38, 50000);

-- Insert sample shapefile integration log entries
INSERT INTO shapefile_integration_log (log_id, shapefile_name, source_path, feature_type, feature_count, source_crs, target_crs, ogr2ogr_command, transformed_path, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status, target_table, load_timestamp, processing_duration_seconds) VALUES
('log_shp_001', 'w_18mr25.shp', '/data/raw/shapefiles/cwa/w_18mr25.shp', 'CWA', 122, 'EPSG:4326', 'EPSG:4326', 'ogr2ogr -t_srs EPSG:4326', '/data/transformed/shapefiles/cwa/w_18mr25_wgs84.shp', -125.0, 24.0, -66.0, 49.0, 'Success', 'shapefile_boundaries', '2026-02-03 11:00:00', 120),
('log_shp_002', 'fz18mr25.shp', '/data/raw/shapefiles/firezones/fz18mr25.shp', 'FireZone', 350, 'EPSG:4326', 'EPSG:4326', 'ogr2ogr -t_srs EPSG:4326', '/data/transformed/shapefiles/firezones/fz18mr25_wgs84.shp', -125.0, 24.0, -66.0, 49.0, 'Success', 'shapefile_boundaries', '2026-02-03 11:00:00', 95),
('log_shp_003', 'mz18mr25.shp', '/data/raw/shapefiles/marine/mz18mr25.shp', 'MarineZone', 85, 'EPSG:4326', 'EPSG:4326', 'ogr2ogr -t_srs EPSG:4326', '/data/transformed/shapefiles/marine/mz18mr25_wgs84.shp', -125.0, 24.0, -66.0, 49.0, 'Success', 'shapefile_boundaries', '2026-02-03 11:00:00', 65);

-- Insert sample spatial join results
INSERT INTO spatial_join_results (join_id, grib_file, shapefile_name, join_type, gdal_command, features_matched, features_total, match_percentage, output_file, forecast_id, boundary_id) VALUES
('join_001', 'ds.temp.bin', 'w_18mr25.shp', 'Point-in-Polygon', 'gdalwarp -cutline', 45000, 50000, 90.00, '/data/transformed/spatial_joins/temp_cwa_clipped.tif', 'grib_temp_001', 'cwa_001'),
('join_002', 'ds.qpf.bin', 'fz18mr25.shp', 'Raster-to-Vector', 'gdalwarp -cutline', 32000, 50000, 64.00, '/data/transformed/spatial_joins/qpf_firezone_clipped.tif', 'grib_qpf_001', 'fz_001'),
('join_003', 'ds.wspd.bin', 'mz18mr25.shp', 'Clip', 'gdalwarp -cutline -crop_to_cutline', 15000, 50000, 30.00, '/data/transformed/spatial_joins/wspd_marine_clipped.tif', 'grib_wspd_001', 'mz_001');

-- Insert sample data quality metrics
INSERT INTO data_quality_metrics (metric_id, metric_date, data_source, files_processed, files_successful, files_failed, success_rate, total_records, records_with_errors, error_rate, spatial_coverage_km2, temporal_coverage_hours, data_freshness_minutes) VALUES
('metric_001', '2026-02-03', 'GRIB2', 15, 14, 1, 93.33, 750000, 2500, 0.33, 7850000.00, 168, 5),
('metric_002', '2026-02-03', 'Shapefile', 8, 8, 0, 100.00, 557, 0, 0.00, 7850000.00, 0, 60),
('metric_003', '2026-02-03', 'API', 0, 0, 0, 0.00, 5000, 25, 0.50, 0.00, 24, 5);

-- Insert sample load status entries
INSERT INTO load_status (load_id, source_file, target_table, load_start_time, load_end_time, load_duration_seconds, records_loaded, file_size_mb, load_rate_mb_per_sec, load_status, warehouse, data_source_type) VALUES
('load_001', '/data/transformed/grib2/ds.temp_transformed.tif', 'grib2_forecasts', '2026-02-03 12:05:00', '2026-02-03 12:05:45', 45, 50000, 125.5, 2.79, 'Success', 'WEATHER_WH', 'GRIB2'),
('load_002', '/data/transformed/shapefiles/cwa/w_18mr25_wgs84.shp', 'shapefile_boundaries', '2026-02-03 11:00:00', '2026-02-03 11:02:00', 120, 122, 2.3, 0.02, 'Success', 'WEATHER_WH', 'Shapefile'),
('load_003', '/data/api/observations_20260203.json', 'weather_observations', '2026-02-03 12:00:00', '2026-02-03 12:00:15', 15, 5000, 0.5, 0.03, 'Success', 'WEATHER_WH', 'API');
