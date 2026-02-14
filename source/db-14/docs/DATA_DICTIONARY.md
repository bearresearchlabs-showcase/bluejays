# Data Dictionary - db-14

**Created:** 2026-02-05

## Overview

This data dictionary provides comprehensive column-level documentation for all tables in the Cloud Instance Cost  Database.

## Tables

### cloud_providers

Stores cloud provider metadata (AWS, GCP, Azure).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| provider_id | VARCHAR(50) | PRIMARY KEY | Unique identifier for cloud provider ('aws', 'gcp', 'azure') |
| provider_name | VARCHAR(100) | NOT NULL | Provider name ('AWS', 'GCP', 'Azure') |
| provider_display_name | VARCHAR(255) | | Human-readable display name |
| api_base_url | VARCHAR(500) | | Base URL for provider API |
| pricing_api_endpoint | VARCHAR(500) | | Endpoint for pricing API |
| documentation_url | VARCHAR(500) | | URL to provider documentation |
| data_source | VARCHAR(100) | | Source of data ('vantage.sh', 'official_api', 'scraped') |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |
| update_frequency | VARCHAR(50) | | Update frequency ('daily', 'weekly', 'monthly') |
| data_quality_score | NUMERIC(5, 2) | | Data quality score (0-100) |

### cloud_regions

Stores region metadata for all cloud providers.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| region_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for region |
| provider_id | VARCHAR(50) | NOT NULL, FK → cloud_providers | Cloud provider identifier |
| region_code | VARCHAR(50) | NOT NULL | Region code ('us-east-1', 'us-central1', 'eastus') |
| region_name | VARCHAR(255) | | Region name |
| region_display_name | VARCHAR(255) | | Human-readable display name |
| country_code | VARCHAR(2) | | ISO country code |
| continent | VARCHAR(50) | | Continent name |
| timezone | VARCHAR(50) | | Timezone identifier |
| is_active | BOOLEAN | DEFAULT TRUE | Whether region is currently active |
| launch_date | DATE | | Region launch date |
| data_center_count | INTEGER | | Number of data centers in region |
| availability_zones_count | INTEGER | | Number of availability zones |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### instance_families

Stores instance family metadata (General Purpose, Compute Optimized, etc.).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| family_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for instance family |
| provider_id | VARCHAR(50) | NOT NULL, FK → cloud_providers | Cloud provider identifier |
| family_name | VARCHAR(100) | NOT NULL | Family name ('General Purpose', 'Compute Optimized', 'Memory Optimized') |
| family_code | VARCHAR(50) | | Family code ('m5', 'c5', 'r5' for AWS) |
| family_description | TEXT | | Detailed family description |
| use_case_category | VARCHAR(100) | | Use case category |
| target_workloads | TEXT | | Target workload types |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### cloud_instances

Core table storing all cloud instance specifications.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| instance_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for instance |
| provider_id | VARCHAR(50) | NOT NULL, FK → cloud_providers | Cloud provider identifier |
| instance_name | VARCHAR(100) | NOT NULL | Instance name ('m5.large', 'n1-standard-4', 'Standard_D2s_v3') |
| api_name | VARCHAR(100) | | API identifier |
| instance_family_id | VARCHAR(255) | FK → instance_families | Instance family identifier |
| region_id | VARCHAR(255) | FK → cloud_regions | Region identifier |
| vcpus | INTEGER | NOT NULL | Number of virtual CPUs |
| memory_gb | NUMERIC(10, 2) | NOT NULL | Memory in gigabytes |
| memory_mb | INTEGER | | Memory in megabytes (alternative) |
| instance_storage_gb | NUMERIC(10, 2) | | Instance storage in gigabytes |
| instance_storage_type | VARCHAR(50) | | Storage type ('EBS', 'NVMe SSD', 'HDD', 'Local SSD') |
| network_performance | VARCHAR(100) | | Network performance description |
| network_bandwidth_gbps | NUMERIC(10, 2) | | Network bandwidth in Gbps |
| ebs_optimized | BOOLEAN | | Whether EBS optimized |
| ebs_optimization_surcharge | NUMERIC(10, 4) | | EBS optimization surcharge |
| gpu_count | INTEGER | DEFAULT 0 | Number of GPUs |
| gpu_type | VARCHAR(100) | | GPU type |
| gpu_memory_gb | NUMERIC(10, 2) | | GPU memory in gigabytes |
| architecture | VARCHAR(50) | | Architecture ('x86_64', 'arm64', 'amd64') |
| processor_type | VARCHAR(100) | | Processor type ('Intel Xeon', 'AMD EPYC', 'AWS Graviton') |
| processor_speed_ghz | NUMERIC(5, 2) | | Processor speed in GHz |
| hypervisor | VARCHAR(50) | | Hypervisor type |
| virtualization_type | VARCHAR(50) | | Virtualization type |
| is_burstable | BOOLEAN | DEFAULT FALSE | Whether instance is burstable |
| baseline_performance | NUMERIC(5, 2) | | Baseline performance percentage (for burstable) |
| is_current_generation | BOOLEAN | DEFAULT TRUE | Whether current generation |
| is_available | BOOLEAN | DEFAULT TRUE | Whether instance is available |
| launch_date | DATE | | Instance launch date |
| deprecation_date | DATE | | Instance deprecation date |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### instance_performance_metrics

