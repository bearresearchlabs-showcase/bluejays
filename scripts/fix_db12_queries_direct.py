#!/usr/bin/env python3
"""Direct fixes for db-12 SQL queries - apply to queries.json."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
QJ = ROOT / "source" / "db-12" / "app" / "QUERIES" / "queries.json"


def fix_sql_direct(sql: str, query_num: int = None) -> str:
    s = sql
    # 0. ROUNDROUND corruption -> ROUND (fix_postgresql can produce this)
    s = re.sub(r'\bROUNDROUND\b', 'ROUND', s, flags=re.I)
    # 1. ROUND(expr::numeric, 00 AS -> ROUND(expr::numeric, 0) AS
    s = re.sub(r'(::numeric)\s*,\s*00\s+AS\s+', r'\1, 0) AS ', s, flags=re.I)
    # 1b. ROUND(expr, 00 AS (without ::numeric before) - e.g. ROUND(frs.distance_meters::numeric, 00 AS
    s = re.sub(r',\s*00\s+AS\s+', r', 0) AS ', s, flags=re.I)
    # 2. ROUND(((((expr / 1000.0::numeric, 2) or ROUND((((expr / 1000.0)::numeric, 2) -> ROUND((expr / 1000.0)::numeric, 2)
    s = re.sub(r'ROUND\s*\(\s*(\(\s*)+([^/]+)\s*/\s*1000\.0\s*\)?\s*::\s*numeric\s*,\s*2\s*\)', r'ROUND((\2 / 1000.0)::numeric, 2)', s, flags=re.I)
    # 3. THEN X THEN 0 ELSE 0 -> THEN X ELSE 0
    while re.search(r'THEN\s+.+?\s+THEN\s+0\s+ELSE\s+0', s, re.I | re.DOTALL):
        s = re.sub(r'THEN\s+(.+?)\s+THEN\s+0\s+ELSE\s+0', r'THEN \1 ELSE 0', s, flags=re.I | re.DOTALL, count=1)
    # 3b. THEN 50 THEN 25 ELSE 25 -> THEN 50 ELSE 25 (duplicate THEN with numeric)
    while re.search(r'THEN\s+\d+\s+THEN\s+\d+\s+ELSE\b', s, re.I):
        s = re.sub(r'THEN\s+(\d+)\s+THEN\s+(\d+)\s+ELSE\s+(\d+)', r'THEN \1 ELSE \3', s, flags=re.I, count=1)
    # 3c. resolution_rate_pct: (expr) * 100 THEN 0 ELSE 0 -> (expr) * 100 ELSE 0 (malformed CASE)
    s = re.sub(
        r'\)\s*::\s*NUMERIC\s*/\s*COUNT\s*\(\s*\*\s*\)\s*::\s*NUMERIC\)\s*\*\s*100\s+THEN\s+0\s+ELSE\s+0\s+END',
        ')::NUMERIC / COUNT(*)::NUMERIC) * 100 ELSE 0 END',
        s,
        flags=re.I
    )
    # 3d. Q8: (expr) * 100 THEN 100 ELSE -> (expr) * 100 ELSE (when LEAST/cap at 100)
    s = re.sub(
        r'\)\s*/\s*usb\.signup_bonus_spend_requirement\)\s*\*\s*100\s+THEN\s+100\s+ELSE\b',
        ') / usb.signup_bonus_spend_requirement) * 100 ELSE',
        s,
        flags=re.I
    )
    # 3e. Q8: THEN signup_bonus_points THEN 0 ELSE 0 -> THEN signup_bonus_points ELSE 0
    s = re.sub(
        r"THEN\s+signup_bonus_points\s+THEN\s+0\s+ELSE\s+0\s+END",
        r"THEN signup_bonus_points ELSE 0 END",
        s,
        flags=re.I
    )
    # 4. THEN X THEN 100 ELSE -> THEN X ELSE (for Q8)
    while re.search(r'THEN\s+.+?\s+THEN\s+100\s+ELSE\b', s, re.I | re.DOTALL):
        s = re.sub(r'THEN\s+(.+?)\s+THEN\s+100\s+ELSE\b', r'THEN \1 ELSE', s, flags=re.I | re.DOTALL, count=1)
    # 4b. THEN X THEN NULL ELSE NULL -> THEN X ELSE NULL (for Q2 applicable_offer)
    while re.search(r'THEN\s+.+?\s+THEN\s+NULL\s+ELSE\s+NULL', s, re.I | re.DOTALL):
        s = re.sub(r'THEN\s+(.+?)\s+THEN\s+NULL\s+ELSE\s+NULL', r'THEN \1 ELSE NULL', s, flags=re.I | re.DOTALL, count=1)
    # 5. INTERVAL ''24 months'' -> INTERVAL '24 months'
    s = re.sub(r"INTERVAL\s+''([^']+)''", r"INTERVAL '\1'", s, flags=re.I)
    # 5a. DATEDIFF('month') - also in fix_postgresql; keep here for when fix_db12 runs alone
    s = re.sub(
        r"DATEDIFF\s*\(\s*'month'\s*,\s*(MIN\([^)]+\))\s*,\s*(MAX\([^)]+\))\s*\)",
        r"((EXTRACT(YEAR FROM age((\2)::timestamp, (\1)::timestamp)) * 12 + EXTRACT(MONTH FROM age((\2)::timestamp, (\1)::timestamp))))::integer",
        s,
        flags=re.I
    )
    # 5a-repair: Fix corrupted age(MAX(x::timestamp, MIN(x)::timestamp) -> age(MAX(x)::timestamp, MIN(x)::timestamp)
    s = re.sub(
        r"age\s*\(\s*MAX\s*\(\s*([^)]+)\s*::\s*timestamp\s*,\s*MIN\s*\(\s*\1\s*\)\s*::\s*timestamp\s*\)\s*\)?",
        r"age(MAX(\1)::timestamp, MIN(\1)::timestamp)",
        s,
        flags=re.I
    )
    # 5a-repair-extra: Remove stray )::integer) -> )::integer (extra paren from corruption)
    s = re.sub(
        r"\)\s*::\s*integer\s*\)\s+AS\s+months_span",
        r")::integer AS months_span",
        s,
        flags=re.I
    )
    # 5b. Q6: Recursive CTE ARRAY type - cast ARRAY[uc.card_id] to VARCHAR[] for compatibility
    s = re.sub(r'\bARRAY\s*\[\s*uc\.card_id\s*\]\s+AS\s+card_path', 'ARRAY[uc.card_id]::VARCHAR[] AS card_path', s, flags=re.I)
    # 5c. Q6: (c524.last_application_month + INTERVAL ''24 months'::date - CURRENT_DATE::date')
    # -> ((c524.last_application_month + INTERVAL '24 months')::date - CURRENT_DATE::date)
    s = re.sub(
        r"\(\s*c524\.last_application_month\s*\+\s*INTERVAL\s+''24\s+months'::date\s*-\s*CURRENT_DATE::date'\)",
        "((c524.last_application_month + INTERVAL '24 months')::date - CURRENT_DATE::date)",
        s,
        flags=re.I
    )
    # 5d. Q6: asr.last_application_month does not exist - use c524.last_application_month (from joined chase_5_24_calculation)
    s = re.sub(
        r'\basr\.last_application_month\b',
        'c524.last_application_month',
        s,
        flags=re.I
    )
    # 6. ar.needs_activation in GROUP BY - add to offer_performance_analysis GROUP BY
    s = re.sub(
        r'(ar\.overall_offer_rank)\s*\n\s*\)\s*,\s*\n',
        r'\1,\n        ar.needs_activation\n    ),\n',
        s,
        flags=re.I,
        count=1
    )
    # 7. Q7: ROUND(((((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings
    # Fix: ROUND((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings
    s = re.sub(
        r'ROUND\s*\(\s*\(\s*\(\s*\(\s*\(\s*\(\s*orc\.optimized_net_value\s*-\s*orc\.total_portfolio_net_value\s*\)\s*::\s*numeric\s*,\s*2\s*\)\s+AS\s+potential_savings',
        'ROUND((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings',
        s,
        flags=re.I
    )
    # 7b. Q4: irs.timeliness_risk_score + irs.dispute_risk_score + irs.trend_adjustment)::numeric, 2) AS total_risk_score
    # Missing ROUND( - fix: ROUND((irs.timeliness_risk_score + irs.dispute_risk_score + irs.trend_adjustment)::numeric, 2)
    s = re.sub(
        r'(irs\.timeliness_risk_score\s*\+\s*irs\.dispute_risk_score\s*\+\s*irs\.trend_adjustment)\s*\)\s*::\s*numeric\s*,\s*2\s*\)\s+AS\s+total_risk_score',
        r'ROUND((\1)::numeric, 2) AS total_risk_score',
        s,
        flags=re.I
    )
    # 7b2. Q4: Malformed ROUND - irs.trend_adjustment\n       ::numeric, 2) AS total_risk_score (missing ) before ::numeric)
    s = re.sub(
        r'(irs\.trend_adjustment)\s*\n\s*::\s*numeric\s*,\s*2\s*\)\s+AS\s+total_risk_score',
        r'\1)::numeric, 2) AS total_risk_score',
        s,
        flags=re.I
    )
    # 7c. Q7: Malformed ROUND - orc.optimized_net_value - orc.total_portfolio_net_value::numeric, 2) (missing parens)
    s = re.sub(
        r'(orc\.optimized_net_value\s*-\s*orc\.total_portfolio_net_value)\s*::\s*numeric\s*,\s*2\s*\)\s+AS\s+potential_savings',
        r'ROUND((\1)::numeric, 2) AS potential_savings',
        s,
        flags=re.I
    )
    # 7c2. Q7: Double ROUND - ROUND((ROUND((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings
    s = re.sub(
        r'ROUND\s*\(\s*\(\s*ROUND\s*\(\s*\(orc\.optimized_net_value\s*-\s*orc\.total_portfolio_net_value\)\s*::\s*numeric\s*,\s*2\s*\)\s+AS\s+potential_savings',
        r'ROUND((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings',
        s,
        flags=re.I
    )
    # 7c3. Q7: Malformed ROUND - ROUND(((expr)::numeric, 2) AS (extra paren; replace ROUND((( with ROUND(()
    s = re.sub(
        r'ROUND\s*\(\s*\(\s*\(\s*\(orc\.optimized_net_value\s*-\s*orc\.total_portfolio_net_value\)\s*::\s*numeric\s*,\s*2\s*\)\s+AS\s+potential_savings',
        r'ROUND((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings',
        s,
        flags=re.I
    )
    # 7c3b. Simpler: ROUND(((orc. -> ROUND((orc. (string replace for the specific malformed case)
    s = s.replace(
        'ROUND(((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings',
        'ROUND((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings'
    )
    # 7c3c. ROUND(((expr)::numeric, 2) - extra open paren; ROUND(( -> ROUND(
    s = re.sub(
        r'ROUND\s*\(\s*\(\s*\(\s*\(orc\.optimized_net_value\s*-\s*orc\.total_portfolio_net_value\)\s*::\s*numeric\s*,\s*2\s*\)\s+AS\s+potential_savings',
        r'ROUND((orc.optimized_net_value - orc.total_portfolio_net_value)::numeric, 2) AS potential_savings',
        s,
        flags=re.I
    )
    # 8. Q9: (mcr.frequency_score * 0.4 + mcr.spending_score * 0.6) - can't ref aliases in same SELECT
    # Inline: replace with the CASE expressions
    s = re.sub(
        r'\(\s*mcr\.frequency_score\s*\*\s*0\.4\s*\+\s*mcr\.spending_score\s*\*\s*0\.6\s*\)\s+AS\s+merchant_importance_score',
        '''(
            CASE WHEN mcr.transaction_count >= 10 THEN 100 WHEN mcr.transaction_count >= 5 THEN 75 WHEN mcr.transaction_count >= 2 THEN 50 ELSE 25 END * 0.4 +
            CASE WHEN mcr.total_spending > 1000 THEN 100 WHEN mcr.total_spending > 500 THEN 75 WHEN mcr.total_spending > 200 THEN 50 ELSE 25 END * 0.6
        ) AS merchant_importance_score''',
        s,
        flags=re.I
    )
    # 8b. Q4 only: ROUND((((ROUND((irs...trend_adjustment)::numeric, 2) -> ROUND((irs...trend_adjustment)::numeric, 2)
    if query_num == 4:
        s = re.sub(r'ROUND\s*\(\s*\([^)]*ROUND\s*\(\s*\(', 'ROUND((', s, flags=re.I)
    # 9. Q9: mcr.card_used, ps.card_used do not exist -> card_id
    s = re.sub(r'\bmcr\.card_used\b', 'mcr.card_id', s, flags=re.I)
    s = re.sub(r'\bps\.card_used\b', 'ps.card_id', s, flags=re.I)
    # 9b. Q9: In recommendation_status (FROM predictive_scoring ps), acfm not in FROM - use ps.current_rewards
    # Only replace the ROUND(acfm.current_rewards::numeric, 2) occurrence (in recommendation_status), not acfm.current_rewards in optimal_card_calculation
    s = re.sub(r'ROUND\s*\(\s*acfm\.current_rewards\s*::\s*numeric\s*,\s*2\s*\)\s+AS\s+current_rewards', 'ROUND(ps.current_rewards::numeric, 2) AS current_rewards', s, flags=re.I)
    # 9d. Q9: optimal_card_calculation has acfm.* AND acfm.current_rewards -> duplicate column, causes ambiguity
    # Remove redundant acfm.current_rewards (already in acfm.*)
    s = re.sub(
        r'(\bEND AS expected_rewards_optimal,)\s*acfm\.current_rewards\s*,',
        r'\1',
        s,
        flags=re.I
    )
    # 9c. Q4: fc.* columns do not exist -> mca.* (fc not in FROM)
    s = re.sub(r'\bfc\.resolution_rate_pct\b', 'mca.resolution_rate_pct', s, flags=re.I)
    s = re.sub(r'\bfc\.timely_response_rate_pct\b', 'mca.timely_response_rate_pct', s, flags=re.I)
    s = re.sub(r'\bfc\.dispute_rate_pct\b', 'mca.dispute_rate_pct', s, flags=re.I)
    # 10. Q8: INTERVAL 'cc.signup_bonus_timeframe_months MONTH' and usb variant -> make_interval
    s = re.sub(
        r"INTERVAL\s+'cc\.signup_bonus_timeframe_months\s+MONTH'",
        "make_interval(months => cc.signup_bonus_timeframe_months::integer)",
        s,
        flags=re.I
    )
    s = re.sub(
        r"INTERVAL\s+'usb\.signup_bonus_timeframe_months\s+MONTH'",
        "make_interval(months => usb.signup_bonus_timeframe_months::integer)",
        s,
        flags=re.I
    )
    # 10b. Q8: days_until_deadline - (uc.account_opening_date + INTERVAL 'cc...MONTH::date - CURRENT_DATE::date')
    s = re.sub(
        r"\(uc\.account_opening_date\s*\+\s*INTERVAL\s+'cc\.signup_bonus_timeframe_months\s+MONTH::date\s*-\s*CURRENT_DATE::date'\)",
        "((uc.account_opening_date + make_interval(months => cc.signup_bonus_timeframe_months::integer))::date - CURRENT_DATE::date)",
        s,
        flags=re.I
    )
    # 10c. INTERVAL 'table.signup_bonus_timeframe_months MONTH...' (any malformed variant)
    s = re.sub(
        r"INTERVAL\s+'(cc|usb)\.signup_bonus_timeframe_months\s+MONTH[^']*'",
        r"make_interval(months => \1.signup_bonus_timeframe_months::integer)",
        s,
        flags=re.I
    )
    # 11a. Q7: orc.user_id does not exist - orc is card-level; use literal for user_001
    s = re.sub(r'\borc\.user_id\b', "'user_001'", s, flags=re.I)
    # 11b. Q7: final_renewal_summary has 'user_001' literal without alias - add AS user_id
    s = re.sub(
        r"(final_renewal_summary AS \(\s*SELECT\s+)'user_001'\s*,",
        r"\1'user_001' AS user_id,",
        s,
        flags=re.I
    )
    # 11. Q11-30: COUNT(DISTINCT t4.x) OVER () - PostgreSQL doesn't support. Use scalar subquery.
    if query_num and 11 <= query_num <= 30:
        cte_name = f"topic_cte2_q{query_num}"
        s = re.sub(
            r"COUNT\s*\(\s*DISTINCT\s+t\d+\.issuer_id\s*\)\s+OVER\s*\(\s*\)",
            f"(SELECT COUNT(DISTINCT issuer_id) FROM {cte_name})",
            s,
            flags=re.IGNORECASE
        )
        s = re.sub(
            r"COUNT\s*\(\s*DISTINCT\s+t\d+\.card_type\s*\)\s+OVER\s*\(\s*\)",
            f"(SELECT COUNT(DISTINCT card_type) FROM {cte_name})",
            s,
            flags=re.IGNORECASE
        )
        s = re.sub(
            r"COUNT\s*\(\s*DISTINCT\s+t\d+\.card_network\s*\)\s+OVER\s*\(\s*\)",
            f"(SELECT COUNT(DISTINCT card_network) FROM {cte_name})",
            s,
            flags=re.IGNORECASE
        )
    return s


def main():
    data = json.loads(QJ.read_text(encoding="utf-8"))
    changed = False
    for q in data.get("queries", []):
        old = q.get("sql", "")
        new = fix_sql_direct(old, q.get("number"))
        if new != old:
            q["sql"] = new
            changed = True
    if changed:
        QJ.write_text(json.dumps(data, indent=2))
        print("Updated db-12 queries.json")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
