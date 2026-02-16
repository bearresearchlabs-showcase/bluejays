-- Maritime Shipping Intelligence Database Sample Data
-- Compatible with PostgreSQL
-- Production sample data for maritime schedules and shipping intelligence system

-- Insert Carriers
INSERT INTO carriers (carrier_id, carrier_name, scac_code, carrier_type, country, website, status, fleet_size, total_capacity_teu, established_year) VALUES
('CAR001', 'Maersk Line', 'MAEU', 'Container', 'Denmark', 'https://www.maersk.com', 'Active', 700, 4200000, 1928),
('CAR002', 'Mediterranean Shipping Company', 'MSCU', 'Container', 'Switzerland', 'https://www.msc.com', 'Active', 650, 4500000, 1970),
('CAR003', 'CMA CGM', 'CMAU', 'Container', 'France', 'https://www.cma-cgm.com', 'Active', 550, 3200000, 1978),
('CAR004', 'COSCO Shipping Lines', 'COSU', 'Container', 'China', 'https://www.coscoshipping.com', 'Active', 500, 2900000, 2016),
('CAR005', 'Hapag-Lloyd', 'HLBU', 'Container', 'Germany', 'https://www.hapag-lloyd.com', 'Active', 250, 1800000, 1970),
('CAR006', 'Evergreen Line', 'EGLV', 'Container', 'Taiwan', 'https://www.evergreen-line.com', 'Active', 200, 1500000, 1968),
('CAR007', 'Yang Ming Marine Transport', 'YMLU', 'Container', 'Taiwan', 'https://www.yangming.com', 'Active', 100, 700000, 1972),
('CAR008', 'ONE (Ocean Network Express)', 'ONEY', 'Container', 'Singapore', 'https://www.one-line.com', 'Active', 220, 1600000, 2017),
('CAR009', 'ZIM Integrated Shipping Services', 'ZIMU', 'Container', 'Israel', 'https://www.zim.com', 'Active', 120, 500000, 1945),
('CAR010', 'Hyundai Merchant Marine', 'HMMU', 'Container', 'South Korea', 'https://www.hmm21.com', 'Active', 80, 600000, 1976);

-- Insert Locations
INSERT INTO locations (location_id, location_name, location_type, country_code, latitude, longitude) VALUES
('LOC001', 'United States', 'Country', 'USA', 39.8283, -98.5795),
('LOC002', 'China', 'Country', 'CHN', 35.8617, 104.1954),
('LOC003', 'Singapore', 'Country', 'SGP', 1.3521, 103.8198),
('LOC004', 'Netherlands', 'Country', 'NLD', 52.1326, 5.2913),
('LOC005', 'Germany', 'Country', 'DEU', 51.1657, 10.4515),
('LOC006', 'United Kingdom', 'Country', 'GBR', 55.3781, -3.4360),
('LOC007', 'Japan', 'Country', 'JPN', 36.2048, 138.2529),
('LOC008', 'South Korea', 'Country', 'KOR', 35.9078, 127.7669),
('LOC009', 'United Arab Emirates', 'Country', 'ARE', 23.4241, 53.8478),
('LOC010', 'California', 'State', 'USA', 36.7783, -119.4179);

