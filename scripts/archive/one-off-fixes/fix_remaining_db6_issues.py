#!/usr/bin/env python3
"""
Fix remaining issues in db-6 queries.md
"""
import re
from pathlib import Path

def fix_db6_queries():
    queries_file = Path('db-6/queries/queries.md')
    content = queries_file.read_text()
    original_content = content
    
    # Fix 1: Query 1 - Ensure all ST_DISTANCE calls use ::geography casts
    # The error says geography, numeric - need to ensure both args are geography
    content = re.sub(
        r'ST_DISTANCE\s*\(\s*sb\.boundary_geom\s*::\s*geography\s*,\s*fpc\.grid_cell_latitude',
        r'ST_DISTANCE(sb.boundary_geom::geography, fpc.grid_cell_geom::geography',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 2: Query 2 - Fix double geometry casts and ensure ST_Within uses geometry
    # Remove double casts
    content = re.sub(
        r'::geometry::geometry',
        r'::geometry',
        content
    )
    
    # Fix 3: Query 5 - Fix cga.station_geom references (should be sda.station_geom)
    content = re.sub(
        r'\bcga\.station_geom\b',
        r'sda.station_geom',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 4: Query 8 - Ensure AVG(AVG(...)) pattern is used consistently
    # Check if there are any remaining AVG(vm.absolute_error) OVER without double AVG
    # This should already be fixed, but let's ensure
    
    # Fix 5: Query 9 - Ensure ST_TOUCHES uses CAST and fix ST_INTERSECTS/ST_DISTANCE
    # ST_INTERSECTS needs geometry casts
    content = re.sub(
        r'ST_INTERSECTS\s*\(\s*sb1\.boundary_geom\s*,\s*sb2\.boundary_geom\s*\)',
        r'ST_INTERSECTS(CAST(sb1.boundary_geom AS geometry), CAST(sb2.boundary_geom AS geometry))',
        content,
        flags=re.IGNORECASE
    )
    
    # ST_DISTANCE for boundaries should use geography
    content = re.sub(
        r'ST_DISTANCE\s*\(\s*sb1\.boundary_geom\s*,\s*sb2\.boundary_geom\s*\)',
        r'ST_DISTANCE(sb1.boundary_geom::geography, sb2.boundary_geom::geography)',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 6: Query 5 - Fix ST_DISTANCE calls that might be missing casts
    # In station_density_analysis CTE
    content = re.sub(
        r'ST_DISTANCE\s*\(\s*scb\.station_geom\s*,\s*scb2\.station_geom\s*\)',
        r'ST_DISTANCE(scb.station_geom::geography, scb2.station_geom::geography)',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 7: Query 5 - Fix ST_DISTANCE in boundary_coverage_analysis
    content = re.sub(
        r'ST_DISTANCE\s*\(\s*sda\.station_geom\s*,\s*sb\.boundary_geom\s*\)',
        r'ST_DISTANCE(sda.station_geom::geography, sb.boundary_geom::geography)',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 8: Query 5 - Fix ST_DISTANCE in interpolation_opportunity_analysis
    content = re.sub(
        r'ST_DISTANCE\s*\(\s*gf\.grid_cell_geom\s*,\s*sda\.station_geom\s*\)',
        r'ST_DISTANCE(gf.grid_cell_geom::geography, sda.station_geom::geography)',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 9: Query 2 - Ensure ST_Within in recursive CTE uses proper geometry casts
    # The error shows sb3.boundary_geom::geometry::geometry - need to fix this
    # This should be caught by fix 2, but let's be more specific
    
    if content != original_content:
        queries_file.write_text(content)
        print("Fixed db-6 queries.md")
        return True
    else:
        print("No changes needed for db-6 queries.md")
        return False

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    fix_db6_queries()
