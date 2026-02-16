# Chat/Messaging System — Query Documentation

## Database Overview

```yaml
db_id: db-1
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
This database supports analytics for db-1.
```

## Use Case

```text
Target use cases for db-1: analytics, reporting, dashboards.
```

## Business Value

```text
Business value for db-1.
```

## Schema

```sql
-- Chat Messaging Platform Schema (db-1)
-- Compatible with PostgreSQL
-- ACID-compliant: PKs and FKs for referential integrity

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255),
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID REFERENCES profiles(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(id),
    sender_id UUID NOT NULL REFERENCES profiles(id),
    is_ai BOOLEAN NOT NULL DEFAULT FALSE,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_participants (
    chat_id UUID NOT NULL REFERENCES chats(id),
    user_id UUID NOT NULL REFERENCES profiles(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (chat_id, user_id)
);

CREATE TABLE friends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id),
    friend_id UUID NOT NULL REFERENCES profiles(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id),
    type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read BOOLEAN DEFAULT FALSE,
    seen_at TIMESTAMP
);

CREATE TABLE file_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(id),
    user_id UUID NOT NULL REFERENCES profiles(id),
    file_name VARCHAR(255),
    file_type VARCHAR(100),
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE anonymous_chats (
    id UUID PRIMARY KEY DEFAULT gen_rand
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

### Query 1 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 1,
  "question": "How has aircraft altitude varied over the past year? I'd like to see rolling averages and outlier counts broken down by day and aircraft.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 60\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Fleet operators monitor ADS-B telemetry to track how aircraft altitude varies over time, helping them spot anomalies and identify maintenance needs before they become critical. Each aircraft transmits a unique ICAO 24-bit transponder hex code, and altitude is recorded in feet. Operators need daily summaries to detect unusual patterns that might indicate sensor drift, flight envelope excursions, or operational issues. Task: Produce daily aggregated altitude statistics for each aircraft, including rolling averages to smooth short-term fluctuations and outlier counts to flag abnormal readings. Action: The query constructs four common table expressions (CTEs). First, it retains the 60 most recent telemetry points per aircraft to limit memory usage. Second, it computes a 5-row rolling average of altitude for each aircraft to identify trends. Third, it flags statistical outliers by calculating z-scores and marking any reading that exceeds 2 standard deviations from the mean; when ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and hex",
  "normal_query": "Calculate daily altitude statistics for each aircraft over the last 365 days, including rolling averages and outlier counts."
}
```

### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 2,
  "question": "Can you show me weekly altitude statistics grouped by speed range? I need quartiles, outlier counts, and how many readings show an upward trend.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 70\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Flight analysts want to understand how altitude behavior differs across groundspeed ranges (measured in knots) to identify whether fast-flying aircraft exhibit different operational patterns than slower ones. For example, cruise-speed flight may show tighter altitude clustering, while climb or descent phases at different speeds may show more variability. This comparison helps optimize flight profiles and detect speed-related anomalies. Task: Produce weekly altitude statistics segmented by speed bucket, including quartiles to show distribution, counts of statistical outliers, and counts of readings that are trending upward. Action: The query groups telemetry by week and speed bucket. Within each speed bucket, it divides altitude readings into sextiles (six equal-frequency bins) to capture distribution shape. It calculates z-scores for each reading and flags those exceeding 2 standard deviations as outliers. Using the LAG and LEAD window functions, it compares each altitude re",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and speed",
  "normal_query": "Calculate weekly altitude statistics segmented by speed bucket, including quartiles, z-score-based outliers, and counts of increasing-trend readings."
}
```

### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 3,
  "question": "Give me monthly altitude summaries for each aircraft\u2014quartiles, median, outlier count, and rolling average.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 80\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Fleet managers produce monthly reports to track long-term altitude trends for each aircraft and identify seasonal or cyclical patterns that might affect operations. Monthly aggregation smooths out daily noise and reveals gradual shifts in flight behavior, such as changes in typical cruise altitude or increased variability that could indicate equipment degradation. These reports support strategic decisions about fleet deployment, maintenance scheduling, and route optimization. Task: Produce monthly altitude summaries for each aircraft, including quartiles to show distribution spread, median to identify the central tendency, outlier count to flag anomalies, and rolling average to reveal trends across months. Action: The query groups telemetry by month and aircraft hex code. For each group, it uses the PERCENTILE_CONT function to calculate the first quartile (Q1), median (Q2), and third quartile (Q3), providing a robust view of altitude distribution. It computes a 6-row rolling",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and hex",
  "normal_query": "Calculate monthly altitude statistics per aircraft hex code, including quartiles, median, outlier count, and rolling average."
}
```

### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 4,
  "question": "I need a daily altitude breakdown by speed\u2014how many outliers are there, how many readings are increasing, and what's the maximum cumulative sum?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 90\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Operations teams want to understand whether certain flight speed regimes\u2014such as cruise versus climb or descent\u2014exhibit more altitude anomalies or different trend behaviors. Daily breakdowns by speed help pinpoint whether specific phases of flight are associated with sensor issues, pilot technique variations, or airspace constraints. The cumulative sum metric helps identify which speed ranges accumulate the most altitude change, which can indicate workload or operational complexity. Task: Produce daily altitude statistics segmented by speed, including the count of outlier readings, the count of readings showing an increasing trend, and the peak cumulative sum of altitude changes within each speed bucket. Action: The query groups telemetry by date and speed. For each group, it calculates a running cumulative sum of altitude changes to track total vertical movement within that speed bucket. It applies a 7-row rolling window to compute moving statistics and divides altitude int",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and speed",
  "normal_query": "Calculate daily altitude statistics by speed, including outlier count, increasing-trend count, and maximum cumulative sum."
}
```

### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 5,
  "question": "Show me weekly altitude metrics for each aircraft\u2014record count, quartiles, standard deviation, and how many readings are trending upward.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 100\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Fleet analysts compare altitude variability and trend direction across aircraft on a weekly basis to identify which units are behaving normally and which may require attention. Standard deviation is a key indicator of altitude stability\u2014low standard deviation suggests consistent flight behavior, while high standard deviation may indicate erratic altitude changes due to turbulence, equipment issues, or unusual flight profiles. Combining variability measures with trend counts helps prioritize follow-up investigations. Task: Produce weekly altitude metrics for each aircraft, including the number of telemetry records, altitude quartiles to show distribution, standard deviation to quantify variability, and a count of readings where altitude is increasing to assess climb behavior. Action: The query groups telemetry by week and aircraft hex code. For each group, it calculates the standard deviation of altitude to measure dispersion around the mean, and computes quartiles (Q1, Q3) t",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and hex",
  "normal_query": "Calculate weekly altitude statistics per aircraft hex code, including record count, quartiles, standard deviation, and increasing-trend count."
}
```

### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 6,
  "question": "I need daily altitude statistics broken down by speed bucket, including quartiles, a rolling average, and a count of outlier readings.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 110\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Flight operations analysts monitor daily altitude patterns across different speed regimes to identify anomalies that may indicate instrumentation issues, unusual weather encounters, or non-standard flight profiles. Speed buckets help isolate behavior in climb, cruise, and descent phases. Task: Produce daily altitude statistics segmented by speed bucket, including quartile distributions, a rolling average for trend smoothing, and a count of statistical outliers. Action: The query groups records by calendar day and speed bucket, extracts hour and day-of-week for temporal context, computes z-scores for each altitude reading using the mean and standard deviation of the group (defaulting to zero when standard deviation is zero to prevent division errors), flags outliers as readings with absolute z-score above a threshold, calculates a 5-row rolling average of altitude to smooth short-term fluctuations, and filters to groups with at least 2 records to ensure statistical validity. ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and speed",
  "normal_query": "Compute daily altitude statistics grouped by speed bucket, including quartiles, rolling average, and z-score-based outlier count."
}
```

### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 7,
  "question": "I want a monthly altitude analysis for each aircraft hex code, including quartiles, minimum and maximum values, outlier count, and the maximum cumulative sum.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 120\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Fleet managers need monthly summaries of altitude performance for each aircraft to compare operational profiles, assess consistency across the fleet, and identify aircraft with unusual altitude distributions or high cumulative activity that may require maintenance review. Task: Produce monthly altitude statistics for each aircraft hex code, including quartile distributions, minimum and maximum altitudes, a count of statistical outliers, and the maximum value of a cumulative altitude sum. Action: The query groups records by month and aircraft hex code, captures the minimum and maximum altitude values to show the operational range, flags outliers as readings with z-score above 2 standard deviations from the group mean, limits analysis to the most recent 80 data points per aircraft to focus on recent behavior, computes PERCENT_RANK to understand each reading's relative position within the month, calculates a cumulative sum of altitude over time-ordered readings using a window f",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and hex",
  "normal_query": "Compute monthly altitude statistics per aircraft hex code with quartiles, minimum, maximum, outlier count, and maximum cumulative sum."
}
```

### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 8,
  "question": "I need daily altitude statistics by aircraft hex code showing gaps between consecutive readings, sequential altitude differences, and quartiles.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 130\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Safety analysts need to detect rapid altitude changes between consecutive readings for each aircraft, as sudden climbs or descents may indicate turbulence, emergency maneuvers, or data quality issues. Understanding the time gaps between readings also helps assess data continuity. Task: Produce daily altitude statistics for each aircraft hex code, including sequential differences between consecutive altitude readings and quartile distributions. Action: The query groups records by calendar day and aircraft hex code, orders readings chronologically by timestamp, uses the LAG window function to retrieve the previous altitude reading for each row (with the first reading per aircraft having no prior value and thus NULL), computes the altitude difference from the prior reading (current minus previous), derives a trend direction indicator from the sign of that difference (climbing, descending, or level), uses LAG to capture the previous altitude value and LEAD to capture the next al",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and speed",
  "normal_query": "Compute daily altitude statistics per aircraft hex code with sequential differences between consecutive readings, gap analysis, and quartiles."
}
```

### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 9,
  "question": "I need daily altitude statistics by speed bucket with z-score-based anomaly detection, quartiles, and counts of different trend directions.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 140\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Quality assurance teams monitor altitude behavior within specific speed regimes to detect anomalies such as unexpected altitude holds during high-speed segments or erratic altitude changes during approach speeds. Identifying statistical outliers helps flag data for manual review or operational investigation. Task: Produce daily altitude statistics segmented by speed bucket, including z-score-based anomaly detection, quartile distributions, and counts of increasing versus decreasing altitude trends. Action: The query groups records by calendar day and speed bucket, computes the mean and standard deviation of altitude for each group, flags anomalies as readings where altitude deviates by more than 2 standard deviations from the partition mean, safely handles cases where standard deviation is zero (preventing division errors by using a conditional check), segments the altitude distribution into octiles (8 equal-frequency bins) to understand the shape of the distribution, calcul",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and hex",
  "normal_query": "Compute daily altitude statistics grouped by speed bucket with z-score anomaly detection, quartiles, and trend direction counts."
}
```

### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 10,
  "question": "I want weekly altitude statistics by aircraft hex code with recency and frequency scoring, quartiles, and a rolling average.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 150\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Maintenance planners prioritize aircraft inspections based on activity patterns, using recency (how recently an aircraft was active) and frequency (how often it appears in the data) as key indicators. Aircraft that are both frequently active and recently observed may require earlier inspection scheduling. Task: Produce weekly altitude statistics for each aircraft hex code, incorporating recency-frequency style metrics along with quartile distributions and rolling averages. Action: The query groups records by calendar week and aircraft hex code, assigns a ROW_NUMBER to each reading ordered by timestamp descending to score recency (with 1 being the most recent reading), uses the total record count per aircraft per week as a frequency proxy to measure activity level, ranks aircraft by their cumulative sum of altitude to identify those with the highest total activity, computes a 6-row rolling average of altitude to smooth week-to-week variation, filters to groups with at least 3",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and speed",
  "normal_query": "Compute weekly altitude statistics per aircraft hex code with recency-frequency metrics, quartiles, and rolling average."
}
```

### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 11,
  "question": "What are the monthly altitude patterns across different speed ranges, analyzed like cohort retention with quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 160\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Aviation analysts need to understand how aircraft altitude behavior varies across different speed regimes over time, similar to how product teams track user cohorts, to identify performance patterns and anomalies in flight operations. Task: Generate monthly altitude statistics segmented by speed bucket with cohort-style progression metrics and quartile distributions. Action: The SQL query treats each speed range as a distinct cohort and tracks altitude as the primary metric. It limits the dataset to 90 data points per speed bucket for performance. Window functions calculate increasing_count to measure how many periods show growth (analogous to retention) and trend_direction to classify the movement pattern. Results are ordered by time period and average value to prioritize recent data and prominent patterns. Result: A dataset showing monthly altitude metrics for each speed cohort, including retention-style progression indicators, quartile boundaries (25th, 50th, 75th percent",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and hex",
  "normal_query": "Calculate monthly altitude statistics grouped by speed range, including cohort-style retention metrics and quartile breakdowns."
}
```

### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 12,
  "question": "What are the daily altitude change patterns for each aircraft, including acceleration-like metrics, quartiles, and outlier detection?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 170\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Flight safety analysts need to detect sudden altitude changes that might indicate emergency maneuvers, equipment issues, or unusual flight patterns. Tracking not just altitude changes (first derivative) but the acceleration of those changes (second derivative) helps identify critical events early. Task: Produce daily altitude statistics for each aircraft including change rate metrics, quartile distributions, and statistical outlier counts. Action: The SQL query computes altitude change from the previous reading using LAG to create a first derivative. The trend_direction field (Increasing/Decreasing) captures the sign of change. By combining LAG and LEAD window functions, the query enables calculation of previous and next values, which implicitly provides second-order derivative information (how the rate of change itself is changing). Statistical outliers are flagged using z-score thresholds, and results are limited to 60 data points per aircraft for manageability. Result: A ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and speed",
  "normal_query": "Calculate daily altitude statistics per aircraft hex code with rate-of-change metrics, quartile distributions, and outlier counts."
}
```

### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 13,
  "question": "How do weekly altitude distributions compare across speed categories, with percentile rankings and quartile breakdowns?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 180\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Aviation operations teams need to benchmark altitude patterns across different speed regimes to understand whether aircraft at cruise speed, climbing speed, or descending speed maintain appropriate altitude profiles relative to each other. This cross-category comparison helps identify operational inefficiencies or safety concerns. Task: Generate weekly altitude statistics segmented by speed with percentile-based benchmarking across categories and quartile distributions. Action: The SQL query employs PERCENT_RANK to calculate where each speed category falls relative to all others in altitude distribution, and PERCENTILE_CONT to compute precise percentile values for benchmarking. Data is segmented into sextiles (six equal groups) for granular distribution analysis. Speed categories are ranked by cumulative altitude sum to identify which regimes accumulate the most altitude exposure. Partition-level averages and standard deviations enable z-score calculations for cross-category",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and hex",
  "normal_query": "Calculate weekly altitude statistics by speed category with cross-category percentile benchmarking and quartile distributions."
}
```

### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 14,
  "question": "What are the monthly altitude trends for each aircraft using smoothed moving averages, with quartiles and trend pattern counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 190\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Aircraft maintenance teams and flight operations analysts need to identify underlying altitude trends for individual aircraft by filtering out short-term noise and volatility. Raw altitude readings can be erratic due to weather, air traffic control instructions, and normal flight operations, making trend detection difficult without smoothing techniques. Task: Produce monthly altitude statistics for each aircraft incorporating moving average smoothing, quartile distributions, and counts of trending periods. Action: The SQL query implements a 6-row rolling window to calculate a simple moving average of altitude readings, producing an avg_rolling metric that smooths out short-term fluctuations. The query counts periods where altitude is increasing to quantify upward trend frequency, and counts statistical outlier readings that fall outside normal ranges. Results are limited to 80 data points per aircraft for performance, with a minimum threshold of 1 record per aircraft group t",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and speed",
  "normal_query": "Calculate monthly altitude statistics per aircraft hex code with weighted moving averages, quartile distributions, and trend frequency counts."
}
```

### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 15,
  "question": "What are the daily peak altitude periods for each speed category, including efficiency metrics and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 200\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Air traffic management and capacity planning teams need to identify when aircraft in different speed categories reach peak altitudes each day. Understanding these peak periods helps optimize airspace utilization, predict congestion, and allocate resources effectively. Efficiency metrics tied to these peaks provide insights into operational performance. Task: Generate daily altitude statistics segmented by speed category with peak period identification and efficiency proxy metrics. Action: The SQL query ranks altitude readings within each day using window functions to identify peak values for each speed category. Temporal features are extracted including hour of day and day of week to enable pattern analysis across time dimensions. The query calculates max_cumulative (running maximum altitude) and avg_rolling (moving average) as proxy metrics for operational efficiency\u2014higher cumulative maximums and stable rolling averages suggest consistent, efficient altitude management. A ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and hex",
  "normal_query": "Calculate daily altitude statistics by speed category with peak period identification, operational efficiency metrics, and quartile distributions."
}
```

### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 16,
  "question": "What are the weekly altitude statistics for each aircraft with lifetime value metrics, quartiles, and cumulative totals?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 210\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The maintenance planning team needs to prioritize aircraft for scheduled inspections based on their total flight activity over time. Lifetime value (LTV) style metrics provide a clear ranking of aircraft by cumulative altitude exposure, helping allocate maintenance resources to the most heavily used aircraft first. Task: Generate weekly altitude statistics for each aircraft that include LTV-style activity metrics, quartile rankings, and cumulative measures. Action: The query computes cumulative_sum of altitude readings as a proxy for total exposure, tracks max_cumulative values to represent lifetime activity, ranks aircraft using cumulative sum ordering, applies PERCENT_RANK to determine which quartile each aircraft falls into for distribution analysis, limits output to 60 data points per aircraft to keep results manageable, and filters to include only aircraft groups with at least 3 records to ensure statistical validity. Result: Returns a dataset with one row per aircraft ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and speed",
  "normal_query": "Calculate weekly altitude statistics per aircraft including lifetime value metrics, quartile distribution, and cumulative sum analysis."
}
```

### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 17,
  "question": "How do monthly altitude patterns vary by speed range with year-over-year growth analysis and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 220\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Flight operations analysts need to understand how altitude behavior changes across different speed regimes year-over-year to identify trends in aircraft performance and operational patterns. Comparing the same months across consecutive years reveals whether altitude profiles are shifting due to route changes, aircraft aging, or operational adjustments. Task: Generate monthly altitude statistics segmented by speed range that include year-over-year style growth metrics and quartile distribution. Action: The query uses trend_direction and delta_value fields to calculate growth indicators comparing current month to prior year, employs the LAG window function to retrieve previous period values for comparison calculations, filters the dataset to the last 365 days to ensure exactly one year of comparison data is available, limits output to 90 data points per speed range to balance detail with performance, and computes quartile boundaries for distribution analysis. Result: Returns m",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and hex",
  "normal_query": "Calculate monthly altitude statistics grouped by speed range with year-over-year growth indicators and quartile distribution."
}
```

### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 18,
  "question": "What are the daily altitude statistics by aircraft for creating heatmap visualizations with quartiles and outliers?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 230\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The fleet operations dashboard requires heatmap visualizations that allow managers to quickly spot altitude anomalies and patterns across the entire fleet over time. Heatmaps provide an intuitive color-coded view where unusual altitude behavior stands out visually, enabling rapid identification of aircraft that may need attention. Task: Generate daily altitude statistics for each aircraft in a format optimized for heatmap rendering with quartile bands and outlier detection. Action: The query structures data with period (date) and aircraft hex as the two heatmap dimensions for x and y axes, calculates avg_value and record_count as the intensity metric that determines heatmap cell color, extracts hour and day-of-week components to enable alternative 2D heatmap views showing intraday and weekly patterns, flags outlier readings using z-score thresholds to highlight anomalous cells, orders results by period and avg_value for efficient rendering, and includes quartile calculations",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and speed",
  "normal_query": "Calculate daily altitude statistics per aircraft formatted for heatmap visualization including quartile ranges and outlier counts."
}
```

### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 19,
  "question": "What are the weekly altitude statistics by speed range showing running percentile distributions, quartiles, and trend patterns?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 240\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Performance analysts need to understand how altitude readings are distributed within each speed bucket over time to identify whether certain speed ranges consistently operate at different altitude bands. Running percentiles reveal the shape of the distribution and help detect whether altitude variability is increasing or decreasing within speed categories. Task: Generate weekly altitude statistics segmented by speed range that show running percentile positions, quartile boundaries, and counts of trend directions. Action: The query applies PERCENT_RANK to assign each reading a percentile position within its speed group for that week, uses PERCENTILE_CONT to calculate the actual quartile threshold values for distribution analysis, limits output to 70 data points per speed range to balance temporal resolution with query performance, counts the number of readings showing increasing trends versus stable or decreasing patterns, and flags outlier readings that fall outside normal d",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and hex",
  "normal_query": "Calculate weekly altitude statistics grouped by speed range with running percentile analysis, quartile distribution, and trend direction counts."
}
```

### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 20,
  "question": "What are the monthly altitude statistics by aircraft showing correlation patterns with prior readings, quartiles, and rolling averages?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 250\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The predictive maintenance team wants to identify whether altitude patterns for individual aircraft show correlation with their own historical readings, which could indicate degrading performance or systematic drift over time. Cross-correlation analysis reveals whether current altitude behavior is consistent with or diverging from past patterns for that specific aircraft. Task: Generate monthly altitude statistics for each aircraft that include correlation-style sequential metrics, quartile ranges, and rolling averages. Action: The query uses LAG and LEAD window functions to access prior and next period altitude values for sequential comparison, computes delta_value by comparing current readings to lagged values to measure period-over-period change, captures trend_direction to indicate whether altitude is increasing, stable, or decreasing relative to history, calculates partition_avg and partition_stddev within each aircraft group to enable standardization and correlation co",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and speed",
  "normal_query": "Calculate monthly altitude statistics per aircraft with cross-correlation style metrics, quartile distribution, and rolling average trends."
}
```

### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 21,
  "question": "What are the daily altitude statistics by speed category, including status transitions, quartile distributions, and outlier counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 260\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The aviation safety team needs to perform forensic analysis on how aircraft altitude states transition throughout the day. Understanding how altitude moves from Increasing to Decreasing or Stable status over time helps identify abnormal flight patterns and potential safety concerns. Task: Generate comprehensive daily altitude statistics segmented by speed category, incorporating status transition tracking, quartile distributions, and outlier identification. Action: The query treats trend_direction values (Increasing, Decreasing, Stable) as altitude status indicators and uses delta_value as the transition driver. It employs LAG and LEAD window functions to establish forensic sequencing of status changes, calculates z-scores to flag statistical outliers, and filters for groups with at least 2 records to ensure meaningful analysis. Result: A dataset containing daily metrics for each speed category, showing status transition sequences, quartile breakdowns (Q1, Q2/median, Q3), an",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and hex",
  "normal_query": "Calculate daily altitude statistics grouped by speed, including status transition analysis, quartile distributions, and outlier counts."
}
```

### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 22,
  "question": "What are the weekly altitude statistics by aircraft hex code with complete dashboard metrics including quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 270\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The fleet operations dashboard requires a comprehensive single-query data source that provides all essential monitoring metrics for the entire aircraft fleet. Operations managers need to view multiple statistical dimensions simultaneously to assess fleet health and performance trends. Task: Produce complete weekly altitude statistics for each aircraft, delivering all required dashboard metrics in a single result set. Action: The query performs a unified aggregation pass that calculates record_count, avg_value, all quartiles (Q1, Q2, Q3), standard deviation, minimum and maximum values, outlier_count, increasing_count (upward trend occurrences), avg_rolling (moving average), and max_cumulative (running maximum). It filters for groups containing at least 3 records to ensure statistical validity. Result: A comprehensive weekly metrics dataset for each aircraft hex code, containing the full dashboard metric suite with quartile distributions and all key statistical indicators.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and speed",
  "normal_query": "Generate weekly altitude statistics per aircraft hex identifier with full multi-metric aggregation including quartiles for dashboard display."
}
```

### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 23,
  "question": "What are the monthly altitude statistics by speed category showing sequential patterns and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 280\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The analytics team needs to understand how altitude values evolve over time within different speed ranges to identify flight pattern trends and anomalies. Sequential pattern mining helps reveal temporal dependencies and progression characteristics in altitude behavior across operating speeds. Task: Generate monthly altitude statistics segmented by speed category, incorporating sequential pattern analysis and quartile distributions. Action: The query leverages LAG and LEAD window functions to capture preceding and following values, uses delta_value and trend_direction to establish sequential relationships, applies ROWS BETWEEN frame specifications for windowed calculations, employs ROW_NUMBER for deterministic ordering, and limits each speed category to 90 data points to manage result size. Result: A monthly metrics dataset for each speed category, revealing sequential altitude patterns, temporal trends, and quartile distributions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and hex",
  "normal_query": "Calculate monthly altitude statistics grouped by speed with sequential pattern analysis metrics and quartile distributions."
}
```

### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 24,
  "question": "What are the daily altitude statistics by aircraft hex code including concentration indices, quartiles, and outlier counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 290\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Fleet managers need to understand activity concentration patterns to identify which aircraft account for the majority of operational activity. Concentration indices reveal whether activity is evenly distributed across the fleet or concentrated in specific aircraft, helping with resource allocation and maintenance planning. Task: Produce daily altitude statistics for each aircraft with concentration metrics, quartile distributions, and outlier identification. Action: The query computes concentration metrics using DENSE_RANK for positional ranking, PERCENT_RANK for percentile positioning, and cumulative_sum distribution to measure activity accumulation. It segments aircraft into five quintiles using NTILE(5) for stratification analysis, flags statistical outliers via z-score calculation, and requires at least 2 records per aircraft group for meaningful results. Result: A daily metrics dataset for each aircraft hex code, containing concentration indices that show activity distr",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and speed",
  "normal_query": "Generate daily altitude statistics per aircraft hex identifier with concentration index calculations, quartile distributions, and outlier counts."
}
```

### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 25,
  "question": "What are the weekly altitude statistics by speed category with anomaly scores, quartiles, and trend counts?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 300\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Operations analysts need to prioritize which speed categories require investigation due to unusual altitude behavior. Anomaly scoring provides a quantitative method to rank and filter speed buckets based on how significantly their altitude patterns deviate from expected norms, enabling efficient allocation of investigation resources. Task: Generate weekly altitude statistics for each speed category with calculated anomaly scores, quartile distributions, and trend frequency counts. Action: The query uses z_score as the primary anomaly detection metric, aggregates the count of outlier observations, computes partition-level average and standard deviation for benchmarking, limits each speed category to 70 data points for manageability, and requires at least 3 records per group to ensure statistical reliability. Result: A weekly metrics dataset for each speed category, containing anomaly scores for prioritization, quartile distributions for spread analysis, and counts of each tre",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and hex",
  "normal_query": "Calculate weekly altitude statistics grouped by speed, including statistical anomaly scores, quartile distributions, and trend direction counts."
}
```

### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 26,
  "question": "What are the monthly altitude statistics by aircraft with quartile breakdowns for fiscal period comparative reporting?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 310\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The finance and operations teams need to compare aircraft altitude performance across fiscal periods (month-over-month and quarter-over-quarter) to support budget planning, capacity forecasting, and operational variance analysis. Task: Generate comprehensive monthly altitude statistics for each aircraft that enable fiscal period comparative reporting with statistical depth. Action: The query truncates timestamps to monthly periods using DATE_TRUNC('month'), computes altitude quartiles (25th, 50th, 75th percentiles), average, and standard deviation for each aircraft hex identifier, limits output to 80 data points per aircraft to manage report size, and filters to include only aircraft groups with at least 1 recorded altitude measurement to ensure data validity. Result: A dataset containing monthly altitude metrics per aircraft including quartiles, mean, and standard deviation, formatted for fiscal period comparison dashboards and trend analysis reports.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and speed",
  "normal_query": "Calculate monthly altitude statistics for each aircraft hex identifier, including quartiles to support fiscal period comparison and month-over-month analysis."
}
```

### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 27,
  "question": "What are the daily altitude statistics grouped by speed range, including throughput indicators, quartiles, and rolling averages for optimization?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 320\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The capacity planning and network optimization teams need to understand how altitude activity is distributed across different speed ranges on a daily basis to optimize airspace throughput, identify bottlenecks, and allocate resources effectively. Task: Produce daily altitude statistics segmented by speed ranges that include throughput proxies, statistical distributions, and smoothed trend indicators. Action: The query groups altitude data by daily periods and speed buckets, calculates record_count as a volume throughput indicator, computes a 7-row rolling average (avg_rolling) to smooth daily volatility, tracks max_cumulative altitude to identify capacity ceilings, generates quartile statistics for distribution analysis, limits output to 90 data points per speed range for performance, and requires at least 2 records per speed group to ensure statistical reliability. Result: A comprehensive dataset of daily altitude metrics per speed range containing throughput volume indicat",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and hex",
  "normal_query": "Calculate daily altitude statistics segmented by speed buckets with throughput optimization metrics, quartile distributions, and 7-day rolling averages."
}
```

### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 28,
  "question": "What are the weekly cumulative altitude trends by aircraft with quartile analysis for pattern recognition?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 330\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Flight operations analysts need to monitor how total altitude activity accumulates over time for each aircraft to identify usage patterns, detect anomalies in flight behavior, and rank aircraft by operational intensity for maintenance scheduling and fleet management. Task: Generate weekly altitude statistics per aircraft that reveal cumulative trends, directional patterns, and relative activity rankings. Action: The query aggregates altitude data into weekly periods per aircraft hex identifier, calculates cumulative_sum to track total altitude accumulation over time, computes max_cumulative to identify peak activity levels, determines trend_direction (increasing/decreasing) and counts consecutive increasing periods (increasing_count) for pattern recognition, ranks aircraft by their cumulative altitude sum to identify most active units, generates quartile statistics for distribution analysis, and requires at least 3 records per aircraft group to ensure trend validity. Result:",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by month and speed",
  "normal_query": "Calculate weekly altitude statistics for each aircraft hex with cumulative trend analysis, activity ranking, and quartile distributions."
}
```

### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 29,
  "question": "What are the monthly altitude statistics segmented by speed range with multi-dimensional aggregation and quartiles for pivot analysis?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 340\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Business intelligence and analytics teams require flexible, multi-dimensional altitude data that can be pivoted, sliced, and diced by both time period and speed range to support ad-hoc analysis, executive dashboards, and custom reporting requirements across different operational and strategic use cases. Task: Produce monthly altitude statistics segmented by speed ranges with comprehensive multi-dimensional aggregations suitable for pivot table analysis and cross-dimensional slicing. Action: The query creates a two-dimensional aggregation using monthly period (DATE_TRUNC) and speed bucket as primary dimensions, calculates extensive statistics including record count, average altitude, all percentiles (quartiles: 25th, 50th, 75th), standard deviation, minimum and maximum values, outlier counts to identify anomalies, and trend counts to capture directional changes, and requires at least 1 record per dimension combination to include all possible segments. Result: A fully-dimensio",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by day and hex",
  "normal_query": "Calculate monthly altitude statistics grouped by speed buckets with comprehensive multi-dimensional aggregations and quartile distributions to support flexible pivot reporting."
}
```

### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 30,
  "question": "What are the weekly altitude statistics by speed range with IQR-based outlier detection and quartile analysis?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 350\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Data quality and safety analysts need robust outlier detection in weekly altitude data segmented by speed to identify unusual flight patterns, potential sensor errors, or safety concerns, using the Interquartile Range (IQR) method which is less sensitive to extreme values than z-score approaches and provides more interpretable thresholds based on data distribution. Task: Generate weekly altitude statistics per speed range with IQR-methodology outlier detection and supporting quartile measures. Action: The query groups altitude data into weekly periods and speed buckets, calculates precise quartiles using PERCENTILE_CONT for Q1 (25th percentile) and Q3 (75th percentile) which form the basis of IQR calculation, identifies potential outliers using z-score threshold above 2 standard deviations as an approximation of the IQR 1.5\u00d7IQR rule, computes standard deviation (stddev_value) to support alternative IQR-based outlier formulas, includes trend counts to track directional patter",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "timestamp",
    "aircraft_position_history",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and speed",
  "normal_query": "Calculate weekly altitude statistics grouped by speed buckets using IQR-style outlier detection methodology with quartiles and trend indicators."
}
```
