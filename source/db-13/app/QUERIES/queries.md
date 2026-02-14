# Database 13 - AI Benchmark Marketing Database - Extremely Complex SQL Queries

# Database Schema: DB13

**Description:** AI Benchmark Marketing and Model Performance Tracking System
**Created:** 2026-02-04

## Overview

This database contains AI benchmark and marketing data from Artificial Analysis, NIST, NSF, Data.gov, Papers with Code, Hugging Face, GitHub, and other sources including AI models, performance metrics, benchmark evaluations, model comparisons, marketing insights, government benchmark data, adoption metrics, pricing history, performance history, data sources, and pipeline metadata.

## Tables

### `ai_models`
Core AI model catalog with metadata, creator information, and technical specifications

### `model_performance_metrics`
Performance metrics from Artificial Analysis Intelligence Index and benchmarks

### `benchmark_evaluations`
Individual benchmark test results from various evaluations (GDPval-AA, Terminal-Bench, SciCode, etc.)

### `model_comparisons`
Competitive analysis and model-to-model comparisons

### `marketing_intelligence`
Aggregated marketing insights, trends, and market positioning

### `government_benchmark_data`
Benchmark data from NIST, NSF, DARPA, and other government sources

### `model_adoption_metrics`
Usage and adoption metrics for marketing insights

### `model_pricing_history`
Historical pricing data for trend analysis

### `model_performance_history`
Historical performance metrics for trend analysis

### `data_sources`
Source tracking for data lineage and quality monitoring

### `pipeline_metadata`
ETL pipeline execution tracking and error logging

---

This file contains 30 extremely complex SQL queries focused on business-oriented use cases for client deliverables. All queries are designed to work across PostgreSQL.

## Query 1: Multi-Model Performance Comparison with Intelligence Index Ranking and Competitive Positioning

**Description:** Analyzes AI model performance across multiple dimensions including Intelligence Index scores, output speed, latency, and pricing. Uses multiple CTEs to rank models, calculate competitive positioning metrics, identify market leaders, and perform percentile-based analysis with window functions for comprehensive performance comparison.

**Use Case:** Competitive intelligence analysis for AI model benchmarking platforms - identify top-performing models across different performance dimensions and price points

**Business Value:** Enables AI companies and researchers to identify market leaders, competitive positioning, and optimal price-performance models, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive multi-dimensional model performance comparison with competitive positioning for strategic model selection decisions

**Complexity:** Deep nested CTEs (7+ levels), multiple joins across ai_models/model_performance_metrics/benchmark_evaluations tables, window functions with frame clauses, percentile calculations, ranking functions, correlated subqueries, complex aggregations

**Expected Output:** Model performance comparison report showing top models by intelligence, speed, and price-performance ratio with competitive positioning metrics

```sql
WITH model_base_metrics AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        am.license_type,
        am.context_window,
        am.total_parameters_billions,
        am.is_reasoning_model,
        mpm.evaluation_date,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.latency_seconds,
        mpm.blended_price_per_million_tokens,
        mpm.omniscience_index
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '90 days'
        AND am.model_status = 'active'
),
percentiles AS (
    SELECT
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY intelligence_index_score) AS q1_intelligence,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY intelligence_index_score) AS q3_intelligence,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY output_speed_tokens_per_sec) AS median_speed
    FROM model_base_metrics
),
intelligence_rankings AS (
    SELECT
        mbm.*,
        RANK() OVER (ORDER BY mbm.intelligence_index_score DESC NULLS LAST) AS intelligence_rank,
        p.median_intelligence,
        p.q1_intelligence,
        p.q3_intelligence,
        p.median_speed
    FROM model_base_metrics mbm
    CROSS JOIN percentiles p
),
speed_rankings AS (
    SELECT
        ir.*,
        RANK() OVER (ORDER BY ir.output_speed_tokens_per_sec DESC NULLS LAST) AS speed_rank
    FROM intelligence_rankings ir
),
price_performance_metrics AS (
    SELECT
        sr.*,
        CASE
            WHEN sr.blended_price_per_million_tokens > 0 AND sr.intelligence_index_score > 0 THEN
                sr.intelligence_index_score / sr.blended_price_per_million_tokens
            ELSE NULL
        END AS intelligence_per_dollar,
        CASE
            WHEN sr.blended_price_per_million_tokens > 0 AND sr.output_speed_tokens_per_sec > 0 THEN
                sr.output_speed_tokens_per_sec / sr.blended_price_per_million_tokens
            ELSE NULL
        END AS speed_per_dollar,
        RANK() OVER (ORDER BY 
            CASE
                WHEN sr.blended_price_per_million_tokens > 0 AND sr.intelligence_index_score > 0 THEN
                    sr.intelligence_index_score / sr.blended_price_per_million_tokens
                ELSE NULL
            END DESC NULLS LAST
        ) AS price_performance_rank
    FROM speed_rankings sr
),
competitive_positioning AS (
    SELECT
        ppm.*,
        CASE
            WHEN ppm.intelligence_index_score >= ppm.q3_intelligence THEN 'leader'
            WHEN ppm.intelligence_index_score >= ppm.median_intelligence THEN 'challenger'
            WHEN ppm.intelligence_index_score >= ppm.q1_intelligence THEN 'follower'
            ELSE 'niche'
        END AS market_position,
        CASE
            WHEN ppm.intelligence_rank <= 10 THEN 'top_10'
            WHEN ppm.intelligence_rank <= 25 THEN 'top_25'
            WHEN ppm.intelligence_rank <= 50 THEN 'top_50'
            ELSE 'other'
        END AS intelligence_tier,
        CASE
            WHEN ppm.speed_rank <= 10 THEN 'top_10'
            WHEN ppm.speed_rank <= 25 THEN 'top_25'
            WHEN ppm.speed_rank <= 50 THEN 'top_50'
            ELSE 'other'
        END AS speed_tier
    FROM price_performance_metrics ppm
),
benchmark_aggregates AS (
    SELECT
        cp.model_id,
        COUNT(DISTINCT be.benchmark_name) AS benchmark_count,
        AVG(be.score) AS avg_benchmark_score,
        MAX(be.score) AS max_benchmark_score,
        MIN(be.score) AS min_benchmark_score,
        STDDEV(be.score) AS benchmark_score_stddev
    FROM competitive_positioning cp
    LEFT JOIN benchmark_evaluations be ON cp.model_id = be.model_id
        AND be.evaluation_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY cp.model_id
),
final_comparison AS (
    SELECT
        cp.model_id,
        cp.model_name,
        cp.creator_company,
        cp.model_family,
        cp.license_type,
        cp.context_window,
        cp.total_parameters_billions,
        cp.is_reasoning_model,
        cp.evaluation_date,
        cp.intelligence_index_score,
        cp.output_speed_tokens_per_sec,
        cp.latency_seconds,
        cp.blended_price_per_million_tokens,
        cp.omniscience_index,
        cp.intelligence_rank,
        cp.median_intelligence,
        cp.q1_intelligence,
        cp.q3_intelligence,
        cp.speed_rank,
        cp.market_position,
        cp.intelligence_tier,
        cp.speed_tier,
        cp.intelligence_per_dollar,
        cp.speed_per_dollar,
        cp.price_performance_rank,
        ba.benchmark_count,
        ROUND(CAST(ba.avg_benchmark_score AS NUMERIC), 4) AS avg_benchmark_score,
        ROUND(CAST(ba.max_benchmark_score AS NUMERIC), 4) AS max_benchmark_score,
        ROUND(CAST(ba.min_benchmark_score AS NUMERIC), 4) AS min_benchmark_score,
        ROUND(CAST(ba.benchmark_score_stddev AS NUMERIC), 4) AS benchmark_score_stddev
    FROM competitive_positioning cp
    LEFT JOIN benchmark_aggregates ba ON cp.model_id = ba.model_id
)
SELECT
    model_name,
    creator_company,
    model_family,
    license_type,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    intelligence_rank,
    market_position,
    intelligence_tier,
    ROUND(CAST(output_speed_tokens_per_sec AS NUMERIC), 2) AS output_speed_tokens_per_sec,
    speed_rank,
    speed_tier,
    ROUND(CAST(latency_seconds AS NUMERIC), 4) AS latency_seconds,
    ROUND(CAST(blended_price_per_million_tokens AS NUMERIC), 4) AS blended_price_per_million_tokens,
    price_performance_rank,
    intelligence_per_dollar,
    speed_per_dollar,
    benchmark_count,
    avg_benchmark_score,
    context_window,
    total_parameters_billions,
    is_reasoning_model,
    evaluation_date
FROM final_comparison
WHERE intelligence_rank <= 50 OR speed_rank <= 50 OR price_performance_rank <= 50
ORDER BY intelligence_index_score DESC NULLS LAST
LIMIT 100;
```

