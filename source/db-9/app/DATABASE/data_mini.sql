-- Sample Data for Shipping Intelligence Database (Docker mini)
-- Compatible with PostgreSQL
-- Production sample data for shipping intelligence and rate comparison system

-- Insert shipping carriers
INSERT INTO shipping_carriers (carrier_id, carrier_name, carrier_code, carrier_type, api_endpoint, rate_api_version, tracking_api_version, commercial_pricing_available, requires_account, active_status) VALUES
('carrier_usps', 'United States Postal Service', 'USPS', 'Postal', 'https://developers.usps.com/api', '3.0', '3.0', TRUE, TRUE, TRUE),
('carrier_ups', 'United Parcel Service', 'UPS', 'Courier', 'https://developer.ups.com/api', 'v1', 'v1', TRUE, TRUE, TRUE),
('carrier_fedex', 'FedEx Corporation', 'FEDEX', 'Courier', 'https://developer.fedex.com/api', 'v1', 'v1', TRUE, TRUE, TRUE);

-- Insert shipping service types
INSERT INTO shipping_service_types (service_id, carrier_id, service_code, service_name, service_category, domestic_available, international_available, max_weight_lbs, max_dimensions_length, max_dimensions_width, max_dimensions_height, tracking_included, insurance_available, signature_required, active_status) VALUES
('service_usps_priority', 'carrier_usps', 'PRIORITY', 'Priority Mail', 'Priority', TRUE, TRUE, 70.0, 108.0, 108.0, 108.0, TRUE, TRUE, FALSE, TRUE),
('service_usps_priority_express', 'carrier_usps', 'PRIORITY_EXPRESS', 'Priority Mail Express', 'Express', TRUE, TRUE, 70.0, 108.0, 108.0, 108.0, TRUE, TRUE, TRUE, TRUE),
('service_usps_ground', 'carrier_usps', 'GROUND', 'USPS Ground Advantage', 'Ground', TRUE, FALSE, 70.0, 130.0, 130.0, 130.0, TRUE, TRUE, FALSE, TRUE),
('service_usps_first_class', 'carrier_usps', 'FIRST_CLASS', 'First-Class Mail', 'Economy', TRUE, TRUE, 15.999, 108.0, 108.0, 108.0, TRUE, FALSE, FALSE, TRUE),
('service_ups_ground', 'carrier_ups', 'GROUND', 'UPS Ground', 'Ground', TRUE, FALSE, 150.0, 108.0, 108.0, 108.0, TRUE, TRUE, FALSE, TRUE),
('service_ups_next_day_air', 'carrier_ups', 'NEXT_DAY_AIR', 'UPS Next Day Air', 'Express', TRUE, TRUE, 150.0, 108.0, 108.0, 108.0, TRUE, TRUE, TRUE, TRUE),
('service_ups_2nd_day_air', 'carrier_ups', '2ND_DAY_AIR', 'UPS 2nd Day Air', 'Express', TRUE, TRUE, 150.0, 108.0, 108.0, 108.0, TRUE, TRUE, FALSE, TRUE),
('service_fedex_ground', 'carrier_fedex', 'GROUND', 'FedEx Ground', 'Ground', TRUE, FALSE, 150.0, 108.0, 108.0, 108.0, TRUE, TRUE, FALSE, TRUE),
('service_fedex_express', 'carrier_fedex', 'EXPRESS', 'FedEx Express', 'Express', TRUE, TRUE, 150.0, 108.0, 108.0, 108.0, TRUE, TRUE, TRUE, TRUE);

