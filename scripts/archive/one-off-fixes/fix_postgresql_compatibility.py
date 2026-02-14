#!/usr/bin/env python3
"""
Fix PostgreSQL Compatibility Issues
- Fixes VARCHAR length limits
- Fixes query syntax errors
- Fixes function compatibility
"""

import re
from pathlib import Path
from typing import List, Tuple

def fix_schema_varchar_limits(file_path: Path) -> Tuple[int, List[str]]:
    """Replace VARCHAR(16777216) with TEXT in schema files"""
    if not file_path.exists():
        return 0, []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes = []
    
    # Replace VARCHAR(16777216) with TEXT
    pattern = r'VARCHAR\s*\(\s*16777216\s*\)'
    matches = list(re.finditer(pattern, content, re.IGNORECASE))
    
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        fixes.append(f"Line {line_num}: VARCHAR(16777216) -> TEXT")
    
    content = re.sub(pattern, 'TEXT', content, flags=re.IGNORECASE)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return len(matches), fixes
    
    return 0, []

def fix_query_syntax_errors(file_path: Path) -> Tuple[int, List[str]]:
    """Fix query syntax errors in queries.md files"""
    if not file_path.exists():
        return 0, []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes = []
    
    # Fix 1: DATE_PART with CURRENT_TIMESTAMP() -> CURRENT_TIMESTAMP
    pattern1 = r"DATE_PART\s*\(\s*['\"]day['\"]\s*,\s*CURRENT_TIMESTAMP\s*\(\s*\)\s*-\s*"
    if re.search(pattern1, content, re.IGNORECASE):
        content = re.sub(r'CURRENT_TIMESTAMP\s*\(\s*\)', 'CURRENT_TIMESTAMP', content, flags=re.IGNORECASE)
        fixes.append("Fixed CURRENT_TIMESTAMP() -> CURRENT_TIMESTAMP")
    
    # Fix 2: DATE_ADD -> PostgreSQL date arithmetic
    pattern2 = r"DATE_ADD\s*\(\s*([^,]+)\s*,\s*INTERVAL\s+([^)]+)\s*\)"
    def replace_date_add(match):
        date_expr = match.group(1)
        interval = match.group(2)
        return f"({date_expr} + INTERVAL {interval})"
    
    if re.search(pattern2, content, re.IGNORECASE):
        content = re.sub(pattern2, replace_date_add, content, flags=re.IGNORECASE)
        fixes.append("Fixed DATE_ADD -> PostgreSQL date arithmetic")
    
    # Fix 3: CROSS JOIN ... ON -> INNER JOIN
    pattern3 = r'CROSS\s+JOIN\s+(\w+)\s+(\w+)\s+ON\s+'
    def replace_cross_join(match):
        table = match.group(1)
        alias = match.group(2)
        return f"INNER JOIN {table} {alias} ON "
    
    if re.search(pattern3, content, re.IGNORECASE):
        content = re.sub(pattern3, replace_cross_join, content, flags=re.IGNORECASE)
        fixes.append("Fixed CROSS JOIN ... ON -> INNER JOIN")
    
    # Fix 4: DISTINCT in window functions - remove DISTINCT from OVER clause
    # Pattern: COUNT(DISTINCT ...) OVER (...) -> COUNT(...) OVER (DISTINCT ...) is invalid
    # We need to use subquery or CTE instead
    # This is complex, so we'll note it but may need manual fixes
    
    # Fix 5: DATEDIFF -> PostgreSQL date difference
    pattern5 = r"DATEDIFF\s*\(\s*['\"]day['\"]\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)"
    def replace_datediff(match):
        date1 = match.group(1)
        date2 = match.group(2)
        return f"EXTRACT(EPOCH FROM ({date2} - {date1})) / 86400"
    
    if re.search(pattern5, content, re.IGNORECASE):
        content = re.sub(pattern5, replace_datediff, content, flags=re.IGNORECASE)
        fixes.append("Fixed DATEDIFF -> EXTRACT(EPOCH FROM ...)")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return len(fixes), fixes
    
    return 0, []

def fix_division_by_zero(file_path: Path) -> Tuple[int, List[str]]:
    """Add NULLIF to prevent division by zero"""
    if not file_path.exists():
        return 0, []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes = []
    
    # Pattern: / column_name or / (expression)
    # Replace: / NULLIF(column_name, 0) or / NULLIF((expression), 0)
    # This is complex and context-dependent, so we'll be conservative
    
    # Simple pattern: column / other_column -> column / NULLIF(other_column, 0)
    pattern = r'(\w+)\s*/\s*(\w+)'
    # But this is too broad - we need to be more careful
    
    # For now, we'll note this but may need manual fixes
    # The actual fixes should be done query-by-query
    
    return 0, []

def main():
    """Fix all PostgreSQL compatibility issues"""
    root_dir = Path(__file__).parent.parent
    
    print("="*70)
    print("PostgreSQL Compatibility Fixes")
    print("="*70)
    
    # Fix schema files
    print("\n1. Fixing Schema VARCHAR Length Limits...")
    schema_fixes = {}
    for db_num in range(6, 16):
        db_name = f'db-{db_num}'
        schema_file = root_dir / db_name / 'data' / 'schema.sql'
        
        if schema_file.exists():
            count, fixes = fix_schema_varchar_limits(schema_file)
            if count > 0:
                schema_fixes[db_name] = {'count': count, 'fixes': fixes}
                print(f"  {db_name}: Fixed {count} VARCHAR(16777216) -> TEXT")
    
    # Fix query files
    print("\n2. Fixing Query Syntax Errors...")
    query_fixes = {}
    for db_num in range(6, 16):
        db_name = f'db-{db_num}'
        query_file = root_dir / db_name / 'queries' / 'queries.md'
        
        if query_file.exists():
            count, fixes = fix_query_syntax_errors(query_file)
            if count > 0:
                query_fixes[db_name] = {'count': count, 'fixes': fixes}
                print(f"  {db_name}: Applied {count} fixes")
                for fix in fixes:
                    print(f"    - {fix}")
    
    print("\n" + "="*70)
    print("Fix Summary")
    print("="*70)
    print(f"\nSchema Files Fixed: {len(schema_fixes)}")
    print(f"Query Files Fixed: {len(query_fixes)}")
    
    return schema_fixes, query_fixes

if __name__ == '__main__':
    main()