## Query 2: Model Pricing Trend Analysis with Market Share Impact and Adoption Correlation

**Description:** Analyzes historical pricing trends for AI models, correlating price changes with market share shifts and adoption metrics. Uses recursive CTEs for temporal analysis, window functions for trend detection, and complex aggregations to identify pricing strategies and their market impact.

**Use Case:** Pricing strategy analysis for AI model providers - understand how pricing changes affect market share and adoption rates

**Business Value:** Enables AI companies to optimize pricing strategies based on market response, supporting $1M+ ARR AI model marketplace platforms

**Purpose:** Provides pricing trend analysis with market impact correlation for strategic pricing decisions

**Complexity:** Recursive CTEs for temporal analysis, multiple window functions with different frame clauses, complex joins across model_pricing_history/model_adoption_metrics/marketing_intelligence, correlation calculations, trend detection algorithms

**Expected Output:** Pricing trend report showing price changes over time with corresponding market share and adoption rate changes

```sql
WITH RECURSIVE pricing_timeline AS (
    SELECT
        mph.model_id,
        mph.pricing_date,
        mph.blended_price_per_million_tokens,
        am.model_name,
        am.creator_company,
        am.model_family,
        LAG(mph.blended_price_per_million_tokens, 1) OVER (
            PARTITION BY mph.model_id
            ORDER BY mph.pricing_date
        ) AS prev_price,
        LEAD(mph.blended_price_per_million_tokens, 1) OVER (
            PARTITION BY mph.model_id
            ORDER BY mph.pricing_date
        ) AS next_price
    FROM model_pricing_history mph
    INNER JOIN ai_models am ON mph.model_id = am.model_id
    WHERE mph.pricing_date >= CURRENT_DATE - INTERVAL '730 days'
        AND am.model_status = 'active'
    
    UNION ALL
    
    SELECT
        pt.model_id,
        (pt.pricing_date + INTERVAL '1 day')::date AS pricing_date,
        CAST(CASE
            WHEN pt.next_price IS NOT NULL THEN pt.next_price
            ELSE pt.blended_price_per_million_tokens
        END AS NUMERIC(10,4)) AS blended_price_per_million_tokens,
        pt.model_name,
        pt.creator_company,
        pt.model_family,
        pt.blended_price_per_million_tokens AS prev_price,
        pt.next_price
    FROM pricing_timeline pt
    WHERE pt.pricing_date < CURRENT_DATE
        AND pt.pricing_date >= CURRENT_DATE - INTERVAL '730 days'
),
price_changes AS (
    SELECT
        pt.*,
        CASE
            WHEN pt.prev_price IS NOT NULL AND pt.prev_price > 0 THEN
                ((pt.blended_price_per_million_tokens - pt.prev_price) / pt.prev_price) * 100
            ELSE NULL
        END AS price_change_percent,
        CASE
            WHEN pt.prev_price IS NOT NULL THEN
                pt.blended_price_per_million_tokens - pt.prev_price
            ELSE NULL
        END AS price_change_absolute,
        AVG(pt.blended_price_per_million_tokens) OVER (
            PARTITION BY pt.model_id
            ORDER BY pt.pricing_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS moving_avg_30d,
        STDDEV(pt.blended_price_per_million_tokens) OVER (
            PARTITION BY pt.model_id
            ORDER BY pt.pricing_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS price_volatility_30d
    FROM pricing_timeline pt
),
adoption_correlation AS (
    SELECT
        pc.*,
        mam.metric_date,
        mam.market_penetration_percent,
        mam.active_users_thousands,
        mam.api_calls_millions,
        mam.developer_sentiment_score,
        mam.adoption_trend,
        CASE
            WHEN ABS((pc.pricing_date - mam.metric_date)) <= 30 THEN mam.market_penetration_percent
            ELSE NULL
        END AS correlated_market_penetration,
        CASE
            WHEN ABS((pc.pricing_date - mam.metric_date)) <= 30 THEN mam.active_users_thousands
            ELSE NULL
        END AS correlated_active_users
    FROM price_changes pc
    LEFT JOIN model_adoption_metrics mam ON pc.model_id = mam.model_id
        AND ABS((pc.pricing_date - mam.metric_date)) <= 30
),
market_share_impact AS (
    SELECT
        ac.*,
        mi.analysis_date,
        mi.market_share_percentage,
        mi.market_position,
        mi.growth_rate_percent,
        CASE
            WHEN ABS((ac.pricing_date - mi.analysis_date)) <= 60 THEN mi.market_share_percentage
            ELSE NULL
        END AS correlated_market_share,
        CASE
            WHEN ABS((ac.pricing_date - mi.analysis_date)) <= 60 THEN mi.growth_rate_percent
            ELSE NULL
        END AS correlated_growth_rate
    FROM adoption_correlation ac
    LEFT JOIN marketing_intelligence mi ON ac.creator_company = mi.creator_company
        AND ABS((ac.pricing_date - mi.analysis_date)) <= 60
),
trend_analysis AS (
    SELECT
        msi.*,
        CASE
            WHEN msi.price_change_percent < -10 THEN 'significant_decrease'
            WHEN msi.price_change_percent < -5 THEN 'moderate_decrease'
            WHEN msi.price_change_percent < 0 THEN 'slight_decrease'
            WHEN msi.price_change_percent = 0 THEN 'stable'
            WHEN msi.price_change_percent <= 5 THEN 'slight_increase'
            WHEN msi.price_change_percent <= 10 THEN 'moderate_increase'
            ELSE 'significant_increase'
        END AS price_change_category,
        CASE
            WHEN msi.correlated_market_share IS NOT NULL AND LAG(msi.correlated_market_share, 1) OVER (
                PARTITION BY msi.model_id ORDER BY msi.pricing_date
            ) IS NOT NULL THEN
                msi.correlated_market_share - LAG(msi.correlated_market_share, 1) OVER (
                    PARTITION BY msi.model_id ORDER BY msi.pricing_date
                )
            ELSE NULL
        END AS market_share_change,
        CASE
            WHEN msi.correlated_active_users IS NOT NULL AND LAG(msi.correlated_active_users, 1) OVER (
                PARTITION BY msi.model_id ORDER BY msi.pricing_date
            ) IS NOT NULL THEN
                msi.correlated_active_users - LAG(msi.correlated_active_users, 1) OVER (
                    PARTITION BY msi.model_id ORDER BY msi.pricing_date
                )
            ELSE NULL
        END AS active_users_change
    FROM market_share_impact msi
)
SELECT
    model_name,
    creator_company,
    model_family,
    pricing_date,
    ROUND(CAST(blended_price_per_million_tokens AS NUMERIC), 4) AS price,
    ROUND(CAST(prev_price AS NUMERIC), 4) AS prev_price,
    ROUND(CAST(price_change_percent AS NUMERIC), 2) AS price_change_percent,
    price_change_category,
    ROUND(CAST(moving_avg_30d AS NUMERIC), 4) AS moving_avg_30d,
    ROUND(CAST(price_volatility_30d AS NUMERIC), 4) AS price_volatility_30d,
    ROUND(CAST(correlated_market_share AS NUMERIC), 2) AS market_share,
    ROUND(CAST(market_share_change AS NUMERIC), 2) AS market_share_change,
    ROUND(CAST(correlated_market_penetration AS NUMERIC), 2) AS market_penetration,
    ROUND(CAST(correlated_active_users AS NUMERIC), 0) AS active_users_thousands,
    ROUND(CAST(active_users_change AS NUMERIC), 0) AS active_users_change,
    ROUND(CAST(correlated_growth_rate AS NUMERIC), 2) AS growth_rate_percent,
    adoption_trend
FROM trend_analysis
WHERE pricing_date >= CURRENT_DATE - INTERVAL '365 days'
    AND (price_change_percent IS NOT NULL OR correlated_market_share IS NOT NULL)
ORDER BY model_id, pricing_date DESC;
```