-- Insert Ports
INSERT INTO ports (port_id, port_name, port_code, locode, location_id, country, country_code, latitude, longitude, port_type, timezone, depth_meters, container_capacity_teu, berth_count, status, data_source) VALUES
('PORT001', 'Port of Los Angeles', 'LAX', 'USLAX', 'LOC010', 'United States', 'USA', 33.7278, -118.2644, 'Container', 'America/Los_Angeles', 16.0, 10000000, 270, 'Active', 'MARAD'),
('PORT002', 'Port of Long Beach', 'LGB', 'USLGB', 'LOC010', 'United States', 'USA', 33.7542, -118.2167, 'Container', 'America/Los_Angeles', 16.0, 8000000, 80, 'Active', 'MARAD'),
('PORT003', 'Port of New York and New Jersey', 'NYC', 'USNYC', 'LOC001', 'United States', 'USA', 40.6892, -74.0445, 'Container', 'America/New_York', 15.0, 7000000, 200, 'Active', 'MARAD'),
('PORT004', 'Port of Savannah', 'SAV', 'USSAV', 'LOC001', 'United States', 'USA', 32.0809, -81.0912, 'Container', 'America/New_York', 13.7, 5000000, 36, 'Active', 'MARAD'),
('PORT005', 'Port of Shanghai', 'SHA', 'CNSHA', 'LOC002', 'China', 'CHN', 31.2304, 121.4737, 'Container', 'Asia/Shanghai', 15.0, 47000000, 200, 'Active', 'MARAD'),
('PORT006', 'Port of Singapore', 'SIN', 'SGSIN', 'LOC003', 'Singapore', 'SGP', 1.2897, 103.8501, 'Container', 'Asia/Singapore', 16.0, 37000000, 200, 'Active', 'MARAD'),
('PORT007', 'Port of Rotterdam', 'RTM', 'NLRTM', 'LOC004', 'Netherlands', 'NLD', 51.9225, 4.4792, 'Container', 'Europe/Amsterdam', 24.0, 15000000, 100, 'Active', 'MARAD'),
('PORT008', 'Port of Hamburg', 'HAM', 'DEHAM', 'LOC005', 'Germany', 'DEU', 53.5511, 9.9937, 'Container', 'Europe/Berlin', 15.0, 9000000, 50, 'Active', 'MARAD'),
('PORT009', 'Port of Busan', 'PUS', 'KRPUS', 'LOC008', 'South Korea', 'KOR', 35.1796, 129.0756, 'Container', 'Asia/Seoul', 16.0, 22000000, 150, 'Active', 'MARAD'),
('PORT010', 'Port of Dubai', 'DXB', 'AEDXB', 'LOC009', 'United Arab Emirates', 'ARE', 25.2048, 55.2708, 'Container', 'Asia/Dubai', 15.0, 15000000, 67, 'Active', 'MARAD'),
('PORT011', 'Port of Tokyo', 'TYO', 'JPTYO', 'LOC007', 'Japan', 'JPN', 35.6762, 139.6503, 'Container', 'Asia/Tokyo', 15.0, 5000000, 30, 'Active', 'MARAD'),
('PORT012', 'Port of London', 'LON', 'GBLON', 'LOC006', 'United Kingdom', 'GBR', 51.5074, -0.1278, 'Container', 'Europe/London', 14.0, 3000000, 25, 'Active', 'MARAD');

