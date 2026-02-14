# Data Dictionary - db-13

## Overview

**Database Name:** AI Benchmark Marketing Database  
**Schema Name:** DB13  
**Created:** 2026-02-04

This data dictionary provides detailed descriptions of all columns in the database schema, including data types, constraints, business context, and usage notes.

---

## Table: ai_models

Core AI model catalog with metadata, creator information, and technical specifications.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `model_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each AI model | Primary key used in all foreign key relationships |
| `model_name` | VARCHAR(500) | NOT NULL | Full name of the AI model (e.g., "GPT-4", "Claude 3 Opus") | Human-readable model name for display and reporting |
| `model_slug` | VARCHAR(500) | UNIQUE | URL-friendly identifier for the model | Used in URLs and API endpoints (e.g., "gpt-4", "claude-3-opus") |
| `creator_company` | VARCHAR(255) | NOT NULL | Company that created the model | Creator organization (OpenAI, Anthropic, Google, Meta, etc.) - used for competitive analysis |
| `creator_type` | VARCHAR(50) | NULL | Type of creator organization | Values: 'open_source', 'proprietary', 'hybrid' - indicates model licensing approach |
| `license_type` | VARCHAR(50) | NULL | License type of the model | Values: 'open', 'proprietary', 'commercial_restricted' - determines usage rights |
| `model_family` | VARCHAR(255) | NULL | Model family or series | Model family grouping (GPT, Claude, Gemini, Llama, etc.) - used for family-level analysis |
| `model_version` | VARCHAR(100) | NULL | Version number or identifier | Model version (e.g., "4", "3.5", "2.0") - tracks model evolution |
| `release_date` | DATE | NULL | Date when model was released | Release date for temporal analysis and version tracking |
| `context_window` | INTEGER | NULL | Maximum context window in tokens | Maximum input tokens supported - critical for use case matching |
| `total_parameters_billions` | NUMERIC(10, 2) | NULL | Total parameters in billions | Total model parameters (for open weights models) - indicates model scale |
| `active_parameters_billions` | NUMERIC(10, 2) | NULL | Active parameters at inference in billions | Active parameters for MoE (Mixture of Experts) models - actual compute requirements |
| `model_type` | VARCHAR(50) | NULL | Model architecture type | Values: 'dense', 'moe', 'reasoning', 'non_reasoning' - architecture classification |
| `architecture_type` | VARCHAR(100) | NULL | Transformer architecture details | Detailed architecture information (e.g., "Transformer", "MoE-16") |
| `training_data_size_tokens` | NUMERIC(20, 0) | NULL | Training data size in tokens | Training dataset size - indicates training scale |
| `training_compute_pflops` | NUMERIC(20, 2) | NULL | Training compute in petaFLOPs | Training compute requirements - cost and resource indicators |
| `is_reasoning_model` | BOOLEAN | DEFAULT FALSE | Flag indicating if model supports reasoning | TRUE for models with reasoning capabilities (e.g., o1, DeepSeek-R1) |
| `is_multimodal` | BOOLEAN | DEFAULT FALSE | Flag indicating if model supports multiple modalities | TRUE for models supporting text, images, audio, etc. |
| `supports_streaming` | BOOLEAN | DEFAULT TRUE | Flag indicating if model supports streaming responses | TRUE if model supports streaming output - affects user experience |
| `supports_function_calling` | BOOLEAN | DEFAULT FALSE | Flag indicating if model supports function calling | TRUE if model supports tool/function calling - agentic capabilities |
| `supports_vision` | BOOLEAN | DEFAULT FALSE | Flag indicating if model supports vision | TRUE if model can process images - multimodal capability |
| `supports_audio` | BOOLEAN | DEFAULT FALSE | Flag indicating if model supports audio | TRUE if model can process audio - multimodal capability |
| `model_status` | VARCHAR(50) | DEFAULT 'active' | Current status of the model | Values: 'active', 'deprecated', 'preview', 'experimental' - lifecycle status |
| `data_source` | VARCHAR(100) | DEFAULT 'ARTIFICIAL_ANALYSIS' | Source of the model data | Data source identifier for lineage tracking |
| `source_url` | VARCHAR(1000) | NULL | URL to model source or documentation | Link to model documentation or source page |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp for record creation |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was last updated | Audit timestamp for record updates |
| `metadata_json` | VARCHAR(16777216) | NULL | Additional JSON metadata | Flexible JSON storage for extended metadata and custom fields |

---

## Table: model_performance_metrics

Performance metrics from Artificial Analysis Intelligence Index and other benchmarks.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `metric_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each performance metric record | Primary key for performance metrics |
| `model_id` | VARCHAR(255) | NOT NULL, FK → ai_models | Reference to AI model | Foreign key linking to ai_models table |
| `evaluation_date` | DATE | NOT NULL | Date of performance evaluation | Evaluation date for temporal analysis |
| `intelligence_index_score` | NUMERIC(10, 4) | NULL | Artificial Analysis Intelligence Index v4.0 score | Primary performance metric - overall intelligence score |
| `intelligence_index_percentile` | NUMERIC(5, 2) | NULL | Percentile ranking of intelligence score | Percentile ranking (0-100) for competitive positioning |
| `coding_index_score` | NUMERIC(10, 4) | NULL | Coding-specific performance score | Coding capability score - important for developer use cases |
| `agentic_index_score` | NUMERIC(10, 4) | NULL | Agentic capabilities score | Agentic/AI agent performance score - autonomous task execution |
| `output_speed_tokens_per_sec` | NUMERIC(10, 2) | NULL | Output tokens per second | Speed metric - tokens generated per second |
| `latency_seconds` | NUMERIC(10, 4) | NULL | Time to first token in seconds | Latency metric - time until first token output |
| `end_to_end_response_time_500tokens` | NUMERIC(10, 4) | NULL | Seconds to output 500 tokens | End-to-end response time for 500 tokens - user experience metric |
| `input_price_per_million_tokens` | NUMERIC(10, 4) | NULL | USD per 1M input tokens | Input pricing - cost per million input tokens |
| `output_price_per_million_tokens` | NUMERIC(10, 4) | NULL | USD per 1M output tokens | Output pricing - cost per million output tokens |
| `blended_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Blended price (3:1 input:output ratio) | Blended pricing - weighted average of input/output prices |
| `reasoning_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Reasoning tokens price (if applicable) | Reasoning-specific pricing for reasoning models |
| `openness_index` | NUMERIC(5, 2) | NULL | Openness Index (0-100) | Openness score - measures model openness and transparency |
| `omniscience_index` | NUMERIC(10, 4) | NULL | AA-Omniscience Index (-100 to 100) | Omniscience score - measures factual accuracy and knowledge |
| `omniscience_accuracy` | NUMERIC(5, 2) | NULL | Accuracy percentage | Accuracy percentage from omniscience evaluation |
| `omniscience_hallucination_rate` | NUMERIC(5, 2) | NULL | Hallucination rate percentage | Hallucination rate - lower is better |
| `evaluation_version` | VARCHAR(50) | NULL | Evaluation framework version | Version of evaluation framework used |
| `data_source` | VARCHAR(100) | DEFAULT 'ARTIFICIAL_ANALYSIS' | Source of the performance data | Data source identifier for lineage tracking |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was last updated | Audit timestamp |