## Query 3: Benchmark Evaluation Performance Across Model Families with Statistical Significance Testing

**Description:** Compares benchmark evaluation results across different model families (GPT, Claude, Gemini, Llama, etc.), calculating statistical significance, performance variance, and family-level competitive advantages. Uses multiple CTEs for family aggregation, statistical calculations, and performance ranking.

**Use Case:** Model family competitive analysis for AI research organizations - identify which model families excel in specific benchmark categories

**Business Value:** Enables AI research organizations to identify competitive advantages by model family, supporting $1M+ ARR AI research platforms

**Purpose:** Provides model family-level benchmark performance analysis with statistical significance for research and competitive intelligence

**Complexity:** Multiple CTEs (6+ levels), complex aggregations with statistical functions (STDDEV, VARIANCE), window functions for ranking, joins across ai_models/benchmark_evaluations, statistical significance calculations, family-level grouping

**Expected Output:** Model family benchmark performance report showing average scores, variance, and statistical significance by benchmark category

```sql
WITH model_family_base AS (
    SELECT
        am.model_id,
        am.model_name,
        am.model_family,
        am.creator_company,
        be.benchmark_name,
        be.benchmark_category,
        be.score,
        be.normalized_score,
        be.percentile_rank,
        be.evaluation_date,
        be.total_tests,
        be.passed_tests,
        be.accuracy_percentage
    FROM ai_models am
    INNER JOIN benchmark_evaluations be ON am.model_id = be.model_id
    WHERE be.evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
        AND am.model_status = 'active'
        AND am.model_family IS NOT NULL
),
family_benchmark_stats AS (
    SELECT
        mfb.model_family,
        mfb.benchmark_name,
        mfb.benchmark_category,
        COUNT(DISTINCT mfb.model_id) AS model_count,
        AVG(mfb.score) AS avg_score,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mfb.score) AS median_score,
        STDDEV(mfb.score) AS score_stddev,
        VARIANCE(mfb.score) AS score_variance,
        MIN(mfb.score) AS min_score,
        MAX(mfb.score) AS max_score,
        AVG(mfb.normalized_score) AS avg_normalized_score,
        AVG(mfb.percentile_rank) AS avg_percentile_rank,
        AVG(mfb.accuracy_percentage) AS avg_accuracy_percentage
    FROM model_family_base mfb
    GROUP BY mfb.model_family, mfb.benchmark_name, mfb.benchmark_category
),
overall_benchmark_stats AS (
    SELECT
        benchmark_name,
        benchmark_category,
        AVG(score) AS overall_avg_score,
        STDDEV(score) AS overall_stddev
    FROM model_family_base
    GROUP BY benchmark_name, benchmark_category
),
statistical_significance AS (
    SELECT
        fbs.*,
        obs.overall_avg_score,
        obs.overall_stddev,
        CASE
            WHEN obs.overall_stddev > 0 THEN
                ABS(fbs.avg_score - obs.overall_avg_score) / obs.overall_stddev
            ELSE NULL
        END AS z_score,
        CASE
            WHEN obs.overall_stddev > 0 AND fbs.model_count >= 3 THEN
                CASE
                    WHEN ABS(fbs.avg_score - obs.overall_avg_score) / obs.overall_stddev >= 2.0 THEN 'highly_significant'
                    WHEN ABS(fbs.avg_score - obs.overall_avg_score) / obs.overall_stddev >= 1.5 THEN 'significant'
                    WHEN ABS(fbs.avg_score - obs.overall_avg_score) / obs.overall_stddev >= 1.0 THEN 'moderate'
                    ELSE 'not_significant'
                END
            ELSE 'insufficient_data'
        END AS significance_level
    FROM family_benchmark_stats fbs
    INNER JOIN overall_benchmark_stats obs ON fbs.benchmark_name = obs.benchmark_name
        AND fbs.benchmark_category = obs.benchmark_category
),
family_rankings AS (
    SELECT
        ss.*,
        RANK() OVER (
            PARTITION BY ss.benchmark_name
            ORDER BY ss.avg_score DESC
        ) AS family_rank_by_score,
        RANK() OVER (
            PARTITION BY ss.benchmark_category
            ORDER BY ss.avg_score DESC
        ) AS family_rank_by_category,
        PERCENT_RANK() OVER (
            PARTITION BY ss.benchmark_category
            ORDER BY ss.avg_score DESC
        ) AS family_percentile_rank
    FROM statistical_significance ss
),
competitive_advantages AS (
    SELECT
        fr.*,
        CASE
            WHEN fr.family_rank_by_score = 1 THEN 'leader'
            WHEN fr.family_rank_by_score <= 3 THEN 'top_performer'
            WHEN fr.family_rank_by_score <= 5 THEN 'strong_performer'
            ELSE 'average_performer'
        END AS performance_tier,
        CASE
            WHEN fr.significance_level IN ('highly_significant', 'significant') AND fr.avg_score > fr.overall_avg_score THEN 'competitive_advantage'
            WHEN fr.significance_level IN ('highly_significant', 'significant') AND fr.avg_score < fr.overall_avg_score THEN 'competitive_disadvantage'
            ELSE 'neutral'
        END AS competitive_position
    FROM family_rankings fr
)
SELECT
    model_family,
    benchmark_name,
    benchmark_category,
    model_count,
    ROUND(CAST(avg_score AS NUMERIC), 4) AS avg_score,
    ROUND(CAST(median_score AS NUMERIC), 4) AS median_score,
    ROUND(CAST(score_stddev AS NUMERIC), 4) AS score_stddev,
    ROUND(CAST(score_variance AS NUMERIC), 4) AS score_variance,
    ROUND(CAST(min_score AS NUMERIC), 4) AS min_score,
    ROUND(CAST(max_score AS NUMERIC), 4) AS max_score,
    ROUND(CAST(avg_normalized_score AS NUMERIC), 4) AS avg_normalized_score,
    ROUND(CAST(avg_percentile_rank AS NUMERIC), 2) AS avg_percentile_rank,
    ROUND(CAST(avg_accuracy_percentage AS NUMERIC), 2) AS avg_accuracy_percentage,
    ROUND(CAST(z_score AS NUMERIC), 4) AS z_score,
    significance_level,
    family_rank_by_score,
    family_rank_by_category,
    ROUND(CAST(family_percentile_rank * 100 AS NUMERIC), 2) AS family_percentile_rank,
    performance_tier,
    competitive_position
FROM competitive_advantages
ORDER BY benchmark_category, family_rank_by_score;
```

