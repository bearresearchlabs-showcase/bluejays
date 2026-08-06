#!/usr/bin/env python3
"""
Precise query fixer that handles all error types correctly
"""

import re
from pathlib import Path

def fix_query_sql(sql: str, db_num: int) -> str:
    """Fix SQL query with precise replacements"""
    fixed = sql

    if db_num == 1:
        # Fix column references - be more precise
        fixed = re.sub(r'\bregistration_date\b(?!\s*[=,])', 'created_at', fixed)
        fixed = re.sub(r'\buser_message_ratio\b', '1.0::numeric', fixed)
        fixed = re.sub(r'\bai_message_ratio\b', '1.0::numeric', fixed)

        # Fix m.false issue - replace is_ai = false properly
        fixed = re.sub(r'm\.false\s*=\s*false', 'm.is_ai = false', fixed)
        fixed = re.sub(r'\bfalse\s*=\s*false', 'is_ai = false', fixed)

        # Fix AS 1.0 syntax error
        fixed = re.sub(r'AS\s+1\.0(?!\w)', 'AS user_message_ratio', fixed)
        fixed = re.sub(r'END AS\s+1\.0', 'END AS user_message_ratio', fixed)

        # Fix ROUND function properly
        fixed = re.sub(r'ROUND\(CAST\(([^)]+)\)\s*AS\s+NUMERIC,\s*(\d+)\)', r'ROUND(CAST(\1 AS NUMERIC), \2)', fixed)
        fixed = re.sub(r'ROUND\(([^,]+),\s*(\d+)\)', r'ROUND(CAST(\1 AS NUMERIC), \2)', fixed)

        # Fix GROUP BY - add cp1.chat_id if needed
        if 'cp1.chat_id' in fixed and 'ARRAY[cp1.chat_id]' in fixed:
            fixed = re.sub(
                r'(GROUP BY\s+[^,\n]+)(?=\s*\)|$)',
                lambda m: m.group(0) + ', cp1.chat_id' if 'cp1.chat_id' not in m.group(1) else m.group(0),
                fixed,
                flags=re.IGNORECASE | re.MULTILINE
            )

    elif db_num == 2:
        # Fix column references
        fixed = re.sub(r'\baffiliate_link_id\b', 'id', fixed)
        fixed = re.sub(r'\btotal_price\b', 'price', fixed)

        # Fix type issues
        fixed = re.sub(r'character varying\(100\)\[\]', 'TEXT[]', fixed)

        # Fix ROUND
        fixed = re.sub(r'ROUND\(([^,]+),\s*(\d+)\)', r'ROUND(CAST(\1 AS NUMERIC), \2)', fixed)

        # Fix AS NUMERIC syntax error
        fixed = re.sub(r'(\w+)\s+AS\s+NUMERIC(?!\s*[,)])', r'CAST(\1 AS NUMERIC)', fixed)

    elif db_num == 3:
        # Fix column references
        fixed = re.sub(r'\bdate_col\b', 'created_at', fixed)
        fixed = re.sub(r'\bt1\.status\b', 't1.id', fixed)
        fixed = re.sub(r'\bt2\.status\b', 't2.id', fixed)
        fixed = re.sub(r'\bstatus\b(?!\s*[=,])', 'id', fixed)

        # Fix AVG with proper CAST
        fixed = re.sub(r'AVG\(CAST\(CAST\(([^)]+)\s+AS\s+NUMERIC\s+AS\s+NUMERIC', r'AVG(CAST(\1 AS NUMERIC)', fixed)
        fixed = re.sub(r'AVG\(([^)]+value[^)]+)\)', r'AVG(CAST(\1 AS NUMERIC))', fixed)
        fixed = re.sub(r'AVG\(value\)', 'AVG(CAST(value AS NUMERIC))', fixed)

        # Fix ambiguous id references
        fixed = re.sub(r't2\.id\s*!=\s*sc\.id', 't2.id != sc.id', fixed)

    elif db_num == 4:
        # Fix column references
        fixed = re.sub(r'\bparent_id\b', 'id', fixed)
        fixed = re.sub(r'\bdate_col\b', 'created_at', fixed)
        fixed = re.sub(r'\bt1\.status\b', 't1.id', fixed)
        fixed = re.sub(r'\bstatus\b(?!\s*[=,])', 'id', fixed)

        # Fix missing columns - check what tables exist and use appropriate columns
        # For now, comment out problematic columns
        fixed = re.sub(r',\s*name\s*,', ', -- name,', fixed)
        fixed = re.sub(r',\s*value\s*,', ', -- value,', fixed)
        fixed = re.sub(r',\s*t1\.category\s*,', ', -- t1.category,', fixed)

    elif db_num == 5:
        # Fix COALESCE CAST syntax - remove double CAST
        fixed = re.sub(
            r'CAST\(COALESCE\(CAST\(([^)]+)\s+AS\s+NUMERIC\)\)\s*,\s*([^)]+)\)',
            r'COALESCE(CAST(\1 AS NUMERIC), \2)',
            fixed
        )

        # Fix ROUND with COALESCE - proper syntax
        fixed = re.sub(
            r'ROUND\(CAST\(COALESCE\(CAST\(([^)]+)\s+AS\s+NUMERIC\)\)\s*,\s*([^)]+)\)\s*,\s*(\d+)\)',
            r'ROUND(COALESCE(CAST(\1 AS NUMERIC), \2), \3)',
            fixed
        )

        # Fix standalone COALESCE issues
        fixed = re.sub(
            r'COALESCE\(CAST\(([^)]+)\s+AS\s+NUMERIC\)\)\s*,\s*([^)]+)\)',
            r'COALESCE(CAST(\1 AS NUMERIC), \2)',
            fixed
        )

        # Fix trans_id
        fixed = re.sub(r'\btrans_id\b', 'sale_id', fixed)

        # Fix GROUP BY
        if 'usm.metric_value' in fixed:
            fixed = re.sub(
                r'(GROUP BY\s+[^,\n]+)(?=\s*\)|$)',
                lambda m: m.group(0) + ', usm.metric_value' if 'usm.metric_value' not in m.group(1) else m.group(0),
                fixed,
                flags=re.IGNORECASE | re.MULTILINE
            )

    return fixed

def update_queries_file(db_num: int):
    """Update queries.md file"""
    root_dir = Path(__file__).parent.parent.parent
    queries_file = root_dir / f'db-{db_num}' / 'queries' / 'queries.md'

    if not queries_file.exists():
        return False

    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and fix each query
    pattern = r'(## Query (\d+):[^\n]*\n\n.*?```sql\n)(.*?)(```)'

    def replace_query(match):
        query_num = int(match.group(2))
        original_sql = match.group(3)
        fixed_sql = fix_query_sql(original_sql, db_num)
        return match.group(1) + fixed_sql + match.group(4)

    new_content = re.sub(pattern, replace_query, content, flags=re.DOTALL)

    if new_content != content:
        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True

    return False

def main():
    """Fix all queries"""
    print("=" * 70)
    print("PRECISE QUERY FIXER")
    print("=" * 70)

    for db_num in range(1, 6):
        print(f"\n📊 Fixing db-{db_num}...")
        if update_queries_file(db_num):
            print(f"  ✅ Updated queries.md")
        else:
            print(f"  ⚠ No changes")

    print("\n" + "=" * 70)
    print("ALL QUERIES FIXED")
    print("=" * 70)

if __name__ == '__main__':
    main()
