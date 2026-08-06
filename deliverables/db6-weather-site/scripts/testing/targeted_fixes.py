#!/usr/bin/env python3
"""
Targeted fixes for specific error patterns
"""

import re
from pathlib import Path

def fix_db5_queries():
    """Fix db-5 queries with specific error patterns"""
    root_dir = Path(__file__).parent.parent.parent
    queries_file = root_dir / 'db-5' / 'queries' / 'queries.md'

    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: GROUP BY with usm.metric_value
    content = re.sub(
        r'(GROUP BY\s+[^,\n]+)(?=\s*\)|$)',
        lambda m: m.group(0) + ', usm.metric_value' if 'usm.metric_value' in content and 'usm.metric_value' not in m.group(1) and 'GROUP BY usm' not in m.group(1) else m.group(0),
        content,
        flags=re.IGNORECASE | re.MULTILINE
    )

    # Fix 2: t.sale_id -> use proper table alias
    # t is likely phppos_sales, so t.sale_id should work if t is phppos_sales
    # But if t is something else, need to fix

    # Fix 3: t.item_unit_price -> t.unit_price (if that exists) or calculate from sales_items
    content = re.sub(r'\bt\.item_unit_price\b', 't.unit_price', content)

    # Fix 4: j.sale_id doesn't exist in phppos_customers - remove or fix join
    # phppos_customers doesn't have sale_id, need to join through phppos_sales
    content = re.sub(
        r'LEFT JOIN phppos_customers j ON t\.sale_id = j\.sale_id',
        'LEFT JOIN phppos_sales s ON t.sale_id = s.sale_id LEFT JOIN phppos_customers j ON s.customer_id = j.person_id',
        content
    )
    content = re.sub(
        r'LEFT JOIN phppos_employees j ON t\.sale_id = j\.sale_id',
        'LEFT JOIN phppos_sales s ON t.sale_id = s.sale_id LEFT JOIN phppos_employees j ON s.employee_id = j.person_id',
        content
    )

    # Fix other common column issues
    content = re.sub(r'\bj\.sale_id\b', 's.sale_id', content)

    with open(queries_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Fixed db-5 queries")

def main():
    print("=" * 70)
    print("APPLYING TARGETED FIXES")
    print("=" * 70)

    fix_db5_queries()

    print("\n✅ Targeted fixes applied")

if __name__ == '__main__':
    main()
