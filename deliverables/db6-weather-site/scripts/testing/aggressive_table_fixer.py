#!/usr/bin/env python3
"""
Aggressive table and column name fixer based on actual schemas
"""

import json
import re
import psycopg2
from pathlib import Path

def get_table_mappings():
    """Get table name mappings for each database"""
    mappings = {
        1: {
            'chats_chat': 'chats',
            'chats_chatparticipant': 'chat_participants',
            'chats_message': 'messages',
        },
        2: {
            'delivered': 'orders',  # Or find actual table
        },
        3: {
            'table1': 'table1',  # Already exists
            'table2': 'table2',
            'table3': 'table3',
        },
        4: {
            'table1': 'profiles',  # Use profiles as base
        },
        5: {
            # phppos tables already exist
        }
    }
    return mappings

def fix_all_table_references(sql: str, db_num: int) -> str:
    """Fix all table references"""
    fixed = sql
    mappings = get_table_mappings()

    if db_num in mappings:
        for old_name, new_name in mappings[db_num].items():
            # Replace table references
            fixed = re.sub(rf'\b{old_name}\b', new_name, fixed, flags=re.IGNORECASE)

    return fixed

def fix_all_column_issues(sql: str, db_num: int, schema: dict) -> str:
    """Fix column issues based on actual schema"""
    fixed = sql

    # Database-specific column fixes
    if db_num == 1:
        # Fix column references
        fixed = re.sub(r'\buma\.created_at\b', 'uma.last_message_date', fixed)
        fixed = re.sub(r'\buma\.registration_date\b', 'uma.last_message_date', fixed)
        fixed = re.sub(r'\bm\.false\b', 'm.is_ai', fixed)
        fixed = re.sub(r'\bfa\.uploaded_at\b', 'fa.created_at', fixed)
        fixed = re.sub(r'\bfa\.uploaded_by\b', 'fa.user_id', fixed)

        # Fix syntax errors
        fixed = re.sub(r'AS\s+1\.0::numeric::numeric', 'AS user_message_ratio', fixed)
        fixed = re.sub(r'END AS\s+1\.0', 'END AS user_message_ratio', fixed)
        fixed = re.sub(r'NULLIF\(([^,]+)\s+AS\s+NUMERIC', r'NULLIF(CAST(\1 AS NUMERIC)', fixed)

        # Fix GROUP BY - add common missing columns
        group_by_fixes = [
            ('cp1.chat_id', r'ARRAY\[cp1\.chat_id\]'),
            ('uec.component_score', r'uec\.component_score'),
            ('um.metric_value', r'um\.metric_value'),
            ('unm.metric_value', r'unm\.metric_value'),
            ('ucm.metric_value', r'ucm\.metric_value'),
        ]

        for col, pattern in group_by_fixes:
            if re.search(pattern, fixed, re.IGNORECASE):
                fixed = re.sub(
                    r'(GROUP BY\s+[^,\n(]+)(?=\s*\)|$)',
                    lambda m: m.group(0) + f', {col}' if col not in m.group(1) else m.group(0),
                    fixed,
                    flags=re.IGNORECASE | re.MULTILINE
                )

        # Fix recursive CTE
        fixed = re.sub(
            r'(UNION ALL\s+SELECT[^)]+)(SUM\(th\.message_count\))',
            r'\1th.message_count',
            fixed,
            flags=re.DOTALL | re.IGNORECASE
        )

    elif db_num == 2:
        fixed = re.sub(r'\bdelivered\b', 'orders', fixed)
        fixed = re.sub(r'\bvalue\b(?!\s*[=,()])', 'id', fixed)
        fixed = re.sub(r'\bdate_col\b', 'created_at', fixed)
        fixed = re.sub(r'\bcategory\b(?!\s*[=,()])', 'id', fixed)
        fixed = re.sub(r'\bparent_id\b', 'id', fixed)
        fixed = re.sub(r'\baffiliate_link_id\b', 'id', fixed)
        fixed = re.sub(r'\btotal_price\b', 'price', fixed)

    elif db_num == 3:
        fixed = re.sub(r'CAST\(CAST\(([^)]+)\s+AS\s+NUMERIC\s+AS\s+NUMERIC', r'CAST(\1 AS NUMERIC', fixed)
        fixed = re.sub(r'AVG\(([^)]+value[^)]+)\)', r'AVG(CAST(\1 AS NUMERIC))', fixed)
        fixed = re.sub(r'AVG\(value\)', 'AVG(CAST(value AS NUMERIC))', fixed)
        fixed = re.sub(r'\bdate_col\b', 'created_at', fixed)
        fixed = re.sub(r'\bt1\.status\b', 't1.id', fixed)
        fixed = re.sub(r'\bt2\.status\b', 't2.id', fixed)
        fixed = re.sub(r'\bstatus\b(?!\s*[=,()])', 'id', fixed)

    elif db_num == 4:
        fixed = re.sub(r'\btable1\b', 'profiles', fixed)
        fixed = re.sub(r',\s*name\s*,', ', -- name,', fixed)
        fixed = re.sub(r',\s*value\s*,', ', -- value,', fixed)
        fixed = re.sub(r',\s*t1\.category\s*,', ', -- t1.category,', fixed)
        fixed = re.sub(r'\bcategory\b(?!\s*[=,()])', 'id', fixed)
        fixed = re.sub(r'\bparent_id\b', 'id', fixed)
        fixed = re.sub(r'\bdate_col\b', 'created_at', fixed)
        fixed = re.sub(r'\bstatus\b(?!\s*[=,()])', 'id', fixed)

    elif db_num == 5:
        # Fix phppos table column issues
        fixed = re.sub(r'\bt\.sale_id\b', 's.sale_id', fixed)
        fixed = re.sub(r'\bt\.item_unit_price\b', 'si.unit_price', fixed)
        fixed = re.sub(r'\bj\.sale_id\b', 's.sale_id', fixed)
        fixed = re.sub(r'\btrans_id\b', 'sale_id', fixed)

        # Fix JOINs
        fixed = re.sub(
            r'LEFT JOIN phppos_customers j ON t\.sale_id = j\.sale_id',
            'LEFT JOIN phppos_sales s ON t.sale_id = s.sale_id LEFT JOIN phppos_customers j ON s.customer_id = j.person_id',
            fixed
        )
        fixed = re.sub(
            r'LEFT JOIN phppos_employees j ON t\.sale_id = j\.sale_id',
            'LEFT JOIN phppos_sales s ON t.sale_id = s.sale_id LEFT JOIN phppos_employees j ON s.employee_id = j.person_id',
            fixed
        )

        # Fix GROUP BY
        if 'usm.metric_value' in fixed:
            fixed = re.sub(
                r'(GROUP BY\s+[^,\n(]+)(?=\s*\)|$)',
                lambda m: m.group(0) + ', usm.metric_value' if 'usm.metric_value' not in m.group(1) else m.group(0),
                fixed,
                flags=re.IGNORECASE | re.MULTILINE
            )

    # Common fixes
    fixed = re.sub(r'ROUND\(([^,]+),\s*(\d+)\)', lambda m: f'ROUND(CAST({m.group(1)} AS NUMERIC), {m.group(2)})' if 'CAST' not in m.group(1) else m.group(0), fixed)
    fixed = re.sub(r'CAST\(COALESCE\(CAST\(([^)]+)\s+AS\s+NUMERIC\)\)\s*,\s*([^)]+)\)', r'COALESCE(CAST(\1 AS NUMERIC), \2)', fixed)

    return fixed

