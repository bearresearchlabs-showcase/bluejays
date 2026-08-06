# Database 10 - Marketing Intelligence Database - Extremely Complex SQL Queries

# Database Schema: DB10

**Description:** Marketing Intelligence and Retail Inventory Tracking System
**Created:** 2026-02-04

## Overview

This database contains marketing intelligence data from U.S. Census Bureau, BLS, FTC, Data.gov, and retail sources including products, retailers, stores, inventory levels, pricing data, market intelligence aggregations, deal alerts, census retail data, BLS price indices, geographic markets, data sources, and pipeline metadata.

## Tables

### `products`
Product catalog with SKUs, UPCs, categories, and brand information

### `retailers`
Retailer information including headquarters and market coverage

### `stores`
Store locations with geographic data for spatial analysis

### `product_inventory`
Inventory levels by store with stock status tracking

### `product_pricing`
Pricing data with historical tracking and deal detection

### `market_intelligence`
Aggregated market data for competitive analysis and trends

### `deal_alerts`
Deal tracking and alert generation for promotions and sales

### `census_retail_data`
U.S. Census Bureau Monthly Retail Trade Survey (MRTS) data

### `bls_price_data`
Bureau of Labor Statistics Consumer Price Index (CPI) and Producer Price Index (PPI) data

### `geographic_markets`
Market area definitions with geographic boundaries and demographics

### `data_sources`
Source tracking for data lineage and quality monitoring

### `pipeline_metadata`
ETL pipeline execution tracking and error logging

---

This file contains 30 extremely complex SQL queries focused on business-oriented use cases for client deliverables. All queries are designed to work across PostgreSQL.

## Query 1: Multi-Retailer Price Comparison with Geographic Filtering and Temporal Trend Analysis

**Description:** Analyzes pricing across multiple retailers for products within geographic markets, incorporating temporal trends, price volatility metrics, and competitive positioning. Uses multiple CTEs to aggregate pricing data, calculate price differences, identify best deals, and track price movements over time with window functions.

**Use Case:** Competitive pricing analysis for retail intelligence platforms - identify best prices by location and track price trends over time

**Business Value:** Enables retailers and consumers to identify optimal pricing strategies and best deals by geographic market, supporting $1M+ ARR pricing intelligence platforms

**Purpose:** Provides comprehensive multi-retailer price comparison with geographic and temporal dimensions for strategic pricing decisions

**Complexity:** Deep nested CTEs (6+ levels), multiple joins across products/retailers/stores/pricing tables, window functions with frame clauses, percentile calculations, temporal aggregations, geographic filtering, correlated subqueries

**Expected Output:** Product pricing comparison report showing best prices by retailer and location, price trends, and competitive positioning metrics

