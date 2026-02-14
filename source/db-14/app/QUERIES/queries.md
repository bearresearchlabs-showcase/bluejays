# Database 14 - Cloud Instance Cost - Extremely Complex SQL Queries

# Database Schema: DB14

**Description:** Cloud Instance Cost Database
**Created:** 2026-02-05

## Overview

This database contains cloud instance pricing, specifications, and performance data across AWS, GCP, and Azure. The database supports cloud instance cost analysis, optimization, cross-cloud comparisons, and intelligent recommendations for enterprises and cloud cost optimization platforms.

## Tables

### `cloud_providers`
Stores cloud provider metadata (AWS, GCP, Azure)

### `cloud_regions`
Stores region metadata for all cloud providers

### `instance_families`
Stores instance family metadata (General Purpose, Compute Optimized, etc.)

### `cloud_instances`
Core table storing all cloud instance specifications

### `instance_performance_metrics`
Stores performance benchmark data (CoreMark, FFmpeg FPS, etc.)

### `instance_pricing`
Stores pricing data for all pricing models (on-demand, reserved, spot)

### `historical_pricing`
Tracks pricing changes over time for trend analysis

### `cost_optimization_recommendations`
Stores AI-generated cost optimization recommendations

### `instance_comparison_matrix`
Stores cross-provider instance comparisons

### `data_extraction_log`
Tracks data extraction operations from various sources

### `cost__analytics`
Pre-aggregated analytics for fast querying

---

This file contains 30 extremely complex SQL queries focused on cloud instance cost analysis and optimization. All queries are designed to work across PostgreSQL.

## Query 1: Multi-Provider Cost-Performance Analysis with Recursive Instance Matching and Cross-Cloud Optimization Recommendations

**Use Case:** **Cloud Cost Optimization - Cross-Cloud Instance Right-Sizing Analysis for Enterprise Migration Planning**

**Description:** Enterprise-level multi-provider cost-performance analysis using recursive CTE for instance matching across AWS, Azure, and GCP, with complex aggregations, window functions, percentile calculations, and cross-cloud optimization recommendations. Demonstrates production patterns used by cloud cost optimization platforms.

**Business Value:** Comprehensive cost-performance comparison report showing optimal instance selections across all three major cloud providers with cost savings projections, performance benchmarks, and migration recommendations. Helps enterprises identify cost savings opportunities during cloud migrations.

**Purpose:** Identifies the most cost-effective instance configurations across AWS, Azure, and GCP by matching instances with similar specifications and comparing their cost-performance ratios, enabling data-driven cloud provider selection.

**Complexity:** Recursive CTE for instance matching, 8+ nested CTEs, complex aggregations, window functions with multiple frame clauses, percentile calculations, cross-provider comparisons, cost optimization algorithms

**Expected Output:** Report showing matched instances across providers with cost savings, performance metrics, and optimization recommendations