-- Insert Vessels
INSERT INTO vessels (vessel_id, vessel_name, imo_number, mmsi, call_sign, carrier_id, vessel_type, flag_country, flag_country_code, year_built, gross_tonnage, deadweight_tonnage, length_meters, beam_meters, draft_meters, max_speed_knots, container_capacity_teu, status, data_source) VALUES
('VES001', 'MSC Gulsun', '9776361', '249110000', '9HA2227', 'CAR002', 'Container', 'Panama', 'PAN', 2019, 232618, 199700, 399.9, 61.5, 16.0, 22.0, 23756, 'Active', 'USCG'),
('VES002', 'MSC Oscar', '9703318', '249110000', '9HA2228', 'CAR002', 'Container', 'Panama', 'PAN', 2015, 197362, 199700, 395.4, 59.0, 16.0, 22.0, 19224, 'Active', 'USCG'),
('VES003', 'CMA CGM Antoine de Saint Exupery', '9778523', '228339600', 'FNBP', 'CAR003', 'Container', 'France', 'FRA', 2018, 219277, 199700, 400.0, 59.0, 16.0, 22.0, 20722, 'Active', 'USCG'),
('VES004', 'COSCO Shipping Universe', '9776171', '477123400', 'BQCS', 'CAR004', 'Container', 'Hong Kong', 'HKG', 2018, 199744, 199700, 400.0, 58.6, 16.0, 22.0, 21237, 'Active', 'USCG'),
('VES005', 'Madrid Maersk', '9784308', '220417000', 'OYGR2', 'CAR001', 'Container', 'Denmark', 'DNK', 2017, 210692, 199700, 399.0, 58.6, 16.0, 22.0, 20568, 'Active', 'USCG'),
('VES006', 'Munich Maersk', '9784310', '220417000', 'OYGR3', 'CAR001', 'Container', 'Denmark', 'DNK', 2017, 210692, 199700, 399.0, 58.6, 16.0, 22.0, 20568, 'Active', 'USCG'),
('VES007', 'Hamburg Express', '9784309', '211331000', 'DHBN', 'CAR005', 'Container', 'Germany', 'DEU', 2017, 210692, 199700, 399.0, 58.6, 16.0, 22.0, 20568, 'Active', 'USCG'),
('VES008', 'Ever Golden', '9776172', '416000000', 'BQCT', 'CAR006', 'Container', 'Panama', 'PAN', 2018, 199744, 199700, 400.0, 58.6, 16.0, 22.0, 20212, 'Active', 'USCG'),
('VES009', 'YM Efficiency', '9776173', '416000000', 'BQCU', 'CAR007', 'Container', 'Singapore', 'SGP', 2018, 199744, 199700, 400.0, 58.6, 16.0, 22.0, 20212, 'Active', 'USCG'),
('VES010', 'ONE Innovation', '9776174', '563000000', '9VHF', 'CAR008', 'Container', 'Singapore', 'SGP', 2018, 199744, 199700, 400.0, 58.6, 16.0, 22.0, 20212, 'Active', 'USCG');

-- Insert Routes
INSERT INTO routes (route_id, route_name, route_code, carrier_id, service_type, route_type, frequency_weeks, transit_time_days, status, start_date) VALUES
('ROU001', 'Asia-Europe Express', 'AEX', 'CAR001', 'Express', 'Asia-Europe', 1, 28, 'Active', '2020-01-01'),
('ROU002', 'Trans-Pacific Express', 'TPX', 'CAR002', 'Express', 'Trans-Pacific', 1, 14, 'Active', '2020-01-01'),
('ROU003', 'Asia-Mediterranean', 'AMX', 'CAR003', 'Regular', 'Asia-Mediterranean', 1, 30, 'Active', '2020-01-01'),
('ROU004', 'Pacific Southwest', 'PSW', 'CAR004', 'Regular', 'Trans-Pacific', 1, 18, 'Active', '2020-01-01'),
('ROU005', 'North Europe Express', 'NEX', 'CAR005', 'Express', 'Asia-Europe', 1, 26, 'Active', '2020-01-01'),
('ROU006', 'Asia-US East Coast', 'AEC', 'CAR006', 'Regular', 'Trans-Pacific', 1, 35, 'Active', '2020-01-01'),
('ROU007', 'Far East Express', 'FEX', 'CAR007', 'Express', 'Trans-Pacific', 1, 16, 'Active', '2020-01-01'),
('ROU008', 'Asia-Europe Loop', 'AEL', 'CAR008', 'Regular', 'Asia-Europe', 1, 32, 'Active', '2020-01-01'),
('ROU009', 'Pacific Express', 'PEX', 'CAR009', 'Express', 'Trans-Pacific', 1, 20, 'Active', '2020-01-01'),
('ROU010', 'Asia-US West Coast', 'AWC', 'CAR010', 'Regular', 'Trans-Pacific', 1, 15, 'Active', '2020-01-01');

