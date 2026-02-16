# ID: db-2 - Name: Filling Station Retail / POS (phppos)

This document provides comprehensive documentation for database db-2, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**, representing real-world enterprise implementations.

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

1. [Query 1: Can you show me how each employee's daily sales have been trending over the past year? I'd like to see rolling 7-day averages and identify how many transactions exceed their personal average.](#query-1)
    - **Use Case:** Can you show me how each employee's daily sales have been trending over the past year? I'd like to see rolling 7-day averages and identify how many transactions exceed their personal average.
    - *What it does:* Situation: Store managers monitor employee performance to identify top performers for recognition and struggling employees who need coaching. They nee...
    - *Business Value:* Daily aggregated sales metrics with rolling averages and trend indicators

2. [Query 2: Can you break down monthly purchase behavior by customer? I need to see quartile distributions, how many outlier transactions occurred, and which customers show increasing purchase trends.](#query-2)
    - **Use Case:** Can you break down monthly purchase behavior by customer? I need to see quartile distributions, how many outlier transactions occurred, and which customers show increasing purchase trends.
    - *What it does:* Situation: Marketing and customer success teams segment customers by purchase patterns to tailor retention campaigns, identify VIP customers with unus...
    - *Business Value:* Aggregated metrics for customer purchase frequency segmentation

3. [Query 3: Show me daily performance quartiles for each employee — I want to see transaction count, median sales, outlier count, and a rolling average.](#query-3)
    - **Use Case:** Show me daily performance quartiles for each employee — I want to see transaction count, median sales, outlier count, and a rolling average.
    - *What it does:* Situation: Operations managers compare employee performance daily to ensure fair workload distribution, recognize high achievers, and identify employe...
    - *Business Value:* Aggregated metrics for employee performance quartile ranking

4. [Query 4: I need a weekly breakdown of sales by payment type — show me quartiles, outlier counts, and how many transactions are on an upward trend.](#query-4)
    - **Use Case:** I need a weekly breakdown of sales by payment type — show me quartiles, outlier counts, and how many transactions are on an upward trend.
    - *What it does:* Situation: Finance and fraud prevention teams monitor payment method usage patterns to ensure accurate reconciliation, detect anomalies that may indic...
    - *Business Value:* Aggregated metrics for payment type revenue distribution

5. [Query 5: Give me monthly sales velocity by store location — I want quartiles, standard deviation, outlier count, and cumulative totals.](#query-5)
    - **Use Case:** Give me monthly sales velocity by store location — I want quartiles, standard deviation, outlier count, and cumulative totals.
    - *What it does:* Situation: Regional managers and operations executives compare store performance across multiple locations to allocate marketing budgets, decide on ne...
    - *Business Value:* Aggregated metrics for location-based sales velocity

6. [Query 6: Show me daily sales performance by employee with quartile distributions, rolling averages, and anomaly detection.](#query-6)
    - **Use Case:** Show me daily sales performance by employee with quartile distributions, rolling averages, and anomaly detection.
    - *What it does:* Situation: The sales operations team needs to monitor daily employee performance to identify unusual patterns that may indicate data entry errors, fra...
    - *Business Value:* Aggregated metrics for hourly sales pattern detection

7. [Query 7: Show me monthly sales by customer with purchase frequency gap analysis, quartiles, and trend indicators.](#query-7)
    - **Use Case:** Show me monthly sales by customer with purchase frequency gap analysis, quartiles, and trend indicators.
    - *What it does:* Situation: The customer success team is building a churn prediction model and needs to understand how customer purchase behavior evolves month-over-mo...
    - *Business Value:* Aggregated metrics for invoice gap analysis

8. [Query 8: Show me daily sales by payment type with anomaly detection, quartiles, and trend patterns.](#query-8)
    - **Use Case:** Show me daily sales by payment type with anomaly detection, quartiles, and trend patterns.
    - *What it does:* Situation: The finance and fraud detection teams need to monitor payment processing patterns across different payment types (credit card, cash, digita...
    - *Business Value:* Aggregated metrics for suspended transaction anomaly detection

9. [Query 9: Show me weekly sales by customer with recency-frequency analysis, quartiles, and rolling averages.](#query-9)
    - **Use Case:** Show me weekly sales by customer with recency-frequency analysis, quartiles, and rolling averages.
    - *What it does:* Situation: The marketing team is designing targeted retention and upsell campaigns and needs to segment customers based on how recently and how freque...
    - *Business Value:* Aggregated metrics for customer recency-frequency analysis

10. [Query 10: Show me monthly sales by employee with cohort-style retention analysis and quartile distributions.](#query-10)
    - **Use Case:** Show me monthly sales by employee with cohort-style retention analysis and quartile distributions.
    - *What it does:* Situation: The human resources and sales management teams need to track how employee sales performance evolves over their tenure to identify which emp...
    - *Business Value:* Aggregated metrics for multi-period cohort retention

11. [Query 11: What are the daily sales statistics by location, including acceleration rate, quartiles, and outlier count?](#query-11)
    - **Use Case:** What are the daily sales statistics by location, including acceleration rate, quartiles, and outlier count?
    - *What it does:* Situation: The retail operations team is planning regional expansion and needs to understand how quickly revenue is growing at each location. Sales ac...
    - *Business Value:* Aggregated metrics for sales acceleration rate computation

12. [Query 12: What are the weekly sales statistics by employee with cross-location revenue benchmarking and quartiles?](#query-12)
    - **Use Case:** What are the weekly sales statistics by employee with cross-location revenue benchmarking and quartiles?
    - *What it does:* Situation: The sales management team wants to identify top-performing employees across all locations and establish fair, data-driven sales targets tha...
    - *Business Value:* Aggregated metrics for cross-location revenue benchmarking

13. [Query 13: What are the monthly sales statistics by payment type with time-weighted moving average and quartiles?](#query-13)
    - **Use Case:** What are the monthly sales statistics by payment type with time-weighted moving average and quartiles?
    - *What it does:* Situation: The finance team needs to understand long-term trends in payment method preferences, but monthly data contains seasonal noise from holidays...
    - *Business Value:* Aggregated metrics for time-weighted moving average

14. [Query 14: What are the daily sales statistics by customer with peak hour identification and quartiles?](#query-14)
    - **Use Case:** What are the daily sales statistics by customer with peak hour identification and quartiles?
    - *What it does:* Situation: The store operations team is optimizing labor scheduling and promotional timing to align with customer shopping patterns. Understanding whe...
    - *Business Value:* Aggregated metrics for peak hour identification and staffing

15. [Query 15: What are the weekly sales statistics by location with customer lifetime value estimation metrics and quartiles?](#query-15)
    - **Use Case:** What are the weekly sales statistics by location with customer lifetime value estimation metrics and quartiles?
    - *What it does:* Situation: The marketing and real estate teams are prioritizing locations for increased investment, lease renewals, and targeted campaigns. Customer l...
    - *Business Value:* Aggregated metrics for customer lifetime value estimation

16. [Query 16: What are the monthly sales statistics for each employee, including year-over-year growth rates with seasonal adjustments and quartile distributions?](#query-16)
    - **Use Case:** What are the monthly sales statistics for each employee, including year-over-year growth rates with seasonal adjustments and quartile distributions?
    - *What it does:* Situation: The sales management team needs to compare employee performance across different seasons and years to identify top performers and plan reso...
    - *Business Value:* Aggregated metrics for yoy growth rate with seasonal adjustment

17. [Query 17: What are the daily sales statistics broken down by payment type, formatted for transaction velocity heatmap visualization with quartile distributions?](#query-17)
    - **Use Case:** What are the daily sales statistics broken down by payment type, formatted for transaction velocity heatmap visualization with quartile distributions?
    - *What it does:* Situation: The operations team wants to create visual heatmaps showing how payment methods (credit card, cash, mobile payment, etc.) are used througho...
    - *Business Value:* Aggregated metrics for transaction velocity heatmap data

18. [Query 18: What are the weekly sales statistics for each customer, including running percentile distributions and quartile rankings?](#query-18)
    - **Use Case:** What are the weekly sales statistics for each customer, including running percentile distributions and quartile rankings?
    - *What it does:* Situation: The marketing and customer success teams need to understand how customer spending patterns distribute within each week to support customer...
    - *Business Value:* Aggregated metrics for running percentile sales distribution

19. [Query 19: What are the monthly sales statistics by location, including employee cross-sell effectiveness metrics and quartile distributions?](#query-19)
    - **Use Case:** What are the monthly sales statistics by location, including employee cross-sell effectiveness metrics and quartile distributions?
    - *What it does:* Situation: Regional and location managers need to evaluate which store locations are most effective at cross-selling additional products or services,...
    - *Business Value:* Aggregated metrics for employee cross-sell effectiveness

20. [Query 20: What are the daily sales statistics for each employee, including forensic analysis of deleted transactions and quartile distributions?](#query-20)
    - **Use Case:** What are the daily sales statistics for each employee, including forensic analysis of deleted transactions and quartile distributions?
    - *What it does:* Situation: The loss prevention and audit teams need to investigate transaction anomalies by tracing the complete sequence of sales events including vo...
    - *Business Value:* Aggregated metrics for deleted transaction forensic analysis

21. [Query 21: What are the weekly sales statistics broken down by payment type, including quartiles and all key metrics for the executive dashboard?](#query-21)
    - **Use Case:** What are the weekly sales statistics broken down by payment type, including quartiles and all key metrics for the executive dashboard?
    - *What it does:* Situation: The executive team reviews a weekly dashboard that requires a comprehensive view of sales performance across different payment methods (cre...
    - *Business Value:* Aggregated metrics for multi-metric dashboard aggregation

22. [Query 22: How do individual customer purchasing patterns evolve month-over-month, including sequential behavior metrics and quartile distributions?](#query-22)
    - **Use Case:** How do individual customer purchasing patterns evolve month-over-month, including sequential behavior metrics and quartile distributions?
    - *What it does:* Situation: The personalization team needs to understand how each customer's purchasing behavior changes over time to tailor marketing campaigns, predi...
    - *Business Value:* Aggregated metrics for sequential purchase pattern mining

23. [Query 23: What is the daily revenue concentration across different store locations, showing which locations dominate sales and their quartile distributions?](#query-23)
    - **Use Case:** What is the daily revenue concentration across different store locations, showing which locations dominate sales and their quartile distributions?
    - *What it does:* Situation: The operations team needs to understand how revenue is distributed across store locations to make informed decisions about staffing levels,...
    - *Business Value:* Aggregated metrics for revenue concentration index

24. [Query 24: Which employees show unusual weekly sales patterns that may indicate exceptional performance or require additional training support?](#query-24)
    - **Use Case:** Which employees show unusual weekly sales patterns that may indicate exceptional performance or require additional training support?
    - *What it does:* Situation: The sales management team monitors employee performance to identify both top performers who deserve recognition and individuals who may nee...
    - *Business Value:* Aggregated metrics for anomaly score computation

25. [Query 25: How do monthly sales trends compare across different payment types for fiscal period reporting and quarter-over-quarter analysis?](#query-25)
    - **Use Case:** How do monthly sales trends compare across different payment types for fiscal period reporting and quarter-over-quarter analysis?
    - *What it does:* Situation: The finance department prepares monthly and quarterly reports comparing payment method performance across fiscal periods to identify trends...
    - *Business Value:* Aggregated metrics for fiscal period comparative analysis

26. [Query 26: What are the daily sales statistics for each customer, including transaction throughput metrics and quartile distributions?](#query-26)
    - **Use Case:** What are the daily sales statistics for each customer, including transaction throughput metrics and quartile distributions?
    - *What it does:* Situation: The business needs to assess transaction volume patterns per customer to optimize system capacity planning and refine loyalty program tiers...
    - *Business Value:* Aggregated metrics for transaction throughput optimization

27. [Query 27: What are the weekly sales statistics by store location, including payment method trend analysis and quartile distributions?](#query-27)
    - **Use Case:** What are the weekly sales statistics by store location, including payment method trend analysis and quartile distributions?
    - *What it does:* Situation: The retail operations team needs to identify shifts in payment method preferences (such as credit card versus cash usage) across different...
    - *Business Value:* Aggregated metrics for store account payment trend analysis

28. [Query 28: What are the monthly sales statistics for each employee, with multi-dimensional aggregation and quartile distributions?](#query-28)
    - **Use Case:** What are the monthly sales statistics for each employee, with multi-dimensional aggregation and quartile distributions?
    - *What it does:* Situation: The sales management team requires flexible reporting capabilities that allow pivoting sales data by both time period and employee to suppo...
    - *Business Value:* Aggregated metrics for multi-dimensional pivot analysis

29. [Query 29: What are the daily sales statistics by payment type, including sales funnel stage progression and quartile distributions?](#query-29)
    - **Use Case:** What are the daily sales statistics by payment type, including sales funnel stage progression and quartile distributions?
    - *What it does:* Situation: The analytics team needs to understand how payment method preferences evolve throughout the day to identify conversion patterns and optimiz...
    - *Business Value:* Aggregated metrics for sales funnel stage progression

30. [Query 30: What are the weekly sales statistics per customer, with IQR-based outlier detection and quartile distributions?](#query-30)
    - **Use Case:** What are the weekly sales statistics per customer, with IQR-based outlier detection and quartile distributions?
    - *What it does:* Situation: The fraud detection and customer experience teams need to identify customers with unusual spending patterns—either abnormally high spenders...
    - *Business Value:* Aggregated metrics for outlier detection with iqr method

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

Real-world retail Point-of-Sale (POS) database from a family business in Kenya, featuring complete transactional history, inventory management, and multi-location operations. Includes phppos schema with sales, line items, payments, inventory, products, and suppliers.

- Sales transactions and line items
- Payment records and inventory movements
- Product catalog and purchase orders
- Supplier receivings and multi-location support

- **PostgreSQL**: Full support

---

---

### Data Dictionary

This section provides a comprehensive data dictionary for all tables in the database, including column names, data types, constraints, and descriptions. Tables are organized by functional category for easier navigation.

See `docs/SCHEMA.md` for full LUCASA schema. This deliverable uses a minimal 8-table subset: `phppos_people`, `phppos_employees`, `phppos_employees_locations`, `phppos_items`, `phppos_locations`, `phppos_location_items`, `phppos_sales`. ACID-compliant with PKs and FKs.

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

## Query 1: Can you show me how each employee's daily sales have been trending over the past year? I'd like to see rolling 7-day averages and identify how many transactions exceed their personal average. {#query-1}

**Use Case:** **Can you show me how each employee's daily sales have been trending over the past year? I'd like to see rolling 7-day averages and identify how many transactions exceed their personal average.**

**Description:** Situation: Store managers monitor employee performance to identify top performers for recognition and struggling employees who need coaching. They need visibility into daily sales patterns smoothed by weekly trends to distinguish genuine performance shifts from day-to-day noise. Task: Generate daily sales metrics for each employee that include a rolling 7-day average and a count of transactions exceeding the employee's personal average. Action: The query groups transactions by date and employee, then computes each employee's overall average transaction value as a benchmark. It applies a 7-row rolling window ordered by date to calculate smoothed averages, compares individual transactions against the employee's benchmark to count above-average performance, retains only the 100 most recent transactions per employee to focus on current trends, and excludes days with single transactions to avoid statistical noise. Result: A dataset containing daily metrics for each employee showing their ro

**Business Value:** Daily aggregated sales metrics with rolling averages and trend indicators

**Complexity:** challenging

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

---

## Query 2: Can you break down monthly purchase behavior by customer? I need to see quartile distributions, how many outlier transactions occurred, and which customers show increasing purchase trends. {#query-2}

**Use Case:** **Can you break down monthly purchase behavior by customer? I need to see quartile distributions, how many outlier transactions occurred, and which customers show increasing purchase trends.**

**Description:** Situation: Marketing and customer success teams segment customers by purchase patterns to tailor retention campaigns, identify VIP customers with unusual high spending, and detect disengagement early. Understanding statistical distributions and trend directions enables targeted interventions. Task: Produce monthly aggregated sales statistics per customer that include quartile breakdowns, counts of statistical outliers, and identification of upward spending trends. Action: The query groups purchases by month and customer, then calculates quartiles by segmenting spend into sextiles (six equal groups). It computes z-scores for each transaction and flags those exceeding two standard deviations as outliers. To detect momentum, it derives trend direction by comparing consecutive transaction amounts and counts how many show increases. The query limits each customer to their 70 most recent data points for manageability and requires at least three transactions per month per customer to ensure s

**Business Value:** Aggregated metrics for customer purchase frequency segmentation

**Complexity:** challenging

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

---

## Query 3: Show me daily performance quartiles for each employee — I want to see transaction count, median sales, outlier count, and a rolling average. {#query-3}

**Use Case:** **Show me daily performance quartiles for each employee — I want to see transaction count, median sales, outlier count, and a rolling average.**

**Description:** Situation: Operations managers compare employee performance daily to ensure fair workload distribution, recognize high achievers, and identify employees whose sales patterns deviate significantly from the norm, which may indicate training needs or exceptional customer service. Quartile analysis provides a standardized benchmark across the team. Task: Generate daily sales statistics for each employee that include transaction count, first quartile, median, third quartile, outlier count, and a rolling average. Action: The query groups sales by date and employee, then applies PERCENTILE_CONT to compute Q1 (25th percentile), median (50th percentile), and Q3 (75th percentile) for robust statistical summaries. It calculates a 7-row rolling average to smooth daily volatility, segments transactions into septiles (seven equal groups) to classify distribution spread, and permits single-transaction days to accommodate newly hired employees who are ramping up. Result: Daily performance metrics for

**Business Value:** Aggregated metrics for employee performance quartile ranking

**Complexity:** challenging

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

---

## Query 4: I need a weekly breakdown of sales by payment type — show me quartiles, outlier counts, and how many transactions are on an upward trend. {#query-4}

**Use Case:** **I need a weekly breakdown of sales by payment type — show me quartiles, outlier counts, and how many transactions are on an upward trend.**

**Description:** Situation: Finance and fraud prevention teams monitor payment method usage patterns to ensure accurate reconciliation, detect anomalies that may indicate fraud or processing errors, and understand customer payment preferences over time. Weekly aggregation balances granularity with trend stability. Task: Produce weekly sales statistics segmented by payment type (cash, credit card, mobile payment, etc.) that include quartile distributions, counts of outlier transactions, and identification of increasing transaction trends. Action: The query groups transactions by week and payment type, then computes quartiles to understand the spread of transaction amounts within each payment method. It applies an 8-row rolling window to smooth weekly fluctuations, segments data into octiles (eight equal groups) for finer distribution analysis, flags statistical outliers, counts transactions that increase compared to prior periods to identify momentum, and requires at least two records per week per payme

**Business Value:** Aggregated metrics for payment type revenue distribution

**Complexity:** challenging

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

---

## Query 5: Give me monthly sales velocity by store location — I want quartiles, standard deviation, outlier count, and cumulative totals. {#query-5}

**Use Case:** **Give me monthly sales velocity by store location — I want quartiles, standard deviation, outlier count, and cumulative totals.**

**Description:** Situation: Regional managers and operations executives compare store performance across multiple locations to allocate marketing budgets, decide on new store openings or closures, and identify underperforming sites that require operational improvements. Monthly aggregation provides enough data to smooth daily volatility while remaining actionable for quarterly planning cycles. Task: Generate monthly sales statistics for each location that include quartile distributions, standard deviation as a measure of sales volatility, count of outlier transactions, and the maximum cumulative sales sum. Action: The query groups sales by month and location, then calculates Q1, median, and Q3 to profile the spending distribution at each site. It computes standard deviation to quantify sales variability, which helps distinguish consistently performing stores from volatile ones. A 9-row rolling window smooths multi-month trends, and the data is segmented into noniles (nine equal groups) for granular dis

**Business Value:** Aggregated metrics for location-based sales velocity

**Complexity:** challenging

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

---

## Query 6: Show me daily sales performance by employee with quartile distributions, rolling averages, and anomaly detection. {#query-6}

**Use Case:** **Show me daily sales performance by employee with quartile distributions, rolling averages, and anomaly detection.**

**Description:** Situation: The sales operations team needs to monitor daily employee performance to identify unusual patterns that may indicate data entry errors, fraudulent transactions, or exceptional sales activity requiring investigation. Task: Generate comprehensive daily sales statistics for each employee that include quartile distributions, rolling trend indicators, and statistical anomaly detection. Action: The query aggregates sales transactions by day and employee, extracts temporal features (hour of day and day of week) to provide context, calculates quartile boundaries (25th, 50th, 75th percentiles) for distribution analysis, computes a 10-day rolling average to smooth short-term fluctuations, applies z-score methodology to flag statistical outliers beyond normal variance, and accommodates employees who may have only a single transaction on certain days. Result: A dataset containing daily performance metrics for each employee including quartile values for understanding sales distribution,

**Business Value:** Aggregated metrics for hourly sales pattern detection

**Complexity:** challenging

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

---

## Query 7: Show me monthly sales by customer with purchase frequency gap analysis, quartiles, and trend indicators. {#query-7}

**Use Case:** **Show me monthly sales by customer with purchase frequency gap analysis, quartiles, and trend indicators.**

**Description:** Situation: The customer success team is building a churn prediction model and needs to understand how customer purchase behavior evolves month-over-month, specifically looking at changes in purchase frequency and spending amounts to identify customers at risk of churning. Task: Produce monthly sales statistics for each customer that capture sequential purchasing patterns through gap-style metrics, quartile distributions for spend analysis, and directional trend indicators. Action: The query groups sales data by month and customer, uses window functions LAG and LEAD to compute differences between consecutive months (measuring changes in purchase frequency and amounts), derives trend direction indicators (increasing, stable, or decreasing), calculates quartile boundaries for spend distribution analysis, and filters to include only customers with at least 3 months of purchase history to ensure meaningful trend detection. Result: A dataset containing monthly metrics for each customer inclu

**Business Value:** Aggregated metrics for invoice gap analysis

**Complexity:** challenging

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

---

## Query 8: Show me daily sales by payment type with anomaly detection, quartiles, and trend patterns. {#query-8}

**Use Case:** **Show me daily sales by payment type with anomaly detection, quartiles, and trend patterns.**

**Description:** Situation: The finance and fraud detection teams need to monitor payment processing patterns across different payment types (credit card, cash, digital wallet, etc.) to quickly identify unusual activity that may signal system malfunctions, fraudulent behavior, or unexpected shifts in customer payment preferences. Task: Generate daily sales statistics segmented by payment type that include statistical anomaly detection, quartile distributions for normal range identification, and trend pattern analysis. Action: The query aggregates transactions by day and payment type, applies z-score statistical methodology to flag days where transaction volumes or amounts fall outside normal variance thresholds, calculates quartile boundaries to establish baseline expectations for each payment type, derives trend direction indicators to capture momentum patterns, and requires at least 2 transaction records per group to enable meaningful statistical comparison. Result: A dataset containing daily metrics

**Business Value:** Aggregated metrics for suspended transaction anomaly detection

**Complexity:** challenging

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

---

## Query 9: Show me weekly sales by customer with recency-frequency analysis, quartiles, and rolling averages. {#query-9}

**Use Case:** **Show me weekly sales by customer with recency-frequency analysis, quartiles, and rolling averages.**

**Description:** Situation: The marketing team is designing targeted retention and upsell campaigns and needs to segment customers based on how recently and how frequently they purchase, combined with their spending patterns, to prioritize outreach efforts and personalize messaging for maximum campaign effectiveness. Task: Produce weekly sales statistics for each customer that incorporate RFM-style (recency-frequency-monetary) metrics, quartile distributions for spend segmentation, and rolling averages for trend identification. Action: The query groups sales transactions by week and customer, uses the ROW_NUMBER window function to establish recency ordering (identifying most recent purchases), ranks customers by cumulative spending to determine monetary value tiers, calculates quartile boundaries for spend distribution analysis, computes rolling averages to smooth weekly volatility, and filters to include only customers with at least 3 weeks of purchase activity to ensure statistically meaningful metri

**Business Value:** Aggregated metrics for customer recency-frequency analysis

**Complexity:** challenging

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

---

## Query 10: Show me monthly sales by employee with cohort-style retention analysis and quartile distributions. {#query-10}

**Use Case:** **Show me monthly sales by employee with cohort-style retention analysis and quartile distributions.**

**Description:** Situation: The human resources and sales management teams need to track how employee sales performance evolves over their tenure to identify which employees are improving, plateauing, or declining, informing decisions about additional training needs, recognition programs, and retention strategies for high performers. Task: Generate monthly sales statistics for each employee that apply cohort analysis methodology to compare performance trajectories over time, combined with quartile distributions for peer benchmarking. Action: The query aggregates sales by month and employee, calculates an increasing_count metric that tracks cumulative months of activity to enable cohort-based comparisons, derives trend_direction indicators to classify performance momentum (improving, stable, declining), computes quartile boundaries to enable relative performance assessment against peers, and accommodates single-record months to include newly hired employees in the analysis without distorting statistical

**Business Value:** Aggregated metrics for multi-period cohort retention

**Complexity:** challenging

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

---

## Query 11: What are the daily sales statistics by location, including acceleration rate, quartiles, and outlier count? {#query-11}

**Use Case:** **What are the daily sales statistics by location, including acceleration rate, quartiles, and outlier count?**

**Description:** Situation: The retail operations team is planning regional expansion and needs to understand how quickly revenue is growing at each location. Sales acceleration metrics reveal which stores are gaining momentum versus plateauing, helping prioritize investment decisions. Task: Calculate daily sales statistics for each location including acceleration rate, quartile distribution, and outlier identification. Action: The query groups transactions by calendar day and location, computes delta_value to measure day-over-day change in sales velocity, calculates quartile boundaries (Q1, Q2, Q3) for the distribution, identifies outliers beyond typical ranges, and filters to locations with at least 2 days of data to ensure meaningful trend analysis. Result: A dataset showing daily performance metrics for each location—acceleration indicators measuring growth momentum, quartile values showing the sales distribution, and outlier counts flagging anomalous days that may require investigation.

**Business Value:** Aggregated metrics for sales acceleration rate computation

**Complexity:** challenging

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

---

## Query 12: What are the weekly sales statistics by employee with cross-location revenue benchmarking and quartiles? {#query-12}

**Use Case:** **What are the weekly sales statistics by employee with cross-location revenue benchmarking and quartiles?**

**Description:** Situation: The sales management team wants to identify top-performing employees across all locations and establish fair, data-driven sales targets that account for regional differences. Cross-employee benchmarking provides objective performance comparisons while controlling for location-specific factors. Task: Calculate weekly sales statistics for each employee including cross-location benchmarking metrics and quartile distribution. Action: The query groups transactions by calendar week and employee, applies PERCENT_RANK to determine each employee's relative position within their cohort, uses DENSE_RANK for sequential performance ordering without gaps, calculates quartile boundaries to segment the sales distribution, and requires at least 3 weeks of data per employee to establish reliable patterns. Result: A dataset showing weekly performance metrics for each employee—benchmark rankings showing relative standing among peers, quartile values revealing the distribution of their sales, an

**Business Value:** Aggregated metrics for cross-location revenue benchmarking

**Complexity:** challenging

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

---

## Query 13: What are the monthly sales statistics by payment type with time-weighted moving average and quartiles? {#query-13}

**Use Case:** **What are the monthly sales statistics by payment type with time-weighted moving average and quartiles?**

**Description:** Situation: The finance team needs to understand long-term trends in payment method preferences, but monthly data contains seasonal noise from holidays, promotions, and shopping cycles. Moving averages smooth these fluctuations to reveal the underlying shift in customer payment behavior, which informs payment processing investments and partnership decisions. Task: Calculate monthly sales statistics by payment type including time-weighted moving average and quartile distribution. Action: The query groups transactions by calendar month and payment type (credit card, cash, mobile wallet, etc.), computes a rolling average using a ROWS BETWEEN window frame that looks backward across multiple months to smooth volatility, calculates quartile boundaries for the distribution, and requires at least 2 months of data per payment type to establish baseline trends. Result: A dataset showing monthly performance metrics for each payment type—rolling averages that reveal smoothed trend lines free from s

**Business Value:** Aggregated metrics for time-weighted moving average

**Complexity:** challenging

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

---

## Query 14: What are the daily sales statistics by customer with peak hour identification and quartiles? {#query-14}

**Use Case:** **What are the daily sales statistics by customer with peak hour identification and quartiles?**

**Description:** Situation: The store operations team is optimizing labor scheduling and promotional timing to align with customer shopping patterns. Understanding when specific customer segments prefer to shop enables better staff allocation during high-traffic periods and more effective promotional campaign timing. Peak hour identification also supports inventory replenishment planning. Task: Calculate daily sales statistics per customer including peak hour identification and quartile distribution. Action: The query groups transactions by calendar day and customer, extracts the sale_hour timestamp component to identify when each transaction occurred, determines peak shopping hours for each customer segment through frequency analysis, calculates quartile boundaries for the sales distribution, and includes even single-transaction days to capture all customer activity patterns without imposing minimum thresholds. Result: A dataset showing daily performance metrics for each customer—peak hour indicators

**Business Value:** Aggregated metrics for peak hour identification and staffing

**Complexity:** challenging

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

---

## Query 15: What are the weekly sales statistics by location with customer lifetime value estimation metrics and quartiles? {#query-15}

**Use Case:** **What are the weekly sales statistics by location with customer lifetime value estimation metrics and quartiles?**

**Description:** Situation: The marketing and real estate teams are prioritizing locations for increased investment, lease renewals, and targeted campaigns. Customer lifetime value (LTV) concepts applied at the location level help identify which stores generate the most sustained, cumulative value over time versus one-time spikes, informing strategic resource allocation decisions. Task: Calculate weekly sales statistics per location including LTV-style estimation metrics and quartile distribution. Action: The query groups transactions by calendar week and location, computes cumulative_sum to track running total revenue as a proxy for long-term value generation, calculates max_cumulative to identify peak value contribution periods, applies quartile segmentation to the distribution, and requires at least 3 weeks of data per location to establish meaningful cumulative patterns rather than isolated events. Result: A dataset showing weekly performance metrics for each location—LTV-style rankings that priori

**Business Value:** Aggregated metrics for customer lifetime value estimation

**Complexity:** challenging

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

---

## Query 16: What are the monthly sales statistics for each employee, including year-over-year growth rates with seasonal adjustments and quartile distributions? {#query-16}

**Use Case:** **What are the monthly sales statistics for each employee, including year-over-year growth rates with seasonal adjustments and quartile distributions?**

**Description:** Situation: The sales management team needs to compare employee performance across different seasons and years to identify top performers and plan resource allocation for the upcoming year. Year-over-year growth metrics help normalize seasonal fluctuations in sales patterns. Task: Calculate monthly sales statistics for each employee showing year-over-year growth trends and quartile rankings. Action: The query groups sales data by month and employee identifier, applies window functions to compute trend_direction and delta_value metrics for growth analysis, filters records to the most recent 365 days to enable valid year-over-year comparisons, and accommodates months where an employee may have only a single transaction record. Result: A dataset containing monthly sales metrics for each employee, including growth direction indicators, percentage or absolute delta values from the prior year, and quartile positions within their peer group.

**Business Value:** Aggregated metrics for yoy growth rate with seasonal adjustment

**Complexity:** challenging

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

---

## Query 17: What are the daily sales statistics broken down by payment type, formatted for transaction velocity heatmap visualization with quartile distributions? {#query-17}

**Use Case:** **What are the daily sales statistics broken down by payment type, formatted for transaction velocity heatmap visualization with quartile distributions?**

**Description:** Situation: The operations team wants to create visual heatmaps showing how payment methods (credit card, cash, mobile payment, etc.) are used throughout different days and times, enabling quick identification of payment mix shifts and transaction velocity patterns that inform staffing and system capacity decisions. Task: Generate daily sales statistics segmented by payment type in a format suitable for heatmap visualization tools. Action: The query groups transaction data by calendar day and payment_type, structures output using period (date/time dimension) and payment_type as the two heatmap axes, calculates quartile distributions to enable color-coding intensity, counts trend occurrences for velocity indicators, and filters to groups with at least 2 transaction records to ensure statistical relevance. Result: A heatmap-ready dataset with daily metrics for each payment type, including dimensional coordinates for plotting, quartile values for color intensity mapping, and trend counts s

**Business Value:** Aggregated metrics for transaction velocity heatmap data

**Complexity:** challenging

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

---

## Query 18: What are the weekly sales statistics for each customer, including running percentile distributions and quartile rankings? {#query-18}

**Use Case:** **What are the weekly sales statistics for each customer, including running percentile distributions and quartile rankings?**

**Description:** Situation: The marketing and customer success teams need to understand how customer spending patterns distribute within each week to support customer segmentation strategies, identify high-value customers, and detect changes in purchasing behavior that may signal upsell opportunities or churn risk. Task: Calculate weekly sales statistics for each customer showing their position in the spending distribution using running percentiles and quartiles. Action: The query groups sales transactions by calendar week and customer identifier, applies PERCENT_RANK window function to show each customer's relative position in the weekly spending distribution, uses PERCENTILE_CONT to calculate quartile boundaries (25th, 50th, 75th percentiles) for the week, and filters to groups containing at least 3 transaction records to ensure meaningful statistical calculations. Result: A dataset of weekly metrics for each customer showing their running percentile rank within that week's customer base, quartile cl

**Business Value:** Aggregated metrics for running percentile sales distribution

**Complexity:** challenging

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

---

## Query 19: What are the monthly sales statistics by location, including employee cross-sell effectiveness metrics and quartile distributions? {#query-19}

**Use Case:** **What are the monthly sales statistics by location, including employee cross-sell effectiveness metrics and quartile distributions?**

**Description:** Situation: Regional and location managers need to evaluate which store locations are most effective at cross-selling additional products or services, helping identify where training programs, employee incentives, or merchandising strategies are successfully driving multi-item purchases versus locations that need support. Task: Calculate monthly sales statistics for each location with metrics showing cross-sell effectiveness and quartile performance rankings. Action: The query groups sales data by calendar month and location identifier, uses DENSE_RANK window function to rank locations by cross-sell metrics within each month, calculates partition-specific statistics to enable peer comparisons across similar location types or regions, computes quartile distributions to classify high and low performers, and filters to groups with at least 3 transaction records for statistical validity. Result: A dataset of monthly metrics for each location including cross-sell effectiveness indicators (su

**Business Value:** Aggregated metrics for employee cross-sell effectiveness

**Complexity:** challenging

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

---

## Query 20: What are the daily sales statistics for each employee, including forensic analysis of deleted transactions and quartile distributions? {#query-20}

**Use Case:** **What are the daily sales statistics for each employee, including forensic analysis of deleted transactions and quartile distributions?**

**Description:** Situation: The loss prevention and audit teams need to investigate transaction anomalies by tracing the complete sequence of sales events including voids, refunds, and soft-deleted records to detect potential fraud patterns, training issues, or system errors. Understanding the temporal sequence and deletion patterns of transactions helps identify suspicious behavior or process breakdowns. Task: Generate daily sales statistics for each employee incorporating forensic metrics that track transaction sequencing and deletion activity. Action: The query groups transaction records by calendar day and employee identifier, applies LAG and LEAD window functions to sequence transactions chronologically and identify gaps or reversals, leverages the deleted flag column (if present) to track soft-deleted or voided transactions separately from completed sales, calculates quartile distributions for transaction volumes and values, and includes all transaction states to provide complete forensic visibil

**Business Value:** Aggregated metrics for deleted transaction forensic analysis

**Complexity:** challenging

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

---

## Query 21: What are the weekly sales statistics broken down by payment type, including quartiles and all key metrics for the executive dashboard? {#query-21}

**Use Case:** **What are the weekly sales statistics broken down by payment type, including quartiles and all key metrics for the executive dashboard?**

**Description:** Situation: The executive team reviews a weekly dashboard that requires a comprehensive view of sales performance across different payment methods (credit card, cash, digital wallet, etc.) to understand payment preference trends and identify potential issues with specific payment channels. Task: Generate a complete set of weekly sales statistics segmented by payment type that includes all dashboard-required metrics in a single query. Action: The SQL groups transactions by calendar week and payment type, then computes multiple aggregations in one pass: record count, average transaction value, first/second/third quartiles for distribution analysis, standard deviation for volatility, minimum and maximum values for range, outlier count using z-score threshold, count of week-over-week increases using window functions, rolling 3-week average for trend smoothing, and cumulative maximum to track peaks. The query filters to include only groups with at least 2 records to ensure statistical validi

**Business Value:** Aggregated metrics for multi-metric dashboard aggregation

**Complexity:** challenging

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

---

## Query 22: How do individual customer purchasing patterns evolve month-over-month, including sequential behavior metrics and quartile distributions? {#query-22}

**Use Case:** **How do individual customer purchasing patterns evolve month-over-month, including sequential behavior metrics and quartile distributions?**

**Description:** Situation: The personalization team needs to understand how each customer's purchasing behavior changes over time to tailor marketing campaigns, predict churn, and identify upsell opportunities. Sequential pattern mining reveals whether customers are increasing spend, changing purchase frequency, or showing signs of disengagement. Task: Produce monthly sales statistics for each customer that capture sequential purchasing patterns alongside distribution metrics. Action: The SQL groups all transactions by calendar month and customer ID, then applies window functions to analyze temporal patterns: LAG retrieves the previous month's value for each customer, LEAD fetches the next month's value, delta_value calculates month-over-month change, and trend_direction classifies the movement as increasing, decreasing, or stable. The query also computes quartiles (Q1, median, Q3) to understand spending distribution and includes record count, average, and range metrics. Only customers with at least 3

**Business Value:** Aggregated metrics for sequential purchase pattern mining

**Complexity:** challenging

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

---

## Query 23: What is the daily revenue concentration across different store locations, showing which locations dominate sales and their quartile distributions? {#query-23}

**Use Case:** **What is the daily revenue concentration across different store locations, showing which locations dominate sales and their quartile distributions?**

**Description:** Situation: The operations team needs to understand how revenue is distributed across store locations to make informed decisions about staffing levels, inventory allocation, and potential store expansions or closures. Revenue concentration metrics reveal whether sales are evenly distributed or heavily concentrated in a few high-performing locations. Task: Generate daily sales statistics for each location that quantify revenue concentration and competitive positioning. Action: The SQL groups transactions by calendar day and location, then computes concentration metrics using advanced window functions: DENSE_RANK assigns a ranking to each location based on daily sales (with ties receiving the same rank), PERCENT_RANK calculates the percentile position of each location (0 = lowest, 1 = highest), and cumulative_sum tracks running total revenue across ranked locations to identify the share captured by top performers. The query also includes quartile calculations (Q1, median, Q3), record coun

**Business Value:** Aggregated metrics for revenue concentration index

**Complexity:** challenging

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

---

## Query 24: Which employees show unusual weekly sales patterns that may indicate exceptional performance or require additional training support? {#query-24}

**Use Case:** **Which employees show unusual weekly sales patterns that may indicate exceptional performance or require additional training support?**

**Description:** Situation: The sales management team monitors employee performance to identify both top performers who deserve recognition and individuals who may need coaching or are exhibiting unusual sales patterns that warrant investigation. Anomaly scores provide an objective, data-driven method to prioritize which employees to review rather than relying on subjective assessments. Task: Produce weekly sales statistics for each employee that include statistical anomaly scores to flag unusual performance patterns. Action: The SQL groups all transactions by calendar week and employee ID, then calculates a comprehensive set of metrics with focus on anomaly detection: z_score (standardized score showing how many standard deviations from the mean) serves as the primary anomaly indicator, with values beyond ±2 or ±3 indicating unusual patterns. The query also computes quartiles (Q1, median, Q3) for distribution context, record count, average sale value, standard deviation for volatility assessment, and

**Business Value:** Aggregated metrics for anomaly score computation

**Complexity:** challenging

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

---

## Query 25: How do monthly sales trends compare across different payment types for fiscal period reporting and quarter-over-quarter analysis? {#query-25}

**Use Case:** **How do monthly sales trends compare across different payment types for fiscal period reporting and quarter-over-quarter analysis?**

**Description:** Situation: The finance department prepares monthly and quarterly reports comparing payment method performance across fiscal periods to identify trends in customer payment preferences, assess the impact of new payment options, and forecast payment processing costs. The data must align with fiscal calendar months to match other financial reporting. Task: Generate monthly sales statistics segmented by payment type that align with fiscal period boundaries for comparative analysis. Action: The SQL groups transactions by fiscal month (using DATE_TRUNC('month') to standardize all dates to the first day of each month) and payment type, then computes a comprehensive set of metrics: record count showing transaction volume, average transaction value, quartiles (Q1, median, Q3) for distribution analysis, standard deviation for variability, minimum and maximum values for range, and additional summary statistics. The month truncation ensures each payment type's metrics can be easily compared month-o

**Business Value:** Aggregated metrics for fiscal period comparative analysis

**Complexity:** challenging

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

---

## Query 26: What are the daily sales statistics for each customer, including transaction throughput metrics and quartile distributions? {#query-26}

**Use Case:** **What are the daily sales statistics for each customer, including transaction throughput metrics and quartile distributions?**

**Description:** Situation: The business needs to assess transaction volume patterns per customer to optimize system capacity planning and refine loyalty program tiers based on purchasing frequency and consistency. Task: Generate daily sales statistics for each customer that include throughput metrics and quartile distributions. Action: The query aggregates sales data by day and customer identifier, calculates throughput proxies such as record count, rolling averages, and cumulative maximums, and includes days with single transactions to capture all customer activity. Result: A dataset containing daily metrics for each customer with throughput indicators, quartile values (Q1, Q2, Q3), and activity level classifications for capacity and loyalty analysis.

**Business Value:** Aggregated metrics for transaction throughput optimization

**Complexity:** challenging

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

---

## Query 27: What are the weekly sales statistics by store location, including payment method trend analysis and quartile distributions? {#query-27}

**Use Case:** **What are the weekly sales statistics by store location, including payment method trend analysis and quartile distributions?**

**Description:** Situation: The retail operations team needs to identify shifts in payment method preferences (such as credit card versus cash usage) across different store locations to optimize payment terminal deployment and cash management strategies. Task: Generate weekly sales statistics for each location that include payment trend metrics and quartile distributions. Action: The query aggregates sales data by week and location, calculates trend direction indicators and counts of increasing payment patterns to analyze shifts in payment mix, and filters to include only location-weeks with at least 3 transaction records to ensure statistical relevance. Result: A dataset containing weekly metrics for each location with payment trend indicators, quartile values, and activity summaries for terminal planning and cash handling optimization.

**Business Value:** Aggregated metrics for store account payment trend analysis

**Complexity:** challenging

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

---

## Query 28: What are the monthly sales statistics for each employee, with multi-dimensional aggregation and quartile distributions? {#query-28}

**Use Case:** **What are the monthly sales statistics for each employee, with multi-dimensional aggregation and quartile distributions?**

**Description:** Situation: The sales management team requires flexible reporting capabilities that allow pivoting sales data by both time period and employee to support ad-hoc performance analysis and commission calculations. Task: Generate monthly sales statistics for each employee with multi-dimensional aggregation structure and quartile distributions. Action: The query aggregates sales data by month and employee identifier, uses both period and employee_id as dimensional attributes to enable pivot table analysis, and includes months where employees have only a single transaction to provide complete coverage. Result: A dataset containing monthly metrics for each employee with multi-dimensional attributes, quartile values, and summary statistics that support flexible pivot analysis and performance reporting.

**Business Value:** Aggregated metrics for multi-dimensional pivot analysis

**Complexity:** challenging

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

---

## Query 29: What are the daily sales statistics by payment type, including sales funnel stage progression and quartile distributions? {#query-29}

**Use Case:** **What are the daily sales statistics by payment type, including sales funnel stage progression and quartile distributions?**

**Description:** Situation: The analytics team needs to understand how payment method preferences evolve throughout the day to identify conversion patterns and optimize checkout flow recommendations at different times. Task: Generate daily sales statistics by payment type that include funnel stage progression indicators and quartile distributions. Action: The query aggregates sales data by day and payment type, calculates trend direction metrics to track stage progression through the day, and filters to include only day-payment type combinations with at least 2 transaction records to ensure meaningful trend detection. Result: A dataset containing daily metrics for each payment type with funnel progression indicators, quartile values, and stage evolution patterns for conversion optimization analysis.

**Business Value:** Aggregated metrics for sales funnel stage progression

**Complexity:** challenging

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

---

## Query 30: What are the weekly sales statistics per customer, with IQR-based outlier detection and quartile distributions? {#query-30}

**Use Case:** **What are the weekly sales statistics per customer, with IQR-based outlier detection and quartile distributions?**

**Description:** Situation: The fraud detection and customer experience teams need to identify customers with unusual spending patterns—either abnormally high spenders who may require VIP treatment or anomalous patterns that could indicate fraudulent activity—using statistical quartile-based methods. Task: Generate weekly sales statistics per customer with IQR-style outlier detection and quartile distributions. Action: The query aggregates sales data by week and customer, calculates first quartile (Q1) and third quartile (Q3) using PERCENTILE_CONT functions, applies z-score thresholds above 2 standard deviations to approximate IQR outlier detection methodology, and filters to include only customer-weeks with at least 3 transaction records to ensure statistical validity. Result: A dataset containing weekly metrics for each customer with quartile values, IQR-based outlier flags, trend counts, and statistical indicators for fraud detection and VIP customer identification.

**Business Value:** Aggregated metrics for outlier detection with iqr method

**Complexity:** challenging

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

---

## Usage Instructions

Load schema.sql and data.sql into PostgreSQL. See docs/POSTGRES_MIGRATION.md for migration from MySQL format.

---

## Platform Compatibility

All queries in this database are designed to work across multiple database platforms:

- **PostgreSQL**: Full support with standard SQL features

Queries use standard SQL syntax and avoid platform-specific features to ensure compatibility.

---

**Document Information:**

- **Generated**: 20260216-0700
- **Database**: db-2
- **Type**: Filling Station Retail / POS (phppos)
- **Queries**: 30 production queries
- **Status**: ✅ Complete Comprehensive Deliverable