Stores performance benchmark data (CoreMark, FFmpeg FPS, etc.).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| metric_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for metric |
| instance_id | VARCHAR(255) | NOT NULL, FK → cloud_instances | Instance identifier |
| benchmark_name | VARCHAR(100) | NOT NULL | Benchmark name ('CoreMark', 'FFmpeg FPS', 'SPECint', 'Geekbench') |
| benchmark_score | NUMERIC(15, 2) | | Raw benchmark score |
| benchmark_score_normalized | NUMERIC(15, 2) | | Normalized score (across providers) |
| benchmark_version | VARCHAR(50) | | Benchmark version |
| test_date | DATE | | Test date |
| test_environment | VARCHAR(255) | | Test environment description |
| test_methodology | TEXT | | Test methodology details |
| sample_size | INTEGER | | Sample size for benchmark |
| confidence_level | NUMERIC(5, 2) | | Confidence level (0-100) |
| source | VARCHAR(100) | | Source ('vantage.sh', 'official', 'third_party') |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### instance_pricing

Stores pricing data for all pricing models (on-demand, reserved, spot).

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| pricing_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for pricing entry |
| instance_id | VARCHAR(255) | NOT NULL, FK → cloud_instances | Instance identifier |
| region_id | VARCHAR(255) | NOT NULL, FK → cloud_regions | Region identifier |
| pricing_model | VARCHAR(50) | NOT NULL | Pricing model ('on_demand', 'reserved_1yr', 'reserved_3yr', 'spot', 'savings_plan') |
| operating_system | VARCHAR(50) | | Operating system ('Linux', 'Windows', 'RHEL', 'SUSE') |
| currency | VARCHAR(10) | DEFAULT 'USD' | Currency code |
| price_per_hour | NUMERIC(15, 6) | | Price per hour |
| price_per_month | NUMERIC(15, 2) | | Price per month |
| price_per_year | NUMERIC(15, 2) | | Price per year |
| price_per_unit | VARCHAR(50) | | Pricing unit ('Instance', 'vCPU', 'GB') |
| upfront_cost | NUMERIC(15, 2) | | Upfront cost (for reserved instances) |
| effective_hourly_cost | NUMERIC(15, 6) | | Calculated effective hourly cost |
| discount_percentage | NUMERIC(5, 2) | | Discount percentage |
| term_length_months | INTEGER | | Term length in months |
| payment_option | VARCHAR(50) | | Payment option ('no_upfront', 'partial_upfront', 'all_upfront') |
| utilization_commitment | NUMERIC(5, 2) | | Utilization commitment percentage (for savings plans) |
| pricing_effective_date | DATE | | Pricing effective date |
| pricing_end_date | DATE | | Pricing end date |
| is_current | BOOLEAN | DEFAULT TRUE | Whether current pricing |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### historical_pricing

Tracks pricing changes over time for trend analysis.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| historical_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for historical entry |
| instance_id | VARCHAR(255) | NOT NULL, FK → cloud_instances | Instance identifier |
| region_id | VARCHAR(255) | NOT NULL, FK → cloud_regions | Region identifier |
| pricing_model | VARCHAR(50) | NOT NULL | Pricing model |
| operating_system | VARCHAR(50) | | Operating system |
| price_per_hour | NUMERIC(15, 6) | | Historical price per hour |
| price_change_percentage | NUMERIC(8, 4) | | Price change percentage |
| price_change_amount | NUMERIC(15, 6) | | Price change amount |
| effective_date | DATE | NOT NULL | Effective date of price change |
| change_type | VARCHAR(50) | | Change type ('price_increase', 'price_decrease', 'new_instance') |
| change_reason | TEXT | | Reason for price change |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### cost_optimization_recommendations