---

## Table: benchmark_evaluations

Individual benchmark test results from various evaluations (GDPval-AA, Terminal-Bench, SciCode, etc.).

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `evaluation_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each benchmark evaluation | Primary key for benchmark evaluations |
| `model_id` | VARCHAR(255) | NOT NULL, FK → ai_models | Reference to AI model | Foreign key linking to ai_models table |
| `benchmark_name` | VARCHAR(255) | NOT NULL | Name of benchmark | Benchmark identifier (GDPval-AA, Terminal-Bench Hard, SciCode, etc.) |
| `benchmark_category` | VARCHAR(100) | NULL | Category of benchmark | Values: 'intelligence', 'coding', 'reasoning', 'knowledge', 'agentic' |
| `evaluation_date` | DATE | NOT NULL | Date of evaluation | Evaluation date for temporal analysis |
| `score` | NUMERIC(10, 4) | NULL | Raw benchmark score | Raw score from benchmark evaluation |
| `normalized_score` | NUMERIC(10, 4) | NULL | Normalized score (0-100 or percentile) | Normalized score for cross-benchmark comparison |
| `percentile_rank` | NUMERIC(5, 2) | NULL | Percentile ranking | Percentile rank (0-100) for competitive positioning |
| `total_tests` | INTEGER | NULL | Total number of test cases | Total tests in benchmark suite |
| `passed_tests` | INTEGER | NULL | Number of passed tests | Number of successful test cases |
| `failed_tests` | INTEGER | NULL | Number of failed tests | Number of failed test cases |
| `accuracy_percentage` | NUMERIC(5, 2) | NULL | Accuracy percentage | Accuracy percentage (passed_tests / total_tests * 100) |
| `evaluation_methodology` | VARCHAR(500) | NULL | Description of evaluation methodology | Methodology description for transparency |
| `benchmark_version` | VARCHAR(50) | NULL | Benchmark version | Version of benchmark used |
| `evaluation_metadata` | VARCHAR(16777216) | NULL | JSON metadata with detailed results | Detailed results in JSON format |
| `data_source` | VARCHAR(100) | DEFAULT 'ARTIFICIAL_ANALYSIS' | Source of the benchmark data | Data source identifier |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was last updated | Audit timestamp |

---

## Table: model_comparisons

Competitive analysis and model-to-model comparisons.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `comparison_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each comparison | Primary key for comparisons |
| `model_id_1` | VARCHAR(255) | NOT NULL, FK → ai_models | First model in comparison | Foreign key to first model |
| `model_id_2` | VARCHAR(255) | NOT NULL, FK → ai_models | Second model in comparison | Foreign key to second model |
| `comparison_date` | DATE | NOT NULL | Date of comparison | Comparison date for temporal analysis |
| `comparison_dimension` | VARCHAR(100) | NULL | Dimension of comparison | Values: 'intelligence', 'speed', 'price', 'overall' |
| `model_1_score` | NUMERIC(10, 4) | NULL | Score for first model | Performance score for model 1 |
| `model_2_score` | NUMERIC(10, 4) | NULL | Score for second model | Performance score for model 2 |
| `winner_model_id` | VARCHAR(255) | NULL, FK → ai_models | Model with better score | Foreign key to winning model |
| `score_difference` | NUMERIC(10, 4) | NULL | Absolute difference in scores | Absolute score difference (|model_1_score - model_2_score|) |
| `score_difference_percent` | NUMERIC(5, 2) | NULL | Percentage difference | Percentage difference in scores |
| `comparison_context` | VARCHAR(500) | NULL | Context of comparison | Additional context for comparison |
| `data_source` | VARCHAR(100) | DEFAULT 'ARTIFICIAL_ANALYSIS' | Source of the comparison data | Data source identifier |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |

---

## Table: marketing_intelligence

Aggregated marketing insights, trends, and market positioning.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `intelligence_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each intelligence record | Primary key for marketing intelligence |
| `analysis_date` | DATE | NOT NULL | Date of analysis | Analysis date for temporal tracking |
| `analysis_type` | VARCHAR(100) | NULL | Type of analysis | Values: 'market_share', 'trend_analysis', 'competitive_positioning', 'price_analysis' |
| `creator_company` | VARCHAR(255) | NULL | Company being analyzed | Company name (nullable for industry-wide analysis) |
| `model_family` | VARCHAR(255) | NULL | Model family being analyzed | Model family (GPT, Claude, etc.) |
| `market_segment` | VARCHAR(100) | NULL | Market segment | Values: 'high_intelligence', 'cost_effective', 'fast', 'open_source', etc. |
| `market_share_percentage` | NUMERIC(5, 2) | NULL | Market share percentage | Market share percentage (0-100) |
| `market_position` | VARCHAR(50) | NULL | Market position | Values: 'leader', 'challenger', 'follower', 'niche' |
| `average_intelligence_score` | NUMERIC(10, 4) | NULL | Average intelligence score | Average intelligence index score for segment |
| `average_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Average price per million tokens | Average pricing for segment |
| `average_speed_tokens_per_sec` | NUMERIC(10, 2) | NULL | Average speed in tokens per second | Average output speed for segment |
| `model_count` | INTEGER | NULL | Number of models in segment | Count of models in market segment |
| `growth_rate_percent` | NUMERIC(5, 2) | NULL | Growth rate percentage | Growth rate percentage (can be negative) |
| `trend_direction` | VARCHAR(50) | NULL | Trend direction | Values: 'increasing', 'decreasing', 'stable' |
| `competitive_advantage` | VARCHAR(500) | NULL | Key competitive advantages | Description of competitive advantages |
| `market_insights` | VARCHAR(16777216) | NULL | Detailed insights JSON | Detailed market insights in JSON format |
| `data_source` | VARCHAR(100) | DEFAULT 'CALCULATED' | Source of the intelligence data | Data source identifier (typically 'CALCULATED') |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was last updated | Audit timestamp |

---

## Table: government_benchmark_data

