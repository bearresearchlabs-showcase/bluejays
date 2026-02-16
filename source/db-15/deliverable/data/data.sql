-- Sample Data for Electricity Cost and Solar Rebate Database
-- Compatible with PostgreSQL
-- Production sample data for electricity cost and solar rebate system

-- Insert sample states
INSERT INTO states (state_id, state_name, state_full_name, region, division, timezone, is_active) VALUES
('CA', 'California', 'State of California', 'West', 'Pacific', 'America/Los_Angeles', TRUE),
('NY', 'New York', 'State of New York', 'Northeast', 'Middle Atlantic', 'America/New_York', TRUE),
('TX', 'Texas', 'State of Texas', 'South', 'West South Central', 'America/Chicago', TRUE),
('FL', 'Florida', 'State of Florida', 'South', 'South Atlantic', 'America/New_York', TRUE),
('IL', 'Illinois', 'State of Illinois', 'Midwest', 'East North Central', 'America/Chicago', TRUE),
('PA', 'Pennsylvania', 'Commonwealth of Pennsylvania', 'Northeast', 'Middle Atlantic', 'America/New_York', TRUE),
('OH', 'Ohio', 'State of Ohio', 'Midwest', 'East North Central', 'America/New_York', TRUE),
('GA', 'Georgia', 'State of Georgia', 'South', 'South Atlantic', 'America/New_York', TRUE),
('NC', 'North Carolina', 'State of North Carolina', 'South', 'South Atlantic', 'America/New_York', TRUE),
('MI', 'Michigan', 'State of Michigan', 'Midwest', 'East North Central', 'America/Detroit', TRUE);

-- Insert sample counties
INSERT INTO counties (county_id, state_id, county_name, county_fips_code, county_seat, population, area_sq_miles) VALUES
('ca_los_angeles', 'CA', 'Los Angeles', '06037', 'Los Angeles', 10014009, 4751.34),
('ny_new_york', 'NY', 'New York', '36061', 'Manhattan', 1694251, 22.83),
('tx_harris', 'TX', 'Harris', '48201', 'Houston', 4731145, 1778.64),
('fl_miami_dade', 'FL', 'Miami-Dade', '12086', 'Miami', 2701767, 1898.00),
('il_cook', 'IL', 'Cook', '17031', 'Chicago', 5275541, 1635.00),
('pa_philadelphia', 'PA', 'Philadelphia', '42101', 'Philadelphia', 1584064, 134.10),
('oh_cuyahoga', 'OH', 'Cuyahoga', '39035', 'Cleveland', 1248512, 458.49),
('ga_fulton', 'GA', 'Fulton', '13121', 'Atlanta', 1063937, 528.73),
('nc_mecklenburg', 'NC', 'Mecklenburg', '37119', 'Charlotte', 1115481, 529.00),
('mi_wayne', 'MI', 'Wayne', '26163', 'Detroit', 1797848, 611.82);

-- Insert sample zip codes
INSERT INTO zip_codes (zip_code, state_id, county_id, city, latitude, longitude, timezone) VALUES
('90001', 'CA', 'ca_los_angeles', 'Los Angeles', 33.9731, -118.2479, 'America/Los_Angeles'),
('10001', 'NY', 'ny_new_york', 'New York', 40.7506, -73.9972, 'America/New_York'),
('77001', 'TX', 'tx_harris', 'Houston', 29.7604, -95.3698, 'America/Chicago'),
('33101', 'FL', 'fl_miami_dade', 'Miami', 25.7617, -80.1918, 'America/New_York'),
('60601', 'IL', 'il_cook', 'Chicago', 41.8781, -87.6298, 'America/Chicago'),
('19101', 'PA', 'pa_philadelphia', 'Philadelphia', 39.9526, -75.1652, 'America/New_York'),
('44101', 'OH', 'oh_cuyahoga', 'Cleveland', 41.4993, -81.6944, 'America/New_York'),
('30301', 'GA', 'ga_fulton', 'Atlanta', 33.7490, -84.3880, 'America/New_York'),
('28201', 'NC', 'nc_mecklenburg', 'Charlotte', 35.2271, -80.8431, 'America/New_York'),
('48201', 'MI', 'mi_wayne', 'Detroit', 42.3314, -83.0458, 'America/Detroit');

