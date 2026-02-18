-- Cloud Instance Cost Database Schema
-- Compatible with PostgreSQL
-- Production schema for cloud instance cost analysis and optimization system

-- Cloud Providers Table
-- Stores cloud provider metadata
CREATE TABLE cloud_providers (
    provider_id VARCHAR(50) PRIMARY KEY,
    provider_name VARCHAR(100) NOT NULL,  -- 'AWS', 'GCP', 'Azure'
    provider_display_name VARCHAR(255),
    api_base_url VARCHAR(500),
    pricing_api_endpoint VARCHAR(500),
    documentation_url VARCHAR(500),
    data_source VARCHAR(100),  -- 'vantage.sh', 'official_api', 'scraped'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_frequency VARCHAR(50),  -- 'daily', 'weekly', 'monthly'
    data_quality_score NUMERIC(5, 2)
);

-- Cloud Regions Table
-- Stores region metadata for all cloud providers
CREATE TABLE cloud_regions (
    region_id VARCHAR(255) PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL,
    region_code VARCHAR(50) NOT NULL,  -- 'us-east-1', 'us-central1', 'eastus'
    region_name VARCHAR(255),
    region_display_name VARCHAR(255),
    country_code VARCHAR(2),
    continent VARCHAR(50),
    timezone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    launch_date DATE,
    data_center_count INTEGER,
    availability_zones_count INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES cloud_providers(provider_id)
);

-- Instance Families Table
-- Stores instance family metadata (e.g., 'General Purpose', 'Compute Optimized')
CREATE TABLE instance_families (
    family_id VARCHAR(255) PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL,
    family_name VARCHAR(100) NOT NULL,  -- 'General Purpose', 'Compute Optimized', 'Memory Optimized'
    family_code VARCHAR(50),  -- 'm5', 'c5', 'r5' for AWS
    family_description TEXT,
    use_case_category VARCHAR(100),
    target_workloads TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES cloud_providers(provider_id)
);

-- Cloud Instances Table
-- Core table storing all cloud instance specifications
CREATE TABLE cloud_instances (
    instance_id VARCHAR(255) PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL,
    instance_name VARCHAR(100) NOT NULL,  -- 'm5.large', 'n1-standard-4', 'Standard_D2s_v3'
    api_name VARCHAR(100),  -- API identifier
    instance_family_id VARCHAR(255),
    region_id VARCHAR(255),
    vcpus INTEGER NOT NULL,
    memory_gb NUMERIC(10, 2) NOT NULL,
    memory_mb INTEGER,
    instance_storage_gb NUMERIC(10, 2),
    instance_storage_type VARCHAR(50),  -- 'EBS', 'NVMe SSD', 'HDD', 'Local SSD'
    network_performance VARCHAR(100),  -- 'Up to 10 Gigabit', '25 Gigabit'
    network_bandwidth_gbps NUMERIC(10, 2),
    ebs_optimized BOOLEAN,
    ebs_optimization_surcharge NUMERIC(10, 4),
    gpu_count INTEGER DEFAULT 0,
    gpu_type VARCHAR(100),
    gpu_memory_gb NUMERIC(10, 2),
    architecture VARCHAR(50),  -- 'x86_64', 'arm64', 'amd64'
    processor_type VARCHAR(100),  -- 'Intel Xeon', 'AMD EPYC', 'AWS Graviton'
    processor_speed_ghz NUMERIC(5, 2),
    hypervisor VARCHAR(50),
    virtualization_type VARCHAR(50),
    is_burstable BOOLEAN DEFAULT FALSE,
    baseline_performance NUMERIC(5, 2),  -- For burstable instances
    is_current_generation BOOLEAN DEFAULT TRUE,
    is_available BOOLEAN DEFAULT TRUE,
    launch_date DATE,
    deprecation_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES cloud_providers(provider_id),
    FOREIGN KEY (instance_family_id) REFERENCES instance_families(family_id),
    FOREIGN KEY (region_id) REFERENCES cloud_regions(region_id)
);

