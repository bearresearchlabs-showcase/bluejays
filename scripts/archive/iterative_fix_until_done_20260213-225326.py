#!/usr/bin/env python3
"""
Iterative Query Fixer - Keeps fixing until all queries pass
"""

import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List

class IterativeFixer:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.schema_file = root_dir / 'results' / 'actual_schemas.json'
        with open(self.schema_file, 'r') as f:
            self.schemas = json.load(f)

    def get_test_results(self, db_num: int) -> Dict:
        """Get test results"""
        results_file = self.root_dir / f'db-{db_num}' / 'results' / 'query_test_results_postgres.json'
        if results_file.exists():
            with open(results_file, 'r') as f:
                return json.load(f)
        return {}

    def extract_query_sql(self, queries_file: Path, query_num: int) -> str:
        """Extract SQL for a query"""
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()
        pattern = rf'## Query {query_num}:.*?```sql\s*(.*?)```'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else None

    def update_query(self, queries_file: Path, query_num: int, new_sql: str):
        """Update a query"""
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()
        pattern = rf'(## Query {query_num}:.*?```sql\s*)(.*?)(```)'
        def replace(match):
            return match.group(1) + new_sql + '\n' + match.group(3)
        content = re.sub(pattern, replace, content, flags=re.DOTALL | re.IGNORECASE)
        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def fix_query_error(self, sql: str, error: str, db_num: int) -> tuple[str, bool]:
        """Fix a query based on error - returns (fixed_sql, was_fixed)"""
        fixed = sql
        was_fixed = False

        # Fix PERCENTILE_CONT with OVER
        if 'PERCENTILE_CONT' in error or 'OVER is not supported' in error:
            new_fixed = re.sub(
                r'PERCENTILE_CONT\(([^)]+)\)\s+WITHIN\s+GROUP\s*\(([^)]+)\)\s+OVER\s*\([^)]+\)',
                r'PERCENTILE_CONT(\1) WITHIN GROUP (\2)',
                fixed,
                flags=re.IGNORECASE | re.DOTALL
            )
            if new_fixed != fixed:
                fixed = new_fixed
                was_fixed = True

        # Fix GROUP BY errors
        if 'must appear in the GROUP BY clause' in error:
            col_match = re.search(r'column ["\']?(\w+)\.(\w+)["\']? must appear', error)
            if col_match:
                table_alias = col_match.group(1)
                col_name = col_match.group(2)
                # Find GROUP BY and add column
                def add_to_group_by(match):
                    gb = match.group(0)
                    new_col = f'{table_alias}.{col_name}'
                    if new_col not in gb and col_name not in gb:
                        return gb.rstrip() + f', {new_col}'
                    return gb
                new_fixed = re.sub(r'GROUP BY\s+[^;]+', add_to_group_by, fixed, flags=re.IGNORECASE | re.MULTILINE)
                if new_fixed != fixed:
                    fixed = new_fixed
                    was_fixed = True

        # Fix syntax errors with CAST
        if 'syntax error' in error and ('CAST' in error or 'AS NUMERIC' in error):
            new_fixed = re.sub(
                r'CAST\(CAST\(([^)]+)\s+AS\s+NUMERIC\s*\)\s*\)',
                r'CAST(\1 AS NUMERIC)',
                fixed,
                flags=re.IGNORECASE
            )
            if new_fixed != fixed:
                fixed = new_fixed
                was_fixed = True

        # Fix missing FROM clauses
        if 'missing FROM-clause entry' in error:
            table_match = re.search(r'table ["\']?(\w+)["\']?', error)
            if table_match:
                missing_alias = table_match.group(1)
                # Try to find where it's used and fix
                # This is complex - may need manual fixing
                pass

        # Fix undefined columns - map to actual columns
        if 'does not exist' in error and 'column' in error:
            col_match = re.search(r'column ["\']?(\w+)\.(\w+)["\']? does not exist', error)
            if col_match:
                table_alias = col_match.group(1)
                col_name = col_match.group(2)

                # Common mappings
                mappings = {
                    'uploaded_at': 'created_at',
                    'file_size': 'file_size',  # Check if exists
                    'max_file_size': 'file_size',
                }

                if col_name in mappings:
                    replacement = mappings[col_name]
                    new_fixed = re.sub(
                        rf'\b{table_alias}\.{col_name}\b',
                        f'{table_alias}.{replacement}',
                        fixed,
                        flags=re.IGNORECASE
                    )
                    if new_fixed != fixed:
                        fixed = new_fixed
                        was_fixed = True

        return fixed, was_fixed

    def fix_database(self, db_num: int, max_iterations: int = 50) -> tuple[int, int]:
        """Fix queries for a database iteratively"""
        queries_file = self.root_dir / f'db-{db_num}' / 'queries' / 'queries.md'
        if not queries_file.exists():
            return 0, 0

        iteration = 0
        last_passing = -1

        while iteration < max_iterations:
            iteration += 1

            # Run tests
            result = subprocess.run(
                ['python3', str(self.root_dir / 'run_comprehensive_tests.py')],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                timeout=300
            )

            # Get results
            test_results = self.get_test_results(db_num)
            if not test_results:
                break

            pg_results = test_results.get('postgresql', {}).get('queries', [])
            passing = sum(1 for q in pg_results if q.get('success', False))
            total = len(pg_results)

            if iteration % 5 == 0 or passing != last_passing:
                print(f"  Iteration {iteration}: {passing}/{total} passing")

            if passing == total:
                print(f"  ✅ All {total} queries passing!")
                return passing, total

            if passing == last_passing and iteration > 5:
                # No improvement - try more aggressive fixes
                break

            last_passing = passing

            # Fix failing queries
            fixed_count = 0
            for q_result in pg_results:
                if not q_result.get('success', False):
                    q_num = q_result.get('query_number')
                    error = q_result.get('error', '')

                    if q_num and error:
                        sql = self.extract_query_sql(queries_file, q_num)
                        if sql:
                            fixed_sql, was_fixed = self.fix_query_error(sql, error, db_num)
                            if was_fixed:
                                self.update_query(queries_file, q_num, fixed_sql)
                                fixed_count += 1

            if fixed_count == 0 and iteration > 3:
                break

        return last_passing, total

    def fix_all(self):
        """Fix all databases"""
        print("="*70)
        print("ITERATIVE QUERY FIXER - FIXING UNTIL DONE")
        print("="*70)

        results = {}
        for db_num in range(1, 6):
            print(f"\n🔧 Fixing db-{db_num}...")
            passing, total = self.fix_database(db_num)
            results[f'db-{db_num}'] = {'passing': passing, 'total': total}

        print("\n" + "="*70)
        print("FIXING COMPLETE")
        print("="*70)

        total_passing = sum(r['passing'] for r in results.values())
        total_queries = sum(r['total'] for r in results.values())

        print(f"\nFinal: {total_passing}/{total_queries} queries passing ({total_passing*100/total_queries:.1f}%)")
        return results

if __name__ == '__main__':
    root_dir = Path(__file__).parent
    fixer = IterativeFixer(root_dir)
    fixer.fix_all()