-- Insert shipping zones (sample zone mappings for major cities)
INSERT INTO shipping_zones (zone_id, carrier_id, origin_zip_code, destination_zip_code, zone_number, zone_type, distance_miles, transit_days_min, transit_days_max, effective_date, expiration_date) VALUES
('zone_usps_10001_90210', 'carrier_usps', '10001', '90210', 8, 'Domestic', 2785.0, 3, 5, '2026-01-01', NULL),
('zone_usps_10001_60601', 'carrier_usps', '10001', '60601', 3, 'Domestic', 790.0, 2, 3, '2026-01-01', NULL),
('zone_usps_10001_33101', 'carrier_usps', '10001', '33101', 5, 'Domestic', 1289.0, 2, 4, '2026-01-01', NULL),
('zone_usps_10001_98101', 'carrier_usps', '10001', '98101', 8, 'Domestic', 2408.0, 4, 6, '2026-01-01', NULL),
('zone_usps_90210_10001', 'carrier_usps', '90210', '10001', 8, 'Domestic', 2785.0, 3, 5, '2026-01-01', NULL),
('zone_usps_90210_60601', 'carrier_usps', '90210', '60601', 6, 'Domestic', 2014.0, 3, 4, '2026-01-01', NULL),
('zone_usps_90210_98101', 'carrier_usps', '90210', '98101', 3, 'Domestic', 1135.0, 2, 3, '2026-01-01', NULL),
('zone_ups_10001_90210', 'carrier_ups', '10001', '90210', 8, 'Domestic', 2785.0, 5, 7, '2026-01-01', NULL),
('zone_ups_10001_60601', 'carrier_ups', '10001', '60601', 3, 'Domestic', 790.0, 1, 2, '2026-01-01', NULL),
('zone_ups_90210_10001', 'carrier_ups', '90210', '10001', 8, 'Domestic', 2785.0, 5, 7, '2026-01-01', NULL),
('zone_ups_90210_60601', 'carrier_ups', '90210', '60601', 6, 'Domestic', 2014.0, 4, 5, '2026-01-01', NULL);

-- Insert shipping rates (sample rates for different weights and zones)
INSERT INTO shipping_rates (rate_id, carrier_id, service_id, zone_id, weight_lbs, weight_oz, rate_amount, rate_type, surcharge_amount, total_rate, effective_date, expiration_date, rate_source) VALUES
('rate_usps_priority_1lb_zone3', 'carrier_usps', 'service_usps_priority', 'zone_usps_10001_60601', 1.0, 16.0, 8.95, 'Commercial', 0.0, 8.95, '2026-01-01', NULL, 'API'),
('rate_usps_priority_2lb_zone3', 'carrier_usps', 'service_usps_priority', 'zone_usps_10001_60601', 2.0, 32.0, 10.25, 'Commercial', 0.0, 10.25, '2026-01-01', NULL, 'API'),
('rate_usps_priority_5lb_zone3', 'carrier_usps', 'service_usps_priority', 'zone_usps_10001_60601', 5.0, 80.0, 14.50, 'Commercial', 0.0, 14.50, '2026-01-01', NULL, 'API'),
('rate_usps_priority_1lb_zone8', 'carrier_usps', 'service_usps_priority', 'zone_usps_10001_90210', 1.0, 16.0, 12.95, 'Commercial', 0.0, 12.95, '2026-01-01', NULL, 'API'),
('rate_usps_priority_2lb_zone8', 'carrier_usps', 'service_usps_priority', 'zone_usps_10001_90210', 2.0, 32.0, 15.25, 'Commercial', 0.0, 15.25, '2026-01-01', NULL, 'API'),
('rate_usps_express_1lb_zone3', 'carrier_usps', 'service_usps_priority_express', 'zone_usps_10001_60601', 1.0, 16.0, 26.95, 'Commercial', 0.0, 26.95, '2026-01-01', NULL, 'API'),
('rate_usps_express_2lb_zone3', 'carrier_usps', 'service_usps_priority_express', 'zone_usps_10001_60601', 2.0, 32.0, 28.95, 'Commercial', 0.0, 28.95, '2026-01-01', NULL, 'API'),
('rate_ups_ground_1lb_zone3', 'carrier_ups', 'service_ups_ground', 'zone_ups_10001_60601', 1.0, 16.0, 9.25, 'Daily', 0.0, 9.25, '2026-01-01', NULL, 'API'),
('rate_ups_ground_5lb_zone3', 'carrier_ups', 'service_ups_ground', 'zone_ups_10001_60601', 5.0, 80.0, 12.50, 'Daily', 0.0, 12.50, '2026-01-01', NULL, 'API'),
('rate_ups_ground_10lb_zone3', 'carrier_ups', 'service_ups_ground', 'zone_ups_10001_60601', 10.0, 160.0, 18.75, 'Daily', 0.0, 18.75, '2026-01-01', NULL, 'API'),
('rate_ups_nda_1lb_zone3', 'carrier_ups', 'service_ups_next_day_air', 'zone_ups_10001_60601', 1.0, 16.0, 45.95, 'Daily', 0.0, 45.95, '2026-01-01', NULL, 'API'),
('rate_ups_nda_5lb_zone3', 'carrier_ups', 'service_ups_next_day_air', 'zone_ups_10001_60601', 5.0, 80.0, 65.50, 'Daily', 0.0, 65.50, '2026-01-01', NULL, 'API');

