#!/usr/bin/env python3
"""Apply db-15 specific PostgreSQL fixes to queries.json"""
import json
import re
from pathlib import Path

BASE = Path(__file__).parent.parent
QPATH = BASE / "source" / "db-15" / "app" / "QUERIES" / "queries.json"


def fix_query(sql: str, num: int) -> str:
    s = sql

    # Q2: Recursive CTE type - 0 AS cumulative_kwh_usage -> 0::NUMERIC
    if num == 2:
        s = s.replace("0 AS cumulative_kwh_usage,", "0::NUMERIC AS cumulative_kwh_usage,")

    # Q4: EXTRACT(EPOCH FROM (date - date)) - date subtraction gives integer
    if num == 4:
        s = re.sub(
            r"EXTRACT\s*\(\s*EPOCH\s+FROM\s*\(\s*her\.effective_date\s*-\s*MIN\s*\(\s*her\.effective_date\s*\)\s+OVER\s*\([^)]+\)\s*\)\s*\)\s*/\s*2592000",
            r"((her.effective_date - MIN(her.effective_date) OVER (PARTITION BY her.utility_id, her.rate_code_id))::numeric * 86400 / 2592000)",
            s,
            flags=re.IGNORECASE,
        )

    # Q5: mi.region does not exist - market_intelligence uses urp.* but urp lacks region; use s.region in final_comparison_matrix
    if num == 5:
        s = s.replace("mi.region,", "s.region,")

    # Q7: COUNT(DISTINCT) in window function not supported in PostgreSQL; replace with scalar subqueries
    if num == 7:
        s = s.replace(
            "COUNT(DISTINCT msc.rate_code_id) OVER (PARTITION BY msc.region) AS region_total_rate_codes,\n        COUNT(DISTINCT msc.state_id) OVER (PARTITION BY msc.region) AS region_state_count",
            "(SELECT COUNT(DISTINCT msc2.rate_code_id) FROM market_share_calculations msc2 WHERE msc2.region = msc.region) AS region_total_rate_codes,\n        (SELECT COUNT(DISTINCT msc2.state_id) FROM market_share_calculations msc2 WHERE msc2.region = msc.region) AS region_state_count",
        )

    # Q8: CASE WHEN year_num <= 10 THEN ... THEN 0 ELSE 0 (malformed CASE)
    if num == 8:
        s = re.sub(
            r"CASE WHEN yrs\.year_num <= 10 THEN rc\.annual_savings / POWER\(1\.03, yrs\.year_num\) THEN 0 ELSE 0 END",
            "CASE WHEN yrs.year_num <= 10 THEN rc.annual_savings / POWER(1.03, yrs.year_num) ELSE 0 END",
            s,
        )
        s = re.sub(
            r"CASE WHEN year_num <= 10 THEN rc\.annual_savings / POWER\(1\.03, year_num\) THEN 0 ELSE 0 END",
            "CASE WHEN yrs.year_num <= 10 THEN rc.annual_savings / POWER(1.03, yrs.year_num) ELSE 0 END",
            s,
        )
        s = s.replace(
            "CROSS JOIN GENERATE_SERIES(1, 25) AS year_num",
            "CROSS JOIN (SELECT generate_series(1, 25) AS year_num) yrs",
        )
        s = s.replace("ORDER BY year_num\n            ROWS", "ORDER BY yrs.year_num\n            ROWS")
        s = s.replace("POWER(1.03, year_num)", "POWER(1.03, yrs.year_num)")
        s = s.replace("CASE WHEN year_num <= 10", "CASE WHEN yrs.year_num <= 10")
        # Add year_num to SELECT for WHERE npva.year_num = 1
        s = s.replace(
            "END AS roi_25yr_percentage\n    FROM roi_calculations rc",
            "END AS roi_25yr_percentage,\n        yrs.year_num AS year_num\n    FROM roi_calculations rc",
        )
        s = s.replace("CASE WHEN year_num <= 10", "CASE WHEN yrs.year_num <= 10")
        s = s.replace("npva.year_num = 1", "npva.year_num = 1")  # no change - year_num is now a column

    # Q9: state_rate_summary does not exist - CTE is state_rate_statistics; fix subquery reference
    if num == 9:
        s = s.replace(
            "FROM state_rate_summary srs2 WHERE srs2.state_id = srs.state_id",
            "FROM state_rate_statistics srs2 WHERE srs2.region = srs.region",
        )

    # Q10: tier_count and tou_period_count ambiguous - complexity_metrics has rsd.* (includes both)
    # and toua.tou_period_count. Use explicit rsd columns excluding tou_period_count.
    if num == 10:
        s = s.replace(
            "rsd.*,\n        tca.distinct_tier_levels,",
            "rsd.rate_structure_id, rsd.utility_id, rsd.rate_code_id, rsd.rate_name, rsd.code_structure_type,\n        rsd.effective_date, rsd.energy_charge_usd_per_kwh, rsd.fixed_charge_usd, rsd.demand_charge_usd_per_kw, rsd.tier_count,\n        tca.distinct_tier_levels,",
        )
        s = s.replace(
            "(COALESCE(rsd.tou_period_count, 0) * 1.5)",
            "(COALESCE(toua.tou_period_count, 0) * 1.5)",
        )
        # cm.state_id does not exist - add uc.state_id and use uc.state_id in structure_optimization_analysis
        s = s.replace(
            "cm.*,\n        uc.utility_name,\n        rc.rate_code,\n        s.state_name,",
            "cm.*,\n        uc.state_id,\n        uc.utility_name,\n        rc.rate_code,\n        s.state_name,",
        )
        s = s.replace(
            "AVG(cm.complexity_score) OVER (PARTITION BY cm.state_id) AS state_avg_complexity,",
            "AVG(cm.complexity_score) OVER (PARTITION BY uc.state_id) AS state_avg_complexity,",
        )

    # Q11: avg_days_until_expiration ambiguous - final_expiration_intelligence has rea.* and ROUND(rea.avg_days...); use explicit columns
    if num == 11:
        s = s.replace(
            "SELECT\n        rea.*,\n        ROUND(rea.avg_days_until_expiration::numeric, 0) AS avg_days_until_expiration,\n        ROUND(rea.min_days_until_expiration::numeric, 0) AS min_days_until_expiration,\n        CASE\n            WHEN rea.expiring_90days > 0 THEN 'High Expiration Risk'\n            WHEN rea.expiring_180days > 0 THEN 'Moderate Expiration Risk'\n            WHEN rea.expiring_1year > 0 THEN 'Low Expiration Risk'\n            ELSE 'No Near-Term Expirations'\n        END AS expiration_risk_level\n    FROM rebate_expiration_analysis rea",
            "SELECT\n        rea.rebate_level, rea.total_rebates, rea.active_rebates, rea.expired_rebates,\n        rea.expiring_90days, rea.expiring_180days, rea.expiring_1year,\n        ROUND(rea.avg_days_until_expiration::numeric, 0) AS avg_days_until_expiration,\n        ROUND(rea.min_days_until_expiration::numeric, 0) AS min_days_until_expiration,\n        CASE\n            WHEN rea.expiring_90days > 0 THEN 'High Expiration Risk'\n            WHEN rea.expiring_180days > 0 THEN 'Moderate Expiration Risk'\n            WHEN rea.expiring_1year > 0 THEN 'Low Expiration Risk'\n            ELSE 'No Near-Term Expirations'\n        END AS expiration_risk_level\n    FROM rebate_expiration_analysis rea",
        )

    # Q12: Remove duplicate columns in final_geographic_optimization (zco.* + ROUND creates ambiguity)
    if num == 12:
        s = s.replace(
            "zco.*,\n        ROUND(zco.difference_from_county_avg::numeric, 6) AS difference_from_county_avg,\n        ROUND(zco.difference_from_county_avg_percentage::numeric, 2) AS difference_from_county_avg_percentage,\n        ROUND(zco.difference_from_state_avg::numeric, 6) AS difference_from_state_avg,\n        ROUND(zco.difference_from_state_avg_percentage::numeric, 2) AS difference_from_state_avg_percentage,\n        -- Window",
            "zco.*,\n        -- Window",
        )
        s = s.replace("cra.difference_from_county_avg, cra.difference_from_county_avg_percentage,", "difference_from_county_avg, difference_from_county_avg_percentage,")

    # Q13: final_portfolio_analysis has pdm.* and ROUND(pdm.diversity_score) - duplicate column; remove duplicate
    if num == 13:
        s = s.replace(
            "SELECT\n        pdm.*,\n        ROUND(pdm.diversity_score::numeric, 2) AS diversity_score,",
            "SELECT\n        pdm.utility_id, pdm.utility_name, pdm.utility_type, pdm.state_id, pdm.state_name,\n        pdm.rate_codes_offered, pdm.total_rates, pdm.rate_types_offered, pdm.structure_types_offered, pdm.sectors_covered,\n        pdm.portfolio_avg_rate, pdm.portfolio_min_rate, pdm.portfolio_max_rate,\n        pdm.state_avg_rate_codes, pdm.state_avg_total_rates, pdm.state_avg_rate_types, pdm.state_avg_structure_types, pdm.state_median_rate_codes,\n        ROUND(pdm.diversity_score::numeric, 2) AS diversity_score,\n        pdm.portfolio_completeness, pdm.rate_range_diversity,",
        )

    # Q14: final_economics_analysis has rae.* and re-adds - duplicate columns; use explicit select
    if num == 14:
        s = s.replace(
            "SELECT\n        rae.*,\n        ROUND(rae.annual_savings::numeric, 2) AS annual_savings,\n        ROUND(rae.payback_period_years::numeric, 2) AS payback_period_years,\n        ROUND(rae.total_rebates::numeric, 2) AS total_rebates,\n        ROUND(rae.net_system_cost::numeric, 2) AS net_system_cost,\n        ROUND(rae.rebate_adjusted_payback_years::numeric, 2) AS rebate_adjusted_payback_years,\n        -- Investment classification\n        CASE\n            WHEN rae.rebate_adjusted_payback_years <= 5 THEN 'Excellent Investment'\n            WHEN rae.rebate_adjusted_payback_years <= 8 THEN 'Good Investment'\n            WHEN rae.rebate_adjusted_payback_years <= 12 THEN 'Moderate Investment'\n            ELSE 'Long-Term Investment'\n        END AS investment_classification\n    FROM rebate_adjusted_economics rae",
            "SELECT\n        rae.system_size_kw, rae.total_system_cost, rae.annual_production_kwh, rae.utility_id, rae.utility_name, rae.state_id,\n        rae.retail_rate, rae.effective_export_rate, rae.net_metering_capacity_limit_kw,\n        ROUND(rae.annual_savings::numeric, 2) AS annual_savings,\n        ROUND(rae.payback_period_years::numeric, 2) AS payback_period_years,\n        ROUND(rae.total_rebates::numeric, 2) AS total_rebates,\n        ROUND(rae.net_system_cost::numeric, 2) AS net_system_cost,\n        ROUND(rae.rebate_adjusted_payback_years::numeric, 2) AS rebate_adjusted_payback_years,\n        CASE\n            WHEN rae.rebate_adjusted_payback_years <= 5 THEN 'Excellent Investment'\n            WHEN rae.rebate_adjusted_payback_years <= 8 THEN 'Good Investment'\n            WHEN rae.rebate_adjusted_payback_years <= 12 THEN 'Moderate Investment'\n            ELSE 'Long-Term Investment'\n        END AS investment_classification\n    FROM rebate_adjusted_economics rae",
        )

    # Q15: final_volatility_analysis has ra.* and re-adds avg_rate_3yr - duplicate columns cause ambiguity
    if num == 15:
        old15 = (
            "SELECT\n        ra.*,\n        ROUND(ra.avg_rate_3yr::numeric, 6) AS avg_rate_3yr,\n        ROUND(ra.rate_volatility::numeric, 6) AS rate_volatility,\n        ROUND(ra.coefficient_of_variation::numeric, 2) AS coefficient_of_variation,\n        ROUND(ra.rate_range_3yr::numeric, 6) AS rate_range_3yr,\n        ROUND(ra.state_avg_volatility::numeric, 2) AS state_avg_volatility,\n        ROUND((ra.state_volatility_percentile  * 100)::numeric, 2) AS state_volatility_percentile\n    FROM risk_assessment ra"
        )
        new15 = (
            "SELECT\n        ra.utility_id, ra.utility_name, ra.rate_code_id, ra.rate_code, ra.state_id, ra.state_name,\n        ra.months_analyzed, ra.min_rate_3yr, ra.max_rate_3yr, ra.volatility_classification, ra.risk_level,\n        ROUND(ra.avg_rate_3yr::numeric, 6) AS avg_rate_3yr,\n        ROUND(ra.rate_volatility::numeric, 6) AS rate_volatility,\n        ROUND(ra.coefficient_of_variation::numeric, 2) AS coefficient_of_variation,\n        ROUND(ra.rate_range_3yr::numeric, 6) AS rate_range_3yr,\n        ROUND(ra.state_avg_volatility::numeric, 2) AS state_avg_volatility,\n        ROUND((ra.state_volatility_percentile * 100)::numeric, 2) AS state_volatility_percentile\n    FROM risk_assessment ra"
        )
        if old15 in s:
            s = s.replace(old15, new15)
        else:
            # Fallback: replace ra.* with explicit columns
            s = s.replace(
                "ra.*,\n        ROUND(ra.avg_rate_3yr::numeric, 6) AS avg_rate_3yr,",
                "ra.utility_id, ra.utility_name, ra.rate_code_id, ra.rate_code, ra.state_id, ra.state_name,\n        ra.months_analyzed, ra.min_rate_3yr, ra.max_rate_3yr, ra.volatility_classification, ra.risk_level,\n        ROUND(ra.avg_rate_3yr::numeric, 6) AS avg_rate_3yr,",
            )

    # Q30: monthly_cost_1000kwh ambiguous - optimization_recommendations has cos.* and ROUND(cos.monthly_cost...); use explicit select
    if num == 30:
        s = s.replace(
            "SELECT\n        cos.*,\n        ROUND(cos.monthly_cost_1000kwh::numeric, 2) AS monthly_cost_1000kwh,\n        ROUND(cos.monthly_cost_2000kwh::numeric, 2) AS monthly_cost_2000kwh,\n        CASE\n            WHEN cos.competitiveness = 'More Competitive' THEN 'Optimal Rate'\n            WHEN cos.competitiveness = 'Less Competitive' THEN 'Consider Alternative Rates'\n            ELSE 'Evaluate Further'\n        END AS optimization_recommendation\n    FROM cost_optimization_scenarios cos",
            "SELECT\n        cos.rate_id, cos.utility_id, cos.utility_name, cos.state_id, cos.state_name,\n        cos.rate_code_id, cos.rate_code, cos.rate_type,\n        cos.energy_charge_usd_per_kwh, cos.fixed_charge_usd, cos.state_avg_rate, cos.utility_avg_rate,\n        ROUND(cos.monthly_cost_1000kwh::numeric, 2) AS monthly_cost_1000kwh,\n        ROUND(cos.monthly_cost_2000kwh::numeric, 2) AS monthly_cost_2000kwh,\n        cos.competitiveness,\n        CASE\n            WHEN cos.competitiveness = 'More Competitive' THEN 'Optimal Rate'\n            WHEN cos.competitiveness = 'Less Competitive' THEN 'Consider Alternative Rates'\n            ELSE 'Evaluate Further'\n        END AS optimization_recommendation\n    FROM cost_optimization_scenarios cos",
        )

    # Q26: ARRAY[rc.rate_code_id] AS code_path -> cast for recursive
    if num == 26:
        s = s.replace("ARRAY[rc.rate_code_id] AS code_path", "ARRAY[rc.rate_code_id]::varchar[] AS code_path")

    return s


def main():
    data = json.loads(QPATH.read_text(encoding="utf-8"))
    changed = False
    for q in data.get("queries", []):
        num = q.get("number")
        old = q.get("sql", "")
        new = fix_query(old, num)
        if new != old:
            q["sql"] = new
            changed = True
    if changed:
        QPATH.write_text(json.dumps(data, indent=2))
        print("db-15: updated")
    else:
        print("db-15: no changes")


if __name__ == "__main__":
    main()
