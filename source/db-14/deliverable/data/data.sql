-- Sample Data for Cloud Instance Cost Database
-- Compatible with PostgreSQL
-- Production sample data for cloud instance cost system
--
-- NOTE: For a full 1+ GB dataset extracted from real internet sources,
-- see data_large.sql which contains 2.7+ million records.
-- This file contains a smaller sample dataset for quick testing.

-- Insert sample cloud providers
INSERT INTO cloud_providers (provider_id, provider_name, provider_display_name, api_base_url, pricing_api_endpoint, documentation_url, data_source, update_frequency, data_quality_score) VALUES
('aws', 'AWS', 'Amazon Web Services', 'https://pricing.us-east-1.amazonaws.com', '/offers/v1.0/aws/index.json', 'https://aws.amazon.com/pricing/', 'vantage.sh', 'daily', 95.00),
('gcp', 'GCP', 'Google Cloud Platform', 'https://cloudbilling.googleapis.com', '/v1/services', 'https://cloud.google.com/pricing/', 'vantage.sh', 'daily', 92.50),
('azure', 'Azure', 'Microsoft Azure', 'https://prices.azure.com/api/retail', '/prices', 'https://azure.microsoft.com/pricing/', 'vantage.sh', 'daily', 90.00);

-- Insert sample cloud regions (AWS)
INSERT INTO cloud_regions (region_id, provider_id, region_code, region_name, region_display_name, country_code, continent, timezone, is_active, launch_date, data_center_count, availability_zones_count) VALUES
('aws-us-east-1', 'aws', 'us-east-1', 'US East (N. Virginia)', 'US East (N. Virginia)', 'US', 'North America', 'America/New_York', TRUE, '2006-08-25', 6, 6),
('aws-us-west-2', 'aws', 'us-west-2', 'US West (Oregon)', 'US West (Oregon)', 'US', 'North America', 'America/Los_Angeles', TRUE, '2011-11-09', 4, 4),
('aws-eu-west-1', 'aws', 'eu-west-1', 'Europe (Ireland)', 'Europe (Ireland)', 'IE', 'Europe', 'Europe/Dublin', TRUE, '2006-12-13', 3, 3),
('aws-ap-southeast-1', 'aws', 'ap-southeast-1', 'Asia Pacific (Singapore)', 'Asia Pacific (Singapore)', 'SG', 'Asia', 'Asia/Singapore', TRUE, '2010-04-29', 2, 2);

-- Insert sample cloud regions (GCP)
INSERT INTO cloud_regions (region_id, provider_id, region_code, region_name, region_display_name, country_code, continent, timezone, is_active, launch_date, data_center_count, availability_zones_count) VALUES
('gcp-us-central1', 'gcp', 'us-central1', 'US Central (Iowa)', 'US Central (Iowa)', 'US', 'North America', 'America/Chicago', TRUE, '2014-06-25', 3, 3),
('gcp-us-west1', 'gcp', 'us-west1', 'US West (Oregon)', 'US West (Oregon)', 'US', 'North America', 'America/Los_Angeles', TRUE, '2014-06-25', 2, 2),
('gcp-europe-west1', 'gcp', 'europe-west1', 'Europe (Belgium)', 'Europe (Belgium)', 'BE', 'Europe', 'Europe/Brussels', TRUE, '2014-06-25', 2, 2),
('gcp-asia-east1', 'gcp', 'asia-east1', 'Asia Pacific (Taiwan)', 'Asia Pacific (Taiwan)', 'TW', 'Asia', 'Asia/Taipei', TRUE, '2014-06-25', 2, 2);

-- Insert sample cloud regions (Azure)
INSERT INTO cloud_regions (region_id, provider_id, region_code, region_name, region_display_name, country_code, continent, timezone, is_active, launch_date, data_center_count, availability_zones_count) VALUES
('azure-eastus', 'azure', 'eastus', 'East US', 'East US', 'US', 'North America', 'America/New_York', TRUE, '2014-04-01', 3, 3),
('azure-westus2', 'azure', 'westus2', 'West US 2', 'West US 2', 'US', 'North America', 'America/Los_Angeles', TRUE, '2016-09-15', 2, 2),
('azure-westeurope', 'azure', 'westeurope', 'West Europe', 'West Europe', 'NL', 'Europe', 'Europe/Amsterdam', TRUE, '2014-04-01', 2, 2),
('azure-southeastasia', 'azure', 'southeastasia', 'Southeast Asia', 'Southeast Asia', 'SG', 'Asia', 'Asia/Singapore', TRUE, '2014-04-01', 2, 2);