-- Insert packages
INSERT INTO packages (package_id, user_id, package_reference, weight_lbs, weight_oz, length_inches, width_inches, height_inches, dimensional_weight_lbs, cubic_volume_cubic_inches, package_type, package_value, contents_description) VALUES
('pkg_001', 'user_001', 'ORDER-2026-001', 1.5, 24.0, 12.0, 8.0, 6.0, 1.5, 576.0, 'Box', 45.99, 'Electronics - Small Device'),
('pkg_002', 'user_001', 'ORDER-2026-002', 5.0, 80.0, 18.0, 12.0, 10.0, 5.0, 2160.0, 'Box', 125.50, 'Clothing - Multiple Items'),
('pkg_003', 'user_002', 'ORDER-2026-003', 0.5, 8.0, 10.0, 7.0, 1.0, 0.5, 70.0, 'Envelope', 15.00, 'Documents'),
('pkg_004', 'user_002', 'ORDER-2026-004', 2.5, 40.0, 14.0, 10.0, 8.0, 2.5, 1120.0, 'Box', 89.99, 'Books - Collection'),
('pkg_005', 'user_003', 'ORDER-2026-005', 10.0, 160.0, 20.0, 16.0, 12.0, 10.0, 3840.0, 'Box', 250.00, 'Home Goods - Kitchen Items');

-- Insert shipments
INSERT INTO shipments (shipment_id, package_id, carrier_id, service_id, tracking_number, origin_name, origin_address_line1, origin_city, origin_state, origin_zip_code, origin_country, destination_name, destination_address_line1, destination_city, destination_state, destination_zip_code, destination_country, zone_id, rate_id, label_cost, insurance_cost, signature_cost, total_cost, shipment_status, label_created_at, estimated_delivery_date, actual_delivery_date) VALUES
('ship_001', 'pkg_001', 'carrier_usps', 'service_usps_priority', '9400111899223197428490', 'Acme Shipping', '123 Main St', 'New York', 'NY', '10001', 'US', 'John Doe', '456 Oak Ave', 'Chicago', 'IL', '60601', 'US', 'zone_usps_10001_60601', 'rate_usps_priority_1lb_zone3', 8.95, 0.0, 0.0, 8.95, 'Delivered', '2026-02-01 10:00:00', '2026-02-03', '2026-02-03'),
('ship_002', 'pkg_002', 'carrier_usps', 'service_usps_priority', '9400111899223197428491', 'Acme Shipping', '123 Main St', 'New York', 'NY', '10001', 'US', 'Jane Smith', '789 Pine St', 'Beverly Hills', 'CA', '90210', 'US', 'zone_usps_10001_90210', 'rate_usps_priority_2lb_zone8', 15.25, 2.50, 0.0, 17.75, 'In Transit', '2026-02-02 14:30:00', '2026-02-05', NULL),
('ship_003', 'pkg_003', 'carrier_usps', 'service_usps_first_class', '9400111899223197428492', 'Quick Ship Co', '456 Commerce Blvd', 'Los Angeles', 'CA', '90210', 'US', 'Bob Johnson', '321 Elm St', 'Seattle', 'WA', '98101', 'US', 'zone_usps_90210_98101', NULL, 4.50, 0.0, 0.0, 4.50, 'Label Created', '2026-02-03 09:15:00', '2026-02-05', NULL),
('ship_004', 'pkg_004', 'carrier_ups', 'service_ups_ground', '1Z999AA10123456784', 'Global Shipping', '789 Business Park', 'Chicago', 'IL', '60601', 'US', 'Alice Williams', '654 Maple Dr', 'New York', 'NY', '10001', 'US', 'zone_ups_10001_60601', 'rate_ups_ground_1lb_zone3', 9.25, 0.0, 0.0, 9.25, 'Delivered', '2026-02-01 08:00:00', '2026-02-02', '2026-02-02'),
('ship_005', 'pkg_005', 'carrier_ups', 'service_ups_next_day_air', '1Z999AA10123456785', 'Express Logistics', '321 Industrial Way', 'Miami', 'FL', '33101', 'US', 'Charlie Brown', '987 Cedar Ln', 'Chicago', 'IL', '60601', 'US', 'zone_ups_10001_60601', 'rate_ups_nda_5lb_zone3', 65.50, 5.00, 3.50, 74.00, 'In Transit', '2026-02-03 11:00:00', '2026-02-04', NULL),
('ship_006', 'pkg_002', 'carrier_usps', 'service_usps_priority', '9400111899223197428493', 'Acme Shipping', '123 Main St', 'New York', 'NY', '10001', 'US', 'Marie Dupont', '100 Rue Ste-Catherine', 'Montreal', 'QC', 'H2X 1Y4', 'CA', NULL, NULL, 25.00, 5.00, 0.0, 30.00, 'Delivered', '2026-02-01 09:00:00', '2026-02-05', '2026-02-05');

