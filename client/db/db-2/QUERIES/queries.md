# Filling Station Retail / POS (phppos) — Query Documentation

## Database Overview

```yaml
db_id: db-2
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
This database supports analytics for db-2.
```

## Use Case

```text
Target use cases for db-2: analytics, reporting, dashboards.
```

## Business Value

```text
Business value for db-2.
```

## Schema

```sql
-- Minimal phppos schema for db-2 (PostgreSQL)
-- Only tables needed for gov-rebuilt data and queries
-- ACID-compliant: PKs and FKs for referential integrity

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
    default_tax_4_name VARCHAR(255),
    defau
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
  "db_id": "db-2",
  "question_id": 1,
  "question": "Can you show me how each employee's daily sales have been trending over the past year? I'd like to see rolling 7-day averages and identify how many transactions exceed their personal average.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day) AS daily_count,\n        AVG(c1.sale_id) OVER (ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg_7d,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 100\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS emp_avg,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        NTILE(4) OVER (ORDER BY c3.sale_id) AS quartile,\n        DENSE_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.daily_count DESC) AS activity_rank,\n        CASE \n            WHEN c3.sale_id > c3.emp_avg THEN 'Above Average'\n            WHEN c3.sale_id = c3.emp_avg THEN 'Average'\n            ELSE 'Below Average'\n        END AS performance_category\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS analysis_date,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    SUM(CASE WHEN c4.performance_category = 'Above Average' THEN 1 ELSE 0 END) AS above_avg_count,\n    AVG(c4.rolling_avg_7d) AS avg_rolling_7d\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) > 1\nORDER BY analysis_date DESC, record_count DESC\nLIMIT 100",
  "evidence": "Situation: Store managers monitor employee performance to identify top performers for recognition and struggling employees who need coaching. They need visibility into daily sales patterns smoothed by weekly trends to distinguish genuine performance shifts from day-to-day noise. Task: Generate daily sales metrics for each employee that include a rolling 7-day average and a count of transactions exceeding the employee's personal average. Action: The query groups transactions by date and employee, then computes each employee's overall average transaction value as a benchmark. It applies a 7-row rolling window ordered by date to calculate smoothed averages, compares individual transactions against the employee's benchmark to count above-average performance, retains only the 100 most recent transactions per employee to focus on current trends, and excludes days with single transactions to avoid statistical noise. Result: A dataset containing daily metrics for each employee showing their ro",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Daily aggregated sales metrics with rolling averages and trend indicators",
  "normal_query": "Calculate daily sales metrics for each employee including rolling 7-day average and count of transactions above their personal average."
}
```

### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 2,
  "question": "Can you break down monthly purchase behavior by customer? I need to see quartile distributions, how many outlier transactions occurred, and which customers show increasing purchase trends.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 70\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Marketing and customer success teams segment customers by purchase patterns to tailor retention campaigns, identify VIP customers with unusual high spending, and detect disengagement early. Understanding statistical distributions and trend directions enables targeted interventions. Task: Produce monthly aggregated sales statistics per customer that include quartile breakdowns, counts of statistical outliers, and identification of upward spending trends. Action: The query groups purchases by month and customer, then calculates quartiles by segmenting spend into sextiles (six equal groups). It computes z-scores for each transaction and flags those exceeding two standard deviations as outliers. To detect momentum, it derives trend direction by comparing consecutive transaction amounts and counts how many show increases. The query limits each customer to their 70 most recent data points for manageability and requires at least three transactions per month per customer to ensure s",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for customer purchase frequency segmentation",
  "normal_query": "Generate monthly customer purchase statistics including quartiles, z-score-based outlier count, and count of transactions following an increasing trend."
}
```

### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 3,
  "question": "Show me daily performance quartiles for each employee \u2014 I want to see transaction count, median sales, outlier count, and a rolling average.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 80\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Operations managers compare employee performance daily to ensure fair workload distribution, recognize high achievers, and identify employees whose sales patterns deviate significantly from the norm, which may indicate training needs or exceptional customer service. Quartile analysis provides a standardized benchmark across the team. Task: Generate daily sales statistics for each employee that include transaction count, first quartile, median, third quartile, outlier count, and a rolling average. Action: The query groups sales by date and employee, then applies PERCENTILE_CONT to compute Q1 (25th percentile), median (50th percentile), and Q3 (75th percentile) for robust statistical summaries. It calculates a 7-row rolling average to smooth daily volatility, segments transactions into septiles (seven equal groups) to classify distribution spread, and permits single-transaction days to accommodate newly hired employees who are ramping up. Result: Daily performance metrics for ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for employee performance quartile ranking",
  "normal_query": "Calculate daily sales statistics per employee with quartiles, median, outlier count, and rolling average."
}
```

### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 4,
  "question": "I need a weekly breakdown of sales by payment type \u2014 show me quartiles, outlier counts, and how many transactions are on an upward trend.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY payment_type ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.payment_type) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.payment_type ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 90\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.payment_type) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.payment_type) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.payment_type ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.payment_type ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.payment_type,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.payment_type\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Finance and fraud prevention teams monitor payment method usage patterns to ensure accurate reconciliation, detect anomalies that may indicate fraud or processing errors, and understand customer payment preferences over time. Weekly aggregation balances granularity with trend stability. Task: Produce weekly sales statistics segmented by payment type (cash, credit card, mobile payment, etc.) that include quartile distributions, counts of outlier transactions, and identification of increasing transaction trends. Action: The query groups transactions by week and payment type, then computes quartiles to understand the spread of transaction amounts within each payment method. It applies an 8-row rolling window to smooth weekly fluctuations, segments data into octiles (eight equal groups) for finer distribution analysis, flags statistical outliers, counts transactions that increase compared to prior periods to identify momentum, and requires at least two records per week per payme",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for payment type revenue distribution",
  "normal_query": "Compute weekly sales statistics by payment type with quartiles, outlier count, and count of transactions showing an increasing trend."
}
```

### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 5,
  "question": "Give me monthly sales velocity by store location \u2014 I want quartiles, standard deviation, outlier count, and cumulative totals.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 100\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.location_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.location_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Regional managers and operations executives compare store performance across multiple locations to allocate marketing budgets, decide on new store openings or closures, and identify underperforming sites that require operational improvements. Monthly aggregation provides enough data to smooth daily volatility while remaining actionable for quarterly planning cycles. Task: Generate monthly sales statistics for each location that include quartile distributions, standard deviation as a measure of sales volatility, count of outlier transactions, and the maximum cumulative sales sum. Action: The query groups sales by month and location, then calculates Q1, median, and Q3 to profile the spending distribution at each site. It computes standard deviation to quantify sales variability, which helps distinguish consistently performing stores from volatile ones. A 9-row rolling window smooths multi-month trends, and the data is segmented into noniles (nine equal groups) for granular dis",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for location-based sales velocity",
  "normal_query": "Compute monthly sales statistics per location with quartiles, standard deviation, outlier count, and maximum cumulative sum."
}
```

### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 6,
  "question": "Show me daily sales performance by employee with quartile distributions, rolling averages, and anomaly detection.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 110\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The sales operations team needs to monitor daily employee performance to identify unusual patterns that may indicate data entry errors, fraudulent transactions, or exceptional sales activity requiring investigation. Task: Generate comprehensive daily sales statistics for each employee that include quartile distributions, rolling trend indicators, and statistical anomaly detection. Action: The query aggregates sales transactions by day and employee, extracts temporal features (hour of day and day of week) to provide context, calculates quartile boundaries (25th, 50th, 75th percentiles) for distribution analysis, computes a 10-day rolling average to smooth short-term fluctuations, applies z-score methodology to flag statistical outliers beyond normal variance, and accommodates employees who may have only a single transaction on certain days. Result: A dataset containing daily performance metrics for each employee including quartile values for understanding sales distribution, ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for hourly sales pattern detection",
  "normal_query": "Calculate daily sales statistics for each employee including quartile distributions, rolling averages, and z-score outlier counts."
}
```

### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 7,
  "question": "Show me monthly sales by customer with purchase frequency gap analysis, quartiles, and trend indicators.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 120\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.sale_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.sale_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The customer success team is building a churn prediction model and needs to understand how customer purchase behavior evolves month-over-month, specifically looking at changes in purchase frequency and spending amounts to identify customers at risk of churning. Task: Produce monthly sales statistics for each customer that capture sequential purchasing patterns through gap-style metrics, quartile distributions for spend analysis, and directional trend indicators. Action: The query groups sales data by month and customer, uses window functions LAG and LEAD to compute differences between consecutive months (measuring changes in purchase frequency and amounts), derives trend direction indicators (increasing, stable, or decreasing), calculates quartile boundaries for spend distribution analysis, and filters to include only customers with at least 3 months of purchase history to ensure meaningful trend detection. Result: A dataset containing monthly metrics for each customer inclu",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for invoice gap analysis",
  "normal_query": "Calculate monthly sales statistics for each customer including gap analysis metrics between consecutive months, quartile distributions, and trend direction counts."
}
```

### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 8,
  "question": "Show me daily sales by payment type with anomaly detection, quartiles, and trend patterns.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 130\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The finance and fraud detection teams need to monitor payment processing patterns across different payment types (credit card, cash, digital wallet, etc.) to quickly identify unusual activity that may signal system malfunctions, fraudulent behavior, or unexpected shifts in customer payment preferences. Task: Generate daily sales statistics segmented by payment type that include statistical anomaly detection, quartile distributions for normal range identification, and trend pattern analysis. Action: The query aggregates transactions by day and payment type, applies z-score statistical methodology to flag days where transaction volumes or amounts fall outside normal variance thresholds, calculates quartile boundaries to establish baseline expectations for each payment type, derives trend direction indicators to capture momentum patterns, and requires at least 2 transaction records per group to enable meaningful statistical comparison. Result: A dataset containing daily metrics",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for suspended transaction anomaly detection",
  "normal_query": "Calculate daily sales statistics grouped by payment type including z-score anomaly detection, quartile distributions, and trend direction counts."
}
```

### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 9,
  "question": "Show me weekly sales by customer with recency-frequency analysis, quartiles, and rolling averages.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 140\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The marketing team is designing targeted retention and upsell campaigns and needs to segment customers based on how recently and how frequently they purchase, combined with their spending patterns, to prioritize outreach efforts and personalize messaging for maximum campaign effectiveness. Task: Produce weekly sales statistics for each customer that incorporate RFM-style (recency-frequency-monetary) metrics, quartile distributions for spend segmentation, and rolling averages for trend identification. Action: The query groups sales transactions by week and customer, uses the ROW_NUMBER window function to establish recency ordering (identifying most recent purchases), ranks customers by cumulative spending to determine monetary value tiers, calculates quartile boundaries for spend distribution analysis, computes rolling averages to smooth weekly volatility, and filters to include only customers with at least 3 weeks of purchase activity to ensure statistically meaningful metri",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for customer recency-frequency analysis",
  "normal_query": "Calculate weekly sales statistics for each customer including recency-frequency metrics, quartile distributions, and rolling averages."
}
```

### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 10,
  "question": "Show me monthly sales by employee with cohort-style retention analysis and quartile distributions.",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 150\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The human resources and sales management teams need to track how employee sales performance evolves over their tenure to identify which employees are improving, plateauing, or declining, informing decisions about additional training needs, recognition programs, and retention strategies for high performers. Task: Generate monthly sales statistics for each employee that apply cohort analysis methodology to compare performance trajectories over time, combined with quartile distributions for peer benchmarking. Action: The query aggregates sales by month and employee, calculates an increasing_count metric that tracks cumulative months of activity to enable cohort-based comparisons, derives trend_direction indicators to classify performance momentum (improving, stable, declining), computes quartile boundaries to enable relative performance assessment against peers, and accommodates single-record months to include newly hired employees in the analysis without distorting statistical",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for multi-period cohort retention",
  "normal_query": "Calculate monthly sales statistics for each employee including cohort-style performance metrics and quartile distributions."
}
```

### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 11,
  "question": "What are the daily sales statistics by location, including acceleration rate, quartiles, and outlier count?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 160\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The retail operations team is planning regional expansion and needs to understand how quickly revenue is growing at each location. Sales acceleration metrics reveal which stores are gaining momentum versus plateauing, helping prioritize investment decisions. Task: Calculate daily sales statistics for each location including acceleration rate, quartile distribution, and outlier identification. Action: The query groups transactions by calendar day and location, computes delta_value to measure day-over-day change in sales velocity, calculates quartile boundaries (Q1, Q2, Q3) for the distribution, identifies outliers beyond typical ranges, and filters to locations with at least 2 days of data to ensure meaningful trend analysis. Result: A dataset showing daily performance metrics for each location\u2014acceleration indicators measuring growth momentum, quartile values showing the sales distribution, and outlier counts flagging anomalous days that may require investigation.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for sales acceleration rate computation",
  "normal_query": "Calculate daily sales statistics for each location with acceleration metrics, quartile distribution, and count of outliers."
}
```

### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 12,
  "question": "What are the weekly sales statistics by employee with cross-location revenue benchmarking and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 170\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.location_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.location_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The sales management team wants to identify top-performing employees across all locations and establish fair, data-driven sales targets that account for regional differences. Cross-employee benchmarking provides objective performance comparisons while controlling for location-specific factors. Task: Calculate weekly sales statistics for each employee including cross-location benchmarking metrics and quartile distribution. Action: The query groups transactions by calendar week and employee, applies PERCENT_RANK to determine each employee's relative position within their cohort, uses DENSE_RANK for sequential performance ordering without gaps, calculates quartile boundaries to segment the sales distribution, and requires at least 3 weeks of data per employee to establish reliable patterns. Result: A dataset showing weekly performance metrics for each employee\u2014benchmark rankings showing relative standing among peers, quartile values revealing the distribution of their sales, an",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for cross-location revenue benchmarking",
  "normal_query": "Calculate weekly sales statistics for each employee with cross-location benchmarking metrics and quartile distribution."
}
```

### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 13,
  "question": "What are the monthly sales statistics by payment type with time-weighted moving average and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 180\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.sale_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.sale_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The finance team needs to understand long-term trends in payment method preferences, but monthly data contains seasonal noise from holidays, promotions, and shopping cycles. Moving averages smooth these fluctuations to reveal the underlying shift in customer payment behavior, which informs payment processing investments and partnership decisions. Task: Calculate monthly sales statistics by payment type including time-weighted moving average and quartile distribution. Action: The query groups transactions by calendar month and payment type (credit card, cash, mobile wallet, etc.), computes a rolling average using a ROWS BETWEEN window frame that looks backward across multiple months to smooth volatility, calculates quartile boundaries for the distribution, and requires at least 2 months of data per payment type to establish baseline trends. Result: A dataset showing monthly performance metrics for each payment type\u2014rolling averages that reveal smoothed trend lines free from s",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for time-weighted moving average",
  "normal_query": "Calculate monthly sales statistics for each payment type with time-weighted moving average and quartile distribution."
}
```

### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 14,
  "question": "What are the daily sales statistics by customer with peak hour identification and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 190\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The store operations team is optimizing labor scheduling and promotional timing to align with customer shopping patterns. Understanding when specific customer segments prefer to shop enables better staff allocation during high-traffic periods and more effective promotional campaign timing. Peak hour identification also supports inventory replenishment planning. Task: Calculate daily sales statistics per customer including peak hour identification and quartile distribution. Action: The query groups transactions by calendar day and customer, extracts the sale_hour timestamp component to identify when each transaction occurred, determines peak shopping hours for each customer segment through frequency analysis, calculates quartile boundaries for the sales distribution, and includes even single-transaction days to capture all customer activity patterns without imposing minimum thresholds. Result: A dataset showing daily performance metrics for each customer\u2014peak hour indicators ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for peak hour identification and staffing",
  "normal_query": "Calculate daily sales statistics for each customer with peak hour metrics and quartile distribution."
}
```

### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 15,
  "question": "What are the weekly sales statistics by location with customer lifetime value estimation metrics and quartiles?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 200\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The marketing and real estate teams are prioritizing locations for increased investment, lease renewals, and targeted campaigns. Customer lifetime value (LTV) concepts applied at the location level help identify which stores generate the most sustained, cumulative value over time versus one-time spikes, informing strategic resource allocation decisions. Task: Calculate weekly sales statistics per location including LTV-style estimation metrics and quartile distribution. Action: The query groups transactions by calendar week and location, computes cumulative_sum to track running total revenue as a proxy for long-term value generation, calculates max_cumulative to identify peak value contribution periods, applies quartile segmentation to the distribution, and requires at least 3 weeks of data per location to establish meaningful cumulative patterns rather than isolated events. Result: A dataset showing weekly performance metrics for each location\u2014LTV-style rankings that priori",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for customer lifetime value estimation",
  "normal_query": "Calculate weekly sales statistics for each location with LTV-style metrics and quartile distribution."
}
```

### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 16,
  "question": "What are the monthly sales statistics for each employee, including year-over-year growth rates with seasonal adjustments and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 210\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The sales management team needs to compare employee performance across different seasons and years to identify top performers and plan resource allocation for the upcoming year. Year-over-year growth metrics help normalize seasonal fluctuations in sales patterns. Task: Calculate monthly sales statistics for each employee showing year-over-year growth trends and quartile rankings. Action: The query groups sales data by month and employee identifier, applies window functions to compute trend_direction and delta_value metrics for growth analysis, filters records to the most recent 365 days to enable valid year-over-year comparisons, and accommodates months where an employee may have only a single transaction record. Result: A dataset containing monthly sales metrics for each employee, including growth direction indicators, percentage or absolute delta values from the prior year, and quartile positions within their peer group.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for yoy growth rate with seasonal adjustment",
  "normal_query": "Calculate monthly sales performance metrics for each employee, including year-over-year growth comparisons and quartile distributions."
}
```

### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 17,
  "question": "What are the daily sales statistics broken down by payment type, formatted for transaction velocity heatmap visualization with quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 220\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.location_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.location_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The operations team wants to create visual heatmaps showing how payment methods (credit card, cash, mobile payment, etc.) are used throughout different days and times, enabling quick identification of payment mix shifts and transaction velocity patterns that inform staffing and system capacity decisions. Task: Generate daily sales statistics segmented by payment type in a format suitable for heatmap visualization tools. Action: The query groups transaction data by calendar day and payment_type, structures output using period (date/time dimension) and payment_type as the two heatmap axes, calculates quartile distributions to enable color-coding intensity, counts trend occurrences for velocity indicators, and filters to groups with at least 2 transaction records to ensure statistical relevance. Result: A heatmap-ready dataset with daily metrics for each payment type, including dimensional coordinates for plotting, quartile values for color intensity mapping, and trend counts s",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for transaction velocity heatmap data",
  "normal_query": "Generate daily sales metrics grouped by payment type, optimized for heatmap visualization with quartile breakdowns and trend indicators."
}
```

### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 18,
  "question": "What are the weekly sales statistics for each customer, including running percentile distributions and quartile rankings?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 230\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.sale_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.sale_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The marketing and customer success teams need to understand how customer spending patterns distribute within each week to support customer segmentation strategies, identify high-value customers, and detect changes in purchasing behavior that may signal upsell opportunities or churn risk. Task: Calculate weekly sales statistics for each customer showing their position in the spending distribution using running percentiles and quartiles. Action: The query groups sales transactions by calendar week and customer identifier, applies PERCENT_RANK window function to show each customer's relative position in the weekly spending distribution, uses PERCENTILE_CONT to calculate quartile boundaries (25th, 50th, 75th percentiles) for the week, and filters to groups containing at least 3 transaction records to ensure meaningful statistical calculations. Result: A dataset of weekly metrics for each customer showing their running percentile rank within that week's customer base, quartile cl",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for running percentile sales distribution",
  "normal_query": "Calculate weekly sales performance metrics for each customer, showing running percentile positions and quartile distributions."
}
```

### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 19,
  "question": "What are the monthly sales statistics by location, including employee cross-sell effectiveness metrics and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 240\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: Regional and location managers need to evaluate which store locations are most effective at cross-selling additional products or services, helping identify where training programs, employee incentives, or merchandising strategies are successfully driving multi-item purchases versus locations that need support. Task: Calculate monthly sales statistics for each location with metrics showing cross-sell effectiveness and quartile performance rankings. Action: The query groups sales data by calendar month and location identifier, uses DENSE_RANK window function to rank locations by cross-sell metrics within each month, calculates partition-specific statistics to enable peer comparisons across similar location types or regions, computes quartile distributions to classify high and low performers, and filters to groups with at least 3 transaction records for statistical validity. Result: A dataset of monthly metrics for each location including cross-sell effectiveness indicators (su",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for employee cross-sell effectiveness",
  "normal_query": "Generate monthly sales metrics for each location showing cross-sell performance indicators and quartile rankings."
}
```

### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 20,
  "question": "What are the daily sales statistics for each employee, including forensic analysis of deleted transactions and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 250\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The loss prevention and audit teams need to investigate transaction anomalies by tracing the complete sequence of sales events including voids, refunds, and soft-deleted records to detect potential fraud patterns, training issues, or system errors. Understanding the temporal sequence and deletion patterns of transactions helps identify suspicious behavior or process breakdowns. Task: Generate daily sales statistics for each employee incorporating forensic metrics that track transaction sequencing and deletion activity. Action: The query groups transaction records by calendar day and employee identifier, applies LAG and LEAD window functions to sequence transactions chronologically and identify gaps or reversals, leverages the deleted flag column (if present) to track soft-deleted or voided transactions separately from completed sales, calculates quartile distributions for transaction volumes and values, and includes all transaction states to provide complete forensic visibil",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for deleted transaction forensic analysis",
  "normal_query": "Calculate daily sales metrics for each employee with forensic tracking of transaction sequences, voids, refunds, and soft-deleted records, plus quartile distributions."
}
```

### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 21,
  "question": "What are the weekly sales statistics broken down by payment type, including quartiles and all key metrics for the executive dashboard?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 260\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The executive team reviews a weekly dashboard that requires a comprehensive view of sales performance across different payment methods (credit card, cash, digital wallet, etc.) to understand payment preference trends and identify potential issues with specific payment channels. Task: Generate a complete set of weekly sales statistics segmented by payment type that includes all dashboard-required metrics in a single query. Action: The SQL groups transactions by calendar week and payment type, then computes multiple aggregations in one pass: record count, average transaction value, first/second/third quartiles for distribution analysis, standard deviation for volatility, minimum and maximum values for range, outlier count using z-score threshold, count of week-over-week increases using window functions, rolling 3-week average for trend smoothing, and cumulative maximum to track peaks. The query filters to include only groups with at least 2 records to ensure statistical validi",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for multi-metric dashboard aggregation",
  "normal_query": "Calculate comprehensive weekly sales statistics grouped by payment type, including quartiles and multi-metric aggregations for dashboard reporting."
}
```

### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 22,
  "question": "How do individual customer purchasing patterns evolve month-over-month, including sequential behavior metrics and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 270\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The personalization team needs to understand how each customer's purchasing behavior changes over time to tailor marketing campaigns, predict churn, and identify upsell opportunities. Sequential pattern mining reveals whether customers are increasing spend, changing purchase frequency, or showing signs of disengagement. Task: Produce monthly sales statistics for each customer that capture sequential purchasing patterns alongside distribution metrics. Action: The SQL groups all transactions by calendar month and customer ID, then applies window functions to analyze temporal patterns: LAG retrieves the previous month's value for each customer, LEAD fetches the next month's value, delta_value calculates month-over-month change, and trend_direction classifies the movement as increasing, decreasing, or stable. The query also computes quartiles (Q1, median, Q3) to understand spending distribution and includes record count, average, and range metrics. Only customers with at least 3",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for sequential purchase pattern mining",
  "normal_query": "Calculate monthly sales statistics for each customer with sequential purchase pattern analysis and quartile breakdowns."
}
```

### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 23,
  "question": "What is the daily revenue concentration across different store locations, showing which locations dominate sales and their quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 280\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The operations team needs to understand how revenue is distributed across store locations to make informed decisions about staffing levels, inventory allocation, and potential store expansions or closures. Revenue concentration metrics reveal whether sales are evenly distributed or heavily concentrated in a few high-performing locations. Task: Generate daily sales statistics for each location that quantify revenue concentration and competitive positioning. Action: The SQL groups transactions by calendar day and location, then computes concentration metrics using advanced window functions: DENSE_RANK assigns a ranking to each location based on daily sales (with ties receiving the same rank), PERCENT_RANK calculates the percentile position of each location (0 = lowest, 1 = highest), and cumulative_sum tracks running total revenue across ranked locations to identify the share captured by top performers. The query also includes quartile calculations (Q1, median, Q3), record coun",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for revenue concentration index",
  "normal_query": "Calculate daily sales statistics by location with revenue concentration indices and quartile analysis."
}
```

### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 24,
  "question": "Which employees show unusual weekly sales patterns that may indicate exceptional performance or require additional training support?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 290\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The sales management team monitors employee performance to identify both top performers who deserve recognition and individuals who may need coaching or are exhibiting unusual sales patterns that warrant investigation. Anomaly scores provide an objective, data-driven method to prioritize which employees to review rather than relying on subjective assessments. Task: Produce weekly sales statistics for each employee that include statistical anomaly scores to flag unusual performance patterns. Action: The SQL groups all transactions by calendar week and employee ID, then calculates a comprehensive set of metrics with focus on anomaly detection: z_score (standardized score showing how many standard deviations from the mean) serves as the primary anomaly indicator, with values beyond \u00b12 or \u00b13 indicating unusual patterns. The query also computes quartiles (Q1, median, Q3) for distribution context, record count, average sale value, standard deviation for volatility assessment, and ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for anomaly score computation",
  "normal_query": "Calculate weekly sales statistics for each employee with anomaly detection scores and quartile analysis."
}
```

### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 25,
  "question": "How do monthly sales trends compare across different payment types for fiscal period reporting and quarter-over-quarter analysis?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY location_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.location_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.location_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 300\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.location_id) AS partition_stddev,\n        NTILE(5) OVER (PARTITION BY c2.location_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.location_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.location_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.location_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The finance department prepares monthly and quarterly reports comparing payment method performance across fiscal periods to identify trends in customer payment preferences, assess the impact of new payment options, and forecast payment processing costs. The data must align with fiscal calendar months to match other financial reporting. Task: Generate monthly sales statistics segmented by payment type that align with fiscal period boundaries for comparative analysis. Action: The SQL groups transactions by fiscal month (using DATE_TRUNC('month') to standardize all dates to the first day of each month) and payment type, then computes a comprehensive set of metrics: record count showing transaction volume, average transaction value, quartiles (Q1, median, Q3) for distribution analysis, standard deviation for variability, minimum and maximum values for range, and additional summary statistics. The month truncation ensures each payment type's metrics can be easily compared month-o",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for fiscal period comparative analysis",
  "normal_query": "Calculate monthly sales statistics by payment type formatted for fiscal period comparisons with quartile distributions."
}
```

### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 26,
  "question": "What are the daily sales statistics for each customer, including transaction throughput metrics and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 310\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(6) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The business needs to assess transaction volume patterns per customer to optimize system capacity planning and refine loyalty program tiers based on purchasing frequency and consistency. Task: Generate daily sales statistics for each customer that include throughput metrics and quartile distributions. Action: The query aggregates sales data by day and customer identifier, calculates throughput proxies such as record count, rolling averages, and cumulative maximums, and includes days with single transactions to capture all customer activity. Result: A dataset containing daily metrics for each customer with throughput indicators, quartile values (Q1, Q2, Q3), and activity level classifications for capacity and loyalty analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for transaction throughput optimization",
  "normal_query": "Calculate daily sales statistics per customer with transaction throughput indicators and quartile breakdowns."
}
```

### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 27,
  "question": "What are the weekly sales statistics by store location, including payment method trend analysis and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 320\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(7) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The retail operations team needs to identify shifts in payment method preferences (such as credit card versus cash usage) across different store locations to optimize payment terminal deployment and cash management strategies. Task: Generate weekly sales statistics for each location that include payment trend metrics and quartile distributions. Action: The query aggregates sales data by week and location, calculates trend direction indicators and counts of increasing payment patterns to analyze shifts in payment mix, and filters to include only location-weeks with at least 3 transaction records to ensure statistical relevance. Result: A dataset containing weekly metrics for each location with payment trend indicators, quartile values, and activity summaries for terminal planning and cash handling optimization.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for store account payment trend analysis",
  "normal_query": "Calculate weekly sales statistics per location with payment trend indicators and quartile breakdowns."
}
```

### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 28,
  "question": "What are the monthly sales statistics for each employee, with multi-dimensional aggregation and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.employee_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.employee_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 330\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.employee_id) AS partition_stddev,\n        NTILE(8) OVER (PARTITION BY c2.employee_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.employee_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('week', c4.sale_time) AS period,\n    c4.employee_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('week', c4.sale_time), c4.employee_id\nHAVING COUNT(*) >= 2\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The sales management team requires flexible reporting capabilities that allow pivoting sales data by both time period and employee to support ad-hoc performance analysis and commission calculations. Task: Generate monthly sales statistics for each employee with multi-dimensional aggregation structure and quartile distributions. Action: The query aggregates sales data by month and employee identifier, uses both period and employee_id as dimensional attributes to enable pivot table analysis, and includes months where employees have only a single transaction to provide complete coverage. Result: A dataset containing monthly metrics for each employee with multi-dimensional attributes, quartile values, and summary statistics that support flexible pivot analysis and performance reporting.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for multi-dimensional pivot analysis",
  "normal_query": "Calculate monthly sales statistics per employee with multi-dimensional grouping and quartile breakdowns."
}
```

### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 29,
  "question": "What are the daily sales statistics by payment type, including sales funnel stage progression and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.customer_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.customer_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 340\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.customer_id) AS partition_stddev,\n        NTILE(9) OVER (PARTITION BY c2.customer_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.customer_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('month', c4.sale_time) AS period,\n    c4.customer_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('month', c4.sale_time), c4.customer_id\nHAVING COUNT(*) >= 3\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The analytics team needs to understand how payment method preferences evolve throughout the day to identify conversion patterns and optimize checkout flow recommendations at different times. Task: Generate daily sales statistics by payment type that include funnel stage progression indicators and quartile distributions. Action: The query aggregates sales data by day and payment type, calculates trend direction metrics to track stage progression through the day, and filters to include only day-payment type combinations with at least 2 transaction records to ensure meaningful trend detection. Result: A dataset containing daily metrics for each payment type with funnel progression indicators, quartile values, and stage evolution patterns for conversion optimization analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for sales funnel stage progression",
  "normal_query": "Calculate daily sales statistics by payment type with funnel progression metrics and quartile breakdowns."
}
```

### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-2",
  "question_id": 30,
  "question": "What are the weekly sales statistics per customer, with IQR-based outlier detection and quartile distributions?",
  "SQL": "WITH cte_level_1 AS (\n    SELECT \n        *,\n        ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY sale_time DESC) AS rn,\n        DATE_TRUNC('day', sale_time) AS sale_day,\n        DATE_TRUNC('week', sale_time) AS sale_week,\n        EXTRACT(HOUR FROM sale_time) AS sale_hour,\n        EXTRACT(DOW FROM sale_time) AS sale_dow\n    FROM phppos_sales\n    WHERE sale_time >= CURRENT_TIMESTAMP - INTERVAL '365 days'\n),\ncte_level_2 AS (\n    SELECT\n        c1.*,\n        COUNT(*) OVER (PARTITION BY c1.sale_day, c1.sale_id) AS daily_partition_count,\n        AVG(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,\n        SUM(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,\n        FIRST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time) AS first_value,\n        LAST_VALUE(c1.sale_id) OVER (PARTITION BY c1.sale_id ORDER BY c1.sale_time ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_value\n    FROM cte_level_1 c1\n    WHERE c1.rn <= 350\n),\ncte_level_3 AS (\n    SELECT\n        c2.*,\n        LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS prev_value,\n        LEAD(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS next_value,\n        c2.sale_id - LAG(c2.sale_id, 1) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_time) AS delta_value,\n        AVG(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_avg,\n        STDDEV(c2.sale_id) OVER (PARTITION BY c2.sale_id) AS partition_stddev,\n        NTILE(4) OVER (PARTITION BY c2.sale_id ORDER BY c2.sale_id) AS ntile_bucket,\n        RANK() OVER (PARTITION BY c2.sale_day ORDER BY c2.sale_id DESC) AS daily_rank\n    FROM cte_level_2 c2\n),\ncte_level_4 AS (\n    SELECT\n        c3.*,\n        CASE \n            WHEN c3.partition_stddev > 0 THEN (c3.sale_id - c3.partition_avg) / c3.partition_stddev\n            ELSE 0 \n        END AS z_score,\n        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,\n        PERCENT_RANK() OVER (PARTITION BY c3.sale_id ORDER BY c3.sale_id) AS pct_rank,\n        CASE\n            WHEN c3.delta_value > 0 THEN 'Increasing'\n            WHEN c3.delta_value < 0 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM cte_level_3 c3\n)\nSELECT\n    DATE_TRUNC('day', c4.sale_time) AS period,\n    c4.sale_id,\n    COUNT(*) AS record_count,\n    AVG(c4.sale_id) AS avg_value,\n    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.sale_id) AS q1_value,\n    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.sale_id) AS median_value,\n    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.sale_id) AS q3_value,\n    STDDEV(c4.sale_id) AS stddev_value,\n    MIN(c4.sale_id) AS min_value,\n    MAX(c4.sale_id) AS max_value,\n    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,\n    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,\n    AVG(c4.rolling_avg) AS avg_rolling,\n    MAX(c4.cumulative_sum) AS max_cumulative\nFROM cte_level_4 c4\nGROUP BY DATE_TRUNC('day', c4.sale_time), c4.sale_id\nHAVING COUNT(*) >= 1\nORDER BY period DESC, avg_value DESC\nLIMIT 100",
  "evidence": "Situation: The fraud detection and customer experience teams need to identify customers with unusual spending patterns\u2014either abnormally high spenders who may require VIP treatment or anomalous patterns that could indicate fraudulent activity\u2014using statistical quartile-based methods. Task: Generate weekly sales statistics per customer with IQR-style outlier detection and quartile distributions. Action: The query aggregates sales data by week and customer, calculates first quartile (Q1) and third quartile (Q3) using PERCENTILE_CONT functions, applies z-score thresholds above 2 standard deviations to approximate IQR outlier detection methodology, and filters to include only customer-weeks with at least 3 transaction records to ensure statistical validity. Result: A dataset containing weekly metrics for each customer with quartile values, IQR-based outlier flags, trend counts, and statistical indicators for fraud detection and VIP customer identification.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "sale_time",
    "phppos_sales",
    "cte_level_1",
    "cte_level_2",
    "cte_level_3",
    "cte_level_4"
  ],
  "schema_context": {},
  "expected_output": "Aggregated metrics for outlier detection with iqr method",
  "normal_query": "Calculate weekly sales statistics per customer with IQR-style outlier identification and quartile breakdowns."
}
```