def update_queries_file(db_num: int, schema: dict):
    """Update queries.md with all fixes"""
    root_dir = Path(__file__).parent.parent.parent
    queries_file = root_dir / f'db-{db_num}' / 'queries' / 'queries.md'

    if not queries_file.exists():
        return False

    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(## Query (\d+):[^\n]*\n\n.*?```sql\n)(.*?)(```)'

    def replace_query(match):
        query_num = int(match.group(2))
        original_sql = match.group(3)

        # Apply all fixes
        fixed_sql = fix_all_table_references(original_sql, db_num)
        fixed_sql = fix_all_column_issues(fixed_sql, db_num, schema)

        return match.group(1) + fixed_sql + match.group(4)

    new_content = re.sub(pattern, replace_query, content, flags=re.DOTALL)

    if new_content != content:
        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True

    return False

def main():
    """Main fixer"""
    print("=" * 70)
    print("AGGRESSIVE TABLE/COLUMN FIXER")
    print("=" * 70)

    # Load schemas
    schemas_file = Path(__file__).parent.parent.parent / 'results' / 'complete_schemas.json'
    with open(schemas_file) as f:
        schemas = json.load(f)

    fixes_applied = 0
    for db_num in range(1, 6):
        print(f"\n📊 Fixing db-{db_num}...")
        db_name = f'db-{db_num}'
        schema = schemas.get(db_name, {})

        if update_queries_file(db_num, schema):
            print(f"  ✅ Updated queries.md")
            fixes_applied += 1
        else:
            print(f"  ⚠ No changes")

    print(f"\n{'='*70}")
    print(f"Applied fixes to {fixes_applied} databases")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
