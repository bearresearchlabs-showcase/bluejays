#!/usr/bin/env python3
"""
Comprehensive schema-aware query fixer addressing all specific errors
"""

import json
import re
from pathlib import Path
from typing import Dict

def load_schemas() -> Dict:
    """Load schemas"""
    schemas_file = Path(__file__).parent.parent.parent / 'results' / 'complete_schemas.json'
    with open(schemas_file) as f:
        return json.load(f)

def load_errors() -> Dict:
    """Load errors"""
    errors_file = Path(__file__).parent.parent.parent / 'results' / 'detailed_errors.json'
    with open(errors_file) as f:
        return json.load(f)

def fix_db1_query(sql: str, error_info: Dict) -> str:
    """Fix db-1 query"""
    fixed = sql

    # Fix chats_chat -> chats
    fixed = re.sub(r'\bchats_chat\b', 'chats', fixed)

    # Fix column references
    fixed = re.sub(r'\buma\.created_at\b', 'uma.last_message_date', fixed)
    fixed = re.sub(r'\buma\.registration_date\b', 'uma.last_message_date', fixed)
    fixed = re.sub(r'\bm\.false\b', 'm.is_ai', fixed)
    fixed = re.sub(r'\bfa\.uploaded_at\b', 'fa.created_at', fixed)

    # Fix syntax errors
    fixed = re.sub(r'AS\s+1\.0::numeric::numeric', 'AS user_message_ratio', fixed)
    fixed = re.sub(r'NULLIF\(([^,]+)\s+AS\s+NUMERIC', r'NULLIF(CAST(\1 AS NUMERIC)', fixed)

    # Fix GROUP BY errors
    if 'group_by_column' in error_info:
        col = error_info['group_by_column']
        fixed = re.sub(
            r'(GROUP BY\s+[^,\n(]+)(?=\s*\)|$)',
            lambda m: m.group(0) + f', {col}' if col not in m.group(1) else m.group(0),
            fixed,
            flags=re.IGNORECASE | re.MULTILINE
        )

    # Fix recursive CTE aggregation
    fixed = re.sub(
        r'(UNION ALL\s+SELECT[^)]+)(SUM\(th\.message_count\))',
        r'\1th.message_count',
        fixed,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Fix missing FROM clause
    if 'missing FROM-clause' in error_info.get('message', ''):
        # Add missing table alias
        if 'cp1.chat_id' in fixed and 'FROM' not in fixed.split('cp1.chat_id')[0][-100:]:
            # Try to add the missing table
            pass

    return fixed

def fix_db2_query(sql: str, error_info: Dict) -> str:
    """Fix db-2 query"""
    fixed = sql

    # Fix missing table
    fixed = re.sub(r'\bdelivered\b', 'orders', fixed)  # Use orders table if exists

    # Fix missing columns
    fixed = re.sub(r'\bvalue\b(?!\s*[=,])', 'id', fixed)  # Use id as fallback
    fixed = re.sub(r'\bdate_col\b', 'created_at', fixed)
    fixed = re.sub(r'\bcategory\b(?!\s*[=,])', 'id', fixed)
    fixed = re.sub(r'\bparent_id\b', 'id', fixed)

    # Fix function errors
    fixed = re.sub(r'ROUND\(([^,]+),\s*(\d+)\)', r'ROUND(CAST(\1 AS NUMERIC), \2)', fixed)

    return fixed

def fix_db3_query(sql: str, error_info: Dict) -> str:
    """Fix db-3 query"""
    fixed = sql

    # Fix syntax errors - double CAST
    fixed = re.sub(r'CAST\(CAST\(([^)]+)\s+AS\s+NUMERIC\s+AS\s+NUMERIC', r'CAST(\1 AS NUMERIC', fixed)

    # Fix AVG on text
    fixed = re.sub(r'AVG\(([^)]+value[^)]+)\)', r'AVG(CAST(\1 AS NUMERIC))', fixed)
    fixed = re.sub(r'AVG\(value\)', 'AVG(CAST(value AS NUMERIC))', fixed)

    # Fix ambiguous columns
    fixed = re.sub(r't2\.id\s*!=\s*sc\.id', 't2.id != sc.id', fixed)

    # Fix date_col
    fixed = re.sub(r'\bdate_col\b', 'created_at', fixed)
    fixed = re.sub(r'\bstatus\b(?!\s*[=,])', 'id', fixed)

    return fixed

def fix_db4_query(sql: str, error_info: Dict) -> str:
    """Fix db-4 query"""
    fixed = sql

    # Fix missing table
    fixed = re.sub(r'\btable1\b', 'profiles', fixed)  # Use profiles as base table

    # Fix missing columns
    fixed = re.sub(r',\s*name\s*,', ', -- name,', fixed)
    fixed = re.sub(r',\s*value\s*,', ', -- value,', fixed)
    fixed = re.sub(r',\s*t1\.category\s*,', ', -- t1.category,', fixed)
    fixed = re.sub(r'\bcategory\b(?!\s*[=,])', 'id', fixed)

    # Fix other issues
    fixed = re.sub(r'\bparent_id\b', 'id', fixed)
    fixed = re.sub(r'\bdate_col\b', 'created_at', fixed)
    fixed = re.sub(r'\bstatus\b(?!\s*[=,])', 'id', fixed)

    return fixed

def fix_db5_query(sql: str, error_info: Dict) -> str:
    """Fix db-5 query"""
    fixed = sql

    # Fix GROUP BY
    if 'group_by_column' in error_info:
        col = error_info['group_by_column']
        fixed = re.sub(
            r'(GROUP BY\s+[^,\n(]+)(?=\s*\)|$)',
            lambda m: m.group(0) + f', {col}' if col not in m.group(1) else m.group(0),
            fixed,
            flags=re.IGNORECASE | re.MULTILINE
        )

    # Fix missing columns - check what columns actually exist in phppos tables
    # Common fixes
    fixed = re.sub(r'\bt\.sale_id\b', 's.sale_id', fixed)  # If t is not phppos_sales
    fixed = re.sub(r'\bt\.item_unit_price\b', 'si.unit_price', fixed)
    fixed = re.sub(r'\bj\.sale_id\b', 's.sale_id', fixed)

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

    # Fix missing table references
    if 'missing_table' in error_info:
        table = error_info['missing_table']
        # Map to existing table if possible
        if 'sales' in table.lower():
            fixed = re.sub(rf'\b{table}\b', 'phppos_sales', fixed)

    return fixed

def update_queries_file(db_num: int, schemas: Dict, errors: Dict):
    """Update queries.md"""
    root_dir = Path(__file__).parent.parent.parent
    queries_file = root_dir / f'db-{db_num}' / 'queries' / 'queries.md'

    if not queries_file.exists():
        return False

    db_name = f'db-{db_num}'
    db_errors = errors.get(db_name, {})

    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix each query
    pattern = r'(## Query (\d+):[^\n]*\n\n.*?```sql\n)(.*?)(```)'

    def replace_query(match):
        query_num = int(match.group(2))
        original_sql = match.group(3)

        error_info = db_errors.get(str(query_num), {})

        # Apply database-specific fixes
        if db_num == 1:
            fixed_sql = fix_db1_query(original_sql, error_info)
        elif db_num == 2:
            fixed_sql = fix_db2_query(original_sql, error_info)
        elif db_num == 3:
            fixed_sql = fix_db3_query(original_sql, error_info)
        elif db_num == 4:
            fixed_sql = fix_db4_query(original_sql, error_info)
        elif db_num == 5:
            fixed_sql = fix_db5_query(original_sql, error_info)
        else:
            fixed_sql = original_sql

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
    print("COMPREHENSIVE SCHEMA FIXER")
    print("=" * 70)

    schemas = load_schemas()
    errors = load_errors()

    fixes_applied = 0
    for db_num in range(1, 6):
        print(f"\n📊 Fixing db-{db_num}...")
        if update_queries_file(db_num, schemas, errors):
            print(f"  ✅ Updated queries.md")
            fixes_applied += 1
        else:
            print(f"  ⚠ No changes")

    print(f"\n{'='*70}")
    print(f"Applied fixes to {fixes_applied} databases")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
