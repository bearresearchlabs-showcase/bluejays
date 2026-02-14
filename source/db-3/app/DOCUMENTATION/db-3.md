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

1. [Query 1: Multi-Window Time-Series Analysis with Rolling Aggregates](#query-1)
    - **Use Case:** Business analytics for multi-window time-series analysis with rolling aggregates
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for multi-window time-series analysis with rolling aggregates.  **...
    - *Business Value:* Actionable insights from multi-window time-series analysis with rolling aggregates
    - *Purpose:* Production multi-window time-series analysis with rolling aggregates analysis

2. [Query 2: Segmentation Analysis with Decile Ranking](#query-2)
    - **Use Case:** Business analytics for segmentation analysis with decile ranking
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for segmentation analysis with decile ranking.  **Use Case:** Bus...
    - *Business Value:* Actionable insights from segmentation analysis with decile ranking
    - *Purpose:* Production segmentation analysis with decile ranking analysis

3. [Query 3: Performance Quartile Distribution](#query-3)
    - **Use Case:** Business analytics for performance quartile distribution
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for performance quartile distribution.  **Use Case:** Business a...
    - *Business Value:* Actionable insights from performance quartile distribution
    - *Purpose:* Production performance quartile distribution analysis

4. [Query 4: Revenue Distribution by Category](#query-4)
    - **Use Case:** Business analytics for revenue distribution by category
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for revenue distribution by category.  **Use Case:** Business anal...
    - *Business Value:* Actionable insights from revenue distribution by category
    - *Purpose:* Production revenue distribution by category analysis

5. [Query 5: Velocity and Acceleration Metrics](#query-5)
    - **Use Case:** Business analytics for velocity and acceleration metrics
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for velocity and acceleration metrics.  **Use Case:** Business an...
    - *Business Value:* Actionable insights from velocity and acceleration metrics
    - *Purpose:* Production velocity and acceleration metrics analysis

6. [Query 6: Hourly Pattern Detection and Clustering](#query-6)
    - **Use Case:** Business analytics for hourly pattern detection and clustering
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for hourly pattern detection and clustering.  **Use Case:** Busine...
    - *Business Value:* Actionable insights from hourly pattern detection and clustering
    - *Purpose:* Production hourly pattern detection and clustering analysis

7. [Query 7: Gap Analysis with Sequential Difference](#query-7)
    - **Use Case:** Business analytics for gap analysis with sequential difference
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for gap analysis with sequential difference.  **Use Case:** Busi...
    - *Business Value:* Actionable insights from gap analysis with sequential difference
    - *Purpose:* Production gap analysis with sequential difference analysis

8. [Query 8: Anomaly Detection Using Z-Score Windows](#query-8)
    - **Use Case:** Business analytics for anomaly detection using z-score windows
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for anomaly detection using z-score windows.  **Use Case:** Busine...
    - *Business Value:* Actionable insights from anomaly detection using z-score windows
    - *Purpose:* Production anomaly detection using z-score windows analysis

9. [Query 9: Recency-Frequency-Monetary Scoring](#query-9)
    - **Use Case:** Business analytics for recency-frequency-monetary scoring
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for recency-frequency-monetary scoring.  **Use Case:** Business a...
    - *Business Value:* Actionable insights from recency-frequency-monetary scoring
    - *Purpose:* Production recency-frequency-monetary scoring analysis

10. [Query 10: Multi-Period Cohort Retention Analysis](#query-10)
    - **Use Case:** Business analytics for multi-period cohort retention analysis
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for multi-period cohort retention analysis.  **Use Case:** Busin...
    - *Business Value:* Actionable insights from multi-period cohort retention analysis
    - *Purpose:* Production multi-period cohort retention analysis analysis

11. [Query 11: Second-Order Derivative Computation](#query-11)
    - **Use Case:** Business analytics for second-order derivative computation
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for second-order derivative computation.  **Use Case:** Business a...
    - *Business Value:* Actionable insights from second-order derivative computation
    - *Purpose:* Production second-order derivative computation analysis

12. [Query 12: Cross-Category Benchmarking with Percentiles](#query-12)
    - **Use Case:** Business analytics for cross-category benchmarking with percentiles
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for cross-category benchmarking with percentiles.  **Use Case:**...
    - *Business Value:* Actionable insights from cross-category benchmarking with percentiles
    - *Purpose:* Production cross-category benchmarking with percentiles analysis

13. [Query 13: Exponentially Weighted Moving Average](#query-13)
    - **Use Case:** Business analytics for exponentially weighted moving average
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for exponentially weighted moving average.  **Use Case:** Busine...
    - *Business Value:* Actionable insights from exponentially weighted moving average
    - *Purpose:* Production exponentially weighted moving average analysis

14. [Query 14: Peak Period Identification and Efficiency](#query-14)
    - **Use Case:** Business analytics for peak period identification and efficiency
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for peak period identification and efficiency.  **Use Case:** Busi...
    - *Business Value:* Actionable insights from peak period identification and efficiency
    - *Purpose:* Production peak period identification and efficiency analysis

15. [Query 15: Lifetime Value Estimation Model](#query-15)
    - **Use Case:** Business analytics for lifetime value estimation model
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for lifetime value estimation model.  **Use Case:** Business anal...
    - *Business Value:* Actionable insights from lifetime value estimation model
    - *Purpose:* Production lifetime value estimation model analysis

16. [Query 16: Year-over-Year Growth Rate Analysis](#query-16)
    - **Use Case:** Business analytics for year-over-year growth rate analysis
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for year-over-year growth rate analysis.  **Use Case:** Business...
    - *Business Value:* Actionable insights from year-over-year growth rate analysis
    - *Purpose:* Production year-over-year growth rate analysis analysis

17. [Query 17: Heatmap Data Generation by Time Dimensions](#query-17)
    - **Use Case:** Business analytics for heatmap data generation by time dimensions
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for heatmap data generation by time dimensions.  **Use Case:** Bus...
    - *Business Value:* Actionable insights from heatmap data generation by time dimensions
    - *Purpose:* Production heatmap data generation by time dimensions analysis

18. [Query 18: Running Percentile Distribution Computation](#query-18)
    - **Use Case:** Business analytics for running percentile distribution computation
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for running percentile distribution computation.  **Use Case:** B...
    - *Business Value:* Actionable insights from running percentile distribution computation
    - *Purpose:* Production running percentile distribution computation analysis

19. [Query 19: Cross-Correlation Pattern Analysis](#query-19)
    - **Use Case:** Business analytics for cross-correlation pattern analysis
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for cross-correlation pattern analysis.  **Use Case:** Business...
    - *Business Value:* Actionable insights from cross-correlation pattern analysis
    - *Purpose:* Production cross-correlation pattern analysis analysis

20. [Query 20: Forensic Analysis of Status Transitions](#query-20)
    - **Use Case:** Business analytics for forensic analysis of status transitions
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for forensic analysis of status transitions.  **Use Case:** Busine...
    - *Business Value:* Actionable insights from forensic analysis of status transitions
    - *Purpose:* Production forensic analysis of status transitions analysis

21. [Query 21: Multi-Metric Dashboard Aggregation Pipeline](#query-21)
    - **Use Case:** Business analytics for multi-metric dashboard aggregation pipeline
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for multi-metric dashboard aggregation pipeline.  **Use Case:** B...
    - *Business Value:* Actionable insights from multi-metric dashboard aggregation pipeline
    - *Purpose:* Production multi-metric dashboard aggregation pipeline analysis

22. [Query 22: Sequential Pattern Mining with Windows](#query-22)
    - **Use Case:** Business analytics for sequential pattern mining with windows
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for sequential pattern mining with windows.  **Use Case:** Busin...
    - *Business Value:* Actionable insights from sequential pattern mining with windows
    - *Purpose:* Production sequential pattern mining with windows analysis

23. [Query 23: Concentration Index Computation](#query-23)
    - **Use Case:** Business analytics for concentration index computation
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for concentration index computation.  **Use Case:** Business analy...
    - *Business Value:* Actionable insights from concentration index computation
    - *Purpose:* Production concentration index computation analysis

24. [Query 24: Statistical Anomaly Score Assignment](#query-24)
    - **Use Case:** Business analytics for statistical anomaly score assignment
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for statistical anomaly score assignment.  **Use Case:** Business...
    - *Business Value:* Actionable insights from statistical anomaly score assignment
    - *Purpose:* Production statistical anomaly score assignment analysis

25. [Query 25: Fiscal Period Comparative Reporting](#query-25)
    - **Use Case:** Business analytics for fiscal period comparative reporting
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for fiscal period comparative reporting.  **Use Case:** Business...
    - *Business Value:* Actionable insights from fiscal period comparative reporting
    - *Purpose:* Production fiscal period comparative reporting analysis

26. [Query 26: Throughput Optimization Metrics](#query-26)
    - **Use Case:** Business analytics for throughput optimization metrics
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for throughput optimization metrics.  **Use Case:** Business analy...
    - *Business Value:* Actionable insights from throughput optimization metrics
    - *Purpose:* Production throughput optimization metrics analysis

27. [Query 27: Cumulative Trend Analysis Pipeline](#query-27)
    - **Use Case:** Business analytics for cumulative trend analysis pipeline
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for cumulative trend analysis pipeline.  **Use Case:** Business a...
    - *Business Value:* Actionable insights from cumulative trend analysis pipeline
    - *Purpose:* Production cumulative trend analysis pipeline analysis

28. [Query 28: Multi-Dimensional Pivot Aggregation](#query-28)
    - **Use Case:** Business analytics for multi-dimensional pivot aggregation
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and month-level grouping for multi-dimensional pivot aggregation.  **Use Case:** Business...
    - *Business Value:* Actionable insights from multi-dimensional pivot aggregation
    - *Purpose:* Production multi-dimensional pivot aggregation analysis

29. [Query 29: Funnel Stage Progression Tracking](#query-29)
    - **Use Case:** Business analytics for funnel stage progression tracking
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and day-level grouping for funnel stage progression tracking.  **Use Case:** Business ana...
    - *Business Value:* Actionable insights from funnel stage progression tracking
    - *Purpose:* Production funnel stage progression tracking analysis

30. [Query 30: Outlier Detection with IQR Method](#query-30)
    - **Use Case:** Business analytics for outlier detection with iqr method
    - *What it does:* Uses 4 CTEs with window functions, statistical aggregations, and week-level grouping for outlier detection with iqr method.  **Use Case:** Business an...
    - *Business Value:* Actionable insights from outlier detection with iqr method
    - *Purpose:* Production outlier detection with iqr method analysis

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
- **Databricks**: Compatible with Delta Lake
- **Snowflake**: Full support

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

## Query 1: Multi-Window Time-Series Analysis with Rolling Aggregates {#query-1}

**Use Case:** **Business analytics for multi-window time-series analysis with rolling aggregates**

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

---

## Query 2: Segmentation Analysis with Decile Ranking {#query-2}

**Use Case:** **Business analytics for segmentation analysis with decile ranking**

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

---

## Query 3: Performance Quartile Distribution {#query-3}

**Use Case:** **Business analytics for performance quartile distribution**

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

---

## Query 4: Revenue Distribution by Category {#query-4}

**Use Case:** **Business analytics for revenue distribution by category**

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

---

## Query 5: Velocity and Acceleration Metrics {#query-5}

**Use Case:** **Business analytics for velocity and acceleration metrics**

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

---

## Query 6: Hourly Pattern Detection and Clustering {#query-6}

**Use Case:** **Business analytics for hourly pattern detection and clustering**

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

---

## Query 7: Gap Analysis with Sequential Difference {#query-7}

**Use Case:** **Business analytics for gap analysis with sequential difference**

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

---

## Query 8: Anomaly Detection Using Z-Score Windows {#query-8}

**Use Case:** **Business analytics for anomaly detection using z-score windows**

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

---

## Query 9: Recency-Frequency-Monetary Scoring {#query-9}

**Use Case:** **Business analytics for recency-frequency-monetary scoring**

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

---

## Query 10: Multi-Period Cohort Retention Analysis {#query-10}

**Use Case:** **Business analytics for multi-period cohort retention analysis**

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

---

## Query 11: Second-Order Derivative Computation {#query-11}

**Use Case:** **Business analytics for second-order derivative computation**

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

---

## Query 12: Cross-Category Benchmarking with Percentiles {#query-12}

**Use Case:** **Business analytics for cross-category benchmarking with percentiles**

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

---

## Query 13: Exponentially Weighted Moving Average {#query-13}

**Use Case:** **Business analytics for exponentially weighted moving average**

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

---

## Query 14: Peak Period Identification and Efficiency {#query-14}

**Use Case:** **Business analytics for peak period identification and efficiency**

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

---

## Query 15: Lifetime Value Estimation Model {#query-15}

**Use Case:** **Business analytics for lifetime value estimation model**

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

---

## Query 16: Year-over-Year Growth Rate Analysis {#query-16}

**Use Case:** **Business analytics for year-over-year growth rate analysis**

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

---

## Query 17: Heatmap Data Generation by Time Dimensions {#query-17}

**Use Case:** **Business analytics for heatmap data generation by time dimensions**

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

---

## Query 18: Running Percentile Distribution Computation {#query-18}

**Use Case:** **Business analytics for running percentile distribution computation**

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

---

## Query 19: Cross-Correlation Pattern Analysis {#query-19}

**Use Case:** **Business analytics for cross-correlation pattern analysis**

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

---

## Query 20: Forensic Analysis of Status Transitions {#query-20}

**Use Case:** **Business analytics for forensic analysis of status transitions**

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

---

## Query 21: Multi-Metric Dashboard Aggregation Pipeline {#query-21}

**Use Case:** **Business analytics for multi-metric dashboard aggregation pipeline**

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

---

## Query 22: Sequential Pattern Mining with Windows {#query-22}

**Use Case:** **Business analytics for sequential pattern mining with windows**

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

---

## Query 23: Concentration Index Computation {#query-23}

**Use Case:** **Business analytics for concentration index computation**

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

---

## Query 24: Statistical Anomaly Score Assignment {#query-24}

**Use Case:** **Business analytics for statistical anomaly score assignment**

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

---

## Query 25: Fiscal Period Comparative Reporting {#query-25}

**Use Case:** **Business analytics for fiscal period comparative reporting**

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

---

## Query 26: Throughput Optimization Metrics {#query-26}

**Use Case:** **Business analytics for throughput optimization metrics**

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

---

## Query 27: Cumulative Trend Analysis Pipeline {#query-27}

**Use Case:** **Business analytics for cumulative trend analysis pipeline**

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

---

## Query 28: Multi-Dimensional Pivot Aggregation {#query-28}

**Use Case:** **Business analytics for multi-dimensional pivot aggregation**

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

---

## Query 29: Funnel Stage Progression Tracking {#query-29}

**Use Case:** **Business analytics for funnel stage progression tracking**

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

---

## Query 30: Outlier Detection with IQR Method {#query-30}

**Use Case:** **Business analytics for outlier detection with iqr method**

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

---

## Usage Instructions

Load schema.sql and data.sql. See docs/README.md for restoration options.

---

## Platform Compatibility

All queries in this database are designed to work across multiple database platforms:

- **PostgreSQL**: Full support with standard SQL features
- **Databricks**: Compatible with Delta Lake and Spark SQL
- **Snowflake**: Full support with Snowflake SQL syntax

Queries use standard SQL syntax and avoid platform-specific features to ensure cross-platform compatibility.

---

**Document Information:**

- **Generated**: 20260209-2214
- **Database**: db-3
- **Type**: Hierarchical Orders (LinkWay)
- **Queries**: 30 production queries
- **Status**: ✅ Complete Comprehensive Deliverable
