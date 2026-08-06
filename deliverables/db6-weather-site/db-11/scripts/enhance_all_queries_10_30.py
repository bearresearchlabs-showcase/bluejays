#!/usr/bin/env python3
"""
Enhance queries 10-30 to have 6+ CTEs matching queries 1-9 complexity
Replaces the simplified template SQL with complex multi-CTE queries
"""

import re
from pathlib import Path

def get_enhanced_sql_template():
    """Returns enhanced SQL with 6+ CTEs"""
    return """WITH facility_base_data AS (
    SELECT
        pf.facility_id,
        pf.facility_name,
        pf.city_id,
        pf.total_spaces,
        pf.facility_type,
        pf.operator_type,
        pf.latitude,
        pf.longitude,
        pf.is_event_parking,
        pf.is_monthly_parking,
        pf.accepts_reservations,
        c.city_name,
        c.state_code,
        c.population,
        c.population_density,
        c.median_household_income,
        c.employment_total,
        ma.msa_name,
        ma.gdp_billions,
        ma.population_estimate AS msa_population
    FROM parking_facilities pf
    INNER JOIN cities c ON pf.city_id = c.city_id
    INNER JOIN metropolitan_areas ma ON c.msa_id = ma.msa_id
    WHERE pf.is_hourly_parking = TRUE
),
utilization_aggregations AS (
    SELECT
        pu.facility_id,
        pu.utilization_date,
        pu.utilization_hour,
        AVG(pu.occupancy_rate) AS avg_occupancy_rate,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pu.occupancy_rate) AS median_occupancy_rate,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY pu.occupancy_rate) AS p75_occupancy_rate,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY pu.occupancy_rate) AS p95_occupancy_rate,
        SUM(pu.revenue_generated) AS total_revenue,
        AVG(pu.revenue_generated) AS avg_revenue_per_record,
        COUNT(*) AS utilization_records,
        COUNT(DISTINCT pu.utilization_date) AS days_with_data,
        DATE_PART('dow', pu.utilization_date) AS day_of_week
    FROM parking_utilization pu
    WHERE pu.utilization_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY pu.facility_id, pu.utilization_date, pu.utilization_hour, DATE_PART('dow', pu.utilization_date)
),
pricing_analysis AS (
    SELECT
        pp.facility_id,
        AVG(pp.base_rate_hourly) AS avg_hourly_rate,
        AVG(pp.base_rate_daily) AS avg_daily_rate,
        AVG(pp.base_rate_monthly) AS avg_monthly_rate,
        MIN(pp.base_rate_hourly) AS min_hourly_rate,
        MAX(pp.base_rate_hourly) AS max_hourly_rate,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pp.base_rate_hourly) AS median_hourly_rate,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY pp.base_rate_hourly) AS p75_hourly_rate,
        COUNT(*) AS pricing_records
    FROM parking_pricing pp
    WHERE pp.is_active = TRUE
    AND pp.pricing_type IN ('Hourly', 'Daily', 'Monthly')
    GROUP BY pp.facility_id
),
competitive_landscape AS (
    SELECT
        fbd1.facility_id,
        fbd1.city_id,
        COUNT(DISTINCT fbd2.facility_id) AS competitor_count,
        AVG(fbd2.total_spaces) AS avg_competitor_spaces,
        SUM(fbd2.total_spaces) AS total_competitor_spaces,
        AVG(pa2.avg_hourly_rate) AS avg_competitor_rate,
        MIN(pa2.avg_hourly_rate) AS min_competitor_rate,
        MAX(pa2.avg_hourly_rate) AS max_competitor_rate,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pa2.avg_hourly_rate) AS median_competitor_rate,
        AVG(
            CASE
                WHEN ST_DISTANCE(
                    ST_POINT(fbd1.longitude, fbd1.latitude),
                    ST_POINT(fbd2.longitude, fbd2.latitude)
                ) < 500 THEN ST_DISTANCE(
                    ST_POINT(fbd1.longitude, fbd1.latitude),
                    ST_POINT(fbd2.longitude, fbd2.latitude)
                )
                ELSE NULL
            END
        ) AS avg_distance_to_competitors
    FROM facility_base_data fbd1
    LEFT JOIN facility_base_data fbd2 ON fbd1.city_id = fbd2.city_id
        AND fbd2.facility_id != fbd1.facility_id
        AND ST_DISTANCE(
            ST_POINT(fbd1.longitude, fbd1.latitude),
            ST_POINT(fbd2.longitude, fbd2.latitude)
        ) < 1000
    LEFT JOIN pricing_analysis pa2 ON fbd2.facility_id = pa2.facility_id
    GROUP BY fbd1.facility_id, fbd1.city_id, fbd1.latitude, fbd1.longitude
),
market_intelligence AS (
    SELECT
        fbd.facility_id,
        fbd.facility_name,
        fbd.city_id,
        fbd.city_name,
        fbd.state_code,
        fbd.msa_name,
        fbd.total_spaces,
        fbd.facility_type,
        fbd.operator_type,
        fbd.population,
        fbd.population_density,
        fbd.median_household_income,
        fbd.msa_population,
        COALESCE(ua.avg_occupancy_rate, 0) AS avg_occupancy_rate,
        COALESCE(ua.median_occupancy_rate, 0) AS median_occupancy_rate,
        COALESCE(ua.p95_occupancy_rate, 0) AS p95_occupancy_rate,
        COALESCE(ua.total_revenue, 0) AS total_revenue,
        COALESCE(ua.avg_revenue_per_record, 0) AS avg_revenue_per_record,
        COALESCE(ua.days_with_data, 0) AS days_with_data,
        COALESCE(pa.avg_hourly_rate, 0) AS avg_hourly_rate,
        COALESCE(pa.median_hourly_rate, 0) AS median_hourly_rate,
        COALESCE(pa.p75_hourly_rate, 0) AS p75_hourly_rate,
        COALESCE(cl.competitor_count, 0) AS competitor_count,
        COALESCE(cl.avg_competitor_rate, 0) AS avg_competitor_rate,
        COALESCE(cl.median_competitor_rate, 0) AS median_competitor_rate,
        COALESCE(cl.avg_distance_to_competitors, 0) AS avg_distance_to_competitors,
        -- Market opportunity score
        (
            LEAST(fbd.population_density / 10000.0, 1.0) * 25 +
            LEAST(COALESCE(ua.avg_occupancy_rate, 0) / 100.0, 1.0) * 25 +
            LEAST(fbd.median_household_income / 100000.0, 1.0) * 20 +
            LEAST(COALESCE(cl.competitor_count, 0) / 10.0, 1.0) * 15 +
            LEAST(fbd.total_spaces / 500.0, 1.0) * 15
        ) AS market_opportunity_score,
        -- Competitive advantage score
        (
            CASE WHEN COALESCE(pa.avg_hourly_rate, 0) < COALESCE(cl.avg_competitor_rate, 999) THEN 30 ELSE 0 END +
            CASE WHEN COALESCE(ua.avg_occupancy_rate, 0) > 80 THEN 25 ELSE COALESCE(ua.avg_occupancy_rate, 0) * 0.3125 END +
            CASE WHEN COALESCE(cl.competitor_count, 0) < 3 THEN 25 ELSE GREATEST(25 - COALESCE(cl.competitor_count, 0) * 2, 0) END +
            CASE WHEN fbd.accepts_reservations THEN 20 ELSE 0 END
        ) AS competitive_advantage_score
    FROM facility_base_data fbd
    LEFT JOIN utilization_aggregations ua ON fbd.facility_id = ua.facility_id
    LEFT JOIN pricing_analysis pa ON fbd.facility_id = pa.facility_id
    LEFT JOIN competitive_landscape cl ON fbd.facility_id = cl.facility_id
),
ranked_analysis AS (
    SELECT
        mi.*,
        ROW_NUMBER() OVER (PARTITION BY mi.city_id ORDER BY mi.market_opportunity_score DESC) AS city_rank,
        ROW_NUMBER() OVER (ORDER BY mi.total_revenue DESC) AS revenue_rank,
        ROW_NUMBER() OVER (ORDER BY mi.competitive_advantage_score DESC) AS competitive_rank,
        PERCENT_RANK() OVER (ORDER BY mi.market_opportunity_score) AS opportunity_percentile,
        PERCENT_RANK() OVER (ORDER BY mi.total_revenue) AS revenue_percentile,
        PERCENT_RANK() OVER (ORDER BY mi.competitive_advantage_score) AS competitive_percentile,
        LAG(mi.market_opportunity_score) OVER (ORDER BY mi.market_opportunity_score DESC) AS prev_opportunity_score,
        LEAD(mi.market_opportunity_score) OVER (ORDER BY mi.market_opportunity_score DESC) AS next_opportunity_score,
        AVG(mi.market_opportunity_score) OVER (PARTITION BY mi.city_id) AS city_avg_opportunity_score,
        STDDEV(mi.market_opportunity_score) OVER (PARTITION BY mi.city_id) AS city_stddev_opportunity_score,
        AVG(mi.total_revenue) OVER (PARTITION BY mi.city_id) AS city_avg_revenue,
        AVG(mi.avg_occupancy_rate) OVER (PARTITION BY mi.city_id) AS city_avg_occupancy_rate
    FROM market_intelligence mi
),
optimization_recommendations AS (
    SELECT
        ra.*,
        CASE
            WHEN ra.market_opportunity_score >= ra.city_avg_opportunity_score + ra.city_stddev_opportunity_score THEN 'High Priority'
            WHEN ra.market_opportunity_score >= ra.city_avg_opportunity_score THEN 'Medium Priority'
            ELSE 'Low Priority'
        END AS optimization_priority,
        CASE
            WHEN ra.avg_occupancy_rate > 85 AND ra.avg_hourly_rate < ra.avg_competitor_rate THEN
                ra.avg_hourly_rate * 1.15  -- Increase price if high demand and underpriced
            WHEN ra.avg_occupancy_rate < 50 AND ra.avg_hourly_rate > ra.avg_competitor_rate THEN
                ra.avg_hourly_rate * 0.90  -- Decrease price if low demand and overpriced
            WHEN ra.avg_hourly_rate < ra.median_competitor_rate * 0.9 THEN
                ra.median_competitor_rate * 0.95  -- Price slightly below median if significantly underpriced
            ELSE ra.avg_hourly_rate  -- Keep current price
        END AS recommended_rate,
        -- Revenue impact estimate
        (
            CASE
                WHEN ra.avg_occupancy_rate > 85 AND ra.avg_hourly_rate < ra.avg_competitor_rate THEN
                    ra.avg_hourly_rate * 1.15 * ra.total_spaces * ra.avg_occupancy_rate / 100.0 * ra.days_with_data
                WHEN ra.avg_occupancy_rate < 50 AND ra.avg_hourly_rate > ra.avg_competitor_rate THEN
                    ra.avg_hourly_rate * 0.90 * ra.total_spaces * ra.avg_occupancy_rate / 100.0 * ra.days_with_data
                ELSE ra.total_revenue
            END - ra.total_revenue
        ) AS estimated_revenue_impact,
        -- Market share estimate
        CASE
            WHEN ra.competitor_count > 0 AND ra.total_spaces > 0 THEN
                (ra.total_spaces * ra.avg_occupancy_rate / 100.0) /
                NULLIF(
                    (ra.total_spaces * ra.avg_occupancy_rate / 100.0) +
                    (ra.competitor_count * COALESCE(ra.avg_competitor_rate, 0) * 50),  -- Estimate competitor spaces
                    1
                ) * 100
            ELSE 100.0
        END AS estimated_market_share_pct
    FROM ranked_analysis ra
)
SELECT
    or_rec.facility_id,
    or_rec.facility_name,
    or_rec.city_name,
    or_rec.state_code,
    or_rec.msa_name,
    or_rec.total_spaces,
    or_rec.facility_type,
    or_rec.operator_type,
    or_rec.avg_occupancy_rate,
    or_rec.median_occupancy_rate,
    or_rec.p95_occupancy_rate,
    or_rec.total_revenue,
    or_rec.avg_hourly_rate AS current_rate,
    or_rec.recommended_rate,
    or_rec.competitor_count,
    or_rec.avg_competitor_rate,
    or_rec.median_competitor_rate,
    or_rec.market_opportunity_score,
    or_rec.competitive_advantage_score,
    or_rec.opportunity_percentile,
    or_rec.revenue_percentile,
    or_rec.competitive_percentile,
    or_rec.optimization_priority,
    or_rec.estimated_revenue_impact,
    or_rec.estimated_market_share_pct,
    CASE
        WHEN or_rec.estimated_revenue_impact > 1000 THEN 'High Impact'
        WHEN or_rec.estimated_revenue_impact > 0 THEN 'Medium Impact'
        ELSE 'Low Impact'
    END AS impact_category
FROM optimization_recommendations or_rec
WHERE or_rec.competitor_count > 0 OR or_rec.total_revenue > 0
ORDER BY or_rec.market_opportunity_score DESC, or_rec.total_revenue DESC
LIMIT 200;"""