Benchmark data from NIST, NSF, DARPA, and other government sources.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `gov_benchmark_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each government benchmark record | Primary key for government benchmarks |
| `source_agency` | VARCHAR(100) | NOT NULL | Source agency | Values: 'NIST', 'NSF', 'DARPA', 'NIST_AI_RMF', etc. |
| `benchmark_name` | VARCHAR(255) | NOT NULL | Name of benchmark | Government benchmark name |
| `benchmark_category` | VARCHAR(100) | NULL | Category of benchmark | Values: 'safety', 'robustness', 'bias', 'efficiency', 'accuracy' |
| `model_id` | VARCHAR(255) | NULL, FK → ai_models | Reference to AI model | Foreign key (nullable if model not in ai_models) |
| `model_name` | VARCHAR(500) | NULL | Model name if not in ai_models | Model name for external models |
| `evaluation_date` | DATE | NOT NULL | Date of evaluation | Evaluation date |
| `test_suite_name` | VARCHAR(255) | NULL | Specific test suite | Test suite identifier |
| `score` | NUMERIC(10, 4) | NULL | Benchmark score | Raw benchmark score |
| `score_type` | VARCHAR(50) | NULL | Type of score | Values: 'accuracy', 'f1', 'bleu', 'rouge', 'pass_rate', etc. |
| `test_count` | INTEGER | NULL | Number of tests | Total number of tests |
| `passed_count` | INTEGER | NULL | Number of passed tests | Number of successful tests |
| `compliance_level` | VARCHAR(50) | NULL | Compliance level | Values: 'compliant', 'partially_compliant', 'non_compliant' |
| `safety_score` | NUMERIC(5, 2) | NULL | Safety score (if applicable) | Safety evaluation score (0-100) |
| `robustness_score` | NUMERIC(5, 2) | NULL | Robustness score (if applicable) | Robustness evaluation score (0-100) |
| `bias_score` | NUMERIC(5, 2) | NULL | Bias score (if applicable) | Bias evaluation score (0-100) |
| `efficiency_score` | NUMERIC(5, 2) | NULL | Efficiency score (if applicable) | Efficiency evaluation score (0-100) |
| `benchmark_metadata` | VARCHAR(16777216) | NULL | JSON metadata | Detailed benchmark results in JSON |
| `source_url` | VARCHAR(1000) | NULL | URL to benchmark source | Link to benchmark documentation |
| `data_source` | VARCHAR(100) | DEFAULT 'GOVERNMENT' | Source of the data | Data source identifier |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was last updated | Audit timestamp |

---

## Table: model_adoption_metrics

Usage and adoption metrics for marketing intelligence.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `adoption_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each adoption record | Primary key for adoption metrics |
| `model_id` | VARCHAR(255) | NOT NULL, FK → ai_models | Reference to AI model | Foreign key linking to ai_models |
| `metric_date` | DATE | NOT NULL | Date of metric | Metric date for temporal analysis |
| `api_calls_millions` | NUMERIC(10, 2) | NULL | Estimated API calls in millions | API usage volume indicator |
| `active_users_thousands` | INTEGER | NULL | Estimated active users in thousands | Active user count indicator |
| `market_penetration_percent` | NUMERIC(5, 2) | NULL | Market penetration percentage | Market penetration (0-100) |
| `developer_sentiment_score` | NUMERIC(5, 2) | NULL | Sentiment score (-100 to 100) | Developer sentiment (-100 negative, 100 positive) |
| `github_stars` | INTEGER | NULL | GitHub stars (for open source models) | GitHub popularity metric |
| `github_forks` | INTEGER | NULL | GitHub forks | GitHub engagement metric |
| `research_citations` | INTEGER | NULL | Research paper citations | Academic/research adoption indicator |
| `industry_adoption_score` | NUMERIC(5, 2) | NULL | Industry adoption score (0-100) | Industry adoption metric |
| `enterprise_adoption_percent` | NUMERIC(5, 2) | NULL | Enterprise adoption percentage | Enterprise market penetration |
| `adoption_trend` | VARCHAR(50) | NULL | Adoption trend | Values: 'growing', 'stable', 'declining' |
| `adoption_metadata` | VARCHAR(16777216) | NULL | JSON metadata | Additional adoption data in JSON |
| `data_source` | VARCHAR(100) | DEFAULT 'AGGREGATED' | Source of the adoption data | Data source identifier |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was last updated | Audit timestamp |

---

## Table: model_pricing_history

