#!/usr/bin/env python3
"""
Expand template queries 5-30 with fully complex SQL
Each query will have 6+ CTEs, window functions, complex aggregations
"""

import re
from pathlib import Path

def generate_complex_query_5():
    """Query 5: Product Category Trend Analysis with Seasonal Decomposition"""
    return """```sql
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
```"""

# Read queries file
queries_file = Path(__file__).parent.parent / "queries" / "queries.md"
with open(queries_file, 'r') as f:
    content = f.read()

# Replace query 5 template
query_5_pattern = r'```sql\nWITH base_data AS \([\s\S]*?```'
query_5_replacement = generate_complex_query_5()

# Find and replace query 5
query_5_section = re.search(r'## Query 5:.*?```sql\nWITH base_data AS.*?```', content, re.DOTALL)
if query_5_section:
    old_query_5 = query_5_section.group(0)
    # Extract the header part
    header_match = re.search(r'(## Query 5:.*?\*\*Expected Output:\*\*.*?\n)', old_query_5, re.DOTALL)
    if header_match:
        new_query_5 = header_match.group(1) + '\n' + query_5_replacement
        content = content.replace(old_query_5, new_query_5)
        print("Query 5 replaced")
    else:
        print("Could not find Query 5 header")
else:
    print("Query 5 template not found")

# Write back
with open(queries_file, 'w') as f:
    f.write(content)

print("File updated")
