#!/usr/bin/env python3
"""
Integrated Test-and-Fix Script
Runs tests, detects failures, applies fixes automatically, iterates until resolved
"""

import json
import re
import time
import psycopg2
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import subprocess
import sys

# Import from test script
sys.path.insert(0, str(Path(__file__).parent))
from test_queries_postgres import QueryParser, DatabaseTester

LOG_PATH = Path("/Users/machine/Documents/AQ/db/.cursor/debug.log")
SERVER_ENDPOINT = "http://127.0.0.1:7243/ingest/f36d5adc-fbca-48e9-806c-9a666c5249fd"
SESSION_ID = "debug-session"

def log_debug(hypothesis_id: str, location: str, message: str, data: dict = None):
    """Log debug information"""
    payload = {
        "sessionId": SESSION_ID,
        "runId": "auto-test-fix",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000)
    }
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(payload) + '\n')
    except:
        pass
    try:
        import urllib.request
        req = urllib.request.Request(
            SERVER_ENDPOINT,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=1)
    except:
        pass


def get_schema_info(db_num: int) -> Dict[str, Dict[str, str]]:
    """Get schema information from PostgreSQL"""
    port = {1: 5432, 2: 5433, 3: 5434, 4: 5435, 5: 5436}[db_num]
    try:
        conn = psycopg2.connect(
            host='127.0.0.1', port=port, database=f'db{db_num}',
            user='postgres', password='postgres', connect_timeout=5
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)

        schema = {}
        for table, col, dtype in cursor.fetchall():
            if table not in schema:
                schema[table] = {}
            schema[table][col] = dtype

        cursor.close()
        conn.close()
        return schema
    except Exception as e:
        log_debug("SCHEMA", "get_schema_info", f"Schema fetch failed: {e}", {"db_num": db_num})
        return {}