-- Instance Performance Metrics Table
-- Stores performance benchmark data (CoreMark, FFmpeg FPS, etc.)
CREATE TABLE instance_performance_metrics (
    metric_id VARCHAR(255) PRIMARY KEY,
    instance_id VARCHAR(255) NOT NULL,
    benchmark_name VARCHAR(100) NOT NULL,  -- 'CoreMark', 'FFmpeg FPS', 'SPECint', 'Geekbench'
    benchmark_score NUMERIC(15, 2),
    benchmark_score_normalized NUMERIC(15, 2),  -- Normalized across providers
    benchmark_version VARCHAR(50),
    test_date DATE,
    test_environment VARCHAR(255),
    test_methodology TEXT,
    sample_size INTEGER,
    confidence_level NUMERIC(5, 2),
    source VARCHAR(100),  -- 'vantage.sh', 'official', 'third_party'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id)
);

-- Instance Pricing Table
-- Stores pricing data for all pricing models (on-demand, reserved, spot)
CREATE TABLE instance_pricing (
    pricing_id VARCHAR(255) PRIMARY KEY,
    instance_id VARCHAR(255) NOT NULL,
    region_id VARCHAR(255) NOT NULL,
    pricing_model VARCHAR(50) NOT NULL,  -- 'on_demand', 'reserved_1yr', 'reserved_3yr', 'spot', 'savings_plan'
    operating_system VARCHAR(50),  -- 'Linux', 'Windows', 'RHEL', 'SUSE'
    currency VARCHAR(10) DEFAULT 'USD',
    price_per_hour NUMERIC(15, 6),
    price_per_month NUMERIC(15, 2),
    price_per_year NUMERIC(15, 2),
    price_per_unit VARCHAR(50),  -- 'Instance', 'vCPU', 'GB'
    upfront_cost NUMERIC(15, 2),  -- For reserved instances
    effective_hourly_cost NUMERIC(15, 6),  -- Calculated effective cost
    discount_percentage NUMERIC(5, 2),
    term_length_months INTEGER,
    payment_option VARCHAR(50),  -- 'no_upfront', 'partial_upfront', 'all_upfront'
    utilization_commitment NUMERIC(5, 2),  -- For savings plans
    pricing_effective_date DATE,
    pricing_end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id),
    FOREIGN KEY (region_id) REFERENCES cloud_regions(region_id)
);

-- Historical Pricing Table
-- Tracks pricing changes over time for trend analysis
CREATE TABLE historical_pricing (
    historical_id VARCHAR(255) PRIMARY KEY,
    instance_id VARCHAR(255) NOT NULL,
    region_id VARCHAR(255) NOT NULL,
    pricing_model VARCHAR(50) NOT NULL,
    operating_system VARCHAR(50),
    price_per_hour NUMERIC(15, 6),
    price_change_percentage NUMERIC(8, 4),
    price_change_amount NUMERIC(15, 6),
    effective_date DATE NOT NULL,
    change_type VARCHAR(50),  -- 'price_increase', 'price_decrease', 'new_instance'
    change_reason TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id),
    FOREIGN KEY (region_id) REFERENCES cloud_regions(region_id)
);

-- Cost Optimization Recommendations Table
-- Stores AI-generated cost optimization recommendations
CREATE TABLE cost_optimization_recommendations (
    recommendation_id VARCHAR(255) PRIMARY KEY,
    instance_id VARCHAR(255) NOT NULL,
    target_instance_id VARCHAR(255),  -- Recommended alternative instance
    optimization_type VARCHAR(100),  -- 'rightsizing', 'reserved_instance', 'spot_instance', 'region_change'
    current_cost_per_month NUMERIC(15, 2),
    recommended_cost_per_month NUMERIC(15, 2),
    potential_savings_per_month NUMERIC(15, 2),
    potential_savings_percentage NUMERIC(5, 2),
    confidence_score NUMERIC(5, 2),
    recommendation_reasoning TEXT,
    implementation_complexity VARCHAR(50),  -- 'low', 'medium', 'high'
    risk_level VARCHAR(50),  -- 'low', 'medium', 'high'
    estimated_migration_time_hours INTEGER,
    workload_compatibility_score NUMERIC(5, 2),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instance_id) REFERENCES cloud_instances(instance_id),
    FOREIGN KEY (target_instance_id) REFERENCES cloud_instances(instance_id)
);