Stores AI-generated cost optimization recommendations.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| recommendation_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for recommendation |
| instance_id | VARCHAR(255) | NOT NULL, FK → cloud_instances | Source instance identifier |
| target_instance_id | VARCHAR(255) | FK → cloud_instances | Recommended target instance |
| optimization_type | VARCHAR(100) | | Optimization type ('rightsizing', 'reserved_instance', 'spot_instance', 'region_change') |
| current_cost_per_month | NUMERIC(15, 2) | | Current monthly cost |
| recommended_cost_per_month | NUMERIC(15, 2) | | Recommended monthly cost |
| potential_savings_per_month | NUMERIC(15, 2) | | Potential monthly savings |
| potential_savings_percentage | NUMERIC(5, 2) | | Potential savings percentage |
| confidence_score | NUMERIC(5, 2) | | Confidence score (0-100) |
| recommendation_reasoning | TEXT | | Reasoning for recommendation |
| implementation_complexity | VARCHAR(50) | | Implementation complexity ('low', 'medium', 'high') |
| risk_level | VARCHAR(50) | | Risk level ('low', 'medium', 'high') |
| estimated_migration_time_hours | INTEGER | | Estimated migration time in hours |
| workload_compatibility_score | NUMERIC(5, 2) | | Workload compatibility score (0-100) |
| created_date | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Creation timestamp |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### instance_comparison_matrix

Stores cross-provider instance comparisons.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| comparison_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for comparison |
| instance_id_1 | VARCHAR(255) | NOT NULL, FK → cloud_instances | First instance identifier |
| instance_id_2 | VARCHAR(255) | NOT NULL, FK → cloud_instances | Second instance identifier |
| comparison_metric | VARCHAR(100) | | Comparison metric ('price_performance', 'cost_efficiency', 'spec_match') |
| similarity_score | NUMERIC(5, 2) | | Similarity score (0-100) |
| price_difference_percentage | NUMERIC(8, 4) | | Price difference percentage |
| performance_difference_percentage | NUMERIC(8, 4) | | Performance difference percentage |
| vcpu_match | BOOLEAN | | Whether vCPU count matches |
| memory_match | BOOLEAN | | Whether memory matches |
| storage_match | BOOLEAN | | Whether storage matches |
| network_match | BOOLEAN | | Whether network matches |
| comparison_date | DATE | | Comparison date |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### data_extraction_log

Tracks data extraction operations from various sources.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| extraction_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for extraction |
| source_name | VARCHAR(100) | NOT NULL | Source name ('vantage.sh', 'aws_api', 'gcp_api', 'azure_api') |
| source_url | VARCHAR(1000) | | Source URL |
| extraction_type | VARCHAR(50) | | Extraction type ('api', 'scraping', 'export', 'manual') |
| provider_id | VARCHAR(50) | FK → cloud_providers | Provider identifier |
| records_extracted | INTEGER | DEFAULT 0 | Number of records extracted |
| records_successful | INTEGER | DEFAULT 0 | Number of successful records |
| records_failed | INTEGER | DEFAULT 0 | Number of failed records |
| extraction_start_time | TIMESTAMP_NTZ | NOT NULL | Extraction start time |
| extraction_end_time | TIMESTAMP_NTZ | | Extraction end time |
| extraction_duration_seconds | INTEGER | | Extraction duration in seconds |
| data_size_mb | NUMERIC(10, 2) | | Data size in MB |
| extraction_status | VARCHAR(50) | | Extraction status ('success', 'failed', 'partial') |
| error_message | TEXT | | Error message if failed |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

### cost__analytics

Pre-aggregated analytics for fast querying.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| analytics_id | VARCHAR(255) | PRIMARY KEY | Unique identifier for analytics entry |
| provider_id | VARCHAR(50) | FK → cloud_providers | Provider identifier |
| region_id | VARCHAR(255) | FK → cloud_regions | Region identifier |
| instance_family_id | VARCHAR(255) | FK → instance_families | Instance family identifier |
| metric_name | VARCHAR(100) | NOT NULL | Metric name ('avg_price_per_vcpu', 'avg_price_per_gb_memory', 'price_performance_ratio') |
| metric_value | NUMERIC(15, 4) | | Metric value |
| metric_unit | VARCHAR(50) | | Metric unit |
| calculation_date | DATE | NOT NULL | Calculation date |
| sample_size | INTEGER | | Sample size |
| percentile_25 | NUMERIC(15, 4) | | 25th percentile |
| percentile_50 | NUMERIC(15, 4) | | 50th percentile (median) |
| percentile_75 | NUMERIC(15, 4) | | 75th percentile |
| percentile_90 | NUMERIC(15, 4) | | 90th percentile |
| percentile_95 | NUMERIC(15, 4) | | 95th percentile |
| percentile_99 | NUMERIC(15, 4) | | 99th percentile |
| min_value | NUMERIC(15, 4) | | Minimum value |
| max_value | NUMERIC(15, 4) | | Maximum value |
| std_deviation | NUMERIC(15, 4) | | Standard deviation |
| last_updated | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last update timestamp |

---
**Last Updated:** 2026-02-05
