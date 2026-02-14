#!/usr/bin/env python3
"""
Iterative Query Fixer
Reads test results, fixes errors, re-tests until all queries pass
"""

import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class IterativeQueryFixer:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.schema_file = root_dir / 'results' / 'actual_schemas.json'
        with open(self.schema_file, 'r') as f:
            self.schemas = json.load(f)

        # Build column lookup
        self.column_lookup = {}
        for db_key, tables in self.schemas.items():
            db_num = int(db_key.replace('db', ''))
            self.column_lookup[db_num] = {}
            for table_name, columns in tables.items():
                self.column_lookup[db_num][table_name] = {c['name'] for c in columns}

    def get_test_results(self, db_num: int) -> Dict:
        """Get test results for a database"""
        results_file = self.root_dir / f'db-{db_num}' / 'results' / 'query_test_results_postgres.json'
        if results_file.exists():
            with open(results_file, 'r') as f:
                return json.load(f)
        return {}

    def extract_query_sql(self, queries_file: Path, query_num: int) -> str:
        """Extract SQL for a specific query number"""
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find query section
        pattern = rf'## Query {query_num}:.*?```sql\s*(.*?)```'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def fix_query_based_on_error(self, sql: str, error: str, db_num: int) -> str:
        """Fix a query based on its error message"""
        fixed = sql

        # Fix 1: Undefined column errors
        if 'does not exist' in error and 'column' in error:
            # Extract column name from error
            col_match = re.search(r'column ["\']?(\w+)\.(\w+)["\']? does not exist', error)
            if col_match:
                table_alias = col_match.group(1)
                column_name = col_match.group(2)

                # Try to find the column in actual schema
                # Common fixes
                column_fixes = {
                    'uploaded_at': 'created_at',
                    'max_file_size': 'file_size',  # For file_attachments
                }

                if column_name in column_fixes:
                    fixed = re.sub(
                        rf'\b{table_alias}\.{column_name}\b',
                        f'{table_alias}.{column_fixes[column_name]}',
                        fixed,
                        flags=re.IGNORECASE
                    )

        # Fix 2: GROUP BY errors
        if 'must appear in the GROUP BY clause' in error:
            # Extract column from error
            col_match = re.search(r'column ["\']?(\w+)\.(\w+)["\']? must appear', error)
            if col_match:
                table_alias = col_match.group(1)
                column_name = col_match.group(2)

                # Find GROUP BY clause and add column
                # This is complex - we'll add it to the end of GROUP BY
                group_by_pattern = r'(GROUP BY\s+[^;]+)'
                def add_to_group_by(match):
                    group_by = match.group(1)
                    if f'{table_alias}.{column_name}' not in group_by:
                        return group_by + f', {table_alias}.{column_name}'
                    return group_by

                fixed = re.sub(group_by_pattern, add_to_group_by, fixed, flags=re.IGNORECASE)

        # Fix 3: Missing FROM clause
        if 'missing FROM-clause entry' in error:
            # Extract table alias
            table_match = re.search(r'table ["\']?(\w+)["\']?', error)
            if table_match:
                table_alias = table_match.group(1)
                # This usually means the alias is used but not defined
                # We need to understand the query structure to fix this
                # For now, we'll try to find where it's used and comment it out or fix it
                pass  # Complex - requires query understanding

        # Fix 4: Syntax errors with CAST
        if 'syntax error' in error and 'CAST' in error:
            # Fix malformed CAST expressions
            fixed = re.sub(
                r'CAST\s*\(\s*CAST\s*\(([^)]+)\s+AS\s+NUMERIC\s*\)\s*\)\s*\)',
                r'CAST(\1 AS NUMERIC)',
                fixed,
                flags=re.IGNORECASE
            )

        # Fix 5: PERCENTILE_CONT with OVER
        if 'PERCENTILE_CONT' in error or 'OVER is not supported' in error:
            fixed = re.sub(
                r'PERCENTILE_CONT\s*\([^)]+\)\s+WITHIN\s+GROUP\s*\([^)]+\)\s+OVER\s*\([^)]+\)',
                lambda m: re.sub(r'\s+OVER\s*\([^)]+\)', '', m.group(0), flags=re.IGNORECASE),
                fixed,
                flags=re.IGNORECASE | re.DOTALL
            )

        # Fix 6: Recursive CTE aggregate errors
        if 'aggregate functions are not allowed in a recursive query' in error:
            # This requires restructuring - for now, we'll comment out the problematic part
            # This is complex and may require manual fixing
            pass

        return fixed

    def update_query_in_file(self, queries_file: Path, query_num: int, new_sql: str):
        """Update a query in the queries.md file"""
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace the SQL for this query
        pattern = rf'(## Query {query_num}:.*?```sql\s*)(.*?)(```)'

        def replace_sql(match):
            return match.group(1) + new_sql + '\n' + match.group(3)

        fixed_content = re.sub(pattern, replace_sql, content, flags=re.DOTALL | re.IGNORECASE)

        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

    def fix_database_queries(self, db_num: int, max_iterations: int = 10) -> Tuple[int, int]:
        """Fix queries for a database iteratively"""
        queries_file = self.root_dir / f'db-{db_num}' / 'queries' / 'queries.md'
        if not queries_file.exists():
            return 0, 0

        iteration = 0
        last_passing = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"\n  Iteration {iteration} for db-{db_num}...")

            # Run tests
            result = subprocess.run(
                ['python3', str(self.root_dir / 'run_comprehensive_tests.py')],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True
            )

            # Get test results
            test_results = self.get_test_results(db_num)
            if not test_results:
                break

            pg_results = test_results.get('postgresql', {}).get('queries', [])
            passing = sum(1 for q in pg_results if q.get('success', False))
            total = len(pg_results)

            print(f"    Passing: {passing}/{total}")

            if passing == total:
                print(f"  ✅ All queries passing for db-{db_num}!")
                return passing, total

            if passing == last_passing:
                print(f"  ⚠️  No improvement (still {passing}/{total} passing)")
                # Try more aggressive fixes
                break

            last_passing = passing

            # Fix failing queries
            fixed_count = 0
            for query_result in pg_results:
                if not query_result.get('success', False):
                    query_num = query_result.get('query_number')
                    error = query_result.get('error', '')

                    if query_num:
                        sql = self.extract_query_sql(queries_file, query_num)
                        if sql:
                            fixed_sql = self.fix_query_based_on_error(sql, error, db_num)
                            if fixed_sql != sql:
                                self.update_query_in_file(queries_file, query_num, fixed_sql)
                                fixed_count += 1

            print(f"    Fixed {fixed_count} queries")

            if fixed_count == 0:
                print(f"  ⚠️  No more automatic fixes possible")
                break

        return last_passing, total

    def fix_all_databases(self):
        """Fix queries for all databases"""
        print("="*70)
        print("ITERATIVE QUERY FIXER")
        print("="*70)

        results = {}
        for db_num in range(1, 6):
            print(f"\n🔧 Fixing db-{db_num}...")
            passing, total = self.fix_database_queries(db_num)
            results[f'db-{db_num}'] = {'passing': passing, 'total': total}

        print("\n" + "="*70)
        print("FIXING COMPLETE")
        print("="*70)

        total_passing = sum(r['passing'] for r in results.values())
        total_queries = sum(r['total'] for r in results.values())

        print(f"\nOverall: {total_passing}/{total_queries} queries passing")

        return results

def main():
    root_dir = Path(__file__).parent
    fixer = IterativeQueryFixer(root_dir)
    fixer.fix_all_databases()

if __name__ == '__main__':
    main()
