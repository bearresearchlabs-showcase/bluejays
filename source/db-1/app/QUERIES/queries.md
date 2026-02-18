# Chat/Messaging System — Query Documentation

## Database Overview

```yaml
db_id: db-1
domain: Chat / Messaging
source: [commercial]
license_type: [Commercial]
license_cost: [NDA]
tables: 12
total_rows: ~65
date_range: 2020-01-01 to 2026-12-31
sql_dialect: PostgreSQL
```

## Purpose

```text
This database supports analytics for chat and messaging platforms. It models user profiles,
conversations, messages, friend networks, notifications, file attachments, and anonymous
chat flows. It is designed to support text-to-SQL training across engagement, retention,
and operational query types commonly encountered in messaging product analytics.
```

## Use Case

```text
Target use cases for db-1:
- Engagement analytics: active users, message volume, chat participation rates
- Retention: friend networks, invitation flows, re-engagement patterns
- Operations: notification delivery, file attachment usage, anonymous chat metrics
- Product dashboards: conversation growth, AI vs human message mix, peak usage
```

## Business Value

```text
Messaging platforms represent high-value domains for text-to-SQL because:
- Queries require understanding of social graphs (friends, participants, invitations)
- Data relationships are complex (profile → chat → message → attachment chains)
- Stakeholders need self-serve analytics (product, growth, support teams)
- Evidence bridges natural-language questions to schema-grounded SQL.
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
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    join_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE anonymous_chat_users (
    guest_id UUID NOT NULL,
    chat_id UUID NOT NULL REFERENCES anonymous_chats(id),
    PRIMARY KEY (guest_id, chat_id)
);

CREATE TABLE anonymous_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES anonymous_chats(id),
    guest_id UUID NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inviting_user_id UUID NOT NULL REFERENCES profiles(id),
    invited_user_id UUID NOT NULL REFERENCES profiles(id),
    chat_id UUID NOT NULL REFERENCES chats(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aircraft position history (for time-series analytics queries)
CREATE TABLE aircraft_position_history (
    id SERIAL PRIMARY KEY,
    hex VARCHAR(20) NOT NULL,
    speed NUMERIC(10, 2),
    altitude NUMERIC(10, 2),
    timestamp TIMESTAMP NOT NULL
);
CREATE INDEX idx_aircraft_position_hex ON aircraft_position_history(hex);
CREATE INDEX idx_aircraft_position_timestamp ON aircraft_position_history(timestamp);

CREATE INDEX idx_messages_chat_id ON messages(chat_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_chat_participants_user_id ON chat_participants(user_id);
CREATE INDEX idx_friends_user_id ON friends(user_id);
CREATE INDEX idx_friends_friend_id ON friends(friend_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_file_attachments_chat_id ON file_attachments(chat_id);
```

## Domain Knowledge

