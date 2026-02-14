# db-12 ACID and Query Execution Test Report

**Report Date:** 2026-02-10  
**Database:** db-12 (Credit Card and Rewards Optimization System)  
**Test Environment:** Independent PostgreSQL 15 with PostGIS (Docker: port 5433)

---

## ACID Compliance Test Results

| Property | Status | Description |
|----------|--------|-------------|
| **Atomicity** | ✓ PASS | Rollback prevents partial updates – uncommitted inserts are fully rolled back |
| **Consistency** | ✓ PASS | Foreign key constraints enforced – invalid FKs rejected |
| **Isolation** | ✓ PASS | Isolation level: read committed |
| **Durability** | ✓ PASS | Data persists after commit |

**ACID Overall: PASS** – PostgreSQL meets all ACID requirements for db-12.

---

## SQL Query Execution Results

| Metric | Value |
|--------|-------|
| Total Queries | 30 |
| Successful | 1 |
| Failed | 29 |
| Success Rate | 3.33% |

### Successful Queries

| # | Title | Execution Time | Rows |
|---|-------|----------------|------|
| 1 | Multi-Dimensional Rewards Optimization Analysis with Card Portfolio Comparison and Opportunity Cost Calculation | 44.4 ms | 0 |

*Query 1 returned 0 rows due to data conditions (user_001 spending patterns); the query executed correctly.*

### Failure Categories

1. **Syntax Errors (Queries 2–8, 10)**  
   - `THEN` / `ELSE` in CASE expressions  
   - `INTERVAL '24 months'` – PostgreSQL uses `INTERVAL '24 months'` (valid) but some expressions use `INTERVAL 'cc.signup_bonus_timeframe_months MONTH'` (invalid)  
   - `DATEDIFF` – not in PostgreSQL (use `EXTRACT` or date subtraction)  
   - `DATE_ADD` – not in PostgreSQL (use `+ INTERVAL`)

2. **Column Not Found (Query 9)**  
   - `mcr.transaction_count` – alias or column missing in the referenced CTE/view

3. **DISTINCT in Window Functions (Queries 11–30)**  
   - PostgreSQL does not support `COUNT(DISTINCT x) OVER (...)`  
   - Requires rewriting, e.g. using subqueries or different aggregation patterns

---

## Recommendations

1. **Syntax compatibility** – Replace Snowflake/other-dialect constructs with PostgreSQL equivalents:
   - `DATE_ADD(d, n)` → `d + INTERVAL 'n'`
   - `DATEDIFF('month', a, b)` → `EXTRACT(YEAR FROM AGE(b, a)) * 12 + EXTRACT(MONTH FROM AGE(b, a))`
   - `INTERVAL 'x MONTH'` with variables → use `make_interval()` or dynamic SQL

2. **Window functions** – Replace `COUNT(DISTINCT x) OVER (...)` with:
   - Subqueries, or  
   - `DENSE_RANK()`-based counting, or  
   - Pre-aggregation in CTEs

3. **Schema/query alignment** – Ensure CTE column names and aliases match usage (e.g. Query 9).

---

## Test Setup

- **PostgreSQL:** 15 with PostGIS  
- **Database:** db12  
- **Schema:** PostgreSQL-compatible (TIMESTAMP_NTZ → TIMESTAMP, PostGIS)  
- **Data:** Sample issuers, cards, categories, merchants, offers, user_profiles, user_cards, spending_transactions, merchant_locations, CFPB complaints, Federal Reserve data  

Full JSON report: `db-12/results/acid_query_test_report.json`
