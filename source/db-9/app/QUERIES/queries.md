# Shipping Intelligence Database — Query Documentation

## Database Overview

```yaml
db_id: db-9
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
This database supports analytics for db-9.
```

## Use Case

```text
Target use cases for db-9: analytics, reporting, dashboards.
```

## Business Value

```text
Business value for db-9.
```

## Schema

```sql
-- PostgreSQL-specific schema file
-- Generated from schema.sql
-- Generated: 2026-02-05 19:10:05
-- Database: db-9
-- 
-- This file contains PostgreSQL-specific SQL syntax.
-- Use this file when setting up the database in PostgreSQL.
--

-- Shipping Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for shipping and rate comparison system

-- Shipping Carriers Table
-- Stores carrier information (USPS, UPS, FedEx, etc.)
CREATE TABLE shipping_carriers (
    carrier_id VARCHAR(50) PRIMARY KEY,
    carrier_name VARCHAR(100) NOT NULL,
    carrier_code VARCHAR(10) NOT NULL UNIQUE,  -- 'USPS', 'UPS', 'FEDEX'
    carrier_type VARCHAR(50),  -- 'Postal', 'Courier', 'Freight'
    api_endpoint VARCHAR(500),
    rate_api_version VARCHAR(50),
    tracking_api_version VARCHAR(50),
    commercial_pricing_available BOOLEAN DEFAULT FALSE,
    requires_account BOOLEAN DEFAULT FALSE,
    active_status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Shipping Zones Table
-- Stores zone information for rate calculations (USPS zones, UPS zones)
CREATE TABLE shipping_zones (
    zone_id VARCHAR(255) PRIMARY KEY,
    carrier_id VARCHAR(50) NOT NULL,
    origin_zip_code VARCHAR(10) NOT NULL,
    destination_zip_code VARCHAR(10) NOT NULL,
    zone_number INTEGER NOT NULL,
    zone_type VARCHAR(50),  -- 'Domestic', 'International', 'Alaska', 'Hawaii'
    distance_miles NUMERIC(10, 2),
    transit_days_min INTEGER,
    transit_days_max INTEGER,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (carrier_id) REFERENCES shipping_carriers(carrier_id)
);

-- Shipping Service Types Table
-- Stores available service types (Priority Mail, Ground, Express, etc.)
CREATE TABLE shipping_service_types (
    service_id VARCHAR(255) PRIMARY KEY,
    carrier_id VARCHAR(50) NOT NULL,
    service_code VA
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
  "db_id": "db-9",
  "question_id": 1,
  "question": "Can you show me a multi-carrier rate comparison that includes zone analysis and identifies cost optimization opportunities?",
  "SQL": "WITH package_dimensions AS (\n    -- First CTE: Calculate package dimensions and dimensional weight\n    SELECT\n        p.package_id,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches,\n        p.length_inches * p.width_inches * p.height_inches AS cubic_volume_cubic_inches,\n        CASE\n            WHEN p.length_inches * p.width_inches * p.height_inches / 166.0 > p.weight_lbs\n            THEN p.length_inches * p.width_inches * p.height_inches / 166.0\n            ELSE p.weight_lbs\n        END AS billable_weight_lbs,\n        p.package_type\n    FROM packages p\n    WHERE p.package_id = 'PACKAGE_ID_PLACEHOLDER'\n),\nzone_lookup AS (\n    -- Second CTE: Determine shipping zones for origin and destination\n    SELECT DISTINCT\n        z.zone_id,\n        z.carrier_id,\n        z.origin_zip_code,\n        z.destination_zip_code,\n        z.zone_number,\n        z.zone_type,\n        z.transit_days_min,\n        z.transit_days_max,\n        z.effective_date,\n        z.expiration_date\n    FROM shipping_zones z\n    WHERE z.origin_zip_code = 'ORIGIN_ZIP_PLACEHOLDER'\n        AND z.destination_zip_code = 'DEST_ZIP_PLACEHOLDER'\n        AND (z.expiration_date IS NULL OR z.expiration_date >= CURRENT_DATE)\n        AND z.effective_date <= CURRENT_DATE\n),\ncarrier_service_options AS (\n    -- Third CTE: Get all available carrier service combinations\n    SELECT DISTINCT\n        c.carrier_id,\n        c.carrier_name,\n        c.carrier_code,\n        st.service_id,\n        st.service_code,\n        st.service_name,\n        st.service_category,\n        st.max_weight_lbs,\n        st.domestic_available,\n        st.tracking_included,\n        z.zone_number,\n        z.transit_days_min,\n        z.transit_days_max\n    FROM shipping_carriers c\n    CROSS JOIN shipping_service_types st\n    LEFT JOIN zone_lookup z ON c.carrier_id = z.carrier_id\n    WHERE c.active_status = TRUE\n        AND st.active_status = TRUE\n        AND st.domestic_available = TRUE\n),\nrate_calculations AS (\n    -- Fourth CTE: Calculate rates for each carrier/service combination\n    SELECT\n        cso.carrier_id,\n        cso.carrier_name,\n        cso.carrier_code,\n        cso.service_id,\n        cso.service_code,\n        cso.service_name,\n        cso.service_category,\n        cso.zone_number,\n        cso.transit_days_min,\n        cso.transit_days_max,\n        pd.billable_weight_lbs,\n        pd.package_id,\n        COALESCE(\n            (SELECT MIN(sr.total_rate)\n             FROM shipping_rates sr\n             WHERE sr.carrier_id = cso.carrier_id\n                 AND sr.service_id = cso.service_id\n                 AND sr.weight_lbs >= pd.billable_weight_lbs\n                 AND (sr.expiration_date IS NULL OR sr.expiration_date >= CURRENT_DATE)\n                 AND sr.effective_date <= CURRENT_DATE\n             LIMIT 1),\n            999999.99\n        ) AS calculated_rate,\n        CASE\n            WHEN cso.max_weight_lbs IS NOT NULL AND pd.billable_weight_lbs > cso.max_weight_lbs\n            THEN FALSE\n            ELSE TRUE\n        END AS weight_compatible\n    FROM carrier_service_options cso\n    CROSS JOIN package_dimensions pd\n),\nrate_rankings AS (\n    -- Fifth CTE: Rank rates and identify cheapest/fastest options\n    SELECT\n        rc.carrier_id,\n        rc.carrier_name,\n        rc.carrier_code,\n        rc.service_id,\n        rc.service_code,\n        rc.service_name,\n        rc.service_category,\n        rc.zone_number,\n        rc.transit_days_min,\n        rc.transit_days_max,\n        rc.calculated_rate,\n        rc.weight_compatible,\n        ROW_NUMBER() OVER (ORDER BY rc.calculated_rate ASC) AS rate_rank,\n        ROW_NUMBER() OVER (ORDER BY rc.transit_days_min ASC, rc.calculated_rate ASC) AS speed_rank,\n        MIN(rc.calculated_rate) OVER () AS cheapest_rate,\n        MIN(rc.transit_days_min) OVER () AS fastest_transit_days\n    FROM rate_calculations rc\n    WHERE rc.weight_compatible = TRUE\n        AND rc.calculated_rate < 999999.99\n)\nSELECT\n    rr.carrier_name,\n    rr.service_name,\n    rr.calculated_rate AS rate_amount,\n    rr.zone_number,\n    rr.transit_days_min AS estimated_transit_days,\n    CASE\n        WHEN rr.rate_rank = 1 THEN 'Cheapest Option'\n        WHEN rr.speed_rank = 1 THEN 'Fastest Option'\n        ELSE 'Alternative Option'\n    END AS recommendation_type,\n    rr.calculated_rate - rr.cheapest_rate AS cost_difference_from_cheapest,\n    CASE\n        WHEN rr.cheapest_rate > 0\n        THEN ((rr.calculated_rate - rr.cheapest_rate) / rr.cheapest_rate * 100)\n        ELSE 0\n    END AS cost_premium_percentage,\n    CASE\n        WHEN rr.transit_days_min = rr.fastest_transit_days THEN TRUE\n        ELSE FALSE\n    END AS is_fastest_option\nFROM rate_rankings rr\nORDER BY rr.rate_rank, rr.speed_rank;",
  "evidence": "Our shipping operations team in the Shipping Intelligence domain needs to optimize carrier selection and reduce costs. We have historical data from shipments, carriers, and routes that captures shipment tracking and carrier performance metrics. Currently, we manually compare rates across carriers, which is time-consuming and prone to missing cost-saving opportunities. Generate a comprehensive rate comparison analysis that identifies the cheapest carrier, fastest carrier, calculates potential cost savings, and provides detailed rate breakdowns for all available shipping options to support data-driven carrier selection decisions. The SQL query joins shipment, carrier, and route tables, groups results by carrier and shipping zone dimensions, computes aggregate metrics including average rates and transit times, calculates cost differentials using window functions to rank carriers by price and speed, determines quartile distributions for rate analysis, and handles N",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "packages",
    "shipping_zones",
    "shipping_carriers",
    "shipping_service_types",
    "zone_lookup",
    "shipping_rates",
    "carrier_service_options",
    "package_dimensions",
    "rate_calculations",
    "rate_rankings"
  ],
  "schema_context": {},
  "expected_output": "Rate comparison results showing cheapest carrier, fastest carrier, cost savings potential, and detailed rate breakdowns for all available options.",
  "normal_query": "Rate comparison results showing the cheapest carrier option, fastest delivery carrier, potential cost savings, and detailed rate breakdowns across all available shipping options."
}
```

### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 2,
  "question": "Can you provide a shipping zone analysis showing geographic distribution patterns and transit time optimization opportunities?",
  "SQL": "WITH RECURSIVE zone_hierarchy AS (\n    -- Anchor: Base zones\n    SELECT\n        z.zone_id,\n        z.carrier_id,\n        z.origin_zip_code,\n        z.destination_zip_code,\n        z.zone_number,\n        z.zone_type,\n        z.distance_miles,\n        z.transit_days_min,\n        z.transit_days_max,\n        z.transit_days_max - z.transit_days_min AS transit_variance_days,\n        1 AS hierarchy_level,\n        CAST(z.zone_id AS VARCHAR(1000)) AS zone_path\n    FROM shipping_zones z\n    WHERE z.zone_type = 'Domestic'\n        AND (z.expiration_date IS NULL OR z.expiration_date >= CURRENT_DATE)\n    UNION ALL\n    -- Recursive: Find related zones with similar characteristics\n    SELECT\n        z.zone_id,\n        z.carrier_id,\n        z.origin_zip_code,\n        z.destination_zip_code,\n        z.zone_number,\n        z.zone_type,\n        z.distance_miles,\n        z.transit_days_min,\n        z.transit_days_max,\n        z.transit_days_max - z.transit_days_min AS transit_variance_days,\n        zh.hierarchy_level + 1,\n        zh.zone_path || ' -> ' || z.zone_id\n    FROM shipping_zones z\n    INNER JOIN zone_hierarchy zh ON z.carrier_id = zh.carrier_id\n        AND ABS(z.zone_number - zh.zone_number) <= 1\n        AND z.zone_id != zh.zone_id\n    WHERE zh.hierarchy_level < 5\n),\nzone_statistics AS (\n    -- Calculate statistics for each zone\n    SELECT\n        z.zone_number,\n        z.zone_type,\n        COUNT(DISTINCT z.carrier_id) AS carrier_count,\n        COUNT(DISTINCT z.origin_zip_code) AS origin_zip_count,\n        COUNT(DISTINCT z.destination_zip_code) AS destination_zip_count,\n        AVG(z.distance_miles) AS avg_distance_miles,\n        AVG(z.transit_days_min) AS avg_transit_days_min,\n        AVG(z.transit_days_max) AS avg_transit_days_max,\n        AVG(z.transit_days_max - z.transit_days_min) AS avg_transit_variance,\n        MIN(z.transit_days_min) AS fastest_transit_days,\n        MAX(z.transit_days_max) AS slowest_transit_days,\n        COUNT(*) AS total_zone_records\n    FROM shipping_zones z\n    WHERE z.zone_type = 'Domestic'\n        AND (z.expiration_date IS NULL OR z.expiration_date >= CURRENT_DATE)\n    GROUP BY z.zone_number, z.zone_type\n),\ncarrier_zone_performance AS (\n    -- Analyze carrier performance by zone\n    SELECT\n        z.carrier_id,\n        c.carrier_name,\n        z.zone_number,\n        COUNT(DISTINCT z.zone_id) AS zone_coverage_count,\n        AVG(z.transit_days_min) AS avg_min_transit_days,\n        AVG(z.transit_days_max) AS avg_max_transit_days,\n        AVG(z.transit_days_max - z.transit_days_min) AS avg_transit_variance,\n        MIN(z.transit_days_min) AS best_transit_days,\n        MAX(z.transit_days_max) AS worst_transit_days,\n        COUNT(DISTINCT z.origin_zip_code) AS origin_coverage,\n        COUNT(DISTINCT z.destination_zip_code) AS destination_coverage\n    FROM shipping_zones z\n    INNER JOIN shipping_carriers c ON z.carrier_id = c.carrier_id\n    WHERE z.zone_type = 'Domestic'\n        AND (z.expiration_date IS NULL OR z.expiration_date >= CURRENT_DATE)\n        AND c.active_status = TRUE\n    GROUP BY z.carrier_id, c.carrier_name, z.zone_number\n),\nzone_rankings AS (\n    -- Rank zones by performance metrics\n    SELECT\n        zs.zone_number,\n        zs.zone_type,\n        zs.carrier_count,\n        zs.avg_distance_miles,\n        zs.avg_transit_days_min,\n        zs.avg_transit_days_max,\n        zs.avg_transit_variance,\n        zs.fastest_transit_days,\n        zs.slowest_transit_days,\n        ROW_NUMBER() OVER (ORDER BY zs.avg_transit_days_min ASC) AS speed_rank,\n        ROW_NUMBER() OVER (ORDER BY zs.avg_transit_variance ASC) AS consistency_rank,\n        ROW_NUMBER() OVER (ORDER BY zs.carrier_count DESC) AS coverage_rank,\n        PERCENT_RANK() OVER (ORDER BY zs.avg_transit_days_min) AS speed_percentile,\n        PERCENT_RANK() OVER (ORDER BY zs.avg_transit_variance) AS consistency_percentile\n    FROM zone_statistics zs\n)\nSELECT\n    zr.zone_number,\n    zr.zone_type,\n    zr.carrier_count,\n    zr.avg_distance_miles,\n    zr.avg_transit_days_min,\n    zr.avg_transit_days_max,\n    zr.avg_transit_variance,\n    zr.fastest_transit_days,\n    zr.slowest_transit_days,\n    zr.speed_rank,\n    zr.consistency_rank,\n    zr.coverage_rank,\n    CASE\n        WHEN zr.speed_percentile <= 0.25 THEN 'Fast Zone'\n        WHEN zr.speed_percentile >= 0.75 THEN 'Slow Zone'\n        ELSE 'Average Zone'\n    END AS speed_category,\n    CASE\n        WHEN zr.consistency_percentile <= 0.25 THEN 'Consistent Zone'\n        WHEN zr.consistency_percentile >= 0.75 THEN 'Variable Zone'\n        ELSE 'Moderate Zone'\n    END AS consistency_category,\n    czp.carrier_name AS best_carrier_for_zone,\n    czp.avg_min_transit_days AS best_carrier_transit_days\nFROM zone_rankings zr\nLEFT JOIN LATERAL (\n    SELECT carrier_name, avg_min_transit_days\n    FROM carrier_zone_performance czp\n    WHERE czp.zone_number = zr.zone_number\n    ORDER BY czp.avg_min_transit_days ASC\n    LIMIT 1\n) czp ON TRUE\nORDER BY zr.zone_number;",
  "evidence": "Our logistics planning team in the Shipping Intelligence domain needs to understand geographic shipping patterns and optimize delivery times across different zones. We maintain comprehensive data from shipments, carriers, and routes that tracks delivery performance across various geographic zones. Currently, zone-based performance insights are fragmented across multiple reports, making it difficult to identify regional inefficiencies. Produce a detailed zone analysis report showing the distribution of shipments across zones, average transit times for each zone, geographic shipping pattern identification, and specific optimization recommendations to improve zone-based delivery performance. The SQL query aggregates shipment data by geographic zone dimensions, computes average and median transit times using aggregate functions, calculates shipment volume distributions across zones, applies window functions to identify trend patterns and compare zone performance ag",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipping_zones",
    "zone_hierarchy",
    "shipping_carriers",
    "zone_statistics",
    "zone_rankings",
    "lateral",
    "carrier_zone_performance"
  ],
  "schema_context": {},
  "expected_output": "Zone analysis results showing zone distributions, average transit times by zone, geographic shipping patterns, and optimization recommendations.",
  "normal_query": "Zone analysis results displaying zone-level distribution statistics, average transit times by shipping zone, geographic shipping pattern trends, and actionable optimization recommendations."
}
```

### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 3,
  "question": "Can you show me shipment tracking analytics with event pattern analysis and delivery time predictions?",
  "SQL": "WITH tracking_event_sequence AS (\n    -- First CTE: Sequence tracking events chronologically\n    SELECT\n        te.event_id,\n        te.shipment_id,\n        te.tracking_number,\n        te.event_timestamp,\n        te.event_type,\n        te.event_status,\n        te.event_location,\n        te.event_city,\n        te.event_state,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.estimated_delivery_date,\n        ROW_NUMBER() OVER (PARTITION BY te.shipment_id ORDER BY te.event_timestamp ASC) AS event_sequence,\n        LAG(te.event_timestamp) OVER (PARTITION BY te.shipment_id ORDER BY te.event_timestamp ASC) AS previous_event_timestamp,\n        LEAD(te.event_timestamp) OVER (PARTITION BY te.shipment_id ORDER BY te.event_timestamp ASC) AS next_event_timestamp\n    FROM tracking_events te\n    INNER JOIN shipments s ON te.shipment_id = s.shipment_id\n),\nevent_time_intervals AS (\n    -- Second CTE: Calculate time intervals between events\n    SELECT\n        tes.event_id,\n        tes.shipment_id,\n        tes.tracking_number,\n        tes.event_timestamp,\n        tes.event_type,\n        tes.event_status,\n        tes.event_location,\n        tes.event_city,\n        tes.event_state,\n        tes.carrier_id,\n        tes.service_id,\n        tes.origin_zip_code,\n        tes.destination_zip_code,\n        tes.estimated_delivery_date,\n        tes.event_sequence,\n        EXTRACT(EPOCH FROM (tes.event_timestamp - tes.previous_event_timestamp)) / 3600.0 AS hours_since_previous_event,\n        EXTRACT(EPOCH FROM (tes.next_event_timestamp - tes.event_timestamp)) / 3600.0 AS hours_until_next_event,\n        EXTRACT(EPOCH FROM (tes.event_timestamp - (SELECT MIN(event_timestamp) FROM tracking_events WHERE shipment_id = tes.shipment_id))) / 3600.0 AS total_hours_since_first_event\n    FROM tracking_event_sequence tes\n),\nshipment_progress_analysis AS (\n    -- Third CTE: Analyze shipment progress and identify milestones\n    SELECT\n        eti.shipment_id,\n        eti.tracking_number,\n        eti.carrier_id,\n        eti.service_id,\n        eti.origin_zip_code,\n        eti.destination_zip_code,\n        eti.estimated_delivery_date,\n        COUNT(*) AS total_events,\n        MIN(eti.event_timestamp) AS first_event_timestamp,\n        MAX(eti.event_timestamp) AS last_event_timestamp,\n        MAX(CASE WHEN eti.event_type = 'Label Created' THEN eti.event_timestamp END) AS label_created_timestamp,\n        MAX(CASE WHEN eti.event_type = 'In Transit' THEN eti.event_timestamp END) AS in_transit_timestamp,\n        MAX(CASE WHEN eti.event_type = 'Out for Delivery' THEN eti.event_timestamp END) AS out_for_delivery_timestamp,\n        MAX(CASE WHEN eti.event_type = 'Delivered' THEN eti.event_timestamp END) AS delivered_timestamp,\n        MAX(CASE WHEN eti.event_type = 'Exception' THEN eti.event_timestamp END) AS exception_timestamp,\n        COUNT(CASE WHEN eti.event_type = 'Exception' THEN 1 END) AS exception_count,\n        AVG(eti.hours_since_previous_event) AS avg_hours_between_events,\n        MAX(eti.hours_since_previous_event) AS max_hours_between_events\n    FROM event_time_intervals eti\n    GROUP BY eti.shipment_id, eti.tracking_number, eti.carrier_id, eti.service_id, eti.origin_zip_code, eti.destination_zip_code, eti.estimated_delivery_date\n),\nhistorical_delivery_patterns AS (\n    -- Fourth CTE: Analyze historical delivery patterns by carrier and service\n    SELECT\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        COUNT(*) AS historical_shipment_count,\n        AVG(EXTRACT(EPOCH FROM (spa.delivered_timestamp - spa.label_created_timestamp)) / 86400.0) AS avg_delivery_days,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (spa.delivered_timestamp - spa.label_created_timestamp)) / 86400.0) AS median_delivery_days,\n        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (spa.delivered_timestamp - spa.label_created_timestamp)) / 86400.0) AS p95_delivery_days,\n        STDDEV(EXTRACT(EPOCH FROM (spa.delivered_timestamp - spa.label_created_timestamp)) / 86400.0) AS stddev_delivery_days,\n        COUNT(CASE WHEN spa.exception_count > 0 THEN 1 END) AS shipments_with_exceptions,\n        COUNT(CASE WHEN spa.delivered_timestamp <= spa.estimated_delivery_date THEN 1 END) AS on_time_deliveries\n    FROM shipment_progress_analysis spa\n    INNER JOIN shipments s ON spa.shipment_id = s.shipment_id\n    WHERE spa.delivered_timestamp IS NOT NULL\n        AND spa.label_created_timestamp IS NOT NULL\n    GROUP BY s.carrier_id, s.service_id, s.origin_zip_code, s.destination_zip_code\n),\ndelivery_prediction AS (\n    -- Fifth CTE: Predict delivery dates for in-transit shipments\n    SELECT\n        spa.shipment_id,\n        spa.tracking_number,\n        spa.carrier_id,\n        spa.service_id,\n        spa.origin_zip_code,\n        spa.destination_zip_code,\n        spa.estimated_delivery_date AS carrier_estimated_delivery,\n        spa.label_created_timestamp,\n        spa.last_event_timestamp,\n        spa.total_hours_since_first_event / 24.0 AS days_in_transit,\n        hdp.avg_delivery_days AS historical_avg_delivery_days,\n        hdp.median_delivery_days AS historical_median_delivery_days,\n        hdp.p95_delivery_days AS historical_p95_delivery_days,\n        CASE\n            WHEN spa.delivered_timestamp IS NOT NULL THEN spa.delivered_timestamp\n            WHEN spa.out_for_delivery_timestamp IS NOT NULL THEN spa.out_for_delivery_timestamp + INTERVAL '1 day'\n            WHEN spa.in_transit_timestamp IS NOT NULL THEN spa.label_created_timestamp + INTERVAL '1 day' * hdp.median_delivery_days\n            ELSE spa.estimated_delivery_date\n        END AS predicted_delivery_date,\n        spa.exception_count,\n        CASE\n            WHEN spa.exception_count > 0 THEN TRUE\n            WHEN spa.max_hours_between_events > 48 THEN TRUE\n            ELSE FALSE\n        END AS has_anomaly\n    FROM shipment_progress_analysis spa\n    LEFT JOIN historical_delivery_patterns hdp ON spa.carrier_id = hdp.carrier_id\n        AND spa.service_id = hdp.service_id\n        AND spa.origin_zip_code = hdp.origin_zip_code\n        AND spa.destination_zip_code = hdp.destination_zip_code\n),\nanomaly_detection AS (\n    -- Sixth CTE: Detect anomalies and potential delays\n    SELECT\n        dp.shipment_id,\n        dp.tracking_number,\n        dp.carrier_id,\n        dp.service_id,\n        dp.predicted_delivery_date,\n        dp.carrier_estimated_delivery,\n        dp.has_anomaly,\n        dp.exception_count,\n        CASE\n            WHEN dp.predicted_delivery_date > dp.carrier_estimated_delivery + INTERVAL '2 days' THEN 'Potential Delay'\n            WHEN dp.has_anomaly = TRUE THEN 'Anomaly Detected'\n            WHEN dp.days_in_transit > dp.historical_p95_delivery_days THEN 'Slow Progress'\n            ELSE 'Normal'\n        END AS shipment_status_category,\n        CASE\n            WHEN dp.predicted_delivery_date > dp.carrier_estimated_delivery THEN EXTRACT(EPOCH FROM (dp.predicted_delivery_date - dp.carrier_estimated_delivery)) / 86400.0\n            ELSE 0\n        END AS predicted_delay_days\n    FROM delivery_prediction dp\n)\nSELECT\n    ad.shipment_id,\n    ad.tracking_number,\n    c.carrier_name,\n    st.service_name,\n    ad.predicted_delivery_date,\n    ad.carrier_estimated_delivery,\n    ad.shipment_status_category,\n    ad.predicted_delay_days,\n    ad.exception_count,\n    ad.has_anomaly,\n    CASE\n        WHEN ad.shipment_status_category != 'Normal' THEN 'Action Required'\n        ELSE 'Monitoring'\n    END AS alert_level\nFROM anomaly_detection ad\nINNER JOIN shipping_carriers c ON ad.carrier_id = c.carrier_id\nINNER JOIN shipping_service_types st ON ad.service_id = st.service_id\nORDER BY ad.predicted_delivery_date, ad.predicted_delay_days DESC;",
  "evidence": "Our customer service and operations teams in the Shipping Intelligence domain need proactive visibility into shipment status and potential delivery issues. We collect detailed tracking event data from shipments, carriers, and routes that captures every milestone in the delivery lifecycle. Currently, we reactively respond to delivery problems rather than predicting and preventing them, leading to customer dissatisfaction and expedited shipping costs. Create a comprehensive tracking analytics report that predicts delivery times, identifies event patterns indicating potential delays, detects anomalies in shipping behavior, and evaluates carrier performance metrics to enable proactive shipment management. The SQL query analyzes tracking event sequences across shipments, groups events by shipment and carrier dimensions, computes aggregate metrics for event timing and frequency, applies window functions to calculate rolling averages and identify deviation patterns fr",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "tracking_events",
    "shipments",
    "tracking_event_sequence",
    "event_time_intervals",
    "shipment_progress_analysis",
    "historical_delivery_patterns",
    "delivery_prediction",
    "anomaly_detection",
    "shipping_carriers",
    "shipping_service_types"
  ],
  "schema_context": {},
  "expected_output": "Tracking analytics showing delivery predictions, event patterns, anomaly detection results, and carrier performance metrics.",
  "normal_query": "Tracking analytics results presenting delivery time predictions, shipping event pattern analysis, anomaly detection findings, and comprehensive carrier performance metrics."
}
```

### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 4,
  "question": "Can you give me an address validation quality analysis including correction rate metrics and accuracy trends?",
  "SQL": "WITH address_validation_comparison AS (\n    -- First CTE: Compare input and validated addresses\n    SELECT\n        avr.validation_id,\n        avr.input_address_line1,\n        avr.input_address_line2,\n        avr.input_city,\n        avr.input_state,\n        avr.input_zip_code,\n        avr.validated_address_line1,\n        avr.validated_address_line2,\n        avr.validated_city,\n        avr.validated_state,\n        avr.validated_zip_code,\n        avr.validated_zip_plus_4,\n        avr.validation_status,\n        avr.dpv_confirmation,\n        avr.cmra_flag,\n        avr.vacant_flag,\n        avr.residential_flag,\n        CASE\n            WHEN UPPER(TRIM(avr.input_address_line1)) != UPPER(TRIM(avr.validated_address_line1))\n                OR UPPER(TRIM(avr.input_city)) != UPPER(TRIM(avr.validated_city))\n                OR UPPER(TRIM(avr.input_state)) != UPPER(TRIM(avr.validated_state))\n                OR UPPER(TRIM(avr.input_zip_code)) != UPPER(TRIM(avr.validated_zip_code))\n            THEN TRUE\n            ELSE FALSE\n        END AS address_was_corrected,\n        CASE\n            WHEN UPPER(TRIM(avr.input_address_line1)) != UPPER(TRIM(avr.validated_address_line1)) THEN 'Address Line 1'\n            WHEN UPPER(TRIM(avr.input_city)) != UPPER(TRIM(avr.validated_city)) THEN 'City'\n            WHEN UPPER(TRIM(avr.input_state)) != UPPER(TRIM(avr.validated_state)) THEN 'State'\n            WHEN UPPER(TRIM(avr.input_zip_code)) != UPPER(TRIM(avr.validated_zip_code)) THEN 'ZIP Code'\n            ELSE 'No Correction'\n        END AS correction_type,\n        avr.validation_timestamp\n    FROM address_validation_results avr\n),\nvalidation_statistics AS (\n    -- Second CTE: Calculate validation statistics\n    SELECT\n        DATE(avc.validation_timestamp) AS validation_date,\n        COUNT(*) AS total_validations,\n        COUNT(CASE WHEN avc.validation_status = 'Valid' THEN 1 END) AS valid_count,\n        COUNT(CASE WHEN avc.validation_status = 'Corrected' THEN 1 END) AS corrected_count,\n        COUNT(CASE WHEN avc.validation_status = 'Invalid' THEN 1 END) AS invalid_count,\n        COUNT(CASE WHEN avc.validation_status = 'Ambiguous' THEN 1 END) AS ambiguous_count,\n        COUNT(CASE WHEN avc.address_was_corrected = TRUE THEN 1 END) AS address_corrections_count,\n        COUNT(CASE WHEN avc.dpv_confirmation = 'Y' THEN 1 END) AS dpv_confirmed_count,\n        COUNT(CASE WHEN avc.cmra_flag = TRUE THEN 1 END) AS cmra_count,\n        COUNT(CASE WHEN avc.vacant_flag = TRUE THEN 1 END) AS vacant_count,\n        COUNT(CASE WHEN avc.residential_flag = TRUE THEN 1 END) AS residential_count,\n        AVG(CASE WHEN avc.address_was_corrected = TRUE THEN 1 ELSE 0 END) * 100 AS correction_rate_percentage\n    FROM address_validation_comparison avc\n    GROUP BY DATE(avc.validation_timestamp)\n),\ncorrection_pattern_analysis AS (\n    -- Third CTE: Analyze correction patterns\n    SELECT\n        avc.correction_type,\n        COUNT(*) AS correction_count,\n        COUNT(DISTINCT avc.validated_state) AS states_affected,\n        COUNT(DISTINCT SUBSTRING(avc.validated_zip_code, 1, 5)) AS zip_codes_affected,\n        AVG(CASE WHEN avc.dpv_confirmation = 'Y' THEN 1 ELSE 0 END) * 100 AS dpv_confirmation_rate,\n        COUNT(CASE WHEN avc.validation_status = 'Valid' THEN 1 END) AS valid_after_correction_count\n    FROM address_validation_comparison avc\n    WHERE avc.address_was_corrected = TRUE\n    GROUP BY avc.correction_type\n),\nvalidation_quality_metrics AS (\n    -- Fourth CTE: Calculate quality metrics\n    SELECT\n        vs.validation_date,\n        vs.total_validations,\n        vs.valid_count,\n        vs.corrected_count,\n        vs.invalid_count,\n        vs.ambiguous_count,\n        vs.address_corrections_count,\n        vs.dpv_confirmed_count,\n        vs.cmra_count,\n        vs.vacant_count,\n        vs.residential_count,\n        vs.correction_rate_percentage,\n        CASE\n            WHEN vs.total_validations > 0\n            THEN (vs.valid_count + vs.corrected_count)::numeric / vs.total_validations * 100\n            ELSE 0\n        END AS success_rate_percentage,\n        CASE\n            WHEN vs.total_validations > 0\n            THEN vs.dpv_confirmed_count::numeric / vs.total_validations * 100\n            ELSE 0\n        END AS dpv_confirmation_rate_percentage,\n        CASE\n            WHEN vs.total_validations > 0\n            THEN vs.invalid_count::numeric / vs.total_validations * 100\n            ELSE 0\n        END AS invalid_rate_percentage\n    FROM validation_statistics vs\n)\nSELECT\n    vqm.validation_date,\n    vqm.total_validations,\n    vqm.valid_count,\n    vqm.corrected_count,\n    vqm.invalid_count,\n    vqm.ambiguous_count,\n    vqm.address_corrections_count,\n    vqm.dpv_confirmed_count,\n    vqm.success_rate_percentage,\n    vqm.correction_rate_percentage,\n    vqm.dpv_confirmation_rate_percentage,\n    vqm.invalid_rate_percentage,\n    cpa.correction_type AS most_common_correction_type,\n    cpa.correction_count AS most_common_correction_count,\n    CASE\n        WHEN vqm.success_rate_percentage >= 95 THEN 'Excellent'\n        WHEN vqm.success_rate_percentage >= 85 THEN 'Good'\n        WHEN vqm.success_rate_percentage >= 75 THEN 'Fair'\n        ELSE 'Needs Improvement'\n    END AS quality_category\nFROM validation_quality_metrics vqm\nLEFT JOIN LATERAL (\n    SELECT correction_type, correction_count\n    FROM correction_pattern_analysis cpa\n    ORDER BY cpa.correction_count DESC\n    LIMIT 1\n) cpa ON TRUE\nORDER BY vqm.validation_date DESC;",
  "evidence": "Our data quality team in the Shipping Intelligence domain is experiencing increasing delivery failures and returns due to invalid or incomplete shipping addresses. We maintain records from shipments, carriers, and routes that include both original entered addresses and validated/corrected versions. Poor address quality leads to failed deliveries, increased costs from address correction services, and negative customer experiences, but we lack systematic visibility into where and why address issues occur. Generate a comprehensive address validation quality analysis showing validation success rates, common correction patterns, overall data quality metrics by source and region, and actionable recommendations for improving address capture accuracy to reduce delivery failures. The SQL query joins shipment address data with validation results, groups records by relevant dimensions such as address source, geographic region, and entry channel, computes aggregate validat",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "address_validation_results",
    "address_validation_comparison",
    "validation_statistics",
    "validation_quality_metrics",
    "lateral",
    "correction_pattern_analysis"
  ],
  "schema_context": {},
  "expected_output": "Address validation analytics showing validation rates, correction patterns, quality metrics, and recommendations for improving address accuracy.",
  "normal_query": "Address validation analytics displaying validation success rates, address correction pattern analysis, data quality metrics, and specific recommendations for improving address accuracy across the shipping network."
}
```

### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 5,
  "question": "Can you show me shipping cost analytics with revenue optimization insights and carrier performance comparisons?",
  "SQL": "WITH shipment_cost_details AS (\n    -- First CTE: Aggregate shipment costs\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.package_id,\n        DATE(s.created_at) AS shipment_date,\n        s.label_cost,\n        s.insurance_cost,\n        s.signature_cost,\n        s.total_cost,\n        p.weight_lbs,\n        p.package_value,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.shipment_status,\n        CASE\n            WHEN s.shipment_status = 'Delivered' THEN s.total_cost\n            ELSE 0\n        END AS delivered_cost,\n        CASE\n            WHEN s.shipment_status IN ('Exception', 'Returned') THEN s.total_cost\n            ELSE 0\n        END AS exception_cost\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n),\ndaily_cost_summary AS (\n    -- Second CTE: Daily cost summaries\n    SELECT\n        scd.shipment_date,\n        scd.carrier_id,\n        scd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(scd.total_cost) AS total_revenue,\n        SUM(scd.label_cost) AS total_label_cost,\n        SUM(scd.insurance_cost) AS total_insurance_cost,\n        SUM(scd.signature_cost) AS total_signature_cost,\n        SUM(scd.delivered_cost) AS delivered_revenue,\n        SUM(scd.exception_cost) AS exception_revenue,\n        AVG(scd.total_cost) AS avg_shipment_cost,\n        AVG(scd.weight_lbs) AS avg_weight_lbs,\n        COUNT(CASE WHEN scd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        COUNT(CASE WHEN scd.shipment_status IN ('Exception', 'Returned') THEN 1 END) AS exception_count\n    FROM shipment_cost_details scd\n    GROUP BY scd.shipment_date, scd.carrier_id, scd.service_id\n),\ncarrier_performance_metrics AS (\n    -- Third CTE: Calculate carrier performance metrics\n    SELECT\n        dcs.carrier_id,\n        c.carrier_name,\n        COUNT(DISTINCT dcs.shipment_date) AS active_days,\n        SUM(dcs.total_shipments) AS total_shipments,\n        SUM(dcs.total_revenue) AS total_revenue,\n        SUM(dcs.delivered_revenue) AS delivered_revenue,\n        SUM(dcs.exception_revenue) AS exception_revenue,\n        AVG(dcs.avg_shipment_cost) AS avg_shipment_cost,\n        AVG(dcs.avg_weight_lbs) AS avg_weight_lbs,\n        SUM(dcs.delivered_count) AS total_delivered,\n        SUM(dcs.exception_count) AS total_exceptions,\n        CASE\n            WHEN SUM(dcs.total_shipments) > 0\n            THEN SUM(dcs.delivered_count)::numeric / SUM(dcs.total_shipments) * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        CASE\n            WHEN SUM(dcs.total_shipments) > 0\n            THEN SUM(dcs.exception_count)::numeric / SUM(dcs.total_shipments) * 100\n            ELSE 0\n        END AS exception_rate,\n        CASE\n            WHEN SUM(dcs.delivered_count) > 0\n            THEN SUM(dcs.delivered_revenue) / SUM(dcs.delivered_count)\n            ELSE 0\n        END AS avg_revenue_per_delivered_shipment\n    FROM daily_cost_summary dcs\n    INNER JOIN shipping_carriers c ON dcs.carrier_id = c.carrier_id\n    GROUP BY dcs.carrier_id, c.carrier_name\n),\nservice_performance_metrics AS (\n    -- Fourth CTE: Calculate service performance metrics\n    SELECT\n        dcs.service_id,\n        st.service_name,\n        st.service_category,\n        COUNT(DISTINCT dcs.shipment_date) AS active_days,\n        SUM(dcs.total_shipments) AS total_shipments,\n        SUM(dcs.total_revenue) AS total_revenue,\n        AVG(dcs.avg_shipment_cost) AS avg_shipment_cost,\n        SUM(dcs.delivered_count) AS total_delivered,\n        SUM(dcs.exception_count) AS total_exceptions,\n        CASE\n            WHEN SUM(dcs.total_shipments) > 0\n            THEN SUM(dcs.delivered_count)::numeric / SUM(dcs.total_shipments) * 100\n            ELSE 0\n        END AS delivery_success_rate\n    FROM daily_cost_summary dcs\n    INNER JOIN shipping_service_types st ON dcs.service_id = st.service_id\n    GROUP BY dcs.service_id, st.service_name, st.service_category\n),\ncost_optimization_opportunities AS (\n    -- Fifth CTE: Identify cost optimization opportunities\n    SELECT\n        scd.shipment_id,\n        scd.carrier_id,\n        scd.service_id,\n        scd.total_cost,\n        scd.origin_zip_code,\n        scd.destination_zip_code,\n        (SELECT MIN(sr.total_rate)\n         FROM shipping_rates sr\n         WHERE sr.carrier_id != scd.carrier_id\n             AND sr.weight_lbs >= scd.weight_lbs\n             AND (sr.expiration_date IS NULL OR sr.expiration_date >= CURRENT_DATE)\n             AND sr.effective_date <= CURRENT_DATE\n         LIMIT 1) AS alternative_min_rate,\n        scd.total_cost - (SELECT MIN(sr.total_rate)\n                          FROM shipping_rates sr\n                          WHERE sr.carrier_id != scd.carrier_id\n                              AND sr.weight_lbs >= scd.weight_lbs\n                              AND (sr.expiration_date IS NULL OR sr.expiration_date >= CURRENT_DATE)\n                              AND sr.effective_date <= CURRENT_DATE\n                          LIMIT 1) AS potential_savings\n    FROM shipment_cost_details scd\n    WHERE scd.shipment_status = 'Delivered'\n)\nSELECT\n    cpm.carrier_name,\n    cpm.total_shipments,\n    cpm.total_revenue,\n    cpm.delivered_revenue,\n    cpm.exception_revenue,\n    cpm.avg_shipment_cost,\n    cpm.delivery_success_rate,\n    cpm.exception_rate,\n    cpm.avg_revenue_per_delivered_shipment,\n    ROW_NUMBER() OVER (ORDER BY cpm.total_revenue DESC) AS revenue_rank,\n    ROW_NUMBER() OVER (ORDER BY cpm.delivery_success_rate DESC) AS performance_rank,\n    ROW_NUMBER() OVER (ORDER BY cpm.avg_shipment_cost ASC) AS cost_efficiency_rank,\n    SUM(COALESCE(coo.potential_savings, 0)) OVER (PARTITION BY cpm.carrier_id) AS total_potential_savings,\n    CASE\n        WHEN cpm.delivery_success_rate >= 95 AND cpm.exception_rate <= 2 THEN 'Excellent'\n        WHEN cpm.delivery_success_rate >= 90 AND cpm.exception_rate <= 5 THEN 'Good'\n        WHEN cpm.delivery_success_rate >= 85 AND cpm.exception_rate <= 10 THEN 'Fair'\n        ELSE 'Needs Improvement'\n    END AS performance_category\nFROM carrier_performance_metrics cpm\nLEFT JOIN cost_optimization_opportunities coo ON cpm.carrier_id = coo.carrier_id\nGROUP BY cpm.carrier_id, cpm.carrier_name, cpm.total_shipments, cpm.total_revenue, cpm.delivered_revenue, cpm.exception_revenue, cpm.avg_shipment_cost, cpm.delivery_success_rate, cpm.exception_rate, cpm.avg_revenue_per_delivered_shipment\nORDER BY cpm.total_revenue DESC;",
  "evidence": "Our finance and operations leadership in the Shipping Intelligence domain needs to control rising shipping costs while maintaining service quality. We track comprehensive data from shipments, carriers, and routes that captures actual costs, billed amounts, service levels, and performance metrics. Shipping costs represent a significant operational expense, but we lack integrated visibility into cost drivers, carrier efficiency, and optimization opportunities, making it difficult to negotiate better rates or select cost-effective carriers. Deliver a comprehensive shipping cost analytics report showing revenue and cost metrics, detailed breakdowns of cost components (base rates, fuel surcharges, accessorial fees), comparative carrier performance analysis, and specific optimization recommendations to reduce total shipping spend while maintaining or improving delivery performance. The SQL query integrates shipment cost data with carrier performance metrics, groups r",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "shipment_cost_details",
    "daily_cost_summary",
    "shipping_carriers",
    "shipping_service_types",
    "shipping_rates",
    "carrier_performance_metrics",
    "cost_optimization_opportunities"
  ],
  "schema_context": {},
  "expected_output": "Shipping cost analytics showing revenue metrics, cost breakdowns, carrier performance comparisons, and optimization recommendations.",
  "normal_query": "Shipping cost analytics presenting revenue metrics, detailed cost breakdowns by component, carrier-to-carrier performance comparisons, and specific optimization recommendations for reducing shipping expenses."
}
```

### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 6,
  "question": "Show me bulk shipping preset optimization results with weight distribution analysis.",
  "SQL": "WITH preset_usage_analysis AS (\n    -- First CTE: Analyze preset usage patterns\n    SELECT\n        bsp.preset_id,\n        bsp.user_id,\n        bsp.preset_name,\n        bsp.package_type,\n        bsp.default_weight_lbs,\n        bsp.default_length_inches,\n        bsp.default_width_inches,\n        bsp.default_height_inches,\n        bsp.default_service_id,\n        bsp.default_carrier_id,\n        COUNT(s.shipment_id) AS usage_count,\n        SUM(s.total_cost) AS total_cost_using_preset,\n        AVG(s.total_cost) AS avg_cost_per_shipment,\n        AVG(p.weight_lbs) AS avg_actual_weight_lbs,\n        AVG(p.length_inches) AS avg_actual_length_inches,\n        AVG(p.width_inches) AS avg_actual_width_inches,\n        AVG(p.height_inches) AS avg_actual_height_inches\n    FROM bulk_shipping_presets bsp\n    LEFT JOIN shipments s ON s.carrier_id = bsp.default_carrier_id\n        AND s.service_id = bsp.default_service_id\n    LEFT JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n    GROUP BY bsp.preset_id, bsp.user_id, bsp.preset_name, bsp.package_type, bsp.default_weight_lbs, bsp.default_length_inches, bsp.default_width_inches, bsp.default_height_inches, bsp.default_service_id, bsp.default_carrier_id\n),\npreset_cost_analysis AS (\n    -- Second CTE: Analyze preset costs and identify optimization opportunities\n    SELECT\n        pua.preset_id,\n        pua.preset_name,\n        pua.usage_count,\n        pua.total_cost_using_preset,\n        pua.avg_cost_per_shipment,\n        pua.default_weight_lbs,\n        pua.avg_actual_weight_lbs,\n        ABS(pua.default_weight_lbs - pua.avg_actual_weight_lbs) AS weight_difference_lbs,\n        (SELECT MIN(sr.total_rate)\n         FROM shipping_rates sr\n         WHERE sr.carrier_id = pua.default_carrier_id\n             AND sr.weight_lbs >= pua.avg_actual_weight_lbs\n             AND (sr.expiration_date IS NULL OR sr.expiration_date >= CURRENT_DATE)\n             AND sr.effective_date <= CURRENT_DATE\n         LIMIT 1) AS optimized_rate,\n        pua.avg_cost_per_shipment - (SELECT MIN(sr.total_rate)\n                                      FROM shipping_rates sr\n                                      WHERE sr.carrier_id = pua.default_carrier_id\n                                          AND sr.weight_lbs >= pua.avg_actual_weight_lbs\n                                          AND (sr.expiration_date IS NULL OR sr.expiration_date >= CURRENT_DATE)\n                                          AND sr.effective_date <= CURRENT_DATE\n                                      LIMIT 1) AS potential_savings_per_shipment\n    FROM preset_usage_analysis pua\n    WHERE pua.usage_count > 0\n),\npreset_recommendations AS (\n    -- Third CTE: Generate preset optimization recommendations\n    SELECT\n        pca.preset_id,\n        pca.preset_name,\n        pca.usage_count,\n        pca.avg_cost_per_shipment,\n        pca.optimized_rate,\n        pca.potential_savings_per_shipment,\n        pca.potential_savings_per_shipment * pca.usage_count AS total_potential_savings,\n        CASE\n            WHEN pca.weight_difference_lbs > 1.0 THEN 'Adjust Weight Default'\n            WHEN pca.potential_savings_per_shipment > 2.0 THEN 'Optimize Service Selection'\n            ELSE 'Preset Optimal'\n        END AS optimization_recommendation\n    FROM preset_cost_analysis pca\n)\nSELECT\n    pr.preset_id,\n    pr.preset_name,\n    pr.usage_count,\n    pr.avg_cost_per_shipment,\n    pr.optimized_rate,\n    pr.potential_savings_per_shipment,\n    pr.total_potential_savings,\n    pr.optimization_recommendation,\n    ROW_NUMBER() OVER (ORDER BY pr.total_potential_savings DESC) AS savings_rank\nFROM preset_recommendations pr\nORDER BY pr.total_potential_savings DESC;",
  "evidence": "The logistics operations team manages high-volume shipping and needs to optimize preset configurations to reduce costs. Historical shipment data across carriers and routes contains weight distributions and configuration patterns that can reveal cost-saving opportunities. Analyze bulk shipping presets to identify optimal configurations based on weight distribution patterns, calculate potential cost savings, and determine usage patterns across different shipment types. The query joins shipments with preset configurations and carrier rate tables, groups by preset type and weight brackets, computes aggregate metrics including average weights and costs, calculates quartiles for weight distribution analysis, uses window functions to compare actual versus optimal preset usage, and handles NULL values in optional preset fields. Returns a dataset containing preset recommendations, estimated cost savings per configuration, weight distribution quartiles, usage fre",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "bulk_shipping_presets",
    "shipments",
    "packages",
    "shipping_rates",
    "preset_usage_analysis",
    "preset_cost_analysis",
    "preset_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Bulk shipping preset optimization results showing recommended configurations, cost savings potential, and usage patterns.",
  "normal_query": "Bulk shipping preset optimization analysis showing recommended preset configurations, potential cost savings, weight distribution patterns, and usage frequency across shipment types."
}
```

### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 7,
  "question": "Show me international shipping customs analysis with duty and tax optimization opportunities.",
  "SQL": "WITH international_shipment_details AS (\n    -- First CTE: Get international shipment and customs details\n    SELECT\n        ic.customs_id,\n        ic.shipment_id,\n        ic.customs_declaration_number,\n        ic.customs_value,\n        ic.currency_code,\n        ic.hs_tariff_code,\n        ic.country_of_origin,\n        ic.customs_duty_amount,\n        ic.customs_tax_amount,\n        ic.customs_fees_amount,\n        ic.total_customs_amount,\n        ic.customs_status,\n        ic.customs_cleared_date,\n        s.destination_country,\n        s.destination_zip_code,\n        s.total_cost AS shipment_cost,\n        p.package_value,\n        s.created_at AS shipment_date\n    FROM international_customs ic\n    INNER JOIN shipments s ON ic.shipment_id = s.shipment_id\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.destination_country != 'US'\n),\ncustoms_value_analysis AS (\n    -- Second CTE: Analyze customs value patterns\n    SELECT\n        isd.destination_country,\n        COUNT(*) AS total_shipments,\n        AVG(isd.customs_value) AS avg_customs_value,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY isd.customs_value) AS median_customs_value,\n        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY isd.customs_value) AS p95_customs_value,\n        AVG(isd.customs_duty_amount) AS avg_duty_amount,\n        AVG(isd.customs_tax_amount) AS avg_tax_amount,\n        AVG(isd.customs_fees_amount) AS avg_fees_amount,\n        AVG(isd.total_customs_amount) AS avg_total_customs_amount,\n        COUNT(CASE WHEN isd.customs_status = 'Cleared' THEN 1 END) AS cleared_count,\n        COUNT(CASE WHEN isd.customs_status = 'Held' THEN 1 END) AS held_count,\n        COUNT(CASE WHEN isd.customs_status = 'Returned' THEN 1 END) AS returned_count\n    FROM international_shipment_details isd\n    GROUP BY isd.destination_country\n),\nduty_rate_analysis AS (\n    -- Third CTE: Analyze duty rates by country and tariff code\n    SELECT\n        isd.destination_country,\n        isd.hs_tariff_code,\n        COUNT(*) AS shipment_count,\n        AVG(isd.customs_duty_amount / NULLIF(isd.customs_value, 0) * 100) AS avg_duty_rate_percentage,\n        AVG(isd.customs_tax_amount / NULLIF(isd.customs_value, 0) * 100) AS avg_tax_rate_percentage,\n        AVG(isd.total_customs_amount / NULLIF(isd.customs_value, 0) * 100) AS avg_total_customs_rate_percentage\n    FROM international_shipment_details isd\n    WHERE isd.customs_value > 0\n        AND isd.hs_tariff_code IS NOT NULL\n    GROUP BY isd.destination_country, isd.hs_tariff_code\n),\ncustoms_clearance_performance AS (\n    -- Fourth CTE: Analyze customs clearance performance\n    SELECT\n        isd.destination_country,\n        COUNT(*) AS total_shipments,\n        COUNT(CASE WHEN isd.customs_status = 'Cleared' THEN 1 END) AS cleared_shipments,\n        COUNT(CASE WHEN isd.customs_status = 'Held' THEN 1 END) AS held_shipments,\n        COUNT(CASE WHEN isd.customs_status = 'Returned' THEN 1 END) AS returned_shipments,\n        AVG(EXTRACT(EPOCH FROM (isd.customs_cleared_date - isd.shipment_date)) / 86400.0) AS avg_clearance_days,\n        CASE\n            WHEN COUNT(*) > 0\n            THEN COUNT(CASE WHEN isd.customs_status = 'Cleared' THEN 1 END)::numeric / COUNT(*) * 100\n            ELSE 0\n        END AS clearance_success_rate\n    FROM international_shipment_details isd\n    GROUP BY isd.destination_country\n),\ncustoms_optimization_opportunities AS (\n    -- Fifth CTE: Identify customs optimization opportunities\n    SELECT\n        isd.customs_id,\n        isd.shipment_id,\n        isd.destination_country,\n        isd.customs_value,\n        isd.total_customs_amount,\n        cva.avg_total_customs_amount AS country_avg_customs_amount,\n        isd.total_customs_amount - cva.avg_total_customs_amount AS deviation_from_avg,\n        CASE\n            WHEN isd.total_customs_amount > cva.avg_total_customs_amount * 1.2 THEN 'High Customs Cost'\n            WHEN isd.total_customs_amount < cva.avg_total_customs_amount * 0.8 THEN 'Low Customs Cost'\n            ELSE 'Normal'\n        END AS cost_category\n    FROM international_shipment_details isd\n    INNER JOIN customs_value_analysis cva ON isd.destination_country = cva.destination_country\n)\nSELECT\n    ccp.destination_country,\n    cva.total_shipments,\n    cva.avg_customs_value,\n    cva.median_customs_value,\n    cva.avg_total_customs_amount,\n    ccp.cleared_shipments,\n    ccp.held_shipments,\n    ccp.returned_shipments,\n    ccp.clearance_success_rate,\n    ccp.avg_clearance_days,\n    COUNT(CASE WHEN coo.cost_category = 'High Customs Cost' THEN 1 END) AS high_cost_shipments,\n    COUNT(CASE WHEN coo.cost_category = 'Low Customs Cost' THEN 1 END) AS low_cost_shipments,\n    CASE\n        WHEN ccp.clearance_success_rate >= 95 THEN 'Excellent'\n        WHEN ccp.clearance_success_rate >= 85 THEN 'Good'\n        WHEN ccp.clearance_success_rate >= 75 THEN 'Fair'\n        ELSE 'Needs Improvement'\n    END AS performance_category\nFROM customs_clearance_performance ccp\nINNER JOIN customs_value_analysis cva ON ccp.destination_country = cva.destination_country\nLEFT JOIN customs_optimization_opportunities coo ON ccp.destination_country = coo.destination_country\nGROUP BY ccp.destination_country, cva.total_shipments, cva.avg_customs_value, cva.median_customs_value, cva.avg_total_customs_amount, ccp.cleared_shipments, ccp.held_shipments, ccp.returned_shipments, ccp.clearance_success_rate, ccp.avg_clearance_days\nORDER BY ccp.clearance_success_rate DESC, ccp.avg_clearance_days ASC;",
  "evidence": "The international shipping department faces increasing customs duties and taxes on cross-border shipments, impacting profitability. Customs clearance data including duty assessments, tax calculations, and clearance outcomes needs analysis to identify optimization opportunities and improve success rates. Analyze international customs data to calculate total duty and tax amounts, identify patterns in clearance delays or failures, detect optimization opportunities through tariff classification or routing changes, and measure clearance success rates by destination country. The query joins international shipments with customs declarations, duty assessments, and clearance status tables, groups by destination country and product category, computes aggregate duty and tax amounts, calculates clearance success rates and average processing times, uses window functions to identify trends over rolling time periods and compare against historical baselines, and handles cases ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "international_customs",
    "shipments",
    "packages",
    "international_shipment_details",
    "customs_value_analysis",
    "customs_clearance_performance",
    "customs_optimization_opportunities"
  ],
  "schema_context": {},
  "expected_output": "International customs analysis showing duty amounts, tax calculations, optimization opportunities, and clearance success rates.",
  "normal_query": "International customs compliance analysis displaying duty amounts, tax calculations, clearance success rates, and optimization opportunities for international shipments."
}
```

### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 8,
  "question": "Show me shipping adjustment analysis with discrepancy detection and cost recovery opportunities.",
  "SQL": "WITH adjustment_details AS (\n    -- First CTE: Get detailed adjustment information\n    SELECT\n        sa.adjustment_id,\n        sa.shipment_id,\n        sa.tracking_number,\n        sa.adjustment_type,\n        sa.original_amount,\n        sa.adjusted_amount,\n        sa.adjustment_amount,\n        sa.adjustment_reason,\n        sa.adjustment_status,\n        sa.adjustment_date,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost AS original_shipment_cost,\n        p.weight_lbs AS declared_weight_lbs,\n        p.length_inches AS declared_length_inches,\n        p.width_inches AS declared_width_inches,\n        p.height_inches AS declared_height_inches\n    FROM shipping_adjustments sa\n    INNER JOIN shipments s ON sa.shipment_id = s.shipment_id\n    INNER JOIN packages p ON s.package_id = p.package_id\n),\nadjustment_statistics AS (\n    -- Second CTE: Calculate adjustment statistics by type\n    SELECT\n        ad.adjustment_type,\n        COUNT(*) AS total_adjustments,\n        SUM(ABS(ad.adjustment_amount)) AS total_adjustment_amount,\n        AVG(ABS(ad.adjustment_amount)) AS avg_adjustment_amount,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(ad.adjustment_amount)) AS median_adjustment_amount,\n        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ABS(ad.adjustment_amount)) AS p95_adjustment_amount,\n        COUNT(CASE WHEN ad.adjustment_status = 'Applied' THEN 1 END) AS applied_count,\n        COUNT(CASE WHEN ad.adjustment_status = 'Disputed' THEN 1 END) AS disputed_count,\n        COUNT(CASE WHEN ad.adjustment_status = 'Resolved' THEN 1 END) AS resolved_count\n    FROM adjustment_details ad\n    GROUP BY ad.adjustment_type\n),\ncarrier_adjustment_patterns AS (\n    -- Third CTE: Analyze adjustment patterns by carrier\n    SELECT\n        ad.carrier_id,\n        c.carrier_name,\n        ad.adjustment_type,\n        COUNT(*) AS adjustment_count,\n        SUM(ABS(ad.adjustment_amount)) AS total_adjustment_amount,\n        AVG(ABS(ad.adjustment_amount)) AS avg_adjustment_amount,\n        COUNT(CASE WHEN ad.adjustment_status = 'Disputed' THEN 1 END) AS disputed_count,\n        COUNT(CASE WHEN ad.adjustment_status = 'Resolved' THEN 1 END) AS resolved_count\n    FROM adjustment_details ad\n    INNER JOIN shipping_carriers c ON ad.carrier_id = c.carrier_id\n    GROUP BY ad.carrier_id, c.carrier_name, ad.adjustment_type\n),\ndiscrepancy_analysis AS (\n    -- Fourth CTE: Analyze discrepancies and identify root causes\n    SELECT\n        ad.adjustment_id,\n        ad.adjustment_type,\n        ad.adjustment_amount,\n        ad.adjustment_reason,\n        ad.carrier_id,\n        ad.declared_weight_lbs,\n        ad.declared_length_inches,\n        ad.declared_width_inches,\n        ad.declared_height_inches,\n        CASE\n            WHEN ad.adjustment_type = 'Weight' AND ad.adjustment_amount > 0 THEN 'Weight Under-declared'\n            WHEN ad.adjustment_type = 'Weight' AND ad.adjustment_amount < 0 THEN 'Weight Over-declared'\n            WHEN ad.adjustment_type = 'Dimensions' AND ad.adjustment_amount > 0 THEN 'Dimensions Under-declared'\n            WHEN ad.adjustment_type = 'Dimensions' AND ad.adjustment_amount < 0 THEN 'Dimensions Over-declared'\n            WHEN ad.adjustment_type = 'Zone' AND ad.adjustment_amount > 0 THEN 'Zone Under-calculated'\n            WHEN ad.adjustment_type = 'Zone' AND ad.adjustment_amount < 0 THEN 'Zone Over-calculated'\n            ELSE 'Other Discrepancy'\n        END AS discrepancy_category,\n        CASE\n            WHEN ABS(ad.adjustment_amount) > ad.original_shipment_cost * 0.1 THEN 'High Impact'\n            WHEN ABS(ad.adjustment_amount) > ad.original_shipment_cost * 0.05 THEN 'Medium Impact'\n            ELSE 'Low Impact'\n        END AS impact_level\n    FROM adjustment_details ad\n),\ncost_recovery_opportunities AS (\n    -- Fifth CTE: Identify cost recovery opportunities\n    SELECT\n        da.adjustment_type,\n        da.discrepancy_category,\n        COUNT(*) AS discrepancy_count,\n        SUM(ABS(da.adjustment_amount)) AS total_recoverable_amount,\n        AVG(ABS(da.adjustment_amount)) AS avg_recoverable_amount,\n        COUNT(CASE WHEN da.adjustment_status = 'Disputed' THEN 1 END) AS disputed_count,\n        COUNT(CASE WHEN da.adjustment_status = 'Resolved' AND da.adjustment_amount < 0 THEN 1 END) AS successful_recoveries\n    FROM discrepancy_analysis da\n    GROUP BY da.adjustment_type, da.discrepancy_category\n)\nSELECT\n    as_stats.adjustment_type,\n    as_stats.total_adjustments,\n    as_stats.total_adjustment_amount,\n    as_stats.avg_adjustment_amount,\n    as_stats.median_adjustment_amount,\n    as_stats.applied_count,\n    as_stats.disputed_count,\n    as_stats.resolved_count,\n    cro.discrepancy_category,\n    cro.total_recoverable_amount,\n    cro.avg_recoverable_amount,\n    cro.successful_recoveries,\n    CASE\n        WHEN as_stats.total_adjustments > 0\n        THEN as_stats.disputed_count::numeric / as_stats.total_adjustments * 100\n        ELSE 0\n    END AS dispute_rate_percentage,\n    CASE\n        WHEN cro.discrepancy_count > 0\n        THEN cro.successful_recoveries::numeric / cro.discrepancy_count * 100\n        ELSE 0\n    END AS recovery_success_rate_percentage\nFROM adjustment_statistics as_stats\nLEFT JOIN cost_recovery_opportunities cro ON as_stats.adjustment_type = cro.adjustment_type\nORDER BY as_stats.total_adjustment_amount DESC;",
  "evidence": "The finance team has noticed an increase in shipping adjustments and billing discrepancies that result in revenue leakage. Adjustment records across shipments capture discrepancy types, amounts, and reasons, which need systematic analysis to recover costs and prevent future issues. Analyze shipping adjustments to categorize adjustment types, detect patterns in discrepancies, quantify cost recovery opportunities, identify root causes, and generate prevention recommendations. The query joins shipment records with adjustment transactions and billing data, groups by adjustment type, carrier, and time period, computes aggregate adjustment amounts and frequencies, calculates quartiles to identify outlier adjustments, uses window functions to track adjustment trends over time and compare carrier performance, detects patterns through correlation analysis, and handles edge cases including reversed adjustments and NULL reason codes. Returns a detailed dataset con",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipping_adjustments",
    "shipments",
    "packages",
    "adjustment_details",
    "shipping_carriers",
    "discrepancy_analysis",
    "adjustment_statistics",
    "cost_recovery_opportunities"
  ],
  "schema_context": {},
  "expected_output": "Shipping adjustment analysis showing adjustment types, discrepancy patterns, cost recovery opportunities, and prevention recommendations.",
  "normal_query": "Shipping adjustment and discrepancy analysis showing adjustment types, pattern detection, root cause identification, cost recovery opportunities, and prevention recommendations."
}
```

### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 9,
  "question": "Show me API rate request performance analysis with optimization recommendations.",
  "SQL": "WITH api_request_details AS (\n    -- First CTE: Get detailed API request information\n    SELECT\n        arl.log_id,\n        arl.carrier_id,\n        c.carrier_name,\n        arl.request_type,\n        arl.origin_zip_code,\n        arl.destination_zip_code,\n        arl.weight_lbs,\n        arl.request_timestamp,\n        arl.response_time_ms,\n        arl.response_status_code,\n        arl.rate_returned,\n        arl.error_message,\n        arl.api_endpoint,\n        DATE(arl.request_timestamp) AS request_date,\n        EXTRACT(HOUR FROM arl.request_timestamp) AS request_hour\n    FROM api_rate_request_log arl\n    INNER JOIN shipping_carriers c ON arl.carrier_id = c.carrier_id\n),\napi_performance_metrics AS (\n    -- Second CTE: Calculate API performance metrics\n    SELECT\n        ard.carrier_id,\n        ard.carrier_name,\n        ard.request_type,\n        COUNT(*) AS total_requests,\n        COUNT(CASE WHEN ard.response_status_code = 200 THEN 1 END) AS successful_requests,\n        COUNT(CASE WHEN ard.response_status_code != 200 OR ard.error_message IS NOT NULL THEN 1 END) AS failed_requests,\n        AVG(ard.response_time_ms) AS avg_response_time_ms,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ard.response_time_ms) AS median_response_time_ms,\n        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ard.response_time_ms) AS p95_response_time_ms,\n        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY ard.response_time_ms) AS p99_response_time_ms,\n        MIN(ard.response_time_ms) AS min_response_time_ms,\n        MAX(ard.response_time_ms) AS max_response_time_ms,\n        STDDEV(ard.response_time_ms) AS stddev_response_time_ms,\n        CASE\n            WHEN COUNT(*) > 0\n            THEN COUNT(CASE WHEN ard.response_status_code = 200 THEN 1 END)::numeric / COUNT(*) * 100\n            ELSE 0\n        END AS success_rate_percentage\n    FROM api_request_details ard\n    GROUP BY ard.carrier_id, ard.carrier_name, ard.request_type\n),\nhourly_performance_patterns AS (\n    -- Third CTE: Analyze hourly performance patterns\n    SELECT\n        ard.carrier_id,\n        ard.request_hour,\n        COUNT(*) AS request_count,\n        AVG(ard.response_time_ms) AS avg_response_time_ms,\n        COUNT(CASE WHEN ard.response_status_code != 200 OR ard.error_message IS NOT NULL THEN 1 END) AS error_count,\n        CASE\n            WHEN COUNT(*) > 0\n            THEN COUNT(CASE WHEN ard.response_status_code != 200 OR ard.error_message IS NOT NULL THEN 1 END)::numeric / COUNT(*) * 100\n            ELSE 0\n        END AS error_rate_percentage\n    FROM api_request_details ard\n    GROUP BY ard.carrier_id, ard.request_hour\n),\nerror_pattern_analysis AS (\n    -- Fourth CTE: Analyze error patterns\n    SELECT\n        ard.carrier_id,\n        ard.carrier_name,\n        ard.error_message,\n        COUNT(*) AS error_count,\n        AVG(ard.response_time_ms) AS avg_response_time_on_error_ms,\n        COUNT(DISTINCT ard.origin_zip_code) AS affected_origin_zips,\n        COUNT(DISTINCT ard.destination_zip_code) AS affected_destination_zips\n    FROM api_request_details ard\n    WHERE ard.response_status_code != 200 OR ard.error_message IS NOT NULL\n    GROUP BY ard.carrier_id, ard.carrier_name, ard.error_message\n),\noptimization_recommendations AS (\n    -- Fifth CTE: Generate optimization recommendations\n    SELECT\n        apm.carrier_id,\n        apm.carrier_name,\n        apm.request_type,\n        apm.total_requests,\n        apm.success_rate_percentage,\n        apm.avg_response_time_ms,\n        apm.p95_response_time_ms,\n        CASE\n            WHEN apm.success_rate_percentage < 95 THEN 'Improve Error Handling'\n            WHEN apm.p95_response_time_ms > 2000 THEN 'Optimize Response Time'\n            WHEN apm.avg_response_time_ms > 1000 THEN 'Consider Caching'\n            ELSE 'Performance Optimal'\n        END AS optimization_recommendation,\n        CASE\n            WHEN apm.p95_response_time_ms > 2000 THEN apm.p95_response_time_ms - 1000\n            ELSE 0\n        END AS potential_time_savings_ms\n    FROM api_performance_metrics apm\n)\nSELECT\n        or_rec.carrier_name,\n        or_rec.request_type,\n        or_rec.total_requests,\n        or_rec.success_rate_percentage,\n        or_rec.avg_response_time_ms,\n        or_rec.p95_response_time_ms,\n        or_rec.optimization_recommendation,\n        or_rec.potential_time_savings_ms,\n        hpp.request_hour AS peak_error_hour,\n        hpp.error_rate_percentage AS peak_error_rate,\n        epa.error_message AS most_common_error,\n        epa.error_count AS most_common_error_count,\n        ROW_NUMBER() OVER (ORDER BY or_rec.avg_response_time_ms DESC) AS performance_rank\nFROM optimization_recommendations or_rec\nLEFT JOIN LATERAL (\n    SELECT request_hour, error_rate_percentage\n    FROM hourly_performance_patterns hpp\n    WHERE hpp.carrier_id = or_rec.carrier_id\n    ORDER BY hpp.error_rate_percentage DESC\n    LIMIT 1\n) hpp ON TRUE\nLEFT JOIN LATERAL (\n    SELECT error_message, error_count\n    FROM error_pattern_analysis epa\n    WHERE epa.carrier_id = or_rec.carrier_id\n    ORDER BY epa.error_count DESC\n    LIMIT 1\n) epa ON TRUE\nORDER BY or_rec.avg_response_time_ms DESC;",
  "evidence": "The engineering team supports shipping rate APIs that serve real-time quotes to customers and internal systems. Recent performance degradation has impacted user experience, and API request logs contain response times, error codes, and usage patterns that need analysis to identify bottlenecks and optimization opportunities. Analyze API rate request performance to measure response times, calculate error rates, identify performance bottlenecks, detect usage patterns, and generate optimization recommendations to improve reliability and speed. The query aggregates API request logs, groups by endpoint, carrier integration, and time intervals, computes percentile metrics for response times (p50, p95, p99), calculates error rates by error type and endpoint, uses window functions to track performance trends over rolling windows and identify degradation patterns, correlates slow responses with carrier APIs or data volume, and handles NULL values in optional request param",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "arl",
    "api_rate_request_log",
    "shipping_carriers",
    "api_request_details",
    "api_performance_metrics",
    "optimization_recommendations",
    "lateral",
    "hourly_performance_patterns",
    "error_pattern_analysis"
  ],
  "schema_context": {},
  "expected_output": "API performance analysis showing response times, error rates, optimization opportunities, and performance recommendations.",
  "normal_query": "API performance monitoring analysis displaying response times, error rates, throughput metrics, bottleneck identification, and optimization recommendations for rate request APIs."
}
```

### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 10,
  "question": "Show me a comprehensive shipping analytics dashboard with revenue trends and performance metrics.",
  "SQL": "WITH daily_shipment_summary AS (\n    -- First CTE: Daily shipment summaries\n    SELECT\n        DATE(s.created_at) AS shipment_date,\n        s.carrier_id,\n        s.service_id,\n        COUNT(*) AS shipment_count,\n        SUM(s.total_cost) AS total_revenue,\n        AVG(s.total_cost) AS avg_shipment_cost,\n        COUNT(CASE WHEN s.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        COUNT(CASE WHEN s.shipment_status IN ('Exception', 'Returned') THEN 1 END) AS exception_count,\n        AVG(p.weight_lbs) AS avg_weight_lbs\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n    GROUP BY DATE(s.created_at), s.carrier_id, s.service_id\n),\nrevenue_trend_analysis AS (\n    -- Second CTE: Revenue trend analysis\n    SELECT\n        dss.shipment_date,\n        SUM(dss.total_revenue) AS daily_revenue,\n        SUM(dss.shipment_count) AS daily_shipments,\n        AVG(dss.avg_shipment_cost) AS daily_avg_cost,\n        LAG(SUM(dss.total_revenue)) OVER (ORDER BY dss.shipment_date) AS previous_day_revenue,\n        LAG(SUM(dss.total_revenue), 7) OVER (ORDER BY dss.shipment_date) AS week_ago_revenue,\n        LAG(SUM(dss.total_revenue), 30) OVER (ORDER BY dss.shipment_date) AS month_ago_revenue,\n        AVG(SUM(dss.total_revenue)) OVER (ORDER BY dss.shipment_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS seven_day_avg_revenue,\n        AVG(SUM(dss.total_revenue)) OVER (ORDER BY dss.shipment_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS thirty_day_avg_revenue\n    FROM daily_shipment_summary dss\n    GROUP BY dss.shipment_date\n),\ncarrier_performance_summary AS (\n    -- Third CTE: Carrier performance summary\n    SELECT\n        dss.carrier_id,\n        c.carrier_name,\n        SUM(dss.total_revenue) AS total_revenue,\n        SUM(dss.shipment_count) AS total_shipments,\n        AVG(dss.avg_shipment_cost) AS avg_shipment_cost,\n        SUM(dss.delivered_count) AS total_delivered,\n        SUM(dss.exception_count) AS total_exceptions,\n        CASE\n            WHEN SUM(dss.shipment_count) > 0\n            THEN SUM(dss.delivered_count)::numeric / SUM(dss.shipment_count) * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        CASE\n            WHEN SUM(dss.shipment_count) > 0\n            THEN SUM(dss.exception_count)::numeric / SUM(dss.shipment_count) * 100\n            ELSE 0\n        END AS exception_rate\n    FROM daily_shipment_summary dss\n    INNER JOIN shipping_carriers c ON dss.carrier_id = c.carrier_id\n    GROUP BY dss.carrier_id, c.carrier_name\n),\nservice_performance_summary AS (\n    -- Fourth CTE: Service performance summary\n    SELECT\n        dss.service_id,\n        st.service_name,\n        st.service_category,\n        SUM(dss.total_revenue) AS total_revenue,\n        SUM(dss.shipment_count) AS total_shipments,\n        AVG(dss.avg_shipment_cost) AS avg_shipment_cost,\n        SUM(dss.delivered_count) AS total_delivered,\n        CASE\n            WHEN SUM(dss.shipment_count) > 0\n            THEN SUM(dss.delivered_count)::numeric / SUM(dss.shipment_count) * 100\n            ELSE 0\n        END AS delivery_success_rate\n    FROM daily_shipment_summary dss\n    INNER JOIN shipping_service_types st ON dss.service_id = st.service_id\n    GROUP BY dss.service_id, st.service_name, st.service_category\n),\nrevenue_growth_metrics AS (\n    -- Fifth CTE: Calculate revenue growth metrics\n    SELECT\n        rta.shipment_date,\n        rta.daily_revenue,\n        rta.daily_shipments,\n        rta.daily_avg_cost,\n        rta.previous_day_revenue,\n        rta.week_ago_revenue,\n        rta.month_ago_revenue,\n        rta.seven_day_avg_revenue,\n        rta.thirty_day_avg_revenue,\n        CASE\n            WHEN rta.previous_day_revenue > 0\n            THEN ((rta.daily_revenue - rta.previous_day_revenue) / rta.previous_day_revenue * 100)\n            ELSE 0\n        END AS day_over_day_growth_percentage,\n        CASE\n            WHEN rta.week_ago_revenue > 0\n            THEN ((rta.daily_revenue - rta.week_ago_revenue) / rta.week_ago_revenue * 100)\n            ELSE 0\n        END AS week_over_week_growth_percentage,\n        CASE\n            WHEN rta.month_ago_revenue > 0\n            THEN ((rta.daily_revenue - rta.month_ago_revenue) / rta.month_ago_revenue * 100)\n            ELSE 0\n        END AS month_over_month_growth_percentage\n    FROM revenue_trend_analysis rta\n),\ndashboard_summary AS (\n    -- Sixth CTE: Aggregate dashboard summary\n    SELECT\n        rgm.shipment_date,\n        rgm.daily_revenue,\n        rgm.daily_shipments,\n        rgm.daily_avg_cost,\n        rgm.day_over_day_growth_percentage,\n        rgm.week_over_week_growth_percentage,\n        rgm.month_over_month_growth_percentage,\n        rgm.seven_day_avg_revenue,\n        rgm.thirty_day_avg_revenue,\n        (SELECT SUM(total_revenue) FROM carrier_performance_summary) AS total_revenue_all_carriers,\n        (SELECT SUM(total_shipments) FROM carrier_performance_summary) AS total_shipments_all_carriers,\n        (SELECT carrier_name FROM carrier_performance_summary ORDER BY total_revenue DESC LIMIT 1) AS top_carrier_by_revenue,\n        (SELECT service_name FROM service_performance_summary ORDER BY total_revenue DESC LIMIT 1) AS top_service_by_revenue\n    FROM revenue_growth_metrics rgm\n)\nSELECT\n    ds.shipment_date,\n    ds.daily_revenue,\n    ds.daily_shipments,\n    ds.daily_avg_cost,\n    ds.day_over_day_growth_percentage,\n    ds.week_over_week_growth_percentage,\n    ds.month_over_month_growth_percentage,\n    ds.seven_day_avg_revenue,\n    ds.thirty_day_avg_revenue,\n    ds.total_revenue_all_carriers,\n    ds.total_shipments_all_carriers,\n    ds.top_carrier_by_revenue,\n    ds.top_service_by_revenue,\n    CASE\n        WHEN ds.day_over_day_growth_percentage > 5 THEN 'Strong Growth'\n        WHEN ds.day_over_day_growth_percentage > 0 THEN 'Moderate Growth'\n        WHEN ds.day_over_day_growth_percentage > -5 THEN 'Stable'\n        ELSE 'Declining'\n    END AS growth_category\nFROM dashboard_summary ds\nORDER BY ds.shipment_date DESC\nLIMIT 30;",
  "evidence": "Executive leadership requires a comprehensive view of shipping operations to make strategic decisions about carrier partnerships, pricing strategies, and operational investments. Data across shipments, carriers, routes, and financial transactions contains the metrics needed to assess business performance and identify growth opportunities. Build a comprehensive analytics dashboard showing revenue trends over time, shipment volume patterns, carrier performance comparisons, cost efficiency metrics, profitability analysis, and key business intelligence insights to support strategic decision-making. The query joins shipments with carrier performance data, financial transactions, and route information, groups by time period, carrier, service level, and region, computes aggregate metrics including revenue, shipment volumes, average costs, and profit margins, calculates growth rates and year-over-year comparisons, uses window functions for trend analysis including movi",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "daily_shipment_summary",
    "shipping_carriers",
    "shipping_service_types",
    "revenue_trend_analysis",
    "carrier_performance_summary",
    "service_performance_summary",
    "revenue_growth_metrics",
    "dashboard_summary"
  ],
  "schema_context": {},
  "expected_output": "Shipping analytics dashboard showing revenue trends, shipment volumes, performance metrics, and business intelligence insights.",
  "normal_query": "Executive shipping analytics dashboard displaying revenue trends, shipment volume analysis, carrier performance metrics, cost efficiency indicators, and key business intelligence insights."
}
```

### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 11,
  "question": "Can you show me the dimensional weight optimization analysis along with recommended package configurations?",
  "SQL": "WITH package_dimension_analysis AS (\n    -- First CTE: Analyze package dimensions and calculate dimensional weights\n    SELECT\n        p.package_id,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches,\n        p.length_inches * p.width_inches * p.height_inches AS cubic_volume_cubic_inches,\n        p.length_inches * p.width_inches * p.height_inches / 166.0 AS dimensional_weight_lbs,\n        CASE\n            WHEN p.length_inches * p.width_inches * p.height_inches / 166.0 > p.weight_lbs\n            THEN p.length_inches * p.width_inches * p.height_inches / 166.0\n            ELSE p.weight_lbs\n        END AS billable_weight_lbs,\n        CASE\n            WHEN p.length_inches * p.width_inches * p.height_inches / 166.0 > p.weight_lbs THEN TRUE\n            ELSE FALSE\n        END AS dimensional_weight_applies\n    FROM packages p\n),\ndimensional_weight_impact AS (\n    -- Second CTE: Calculate dimensional weight impact on shipping costs\n    SELECT\n        pda.package_id,\n        pda.weight_lbs,\n        pda.dimensional_weight_lbs,\n        pda.billable_weight_lbs,\n        pda.dimensional_weight_applies,\n        pda.billable_weight_lbs - pda.weight_lbs AS weight_premium_lbs,\n        s.shipment_id,\n        s.total_cost AS actual_cost,\n        (SELECT MIN(sr.total_rate)\n         FROM shipping_rates sr\n         WHERE sr.carrier_id = s.carrier_id\n             AND sr.service_id = s.service_id\n             AND sr.weight_lbs >= pda.weight_lbs\n             AND (sr.expiration_date IS NULL OR sr.expiration_date >= CURRENT_DATE)\n             AND sr.effective_date <= CURRENT_DATE\n         LIMIT 1) AS cost_at_actual_weight,\n        (SELECT MIN(sr.total_rate)\n         FROM shipping_rates sr\n         WHERE sr.carrier_id = s.carrier_id\n             AND sr.service_id = s.service_id\n             AND sr.weight_lbs >= pda.billable_weight_lbs\n             AND (sr.expiration_date IS NULL OR sr.expiration_date >= CURRENT_DATE)\n             AND sr.effective_date <= CURRENT_DATE\n         LIMIT 1) AS cost_at_billable_weight\n    FROM package_dimension_analysis pda\n    INNER JOIN shipments s ON pda.package_id = s.package_id\n    WHERE s.shipment_status = 'Delivered'\n),\noptimization_opportunities AS (\n    -- Third CTE: Identify optimization opportunities\n    SELECT\n        dwi.package_id,\n        dwi.weight_lbs,\n        dwi.dimensional_weight_lbs,\n        dwi.billable_weight_lbs,\n        dwi.dimensional_weight_applies,\n        dwi.weight_premium_lbs,\n        dwi.actual_cost,\n        dwi.cost_at_actual_weight,\n        dwi.cost_at_billable_weight,\n        dwi.cost_at_billable_weight - dwi.cost_at_actual_weight AS dimensional_weight_cost_impact,\n        CASE\n            WHEN dwi.dimensional_weight_applies = TRUE AND dwi.weight_premium_lbs > 1.0 THEN 'High Optimization Potential'\n            WHEN dwi.dimensional_weight_applies = TRUE AND dwi.weight_premium_lbs > 0.5 THEN 'Moderate Optimization Potential'\n            WHEN dwi.dimensional_weight_applies = TRUE THEN 'Low Optimization Potential'\n            ELSE 'No Optimization Needed'\n        END AS optimization_category\n    FROM dimensional_weight_impact dwi\n),\npackage_configuration_recommendations AS (\n    -- Fourth CTE: Generate package configuration recommendations\n    SELECT\n        oo.package_id,\n        oo.weight_lbs,\n        oo.dimensional_weight_lbs,\n        oo.billable_weight_lbs,\n        oo.dimensional_weight_applies,\n        oo.dimensional_weight_cost_impact,\n        oo.optimization_category,\n        CASE\n            WHEN oo.dimensional_weight_applies = TRUE THEN\n                SQRT((oo.billable_weight_lbs * 166.0) / (oo.weight_lbs * 1.1)) * \n                POWER(oo.billable_weight_lbs * 166.0 / (oo.weight_lbs * 1.1), 1.0/3.0)\n            ELSE NULL\n        END AS recommended_max_dimension_inches,\n        oo.dimensional_weight_cost_impact * 0.5 AS potential_cost_savings\n    FROM optimization_opportunities oo\n)\nSELECT\n    pcr.package_id,\n    pcr.weight_lbs,\n    pcr.dimensional_weight_lbs,\n    pcr.billable_weight_lbs,\n    pcr.dimensional_weight_applies,\n    pcr.dimensional_weight_cost_impact,\n    pcr.optimization_category,\n    pcr.recommended_max_dimension_inches,\n    pcr.potential_cost_savings,\n    ROW_NUMBER() OVER (ORDER BY pcr.dimensional_weight_cost_impact DESC) AS optimization_priority_rank\nFROM package_configuration_recommendations pcr\nWHERE pcr.dimensional_weight_applies = TRUE\nORDER BY pcr.dimensional_weight_cost_impact DESC;",
  "evidence": "The logistics team is evaluating packaging efficiency to reduce shipping costs. Current packages may not be optimized for dimensional weight pricing used by carriers, leading to unnecessary surcharges. The shipments table contains package dimensions and weights, while carriers table has dimensional weight divisors and pricing rules. Analyze dimensional weight optimization opportunities and recommend optimal package configurations that minimize costs. The query calculates actual weight versus dimensional weight (length \u00d7 width \u00d7 height / divisor) for each package type, groups shipments by package configuration, computes cost differences between actual and optimized scenarios, uses window functions to rank package configurations by savings potential, and identifies quartiles of cost savings across different package types. Returns a dataset showing current package configurations, recommended optimized dimensions, projected cost savings per configuration, a",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "packages",
    "shipping_rates",
    "package_dimension_analysis",
    "shipments",
    "dimensional_weight_impact",
    "optimization_opportunities",
    "package_configuration_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Dimensional weight optimization results showing recommended package configurations and cost savings potential.",
  "normal_query": "Show dimensional weight optimization results with recommended package configurations and potential cost savings."
}
```

### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 12,
  "question": "Can you provide a shipping zone coverage analysis that identifies geographic gaps in our service areas?",
  "SQL": "WITH RECURSIVE zone_coverage_map AS (\n    -- Anchor: Base zone coverage\n    SELECT\n        z.zone_id,\n        z.carrier_id,\n        z.origin_zip_code,\n        z.destination_zip_code,\n        z.zone_number,\n        SUBSTRING(z.origin_zip_code, 1, 3) AS origin_zip_prefix,\n        SUBSTRING(z.destination_zip_code, 1, 3) AS destination_zip_prefix,\n        1 AS coverage_level\n    FROM shipping_zones z\n    WHERE z.zone_type = 'Domestic'\n        AND (z.expiration_date IS NULL OR z.expiration_date >= CURRENT_DATE)\n    UNION ALL\n    -- Recursive: Expand coverage to adjacent zones\n    SELECT\n        z.zone_id,\n        z.carrier_id,\n        z.origin_zip_code,\n        z.destination_zip_code,\n        z.zone_number,\n        SUBSTRING(z.origin_zip_code, 1, 3) AS origin_zip_prefix,\n        SUBSTRING(z.destination_zip_code, 1, 3) AS destination_zip_prefix,\n        zcm.coverage_level + 1\n    FROM shipping_zones z\n    INNER JOIN zone_coverage_map zcm ON z.carrier_id = zcm.carrier_id\n        AND ABS(z.zone_number - zcm.zone_number) <= 1\n    WHERE zcm.coverage_level < 3\n),\nzip_prefix_coverage AS (\n    -- Calculate coverage by ZIP prefix\n    SELECT\n        zcm.origin_zip_prefix,\n        zcm.destination_zip_prefix,\n        zcm.carrier_id,\n        COUNT(DISTINCT zcm.zone_id) AS zone_count,\n        COUNT(DISTINCT zcm.zone_number) AS unique_zone_numbers,\n        AVG(zcm.zone_number) AS avg_zone_number,\n        MIN(zcm.zone_number) AS min_zone_number,\n        MAX(zcm.zone_number) AS max_zone_number\n    FROM zone_coverage_map zcm\n    GROUP BY zcm.origin_zip_prefix, zcm.destination_zip_prefix, zcm.carrier_id\n),\ncoverage_gaps AS (\n    -- Identify coverage gaps\n    SELECT\n        opc.origin_zip_prefix,\n        opc.destination_zip_prefix,\n        opc.carrier_id,\n        opc.zone_count,\n        opc.unique_zone_numbers,\n        opc.avg_zone_number,\n        CASE\n            WHEN opc.zone_count = 0 THEN 'No Coverage'\n            WHEN opc.zone_count < 3 THEN 'Limited Coverage'\n            WHEN opc.max_zone_number - opc.min_zone_number > 5 THEN 'High Zone Variance'\n            ELSE 'Good Coverage'\n        END AS coverage_category\n    FROM zip_prefix_coverage opc\n),\ncarrier_coverage_comparison AS (\n    -- Compare carrier coverage\n    SELECT\n        cg.origin_zip_prefix,\n        cg.destination_zip_prefix,\n        COUNT(DISTINCT cg.carrier_id) AS carrier_count,\n        STRING_AGG(DISTINCT c.carrier_name, ', ') AS available_carriers,\n        MIN(CASE WHEN cg.coverage_category = 'Good Coverage' THEN 1 ELSE 0 END) AS has_good_coverage,\n        MAX(CASE WHEN cg.coverage_category = 'No Coverage' THEN 1 ELSE 0 END) AS has_no_coverage\n    FROM coverage_gaps cg\n    INNER JOIN shipping_carriers c ON cg.carrier_id = c.carrier_id\n    GROUP BY cg.origin_zip_prefix, cg.destination_zip_prefix\n)\nSELECT\n    ccc.origin_zip_prefix,\n    ccc.destination_zip_prefix,\n    ccc.carrier_count,\n    ccc.available_carriers,\n    ccc.has_good_coverage,\n    ccc.has_no_coverage,\n    CASE\n        WHEN ccc.has_no_coverage = 1 THEN 'Coverage Gap Identified'\n        WHEN ccc.carrier_count = 1 THEN 'Single Carrier Coverage'\n        WHEN ccc.has_good_coverage = 1 THEN 'Good Coverage'\n        ELSE 'Limited Coverage'\n    END AS coverage_status,\n    COUNT(*) OVER (PARTITION BY ccc.origin_zip_prefix) AS destination_count_for_origin,\n    COUNT(*) OVER (PARTITION BY ccc.destination_zip_prefix) AS origin_count_for_destination\nFROM carrier_coverage_comparison ccc\nORDER BY ccc.has_no_coverage DESC, ccc.carrier_count ASC;",
  "evidence": "The operations team needs to assess current shipping zone coverage to identify underserved geographic areas and expansion opportunities. The routes table contains zone definitions and service areas, shipments table has destination data, and carriers table shows service capabilities. Some zones may have poor coverage leading to higher costs or longer delivery times. Analyze zone coverage patterns to identify geographic gaps, underutilized routes, and opportunities for service optimization. The query groups shipments by geographic zone and carrier, calculates coverage metrics including shipment density per zone, identifies zones with sparse coverage or no service, uses window functions to compare zone performance against regional averages, computes distance and cost metrics for underserved areas, and handles NULL values for zones without historical shipment data. Returns coverage metrics per zone including shipment volume, average delivery time, cost per ",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipping_zones",
    "zone_coverage_map",
    "zip_prefix_coverage",
    "coverage_gaps",
    "shipping_carriers",
    "carrier_coverage_comparison"
  ],
  "schema_context": {},
  "expected_output": "Zone coverage analysis showing coverage gaps, optimization opportunities, and route recommendations.",
  "normal_query": "Display zone coverage analysis highlighting coverage gaps, optimization opportunities, and recommended route expansions."
}
```

### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 13,
  "question": "Can you show me the shipping rate volatility analysis with price trend predictions?",
  "SQL": "WITH rate_history_analysis AS (\n    -- First CTE: Analyze rate history over time\n    SELECT\n        sr.rate_id,\n        sr.carrier_id,\n        sr.service_id,\n        sr.weight_lbs,\n        sr.rate_amount,\n        sr.total_rate,\n        sr.effective_date,\n        sr.expiration_date,\n        DATE_DIFF('day', sr.effective_date, COALESCE(sr.expiration_date, CURRENT_DATE)) AS rate_duration_days,\n        LAG(sr.total_rate) OVER (PARTITION BY sr.carrier_id, sr.service_id, sr.weight_lbs ORDER BY sr.effective_date) AS previous_rate,\n        LEAD(sr.total_rate) OVER (PARTITION BY sr.carrier_id, sr.service_id, sr.weight_lbs ORDER BY sr.effective_date) AS next_rate\n    FROM shipping_rates sr\n    WHERE sr.effective_date >= CURRENT_DATE - INTERVAL '365 days'\n),\nrate_changes AS (\n    -- Second CTE: Calculate rate changes\n    SELECT\n        rha.carrier_id,\n        rha.service_id,\n        rha.weight_lbs,\n        rha.effective_date,\n        rha.total_rate,\n        rha.previous_rate,\n        rha.next_rate,\n        CASE\n            WHEN rha.previous_rate IS NOT NULL\n            THEN rha.total_rate - rha.previous_rate\n            ELSE 0\n        END AS rate_change_amount,\n        CASE\n            WHEN rha.previous_rate IS NOT NULL AND rha.previous_rate > 0\n            THEN ((rha.total_rate - rha.previous_rate) / rha.previous_rate * 100)\n            ELSE 0\n        END AS rate_change_percentage,\n        CASE\n            WHEN rha.next_rate IS NOT NULL\n            THEN rha.next_rate - rha.total_rate\n            ELSE 0\n        END AS next_rate_change_amount\n    FROM rate_history_analysis rha\n),\nvolatility_metrics AS (\n    -- Third CTE: Calculate volatility metrics\n    SELECT\n        rc.carrier_id,\n        rc.service_id,\n        rc.weight_lbs,\n        COUNT(*) AS rate_change_count,\n        AVG(ABS(rc.rate_change_percentage)) AS avg_absolute_change_percentage,\n        STDDEV(rc.rate_change_percentage) AS rate_volatility,\n        MAX(ABS(rc.rate_change_percentage)) AS max_change_percentage,\n        COUNT(CASE WHEN rc.rate_change_percentage > 0 THEN 1 END) AS rate_increase_count,\n        COUNT(CASE WHEN rc.rate_change_percentage < 0 THEN 1 END) AS rate_decrease_count,\n        AVG(rc.total_rate) AS avg_rate,\n        MIN(rc.total_rate) AS min_rate,\n        MAX(rc.total_rate) AS max_rate\n    FROM rate_changes rc\n    WHERE rc.rate_change_amount != 0\n    GROUP BY rc.carrier_id, rc.service_id, rc.weight_lbs\n),\ntrend_analysis AS (\n    -- Fourth CTE: Analyze rate trends\n    SELECT\n        vm.carrier_id,\n        vm.service_id,\n        vm.weight_lbs,\n        vm.rate_volatility,\n        vm.avg_rate,\n        vm.min_rate,\n        vm.max_rate,\n        CASE\n            WHEN vm.rate_increase_count > vm.rate_decrease_count * 1.5 THEN 'Increasing Trend'\n            WHEN vm.rate_decrease_count > vm.rate_increase_count * 1.5 THEN 'Decreasing Trend'\n            ELSE 'Stable Trend'\n        END AS rate_trend,\n        CASE\n            WHEN vm.rate_volatility > 10 THEN 'High Volatility'\n            WHEN vm.rate_volatility > 5 THEN 'Moderate Volatility'\n            ELSE 'Low Volatility'\n        END AS volatility_category\n    FROM volatility_metrics vm\n),\nrate_prediction AS (\n    -- Fifth CTE: Predict future rate changes\n    SELECT\n        ta.carrier_id,\n        c.carrier_name,\n        ta.service_id,\n        st.service_name,\n        ta.weight_lbs,\n        ta.avg_rate,\n        ta.min_rate,\n        ta.max_rate,\n        ta.rate_trend,\n        ta.volatility_category,\n        ta.rate_volatility,\n        CASE\n            WHEN ta.rate_trend = 'Increasing Trend' THEN ta.avg_rate * 1.05\n            WHEN ta.rate_trend = 'Decreasing Trend' THEN ta.avg_rate * 0.95\n            ELSE ta.avg_rate\n        END AS predicted_next_rate,\n        ta.avg_rate - ta.min_rate AS potential_savings_from_min_rate\n    FROM trend_analysis ta\n    INNER JOIN shipping_carriers c ON ta.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON ta.service_id = st.service_id\n)\nSELECT\n    rp.carrier_name,\n    rp.service_name,\n    rp.weight_lbs,\n    rp.avg_rate,\n    rp.min_rate,\n    rp.max_rate,\n    rp.rate_trend,\n    rp.volatility_category,\n    rp.predicted_next_rate,\n    rp.potential_savings_from_min_rate,\n    CASE\n        WHEN rp.rate_trend = 'Increasing Trend' AND rp.volatility_category = 'High Volatility' THEN 'Consider Locking Rates'\n        WHEN rp.rate_trend = 'Decreasing Trend' THEN 'Wait for Lower Rates'\n        ELSE 'Monitor Closely'\n    END AS optimization_recommendation\nFROM rate_prediction rp\nORDER BY rp.rate_volatility DESC, rp.potential_savings_from_min_rate DESC;",
  "evidence": "Finance and procurement teams are concerned about shipping cost fluctuations affecting budget predictability. The carriers table contains historical rate data, shipments table has actual costs paid over time, and routes table includes lane-specific pricing. Rate volatility varies by carrier, season, and route, making cost forecasting challenging. Analyze shipping rate volatility patterns and generate price trend predictions to support budgeting and carrier negotiation strategies. The query aggregates shipping costs by carrier and route over time, calculates volatility metrics including standard deviation and coefficient of variation, uses window functions to compute rolling averages and period-over-period rate changes, identifies seasonal patterns and anomalies in pricing, performs quartile analysis to categorize rate stability, and handles NULL values in historical rate data using appropriate imputation. Returns volatility metrics per carrier and route",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipping_rates",
    "rate_history_analysis",
    "rate_changes",
    "volatility_metrics",
    "trend_analysis",
    "shipping_carriers",
    "shipping_service_types",
    "rate_prediction"
  ],
  "schema_context": {},
  "expected_output": "Rate volatility analysis showing price trends, volatility metrics, and optimization recommendations.",
  "normal_query": "Present rate volatility analysis showing historical price trends, volatility metrics, and cost optimization recommendations."
}
```

### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 14,
  "question": "Can you compare carrier service performance focusing on delivery time analysis?",
  "SQL": "WITH shipment_delivery_metrics AS (\n    -- First CTE: Calculate delivery metrics for each shipment\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.label_created_at,\n        s.estimated_delivery_date,\n        s.actual_delivery_date,\n        s.shipment_status,\n        z.zone_number,\n        z.transit_days_min AS expected_transit_days_min,\n        z.transit_days_max AS expected_transit_days_max,\n        CASE\n            WHEN s.actual_delivery_date IS NOT NULL AND s.label_created_at IS NOT NULL\n            THEN EXTRACT(EPOCH FROM (s.actual_delivery_date - s.label_created_at)) / 86400.0\n            ELSE NULL\n        END AS actual_transit_days,\n        CASE\n            WHEN s.actual_delivery_date IS NOT NULL AND s.estimated_delivery_date IS NOT NULL\n            THEN EXTRACT(EPOCH FROM (s.actual_delivery_date - s.estimated_delivery_date)) / 86400.0\n            ELSE NULL\n        END AS delivery_variance_days\n    FROM shipments s\n    LEFT JOIN shipping_zones z ON s.zone_id = z.zone_id\n    WHERE s.shipment_status IN ('Delivered', 'Exception', 'Returned')\n        AND s.label_created_at IS NOT NULL\n),\ncarrier_service_performance AS (\n    -- Second CTE: Aggregate performance by carrier and service\n    SELECT\n        sdm.carrier_id,\n        sdm.service_id,\n        COUNT(*) AS total_shipments,\n        COUNT(CASE WHEN sdm.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        COUNT(CASE WHEN sdm.shipment_status IN ('Exception', 'Returned') THEN 1 END) AS exception_count,\n        AVG(sdm.actual_transit_days) AS avg_actual_transit_days,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sdm.actual_transit_days) AS median_transit_days,\n        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY sdm.actual_transit_days) AS p95_transit_days,\n        AVG(sdm.delivery_variance_days) AS avg_delivery_variance_days,\n        COUNT(CASE WHEN sdm.delivery_variance_days <= 0 THEN 1 END) AS on_time_deliveries,\n        COUNT(CASE WHEN sdm.delivery_variance_days > 1 THEN 1 END) AS late_deliveries,\n        AVG(sdm.expected_transit_days_min) AS avg_expected_transit_days_min,\n        AVG(sdm.expected_transit_days_max) AS avg_expected_transit_days_max\n    FROM shipment_delivery_metrics sdm\n    WHERE sdm.actual_transit_days IS NOT NULL\n    GROUP BY sdm.carrier_id, sdm.service_id\n),\nperformance_rankings AS (\n    -- Third CTE: Rank carrier-service combinations\n    SELECT\n        csp.carrier_id,\n        c.carrier_name,\n        csp.service_id,\n        st.service_name,\n        csp.total_shipments,\n        csp.delivered_count,\n        csp.exception_count,\n        csp.avg_actual_transit_days,\n        csp.median_transit_days,\n        csp.p95_transit_days,\n        csp.avg_delivery_variance_days,\n        csp.on_time_deliveries,\n        csp.late_deliveries,\n        CASE\n            WHEN csp.total_shipments > 0\n            THEN csp.delivered_count::numeric / csp.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        CASE\n            WHEN csp.total_shipments > 0\n            THEN csp.on_time_deliveries::numeric / csp.total_shipments * 100\n            ELSE 0\n        END AS on_time_delivery_rate,\n        ROW_NUMBER() OVER (ORDER BY csp.avg_actual_transit_days ASC) AS speed_rank,\n        ROW_NUMBER() OVER (ORDER BY (csp.delivered_count::numeric / NULLIF(csp.total_shipments, 0) * 100) DESC) AS reliability_rank,\n        ROW_NUMBER() OVER (ORDER BY (csp.on_time_deliveries::numeric / NULLIF(csp.total_shipments, 0) * 100) DESC) AS on_time_rank\n    FROM carrier_service_performance csp\n    INNER JOIN shipping_carriers c ON csp.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON csp.service_id = st.service_id\n    WHERE csp.total_shipments >= 10\n),\nperformance_categories AS (\n    -- Fourth CTE: Categorize performance\n    SELECT\n        pr.carrier_id,\n        pr.carrier_name,\n        pr.service_id,\n        pr.service_name,\n        pr.total_shipments,\n        pr.delivery_success_rate,\n        pr.on_time_delivery_rate,\n        pr.avg_actual_transit_days,\n        pr.median_transit_days,\n        pr.p95_transit_days,\n        pr.speed_rank,\n        pr.reliability_rank,\n        pr.on_time_rank,\n        CASE\n            WHEN pr.delivery_success_rate >= 95 AND pr.on_time_delivery_rate >= 90 THEN 'Excellent'\n            WHEN pr.delivery_success_rate >= 90 AND pr.on_time_delivery_rate >= 80 THEN 'Good'\n            WHEN pr.delivery_success_rate >= 85 AND pr.on_time_delivery_rate >= 70 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category,\n        (pr.speed_rank + pr.reliability_rank + pr.on_time_rank) / 3.0 AS overall_rank_score\n    FROM performance_rankings pr\n)\nSELECT\n    pc.carrier_name,\n    pc.service_name,\n    pc.total_shipments,\n    pc.delivery_success_rate,\n    pc.on_time_delivery_rate,\n    pc.avg_actual_transit_days,\n    pc.median_transit_days,\n    pc.p95_transit_days,\n    pc.performance_category,\n    pc.overall_rank_score,\n    ROW_NUMBER() OVER (ORDER BY pc.overall_rank_score ASC) AS overall_rank\nFROM performance_categories pc\nORDER BY pc.overall_rank_score ASC;",
  "evidence": "The logistics manager needs to evaluate carrier performance to inform contract renewals and carrier selection decisions. The shipments table tracks actual delivery times and outcomes, carriers table contains service level agreements (SLAs), and routes table has expected transit times. Performance varies significantly across carriers and service types, impacting customer satisfaction. Compare carrier performance across key metrics including delivery times, on-time rates, and service reliability to identify top performers and underperformers. The query joins shipments with carriers and routes data, groups by carrier and service level, calculates delivery time metrics including average, median, and percentile distributions, computes on-time delivery rates against SLA commitments, uses window functions to rank carriers by performance metrics and calculate rolling performance trends, identifies patterns in delays by carrier and route, and handles NULL values for inc",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "shipping_zones",
    "shipment_delivery_metrics",
    "carrier_service_performance",
    "shipping_carriers",
    "shipping_service_types",
    "performance_rankings",
    "performance_categories"
  ],
  "schema_context": {},
  "expected_output": "Carrier service performance comparison showing delivery times, success rates, and reliability metrics.",
  "normal_query": "Show carrier service performance comparison with delivery time breakdowns, success rates, and reliability metrics."
}
```

### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 15,
  "question": "Can you provide a route optimization analysis showing cost and time trade-offs?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "The supply chain team is seeking to optimize shipping routes to balance cost efficiency with delivery speed requirements. The routes table contains available paths between origins and destinations with associated costs and transit times, shipments table has historical routing decisions and outcomes, and carriers table shows service options. Current routing may not be optimal due to changing conditions and priorities. Analyze route alternatives to identify optimal routing strategies that balance cost minimization with acceptable delivery timeframes. The query evaluates alternative routes between origin-destination pairs, groups shipments by route and calculates total costs and average transit times, computes cost-per-day metrics to quantify trade-offs, uses window functions to rank routes by efficiency scores combining cost and time factors, identifies Pareto-optimal routes where neither cost nor time can be improved without sacrificing the other, calculates qua",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Route optimization results showing optimal routes, cost-time trade-offs, and efficiency metrics.",
  "normal_query": "Display route optimization results showing optimal route selections, cost versus time trade-offs, and overall efficiency metrics."
}
```

### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 16,
  "question": "Can you provide a detailed breakdown of our shipping costs showing how much each component contributes to the total?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "Our shipping operations team needs to understand the composition of shipping costs to identify savings opportunities. The Shipping Intelligence system tracks costs across shipments, carriers, and routes, capturing detailed cost components including base rates, fuel surcharges, accessorial fees, and handling charges. Management has requested visibility into which cost elements drive overall expenses. Generate a cost breakdown analysis that displays individual cost components, calculates each component's percentage contribution to total costs, and provides actionable optimization recommendations based on cost patterns. The SQL query joins shipment and cost tables, groups results by cost component type and carrier, computes aggregate totals and percentages for each component, uses window functions to calculate running totals and compare costs across time periods, applies quartile analysis to identify outlier expenses, and handles NULL values in optional cost field",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Cost breakdown analysis showing component costs, cost attribution, and optimization recommendations.",
  "normal_query": "Provide a comprehensive cost breakdown analysis that shows individual component costs, their attribution to total shipping expenses, and identifies optimization opportunities."
}
```

### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 17,
  "question": "Can you analyze our shipment tracking events to identify unusual patterns or anomalies that might indicate problems?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "Our logistics operations center monitors thousands of tracking events daily across shipments. Recent delivery delays and customer complaints suggest potential systemic issues that aren't immediately visible in standard reports. The Shipping Intelligence platform captures granular tracking events including scans, location updates, status changes, and timestamps across all carriers and routes. The operations team needs to distinguish between normal variance and genuine problems requiring intervention. Perform tracking pattern analysis that establishes normal event sequences and timing baselines, identifies statistically significant anomalies and deviations, and generates predictive alerts for shipments at risk. The SQL query aggregates tracking events by shipment and route, calculates baseline metrics for event frequency and timing intervals using statistical measures, employs window functions to compute rolling averages and standard deviations for comparison, fl",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Tracking pattern analysis showing normal patterns, detected anomalies, and predictive insights.",
  "normal_query": "Analyze tracking event patterns to establish baseline behavior, detect anomalies that deviate from normal patterns, and provide predictive insights for potential issues."
}
```

### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 18,
  "question": "How accurate is our address validation system, and what impact do address corrections have on delivery performance?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "Our shipping department has invested in address validation technology to reduce failed deliveries and returns caused by incorrect addresses. However, we lack visibility into how well the system performs and whether address corrections actually improve delivery outcomes. The Shipping Intelligence database contains original addresses entered by customers, validated/corrected addresses from the validation service, delivery attempt results, and final delivery status across all shipments. Stakeholders need metrics to assess ROI and identify opportunities for system improvement. Generate address validation quality metrics that measure validation accuracy rates, quantify the impact of corrections on successful delivery rates, and reveal quality trends across different address types and geographic regions. The SQL query joins shipment, address validation, and delivery outcome tables, groups data by address type, region, and time period, calculates validation accuracy b",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Address validation quality metrics showing accuracy rates, correction impact, and quality trends.",
  "normal_query": "Evaluate address validation quality by measuring accuracy rates, analyzing the impact of address corrections on successful deliveries, and tracking quality improvement trends over time."
}
```

### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 19,
  "question": "What are the most efficient international shipping routes considering both cost and delivery time, and how do customs procedures affect them?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "Our international shipping volume has grown 40% this year, but profit margins are under pressure due to varying costs and unpredictable delivery times across different routes and countries. The Shipping Intelligence system tracks international shipments across multiple carriers and routes, capturing detailed data on shipping costs, transit times, customs clearance durations, duties and taxes, and final delivery performance. The supply chain team needs to optimize route selection to balance customer expectations for speed with financial constraints. Conduct international route analysis that identifies optimal shipping routes based on cost-time trade-offs, evaluates customs clearance efficiency by destination country, and provides data-driven route recommendations for different shipment profiles. The SQL query joins shipments, routes, carriers, and customs clearance tables filtered for international destinations, groups by origin-destination pairs, carrier, and r",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "International route analysis showing optimal routes, customs considerations, and cost-time trade-offs.",
  "normal_query": "Analyze international shipping routes to identify optimal pathways that balance cost and transit time while accounting for customs clearance requirements and complexities."
}
```

### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 20,
  "question": "Can you create a comparison matrix showing how different carriers' rates vary across package weights, zones, and service levels?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "Our shipping department works with multiple carriers and faces complex rate structures that vary by package weight, dimensional weight, destination zone, service level, and additional surcharges. Current carrier selection is often based on outdated assumptions rather than current rates, potentially costing thousands in unnecessary expenses. The Shipping Intelligence platform maintains comprehensive rate tables for all contracted carriers, including base rates, zone pricing, weight breaks, dimensional factors, and accessorial charges, along with historical shipment data showing actual charges paid. Procurement needs detailed comparisons to renegotiate contracts and operations needs guidance for daily carrier selection decisions. Create a carrier rate comparison matrix that displays pricing across multiple dimensions\u2014weight bands, destination zones, service levels, and package types\u2014calculates total delivered costs including all surcharges, and identifies the optimal car",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Rate comparison matrix showing carrier rates across multiple dimensions and optimal selections.",
  "normal_query": "Build a multi-dimensional carrier rate comparison matrix that displays pricing across carriers, package characteristics, destination zones, and service tiers to identify optimal carrier selections for different scenarios."
}
```

### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 21,
  "question": "Can you show me package dimension optimization results along with volume efficiency analysis?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "Our shipping operations team needs to optimize packaging costs and reduce wasted space. The Shipping Intelligence database contains historical shipment data including package dimensions, weights, and actual shipping costs across multiple carriers and routes. We've noticed significant variation in package sizes for similar products, suggesting optimization opportunities. Analyze package dimensions to identify optimization opportunities and quantify potential cost savings from right-sizing packages. The query joins shipment and package dimension tables, then groups by product categories and current package size ranges. It calculates volume efficiency ratios (product volume vs package volume), computes quartiles to identify outliers, and uses window functions to compare current dimensions against optimal benchmarks. The analysis aggregates potential savings by calculating the difference between actual costs and projected costs with optimized dimensions, while hand",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Package dimension optimization results showing recommended dimensions and cost savings potential.",
  "normal_query": "Show package dimension optimization results with recommended dimensions and potential cost savings."
}
```

### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 22,
  "question": "Can you provide shipping zone transit time analysis including reliability metrics?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "The logistics operations team is experiencing customer complaints about delivery delays and needs to evaluate carrier performance across different shipping zones. The Shipping Intelligence system tracks shipment timestamps, carrier assignments, origin-destination pairs, and promised delivery dates. Understanding transit time reliability by zone is critical for setting accurate customer expectations and renegotiating carrier contracts. Analyze transit times across shipping zones to compare actual performance against expected delivery windows and rank carrier reliability. The query joins shipments with carriers and routes tables, filtering for completed deliveries within the analysis period. It groups data by shipping zone and carrier, calculating average actual transit times, expected transit times based on service level agreements, and variance metrics. Window functions compute rolling 30-day averages for trend analysis and rank carriers within each zone by on-",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Zone transit time analysis showing actual vs expected times, reliability metrics, and performance rankings.",
  "normal_query": "Show zone transit time analysis with actual versus expected delivery times, reliability metrics, and carrier performance rankings."
}
```

### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 23,
  "question": "Can you show me customs duty optimization analysis with tariff code breakdown?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "The international shipping division is seeking to reduce customs duty expenses for cross-border shipments. The Shipping Intelligence database contains historical customs data including tariff codes (HS codes), duty amounts paid, product classifications, and destination countries. Recent audits suggest that some products may be misclassified or that alternative tariff codes could result in lower duty rates. Our finance team needs actionable insights to optimize duty payments while maintaining compliance. Analyze customs duty payments by tariff code to identify misclassification issues and quantify potential savings from tariff optimization. The query joins shipment data with customs declarations and tariff code reference tables, grouping by product type, current tariff code, and destination country. It calculates aggregate duty amounts paid, average duty rates, and compares against alternative valid tariff codes for similar products. Window functions rank produc",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Customs duty optimization results showing tariff code analysis and cost reduction opportunities.",
  "normal_query": "Show customs duty optimization results including tariff code analysis and cost reduction opportunities."
}
```

### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 24,
  "question": "Can you show me API rate cache optimization with hit rate analysis?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "Our shipping platform's API serves rate quotes to customers and internal systems, generating millions of requests daily. The engineering team has implemented caching to reduce load on carrier API endpoints and improve response times, but cache effectiveness varies significantly across different request types and routes. The system logs capture API request metadata, cache hit/miss events, response times, and carrier API costs. We need to optimize caching strategy to reduce both latency and carrier API charges. Analyze API cache performance to identify hit rate patterns, quantify cost savings, and find opportunities to improve cache effectiveness. The query joins API request logs with cache performance metrics and carrier cost data, grouping by request type (e.g., rate quotes, tracking, address validation), route popularity, and time windows. It calculates cache hit rates, miss rates, and partial hit percentages where rate data is partially cached. Window functio",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "API cache optimization results showing hit rates, caching opportunities, and performance improvements.",
  "normal_query": "Show API cache optimization results including cache hit rates, caching opportunities, and performance improvements."
}
```

### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 25,
  "question": "Can you provide shipping revenue forecasting with trend analysis?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "The finance and sales teams require accurate revenue forecasts for quarterly planning and investor reporting. The Shipping Intelligence platform contains historical revenue data segmented by carrier, service level, customer segment, and geographic region, spanning multiple years with seasonal patterns. Recent market changes including fuel price volatility and new competitor entries make reliable forecasting critical. Leadership needs probabilistic forecasts with confidence bounds to support strategic decisions around capacity planning and pricing strategies. Generate revenue forecasts for upcoming quarters with confidence intervals and identify underlying trends driving revenue changes. The query extracts historical revenue data from shipments and billing tables, grouping by month, carrier, service level, and customer segment. It calculates year-over-year and month-over-month growth rates, applies time-series aggregations to identify seasonal patterns, and uses",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Revenue forecasts showing predicted revenue, confidence intervals, and trend analysis.",
  "normal_query": "Show revenue forecasts including predicted revenue amounts, confidence intervals, and trend analysis."
}
```

### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 26,
  "question": "Can you show me how our carriers are performing compared to industry standards and best practices?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "As a logistics manager in the Shipping Intelligence domain, I need to evaluate whether our contracted carriers are meeting industry benchmarks. Our shipments, carriers, and routes data contains historical performance metrics including on-time delivery rates, damage rates, and cost efficiency. We want to identify underperforming carriers and negotiate better contracts based on data-driven comparisons to industry standards. Generate carrier performance benchmarks that compare each carrier's key performance indicators against industry standards and identify gaps from best practices. The query joins shipment data with carrier information and industry benchmark tables. It groups results by carrier and service type, computing aggregate metrics such as average delivery time, on-time percentage, and cost per shipment. Window functions calculate percentile rankings to show where each carrier stands relative to industry quartiles. The query handles NULL values for incomp",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Carrier performance benchmarks showing performance relative to industry standards and best practices.",
  "normal_query": "Carrier performance benchmarks comparing actual performance metrics against industry standards and best practices."
}
```

### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 27,
  "question": "Can you analyze our dimensional weight costs and show me where we can optimize packaging?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "As a supply chain analyst in the Shipping Intelligence domain, I'm concerned about rising shipping costs due to dimensional weight (DIM weight) pricing, where carriers charge based on package volume rather than actual weight. Our shipments table contains both actual weight and package dimensions, while carriers apply varying DIM divisors. Many shipments are being charged at dimensional weight instead of actual weight, inflating costs. I need to quantify this cost impact and identify optimization opportunities through better packaging. Perform a dimensional weight cost analysis that calculates the cost difference between actual weight and dimensional weight billing, and provide specific optimization recommendations for reducing DIM weight charges. The query calculates dimensional weight for each shipment using carrier-specific DIM divisors (length \u00d7 width \u00d7 height / divisor) and compares it to actual weight. It groups shipments by product category, package type,",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Dimensional weight cost analysis showing cost impact and optimization recommendations.",
  "normal_query": "Dimensional weight cost analysis identifying cost impact of dimensional pricing and providing actionable optimization recommendations."
}
```

### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 28,
  "question": "What are the efficiency metrics for our shipping routes, and which routes need optimization?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "As a transportation manager in the Shipping Intelligence domain, I oversee a network of shipping routes connecting our distribution centers to customer locations. Our routes table contains transit times, distances, fuel costs, and capacity utilization data, while the shipments table tracks actual deliveries. Some routes consistently underperform with longer transit times, lower fill rates, or higher per-mile costs than others. I need comprehensive efficiency metrics to identify which routes require optimization through rerouting, carrier changes, or consolidation strategies. Calculate route efficiency metrics that score each route's performance, rank routes by efficiency, and highlight specific optimization opportunities based on transit time, cost efficiency, and capacity utilization. The query joins routes with shipment performance data and groups by origin-destination pairs and carrier. It computes efficiency scores using weighted factors including average t",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Route efficiency metrics showing efficiency scores, performance rankings, and optimization opportunities.",
  "normal_query": "Route efficiency metrics with calculated efficiency scores, performance rankings across routes, and identification of optimization opportunities."
}
```

### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 29,
  "question": "Can you aggregate rates from all our carriers and identify the best rate for each shipment scenario?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "As a shipping operations manager in the Shipping Intelligence domain, we work with multiple carriers (UPS, FedEx, USPS, regional carriers) each offering different rates based on weight, dimensions, destination zone, and service level. Rate tables are stored separately by carrier with complex pricing rules including base rates, surcharges, and volume discounts. When processing shipments, we manually compare rates across carriers, which is time-consuming and error-prone, often missing cost-saving opportunities. We need an automated system to aggregate all carrier rates and select the optimal rate for each shipment. Create a multi-carrier rate aggregation that retrieves all applicable rates from each carrier for given shipment parameters and automatically identifies the best (lowest cost) rate selection while considering service level requirements. The query unions rate tables from all carrier databases, applying carrier-specific pricing logic including base rates",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Multi-carrier rate aggregation showing all available rates and best rate selections.",
  "normal_query": "Multi-carrier rate aggregation displaying all available carrier rates with automated best rate selection for each shipping scenario."
}
```

### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-9",
  "question_id": 30,
  "question": "Can you build me a comprehensive real-time shipping intelligence dashboard with all key metrics and trends?",
  "SQL": "WITH base_data AS (\n    -- First CTE: Base data extraction\n    SELECT\n        s.shipment_id,\n        s.carrier_id,\n        s.service_id,\n        s.origin_zip_code,\n        s.destination_zip_code,\n        s.total_cost,\n        s.shipment_status,\n        s.created_at,\n        p.weight_lbs,\n        p.length_inches,\n        p.width_inches,\n        p.height_inches\n    FROM shipments s\n    INNER JOIN packages p ON s.package_id = p.package_id\n    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'\n),\naggregated_metrics AS (\n    -- Second CTE: Aggregate metrics\n    SELECT\n        bd.carrier_id,\n        bd.service_id,\n        COUNT(*) AS total_shipments,\n        SUM(bd.total_cost) AS total_revenue,\n        AVG(bd.total_cost) AS avg_cost,\n        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,\n        AVG(bd.weight_lbs) AS avg_weight_lbs\n    FROM base_data bd\n    GROUP BY bd.carrier_id, bd.service_id\n),\nperformance_analysis AS (\n    -- Third CTE: Performance analysis\n    SELECT\n        am.carrier_id,\n        c.carrier_name,\n        am.service_id,\n        st.service_name,\n        am.total_shipments,\n        am.total_revenue,\n        am.avg_cost,\n        am.delivered_count,\n        CASE\n            WHEN am.total_shipments > 0\n            THEN am.delivered_count::numeric / am.total_shipments * 100\n            ELSE 0\n        END AS delivery_success_rate,\n        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,\n        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank\n    FROM aggregated_metrics am\n    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id\n    INNER JOIN shipping_service_types st ON am.service_id = st.service_id\n),\noptimization_recommendations AS (\n    -- Fourth CTE: Generate optimization recommendations\n    SELECT\n        pa.carrier_id,\n        pa.carrier_name,\n        pa.service_id,\n        pa.service_name,\n        pa.total_shipments,\n        pa.total_revenue,\n        pa.avg_cost,\n        pa.delivery_success_rate,\n        pa.revenue_rank,\n        pa.cost_rank,\n        CASE\n            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'\n            WHEN pa.delivery_success_rate >= 90 THEN 'Good'\n            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'\n            ELSE 'Needs Improvement'\n        END AS performance_category\n    FROM performance_analysis pa\n)\nSELECT\n    or_rec.carrier_name,\n    or_rec.service_name,\n    or_rec.total_shipments,\n    or_rec.total_revenue,\n    or_rec.avg_cost,\n    or_rec.delivery_success_rate,\n    or_rec.performance_category,\n    or_rec.revenue_rank,\n    or_rec.cost_rank\nFROM optimization_recommendations or_rec\nORDER BY or_rec.total_revenue DESC;",
  "evidence": "As the Director of Logistics in the Shipping Intelligence domain, I need a unified view of our entire shipping operation spanning multiple carriers, routes, and distribution centers. Our data is fragmented across shipment tracking systems, carrier performance databases, and cost accounting tables. Executive leadership requires real-time visibility into shipping costs, carrier performance, route efficiency, and emerging issues. Currently, we compile reports manually from multiple sources, resulting in delayed insights and missed optimization opportunities. We need a comprehensive dashboard that consolidates all shipping intelligence into actionable metrics updated in real-time. Build a comprehensive shipping intelligence dashboard that aggregates all key metrics including shipping costs, carrier performance scores, route efficiency, on-time delivery rates, cost trends, and identifies actionable insights for operational improvement. The query performs complex joi",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "shipments",
    "packages",
    "base_data",
    "aggregated_metrics",
    "shipping_carriers",
    "shipping_service_types",
    "performance_analysis",
    "optimization_recommendations"
  ],
  "schema_context": {},
  "expected_output": "Comprehensive dashboard showing all key shipping intelligence metrics, trends, and actionable insights.",
  "normal_query": "Comprehensive real-time shipping intelligence dashboard displaying all critical metrics, performance trends, and actionable insights across carriers, costs, and operations."
}
```
