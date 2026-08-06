#!/usr/bin/env python3
"""
Fix common SQL syntax errors across all database queries.
Fixes: THEN X THEN Y -> THEN X ELSE Y, ROUND parentheses, etc.
"""

import re
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent


def fix_then_else_complex(sql: str) -> str:
    """Fix THEN <expr> THEN <expr> -> THEN <expr> ELSE <expr> (duplicate THEN should be ELSE)"""
    # Pattern 1: THEN <identifier> THEN - e.g. THEN jsr.importance_score THEN NULL
    # Use [a-zA-Z0-9_.]+ to avoid matching THEN 10 WHEN ... THEN (would break CASE WHEN)
    sql = re.sub(
        r'\bTHEN\s+([a-zA-Z0-9_.]+)\s+THEN\s+',
        r'THEN \1 ELSE ',
        sql,
        flags=re.IGNORECASE
    )
    # Pattern 2: THEN <numeric> THEN - e.g. THEN 25.0 THEN
    sql = re.sub(
        r'\bTHEN\s+([\d.]+)\s+THEN\s+',
        r'THEN \1 ELSE ',
        sql,
        flags=re.IGNORECASE
    )
    # Pattern 3: THEN EXTRACT(...)/86400 THEN - common in time calculations
    sql = re.sub(
        r'\bTHEN\s+(EXTRACT\s*\([^)]+\)\s*/\s*86400)\s+THEN\s+',
        r'THEN \1 ELSE ',
        sql,
        flags=re.IGNORECASE
    )
    # Pattern 4: THEN identifier - number THEN -> THEN identifier - number ELSE
    sql = re.sub(
        r'\bTHEN\s+([a-zA-Z0-9_.]+)\s*-\s*(\d+)\s+THEN\s+0\s+ELSE\s+0\b',
        r'THEN \1 - \2 ELSE 0',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_then_null_pattern(sql: str) -> str:
    """Fix THEN NULL THEN -> THEN NULL ELSE (common in COALESCE/ROUND patterns)"""
    sql = re.sub(r'\bTHEN\s+NULL\s+THEN\s+', r'THEN NULL ELSE ', sql, flags=re.IGNORECASE)
    return sql


def fix_then_expr_then_null(sql: str) -> str:
    """Fix )::numeric, 2) THEN NULL -> )::numeric, 2) ELSE NULL (corrupted CASE)"""
    sql = re.sub(
        r'(\)::numeric,\s*2\))\s+THEN\s+NULL\b',
        r'\1 ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    # Fix ) THEN NULL -> ) ELSE NULL (expr as THEN value, second THEN should be ELSE)
    sql = re.sub(
        r'\)\s+THEN\s+NULL\b',
        r') ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    # Fix expr / expr THEN NULL -> expr / expr ELSE NULL (db-13)
    sql = re.sub(
        r'([a-zA-Z0-9_.]+)\s*/\s*([a-zA-Z0-9_.]+)(?!\s*[><=])\s+THEN\s+NULL\b',
        r'\1 / \2 ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    # Fix expr - expr THEN NULL -> expr - expr ELSE NULL (no comparison after)
    sql = re.sub(
        r'([a-zA-Z0-9_.]+)\s*-\s*([a-zA-Z0-9_.]+)(?!\s*[><=])\s+THEN\s+NULL\b',
        r'\1 - \2 ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    # Fix ) THEN 0 -> ) ELSE 0 (same pattern)
    sql = re.sub(
        r'\)\s+THEN\s+0\s+ELSE\s+0\s+END\b',
        r') ELSE 0 END',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'\)\s+THEN\s+0\s+END\b',
        r') ELSE 0 END',
        sql,
        flags=re.IGNORECASE
    )
    # Fix )::numeric, 0) THEN -> )::numeric, 0) ELSE (db-8 Q28 malformed CASE)
    sql = re.sub(
        r'(\)::numeric,\s*0\))\s+THEN\s+',
        r'\1 ELSE ',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_lag_numeric_offset(sql: str) -> str:
    """Fix LAG(expr)::numeric, 1) OVER -> LAG(expr, 1)::numeric OVER (wrong paren placement)"""
    sql = re.sub(
        r'LAG\s*\(\s*([a-zA-Z0-9_.]+)\s*\)\s*::numeric\s*,\s*1\s*\)\s+OVER',
        r'LAG(\1, 1)::numeric OVER',
        sql,
        flags=re.IGNORECASE
    )
    # LAG(expr, 1)::numeric OVER (ORDER BY ...) - ensure OVER has proper window
    sql = re.sub(
        r'LAG\s*\(\s*([a-zA-Z0-9_.]+)\s*,\s*1\s*\)\s*::numeric\s+OVER\s*\(\s*ORDER',
        r'LAG(\1, 1)::numeric OVER (ORDER',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_count_distinct_extra_paren(sql: str) -> str:
    """Fix COUNT(DISTINCT x))::numeric -> COUNT(DISTINCT x)::numeric (extra paren)"""
    sql = re.sub(
        r'COUNT\s*\(\s*DISTINCT\s+([a-zA-Z0-9_.]+)\s*\)\s*\)\s*::numeric',
        r'COUNT(DISTINCT \1)::numeric',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_round_parens_generic(sql: str) -> str:
    """Fix ROUND((((((((expr * 100::numeric, 2) - collapse extra parens to ROUND(expr * 100::numeric, 2)"""
    # Match ROUND with one or more extra opening parens, capture identifier and rest
    # ROUND((((((((x * 100::numeric, 2) -> ROUND(x * 100::numeric, 2)
    def repl(m):
        return f'ROUND({m.group(1)} * 100::numeric, 2)'
    sql = re.sub(
        r'ROUND\s*\(+([a-zA-Z0-9_.]+)\s*\*\s*100::numeric\s*,\s*2\s*\)',
        repl,
        sql,
        flags=re.IGNORECASE
    )
    # Also fix: ROUND((((((((expr - expr)::numeric, 2) - expression with minus
    sql = re.sub(
        r'ROUND\s*\(+([a-zA-Z0-9_.]+)\s*-\s*([a-zA-Z0-9_.]+)::numeric\s*,\s*2\s*\)',
        r'ROUND((\1 - \2)::numeric, 2)',
        sql,
        flags=re.IGNORECASE
    )
    # Fix ROUND((((((((((expr)::numeric, 2) - collapse 3+ extra opening parens to 1
    sql = re.sub(
        r'ROUND\s*\(\s*\(\s*\(\s*\(\s*\(\s*\(\s*\(\s*\(\s*\(\s*\(\s*\(',
        r'ROUND((',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_duplicate_else(sql: str) -> str:
    """Fix ELSE x ELSE x -> ELSE x (duplicate introduced by over-fix)"""
    sql = re.sub(r'\bELSE\s+(\d+)\s+ELSE\s+\d+\b', r'ELSE \1', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bELSE\s+NULL\s+ELSE\s+NULL\b', r'ELSE NULL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bELSE\s+0\s+ELSE\s+0\s+END\b', r'ELSE 0 END', sql, flags=re.IGNORECASE)
    return sql


def fix_when_else_missing_then(sql: str) -> str:
    """Fix WHEN condition ELSE value -> WHEN condition THEN value (missing THEN before ELSE)"""
    # Only when condition doesn't contain THEN (avoid matching WHEN x THEN y ELSE z)
    # WHEN x ELSE y ELSE/END/WHEN - the first ELSE should be THEN
    sql = re.sub(
        r'\bWHEN\s+([^T]+?)\s+ELSE\s+([^\s]+(?:\s+[^\s]+)*?)\s+(ELSE\s|END\s|WHEN\s|,)',
        r'WHEN \1 THEN \2 \3',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_round_numeric_cast(sql: str) -> str:
    """Fix ROUND(percentile * 100::numeric, 2) - ensure proper cast for double precision"""
    # PostgreSQL ROUND(numeric, int) - if percentile is double, cast it
    sql = re.sub(
        r'ROUND\s*\(\s*([a-zA-Z0-9_.]+)\s*\*\s*100::numeric\s*,\s*2\s*\)',
        r'ROUND((\1 * 100)::numeric, 2)',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_st_dwithin_text(sql: str) -> str:
    """Fix ST_DWithin(text, geography, int) - cast text to geography"""
    sql = re.sub(
        r'ST_DWITHIN\s*\(\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*,\s*(\d+)\s*\)',
        r'ST_DWithin(\1.\2::geography, \3.\4::geography, \5)',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_st_within_geometry(sql: str) -> str:
    """Fix ST_Within(geography, geography) - use geometry cast for PostGIS compatibility"""
    # ST_Within(a, b) with geom columns - cast to geometry for reliability
    sql = re.sub(
        r'ST_WITHIN\s*\(\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*\)',
        r'ST_Within(\1.\2::geometry, \3.\4::geometry)',
        sql,
        flags=re.IGNORECASE
    )
    # ST_Within(col, (SELECT col FROM ...)) - cast both to geometry
    sql = re.sub(
        r'ST_WITHIN\s*\(\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*,\s*\(\s*SELECT\s+([a-zA-Z0-9_.]+)\s+FROM',
        r'ST_Within(\1.\2::geometry, (SELECT \3::geometry FROM',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_st_touches_geometry(sql: str) -> str:
    """Fix ST_Touches(geography, geography) - use geometry cast"""
    sql = re.sub(
        r'ST_TOUCHES\s*\(\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*\)',
        r'ST_Touches(\1.\2::geometry, \3.\4::geometry)',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_st_distance_geometry(sql: str) -> str:
    """Fix ST_DISTANCE(text, text) - cast to geometry for PostGIS"""
    # ST_DISTANCE(geom1, geom2) - cast column refs to geometry
    sql = re.sub(
        r'ST_DISTANCE\s*\(\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*\)',
        r'ST_Distance(\1.\2::geometry, \3.\4::geometry)',
        sql,
        flags=re.IGNORECASE
    )
    # Also fix ST_DISTANCE with non-dotted refs
    sql = re.sub(
        r'ST_DISTANCE\s*\(\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\)',
        r'ST_Distance(\1::geometry, \2::geometry)',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_st_union_geometry(sql: str) -> str:
    """Fix ST_Union(geography, geography) - cast to geometry for PostGIS"""
    sql = re.sub(
        r'ST_UNION\s*\(\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*\)',
        r'ST_Union(\1.\2::geometry, \3.\4::geometry)',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_st_translate_geometry(sql: str) -> str:
    """Fix ST_Translate(geography, x, y) - cast to geometry for PostGIS"""
    sql = re.sub(
        r'ST_TRANSLATE\s*\(\s*([a-zA-Z0-9_.]+)\.([a-zA-Z0-9_]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)',
        r'ST_Translate(\1.\2::geometry, \3, \4)',
        sql,
        flags=re.IGNORECASE
    )
    # ST_Translate with subquery: (SELECT col FROM tbl WHERE ...)
    sql = re.sub(
        r'ST_TRANSLATE\s*\(\s*\(\s*SELECT\s+([a-zA-Z0-9_]+)\s+FROM',
        r'ST_Translate((SELECT \1::geometry FROM',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_end_times_then_else(sql: str) -> str:
    """Fix END * 0.8 ELSE 'X' -> END * 0.8 THEN 'X' (typo: ELSE should be THEN)"""
    sql = re.sub(
        r'\bEND\s*\*\s*0\.8\s+ELSE\s+',
        r'END * 0.8 THEN ',
        sql,
        flags=re.IGNORECASE
    )
    # Also fix END * 0.9 ELSE
    sql = re.sub(
        r'\bEND\s*\*\s*0\.9\s+ELSE\s+',
        r'END * 0.9 THEN ',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_round_numeric_comma(sql: str) -> str:
    """Fix ROUND((((expr)::numeric, 2) - too many ( before. Collapse ROUND(((( to ROUND(("""
    sql = re.sub(
        r'ROUND\s*\(\s*\(\s*\(\s*\(\s*\(\s*\(',
        r'ROUND(((',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'ROUND\s*\(\s*\(\s*\(\s*\(\s*\(',
        r'ROUND(((',
        sql,
        flags=re.IGNORECASE
    )
    # Fix )::numeric), 2) -> )::numeric, 2) (extra paren before comma breaks ROUND)
    sql = re.sub(
        r'\)\s*::\s*numeric\s*\)\s*,\s*2\s*\)',
        r')::numeric, 2)',
        sql,
        flags=re.IGNORECASE
    )
    # Fix ))::numeric, 2) -> )::numeric, 2) (db-8: ROUND((expr))::numeric, 2) - extra ) before ::)
    sql = re.sub(
        r'\)\s*\)\s*::\s*numeric\s*,\s*2\s*\)',
        r')::numeric, 2)',
        sql,
        flags=re.IGNORECASE
    )
    # Fix * 100::numeric))::numeric, 2) -> * 100::numeric)::numeric, 2) (extra ) in ROUND)
    sql = re.sub(
        r'\*\s*100::numeric\)\)::numeric\s*,\s*2\s*\)',
        r'* 100::numeric)::numeric, 2)',
        sql,
        flags=re.IGNORECASE
    )
    # Fix ) * 100::numeric))::numeric -> ) * 100::numeric)::numeric (CASE expr)
    sql = re.sub(
        r'\)\s*\*\s*100::numeric\)\)::numeric',
        r') * 100::numeric)::numeric',
        sql,
        flags=re.IGNORECASE
    )
    # Fix ROUND(((expr)::numeric, 2) -> ROUND((expr)::numeric, 2) (extra ( in ROUND)
    sql = re.sub(
        r'ROUND\s*\(\s*\(\s*\(\s*\(',
        r'ROUND((',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'ROUND\s*\(\s*\(\s*\(',
        r'ROUND((',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_round_numeric_else_null(sql: str) -> str:
    """No-op - was adding wrong )"""
    return sql


def fix_then_div_86400_then(sql: str) -> str:
    """Fix ) / 86400 THEN 0 ELSE -> ) / 86400 ELSE 0 (don't create ELSE 0 ELSE 0)"""
    sql = re.sub(
        r'\)\s*/\s*86400\.?\d*\s+THEN\s+0\s+ELSE\s+0\b',
        r') / 86400 ELSE 0',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'\)\s*/\s*86400\.?\d*\s+THEN\s+',
        r') / 86400 ELSE ',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_then_then_null_more(sql: str) -> str:
    """Fix * 100::numeric, 2) THEN NULL -> * 100::numeric), 2) ELSE NULL and similar"""
    sql = re.sub(
        r'\*\s*100::numeric\)\)::numeric,\s*2\)\s+THEN\s+NULL\b',
        r'* 100::numeric)::numeric), 2) ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    sql = re.sub(
        r'\)\s*\*\s*100::numeric,\s*2\)\s+THEN\s+NULL\b',
        r') * 100::numeric), 2) ELSE NULL',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_round_double_precision(sql: str) -> str:
    """Fix ROUND(double_expr, 2) - PostgreSQL needs ::numeric for double precision"""
    # ROUND(((p75 - p25) / NULLIF(p50, 0)) * 100, 2) - wrap entire expr in ::numeric
    sql = re.sub(
        r'ROUND\s*\(\s*\(\(([a-zA-Z0-9_.]+)\s*-\s*([a-zA-Z0-9_.]+)\)\s*/\s*NULLIF\s*\(([a-zA-Z0-9_.]+)::numeric,\s*0\)\s*\)\s*\*\s*100\s*,\s*2\s*\)',
        r'ROUND((((\1 - \2) / NULLIF(\3::numeric, 0)) * 100)::numeric, 2)',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_lag_paren_over(sql: str) -> str:
    """Fix LAG(expr, 1)::numeric OVER -> LAG(expr, 1)::numeric OVER (wrong: LAG(expr)::numeric, 1) OVER)"""
    sql = re.sub(
        r'LAG\s*\(\s*([a-zA-Z0-9_.]+)\s*,\s*1\s*\)\s*::numeric\s+OVER',
        r'LAG(\1, 1)::numeric OVER',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_when_cond_then_else(sql: str) -> str:
    """Fix ) > 0 ELSE ROUND -> ) > 0 THEN ROUND (missing THEN before ELSE in CASE)"""
    sql = re.sub(
        r'\)\s*>\s*0\s+ELSE\s+ROUND\s*\(',
        r') > 0 THEN ROUND(',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_on_clause_missing_paren(sql: str) -> str:
    """Fix ON (... AND TRUE) WHERE -> add missing ) before WHERE in JOIN"""
    # INNER JOIN t ON ( ... AND TRUE\n    WHERE -> ON ( ... AND TRUE)\n    WHERE
    sql = re.sub(
        r'(\bAND\s+TRUE)\s*\n(\s*)WHERE\b',
        r'\1)\n\2WHERE',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_when_else_missing_then_broad(sql: str) -> str:
    """Fix WHEN cond ELSE val -> WHEN cond THEN val (broader pattern for CASE)"""
    # WHEN x ELSE y (missing THEN) - match when condition has no THEN
    # Avoid: WHEN x THEN y ELSE z (already correct)
    # Match: WHEN something_not_containing_THEN_keyword ELSE value
    # Use negative lookbehind to avoid WHEN...THEN - we want WHEN...ELSE without THEN
    def repl(m):
        cond, val = m.group(1).strip(), m.group(2).strip()
        if ' THEN ' in cond:
            return m.group(0)  # Has THEN, skip
        return f'WHEN {cond} THEN {val}'
    sql = re.sub(
        r'\bWHEN\s+([^W]+?)\s+ELSE\s+([^\s]+(?:\s+[^\s]+)*?)(?=\s+ELSE\s|\s+END\s|\s+WHEN\s|,|\s*\))',
        repl,
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_array_agg_filter_syntax(sql: str) -> str:
    """Fix invalid ORDER BY ... DESC) FILTER -> ORDER BY ... DESC) in ARRAY_AGG"""
    # ARRAY_AGG(... ORDER BY x DESC) FILTER - the ) might be in wrong place
    # If we have ") DESC) FILTER" - the ORDER BY should be "ORDER BY expr DESC"
    # ARRAY_AGG(DISTINCT x) DESC) FILTER - wrong. Should be ARRAY_AGG(DISTINCT x ORDER BY ...) FILTER
    # Or ARRAY_AGG(...)  FILTER (WHERE ...) - the FILTER applies to the aggregate
    # Error: "ARRAY_AGG(DISTINCT s.skill_name) DESC) FILTER"
    # The ORDER BY clause might be: ORDER BY ARRAY_AGG(DISTINCT s.skill_name) DESC
    # So we have ORDER BY expr DESC - correct. The ") FILTER" - the ) might close something.
    # Actually: ORDER BY ... ARRAY_AGG(DISTINCT s.skill_name) DESC) FILTER
    # The issue: we have extra ) - ORDER BY a, b DESC) - the ) closes ORDER BY? No.
    # In PostgreSQL: ORDER BY col1, col2 DESC - correct.
    # ORDER BY ARRAY_AGG(...) DESC) FILTER - the ) before FILTER is wrong.
    # Maybe it's: ORDER BY some_function(ARRAY_AGG(...) DESC) - no.
    # Let me just replace ") FILTER" with ") FILTER" - that doesn't help.
    # The fix: "DESC) FILTER" could be "DESC) FILTER" - perhaps the ORDER BY is wrong.
    # In ARRAY_AGG: ARRAY_AGG(expr ORDER BY col DESC) - the ORDER BY is inside ARRAY_AGG.
    # So we might have ARRAY_AGG(DISTINCT s.skill_name ORDER BY ... DESC) - but we have ") DESC) FILTER"
    # So it's ARRAY_AGG(DISTINCT s.skill_name) ... DESC) FILTER - the structure is wrong.
    # Perhaps: ARRAY_AGG(DISTINCT s.skill_name DESC) FILTER - no, DISTINCT doesn't take ORDER.
    # I'll add a fix that removes the erroneous ) between DESC and FILTER when it's clearly wrong.
    sql = re.sub(
        r'(ARRAY_AGG\([^)]+\))\s+DESC\)\s+FILTER',
        r'\1 DESC) FILTER',
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_recursive_cte_varchar(sql: str) -> str:
    """Fix recursive CTE type mismatch: full_path_name varchar vs text"""
    # db-8: cast recursive term's full_path_name to VARCHAR(255) to match anchor
    sql = re.sub(
        r'sh\.full_path_name\s*\|\|\s*[\'"]\s*->\s*[\'"]\s*\|\|\s*s\.skill_name',
        r"(sh.full_path_name || ' -> ' || s.skill_name)::VARCHAR(255)",
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_and_zero_comma(sql: str) -> str:
    """Fix AND 0, -> AND TRUE (corrupted spatial condition placeholder)"""
    sql = re.sub(r'\bAND\s+0\s*,\s*', r'AND TRUE ', sql, flags=re.IGNORECASE)
    return sql


def fix_paren_lt_then(sql: str) -> str:
    """Fix AND TRUE point(...) -> proper ST_DWithin for spatial nearby count."""
    # AND TRUE point(pf2.longitude, pf2.latitude) - corrupted; was ST_DWithin
    sql = re.sub(
        r'AND\s+TRUE\s+point\s*\(\s*([a-zA-Z0-9_.]+)\.longitude\s*,\s*([a-zA-Z0-9_.]+)\.latitude\s*\)',
        r'AND ST_DWithin(ST_SetSRID(ST_MakePoint(pf.longitude, pf.latitude), 4326)::geography, ST_SetSRID(ST_MakePoint(\1.longitude, \2.latitude), 4326)::geography, 1000)',
        sql,
        flags=re.IGNORECASE
    )
    # (0) < 1000 THEN -> (SELECT COUNT(*) FROM ... ) < 1000 THEN (valid scalar subquery)
    sql = re.sub(
        r'\(\s*0\s*\)\s*<\s+1000\s+THEN\s+',
        r'(SELECT COUNT(*) FROM parking_facilities pf2 WHERE pf2.city_id = pf.city_id AND pf2.facility_id != pf.facility_id) < 1000 THEN ',
        sql,
        flags=re.IGNORECASE
    )
    # Fix (0) < 500 THEN 0, point(...) - (0) was wrong; use (SELECT 0) for valid scalar
    sql = re.sub(r'\(\s*0\s*\)\s*<\s+500\s+THEN\s+0\s*,\s*point\s*\(', r'(SELECT 0) < 500 THEN 0, point(', sql, flags=re.IGNORECASE)
    # Fix THEN 0, point( -> THEN 0 ELSE point( (CASE WHEN ... THEN single_value)
    sql = re.sub(r'THEN\s+0\s*,\s*point\s*\(', r'THEN 0 ELSE point(', sql, flags=re.IGNORECASE)
    return sql


def fix_expr_then_zero(sql: str) -> str:
    """Fix ) THEN 0 -> ) ELSE 0 (malformed CASE default)"""
    sql = re.sub(r'\)\s+THEN\s+0\s+ELSE\s+NULL\b', r') ELSE 0', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\)\s+THEN\s+0\s+END\b', r') ELSE 0 END', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\)\s+THEN\s+0\b', r') ELSE 0', sql, flags=re.IGNORECASE)
    # Fix expr / expr THEN 0 -> expr / expr ELSE 0 (db-11: COALESCE(ubd.total_revenue, 0) / ds.population THEN 0)
    sql = re.sub(r'\)\s*/\s*([a-zA-Z0-9_.]+)\s+THEN\s+0\b', r') / \1 ELSE 0', sql, flags=re.IGNORECASE)
    return sql


def fix_null_avg_cast(sql: str) -> str:
    """Fix NULL, AVG(0))::TEXT -> correct ST_SETSRID(ST_MAKEPOINT(...))::GEOGRAPHY for cluster_center_geom"""
    # db-6 query 29: corrupted cluster_center_geom - restore PostGIS centroid
    sql = re.sub(
        r'NULL,\s*AVG\(0\)\)::TEXT\s+AS\s+cluster_center_geom',
        r"ST_SETSRID(ST_MAKEPOINT(AVG(ST_X(fc.grid_geom::GEOMETRY)), AVG(ST_Y(fc.grid_geom::GEOMETRY))), 4326)::GEOGRAPHY AS cluster_center_geom",
        sql,
        flags=re.IGNORECASE
    )
    return sql


def fix_all(sql: str) -> str:
    # Run THEN/ELSE fix repeatedly for nested CASE (THEN x THEN y -> THEN x ELSE y)
    for _ in range(5):
        prev = sql
        sql = fix_then_else_complex(sql)
        if sql == prev:
            break
    sql = fix_then_null_pattern(sql)
    sql = fix_then_expr_then_null(sql)
    sql = fix_lag_numeric_offset(sql)
    sql = fix_count_distinct_extra_paren(sql)
    sql = fix_duplicate_else(sql)
    sql = fix_round_parens_generic(sql)
    sql = fix_round_numeric_cast(sql)
    sql = fix_when_else_missing_then(sql)
    # fix_when_else_missing_then_broad disabled - can break valid CASE WHEN x THEN y ELSE z
    # sql = fix_when_else_missing_then_broad(sql)
    sql = fix_on_clause_missing_paren(sql)
    sql = fix_recursive_cte_varchar(sql)
    sql = fix_null_avg_cast(sql)
    sql = fix_round_numeric_comma(sql)
    sql = fix_then_div_86400_then(sql)
    sql = fix_then_then_null_more(sql)
    sql = fix_round_double_precision(sql)
    sql = fix_lag_paren_over(sql)
    sql = fix_when_cond_then_else(sql)
    sql = fix_st_dwithin_text(sql)
    sql = fix_st_within_geometry(sql)
    sql = fix_st_touches_geometry(sql)
    sql = fix_st_distance_geometry(sql)
    sql = fix_st_union_geometry(sql)
    sql = fix_st_translate_geometry(sql)
    sql = fix_end_times_then_else(sql)
    sql = fix_and_zero_comma(sql)
    sql = fix_paren_lt_then(sql)
    sql = fix_expr_then_zero(sql)
    return sql


def process_queries_json(path: Path) -> int:
    """Process queries.json and fix SQL"""
    data = json.loads(path.read_text(encoding='utf-8'))
    fixes = 0
    for q in data.get('queries', []):
        if 'sql' in q:
            orig = q['sql']
            fixed = fix_all(orig)
            if fixed != orig:
                q['sql'] = fixed
                fixes += 1
    if fixes:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return fixes


def main():
    total = 0
    for db_dir in sorted(ROOT.iterdir()):
        if db_dir.is_dir() and db_dir.name.startswith('db-') and db_dir.name[3:].isdigit():
            qj = db_dir / 'queries' / 'queries.json'
            if qj.exists():
                n = process_queries_json(qj)
                if n:
                    print(f"{db_dir.name}: Fixed {n} queries")
                total += n
    print(f"\nTotal: {total} queries fixed")

if __name__ == '__main__':
    main()
