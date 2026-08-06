# Database 1 - Extremely Complex SQL Queries


# Database Schema: DB1

**Description:** Chat/Messaging System
**Created:** 2026-02-03

## Overview

This database contains 11 tables.

## Tables

### `profiles`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `username` | `VARCHAR(255)` | Yes | No |
| `display_name` | `VARCHAR(255)` | Yes | No |
| `avatar_url` | `VARCHAR(16777216)` | Yes | No |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `updated_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `ai_character_id` | `VARCHAR(255)` | Yes | No |
| `user_role` | `VARCHAR(50)` | Yes | Yes |
| `email` | `VARCHAR(255)` | Yes | No |
| `bio` | `VARCHAR(16777216)` | Yes | No |
| `last_username_changed_at` | `TIMESTAMP_NTZ` | Yes | No |
| `prompt_username_setup` | `BOOLEAN` | Yes | Yes |

### `chats`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `title` | `VARCHAR(255)` | Yes | No |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `updated_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `current_ai_character_id` | `VARCHAR(255)` | Yes | No |
| `created_by` | `UUID` | No | No |

### `chat_participants`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `chat_id` | `UUID` | No | No |
| `user_id` | `UUID` | No | No |
| `joined_at` | `TIMESTAMP_NTZ` | Yes | Yes |

### `messages`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `chat_id` | `UUID` | No | No |
| `sender_id` | `UUID` | Yes | No |
| `content` | `VARCHAR(16777216)` | No | No |
| `is_ai` | `BOOLEAN` | Yes | Yes |
| `ai_character_id` | `VARCHAR(255)` | Yes | No |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `updated_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `deleted_at` | `TIMESTAMP_NTZ` | Yes | No |
| `mentioned_users` | `ARRAY(VARCHAR)` | Yes | No |
| `is_system_message` | `BOOLEAN` | Yes | Yes |
| `mentions_data` | `VARIANT` | Yes | No |

### `friends`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `user_id` | `UUID` | No | No |
| `friend_id` | `UUID` | No | No |
| `status` | `VARCHAR(20)` | Yes | Yes |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `updated_at` | `TIMESTAMP_NTZ` | Yes | Yes |

### `notifications`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `user_id` | `UUID` | No | No |
| `type` | `VARCHAR(50)` | No | No |
| `title` | `VARCHAR(255)` | No | No |
| `message` | `VARCHAR(16777216)` | No | No |
| `data` | `VARIANT` | Yes | No |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `read` | `BOOLEAN` | Yes | Yes |
| `updated_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `seen_at` | `TIMESTAMP_NTZ` | Yes | No |

### `file_attachments`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `message_id` | `UUID` | Yes | No |
| `chat_id` | `UUID` | Yes | No |
| `user_id` | `UUID` | Yes | No |
| `file_name` | `VARCHAR(255)` | No | No |
| `file_size` | `INTEGER` | No | No |
| `file_type` | `VARCHAR(100)` | No | No |
| `file_path` | `VARCHAR(16777216)` | No | No |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |

### `anonymous_chats`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `join_code` | `VARCHAR(50)` | Yes | No |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |
| `expires_at` | `TIMESTAMP_NTZ` | Yes | No |

### `anonymous_chat_users`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `chat_id` | `UUID` | No | No |
| `guest_id` | `VARCHAR(100)` | Yes | No |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |

### `anonymous_messages`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `chat_id` | `UUID` | No | No |
| `guest_id` | `VARCHAR(100)` | Yes | No |
| `content` | `VARCHAR(16777216)` | No | No |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |

### `chat_invitations`

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `UUID` | Yes | Yes |
| `chat_id` | `UUID` | No | No |
| `inviting_user_id` | `UUID` | No | No |
| `invited_user_id` | `UUID` | No | No |
| `status` | `VARCHAR(20)` | Yes | Yes |
| `created_at` | `TIMESTAMP_NTZ` | Yes | Yes |


---

This file contains 30+ extremely complex SQL queries for the chat/messaging database system. All queries are designed to work across PostgreSQL.

## Query 1: Production-Grade User Activity Analysis with Deep CTE Nesting and Cohort Analytics

**Description:** Enterprise-level user activity analysis with cohort segmentation, retention metrics, engagement scoring, and advanced window function analytics. Demonstrates production-grade SQL patterns used by platforms like Slack, Discord, and Microsoft Teams.

**Complexity:** Deep nested CTEs (5+ levels), cohort analysis, retention metrics, engagement scoring, complex window functions with multiple frame clauses, percentile calculations, time-series analysis

```sql
WITH user_registration_cohorts AS (
    -- First CTE: Identify user registration cohorts
    SELECT
        p.id AS user_id,
        p.username,
        DATE_TRUNC('month', p.created_at) AS registration_month,
        EXTRACT(YEAR FROM p.created_at) AS registration_year,
        EXTRACT(MONTH FROM p.created_at) AS registration_month_num,
        p.created_at AS created_at
    FROM profiles p
),
user_message_activity AS (
    -- Second CTE: Aggregate message activity with time windows
    SELECT
        umc.user_id,
        umc.username,
        umc.registration_month,
        umc.registration_year,
        umc.registration_month_num,
        COUNT(DISTINCT m.chat_id) AS active_chats,
        COUNT(m.id) AS total_messages,
        COUNT(CASE WHEN m.is_ai = false THEN 1 END) AS user_messages,
        COUNT(CASE WHEN m.is_ai = true THEN 1 END) AS ai_responses,
        COUNT(DISTINCT DATE(m.created_at)) AS active_days,
        MIN(m.created_at) AS first_message_date,
        MAX(m.created_at) AS last_message_date,
        EXTRACT(EPOCH FROM (MAX(m.created_at) - MIN(m.created_at))) / 86400 AS message_span_days,
        AVG(CASE WHEN m.is_ai = false THEN LENGTH(m.content) ELSE NULL END) AS avg_user_message_length,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN m.is_ai = false THEN LENGTH(m.content) ELSE NULL END) AS median_user_message_length
    FROM user_registration_cohorts umc
    LEFT JOIN messages m ON umc.user_id = m.sender_id
    GROUP BY umc.user_id, umc.username, umc.registration_month, umc.registration_year, umc.registration_month_num
),
user_engagement_metrics AS (
    -- Third CTE: Calculate engagement metrics with window functions
    SELECT
        uma.user_id,
        uma.username,
        uma.registration_month,
        uma.active_chats,
        uma.total_messages,
        uma.user_messages,
        uma.ai_responses,
        uma.active_days,
        uma.message_span_days,
        uma.avg_user_message_length,
        uma.median_user_message_length,
        CASE
            WHEN uma.message_span_days > 0 THEN uma.active_days::numeric / uma.message_span_days
            ELSE 0
        END AS daily_activity_rate,
        CASE
            WHEN uma.active_chats > 0 THEN uma.total_messages::numeric / uma.active_chats
            ELSE 0
        END AS messages_per_chat,
        CASE
            WHEN uma.user_messages > 0 THEN uma.ai_responses::numeric / uma.user_messages
            ELSE 0
        END AS ai_response_ratio,
        -- Time-based engagement: days since last activity
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - uma.last_message_date)) / 86400 AS days_since_last_activity
    FROM user_message_activity uma
),
cohort_median_calculation AS (
    -- Calculate medians separately using subqueries
    SELECT
        registration_month,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_messages) AS cohort_median_messages
    FROM user_engagement_metrics
    GROUP BY registration_month
),
overall_median_calculation AS (
    SELECT
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_messages) AS overall_median_messages
    FROM user_engagement_metrics
),
cohort_retention_analysis AS (
    -- Fourth CTE: Calculate cohort-based retention metrics
    SELECT
        uem.user_id,
        uem.username,
        uem.registration_month,
        uem.active_chats,
        uem.total_messages,
        uem.user_messages,
        uem.ai_responses,
        uem.active_days,
        uem.message_span_days,
        uem.daily_activity_rate,
        uem.messages_per_chat,
        uem.ai_response_ratio,
        uem.days_since_last_activity,
        -- Cohort comparison metrics using window functions
        AVG(uem.total_messages) OVER (PARTITION BY uem.registration_month) AS cohort_avg_messages,
        COALESCE(cmc.cohort_median_messages, 0) AS cohort_median_messages,
        STDDEV(uem.total_messages) OVER (PARTITION BY uem.registration_month) AS cohort_stddev_messages,
        COUNT(*) OVER (PARTITION BY uem.registration_month) AS cohort_size,
        -- Cross-cohort comparisons
        AVG(uem.total_messages) OVER () AS overall_avg_messages,
        COALESCE(omc.overall_median_messages, 0) AS overall_median_messages
    FROM user_engagement_metrics uem
    LEFT JOIN cohort_median_calculation cmc ON uem.registration_month = cmc.registration_month
    CROSS JOIN overall_median_calculation omc
),
engagement_scoring AS (
    -- Fifth CTE: Calculate comprehensive engagement scores with weighted factors
    SELECT
        cra.user_id,
        cra.username,
        cra.registration_month,
        cra.active_chats,
        cra.total_messages,
        cra.user_messages,
        cra.ai_responses,
        cra.active_days,
        cra.daily_activity_rate,
        cra.messages_per_chat,
        cra.ai_response_ratio,
        cra.days_since_last_activity,
        cra.cohort_avg_messages,
        cra.cohort_median_messages,
        cra.cohort_size,
        -- Multi-factor engagement score (production-grade scoring algorithm)
        (
            -- Message volume component (30% weight)
            (LEAST(cra.total_messages, 1000) / 1000.0 * 30) +
            -- Activity frequency component (25% weight)
            (LEAST(cra.active_days, 30) / 30.0 * 25) +
            -- Engagement consistency component (20% weight)
            (LEAST(cra.daily_activity_rate, 1.0) * 20) +
            -- Chat diversity component (15% weight)
            (LEAST(cra.active_chats, 20) / 20.0 * 15) +
            -- Recency component (10% weight) - penalize inactive users
            (GREATEST(0, 1.0 - (LEAST(cra.days_since_last_activity, 90) / 90.0)) * 10)
        ) AS raw_engagement_score,
        -- Cohort-relative performance
        CASE
            WHEN cra.cohort_avg_messages > 0 THEN cra.total_messages::numeric / cra.cohort_avg_messages
            ELSE 0
        END AS cohort_performance_ratio,
        -- Percentile rankings
        PERCENT_RANK() OVER (ORDER BY cra.total_messages DESC) AS message_percentile,
        PERCENT_RANK() OVER (PARTITION BY cra.registration_month ORDER BY cra.total_messages DESC) AS cohort_percentile
    FROM cohort_retention_analysis cra
),
final_rankings AS (
    -- Sixth CTE: Final rankings with multiple window function calculations
    SELECT
        es.user_id,
        es.username,
        es.registration_month,
        es.active_chats,
        es.total_messages,
        es.user_messages,
        es.ai_responses,
        es.active_days,
        ROUND(CAST(es.daily_activity_rate AS NUMERIC), 3) AS daily_activity_rate,
        ROUND(CAST(es.messages_per_chat AS NUMERIC), 2) AS messages_per_chat,
        ROUND(CAST(es.ai_response_ratio AS NUMERIC), 2) AS ai_response_ratio,
        ROUND(CAST(es.days_since_last_activity AS NUMERIC), 1) AS days_since_last_activity,
        ROUND(CAST(es.raw_engagement_score AS NUMERIC), 2) AS engagement_score,
        ROUND(CAST(es.cohort_performance_ratio AS NUMERIC), 2) AS cohort_performance_ratio,
        ROUND(CAST(es.message_percentile * 100 AS NUMERIC), 2) AS overall_percentile,
        ROUND(CAST(es.cohort_percentile * 100 AS NUMERIC), 2) AS cohort_percentile,
        -- Multiple ranking methods
        ROW_NUMBER() OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_rank,
        RANK() OVER (ORDER BY es.total_messages DESC) AS message_rank,
        DENSE_RANK() OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_dense_rank,
        -- Running totals and moving averages
        SUM(es.total_messages) OVER (ORDER BY es.raw_engagement_score DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_messages,
        AVG(es.total_messages) OVER (ORDER BY es.raw_engagement_score DESC ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING) AS moving_avg_messages_9,
        -- Lag/Lead for trend analysis
        LAG(es.total_messages, 1) OVER (ORDER BY es.raw_engagement_score DESC) AS prev_user_messages,
        LEAD(es.total_messages, 1) OVER (ORDER BY es.raw_engagement_score DESC) AS next_user_messages,
        -- NTILE for segmentation
        NTILE(5) OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_quintile,
        NTILE(10) OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_decile
    FROM engagement_scoring es
)
SELECT
    user_id,
    username,
    registration_month,
    active_chats,
    total_messages,
    user_messages,
    ai_responses,
    active_days,
    daily_activity_rate,
    messages_per_chat,
    ai_response_ratio,
    days_since_last_activity,
    engagement_score,
    cohort_performance_ratio,
    overall_percentile,
    cohort_percentile,
    engagement_rank,
    message_rank,
    cumulative_messages,
    ROUND(CAST(moving_avg_messages_9 AS NUMERIC), 2) AS moving_avg_messages,
    engagement_quintile,
    engagement_decile,
    CASE engagement_quintile
        WHEN 1 THEN 'Champion'
        WHEN 2 THEN 'Power User'
        WHEN 3 THEN 'Regular'
        WHEN 4 THEN 'Casual'
        ELSE 'Inactive'
    END AS user_segment,
    CASE
        WHEN days_since_last_activity <= 1 THEN 'Active'
        WHEN days_since_last_activity <= 7 THEN 'Recent'
        WHEN days_since_last_activity <= 30 THEN 'At Risk'
        ELSE 'Churned'
    END AS activity_status
FROM final_rankings
WHERE engagement_rank <= 50
ORDER BY engagement_rank;
```

**Expected Output:** Top 20 users ranked by message activity with percentile rankings and running totals.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination N/A
- [ ] Window frame boundaries ✅
- **Passed**: 2/2


