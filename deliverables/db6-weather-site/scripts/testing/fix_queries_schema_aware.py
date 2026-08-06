#!/usr/bin/env python3
"""
Schema-aware query fixer
Fixes queries based on actual database schemas
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set

class SchemaAwareFixer:
    def __init__(self, schema_file: Path):
        """Initialize with actual database schemas"""
        with open(schema_file, 'r') as f:
            self.schemas = json.load(f)

        # Build column lookup maps
        self.column_maps = {}
        for db_key, tables in self.schemas.items():
            db_num = int(db_key.replace('db', ''))
            self.column_maps[db_num] = {}
            for table_name, columns in tables.items():
                col_names = [c['name'] for c in columns]
                self.column_maps[db_num][table_name] = set(col_names)

    def get_table_columns(self, db_num: int, table_name: str) -> Set[str]:
        """Get columns for a table"""
        return self.column_maps.get(db_num, {}).get(table_name, set())

    def find_table_for_column(self, db_num: int, column_name: str) -> List[str]:
        """Find tables that contain a column"""
        tables = []
        for table_name, columns in self.column_maps.get(db_num, {}).items():
            if column_name in columns:
                tables.append(table_name)
        return tables

    def fix_column_reference(self, sql: str, db_num: int, table_alias: str, column_name: str) -> str:
        """Fix a column reference if it doesn't exist"""
        # Check if column exists in any table for this database
        possible_tables = self.find_table_for_column(db_num, column_name)

        if not possible_tables:
            # Column doesn't exist - try common alternatives
            alternatives = {
                'uploaded_at': 'created_at',
                'category': None,  # Need context
                'value': None,  # Need context
                'date_col': 'created_at',
                'parent_id': None,  # Need context
            }

            if column_name in alternatives and alternatives[column_name]:
                return sql.replace(f'{table_alias}.{column_name}', f'{table_alias}.{alternatives[column_name]}')

        return sql

    def fix_query(self, sql: str, db_num: int) -> str:
        """Fix a query based on schema"""
        fixed = sql

        # Fix common column name mismatches
        column_fixes = {
            'uploaded_at': 'created_at',
        }

        for wrong_col, correct_col in column_fixes.items():
            # Fix in SELECT clauses
            fixed = re.sub(
                rf'\b(\w+)\.{wrong_col}\b',
                rf'\1.{correct_col}',
                fixed,
                flags=re.IGNORECASE
            )

        # Fix file_attachments.uploaded_at -> file_attachments.created_at
        fixed = re.sub(
            r'fa\d+\.uploaded_at',
            lambda m: m.group(0).replace('uploaded_at', 'created_at'),
            fixed,
            flags=re.IGNORECASE
        )

        # Fix recursive CTE aggregate issues
        # Remove aggregates from recursive terms (this is a PostgreSQL limitation)
        # This is complex and may require query restructuring

        # Fix GROUP BY issues - add missing non-aggregated columns
        # This requires parsing the query structure

        return fixed

def main():
    """Main execution"""
    root_dir = Path(__file__).parent.parent.parent
    schema_file = root_dir / 'results' / 'actual_schemas.json'

    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return

    fixer = SchemaAwareFixer(schema_file)

    print("="*70)
    print("SCHEMA-AWARE QUERY FIXER")
    print("="*70)
    print("\n⚠️  This fixer handles simple column name fixes.")
    print("   Complex schema mismatches may require manual query rewriting.")
    print()

    # Fix queries for each database
    for db_num in range(1, 6):
        db_dir = root_dir / f'db-{db_num}'
        queries_file = db_dir / 'queries' / 'queries.md'

        if not queries_file.exists():
            continue

        print(f"🔧 Fixing db-{db_num}...")

        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix SQL blocks
        def fix_sql_block(match):
            prefix = match.group(1)
            sql = match.group(2)
            suffix = match.group(3)

            fixed_sql = fixer.fix_query(sql, db_num)
            return prefix + fixed_sql + suffix

        pattern = r'(```sql\s*)(.*?)(```)'
        fixed_content = re.sub(pattern, fix_sql_block, content, flags=re.DOTALL | re.MULTILINE)

        # Write fixed content
        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"  ✅ Fixed queries")

    print("\n✅ Schema-aware fixes complete!")

if __name__ == '__main__':
    main()
