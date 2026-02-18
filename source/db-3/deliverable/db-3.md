# ID: db-3 - Name: Hierarchical Orders (LinkWay)

This document provides comprehensive documentation for database db-3, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**, representing real-world enterprise implementations.

---

## Table of Contents

### Database Documentation

1. [Database Overview](#database-overview)
   - Description and key features
   - Business context and use cases
   - Platform compatibility
   - Data sources

2. [Database Schema Documentation](#database-schema-documentation)
   - Complete schema overview
   - All tables with detailed column definitions
   - Indexes and constraints
   - Entity-Relationship diagrams
   - Table relationships

3. [Data Dictionary](#data-dictionary)
   - Comprehensive column-level documentation
   - Data types and constraints
   - Column descriptions and business context

### SQL Queries (30 Production Queries)

1. [Query 1: I want to see how order total amounts vary over the past year, with rolling averages and outlier counts broken down by day and seller code.](#query-1)
    - **Use Case:** I want to see how order total amounts vary over the past year, with rolling averages and outlier counts broken down by day and seller code.
    - *What it does:* Order managers need to monitor how seller total amounts fluctuate over time to identify unusual patterns and flag potential issues that require attent...
    - *Business Value:* Aggregated metrics grouped by day and seller_id

2. [Query 2: Can you show me weekly order total amount statistics grouped by order status bucket? I need quartiles, outliers, and the count of readings that are trending upward.](#query-2)
    - **Use Case:** Can you show me weekly order total amount statistics grouped by order status bucket? I need quartiles, outliers, and the count of readings that are trending upward.
    - *What it does:* Business analysts want to compare total_amount distribution patterns across different order status buckets to understand how orders behave differently...
    - *Business Value:* Aggregated metrics grouped by week and status

3. [Query 3: Give me monthly order total amount summaries by seller — I need quartiles, median, outlier count, and a rolling average.](#query-3)
    - **Use Case:** Give me monthly order total amount summaries by seller — I need quartiles, median, outlier count, and a rolling average.
    - *What it does:* Fleet and operations managers require monthly reporting to track long-term total_amount trends for each seller and identify seasonal patterns or cycli...
    - *Business Value:* Aggregated metrics grouped by month and seller_id

4. [Query 4: I need a daily order total amount breakdown by order status — specifically how many outliers there are, how many readings are increasing, and what the maximum cumulative sum is.](#query-4)
    - **Use Case:** I need a daily order total amount breakdown by order status — specifically how many outliers there are, how many readings are increasing, and what the maximum cumulative sum is.
    - *What it does:* Daily operational dashboards segmented by order status help warehouse and fulfillment teams identify whether certain processing stages (e.g., pending...
    - *Business Value:* Aggregated metrics grouped by day and status

5. [Query 5: Show me weekly order total amount metrics per seller — I want record count, quartiles, standard deviation, and the count of readings that are increasing.](#query-5)
    - **Use Case:** Show me weekly order total amount metrics per seller — I want record count, quartiles, standard deviation, and the count of readings that are increasing.
    - *What it does:* Weekly performance reviews at the seller level help account managers compare variability (measured by standard deviation) and trend momentum across th...
    - *Business Value:* Aggregated metrics grouped by week and seller_id

6. [Query 6: I need daily order total amount statistics broken down by order status bucket, including quartiles, rolling averages, and outlier detection.](#query-6)
    - **Use Case:** I need daily order total amount statistics broken down by order status bucket, including quartiles, rolling averages, and outlier detection.
    - *What it does:* The operations team monitors order processing across different status categories (pending, shipped, delivered, etc.) and needs to identify anomalies i...
    - *Business Value:* Aggregated metrics grouped by day and status

7. [Query 7: I need monthly order total amount analysis by seller, showing quartiles, minimum and maximum values, outlier count, and cumulative sum.](#query-7)
    - **Use Case:** I need monthly order total amount analysis by seller, showing quartiles, minimum and maximum values, outlier count, and cumulative sum.
    - *What it does:* The business intelligence team performs monthly seller performance reviews and needs to compare order value distributions across the entire seller net...
    - *Business Value:* Aggregated metrics grouped by month and seller_id

8. [Query 8: Show me daily order total amounts by seller with gaps between readings and sequential differences, plus quartile distributions.](#query-8)
    - **Use Case:** Show me daily order total amounts by seller with gaps between readings and sequential differences, plus quartile distributions.
    - *What it does:* Financial analysts need to track how individual seller order volumes change day-over-day to detect sudden spikes or drops that might indicate market o...
    - *Business Value:* Aggregated metrics grouped by day and status

9. [Query 9: I need daily order total amounts grouped by order status with anomaly detection using z-scores, quartiles, and trend counts.](#query-9)
    - **Use Case:** I need daily order total amounts grouped by order status with anomaly detection using z-scores, quartiles, and trend counts.
    - *What it does:* The quality assurance team monitors order processing patterns across different status categories to quickly identify unusual total_amount behaviors th...
    - *Business Value:* Aggregated metrics grouped by week and seller_id

10. [Query 10: I want weekly order total amount statistics by seller with recency and frequency scoring, quartiles, and rolling averages.](#query-10)
    - **Use Case:** I want weekly order total amount statistics by seller with recency and frequency scoring, quartiles, and rolling averages.
    - *What it does:* The seller management team uses recency-frequency-monetary (RFM) style analysis to prioritize which sellers require attention for relationship managem...
    - *Business Value:* Aggregated metrics grouped by month and status

11. [Query 11: What are the monthly order total amount statistics by order status, including cohort-style retention metrics and quartile distributions?](#query-11)
    - **Use Case:** What are the monthly order total amount statistics by order status, including cohort-style retention metrics and quartile distributions?
    - *What it does:* The business needs to understand how different order status categories (such as delivered, cancelled, or in-transit) behave over time in terms of tota...
    - *Business Value:* Aggregated metrics grouped by day and seller_id

12. [Query 12: What are the daily order total amount statistics per seller, including second-order change detection, quartiles, and outlier counts?](#query-12)
    - **Use Case:** What are the daily order total amount statistics per seller, including second-order change detection, quartiles, and outlier counts?
    - *What it does:* Sudden accelerations or decelerations in a seller's daily order total amounts can signal operational issues, fraud, or market opportunities that requi...
    - *Business Value:* Aggregated metrics grouped by week and status

13. [Query 13: What are the weekly order total amount statistics by order status, with cross-category percentile benchmarking and quartile analysis?](#query-13)
    - **Use Case:** What are the weekly order total amount statistics by order status, with cross-category percentile benchmarking and quartile analysis?
    - *What it does:* Different order statuses (such as completed, pending, or cancelled) represent distinct operational states, and understanding how total order amounts a...
    - *Business Value:* Aggregated metrics grouped by month and seller_id

14. [Query 14: What are the monthly order total amount statistics per seller, including weighted moving averages, quartiles, and trend pattern counts?](#query-14)
    - **Use Case:** What are the monthly order total amount statistics per seller, including weighted moving averages, quartiles, and trend pattern counts?
    - *What it does:* Monthly order total amounts for individual sellers often contain noise from seasonal variations, one-time events, or data irregularities that obscure...
    - *Business Value:* Aggregated metrics grouped by day and status

15. [Query 15: What are the daily order total amount statistics by order status, including peak period identification, operational efficiency metrics, and quartiles?](#query-15)
    - **Use Case:** What are the daily order total amount statistics by order status, including peak period identification, operational efficiency metrics, and quartiles?
    - *What it does:* Understanding when order total amounts reach peak levels within each order status category is critical for capacity planning, resource allocation, and...
    - *Business Value:* Aggregated metrics grouped by week and seller_id

16. [Query 16: What are the weekly order totals per seller with lifetime value metrics, quartiles, and cumulative sum?](#query-16)
    - **Use Case:** What are the weekly order totals per seller with lifetime value metrics, quartiles, and cumulative sum?
    - *What it does:* The business needs to prioritize sellers based on their total transaction activity over time to optimize maintenance scheduling and resource allocatio...
    - *Business Value:* Aggregated metrics grouped by month and status

17. [Query 17: How do monthly order totals by order status compare year-over-year with growth rates and quartiles?](#query-17)
    - **Use Case:** How do monthly order totals by order status compare year-over-year with growth rates and quartiles?
    - *What it does:* The business needs to understand how order volume patterns evolve across different order statuses (e.g., delivered, cancelled, processing) from one ye...
    - *Business Value:* Aggregated metrics grouped by day and seller_id

18. [Query 18: What are the daily order totals per seller formatted for heatmap visualization with quartiles and outliers?](#query-18)
    - **Use Case:** What are the daily order totals per seller formatted for heatmap visualization with quartiles and outliers?
    - *What it does:* The business requires a visual representation of total_amount patterns across time and sellers to gain quick, fleet-wide operational insights. Heatmap...
    - *Business Value:* Aggregated metrics grouped by week and status

19. [Query 19: What are the weekly order totals by status showing running percentile distributions, quartiles, and trend patterns?](#query-19)
    - **Use Case:** What are the weekly order totals by status showing running percentile distributions, quartiles, and trend patterns?
    - *What it does:* The business needs to understand how order amounts distribute within each order status category over time. Running percentiles reveal whether order va...
    - *Business Value:* Aggregated metrics grouped by month and seller_id

20. [Query 20: What are the monthly order totals per seller with sequential correlation patterns, quartiles, and rolling averages?](#query-20)
    - **Use Case:** What are the monthly order totals per seller with sequential correlation patterns, quartiles, and rolling averages?
    - *What it does:* The business needs to understand how current order amounts relate to previous periods across the seller base. Cross-correlation pattern analysis revea...
    - *Business Value:* Aggregated metrics grouped by day and status

21. [Query 21: What are the daily order total amount statistics by order status, including status transition analysis, quartile distributions, and outlier counts?](#query-21)
    - **Use Case:** What are the daily order total amount statistics by order status, including status transition analysis, quartile distributions, and outlier counts?
    - *What it does:* The finance team needs to perform forensic analysis on how order total amounts transition between different trend states (Increasing, Decreasing, Stab...
    - *Business Value:* Aggregated metrics grouped by week and seller_id

22. [Query 22: What are the weekly order total amount statistics per seller with complete dashboard metrics including quartiles and multi-dimensional aggregations?](#query-22)
    - **Use Case:** What are the weekly order total amount statistics per seller with complete dashboard metrics including quartiles and multi-dimensional aggregations?
    - *What it does:* The operations dashboard requires a unified data source that consolidates all key performance metrics for monitoring seller activity across the entire...
    - *Business Value:* Aggregated metrics grouped by month and status

23. [Query 23: What are the monthly order total amount statistics by order status with sequential pattern analysis and quartile distributions?](#query-23)
    - **Use Case:** What are the monthly order total amount statistics by order status with sequential pattern analysis and quartile distributions?
    - *What it does:* The analytics team needs to understand how order total amounts evolve sequentially over time within each order status category to identify temporal pa...
    - *Business Value:* Aggregated metrics grouped by day and seller_id

24. [Query 24: What are the daily order total amount statistics per seller with concentration indices, quartile distributions, and outlier counts?](#query-24)
    - **Use Case:** What are the daily order total amount statistics per seller with concentration indices, quartile distributions, and outlier counts?
    - *What it does:* Management needs to assess market concentration and identify whether order activity is concentrated among a few top sellers or distributed evenly, whi...
    - *Business Value:* Aggregated metrics grouped by week and status

25. [Query 25: What are the weekly order total amount statistics by order status with statistical anomaly scores, quartile distributions, and trend counts?](#query-25)
    - **Use Case:** What are the weekly order total amount statistics by order status with statistical anomaly scores, quartile distributions, and trend counts?
    - *What it does:* The quality assurance team needs a prioritization system to identify which order status categories exhibit unusual total amount patterns that warrant...
    - *Business Value:* Aggregated metrics grouped by month and seller_id

26. [Query 26: What are the monthly order totals for each seller, broken down with quartiles for fiscal period comparison?](#query-26)
    - **Use Case:** What are the monthly order totals for each seller, broken down with quartiles for fiscal period comparison?
    - *What it does:* The finance team needs to compare seller performance across fiscal periods (month-over-month and quarter-over-quarter) for budgeting and planning cycl...
    - *Business Value:* Aggregated metrics grouped by day and status

27. [Query 27: What are the daily order totals by order status, including throughput metrics, quartiles, and rolling averages?](#query-27)
    - **Use Case:** What are the daily order totals by order status, including throughput metrics, quartiles, and rolling averages?
    - *What it does:* Operations teams need to monitor order throughput and capacity utilization across different status categories (pending, processing, shipped, delivered...
    - *Business Value:* Aggregated metrics grouped by week and seller_id

28. [Query 28: What are the weekly order totals per seller with cumulative trends, quartiles, and activity rankings?](#query-28)
    - **Use Case:** What are the weekly order totals per seller with cumulative trends, quartiles, and activity rankings?
    - *What it does:* Sales leadership needs to track how each seller's total order value accumulates over time to identify growth trajectories, seasonal patterns, and top...
    - *Business Value:* Aggregated metrics grouped by month and status

29. [Query 29: What are the monthly order totals by order status with multi-dimensional aggregations and quartiles?](#query-29)
    - **Use Case:** What are the monthly order totals by order status with multi-dimensional aggregations and quartiles?
    - *What it does:* Business analysts require flexible data structures that support dynamic pivoting and slicing across time periods and order statuses for ad-hoc reporti...
    - *Business Value:* Aggregated metrics grouped by day and seller_id

30. [Query 30: What are the weekly order totals by order status with IQR-based outlier detection, quartiles, and trend metrics?](#query-30)
    - **Use Case:** What are the weekly order totals by order status with IQR-based outlier detection, quartiles, and trend metrics?
    - *What it does:* Data quality teams need robust outlier detection methods that complement z-score approaches, particularly for skewed distributions where the Interquar...
    - *Business Value:* Aggregated metrics grouped by week and status

### Additional Information

- [Usage Instructions](#usage-instructions)
- [Platform Compatibility](#platform-compatibility)
- [Business Context](#business-context)

---

## Business Context

**Enterprise-Grade Database System**

This database and all associated queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**. These are not academic examples or toy databases—they represent real-world implementations that power critical business operations, serve paying customers, and generate significant revenue.

**What This Means:**

- **Production-Ready**: All queries have been tested and optimized in production environments
- **Business-Critical**: These queries solve real business problems for revenue-generating companies
- **Scalable**: Designed to handle enterprise-scale data volumes and query loads
- **Proven**: Each query addresses a specific business need that has been validated through actual customer use

**Business Value:**

Every query in this database was created to solve a specific business problem for a company generating $1M+ ARR. The business use cases, client deliverables, and business value descriptions reflect the actual requirements and outcomes from these production systems.

---

## Database Overview

LinkWay Live database export with hierarchical order structure. Structured export from PostgreSQL (Django backend) with schema and data for local analysis, backups, and migrations.

- Hierarchical order management
- Django backend schema
- Full schema and data export

- **PostgreSQL**: Full support
- **, **: Compatible with Delta Lake
- **, **: Full support

---

---

### Data Dictionary

This section provides a comprehensive data dictionary for all tables in the database, including column names, data types, constraints, and descriptions. Tables are organized by functional category for easier navigation.

See `docs/SCHEMA.md` for table relationships. Includes `orders_order` view and hierarchical order tables.

---

---

---

## SQL Queries

This database includes **30 production SQL queries**, each designed to solve specific business problems for companies with $1M+ ARR. Each query includes:

- **Business Use Case**: The specific business problem this query solves
- **Description**: Technical explanation of what the query does
- **Client Deliverable**: What output or report this query generates
- **Business Value**: The business impact and value delivered
- **Complexity**: Technical complexity indicators
- **SQL Code**: Complete, production-ready SQL query

---

## Query 1: I want to see how order total amounts vary over the past year, with rolling averages and outlier counts broken down by day and seller code. {#query-1}

**Use Case:** **I want to see how order total amounts vary over the past year, with rolling averages and outlier counts broken down by day and seller code.**

**Description:** Order managers need to monitor how seller total amounts fluctuate over time to identify unusual patterns and flag potential issues that require attention. Each seller has a unique seller_id identifier, and the total_amount field captures the order value for analysis. Produce daily aggregated total_amount statistics per seller, including rolling averages, outlier detection, and trend classification. The query constructs four CTEs: first, it retains the 60 most recent order records per seller to focus on recent activity; second, it calculates a 5-row rolling average to smooth short-term fluctuations; third, it flags outliers by computing z-scores and marking any total_amount that exceeds 2 standard deviations from the mean (setting z-score to 0 when standard deviation is zero to prevent division errors); fourth, it classifies each reading as Increasing, Decreasing, or Stable by comparing consecutive values. The final aggregation groups by day and seller_id, requi

**Business Value:** Aggregated metrics grouped by day and seller_id

**Complexity:** challenging

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

---

## Query 2: Can you show me weekly order total amount statistics grouped by order status bucket? I need quartiles, outliers, and the count of readings that are trending upward. {#query-2}

**Use Case:** **Can you show me weekly order total amount statistics grouped by order status bucket? I need quartiles, outliers, and the count of readings that are trending upward.**

**Description:** Business analysts want to compare total_amount distribution patterns across different order status buckets to understand how orders behave differently depending on their processing stage or fulfillment state. Produce weekly total_amount statistics segmented by status bucket, including quartiles, outlier identification, and trend direction counts. The query groups orders by week and status, then segments the total_amount into sextiles (six equal groups) within each status bucket to understand distribution shape. It flags statistical outliers by calculating z-scores and marking any value exceeding 2 standard deviations from the bucket mean. Using window functions LAG and LEAD, it compares each reading with its predecessor and successor to classify it as Increasing, Decreasing, or Stable. The query filters out sparse status buckets containing fewer than 3 records to ensure meaningful statistical analysis. Weekly metrics per status bucket showing quartiles,

**Business Value:** Aggregated metrics grouped by week and status

**Complexity:** challenging

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

---

## Query 3: Give me monthly order total amount summaries by seller — I need quartiles, median, outlier count, and a rolling average. {#query-3}

**Use Case:** **Give me monthly order total amount summaries by seller — I need quartiles, median, outlier count, and a rolling average.**

**Description:** Fleet and operations managers require monthly reporting to track long-term total_amount trends for each seller and identify seasonal patterns or cyclical behavior that may inform inventory planning and demand forecasting. Produce monthly total_amount summaries per seller including quartiles, median, outlier detection, and rolling average. The query groups orders by month and seller_id, then applies PERCENTILE_CONT aggregate functions to calculate the first quartile (Q1), median (Q2), and third quartile (Q3) for distribution analysis. It computes a 6-row rolling average to smooth month-to-month volatility and reveal underlying trends. To manage memory and computational performance, the query limits analysis to the 80 most recent order records per seller. It allows single-record months for sparse sellers to avoid excluding important low-volume accounts. Outliers are identified using z-score methodology, flagging values more than 2 standard deviations from the sel

**Business Value:** Aggregated metrics grouped by month and seller_id

**Complexity:** challenging

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

---

## Query 4: I need a daily order total amount breakdown by order status — specifically how many outliers there are, how many readings are increasing, and what the maximum cumulative sum is. {#query-4}

**Use Case:** **I need a daily order total amount breakdown by order status — specifically how many outliers there are, how many readings are increasing, and what the maximum cumulative sum is.**

**Description:** Daily operational dashboards segmented by order status help warehouse and fulfillment teams identify whether certain processing stages (e.g., pending review vs. shipped) exhibit more anomalies or volatility that could signal bottlenecks or quality issues. Produce daily total_amount statistics by order status including outlier count, increasing-trend count, and peak cumulative sum. The query groups orders by day and status, then computes a running cumulative sum of total_amount within each status category to track order volume accumulation throughout the day. It applies a 7-row rolling window to calculate moving statistics and smooth noise. Orders are segmented into octiles (eight equal groups) within each status to understand distributional characteristics. Trend direction is derived by calculating the difference between consecutive total_amount readings; when the prior value is missing (first record in a sequence), the reading is classified as Stable by defaul

**Business Value:** Aggregated metrics grouped by day and status

**Complexity:** challenging

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

---

## Query 5: Show me weekly order total amount metrics per seller — I want record count, quartiles, standard deviation, and the count of readings that are increasing. {#query-5}

**Use Case:** **Show me weekly order total amount metrics per seller — I want record count, quartiles, standard deviation, and the count of readings that are increasing.**

**Description:** Weekly performance reviews at the seller level help account managers compare variability (measured by standard deviation) and trend momentum across the entire seller portfolio to prioritize follow-up and relationship management activities. Produce weekly total_amount metrics per seller including record count, quartiles, standard deviation, and increasing-trend count. The query groups orders by week and seller_id, calculating standard deviation to quantify the dispersion and volatility of total_amount values for each seller. It counts the number of readings classified as Increasing by comparing each value with the previous period using window functions. To optimize performance and focus on recent behavior, the query limits analysis to the 60 most recent order records per seller. Sellers are ranked by cumulative total_amount sum to enable prioritization of high-value accounts in subsequent reporting and review processes. Quartiles (Q1, median, Q3) are computed to

**Business Value:** Aggregated metrics grouped by week and seller_id

**Complexity:** challenging

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

---

## Query 6: I need daily order total amount statistics broken down by order status bucket, including quartiles, rolling averages, and outlier detection. {#query-6}

**Use Case:** **I need daily order total amount statistics broken down by order status bucket, including quartiles, rolling averages, and outlier detection.**

**Description:** The operations team monitors order processing across different status categories (pending, shipped, delivered, etc.) and needs to identify anomalies in daily order values within specific status buckets to maintain quality control and detect processing issues early. Generate comprehensive daily total_amount statistics for each order status, including quartile distributions, rolling averages, and outlier detection metrics. The SQL groups orders by calendar day and order status, extracts hour and day-of-week for temporal context, calculates z-scores to identify statistical outliers (handling zero standard deviation cases by substituting zero to prevent division errors), computes a 5-row rolling average to smooth short-term fluctuations, and requires at least 2 records per group to ensure meaningful statistics. A dataset containing daily metrics for each order status—first, second (median), and third quartiles, a 5-day rolling average, and a count of outlie

**Business Value:** Aggregated metrics grouped by day and status

**Complexity:** challenging

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

---

## Query 7: I need monthly order total amount analysis by seller, showing quartiles, minimum and maximum values, outlier count, and cumulative sum. {#query-7}

**Use Case:** **I need monthly order total amount analysis by seller, showing quartiles, minimum and maximum values, outlier count, and cumulative sum.**

**Description:** The business intelligence team performs monthly seller performance reviews and needs to compare order value distributions across the entire seller network, identifying both typical ranges and exceptional patterns to support commission calculations and seller tier classifications. Generate monthly total_amount statistics for each seller including quartile distributions, range boundaries, outlier counts, and cumulative activity totals. The SQL groups orders by month and seller_id, captures the minimum and maximum total_amount to define the value range for each seller, flags outliers using z-scores greater than 2 to identify unusually high or low orders, limits analysis to the most recent 80 data points per seller to focus on current patterns, calculates PERCENT_RANK to show relative position within the seller's distribution, and uses LAST_VALUE with proper window framing to ensure accurate retrieval of the final cumulative sum in each partition. A monthly

**Business Value:** Aggregated metrics grouped by month and seller_id

**Complexity:** challenging

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

---

## Query 8: Show me daily order total amounts by seller with gaps between readings and sequential differences, plus quartile distributions. {#query-8}

**Use Case:** **Show me daily order total amounts by seller with gaps between readings and sequential differences, plus quartile distributions.**

**Description:** Financial analysts need to track how individual seller order volumes change day-over-day to detect sudden spikes or drops that might indicate market opportunities, operational problems, or fraudulent activity patterns. Generate daily total_amount statistics for each seller that highlight sequential changes and distribution characteristics. The SQL groups orders by calendar day and seller_id, uses the LAG window function to compute the difference between consecutive daily readings (with the first row per seller naturally having no prior value), derives trend direction (increasing, decreasing, or stable) from that sequential change, and employs both LAG and LEAD to capture previous and next day values for context. Gap analysis is performed implicitly through timestamp-based ordering of consecutive records. A daily metrics dataset for each seller showing sequential differences from the prior day, trend direction indicators, previous and next day values, an

**Business Value:** Aggregated metrics grouped by day and status

**Complexity:** challenging

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

---

## Query 9: I need daily order total amounts grouped by order status with anomaly detection using z-scores, quartiles, and trend counts. {#query-9}

**Use Case:** **I need daily order total amounts grouped by order status with anomaly detection using z-scores, quartiles, and trend counts.**

**Description:** The quality assurance team monitors order processing patterns across different status categories to quickly identify unusual total_amount behaviors that might signal system errors, pricing mistakes, or fraud, with different status buckets (pending, processing, shipped, delivered) having distinct expected value patterns. Generate daily total_amount statistics for each order status incorporating statistical anomaly detection, distribution metrics, and directional trend analysis. The SQL groups orders by calendar day and order status, flags anomalies where total_amount deviates more than 2 standard deviations from the partition mean, safely handles zero standard deviation cases to avoid mathematical errors, segments the distribution into octiles for granular analysis, and computes metrics over a 7-row rolling window to capture weekly patterns. The query also counts records showing increasing trends versus those showing decreasing or stable patterns. A dail

**Business Value:** Aggregated metrics grouped by week and seller_id

**Complexity:** challenging

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

---

## Query 10: I want weekly order total amount statistics by seller with recency and frequency scoring, quartiles, and rolling averages. {#query-10}

**Use Case:** **I want weekly order total amount statistics by seller with recency and frequency scoring, quartiles, and rolling averages.**

**Description:** The seller management team uses recency-frequency-monetary (RFM) style analysis to prioritize which sellers require attention for relationship management, support allocation, or compliance review, combining how recently and how frequently each seller has been active with their order value patterns. Generate weekly total_amount statistics for each seller incorporating recency and frequency scoring alongside distribution and trend metrics. The SQL groups orders by calendar week and seller_id, assigns ROW_NUMBER in descending date order to create a recency score (where 1 represents the most recent activity), uses the record count within each week as a frequency proxy indicating seller activity level, ranks sellers by cumulative order sum to identify top performers, and computes a 6-row rolling average to smooth weekly volatility. The query requires at least 3 records per group to ensure statistical reliability. A weekly summary for each seller showing tota

**Business Value:** Aggregated metrics grouped by month and status

**Complexity:** challenging

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

---

## Query 11: What are the monthly order total amount statistics by order status, including cohort-style retention metrics and quartile distributions? {#query-11}

**Use Case:** **What are the monthly order total amount statistics by order status, including cohort-style retention metrics and quartile distributions?**

**Description:** The business needs to understand how different order status categories (such as delivered, cancelled, or in-transit) behave over time in terms of total order amounts. Treating each status as a cohort enables retention-style analysis to compare lifecycle patterns and identify which statuses show growth or decline month-over-month. Generate monthly statistics of total order amounts segmented by order status, incorporating cohort-style retention metrics and quartile distributions to reveal behavioral patterns. The SQL query treats each order status as a distinct cohort and aggregates total_amount as the key metric. It limits the dataset to 90 data points per status to ensure manageability. The query calculates increasing_count to track how many periods show growth (similar to retention cohorts) and trend_direction to indicate whether amounts are rising or falling. Results are ordered by time period and average value to prioritize recent and prominent cohorts. Quar

**Business Value:** Aggregated metrics grouped by day and seller_id

**Complexity:** challenging

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

---

## Query 12: What are the daily order total amount statistics per seller, including second-order change detection, quartiles, and outlier counts? {#query-12}

**Use Case:** **What are the daily order total amount statistics per seller, including second-order change detection, quartiles, and outlier counts?**

**Description:** Sudden accelerations or decelerations in a seller's daily order total amounts can signal operational issues, fraud, or market opportunities that require immediate attention. First-order changes (day-over-day differences) show velocity, but second-order changes (the rate of change of those differences) reveal acceleration patterns that are more actionable for anomaly detection. Produce daily total order amount statistics for each seller, including change acceleration metrics, quartile distributions, and counts of statistical outliers to flag unusual seller behavior. The SQL query computes the first derivative by calculating the difference from the prior day's total_amount using the LAG window function. It then uses trend_direction (Increasing/Decreasing) to represent the sign of this change. By applying LAG and LEAD functions to access previous and next period values, the query enables implicit calculation of second derivatives (acceleration). Z-score calculatio

**Business Value:** Aggregated metrics grouped by week and status

**Complexity:** challenging

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

---

## Query 13: What are the weekly order total amount statistics by order status, with cross-category percentile benchmarking and quartile analysis? {#query-13}

**Use Case:** **What are the weekly order total amount statistics by order status, with cross-category percentile benchmarking and quartile analysis?**

**Description:** Different order statuses (such as completed, pending, or cancelled) represent distinct operational states, and understanding how total order amounts are distributed across these statuses helps identify performance outliers and benchmark relative performance. Cross-category percentile analysis reveals which statuses consistently perform above or below others. Generate weekly total order amount statistics segmented by order status, incorporating percentile-based benchmarking across all statuses and quartile distributions within each status to enable comparative performance analysis. The SQL query employs PERCENT_RANK to calculate each status's relative position within the overall weekly distribution, enabling cross-status comparison. PERCENTILE_CONT functions compute precise percentile values for benchmarking. The data is segmented into sextiles (six equal groups) for granular distribution analysis. Statuses are ranked by cumulative sum to identify the largest co

**Business Value:** Aggregated metrics grouped by month and seller_id

**Complexity:** challenging

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

---

## Query 14: What are the monthly order total amount statistics per seller, including weighted moving averages, quartiles, and trend pattern counts? {#query-14}

**Use Case:** **What are the monthly order total amount statistics per seller, including weighted moving averages, quartiles, and trend pattern counts?**

**Description:** Monthly order total amounts for individual sellers often contain noise from seasonal variations, one-time events, or data irregularities that obscure underlying trends. Moving averages smooth this volatility to reveal genuine growth or decline patterns, enabling more confident strategic decisions about seller performance and resource allocation. Produce monthly total order amount statistics for each seller, incorporating moving average smoothing to reveal underlying trends, quartile distributions for performance segmentation, and counts of increasing periods and outliers to quantify momentum. The SQL query implements a 6-month rolling window to calculate a simple moving average (avg_rolling) that smooths short-term fluctuations. It counts the number of periods showing increasing trends to measure positive momentum and flags outlier readings using statistical thresholds. The dataset is limited to 80 data points per seller to capture sufficient historical context

**Business Value:** Aggregated metrics grouped by day and status

**Complexity:** challenging

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

---

## Query 15: What are the daily order total amount statistics by order status, including peak period identification, operational efficiency metrics, and quartiles? {#query-15}

**Use Case:** **What are the daily order total amount statistics by order status, including peak period identification, operational efficiency metrics, and quartiles?**

**Description:** Understanding when order total amounts reach peak levels within each order status category is critical for capacity planning, resource allocation, and operational readiness. Identifying these peak periods and their temporal patterns (hour of day, day of week) enables proactive staffing and infrastructure scaling decisions. Efficiency metrics help assess whether the system is operating near its theoretical capacity during these peaks. Generate daily total order amount statistics segmented by order status, incorporating peak period identification with temporal context and operational efficiency proxy metrics, along with quartile distributions for performance benchmarking. The SQL query ranks each day's total_amount readings within their respective order status groups to identify peak periods (highest values). It extracts temporal dimensions including hour of day and day of week to reveal cyclical patterns in peak occurrence. The query uses max_cumulative (running

**Business Value:** Aggregated metrics grouped by week and seller_id

**Complexity:** challenging

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

---

## Query 16: What are the weekly order totals per seller with lifetime value metrics, quartiles, and cumulative sum? {#query-16}

**Use Case:** **What are the weekly order totals per seller with lifetime value metrics, quartiles, and cumulative sum?**

**Description:** The business needs to prioritize sellers based on their total transaction activity over time to optimize maintenance scheduling and resource allocation. Lifetime value (LTV) style metrics provide a cumulative view of each seller's contribution, helping identify high-value sellers. Generate weekly total_amount statistics per seller that include LTV-style metrics, distribution quartiles, and cumulative sum analysis. The query computes cumulative_sum of order amounts and tracks max_cumulative as value proxies for lifetime contribution. It ranks sellers by their cumulative sum to identify top performers. PERCENT_RANK is applied to show distribution position within the seller population. The analysis limits results to 60 data points per seller to maintain query performance and requires at least 3 records per seller group to ensure statistical validity. Returns weekly metrics for each seller including LTV-style ranking, quartile distributions (25th, 50th, 75t

**Business Value:** Aggregated metrics grouped by month and status

**Complexity:** challenging

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

---

## Query 17: How do monthly order totals by order status compare year-over-year with growth rates and quartiles? {#query-17}

**Use Case:** **How do monthly order totals by order status compare year-over-year with growth rates and quartiles?**

**Description:** The business needs to understand how order volume patterns evolve across different order statuses (e.g., delivered, cancelled, processing) from one year to the next. Year-over-year (YoY) growth analysis reveals seasonal trends, status-specific patterns, and helps forecast capacity requirements across different operational states. Produce monthly total_amount statistics segmented by order status that include YoY-style growth metrics and quartile distributions. The query calculates trend_direction and delta_value fields to support growth analysis comparisons. It uses the LAG window function to capture prior period values for computing growth rates. Data is filtered to the last 365 days to enable one-year comparison windows. Results are limited to 90 data points per order status to balance detail with performance. Returns monthly metrics for each order status including growth direction indicators (increasing/decreasing trends), delta values showing period-

**Business Value:** Aggregated metrics grouped by day and seller_id

**Complexity:** challenging

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

---

## Query 18: What are the daily order totals per seller formatted for heatmap visualization with quartiles and outliers? {#query-18}

**Use Case:** **What are the daily order totals per seller formatted for heatmap visualization with quartiles and outliers?**

**Description:** The business requires a visual representation of total_amount patterns across time and sellers to gain quick, fleet-wide operational insights. Heatmap visualizations allow analysts to spot anomalies, identify peak transaction periods, and compare seller performance at a glance across two dimensions (time and seller). Generate daily total_amount statistics per seller formatted specifically for heatmap visualization requirements. The query uses time period and seller_id as the two primary heatmap dimensions. It computes avg_value and record_count as intensity metrics for heatmap color coding. Additional time attributes are extracted, including hour of day and day of week, enabling flexible 2D heatmap configurations. Z-score calculations flag statistical outliers in the data. Results are ordered by period and avg_value to facilitate heatmap rendering. Returns daily metrics for each seller in heatmap-ready format with dimensional coordinates (time, seller_i

**Business Value:** Aggregated metrics grouped by week and status

**Complexity:** challenging

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

---

## Query 19: What are the weekly order totals by status showing running percentile distributions, quartiles, and trend patterns? {#query-19}

**Use Case:** **What are the weekly order totals by status showing running percentile distributions, quartiles, and trend patterns?**

**Description:** The business needs to understand how order amounts distribute within each order status category over time. Running percentiles reveal whether order values are consistently high, low, or variable within status buckets (e.g., delivered vs. cancelled), helping identify status-specific patterns and anomalies in transaction values. Generate weekly total_amount statistics segmented by order status that include running percentile calculations, quartile distributions, and trend pattern counts. The query applies PERCENT_RANK to assign each order a percentile position within its status group, showing relative standing over time. PERCENTILE_CONT computes continuous percentile values for quartile breakpoints. Results are limited to 70 data points per order status to maintain performance. The query counts records showing increasing trends versus outlier readings to quantify pattern consistency. Returns weekly metrics for each order status including running percentil

**Business Value:** Aggregated metrics grouped by month and seller_id

**Complexity:** challenging

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

---

## Query 20: What are the monthly order totals per seller with sequential correlation patterns, quartiles, and rolling averages? {#query-20}

**Use Case:** **What are the monthly order totals per seller with sequential correlation patterns, quartiles, and rolling averages?**

**Description:** The business needs to understand how current order amounts relate to previous periods across the seller base. Cross-correlation pattern analysis reveals whether sellers show consistent month-to-month behavior, seasonal cycles, or trend shifts. These patterns help predict future performance and identify sellers whose transaction patterns deviate from historical norms. Generate monthly total_amount statistics per seller that include correlation-style sequential metrics and quartile distributions. The query uses LAG and LEAD window functions to access preceding and following month values for each seller, enabling sequential correlation analysis. It calculates delta_value to measure period-over-period changes. The trend_direction field captures whether values are increasing, decreasing, or stable. Partition_avg and partition_stddev are computed within each seller group to enable z-score normalization and standardized comparison across sellers with different volume

**Business Value:** Aggregated metrics grouped by day and status

**Complexity:** challenging

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

---

## Query 21: What are the daily order total amount statistics by order status, including status transition analysis, quartile distributions, and outlier counts? {#query-21}

**Use Case:** **What are the daily order total amount statistics by order status, including status transition analysis, quartile distributions, and outlier counts?**

**Description:** The finance team needs to perform forensic analysis on how order total amounts transition between different trend states (Increasing, Decreasing, Stable) over time to identify unusual patterns and potential issues requiring investigation. Generate comprehensive daily total amount statistics grouped by order status, incorporating status transition tracking, quartile breakdowns, and outlier identification. The query treats trend_direction values (Increasing, Decreasing, Stable) as distinct status categories and uses delta_value to drive transition logic. It employs LAG and LEAD window functions to capture sequential status changes for forensic tracing, calculates z-scores to flag statistical outliers, computes quartile distributions (Q1, Q2, Q3) for each status group, and filters to include only groups with at least 2 records to ensure statistical validity. A daily metrics report for each order status showing status transition sequences, quartile boundari

**Business Value:** Aggregated metrics grouped by week and seller_id

**Complexity:** challenging

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

---

## Query 22: What are the weekly order total amount statistics per seller with complete dashboard metrics including quartiles and multi-dimensional aggregations? {#query-22}

**Use Case:** **What are the weekly order total amount statistics per seller with complete dashboard metrics including quartiles and multi-dimensional aggregations?**

**Description:** The operations dashboard requires a unified data source that consolidates all key performance metrics for monitoring seller activity across the entire fleet, eliminating the need for multiple separate queries. Generate a complete weekly total amount statistical profile for each seller that includes all critical dashboard metrics in a single result set. The query performs a comprehensive single-pass aggregation that computes record_count (volume), avg_value (mean), quartiles (Q1, Q2/median, Q3), standard deviation (stddev), minimum and maximum values, outlier_count (anomalies), increasing_count (positive trends), avg_rolling (moving average), and max_cumulative (peak cumulative total). It applies a filter requiring at least 3 records per seller-week group to ensure meaningful statistics. A weekly metrics dataset for each seller containing the full dashboard suite of statistics—volume counts, central tendency measures, quartile distributions, dispersion m

**Business Value:** Aggregated metrics grouped by month and status

**Complexity:** challenging

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

---

## Query 23: What are the monthly order total amount statistics by order status with sequential pattern analysis and quartile distributions? {#query-23}

**Use Case:** **What are the monthly order total amount statistics by order status with sequential pattern analysis and quartile distributions?**

**Description:** The analytics team needs to understand how order total amounts evolve sequentially over time within each order status category to identify temporal patterns and trends that inform forecasting models. Produce monthly total amount statistical summaries for each order status that capture sequential evolution patterns alongside standard quartile distributions. The query employs LAG and LEAD window functions to access previous and next period values, calculates delta_value (period-over-period change) and trend_direction (Increasing/Decreasing/Stable) to characterize sequential patterns, uses ROWS BETWEEN window frames to define sliding analysis windows, applies ROW_NUMBER for maintaining temporal ordering within each status partition, limits output to 90 data points per status to manage result size, and computes quartile distributions (Q1, Q2, Q3) for value spread analysis. A monthly metrics report for each order status showing sequential pattern indicators

**Business Value:** Aggregated metrics grouped by day and seller_id

**Complexity:** challenging

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

---

## Query 24: What are the daily order total amount statistics per seller with concentration indices, quartile distributions, and outlier counts? {#query-24}

**Use Case:** **What are the daily order total amount statistics per seller with concentration indices, quartile distributions, and outlier counts?**

**Description:** Management needs to assess market concentration and identify whether order activity is concentrated among a few top sellers or distributed evenly, which informs resource allocation and risk management strategies. Generate daily total amount statistics for each seller that quantify concentration patterns, statistical distributions, and anomalies. The query uses DENSE_RANK to establish seller ranking by total amount, calculates PERCENT_RANK to determine relative position within the distribution, computes cumulative_sum distribution to measure how much total activity accumulates in top-ranked sellers (concentration measurement), segments sellers into quintiles using NTILE(5) for stratified analysis, flags statistical outliers by calculating z-scores and identifying values beyond normal variance thresholds, computes quartile boundaries (Q1, Q2, Q3) for distribution shape, and requires at least 2 records per seller-day group to ensure valid statistical calculations.

**Business Value:** Aggregated metrics grouped by week and status

**Complexity:** challenging

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

---

## Query 25: What are the weekly order total amount statistics by order status with statistical anomaly scores, quartile distributions, and trend counts? {#query-25}

**Use Case:** **What are the weekly order total amount statistics by order status with statistical anomaly scores, quartile distributions, and trend counts?**

**Description:** The quality assurance team needs a prioritization system to identify which order status categories exhibit unusual total amount patterns that warrant immediate investigation, based on statistical anomaly scoring. Produce weekly total amount statistical summaries for each order status that assign anomaly scores, characterize distributions, and quantify trend patterns. The query calculates z_score (standard score) as the primary anomaly detection metric by measuring how many standard deviations each value falls from the mean, aggregates outlier_count to quantify the number of anomalous records in each status group, computes partition_avg (mean) and partition_stddev (standard deviation) to establish baseline statistics for each status partition, counts records by trend_direction (Increasing/Decreasing/Stable) to summarize directional patterns, limits output to 70 data points per status to maintain manageable result sizes, computes quartile distributions (Q1, Q2, Q

**Business Value:** Aggregated metrics grouped by month and seller_id

**Complexity:** challenging

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

---

## Query 26: What are the monthly order totals for each seller, broken down with quartiles for fiscal period comparison? {#query-26}

**Use Case:** **What are the monthly order totals for each seller, broken down with quartiles for fiscal period comparison?**

**Description:** The finance team needs to compare seller performance across fiscal periods (month-over-month and quarter-over-quarter) for budgeting and planning cycles. Generate monthly total_amount statistics for each seller that support fiscal period comparative analysis. The query groups orders by seller and month using DATE_TRUNC('month'), calculates quartiles (25th, 50th, 75th percentiles), average, and standard deviation for each seller-month combination, limits output to 80 data points per seller to keep reporting manageable, and filters to include only groups with at least 1 record. A dataset containing monthly total_amount metrics per seller including quartile breakdowns, averages, and standard deviations suitable for period-over-period fiscal comparison and variance analysis.

**Business Value:** Aggregated metrics grouped by day and status

**Complexity:** challenging

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

---

## Query 27: What are the daily order totals by order status, including throughput metrics, quartiles, and rolling averages? {#query-27}

**Use Case:** **What are the daily order totals by order status, including throughput metrics, quartiles, and rolling averages?**

**Description:** Operations teams need to monitor order throughput and capacity utilization across different status categories (pending, processing, shipped, delivered) to optimize workflow and identify bottlenecks in the order fulfillment pipeline. Generate daily total_amount statistics segmented by order status that include throughput indicators, quartiles, and trend smoothing via rolling averages. The query groups orders by status and day, calculates throughput proxy metrics including record_count (volume), avg_rolling (7-row moving average for trend smoothing), and max_cumulative (peak capacity tracking), computes quartile distributions for variability analysis, limits output to 90 data points per status category, and filters to include only groups with at least 2 records to ensure statistical validity. A dataset containing daily metrics per order status with throughput indicators (volume, rolling trends, cumulative peaks), quartile distributions for variability ass

**Business Value:** Aggregated metrics grouped by week and seller_id

**Complexity:** challenging

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

---

## Query 28: What are the weekly order totals per seller with cumulative trends, quartiles, and activity rankings? {#query-28}

**Use Case:** **What are the weekly order totals per seller with cumulative trends, quartiles, and activity rankings?**

**Description:** Sales leadership needs to track how each seller's total order value accumulates over time to identify growth trajectories, seasonal patterns, and top performers for incentive programs and resource allocation decisions. Generate weekly total_amount statistics per seller that reveal cumulative growth patterns, distribution characteristics, and relative seller rankings. The query groups orders by seller and week, calculates cumulative metrics including cumulative_sum (running total) and max_cumulative (peak performance tracking), derives trend indicators such as trend_direction (up/down/stable) and increasing_count (consecutive growth periods), computes quartile distributions to understand value spread, ranks sellers by their cumulative sum to identify top performers, and filters to include only groups with at least 3 records to ensure meaningful trend detection. A dataset containing weekly metrics per seller with cumulative trend indicators (running total

**Business Value:** Aggregated metrics grouped by month and status

**Complexity:** challenging

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

---

## Query 29: What are the monthly order totals by order status with multi-dimensional aggregations and quartiles? {#query-29}

**Use Case:** **What are the monthly order totals by order status with multi-dimensional aggregations and quartiles?**

**Description:** Business analysts require flexible data structures that support dynamic pivoting and slicing across time periods and order statuses for ad-hoc reporting, executive dashboards, and exploratory analysis of order patterns and status distributions. Generate monthly total_amount statistics segmented by order status with comprehensive multi-dimensional aggregation metrics and quartile breakdowns. The query uses two dimensions—time period (month) and order status—as the grouping structure, then aggregates a comprehensive set of metrics including record count (volume), average (central tendency), quartiles (25th, 50th, 75th percentiles for distribution analysis), standard deviation (variability), min and max (range), outlier_count (anomaly detection), and trend indicators (increasing_count, decreasing_count), requiring at least 1 record per group to maintain data completeness. A multi-dimensional dataset containing monthly metrics per order status with complete

**Business Value:** Aggregated metrics grouped by day and seller_id

**Complexity:** challenging

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

---

## Query 30: What are the weekly order totals by order status with IQR-based outlier detection, quartiles, and trend metrics? {#query-30}

**Use Case:** **What are the weekly order totals by order status with IQR-based outlier detection, quartiles, and trend metrics?**

**Description:** Data quality teams need robust outlier detection methods that complement z-score approaches, particularly for skewed distributions where the Interquartile Range (IQR) method—based on quartile spreads—provides more reliable anomaly flagging than standard deviation-based techniques for identifying unusual order patterns by status. Generate weekly total_amount statistics by order status that incorporate IQR-style outlier detection logic alongside quartile distributions and trend indicators. The query groups orders by status and week, calculates precise quartiles using PERCENTILE_CONT for Q1 (25th) and Q3 (75th) percentiles to support IQR calculation, flags potential outliers using z-score > 2 as a threshold approximation for values outside typical ranges, includes stddev_value to enable alternative IQR-based outlier boundary calculations (Q1-1.5×IQR and Q3+1.5×IQR), computes trend counts (increasing_count, decreasing_count) for pattern detection, limits output to

**Business Value:** Aggregated metrics grouped by week and status

**Complexity:** challenging

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

---

## Usage Instructions

Load schema.sql and data.sql. See docs/README.md for restoration options.

---

## Platform Compatibility

All queries in this database are designed to work across multiple database platforms:

- **PostgreSQL**: Full support with standard SQL features

Queries use standard SQL syntax and avoid platform-specific features to ensure compatibility.

---

**Document Information:**

- **Generated**: 20260218-0146
- **Database**: db-3
- **Type**: Hierarchical Orders (LinkWay)
- **Queries**: 30 production queries
- **Status**: ✅ Complete Comprehensive Deliverable
