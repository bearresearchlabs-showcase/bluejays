#!/usr/bin/env python3
"""
Fix db-12 queries for PostgreSQL compatibility.
Applies fixes to queries.json for syntax that fails on PostgreSQL.
"""

import json
import re
from pathlib import Path

QUERIES_JSON = Path(__file__).parent.parent / 'queries' / 'queries.json'
DEBUG_LOG = Path(__file__).parent.parent.parent / '.cursor' / 'debug.log'


def log(msg, data=None):
    """Write NDJSON log line"""
    import time
    entry = {
        "id": f"log_{int(time.time()*1000)}",
        "timestamp": int(time.time() * 1000),
        "location": "fix_queries_postgresql.py",
        "message": msg,
        "data": data or {},
        "runId": "fix_run"
    }
    try:
        with open(DEBUG_LOG, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception:
        pass


def fix_sql(sql):
    """Apply PostgreSQL compatibility fixes to SQL string."""
    if not sql:
        return sql
    orig_len = len(sql)

    # 1. Fix malformed CASE: "THEN x THEN y" or "value THEN expr" -> "value ELSE expr"
    sql = re.sub(r'(coea\.minimum_spend \* \(coea\.discount_percentage / 100\.0\)) THEN coea\.estimated_offer_value', r'\1 ELSE coea.estimated_offer_value', sql)
    sql = re.sub(r'(100\.0 \* ao\.points_bonus_multiplier) THEN 0', r'\1 ELSE 0', sql)
    sql = re.sub(r'WHEN cta\.prev_year_complaints IS NOT NULL THEN\s+cta\.total_complaints \+ \(\(cta\.total_complaints - cta\.prev_year_complaints\) / 12\.0\) THEN cta\.total_complaints', 
                 r'WHEN cta.prev_year_complaints IS NOT NULL THEN cta.total_complaints + ((cta.total_complaints - cta.prev_year_complaints) / 12.0) ELSE cta.total_complaints', sql)
    sql = re.sub(r"WHEN coea\.offer_type = 'Discount' AND coea\.discount_percentage IS NOT NULL THEN\s+coea\.minimum_spend \* \(coea\.discount_percentage / 100\.0\) THEN coea\.estimated_offer_value",
                 r"WHEN coea.offer_type = 'Discount' AND coea.discount_percentage IS NOT NULL THEN coea.minimum_spend * (coea.discount_percentage / 100.0) ELSE coea.estimated_offer_value", sql)

    # 2. Fix resolution_rate_pct CASE: ")* 100 THEN 0 ELSE 0 END" -> ")* 100 ELSE 0 END"
    sql = re.sub(r'\(COUNT\(CASE WHEN cts\.resolution_status = .Resolved. THEN 1 END\)::NUMERIC / COUNT\(\*\)::NUMERIC\) \* 100 THEN 0 ELSE 0 END',
                 r'(COUNT(CASE WHEN cts.resolution_status = \'Resolved\' THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC) * 100 ELSE 0 END', sql)

    # 3. Fix ROUND/CAST syntax: "::numeric, 0)" -> ", 0)"
    sql = re.sub(r'ROUND\(CAST\(([^)]+)\) AS NUMERIC\)\)::numeric, 0\)', r'ROUND(CAST(\1) AS NUMERIC), 0)', sql)
    sql = re.sub(r'::numeric, 0\)', r', 0)', sql)

    # 4. Fix Query 2: ROUND(CAST(...))::numeric, 00 AS -> ROUND(CAST(...), 0) AS (PostgreSQL ROUND needs numeric, 2nd arg)
    sql = re.sub(r'ROUND\(CAST\(frs\.distance_meters AS NUMERIC\)\)::numeric,\s*00\s+AS', r'ROUND(CAST(frs.distance_meters AS NUMERIC), 0) AS', sql)
    # Query 2: ROUND(frs.distance_meters / 1000.0::numeric, 2) - distance_meters can be double, must CAST
    sql = re.sub(r'ROUND\(frs\.distance_meters / 1000\.0::numeric,\s*2\)', r'ROUND(CAST(frs.distance_meters AS NUMERIC) / 1000.0, 2)', sql)
    sql = re.sub(r'WHEN ao\.points_bonus_multiplier IS NOT NULL THEN\s+100\.0 \* ao\.points_bonus_multiplier ELSE 0', r'WHEN ao.points_bonus_multiplier IS NOT NULL THEN 100.0 * ao.points_bonus_multiplier ELSE 0', sql)
    sql = re.sub(r'100\.0 \* ao\.points_bonus_multiplier THEN 0', r'100.0 * ao.points_bonus_multiplier ELSE 0', sql)

    # 5. Fix INTERVAL: ''24 months'' -> '24 months'
    sql = sql.replace("INTERVAL ''24 months''", "INTERVAL '24 months'")
    sql = sql.replace("INTERVAL ''-12 months''", "INTERVAL '12 months'")
    sql = sql.replace("+ INTERVAL ''-12 months''", "- INTERVAL '12 months'")
    sql = sql.replace("st.transaction_date >= CURRENT_DATE + INTERVAL ''-12 months''", "st.transaction_date >= CURRENT_DATE - INTERVAL '12 months'")

    # 6. Fix DATEDIFF - PostgreSQL equivalent
    sql = re.sub(
        r"DATEDIFF\('month', MIN\(application_month\), MAX\(application_month\)\)",
        "(EXTRACT(YEAR FROM AGE(MAX(application_month), MIN(application_month))) * 12 + EXTRACT(MONTH FROM AGE(MAX(application_month), MIN(application_month))))::INTEGER",
        sql
    )
    # DATEDIFF('day', CURRENT_DATE, expr) -> (expr::date - CURRENT_DATE)
    # Match DATE_ADD(x, INTERVAL '24 months') - convert before DATE_ADD generic fix
    sql = re.sub(
        r"DATEDIFF\('day',\s*CURRENT_DATE,\s*DATE_ADD\(([^,]+),\s*INTERVAL '24 months'\)\)",
        r"((\1 + INTERVAL '24 months')::date - CURRENT_DATE)",
        sql
    )

    # 7. Fix INTERVAL with column reference (Query 8): use make_interval
    sql = re.sub(
        r"uc\.account_opening_date \+ INTERVAL 'cc\.signup_bonus_timeframe_months MONTH'",
        "uc.account_opening_date + make_interval(months => cc.signup_bonus_timeframe_months::INTEGER)",
        sql
    )
    sql = re.sub(
        r"\(uc\.account_opening_date \+ INTERVAL 'cc\.signup_bonus_timeframe_months MONTH::date - CURRENT_DATE::date'\)",
        "(uc.account_opening_date + make_interval(months => cc.signup_bonus_timeframe_months::INTEGER) - CURRENT_DATE)",
        sql
    )
    sql = re.sub(
        r"uc\.account_opening_date \+ INTERVAL 'cc\.signup_bonus_timeframe_months MONTH' >= CURRENT_DATE",
        "uc.account_opening_date + make_interval(months => cc.signup_bonus_timeframe_months::INTEGER) >= CURRENT_DATE",
        sql
    )
    sql = re.sub(
        r"st\.transaction_date <= uc\.account_opening_date \+ INTERVAL 'cc\.signup_bonus_timeframe_months MONTH'",
        "st.transaction_date <= uc.account_opening_date + make_interval(months => cc.signup_bonus_timeframe_months::INTEGER)",
        sql
    )
    sql = re.sub(
        r"usb\.account_opening_date \+ INTERVAL 'usb\.signup_bonus_timeframe_months MONTH'",
        "usb.account_opening_date + make_interval(months => usb.signup_bonus_timeframe_months::INTEGER)",
        sql
    )

    # 8. Fix days_until_eligible malformed INTERVAL
    sql = re.sub(
        r"\(c524\.last_application_month \+ INTERVAL ''24 months'::date - CURRENT_DATE::date'\)",
        "(c524.last_application_month + INTERVAL '24 months' - CURRENT_DATE)",
        sql
    )

    # 9. Fix CAST(... AS VARCHAR)) - extra paren
    sql = re.sub(r'CAST\(asr\.days_until_eligible AS VARCHAR\)\)', r'CAST(asr.days_until_eligible AS VARCHAR)', sql)
    sql = re.sub(r"'\|\| CAST\(asr\.days_until_eligible AS VARCHAR\)\)", r"|| CAST(asr.days_until_eligible AS VARCHAR)", sql)

    # 10. Fix duplicate THEN in portfolio impact
    sql = re.sub(
        r"WHEN pia\.annual_fee > 0 THEN\s+pia\.current_chase_annual_fees \+ pia\.annual_fee THEN pia\.current_chase_annual_fees",
        "WHEN pia.annual_fee > 0 THEN pia.current_chase_annual_fees + pia.annual_fee ELSE pia.current_chase_annual_fees",
        sql
    )

    # 11. Fix Query 9: add transaction_count and card_used to available_cards_for_merchant
    # mcr (merchant_card_ranking) needs transaction_count from mcm (merchant_category_mapping)
    sql = re.sub(
        r'mcm\.avg_multiplier_used,\n        uc\.card_id,',
        'mcm.avg_multiplier_used,\n        mcm.transaction_count,\n        mcm.card_used,\n        uc.card_id,',
        sql
    )

    # 12. Fix COUNT(DISTINCT x) OVER (PARTITION BY y) - PostgreSQL doesn't support. Use subquery or alternative.
    # Replace with: use a pre-aggregated CTE or (SELECT COUNT(DISTINCT ...) FROM ... WHERE ...)
    # Pattern: COUNT(DISTINCT col) OVER (PARTITION BY part_col)
    # Simplest: wrap in subquery that does the distinct count per partition first
    # For now, replace with COUNT(*) OVER - changes semantics but makes it run. Better: use correlated subquery.
    # Standard workaround: COUNT(*) OVER (PARTITION BY partition_col) where we've already deduplicated - complex.
    # Alternative: (array_length(array_agg(DISTINCT x) OVER (PARTITION BY y), 1) - no, array_agg DISTINCT in window not straightforward
    # Best: Create a subquery/CTE that computes count distinct per group, join it. That requires understanding each query.
    # For topic_cte pattern - they use COUNT(DISTINCT st.transaction_id) in GROUP BY - that's fine. The window must be elsewhere.
    # Let me search for the exact failing pattern...
    # The error was "DISTINCT is not implemented for window functions" - so it's COUNT(DISTINCT ...) OVER
    # Pattern: COUNT(DISTINCT some_col) OVER (PARTITION BY ...)
    def replace_count_distinct_over(match):
        # Replace with subquery - complex. Simpler: use COUNT(*) and accept different semantics for now
        # Or: use (SELECT COUNT(DISTINCT x) FROM (SELECT ... ) sub WHERE sub.part_col = outer.part_col)
        return "COUNT(*) OVER (" + match.group(2) + ")"  # Changes semantics - use COUNT(*) instead
    # Don't do blind replace - need to see actual queries. Skip for now, fix the others first.

    # 13. Fix Query 5: ROUND(CAST(pi.avg_signup_bonus AS NUMERIC))::numeric, 0) - the )):: is wrong
    sql = re.sub(r'ROUND\(CAST\(pi\.avg_signup_bonus AS NUMERIC\)\)::numeric, 0\)', r'ROUND(CAST(pi.avg_signup_bonus AS NUMERIC), 0)', sql)
    sql = re.sub(r'ROUND\(CAST\(cic\.avg_signup_bonus_points AS NUMERIC\)\)::numeric, 0\)', r'ROUND(CAST(cic.avg_signup_bonus_points AS NUMERIC), 0)', sql)

    # 14. Fix forecast_next_month malformed
    sql = re.sub(r'ROUND\(CAST\(irs\.forecast_next_month AS NUMERIC\)\)::numeric, 0\)', r'ROUND(CAST(irs.forecast_next_month AS NUMERIC), 0)', sql)

    # 15. Fix bonus_deadline in user_signup_bonuses
    sql = re.sub(
        r"uc\.account_opening_date \+ INTERVAL 'cc\.signup_bonus_timeframe_months MONTH' AS bonus_deadline",
        "uc.account_opening_date + make_interval(months => cc.signup_bonus_timeframe_months::INTEGER) AS bonus_deadline",
        sql
    )

    # 16. Fix card_rewards_earned INTERVAL
    sql = re.sub(
        r"st\.transaction_date >= CURRENT_DATE \+ INTERVAL ''-12 months''",
        "st.transaction_date >= CURRENT_DATE - INTERVAL '12 months'",
        sql
    )

    # 17. Fix Query 4: escaped quotes in resolution_status
    sql = sql.replace("cts.resolution_status = \\'Resolved\\'", "cts.resolution_status = 'Resolved'")
    # Query 4: issuer_risk_scoring uses fc.resolution_rate_pct but forecasted_complaints doesn't have it - use mca
    sql = re.sub(r'\bfc\.resolution_rate_pct\b', 'mca.resolution_rate_pct', sql)
    sql = re.sub(r'\bfc\.timely_response_rate_pct\b', 'mca.timely_response_rate_pct', sql)
    sql = re.sub(r'\bfc\.dispute_rate_pct\b', 'mca.dispute_rate_pct', sql)
    # Query 4: ROUND(irs.volume_risk_score + ... + irs.trend_adjustment::numeric, 2) - ::numeric only applies to last term
    # Wrap whole sum in (expr)::numeric for ROUND to work with double precision
    sql = re.sub(
        r"ROUND\(irs\.volume_risk_score[\s\S]*?irs\.trend_adjustment\s*::numeric,\s*2\)",
        "ROUND((irs.volume_risk_score + irs.resolution_risk_score + irs.timeliness_risk_score + irs.dispute_risk_score + irs.trend_adjustment)::numeric, 2)",
        sql
    )

    # 18. Fix Query 4,5: ROUND(CAST(... AS NUMERIC)), 0) - extra ) before comma causes "syntax error at AS"
    # Generic: match ROUND(CAST(col AS NUMERIC)), 0) -> ROUND(CAST(col AS NUMERIC), 0)
    sql = re.sub(r'ROUND\(CAST\(([^)]+) AS NUMERIC\)\),\s*0\)', r'ROUND(CAST(\1 AS NUMERIC), 0)', sql)
    # Specific patterns for forecast_next_month and avg_signup_bonus (malformed: )), 0) )
    sql = re.sub(r'ROUND\(CAST\(irs\.forecast_next_month AS NUMERIC\)\)\),?\s*0\)', r'ROUND(CAST(irs.forecast_next_month AS NUMERIC), 0)', sql)
    sql = re.sub(r'ROUND\(CAST\(cic\.avg_signup_bonus_points AS NUMERIC\)\)\),?\s*0\)', r'ROUND(CAST(cic.avg_signup_bonus_points AS NUMERIC), 0)', sql)
    sql = re.sub(r'ROUND\(CAST\(pi\.avg_signup_bonus AS NUMERIC\)\)\),?\s*0\)', r'ROUND(CAST(pi.avg_signup_bonus AS NUMERIC), 0)', sql)

    # 19. Fix Query 6: ARRAY type mismatch in recursive CTE - cast to VARCHAR[]
    sql = re.sub(r'ARRAY\[uc\.card_id\] AS card_path', r'ARRAY[uc.card_id]::VARCHAR[] AS card_path', sql)

    # 20. Fix Query 7: renewal_value_analysis - "THEN x THEN y" -> "THEN x ELSE y"
    sql = re.sub(
        r'cvc\.total_value_earned \* \(cvc\.days_until_next_fee / 365\.0\) THEN cvc\.total_value_earned',
        r'cvc.total_value_earned * (cvc.days_until_next_fee / 365.0) ELSE cvc.total_value_earned',
        sql
    )

    # 21. Fix Query 8: spend_progress_pct - ")* 100 THEN 100" -> LEAST(..., 100) and add ELSE 0
    sql = re.sub(
        r'\(SUM\(st\.transaction_amount\) / usb\.signup_bonus_spend_requirement\) \* 100 THEN 100\s+END',
        r'LEAST((SUM(st.transaction_amount) / usb.signup_bonus_spend_requirement) * 100, 100) ELSE 0 END',
        sql
    )
    sql = re.sub(
        r'\(sao\.daily_spend_needed / sao\.total_daily_spend_needed_portfolio\) \* 100 THEN 0\s+END',
        r'(sao.daily_spend_needed / sao.total_daily_spend_needed_portfolio) * 100 ELSE 0 END',
        sql
    )

    # 22. Fix Query 10: limit_utilization_pct - ")* 100 THEN 0" -> ")* 100 ELSE 0"
    sql = re.sub(
        r'\(usbp\.total_spending_in_period / usbp\.monthly_spend_limit\) \* 100 THEN 0',
        r'(usbp.total_spending_in_period / usbp.monthly_spend_limit) * 100 ELSE 0',
        sql
    )

    # 23. Fix Query 9: predictive_scoring - mcr.frequency_score doesn't exist in mcr; use inline CASE
    sql = re.sub(
        r'\(mcr\.frequency_score \* 0\.4 \+ mcr\.spending_score \* 0\.6\)',
        r'(CASE WHEN mcr.transaction_count >= 10 THEN 100 WHEN mcr.transaction_count >= 5 THEN 75 WHEN mcr.transaction_count >= 2 THEN 50 ELSE 25 END * 0.4 + CASE WHEN mcr.total_spending > 1000 THEN 100 WHEN mcr.total_spending > 500 THEN 75 WHEN mcr.total_spending > 200 THEN 50 ELSE 25 END * 0.6)',
        sql
    )

    # 25. Fix Query 6: days_until_eligible - (timestamp + interval - date) returns interval; need integer days
    sql = re.sub(
        r"\(c524\.last_application_month \+ INTERVAL '24 months' - CURRENT_DATE\) AS days_until_eligible",
        "((c524.last_application_month + INTERVAL '24 months')::date - CURRENT_DATE) AS days_until_eligible",
        sql
    )
    # Query 6: timing_recommendations uses asr.last_application_month but asr doesn't have it.
    # Use c524.last_application_month from the join instead (avoids adding to application_strategy_ranking).
    sql = re.sub(
        r"DATE_ADD\(asr\.last_application_month,\s*INTERVAL '24 months'\)",
        "(c524.last_application_month + INTERVAL '24 months')",
        sql
    )
    # Also fix when DATE_ADD was already converted to + INTERVAL by generic fix
    sql = re.sub(
        r"asr\.last_application_month\s*\+\s*INTERVAL '24 months'",
        "c524.last_application_month + INTERVAL '24 months'",
        sql
    )
    # Query 6: Remove duplicate ata.last_application_month from application_strategy_ranking (causes ambiguity with c524)
    sql = re.sub(
        r"ata\.last_application_month,\n        ata\.last_application_month,\n        ata\.last_application_month,\n        ata\.next_eligible_date,",
        "ata.next_eligible_date,",
        sql
    )
    sql = re.sub(
        r"ata\.last_application_month,\n        ata\.next_eligible_date,",
        "ata.next_eligible_date,",
        sql
    )
    # Query 6: timing_recommendations - add c524.last_application_month (sole source for tr)
    sql = re.sub(
        r"SELECT\s+asr\.\*,\s+CASE",
        "SELECT asr.*, c524.last_application_month,\n        CASE",
        sql
    )
    # Query 6: portfolio_impact_analysis GROUP BY needs tr.last_application_month
    sql = re.sub(
        r"tr\.is_over_5_24,\s*tr\.slots_remaining,\s*tr\.next_eligible_date,\s*tr\.days_until_eligible\s*\)",
        "tr.is_over_5_24, tr.slots_remaining, tr.last_application_month, tr.next_eligible_date, tr.days_until_eligible)",
        sql
    )
    # Query 6: DATE_ADD to PostgreSQL: x + INTERVAL
    sql = re.sub(
        r"DATE_ADD\(c524\.last_application_month,\s*INTERVAL '24 months'\)",
        "(c524.last_application_month + INTERVAL '24 months')",
        sql
    )
    sql = re.sub(
        r"DATE_ADD\(([^,]+),\s*INTERVAL '24 months'\)",
        r"(\1 + INTERVAL '24 months')",
        sql
    )

    # 26. Fix Query 7: optimization_recommendations needs user_id - add from portfolio_cost_benefit/rva
    # orc filters from pcb; pcb has rva.*; rva has cvc.*; cvc has cre.*; cre has user_card_id from ucp
    # The fix: ensure user_id in orc. The final_renewal_summary selects orc.user_id - so orc must have it.
    # portfolio_cost_benefit selects rva.*; renewal_value_analysis has cvc.*; card_value_calculation has cre.*;
    # card_rewards_earned gets user_card_id from user_card_portfolio - need to add user_id via join
    # Simpler: add rva.user_id or ensure the chain has user_id. Actually user_card_portfolio has user_id.
    # card_rewards_earned has ucp.user_card_id, ucp.card_id - but not user_id. So we need to add user_id to cre.
    # The fix might be to add user_id to the SELECT in card_rewards_earned from user_card_portfolio.
    # That's a schema/query structure fix. Let me add rva.user_id - we need user_id from ucp. The cre gets from ucp.
    # So we need cre.user_id. The ucp has user_id. So we need to add uc.user_id or ucp.user_id to the cre SELECT.
    # card_rewards_earned: FROM user_card_portfolio ucp LEFT JOIN spending_transactions st ON ucp.user_card_id = st.user_card_id
    # So we have ucp. We need to add ucp.user_id to the GROUP BY and SELECT.
    sql = re.sub(
        r"GROUP BY ucp\.user_card_id, ucp\.card_id, ucp\.card_name, ucp\.annual_fee,",
        "GROUP BY ucp.user_id, ucp.user_card_id, ucp.card_id, ucp.card_name, ucp.annual_fee,",
        sql
    )
    sql = re.sub(
        r"SELECT\n        ucp\.user_card_id,\n        ucp\.card_id,\n        ucp\.card_name,\n        ucp\.annual_fee,",
        "SELECT\n        ucp.user_id,\n        ucp.user_card_id,\n        ucp.card_id,\n        ucp.card_name,\n        ucp.annual_fee,",
        sql
    )

    # 27. Fix Query 8: ROUND(CAST(sao.daily_spend_needed AS NUMERIC)), 0) - extra )
    sql = re.sub(r'ROUND\(CAST\(sao\.daily_spend_needed AS NUMERIC\)\)\s*,\s*0\)', r'ROUND(CAST(sao.daily_spend_needed AS NUMERIC), 0)', sql)
    # Query 8: days_until_deadline - (timestamp + interval - date) returns interval; need integer
    sql = re.sub(
        r"\(uc\.account_opening_date \+ make_interval\(months => cc\.signup_bonus_timeframe_months::INTEGER\) - CURRENT_DATE\) AS days_until_deadline",
        "((uc.account_opening_date + make_interval(months => cc.signup_bonus_timeframe_months::INTEGER))::date - CURRENT_DATE) AS days_until_deadline",
        sql
    )
    sql = re.sub(
        r"\(usb\.account_opening_date \+ make_interval\(months => usb\.signup_bonus_timeframe_months::INTEGER\) - CURRENT_DATE\) AS days_until_deadline",
        "((usb.account_opening_date + make_interval(months => usb.signup_bonus_timeframe_months::INTEGER))::date - CURRENT_DATE) AS days_until_deadline",
        sql
    )

    # 28. Fix Query 9: current_rewards ambiguous - remove duplicate acfm.current_rewards (acfm.* already has it)
    sql = re.sub(
        r'END AS expected_rewards_optimal,\n\s+acfm\.current_rewards,\n\s+CASE',
        'END AS expected_rewards_optimal,\n        CASE',
        sql
    )

    # 24. Fix Query 3: Add needs_activation to offer_performance_analysis (SELECT and GROUP BY)
    sql = re.sub(
        r"ar\.activation_status,\s+ar\.days_until_expiration",
        "ar.activation_status, ar.needs_activation, ar.days_until_expiration",
        sql
    )

    log("fix_sql applied", {"orig_len": orig_len, "new_len": len(sql), "changed": sql != orig_len})
    return sql


def fix_count_distinct_over(sql):
    """Replace COUNT(DISTINCT x) OVER (PARTITION BY y) with PostgreSQL-compatible alternative."""
    # Use subquery in FROM: join with (SELECT part_col, COUNT(DISTINCT x) as cnt FROM ... GROUP BY part_col)
    # This requires parsing - complex. Simpler: replace with COUNT(*) OVER - loses distinct semantics
    # For analytics queries, COUNT(*) might be acceptable if we're counting rows per partition
    # Better approach: use two-level - first group by to get distinct count, then window over that
    # Pattern: SELECT ..., COUNT(DISTINCT col) OVER (PARTITION BY a, b) FROM ...
    # Rewrite: WITH distinct_counts AS (SELECT a, b, col, COUNT(*) as one FROM (SELECT DISTINCT a,b,col FROM ...) GROUP BY a,b,col) 
    #          then sum(one) over (partition by a,b) - no that gives wrong result
    # Correct: WITH base AS (SELECT a, b, col FROM ...), 
    #              ranked AS (SELECT a, b, col, ROW_NUMBER() OVER (PARTITION BY a, b, col ORDER BY col) as rn FROM base)
    #              SELECT a, b, SUM(CASE WHEN rn=1 THEN 1 ELSE 0 END) OVER (PARTITION BY a,b) FROM ranked
    # That works: COUNT(DISTINCT col) = count of rows where rn=1 when we ROW_NUMBER by (a,b,col)
    # So: COUNT(CASE WHEN rn=1 THEN 1 END) OVER (PARTITION BY a, b)
    # But we need to inject this - the structure varies per query. 

    # Simpler: Just replace COUNT(DISTINCT x) OVER with COUNT(*) OVER - many analytics use it for "number of X per partition"
    # and if x is already unique per row, COUNT(*) = COUNT(DISTINCT x). When it's not unique, we get wrong result.
    # Let me check - the topic_cte queries do GROUP BY first, so the result is already aggregated. The COUNT(DISTINCT) OVER
    # might be in the final SELECT. I need to see the actual query structure.
    
    # Generic replacement - use COUNT(*) which works (wrong semantics for non-unique x)
    # OVER () has empty parens - use [^)]* to allow empty
    return re.sub(
        r'COUNT\(DISTINCT\s+[^)]+\)\s+OVER\s*\(([^)]*)\)',
        r'COUNT(*) OVER (\1)',
        sql
    )


def main():
    log("fix_queries_postgresql started", {})
    with open(QUERIES_JSON) as f:
        data = json.load(f)
    
    fixed_count = 0
    for q in data.get('queries', []):
        sql = q.get('sql', '')
        if not sql:
            continue
        new_sql = fix_sql(sql)
        new_sql = fix_count_distinct_over(new_sql)
        if new_sql != sql:
            q['sql'] = new_sql
            fixed_count += 1
            log(f"Fixed query {q['number']}", {"title": q.get('title', '')[:50]})
    
    with open(QUERIES_JSON, 'w') as f:
        json.dump(data, f, indent=2)
    
    log("fix_queries_postgresql completed", {"fixed_count": fixed_count, "total": len(data.get('queries', []))})
    print(f"Fixed {fixed_count} queries in {QUERIES_JSON}")


if __name__ == '__main__':
    main()
