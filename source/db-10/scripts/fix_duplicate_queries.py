#!/usr/bin/env python3
"""Replace duplicate queries 7-30 in db-10 with unique SQL. Run from repo root."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent  # repo root
QUERIES_MD = ROOT / "source" / "db-10" / "app" / "QUERIES" / "queries.md"

# 24 unique SQL queries for queries 7-30 (each uses CTEs, db-10 schema, distinct logic)
UNIQUE_QUERIES = {
    7: """WITH census_monthly AS (
    SELECT year, month, industry_category, retail_sales_amount, inventory_amount,
        sales_change_percent, inventory_change_percent,
        LAG(retail_sales_amount) OVER (PARTITION BY industry_category ORDER BY year, month) AS prev_sales,
        AVG(retail_sales_amount) OVER (PARTITION BY industry_category ORDER BY year, month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS moving_avg_12m
    FROM census_retail_data
    WHERE year >= EXTRACT(YEAR FROM CURRENT_DATE) - 3
),
yoy_growth AS (
    SELECT *, CASE WHEN prev_sales > 0 THEN ((retail_sales_amount - prev_sales) / prev_sales) * 100 ELSE NULL END AS mom_growth
    FROM census_monthly
)
SELECT industry_category, year, month, retail_sales_amount, inventory_amount,
    ROUND(CAST(moving_avg_12m AS NUMERIC), 2) AS moving_avg_12m,
    sales_change_percent, mom_growth
FROM yoy_growth
ORDER BY industry_category, year DESC, month DESC
LIMIT 100""",

    8: """WITH bls_by_category AS (
    SELECT product_category, year, period, price_index_value, percent_change, percent_change_year_ago, index_type,
        AVG(price_index_value) OVER (PARTITION BY product_category ORDER BY year, period ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS moving_avg_4q,
        ROW_NUMBER() OVER (PARTITION BY product_category ORDER BY year DESC, period DESC) AS recency_rank
    FROM bls_price_data
    WHERE year >= EXTRACT(YEAR FROM CURRENT_DATE) - 2
),
category_trends AS (
    SELECT *, PERCENT_RANK() OVER (PARTITION BY year ORDER BY percent_change_year_ago DESC) AS change_percentile
    FROM bls_by_category
)
SELECT product_category, year, period, price_index_value, percent_change_year_ago, index_type,
    ROUND(CAST(moving_avg_4q AS NUMERIC), 2) AS moving_avg_4q, change_percentile
FROM category_trends
WHERE recency_rank <= 12
ORDER BY product_category, year DESC, period DESC
LIMIT 100""",

    9: """WITH mi_by_market AS (
    SELECT mi.product_id, p.product_name, p.category, mi.market_area, mi.market_type,
        mi.average_price, mi.median_price, mi.availability_rate, mi.market_share, mi.competitor_count,
        mi.intelligence_date, mi.data_quality_score,
        RANK() OVER (PARTITION BY mi.product_id ORDER BY mi.intelligence_date DESC) AS date_rank
    FROM market_intelligence mi
    INNER JOIN products p ON mi.product_id = p.product_id
    WHERE mi.intelligence_date >= CURRENT_DATE - INTERVAL '90 days' AND p.is_active = TRUE
),
latest_mi AS (
    SELECT * FROM mi_by_market WHERE date_rank = 1
),
market_aggregates AS (
    SELECT market_type, market_area,
        COUNT(DISTINCT product_id) AS product_count,
        AVG(average_price) AS avg_market_price,
        AVG(availability_rate) AS avg_availability,
        SUM(competitor_count) AS total_competitors
    FROM latest_mi
    GROUP BY market_type, market_area
)
SELECT lm.*, ma.product_count, ROUND(CAST(ma.avg_market_price AS NUMERIC), 2) AS market_avg_price
FROM latest_mi lm
LEFT JOIN market_aggregates ma ON lm.market_type = ma.market_type AND lm.market_area = ma.market_area
ORDER BY lm.product_id, lm.market_area
LIMIT 100""",

    10: """WITH deal_summary AS (
    SELECT da.retailer_id, r.retailer_name, da.deal_type, da.product_id, p.category,
        COUNT(*) AS deal_count, AVG(da.discount_percentage) AS avg_discount,
        MIN(da.deal_price) AS min_deal_price, SUM(da.original_price - da.deal_price) AS total_savings
    FROM deal_alerts da
    INNER JOIN retailers r ON da.retailer_id = r.retailer_id
    INNER JOIN products p ON da.product_id = p.product_id
    WHERE da.deal_status = 'active' AND da.deal_start_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY da.retailer_id, r.retailer_name, da.deal_type, da.product_id, p.category
),
retailer_deals AS (
    SELECT retailer_id, retailer_name, deal_type,
        SUM(deal_count) AS total_deals, AVG(avg_discount) AS retailer_avg_discount,
        SUM(total_savings) AS total_savings
    FROM deal_summary
    GROUP BY retailer_id, retailer_name, deal_type
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY deal_type ORDER BY total_deals DESC) AS deal_rank
    FROM retailer_deals
)
SELECT retailer_name, deal_type, total_deals, ROUND(CAST(retailer_avg_discount AS NUMERIC), 2) AS avg_discount,
    ROUND(CAST(total_savings AS NUMERIC), 2) AS total_savings, deal_rank
FROM ranked
ORDER BY deal_type, deal_rank
LIMIT 100""",

    11: """WITH pipeline_stats AS (
    SELECT pm.source_id, ds.source_name, ds.source_type, pm.pipeline_type, pm.status,
        pm.records_processed, pm.records_successful, pm.records_failed,
        pm.processing_duration_seconds, pm.extraction_date,
        ROW_NUMBER() OVER (PARTITION BY pm.source_id ORDER BY pm.extraction_date DESC) AS run_rank
    FROM pipeline_metadata pm
    INNER JOIN data_sources ds ON pm.source_id = ds.source_id
    WHERE pm.extraction_date >= CURRENT_TIMESTAMP - INTERVAL '7 days'
),
latest_runs AS (
    SELECT * FROM pipeline_stats WHERE run_rank = 1
),
source_quality AS (
    SELECT source_id, source_name, source_type,
        SUM(records_processed) AS total_processed, SUM(records_successful) AS total_success,
        AVG(processing_duration_seconds) AS avg_duration,
        COUNT(CASE WHEN status = 'success' THEN 1 END) AS success_count,
        COUNT(*) AS total_runs
    FROM pipeline_metadata
    WHERE extraction_date >= CURRENT_TIMESTAMP - INTERVAL '30 days'
    GROUP BY source_id, source_name, source_type
)
SELECT sq.*, lr.status AS last_status, lr.extraction_date AS last_run,
    CASE WHEN sq.total_processed > 0 THEN (sq.total_success::NUMERIC / sq.total_processed) * 100 ELSE 0 END AS success_rate
FROM source_quality sq
LEFT JOIN latest_runs lr ON sq.source_id = lr.source_id
ORDER BY sq.total_processed DESC
LIMIT 100""",

    12: """WITH store_density AS (
    SELECT store_state, store_city, COUNT(*) AS store_count,
        COUNT(DISTINCT retailer_id) AS retailer_count,
        AVG(store_size_sqft) AS avg_size
    FROM stores
    WHERE store_status = 'open'
    GROUP BY store_state, store_city
),
state_totals AS (
    SELECT store_state, SUM(store_count) AS state_stores, SUM(retailer_count) AS state_retailers
    FROM store_density
    GROUP BY store_state
),
density_ranked AS (
    SELECT sd.*, st.state_stores,
        (sd.store_count::NUMERIC / NULLIF(st.state_stores, 0)) * 100 AS pct_of_state,
        RANK() OVER (PARTITION BY sd.store_state ORDER BY sd.store_count DESC) AS city_rank
    FROM store_density sd
    INNER JOIN state_totals st ON sd.store_state = st.store_state
)
SELECT store_state, store_city, store_count, retailer_count, ROUND(CAST(avg_size AS NUMERIC), 0) AS avg_size,
    state_stores, ROUND(CAST(pct_of_state AS NUMERIC), 2) AS pct_of_state, city_rank
FROM density_ranked
ORDER BY store_state, city_rank
LIMIT 100""",

    13: """WITH product_retailer_availability AS (
    SELECT p.product_id, p.product_name, p.category, r.retailer_id, r.retailer_name,
        COUNT(DISTINCT pi.store_id) AS stores_with_stock,
        COUNT(DISTINCT pp.store_id) AS stores_with_pricing,
        SUM(CASE WHEN pi.stock_status = 'in_stock' THEN 1 ELSE 0 END) AS in_stock_count,
        AVG(pp.current_price) AS avg_price
    FROM products p
    CROSS JOIN retailers r
    LEFT JOIN product_inventory pi ON p.product_id = pi.product_id
        AND EXISTS (SELECT 1 FROM stores s WHERE s.store_id = pi.store_id AND s.retailer_id = r.retailer_id)
    LEFT JOIN product_pricing pp ON p.product_id = pp.product_id AND pp.retailer_id = r.retailer_id
    WHERE p.is_active = TRUE AND r.retailer_status = 'active'
    GROUP BY p.product_id, p.product_name, p.category, r.retailer_id, r.retailer_name
),
availability_pct AS (
    SELECT *, CASE WHEN stores_with_pricing > 0 THEN (in_stock_count::NUMERIC / stores_with_pricing) * 100 ELSE 0 END AS availability_pct
    FROM product_retailer_availability
)
SELECT product_name, category, retailer_name, stores_with_stock, stores_with_pricing,
    ROUND(CAST(availability_pct AS NUMERIC), 2) AS availability_pct,
    ROUND(CAST(avg_price AS NUMERIC), 2) AS avg_price
FROM availability_pct
WHERE stores_with_pricing > 0
ORDER BY product_id, availability_pct DESC
LIMIT 100""",

    14: """WITH category_pricing AS (
    SELECT p.category, p.subcategory, pp.retailer_id, r.retailer_name,
        AVG(pp.current_price) AS avg_price, STDDEV(pp.current_price) AS price_std,
        MIN(pp.current_price) AS min_price, MAX(pp.current_price) AS max_price,
        COUNT(DISTINCT pp.product_id) AS product_count
    FROM product_pricing pp
    INNER JOIN products p ON pp.product_id = p.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    WHERE pp.price_effective_date >= CURRENT_DATE - INTERVAL '90 days' AND p.is_active = TRUE
    GROUP BY p.category, p.subcategory, pp.retailer_id, r.retailer_name
),
category_baseline AS (
    SELECT category, subcategory, AVG(avg_price) AS category_avg, STDDEV(avg_price) AS category_std
    FROM category_pricing
    GROUP BY category, subcategory
),
price_position AS (
    SELECT cp.*, cb.category_avg,
        (cp.avg_price - cb.category_avg) / NULLIF(cb.category_std, 0) AS price_z_score,
        PERCENT_RANK() OVER (PARTITION BY cp.category, cp.subcategory ORDER BY cp.avg_price) AS price_percentile
    FROM category_pricing cp
    INNER JOIN category_baseline cb ON cp.category = cb.category AND cp.subcategory = cb.subcategory
)
SELECT category, subcategory, retailer_name, ROUND(CAST(avg_price AS NUMERIC), 2) AS avg_price,
    ROUND(CAST(price_std AS NUMERIC), 2) AS price_std, product_count,
    ROUND(CAST(price_z_score AS NUMERIC), 2) AS price_z_score,
    ROUND(CAST(price_percentile * 100 AS NUMERIC), 2) AS price_percentile
FROM price_position
ORDER BY category, subcategory, avg_price
LIMIT 100""",

    15: """WITH geo_market_stats AS (
    SELECT gm.market_id, gm.market_name, gm.market_type, gm.state_code, gm.population, gm.median_income,
        COUNT(DISTINCT s.store_id) AS store_count,
        COUNT(DISTINCT s.retailer_id) AS retailer_count
    FROM geographic_markets gm
    LEFT JOIN stores s ON (gm.market_type = 'state' AND s.store_state = gm.state_code)
        OR (gm.market_type = 'zip' AND s.store_zip = gm.market_code)
    WHERE s.store_status = 'open' OR s.store_id IS NULL
    GROUP BY gm.market_id, gm.market_name, gm.market_type, gm.state_code, gm.population, gm.median_income
),
market_density AS (
    SELECT *, CASE WHEN population > 0 THEN store_count::NUMERIC / (population / 10000) ELSE 0 END AS stores_per_10k
    FROM geo_market_stats
)
SELECT market_name, market_type, state_code, population, median_income, store_count, retailer_count,
    ROUND(CAST(stores_per_10k AS NUMERIC), 4) AS stores_per_10k_pop
FROM market_density
WHERE population IS NOT NULL
ORDER BY stores_per_10k DESC
LIMIT 100""",

    16: """WITH brand_pricing AS (
    SELECT p.brand, p.category, pp.current_price, pp.price_type, pp.price_effective_date,
        ROW_NUMBER() OVER (PARTITION BY p.brand, p.category ORDER BY pp.price_effective_date DESC) AS price_rank
    FROM product_pricing pp
    INNER JOIN products p ON pp.product_id = p.product_id
    WHERE pp.price_effective_date >= CURRENT_DATE - INTERVAL '180 days' AND p.is_active = TRUE AND p.brand IS NOT NULL
),
latest_brand_prices AS (
    SELECT brand, category, current_price, price_type FROM brand_pricing WHERE price_rank = 1
),
brand_aggregates AS (
    SELECT brand, category,
        COUNT(*) AS product_count, AVG(current_price) AS avg_price,
        MIN(current_price) AS min_price, MAX(current_price) AS max_price,
        COUNT(CASE WHEN price_type = 'sale' THEN 1 END) AS sale_count
    FROM latest_brand_prices
    GROUP BY brand, category
)
SELECT brand, category, product_count, ROUND(CAST(avg_price AS NUMERIC), 2) AS avg_price,
    ROUND(CAST(min_price AS NUMERIC), 2) AS min_price, ROUND(CAST(max_price AS NUMERIC), 2) AS max_price, sale_count
FROM brand_aggregates
ORDER BY brand, category
LIMIT 100""",

    17: """WITH retailer_store_summary AS (
    SELECT r.retailer_id, r.retailer_name, r.retailer_type, r.market_coverage,
        COUNT(s.store_id) AS store_count,
        COUNT(DISTINCT s.store_state) AS state_count,
        AVG(s.store_size_sqft) AS avg_store_size
    FROM retailers r
    LEFT JOIN stores s ON r.retailer_id = s.retailer_id AND s.store_status = 'open'
    WHERE r.retailer_status = 'active'
    GROUP BY r.retailer_id, r.retailer_name, r.retailer_type, r.market_coverage
),
retailer_products AS (
    SELECT pp.retailer_id, COUNT(DISTINCT pp.product_id) AS product_count,
        AVG(pp.current_price) AS avg_price
    FROM product_pricing pp
    WHERE pp.price_effective_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY pp.retailer_id
)
SELECT rss.*, rp.product_count, ROUND(CAST(rp.avg_price AS NUMERIC), 2) AS avg_price,
    ROUND(CAST(rss.avg_store_size AS NUMERIC), 0) AS avg_store_size
FROM retailer_store_summary rss
LEFT JOIN retailer_products rp ON rss.retailer_id = rp.retailer_id
ORDER BY rss.store_count DESC
LIMIT 100""",

    18: """WITH inventory_trends AS (
    SELECT pi.product_id, p.product_name, p.category, pi.store_id, pi.stock_level, pi.stock_status,
        pi.last_checked_at, pi.last_restocked_at,
        DATE_TRUNC('week', pi.last_checked_at) AS check_week,
        LAG(pi.stock_level) OVER (PARTITION BY pi.product_id, pi.store_id ORDER BY pi.last_checked_at) AS prev_stock
    FROM product_inventory pi
    INNER JOIN products p ON pi.product_id = p.product_id
    WHERE pi.last_checked_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'
),
weekly_aggregates AS (
    SELECT product_id, product_name, category, check_week,
        AVG(stock_level) AS avg_stock, AVG(CASE WHEN stock_status = 'in_stock' THEN 1.0 ELSE 0 END) AS in_stock_rate,
        COUNT(DISTINCT store_id) AS store_count
    FROM inventory_trends
    GROUP BY product_id, product_name, category, check_week
),
with_trend AS (
    SELECT *, LAG(avg_stock) OVER (PARTITION BY product_id ORDER BY check_week) AS prev_week_stock
    FROM weekly_aggregates
)
SELECT product_name, category, check_week, ROUND(CAST(avg_stock AS NUMERIC), 2) AS avg_stock,
    ROUND(CAST(in_stock_rate * 100 AS NUMERIC), 2) AS in_stock_pct, store_count,
    CASE WHEN prev_week_stock > 0 THEN ROUND(CAST(((avg_stock - prev_week_stock) / prev_week_stock) * 100 AS NUMERIC), 2) ELSE NULL END AS wow_change
FROM with_trend
ORDER BY product_id, check_week DESC
LIMIT 100""",

    19: """WITH deal_timing AS (
    SELECT da.deal_id, da.product_id, p.category, da.retailer_id, da.deal_type,
        da.deal_start_date, da.deal_end_date, da.discount_percentage,
        EXTRACT(DOW FROM da.deal_start_date) AS start_dow,
        EXTRACT(MONTH FROM da.deal_start_date) AS start_month,
        (COALESCE(da.deal_end_date, da.deal_start_date) - da.deal_start_date) AS duration_days
    FROM deal_alerts da
    INNER JOIN products p ON da.product_id = p.product_id
    WHERE da.deal_start_date >= CURRENT_DATE - INTERVAL '180 days'
),
timing_patterns AS (
    SELECT deal_type, start_dow, start_month,
        COUNT(*) AS deal_count, AVG(discount_percentage) AS avg_discount,
        AVG(duration_days) AS avg_duration
    FROM deal_timing
    GROUP BY deal_type, start_dow, start_month
)
SELECT deal_type, start_dow, start_month, deal_count,
    ROUND(CAST(avg_discount AS NUMERIC), 2) AS avg_discount,
    ROUND(CAST(avg_duration AS NUMERIC), 1) AS avg_duration_days
FROM timing_patterns
ORDER BY deal_type, deal_count DESC
LIMIT 100""",

    20: """WITH naics_retail AS (
    SELECT naics_code, industry_category, year, month,
        retail_sales_amount, inventory_amount, sales_change_percent,
        SUM(retail_sales_amount) OVER (PARTITION BY year ORDER BY month) AS ytd_sales,
        AVG(retail_sales_amount) OVER (PARTITION BY industry_category ORDER BY year, month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3m
    FROM census_retail_data
    WHERE year >= EXTRACT(YEAR FROM CURRENT_DATE) - 2
),
industry_rank AS (
    SELECT *, RANK() OVER (PARTITION BY year, month ORDER BY retail_sales_amount DESC) AS sales_rank
    FROM naics_retail
)
SELECT naics_code, industry_category, year, month, retail_sales_amount, inventory_amount,
    ROUND(CAST(ytd_sales AS NUMERIC), 2) AS ytd_sales,
    ROUND(CAST(moving_avg_3m AS NUMERIC), 2) AS moving_avg_3m, sales_rank
FROM industry_rank
ORDER BY year DESC, month DESC, sales_rank
LIMIT 100""",

    21: """WITH product_market_coverage AS (
    SELECT mi.product_id, p.product_name, mi.market_type,
        COUNT(DISTINCT mi.market_area) AS market_count,
        AVG(mi.average_price) AS avg_price, AVG(mi.availability_rate) AS avg_availability,
        SUM(mi.competitor_count) AS total_competitors
    FROM market_intelligence mi
    INNER JOIN products p ON mi.product_id = p.product_id
    WHERE mi.intelligence_date >= CURRENT_DATE - INTERVAL '60 days'
    GROUP BY mi.product_id, p.product_name, mi.market_type
),
national_vs_regional AS (
    SELECT product_id, product_name,
        MAX(CASE WHEN market_type = 'national' THEN market_count END) AS national_markets,
        MAX(CASE WHEN market_type = 'state' THEN market_count END) AS state_markets,
        MAX(CASE WHEN market_type = 'city' THEN market_count END) AS city_markets
    FROM product_market_coverage
    GROUP BY product_id, product_name
)
SELECT pmc.*, nvr.national_markets, nvr.state_markets, nvr.city_markets
FROM product_market_coverage pmc
LEFT JOIN national_vs_regional nvr ON pmc.product_id = nvr.product_id
ORDER BY pmc.product_id, pmc.market_type
LIMIT 100""",

    22: """WITH data_source_health AS (
    SELECT ds.source_id, ds.source_name, ds.source_type, ds.data_quality_score, ds.is_active,
        pm.status AS last_status, pm.records_processed, pm.records_successful, pm.records_failed,
        pm.extraction_date, pm.processing_duration_seconds,
        ROW_NUMBER() OVER (PARTITION BY ds.source_id ORDER BY pm.extraction_date DESC) AS rn
    FROM data_sources ds
    LEFT JOIN pipeline_metadata pm ON ds.source_id = pm.source_id
    WHERE ds.is_active = TRUE
),
latest_health AS (
    SELECT * FROM data_source_health WHERE rn = 1
)
SELECT source_name, source_type, data_quality_score, last_status, records_processed,
    records_successful, records_failed, extraction_date, processing_duration_seconds
FROM latest_health
ORDER BY data_quality_score DESC NULLS LAST
LIMIT 100""",

    23: """WITH store_product_matrix AS (
    SELECT s.store_id, s.store_city, s.store_state, s.retailer_id, r.retailer_name,
        pi.product_id, p.category, pi.stock_level, pi.stock_status,
        pp.current_price
    FROM stores s
    INNER JOIN retailers r ON s.retailer_id = r.retailer_id
    LEFT JOIN product_inventory pi ON s.store_id = pi.store_id
    LEFT JOIN products p ON pi.product_id = p.product_id
    LEFT JOIN product_pricing pp ON pi.product_id = pp.product_id AND pp.store_id = s.store_id
    WHERE s.store_status = 'open' AND r.retailer_status = 'active'
),
city_category_summary AS (
    SELECT store_city, store_state, category,
        COUNT(DISTINCT store_id) AS store_count,
        COUNT(DISTINCT CASE WHEN stock_status = 'in_stock' THEN product_id END) AS products_in_stock,
        AVG(current_price) AS avg_price
    FROM store_product_matrix
    WHERE category IS NOT NULL
    GROUP BY store_city, store_state, category
)
SELECT store_city, store_state, category, store_count, products_in_stock,
    ROUND(CAST(avg_price AS NUMERIC), 2) AS avg_price
FROM city_category_summary
ORDER BY store_state, store_city, store_count DESC
LIMIT 100""",

    24: """WITH bls_inflation AS (
    SELECT product_category, year, period, price_index_value, percent_change_year_ago, index_type,
        LAG(price_index_value) OVER (PARTITION BY product_category ORDER BY year, period) AS prev_index,
        AVG(percent_change_year_ago) OVER (PARTITION BY product_category ORDER BY year, period ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS smoothed_yoy
    FROM bls_price_data
    WHERE index_type IN ('CPI', 'PPI') AND year >= EXTRACT(YEAR FROM CURRENT_DATE) - 3
),
inflation_impact AS (
    SELECT *, CASE WHEN prev_index > 0 THEN ((price_index_value - prev_index) / prev_index) * 100 ELSE NULL END AS period_change
    FROM bls_inflation
)
SELECT product_category, year, period, price_index_value, percent_change_year_ago,
    ROUND(CAST(smoothed_yoy AS NUMERIC), 2) AS smoothed_yoy, index_type
FROM inflation_impact
ORDER BY product_category, year DESC, period DESC
LIMIT 100""",

    25: """WITH online_vs_store AS (
    SELECT pp.product_id, p.category, pp.is_online_price, r.retailer_id,
        AVG(pp.current_price) AS avg_price, COUNT(*) AS price_count,
        AVG(pp.shipping_cost) AS avg_shipping
    FROM product_pricing pp
    INNER JOIN products p ON pp.product_id = p.product_id
    INNER JOIN retailers r ON pp.retailer_id = r.retailer_id
    WHERE pp.price_effective_date >= CURRENT_DATE - INTERVAL '90 days' AND p.is_active = TRUE
    GROUP BY pp.product_id, p.category, pp.is_online_price, r.retailer_id
),
channel_comparison AS (
    SELECT category, retailer_id,
        MAX(CASE WHEN is_online_price THEN avg_price END) AS online_price,
        MAX(CASE WHEN NOT is_online_price THEN avg_price END) AS store_price,
        MAX(CASE WHEN is_online_price THEN avg_shipping END) AS online_shipping
    FROM online_vs_store
    GROUP BY category, retailer_id
)
SELECT category, retailer_id,
    ROUND(CAST(online_price AS NUMERIC), 2) AS online_price,
    ROUND(CAST(store_price AS NUMERIC), 2) AS store_price,
    ROUND(CAST(online_shipping AS NUMERIC), 2) AS online_shipping,
    CASE WHEN store_price > 0 THEN ROUND(CAST(((online_price - store_price) / store_price) * 100 AS NUMERIC), 2) ELSE NULL END AS online_premium_pct
FROM channel_comparison
WHERE online_price IS NOT NULL AND store_price IS NOT NULL
ORDER BY category, online_premium_pct DESC NULLS LAST
LIMIT 100""",

    26: """WITH low_stock_alerts AS (
    SELECT pi.product_id, p.product_name, p.category, pi.store_id, s.retailer_id, r.retailer_name,
        pi.stock_level, pi.reorder_point, pi.stock_status, pi.last_checked_at,
        CASE WHEN pi.reorder_point IS NOT NULL AND pi.stock_level <= pi.reorder_point THEN 1 ELSE 0 END AS below_reorder,
        CASE WHEN pi.stock_status = 'out_of_stock' THEN 1 ELSE 0 END AS is_oos
    FROM product_inventory pi
    INNER JOIN products p ON pi.product_id = p.product_id
    INNER JOIN stores s ON pi.store_id = s.store_id
    INNER JOIN retailers r ON s.retailer_id = r.retailer_id
    WHERE pi.last_checked_at >= CURRENT_TIMESTAMP - INTERVAL '7 days' AND p.is_active = TRUE
),
reorder_priority AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY retailer_id ORDER BY below_reorder DESC, stock_level ASC) AS priority_rank
    FROM low_stock_alerts
    WHERE below_reorder = 1 OR is_oos = 1
)
SELECT product_name, category, retailer_name, store_id, stock_level, reorder_point, stock_status, priority_rank
FROM reorder_priority
ORDER BY retailer_id, priority_rank
LIMIT 100""",

    27: """WITH category_census_match AS (
    SELECT p.category, p.subcategory, crd.industry_category, crd.naics_code,
        crd.retail_sales_amount, crd.year, crd.month,
        ROW_NUMBER() OVER (PARTITION BY p.category, crd.year, crd.month ORDER BY crd.retail_sales_amount DESC) AS industry_rank
    FROM products p
    CROSS JOIN census_retail_data crd
    WHERE crd.year >= EXTRACT(YEAR FROM CURRENT_DATE) - 1
    GROUP BY p.category, p.subcategory, crd.industry_category, crd.naics_code, crd.retail_sales_amount, crd.year, crd.month
),
top_industries AS (
    SELECT * FROM category_census_match WHERE industry_rank <= 3
)
SELECT category, subcategory, industry_category, naics_code, retail_sales_amount, year, month, industry_rank
FROM top_industries
ORDER BY category, year DESC, month DESC, industry_rank
LIMIT 100""",

    28: """WITH deal_depth AS (
    SELECT da.product_id, p.product_name, p.category, da.retailer_id,
        da.deal_price, da.original_price, da.discount_percentage,
        (da.original_price - da.deal_price) AS savings_amount,
        ((da.original_price - da.deal_price) / NULLIF(da.original_price, 0)) * 100 AS savings_pct,
        RANK() OVER (PARTITION BY p.category ORDER BY da.discount_percentage DESC) AS discount_rank
    FROM deal_alerts da
    INNER JOIN products p ON da.product_id = p.product_id
    WHERE da.deal_status = 'active' AND da.deal_start_date >= CURRENT_DATE - INTERVAL '14 days'
),
top_deals AS (
    SELECT * FROM deal_depth WHERE discount_rank <= 5
)
SELECT product_name, category, retailer_id, deal_price, original_price, discount_percentage,
    ROUND(CAST(savings_amount AS NUMERIC), 2) AS savings_amount,
    ROUND(CAST(savings_pct AS NUMERIC), 2) AS savings_pct, discount_rank
FROM top_deals
ORDER BY category, discount_rank
LIMIT 100""",

    29: """WITH gm_population AS (
    SELECT market_id, market_name, market_type, state_code, population, median_income,
        CASE WHEN market_type = 'state' THEN 1 WHEN market_type = 'msa' THEN 2 WHEN market_type = 'county' THEN 3
             WHEN market_type = 'city' THEN 4 WHEN market_type = 'zip' THEN 5 ELSE 6 END AS granularity
    FROM geographic_markets
    WHERE population IS NOT NULL
),
market_hierarchy AS (
    SELECT *, NTILE(4) OVER (ORDER BY population DESC) AS population_quartile,
        PERCENT_RANK() OVER (ORDER BY median_income) AS income_percentile
    FROM gm_population
)
SELECT market_name, market_type, state_code, population, median_income, granularity,
    population_quartile, ROUND(CAST(income_percentile * 100 AS NUMERIC), 2) AS income_percentile
FROM market_hierarchy
ORDER BY population DESC
LIMIT 100""",

    30: """WITH cross_retailer_pricing AS (
    SELECT pp.product_id, p.product_name, p.category,
        COUNT(DISTINCT pp.retailer_id) AS retailer_count,
        MIN(pp.current_price) AS min_price, MAX(pp.current_price) AS max_price,
        AVG(pp.current_price) AS avg_price, STDDEV(pp.current_price) AS price_std
    FROM product_pricing pp
    INNER JOIN products p ON pp.product_id = p.product_id
    WHERE pp.price_effective_date >= CURRENT_DATE - INTERVAL '30 days' AND p.is_active = TRUE
    GROUP BY pp.product_id, p.product_name, p.category
),
price_spread AS (
    SELECT *, (max_price - min_price) AS price_range,
        CASE WHEN avg_price > 0 THEN (price_std / avg_price) * 100 ELSE 0 END AS price_cv_pct
    FROM cross_retailer_pricing
    WHERE retailer_count >= 2
)
SELECT product_name, category, retailer_count, ROUND(CAST(min_price AS NUMERIC), 2) AS min_price,
    ROUND(CAST(max_price AS NUMERIC), 2) AS max_price, ROUND(CAST(avg_price AS NUMERIC), 2) AS avg_price,
    ROUND(CAST(price_range AS NUMERIC), 2) AS price_range, ROUND(CAST(price_cv_pct AS NUMERIC), 2) AS price_cv_pct
FROM price_spread
ORDER BY price_range DESC
LIMIT 100""",
}


def main():
    content = QUERIES_MD.read_text(encoding="utf-8")
    for qnum in range(7, 31):
        if qnum not in UNIQUE_QUERIES:
            continue
        block_start = content.find(f'### Query {qnum} —')
        if block_start == -1:
            continue
        block_end = content.find('\n### Query ', block_start + 1)
        if block_end == -1:
            block_end = len(content)
        block = content[block_start:block_end]
        sql_match = re.search(r'"SQL":\s*"((?:[^"\\]|\\.)*)"', block)
        if sql_match:
            sql = UNIQUE_QUERIES[qnum]
            escaped_sql = sql.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            new_block = block[:sql_match.start(1)] + escaped_sql + block[sql_match.end(1):]
            content = content[:block_start] + new_block + content[block_end:]
    QUERIES_MD.write_text(content, encoding="utf-8")
    print(f"Updated queries 7-30 in {QUERIES_MD}")


if __name__ == "__main__":
    main()
