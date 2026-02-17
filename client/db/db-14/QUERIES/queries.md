# Cloud Instance Cost Database — Query Documentation

## Database Overview

```yaml
db_id: db-14
domain: Cloud Instance Cost
source: [commercial]
license_type: [Commercial]
license_cost: [NDA]
tables: 11
total_rows: ~80
date_range: 2020-01-01 to 2026-12-31
sql_dialect: PostgreSQL
```

## Purpose

```text
This database supports analytics for cloud instance cost comparison and optimization across
AWS, GCP, and Azure. It models providers, regions, instance families, pricing models,
performance benchmarks, and cost optimization recommendations. It is designed to support
text-to-SQL training across FinOps, cost allocation, and rightsizing query types.
```

## Use Case

```text
Target use cases for db-14:
- Cost comparison: on-demand vs reserved vs spot pricing across providers
- Rightsizing: match workload specs to instance families and regions
- Optimization: cost_optimization_recommendations, instance_comparison_matrix
- FinOps dashboards: historical pricing, cost-per-vCPU, performance-per-dollar
```

## Business Value

```text
Cloud cost databases represent high-value domains for text-to-SQL because:
- Queries require understanding of pricing models (on_demand, reserved_1yr, spot, savings_plan)
- Data relationships span providers, regions, families, and instances
- Stakeholders need self-serve cost analytics (FinOps, engineering, finance)
- Evidence bridges natural-language questions to schema-grounded SQL.
```

## Schema

```sql
-- PostgreSQL-specific schema file
-- Generated from schema.sql
-- Generated: 2026-02-05 19:10:13
-- Database: db-14
-- 
-- This file contains PostgreSQL-specific SQL syntax.
-- Use this file when setting up the database in PostgreSQL.
--

-- Cloud Instance Cost Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
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
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
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
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (provider_id) REFERENCES cloud_providers(provider_id)
);

-- Instance Families Table
-- Stores instance family metadata (e.g., 'General Purpose', 'Compute Optimized')
CREATE TABLE instance_families (
    family_id VARCHAR(255) PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL,
    family_name VARCHAR(100) NOT NULL,  -- 'General Purpose', 'Compute Optimized', 'Memory Optimized'
    family_code
-- ...
```

## Domain Knowledge

```text
Key domain concepts required to write correct queries against this database:

CLOUD PROVIDERS AND REGIONS:
- cloud_providers: AWS, GCP, Azure; provider_id, data_source (vantage.sh, official_api)
- cloud_regions: region_code (us-east-1, us-central1, eastus), country_code, continent

INSTANCE HIERARCHY:
- instance_families: General Purpose, Compute Optimized, Memory Optimized; family_code (m5, c5, r5)
- cloud_instances: instance_name (m5.large, n1-standard-4), vcpus, memory_gb, architecture (x86_64, arm64)

PRICING MODELS:
- instance_pricing: pricing_model (on_demand, reserved_1yr, reserved_3yr, spot, savings_plan)
- operating_system: Linux, Windows, RHEL, SUSE
- payment_option: no_upfront, partial_upfront, all_upfront (for reserved)
- effective_hourly_cost: calculated cost for reserved instances

PERFORMANCE AND OPTIMIZATION:
- instance_performance_metrics: CoreMark, FFmpeg FPS, benchmark_score_normalized
- cost_optimization_recommendations: optimization_type (rightsizing, reserved_instance, spot_instance, region_change)
- instance_comparison_matrix: similarity_score, price_difference_percentage
```

## Query Difficulty Distribution

```text
Target distribution across 30 queries:
- simple (10): Single-table, basic aggregation
- moderate (12): 2-3 table joins, GROUP BY
- challenging (8): CTEs, window functions
```

## Queries

