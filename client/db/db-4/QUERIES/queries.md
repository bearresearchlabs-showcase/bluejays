# SharedAI Models (Seydam AI) — Query Documentation

## Database Overview

```yaml
db_id: db-4
domain: SharedAI / AI Model Registry
source: [commercial]
license_type: [Commercial]
license_cost: [NDA]
tables: 1
total_rows: ~200
date_range: 2020-01-01 to 2026-12-31
sql_dialect: PostgreSQL
```

## Purpose

```text
This database supports analytics for SharedAI (Seydam AI) model registries. It models
AI/ML models created by users, including model names, ownership, and creation timestamps.
It is designed to support text-to-SQL training across adoption, usage, and operational
query types commonly encountered in AI platform analytics.
```

## Use Case

```text
Target use cases for db-4:
- Adoption analytics: model creation volume, user activity, growth trends
- Usage patterns: models per user, creation frequency, time-of-day distribution
- Operations: outlier detection, rolling metrics, quartile analysis for capacity planning
- Product dashboards: model registry growth, top creators, adoption curves
```

## Business Value

```text
AI model registries represent high-value domains for text-to-SQL because:
- Queries require understanding of model lifecycle (creation, ownership, timestamps)
- Stakeholders need self-serve analytics (product, platform, growth teams)
- Evidence bridges natural-language questions to schema-grounded SQL.
```

## Schema

```sql
-- db-4 SharedAI Models - Production schema for query execution
-- Compatible with PostgreSQL
-- Single canonical schema: models table (queries use FROM models)

CREATE TABLE IF NOT EXISTS public.models (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_models_created_at ON public.models(created_at);
CREATE INDEX IF NOT EXISTS idx_models_user_id ON public.models(user_id);
CREATE INDEX IF NOT EXISTS idx_models_name ON public.models(name);
```

## Domain Knowledge

```text
Key domain concepts required to write correct queries against this database:

MODELS TABLE:
- id: BIGINT primary key; used as numeric proxy in aggregations (count, avg, percentile)
- name: model identifier/name; partition key for per-model analytics
- user_id: creator/owner; partition key for per-user analytics
- created_at: timestamp of model creation; used for time-bucketing (day, week, month)

ANALYTICS PATTERNS:
- Rolling averages: ROWS BETWEEN N PRECEDING AND CURRENT ROW over created_at
- Z-scores: (value - partition_avg) / partition_stddev for outlier detection
- Quartiles: PERCENTILE_CONT(0.25), (0.5), (0.75) WITHIN GROUP
- Trend direction: LAG/LEAD to classify Increasing, Decreasing, Stable
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
  "db_id": "db-4",
  "question_id": 1,
  "question": "I need to see how model altitude varies day by day over the past year, including rolling averages and how many outlier readings we get per model.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 60\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.name\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query constructs four CTEs. First, it retains the 60 most recent records per model name (cte_level_1). Second, it computes a 5-row rolling average and cumulative sum via window functions on id (cte_level_2). Third, it uses LAG, LEAD, and partition statistics for trend and z-score calculation (cte_level_3). Fourth, it flags outliers (z-score > 2) and trend direction, then aggregates by day and name with PERCENTILE_CONT, SUM for outlier/increasing counts, and AVG for rolling average.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and name",
  "normal_query": "Compute daily model altitude statistics with rolling averages and outlier counts for each aircraft model over the last 365 days."
}
```



### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 2,
  "question": "Can you show me weekly altitude statistics grouped by airspeed bucket? I need quartiles, outlier counts, and how many readings are trending upward.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 70\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and user_id. It divides id into sextiles (NTILE(6)), calculates z-scores per partition, flags outliers (>2 std dev), and uses LAG/LEAD to compare consecutive values for trend direction. Aggregates include quartiles (PERCENTILE_CONT), outlier count, and increasing-trend count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and user_id",
  "normal_query": "Compute weekly model altitude statistics by airspeed bucket with quartiles, z-score outliers, and increasing-trend counts."
}
```



### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 3,
  "question": "Give me monthly altitude summaries for each aircraft model\u2014quartiles, median, outlier count, and the rolling average.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 80\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.name\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and name. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 6-row rolling average; flags outliers via z-score; and aggregates record count, stddev, min, max, outlier count, and increasing count. ROW_NUMBER limits to 80 points per model name.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and name",
  "normal_query": "Compute monthly model altitude statistics per aircraft model with quartiles, median, outlier count, and rolling average."
}
```



### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 4,
  "question": "I need a daily breakdown of altitude by flight phase\u2014how many outliers, how many readings are increasing, and what's the maximum cumulative sum.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 90\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and user_id. It calculates running cumulative sum of id, applies a 7-row rolling window, uses NTILE(8) for distribution, and aggregates outlier count, increasing-trend count, and max cumulative sum per group.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and user_id",
  "normal_query": "Compute daily model altitude statistics by flight phase with outlier count, increasing-trend count, and maximum cumulative sum."
}
```



### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 5,
  "question": "Show me weekly altitude metrics for each aircraft model\u2014record count, quartiles, standard deviation, and how many readings are increasing.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 100\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.name\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and name. It calculates STDDEV, PERCENTILE_CONT for quartiles, and uses LAG/LEAD with delta_value to derive trend_direction. Aggregates include record count, quartiles, stddev, outlier count, and increasing count. ROW_NUMBER limits to 100 points per model.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and name",
  "normal_query": "Compute weekly model altitude statistics per aircraft model with record count, quartiles, standard deviation, and increasing-trend count."
}
```



### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 6,
  "question": "I need daily model ID statistics broken down by user bucket, including quartiles, rolling averages, and outlier detection to monitor flight regime behavior.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 110\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and user_id. It computes z-scores (mean, stddev per partition; zero when stddev=0), flags outliers, calculates a rolling average, and filters to groups with \u22651 record. Output includes quartiles, rolling average, and outlier count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and user_id",
  "normal_query": "Compute daily model ID statistics grouped by user, including quartiles, rolling average, and z-score based outlier count."
}
```



### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 7,
  "question": "I want monthly model ID analysis grouped by model name, showing quartiles, min/max ranges, outlier counts, and cumulative sum trends.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 120\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.name\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and name. It captures min/max id, flags outliers (z-score > 2), limits to 120 points per model, uses PERCENT_RANK, and calculates cumulative sum via window. Aggregates include quartiles, min, max, outlier count, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and name",
  "normal_query": "Compute monthly model ID statistics per model name with quartiles, minimum and maximum values, outlier count, and maximum cumulative sum."
}
```



### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 8,
  "question": "Show me daily model ID statistics by model name with gaps between readings, sequential differences from one reading to the next, and quartile distributions.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 130\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and user_id. It uses LAG to get previous id, computes delta (current minus previous), derives trend_direction from the sign, and uses LEAD for next value. Aggregates include quartiles and sequential difference metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and user_id",
  "normal_query": "Compute daily model ID statistics per model name including sequential differences, gap analysis, and quartiles."
}
```



### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 9,
  "question": "I need daily model ID statistics by user with z-score based anomaly detection, quartiles, and counts of increasing versus decreasing trends.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 140\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.name\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and name. It computes mean and stddev per group, flags anomalies (|z| > 2), handles stddev=0 safely, segments into septiles (NTILE(7)), and aggregates quartiles, outlier count, and trend direction counts.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and name",
  "normal_query": "Compute daily model ID statistics grouped by user with z-score anomaly detection, quartiles, and trend direction counts."
}
```



### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 10,
  "question": "Give me weekly model ID statistics by model name with recency and frequency scoring to prioritize maintenance, plus quartiles and rolling averages.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 150\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and user_id. It assigns ROW_NUMBER (desc timestamp) for recency scoring, uses record count as frequency proxy, ranks by cumulative sum, computes 6-row rolling average, and filters to groups with \u22652 records. Output includes quartiles and rolling average.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and user_id",
  "normal_query": "Compute weekly model ID statistics per model name with recency-frequency scoring metrics, quartiles, and rolling average."
}
```



### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 11,
  "question": "What are the monthly model ID retention patterns and distribution quartiles for each user cohort?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 160\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.name\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query treats each model name as a cohort dimension. It limits to 160 points per name, uses window functions for increasing_count and trend_direction (analogous to retention), and orders by time period and average value. Output includes cohort-style progression and quartile boundaries.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and name",
  "normal_query": "Calculate monthly model ID statistics grouped by user, including cohort-style retention metrics and quartile distributions."
}
```



### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 12,
  "question": "What are the daily model ID acceleration patterns, quartiles, and outlier frequencies for each model name?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 170\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and user_id. It uses LAG to create first derivative (id change). trend_direction captures sign of change. LAG and LEAD together enable second-order derivative. Z-scores flag outliers. Output includes change rate metrics, quartiles, and outlier count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and user_id",
  "normal_query": "Calculate daily model ID statistics per model name, including rate-of-change metrics, quartile distributions, and outlier counts."
}
```



### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 13,
  "question": "How do weekly model ID distributions compare across users using percentile benchmarking and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 180\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.name\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and name. It employs PERCENT_RANK for cross-category benchmarking and PERCENTILE_CONT for percentile values. Data segmented into quintiles (NTILE(5)). Partition-level avg/stddev enable z-scores. Output includes percentile rankings and quartile distributions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and name",
  "normal_query": "Calculate weekly model ID statistics by user with cross-user percentile rankings and quartile distributions."
}
```



### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 14,
  "question": "What are the monthly smoothed model ID trends, quartiles, and directional pattern counts for each model?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 190\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and user_id. It implements a 3-row rolling window for simple moving average (avg_rolling). It counts periods where id is increasing and flags statistical outliers. Limited to 190 points per user. Output includes quartiles and trend pattern counts.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and user_id",
  "normal_query": "Calculate monthly model ID statistics per model name using weighted moving averages, quartile distributions, and trend frequency counts."
}
```



### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 15,
  "question": "What are the daily peak model ID periods, operational efficiency metrics, and quartiles for each user?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 200\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.name\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and name. It ranks id within each day using window functions to identify peaks per user category. Extracts hour and day-of-week for temporal analysis. Calculates max_cumulative and avg_rolling. Output includes peak period identification and quartile distributions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and name",
  "normal_query": "Calculate daily model ID statistics by user, identifying peak periods, operational efficiency indicators, and quartile distributions."
}
```



### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 16,
  "question": "What are the weekly model ID statistics by model name, including lifetime value style estimation, quartile distributions, and cumulative sums?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 210\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and user_id. It computes cumulative_sum as total activity proxy, tracks max_cumulative for lifetime value, ranks users by cumulative sum, applies PERCENT_RANK. Limited to 210 points per user, \u22652 records per group. Output includes LTV metrics, quartiles, and cumulative totals.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and user_id",
  "normal_query": "Calculate weekly model ID statistics grouped by model name, incorporating lifetime value style metrics, quartile distributions, and cumulative sum analysis."
}
```



### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 17,
  "question": "What are the monthly model ID statistics by user showing year-over-year growth rate style analysis and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 220\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.name\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and name. It extracts hour_val and dow_val for temporal context. Uses window functions (rolling avg, cumulative sum, LAG, LEAD) and aggregates by period and name. Output includes temporal correlation metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and name",
  "normal_query": "Calculate monthly model ID statistics grouped by user, incorporating year-over-year growth style metrics and quartile distributions."
}
```



### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 18,
  "question": "What are the daily model ID statistics by model name formatted for heatmap visualization, including quartile distributions and outlier counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 230\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and user_id. It uses period and user_id as dimensions. Computes avg_value and record_count, extracts hour and day-of-week, flags outliers via z-scores. Output includes quartiles and outlier count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and user_id",
  "normal_query": "Calculate daily model ID statistics grouped by model name, structured for heatmap visualization with quartile distributions and outlier counts."
}
```



### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 19,
  "question": "What are the weekly model ID statistics by user showing running percentile distributions, quartiles, and trend counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 240\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.name\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and name. It applies PERCENT_RANK for running percentile position and PERCENTILE_CONT for quartile breakpoints. Limited to 240 points per model. Counts increasing trends and outliers. Output includes running percentiles, quartiles, and trend pattern counts.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and name",
  "normal_query": "Calculate weekly model ID statistics grouped by user, incorporating running percentile distributions, quartile analysis, and trend counts."
}
```



### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 20,
  "question": "What are the monthly model ID statistics by model name showing cross-correlation pattern analysis, quartile distributions, and rolling averages?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 250\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and user_id. It uses LAG and LEAD to access preceding and following period values. Calculates delta_value and trend_direction. Partition_avg and partition_stddev enable z-score normalization. Output includes sequential correlation metrics and quartiles.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and user_id",
  "normal_query": "Calculate monthly model ID statistics grouped by model name, incorporating cross-correlation style metrics, quartile distributions, and rolling averages."
}
```



### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 21,
  "question": "What are the daily model ID statistics for each user, including status transition forensics, quartile distributions, and outlier counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 260\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.name\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and name. It treats trend_direction (Increasing, Decreasing, Stable) as status categories. Uses LAG and LEAD for sequential status change tracing, calculates z-scores, computes quartiles per group. Output includes status transition sequences and quartile boundaries.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and name",
  "normal_query": "Calculate daily model ID statistics grouped by user, incorporating status transition analysis, quartile distributions, and outlier detection counts."
}
```



### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 22,
  "question": "What are the weekly model ID metrics for each model name, providing complete dashboard-ready statistics with quartiles and multi-dimensional aggregations?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 270\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and user_id. It performs single-pass aggregation: record_count, avg_value, quartiles, stddev, min, max, outlier_count, increasing_count, avg_rolling, max_cumulative. Filters to \u22652 records per user-month. Output includes full dashboard suite of statistics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and user_id",
  "normal_query": "Generate weekly model ID statistics aggregated by model name, delivering a complete set of dashboard metrics including quartiles and comprehensive multi-metric summaries."
}
```



### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 23,
  "question": "What are the monthly model ID statistics for each user, revealing sequential patterns through window functions and quartile analysis?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 280\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.name\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and name. It employs LAG and LEAD for previous/next period values, calculates delta_value and trend_direction, uses ROWS BETWEEN window frames, applies ROW_NUMBER for ordering, limits to 280 points per model. Output includes sequential pattern indicators and quartiles.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and name",
  "normal_query": "Compute monthly model ID statistics segmented by user, incorporating sequential pattern detection metrics and quartile distributions."
}
```



### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 24,
  "question": "What are the daily model ID statistics for each model name, including concentration indices, quartile distributions, and outlier counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 290\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and user_id. It uses DENSE_RANK for ranking, PERCENT_RANK for relative position, cumulative_sum for concentration measurement, NTILE(4) for quartiles, z-scores for outliers. Output includes concentration indices, quartiles, and outlier count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and user_id",
  "normal_query": "Calculate daily model ID statistics grouped by model name, featuring concentration index measurements, quartile analysis, and outlier detection counts."
}
```



### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 25,
  "question": "What are the weekly model ID statistics for each user, featuring statistical anomaly scores, quartile distributions, and trend pattern counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 300\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.name\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and name. It calculates z_score as anomaly metric, aggregates outlier_count, computes partition_avg and partition_stddev, counts trend_direction records, limits to 300 points per model. Output includes anomaly scores, quartiles, and trend counts.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and name",
  "normal_query": "Generate weekly model ID statistics by user with anomaly score assignments, quartile analysis, and aggregated trend pattern counts."
}
```



### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 26,
  "question": "What are the monthly model ID statistics by model name for fiscal period comparative reporting with quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 310\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and user_id. It uses DATE_TRUNC('month') for period grouping. Calculates quartiles (PERCENTILE_CONT), average, and standard deviation. Limits to 310 points per user. Output includes quartile breakdowns for fiscal period comparison.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and user_id",
  "normal_query": "Calculate monthly model ID statistics grouped by model name to enable fiscal period comparison, including quartile distributions."
}
```



### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 27,
  "question": "What are the daily model ID statistics by user with throughput optimization metrics, quartiles, and rolling averages?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 320\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.name\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and name. It calculates record_count (volume), avg_rolling (9-row moving average), max_cumulative (peak capacity). Limits to 320 points per model, \u22651 record per group. Output includes throughput indicators, quartiles, and rolling averages.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and name",
  "normal_query": "Calculate daily model ID statistics grouped by user, including throughput metrics, quartile distributions, and rolling averages."
}
```



### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 28,
  "question": "What are the weekly model ID statistics by model name for cumulative trend analysis with quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 330\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and user_id. It computes cumulative_sum and max_cumulative. Derives trend_direction and increasing_count. Ranks users by cumulative sum. Filters to \u22652 records per group. Output includes cumulative trend indicators, quartiles, and user rankings.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and user_id",
  "normal_query": "Calculate weekly model ID statistics grouped by model name to support cumulative trend analysis, including quartile distributions."
}
```



### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 29,
  "question": "What are the monthly model ID statistics by user for multi-dimensional pivot aggregation with quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 340\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.name\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and name. It uses time period (day) and name as grouping dimensions. Aggregates record count, average, quartiles, stddev, min, max, outlier_count, trend indicators. Requires \u22653 records per group. Output includes multi-dimensional aggregate metrics and quartiles.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and name",
  "normal_query": "Calculate monthly model ID statistics grouped by user to enable multi-dimensional aggregation and pivot analysis, including quartile distributions."
}
```



### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 30,
  "question": "What are the weekly model ID statistics by user for IQR-style outlier detection with quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.user_id) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.user_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 350\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.user_id ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.user_id) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.user_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.user_id ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.user_id ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.created_at) AS period,\n    c4.user_id,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.created_at), c4.user_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and user_id. It calculates quartiles via PERCENTILE_CONT for Q1 and Q3 (IQR support), flags outliers (z-score > 2), includes stddev_value for IQR-based boundaries, computes trend counts. Limited to 350 points per user. Output includes IQR-style outlier detection, quartiles, and trend metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and user_id",
  "normal_query": "Calculate weekly model ID statistics grouped by user using IQR-style outlier detection methodology, including quartile distributions."
}
```