Historical pricing data for trend analysis.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `pricing_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each pricing record | Primary key for pricing history |
| `model_id` | VARCHAR(255) | NOT NULL, FK → ai_models | Reference to AI model | Foreign key linking to ai_models |
| `pricing_date` | DATE | NOT NULL | Date of pricing | Pricing date for temporal analysis |
| `input_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Input price per million tokens | Input token pricing in USD |
| `output_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Output price per million tokens | Output token pricing in USD |
| `blended_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Blended price | Blended pricing (weighted average) |
| `reasoning_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Reasoning tokens price | Reasoning-specific pricing |
| `cached_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Cached pricing (if applicable) | Cached token pricing |
| `image_input_price_per_million_tokens` | NUMERIC(10, 4) | NULL | Image input pricing | Image input token pricing |
| `price_change_percent` | NUMERIC(5, 2) | NULL | Price change percentage | Price change from previous period |
| `pricing_tier` | VARCHAR(50) | NULL | Pricing tier | Values: 'free', 'tier_1', 'tier_2', 'enterprise', etc. |
| `pricing_region` | VARCHAR(50) | DEFAULT 'US' | Pricing region | Geographic region for pricing |
| `data_source` | VARCHAR(100) | DEFAULT 'ARTIFICIAL_ANALYSIS' | Source of the pricing data | Data source identifier |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |

---

## Table: model_performance_history

Historical performance metrics for trend analysis.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `performance_history_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each performance history record | Primary key for performance history |
| `model_id` | VARCHAR(255) | NOT NULL, FK → ai_models | Reference to AI model | Foreign key linking to ai_models |
| `performance_date` | DATE | NOT NULL | Date of performance measurement | Performance date for temporal analysis |
| `intelligence_index_score` | NUMERIC(10, 4) | NULL | Intelligence index score | Historical intelligence index score |
| `output_speed_tokens_per_sec` | NUMERIC(10, 2) | NULL | Output speed in tokens per second | Historical output speed |
| `latency_seconds` | NUMERIC(10, 4) | NULL | Latency in seconds | Historical latency |
| `performance_change_percent` | NUMERIC(5, 2) | NULL | Performance change percentage | Performance change from previous period |
| `benchmark_scores_json` | VARCHAR(16777216) | NULL | JSON with all benchmark scores | Historical benchmark scores in JSON |
| `data_source` | VARCHAR(100) | DEFAULT 'ARTIFICIAL_ANALYSIS' | Source of the performance data | Data source identifier |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |

---

## Table: data_sources

Source tracking for data lineage and quality monitoring.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `source_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each data source | Primary key for data sources |
| `source_name` | VARCHAR(255) | NOT NULL, UNIQUE | Unique source name | Source identifier (e.g., 'ARTIFICIAL_ANALYSIS', 'NIST_API') |
| `source_type` | VARCHAR(50) | NULL | Type of source | Values: 'api', 'scraper', 'government', 'research', 'aggregated' |
| `source_category` | VARCHAR(100) | NULL | Category of source | Values: 'benchmark', 'pricing', 'adoption', 'government', 'research' |
| `api_endpoint` | VARCHAR(1000) | NULL | API endpoint URL | API endpoint for data extraction |
| `api_documentation_url` | VARCHAR(1000) | NULL | API documentation URL | Link to API documentation |
| `rate_limit_per_hour` | INTEGER | NULL | Rate limit per hour | API rate limit (requests per hour) |
| `rate_limit_per_day` | INTEGER | NULL | Rate limit per day | API rate limit (requests per day) |
| `authentication_type` | VARCHAR(50) | NULL | Authentication type | Values: 'none', 'api_key', 'oauth', 'bearer_token' |
| `last_sync_at` | TIMESTAMP_NTZ | NULL | Last synchronization timestamp | Last successful data sync timestamp |
| `sync_frequency` | VARCHAR(50) | NULL | Synchronization frequency | Values: 'hourly', 'daily', 'weekly', 'monthly', 'manual' |
| `data_quality_score` | NUMERIC(5, 2) | NULL | Data quality score (0-100) | Data quality metric (0-100, higher is better) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active status flag | TRUE if source is currently active |
| `source_metadata` | VARCHAR(16777216) | NULL | JSON metadata | Additional source metadata in JSON |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was created | Audit timestamp |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Timestamp when record was last updated | Audit timestamp |

---

## Table: pipeline_metadata

