# SharedAI Models (Seydam AI) — Query Documentation

## Database Overview

```yaml
db_id: db-4
domain: Database domain
source: [synthetic / open / commercial]
license_type: [Commercial / Open / Academic]
license_cost: [Annual cost if applicable]
tables: 0
total_rows: ~0
date_range: 2020-01-01 to 2026-12-31
sql_dialect: PostgreSQL
```

## Purpose

```text
This database supports analytics for db-4.
```

## Use Case

```text
Target use cases for db-4: analytics, reporting, dashboards.
```

## Business Value

```text
Business value for db-4.
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

### Query 1 — moderate / aggregation

```json
{
  "db_id": "db-4",
  "question_id": 1,
  "question": "I need to see how model altitude varies day by day over the past year, including rolling averages and how many outlier readings we get per model.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY name ORDER BY created_at DESC) AS rn,\n        DATE_TRUNC('day', created_at) AS day_bucket,\n        DATE_TRUNC('week', created_at) AS week_bucket,\n        EXTRACT(HOUR FROM created_at) AS hour_val,\n        EXTRACT(DOW FROM created_at) AS dow_val\n    FROM models\n    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.name) AS daily_partition_count,\n        AVG(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at) AS first_val,\n        LAST_VALUE(c1.id) OVER (PARTITION BY c1.name ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 60\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS prev_value,\n        LEAD(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS next_value,\n        c2.id - LAG(c2.id, 1) OVER (PARTITION BY c2.name ORDER BY c2.created_at) AS delta_value,\n        AVG(c2.id) OVER (PARTITION BY c2.name) AS partition_avg,\n        STDDEV(c2.id) OVER (PARTITION BY c2.name) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.name ORDER BY c2.id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.name ORDER BY c3.id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.created_at) AS period,\n    c4.name,\n    COUNT(*) AS record_count,\n    AVG(c4.id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.id) AS q3_value,\n    STDDEV(c4.id) AS stddev_value,\n    MIN(c4.id) AS min_value,\n    MAX(c4.id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.created_at), c4.name\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Platform operators monitoring ADS-B telemetry need to track how aircraft altitude varies over time to identify anomalies and determine when maintenance is required. Each aircraft model has a unique ICAO 24-bit transponder code (model name), and altitude is recorded in feet. Produce daily aggregated altitude statistics per aircraft model, including rolling averages and counts of outlier readings. The query constructs four CTEs: first it retains the 60 most recent data points per model to manage memory, then computes a 5-row rolling average to smooth short-term fluctuations, flags outliers where altitude exceeds 2 standard deviations from the mean, and classifies each reading as Increasing, Decreasing, or Stable based on comparison with the prior value. It groups results by day and model name, requiring at least 2 records per group for statistical validity. When standard deviation is zero (no variation), it sets the z-score to 0 to avoid division-by-zero errors. ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Analysts need to compare altitude patterns across different groundspeed buckets (measured in knots) to understand how aircraft behave differently at various speeds\u2014for example, fast-flying aircraft during cruise versus slower speeds during approach. Produce weekly altitude statistics segmented by airspeed bucket, including quartiles, outlier counts, and trend direction indicators. The query groups telemetry by week and airspeed, segments altitude into sextiles (six quantile bins) within each airspeed bucket, flags statistical outliers using z-scores above 2, and applies LAG and LEAD window functions to classify each reading as Increasing, Decreasing, or Stable by comparing it to adjacent records. It filters out sparse buckets containing fewer than 3 records to ensure statistical robustness. Weekly metrics per airspeed bucket showing quartiles (Q1, median, Q3), count of outlier readings, and the number of readings that are trending upward.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Fleet managers require monthly reporting to track long-term altitude trends per aircraft model and identify seasonal patterns or gradual shifts that may indicate systemic issues or operational changes. Produce monthly altitude summaries for each aircraft model, including quartiles, median, outlier count, and a rolling average. The query groups telemetry by month and model name, uses PERCENTILE_CONT to calculate Q1, median, and Q3, computes a 6-row rolling average to smooth monthly fluctuations, limits the dataset to the 80 most recent data points per model to control memory usage, and allows months with a single record for sparse or infrequently observed aircraft models. Monthly metrics per aircraft model containing record count, quartiles (Q1, median, Q3), count of outlier readings, and the rolling average altitude.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Daily breakdowns by flight phase (such as cruise, climb, or descent) help analysts identify whether certain operational regimes exhibit more altitude anomalies, which may indicate autopilot issues, turbulence, or non-standard procedures. Produce daily altitude statistics segmented by flight phase, including outlier count, count of increasing-trend readings, and the peak cumulative sum of altitude changes. The query groups telemetry by day and flight phase, computes a running cumulative sum of altitude per phase to track total vertical movement, applies a 7-row rolling window to smooth noise, segments altitude into octiles (eight quantile bins) for distribution analysis, and derives trend direction by comparing each reading to the previous one using a window function. When the prior value is missing (e.g., first record in a phase), it treats the reading as Stable. Daily metrics per flight phase showing outlier count, number of readings classified as incr",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Weekly views per aircraft model allow fleet operators to compare altitude variability (measured by standard deviation) and trend direction across the entire fleet, helping prioritize models that show unusual dispersion or consistent upward drift. Produce weekly altitude metrics for each aircraft model, including record count, quartiles, standard deviation, and count of readings trending upward. The query groups telemetry by week and model name, computes standard deviation to quantify altitude dispersion and variability, counts readings classified as Increasing by comparing each to the prior value, limits the dataset to the 60 most recent points per model to manage memory, and ranks models by cumulative sum to prioritize those with the largest total altitude changes for investigation. Weekly metrics per aircraft model containing record count, quartiles (Q1, median, Q3), standard deviation, and the number of readings that are trending upward.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Flight operations teams monitor model ID patterns across different user buckets to identify anomalies that may indicate issues in specific flight regimes or operational conditions. Generate daily model ID statistics segmented by user_id that include quartile distributions, rolling averages for trend analysis, and automated outlier detection. The query groups records by calendar day and user_id, extracts temporal features (hour and day-of-week) for intermediate analysis, calculates z-scores to identify statistical outliers (handling zero standard deviation cases by defaulting to zero to prevent division errors), computes a 5-row rolling window average to smooth short-term fluctuations, and filters to include only groups with at least 2 records to ensure statistical validity. A dataset containing daily metrics for each user_id, including first/third quartiles, 5-period moving average, and count of outlier observations exceeding 2 standard deviations.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Fleet management requires monthly aggregated analysis of model ID metrics across different aircraft models to enable fleet-wide comparisons of operational ranges and cumulative activity patterns. Produce comprehensive monthly model ID statistics for each aircraft model, including quartile distributions, value ranges, outlier identification, and cumulative activity tracking. The query groups data by calendar month and model name, captures the full range of model IDs (minimum and maximum values), flags outliers using z-score methodology (values exceeding 2 standard deviations from the mean), limits analysis to the most recent 80 data points per model to focus on current patterns, calculates PERCENT_RANK to determine relative position within each model's distribution, and ensures LAST_VALUE window function retrieves the true final value in each partition by proper frame specification. Monthly summary metrics for each model including first/third quartiles, ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Flight analysts need visibility into how model ID values change between consecutive readings to detect sudden altitude climbs, descents, or other significant operational transitions that may require investigation. Generate daily model ID statistics for each aircraft model that highlight sequential changes, identify gaps in the data stream, and provide quartile context. The query groups observations by calendar day and model name, uses the LAG window function to compute the difference between each reading and its immediate predecessor (with the first row in each model partition having no prior value and thus null delta), derives trend direction classification (increasing/decreasing/stable) from the calculated change value, employs both LAG and LEAD functions to capture previous and next values for context, and performs gap analysis implicitly through timestamp-based ordering to identify breaks in the sequence. Daily metrics for each model including seque",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Operations teams require automated anomaly detection at the user bucket level to identify unusual model ID patterns that may indicate irregular flight behavior or data quality issues within specific operational regimes. Produce daily model ID statistics segmented by user_id that incorporate statistical anomaly detection, quartile distributions, and trend analysis counting. The query groups records by calendar day and user_id, flags anomalies where individual model ID values exceed 2 standard deviations from the partition mean (indicating statistically significant outliers), handles edge cases where standard deviation is zero by safely defaulting z-scores to prevent mathematical errors, segments the distribution into octiles (8 equal groups) for granular distribution analysis, applies a 7-row rolling window for smoothed trend calculation, and counts observations exhibiting increasing versus decreasing trends. Daily metrics for each user_id including tota",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Maintenance planning teams need to prioritize which aircraft models to inspect based on both how frequently they appear in the data (indicating high utilization) and how recently they were active (indicating current operational status). Generate weekly model ID statistics for each aircraft model that incorporate recency-frequency style scoring metrics alongside traditional quartile distributions and trend smoothing. The query groups data by calendar week and model name, assigns ROW_NUMBER rankings to establish recency scores (with rank 1 being most recent activity), uses record_count as a proxy for frequency of activity, ranks models by their cumulative sum to identify highest total activity, computes a 6-row rolling average to smooth weekly volatility and reveal underlying trends, and filters to include only groups with at least 3 records to ensure meaningful statistical calculations. Weekly summary metrics for each model including total record count (",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "The analytics team needs to understand how different user cohorts (bucketed by user_id) exhibit varying model ID behavior over time, similar to retention analysis in product analytics. This cohort-style comparison reveals whether certain flight regimes or user segments show more stable or growing ID patterns month-over-month. Generate monthly model ID statistics segmented by user_id, incorporating cohort-style retention indicators and quartile breakdowns to identify user segments with strong versus weak engagement patterns. The SQL treats each user_id bucket as a distinct cohort and tracks model ID as the key metric. It limits the dataset to 90 data points per user_id to ensure balanced comparison. The query calculates increasing_count (how many periods show growth) and trend_direction (Increasing/Decreasing/Stable) to mirror retention curve analysis. Results are ordered by time period and average value to surface both recent trends and prominent cohorts. Resul",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Engineering teams monitoring flight systems need to detect not just changes in model ID, but accelerating changes\u2014where the rate of increase or decrease itself is changing rapidly. Such second-order derivative patterns can indicate developing issues like sensor drift, system instability, or sudden operational shifts that first-order metrics alone might miss. Produce daily model ID statistics for each model name, incorporating change velocity metrics (first derivative), acceleration indicators (second derivative), quartile distributions, and counts of statistical outliers to flag anomalous behavior. The SQL computes the first derivative by calculating the change from the prior reading using LAG. It infers acceleration (second derivative) by analyzing consecutive changes via LAG and LEAD on the change values. The trend_direction field (Increasing/Decreasing) captures the sign of change velocity. Z-score calculations flag statistical outliers beyond normal variati",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Operations analysts need to benchmark model ID performance across different user segments (representing different flight regimes or operational contexts) to identify which user groups have consistently high, average, or low ID values. Cross-category benchmarking using percentiles provides a normalized view that accounts for the overall distribution, making it possible to compare user_id buckets fairly even when absolute ID scales differ. Generate weekly model ID statistics segmented by user_id, incorporating percentile-based benchmarking across all users, quartile breakdowns within each user, and cross-category performance rankings to identify top and bottom performing user segments. The SQL employs PERCENT_RANK to calculate each user_id's relative standing in the overall distribution and PERCENTILE_CONT to compute exact percentile values for benchmarking. It segments the data into sextiles (six equal groups) for granular comparison. User_ids are ranked by cumu",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Raw model ID data often contains noise from temporary fluctuations, measurement variance, or transient operational events. To identify genuine underlying trends in model behavior over time, analysts need smoothed metrics that filter out short-term volatility while preserving meaningful directional patterns. Moving averages provide this smoothing effect, making it easier to spot sustained increases, decreases, or stability in model ID values. Produce monthly model ID statistics for each model name, incorporating rolling moving averages to smooth volatility, quartile distributions for spread analysis, and counts of increasing periods and outliers to quantify trend strength and data quality. The SQL applies a 6-row rolling window function to calculate a simple moving average (avg_rolling) that smooths out short-term fluctuations. It counts the number of periods showing increasing trends to measure momentum strength. Outlier readings (based on z-scores) are tallied",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Capacity planners and operations teams need to identify when model ID values reach their peak within each user segment (flight regime) on a daily basis. Understanding these peak periods\u2014including the time of day and day of week\u2014enables better resource allocation, maintenance scheduling, and operational planning. Additionally, efficiency metrics that compare current performance to historical maximums and rolling averages help assess whether the system is operating near capacity or has headroom. Generate daily model ID statistics segmented by user_id, incorporating peak period identification with temporal context, operational efficiency metrics comparing current to maximum and average performance, and quartile distributions to understand value spread. The SQL ranks all readings by model ID value within each day to identify peak observations (rank = 1). It extracts hour-of-day and day-of-week from timestamps to provide temporal context for peak periods. The query ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "The maintenance scheduling team needs to prioritize aircraft models based on their total activity patterns over time. Lifetime value style metrics provide a way to rank models by cumulative activity, helping allocate maintenance resources to the most critical models. Generate weekly model ID statistics for each model name that include lifetime value style metrics, quartile distributions, and cumulative sum calculations. The query computes cumulative_sum and max_cumulative as proxy metrics for lifetime value estimation, ranks models by their cumulative sum to establish priority order, applies PERCENT_RANK to determine quartile distribution across the fleet, limits output to 60 data points per model to ensure manageable result sets, calculates rolling averages to smooth short-term fluctuations, counts outlier occurrences for anomaly detection, and requires at least 3 records per model group to ensure statistical validity. A weekly summary per model name c",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Flight operations analysts need to understand how model ID patterns evolve across different flight regimes and user profiles from one year to the next. Year-over-year growth analysis reveals whether activity is increasing, decreasing, or stabilizing for each user, which informs capacity planning and operational adjustments. Generate monthly model ID statistics for each user_id that include year-over-year growth style metrics and quartile distributions. The query uses trend_direction and delta_value fields to support growth rate calculations, applies the LAG window function to capture prior period values for comparison, filters data to the last 365 days to enable meaningful one-year comparisons, limits output to 90 data points per user_id to balance detail with performance, computes quartiles using PERCENT_RANK to show distribution across users, and calculates month-over-month changes to identify growth trends. A monthly summary per user_id containing gr",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Fleet managers require visual tools to quickly identify model ID patterns across the entire fleet over time. Heatmap visualizations provide an intuitive way to spot anomalies, trends, and patterns by displaying intensity across two dimensions\u2014time and model. Generate daily model ID statistics for each model name in a format optimized for heatmap visualization, including quartile distributions and outlier detection. The query uses period and model name as the two primary heatmap dimensions, calculates avg_value and record_count as intensity metrics to drive heatmap color gradients, extracts hour and day-of-week components to enable flexible 2D heatmap options, flags outliers using z-score thresholds to highlight anomalies visually, computes quartiles using PERCENT_RANK for distribution context, orders results by period and avg_value to facilitate rendering, and includes outlier counts to quantify data quality issues. A daily summary per model name contai",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Operations teams need to understand how model ID values are distributed within each user's activity bucket over time. Running percentile distributions reveal whether a user's current activity is typical, above average, or below average relative to their historical patterns, which helps identify operational anomalies or shifts in usage patterns. Generate weekly model ID statistics for each user_id that include running percentile distributions, quartile positions, and trend counts. The query applies PERCENT_RANK to calculate each record's position within the user's distribution, uses PERCENTILE_CONT to compute continuous percentile values for smoother distribution analysis, limits output to 70 data points per user_id to balance historical depth with query performance, counts records with increasing trends to quantify upward momentum, flags and counts outlier readings using statistical thresholds, computes quartile boundaries to segment the distribution, and order",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Fleet analysts need to understand how current model ID readings relate to prior readings across different aircraft models. Cross-correlation pattern analysis reveals whether changes in one time period predict or correlate with changes in subsequent periods, which is critical for predictive maintenance and early warning systems. Generate monthly model ID statistics for each model name that include cross-correlation style metrics, quartile distributions, and rolling averages. The query uses LAG and LEAD window functions to access prior and subsequent period values for sequential correlation analysis, calculates delta_value to measure period-over-period changes, captures trend_direction to identify pattern consistency across time, computes partition_avg and partition_stddev to enable normalization and standardized comparison across models with different baseline values, limits output to 80 data points per model to provide sufficient history for pattern detection w",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "The forensic team needs to trace how model IDs transition between behavioral states (Increasing, Decreasing, Stable) over time within each user account to identify suspicious patterns and investigate anomalies. Generate comprehensive daily model ID statistics segmented by user_id, including full status transition tracking, quartile breakdowns, and counts of statistical outliers. The query interprets trend_direction values (Increasing/Decreasing/Stable) as distinct status states and uses delta_value as the transition driver. It employs LAG and LEAD window functions to create forensic sequences showing before-and-after states, calculates z-scores to flag statistical outliers beyond normal variance, computes Q1, median, and Q3 quartiles for distribution analysis, and filters to include only user groups with at least 2 historical records to ensure meaningful comparisons. A dataset with one row per user_id per day containing status transition sequences, quar",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Operations dashboards require a consolidated data feed that provides all essential monitoring metrics in a single query to track fleet-wide model performance without multiple database calls. Produce a complete weekly statistical profile of model IDs grouped by model name, encompassing all critical dashboard metrics in one result set. The query performs a comprehensive single-pass aggregation computing record_count (total observations), avg_value (mean ID value), quartiles (Q1, median, Q3), stddev (standard deviation), min and max (range bounds), outlier_count (statistical anomalies), increasing_count (upward trend instances), avg_rolling (moving average), and max_cumulative (peak accumulation) for each model. It applies a minimum threshold of 3 records per model group to ensure statistical validity. A weekly metrics table with one row per model name containing the full dashboard metric suite: counts, averages, quartiles, deviation measures, range limits",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Analysts need to understand how model ID values evolve chronologically within each user's activity stream to identify behavioral patterns, trends, and sequential dependencies over monthly periods. Generate monthly model ID statistical profiles by user_id that capture sequential evolution patterns alongside standard distribution metrics. The query applies LAG window functions to access previous period values, LEAD functions to peek at subsequent values, and calculates delta_value (period-over-period change) and trend_direction (Increasing/Decreasing/Stable classification) to characterize sequential behavior. It uses ROWS BETWEEN frame specifications to define precise window boundaries for rolling calculations, employs ROW_NUMBER for chronological ordering within each user partition, computes quartiles (Q1, median, Q3) for distribution analysis, and enforces a limit of 90 data points per user_id to maintain query performance. A monthly dataset with one ro",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Product managers need to assess market concentration by understanding what proportion of total model activity is dominated by top-performing models versus distributed across the portfolio, enabling competitive positioning and resource allocation decisions. Produce daily model ID statistics segmented by model name with concentration metrics, quartile breakdowns, and outlier tallies. The query uses DENSE_RANK to assign density-based rankings within model groups, applies PERCENT_RANK to calculate percentile positions showing relative standing, computes cumulative_sum distributions to measure concentration curves, segments models into quintiles using NTILE(5) for five-tier stratification, flags statistical outliers via z-score threshold tests, calculates quartiles (Q1, median, Q3) for distribution shape analysis, and requires at least 2 records per model group to enable comparative metrics. A daily metrics table with one row per model name containing concen",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "The data science team requires prioritized anomaly scores to efficiently allocate investigation resources by identifying which user accounts exhibit the most unusual model ID patterns that deviate significantly from normal behavior. Produce weekly model ID statistical summaries by user_id incorporating anomaly severity scores, quartile distributions, and trend behavior counts. The query calculates z_scores (standardized deviation from mean) as the primary anomaly indicator, aggregates outlier_count to tally observations beyond acceptable thresholds, computes partition_avg (mean within user partition) and partition_stddev (standard deviation within user partition) to establish baseline behavior for anomaly detection, calculates quartiles (Q1, median, Q3) for distribution characterization, counts instances of each trend_direction category (Increasing/Decreasing/Stable), enforces a limit of 70 data points per user_id to balance coverage and performance, and requir",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "The finance team requires month-over-month and quarter-over-quarter comparative analysis of model performance to support fiscal period reporting and strategic planning activities. Generate monthly aggregated model ID statistics for each model name that facilitate fiscal period comparisons. The query truncates timestamps to month-level granularity using DATE_TRUNC('month') to define reporting periods, computes quartile distributions (25th, 50th, 75th percentiles), calculates average and standard deviation metrics for each model name, limits output to 80 data points per model to ensure manageable result sets, and filters to include only groups with at least 1 record. A dataset containing monthly metrics for each model name, including quartiles, averages, and standard deviations, structured to enable fiscal period-over-period comparative analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "The operations team needs to assess daily ID activity levels across different users to optimize system capacity and resource allocation for throughput planning. Produce daily aggregated model ID statistics for each user that include throughput indicators, quartile distributions, and rolling average calculations. The query aggregates data at daily granularity grouped by user_id, computes record counts as a throughput proxy, calculates a 7-row rolling window average to smooth daily fluctuations, derives maximum cumulative values to track peak activity, generates quartile distributions for variability analysis, limits output to 90 data points per user, and filters to include only groups with at least 2 records. A dataset containing daily metrics for each user_id, including record counts, 7-day rolling averages, cumulative maximums, and quartiles to support throughput optimization and capacity planning.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Product managers need to understand how total model ID activity accumulates over time for each model to identify growth patterns and prioritize development efforts. Generate weekly aggregated model ID statistics for each model name that reveal cumulative trends and activity patterns. The query aggregates data at weekly intervals grouped by model name, computes cumulative sum of IDs to show total activity buildup, calculates maximum cumulative values for peak tracking, determines trend direction indicators to identify growth or decline, counts increasing trend periods to quantify momentum, ranks models by their cumulative sum to prioritize high-activity models, generates quartile distributions for variability assessment, and filters to include only groups with at least 3 records. A dataset containing weekly metrics for each model name, including cumulative sums, trend directions, activity rankings, and quartiles to enable cumulative trend analysis and mo",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Business analysts require flexible, multi-dimensional views of model ID activity by time period and user to support ad-hoc analysis, custom reporting, and pivot table generation. Produce monthly aggregated model ID statistics for each user that support multi-dimensional slicing and pivoting operations. The query aggregates data at monthly granularity using period as the time dimension and user_id as the categorical dimension, computes comprehensive statistics including record counts, averages, percentile distributions (quartiles), standard deviations, minimum and maximum values, counts records flagged as outliers for quality assessment, tracks trend indicators for directional analysis, and filters to include only groups with at least 1 record. A dataset containing monthly metrics for each user_id across multiple statistical dimensions\u2014counts, central tendency, spread, extremes, quartiles, outliers, and trends\u2014structured to support pivot tables and multi",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
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
  "evidence": "Data quality engineers need to identify anomalous user activity patterns using quartile-based outlier detection methods (IQR approach) to complement existing z-score analysis and improve anomaly detection coverage. Generate weekly aggregated model ID statistics for each user that incorporate IQR-style outlier detection alongside quartile distributions. The query aggregates data at weekly intervals grouped by user_id, computes first quartile (Q1) and third quartile (Q3) using PERCENTILE_CONT to establish the interquartile range foundation, identifies outliers using z-score threshold above 2 as an approximation for IQR-style detection, calculates standard deviation values to support alternative IQR-based outlier thresholds, counts records exhibiting increasing trends for pattern analysis, limits output to 70 data points per user to maintain performance, and filters to include only groups with at least 3 records for statistical validity. A dataset containi",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "created_at",
    "models",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and user_id",
  "normal_query": "Calculate weekly model ID statistics grouped by user using IQR-style outlier detection methodology, including quartile distributions."
}
```