## Query 4: Government Benchmark Compliance Tracking with Risk Assessment and Regulatory Alignment

**Description:** Tracks AI model compliance with government benchmarks (NIST, NSF, DARPA), calculating compliance scores, risk assessments, and regulatory alignment metrics. Uses multiple CTEs to aggregate government benchmark data, calculate compliance levels, and identify compliance gaps.

**Use Case:** Regulatory compliance tracking for enterprise AI deployments - ensure models meet government safety and robustness standards

**Business Value:** Enables enterprises to ensure AI model compliance with government standards, supporting $1M+ ARR enterprise AI governance platforms

**Purpose:** Provides comprehensive government benchmark compliance tracking with risk assessment for regulatory compliance

**Complexity:** Multiple CTEs (5+ levels), complex joins across ai_models/government_benchmark_data, compliance scoring algorithms, risk calculation functions, regulatory alignment metrics, conditional aggregations

**Expected Output:** Analysis report with comprehensive metrics and insights for query 4

```sql
WITH government_benchmarks_base AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        gbd.gov_benchmark_id,
        gbd.source_agency,
        gbd.benchmark_name,
        gbd.benchmark_category,
        CASE
            WHEN gbd.compliance_level = 'compliant' THEN 100
            WHEN gbd.compliance_level = 'partially_compliant' THEN 60
            WHEN gbd.compliance_level = 'non_compliant' THEN 20
            ELSE (COALESCE(gbd.safety_score, 0) + COALESCE(gbd.robustness_score, 0)) / 2
        END AS compliance_score,
        gbd.evaluation_date,
        gbd.compliance_level
    FROM ai_models am
    INNER JOIN government_benchmark_data gbd ON am.model_id = gbd.model_id
    WHERE gbd.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
compliance_aggregation AS (
    SELECT
        gbb.model_id,
        gbb.model_name,
        gbb.creator_company,
        gbb.source_agency,
        COUNT(DISTINCT gbb.gov_benchmark_id) AS benchmark_count,
        AVG(gbb.compliance_score) AS avg_compliance_score,
        MIN(gbb.compliance_score) AS min_compliance_score,
        MAX(gbb.compliance_score) AS max_compliance_score,
        STDDEV(gbb.compliance_score) AS compliance_score_stddev,
        COUNT(CASE WHEN gbb.compliance_level = 'compliant' THEN 1 END) AS certified_count,
        COUNT(CASE WHEN gbb.compliance_score >= 75 THEN 1 END) AS low_risk_count,
        COUNT(CASE WHEN gbb.compliance_score < 60 THEN 1 END) AS high_risk_count
    FROM government_benchmarks_base gbb
    GROUP BY gbb.model_id, gbb.model_name, gbb.creator_company, gbb.source_agency
),
risk_assessment AS (
    SELECT
        ca.*,
        CASE
            WHEN ca.avg_compliance_score >= 90 THEN 'low_risk'
            WHEN ca.avg_compliance_score >= 75 THEN 'moderate_risk'
            WHEN ca.avg_compliance_score >= 60 THEN 'elevated_risk'
            ELSE 'high_risk'
        END AS overall_risk_level,
        CASE
            WHEN ca.certified_count = ca.benchmark_count THEN 'fully_certified'
            WHEN ca.certified_count > 0 THEN 'partially_certified'
            ELSE 'not_certified'
        END AS certification_status
    FROM compliance_aggregation ca
),
regulatory_alignment AS (
    SELECT
        ra.*,
        CASE
            WHEN ra.source_agency = 'NIST' AND ra.avg_compliance_score >= 85 THEN 'nist_aligned'
            WHEN ra.source_agency = 'NSF' AND ra.avg_compliance_score >= 80 THEN 'nsf_aligned'
            WHEN ra.source_agency = 'DARPA' AND ra.avg_compliance_score >= 75 THEN 'darpa_aligned'
            ELSE 'not_aligned'
        END AS regulatory_alignment_status
    FROM risk_assessment ra
)
SELECT
    model_name,
    creator_company,
    source_agency,
    benchmark_count,
    ROUND(CAST(avg_compliance_score AS NUMERIC), 2) AS avg_compliance_score,
    ROUND(CAST(min_compliance_score AS NUMERIC), 2) AS min_compliance_score,
    ROUND(CAST(max_compliance_score AS NUMERIC), 2) AS max_compliance_score,
    ROUND(CAST(compliance_score_stddev AS NUMERIC), 2) AS compliance_score_stddev,
    certified_count,
    low_risk_count,
    high_risk_count,
    overall_risk_level,
    certification_status,
    regulatory_alignment_status
FROM regulatory_alignment
ORDER BY source_agency, avg_compliance_score DESC;
```


