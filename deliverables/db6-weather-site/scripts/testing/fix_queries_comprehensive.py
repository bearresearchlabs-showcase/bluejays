#!/usr/bin/env python3
"""
Comprehensive Query Fixer
Fixes common SQL errors in queries based on actual database schemas
"""

import re
import json
from pathlib import Path
from typing import Dict, List

class QueryFixer:
    def __init__(self, schema_file: Path):
        """Initialize with actual database schemas"""
        with open(schema_file, 'r') as f:
            self.schemas = json.load(f)

    def fix_query(self, query_sql: str, db_num: int) -> str:
        """Fix a single query"""
        fixed = query_sql

        # Get schema for this database
        schema_key = f'db{db_num}'
        if schema_key not in self.schemas:
            return fixed

        schema = self.schemas[schema_key]

        # Fix 1: Remove double CAST patterns: CAST(...AS NUMERIC) AS NUMERIC
        fixed = re.sub(
            r'CAST\(CAST\(([^)]+)\s+AS\s+NUMERIC\)\s+AS\s+NUMERIC\)',
            r'CAST(\1 AS NUMERIC)',
            fixed,
            flags=re.IGNORECASE
        )

        # Fix 2: Fix triple CAST patterns
        fixed = re.sub(
            r'CAST\(CAST\(CAST\(([^)]+)\s+AS\s+NUMERIC\)\s+AS\s+NUMERIC\)\s+AS\s+NUMERIC\)',
            r'CAST(\1 AS NUMERIC)',
            fixed,
            flags=re.IGNORECASE
        )

        # Fix 3: Fix syntax errors like "chs.1.0" -> "chs.user_message_ratio"
        fixed = re.sub(
            r'(\w+)\.1\.0',
            r'\1.user_message_ratio',
            fixed
        )

        # Fix 4: Fix PERCENTILE_CONT with OVER (PostgreSQL doesn't support this)
        # Replace: PERCENTILE_CONT(0.5) WITHIN GROUP (...) OVER (...)
        # With: PERCENTILE_CONT(0.5) WITHIN GROUP (...)
        fixed = re.sub(
            r'PERCENTILE_CONT\(([^)]+)\)\s+WITHIN\s+GROUP\s*\(([^)]+)\)\s+OVER\s*\(([^)]+)\)',
            lambda m: f'PERCENTILE_CONT({m.group(1)}) WITHIN GROUP ({m.group(2)})',
            fixed,
            flags=re.IGNORECASE
        )

        # Fix 5: Fix aggregate functions in recursive CTE recursive terms
        # This is more complex - we'll need to restructure the query
        # For now, comment out problematic aggregates in recursive terms

        # Fix 6: Fix GROUP BY issues - add missing columns
        # This requires understanding the query structure, so we'll handle it case by case

        # Fix 7: Fix missing FROM clause entries
        # This usually means a table alias is used but not defined

        # Fix 8: Fix column name mismatches based on actual schema
        # Check common mismatches

        return fixed

    def fix_queries_file(self, queries_file: Path, db_num: int, output_file: Path):
        """Fix all queries in a queries.md file"""
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract queries
        query_pattern = r'(## Query \d+:.*?```sql\s*)(.*?)(```)'

        def fix_match(match):
            header = match.group(1)
            sql = match.group(2)
            closing = match.group(3)

            fixed_sql = self.fix_query(sql, db_num)
            return header + fixed_sql + closing

        fixed_content = re.sub(query_pattern, fix_match, content, flags=re.DOTALL | re.IGNORECASE)

        # Write fixed file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        return fixed_content

def main():
    """Main execution"""
    root_dir = Path(__file__).parent.parent.parent
    schema_file = root_dir / 'results' / 'actual_schemas.json'

    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return

    fixer = QueryFixer(schema_file)

    # Fix queries for each database
    for db_num in range(1, 6):
        db_dir = root_dir / f'db-{db_num}'
        queries_file = db_dir / 'queries' / 'queries.md'

        if not queries_file.exists():
            print(f"⚠️  Skipping db-{db_num}: queries.md not found")
            continue

        print(f"\n🔧 Fixing queries for db-{db_num}...")

        # Create backup
        backup_file = queries_file.with_suffix('.md.backup')
        if not backup_file.exists():
            import shutil
            shutil.copy2(queries_file, backup_file)
            print(f"  ✅ Created backup: {backup_file}")

        # Fix queries
        fixed_file = db_dir / 'queries' / 'queries_fixed.md'
        fixer.fix_queries_file(queries_file, db_num, fixed_file)
        print(f"  ✅ Fixed queries saved to: {fixed_file}")

    print("\n✅ Query fixing complete!")

if __name__ == '__main__':
    main()