-- Insert sample instance families (AWS)
INSERT INTO instance_families (family_id, provider_id, family_name, family_code, family_description, use_case_category, target_workloads) VALUES
('aws-m5', 'aws', 'General Purpose', 'm5', 'General purpose instances with balanced compute, memory, and networking', 'General Purpose', 'Web servers, small databases, development environments'),
('aws-c5', 'aws', 'Compute Optimized', 'c5', 'Compute-optimized instances with high-performance processors', 'Compute Optimized', 'Batch processing, high-performance computing, scientific modeling'),
('aws-r5', 'aws', 'Memory Optimized', 'r5', 'Memory-optimized instances for memory-intensive workloads', 'Memory Optimized', 'In-memory databases, real-time analytics, caching');

-- Insert sample instance families (GCP)
INSERT INTO instance_families (family_id, provider_id, family_name, family_code, family_description, use_case_category, target_workloads) VALUES
('gcp-n1', 'gcp', 'General Purpose', 'n1', 'General purpose instances with balanced resources', 'General Purpose', 'Web applications, small databases, development'),
('gcp-c2', 'gcp', 'Compute Optimized', 'c2', 'Compute-optimized instances with high CPU performance', 'Compute Optimized', 'CPU-intensive workloads, batch processing, HPC'),
('gcp-m1', 'gcp', 'Memory Optimized', 'm1', 'Memory-optimized instances for memory-intensive applications', 'Memory Optimized', 'In-memory databases, analytics, caching');

-- Insert sample instance families (Azure)
INSERT INTO instance_families (family_id, provider_id, family_name, family_code, family_description, use_case_category, target_workloads) VALUES
('azure-dsv3', 'azure', 'General Purpose', 'Dsv3', 'General purpose instances with balanced CPU and memory', 'General Purpose', 'Web servers, small databases, development'),
('azure-fsv2', 'azure', 'Compute Optimized', 'Fsv2', 'Compute-optimized instances with high CPU performance', 'Compute Optimized', 'Batch processing, HPC, scientific computing'),
('azure-esv3', 'azure', 'Memory Optimized', 'Esv3', 'Memory-optimized instances for memory-intensive workloads', 'Memory Optimized', 'In-memory databases, analytics, caching');

-- Insert sample cloud instances (AWS)
INSERT INTO cloud_instances (instance_id, provider_id, instance_name, api_name, instance_family_id, region_id, vcpus, memory_gb, memory_mb, instance_storage_gb, instance_storage_type, network_performance, network_bandwidth_gbps, ebs_optimized, gpu_count, architecture, processor_type, processor_speed_ghz, is_current_generation, is_available, launch_date) VALUES
('aws-m5-large-us-east-1', 'aws', 'm5.large', 'm5.large', 'aws-m5', 'aws-us-east-1', 2, 8.0, 8192, 0, 'EBS', 'Up to 10 Gigabit', 10.0, TRUE, 0, 'x86_64', 'Intel Xeon Platinum 8175M', 2.5, TRUE, TRUE, '2017-11-20'),
('aws-m5-xlarge-us-east-1', 'aws', 'm5.xlarge', 'm5.xlarge', 'aws-m5', 'aws-us-east-1', 4, 16.0, 16384, 0, 'EBS', 'Up to 10 Gigabit', 10.0, TRUE, 0, 'x86_64', 'Intel Xeon Platinum 8175M', 2.5, TRUE, TRUE, '2017-11-20'),
('aws-c5-large-us-east-1', 'aws', 'c5.large', 'c5.large', 'aws-c5', 'aws-us-east-1', 2, 4.0, 4096, 0, 'EBS', 'Up to 10 Gigabit', 10.0, TRUE, 0, 'x86_64', 'Intel Xeon Platinum 8124M', 3.5, TRUE, TRUE, '2017-11-20'),
('aws-r5-large-us-east-1', 'aws', 'r5.large', 'r5.large', 'aws-r5', 'aws-us-east-1', 2, 16.0, 16384, 0, 'EBS', 'Up to 10 Gigabit', 10.0, TRUE, 0, 'x86_64', 'Intel Xeon Platinum 8175M', 2.5, TRUE, TRUE, '2017-11-20');

