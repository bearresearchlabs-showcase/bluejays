# POS Retail (Lucasa) — Query Documentation

## Database Overview

```yaml
db_id: db-5
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
This database supports analytics for db-5.
```

## Use Case

```text
Target use cases for db-5: analytics, reporting, dashboards.
```

## Business Value

```text
Business value for db-5.
```

## Schema

```sql
-- Minimal phppos schema for db-5 (PostgreSQL)
-- Same as db-2 - only tables needed for gov-rebuilt data and queries
-- ACID: Foreign keys and constraints for referential integrity

CREATE TABLE phppos_people (
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone_number VARCHAR(50),
    email VARCHAR(255),
    address_1 VARCHAR(255),
    address_2 VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(50),
    zip VARCHAR(20),
    country VARCHAR(100),
    comments TEXT,
    person_id INTEGER PRIMARY KEY
);

CREATE TABLE phppos_employees (
    person_id INTEGER PRIMARY KEY REFERENCES phppos_people(person_id),
    username VARCHAR(255),
    password VARCHAR(255),
    balance NUMERIC(15,2) DEFAULT 0,
    deleted INTEGER DEFAULT 0,
    hide_from_switch_user INTEGER DEFAULT 0
);

CREATE TABLE phppos_items (
    name VARCHAR(255),
    category VARCHAR(255),
    description TEXT,
    cost_price NUMERIC(15,2) DEFAULT 0,
    unit_price NUMERIC(15,2) DEFAULT 0,
    item_id INTEGER PRIMARY KEY,
    allow_alt_description INTEGER DEFAULT 0,
    is_serialized INTEGER DEFAULT 0,
    override_default_tax INTEGER DEFAULT 0,
    is_service INTEGER DEFAULT 0,
    deleted INTEGER DEFAULT 0
);

CREATE TABLE phppos_locations (
    location_id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    address TEXT,
    phone VARCHAR(50),
    fax VARCHAR(50),
    email VARCHAR(255),
    receive_stock_alert VARCHAR(10) DEFAULT '0',
    stock_alert_email VARCHAR(255),
    timezone VARCHAR(100),
    mailchimp_api_key VARCHAR(255),
    enable_credit_card_processing VARCHAR(10) DEFAULT '0',
    merchant_id VARCHAR(255),
    merchant_password VARCHAR(255),
    default_tax_1_rate NUMERIC(10,2),
    default_tax_1_name VARCHAR(255),
    default_tax_2_rate NUMERIC(10,2),
    default_tax_2_name VARCHAR(255),
    default_tax_2_cumulative VARCHAR(10) DEFAULT '0',
    default_tax_3_rate NUMERIC(10,2),
    default_tax_3_name VARCHAR(255),
    default_tax_4_rate NUMERIC(10,2),
    default_tax_4_name V
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
  "db_id": "db-5",
  "question_id": 1,
  "question": "Can you show me each employee's daily sales performance over the past year, including their 7-day rolling average and how many of their transactions exceeded their personal average?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day) AS daily_count,\n        AVG(c1.sale_id) OVER (ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg_7d,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 100\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS emp_avg,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        NTILE(4) OVER (ORDER BY c3.sale_id) AS quartile,\n        DENSE_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.daily_count DESC) AS activity_rank,\n        CASE \n            WHEN c3.sale_id > c3.emp_avg THEN 'Above Average'\n            WHEN c3.sale_id = c3.emp_avg THEN 'Average'\n            ELSE 'Below Average'\n        END AS performance_category\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS analysis_date,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    SUM(CASE WHEN c4.performance_category = 'Above Average' THEN 1 ELSE 0 END) AS above_avg_count,\n    AVG(c4.rolling_avg_7d) AS avg_rolling_7d\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) > 1\nORDER BY analysis_date DESC, record_count DESC\nLIMIT 100",
  "evidence": "The query groups transactions by date and employee_id. It computes each employee's overall average (emp_avg), uses a 7-row window for rolling_avg_7d, counts transactions exceeding emp_avg (above_avg_count), retains the 100 most recent per employee, and excludes days with only one transaction. Output includes record_count, quartiles, stddev, above_avg_count, and avg_rolling_7d.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Daily aggregated sales metrics with rolling averages and trend indicators",
  "description": "Store managers need visibility into daily employee performance to identify top performers, coach underperformers, and understand whether sales representatives consistently beat their own benchmarks.",
  "normal_query": "Calculate daily sales metrics for each employee with 7-day rolling average and count of above-average transactions."
}
```


### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 2,
  "question": "Can you show me monthly purchase patterns for each customer, including quartiles, the count of statistical outliers, and how many transactions show an upward trend?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 70\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and customer_id. It uses NTILE(6) for sextiles, calculates z-scores per partition, flags outliers (>2 std dev), derives trend_direction via LAG/LEAD delta_value, limits to 70 points per customer, and requires \u22653 monthly records. Aggregates include quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for customer purchase frequency segmentation",
  "description": "Marketing and customer success teams segment customers by spending behavior to identify high-value or erratic spenders and detect rising or falling engagement for retention and upsell campaigns.",
  "normal_query": "Calculate monthly sales statistics per customer including quartiles, z-score-based outlier count, and count of transactions with increasing trend."
}
```


### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 3,
  "question": "Can you give me daily performance statistics for each employee, including transaction count, quartiles, median, outlier count, and a rolling average?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 80\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and employee_id. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 7-row rolling average; segments into septiles (NTILE(7)); flags outliers via z-score; and includes single-transaction days. Output includes quartiles, stddev, outlier count, increasing count, and rolling average.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for employee performance quartile ranking",
  "description": "Operations managers need daily performance quartiles to benchmark employees, identify consistent high performers for recognition, and flag statistical outliers who may need coaching or compliance review.",
  "normal_query": "Calculate daily sales statistics per employee including record count, quartiles, median, outlier count, and 7-day rolling average."
}
```


### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 4,
  "question": "Can you give me a weekly breakdown of sales by payment type, including quartiles, outlier count, and the number of transactions showing an increasing trend?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY payment_type ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.payment_type) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 90\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.payment_type) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.payment_type) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.payment_type ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.payment_type,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.payment_type\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and payment_type. It uses an 8-row rolling window, segments into octiles (NTILE(8)), derives trend_direction from LAG/LEAD, and requires \u22652 weekly records per payment type. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for payment type revenue distribution",
  "description": "Finance and fraud prevention teams monitor payment method performance over time to reconcile accounts, detect unusual transaction patterns, and understand customer payment preferences for strategic planning.",
  "normal_query": "Calculate weekly sales statistics by payment type including quartiles, outlier count, and count of transactions with increasing trend."
}
```


### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 5,
  "question": "Can you show me monthly sales velocity by store location, including quartiles, standard deviation, outlier count, and cumulative sum?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 100\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.location_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.location_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and location_id. It computes STDDEV for volatility, uses a 9-row rolling window, segments into noniles (NTILE(9)), limits to 100 points per location, and requires \u22653 monthly records. Output includes quartiles, stddev, outlier count, increasing count, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for location-based sales velocity",
  "description": "Regional managers and real estate teams compare store performance across locations to allocate marketing budgets, decide on lease renewals, and identify underperforming locations requiring operational changes.",
  "normal_query": "Calculate monthly sales statistics per location including quartiles, standard deviation, outlier count, and maximum cumulative sum."
}
```


### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 6,
  "question": "Show me daily sales metrics for each employee including quartiles, rolling averages, and any anomalies that stand out.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 110\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and employee_id. It extracts hour and day-of-week, computes z-scores (zero when stddev=0), flags outliers, calculates a 10-row rolling average, and includes single-transaction days. Output includes quartiles, rolling average, outlier count, and increasing count.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for hourly sales pattern detection",
  "description": "Sales operations teams monitor employee performance daily to identify unusual patterns that may indicate data entry errors, fraudulent activity, or exceptional performance requiring investigation.",
  "normal_query": "Calculate daily sales statistics per employee including quartiles, 10-day rolling average, and z-score based anomaly detection."
}
```


### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 7,
  "question": "Give me monthly sales by customer with invoice gap analysis, quartiles, and trend indicators.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 120\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.sale_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.sale_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and customer_id. It employs LAG and LEAD for gap analysis between consecutive periods, derives trend_direction, computes quartiles, and requires \u22653 months of purchase history. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for invoice gap analysis",
  "description": "Customer success teams want to understand how customer purchasing behavior changes month-over-month to predict churn risk and identify upsell opportunities.",
  "normal_query": "Calculate monthly sales statistics per customer including period-over-period gap metrics, quartiles, and directional trend counts."
}
```


### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 8,
  "question": "Show me daily sales by payment method with anomaly detection and quartile breakdowns.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 130\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and payment_type. It calculates z-scores to flag outliers, computes quartiles, derives trend_direction from LAG/LEAD, and requires \u22652 transactions per payment type per day. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for suspended transaction anomaly detection",
  "description": "Finance and fraud prevention teams monitor payment method usage patterns daily because anomalous behavior may signal technical problems, fraudulent activity, or shifts in customer preferences.",
  "normal_query": "Calculate daily sales statistics by payment type including z-score anomaly detection, quartiles, and trend pattern counts."
}
```


### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 9,
  "question": "Give me weekly sales by customer with recency-frequency analysis, quartiles, and rolling averages.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 140\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and customer_id. It applies ROW_NUMBER (desc) for recency scoring, uses record count as frequency proxy, ranks by cumulative sum, computes 6-row rolling average, and requires \u22651 record per group. Output includes quartiles, outlier count, increasing count, and rolling average.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for customer recency-frequency analysis",
  "description": "Marketing teams segment customers based on recent purchasing activity and frequency to design targeted retention campaigns, loyalty rewards, and personalized upsell offers.",
  "normal_query": "Calculate weekly sales statistics per customer including recency-frequency scoring, quartile distributions, and rolling average trends."
}
```


### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 10,
  "question": "Show me monthly sales by employee with cohort-style retention metrics and quartiles.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 150\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and customer_id. It calculates increasing_count and trend_direction (cohort-style), derives quartiles, accommodates single-record months for new hires, and requires \u22652 records per group. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for multi-period cohort retention",
  "description": "Human resources and sales management teams track how employee sales performance evolves over time, similar to cohort retention analysis, to inform training programs and retention strategies.",
  "normal_query": "Calculate monthly sales statistics per employee including cohort-retention style indicators, quartile distributions, and progression metrics."
}
```


### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 11,
  "question": "What are the daily sales statistics by location, including acceleration rate, quartiles, and outlier count?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 160\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and location_id. It computes delta_value as acceleration indicator, calculates quartiles (PERCENTILE_CONT), counts outliers, and requires \u22652 transactions per location-day. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for sales acceleration rate computation",
  "description": "Retail operations teams need to understand sales acceleration patterns at each location to identify high-growth stores for expansion and resource allocation.",
  "normal_query": "Calculate daily sales statistics for each location, including acceleration metrics, quartile distribution, and the count of outlier transactions."
}
```


### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 12,
  "question": "What are the weekly sales statistics by employee, including cross-location revenue benchmarking and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 170\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.location_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.location_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and employee_id. It computes PERCENT_RANK for cross-location percentile position, applies DENSE_RANK for tier classification, calculates quartiles, and requires \u22653 transactions per employee-week. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for cross-location revenue benchmarking",
  "description": "Sales management teams benchmark employee performance across all locations to identify top performers, establish fair compensation targets, and provide coaching to underperformers.",
  "normal_query": "Calculate weekly sales statistics for each employee, including benchmarking metrics for cross-employee comparison and quartile distribution."
}
```


### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 13,
  "question": "What are the monthly sales statistics by payment type, including time-weighted moving average and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 180\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.sale_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.sale_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and payment_type. It computes a rolling average using ROWS BETWEEN, calculates Q1, median, Q3 quartiles, and requires \u22652 records per payment-type-month. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for time-weighted moving average",
  "description": "Finance and strategy teams need to understand long-term trends in payment method preferences, filtering out seasonal spikes and promotional effects that create short-term noise.",
  "normal_query": "Calculate monthly sales statistics for each payment type, including a time-weighted moving average and quartile distribution."
}
```


### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 14,
  "question": "What are the daily sales statistics by customer, including peak hour identification for staffing and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 190\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and customer_id. It extracts hour for peak identification, calculates quartiles, includes single-transaction customer-days, and uses rolling avg and cumulative sum. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for peak hour identification and staffing",
  "description": "Operations teams optimize staff scheduling and promotional timing by understanding when different customer segments make purchases throughout the day.",
  "normal_query": "Calculate daily sales statistics for each customer, including peak hour metrics for staffing optimization and quartile distribution."
}
```


### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 15,
  "question": "What are the weekly sales statistics by location, including customer lifetime value estimation style metrics and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 200\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and customer_id (LTV by location). It computes cumulative_sum and max_cumulative as LTV proxies, ranks locations by cumulative sum, calculates quartiles, and requires \u22651 record per group. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for customer lifetime value estimation",
  "description": "Corporate strategy and real estate teams prioritize locations for capital investment and concentrated marketing spend using LTV-style principles.",
  "normal_query": "Calculate weekly sales statistics for each location, including LTV-style metrics for investment prioritization and quartile distribution."
}
```


### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 16,
  "question": "What are the monthly sales statistics for each employee, including year-over-year growth rates adjusted for seasonal trends and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 210\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and employee_id. It calculates trend_direction and delta_value for YoY-style growth, computes quartiles, limits to 210 points per employee, and requires \u22652 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for yoy growth rate with seasonal adjustment",
  "description": "Sales management teams evaluate employee performance across different seasons and plan staffing and training budgets for the upcoming fiscal year.",
  "normal_query": "Calculate monthly sales performance metrics for each employee, including year-over-year growth rates, seasonal trend adjustments, and quartile distributions."
}
```


### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 17,
  "question": "What are the daily sales breakdowns by payment type that can be used to create a transaction velocity heatmap with quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 220\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.location_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.location_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and payment_type. It uses period and payment_type as heatmap axes, calculates quartiles and trend counts, and requires \u22652 records per day-payment group. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for transaction velocity heatmap data",
  "description": "Finance and operations teams visualize payment method adoption and transaction velocity patterns throughout the week and month to optimize payment processing infrastructure.",
  "normal_query": "Generate daily sales statistics grouped by payment type, including transaction velocity metrics, quartile distributions, and trend indicators formatted for heatmap visualization."
}
```


### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 18,
  "question": "What are the weekly sales statistics for each customer showing their running percentile distribution within each week and quartile classifications?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 230\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.sale_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.sale_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and sale_id (customer proxy). It employs PERCENT_RANK for running percentile position and PERCENTILE_CONT for quartile boundaries. Requires \u22651 record per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for running percentile sales distribution",
  "description": "Marketing and customer success teams segment customers based on weekly spending behavior to personalize engagement, identify high-value customers for VIP programs, and detect at-risk customers.",
  "normal_query": "Compute weekly sales metrics for each customer, including their running percentile rank within the weekly customer cohort and quartile distributions."
}
```


### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 19,
  "question": "What are the monthly sales statistics by location that measure employee cross-selling effectiveness along with quartile performance distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 240\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and employee_id. It uses DENSE_RANK for location ranking, calculates quartiles, and produces cross-sell-style metrics. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for employee cross-sell effectiveness",
  "description": "Regional sales management teams identify which locations have the most effective cross-selling techniques so they can replicate best practices across underperforming stores.",
  "normal_query": "Calculate monthly sales performance metrics for each location, including cross-sell effectiveness indicators, comparative rankings, and quartile distributions."
}
```


### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 20,
  "question": "What are the daily sales statistics by employee that include forensic analysis of deleted transactions, transaction sequencing, and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 250\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and employee_id. It uses LAG and LEAD for sequential transaction analysis, calculates time gaps between consecutive transactions, derives trend_direction, and computes quartiles. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for deleted transaction forensic analysis",
  "description": "Internal audit and loss prevention teams investigate patterns in voided, refunded, or soft-deleted transactions that might indicate employee fraud, system errors, or training issues.",
  "normal_query": "Generate daily sales metrics for each employee with forensic analysis indicators for voided and deleted transactions, sequential transaction patterns, and quartile distributions."
}
```


### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 21,
  "question": "What are the weekly sales statistics broken down by payment type, including quartiles and multi-metric aggregations for our executive dashboard?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 260\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and employee_id. It performs single-pass aggregation: record_count, avg_value, quartiles, stddev, min, max, outlier_count, increasing_count, avg_rolling, max_cumulative. Requires \u22651 record per group. Output includes full dashboard suite of statistics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for multi-metric dashboard aggregation",
  "description": "Executive teams require a unified dashboard view that consolidates all critical payment-related metrics across different payment types for weekly review meetings.",
  "normal_query": "Calculate comprehensive weekly sales statistics grouped by payment type, including quartiles and all dashboard metrics for executive review."
}
```


### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 22,
  "question": "What are the monthly sales statistics for each customer that reveal sequential purchase patterns and include quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 270\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and customer_id. It employs LAG and LEAD for previous/next month values, calculates delta_value and trend_direction for sequential patterns, and requires \u22652 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for sequential purchase pattern mining",
  "description": "Marketing teams need to understand how individual customer purchasing behavior evolves month-over-month to build effective personalization strategies and targeted campaigns.",
  "normal_query": "Calculate monthly sales statistics per customer with sequential purchase pattern metrics and quartile analysis for behavior tracking."
}
```


### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 23,
  "question": "What are the daily sales statistics by location that show revenue concentration indices and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 280\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and customer_id. It uses DENSE_RANK and PERCENT_RANK for concentration indices, cumulative_sum for revenue concentration, and requires \u22653 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for revenue concentration index",
  "description": "Operations management needs to understand how revenue is distributed across locations daily for resource allocation, staffing levels, and identifying which locations drive the majority of sales.",
  "normal_query": "Calculate daily sales statistics per location with revenue concentration metrics and quartiles to understand sales distribution patterns."
}
```


### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 24,
  "question": "What are the weekly sales statistics for each employee that include anomaly scores and quartiles to identify unusual performance patterns?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 290\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and employee_id. It calculates z_score as anomaly metric, aggregates outlier_count, computes quartiles, and requires \u22651 record per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for anomaly score computation",
  "description": "Human resources and sales management need to systematically identify employees with unusual sales patterns for recognition or compliance investigation.",
  "normal_query": "Calculate weekly sales statistics per employee with computed anomaly scores and quartile distributions for performance monitoring."
}
```


### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 25,
  "question": "What are the monthly sales statistics by payment type formatted for fiscal period comparative analysis with quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 300\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.location_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.location_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and location_id. It uses DATE_TRUNC('month') for fiscal period alignment, calculates quartiles (PERCENTILE_CONT), and requires \u22652 records per payment-type-month. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for fiscal period comparative analysis",
  "description": "Finance departments require standardized monthly reporting aligned with fiscal periods for month-over-month and quarter-over-quarter comparisons of payment type performance.",
  "normal_query": "Calculate monthly sales statistics grouped by payment type for fiscal period reporting, including quartiles to support period-over-period comparisons."
}
```


### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 26,
  "question": "What are the daily sales statistics for each customer, including transaction throughput metrics and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 310\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and employee_id. It calculates record_count (throughput proxy), avg_rolling, max_cumulative, preserves single-transaction months, and requires \u22653 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for transaction throughput optimization",
  "description": "Business needs to assess transaction volume patterns per customer to optimize system capacity planning and design tiered loyalty programs based on activity levels.",
  "normal_query": "Calculate daily sales statistics for each customer including throughput indicators and quartile breakdowns."
}
```


### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 27,
  "question": "What are the weekly sales statistics by store location, showing payment method trend analysis and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 320\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and customer_id. It computes trend_direction and increasing_count for payment trend analysis, requires \u22651 record per group, and produces quartiles and cumulative metrics. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for store account payment trend analysis",
  "description": "Retail operations management requires analysis of payment method trends across store locations to identify shifts in payment mix for terminal deployment and maintenance planning.",
  "normal_query": "Calculate weekly sales statistics for each location including payment trend indicators and quartile breakdowns."
}
```


### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 28,
  "question": "What are the monthly sales statistics for each employee, structured for multi-dimensional pivot analysis with quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 330\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by week and employee_id. It uses period and employee_id as dimensional axes for pivoting, retains single-record months for complete coverage, and requires \u22652 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for multi-dimensional pivot analysis",
  "description": "Business intelligence teams require flexible, multi-dimensional sales data aggregated by time period and employee to support ad-hoc reporting, pivot tables, and cross-functional analysis.",
  "normal_query": "Calculate monthly sales statistics for each employee with multi-dimensional aggregation structure and quartile breakdowns."
}
```


### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 29,
  "question": "What are the daily sales statistics by payment type, showing sales funnel stage progression and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 340\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by month and customer_id. It calculates trend_direction for funnel stage progression, requires \u22653 records per group, and produces quartiles and cumulative metrics. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for sales funnel stage progression",
  "description": "Sales and conversion optimization teams track how the mix of payment methods evolves throughout each day to understand customer payment preferences at different times and stages.",
  "normal_query": "Calculate daily sales statistics for each payment type including funnel progression metrics and quartile breakdowns."
}
```


### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-5",
  "question_id": 30,
  "question": "What are the weekly sales statistics for each customer, using IQR-based outlier detection methods and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 350\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.sale_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.sale_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "The query groups by day and sale_id (customer proxy). It calculates quartiles via PERCENTILE_CONT for Q1 and Q3 (IQR support), flags outliers (z-score > 2), and requires \u22653 records per customer-week. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for outlier detection with iqr method",
  "description": "Fraud detection and customer relationship management teams identify customers with unusual spending patterns using statistical outlier detection to flag potential fraud or high-value VIP customers.",
  "normal_query": "Calculate weekly sales statistics for each customer with IQR-style outlier detection and quartile breakdowns."
}
```

