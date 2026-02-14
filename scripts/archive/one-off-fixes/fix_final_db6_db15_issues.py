#!/usr/bin/env python3
"""
Final fixes for db-6 and db-15 remaining issues
"""
import re
from pathlib import Path

def fix_all():
    fixes = []
    
    # Fix db-6
    queries_file = Path('db-6/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # Fix Query 9 - ST_UNION(geography, geography) -> CAST to geometry
    content = re.sub(
        r'ST_UNION\s*\(\s*bp\.boundary1_geom\s*,\s*bp\.boundary2_geom\s*\)',
        r'ST_UNION(CAST(bp.boundary1_geom AS geometry), CAST(bp.boundary2_geom AS geometry))',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 2 - Check recursive CTE type consistency
    # The error says column 8 has type mismatch - need to check the recursive CTE
    
    if content != original:
        queries_file.write_text(content)
        fixes.append("db-6")
    
    # Fix db-15
    queries_file = Path('db-15/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # Fix Query 3 - roa.utility_id -> roa.utility_code (check what roa actually has)
    # Actually, roa is rebate_optimization_analysis, need to check what it selects
    # But error says roa.utility_code exists, so change utility_id to utility_code
    content = re.sub(
        r'\broa\.utility_id\b',
        r'roa.utility_code',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 5 - s.state_code -> s.state_id (state_id IS the state code in this schema)
    content = re.sub(
        r'\bs\.state_code\b',
        r's.state_id',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 7 - GROUP BY issue with rc.rate_code_id
    # Need to add rc.rate_code_id to GROUP BY or use aggregate
    
    # Fix Query 8 - npva.year doesn't exist
    # Need to check npv_analysis CTE structure
    
    # Fix Query 10 - rs.rate_structure_type -> rc.rate_structure_type
    content = re.sub(
        r'\brs\.rate_structure_type\b',
        r'rc.rate_structure_type',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 12 - gra.utility_id -> er.utility_id
    content = re.sub(
        r'\bgra\.utility_id\b',
        r'er.utility_id',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix Query 14 - fra.annual_savings -> sec.annual_savings (fra doesn't exist, should be sec)
    content = re.sub(
        r'\bfra\.annual_savings\b',
        r'sec.annual_savings',
        content,
        flags=re.IGNORECASE
    )
    content = re.sub(
        r'\bfra\.payback_period_years\b',
        r'sec.payback_period_years',
        content,
        flags=re.IGNORECASE
    )
    
    if content != original:
        queries_file.write_text(content)
        fixes.append("db-15")
    
    return fixes

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    fixes = fix_all()
    if fixes:
        print(f"Fixed: {', '.join(fixes)}")
    else:
        print("No fixes needed")
