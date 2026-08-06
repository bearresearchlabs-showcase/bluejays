#!/usr/bin/env python3
"""
Comprehensive script to rewrite queries for db-2 through db-5.
Applies schema-aware column mappings and fixes common issues.
"""

import re
import json
from pathlib import Path

# Load actual schemas
SCHEMAS_FILE = Path(__file__).parent.parent / 'results' / 'actual_schemas.json'

def load_schemas():
    """Load actual database schemas"""
    with open(SCHEMAS_FILE, 'r') as f:
        return json.load(f)

def get_column_mappings(db_name):
    """Get column mappings for a specific database"""
    schemas = load_schemas()
    db_schema = schemas.get(db_name, {})

    mappings = {}

    if db_name == 'db2':
        # orders_order mappings
        mappings.update({
            r'\bo\.price\b': 'o.total_price',
            r'\bo2\.price\b': 'o2.total_price',
            r'\bo3\.price\b': 'o3.total_price',
            r'\bo4\.price\b': 'o4.total_price',
            r'\bo\.total_amount\b': 'o.total_price',
            r'\bo2\.total_amount\b': 'o2.total_price',
            r'\bo3\.total_amount\b': 'o3.total_price',
        })

        # commissions_commission mappings
        mappings.update({
            r'\bc\.amount\b': 'c.commission_amount',
            r'\bc2\.amount\b': 'c2.commission_amount',
            r'\bc3\.amount\b': 'c3.commission_amount',
        })

        # affiliates_clicktracking mappings
        mappings.update({
            r'\bct\.created_at\b': 'ct.clicked_at',
            r'\bct2\.created_at\b': 'ct2.clicked_at',
            r'\bct3\.created_at\b': 'ct3.clicked_at',
            r'\bct4\.created_at\b': 'ct4.clicked_at',
        })

        # Join fixes
        mappings.update({
            r'CAST\(al\.id AS TEXT\)\s*=\s*CAST\(ct\.id AS TEXT\)': 'al.id = ct.link_id',
            r'ct2\.id\s*=\s*al2\.id': 'ct2.link_id = al2.id',
            r'ct3\.id\s*=\s*ct4\.id': 'ct3.link_id = ct4.link_id',
        })

    elif db_name == 'db3':
        # db3 uses table1, table2, table3 with name, value, category columns
        # Fix type casting issues
        mappings.update({
            r'CAST\(value AS NUMERIC AS NUMERIC\)': 'CAST(value AS NUMERIC)',
            r'AS NUMERIC AS NUMERIC': 'AS NUMERIC',
            r'AVG\(t3\.value\)': 'AVG(CAST(t3.value AS NUMERIC))',
        })
        # Fix foreign_id references - table1 has parent_id, not foreign_id
        mappings.update({
            r't3\.foreign_id': 't3.parent_id',
            r't2\.foreign_id': 't2.parent_id',
        })

    elif db_name == 'db4':
        # db4 has anonymous chat tables
        # Fix generic columns
        mappings.update({
            r't\.category': 't.chat_id',  # Use chat_id as category
            r'sc\.category': 'sc.chat_id',
            r't3\.foreign_id': 't3.chat_id',
            r'h\.parent_id': 'NULL',  # anonymous_chat_users doesn't have parent_id
        })
        # Fix value references
        mappings.update({
            r't1\.value': 't1.id',  # Use id as value proxy
        })

    elif db_name == 'db5':
        # db5 has phppos tables
        # Fix GROUP BY issues
        mappings.update({
            r'GROUP BY usm\.id,\s*usm\.metric_type\s*$': 'GROUP BY usm.id, usm.metric_type, usm.metric_value',
        })
        # Fix column references
        mappings.update({
            r't\.trans_date': 't.trans_time',  # phppos tables use trans_time
            r't\.quantity': 't.quantity_purchased',
            r't\.unit_price': 't.item_unit_price',
            r't\.percent': 't.discount_percent',
        })

    return mappings