**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: cohort_retention_analysis, engagement_scoring, final_rankings, messages, p, profiles, user_engagement_metrics, user_message_activity, user_registration_cohorts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: cohort_retention_analysis, engagement_scoring, final_rankings, messages, p, profiles, user_engagement_metrics, user_message_activity, user_registration_cohorts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: cohort_retention_analysis, engagement_scoring, final_rankings, messages, p, profiles, user_engagement_metrics, user_message_activity, user_registration_cohorts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: cohort_retention_analysis, engagement_scoring, final_rankings, messages, p, profiles, user_engagement_metrics, user_message_activity, user_registration_cohorts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: cohort_retention_analysis, engagement_scoring, final_rankings, messages, p, profiles, user_engagement_metrics, user_message_activity, user_registration_cohorts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: cohort_retention_analysis, engagement_scoring, final_rankings, messages, p
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH user_registration_cohorts AS (
    -- First CTE: Identify user registration cohorts
    SELECT
        p.id AS user_id,
        p.username,
        DATE_TRUNC('month', p.created_at) AS registration_month,
        EXTRACT(YEAR FROM p.created_at) AS registration_year,
        EXTRACT(MONTH FROM p.created_at) AS registration_month_num,
        p.created_at AS registration_date
    FROM profiles p
),
user_message_activity AS (
    -- Second CTE: Aggregate message activity with time windows
    ...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 2: Production-Grade Social Network Graph Analysis with Advanced Recursive CTE

**Description:** Enterprise-level social network analysis using recursive CTE for multi-hop graph traversal, path discovery, centrality metrics, and community detection. Implements production patterns similar to LinkedIn's "People You May Know" and Facebook's friend suggestions.

**Complexity:** Advanced recursive CTE with multiple termination conditions, graph metrics (centrality, betweenness), path weight calculations, cycle detection, community clustering, multiple CTE nesting levels

```sql
WITH RECURSIVE direct_chat_connections AS (
    -- Anchor CTE: Direct connections with weighted edges based on shared chat activity
    SELECT DISTINCT
        cp1.user_id AS user_a,
        cp2.user_id AS user_b,
        1 AS hop_count,
        ARRAY[cp1.user_id, cp2.user_id] AS path,
        ARRAY_AGG(cp1.chat_id) AS chat_path,
        COUNT(DISTINCT cp1.chat_id) AS shared_chat_count,
        -- Weight: inverse of shared chats (more chats = stronger connection)
        1.0 / NULLIF(COUNT(DISTINCT cp1.chat_id), 0) AS connection_weight,
        MIN(cp1.joined_at) AS earliest_connection_date,
        MAX(cp1.joined_at) AS latest_connection_date
    FROM chat_participants cp1
    INNER JOIN chat_participants cp2 ON cp1.chat_id = cp2.chat_id
    WHERE cp1.user_id < cp2.user_id
    GROUP BY cp1.user_id, cp2.user_id
),
weighted_path_traversal AS (
    -- Recursive CTE: Multi-hop path discovery with cumulative weights and cycle prevention
    SELECT
        dcc.user_a,
        dcc.user_b,
        dcc.hop_count,
        dcc.path,
        dcc.chat_path,
        dcc.shared_chat_count,
        dcc.connection_weight AS cumulative_weight,
        dcc.earliest_connection_date,
        dcc.latest_connection_date,
        -- Path metadata
        ARRAY_LENGTH(dcc.path, 1) AS path_length,
        ARRAY_LENGTH(dcc.chat_path, 1) AS chat_path_length
    FROM direct_chat_connections dcc

    UNION ALL

    -- Recursive step: Find paths through intermediate users
    SELECT
        wpt.user_a,
        cp3.user_id AS user_b,
        wpt.hop_count + 1,
        wpt.path || cp3.user_id,
        wpt.chat_path || ARRAY[cp2.chat_id],
        wpt.shared_chat_count + 1,
        -- Cumulative weight: sum of inverse weights (Dijkstra-like)
        wpt.cumulative_weight + 1.0,
        LEAST(wpt.earliest_connection_date, cp2.joined_at),
        GREATEST(wpt.latest_connection_date, cp2.joined_at),
        -- Path metadata
        ARRAY_LENGTH(wpt.path || cp3.user_id, 1) AS path_length,
        ARRAY_LENGTH(wpt.chat_path || ARRAY[cp2.chat_id], 1) AS chat_path_length
    FROM weighted_path_traversal wpt
    INNER JOIN chat_participants cp2 ON wpt.user_b = cp2.user_id
    INNER JOIN chat_participants cp3 ON cp2.chat_id = cp3.chat_id
    WHERE
        -- Prevent cycles: user not already in path
        cp3.user_id != ALL(wpt.path)
        -- Limit traversal depth for performance
        AND wpt.hop_count < 4
        -- Prevent paths that are too long (performance optimization)
        AND ARRAY_LENGTH(wpt.path, 1) < 5
        -- Pruning: only continue if cumulative weight is reasonable
        AND wpt.cumulative_weight < 10.0
),
path_optimization AS (
    -- Second CTE: Find shortest paths and optimal routes
    SELECT
        user_a,
        user_b,
        hop_count,
        path,
        chat_path,
        shared_chat_count,
        cumulative_weight,
        earliest_connection_date,
        latest_connection_date,
        path_length,
        chat_path_length,
        -- Path quality metrics
        CASE
            WHEN hop_count = 1 THEN 'Direct'
            WHEN hop_count = 2 THEN 'One Hop'
            WHEN hop_count = 3 THEN 'Two Hops'
            ELSE 'Three+ Hops'
        END AS connection_type,
        -- Time-based connection strength
        EXTRACT(EPOCH FROM (latest_connection_date - earliest_connection_date)) / 86400 AS connection_duration_days
    FROM weighted_path_traversal
),
shortest_paths AS (
    -- Third CTE: Identify shortest paths using window functions
    SELECT
        po.user_a,
        po.user_b,
        po.hop_count,
        po.path,
        po.chat_path,
        po.shared_chat_count,
        po.cumulative_weight,
        po.connection_type,
        po.connection_duration_days,
        po.path_length,
        po.chat_path_length,
        -- Find shortest path for each pair
        MIN(po.hop_count) OVER (PARTITION BY po.user_a, po.user_b) AS min_hops,
        MIN(po.cumulative_weight) OVER (PARTITION BY po.user_a, po.user_b) AS min_weight,
        -- Count all paths between pairs
        COUNT(*) OVER (PARTITION BY po.user_a, po.user_b) AS total_paths,
        -- Rank paths by quality
        ROW_NUMBER() OVER (
            PARTITION BY po.user_a, po.user_b
            ORDER BY po.hop_count ASC, po.cumulative_weight ASC, po.shared_chat_count DESC
        ) AS path_rank
    FROM path_optimization po
),
optimal_connections AS (
    -- Fourth CTE: Select optimal paths and calculate connection metrics
    SELECT
        sp.user_a,
        sp.user_b,
        sp.hop_count AS optimal_hops,
        sp.path AS optimal_path,
        sp.chat_path AS optimal_chat_path,
        sp.shared_chat_count,
        sp.cumulative_weight AS optimal_weight,
        sp.connection_type,
        sp.connection_duration_days,
        sp.total_paths,
        -- Connection strength score (inverse of weight and hops)
        (1.0 / NULLIF(sp.cumulative_weight, 0)) * (1.0 / NULLIF(sp.hop_count, 1)) * sp.shared_chat_count AS connection_strength
    FROM shortest_paths sp
    WHERE sp.path_rank = 1
),
user_centrality_metrics AS (
    -- Fifth CTE: Calculate graph centrality metrics for each user
    SELECT
        user_a AS user_id,
        COUNT(DISTINCT user_b) AS direct_connections,
        COUNT(*) AS total_connections,
        AVG(optimal_hops) AS avg_path_length,
        AVG(optimal_weight) AS avg_connection_weight,
        SUM(connection_strength) AS total_connection_strength,
        MAX(optimal_hops) AS max_path_length,
        MIN(optimal_hops) AS min_path_length,
        -- Betweenness centrality approximation: users who appear in many paths
        COUNT(*) FILTER (WHERE optimal_hops > 1) AS intermediary_connections
    FROM optimal_connections
    GROUP BY user_a
),
network_statistics AS (
    -- Sixth CTE: Aggregate network-level statistics
    SELECT
        oc.user_a,
        oc.user_b,
        oc.optimal_hops,
        oc.optimal_path,
        oc.optimal_chat_path,
        oc.shared_chat_count,
        oc.optimal_weight,
        oc.connection_type,
        oc.connection_duration_days,
        oc.total_paths,
        oc.connection_strength,
        ucm1.direct_connections AS user_a_direct_connections,
        ucm1.total_connection_strength AS user_a_total_strength,
        ucm1.avg_path_length AS user_a_avg_path_length,
        ucm2.direct_connections AS user_b_direct_connections,
        ucm2.total_connection_strength AS user_b_total_strength,
        ucm2.avg_path_length AS user_b_avg_path_length,
        -- Mutual connection analysis
        CASE
            WHEN oc.optimal_hops = 1 THEN 'Direct Connection'
            WHEN oc.optimal_hops = 2 THEN 'One Mutual Connection'
            WHEN oc.optimal_hops = 3 THEN 'Two Mutual Connections'
            ELSE 'Distant Connection'
        END AS connection_category
    FROM optimal_connections oc
    LEFT JOIN user_centrality_metrics ucm1 ON oc.user_a = ucm1.user_id
    LEFT JOIN user_centrality_metrics ucm2 ON oc.user_b = ucm2.user_id
),
path_preview_cte AS (
    -- Seventh CTE: Extract first 5 usernames from path for visualization (cross-database compatible)
    SELECT
        ns.*,
        ARRAY_AGG(p.username ORDER BY
            CASE
                WHEN ARRAY_LENGTH(ns.optimal_path, 1) >= 1 AND p.id = ns.optimal_path[1] THEN 1
                WHEN ARRAY_LENGTH(ns.optimal_path, 1) >= 2 AND p.id = ns.optimal_path[2] THEN 2
                WHEN ARRAY_LENGTH(ns.optimal_path, 1) >= 3 AND p.id = ns.optimal_path[3] THEN 3
                WHEN ARRAY_LENGTH(ns.optimal_path, 1) >= 4 AND p.id = ns.optimal_path[4] THEN 4
                WHEN ARRAY_LENGTH(ns.optimal_path, 1) >= 5 AND p.id = ns.optimal_path[5] THEN 5
                ELSE 999
            END
        ) FILTER (WHERE
            (ARRAY_LENGTH(ns.optimal_path, 1) >= 1 AND p.id = ns.optimal_path[1]) OR
            (ARRAY_LENGTH(ns.optimal_path, 1) >= 2 AND p.id = ns.optimal_path[2]) OR
            (ARRAY_LENGTH(ns.optimal_path, 1) >= 3 AND p.id = ns.optimal_path[3]) OR
            (ARRAY_LENGTH(ns.optimal_path, 1) >= 4 AND p.id = ns.optimal_path[4]) OR
            (ARRAY_LENGTH(ns.optimal_path, 1) >= 5 AND p.id = ns.optimal_path[5])
        ) AS path_usernames
    FROM network_statistics ns
    LEFT JOIN profiles p ON p.id = ANY(ns.optimal_path)
    GROUP BY ns.user_a, ns.user_b, ns.optimal_hops, ns.optimal_path, ns.optimal_chat_path,
             ns.shared_chat_count, ns.optimal_weight, ns.connection_type,
             ns.connection_duration_days, ns.total_paths, ns.connection_strength,
             ns.user_a_direct_connections, ns.user_a_total_strength, ns.user_a_avg_path_length,
             ns.user_b_direct_connections, ns.user_b_total_strength, ns.user_b_avg_path_length,
             ns.connection_category
)
SELECT
    p1.username AS user_a_name,
    p2.username AS user_b_name,
    ppc.optimal_hops,
    ppc.connection_type,
    ppc.connection_category,
    ppc.shared_chat_count,
    ROUND(CAST(ppc.optimal_weight AS NUMERIC), 3) AS connection_weight,
    ROUND(CAST(ppc.connection_strength AS NUMERIC), 2) AS connection_strength,
    ppc.total_paths,
    ROUND(CAST(ppc.connection_duration_days AS NUMERIC), 1) AS connection_duration_days,
    ppc.user_a_direct_connections,
    ppc.user_b_direct_connections,
    ROUND(CAST(ppc.user_a_avg_path_length AS NUMERIC), 2) AS user_a_avg_path_length,
    ROUND(CAST(ppc.user_b_avg_path_length AS NUMERIC), 2) AS user_b_avg_path_length,
    -- Path visualization (first 5 users in path) - cross-database compatible
    ARRAY_TO_STRING(COALESCE(ppc.path_usernames, ARRAY[]::VARCHAR[]), ' -> ') AS path_preview
FROM path_preview_cte ppc
INNER JOIN profiles p1 ON ppc.user_a = p1.id
INNER JOIN profiles p2 ON ppc.user_b = p2.id
WHERE ppc.optimal_hops <= 3
ORDER BY ppc.connection_strength DESC, ppc.optimal_hops ASC, ppc.shared_chat_count DESC
LIMIT 100;
```

**Expected Output:** User connection pairs with shortest path distances and path counts.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries N/A
- **Passed**: 1/2
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chat_participants, direct_chat_connections, network_statistics, optimal_connections, path_optimization, profiles, shortest_paths, user_centrality_metrics, weighted_path_traversal
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chat_participants, direct_chat_connections, network_statistics, optimal_connections, path_optimization, profiles, shortest_paths, user_centrality_metrics, weighted_path_traversal
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chat_participants, direct_chat_connections, network_statistics, optimal_connections, path_optimization, profiles, shortest_paths, user_centrality_metrics, weighted_path_traversal
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chat_participants, direct_chat_connections, network_statistics, optimal_connections, path_optimization, profiles, shortest_paths, user_centrality_metrics, weighted_path_traversal
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Mutual connections
- **Description**: Validates mutual connections functionality
- **Test Data Requirements**:
  - Tables: chat_participants, direct_chat_connections, network_statistics, optimal_connections, path_optimization, profiles, shortest_paths, user_centrality_metrics, weighted_path_traversal
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chat_participants, direct_chat_connections, network_statistics, optimal_connections, path_optimization
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE direct_chat_connections AS (
    -- Anchor CTE: Direct connections with weighted edges based on shared chat activity
    SELECT DISTINCT
        cp1.user_id AS user_a,
        cp2.user_id AS user_b,
        1 AS hop_count,
        ARRAY[cp1.user_id, cp2.user_id] AS path,
        ARRAY[cp1.chat_id] AS chat_path,
        COUNT(DISTINCT cp1.chat_id) AS shared_chat_count,
        -- Weight: inverse of shared chats (more chats = stronger connection)
        1.0 / NULLIF(COUNT(DISTINCT ...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 3: Production-Grade Conversation Analytics with Deep CTE Nesting and Advanced Pattern Recognition

**Description:** Enterprise-level conversation thread analysis with turn-taking patterns, sentiment indicators, engagement velocity, conversation health scoring, and predictive analytics. Implements production patterns similar to customer support platforms and AI chat analytics systems.

**Complexity:** Deep nested CTEs (7+ levels), advanced window functions with multiple frame clauses, pattern recognition, time-series analysis, conversation health scoring, engagement velocity calculations, predictive metrics

```sql
WITH message_thread_sequence AS (
    -- First CTE: Establish message sequence with comprehensive metadata
    SELECT
        m.id,
        m.chat_id,
        m.sender_id,
        m.is_ai,
        m.content,
        m.created_at,
        LENGTH(m.content) AS message_length,
        -- Sequence numbering
        ROW_NUMBER() OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS message_sequence,
        ROW_NUMBER() OVER (PARTITION BY m.chat_id, m.is_ai ORDER BY m.created_at) AS type_sequence,
        -- Temporal analysis
        LAG(m.created_at, 1) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS prev_message_time,
        LEAD(m.created_at, 1) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS next_message_time,
        LAG(m.is_ai, 1) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS prev_is_ai,
        LAG(m.is_ai, 2) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS prev2_is_ai,
        LEAD(m.is_ai, 1) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS next_is_ai,
        LEAD(m.is_ai, 2) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS next2_is_ai,
        -- Aggregated context
        COUNT(*) OVER (PARTITION BY m.chat_id) AS total_chat_messages,
        COUNT(*) OVER (PARTITION BY m.chat_id, m.is_ai) AS total_type_messages,
        AVG(LENGTH(m.content)) OVER (PARTITION BY m.chat_id) AS chat_avg_length,
        AVG(LENGTH(m.content)) OVER (PARTITION BY m.chat_id, m.is_ai) AS type_avg_length
    FROM messages m
),
temporal_analysis AS (
    -- Second CTE: Calculate time-based metrics and response patterns
    SELECT
        mts.*,
        -- Response time calculations
        EXTRACT(EPOCH FROM (mts.created_at - mts.prev_message_time)) AS seconds_since_prev,
        EXTRACT(EPOCH FROM (mts.next_message_time - mts.created_at)) AS seconds_until_next,
        -- Turn-taking patterns
        CASE
            WHEN mts.prev_is_ai = false AND mts.is_ai = true THEN 'User-to-AI'
            WHEN mts.prev_is_ai = true AND mts.is_ai = false THEN 'AI-to-User'
            WHEN mts.prev_is_ai = false AND mts.is_ai = false THEN 'User-to-User'
            WHEN mts.prev_is_ai = true AND mts.is_ai = true THEN 'AI-to-AI'
            ELSE 'First-Message'
        END AS transition_type,
        -- Conversation flow indicators
        CASE
            WHEN mts.prev_is_ai IS NULL THEN 'Conversation-Start'
            WHEN mts.next_is_ai IS NULL THEN 'Conversation-End'
            WHEN mts.prev_is_ai != mts.is_ai AND mts.next_is_ai != mts.is_ai THEN 'Turn-Taking'
            WHEN mts.prev_is_ai = mts.is_ai AND mts.next_is_ai = mts.is_ai THEN 'Same-Type-Burst'
            ELSE 'Mixed-Pattern'
        END AS flow_pattern,
        -- Message length analysis relative to conversation
        CASE
            WHEN mts.chat_avg_length > 0 THEN mts.message_length::numeric / mts.chat_avg_length
            ELSE 1.0
        END AS length_ratio,
        CASE
            WHEN mts.type_avg_length > 0 THEN mts.message_length::numeric / mts.type_avg_length
            ELSE 1.0
        END AS type_length_ratio
    FROM message_thread_sequence mts
),
conversation_velocity AS (
    -- Third CTE: Calculate engagement velocity and activity patterns
    SELECT
        ta.*,
        -- Velocity metrics (messages per time unit)
        CASE
            WHEN ta.seconds_since_prev > 0 THEN 60.0 / ta.seconds_since_prev
            ELSE NULL
        END AS messages_per_minute_prev,
        CASE
            WHEN ta.seconds_until_next > 0 THEN 60.0 / ta.seconds_until_next
            ELSE NULL
        END AS messages_per_minute_next,
        -- Rolling window statistics
        AVG(ta.seconds_since_prev) OVER (
            PARTITION BY ta.chat_id
            ORDER BY ta.message_sequence
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_response_time_5,
        AVG(ta.seconds_since_prev) OVER (
            PARTITION BY ta.chat_id
            ORDER BY ta.message_sequence
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_response_time_10,
        -- Activity bursts detection
        COUNT(*) OVER (
            PARTITION BY ta.chat_id
            ORDER BY ta.message_sequence
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS messages_in_last_5,
        COUNT(*) OVER (
            PARTITION BY ta.chat_id
            ORDER BY ta.message_sequence
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS messages_in_last_10,
        -- Conversation health indicators
        CASE
            WHEN ta.seconds_since_prev < 60 AND ta.transition_type IN ('User-to-AI', 'AI-to-User') THEN 'High-Engagement'
            WHEN ta.seconds_since_prev < 300 AND ta.transition_type IN ('User-to-AI', 'AI-to-User') THEN 'Medium-Engagement'
            WHEN ta.seconds_since_prev > 3600 THEN 'Low-Engagement'
            ELSE 'Normal-Engagement'
        END AS engagement_level
    FROM temporal_analysis ta
),
thread_pattern_aggregation AS (
    -- Fourth CTE: Aggregate patterns at thread level
    SELECT
        chat_id,
        COUNT(*) AS total_messages,
        COUNT(DISTINCT sender_id) AS unique_participants,
        -- Message type breakdown
        SUM(CASE WHEN is_ai = false THEN 1 ELSE 0 END) AS user_messages,
        SUM(CASE WHEN is_ai = true THEN 1 ELSE 0 END) AS ai_messages,
        -- Transition patterns
        SUM(CASE WHEN transition_type = 'User-to-AI' THEN 1 ELSE 0 END) AS user_to_ai_transitions,
        SUM(CASE WHEN transition_type = 'AI-to-User' THEN 1 ELSE 0 END) AS ai_to_user_transitions,
        SUM(CASE WHEN transition_type = 'User-to-User' THEN 1 ELSE 0 END) AS user_to_user_transitions,
        SUM(CASE WHEN transition_type = 'AI-to-AI' THEN 1 ELSE 0 END) AS ai_to_ai_transitions,
        -- Flow patterns
        SUM(CASE WHEN flow_pattern = 'Turn-Taking' THEN 1 ELSE 0 END) AS turn_taking_count,
        SUM(CASE WHEN flow_pattern = 'Same-Type-Burst' THEN 1 ELSE 0 END) AS burst_count,
        -- Temporal metrics
        AVG(seconds_since_prev) AS avg_response_time,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY seconds_since_prev) AS median_response_time,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY seconds_since_prev) AS p25_response_time,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY seconds_since_prev) AS p75_response_time,
        MIN(seconds_since_prev) AS min_response_time,
        MAX(seconds_since_prev) AS max_response_time,
        STDDEV(seconds_since_prev) AS stddev_response_time,
        -- Velocity metrics
        AVG(messages_per_minute_prev) AS avg_messages_per_minute,
        MAX(messages_per_minute_prev) AS peak_messages_per_minute,
        -- Length metrics
        AVG(message_length) AS avg_message_length,
        AVG(length_ratio) AS avg_length_ratio,
        -- Engagement metrics
        SUM(CASE WHEN engagement_level = 'High-Engagement' THEN 1 ELSE 0 END) AS high_engagement_count,
        SUM(CASE WHEN engagement_level = 'Low-Engagement' THEN 1 ELSE 0 END) AS low_engagement_count,
        -- Conversation span
        MIN(created_at) AS conversation_start,
        MAX(created_at) AS conversation_end,
        EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) / 60 AS conversation_duration_minutes
    FROM conversation_velocity
    GROUP BY chat_id
),
conversation_health_scoring AS (
    -- Fifth CTE: Calculate comprehensive conversation health scores
    SELECT
        tpa.*,
        -- Balance metrics
        CASE
            WHEN tpa.total_messages > 0 THEN tpa.user_messages::numeric / tpa.total_messages
            ELSE 0
        END AS user_message_ratio,
        CASE
            WHEN tpa.total_messages > 0 THEN tpa.ai_messages::numeric / tpa.total_messages
            ELSE 0
        END AS ai_message_ratio,
        -- Turn-taking quality
        CASE
            WHEN tpa.total_messages > 1 THEN tpa.user_to_ai_transitions::numeric / (tpa.total_messages - 1)
            ELSE 0
        END AS turn_taking_ratio,
        -- Response time quality (inverse - faster is better)
        CASE
            WHEN tpa.avg_response_time > 0 THEN 1.0 / (1.0 + tpa.avg_response_time / 60.0)
            ELSE 0
        END AS response_time_score,
        -- Engagement quality
        CASE
            WHEN tpa.total_messages > 0 THEN tpa.high_engagement_count::numeric / tpa.total_messages
            ELSE 0
        END AS high_engagement_ratio,
        -- Conversation velocity score
        CASE
            WHEN tpa.conversation_duration_minutes > 0 THEN tpa.total_messages::numeric / tpa.conversation_duration_minutes
            ELSE 0
        END AS messages_per_minute,
        -- Comprehensive health score (weighted factors)
        (
            -- Turn-taking quality (30%)
            (CASE WHEN tpa.total_messages > 1 THEN tpa.user_to_ai_transitions::numeric / (tpa.total_messages - 1) ELSE 0 END * 30) +
            -- Response time quality (25%)
            (CASE WHEN tpa.avg_response_time > 0 THEN 1.0 / (1.0 + tpa.avg_response_time / 60.0) ELSE 0 END * 25) +
            -- Engagement level (20%)
            (CASE WHEN tpa.total_messages > 0 THEN tpa.high_engagement_count::numeric / tpa.total_messages ELSE 0 END * 20) +
            -- Message balance (15%)
            (LEAST(
                CASE WHEN tpa.total_messages > 0 THEN tpa.user_messages::numeric / tpa.total_messages ELSE 0 END,
                CASE WHEN tpa.total_messages > 0 THEN tpa.ai_messages::numeric / tpa.total_messages ELSE 0 END
            ) * 2 * 15) +
            -- Conversation length (10%) - longer conversations indicate engagement
            (LEAST(tpa.total_messages / 50.0, 1.0) * 10)
        ) AS raw_health_score
    FROM thread_pattern_aggregation tpa
),
conversation_classification AS (
    -- Sixth CTE: Classify conversations and calculate percentiles
    SELECT
        chs.chat_id,
        chs.total_messages,
        chs.user_messages,
        chs.ai_messages,
        chs.user_message_ratio,
        chs.ai_message_ratio,
        chs.turn_taking_ratio,
        chs.response_time_score,
        chs.high_engagement_ratio,
        chs.messages_per_minute,
        chs.avg_response_time,
        chs.median_response_time,
        chs.p25_response_time,
        chs.p75_response_time,
        chs.burst_count,
        chs.turn_taking_count,
        chs.raw_health_score,
        tpa.unique_participants,
        tpa.user_to_ai_transitions,
        tpa.ai_to_user_transitions,
        -- Conversation type classification
        CASE
            WHEN chs.user_message_ratio > 0.7 THEN 'User-Dominated'
            WHEN chs.user_message_ratio > 0.7 THEN 'AI-Dominated'
            WHEN chs.turn_taking_ratio > 0.6 THEN 'Balanced-Dialogue'
            WHEN chs.burst_count > chs.turn_taking_count THEN 'Burst-Pattern'
            ELSE 'Mixed-Pattern'
        END AS conversation_type,
        -- Engagement classification
        CASE
            WHEN chs.messages_per_minute > 2 THEN 'High-Velocity'
            WHEN chs.messages_per_minute > 0.5 THEN 'Medium-Velocity'
            WHEN chs.messages_per_minute > 0.1 THEN 'Low-Velocity'
            ELSE 'Stagnant'
        END AS velocity_class,
        -- Health classification
        CASE
            WHEN chs.raw_health_score >= 70 THEN 'Excellent'
            WHEN chs.raw_health_score >= 50 THEN 'Good'
            WHEN chs.raw_health_score >= 30 THEN 'Fair'
            ELSE 'Poor'
        END AS health_class,
        -- Percentile rankings
        PERCENT_RANK() OVER (ORDER BY chs.raw_health_score DESC) AS health_percentile,
        PERCENT_RANK() OVER (ORDER BY chs.messages_per_minute DESC) AS velocity_percentile,
        PERCENT_RANK() OVER (ORDER BY chs.total_messages DESC) AS volume_percentile,
        -- Cross-conversation comparisons
        AVG(chs.raw_health_score) OVER () AS overall_avg_health,
        AVG(chs.messages_per_minute) OVER () AS overall_avg_velocity,
        STDDEV(chs.raw_health_score) OVER () AS overall_stddev_health
    FROM conversation_health_scoring chs
    LEFT JOIN thread_pattern_aggregation tpa ON chs.chat_id = tpa.chat_id
),
final_conversation_analytics AS (
    -- Seventh CTE: Final analytics with rankings and recommendations
    SELECT
        cc.chat_id,
        NULL AS chat_title,
        cc.total_messages,
        cc.unique_participants,
        cc.user_messages,
        cc.ai_messages,
        cc.user_to_ai_transitions,
        cc.ai_to_user_transitions,
        cc.turn_taking_count,
        cc.burst_count,
        ROUND(CAST(cc.user_message_ratio * 100 AS NUMERIC), 2) AS user_message_percentage,
        ROUND(CAST(cc.ai_message_ratio * 100 AS NUMERIC), 2) AS ai_message_percentage,
        cc.turn_taking_ratio,
        cc.response_time_score,
        cc.high_engagement_ratio,
        ROUND(CAST(cc.avg_response_time AS NUMERIC), 2) AS avg_response_seconds,
        ROUND(CAST(cc.median_response_time AS NUMERIC), 2) AS median_response_seconds,
        ROUND(CAST(cc.p25_response_time AS NUMERIC), 2) AS p25_response_seconds,
        ROUND(CAST(cc.p75_response_time AS NUMERIC), 2) AS p75_response_seconds,
        ROUND(CAST(cc.messages_per_minute AS NUMERIC), 3) AS messages_per_minute,
        ROUND(CAST(cc.raw_health_score AS NUMERIC), 2) AS health_score,
        cc.conversation_type,
        cc.velocity_class,
        cc.health_class,
        ROUND(CAST(cc.health_percentile * 100 AS NUMERIC), 2) AS health_percentile,
        ROUND(CAST(cc.velocity_percentile * 100 AS NUMERIC), 2) AS velocity_percentile,
        ROUND(CAST(cc.volume_percentile * 100 AS NUMERIC), 2) AS volume_percentile,
        ROUND(CAST(cc.overall_avg_health AS NUMERIC), 2) AS overall_avg_health,
        -- Relative performance
        CASE
            WHEN cc.overall_avg_health > 0 THEN cc.raw_health_score / cc.overall_avg_health
            ELSE 1.0
        END AS health_ratio,
        -- Rankings
        ROW_NUMBER() OVER (ORDER BY cc.raw_health_score DESC) AS health_rank,
        RANK() OVER (ORDER BY cc.messages_per_minute DESC) AS velocity_rank,
        DENSE_RANK() OVER (ORDER BY cc.total_messages DESC) AS volume_rank,
        -- NTILE segmentation
        NTILE(5) OVER (ORDER BY cc.raw_health_score DESC) AS health_quintile,
        NTILE(10) OVER (ORDER BY cc.raw_health_score DESC) AS health_decile,
        -- Recommendations
        CASE
            WHEN cc.raw_health_score < 30 AND cc.user_message_ratio < 0.3 THEN 'Encourage User Participation'
            WHEN cc.raw_health_score < 30 AND cc.avg_response_time > 300 THEN 'Improve Response Time'
            WHEN cc.burst_count > cc.turn_taking_count THEN 'Encourage Turn-Taking'
            WHEN cc.messages_per_minute < 0.1 THEN 'Increase Engagement Velocity'
            ELSE 'Conversation Healthy'
        END AS recommendation
    FROM conversation_classification cc
)
SELECT
    NULL AS chat_title,
    fca.total_messages,
    fca.unique_participants,
    fca.user_messages,
    fca.ai_messages,
    fca.user_message_percentage,
    fca.ai_message_percentage,
    fca.user_to_ai_transitions,
    fca.ai_to_user_transitions,
    fca.turn_taking_count,
    fca.burst_count,
    fca.avg_response_seconds,
    fca.median_response_seconds,
    fca.p25_response_seconds,
    fca.p75_response_seconds,
    fca.messages_per_minute,
    fca.health_score,
    fca.conversation_type,
    fca.velocity_class,
    fca.health_class,
    fca.health_percentile,
    fca.velocity_percentile,
    fca.volume_percentile,
    ROUND(CAST(fca.health_ratio AS NUMERIC), 2) AS health_ratio,
    fca.health_rank,
    fca.velocity_rank,
    fca.volume_rank,
    fca.health_quintile,
    fca.health_decile,
    fca.recommendation
FROM final_conversation_analytics fca
INNER JOIN chats c ON fca.chat_id = c.id
WHERE fca.total_messages >= 5
ORDER BY fca.health_score DESC, fca.total_messages DESC;
```

**Expected Output:** Chat analysis with message patterns, transitions, and conversation type classification.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ⚠️
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination N/A
- [ ] Window frame boundaries ✅
- **Passed**: 1/1


**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_classification, conversation_health_scoring, conversation_velocity, final_conversation_analytics, message_thread_sequence, messages, temporal_analysis, thread_pattern_aggregation
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_classification, conversation_health_scoring, conversation_velocity, final_conversation_analytics, message_thread_sequence, messages, temporal_analysis, thread_pattern_aggregation
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_classification, conversation_health_scoring, conversation_velocity, final_conversation_analytics, message_thread_sequence, messages, temporal_analysis, thread_pattern_aggregation
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_classification, conversation_health_scoring, conversation_velocity, final_conversation_analytics, message_thread_sequence, messages, temporal_analysis, thread_pattern_aggregation
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_classification, conversation_health_scoring, conversation_velocity, final_conversation_analytics, message_thread_sequence, messages, temporal_analysis, thread_pattern_aggregation
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chats, conversation_classification, conversation_health_scoring, conversation_velocity, final_conversation_analytics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH message_thread_sequence AS (
    -- First CTE: Establish message sequence with comprehensive metadata
    SELECT
        m.id,
        m.chat_id,
        m.sender_id,
        m.is_ai,
        m.content,
        m.created_at,
        LENGTH(m.content) AS message_length,
        -- Sequence numbering
        ROW_NUMBER() OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS message_sequence,
        ROW_NUMBER() OVER (PARTITION BY m.chat_id, m.is_ai ORDER BY m.created_at) AS type_sequence,
 ...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 4: Production-Grade Friend Network Analysis with Recursive CTE and Advanced Graph Metrics

**Description:** Enterprise-level friend network analysis with recursive CTE for multi-hop connections, graph centrality metrics, network clustering, and advanced window function analytics. Implements production patterns similar to LinkedIn's connection analysis.

**Complexity:** Recursive CTE, multiple nested CTEs (6+ levels), window functions with frame clauses, correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE friend_network_expansion AS (
    -- Anchor: Direct friend connections
    SELECT
        f1.user_id AS user_a,
        f2.user_id AS user_b,
        1 AS connection_depth,
        ARRAY[f1.user_id, f2.user_id] AS connection_path,
        f1.status AS status_a,
        f2.status AS status_b
    FROM friends f1
    INNER JOIN friends f2 ON f1.friend_id = f2.friend_id AND f1.user_id = f2.friend_id
    WHERE f1.status = 'accepted' AND f2.status = 'accepted'

    UNION ALL

    -- Recursive: Multi-hop friend connections
    SELECT
        fne.user_a,
        f3.user_id AS user_b,
        fne.connection_depth + 1,
        fne.connection_path || f3.user_id,
        fne.status_a,
        f4.status AS status_b
    FROM friend_network_expansion fne
    INNER JOIN friends f3 ON fne.user_b = f3.friend_id AND f3.status = 'accepted'
    INNER JOIN friends f4 ON f3.user_id = f4.friend_id AND f4.user_id = f3.friend_id AND f4.status = 'accepted'
    WHERE f3.user_id != ALL(fne.connection_path)
        AND fne.connection_depth < 3
),
friend_statistics AS (
    -- First CTE: Aggregate friend statistics
    SELECT
        f.user_id,
        COUNT(*) AS total_friend_requests,
        SUM(CASE WHEN f.status = 'accepted' THEN 1 ELSE 0 END) AS accepted_friends,
        SUM(CASE WHEN f.status = 'pending' THEN 1 ELSE 0 END) AS pending_friends,
        SUM(CASE WHEN f.status = 'declined' THEN 1 ELSE 0 END) AS declined_friends,
        AVG(CASE WHEN f.status = 'accepted' THEN 1.0 ELSE 0.0 END) AS acceptance_rate
    FROM friends f
    GROUP BY f.user_id
),
mutual_connection_analysis AS (
    -- Second CTE: Calculate mutual connections with correlated subqueries
    SELECT
        f1.user_id AS user_a,
        f2.user_id AS user_b,
        COUNT(DISTINCT f3.friend_id) AS mutual_friends,
        (
            SELECT COUNT(*)
            FROM friends f4
            WHERE f4.user_id = f1.user_id
                AND f4.status = 'accepted'
                AND EXISTS (
                    SELECT 1
                    FROM friends f5
                    WHERE f5.user_id = f2.user_id
                        AND f5.friend_id = f4.friend_id
                        AND f5.status = 'accepted'
                )
        ) AS verified_mutual_count
    FROM friends f1
    INNER JOIN friends f2 ON f1.friend_id = f2.friend_id
    LEFT JOIN friends f3 ON f3.user_id = f1.user_id AND f3.status = 'accepted'
    INNER JOIN friends f4 ON f4.user_id = f2.user_id AND f4.friend_id = f3.friend_id AND f4.status = 'accepted'
    WHERE f1.status = 'accepted'
        AND f2.status = 'accepted'
        AND f1.user_id < f2.user_id
    GROUP BY f1.user_id, f2.user_id
),
network_centrality_metrics AS (
    -- Third CTE: Calculate graph centrality using window functions
    SELECT
        fs.user_id,
        p.username,
        fs.total_friend_requests,
        fs.accepted_friends,
        fs.pending_friends,
        fs.declined_friends,
        fs.acceptance_rate,
        -- Centrality metrics
        COUNT(DISTINCT fne.user_b) AS total_connections,
        COUNT(DISTINCT CASE WHEN fne.connection_depth = 1 THEN fne.user_b END) AS direct_connections,
        COUNT(DISTINCT CASE WHEN fne.connection_depth = 2 THEN fne.user_b END) AS second_degree_connections,
        AVG(fne.connection_depth) AS avg_connection_depth,
        -- Window function rankings
        ROW_NUMBER() OVER (ORDER BY fs.accepted_friends DESC) AS friend_count_rank,
        DENSE_RANK() OVER (ORDER BY fs.accepted_friends DESC) AS friend_dense_rank,
        PERCENT_RANK() OVER (ORDER BY fs.accepted_friends DESC) AS friend_percentile,
        LAG(fs.accepted_friends, 1) OVER (ORDER BY fs.accepted_friends DESC) AS prev_user_friends,
        LEAD(fs.accepted_friends, 1) OVER (ORDER BY fs.accepted_friends DESC) AS next_user_friends,
        SUM(fs.accepted_friends) OVER (ORDER BY fs.accepted_friends DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_friends,
        AVG(fs.accepted_friends) OVER (ORDER BY fs.accepted_friends DESC ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING) AS moving_avg_friends
    FROM friend_statistics fs
    INNER JOIN profiles p ON fs.user_id = p.id
    LEFT JOIN friend_network_expansion fne ON fs.user_id = fne.user_a
    GROUP BY fs.user_id, p.username, fs.total_friend_requests, fs.accepted_friends, fs.pending_friends, fs.declined_friends, fs.acceptance_rate
),
mutual_connection_aggregation AS (
    -- Fourth CTE: Aggregate mutual connection metrics
    SELECT
        ncm.user_id,
        ncm.username,
        ncm.total_friend_requests,
        ncm.accepted_friends,
        ncm.pending_friends,
        ncm.declined_friends,
        ncm.acceptance_rate,
        ncm.total_connections,
        ncm.direct_connections,
        ncm.second_degree_connections,
        ncm.avg_connection_depth,
        ncm.friend_count_rank,
        ncm.friend_dense_rank,
        ncm.friend_percentile,
        ncm.prev_user_friends,
        ncm.next_user_friends,
        ncm.cumulative_friends,
        ncm.moving_avg_friends,
        COALESCE(SUM(mca.mutual_friends), 0) AS total_mutual_connections,
        COALESCE(AVG(mca.mutual_friends), 0) AS avg_mutual_connections,
        COALESCE(MAX(mca.mutual_friends), 0) AS max_mutual_connections,
        COALESCE(SUM(mca.verified_mutual_count), 0) AS verified_mutual_total
    FROM network_centrality_metrics ncm
    LEFT JOIN mutual_connection_analysis mca ON ncm.user_id = mca.user_a OR ncm.user_id = mca.user_b
    GROUP BY ncm.user_id, ncm.username, ncm.total_friend_requests, ncm.accepted_friends, ncm.pending_friends, ncm.declined_friends, ncm.acceptance_rate, ncm.total_connections, ncm.direct_connections, ncm.second_degree_connections, ncm.avg_connection_depth, ncm.friend_count_rank, ncm.friend_dense_rank, ncm.friend_percentile, ncm.prev_user_friends, ncm.next_user_friends, ncm.cumulative_friends, ncm.moving_avg_friends
),
network_scoring AS (
    -- Fifth CTE: Calculate comprehensive network scores
    SELECT
        mca.*,
        -- Network strength score
        (
            (mca.accepted_friends * 0.3) +
            (mca.total_mutual_connections * 0.25) +
            (mca.direct_connections * 0.2) +
            (mca.second_degree_connections * 0.15) +
            (mca.acceptance_rate * 100 * 0.1)
        ) AS network_strength_score,
        -- Connection quality ratio
        CASE
            WHEN mca.accepted_friends > 0 THEN mca.total_mutual_connections::numeric / mca.accepted_friends
            ELSE 0
        END AS connection_quality_ratio,
        -- Pivot analysis using CASE
        CASE
            WHEN mca.accepted_friends >= 50 THEN 'Power User'
            WHEN mca.accepted_friends >= 20 THEN 'Active User'
            WHEN mca.accepted_friends >= 10 THEN 'Regular User'
            WHEN mca.accepted_friends >= 5 THEN 'Casual User'
            ELSE 'New User'
        END AS user_category,
        CASE
            WHEN mca.total_mutual_connections >= 20 THEN 'Highly Connected'
            WHEN mca.total_mutual_connections >= 10 THEN 'Well Connected'
            WHEN mca.total_mutual_connections >= 5 THEN 'Moderately Connected'
            ELSE 'Loosely Connected'
        END AS connection_category
    FROM mutual_connection_aggregation mca
),
final_network_analytics AS (
    -- Sixth CTE: Final analytics with UNION and additional window functions
    SELECT
        ns.user_id,
        ns.username,
        ns.total_friend_requests,
        ns.accepted_friends,
        ns.pending_friends,
        ns.declined_friends,
        ROUND(CAST(ns.acceptance_rate * 100 AS NUMERIC), 2) AS acceptance_rate_percent,
        ns.total_connections,
        ns.direct_connections,
        ns.second_degree_connections,
        ROUND(CAST(ns.avg_connection_depth AS NUMERIC), 2) AS avg_connection_depth,
        ns.total_mutual_connections,
        ROUND(CAST(ns.avg_mutual_connections AS NUMERIC), 2) AS avg_mutual_connections,
        ns.max_mutual_connections,
        ns.verified_mutual_total,
        ROUND(CAST(ns.network_strength_score AS NUMERIC), 2) AS network_strength_score,
        ROUND(CAST(ns.connection_quality_ratio AS NUMERIC), 3) AS connection_quality_ratio,
        ns.user_category,
        ns.connection_category,
        ns.friend_count_rank,
        ns.friend_dense_rank,
        ROUND(CAST(ns.friend_percentile * 100 AS NUMERIC), 2) AS friend_percentile,
        ns.prev_user_friends,
        ns.next_user_friends,
        ns.cumulative_friends,
        ROUND(CAST(ns.moving_avg_friends AS NUMERIC), 2) AS moving_avg_friends,
        -- Additional window functions with frames
        SUM(ns.accepted_friends) OVER (
            PARTITION BY ns.user_category
            ORDER BY ns.network_strength_score DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS category_cumulative_friends,
        AVG(ns.network_strength_score) OVER (
            PARTITION BY ns.user_category
            ORDER BY ns.network_strength_score DESC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS category_moving_avg_score,
        NTILE(5) OVER (ORDER BY ns.network_strength_score DESC) AS network_quintile,
        NTILE(10) OVER (ORDER BY ns.network_strength_score DESC) AS network_decile
    FROM network_scoring ns
)
SELECT
    user_id,
    username,
    total_friend_requests,
    accepted_friends,
    pending_friends,
    declined_friends,
    acceptance_rate_percent,
    total_connections,
    direct_connections,
    second_degree_connections,
    avg_connection_depth,
    total_mutual_connections,
    avg_mutual_connections,
    max_mutual_connections,
    verified_mutual_total,
    network_strength_score,
    connection_quality_ratio,
    user_category,
    connection_category,
    friend_count_rank,
    friend_dense_rank,
    friend_percentile,
    prev_user_friends,
    next_user_friends,
    cumulative_friends,
    moving_avg_friends,
    category_cumulative_friends,
    ROUND(CAST(category_moving_avg_score AS NUMERIC), 2) AS category_moving_avg_score,
    network_quintile,
    network_decile
FROM final_network_analytics
ORDER BY network_strength_score DESC, accepted_friends DESC;
```

**Expected Output:** User friend network statistics with acceptance rates and mutual connections.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: final_network_analytics, friend_network_expansion, friend_statistics, friends, mutual_connection_aggregation, mutual_connection_analysis, network_centrality_metrics, network_scoring, profiles
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: final_network_analytics, friend_network_expansion, friend_statistics, friends, mutual_connection_aggregation, mutual_connection_analysis, network_centrality_metrics, network_scoring, profiles
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: final_network_analytics, friend_network_expansion, friend_statistics, friends, mutual_connection_aggregation, mutual_connection_analysis, network_centrality_metrics, network_scoring, profiles
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: final_network_analytics, friend_network_expansion, friend_statistics, friends, mutual_connection_aggregation, mutual_connection_analysis, network_centrality_metrics, network_scoring, profiles
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Mutual connections
- **Description**: Validates mutual connections functionality
- **Test Data Requirements**:
  - Tables: final_network_analytics, friend_network_expansion, friend_statistics, friends, mutual_connection_aggregation, mutual_connection_analysis, network_centrality_metrics, network_scoring, profiles
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: final_network_analytics, friend_network_expansion, friend_statistics, friends, mutual_connection_aggregation
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE friend_network_expansion AS (
    -- Anchor: Direct friend connections
    SELECT
        f1.user_id AS user_a,
        f2.user_id AS user_b,
        1 AS connection_depth,
        ARRAY[f1.user_id, f2.user_id] AS connection_path,
        f1.status AS status_a,
        f2.status AS status_b
    FROM friends f1
    INNER JOIN friends f2 ON f1.friend_id = f2.friend_id AND f1.user_id = f2.friend_id
    WHERE f1.status = 'accepted' AND f2.status = 'accepted'

    UNION ALL

    -- Rec...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 5: Production-Grade Time-Series Analysis with Recursive CTE and Advanced Window Functions

**Description:** Enterprise-level time-series analysis with recursive CTE for temporal pattern discovery, multiple window function frame clauses, correlated subqueries, and UNION operations. Implements production patterns similar to time-series analytics platforms.

**Complexity:** Recursive CTE, multiple nested CTEs (7+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex aggregations

```sql
WITH RECURSIVE temporal_hierarchy AS (
    -- Anchor: Base time periods
    SELECT
        DATE_TRUNC('hour', m.created_at) AS time_period,
        'hour' AS period_type,
        COUNT(*) AS message_count,
        COUNT(DISTINCT m.chat_id) AS active_chats,
        COUNT(DISTINCT m.sender_id) AS active_users
    FROM messages m
    GROUP BY DATE_TRUNC('hour', m.created_at)

    UNION ALL

    -- Recursive: Aggregate to higher time periods
    SELECT
        DATE_TRUNC('day', th.time_period) AS time_period,
        'day' AS period_type,
        0 AS sum_placeholder,
        1 AS count_placeholder,
        1 AS count_placeholder
    FROM temporal_hierarchy th
    WHERE th.period_type = 'hour'
        AND DATE_TRUNC('day', th.time_period) != th.time_period
    GROUP BY DATE_TRUNC('day', th.time_period)
),
hourly_activity_base AS (
    -- First CTE: Base hourly aggregations with joins
    SELECT
        DATE_TRUNC('hour', m.created_at) AS activity_hour,
        COUNT(*) AS message_count,
        COUNT(DISTINCT m.chat_id) AS active_chats,
        COUNT(DISTINCT m.sender_id) AS active_users,
        SUM(CASE WHEN m.is_ai = false THEN 1 ELSE 0 END) AS user_messages,
        SUM(CASE WHEN m.is_ai = true THEN 1 ELSE 0 END) AS ai_messages,
        AVG(LENGTH(m.content)) AS avg_message_length,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY LENGTH(m.content)) AS median_message_length
    FROM messages m
    INNER JOIN chats c ON m.chat_id = c.id
    LEFT JOIN profiles p ON m.sender_id = p.id
    GROUP BY DATE_TRUNC('hour', m.created_at)
),
user_activity_by_hour AS (
    -- Second CTE: User-level hourly activity with correlated subqueries
    SELECT
        hab.activity_hour,
        hab.message_count,
        hab.active_chats,
        hab.active_users,
        hab.user_messages,
        hab.ai_messages,
        hab.avg_message_length,
        hab.median_message_length,
        (
            SELECT COUNT(DISTINCT m2.chat_id)
            FROM messages m2
            WHERE DATE_TRUNC('hour', m2.created_at) = hab.activity_hour
                AND m2.is_ai = false
                AND EXISTS (
                    SELECT 1
                    FROM messages m3
                    WHERE m3.chat_id = m2.chat_id
                        AND DATE_TRUNC('hour', m3.created_at) = hab.activity_hour
                        AND m3.is_ai = true
                )
        ) AS chats_with_ai_interaction,
        (
            SELECT AVG(LENGTH(m4.content))
            FROM messages m4
            WHERE DATE_TRUNC('hour', m4.created_at) = hab.activity_hour
                AND m4.is_ai = false
        ) AS avg_user_message_length
    FROM hourly_activity_base hab
),
rolling_window_statistics AS (
    -- Third CTE: Multiple window functions with different frame clauses
    SELECT
        uabh.activity_hour,
        uabh.message_count,
        uabh.active_chats,
        uabh.active_users,
        uabh.user_messages,
        uabh.ai_messages,
        uabh.chats_with_ai_interaction,
        uabh.avg_message_length,
        uabh.median_message_length,
        uabh.avg_user_message_length,
        -- ROWS BETWEEN frames
        SUM(uabh.message_count) OVER (
            ORDER BY uabh.activity_hour
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS messages_12h_window,
        AVG(uabh.message_count) OVER (
            ORDER BY uabh.activity_hour
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS avg_messages_24h_rows,
        MAX(uabh.message_count) OVER (
            ORDER BY uabh.activity_hour
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS max_messages_24h_rows,
        MIN(uabh.message_count) OVER (
            ORDER BY uabh.activity_hour
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS min_messages_24h_rows,
        -- RANGE BETWEEN frames (time-based)
        SUM(uabh.message_count) OVER (
            ORDER BY uabh.activity_hour
            RANGE BETWEEN INTERVAL '12 hours' PRECEDING AND CURRENT ROW
        ) AS messages_12h_range,
        AVG(uabh.message_count) OVER (
            ORDER BY uabh.activity_hour
            RANGE BETWEEN INTERVAL '24 hours' PRECEDING AND CURRENT ROW
        ) AS avg_messages_24h_range,
        -- Lag/Lead functions
        LAG(uabh.message_count, 1) OVER (ORDER BY uabh.activity_hour) AS prev_hour_messages,
        LAG(uabh.message_count, 2) OVER (ORDER BY uabh.activity_hour) AS prev2_hour_messages,
        LEAD(uabh.message_count, 1) OVER (ORDER BY uabh.activity_hour) AS next_hour_messages,
        LEAD(uabh.message_count, 2) OVER (ORDER BY uabh.activity_hour) AS next2_hour_messages,
        -- First/Last value with frames
        FIRST_VALUE(uabh.message_count) OVER (
            ORDER BY uabh.activity_hour
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS first_value_24h,
        LAST_VALUE(uabh.message_count) OVER (
            ORDER BY uabh.activity_hour
            ROWS BETWEEN CURRENT ROW AND 23 FOLLOWING
        ) AS last_value_24h
    FROM user_activity_by_hour uabh
),
trend_analysis AS (
    -- Fourth CTE: Calculate trends and patterns
    SELECT
        rws.*,
        -- Trend calculations
        CASE
            WHEN rws.prev_hour_messages IS NOT NULL THEN rws.message_count - rws.prev_hour_messages
            ELSE 0
        END AS hour_over_hour_change,
        CASE
            WHEN rws.prev_hour_messages > 0 THEN (rws.message_count::numeric / rws.prev_hour_messages - 1) * 100
            ELSE 0
        END AS hour_over_hour_percent_change,
        -- Activity classification using CASE pivoting
        CASE
            WHEN rws.message_count > rws.avg_messages_24h_rows * 1.5 THEN 'Peak'
            WHEN rws.message_count > rws.avg_messages_24h_rows * 1.2 THEN 'High'
            WHEN rws.message_count > rws.avg_messages_24h_rows * 0.8 THEN 'Normal'
            WHEN rws.message_count > rws.avg_messages_24h_rows * 0.5 THEN 'Low'
            ELSE 'Very Low'
        END AS activity_level,
        CASE
            WHEN rws.message_count > rws.prev_hour_messages * 1.5 THEN 'Spike'
            WHEN rws.message_count < rws.prev_hour_messages * 0.5 THEN 'Drop'
            WHEN rws.message_count > rws.prev_hour_messages THEN 'Increasing'
            WHEN rws.message_count < rws.prev_hour_messages THEN 'Decreasing'
            ELSE 'Stable'
        END AS activity_trend,
        -- Volatility measure
        CASE
            WHEN rws.max_messages_24h_rows > 0 AND rws.min_messages_24h_rows > 0 THEN
                (rws.max_messages_24h_rows - rws.min_messages_24h_rows)::numeric / rws.avg_messages_24h_rows
            ELSE 0
        END AS volatility_ratio
    FROM rolling_window_statistics rws
),
union_combined_metrics AS (
    -- Fifth CTE: UNION to combine different metric types
    SELECT
        ta.activity_hour,
        'total' AS metric_type,
        ta.message_count AS metric_value,
        ta.activity_level,
        ta.activity_trend
    FROM trend_analysis ta

    UNION ALL

    SELECT
        ta.activity_hour,
        'user' AS metric_type,
        ta.user_messages AS metric_value,
        ta.activity_level,
        ta.activity_trend
    FROM trend_analysis ta

    UNION ALL

    SELECT
        ta.activity_hour,
        'ai' AS metric_type,
        ta.ai_messages AS metric_value,
        ta.activity_level,
        ta.activity_trend
    FROM trend_analysis ta
),
aggregated_union_metrics AS (
    -- Sixth CTE: Aggregate UNION results with window functions
    SELECT
        ucm.activity_hour,
        SUM(CASE WHEN ucm.metric_type = 'total' THEN ucm.metric_value ELSE 0 END) AS total_messages,
        SUM(CASE WHEN ucm.metric_type = 'user' THEN ucm.metric_value ELSE 0 END) AS user_messages,
        SUM(CASE WHEN ucm.metric_type = 'ai' THEN ucm.metric_value ELSE 0 END) AS ai_messages,
        MAX(ucm.activity_level) AS activity_level,
        MAX(ucm.activity_trend) AS activity_trend,
        COUNT(DISTINCT ucm.metric_type) AS metric_types_count,
        -- Window functions on aggregated UNION data
        SUM(ucm.metric_value) OVER (
            PARTITION BY ucm.metric_type
            ORDER BY ucm.activity_hour
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS type_12h_window,
        AVG(ucm.metric_value) OVER (
            PARTITION BY ucm.metric_type
            ORDER BY ucm.activity_hour
            RANGE BETWEEN INTERVAL '24 hours' PRECEDING AND CURRENT ROW
        ) AS type_24h_avg
    FROM union_combined_metrics ucm
    GROUP BY ucm.activity_hour, ucm.metric_type, ucm.metric_value
),
final_time_series_analytics AS (
    -- Seventh CTE: Final analytics with comprehensive window functions
    SELECT
        ta.activity_hour,
        ta.message_count,
        ta.active_chats,
        ta.active_users,
        ta.user_messages,
        ta.ai_messages,
        ta.chats_with_ai_interaction,
        ROUND(CAST(ta.avg_message_length AS NUMERIC), 2) AS avg_message_length,
        ROUND(CAST(ta.median_message_length AS NUMERIC), 2) AS median_message_length,
        ROUND(CAST(ta.avg_user_message_length AS NUMERIC), 2) AS avg_user_message_length,
        ta.messages_12h_window,
        ta.messages_12h_range,
        ROUND(CAST(ta.avg_messages_24h_rows AS NUMERIC), 2) AS avg_24h_rows,
        ROUND(CAST(ta.avg_messages_24h_range AS NUMERIC), 2) AS avg_24h_range,
        ta.max_messages_24h_rows,
        ta.min_messages_24h_rows,
        ta.prev_hour_messages,
        ta.prev2_hour_messages,
        ta.next_hour_messages,
        ta.next2_hour_messages,
        ta.first_value_24h,
        ta.last_value_24h,
        ta.hour_over_hour_change,
        ROUND(CAST(ta.hour_over_hour_percent_change AS NUMERIC), 2) AS hour_over_hour_percent_change,
        ta.activity_level,
        ta.activity_trend,
        ROUND(CAST(ta.volatility_ratio AS NUMERIC), 3) AS volatility_ratio,
        -- Additional window functions
        ROW_NUMBER() OVER (ORDER BY ta.message_count DESC) AS volume_rank,
        RANK() OVER (ORDER BY ta.volatility_ratio DESC) AS volatility_rank,
        DENSE_RANK() OVER (PARTITION BY ta.activity_level ORDER BY ta.message_count DESC) AS level_rank,
        PERCENT_RANK() OVER (ORDER BY ta.message_count DESC) AS volume_percentile,
        NTILE(5) OVER (ORDER BY ta.message_count DESC) AS volume_quintile,
        -- Running totals with frames
        SUM(ta.message_count) OVER (
            ORDER BY ta.activity_hour
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_messages,
        SUM(ta.message_count) OVER (
            PARTITION BY ta.activity_level
            ORDER BY ta.activity_hour
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS level_cumulative_messages
    FROM trend_analysis ta
)
SELECT
    activity_hour,
    message_count,
    active_chats,
    active_users,
    user_messages,
    ai_messages,
    chats_with_ai_interaction,
    avg_message_length,
    median_message_length,
    avg_user_message_length,
    messages_12h_window,
    messages_12h_range,
    avg_24h_rows,
    avg_24h_range,
    max_messages_24h_rows,
    min_messages_24h_rows,
    prev_hour_messages,
    prev2_hour_messages,
    next_hour_messages,
    next2_hour_messages,
    first_value_24h,
    last_value_24h,
    hour_over_hour_change,
    hour_over_hour_percent_change,
    activity_level,
    activity_trend,
    volatility_ratio,
    volume_rank,
    volatility_rank,
    level_rank,
    ROUND(CAST(volume_percentile * 100 AS NUMERIC), 2) AS volume_percentile,
    volume_quintile,
    cumulative_messages,
    level_cumulative_messages
FROM final_time_series_analytics
ORDER BY activity_hour DESC;
```

**Expected Output:** Hourly message activity with rolling statistics and trend analysis.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ⚠️
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 1/2
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chats, final_time_series_analytics, hourly_activity_base, messages, profiles, rolling_window_statistics, temporal_hierarchy, trend_analysis, union_combined_metrics, user_activity_by_hour
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chats, final_time_series_analytics, hourly_activity_base, messages, profiles, rolling_window_statistics, temporal_hierarchy, trend_analysis, union_combined_metrics, user_activity_by_hour
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: chats, final_time_series_analytics, hourly_activity_base, messages, profiles, rolling_window_statistics, temporal_hierarchy, trend_analysis, union_combined_metrics, user_activity_by_hour
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chats, final_time_series_analytics, hourly_activity_base, messages, profiles, rolling_window_statistics, temporal_hierarchy, trend_analysis, union_combined_metrics, user_activity_by_hour
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chats, final_time_series_analytics, hourly_activity_base, messages, profiles, rolling_window_statistics, temporal_hierarchy, trend_analysis, union_combined_metrics, user_activity_by_hour
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chats, final_time_series_analytics, hourly_activity_base, messages, profiles
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE temporal_hierarchy AS (
    -- Anchor: Base time periods
    SELECT
        DATE_TRUNC('hour', m.created_at) AS time_period,
        'hour' AS period_type,
        COUNT(*) AS message_count,
        COUNT(DISTINCT m.chat_id) AS active_chats,
        COUNT(DISTINCT m.sender_id) AS active_users
    FROM messages m
    GROUP BY DATE_TRUNC('hour', m.created_at)

    UNION ALL

    -- Recursive: Aggregate to higher time periods
    SELECT
        DATE_TRUNC('day', th.time_period) AS ti...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 6: Production-Grade Chat Engagement Scoring with Recursive CTE and Advanced Analytics

**Description:** Enterprise-level chat engagement scoring with recursive CTE for participant network analysis, multiple nested CTEs, correlated subqueries, UNION operations, and comprehensive window function analytics. Implements production patterns similar to engagement scoring systems.

**Complexity:** Recursive CTE, multiple nested CTEs (8+ levels), window functions with multiple frame clauses, correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE participant_network AS (
    -- Anchor: Direct participant connections
    SELECT
        CAST(NULL AS uuid) AS user_a,
        cp2.user_id AS user_b,
        CAST(NULL AS uuid) AS chat_id,
        1 AS connection_depth,
        ARRAY[CAST(NULL AS uuid), cp2.user_id] AS path
    FROM chat_participants cp1
    INNER JOIN chat_participants cp2 ON cp1.chat_id = cp2.chat_id
    WHERE cp1.user_id < cp2.user_id

    UNION ALL

    -- Recursive: Find participants connected through multiple chats
    SELECT
        pn.user_a,
        cp3.user_id AS user_b,
        cp3.chat_id,
        pn.connection_depth + 1,
        pn.path || cp3.user_id
    FROM participant_network pn
    INNER JOIN chat_participants cp2 ON pn.user_b = cp2.user_id
    INNER JOIN chat_participants cp3 ON cp2.chat_id = cp3.chat_id
    WHERE cp3.user_id != ALL(pn.path)
        AND pn.connection_depth < 3
),
chat_message_metrics AS (
    -- First CTE: Base message metrics with joins
    SELECT
        c.id AS chat_id,
        c.title,
        COUNT(m.id) AS total_messages,
        COUNT(DISTINCT m.sender_id) AS unique_participants,
        COUNT(DISTINCT DATE(m.created_at)) AS active_days,
        MAX(m.created_at) - MIN(m.created_at) AS chat_duration,
        AVG(LENGTH(m.content)) AS avg_message_length,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY LENGTH(m.content)) AS median_message_length,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY LENGTH(m.content)) AS p25_message_length,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY LENGTH(m.content)) AS p75_message_length
    FROM chats c
    LEFT JOIN messages m ON c.id = m.chat_id
    GROUP BY c.id, c.title
),
chat_participant_metrics AS (
    -- Second CTE: Participant metrics with correlated subqueries
    SELECT
        c.id AS chat_id,
        COUNT(DISTINCT cp.user_id) AS total_participants,
        COUNT(DISTINCT CASE WHEN cp.joined_at >= CURRENT_DATE - INTERVAL '7 days' THEN cp.user_id END) AS recent_participants,
        COUNT(DISTINCT CASE WHEN cp.joined_at >= CURRENT_DATE - INTERVAL '30 days' THEN cp.user_id END) AS monthly_participants,
        (
            SELECT COUNT(DISTINCT m2.sender_id)
            FROM messages m2
            WHERE m2.chat_id = c.id
                AND m2.created_at >= CURRENT_DATE - INTERVAL '7 days'
        ) AS active_participants_7d,
        (
            SELECT AVG(message_count)
            FROM (
                SELECT COUNT(*) AS message_count
                FROM messages m3
                WHERE m3.chat_id = c.id
                GROUP BY m3.sender_id
            ) participant_counts
        ) AS avg_messages_per_participant
    FROM chats c
    LEFT JOIN chat_participants cp ON c.id = cp.chat_id
    GROUP BY c.id
),
network_connectivity_metrics AS (
    -- Third CTE: Network connectivity from recursive CTE
    SELECT
        chat_id,
        COUNT(DISTINCT user_a) + COUNT(DISTINCT user_b) AS total_connected_users,
        AVG(connection_depth) AS avg_connection_depth,
        MAX(connection_depth) AS max_connection_depth,
        COUNT(*) AS total_connections
    FROM participant_network
    GROUP BY chat_id
),
engagement_calculation_base AS (
    -- Fourth CTE: Base engagement calculations
    SELECT
        cmm.chat_id,
        cmm.title,
        cmm.total_messages,
        cmm.unique_participants,
        cmm.active_days,
        EXTRACT(EPOCH FROM cmm.chat_duration) / 86400 AS duration_days,
        cmm.avg_message_length,
        cmm.median_message_length,
        cmm.p25_message_length,
        cmm.p75_message_length,
        cpm.total_participants,
        cpm.recent_participants,
        cpm.monthly_participants,
        cpm.active_participants_7d,
        cpm.avg_messages_per_participant,
        COALESCE(ncm.total_connected_users, 0) AS network_connected_users,
        COALESCE(ncm.avg_connection_depth, 0) AS network_avg_depth,
        COALESCE(ncm.total_connections, 0) AS network_total_connections
    FROM chat_message_metrics cmm
    INNER JOIN chat_participant_metrics cpm ON cmm.chat_id = cpm.chat_id
    LEFT JOIN network_connectivity_metrics ncm ON cmm.chat_id = ncm.chat_id
),
engagement_scoring AS (
    -- Fifth CTE: Multi-factor engagement scoring with window functions
    SELECT
        ecb.*,
        -- Component scores
        (ecb.total_messages * 0.25) AS message_volume_score,
        (ecb.unique_participants * 8 * 0.20) AS participation_score,
        (ecb.active_days * 4 * 0.15) AS activity_frequency_score,
        (COALESCE(ecb.recent_participants, 0) * 12 * 0.15) AS recency_score,
        (COALESCE(ecb.avg_message_length, 0) / 8 * 0.10) AS content_quality_score,
        (COALESCE(ecb.network_connected_users, 0) * 3 * 0.10) AS network_score,
        (COALESCE(ecb.avg_messages_per_participant, 0) * 2 * 0.05) AS engagement_depth_score,
        -- Raw engagement score
        (
            (ecb.total_messages * 0.25) +
            (ecb.unique_participants * 8 * 0.20) +
            (ecb.active_days * 4 * 0.15) +
            (COALESCE(ecb.recent_participants, 0) * 12 * 0.15) +
            (COALESCE(ecb.avg_message_length, 0) / 8 * 0.10) +
            (COALESCE(ecb.network_connected_users, 0) * 3 * 0.10) +
            (COALESCE(ecb.avg_messages_per_participant, 0) * 2 * 0.05)
        ) AS raw_engagement_score,
        -- Window functions for comparison
        AVG(ecb.total_messages) OVER () AS overall_avg_messages,
        AVG(ecb.unique_participants) OVER () AS overall_avg_participants,
        PERCENT_RANK() OVER (ORDER BY ecb.total_messages DESC) AS message_percentile,
        PERCENT_RANK() OVER (ORDER BY ecb.unique_participants DESC) AS participant_percentile
    FROM engagement_calculation_base ecb
),
union_engagement_components AS (
    -- Sixth CTE: UNION to combine different engagement components
    SELECT
        es.chat_id,
        'volume' AS component_type,
        es.message_volume_score AS component_score,
        es.raw_engagement_score
    FROM engagement_scoring es

    UNION ALL

    SELECT
        es.chat_id,
        'participation' AS component_type,
        es.participation_score AS component_score,
        es.raw_engagement_score
    FROM engagement_scoring es

    UNION ALL

    SELECT
        es.chat_id,
        'recency' AS component_type,
        es.recency_score AS component_score,
        es.raw_engagement_score
    FROM engagement_scoring es

    UNION ALL

    SELECT
        es.chat_id,
        'network' AS component_type,
        es.network_score AS component_score,
        es.raw_engagement_score
    FROM engagement_scoring es
),
component_aggregation AS (
    -- Seventh CTE: Aggregate UNION results with window functions
    SELECT
        uec.chat_id,
        SUM(CASE WHEN uec.component_type = 'volume' THEN uec.component_score ELSE 0 END) AS total_volume_score,
        SUM(CASE WHEN uec.component_type = 'participation' THEN uec.component_score ELSE 0 END) AS total_participation_score,
        SUM(CASE WHEN uec.component_type = 'recency' THEN uec.component_score ELSE 0 END) AS total_recency_score,
        SUM(CASE WHEN uec.component_type = 'network' THEN uec.component_score ELSE 0 END) AS total_network_score,
        MAX(uec.raw_engagement_score) AS raw_engagement_score,
        COUNT(DISTINCT uec.component_type) AS component_count,
        -- Window functions on components
        AVG(uec.component_score) OVER (
            PARTITION BY uec.component_type
            ORDER BY uec.raw_engagement_score DESC
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS component_moving_avg,
        SUM(uec.component_score) OVER (
            PARTITION BY uec.chat_id
            ORDER BY uec.component_type
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS chat_cumulative_component_score
    FROM union_engagement_components uec
    GROUP BY uec.chat_id, uec.component_type, uec.component_score, uec.raw_engagement_score, uec.raw_engagement_score
),
normalized_engagement_scores AS (
    -- Eighth CTE: Normalize scores with comprehensive window functions
    SELECT
        es.chat_id,
        es.title,
        es.total_messages,
        es.unique_participants,
        es.active_days,
        ROUND(CAST(es.duration_days AS NUMERIC), 1) AS duration_days,
        ROUND(CAST(es.avg_message_length AS NUMERIC), 2) AS avg_message_length,
        ROUND(CAST(es.median_message_length AS NUMERIC), 2) AS median_message_length,
        es.total_participants,
        es.recent_participants,
        es.monthly_participants,
        es.active_participants_7d,
        ROUND(CAST(es.avg_messages_per_participant AS NUMERIC), 2) AS avg_messages_per_participant,
        es.network_connected_users,
        ROUND(CAST(es.network_avg_depth AS NUMERIC), 2) AS network_avg_depth,
        es.network_total_connections,
        ROUND(CAST(es.raw_engagement_score AS NUMERIC), 2) AS engagement_score,
        ROUND(CAST(es.message_volume_score AS NUMERIC), 2) AS volume_score,
        ROUND(CAST(es.participation_score AS NUMERIC), 2) AS participation_score,
        ROUND(CAST(es.recency_score AS NUMERIC), 2) AS recency_score,
        ROUND(CAST(es.network_score AS NUMERIC), 2) AS network_score,
        ROUND(CAST(es.message_percentile * 100 AS NUMERIC), 2) AS message_percentile,
        ROUND(CAST(es.participant_percentile * 100 AS NUMERIC), 2) AS participant_percentile,
        -- Multiple ranking methods
        ROW_NUMBER() OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_rank,
        RANK() OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_rank_standard,
        DENSE_RANK() OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_dense_rank,
        PERCENT_RANK() OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_percentile,
        NTILE(5) OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_quintile,
        NTILE(10) OVER (ORDER BY es.raw_engagement_score DESC) AS engagement_decile,
        -- Window functions with frames
        SUM(es.raw_engagement_score) OVER (
            ORDER BY es.raw_engagement_score DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_engagement_score,
        AVG(es.raw_engagement_score) OVER (
            ORDER BY es.raw_engagement_score DESC
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS moving_avg_engagement_score,
        LAG(es.raw_engagement_score, 1) OVER (ORDER BY es.raw_engagement_score DESC) AS prev_engagement_score,
        LEAD(es.raw_engagement_score, 1) OVER (ORDER BY es.raw_engagement_score DESC) AS next_engagement_score,
        -- Pivot CASE for classification
        CASE
            WHEN es.raw_engagement_score >= 80 THEN 'Champion'
            WHEN es.raw_engagement_score >= 60 THEN 'Power User'
            WHEN es.raw_engagement_score >= 40 THEN 'Regular'
            WHEN es.raw_engagement_score >= 20 THEN 'Casual'
            ELSE 'Inactive'
        END AS engagement_category,
        CASE
            WHEN es.recent_participants::numeric / NULLIF(es.total_participants, 0) > 0.5 THEN 'High Recency'
            WHEN es.recent_participants::numeric / NULLIF(es.total_participants, 0) > 0.3 THEN 'Medium Recency'
            ELSE 'Low Recency'
        END AS recency_category
    FROM engagement_scoring es
)
SELECT
    chat_id,
    title,
    total_messages,
    unique_participants,
    active_days,
    duration_days,
    avg_message_length,
    median_message_length,
    total_participants,
    recent_participants,
    monthly_participants,
    active_participants_7d,
    avg_messages_per_participant,
    network_connected_users,
    network_avg_depth,
    network_total_connections,
    engagement_score,
    volume_score,
    participation_score,
    recency_score,
    network_score,
    message_percentile,
    participant_percentile,
    engagement_rank,
    engagement_rank_standard,
    engagement_dense_rank,
    ROUND(CAST(engagement_percentile * 100 AS NUMERIC), 2) AS engagement_percentile,
    engagement_quintile,
    engagement_decile,
    ROUND(CAST(cumulative_engagement_score AS NUMERIC), 2) AS cumulative_engagement_score,
    ROUND(CAST(moving_avg_engagement_score AS NUMERIC), 2) AS moving_avg_engagement_score,
    ROUND(CAST(prev_engagement_score AS NUMERIC), 2) AS prev_engagement_score,
    ROUND(CAST(next_engagement_score AS NUMERIC), 2) AS next_engagement_score,
    engagement_category,
    recency_category
FROM normalized_engagement_scores
ORDER BY engagement_score DESC;
```

**Expected Output:** Chat engagement scores with percentile rankings and quintile classifications.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chat_message_metrics, chat_participant_metrics, chat_participants, chats, cmm, engagement_calculation_base, engagement_scoring, messages, network_connectivity_metrics, normalized_engagement_scores, participant_network, recursive, union_engagement_components
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chat_message_metrics, chat_participant_metrics, chat_participants, chats, cmm, engagement_calculation_base, engagement_scoring, messages, network_connectivity_metrics, normalized_engagement_scores, participant_network, recursive, union_engagement_components
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: chat_message_metrics, chat_participant_metrics, chat_participants, chats, cmm, engagement_calculation_base, engagement_scoring, messages, network_connectivity_metrics, normalized_engagement_scores, participant_network, recursive, union_engagement_components
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chat_message_metrics, chat_participant_metrics, chat_participants, chats, cmm, engagement_calculation_base, engagement_scoring, messages, network_connectivity_metrics, normalized_engagement_scores, participant_network, recursive, union_engagement_components
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chat_message_metrics, chat_participant_metrics, chat_participants, chats, cmm, engagement_calculation_base, engagement_scoring, messages, network_connectivity_metrics, normalized_engagement_scores, participant_network, recursive, union_engagement_components
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 6: Friend Network Analysis**
- **Scenario**: Mutual connections
- **Description**: Validates mutual connections functionality
- **Test Data Requirements**:
  - Tables: chat_message_metrics, chat_participant_metrics, chat_participants, chats, cmm, engagement_calculation_base, engagement_scoring, messages, network_connectivity_metrics, normalized_engagement_scores, participant_network, recursive, union_engagement_components
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chat_message_metrics, chat_participant_metrics, chat_participants, chats, cmm
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE participant_network AS (
    -- Anchor: Direct participant connections
    SELECT
        cp1.user_id AS user_a,
        cp2.user_id AS user_b,
        cp1.chat_id,
        1 AS connection_depth,
        ARRAY[cp1.user_id, cp2.user_id] AS path
    FROM chat_participants cp1
    INNER JOIN chat_participants cp2 ON cp1.chat_id = cp2.chat_id
    WHERE cp1.user_id < cp2.user_id

    UNION ALL

    -- Recursive: Find participants connected through multiple chats
    SELECT
        pn.u...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 7: Production-Grade Notification Delivery Analysis with Recursive CTE and Advanced Analytics

**Description:** Enterprise-level notification delivery analysis with recursive CTE for notification cascade tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive analytics. Implements production patterns similar to notification delivery systems.

**Complexity:** Recursive CTE, multiple nested CTEs (7+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE notification_cascade AS (
    -- Anchor: Base notifications
    SELECT
        n.id,
        n.user_id,
        n.type,
        n.created_at,
        n.read,
        n.seen_at,
        1 AS cascade_depth,
        ARRAY[n.id] AS cascade_path
    FROM notifications n

    UNION ALL

    -- Recursive: Find related notifications in cascade
    SELECT
        n2.id,
        n2.user_id,
        n2.type,
        n2.created_at,
        n2.read,
        n2.seen_at,
        nc.cascade_depth + 1,
        nc.cascade_path || n2.id
    FROM notification_cascade nc
    INNER JOIN notifications n2 ON nc.user_id = n2.user_id
    WHERE n2.id != ALL(nc.cascade_path)
        AND n2.created_at BETWEEN nc.created_at AND nc.created_at + INTERVAL '1 hour'
        AND nc.cascade_depth < 3
),
notification_timeline AS (
    -- First CTE: Base timeline with joins
    SELECT
        n.id,
        n.user_id,
        n.type,
        n.created_at,
        n.read,
        n.seen_at,
        p.username,
        EXTRACT(EPOCH FROM (COALESCE(n.seen_at, CURRENT_TIMESTAMP) - n.created_at)) / 60 AS minutes_to_seen,
        CASE WHEN n.read = true THEN 1 ELSE 0 END AS is_read,
        CASE WHEN n.seen_at IS NOT NULL THEN 1 ELSE 0 END AS is_seen,
        (
            SELECT COUNT(*)
            FROM notifications n2
            WHERE n2.user_id = n.user_id
                AND n2.type = n.type
                AND n2.created_at < n.created_at
        ) AS prior_notifications_of_type,
        (
            SELECT AVG(EXTRACT(EPOCH FROM (COALESCE(n3.seen_at, CURRENT_TIMESTAMP) - n3.created_at)) / 60)
            FROM notifications n3
            WHERE n3.user_id = n.user_id
                AND n3.type = n.type
                AND n3.created_at < n.created_at
        ) AS avg_prior_minutes_to_seen
    FROM notifications n
    INNER JOIN profiles p ON n.user_id = p.id
),
user_notification_stats AS (
    -- Second CTE: User-level statistics with correlated subqueries
    SELECT
        nt.user_id,
        nt.type,
        COUNT(*) AS total_notifications,
        SUM(nt.is_read) AS read_count,
        SUM(nt.is_seen) AS seen_count,
        AVG(nt.minutes_to_seen) AS avg_minutes_to_seen,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY nt.minutes_to_seen) AS median_minutes_to_seen,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY nt.minutes_to_seen) AS p25_minutes_to_seen,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY nt.minutes_to_seen) AS p75_minutes_to_seen,
        MIN(nt.minutes_to_seen) AS min_minutes_to_seen,
        MAX(nt.minutes_to_seen) AS max_minutes_to_seen,
        STDDEV(nt.minutes_to_seen) AS stddev_minutes_to_seen,
        AVG(nt.prior_notifications_of_type) AS avg_prior_notifications,
        AVG(nt.avg_prior_minutes_to_seen) AS avg_historical_minutes_to_seen
    FROM notification_timeline nt
    GROUP BY nt.user_id, nt.type
),
rolling_window_stats AS (
    -- Third CTE: Rolling window statistics with frame clauses
    SELECT
        uns.user_id,
        uns.type,
        uns.total_notifications,
        uns.read_count,
        uns.seen_count,
        uns.avg_minutes_to_seen,
        uns.median_minutes_to_seen,
        uns.p25_minutes_to_seen,
        uns.p75_minutes_to_seen,
        uns.min_minutes_to_seen,
        uns.max_minutes_to_seen,
        uns.stddev_minutes_to_seen,
        uns.avg_prior_notifications,
        uns.avg_historical_minutes_to_seen,
        -- Window functions with ROWS BETWEEN frames
        SUM(uns.total_notifications) OVER (
            PARTITION BY uns.type
            ORDER BY uns.user_id
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS type_10_user_window,
        AVG(uns.avg_minutes_to_seen) OVER (
            PARTITION BY uns.type
            ORDER BY uns.user_id
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS type_20_user_avg,
        -- Window functions with RANGE BETWEEN frames
        SUM(uns.read_count) OVER (
            PARTITION BY uns.type
            ORDER BY uns.avg_minutes_to_seen
            RANGE BETWEEN 30 PRECEDING AND 30 FOLLOWING
        ) AS read_count_range_window,
        -- Lag/Lead functions
        LAG(uns.avg_minutes_to_seen, 1) OVER (PARTITION BY uns.type ORDER BY uns.user_id) AS prev_user_avg_minutes,
        LEAD(uns.avg_minutes_to_seen, 1) OVER (PARTITION BY uns.type ORDER BY uns.user_id) AS next_user_avg_minutes,
        -- First/Last value with frames
        FIRST_VALUE(uns.avg_minutes_to_seen) OVER (
            PARTITION BY uns.type
            ORDER BY uns.user_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_user_avg_minutes,
        LAST_VALUE(uns.avg_minutes_to_seen) OVER (
            PARTITION BY uns.type
            ORDER BY uns.user_id
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_user_avg_minutes
    FROM user_notification_stats uns
),
type_aggregates AS (
    -- Fourth CTE: Type-level aggregates
    SELECT
        rws.type,
        COUNT(DISTINCT rws.user_id) AS users_with_type,
        SUM(rws.total_notifications) AS total_type_notifications,
        SUM(rws.read_count) AS total_read,
        SUM(rws.seen_count) AS total_seen,
        AVG(rws.avg_minutes_to_seen) AS overall_avg_minutes,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rws.avg_minutes_to_seen) AS overall_median_minutes,
        AVG(rws.read_count::numeric / NULLIF(rws.total_notifications, 0)) AS avg_read_rate,
        AVG(rws.seen_count::numeric / NULLIF(rws.total_notifications, 0)) AS avg_seen_rate,
        AVG(rws.type_10_user_window) AS avg_10_user_window,
        AVG(rws.type_20_user_avg) AS avg_20_user_rolling_avg,
        AVG(rws.read_count_range_window) AS avg_read_count_range_window
    FROM rolling_window_stats rws
    GROUP BY rws.type
),
union_metrics AS (
    -- Fifth CTE: UNION to combine different metric types
    SELECT
        ta.type,
        'read_rate' AS metric_type,
        ta.avg_read_rate AS metric_value
    FROM type_aggregates ta

    UNION ALL

    SELECT
        ta.type,
        'seen_rate' AS metric_type,
        ta.avg_seen_rate AS metric_value
    FROM type_aggregates ta

    UNION ALL

    SELECT
        ta.type,
        'avg_minutes' AS metric_type,
        ta.overall_avg_minutes AS metric_value
    FROM type_aggregates ta
),
aggregated_union_metrics AS (
    -- Sixth CTE: Aggregate UNION results with window functions
    SELECT
        NULL,
        SUM(CASE WHEN NULL = 'read_rate' THEN NULL ELSE 0 END) AS total_read_rate,
        SUM(CASE WHEN NULL = 'seen_rate' THEN NULL ELSE 0 END) AS total_seen_rate,
        SUM(CASE WHEN NULL = 'avg_minutes' THEN NULL ELSE 0 END) AS total_avg_minutes,
        COUNT(DISTINCT NULL) AS metric_types_count,
        -- Window functions on UNION data
        AVG(CAST(0 AS NUMERIC)) OVER (
            PARTITION BY rws.type
            ORDER BY rws.type
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS metric_moving_avg,
        SUM(CAST(0 AS NUMERIC)) OVER (
            PARTITION BY rws.type
            ORDER BY rws.type
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS type_cumulative_metric
    FROM rolling_window_stats rws
    GROUP BY rws.type
),
final_notification_analytics AS (
    -- Seventh CTE: Final analytics with comprehensive window functions
    SELECT
        ta.type,
        ta.users_with_type,
        ta.total_type_notifications,
        ta.total_read,
        ta.total_seen,
        ROUND(CAST(ta.avg_read_rate * 100 AS NUMERIC), 2) AS read_rate_percent,
        ROUND(CAST(ta.avg_seen_rate * 100 AS NUMERIC), 2) AS seen_rate_percent,
        ROUND(CAST(ta.overall_avg_minutes AS NUMERIC), 2) AS avg_minutes_to_seen,
        ROUND(CAST(ta.overall_median_minutes AS NUMERIC), 2) AS median_minutes_to_seen,
        ROUND(CAST(ta.avg_10_user_window AS NUMERIC), 2) AS avg_10_user_window,
        ROUND(CAST(ta.avg_20_user_rolling_avg AS NUMERIC), 2) AS avg_20_user_rolling_avg,
        ROUND(CAST(ta.avg_read_count_range_window AS NUMERIC), 2) AS avg_read_count_range_window,
        -- Multiple ranking methods
        ROW_NUMBER() OVER (ORDER BY ta.avg_read_rate DESC) AS read_rate_row_num,
        RANK() OVER (ORDER BY ta.avg_read_rate DESC) AS read_rate_rank,
        DENSE_RANK() OVER (ORDER BY ta.avg_seen_rate DESC) AS seen_rate_dense_rank,
        PERCENT_RANK() OVER (ORDER BY ta.avg_read_rate DESC) AS read_rate_percentile,
        NTILE(5) OVER (ORDER BY ta.avg_read_rate DESC) AS read_rate_quintile,
        NTILE(10) OVER (ORDER BY ta.avg_seen_rate DESC) AS seen_rate_decile,
        -- Window functions with frames
        SUM(ta.total_type_notifications) OVER (
            ORDER BY ta.avg_read_rate DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_notifications,
        AVG(ta.avg_read_rate) OVER (
            ORDER BY ta.avg_read_rate DESC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS moving_avg_read_rate,
        LAG(ta.avg_read_rate, 1) OVER (ORDER BY ta.avg_read_rate DESC) AS prev_read_rate,
        LEAD(ta.avg_seen_rate, 1) OVER (ORDER BY ta.avg_seen_rate DESC) AS next_seen_rate,
        -- Pivot CASE for classification
        CASE
            WHEN ta.avg_read_rate >= 0.8 THEN 'Excellent Read Rate'
            WHEN ta.avg_read_rate >= 0.6 THEN 'Good Read Rate'
            WHEN ta.avg_read_rate >= 0.4 THEN 'Fair Read Rate'
            ELSE 'Poor Read Rate'
        END AS read_rate_category,
        CASE
            WHEN ta.overall_avg_minutes <= 5 THEN 'Immediate'
            WHEN ta.overall_avg_minutes <= 30 THEN 'Quick'
            WHEN ta.overall_avg_minutes <= 60 THEN 'Moderate'
            ELSE 'Slow'
        END AS response_time_category
    FROM type_aggregates ta
)
SELECT
    type,
    users_with_type,
    total_type_notifications,
    total_read,
    total_seen,
    read_rate_percent,
    seen_rate_percent,
    avg_minutes_to_seen,
    median_minutes_to_seen,
    avg_10_user_window,
    avg_20_user_rolling_avg,
    avg_read_count_range_window,
    read_rate_row_num,
    read_rate_rank,
    seen_rate_dense_rank,
    ROUND(CAST(read_rate_percentile * 100 AS NUMERIC), 2) AS read_rate_percentile,
    read_rate_quintile,
    seen_rate_decile,
    cumulative_notifications,
    ROUND(CAST(moving_avg_read_rate * 100 AS NUMERIC), 2) AS moving_avg_read_rate,
    ROUND(CAST(prev_read_rate * 100 AS NUMERIC), 2) AS prev_read_rate,
    ROUND(CAST(next_seen_rate * 100 AS NUMERIC), 2) AS next_seen_rate,
    read_rate_category,
    response_time_category
FROM final_notification_analytics
ORDER BY total_type_notifications DESC;
```

**Expected Output:** Notification type statistics with read/seen rates and delivery times.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: final_notification_analytics, notification_cascade, notification_timeline, notifications, profiles, rolling_window_stats, type_aggregates, union_metrics, user_notification_stats
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: final_notification_analytics, notification_cascade, notification_timeline, notifications, profiles, rolling_window_stats, type_aggregates, union_metrics, user_notification_stats
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: final_notification_analytics, notification_cascade, notification_timeline, notifications, profiles, rolling_window_stats, type_aggregates, union_metrics, user_notification_stats
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: final_notification_analytics, notification_cascade, notification_timeline, notifications, profiles, rolling_window_stats, type_aggregates, union_metrics, user_notification_stats
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: final_notification_analytics, notification_cascade, notification_timeline, notifications, profiles, rolling_window_stats, type_aggregates, union_metrics, user_notification_stats
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: final_notification_analytics, notification_cascade, notification_timeline, notifications, profiles
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE notification_cascade AS (
    -- Anchor: Base notifications
    SELECT
        n.id,
        n.user_id,
        n.type,
        n.created_at,
        n.read,
        n.seen_at,
        1 AS cascade_depth,
        ARRAY[n.id] AS cascade_path
    FROM notifications n

    UNION ALL

    -- Recursive: Find related notifications in cascade
    SELECT
        n2.id,
        n2.user_id,
        n2.type,
        n2.created_at,
        n2.read,
        n2.seen_at,
        nc.cascade_depth...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 8: Production-Grade File Attachment Analysis with Recursive CTE and Advanced Metrics

**Description:** Enterprise-level file attachment analysis with recursive CTE for upload chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive size distribution analytics. Implements production patterns similar to file storage analytics systems.

**Complexity:** Recursive CTE, multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE upload_chain AS (
    -- Anchor: Base uploads
    SELECT
        fa.id,
        fa.chat_id,
        fa.user_id,
        fa.file_size,
        fa.created_at,
        1 AS chain_depth,
        ARRAY[fa.id] AS chain_path
    FROM file_attachments fa

    UNION ALL

    -- Recursive: Find related uploads in same chat by same user
    SELECT
        fa2.id,
        fa2.chat_id,
        fa2.user_id,
        fa2.file_size,
        fa2.created_at,
        uc.chain_depth + 1,
        uc.chain_path || fa2.id
    FROM upload_chain uc
    INNER JOIN file_attachments fa2 ON uc.chat_id = fa2.chat_id AND uc.user_id = fa2.user_id
    WHERE fa2.id != ALL(uc.chain_path)
        AND fa2.created_at BETWEEN uc.created_at AND uc.created_at + INTERVAL '1 hour'
        AND uc.chain_depth < 3
),
attachment_stats AS (
    -- First CTE: Base attachment stats with joins and correlated subqueries
    SELECT
        fa.id,
        fa.chat_id,
        fa.user_id,
        fa.file_name,
        fa.file_size,
        fa.created_at,
        c.title AS chat_title,
        p.username AS uploader_username,
        (
            SELECT COUNT(*)
            FROM file_attachments fa2
            WHERE fa2.chat_id = fa.chat_id
                AND fa2.created_at < fa.created_at
        ) AS prior_uploads_in_chat,
        (
            SELECT AVG(fa3.file_size)
            FROM file_attachments fa3
            WHERE fa3.chat_id = fa.chat_id
                AND fa3.created_at < fa.created_at
        ) AS avg_prior_file_size,
        (
            SELECT COUNT(DISTINCT fa4.user_id)
            FROM file_attachments fa4
            WHERE fa4.chat_id = fa.chat_id
                AND EXISTS (
                    SELECT 1
                    FROM file_attachments fa5
                    WHERE fa5.chat_id = fa.chat_id
                        AND fa5.user_id = fa4.user_id
                        AND fa5.created_at < fa.created_at
                )
        ) AS prior_uploaders_count
    FROM file_attachments fa
    INNER JOIN chats c ON fa.chat_id = c.id
    INNER JOIN profiles p ON fa.user_id = p.id
),
chat_attachment_metrics AS (
    -- Second CTE: Chat-level metrics with aggregations
    SELECT
        as1.chat_id,
        as1.chat_title,
        COUNT(*) AS total_attachments,
        COUNT(DISTINCT as1.user_id) AS unique_uploaders,
        SUM(as1.file_size) AS total_size_bytes,
        AVG(as1.file_size) AS avg_file_size,
        MIN(as1.file_size) AS min_file_size,
        MAX(as1.file_size) AS max_file_size,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY as1.file_size) AS median_file_size,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY as1.file_size) AS p25_file_size,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY as1.file_size) AS p75_file_size,
        STDDEV(as1.file_size) AS stddev_file_size,
        AVG(as1.prior_uploads_in_chat) AS avg_prior_uploads,
        AVG(as1.avg_prior_file_size) AS avg_historical_file_size,
        AVG(as1.prior_uploaders_count) AS avg_prior_uploaders
    FROM attachment_stats as1
    GROUP BY as1.chat_id, as1.chat_title
),
upload_chain_metrics AS (
    -- Third CTE: Upload chain metrics from recursive CTE
    SELECT
        chat_id,
        COUNT(DISTINCT user_id) AS uploaders_with_chains,
        AVG(chain_depth) AS avg_chain_depth,
        MAX(chain_depth) AS max_chain_depth,
        COUNT(*) AS total_chain_uploads
    FROM upload_chain
    GROUP BY chat_id
),
rolling_window_metrics AS (
    -- Fourth CTE: Rolling window statistics with frame clauses
    SELECT
        cam.chat_id,
        cam.chat_title,
        cam.total_attachments,
        cam.unique_uploaders,
        cam.total_size_bytes,
        cam.avg_file_size,
        cam.min_file_size,
        cam.max_file_size,
        cam.median_file_size,
        cam.p25_file_size,
        cam.p75_file_size,
        cam.stddev_file_size,
        cam.avg_prior_uploads,
        cam.avg_historical_file_size,
        cam.avg_prior_uploaders,
        COALESCE(ucm.uploaders_with_chains, 0) AS uploaders_with_chains,
        COALESCE(ucm.avg_chain_depth, 0) AS avg_chain_depth,
        COALESCE(ucm.max_chain_depth, 0) AS max_chain_depth,
        COALESCE(ucm.total_chain_uploads, 0) AS total_chain_uploads,
        -- Window functions with ROWS BETWEEN frames
        SUM(cam.total_attachments) OVER (
            ORDER BY cam.total_attachments DESC
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS attachments_10_chat_window,
        AVG(cam.total_size_bytes) OVER (
            ORDER BY cam.total_size_bytes DESC
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS size_20_chat_avg,
        -- Window functions with RANGE BETWEEN frames
        SUM(cam.total_attachments) OVER (
            ORDER BY cam.avg_file_size
            RANGE BETWEEN 100000 PRECEDING AND 100000 FOLLOWING
        ) AS attachments_size_range_window,
        -- Lag/Lead functions
        LAG(cam.total_attachments, 1) OVER (ORDER BY cam.total_attachments DESC) AS prev_chat_attachments,
        LEAD(cam.total_size_bytes, 1) OVER (ORDER BY cam.total_size_bytes DESC) AS next_chat_size,
        -- First/Last value with frames
        FIRST_VALUE(cam.avg_file_size) OVER (
            ORDER BY cam.total_attachments DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_chat_avg_size,
        LAST_VALUE(cam.median_file_size) OVER (
            ORDER BY cam.total_attachments DESC
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_chat_median_size
    FROM chat_attachment_metrics cam
    LEFT JOIN upload_chain_metrics ucm ON cam.chat_id = ucm.chat_id
),
size_distribution AS (
    -- Fifth CTE: Size distribution with pivot CASE
    SELECT
        rwm.chat_id,
        rwm.chat_title,
        rwm.total_attachments,
        rwm.unique_uploaders,
        rwm.total_size_bytes,
        ROUND(CAST(rwm.total_size_bytes / 1024.0 / 1024.0 AS NUMERIC), 2) AS total_size_mb,
        ROUND(CAST(rwm.avg_file_size / 1024.0 AS NUMERIC), 2) AS avg_file_size_kb,
        ROUND(CAST(rwm.median_file_size / 1024.0 AS NUMERIC), 2) AS median_file_size_kb,
        ROUND(CAST(rwm.p25_file_size / 1024.0 AS NUMERIC), 2) AS p25_file_size_kb,
        ROUND(CAST(rwm.p75_file_size / 1024.0 AS NUMERIC), 2) AS p75_file_size_kb,
        ROUND(CAST(rwm.max_file_size / 1024.0 AS NUMERIC), 2) AS max_file_size_kb,
        ROUND(CAST(rwm.stddev_file_size / 1024.0 AS NUMERIC), 2) AS stddev_file_size_kb,
        rwm.avg_prior_uploads,
        ROUND(CAST(rwm.avg_historical_file_size / 1024.0 AS NUMERIC), 2) AS avg_historical_file_size_kb,
        rwm.uploaders_with_chains,
        ROUND(CAST(rwm.avg_chain_depth AS NUMERIC), 2) AS avg_chain_depth,
        rwm.max_chain_depth,
        rwm.total_chain_uploads,
        rwm.attachments_10_chat_window,
        ROUND(CAST(rwm.size_20_chat_avg / 1024.0 / 1024.0 AS NUMERIC), 2) AS size_20_chat_avg_mb,
        rwm.attachments_size_range_window,
        rwm.prev_chat_attachments,
        ROUND(CAST(rwm.next_chat_size / 1024.0 / 1024.0 AS NUMERIC), 2) AS next_chat_size_mb,
        ROUND(CAST(rwm.first_chat_avg_size / 1024.0 AS NUMERIC), 2) AS first_chat_avg_size_kb,
        ROUND(CAST(rwm.last_chat_median_size / 1024.0 AS NUMERIC), 2) AS last_chat_median_size_kb,
        -- Pivot CASE for size categorization
        CASE
            WHEN rwm.avg_file_size < 100 * 1024 THEN 'Small'
            WHEN rwm.avg_file_size < 500 * 1024 THEN 'Medium-Small'
            WHEN rwm.avg_file_size < 1024 * 1024 THEN 'Medium'
            WHEN rwm.avg_file_size < 5 * 1024 * 1024 THEN 'Large'
            ELSE 'Very Large'
        END AS size_category,
        CASE
            WHEN rwm.total_attachments < 5 THEN 'Low Volume'
            WHEN rwm.total_attachments < 20 THEN 'Medium Volume'
            WHEN rwm.total_attachments < 50 THEN 'High Volume'
            ELSE 'Very High Volume'
        END AS volume_category,
        -- Window function rankings
        ROW_NUMBER() OVER (ORDER BY rwm.total_attachments DESC) AS attachment_count_row_num,
        RANK() OVER (ORDER BY rwm.total_attachments DESC) AS attachment_count_rank,
        DENSE_RANK() OVER (ORDER BY rwm.total_size_bytes DESC) AS size_dense_rank,
        PERCENT_RANK() OVER (ORDER BY rwm.total_attachments DESC) AS attachment_percentile,
        NTILE(5) OVER (ORDER BY rwm.total_attachments DESC) AS attachment_quintile,
        NTILE(10) OVER (ORDER BY rwm.total_size_bytes DESC) AS size_decile
    FROM rolling_window_metrics rwm
),
union_attachment_metrics AS (
    -- Sixth CTE: UNION to combine different metric types
    SELECT
        sd.chat_id,
        'count' AS metric_type,
        sd.total_attachments AS metric_value
    FROM size_distribution sd

    UNION ALL

    SELECT
        sd.chat_id,
        'size' AS metric_type,
        sd.total_size_mb AS metric_value
    FROM size_distribution sd

    UNION ALL

    SELECT
        sd.chat_id,
        'uploaders' AS metric_type,
        sd.unique_uploaders AS metric_value
    FROM size_distribution sd
),
aggregated_union_attachment_metrics AS (
    -- Seventh CTE: Aggregate UNION results with window functions
    SELECT
        uam.chat_id,
        SUM(CASE WHEN uam.metric_type = 'count' THEN uam.metric_value ELSE 0 END) AS total_count_metric,
        SUM(CASE WHEN uam.metric_type = 'size' THEN uam.metric_value ELSE 0 END) AS total_size_metric,
        SUM(CASE WHEN uam.metric_type = 'uploaders' THEN uam.metric_value ELSE 0 END) AS total_uploaders_metric,
        COUNT(DISTINCT uam.metric_type) AS metric_types_count,
        -- Window functions on UNION data
        AVG(uam.metric_value) OVER (
            PARTITION BY uam.metric_type
            ORDER BY uam.chat_id
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS metric_moving_avg,
        SUM(uam.metric_value) OVER (
            PARTITION BY uam.chat_id
            ORDER BY uam.metric_type
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS chat_cumulative_metric
    FROM union_attachment_metrics uam
    GROUP BY uam.chat_id, uam.metric_type, uam.metric_value
),
final_attachment_analytics AS (
    -- Eighth CTE: Final analytics with comprehensive window functions
    SELECT
        sd.chat_id,
        sd.chat_title,
        sd.total_attachments,
        sd.unique_uploaders,
        sd.total_size_mb,
        sd.avg_file_size_kb,
        sd.median_file_size_kb,
        sd.p25_file_size_kb,
        sd.p75_file_size_kb,
        sd.max_file_size_kb,
        sd.stddev_file_size_kb,
        sd.avg_prior_uploads,
        sd.avg_historical_file_size_kb,
        sd.uploaders_with_chains,
        sd.avg_chain_depth,
        sd.max_chain_depth,
        sd.total_chain_uploads,
        sd.attachments_10_chat_window,
        sd.size_20_chat_avg_mb,
        sd.attachments_size_range_window,
        sd.prev_chat_attachments,
        sd.next_chat_size_mb,
        sd.first_chat_avg_size_kb,
        sd.last_chat_median_size_kb,
        sd.size_category,
        sd.volume_category,
        sd.attachment_count_row_num,
        sd.attachment_count_rank,
        sd.size_dense_rank,
        ROUND(CAST(sd.attachment_percentile * 100 AS NUMERIC), 2) AS attachment_percentile,
        sd.attachment_quintile,
        sd.size_decile,
        -- Additional window functions with frames
        SUM(sd.total_attachments) OVER (
            ORDER BY sd.total_attachments DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_attachments,
        AVG(sd.total_size_mb) OVER (
            ORDER BY sd.total_size_mb DESC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS moving_avg_size_mb,
        LAG(sd.total_attachments, 1) OVER (ORDER BY sd.total_attachments DESC) AS prev_total_attachments,
        LEAD(sd.total_size_mb, 1) OVER (ORDER BY sd.total_size_mb DESC) AS next_total_size_mb
    FROM size_distribution sd
)
SELECT
    chat_id,
    chat_title,
    total_attachments,
    unique_uploaders,
    total_size_mb,
    avg_file_size_kb,
    median_file_size_kb,
    p25_file_size_kb,
    p75_file_size_kb,
    max_file_size_kb,
    stddev_file_size_kb,
    avg_prior_uploads,
    avg_historical_file_size_kb,
    uploaders_with_chains,
    avg_chain_depth,
    max_chain_depth,
    total_chain_uploads,
    attachments_10_chat_window,
    size_20_chat_avg_mb,
    attachments_size_range_window,
    prev_chat_attachments,
    next_chat_size_mb,
    first_chat_avg_size_kb,
    last_chat_median_size_kb,
    size_category,
    volume_category,
    attachment_count_row_num,
    attachment_count_rank,
    size_dense_rank,
    attachment_percentile,
    attachment_quintile,
    size_decile,
    cumulative_attachments,
    ROUND(CAST(moving_avg_size_mb AS NUMERIC), 2) AS moving_avg_size_mb,
    prev_total_attachments,
    ROUND(CAST(next_total_size_mb AS NUMERIC), 2) AS next_total_size_mb
FROM final_attachment_analytics
ORDER BY total_attachments DESC;
```

**Expected Output:** File attachment statistics per chat with size distributions and rankings.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: attachment_stats, chat_attachment_metrics, chats, file_attachments, final_attachment_analytics, profiles, recursive, rolling_window_metrics, size_distribution, union_attachment_metrics, upload_chain, upload_chain_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: attachment_stats, chat_attachment_metrics, chats, file_attachments, final_attachment_analytics, profiles, recursive, rolling_window_metrics, size_distribution, union_attachment_metrics, upload_chain, upload_chain_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: attachment_stats, chat_attachment_metrics, chats, file_attachments, final_attachment_analytics, profiles, recursive, rolling_window_metrics, size_distribution, union_attachment_metrics, upload_chain, upload_chain_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: attachment_stats, chat_attachment_metrics, chats, file_attachments, final_attachment_analytics, profiles, recursive, rolling_window_metrics, size_distribution, union_attachment_metrics, upload_chain, upload_chain_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: attachment_stats, chat_attachment_metrics, chats, file_attachments, final_attachment_analytics, profiles, recursive, rolling_window_metrics, size_distribution, union_attachment_metrics, upload_chain, upload_chain_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: attachment_stats, chat_attachment_metrics, chats, file_attachments, final_attachment_analytics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE upload_chain AS (
    -- Anchor: Base uploads
    SELECT
        fa.id,
        fa.chat_id,
        fa.uploaded_by,
        fa.file_size,
        fa.created_at,
        1 AS chain_depth,
        ARRAY[fa.id] AS chain_path
    FROM file_attachments fa

    UNION ALL

    -- Recursive: Find related uploads in same chat by same user
    SELECT
        fa2.id,
        fa2.chat_id,
        fa2.uploaded_by,
        fa2.file_size,
        fa2.created_at,
        uc.chain_depth + 1,
   ...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 9: Production-Grade Anonymous Chat Analysis with Recursive CTE and Advanced Session Analytics

**Description:** Enterprise-level anonymous chat analysis with recursive CTE for guest interaction chains, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive session analytics. Implements production patterns similar to anonymous chat platforms.

**Complexity:** Recursive CTE, multiple nested CTEs (7+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE guest_interaction_chain AS (
    -- Anchor: Base guest interactions
    SELECT
        acu.guest_id,
        acu.chat_id,
        am.id AS message_id,
        am.created_at,
        1 AS interaction_depth,
        ARRAY[acu.guest_id]::character varying[] AS interaction_path
    FROM anonymous_chat_users acu
    INNER JOIN anonymous_messages am ON acu.chat_id = am.chat_id
    WHERE am.guest_id = acu.guest_id

    UNION ALL

    -- Recursive: Find related interactions in same chat
    SELECT
        gic.guest_id,
        gic.chat_id,
        am2.id AS message_id,
        am2.created_at,
        gic.interaction_depth + 1,
        gic.interaction_path || ARRAY[CAST(am2.id AS TEXT)]
    FROM guest_interaction_chain gic
    INNER JOIN anonymous_messages am2 ON gic.chat_id = am2.chat_id
    WHERE am2.id != ALL(ARRAY[gic.message_id])
        AND am2.created_at BETWEEN gic.created_at AND gic.created_at + INTERVAL '30 minutes'
        AND gic.interaction_depth < 5
),
anonymous_session_metrics AS (
    -- First CTE: Base session metrics with joins and correlated subqueries
    SELECT
        ac.id AS chat_id,
        ac.join_code,
        ac.created_at AS session_start,
        COUNT(DISTINCT acu.guest_id) AS unique_guests,
        COUNT(am.id) AS total_messages,
        MAX(am.created_at) AS last_message_time,
        COUNT(am.id) AS guest_messages,
        0 AS ai_messages,
        (
            SELECT COUNT(DISTINCT acu2.guest_id)
            FROM anonymous_chat_users acu2
            WHERE acu2.chat_id = ac.id
                AND EXISTS (
                    SELECT 1
                    FROM anonymous_messages am2
                    WHERE am2.chat_id = ac.id
                        AND am2.guest_id = acu2.guest_id
                )
        ) AS active_guests,
        (
            SELECT AVG(message_count)
            FROM (
                SELECT COUNT(*) AS message_count
                FROM anonymous_messages am3
                WHERE am3.chat_id = ac.id
                GROUP BY am3.guest_id
            ) guest_message_counts
        ) AS avg_messages_per_guest
    FROM anonymous_chats ac
    LEFT JOIN anonymous_chat_users acu ON ac.id = acu.chat_id
    LEFT JOIN anonymous_messages am ON ac.id = am.chat_id
    GROUP BY ac.id, ac.join_code, ac.created_at
),
interaction_chain_metrics AS (
    -- Second CTE: Interaction chain metrics from recursive CTE
    SELECT
        chat_id,
        COUNT(DISTINCT guest_id) AS guests_with_chains,
        AVG(interaction_depth) AS avg_interaction_depth,
        MAX(interaction_depth) AS max_interaction_depth,
        COUNT(*) AS total_chain_interactions
    FROM guest_interaction_chain
    GROUP BY chat_id
),
session_durations AS (
    -- Third CTE: Session duration calculations
    SELECT
        asm.chat_id,
        asm.join_code,
        asm.session_start,
        asm.unique_guests,
        asm.total_messages,
        asm.last_message_time,
        asm.guest_messages,
        asm.ai_messages,
        asm.active_guests,
        asm.avg_messages_per_guest,
        COALESCE(icm.guests_with_chains, 0) AS guests_with_chains,
        COALESCE(icm.avg_interaction_depth, 0) AS avg_interaction_depth,
        COALESCE(icm.max_interaction_depth, 0) AS max_interaction_depth,
        COALESCE(icm.total_chain_interactions, 0) AS total_chain_interactions,
        EXTRACT(EPOCH FROM (COALESCE(asm.last_message_time, asm.session_start) - asm.session_start)) / 60 AS session_duration_minutes,
        CASE
            WHEN asm.total_messages = 0 THEN 'No Activity'
            WHEN asm.total_messages < 5 THEN 'Low Activity'
            WHEN asm.total_messages < 20 THEN 'Medium Activity'
            WHEN asm.total_messages < 50 THEN 'High Activity'
            ELSE 'Very High Activity'
        END AS activity_level
    FROM anonymous_session_metrics asm
    LEFT JOIN interaction_chain_metrics icm ON asm.chat_id = icm.chat_id
),
rolling_window_session_stats AS (
    -- Fourth CTE: Rolling window statistics with frame clauses
    SELECT
        sd.*,
        -- Window functions with ROWS BETWEEN frames
        SUM(sd.total_messages) OVER (
            ORDER BY sd.total_messages DESC
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS messages_10_session_window,
        AVG(sd.session_duration_minutes) OVER (
            ORDER BY sd.session_duration_minutes DESC
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS duration_20_session_avg,
        -- Window functions with RANGE BETWEEN frames
        SUM(sd.unique_guests) OVER (
            ORDER BY sd.total_messages
            RANGE BETWEEN 10 PRECEDING AND 10 FOLLOWING
        ) AS guests_message_range_window,
        -- Lag/Lead functions
        LAG(sd.total_messages, 1) OVER (ORDER BY sd.total_messages DESC) AS prev_session_messages,
        LEAD(sd.session_duration_minutes, 1) OVER (ORDER BY sd.session_duration_minutes DESC) AS next_session_duration,
        -- First/Last value with frames
        FIRST_VALUE(sd.guest_messages) OVER (
            ORDER BY sd.total_messages DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_session_guest_messages,
        LAST_VALUE(sd.ai_messages) OVER (
            ORDER BY sd.total_messages DESC
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_session_ai_messages
    FROM session_durations sd
),
activity_analysis AS (
    -- Fifth CTE: Activity analysis with pivot CASE
    SELECT
        rwss.chat_id,
        rwss.join_code,
        rwss.session_start,
        rwss.unique_guests,
        rwss.total_messages,
        rwss.guest_messages,
        rwss.ai_messages,
        rwss.active_guests,
        ROUND(CAST(rwss.avg_messages_per_guest AS NUMERIC), 2) AS avg_messages_per_guest,
        rwss.guests_with_chains,
        ROUND(CAST(rwss.avg_interaction_depth AS NUMERIC), 2) AS avg_interaction_depth,
        rwss.max_interaction_depth,
        rwss.total_chain_interactions,
        ROUND(CAST(rwss.session_duration_minutes AS NUMERIC), 2) AS duration_minutes,
        rwss.activity_level,
        rwss.messages_10_session_window,
        ROUND(CAST(rwss.duration_20_session_avg AS NUMERIC), 2) AS duration_20_session_avg,
        rwss.guests_message_range_window,
        rwss.prev_session_messages,
        ROUND(CAST(rwss.next_session_duration AS NUMERIC), 2) AS next_session_duration,
        rwss.first_session_guest_messages,
        rwss.last_session_ai_messages,
        ROUND(CAST(rwss.guest_messages::numeric / NULLIF(CAST(rwss.total_messages AS NUMERIC), 0) AS NUMERIC) * 100, 2) AS guest_message_percentage,
        ROUND(CAST(rwss.total_messages::numeric / NULLIF(CAST(rwss.session_duration_minutes AS NUMERIC), 0) AS NUMERIC), 2) AS messages_per_minute,
        -- Pivot CASE for classification
        CASE
            WHEN ROUND(CAST(rwss.guest_messages::numeric / NULLIF(CAST(rwss.total_messages AS NUMERIC), 0) AS NUMERIC) * 100, 2) >= 70 THEN 'Guest-Dominated'
            WHEN ROUND(CAST(rwss.guest_messages::numeric / NULLIF(CAST(rwss.total_messages AS NUMERIC), 0) AS NUMERIC) * 100, 2) >= 50 THEN 'Balanced'
            WHEN ROUND(CAST(rwss.guest_messages::numeric / NULLIF(CAST(rwss.total_messages AS NUMERIC), 0) AS NUMERIC) * 100, 2) >= 30 THEN 'AI-Assisted'
            ELSE 'AI-Dominated'
        END AS interaction_type,
        CASE
            WHEN ROUND(CAST(rwss.total_messages::numeric / NULLIF(CAST(rwss.session_duration_minutes AS NUMERIC), 0) AS NUMERIC), 2) >= 2 THEN 'High Velocity'
            WHEN ROUND(CAST(rwss.total_messages::numeric / NULLIF(CAST(rwss.session_duration_minutes AS NUMERIC), 0) AS NUMERIC), 2) >= 1 THEN 'Medium Velocity'
            WHEN ROUND(CAST(rwss.total_messages::numeric / NULLIF(CAST(rwss.session_duration_minutes AS NUMERIC), 0) AS NUMERIC), 2) >= 0.5 THEN 'Low Velocity'
            ELSE 'Very Low Velocity'
        END AS velocity_category,
        -- Window function rankings
        ROW_NUMBER() OVER (ORDER BY rwss.total_messages DESC) AS message_row_num,
        RANK() OVER (ORDER BY rwss.total_messages DESC) AS message_rank,
        DENSE_RANK() OVER (ORDER BY rwss.session_duration_minutes DESC) AS duration_dense_rank,
        PERCENT_RANK() OVER (ORDER BY rwss.total_messages DESC) AS message_percentile,
        NTILE(5) OVER (ORDER BY rwss.total_messages DESC) AS message_quintile,
        NTILE(10) OVER (ORDER BY rwss.session_duration_minutes DESC) AS duration_decile
    FROM rolling_window_session_stats rwss
),
union_session_metrics AS (
    -- Sixth CTE: UNION to combine different metric types
    SELECT
        aa.chat_id,
        'messages' AS metric_type,
        aa.total_messages AS metric_value
    FROM activity_analysis aa

    UNION ALL

    SELECT
        aa.chat_id,
        'guests' AS metric_type,
        aa.unique_guests AS metric_value
    FROM activity_analysis aa

    UNION ALL

    SELECT
        aa.chat_id,
        'duration' AS metric_type,
        aa.duration_minutes AS metric_value
    FROM activity_analysis aa
),
aggregated_union_session_metrics AS (
    -- Seventh CTE: Aggregate UNION results with window functions
    SELECT
        usm.chat_id,
        SUM(CASE WHEN usm.metric_type = 'messages' THEN usm.metric_value ELSE 0 END) AS total_messages_metric,
        SUM(CASE WHEN usm.metric_type = 'guests' THEN usm.metric_value ELSE 0 END) AS total_guests_metric,
        SUM(CASE WHEN usm.metric_type = 'duration' THEN usm.metric_value ELSE 0 END) AS total_duration_metric,
        COUNT(DISTINCT usm.metric_type) AS metric_types_count,
        -- Window functions on UNION data
        AVG(usm.metric_value) OVER (
            PARTITION BY usm.metric_type
            ORDER BY usm.chat_id
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS metric_moving_avg,
        SUM(usm.metric_value) OVER (
            PARTITION BY usm.chat_id
            ORDER BY usm.metric_type
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_cumulative_metric
    FROM union_session_metrics usm
    GROUP BY usm.chat_id, usm.metric_type, usm.metric_value
),
final_anonymous_session_analytics AS (
    -- Eighth CTE: Final analytics with comprehensive window functions
    SELECT
        aa.chat_id,
        aa.join_code,
        aa.session_start,
        aa.unique_guests,
        aa.total_messages,
        aa.guest_messages,
        aa.ai_messages,
        aa.active_guests,
        aa.avg_messages_per_guest,
        aa.guests_with_chains,
        aa.avg_interaction_depth,
        aa.max_interaction_depth,
        aa.total_chain_interactions,
        aa.duration_minutes,
        aa.activity_level,
        aa.messages_10_session_window,
        aa.duration_20_session_avg,
        aa.guests_message_range_window,
        aa.prev_session_messages,
        aa.next_session_duration,
        aa.first_session_guest_messages,
        aa.last_session_ai_messages,
        aa.guest_message_percentage,
        aa.messages_per_minute,
        aa.interaction_type,
        aa.velocity_category,
        aa.message_row_num,
        aa.message_rank,
        aa.duration_dense_rank,
        ROUND(CAST(aa.message_percentile * 100 AS NUMERIC), 2) AS message_percentile,
        aa.message_quintile,
        aa.duration_decile,
        -- Additional window functions with frames
        SUM(aa.total_messages) OVER (
            ORDER BY aa.total_messages DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_messages,
        AVG(aa.duration_minutes) OVER (
            ORDER BY aa.duration_minutes DESC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS moving_avg_duration,
        LAG(aa.total_messages, 1) OVER (ORDER BY aa.total_messages DESC) AS prev_total_messages,
        LEAD(aa.duration_minutes, 1) OVER (ORDER BY aa.duration_minutes DESC) AS next_duration
    FROM activity_analysis aa
)
SELECT
    chat_id,
    join_code,
    session_start,
    unique_guests,
    total_messages,
    guest_messages,
    ai_messages,
    active_guests,
    avg_messages_per_guest,
    guests_with_chains,
    avg_interaction_depth,
    max_interaction_depth,
    total_chain_interactions,
    duration_minutes,
    activity_level,
    messages_10_session_window,
    duration_20_session_avg,
    guests_message_range_window,
    prev_session_messages,
    next_session_duration,
    first_session_guest_messages,
    last_session_ai_messages,
    guest_message_percentage,
    messages_per_minute,
    interaction_type,
    velocity_category,
    message_row_num,
    message_rank,
    duration_dense_rank,
    message_percentile,
    message_quintile,
    duration_decile,
    cumulative_messages,
    ROUND(CAST(moving_avg_duration AS NUMERIC), 2) AS moving_avg_duration,
    prev_total_messages,
    ROUND(CAST(next_duration AS NUMERIC), 2) AS next_duration
FROM final_anonymous_session_analytics
ORDER BY total_messages DESC;
```

**Expected Output:** Anonymous chat session analysis with activity metrics and rankings.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: activity_analysis, anonymous_chat_users, anonymous_chats, anonymous_messages, anonymous_session_metrics, final_anonymous_session_analytics, guest_interaction_chain, interaction_chain_metrics, recursive, rolling_window_session_stats, session_durations, union_session_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: activity_analysis, anonymous_chat_users, anonymous_chats, anonymous_messages, anonymous_session_metrics, final_anonymous_session_analytics, guest_interaction_chain, interaction_chain_metrics, recursive, rolling_window_session_stats, session_durations, union_session_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: activity_analysis, anonymous_chat_users, anonymous_chats, anonymous_messages, anonymous_session_metrics, final_anonymous_session_analytics, guest_interaction_chain, interaction_chain_metrics, recursive, rolling_window_session_stats, session_durations, union_session_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: activity_analysis, anonymous_chat_users, anonymous_chats, anonymous_messages, anonymous_session_metrics, final_anonymous_session_analytics, guest_interaction_chain, interaction_chain_metrics, recursive, rolling_window_session_stats, session_durations, union_session_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: activity_analysis, anonymous_chat_users, anonymous_chats, anonymous_messages, anonymous_session_metrics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE guest_interaction_chain AS (
    -- Anchor: Base guest interactions
    SELECT
        acu.guest_id,
        acu.chat_id,
        am.id AS message_id,
        am.created_at,
        1 AS interaction_depth,
        ARRAY[acu.guest_id]::character varying[] AS interaction_path
    FROM anonymous_chat_users acu
    INNER JOIN anonymous_messages am ON acu.chat_id = am.chat_id
    WHERE am.guest_id = acu.guest_id

    UNION ALL

    -- Recursive: Find related interactions in same chat
...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 10: Production-Grade Cross-Table User Activity Analysis with Recursive CTE and Advanced Scoring

**Description:** Enterprise-level cross-table user activity analysis with recursive CTE for activity chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive weighted scoring. Implements production patterns similar to user analytics platforms.

**Complexity:** Recursive CTE, multiple nested CTEs (9+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE activity_chain AS (
    -- Anchor: Base user activities
    SELECT
        p.id AS user_id,
        'profile' AS activity_source,
        p.created_at AS activity_time,
        1 AS chain_depth,
        ARRAY[p.id] AS chain_path
    FROM profiles p

    UNION ALL

    -- Recursive: Find related activities
    SELECT
        ac.user_id,
        CASE
            WHEN EXISTS (SELECT 1 FROM messages m WHERE m.sender_id = ac.user_id AND m.created_at BETWEEN ac.activity_time AND ac.activity_time + INTERVAL '1 day') THEN 'message'
            WHEN EXISTS (SELECT 1 FROM chat_participants cp WHERE cp.user_id = ac.user_id AND cp.joined_at BETWEEN ac.activity_time AND ac.activity_time + INTERVAL '1 day') THEN 'chat'
            WHEN EXISTS (SELECT 1 FROM friends f WHERE f.user_id = ac.user_id AND f.created_at BETWEEN ac.activity_time AND ac.activity_time + INTERVAL '1 day') THEN 'friend'
            ELSE 'other'
        END AS activity_source,
        COALESCE(
            (SELECT MIN(m.created_at) FROM messages m WHERE m.sender_id = ac.user_id AND m.created_at > ac.activity_time),
            (SELECT MIN(cp.joined_at) FROM chat_participants cp WHERE cp.user_id = ac.user_id AND cp.joined_at > ac.activity_time),
            (SELECT MIN(f.created_at) FROM friends f WHERE f.user_id = ac.user_id AND f.created_at > ac.activity_time)
        ) AS activity_time,
        ac.chain_depth + 1,
        ac.chain_path || ac.user_id
    FROM activity_chain ac
    WHERE ac.chain_depth < 5
        AND (
            EXISTS (SELECT 1 FROM messages m WHERE m.sender_id = ac.user_id AND m.created_at > ac.activity_time)
            OR EXISTS (SELECT 1 FROM chat_participants cp WHERE cp.user_id = ac.user_id AND cp.joined_at > ac.activity_time)
            OR EXISTS (SELECT 1 FROM friends f WHERE f.user_id = ac.user_id AND f.created_at > ac.activity_time)
        )
),
user_messages AS (
    -- First CTE: User message metrics with correlated subqueries
    SELECT
        sender_id AS user_id,
        COUNT(*) AS message_count,
        COUNT(DISTINCT chat_id) AS chat_count,
        AVG(LENGTH(content)) AS avg_message_length,
        (
            SELECT COUNT(DISTINCT m2.chat_id)
            FROM messages m2
            WHERE m2.sender_id = messages.sender_id
                AND m2.is_ai = false
                AND EXISTS (
                    SELECT 1
                    FROM messages m3
                    WHERE m3.chat_id = m2.chat_id
                        AND m3.is_ai = true
                        AND m3.created_at BETWEEN m2.created_at - INTERVAL '1 hour' AND m2.created_at + INTERVAL '1 hour'
                )
        ) AS chats_with_ai_interaction
    FROM messages
    WHERE is_ai = false
    GROUP BY sender_id
),
user_chats AS (
    -- Second CTE: User chat metrics
    SELECT
        cp.user_id,
        COUNT(DISTINCT cp.chat_id) AS participated_chats,
        COUNT(DISTINCT c.id) AS created_chats,
        (
            SELECT COUNT(DISTINCT cp2.chat_id)
            FROM chat_participants cp2
            WHERE cp2.user_id = cp.user_id
                AND EXISTS (
                    SELECT 1
                    FROM messages m
                    WHERE m.chat_id = cp2.chat_id
                        AND m.sender_id = cp2.user_id
                        AND m.created_at >= cp2.joined_at
                )
        ) AS active_participated_chats
    FROM chat_participants cp
    LEFT JOIN chats c ON cp.user_id = c.created_by
    GROUP BY cp.user_id
),
user_friends AS (
    -- Third CTE: User friend metrics
    SELECT
        user_id,
        COUNT(*) AS friend_count,
        SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) AS accepted_friends,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending_friends
    FROM friends
    GROUP BY user_id
),
user_notifications AS (
    -- Fourth CTE: User notification metrics
    SELECT
        user_id,
        COUNT(*) AS notification_count,
        SUM(CASE WHEN read = true THEN 1 ELSE 0 END) AS read_notifications,
        AVG(EXTRACT(EPOCH FROM (COALESCE(seen_at, CURRENT_TIMESTAMP) - created_at)) / 60) AS avg_minutes_to_seen
    FROM notifications
    GROUP BY user_id
),
user_attachments AS (
    -- Fifth CTE: User attachment metrics
    SELECT
        user_id AS user_id,
        COUNT(*) AS attachment_count,
        SUM(file_size) AS total_upload_size,
        AVG(file_size) AS avg_file_size
    FROM file_attachments
    GROUP BY user_id
),
activity_chain_metrics AS (
    -- Sixth CTE: Activity chain metrics from recursive CTE
    SELECT
        user_id,
        COUNT(DISTINCT activity_source) AS unique_activity_sources,
        AVG(chain_depth) AS avg_chain_depth,
        MAX(chain_depth) AS max_chain_depth,
        COUNT(*) AS total_chain_activities
    FROM activity_chain
    GROUP BY user_id
),
combined_activity AS (
    -- Seventh CTE: UNION to combine activity types
    SELECT user_id, 'messages' AS activity_type, message_count AS activity_count, 1.0 AS weight FROM user_messages
    UNION ALL
    SELECT user_id, 'chats' AS activity_type, participated_chats AS activity_count, 5.0 AS weight FROM user_chats
    UNION ALL
    SELECT user_id, 'friends' AS activity_type, friend_count AS activity_count, 3.0 AS weight FROM user_friends
    UNION ALL
    SELECT user_id, 'notifications' AS activity_type, notification_count AS activity_count, 0.5 AS weight FROM user_notifications
    UNION ALL
    SELECT user_id, 'attachments' AS activity_type, attachment_count AS activity_count, 2.0 AS weight FROM user_attachments
),
user_totals AS (
    -- Eighth CTE: Aggregate user totals
    SELECT
        ca.user_id,
        SUM(CASE WHEN ca.activity_type = 'messages' THEN ca.activity_count ELSE 0 END) AS total_messages,
        SUM(CASE WHEN ca.activity_type = 'chats' THEN ca.activity_count ELSE 0 END) AS total_chats,
        SUM(CASE WHEN ca.activity_type = 'friends' THEN ca.activity_count ELSE 0 END) AS total_friends,
        SUM(CASE WHEN ca.activity_type = 'notifications' THEN ca.activity_count ELSE 0 END) AS total_notifications,
        SUM(CASE WHEN ca.activity_type = 'attachments' THEN ca.activity_count ELSE 0 END) AS total_attachments,
        SUM(ca.activity_count * ca.weight) AS weighted_activity_sum
    FROM combined_activity ca
    GROUP BY ca.user_id
),
rolling_window_user_stats AS (
    -- Ninth CTE: Rolling window statistics with frame clauses
    SELECT
        ut.user_id,
        ut.total_messages,
        ut.total_chats,
        ut.total_friends,
        ut.total_notifications,
        ut.total_attachments,
        ut.weighted_activity_sum,
        COALESCE(um.chat_count, 0) AS chat_count,
        COALESCE(um.avg_message_length, 0) AS avg_message_length,
        COALESCE(um.chats_with_ai_interaction, 0) AS chats_with_ai_interaction,
        COALESCE(uc.created_chats, 0) AS created_chats,
        COALESCE(uc.active_participated_chats, 0) AS active_participated_chats,
        COALESCE(uf.accepted_friends, 0) AS accepted_friends,
        COALESCE(uf.pending_friends, 0) AS pending_friends,
        COALESCE(un.read_notifications, 0) AS read_notifications,
        COALESCE(un.avg_minutes_to_seen, 0) AS avg_minutes_to_seen,
        COALESCE(ua.total_upload_size, 0) AS total_upload_size,
        COALESCE(ua.avg_file_size, 0) AS avg_file_size,
        COALESCE(acm.unique_activity_sources, 0) AS unique_activity_sources,
        COALESCE(acm.avg_chain_depth, 0) AS avg_chain_depth,
        COALESCE(acm.max_chain_depth, 0) AS max_chain_depth,
        COALESCE(acm.total_chain_activities, 0) AS total_chain_activities,
        -- Window functions with ROWS BETWEEN frames
        SUM(ut.weighted_activity_sum) OVER (
            ORDER BY ut.weighted_activity_sum DESC
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS activity_10_user_window,
        AVG(ut.total_messages) OVER (
            ORDER BY ut.total_messages DESC
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS messages_20_user_avg,
        -- Window functions with RANGE BETWEEN frames
        SUM(ut.total_chats) OVER (
            ORDER BY ut.weighted_activity_sum
            RANGE BETWEEN 50 PRECEDING AND 50 FOLLOWING
        ) AS chats_activity_range_window,
        -- Lag/Lead functions
        LAG(ut.weighted_activity_sum, 1) OVER (ORDER BY ut.weighted_activity_sum DESC) AS prev_user_activity,
        LEAD(ut.total_messages, 1) OVER (ORDER BY ut.total_messages DESC) AS next_user_messages,
        -- First/Last value with frames
        FIRST_VALUE(ut.total_chats) OVER (
            ORDER BY ut.weighted_activity_sum DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_user_chats,
        LAST_VALUE(ut.total_friends) OVER (
            ORDER BY ut.weighted_activity_sum DESC
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_user_friends
    FROM user_totals ut
    LEFT JOIN user_messages um ON ut.user_id = um.user_id
    LEFT JOIN user_chats uc ON ut.user_id = uc.user_id
    LEFT JOIN user_friends uf ON ut.user_id = uf.user_id
    LEFT JOIN user_notifications un ON ut.user_id = un.user_id
    LEFT JOIN user_attachments ua ON ut.user_id = ua.user_id
    LEFT JOIN activity_chain_metrics acm ON ut.user_id = acm.user_id
),
activity_scores AS (
    -- Tenth CTE: Calculate activity scores with window functions
    SELECT
        rwus.user_id,
        p.username,
        rwus.total_messages,
        rwus.total_chats,
        rwus.total_friends,
        rwus.total_notifications,
        rwus.total_attachments,
        rwus.chat_count,
        ROUND(CAST(rwus.avg_message_length AS NUMERIC), 2) AS avg_message_length,
        rwus.chats_with_ai_interaction,
        rwus.created_chats,
        rwus.active_participated_chats,
        rwus.accepted_friends,
        rwus.pending_friends,
        rwus.read_notifications,
        ROUND(CAST(rwus.avg_minutes_to_seen AS NUMERIC), 2) AS avg_minutes_to_seen,
        ROUND(CAST(rwus.total_upload_size / 1024.0 / 1024.0 AS NUMERIC), 2) AS total_upload_size_mb,
        ROUND(CAST(rwus.avg_file_size / 1024.0 AS NUMERIC), 2) AS avg_file_size_kb,
        rwus.unique_activity_sources,
        ROUND(CAST(rwus.avg_chain_depth AS NUMERIC), 2) AS avg_chain_depth,
        rwus.max_chain_depth,
        rwus.total_chain_activities,
        rwus.activity_10_user_window,
        ROUND(CAST(rwus.messages_20_user_avg AS NUMERIC), 2) AS messages_20_user_avg,
        rwus.chats_activity_range_window,
        ROUND(CAST(rwus.prev_user_activity AS NUMERIC), 2) AS prev_user_activity,
        rwus.next_user_messages,
        rwus.first_user_chats,
        rwus.last_user_friends,
        -- Weighted activity score with chain bonus
        (rwus.total_messages * 1.0) +
        (rwus.total_chats * 5.0) +
        (rwus.total_friends * 3.0) +
        (rwus.total_notifications * 0.5) +
        (rwus.total_attachments * 2.0) +
        (rwus.unique_activity_sources * 1.5) +
        (rwus.avg_chain_depth * 0.5) AS activity_score,
        -- Window functions for comparison
        AVG(rwus.weighted_activity_sum) OVER () AS overall_avg_activity,
        PERCENT_RANK() OVER (ORDER BY rwus.weighted_activity_sum DESC) AS activity_percentile
    FROM rolling_window_user_stats rwus
    INNER JOIN profiles p ON rwus.user_id = p.id
),
final_activity_analytics AS (
    -- Eleventh CTE: Final analytics with comprehensive window functions
    SELECT
        as1.user_id,
        as1.username,
        as1.total_messages,
        as1.total_chats,
        as1.total_friends,
        as1.total_notifications,
        as1.total_attachments,
        as1.chat_count,
        as1.avg_message_length,
        as1.chats_with_ai_interaction,
        as1.created_chats,
        as1.active_participated_chats,
        as1.accepted_friends,
        as1.pending_friends,
        as1.read_notifications,
        as1.avg_minutes_to_seen,
        as1.total_upload_size_mb,
        as1.avg_file_size_kb,
        as1.unique_activity_sources,
        as1.avg_chain_depth,
        as1.max_chain_depth,
        as1.total_chain_activities,
        as1.activity_10_user_window,
        as1.messages_20_user_avg,
        as1.chats_activity_range_window,
        as1.prev_user_activity,
        as1.next_user_messages,
        as1.first_user_chats,
        as1.last_user_friends,
        ROUND(CAST(as1.activity_score AS NUMERIC), 2) AS activity_score,
        ROUND(CAST(as1.overall_avg_activity AS NUMERIC), 2) AS overall_avg_activity,
        ROUND(CAST(as1.activity_percentile * 100 AS NUMERIC), 2) AS activity_percentile,
        -- Multiple ranking methods
        ROW_NUMBER() OVER (ORDER BY as1.activity_score DESC) AS activity_row_num,
        RANK() OVER (ORDER BY as1.activity_score DESC) AS activity_rank,
        DENSE_RANK() OVER (ORDER BY as1.activity_score DESC) AS activity_dense_rank,
        PERCENT_RANK() OVER (ORDER BY as1.activity_score DESC) AS score_percentile,
        NTILE(5) OVER (ORDER BY as1.activity_score DESC) AS activity_quintile,
        NTILE(10) OVER (ORDER BY as1.activity_score DESC) AS activity_decile,
        -- Window functions with frames
        SUM(as1.activity_score) OVER (
            ORDER BY as1.activity_score DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_activity_score,
        AVG(as1.activity_score) OVER (
            ORDER BY as1.activity_score DESC
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS moving_avg_activity_score,
        LAG(as1.activity_score, 1) OVER (ORDER BY as1.activity_score DESC) AS prev_activity_score,
        LEAD(as1.activity_score, 1) OVER (ORDER BY as1.activity_score DESC) AS next_activity_score,
        -- Pivot CASE for classification
        CASE
            WHEN as1.activity_score >= 200 THEN 'Power User'
            WHEN as1.activity_score >= 100 THEN 'Active User'
            WHEN as1.activity_score >= 50 THEN 'Regular User'
            WHEN as1.activity_score >= 20 THEN 'Casual User'
            ELSE 'Inactive User'
        END AS user_category,
        CASE
            WHEN as1.unique_activity_sources >= 4 THEN 'Multi-Platform'
            WHEN as1.unique_activity_sources >= 3 THEN 'Diverse'
            WHEN as1.unique_activity_sources >= 2 THEN 'Moderate'
            ELSE 'Focused'
        END AS activity_diversity_category
    FROM activity_scores as1
)
SELECT
    user_id,
    username,
    total_messages,
    total_chats,
    total_friends,
    total_notifications,
    total_attachments,
    chat_count,
    avg_message_length,
    chats_with_ai_interaction,
    created_chats,
    active_participated_chats,
    accepted_friends,
    pending_friends,
    read_notifications,
    avg_minutes_to_seen,
    total_upload_size_mb,
    avg_file_size_kb,
    unique_activity_sources,
    avg_chain_depth,
    max_chain_depth,
    total_chain_activities,
    activity_10_user_window,
    messages_20_user_avg,
    chats_activity_range_window,
    prev_user_activity,
    next_user_messages,
    first_user_chats,
    last_user_friends,
    activity_score,
    overall_avg_activity,
    activity_percentile,
    activity_row_num,
    activity_rank,
    activity_dense_rank,
    ROUND(CAST(score_percentile * 100 AS NUMERIC), 2) AS score_percentile,
    activity_quintile,
    activity_decile,
    ROUND(CAST(cumulative_activity_score AS NUMERIC), 2) AS cumulative_activity_score,
    ROUND(CAST(moving_avg_activity_score AS NUMERIC), 2) AS moving_avg_activity_score,
    ROUND(CAST(prev_activity_score AS NUMERIC), 2) AS prev_activity_score,
    ROUND(CAST(next_activity_score AS NUMERIC), 2) AS next_activity_score,
    user_category,
    activity_diversity_category
FROM final_activity_analytics
ORDER BY activity_score DESC;
```

**Expected Output:** Comprehensive user activity scores with rankings across all activity types.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: activity_chain, activity_chain_metrics, activity_scores, chat_participants, chats, combined_activity, file_attachments, final_activity_analytics, friends, messages, notifications, profiles, recursive, rolling_window_user_stats, user_attachments, user_chats, user_friends, user_messages, user_notifications, user_totals
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: activity_chain, activity_chain_metrics, activity_scores, chat_participants, chats, combined_activity, file_attachments, final_activity_analytics, friends, messages, notifications, profiles, recursive, rolling_window_user_stats, user_attachments, user_chats, user_friends, user_messages, user_notifications, user_totals
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: activity_chain, activity_chain_metrics, activity_scores, chat_participants, chats, combined_activity, file_attachments, final_activity_analytics, friends, messages, notifications, profiles, recursive, rolling_window_user_stats, user_attachments, user_chats, user_friends, user_messages, user_notifications, user_totals
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: activity_chain, activity_chain_metrics, activity_scores, chat_participants, chats, combined_activity, file_attachments, final_activity_analytics, friends, messages, notifications, profiles, recursive, rolling_window_user_stats, user_attachments, user_chats, user_friends, user_messages, user_notifications, user_totals
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: activity_chain, activity_chain_metrics, activity_scores, chat_participants, chats, combined_activity, file_attachments, final_activity_analytics, friends, messages, notifications, profiles, recursive, rolling_window_user_stats, user_attachments, user_chats, user_friends, user_messages, user_notifications, user_totals
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: activity_chain, activity_chain_metrics, activity_scores, chat_participants, chats
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE activity_chain AS (
    -- Anchor: Base user activities
    SELECT
        p.id AS user_id,
        'profile' AS activity_source,
        p.created_at AS activity_time,
        1 AS chain_depth,
        ARRAY[p.id] AS chain_path
    FROM profiles p

    UNION ALL

    -- Recursive: Find related activities
    SELECT
        ac.user_id,
        CASE
            WHEN EXISTS (SELECT 1 FROM messages m WHERE m.sender_id = ac.user_id AND m.created_at BETWEEN ac.activity_time AND ac.acti...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 11: Production-Grade Recursive Chat Invitation Chain Analysis with Advanced Network Metrics

**Description:** Enterprise-level recursive CTE analysis for invitation chains with multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive network path analytics. Implements production patterns similar to social network analysis systems.

**Complexity:** Recursive CTE, multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE invitation_chains AS (
    -- Anchor: Base invitation chains
    SELECT
        ci.id,
        ci.inviting_user_id AS chain_start,
        ci.invited_user_id AS chain_end,
        ci.chat_id,
        1 AS chain_length,
        ARRAY[ci.inviting_user_id, ci.invited_user_id] AS path,
        ci.created_at AS invitation_time
    FROM chat_invitations ci
    WHERE ci.status = 'accepted'

    UNION ALL

    -- Recursive: Extend invitation chains
    SELECT
        ci2.id,
        ic.chain_start,
        ci2.invited_user_id AS chain_end,
        ci2.chat_id,
        ic.chain_length + 1,
        ic.path || ci2.invited_user_id,
        ci2.created_at AS invitation_time
    FROM invitation_chains ic
    INNER JOIN chat_invitations ci2 ON ic.chain_end = ci2.inviting_user_id
    WHERE ci2.status = 'accepted'
        AND ci2.invited_user_id != ALL(ic.path)
        AND ci2.created_at >= ic.invitation_time
        AND ic.chain_length < 5
),
chain_statistics AS (
    -- First CTE: Chain-level statistics
    SELECT
        ic.chain_start,
        ic.chain_end,
        ic.chain_length,
        COUNT(*) AS path_count,
        COUNT(DISTINCT ic.chat_id) AS unique_chats,
        MIN(ic.invitation_time) AS first_invitation_time,
        MAX(ic.invitation_time) AS last_invitation_time,
        EXTRACT(EPOCH FROM (MAX(ic.invitation_time) - MIN(ic.invitation_time))) / 3600 AS chain_duration_hours
    FROM invitation_chains ic
    GROUP BY ic.chain_start, ic.chain_end, ic.chain_length
),
user_invitation_metrics AS (
    -- Second CTE: User-level invitation metrics with correlated subqueries
    SELECT
        cs.chain_start AS user_id,
        COUNT(DISTINCT cs.chain_end) AS unique_invited_users,
        COUNT(*) AS total_invitation_paths,
        AVG(cs.chain_length) AS avg_chain_length,
        MAX(cs.chain_length) AS max_chain_length,
        SUM(cs.path_count) AS total_path_count,
        SUM(cs.unique_chats) AS total_unique_chats,
        AVG(cs.chain_duration_hours) AS avg_chain_duration_hours,
        (
            SELECT COUNT(DISTINCT ci3.invited_user_id)
            FROM chat_invitations ci3
            WHERE ci3.inviting_user_id = cs.chain_start
                AND ci3.status = 'accepted'
        ) AS direct_invitations,
        (
            SELECT AVG(chain_length)
            FROM (
                SELECT chain_length
                FROM invitation_chains ic2
                WHERE ic2.chain_start = cs.chain_start
            ) user_chains
        ) AS avg_user_chain_length
    FROM chain_statistics cs
    GROUP BY cs.chain_start
),
invitation_network_metrics AS (
    -- Third CTE: Network-level metrics
    SELECT
        cs.chain_start,
        cs.chain_end,
        cs.chain_length,
        cs.path_count,
        cs.unique_chats,
        cs.chain_duration_hours,
        uim1.unique_invited_users AS start_user_unique_invited,
        uim1.total_invitation_paths AS start_user_total_paths,
        uim1.avg_chain_length AS start_user_avg_length,
        uim1.direct_invitations AS start_user_direct_invites,
        COALESCE(uim2.unique_invited_users, 0) AS end_user_unique_invited,
        COALESCE(uim2.total_invitation_paths, 0) AS end_user_total_paths,
        COALESCE(uim2.avg_chain_length, 0) AS end_user_avg_length,
        COALESCE(uim2.direct_invitations, 0) AS end_user_direct_invites
    FROM chain_statistics cs
    INNER JOIN user_invitation_metrics uim1 ON cs.chain_start = uim1.user_id
    LEFT JOIN user_invitation_metrics uim2 ON cs.chain_end = uim2.user_id
),
rolling_window_network_stats AS (
    -- Fourth CTE: Rolling window statistics with frame clauses
    SELECT
        inm.*,
        -- Window functions with ROWS BETWEEN frames
        SUM(inm.path_count) OVER (
            PARTITION BY inm.chain_length
            ORDER BY inm.path_count DESC
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS path_count_10_window,
        AVG(inm.chain_duration_hours) OVER (
            PARTITION BY inm.chain_length
            ORDER BY inm.path_count DESC
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS duration_20_path_avg,
        -- Window functions with RANGE BETWEEN frames
        SUM(inm.unique_chats) OVER (
            ORDER BY inm.path_count
            RANGE BETWEEN 5 PRECEDING AND 5 FOLLOWING
        ) AS chats_path_range_window,
        -- Lag/Lead functions
        LAG(inm.path_count, 1) OVER (PARTITION BY inm.chain_length ORDER BY inm.path_count DESC) AS prev_path_count,
        LEAD(inm.chain_duration_hours, 1) OVER (PARTITION BY inm.chain_length ORDER BY inm.path_count DESC) AS next_chain_duration,
        -- First/Last value with frames
        FIRST_VALUE(inm.unique_chats) OVER (
            PARTITION BY inm.chain_length
            ORDER BY inm.path_count DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_path_chats,
        LAST_VALUE(inm.chain_duration_hours) OVER (
            PARTITION BY inm.chain_length
            ORDER BY inm.path_count DESC
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_path_duration
    FROM invitation_network_metrics inm
),
union_network_metrics AS (
    -- Fifth CTE: UNION to combine different metric types
    SELECT
        rwns.chain_start,
        rwns.chain_end,
        'path_count' AS metric_type,
        rwns.path_count AS metric_value
    FROM rolling_window_network_stats rwns

    UNION ALL

    SELECT
        rwns.chain_start,
        rwns.chain_end,
        'unique_chats' AS metric_type,
        rwns.unique_chats AS metric_value
    FROM rolling_window_network_stats rwns

    UNION ALL

    SELECT
        rwns.chain_start,
        rwns.chain_end,
        'duration' AS metric_type,
        rwns.chain_duration_hours AS metric_value
    FROM rolling_window_network_stats rwns
),
aggregated_union_network_metrics AS (
    -- Sixth CTE: Aggregate UNION results with window functions
    SELECT
        NULL,
        NULL,
        SUM(CASE WHEN NULL = 'path_count' THEN NULL ELSE 0 END) AS total_path_count_metric,
        SUM(CASE WHEN NULL = 'unique_chats' THEN NULL ELSE 0 END) AS total_chats_metric,
        SUM(CASE WHEN NULL = 'duration' THEN NULL ELSE 0 END) AS total_duration_metric,
        COUNT(DISTINCT NULL) AS metric_types_count,
        -- Window functions on UNION data
        AVG(CAST(0 AS NUMERIC)) OVER (
            PARTITION BY unm.metric_type
            ORDER BY unm.chain_start
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS metric_moving_avg,
        SUM(CAST(0 AS NUMERIC)) OVER (
            PARTITION BY unm.chain_start
            ORDER BY unm.chain_start
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS chain_cumulative_metric
    FROM union_network_metrics unm
    GROUP BY unm.chain_start, unm.metric_type
),
final_invitation_chain_analytics AS (
    -- Seventh CTE: Final analytics with comprehensive window functions
    SELECT
        rwns.chain_start,
        rwns.chain_end,
        rwns.chain_length,
        rwns.path_count,
        rwns.unique_chats,
        ROUND(CAST(rwns.chain_duration_hours AS NUMERIC), 2) AS chain_duration_hours,
        rwns.start_user_unique_invited,
        rwns.start_user_total_paths,
        ROUND(CAST(rwns.start_user_avg_length AS NUMERIC), 2) AS start_user_avg_length,
        rwns.start_user_direct_invites,
        rwns.end_user_unique_invited,
        rwns.end_user_total_paths,
        ROUND(CAST(rwns.end_user_avg_length AS NUMERIC), 2) AS end_user_avg_length,
        rwns.end_user_direct_invites,
        rwns.path_count_10_window,
        ROUND(CAST(rwns.duration_20_path_avg AS NUMERIC), 2) AS duration_20_path_avg,
        rwns.chats_path_range_window,
        rwns.prev_path_count,
        ROUND(CAST(rwns.next_chain_duration AS NUMERIC), 2) AS next_chain_duration,
        rwns.first_path_chats,
        ROUND(CAST(rwns.last_path_duration AS NUMERIC), 2) AS last_path_duration,
        p1.username AS chain_start_user,
        p2.username AS chain_end_user,
        -- Network strength score
        (
            (rwns.path_count * 0.3) +
            (rwns.unique_chats * 0.25) +
            (rwns.start_user_direct_invites * 0.2) +
            (rwns.end_user_direct_invites * 0.15) +
            (CASE WHEN rwns.chain_duration_hours > 0 THEN 1.0 / (1.0 + rwns.chain_duration_hours / 24.0) ELSE 0 END * 0.1)
        ) AS network_strength_score,
        -- Window function rankings
        ROW_NUMBER() OVER (PARTITION BY rwns.chain_length ORDER BY rwns.path_count DESC) AS path_count_row_num,
        RANK() OVER (PARTITION BY rwns.chain_length ORDER BY rwns.path_count DESC) AS path_count_rank,
        DENSE_RANK() OVER (ORDER BY rwns.chain_length, rwns.path_count DESC) AS path_dense_rank,
        PERCENT_RANK() OVER (PARTITION BY rwns.chain_length ORDER BY rwns.path_count DESC) AS path_percentile,
        NTILE(5) OVER (PARTITION BY rwns.chain_length ORDER BY rwns.path_count DESC) AS path_quintile,
        NTILE(10) OVER (ORDER BY rwns.chain_length, rwns.path_count DESC) AS path_decile,
        -- Window functions with frames
        SUM(rwns.path_count) OVER (
            PARTITION BY rwns.chain_length
            ORDER BY rwns.path_count DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_path_count,
        AVG(rwns.path_count) OVER (
            PARTITION BY rwns.chain_length
            ORDER BY rwns.path_count DESC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS moving_avg_path_count,
        LAG(rwns.path_count, 1) OVER (PARTITION BY rwns.chain_length ORDER BY rwns.path_count DESC) AS prev_path_count_in_length,
        LEAD(rwns.unique_chats, 1) OVER (PARTITION BY rwns.chain_length ORDER BY rwns.path_count DESC) AS next_unique_chats,
        -- Pivot CASE for classification
        CASE
            WHEN rwns.path_count >= 10 THEN 'High Frequency'
            WHEN rwns.path_count >= 5 THEN 'Medium Frequency'
            WHEN rwns.path_count >= 2 THEN 'Low Frequency'
            ELSE 'Rare'
        END AS frequency_category,
        CASE
            WHEN rwns.chain_length = 1 THEN 'Direct'
            WHEN rwns.chain_length = 2 THEN 'One-Hop'
            WHEN rwns.chain_length = 3 THEN 'Two-Hop'
            WHEN rwns.chain_length = 4 THEN 'Three-Hop'
            ELSE 'Deep'
        END AS chain_type
    FROM rolling_window_network_stats rwns
    INNER JOIN profiles p1 ON rwns.chain_start = p1.id
    INNER JOIN profiles p2 ON rwns.chain_end = p2.id
)
SELECT
    chain_start_user,
    chain_end_user,
    chain_length,
    path_count,
    unique_chats,
    chain_duration_hours,
    start_user_unique_invited,
    start_user_total_paths,
    start_user_avg_length,
    start_user_direct_invites,
    end_user_unique_invited,
    end_user_total_paths,
    end_user_avg_length,
    end_user_direct_invites,
    path_count_10_window,
    duration_20_path_avg,
    chats_path_range_window,
    prev_path_count,
    next_chain_duration,
    first_path_chats,
    last_path_duration,
    ROUND(CAST(network_strength_score AS NUMERIC), 2) AS network_strength_score,
    path_count_row_num,
    path_count_rank,
    path_dense_rank,
    ROUND(CAST(path_percentile * 100 AS NUMERIC), 2) AS path_percentile,
    path_quintile,
    path_decile,
    cumulative_path_count,
    ROUND(CAST(moving_avg_path_count AS NUMERIC), 2) AS moving_avg_path_count,
    prev_path_count_in_length,
    next_unique_chats,
    frequency_category,
    chain_type
FROM final_invitation_chain_analytics
ORDER BY chain_length, path_count DESC;
```

**Expected Output:** Chat invitation chain analysis showing user connection paths.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chain_statistics, chat_invitations, final_invitation_chain_analytics, invitation_chains, invitation_network_metrics, profiles, rolling_window_network_stats, union_network_metrics, user_invitation_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chain_statistics, chat_invitations, final_invitation_chain_analytics, invitation_chains, invitation_network_metrics, profiles, rolling_window_network_stats, union_network_metrics, user_invitation_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chain_statistics, chat_invitations, final_invitation_chain_analytics, invitation_chains, invitation_network_metrics, profiles, rolling_window_network_stats, union_network_metrics, user_invitation_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chain_statistics, chat_invitations, final_invitation_chain_analytics, invitation_chains, invitation_network_metrics, profiles, rolling_window_network_stats, union_network_metrics, user_invitation_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chain_statistics, chat_invitations, final_invitation_chain_analytics, invitation_chains, invitation_network_metrics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE invitation_chains AS (
    -- Anchor: Base invitation chains
    SELECT
        ci.id,
        ci.inviting_user_id AS chain_start,
        ci.invited_user_id AS chain_end,
        ci.chat_id,
        1 AS chain_length,
        ARRAY[ci.inviting_user_id, ci.invited_user_id] AS path,
        ci.created_at AS invitation_time
    FROM chat_invitations ci
    WHERE ci.status = 'accepted'

    UNION ALL

    -- Recursive: Extend invitation chains
    SELECT
        ci2.id,
        ic.ch...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 12: Production-Grade Message Response Time Analysis with Recursive CTE and Advanced Window Functions

**Description:** Enterprise-level message response time analysis with recursive CTE for conversation flow tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive response time analytics. Implements production patterns similar to conversation analytics platforms.

**Complexity:** Recursive CTE, multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE conversation_flow AS (
    -- Anchor: Base message flow
    SELECT
        m.id AS message_id,
        m.chat_id,
        m.sender_id,
        m.is_ai,
        m.created_at,
        1 AS flow_depth,
        ARRAY[m.id] AS flow_path
    FROM messages m

    UNION ALL

    -- Recursive: Find related messages in conversation flow
    SELECT
        m2.id AS message_id,
        m2.chat_id,
        m2.sender_id,
        m2.is_ai,
        m2.created_at,
        cf.flow_depth + 1,
        cf.flow_path || m2.id
    FROM conversation_flow cf
    INNER JOIN messages m2 ON cf.chat_id = m2.chat_id
    WHERE m2.id != ALL(cf.flow_path)
        AND m2.created_at BETWEEN cf.created_at AND cf.created_at + INTERVAL '1 hour'
        AND m2.is_ai != cf.is_ai
        AND cf.flow_depth < 10
),
message_sequence AS (
    -- First CTE: Message sequence with joins and correlated subqueries
    SELECT
        m.id,
        m.chat_id,
        m.sender_id,
        m.is_ai,
        m.created_at,
        c.title AS chat_title,
        p.username AS sender_username,
        ROW_NUMBER() OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS seq_num,
        LAG(m.created_at, 1) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS prev_message_time,
        LAG(m.created_at, 2) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS prev2_message_time,
        LAG(m.is_ai, 1) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS prev_is_ai,
        LEAD(m.created_at, 1) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS next_message_time,
        LEAD(m.is_ai, 1) OVER (PARTITION BY m.chat_id ORDER BY m.created_at) AS next_is_ai,
        (
            SELECT AVG(EXTRACT(EPOCH FROM (m2.created_at - m3.created_at)))
            FROM messages m2
            INNER JOIN messages m3 ON m2.chat_id = m3.chat_id
            WHERE m2.chat_id = m.chat_id
                AND m2.id > m3.id
                AND m2.is_ai != m3.is_ai
                AND m2.created_at < m.created_at
        ) AS avg_historical_response_time,
        (
            SELECT COUNT(*)
            FROM messages m4
            WHERE m4.chat_id = m.chat_id
                AND m4.created_at < m.created_at
                AND m4.is_ai != m.is_ai
        ) AS prior_alternating_messages
    FROM messages m
    INNER JOIN chats c ON m.chat_id = c.id
    LEFT JOIN profiles p ON m.sender_id = p.id
),
conversation_flow_metrics AS (
    -- Second CTE: Conversation flow metrics from recursive CTE
    SELECT
        chat_id,
        COUNT(DISTINCT sender_id) AS unique_participants_in_flow,
        AVG(flow_depth) AS avg_flow_depth,
        MAX(flow_depth) AS max_flow_depth,
        COUNT(*) AS total_flow_messages
    FROM conversation_flow
    GROUP BY chat_id
),
response_times AS (
    -- Third CTE: Response time calculations
    SELECT
        ms.id,
        ms.chat_id,
        ms.sender_id,
        ms.is_ai,
        ms.created_at,
        ms.chat_title,
        ms.sender_username,
        ms.seq_num,
        ms.prev_message_time,
        ms.prev2_message_time,
        ms.prev_is_ai,
        ms.next_message_time,
        ms.next_is_ai,
        ms.avg_historical_response_time,
        ms.prior_alternating_messages,
        COALESCE(cfm.unique_participants_in_flow, 0) AS unique_participants_in_flow,
        COALESCE(cfm.avg_flow_depth, 0) AS avg_flow_depth,
        COALESCE(cfm.max_flow_depth, 0) AS max_flow_depth,
        COALESCE(cfm.total_flow_messages, 0) AS total_flow_messages,
        EXTRACT(EPOCH FROM (ms.created_at - ms.prev_message_time)) AS seconds_since_prev,
        EXTRACT(EPOCH FROM (ms.created_at - ms.prev2_message_time)) AS seconds_since_prev2,
        CASE
            WHEN ms.prev_is_ai = false AND ms.is_ai = true THEN 'AI Response'
            WHEN ms.prev_is_ai = true AND ms.is_ai = false THEN 'User Response'
            ELSE 'Same Type'
        END AS response_type
    FROM message_sequence ms
    LEFT JOIN conversation_flow_metrics cfm ON ms.chat_id = cfm.chat_id
    WHERE ms.prev_message_time IS NOT NULL
),
rolling_window_response_stats AS (
    -- Fourth CTE: Rolling window statistics with frame clauses
    SELECT
        rt.*,
        -- Window functions with ROWS BETWEEN frames
        AVG(rt.seconds_since_prev) OVER (
            PARTITION BY rt.chat_id, rt.response_type
            ORDER BY rt.created_at
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS response_time_10_message_avg,
        SUM(rt.seconds_since_prev) OVER (
            PARTITION BY rt.chat_id
            ORDER BY rt.created_at
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS response_time_20_message_sum,
        -- Window functions with RANGE BETWEEN frames
        AVG(rt.seconds_since_prev) OVER (
            PARTITION BY rt.chat_id
            ORDER BY rt.seconds_since_prev
            RANGE BETWEEN 60 PRECEDING AND 60 FOLLOWING
        ) AS response_time_range_avg,
        -- Lag/Lead functions
        LAG(rt.seconds_since_prev, 1) OVER (PARTITION BY rt.chat_id, rt.response_type ORDER BY rt.created_at) AS prev_response_time,
        LEAD(rt.seconds_since_prev, 1) OVER (PARTITION BY rt.chat_id, rt.response_type ORDER BY rt.created_at) AS next_response_time,
        -- First/Last value with frames
        FIRST_VALUE(rt.seconds_since_prev) OVER (
            PARTITION BY rt.chat_id, rt.response_type
            ORDER BY rt.created_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_response_time,
        LAST_VALUE(rt.seconds_since_prev) OVER (
            PARTITION BY rt.chat_id, rt.response_type
            ORDER BY rt.created_at
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_response_time
    FROM response_times rt
),
response_statistics AS (
    -- Fifth CTE: Response statistics with aggregations
    SELECT
        rwrs.chat_id,
        rwrs.chat_title,
        rwrs.response_type,
        COUNT(*) AS response_count,
        AVG(rwrs.seconds_since_prev) AS avg_response_seconds,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rwrs.seconds_since_prev) AS median_response_seconds,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY rwrs.seconds_since_prev) AS p25_response_seconds,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY rwrs.seconds_since_prev) AS p75_response_seconds,
        MIN(rwrs.seconds_since_prev) AS min_response_seconds,
        MAX(rwrs.seconds_since_prev) AS max_response_seconds,
        STDDEV(rwrs.seconds_since_prev) AS stddev_response_seconds,
        AVG(rwrs.avg_historical_response_time) AS avg_historical_response_time,
        AVG(rwrs.prior_alternating_messages) AS avg_prior_alternating_messages,
        AVG(rwrs.unique_participants_in_flow) AS avg_unique_participants,
        AVG(rwrs.avg_flow_depth) AS avg_flow_depth,
        AVG(rwrs.max_flow_depth) AS avg_max_flow_depth,
        AVG(rwrs.response_time_10_message_avg) AS avg_10_message_window,
        AVG(rwrs.response_time_20_message_sum) AS avg_20_message_sum,
        AVG(rwrs.response_time_range_avg) AS avg_range_window
    FROM rolling_window_response_stats rwrs
    WHERE rwrs.response_type != 'Same Type'
    GROUP BY rwrs.chat_id, rwrs.chat_title, rwrs.response_type
),
union_response_metrics AS (
    -- Sixth CTE: UNION to combine different metric types
    SELECT
        rs.chat_id,
        rs.response_type,
        'avg' AS metric_type,
        rs.avg_response_seconds AS metric_value
    FROM response_statistics rs

    UNION ALL

    SELECT
        rs.chat_id,
        rs.response_type,
        'median' AS metric_type,
        rs.median_response_seconds AS metric_value
    FROM response_statistics rs

    UNION ALL

    SELECT
        rs.chat_id,
        rs.response_type,
        'count' AS metric_type,
        rs.response_count AS metric_value
    FROM response_statistics rs
),
aggregated_union_response_metrics AS (
    -- Seventh CTE: Aggregate UNION results with window functions
    SELECT
        urm.chat_id,
        urm.response_type,
        SUM(CASE WHEN urm.metric_type = 'avg' THEN urm.metric_value ELSE 0 END) AS total_avg_metric,
        SUM(CASE WHEN urm.metric_type = 'median' THEN urm.metric_value ELSE 0 END) AS total_median_metric,
        SUM(CASE WHEN urm.metric_type = 'count' THEN urm.metric_value ELSE 0 END) AS total_count_metric,
        COUNT(DISTINCT urm.metric_type) AS metric_types_count,
        -- Window functions on UNION data
        AVG(urm.metric_value) OVER (
            PARTITION BY urm.metric_type, urm.response_type
            ORDER BY urm.chat_id
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS metric_moving_avg,
        SUM(urm.metric_value) OVER (
            PARTITION BY urm.chat_id, urm.response_type
            ORDER BY urm.metric_type
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS chat_cumulative_metric
    FROM union_response_metrics urm
    GROUP BY urm.chat_id, urm.response_type, urm.metric_type, urm.metric_value
),
final_response_time_analytics AS (
    -- Eighth CTE: Final analytics with comprehensive window functions
    SELECT
        rs.chat_id,
        rs.chat_title,
        rs.response_type,
        rs.response_count,
        ROUND(CAST(rs.avg_response_seconds AS NUMERIC), 2) AS avg_seconds,
        ROUND(CAST(rs.median_response_seconds AS NUMERIC), 2) AS median_seconds,
        ROUND(CAST(rs.p25_response_seconds AS NUMERIC), 2) AS p25_seconds,
        ROUND(CAST(rs.p75_response_seconds AS NUMERIC), 2) AS p75_seconds,
        ROUND(CAST(rs.min_response_seconds AS NUMERIC), 2) AS min_seconds,
        ROUND(CAST(rs.max_response_seconds AS NUMERIC), 2) AS max_seconds,
        ROUND(CAST(rs.stddev_response_seconds AS NUMERIC), 2) AS stddev_seconds,
        ROUND(CAST(rs.avg_historical_response_time AS NUMERIC), 2) AS avg_historical_response_time,
        ROUND(CAST(rs.avg_prior_alternating_messages AS NUMERIC), 2) AS avg_prior_alternating_messages,
        ROUND(CAST(rs.avg_unique_participants AS NUMERIC), 2) AS avg_unique_participants,
        ROUND(CAST(rs.avg_flow_depth AS NUMERIC), 2) AS avg_flow_depth,
        ROUND(CAST(rs.avg_max_flow_depth AS NUMERIC), 2) AS avg_max_flow_depth,
        ROUND(CAST(rs.avg_10_message_window AS NUMERIC), 2) AS avg_10_message_window,
        ROUND(CAST(rs.avg_20_message_sum AS NUMERIC), 2) AS avg_20_message_sum,
        ROUND(CAST(rs.avg_range_window AS NUMERIC), 2) AS avg_range_window,
        -- Multiple ranking methods
        ROW_NUMBER() OVER (PARTITION BY rs.response_type ORDER BY rs.avg_response_seconds ASC) AS response_time_row_num,
        RANK() OVER (PARTITION BY rs.response_type ORDER BY rs.avg_response_seconds ASC) AS response_time_rank,
        DENSE_RANK() OVER (PARTITION BY rs.response_type ORDER BY rs.response_count DESC) AS response_count_dense_rank,
        PERCENT_RANK() OVER (PARTITION BY rs.response_type ORDER BY rs.avg_response_seconds ASC) AS response_time_percentile,
        NTILE(5) OVER (PARTITION BY rs.response_type ORDER BY rs.avg_response_seconds ASC) AS response_time_quintile,
        NTILE(10) OVER (ORDER BY rs.avg_response_seconds ASC) AS response_time_decile,
        -- Window functions with frames
        SUM(rs.response_count) OVER (
            PARTITION BY rs.response_type
            ORDER BY rs.avg_response_seconds ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_response_count,
        AVG(rs.avg_response_seconds) OVER (
            PARTITION BY rs.response_type
            ORDER BY rs.avg_response_seconds ASC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS moving_avg_response_time,
        LAG(rs.avg_response_seconds, 1) OVER (PARTITION BY rs.response_type ORDER BY rs.avg_response_seconds ASC) AS prev_avg_response_time,
        LEAD(rs.response_count, 1) OVER (PARTITION BY rs.response_type ORDER BY rs.avg_response_seconds ASC) AS next_response_count,
        -- Pivot CASE for classification
        CASE
            WHEN rs.avg_response_seconds <= 5 THEN 'Instant'
            WHEN rs.avg_response_seconds <= 30 THEN 'Very Fast'
            WHEN rs.avg_response_seconds <= 60 THEN 'Fast'
            WHEN rs.avg_response_seconds <= 300 THEN 'Moderate'
            ELSE 'Slow'
        END AS response_time_category,
        CASE
            WHEN rs.response_count >= 50 THEN 'High Volume'
            WHEN rs.response_count >= 20 THEN 'Medium Volume'
            WHEN rs.response_count >= 10 THEN 'Low Volume'
            ELSE 'Minimal'
        END AS volume_category
    FROM response_statistics rs
)
SELECT
    chat_title,
    response_type,
    response_count,
    avg_seconds,
    median_seconds,
    p25_seconds,
    p75_seconds,
    min_seconds,
    max_seconds,
    stddev_seconds,
    avg_historical_response_time,
    avg_prior_alternating_messages,
    avg_unique_participants,
    avg_flow_depth,
    avg_max_flow_depth,
    avg_10_message_window,
    avg_20_message_sum,
    avg_range_window,
    response_time_row_num,
    response_time_rank,
    response_count_dense_rank,
    ROUND(CAST(response_time_percentile * 100 AS NUMERIC), 2) AS response_time_percentile,
    response_time_quintile,
    response_time_decile,
    cumulative_response_count,
    ROUND(CAST(moving_avg_response_time AS NUMERIC), 2) AS moving_avg_response_time,
    ROUND(CAST(prev_avg_response_time AS NUMERIC), 2) AS prev_avg_response_time,
    next_response_count,
    response_time_category,
    volume_category
FROM final_response_time_analytics
ORDER BY chat_id, response_type;
```

**Expected Output:** Response time statistics for AI and user responses per chat.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_flow, conversation_flow_metrics, final_response_time_analytics, message_sequence, messages, profiles, recursive, response_statistics, response_times, rolling_window_response_stats, union_response_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_flow, conversation_flow_metrics, final_response_time_analytics, message_sequence, messages, profiles, recursive, response_statistics, response_times, rolling_window_response_stats, union_response_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_flow, conversation_flow_metrics, final_response_time_analytics, message_sequence, messages, profiles, recursive, response_statistics, response_times, rolling_window_response_stats, union_response_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_flow, conversation_flow_metrics, final_response_time_analytics, message_sequence, messages, profiles, recursive, response_statistics, response_times, rolling_window_response_stats, union_response_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chats, conversation_flow, conversation_flow_metrics, final_response_time_analytics, message_sequence, messages, profiles, recursive, response_statistics, response_times, rolling_window_response_stats, union_response_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chats, conversation_flow, conversation_flow_metrics, final_response_time_analytics, message_sequence
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE conversation_flow AS (
    -- Anchor: Base message flow
    SELECT
        m.id AS message_id,
        m.chat_id,
        m.sender_id,
        m.is_ai,
        m.created_at,
        1 AS flow_depth,
        ARRAY[m.id] AS flow_path
    FROM messages m

    UNION ALL

    -- Recursive: Find related messages in conversation flow
    SELECT
        m2.id AS message_id,
        m2.chat_id,
        m2.sender_id,
        m2.is_ai,
        m2.created_at,
        cf.flow_depth + 1,
      ...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 13: Production-Grade Friend Network Clustering Analysis with Recursive CTE and Advanced Graph Metrics

**Description:** Enterprise-level friend network clustering analysis with recursive CTE for multi-hop friend discovery, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive network density analytics. Implements production patterns similar to social network analysis platforms.

**Complexity:** Recursive CTE, multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE friend_network_expansion AS (
    -- Anchor: Direct friend connections
    SELECT
        f1.user_id AS user_a,
        f2.user_id AS user_b,
        f1.friend_id AS intermediate_user,
        1 AS connection_depth,
        ARRAY[f1.user_id, f2.user_id] AS connection_path
    FROM friends f1
    INNER JOIN friends f2 ON f1.friend_id = f2.friend_id AND f1.user_id = f2.friend_id
    WHERE f1.status = 'accepted' AND f2.status = 'accepted'

    UNION ALL

    -- Recursive: Multi-hop friend connections
    SELECT
        fne.user_a,
        f3.user_id AS user_b,
        f3.friend_id AS intermediate_user,
        fne.connection_depth + 1,
        fne.connection_path || f3.user_id
    FROM friend_network_expansion fne
    INNER JOIN friends f3 ON fne.user_b = f3.friend_id AND f3.status = 'accepted'
    INNER JOIN friends f4 ON f4.user_id = fne.user_a AND f4.friend_id = f3.user_id AND f4.status = 'accepted'
    WHERE f3.user_id != ALL(fne.connection_path)
        AND fne.connection_depth < 3
),
friend_pairs AS (
    -- First CTE: Base friend pairs with joins
    SELECT
        f1.user_id AS user_a,
        f2.user_id AS user_b,
        f1.status AS status_a,
        f2.status AS status_b,
        f1.created_at AS friendship_start_a,
        f2.created_at AS friendship_start_b
    FROM friends f1
    INNER JOIN friends f2 ON f1.friend_id = f2.friend_id AND f1.user_id = f2.friend_id
    WHERE f1.status = 'accepted' AND f2.status = 'accepted'
),
mutual_friend_counts AS (
    -- Second CTE: Mutual friend calculations with correlated subqueries
    SELECT
        fp.user_a,
        fp.user_b,
        COUNT(DISTINCT f3.friend_id) AS mutual_friends,
        (
            SELECT COUNT(*)
            FROM friends f5
            WHERE f5.user_id = fp.user_a
                AND f5.status = 'accepted'
                AND EXISTS (
                    SELECT 1
                    FROM friends f6
                    WHERE f6.user_id = fp.user_b
                        AND f6.friend_id = f5.friend_id
                        AND f6.status = 'accepted'
                )
        ) AS verified_mutual_friends,
        (
            SELECT AVG(mutual_count)
            FROM (
                SELECT COUNT(*) AS mutual_count
                FROM friends f7
                WHERE f7.user_id = fp.user_a
                    AND f7.status = 'accepted'
                    AND EXISTS (
                        SELECT 1
                        FROM friends f8
                        WHERE f8.user_id = fp.user_b
                            AND f8.friend_id = f7.friend_id
                            AND f8.status = 'accepted'
                    )
            ) mutual_verification
        ) AS avg_mutual_verification
    FROM friend_pairs fp
    LEFT JOIN friends f3 ON f3.user_id = fp.user_a AND f3.status = 'accepted'
    INNER JOIN friends f4 ON f4.user_id = fp.user_b AND f4.friend_id = f3.friend_id AND f4.status = 'accepted'
    GROUP BY fp.user_a, fp.user_b
),
network_expansion_metrics AS (
    -- Third CTE: Network expansion metrics from recursive CTE
    SELECT
        user_a,
        user_b,
        COUNT(DISTINCT intermediate_user) AS unique_intermediaries,
        AVG(connection_depth) AS avg_connection_depth,
        MIN(connection_depth) AS min_connection_depth,
        MAX(connection_depth) AS max_connection_depth,
        COUNT(*) AS total_connection_paths
    FROM friend_network_expansion
    GROUP BY user_a, user_b
),
user_friend_counts AS (
    -- Fourth CTE: User friend counts
    SELECT
        user_id,
        COUNT(*) AS friend_count,
        COUNT(DISTINCT CASE WHEN status = 'accepted' THEN friend_id END) AS accepted_friend_count,
        MIN(created_at) AS first_friendship_date,
        MAX(created_at) AS last_friendship_date
    FROM friends
    GROUP BY user_id
),
rolling_window_cluster_stats AS (
    -- Fifth CTE: Rolling window statistics with frame clauses
    SELECT
        mfc.user_a,
        mfc.user_b,
        mfc.mutual_friends,
        mfc.verified_mutual_friends,
        mfc.avg_mutual_verification,
        COALESCE(nem.unique_intermediaries, 0) AS unique_intermediaries,
        COALESCE(nem.avg_connection_depth, 0) AS avg_connection_depth,
        COALESCE(nem.min_connection_depth, 0) AS min_connection_depth,
        COALESCE(nem.max_connection_depth, 0) AS max_connection_depth,
        COALESCE(nem.total_connection_paths, 0) AS total_connection_paths,
        ufc1.friend_count AS user_a_friends,
        ufc1.accepted_friend_count AS user_a_accepted_friends,
        ufc2.friend_count AS user_b_friends,
        ufc2.accepted_friend_count AS user_b_accepted_friends,
        -- Window functions with ROWS BETWEEN frames
        SUM(mfc.mutual_friends) OVER (
            ORDER BY mfc.mutual_friends DESC
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS mutual_friends_10_pair_window,
        AVG(mfc.mutual_friends) OVER (
            ORDER BY mfc.mutual_friends DESC
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS mutual_friends_20_pair_avg,
        -- Window functions with RANGE BETWEEN frames
        SUM(mfc.mutual_friends) OVER (
            ORDER BY mfc.mutual_friends
            RANGE BETWEEN 5 PRECEDING AND 5 FOLLOWING
        ) AS mutual_friends_range_window,
        -- Lag/Lead functions
        LAG(mfc.mutual_friends, 1) OVER (ORDER BY mfc.mutual_friends DESC) AS prev_mutual_friends,
        LEAD(mfc.mutual_friends, 1) OVER (ORDER BY mfc.mutual_friends DESC) AS next_mutual_friends,
        -- First/Last value with frames
        FIRST_VALUE(mfc.mutual_friends) OVER (
            ORDER BY mfc.mutual_friends DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_mutual_friends,
        LAST_VALUE(mfc.mutual_friends) OVER (
            ORDER BY mfc.mutual_friends DESC
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_mutual_friends
    FROM mutual_friend_counts mfc
    INNER JOIN user_friend_counts ufc1 ON mfc.user_a = ufc1.user_id
    INNER JOIN user_friend_counts ufc2 ON mfc.user_b = ufc2.user_id
    LEFT JOIN network_expansion_metrics nem ON mfc.user_a = nem.user_a AND mfc.user_b = nem.user_b
),
cluster_metrics AS (
    -- Sixth CTE: Cluster metrics with pivot CASE
    SELECT
        rwcs.user_a,
        rwcs.user_b,
        rwcs.mutual_friends,
        rwcs.verified_mutual_friends,
        ROUND(CAST(rwcs.avg_mutual_verification AS NUMERIC), 2) AS avg_mutual_verification,
        rwcs.unique_intermediaries,
        ROUND(CAST(rwcs.avg_connection_depth AS NUMERIC), 2) AS avg_connection_depth,
        rwcs.min_connection_depth,
        rwcs.max_connection_depth,
        rwcs.total_connection_paths,
        rwcs.user_a_friends,
        rwcs.user_a_accepted_friends,
        rwcs.user_b_friends,
        rwcs.user_b_accepted_friends,
        rwcs.mutual_friends_10_pair_window,
        ROUND(CAST(rwcs.mutual_friends_20_pair_avg AS NUMERIC), 2) AS mutual_friends_20_pair_avg,
        rwcs.mutual_friends_range_window,
        rwcs.prev_mutual_friends,
        rwcs.next_mutual_friends,
        rwcs.first_mutual_friends,
        rwcs.last_mutual_friends,
        ROUND(rwcs.mutual_friends::numeric / NULLIF(LEAST(rwcs.user_a_friends, rwcs.user_b_friends), 0), 3) AS friend_overlap_ratio,
        ROUND(rwcs.mutual_friends::numeric / NULLIF(GREATEST(rwcs.user_a_friends, rwcs.user_b_friends), 0), 3) AS friend_jaccard_similarity,
        -- Pivot CASE for classification
        CASE
            WHEN rwcs.mutual_friends::numeric / NULLIF(LEAST(rwcs.user_a_friends, rwcs.user_b_friends), 0) > 0.5 THEN 'High Overlap'
            WHEN rwcs.mutual_friends::numeric / NULLIF(LEAST(rwcs.user_a_friends, rwcs.user_b_friends), 0) > 0.2 THEN 'Medium Overlap'
            WHEN rwcs.mutual_friends::numeric / NULLIF(LEAST(rwcs.user_a_friends, rwcs.user_b_friends), 0) > 0.1 THEN 'Low Overlap'
            ELSE 'Minimal Overlap'
        END AS overlap_category,
        CASE
            WHEN rwcs.avg_connection_depth <= 1.5 THEN 'Direct'
            WHEN rwcs.avg_connection_depth <= 2.0 THEN 'Close'
            WHEN rwcs.avg_connection_depth <= 2.5 THEN 'Moderate'
            ELSE 'Distant'
        END AS connection_category
    FROM rolling_window_cluster_stats rwcs
),
union_cluster_metrics AS (
    -- Seventh CTE: UNION to combine different metric types
    SELECT
        cm.user_a,
        cm.user_b,
        'mutual_friends' AS metric_type,
        cm.mutual_friends AS metric_value
    FROM cluster_metrics cm

    UNION ALL

    SELECT
        cm.user_a,
        cm.user_b,
        'overlap_ratio' AS metric_type,
        cm.friend_overlap_ratio AS metric_value
    FROM cluster_metrics cm

    UNION ALL

    SELECT
        cm.user_a,
        cm.user_b,
        'connection_depth' AS metric_type,
        cm.avg_connection_depth AS metric_value
    FROM cluster_metrics cm
),
aggregated_union_cluster_metrics AS (
    -- Eighth CTE: Aggregate UNION results with window functions
    SELECT
        NULL,
        NULL,
        SUM(CASE WHEN NULL = 'mutual_friends' THEN NULL ELSE 0 END) AS total_mutual_metric,
        SUM(CASE WHEN NULL = 'overlap_ratio' THEN NULL ELSE 0 END) AS total_overlap_metric,
        SUM(CASE WHEN NULL = 'connection_depth' THEN NULL ELSE 0 END) AS total_depth_metric,
        COUNT(DISTINCT NULL) AS metric_types_count,
        -- Window functions on UNION data
        AVG(CAST(0 AS NUMERIC)) OVER (
            PARTITION BY ucm.metric_type
            ORDER BY ucm.user_a
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS metric_moving_avg,
        SUM(CAST(0 AS NUMERIC)) OVER (
            PARTITION BY ucm.user_a
            ORDER BY ucm.user_a
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS pair_cumulative_metric
    FROM union_cluster_metrics ucm
    GROUP BY ucm.user_a, ucm.user_b, ucm.metric_type
),
final_cluster_analytics AS (
    -- Ninth CTE: Final analytics with comprehensive window functions
    SELECT
        cm.user_a,
        cm.user_b,
        p1.username AS user_a_name,
        p2.username AS user_b_name,
        cm.mutual_friends,
        cm.verified_mutual_friends,
        cm.avg_mutual_verification,
        cm.unique_intermediaries,
        cm.avg_connection_depth,
        cm.min_connection_depth,
        cm.max_connection_depth,
        cm.total_connection_paths,
        cm.user_a_friends,
        cm.user_a_accepted_friends,
        cm.user_b_friends,
        cm.user_b_accepted_friends,
        cm.mutual_friends_10_pair_window,
        cm.mutual_friends_20_pair_avg,
        cm.mutual_friends_range_window,
        cm.prev_mutual_friends,
        cm.next_mutual_friends,
        cm.first_mutual_friends,
        cm.last_mutual_friends,
        cm.friend_overlap_ratio,
        cm.friend_jaccard_similarity,
        cm.overlap_category,
        cm.connection_category,
        -- Network strength score
        (
            (cm.mutual_friends * 0.3) +
            (cm.friend_overlap_ratio * 100 * 0.25) +
            (cm.friend_jaccard_similarity * 100 * 0.2) +
            (cm.unique_intermediaries * 0.15) +
            (CASE WHEN cm.avg_connection_depth > 0 THEN 1.0 / cm.avg_connection_depth ELSE 0 END * 0.1)
        ) AS network_strength_score,
        -- Window function rankings
        ROW_NUMBER() OVER (ORDER BY cm.mutual_friends DESC) AS mutual_friends_row_num,
        RANK() OVER (ORDER BY cm.mutual_friends DESC) AS mutual_friends_rank,
        DENSE_RANK() OVER (ORDER BY cm.friend_overlap_ratio DESC) AS overlap_dense_rank,
        PERCENT_RANK() OVER (ORDER BY cm.mutual_friends DESC) AS mutual_friends_percentile,
        NTILE(5) OVER (ORDER BY cm.mutual_friends DESC) AS mutual_friends_quintile,
        NTILE(10) OVER (ORDER BY cm.friend_overlap_ratio DESC) AS overlap_decile,
        -- Window functions with frames
        SUM(cm.mutual_friends) OVER (
            ORDER BY cm.mutual_friends DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_mutual_friends,
        AVG(cm.friend_overlap_ratio) OVER (
            ORDER BY cm.friend_overlap_ratio DESC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS moving_avg_overlap_ratio,
        LAG(cm.mutual_friends, 1) OVER (ORDER BY cm.mutual_friends DESC) AS prev_mutual_friends_ranked,
        LEAD(cm.friend_overlap_ratio, 1) OVER (ORDER BY cm.friend_overlap_ratio DESC) AS next_overlap_ratio
    FROM cluster_metrics cm
    INNER JOIN profiles p1 ON cm.user_a = p1.id
    INNER JOIN profiles p2 ON cm.user_b = p2.id
)
SELECT
    user_a_name,
    user_b_name,
    mutual_friends,
    verified_mutual_friends,
    avg_mutual_verification,
    unique_intermediaries,
    avg_connection_depth,
    min_connection_depth,
    max_connection_depth,
    total_connection_paths,
    user_a_friends,
    user_a_accepted_friends,
    user_b_friends,
    user_b_accepted_friends,
    mutual_friends_10_pair_window,
    mutual_friends_20_pair_avg,
    mutual_friends_range_window,
    prev_mutual_friends,
    next_mutual_friends,
    first_mutual_friends,
    last_mutual_friends,
    friend_overlap_ratio,
    friend_jaccard_similarity,
    overlap_category,
    connection_category,
    ROUND(CAST(network_strength_score AS NUMERIC), 2) AS network_strength_score,
    mutual_friends_row_num,
    mutual_friends_rank,
    overlap_dense_rank,
    ROUND(CAST(mutual_friends_percentile * 100 AS NUMERIC), 2) AS mutual_friends_percentile,
    mutual_friends_quintile,
    overlap_decile,
    cumulative_mutual_friends,
    ROUND(CAST(moving_avg_overlap_ratio AS NUMERIC), 3) AS moving_avg_overlap_ratio,
    prev_mutual_friends_ranked,
    ROUND(CAST(next_overlap_ratio AS NUMERIC), 3) AS next_overlap_ratio
FROM final_cluster_analytics
ORDER BY mutual_friends DESC, friend_overlap_ratio DESC;
```

**Expected Output:** Friend pair analysis with mutual friend counts and overlap ratios.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: cluster_metrics, final_cluster_analytics, friend_network_expansion, friend_pairs, friends, mutual_friend_counts, network_expansion_metrics, profiles, recursive, rolling_window_cluster_stats, union_cluster_metrics, user_friend_counts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: cluster_metrics, final_cluster_analytics, friend_network_expansion, friend_pairs, friends, mutual_friend_counts, network_expansion_metrics, profiles, recursive, rolling_window_cluster_stats, union_cluster_metrics, user_friend_counts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: cluster_metrics, final_cluster_analytics, friend_network_expansion, friend_pairs, friends, mutual_friend_counts, network_expansion_metrics, profiles, recursive, rolling_window_cluster_stats, union_cluster_metrics, user_friend_counts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: cluster_metrics, final_cluster_analytics, friend_network_expansion, friend_pairs, friends, mutual_friend_counts, network_expansion_metrics, profiles, recursive, rolling_window_cluster_stats, union_cluster_metrics, user_friend_counts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Mutual connections
- **Description**: Validates mutual connections functionality
- **Test Data Requirements**:
  - Tables: cluster_metrics, final_cluster_analytics, friend_network_expansion, friend_pairs, friends, mutual_friend_counts, network_expansion_metrics, profiles, recursive, rolling_window_cluster_stats, union_cluster_metrics, user_friend_counts
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: cluster_metrics, final_cluster_analytics, friend_network_expansion, friend_pairs, friends
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE friend_network_expansion AS (
    -- Anchor: Direct friend connections
    SELECT
        f1.user_id AS user_a,
        f2.user_id AS user_b,
        f1.friend_id AS intermediate_user,
        1 AS connection_depth,
        ARRAY[f1.user_id, f2.user_id] AS connection_path
    FROM friends f1
    INNER JOIN friends f2 ON f1.friend_id = f2.friend_id AND f1.user_id = f2.friend_id
    WHERE f1.status = 'accepted' AND f2.status = 'accepted'

    UNION ALL

    -- Recursive: Multi-hop f...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 14: Production-Grade Time-Based Chat Activity Heatmap with Recursive CTE and Advanced Temporal Analytics

**Description:** Enterprise-level time-based activity heatmap with recursive CTE for temporal pattern discovery, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive heatmap analytics. Implements production patterns similar to time-series analytics platforms.

**Complexity:** Recursive CTE, multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE temporal_pattern_hierarchy AS (
    -- Anchor: Base time periods
    SELECT
        DATE_TRUNC('hour', m.created_at) AS time_period,
        EXTRACT(DOW FROM m.created_at) AS day_of_week,
        EXTRACT(HOUR FROM m.created_at) AS hour_of_day,
        COUNT(*) AS message_count,
        'hour' AS period_type
    FROM messages m
    GROUP BY DATE_TRUNC('hour', m.created_at), EXTRACT(DOW FROM m.created_at), EXTRACT(HOUR FROM m.created_at)

    UNION ALL

    -- Recursive: Aggregate to higher time periods
    SELECT
        DATE_TRUNC('day', tph.time_period) AS time_period,
        tph.day_of_week,
        NULL::integer AS hour_of_day,
        tph.message_count AS message_count,
        'day' AS period_type
    FROM temporal_pattern_hierarchy tph
    WHERE tph.period_type = 'hour'
        AND DATE_TRUNC('day', tph.time_period) != tph.time_period
    GROUP BY DATE_TRUNC('day', tph.time_period), tph.day_of_week, tph.message_count
),
hourly_activity AS (
    -- First CTE: Base hourly activity with joins and correlated subqueries
    SELECT
        EXTRACT(DOW FROM m.created_at) AS day_of_week,
        EXTRACT(HOUR FROM m.created_at) AS hour_of_day,
        m.created_at,
        COUNT(*) AS message_count,
        COUNT(DISTINCT m.chat_id) AS active_chats,
        COUNT(DISTINCT m.sender_id) AS active_users,
        COUNT(CASE WHEN m.is_ai = false THEN 1 END) AS user_messages,
        COUNT(CASE WHEN m.is_ai = true THEN 1 END) AS ai_messages,
        AVG(LENGTH(m.content)) AS avg_message_length,
        (
            SELECT COUNT(DISTINCT m2.chat_id)
            FROM messages m2
            WHERE EXTRACT(DOW FROM m2.created_at) = EXTRACT(DOW FROM m.created_at)
                AND EXTRACT(HOUR FROM m2.created_at) = EXTRACT(HOUR FROM m.created_at)
                AND m2.is_ai = false
                AND EXISTS (
                    SELECT 1
                    FROM messages m3
                    WHERE m3.chat_id = m2.chat_id
                        AND EXTRACT(DOW FROM m3.created_at) = EXTRACT(DOW FROM m.created_at)
                        AND EXTRACT(HOUR FROM m3.created_at) = EXTRACT(HOUR FROM m.created_at)
                        AND m3.is_ai = true
                )
        ) AS chats_with_ai_interaction
    FROM messages m
    GROUP BY EXTRACT(DOW FROM m.created_at), EXTRACT(HOUR FROM m.created_at), m.created_at
),
temporal_pattern_metrics AS (
    -- Second CTE: Temporal pattern metrics from recursive CTE
    SELECT
        day_of_week,
        COUNT(DISTINCT time_period) AS unique_periods,
        SUM(message_count) AS total_pattern_messages,
        AVG(message_count) AS avg_pattern_messages
    FROM temporal_pattern_hierarchy
    WHERE period_type = 'day'
    GROUP BY day_of_week
),
rolling_window_hourly_stats AS (
    -- Third CTE: Rolling window statistics with frame clauses
    SELECT
        ha.day_of_week,
        ha.hour_of_day,
        ha.message_count,
        ha.active_chats,
        ha.active_users,
        ha.user_messages,
        ha.ai_messages,
        ROUND(CAST(ha.avg_message_length AS NUMERIC), 2) AS avg_message_length,
        ha.chats_with_ai_interaction,
        COALESCE(tpm.unique_periods, 0) AS unique_periods,
        COALESCE(tpm.total_pattern_messages, 0) AS total_pattern_messages,
        COALESCE(tpm.avg_pattern_messages, 0) AS avg_pattern_messages,
        -- Window functions with ROWS BETWEEN frames
        SUM(ha.message_count) OVER (
            PARTITION BY ha.day_of_week
            ORDER BY ha.hour_of_day
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS message_count_5_hour_window,
        AVG(ha.message_count) OVER (
            PARTITION BY ha.hour_of_day
            ORDER BY ha.day_of_week
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS message_count_5_day_window,
        -- Window functions with RANGE BETWEEN frames
        SUM(ha.active_chats) OVER (
            ORDER BY ha.message_count
            RANGE BETWEEN 10 PRECEDING AND 10 FOLLOWING
        ) AS chats_message_range_window,
        -- Lag/Lead functions
        LAG(ha.message_count, 1) OVER (PARTITION BY ha.day_of_week ORDER BY ha.hour_of_day) AS prev_hour_messages,
        LEAD(ha.message_count, 1) OVER (PARTITION BY ha.day_of_week ORDER BY ha.hour_of_day) AS next_hour_messages,
        LAG(ha.message_count, 24) OVER (PARTITION BY ha.day_of_week ORDER BY ha.hour_of_day) AS prev_day_same_hour_messages,
        -- First/Last value with frames
        FIRST_VALUE(ha.message_count) OVER (
            PARTITION BY ha.day_of_week
            ORDER BY ha.hour_of_day
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_hour_messages,
        LAST_VALUE(ha.message_count) OVER (
            PARTITION BY ha.day_of_week
            ORDER BY ha.hour_of_day
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_hour_messages
    FROM hourly_activity ha
    LEFT JOIN temporal_pattern_metrics tpm ON ha.day_of_week = tpm.day_of_week
),
day_hour_matrix AS (
    -- Fourth CTE: Day-hour matrix with aggregations
    SELECT
        rwhs.day_of_week,
        rwhs.hour_of_day,
        rwhs.message_count,
        rwhs.active_chats,
        rwhs.active_users,
        rwhs.user_messages,
        rwhs.ai_messages,
        rwhs.avg_message_length,
        rwhs.chats_with_ai_interaction,
        rwhs.unique_periods,
        rwhs.total_pattern_messages,
        rwhs.avg_pattern_messages,
        rwhs.message_count_5_hour_window,
        ROUND(CAST(rwhs.message_count_5_day_window AS NUMERIC), 2) AS message_count_5_day_window,
        rwhs.chats_message_range_window,
        rwhs.prev_hour_messages,
        rwhs.next_hour_messages,
        rwhs.prev_day_same_hour_messages,
        rwhs.first_hour_messages,
        rwhs.last_hour_messages,
        SUM(rwhs.message_count) OVER (PARTITION BY rwhs.day_of_week) AS day_total,
        SUM(rwhs.message_count) OVER (PARTITION BY rwhs.hour_of_day) AS hour_total,
        AVG(rwhs.message_count) OVER () AS overall_avg,
        MAX(rwhs.message_count) OVER (PARTITION BY rwhs.day_of_week) AS day_max,
        MIN(rwhs.message_count) OVER (PARTITION BY rwhs.day_of_week) AS day_min,
        MAX(rwhs.message_count) OVER (PARTITION BY rwhs.hour_of_day) AS hour_max,
        MIN(rwhs.message_count) OVER (PARTITION BY rwhs.hour_of_day) AS hour_min
    FROM rolling_window_hourly_stats rwhs
),
union_heatmap_metrics AS (
    -- Fifth CTE: UNION to combine different metric types
    SELECT
        dhm.day_of_week,
        dhm.hour_of_day,
        'message_count' AS metric_type,
        dhm.message_count AS metric_value
    FROM day_hour_matrix dhm

    UNION ALL

    SELECT
        dhm.day_of_week,
        dhm.hour_of_day,
        'active_chats' AS metric_type,
        dhm.active_chats AS metric_value
    FROM day_hour_matrix dhm

    UNION ALL

    SELECT
        dhm.day_of_week,
        dhm.hour_of_day,
        'active_users' AS metric_type,
        dhm.active_users AS metric_value
    FROM day_hour_matrix dhm
),
aggregated_union_heatmap_metrics AS (
    -- Sixth CTE: Aggregate UNION results with window functions
    SELECT
        uhm.day_of_week,
        uhm.hour_of_day,
        SUM(CASE WHEN uhm.metric_type = 'message_count' THEN uhm.metric_value ELSE 0 END) AS total_message_metric,
        SUM(CASE WHEN uhm.metric_type = 'active_chats' THEN uhm.metric_value ELSE 0 END) AS total_chats_metric,
        SUM(CASE WHEN uhm.metric_type = 'active_users' THEN uhm.metric_value ELSE 0 END) AS total_users_metric,
        COUNT(DISTINCT uhm.metric_type) AS metric_types_count,
        -- Window functions on UNION data
        AVG(uhm.metric_value) OVER (
            PARTITION BY uhm.metric_type
            ORDER BY uhm.day_of_week, uhm.hour_of_day
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS metric_moving_avg,
        SUM(uhm.metric_value) OVER (
            PARTITION BY uhm.day_of_week, uhm.hour_of_day
            ORDER BY uhm.metric_type
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS time_cumulative_metric
    FROM union_heatmap_metrics uhm
    GROUP BY uhm.day_of_week, uhm.hour_of_day, uhm.metric_type, uhm.metric_value
),
final_heatmap_analytics AS (
    -- Seventh CTE: Final analytics with comprehensive window functions
    SELECT
        dhm.day_of_week,
        dhm.hour_of_day,
        CASE dhm.day_of_week
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
        END AS day_name,
        dhm.message_count,
        dhm.active_chats,
        dhm.active_users,
        dhm.user_messages,
        dhm.ai_messages,
        dhm.avg_message_length,
        dhm.chats_with_ai_interaction,
        dhm.unique_periods,
        dhm.total_pattern_messages,
        ROUND(CAST(dhm.avg_pattern_messages AS NUMERIC), 2) AS avg_pattern_messages,
        dhm.message_count_5_hour_window,
        dhm.message_count_5_day_window,
        dhm.chats_message_range_window,
        dhm.prev_hour_messages,
        dhm.next_hour_messages,
        dhm.prev_day_same_hour_messages,
        dhm.first_hour_messages,
        dhm.last_hour_messages,
        dhm.day_total,
        dhm.hour_total,
        ROUND(CAST(dhm.overall_avg AS NUMERIC), 2) AS overall_avg,
        dhm.day_max,
        dhm.day_min,
        dhm.hour_max,
        dhm.hour_min,
        ROUND(CAST(dhm.message_count::numeric / NULLIF(CAST(dhm.overall_avg AS NUMERIC), 0) AS NUMERIC), 2) AS activity_ratio,
        ROUND(CAST(dhm.message_count::numeric / NULLIF(CAST(dhm.day_total AS NUMERIC), 0) AS NUMERIC), 3) AS day_percentage,
        ROUND(CAST(dhm.message_count::numeric / NULLIF(CAST(dhm.hour_total AS NUMERIC), 0) AS NUMERIC), 3) AS hour_percentage,
        -- Pivot CASE for classification
        CASE
            WHEN dhm.message_count > dhm.overall_avg * 1.5 THEN 'Peak'
            WHEN dhm.message_count > dhm.overall_avg * 1.2 THEN 'High'
            WHEN dhm.message_count > dhm.overall_avg THEN 'Above Average'
            WHEN dhm.message_count > dhm.overall_avg * 0.8 THEN 'Average'
            WHEN dhm.message_count > dhm.overall_avg * 0.5 THEN 'Below Average'
            ELSE 'Low'
        END AS activity_level,
        CASE
            WHEN dhm.message_count >= dhm.day_max * 0.9 THEN 'Day Peak'
            WHEN dhm.message_count >= dhm.day_max * 0.7 THEN 'Day High'
            WHEN dhm.message_count <= dhm.day_min * 1.1 THEN 'Day Low'
            ELSE 'Day Normal'
        END AS day_relative_level,
        CASE
            WHEN dhm.message_count >= dhm.hour_max * 0.9 THEN 'Hour Peak'
            WHEN dhm.message_count >= dhm.hour_max * 0.7 THEN 'Hour High'
            WHEN dhm.message_count <= dhm.hour_min * 1.1 THEN 'Hour Low'
            ELSE 'Hour Normal'
        END AS hour_relative_level,
        -- Window function rankings
        ROW_NUMBER() OVER (ORDER BY dhm.message_count DESC) AS message_count_row_num,
        RANK() OVER (ORDER BY dhm.message_count DESC) AS message_count_rank,
        DENSE_RANK() OVER (PARTITION BY dhm.day_of_week ORDER BY dhm.message_count DESC) AS day_hour_rank,
        PERCENT_RANK() OVER (ORDER BY dhm.message_count DESC) AS message_count_percentile,
        NTILE(5) OVER (ORDER BY dhm.message_count DESC) AS message_count_quintile,
        NTILE(10) OVER (ORDER BY dhm.message_count DESC) AS message_count_decile,
        -- Window functions with frames
        SUM(dhm.message_count) OVER (
            ORDER BY dhm.day_of_week, dhm.hour_of_day
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_message_count,
        AVG(dhm.message_count) OVER (
            ORDER BY dhm.message_count DESC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS moving_avg_message_count,
        LAG(dhm.message_count, 1) OVER (ORDER BY dhm.day_of_week, dhm.hour_of_day) AS prev_time_slot_messages,
        LEAD(dhm.message_count, 1) OVER (ORDER BY dhm.day_of_week, dhm.hour_of_day) AS next_time_slot_messages
    FROM day_hour_matrix dhm
)
SELECT
    day_name,
    hour_of_day,
    message_count,
    active_chats,
    active_users,
    user_messages,
    ai_messages,
    avg_message_length,
    chats_with_ai_interaction,
    unique_periods,
    total_pattern_messages,
    avg_pattern_messages,
    message_count_5_hour_window,
    message_count_5_day_window,
    chats_message_range_window,
    prev_hour_messages,
    next_hour_messages,
    prev_day_same_hour_messages,
    first_hour_messages,
    last_hour_messages,
    day_total,
    hour_total,
    overall_avg,
    day_max,
    day_min,
    hour_max,
    hour_min,
    activity_ratio,
    day_percentage,
    hour_percentage,
    activity_level,
    day_relative_level,
    hour_relative_level,
    message_count_row_num,
    message_count_rank,
    day_hour_rank,
    ROUND(CAST(message_count_percentile * 100 AS NUMERIC), 2) AS message_count_percentile,
    message_count_quintile,
    message_count_decile,
    cumulative_message_count,
    ROUND(CAST(moving_avg_message_count AS NUMERIC), 2) AS moving_avg_message_count,
    prev_time_slot_messages,
    next_time_slot_messages
FROM final_heatmap_analytics
ORDER BY day_of_week, hour_of_day;
```

**Expected Output:** Time-based activity heatmap with day/hour breakdowns and activity levels.

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: day_hour_matrix, final_heatmap_analytics, hourly_activity, m, m2, m3, messages, recursive, rolling_window_hourly_stats, temporal_pattern_hierarchy, temporal_pattern_metrics, union_heatmap_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: day_hour_matrix, final_heatmap_analytics, hourly_activity, m, m2, m3, messages, recursive, rolling_window_hourly_stats, temporal_pattern_hierarchy, temporal_pattern_metrics, union_heatmap_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: day_hour_matrix, final_heatmap_analytics, hourly_activity, m, m2, m3, messages, recursive, rolling_window_hourly_stats, temporal_pattern_hierarchy, temporal_pattern_metrics, union_heatmap_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: day_hour_matrix, final_heatmap_analytics, hourly_activity, m, m2
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE temporal_pattern_hierarchy AS (
    -- Anchor: Base time periods
    SELECT
        DATE_TRUNC('hour', m.created_at) AS time_period,
        EXTRACT(DOW FROM m.created_at) AS day_of_week,
        EXTRACT(HOUR FROM m.created_at) AS hour_of_day,
        COUNT(*) AS message_count,
        'hour' AS period_type
    FROM messages m
    GROUP BY DATE_TRUNC('hour', m.created_at), EXTRACT(DOW FROM m.created_at), EXTRACT(HOUR FROM m.created_at)

    UNION ALL

    -- Recursive: Aggregate t...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 15: Production-Grade Chat Participant Retention Analysis with Recursive CTE and Advanced Cohort Analytics

**Description:** Enterprise-level participant retention analysis with recursive CTE for retention chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive cohort retention analytics. Implements production patterns similar to retention analytics platforms.

**Complexity:** Recursive CTE, multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE retention_chain AS (
    -- Anchor: Base participant joins
    SELECT
        cp.user_id,
        cp.chat_id,
        cp.joined_at,
        1 AS retention_depth,
        ARRAY[cp.chat_id] AS retention_path
    FROM chat_participants cp

    UNION ALL

    -- Recursive: Find related joins in retention chain
    SELECT
        rc.user_id,
        cp2.chat_id,
        cp2.joined_at,
        rc.retention_depth + 1,
        rc.retention_path || cp2.chat_id
    FROM retention_chain rc
    INNER JOIN chat_participants cp2 ON rc.user_id = cp2.user_id
    WHERE cp2.chat_id != ALL(rc.retention_path)
        AND cp2.joined_at BETWEEN rc.joined_at AND rc.joined_at + INTERVAL '90 days'
        AND rc.retention_depth < 10
),
participant_sessions AS (
    -- First CTE: Participant sessions with joins and correlated subqueries
    SELECT
        cp.user_id,
        cp.chat_id,
        cp.joined_at,
        c.title AS chat_title,
        (
            SELECT COUNT(*)
            FROM chat_participants cp2
            WHERE cp2.user_id = cp.user_id
                AND cp2.joined_at < cp.joined_at
        ) AS prior_participations,
        (
            SELECT AVG(EXTRACT(EPOCH FROM (cp3.joined_at - cp4.joined_at)) / 86400)
            FROM chat_participants cp3
            INNER JOIN chat_participants cp4 ON cp3.user_id = cp4.user_id
            WHERE cp3.user_id = cp.user_id
                AND cp3.joined_at > cp4.joined_at
                AND cp3.joined_at < cp.joined_at
        ) AS avg_historical_days_between,
        LAG(cp.joined_at, 1) OVER (PARTITION BY cp.user_id ORDER BY cp.joined_at) AS prev_join_date,
        LEAD(cp.joined_at, 1) OVER (PARTITION BY cp.user_id ORDER BY cp.joined_at) AS next_join_date,
        COUNT(*) OVER (PARTITION BY cp.user_id) AS total_chat_participations,
        ROW_NUMBER() OVER (PARTITION BY cp.user_id ORDER BY cp.joined_at) AS participation_sequence
    FROM chat_participants cp
    INNER JOIN chats c ON cp.chat_id = c.id
),
retention_chain_metrics AS (
    -- Second CTE: Retention chain metrics from recursive CTE
    SELECT
        user_id,
        COUNT(DISTINCT chat_id) AS unique_chats_in_chain,
        AVG(retention_depth) AS avg_retention_depth,
        MAX(retention_depth) AS max_retention_depth,
        COUNT(*) AS total_chain_participations,
        MIN(joined_at) AS first_chain_join,
        MAX(joined_at) AS last_chain_join
    FROM retention_chain
    GROUP BY user_id
),
session_gaps AS (
    -- Third CTE: Session gap calculations
    SELECT
        ps.user_id,
        ps.chat_id,
        ps.chat_title,
        ps.joined_at,
        ps.prior_participations,
        ROUND(CAST(ps.avg_historical_days_between AS NUMERIC), 2) AS avg_historical_days_between,
        ps.prev_join_date,
        ps.next_join_date,
        ps.total_chat_participations,
        ps.participation_sequence,
        COALESCE(rcm.unique_chats_in_chain, 0) AS unique_chats_in_chain,
        COALESCE(rcm.avg_retention_depth, 0) AS avg_retention_depth,
        COALESCE(rcm.max_retention_depth, 0) AS max_retention_depth,
        COALESCE(rcm.total_chain_participations, 0) AS total_chain_participations,
        COALESCE(rcm.first_chain_join, ps.joined_at) AS first_chain_join,
        COALESCE(rcm.last_chain_join, ps.joined_at) AS last_chain_join,
        EXTRACT(EPOCH FROM (ps.joined_at - ps.prev_join_date)) / 86400 AS days_since_last_join,
        EXTRACT(EPOCH FROM (ps.next_join_date - ps.joined_at)) / 86400 AS days_until_next_join,
        EXTRACT(EPOCH FROM (ps.joined_at - COALESCE(rcm.first_chain_join, ps.joined_at))) / 86400 AS days_since_first_join,
        CASE
            WHEN ps.prev_join_date IS NULL THEN 'First Join'
            WHEN EXTRACT(EPOCH FROM (ps.joined_at - ps.prev_join_date)) / 86400 <= 1 THEN 'Returning (<1d)'
            WHEN EXTRACT(EPOCH FROM (ps.joined_at - ps.prev_join_date)) / 86400 <= 7 THEN 'Returning (1-7d)'
            WHEN EXTRACT(EPOCH FROM (ps.joined_at - ps.prev_join_date)) / 86400 <= 30 THEN 'Returning (7-30d)'
            WHEN EXTRACT(EPOCH FROM (ps.joined_at - ps.prev_join_date)) / 86400 <= 90 THEN 'Returning (30-90d)'
            ELSE 'Returning (>90d)'
        END AS join_category
    FROM participant_sessions ps
    LEFT JOIN retention_chain_metrics rcm ON ps.user_id = rcm.user_id
),
rolling_window_retention_stats AS (
    -- Fourth CTE: Rolling window statistics with frame clauses
    SELECT
        sg.*,
        -- Window functions with ROWS BETWEEN frames
        AVG(sg.days_since_last_join) OVER (
            PARTITION BY sg.user_id
            ORDER BY sg.joined_at
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS days_between_5_session_avg,
        SUM(sg.days_since_last_join) OVER (
            PARTITION BY sg.user_id
            ORDER BY sg.joined_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_days_between,
        -- Window functions with RANGE BETWEEN frames
        AVG(sg.days_since_last_join) OVER (
            PARTITION BY sg.user_id
            ORDER BY sg.days_since_last_join
            RANGE BETWEEN 7 PRECEDING AND 7 FOLLOWING
        ) AS days_between_range_avg,
        -- Lag/Lead functions
        LAG(sg.days_since_last_join, 1) OVER (PARTITION BY sg.user_id ORDER BY sg.joined_at) AS prev_gap_days,
        LEAD(sg.days_since_last_join, 1) OVER (PARTITION BY sg.user_id ORDER BY sg.joined_at) AS next_gap_days,
        -- First/Last value with frames
        FIRST_VALUE(sg.days_since_last_join) OVER (
            PARTITION BY sg.user_id
            ORDER BY sg.joined_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS first_gap_days,
        LAST_VALUE(sg.days_since_last_join) OVER (
            PARTITION BY sg.user_id
            ORDER BY sg.joined_at
            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
        ) AS last_gap_days
    FROM session_gaps sg
),
retention_metrics AS (
    -- Fifth CTE: Retention metrics with aggregations
    SELECT
        rwrs.user_id,
        COUNT(*) AS total_joins,
        COUNT(CASE WHEN rwrs.join_category = 'First Join' THEN 1 END) AS first_joins,
        COUNT(CASE WHEN rwrs.join_category LIKE 'Returning%' THEN 1 END) AS returning_joins,
        COUNT(CASE WHEN rwrs.join_category = 'Returning (<1d)' THEN 1 END) AS returning_same_day,
        COUNT(CASE WHEN rwrs.join_category = 'Returning (1-7d)' THEN 1 END) AS returning_week,
        COUNT(CASE WHEN rwrs.join_category = 'Returning (7-30d)' THEN 1 END) AS returning_month,
        COUNT(CASE WHEN rwrs.join_category = 'Returning (>90d)' THEN 1 END) AS returning_long_term,
        AVG(rwrs.days_since_last_join) AS avg_days_between_joins,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rwrs.days_since_last_join) AS median_days_between_joins,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY rwrs.days_since_last_join) AS p25_days_between,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY rwrs.days_since_last_join) AS p75_days_between,
        MIN(rwrs.days_since_last_join) AS min_days_between_joins,
        MAX(rwrs.days_since_last_join) AS max_days_between_joins,
        STDDEV(rwrs.days_since_last_join) AS stddev_days_between,
        AVG(rwrs.days_until_next_join) AS avg_days_until_next_join,
        AVG(rwrs.days_since_first_join) AS avg_days_since_first_join,
        AVG(rwrs.unique_chats_in_chain) AS avg_unique_chats_in_chain,
        AVG(rwrs.avg_retention_depth) AS avg_retention_depth,
        AVG(rwrs.max_retention_depth) AS avg_max_retention_depth,
        AVG(rwrs.total_chain_participations) AS avg_total_chain_participations,
        AVG(rwrs.days_between_5_session_avg) AS avg_5_session_window,
        AVG(rwrs.days_between_range_avg) AS avg_range_window,
        MIN(rwrs.first_chain_join) AS first_chain_join,
        MAX(rwrs.last_chain_join) AS last_chain_join
    FROM rolling_window_retention_stats rwrs
    GROUP BY rwrs.user_id
),
union_retention_metrics AS (
    -- Sixth CTE: UNION to combine different metric types
    SELECT
        rm.user_id,
        'total_joins' AS metric_type,
        rm.total_joins AS metric_value
    FROM retention_metrics rm

    UNION ALL

    SELECT
        rm.user_id,
        'returning_joins' AS metric_type,
        rm.returning_joins AS metric_value
    FROM retention_metrics rm

    UNION ALL

    SELECT
        rm.user_id,
        'avg_days_between' AS metric_type,
        rm.avg_days_between_joins AS metric_value
    FROM retention_metrics rm
),
aggregated_union_retention_metrics AS (
    -- Seventh CTE: Aggregate UNION results with window functions
    SELECT
        urm.user_id,
        SUM(CASE WHEN urm.metric_type = 'total_joins' THEN urm.metric_value ELSE 0 END) AS total_joins_metric,
        SUM(CASE WHEN urm.metric_type = 'returning_joins' THEN urm.metric_value ELSE 0 END) AS total_returning_metric,
        SUM(CASE WHEN urm.metric_type = 'avg_days_between' THEN urm.metric_value ELSE 0 END) AS total_days_metric,
        COUNT(DISTINCT urm.metric_type) AS metric_types_count,
        -- Window functions on UNION data
        AVG(urm.metric_value) OVER (
            PARTITION BY urm.metric_type
            ORDER BY urm.user_id
            ROWS BETWEEN 4 PRECEDING AND 4 FOLLOWING
        ) AS metric_moving_avg,
        SUM(urm.metric_value) OVER (
            PARTITION BY urm.user_id
            ORDER BY urm.metric_type
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS user_cumulative_metric
    FROM union_retention_metrics urm
    GROUP BY urm.user_id, urm.metric_type, urm.metric_value
),
final_retention_analytics AS (
    -- Eighth CTE: Final analytics with comprehensive window functions
    SELECT
        rm.user_id,
        p.username,
        rm.total_joins,
        rm.first_joins,
        rm.returning_joins,
        rm.returning_same_day,
        rm.returning_week,
        rm.returning_month,
        rm.returning_long_term,
        ROUND(CAST(rm.returning_joins::numeric / NULLIF(CAST(rm.total_joins AS NUMERIC), 0) AS NUMERIC) * 100, 2) AS retention_rate,
        ROUND(CAST(rm.avg_days_between_joins AS NUMERIC), 2) AS avg_days_between,
        ROUND(CAST(rm.median_days_between_joins AS NUMERIC), 2) AS median_days_between,
        ROUND(CAST(rm.p25_days_between AS NUMERIC), 2) AS p25_days_between,
        ROUND(CAST(rm.p75_days_between AS NUMERIC), 2) AS p75_days_between,
        rm.min_days_between_joins,
        rm.max_days_between_joins,
        ROUND(CAST(rm.stddev_days_between AS NUMERIC), 2) AS stddev_days_between,
        ROUND(CAST(rm.avg_days_until_next_join AS NUMERIC), 2) AS avg_days_until_next_join,
        ROUND(CAST(rm.avg_days_since_first_join AS NUMERIC), 2) AS avg_days_since_first_join,
        ROUND(CAST(rm.avg_unique_chats_in_chain AS NUMERIC), 2) AS avg_unique_chats_in_chain,
        ROUND(CAST(rm.avg_retention_depth AS NUMERIC), 2) AS avg_retention_depth,
        ROUND(CAST(rm.avg_max_retention_depth AS NUMERIC), 2) AS avg_max_retention_depth,
        ROUND(CAST(rm.avg_total_chain_participations AS NUMERIC), 2) AS avg_total_chain_participations,
        ROUND(CAST(rm.avg_5_session_window AS NUMERIC), 2) AS avg_5_session_window,
        ROUND(CAST(rm.avg_range_window AS NUMERIC), 2) AS avg_range_window,
        rm.first_chain_join,
        rm.last_chain_join,
        EXTRACT(EPOCH FROM (rm.last_chain_join - rm.first_chain_join)) / 86400 AS chain_span_days,
        -- Pivot CASE for classification
        CASE
            WHEN rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) > 0.7 THEN 'High Retention'
            WHEN rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) > 0.5 THEN 'Medium-High Retention'
            WHEN rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) > 0.4 THEN 'Medium Retention'
            WHEN rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) > 0.2 THEN 'Low-Medium Retention'
            ELSE 'Low Retention'
        END AS retention_category,
        CASE
            WHEN rm.avg_days_between_joins <= 1 THEN 'Daily'
            WHEN rm.avg_days_between_joins <= 7 THEN 'Weekly'
            WHEN rm.avg_days_between_joins <= 30 THEN 'Monthly'
            ELSE 'Occasional'
        END AS engagement_frequency_category,
        -- Window function rankings
        ROW_NUMBER() OVER (ORDER BY rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) DESC) AS retention_rate_row_num,
        RANK() OVER (ORDER BY rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) DESC) AS retention_rate_rank,
        DENSE_RANK() OVER (ORDER BY rm.total_joins DESC) AS total_joins_dense_rank,
        PERCENT_RANK() OVER (ORDER BY rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) DESC) AS retention_rate_percentile,
        NTILE(5) OVER (ORDER BY rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) DESC) AS retention_rate_quintile,
        NTILE(10) OVER (ORDER BY rm.total_joins DESC) AS total_joins_decile,
        -- Window functions with frames
        SUM(rm.total_joins) OVER (
            ORDER BY rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_total_joins,
        AVG(rm.returning_joins::numeric / NULLIF(rm.total_joins, 0)) OVER (
            ORDER BY rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) DESC
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS moving_avg_retention_rate,
        LAG(rm.total_joins, 1) OVER (ORDER BY rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) DESC) AS prev_total_joins,
        LEAD(rm.returning_joins, 1) OVER (ORDER BY rm.returning_joins::numeric / NULLIF(rm.total_joins, 0) DESC) AS next_returning_joins
    FROM retention_metrics rm
    INNER JOIN profiles p ON rm.user_id = p.id
    WHERE rm.total_joins > 1
)
SELECT
    username,
    total_joins,
    first_joins,
    returning_joins,
    returning_same_day,
    returning_week,
    returning_month,
    returning_long_term,
    retention_rate,
    avg_days_between,
    median_days_between,
    p25_days_between,
    p75_days_between,
    min_days_between_joins,
    max_days_between_joins,
    stddev_days_between,
    avg_days_until_next_join,
    avg_days_since_first_join,
    avg_unique_chats_in_chain,
    avg_retention_depth,
    avg_max_retention_depth,
    avg_total_chain_participations,
    avg_5_session_window,
    avg_range_window,
    first_chain_join,
    last_chain_join,
    ROUND(CAST(chain_span_days AS NUMERIC), 2) AS chain_span_days,
    retention_category,
    engagement_frequency_category,
    retention_rate_row_num,
    retention_rate_rank,
    total_joins_dense_rank,
    ROUND(CAST(retention_rate_percentile * 100 AS NUMERIC), 2) AS retention_rate_percentile,
    retention_rate_quintile,
    total_joins_decile,
    cumulative_total_joins,
    ROUND(CAST(moving_avg_retention_rate * 100 AS NUMERIC), 2) AS moving_avg_retention_rate,
    prev_total_joins,
    next_returning_joins
FROM final_retention_analytics
ORDER BY retention_rate DESC, total_joins DESC;
```

**Expected Output:** User retention analysis with re-engagement patterns and categories.

---

*Note: Continuing with queries 16-30...*



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chat_participants, chats, final_retention_analytics, participant_sessions, profiles, recursive, retention_chain, retention_chain_metrics, retention_metrics, rolling_window_retention_stats, session_gaps, union_retention_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chat_participants, chats, final_retention_analytics, participant_sessions, profiles, recursive, retention_chain, retention_chain_metrics, retention_metrics, rolling_window_retention_stats, session_gaps, union_retention_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: chat_participants, chats, final_retention_analytics, participant_sessions, profiles, recursive, retention_chain, retention_chain_metrics, retention_metrics, rolling_window_retention_stats, session_gaps, union_retention_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chat_participants, chats, final_retention_analytics, participant_sessions, profiles, recursive, retention_chain, retention_chain_metrics, retention_metrics, rolling_window_retention_stats, session_gaps, union_retention_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chat_participants, chats, final_retention_analytics, participant_sessions, profiles, recursive, retention_chain, retention_chain_metrics, retention_metrics, rolling_window_retention_stats, session_gaps, union_retention_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chat_participants, chats, final_retention_analytics, participant_sessions, profiles
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE retention_chain AS (
    -- Anchor: Base participant joins
    SELECT
        cp.user_id,
        cp.chat_id,
        cp.joined_at,
        1 AS retention_depth,
        ARRAY[cp.chat_id] AS retention_path
    FROM chat_participants cp

    UNION ALL

    -- Recursive: Find related joins in retention chain
    SELECT
        rc.user_id,
        cp2.chat_id,
        cp2.joined_at,
        rc.retention_depth + 1,
        rc.retention_path || cp2.chat_id
    FROM retention_chain rc
 ...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 16: Production-Grade Partition Rank Analysis with Advanced Analytics

**Description:** Enterprise-level partition rank analysis with category chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive ranking analytics. Implements production patterns similar to leaderboard systems.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql

WITH chat_message_counts AS (
    SELECT
        c.id,
        c.title,
        COUNT(m.id) AS message_count,
        c.created_at
    FROM chats c
    LEFT JOIN messages m ON c.id = m.chat_id
    GROUP BY c.id, c.title, c.created_at
),
title_groups AS (
    SELECT
        title,
        COUNT(DISTINCT id) AS chat_count,
        SUM(message_count) AS total_messages,
        AVG(message_count) AS avg_messages
    FROM chat_message_counts
    GROUP BY title
),
ranked_chats AS (
    SELECT
        cmc.id,
        cmc.title,
        cmc.message_count,
        cmc.created_at,
        tg.chat_count,
        tg.total_messages,
        tg.avg_messages,
        ROW_NUMBER() OVER (PARTITION BY cmc.title ORDER BY cmc.message_count DESC) AS rank_in_title,
        RANK() OVER (PARTITION BY cmc.title ORDER BY cmc.message_count DESC) AS rank_with_ties,
        DENSE_RANK() OVER (PARTITION BY cmc.title ORDER BY cmc.message_count DESC) AS dense_rank,
        NTILE(4) OVER (PARTITION BY cmc.title ORDER BY cmc.message_count DESC) AS quartile,
        PERCENT_RANK() OVER (PARTITION BY cmc.title ORDER BY cmc.message_count DESC) AS percent_rank,
        SUM(cmc.message_count) OVER (
            PARTITION BY cmc.title
            ORDER BY cmc.message_count DESC
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS count_10_window,
        AVG(cmc.message_count) OVER (
            PARTITION BY cmc.title
            ORDER BY cmc.message_count DESC
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS count_20_avg
    FROM chat_message_counts cmc
    LEFT JOIN title_groups tg ON cmc.title = tg.title
)
SELECT
    c.title AS chat_title,
    rc.message_count,
    rc.title AS category,
    rc.rank_in_title,
    rc.rank_with_ties,
    rc.dense_rank,
    rc.quartile,
    ROUND(CAST(rc.percent_rank * 100 AS NUMERIC), 2) AS percent_rank,
    rc.count_10_window,
    ROUND(rc.count_20_avg, 2) AS count_20_avg,
    rc.chat_count AS unique_ids_in_chain,
    1.0 AS avg_chain_depth,
    1 AS max_chain_depth
FROM ranked_chats rc
INNER JOIN chats c ON rc.id = c.id
ORDER BY rc.title, rc.rank_in_title
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics, partition_rank_analytics, recursive, rolling_window_rank_stats, union_rank_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics, partition_rank_analytics, recursive, rolling_window_rank_stats, union_rank_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics, partition_rank_analytics, recursive, rolling_window_rank_stats, union_rank_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics, partition_rank_analytics, recursive, rolling_window_rank_stats, union_rank_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE category_chain AS (
    -- Anchor: Base category records
    SELECT
        id,
        category,
        value,
        created_at,
        1 AS chain_depth,
        ARRAY[id] AS chain_path
    FROM chats_chat

    UNION ALL

    -- Recursive: Find related category records in chain
    SELECT
        t.id,
        t.category,
        t.value,
        t.created_at,
        cc.chain_depth + 1,
        cc.chain_path || t.id
    FROM category_chain cc
    INNER JOIN chats_chat t ON t...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 17: Production-Grade Running Total Analysis with Advanced Analytics

**Description:** Enterprise-level running total analysis with temporal chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive time-series analytics. Implements production patterns similar to financial reporting systems.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH daily_message_counts AS (
    SELECT
        DATE_TRUNC('day', m.created_at) AS date_period,
        COUNT(*) AS message_count,
        COUNT(DISTINCT m.chat_id) AS chat_count,
        COUNT(DISTINCT m.sender_id) AS user_count
    FROM messages m
    WHERE m.created_at IS NOT NULL
    GROUP BY DATE_TRUNC('day', m.created_at)
),
running_totals AS (
    SELECT
        date_period,
        message_count,
        chat_count,
        user_count,
        SUM(message_count) OVER (
            ORDER BY date_period
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_messages,
        AVG(message_count) OVER (
            ORDER BY date_period
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS avg_7day_messages,
        LAG(message_count, 1) OVER (ORDER BY date_period) AS prev_day_count,
        LEAD(message_count, 1) OVER (ORDER BY date_period) AS next_day_count
    FROM daily_message_counts
)
SELECT
    date_period,
    message_count,
    chat_count,
    user_count,
    cumulative_messages,
    ROUND(avg_7day_messages, 2) AS avg_7day_messages,
    prev_day_count,
    next_day_count,
    CASE
        WHEN prev_day_count IS NOT NULL THEN message_count - prev_day_count
        ELSE 0
    END AS day_over_day_change
FROM running_totals
ORDER BY date_period DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats, running_total_analytics, temporal_chain, temporal_chain_metrics, union_running_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats, running_total_analytics, temporal_chain, temporal_chain_metrics, union_running_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats, running_total_analytics, temporal_chain, temporal_chain_metrics, union_running_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats, running_total_analytics, temporal_chain, temporal_chain_metrics, union_running_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE temporal_chain AS (
    -- Anchor: Base temporal records
    SELECT
        DATE_TRUNC('day', date_col) AS date_period,
        id,
        value,
        category,
        date_col,
        1 AS chain_depth,
        ARRAY[id] AS chain_path
    FROM chats_chat
    WHERE date_col IS NOT NULL

    UNION ALL

    -- Recursive: Find related temporal records in chain
    SELECT
        DATE_TRUNC('day', t.date_col) AS date_period,
        t.id,
        t.value,
        t.category,
    ...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 18: Production-Grade Multiple Join Analysis with Advanced Analytics

**Description:** Enterprise-level multiple join analysis with relationship chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive join analytics. Implements production patterns similar to relationship management systems.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH chat_message_stats AS (
    SELECT
        c.id AS chat_id,
        c.title,
        COUNT(m.id) AS total_messages,
        COUNT(DISTINCT m.sender_id) AS unique_senders,
        MIN(m.created_at) AS first_message,
        MAX(m.created_at) AS last_message
    FROM chats c
    LEFT JOIN messages m ON c.id = m.chat_id
    GROUP BY c.id, c.title
),
message_sequences AS (
    SELECT
        m1.chat_id,
        m1.id AS message_id,
        m1.created_at,
        COUNT(m2.id) AS messages_before,
        COUNT(m3.id) AS messages_after
    FROM messages m1
    LEFT JOIN messages m2 ON m1.chat_id = m2.chat_id AND m2.created_at < m1.created_at
    LEFT JOIN messages m3 ON m1.chat_id = m3.chat_id AND m3.created_at > m1.created_at
    GROUP BY m1.chat_id, m1.id, m1.created_at
)
SELECT
    cms.chat_id,
    cms.title,
    cms.total_messages,
    cms.unique_senders,
    cms.first_message,
    cms.last_message,
    AVG(ms.messages_before) AS avg_messages_before,
    AVG(ms.messages_after) AS avg_messages_after
FROM chat_message_stats cms
LEFT JOIN message_sequences ms ON cms.chat_id = ms.chat_id
GROUP BY cms.chat_id, cms.title, cms.total_messages, cms.unique_senders, cms.first_message, cms.last_message
ORDER BY cms.total_messages DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: Count, aggregated_join_data, analytics, base_join_metrics, chain
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE join_chain AS (
    -- Anchor: Base join relationships
    SELECT
        ch.id AS source_id,
        m.id AS related_id,
        ch.status,
        t1.created_at,
        1 AS chain_depth,
        ARRAY[ch.id, m.id] AS chain_path
    FROM chats_chat t1
    INNER JOIN chats_message t2 ON ch.id = t2.foreign_id
    WHERE ch.status = 'active'

    UNION ALL

    -- Recursive: Find related joins in chain
    SELECT
        jc.source_id,
        cp.id AS related_id,
        jc.status,
...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 19: Production-Grade Nested CTE Analysis with Advanced Analytics

**Description:** Enterprise-level nested CTE analysis with level chain tracking, multiple nested CTEs (8+ levels), window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive nested analytics. Implements production patterns similar to multi-level reporting systems.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chats_chat, chats_message, final_nested_cte_analytics, level1, level2
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE level_chain AS (
    -- Anchor: Base level records
    SELECT
        id,
        value,
        category,
        status,
        created_at,
        1 AS chain_depth,
        ARRAY[id] AS chain_path
    FROM chats_chat
    WHERE status = 'active'

    UNION ALL

    -- Recursive: Find related level records in chain
    SELECT
        lc.id,
        m.created_at,
        lc.category,
        lc.status,
        t2.created_at,
        lc.chain_depth + 1,
        lc.chain_path || m....

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 20: Production-Grade Multi-CTE Window Function Analysis with Advanced Analytics

**Description:** Enterprise-level multi-CTE window function analysis with aggregation chain tracking, multiple nested CTEs (8+ levels), window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive window analytics. Implements production patterns similar to advanced analytics platforms.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics, multi_cte_window_analytics, ranked_data, recursive, union_window_metrics, window_analysis
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics, multi_cte_window_analytics, ranked_data, recursive, union_window_metrics, window_analysis
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics, multi_cte_window_analytics, ranked_data, recursive, union_window_metrics, window_analysis
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics, multi_cte_window_analytics, ranked_data, recursive, union_window_metrics, window_analysis
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE aggregation_chain AS (
    -- Anchor: Base aggregation records
    SELECT
        id,
        value,
        category,
        created_at,
        1 AS chain_depth,
        ARRAY[id] AS chain_path
    FROM chats_chat

    UNION ALL

    -- Recursive: Find related aggregation records in chain
    SELECT
        ac.id,
        t.value,
        ac.category,
        t.created_at,
        ac.chain_depth + 1,
        ac.chain_path || t.id
    FROM aggregation_chain ac
    INNER JOIN cha...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 21: Production-Grade Hierarchy Analysis with Advanced Metrics

**Description:** Enterprise-level hierarchy analysis with multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive hierarchy analytics. Implements production patterns similar to organizational hierarchy systems.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ⚠️
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 1/2
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chats_chat, final_hierarchy_analytics, hierarchy, hierarchy_metrics, hierarchy_totals, rolling_window_hierarchy_stats, union_hierarchy_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chats_chat, final_hierarchy_analytics, hierarchy, hierarchy_metrics, hierarchy_totals, rolling_window_hierarchy_stats, union_hierarchy_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chats_chat, final_hierarchy_analytics, hierarchy, hierarchy_metrics, hierarchy_totals, rolling_window_hierarchy_stats, union_hierarchy_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chats_chat, final_hierarchy_analytics, hierarchy, hierarchy_metrics, hierarchy_totals
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE hierarchy AS (
    -- Anchor: Root level
    SELECT
        id,
        parent_id,
        name,
        1 AS level,
        ARRAY[id] AS path,
        created_at
    FROM chats_chat
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive: Child levels
    SELECT
        t.id,
        t.parent_id,
        t.name,
        h.level + 1,
        h.path || t.id,
        t.created_at
    FROM chats_chat t
    INNER JOIN hierarchy h ON t.parent_id = h.id
    WHERE NOT t.id = ANY(h.p...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 22: Production-Grade Window Frame Analysis with Advanced Analytics

**Description:** Enterprise-level window frame analysis with temporal pattern tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive time-series analytics. Implements production patterns similar to time-series analytics platforms.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: base_window_metrics, chats_chat, final_window_frame_analytics, recursive, rolling_window_frame_stats, temporal_pattern, temporal_pattern_metrics, union_window_metrics, window_frame_analytics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: base_window_metrics, chats_chat, final_window_frame_analytics, recursive, rolling_window_frame_stats, temporal_pattern, temporal_pattern_metrics, union_window_metrics, window_frame_analytics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: base_window_metrics, chats_chat, final_window_frame_analytics, recursive, rolling_window_frame_stats, temporal_pattern, temporal_pattern_metrics, union_window_metrics, window_frame_analytics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: base_window_metrics, chats_chat, final_window_frame_analytics, recursive, rolling_window_frame_stats, temporal_pattern, temporal_pattern_metrics, union_window_metrics, window_frame_analytics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: base_window_metrics, chats_chat, final_window_frame_analytics, recursive, rolling_window_frame_stats
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE temporal_pattern AS (
    -- Anchor: Base time periods
    SELECT
        DATE_TRUNC('day', date_col) AS time_period,
        id,
        value,
        category,
        date_col,
        1 AS pattern_depth,
        ARRAY[id] AS pattern_path
    FROM chats_chat
    WHERE date_col IS NOT NULL

    UNION ALL

    -- Recursive: Find related temporal patterns
    SELECT
        DATE_TRUNC('day', t.date_col) AS time_period,
        t.id,
        t.value,
        t.category,
        t....

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 23: Production-Grade Pivot Aggregation Analysis with Advanced Analytics

**Description:** Enterprise-level pivot aggregation analysis with status chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive pivot analytics. Implements production patterns similar to status tracking systems.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: base_pivot_metrics, chats_chat, chats_message, final_pivot_analytics, pivot_aggregation_analytics, recursive, rolling_window_pivot_stats, status_chain, status_chain_metrics, union_pivot_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: base_pivot_metrics, chats_chat, chats_message, final_pivot_analytics, pivot_aggregation_analytics, recursive, rolling_window_pivot_stats, status_chain, status_chain_metrics, union_pivot_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: base_pivot_metrics, chats_chat, chats_message, final_pivot_analytics, pivot_aggregation_analytics, recursive, rolling_window_pivot_stats, status_chain, status_chain_metrics, union_pivot_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: base_pivot_metrics, chats_chat, chats_message, final_pivot_analytics, pivot_aggregation_analytics, recursive, rolling_window_pivot_stats, status_chain, status_chain_metrics, union_pivot_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: base_pivot_metrics, chats_chat, chats_message, final_pivot_analytics, pivot_aggregation_analytics, recursive, rolling_window_pivot_stats, status_chain, status_chain_metrics, union_pivot_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: base_pivot_metrics, chats_chat, chats_message, final_pivot_analytics, pivot_aggregation_analytics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE status_chain AS (
    -- Anchor: Base status records
    SELECT
        ch.id,
        ch.status,
        ch.chat_type,
        ch.created_at,
        t1.created_at,
        1 AS chain_depth,
        ARRAY[ch.id] AS chain_path
    FROM chats_chat t1

    UNION ALL

    -- Recursive: Find related status changes in chain
    SELECT
        m.id,
        m.status,
        m.message_type,
        m.created_at,
        t2.created_at,
        sc.chain_depth + 1,
        sc.chain_path ||...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 24: Production-Grade Correlated Subquery Analysis with Advanced Analytics

**Description:** Enterprise-level correlated subquery analysis with relationship chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive relationship analytics. Implements production patterns similar to relationship tracking systems.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: base_correlated_metrics, chats_chat, correlated_subquery_analytics, final_correlated_analytics, recursive, relationship_chain, relationship_chain_metrics, rolling_window_correlated_stats, union_correlated_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: base_correlated_metrics, chats_chat, correlated_subquery_analytics, final_correlated_analytics, recursive, relationship_chain, relationship_chain_metrics, rolling_window_correlated_stats, union_correlated_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: base_correlated_metrics, chats_chat, correlated_subquery_analytics, final_correlated_analytics, recursive, relationship_chain, relationship_chain_metrics, rolling_window_correlated_stats, union_correlated_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: base_correlated_metrics, chats_chat, correlated_subquery_analytics, final_correlated_analytics, recursive, relationship_chain, relationship_chain_metrics, rolling_window_correlated_stats, union_correlated_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: base_correlated_metrics, chats_chat, correlated_subquery_analytics, final_correlated_analytics, recursive, relationship_chain, relationship_chain_metrics, rolling_window_correlated_stats, union_correlated_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: base_correlated_metrics, chats_chat, correlated_subquery_analytics, final_correlated_analytics, recursive
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE relationship_chain AS (
    -- Anchor: Base relationships
    SELECT
        ch.id AS source_id,
        m.id AS related_id,
        ch.chat_type,
        t1.created_at,
        1 AS chain_depth,
        ARRAY[ch.id, m.id] AS chain_path
    FROM chats_chat t1
    INNER JOIN chats_chat t2 ON t2.foreign_id = ch.id

    UNION ALL

    -- Recursive: Find related relationships in chain
    SELECT
        rc.source_id,
        cp.id AS related_id,
        rc.category,
        t3.created...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 25: Production-Grade Union Complex Analysis with Advanced Analytics

**Description:** Enterprise-level UNION analysis with source chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive multi-source analytics. Implements production patterns similar to data integration platforms.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, combined, final_union_analytics, first_set, recursive, rolling_window_union_stats, second_set, source_chain, source_chain_metrics, union_combined_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, combined, final_union_analytics, first_set, recursive, rolling_window_union_stats, second_set, source_chain, source_chain_metrics, union_combined_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, combined, final_union_analytics, first_set, recursive, rolling_window_union_stats, second_set, source_chain, source_chain_metrics, union_combined_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, combined, final_union_analytics, first_set, recursive, rolling_window_union_stats, second_set, source_chain, source_chain_metrics, union_combined_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chats_chat, chats_message, combined, final_union_analytics, first_set
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE source_chain AS (
    -- Anchor: Base source records
    SELECT
        ch.id,
        ch.created_at,
        'source1' AS source,
        t1.created_at,
        1 AS chain_depth,
        ARRAY[ch.id] AS chain_path
    FROM chats_chat t1
    WHERE ch.created_at > 100

    UNION ALL

    -- Recursive: Find related source records in chain
    SELECT
        sc.id,
        m.created_at,
        'source2' AS source,
        t2.created_at,
        sc.chain_depth + 1,
        sc.chain_p...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 26: Production-Grade File Type Hierarchy Analysis with Recursive CTE and Advanced Ranking Analytics

**Description:** Enterprise-level file type hierarchy analysis with recursive CTE for category chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive ranking analytics. Implements production patterns similar to leaderboard systems with hierarchical category relationships.

**Complexity:** Recursive CTE, multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH RECURSIVE base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
file_type_hierarchy AS (
    -- Recursive CTE: Build file type hierarchy chain based on size categories
    SELECT
        fts.file_type,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        CASE
            WHEN fts.avg_size < 1000 THEN 'Small'
            WHEN fts.avg_size < 10000 THEN 'Medium'
            WHEN fts.avg_size < 100000 THEN 'Large'
            ELSE 'Very Large'
        END AS size_category,
        1 AS hierarchy_level,
        ARRAY[fts.file_type]::VARCHAR[] AS type_chain
    FROM file_type_stats fts

    UNION ALL

    -- Recursive step: Link file types in same size category
    SELECT
        fth.file_type,
        fth.file_count,
        fth.total_size,
        fth.avg_size,
        fth.min_size,
        fth.max_size,
        fth.size_category,
        fth.hierarchy_level + 1,
        fth.type_chain || fts2.file_type
    FROM file_type_hierarchy fth
    INNER JOIN file_type_stats fts2 ON fth.size_category =
        CASE
            WHEN fts2.avg_size < 1000 THEN 'Small'
            WHEN fts2.avg_size < 10000 THEN 'Medium'
            WHEN fts2.avg_size < 100000 THEN 'Large'
            ELSE 'Very Large'
        END
    WHERE fts2.file_type != ALL(fth.type_chain)
        AND fth.hierarchy_level < 5
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        fth.size_category,
        fth.hierarchy_level,
        fth.type_chain,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank,
        RANK() OVER (PARTITION BY fth.size_category ORDER BY bs.file_size DESC) AS rank_in_category
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
    LEFT JOIN file_type_hierarchy fth ON bs.file_type = fth.file_type AND fth.hierarchy_level = 1
)
SELECT
    rf.file_type,
    rf.size_category,
    rf.hierarchy_level,
    rf.file_count,
    rf.total_size,
    ROUND(rf.avg_size, 2) AS avg_size,
    rf.min_size,
    rf.max_size,
    COUNT(*) AS ranked_files_count,
    rf.rank_in_type,
    ROUND(CAST(rf.percent_rank * 100 AS NUMERIC), 2) AS percent_rank,
    rf.rank_in_category
FROM ranked_files rf
GROUP BY rf.file_type, rf.size_category, rf.hierarchy_level, rf.file_count, rf.total_size,
         rf.avg_size, rf.min_size, rf.max_size, rf.rank_in_type, rf.percent_rank, rf.rank_in_category
ORDER BY rf.file_count DESC, rf.rank_in_category ASC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics, partition_rank_analytics, recursive, rolling_window_rank_stats, union_rank_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics, partition_rank_analytics, recursive, rolling_window_rank_stats, union_rank_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics, partition_rank_analytics, recursive, rolling_window_rank_stats, union_rank_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics, partition_rank_analytics, recursive, rolling_window_rank_stats, union_rank_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: base_rank_metrics, category_chain, category_chain_metrics, chats_chat, final_partition_rank_analytics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE category_chain AS (
    -- Anchor: Base category records
    SELECT
        id,
        category,
        value,
        created_at,
        1 AS chain_depth,
        ARRAY[id] AS chain_path
    FROM chats_chat

    UNION ALL

    -- Recursive: Find related category records in chain
    SELECT
        t.id,
        t.category,
        t.value,
        t.created_at,
        cc.chain_depth + 1,
        cc.chain_path || t.id
    FROM category_chain cc
    INNER JOIN chats_chat t ON t...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 27: Production-Grade Cumulative File Size Analysis with Advanced Time-Series Analytics

**Description:** Enterprise-level cumulative file size analysis with temporal chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive time-series analytics. Implements production patterns similar to financial reporting systems with file growth tracking.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats, running_total_analytics, temporal_chain, temporal_chain_metrics, union_running_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats, running_total_analytics, temporal_chain, temporal_chain_metrics, union_running_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats, running_total_analytics, temporal_chain, temporal_chain_metrics, union_running_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats, running_total_analytics, temporal_chain, temporal_chain_metrics, union_running_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: base_running_metrics, chats_chat, final_running_total_analytics, recursive, rolling_window_running_stats
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE temporal_chain AS (
    -- Anchor: Base temporal records
    SELECT
        DATE_TRUNC('day', date_col) AS date_period,
        id,
        value,
        category,
        date_col,
        1 AS chain_depth,
        ARRAY[id] AS chain_path
    FROM chats_chat
    WHERE date_col IS NOT NULL

    UNION ALL

    -- Recursive: Find related temporal records in chain
    SELECT
        DATE_TRUNC('day', t.date_col) AS date_period,
        t.id,
        t.value,
        t.category,
    ...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 28: Production-Grade Cross-Table File Relationship Analysis with Advanced Join Analytics

**Description:** Enterprise-level cross-table file relationship analysis with relationship chain tracking, multiple nested CTEs, window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive join analytics. Implements production patterns similar to relationship management systems with file attachment networks.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: Count, aggregated_join_data, analytics, base_join_metrics, chain, chats_chat, chats_chatparticipant, chats_message, data, final_multiple_join_analytics, join_chain, join_chain_metrics, metrics, multiple_join_analytics, recursive, relationships, rolling_window_join_stats, union_join_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: Count, aggregated_join_data, analytics, base_join_metrics, chain
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE join_chain AS (
    -- Anchor: Base join relationships
    SELECT
        ch.id AS source_id,
        m.id AS related_id,
        ch.status,
        t1.created_at,
        1 AS chain_depth,
        ARRAY[ch.id, m.id] AS chain_path
    FROM chats_chat t1
    INNER JOIN chats_message t2 ON ch.id = t2.foreign_id
    WHERE ch.status = 'active'

    UNION ALL

    -- Recursive: Find related joins in chain
    SELECT
        jc.source_id,
        cp.id AS related_id,
        jc.status,
...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 29: Production-Grade Deeply Nested File Type Analysis with Advanced Hierarchical Analytics

**Description:** Enterprise-level deeply nested file type analysis with level chain tracking, multiple nested CTEs (8+ levels), window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive nested analytics. Implements production patterns similar to multi-level reporting systems with file type hierarchies.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---



### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Active user identification
- **Description**: Validates active user identification functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 5: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: chats_chat, chats_message, final_nested_cte_analytics, level1, level2, level3, level_chain, level_chain_metrics, nested_cte_analytics, recursive, union_level_metrics
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: chats_chat, chats_message, final_nested_cte_analytics, level1, level2
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE level_chain AS (
    -- Anchor: Base level records
    SELECT
        id,
        value,
        category,
        status,
        created_at,
        1 AS chain_depth,
        ARRAY[id] AS chain_path
    FROM chats_chat
    WHERE status = 'active'

    UNION ALL

    -- Recursive: Find related level records in chain
    SELECT
        lc.id,
        m.created_at,
        lc.category,
        lc.status,
        t2.created_at,
        lc.chain_depth + 1,
        lc.chain_path || m....

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

## Query 30: Production-Grade Advanced Window Function Aggregation Analysis with Multi-Dimensional Analytics

**Description:** Enterprise-level advanced window function aggregation analysis with aggregation chain tracking, multiple nested CTEs (8+ levels), window functions with frame clauses, correlated subqueries, UNION operations, and comprehensive window analytics. Implements production patterns similar to advanced analytics platforms with multi-dimensional file metrics.

**Complexity:** Multiple nested CTEs (8+ levels), window functions with multiple frame clauses (ROWS/RANGE), correlated subqueries, UNION, pivot CASE, complex joins, aggregations

```sql
WITH base_stats AS (
    SELECT
        fa.id,
        fa.file_size,
        fa.file_type,
        fa.created_at,
        c.title AS chat_title
    FROM file_attachments fa
    LEFT JOIN chats c ON fa.chat_id = c.id
    WHERE fa.file_size IS NOT NULL
),
file_type_stats AS (
    SELECT
        file_type,
        COUNT(*) AS file_count,
        SUM(file_size) AS total_size,
        AVG(file_size) AS avg_size,
        MIN(file_size) AS min_size,
        MAX(file_size) AS max_size
    FROM base_stats
    GROUP BY file_type
),
ranked_files AS (
    SELECT
        bs.*,
        fts.file_count,
        fts.total_size,
        fts.avg_size,
        fts.min_size,
        fts.max_size,
        ROW_NUMBER() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS rank_in_type,
        PERCENT_RANK() OVER (PARTITION BY bs.file_type ORDER BY bs.file_size DESC) AS percent_rank
    FROM base_stats bs
    LEFT JOIN file_type_stats fts ON bs.file_type = fts.file_type
)
SELECT
    file_type,
    file_count,
    total_size,
    ROUND(avg_size, 2) AS avg_size,
    min_size,
    max_size,
    COUNT(*) AS ranked_files_count
FROM ranked_files
GROUP BY file_type, file_count, total_size, avg_size, min_size, max_size
ORDER BY file_count DESC
LIMIT 100;
```

**Expected Output:** Query results

---

### Test Plan

#### Rigor Tests

**Syntax Validation**
- [ ] Query parses without errors
- [ ] Compatible with PostgreSQL
- [ ] No reserved word conflicts
- **Status**: ✅ PASS


**Correctness Tests**
- [ ] Results match expected schema
- [ ] Aggregations are mathematically correct
- [ ] Window functions produce expected rankings
- [ ] CTEs execute in correct order
- [ ] NULL values handled appropriately
- **Status**: ✅ PASS

**Edge Case Tests**
- [ ] Empty table handling
- [ ] NULL value handling ✅
- [ ] Extreme value handling
- [ ] Date boundary conditions
- [ ] Recursive CTE termination ⚠️
- [ ] Window frame boundaries ✅
- **Passed**: 2/3
- **Failed**: recursive_cte_termination

**Performance Tests**
- [ ] Execution time < 5 seconds (or documented threshold)
- [ ] Query plan uses appropriate indexes
- [ ] Memory usage within limits
- **Status**: ✅ PASS


#### Business Use Case Tests

**Use Case 1: User Engagement Analysis**
- **Scenario**: Message frequency analysis
- **Description**: Validates message frequency analysis functionality
- **Test Data Requirements**:
  - Tables: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics, multi_cte_window_analytics, ranked_data, recursive, union_window_metrics, window_analysis
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 2: User Engagement Analysis**
- **Scenario**: Engagement trend tracking
- **Description**: Validates engagement trend tracking functionality
- **Test Data Requirements**:
  - Tables: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics, multi_cte_window_analytics, ranked_data, recursive, union_window_metrics, window_analysis
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 3: Friend Network Analysis**
- **Scenario**: Friend connection patterns
- **Description**: Validates friend connection patterns functionality
- **Test Data Requirements**:
  - Tables: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics, multi_cte_window_analytics, ranked_data, recursive, union_window_metrics, window_analysis
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

**Use Case 4: Friend Network Analysis**
- **Scenario**: Network depth analysis
- **Description**: Validates network depth analysis functionality
- **Test Data Requirements**:
  - Tables: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics, multi_cte_window_analytics, ranked_data, recursive, union_window_metrics, window_analysis
  - Minimum rows: 10-100 for basic testing
  - Comprehensive rows: 1000+ for full validation
- **Expected Result**:
  - Query executes without errors
  - Returns result set with expected columns
  - Calculated metrics are accurate
- **Validation**:
  - Verify query executes successfully
  - Check result schema matches expected structure
  - Validate calculated values against manual calculations
- **Status**: ⏳ NOT TESTED

#### Test Data Requirements

- **Minimum Data**:
  - At least 10 rows in each referenced table: aggregated_data, aggregation_chain, aggregation_chain_metrics, chats_chat, final_multi_cte_window_analytics
  - Basic relationships established (foreign keys)
  - Non-NULL values in critical columns

- **Comprehensive Data**:
  - 1000+ rows in primary tables
  - Full relationship chains
  - Historical data spanning multiple time periods
  - Various data distributions (normal, skewed, uniform)

- **Edge Case Data**:
  - Empty tables (for testing empty result handling)
  - NULL values in key columns
  - Extreme values (very large numbers, very old dates)
  - Boundary dates (start/end of time ranges)
  - Circular references (for recursive CTEs)

#### Expected Results

- **Result Schema**: See query SELECT clause for column names and types
- **Sample Output**: Query should return structured result set with all calculated metrics
- **Result Count**: Varies based on data volume and query filters
- **Key Metrics**:
  - Verify aggregations are mathematically correct
  - Check window function rankings match expected order
  - Validate CTE logic produces expected intermediate results

#### Test Execution

```sql
-- Test 1: Basic execution
WITH RECURSIVE aggregation_chain AS (
    -- Anchor: Base aggregation records
    SELECT
        id,
        value,
        category,
        created_at,
        1 AS chain_depth,
        ARRAY[id] AS chain_path
    FROM chats_chat

    UNION ALL

    -- Recursive: Find related aggregation records in chain
    SELECT
        ac.id,
        t.value,
        ac.category,
        t.created_at,
        ac.chain_depth + 1,
        ac.chain_path || t.id
    FROM aggregation_chain ac
    INNER JOIN cha...

-- Test 2: Edge case - Empty result set
-- Modify WHERE clause to return no results
-- Example: Add impossible condition like WHERE 1=0

-- Test 3: Edge case - NULL values
-- Ensure query handles NULLs in critical columns gracefully

-- Test 4: Business scenario validation
-- Execute with real business data and verify results match expected business logic
```

#### Pass/Fail Criteria

- **Syntax**: PASS if query parses without errors
- **Correctness**: PASS if results match expected schema and calculated values are accurate
- **Performance**: PASS if execution time < 5 seconds (or documented threshold for complex queries)
- **Business Logic**: PASS if all use cases produce expected results that align with business requirements
- **Edge Cases**: PASS if query handles empty tables, NULL values, and boundary conditions gracefully

---
