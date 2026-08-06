#!/usr/bin/env python3
"""
Rewrite queries for db-2 through db-5 to match actual schemas.
"""

import re
import json
from pathlib import Path

# Column mappings for db-2
DB2_COLUMN_MAPPINGS = {
    # orders_order table
    r'\bo\.price\b': 'o.total_price',  # orders_order has total_price, not price
    r'\bo2\.price\b': 'o2.total_price',
    r'\bo3\.price\b': 'o3.total_price',
    r'\bo4\.price\b': 'o4.total_price',
    r'\bo\.amount\b': 'o.total_price',
    r'\bo2\.amount\b': 'o2.total_price',
    r'\bo\.total_amount\b': 'o.total_price',  # orders_order has total_price
    r'\bo2\.total_amount\b': 'o2.total_price',

    # commissions_commission table
    r'\bc\.amount\b': 'c.commission_amount',  # commissions_commission has commission_amount, not amount
    r'\bc2\.amount\b': 'c2.commission_amount',
    r'\bc3\.amount\b': 'c3.commission_amount',

    # Generic template columns that don't exist - need table-specific replacements
    # These will be handled case-by-case based on context
}

# Schema info for db-2
DB2_SCHEMA = {
    'orders_order': ['id', 'order_number', 'quantity', 'unit_price', 'total_price', 'status', 'created_at', 'updated_at', 'customer_order_id', 'product_id', 'seller_id'],
    'commissions_commission': ['id', 'gross_sale_amount', 'commission_rate', 'commission_amount', 'platform_fee_rate', 'platform_fee_amount', 'net_commission', 'status', 'earned_at', 'holdback_until', 'approved_at', 'paid_at', 'reversal_reason', 'reversed_at', 'created_at', 'marketer_id', 'order_id', 'product_id', 'payout_id'],
    'products_product': ['id', 'name', 'slug', 'description', 'short_description', 'price', 'compare_at_price', 'cost_price', 'commission_rate', 'commission_type', 'fixed_commission_amount', 'stock_quantity', 'sku', 'images', 'specifications', 'is_active', 'is_featured', 'min_order_quantity', 'max_order_quantity', 'weight_kg', 'dimensions', 'seo_title', 'seo_description', 'seo_keywords', 'total_sales', 'total_revenue', 'average_rating', 'review_count', 'created_at', 'updated_at', 'seller_id', 'category_id'],
    'products_productcategory': ['id', 'name', 'slug', 'description', 'is_active', 'created_at', 'parent_id'],
}

def fix_nullif_syntax(text):
    """Fix NULLIF syntax errors like: NULLIF(CAST(... AS NUMERIC), 0) AS NUMERIC), 2)"""
    # Pattern: NULLIF(CAST(... AS NUMERIC), 0) AS NUMERIC), 2)
    # Should be: NULLIF(CAST(... AS NUMERIC), 0), 2)
    pattern = r'NULLIF\(CAST\(([^)]+)\) AS NUMERIC\),\s*0\)\s*AS NUMERIC\),\s*(\d+)\)'
    replacement = r'NULLIF(CAST(\1) AS NUMERIC), 0), \2)'
    return re.sub(pattern, replacement, text)

def fix_query_3_category_hierarchy(text):
    """Fix Query 3 category hierarchy issues"""
    # Fix anchor: WHERE pc.id IS NULL should be WHERE pc.parent_id IS NULL
    text = re.sub(
        r'FROM products_productcategory pc\s+WHERE pc\.id IS NULL',
        'FROM products_productcategory pc\n    WHERE pc.parent_id IS NULL',
        text
    )

    # Fix recursive: INNER JOIN category_hierarchy ch ON pc.id = ch.id should be pc.parent_id = ch.id
    text = re.sub(
        r'INNER JOIN category_hierarchy ch ON pc\.id = ch\.id',
        'INNER JOIN category_hierarchy ch ON pc.parent_id = ch.id',
        text
    )

    # Fix o.price to o.total_price
    text = re.sub(r'\bo\.price\b', 'o.total_price', text)
    text = re.sub(r'\bo2\.price\b', 'o2.total_price', text)
    text = re.sub(r'\bo3\.price\b', 'o3.total_price', text)

    # Fix NULLIF syntax error on line 1538
    # ROUND(CAST(ct.product_count::numeric / NULLIF(CAST(ct.level_product_total AS NUMERIC), 0) * 100, 2) AS product_share_percent,
    # Should be: ROUND(CAST(ct.product_count::numeric / NULLIF(CAST(ct.level_product_total AS NUMERIC), 0) * 100 AS NUMERIC), 2) AS product_share_percent,
    text = re.sub(
        r'ROUND\(CAST\(ct\.product_count::numeric / NULLIF\(CAST\(ct\.level_product_total AS NUMERIC\),\s*0\)\s*\*\s*100,\s*2\)\s*AS product_share_percent,',
        'ROUND(CAST(ct.product_count::numeric / NULLIF(CAST(ct.level_product_total AS NUMERIC), 0) * 100 AS NUMERIC), 2) AS product_share_percent,',
        text
    )
    text = re.sub(
        r'ROUND\(CAST\(ct\.total_revenue::numeric / NULLIF\(CAST\(ct\.level_revenue_total AS NUMERIC\),\s*0\)\s*\*\s*100,\s*2\)\s*AS revenue_share_percent,',
        'ROUND(CAST(ct.total_revenue::numeric / NULLIF(CAST(ct.level_revenue_total AS NUMERIC), 0) * 100 AS NUMERIC), 2) AS revenue_share_percent,',
        text
    )

    return text

def fix_query_4_generic_columns(text):
    """Fix Query 4 - replace generic 'name' column"""
    # Query 4 uses generic 'name' column that doesn't exist
    # Need to identify the table and use appropriate column
    # Based on context, this might be products_productcategory.name or products_product.name
    # This will need manual review, but let's try products_productcategory.name
    pass  # Will handle case-by-case

def apply_db2_fixes(text):
    """Apply all db-2 specific fixes"""
    # Fix NULLIF syntax
    text = fix_nullif_syntax(text)

    # Apply column mappings
    for pattern, replacement in DB2_COLUMN_MAPPINGS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Fix Query 3 specifically
    if 'category_hierarchy AS (' in text and 'products_productcategory' in text:
        text = fix_query_3_category_hierarchy(text)

    return text

def main():
    """Main function to rewrite queries"""
    base_path = Path(__file__).parent.parent

    # Process db-2
    db2_queries_file = base_path / 'db-2' / 'queries' / 'queries.md'
    if db2_queries_file.exists():
        print(f"Processing {db2_queries_file}...")
        with open(db2_queries_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply fixes
        fixed_content = apply_db2_fixes(content)

        # Write back
        with open(db2_queries_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"Fixed {db2_queries_file}")

    print("Done!")

if __name__ == '__main__':
    main()
