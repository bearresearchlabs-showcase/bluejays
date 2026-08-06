#!/usr/bin/env python3
"""
Fix Division by Zero Issues in db-11
Adds NULLIF guards to prevent division by zero errors
"""

import re
import sys
from pathlib import Path

def fix_division_by_zero(content: str) -> tuple[str, int]:
    """Add NULLIF guards to division operations"""
    fixes = 0
    
    # Pattern: col1 / col2 (where col2 could be zero)
    # Match: identifier / identifier (not constants)
    pattern = r'(\b[\w.]+)\s*/\s*(\b[\w.()]+)'
    
    def replace_division(match):
        nonlocal fixes
        numerator = match.group(1)
        denominator = match.group(2)
        
        # Skip if denominator is a constant (number or string literal)
        if re.match(r'^\d+\.?\d*$', denominator) or denominator.startswith("'") or denominator.startswith('"'):
            return match.group(0)
        
        # Skip if already has NULLIF
        if 'NULLIF' in match.group(0):
            return match.group(0)
        
        # Skip if denominator is a function call (like COUNT, SUM, etc.)
        if '(' in denominator and not denominator.startswith('('):
            return match.group(0)
        
        fixes += 1
        return f"{numerator} / NULLIF({denominator}, 0)"
    
    content = re.sub(pattern, replace_division, content)
    
    return content, fixes

def main():
    if len(sys.argv) < 2:
        print("Usage: fix_division_by_zero.py <db-number>")
        sys.exit(1)
    
    db_num = sys.argv[1]
    db_path = Path(f'db-{db_num}/queries/queries.md')
    
    if not db_path.exists():
        print(f"Error: {db_path} not found")
        sys.exit(1)
    
    with open(db_path, 'r') as f:
        content = f.read()
    
    original_content = content
    content, fixes = fix_division_by_zero(content)
    
    if fixes > 0:
        with open(db_path, 'w') as f:
            f.write(content)
        print(f"db-{db_num}: FIXED - {fixes} division operations protected with NULLIF")
    else:
        print(f"db-{db_num}: No changes needed")

if __name__ == '__main__':
    main()