-- Insert tracking events
INSERT INTO tracking_events (event_id, shipment_id, tracking_number, event_timestamp, event_type, event_status, event_location, event_city, event_state, event_zip_code, event_country, event_description, carrier_status_code) VALUES
('event_001', 'ship_001', '9400111899223197428490', '2026-02-01 10:05:00', 'Label Created', 'ACCEPTED', 'USPS Facility', 'New York', 'NY', '10001', 'US', 'Shipping Label Created, USPS Awaiting Item', 'AC'),
('event_002', 'ship_001', '9400111899223197428490', '2026-02-01 14:30:00', 'In Transit', 'IN_TRANSIT', 'USPS Regional Facility', 'Newark', 'NJ', '07114', 'US', 'Arrived at USPS Regional Facility', 'IT'),
('event_003', 'ship_001', '9400111899223197428490', '2026-02-02 08:15:00', 'In Transit', 'IN_TRANSIT', 'USPS Regional Facility', 'Chicago', 'IL', '60601', 'US', 'Arrived at USPS Regional Facility', 'IT'),
('event_004', 'ship_001', '9400111899223197428490', '2026-02-03 09:00:00', 'Out for Delivery', 'OUT_FOR_DELIVERY', 'USPS Post Office', 'Chicago', 'IL', '60601', 'US', 'Out for Delivery', 'OF'),
('event_005', 'ship_001', '9400111899223197428490', '2026-02-03 14:30:00', 'Delivered', 'DELIVERED', 'Residence', 'Chicago', 'IL', '60601', 'US', 'Delivered, Left with Individual', 'DE'),
('event_006', 'ship_002', '9400111899223197428491', '2026-02-02 14:35:00', 'Label Created', 'ACCEPTED', 'USPS Facility', 'New York', 'NY', '10001', 'US', 'Shipping Label Created, USPS Awaiting Item', 'AC'),
('event_007', 'ship_002', '9400111899223197428491', '2026-02-02 18:00:00', 'In Transit', 'IN_TRANSIT', 'USPS Regional Facility', 'Newark', 'NJ', '07114', 'US', 'Departed USPS Regional Facility', 'IT'),
('event_008', 'ship_004', '1Z999AA10123456784', '2026-02-01 08:05:00', 'Label Created', 'LABEL_CREATED', 'UPS Facility', 'Chicago', 'IL', '60601', 'US', 'Shipment Created', 'OC'),
('event_009', 'ship_004', '1Z999AA10123456784', '2026-02-01 12:00:00', 'In Transit', 'IN_TRANSIT', 'UPS Hub', 'Chicago', 'IL', '60601', 'US', 'Origin Scan', 'OR'),
('event_010', 'ship_004', '1Z999AA10123456784', '2026-02-01 20:00:00', 'In Transit', 'IN_TRANSIT', 'UPS Hub', 'Newark', 'NJ', '07114', 'US', 'Arrival Scan', 'AR'),
('event_011', 'ship_004', '1Z999AA10123456784', '2026-02-02 08:00:00', 'Delivered', 'DELIVERED', 'Residence', 'New York', 'NY', '10001', 'US', 'Delivered', 'D');