-- Instance Comparison Matrix Table
-- Stores cross-provider instance comparisons
CREATE TABLE instance_comparison_matrix (
    comparison_id VARCHAR(255) PRIMARY KEY,
    instance_id_1 VARCHAR(255) NOT NULL,
    instance_id_2 VARCHAR(255) NOT NULL,
    comparison_metric VARCHAR(100),  -- 'price_performance', 'cost_efficiency', 'spec_match'
    similarity_score NUMERIC(5, 2),  -- 0-100 similarity score
    price_difference_percentage NUMERIC(8, 4),
    performance_difference_percentage NUMERIC(8, 4),
    vcpu_match BOOLEAN,
    memory_match BOOLEAN,
    storage_match BOOLEAN,
    network_match BOOLEAN,
    comparison_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instance_id_1) REFERENCES cloud_instances(instance_id),
    FOREIGN KEY (instance_id_2) REFERENCES cloud_instances(instance_id)
);

-- Data Extraction Log Table
-- Tracks data extraction operations from various sources
CREATE TABLE data_extraction_log (
    extraction_id VARCHAR(255) PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,  -- 'vantage.sh', 'aws_api', 'gcp_api', 'azure_api'
    source_url VARCHAR(1000),
    extraction_type VARCHAR(50),  -- 'api', 'scraping', 'export', 'manual'
    provider_id VARCHAR(50),
    records_extracted INTEGER DEFAULT 0,
    records_successful INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    extraction_start_time TIMESTAMP NOT NULL,
    extraction_end_time TIMESTAMP,
    extraction_duration_seconds INTEGER,
    data_size_mb NUMERIC(10, 2),
    extraction_status VARCHAR(50),  -- 'success', 'failed', 'partial'
    error_message TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES cloud_providers(provider_id)
);

-- Cost Analytics Table
-- Pre-aggregated analytics for fast querying
CREATE TABLE cost__analytics (
    analytics_id VARCHAR(255) PRIMARY KEY,
    provider_id VARCHAR(50),
    region_id VARCHAR(255),
    instance_family_id VARCHAR(255),
    metric_name VARCHAR(100) NOT NULL,  -- 'avg_price_per_vcpu', 'avg_price_per_gb_memory', 'price_performance_ratio'
    metric_value NUMERIC(15, 4),
    metric_unit VARCHAR(50),
    calculation_date DATE NOT NULL,
    sample_size INTEGER,
    percentile_25 NUMERIC(15, 4),
    percentile_50 NUMERIC(15, 4),  -- Median
    percentile_75 NUMERIC(15, 4),
    percentile_90 NUMERIC(15, 4),
    percentile_95 NUMERIC(15, 4),
    percentile_99 NUMERIC(15, 4),
    min_value NUMERIC(15, 4),
    max_value NUMERIC(15, 4),
    std_deviation NUMERIC(15, 4),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES cloud_providers(provider_id),
    FOREIGN KEY (region_id) REFERENCES cloud_regions(region_id),
    FOREIGN KEY (instance_family_id) REFERENCES instance_families(family_id)
);

-- Create indexes for performance
CREATE INDEX idx_cloud_instances_provider ON cloud_instances(provider_id);
CREATE INDEX idx_cloud_instances_family ON cloud_instances(instance_family_id);
CREATE INDEX idx_cloud_instances_region ON cloud_instances(region_id);
CREATE INDEX idx_cloud_instances_vcpus_memory ON cloud_instances(vcpus, memory_gb);
CREATE INDEX idx_instance_pricing_instance_region ON instance_pricing(instance_id, region_id);
CREATE INDEX idx_instance_pricing_model ON instance_pricing(pricing_model, is_current);
CREATE INDEX idx_instance_pricing_price ON instance_pricing(price_per_hour);
CREATE INDEX idx_performance_metrics_instance ON instance_performance_metrics(instance_id);
CREATE INDEX idx_performance_metrics_benchmark ON instance_performance_metrics(benchmark_name, benchmark_score);
CREATE INDEX idx_historical_pricing_instance_date ON historical_pricing(instance_id, effective_date);
CREATE INDEX idx_cost_optimization_instance ON cost_optimization_recommendations(instance_id);
CREATE INDEX idx_cost_optimization_savings ON cost_optimization_recommendations(potential_savings_per_month DESC);
CREATE INDEX idx_comparison_matrix_instances ON instance_comparison_matrix(instance_id_1, instance_id_2);
CREATE INDEX idx_extraction_log_provider ON data_extraction_log(provider_id, extraction_start_time);
CREATE INDEX idx_analytics_provider_region ON cost__analytics(provider_id, region_id, calculation_date);