-- Insert sample utility companies
INSERT INTO utility_companies (utility_id, utility_name, utility_display_name, utility_type, state_id, service_territory_description, eia_utility_id, openei_utility_id, website_url, total_customers, total_mwh_sold, is_active) VALUES
('util_ca_pge', 'Pacific Gas and Electric Company', 'PG&E', 'Investor-Owned', 'CA', 'Northern and Central California', 'EIA_14328', 'PG&E', 'https://www.pge.com', 16000000, 75000000, TRUE),
('util_ny_coned', 'Consolidated Edison Company of New York', 'Con Edison', 'Investor-Owned', 'NY', 'New York City and Westchester County', 'EIA_11109', 'CONED', 'https://www.coned.com', 3600000, 28000000, TRUE),
('util_tx_reliant', 'Reliant Energy', 'Reliant', 'Power Marketer', 'TX', 'Texas competitive market', 'EIA_17261', 'RELIANT', 'https://www.reliant.com', 1500000, 12000000, TRUE),
('util_fl_fpl', 'Florida Power & Light Company', 'FPL', 'Investor-Owned', 'FL', 'Southeast Florida', 'EIA_10259', 'FPL', 'https://www.fpl.com', 5100000, 90000000, TRUE),
('util_il_comed', 'Commonwealth Edison Company', 'ComEd', 'Investor-Owned', 'IL', 'Northern Illinois including Chicago', 'EIA_10141', 'COMED', 'https://www.comed.com', 4000000, 70000000, TRUE),
('util_pa_peco', 'PECO Energy Company', 'PECO', 'Investor-Owned', 'PA', 'Southeastern Pennsylvania', 'EIA_14341', 'PECO', 'https://www.peco.com', 1600000, 25000000, TRUE),
('util_oh_firstenergy', 'FirstEnergy Corp', 'FirstEnergy', 'Investor-Owned', 'OH', 'Northern Ohio', 'EIA_10260', 'FE', 'https://www.firstenergycorp.com', 6000000, 85000000, TRUE),
('util_ga_georgia_power', 'Georgia Power Company', 'Georgia Power', 'Investor-Owned', 'GA', 'Statewide Georgia', 'EIA_10261', 'GPC', 'https://www.georgiapower.com', 2600000, 72000000, TRUE),
('util_nc_duke', 'Duke Energy Carolinas', 'Duke Energy', 'Investor-Owned', 'NC', 'North and South Carolina', 'EIA_10262', 'DUKE', 'https://www.duke-energy.com', 7700000, 150000000, TRUE),
('util_mi_dte', 'DTE Electric Company', 'DTE Energy', 'Investor-Owned', 'MI', 'Southeastern Michigan', 'EIA_10263', 'DTE', 'https://www.dteenergy.com', 2200000, 50000000, TRUE);

-- Insert sample rate codes
INSERT INTO rate_codes (rate_code_id, rate_code, rate_code_description, rate_code_category, sector, rate_structure_type, is_active) VALUES
('rc_res_1', 'R-1', 'Residential Standard Rate', 'Residential', 'Residential', 'Flat', TRUE),
('rc_res_2', 'R-2', 'Residential Time-of-Use Rate', 'Residential', 'Residential', 'Time-of-Use', TRUE),
('rc_res_3', 'R-3', 'Residential Tiered Rate', 'Residential', 'Residential', 'Tiered', TRUE),
('rc_com_1', 'GS-1', 'General Service Small Commercial', 'Commercial', 'Commercial', 'Flat', TRUE),
('rc_com_2', 'GS-2', 'General Service Large Commercial', 'Commercial', 'Commercial', 'Demand', TRUE),
('rc_com_3', 'GS-3', 'Commercial Time-of-Use', 'Commercial', 'Commercial', 'Time-of-Use', TRUE),
('rc_ind_1', 'E-1', 'Industrial Standard Rate', 'Industrial', 'Industrial', 'Demand', TRUE),
('rc_ind_2', 'E-2', 'Industrial Time-of-Use Rate', 'Industrial', 'Industrial', 'Time-of-Use', TRUE),
('rc_ag_1', 'AG-1', 'Agricultural Rate', 'Agricultural', 'Agricultural', 'Flat', TRUE),
('rc_light_1', 'L-1', 'Street Lighting Rate', 'Lighting', 'Lighting', 'Flat', TRUE);