-- Insert Route Ports
INSERT INTO route_ports (route_port_id, route_id, port_id, port_sequence, port_role) VALUES
('RP001', 'ROU001', 'PORT005', 1, 'Origin'),
('RP002', 'ROU001', 'PORT006', 2, 'Transshipment'),
('RP003', 'ROU001', 'PORT007', 3, 'Destination'),
('RP004', 'ROU002', 'PORT005', 1, 'Origin'),
('RP005', 'ROU002', 'PORT001', 2, 'Destination'),
('RP006', 'ROU002', 'PORT002', 3, 'Destination'),
('RP007', 'ROU003', 'PORT005', 1, 'Origin'),
('RP008', 'ROU003', 'PORT006', 2, 'Transshipment'),
('RP009', 'ROU003', 'PORT010', 3, 'Transshipment'),
('RP010', 'ROU003', 'PORT007', 4, 'Destination'),
('RP011', 'ROU004', 'PORT009', 1, 'Origin'),
('RP012', 'ROU004', 'PORT001', 2, 'Destination'),
('RP013', 'ROU005', 'PORT005', 1, 'Origin'),
('RP014', 'ROU005', 'PORT008', 2, 'Destination'),
('RP015', 'ROU006', 'PORT005', 1, 'Origin'),
('RP016', 'ROU006', 'PORT003', 2, 'Destination');

-- Insert Port Pairs
INSERT INTO port_pairs (port_pair_id, origin_port_id, destination_port_id, carrier_id, route_id, direct_service, transshipment_required, average_transit_days, service_frequency_weeks, status) VALUES
('PP001', 'PORT005', 'PORT001', 'CAR002', 'ROU002', TRUE, FALSE, 14, 1, 'Active'),
('PP002', 'PORT005', 'PORT002', 'CAR002', 'ROU002', TRUE, FALSE, 14, 1, 'Active'),
('PP003', 'PORT005', 'PORT007', 'CAR001', 'ROU001', FALSE, TRUE, 28, 1, 'Active'),
('PP004', 'PORT001', 'PORT005', 'CAR004', 'ROU004', TRUE, FALSE, 18, 1, 'Active'),
('PP005', 'PORT006', 'PORT007', 'CAR003', 'ROU003', FALSE, TRUE, 30, 1, 'Active'),
('PP006', 'PORT005', 'PORT003', 'CAR006', 'ROU006', FALSE, TRUE, 35, 1, 'Active'),
('PP007', 'PORT009', 'PORT001', 'CAR004', 'ROU004', TRUE, FALSE, 18, 1, 'Active'),
('PP008', 'PORT005', 'PORT008', 'CAR005', 'ROU005', TRUE, FALSE, 26, 1, 'Active');

