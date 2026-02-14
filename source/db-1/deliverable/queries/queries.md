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
  "question": "Multi-Window Time-Series Analysis with Rolling Aggregates",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 60\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for multi-window time-series analysis with rolling aggregates Business Value: Actionable insights from multi-window time-series analysis with rolling aggregates Purpose: Production multi-window time-series analysis with rolling aggregates analysis Complexity: 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by ",
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
  "expected_output": "Aggregated metrics grouped by day and hex"
}
```

### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 2,
  "question": "Segmentation Analysis with Decile Ranking",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 70\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for segmentation analysis with decile ranking Business Value: Actionable insights from segmentation analysis with decile ranking Purpose: Production segmentation analysis with decile ranking analysis Complexity: 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and speed",
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
  "expected_output": "Aggregated metrics grouped by week and speed"
}
```

### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 3,
  "question": "Performance Quartile Distribution",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 80\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for performance quartile distribution Business Value: Actionable insights from performance quartile distribution Purpose: Production performance quartile distribution analysis Complexity: 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and hex",
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
  "expected_output": "Aggregated metrics grouped by month and hex"
}
```

### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 4,
  "question": "Category Revenue Distribution Analysis",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 90\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for category revenue distribution analysis Business Value: Actionable insights from category revenue distribution analysis Purpose: Production category revenue distribution analysis analysis Complexity: 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and speed",
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
  "expected_output": "Aggregated metrics grouped by day and speed"
}
```

### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 5,
  "question": "Velocity and Acceleration Metrics",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 100\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for velocity and acceleration metrics Business Value: Actionable insights from velocity and acceleration metrics Purpose: Production velocity and acceleration metrics analysis Complexity: 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and hex",
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
  "expected_output": "Aggregated metrics grouped by week and hex"
}
```

### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 6,
  "question": "Hourly Pattern Detection and Clustering",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 110\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for hourly pattern detection and clustering Business Value: Actionable insights from hourly pattern detection and clustering Purpose: Production hourly pattern detection and clustering analysis Complexity: 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and speed",
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
  "expected_output": "Aggregated metrics grouped by day and speed"
}
```

### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 7,
  "question": "Gap Analysis with Sequential Difference",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 120\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for gap analysis with sequential difference Business Value: Actionable insights from gap analysis with sequential difference Purpose: Production gap analysis with sequential difference analysis Complexity: 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and hex",
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
  "expected_output": "Aggregated metrics grouped by month and hex"
}
```

### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 8,
  "question": "Anomaly Detection Using Z-Score Windows",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 130\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for anomaly detection using z-score windows Business Value: Actionable insights from anomaly detection using z-score windows Purpose: Production anomaly detection using z-score windows analysis Complexity: 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and speed",
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
  "expected_output": "Aggregated metrics grouped by day and speed"
}
```

### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 9,
  "question": "Recency-Frequency Scoring Model",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 140\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for recency-frequency scoring model Business Value: Actionable insights from recency-frequency scoring model Purpose: Production recency-frequency scoring model analysis Complexity: 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and hex",
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
  "expected_output": "Aggregated metrics grouped by week and hex"
}
```

### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 10,
  "question": "Multi-Period Cohort Retention Analysis",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 150\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for multi-period cohort retention analysis Business Value: Actionable insights from multi-period cohort retention analysis Purpose: Production multi-period cohort retention analysis analysis Complexity: 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and speed",
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
  "expected_output": "Aggregated metrics grouped by month and speed"
}
```

### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 11,
  "question": "Second-Order Derivative Computation",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 160\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for second-order derivative computation Business Value: Actionable insights from second-order derivative computation Purpose: Production second-order derivative computation analysis Complexity: 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and hex",
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
  "expected_output": "Aggregated metrics grouped by day and hex"
}
```

### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 12,
  "question": "Cross-Category Benchmarking with Percentiles",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 170\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for cross-category benchmarking with percentiles Business Value: Actionable insights from cross-category benchmarking with percentiles Purpose: Production cross-category benchmarking with percentiles analysis Complexity: 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and speed",
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
  "expected_output": "Aggregated metrics grouped by week and speed"
}
```

### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 13,
  "question": "Weighted Moving Average Pipeline",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 180\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for weighted moving average pipeline Business Value: Actionable insights from weighted moving average pipeline Purpose: Production weighted moving average pipeline analysis Complexity: 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and hex",
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
  "expected_output": "Aggregated metrics grouped by month and hex"
}
```

### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 14,
  "question": "Peak Period Identification and Efficiency",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 190\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for peak period identification and efficiency Business Value: Actionable insights from peak period identification and efficiency Purpose: Production peak period identification and efficiency analysis Complexity: 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and speed",
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
  "expected_output": "Aggregated metrics grouped by day and speed"
}
```

### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 15,
  "question": "Lifetime Value Estimation Model",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 200\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for lifetime value estimation model Business Value: Actionable insights from lifetime value estimation model Purpose: Production lifetime value estimation model analysis Complexity: 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and hex",
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
  "expected_output": "Aggregated metrics grouped by week and hex"
}
```

### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 16,
  "question": "Year-over-Year Growth Rate Analysis",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 210\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for year-over-year growth rate analysis Business Value: Actionable insights from year-over-year growth rate analysis Purpose: Production year-over-year growth rate analysis analysis Complexity: 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and speed",
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
  "expected_output": "Aggregated metrics grouped by month and speed"
}
```

### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 17,
  "question": "Heatmap Data Generation by Dimensions",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 220\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for heatmap data generation by dimensions Business Value: Actionable insights from heatmap data generation by dimensions Purpose: Production heatmap data generation by dimensions analysis Complexity: 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and hex",
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
  "expected_output": "Aggregated metrics grouped by day and hex"
}
```

### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 18,
  "question": "Running Percentile Distribution",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 230\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for running percentile distribution Business Value: Actionable insights from running percentile distribution Purpose: Production running percentile distribution analysis Complexity: 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and speed",
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
  "expected_output": "Aggregated metrics grouped by week and speed"
}
```

### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 19,
  "question": "Cross-Correlation Pattern Analysis",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 240\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for cross-correlation pattern analysis Business Value: Actionable insights from cross-correlation pattern analysis Purpose: Production cross-correlation pattern analysis analysis Complexity: 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and hex",
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
  "expected_output": "Aggregated metrics grouped by month and hex"
}
```

### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 20,
  "question": "Status Transition Forensic Analysis",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 250\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for status transition forensic analysis Business Value: Actionable insights from status transition forensic analysis Purpose: Production status transition forensic analysis analysis Complexity: 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and speed",
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
  "expected_output": "Aggregated metrics grouped by day and speed"
}
```

### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 21,
  "question": "Multi-Metric Dashboard Aggregation",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 260\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for multi-metric dashboard aggregation Business Value: Actionable insights from multi-metric dashboard aggregation Purpose: Production multi-metric dashboard aggregation analysis Complexity: 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and hex",
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
  "expected_output": "Aggregated metrics grouped by week and hex"
}
```

### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 22,
  "question": "Sequential Pattern Mining with Windows",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 270\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for sequential pattern mining with windows Business Value: Actionable insights from sequential pattern mining with windows Purpose: Production sequential pattern mining with windows analysis Complexity: 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and speed",
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
  "expected_output": "Aggregated metrics grouped by month and speed"
}
```

### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 23,
  "question": "Concentration Index Computation",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 280\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for concentration index computation Business Value: Actionable insights from concentration index computation Purpose: Production concentration index computation analysis Complexity: 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and hex",
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
  "expected_output": "Aggregated metrics grouped by day and hex"
}
```

### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 24,
  "question": "Statistical Anomaly Score Assignment",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 290\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for statistical anomaly score assignment Business Value: Actionable insights from statistical anomaly score assignment Purpose: Production statistical anomaly score assignment analysis Complexity: 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and speed",
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
  "expected_output": "Aggregated metrics grouped by week and speed"
}
```

### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 25,
  "question": "Fiscal Period Comparative Reporting",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 300\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for fiscal period comparative reporting Business Value: Actionable insights from fiscal period comparative reporting Purpose: Production fiscal period comparative reporting analysis Complexity: 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and hex",
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
  "expected_output": "Aggregated metrics grouped by month and hex"
}
```

### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 26,
  "question": "Throughput Optimization Metrics",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 310\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for throughput optimization metrics Business Value: Actionable insights from throughput optimization metrics Purpose: Production throughput optimization metrics analysis Complexity: 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and speed",
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
  "expected_output": "Aggregated metrics grouped by day and speed"
}
```

### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 27,
  "question": "Cumulative Trend Analysis Pipeline",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 320\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for cumulative trend analysis pipeline Business Value: Actionable insights from cumulative trend analysis pipeline Purpose: Production cumulative trend analysis pipeline analysis Complexity: 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and hex",
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
  "expected_output": "Aggregated metrics grouped by week and hex"
}
```

### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 28,
  "question": "Multi-Dimensional Pivot Aggregation",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 330\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping. Use Case: Business analytics for multi-dimensional pivot aggregation Business Value: Actionable insights from multi-dimensional pivot aggregation Purpose: Production multi-dimensional pivot aggregation analysis Complexity: 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by month and speed",
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
  "expected_output": "Aggregated metrics grouped by month and speed"
}
```

### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 29,
  "question": "Funnel Stage Progression Tracking",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 340\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.timestamp) AS period,\n    c4.hex,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping. Use Case: Business analytics for funnel stage progression tracking Business Value: Actionable insights from funnel stage progression tracking Purpose: Production funnel stage progression tracking analysis Complexity: 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by day and hex",
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
  "expected_output": "Aggregated metrics grouped by day and hex"
}
```

### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-1",
  "question_id": 30,
  "question": "Outlier Detection with IQR Method",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,\n        DATE_TRUNC('day', timestamp) AS day_bucket,\n        DATE_TRUNC('week', timestamp) AS week_bucket,\n        EXTRACT(HOUR FROM timestamp) AS hour_val,\n        EXTRACT(DOW FROM timestamp) AS dow_val\n    FROM aircraft_position_history\n    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,\n        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,\n        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 350\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,\n        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,\n        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,\n        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,\n        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.timestamp) AS period,\n    c4.speed,\n    COUNT(*) AS record_count,\n    AVG(c4.altitude) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,\n    STDDEV(c4.altitude) AS stddev_value,\n    MIN(c4.altitude) AS min_value,\n    MAX(c4.altitude) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Description: Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping. Use Case: Business analytics for outlier detection with iqr method Business Value: Actionable insights from outlier detection with iqr method Purpose: Production outlier detection with iqr method analysis Complexity: 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic Expected Output: Aggregated metrics grouped by week and speed",
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
  "expected_output": "Aggregated metrics grouped by week and speed"
}
```