-- Insert sample rate structures (must exist before electricity_rates)
INSERT INTO rate_structures (rate_structure_id, utility_id, rate_code_id, rate_name, rate_description, effective_date, expiration_date, approval_status, regulatory_authority, is_current) VALUES
('rs_001', 'util_ca_pge', 'rc_res_1', 'PG&E Residential Flat', 'Single rate per kWh', '2024-01-01', '2024-12-31', 'Approved', 'CPUC', TRUE),
('rs_002', 'util_ca_pge', 'rc_res_2', 'PG&E Residential TOU', 'Time-of-use rates', '2024-01-01', '2024-12-31', 'Approved', 'CPUC', TRUE),
('rs_003', 'util_ny_coned', 'rc_res_1', 'ConEd Residential', 'Standard residential rate', '2024-01-01', '2024-12-31', 'Approved', 'NYPSC', TRUE),
('rs_004', 'util_tx_reliant', 'rc_res_1', 'Reliant Residential', 'Residential rate plan', '2024-01-01', '2024-12-31', 'Approved', 'PUCT', TRUE),
('rs_005', 'util_fl_fpl', 'rc_res_1', 'FPL Residential', 'Residential rate', '2024-01-01', '2024-12-31', 'Approved', 'FPSC', TRUE),
('rs_006', 'util_il_comed', 'rc_res_1', 'ComEd Residential', 'Residential rate', '2024-01-01', '2024-12-31', 'Approved', 'ICC', TRUE);

-- Insert sample electricity rates (schema columns: rate_id, rate_structure_id, utility_id, rate_code_id, state_id, rate_type, billing_period, fixed_charge_usd, energy_charge_usd_per_kwh, demand_charge_usd_per_kw, effective_date, expiration_date, is_current, data_source)
INSERT INTO electricity_rates (rate_id, rate_structure_id, utility_id, rate_code_id, state_id, rate_type, billing_period, fixed_charge_usd, energy_charge_usd_per_kwh, demand_charge_usd_per_kw, effective_date, expiration_date, is_current, data_source) VALUES
('rate_001', 'rs_001', 'util_ca_pge', 'rc_res_1', 'CA', 'Residential', 'Monthly', 10.00, 0.32, NULL, '2024-01-01', '2024-12-31', TRUE, 'openei'),
('rate_002', 'rs_002', 'util_ca_pge', 'rc_res_2', 'CA', 'Residential', 'Monthly', 10.00, 0.36, NULL, '2024-01-01', '2024-12-31', TRUE, 'openei'),
('rate_003', 'rs_003', 'util_ny_coned', 'rc_res_1', 'NY', 'Residential', 'Monthly', 19.50, 0.18, NULL, '2024-01-01', '2024-12-31', TRUE, 'openei'),
('rate_004', 'rs_004', 'util_tx_reliant', 'rc_res_1', 'TX', 'Residential', 'Monthly', 9.95, 0.12, NULL, '2024-01-01', '2024-12-31', TRUE, 'openei'),
('rate_005', 'rs_005', 'util_fl_fpl', 'rc_res_1', 'FL', 'Residential', 'Monthly', 8.50, 0.11, NULL, '2024-01-01', '2024-12-31', TRUE, 'openei'),
('rate_006', 'rs_006', 'util_il_comed', 'rc_res_1', 'IL', 'Residential', 'Monthly', 15.00, 0.08, NULL, '2024-01-01', '2024-12-31', TRUE, 'openei');

-- Insert sample tiered rate tiers (schema: tier_id, rate_structure_id, tier_number, tier_start_kwh, tier_end_kwh, energy_charge_usd_per_kwh, effective_date)
INSERT INTO tiered_rate_tiers (tier_id, rate_structure_id, tier_number, tier_start_kwh, tier_end_kwh, energy_charge_usd_per_kwh, effective_date) VALUES
('tier_001_1', 'rs_001', 1, 0, 350, 0.28, '2024-01-01'),
('tier_001_2', 'rs_001', 2, 351, 700, 0.35, '2024-01-01'),
('tier_001_3', 'rs_001', 3, 701, NULL, 0.42, '2024-01-01'),
('tier_003_1', 'rs_003', 1, 0, NULL, 0.18, '2024-01-01');