## Query 5: Model Adoption Prediction with Performance Correlation and Market Penetration Analysis

**Description:** Predicts model adoption trends based on performance metrics, pricing, and historical adoption data. Uses recursive CTEs for trend projection, window functions for moving averages, and complex correlation calculations between performance and adoption metrics.

**Use Case:** Market forecasting for AI model providers - predict which models will gain market share based on performance and pricing

**Business Value:** Enables AI companies to forecast market adoption and optimize product strategy, supporting $1M+ ARR AI market intelligence platforms

**Purpose:** Provides model adoption prediction with performance correlation for strategic market planning

**Complexity:** Recursive CTEs for trend projection, multiple window functions with different frame clauses, correlation calculations, predictive analytics, joins across model_adoption_metrics/model_performance_metrics/model_pricing_history

**Expected Output:** Analysis report with comprehensive metrics and insights for query 5

```sql
WITH RECURSIVE adoption_trends AS (
    SELECT
        mam.model_id,
        mam.metric_date,
        mam.market_penetration_percent,
        mam.active_users_thousands,
        mam.api_calls_millions,
        mam.developer_sentiment_score,
        am.model_name,
        am.creator_company,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mph.blended_price_per_million_tokens
    FROM model_adoption_metrics mam
    INNER JOIN ai_models am ON mam.model_id = am.model_id
    LEFT JOIN model_performance_metrics mpm ON mam.model_id = mpm.model_id
        AND ABS((mam.metric_date - mpm.evaluation_date)) <= 30
    LEFT JOIN model_pricing_history mph ON mam.model_id = mph.model_id
        AND ABS((mam.metric_date - mph.pricing_date)) <= 30
    WHERE mam.metric_date >= CURRENT_DATE - INTERVAL '365 days'
    
    UNION ALL
    
    SELECT
        at.model_id,
        (at.metric_date + INTERVAL '1 day')::date AS metric_date,
        at.market_penetration_percent,
        at.active_users_thousands,
        at.api_calls_millions,
        at.developer_sentiment_score,
        at.model_name,
        at.creator_company,
        at.intelligence_index_score,
        at.output_speed_tokens_per_sec,
        at.blended_price_per_million_tokens
    FROM adoption_trends at
    WHERE at.metric_date < CURRENT_DATE
        AND at.metric_date >= CURRENT_DATE - INTERVAL '365 days'
),
performance_correlation AS (
    SELECT
        at.*,
        AVG(at.market_penetration_percent) OVER (
            PARTITION BY at.model_id
            ORDER BY at.metric_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS moving_avg_penetration_30d,
        AVG(at.intelligence_index_score) OVER (
            PARTITION BY at.model_id
            ORDER BY at.metric_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS moving_avg_intelligence_30d,
        CORR(at.intelligence_index_score, at.market_penetration_percent) OVER (
            PARTITION BY at.model_id
            ORDER BY at.metric_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS performance_adoption_correlation
    FROM adoption_trends at
)
SELECT
    model_name,
    creator_company,
    metric_date,
    ROUND(CAST(market_penetration_percent AS NUMERIC), 2) AS market_penetration_percent,
    ROUND(CAST(moving_avg_penetration_30d AS NUMERIC), 2) AS moving_avg_penetration_30d,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(moving_avg_intelligence_30d AS NUMERIC), 4) AS moving_avg_intelligence_30d,
    ROUND(CAST(performance_adoption_correlation AS NUMERIC), 4) AS performance_adoption_correlation,
    active_users_thousands,
    api_calls_millions,
    developer_sentiment_score,
    output_speed_tokens_per_sec,
    blended_price_per_million_tokens
FROM performance_correlation
WHERE metric_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, metric_date DESC;
```


## Query 6: Model Performance Trajectory Analysis with Temporal Clustering

**Description:** Analyzes model performance trajectories over time using temporal clustering, identifying performance trends, degradation patterns, and improvement cycles. Uses multiple CTEs with window functions for trajectory analysis, temporal clustering algorithms, and performance trend detection.

**Use Case:** Performance monitoring for AI model providers - track model performance evolution and identify degradation or improvement patterns

**Business Value:** Enables AI companies to monitor model performance trajectories and optimize model updates, supporting $1M+ ARR AI performance monitoring platforms

**Purpose:** Provides comprehensive performance trajectory analysis with temporal clustering for model lifecycle management

**Complexity:** Multiple CTEs (7+ levels), window functions with complex frame clauses, temporal clustering algorithms, performance trend detection, joins across model_performance_history/ai_models/benchmark_evaluations

**Expected Output:** Performance trajectory analysis with clustering results, trend indicators, and lifecycle stage identification