-- Insert sample cloud instances (GCP)
INSERT INTO cloud_instances (instance_id, provider_id, instance_name, api_name, instance_family_id, region_id, vcpus, memory_gb, memory_mb, instance_storage_gb, instance_storage_type, network_performance, network_bandwidth_gbps, ebs_optimized, gpu_count, architecture, processor_type, processor_speed_ghz, is_current_generation, is_available, launch_date) VALUES
('gcp-n1-standard-2-us-central1', 'gcp', 'n1-standard-2', 'n1-standard-2', 'gcp-n1', 'gcp-us-central1', 2, 7.5, 7680, 0, 'Persistent Disk', '1 Gbps', 1.0, FALSE, 0, 'x86_64', 'Intel Skylake', 2.0, TRUE, TRUE, '2014-06-25'),
('gcp-n1-standard-4-us-central1', 'gcp', 'n1-standard-4', 'n1-standard-4', 'gcp-n1', 'gcp-us-central1', 4, 15.0, 15360, 0, 'Persistent Disk', '2 Gbps', 2.0, FALSE, 0, 'x86_64', 'Intel Skylake', 2.0, TRUE, TRUE, '2014-06-25'),
('gcp-c2-standard-4-us-central1', 'gcp', 'c2-standard-4', 'c2-standard-4', 'gcp-c2', 'gcp-us-central1', 4, 16.0, 16384, 0, 'Persistent Disk', '10 Gbps', 10.0, FALSE, 0, 'x86_64', 'Intel Cascade Lake', 3.8, TRUE, TRUE, '2019-08-20'),
('gcp-m1-megamem-4-us-central1', 'gcp', 'm1-megamem-4', 'm1-megamem-4', 'gcp-m1', 'gcp-us-central1', 4, 96.0, 98304, 0, 'Persistent Disk', '10 Gbps', 10.0, FALSE, 0, 'x86_64', 'Intel Skylake', 2.0, TRUE, TRUE, '2014-06-25');

-- Insert sample cloud instances (Azure)
INSERT INTO cloud_instances (instance_id, provider_id, instance_name, api_name, instance_family_id, region_id, vcpus, memory_gb, memory_mb, instance_storage_gb, instance_storage_type, network_performance, network_bandwidth_gbps, ebs_optimized, gpu_count, architecture, processor_type, processor_speed_ghz, is_current_generation, is_available, launch_date) VALUES
('azure-d2s-v3-eastus', 'azure', 'Standard_D2s_v3', 'Standard_D2s_v3', 'azure-dsv3', 'azure-eastus', 2, 8.0, 8192, 16, 'SSD', 'Moderate', 1.0, FALSE, 0, 'x86_64', 'Intel Xeon E5-2673 v4', 2.3, TRUE, TRUE, '2017-12-01'),
('azure-d4s-v3-eastus', 'azure', 'Standard_D4s_v3', 'Standard_D4s_v3', 'azure-dsv3', 'azure-eastus', 4, 16.0, 16384, 32, 'SSD', 'Moderate', 2.0, FALSE, 0, 'x86_64', 'Intel Xeon E5-2673 v4', 2.3, TRUE, TRUE, '2017-12-01'),
('azure-f2s-v2-eastus', 'azure', 'Standard_F2s_v2', 'Standard_F2s_v2', 'azure-fsv2', 'azure-eastus', 2, 4.0, 4096, 16, 'SSD', 'Moderate', 1.0, FALSE, 0, 'x86_64', 'Intel Xeon Platinum 8168', 2.7, TRUE, TRUE, '2017-12-01'),
('azure-e2s-v3-eastus', 'azure', 'Standard_E2s_v3', 'Standard_E2s_v3', 'azure-esv3', 'azure-eastus', 2, 16.0, 16384, 32, 'SSD', 'Moderate', 1.0, FALSE, 0, 'x86_64', 'Intel Xeon E5-2673 v4', 2.3, TRUE, TRUE, '2017-12-01');

