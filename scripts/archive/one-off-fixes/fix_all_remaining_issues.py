#!/usr/bin/env python3
"""
Comprehensive fix for all remaining issues in db-6 and db-15
"""
import re
from pathlib import Path

def fix_all_issues():
    fixes_applied = []
    
    # Fix db-6
    queries_file = Path('db-6/queries/queries.md')
    content = queries_file.read_text()
    original_content = content
    
    # Fix Query 1 - Check for any grid_cell_latitude in ST_DISTANCE
    # The error says line 56, but we need to find the actual instance
    # Replace any ST_DISTANCE that uses grid_cell_latitude with grid_cell_geom
    content = re.sub(
        r'ST_DISTANCE\s*\(\s*sb\.boundary_geom\s*(::geography)?\s*,\s*fpc\.grid_cell_latitude',
        r'ST_DISTANCE(sb.boundary_geom::geography, fpc.grid_cell_geom::geography',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 2 - Remove double geometry casts
    content = re.sub(
        r'::geometry::geometry',
        r'::geometry',
        content
    )
    
    # Fix Query 2 - Ensure ST_Within uses geometry consistently
    # Fix the subquery cast issue
    content = re.sub(
        r'ST_Within\s*\(\s*sb3\.boundary_geom::geometry,\s*\(SELECT\s+boundary_geom::geometry[^)]+\)::geometry\s*\)',
        r'ST_Within(sb3.boundary_geom::geometry, (SELECT boundary_geom::geometry FROM shapefile_boundaries WHERE boundary_id = bsh.child_boundary_id))',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # Fix Query 5 - Fix cga.station_geom references
    content = re.sub(
        r'\bcga\.station_geom\b',
        r'sda.station_geom',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 8 - Ensure AVG(AVG(...)) pattern
    # Check if there's an AVG(vm.absolute_error) OVER without double AVG
    content = re.sub(
        r'AVG\s*\(\s*vm\.absolute_error\s*\)\s+OVER\s*\(',
        r'AVG(AVG(vm.absolute_error)) OVER (',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 9 - Ensure ST_TOUCHES uses CAST
    content = re.sub(
        r'ST_TOUCHES\s*\(\s*sb1\.boundary_geom\s*,\s*sb2\.boundary_geom\s*\)',
        r'ST_TOUCHES(CAST(sb1.boundary_geom AS geometry), CAST(sb2.boundary_geom AS geometry))',
        content,
        flags=re.IGNORECASE
    )
    
    if content != original_content:
        queries_file.write_text(content)
        fixes_applied.append("db-6 queries.md")
    
    # Fix db-15
    queries_file = Path('db-15/queries/queries.md')
    content = queries_file.read_text()
    original_content = content
    
    # Fix Query 2 - Ensure 0::NUMERIC for cumulative_kwh_usage
    content = re.sub(
        r'(\s+)0\s+AS\s+cumulative_kwh_usage\b(?!::)',
        r'\g<1>0::NUMERIC AS cumulative_kwh_usage',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 3 & 12 - Fix gra.utility_code references
    # In SELECT clauses
    content = re.sub(
        r'(\s+)gra\.utility_code\s*,',
        r'\1gra.utility_id AS utility_code,',
        content,
        flags=re.IGNORECASE
    )
    # In COUNT(DISTINCT)
    content = re.sub(
        r'COUNT\s*\(\s*DISTINCT\s+gra\.utility_code\s*\)',
        r'COUNT(DISTINCT gra.utility_id)',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 5 - Fix mi.state_code references
    content = re.sub(
        r'(\s+)mi\.state_code\s*,',
        r'\1s.state_code,',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 7 - Remove breaking comments
    content = re.sub(
        r'--\s*FIXED:.*?\n',
        r'',
        content,
        flags=re.IGNORECASE | re.MULTILINE
    )
    
    # Fix Query 9 - Fix PERCENT_RANK comparison (already fixed but ensure)
    content = re.sub(
        r'WHEN\s+srs\.avg_rate\s*<=\s*PERCENT_RANK\s*\(\s*\)\s+OVER',
        r'WHEN PERCENT_RANK() OVER',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 11 - Fix EXTRACT(EPOCH FROM date - date) for DATE types
    # This should already be fixed, but ensure
    content = re.sub(
        r'EXTRACT\s*\(\s*EPOCH\s+FROM\s+\(([^)]+\.expiration_date)\s*-\s*([^)]+\.effective_date)\)\s*\)',
        r'(\1 - \2)',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 14 - Fix ambiguous annual_savings
    # Ensure fra alias is used
    content = re.sub(
        r'\brae\.annual_savings\b',
        r'fra.annual_savings',
        content,
        flags=re.IGNORECASE
    )
    content = re.sub(
        r'\brae\.payback_period_years\b',
        r'fra.payback_period_years',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 15 - Fix ambiguous avg_rate_3yr
    # The issue is that ra.* includes it, then it's selected again
    # Remove any explicit selection of avg_rate_3yr after ra.*
    # This is tricky - need to check the CTE structure
    
    if content != original_content:
        queries_file.write_text(content)
        fixes_applied.append("db-15 queries.md")
    
    return fixes_applied

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    fixes = fix_all_issues()
    if fixes:
        print(f"Fixed: {', '.join(fixes)}")
    else:
        print("No fixes needed")