-- Insert address validation results
INSERT INTO address_validation_results (validation_id, input_address_line1, input_city, input_state, input_zip_code, validated_address_line1, validated_city, validated_state, validated_zip_code, validated_zip_plus_4, validation_status, delivery_point_code, carrier_route, dpv_confirmation, cmra_flag, vacant_flag, residential_flag) VALUES
('val_001', '456 Oak Ave', 'Chicago', 'IL', '60601', '456 OAK AVE', 'CHICAGO', 'IL', '60601', '60601-1234', 'Valid', '12', 'C012', 'Y', FALSE, FALSE, TRUE),
('val_002', '789 Pine St', 'Beverly Hills', 'CA', '90210', '789 PINE ST', 'BEVERLY HILLS', 'CA', '90210', '90210-5678', 'Valid', '34', 'C034', 'Y', FALSE, FALSE, TRUE),
('val_003', '321 Elm St', 'Seattle', 'WA', '98101', '321 ELM ST', 'SEATTLE', 'WA', '98101', '98101-9012', 'Valid', '56', 'C056', 'Y', FALSE, FALSE, TRUE),
('val_004', '654 Maple Dr', 'New York', 'NY', '10001', '654 MAPLE DR', 'NEW YORK', 'NY', '10001', '10001-3456', 'Valid', '78', 'C078', 'Y', FALSE, FALSE, TRUE),
('val_005', '987 Cedar Ln', 'Chicago', 'IL', '60601', '987 CEDAR LN', 'CHICAGO', 'IL', '60601', '60601-7890', 'Valid', '90', 'C090', 'Y', FALSE, FALSE, TRUE);

-- Insert bulk shipping presets
INSERT INTO bulk_shipping_presets (preset_id, user_id, preset_name, package_type, default_weight_lbs, default_length_inches, default_width_inches, default_height_inches, default_service_id, default_carrier_id, default_insurance_amount, default_signature_required) VALUES
('preset_001', 'user_001', 'Small Package Standard', 'Box', 1.0, 12.0, 8.0, 6.0, 'service_usps_priority', 'carrier_usps', 0.0, FALSE),
('preset_002', 'user_001', 'Medium Package Express', 'Box', 5.0, 18.0, 12.0, 10.0, 'service_usps_priority_express', 'carrier_usps', 100.0, TRUE),
('preset_003', 'user_002', 'Document Envelope', 'Envelope', 0.5, 10.0, 7.0, 1.0, 'service_usps_first_class', 'carrier_usps', 0.0, FALSE),
('preset_004', 'user_003', 'Large Package Ground', 'Box', 10.0, 20.0, 16.0, 12.0, 'service_ups_ground', 'carrier_ups', 250.0, FALSE);

-- Insert rate comparison results
INSERT INTO rate_comparison_results (comparison_id, package_id, origin_zip_code, destination_zip_code, comparison_timestamp, cheapest_carrier_id, cheapest_service_id, cheapest_rate, fastest_carrier_id, fastest_service_id, fastest_transit_days, total_options_count) VALUES
('comp_001', 'pkg_001', '10001', '60601', '2026-02-01 09:45:00', 'carrier_usps', 'service_usps_priority', 8.95, 'carrier_ups', 'service_ups_next_day_air', 1, 6),
('comp_002', 'pkg_002', '10001', '90210', '2026-02-02 14:00:00', 'carrier_usps', 'service_usps_priority', 15.25, 'carrier_usps', 'service_usps_priority_express', 2, 5),
('comp_003', 'pkg_003', '90210', '98101', '2026-02-03 08:30:00', 'carrier_usps', 'service_usps_first_class', 4.50, 'carrier_usps', 'service_usps_priority', 2, 4);

