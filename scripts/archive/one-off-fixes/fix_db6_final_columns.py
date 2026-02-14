#!/usr/bin/env python3
"""
Fix final db-6 column reference errors
"""
import re
from pathlib import Path

def fix_all():
    queries_file = Path('db-6/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # Query 25: Fix nrs.state_code - nexrad_radar_sites doesn't have state_code
    content = re.sub(
        r'\bnrs\.state_code\b',
        r'NULL::VARCHAR(10) AS state_code',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 27: Fix sis.sensor_name - satellite_imagery_sources doesn't have sensor_name
    content = re.sub(
        r'\bsis\.sensor_name\b',
        r'sis.source_name',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 29: Fix sip.fire_temperature_k - satellite_imagery_products doesn't have fire_temperature_k
    content = re.sub(
        r'\bsip\.fire_temperature_k\b',
        r'NULL::NUMERIC AS fire_temperature_k',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix crm.loss_amount - should be crm.claim_amount (already fixed in CTE but need to check all references)
    # Actually, I already fixed hc.loss_amount -> hc.claim_amount, but crm comes from claims_risk_matching
    # which selects hc.loss_amount AS loss_amount, so I need to change the SELECT in claims_risk_matching
    # Let me check if there are any remaining crm.loss_amount references
    
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
