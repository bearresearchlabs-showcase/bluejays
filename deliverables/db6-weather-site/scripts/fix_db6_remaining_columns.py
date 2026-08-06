#!/usr/bin/env python3
"""
Fix remaining db-6 column reference errors
"""
import re
from pathlib import Path

def fix_all():
    queries_file = Path('db-6/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # Query 25: Fix nrs.site_latitude -> nrs.latitude
    content = re.sub(
        r'\bnrs\.site_latitude\b',
        r'nrs.latitude',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 25: Fix nrs.site_longitude -> nrs.longitude (if exists)
    content = re.sub(
        r'\bnrs\.site_longitude\b',
        r'nrs.longitude',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 27, 29: Fix sis.satellite_name -> sis.source_name
    content = re.sub(
        r'\bsis\.satellite_name\b',
        r'sis.source_name',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 27, 29, 30: Fix sip.grid_latitude - satellite_imagery_products doesn't have grid_latitude
    # Need to extract from grid_geom or use NULL
    # Actually, let me check if we can use ST_X/ST_Y on geography
    # For now, use NULL or extract from geometry
    content = re.sub(
        r'\bsip\.grid_latitude\b',
        r'ST_Y(sip.grid_geom::geometry) AS grid_latitude',
        content,
        flags=re.IGNORECASE
    )
    
    content = re.sub(
        r'\bsip\.grid_longitude\b',
        r'ST_X(sip.grid_geom::geometry) AS grid_longitude',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 1: Fix missing FROM-clause entry for table "ac"
    # Need to check what "ac" refers to - likely an alias issue
    
    # Query 3, 5: Fix "in an aggregate with DISTINCT, ORDER BY expressions must appear"
    # This is a PostgreSQL-specific issue with DISTINCT and ORDER BY
    
    # Query 4: Fix "function round(double precision, integer) does not exist"
    # PostgreSQL requires CAST to NUMERIC for ROUND
    content = re.sub(
        r'ROUND\(([^,]+),\s*(\d+)\)',
        r'ROUND(CAST(\1 AS NUMERIC), \2)',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 6, 9: Fix missing FROM-clause entry for table "c"
    # Need to check what "c" refers to
    
    # Query 8: Fix "aggregate function calls cannot be nested"
    # PostgreSQL doesn't allow AVG(AVG(...)) - need to use subquery
    
    # Query 11: Fix syntax error at or near "("
    # Need to check the specific syntax issue
    
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
