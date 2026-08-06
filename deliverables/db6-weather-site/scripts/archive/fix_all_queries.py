#!/usr/bin/env python3
"""
Fix all queries in all databases based on test results
"""

import re
import json
from pathlib import Path
from typing import Dict

def fix_query_sql(sql: str) -> str:
    """Fix common SQL errors"""
    fixed = sql

    # Fix 1: Remove triple/double CAST patterns
    # CAST(CAST(CAST(x AS NUMERIC) AS NUMERIC) AS NUMERIC) -> CAST(x AS NUMERIC)
    fixed = re.sub(
        r'CAST\s*\(\s*CAST\s*\(\s*CAST\s*\(([^)]+)\s+AS\s+NUMERIC\s*\)\s+AS\s+NUMERIC\s*\)\s+AS\s+NUMERIC\s*\)',
        r'CAST(\1 AS NUMERIC)',
        fixed,
        flags=re.IGNORECASE | re.MULTILINE
    )

    # Fix double CAST
    fixed = re.sub(
        r'CAST\s*\(\s*CAST\s*\(([^)]+)\s+AS\s+NUMERIC\s*\)\s+AS\s+NUMERIC\s*\)',
        r'CAST(\1 AS NUMERIC)',
        fixed,
        flags=re.IGNORECASE | re.MULTILINE
    )

    # Fix 2: Fix PERCENTILE_CONT with OVER (PostgreSQL doesn't support this)
    # PERCENTILE_CONT(...) WITHIN GROUP (...) OVER (...) -> Use subquery or window function alternative
    def fix_percentile_over(match):
        full_match = match.group(0)
        # Remove OVER clause, keep WITHIN GROUP
        fixed_match = re.sub(r'\s+OVER\s*\([^)]*\)', '', full_match, flags=re.IGNORECASE)
        return fixed_match

    fixed = re.sub(
        r'PERCENTILE_CONT\s*\([^)]+\)\s+WITHIN\s+GROUP\s*\([^)]+\)\s+OVER\s*\([^)]+\)',
        fix_percentile_over,
        fixed,
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
    )

    # Fix 3: Fix syntax errors like "chs.1.0" -> proper column reference
    fixed = re.sub(
        r'(\w+)\.1\.0',
        r'\1.user_message_ratio',
        fixed
    )

    # Fix 4: Fix redundant COALESCE: COALESCE(x, x) -> x
    fixed = re.sub(
        r'COALESCE\s*\(\s*(\w+\.\w+)\s*,\s*\1\s*\)',
        r'\1',
        fixed,
        flags=re.IGNORECASE
    )

    # Fix 5: Fix GROUP BY issues - ensure all non-aggregated columns are in GROUP BY
    # This is complex and requires understanding the query structure

    # Fix 6: Fix missing FROM clause entries
    # This usually means a table alias is referenced but not defined in FROM

    return fixed

def fix_queries_md_file(file_path: Path) -> str:
    """Fix all queries in a queries.md file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract and fix each SQL block
    def fix_sql_block(match):
        prefix = match.group(1)  # ```sql
        sql = match.group(2)
        suffix = match.group(3)  # ```

        fixed_sql = fix_query_sql(sql)
        return prefix + fixed_sql + suffix

    # Match SQL code blocks
    pattern = r'(```sql\s*)(.*?)(```)'
    fixed_content = re.sub(pattern, fix_sql_block, content, flags=re.DOTALL | re.MULTILINE)

    return fixed_content

def main():
    """Main execution"""
    root_dir = Path(__file__).parent

    print("="*70)
    print("FIXING ALL QUERIES")
    print("="*70)

    # Fix queries for each database
    for db_num in range(1, 6):
        db_dir = root_dir / f'db-{db_num}'
        queries_file = db_dir / 'queries' / 'queries.md'

        if not queries_file.exists():
            print(f"\n⚠️  Skipping db-{db_num}: queries.md not found")
            continue

        print(f"\n🔧 Fixing queries for db-{db_num}...")

        # Create backup
        backup_file = queries_file.with_suffix('.md.backup')
        if not backup_file.exists():
            import shutil
            shutil.copy2(queries_file, backup_file)
            print(f"  ✅ Created backup: {backup_file.name}")

        # Fix queries
        fixed_content = fix_queries_md_file(queries_file)

        # Write fixed content
        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"  ✅ Fixed queries in: {queries_file.name}")

    print("\n" + "="*70)
    print("QUERY FIXING COMPLETE")
    print("="*70)
    print("\n⚠️  Note: Some complex errors may require manual fixes.")
    print("   Re-run tests to verify fixes.")

if __name__ == '__main__':
    main()