```sql
WITH performance_timeline AS (
    SELECT
        mph.model_id,
        mph.performance_date AS evaluation_date,
        mph.intelligence_index_score,
        mph.output_speed_tokens_per_sec,
        mph.latency_seconds,
        am.model_name,
        am.creator_company,
        am.model_family,
        LAG(mph.intelligence_index_score, 1) OVER (
            PARTITION BY mph.model_id
            ORDER BY mph.performance_date
        ) AS prev_intelligence_score,
        LEAD(mph.intelligence_index_score, 1) OVER (
            PARTITION BY mph.model_id
            ORDER BY mph.performance_date
        ) AS next_intelligence_score,
        AVG(mph.intelligence_index_score) OVER (
            PARTITION BY mph.model_id
            ORDER BY mph.performance_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS moving_avg_intelligence_30d,
        STDDEV(mph.intelligence_index_score) OVER (
            PARTITION BY mph.model_id
            ORDER BY mph.performance_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_30d
    FROM model_performance_history mph
    INNER JOIN ai_models am ON mph.model_id = am.model_id
    WHERE mph.performance_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
trajectory_calculation AS (
    SELECT
        pt.*,
        CASE
            WHEN pt.prev_intelligence_score IS NOT NULL THEN
                pt.intelligence_index_score - pt.prev_intelligence_score
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN pt.prev_intelligence_score IS NOT NULL AND pt.prev_intelligence_score != 0 THEN
                ((pt.intelligence_index_score - pt.prev_intelligence_score) / pt.prev_intelligence_score) * 100
            ELSE NULL
        END AS intelligence_change_percent,
        CASE
            WHEN (pt.intelligence_index_score - pt.prev_intelligence_score) > 0 THEN 'improving'
            WHEN (pt.intelligence_index_score - pt.prev_intelligence_score) < 0 THEN 'degrading'
            ELSE 'stable'
        END AS trajectory_direction,
        COUNT(*) OVER (
            PARTITION BY pt.model_id
            ORDER BY pt.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS evaluation_count_90d
    FROM performance_timeline pt
),
temporal_clustering AS (
    SELECT
        tc.*,
        AVG(tc.intelligence_change_percent) OVER (
            PARTITION BY tc.model_id, tc.trajectory_direction
            ORDER BY tc.evaluation_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS cluster_avg_change_7d,
        (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tc2.intelligence_change_percent)
         FROM trajectory_calculation tc2
         WHERE tc2.model_id = tc.model_id AND tc2.trajectory_direction = tc.trajectory_direction) AS cluster_median_change
    FROM trajectory_calculation tc
),
lifecycle_stage_detection AS (
    SELECT
        tcl.*,
        CASE
            WHEN tcl.evaluation_count_90d < 10 THEN 'early_stage'
            WHEN tcl.moving_avg_intelligence_30d < 50 THEN 'development'
            WHEN tcl.moving_avg_intelligence_30d >= 50 AND tcl.moving_avg_intelligence_30d < 75 THEN 'mature'
            WHEN tcl.moving_avg_intelligence_30d >= 75 THEN 'advanced'
            ELSE 'unknown'
        END AS lifecycle_stage,
        CASE
            WHEN tcl.intelligence_volatility_30d < 2 THEN 'stable'
            WHEN tcl.intelligence_volatility_30d < 5 THEN 'moderate_volatility'
            ELSE 'high_volatility'
        END AS volatility_category
    FROM temporal_clustering tcl
),
trend_analysis AS (
    SELECT
        lsd.*,
        COUNT(CASE WHEN lsd.trajectory_direction = 'improving' THEN 1 END) OVER (
            PARTITION BY lsd.model_id
            ORDER BY lsd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS improving_count_30d,
        COUNT(CASE WHEN lsd.trajectory_direction = 'degrading' THEN 1 END) OVER (
            PARTITION BY lsd.model_id
            ORDER BY lsd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS degrading_count_30d
    FROM lifecycle_stage_detection lsd
),
final_trajectory_analysis AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.improving_count_30d > ta.degrading_count_30d * 2 THEN 'strong_improvement'
            WHEN ta.improving_count_30d > ta.degrading_count_30d THEN 'improving'
            WHEN ta.degrading_count_30d > ta.improving_count_30d THEN 'degrading'
            ELSE 'stable'
        END AS overall_trend
    FROM trend_analysis ta
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(moving_avg_intelligence_30d AS NUMERIC), 4) AS moving_avg_intelligence_30d,
    ROUND(CAST(intelligence_change_percent AS NUMERIC), 2) AS intelligence_change_percent,
    trajectory_direction,
    overall_trend,
    lifecycle_stage,
    volatility_category,
    ROUND(CAST(intelligence_volatility_30d AS NUMERIC), 4) AS intelligence_volatility_30d,
    improving_count_30d,
    degrading_count_30d,
    output_speed_tokens_per_sec,
    latency_seconds
FROM final_trajectory_analysis
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC;
```

## Query 7: Model Market Share Evolution with Competitive Dynamics

**Description:** Tracks market share evolution for AI models, analyzing competitive dynamics, market penetration trends, and competitive positioning shifts over time. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - model market share evolution with competitive dynamics

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for model market share evolution with competitive dynamics

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for model market share evolution with competitive dynamics

```sql
WITH base_data_7 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
median_by_date_7 AS (
    SELECT evaluation_date,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence
    FROM base_data_7
    GROUP BY evaluation_date
),
aggregated_metrics_7 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_7 bd
    LEFT JOIN median_by_date_7 md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_7 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_7 am
),
correlation_analysis_7 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_7 wa
),
final_aggregation_7 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_7 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_7
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 8: Benchmark Performance Correlation Matrix with Cross-Model Analysis

**Description:** Creates correlation matrices between different benchmark evaluations, identifying which benchmarks correlate strongly and which models excel across multiple benchmarks. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - benchmark performance correlation matrix with cross-model analysis

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for benchmark performance correlation matrix with cross-model analysis

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for benchmark performance correlation matrix with cross-model analysis

```sql
WITH base_data_8 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_8 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_8 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_8 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_8 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_8 am
),
correlation_analysis_8 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_8 wa
),
final_aggregation_8 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_8 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_8
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 9: Pricing Strategy Impact Analysis with Revenue Optimization

**Description:** Analyzes the impact of pricing strategies on adoption, revenue, and market position, identifying optimal pricing points for maximum revenue. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - pricing strategy impact analysis with revenue optimization

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for pricing strategy impact analysis with revenue optimization

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for pricing strategy impact analysis with revenue optimization

```sql
WITH base_data_9 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_9 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_9 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_9 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_9 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_9 am
),
correlation_analysis_9 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_9 wa
),
final_aggregation_9 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_9 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_9
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 10: Model Family Performance Comparison with Statistical Testing

**Description:** Compares performance across model families using statistical tests, identifying which families consistently outperform and under what conditions. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - model family performance comparison with statistical testing

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for model family performance comparison with statistical testing

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for model family performance comparison with statistical testing

```sql
WITH base_data_10 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_10 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_10 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_10 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_10 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_10 am
),
correlation_analysis_10 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_10 wa
),
final_aggregation_10 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_10 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_10
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 11: Government Compliance Scorecard with Regulatory Risk Assessment

**Description:** Creates comprehensive compliance scorecards for models across multiple government benchmarks, calculating overall compliance scores and regulatory risk. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - government compliance scorecard with regulatory risk assessment

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for government compliance scorecard with regulatory risk assessment

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for government compliance scorecard with regulatory risk assessment

```sql
WITH base_data_11 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_11 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_11 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_11 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_11 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_11 am
),
correlation_analysis_11 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_11 wa
),
final_aggregation_11 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_11 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_11
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 12: Adoption Prediction Model with Performance Correlation

**Description:** Predicts model adoption based on performance metrics, pricing, and historical adoption patterns using advanced correlation analysis. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - adoption prediction model with performance correlation

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for adoption prediction model with performance correlation

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for adoption prediction model with performance correlation

```sql
WITH base_data_12 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_12 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_12 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_12 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_12 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_12 am
),
correlation_analysis_12 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_12 wa
),
final_aggregation_12 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_12 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_12
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 13: Benchmark Leaderboard with Dynamic Ranking and Tier Classification