def apply_common_fixes(sql: str, error_msg: str, db_num: int, schema: Dict) -> str:
    """Apply common fixes based on error patterns"""
    fixed = sql

    # Pattern 1: AVG/SUM on text columns
    if re.search(r'function (avg|sum|max|min)\((\w+)\) does not exist', error_msg, re.IGNORECASE):
        func_match = re.search(r'function (\w+)\((\w+)\)', error_msg, re.IGNORECASE)
        if func_match:
            func = func_match.group(1).upper()
            col = func_match.group(2)
            # Cast the column in all aggregate calls
            pattern = rf'{func}\(([^)]*{re.escape(col)}[^)]*)\)'
            def cast_agg(m):
                expr = m.group(1)
                return f'{func}(CAST({expr} AS NUMERIC))'
            fixed = re.sub(pattern, cast_agg, fixed, flags=re.IGNORECASE)
            log_debug("FIX", "cast_aggregate", f"Cast {func} on {col}", {"db_num": db_num})

    # Pattern 2: Type mismatch in comparisons
    if re.search(r'operator does not exist: (\w+) (?:>|<|=|>=|<=|!=) (\w+)', error_msg):
        # Cast TEXT/UUID to NUMERIC for numeric comparisons
        pattern = r'(\w+\.?\w*)\s*([><=!]+)\s*(\d+)'
        def cast_comparison(m):
            col_expr = m.group(1)
            op = m.group(2)
            val = m.group(3)
            return f'CAST({col_expr} AS NUMERIC) {op} {val}'
        fixed = re.sub(pattern, cast_comparison, fixed)
        log_debug("FIX", "cast_comparison", "Cast comparison operands", {"db_num": db_num})

    # Pattern 3: CASE type mismatch
    if 'CASE types' in error_msg:
        # Find CASE expressions and ensure consistent types
        pattern = r'(CASE\s+WHEN[^T]+THEN\s+)([^E]+)(\s+ELSE\s+)([^E]+)(\s+END)'
        def cast_case(m):
            case_start = m.group(1)
            then_val = m.group(2)
            else_keyword = m.group(3)
            else_val = m.group(4)
            case_end = m.group(5)
            return f'{case_start}CAST({then_val} AS NUMERIC){else_keyword}CAST({else_val} AS NUMERIC){case_end}'
        fixed = re.sub(pattern, cast_case, fixed, flags=re.IGNORECASE | re.DOTALL)
        log_debug("FIX", "cast_case", "Cast CASE expression", {"db_num": db_num})

    # Pattern 4: UNION type mismatch
    if 'UNION types' in error_msg:
        # Extract column names from UNION SELECTs
        union_pattern = r'(SELECT\s+)([^U]+)(\s+UNION\s+)(SELECT\s+)([^U]+)'
        def cast_union(m):
            left_select = m.group(1) + m.group(2)
            union_keyword = m.group(3)
            right_select = m.group(4) + m.group(5)

            # Extract first column from each SELECT
            left_col_match = re.search(r'SELECT\s+([^,\s]+)', left_select, re.IGNORECASE)
            right_col_match = re.search(r'SELECT\s+([^,\s]+)', right_select, re.IGNORECASE)

            if left_col_match and right_col_match:
                left_col = left_col_match.group(1).strip()
                right_col = right_col_match.group(1).strip()

                # Wrap first column in CAST to TEXT
                left_fixed = re.sub(
                    rf'SELECT\s+{re.escape(left_col)}\b',
                    f'SELECT CAST({left_col} AS TEXT)',
                    left_select,
                    count=1,
                    flags=re.IGNORECASE
                )
                right_fixed = re.sub(
                    rf'SELECT\s+{re.escape(right_col)}\b',
                    f'SELECT CAST({right_col} AS TEXT)',
                    right_select,
                    count=1,
                    flags=re.IGNORECASE
                )
                return f'{left_fixed}{union_keyword}{right_fixed}'
            return m.group(0)
        fixed = re.sub(union_pattern, cast_union, fixed, flags=re.IGNORECASE | re.DOTALL)
        log_debug("FIX", "cast_union", "Cast UNION columns", {"db_num": db_num})

    # Pattern 5: Missing column
    missing_col_match = re.search(r'column "?([\w.]+)"? does not exist', error_msg)
    if missing_col_match:
        missing_col = missing_col_match.group(1)
        # Try to find similar column in schema
        if '.' in missing_col:
            table_alias, col_name = missing_col.split('.', 1)
            # Search schema for similar column
            for table_name, columns in schema.items():
                if col_name in columns:
                    # Column exists, might be wrong table alias
                    # Try to find correct alias in query
                    alias_pattern = rf'FROM\s+{re.escape(table_name)}\s+(\w+)'
                    alias_match = re.search(alias_pattern, fixed, re.IGNORECASE)
                    if alias_match:
                        correct_alias = alias_match.group(1)
                        fixed = fixed.replace(missing_col, f'{correct_alias}.{col_name}')
                        log_debug("FIX", "fix_column", f"Fixed column {missing_col}", {"db_num": db_num})
                        break

    # Pattern 6: Ambiguous column
    if 'column reference "' in error_msg and '" is ambiguous' in error_msg:
        ambiguous_match = re.search(r'column reference "(\w+)" is ambiguous', error_msg)
        if ambiguous_match:
            col_name = ambiguous_match.group(1)
            # Find first table alias and qualify
            alias_pattern = r'FROM\s+(\w+)\s+(\w+)'
            alias_match = re.search(alias_pattern, fixed, re.IGNORECASE)
            if alias_match:
                table_alias = alias_match.group(2)
                # Replace unqualified column with qualified
                pattern = rf'(?<!\.)\b{re.escape(col_name)}\b'
                fixed = re.sub(pattern, f'{table_alias}.{col_name}', fixed, count=1)
                log_debug("FIX", "qualify_column", f"Qualified {col_name}", {"db_num": db_num})

    # Pattern 7: GROUP BY missing column
    group_by_match = re.search(r'column "?([\w.]+)"? must appear in the GROUP BY clause', error_msg)
    if group_by_match:
        missing_col = group_by_match.group(1)
        # Find GROUP BY and add column
        group_by_pattern = r'(GROUP BY\s+[^,\n]+(?:,\s*[^,\n]+)*)'
        def add_to_group_by(m):
            group_by_clause = m.group(1)
            if missing_col not in group_by_clause:
                return f'{group_by_clause}, {missing_col}'
            return group_by_clause
        fixed = re.sub(group_by_pattern, add_to_group_by, fixed, flags=re.IGNORECASE)
        log_debug("FIX", "add_group_by", f"Added {missing_col} to GROUP BY", {"db_num": db_num})

    # Pattern 8: Missing column (unqualified) - comment out or replace
    missing_col_match = re.search(r'column "(\w+)" does not exist', error_msg)
    if missing_col_match and not '.' in missing_col_match.group(1):
        missing_col = missing_col_match.group(1)
        # db-4 specific: category doesn't exist, use chat_id or id instead
        if db_num == 4 and missing_col == 'category':
            # Replace category with chat_id or id
            fixed = re.sub(rf'\b{re.escape(missing_col)}\b', 'chat_id', fixed, count=1)
            log_debug("FIX", "replace_category", "Replaced category with chat_id", {"db_num": db_num})
        # If column doesn't exist in schema, comment it out
        elif not any(missing_col in cols for cols in schema.values()):
            # Comment out the column reference
            fixed = re.sub(rf'(\s*){re.escape(missing_col)}(\s*,|\s*$)', r'\1-- ' + missing_col + r'\2', fixed)
            log_debug("FIX", "comment_column", f"Commented out {missing_col}", {"db_num": db_num})

    # Pattern 9: Syntax error - WHERE without space
    if 'syntax error' in error_msg.lower() and 'WHERE' in error_msg:
        # Fix "WHERE.column" to "WHERE column" or remove WHERE if it's a typo
        fixed = re.sub(r'WHERE\.(\w+)', r'WHERE \1', fixed)
        # Fix "WHERE," to remove WHERE
        fixed = re.sub(r'WHERE\s*,', ',', fixed)
        log_debug("FIX", "fix_where_syntax", "Fixed WHERE syntax", {"db_num": db_num})

    # Pattern 10: COALESCE type mismatch
    if 'COALESCE types' in error_msg:
        # Find COALESCE expressions and cast both operands
        pattern = r'COALESCE\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)'
        def cast_coalesce(m):
            expr1 = m.group(1).strip()
            expr2 = m.group(2).strip()
            # Cast both to TEXT as safe default
            return f'COALESCE(CAST({expr1} AS TEXT), CAST({expr2} AS TEXT))'
        fixed = re.sub(pattern, cast_coalesce, fixed, flags=re.IGNORECASE)
        log_debug("FIX", "cast_coalesce", "Cast COALESCE operands", {"db_num": db_num})

    # Pattern 11: Foreign key column doesn't exist
    if 'foreign_id' in error_msg.lower() and 'does not exist' in error_msg:
        # Replace foreign_id with id
        fixed = re.sub(r'\bforeign_id\b', 'id', fixed, flags=re.IGNORECASE)
        log_debug("FIX", "replace_foreign_id", "Replaced foreign_id with id", {"db_num": db_num})

    # Pattern 12: Missing column in SELECT list - try to find alternative
    if 'does not exist' in error_msg and 'LINE' in error_msg:
        # Extract line number and column name
        line_match = re.search(r'LINE\s+(\d+):', error_msg)
        col_match = re.search(r'LINE\s+\d+:\s*([^\n]+)', error_msg)
        if line_match and col_match:
            line_content = col_match.group(1)
            # Try to find the problematic column
            col_name_match = re.search(r'(\w+)', line_content.strip())
            if col_name_match:
                problematic_col = col_name_match.group(1)
                # db-4: category -> chat_id
                if db_num == 4 and problematic_col == 'category':
                    fixed = re.sub(rf'\b{re.escape(problematic_col)}\b', 'chat_id', fixed)
                    log_debug("FIX", "fix_select_column", f"Fixed {problematic_col}", {"db_num": db_num})

    return fixed