-- Insert sample instance performance metrics (CoreMark scores)
INSERT INTO instance_performance_metrics (metric_id, instance_id, benchmark_name, benchmark_score, benchmark_score_normalized, benchmark_version, test_date, test_environment, source, confidence_level) VALUES
('perf-aws-m5-large-coremark', 'aws-m5-large-us-east-1', 'CoreMark', 24500.00, 24500.00, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 95.00),
('perf-aws-m5-xlarge-coremark', 'aws-m5-xlarge-us-east-1', 'CoreMark', 49000.00, 49000.00, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 95.00),
('perf-aws-c5-large-coremark', 'aws-c5-large-us-east-1', 'CoreMark', 28000.00, 28000.00, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 95.00),
('perf-gcp-n1-standard-2-coremark', 'gcp-n1-standard-2-us-central1', 'CoreMark', 22000.00, 22000.00, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 92.50),
('perf-gcp-c2-standard-4-coremark', 'gcp-c2-standard-4-us-central1', 'CoreMark', 52000.00, 52000.00, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 95.00),
('perf-azure-d2s-v3-coremark', 'azure-d2s-v3-eastus', 'CoreMark', 23000.00, 23000.00, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 90.00);

-- Insert sample instance performance metrics (FFmpeg FPS scores)
INSERT INTO instance_performance_metrics (metric_id, instance_id, benchmark_name, benchmark_score, benchmark_score_normalized, benchmark_version, test_date, test_environment, source, confidence_level) VALUES
('perf-aws-m5-large-ffmpeg', 'aws-m5-large-us-east-1', 'FFmpeg FPS', 45.5, 45.5, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 95.00),
('perf-aws-m5-xlarge-ffmpeg', 'aws-m5-xlarge-us-east-1', 'FFmpeg FPS', 91.0, 91.0, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 95.00),
('perf-aws-c5-large-ffmpeg', 'aws-c5-large-us-east-1', 'FFmpeg FPS', 52.0, 52.0, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 95.00),
('perf-gcp-n1-standard-2-ffmpeg', 'gcp-n1-standard-2-us-central1', 'FFmpeg FPS', 42.0, 42.0, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 92.50),
('perf-gcp-c2-standard-4-ffmpeg', 'gcp-c2-standard-4-us-central1', 'FFmpeg FPS', 98.0, 98.0, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 95.00),
('perf-azure-d2s-v3-ffmpeg', 'azure-d2s-v3-eastus', 'FFmpeg FPS', 44.0, 44.0, '1.0', '2026-01-15', 'Linux Ubuntu 22.04', 'vantage.sh', 90.00);

-- Insert sample instance pricing (on-demand Linux)
INSERT INTO instance_pricing (pricing_id, instance_id, region_id, pricing_model, operating_system, currency, price_per_hour, price_per_month, price_per_year, is_current) VALUES
('price-aws-m5-large-ondemand', 'aws-m5-large-us-east-1', 'aws-us-east-1', 'on_demand', 'Linux', 'USD', 0.096000, 70.08, 840.96, TRUE),
('price-aws-m5-xlarge-ondemand', 'aws-m5-xlarge-us-east-1', 'aws-us-east-1', 'on_demand', 'Linux', 'USD', 0.192000, 140.16, 1681.92, TRUE),
('price-aws-c5-large-ondemand', 'aws-c5-large-us-east-1', 'aws-us-east-1', 'on_demand', 'Linux', 'USD', 0.085000, 62.05, 744.60, TRUE),
('price-gcp-n1-standard-2-ondemand', 'gcp-n1-standard-2-us-central1', 'gcp-us-central1', 'on_demand', 'Linux', 'USD', 0.095000, 69.35, 832.20, TRUE),
('price-gcp-c2-standard-4-ondemand', 'gcp-c2-standard-4-us-central1', 'gcp-us-central1', 'on_demand', 'Linux', 'USD', 0.208900, 152.50, 1830.00, TRUE),
('price-azure-d2s-v3-ondemand', 'azure-d2s-v3-eastus', 'azure-eastus', 'on_demand', 'Linux', 'USD', 0.096000, 70.08, 840.96, TRUE);

