#!/usr/bin/env python3
"""
Customize queries for all databases to use actual schema columns instead of placeholders.
This script replaces placeholder columns (value, category, etc.) with actual columns from schemas.
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

BASE = Path("/Users/machine/Documents/AQ/db")

# Database-specific column mappings
# Maps placeholder columns to actual columns per database
DB_COLUMN_MAPPINGS = {
    1: {  # Airplane Tracking
        'main_table': 'aircraft_position_history',
        'value': 'altitude',  # Use altitude as primary numeric value
        'category': 'hex',    # Use hex code as category/grouping
        'id': 'id',
        'created_at': 'created_at',
        'timestamp': 'timestamp',
        'numeric_cols': ['altitude', 'speed', 'track', 'vertical_rate', 'lat', 'lon'],
        'time_cols': ['created_at', 'timestamp'],
        'text_cols': ['hex', 'flight']
    },
    2: {  # Filling Station POS
        'main_table': 'phppos_sales',
        'value': 'sale_id',  # Use sale_id as primary numeric
        'category': 'employee_id',  # Use employee_id as category
        'id': 'sale_id',
        'created_at': 'sale_time',
        'timestamp': 'sale_time',
        'numeric_cols': ['sale_id', 'customer_id', 'employee_id'],
        'time_cols': ['sale_time', 'sale_date'],
        'text_cols': ['comment']
    },
    3: {  # Linkway Ecommerce
        'main_table': 'orders_order',
        'value': 'total_amount',
        'category': 'status',
        'id': 'id',
        'created_at': 'created_at',
        'timestamp': 'created_at',
        'numeric_cols': ['total_amount', 'id'],
        'time_cols': ['created_at'],
        'text_cols': ['order_number', 'status']
    },
    4: {  # Seydam AI
        'main_table': 'models',
        'value': 'id',
        'category': 'name',
        'id': 'id',
        'created_at': 'created_at',
        'timestamp': 'created_at',
        'numeric_cols': ['id'],
        'time_cols': ['created_at'],
        'text_cols': ['name']
    },
    5: {  # SharedAI
        'main_table': 'chats',
        'value': 'id',
        'category': 'id',
        'id': 'id',
        'created_at': 'created_at',
        'timestamp': 'created_at',
        'numeric_cols': ['id'],
        'time_cols': ['created_at'],
        'text_cols': []
    }
}

def customize_query_sql(sql: str, mapping: Dict) -> str:
    """Replace placeholder columns with actual columns."""
    # Replace value references
    sql = re.sub(r'\bvalue\b', mapping['value'], sql, flags=re.IGNORECASE)
    
    # Replace category references (be careful with PARTITION BY)
    sql = re.sub(r'PARTITION BY\s+c\d+\.category\b', 
                 f"PARTITION BY c1.{mapping['category']}", sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bc\d+\.category\b', mapping['category'], sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bcategory\b', mapping['category'], sql, flags=re.IGNORECASE)
    
    # Ensure table names are correct (they should already be, but verify)
    # sql = sql.replace('main_table', mapping['main_table'])
    
    return sql

def customize_queries_file(db_num: int) -> bool:
    """Customize queries.md file for a database."""
    queries_file = BASE / f"db-{db_num}/queries/queries.md"
    if not queries_file.exists():
        print(f"❌ db-{db_num}: queries.md not found")
        return False
    
    if db_num not in DB_COLUMN_MAPPINGS:
        print(f"❌ db-{db_num}: No column mapping defined")
        return False
    
    mapping = DB_COLUMN_MAPPINGS[db_num]
    content = queries_file.read_text()
    
    # Extract and customize each query
    # Pattern: ## Query N: ... ```sql ... ```
    query_pattern = r'(## Query \d+:.*?```sql\n)(.*?)(\n```)'
    
    def replace_query(match):
        header = match.group(1)
        sql = match.group(2)
        footer = match.group(3)
        
        # Customize SQL
        customized_sql = customize_query_sql(sql, mapping)
        
        return header + customized_sql + footer
    
    customized_content = re.sub(query_pattern, replace_query, content, flags=re.DOTALL)
    
    # Write back
    queries_file.write_text(customized_content)
    print(f"✅ db-{db_num}: Customized queries.md")
    return True

def main():
    """Customize queries for all databases."""
    print("=" * 70)
    print("Customizing Queries for All Databases")
    print("=" * 70)
    
    success_count = 0
    for db_num in [1, 2, 3, 4, 5]:
        if customize_queries_file(db_num):
            success_count += 1
    
    print(f"\n{'=' * 70}")
    print(f"Completed: {success_count}/5 databases")
    print(f"{'=' * 70}")

if __name__ == '__main__':
    main()
