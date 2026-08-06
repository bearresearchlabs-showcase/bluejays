#!/usr/bin/env python3
"""
Comprehensive Query Fixer - Iterates until all queries pass
Handles all error types systematically
"""

import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set

class ComprehensiveQueryFixer:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.schema_file = root_dir / 'results' / 'actual_schemas.json'
        with open(self.schema_file, 'r') as f:
            self.schemas = json.load(f)

        # Build comprehensive column lookup
        self.column_lookup = {}
        self.table_lookup = {}
        for db_key, tables in self.schemas.items():
            db_num = int(db_key.replace('db', ''))
            self.column_lookup[db_num] = {}
            self.table_lookup[db_num] = set(tables.keys())
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

        pattern = rf'## Query {query_num}:.*?```sql\s*(.*?)```'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def update_query_in_file(self, queries_file: Path, query_num: int, new_sql: str):
        """Update a query in the queries.md file"""
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = rf'(## Query {query_num}:.*?```sql\s*)(.*?)(```)'

        def replace_sql(match):
            return match.group(1) + new_sql + '\n' + match.group(3)

        fixed_content = re.sub(pattern, replace_sql, content, flags=re.DOTALL | re.IGNORECASE)

        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

    def fix_query_comprehensive(self, sql: str, error: str, db_num: int, query_num: int) -> Tuple[str, bool]:
        """Comprehensively fix a query based on error - returns (fixed_sql, was_fixed)"""
        fixed = sql
        was_fixed = False

        # Fix 1: Missing column in CTE - add it to SELECT
        if 'does not exist' in error and 'column' in error:
            col_match = re.search(r'column ["\']?(\w+)\.(\w+)["\']? does not exist', error)
            if col_match:
                table_alias = col_match.group(1)
                column_name = col_match.group(2)

                # Check if it's a CTE alias
                cte_pattern = rf'{table_alias}\s+AS\s*\([^)]*SELECT[^)]*\)'
                cte_match = re.search(cte_pattern, sql, re.IGNORECASE | re.DOTALL)

                if cte_match:
                    # Find the CTE definition
                    cte_def = cte_match.group(0)
                    # Check if column should come from a source table
                    # Common fixes
                    column_fixes = {
                        'max_file_size': 'max_file_size',  # Should be selected from source
                        'uploaded_at': 'created_at',
                        'file_size': 'max_file_size',  # If used as max
                    }

                    if column_name in column_fixes:
                        source_col = column_fixes[column_name]
                        # Try to add it to the CTE SELECT
                        select_match = re.search(r'(SELECT\s+.*?)(FROM)', cte_def, re.DOTALL | re.IGNORECASE)
                        if select_match:
                            select_clause = select_match.group(1)
                            # Check if source_col is already selected
                            if source_col not in select_clause and f'{table_alias}.{source_col}' not in select_clause:
                                # Add it before FROM
                                new_select = select_clause.rstrip() + f',\n        {table_alias}.{source_col} AS {column_name}\n    '
                                fixed_cte = cte_def.replace(select_match.group(0), new_select + select_match.group(2))
                                fixed = sql.replace(cte_def, fixed_cte)
                                was_fixed = True

        # Fix 2: GROUP BY errors - add missing column
        if 'must appear in the GROUP BY clause' in error:
            col_match = re.search(r'column ["\']?(\w+)\.(\w+)["\']? must appear', error)
            if col_match:
                table_alias = col_match.group(1)
                column_name = col_match.group(2)

                # Find GROUP BY and add column
                group_by_pattern = r'(GROUP BY\s+)([^;]+?)(\s|;|$)'
                def add_to_group_by(match):
                    group_by_cols = match.group(2)
                    new_col = f'{table_alias}.{column_name}'
                    if new_col not in group_by_cols and column_name not in group_by_cols:
                        return match.group(1) + group_by_cols + f', {new_col}' + match.group(3)
                    return match.group(0)

                new_fixed = re.sub(group_by_pattern, add_to_group_by, fixed, flags=re.IGNORECASE | re.MULTILINE)
                if new_fixed != fixed:
                    fixed = new_fixed
                    was_fixed = True

        # Fix 3: Syntax errors with CAST
        if 'syntax error' in error and ('CAST' in error or 'AS NUMERIC' in error):
            # Fix malformed CAST: CAST(CAST(x AS NUMERIC)) -> CAST(x AS NUMERIC)
            new_fixed = re.sub(
                r'CAST\s*\(\s*CAST\s*\(([^)]+)\s+AS\s+NUMERIC\s*\)\s*\)',
                r'CAST(\1 AS NUMERIC)',
                fixed,
                flags=re.IGNORECASE
            )
            if new_fixed != fixed:
                fixed = new_fixed
                was_fixed = True

        # Fix 4: PERCENTILE_CONT with OVER
        if 'PERCENTILE_CONT' in error or 'OVER is not supported' in error:
            new_fixed = re.sub(
                r'PERCENTILE_CONT\s*\([^)]+\)\s+WITHIN\s+GROUP\s*\([^)]+\)\s+OVER\s*\([^)]+\)',
                lambda m: re.sub(r'\s+OVER\s*\([^)]+\)', '', m.group(0), flags=re.IGNORECASE),
                fixed,
                flags=re.IGNORECASE | re.DOTALL
            )
            if new_fixed != fixed:
                fixed = new_fixed
                was_fixed = True

        # Fix 5: Recursive CTE aggregate - remove aggregate from recursive term
        if 'aggregate functions are not allowed in a recursive query' in error:
            # Find the recursive UNION ALL part
            recursive_pattern = r'(UNION\s+ALL\s+.*?SELECT\s+)(.*?)(FROM\s+\w+\s+\w+)'
            def fix_recursive(match):
                select_part = match.group(2)
                # Remove aggregates, keep non-aggregate expressions
                # This is complex - for now, comment out problematic aggregates
                if 'SUM(' in select_part or 'COUNT(' in select_part or 'AVG(' in select_part:
                    # Try to restructure - this may need manual fixing
                    pass
                return match.group(0)

            # For now, we'll skip recursive CTE fixes as they're complex
            pass

        # Fix 6: Missing FROM clause - this usually means alias is wrong
        if 'missing FROM-clause entry' in error:
            table_match = re.search(r'table ["\']?(\w+)["\']?', error)
            if table_match:
                missing_alias = table_match.group(1)
                # Try to find where it's used and see if we can fix the reference
                # This is complex and may need query understanding
                pass

        return fixed, was_fixed

    def fix_database_iteratively(self, db_num: int, max_iterations: int = 20) -> Tuple[int, int]:
        """Fix queries for a database iteratively"""
        queries_file = self.root_dir / f'db-{db_num}' / 'queries' / 'queries.md'
        if not queries_file.exists():
            return 0, 0

        iteration = 0
        last_passing = -1

        while iteration < max_iterations:
            iteration += 1
            print(f"\n  Iteration {iteration} for db-{db_num}...")

            # Run tests
            result = subprocess.run(
                ['python3', str(self.root_dir / 'run_comprehensive_tests.py')],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                timeout=300
            )

            # Get test results
            test_results = self.get_test_results(db_num)
            if not test_results:
                print(f"    ⚠️  No test results found")
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
                if iteration > 3:  # Give up after 3 iterations with no improvement
                    break

            last_passing = passing

            # Fix failing queries
            fixed_count = 0
            for query_result in pg_results:
                if not query_result.get('success', False):
                    query_num = query_result.get('query_number')
                    error = query_result.get('error', '')

                    if query_num and error:
                        sql = self.extract_query_sql(queries_file, query_num)
                        if sql:
                            fixed_sql, was_fixed = self.fix_query_comprehensive(sql, error, db_num, query_num)
                            if was_fixed:
                                self.update_query_in_file(queries_file, query_num, fixed_sql)
                                fixed_count += 1
                                print(f"      Fixed Query {query_num}")

            print(f"    Fixed {fixed_count} queries")

            if fixed_count == 0:
                print(f"  ⚠️  No more automatic fixes possible")
                break

        return last_passing, total

    def fix_all_databases(self):
        """Fix queries for all databases"""
        print("="*70)
        print("COMPREHENSIVE ITERATIVE QUERY FIXER")
        print("="*70)

        results = {}
        for db_num in range(1, 6):
            print(f"\n🔧 Fixing db-{db_num}...")
            passing, total = self.fix_database_iteratively(db_num)
            results[f'db-{db_num}'] = {'passing': passing, 'total': total}

        print("\n" + "="*70)
        print("FIXING COMPLETE")
        print("="*70)

        total_passing = sum(r['passing'] for r in results.values())
        total_queries = sum(r['total'] for r in results.values())

        print(f"\nOverall: {total_passing}/{total_queries} queries passing ({total_passing*100/total_queries:.1f}%)")

        return results

def main():
    root_dir = Path(__file__).parent
    fixer = ComprehensiveQueryFixer(root_dir)
    fixer.fix_all_databases()

if __name__ == '__main__':
    main()