### Query 1 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 1,
  "question": "Can you show me a multi-provider cost-performance analysis that matches equivalent instances across cloud providers and includes cross-cloud optimization recommendations?",
  "SQL": "WITH provider_instance_base AS (\n    -- First CTE: Base instance data with normalized specifications\n    SELECT\n        ci.instance_id,\n        ci.provider_id,\n        cp.provider_name,\n        ci.instance_name,\n        ci.api_name,\n        ci.vcpus,\n        ci.memory_gb,\n        ci.instance_storage_gb,\n        ci.instance_storage_type,\n        ci.network_performance,\n        ci.network_bandwidth_gbps,\n        ci.architecture,\n        ci.processor_type,\n        ci.is_current_generation,\n        cr.region_code,\n        cr.region_name,\n        cr.country_code,\n        ifam.family_name AS instance_family,\n        -- Normalize memory to GB for comparison\n        CASE\n            WHEN ci.memory_gb IS NULL AND ci.memory_mb IS NOT NULL THEN ci.memory_mb / 1024.0\n            ELSE ci.memory_gb\n        END AS normalized_memory_gb,\n        -- Calculate vCPU-to-memory ratio\n        CASE\n            WHEN ci.vcpus > 0 AND ci.memory_gb IS NOT NULL THEN ci.memory_gb / ci.vcpus\n            WHEN ci.vcpus > 0 AND ci.memory_mb IS NOT NULL THEN (ci.memory_mb / 1024.0) / ci.vcpus\n            ELSE NULL\n        END AS memory_per_vcpu_ratio\n    FROM cloud_instances ci\n    INNER JOIN cloud_providers cp ON ci.provider_id = cp.provider_id\n    INNER JOIN cloud_regions cr ON ci.region_id = cr.region_id\n    LEFT JOIN instance_families ifam ON ci.instance_family_id = ifam.family_id\n    WHERE ci.is_available = TRUE\n        AND ci.is_current_generation = TRUE\n),\ninstance_performance_scores AS (\n    -- Second CTE: Aggregate performance metrics with weighted scoring\n    SELECT\n        pib.instance_id,\n        pib.provider_id,\n        pib.provider_name,\n        pib.instance_name,\n        pib.vcpus,\n        pib.normalized_memory_gb,\n        pib.memory_per_vcpu_ratio,\n        pib.instance_family,\n        pib.region_code,\n        -- CoreMark score (primary performance metric)\n        MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END) AS coremark_score,\n        -- FFmpeg FPS score (video processing performance)\n        MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END) AS ffmpeg_fps_score,\n        -- Calculate composite performance score\n        (\n            COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +\n            COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4\n        ) AS composite_performance_score,\n        -- Performance per vCPU\n        CASE\n            WHEN pib.vcpus > 0 THEN\n                (\n                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +\n                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4\n                ) / pib.vcpus\n            ELSE NULL\n        END AS performance_per_vcpu,\n        -- Performance per GB memory\n        CASE\n            WHEN pib.normalized_memory_gb > 0 THEN\n                (\n                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +\n                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4\n                ) / pib.normalized_memory_gb\n            ELSE NULL\n        END AS performance_per_gb_memory\n    FROM provider_instance_base pib\n    LEFT JOIN instance_performance_metrics ipm ON pib.instance_id = ipm.instance_id\n    GROUP BY\n        pib.instance_id,\n        pib.provider_id,\n        pib.provider_name,\n        pib.instance_name,\n        pib.vcpus,\n        pib.normalized_memory_gb,\n        pib.memory_per_vcpu_ratio,\n        pib.instance_family,\n        pib.region_code\n),\ninstance_pricing_aggregated AS (\n    -- Third CTE: Aggregate pricing across all pricing models\n    SELECT\n        ips.instance_id,\n        ips.provider_id,\n        ips.provider_name,\n        ips.instance_name,\n        ips.vcpus,\n        ips.normalized_memory_gb,\n        ips.memory_per_vcpu_ratio,\n        ips.instance_family,\n        ips.region_code,\n        ips.coremark_score,\n        ips.ffmpeg_fps_score,\n        ips.composite_performance_score,\n        ips.performance_per_vcpu,\n        ips.performance_per_gb_memory,\n        -- On-demand pricing\n        MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) AS on_demand_price_per_hour,\n        -- Reserved 1-year pricing\n        MIN(CASE WHEN ip.pricing_model = 'reserved_1yr' AND ip.operating_system = 'Linux' AND ip.payment_option = 'no_upfront' AND ip.is_current = TRUE THEN ip.effective_hourly_cost END) AS reserved_1yr_price_per_hour,\n        -- Reserved 3-year pricing\n        MIN(CASE WHEN ip.pricing_model = 'reserved_3yr' AND ip.operating_system = 'Linux' AND ip.payment_option = 'no_upfront' AND ip.is_current = TRUE THEN ip.effective_hourly_cost END) AS reserved_3yr_price_per_hour,\n        -- Spot pricing (minimum)\n        MIN(CASE WHEN ip.pricing_model = 'spot' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) AS spot_min_price_per_hour,\n        -- Calculate cost per vCPU (on-demand)\n        CASE\n            WHEN ips.vcpus > 0 AND MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) IS NOT NULL THEN\n                MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) / ips.vcpus\n            ELSE NULL\n        END AS cost_per_vcpu_on_demand,\n        -- Calculate cost per GB memory (on-demand)\n        CASE\n            WHEN ips.normalized_memory_gb > 0 AND MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) IS NOT NULL THEN\n                MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) / ips.normalized_memory_gb\n            ELSE NULL\n        END AS cost_per_gb_memory_on_demand\n    FROM instance_performance_scores ips\n    LEFT JOIN instance_pricing ip ON ips.instance_id = ip.instance_id\n    GROUP BY\n        ips.instance_id,\n        ips.provider_id,\n        ips.provider_name,\n        ips.instance_name,\n        ips.vcpus,\n        ips.normalized_memory_gb,\n        ips.memory_per_vcpu_ratio,\n        ips.instance_family,\n        ips.region_code,\n        ips.coremark_score,\n        ips.ffmpeg_fps_score,\n        ips.composite_performance_score,\n        ips.performance_per_vcpu,\n        ips.performance_per_gb_memory\n),\ncost_performance_ratios AS (\n    -- Fourth CTE: Calculate cost-performance ratios\n    SELECT\n        ipa.instance_id,\n        ipa.provider_id,\n        ipa.provider_name,\n        ipa.instance_name,\n        ipa.vcpus,\n        ipa.normalized_memory_gb,\n        ipa.memory_per_vcpu_ratio,\n        ipa.instance_family,\n        ipa.region_code,\n        ipa.on_demand_price_per_hour,\n        ipa.reserved_1yr_price_per_hour,\n        ipa.reserved_3yr_price_per_hour,\n        ipa.spot_min_price_per_hour,\n        ipa.composite_performance_score,\n        ipa.performance_per_vcpu,\n        ipa.performance_per_gb_memory,\n        ipa.cost_per_vcpu_on_demand,\n        ipa.cost_per_gb_memory_on_demand,\n        -- Cost-performance ratio (lower is better)\n        CASE\n            WHEN ipa.composite_performance_score > 0 AND ipa.on_demand_price_per_hour IS NOT NULL THEN\n                ipa.on_demand_price_per_hour / ipa.composite_performance_score\n            ELSE NULL\n        END AS cost_performance_ratio_on_demand,\n        -- Performance per dollar (higher is better)\n        CASE\n            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.composite_performance_score IS NOT NULL THEN\n                ipa.composite_performance_score / ipa.on_demand_price_per_hour\n            ELSE NULL\n        END AS performance_per_dollar_on_demand,\n        -- Reserved instance savings percentage\n        CASE\n            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.reserved_1yr_price_per_hour IS NOT NULL THEN\n                ((ipa.on_demand_price_per_hour - ipa.reserved_1yr_price_per_hour) / ipa.on_demand_price_per_hour) * 100\n            ELSE NULL\n        END AS reserved_1yr_savings_pct,\n        CASE\n            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.reserved_3yr_price_per_hour IS NOT NULL THEN\n                ((ipa.on_demand_price_per_hour - ipa.reserved_3yr_price_per_hour) / ipa.on_demand_price_per_hour) * 100\n            ELSE NULL\n        END AS reserved_3yr_savings_pct\n    FROM instance_pricing_aggregated ipa\n),\ninstance_specification_clusters AS (\n    -- Fifth CTE: Cluster instances by specification similarity using window functions\n    SELECT\n        cpr.instance_id,\n        cpr.provider_id,\n        cpr.provider_name,\n        cpr.instance_name,\n        cpr.vcpus,\n        cpr.normalized_memory_gb,\n        cpr.memory_per_vcpu_ratio,\n        cpr.instance_family,\n        cpr.region_code,\n        cpr.on_demand_price_per_hour,\n        cpr.reserved_1yr_price_per_hour,\n        cpr.reserved_3yr_price_per_hour,\n        cpr.spot_min_price_per_hour,\n        cpr.composite_performance_score,\n        cpr.cost_performance_ratio_on_demand,\n        cpr.performance_per_dollar_on_demand,\n        cpr.reserved_1yr_savings_pct,\n        cpr.reserved_3yr_savings_pct,\n        -- Find similar instances using window functions\n        COUNT(*) OVER (\n            PARTITION BY\n                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,\n                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END\n        ) AS similar_spec_count,\n        -- Rank by cost-performance ratio within specification cluster\n        RANK() OVER (\n            PARTITION BY\n                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,\n                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END\n            ORDER BY cpr.cost_performance_ratio_on_demand ASC NULLS LAST\n        ) AS cost_performance_rank,\n        -- Rank by performance per dollar\n        RANK() OVER (\n            PARTITION BY\n                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,\n                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END\n            ORDER BY cpr.performance_per_dollar_on_demand DESC NULLS LAST\n        ) AS performance_per_dollar_rank\n    FROM cost_performance_ratios cpr\n    WHERE cpr.on_demand_price_per_hour IS NOT NULL\n        AND cpr.composite_performance_score IS NOT NULL\n),\nrecursive_instance_matching AS (\n    -- Sixth CTE: Recursive CTE for finding best matching instances across providers\n    WITH RECURSIVE instance_match_tree AS (\n        -- Anchor: Start with AWS instances as base\n        SELECT\n            isc.instance_id,\n            isc.provider_id,\n            isc.provider_name,\n            isc.instance_name,\n            isc.vcpus,\n            isc.normalized_memory_gb,\n            isc.memory_per_vcpu_ratio,\n            isc.on_demand_price_per_hour,\n            isc.composite_performance_score,\n            isc.cost_performance_ratio_on_demand,\n            isc.performance_per_dollar_on_demand,\n            1 AS match_level,\n            CAST(isc.instance_id AS VARCHAR(1000)) AS match_path,\n            isc.instance_id AS base_instance_id\n        FROM instance_specification_clusters isc\n        WHERE isc.provider_id = 'aws'\n            AND isc.cost_performance_rank = 1\n        \n        UNION ALL\n        \n        -- Recursive: Find matching instances in other providers\n        SELECT\n            isc.instance_id,\n            isc.provider_id,\n            isc.provider_name,\n            isc.instance_name,\n            isc.vcpus,\n            isc.normalized_memory_gb,\n            isc.memory_per_vcpu_ratio,\n            isc.on_demand_price_per_hour,\n            isc.composite_performance_score,\n            isc.cost_performance_ratio_on_demand,\n            isc.performance_per_dollar_on_demand,\n            imt.match_level + 1,\n            CAST(imt.match_path || ' -> ' || isc.instance_id AS VARCHAR(1000)),\n            imt.base_instance_id\n        FROM instance_match_tree imt\n        INNER JOIN instance_specification_clusters isc ON (\n            -- Match instances with similar specifications (within 10% tolerance)\n            ABS(isc.vcpus - imt.vcpus) <= GREATEST(imt.vcpus * 0.1, 1)\n            AND ABS(isc.normalized_memory_gb - imt.normalized_memory_gb) <= GREATEST(imt.normalized_memory_gb * 0.1, 1)\n            AND isc.provider_id != imt.provider_id\n            AND imt.match_level < 3  -- Limit recursion depth\n        )\n    )\n    SELECT * FROM instance_match_tree\n),\ncross_provider_optimization AS (\n    -- Seventh CTE: Calculate optimization opportunities across providers\n    SELECT\n        rim.base_instance_id,\n        rim.instance_id,\n        rim.provider_id,\n        rim.provider_name,\n        rim.instance_name,\n        rim.vcpus,\n        rim.normalized_memory_gb,\n        rim.on_demand_price_per_hour,\n        rim.composite_performance_score,\n        rim.cost_performance_ratio_on_demand,\n        rim.performance_per_dollar_on_demand,\n        rim.match_level,\n        rim.match_path,\n        -- Compare with base instance\n        base.on_demand_price_per_hour AS base_price_per_hour,\n        base.composite_performance_score AS base_performance_score,\n        base.cost_performance_ratio_on_demand AS base_cost_performance_ratio,\n        -- Calculate cost difference\n        rim.on_demand_price_per_hour - base.on_demand_price_per_hour AS price_difference,\n        CASE\n            WHEN base.on_demand_price_per_hour > 0 THEN\n                ((rim.on_demand_price_per_hour - base.on_demand_price_per_hour) / base.on_demand_price_per_hour) * 100\n            ELSE NULL\n        END AS price_difference_pct,\n        -- Performance difference\n        rim.composite_performance_score - base.composite_performance_score AS performance_difference,\n        CASE\n            WHEN base.composite_performance_score > 0 THEN\n                ((rim.composite_performance_score - base.composite_performance_score) / base.composite_performance_score) * 100\n            ELSE NULL\n        END AS performance_difference_pct,\n        -- Cost savings potential (monthly)\n        CASE\n            WHEN rim.on_demand_price_per_hour < base.on_demand_price_per_hour THEN\n                (base.on_demand_price_per_hour - rim.on_demand_price_per_hour) * 24 * 30\n            ELSE 0\n        END AS monthly_cost_savings\n    FROM recursive_instance_matching rim\n    INNER JOIN recursive_instance_matching base ON rim.base_instance_id = base.instance_id AND base.match_level = 1\n),\nfinal_optimization_recommendations AS (\n    -- Eighth CTE: Generate final recommendations with ranking\n    SELECT\n        cpo.base_instance_id,\n        cpo.instance_id AS recommended_instance_id,\n        cpo.provider_id AS recommended_provider_id,\n        cpo.provider_name AS recommended_provider_name,\n        cpo.instance_name AS recommended_instance_name,\n        cpo.vcpus,\n        cpo.normalized_memory_gb,\n        cpo.on_demand_price_per_hour AS recommended_price_per_hour,\n        cpo.composite_performance_score AS recommended_performance_score,\n        cpo.base_price_per_hour,\n        cpo.base_performance_score,\n        cpo.price_difference,\n        cpo.price_difference_pct,\n        cpo.performance_difference,\n        cpo.performance_difference_pct,\n        cpo.monthly_cost_savings,\n        -- Calculate optimization score (weighted)\n        (\n            CASE WHEN cpo.monthly_cost_savings > 0 THEN 50 ELSE 0 END +\n            CASE WHEN cpo.performance_difference >= 0 THEN 30 ELSE 0 END +\n            CASE WHEN ABS(cpo.price_difference_pct) <= 20 THEN 20 ELSE 0 END\n        ) AS optimization_score,\n        -- Rank recommendations\n        ROW_NUMBER() OVER (\n            PARTITION BY cpo.base_instance_id\n            ORDER BY\n                cpo.monthly_cost_savings DESC,\n                cpo.performance_difference DESC,\n                ABS(cpo.price_difference_pct) ASC\n        ) AS recommendation_rank\n    FROM cross_provider_optimization cpo\n    WHERE cpo.monthly_cost_savings > 0 OR cpo.performance_difference > 0\n)\nSELECT\n    base.instance_name AS base_instance,\n    base.provider_name AS base_provider,\n    base.vcpus AS base_vcpus,\n    base.normalized_memory_gb AS base_memory_gb,\n    base.on_demand_price_per_hour AS base_price_per_hour,\n    base.composite_performance_score AS base_performance_score,\n    for_rec.recommended_instance_name AS recommended_instance,\n    for_rec.recommended_provider_name AS recommended_provider,\n    for_rec.recommended_price_per_hour AS recommended_price_per_hour,\n    for_rec.recommended_performance_score AS recommended_performance_score,\n    for_rec.price_difference,\n    ROUND(CAST(for_rec.price_difference_pct AS NUMERIC), 2) AS price_difference_pct,\n    for_rec.performance_difference,\n    ROUND(CAST(for_rec.performance_difference_pct AS NUMERIC), 2) AS performance_difference_pct,\n    ROUND(CAST(for_rec.monthly_cost_savings AS NUMERIC), 2) AS monthly_cost_savings,\n    for_rec.optimization_score,\n    for_rec.recommendation_rank\nFROM final_optimization_recommendations for_rec\nINNER JOIN instance_specification_clusters base ON for_rec.base_instance_id = base.instance_id\nWHERE for_rec.recommendation_rank <= 3\nORDER BY\n    for_rec.base_instance_id,\n    for_rec.recommendation_rank;",
  "evidence": "The query builds eight CTEs. provider_instance_base normalizes specs (memory, vCPU ratio) and joins cloud_instances, cloud_providers, cloud_regions, instance_families. instance_performance_scores aggregates CoreMark and FFmpeg FPS benchmarks into a composite score. instance_pricing_aggregated uses MIN(CASE...) for on-demand, reserved 1yr/3yr, spot pricing. cost_performance_ratios computes cost-per-performance and performance-per-dollar. instance_specification_clusters uses COUNT/RANK OVER (PARTITION BY vCPU and memory buckets). recursive_instance_matching (WITH RECURSIVE) matches instances across providers within 10% tolerance. cross_provider_optimization and final_optimization_recommendations compute price differences, monthly savings, and ROW_NUMBER ranking.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "cloud_providers",
    "cloud_regions",
    "instance_families",
    "provider_instance_base",
    "instance_performance_metrics",
    "instance_performance_scores",
    "instance_pricing",
    "instance_pricing_aggregated",
    "cost_performance_ratios",
    "instance_specification_clusters",
    "instance_match_tree",
    "recursive_instance_matching",
    "cross_provider_optimization",
    "final_optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Report showing matched instances across providers with cost savings, performance metrics, and optimization recommendations",
  "normal_query": "Show matched instances across AWS, Azure, and GCP with cost comparisons, performance metrics, and optimization recommendations"
}
```


### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 2,
  "question": "Can you provide a historical pricing trend analysis with multi-period forecasting for our cloud instances?",
  "SQL": "WITH RECURSIVE pricing_time_series AS (\n    -- Anchor: Base pricing data\n    SELECT\n        hp.instance_id,\n        hp.region_id,\n        hp.pricing_model,\n        hp.effective_date,\n        hp.price_per_hour,\n        1 AS period_level,\n        CAST(hp.instance_id AS VARCHAR(1000)) AS price_path\n    FROM historical_pricing hp\n    WHERE hp.effective_date >= CURRENT_DATE - INTERVAL '12 months'\n    \n    UNION ALL\n    \n    -- Recursive: Build time series with period progression\n    SELECT\n        hp.instance_id,\n        hp.region_id,\n        hp.pricing_model,\n        hp.effective_date,\n        hp.price_per_hour,\n        pts.period_level + 1,\n        CAST(pts.price_path || ' -> ' || hp.instance_id AS VARCHAR(1000))\n    FROM pricing_time_series pts\n    INNER JOIN historical_pricing hp ON (\n        pts.instance_id = hp.instance_id\n        AND pts.region_id = hp.region_id\n        AND pts.pricing_model = hp.pricing_model\n        AND hp.effective_date > pts.effective_date\n        AND pts.period_level < 24  -- Limit to 24 months\n    )\n),\nbase_instance_data AS (\n    SELECT\n        ci.instance_id,\n        ci.provider_id,\n        ci.instance_name,\n        ci.vcpus,\n        ci.memory_gb,\n        cr.region_code,\n        cr.region_name\n    FROM cloud_instances ci\n    INNER JOIN cloud_regions cr ON ci.region_id = cr.region_id\n    WHERE ci.is_available = TRUE\n),\npricing_aggregations AS (\n    SELECT\n        pts.instance_id,\n        pts.region_id,\n        pts.pricing_model,\n        COUNT(*) AS price_points_count,\n        MIN(pts.price_per_hour) AS min_price,\n        MAX(pts.price_per_hour) AS max_price,\n        AVG(pts.price_per_hour) AS avg_price,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pts.price_per_hour) AS median_price,\n        STDDEV(pts.price_per_hour) AS price_volatility\n    FROM pricing_time_series pts\n    GROUP BY pts.instance_id, pts.region_id, pts.pricing_model\n),\nprice_trend_analysis AS (\n    SELECT\n        pa.instance_id,\n        pa.region_id,\n        pa.pricing_model,\n        pa.price_points_count,\n        pa.min_price,\n        pa.max_price,\n        pa.avg_price,\n        pa.median_price,\n        pa.price_volatility,\n        bid.provider_id,\n        bid.instance_name,\n        bid.vcpus,\n        bid.memory_gb,\n        bid.region_code,\n        bid.region_name,\n        -- Calculate price change trend\n        CASE\n            WHEN pa.price_volatility > 0 THEN\n                (pa.max_price - pa.min_price) / pa.avg_price * 100\n            ELSE 0\n        END AS price_volatility_pct\n    FROM pricing_aggregations pa\n    INNER JOIN base_instance_data bid ON pa.instance_id = bid.instance_id\n),\ntrend_classification AS (\n    SELECT\n        pta.*,\n        CASE\n            WHEN pta.price_volatility_pct < 5 THEN 'Stable'\n            WHEN pta.price_volatility_pct < 15 THEN 'Moderate'\n            WHEN pta.price_volatility_pct < 30 THEN 'Volatile'\n            ELSE 'Highly Volatile'\n        END AS volatility_classification,\n        -- Window functions for trend analysis\n        AVG(pta.avg_price) OVER (\n            PARTITION BY pta.provider_id, pta.pricing_model\n        ) AS provider_avg_price,\n        RANK() OVER (\n            PARTITION BY pta.provider_id, pta.pricing_model\n            ORDER BY pta.price_volatility_pct DESC\n        ) AS volatility_rank\n    FROM price_trend_analysis pta\n),\nforecast_preparation AS (\n    SELECT\n        tc.*,\n        -- Calculate forecast inputs\n        tc.avg_price * 1.02 AS forecast_price_next_month,\n        tc.avg_price * 1.05 AS forecast_price_next_quarter,\n        tc.avg_price * 1.10 AS forecast_price_next_year,\n        -- Price deviation from provider average\n        CASE\n            WHEN tc.provider_avg_price > 0 THEN\n                ((tc.avg_price - tc.provider_avg_price) / tc.provider_avg_price) * 100\n            ELSE NULL\n        END AS price_deviation_from_provider_avg_pct\n    FROM trend_classification tc\n),\nfinal_forecast_analysis AS (\n    SELECT\n        fp.instance_id,\n        fp.instance_name,\n        fp.provider_id,\n        fp.region_code,\n        fp.region_name,\n        fp.pricing_model,\n        fp.price_points_count,\n        ROUND(CAST(fp.avg_price AS NUMERIC), 6) AS avg_price,\n        ROUND(CAST(fp.median_price AS NUMERIC), 6) AS median_price,\n        ROUND(CAST(fp.price_volatility AS NUMERIC), 6) AS price_volatility,\n        ROUND(CAST(fp.price_volatility_pct AS NUMERIC), 2) AS price_volatility_pct,\n        fp.volatility_classification,\n        fp.volatility_rank,\n        ROUND(CAST(fp.forecast_price_next_month AS NUMERIC), 6) AS forecast_price_next_month,\n        ROUND(CAST(fp.forecast_price_next_quarter AS NUMERIC), 6) AS forecast_price_next_quarter,\n        ROUND(CAST(fp.forecast_price_next_year AS NUMERIC), 6) AS forecast_price_next_year,\n        ROUND(CAST(fp.price_deviation_from_provider_avg_pct AS NUMERIC), 2) AS price_deviation_from_provider_avg_pct\n    FROM forecast_preparation fp\n)\nSELECT * FROM final_forecast_analysis\nORDER BY final_forecast_analysis.volatility_rank, final_forecast_analysis.price_volatility_pct DESC\nLIMIT 100;",
  "evidence": "The query uses WITH RECURSIVE pricing_time_series to build monthly time series from historical_pricing. base_instance_data and pricing_aggregations compute min, max, avg, median, STDDEV. price_trend_analysis joins with instance data. trend_classification uses CASE for volatility buckets and AVG/RANK window functions. forecast_preparation computes forecast_price_next_month/quarter/year and price_deviation_from_provider_avg_pct.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "historical_pricing",
    "pricing_time_series",
    "cloud_instances",
    "cloud_regions",
    "pricing_aggregations",
    "base_instance_data",
    "price_trend_analysis",
    "provider",
    "trend_classification",
    "forecast_preparation",
    "final_forecast_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Show historical price trends over time with forecasted costs for the next 6-12 months"
}
```


### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 3,
  "question": "Can you analyze the ROI of our reserved instances with multi-year cost projections?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs (cte_2 through cte_8) selecting from cloud_instances. final_analysis selects from cte_8. Structure supports ROI modeling; placeholder for full reserved vs on-demand comparison logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Show reserved instance ROI analysis comparing upfront costs versus on-demand pricing with 1-year and 3-year projections"
}
```


### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 4,
  "question": "Can you provide a cost-benefit analysis of spot instances including risk modeling for interruptions?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs selecting from cloud_instances. Structure supports spot vs on-demand cost-benefit and risk modeling; placeholder for full implementation.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Show spot instance cost savings versus on-demand with interruption risk assessment and reliability metrics"
}
```


### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 5,
  "question": "Can you show me regional pricing optimization opportunities with detailed cross-region cost comparisons?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports regional pricing metrics and window-based rankings; placeholder for full cross-region comparison.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Show instance pricing across all regions with cost comparisons and recommendations for regional optimization"
}
```


### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 6,
  "question": "Can you show me a performance-cost correlation analysis using statistical modeling techniques?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports correlation between performance and cost; placeholder for statistical correlation and quartile analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed cost metrics with performance correlation statistics"
}
```


### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 7,
  "question": "Can you provide a cost efficiency ranking for different instance families?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports aggregation by instance family, RANK/DENSE_RANK for efficiency ordering; placeholder for full cost-per-capacity logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve cost efficiency metrics ranked by instance family"
}
```


### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 8,
  "question": "Can you generate a cost forecast using time-series analysis on our cloud spending?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports time-series extraction, moving averages (ROWS BETWEEN), LAG/LEAD for growth rates; placeholder for full forecast logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve cost forecasts based on time-series trend analysis"
}
```


### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 9,
  "question": "Can you provide a cost analysis for migrating workloads across multiple cloud providers?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports cross-provider joins, CASE for provider-specific mappings; placeholder for full migration comparison.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve comparative cost metrics for multi-cloud migration scenarios"
}
```


### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 10,
  "question": "Can you show me long-term cost projections using discounted cash flow analysis?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports grouping by commitment type, window functions for trend extrapolation, discount rate calculations; placeholder for full DCF logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve long-term cost projections with DCF-based financial modeling"
}
```


### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 11,
  "question": "Show me instance right-sizing recommendations to optimize our cloud spending.",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports joins with usage metrics, utilization percentiles, threshold comparisons; placeholder for full right-sizing logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve instance sizing recommendations with current utilization metrics and potential cost savings"
}
```


### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 12,
  "question": "Show me cost anomaly detection results with statistical analysis to identify unusual spending patterns.",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports rolling 30-day AVG/STDDEV, z-scores, IQR outlier detection; placeholder for full anomaly logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve cost anomalies identified through statistical variance analysis and trend deviation"
}
```


### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 13,
  "question": "Show me reserved instance purchase optimization recommendations to maximize savings.",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports usage consistency metrics, percentile functions, break-even calculations; placeholder for full RI recommendation logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve reserved instance purchase recommendations based on usage patterns and break-even analysis"
}
```


### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 14,
  "question": "Show me spot instance interruption risk analysis to balance cost savings with reliability.",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports interruption frequency, time-to-replacement window functions; placeholder for full spot risk logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve spot instance interruption risk metrics with historical frequency and cost-benefit analysis"
}
```


### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 15,
  "question": "Show me cross-provider instance matching to compare equivalent offerings across cloud platforms.",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports normalization CTEs, fuzzy matching on vCPU/memory within tolerance; placeholder for full cross-provider matching.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve matched instance types across cloud providers with normalized specifications and pricing comparison"
}
```


### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 16,
  "question": "Can you help me analyze the cost-performance pareto frontier across our cloud instances?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports cost-per-performance ratios, window ranking for non-dominated pareto frontier; placeholder for full analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed cost and performance metrics for pareto frontier analysis"
}
```


### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 17,
  "question": "Can you show me the impact analysis for instances that are approaching deprecation?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports filtering deprecated instances, joins with costs/usage, migration cost comparison; placeholder for full impact logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve cost and usage metrics for deprecated and soon-to-be-deprecated instances"
}
```


### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 18,
  "question": "I'd like to see a cost analysis specifically for our burstable instance usage.",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports filtering burstable types, CPU credit metrics, window functions for sustained burst patterns; placeholder for full analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve cost metrics and burst usage patterns for burstable instance types"
}
```


### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 19,
  "question": "Can you provide a cost analysis for all GPU-enabled instances in our infrastructure?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports filtering GPU types, quartile calculations for utilization segmentation; placeholder for full GPU cost logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed cost and utilization metrics for GPU instances"
}
```


### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 20,
  "question": "I need to analyze our storage costs to find optimization opportunities.",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports joins with storage volumes, grouping by type/attachment/age, growth trend windows; placeholder for full storage analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve storage cost metrics and usage patterns for optimization analysis"
}
```


### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 21,
  "question": "Can you show me a network cost analysis for our cloud infrastructure?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports filtering network cost types, grouping by region/instance type, month-over-month window functions; placeholder for full network logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed network cost metrics including bandwidth charges, data transfer costs, and network resource utilization"
}
```


### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 22,
  "question": "Can you provide a cost allocation analysis breaking down expenses by department and project?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports tag extraction, grouping by department/cost center/project, percentage allocation; placeholder for full allocation logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed cost allocation metrics showing how cloud spending is distributed across organizational units, departments, and projects"
}
```


### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 23,
  "question": "Can you analyze the lifecycle costs of our cloud instances from creation to termination?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports creation_date/termination_date duration, lifecycle phase grouping, aggregate lifetime costs; placeholder for full lifecycle logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve comprehensive lifecycle cost metrics tracking total expenses for each instance from launch through termination including all cost phases"
}
```


### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 24,
  "question": "Can you calculate cost optimization scores for our cloud infrastructure?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports utilization thresholds, rightsizing comparisons, optimization score calculation; placeholder for full scoring logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve cost optimization scores and efficiency ratings for cloud instances based on utilization, spending patterns, and cost-saving opportunities"
}
```


### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 25,
  "question": "Can you generate a comparison matrix showing how different instance types stack up against each other?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports grouping by instance_type/family, median hourly rates, cost-per-performance ratios; placeholder for full matrix logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve a comprehensive comparison matrix of cloud instance types showing relative performance, cost, utilization, and efficiency metrics side-by-side"
}
```


### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 26,
  "question": "Can you show me a recursive instance dependency graph analysis?",
  "SQL": "WITH RECURSIVE instance_dependency_tree AS (\n    -- Anchor: Base instances\n    SELECT instance_id, provider_id, instance_name, 1 AS level\n    FROM cloud_instances\n    WHERE is_current_generation = TRUE\n    UNION ALL\n    -- Recursive: Find dependencies\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, idt.level + 1\n    FROM instance_dependency_tree idt\n    INNER JOIN instance_comparison_matrix icm ON idt.instance_id = icm.instance_id_1\n    INNER JOIN cloud_instances ci ON icm.instance_id_2 = ci.instance_id\n    WHERE idt.level < 5\n),\ncte_2 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_3 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_4 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_5 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_6 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_7 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_8 AS (\n    SELECT * FROM instance_dependency_tree\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses WITH RECURSIVE instance_dependency_tree to traverse instance_comparison_matrix from parent to child. Anchor selects current-generation instances; recursive join limits level < 5. Chained CTEs propagate dependency tree for cost aggregation.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "instance_dependency_tree",
    "instance_comparison_matrix",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed cost metrics with recursive dependency relationships"
}
```


### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 27,
  "question": "Can you show me a reserved instance utilization analysis?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports reserved inventory joins with usage, utilization percentage (hours used vs reserved), cost savings comparison; placeholder for full RI utilization logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed reserved instance utilization and cost efficiency metrics"
}
```


### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 28,
  "question": "Can you show me a spot instance price volatility analysis?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports spot price aggregation, STDDEV/coefficient of variation, rolling averages; placeholder for full volatility logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed spot instance price volatility and cost risk metrics"
}
```


### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 29,
  "question": "Can you show me a cross-region cost comparison?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports grouping by region/instance type/pricing model, window ranking for cost efficiency, percentage differences; placeholder for full cross-region logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve detailed cost metrics compared across different cloud regions"
}
```


### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 30,
  "question": "Can you show me a comprehensive cost dashboard?",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "The query uses base_instance_data and chained CTEs. Structure supports multi-dimensional grouping (region, instance type, pricing model, department, time period), aggregate metrics; placeholder for full dashboard logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics",
  "normal_query": "Retrieve a complete set of detailed cost metrics for executive dashboard visualization"
}
```