```sql
WITH provider_instance_base AS (
    -- First CTE: Base instance data with normalized specifications
    SELECT
        ci.instance_id,
        ci.provider_id,
        cp.provider_name,
        ci.instance_name,
        ci.api_name,
        ci.vcpus,
        ci.memory_gb,
        ci.instance_storage_gb,
        ci.instance_storage_type,
        ci.network_performance,
        ci.network_bandwidth_gbps,
        ci.architecture,
        ci.processor_type,
        ci.is_current_generation,
        cr.region_code,
        cr.region_name,
        cr.country_code,
        ifam.family_name AS instance_family,
        -- Normalize memory to GB for comparison
        CASE
            WHEN ci.memory_gb IS NULL AND ci.memory_mb IS NOT NULL THEN ci.memory_mb / 1024.0
            ELSE ci.memory_gb
        END AS normalized_memory_gb,
        -- Calculate vCPU-to-memory ratio
        CASE
            WHEN ci.vcpus > 0 AND ci.memory_gb IS NOT NULL THEN ci.memory_gb / ci.vcpus
            WHEN ci.vcpus > 0 AND ci.memory_mb IS NOT NULL THEN (ci.memory_mb / 1024.0) / ci.vcpus
            ELSE NULL
        END AS memory_per_vcpu_ratio
    FROM cloud_instances ci
    INNER JOIN cloud_providers cp ON ci.provider_id = cp.provider_id
    INNER JOIN cloud_regions cr ON ci.region_id = cr.region_id
    LEFT JOIN instance_families ifam ON ci.instance_family_id = ifam.family_id
    WHERE ci.is_available = TRUE
        AND ci.is_current_generation = TRUE
),
instance_performance_scores AS (
    -- Second CTE: Aggregate performance metrics with weighted scoring
    SELECT
        pib.instance_id,
        pib.provider_id,
        pib.provider_name,
        pib.instance_name,
        pib.vcpus,
        pib.normalized_memory_gb,
        pib.memory_per_vcpu_ratio,
        pib.instance_family,
        pib.region_code,
        -- CoreMark score (primary performance metric)
        MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END) AS coremark_score,
        -- FFmpeg FPS score (video processing performance)
        MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END) AS ffmpeg_fps_score,
        -- Calculate composite performance score
        (
            COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +
            COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4
        ) AS composite_performance_score,
        -- Performance per vCPU
        CASE
            WHEN pib.vcpus > 0 THEN
                (
                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +
                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4
                ) / pib.vcpus
            ELSE NULL
        END AS performance_per_vcpu,
        -- Performance per GB memory
        CASE
            WHEN pib.normalized_memory_gb > 0 THEN
                (
                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'CoreMark' THEN ipm.benchmark_score_normalized END), 0) * 0.6 +
                    COALESCE(MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_score_normalized END), 0) * 0.4
                ) / pib.normalized_memory_gb
            ELSE NULL
        END AS performance_per_gb_memory
    FROM provider_instance_base pib
    LEFT JOIN instance_performance_metrics ipm ON pib.instance_id = ipm.instance_id
    GROUP BY
        pib.instance_id,
        pib.provider_id,
        pib.provider_name,
        pib.instance_name,
        pib.vcpus,
        pib.normalized_memory_gb,
        pib.memory_per_vcpu_ratio,
        pib.instance_family,
        pib.region_code
),
instance_pricing_aggregated AS (
    -- Third CTE: Aggregate pricing across all pricing models
    SELECT
        ips.instance_id,
        ips.provider_id,
        ips.provider_name,
        ips.instance_name,
        ips.vcpus,
        ips.normalized_memory_gb,
        ips.memory_per_vcpu_ratio,
        ips.instance_family,
        ips.region_code,
        ips.coremark_score,
        ips.ffmpeg_fps_score,
        ips.composite_performance_score,
        ips.performance_per_vcpu,
        ips.performance_per_gb_memory,
        -- On-demand pricing
        MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) AS on_demand_price_per_hour,
        -- Reserved 1-year pricing
        MIN(CASE WHEN ip.pricing_model = 'reserved_1yr' AND ip.operating_system = 'Linux' AND ip.payment_option = 'no_upfront' AND ip.is_current = TRUE THEN ip.effective_hourly_cost END) AS reserved_1yr_price_per_hour,
        -- Reserved 3-year pricing
        MIN(CASE WHEN ip.pricing_model = 'reserved_3yr' AND ip.operating_system = 'Linux' AND ip.payment_option = 'no_upfront' AND ip.is_current = TRUE THEN ip.effective_hourly_cost END) AS reserved_3yr_price_per_hour,
        -- Spot pricing (minimum)
        MIN(CASE WHEN ip.pricing_model = 'spot' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) AS spot_min_price_per_hour,
        -- Calculate cost per vCPU (on-demand)
        CASE
            WHEN ips.vcpus > 0 AND MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) IS NOT NULL THEN
                MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) / ips.vcpus
            ELSE NULL
        END AS cost_per_vcpu_on_demand,
        -- Calculate cost per GB memory (on-demand)
        CASE
            WHEN ips.normalized_memory_gb > 0 AND MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) IS NOT NULL THEN
                MIN(CASE WHEN ip.pricing_model = 'on_demand' AND ip.operating_system = 'Linux' AND ip.is_current = TRUE THEN ip.price_per_hour END) / ips.normalized_memory_gb
            ELSE NULL
        END AS cost_per_gb_memory_on_demand
    FROM instance_performance_scores ips
    LEFT JOIN instance_pricing ip ON ips.instance_id = ip.instance_id
    GROUP BY
        ips.instance_id,
        ips.provider_id,
        ips.provider_name,
        ips.instance_name,
        ips.vcpus,
        ips.normalized_memory_gb,
        ips.memory_per_vcpu_ratio,
        ips.instance_family,
        ips.region_code,
        ips.coremark_score,
        ips.ffmpeg_fps_score,
        ips.composite_performance_score,
        ips.performance_per_vcpu,
        ips.performance_per_gb_memory
),
cost_performance_ratios AS (
    -- Fourth CTE: Calculate cost-performance ratios
    SELECT
        ipa.instance_id,
        ipa.provider_id,
        ipa.provider_name,
        ipa.instance_name,
        ipa.vcpus,
        ipa.normalized_memory_gb,
        ipa.memory_per_vcpu_ratio,
        ipa.instance_family,
        ipa.region_code,
        ipa.on_demand_price_per_hour,
        ipa.reserved_1yr_price_per_hour,
        ipa.reserved_3yr_price_per_hour,
        ipa.spot_min_price_per_hour,
        ipa.composite_performance_score,
        ipa.performance_per_vcpu,
        ipa.performance_per_gb_memory,
        ipa.cost_per_vcpu_on_demand,
        ipa.cost_per_gb_memory_on_demand,
        -- Cost-performance ratio (lower is better)
        CASE
            WHEN ipa.composite_performance_score > 0 AND ipa.on_demand_price_per_hour IS NOT NULL THEN
                ipa.on_demand_price_per_hour / ipa.composite_performance_score
            ELSE NULL
        END AS cost_performance_ratio_on_demand,
        -- Performance per dollar (higher is better)
        CASE
            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.composite_performance_score IS NOT NULL THEN
                ipa.composite_performance_score / ipa.on_demand_price_per_hour
            ELSE NULL
        END AS performance_per_dollar_on_demand,
        -- Reserved instance savings percentage
        CASE
            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.reserved_1yr_price_per_hour IS NOT NULL THEN
                ((ipa.on_demand_price_per_hour - ipa.reserved_1yr_price_per_hour) / ipa.on_demand_price_per_hour) * 100
            ELSE NULL
        END AS reserved_1yr_savings_pct,
        CASE
            WHEN ipa.on_demand_price_per_hour > 0 AND ipa.reserved_3yr_price_per_hour IS NOT NULL THEN
                ((ipa.on_demand_price_per_hour - ipa.reserved_3yr_price_per_hour) / ipa.on_demand_price_per_hour) * 100
            ELSE NULL
        END AS reserved_3yr_savings_pct
    FROM instance_pricing_aggregated ipa
),
instance_specification_clusters AS (
    -- Fifth CTE: Cluster instances by specification similarity using window functions
    SELECT
        cpr.instance_id,
        cpr.provider_id,
        cpr.provider_name,
        cpr.instance_name,
        cpr.vcpus,
        cpr.normalized_memory_gb,
        cpr.memory_per_vcpu_ratio,
        cpr.instance_family,
        cpr.region_code,
        cpr.on_demand_price_per_hour,
        cpr.reserved_1yr_price_per_hour,
        cpr.reserved_3yr_price_per_hour,
        cpr.spot_min_price_per_hour,
        cpr.composite_performance_score,
        cpr.cost_performance_ratio_on_demand,
        cpr.performance_per_dollar_on_demand,
        cpr.reserved_1yr_savings_pct,
        cpr.reserved_3yr_savings_pct,
        -- Find similar instances using window functions
        COUNT(*) OVER (
            PARTITION BY
                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,
                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END
        ) AS similar_spec_count,
        -- Rank by cost-performance ratio within specification cluster
        RANK() OVER (
            PARTITION BY
                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,
                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END
            ORDER BY cpr.cost_performance_ratio_on_demand ASC NULLS LAST
        ) AS cost_performance_rank,
        -- Rank by performance per dollar
        RANK() OVER (
            PARTITION BY
                CASE WHEN cpr.vcpus BETWEEN 2 AND 4 THEN '2-4' WHEN cpr.vcpus BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.vcpus BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.vcpus BETWEEN 16 AND 32 THEN '16-32' ELSE '32+' END,
                CASE WHEN cpr.normalized_memory_gb BETWEEN 4 AND 8 THEN '4-8' WHEN cpr.normalized_memory_gb BETWEEN 8 AND 16 THEN '8-16' WHEN cpr.normalized_memory_gb BETWEEN 16 AND 32 THEN '16-32' WHEN cpr.normalized_memory_gb BETWEEN 32 AND 64 THEN '32-64' ELSE '64+' END
            ORDER BY cpr.performance_per_dollar_on_demand DESC NULLS LAST
        ) AS performance_per_dollar_rank
    FROM cost_performance_ratios cpr
    WHERE cpr.on_demand_price_per_hour IS NOT NULL
        AND cpr.composite_performance_score IS NOT NULL
),
recursive_instance_matching AS (
    -- Sixth CTE: Recursive CTE for finding best matching instances across providers
    WITH RECURSIVE instance_match_tree AS (
        -- Anchor: Start with AWS instances as base
        SELECT
            isc.instance_id,
            isc.provider_id,
            isc.provider_name,
            isc.instance_name,
            isc.vcpus,
            isc.normalized_memory_gb,
            isc.memory_per_vcpu_ratio,
            isc.on_demand_price_per_hour,
            isc.composite_performance_score,
            isc.cost_performance_ratio_on_demand,
            isc.performance_per_dollar_on_demand,
            1 AS match_level,
            CAST(isc.instance_id AS VARCHAR(1000)) AS match_path,
            isc.instance_id AS base_instance_id
        FROM instance_specification_clusters isc
        WHERE isc.provider_id = 'aws'
            AND isc.cost_performance_rank = 1
        
        UNION ALL
        
        -- Recursive: Find matching instances in other providers
        SELECT
            isc.instance_id,
            isc.provider_id,
            isc.provider_name,
            isc.instance_name,
            isc.vcpus,
            isc.normalized_memory_gb,
            isc.memory_per_vcpu_ratio,
            isc.on_demand_price_per_hour,
            isc.composite_performance_score,
            isc.cost_performance_ratio_on_demand,
            isc.performance_per_dollar_on_demand,
            imt.match_level + 1,
            CAST(imt.match_path || ' -> ' || isc.instance_id AS VARCHAR(1000)),
            imt.base_instance_id
        FROM instance_match_tree imt
        INNER JOIN instance_specification_clusters isc ON (
            -- Match instances with similar specifications (within 10% tolerance)
            ABS(isc.vcpus - imt.vcpus) <= GREATEST(imt.vcpus * 0.1, 1)
            AND ABS(isc.normalized_memory_gb - imt.normalized_memory_gb) <= GREATEST(imt.normalized_memory_gb * 0.1, 1)
            AND isc.provider_id != imt.provider_id
            AND imt.match_level < 3  -- Limit recursion depth
        )
    )
    SELECT * FROM instance_match_tree
),
cross_provider_optimization AS (
    -- Seventh CTE: Calculate optimization opportunities across providers
    SELECT
        rim.base_instance_id,
        rim.instance_id,
        rim.provider_id,
        rim.provider_name,
        rim.instance_name,
        rim.vcpus,
        rim.normalized_memory_gb,
        rim.on_demand_price_per_hour,
        rim.composite_performance_score,
        rim.cost_performance_ratio_on_demand,
        rim.performance_per_dollar_on_demand,
        rim.match_level,
        rim.match_path,
        -- Compare with base instance
        base.on_demand_price_per_hour AS base_price_per_hour,
        base.composite_performance_score AS base_performance_score,
        base.cost_performance_ratio_on_demand AS base_cost_performance_ratio,
        -- Calculate cost difference
        rim.on_demand_price_per_hour - base.on_demand_price_per_hour AS price_difference,
        CASE
            WHEN base.on_demand_price_per_hour > 0 THEN
                ((rim.on_demand_price_per_hour - base.on_demand_price_per_hour) / base.on_demand_price_per_hour) * 100
            ELSE NULL
        END AS price_difference_pct,
        -- Performance difference
        rim.composite_performance_score - base.composite_performance_score AS performance_difference,
        CASE
            WHEN base.composite_performance_score > 0 THEN
                ((rim.composite_performance_score - base.composite_performance_score) / base.composite_performance_score) * 100
            ELSE NULL
        END AS performance_difference_pct,
        -- Cost savings potential (monthly)
        CASE
            WHEN rim.on_demand_price_per_hour < base.on_demand_price_per_hour THEN
                (base.on_demand_price_per_hour - rim.on_demand_price_per_hour) * 24 * 30
            ELSE 0
        END AS monthly_cost_savings
    FROM recursive_instance_matching rim
    INNER JOIN recursive_instance_matching base ON rim.base_instance_id = base.instance_id AND base.match_level = 1
),
final_optimization_recommendations AS (
    -- Eighth CTE: Generate final recommendations with ranking
    SELECT
        cpo.base_instance_id,
        cpo.instance_id AS recommended_instance_id,
        cpo.provider_id AS recommended_provider_id,
        cpo.provider_name AS recommended_provider_name,
        cpo.instance_name AS recommended_instance_name,
        cpo.vcpus,
        cpo.normalized_memory_gb,
        cpo.on_demand_price_per_hour AS recommended_price_per_hour,
        cpo.composite_performance_score AS recommended_performance_score,
        cpo.base_price_per_hour,
        cpo.base_performance_score,
        cpo.price_difference,
        cpo.price_difference_pct,
        cpo.performance_difference,
        cpo.performance_difference_pct,
        cpo.monthly_cost_savings,
        -- Calculate optimization score (weighted)
        (
            CASE WHEN cpo.monthly_cost_savings > 0 THEN 50 ELSE 0 END +
            CASE WHEN cpo.performance_difference >= 0 THEN 30 ELSE 0 END +
            CASE WHEN ABS(cpo.price_difference_pct) <= 20 THEN 20 ELSE 0 END
        ) AS optimization_score,
        -- Rank recommendations
        ROW_NUMBER() OVER (
            PARTITION BY cpo.base_instance_id
            ORDER BY
                cpo.monthly_cost_savings DESC,
                cpo.performance_difference DESC,
                ABS(cpo.price_difference_pct) ASC
        ) AS recommendation_rank
    FROM cross_provider_optimization cpo
    WHERE cpo.monthly_cost_savings > 0 OR cpo.performance_difference > 0
)
SELECT
    base.instance_name AS base_instance,
    base.provider_name AS base_provider,
    base.vcpus AS base_vcpus,
    base.normalized_memory_gb AS base_memory_gb,
    base.on_demand_price_per_hour AS base_price_per_hour,
    base.composite_performance_score AS base_performance_score,
    for_rec.recommended_instance_name AS recommended_instance,
    for_rec.recommended_provider_name AS recommended_provider,
    for_rec.recommended_price_per_hour AS recommended_price_per_hour,
    for_rec.recommended_performance_score AS recommended_performance_score,
    for_rec.price_difference,
    ROUND(CAST(for_rec.price_difference_pct AS NUMERIC), 2) AS price_difference_pct,
    for_rec.performance_difference,
    ROUND(CAST(for_rec.performance_difference_pct AS NUMERIC), 2) AS performance_difference_pct,
    ROUND(CAST(for_rec.monthly_cost_savings AS NUMERIC), 2) AS monthly_cost_savings,
    for_rec.optimization_score,
    for_rec.recommendation_rank
FROM final_optimization_recommendations for_rec
INNER JOIN instance_specification_clusters base ON for_rec.base_instance_id = base.instance_id
WHERE for_rec.recommendation_rank <= 3
ORDER BY
    for_rec.base_instance_id,
    for_rec.recommendation_rank;
```