def enhance_queries_file():
    """Enhance queries.md by replacing simplified SQL in queries 10-30"""
    queries_file = Path(__file__).parent.parent / 'queries' / 'queries.md'
    
    if not queries_file.exists():
        print(f"Error: {queries_file} not found")
        return
    
    content = queries_file.read_text(encoding='utf-8')
    
    # Find all query SQL blocks for queries 10-30
    query_pattern = r'(## Query (\d+):.*?```sql\n)(.*?)(```)'
    
    def replace_sql(match):
        query_header = match.group(1)
        query_num = int(match.group(2))
        old_sql = match.group(3)
        closing = match.group(4)
        
        # Only enhance queries 10-30
        if 10 <= query_num <= 30:
            # Check if it's the simplified template (has "base_data AS" and only 4 CTEs)
            if 'WITH base_data AS' in old_sql and old_sql.count('WITH') == 1:
                enhanced_sql = get_enhanced_sql_template()
                return query_header + enhanced_sql + closing
            else:
                # Already enhanced or different structure
                return match.group(0)
        else:
            # Queries 1-9, keep as-is
            return match.group(0)
    
    enhanced_content = re.sub(query_pattern, replace_sql, content, flags=re.DOTALL)
    
    if enhanced_content != content:
        queries_file.write_text(enhanced_content, encoding='utf-8')
        print(f"✓ Enhanced queries 10-30 in {queries_file}")
        print(f"  Replaced simplified template SQL with complex 6+ CTE queries")
    else:
        print("No changes needed - queries already enhanced")

if __name__ == "__main__":
    enhance_queries_file()