-- Insert Port Calls
INSERT INTO port_calls (port_call_id, vessel_id, port_id, voyage_number, route_id, scheduled_arrival, actual_arrival, scheduled_departure, actual_departure, port_call_type, containers_loaded, containers_discharged, status, data_source) VALUES
('PC001', 'VES001', 'PORT001', 'V001', 'ROU002', '2026-02-10 08:00:00', '2026-02-10 08:15:00', '2026-02-11 20:00:00', '2026-02-11 20:30:00', 'Discharging', 0, 8500, 'Completed', 'AIS'),
('PC002', 'VES002', 'PORT002', 'V002', 'ROU002', '2026-02-12 10:00:00', '2026-02-12 10:20:00', '2026-02-13 22:00:00', '2026-02-13 22:15:00', 'Discharging', 0, 7200, 'Completed', 'AIS'),
('PC003', 'VES003', 'PORT007', 'V003', 'ROU003', '2026-02-15 14:00:00', '2026-02-15 14:10:00', '2026-02-16 18:00:00', '2026-02-16 18:20:00', 'Discharging', 0, 6800, 'Completed', 'AIS'),
('PC004', 'VES004', 'PORT005', 'V004', 'ROU004', '2026-02-18 06:00:00', '2026-02-18 06:05:00', '2026-02-19 12:00:00', '2026-02-19 12:10:00', 'Loading', 9200, 0, 'Completed', 'AIS'),
('PC005', 'VES005', 'PORT008', 'V005', 'ROU005', '2026-02-20 16:00:00', '2026-02-20 16:25:00', '2026-02-21 20:00:00', '2026-02-21 20:15:00', 'Discharging', 0, 7500, 'Completed', 'AIS'),
('PC006', 'VES001', 'PORT005', 'V006', 'ROU002', '2026-02-25 08:00:00', NULL, '2026-02-26 20:00:00', NULL, 'Loading', NULL, NULL, 'Scheduled', 'NOAD'),
('PC007', 'VES002', 'PORT006', 'V007', 'ROU002', '2026-02-28 10:00:00', NULL, '2026-03-01 14:00:00', NULL, 'Transshipment', NULL, NULL, 'Scheduled', 'NOAD'),
('PC008', 'VES006', 'PORT001', 'V008', 'ROU001', '2026-03-05 12:00:00', NULL, '2026-03-06 18:00:00', NULL, 'Discharging', NULL, NULL, 'Scheduled', 'NOAD'),
('PC009', 'VES007', 'PORT003', 'V009', 'ROU006', '2026-03-08 14:00:00', NULL, '2026-03-09 20:00:00', NULL, 'Discharging', NULL, NULL, 'Scheduled', 'NOAD'),
('PC010', 'VES008', 'PORT009', 'V010', 'ROU004', '2026-03-10 08:00:00', NULL, '2026-03-11 16:00:00', NULL, 'Loading', NULL, NULL, 'Scheduled', 'NOAD');

-- Insert Sailings
INSERT INTO sailings (sailing_id, vessel_id, voyage_number, route_id, origin_port_id, destination_port_id, scheduled_departure, actual_departure, scheduled_arrival, actual_arrival, transit_days, distance_nautical_miles, average_speed_knots, total_containers, total_teu, capacity_utilization_percent, status, data_source) VALUES
('SAI001', 'VES001', 'V001', 'ROU002', 'PORT005', 'PORT001', '2026-01-28 20:00:00', '2026-01-28 20:15:00', '2026-02-10 08:00:00', '2026-02-10 08:15:00', 13, 5500, 18.5, 18500, 18500, 78.0, 'Completed', 'AIS'),
('SAI002', 'VES002', 'V002', 'ROU002', 'PORT005', 'PORT002', '2026-01-30 22:00:00', '2026-01-30 22:10:00', '2026-02-12 10:00:00', '2026-02-12 10:20:00', 13, 5600, 18.8, 17200, 17200, 72.0, 'Completed', 'AIS'),
('SAI003', 'VES003', 'V003', 'ROU003', 'PORT005', 'PORT007', '2026-02-01 12:00:00', '2026-02-01 12:05:00', '2026-02-15 14:00:00', '2026-02-15 14:10:00', 14, 7200, 21.4, 16800, 16800, 81.0, 'Completed', 'AIS'),
('SAI004', 'VES004', 'V004', 'ROU004', 'PORT009', 'PORT001', '2026-02-05 08:00:00', '2026-02-05 08:10:00', '2026-02-18 06:00:00', '2026-02-18 06:05:00', 13, 5400, 17.3, 19200, 19200, 90.5, 'Completed', 'AIS'),
('SAI005', 'VES005', 'V005', 'ROU005', 'PORT005', 'PORT008', '2026-02-08 16:00:00', '2026-02-08 16:20:00', '2026-02-20 16:00:00', '2026-02-20 16:25:00', 12, 6800, 23.6, 17500, 17500, 85.0, 'Completed', 'AIS'),
('SAI006', 'VES001', 'V006', 'ROU002', 'PORT005', 'PORT001', '2026-02-25 20:00:00', NULL, '2026-03-10 08:00:00', NULL, 13, 5500, NULL, NULL, NULL, NULL, 'Scheduled', 'NOAD'),
('SAI007', 'VES006', 'V008', 'ROU001', 'PORT005', 'PORT001', '2026-03-05 20:00:00', NULL, '2026-03-20 08:00:00', NULL, 15, 5500, NULL, NULL, NULL, NULL, 'Scheduled', 'NOAD'),
('SAI008', 'VES007', 'V009', 'ROU006', 'PORT005', 'PORT003', '2026-03-08 22:00:00', NULL, '2026-03-25 14:00:00', NULL, 17, 7200, NULL, NULL, NULL, NULL, 'Scheduled', 'NOAD');