```text
Key domain concepts required to write correct queries against this database:

CHAT AND MESSAGING:
- profiles: user accounts with username, email, display_name; id is UUID
- chats: conversation containers; created_by references profiles
- messages: individual messages in a chat; sender_id references profiles; is_ai flags AI-generated content
- chat_participants: many-to-many (chat_id, user_id); users must join to participate
- friends: bidirectional relationship; status is pending | accepted | declined

ANONYMOUS FLOWS:
- anonymous_chats: ephemeral chats without identity
- anonymous_chat_users: participants in anonymous chats
- anonymous_messages: messages in anonymous chats

INVITATIONS AND NOTIFICATIONS:
- chat_invitations: invite users to join chats
- notifications: delivery of alerts to users

ATTACHMENTS:
- file_attachments: links messages to uploaded files

AVIATION (aircraft_position_history):
- hex: ICAO 24-bit transponder code identifying aircraft
- altitude: feet; speed: knots (groundspeed)
- timestamp: when the position was recorded
- Rolling averages, z-scores, and quartiles are used for anomaly detection.
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
  "evidence": "The query constructs four CTEs. First, it retains the 60 most recent telemetry points per aircraft (cte_level_1). Second, it computes a 5-row rolling average and cumulative sum via window functions (cte_level_2). Third, it uses LAG, LEAD, and partition statistics for trend and z-score calculation (cte_level_3). Fourth, it flags outliers (z-score > 2) and trend direction, then aggregates by day and hex with PERCENTILE_CONT, SUM for outlier/increasing counts, and AVG for rolling average.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups telemetry by week and speed bucket. It divides altitude into sextiles (NTILE(6)), calculates z-scores per partition, flags outliers (>2 std dev), and uses LAG/LEAD to compare consecutive readings for trend direction. Aggregates include quartiles (PERCENTILE_CONT), outlier count, and increasing-trend count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by month and aircraft hex. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 6-row rolling average; flags outliers via z-score; and aggregates record count, stddev, min, max, outlier count, and increasing count. ROW_NUMBER limits to 80 points per aircraft.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by date and speed. It calculates running cumulative sum of altitude changes, applies a 7-row rolling window, uses NTILE(8) for distribution, and aggregates outlier count, increasing-trend count, and max cumulative sum per group.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by week and hex. It calculates STDDEV, PERCENTILE_CONT for quartiles, and uses LAG/LEAD with delta_value to derive trend_direction. Aggregates include record count, quartiles, stddev, outlier count, and increasing count. ROW_NUMBER limits to 100 points per aircraft.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by day and speed bucket. It computes z-scores (mean, stddev per partition; zero when stddev=0), flags outliers, calculates a 5-row rolling average, and filters to groups with \u22652 records. Output includes quartiles, rolling average, and outlier count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by month and hex. It captures min/max altitude, flags outliers (z-score > 2), limits to 80 points per aircraft, uses PERCENT_RANK, and calculates cumulative sum via window. Aggregates include quartiles, min, max, outlier count, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by day and hex. It uses LAG to get previous altitude, computes delta (current minus previous), derives trend_direction from the sign, and uses LEAD for next value. Aggregates include quartiles and sequential difference metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by day and speed bucket. It computes mean and stddev per group, flags anomalies (|z| > 2), handles stddev=0 safely, segments into octiles (NTILE(8)), and aggregates quartiles, outlier count, and trend direction counts.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by week and hex. It assigns ROW_NUMBER (desc timestamp) for recency scoring, uses record count as frequency proxy, ranks by cumulative sum, computes 6-row rolling average, and filters to groups with \u22653 records. Output includes quartiles and rolling average.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query treats each speed range as a cohort. It limits to 90 points per speed bucket, uses window functions for increasing_count and trend_direction (analogous to retention), and orders by time period and average value. Output includes cohort-style progression and quartile boundaries.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query uses LAG to create first derivative (altitude change). trend_direction captures sign of change. LAG and LEAD together enable second-order derivative (rate of change of rate). Z-scores flag outliers. Limited to 60 points per aircraft. Output includes change rate metrics, quartiles, and outlier count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query employs PERCENT_RANK for cross-category benchmarking and PERCENTILE_CONT for percentile values. Data segmented into sextiles. Speed categories ranked by cumulative altitude sum. Partition-level avg/stddev enable z-scores. Output includes percentile rankings and quartile distributions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query implements a 6-row rolling window for simple moving average (avg_rolling). It counts periods where altitude is increasing and flags statistical outliers. Limited to 80 points per aircraft, minimum 1 record per group. Output includes quartiles and trend pattern counts.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query ranks altitude within each day using window functions to identify peaks per speed category. Extracts hour and day-of-week for temporal analysis. Calculates max_cumulative and avg_rolling as efficiency proxies. Output includes peak period identification and quartile distributions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query computes cumulative_sum as total exposure proxy, tracks max_cumulative for lifetime activity, ranks aircraft by cumulative sum, applies PERCENT_RANK for quartile placement. Limited to 60 points per aircraft, \u22653 records per group. Output includes LTV metrics, quartiles, and cumulative totals.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query extracts hour_val and dow_val for temporal context. It uses window functions (rolling avg, cumulative sum, LAG, LEAD) and aggregates by period and hex. Output includes temporal correlation metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query segments by speed and time period. It uses PARTITION BY speed for window functions, groups by week and speed, and produces regime-specific aggregates including quartiles and trend counts.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query calculates STDDEV per partition as volatility measure. It uses PERCENTILE_CONT for quartiles and trend_direction for consistency. Aggregates include stddev, quartiles, outlier count, and increasing count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query uses PERCENT_RANK and PERCENTILE_CONT for cross-aircraft and cross-speed distribution comparison. DENSE_RANK and NTILE support benchmarking. Output includes percentile rankings and quartile distributions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query implements rolling windows (ROWS BETWEEN N PRECEDING AND CURRENT ROW) for moving average and cumulative sum. Window functions (LAG, LEAD, FIRST_VALUE, LAST_VALUE) support trend analysis. Output includes rolling and cumulative metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query partitions by speed and groups by day and speed. It combines temporal (DATE_TRUNC) and speed dimensions. Output includes speed-temporal segmented aggregates.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query uses PERCENTILE_CONT(0.25), (0.5), (0.75) for quartiles. NTILE provides distribution bins. Output includes q1, median, q3, and distribution shape metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query extracts EXTRACT(HOUR) and EXTRACT(DOW) for temporal features. It correlates these with altitude via partition and grouping. Output includes time-of-day correlation metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query uses PERCENT_RANK across partitions for cross-aircraft and cross-speed comparison. PERCENTILE_CONT and NTILE support distribution analysis. Output includes percentile rankings and quartile breakdowns.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query computes delta_value (current minus LAG) as first derivative. trend_direction (Increasing/Decreasing/Stable) captures sign. LAG+LEAD enable second derivative. Z-scores flag outliers. Output includes rate-of-change and acceleration-like metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups by week and speed. It aggregates altitude metrics per speed-temporal cell. Output includes regime-specific trend aggregates.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query computes cumulative_sum and max_cumulative. ROW_NUMBER (desc) scores recency. Record count proxies frequency. Output includes LTV-style and recency-frequency metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query uses PERCENTILE_CONT and PERCENT_RANK for distribution metrics. Groups by month and hex or speed. Output includes quartiles and percentile distributions across dimensions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query correlates altitude with period (day/week/month), hex, and speed. Multi-dimensional grouping and window functions (PARTITION BY hex, speed) produce cross-dimensional aggregates.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics grouped by week and speed",
  "normal_query": "Calculate weekly altitude statistics grouped by speed buckets using IQR-style outlier detection methodology with quartiles and trend indicators."
}
```


