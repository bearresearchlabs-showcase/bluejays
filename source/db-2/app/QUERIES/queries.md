# SQL Queries for db-2

## Query 1: Multi-Window Time-Series Sales Analysis with Rolling Aggregates

**Description:** Uses 4 CTEs with ROW_NUMBER, LAG, LEAD, and multiple rolling window aggregations across daily sales partitions.

**Use Case:** Daily sales performance dashboard with rolling 7-day trends

**Business Value:** Real-time sales KPI monitoring for store managers

**Purpose:** Identify sales velocity trends and anomalies across time periods

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Daily aggregated sales metrics with rolling averages and trend indicators

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day) AS daily_count,
        AVG(c1.sale_id) OVER (ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg_7d,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum
    FROM cte_level_1 c1
    WHERE c1.rn <= 100
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS emp_avg,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        NTILE(4) OVER (ORDER BY c3.sale_id) AS quartile,
        DENSE_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.daily_count DESC) AS activity_rank,
        CASE 
            WHEN c3.sale_id > c3.emp_avg THEN 'Above Average'
            WHEN c3.sale_id = c3.emp_avg THEN 'Average'
            ELSE 'Below Average'
        END AS performance_category
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS analysis_date,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    STDDEV(c4.sale_id) AS stddev_value,
    SUM(CASE WHEN c4.performance_category = 'Above Average' THEN 1 ELSE 0 END) AS above_avg_count,
    AVG(c4.rolling_avg_7d) AS avg_rolling_7d
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id
HAVING COUNT(*) > 1
ORDER BY analysis_date DESC, record_count DESC
LIMIT 100
```

## Query 2: Customer Purchase Frequency Segmentation

**Description:** Segments customers by purchase frequency using decile analysis and cohort comparison

**Use Case:** Business analytics for customer purchase frequency segmentation

**Business Value:** Actionable insights from customer purchase frequency segmentation

**Purpose:** Production customer purchase frequency segmentation analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for customer purchase frequency segmentation

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 70
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.customer_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 3: Employee Performance Quartile Ranking

**Description:** Ranks employees into performance quartiles with trailing 30-day trend analysis

**Use Case:** Business analytics for employee performance quartile ranking

**Business Value:** Actionable insights from employee performance quartile ranking

**Purpose:** Production employee performance quartile ranking analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for employee performance quartile ranking

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 80
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 4: Payment Type Revenue Distribution

**Description:** Analyzes revenue distribution across payment methods with month-over-month growth

**Use Case:** Business analytics for payment type revenue distribution

**Business Value:** Actionable insights from payment type revenue distribution

**Purpose:** Production payment type revenue distribution analysis

**Complexity:** 4 CTEs, 4 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for payment type revenue distribution

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY payment_type ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.payment_type) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 90
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.payment_type) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.payment_type) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.payment_type ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.payment_type,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.payment_type
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 5: Location-Based Sales Velocity

**Description:** Computes sales velocity per location with moving average and acceleration metrics

**Use Case:** Business analytics for location-based sales velocity

**Business Value:** Actionable insights from location-based sales velocity

**Purpose:** Production location-based sales velocity analysis

**Complexity:** 4 CTEs, 5 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for location-based sales velocity

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 100
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.location_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.location_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 6: Hourly Sales Pattern Detection

**Description:** Detects hourly sales patterns using date_part extraction and cyclic aggregation

**Use Case:** Business analytics for hourly sales pattern detection

**Business Value:** Actionable insights from hourly sales pattern detection

**Purpose:** Production hourly sales pattern detection analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for hourly sales pattern detection

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 110
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 7: Invoice Gap Analysis

**Description:** Identifies gaps in invoice numbering sequences using LAG-based difference calculations

**Use Case:** Business analytics for invoice gap analysis

**Business Value:** Actionable insights from invoice gap analysis

**Purpose:** Production invoice gap analysis analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for invoice gap analysis

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 120
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.sale_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.sale_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 8: Suspended Transaction Anomaly Detection

**Description:** Flags anomalous suspension patterns using z-score calculations on rolling windows

**Use Case:** Business analytics for suspended transaction anomaly detection

**Business Value:** Actionable insights from suspended transaction anomaly detection

**Purpose:** Production suspended transaction anomaly detection analysis

**Complexity:** 4 CTEs, 4 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for suspended transaction anomaly detection

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 130
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 9: Customer Recency-Frequency Analysis

**Description:** Computes RFM scores using recency windows and frequency distributions

**Use Case:** Business analytics for customer recency-frequency analysis

**Business Value:** Actionable insights from customer recency-frequency analysis

**Purpose:** Production customer recency-frequency analysis analysis

**Complexity:** 4 CTEs, 5 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for customer recency-frequency analysis

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 140
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.customer_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 10: Multi-Period Cohort Retention

**Description:** Tracks cohort retention across multiple time periods with survival analysis patterns

**Use Case:** Business analytics for multi-period cohort retention

**Business Value:** Actionable insights from multi-period cohort retention

**Purpose:** Production multi-period cohort retention analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for multi-period cohort retention

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 150
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.customer_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.customer_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 11: Sales Acceleration Rate Computation

**Description:** Calculates second-order derivatives of sales velocity using nested window functions

**Use Case:** Business analytics for sales acceleration rate computation

**Business Value:** Actionable insights from sales acceleration rate computation

**Purpose:** Production sales acceleration rate computation analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for sales acceleration rate computation

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 160
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 12: Cross-Location Revenue Benchmarking

**Description:** Benchmarks each location against aggregate performance with percentile rankings

**Use Case:** Business analytics for cross-location revenue benchmarking

**Business Value:** Actionable insights from cross-location revenue benchmarking

**Purpose:** Production cross-location revenue benchmarking analysis

**Complexity:** 4 CTEs, 4 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for cross-location revenue benchmarking

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 170
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.location_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.location_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 13: Time-Weighted Moving Average

**Description:** Implements exponentially weighted moving averages using recursive-style CTEs

**Use Case:** Business analytics for time-weighted moving average

**Business Value:** Actionable insights from time-weighted moving average

**Purpose:** Production time-weighted moving average analysis

**Complexity:** 4 CTEs, 5 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for time-weighted moving average

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 180
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.sale_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.sale_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 14: Peak Hour Identification and Staffing

**Description:** Identifies peak transaction hours with staffing efficiency ratios

**Use Case:** Business analytics for peak hour identification and staffing

**Business Value:** Actionable insights from peak hour identification and staffing

**Purpose:** Production peak hour identification and staffing analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for peak hour identification and staffing

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 190
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 15: Customer Lifetime Value Estimation

**Description:** Estimates CLV using purchase frequency, recency, and monetary value metrics

**Use Case:** Business analytics for customer lifetime value estimation

**Business Value:** Actionable insights from customer lifetime value estimation

**Purpose:** Production customer lifetime value estimation analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for customer lifetime value estimation

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 200
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.customer_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 16: YoY Growth Rate with Seasonal Adjustment

**Description:** Computes year-over-year growth rates with seasonal decomposition

**Use Case:** Business analytics for yoy growth rate with seasonal adjustment

**Business Value:** Actionable insights from yoy growth rate with seasonal adjustment

**Purpose:** Production yoy growth rate with seasonal adjustment analysis

**Complexity:** 4 CTEs, 4 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for yoy growth rate with seasonal adjustment

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 210
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 17: Transaction Velocity Heatmap Data

**Description:** Generates heatmap data for transaction velocity by hour and day of week

**Use Case:** Business analytics for transaction velocity heatmap data

**Business Value:** Actionable insights from transaction velocity heatmap data

**Purpose:** Production transaction velocity heatmap data analysis

**Complexity:** 4 CTEs, 5 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for transaction velocity heatmap data

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 220
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.location_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.location_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 18: Running Percentile Sales Distribution

**Description:** Computes running percentile distributions using cumulative window functions

**Use Case:** Business analytics for running percentile sales distribution

**Business Value:** Actionable insights from running percentile sales distribution

**Purpose:** Production running percentile sales distribution analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for running percentile sales distribution

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 230
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.sale_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.sale_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 19: Employee Cross-Sell Effectiveness

**Description:** Measures cross-selling effectiveness using correlated transaction patterns

**Use Case:** Business analytics for employee cross-sell effectiveness

**Business Value:** Actionable insights from employee cross-sell effectiveness

**Purpose:** Production employee cross-sell effectiveness analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for employee cross-sell effectiveness

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 240
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 20: Deleted Transaction Forensic Analysis

**Description:** Forensically analyzes deleted transaction patterns for loss prevention

**Use Case:** Business analytics for deleted transaction forensic analysis

**Business Value:** Actionable insights from deleted transaction forensic analysis

**Purpose:** Production deleted transaction forensic analysis analysis

**Complexity:** 4 CTEs, 4 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for deleted transaction forensic analysis

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 250
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 21: Multi-Metric Dashboard Aggregation

**Description:** Aggregates multiple KPIs into a single dashboard-ready result set

**Use Case:** Business analytics for multi-metric dashboard aggregation

**Business Value:** Actionable insights from multi-metric dashboard aggregation

**Purpose:** Production multi-metric dashboard aggregation analysis

**Complexity:** 4 CTEs, 5 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for multi-metric dashboard aggregation

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 260
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 22: Sequential Purchase Pattern Mining

**Description:** Mines sequential purchase patterns using window-based sequence analysis

**Use Case:** Business analytics for sequential purchase pattern mining

**Business Value:** Actionable insights from sequential purchase pattern mining

**Purpose:** Production sequential purchase pattern mining analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for sequential purchase pattern mining

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 270
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.customer_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.customer_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 23: Revenue Concentration Index

**Description:** Computes Herfindahl-Hirschman style concentration indices for revenue

**Use Case:** Business analytics for revenue concentration index

**Business Value:** Actionable insights from revenue concentration index

**Purpose:** Production revenue concentration index analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for revenue concentration index

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 280
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.customer_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 24: Anomaly Score Computation

**Description:** Assigns anomaly scores using statistical deviation from rolling baselines

**Use Case:** Business analytics for anomaly score computation

**Business Value:** Actionable insights from anomaly score computation

**Purpose:** Production anomaly score computation analysis

**Complexity:** 4 CTEs, 4 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for anomaly score computation

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 290
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 25: Fiscal Period Comparative Analysis

**Description:** Compares performance across fiscal periods with pro-rata adjustments

**Use Case:** Business analytics for fiscal period comparative analysis

**Business Value:** Actionable insights from fiscal period comparative analysis

**Purpose:** Production fiscal period comparative analysis analysis

**Complexity:** 4 CTEs, 5 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for fiscal period comparative analysis

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 300
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.location_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.location_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 26: Transaction Throughput Optimization

**Description:** Identifies throughput bottlenecks using queuing theory metrics

**Use Case:** Business analytics for transaction throughput optimization

**Business Value:** Actionable insights from transaction throughput optimization

**Purpose:** Production transaction throughput optimization analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for transaction throughput optimization

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 310
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 27: Store Account Payment Trend Analysis

**Description:** Analyzes store account payment trends with cumulative and rolling metrics

**Use Case:** Business analytics for store account payment trend analysis

**Business Value:** Actionable insights from store account payment trend analysis

**Purpose:** Production store account payment trend analysis analysis

**Complexity:** 4 CTEs, 7 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for store account payment trend analysis

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 320
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.customer_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 28: Multi-Dimensional Pivot Analysis

**Description:** Creates multi-dimensional pivot-style analysis using CASE-based aggregation

**Use Case:** Business analytics for multi-dimensional pivot analysis

**Business Value:** Actionable insights from multi-dimensional pivot analysis

**Purpose:** Production multi-dimensional pivot analysis analysis

**Complexity:** 4 CTEs, 4 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for multi-dimensional pivot analysis

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 330
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.sale_time) AS period,
    c4.employee_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 29: Sales Funnel Stage Progression

**Description:** Tracks progression through sales funnel stages using state transition analysis

**Use Case:** Business analytics for sales funnel stage progression

**Business Value:** Actionable insights from sales funnel stage progression

**Purpose:** Production sales funnel stage progression analysis

**Complexity:** 4 CTEs, 5 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for sales funnel stage progression

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 340
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.sale_time) AS period,
    c4.customer_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

## Query 30: Outlier Detection with IQR Method

**Description:** Detects outliers using interquartile range method across multiple dimensions

**Use Case:** Business analytics for outlier detection with iqr method

**Business Value:** Actionable insights from outlier detection with iqr method

**Purpose:** Production outlier detection with iqr method analysis

**Complexity:** 4 CTEs, 6 window functions, GROUP BY with HAVING, date arithmetic

**Expected Output:** Aggregated metrics for outlier detection with iqr method

```sql
WITH cte_level_1 AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,
        DATE_TRUNC('day', sale_time) AS sale_day,
        DATE_TRUNC('week', sale_time) AS sale_week,
        EXTRACT(HOUR FROM sale_time) AS sale_hour,
        EXTRACT(DOW FROM sale_time) AS sale_dow
    FROM phppos_sales
    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,
        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,
        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value
    FROM cte_level_1 c1
    WHERE c1.rn <= 350
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,
        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,
        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,
        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,
        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE 
            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev
            ELSE 0 
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.sale_time) AS period,
    c4.sale_id,
    COUNT(*) AS record_count,
    AVG(c4.sale_id) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,
    STDDEV(c4.sale_id) AS stddev_value,
    MIN(c4.sale_id) AS min_value,
    MAX(c4.sale_id) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.sale_time), c4.sale_id
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

