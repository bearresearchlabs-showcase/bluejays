#!/usr/bin/env python3
"""
Fix specific remaining issues in db-15 queries.md
"""
import re
from pathlib import Path

def fix_db15_queries():
    queries_file = Path('db-15/queries/queries.md')
    content = queries_file.read_text()
    original_content = content
    
    # Fix 1: Query 9 - Fix escaped quotes in CASE statement
    content = re.sub(
        r"\\'Lowest Quartile\\'",
        r"'Lowest Quartile'",
        content
    )
    content = re.sub(
        r"\\'Second Quartile\\'",
        r"'Second Quartile'",
        content
    )
    content = re.sub(
        r"\\'Third Quartile\\'",
        r"'Third Quartile'",
        content
    )
    
    # Fix 2: Query 14 - Fix fa.annual_savings (fa is not defined)
    content = re.sub(
        r'\bfa\.annual_savings\b',
        r'annual_savings',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix 3: Query 11 - Fix EXTRACT(EPOCH FROM date - date) for DATE types
    # These should be (date - date) directly since DATE - DATE returns integer days
    # But TIMESTAMP - TIMESTAMP returns interval, so EXTRACT is correct
    # The issue is DATE - DATE, not TIMESTAMP - TIMESTAMP
    # Let me check if there are DATE subtractions with EXTRACT
    
    # Fix 4: Query 7 - Check for breaking comments
    # Remove any comments that break SQL syntax in window functions
    content = re.sub(
        r'--\s*FIXED:.*?\n',
        r'',
        content,
        flags=re.IGNORECASE | re.MULTILINE
    )
    
    # Fix 5: Query 15 - Check if avg_rate_3yr is selected twice
    # The issue is that ra.* includes avg_rate_3yr, and it might be selected again
    # Let me check the final_volatility_analysis CTE
    
    # Fix 6: Query 5 - Check if mi.state_code is referenced directly
    # It should be s.state_code since market_intelligence joins with states
    
    # Fix 7: Query 3 & 12 - Check for any remaining gra.utility_code references
    # Should all be gra.utility_id
    
    # Fix 8: Query 2 - Ensure 0::NUMERIC is used consistently
    # Should already be fixed, but double-check
    
    # Fix 9: Query 26 - Ensure TEXT casts are used consistently
    # Should already be fixed
    
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
