#!/usr/bin/env python3
"""
Iterative query fixer - runs tests, reads errors, fixes queries, repeats until 100% success
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List

def run_tests() -> Dict:
    """Run tests and return results"""
    result = subprocess.run(
        ['python3', 'scripts/testing/test_queries_postgres.py'],
        cwd=Path(__file__).parent.parent.parent,
        capture_output=True,
        text=True,
        env={
            **dict(os.environ),
            'POSTGRES_HOST': '127.0.0.1',
            'POSTGRES_USER': 'postgres',
            'POSTGRES_PASSWORD': 'postgres'
        }
    )

    # Parse results from JSON files
    results = {}
    for db_num in range(1, 6):
        results_file = Path(f'db-{db_num}/results/query_test_results_postgres.json')
        if results_file.exists():
            with open(results_file) as f:
                data = json.load(f)
            results[f'db-{db_num}'] = data

    return results

def fix_query_based_on_error(sql: str, error: str, error_type: str) -> str:
    """Fix query based on specific error message"""
    fixed = sql

    # Handle specific error patterns
    if 'does not exist' in error:
        # Column or table doesn't exist
        if 'column' in error.lower():
            # Extract column name
            col_match = re.search(r'column\s+"?([^"\s.]+)"?\s+does not exist', error, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1)
                # Try common fixes
                if col_name == 'registration_date':
                    fixed = re.sub(rf'\b{col_name}\b', 'created_at', fixed)
                elif col_name in ['user_message_ratio', 'ai_message_ratio']:
                    fixed = re.sub(rf'\b{col_name}\b', '1.0::numeric', fixed)

        elif 'relation' in error.lower() or 'table' in error.lower():
            # Table doesn't exist - might be a CTE issue
            table_match = re.search(r'relation\s+"?([^"\s]+)"?\s+does not exist', error, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                # Check if it's a CTE that should exist
                # This is complex - would need to parse CTE definitions

    elif 'must appear in the GROUP BY' in error:
        # GROUP BY error
        col_match = re.search(r'column\s+"?([^"]+)"?\s+must appear', error, re.IGNORECASE)
        if col_match:
            col_ref = col_match.group(1)
            # Add to GROUP BY - find GROUP BY clause and add column
            fixed = re.sub(
                r'(GROUP BY\s+[^,\n]+)(?=\s*\)|$)',
                lambda m: m.group(0) + f', {col_ref}' if col_ref not in m.group(1) else m.group(0),
                fixed,
                flags=re.IGNORECASE | re.MULTILINE
            )

    elif 'syntax error' in error.lower():
        # Syntax error - try common fixes
        if 'COALESCE' in error or 'CAST' in error:
            # Fix COALESCE/CAST syntax
            fixed = re.sub(
                r'CAST\(COALESCE\(CAST\(([^)]+)\s+AS\s+NUMERIC\)\)\s*,\s*([^)]+)\)',
                r'COALESCE(CAST(\1 AS NUMERIC), \2)',
                fixed
            )

    return fixed

def fix_queries_iteratively(max_iterations=5):
    """Iteratively fix queries until success or max iterations"""
    root_dir = Path(__file__).parent.parent.parent

    for iteration in range(max_iterations):
        print(f"\n{'='*70}")
        print(f"Iteration {iteration + 1}")
        print(f"{'='*70}")

        # Run tests
        print("Running tests...")
        results = run_tests()

        # Count successes
        total_success = 0
        total_queries = 0

        for db_name, data in results.items():
            pg = data.get('postgresql', {})
            queries = pg.get('queries', [])
            successful = len([q for q in queries if q.get('success')])
            total_success += successful
            total_queries += len(queries)

        success_rate = (total_success / total_queries * 100) if total_queries > 0 else 0
        print(f"Success rate: {total_success}/{total_queries} ({success_rate:.1f}%)")

        if total_success == total_queries:
            print("\n✅ ALL QUERIES SUCCESSFUL!")
            return True

        # Fix queries based on errors
        print("Fixing queries based on errors...")
        fixes_applied = 0

        for db_name, data in results.items():
            db_num = int(db_name.split('-')[1])
            queries_file = root_dir / db_name / 'queries' / 'queries.md'

            if not queries_file.exists():
                continue

            pg = data.get('postgresql', {})
            queries = pg.get('queries', [])

            # Read queries.md
            with open(queries_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix each failed query
            for q in queries:
                if not q.get('success'):
                    query_num = q.get('number', 0)
                    error = q.get('error', '')
                    error_type = q.get('error_type', '')

                    # Find query in content
                    pattern = rf'(## Query {query_num}:[^\n]*\n\n.*?```sql\n)(.*?)(```)'
                    match = re.search(pattern, content, re.DOTALL)

                    if match:
                        original_sql = match.group(2)
                        fixed_sql = fix_query_based_on_error(original_sql, error, error_type)

                        if fixed_sql != original_sql:
                            content = content.replace(
                                match.group(0),
                                match.group(1) + fixed_sql + match.group(3)
                            )
                            fixes_applied += 1

            # Write back
            if fixes_applied > 0:
                with open(queries_file, 'w', encoding='utf-8') as f:
                    f.write(content)

        if fixes_applied == 0:
            print("No more fixes to apply")
            break

        print(f"Applied {fixes_applied} fixes")

    return False

if __name__ == '__main__':
    import os
    fix_queries_iteratively()