ETL pipeline execution tracking and error logging.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `pipeline_id` | VARCHAR(255) | PRIMARY KEY, NOT NULL | Unique identifier for each pipeline execution | Primary key for pipeline executions |
| `source_id` | VARCHAR(255) | NOT NULL, FK → data_sources | Reference to data source | Foreign key linking to data_sources |
| `extraction_date` | TIMESTAMP_NTZ | NOT NULL | Date/time of extraction | Pipeline execution timestamp |
| `pipeline_type` | VARCHAR(50) | NULL | Type of pipeline | Values: 'extract', 'transform', 'load', 'full', 'incremental' |
| `records_processed` | INTEGER | DEFAULT 0 | Number of records processed | Total records processed in pipeline |
| `records_successful` | INTEGER | DEFAULT 0 | Number of successful records | Successfully processed records |
| `records_failed` | INTEGER | DEFAULT 0 | Number of failed records | Failed records count |
| `processing_duration_seconds` | INTEGER | NULL | Processing duration in seconds | Pipeline execution time |
| `error_log` | VARCHAR(16777216) | NULL | Error log | Error messages and stack traces |
| `status` | VARCHAR(50) | DEFAULT 'running' | Pipeline status | Values: 'running', 'success', 'failed', 'partial' |
| `start_time` | TIMESTAMP_NTZ | NOT NULL | Pipeline start time | Start timestamp |
| `end_time` | TIMESTAMP_NTZ | NULL | Pipeline end time | End timestamp (NULL if still running) |
| `data_volume_bytes` | BIGINT | NULL | Data volume processed in bytes | Data volume processed |

---

## Data Type Reference

### VARCHAR(n)
Variable-length character strings with maximum length `n`. Used for text fields, identifiers, and JSON metadata.

### INTEGER
32-bit integer values. Used for counts, quantities, and numeric identifiers.

### NUMERIC(p, s)
Fixed-precision decimal numbers with precision `p` (total digits) and scale `s` (decimal places). Used for scores, prices, percentages, and measurements.

### BOOLEAN
Boolean true/false values. Used for flags and status indicators.

### DATE
Date values in YYYY-MM-DD format. Used for dates without time components.

### TIMESTAMP_NTZ
Timestamp without timezone (for cross-database compatibility). Used for audit timestamps and pipeline execution times.

### BIGINT
64-bit integer values. Used for large counts and data volumes.

---

## Common Enumerated Values

### model_status
- `active`: Model is currently active and available
- `deprecated`: Model has been deprecated
- `preview`: Model is in preview/beta
- `experimental`: Model is experimental

### license_type
- `open`: Open source license
- `proprietary`: Proprietary license
- `commercial_restricted`: Commercial use with restrictions

### creator_type
- `open_source`: Open source organization
- `proprietary`: Proprietary organization
- `hybrid`: Hybrid licensing approach

### market_position
- `leader`: Market leader
- `challenger`: Challenger position
- `follower`: Follower position
- `niche`: Niche market position

### trend_direction
- `increasing`: Increasing trend
- `decreasing`: Decreasing trend
- `stable`: Stable trend

### adoption_trend
- `growing`: Growing adoption
- `stable`: Stable adoption
- `declining`: Declining adoption

### compliance_level
- `compliant`: Fully compliant
- `partially_compliant`: Partially compliant
- `non_compliant`: Non-compliant

### pipeline_status
- `running`: Pipeline is currently running
- `success`: Pipeline completed successfully
- `failed`: Pipeline failed
- `partial`: Pipeline completed with partial success

---

## Notes

1. **JSON Metadata Columns**: Several tables include JSON metadata columns (`metadata_json`, `evaluation_metadata`, `benchmark_metadata`, etc.) stored as `VARCHAR(16777216)` for cross-database compatibility. These columns can store structured JSON data for flexible schema extensions.

2. **Foreign Key Relationships**: Foreign keys are defined but may be nullable in some cases (e.g., `government_benchmark_data.model_id`) to allow for external models not yet in the `ai_models` table.

3. **Timestamps**: All tables include `created_at` and `updated_at` timestamp columns (where applicable) for audit tracking. These use `TIMESTAMP_NTZ` (no timezone) for cross-database compatibility.

4. **Data Sources**: The `data_source` column tracks the origin of data for lineage and quality monitoring. Common values include 'ARTIFICIAL_ANALYSIS', 'GOVERNMENT', 'CALCULATED', 'AGGREGATED'.

5. **Cross-Database Compatibility**: All data types and SQL syntax are chosen for compatibility across PostgreSQL (Delta Lake).

---
**Last Updated:** 2026-02-04  
**Version:** 1.0
