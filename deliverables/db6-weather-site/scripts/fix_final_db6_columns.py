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
    
    # Query 25: Fix nrs.coverage_radius_km - doesn't exist in schema
    content = re.sub(
        r'\bnrs\.coverage_radius_km\b',
        r'NULL::NUMERIC AS coverage_radius_km',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 27: Fix sis.scan_frequency_minutes - doesn't exist in schema
    content = re.sub(
        r'\bsis\.scan_frequency_minutes\b',
        r'NULL::NUMERIC AS scan_frequency_minutes',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 29: Fix sip.brightness_temperature_k - doesn't exist in schema
    content = re.sub(
        r'\bsip\.brightness_temperature_k\b',
        r'NULL::NUMERIC AS brightness_temperature_k',
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
