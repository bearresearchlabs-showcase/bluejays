---
title: AI Benchmark Marketing Database — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-13
---

# AI Benchmark Marketing Database — Documentation

**Database:** db-13  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_13
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_13 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load production data from data_large.sql when available (>= 1GB). No sample data.

```bash
psql -U postgres -d db_13 -f data_large.sql
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

- `ai_models` — (see data dictionary)
- `model_performance_metrics` — (see data dictionary)
- `benchmark_evaluations` — (see data dictionary)
- `model_comparisons` — (see data dictionary)
- `marketing_intelligence` — (see data dictionary)
- `government_benchmark_data` — (see data dictionary)
- `model_adoption_metrics` — (see data dictionary)
- `model_pricing_history` — (see data dictionary)
- `model_performance_history` — (see data dictionary)
- `data_sources` — (see data dictionary)
- `pipeline_metadata` — (see data dictionary)

---

## Data Dictionary

### `ai_models`

- `model_id` VARCHAR(255) PRIMARY KEY
- `model_name` VARCHAR(500) NOT NULL
- `model_slug` VARCHAR(500) UNIQUE — URL-friendly identifier
- `creator_company` VARCHAR(255) NOT NULL — OpenAI, Anthropic, Google, Meta, etc.
- `creator_type` VARCHAR(50)  — 'open_source', 'proprietary', 'hybrid'
- `license_type` VARCHAR(50)  — 'open', 'proprietary', 'commercial_restricted'
- `model_family` VARCHAR(255)  — GPT, Claude, Gemini, Llama, etc.
- `model_version` VARCHAR(100)  — Version number or identifier
- `release_date` DATE 
- `context_window` INTEGER  — Maximum context window in tokens
- `total_parameters_billions` NUMERIC(10, 2)  — Total parameters (for open weights)
- `active_parameters_billions` NUMERIC(10, 2)  — Active parameters at inference (MoE models)
- `model_type` VARCHAR(50)  — 'dense', 'moe', 'reasoning', 'non_reasoning'
- `architecture_type` VARCHAR(100)  — Transformer architecture details
- `training_data_size_tokens` NUMERIC(20, 0)  — Training data size
- `training_compute_pflops` NUMERIC(20, 2)  — Training compute in petaFLOPs
- `is_reasoning_model` BOOLEAN 
- `is_multimodal` BOOLEAN 
- `supports_streaming` BOOLEAN 
- `supports_function_calling` BOOLEAN 
- `supports_vision` BOOLEAN 
- `supports_audio` BOOLEAN 
- `model_status` VARCHAR(50)  — 'active', 'deprecated', 'preview', 'experimental'
- `data_source` VARCHAR(100) 
- `source_url` VARCHAR(1000) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 
- `metadata_json` TEXT  — Additional JSON metadata

### `model_performance_metrics`

- `metric_id` VARCHAR(255) PRIMARY KEY
- `model_id` VARCHAR(255) NOT NULL
- `evaluation_date` DATE NOT NULL
- `intelligence_index_score` NUMERIC(10, 4)  — Artificial Analysis Intelligence Index v4.0
- `intelligence_index_percentile` NUMERIC(5, 2)  — Percentile ranking
- `coding_index_score` NUMERIC(10, 4)  — Coding-specific performance
- `agentic_index_score` NUMERIC(10, 4)  — Agentic capabilities score
- `output_speed_tokens_per_sec` NUMERIC(10, 2)  — Output tokens per second
- `latency_seconds` NUMERIC(10, 4)  — Time to first token
- `end_to_end_response_time_500tokens` NUMERIC(10, 4)  — Seconds to output 500 tokens
- `input_price_per_million_tokens` NUMERIC(10, 4)  — USD per 1M input tokens
- `output_price_per_million_tokens` NUMERIC(10, 4)  — USD per 1M output tokens
- `blended_price_per_million_tokens` NUMERIC(10, 4)  — Blended price (3:1 input:output ratio)
- `reasoning_price_per_million_tokens` NUMERIC(10, 4)  — Reasoning tokens price (if applicable)
- `openness_index` NUMERIC(5, 2)  — Openness Index (0-100)
- `omniscience_index` NUMERIC(10, 4)  — AA-Omniscience Index (-100 to 100)
- `omniscience_accuracy` NUMERIC(5, 2)  — Accuracy percentage
- `omniscience_hallucination_rate` NUMERIC(5, 2)  — Hallucination rate percentage
- `evaluation_version` VARCHAR(50)  — Evaluation framework version
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `benchmark_evaluations`

- `evaluation_id` VARCHAR(255) PRIMARY KEY
- `model_id` VARCHAR(255) NOT NULL
- `benchmark_name` VARCHAR(255) NOT NULL — 'GDPval-AA', 'Terminal-Bench Hard', 'SciCode', etc.
- `benchmark_category` VARCHAR(100)  — 'intelligence', 'coding', 'reasoning', 'knowledge', 'agentic'
- `evaluation_date` DATE NOT NULL
- `score` NUMERIC(10, 4)  — Raw score
- `normalized_score` NUMERIC(10, 4)  — Normalized score (0-100 or percentile)
- `percentile_rank` NUMERIC(5, 2)  — Percentile ranking
- `total_tests` INTEGER  — Total number of test cases
- `passed_tests` INTEGER  — Number of passed tests
- `failed_tests` INTEGER  — Number of failed tests
- `accuracy_percentage` NUMERIC(5, 2)  — Accuracy percentage
- `evaluation_methodology` VARCHAR(500)  — Description of evaluation methodology
- `benchmark_version` VARCHAR(50)  — Benchmark version
- `evaluation_metadata` TEXT  — JSON metadata with detailed results
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `model_comparisons`

- `comparison_id` VARCHAR(255) PRIMARY KEY
- `model_id_1` VARCHAR(255) NOT NULL
- `model_id_2` VARCHAR(255) NOT NULL
- `comparison_date` DATE NOT NULL
- `comparison_dimension` VARCHAR(100)  — 'intelligence', 'speed', 'price', 'overall'
- `model_1_score` NUMERIC(10, 4) 
- `model_2_score` NUMERIC(10, 4) 
- `winner_model_id` VARCHAR(255)  — Model with better score
- `score_difference` NUMERIC(10, 4)  — Absolute difference
- `score_difference_percent` NUMERIC(5, 2)  — Percentage difference
- `comparison_context` VARCHAR(500)  — Context of comparison
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 

### `marketing_intelligence`

- `intelligence_id` VARCHAR(255) PRIMARY KEY
- `analysis_date` DATE NOT NULL
- `analysis_type` VARCHAR(100)  — 'market_share', 'trend_analysis', 'competitive_positioning', 'price_analysis'
- `creator_company` VARCHAR(255)  — Company being analyzed (nullable for industry-wide analysis)
- `model_family` VARCHAR(255)  — Model family being analyzed
- `market_segment` VARCHAR(100)  — 'high_intelligence', 'cost_effective', 'fast', 'open_source', etc.
- `market_share_percentage` NUMERIC(5, 2)  — Market share percentage
- `market_position` VARCHAR(50)  — 'leader', 'challenger', 'follower', 'niche'
- `average_intelligence_score` NUMERIC(10, 4)  — Average intelligence score
- `average_price_per_million_tokens` NUMERIC(10, 4)  — Average price
- `average_speed_tokens_per_sec` NUMERIC(10, 2)  — Average speed
- `model_count` INTEGER  — Number of models in segment
- `growth_rate_percent` NUMERIC(5, 2)  — Growth rate percentage
- `trend_direction` VARCHAR(50)  — 'increasing', 'decreasing', 'stable'
- `competitive_advantage` VARCHAR(500)  — Key competitive advantages
- `market_insights` TEXT  — Detailed insights JSON
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `government_benchmark_data`

- `gov_benchmark_id` VARCHAR(255) PRIMARY KEY
- `source_agency` VARCHAR(100) NOT NULL — 'NIST', 'NSF', 'DARPA', 'NIST_AI_RMF', etc.
- `benchmark_name` VARCHAR(255) NOT NULL
- `benchmark_category` VARCHAR(100)  — 'safety', 'robustness', 'bias', 'efficiency', 'accuracy'
- `model_id` VARCHAR(255)  — Link to ai_models if available
- `model_name` VARCHAR(500)  — Model name if not in ai_models table
- `evaluation_date` DATE NOT NULL
- `test_suite_name` VARCHAR(255)  — Specific test suite
- `score` NUMERIC(10, 4)  — Benchmark score
- `score_type` VARCHAR(50)  — 'accuracy', 'f1', 'bleu', 'rouge', 'pass_rate', etc.
- `test_count` INTEGER  — Number of tests
- `passed_count` INTEGER  — Number of passed tests
- `compliance_level` VARCHAR(50)  — 'compliant', 'partially_compliant', 'non_compliant'
- `safety_score` NUMERIC(5, 2)  — Safety score (if applicable)
- `robustness_score` NUMERIC(5, 2)  — Robustness score (if applicable)
- `bias_score` NUMERIC(5, 2)  — Bias score (if applicable)
- `efficiency_score` NUMERIC(5, 2)  — Efficiency score (if applicable)
- `benchmark_metadata` TEXT  — JSON metadata
- `source_url` VARCHAR(1000) 
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `model_adoption_metrics`

- `adoption_id` VARCHAR(255) PRIMARY KEY
- `model_id` VARCHAR(255) NOT NULL
- `metric_date` DATE NOT NULL
- `api_calls_millions` NUMERIC(10, 2)  — Estimated API calls in millions
- `active_users_thousands` INTEGER  — Estimated active users in thousands
- `market_penetration_percent` NUMERIC(5, 2)  — Market penetration percentage
- `developer_sentiment_score` NUMERIC(5, 2)  — Sentiment score (-100 to 100)
- `github_stars` INTEGER  — GitHub stars (for open source models)
- `github_forks` INTEGER  — GitHub forks
- `research_citations` INTEGER  — Research paper citations
- `industry_adoption_score` NUMERIC(5, 2)  — Industry adoption score (0-100)
- `enterprise_adoption_percent` NUMERIC(5, 2)  — Enterprise adoption percentage
- `adoption_trend` VARCHAR(50)  — 'growing', 'stable', 'declining'
- `adoption_metadata` TEXT  — JSON metadata
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `model_pricing_history`

- `pricing_id` VARCHAR(255) PRIMARY KEY
- `model_id` VARCHAR(255) NOT NULL
- `pricing_date` DATE NOT NULL
- `input_price_per_million_tokens` NUMERIC(10, 4) 
- `output_price_per_million_tokens` NUMERIC(10, 4) 
- `blended_price_per_million_tokens` NUMERIC(10, 4) 
- `reasoning_price_per_million_tokens` NUMERIC(10, 4) 
- `cached_price_per_million_tokens` NUMERIC(10, 4)  — Cached pricing (if applicable)
- `image_input_price_per_million_tokens` NUMERIC(10, 4)  — Image input pricing
- `price_change_percent` NUMERIC(5, 2)  — Price change percentage from previous period
- `pricing_tier` VARCHAR(50)  — 'free', 'tier_1', 'tier_2', 'enterprise', etc.
- `pricing_region` VARCHAR(50)  — Pricing region
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 

### `model_performance_history`

- `performance_history_id` VARCHAR(255) PRIMARY KEY
- `model_id` VARCHAR(255) NOT NULL
- `performance_date` DATE NOT NULL
- `intelligence_index_score` NUMERIC(10, 4) 
- `output_speed_tokens_per_sec` NUMERIC(10, 2) 
- `latency_seconds` NUMERIC(10, 4) 
- `performance_change_percent` NUMERIC(5, 2)  — Performance change from previous period
- `benchmark_scores_json` TEXT  — JSON with all benchmark scores
- `data_source` VARCHAR(100) 
- `created_at` TIMESTAMP 

### `data_sources`

- `source_id` VARCHAR(255) PRIMARY KEY
- `source_name` VARCHAR(255) UNIQUE, NOT NULL
- `source_type` VARCHAR(50)  — 'api', 'scraper', 'government', 'research', 'aggregated'
- `source_category` VARCHAR(100)  — 'benchmark', 'pricing', 'adoption', 'government', 'research'
- `api_endpoint` VARCHAR(1000) 
- `api_documentation_url` VARCHAR(1000) 
- `rate_limit_per_hour` INTEGER 
- `rate_limit_per_day` INTEGER 
- `authentication_type` VARCHAR(50)  — 'none', 'api_key', 'oauth', 'bearer_token'
- `last_sync_at` TIMESTAMP 
- `sync_frequency` VARCHAR(50)  — 'hourly', 'daily', 'weekly', 'monthly', 'manual'
- `data_quality_score` NUMERIC(5, 2)  — Data quality score (0-100)
- `is_active` BOOLEAN 
- `source_metadata` TEXT  — JSON metadata
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `pipeline_metadata`

- `pipeline_id` VARCHAR(255) PRIMARY KEY
- `source_id` VARCHAR(255) NOT NULL
- `extraction_date` TIMESTAMP NOT NULL
- `pipeline_type` VARCHAR(50)  — 'extract', 'transform', 'load', 'full', 'incremental'
- `records_processed` INTEGER 
- `records_successful` INTEGER 
- `records_failed` INTEGER 
- `processing_duration_seconds` INTEGER 
- `error_log` TEXT 
- `status` VARCHAR(50)  — 'running', 'success', 'failed', 'partial'
- `start_time` TIMESTAMP NOT NULL
- `end_time` TIMESTAMP 
- `data_volume_bytes` BIGINT  — Data volume processed in bytes

---

*Generated by documentation workflow. MDX-compatible markdown.*
