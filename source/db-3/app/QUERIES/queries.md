# SQL Queries for db-3

## Query 1: Multi-Window Time-Series Analysis with Rolling Aggregates

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for multi-window time-series analysis with rolling aggregates.

**Use Case:** Business analytics for multi-window time-series analysis with rolling aggregates

**Business Value:** Actionable insights from multi-window time-series analysis with rolling aggregates

**Purpose:** Production multi-window time-series analysis with rolling aggregates analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 60
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 2: Segmentation Analysis with Decile Ranking

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for segmentation analysis with decile ranking.

**Use Case:** Business analytics for segmentation analysis with decile ranking

**Business Value:** Actionable insights from segmentation analysis with decile ranking

**Purpose:** Production segmentation analysis with decile ranking analysis

**Complexity:** 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 70
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.status
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 3: Performance Quartile Distribution

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for performance quartile distribution.

**Use Case:** Business analytics for performance quartile distribution

**Business Value:** Actionable insights from performance quartile distribution

**Purpose:** Production performance quartile distribution analysis

**Complexity:** 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 80
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 4: Revenue Distribution by Category

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for revenue distribution by category.

**Use Case:** Business analytics for revenue distribution by category

**Business Value:** Actionable insights from revenue distribution by category

**Purpose:** Production revenue distribution by category analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 90
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.status
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 5: Velocity and Acceleration Metrics

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for velocity and acceleration metrics.

**Use Case:** Business analytics for velocity and acceleration metrics

**Business Value:** Actionable insights from velocity and acceleration metrics

**Purpose:** Production velocity and acceleration metrics analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 100
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 6: Hourly Pattern Detection and Clustering

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for hourly pattern detection and clustering.

**Use Case:** Business analytics for hourly pattern detection and clustering

**Business Value:** Actionable insights from hourly pattern detection and clustering

**Purpose:** Production hourly pattern detection and clustering analysis

**Complexity:** 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 110
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.status
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 7: Gap Analysis with Sequential Difference

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for gap analysis with sequential difference.

**Use Case:** Business analytics for gap analysis with sequential difference

**Business Value:** Actionable insights from gap analysis with sequential difference

**Purpose:** Production gap analysis with sequential difference analysis

**Complexity:** 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 120
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 8: Anomaly Detection Using Z-Score Windows

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for anomaly detection using z-score windows.

**Use Case:** Business analytics for anomaly detection using z-score windows

**Business Value:** Actionable insights from anomaly detection using z-score windows

**Purpose:** Production anomaly detection using z-score windows analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 130
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.status
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 9: Recency-Frequency-Monetary Scoring

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for recency-frequency-monetary scoring.

**Use Case:** Business analytics for recency-frequency-monetary scoring

**Business Value:** Actionable insights from recency-frequency-monetary scoring

**Purpose:** Production recency-frequency-monetary scoring analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 140
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 10: Multi-Period Cohort Retention Analysis

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for multi-period cohort retention analysis.

**Use Case:** Business analytics for multi-period cohort retention analysis

**Business Value:** Actionable insights from multi-period cohort retention analysis

**Purpose:** Production multi-period cohort retention analysis analysis

**Complexity:** 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 150
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.status
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 11: Second-Order Derivative Computation

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for second-order derivative computation.

**Use Case:** Business analytics for second-order derivative computation

**Business Value:** Actionable insights from second-order derivative computation

**Purpose:** Production second-order derivative computation analysis

**Complexity:** 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 160
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 12: Cross-Category Benchmarking with Percentiles

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for cross-category benchmarking with percentiles.

**Use Case:** Business analytics for cross-category benchmarking with percentiles

**Business Value:** Actionable insights from cross-category benchmarking with percentiles

**Purpose:** Production cross-category benchmarking with percentiles analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 170
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.status
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 13: Exponentially Weighted Moving Average

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for exponentially weighted moving average.

**Use Case:** Business analytics for exponentially weighted moving average

**Business Value:** Actionable insights from exponentially weighted moving average

**Purpose:** Production exponentially weighted moving average analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 180
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 14: Peak Period Identification and Efficiency

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for peak period identification and efficiency.

**Use Case:** Business analytics for peak period identification and efficiency

**Business Value:** Actionable insights from peak period identification and efficiency

**Purpose:** Production peak period identification and efficiency analysis

**Complexity:** 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 190
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.status
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 15: Lifetime Value Estimation Model

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for lifetime value estimation model.

**Use Case:** Business analytics for lifetime value estimation model

**Business Value:** Actionable insights from lifetime value estimation model

**Purpose:** Production lifetime value estimation model analysis

**Complexity:** 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 200
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 16: Year-over-Year Growth Rate Analysis

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for year-over-year growth rate analysis.

**Use Case:** Business analytics for year-over-year growth rate analysis

**Business Value:** Actionable insights from year-over-year growth rate analysis

**Purpose:** Production year-over-year growth rate analysis analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 210
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.status
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 17: Heatmap Data Generation by Time Dimensions

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for heatmap data generation by time dimensions.

**Use Case:** Business analytics for heatmap data generation by time dimensions

**Business Value:** Actionable insights from heatmap data generation by time dimensions

**Purpose:** Production heatmap data generation by time dimensions analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 220
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 18: Running Percentile Distribution Computation

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for running percentile distribution computation.

**Use Case:** Business analytics for running percentile distribution computation

