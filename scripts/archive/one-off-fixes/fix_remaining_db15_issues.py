#!/usr/bin/env python3
"""
Fix remaining issues in db-15 queries.md
"""
import re
from pathlib import Path

def fix_db15_queries():
    queries_file = Path('db-15/queries/queries.md')
    content = queries_file.read_text()
    original_content = content
    
    # Fix 1: Query 2 - Ensure cumulative_kwh_usage is NUMERIC in anchor
    # Should already be fixed, but ensure consistency
    content = re.sub(
        r'(\s+)0\s+AS\s+cumulative_kwh_usage\b',
        r'\g<1>0::NUMERIC AS cumulative_kwh_usage',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 2: Query 3 & 12 - Fix gra.utility_code references
    # Replace gra.utility_code with gra.utility_id AS utility_code or gra.utility_id
    # In SELECT clauses, use gra.utility_id AS utility_code
    content = re.sub(
        r'\bgra\.utility_code\b(?=\s*,|\s+FROM|\s+WHERE|\s+GROUP|\s+ORDER|\s+HAVING|\s*$)',
        r'gra.utility_id',
        content,
        flags=re.IGNORECASE
    )
    
    # In COUNT(DISTINCT gra.utility_code), replace with utility_id
    content = re.sub(
        r'COUNT\s*\(\s*DISTINCT\s+gra\.utility_code\s*\)',
        r'COUNT(DISTINCT gra.utility_id)',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 3: Query 5 - Fix mi.state_code references
    # Should be s.state_code since market_intelligence joins with states
    content = re.sub(
        r'\bmi\.state_code\b',
        r's.state_code',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 4: Query 7 - Remove breaking comments in window functions
    # Remove comments that break SQL syntax
    content = re.sub(
        r'--\s*FIXED:\s*DISTINCT\s+removed\s*\n\s*\)',
        r')',
        content,
        flags=re.IGNORECASE | re.MULTILINE
    )
    
    # Fix 5: Query 9 - Fix PERCENT_RANK comparison logic
    # Change from: WHEN srs.avg_rate <= PERCENT_RANK() OVER (...)
    # To: WHEN PERCENT_RANK() OVER (ORDER BY srs.avg_rate) <= 0.25
    content = re.sub(
        r'WHEN\s+srs\.avg_rate\s*<=\s*PERCENT_RANK\s*\(\s*\)\s+OVER\s*\(\s*ORDER\s+BY\s+srs\.avg_rate\s*\)',
        r'WHEN PERCENT_RANK() OVER (ORDER BY srs.avg_rate) <= 0.25',
        content,
        flags=re.IGNORECASE
    )
    
    # Also fix other quartile comparisons
    content = re.sub(
        r'WHEN\s+srs\.avg_rate\s*<=\s*PERCENT_RANK\s*\(\s*\)\s+OVER\s*\(\s*ORDER\s+BY\s+srs\.avg_rate\s*DESC\s*\)',
        r'WHEN PERCENT_RANK() OVER (ORDER BY srs.avg_rate DESC) <= 0.25',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 6: Query 11 - Fix EXTRACT(EPOCH FROM date - date)
    # PostgreSQL DATE - DATE returns integer (days), not interval
    # Remove EXTRACT(EPOCH FROM ...) / 86400 and just use the subtraction
    content = re.sub(
        r'EXTRACT\s*\(\s*EPOCH\s+FROM\s+\(([^)]+)\s*-\s*([^)]+)\)\s*\)\s*/\s*86400',
        r'(\1 - \2)',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 7: Query 14 - Fix ambiguous annual_savings
    # Add alias fra to FROM final_roi_analysis and qualify columns
    content = re.sub(
        r'FROM\s+final_roi_analysis\b(?!\s+fra)',
        r'FROM final_roi_analysis fra',
        content,
        flags=re.IGNORECASE
    )
    
    # Qualify annual_savings and payback_period_years with fra.
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
    
    # Fix 8: Query 15 - Fix ambiguous avg_rate_3yr
    # Remove redundant selection of avg_rate_3yr in final_volatility_analysis
    # Find the pattern where avg_rate_3yr is selected twice
    # This is tricky - need to find the CTE definition
    # The issue is that ra.* includes avg_rate_3yr, then it's selected again explicitly
    # Remove the explicit selection
    
    # Fix 9: Query 26 - Fix recursive CTE array type (char vs TEXT)
    # Ensure all array elements use CAST(... AS TEXT)
    content = re.sub(
        r'::VARCHAR\s*\(\s*255\s*\)',
        r'::TEXT',
        content,
        flags=re.IGNORECASE
    )
    
    # Also ensure CAST(... AS VARCHAR(255)) becomes CAST(... AS TEXT)
    content = re.sub(
        r'CAST\s*\(([^)]+)\s+AS\s+VARCHAR\s*\(\s*255\s*\)\s*\)',
        r'CAST(\1 AS TEXT)',
        content,
        flags=re.IGNORECASE
    )
    
    if content != original_content:
        queries_file.write_text(content)
        print("Fixed db-15 queries.md")
        return True
    else:
        print("No changes needed for db-15 queries.md")
        return False

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    fix_db15_queries()