-- Insert sample time-of-use periods (schema: tou_period_id, rate_structure_id, period_name, period_start_time, period_end_time, day_of_week, energy_charge_usd_per_kwh, effective_date)
INSERT INTO time_of_use_periods (tou_period_id, rate_structure_id, period_name, period_start_time, period_end_time, day_of_week, energy_charge_usd_per_kwh, effective_date) VALUES
('tou_002_peak', 'rs_002', 'Peak Hours', '16:00:00', '21:00:00', 'Weekday', 0.45, '2024-01-01'),
('tou_002_offpeak', 'rs_002', 'Off-Peak Hours', '21:00:00', '16:00:00', 'Weekday', 0.28, '2024-01-01'),
('tou_002_weekend', 'rs_002', 'Weekend Hours', '00:00:00', '23:59:59', 'Weekend', 0.28, '2024-01-01');

-- Insert sample geographic rate areas (schema: rate_area_id, rate_structure_id, state_id, county_id, zip_code, service_area_name, effective_date, expiration_date)
INSERT INTO geographic_rate_areas (rate_area_id, rate_structure_id, state_id, county_id, zip_code, service_area_name, effective_date, expiration_date) VALUES
('area_001', 'rs_001', 'CA', 'ca_los_angeles', '90001', 'PG&E Northern California', '2024-01-01', '2024-12-31'),
('area_002', 'rs_003', 'NY', 'ny_new_york', '10001', 'ConEd New York City', '2024-01-01', '2024-12-31'),
('area_003', 'rs_004', 'TX', 'tx_harris', '77001', 'Reliant Houston', '2024-01-01', '2024-12-31'),
('area_004', 'rs_005', 'FL', 'fl_miami_dade', '33101', 'FPL Miami-Dade', '2024-01-01', '2024-12-31'),
('area_005', 'rs_006', 'IL', 'il_cook', '60601', 'ComEd Chicago', '2024-01-01', '2024-12-31');

-- Insert sample historical electricity rates (schema: historical_rate_id, rate_id, utility_id, rate_code_id, state_id, effective_date, change_type, fixed_charge_usd, energy_charge_usd_per_kwh, demand_charge_usd_per_kw)
INSERT INTO historical_electricity_rates (historical_rate_id, rate_id, utility_id, rate_code_id, state_id, effective_date, change_type, fixed_charge_usd, energy_charge_usd_per_kwh, demand_charge_usd_per_kw) VALUES
('hist_001', 'rate_001', 'util_ca_pge', 'rc_res_1', 'CA', '2023-01-01', 'rate_expired', 10.00, 0.30, NULL),
('hist_002', 'rate_001', 'util_ca_pge', 'rc_res_1', 'CA', '2022-01-01', 'rate_expired', 10.00, 0.28, NULL),
('hist_003', 'rate_003', 'util_ny_coned', 'rc_res_1', 'NY', '2023-01-01', 'rate_expired', 19.50, 0.17, NULL),
('hist_004', 'rate_003', 'util_ny_coned', 'rc_res_1', 'NY', '2022-01-01', 'rate_expired', 19.50, 0.16, NULL),
('hist_005', 'rate_004', 'util_tx_reliant', 'rc_res_1', 'TX', '2023-01-01', 'rate_expired', 9.95, 0.11, NULL);


-- Insert sample federal incentives
INSERT INTO federal_incentives (federal_incentive_id, incentive_name, incentive_type, incentive_description, eligible_technologies, eligible_sectors, incentive_amount_usd, incentive_percentage, incentive_unit, maximum_incentive_usd, minimum_system_size_kw, maximum_system_size_kw, effective_date, expiration_date, is_active, program_website_url, data_source) VALUES
('fed_001', 'Solar Investment Tax Credit (ITC)', 'Tax Credit', '30% federal tax credit for solar installations', ARRAY['Solar PV', 'Solar Thermal'], ARRAY['Residential', 'Commercial'], NULL, 30.00, 'percentage', NULL, NULL, NULL, '2022-01-01', '2032-12-31', TRUE, 'https://www.energy.gov/eere/solar/homeowners-guide-federal-tax-credit-solar-photovoltaics', 'doe'),
('fed_002', 'Residential Energy Efficient Property Credit', 'Tax Credit', 'Tax credit for residential energy efficient property', ARRAY['Solar PV', 'Solar Water Heating', 'Geothermal Heat Pumps'], ARRAY['Residential'], NULL, 30.00, 'percentage', NULL, NULL, NULL, '2022-01-01', '2032-12-31', TRUE, 'https://www.irs.gov/credits-deductions/residential-energy-efficient-property-credit', 'irs');