**Business Value:** Actionable insights from running percentile distribution computation

**Purpose:** Production running percentile distribution computation analysis

**Complexity:** 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 230
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.status
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 19: Cross-Correlation Pattern Analysis

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for cross-correlation pattern analysis.

**Use Case:** Business analytics for cross-correlation pattern analysis

**Business Value:** Actionable insights from cross-correlation pattern analysis

**Purpose:** Production cross-correlation pattern analysis analysis

**Complexity:** 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 240
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 20: Forensic Analysis of Status Transitions

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for forensic analysis of status transitions.

**Use Case:** Business analytics for forensic analysis of status transitions

**Business Value:** Actionable insights from forensic analysis of status transitions

**Purpose:** Production forensic analysis of status transitions analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 250
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.status
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 21: Multi-Metric Dashboard Aggregation Pipeline

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for multi-metric dashboard aggregation pipeline.

**Use Case:** Business analytics for multi-metric dashboard aggregation pipeline

**Business Value:** Actionable insights from multi-metric dashboard aggregation pipeline

**Purpose:** Production multi-metric dashboard aggregation pipeline analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 260
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 22: Sequential Pattern Mining with Windows

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for sequential pattern mining with windows.

**Use Case:** Business analytics for sequential pattern mining with windows

**Business Value:** Actionable insights from sequential pattern mining with windows

**Purpose:** Production sequential pattern mining with windows analysis

**Complexity:** 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 270
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.status
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 23: Concentration Index Computation

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for concentration index computation.

**Use Case:** Business analytics for concentration index computation

**Business Value:** Actionable insights from concentration index computation

**Purpose:** Production concentration index computation analysis

**Complexity:** 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 280
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 24: Statistical Anomaly Score Assignment

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for statistical anomaly score assignment.

**Use Case:** Business analytics for statistical anomaly score assignment

**Business Value:** Actionable insights from statistical anomaly score assignment

**Purpose:** Production statistical anomaly score assignment analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 290
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.status
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 25: Fiscal Period Comparative Reporting

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for fiscal period comparative reporting.

**Use Case:** Business analytics for fiscal period comparative reporting

**Business Value:** Actionable insights from fiscal period comparative reporting

**Purpose:** Production fiscal period comparative reporting analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 300
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 26: Throughput Optimization Metrics

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for throughput optimization metrics.

**Use Case:** Business analytics for throughput optimization metrics

**Business Value:** Actionable insights from throughput optimization metrics

**Purpose:** Production throughput optimization metrics analysis

**Complexity:** 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 310
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.status
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 27: Cumulative Trend Analysis Pipeline

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for cumulative trend analysis pipeline.

**Use Case:** Business analytics for cumulative trend analysis pipeline

**Business Value:** Actionable insights from cumulative trend analysis pipeline

**Purpose:** Production cumulative trend analysis pipeline analysis

**Complexity:** 4 CTEs, 9 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 320
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 28: Multi-Dimensional Pivot Aggregation

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for multi-dimensional pivot aggregation.

**Use Case:** Business analytics for multi-dimensional pivot aggregation

**Business Value:** Actionable insights from multi-dimensional pivot aggregation

**Purpose:** Production multi-dimensional pivot aggregation analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by month and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 330
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.created_at), c4.status
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 29: Funnel Stage Progression Tracking

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for funnel stage progression tracking.

**Use Case:** Business analytics for funnel stage progression tracking

**Business Value:** Actionable insights from funnel stage progression tracking

**Purpose:** Production funnel stage progression tracking analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by day and seller_id

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.seller_id) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.seller_id ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 340
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.seller_id ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.seller_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.seller_id ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.seller_id ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.created_at) AS period,
    c4.seller_id,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.created_at), c4.seller_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 30: Outlier Detection with IQR Method

**Description:** Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for outlier detection with iqr method.

**Use Case:** Business analytics for outlier detection with iqr method

**Business Value:** Actionable insights from outlier detection with iqr method

**Purpose:** Production outlier detection with iqr method analysis

**Complexity:** 4 CTEs, 8 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics grouped by week and status

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) AS rn,
        DATE_TRUNC('day', created_at) AS day_bucket,
        DATE_TRUNC('week', created_at) AS week_bucket,
        EXTRACT(HOUR FROM created_at) AS hour_val,
        EXTRACT(DOW FROM created_at) AS dow_val
    FROM orders_order
    WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.status) AS daily_partition_count,
        AVG(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at) AS first_val,
        LAST_VALUE(c1.total_amount) OVER (PARTITION BY c1.status ORDER BY c1.created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 350
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS prev_value,
        LEAD(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS next_value,
        c2.total_amount - LAG(c2.total_amount, 1) OVER (PARTITION BY c2.status ORDER BY c2.created_at) AS delta_value,
        AVG(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_avg,
        STDDEV(c2.total_amount) OVER (PARTITION BY c2.status) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.status ORDER BY c2.total_amount) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.total_amount DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.total_amount - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.status ORDER BY c3.total_amount) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.created_at) AS period,
    c4.status,
    COUNT(*) AS record_count,
    AVG(c4.total_amount) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.total_amount) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.total_amount) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.total_amount) AS q3_value,
    STDDEV(c4.total_amount) AS stddev_value,
    MIN(c4.total_amount) AS min_value,
    MAX(c4.total_amount) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.created_at), c4.status
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