-- Insert Voyages
INSERT INTO voyages (voyage_id, vessel_id, voyage_number, route_id, start_port_id, end_port_id, start_date, end_date, total_distance_nautical_miles, total_transit_days, port_call_count, total_containers, total_teu, status) VALUES
('VOY001', 'VES001', 'V001', 'ROU002', 'PORT005', 'PORT001', '2026-01-28 20:15:00', '2026-02-10 08:15:00', 5500, 13, 1, 18500, 18500, 'Completed'),
('VOY002', 'VES002', 'V002', 'ROU002', 'PORT005', 'PORT002', '2026-01-30 22:10:00', '2026-02-12 10:20:00', 5600, 13, 1, 17200, 17200, 'Completed'),
('VOY003', 'VES003', 'V003', 'ROU003', 'PORT005', 'PORT007', '2026-02-01 12:05:00', '2026-02-15 14:10:00', 7200, 14, 1, 16800, 16800, 'Completed'),
('VOY004', 'VES004', 'V004', 'ROU004', 'PORT009', 'PORT001', '2026-02-05 08:10:00', '2026-02-18 06:05:00', 5400, 13, 1, 19200, 19200, 'Completed'),
('VOY005', 'VES005', 'V005', 'ROU005', 'PORT005', 'PORT008', '2026-02-08 16:20:00', '2026-02-20 16:25:00', 6800, 12, 1, 17500, 17500, 'Completed'),
('VOY006', 'VES001', 'V006', 'ROU002', 'PORT005', 'PORT001', '2026-02-25 20:00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'In Progress'),
('VOY007', 'VES006', 'V008', 'ROU001', 'PORT005', 'PORT001', '2026-03-05 20:00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'Scheduled'),
('VOY008', 'VES007', 'V009', 'ROU006', 'PORT005', 'PORT003', '2026-03-08 22:00:00', NULL, NULL, NULL, NULL, NULL, NULL, 'Scheduled');

-- Insert Vessel Tracking (AIS data)
INSERT INTO vessel_tracking (tracking_id, vessel_id, mmsi, timestamp, latitude, longitude, speed_knots, course_degrees, heading_degrees, navigation_status, destination, eta, data_source, data_quality) VALUES
('TRK001', 'VES001', '249110000', '2026-02-10 08:00:00', 33.7278, -118.2644, 0.5, 180.0, 180.0, 'Moored', 'Los Angeles', '2026-02-10 08:00:00', 'AIS', 'High'),
('TRK002', 'VES002', '249110000', '2026-02-12 10:00:00', 33.7542, -118.2167, 0.3, 90.0, 90.0, 'Moored', 'Long Beach', '2026-02-12 10:00:00', 'AIS', 'High'),
('TRK003', 'VES003', '228339600', '2026-02-15 14:00:00', 51.9225, 4.4792, 0.2, 270.0, 270.0, 'Moored', 'Rotterdam', '2026-02-15 14:00:00', 'AIS', 'High'),
('TRK004', 'VES004', '477123400', '2026-02-18 06:00:00', 31.2304, 121.4737, 0.4, 0.0, 0.0, 'Moored', 'Shanghai', '2026-02-18 06:00:00', 'AIS', 'High'),
('TRK005', 'VES005', '220417000', '2026-02-20 16:00:00', 53.5511, 9.9937, 0.1, 180.0, 180.0, 'Moored', 'Hamburg', '2026-02-20 16:00:00', 'AIS', 'High'),
('TRK006', 'VES001', '249110000', '2026-02-25 20:00:00', 31.2304, 121.4737, 18.5, 45.0, 45.0, 'Under way', 'Los Angeles', '2026-03-10 08:00:00', 'AIS', 'High'),
('TRK007', 'VES006', '220417000', '2026-03-05 20:00:00', 31.2304, 121.4737, 19.2, 50.0, 50.0, 'Under way', 'Los Angeles', '2026-03-20 08:00:00', 'AIS', 'High'),
('TRK008', 'VES007', '211331000', '2026-03-08 22:00:00', 31.2304, 121.4737, 17.8, 55.0, 55.0, 'Under way', 'New York', '2026-03-25 14:00:00', 'AIS', 'High');

-- Insert Port Statistics
INSERT INTO port_statistics (statistic_id, port_id, statistic_date, statistic_period, total_vessel_calls, total_container_teu, containers_loaded, containers_discharged, containers_transshipped, average_vessel_size_teu, average_dwell_time_hours, berth_utilization_percent, data_source) VALUES
('PS001', 'PORT001', '2026-02-01', 'Monthly', 450, 850000, 420000, 430000, 0, 1888, 48, 85.5, 'MARAD'),
('PS002', 'PORT002', '2026-02-01', 'Monthly', 380, 720000, 360000, 360000, 0, 1895, 52, 82.0, 'MARAD'),
('PS003', 'PORT005', '2026-02-01', 'Monthly', 1200, 3500000, 1800000, 1700000, 0, 2917, 36, 92.0, 'MARAD'),
('PS004', 'PORT006', '2026-02-01', 'Monthly', 950, 2800000, 1400000, 1400000, 0, 2947, 24, 88.5, 'MARAD'),
('PS005', 'PORT007', '2026-02-01', 'Monthly', 520, 1500000, 750000, 750000, 0, 2885, 42, 80.0, 'MARAD'),
('PS006', 'PORT001', '2026-01-01', 'Monthly', 420, 780000, 390000, 390000, 0, 1857, 50, 83.0, 'MARAD'),
('PS007', 'PORT003', '2026-02-01', 'Monthly', 350, 650000, 325000, 325000, 0, 1857, 55, 78.5, 'MARAD'),
('PS008', 'PORT008', '2026-02-01', 'Monthly', 280, 520000, 260000, 260000, 0, 1857, 60, 75.0, 'MARAD');

-- Insert Carrier Performance
INSERT INTO carrier_performance (performance_id, carrier_id, evaluation_period_start, evaluation_period_end, total_voyages, on_time_departures, on_time_arrivals, on_time_performance_percent, average_transit_time_days, vessel_utilization_percent, capacity_utilization_percent, total_teu_carried, port_calls_count, route_coverage_count) VALUES
('CP001', 'CAR001', '2026-01-01', '2026-01-31', 120, 108, 112, 91.7, 14.5, 88.0, 82.5, 2450000, 480, 15),
('CP002', 'CAR002', '2026-01-01', '2026-01-31', 135, 122, 128, 92.6, 13.8, 90.0, 85.0, 2800000, 540, 18),
('CP003', 'CAR003', '2026-01-01', '2026-01-31', 110, 99, 105, 92.7, 15.2, 87.5, 81.0, 2200000, 440, 12),
('CP004', 'CAR004', '2026-01-01', '2026-01-31', 125, 115, 120, 94.0, 14.0, 89.0, 83.5, 2600000, 500, 14),
('CP005', 'CAR005', '2026-01-01', '2026-01-31', 95, 87, 90, 93.2, 13.5, 86.0, 80.0, 1900000, 380, 10);
