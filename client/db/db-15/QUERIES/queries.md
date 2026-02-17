# Electricity Cost and Solar Rebate Database — Query Documentation

## Database Overview

```yaml
db_id: db-15
domain: Electricity / Solar
source: [commercial]
license_type: [Commercial]
license_cost: [NDA]
tables: 17
total_rows: ~105
date_range: 2020-01-01 to 2026-12-31
sql_dialect: PostgreSQL
```

## Purpose

```text
This database supports analytics for electricity cost intelligence and solar rebate programs.
It models U.S. states, counties, zip codes, utility companies, rate structures, electricity
rates (flat, tiered, time-of-use), federal/state/utility incentives, and geographic rate
areas. It is designed to support text-to-SQL training across rate comparison, incentive
eligibility, and solar ROI query types commonly encountered in energy analytics.
```

## Use Case

```text
Target use cases for db-15:
- Rate comparison: compare electricity rates across utilities, states, rate codes
- Solar ROI: aggregate federal, state, and utility incentives by location
- Geographic analytics: rates and incentives by zip, county, state
- Rate structure analysis: tiered vs TOU vs flat; demand charges; fixed charges
- Incentive eligibility: minimum/maximum system size, effective/expiration dates
```

## Business Value

```text
Electricity and solar databases represent high-value domains for text-to-SQL because:
- Queries require understanding of rate structures (tiers, TOU periods, demand charges)
- Incentive stacking (federal + state + utility) requires multi-table joins
- Stakeholders need location-based analytics (installers, homeowners, utilities)
- Evidence bridges natural-language questions to schema-grounded SQL.
```

## Schema

```sql
-- PostgreSQL-specific schema file
-- Generated from schema.sql
-- Generated: 2026-02-05 19:10:13
-- Database: db-15
-- 
-- This file contains PostgreSQL-specific SQL syntax.
-- Use this file when setting up the database in PostgreSQL.
--

-- Electricity Cost Intelligence and Solar Rebate Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for electricity cost intelligence and solar rebate system

-- States Table
-- Stores U.S. state information
CREATE TABLE states (
    state_id VARCHAR(2) PRIMARY KEY,  -- Two-letter state code (e.g., 'CA', 'NY')
    state_name VARCHAR(100) NOT NULL,
    state_full_name VARCHAR(100),
    region VARCHAR(50),  -- 'Northeast', 'South', 'Midwest', 'West'
    division VARCHAR(50),  -- Census division
    timezone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Counties Table
-- Stores county information for geographic rate areas
CREATE TABLE counties (
    county_id VARCHAR(255) PRIMARY KEY,
    state_id VARCHAR(2) NOT NULL,
    county_name VARCHAR(100) NOT NULL,
    county_fips_code VARCHAR(5),  -- 5-digit FIPS code
    county_seat VARCHAR(100),
    population INTEGER,
    area_sq_miles NUMERIC(10, 2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- Zip Codes Table
-- Stores zip code information for location-based rate queries
CREATE TABLE zip_codes (
    zip_code VARCHAR(10) PRIMARY KEY,
    state_id VARCHAR(2) NOT NULL,
    county_id VARCHAR(255),
    city VARCHAR(100),
    latitude NUMERIC(10, 7),  -- WGS84
    longitude NUMERIC(10, 7),  -- WGS84
    timezone VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (county_id) REFERENCES counties(county_id)
);

-- Utility Companies Table
-- Stores electric utility company information
CREATE TABLE utility_companies (
    utility_
-- ...
```

## Domain Knowledge

```text
Key domain concepts required to write correct queries against this database:

GEOGRAPHY:
- states: state_id (2-letter), region, division
- counties: county_fips_code (5-digit), links to state
- zip_codes: links to state/county; latitude/longitude WGS84

UTILITIES AND RATES:
- utility_companies: utility_type (Investor-Owned, Municipal, Cooperative, etc.)
- rate_structures: effective_date, expiration_date, approval_status
- electricity_rates: fixed_charge_usd, energy_charge_usd_per_kwh, demand_charge_usd_per_kw
- rate_structure_type: Flat, Tiered, Time-of-Use, Demand, Hybrid

TIERED AND TOU:
- tiered_rate_tiers: tier_start_kwh, tier_end_kwh (NULL = unlimited)
- time_of_use_periods: period_name (Peak, Off-Peak, Super Off-Peak); period_start_time, period_end_time; season (Summer, Winter, All)

INCENTIVES:
- federal_incentives, state_incentives, utility_incentives
- incentive_type: Tax Credit, Rebate, Grant, Net Metering, Feed-in Tariff
- incentive_unit: per_watt, per_kwh, percentage, fixed_amount
- minimum_system_size_kw, maximum_system_size_kw for eligibility
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
  "db_id": "db-15",
  "question_id": 1,
  "question": "Can you show me a multi-level electricity rate analysis that includes geographic aggregations and rate code breakdowns?",
  "SQL": "WITH state_rate_summary AS (\n    -- First CTE: Aggregate rates by state with comprehensive metrics\n    SELECT\n        s.state_id,\n        s.state_name,\n        s.region,\n        s.division,\n        COUNT(DISTINCT er.utility_id) AS utility_count,\n        COUNT(DISTINCT er.rate_code_id) AS rate_code_count,\n        COUNT(DISTINCT er.rate_id) AS total_rate_count,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_energy_charge,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS median_energy_charge,\n        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS q1_energy_charge,\n        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS q3_energy_charge,\n        MIN(er.energy_charge_usd_per_kwh) AS min_energy_charge,\n        MAX(er.energy_charge_usd_per_kwh) AS max_energy_charge,\n        STDDEV(er.energy_charge_usd_per_kwh) AS stddev_energy_charge,\n        AVG(er.fixed_charge_usd) AS avg_fixed_charge,\n        AVG(er.demand_charge_usd_per_kw) AS avg_demand_charge\n    FROM states s\n    INNER JOIN electricity_rates er ON s.state_id = er.state_id\n    WHERE er.is_current = TRUE\n    GROUP BY s.state_id, s.state_name, s.region, s.division\n),\nutility_rate_analysis AS (\n    -- Second CTE: Analyze rates by utility with rate code breakdown\n    SELECT\n        uc.utility_id,\n        uc.utility_name,\n        uc.utility_type,\n        uc.state_id,\n        COUNT(DISTINCT er.rate_code_id) AS rate_codes_offered,\n        COUNT(DISTINCT er.rate_id) AS total_rates,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_energy_charge,\n        MIN(er.energy_charge_usd_per_kwh) AS min_energy_charge,\n        MAX(er.energy_charge_usd_per_kwh) AS max_energy_charge,\n        AVG(er.fixed_charge_usd) AS avg_fixed_charge,\n        AVG(er.demand_charge_usd_per_kw) AS avg_demand_charge,\n        COUNT(DISTINCT CASE WHEN er.rate_type = 'Residential' THEN er.rate_id END) AS residential_rate_count,\n        COUNT(DISTINCT CASE WHEN er.rate_type = 'Commercial' THEN er.rate_id END) AS commercial_rate_count,\n        COUNT(DISTINCT CASE WHEN er.rate_type = 'Industrial' THEN er.rate_id END) AS industrial_rate_count\n    FROM utility_companies uc\n    INNER JOIN electricity_rates er ON uc.utility_id = er.utility_id\n    WHERE er.is_current = TRUE\n        AND uc.is_active = TRUE\n    GROUP BY uc.utility_id, uc.utility_name, uc.utility_type, uc.state_id\n),\nrate_code_intelligence AS (\n    -- Third CTE: Rate code analysis with structure type breakdown\n    SELECT\n        rc.rate_code_id,\n        rc.rate_code,\n        rc.rate_code_category,\n        rc.sector,\n        rc.rate_structure_type,\n        COUNT(DISTINCT er.utility_id) AS utilities_offering_code,\n        COUNT(DISTINCT er.state_id) AS states_with_code,\n        COUNT(DISTINCT er.rate_id) AS total_rates,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_energy_charge,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS median_energy_charge,\n        STDDEV(er.energy_charge_usd_per_kwh) AS stddev_energy_charge,\n        AVG(er.fixed_charge_usd) AS avg_fixed_charge,\n        AVG(er.demand_charge_usd_per_kw) AS avg_demand_charge\n    FROM rate_codes rc\n    INNER JOIN electricity_rates er ON rc.rate_code_id = er.rate_code_id\n    WHERE er.is_current = TRUE\n        AND rc.is_active = TRUE\n    GROUP BY rc.rate_code_id, rc.rate_code, rc.rate_code_category, rc.sector, rc.rate_structure_type\n),\ngeographic_rate_analysis AS (\n    -- Fourth CTE: Geographic rate analysis by zip code and county\n    SELECT\n        gra.rate_area_id,\n        gra.state_id,\n        gra.county_id,\n        gra.zip_code,\n        COUNT(DISTINCT gra.rate_structure_id) AS rate_structures_in_area,\n        COUNT(DISTINCT rs.utility_id) AS utilities_in_area,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_area_energy_charge,\n        MIN(er.energy_charge_usd_per_kwh) AS min_area_energy_charge,\n        MAX(er.energy_charge_usd_per_kwh) AS max_area_energy_charge\n    FROM geographic_rate_areas gra\n    INNER JOIN rate_structures rs ON gra.rate_structure_id = rs.rate_structure_id\n    INNER JOIN electricity_rates er ON rs.rate_structure_id = er.rate_structure_id\n    WHERE gra.expiration_date IS NULL OR gra.expiration_date > CURRENT_DATE\n        AND er.is_current = TRUE\n    GROUP BY gra.rate_area_id, gra.state_id, gra.county_id, gra.zip_code\n),\nrate_comparison_metrics AS (\n    -- Fifth CTE: Rate comparison metrics with window functions\n    SELECT\n        er.rate_id,\n        er.utility_id,\n        er.state_id,\n        er.rate_code_id,\n        er.energy_charge_usd_per_kwh,\n        er.fixed_charge_usd,\n        er.demand_charge_usd_per_kw,\n        -- Window functions for rate comparisons\n        AVG(er.energy_charge_usd_per_kwh) OVER (\n            PARTITION BY er.state_id, er.rate_type\n        ) AS state_avg_energy_charge,\n        AVG(er.energy_charge_usd_per_kwh) OVER (\n            PARTITION BY er.utility_id\n        ) AS utility_avg_energy_charge,\n        PERCENT_RANK() OVER (\n            PARTITION BY er.state_id\n            ORDER BY er.energy_charge_usd_per_kwh\n        ) AS state_rate_percentile,\n        ROW_NUMBER() OVER (\n            PARTITION BY er.state_id, er.rate_type\n            ORDER BY er.energy_charge_usd_per_kwh\n        ) AS state_rate_rank,\n        NTILE(4) OVER (\n            PARTITION BY er.state_id\n            ORDER BY er.energy_charge_usd_per_kwh\n        ) AS state_rate_quartile,\n        LAG(er.energy_charge_usd_per_kwh, 1) OVER (\n            PARTITION BY er.utility_id, er.rate_code_id\n            ORDER BY er.effective_date\n        ) AS prev_energy_charge,\n        LEAD(er.energy_charge_usd_per_kwh, 1) OVER (\n            PARTITION BY er.utility_id, er.rate_code_id\n            ORDER BY er.effective_date\n        ) AS next_energy_charge\n    FROM electricity_rates er\n    WHERE er.is_current = TRUE\n),\nrate_trend_analysis AS (\n    -- Sixth CTE: Rate trend analysis with historical comparisons\n    SELECT\n        rcm.rate_id,\n        rcm.utility_id,\n        rcm.state_id,\n        rcm.rate_code_id,\n        rcm.energy_charge_usd_per_kwh,\n        rcm.fixed_charge_usd,\n        rcm.demand_charge_usd_per_kw,\n        rcm.state_avg_energy_charge,\n        rcm.utility_avg_energy_charge,\n        rcm.state_rate_percentile,\n        rcm.state_rate_rank,\n        rcm.state_rate_quartile,\n        rcm.prev_energy_charge,\n        rcm.next_energy_charge,\n        -- Rate change calculations\n        CASE\n            WHEN rcm.prev_energy_charge IS NOT NULL THEN\n                rcm.energy_charge_usd_per_kwh - rcm.prev_energy_charge\n            ELSE NULL\n        END AS energy_charge_change,\n        CASE\n            WHEN rcm.prev_energy_charge IS NOT NULL AND rcm.prev_energy_charge != 0 THEN\n                ((rcm.energy_charge_usd_per_kwh - rcm.prev_energy_charge) / ABS(rcm.prev_energy_charge)) * 100\n            ELSE NULL\n        END AS energy_charge_change_percentage,\n        -- Rate competitiveness metrics\n        CASE\n            WHEN rcm.energy_charge_usd_per_kwh < rcm.state_avg_energy_charge THEN 'Below Average'\n            WHEN rcm.energy_charge_usd_per_kwh = rcm.state_avg_energy_charge THEN 'Average'\n            ELSE 'Above Average'\n        END AS competitiveness_classification,\n        -- Historical rate comparison\n        (\n            SELECT AVG(her.energy_charge_usd_per_kwh)\n            FROM historical_electricity_rates her\n            WHERE her.utility_id = rcm.utility_id\n                AND her.rate_code_id = rcm.rate_code_id\n                AND her.effective_date >= CURRENT_DATE - INTERVAL '12 months'\n        ) AS historical_12mo_avg\n    FROM rate_comparison_metrics rcm\n),\nfinal_rate_intelligence AS (\n    -- Seventh CTE: Final intelligence aggregation with comprehensive metrics\n    SELECT\n        rta.rate_id,\n        rta.utility_id,\n        rta.state_id,\n        rta.rate_code_id,\n        srs.state_name,\n        srs.region,\n        srs.division,\n        ura.utility_name,\n        ura.utility_type,\n        rci.rate_code,\n        rci.rate_code_category,\n        rci.sector,\n        rci.rate_structure_type,\n        rta.energy_charge_usd_per_kwh,\n        rta.fixed_charge_usd,\n        rta.demand_charge_usd_per_kw,\n        rta.state_avg_energy_charge,\n        rta.utility_avg_energy_charge,\n        ROUND(CAST(rta.state_rate_percentile * 100 AS NUMERIC), 2) AS state_rate_percentile,\n        rta.state_rate_rank,\n        rta.state_rate_quartile,\n        ROUND(CAST(rta.energy_charge_change AS NUMERIC), 6) AS energy_charge_change,\n        ROUND(CAST(rta.energy_charge_change_percentage AS NUMERIC), 2) AS energy_charge_change_percentage,\n        rta.competitiveness_classification,\n        ROUND(CAST(rta.historical_12mo_avg AS NUMERIC), 6) AS historical_12mo_avg,\n        srs.utility_count,\n        srs.rate_code_count,\n        srs.total_rate_count,\n        ura.rate_codes_offered,\n        ura.total_rates,\n        rci.utilities_offering_code,\n        rci.states_with_code\n    FROM rate_trend_analysis rta\n    INNER JOIN state_rate_summary srs ON rta.state_id = srs.state_id\n    INNER JOIN utility_rate_analysis ura ON rta.utility_id = ura.utility_id\n    INNER JOIN rate_code_intelligence rci ON rta.rate_code_id = rci.rate_code_id\n)\nSELECT\n    rate_id,\n    utility_id,\n    utility_name,\n    utility_type,\n    state_id,\n    state_name,\n    region,\n    division,\n    rate_code_id,\n    rate_code,\n    rate_code_category,\n    sector,\n    rate_structure_type,\n    energy_charge_usd_per_kwh,\n    fixed_charge_usd,\n    demand_charge_usd_per_kw,\n    state_avg_energy_charge,\n    utility_avg_energy_charge,\n    state_rate_percentile,\n    state_rate_rank,\n    state_rate_quartile,\n    energy_charge_change,\n    energy_charge_change_percentage,\n    competitiveness_classification,\n    historical_12mo_avg,\n    utility_count,\n    rate_code_count,\n    total_rate_count,\n    rate_codes_offered,\n    total_rates,\n    utilities_offering_code,\n    states_with_code\nFROM final_rate_intelligence\nORDER BY state_name, utility_name, rate_code, energy_charge_usd_per_kwh;",
  "evidence": "The query groups data by relevant geographic and utility dimensions, computes summary statistics including aggregates and quartile distributions, applies window functions to calculate rolling averages and comparative metrics across time periods and regions, and implements robust NULL handling in joins to ensure data completeness across date ranges.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "states",
    "electricity_rates",
    "utility_companies",
    "rate_codes",
    "geographic_rate_areas",
    "rate_structures",
    "historical_electricity_rates",
    "rate_comparison_metrics",
    "rate_trend_analysis",
    "state_rate_summary",
    "utility_rate_analysis",
    "rate_code_intelligence",
    "final_rate_intelligence"
  ],
  "schema_context": {},
  "expected_output": "Comprehensive rate analysis with geographic aggregations, rate code classifications, utility comparisons, and cost intelligence metrics.",
  "normal_query": "Comprehensive rate analysis with geographic aggregations, rate code classifications, utility comparisons, and cost intelligence metrics"
}
```


### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 2,
  "question": "Can you show me a recursive rate structure analysis with tiered rate calculations and time-of-use optimization recommendations?",
  "SQL": "WITH RECURSIVE tiered_rate_calculations AS (\n    -- Anchor CTE: Base tier calculations for tiered rates\n    SELECT\n        trt.tier_id,\n        trt.rate_structure_id,\n        trt.tier_number,\n        trt.tier_name,\n        trt.tier_start_kwh,\n        trt.tier_end_kwh,\n        trt.energy_charge_usd_per_kwh,\n        rs.utility_id,\n        rs.rate_code_id,\n        er.state_id,\n        -- Calculate tier range\n        CASE\n            WHEN trt.tier_end_kwh IS NULL THEN 999999\n            ELSE trt.tier_end_kwh - trt.tier_start_kwh\n        END AS tier_kwh_range,\n        -- Tier usage scenarios\n        0 AS cumulative_kwh_usage,\n        trt.tier_start_kwh AS scenario_start_kwh,\n        COALESCE(trt.tier_end_kwh, 999999) AS scenario_end_kwh\n    FROM tiered_rate_tiers trt\n    INNER JOIN rate_structures rs ON trt.rate_structure_id = rs.rate_structure_id\n    INNER JOIN electricity_rates er ON rs.rate_structure_id = er.rate_structure_id\n    WHERE rs.is_current = TRUE\n        AND er.is_current = TRUE\n        AND trt.expiration_date IS NULL OR trt.expiration_date > CURRENT_DATE\n\n    UNION ALL\n\n    -- Recursive step: Calculate cumulative tier costs\n    SELECT\n        trc.tier_id,\n        trc.rate_structure_id,\n        trc.tier_number,\n        trc.tier_name,\n        trc.tier_start_kwh,\n        trc.tier_end_kwh,\n        trc.energy_charge_usd_per_kwh,\n        trc.utility_id,\n        trc.rate_code_id,\n        trc.state_id,\n        trc.tier_kwh_range,\n        trc.cumulative_kwh_usage + trc.tier_kwh_range,\n        trc.scenario_start_kwh,\n        trc.scenario_end_kwh\n    FROM tiered_rate_calculations trc\n    INNER JOIN tiered_rate_tiers trt ON (\n        trt.rate_structure_id = trc.rate_structure_id\n        AND trt.tier_number = trc.tier_number + 1\n    )\n    WHERE trc.cumulative_kwh_usage < 10000\n),\ntou_period_analysis AS (\n    -- Second CTE: Time-of-use period analysis with period aggregations\n    SELECT\n        tou.tou_period_id,\n        tou.rate_structure_id,\n        tou.period_name,\n        tou.period_start_time,\n        tou.period_end_time,\n        tou.day_of_week,\n        tou.season,\n        tou.energy_charge_usd_per_kwh,\n        rs.utility_id,\n        rs.rate_code_id,\n        er.state_id,\n        -- Calculate period duration in hours\n        CASE\n            WHEN tou.period_end_time > tou.period_start_time THEN\n                EXTRACT(EPOCH FROM (tou.period_end_time - tou.period_start_time)) / 3600\n            ELSE\n                EXTRACT(EPOCH FROM (tou.period_end_time + INTERVAL '24 hours' - tou.period_start_time)) / 3600\n        END AS period_duration_hours,\n        -- Period cost scenarios\n        CASE\n            WHEN tou.period_name LIKE '%Peak%' THEN 'High Cost'\n            WHEN tou.period_name LIKE '%Off-Peak%' THEN 'Low Cost'\n            ELSE 'Medium Cost'\n        END AS period_cost_category\n    FROM time_of_use_periods tou\n    INNER JOIN rate_structures rs ON tou.rate_structure_id = rs.rate_structure_id\n    INNER JOIN electricity_rates er ON rs.rate_structure_id = er.rate_structure_id\n    WHERE rs.is_current = TRUE\n        AND er.is_current = TRUE\n        AND tou.expiration_date IS NULL OR tou.expiration_date > CURRENT_DATE\n),\nusage_scenario_modeling AS (\n    -- Third CTE: Model usage scenarios for cost calculations\n    SELECT\n        usage_kwh,\n        usage_scenario_name\n    FROM (\n        VALUES\n            (500, 'Low Usage'),\n            (1000, 'Medium Usage'),\n            (2000, 'High Usage'),\n            (5000, 'Very High Usage')\n    ) AS scenarios(usage_kwh, usage_scenario_name)\n),\ntiered_rate_cost_calculations AS (\n    -- Fourth CTE: Calculate costs for tiered rates across usage scenarios\n    SELECT\n        trc.rate_structure_id,\n        trc.utility_id,\n        trc.rate_code_id,\n        trc.state_id,\n        usm.usage_kwh,\n        usm.usage_scenario_name,\n        SUM(\n            CASE\n                WHEN usm.usage_kwh >= trc.tier_start_kwh THEN\n                    CASE\n                        WHEN trc.tier_end_kwh IS NULL OR usm.usage_kwh <= trc.tier_end_kwh THEN\n                            (usm.usage_kwh - trc.tier_start_kwh + 1) * trc.energy_charge_usd_per_kwh\n                        ELSE\n                            trc.tier_kwh_range * trc.energy_charge_usd_per_kwh\n                    END\n                ELSE 0\n            END\n        ) AS tiered_energy_cost,\n        MAX(trc.tier_number) AS tiers_applied,\n        COUNT(DISTINCT trc.tier_id) AS tier_count\n    FROM tiered_rate_calculations trc\n    CROSS JOIN usage_scenario_modeling usm\n    GROUP BY trc.rate_structure_id, trc.utility_id, trc.rate_code_id, trc.state_id, usm.usage_kwh, usm.usage_scenario_name\n),\ntou_rate_cost_calculations AS (\n    -- Fifth CTE: Calculate costs for TOU rates across usage scenarios\n    SELECT\n        toua.rate_structure_id,\n        toua.utility_id,\n        toua.rate_code_id,\n        toua.state_id,\n        usm.usage_kwh,\n        usm.usage_scenario_name,\n        -- Distribute usage across TOU periods (simplified: 40% peak, 60% off-peak)\n        SUM(\n            CASE\n                WHEN toua.period_cost_category = 'High Cost' THEN\n                    usm.usage_kwh * 0.4 * toua.energy_charge_usd_per_kwh\n                WHEN toua.period_cost_category = 'Low Cost' THEN\n                    usm.usage_kwh * 0.6 * toua.energy_charge_usd_per_kwh\n                ELSE\n                    usm.usage_kwh * 0.1 * toua.energy_charge_usd_per_kwh\n            END\n        ) AS tou_energy_cost,\n        COUNT(DISTINCT toua.tou_period_id) AS tou_period_count,\n        AVG(\n            CASE\n                WHEN toua.period_cost_category = 'High Cost' THEN toua.energy_charge_usd_per_kwh\n                ELSE NULL\n            END\n        ) AS avg_peak_rate,\n        AVG(\n            CASE\n                WHEN toua.period_cost_category = 'Low Cost' THEN toua.energy_charge_usd_per_kwh\n                ELSE NULL\n            END\n        ) AS avg_offpeak_rate\n    FROM tou_period_analysis toua\n    CROSS JOIN usage_scenario_modeling usm\n    GROUP BY toua.rate_structure_id, toua.utility_id, toua.rate_code_id, toua.state_id, usm.usage_kwh, usm.usage_scenario_name\n),\nrate_optimization_comparison AS (\n    -- Sixth CTE: Compare tiered vs TOU rates for optimization\n    SELECT\n        COALESCE(trcc.rate_structure_id, torcc.rate_structure_id) AS rate_structure_id,\n        COALESCE(trcc.utility_id, torcc.utility_id) AS utility_id,\n        COALESCE(trcc.rate_code_id, torcc.rate_code_id) AS rate_code_id,\n        COALESCE(trcc.state_id, torcc.state_id) AS state_id,\n        COALESCE(trcc.usage_kwh, torcc.usage_kwh) AS usage_kwh,\n        COALESCE(trcc.usage_scenario_name, torcc.usage_scenario_name) AS usage_scenario_name,\n        trcc.tiered_energy_cost,\n        trcc.tiers_applied,\n        trcc.tier_count,\n        torcc.tou_energy_cost,\n        torcc.tou_period_count,\n        torcc.avg_peak_rate,\n        torcc.avg_offpeak_rate,\n        -- Cost comparison\n        CASE\n            WHEN trcc.tiered_energy_cost IS NOT NULL AND torcc.tou_energy_cost IS NOT NULL THEN\n                trcc.tiered_energy_cost - torcc.tou_energy_cost\n            ELSE NULL\n        END AS cost_difference_tiered_vs_tou,\n        CASE\n            WHEN trcc.tiered_energy_cost IS NOT NULL AND torcc.tou_energy_cost IS NOT NULL AND torcc.tou_energy_cost != 0 THEN\n                ((trcc.tiered_energy_cost - torcc.tou_energy_cost) / ABS(torcc.tou_energy_cost)) * 100\n            ELSE NULL\n        END AS cost_difference_percentage,\n        -- Optimal rate recommendation\n        CASE\n            WHEN trcc.tiered_energy_cost IS NOT NULL AND torcc.tou_energy_cost IS NOT NULL THEN\n                CASE\n                    WHEN trcc.tiered_energy_cost < torcc.tou_energy_cost THEN 'Tiered Rate'\n                    ELSE 'TOU Rate'\n                END\n            WHEN trcc.tiered_energy_cost IS NOT NULL THEN 'Tiered Rate'\n            WHEN torcc.tou_energy_cost IS NOT NULL THEN 'TOU Rate'\n            ELSE 'Standard Rate'\n        END AS optimal_rate_type\n    FROM tiered_rate_cost_calculations trcc\n    FULL OUTER JOIN tou_rate_cost_calculations torcc ON (\n        trcc.rate_structure_id = torcc.rate_structure_id\n        AND trcc.usage_kwh = torcc.usage_kwh\n    )\n)\nSELECT\n    roc.rate_structure_id,\n    roc.utility_id,\n    uc.utility_name,\n    roc.rate_code_id,\n    rc.rate_code,\n    rc.rate_code_category,\n    roc.state_id,\n    s.state_name,\n    roc.usage_kwh,\n    roc.usage_scenario_name,\n    ROUND(CAST(roc.tiered_energy_cost AS NUMERIC), 2) AS tiered_energy_cost,\n    roc.tiers_applied,\n    roc.tier_count,\n    ROUND(CAST(roc.tou_energy_cost AS NUMERIC), 2) AS tou_energy_cost,\n    roc.tou_period_count,\n    ROUND(CAST(roc.avg_peak_rate AS NUMERIC), 6) AS avg_peak_rate,\n    ROUND(CAST(roc.avg_offpeak_rate AS NUMERIC), 6) AS avg_offpeak_rate,\n    ROUND(CAST(roc.cost_difference_tiered_vs_tou AS NUMERIC), 2) AS cost_difference_tiered_vs_tou,\n    ROUND(CAST(roc.cost_difference_percentage AS NUMERIC), 2) AS cost_difference_percentage,\n    roc.optimal_rate_type\nFROM rate_optimization_comparison roc\nINNER JOIN utility_companies uc ON roc.utility_id = uc.utility_id\nINNER JOIN rate_codes rc ON roc.rate_code_id = rc.rate_code_id\nINNER JOIN states s ON roc.state_id = s.state_id\nORDER BY roc.state_id, roc.utility_id, roc.usage_kwh;",
  "evidence": "The query recursively processes rate tier structures, groups data by consumption levels and time periods, computes cost aggregates for each scenario and quartile distribution of outcomes, employs window functions to calculate rolling usage patterns and comparative cost metrics across rate plans, and handles edge cases including NULL values in join conditions and boundary date ranges.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "tiered_rate_tiers",
    "rate_structures",
    "electricity_rates",
    "tiered_rate_calculations",
    "time_of_use_periods",
    "usage_scenario_modeling",
    "tou_period_analysis",
    "tiered_rate_cost_calculations",
    "tou_rate_cost_calculations",
    "rate_optimization_comparison",
    "utility_companies",
    "rate_codes",
    "states"
  ],
  "schema_context": {},
  "expected_output": "Comprehensive tiered rate and TOU analysis with usage scenarios, cost calculations, and optimization recommendations.",
  "normal_query": "Comprehensive tiered rate and time-of-use analysis with usage scenarios, cost calculations, and optimization recommendations"
}
```


### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 3,
  "question": "Can you show me a comprehensive solar rebate aggregation and optimization analysis that includes multi-source incentive analysis?",
  "SQL": "WITH federal_incentive_analysis AS (\n    -- First CTE: Analyze federal incentives with eligibility matching\n    SELECT\n        fi.federal_incentive_id,\n        fi.incentive_name,\n        fi.incentive_type,\n        fi.incentive_amount_usd,\n        fi.incentive_percentage,\n        fi.incentive_unit,\n        fi.maximum_incentive_usd,\n        fi.minimum_system_size_kw,\n        fi.maximum_system_size_kw,\n        fi.effective_date,\n        fi.expiration_date,\n        fi.eligible_technologies,\n        fi.eligible_sectors,\n        -- Calculate incentive value for different system sizes\n        CASE\n            WHEN fi.incentive_unit = 'percentage' THEN\n                CASE\n                    WHEN fi.incentive_percentage IS NOT NULL THEN\n                        CASE\n                            WHEN fi.maximum_incentive_usd IS NOT NULL THEN\n                                LEAST(\n                                    (10000 * fi.incentive_percentage / 100),\n                                    fi.maximum_incentive_usd\n                                )\n                            ELSE (10000 * fi.incentive_percentage / 100)\n                        END\n                    ELSE fi.incentive_amount_usd\n                END\n            WHEN fi.incentive_unit = 'per_watt' THEN\n                CASE\n                    WHEN fi.incentive_amount_usd IS NOT NULL THEN\n                        (10000 * fi.incentive_amount_usd / 1000)\n                    ELSE NULL\n                END\n            WHEN fi.incentive_unit = 'fixed_amount' THEN fi.incentive_amount_usd\n            ELSE fi.incentive_amount_usd\n        END AS estimated_incentive_value_10kw,\n        CASE\n            WHEN fi.incentive_unit = 'percentage' THEN\n                CASE\n                    WHEN fi.incentive_percentage IS NOT NULL THEN\n                        CASE\n                            WHEN fi.maximum_incentive_usd IS NOT NULL THEN\n                                LEAST(\n                                    (5000 * fi.incentive_percentage / 100),\n                                    fi.maximum_incentive_usd\n                                )\n                            ELSE (5000 * fi.incentive_percentage / 100)\n                        END\n                    ELSE fi.incentive_amount_usd\n                END\n            WHEN fi.incentive_unit = 'per_watt' THEN\n                CASE\n                    WHEN fi.incentive_amount_usd IS NOT NULL THEN\n                        (5000 * fi.incentive_amount_usd / 1000)\n                    ELSE NULL\n                END\n            WHEN fi.incentive_unit = 'fixed_amount' THEN fi.incentive_amount_usd\n            ELSE fi.incentive_amount_usd\n        END AS estimated_incentive_value_5kw\n    FROM federal_incentives fi\n    WHERE fi.is_active = TRUE\n        AND (fi.expiration_date IS NULL OR fi.expiration_date > CURRENT_DATE)\n        AND 'Solar Photovoltaics' = ANY(fi.eligible_technologies)\n),\nstate_incentive_analysis AS (\n    -- Second CTE: Analyze state incentives with geographic matching\n    SELECT\n        si.state_incentive_id,\n        si.state_id,\n        s.state_name,\n        s.region,\n        si.incentive_name,\n        si.incentive_type,\n        si.incentive_amount_usd,\n        si.incentive_percentage,\n        si.incentive_unit,\n        si.maximum_incentive_usd,\n        si.minimum_system_size_kw,\n        si.maximum_system_size_kw,\n        si.effective_date,\n        si.expiration_date,\n        si.eligible_technologies,\n        si.eligible_sectors,\n        si.regulatory_authority,\n        -- Calculate incentive value for different system sizes\n        CASE\n            WHEN si.incentive_unit = 'percentage' THEN\n                CASE\n                    WHEN si.incentive_percentage IS NOT NULL THEN\n                        CASE\n                            WHEN si.maximum_incentive_usd IS NOT NULL THEN\n                                LEAST(\n                                    (10000 * si.incentive_percentage / 100),\n                                    si.maximum_incentive_usd\n                                )\n                            ELSE (10000 * si.incentive_percentage / 100)\n                        END\n                    ELSE si.incentive_amount_usd\n                END\n            WHEN si.incentive_unit = 'per_watt' THEN\n                CASE\n                    WHEN si.incentive_amount_usd IS NOT NULL THEN\n                        (10000 * si.incentive_amount_usd / 1000)\n                    ELSE NULL\n                END\n            WHEN si.incentive_unit = 'fixed_amount' THEN si.incentive_amount_usd\n            ELSE si.incentive_amount_usd\n        END AS estimated_incentive_value_10kw,\n        CASE\n            WHEN si.incentive_unit = 'percentage' THEN\n                CASE\n                    WHEN si.incentive_percentage IS NOT NULL THEN\n                        CASE\n                            WHEN si.maximum_incentive_usd IS NOT NULL THEN\n                                LEAST(\n                                    (5000 * si.incentive_percentage / 100),\n                                    si.maximum_incentive_usd\n                                )\n                            ELSE (5000 * si.incentive_percentage / 100)\n                        END\n                    ELSE si.incentive_amount_usd\n                END\n            WHEN si.incentive_unit = 'per_watt' THEN\n                CASE\n                    WHEN si.incentive_amount_usd IS NOT NULL THEN\n                        (5000 * si.incentive_amount_usd / 1000)\n                    ELSE NULL\n                END\n            WHEN si.incentive_unit = 'fixed_amount' THEN si.incentive_amount_usd\n            ELSE si.incentive_amount_usd\n        END AS estimated_incentive_value_5kw\n    FROM state_incentives si\n    INNER JOIN states s ON si.state_id = s.state_id\n    WHERE si.is_active = TRUE\n        AND (si.expiration_date IS NULL OR si.expiration_date > CURRENT_DATE)\n        AND 'Solar Photovoltaics' = ANY(si.eligible_technologies)\n),\nutility_incentive_analysis AS (\n    -- Third CTE: Analyze utility incentives with utility matching\n    SELECT\n        ui.utility_incentive_id,\n        ui.utility_id,\n        uc.utility_name,\n        ui.state_id,\n        s.state_name,\n        ui.incentive_name,\n        ui.incentive_type,\n        ui.incentive_amount_usd,\n        ui.incentive_percentage,\n        ui.incentive_unit,\n        ui.maximum_incentive_usd,\n        ui.minimum_system_size_kw,\n        ui.maximum_system_size_kw,\n        ui.net_metering_capacity_limit_kw,\n        ui.feed_in_tariff_rate_usd_per_kwh,\n        ui.effective_date,\n        ui.expiration_date,\n        ui.eligible_technologies,\n        ui.eligible_sectors,\n        -- Calculate incentive value for different system sizes\n        CASE\n            WHEN ui.incentive_unit = 'percentage' THEN\n                CASE\n                    WHEN ui.incentive_percentage IS NOT NULL THEN\n                        CASE\n                            WHEN ui.maximum_incentive_usd IS NOT NULL THEN\n                                LEAST(\n                                    (10000 * ui.incentive_percentage / 100),\n                                    ui.maximum_incentive_usd\n                                )\n                            ELSE (10000 * ui.incentive_percentage / 100)\n                        END\n                    ELSE ui.incentive_amount_usd\n                END\n            WHEN ui.incentive_unit = 'per_watt' THEN\n                CASE\n                    WHEN ui.incentive_amount_usd IS NOT NULL THEN\n                        (10000 * ui.incentive_amount_usd / 1000)\n                    ELSE NULL\n                END\n            WHEN ui.incentive_unit = 'fixed_amount' THEN ui.incentive_amount_usd\n            ELSE ui.incentive_amount_usd\n        END AS estimated_incentive_value_10kw,\n        CASE\n            WHEN ui.incentive_unit = 'percentage' THEN\n                CASE\n                    WHEN ui.incentive_percentage IS NOT NULL THEN\n                        CASE\n                            WHEN ui.maximum_incentive_usd IS NOT NULL THEN\n                                LEAST(\n                                    (5000 * ui.incentive_percentage / 100),\n                                    ui.maximum_incentive_usd\n                                )\n                            ELSE (5000 * ui.incentive_percentage / 100)\n                        END\n                    ELSE ui.incentive_amount_usd\n                END\n            WHEN ui.incentive_unit = 'per_watt' THEN\n                CASE\n                    WHEN ui.incentive_amount_usd IS NOT NULL THEN\n                        (5000 * ui.incentive_amount_usd / 1000)\n                    ELSE NULL\n                END\n            WHEN ui.incentive_unit = 'fixed_amount' THEN ui.incentive_amount_usd\n            ELSE ui.incentive_amount_usd\n        END AS estimated_incentive_value_5kw\n    FROM utility_incentives ui\n    INNER JOIN utility_companies uc ON ui.utility_id = uc.utility_id\n    INNER JOIN states s ON ui.state_id = s.state_id\n    WHERE ui.is_active = TRUE\n        AND (ui.expiration_date IS NULL OR ui.expiration_date > CURRENT_DATE)\n        AND 'Solar Photovoltaics' = ANY(ui.eligible_technologies)\n),\ngeographic_rebate_aggregation AS (\n    -- Fourth CTE: Aggregate rebates by geographic location\n    SELECT\n        COALESCE(sia.state_id, uia.state_id) AS state_id,\n        COALESCE(sia.state_name, uia.state_name) AS state_name,\n        COALESCE(sia.region, s.region) AS region,\n        uia.utility_id,\n        uia.utility_name,\n        zc.zip_code,\n        zc.city,\n        -- Federal incentive aggregation\n        COUNT(DISTINCT fia.federal_incentive_id) AS federal_incentive_count,\n        SUM(fia.estimated_incentive_value_10kw) AS total_federal_incentives_10kw,\n        SUM(fia.estimated_incentive_value_5kw) AS total_federal_incentives_5kw,\n        -- State incentive aggregation\n        COUNT(DISTINCT sia.state_incentive_id) AS state_incentive_count,\n        SUM(sia.estimated_incentive_value_10kw) AS total_state_incentives_10kw,\n        SUM(sia.estimated_incentive_value_5kw) AS total_state_incentives_5kw,\n        -- Utility incentive aggregation\n        COUNT(DISTINCT uia.utility_incentive_id) AS utility_incentive_count,\n        SUM(uia.estimated_incentive_value_10kw) AS total_utility_incentives_10kw,\n        SUM(uia.estimated_incentive_value_5kw) AS total_utility_incentives_5kw,\n        -- Combined totals\n        SUM(fia.estimated_incentive_value_10kw) + SUM(sia.estimated_incentive_value_10kw) + SUM(uia.estimated_incentive_value_10kw) AS total_combined_incentives_10kw,\n        SUM(fia.estimated_incentive_value_5kw) + SUM(sia.estimated_incentive_value_5kw) + SUM(uia.estimated_incentive_value_5kw) AS total_combined_incentives_5kw\n    FROM federal_incentive_analysis fia\n    CROSS JOIN state_incentive_analysis sia\n    LEFT JOIN utility_incentive_analysis uia ON sia.state_id = uia.state_id\n    LEFT JOIN zip_codes zc ON sia.state_id = zc.state_id\n    LEFT JOIN states s ON sia.state_id = s.state_id\n    GROUP BY\n        COALESCE(sia.state_id, uia.state_id),\n        COALESCE(sia.state_name, uia.state_name),\n        COALESCE(sia.region, s.region),\n        uia.utility_id,\n        uia.utility_name,\n        zc.zip_code,\n        zc.city\n),\nrebate_optimization_analysis AS (\n    -- Fifth CTE: Optimize rebate stacking and calculate ROI\n    SELECT\n        gra.state_id,\n        gra.state_name,\n        gra.region,\n        gra.utility_id,\n        gra.utility_name,\n        gra.zip_code,\n        gra.city,\n        gra.federal_incentive_count,\n        gra.state_incentive_count,\n        gra.utility_incentive_count,\n        gra.total_federal_incentives_10kw,\n        gra.total_state_incentives_10kw,\n        gra.total_utility_incentives_10kw,\n        gra.total_combined_incentives_10kw,\n        gra.total_federal_incentives_5kw,\n        gra.total_state_incentives_5kw,\n        gra.total_utility_incentives_5kw,\n        gra.total_combined_incentives_5kw,\n        -- System cost assumptions (simplified: $3/watt)\n        10000 * 3.0 AS system_cost_10kw,\n        5000 * 3.0 AS system_cost_5kw,\n        -- Net cost after rebates\n        (10000 * 3.0) - gra.total_combined_incentives_10kw AS net_cost_10kw,\n        (5000 * 3.0) - gra.total_combined_incentives_5kw AS net_cost_5kw,\n        -- Rebate percentage\n        CASE\n            WHEN (10000 * 3.0) > 0 THEN\n                (gra.total_combined_incentives_10kw / (10000 * 3.0)) * 100\n            ELSE 0\n        END AS rebate_percentage_10kw,\n        CASE\n            WHEN (5000 * 3.0) > 0 THEN\n                (gra.total_combined_incentives_5kw / (5000 * 3.0)) * 100\n            ELSE 0\n        END AS rebate_percentage_5kw,\n        -- Window functions for comparison\n        AVG(gra.total_combined_incentives_10kw) OVER (\n            PARTITION BY gra.state_id\n        ) AS state_avg_total_incentives_10kw,\n        AVG(gra.total_combined_incentives_10kw) OVER (\n            PARTITION BY gra.region\n        ) AS region_avg_total_incentives_10kw,\n        PERCENT_RANK() OVER (\n            PARTITION BY gra.state_id\n            ORDER BY gra.total_combined_incentives_10kw DESC\n        ) AS state_rebate_percentile,\n        ROW_NUMBER() OVER (\n            PARTITION BY gra.state_id\n            ORDER BY gra.total_combined_incentives_10kw DESC\n        ) AS state_rebate_rank\n    FROM geographic_rebate_aggregation gra\n),\nfinal_rebate_intelligence AS (\n    -- Sixth CTE: Final rebate intelligence with comprehensive metrics\n    SELECT\n        roa.state_id,\n        roa.state_name,\n        roa.region,\n        roa.utility_id,\n        roa.utility_name,\n        roa.zip_code,\n        roa.city,\n        roa.federal_incentive_count,\n        roa.state_incentive_count,\n        roa.utility_incentive_count,\n        roa.federal_incentive_count + roa.state_incentive_count + roa.utility_incentive_count AS total_incentive_count,\n        ROUND(CAST(roa.total_federal_incentives_10kw AS NUMERIC), 2) AS total_federal_incentives_10kw,\n        ROUND(CAST(roa.total_state_incentives_10kw AS NUMERIC), 2) AS total_state_incentives_10kw,\n        ROUND(CAST(roa.total_utility_incentives_10kw AS NUMERIC), 2) AS total_utility_incentives_10kw,\n        ROUND(CAST(roa.total_combined_incentives_10kw AS NUMERIC), 2) AS total_combined_incentives_10kw,\n        ROUND(CAST(roa.total_federal_incentives_5kw AS NUMERIC), 2) AS total_federal_incentives_5kw,\n        ROUND(CAST(roa.total_state_incentives_5kw AS NUMERIC), 2) AS total_state_incentives_5kw,\n        ROUND(CAST(roa.total_utility_incentives_5kw AS NUMERIC), 2) AS total_utility_incentives_5kw,\n        ROUND(CAST(roa.total_combined_incentives_5kw AS NUMERIC), 2) AS total_combined_incentives_5kw,\n        ROUND(CAST(roa.system_cost_10kw AS NUMERIC), 2) AS system_cost_10kw,\n        ROUND(CAST(roa.system_cost_5kw AS NUMERIC), 2) AS system_cost_5kw,\n        ROUND(CAST(roa.net_cost_10kw AS NUMERIC), 2) AS net_cost_10kw,\n        ROUND(CAST(roa.net_cost_5kw AS NUMERIC), 2) AS net_cost_5kw,\n        ROUND(CAST(roa.rebate_percentage_10kw AS NUMERIC), 2) AS rebate_percentage_10kw,\n        ROUND(CAST(roa.rebate_percentage_5kw AS NUMERIC), 2) AS rebate_percentage_5kw,\n        ROUND(CAST(roa.state_avg_total_incentives_10kw AS NUMERIC), 2) AS state_avg_total_incentives_10kw,\n        ROUND(CAST(roa.region_avg_total_incentives_10kw AS NUMERIC), 2) AS region_avg_total_incentives_10kw,\n        ROUND(CAST(roa.state_rebate_percentile * 100 AS NUMERIC), 2) AS state_rebate_percentile,\n        roa.state_rebate_rank,\n        -- Rebate competitiveness classification\n        CASE\n            WHEN roa.total_combined_incentives_10kw > roa.state_avg_total_incentives_10kw THEN 'Above Average'\n            WHEN roa.total_combined_incentives_10kw = roa.state_avg_total_incentives_10kw THEN 'Average'\n            ELSE 'Below Average'\n        END AS rebate_competitiveness\n    FROM rebate_optimization_analysis roa\n)\nSELECT\n    state_id,\n    state_name,\n    region,\n    utility_id,\n    utility_name,\n    zip_code,\n    city,\n    federal_incentive_count,\n    state_incentive_count,\n    utility_incentive_count,\n    total_incentive_count,\n    total_federal_incentives_10kw,\n    total_state_incentives_10kw,\n    total_utility_incentives_10kw,\n    total_combined_incentives_10kw,\n    total_federal_incentives_5kw,\n    total_state_incentives_5kw,\n    total_utility_incentives_5kw,\n    total_combined_incentives_5kw,\n    system_cost_10kw,\n    system_cost_5kw,\n    net_cost_10kw,\n    net_cost_5kw,\n    rebate_percentage_10kw,\n    rebate_percentage_5kw,\n    state_avg_total_incentives_10kw,\n    region_avg_total_incentives_10kw,\n    state_rebate_percentile,\n    state_rebate_rank,\n    rebate_competitiveness\nFROM final_rebate_intelligence\nORDER BY total_combined_incentives_10kw DESC, state_name, utility_name;",
  "evidence": "The query groups incentive data by source type and relevant customer dimensions, computes aggregate rebate amounts and quartile distributions to identify typical and exceptional savings opportunities, uses window functions to calculate rolling incentive trends and comparative savings metrics across regions and time periods, and implements NULL-safe joins.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "federal_incentives",
    "state_incentives",
    "states",
    "utility_incentives",
    "utility_companies",
    "federal_incentive_analysis",
    "state_incentive_analysis",
    "utility_incentive_analysis",
    "zip_codes",
    "geographic_rebate_aggregation",
    "rebate_optimization_analysis",
    "final_rebate_intelligence"
  ],
  "schema_context": {},
  "expected_output": "Comprehensive solar rebate aggregation with federal, state, and utility incentives, rebate stacking optimization, and total savings calculations.",
  "normal_query": "Comprehensive solar rebate aggregation with federal, state, and utility incentives, rebate stacking optimization, and total savings calculations"
}
```


### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 4,
  "question": "Can you show me historical rate trend analysis with time-series forecasting and volatility metrics?",
  "SQL": "WITH historical_rate_timeline AS (\n    -- First CTE: Build comprehensive historical rate timeline\n    SELECT\n        her.historical_rate_id,\n        her.rate_id,\n        her.utility_id,\n        her.rate_code_id,\n        her.state_id,\n        her.effective_date,\n        her.energy_charge_usd_per_kwh,\n        her.fixed_charge_usd,\n        her.demand_charge_usd_per_kw,\n        her.change_type,\n        her.change_percentage,\n        her.change_amount,\n        her.change_reason,\n        uc.utility_name,\n        rc.rate_code,\n        s.state_name,\n        s.region,\n        -- Calculate months since start\n        EXTRACT(EPOCH FROM (her.effective_date - MIN(her.effective_date) OVER (PARTITION BY her.utility_id, her.rate_code_id))) / 2592000 AS months_since_start\n    FROM historical_electricity_rates her\n    INNER JOIN utility_companies uc ON her.utility_id = uc.utility_id\n    INNER JOIN rate_codes rc ON her.rate_code_id = rc.rate_code_id\n    INNER JOIN states s ON her.state_id = s.state_id\n    WHERE her.effective_date >= CURRENT_DATE - INTERVAL '5 years'\n),\nrate_change_analysis AS (\n    -- Second CTE: Analyze rate changes with window functions\n    SELECT\n        hrt.*,\n        -- Previous rate values\n        LAG(hrt.energy_charge_usd_per_kwh, 1) OVER (\n            PARTITION BY hrt.utility_id, hrt.rate_code_id\n            ORDER BY hrt.effective_date\n        ) AS prev_energy_charge,\n        LEAD(hrt.energy_charge_usd_per_kwh, 1) OVER (\n            PARTITION BY hrt.utility_id, hrt.rate_code_id\n            ORDER BY hrt.effective_date\n        ) AS next_energy_charge,\n        -- Rate change calculations\n        hrt.energy_charge_usd_per_kwh - LAG(hrt.energy_charge_usd_per_kwh, 1) OVER (\n            PARTITION BY hrt.utility_id, hrt.rate_code_id\n            ORDER BY hrt.effective_date\n        ) AS energy_charge_change,\n        -- Moving averages\n        AVG(hrt.energy_charge_usd_per_kwh) OVER (\n            PARTITION BY hrt.utility_id, hrt.rate_code_id\n            ORDER BY hrt.effective_date\n            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n        ) AS moving_avg_12mo,\n        AVG(hrt.energy_charge_usd_per_kwh) OVER (\n            PARTITION BY hrt.utility_id, hrt.rate_code_id\n            ORDER BY hrt.effective_date\n            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW\n        ) AS moving_avg_24mo,\n        -- Moving standard deviation (volatility)\n        STDDEV(hrt.energy_charge_usd_per_kwh) OVER (\n            PARTITION BY hrt.utility_id, hrt.rate_code_id\n            ORDER BY hrt.effective_date\n            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n        ) AS moving_stddev_12mo,\n        -- Rate trend direction\n        CASE\n            WHEN hrt.energy_charge_usd_per_kwh > LAG(hrt.energy_charge_usd_per_kwh, 1) OVER (\n                PARTITION BY hrt.utility_id, hrt.rate_code_id\n                ORDER BY hrt.effective_date\n            ) THEN 'Increasing'\n            WHEN hrt.energy_charge_usd_per_kwh < LAG(hrt.energy_charge_usd_per_kwh, 1) OVER (\n                PARTITION BY hrt.utility_id, hrt.rate_code_id\n                ORDER BY hrt.effective_date\n            ) THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS trend_direction\n    FROM historical_rate_timeline hrt\n),\nvolatility_metrics AS (\n    -- Third CTE: Calculate volatility and risk metrics\n    SELECT\n        rca.*,\n        -- Coefficient of variation (volatility measure)\n        CASE\n            WHEN rca.moving_avg_12mo > 0 THEN\n                (rca.moving_stddev_12mo / rca.moving_avg_12mo) * 100\n            ELSE NULL\n        END AS coefficient_of_variation,\n        -- Rate range (max - min) over 12 months\n        MAX(rca.energy_charge_usd_per_kwh) OVER (\n            PARTITION BY rca.utility_id, rca.rate_code_id\n            ORDER BY rca.effective_date\n            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n        ) - MIN(rca.energy_charge_usd_per_kwh) OVER (\n            PARTITION BY rca.utility_id, rca.rate_code_id\n            ORDER BY rca.effective_date\n            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n        ) AS rate_range_12mo,\n        -- Percentile rankings\n        PERCENT_RANK() OVER (\n            PARTITION BY rca.state_id, rca.rate_code_id\n            ORDER BY rca.energy_charge_usd_per_kwh\n        ) AS state_rate_percentile,\n        -- Rate change frequency\n        COUNT(CASE WHEN rca.change_type IN ('rate_increase', 'rate_decrease') THEN 1 END) OVER (\n            PARTITION BY rca.utility_id, rca.rate_code_id\n            ORDER BY rca.effective_date\n            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n        ) AS rate_changes_12mo\n    FROM rate_change_analysis rca\n),\ntrend_identification AS (\n    -- Fourth CTE: Identify trends and patterns\n    SELECT\n        vm.*,\n        -- Trend strength (based on consistency)\n        COUNT(CASE WHEN vm.trend_direction = 'Increasing' THEN 1 END) OVER (\n            PARTITION BY vm.utility_id, vm.rate_code_id\n            ORDER BY vm.effective_date\n            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n        ) AS increasing_periods_12mo,\n        COUNT(CASE WHEN vm.trend_direction = 'Decreasing' THEN 1 END) OVER (\n            PARTITION BY vm.utility_id, vm.rate_code_id\n            ORDER BY vm.effective_date\n            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n        ) AS decreasing_periods_12mo,\n        -- Rate acceleration (change in rate of change)\n        vm.energy_charge_change - LAG(vm.energy_charge_change, 1) OVER (\n            PARTITION BY vm.utility_id, vm.rate_code_id\n            ORDER BY vm.effective_date\n        ) AS rate_acceleration,\n        -- Forecast indicators (simplified linear trend)\n        vm.energy_charge_usd_per_kwh + (\n            AVG(vm.energy_charge_change) OVER (\n                PARTITION BY vm.utility_id, vm.rate_code_id\n                ORDER BY vm.effective_date\n                ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n            ) * 6\n        ) AS forecast_6mo,\n        vm.energy_charge_usd_per_kwh + (\n            AVG(vm.energy_charge_change) OVER (\n                PARTITION BY vm.utility_id, vm.rate_code_id\n                ORDER BY vm.effective_date\n                ROWS BETWEEN 11 PRECEDING AND CURRENT ROW\n            ) * 12\n        ) AS forecast_12mo\n    FROM volatility_metrics vm\n),\nfinal_trend_analysis AS (\n    -- Fifth CTE: Final trend analysis with comprehensive metrics\n    SELECT\n        ti.*,\n        -- Trend classification\n        CASE\n            WHEN ti.increasing_periods_12mo >= 8 THEN 'Strong Increasing Trend'\n            WHEN ti.increasing_periods_12mo >= 6 THEN 'Moderate Increasing Trend'\n            WHEN ti.decreasing_periods_12mo >= 8 THEN 'Strong Decreasing Trend'\n            WHEN ti.decreasing_periods_12mo >= 6 THEN 'Moderate Decreasing Trend'\n            ELSE 'Volatile/Uncertain Trend'\n        END AS trend_classification,\n        -- Volatility classification\n        CASE\n            WHEN ti.coefficient_of_variation > 15 THEN 'High Volatility'\n            WHEN ti.coefficient_of_variation > 8 THEN 'Moderate Volatility'\n            WHEN ti.coefficient_of_variation > 3 THEN 'Low Volatility'\n            ELSE 'Very Low Volatility'\n        END AS volatility_classification,\n        -- Risk level\n        CASE\n            WHEN ti.coefficient_of_variation > 15 AND ti.rate_changes_12mo > 4 THEN 'High Risk'\n            WHEN ti.coefficient_of_variation > 8 OR ti.rate_changes_12mo > 2 THEN 'Moderate Risk'\n            ELSE 'Low Risk'\n        END AS risk_level\n    FROM trend_identification ti\n)\nSELECT\n    utility_id,\n    utility_name,\n    rate_code_id,\n    rate_code,\n    state_id,\n    state_name,\n    region,\n    effective_date,\n    energy_charge_usd_per_kwh,\n    fixed_charge_usd,\n    demand_charge_usd_per_kw,\n    change_type,\n    change_percentage,\n    change_amount,\n    ROUND(CAST(prev_energy_charge AS NUMERIC), 6) AS prev_energy_charge,\n    ROUND(CAST(next_energy_charge AS NUMERIC), 6) AS next_energy_charge,\n    ROUND(CAST(energy_charge_change AS NUMERIC), 6) AS energy_charge_change,\n    ROUND(CAST(moving_avg_12mo AS NUMERIC), 6) AS moving_avg_12mo,\n    ROUND(CAST(moving_avg_24mo AS NUMERIC), 6) AS moving_avg_24mo,\n    ROUND(CAST(moving_stddev_12mo AS NUMERIC), 6) AS moving_stddev_12mo,\n    trend_direction,\n    ROUND(CAST(coefficient_of_variation AS NUMERIC), 2) AS coefficient_of_variation,\n    ROUND(CAST(rate_range_12mo AS NUMERIC), 6) AS rate_range_12mo,\n    ROUND(CAST(state_rate_percentile * 100 AS NUMERIC), 2) AS state_rate_percentile,\n    rate_changes_12mo,\n    increasing_periods_12mo,\n    decreasing_periods_12mo,\n    ROUND(CAST(rate_acceleration AS NUMERIC), 6) AS rate_acceleration,\n    ROUND(CAST(forecast_6mo AS NUMERIC), 6) AS forecast_6mo,\n    ROUND(CAST(forecast_12mo AS NUMERIC), 6) AS forecast_12mo,\n    trend_classification,\n    volatility_classification,\n    risk_level\nFROM final_trend_analysis\nWHERE effective_date >= CURRENT_DATE - INTERVAL '2 years'\nORDER BY utility_id, rate_code_id, effective_date DESC;",
  "evidence": "The query groups historical rate data by relevant time dimensions and market segments, computes statistical aggregates including mean, standard deviation, and quartile distributions to measure central tendency and spread, applies window functions to calculate rolling averages, year-over-year comparisons, and moving volatility metrics across time periods, and handles edge cases such as NULL values in historical records.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "historical_electricity_rates",
    "utility_companies",
    "rate_codes",
    "states",
    "historical_rate_timeline",
    "rate_change_analysis",
    "volatility_metrics",
    "trend_identification",
    "final_trend_analysis"
  ],
  "schema_context": {},
  "expected_output": "Historical rate trend analysis with time-series metrics, volatility calculations, and trend identification.",
  "normal_query": "Historical rate trend analysis with time-series metrics, volatility calculations, and trend identification"
}
```


### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 5,
  "question": "Can you show me a geographic rate comparison matrix with cross-state benchmarking and market analysis?",
  "SQL": "WITH state_rate_benchmarks AS (\n    -- First CTE: Calculate state-level rate benchmarks\n    SELECT\n        s.state_id,\n        s.state_name,\n        s.region,\n        s.division,\n        COUNT(DISTINCT er.utility_id) AS utility_count,\n        COUNT(DISTINCT er.rate_id) AS total_rate_count,\n        AVG(er.energy_charge_usd_per_kwh) AS state_avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS state_median_rate,\n        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS state_q1_rate,\n        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS state_q3_rate,\n        MIN(er.energy_charge_usd_per_kwh) AS state_min_rate,\n        MAX(er.energy_charge_usd_per_kwh) AS state_max_rate,\n        STDDEV(er.energy_charge_usd_per_kwh) AS state_stddev_rate,\n        -- Rate type breakdowns\n        AVG(CASE WHEN er.rate_type = 'Residential' THEN er.energy_charge_usd_per_kwh END) AS state_avg_residential_rate,\n        AVG(CASE WHEN er.rate_type = 'Commercial' THEN er.energy_charge_usd_per_kwh END) AS state_avg_commercial_rate,\n        AVG(CASE WHEN er.rate_type = 'Industrial' THEN er.energy_charge_usd_per_kwh END) AS state_avg_industrial_rate\n    FROM states s\n    INNER JOIN electricity_rates er ON s.state_id = er.state_id\n    WHERE er.is_current = TRUE\n    GROUP BY s.state_id, s.state_name, s.region, s.division\n),\nregion_rate_benchmarks AS (\n    -- Second CTE: Calculate region-level rate benchmarks\n    SELECT\n        srb.region,\n        COUNT(DISTINCT srb.state_id) AS state_count,\n        AVG(srb.state_avg_rate) AS region_avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY srb.state_avg_rate) AS region_median_rate,\n        MIN(srb.state_avg_rate) AS region_min_rate,\n        MAX(srb.state_avg_rate) AS region_max_rate,\n        STDDEV(srb.state_avg_rate) AS region_stddev_rate\n    FROM state_rate_benchmarks srb\n    GROUP BY srb.region\n),\nutility_rate_positioning AS (\n    -- Third CTE: Analyze utility rate positioning within states\n    SELECT\n        er.utility_id,\n        uc.utility_name,\n        uc.utility_type,\n        er.state_id,\n        er.rate_code_id,\n        rc.rate_code,\n        er.rate_type,\n        er.energy_charge_usd_per_kwh,\n        er.fixed_charge_usd,\n        er.demand_charge_usd_per_kw,\n        srb.state_avg_rate,\n        srb.state_median_rate,\n        srb.state_min_rate,\n        srb.state_max_rate,\n        -- Utility positioning metrics\n        er.energy_charge_usd_per_kwh - srb.state_avg_rate AS rate_difference_from_state_avg,\n        CASE\n            WHEN srb.state_avg_rate > 0 THEN\n                ((er.energy_charge_usd_per_kwh - srb.state_avg_rate) / srb.state_avg_rate) * 100\n            ELSE NULL\n        END AS rate_difference_percentage,\n        -- Competitive positioning\n        CASE\n            WHEN er.energy_charge_usd_per_kwh < srb.state_q1_rate THEN 'Lowest Quartile'\n            WHEN er.energy_charge_usd_per_kwh < srb.state_median_rate THEN 'Second Quartile'\n            WHEN er.energy_charge_usd_per_kwh < srb.state_q3_rate THEN 'Third Quartile'\n            ELSE 'Highest Quartile'\n        END AS competitive_position,\n        -- Percentile ranking\n        PERCENT_RANK() OVER (\n            PARTITION BY er.state_id, er.rate_type\n            ORDER BY er.energy_charge_usd_per_kwh\n        ) AS state_rate_percentile\n    FROM electricity_rates er\n    INNER JOIN utility_companies uc ON er.utility_id = uc.utility_id\n    INNER JOIN rate_codes rc ON er.rate_code_id = rc.rate_code_id\n    INNER JOIN state_rate_benchmarks srb ON er.state_id = srb.state_id\n    WHERE er.is_current = TRUE\n),\ncross_state_comparison AS (\n    -- Fourth CTE: Cross-state rate comparisons\n    SELECT\n        urp1.state_id AS state_1_id,\n        urp1.state_avg_rate AS state_1_avg_rate,\n        urp2.state_id AS state_2_id,\n        urp2.state_avg_rate AS state_2_avg_rate,\n        urp1.region AS region_1,\n        urp2.region AS region_2,\n        urp1.state_avg_rate - urp2.state_avg_rate AS rate_difference,\n        CASE\n            WHEN urp2.state_avg_rate > 0 THEN\n                ((urp1.state_avg_rate - urp2.state_avg_rate) / urp2.state_avg_rate) * 100\n            ELSE NULL\n        END AS rate_difference_percentage,\n        CASE\n            WHEN urp1.state_avg_rate < urp2.state_avg_rate THEN 'Lower'\n            WHEN urp1.state_avg_rate > urp2.state_avg_rate THEN 'Higher'\n            ELSE 'Equal'\n        END AS comparison_result\n    FROM state_rate_benchmarks urp1\n    CROSS JOIN state_rate_benchmarks urp2\n    WHERE urp1.state_id < urp2.state_id\n),\nmarket_intelligence AS (\n    -- Fifth CTE: Market intelligence metrics\n    SELECT\n        urp.*,\n        rrb.region_avg_rate,\n        rrb.region_median_rate,\n        rrb.region_min_rate,\n        rrb.region_max_rate,\n        -- Regional positioning\n        urp.energy_charge_usd_per_kwh - rrb.region_avg_rate AS rate_difference_from_region_avg,\n        CASE\n            WHEN rrb.region_avg_rate > 0 THEN\n                ((urp.energy_charge_usd_per_kwh - rrb.region_avg_rate) / rrb.region_avg_rate) * 100\n            ELSE NULL\n        END AS rate_difference_from_region_percentage,\n        -- National positioning (simplified: using region as proxy)\n        AVG(urp.state_avg_rate) OVER () AS national_avg_rate,\n        urp.energy_charge_usd_per_kwh - AVG(urp.state_avg_rate) OVER () AS rate_difference_from_national_avg,\n        -- Market share indicators\n        COUNT(*) OVER (\n            PARTITION BY urp.state_id, urp.rate_type\n        ) AS total_rates_in_state_type,\n        COUNT(*) OVER (\n            PARTITION BY urp.state_id, urp.rate_type\n            ORDER BY urp.energy_charge_usd_per_kwh\n            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW\n        ) AS rates_lower_in_state_type\n    FROM utility_rate_positioning urp\n    INNER JOIN region_rate_benchmarks rrb ON urp.state_id IN (\n        SELECT state_id FROM state_rate_benchmarks WHERE region = rrb.region\n    )\n),\nfinal_comparison_matrix AS (\n    -- Sixth CTE: Final comparison matrix with comprehensive metrics\n    SELECT\n        mi.utility_id,\n        mi.utility_name,\n        mi.utility_type,\n        mi.state_id,\n        s.state_name,\n        mi.region,\n        mi.rate_code_id,\n        mi.rate_code,\n        mi.rate_type,\n        mi.energy_charge_usd_per_kwh,\n        mi.fixed_charge_usd,\n        mi.demand_charge_usd_per_kw,\n        ROUND(CAST(mi.state_avg_rate AS NUMERIC), 6) AS state_avg_rate,\n        ROUND(CAST(mi.state_median_rate AS NUMERIC), 6) AS state_median_rate,\n        ROUND(CAST(mi.state_min_rate AS NUMERIC), 6) AS state_min_rate,\n        ROUND(CAST(mi.state_max_rate AS NUMERIC), 6) AS state_max_rate,\n        ROUND(CAST(mi.rate_difference_from_state_avg AS NUMERIC), 6) AS rate_difference_from_state_avg,\n        ROUND(CAST(mi.rate_difference_percentage AS NUMERIC), 2) AS rate_difference_percentage,\n        mi.competitive_position,\n        ROUND(CAST(mi.state_rate_percentile * 100 AS NUMERIC), 2) AS state_rate_percentile,\n        ROUND(CAST(mi.region_avg_rate AS NUMERIC), 6) AS region_avg_rate,\n        ROUND(CAST(mi.rate_difference_from_region_avg AS NUMERIC), 6) AS rate_difference_from_region_avg,\n        ROUND(CAST(mi.rate_difference_from_region_percentage AS NUMERIC), 2) AS rate_difference_from_region_percentage,\n        ROUND(CAST(mi.national_avg_rate AS NUMERIC), 6) AS national_avg_rate,\n        ROUND(CAST(mi.rate_difference_from_national_avg AS NUMERIC), 6) AS rate_difference_from_national_avg,\n        mi.total_rates_in_state_type,\n        mi.rates_lower_in_state_type,\n        CASE\n            WHEN mi.total_rates_in_state_type > 0 THEN\n                (mi.rates_lower_in_state_type::NUMERIC / mi.total_rates_in_state_type) * 100\n            ELSE NULL\n        END AS market_position_percentage\n    FROM market_intelligence mi\n    INNER JOIN states s ON mi.state_id = s.state_id\n)\nSELECT\n    utility_id,\n    utility_name,\n    utility_type,\n    state_id,\n    state_name,\n    region,\n    rate_code_id,\n    rate_code,\n    rate_type,\n    energy_charge_usd_per_kwh,\n    fixed_charge_usd,\n    demand_charge_usd_per_kw,\n    state_avg_rate,\n    state_median_rate,\n    state_min_rate,\n    state_max_rate,\n    rate_difference_from_state_avg,\n    rate_difference_percentage,\n    competitive_position,\n    state_rate_percentile,\n    region_avg_rate,\n    rate_difference_from_region_avg,\n    rate_difference_from_region_percentage,\n    national_avg_rate,\n    rate_difference_from_national_avg,\n    total_rates_in_state_type,\n    rates_lower_in_state_type,\n    ROUND(CAST(market_position_percentage AS NUMERIC), 2) AS market_position_percentage\nFROM final_comparison_matrix\nORDER BY state_name, rate_type, energy_charge_usd_per_kwh;",
  "evidence": "The query groups rate data by geographic dimensions including state, utility territory, and market segment, computes comparison aggregates and quartile benchmarks to position each market relative to peers, utilizes window functions to calculate cross-market rankings, regional averages, and comparative growth metrics over time, and implements robust NULL handling in geographic joins.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "states",
    "electricity_rates",
    "state_rate_benchmarks",
    "utility_companies",
    "rate_codes",
    "utility_rate_positioning",
    "region_rate_benchmarks",
    "market_intelligence",
    "final_comparison_matrix"
  ],
  "schema_context": {},
  "expected_output": "Geographic rate comparison matrix with cross-state benchmarking, competitive positioning, and market intelligence metrics.",
  "normal_query": "Geographic rate comparison matrix with cross-state benchmarking, competitive positioning, and market intelligence metrics"
}
```


### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 6,
  "question": "Can you show me how our utility's performance compares to competitors, including rate competitiveness analysis?",
  "SQL": "WITH utility_rate_performance AS (\n    -- First CTE: Calculate utility rate performance metrics\n    SELECT\n        uc.utility_id,\n        uc.utility_name,\n        uc.utility_type,\n        uc.state_id,\n        s.state_name,\n        s.region,\n        COUNT(DISTINCT er.rate_id) AS total_rates,\n        COUNT(DISTINCT er.rate_code_id) AS rate_codes_offered,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_energy_charge,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS median_energy_charge,\n        MIN(er.energy_charge_usd_per_kwh) AS min_energy_charge,\n        MAX(er.energy_charge_usd_per_kwh) AS max_energy_charge,\n        STDDEV(er.energy_charge_usd_per_kwh) AS stddev_energy_charge,\n        AVG(er.fixed_charge_usd) AS avg_fixed_charge,\n        AVG(er.demand_charge_usd_per_kw) AS avg_demand_charge,\n        COUNT(DISTINCT CASE WHEN er.rate_type = 'Residential' THEN er.rate_id END) AS residential_rate_count,\n        COUNT(DISTINCT CASE WHEN er.rate_type = 'Commercial' THEN er.rate_id END) AS commercial_rate_count,\n        COUNT(DISTINCT CASE WHEN er.rate_type = 'Industrial' THEN er.rate_id END) AS industrial_rate_count,\n        COUNT(DISTINCT rc.rate_structure_type) AS rate_structure_types,\n        uc.total_customers,\n        uc.total_mwh_sold\n    FROM utility_companies uc\n    INNER JOIN electricity_rates er ON uc.utility_id = er.utility_id\n    INNER JOIN rate_codes rc ON er.rate_code_id = rc.rate_code_id\n    INNER JOIN states s ON uc.state_id = s.state_id\n    WHERE er.is_current = TRUE AND uc.is_active = TRUE\n    GROUP BY uc.utility_id, uc.utility_name, uc.utility_type, uc.state_id, s.state_name, s.region, uc.total_customers, uc.total_mwh_sold\n),\nstate_benchmark_metrics AS (\n    -- Second CTE: Calculate state-level benchmarks\n    SELECT\n        s.state_id,\n        s.state_name,\n        s.region,\n        AVG(urp.avg_energy_charge) AS state_avg_energy_charge,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY urp.avg_energy_charge) AS state_median_energy_charge,\n        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY urp.avg_energy_charge) AS state_q1_energy_charge,\n        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY urp.avg_energy_charge) AS state_q3_energy_charge,\n        MIN(urp.avg_energy_charge) AS state_min_energy_charge,\n        MAX(urp.avg_energy_charge) AS state_max_energy_charge,\n        AVG(urp.avg_fixed_charge) AS state_avg_fixed_charge,\n        COUNT(DISTINCT urp.utility_id) AS state_utility_count\n    FROM utility_rate_performance urp\n    INNER JOIN states s ON urp.state_id = s.state_id\n    GROUP BY s.state_id, s.state_name, s.region\n),\npeer_utility_analysis AS (\n    -- Third CTE: Identify peer utilities\n    SELECT\n        urp1.utility_id,\n        urp1.utility_name,\n        urp1.utility_type,\n        urp1.state_id,\n        urp1.state_name,\n        urp1.region,\n        urp1.avg_energy_charge AS utility_avg_energy_charge,\n        urp1.total_rates,\n        urp1.rate_codes_offered,\n        COUNT(DISTINCT urp2.utility_id) AS peer_utility_count,\n        AVG(urp2.avg_energy_charge) AS peer_avg_energy_charge,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY urp2.avg_energy_charge) AS peer_median_energy_charge\n    FROM utility_rate_performance urp1\n    LEFT JOIN utility_rate_performance urp2 ON (\n        urp1.state_id = urp2.state_id\n        AND urp1.utility_id != urp2.utility_id\n        AND ABS(urp1.total_customers - urp2.total_customers) / NULLIF(urp1.total_customers, 0) < 0.5\n    )\n    GROUP BY urp1.utility_id, urp1.utility_name, urp1.utility_type, urp1.state_id, urp1.state_name, urp1.region,\n             urp1.avg_energy_charge, urp1.total_rates, urp1.rate_codes_offered\n),\ncompetitive_positioning AS (\n    -- Fourth CTE: Calculate competitive positioning\n    SELECT\n        pua.*,\n        sbm.state_avg_energy_charge,\n        sbm.state_median_energy_charge,\n        pua.utility_avg_energy_charge - sbm.state_avg_energy_charge AS difference_from_state_avg,\n        CASE WHEN sbm.state_avg_energy_charge > 0 THEN\n            ((pua.utility_avg_energy_charge - sbm.state_avg_energy_charge) / sbm.state_avg_energy_charge) * 100\n        ELSE NULL END AS difference_from_state_avg_percentage,\n        CASE\n            WHEN pua.utility_avg_energy_charge <= sbm.state_q1_energy_charge THEN 'Lowest Quartile'\n            WHEN pua.utility_avg_energy_charge <= sbm.state_median_energy_charge THEN 'Second Quartile'\n            WHEN pua.utility_avg_energy_charge <= sbm.state_q3_energy_charge THEN 'Third Quartile'\n            ELSE 'Highest Quartile'\n        END AS competitive_quartile,\n        PERCENT_RANK() OVER (PARTITION BY pua.state_id ORDER BY pua.utility_avg_energy_charge) AS state_percentile_rank\n    FROM peer_utility_analysis pua\n    INNER JOIN state_benchmark_metrics sbm ON pua.state_id = sbm.state_id\n),\nfinal_benchmarking_report AS (\n    -- Fifth CTE: Final benchmarking report\n    SELECT\n        cp.*,\n        urp.residential_rate_count,\n        urp.commercial_rate_count,\n        urp.industrial_rate_count,\n        urp.rate_structure_types,\n        urp.total_customers,\n        CASE\n            WHEN cp.difference_from_state_avg_percentage < -10 THEN 'Highly Competitive'\n            WHEN cp.difference_from_state_avg_percentage < -5 THEN 'Competitive'\n            WHEN cp.difference_from_state_avg_percentage < 5 THEN 'Average'\n            WHEN cp.difference_from_state_avg_percentage < 10 THEN 'Above Average'\n            ELSE 'Premium Pricing'\n        END AS performance_classification\n    FROM competitive_positioning cp\n    INNER JOIN utility_rate_performance urp ON cp.utility_id = urp.utility_id\n)\nSELECT\n    utility_id, utility_name, utility_type, state_id, state_name, region,\n    utility_avg_energy_charge, total_rates, rate_codes_offered,\n    ROUND(CAST(state_avg_energy_charge AS NUMERIC), 6) AS state_avg_energy_charge,\n    ROUND(CAST(difference_from_state_avg AS NUMERIC), 6) AS difference_from_state_avg,\n    ROUND(CAST(difference_from_state_avg_percentage AS NUMERIC), 2) AS difference_from_state_avg_percentage,\n    competitive_quartile,\n    ROUND(CAST(state_percentile_rank * 100 AS NUMERIC), 2) AS state_percentile_rank,\n    performance_classification\nFROM final_benchmarking_report\nORDER BY state_name, utility_avg_energy_charge;",
  "evidence": "The query joins rebate, installation, and consumption tables to create a unified dataset. It groups data by utility and relevant time periods to compute aggregate performance metrics such as average rates, rebate participation, and customer adoption. Window functions calculate percentile rankings and quartiles to position each utility against peers. Rolling averages identify trends over time.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "utility_companies",
    "electricity_rates",
    "rate_codes",
    "states",
    "utility_rate_performance",
    "peer_utility_analysis",
    "state_benchmark_metrics",
    "competitive_positioning",
    "final_benchmarking_report"
  ],
  "schema_context": {},
  "expected_output": "Utility performance benchmarking report with rate competitiveness metrics, market positioning, and peer comparisons.",
  "normal_query": "Generate a utility performance benchmarking report that includes rate competitiveness metrics, market positioning relative to peers, and comparative performance indicators."
}
```


### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 7,
  "question": "Can you analyze the market share of different rate codes and show their distribution across utilities?",
  "SQL": "WITH rate_code_adoption AS (\n    -- First CTE: Calculate rate code adoption by utility\n    SELECT\n        rc.rate_code_id,\n        rc.rate_code,\n        rc.rate_code_category,\n        rc.sector,\n        rc.rate_structure_type,\n        er.utility_id,\n        uc.utility_name,\n        er.state_id,\n        s.state_name,\n        s.region,\n        COUNT(DISTINCT er.rate_id) AS rate_count,\n        er.energy_charge_usd_per_kwh,\n        er.effective_date\n    FROM rate_codes rc\n    INNER JOIN electricity_rates er ON rc.rate_code_id = er.rate_code_id\n    INNER JOIN utility_companies uc ON er.utility_id = uc.utility_id\n    INNER JOIN states s ON er.state_id = s.state_id\n    WHERE er.is_current = TRUE AND rc.is_active = TRUE\n),\nutility_rate_code_distribution AS (\n    -- Second CTE: Analyze utility rate code distribution\n    SELECT\n        utility_id,\n        utility_name,\n        state_id,\n        state_name,\n        region,\n        COUNT(DISTINCT rate_code_id) AS rate_codes_adopted,\n        COUNT(DISTINCT rate_code_category) AS rate_categories_covered,\n        COUNT(DISTINCT sector) AS sectors_covered,\n        COUNT(DISTINCT rate_structure_type) AS structure_types_offered,\n        COUNT(DISTINCT rate_id) AS total_rates\n    FROM rate_code_adoption\n    GROUP BY utility_id, utility_name, state_id, state_name, region\n),\nstate_rate_code_penetration AS (\n    -- Third CTE: Calculate state-level rate code penetration\n    SELECT\n        state_id,\n        state_name,\n        region,\n        rate_code_id,\n        rate_code,\n        rate_code_category,\n        sector,\n        COUNT(DISTINCT utility_id) AS utilities_offering_code,\n        COUNT(DISTINCT rate_id) AS total_rates_with_code,\n        AVG(energy_charge_usd_per_kwh) AS avg_rate_for_code,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY energy_charge_usd_per_kwh) AS median_rate_for_code\n    FROM rate_code_adoption\n    GROUP BY state_id, state_name, region, rate_code_id, rate_code, rate_code_category, sector\n),\nmarket_share_calculations AS (\n    -- Fourth CTE: Calculate market share metrics\n    SELECT\n        srcp.*,\n        (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = srcp.state_id AND is_active = TRUE) AS total_utilities_in_state,\n        CASE\n            WHEN (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = srcp.state_id AND is_active = TRUE) > 0 THEN\n                (srcp.utilities_offering_code::NUMERIC / (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = srcp.state_id AND is_active = TRUE)) * 100\n            ELSE 0\n        END AS market_penetration_percentage,\n        -- Window functions for market share ranking\n        ROW_NUMBER() OVER (\n            PARTITION BY srcp.state_id\n            ORDER BY srcp.utilities_offering_code DESC\n        ) AS market_share_rank_state,\n        PERCENT_RANK() OVER (\n            PARTITION BY srcp.state_id\n            ORDER BY srcp.utilities_offering_code DESC\n        ) AS market_share_percentile_state\n    FROM state_rate_code_penetration srcp\n),\nregional_market_dynamics AS (\n    -- Fifth CTE: Analyze regional market dynamics\n    SELECT\n        msc.*,\n        AVG(msc.utilities_offering_code) OVER (PARTITION BY msc.region) AS region_avg_utilities_per_code,\n        AVG(msc.market_penetration_percentage) OVER (PARTITION BY msc.region) AS region_avg_penetration,\n        COUNT(DISTINCT msc.rate_code_id) OVER (PARTITION BY msc.region) AS region_total_rate_codes,\n        COUNT(DISTINCT msc.state_id) OVER (PARTITION BY msc.region) AS region_state_count\n    FROM market_share_calculations msc\n),\nfinal_market_share_analysis AS (\n    -- Sixth CTE: Final market share analysis\n    SELECT\n        rmd.*,\n        CASE\n            WHEN rmd.market_penetration_percentage >= 75 THEN 'Dominant'\n            WHEN rmd.market_penetration_percentage >= 50 THEN 'Major'\n            WHEN rmd.market_penetration_percentage >= 25 THEN 'Moderate'\n            ELSE 'Minor'\n        END AS market_share_classification,\n        CASE\n            WHEN rmd.market_penetration_percentage > rmd.region_avg_penetration THEN 'Above Regional Average'\n            WHEN rmd.market_penetration_percentage = rmd.region_avg_penetration THEN 'At Regional Average'\n            ELSE 'Below Regional Average'\n        END AS regional_positioning\n    FROM regional_market_dynamics rmd\n)\nSELECT\n    state_id, state_name, region,\n    rate_code_id, rate_code, rate_code_category, sector,\n    utilities_offering_code,\n    total_utilities_in_state,\n    ROUND(CAST(market_penetration_percentage AS NUMERIC), 2) AS market_penetration_percentage,\n    total_rates_with_code,\n    ROUND(CAST(avg_rate_for_code AS NUMERIC), 6) AS avg_rate_for_code,\n    ROUND(CAST(median_rate_for_code AS NUMERIC), 6) AS median_rate_for_code,\n    market_share_rank_state,\n    ROUND(CAST(market_share_percentile_state * 100 AS NUMERIC), 2) AS market_share_percentile_state,\n    ROUND(CAST(region_avg_penetration AS NUMERIC), 2) AS region_avg_penetration,\n    market_share_classification,\n    regional_positioning\nFROM final_market_share_analysis\nORDER BY state_name, market_penetration_percentage DESC;",
  "evidence": "The query aggregates customer and consumption data grouped by rate code and utility to calculate market share percentages. It computes adoption rates by dividing customers on each rate code by total customers within each utility and across the market. Window functions rank rate codes by popularity and calculate cumulative market share. Handles NULL or inactive rate codes.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "rate_codes",
    "electricity_rates",
    "utility_companies",
    "states",
    "rate_code_adoption",
    "state_rate_code_penetration",
    "market_share_calculations",
    "regional_market_dynamics",
    "final_market_share_analysis"
  ],
  "schema_context": {},
  "expected_output": "Rate code market share analysis with adoption rates, utility distribution, and market penetration metrics.",
  "normal_query": "Produce a rate code market share analysis showing adoption rates across different customer segments, utility-level distribution patterns, and overall market penetration metrics."
}
```


### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 8,
  "question": "Can you calculate the ROI and payback periods for solar rebate programs?",
  "SQL": "WITH solar_system_scenarios AS (\n    -- First CTE: Define solar system scenarios for analysis\n    SELECT system_size_kw, system_cost_per_watt, system_name\n    FROM (VALUES\n        (5.0, 3.0, 'Small Residential'),\n        (10.0, 3.0, 'Medium Residential'),\n        (20.0, 2.8, 'Large Residential'),\n        (50.0, 2.5, 'Small Commercial'),\n        (100.0, 2.3, 'Medium Commercial'),\n        (500.0, 2.0, 'Large Commercial')\n    ) AS scenarios(system_size_kw, system_cost_per_watt, system_name)\n),\nrebate_aggregation_by_location AS (\n    -- Second CTE: Aggregate all rebates by location\n    SELECT\n        sra.state_id,\n        s.state_name,\n        s.region,\n        sra.utility_id,\n        uc.utility_name,\n        sra.zip_code,\n        zc.city,\n        sra.total_federal_incentives_usd,\n        sra.total_state_incentives_usd,\n        sra.total_utility_incentives_usd,\n        sra.total_combined_incentives_usd,\n        sra.federal_incentive_count,\n        sra.state_incentive_count,\n        sra.utility_incentive_count,\n        sra.total_incentive_count\n    FROM solar_rebate_aggregations sra\n    INNER JOIN states s ON sra.state_id = s.state_id\n    LEFT JOIN utility_companies uc ON sra.utility_id = uc.utility_id\n    LEFT JOIN zip_codes zc ON sra.zip_code = zc.zip_code\n    WHERE sra.calculation_date >= CURRENT_DATE - INTERVAL '90 days'\n),\nelectricity_rate_for_location AS (\n    -- Third CTE: Get electricity rates for ROI calculations\n    SELECT\n        er.state_id,\n        er.utility_id,\n        er.energy_charge_usd_per_kwh,\n        er.fixed_charge_usd,\n        AVG(er.energy_charge_usd_per_kwh) OVER (PARTITION BY er.state_id) AS state_avg_rate\n    FROM electricity_rates er\n    WHERE er.is_current = TRUE AND er.rate_type = 'Residential'\n),\nroi_calculations AS (\n    -- Fourth CTE: Calculate ROI metrics for each scenario\n    SELECT\n        ral.state_id,\n        ral.state_name,\n        ral.region,\n        ral.utility_id,\n        ral.utility_name,\n        ral.zip_code,\n        ral.city,\n        sss.system_size_kw,\n        sss.system_name,\n        sss.system_cost_per_watt,\n        sss.system_size_kw * sss.system_cost_per_watt * 1000 AS total_system_cost,\n        ral.total_combined_incentives_usd AS total_rebates,\n        (sss.system_size_kw * sss.system_cost_per_watt * 1000) - ral.total_combined_incentives_usd AS net_system_cost,\n        erl.energy_charge_usd_per_kwh,\n        erl.state_avg_rate,\n        -- Annual electricity production (simplified: 1500 kWh per kW)\n        sss.system_size_kw * 1500 AS annual_kwh_production,\n        -- Annual savings\n        sss.system_size_kw * 1500 * erl.energy_charge_usd_per_kwh AS annual_savings,\n        -- Payback period (years)\n        CASE\n            WHEN (sss.system_size_kw * 1500 * erl.energy_charge_usd_per_kwh) > 0 THEN\n                ((sss.system_size_kw * sss.system_cost_per_watt * 1000) - ral.total_combined_incentives_usd) / (sss.system_size_kw * 1500 * erl.energy_charge_usd_per_kwh)\n            ELSE NULL\n        END AS payback_period_years,\n        -- Rebate percentage\n        CASE\n            WHEN (sss.system_size_kw * sss.system_cost_per_watt * 1000) > 0 THEN\n                (ral.total_combined_incentives_usd / (sss.system_size_kw * sss.system_cost_per_watt * 1000)) * 100\n            ELSE 0\n        END AS rebate_percentage\n    FROM rebate_aggregation_by_location ral\n    CROSS JOIN solar_system_scenarios sss\n    LEFT JOIN electricity_rate_for_location erl ON ral.state_id = erl.state_id AND ral.utility_id = erl.utility_id\n),\nnpv_analysis AS (\n    -- Fifth CTE: Calculate NPV for 25-year system life\n    SELECT\n        rc.*,\n        -- 25-year NPV calculation (simplified, assuming 3% discount rate)\n        rc.net_system_cost + SUM(\n            rc.annual_savings / POWER(1.03, year_num)\n        ) OVER (\n            PARTITION BY rc.state_id, rc.utility_id, rc.system_size_kw\n            ORDER BY year_num\n            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING\n        ) AS npv_25yr,\n        -- 10-year NPV\n        rc.net_system_cost + SUM(\n            CASE WHEN year_num <= 10 THEN rc.annual_savings / POWER(1.03, year_num) ELSE 0 END\n        ) OVER (\n            PARTITION BY rc.state_id, rc.utility_id, rc.system_size_kw\n        ) AS npv_10yr,\n        -- 25-year total savings\n        rc.annual_savings * 25 AS total_savings_25yr,\n        -- ROI percentage (25-year)\n        CASE\n            WHEN rc.net_system_cost > 0 THEN\n                ((rc.annual_savings * 25 - rc.net_system_cost) / rc.net_system_cost) * 100\n            ELSE NULL\n        END AS roi_25yr_percentage\n    FROM roi_calculations rc\n    CROSS JOIN GENERATE_SERIES(1, 25) AS year_num\n),\nfinal_roi_analysis AS (\n    -- Sixth CTE: Final ROI analysis with comprehensive metrics\n    SELECT\n        npva.state_id,\n        npva.state_name,\n        npva.region,\n        npva.utility_id,\n        npva.utility_name,\n        npva.zip_code,\n        npva.city,\n        npva.system_size_kw,\n        npva.system_name,\n        ROUND(CAST(npva.total_system_cost AS NUMERIC), 2) AS total_system_cost,\n        ROUND(CAST(npva.total_rebates AS NUMERIC), 2) AS total_rebates,\n        ROUND(CAST(npva.net_system_cost AS NUMERIC), 2) AS net_system_cost,\n        ROUND(CAST(npva.rebate_percentage AS NUMERIC), 2) AS rebate_percentage,\n        ROUND(CAST(npva.energy_charge_usd_per_kwh AS NUMERIC), 6) AS energy_charge_usd_per_kwh,\n        npva.annual_kwh_production,\n        ROUND(CAST(npva.annual_savings AS NUMERIC), 2) AS annual_savings,\n        ROUND(CAST(npva.payback_period_years AS NUMERIC), 2) AS payback_period_years,\n        ROUND(CAST(npva.npv_25yr AS NUMERIC), 2) AS npv_25yr,\n        ROUND(CAST(npva.npv_10yr AS NUMERIC), 2) AS npv_10yr,\n        ROUND(CAST(npva.total_savings_25yr AS NUMERIC), 2) AS total_savings_25yr,\n        ROUND(CAST(npva.roi_25yr_percentage AS NUMERIC), 2) AS roi_25yr_percentage,\n        -- Investment classification\n        CASE\n            WHEN npva.payback_period_years <= 5 THEN 'Excellent Investment'\n            WHEN npva.payback_period_years <= 8 THEN 'Good Investment'\n            WHEN npva.payback_period_years <= 12 THEN 'Moderate Investment'\n            ELSE 'Long-Term Investment'\n        END AS investment_classification,\n        -- Window functions for comparison\n        AVG(npva.payback_period_years) OVER (PARTITION BY npva.state_id) AS state_avg_payback,\n        AVG(npva.roi_25yr_percentage) OVER (PARTITION BY npva.state_id) AS state_avg_roi\n    FROM npv_analysis npva\n    WHERE npva.year_num = 1\n)\nSELECT\n    state_id, state_name, region, utility_id, utility_name, zip_code, city,\n    system_size_kw, system_name, total_system_cost, total_rebates, net_system_cost,\n    rebate_percentage, energy_charge_usd_per_kwh, annual_kwh_production,\n    annual_savings, payback_period_years, npv_25yr, npv_10yr, total_savings_25yr,\n    roi_25yr_percentage, investment_classification,\n    ROUND(CAST(state_avg_payback AS NUMERIC), 2) AS state_avg_payback,\n    ROUND(CAST(state_avg_roi AS NUMERIC), 2) AS state_avg_roi\nFROM final_roi_analysis\nORDER BY state_name, payback_period_years;",
  "evidence": "The query joins solar installation records with rebate disbursements and ongoing consumption data to build a complete financial picture. It calculates initial investment costs (installation minus rebates), estimates annual energy savings by multiplying production by avoided electricity rates, and computes simple payback and NPV using appropriate discount rates.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "solar_rebate_aggregations",
    "states",
    "utility_companies",
    "zip_codes",
    "electricity_rates",
    "rebate_aggregation_by_location",
    "solar_system_scenarios",
    "electricity_rate_for_location",
    "roi_calculations",
    "generate_series",
    "npv_analysis",
    "final_roi_analysis"
  ],
  "schema_context": {},
  "expected_output": "Solar rebate ROI analysis with payback periods, NPV calculations, and financial return metrics.",
  "normal_query": "Create a solar rebate ROI analysis that includes payback period calculations, net present value (NPV) metrics, and comprehensive financial return indicators for solar investments."
}
```


### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 9,
  "question": "Can you compare electricity rates across different states and analyze regional market dynamics?",
  "SQL": "WITH state_rate_statistics AS (\n    -- First CTE: Calculate comprehensive state rate statistics\n    SELECT\n        s.state_id,\n        s.state_name,\n        s.region,\n        s.division,\n        COUNT(DISTINCT er.utility_id) AS utility_count,\n        COUNT(DISTINCT er.rate_id) AS total_rate_count,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS median_rate,\n        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS q1_rate,\n        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS q3_rate,\n        MIN(er.energy_charge_usd_per_kwh) AS min_rate,\n        MAX(er.energy_charge_usd_per_kwh) AS max_rate,\n        STDDEV(er.energy_charge_usd_per_kwh) AS stddev_rate,\n        -- Rate type breakdowns\n        AVG(CASE WHEN er.rate_type = 'Residential' THEN er.energy_charge_usd_per_kwh END) AS avg_residential_rate,\n        AVG(CASE WHEN er.rate_type = 'Commercial' THEN er.energy_charge_usd_per_kwh END) AS avg_commercial_rate,\n        AVG(CASE WHEN er.rate_type = 'Industrial' THEN er.energy_charge_usd_per_kwh END) AS avg_industrial_rate\n    FROM states s\n    INNER JOIN electricity_rates er ON s.state_id = er.state_id\n    WHERE er.is_current = TRUE\n    GROUP BY s.state_id, s.state_name, s.region, s.division\n),\nregional_benchmarks AS (\n    -- Second CTE: Calculate regional benchmarks\n    SELECT\n        srs.region,\n        COUNT(DISTINCT srs.state_id) AS state_count,\n        AVG(srs.avg_rate) AS region_avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY srs.avg_rate) AS region_median_rate,\n        MIN(srs.avg_rate) AS region_min_rate,\n        MAX(srs.avg_rate) AS region_max_rate,\n        STDDEV(srs.avg_rate) AS region_stddev_rate,\n        AVG(srs.avg_residential_rate) AS region_avg_residential_rate,\n        AVG(srs.avg_commercial_rate) AS region_avg_commercial_rate,\n        AVG(srs.avg_industrial_rate) AS region_avg_industrial_rate\n    FROM state_rate_statistics srs\n    GROUP BY srs.region\n),\nnational_benchmarks AS (\n    -- Third CTE: Calculate national benchmarks\n    SELECT\n        AVG(srs.avg_rate) AS national_avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY srs.avg_rate) AS national_median_rate,\n        MIN(srs.avg_rate) AS national_min_rate,\n        MAX(srs.avg_rate) AS national_max_rate,\n        STDDEV(srs.avg_rate) AS national_stddev_rate\n    FROM state_rate_statistics srs\n),\nstate_comparison_matrix AS (\n    -- Fourth CTE: Create state comparison matrix\n    SELECT\n        srs1.state_id AS state_1_id,\n        srs1.state_name AS state_1_name,\n        srs1.region AS state_1_region,\n        srs1.avg_rate AS state_1_avg_rate,\n        srs2.state_id AS state_2_id,\n        srs2.state_name AS state_2_name,\n        srs2.region AS state_2_region,\n        srs2.avg_rate AS state_2_avg_rate,\n        srs1.avg_rate - srs2.avg_rate AS rate_difference,\n        CASE\n            WHEN srs2.avg_rate > 0 THEN\n                ((srs1.avg_rate - srs2.avg_rate) / srs2.avg_rate) * 100\n            ELSE NULL\n        END AS rate_difference_percentage,\n        CASE\n            WHEN srs1.region = srs2.region THEN 'Same Region'\n            ELSE 'Different Region'\n        END AS regional_comparison_type\n    FROM state_rate_statistics srs1\n    CROSS JOIN state_rate_statistics srs2\n    WHERE srs1.state_id < srs2.state_id\n),\nregional_positioning AS (\n    -- Fifth CTE: Analyze regional positioning\n    SELECT\n        srs.*,\n        rb.region_avg_rate,\n        rb.region_median_rate,\n        rb.region_min_rate,\n        rb.region_max_rate,\n        nb.national_avg_rate,\n        nb.national_median_rate,\n        -- Regional positioning\n        srs.avg_rate - rb.region_avg_rate AS difference_from_region_avg,\n        CASE\n            WHEN rb.region_avg_rate > 0 THEN\n                ((srs.avg_rate - rb.region_avg_rate) / rb.region_avg_rate) * 100\n            ELSE NULL\n        END AS difference_from_region_avg_percentage,\n        -- National positioning\n        srs.avg_rate - nb.national_avg_rate AS difference_from_national_avg,\n        CASE\n            WHEN nb.national_avg_rate > 0 THEN\n                ((srs.avg_rate - nb.national_avg_rate) / nb.national_avg_rate) * 100\n            ELSE NULL\n        END AS difference_from_national_avg_percentage,\n        -- Regional quartile\n        CASE\n            WHEN srs.avg_rate <= PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY srs.avg_rate) OVER (PARTITION BY srs.region) THEN 'Lowest Quartile'\n            WHEN srs.avg_rate <= PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY srs.avg_rate) OVER (PARTITION BY srs.region) THEN 'Second Quartile'\n            WHEN srs.avg_rate <= PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY srs.avg_rate) OVER (PARTITION BY srs.region) THEN 'Third Quartile'\n            ELSE 'Highest Quartile'\n        END AS regional_quartile,\n        -- National percentile\n        PERCENT_RANK() OVER (ORDER BY srs.avg_rate) AS national_percentile_rank\n    FROM state_rate_statistics srs\n    CROSS JOIN regional_benchmarks rb ON srs.region = rb.region\n    CROSS JOIN national_benchmarks nb\n),\nfinal_cross_state_comparison AS (\n    -- Sixth CTE: Final cross-state comparison\n    SELECT\n        rp.*,\n        ROW_NUMBER() OVER (PARTITION BY rp.region ORDER BY rp.avg_rate) AS region_rate_rank,\n        COUNT(*) OVER (PARTITION BY rp.region) AS states_in_region,\n        -- Market classification\n        CASE\n            WHEN rp.difference_from_national_avg_percentage < -15 THEN 'Very Low Cost State'\n            WHEN rp.difference_from_national_avg_percentage < -5 THEN 'Low Cost State'\n            WHEN rp.difference_from_national_avg_percentage < 5 THEN 'Average Cost State'\n            WHEN rp.difference_from_national_avg_percentage < 15 THEN 'High Cost State'\n            ELSE 'Very High Cost State'\n        END AS market_classification\n    FROM regional_positioning rp\n)\nSELECT\n    state_id, state_name, region, division,\n    utility_count, total_rate_count,\n    ROUND(CAST(avg_rate AS NUMERIC), 6) AS avg_rate,\n    ROUND(CAST(median_rate AS NUMERIC), 6) AS median_rate,\n    ROUND(CAST(q1_rate AS NUMERIC), 6) AS q1_rate,\n    ROUND(CAST(q3_rate AS NUMERIC), 6) AS q3_rate,\n    ROUND(CAST(min_rate AS NUMERIC), 6) AS min_rate,\n    ROUND(CAST(max_rate AS NUMERIC), 6) AS max_rate,\n    ROUND(CAST(avg_residential_rate AS NUMERIC), 6) AS avg_residential_rate,\n    ROUND(CAST(avg_commercial_rate AS NUMERIC), 6) AS avg_commercial_rate,\n    ROUND(CAST(avg_industrial_rate AS NUMERIC), 6) AS avg_industrial_rate,\n    ROUND(CAST(region_avg_rate AS NUMERIC), 6) AS region_avg_rate,\n    ROUND(CAST(difference_from_region_avg AS NUMERIC), 6) AS difference_from_region_avg,\n    ROUND(CAST(difference_from_region_avg_percentage AS NUMERIC), 2) AS difference_from_region_avg_percentage,\n    ROUND(CAST(national_avg_rate AS NUMERIC), 6) AS national_avg_rate,\n    ROUND(CAST(difference_from_national_avg AS NUMERIC), 6) AS difference_from_national_avg,\n    ROUND(CAST(difference_from_national_avg_percentage AS NUMERIC), 2) AS difference_from_national_avg_percentage,\n    regional_quartile,\n    ROUND(CAST(national_percentile_rank * 100 AS NUMERIC), 2) AS national_percentile_rank,\n    region_rate_rank,\n    states_in_region,\n    market_classification\nFROM final_cross_state_comparison\nORDER BY avg_rate;",
  "evidence": "The query aggregates rate and consumption data grouped by state and utility to calculate average rates, rate ranges, and customer-weighted average prices. It uses window functions to rank states by rate competitiveness and calculate regional percentiles. Subqueries or CTEs compute year-over-year rate changes.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "states",
    "electricity_rates",
    "state_rate_statistics",
    "regional_benchmarks",
    "national_benchmarks",
    "regional_positioning",
    "final_cross_state_comparison"
  ],
  "schema_context": {},
  "expected_output": "Cross-state rate comparison with regional market dynamics, competitive analysis, and market trends.",
  "normal_query": "Generate a cross-state rate comparison report that examines regional market dynamics, performs competitive analysis across state boundaries, and identifies emerging market trends."
}
```


### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 10,
  "question": "Can you analyze the complexity of different rate structures and identify optimization opportunities for multi-tier pricing?",
  "SQL": "WITH rate_structure_details AS (\n    -- First CTE: Gather comprehensive rate structure details\n    SELECT\n        rs.rate_structure_id,\n        rs.utility_id,\n        rs.rate_code_id,\n        rs.rate_name,\n        rs.rate_structure_type,\n        rs.effective_date,\n        er.energy_charge_usd_per_kwh,\n        er.fixed_charge_usd,\n        er.demand_charge_usd_per_kw,\n        rc.rate_structure_type AS code_structure_type,\n        COUNT(DISTINCT trt.tier_id) AS tier_count,\n        COUNT(DISTINCT tou.tou_period_id) AS tou_period_count\n    FROM rate_structures rs\n    INNER JOIN electricity_rates er ON rs.rate_structure_id = er.rate_structure_id\n    INNER JOIN rate_codes rc ON rs.rate_code_id = rc.rate_code_id\n    LEFT JOIN tiered_rate_tiers trt ON rs.rate_structure_id = trt.rate_structure_id\n    LEFT JOIN time_of_use_periods tou ON rs.rate_structure_id = tou.rate_structure_id\n    WHERE rs.is_current = TRUE AND er.is_current = TRUE\n    GROUP BY rs.rate_structure_id, rs.utility_id, rs.rate_code_id, rs.rate_name, rs.rate_structure_type,\n             rs.effective_date, er.energy_charge_usd_per_kwh, er.fixed_charge_usd, er.demand_charge_usd_per_kw,\n             rc.rate_structure_type\n),\ntier_complexity_analysis AS (\n    -- Second CTE: Analyze tier complexity\n    SELECT\n        rsd.rate_structure_id,\n        rsd.tier_count,\n        COUNT(DISTINCT trt.tier_number) AS distinct_tier_levels,\n        AVG(trt.energy_charge_usd_per_kwh) AS avg_tier_rate,\n        STDDEV(trt.energy_charge_usd_per_kwh) AS tier_rate_stddev,\n        MAX(trt.tier_end_kwh) - MIN(trt.tier_start_kwh) AS total_tier_range_kwh,\n        AVG(COALESCE(trt.tier_end_kwh, 999999) - trt.tier_start_kwh) AS avg_tier_width_kwh\n    FROM rate_structure_details rsd\n    LEFT JOIN tiered_rate_tiers trt ON rsd.rate_structure_id = trt.rate_structure_id\n    GROUP BY rsd.rate_structure_id, rsd.tier_count\n),\ntou_complexity_analysis AS (\n    -- Third CTE: Analyze TOU complexity\n    SELECT\n        rsd.rate_structure_id,\n        rsd.tou_period_count,\n        COUNT(DISTINCT tou.period_name) AS distinct_period_names,\n        COUNT(DISTINCT tou.season) AS distinct_seasons,\n        COUNT(DISTINCT tou.day_of_week) AS distinct_days,\n        AVG(tou.energy_charge_usd_per_kwh) AS avg_tou_rate,\n        STDDEV(tou.energy_charge_usd_per_kwh) AS tou_rate_stddev,\n        MAX(tou.energy_charge_usd_per_kwh) - MIN(tou.energy_charge_usd_per_kwh) AS tou_rate_range\n    FROM rate_structure_details rsd\n    LEFT JOIN time_of_use_periods tou ON rsd.rate_structure_id = tou.rate_structure_id\n    GROUP BY rsd.rate_structure_id, rsd.tou_period_count\n),\ncomplexity_metrics AS (\n    -- Fourth CTE: Calculate comprehensive complexity metrics\n    SELECT\n        rsd.*,\n        tca.tier_count,\n        tca.distinct_tier_levels,\n        tca.avg_tier_rate,\n        tca.tier_rate_stddev,\n        tca.total_tier_range_kwh,\n        tca.avg_tier_width_kwh,\n        toua.tou_period_count,\n        toua.distinct_period_names,\n        toua.distinct_seasons,\n        toua.distinct_days,\n        toua.avg_tou_rate,\n        toua.tou_rate_stddev,\n        toua.tou_rate_range,\n        -- Complexity score (weighted)\n        (COALESCE(rsd.tier_count, 0) * 2) +\n        (COALESCE(rsd.tou_period_count, 0) * 1.5) +\n        (CASE WHEN er.demand_charge_usd_per_kw > 0 THEN 1 ELSE 0 END) +\n        (CASE WHEN er.fixed_charge_usd > 0 THEN 0.5 ELSE 0 END) AS complexity_score\n    FROM rate_structure_details rsd\n    LEFT JOIN tier_complexity_analysis tca ON rsd.rate_structure_id = tca.rate_structure_id\n    LEFT JOIN tou_complexity_analysis toua ON rsd.rate_structure_id = toua.rate_structure_id\n    INNER JOIN electricity_rates er ON rsd.rate_structure_id = er.rate_structure_id\n),\nstructure_optimization_analysis AS (\n    -- Fifth CTE: Analyze optimization opportunities\n    SELECT\n        cm.*,\n        uc.utility_name,\n        rc.rate_code,\n        s.state_name,\n        -- Complexity classification\n        CASE\n            WHEN cm.complexity_score >= 10 THEN 'Very Complex'\n            WHEN cm.complexity_score >= 6 THEN 'Complex'\n            WHEN cm.complexity_score >= 3 THEN 'Moderate'\n            ELSE 'Simple'\n        END AS complexity_classification,\n        -- Optimization opportunities\n        CASE\n            WHEN cm.tier_count > 5 THEN 'Consider Tier Consolidation'\n            WHEN cm.tou_period_count > 4 THEN 'Consider TOU Period Simplification'\n            WHEN cm.complexity_score > 8 THEN 'High Optimization Potential'\n            ELSE 'Low Optimization Potential'\n        END AS optimization_recommendation,\n        -- Window functions for comparison\n        AVG(cm.complexity_score) OVER (PARTITION BY cm.state_id) AS state_avg_complexity,\n        AVG(cm.complexity_score) OVER (PARTITION BY cm.utility_id) AS utility_avg_complexity\n    FROM complexity_metrics cm\n    INNER JOIN utility_companies uc ON cm.utility_id = uc.utility_id\n    INNER JOIN rate_codes rc ON cm.rate_code_id = rc.rate_code_id\n    INNER JOIN states s ON uc.state_id = s.state_id\n),\nfinal_complexity_analysis AS (\n    -- Sixth CTE: Final complexity analysis\n    SELECT\n        soa.*,\n        ROUND(CAST(soa.complexity_score AS NUMERIC), 2) AS complexity_score,\n        ROUND(CAST(soa.state_avg_complexity AS NUMERIC), 2) AS state_avg_complexity,\n        ROUND(CAST(soa.utility_avg_complexity AS NUMERIC), 2) AS utility_avg_complexity,\n        CASE\n            WHEN soa.complexity_score > soa.state_avg_complexity THEN 'Above State Average'\n            WHEN soa.complexity_score = soa.state_avg_complexity THEN 'At State Average'\n            ELSE 'Below State Average'\n        END AS complexity_positioning\n    FROM structure_optimization_analysis soa\n)\nSELECT\n    rate_structure_id, utility_id, utility_name, rate_code_id, rate_code,\n    state_id, state_name, rate_name, rate_structure_type,\n    tier_count, distinct_tier_levels, tou_period_count, distinct_period_names,\n    complexity_score, complexity_classification, optimization_recommendation,\n    state_avg_complexity, utility_avg_complexity, complexity_positioning\nFROM final_complexity_analysis\nORDER BY complexity_score DESC, state_name, utility_name;",
  "evidence": "The query analyzes rate structure definitions to compute complexity scores based on factors like number of pricing tiers, presence of time-of-use periods, and demand charge components. It groups by rate code and applies scoring logic.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "rate_structures",
    "electricity_rates",
    "rate_codes",
    "tiered_rate_tiers",
    "time_of_use_periods",
    "rate_structure_details",
    "tier_complexity_analysis",
    "tou_complexity_analysis",
    "complexity_metrics",
    "utility_companies",
    "states",
    "structure_optimization_analysis",
    "final_complexity_analysis"
  ],
  "schema_context": {},
  "expected_output": "Rate structure complexity analysis with complexity metrics, multi-tier optimization, and structure comparisons.",
  "normal_query": "Develop a rate structure complexity analysis that measures complexity metrics for different pricing models, identifies multi-tier optimization opportunities, and provides structure-to-structure comparisons."
}
```


### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 11,
  "question": "Can you show me the historical trends of rebate programs along with analysis of when incentives are expiring?",
  "SQL": "WITH federal_rebate_timeline AS (\n    -- First CTE: Build federal rebate timeline\n    SELECT\n        fi.federal_incentive_id,\n        fi.incentive_name,\n        fi.incentive_type,\n        fi.effective_date,\n        fi.expiration_date,\n        fi.incentive_amount_usd,\n        fi.incentive_percentage,\n        fi.maximum_incentive_usd,\n        EXTRACT(EPOCH FROM (fi.expiration_date - fi.effective_date)) / 86400 AS days_active,\n        EXTRACT(EPOCH FROM (fi.expiration_date - CURRENT_DATE)) / 86400 AS days_until_expiration,\n        CASE\n            WHEN fi.expiration_date IS NULL THEN 'No Expiration'\n            WHEN fi.expiration_date > CURRENT_DATE THEN 'Active'\n            ELSE 'Expired'\n        END AS status\n    FROM federal_incentives fi\n    WHERE 'Solar Photovoltaics' = ANY(fi.eligible_technologies)\n),\nstate_rebate_timeline AS (\n    -- Second CTE: Build state rebate timeline\n    SELECT\n        si.state_incentive_id,\n        si.state_id,\n        s.state_name,\n        si.incentive_name,\n        si.incentive_type,\n        si.effective_date,\n        si.expiration_date,\n        si.incentive_amount_usd,\n        si.incentive_percentage,\n        si.maximum_incentive_usd,\n        EXTRACT(EPOCH FROM (si.expiration_date - si.effective_date)) / 86400 AS days_active,\n        EXTRACT(EPOCH FROM (si.expiration_date - CURRENT_DATE)) / 86400 AS days_until_expiration,\n        CASE\n            WHEN si.expiration_date IS NULL THEN 'No Expiration'\n            WHEN si.expiration_date > CURRENT_DATE THEN 'Active'\n            ELSE 'Expired'\n        END AS status\n    FROM state_incentives si\n    INNER JOIN states s ON si.state_id = s.state_id\n    WHERE 'Solar Photovoltaics' = ANY(si.eligible_technologies)\n),\nutility_rebate_timeline AS (\n    -- Third CTE: Build utility rebate timeline\n    SELECT\n        ui.utility_incentive_id,\n        ui.utility_id,\n        uc.utility_name,\n        ui.state_id,\n        ui.incentive_name,\n        ui.incentive_type,\n        ui.effective_date,\n        ui.expiration_date,\n        ui.incentive_amount_usd,\n        ui.incentive_percentage,\n        ui.maximum_incentive_usd,\n        EXTRACT(EPOCH FROM (ui.expiration_date - ui.effective_date)) / 86400 AS days_active,\n        EXTRACT(EPOCH FROM (ui.expiration_date - CURRENT_DATE)) / 86400 AS days_until_expiration,\n        CASE\n            WHEN ui.expiration_date IS NULL THEN 'No Expiration'\n            WHEN ui.expiration_date > CURRENT_DATE THEN 'Active'\n            ELSE 'Expired'\n        END AS status\n    FROM utility_incentives ui\n    INNER JOIN utility_companies uc ON ui.utility_id = uc.utility_id\n    WHERE 'Solar Photovoltaics' = ANY(ui.eligible_technologies)\n),\nrebate_expiration_analysis AS (\n    -- Fourth CTE: Analyze rebate expirations\n    SELECT\n        'Federal' AS rebate_level,\n        COUNT(*) AS total_rebates,\n        COUNT(CASE WHEN status = 'Active' THEN 1 END) AS active_rebates,\n        COUNT(CASE WHEN status = 'Expired' THEN 1 END) AS expired_rebates,\n        COUNT(CASE WHEN days_until_expiration BETWEEN 0 AND 90 THEN 1 END) AS expiring_90days,\n        COUNT(CASE WHEN days_until_expiration BETWEEN 91 AND 180 THEN 1 END) AS expiring_180days,\n        COUNT(CASE WHEN days_until_expiration BETWEEN 181 AND 365 THEN 1 END) AS expiring_1year,\n        AVG(days_until_expiration) AS avg_days_until_expiration,\n        MIN(days_until_expiration) AS min_days_until_expiration\n    FROM federal_rebate_timeline\n    UNION ALL\n    SELECT\n        'State' AS rebate_level,\n        COUNT(*),\n        COUNT(CASE WHEN status = 'Active' THEN 1 END),\n        COUNT(CASE WHEN status = 'Expired' THEN 1 END),\n        COUNT(CASE WHEN days_until_expiration BETWEEN 0 AND 90 THEN 1 END),\n        COUNT(CASE WHEN days_until_expiration BETWEEN 91 AND 180 THEN 1 END),\n        COUNT(CASE WHEN days_until_expiration BETWEEN 181 AND 365 THEN 1 END),\n        AVG(days_until_expiration),\n        MIN(days_until_expiration)\n    FROM state_rebate_timeline\n    UNION ALL\n    SELECT\n        'Utility' AS rebate_level,\n        COUNT(*),\n        COUNT(CASE WHEN status = 'Active' THEN 1 END),\n        COUNT(CASE WHEN status = 'Expired' THEN 1 END),\n        COUNT(CASE WHEN days_until_expiration BETWEEN 0 AND 90 THEN 1 END),\n        COUNT(CASE WHEN days_until_expiration BETWEEN 91 AND 180 THEN 1 END),\n        COUNT(CASE WHEN days_until_expiration BETWEEN 181 AND 365 THEN 1 END),\n        AVG(days_until_expiration),\n        MIN(days_until_expiration)\n    FROM utility_rebate_timeline\n),\nrebate_trend_analysis AS (\n    -- Fifth CTE: Analyze rebate trends over time\n    SELECT\n        DATE_TRUNC('year', effective_date) AS year,\n        DATE_TRUNC('quarter', effective_date) AS quarter,\n        COUNT(*) AS rebates_introduced,\n        AVG(incentive_amount_usd) AS avg_incentive_amount,\n        SUM(incentive_amount_usd) AS total_incentive_value\n    FROM (\n        SELECT effective_date, incentive_amount_usd FROM federal_rebate_timeline\n        UNION ALL\n        SELECT effective_date, incentive_amount_usd FROM state_rebate_timeline\n        UNION ALL\n        SELECT effective_date, incentive_amount_usd FROM utility_rebate_timeline\n    ) all_rebates\n    GROUP BY DATE_TRUNC('year', effective_date), DATE_TRUNC('quarter', effective_date)\n),\nfinal_expiration_intelligence AS (\n    -- Sixth CTE: Final expiration intelligence\n    SELECT\n        rea.*,\n        ROUND(CAST(rea.avg_days_until_expiration AS NUMERIC), 0) AS avg_days_until_expiration,\n        ROUND(CAST(rea.min_days_until_expiration AS NUMERIC), 0) AS min_days_until_expiration,\n        CASE\n            WHEN rea.expiring_90days > 0 THEN 'High Expiration Risk'\n            WHEN rea.expiring_180days > 0 THEN 'Moderate Expiration Risk'\n            WHEN rea.expiring_1year > 0 THEN 'Low Expiration Risk'\n            ELSE 'No Near-Term Expirations'\n        END AS expiration_risk_level\n    FROM rebate_expiration_analysis rea\n)\nSELECT\n    rebate_level, total_rebates, active_rebates, expired_rebates,\n    expiring_90days, expiring_180days, expiring_1year,\n    avg_days_until_expiration, min_days_until_expiration, expiration_risk_level\nFROM final_expiration_intelligence\nORDER BY rebate_level;",
  "evidence": "The query joins rebates, installations, and consumption tables on relevant keys with NULL-safe handling. It groups data by time periods and program dimensions to compute aggregate metrics such as total rebate amounts, application counts, and approval rates. Window functions calculate rolling averages and year-over-year comparisons. Date logic identifies programs nearing expiration.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "federal_incentives",
    "state_incentives",
    "states",
    "utility_incentives",
    "utility_companies",
    "federal_rebate_timeline",
    "state_rebate_timeline",
    "utility_rebate_timeline",
    "rebate_expiration_analysis",
    "final_expiration_intelligence"
  ],
  "schema_context": {},
  "expected_output": "Historical rebate trend analysis with expiration forecasts, lifecycle tracking, and trend identification.",
  "normal_query": "Analyze historical rebate trends including expiration forecasts, program lifecycle tracking, and emerging trend identification."
}
```


### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 12,
  "question": "Can you provide geographic rate optimization analysis broken down by zip code?",
  "SQL": "WITH zip_code_rate_analysis AS (\n    -- First CTE: Analyze rates by zip code\n    SELECT\n        zc.zip_code,\n        zc.city,\n        zc.state_id,\n        s.state_name,\n        zc.county_id,\n        c.county_name,\n        zc.latitude,\n        zc.longitude,\n        COUNT(DISTINCT gra.rate_structure_id) AS available_rate_structures,\n        COUNT(DISTINCT gra.utility_id) AS utilities_serving_zip,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_zip_rate,\n        MIN(er.energy_charge_usd_per_kwh) AS min_zip_rate,\n        MAX(er.energy_charge_usd_per_kwh) AS max_zip_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS median_zip_rate\n    FROM zip_codes zc\n    INNER JOIN states s ON zc.state_id = s.state_id\n    LEFT JOIN counties c ON zc.county_id = c.county_id\n    LEFT JOIN geographic_rate_areas gra ON zc.zip_code = gra.zip_code\n    LEFT JOIN electricity_rates er ON gra.rate_structure_id = er.rate_structure_id\n    WHERE er.is_current = TRUE\n    GROUP BY zc.zip_code, zc.city, zc.state_id, s.state_name, zc.county_id, c.county_name, zc.latitude, zc.longitude\n),\ncounty_rate_benchmarks AS (\n    -- Second CTE: Calculate county-level benchmarks\n    SELECT\n        c.county_id,\n        c.county_name,\n        c.state_id,\n        AVG(zcra.avg_zip_rate) AS county_avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY zcra.avg_zip_rate) AS county_median_rate,\n        MIN(zcra.avg_zip_rate) AS county_min_rate,\n        MAX(zcra.avg_zip_rate) AS county_max_rate\n    FROM zip_code_rate_analysis zcra\n    INNER JOIN counties c ON zcra.county_id = c.county_id\n    GROUP BY c.county_id, c.county_name, c.state_id\n),\nstate_rate_benchmarks AS (\n    -- Third CTE: Calculate state-level benchmarks\n    SELECT\n        s.state_id,\n        s.state_name,\n        AVG(zcra.avg_zip_rate) AS state_avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY zcra.avg_zip_rate) AS state_median_rate\n    FROM zip_code_rate_analysis zcra\n    INNER JOIN states s ON zcra.state_id = s.state_id\n    GROUP BY s.state_id, s.state_name\n),\nzip_code_optimization AS (\n    -- Fourth CTE: Optimize rates by zip code\n    SELECT\n        zcra.*,\n        crb.county_avg_rate,\n        crb.county_median_rate,\n        crb.county_min_rate,\n        crb.county_max_rate,\n        srb.state_avg_rate,\n        srb.state_median_rate,\n        -- Optimization metrics\n        zcra.avg_zip_rate - crb.county_avg_rate AS difference_from_county_avg,\n        CASE\n            WHEN crb.county_avg_rate > 0 THEN\n                ((zcra.avg_zip_rate - crb.county_avg_rate) / crb.county_avg_rate) * 100\n            ELSE NULL\n        END AS difference_from_county_avg_percentage,\n        zcra.avg_zip_rate - srb.state_avg_rate AS difference_from_state_avg,\n        CASE\n            WHEN srb.state_avg_rate > 0 THEN\n                ((zcra.avg_zip_rate - srb.state_avg_rate) / srb.state_avg_rate) * 100\n            ELSE NULL\n        END AS difference_from_state_avg_percentage,\n        -- Rate competitiveness\n        CASE\n            WHEN zcra.avg_zip_rate <= crb.county_min_rate THEN 'Most Competitive'\n            WHEN zcra.avg_zip_rate <= crb.county_median_rate THEN 'Competitive'\n            WHEN zcra.avg_zip_rate <= crb.county_avg_rate THEN 'Average'\n            ELSE 'Above Average'\n        END AS competitiveness_classification\n    FROM zip_code_rate_analysis zcra\n    LEFT JOIN county_rate_benchmarks crb ON zcra.county_id = crb.county_id\n    INNER JOIN state_rate_benchmarks srb ON zcra.state_id = srb.state_id\n),\nfinal_geographic_optimization AS (\n    -- Fifth CTE: Final geographic optimization\n    SELECT\n        zco.*,\n        ROUND(CAST(zco.difference_from_county_avg AS NUMERIC), 6) AS difference_from_county_avg,\n        ROUND(CAST(zco.difference_from_county_avg_percentage AS NUMERIC), 2) AS difference_from_county_avg_percentage,\n        ROUND(CAST(zco.difference_from_state_avg AS NUMERIC), 6) AS difference_from_state_avg,\n        ROUND(CAST(zco.difference_from_state_avg_percentage AS NUMERIC), 2) AS difference_from_state_avg_percentage,\n        -- Window functions for ranking\n        ROW_NUMBER() OVER (PARTITION BY zco.state_id ORDER BY zco.avg_zip_rate) AS state_rate_rank,\n        PERCENT_RANK() OVER (PARTITION BY zco.state_id ORDER BY zco.avg_zip_rate) AS state_rate_percentile\n    FROM zip_code_optimization zco\n)\nSELECT\n    zip_code, city, state_id, state_name, county_id, county_name,\n    latitude, longitude, available_rate_structures, utilities_serving_zip,\n    ROUND(CAST(avg_zip_rate AS NUMERIC), 6) AS avg_zip_rate,\n    ROUND(CAST(min_zip_rate AS NUMERIC), 6) AS min_zip_rate,\n    ROUND(CAST(max_zip_rate AS NUMERIC), 6) AS max_zip_rate,\n    ROUND(CAST(median_zip_rate AS NUMERIC), 6) AS median_zip_rate,\n    ROUND(CAST(county_avg_rate AS NUMERIC), 6) AS county_avg_rate,\n    difference_from_county_avg, difference_from_county_avg_percentage,\n    ROUND(CAST(state_avg_rate AS NUMERIC), 6) AS state_avg_rate,\n    difference_from_state_avg, difference_from_state_avg_percentage,\n    competitiveness_classification, state_rate_rank,\n    ROUND(CAST(state_rate_percentile * 100 AS NUMERIC), 2) AS state_rate_percentile\nFROM final_geographic_optimization\nORDER BY state_name, avg_zip_rate;",
  "evidence": "The query joins customer, consumption, rate, and geographic tables using zip code as the primary dimension. It groups data by zip code and computes aggregated metrics including average rates, total consumption, customer counts, and solar installation penetration. Window functions rank zip codes by performance indicators and calculate percentile distributions. Statistical measures identify outlier zip codes.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "zip_codes",
    "states",
    "counties",
    "geographic_rate_areas",
    "electricity_rates",
    "zip_code_rate_analysis",
    "county_rate_benchmarks",
    "state_rate_benchmarks",
    "zip_code_optimization",
    "final_geographic_optimization"
  ],
  "schema_context": {},
  "expected_output": "Geographic rate optimization with zip code level intelligence and location-based recommendations.",
  "normal_query": "Perform geographic rate optimization with zip code-level intelligence and location-based pricing recommendations."
}
```


### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 13,
  "question": "Can you analyze our utility rate portfolio and show me the diversity metrics across different rate codes?",
  "SQL": "WITH utility_rate_portfolio AS (\n    -- First CTE: Build utility rate portfolio\n    SELECT\n        uc.utility_id,\n        uc.utility_name,\n        uc.utility_type,\n        uc.state_id,\n        s.state_name,\n        COUNT(DISTINCT er.rate_code_id) AS rate_codes_offered,\n        COUNT(DISTINCT er.rate_id) AS total_rates,\n        COUNT(DISTINCT er.rate_type) AS rate_types_offered,\n        COUNT(DISTINCT rc.rate_structure_type) AS structure_types_offered,\n        COUNT(DISTINCT rc.sector) AS sectors_covered,\n        AVG(er.energy_charge_usd_per_kwh) AS portfolio_avg_rate,\n        MIN(er.energy_charge_usd_per_kwh) AS portfolio_min_rate,\n        MAX(er.energy_charge_usd_per_kwh) AS portfolio_max_rate,\n        STDDEV(er.energy_charge_usd_per_kwh) AS portfolio_rate_stddev\n    FROM utility_companies uc\n    INNER JOIN states s ON uc.state_id = s.state_id\n    INNER JOIN electricity_rates er ON uc.utility_id = er.utility_id\n    INNER JOIN rate_codes rc ON er.rate_code_id = rc.rate_code_id\n    WHERE er.is_current = TRUE AND uc.is_active = TRUE\n    GROUP BY uc.utility_id, uc.utility_name, uc.utility_type, uc.state_id, s.state_name\n),\nstate_portfolio_benchmarks AS (\n    -- Second CTE: Calculate state portfolio benchmarks\n    SELECT\n        urp.state_id,\n        AVG(urp.rate_codes_offered) AS state_avg_rate_codes,\n        AVG(urp.total_rates) AS state_avg_total_rates,\n        AVG(urp.rate_types_offered) AS state_avg_rate_types,\n        AVG(urp.structure_types_offered) AS state_avg_structure_types,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY urp.rate_codes_offered) AS state_median_rate_codes\n    FROM utility_rate_portfolio urp\n    GROUP BY urp.state_id\n),\nportfolio_diversity_metrics AS (\n    -- Third CTE: Calculate portfolio diversity metrics\n    SELECT\n        urp.*,\n        spb.state_avg_rate_codes,\n        spb.state_avg_total_rates,\n        spb.state_avg_rate_types,\n        spb.state_avg_structure_types,\n        spb.state_median_rate_codes,\n        -- Diversity score (weighted)\n        (urp.rate_codes_offered * 2.0) +\n        (urp.rate_types_offered * 1.5) +\n        (urp.structure_types_offered * 1.0) +\n        (urp.sectors_covered * 1.5) AS diversity_score,\n        -- Portfolio completeness\n        CASE\n            WHEN urp.rate_types_offered >= 3 AND urp.sectors_covered >= 3 THEN 'Complete Portfolio'\n            WHEN urp.rate_types_offered >= 2 AND urp.sectors_covered >= 2 THEN 'Moderate Portfolio'\n            ELSE 'Limited Portfolio'\n        END AS portfolio_completeness,\n        -- Rate range diversity\n        CASE\n            WHEN urp.portfolio_max_rate - urp.portfolio_min_rate > urp.portfolio_avg_rate * 0.3 THEN 'High Diversity'\n            WHEN urp.portfolio_max_rate - urp.portfolio_min_rate > urp.portfolio_avg_rate * 0.15 THEN 'Moderate Diversity'\n            ELSE 'Low Diversity'\n        END AS rate_range_diversity\n    FROM utility_rate_portfolio urp\n    INNER JOIN state_portfolio_benchmarks spb ON urp.state_id = spb.state_id\n),\nfinal_portfolio_analysis AS (\n    -- Fourth CTE: Final portfolio analysis\n    SELECT\n        pdm.*,\n        ROUND(CAST(pdm.diversity_score AS NUMERIC), 2) AS diversity_score,\n        -- Portfolio positioning\n        CASE\n            WHEN pdm.rate_codes_offered > pdm.state_avg_rate_codes THEN 'Above State Average'\n            WHEN pdm.rate_codes_offered = pdm.state_avg_rate_codes THEN 'At State Average'\n            ELSE 'Below State Average'\n        END AS portfolio_positioning,\n        -- Optimization recommendations\n        CASE\n            WHEN pdm.rate_types_offered < 3 THEN 'Consider Adding More Rate Types'\n            WHEN pdm.sectors_covered < 3 THEN 'Consider Expanding Sector Coverage'\n            WHEN pdm.structure_types_offered < 2 THEN 'Consider Adding Structure Types'\n            ELSE 'Portfolio Well Diversified'\n        END AS optimization_recommendation\n    FROM portfolio_diversity_metrics pdm\n)\nSELECT\n    utility_id, utility_name, utility_type, state_id, state_name,\n    rate_codes_offered, total_rates, rate_types_offered, structure_types_offered, sectors_covered,\n    ROUND(CAST(portfolio_avg_rate AS NUMERIC), 6) AS portfolio_avg_rate,\n    ROUND(CAST(portfolio_min_rate AS NUMERIC), 6) AS portfolio_min_rate,\n    ROUND(CAST(portfolio_max_rate AS NUMERIC), 6) AS portfolio_max_rate,\n    ROUND(CAST(state_avg_rate_codes AS NUMERIC), 2) AS state_avg_rate_codes,\n    diversity_score, portfolio_completeness, rate_range_diversity,\n    portfolio_positioning, optimization_recommendation\nFROM final_portfolio_analysis\nORDER BY state_name, diversity_score DESC;",
  "evidence": "The query aggregates data from rate schedules, customer assignments, and consumption tables grouped by rate code. It computes diversity metrics including customer count per rate, revenue contribution, concentration indices (HHI), and usage pattern variance. Window functions calculate each rate's share of total portfolio and rank rates by multiple dimensions. Quartile analysis segments rates into performance tiers.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "utility_companies",
    "states",
    "electricity_rates",
    "rate_codes",
    "utility_rate_portfolio",
    "state_portfolio_benchmarks",
    "portfolio_diversity_metrics",
    "final_portfolio_analysis"
  ],
  "schema_context": {},
  "expected_output": "Utility rate portfolio analysis with diversity metrics and optimization recommendations.",
  "normal_query": "Analyze the utility rate portfolio with diversity metrics across rate codes and provide optimization recommendations."
}
```


### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 14,
  "question": "Can you show me the financial economics of solar installations including net metering analysis?",
  "SQL": "WITH solar_system_economics AS (\n    -- First CTE: Define solar system economics\n    SELECT\n        system_size_kw,\n        system_cost_per_watt,\n        annual_production_kwh,\n        system_cost_per_watt * system_size_kw * 1000 AS total_system_cost\n    FROM (VALUES\n        (5.0, 3.0, 7500),\n        (10.0, 3.0, 15000),\n        (20.0, 2.8, 30000),\n        (50.0, 2.5, 75000),\n        (100.0, 2.3, 150000)\n    ) AS systems(system_size_kw, system_cost_per_watt, annual_production_kwh)\n),\nnet_metering_analysis AS (\n    -- Second CTE: Analyze net metering programs\n    SELECT\n        ui.utility_incentive_id,\n        ui.utility_id,\n        uc.utility_name,\n        ui.state_id,\n        ui.incentive_type,\n        ui.net_metering_capacity_limit_kw,\n        ui.feed_in_tariff_rate_usd_per_kwh,\n        er.energy_charge_usd_per_kwh AS retail_rate,\n        CASE\n            WHEN ui.feed_in_tariff_rate_usd_per_kwh IS NOT NULL THEN ui.feed_in_tariff_rate_usd_per_kwh\n            ELSE er.energy_charge_usd_per_kwh\n        END AS effective_export_rate\n    FROM utility_incentives ui\n    INNER JOIN utility_companies uc ON ui.utility_id = uc.utility_id\n    LEFT JOIN electricity_rates er ON ui.utility_id = er.utility_id AND er.rate_type = 'Residential'\n    WHERE ui.incentive_type IN ('Net Metering', 'Feed-in Tariff')\n        AND ui.is_active = TRUE\n        AND er.is_current = TRUE\n),\nsolar_economics_calculations AS (\n    -- Third CTE: Calculate solar economics\n    SELECT\n        sse.system_size_kw,\n        sse.total_system_cost,\n        sse.annual_production_kwh,\n        nma.utility_id,\n        nma.utility_name,\n        nma.state_id,\n        nma.retail_rate,\n        nma.effective_export_rate,\n        nma.net_metering_capacity_limit_kw,\n        -- Annual savings (self-consumption + export)\n        CASE\n            WHEN sse.system_size_kw <= COALESCE(nma.net_metering_capacity_limit_kw, 999999) THEN\n                (sse.annual_production_kwh * 0.7 * nma.retail_rate) +  -- Self-consumed\n                (sse.annual_production_kwh * 0.3 * nma.effective_export_rate)  -- Exported\n            ELSE\n                sse.annual_production_kwh * 0.7 * nma.retail_rate  -- Limited by capacity\n        END AS annual_savings,\n        -- Payback period\n        CASE\n            WHEN (sse.annual_production_kwh * 0.7 * nma.retail_rate) > 0 THEN\n                sse.total_system_cost / (sse.annual_production_kwh * 0.7 * nma.retail_rate)\n            ELSE NULL\n        END AS payback_period_years\n    FROM solar_system_economics sse\n    CROSS JOIN net_metering_analysis nma\n),\nrebate_adjusted_economics AS (\n    -- Fourth CTE: Adjust for rebates\n    SELECT\n        sec.*,\n        COALESCE(sra.total_combined_incentives_usd, 0) AS total_rebates,\n        sec.total_system_cost - COALESCE(sra.total_combined_incentives_usd, 0) AS net_system_cost,\n        CASE\n            WHEN sec.annual_savings > 0 THEN\n                (sec.total_system_cost - COALESCE(sra.total_combined_incentives_usd, 0)) / sec.annual_savings\n            ELSE NULL\n        END AS rebate_adjusted_payback_years\n    FROM solar_economics_calculations sec\n    LEFT JOIN solar_rebate_aggregations sra ON sec.state_id = sra.state_id AND sec.utility_id = sra.utility_id\n),\nfinal_economics_analysis AS (\n    -- Fifth CTE: Final economics analysis\n    SELECT\n        rae.*,\n        ROUND(CAST(rae.annual_savings AS NUMERIC), 2) AS annual_savings,\n        ROUND(CAST(rae.payback_period_years AS NUMERIC), 2) AS payback_period_years,\n        ROUND(CAST(rae.total_rebates AS NUMERIC), 2) AS total_rebates,\n        ROUND(CAST(rae.net_system_cost AS NUMERIC), 2) AS net_system_cost,\n        ROUND(CAST(rae.rebate_adjusted_payback_years AS NUMERIC), 2) AS rebate_adjusted_payback_years,\n        -- Investment classification\n        CASE\n            WHEN rae.rebate_adjusted_payback_years <= 5 THEN 'Excellent Investment'\n            WHEN rae.rebate_adjusted_payback_years <= 8 THEN 'Good Investment'\n            WHEN rae.rebate_adjusted_payback_years <= 12 THEN 'Moderate Investment'\n            ELSE 'Long-Term Investment'\n        END AS investment_classification\n    FROM rebate_adjusted_economics rae\n)\nSELECT\n    system_size_kw, utility_id, utility_name, state_id,\n    ROUND(CAST(total_system_cost AS NUMERIC), 2) AS total_system_cost,\n    annual_production_kwh, retail_rate, effective_export_rate,\n    annual_savings, payback_period_years, total_rebates, net_system_cost,\n    rebate_adjusted_payback_years, investment_classification\nFROM final_economics_analysis\nORDER BY state_id, rebate_adjusted_payback_years;",
  "evidence": "The query joins solar installation records with consumption data, rebate payments, utility rates, and net metering credits. It groups by installation and time periods to calculate metrics including total installation cost, rebate amounts received, energy produced, energy consumed, net metering credits earned, and grid electricity costs avoided. Window functions compute cumulative financial flows and identify payback periods.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "utility_incentives",
    "utility_companies",
    "electricity_rates",
    "solar_system_economics",
    "net_metering_analysis",
    "solar_economics_calculations",
    "solar_rebate_aggregations",
    "rebate_adjusted_economics",
    "final_economics_analysis"
  ],
  "schema_context": {},
  "expected_output": "Solar installation economics with net metering analysis and financial modeling.",
  "normal_query": "Analyze solar installation economics with net metering impact and comprehensive financial modeling."
}
```


### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 15,
  "question": "Can you analyze the volatility of our electricity rates and provide risk assessment metrics?",
  "SQL": "WITH historical_rate_volatility AS (\n    -- First CTE: Calculate historical rate volatility\n    SELECT\n        her.utility_id,\n        her.rate_code_id,\n        her.state_id,\n        DATE_TRUNC('month', her.effective_date) AS rate_month,\n        AVG(her.energy_charge_usd_per_kwh) AS monthly_avg_rate,\n        STDDEV(her.energy_charge_usd_per_kwh) AS monthly_stddev_rate,\n        MIN(her.energy_charge_usd_per_kwh) AS monthly_min_rate,\n        MAX(her.energy_charge_usd_per_kwh) AS monthly_max_rate\n    FROM historical_electricity_rates her\n    WHERE her.effective_date >= CURRENT_DATE - INTERVAL '3 years'\n    GROUP BY her.utility_id, her.rate_code_id, her.state_id, DATE_TRUNC('month', her.effective_date)\n),\nvolatility_metrics AS (\n    -- Second CTE: Calculate volatility metrics\n    SELECT\n        hrv.utility_id,\n        hrv.rate_code_id,\n        hrv.state_id,\n        COUNT(*) AS months_analyzed,\n        AVG(hrv.monthly_avg_rate) AS avg_rate_3yr,\n        STDDEV(hrv.monthly_avg_rate) AS rate_volatility,\n        AVG(hrv.monthly_stddev_rate) AS avg_monthly_stddev,\n        MIN(hrv.monthly_min_rate) AS min_rate_3yr,\n        MAX(hrv.monthly_max_rate) AS max_rate_3yr,\n        MAX(hrv.monthly_max_rate) - MIN(hrv.monthly_min_rate) AS rate_range_3yr,\n        -- Coefficient of variation\n        CASE\n            WHEN AVG(hrv.monthly_avg_rate) > 0 THEN\n                (STDDEV(hrv.monthly_avg_rate) / AVG(hrv.monthly_avg_rate)) * 100\n            ELSE NULL\n        END AS coefficient_of_variation\n    FROM historical_rate_volatility hrv\n    GROUP BY hrv.utility_id, hrv.rate_code_id, hrv.state_id\n),\nrisk_assessment AS (\n    -- Third CTE: Assess risk levels\n    SELECT\n        vm.*,\n        uc.utility_name,\n        rc.rate_code,\n        s.state_name,\n        -- Volatility classification\n        CASE\n            WHEN vm.coefficient_of_variation > 15 THEN 'High Volatility'\n            WHEN vm.coefficient_of_variation > 8 THEN 'Moderate Volatility'\n            WHEN vm.coefficient_of_variation > 3 THEN 'Low Volatility'\n            ELSE 'Very Low Volatility'\n        END AS volatility_classification,\n        -- Risk level\n        CASE\n            WHEN vm.coefficient_of_variation > 15 AND vm.rate_range_3yr > vm.avg_rate_3yr * 0.3 THEN 'High Risk'\n            WHEN vm.coefficient_of_variation > 8 OR vm.rate_range_3yr > vm.avg_rate_3yr * 0.2 THEN 'Moderate Risk'\n            ELSE 'Low Risk'\n        END AS risk_level,\n        -- Window functions for comparison\n        AVG(vm.coefficient_of_variation) OVER (PARTITION BY vm.state_id) AS state_avg_volatility,\n        PERCENT_RANK() OVER (PARTITION BY vm.state_id ORDER BY vm.coefficient_of_variation) AS state_volatility_percentile\n    FROM volatility_metrics vm\n    INNER JOIN utility_companies uc ON vm.utility_id = uc.utility_id\n    INNER JOIN rate_codes rc ON vm.rate_code_id = rc.rate_code_id\n    INNER JOIN states s ON vm.state_id = s.state_id\n),\nfinal_volatility_analysis AS (\n    -- Fourth CTE: Final volatility analysis\n    SELECT\n        ra.*,\n        ROUND(CAST(ra.avg_rate_3yr AS NUMERIC), 6) AS avg_rate_3yr,\n        ROUND(CAST(ra.rate_volatility AS NUMERIC), 6) AS rate_volatility,\n        ROUND(CAST(ra.coefficient_of_variation AS NUMERIC), 2) AS coefficient_of_variation,\n        ROUND(CAST(ra.rate_range_3yr AS NUMERIC), 6) AS rate_range_3yr,\n        ROUND(CAST(ra.state_avg_volatility AS NUMERIC), 2) AS state_avg_volatility,\n        ROUND(CAST(ra.state_volatility_percentile * 100 AS NUMERIC), 2) AS state_volatility_percentile\n    FROM risk_assessment ra\n)\nSELECT\n    utility_id, utility_name, rate_code_id, rate_code, state_id, state_name,\n    months_analyzed, avg_rate_3yr, rate_volatility, coefficient_of_variation,\n    min_rate_3yr, max_rate_3yr, rate_range_3yr,\n    volatility_classification, risk_level, state_avg_volatility, state_volatility_percentile\nFROM final_volatility_analysis\nORDER BY coefficient_of_variation DESC, state_name;",
  "evidence": "The query analyzes historical rate data grouped by rate code and time periods. It computes volatility metrics including standard deviation, coefficient of variation, rate change frequency, and maximum single-period changes. Window functions calculate rolling volatility measures and compare current volatility to historical baselines. Statistical tests identify significant volatility.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "historical_electricity_rates",
    "historical_rate_volatility",
    "volatility_metrics",
    "utility_companies",
    "rate_codes",
    "states",
    "risk_assessment",
    "final_volatility_analysis"
  ],
  "schema_context": {},
  "expected_output": "Rate volatility analysis with risk assessment metrics and risk classifications.",
  "normal_query": "Analyze rate volatility patterns with comprehensive risk assessment metrics and risk classification framework."
}
```


### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 16,
  "question": "Can you show me a market segmentation analysis that breaks down the distribution of rate types across different customer segments?",
  "SQL": "WITH rate_type_distribution AS (\n    SELECT\n        er.rate_type,\n        er.state_id,\n        s.state_name,\n        s.region,\n        COUNT(DISTINCT er.rate_id) AS rate_count,\n        COUNT(DISTINCT er.utility_id) AS utility_count,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS median_rate\n    FROM electricity_rates er\n    INNER JOIN states s ON er.state_id = s.state_id\n    WHERE er.is_current = TRUE\n    GROUP BY er.rate_type, er.state_id, s.state_name, s.region\n),\nmarket_segmentation AS (\n    SELECT\n        rtd.*,\n        SUM(rtd.rate_count) OVER (PARTITION BY rtd.state_id) AS total_rates_in_state,\n        SUM(rtd.rate_count) OVER (PARTITION BY rtd.region) AS total_rates_in_region,\n        (rtd.rate_count::NUMERIC / SUM(rtd.rate_count) OVER (PARTITION BY rtd.state_id)) * 100 AS state_market_share,\n        (rtd.rate_count::NUMERIC / SUM(rtd.rate_count) OVER (PARTITION BY rtd.region)) * 100 AS region_market_share\n    FROM rate_type_distribution rtd\n)\nSELECT\n    rate_type, state_id, state_name, region,\n    rate_count, utility_count,\n    ROUND(CAST(avg_rate AS NUMERIC), 6) AS avg_rate,\n    ROUND(CAST(median_rate AS NUMERIC), 6) AS median_rate,\n    total_rates_in_state, total_rates_in_region,\n    ROUND(CAST(state_market_share AS NUMERIC), 2) AS state_market_share,\n    ROUND(CAST(region_market_share AS NUMERIC), 2) AS region_market_share\nFROM market_segmentation\nORDER BY state_name, rate_type;",
  "evidence": "The query joins rebate, installation, and consumption tables, groups customers by rate type and demographic segments, computes aggregate counts and percentages for each segment, calculates quartile distributions to identify concentration patterns, and uses window functions to compare segment performance metrics against overall averages. Handles NULL values in optional fields and filters for active rate codes.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "electricity_rates",
    "states",
    "rate_type_distribution",
    "market_segmentation"
  ],
  "schema_context": {},
  "expected_output": "Market segmentation analysis with rate type distributions and customer segment metrics.",
  "normal_query": "Provide market segmentation analysis showing rate type distributions and customer segment metrics."
}
```


### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 17,
  "question": "Can you provide a cross-utility rate comparison that shows our competitive positioning against other utilities?",
  "SQL": "WITH utility_rate_comparison AS (\n    SELECT\n        er1.utility_id AS utility_1_id,\n        uc1.utility_name AS utility_1_name,\n        er1.state_id,\n        er1.rate_code_id,\n        er1.energy_charge_usd_per_kwh AS utility_1_rate,\n        er2.utility_id AS utility_2_id,\n        uc2.utility_name AS utility_2_name,\n        er2.energy_charge_usd_per_kwh AS utility_2_rate,\n        er1.energy_charge_usd_per_kwh - er2.energy_charge_usd_per_kwh AS rate_difference,\n        CASE\n            WHEN er2.energy_charge_usd_per_kwh > 0 THEN\n                ((er1.energy_charge_usd_per_kwh - er2.energy_charge_usd_per_kwh) / er2.energy_charge_usd_per_kwh) * 100\n            ELSE NULL\n        END AS rate_difference_percentage\n    FROM electricity_rates er1\n    INNER JOIN utility_companies uc1 ON er1.utility_id = uc1.utility_id\n    INNER JOIN electricity_rates er2 ON er1.state_id = er2.state_id AND er1.rate_code_id = er2.rate_code_id\n    INNER JOIN utility_companies uc2 ON er2.utility_id = uc2.utility_id\n    WHERE er1.is_current = TRUE AND er2.is_current = TRUE\n        AND er1.utility_id < er2.utility_id\n),\ncompetitive_positioning AS (\n    SELECT\n        urc.*,\n        CASE\n            WHEN urc.rate_difference < -0.01 THEN 'More Competitive'\n            WHEN urc.rate_difference > 0.01 THEN 'Less Competitive'\n            ELSE 'Similar'\n        END AS competitive_position\n    FROM utility_rate_comparison urc\n)\nSELECT\n    utility_1_id, utility_1_name, utility_2_id, utility_2_name,\n    state_id, rate_code_id,\n    ROUND(CAST(utility_1_rate AS NUMERIC), 6) AS utility_1_rate,\n    ROUND(CAST(utility_2_rate AS NUMERIC), 6) AS utility_2_rate,\n    ROUND(CAST(rate_difference AS NUMERIC), 6) AS rate_difference,\n    ROUND(CAST(rate_difference_percentage AS NUMERIC), 2) AS rate_difference_percentage,\n    competitive_position\nFROM competitive_positioning\nORDER BY state_id, ABS(rate_difference) DESC;",
  "evidence": "The query joins utility rate tables across multiple providers, groups rates by utility and rate type, computes average and median rates for each utility, calculates percentile rankings to determine competitive positioning, uses window functions to compute rolling averages and year-over-year rate changes, and applies benchmarking calculations to show how each utility's rates compare to market averages.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "electricity_rates",
    "utility_companies",
    "utility_rate_comparison",
    "competitive_positioning"
  ],
  "schema_context": {},
  "expected_output": "Cross-utility rate comparison with competitive positioning and benchmarking.",
  "normal_query": "Generate cross-utility rate comparison analysis with competitive positioning and benchmarking metrics."
}
```


### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 18,
  "question": "Can you show me how to optimize rebate stacking to calculate the maximum possible savings for customers?",
  "SQL": "WITH rebate_combinations AS (\n    SELECT\n        sra.state_id,\n        sra.utility_id,\n        sra.zip_code,\n        sra.total_federal_incentives_usd,\n        sra.total_state_incentives_usd,\n        sra.total_utility_incentives_usd,\n        sra.total_combined_incentives_usd,\n        sra.federal_incentive_count,\n        sra.state_incentive_count,\n        sra.utility_incentive_count\n    FROM solar_rebate_aggregations sra\n    WHERE sra.calculation_date >= CURRENT_DATE - INTERVAL '90 days'\n),\nsystem_scenarios AS (\n    SELECT system_size_kw, system_cost_per_watt\n    FROM (VALUES (5.0, 3.0), (10.0, 3.0), (20.0, 2.8)) AS scenarios(system_size_kw, system_cost_per_watt)\n),\nmaximum_savings_calculation AS (\n    SELECT\n        rc.*,\n        ss.system_size_kw,\n        ss.system_cost_per_watt,\n        ss.system_size_kw * ss.system_cost_per_watt * 1000 AS system_cost,\n        rc.total_combined_incentives_usd AS total_rebates,\n        (ss.system_size_kw * ss.system_cost_per_watt * 1000) - rc.total_combined_incentives_usd AS net_cost,\n        (rc.total_combined_incentives_usd / (ss.system_size_kw * ss.system_cost_per_watt * 1000)) * 100 AS rebate_percentage\n    FROM rebate_combinations rc\n    CROSS JOIN system_scenarios ss\n)\nSELECT\n    state_id, utility_id, zip_code, system_size_kw,\n    ROUND(CAST(system_cost AS NUMERIC), 2) AS system_cost,\n    ROUND(CAST(total_rebates AS NUMERIC), 2) AS total_rebates,\n    ROUND(CAST(net_cost AS NUMERIC), 2) AS net_cost,\n    ROUND(CAST(rebate_percentage AS NUMERIC), 2) AS rebate_percentage,\n    federal_incentive_count, state_incentive_count, utility_incentive_count\nFROM maximum_savings_calculation\nORDER BY rebate_percentage DESC, state_id;",
  "evidence": "The query identifies all active rebate programs, cross-references customer eligibility criteria across multiple rebate tables, groups rebates by customer and installation type, computes total savings for each valid rebate combination while respecting stacking restrictions, uses window functions to rank combinations by total savings amount, and aggregates the maximum possible savings per customer.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "solar_rebate_aggregations",
    "rebate_combinations",
    "system_scenarios",
    "maximum_savings_calculation"
  ],
  "schema_context": {},
  "expected_output": "Rebate stacking optimization with maximum savings calculations.",
  "normal_query": "Analyze rebate stacking optimization to identify maximum savings calculations for eligible customers."
}
```


### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 19,
  "question": "Can you analyze the adoption rates of different electricity rate codes and show market penetration across utilities?",
  "SQL": "WITH rate_code_adoption AS (\n    SELECT\n        rc.rate_code_id,\n        rc.rate_code,\n        er.state_id,\n        COUNT(DISTINCT er.utility_id) AS utilities_adopting,\n        COUNT(DISTINCT er.rate_id) AS total_rates\n    FROM rate_codes rc\n    INNER JOIN electricity_rates er ON rc.rate_code_id = er.rate_code_id\n    WHERE er.is_current = TRUE\n    GROUP BY rc.rate_code_id, rc.rate_code, er.state_id\n),\nmarket_penetration AS (\n    SELECT\n        rca.*,\n        (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = rca.state_id AND is_active = TRUE) AS total_utilities_in_state,\n        CASE\n            WHEN (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = rca.state_id AND is_active = TRUE) > 0 THEN\n                (rca.utilities_adopting::NUMERIC / (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = rca.state_id AND is_active = TRUE)) * 100\n            ELSE 0\n        END AS market_penetration_percentage\n    FROM rate_code_adoption rca\n)\nSELECT\n    rate_code_id, rate_code, state_id,\n    utilities_adopting, total_utilities_in_state,\n    ROUND(CAST(market_penetration_percentage AS NUMERIC), 2) AS market_penetration_percentage,\n    total_rates\nFROM market_penetration\nORDER BY state_id, market_penetration_percentage DESC;",
  "evidence": "The query joins customer enrollment records with rate code definitions across utilities, groups customers by rate code type and utility, calculates adoption rates as the percentage of eligible customers enrolled in each rate code, computes market penetration by comparing current enrollments to total addressable customer base, and uses window functions to track adoption trends over time.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "rate_codes",
    "electricity_rates",
    "utility_companies",
    "rate_code_adoption",
    "market_penetration"
  ],
  "schema_context": {},
  "expected_output": "Rate code adoption analysis with market penetration metrics.",
  "normal_query": "Perform rate code adoption analysis with market penetration metrics across utility service areas."
}
```


### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 20,
  "question": "Can you provide a geographic analysis of rebate programs with state-level aggregations and performance metrics?",
  "SQL": "WITH state_rebate_aggregations AS (\n    SELECT\n        sra.state_id,\n        s.state_name,\n        s.region,\n        SUM(sra.total_federal_incentives_usd) AS state_total_federal,\n        SUM(sra.total_state_incentives_usd) AS state_total_state,\n        SUM(sra.total_utility_incentives_usd) AS state_total_utility,\n        SUM(sra.total_combined_incentives_usd) AS state_total_combined,\n        AVG(sra.total_combined_incentives_usd) AS state_avg_combined,\n        COUNT(*) AS location_count\n    FROM solar_rebate_aggregations sra\n    INNER JOIN states s ON sra.state_id = s.state_id\n    GROUP BY sra.state_id, s.state_name, s.region\n),\nregional_rebate_analysis AS (\n    SELECT\n        sra.*,\n        AVG(sra.state_total_combined) OVER (PARTITION BY sra.region) AS region_avg_total,\n        PERCENT_RANK() OVER (ORDER BY sra.state_total_combined DESC) AS national_percentile\n    FROM state_rebate_aggregations sra\n)\nSELECT\n    state_id, state_name, region,\n    ROUND(CAST(state_total_federal AS NUMERIC), 2) AS state_total_federal,\n    ROUND(CAST(state_total_state AS NUMERIC), 2) AS state_total_state,\n    ROUND(CAST(state_total_utility AS NUMERIC), 2) AS state_total_utility,\n    ROUND(CAST(state_total_combined AS NUMERIC), 2) AS state_total_combined,\n    ROUND(CAST(state_avg_combined AS NUMERIC), 2) AS state_avg_combined,\n    location_count,\n    ROUND(CAST(region_avg_total AS NUMERIC), 2) AS region_avg_total,\n    ROUND(CAST(national_percentile * 100 AS NUMERIC), 2) AS national_percentile\nFROM regional_rebate_analysis\nORDER BY state_total_combined DESC;",
  "evidence": "The query joins rebate applications with customer location data, groups rebates by state and utility service territory, computes aggregate metrics including total rebate amounts, application counts, approval rates, and average rebate values per state, calculates quartile distributions to identify high and low performing regions, and uses window functions to rank states by program performance.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "solar_rebate_aggregations",
    "states",
    "state_rebate_aggregations",
    "regional_rebate_analysis"
  ],
  "schema_context": {},
  "expected_output": "Geographic rebate intelligence with state-level aggregations.",
  "normal_query": "Generate geographic rebate intelligence with state-level aggregations and regional performance analysis."
}
```


### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 21,
  "question": "Can you show me the rate trend forecasting using predictive analytics?",
  "SQL": "WITH historical_rate_trends AS (\n    SELECT\n        her.utility_id,\n        her.rate_code_id,\n        her.state_id,\n        DATE_TRUNC('month', her.effective_date) AS rate_month,\n        AVG(her.energy_charge_usd_per_kwh) AS monthly_avg_rate\n    FROM historical_electricity_rates her\n    WHERE her.effective_date >= CURRENT_DATE - INTERVAL '3 years'\n    GROUP BY her.utility_id, her.rate_code_id, her.state_id, DATE_TRUNC('month', her.effective_date)\n),\ntrend_calculation AS (\n    SELECT\n        hrt.*,\n        LAG(hrt.monthly_avg_rate, 1) OVER (PARTITION BY hrt.utility_id, hrt.rate_code_id ORDER BY hrt.rate_month) AS prev_rate,\n        LEAD(hrt.monthly_avg_rate, 1) OVER (PARTITION BY hrt.utility_id, hrt.rate_code_id ORDER BY hrt.rate_month) AS next_rate,\n        AVG(hrt.monthly_avg_rate) OVER (PARTITION BY hrt.utility_id, hrt.rate_code_id ORDER BY hrt.rate_month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS moving_avg_12mo\n    FROM historical_rate_trends hrt\n),\nforecast_models AS (\n    SELECT\n        tc.*,\n        tc.monthly_avg_rate - tc.prev_rate AS monthly_change,\n        AVG(tc.monthly_avg_rate - tc.prev_rate) OVER (PARTITION BY tc.utility_id, tc.rate_code_id ORDER BY tc.rate_month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS avg_monthly_change,\n        tc.monthly_avg_rate + (AVG(tc.monthly_avg_rate - tc.prev_rate) OVER (PARTITION BY tc.utility_id, tc.rate_code_id ORDER BY tc.rate_month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) * 6) AS forecast_6mo,\n        tc.monthly_avg_rate + (AVG(tc.monthly_avg_rate - tc.prev_rate) OVER (PARTITION BY tc.utility_id, tc.rate_code_id ORDER BY tc.rate_month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) * 12) AS forecast_12mo\n    FROM trend_calculation tc\n    WHERE tc.prev_rate IS NOT NULL\n)\nSELECT\n    utility_id, rate_code_id, state_id, rate_month,\n    ROUND(CAST(monthly_avg_rate AS NUMERIC), 6) AS monthly_avg_rate,\n    ROUND(CAST(prev_rate AS NUMERIC), 6) AS prev_rate,\n    ROUND(CAST(monthly_change AS NUMERIC), 6) AS monthly_change,\n    ROUND(CAST(avg_monthly_change AS NUMERIC), 6) AS avg_monthly_change,\n    ROUND(CAST(forecast_6mo AS NUMERIC), 6) AS forecast_6mo,\n    ROUND(CAST(forecast_12mo AS NUMERIC), 6) AS forecast_12mo\nFROM forecast_models\nWHERE rate_month >= CURRENT_DATE - INTERVAL '6 months'\nORDER BY utility_id, rate_code_id, rate_month DESC;",
  "evidence": "The query aggregates historical rate data by time periods and rate categories, calculates statistical measures including moving averages and growth rates, applies window functions to compute rolling trends and year-over-year comparisons, and handles NULL values in temporal joins to ensure complete time series coverage.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "historical_electricity_rates",
    "historical_rate_trends",
    "trend_calculation",
    "forecast_models"
  ],
  "schema_context": {},
  "expected_output": "Rate trend forecasting with predictive analytics and trend predictions.",
  "normal_query": "Show rate trend forecasting with predictive analytics and future trend predictions."
}
```


### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 22,
  "question": "Can you show me the utility rate strategy analysis with recommendations for rate code portfolio optimization?",
  "SQL": "WITH utility_portfolio_analysis AS (\n    SELECT\n        uc.utility_id,\n        uc.utility_name,\n        uc.state_id,\n        COUNT(DISTINCT er.rate_code_id) AS rate_codes_offered,\n        COUNT(DISTINCT er.rate_id) AS total_rates,\n        AVG(er.energy_charge_usd_per_kwh) AS portfolio_avg_rate,\n        STDDEV(er.energy_charge_usd_per_kwh) AS portfolio_rate_stddev\n    FROM utility_companies uc\n    INNER JOIN electricity_rates er ON uc.utility_id = er.utility_id\n    WHERE er.is_current = TRUE\n    GROUP BY uc.utility_id, uc.utility_name, uc.state_id\n),\nportfolio_optimization AS (\n    SELECT\n        upa.*,\n        CASE\n            WHEN upa.rate_codes_offered >= 5 AND upa.portfolio_rate_stddev > upa.portfolio_avg_rate * 0.1 THEN 'Well Diversified'\n            WHEN upa.rate_codes_offered >= 3 THEN 'Moderately Diversified'\n            ELSE 'Limited Diversification'\n        END AS diversification_status,\n        CASE\n            WHEN upa.rate_codes_offered < 3 THEN 'Consider Adding Rate Codes'\n            WHEN upa.portfolio_rate_stddev < upa.portfolio_avg_rate * 0.05 THEN 'Consider Rate Differentiation'\n            ELSE 'Portfolio Optimized'\n        END AS optimization_recommendation\n    FROM utility_portfolio_analysis upa\n)\nSELECT\n    utility_id, utility_name, state_id,\n    rate_codes_offered, total_rates,\n    ROUND(CAST(portfolio_avg_rate AS NUMERIC), 6) AS portfolio_avg_rate,\n    ROUND(CAST(portfolio_rate_stddev AS NUMERIC), 6) AS portfolio_rate_stddev,\n    diversification_status, optimization_recommendation\nFROM portfolio_optimization\nORDER BY state_id, utility_name;",
  "evidence": "The query groups customers and consumption data by rate code and customer segment, computes aggregate metrics including revenue per customer and penetration rates, uses window functions to rank rate codes by performance indicators and calculate market share within segments, and applies quartile analysis to identify high and low performers while handling edge cases in customer transitions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "utility_companies",
    "electricity_rates",
    "utility_portfolio_analysis",
    "portfolio_optimization"
  ],
  "schema_context": {},
  "expected_output": "Utility rate strategy analysis with portfolio optimization recommendations.",
  "normal_query": "Show utility rate strategy analysis with rate code portfolio optimization recommendations."
}
```


### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 23,
  "question": "Can you show me the solar rebate market analysis including incentive availability trends?",
  "SQL": "WITH incentive_availability AS (\n    SELECT\n        s.state_id,\n        s.state_name,\n        s.region,\n        COUNT(DISTINCT fi.federal_incentive_id) AS federal_incentives_available,\n        COUNT(DISTINCT si.state_incentive_id) AS state_incentives_available,\n        COUNT(DISTINCT ui.utility_incentive_id) AS utility_incentives_available,\n        COUNT(DISTINCT ui.utility_id) AS utilities_with_incentives\n    FROM states s\n    LEFT JOIN federal_incentives fi ON fi.is_active = TRUE AND (fi.expiration_date IS NULL OR fi.expiration_date > CURRENT_DATE)\n    LEFT JOIN state_incentives si ON s.state_id = si.state_id AND si.is_active = TRUE AND (si.expiration_date IS NULL OR si.expiration_date > CURRENT_DATE)\n    LEFT JOIN utility_incentives ui ON s.state_id = ui.state_id AND ui.is_active = TRUE AND (ui.expiration_date IS NULL OR ui.expiration_date > CURRENT_DATE)\n    GROUP BY s.state_id, s.state_name, s.region\n),\nmarket_coverage_analysis AS (\n    SELECT\n        ia.*,\n        (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = ia.state_id AND is_active = TRUE) AS total_utilities_in_state,\n        CASE\n            WHEN (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = ia.state_id AND is_active = TRUE) > 0 THEN\n                (ia.utilities_with_incentives::NUMERIC / (SELECT COUNT(DISTINCT utility_id) FROM utility_companies WHERE state_id = ia.state_id AND is_active = TRUE)) * 100\n            ELSE 0\n        END AS utility_coverage_percentage\n    FROM incentive_availability ia\n)\nSELECT\n    state_id, state_name, region,\n    federal_incentives_available, state_incentives_available, utility_incentives_available,\n    utilities_with_incentives, total_utilities_in_state,\n    ROUND(CAST(utility_coverage_percentage AS NUMERIC), 2) AS utility_coverage_percentage\nFROM market_coverage_analysis\nORDER BY utility_coverage_percentage DESC, state_name;",
  "evidence": "The query aggregates rebate application and installation data by program type, geographic region, and time period, calculates utilization rates and remaining budget allocations, employs window functions to track cumulative redemption patterns and forecast depletion timelines, and handles NULL values in eligibility criteria joins.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "states",
    "federal_incentives",
    "state_incentives",
    "utility_incentives",
    "utility_companies",
    "incentive_availability",
    "market_coverage_analysis"
  ],
  "schema_context": {},
  "expected_output": "Solar rebate market intelligence with incentive availability analysis.",
  "normal_query": "Show solar rebate market intelligence with detailed incentive availability analysis."
}
```


### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 24,
  "question": "Can you show me a cross-regional rate comparison with market share analysis?",
  "SQL": "WITH regional_rate_statistics AS (\n    SELECT\n        s.region,\n        COUNT(DISTINCT er.utility_id) AS utility_count,\n        COUNT(DISTINCT er.rate_id) AS total_rates,\n        AVG(er.energy_charge_usd_per_kwh) AS region_avg_rate,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY er.energy_charge_usd_per_kwh) AS region_median_rate,\n        MIN(er.energy_charge_usd_per_kwh) AS region_min_rate,\n        MAX(er.energy_charge_usd_per_kwh) AS region_max_rate\n    FROM states s\n    INNER JOIN electricity_rates er ON s.state_id = er.state_id\n    WHERE er.is_current = TRUE\n    GROUP BY s.region\n),\nmarket_share_by_region AS (\n    SELECT\n        rrs.*,\n        SUM(rrs.total_rates) OVER () AS national_total_rates,\n        (rrs.total_rates::NUMERIC / SUM(rrs.total_rates) OVER ()) * 100 AS regional_market_share\n    FROM regional_rate_statistics rrs\n)\nSELECT\n    region, utility_count, total_rates,\n    ROUND(CAST(region_avg_rate AS NUMERIC), 6) AS region_avg_rate,\n    ROUND(CAST(region_median_rate AS NUMERIC), 6) AS region_median_rate,\n    ROUND(CAST(region_min_rate AS NUMERIC), 6) AS region_min_rate,\n    ROUND(CAST(region_max_rate AS NUMERIC), 6) AS region_max_rate,\n    national_total_rates,\n    ROUND(CAST(regional_market_share AS NUMERIC), 2) AS regional_market_share\nFROM market_share_by_region\nORDER BY regional_market_share DESC;",
  "evidence": "The query groups rate and customer data by geographic region and rate category, calculates average rates and rate distributions within each region, uses window functions to compute market share percentages and rank regions by competitiveness metrics, and performs comparative analysis across regions while handling differences in rate structure definitions and NULL values in regional boundary assignments.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "states",
    "electricity_rates",
    "regional_rate_statistics",
    "market_share_by_region"
  ],
  "schema_context": {},
  "expected_output": "Cross-regional rate comparison with market share analysis.",
  "normal_query": "Show cross-regional rate comparison with detailed market share analysis."
}
```


### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 25,
  "question": "Can you show me the rate structure performance analysis with cost efficiency metrics?",
  "SQL": "WITH rate_structure_performance AS (\n    SELECT\n        rs.rate_structure_id,\n        rs.utility_id,\n        rs.rate_code_id,\n        er.energy_charge_usd_per_kwh,\n        er.fixed_charge_usd,\n        er.demand_charge_usd_per_kw,\n        COUNT(DISTINCT trt.tier_id) AS tier_count,\n        COUNT(DISTINCT tou.tou_period_id) AS tou_period_count\n    FROM rate_structures rs\n    INNER JOIN electricity_rates er ON rs.rate_structure_id = er.rate_structure_id\n    LEFT JOIN tiered_rate_tiers trt ON rs.rate_structure_id = trt.rate_structure_id\n    LEFT JOIN time_of_use_periods tou ON rs.rate_structure_id = tou.rate_structure_id\n    WHERE rs.is_current = TRUE AND er.is_current = TRUE\n    GROUP BY rs.rate_structure_id, rs.utility_id, rs.rate_code_id, er.energy_charge_usd_per_kwh, er.fixed_charge_usd, er.demand_charge_usd_per_kw\n),\nefficiency_metrics AS (\n    SELECT\n        rsp.*,\n        (rsp.energy_charge_usd_per_kwh * 1000) + COALESCE(rsp.fixed_charge_usd, 0) + COALESCE(rsp.demand_charge_usd_per_kw, 0) AS total_cost_per_1000kwh,\n        CASE\n            WHEN rsp.tier_count > 0 OR rsp.tou_period_count > 0 THEN 'Complex Structure'\n            ELSE 'Simple Structure'\n        END AS structure_complexity\n    FROM rate_structure_performance rsp\n)\nSELECT\n    rate_structure_id, utility_id, rate_code_id,\n    ROUND(CAST(energy_charge_usd_per_kwh AS NUMERIC), 6) AS energy_charge_usd_per_kwh,\n    ROUND(CAST(fixed_charge_usd AS NUMERIC), 2) AS fixed_charge_usd,\n    ROUND(CAST(demand_charge_usd_per_kw AS NUMERIC), 4) AS demand_charge_usd_per_kw,\n    tier_count, tou_period_count,\n    ROUND(CAST(total_cost_per_1000kwh AS NUMERIC), 2) AS total_cost_per_1000kwh,\n    structure_complexity\nFROM efficiency_metrics\nORDER BY total_cost_per_1000kwh;",
  "evidence": "The query groups consumption and billing data by rate structure type and customer characteristics, computes aggregate metrics including revenue yield, cost-to-serve ratios, and customer retention rates, applies window functions to calculate efficiency quartiles and benchmark performance across structures, and handles edge cases such as hybrid rate customers and NULL values in cost allocation joins.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "rate_structures",
    "electricity_rates",
    "tiered_rate_tiers",
    "time_of_use_periods",
    "rate_structure_performance",
    "efficiency_metrics"
  ],
  "schema_context": {},
  "expected_output": "Rate structure performance analysis with cost efficiency metrics.",
  "normal_query": "Show rate structure performance analysis with detailed cost efficiency metrics."
}
```


### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 26,
  "question": "Can you show me a recursive analysis of our rate code hierarchy that traverses multiple levels of the rate structure?",
  "SQL": "WITH RECURSIVE rate_code_hierarchy AS (\n    SELECT\n        rc.rate_code_id AS parent_code_id,\n        rc.rate_code AS parent_code,\n        rc.rate_code_category,\n        rc2.rate_code_id AS child_code_id,\n        rc2.rate_code AS child_code,\n        1 AS hierarchy_level,\n        ARRAY[rc.rate_code_id] AS code_path\n    FROM rate_codes rc\n    INNER JOIN rate_codes rc2 ON rc.rate_code_category = rc2.rate_code_category AND rc.rate_code_id != rc2.rate_code_id\n    WHERE rc.is_active = TRUE AND rc2.is_active = TRUE\n    \n    UNION ALL\n    \n    SELECT\n        rch.parent_code_id,\n        rch.parent_code,\n        rch.rate_code_category,\n        rc3.rate_code_id,\n        rc3.rate_code,\n        rch.hierarchy_level + 1,\n        rch.code_path || ARRAY[rc3.rate_code_id]\n    FROM rate_code_hierarchy rch\n    INNER JOIN rate_codes rc3 ON rch.rate_code_category = rc3.rate_code_category\n    WHERE rch.hierarchy_level < 5\n        AND NOT rc3.rate_code_id = ANY(rch.code_path)\n),\nhierarchy_analysis AS (\n    SELECT\n        rch.*,\n        array_length(rch.code_path, 1) AS path_length,\n        COUNT(*) OVER (PARTITION BY rch.parent_code_id) AS total_children\n    FROM rate_code_hierarchy rch\n)\nSELECT\n    parent_code_id, parent_code, child_code_id, child_code,\n    rate_code_category, hierarchy_level, path_length, total_children\nFROM hierarchy_analysis\nORDER BY parent_code, hierarchy_level;",
  "evidence": "The query uses recursive CTEs to traverse the rate code hierarchy from top-level parent codes down through all descendant levels, joining rebate, installation, and consumption tables as needed. It groups results by rate code level and hierarchy path, computes aggregate metrics at each level including customer counts and usage volumes, and applies window functions to calculate cumulative metrics across the hierarchy.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "rate_codes",
    "rate_code_hierarchy",
    "hierarchy_analysis"
  ],
  "schema_context": {},
  "expected_output": "Recursive rate code hierarchy analysis with multi-level traversal.",
  "normal_query": "Perform recursive rate code hierarchy analysis with multi-level structure traversal."
}
```


### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 27,
  "question": "Can you provide a comprehensive rate analysis dashboard that breaks down rates across multiple dimensions?",
  "SQL": "WITH rate_intelligence_summary AS (\n    SELECT\n        s.state_id,\n        s.state_name,\n        s.region,\n        COUNT(DISTINCT er.utility_id) AS utility_count,\n        COUNT(DISTINCT er.rate_id) AS total_rates,\n        AVG(er.energy_charge_usd_per_kwh) AS avg_rate,\n        MIN(er.energy_charge_usd_per_kwh) AS min_rate,\n        MAX(er.energy_charge_usd_per_kwh) AS max_rate,\n        COUNT(DISTINCT er.rate_type) AS rate_types,\n        COUNT(DISTINCT rc.rate_structure_type) AS structure_types\n    FROM states s\n    INNER JOIN electricity_rates er ON s.state_id = er.state_id\n    INNER JOIN rate_codes rc ON er.rate_code_id = rc.rate_code_id\n    WHERE er.is_current = TRUE\n    GROUP BY s.state_id, s.state_name, s.region\n),\nrebate_intelligence_summary AS (\n    SELECT\n        sra.state_id,\n        SUM(sra.total_combined_incentives_usd) AS total_rebates,\n        AVG(sra.total_combined_incentives_usd) AS avg_rebates,\n        COUNT(*) AS rebate_locations\n    FROM solar_rebate_aggregations sra\n    GROUP BY sra.state_id\n),\ncomprehensive_dashboard AS (\n    SELECT\n        ris.*,\n        COALESCE(rebis.total_rebates, 0) AS total_rebates,\n        COALESCE(rebis.avg_rebates, 0) AS avg_rebates,\n        COALESCE(rebis.rebate_locations, 0) AS rebate_locations,\n        AVG(ris.avg_rate) OVER (PARTITION BY ris.region) AS region_avg_rate,\n        PERCENT_RANK() OVER (ORDER BY ris.avg_rate) AS national_percentile\n    FROM rate_intelligence_summary ris\n    LEFT JOIN rebate_intelligence_summary rebis ON ris.state_id = rebis.state_id\n)\nSELECT\n    state_id, state_name, region,\n    utility_count, total_rates, rate_types, structure_types,\n    ROUND(CAST(avg_rate AS NUMERIC), 6) AS avg_rate,\n    ROUND(CAST(min_rate AS NUMERIC), 6) AS min_rate,\n    ROUND(CAST(max_rate AS NUMERIC), 6) AS max_rate,\n    ROUND(CAST(total_rebates AS NUMERIC), 2) AS total_rebates,\n    ROUND(CAST(avg_rebates AS NUMERIC), 2) AS avg_rebates,\n    rebate_locations,\n    ROUND(CAST(region_avg_rate AS NUMERIC), 6) AS region_avg_rate,\n    ROUND(CAST(national_percentile * 100 AS NUMERIC), 2) AS national_percentile\nFROM comprehensive_dashboard\nORDER BY state_name;",
  "evidence": "The query joins rebate eligibility, solar installation, and consumption data across common keys, then groups by multiple dimensions such as region, customer segment, rate type, and time period. It computes aggregate statistics including average rates, total revenue, customer counts, and usage volumes, calculates quartile distributions to identify rate outliers, and applies window functions to generate cross-dimensional comparisons.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "states",
    "electricity_rates",
    "rate_codes",
    "solar_rebate_aggregations",
    "rate_intelligence_summary",
    "rebate_intelligence_summary",
    "comprehensive_dashboard"
  ],
  "schema_context": {},
  "expected_output": "Comprehensive rate intelligence dashboard with multi-dimensional analysis.",
  "normal_query": "Generate comprehensive rate intelligence dashboard with multi-dimensional breakdown analysis."
}
```


### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 28,
  "question": "Can you show me a competitive analysis of our solar rebate programs and how we position against the market?",
  "SQL": "WITH rebate_competitive_analysis AS (\n    SELECT\n        sra.state_id,\n        s.state_name,\n        s.region,\n        sra.utility_id,\n        uc.utility_name,\n        sra.total_combined_incentives_usd,\n        AVG(sra.total_combined_incentives_usd) OVER (PARTITION BY sra.state_id) AS state_avg_rebates,\n        AVG(sra.total_combined_incentives_usd) OVER (PARTITION BY s.region) AS region_avg_rebates,\n        PERCENT_RANK() OVER (PARTITION BY sra.state_id ORDER BY sra.total_combined_incentives_usd DESC) AS state_rebate_percentile\n    FROM solar_rebate_aggregations sra\n    INNER JOIN states s ON sra.state_id = s.state_id\n    LEFT JOIN utility_companies uc ON sra.utility_id = uc.utility_id\n),\ncompetitive_positioning AS (\n    SELECT\n        rca.*,\n        CASE\n            WHEN rca.total_combined_incentives_usd > rca.state_avg_rebates THEN 'Above State Average'\n            WHEN rca.total_combined_incentives_usd = rca.state_avg_rebates THEN 'At State Average'\n            ELSE 'Below State Average'\n        END AS competitive_position\n    FROM rebate_competitive_analysis rca\n)\nSELECT\n    state_id, state_name, region, utility_id, utility_name,\n    ROUND(CAST(total_combined_incentives_usd AS NUMERIC), 2) AS total_combined_incentives_usd,\n    ROUND(CAST(state_avg_rebates AS NUMERIC), 2) AS state_avg_rebates,\n    ROUND(CAST(region_avg_rebates AS NUMERIC), 2) AS region_avg_rebates,\n    ROUND(CAST(state_rebate_percentile * 100 AS NUMERIC), 2) AS state_rebate_percentile,\n    competitive_position\nFROM competitive_positioning\nORDER BY state_name, total_combined_incentives_usd DESC;",
  "evidence": "The query joins solar installation records with rebate eligibility and consumption data to calculate program performance metrics. It groups by program type, geographic market, and customer segment to enable competitive comparisons, computes aggregate metrics including average rebate amounts, participation rates, installation counts, and cost per watt, and applies window functions to calculate market share and competitive positioning.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "solar_rebate_aggregations",
    "states",
    "utility_companies",
    "rebate_competitive_analysis",
    "competitive_positioning"
  ],
  "schema_context": {},
  "expected_output": "Solar rebate competitive analysis with market positioning intelligence.",
  "normal_query": "Conduct solar rebate competitive analysis with market positioning intelligence assessment."
}
```


### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 29,
  "question": "Can you analyze how our electricity rates cluster geographically and identify regional patterns?",
  "SQL": "WITH geographic_rate_clusters AS (\n    SELECT\n        s.state_id,\n        s.state_name,\n        s.region,\n        AVG(er.energy_charge_usd_per_kwh) AS state_avg_rate,\n        COUNT(DISTINCT er.utility_id) AS utility_count,\n        COUNT(DISTINCT er.rate_id) AS rate_count\n    FROM states s\n    INNER JOIN electricity_rates er ON s.state_id = er.state_id\n    WHERE er.is_current = TRUE\n    GROUP BY s.state_id, s.state_name, s.region\n),\ncluster_identification AS (\n    SELECT\n        grc.*,\n        AVG(grc.state_avg_rate) OVER (PARTITION BY grc.region) AS region_cluster_avg,\n        CASE\n            WHEN grc.state_avg_rate <= AVG(grc.state_avg_rate) OVER (PARTITION BY grc.region) * 0.9 THEN 'Low Cost Cluster'\n            WHEN grc.state_avg_rate >= AVG(grc.state_avg_rate) OVER (PARTITION BY grc.region) * 1.1 THEN 'High Cost Cluster'\n            ELSE 'Average Cost Cluster'\n        END AS cluster_classification\n    FROM geographic_rate_clusters grc\n)\nSELECT\n    state_id, state_name, region,\n    ROUND(CAST(state_avg_rate AS NUMERIC), 6) AS state_avg_rate,\n    utility_count, rate_count,\n    ROUND(CAST(region_cluster_avg AS NUMERIC), 6) AS region_cluster_avg,\n    cluster_classification\nFROM cluster_identification\nORDER BY region, state_avg_rate;",
  "evidence": "The query aggregates rebate, installation, and consumption data by geographic dimensions such as zip code, county, and service region. It groups by geographic hierarchies to analyze rate distributions at multiple geographic scales, computes statistical aggregates including average rates, rate variance, customer density, and consumption intensity by region, and applies window functions to calculate regional rankings and clustering metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "states",
    "electricity_rates",
    "geographic_rate_clusters",
    "cluster_identification"
  ],
  "schema_context": {},
  "expected_output": "Geographic rate clustering analysis with regional pattern identification.",
  "normal_query": "Perform geographic rate clustering analysis with regional pattern identification."
}
```


### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-15",
  "question_id": 30,
  "question": "Can you provide an enterprise-level rate optimization platform with comprehensive cost analysis capabilities?",
  "SQL": "WITH comprehensive_rate_analysis AS (\n    SELECT\n        er.rate_id,\n        er.utility_id,\n        uc.utility_name,\n        er.state_id,\n        s.state_name,\n        er.rate_code_id,\n        rc.rate_code,\n        er.rate_type,\n        er.energy_charge_usd_per_kwh,\n        er.fixed_charge_usd,\n        er.demand_charge_usd_per_kw,\n        AVG(er.energy_charge_usd_per_kwh) OVER (PARTITION BY er.state_id, er.rate_type) AS state_avg_rate,\n        AVG(er.energy_charge_usd_per_kwh) OVER (PARTITION BY er.utility_id) AS utility_avg_rate\n    FROM electricity_rates er\n    INNER JOIN utility_companies uc ON er.utility_id = uc.utility_id\n    INNER JOIN states s ON er.state_id = s.state_id\n    INNER JOIN rate_codes rc ON er.rate_code_id = rc.rate_code_id\n    WHERE er.is_current = TRUE\n),\ncost_optimization_scenarios AS (\n    SELECT\n        cra.*,\n        -- Scenario: 1000 kWh/month usage\n        (cra.energy_charge_usd_per_kwh * 1000) + COALESCE(cra.fixed_charge_usd, 0) AS monthly_cost_1000kwh,\n        -- Scenario: 2000 kWh/month usage\n        (cra.energy_charge_usd_per_kwh * 2000) + COALESCE(cra.fixed_charge_usd, 0) AS monthly_cost_2000kwh,\n        -- Cost competitiveness\n        CASE\n            WHEN cra.energy_charge_usd_per_kwh < cra.state_avg_rate THEN 'More Competitive'\n            WHEN cra.energy_charge_usd_per_kwh > cra.state_avg_rate THEN 'Less Competitive'\n            ELSE 'Average'\n        END AS competitiveness\n    FROM comprehensive_rate_analysis cra\n),\noptimization_recommendations AS (\n    SELECT\n        cos.*,\n        ROUND(CAST(cos.monthly_cost_1000kwh AS NUMERIC), 2) AS monthly_cost_1000kwh,\n        ROUND(CAST(cos.monthly_cost_2000kwh AS NUMERIC), 2) AS monthly_cost_2000kwh,\n        CASE\n            WHEN cos.competitiveness = 'More Competitive' THEN 'Optimal Rate'\n            WHEN cos.competitiveness = 'Less Competitive' THEN 'Consider Alternative Rates'\n            ELSE 'Evaluate Further'\n        END AS optimization_recommendation\n    FROM cost_optimization_scenarios cos\n)\nSELECT\n    rate_id, utility_id, utility_name, state_id, state_name,\n    rate_code_id, rate_code, rate_type,\n    ROUND(CAST(energy_charge_usd_per_kwh AS NUMERIC), 6) AS energy_charge_usd_per_kwh,\n    ROUND(CAST(fixed_charge_usd AS NUMERIC), 2) AS fixed_charge_usd,\n    ROUND(CAST(state_avg_rate AS NUMERIC), 6) AS state_avg_rate,\n    monthly_cost_1000kwh, monthly_cost_2000kwh,\n    competitiveness, optimization_recommendation\nFROM optimization_recommendations\nORDER BY state_name, monthly_cost_1000kwh;",
  "evidence": "The query integrates data from rebate eligibility, solar installations, and consumption systems through comprehensive joins on customer and time dimensions. It groups by enterprise-relevant dimensions including customer segment, product line, geography, and time period to enable strategic analysis, computes aggregate metrics across dimensions, and applies window functions for cross-dimensional comparisons and trend analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "electricity_rates",
    "utility_companies",
    "states",
    "rate_codes",
    "comprehensive_rate_analysis",
    "cost_optimization_scenarios",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Enterprise rate optimization platform with comprehensive cost intelligence.",
  "normal_query": "Deploy enterprise rate optimization platform with comprehensive cost intelligence and analysis."
}
```