def fix_nullif_syntax(text):
    """Fix NULLIF syntax errors"""
    # Pattern: ROUND(CAST(... / NULLIF(...), 0) * 100, 2) AS column_name,
    # Should be: ROUND(CAST(... / NULLIF(...), 0) * 100 AS NUMERIC), 2) AS column_name,
    pattern = r'ROUND\(CAST\(([^)]+)\s*/\s*NULLIF\(CAST\(([^)]+)\)\s*AS\s*NUMERIC\),\s*0\)\s*\*\s*100,\s*2\)\s*AS\s*(\w+),'
    replacement = r'ROUND(CAST(\1 / NULLIF(CAST(\2) AS NUMERIC), 0) * 100 AS NUMERIC), 2) AS \3,'
    text = re.sub(pattern, replacement, text)

    # Fix "AS NUMERIC AS NUMERIC" double casting
    text = re.sub(r'AS NUMERIC AS NUMERIC', 'AS NUMERIC', text)
    text = re.sub(r'CAST\(([^)]+)\) AS NUMERIC AS NUMERIC', r'CAST(\1) AS NUMERIC', text)

    return text

def fix_array_casting(text, db_name):
    """Fix array type casting issues"""
    if db_name == 'db2':
        # Fix ARRAY[pc.name] type mismatch
        text = re.sub(
            r'ARRAY\[pc\.name\]',
            r'ARRAY[CAST(pc.name AS character varying)]',
            text
        )
        text = re.sub(
            r'ARRAY\[t\.name\]',
            r'ARRAY[CAST(t.name AS character varying)]',
            text
        )
    return text

def fix_group_by_issues(text):
    """Fix GROUP BY clause issues with window functions"""
    # Pattern: GROUP BY col1, col2 without metric_value when using window functions
    # This is context-dependent, so we'll handle specific cases
    patterns = [
        (r'GROUP BY uhm\.id,\s*uhm\.metric_type\s*$', 'GROUP BY uhm.id, uhm.metric_type, uhm.metric_value'),
        (r'GROUP BY ucm\.category_id,\s*ucm\.metric_type\s*$', 'GROUP BY ucm.category_id, ucm.metric_type, ucm.metric_value'),
        (r'GROUP BY uwm\.id,\s*uwm\.metric_type\s*$', 'GROUP BY uwm.id, uwm.metric_type, uwm.metric_value'),
        (r'GROUP BY usm\.id,\s*usm\.metric_type\s*$', 'GROUP BY usm.id, usm.metric_type, usm.metric_value'),
        (r'GROUP BY ucm\.id,\s*ucm\.metric_type\s*$', 'GROUP BY ucm.id, ucm.metric_type, ucm.metric_value'),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)

    return text

def apply_fixes(text, db_name):
    """Apply all fixes for a database"""
    # Load column mappings
    mappings = get_column_mappings(db_name)

    # Apply column mappings
    for pattern, replacement in mappings.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Fix NULLIF syntax
    text = fix_nullif_syntax(text)

    # Fix array casting
    text = fix_array_casting(text, db_name)

    # Fix GROUP BY issues
    text = fix_group_by_issues(text)

    return text

def rewrite_queries_file(db_name):
    """Rewrite queries for a specific database"""
    base_path = Path(__file__).parent.parent
    queries_file = base_path / f'db-{db_name[-1]}' / 'queries' / 'queries.md'

    if not queries_file.exists():
        print(f"File not found: {queries_file}")
        return False

    print(f"Processing {queries_file}...")

    # Read file
    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply fixes
    fixed_content = apply_fixes(content, db_name)

    # Write back
    with open(queries_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"✅ Fixed {queries_file}")
    return True

def main():
    """Main function"""
    databases = ['db2', 'db3', 'db4', 'db5']

    for db_name in databases:
        rewrite_queries_file(db_name)

    print("\n✅ All queries rewritten!")

if __name__ == '__main__':
    main()