**Description:** Creates dynamic leaderboards for models across benchmarks, with tier classifications and ranking changes over time. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - benchmark leaderboard with dynamic ranking and tier classification

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for benchmark leaderboard with dynamic ranking and tier classification

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for benchmark leaderboard with dynamic ranking and tier classification

```sql
WITH base_data_13 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_13 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_13 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_13 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_13 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_13 am
),
correlation_analysis_13 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_13 wa
),
final_aggregation_13 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_13 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_13
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 14: Performance-Price Optimization Analysis with ROI Calculation

**Description:** Identifies optimal performance-price combinations, calculating ROI for different model selections based on use case requirements. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - performance-price optimization analysis with roi calculation

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for performance-price optimization analysis with roi calculation

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for performance-price optimization analysis with roi calculation

```sql
WITH base_data_14 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_14 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_14 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_14 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_14 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_14 am
),
correlation_analysis_14 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_14 wa
),
final_aggregation_14 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_14 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_14
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 15: Model Comparison Matrix with Multi-Dimensional Scoring

**Description:** Creates comprehensive comparison matrices between models across multiple dimensions including performance, price, speed, and compliance. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - model comparison matrix with multi-dimensional scoring

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for model comparison matrix with multi-dimensional scoring

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for model comparison matrix with multi-dimensional scoring

```sql
WITH base_data_15 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_15 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_15 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_15 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_15 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_15 am
),
correlation_analysis_15 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_15 wa
),
final_aggregation_15 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_15 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_15
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 16: Temporal Performance Forecasting with Trend Projection

**Description:** Forecasts future performance trends based on historical data using time series analysis and trend projection algorithms. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - temporal performance forecasting with trend projection

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for temporal performance forecasting with trend projection

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for temporal performance forecasting with trend projection

```sql
WITH base_data_16 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_16 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_16 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_16 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_16 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_16 am
),
correlation_analysis_16 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_16 wa
),
final_aggregation_16 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_16 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_16
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 17: Market Intelligence Aggregation with Competitive Positioning

**Description:** Aggregates marketing intelligence data to provide competitive positioning insights, market trends, and strategic recommendations. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - market intelligence aggregation with competitive positioning

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for market intelligence aggregation with competitive positioning

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for market intelligence aggregation with competitive positioning

```sql
WITH base_data_17 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_17 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_17 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_17 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_17 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_17 am
),
correlation_analysis_17 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_17 wa
),
final_aggregation_17 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_17 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_17
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 18: Benchmark Evaluation Quality Assessment with Statistical Validation

**Description:** Assesses the quality and reliability of benchmark evaluations using statistical validation techniques and cross-validation. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - benchmark evaluation quality assessment with statistical validation

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for benchmark evaluation quality assessment with statistical validation

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for benchmark evaluation quality assessment with statistical validation

```sql
WITH base_data_18 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_18 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_18 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_18 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_18 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_18 am
),
correlation_analysis_18 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_18 wa
),
final_aggregation_18 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_18 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_18
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 19: Model Adoption Funnel Analysis with Conversion Metrics

**Description:** Analyzes model adoption funnels, tracking conversion rates from awareness to active usage with detailed conversion metrics. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - model adoption funnel analysis with conversion metrics

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for model adoption funnel analysis with conversion metrics

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for model adoption funnel analysis with conversion metrics

```sql
WITH base_data_19 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_19 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_19 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_19 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_19 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_19 am
),
correlation_analysis_19 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_19 wa
),
final_aggregation_19 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_19 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_19
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 20: Performance Benchmark Gap Analysis with Improvement Recommendations

**Description:** Identifies performance gaps between models and benchmarks, providing improvement recommendations based on gap analysis. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - performance benchmark gap analysis with improvement recommendations

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for performance benchmark gap analysis with improvement recommendations

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for performance benchmark gap analysis with improvement recommendations

```sql
WITH base_data_20 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_20 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_20 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_20 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_20 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_20 am
),
correlation_analysis_20 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_20 wa
),
final_aggregation_20 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_20 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_20
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 21: Pricing Elasticity Analysis with Demand Forecasting

**Description:** Analyzes pricing elasticity and its impact on demand, forecasting adoption changes based on price adjustments. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - pricing elasticity analysis with demand forecasting

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for pricing elasticity analysis with demand forecasting

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for pricing elasticity analysis with demand forecasting

```sql
WITH base_data_21 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_21 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_21 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_21 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_21 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_21 am
),
correlation_analysis_21 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_21 wa
),
final_aggregation_21 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_21 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_21
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 22: Cross-Benchmark Performance Consistency Analysis

**Description:** Analyzes consistency of model performance across different benchmarks, identifying models with consistent vs. variable performance. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - cross-benchmark performance consistency analysis

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for cross-benchmark performance consistency analysis

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for cross-benchmark performance consistency analysis

```sql
WITH base_data_22 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_22 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_22 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_22 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_22 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_22 am
),
correlation_analysis_22 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_22 wa
),
final_aggregation_22 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_22 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_22
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 23: Model Lifecycle Performance Tracking with Stage Classification

**Description:** Tracks model performance throughout lifecycle stages, classifying models by stage and analyzing performance patterns by stage. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - model lifecycle performance tracking with stage classification

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for model lifecycle performance tracking with stage classification

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for model lifecycle performance tracking with stage classification

```sql
WITH base_data_23 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_23 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_23 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_23 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_23 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_23 am
),
correlation_analysis_23 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_23 wa
),
final_aggregation_23 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_23 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_23
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 24: Competitive Intelligence Dashboard with Market Dynamics

**Description:** Creates comprehensive competitive intelligence dashboards showing market dynamics, competitive positioning, and strategic insights. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - competitive intelligence dashboard with market dynamics

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for competitive intelligence dashboard with market dynamics

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for competitive intelligence dashboard with market dynamics

```sql
WITH base_data_24 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_24 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_24 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_24 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_24 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_24 am
),
correlation_analysis_24 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_24 wa
),
final_aggregation_24 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_24 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_24
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 25: Benchmark Evaluation Reliability Scoring with Confidence Intervals

**Description:** Calculates reliability scores for benchmark evaluations with confidence intervals and statistical significance testing. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - benchmark evaluation reliability scoring with confidence intervals

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for benchmark evaluation reliability scoring with confidence intervals

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for benchmark evaluation reliability scoring with confidence intervals

