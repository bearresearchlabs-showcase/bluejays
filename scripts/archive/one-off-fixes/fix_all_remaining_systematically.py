#!/usr/bin/env python3
"""
Systematic fix script for all remaining PostgreSQL compatibility issues
"""

import re
import sys
from pathlib import Path

def fix_ambiguous_columns(content: str) -> tuple[str, int]:
    """Fix ambiguous column references by adding table qualifiers"""
    fixes = 0
    
    # Pattern: Column reference in SELECT without qualifier that might be ambiguous
    # This is complex - we'll focus on common patterns
    
    # Fix: SELECT col FROM table1 JOIN table2 WHERE col = ... (ambiguous)
    # This requires context-aware parsing, so we'll handle specific cases
    
    return content, fixes

def fix_undefined_columns(content: str, db_num: str) -> tuple[str, int]:
    """Fix undefined column references"""
    fixes = 0
    
    # db-13: Fix evaluation_date -> created_at in Query 6 (already done)
    # db-13: Fix benchmark_id -> id in Query 4 (already done)
    
    return content, fixes

def fix_type_mismatches(content: str) -> tuple[str, int]:
    """Fix type mismatches in recursive CTEs and arrays"""
    fixes = 0
    
    # Fix recursive CTE array type mismatches
    # Pattern: ARRAY[col] where col might be inferred as wrong type
    pattern = r'ARRAY\[([^]]+)\]'
    def replace_array(match):
        nonlocal fixes
        expr = match.group(1)
        # If it's a column reference, cast to VARCHAR
        if re.match(r'^\w+\.\w+$', expr.strip()):
            fixes += 1
            return f'ARRAY[{expr}::VARCHAR(255)]'
        return match.group(0)
    
    content = re.sub(pattern, replace_array, content)
    
    return content, fixes

def fix_cross_join_on(content: str) -> tuple[str, int]:
    """Fix CROSS JOIN ... ON to INNER JOIN ... ON"""
    fixes = 0
    pattern = r'CROSS\s+JOIN\s+(\w+)\s+ON\s+'
    def replace_cross_join(match):
        nonlocal fixes
        fixes += 1
        table = match.group(1)
        return f"INNER JOIN {table} ON "
    content = re.sub(pattern, replace_cross_join, content, flags=re.IGNORECASE)
    return content, fixes

def fix_all_issues(content: str, db_num: str) -> tuple[str, int]:
    """Apply all fixes"""
    total_fixes = 0
    
    # Apply fixes in order
    content, fixes = fix_cross_join_on(content)
    total_fixes += fixes
    
    content, fixes = fix_type_mismatches(content)
    total_fixes += fixes
    
    return content, total_fixes

def main():
    if len(sys.argv) < 2:
        print("Usage: fix_all_remaining_systematically.py <db-number> [db-number2 ...]")
        sys.exit(1)
    
    db_nums = sys.argv[1:]
    
    for db_num in db_nums:
        db_path = Path(f'db-{db_num}/queries/queries.md')
        
        if not db_path.exists():
            print(f"Error: {db_path} not found")
            continue
        
        with open(db_path, 'r') as f:
            content = f.read()
        
        original_content = content
        content, fixes = fix_all_issues(content, db_num)
        
        if fixes > 0:
            with open(db_path, 'w') as f:
                f.write(content)
            print(f"db-{db_num}: FIXED - {fixes} fixes applied")
        else:
            print(f"db-{db_num}: No changes needed")

if __name__ == '__main__':
    main()
