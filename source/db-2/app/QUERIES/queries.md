# Filling Station Retail / POS (phppos) — Query Documentation

## Database Overview

```yaml
db_id: db-2
domain: Filling Station Retail / POS
source: [commercial]
license_type: [Commercial]
license_cost: [NDA]
tables: 7
total_rows: ~7.5K
date_range: 2020-01-01 to 2026-12-31
sql_dialect: PostgreSQL
```

## Purpose

```text
This database supports analytics for filling station and retail point-of-sale (POS) operations.
It models people, employees, items, locations, inventory, and sales transactions. It is designed
to support text-to-SQL training across revenue, inventory, and workforce query types commonly
encountered in convenience store and gas station retail analytics.
```

## Use Case

```text
Target use cases for db-2:
- Sales analytics: daily/weekly revenue by employee, location, or item category
- Performance: employee sales trends, rolling averages, above-average transaction counts
- Inventory: stock levels by location, reorder alerts, item movement
- Operations: multi-location comparison, payment type mix, peak hours
- Product dashboards: margin analysis (unit_price vs cost_price), category performance
```

## Business Value

```text
Retail POS databases represent high-value domains for text-to-SQL because:
- Queries require understanding of multi-location, multi-employee hierarchies
- Data relationships span people → employees → sales → items → locations
- Stakeholders need self-serve analytics (store managers, regional ops, finance)
- Evidence bridges natural-language questions to schema-grounded SQL.
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
Key domain concepts required to write correct queries against this database:

PEOPLE AND EMPLOYEES:
- phppos_people: base person record (person_id); employees extend via phppos_employees
- phppos_employees: person_id PK/FK; username, balance; deleted=1 means soft-deleted
- phppos_employees_locations: many-to-many; which employees work at which locations

ITEMS AND INVENTORY:
- phppos_items: products; cost_price (wholesale), unit_price (retail); category for grouping
- phppos_location_items: inventory per location; quantity is stock on hand
- is_serialized, is_service: item type flags; deleted=1 means discontinued

LOCATIONS:
- phppos_locations: store sites; default_tax_1..5 for tax rates; stock_alert_email for reorders
- receive_stock_alert: '0' or '1' for low-stock notifications

SALES:
- phppos_sales: sale_id, employee_id, sale_time, customer_id, payment_type, location_id
- sale_time: transaction timestamp; group by DATE_TRUNC for daily/weekly aggregation
- Rolling averages and performance_category (Above/Below Average) used for trend analysis.
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
  "evidence": "The query groups transactions by date and employee, then computes each employee's overall average transaction value as a benchmark. It applies a 7-row rolling window ordered by date to calculate smoothed averages, compares individual transactions against the employee's benchmark to count above-average performance, retains only the 100 most recent transactions per employee to focus on current trends, and excludes days with single transactions to avoid statistical noise. A dataset containing daily metrics for each employee showing their ro",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups purchases by month and customer, then calculates quartiles by segmenting spend into sextiles (six equal groups). It computes z-scores for each transaction and flags those exceeding two standard deviations as outliers. To detect momentum, it derives trend direction by comparing consecutive transaction amounts and counts how many show increases. The query limits each customer to their 70 most recent data points for manageability and requires at least three transactions per month per customer to ensure s",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups sales by date and employee, then applies PERCENTILE_CONT to compute Q1 (25th percentile), median (50th percentile), and Q3 (75th percentile) for robust statistical summaries. It calculates a 7-row rolling average to smooth daily volatility, segments transactions into septiles (seven equal groups) to classify distribution spread, and permits single-transaction days to accommodate newly hired employees who are ramping up. Daily performance metrics for",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups transactions by week and payment type, then computes quartiles to understand the spread of transaction amounts within each payment method. It applies an 8-row rolling window to smooth weekly fluctuations, segments data into octiles (eight equal groups) for finer distribution analysis, flags statistical outliers, counts transactions that increase compared to prior periods to identify momentum, and requires at least two records per week per payme",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups sales by month and location, then calculates Q1, median, and Q3 to profile the spending distribution at each site. It computes standard deviation to quantify sales variability, which helps distinguish consistently performing stores from volatile ones. A 9-row rolling window smooths multi-month trends, and the data is segmented into noniles (nine equal groups) for granular dis",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query aggregates sales transactions by day and employee, extracts temporal features (hour of day and day of week) to provide context, calculates quartile boundaries (25th, 50th, 75th percentiles) for distribution analysis, computes a 10-day rolling average to smooth short-term fluctuations, applies z-score methodology to flag statistical outliers beyond normal variance, and accommodates employees who may have only a single transaction on certain days. A dataset containing daily performance metrics for each employee including quartile values for understanding sales distribution,",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups sales data by month and customer, uses window functions LAG and LEAD to compute differences between consecutive months (measuring changes in purchase frequency and amounts), derives trend direction indicators (increasing, stable, or decreasing), calculates quartile boundaries for spend distribution analysis, and filters to include only customers with at least 3 months of purchase history to ensure meaningful trend detection. A dataset containing monthly metrics for each customer inclu",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query aggregates transactions by day and payment type, applies z-score statistical methodology to flag days where transaction volumes or amounts fall outside normal variance thresholds, calculates quartile boundaries to establish baseline expectations for each payment type, derives trend direction indicators to capture momentum patterns, and requires at least 2 transaction records per group to enable meaningful statistical comparison. A dataset containing daily metrics",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups sales transactions by week and customer, uses the ROW_NUMBER window function to establish recency ordering (identifying most recent purchases), ranks customers by cumulative spending to determine monetary value tiers, calculates quartile boundaries for spend distribution analysis, computes rolling averages to smooth weekly volatility, and filters to include only customers with at least 3 weeks of purchase activity to ensure statistically meaningful metri",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query aggregates sales by month and employee, calculates an increasing_count metric that tracks cumulative months of activity to enable cohort-based comparisons, derives trend_direction indicators to classify performance momentum (improving, stable, declining), computes quartile boundaries to enable relative performance assessment against peers, and accommodates single-record months to include newly hired employees in the analysis without distorting statistical",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups transactions by calendar day and location, computes delta_value to measure day-over-day change in sales velocity, calculates quartile boundaries (Q1, Q2, Q3) for the distribution, identifies outliers beyond typical ranges, and filters to locations with at least 2 days of data to ensure meaningful trend analysis. A dataset showing daily performance metrics for each location\u2014acceleration indicators measuring growth momentum, quartile values showing the sales distribution, and outlier counts flagging anomalous days that may require investigation.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups transactions by calendar week and employee, applies PERCENT_RANK to determine each employee's relative position within their cohort, uses DENSE_RANK for sequential performance ordering without gaps, calculates quartile boundaries to segment the sales distribution, and requires at least 3 weeks of data per employee to establish reliable patterns. A dataset showing weekly performance metrics for each employee\u2014benchmark rankings showing relative standing among peers, quartile values revealing the distribution of their sales, an",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups transactions by calendar month and payment type (credit card, cash, mobile wallet, etc.), computes a rolling average using a ROWS BETWEEN window frame that looks backward across multiple months to smooth volatility, calculates quartile boundaries for the distribution, and requires at least 2 months of data per payment type to establish baseline trends. A dataset showing monthly performance metrics for each payment type\u2014rolling averages that reveal smoothed trend lines free from s",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups transactions by calendar day and customer, extracts the sale_hour timestamp component to identify when each transaction occurred, determines peak shopping hours for each customer segment through frequency analysis, calculates quartile boundaries for the sales distribution, and includes even single-transaction days to capture all customer activity patterns without imposing minimum thresholds. A dataset showing daily performance metrics for each customer\u2014peak hour indicators",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups transactions by calendar week and location, computes cumulative_sum to track running total revenue as a proxy for long-term value generation, calculates max_cumulative to identify peak value contribution periods, applies quartile segmentation to the distribution, and requires at least 3 weeks of data per location to establish meaningful cumulative patterns rather than isolated events. A dataset showing weekly performance metrics for each location\u2014LTV-style rankings that priori",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups sales data by month and employee identifier, applies window functions to compute trend_direction and delta_value metrics for growth analysis, filters records to the most recent 365 days to enable valid year-over-year comparisons, and accommodates months where an employee may have only a single transaction record. A dataset containing monthly sales metrics for each employee, including growth direction indicators, percentage or absolute delta values from the prior year, and quartile positions within their peer group.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups transaction data by calendar day and payment_type, structures output using period (date/time dimension) and payment_type as the two heatmap axes, calculates quartile distributions to enable color-coding intensity, counts trend occurrences for velocity indicators, and filters to groups with at least 2 transaction records to ensure statistical relevance. A heatmap-ready dataset with daily metrics for each payment type, including dimensional coordinates for plotting, quartile values for color intensity mapping, and trend counts s",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups sales transactions by calendar week and customer identifier, applies PERCENT_RANK window function to show each customer's relative position in the weekly spending distribution, uses PERCENTILE_CONT to calculate quartile boundaries (25th, 50th, 75th percentiles) for the week, and filters to groups containing at least 3 transaction records to ensure meaningful statistical calculations. A dataset of weekly metrics for each customer showing their running percentile rank within that week's customer base, quartile cl",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups sales data by calendar month and location identifier, uses DENSE_RANK window function to rank locations by cross-sell metrics within each month, calculates partition-specific statistics to enable peer comparisons across similar location types or regions, computes quartile distributions to classify high and low performers, and filters to groups with at least 3 transaction records for statistical validity. A dataset of monthly metrics for each location including cross-sell effectiveness indicators (su",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query groups transaction records by calendar day and employee identifier, applies LAG and LEAD window functions to sequence transactions chronologically and identify gaps or reversals, leverages the deleted flag column (if present) to track soft-deleted or voided transactions separately from completed sales, calculates quartile distributions for transaction volumes and values, and includes all transaction states to provide complete forensic visibil",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query filters to include only groups with at least 2 records to ensure statistical validi",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query also computes quartiles (Q1, median, Q3) to understand spending distribution and includes record count, average, and range metrics. Only customers with at least 3",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query also includes quartile calculations (Q1, median, Q3), record coun",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query also computes quartiles (Q1, median, Q3) for distribution context, record count, average sale value, standard deviation for volatility assessment, and",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The month truncation ensures each payment type's metrics can be easily compared month-o",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query aggregates sales data by day and customer identifier, calculates throughput proxies such as record count, rolling averages, and cumulative maximums, and includes days with single transactions to capture all customer activity. A dataset containing daily metrics for each customer with throughput indicators, quartile values (Q1, Q2, Q3), and activity level classifications for capacity and loyalty analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query aggregates sales data by week and location, calculates trend direction indicators and counts of increasing payment patterns to analyze shifts in payment mix, and filters to include only location-weeks with at least 3 transaction records to ensure statistical relevance. A dataset containing weekly metrics for each location with payment trend indicators, quartile values, and activity summaries for terminal planning and cash handling optimization.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query aggregates sales data by month and employee identifier, uses both period and employee_id as dimensional attributes to enable pivot table analysis, and includes months where employees have only a single transaction to provide complete coverage. A dataset containing monthly metrics for each employee with multi-dimensional attributes, quartile values, and summary statistics that support flexible pivot analysis and performance reporting.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query aggregates sales data by day and payment type, calculates trend direction metrics to track stage progression through the day, and filters to include only day-payment type combinations with at least 2 transaction records to ensure meaningful trend detection. A dataset containing daily metrics for each payment type with funnel progression indicators, quartile values, and stage evolution patterns for conversion optimization analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
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
  "evidence": "The query aggregates sales data by week and customer, calculates first quartile (Q1) and third quartile (Q3) using PERCENTILE_CONT functions, applies z-score thresholds above 2 standard deviations to approximate IQR outlier detection methodology, and filters to include only customer-weeks with at least 3 transaction records to ensure statistical validity. A dataset containing weekly metrics for each customer with quartile values, IQR-based outlier flags, trend counts, and statistical indicators for fraud detection and VIP customer identification.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [],
  "schema_context": {},
  "expected_output": "Aggregated metrics for outlier detection with iqr method",
  "normal_query": "Calculate weekly sales statistics per customer with IQR-style outlier identification and quartile breakdowns."
}
```