-- Insert sample state incentives
INSERT INTO state_incentives (state_incentive_id, state_id, incentive_name, incentive_type, incentive_description, eligible_technologies, eligible_sectors, incentive_amount_usd, incentive_percentage, incentive_unit, maximum_incentive_usd, minimum_system_size_kw, maximum_system_size_kw, effective_date, expiration_date, is_active, program_website_url, regulatory_authority, data_source) VALUES
('state_ca_001', 'CA', 'California Solar Initiative', 'Rebate', 'State rebate program for residential solar', ARRAY['Solar PV'], ARRAY['Residential'], 0.25, NULL, 'per_watt', 5000.00, NULL, NULL, '2007-01-01', NULL, TRUE, 'https://www.cpuc.ca.gov/solar', 'California Public Utilities Commission', 'dsire'),
('state_ny_001', 'NY', 'NY-Sun Incentive Program', 'Rebate', 'New York state solar incentive program', ARRAY['Solar PV'], ARRAY['Residential', 'Commercial'], 0.50, NULL, 'per_watt', 10000.00, NULL, NULL, '2014-01-01', '2025-12-31', TRUE, 'https://www.nyserda.ny.gov/All-Programs/Programs/NY-Sun', 'New York State Energy Research and Development Authority', 'dsire'),
('state_tx_001', 'TX', 'Texas Solar Rebate Program', 'Rebate', 'Texas state solar rebate program', ARRAY['Solar PV'], ARRAY['Residential'], 0.15, NULL, 'per_watt', 2500.00, NULL, NULL, '2021-01-01', '2026-12-31', TRUE, 'https://www.texas.gov/solar', 'Texas State Energy Conservation Office', 'dsire'),
('state_fl_001', 'FL', 'Florida Solar Rebate', 'Rebate', 'Florida state solar rebate program', ARRAY['Solar PV'], ARRAY['Residential'], 0.10, NULL, 'per_watt', 2000.00, NULL, NULL, '2022-01-01', '2025-12-31', TRUE, 'https://www.florida.gov/solar', 'Florida Department of Agriculture and Consumer Services', 'dsire'),
('state_il_001', 'IL', 'Illinois Solar Rebate', 'Rebate', 'Illinois state solar rebate program', ARRAY['Solar PV'], ARRAY['Residential'], 0.18, NULL, 'per_watt', 4000.00, NULL, NULL, '2020-01-01', '2024-12-31', TRUE, 'https://www.illinois.gov/solar', 'Illinois Power Agency', 'dsire');

-- Insert sample utility incentives
INSERT INTO utility_incentives (utility_incentive_id, utility_id, state_id, incentive_name, incentive_type, incentive_description, eligible_technologies, eligible_sectors, incentive_amount_usd, incentive_percentage, incentive_unit, maximum_incentive_usd, minimum_system_size_kw, maximum_system_size_kw, net_metering_capacity_limit_kw, feed_in_tariff_rate_usd_per_kwh, effective_date, expiration_date, is_active, program_website_url, data_source) VALUES
('util_ca_pge_001', 'util_ca_pge', 'CA', 'PG&E Solar Rebate', 'Rebate', 'PG&E utility-specific solar rebate', ARRAY['Solar PV'], ARRAY['Residential', 'Commercial'], 0.20, NULL, 'per_watt', 3000.00, NULL, NULL, NULL, NULL, '2020-01-01', '2025-12-31', TRUE, 'https://www.pge.com/solar', 'utility_website'),
('util_ny_coned_001', 'util_ny_coned', 'NY', 'ConEd Solar Rebate', 'Rebate', 'ConEd utility-specific solar rebate', ARRAY['Solar PV'], ARRAY['Residential', 'Commercial'], 0.30, NULL, 'per_watt', 5000.00, NULL, NULL, NULL, NULL, '2019-01-01', '2024-12-31', TRUE, 'https://www.coned.com/solar', 'utility_website'),
('util_ca_pge_002', 'util_ca_pge', 'CA', 'PG&E Net Metering', 'Net Metering', 'Net metering program for solar customers', ARRAY['Solar PV'], ARRAY['Residential', 'Commercial'], NULL, NULL, 'per_kwh', NULL, NULL, 1000.00, 1000.00, NULL, '2020-01-01', NULL, TRUE, 'https://www.pge.com/netmetering', 'utility_website'),
('util_ny_coned_002', 'util_ny_coned', 'NY', 'ConEd Net Metering', 'Net Metering', 'Net metering program for solar customers', ARRAY['Solar PV'], ARRAY['Residential', 'Commercial'], NULL, NULL, 'per_kwh', NULL, NULL, 2000.00, 2000.00, NULL, '2019-01-01', NULL, TRUE, 'https://www.coned.com/netmetering', 'utility_website');

