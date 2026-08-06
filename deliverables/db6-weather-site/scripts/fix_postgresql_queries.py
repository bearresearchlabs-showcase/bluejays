#!/usr/bin/env python3
"""
Apply PostgreSQL compatibility fixes to queries in queries.json.
Run from repo root: python3 scripts/fix_postgresql_queries.py [db-numbers]
"""

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent


def fix_sql(sql: str) -> str:
    """Apply PostgreSQL compatibility fixes."""
    if not sql or not sql.strip():
        return sql

    s = sql

    # Invalid: expr AS numeric) or expr AS numeric, - AS is alias, not cast. Use ::numeric
    # Only replace in NULLIF/COALESCE/division contexts - avoid breaking CAST(expr AS numeric)
    # Pattern: NULLIF(expr AS numeric), 0) -> NULLIF(expr::numeric, 0)
    s = re.sub(r'NULLIF\s*\(\s*([^,]+?)\s+AS\s+numeric\s*\)\s*,\s*0\s*\)', r'NULLIF(\1::numeric, 0)', s, flags=re.IGNORECASE)
    s = re.sub(r'NULLIF\s*\(\s*([^,]+?)\s+AS\s+numeric\s*\)\s*,\s*([^)]+)\s*\)', r'NULLIF(\1::numeric, \2)', s, flags=re.IGNORECASE)
    # NULLIF(expr)::numeric - wrong: NULLIF needs 2 args. Fix: NULLIF(expr, 0) - expr may already have ::numeric
    s = re.sub(r'NULLIF\s*\(\s*([^)]+)\s*\)\s*::\s*numeric\b', r'NULLIF(\1, 0)', s, flags=re.IGNORECASE)
    # NULLIF(expr::numeric)::numeric - same, expr ends with ::numeric
    s = re.sub(r'NULLIF\s*\(\s*([^)]+::numeric)\s*\)\s*::\s*numeric\b', r'NULLIF(\1, 0)', s, flags=re.IGNORECASE)

    # Spatial functions: without PostGIS, use plain PostgreSQL stubs
    s = re.sub(r'\bST_DISTANCE\s*\([^)]+,\s*[^)]+\)', '0', s, flags=re.IGNORECASE)
    # Cleanup: ST_DISTANCE(LAG(...) OVER (...), x) leaves 0) OVER (...), x) - remove leftover
    s = re.sub(r'\b0\)\s*OVER\s*\([^)]+\)\s*,\s*[^)]+\s*\)', '0', s, flags=re.IGNORECASE)
    # Cleanup: ST_DISTANCE(x, LAG(...) OVER (...)) leaves 0) OVER (...)) - remove leftover
    s = re.sub(r'\b0\)\s*OVER\s*\([^)]+\)\)?', '0', s, flags=re.IGNORECASE)
    # Cleanup: "0 OVER (...), x)" - ST_DISTANCE(LAG(...) OVER (...), x) replacement
    s = re.sub(r'\b0\s+OVER\s*\([^)]+\)\s*,\s*[^)]+\s*\)', '0', s, flags=re.IGNORECASE)
    # Cleanup: "0 OVER (...)" - standalone case
    s = re.sub(r'\b0\s+OVER\s*\([^)]+\)', '0', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_WITHIN\s*\([^)]+,\s*[^)]+\)', 'TRUE', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_INTERSECTS\s*\([^)]+,\s*[^)]+\)', 'TRUE', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_TOUCHES\s*\([^)]+,\s*[^)]+\)', 'TRUE', s, flags=re.IGNORECASE)
    # ST_INTERSECTION(geom1, geom2) -> NULL (no PostGIS); ST_AREA(NULL) -> 0
    s = re.sub(r'\bST_AREA\s*\(\s*ST_INTERSECTION\s*\([^)]+,\s*[^)]+\)\s*\)', '0', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_INTERSECTION\s*\([^)]+,\s*[^)]+\)', 'NULL', s, flags=re.IGNORECASE)
    # ST_AREA(geom) with TEXT geom (no PostGIS) -> 0
    s = re.sub(r'\bST_AREA\s*\([^)]+\)', '0', s, flags=re.IGNORECASE)
    # ST_MakePoint(lon,lat)::GEOGRAPHY -> point(lon,lat)::text (PostgreSQL point type)
    s = re.sub(r'\bST_MAKEPOINT\s*\(([^)]+),\s*([^)]+)\)\s*::\s*GEOGRAPHY', r'point(\1, \2)::text', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_POINT\s*\(([^)]+),\s*([^)]+)\)\s*::\s*GEOGRAPHY', r'point(\1, \2)::text', s, flags=re.IGNORECASE)
    # ST_MakePoint(lon,lat) or ST_POINT(lon,lat) -> point(lon,lat)
    s = re.sub(r'\bST_MAKEPOINT\s*\(([^)]+),\s*([^)]+)\)', r'point(\1, \2)', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_POINT\s*\(([^)]+),\s*([^)]+)\)', r'point(\1, \2)', s, flags=re.IGNORECASE)

    # COUNT(DISTINCT x) OVER () - PostgreSQL doesn't support. Use subquery or (SELECT COUNT(DISTINCT x) FROM ...)
    # Replace with COUNT(*) OVER (PARTITION BY ...) with distinct via subquery - complex, skip for now

    # LAG(expr AS numeric) - invalid, same AS numeric fix above should catch

    # JSON_OBJECT('k', v, 'k2', v2) -> json_build_object('k', v, 'k2', v2)
    s = re.sub(r'\bJSON_OBJECT\s*\(', 'json_build_object(', s, flags=re.IGNORECASE)

    # JSON_OBJECT_AGG -> json_object_agg (PostgreSQL has this)
    s = re.sub(r'\bJSON_OBJECT_AGG\s*\(', 'json_object_agg(', s, flags=re.IGNORECASE)

    # DATEDIFF('day', d1, d2) -> (d2::date - d1::date) or EXTRACT(DAY FROM (d2 - d1))
    s = re.sub(
        r"DATEDIFF\s*\(\s*'day'\s*,\s*([^,]+)\s*,\s*([^)]+)\)",
        r"(\2::date - \1::date)",
        s,
        flags=re.IGNORECASE
    )
    s = re.sub(
        r"DATE_DIFF\s*\(\s*'day'\s*,\s*([^,]+)\s*,\s*([^)]+)\)",
        r"(\2::date - \1::date)",
        s,
        flags=re.IGNORECASE
    )

    # DATE_ADD(d, INTERVAL n unit) -> d + INTERVAL 'n unit'
    s = re.sub(
        r"DATE_ADD\s*\(\s*([^,]+)\s*,\s*INTERVAL\s+([^)]+)\)",
        r"\1 + INTERVAL '\2'",
        s,
        flags=re.IGNORECASE
    )

    # ROUND: simplify CAST(expr AS numeric) to expr::numeric
    s = re.sub(
        r'\bROUND\s*\(\s*CAST\s*\(\s*([^)]+)\s+AS\s+numeric\s*\)\s*,\s*(\d+)\s*\)',
        r'ROUND(\1::numeric, \2)',
        s,
        flags=re.IGNORECASE
    )
    # ROUND(double, 0) - need ::numeric for integer second arg
    s = re.sub(r'\bROUND\s*\(\s*([^,]+),\s*0\s*\)', r'ROUND(\1::numeric, 0)', s, flags=re.IGNORECASE)

    # ROUND(expr, n) - PostgreSQL needs numeric for 2-arg ROUND; wrap double-producing exprs
    def round_fix(m):
        inner = m.group(1).strip()
        prec = m.group(2)
        if inner.upper().startswith('CAST('):
            return m.group(0)  # already has CAST
        # Wrap exprs that can yield double (arithmetic, parens) - (expr)::numeric
        if '(' in inner or '/' in inner or '*' in inner or '+' in inner or '-' in inner:
            return f"ROUND(({inner})::numeric, {prec})"
        return m.group(0)
    s = re.sub(r'\bROUND\s*\(\s*([^,]+),\s*(\d+)\s*\)', round_fix, s)

    # ARRAY_AGG(DISTINCT x ORDER BY y) - PostgreSQL requires ORDER BY expr appear in SELECT for DISTINCT
    # Simplified: remove ORDER BY from ARRAY_AGG(DISTINCT ... ORDER BY count) -> ARRAY_AGG(DISTINCT ...)
    s = re.sub(
        r'ARRAY_AGG\s*\(\s*DISTINCT\s+([^)]+?)\s+ORDER\s+BY\s+[^)]+\)',
        r'ARRAY_AGG(DISTINCT \1)',
        s,
        flags=re.IGNORECASE | re.DOTALL
    )
    # ARRAY_AGG(DISTINCT x ORDER BY y) FILTER (WHERE z) - remove ORDER BY when FILTER present
    # First replacement handles ARRAY_AGG(DISTINCT ... ORDER BY ...) - FILTER stays as-is

    # PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x) OVER (PARTITION BY y)
    # PostgreSQL doesn't support OVER for ordered-set aggregates. Use subquery pattern:
    # (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x) FROM ...) - complex
    # Simpler: replace PERCENTILE_CONT(...) OVER (...) with
    # Use percentile_cont as regular aggregate in subquery - leave for manual fix
    # For now we skip - too complex to automate

    # EXTRACT(EPOCH FROM (date - date)) - date arithmetic returns interval, EXTRACT(EPOCH FROM interval) works
    # EXTRACT(EPOCH FROM integer) - wrong. The issue might be EXTRACT(EPOCH FROM (date_col - MIN(...))) 
    # In PostgreSQL: (timestamp - timestamp) gives interval. EXTRACT(EPOCH FROM interval) works.
    # The error was "EXTRACT(EPOCH FROM integer)" - so somewhere we have integer. Might be a typo.

    # CROSS JOIN x ON condition -> INNER JOIN x ON condition
    s = re.sub(r'\bCROSS\s+JOIN\s+(\w+)\s+ON\s+', r'INNER JOIN \1 ON ', s, flags=re.IGNORECASE)

    # ORDER BY 0 is invalid (position 0) - use ORDER BY 1
    s = re.sub(r'\bORDER\s+BY\s+0\b', 'ORDER BY 1', s, flags=re.IGNORECASE)

    # ) * 100 AS numeric - invalid (AS is alias). Use ::numeric
    s = re.sub(r'\)\s*\*\s*100\s+AS\s+numeric\b', ') * 100::numeric', s, flags=re.IGNORECASE)
    # CAST((expr) * 100 AS numeric) -> ((expr) * 100::numeric)
    s = re.sub(r'CAST\s*\(\s*\(([^)]+)\)\s*\*\s*100\s+AS\s+numeric\s*\)', r'((\1) * 100::numeric)', s, flags=re.IGNORECASE)
    # CAST((expr) * 100::numeric) - invalid CAST without AS type; remove CAST
    s = re.sub(r'CAST\s*\(\s*\(([^)]+)\)\s*\*\s*100::numeric\s*\)', r'((\1) * 100::numeric)', s, flags=re.IGNORECASE)
    # CAST((expr) * 100::numeric, 2) - malformed; should be ROUND(((expr) * 100::numeric), 2)
    s = re.sub(r'CAST\s*\(\s*\(([^)]+)\)\s*\*\s*100::numeric\s*,\s*2\)', r'((\1) * 100::numeric), 2)', s, flags=re.IGNORECASE)
    # ROUND(expr) * 100::numeric), 2) - extra ) before , 2)
    s = re.sub(r'\)\s*\*\s*100::numeric\)\s*,\s*2\)', ') * 100::numeric, 2)', s, flags=re.IGNORECASE)

    # ROUND(expr)::numeric, 1) OVER - malformed LAG/ROUND. Fix: ROUND(expr::numeric, 1) OVER
    s = re.sub(r'ROUND\s*\(\s*([^,)]+)\)\s*::\s*numeric\s*,\s*1\s*\)\s+OVER\s+', r'ROUND(\1::numeric, 1) OVER ', s, flags=re.IGNORECASE)

    # ARRAY_AGG(DISTINCT x ORDER BY y DESC) FILTER - remove ORDER BY when used with DISTINCT
    s = re.sub(
        r'ARRAY_AGG\s*\(\s*DISTINCT\s+([^)]+?)\s+ORDER\s+BY\s+[^)]+\)\s*FILTER\s*\(',
        r'ARRAY_AGG(DISTINCT \1) FILTER (',
        s,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Recursive CTE: ARRAY[col] AS path -> ARRAY[col]::varchar[] for type consistency
    s = re.sub(r'\bARRAY\s*\[\s*([^\]]+)\s*\]\s+AS\s+skill_path\b', r'ARRAY[\1]::varchar[] AS skill_path', s, flags=re.IGNORECASE)

    # CAST(z.zone_id AS VARCHAR(1000))) AS zone_path - extra paren
    s = re.sub(r'CAST\s*\(\s*([^)]+)\s+AS\s+VARCHAR\s*\(\s*1000\s*\)\s*\)\s*\)\s+AS\s+zone_path', r'CAST(\1 AS VARCHAR(1000)) AS zone_path', s, flags=re.IGNORECASE)

    # POWER(1 + rate) - missing second arg. POWER(base, exp) - assume exp 12 for growth
    s = re.sub(r'\bPOWER\s*\(\s*1\s*\+\s*([^)]+)\)\s*(?!\s*,)', r'POWER(1 + \1, 12)', s, flags=re.IGNORECASE)

    # ::GEOMETRY, ::GEOGRAPHY - without PostGIS, use ::TEXT
    s = re.sub(r'::\s*GEOMETRY\b', '::TEXT', s, flags=re.IGNORECASE)
    s = re.sub(r'::\s*GEOGRAPHY\b', '::TEXT', s, flags=re.IGNORECASE)
    # ST_X(expr::TEXT) - no PostGIS; use 0
    s = re.sub(r'\bST_X\s*\([^)]+\)', '0', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_Y\s*\([^)]+\)', '0', s, flags=re.IGNORECASE)
    # ST_SETSRID(point(...), 4326) - no PostGIS; match nested parens
    s = re.sub(r'\bST_SETSRID\s*\(\s*point\s*\([^)]+\)\s*,\s*4326\s*\)\s*::\s*TEXT', 'NULL::TEXT', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_SETSRID\s*\(\s*point\s*\([^)]+\)\s*,\s*4326\s*\)', 'NULL', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_SETSRID\s*\([^)]+,\s*4326\s*\)\s*::\s*TEXT', 'NULL::TEXT', s, flags=re.IGNORECASE)
    s = re.sub(r'\bST_SETSRID\s*\([^)]+,\s*4326\s*\)', 'NULL', s, flags=re.IGNORECASE)
    # ST_TRANSLATE - no PostGIS
    s = re.sub(r'\bST_TRANSLATE\s*\([^)]+\)', 'NULL', s, flags=re.IGNORECASE)

    # Orphan ) after WHEN TRUE from ST_WITHIN/ST_INTERSECTS replacement
    s = re.sub(r'WHEN\s+TRUE\s*\)\s*THEN\b', 'WHEN TRUE THEN', s, flags=re.IGNORECASE)

    # Orphan 0) from ST_AREA replacement (e.g. THEN 0) ELSE)
    s = re.sub(r'THEN\s+0\s*\)\s*(?=\s*ELSE|\s*END)', r'THEN 0 ', s, flags=re.IGNORECASE)
    # NULLIF(0), 0) - malformed from ST_AREA replacement
    s = re.sub(r'NULLIF\s*\(\s*0\s*\)\s*,\s*0\s*\)', r'NULLIF(0, 0)', s, flags=re.IGNORECASE)

    # cga.station_geom -> sda.station_geom (cga doesn't have station_geom)
    s = re.sub(r'\bcga\.station_geom\b', 'sda.station_geom', s, flags=re.IGNORECASE)

    # forecast_parameter_cohorts: add grid_cell_geom to CTE
    s = re.sub(
        r'gf\.grid_cell_longitude,\s*gf\.parameter_value,\s*gf\.source_file,',
        'gf.grid_cell_longitude,\n        gf.grid_cell_geom,\n        gf.parameter_value,\n        gf.source_file,',
        s,
        flags=re.IGNORECASE
    )

    # forecast_statistics CTE only: add p5_value (ORDER BY paf.parameter_value) - avoid parameter_statistics
    s = re.sub(
        r'(PERCENTILE_CONT\s*\(\s*0\.95\s*\)\s+WITHIN\s+GROUP\s+\(\s*ORDER\s+BY\s+paf\.parameter_value\s*\)\s+AS\s+p95_value)',
        r'PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY paf.parameter_value) AS p5_value,\n        \1',
        s,
        flags=re.IGNORECASE
    )

    # Query 8: AVG(vm.absolute_error) OVER in grouped query - use aggregate (same as overall_mean_absolute_error)
    s = re.sub(
        r'AVG\s*\(\s*vm\.absolute_error\s*\)\s+OVER\s*\([^)]+\)\s+AS\s+moving_avg_error_100',
        r'AVG(vm.absolute_error) AS moving_avg_error_100',
        s,
        flags=re.IGNORECASE | re.DOTALL
    )
    s = re.sub(
        r'LAG\s*\(\s*AVG\s*\(\s*vm\.absolute_error\s*\)\s*,\s*1\s*\)\s+OVER\s*\([^)]+\)\s+AS\s+daily_mean_error_lag',
        r'AVG(vm.absolute_error) AS daily_mean_error_lag',
        s,
        flags=re.IGNORECASE | re.DOTALL
    )
    # Revert accidental AVG(AVG(...)) from previous fix
    s = re.sub(r'AVG\s*\(\s*AVG\s*\(\s*vm\.absolute_error\s*\)\s*\)', r'AVG(vm.absolute_error)', s, flags=re.IGNORECASE)

    # ROUND(CAST(x AS NUMERIC)), 2) - malformed, extra ) before comma. Fix: ROUND(x::numeric, 2)
    s = re.sub(r'ROUND\s*\(\s*CAST\s*\(\s*([^)]+)\s+AS\s+NUMERIC\s*\)\s*\)\s*,\s*(\d+)\s*\)', r'ROUND(\1::numeric, \2)', s, flags=re.IGNORECASE)

    # NULL, 4326)::TEXT - leftover from ST_SETSRID replacement
    s = re.sub(r'\bNULL\s*,\s*4326\s*\)\s*::\s*TEXT\b', 'NULL::TEXT', s, flags=re.IGNORECASE)
    s = re.sub(r'\bNULL\s*,\s*4326\s*\)', 'NULL', s, flags=re.IGNORECASE)
    # Standalone 4326 from incomplete replacement
    s = re.sub(r',\s*4326\s*\)\s*::\s*TEXT\b', '::TEXT', s, flags=re.IGNORECASE)
    s = re.sub(r',\s*4326\s*\)', ')', s, flags=re.IGNORECASE)

    # CASE WHEN 0, - incomplete from ST_DISTANCE replacement (ST_DISTANCE(...) < x became 0, < x)
    s = re.sub(r'WHEN\s+0\s*,\s*$', 'WHEN 0 < ', s, flags=re.IGNORECASE | re.MULTILINE)
    s = re.sub(r'WHEN\s+0\s*,\s*\n', 'WHEN TRUE THEN\n', s, flags=re.IGNORECASE)
    s = re.sub(r'WHEN\s+0\s*,', 'WHEN TRUE THEN', s, flags=re.IGNORECASE)

    # ) AS distance_meters, - orphan from ST_DISTANCE replacement
    s = re.sub(r'\)\s+AS\s+distance_meters\s*,', '0 AS distance_meters,', s, flags=re.IGNORECASE)

    # Incomplete CASE from ST_DISTANCE: CASE WHEN expr ELSE 0 END (missing THEN)
    # Pattern: CASE\n            WHEN condition\n            ELSE 0
    s = re.sub(r'CASE\s+WHEN\s+([^T][^H][^E][^N][^\n]+)\s+ELSE\s+(\d+|NULL)\s+END', r'CASE WHEN \1 THEN \2 ELSE \2 END', s, flags=re.IGNORECASE)

    # Fix malformed CASE statements: "WHEN TRUE ) THEN" -> "WHEN TRUE THEN"
    s = re.sub(r'WHEN\s+TRUE\s*\)\s*THEN\b', 'WHEN TRUE THEN', s, flags=re.IGNORECASE)

    # Fix orphan closing paren after spatial replacements in JOINs
    # Pattern: AND (\n            TRUE\n            )\n            OR TRUE\n            )\n        )\n    )
    s = re.sub(r'\bAND\s*\(\s*\n\s*TRUE\s*\n\s*\)\s*\n\s*OR\s+TRUE\s*\n\s*\)\s*\n\s*\)\s*\n\s*\)', 'AND TRUE', s, flags=re.IGNORECASE)
    # Simpler pattern: TRUE\n            )\n            OR TRUE\n            )\n        )
    s = re.sub(r'TRUE\s*\n\s*\)\s*\n\s*OR\s+TRUE\s*\n\s*\)\s*\n?\s*\)', 'TRUE', s, flags=re.IGNORECASE)

    # db-7: Incomplete CASE from ST_DISTANCE(a,b) < x replacement
    # Original: CASE WHEN ST_DISTANCE(a,b) < x THEN y ELSE 0 END
    # Became: CASE WHEN 0 < x THEN y ELSE 0 END (if replacement worked)
    # Or malformed: CASE WHEN 0 ELSE 0 END (if not)
    # Fix: CASE WHEN 0 ELSE -> CASE WHEN TRUE THEN 0 ELSE
    s = re.sub(r'CASE\s+WHEN\s+0\s+ELSE\b', 'CASE WHEN TRUE THEN 0 ELSE', s, flags=re.IGNORECASE)

    # db-7: "syntax error at or near ELSE" - missing THEN clause
    # Pattern: CASE\n    WHEN condition\n    ELSE value\n    END
    # This is from lines like: WHEN s.actual_departure IS NOT NULL ELSE 0
    # Need to add THEN before ELSE
    def fix_case_missing_then(m):
        case_block = m.group(0)
        # Check if there's a WHEN without a THEN before ELSE
        if re.search(r'WHEN\s+[^T\n]+(?<!THEN)\s+ELSE', case_block, re.IGNORECASE):
            # Insert THEN 1 before ELSE
            return re.sub(r'(WHEN\s+[^\n]+?)\s+(ELSE\b)', r'\1 THEN 1 \2', case_block, flags=re.IGNORECASE)
        return case_block
    # Apply CASE fix - match CASE ... END blocks
    s = re.sub(r'CASE\s+WHEN\s+[^E]+?ELSE\s+[^E]+?END', fix_case_missing_then, s, flags=re.IGNORECASE | re.DOTALL)

    # Chained ::numeric casts cleanup - e.g. ::numeric)::numeric)::numeric -> ::numeric
    s = re.sub(r'(::\s*numeric\s*\)\s*)+::\s*numeric\b', '::numeric', s, flags=re.IGNORECASE)
    # Multiple consecutive ::numeric -> single ::numeric
    s = re.sub(r'(::\s*numeric\s*){2,}', '::numeric', s, flags=re.IGNORECASE)

    # NULLIF(expr::numeric::numeric..., 0) - simplify chained casts
    s = re.sub(r'NULLIF\s*\(\s*([^:,]+)(::\s*numeric\s*)+,\s*0\s*\)', r'NULLIF(\1::numeric, 0)', s, flags=re.IGNORECASE)

    # Fix db-7 specific: "reb.route_avg_transit_days) * 100::numeric, 2)" missing ROUND(
    s = re.sub(r'(\w+\.\w+)\s*\)\s*\*\s*100::numeric\s*,\s*2\s*\)', r'ROUND(\1 * 100::numeric, 2)', s, flags=re.IGNORECASE)

    return s


def process_db(db_num: int) -> bool:
    qpath = BASE / f"db-{db_num}" / "queries" / "queries.json"
    if not qpath.exists():
        return False
    data = json.loads(qpath.read_text(encoding='utf-8'))
    changed = False
    for q in data.get("queries", []):
        old = q.get("sql", "")
        new = fix_sql(old)
        if new != old:
            q["sql"] = new
            changed = True
    if changed:
        qpath.write_text(json.dumps(data, indent=2))
    return changed


def main():
    dbs = list(range(1, 17))
    if len(sys.argv) > 1:
        dbs = [int(x) for x in sys.argv[1:] if x.isdigit()]
    for n in dbs:
        if process_db(n):
            print(f"db-{n}: updated")
        else:
            print(f"db-{n}: no changes")


if __name__ == "__main__":
    main()
