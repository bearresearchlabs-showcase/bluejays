# Cloud Instance Cost Database — Query Documentation

## Database Overview

```yaml
db_id: db-14
domain: Database domain
source: [synthetic / open / commercial]
license_type: [Commercial / Open / Academic]
license_cost: [Annual cost if applicable]
tables: 0
total_rows: ~0
date_range: 2020-01-01 to 2024-12-31
sql_dialect: PostgreSQL
```

## Purpose

```text
This database supports analytics for db-14.
```

## Use Case

```text
Target use cases for db-14: analytics, reporting, dashboards.
```

## Business Value

```text
Business value for db-14.
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
Domain-specific concepts for this database.
```

## Query Difficulty Distribution

```text
Target distribution across 30 queries:
- simple (10): Single-table, basic aggregation
- moderate (12): 2-3 table joins, GROUP BY
- challenging (8): CTEs, window functions
```

## Queries

### Query 1 — challenging / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 1,
  "question": "Multi-Provider Cost-Performance Analysis with Recursive Instance Matching and Cross-Cloud Optimization Recommendations",
  "SQL": "WITH provider_instance_base AS (\n    -- First CTE: Base instance data with normalized specifications\n    SELECT\n        ci.instance_id,\n        ci.provider_id,\n        cp.provider_name,\n        ci.instance_name,\n        ci.api_name,\n        ci.vcpus,\n        ci.memory_gb,\n        ci.instance_storage_gb,\n        ci.instance_storage_type,\n        ci.network_performance,\n        ci.network_bandwidth_gbps,\n        ci.architecture,\n        ci.processor_type,\n        ci.is_current_generation,\n        cr.region_code,\n        cr.region_name,\n        cr.country_code,\n        ifam.family_name AS instance_family,\n        -- Normalize memory to GB for comparison\n        CASE\n            WHEN ci.memory_gb IS NULL AND ci.memory_mb IS NOT NULL THEN ci.memory_mb / 1024.0\n            ELSE ci.memory_gb\n        END AS normalized_memory_gb,\n        -- Calculate vCPU-to-memory ratio\n        CASE\n            WHEN ci.vcpus > 0 AND ci.memory_gb IS NOT NULL THEN ci.memory_gb / ci.vcpus\n            WHEN ci.vcpus > 0 AND ci.memory_mb IS NOT NULL THEN (ci.memory_mb / 1024.0) / ci.vcpus\n            ELSE NULL\n        END AS memory_per_vcpu_ratio\n    FROM cloud_instances ci\n    INNER JOIN cloud_providers cp ON ci.provider_id = cp.provider_id\n    INNER JOIN cloud_regions cr ON ci.region_id = cr.region_id\n    LEFT JOIN instance_families ifam ON ci.instance_family_id = ifam.family_id\n    WHERE ci.is_available = TRUE\n        AND ci.is_current_generation = TRUE\n),\ninstance_performance_scores AS (\n    -- Second CTE: Aggregate performance metrics with weighted scoring\n    SELECT\n        pib.instance_id,\n        pib.provider_id,\n        pib.provider_name,\n        pib.instance_name,\n        pib.vcpus,\n        pib.normalized_memory_gb,\n        pib.memory_per_vcpu_ratio,\n        pib.instance_family,\n        pib.region_code,\n        -- CoreMark score (primary performance metric)\n        MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END) AS coremark_score,\n        -- FFmpeg FPS score (video processing performance)\n        MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END) AS ffmpeg_fps_score,\n        -- Calculate composite performance score\n        (\n            COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +\n            COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4\n        ) AS composite_performance_score,\n        -- Performance per vCPU\n        CASE\n            WHEN pib.vcpus > 0 THEN\n                (\n                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +\n                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4\n                ) / pib.vcpus\n            ELSE NULL\n        END AS performance_per_vcpu,\n        -- Performance per GB memory\n        CASE\n            WHEN pib.normalized_memory_gb > 0 THEN\n                (\n                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +\n                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4\n                ) / pib.normalized_memory_gb\n            ELSE NULL\n        END AS performance_per_gb_memory\n    FROM provider_instance_base pib\n    LEFT JOIN instance_performance_metrics ipm ON pib.instance_id = ipm.instance_id\n    GROUP BY\n        pib.instance_id,\n        pib.provider_id,\n        pib.provider_name,\n        pib.instance_name,\n        pib.vcpus,\n        pib.normalized_memory_gb,\n        pib.memory_per_vcpu_ratio,\n        pib.instance_family,\n        pib.region_code\n),\ninstance_pricing_aggregated AS (\n    -- Third CTE: Aggregate pricing across all pricing models\n    SELECT\n        ips.instance_id,\n        ips.provider_id,\n        ips.provider_name,\n        ips.instance_name,\n        ips.vcpus,\n        ips.normalized_memory_gb,\n        ips.memory_per_vcpu_ratio,\n        ips.instance_family,\n        ips.region_code,\n        ips.coremark_score,\n        ips.ffmpeg_fps_score,\n        ips.composite_performance_score,\n        ips.performance_per_vcpu,\n        ips.performance_per_gb_memory,\n        -- On-demand pricing\n        MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) AS on_demand_price_per_hour,\n        -- Reserved 1-year pricing\n        MIN(CASE WHEN ip.pricing_model = 'reserved_1yr' AND ip.operating_system = 'Linux' AND ip.payment_option = 'no_upfront' AND ip.is_current = TRUE THEN ip.effective_hourly_cost END) AS reserved_1yr_price_per_hour,\n        -- Reserved 3-year pricing\n        MIN(CASE WHEN ip.pricing_model = 'reserved_3yr' AND ip.operating_system = 'Linux' AND ip.payment_option = 'no_upfront' AND ip.is_current = TRUE THEN ip.effective_hourly_cost END) AS reserved_3yr_price_per_hour,\n        -- Spot pricing (minimum)\n        MIN(CASE WHEN ip.pricing_model = 'spot' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) AS spot_min_price_per_hour,\n        -- Calculate cost per vCPU (on-demand)\n        CASE\n            WHEN ips.vcpus > 0 AND MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) IS NOT NULL THEN\n                MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) / ips.vcpus\n            ELSE NULL\n        END AS cost_per_vcpu_on_demand,\n        -- Calculate cost per GB memory (on-demand)\n        CASE\n            WHEN ips.normalized_memory_gb > 0 AND MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) IS NOT NULL THEN\n                MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) / ips.normalized_memory_gb\n            ELSE NULL\n        END AS cost_per_gb_memory_on_demand\n    FROM instance_performance_scores ips\n    LEFT JOIN instance_pricing ip ON ips.instance_id = ip.instance_id\n    GROUP BY\n        ips.instance_id,\n        ips.provider_id,\n        ips.provider_name,\n        ips.instance_name,\n        ips.vcpus,\n        ips.normalized_memory_gb,\n        ips.memory_per_vcpu_ratio,\n        ips.instance_family,\n        ips.region_code,\n        ips.coremark_score,\n        ips.ffmpeg_fps_score,\n        ips.composite_performance_score,\n        ips.performance_per_vcpu,\n        ips.performance_per_gb_memory\n),\ncost_performance_ratios AS (\n    -- Fourth CTE: Calculate cost-performance ratios\n    SELECT\n        ipa.instance_id,\n        ipa.provider_id,\n        ipa.provider_name,\n        ipa.instance_name,\n        ipa.vcpus,\n        ipa.normalized_memory_gb,\n        ipa.memory_per_vcpu_ratio,\n        ipa.instance_family,\n        ipa.region_code,\n        ipa.on_demand_price_per_hour,\n        ipa.reserved_1yr_price_per_hour,\n        ipa.reserved_3yr_price_per_hour,\n        ipa.spot_min_price_per_hour,\n        ipa.composite_performance_score,\n        ipa.performance_per_vcpu,\n        ipa.performance_per_gb_memory,\n        ipa.cost_per_vcpu_on_demand,\n        ipa.cost_per_gb_memory_on_demand,\n        -- Cost-performance ratio (lower is better)\n        CASE\n            WHEN ipa.composite_performance_score > 0 AND ipa.on_demand_price_per_hour IS NOT NULL THEN\n                ipa.on_demand_price_per_hour / ipa.composite_performance_score\n            ELSE NULL\n        END AS cost_performance_ratio_on_demand,\n        -- Performance per dollar (higher is better)\n        CASE\n            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.composite_performance_score IS NOT NULL THEN\n                ipa.composite_performance_score / ipa.on_demand_price_per_hour\n            ELSE NULL\n        END AS performance_per_dollar_on_demand,\n        -- Reserved instance savings percentage\n        CASE\n            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.reserved_1yr_price_per_hour IS NOT NULL THEN\n                ((ipa.on_demand_price_per_hour - ipa.reserved_1yr_price_per_hour) / ipa.on_demand_price_per_hour) * 100\n            ELSE NULL\n        END AS reserved_1yr_savings_pct,\n        CASE\n            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.reserved_3yr_price_per_hour IS NOT NULL THEN\n                ((ipa.on_demand_price_per_hour - ipa.reserved_3yr_price_per_hour) / ipa.on_demand_price_per_hour) * 100\n            ELSE NULL\n        END AS reserved_3yr_savings_pct\n    FROM instance_pricing_aggregated ipa\n),\ninstance_specification_clusters AS (\n    -- Fifth CTE: Cluster instances by specification similarity using window functions\n    SELECT\n        cpr.instance_id,\n        cpr.provider_id,\n        cpr.provider_name,\n        cpr.instance_name,\n        cpr.vcpus,\n        cpr.normalized_memory_gb,\n        cpr.memory_per_vcpu_ratio,\n        cpr.instance_family,\n        cpr.region_code,\n        cpr.on_demand_price_per_hour,\n        cpr.reserved_1yr_price_per_hour,\n        cpr.reserved_3yr_price_per_hour,\n        cpr.spot_min_price_per_hour,\n        cpr.composite_performance_score,\n        cpr.cost_performance_ratio_on_demand,\n        cpr.performance_per_dollar_on_demand,\n        cpr.reserved_1yr_savings_pct,\n        cpr.reserved_3yr_savings_pct,\n        -- Find similar instances using window functions\n        COUNT(*) OVER (\n            PARTITION BY\n                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,\n                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END\n        ) AS similar_spec_count,\n        -- Rank by cost-performance ratio within specification cluster\n        RANK() OVER (\n            PARTITION BY\n                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,\n                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END\n            ORDER BY cpr.cost_performance_ratio_on_demand ASC NULLS LAST\n        ) AS cost_performance_rank,\n        -- Rank by performance per dollar\n        RANK() OVER (\n            PARTITION BY\n                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,\n                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END\n            ORDER BY cpr.performance_per_dollar_on_demand DESC NULLS LAST\n        ) AS performance_per_dollar_rank\n    FROM cost_performance_ratios cpr\n    WHERE cpr.on_demand_price_per_hour IS NOT NULL\n        AND cpr.composite_performance_score IS NOT NULL\n),\nrecursive_instance_matching AS (\n    -- Sixth CTE: Recursive CTE for finding best matching instances across providers\n    WITH RECURSIVE instance_match_tree AS (\n        -- Anchor: Start with AWS instances as base\n        SELECT\n            isc.instance_id,\n            isc.provider_id,\n            isc.provider_name,\n            isc.instance_name,\n            isc.vcpus,\n            isc.normalized_memory_gb,\n            isc.memory_per_vcpu_ratio,\n            isc.on_demand_price_per_hour,\n            isc.composite_performance_score,\n            isc.cost_performance_ratio_on_demand,\n            isc.performance_per_dollar_on_demand,\n            1 AS match_level,\n            CAST(isc.instance_id AS VARCHAR(1000)) AS match_path,\n            isc.instance_id AS base_instance_id\n        FROM instance_specification_clusters isc\n        WHERE isc.provider_id = 'aws'\n            AND isc.cost_performance_rank = 1\n        \n        UNION ALL\n        \n        -- Recursive: Find matching instances in other providers\n        SELECT\n            isc.instance_id,\n            isc.provider_id,\n            isc.provider_name,\n            isc.instance_name,\n            isc.vcpus,\n            isc.normalized_memory_gb,\n            isc.memory_per_vcpu_ratio,\n            isc.on_demand_price_per_hour,\n            isc.composite_performance_score,\n            isc.cost_performance_ratio_on_demand,\n            isc.performance_per_dollar_on_demand,\n            imt.match_level + 1,\n            CAST(imt.match_path || ' -> ' || isc.instance_id AS VARCHAR(1000)),\n            imt.base_instance_id\n        FROM instance_match_tree imt\n        INNER JOIN instance_specification_clusters isc ON (\n            -- Match instances with similar specifications (within 10% tolerance)\n            ABS(isc.vcpus - imt.vcpus) <= GREATEST(imt.vcpus * 0.1, 1)\n            AND ABS(isc.normalized_memory_gb - imt.normalized_memory_gb) <= GREATEST(imt.normalized_memory_gb * 0.1, 1)\n            AND isc.provider_id != imt.provider_id\n            AND imt.match_level < 3  -- Limit recursion depth\n        )\n    )\n    SELECT * FROM instance_match_tree\n),\ncross_provider_optimization AS (\n    -- Seventh CTE: Calculate optimization opportunities across providers\n    SELECT\n        rim.base_instance_id,\n        rim.instance_id,\n        rim.provider_id,\n        rim.provider_name,\n        rim.instance_name,\n        rim.vcpus,\n        rim.normalized_memory_gb,\n        rim.on_demand_price_per_hour,\n        rim.composite_performance_score,\n        rim.cost_performance_ratio_on_demand,\n        rim.performance_per_dollar_on_demand,\n        rim.match_level,\n        rim.match_path,\n        -- Compare with base instance\n        base.on_demand_price_per_hour AS base_price_per_hour,\n        base.composite_performance_score AS base_performance_score,\n        base.cost_performance_ratio_on_demand AS base_cost_performance_ratio,\n        -- Calculate cost difference\n        rim.on_demand_price_per_hour - base.on_demand_price_per_hour AS price_difference,\n        CASE\n            WHEN base.on_demand_price_per_hour > 0 THEN\n                ((rim.on_demand_price_per_hour - base.on_demand_price_per_hour) / base.on_demand_price_per_hour) * 100\n            ELSE NULL\n        END AS price_difference_pct,\n        -- Performance difference\n        rim.composite_performance_score - base.composite_performance_score AS performance_difference,\n        CASE\n            WHEN base.composite_performance_score > 0 THEN\n                ((rim.composite_performance_score - base.composite_performance_score) / base.composite_performance_score) * 100\n            ELSE NULL\n        END AS performance_difference_pct,\n        -- Cost savings potential (monthly)\n        CASE\n            WHEN rim.on_demand_price_per_hour < base.on_demand_price_per_hour THEN\n                (base.on_demand_price_per_hour - rim.on_demand_price_per_hour) * 24 * 30\n            ELSE 0\n        END AS monthly_cost_savings\n    FROM recursive_instance_matching rim\n    INNER JOIN recursive_instance_matching base ON rim.base_instance_id = base.instance_id AND base.match_level = 1\n),\nfinal_optimization_recommendations AS (\n    -- Eighth CTE: Generate final recommendations with ranking\n    SELECT\n        cpo.base_instance_id,\n        cpo.instance_id AS recommended_instance_id,\n        cpo.provider_id AS recommended_provider_id,\n        cpo.provider_name AS recommended_provider_name,\n        cpo.instance_name AS recommended_instance_name,\n        cpo.vcpus,\n        cpo.normalized_memory_gb,\n        cpo.on_demand_price_per_hour AS recommended_price_per_hour,\n        cpo.composite_performance_score AS recommended_performance_score,\n        cpo.base_price_per_hour,\n        cpo.base_performance_score,\n        cpo.price_difference,\n        cpo.price_difference_pct,\n        cpo.performance_difference,\n        cpo.performance_difference_pct,\n        cpo.monthly_cost_savings,\n        -- Calculate optimization score (weighted)\n        (\n            CASE WHEN cpo.monthly_cost_savings > 0 THEN 50 ELSE 0 END +\n            CASE WHEN cpo.performance_difference >= 0 THEN 30 ELSE 0 END +\n            CASE WHEN ABS(cpo.price_difference_pct) <= 20 THEN 20 ELSE 0 END\n        ) AS optimization_score,\n        -- Rank recommendations\n        ROW_NUMBER() OVER (\n            PARTITION BY cpo.base_instance_id\n            ORDER BY\n                cpo.monthly_cost_savings DESC,\n                cpo.performance_difference DESC,\n                ABS(cpo.price_difference_pct) ASC\n        ) AS recommendation_rank\n    FROM cross_provider_optimization cpo\n    WHERE cpo.monthly_cost_savings > 0 OR cpo.performance_difference > 0\n)\nSELECT\n    base.instance_name AS base_instance,\n    base.provider_name AS base_provider,\n    base.vcpus AS base_vcpus,\n    base.normalized_memory_gb AS base_memory_gb,\n    base.on_demand_price_per_hour AS base_price_per_hour,\n    base.composite_performance_score AS base_performance_score,\n    for_rec.recommended_instance_name AS recommended_instance,\n    for_rec.recommended_provider_name AS recommended_provider,\n    for_rec.recommended_price_per_hour AS recommended_price_per_hour,\n    for_rec.recommended_performance_score AS recommended_performance_score,\n    for_rec.price_difference,\n    ROUND(CAST(for_rec.price_difference_pct AS NUMERIC), 2) AS price_difference_pct,\n    for_rec.performance_difference,\n    ROUND(CAST(for_rec.performance_difference_pct AS NUMERIC), 2) AS performance_difference_pct,\n    ROUND(CAST(for_rec.monthly_cost_savings AS NUMERIC), 2) AS monthly_cost_savings,\n    for_rec.optimization_score,\n    for_rec.recommendation_rank\nFROM final_optimization_recommendations for_rec\nINNER JOIN instance_specification_clusters base ON for_rec.base_instance_id = base.instance_id\nWHERE for_rec.recommendation_rank <= 3\nORDER BY\n    for_rec.base_instance_id,\n    for_rec.recommendation_rank;",
  "evidence": "Use Case: Cloud Cost Optimization - Cross-Cloud Instance Right-Sizing Analysis for Enterprise Migration Planning Description: Enterprise-level multi-provider cost-performance analysis using recursive CTE for instance matching across AWS, Azure, and GCP, with complex aggregations, window functions, percentile calculations, and cross-cloud optimization recommendations. Demonstrates production patterns used by cloud cost optimization platforms. Business Value: Comprehensive cost-performance compari",
  "difficulty": "challenging",
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
  "expected_output": "Report showing matched instances across providers with cost savings, performance metrics, and optimization recommendations"
}
```

### Query 2 — challenging / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 2,
  "question": "Historical Pricing Trend Analysis with Recursive CTE and Multi-Period Forecasting",
  "SQL": "WITH RECURSIVE pricing_time_series AS (\n    -- Anchor: Base pricing data\n    SELECT\n        hp.instance_id,\n        hp.region_id,\n        hp.pricing_model,\n        hp.effective_date,\n        hp.price_per_hour,\n        1 AS period_level,\n        CAST(hp.instance_id AS VARCHAR(1000)) AS price_path\n    FROM historical_pricing hp\n    WHERE hp.effective_date >= CURRENT_DATE - INTERVAL '12 months'\n    \n    UNION ALL\n    \n    -- Recursive: Build time series with period progression\n    SELECT\n        hp.instance_id,\n        hp.region_id,\n        hp.pricing_model,\n        hp.effective_date,\n        hp.price_per_hour,\n        pts.period_level + 1,\n        CAST(pts.price_path || ' -> ' || hp.instance_id AS VARCHAR(1000))\n    FROM pricing_time_series pts\n    INNER JOIN historical_pricing hp ON (\n        pts.instance_id = hp.instance_id\n        AND pts.region_id = hp.region_id\n        AND pts.pricing_model = hp.pricing_model\n        AND hp.effective_date > pts.effective_date\n        AND pts.period_level < 24  -- Limit to 24 months\n    )\n),\nbase_instance_data AS (\n    SELECT\n        ci.instance_id,\n        ci.provider_id,\n        ci.instance_name,\n        ci.vcpus,\n        ci.memory_gb,\n        cr.region_code,\n        cr.region_name\n    FROM cloud_instances ci\n    INNER JOIN cloud_regions cr ON ci.region_id = cr.region_id\n    WHERE ci.is_available = TRUE\n),\npricing_aggregations AS (\n    SELECT\n        pts.instance_id,\n        pts.region_id,\n        pts.pricing_model,\n        COUNT(*) AS price_points_count,\n        MIN(pts.price_per_hour) AS min_price,\n        MAX(pts.price_per_hour) AS max_price,\n        AVG(pts.price_per_hour) AS avg_price,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pts.price_per_hour) AS median_price,\n        STDDEV(pts.price_per_hour) AS price_volatility\n    FROM pricing_time_series pts\n    GROUP BY pts.instance_id, pts.region_id, pts.pricing_model\n),\nprice_trend_analysis AS (\n    SELECT\n        pa.instance_id,\n        pa.region_id,\n        pa.pricing_model,\n        pa.price_points_count,\n        pa.min_price,\n        pa.max_price,\n        pa.avg_price,\n        pa.median_price,\n        pa.price_volatility,\n        bid.provider_id,\n        bid.instance_name,\n        bid.vcpus,\n        bid.memory_gb,\n        bid.region_code,\n        bid.region_name,\n        -- Calculate price change trend\n        CASE\n            WHEN pa.price_volatility > 0 THEN\n                (pa.max_price - pa.min_price) / pa.avg_price * 100\n            ELSE 0\n        END AS price_volatility_pct\n    FROM pricing_aggregations pa\n    INNER JOIN base_instance_data bid ON pa.instance_id = bid.instance_id\n),\ntrend_classification AS (\n    SELECT\n        pta.*,\n        CASE\n            WHEN pta.price_volatility_pct < 5 THEN 'Stable'\n            WHEN pta.price_volatility_pct < 15 THEN 'Moderate'\n            WHEN pta.price_volatility_pct < 30 THEN 'Volatile'\n            ELSE 'Highly Volatile'\n        END AS volatility_classification,\n        -- Window functions for trend analysis\n        AVG(pta.avg_price) OVER (\n            PARTITION BY pta.provider_id, pta.pricing_model\n        ) AS provider_avg_price,\n        RANK() OVER (\n            PARTITION BY pta.provider_id, pta.pricing_model\n            ORDER BY pta.price_volatility_pct DESC\n        ) AS volatility_rank\n    FROM price_trend_analysis pta\n),\nforecast_preparation AS (\n    SELECT\n        tc.*,\n        -- Calculate forecast inputs\n        tc.avg_price * 1.02 AS forecast_price_next_month,\n        tc.avg_price * 1.05 AS forecast_price_next_quarter,\n        tc.avg_price * 1.10 AS forecast_price_next_year,\n        -- Price deviation from provider average\n        CASE\n            WHEN tc.provider_avg_price > 0 THEN\n                ((tc.avg_price - tc.provider_avg_price) / tc.provider_avg_price) * 100\n            ELSE NULL\n        END AS price_deviation_from_provider_avg_pct\n    FROM trend_classification tc\n),\nfinal_forecast_analysis AS (\n    SELECT\n        fp.instance_id,\n        fp.instance_name,\n        fp.provider_id,\n        fp.region_code,\n        fp.region_name,\n        fp.pricing_model,\n        fp.price_points_count,\n        ROUND(CAST(fp.avg_price AS NUMERIC), 6) AS avg_price,\n        ROUND(CAST(fp.median_price AS NUMERIC), 6) AS median_price,\n        ROUND(CAST(fp.price_volatility AS NUMERIC), 6) AS price_volatility,\n        ROUND(CAST(fp.price_volatility_pct AS NUMERIC), 2) AS price_volatility_pct,\n        fp.volatility_classification,\n        fp.volatility_rank,\n        ROUND(CAST(fp.forecast_price_next_month AS NUMERIC), 6) AS forecast_price_next_month,\n        ROUND(CAST(fp.forecast_price_next_quarter AS NUMERIC), 6) AS forecast_price_next_quarter,\n        ROUND(CAST(fp.forecast_price_next_year AS NUMERIC), 6) AS forecast_price_next_year,\n        ROUND(CAST(fp.price_deviation_from_provider_avg_pct AS NUMERIC), 2) AS price_deviation_from_provider_avg_pct\n    FROM forecast_preparation fp\n)\nSELECT * FROM final_forecast_analysis\nORDER BY final_forecast_analysis.volatility_rank, final_forecast_analysis.price_volatility_pct DESC\nLIMIT 100;",
  "evidence": "Use Case: Cloud Cost Forecasting - Historical Pricing Trend Analysis with Recursive CTE and Multi-Period Forecasting Description: Enterprise-level historical pricing trend analysis with recursive cte and multi-period forecasting with Recursive CTE for time-series analysis, 8+ nested CTEs. Demonstrates production patterns for cloud cost . Business Value: Historical Pricing Trend Analysis with Recursive CTE and Multi-Period Forecasting report showing cost  metrics and recommendations. Purpose: Pro",
  "difficulty": "challenging",
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
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 3,
  "question": "Reserved Instance ROI Analysis with Multi-Year Projections",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Optimization - Reserved Instance ROI Analysis with Multi-Year Projections Description: Enterprise-level reserved instance roi analysis with multi-year projections with 8+ nested CTEs, financial calculations. Demonstrates production patterns for cloud cost . Business Value: Reserved Instance ROI Analysis with Multi-Year Projections report showing cost  metrics and recommendations. Purpose: Provides reserved instance roi analysis with multi-year projections to enable data-driv",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 4,
  "question": "Spot Instance Cost-Benefit Analysis with Risk Modeling",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Optimization - Spot Instance Cost-Benefit Analysis with Risk Modeling Description: Enterprise-level spot instance cost-benefit analysis with risk modeling with 8+ nested CTEs, probability calculations. Demonstrates production patterns for cloud cost . Business Value: Spot Instance Cost-Benefit Analysis with Risk Modeling report showing cost  metrics and recommendations. Purpose: Provides spot instance cost-benefit analysis with risk modeling to enable data-driven cloud cost ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 5,
  "question": "Regional Pricing Optimization with Cross-Region Comparisons",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Optimization - Regional Pricing Optimization with Cross-Region Comparisons Description: Enterprise-level regional pricing optimization with cross-region comparisons with 8+ nested CTEs, cross-region analysis. Demonstrates production patterns for cloud cost . Business Value: Regional Pricing Optimization with Cross-Region Comparisons report showing cost  metrics and recommendations. Purpose: Provides regional pricing optimization with cross-region comparisons to enable data-d",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 6,
  "question": "Performance-Cost Correlation Analysis with Statistical Modeling",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost  - Performance-Cost Correlation Analysis with Statistical Modeling Description: Enterprise-level performance-cost correlation analysis with statistical modeling with 8+ nested CTEs, correlation calculations. Demonstrates production patterns for cloud cost . Business Value: Performance-Cost Correlation Analysis with Statistical Modeling report showing cost  metrics and recommendations. Purpose: Provides performance-cost correlation analysis with statistical modeling to enable",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 7,
  "question": "Instance Family Cost Efficiency Ranking",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Optimization - Instance Family Cost Efficiency Ranking Description: Enterprise-level instance family cost efficiency ranking with 8+ nested CTEs, percentile analysis. Demonstrates production patterns for cloud cost . Business Value: Instance Family Cost Efficiency Ranking report showing cost  metrics and recommendations. Purpose: Provides instance family cost efficiency ranking to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, percentile analysis, windo",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 8,
  "question": "Cost Forecasting with Time-Series Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Planning - Cost Forecasting with Time-Series Analysis Description: Enterprise-level cost forecasting with time-series analysis with 8+ nested CTEs, time-series. Demonstrates production patterns for cloud cost . Business Value: Cost Forecasting with Time-Series Analysis report showing cost  metrics and recommendations. Purpose: Provides cost forecasting with time-series analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, time-series, window functi",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 9,
  "question": "Multi-Cloud Migration Cost Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Migration Planning - Multi-Cloud Migration Cost Analysis Description: Enterprise-level multi-cloud migration cost analysis with 8+ nested CTEs, migration analysis. Demonstrates production patterns for cloud cost . Business Value: Multi-Cloud Migration Cost Analysis report showing cost  metrics and recommendations. Purpose: Provides multi-cloud migration cost analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, migration analysis, window functions with ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 10,
  "question": "Long-Term Cost Projections with DCF Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Financial Planning - Long-Term Cost Projections with DCF Analysis Description: Enterprise-level long-term cost projections with dcf analysis with 8+ nested CTEs, financial modeling. Demonstrates production patterns for cloud cost . Business Value: Long-Term Cost Projections with DCF Analysis report showing cost  metrics and recommendations. Purpose: Provides long-term cost projections with dcf analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, financ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 11,
  "question": "Instance Right-Sizing Recommendations",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Optimization - Instance Right-Sizing Recommendations Description: Enterprise-level instance right-sizing recommendations with 8+ nested CTEs, workload matching. Demonstrates production patterns for cloud cost . Business Value: Instance Right-Sizing Recommendations report showing cost  metrics and recommendations. Purpose: Provides instance right-sizing recommendations to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, workload matching, window functions ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 12,
  "question": "Cost Anomaly Detection with Statistical Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Monitoring - Cost Anomaly Detection with Statistical Analysis Description: Enterprise-level cost anomaly detection with statistical analysis with 8+ nested CTEs, outlier detection. Demonstrates production patterns for cloud cost . Business Value: Cost Anomaly Detection with Statistical Analysis report showing cost  metrics and recommendations. Purpose: Provides cost anomaly detection with statistical analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 13,
  "question": "Reserved Instance Purchase Optimization",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Procurement - Reserved Instance Purchase Optimization Description: Enterprise-level reserved instance purchase optimization with 8+ nested CTEs, usage analysis. Demonstrates production patterns for cloud cost . Business Value: Reserved Instance Purchase Optimization report showing cost  metrics and recommendations. Purpose: Provides reserved instance purchase optimization to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, usage analysis, window functions with",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 14,
  "question": "Spot Instance Interruption Risk Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Risk Management - Spot Instance Interruption Risk Analysis Description: Enterprise-level spot instance interruption risk analysis with 8+ nested CTEs, risk modeling. Demonstrates production patterns for cloud cost . Business Value: Spot Instance Interruption Risk Analysis report showing cost  metrics and recommendations. Purpose: Provides spot instance interruption risk analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, risk modeling, window function",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 15,
  "question": "Cross-Provider Instance Matching",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Migration Planning - Cross-Provider Instance Matching Description: Enterprise-level cross-provider instance matching with 8+ nested CTEs, similarity scoring. Demonstrates production patterns for cloud cost . Business Value: Cross-Provider Instance Matching report showing cost  metrics and recommendations. Purpose: Provides cross-provider instance matching to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, similarity scoring, window functions with multiple fra",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 16,
  "question": "Cost-Performance Pareto Frontier Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Optimization - Cost-Performance Pareto Frontier Analysis Description: Enterprise-level cost-performance pareto frontier analysis with 8+ nested CTEs, Pareto analysis. Demonstrates production patterns for cloud cost . Business Value: Cost-Performance Pareto Frontier Analysis report showing cost  metrics and recommendations. Purpose: Provides cost-performance pareto frontier analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, Pareto analysis, window fun",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 17,
  "question": "Instance Deprecation Impact Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Planning - Instance Deprecation Impact Analysis Description: Enterprise-level instance deprecation impact analysis with 8+ nested CTEs, deprecation analysis. Demonstrates production patterns for cloud cost . Business Value: Instance Deprecation Impact Analysis report showing cost  metrics and recommendations. Purpose: Provides instance deprecation impact analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, deprecation analysis, window functions with mu",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 18,
  "question": "Burstable Instance Cost Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Optimization - Burstable Instance Cost Analysis Description: Enterprise-level burstable instance cost analysis with 8+ nested CTEs, baseline modeling. Demonstrates production patterns for cloud cost . Business Value: Burstable Instance Cost Analysis report showing cost  metrics and recommendations. Purpose: Provides burstable instance cost analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, baseline modeling, window functions with multiple frame ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 19,
  "question": "GPU Instance Cost Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud ML/AI Cost Optimization - GPU Instance Cost Analysis Description: Enterprise-level gpu instance cost analysis with 8+ nested CTEs, GPU analysis. Demonstrates production patterns for cloud cost . Business Value: GPU Instance Cost Analysis report showing cost  metrics and recommendations. Purpose: Provides gpu instance cost analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, GPU analysis, window functions with multiple frame clauses, complex aggregation",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 20,
  "question": "Storage Cost Optimization",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Storage Optimization - Storage Cost Optimization Description: Enterprise-level storage cost optimization with 8+ nested CTEs, storage analysis. Demonstrates production patterns for cloud cost . Business Value: Storage Cost Optimization report showing cost  metrics and recommendations. Purpose: Provides storage cost optimization to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, storage analysis, window functions with multiple frame clauses, complex aggregatio",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 21,
  "question": "Network Cost Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Network Optimization - Network Cost Analysis Description: Enterprise-level network cost analysis with 8+ nested CTEs, network analysis. Demonstrates production patterns for cloud cost . Business Value: Network Cost Analysis report showing cost  metrics and recommendations. Purpose: Provides network cost analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, network analysis, window functions with multiple frame clauses, complex aggregations, percentile c",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 22,
  "question": "Cost Allocation Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Financial Management - Cost Allocation Analysis Description: Enterprise-level cost allocation analysis with 8+ nested CTEs, allocation calculations. Demonstrates production patterns for cloud cost . Business Value: Cost Allocation Analysis report showing cost  metrics and recommendations. Purpose: Provides cost allocation analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, allocation calculations, window functions with multiple frame clauses, complex ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 23,
  "question": "Instance Lifecycle Cost Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Lifecycle Management - Instance Lifecycle Cost Analysis Description: Enterprise-level instance lifecycle cost analysis with 8+ nested CTEs, lifecycle tracking. Demonstrates production patterns for cloud cost . Business Value: Instance Lifecycle Cost Analysis report showing cost  metrics and recommendations. Purpose: Provides instance lifecycle cost analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, lifecycle tracking, window functions with multiple f",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 24,
  "question": "Cost Optimization Score Calculation",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost  - Cost Optimization Score Calculation Description: Enterprise-level cost optimization score calculation with 8+ nested CTEs, scoring algorithms. Demonstrates production patterns for cloud cost . Business Value: Cost Optimization Score Calculation report showing cost  metrics and recommendations. Purpose: Provides cost optimization score calculation to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, scoring algorithms, window functions with multiple fram",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 25,
  "question": "Instance Comparison Matrix Generation",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud  - Instance Comparison Matrix Generation Description: Enterprise-level instance comparison matrix generation with 8+ nested CTEs, matrix generation. Demonstrates production patterns for cloud cost . Business Value: Instance Comparison Matrix Generation report showing cost  metrics and recommendations. Purpose: Provides instance comparison matrix generation to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, matrix generation, window functions with multiple fra",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 26 — challenging / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 26,
  "question": "Recursive Instance Dependency Graph Analysis",
  "SQL": "WITH RECURSIVE instance_dependency_tree AS (\n    -- Anchor: Base instances\n    SELECT instance_id, provider_id, instance_name, 1 AS level\n    FROM cloud_instances\n    WHERE is_current_generation = TRUE\n    UNION ALL\n    -- Recursive: Find dependencies\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, idt.level + 1\n    FROM instance_dependency_tree idt\n    INNER JOIN instance_comparison_matrix icm ON idt.instance_id = icm.instance_id_1\n    INNER JOIN cloud_instances ci ON icm.instance_id_2 = ci.instance_id\n    WHERE idt.level < 5\n),\ncte_2 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_3 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_4 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_5 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_6 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_7 AS (\n    SELECT * FROM instance_dependency_tree\n),\ncte_8 AS (\n    SELECT * FROM instance_dependency_tree\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost  - Recursive Instance Dependency Graph Analysis Description: Enterprise-level recursive instance dependency graph analysis with Recursive CTE, 8+ nested CTEs, graph traversal. Demonstrates production patterns for cloud cost . Business Value: Recursive Instance Dependency Graph Analysis report showing cost  metrics and recommendations. Purpose: Provides recursive instance dependency graph analysis to enable data-driven cloud cost decisions. Complexity: Recursive CTE, 8+ neste",
  "difficulty": "challenging",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "instance_dependency_tree",
    "instance_comparison_matrix",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 27,
  "question": "Reserved Instance Utilization Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost Optimization - Reserved Instance Utilization Analysis Description: Enterprise-level reserved instance utilization analysis with 8+ nested CTEs, utilization tracking. Demonstrates production patterns for cloud cost . Business Value: Reserved Instance Utilization Analysis report showing cost  metrics and recommendations. Purpose: Provides reserved instance utilization analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, utilization tracking, window ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 28,
  "question": "Spot Instance Price Volatility Analysis",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Risk Management - Spot Instance Price Volatility Analysis Description: Enterprise-level spot instance price volatility analysis with 8+ nested CTEs, volatility calculations. Demonstrates production patterns for cloud cost . Business Value: Spot Instance Price Volatility Analysis report showing cost  metrics and recommendations. Purpose: Provides spot instance price volatility analysis to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, volatility calculations,",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 29,
  "question": "Cross-Region Cost Comparison",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Global Optimization - Cross-Region Cost Comparison Description: Enterprise-level cross-region cost comparison with 8+ nested CTEs, cross-region analysis. Demonstrates production patterns for cloud cost . Business Value: Cross-Region Cost Comparison report showing cost  metrics and recommendations. Purpose: Provides cross-region cost comparison to enable data-driven cloud cost decisions. Complexity: 8+ nested CTEs, cross-region analysis, window functions with multiple frame clause",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```

### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-14",
  "question_id": 30,
  "question": "Comprehensive Cost  Dashboard",
  "SQL": "WITH base_instance_data AS (\n    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb\n    FROM cloud_instances ci\n    WHERE ci.is_available = TRUE\n),\ncte_2 AS (\n    SELECT * FROM base_instance_data\n),\ncte_3 AS (\n    SELECT * FROM base_instance_data\n),\ncte_4 AS (\n    SELECT * FROM base_instance_data\n),\ncte_5 AS (\n    SELECT * FROM base_instance_data\n),\ncte_6 AS (\n    SELECT * FROM base_instance_data\n),\ncte_7 AS (\n    SELECT * FROM base_instance_data\n),\ncte_8 AS (\n    SELECT * FROM base_instance_data\n),\nfinal_analysis AS (\n    SELECT * FROM cte_8\n)\nSELECT * FROM final_analysis LIMIT 100;",
  "evidence": "Use Case: Cloud Cost  - Comprehensive Cost  Dashboard Description: Enterprise-level comprehensive cost  dashboard with 9+ nested CTEs, multi-metric aggregation. Demonstrates production patterns for cloud cost . Business Value: Comprehensive Cost  Dashboard report showing cost  metrics and recommendations. Purpose: Provides comprehensive cost  dashboard to enable data-driven cloud cost decisions. Complexity: 9+ nested CTEs, multi-metric aggregation, window functions with multiple frame clauses, c",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "cloud_instances",
    "base_instance_data",
    "cte_8",
    "final_analysis"
  ],
  "schema_context": {},
  "expected_output": "Query results with detailed cost  metrics"
}
```