-- Insert shipping adjustments
INSERT INTO shipping_adjustments (adjustment_id, shipment_id, tracking_number, adjustment_type, original_amount, adjusted_amount, adjustment_amount, adjustment_reason, adjustment_status, adjustment_date) VALUES
('adj_001', 'ship_002', '9400111899223197428491', 'Weight', 15.25, 17.75, 2.50, 'Package weight exceeded declared weight by 0.5 lbs', 'Applied', '2026-02-03'),
('adj_002', 'ship_005', '1Z999AA10123456785', 'Dimensions', 65.50, 68.00, 2.50, 'Package dimensions exceeded declared dimensions', 'Pending', '2026-02-03');

-- Insert shipping analytics
INSERT INTO shipping_analytics (analytics_id, analytics_date, carrier_id, service_id, total_shipments, total_revenue, average_rate, total_packages, total_weight_lbs, average_transit_days, on_time_delivery_rate, exception_rate, average_package_value) VALUES
('analytics_001', '2026-02-01', 'carrier_usps', 'service_usps_priority', 15, 134.25, 8.95, 15, 22.5, 2.5, 93.33, 6.67, 45.50),
('analytics_002', '2026-02-01', 'carrier_ups', 'service_ups_ground', 8, 74.00, 9.25, 8, 12.0, 1.5, 100.00, 0.00, 85.00),
('analytics_003', '2026-02-02', 'carrier_usps', 'service_usps_priority', 12, 107.40, 8.95, 12, 18.0, 2.3, 91.67, 8.33, 52.25),
('analytics_004', '2026-02-03', 'carrier_usps', 'service_usps_priority_express', 5, 134.75, 26.95, 5, 7.5, 1.0, 100.00, 0.00, 125.00);

-- Insert international customs (sample international shipment - ship_006 to Canada)
INSERT INTO international_customs (customs_id, shipment_id, customs_declaration_number, customs_value, currency_code, contents_description, hs_tariff_code, country_of_origin, customs_duty_amount, customs_tax_amount, customs_fees_amount, total_customs_amount, customs_status, customs_cleared_date) VALUES
('customs_001', 'ship_006', 'CBP-2026-001234', 125.50, 'USD', 'Clothing - Cotton Apparel', '6203.42', 'CN', 12.55, 10.04, 5.00, 27.59, 'Cleared', '2026-02-05');

-- Insert API rate request log
INSERT INTO api_rate_request_log (log_id, carrier_id, request_type, origin_zip_code, destination_zip_code, weight_lbs, request_timestamp, response_time_ms, response_status_code, rate_returned, api_endpoint) VALUES
('log_001', 'carrier_usps', 'Rate', '10001', '60601', 1.0, '2026-02-01 09:45:00', 245, 200, 8.95, 'https://developers.usps.com/api/prices/v1/domestic'),
('log_002', 'carrier_ups', 'Rate', '10001', '60601', 1.0, '2026-02-01 09:45:05', 312, 200, 9.25, 'https://developer.ups.com/api/rating/v1'),
('log_003', 'carrier_usps', 'Rate', '10001', '90210', 2.0, '2026-02-02 14:00:00', 198, 200, 15.25, 'https://developers.usps.com/api/prices/v1/domestic'),
('log_004', 'carrier_usps', 'Tracking', '10001', NULL, NULL, '2026-02-01 10:00:00', 156, 200, NULL, 'https://developers.usps.com/api/tracking/v1'),
('log_005', 'carrier_ups', 'Tracking', '60601', NULL, NULL, '2026-02-01 08:05:00', 189, 200, NULL, 'https://developer.ups.com/api/tracking/v1');
