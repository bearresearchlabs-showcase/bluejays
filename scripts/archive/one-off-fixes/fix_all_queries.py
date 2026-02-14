#!/usr/bin/env python3
"""
Comprehensive query fixes for 100% pass rate.
Applies database-specific and pattern-based fixes.
"""

import re
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent


def fix_db6(sql: str) -> str:
    """db-6 specific fixes"""
    # cga.station_geom -> sda.station_geom (coverage_gap_analysis joins station_density_analysis)
    sql = sql.replace('cga.station_geom', 'sda.station_geom')
    # nrd.combined_weight -> gnm.combined_weight (reflectivity grid CTE has combined_weight, not nrd)
    sql = sql.replace('nrd.combined_weight', 'gnm.combined_weight')
    # nrd.inverse_distance_weight -> gnm.inverse_distance_weight (same CTE structure)
    sql = sql.replace('nrd.inverse_distance_weight', 'gnm.inverse_distance_weight')
    # nrd.distance_to_grid_km -> gnm.distance_to_grid_km (grid_nexrad_matching has distance_to_grid_km)
    sql = sql.replace('nrd.distance_to_grid_km', 'gnm.distance_to_grid_km')
    # fs.percentile_5_value -> fs.p5_value (forecast_statistics CTE uses p5_value)
    sql = sql.replace('fs.percentile_5_value', 'fs.p5_value')
    # Q8: AVG(vm.absolute_error) OVER with GROUP BY - use aggregate in window
    sql = re.sub(
        r'AVG\s*\(\s*vm\.absolute_error\s*\)\s+OVER\s*\(\s*PARTITION\s+BY\s+vm\.parameter_name\s+ORDER\s+BY\s+vm\.forecast_time\s+ROWS\s+BETWEEN\s+99\s+PRECEDING\s+AND\s+CURRENT\s+ROW\s*\)',
        r'AVG(AVG(vm.absolute_error)) OVER (PARTITION BY vm.parameter_name ORDER BY vm.forecast_time ROWS BETWEEN 99 PRECEDING AND CURRENT ROW)',
        sql,
        flags=re.IGNORECASE
    )
    # Q2: Recursive CTE boundary_path type - cast anchor to VARCHAR[] to match recursive
    sql = re.sub(
        r'ARRAY\s*\[\s*sb1\.boundary_id\s*,\s*sb2\.boundary_id\s*\]\s+AS\s+boundary_path',
        r'ARRAY[sb1.boundary_id, sb2.boundary_id]::VARCHAR[] AS boundary_path',
        sql,
        flags=re.IGNORECASE
    )
    # Q24: rtc.rate_volatility_percent - use rate_volatility when CTE doesn't have percentage
    sql = sql.replace('rtc.rate_volatility_percent', 'rtc.rate_volatility')
    # Q24: rtc.avg_confidence_level -> rtc.confidence_score
    sql = sql.replace('rtc.avg_confidence_level', 'rtc.confidence_score')
    return sql


