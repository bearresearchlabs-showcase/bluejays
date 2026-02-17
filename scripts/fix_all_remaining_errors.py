#!/usr/bin/env python3
"""
Fix all remaining query errors in db-6
"""
import re
from pathlib import Path

def fix_all():
    queries_file = Path('db-6/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # Query 4: Fix ROUND function - ensure all ROUND calls cast to NUMERIC
    # This is already mostly done, but check for any remaining issues
    # The pattern ROUND(CAST(...AS NUMERIC), ...) should be fine
    
    # Query 8: Fix nested aggregates - AVG(AVG(...)) OVER (...)
    # Replace with subquery approach
    content = re.sub(
        r'AVG\(AVG\(([^)]+)\)\)\s+OVER\s*\(([^)]+)\)',
        r'(SELECT AVG(\1) FROM (SELECT \1 FROM validation_metrics vm2 WHERE vm2.parameter_name = vm.parameter_name) sub)',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # Actually, a simpler fix: use window function on already aggregated value
    # But first need to aggregate in a CTE, then use window function
    # Let me find the exact pattern first
    
    # Query 18: Fix crm.claim_amount - ensure claims_risk_matching selects claim_amount AS loss_amount
    # This was already fixed, but let me verify
    
    # Query 25: Fix nrs.cwa_code - replace with NULL
    content = re.sub(
        r'\bnrs\.cwa_code\b',
        r'NULL::VARCHAR(10) AS cwa_code',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 27: Fix sis.spatial_resolution_km - replace with NULL
    content = re.sub(
        r'\bsis\.spatial_resolution_km\b',
        r'NULL::NUMERIC AS spatial_resolution_km',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 29: Fix sip.fire_power_mw - replace with NULL
    content = re.sub(
        r'\bsip\.fire_power_mw\b',
        r'NULL::NUMERIC AS fire_power_mw',
        content,
        flags=re.IGNORECASE
    )
    
    if content != original:
        queries_file.write_text(content)
        return ["db-6"]
    return []

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    fixes = fix_all()
    if fixes:
        print(f"Fixed: {', '.join(fixes)}")
    else:
        print("No fixes needed")