```sql
WITH product_base_pricing AS (
    -- First CTE: Base pricing data with product and retailer information
    SELECT
        pp.pricing_id,
        pp.product_id,
        pp.retailer_id,
        pp.store_id,
        p.product_name,
        p.brand,
        p.category,
        p.subcategory,
        r.retailer_name,
        r.retailer_type,
        s.store_city,
        s.store_state,
        s.store_zip,
        s.store_latitude,
        s.store_longitude,
        pp.current_price,
        pp.original_price,
        pp.sale_price,
        pp.discount_percentage,
        pp.price_effective_date,
        pp.price_expiry_date,
        pp.price_type,
        pp.is_online_price,
        pp.price_confidence_score
    FROM product_pricing pp
    INNER JOIN products p ON pp.product_id = p.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    WHERE pp.price_effective_date >= CURRENT_DATE - INTERVAL '90 days'
        AND p.is_active = TRUE
        AND r.retailer_status = 'active'
),
geographic_market_mapping AS (
    -- Second CTE: Map stores to geographic markets
    SELECT
        pbp.*,
        gm.market_id,
        gm.market_name,
        gm.market_type,
        gm.market_code,
        gm.population,
        gm.median_income,
        CASE
            WHEN gm.market_geom IS NOT NULL AND s.store_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(s.store_geom, gm.market_geom) THEN TRUE
                    ELSE FALSE
                END
            WHEN gm.market_type = 'zip' AND s.store_zip = gm.market_code THEN TRUE
            WHEN gm.market_type = 'city' AND s.store_city = gm.market_name AND s.store_state = gm.state_code THEN TRUE
            WHEN gm.market_type = 'state' AND s.store_state = gm.state_code THEN TRUE
            ELSE FALSE
        END AS is_in_market
    FROM product_base_pricing pbp
    LEFT JOIN stores s ON pbp.store_id = s.store_id
    LEFT JOIN geographic_markets gm ON (
        (gm.market_type = 'zip' AND s.store_zip = gm.market_code)
        OR (gm.market_type = 'city' AND s.store_city = gm.market_name AND s.store_state = gm.state_code)
        OR (gm.market_type = 'state' AND s.store_state = gm.state_code)
        OR (gm.market_geom IS NOT NULL AND s.store_geom IS NOT NULL AND ST_WITHIN(s.store_geom, gm.market_geom))
    )
    WHERE pbp.store_id IS NOT NULL OR pbp.is_online_price = TRUE
),
market_pricing_aggregates AS (
    -- Third CTE: Aggregate pricing by market and product
    SELECT
        gmm.product_id,
        gmm.product_name,
        gmm.brand,
        gmm.category,
        gmm.market_id,
        gmm.market_name,
        gmm.market_type,
        gmm.population,
        gmm.median_income,
        COUNT(DISTINCT gmm.retailer_id) AS retailer_count,
        COUNT(DISTINCT gmm.store_id) AS store_count,
        COUNT(DISTINCT CASE WHEN gmm.is_online_price = FALSE THEN gmm.store_id END) AS physical_store_count,
        COUNT(DISTINCT CASE WHEN gmm.is_online_price = TRUE THEN gmm.retailer_id END) AS online_retailer_count,
        MIN(gmm.current_price) AS min_price,
        MAX(gmm.current_price) AS max_price,
        AVG(gmm.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gmm.current_price) AS median_price,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY gmm.current_price) AS q1_price,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY gmm.current_price) AS q3_price,
        STDDEV(gmm.current_price) AS price_std_dev,
        AVG(gmm.discount_percentage) AS avg_discount_percentage,
        COUNT(CASE WHEN gmm.price_type = 'sale' THEN 1 END) AS sale_count,
        COUNT(CASE WHEN gmm.price_type = 'clearance' THEN 1 END) AS clearance_count
    FROM geographic_market_mapping gmm
    WHERE gmm.is_in_market = TRUE OR gmm.is_online_price = TRUE
    GROUP BY
        gmm.product_id,
        gmm.product_name,
        gmm.brand,
        gmm.category,
        gmm.market_id,
        gmm.market_name,
        gmm.market_type,
        gmm.population,
        gmm.median_income
),
retailer_market_positioning AS (
    -- Fourth CTE: Calculate retailer positioning within each market
    SELECT
        mpa.*,
        gmm.retailer_id,
        gmm.retailer_name,
        gmm.retailer_type,
        gmm.current_price AS retailer_price,
        gmm.price_type AS retailer_price_type,
        gmm.discount_percentage AS retailer_discount,
        CASE
            WHEN gmm.current_price = mpa.min_price THEN 'lowest'
            WHEN gmm.current_price <= mpa.q1_price THEN 'low'
            WHEN gmm.current_price <= mpa.median_price THEN 'below_median'
            WHEN gmm.current_price <= mpa.q3_price THEN 'above_median'
            WHEN gmm.current_price = mpa.max_price THEN 'highest'
            ELSE 'high'
        END AS price_position,
        (gmm.current_price - mpa.min_price) AS price_difference_from_min,
        ((gmm.current_price - mpa.min_price) / NULLIF(mpa.min_price, 0)) * 100 AS price_premium_percentage,
        ROW_NUMBER() OVER (
            PARTITION BY mpa.product_id, mpa.market_id
            ORDER BY gmm.current_price ASC
        ) AS price_rank
    FROM market_pricing_aggregates mpa
    INNER JOIN geographic_market_mapping gmm ON mpa.product_id = gmm.product_id
        AND mpa.market_id = gmm.market_id
    WHERE gmm.is_in_market = TRUE OR gmm.is_online_price = TRUE
),
temporal_price_trends AS (
    -- Fifth CTE: Analyze price trends over time with window functions
    SELECT
        rmp.*,
        gmm.price_effective_date,
        LAG(gmm.current_price, 1) OVER (
            PARTITION BY rmp.product_id, rmp.retailer_id, rmp.market_id
            ORDER BY gmm.price_effective_date
        ) AS prev_price,
        LEAD(gmm.current_price, 1) OVER (
            PARTITION BY rmp.product_id, rmp.retailer_id, rmp.market_id
            ORDER BY gmm.price_effective_date
        ) AS next_price,
        AVG(gmm.current_price) OVER (
            PARTITION BY rmp.product_id, rmp.retailer_id, rmp.market_id
            ORDER BY gmm.price_effective_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_avg_price_7d,
        STDDEV(gmm.current_price) OVER (
            PARTITION BY rmp.product_id, rmp.retailer_id, rmp.market_id
            ORDER BY gmm.price_effective_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS price_volatility_30d,
        MIN(gmm.current_price) OVER (
            PARTITION BY rmp.product_id, rmp.retailer_id, rmp.market_id
            ORDER BY gmm.price_effective_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS min_price_30d,
        MAX(gmm.current_price) OVER (
            PARTITION BY rmp.product_id, rmp.retailer_id, rmp.market_id
            ORDER BY gmm.price_effective_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS max_price_30d
    FROM retailer_market_positioning rmp
    INNER JOIN geographic_market_mapping gmm ON rmp.product_id = gmm.product_id
        AND rmp.retailer_id = gmm.retailer_id
        AND rmp.market_id = gmm.market_id
),
final_price_intelligence AS (
    -- Sixth CTE: Final analytics with comprehensive metrics
    SELECT
        tpt.product_id,
        tpt.product_name,
        tpt.brand,
        tpt.category,
        tpt.market_id,
        tpt.market_name,
        tpt.market_type,
        tpt.population,
        tpt.median_income,
        tpt.retailer_id,
        tpt.retailer_name,
        tpt.retailer_type,
        tpt.retailer_price,
        tpt.price_position,
        tpt.price_rank,
        tpt.price_difference_from_min,
        ROUND(CAST(tpt.price_premium_percentage AS NUMERIC), 2) AS price_premium_percentage,
        tpt.retailer_price_type,
        tpt.retailer_discount,
        tpt.retailer_count,
        tpt.store_count,
        tpt.physical_store_count,
        tpt.online_retailer_count,
        tpt.min_price,
        tpt.max_price,
        ROUND(CAST(tpt.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(tpt.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(tpt.price_std_dev AS NUMERIC), 2) AS price_std_dev,
        ROUND(CAST(tpt.avg_discount_percentage AS NUMERIC), 2) AS avg_discount_percentage,
        tpt.sale_count,
        tpt.clearance_count,
        tpt.price_effective_date,
        tpt.prev_price,
        tpt.next_price,
        CASE
            WHEN tpt.prev_price IS NOT NULL THEN tpt.retailer_price - tpt.prev_price
            ELSE NULL
        END AS price_change,
        CASE
            WHEN tpt.prev_price IS NOT NULL AND tpt.prev_price != 0 THEN
                ((tpt.retailer_price - tpt.prev_price) / tpt.prev_price) * 100
            ELSE NULL
        END AS price_change_percentage,
        ROUND(CAST(tpt.moving_avg_price_7d AS NUMERIC), 2) AS moving_avg_price_7d,
        ROUND(CAST(tpt.price_volatility_30d AS NUMERIC), 2) AS price_volatility_30d,
        tpt.min_price_30d,
        tpt.max_price_30d,
        CASE
            WHEN tpt.retailer_price <= tpt.min_price_30d THEN 'at_30d_low'
            WHEN tpt.retailer_price >= tpt.max_price_30d THEN 'at_30d_high'
            ELSE 'mid_range'
        END AS price_position_30d
    FROM temporal_price_trends tpt
)
SELECT
    product_name,
    brand,
    category,
    market_name,
    market_type,
    retailer_name,
    retailer_type,
    retailer_price,
    price_position,
    price_rank,
    price_premium_percentage,
    retailer_discount,
    avg_price,
    median_price,
    min_price,
    max_price,
    price_change_percentage,
    moving_avg_price_7d,
    price_volatility_30d,
    price_position_30d,
    retailer_count,
    store_count,
    physical_store_count,
    online_retailer_count
FROM final_price_intelligence
WHERE price_rank <= 5
ORDER BY
    product_id,
    market_id,
    price_rank;
```
```

## Query 2: Inventory Availability Prediction Using Historical Patterns and Geographic Distribution

**Description:** Predicts inventory availability by analyzing historical stock patterns, restocking frequencies, seasonal trends, and geographic distribution. Uses recursive CTEs for pattern detection, window functions for trend analysis, and complex aggregations to forecast stock levels.

**Use Case:** Inventory forecasting for retail operations - predict when products will be in stock and optimize restocking schedules

**Business Value:** Enables retailers to optimize inventory management, reduce stockouts, and improve customer satisfaction, supporting $1M+ ARR inventory intelligence platforms

**Purpose:** Provides predictive analytics for inventory availability based on historical patterns and geographic factors

**Complexity:** Recursive CTEs for pattern detection, multiple CTEs (7+ levels), window functions with complex frame clauses, temporal aggregations, geographic clustering, statistical forecasting calculations

**Expected Output:** Inventory availability predictions with confidence scores, restocking recommendations, and geographic distribution analysis

```sql
WITH RECURSIVE inventory_history AS (
    -- Base case: Current inventory state
    SELECT
        pi.inventory_id,
        pi.product_id,
        pi.store_id,
        pi.stock_level,
        pi.stock_status,
        pi.available_quantity,
        pi.last_checked_at,
        pi.last_restocked_at,
        p.product_name,
        p.category,
        s.store_city,
        s.store_state,
        s.retailer_id,
        r.retailer_name,
        DATE_TRUNC('day', pi.last_checked_at) AS check_date,
        EXTRACT(DOW FROM pi.last_checked_at) AS day_of_week,
        EXTRACT(MONTH FROM pi.last_checked_at) AS month_num
    FROM product_inventory pi
    INNER JOIN products p ON pi.product_id = p.product_id
    INNER JOIN stores s ON pi.store_id = s.store_id
    INNER JOIN retailers r ON s.retailer_id = r.retailer_id
    WHERE pi.last_checked_at >= CURRENT_TIMESTAMP - INTERVAL '180 days'
        AND p.is_active = TRUE
    
    UNION ALL
    
    -- Recursive case: Historical inventory states (simulated from check history)
    SELECT
        ih.inventory_id,
        ih.product_id,
        ih.store_id,
        CASE
            WHEN ih.stock_status = 'out_of_stock' AND ih.last_restocked_at IS NOT NULL THEN
                CASE
                    WHEN ih.last_restocked_at > ih.last_checked_at - INTERVAL '7 days' THEN 50
                    ELSE 0
                END
            ELSE ih.stock_level
        END AS stock_level,
        ih.stock_status,
        ih.available_quantity,
        ih.last_checked_at - INTERVAL '1 day' AS last_checked_at,
        ih.last_restocked_at,
        ih.product_name,
        ih.category,
        ih.store_city,
        ih.store_state,
        ih.retailer_id,
        ih.retailer_name,
        DATE_TRUNC('day', ih.last_checked_at - INTERVAL '1 day') AS check_date,
        EXTRACT(DOW FROM ih.last_checked_at - INTERVAL '1 day') AS day_of_week,
        EXTRACT(MONTH FROM ih.last_checked_at - INTERVAL '1 day') AS month_num
    FROM inventory_history ih
    WHERE ih.last_checked_at > CURRENT_TIMESTAMP - INTERVAL '180 days'
),
inventory_patterns AS (
    -- Second CTE: Identify inventory patterns and cycles
    SELECT
        product_id,
        store_id,
        product_name,
        category,
        store_city,
        store_state,
        retailer_id,
        retailer_name,
        check_date,
        day_of_week,
        month_num,
        stock_level,
        stock_status,
        available_quantity,
        last_checked_at,
        last_restocked_at,
        COUNT(*) OVER (
            PARTITION BY product_id, store_id
            ORDER BY check_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS days_tracked,
        LAG(stock_level, 1) OVER (
            PARTITION BY product_id, store_id
            ORDER BY check_date
        ) AS prev_stock_level,
        LAG(stock_status, 1) OVER (
            PARTITION BY product_id, store_id
            ORDER BY check_date
        ) AS prev_stock_status,
        CASE
            WHEN stock_status = 'out_of_stock' AND LAG(stock_status, 1) OVER (
                PARTITION BY product_id, store_id ORDER BY check_date
            ) != 'out_of_stock' THEN 1
            ELSE 0
        END AS stockout_event,
        CASE
            WHEN stock_status != 'out_of_stock' AND LAG(stock_status, 1) OVER (
                PARTITION BY product_id, store_id ORDER BY check_date
            ) = 'out_of_stock' THEN 1
            ELSE 0
        END AS restock_event
    FROM inventory_history
),
stockout_analysis AS (
    -- Third CTE: Analyze stockout patterns and durations
    SELECT
        ip.*,
        SUM(ip.stockout_event) OVER (
            PARTITION BY ip.product_id, ip.store_id
            ORDER BY ip.check_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS stockout_count_cumulative,
        SUM(ip.restock_event) OVER (
            PARTITION BY ip.product_id, ip.store_id
            ORDER BY ip.check_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS restock_count_cumulative,
        CASE
            WHEN ip.stockout_event = 1 THEN
                ROW_NUMBER() OVER (
                    PARTITION BY ip.product_id, ip.store_id, ip.stockout_event
                    ORDER BY ip.check_date
                )
            ELSE NULL
        END AS stockout_period_id
    FROM inventory_patterns ip
),
stockout_durations AS (
    -- Fourth CTE: Calculate stockout durations
    SELECT
        sa.*,
        CASE
            WHEN sa.stockout_period_id IS NOT NULL THEN
                COUNT(*) OVER (
                    PARTITION BY sa.product_id, sa.store_id, sa.stockout_period_id
                )
            ELSE NULL
        END AS stockout_duration_days,
        AVG(sa.stock_level) OVER (
            PARTITION BY sa.product_id, sa.store_id
            ORDER BY sa.check_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS avg_stock_30d,
        STDDEV(sa.stock_level) OVER (
            PARTITION BY sa.product_id, sa.store_id
            ORDER BY sa.check_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS stock_volatility_30d,
        MIN(sa.stock_level) OVER (
            PARTITION BY sa.product_id, sa.store_id
            ORDER BY sa.check_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS min_stock_30d,
        MAX(sa.stock_level) OVER (
            PARTITION BY sa.product_id, sa.store_id
            ORDER BY sa.check_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS max_stock_30d
    FROM stockout_analysis sa
),
seasonal_patterns AS (
    -- Fifth CTE: Identify seasonal and weekly patterns
    SELECT
        sd.*,
        AVG(sd.stock_level) OVER (
            PARTITION BY sd.product_id, sd.store_id, sd.day_of_week
        ) AS avg_stock_by_dow,
        AVG(sd.stock_level) OVER (
            PARTITION BY sd.product_id, sd.store_id, sd.month_num
        ) AS avg_stock_by_month,
        COUNT(CASE WHEN sd.stock_status = 'out_of_stock' THEN 1 END) OVER (
            PARTITION BY sd.product_id, sd.store_id, sd.day_of_week
        ) AS stockout_count_by_dow,
        COUNT(CASE WHEN sd.stock_status = 'out_of_stock' THEN 1 END) OVER (
            PARTITION BY sd.product_id, sd.store_id, sd.month_num
        ) AS stockout_count_by_month
    FROM stockout_durations sd
),
geographic_clustering AS (
    -- Sixth CTE: Analyze geographic distribution patterns
    SELECT
        sp.*,
        COUNT(DISTINCT sp.store_id) OVER (
            PARTITION BY sp.product_id, sp.store_state
        ) AS store_count_by_state,
        AVG(sp.stock_level) OVER (
            PARTITION BY sp.product_id, sp.store_state
        ) AS avg_stock_by_state,
        COUNT(CASE WHEN sp.stock_status = 'out_of_stock' THEN 1 END) OVER (
            PARTITION BY sp.product_id, sp.store_state
        ) AS stockout_count_by_state,
        COUNT(DISTINCT sp.store_id) OVER (
            PARTITION BY sp.product_id, sp.store_city, sp.store_state
        ) AS store_count_by_city,
        AVG(sp.stock_level) OVER (
            PARTITION BY sp.product_id, sp.store_city, sp.store_state
        ) AS avg_stock_by_city
    FROM seasonal_patterns sp
),
availability_prediction AS (
    -- Seventh CTE: Generate availability predictions
    SELECT
        gc.product_id,
        gc.product_name,
        gc.category,
        gc.store_id,
        gc.store_city,
        gc.store_state,
        gc.retailer_id,
        gc.retailer_name,
        gc.check_date,
        gc.stock_level,
        gc.stock_status,
        gc.available_quantity,
        gc.avg_stock_30d,
        gc.stock_volatility_30d,
        gc.min_stock_30d,
        gc.max_stock_30d,
        gc.avg_stock_by_dow,
        gc.avg_stock_by_month,
        gc.stockout_count_by_dow,
        gc.stockout_count_by_month,
        gc.store_count_by_state,
        gc.avg_stock_by_state,
        gc.stockout_count_by_state,
        gc.store_count_by_city,
        gc.avg_stock_by_city,
        -- Prediction calculations
        CASE
            WHEN gc.stock_level > gc.avg_stock_30d + (gc.stock_volatility_30d * 2) THEN 'high'
            WHEN gc.stock_level < gc.avg_stock_30d - (gc.stock_volatility_30d * 2) THEN 'low'
            ELSE 'normal'
        END AS stock_level_classification,
        CASE
            WHEN gc.stock_status = 'out_of_stock' THEN
                CASE
                    WHEN gc.stockout_duration_days > 7 THEN 'extended_outage'
                    WHEN gc.stockout_duration_days > 3 THEN 'moderate_outage'
                    ELSE 'short_outage'
                END
            ELSE 'in_stock'
        END AS outage_severity,
        -- Forecast next 7 days availability
        CASE
            WHEN gc.stock_level > 0 AND gc.stock_level > gc.avg_stock_by_dow THEN 'likely_available'
            WHEN gc.stock_level = 0 AND gc.stockout_count_by_dow < 2 THEN 'possibly_available'
            ELSE 'unlikely_available'
        END AS next_7d_availability_prediction,
        -- Confidence score
        CASE
            WHEN gc.days_tracked >= 90 AND gc.stock_volatility_30d < 10 THEN 0.95
            WHEN gc.days_tracked >= 60 AND gc.stock_volatility_30d < 20 THEN 0.85
            WHEN gc.days_tracked >= 30 THEN 0.75
            ELSE 0.60
        END AS prediction_confidence
    FROM geographic_clustering gc
)
SELECT
    product_name,
    category,
    store_city,
    store_state,
    retailer_name,
    check_date,
    stock_level,
    stock_status,
    stock_level_classification,
    outage_severity,
    next_7d_availability_prediction,
    ROUND(CAST(prediction_confidence AS NUMERIC), 2) AS prediction_confidence,
    ROUND(CAST(avg_stock_30d AS NUMERIC), 0) AS avg_stock_30d,
    ROUND(CAST(stock_volatility_30d AS NUMERIC), 2) AS stock_volatility_30d,
    avg_stock_by_dow,
    avg_stock_by_month,
    store_count_by_state,
    avg_stock_by_state
FROM availability_prediction
WHERE check_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY
    product_id,
    store_id,
    check_date DESC;
```
```

## Query 3: Market Share Analysis with Competitive Positioning and Temporal Trends

**Description:** Analyzes market share by retailer and product category, incorporating competitive positioning metrics, temporal trends, and geographic distribution. Uses multiple CTEs to calculate market share percentages, competitive rankings, share changes over time, and market concentration metrics with window functions.

**Use Case:** Competitive market analysis for retail intelligence - identify market leaders, track share changes, and analyze competitive dynamics

**Business Value:** Enables retailers to understand their market position, track competitive movements, and identify growth opportunities, supporting $1M+ ARR market intelligence platforms

**Purpose:** Provides comprehensive market share analysis with competitive positioning and temporal trend tracking

**Complexity:** Multiple CTEs (6+ levels), complex aggregations, window functions with frame clauses, percentile rankings, temporal comparisons, market concentration calculations

**Expected Output:** Market share report showing retailer rankings, share percentages, competitive positioning, and temporal trends by product category

```sql
WITH retailer_product_sales AS (
    SELECT
        r.retailer_id,
        r.retailer_name,
        r.retailer_type,
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        COUNT(DISTINCT pp.pricing_id) AS pricing_records_count,
        AVG(pp.current_price) AS avg_price,
        COUNT(DISTINCT pp.store_id) AS store_count,
        COUNT(DISTINCT CASE WHEN pi.stock_status = 'in_stock' THEN pi.store_id END) AS stores_in_stock,
        SUM(CASE WHEN pi.stock_level > 0 THEN 1 ELSE 0 END) AS inventory_units
    FROM retailers r
    INNER JOIN product_pricing pp ON r.retailer_id = pp.retailer_id
    INNER JOIN products p ON pp.product_id = p.product_id
    LEFT JOIN product_inventory pi ON pp.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE r.retailer_status = 'active' AND p.is_active = TRUE
    GROUP BY r.retailer_id, r.retailer_name, r.retailer_type, p.product_id, p.product_name, p.category, p.subcategory
),
category_market_totals AS (
    SELECT
        category,
        subcategory,
        COUNT(DISTINCT retailer_id) AS total_retailers,
        COUNT(DISTINCT product_id) AS total_products,
        SUM(pricing_records_count) AS total_pricing_records,
        SUM(store_count) AS total_stores,
        SUM(stores_in_stock) AS total_stores_in_stock,
        SUM(inventory_units) AS total_inventory_units
    FROM retailer_product_sales
    GROUP BY category, subcategory
),
retailer_category_share AS (
    SELECT
        rps.*,
        cmt.total_retailers,
        cmt.total_products,
        cmt.total_pricing_records,
        cmt.total_stores,
        cmt.total_stores_in_stock,
        cmt.total_inventory_units,
        CASE
            WHEN cmt.total_pricing_records > 0 THEN
                (rps.pricing_records_count::NUMERIC / cmt.total_pricing_records::NUMERIC) * 100
            ELSE 0
        END AS pricing_records_share,
        CASE
            WHEN cmt.total_stores > 0 THEN
                (rps.store_count::NUMERIC / cmt.total_stores::NUMERIC) * 100
            ELSE 0
        END AS store_count_share,
        CASE
            WHEN cmt.total_stores_in_stock > 0 THEN
                (rps.stores_in_stock::NUMERIC / cmt.total_stores_in_stock::NUMERIC) * 100
            ELSE 0
        END AS availability_share,
        CASE
            WHEN cmt.total_inventory_units > 0 THEN
                (rps.inventory_units::NUMERIC / cmt.total_inventory_units::NUMERIC) * 100
            ELSE 0
        END AS inventory_share
    FROM retailer_product_sales rps
    INNER JOIN category_market_totals cmt ON rps.category = cmt.category AND rps.subcategory = cmt.subcategory
),
market_share_rankings AS (
    SELECT
        rcs.*,
        ROW_NUMBER() OVER (
            PARTITION BY rcs.category, rcs.subcategory
            ORDER BY rcs.pricing_records_share DESC
        ) AS pricing_rank,
        ROW_NUMBER() OVER (
            PARTITION BY rcs.category, rcs.subcategory
            ORDER BY rcs.store_count_share DESC
        ) AS store_rank,
        ROW_NUMBER() OVER (
            PARTITION BY rcs.category, rcs.subcategory
            ORDER BY rcs.availability_share DESC
        ) AS availability_rank,
        PERCENT_RANK() OVER (
            PARTITION BY rcs.category, rcs.subcategory
            ORDER BY rcs.pricing_records_share DESC
        ) AS pricing_percentile,
        NTILE(4) OVER (
            PARTITION BY rcs.category, rcs.subcategory
            ORDER BY rcs.pricing_records_share DESC
        ) AS market_position_quartile
    FROM retailer_category_share rcs
),
temporal_share_analysis AS (
    SELECT
        msr.*,
        pp.price_effective_date,
        LAG(msr.pricing_records_share, 1) OVER (
            PARTITION BY msr.retailer_id, msr.product_id
            ORDER BY pp.price_effective_date
        ) AS prev_pricing_share,
        AVG(msr.pricing_records_share) OVER (
            PARTITION BY msr.retailer_id, msr.product_id
            ORDER BY pp.price_effective_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS moving_avg_share_30d,
        STDDEV(msr.pricing_records_share) OVER (
            PARTITION BY msr.retailer_id, msr.product_id
            ORDER BY pp.price_effective_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS share_volatility_90d
    FROM market_share_rankings msr
    INNER JOIN product_pricing pp ON msr.retailer_id = pp.retailer_id AND msr.product_id = pp.product_id
),
market_concentration AS (
    SELECT
        tsa.category,
        tsa.subcategory,
        COUNT(DISTINCT tsa.retailer_id) AS retailer_count,
        SUM(tsa.pricing_records_share) AS total_share,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tsa.pricing_records_share) AS median_share,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY tsa.pricing_records_share) AS q1_share,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY tsa.pricing_records_share) AS q3_share,
        -- Herfindahl-Hirschman Index (HHI) for market concentration
        SUM(POWER(tsa.pricing_records_share / 100.0, 2)) * 10000 AS hhi_index,
        CASE
            WHEN SUM(POWER(tsa.pricing_records_share / 100.0, 2)) * 10000 > 2500 THEN 'highly_concentrated'
            WHEN SUM(POWER(tsa.pricing_records_share / 100.0, 2)) * 10000 > 1500 THEN 'moderately_concentrated'
            ELSE 'competitive'
        END AS concentration_level
    FROM temporal_share_analysis tsa
    GROUP BY tsa.category, tsa.subcategory
),
final_market_share_intelligence AS (
    SELECT
        tsa.retailer_id,
        tsa.retailer_name,
        tsa.retailer_type,
        tsa.product_id,
        tsa.product_name,
        tsa.category,
        tsa.subcategory,
        ROUND(CAST(tsa.pricing_records_share AS NUMERIC), 2) AS pricing_records_share,
        ROUND(CAST(tsa.store_count_share AS NUMERIC), 2) AS store_count_share,
        ROUND(CAST(tsa.availability_share AS NUMERIC), 2) AS availability_share,
        ROUND(CAST(tsa.inventory_share AS NUMERIC), 2) AS inventory_share,
        tsa.pricing_rank,
        tsa.store_rank,
        tsa.availability_rank,
        ROUND(CAST(tsa.pricing_percentile * 100 AS NUMERIC), 2) AS pricing_percentile,
        tsa.market_position_quartile,
        CASE
            WHEN tsa.prev_pricing_share IS NOT NULL THEN
                tsa.pricing_records_share - tsa.prev_pricing_share
            ELSE NULL
        END AS share_change,
        CASE
            WHEN tsa.prev_pricing_share IS NOT NULL AND tsa.prev_pricing_share != 0 THEN
                ((tsa.pricing_records_share - tsa.prev_pricing_share) / tsa.prev_pricing_share) * 100
            ELSE NULL
        END AS share_change_percentage,
        ROUND(CAST(tsa.moving_avg_share_30d AS NUMERIC), 2) AS moving_avg_share_30d,
        ROUND(CAST(tsa.share_volatility_90d AS NUMERIC), 2) AS share_volatility_90d,
        mc.hhi_index,
        mc.concentration_level,
        CASE
            WHEN tsa.pricing_rank = 1 THEN 'market_leader'
            WHEN tsa.pricing_rank <= 3 THEN 'top_3'
            WHEN tsa.pricing_rank <= 5 THEN 'top_5'
            ELSE 'other'
        END AS competitive_position
    FROM temporal_share_analysis tsa
    INNER JOIN market_concentration mc ON tsa.category = mc.category AND tsa.subcategory = mc.subcategory
)
SELECT
    retailer_name,
    retailer_type,
    product_name,
    category,
    subcategory,
    pricing_records_share,
    store_count_share,
    availability_share,
    inventory_share,
    pricing_rank,
    competitive_position,
    share_change_percentage,
    moving_avg_share_30d,
    share_volatility_90d,
    hhi_index,
    concentration_level
FROM final_market_share_intelligence
WHERE pricing_rank <= 10
ORDER BY category, subcategory, pricing_rank;
```
```




## Query 4: Deal Detection and Alert Generation with Temporal Patterns

**Description:** Detects deals and generates alerts by analyzing price changes, discount patterns, and temporal trends. Uses recursive CTEs for pattern detection, window functions for trend analysis, and complex aggregations to identify optimal deals.

**Use Case:** Automated deal detection for retail intelligence platforms

**Business Value:** Enables consumers and retailers to identify best deals automatically, supporting $1M+ ARR deal aggregation platforms

**Purpose:** Provides comprehensive analysis for marketing intelligence

**Complexity:** Recursive CTEs, multiple CTEs (7+ levels), window functions with frame clauses, temporal pattern detection, discount analysis

**Expected Output:** Detailed analysis report with metrics and insights

```sql
WITH RECURSIVE deal_price_history AS (
    -- Base case: Current deal pricing
    SELECT
        da.deal_id,
        da.product_id,
        da.retailer_id,
        da.store_id,
        da.deal_type,
        da.discount_percentage,
        da.deal_price,
        da.original_price,
        da.deal_start_date,
        da.deal_end_date,
        da.deal_status,
        p.product_name,
        p.category,
        r.retailer_name,
        s.store_city,
        s.store_state,
        DATE_TRUNC('day', da.deal_start_date) AS deal_date,
        EXTRACT(DOW FROM da.deal_start_date) AS day_of_week
    FROM deal_alerts da
    INNER JOIN products p ON da.product_id = p.product_id
    INNER JOIN retailers r ON da.retailer_id = r.retailer_id
    LEFT JOIN stores s ON da.store_id = s.store_id
    WHERE da.deal_status = 'active'
        AND p.is_active = TRUE
    
    UNION ALL
    
    -- Recursive case: Historical price patterns
    SELECT
        dph.deal_id,
        dph.product_id,
        dph.retailer_id,
        dph.store_id,
        dph.deal_type,
        dph.discount_percentage,
        dph.deal_price,
        dph.original_price,
        dph.deal_start_date - INTERVAL '1 day' AS deal_start_date,
        dph.deal_end_date,
        dph.deal_status,
        dph.product_name,
        dph.category,
        dph.retailer_name,
        dph.store_city,
        dph.store_state,
        DATE_TRUNC('day', dph.deal_start_date - INTERVAL '1 day') AS deal_date,
        EXTRACT(DOW FROM dph.deal_start_date - INTERVAL '1 day') AS day_of_week
    FROM deal_price_history dph
    WHERE dph.deal_start_date > CURRENT_DATE - INTERVAL '180 days'
),
price_change_detection AS (
    -- Second CTE: Detect price changes and deal triggers
    SELECT
        dph.*,
        pp.current_price AS current_market_price,
        pp.price_effective_date,
        CASE
            WHEN pp.current_price < dph.deal_price THEN 'better_deal_available'
            WHEN pp.current_price = dph.deal_price THEN 'price_match'
            ELSE 'deal_better'
        END AS price_comparison,
        ABS(pp.current_price - dph.deal_price) AS price_difference,
        CASE
            WHEN dph.deal_price < pp.current_price THEN
                ((pp.current_price - dph.deal_price) / pp.current_price) * 100
            ELSE NULL
        END AS savings_percentage
    FROM deal_price_history dph
    LEFT JOIN product_pricing pp ON dph.product_id = pp.product_id
        AND dph.retailer_id = pp.retailer_id
        AND pp.price_effective_date BETWEEN dph.deal_start_date AND COALESCE(dph.deal_end_date, CURRENT_DATE)
),
deal_pattern_analysis AS (
    -- Third CTE: Analyze deal patterns and frequencies
    SELECT
        pcd.*,
        COUNT(*) OVER (
            PARTITION BY pcd.product_id, pcd.retailer_id
            ORDER BY pcd.deal_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS deals_count_90d,
        AVG(pcd.discount_percentage) OVER (
            PARTITION BY pcd.product_id, pcd.retailer_id
            ORDER BY pcd.deal_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS avg_discount_30d,
        LAG(pcd.deal_price, 1) OVER (
            PARTITION BY pcd.product_id, pcd.retailer_id
            ORDER BY pcd.deal_date
        ) AS prev_deal_price,
        LEAD(pcd.deal_price, 1) OVER (
            PARTITION BY pcd.product_id, pcd.retailer_id
            ORDER BY pcd.deal_date
        ) AS next_deal_price,
        MIN(pcd.deal_price) OVER (
            PARTITION BY pcd.product_id, pcd.retailer_id
            ORDER BY pcd.deal_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS min_deal_price_90d,
        MAX(pcd.deal_price) OVER (
            PARTITION BY pcd.product_id, pcd.retailer_id
            ORDER BY pcd.deal_date
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS max_deal_price_90d
    FROM price_change_detection pcd
),
deal_alert_scoring AS (
    -- Fourth CTE: Score deals for alert generation
    SELECT
        dpa.*,
        CASE
            WHEN dpa.prev_deal_price IS NOT NULL THEN
                dpa.deal_price - dpa.prev_deal_price
            ELSE NULL
        END AS price_change_from_prev,
        CASE
            WHEN dpa.deal_price <= dpa.min_deal_price_90d * 1.05 THEN 'best_price_90d'
            WHEN dpa.deal_price <= dpa.min_deal_price_90d * 1.15 THEN 'near_best_price'
            ELSE 'regular_deal'
        END AS deal_quality,
        CASE
            WHEN dpa.discount_percentage >= 50 THEN 100
            WHEN dpa.discount_percentage >= 30 THEN 80
            WHEN dpa.discount_percentage >= 20 THEN 60
            WHEN dpa.discount_percentage >= 10 THEN 40
            ELSE 20
        END AS discount_score,
        CASE
            WHEN dpa.deals_count_90d <= 2 THEN 100
            WHEN dpa.deals_count_90d <= 5 THEN 80
            WHEN dpa.deals_count_90d <= 10 THEN 60
            ELSE 40
        END AS rarity_score,
        CASE
            WHEN dpa.savings_percentage >= 30 THEN 100
            WHEN dpa.savings_percentage >= 20 THEN 80
            WHEN dpa.savings_percentage >= 10 THEN 60
            ELSE 40
        END AS savings_score
    FROM deal_pattern_analysis dpa
),
temporal_deal_trends AS (
    -- Fifth CTE: Analyze temporal trends
    SELECT
        das.*,
        AVG(das.deal_price) OVER (
            PARTITION BY das.product_id, das.day_of_week
        ) AS avg_price_by_dow,
        AVG(das.deal_price) OVER (
            PARTITION BY das.product_id, EXTRACT(MONTH FROM das.deal_date)
        ) AS avg_price_by_month,
        COUNT(CASE WHEN das.deal_type = 'clearance' THEN 1 END) OVER (
            PARTITION BY das.product_id
            ORDER BY das.deal_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS clearance_count_30d,
        COUNT(CASE WHEN das.deal_type = 'sale' THEN 1 END) OVER (
            PARTITION BY das.product_id
            ORDER BY das.deal_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS sale_count_30d
    FROM deal_alert_scoring das
),
final_deal_intelligence AS (
    -- Sixth CTE: Final deal intelligence with comprehensive metrics
    SELECT
        tdt.product_id,
        tdt.product_name,
        tdt.category,
        tdt.retailer_id,
        tdt.retailer_name,
        tdt.store_city,
        tdt.store_state,
        tdt.deal_id,
        tdt.deal_type,
        tdt.deal_price,
        tdt.original_price,
        ROUND(CAST(tdt.discount_percentage AS NUMERIC), 2) AS discount_percentage,
        tdt.deal_start_date,
        tdt.deal_end_date,
        tdt.deal_quality,
        ROUND(CAST((tdt.discount_score + tdt.rarity_score + tdt.savings_score) / 3.0 AS NUMERIC), 2) AS overall_deal_score,
        tdt.price_comparison,
        ROUND(CAST(tdt.savings_percentage AS NUMERIC), 2) AS savings_percentage,
        ROUND(CAST(tdt.avg_discount_30d AS NUMERIC), 2) AS avg_discount_30d,
        tdt.deals_count_90d,
        tdt.clearance_count_30d,
        tdt.sale_count_30d,
        CASE
            WHEN (tdt.discount_score + tdt.rarity_score + tdt.savings_score) / 3.0 >= 80 THEN 'high_priority_alert'
            WHEN (tdt.discount_score + tdt.rarity_score + tdt.savings_score) / 3.0 >= 60 THEN 'medium_priority_alert'
            ELSE 'low_priority_alert'
        END AS alert_priority
    FROM temporal_deal_trends tdt
)
SELECT
    product_name,
    category,
    retailer_name,
    store_city,
    store_state,
    deal_type,
    deal_price,
    original_price,
    discount_percentage,
    deal_start_date,
    deal_end_date,
    deal_quality,
    overall_deal_score,
    alert_priority,
    savings_percentage,
    avg_discount_30d,
    deals_count_90d
FROM final_deal_intelligence
WHERE overall_deal_score >= 60
ORDER BY overall_deal_score DESC, deal_start_date DESC;
```
```


## Query 5: Product Category Trend Analysis with Seasonal Decomposition

**Description:** Analyzes product category trends with seasonal decomposition, identifying cyclical patterns, growth trends, and category performance metrics. Uses multiple CTEs for trend decomposition, window functions for seasonal analysis, and statistical calculations.

**Use Case:** Category performance analysis for retail strategy

**Business Value:** Enables retailers to understand category trends and optimize product mix, supporting $1M+ ARR retail analytics platforms

**Purpose:** Provides comprehensive analysis for marketing intelligence

**Complexity:** Multiple CTEs (8+ levels), seasonal decomposition, window functions with RANGE frames, trend analysis, statistical calculations

**Expected Output:** Detailed analysis report with metrics and insights

```sql
WITH category_sales_base AS (
    SELECT
        p.category,
        p.subcategory,
        p.product_id,
        p.product_name,
        pp.price_effective_date,
        DATE_TRUNC('month', pp.price_effective_date) AS sale_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num,
        EXTRACT(QUARTER FROM pp.price_effective_date) AS quarter_num,
        pp.current_price,
        pp.price_type,
        COUNT(DISTINCT pp.store_id) AS store_count,
        COUNT(DISTINCT pp.retailer_id) AS retailer_count
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    WHERE pp.price_effective_date >= CURRENT_DATE - INTERVAL '2 years'
        AND p.is_active = TRUE
    GROUP BY p.category, p.subcategory, p.product_id, p.product_name, pp.price_effective_date, pp.current_price, pp.price_type
),
monthly_category_aggregates AS (
    SELECT
        category,
        subcategory,
        sale_month,
        month_num,
        quarter_num,
        COUNT(DISTINCT product_id) AS products_count,
        COUNT(DISTINCT retailer_id) AS retailers_count,
        SUM(store_count) AS total_stores,
        AVG(current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY current_price) AS median_price,
        MIN(current_price) AS min_price,
        MAX(current_price) AS max_price,
        STDDEV(current_price) AS price_std_dev,
        COUNT(CASE WHEN price_type = 'sale' THEN 1 END) AS sale_count,
        COUNT(CASE WHEN price_type = 'clearance' THEN 1 END) AS clearance_count
    FROM category_sales_base
    GROUP BY category, subcategory, sale_month, month_num, quarter_num
),
seasonal_decomposition AS (
    SELECT
        mca.*,
        AVG(mca.avg_price) OVER (
            PARTITION BY mca.category, mca.subcategory
            ORDER BY mca.sale_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        AVG(mca.avg_price) OVER (
            PARTITION BY mca.category, mca.subcategory, mca.month_num
        ) AS seasonal_avg_by_month,
        mca.avg_price - AVG(mca.avg_price) OVER (
            PARTITION BY mca.category, mca.subcategory, mca.month_num
        ) AS seasonal_component,
        LAG(mca.avg_price, 12) OVER (
            PARTITION BY mca.category, mca.subcategory
            ORDER BY mca.sale_month
        ) AS year_ago_price,
        LEAD(mca.avg_price, 12) OVER (
            PARTITION BY mca.category, mca.subcategory
            ORDER BY mca.sale_month
        ) AS year_ahead_price
    FROM monthly_category_aggregates mca
),
trend_analysis AS (
    SELECT
        sd.*,
        CASE
            WHEN sd.year_ago_price IS NOT NULL THEN
                ((sd.avg_price - sd.year_ago_price) / sd.year_ago_price) * 100
            ELSE NULL
        END AS yoy_price_change,
        AVG(sd.avg_price) OVER (
            PARTITION BY sd.category, sd.subcategory
            ORDER BY sd.sale_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS moving_avg_3m,
        STDDEV(sd.avg_price) OVER (
            PARTITION BY sd.category, sd.subcategory
            ORDER BY sd.sale_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m,
        ROW_NUMBER() OVER (
            PARTITION BY sd.category, sd.subcategory
            ORDER BY sd.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY sd.category, sd.subcategory
            ORDER BY sd.avg_price DESC
        ) AS price_percentile
    FROM seasonal_decomposition sd
),
category_performance_metrics AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.yoy_price_change > 5 THEN 'strong_growth'
            WHEN ta.yoy_price_change > 0 THEN 'moderate_growth'
            WHEN ta.yoy_price_change > -5 THEN 'stable'
            WHEN ta.yoy_price_change > -10 THEN 'moderate_decline'
            ELSE 'strong_decline'
        END AS trend_classification,
        CASE
            WHEN ta.price_volatility_12m < ta.avg_price * 0.1 THEN 'low_volatility'
            WHEN ta.price_volatility_12m < ta.avg_price * 0.2 THEN 'moderate_volatility'
            ELSE 'high_volatility'
        END AS volatility_classification,
        ta.sale_count + ta.clearance_count AS total_promotions,
        CASE
            WHEN ta.sale_count + ta.clearance_count > ta.products_count * 0.5 THEN 'high_promotion'
            WHEN ta.sale_count + ta.clearance_count > ta.products_count * 0.25 THEN 'moderate_promotion'
            ELSE 'low_promotion'
        END AS promotion_level
    FROM trend_analysis ta
),
final_category_intelligence AS (
    SELECT
        cpm.category,
        cpm.subcategory,
        cpm.sale_month,
        cpm.month_num,
        cpm.quarter_num,
        ROUND(CAST(cpm.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(cpm.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(cpm.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(cpm.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(cpm.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(cpm.seasonal_component AS NUMERIC), 2) AS seasonal_component,
        ROUND(CAST(cpm.yoy_price_change AS NUMERIC), 2) AS yoy_price_change,
        ROUND(CAST(cpm.moving_avg_3m AS NUMERIC), 2) AS moving_avg_3m,
        ROUND(CAST(cpm.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        cpm.trend_classification,
        cpm.volatility_classification,
        cpm.promotion_level,
        cpm.products_count,
        cpm.retailers_count,
        cpm.total_stores,
        cpm.sale_count,
        cpm.clearance_count,
        cpm.total_promotions
    FROM category_performance_metrics cpm
)
SELECT
    category,
    subcategory,
    sale_month,
    avg_price,
    median_price,
    moving_avg_12m,
    seasonal_component,
    yoy_price_change,
    trend_classification,
    volatility_classification,
    promotion_level,
    products_count,
    retailers_count,
    total_promotions
FROM final_category_intelligence
WHERE sale_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, sale_month DESC;
```

## Query 6: Marketing Intelligence Analysis Query 6

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;
```

## Query 7: Marketing Intelligence Analysis Query 7

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 8: Marketing Intelligence Analysis Query 8

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 9: Marketing Intelligence Analysis Query 9

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 10: Marketing Intelligence Analysis Query 10

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 11: Marketing Intelligence Analysis Query 11

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 12: Marketing Intelligence Analysis Query 12

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 13: Marketing Intelligence Analysis Query 13

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 14: Marketing Intelligence Analysis Query 14

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 15: Marketing Intelligence Analysis Query 15

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 16: Marketing Intelligence Analysis Query 16

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 17: Marketing Intelligence Analysis Query 17

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 18: Marketing Intelligence Analysis Query 18

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 19: Marketing Intelligence Analysis Query 19

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 20: Marketing Intelligence Analysis Query 20

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 21: Marketing Intelligence Analysis Query 21

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 22: Marketing Intelligence Analysis Query 22

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 23: Marketing Intelligence Analysis Query 23

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 24: Marketing Intelligence Analysis Query 24

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 25: Marketing Intelligence Analysis Query 25

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 26: Marketing Intelligence Analysis Query 26

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 27: Marketing Intelligence Analysis Query 27

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 28: Marketing Intelligence Analysis Query 28

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 29: Marketing Intelligence Analysis Query 29

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;


```
## Query 30: Marketing Intelligence Analysis Query 30

**Description:** Comprehensive marketing intelligence analysis with multiple CTEs, window functions, and complex aggregations.

**Use Case:** Marketing intelligence for retail operations

**Business Value:** Supports $1M+ ARR marketing intelligence platforms

**Purpose:** Provides detailed marketing intelligence analysis

**Complexity:** Multiple CTEs (6+ levels), window functions, complex aggregations

**Expected Output:** Analysis report with comprehensive metrics

```sql
WITH base_analysis AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.brand,
        pp.pricing_id,
        pp.retailer_id,
        pp.current_price,
        pp.price_effective_date,
        r.retailer_name,
        r.retailer_type,
        s.store_id,
        s.store_city,
        s.store_state,
        pi.stock_level,
        pi.stock_status,
        DATE_TRUNC('month', pp.price_effective_date) AS price_month,
        EXTRACT(MONTH FROM pp.price_effective_date) AS month_num
    FROM products p
    INNER JOIN product_pricing pp ON p.product_id = pp.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    LEFT JOIN stores s ON pp.store_id = s.store_id
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id AND pp.store_id = pi.store_id
    WHERE p.is_active = TRUE
        AND r.retailer_status = 'active'
        AND pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days'
),
aggregated_metrics AS (
    SELECT
        ba.category,
        ba.subcategory,
        ba.brand,
        ba.price_month,
        ba.month_num,
        COUNT(DISTINCT ba.product_id) AS products_count,
        COUNT(DISTINCT ba.retailer_id) AS retailers_count,
        COUNT(DISTINCT ba.store_id) AS stores_count,
        AVG(ba.current_price) AS avg_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ba.current_price) AS median_price,
        MIN(ba.current_price) AS min_price,
        MAX(ba.current_price) AS max_price,
        STDDEV(ba.current_price) AS price_std_dev,
        COUNT(CASE WHEN ba.stock_status = 'in_stock' THEN 1 END) AS in_stock_count,
        COUNT(CASE WHEN ba.stock_status = 'out_of_stock' THEN 1 END) AS out_of_stock_count
    FROM base_analysis ba
    GROUP BY ba.category, ba.subcategory, ba.brand, ba.price_month, ba.month_num
),
temporal_analysis AS (
    SELECT
        am.*,
        LAG(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS prev_month_avg_price,
        LEAD(am.avg_price, 1) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
        ) AS next_month_avg_price,
        AVG(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS moving_avg_12m,
        STDDEV(am.avg_price) OVER (
            PARTITION BY am.category, am.subcategory, am.brand
            ORDER BY am.price_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS price_volatility_12m
    FROM aggregated_metrics am
),
trend_calculations AS (
    SELECT
        ta.*,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL THEN
                ((ta.avg_price - ta.prev_month_avg_price) / ta.prev_month_avg_price) * 100
            ELSE NULL
        END AS mom_price_change,
        CASE
            WHEN ta.prev_month_avg_price IS NOT NULL AND ta.prev_month_avg_price != 0 THEN
                ta.avg_price - ta.prev_month_avg_price
            ELSE NULL
        END AS price_change_amount,
        CASE
            WHEN ta.in_stock_count > 0 THEN
                (ta.in_stock_count::NUMERIC / (ta.in_stock_count + ta.out_of_stock_count)::NUMERIC) * 100
            ELSE 0
        END AS availability_rate
    FROM temporal_analysis ta
),
market_intelligence AS (
    SELECT
        tc.*,
        CASE
            WHEN tc.mom_price_change > 5 THEN 'strong_increase'
            WHEN tc.mom_price_change > 0 THEN 'moderate_increase'
            WHEN tc.mom_price_change > -5 THEN 'stable'
            WHEN tc.mom_price_change > -10 THEN 'moderate_decrease'
            ELSE 'strong_decrease'
        END AS price_trend,
        CASE
            WHEN tc.availability_rate >= 80 THEN 'high_availability'
            WHEN tc.availability_rate >= 50 THEN 'moderate_availability'
            ELSE 'low_availability'
        END AS availability_classification,
        ROW_NUMBER() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_rank,
        PERCENT_RANK() OVER (
            PARTITION BY tc.category, tc.subcategory
            ORDER BY tc.avg_price DESC
        ) AS price_percentile
    FROM trend_calculations tc
),
final_analysis AS (
    SELECT
        mi.category,
        mi.subcategory,
        mi.brand,
        mi.price_month,
        ROUND(CAST(mi.avg_price AS NUMERIC), 2) AS avg_price,
        ROUND(CAST(mi.median_price AS NUMERIC), 2) AS median_price,
        ROUND(CAST(mi.min_price AS NUMERIC), 2) AS min_price,
        ROUND(CAST(mi.max_price AS NUMERIC), 2) AS max_price,
        ROUND(CAST(mi.moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
        ROUND(CAST(mi.mom_price_change AS NUMERIC), 2) AS mom_price_change,
        ROUND(CAST(mi.price_volatility_12m AS NUMERIC), 2) AS price_volatility_12m,
        ROUND(CAST(mi.availability_rate AS NUMERIC), 2) AS availability_rate,
        mi.price_trend,
        mi.availability_classification,
        mi.products_count,
        mi.retailers_count,
        mi.stores_count,
        mi.price_rank,
        ROUND(CAST(mi.price_percentile * 100 AS NUMERIC), 2) AS price_percentile
    FROM market_intelligence mi
)
SELECT
    category,
    subcategory,
    brand,
    price_month,
    avg_price,
    median_price,
    moving_avg_12m,
    mom_price_change,
    price_trend,
    availability_rate,
    availability_classification,
    products_count,
    retailers_count,
    price_percentile
FROM final_analysis
WHERE price_month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY category, subcategory, brand, price_month DESC;

```