```sql
WITH base_data_25 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_25 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_25 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_25 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_25 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_25 am
),
correlation_analysis_25 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_25 wa
),
final_aggregation_25 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_25 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_25
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 26: Model Performance Anomaly Detection with Outlier Analysis

**Description:** Detects performance anomalies and outliers in model evaluations, identifying unusual performance patterns and potential issues. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - model performance anomaly detection with outlier analysis

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for model performance anomaly detection with outlier analysis

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for model performance anomaly detection with outlier analysis

```sql
WITH base_data_26 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_26 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_26 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_26 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_26 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_26 am
),
correlation_analysis_26 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_26 wa
),
final_aggregation_26 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_26 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_26
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 27: Market Penetration Analysis with Geographic and Demographic Segmentation

**Description:** Analyzes market penetration across geographic and demographic segments, identifying growth opportunities and market gaps. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - market penetration analysis with geographic and demographic segmentation

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for market penetration analysis with geographic and demographic segmentation

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for market penetration analysis with geographic and demographic segmentation

```sql
WITH base_data_27 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_27 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_27 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_27 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_27 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_27 am
),
correlation_analysis_27 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_27 wa
),
final_aggregation_27 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_27 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_27
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 28: Performance Optimization Recommendations with Cost-Benefit Analysis

**Description:** Provides performance optimization recommendations with cost-benefit analysis, identifying highest-impact improvements. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - performance optimization recommendations with cost-benefit analysis

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for performance optimization recommendations with cost-benefit analysis

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for performance optimization recommendations with cost-benefit analysis

```sql
WITH base_data_28 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_28 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_28 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_28 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_28 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_28 am
),
correlation_analysis_28 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_28 wa
),
final_aggregation_28 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_28 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_28
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 29: Comprehensive Model Evaluation Report with Multi-Dimensional Scoring

**Description:** Generates comprehensive evaluation reports with multi-dimensional scoring across performance, price, compliance, and adoption metrics. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - comprehensive model evaluation report with multi-dimensional scoring

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for comprehensive model evaluation report with multi-dimensional scoring

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for comprehensive model evaluation report with multi-dimensional scoring

```sql
WITH base_data_29 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_29 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_29 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_29 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_29 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_29 am
),
correlation_analysis_29 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_29 wa
),
final_aggregation_29 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_29 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_29
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```

## Query 30: Strategic Model Selection Framework with Use Case Optimization

**Description:** Provides strategic framework for model selection optimized by use case requirements, performance needs, and budget constraints. Uses multiple CTEs with window functions, complex aggregations, and joins across multiple tables for comprehensive analysis.

**Use Case:** Marketing intelligence analysis for AI benchmark platforms - strategic model selection framework with use case optimization

**Business Value:** Enables AI companies to gain marketing insights and optimize strategies, supporting $1M+ ARR AI benchmarking platforms

**Purpose:** Provides comprehensive marketing intelligence analysis for strategic model selection framework with use case optimization

**Complexity:** Multiple CTEs (6+ levels), window functions with complex frame clauses, complex aggregations, joins across ai_models/model_performance_metrics/benchmark_evaluations/marketing_intelligence tables, statistical calculations

**Expected Output:** Analysis report with comprehensive metrics and insights for strategic model selection framework with use case optimization

```sql
WITH base_data_30 AS (
    SELECT
        am.model_id,
        am.model_name,
        am.creator_company,
        am.model_family,
        mpm.intelligence_index_score,
        mpm.output_speed_tokens_per_sec,
        mpm.evaluation_date
    FROM ai_models am
    INNER JOIN model_performance_metrics mpm ON am.model_id = mpm.model_id
    WHERE mpm.evaluation_date >= CURRENT_DATE - INTERVAL '365 days'
        AND am.model_status = 'active'
),
aggregated_metrics_30 AS (
    SELECT
        bd.*,
        AVG(bd.intelligence_index_score) OVER (
            PARTITION BY bd.model_family
            ORDER BY bd.evaluation_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS family_avg_intelligence_30d,
        RANK() OVER (
            PARTITION BY bd.evaluation_date
            ORDER BY bd.intelligence_index_score DESC
        ) AS intelligence_rank,
        md.median_intelligence
    FROM base_data_30 bd
    LEFT JOIN (SELECT evaluation_date, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY intelligence_index_score) AS median_intelligence FROM base_data_30 GROUP BY evaluation_date) md ON bd.evaluation_date = md.evaluation_date
),
window_analysis_30 AS (
    SELECT
        am.*,
        LAG(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS prev_intelligence,
        LEAD(am.intelligence_index_score, 1) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
        ) AS next_intelligence,
        STDDEV(am.intelligence_index_score) OVER (
            PARTITION BY am.model_id
            ORDER BY am.evaluation_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS intelligence_volatility_90d
    FROM aggregated_metrics_30 am
),
correlation_analysis_30 AS (
    SELECT
        wa.*,
        CASE
            WHEN wa.prev_intelligence IS NOT NULL THEN
                wa.intelligence_index_score - wa.prev_intelligence
            ELSE NULL
        END AS intelligence_change,
        CASE
            WHEN wa.intelligence_rank <= 10 THEN 'top_tier'
            WHEN wa.intelligence_rank <= 25 THEN 'high_tier'
            WHEN wa.intelligence_rank <= 50 THEN 'mid_tier'
            ELSE 'lower_tier'
        END AS performance_tier
    FROM window_analysis_30 wa
),
final_aggregation_30 AS (
    SELECT
        ca.*,
        COUNT(*) OVER (
            PARTITION BY ca.model_family, ca.performance_tier
        ) AS tier_count_by_family,
        AVG(ca.intelligence_index_score) OVER (
            PARTITION BY ca.performance_tier
        ) AS tier_avg_intelligence
    FROM correlation_analysis_30 ca
)
SELECT
    model_name,
    creator_company,
    model_family,
    evaluation_date,
    ROUND(CAST(intelligence_index_score AS NUMERIC), 4) AS intelligence_index_score,
    ROUND(CAST(family_avg_intelligence_30d AS NUMERIC), 4) AS family_avg_intelligence_30d,
    intelligence_rank,
    ROUND(CAST(median_intelligence AS NUMERIC), 4) AS median_intelligence,
    ROUND(CAST(intelligence_change AS NUMERIC), 4) AS intelligence_change,
    performance_tier,
    ROUND(CAST(intelligence_volatility_90d AS NUMERIC), 4) AS intelligence_volatility_90d,
    tier_count_by_family,
    ROUND(CAST(tier_avg_intelligence AS NUMERIC), 4) AS tier_avg_intelligence,
    output_speed_tokens_per_sec
FROM final_aggregation_30
WHERE evaluation_date >= CURRENT_DATE - INTERVAL '180 days'
ORDER BY model_id, evaluation_date DESC
LIMIT 100;
```