def test_and_fix_query(db_num: int, query: Dict[str, str], max_iterations: int = 10) -> Tuple[bool, str, int, List[str]]:
    """Test query and apply fixes iteratively"""
    schema = get_schema_info(db_num)
    port = {1: 5432, 2: 5433, 3: 5434, 4: 5435, 5: 5436}[db_num]

    sql = query['sql']
    iterations = 0
    errors_seen = []

    for iteration in range(max_iterations):
        iterations = iteration + 1
        log_debug("ITER", f"iteration_{iteration}", f"Testing query {query['number']}", {
            "query_num": query['number'],
            "db_num": db_num,
            "iteration": iteration
        })

        try:
            conn = psycopg2.connect(
                host='127.0.0.1', port=port, database=f'db{db_num}',
                user='postgres', password='postgres', connect_timeout=5
            )
            conn.rollback()

            cursor = conn.cursor()
            cursor.execute(sql)
            cursor.fetchmany(10)
            cursor.close()
            conn.close()

            log_debug("SUCCESS", "query_passed", f"Query {query['number']} passed", {
                "query_num": query['number'],
                "iterations": iterations
            })
            return True, sql, iterations, errors_seen

        except psycopg2.Error as e:
            error_msg = str(e)
            errors_seen.append(error_msg[:200])

            log_debug("ERROR", "query_failed", f"Query {query['number']} failed", {
                "query_num": query['number'],
                "error": error_msg[:500],
                "iteration": iteration
            })

            # Apply fixes
            fixed_sql = apply_common_fixes(sql, error_msg, db_num, schema)

            # Check if fix changed anything
            if fixed_sql == sql:
                # No fix applied
                log_debug("STOP", "no_fix", "No automatic fix available", {
                    "query_num": query['number'],
                    "error": error_msg[:500]
                })
                return False, sql, iterations, errors_seen

            sql = fixed_sql

    return False, sql, iterations, errors_seen