-- Insert sample solar rebate aggregations
INSERT INTO solar_rebate_aggregations (aggregation_id, state_id, utility_id, zip_code, total_federal_incentives_usd, total_state_incentives_usd, total_utility_incentives_usd, total_combined_incentives_usd, federal_incentive_count, state_incentive_count, utility_incentive_count, total_incentive_count, calculation_date) VALUES
('agg_001', 'CA', 'util_ca_pge', '90001', 3000.00, 2500.00, 2000.00, 7500.00, 1, 1, 1, 3, '2024-01-01'),
('agg_002', 'NY', 'util_ny_coned', '10001', 3000.00, 5000.00, 3000.00, 11000.00, 1, 1, 1, 3, '2024-01-01'),
('agg_003', 'TX', 'util_tx_reliant', '77001', 3000.00, 1500.00, NULL, 4500.00, 1, 1, 0, 2, '2024-01-01'),
('agg_004', 'FL', 'util_fl_fpl', '33101', 3000.00, 1000.00, NULL, 4000.00, 1, 1, 0, 2, '2024-01-01'),
('agg_005', 'IL', 'util_il_comed', '60601', 3000.00, 1800.00, NULL, 4800.00, 1, 1, 0, 2, '2024-01-01');

-- Insert sample rate comparison matrix
INSERT INTO rate_comparison_matrix (comparison_id, rate_id_1, rate_id_2, comparison_metric, usage_kwh_per_month, rate_1_cost_usd, rate_2_cost_usd, cost_difference_usd, cost_difference_percentage, comparison_date) VALUES
('comp_001', 'rate_001', 'rate_003', 'total_monthly_cost', 500.00, 170.00, 109.50, 60.50, 55.25, '2024-01-01'),
('comp_002', 'rate_001', 'rate_004', 'total_monthly_cost', 500.00, 170.00, 69.95, 100.05, 143.00, '2024-01-01'),
('comp_003', 'rate_003', 'rate_004', 'total_monthly_cost', 500.00, 109.50, 69.95, 39.55, 56.55, '2024-01-01'),
('comp_004', 'rate_005', 'rate_006', 'total_monthly_cost', 500.00, 63.50, 55.00, 8.50, 15.45, '2024-01-01'),
('comp_005', 'rate_001', 'rate_002', 'total_monthly_cost', 500.00, 170.00, 145.00, 25.00, 17.24, '2024-01-01');

-- Insert sample data extraction log (schema: extraction_id, source_id, source_name, extraction_type, extraction_status, records_extracted, records_loaded, records_failed, extraction_start_time, extraction_end_time, error_message)
INSERT INTO data_extraction_log (extraction_id, source_id, source_name, extraction_type, extraction_status, records_extracted, records_loaded, records_failed, extraction_start_time, extraction_end_time, error_message) VALUES
('ext_001', 'openei_utility_rates', 'OpenEI Utility Rates API', 'api', 'success', 150, 150, 0, '2024-01-01 10:00:00', '2024-01-01 10:15:00', NULL),
('ext_002', 'eia_form_861', 'EIA Form 861', 'file_download', 'success', 3700, 3700, 0, '2024-01-01 11:00:00', '2024-01-01 11:30:00', NULL),
('ext_003', 'dsire_solar_rebates', 'DSIRE Solar Rebates', 'api', 'success', 250, 250, 0, '2024-01-01 12:00:00', '2024-01-01 12:20:00', NULL),
('ext_004', 'doe_tax_credits', 'DOE Tax Credits', 'web_scrape', 'success', 5, 5, 0, '2024-01-01 13:00:00', '2024-01-01 13:10:00', NULL),
('ext_005', 'state_commissions', 'State Utility Commissions', 'web_scrape', 'partial', 100, 95, 5, '2024-01-01 14:00:00', '2024-01-01 15:00:00', '5 records failed validation');

