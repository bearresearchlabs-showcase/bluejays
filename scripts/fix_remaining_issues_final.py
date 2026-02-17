#!/usr/bin/env python3
"""
Fix remaining issues in db-6 and db-15
"""
import re
from pathlib import Path

def fix_all():
    fixes = []
    
    # Fix db-15
    queries_file = Path('db-15/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # Fix Query 8 - npva.year -> npva.year_num
    content = re.sub(
        r'\bnpva\.year\b',
        r'npva.year_num',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 14 - sec.annual_savings -> rae.annual_savings (sec not in scope)
    # In final_economics_analysis CTE, it selects from rebate_adjusted_economics rae
    # but references sec.annual_savings which is not in scope
    content = re.sub(
        r'ROUND\(CAST\(sec\.annual_savings AS NUMERIC\), 2\) AS annual_savings,',
        r'ROUND(CAST(rae.annual_savings AS NUMERIC), 2) AS annual_savings,',
        content,
        flags=re.IGNORECASE
    )
    content = re.sub(
        r'ROUND\(CAST\(sec\.payback_period_years AS NUMERIC\), 2\) AS payback_period_years,',
        r'ROUND(CAST(rae.payback_period_years AS NUMERIC), 2) AS payback_period_years,',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 7 - GROUP BY issue with rc.rate_code_id
    # Need to check if rc.rate_code_id is in SELECT but not in GROUP BY
    # This requires more context, so we'll handle it separately
    
    # Fix Query 12 - gra.utility_id -> er.utility_id (already done, but check for remaining)
    
    if content != original:
        queries_file.write_text(content)
        fixes.append("db-15")
    
    # Fix db-6 Query 2 - recursive CTE type mismatch
    queries_file = Path('db-6/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # The error says column 8 has type mismatch
    # Column 8 is coverage_percentage (0-indexed 7th)
    # Anchor has: ST_AREA(sb2.boundary_geom) / NULLIF(ST_AREA(sb1.boundary_geom), 0) * 100
    # Recursive has: bsh.coverage_percentage (which should match)
    # The issue might be that the anchor returns NUMERIC but recursive expects something else
    # Or vice versa. Let me ensure explicit casting
    
    # Fix Query 9 - ST_UNION already fixed, but ensure it's correct
    
    if content != original:
        queries_file.write_text(content)
        fixes.append("db-6")
    
    return fixes

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    fixes = fix_all()
    if fixes:
        print(f"Fixed: {', '.join(fixes)}")
    else:
        print("No fixes needed")