-- Insert sample instance pricing (reserved 1-year)
INSERT INTO instance_pricing (pricing_id, instance_id, region_id, pricing_model, operating_system, currency, price_per_hour, price_per_month, price_per_year, upfront_cost, effective_hourly_cost, discount_percentage, term_length_months, payment_option, is_current) VALUES
('price-aws-m5-large-reserved-1yr', 'aws-m5-large-us-east-1', 'aws-us-east-1', 'reserved_1yr', 'Linux', 'USD', 0.060480, 44.15, 529.80, 0, 0.060480, 37.00, 12, 'no_upfront', TRUE),
('price-aws-m5-xlarge-reserved-1yr', 'aws-m5-xlarge-us-east-1', 'aws-us-east-1', 'reserved_1yr', 'Linux', 'USD', 0.120960, 88.30, 1059.60, 0, 0.120960, 37.00, 12, 'no_upfront', TRUE),
('price-aws-c5-large-reserved-1yr', 'aws-c5-large-us-east-1', 'aws-us-east-1', 'reserved_1yr', 'Linux', 'USD', 0.053550, 39.09, 469.08, 0, 0.053550, 37.00, 12, 'no_upfront', TRUE);

-- Insert sample instance pricing (spot)
INSERT INTO instance_pricing (pricing_id, instance_id, region_id, pricing_model, operating_system, currency, price_per_hour, is_current) VALUES
('price-aws-m5-large-spot', 'aws-m5-large-us-east-1', 'aws-us-east-1', 'spot', 'Linux', 'USD', 0.028800, TRUE),
('price-aws-m5-xlarge-spot', 'aws-m5-xlarge-us-east-1', 'aws-us-east-1', 'spot', 'Linux', 'USD', 0.057600, TRUE),
('price-aws-c5-large-spot', 'aws-c5-large-us-east-1', 'aws-us-east-1', 'spot', 'Linux', 'USD', 0.025500, TRUE);

-- Insert sample historical pricing
INSERT INTO historical_pricing (historical_id, instance_id, region_id, pricing_model, operating_system, price_per_hour, price_change_percentage, price_change_amount, effective_date, change_type) VALUES
('hist-aws-m5-large-2025-01', 'aws-m5-large-us-east-1', 'aws-us-east-1', 'on_demand', 'Linux', 0.094000, -2.08, -0.002000, '2025-01-15', 'price_decrease'),
('hist-aws-m5-large-2025-06', 'aws-m5-large-us-east-1', 'aws-us-east-1', 'on_demand', 'Linux', 0.096000, 2.13, 0.002000, '2025-06-01', 'price_increase'),
('hist-aws-m5-xlarge-2025-01', 'aws-m5-xlarge-us-east-1', 'aws-us-east-1', 'on_demand', 'Linux', 0.188000, -2.08, -0.004000, '2025-01-15', 'price_decrease'),
('hist-aws-m5-xlarge-2025-06', 'aws-m5-xlarge-us-east-1', 'aws-us-east-1', 'on_demand', 'Linux', 0.192000, 2.13, 0.004000, '2025-06-01', 'price_increase');

