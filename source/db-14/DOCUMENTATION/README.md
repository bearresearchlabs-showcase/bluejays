---
title: Cloud Instance Cost Database — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-14
---

# Cloud Instance Cost Database — Documentation

**Database:** db-14  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_14
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_14 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load sample data from data.sql if available.

```bash
psql -U postgres -d db_14 -f data.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

Standard PostgreSQL. No extensions required unless noted.

---

## Schema Overview

**Total tables:** 11

- `cloud_providers` — (see data dictionary)
- `cloud_regions` — (see data dictionary)
- `instance_families` — (see data dictionary)
- `cloud_instances` — (see data dictionary)
- `instance_performance_metrics` — (see data dictionary)
- `instance_pricing` — (see data dictionary)
- `historical_pricing` — (see data dictionary)
- `cost_optimization_recommendations` — (see data dictionary)
- `instance_comparison_matrix` — (see data dictionary)
- `data_extraction_log` — (see data dictionary)
- `cost__analytics` — (see data dictionary)

---

## Data Dictionary

### `cloud_providers`

- `provider_id` VARCHAR(50) PRIMARY KEY
- `provider_name` VARCHAR(100) NOT NULL — 'AWS', 'GCP', 'Azure'
- `provider_display_name` VARCHAR(255) 
- `api_base_url` VARCHAR(500) 
- `pricing_api_endpoint` VARCHAR(500) 
- `documentation_url` VARCHAR(500) 
- `data_source` VARCHAR(100)  — 'vantage.sh', 'official_api', 'scraped'
- `last_updated` TIMESTAMP 
- `update_frequency` VARCHAR(50)  — 'daily', 'weekly', 'monthly'
- `data_quality_score` NUMERIC(5, 2) 

### `cloud_regions`

- `region_id` VARCHAR(255) PRIMARY KEY
- `provider_id` VARCHAR(50) NOT NULL
- `region_code` VARCHAR(50) NOT NULL — 'us-east-1', 'us-central1', 'eastus'
- `region_name` VARCHAR(255) 
- `region_display_name` VARCHAR(255) 
- `country_code` VARCHAR(2) 
- `continent` VARCHAR(50) 
- `timezone` VARCHAR(50) 
- `is_active` BOOLEAN 
- `launch_date` DATE 
- `data_center_count` INTEGER 
- `availability_zones_count` INTEGER 
- `last_updated` TIMESTAMP 

### `instance_families`

- `family_id` VARCHAR(255) PRIMARY KEY
- `provider_id` VARCHAR(50) NOT NULL
- `family_name` VARCHAR(100) NOT NULL — 'General Purpose', 'Compute Optimized', 'Memory Optimized'
- `family_code` VARCHAR(50)  — 'm5', 'c5', 'r5' for AWS
- `family_description` TEXT 
- `use_case_category` VARCHAR(100) 
- `target_workloads` TEXT 
- `last_updated` TIMESTAMP 

### `cloud_instances`

- `instance_id` VARCHAR(255) PRIMARY KEY
- `provider_id` VARCHAR(50) NOT NULL
- `instance_name` VARCHAR(100) NOT NULL — 'm5.large', 'n1-standard-4', 'Standard_D2s_v3'
- `api_name` VARCHAR(100)  — API identifier
- `instance_family_id` VARCHAR(255) 
- `region_id` VARCHAR(255) 
- `vcpus` INTEGER NOT NULL
- `memory_gb` NUMERIC(10, 2) NOT NULL
- `memory_mb` INTEGER 
- `instance_storage_gb` NUMERIC(10, 2) 
- `instance_storage_type` VARCHAR(50)  — 'EBS', 'NVMe SSD', 'HDD', 'Local SSD'
- `network_performance` VARCHAR(100)  — 'Up to 10 Gigabit', '25 Gigabit'
- `network_bandwidth_gbps` NUMERIC(10, 2) 
- `ebs_optimized` BOOLEAN 
- `ebs_optimization_surcharge` NUMERIC(10, 4) 
- `gpu_count` INTEGER 
- `gpu_type` VARCHAR(100) 
- `gpu_memory_gb` NUMERIC(10, 2) 
- `architecture` VARCHAR(50)  — 'x86_64', 'arm64', 'amd64'
- `processor_type` VARCHAR(100)  — 'Intel Xeon', 'AMD EPYC', 'AWS Graviton'
- `processor_speed_ghz` NUMERIC(5, 2) 
- `hypervisor` VARCHAR(50) 
- `virtualization_type` VARCHAR(50) 
- `is_burstable` BOOLEAN 
- `baseline_performance` NUMERIC(5, 2)  — For burstable instances
- `is_current_generation` BOOLEAN 
- `is_available` BOOLEAN 
- `launch_date` DATE 
- `deprecation_date` DATE 
- `last_updated` TIMESTAMP 

### `instance_performance_metrics`

- `metric_id` VARCHAR(255) PRIMARY KEY
- `instance_id` VARCHAR(255) NOT NULL
- `benchmark_name` VARCHAR(100) NOT NULL — 'CoreMark', 'FFmpeg FPS', 'SPECint', 'Geekbench'
- `benchmark_score` NUMERIC(15, 2) 
- `benchmark_score_normalized` NUMERIC(15, 2)  — Normalized across providers
- `benchmark_version` VARCHAR(50) 
- `test_date` DATE 
- `test_environment` VARCHAR(255) 
- `test_methodology` TEXT 
- `sample_size` INTEGER 
- `confidence_level` NUMERIC(5, 2) 
- `source` VARCHAR(100)  — 'vantage.sh', 'official', 'third_party'
- `last_updated` TIMESTAMP 

### `instance_pricing`

- `pricing_id` VARCHAR(255) PRIMARY KEY
- `instance_id` VARCHAR(255) NOT NULL
- `region_id` VARCHAR(255) NOT NULL
- `pricing_model` VARCHAR(50) NOT NULL — 'on_demand', 'reserved_1yr', 'reserved_3yr', 'spot', 'savings_plan'
- `operating_system` VARCHAR(50)  — 'Linux', 'Windows', 'RHEL', 'SUSE'
- `currency` VARCHAR(10) 
- `price_per_hour` NUMERIC(15, 6) 
- `price_per_month` NUMERIC(15, 2) 
- `price_per_year` NUMERIC(15, 2) 
- `price_per_unit` VARCHAR(50)  — 'Instance', 'vCPU', 'GB'
- `upfront_cost` NUMERIC(15, 2)  — For reserved instances
- `effective_hourly_cost` NUMERIC(15, 6)  — Calculated effective cost
- `discount_percentage` NUMERIC(5, 2) 
- `term_length_months` INTEGER 
- `payment_option` VARCHAR(50)  — 'no_upfront', 'partial_upfront', 'all_upfront'
- `utilization_commitment` NUMERIC(5, 2)  — For savings plans
- `pricing_effective_date` DATE 
- `pricing_end_date` DATE 
- `is_current` BOOLEAN 
- `last_updated` TIMESTAMP 

### `historical_pricing`

- `historical_id` VARCHAR(255) PRIMARY KEY
- `instance_id` VARCHAR(255) NOT NULL
- `region_id` VARCHAR(255) NOT NULL
- `pricing_model` VARCHAR(50) NOT NULL
- `operating_system` VARCHAR(50) 
- `price_per_hour` NUMERIC(15, 6) 
- `price_change_percentage` NUMERIC(8, 4) 
- `price_change_amount` NUMERIC(15, 6) 
- `effective_date` DATE NOT NULL
- `change_type` VARCHAR(50)  — 'price_increase', 'price_decrease', 'new_instance'
- `change_reason` TEXT 
- `last_updated` TIMESTAMP 

### `cost_optimization_recommendations`

- `recommendation_id` VARCHAR(255) PRIMARY KEY
- `instance_id` VARCHAR(255) NOT NULL
- `target_instance_id` VARCHAR(255)  — Recommended alternative instance
- `optimization_type` VARCHAR(100)  — 'rightsizing', 'reserved_instance', 'spot_instance', 'region_change'
- `current_cost_per_month` NUMERIC(15, 2) 
- `recommended_cost_per_month` NUMERIC(15, 2) 
- `potential_savings_per_month` NUMERIC(15, 2) 
- `potential_savings_percentage` NUMERIC(5, 2) 
- `confidence_score` NUMERIC(5, 2) 
- `recommendation_reasoning` TEXT 
- `implementation_complexity` VARCHAR(50)  — 'low', 'medium', 'high'
- `risk_level` VARCHAR(50)  — 'low', 'medium', 'high'
- `estimated_migration_time_hours` INTEGER 
- `workload_compatibility_score` NUMERIC(5, 2) 
- `created_date` TIMESTAMP 
- `last_updated` TIMESTAMP 

### `instance_comparison_matrix`

- `comparison_id` VARCHAR(255) PRIMARY KEY
- `instance_id_1` VARCHAR(255) NOT NULL
- `instance_id_2` VARCHAR(255) NOT NULL
- `comparison_metric` VARCHAR(100)  — 'price_performance', 'cost_efficiency', 'spec_match'
- `similarity_score` NUMERIC(5, 2)  — 0-100 similarity score
- `price_difference_percentage` NUMERIC(8, 4) 
- `performance_difference_percentage` NUMERIC(8, 4) 
- `vcpu_match` BOOLEAN 
- `memory_match` BOOLEAN 
- `storage_match` BOOLEAN 
- `network_match` BOOLEAN 
- `comparison_date` DATE 
- `last_updated` TIMESTAMP 

### `data_extraction_log`

- `extraction_id` VARCHAR(255) PRIMARY KEY
- `source_name` VARCHAR(100) NOT NULL — 'vantage.sh', 'aws_api', 'gcp_api', 'azure_api'
- `source_url` VARCHAR(1000) 
- `extraction_type` VARCHAR(50)  — 'api', 'scraping', 'export', 'manual'
- `provider_id` VARCHAR(50) 
- `records_extracted` INTEGER 
- `records_successful` INTEGER 
- `records_failed` INTEGER 
- `extraction_start_time` TIMESTAMP NOT NULL
- `extraction_end_time` TIMESTAMP 
- `extraction_duration_seconds` INTEGER 
- `data_size_mb` NUMERIC(10, 2) 
- `extraction_status` VARCHAR(50)  — 'success', 'failed', 'partial'
- `error_message` TEXT 
- `last_updated` TIMESTAMP 

### `cost__analytics`

- `analytics_id` VARCHAR(255) PRIMARY KEY
- `provider_id` VARCHAR(50) 
- `region_id` VARCHAR(255) 
- `instance_family_id` VARCHAR(255) 
- `metric_name` VARCHAR(100) NOT NULL — 'avg_price_per_vcpu', 'avg_price_per_gb_memory', 'price_performance_ratio'
- `metric_value` NUMERIC(15, 4) 
- `metric_unit` VARCHAR(50) 
- `calculation_date` DATE NOT NULL
- `sample_size` INTEGER 
- `percentile_25` NUMERIC(15, 4) 
- `percentile_50` NUMERIC(15, 4)  — Median
- `percentile_75` NUMERIC(15, 4) 
- `percentile_90` NUMERIC(15, 4) 
- `percentile_95` NUMERIC(15, 4) 
- `percentile_99` NUMERIC(15, 4) 
- `min_value` NUMERIC(15, 4) 
- `max_value` NUMERIC(15, 4) 
- `std_deviation` NUMERIC(15, 4) 
- `last_updated` TIMESTAMP 

---

*Generated by documentation workflow. MDX-compatible markdown.*