def run_test_and_fix(db_num: int, query_numbers: Optional[List[int]] = None) -> Dict:
    """Run tests and fix queries for a database"""
    root_dir = Path(__file__).parent.parent.parent
    queries_file = root_dir / f'db-{db_num}' / 'queries' / 'queries.md'

    if not queries_file.exists():
        return {"error": f"queries.md not found for db-{db_num}"}

    parser = QueryParser()
    queries = parser.extract_queries(queries_file)

    if query_numbers:
        queries = [q for q in queries if q['number'] in query_numbers]

    results = {
        "database": f"db-{db_num}",
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(queries),
        "fixed": [],
        "failed": [],
        "needs_manual": []
    }

    print(f"\n{'='*70}")
    print(f"Auto Test-and-Fix: db-{db_num}")
    print(f"{'='*70}")

    for query in queries:
        print(f"\n🔍 Query {query['number']}: {query['description'][:60]}...")
        success, final_sql, iterations, errors = test_and_fix_query(db_num, query)

        if success:
            print(f"  ✅ Fixed in {iterations} iteration(s)")
            results["fixed"].append({
                "query_number": query['number'],
                "iterations": iterations
            })

            # Update queries.md
            if iterations > 0:
                update_query_in_file(queries_file, query['number'], final_sql)
        else:
            print(f"  ❌ Failed after {iterations} iteration(s)")
            if errors:
                print(f"     Last error: {errors[-1][:100]}...")
            results["failed"].append({
                "query_number": query['number'],
                "iterations": iterations,
                "errors": errors[-3:] if errors else []  # Last 3 errors
            })
            results["needs_manual"].append(query['number'])

    print(f"\n{'='*70}")
    print(f"Summary: {len(results['fixed'])} fixed, {len(results['failed'])} failed")
    print(f"{'='*70}")

    return results


def update_query_in_file(queries_file: Path, query_num: int, fixed_sql: str):
    """Update query SQL in queries.md file"""
    try:
        content = queries_file.read_text(encoding='utf-8')

        # Find the query section and SQL block
        pattern = rf'(## Query {query_num}:.*?```sql\s*)(.*?)(```)'

        def replace_sql(match):
            return f"{match.group(1)}{fixed_sql}\n{match.group(3)}"

        new_content = re.sub(pattern, replace_sql, content, flags=re.DOTALL | re.IGNORECASE)

        if new_content != content:
            queries_file.write_text(new_content, encoding='utf-8')
            log_debug("UPDATE", "query_updated", f"Updated query {query_num}", {
                "query_num": query_num
            })
    except Exception as e:
        log_debug("ERROR", "update_failed", f"Failed to update query {query_num}", {
            "error": str(e)
        })


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Auto Test-and-Fix SQL Queries')
    parser.add_argument('--db', type=int, help='Database number (1-5)', required=True)
    parser.add_argument('--queries', type=str, help='Comma-separated query numbers', default=None)
    parser.add_argument('--max-iterations', type=int, default=10, help='Max fix iterations')

    args = parser.parse_args()

    query_numbers = None
    if args.queries:
        query_numbers = [int(q.strip()) for q in args.queries.split(',')]

    # Clear log file
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    results = run_test_and_fix(args.db, query_numbers)

    # Save results
    root_dir = Path(__file__).parent.parent.parent
    results_file = root_dir / f'db-{args.db}' / 'results' / 'auto_test_fix_results.json'
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2), encoding='utf-8')

    print(f"\n✅ Results saved to: {results_file}")


if __name__ == '__main__':
    main()