-- Insert sample cost optimization recommendations
INSERT INTO cost_optimization_recommendations (recommendation_id, instance_id, target_instance_id, optimization_type, current_cost_per_month, recommended_cost_per_month, potential_savings_per_month, potential_savings_percentage, confidence_score, recommendation_reasoning, implementation_complexity, risk_level, workload_compatibility_score) VALUES
('rec-aws-m5-large-rightsize', 'aws-m5-xlarge-us-east-1', 'aws-m5-large-us-east-1', 'rightsizing', 140.16, 70.08, 70.08, 50.00, 85.00, 'Instance is over-provisioned. Current workload only uses 30% of resources. Rightsizing to m5.large would reduce costs by 50% with minimal performance impact.', 'low', 'low', 90.00),
('rec-aws-c5-large-reserved', 'aws-c5-large-us-east-1', 'aws-c5-large-us-east-1', 'reserved_instance', 62.05, 39.09, 22.96, 37.00, 95.00, 'Instance has consistent usage pattern. Switching to Reserved Instance (1-year, no upfront) would save 37% with no performance impact.', 'low', 'low', 100.00),
('rec-aws-m5-large-spot', 'aws-m5-large-us-east-1', 'aws-m5-large-us-east-1', 'spot_instance', 70.08, 21.02, 49.06, 70.00, 75.00, 'Workload is fault-tolerant and can handle interruptions. Using Spot Instances would save 70% but requires application-level fault tolerance.', 'medium', 'medium', 80.00);

-- Insert sample instance comparison matrix
INSERT INTO instance_comparison_matrix (comparison_id, instance_id_1, instance_id_2, comparison_metric, similarity_score, price_difference_percentage, performance_difference_percentage, vcpu_match, memory_match, comparison_date) VALUES
('comp-aws-gcp-m5-n1', 'aws-m5-large-us-east-1', 'gcp-n1-standard-2-us-central1', 'spec_match', 85.00, 1.05, 11.36, TRUE, FALSE, '2026-02-01'),
('comp-aws-azure-m5-d2s', 'aws-m5-large-us-east-1', 'azure-d2s-v3-eastus', 'spec_match', 95.00, 0.00, 6.52, TRUE, TRUE, '2026-02-01'),
('comp-gcp-azure-n1-d2s', 'gcp-n1-standard-2-us-central1', 'azure-d2s-v3-eastus', 'spec_match', 90.00, -1.05, -4.35, TRUE, FALSE, '2026-02-01');

-- Insert sample data extraction log
INSERT INTO data_extraction_log (extraction_id, source_name, source_url, extraction_type, provider_id, records_extracted, records_successful, records_failed, extraction_start_time, extraction_end_time, extraction_duration_seconds, data_size_mb, extraction_status) VALUES
('extract-vantage-20260201', 'vantage.sh', 'https://instances.vantage.sh/api/v1/instances', 'api', 'aws', 500, 495, 5, '2026-02-01 00:00:00', '2026-02-01 00:15:30', 930, 125.50, 'success'),
('extract-aws-api-20260201', 'aws_api', 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json', 'api', 'aws', 1000, 980, 20, '2026-02-01 01:00:00', '2026-02-01 01:45:00', 2700, 250.00, 'success'),
('extract-gcp-api-20260201', 'gcp_api', 'https://cloudbilling.googleapis.com/v1/services', 'api', 'gcp', 800, 790, 10, '2026-02-01 02:00:00', '2026-02-01 02:30:00', 1800, 180.00, 'success');

-- Insert sample cost analytics
INSERT INTO cost__analytics (analytics_id, provider_id, region_id, instance_family_id, metric_name, metric_value, metric_unit, calculation_date, sample_size, percentile_25, percentile_50, percentile_75, percentile_90, min_value, max_value) VALUES
('analytics-aws-us-east-1-m5-avg-price-vcpu', 'aws', 'aws-us-east-1', 'aws-m5', 'avg_price_per_vcpu', 0.048000, 'USD/hour', '2026-02-01', 50, 0.045000, 0.048000, 0.051000, 0.055000, 0.040000, 0.060000),
('analytics-gcp-us-central1-n1-avg-price-vcpu', 'gcp', 'gcp-us-central1', 'gcp-n1', 'avg_price_per_vcpu', 0.047500, 'USD/hour', '2026-02-01', 40, 0.044000, 0.047500, 0.050000, 0.053000, 0.042000, 0.055000),
('analytics-azure-eastus-dsv3-avg-price-vcpu', 'azure', 'azure-eastus', 'azure-dsv3', 'avg_price_per_vcpu', 0.048000, 'USD/hour', '2026-02-01', 35, 0.045000, 0.048000, 0.051000, 0.054000, 0.043000, 0.056000);