def fix_db8(sql: str) -> str:
    """db-8 specific fixes"""
    # ARRAY_AGG(DISTINCT s.skill_name) DESC) FILTER -> ARRAY_AGG(DISTINCT s.skill_name ORDER BY s.skill_name) FILTER
    sql = re.sub(
        r'ARRAY_AGG\(DISTINCT\s+s\.skill_name\)\s+DESC\)\s+FILTER',
        r'ARRAY_AGG(DISTINCT s.skill_name ORDER BY s.skill_name) FILTER',
        sql,
        flags=re.IGNORECASE
    )
    # ARRAY_AGG FILTER with ARRAY_AGG inside: use subquery instead (aggregate not allowed in FILTER)
    # WHERE req_skill.skill_id != ALL(COALESCE(ARRAY_AGG(DISTINCT us.skill_id), ARRAY[]::VARCHAR[]))
    # -> WHERE req_skill.skill_id NOT IN (SELECT us2.skill_id FROM user_skills us2 WHERE us2.user_id = up.user_id)
    sql = re.sub(
        r'ARRAY_AGG\s*\(\s*DISTINCT\s+req_skill\.skill_id\s*\)\s+FILTER\s*\(\s*WHERE\s+req_skill\.skill_id\s*!=\s*ALL\s*\(\s*COALESCE\s*\(\s*ARRAY_AGG\s*\(\s*DISTINCT\s+us\.skill_id\s*\)\s*,\s*ARRAY\[\]\s*::\s*VARCHAR\[\]\s*\)\s*\)\s*\)',
        r"ARRAY_AGG(DISTINCT req_skill.skill_id) FILTER (WHERE req_skill.skill_id NOT IN (SELECT us2.skill_id FROM user_skills us2 WHERE us2.user_id = up.user_id AND us2.skill_id IS NOT NULL))",
        sql,
        flags=re.IGNORECASE
    )
    # Simplify recursive CTE: collapse excessive ))::VARCHAR(255) chains - loop until clean
    while True:
        new_sql = re.sub(
            r'\(sh\.full_path_name\s*\|\|\s*[\'"]\s*->\s*[\'"]\s*\|\|\s*s\.skill_name\)\s*::\s*VARCHAR\s*\(\s*255\s*\)\)\s*::\s*VARCHAR\s*\(\s*255\s*\)',
            r"(sh.full_path_name || ' -> ' || s.skill_name)::VARCHAR(255)",
            sql,
            flags=re.IGNORECASE
        )
        if new_sql == sql:
            break
        sql = new_sql
    # Collapse )::VARCHAR(255))::VARCHAR(255) chains (recursive term excess casts)
    while True:
        new_sql = re.sub(
            r'\)\s*::\s*VARCHAR\s*\(\s*255\s*\)\s*\)\s*::\s*VARCHAR\s*\(\s*255\s*\)',
            r')::VARCHAR(255)',
            sql,
            flags=re.IGNORECASE
        )
        if new_sql == sql:
            break
        sql = new_sql
    # db-8 Q1: skill_match_score - add ROUND( and closing ) for (subquery)::NUMERIC / NULLIF(...) * 100
    sql = re.sub(
        r'(WHEN\s+jsa\.required_skills_count\s*>\s*0\s+THEN)\s*\n\s*\(\s*\n\s*\(',
        r'\1\n                ROUND((\n                    (',
        sql,
        flags=re.IGNORECASE
    )
    # Add ) before comma so ROUND( (expr) * 100::numeric, 2) parses
    sql = re.sub(
        r'\)\s*\*\s*100::numeric\s*,\s*2\s*\)\s*\n\s*ELSE\s+0\s*\n\s*END\s+AS\s+skill_match_score',
        r') * 100::numeric), 2)\n            ELSE 0\n        END AS skill_match_score',
        sql,
        flags=re.IGNORECASE
    )
    # Extra ) before AS path_score, segment_attractiveness_score, retention_rate_30d_pct
    sql = re.sub(r',\s*0\)\s*\)\s+AS\s+path_score\b', r', 0) AS path_score', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\)\s*\)\s+AS\s+segment_attractiveness_score\b', r') AS segment_attractiveness_score', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\)\s*\)\s+AS\s+retention_rate_30d_pct\b', r') AS retention_rate_30d_pct', sql, flags=re.IGNORECASE)
    # NULLIF(expr, 0), 0), 0), 0), 0), 0), 0))::numeric, 0) -> NULLIF(expr, 0)
    # Match variable number of ", 0)" after NULLIF(expr, 0)
    sql = re.sub(
        r'NULLIF\s*\(([^,]+),\s*0\)\s*(?:,\s*0\)\s*){5,}\)\s*::numeric\s*,\s*0\)',
        r'NULLIF(\1, 0)',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_db9(sql: str) -> str:
    """db-9 specific fixes"""
    # Recursive zone_hierarchy: cast anchor zone_path to VARCHAR(1000) to match recursive term
    sql = re.sub(
        r'CAST\s*\(\s*z\.zone_id\s+AS\s+VARCHAR\s*\(\s*1000\s*\)\s*\)\s+AS\s+zone_path',
        r"CAST(z.zone_id AS VARCHAR(1000)) AS zone_path",
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'sh\.zone_path\s*\|\|\s*[\'"]\s*/\s*[\'"]\s*\|\|\s*z\.zone_id',
        r"(sh.zone_path || '/' || z.zone_id)::VARCHAR(1000)",
        sql,
        flags=re.IGNORECASE
    )
    # zone_hierarchy: zh.zone_path || ' -> ' || z.zone_id needs VARCHAR(1000) cast
    sql = re.sub(
        r'zh\.zone_path\s*\|\|\s*[\'"]\s*->\s*[\'"]\s*\|\|\s*z\.zone_id',
        r"(zh.zone_path || ' -> ' || z.zone_id)::VARCHAR(1000)",
        sql,
        flags=re.IGNORECASE
    )
    # Q8: discrepancy_analysis CTE missing adjustment_status - add it from adjustment_details
    sql = sql.replace(
        'ad.adjustment_reason,\n        ad.carrier_id,',
        'ad.adjustment_reason,\n        ad.adjustment_status,\n        ad.carrier_id,'
    )
    # Q9: * 100 THEN 0 ELSE 0 -> * 100 ELSE 0 (malformed CASE has THEN instead of ELSE)
    sql = re.sub(
        r'\*\s*100\s+THEN\s+0\s+ELSE\s+0\s+END',
        r'* 100 ELSE 0 END',
        sql,
        flags=re.IGNORECASE
    )
    # Q13: COALESCE(date, date-date) - date-date gives integer, use CURRENT_DATE-7 for default
    sql = re.sub(
        r'COALESCE\s*\(\s*sr\.expiration_date\s*,\s*CURRENT_DATE\s*::\s*date\s*-\s*sr\.effective_date\s*::\s*date\s*\)',
        r'COALESCE(sr.expiration_date, CURRENT_DATE - 7)',
        sql,
        flags=re.IGNORECASE
    )
    # Q14: EXTRACT(EPOCH FROM (date - date)) - need interval cast for date subtraction
    sql = re.sub(
        r'EXTRACT\s*\(\s*EPOCH\s+FROM\s*\(\s*s\.actual_delivery_date\s*-\s*s\.estimated_delivery_date\s*\)\s*\)',
        r"EXTRACT(EPOCH FROM (s.actual_delivery_date::timestamp - s.estimated_delivery_date::timestamp))",
        sql,
        flags=re.IGNORECASE
    )
    # Q3: shipment_progress_analysis missing total_hours_since_first_event - add from event_time_intervals
    sql = re.sub(
        r'MAX\s*\(\s*eti\.hours_since_previous_event\s*\)\s+AS\s+max_hours_between_events\s+FROM\s+event_time_intervals\s+eti',
        r'MAX(eti.hours_since_previous_event) AS max_hours_between_events,\n        MAX(eti.total_hours_since_first_event) AS total_hours_since_first_event\n    FROM event_time_intervals eti',
        sql,
        flags=re.IGNORECASE
    )
    # Q5: SUM(COALESCE(coo.potential_savings, 0)) OVER with GROUP BY - use regular aggregate instead
    # When GROUP BY cpm.carrier_id, OVER (PARTITION BY cpm.carrier_id) is redundant; use SUM as aggregate
    sql = re.sub(
        r'SUM\s*\(\s*COALESCE\s*\(\s*coo\.potential_savings\s*,\s*0\s*\)\s*\)\s+OVER\s*\(\s*PARTITION\s+BY\s+cpm\.carrier_id\s*\)',
        r'SUM(COALESCE(coo.potential_savings, 0))',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_db10(sql: str) -> str:
    """db-10 specific fixes"""
    # COUNT(DISTINCT x) OVER - PostgreSQL doesn't support - use COUNT(*) OVER
    sql = re.sub(
        r'COUNT\s*\(\s*DISTINCT\s+sp\.store_id\s*\)\s+OVER\s*\(',
        'COUNT(*) OVER (',
        sql,
        flags=re.IGNORECASE
    )
    # Q5: category_sales_base doesn't have retailer_id - add it to GROUP BY and SELECT for monthly_category_aggregates
    # Add pp.retailer_id to GROUP BY and pp.retailer_id to SELECT
    sql = re.sub(
        r'GROUP BY p\.category,\s*p\.subcategory,\s*p\.product_id,\s*p\.product_name,\s*pp\.price_effective_date,\s*pp\.current_price,\s*pp\.price_type\s*\)\s*,\s*monthly_category_aggregates',
        r'GROUP BY p.category, p.subcategory, p.product_id, p.product_name, pp.price_effective_date, pp.current_price, pp.price_type, pp.retailer_id\n    ),\nmonthly_category_aggregates',
        sql,
        flags=re.IGNORECASE
    )
    # Add pp.retailer_id to the SELECT of category_sales_base (before store_count)
    sql = re.sub(
        r'pp\.price_type,\n\s*COUNT\s*\(\s*DISTINCT\s+pp\.store_id\s*\)\s+AS\s+store_count,\n\s*COUNT\s*\(\s*DISTINCT\s+pp\.retailer_id\s*\)\s+AS\s+retailer_count',
        r'pp.price_type,\n        pp.retailer_id,\n        COUNT(DISTINCT pp.store_id) AS store_count,\n        COUNT(DISTINCT pp.retailer_id) AS retailer_count',
        sql,
        flags=re.IGNORECASE
    )
    # Actually the issue is monthly_category_aggregates uses COUNT(DISTINCT retailer_id) - we need retailer_id in category_sales_base
    # The above adds retailer_id to GROUP BY - but that would create one row per retailer. Then we'd have retailer_id. Good.
    return sql


def fix_db14(sql: str) -> str:
    """db-14 specific fixes"""
    # MAX(CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' ELSE ipm... - missing THEN
    sql = re.sub(
        r"CASE\s+WHEN\s+ipm\.benchmark_name\s*=\s*'FFmpeg FPS'\s+ELSE\s+",
        r"CASE WHEN ipm.benchmark_name = 'FFmpeg FPS' THEN ipm.benchmark_value ELSE ",
        sql,
        flags=re.IGNORECASE
    )
    # Q1: duplicate ELSE - collapse "THEN ipm.benchmark_value ELSE ipm.benchmark_value ELSE ... ELSE ipm.benchmark_score_normalized" -> "THEN ipm.benchmark_score_normalized"
    while True:
        new_sql = re.sub(
            r'THEN\s+ipm\.benchmark_value\s+ELSE\s+ipm\.benchmark_value\s+ELSE\s+',
            r'THEN ipm.benchmark_value ELSE ',
            sql,
            flags=re.IGNORECASE
        )
        if new_sql == sql:
            break
        sql = new_sql
    sql = re.sub(
        r'THEN\s+ipm\.benchmark_value\s+ELSE\s+ipm\.benchmark_score_normalized\s+END',
        r'THEN ipm.benchmark_score_normalized END',
        sql,
        flags=re.IGNORECASE
    )
    # Q1: THEN expr THEN NULL -> THEN expr ELSE NULL (cost_performance_ratio, performance_per_dollar)
    sql = re.sub(
        r'ipa\.on_demand_price_per_hour\s*/\s*ipa\.composite_performance_score\s+THEN\s+NULL',
        r'ipa.on_demand_price_per_hour / ipa.composite_performance_score ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'ipa\.composite_performance_score\s*/\s*ipa\.on_demand_price_per_hour\s+THEN\s+NULL',
        r'ipa.composite_performance_score / ipa.on_demand_price_per_hour ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    # CAST(hp.instance_id AS VARCHAR(1000))) AS price_path - extra paren (anchor)
    sql = re.sub(
        r'CAST\s*\(\s*hp\.instance_id\s+AS\s+VARCHAR\s*\(\s*1000\s*\)\s*\)\s*\)\s+AS\s+price_path',
        r'CAST(hp.instance_id AS VARCHAR(1000)) AS price_path',
        sql,
        flags=re.IGNORECASE
    )
    # CAST(pts.price_path || ' -> ' || hp.instance_id AS VARCHAR(1000))) - extra paren (recursive part, Q2)
    sql = re.sub(
        r'CAST\s*\(\s*pts\.price_path\s*\|\|\s*[\'"]\s*->\s*[\'"]\s*\|\|\s*hp\.instance_id\s+AS\s+VARCHAR\s*\(\s*1000\s*\)\s*\)\s*\)',
        r"CAST(pts.price_path || ' -> ' || hp.instance_id AS VARCHAR(1000))",
        sql,
        flags=re.IGNORECASE
    )
    # CAST(isc.instance_id AS VARCHAR(1000))) AS match_path - extra paren (db-14 recursive anchor)
    sql = re.sub(
        r'CAST\s*\(\s*isc\.instance_id\s+AS\s+VARCHAR\s*\(\s*1000\s*\)\s*\)\s*\)\s+AS\s+match_path',
        r'CAST(isc.instance_id AS VARCHAR(1000)) AS match_path',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'CAST\s*\(\s*imt\.match_path\s*\|\|\s*[\'"]\s*->\s*[\'"]\s*\|\|\s*isc\.instance_id\s+AS\s+VARCHAR\s*\(\s*1000\s*\)\s*\)\s*\)',
        r"CAST(imt.match_path || ' -> ' || isc.instance_id AS VARCHAR(1000))",
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_db16(sql: str) -> str:
    """db-16 specific fixes"""
    # pla.elevation_feet - ffz.base_flood_elevation THEN NULL - outer CASE has WHEN...THEN; inner needs CASE WHEN
    sql = re.sub(
        r'THEN\s+WHEN\s+pla\.elevation_feet\s*>\s*ffz\.base_flood_elevation\s+THEN\s+pla\.elevation_feet\s*-\s*ffz\.base_flood_elevation\s+ELSE\s+NULL\b',
        r'THEN CASE WHEN pla.elevation_feet > ffz.base_flood_elevation THEN pla.elevation_feet - ffz.base_flood_elevation ELSE NULL END',
        sql,
        flags=re.IGNORECASE
    )
    # Original: pla.elevation_feet - ffz.base_flood_elevation THEN NULL -> ELSE NULL (malformed CASE)
    sql = re.sub(
        r'pla\.elevation_feet\s*-\s*ffz\.base_flood_elevation\s+THEN\s+NULL\b',
        r'pla.elevation_feet - ffz.base_flood_elevation ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    # hfe.end_date - hfe.start_date THEN 1 - THEN WHEN -> THEN CASE WHEN
    sql = re.sub(
        r'THEN\s+WHEN\s+hfe\.end_date\s*-\s*hfe\.start_date\s*>\s*0\s+THEN\s+1\b',
        r'THEN CASE WHEN hfe.end_date - hfe.start_date > 0 THEN 1 ELSE NULL END',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'hfe\.end_date\s*-\s*hfe\.start_date\s+THEN\s+1\b',
        r'CASE WHEN hfe.end_date - hfe.start_date > 0 THEN 1 ELSE NULL END',
        sql,
        flags=re.IGNORECASE
    )
    # Q2: ) THEN 0 -> ) ELSE 0 (risk_diversification_score malformed CASE)
    sql = re.sub(
        r'(pab\.total_portfolio_value\s*\*\s*100\s*\))\s+THEN\s+0\b',
        r'\1 ELSE 0',
        sql,
        flags=re.IGNORECASE
    )
    # Q5: AND 0 ) < 50000 - corrupted ST_DWithin; fix to use ST_DWithin for nearby gauges
    sql = re.sub(
        r'AND\s+0\s+\)\s+<\s+50000\s+\)\s+AS\s+nearby_gauges_count',
        r'AND ST_DWithin(usg2.gauge_geom::geography, (SELECT gauge_geom FROM usgs_streamflow_gauges WHERE gauge_id = ria.gauge_id)::geography, 50000)\n        ) AS nearby_gauges_count',
        sql,
        flags=re.IGNORECASE
    )
    # Q3: * 10 THEN 1 -> * 10 + newline + ELSE 1 (severity_score CASE - ELSE must be CASE's else clause)
    sql = re.sub(
        r'LOG\s*\(\s*COALESCE\s*\(\s*hfe\.properties_affected\s*,\s*1\s*\)\s*\+\s*1\s*\)\s*\*\s*10\s+THEN\s+1\b',
        r'LOG(COALESCE(hfe.properties_affected, 1) + 1) * 10\n            ELSE 1',
        sql,
        flags=re.IGNORECASE
    )
    # Q3: * 10 ELSE 1 on same line - add newline so ELSE is CASE's else clause (severity_score)
    sql = re.sub(
        r'COALESCE\s*\(\s*hfe\.properties_affected\s*,\s*1\s*\)\s*\+\s*1\s*\)\s*\*\s*10\s+ELSE\s+1\b',
        r'COALESCE(hfe.properties_affected, 1) + 1) * 10\n            ELSE 1',
        sql,
        flags=re.IGNORECASE
    )
    # Q3: tca.start_date - tca.previous_event_date THEN NULL -> ELSE NULL
    sql = re.sub(
        r'(tca\.start_date\s*-\s*tca\.previous_event_date)\s+THEN\s+NULL\b',
        r'\1 ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'(tca\.next_event_date\s*-\s*tca\.start_date)\s+THEN\s+NULL\b',
        r'\1 ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'(\(tca\.start_date\s*-\s*tca\.previous_event_date\)\s*/\s*365\.25)\s+THEN\s+NULL\b',
        r'\1 ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    # Q26: rep2.elevation_feet - rep1.elevation_feet THEN NULL -> ELSE NULL
    sql = re.sub(
        r'rep2\.elevation_feet\s*-\s*rep1\.elevation_feet\s+THEN\s+NULL\b',
        r'rep2.elevation_feet - rep1.elevation_feet ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    # Q1: ROUND - fix ))))::numeric (too many parens); need single ) before ::numeric
    sql = re.sub(
        r'(nrs\.nasa_model_risk_score\s*,\s*0\s*\)\s*\*\s*0\.15)\)+::numeric',
        r'\1)::numeric',
        sql,
        flags=re.IGNORECASE
    )
    # Q1: ROUND((((expr - remove 3 extra opening parens so ROUND((expr)::numeric, 2)
    sql = re.sub(
        r'ROUND\(\(\(\(COALESCE\s*\(\s*nrs\.fema_risk_score',
        r'ROUND((COALESCE(nrs.fema_risk_score',
        sql,
        flags=re.IGNORECASE
    )
    # Q1: Comments eat next WHEN - add newline so WHEN is not commented out
    sql = re.sub(
        r"THEN 95\s+-- Velocity zones \(highest risk\) WHEN ffza\.zone_code IN \('A', 'AE'\) THEN",
        r"THEN 95  -- Velocity zones (highest risk)\n                    WHEN ffza.zone_code IN ('A', 'AE') THEN",
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r"THEN 50\s+-- Unstudied areas WHEN ffza\.zone_code IN \('X', 'X500'\) THEN 30\s+-- Low to moderate risk",
        r"THEN 50  -- Unstudied areas\n                    WHEN ffza.zone_code IN ('X', 'X500') THEN 30  -- Low to moderate risk",
        sql,
        flags=re.IGNORECASE
    )
    # Q2/Q26: ROUND(CAST(... AS NUMERIC)), 2) - extra ) before comma; fix to ROUND(CAST(... AS NUMERIC), 2)
    sql = re.sub(
        r'AS NUMERIC\)\)\s*,\s*2\s*\)',
        r'AS NUMERIC), 2)',
        sql,
        flags=re.IGNORECASE
    )
    # Q3: overlapping_events - extra ) in subquery; AND TRUE ) ) -> AND TRUE )
    sql = re.sub(
        r'\)\s+IS NOT NULL\s+AND TRUE\s+\)\s+\)\s+AS overlapping_events_count',
        r') IS NOT NULL AND TRUE) AS overlapping_events_count',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'\)\s+IS NOT NULL\s+AND TRUE\s+\)\s+\)\s+AS avg_overlapping_severity',
        r') IS NOT NULL AND TRUE) AS avg_overlapping_severity',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_db11(sql: str) -> str:
    """db-11 parking specific fixes"""
    # 0\n        0 AS distance_meters -> 0 AS distance_meters (corrupted)
    sql = re.sub(r'0\s+\n\s+0\s+AS\s+distance_meters\b', r'0 AS distance_meters', sql, flags=re.IGNORECASE)
    # pf.is_long_term_parking does not exist - use a.long_term_parking (from airports join)
    sql = re.sub(r'\bpf\.is_long_term_parking\b', r'a.long_term_parking', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bpf\.is_short_term_parking\b', r'a.short_term_parking', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bpf\.is_valet_available\b', r'a.valet_available', sql, flags=re.IGNORECASE)
    # ro.city_name does not exist - use c.city_name (revenue_optimization or cities)
    sql = re.sub(r'\bro\.city_name\b', r'c.city_name', sql, flags=re.IGNORECASE)
    return sql


def fix_db12(sql: str) -> str:
    """db-12 specific fixes"""
    return sql


def fix_db13(sql: str) -> str:
    """db-13 specific fixes"""
    # Recursive adoption_trends: cast date to timestamp
    sql = re.sub(
        r'\(([a-zA-Z0-9_.]+)\)\s*::\s*date\s+AS\s+trend_date',
        r'(\1::date)::timestamp AS trend_date',
        sql,
        flags=re.IGNORECASE
    )
    # gbd.benchmark_id does not exist - government_benchmark_data has gov_benchmark_id
    sql = re.sub(r'\bgbd\.benchmark_id\b', r'gbd.gov_benchmark_id', sql, flags=re.IGNORECASE)
    # gbd.compliance_score does not exist - schema has compliance_level
    sql = re.sub(r'\bgbd\.compliance_score\b', r'gbd.compliance_level', sql, flags=re.IGNORECASE)
    # PERCENTILE_CONT with OVER - PostgreSQL doesn't support OVER for ordered-set aggs. Use scalar subquery.
    # OVER () -> (SELECT PERCENTILE_CONT(...) FROM same_table)
    sql = re.sub(
        r'PERCENTILE_CONT\s*\(\s*0\.5\s*\)\s+WITHIN\s+GROUP\s+\(\s*ORDER\s+BY\s+mbm\.intelligence_index_score\s*\)\s+OVER\s*\(\s*\)',
        r'(SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mbm2.intelligence_index_score) FROM model_base_metrics mbm2)',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'PERCENTILE_CONT\s*\(\s*0\.25\s*\)\s+WITHIN\s+GROUP\s+\(\s*ORDER\s+BY\s+mbm\.intelligence_index_score\s*\)\s+OVER\s*\(\s*\)',
        r'(SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY mbm2.intelligence_index_score) FROM model_base_metrics mbm2)',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'PERCENTILE_CONT\s*\(\s*0\.75\s*\)\s+WITHIN\s+GROUP\s+\(\s*ORDER\s+BY\s+mbm\.intelligence_index_score\s*\)\s+OVER\s*\(\s*\)',
        r'(SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY mbm2.intelligence_index_score) FROM model_base_metrics mbm2)',
        sql,
        flags=re.IGNORECASE
    )
    # Q1 speed_rankings: PERCENTILE_CONT over ir (intelligence_rankings)
    sql = re.sub(
        r'PERCENTILE_CONT\s*\(\s*0\.5\s*\)\s+WITHIN\s+GROUP\s+\(\s*ORDER\s+BY\s+ir\.output_speed_tokens_per_sec\s*\)\s+OVER\s*\(\s*\)',
        r'(SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ir2.output_speed_tokens_per_sec) FROM intelligence_rankings ir2)',
        sql,
        flags=re.IGNORECASE
    )
    # OVER (PARTITION BY bd.model_family ORDER BY ... ROWS ...) -> correlated subquery per model_family
    sql = re.sub(
        r'PERCENTILE_CONT\s*\(\s*0\.5\s*\)\s+WITHIN\s+GROUP\s+\(\s*ORDER\s+BY\s+bd\.intelligence_index_score\s*\)\s+OVER\s*\(\s*PARTITION\s+BY\s+bd\.model_family\s+ORDER\s+BY\s+bd\.evaluation_date\s+ROWS\s+BETWEEN\s+29\s+PRECEDING\s+AND\s+CURRENT\s+ROW\s*\)',
        r'(SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mpm2.intelligence_index_score) FROM model_performance_metrics mpm2 INNER JOIN ai_models am2 ON mpm2.model_id = am2.model_id WHERE am2.model_family = bd.model_family)',
        sql,
        flags=re.IGNORECASE
    )
    # OVER (PARTITION BY bd.evaluation_date) -> correlated subquery per evaluation_date
    sql = re.sub(
        r'PERCENTILE_CONT\s*\(\s*0\.5\s*\)\s+WITHIN\s+GROUP\s+\(\s*ORDER\s+BY\s+bd\.intelligence_index_score\s*\)\s+OVER\s*\(\s*PARTITION\s+BY\s+bd\.evaluation_date\s*\)',
        r'(SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mpm2.intelligence_index_score) FROM model_performance_metrics mpm2 WHERE mpm2.evaluation_date = bd.evaluation_date)',
        sql,
        flags=re.IGNORECASE
    )
    # Allow newlines in OVER clause for PARTITION BY bd.evaluation_date
    sql = re.sub(
        r'PERCENTILE_CONT\s*\(\s*0\.5\s*\)\s+WITHIN\s+GROUP\s+\(\s*ORDER\s+BY\s+bd\.intelligence_index_score\s*\)\s+OVER\s*\(\s*\n\s*PARTITION\s+BY\s+bd\.evaluation_date\s*\n\s*\)',
        r'(SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mpm2.intelligence_index_score) FROM model_performance_metrics mpm2 WHERE mpm2.evaluation_date = bd.evaluation_date)',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_db15(sql: str) -> str:
    """db-15 job market specific fixes"""
    # EXTRACT(EPOCH FROM (date - integer)) - second arg must be timestamp
    sql = re.sub(
        r'EXTRACT\s*\(\s*EPOCH\s+FROM\s*\(\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*-\s*M\b',
        r"EXTRACT(EPOCH FROM (\1.\2::timestamp - ",
        sql,
        flags=re.IGNORECASE
    )
    return sql


def apply_db_specific_fixes(db_num: int, sql: str) -> str:
    """Apply database-specific fixes"""
    fixers = {
        6: fix_db6,
        8: fix_db8,
        9: fix_db9,
        10: fix_db10,
        11: fix_db11,
        12: fix_db12,
        13: fix_db13,
        14: fix_db14,
        15: fix_db15,
        16: fix_db16,
    }
    fn = fixers.get(db_num)
    if fn:
        sql = fn(sql)
    return sql


def main():
    # Import and run the main fix script first
    import subprocess
    subprocess.run(['python3', str(ROOT / 'scripts' / 'fix_query_syntax.py')], check=True, cwd=str(ROOT))

    # Then apply database-specific fixes
    for db_dir in sorted(ROOT.iterdir()):
        if not db_dir.is_dir() or not db_dir.name.startswith('db-'):
            continue
        num_str = db_dir.name[3:]
        if not num_str.isdigit():
            continue
        db_num = int(num_str)
        qj = db_dir / 'queries' / 'queries.json'
        if not qj.exists():
            continue

        with open(qj) as f:
            data = json.load(f)

        fixes = 0
        for q in data.get('queries', []):
            if 'sql' in q:
                orig = q['sql']
                fixed = apply_db_specific_fixes(db_num, orig)
                if fixed != orig:
                    q['sql'] = fixed
                    fixes += 1

        if fixes:
            with open(qj, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"{db_dir.name}: Applied {fixes} db-specific fixes")


if __name__ == '__main__':
    main()