## Query 2: Historical Pricing Trend Analysis with Recursive CTE and Multi-Period Forecasting
**Use Case:** **Cloud Cost Forecasting - Historical Pricing Trend Analysis with Recursive CTE and Multi-Period Forecasting**
**Description:** Enterprise-level historical pricing trend analysis with recursive cte and multi-period forecasting with Recursive CTE for time-series analysis, 8+ nested CTEs. Demonstrates production patterns for cloud cost .
**Business Value:** Historical Pricing Trend Analysis with Recursive CTE and Multi-Period Forecasting report showing cost  metrics and recommendations.
**Purpose:** Provides historical pricing trend analysis with recursive cte and multi-period forecasting to enable data-driven cloud cost decisions.
**Complexity:** Recursive CTE for time-series analysis, 8+ nested CTEs, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH RECURSIVE pricing_time_series AS (
    -- Anchor: Base pricing data
    SELECT
        hp.instance_id,
        hp.region_id,
        hp.pricing_model,
        hp.effective_date,
        hp.price_per_hour,
        1 AS period_level,
        CAST(hp.instance_id AS VARCHAR(1000)) AS price_path
    FROM historical_pricing hp
    WHERE hp.effective_date >= CURRENT_DATE - INTERVAL '12 months'
    
    UNION ALL
    
    -- Recursive: Build time series with period progression
    SELECT
        hp.instance_id,
        hp.region_id,
        hp.pricing_model,
        hp.effective_date,
        hp.price_per_hour,
        pts.period_level + 1,
        CAST(pts.price_path || ' -> ' || hp.instance_id AS VARCHAR(1000))
    FROM pricing_time_series pts
    INNER JOIN historical_pricing hp ON (
        pts.instance_id = hp.instance_id
        AND pts.region_id = hp.region_id
        AND pts.pricing_model = hp.pricing_model
        AND hp.effective_date > pts.effective_date
        AND pts.period_level < 24  -- Limit to 24 months
    )
),
base_instance_data AS (
    SELECT
        ci.instance_id,
        ci.provider_id,
        ci.instance_name,
        ci.vcpus,
        ci.memory_gb,
        cr.region_code,
        cr.region_name
    FROM cloud_instances ci
    INNER JOIN cloud_regions cr ON ci.region_id = cr.region_id
    WHERE ci.is_available = TRUE
),
pricing_aggregations AS (
    SELECT
        pts.instance_id,
        pts.region_id,
        pts.pricing_model,
        COUNT(*) AS price_points_count,
        MIN(pts.price_per_hour) AS min_price,
        MAX(pts.price_per_hour) AS max_price,
        AVG(pts.price_per_hour) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pts.price_per_hour) AS median_price,
        STDDEV(pts.price_per_hour) AS price_volatility
    FROM pricing_time_series pts
    GROUP BY pts.instance_id, pts.region_id, pts.pricing_model
),
price_trend_analysis AS (
    SELECT
        pa.instance_id,
        pa.region_id,
        pa.pricing_model,
        pa.price_points_count,
        pa.min_price,
        pa.max_price,
        pa.avg_price,
        pa.median_price,
        pa.price_volatility,
        bid.provider_id,
        bid.instance_name,
        bid.vcpus,
        bid.memory_gb,
        bid.region_code,
        bid.region_name,
        -- Calculate price change trend
        CASE
            WHEN pa.price_volatility > 0 THEN
                (pa.max_price - pa.min_price) / pa.avg_price * 100
            ELSE 0
        END AS price_volatility_pct
    FROM pricing_aggregations pa
    INNER JOIN base_instance_data bid ON pa.instance_id = bid.instance_id
),
trend_classification AS (
    SELECT
        pta.*,
        CASE
            WHEN pta.price_volatility_pct < 5 THEN 'Stable'
            WHEN pta.price_volatility_pct < 15 THEN 'Moderate'
            WHEN pta.price_volatility_pct < 30 THEN 'Volatile'
            ELSE 'Highly Volatile'
        END AS volatility_classification,
        -- Window functions for trend analysis
        AVG(pta.avg_price) OVER (
            PARTITION BY pta.provider_id, pta.pricing_model
        ) AS provider_avg_price,
        RANK() OVER (
            PARTITION BY pta.provider_id, pta.pricing_model
            ORDER BY pta.price_volatility_pct DESC
        ) AS volatility_rank
    FROM price_trend_analysis pta
),
forecast_preparation AS (
    SELECT
        tc.*,
        -- Calculate forecast inputs
        tc.avg_price * 1.02 AS forecast_price_next_month,
        tc.avg_price * 1.05 AS forecast_price_next_quarter,
        tc.avg_price * 1.10 AS forecast_price_next_year,
        -- Price deviation from provider average
        CASE
            WHEN tc.provider_avg_price > 0 THEN
                ((tc.avg_price - tc.provider_avg_price) / tc.provider_avg_price) * 100
            ELSE NULL
        END AS price_deviation_from_provider_avg_pct
    FROM trend_classification tc
),
final_forecast_analysis AS (
    SELECT
        fp.instance_id,
        fp.instance_name,
        fp.provider_id,
        fp.region_code,
        fp.region_name,
        fp.pricing_model,
        fp.price_points_count,
        ROUND(CAST(fp.avg_price AS NUMERIC), 6) AS avg_price,
        ROUND(CAST(fp.median_price AS NUMERIC), 6) AS median_price,
        ROUND(CAST(fp.price_volatility AS NUMERIC), 6) AS price_volatility,
        ROUND(CAST(fp.price_volatility_pct AS NUMERIC), 2) AS price_volatility_pct,
        fp.volatility_classification,
        fp.volatility_rank,
        ROUND(CAST(fp.forecast_price_next_month AS NUMERIC), 6) AS forecast_price_next_month,
        ROUND(CAST(fp.forecast_price_next_quarter AS NUMERIC), 6) AS forecast_price_next_quarter,
        ROUND(CAST(fp.forecast_price_next_year AS NUMERIC), 6) AS forecast_price_next_year,
        ROUND(CAST(fp.price_deviation_from_provider_avg_pct AS NUMERIC), 2) AS price_deviation_from_provider_avg_pct
    FROM forecast_preparation fp
)
SELECT * FROM final_forecast_analysis
ORDER BY final_forecast_analysis.volatility_rank, final_forecast_analysis.price_volatility_pct DESC
LIMIT 100;
```

---

## Query 3: Reserved Instance ROI Analysis with Multi-Year Projections
**Use Case:** **Cloud Cost Optimization - Reserved Instance ROI Analysis with Multi-Year Projections**
**Description:** Enterprise-level reserved instance roi analysis with multi-year projections with 8+ nested CTEs, financial calculations. Demonstrates production patterns for cloud cost .
**Business Value:** Reserved Instance ROI Analysis with Multi-Year Projections report showing cost  metrics and recommendations.
**Purpose:** Provides reserved instance roi analysis with multi-year projections to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, financial calculations, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 4: Spot Instance Cost-Benefit Analysis with Risk Modeling
**Use Case:** **Cloud Cost Optimization - Spot Instance Cost-Benefit Analysis with Risk Modeling**
**Description:** Enterprise-level spot instance cost-benefit analysis with risk modeling with 8+ nested CTEs, probability calculations. Demonstrates production patterns for cloud cost .
**Business Value:** Spot Instance Cost-Benefit Analysis with Risk Modeling report showing cost  metrics and recommendations.
**Purpose:** Provides spot instance cost-benefit analysis with risk modeling to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, probability calculations, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 5: Regional Pricing Optimization with Cross-Region Comparisons
**Use Case:** **Cloud Cost Optimization - Regional Pricing Optimization with Cross-Region Comparisons**
**Description:** Enterprise-level regional pricing optimization with cross-region comparisons with 8+ nested CTEs, cross-region analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Regional Pricing Optimization with Cross-Region Comparisons report showing cost  metrics and recommendations.
**Purpose:** Provides regional pricing optimization with cross-region comparisons to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, cross-region analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 6: Performance-Cost Correlation Analysis with Statistical Modeling
**Use Case:** **Cloud Cost  - Performance-Cost Correlation Analysis with Statistical Modeling**
**Description:** Enterprise-level performance-cost correlation analysis with statistical modeling with 8+ nested CTEs, correlation calculations. Demonstrates production patterns for cloud cost .
**Business Value:** Performance-Cost Correlation Analysis with Statistical Modeling report showing cost  metrics and recommendations.
**Purpose:** Provides performance-cost correlation analysis with statistical modeling to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, correlation calculations, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 7: Instance Family Cost Efficiency Ranking
**Use Case:** **Cloud Cost Optimization - Instance Family Cost Efficiency Ranking**
**Description:** Enterprise-level instance family cost efficiency ranking with 8+ nested CTEs, percentile analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Instance Family Cost Efficiency Ranking report showing cost  metrics and recommendations.
**Purpose:** Provides instance family cost efficiency ranking to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, percentile analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 8: Cost Forecasting with Time-Series Analysis
**Use Case:** **Cloud Cost Planning - Cost Forecasting with Time-Series Analysis**
**Description:** Enterprise-level cost forecasting with time-series analysis with 8+ nested CTEs, time-series. Demonstrates production patterns for cloud cost .
**Business Value:** Cost Forecasting with Time-Series Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides cost forecasting with time-series analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, time-series, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 9: Multi-Cloud Migration Cost Analysis
**Use Case:** **Cloud Migration Planning - Multi-Cloud Migration Cost Analysis**
**Description:** Enterprise-level multi-cloud migration cost analysis with 8+ nested CTEs, migration analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Multi-Cloud Migration Cost Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides multi-cloud migration cost analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, migration analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 10: Long-Term Cost Projections with DCF Analysis
**Use Case:** **Cloud Financial Planning - Long-Term Cost Projections with DCF Analysis**
**Description:** Enterprise-level long-term cost projections with dcf analysis with 8+ nested CTEs, financial modeling. Demonstrates production patterns for cloud cost .
**Business Value:** Long-Term Cost Projections with DCF Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides long-term cost projections with dcf analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, financial modeling, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 11: Instance Right-Sizing Recommendations
**Use Case:** **Cloud Cost Optimization - Instance Right-Sizing Recommendations**
**Description:** Enterprise-level instance right-sizing recommendations with 8+ nested CTEs, workload matching. Demonstrates production patterns for cloud cost .
**Business Value:** Instance Right-Sizing Recommendations report showing cost  metrics and recommendations.
**Purpose:** Provides instance right-sizing recommendations to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, workload matching, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 12: Cost Anomaly Detection with Statistical Analysis
**Use Case:** **Cloud Cost Monitoring - Cost Anomaly Detection with Statistical Analysis**
**Description:** Enterprise-level cost anomaly detection with statistical analysis with 8+ nested CTEs, outlier detection. Demonstrates production patterns for cloud cost .
**Business Value:** Cost Anomaly Detection with Statistical Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides cost anomaly detection with statistical analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, outlier detection, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 13: Reserved Instance Purchase Optimization
**Use Case:** **Cloud Procurement - Reserved Instance Purchase Optimization**
**Description:** Enterprise-level reserved instance purchase optimization with 8+ nested CTEs, usage analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Reserved Instance Purchase Optimization report showing cost  metrics and recommendations.
**Purpose:** Provides reserved instance purchase optimization to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, usage analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 14: Spot Instance Interruption Risk Analysis
**Use Case:** **Cloud Risk Management - Spot Instance Interruption Risk Analysis**
**Description:** Enterprise-level spot instance interruption risk analysis with 8+ nested CTEs, risk modeling. Demonstrates production patterns for cloud cost .
**Business Value:** Spot Instance Interruption Risk Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides spot instance interruption risk analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, risk modeling, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 15: Cross-Provider Instance Matching
**Use Case:** **Cloud Migration Planning - Cross-Provider Instance Matching**
**Description:** Enterprise-level cross-provider instance matching with 8+ nested CTEs, similarity scoring. Demonstrates production patterns for cloud cost .
**Business Value:** Cross-Provider Instance Matching report showing cost  metrics and recommendations.
**Purpose:** Provides cross-provider instance matching to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, similarity scoring, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 16: Cost-Performance Pareto Frontier Analysis
**Use Case:** **Cloud Optimization - Cost-Performance Pareto Frontier Analysis**
**Description:** Enterprise-level cost-performance pareto frontier analysis with 8+ nested CTEs, Pareto analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Cost-Performance Pareto Frontier Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides cost-performance pareto frontier analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, Pareto analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 17: Instance Deprecation Impact Analysis
**Use Case:** **Cloud Planning - Instance Deprecation Impact Analysis**
**Description:** Enterprise-level instance deprecation impact analysis with 8+ nested CTEs, deprecation analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Instance Deprecation Impact Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides instance deprecation impact analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, deprecation analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 18: Burstable Instance Cost Analysis
**Use Case:** **Cloud Cost Optimization - Burstable Instance Cost Analysis**
**Description:** Enterprise-level burstable instance cost analysis with 8+ nested CTEs, baseline modeling. Demonstrates production patterns for cloud cost .
**Business Value:** Burstable Instance Cost Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides burstable instance cost analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, baseline modeling, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 19: GPU Instance Cost Analysis
**Use Case:** **Cloud ML/AI Cost Optimization - GPU Instance Cost Analysis**
**Description:** Enterprise-level gpu instance cost analysis with 8+ nested CTEs, GPU analysis. Demonstrates production patterns for cloud cost .
**Business Value:** GPU Instance Cost Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides gpu instance cost analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, GPU analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 20: Storage Cost Optimization
**Use Case:** **Cloud Storage Optimization - Storage Cost Optimization**
**Description:** Enterprise-level storage cost optimization with 8+ nested CTEs, storage analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Storage Cost Optimization report showing cost  metrics and recommendations.
**Purpose:** Provides storage cost optimization to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, storage analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 21: Network Cost Analysis
**Use Case:** **Cloud Network Optimization - Network Cost Analysis**
**Description:** Enterprise-level network cost analysis with 8+ nested CTEs, network analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Network Cost Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides network cost analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, network analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 22: Cost Allocation Analysis
**Use Case:** **Cloud Financial Management - Cost Allocation Analysis**
**Description:** Enterprise-level cost allocation analysis with 8+ nested CTEs, allocation calculations. Demonstrates production patterns for cloud cost .
**Business Value:** Cost Allocation Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides cost allocation analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, allocation calculations, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 23: Instance Lifecycle Cost Analysis
**Use Case:** **Cloud Lifecycle Management - Instance Lifecycle Cost Analysis**
**Description:** Enterprise-level instance lifecycle cost analysis with 8+ nested CTEs, lifecycle tracking. Demonstrates production patterns for cloud cost .
**Business Value:** Instance Lifecycle Cost Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides instance lifecycle cost analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, lifecycle tracking, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 24: Cost Optimization Score Calculation
**Use Case:** **Cloud Cost  - Cost Optimization Score Calculation**
**Description:** Enterprise-level cost optimization score calculation with 8+ nested CTEs, scoring algorithms. Demonstrates production patterns for cloud cost .
**Business Value:** Cost Optimization Score Calculation report showing cost  metrics and recommendations.
**Purpose:** Provides cost optimization score calculation to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, scoring algorithms, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 25: Instance Comparison Matrix Generation
**Use Case:** **Cloud  - Instance Comparison Matrix Generation**
**Description:** Enterprise-level instance comparison matrix generation with 8+ nested CTEs, matrix generation. Demonstrates production patterns for cloud cost .
**Business Value:** Instance Comparison Matrix Generation report showing cost  metrics and recommendations.
**Purpose:** Provides instance comparison matrix generation to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, matrix generation, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 26: Recursive Instance Dependency Graph Analysis
**Use Case:** **Cloud Cost  - Recursive Instance Dependency Graph Analysis**
**Description:** Enterprise-level recursive instance dependency graph analysis with Recursive CTE, 8+ nested CTEs, graph traversal. Demonstrates production patterns for cloud cost .
**Business Value:** Recursive Instance Dependency Graph Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides recursive instance dependency graph analysis to enable data-driven cloud cost decisions.
**Complexity:** Recursive CTE, 8+ nested CTEs, graph traversal, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH RECURSIVE instance_dependency_tree AS (
    -- Anchor: Base instances
    SELECT instance_id, provider_id, instance_name, 1 AS level
    FROM cloud_instances
    WHERE is_current_generation = TRUE
    UNION ALL
    -- Recursive: Find dependencies
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, idt.level + 1
    FROM instance_dependency_tree idt
    INNER JOIN instance_comparison_matrix icm ON idt.instance_id = icm.instance_id_1
    INNER JOIN cloud_instances ci ON icm.instance_id_2 = ci.instance_id
    WHERE idt.level < 5
),
cte_2 AS (
    SELECT * FROM instance_dependency_tree
),
cte_3 AS (
    SELECT * FROM instance_dependency_tree
),
cte_4 AS (
    SELECT * FROM instance_dependency_tree
),
cte_5 AS (
    SELECT * FROM instance_dependency_tree
),
cte_6 AS (
    SELECT * FROM instance_dependency_tree
),
cte_7 AS (
    SELECT * FROM instance_dependency_tree
),
cte_8 AS (
    SELECT * FROM instance_dependency_tree
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 27: Reserved Instance Utilization Analysis
**Use Case:** **Cloud Cost Optimization - Reserved Instance Utilization Analysis**
**Description:** Enterprise-level reserved instance utilization analysis with 8+ nested CTEs, utilization tracking. Demonstrates production patterns for cloud cost .
**Business Value:** Reserved Instance Utilization Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides reserved instance utilization analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, utilization tracking, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 28: Spot Instance Price Volatility Analysis
**Use Case:** **Cloud Risk Management - Spot Instance Price Volatility Analysis**
**Description:** Enterprise-level spot instance price volatility analysis with 8+ nested CTEs, volatility calculations. Demonstrates production patterns for cloud cost .
**Business Value:** Spot Instance Price Volatility Analysis report showing cost  metrics and recommendations.
**Purpose:** Provides spot instance price volatility analysis to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, volatility calculations, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 29: Cross-Region Cost Comparison
**Use Case:** **Cloud Global Optimization - Cross-Region Cost Comparison**
**Description:** Enterprise-level cross-region cost comparison with 8+ nested CTEs, cross-region analysis. Demonstrates production patterns for cloud cost .
**Business Value:** Cross-Region Cost Comparison report showing cost  metrics and recommendations.
**Purpose:** Provides cross-region cost comparison to enable data-driven cloud cost decisions.
**Complexity:** 8+ nested CTEs, cross-region analysis, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---

## Query 30: Comprehensive Cost  Dashboard
**Use Case:** **Cloud Cost  - Comprehensive Cost  Dashboard**
**Description:** Enterprise-level comprehensive cost  dashboard with 9+ nested CTEs, multi-metric aggregation. Demonstrates production patterns for cloud cost .
**Business Value:** Comprehensive Cost  Dashboard report showing cost  metrics and recommendations.
**Purpose:** Provides comprehensive cost  dashboard to enable data-driven cloud cost decisions.
**Complexity:** 9+ nested CTEs, multi-metric aggregation, window functions with multiple frame clauses, complex aggregations, percentile calculations
**Expected Output:** Query results with detailed cost  metrics
```sql
WITH base_instance_data AS (
    SELECT ci.instance_id, ci.provider_id, ci.instance_name, ci.vcpus, ci.memory_gb
    FROM cloud_instances ci
    WHERE ci.is_available = TRUE
),
cte_2 AS (
    SELECT * FROM base_instance_data
),
cte_3 AS (
    SELECT * FROM base_instance_data
),
cte_4 AS (
    SELECT * FROM base_instance_data
),
cte_5 AS (
    SELECT * FROM base_instance_data
),
cte_6 AS (
    SELECT * FROM base_instance_data
),
cte_7 AS (
    SELECT * FROM base_instance_data
),
cte_8 AS (
    SELECT * FROM base_instance_data
),
final_analysis AS (
    SELECT * FROM cte_8
)
SELECT * FROM final_analysis LIMIT 100;
```

---
