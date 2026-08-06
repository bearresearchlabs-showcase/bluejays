#!/usr/bin/env python3
"""
Automated Query Debugger - Offloads debugging to hardware/machine
Runs tests, parses errors, applies fixes automatically, iterates until resolved
"""

import json
import re
import time
import psycopg2
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import traceback

# Import query parser from test script
import sys
sys.path.insert(0, str(Path(__file__).parent))
from test_queries_postgres import QueryParser, DatabaseTester

LOG_PATH = Path("/Users/machine/Documents/AQ/db/.cursor/debug.log")
SERVER_ENDPOINT = "http://127.0.0.1:7243/ingest/f36d5adc-fbca-48e9-806c-9a666c5249fd"
SESSION_ID = "debug-session"

def log_debug(hypothesis_id: str, location: str, message: str, data: dict = None):
    """Log debug information"""
    payload = {
        "sessionId": SESSION_ID,
        "runId": "auto-debug",
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
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)

        schema = {}
        for table, col, dtype, nullable in cursor.fetchall():
            if table not in schema:
                schema[table] = {}
            schema[table][col] = dtype

        cursor.close()
        conn.close()
        return schema
    except Exception as e:
        log_debug("H1", "get_schema_info", f"Schema fetch failed: {e}", {"db_num": db_num})
        return {}


class ErrorPatternMatcher:
    """Match error patterns and suggest fixes"""

    PATTERNS = {
        'type_mismatch': [
            (r"operator does not exist: (\w+) (?:>|<|=|>=|<=|!=) (\w+)", "cast_comparison"),
            (r"function (avg|sum|max|min)\((\w+)\) does not exist", "cast_aggregate"),
            (r"CASE types (\w+) and (\w+) cannot be matched", "cast_case"),
            (r"UNION types (\w+) and (\w+) cannot be matched", "cast_union"),
            (r"operator does not exist: (\w+) = (\w+)", "cast_equality"),
        ],
        'missing_column': [
            (r"column \"?([\w.]+)\"? does not exist", "fix_column_reference"),
            (r"column reference \"(\w+)\" is ambiguous", "qualify_column"),
        ],
        'group_by': [
            (r"column \"?([\w.]+)\"? must appear in the GROUP BY clause", "add_to_group_by"),
        ],
        'window_function': [
            (r"column \"?([\w.]+)\"? does not exist.*window", "fix_window_column"),
        ],
    }

    @staticmethod
    def match_error(error_msg: str) -> List[Tuple[str, str, Dict]]:
        """Match error message against patterns and return fixes"""
        matches = []
        for category, patterns in ErrorPatternMatcher.PATTERNS.items():
            for pattern, fix_type in patterns:
                match = re.search(pattern, error_msg, re.IGNORECASE)
                if match:
                    matches.append((category, fix_type, {
                        'pattern': pattern,
                        'match': match,
                        'groups': match.groups(),
                        'full_error': error_msg
                    }))
        return matches


class AutomatedQueryFixer:
    """Automatically fix queries based on errors"""

    def __init__(self, db_num: int, schema: Dict):
        self.db_num = db_num
        self.schema = schema
        self.fix_count = 0

    def fix_type_mismatch(self, sql: str, error_info: Dict) -> str:
        """Fix type mismatches"""
        fixed = sql
        error_msg = error_info['full_error']
        groups = error_info['groups']

        # AVG/SUM on text
        if 'function avg' in error_msg.lower() or 'function sum' in error_msg.lower():
            func_name = re.search(r'function (\w+)\(', error_msg, re.IGNORECASE)
            if func_name:
                func = func_name.group(1).upper()
                col_match = re.search(r'function \w+\((\w+)\)', error_msg, re.IGNORECASE)
                if col_match:
                    col = col_match.group(1)
                    # Find all instances of this function call
                    pattern = rf'{func}\(([^)]*{re.escape(col)}[^)]*)\)'
                    fixed = re.sub(pattern, rf'{func}(CAST(\1 AS NUMERIC))', fixed, flags=re.IGNORECASE)

        # Comparison operators
        if 'operator does not exist' in error_msg:
            # Extract column names from error
            col_match = re.search(r'operator does not exist: (\w+) (?:>|<|=|>=|<=|!=) (\w+)', error_msg)
            if col_match:
                left_type, right_type = col_match.groups()
                # Find the comparison in SQL and cast appropriately
                # This is heuristic - try to cast TEXT to NUMERIC
                if 'text' in left_type.lower() or 'uuid' in left_type.lower():
                    # Find comparisons with this column
                    pattern = rf'(\w+\.?\w*)\s*([><=!]+)\s*(\d+)'
                    def cast_left(m):
                        col_expr = m.group(1)
                        op = m.group(2)
                        val = m.group(3)
                        return f'CAST({col_expr} AS NUMERIC) {op} {val}'
                    fixed = re.sub(pattern, cast_left, fixed)

        # CASE type mismatch
        if 'CASE types' in error_msg:
            # Cast CASE expressions to consistent type
            pattern = r'CASE\s+WHEN\s+([^T]+)\s+THEN\s+([^E]+)\s+ELSE\s+([^E]+)\s+END'
            def cast_case(m):
                condition = m.group(1)
                then_val = m.group(2)
                else_val = m.group(3)
                return f'CASE WHEN {condition} THEN CAST({then_val} AS NUMERIC) ELSE CAST({else_val} AS NUMERIC) END'
            fixed = re.sub(pattern, cast_case, fixed, flags=re.IGNORECASE | re.DOTALL)

        # UNION type mismatch
        if 'UNION types' in error_msg:
            # Find UNION statements and ensure consistent types
            # This is complex - we'll cast all UNION columns to TEXT as safe default
            union_pattern = r'(SELECT\s+[^U]+)\s+UNION\s+(SELECT\s+[^U]+)'
            def cast_union(m):
                left_select = m.group(1)
                right_select = m.group(2)
                # Extract first column from each SELECT
                left_col_match = re.search(r'SELECT\s+([^,\s]+)', left_select, re.IGNORECASE)
                right_col_match = re.search(r'SELECT\s+([^,\s]+)', right_select, re.IGNORECASE)
                if left_col_match and right_col_match:
                    left_col = left_col_match.group(1)
                    right_col = right_col_match.group(1)
                    # Wrap in CAST to TEXT
                    left_select_fixed = re.sub(
                        rf'\b{re.escape(left_col)}\b',
                        f'CAST({left_col} AS TEXT)',
                        left_select,
                        count=1,
                        flags=re.IGNORECASE
                    )
                    right_select_fixed = re.sub(
                        rf'\b{re.escape(right_col)}\b',
                        f'CAST({right_col} AS TEXT)',
                        right_select,
                        count=1,
                        flags=re.IGNORECASE
                    )
                    return f'{left_select_fixed} UNION {right_select_fixed}'
                return m.group(0)
            fixed = re.sub(union_pattern, cast_union, fixed, flags=re.IGNORECASE | re.DOTALL)

        return fixed

    def fix_missing_column(self, sql: str, error_info: Dict) -> str:
        """Fix missing column references"""
        fixed = sql
        error_msg = error_info['full_error']
        groups = error_info['groups']

        if groups:
            missing_col = groups[0]
            # Check if it's a qualified column (table.column)
            if '.' in missing_col:
                table_alias, col_name = missing_col.split('.', 1)
                # Try to find correct column in schema
                for table_name, columns in self.schema.items():
                    if col_name in columns:
                        # Column exists in this table, might be wrong alias
                        # Try common aliases
                        common_aliases = [table_name[:2], table_name[:3], 't1', 't2', 't3']
                        for alias in common_aliases:
                            if f'{alias}.{col_name}' in sql:
                                # Column exists with different alias
                                break
                        else:
                            # Column doesn't exist, try to find similar
                            for col in columns:
                                if col.lower() == col_name.lower() or col_name.lower() in col.lower():
                                    # Replace with correct column
                                    fixed = fixed.replace(missing_col, f'{table_alias}.{col}')
                                    break
            else:
                # Unqualified column - try to qualify it
                # Find all table aliases in query
                alias_pattern = r'FROM\s+(\w+)\s+(\w+)'
                aliases = re.findall(alias_pattern, sql, re.IGNORECASE)
                # Try to find column in schema
                for table_name, columns in self.schema.items():
                    if missing_col in columns:
                        # Found it - qualify with table alias
                        for full_table, alias in aliases:
                            if table_name == full_table:
                                fixed = re.sub(
                                    rf'\b{re.escape(missing_col)}\b',
                                    f'{alias}.{missing_col}',
                                    fixed,
                                    count=1
                                )
                                break

        return fixed

    def fix_ambiguous_column(self, sql: str, error_info: Dict) -> str:
        """Fix ambiguous column references"""
        fixed = sql
        error_msg = error_info['full_error']
        groups = error_info['groups']

        if groups:
            ambiguous_col = groups[0]
            # Find all occurrences and qualify them
            # This is heuristic - qualify with first table alias found
            alias_pattern = r'FROM\s+(\w+)\s+(\w+)'
            aliases = re.findall(alias_pattern, sql, re.IGNORECASE)
            if aliases:
                first_alias = aliases[0][1]
                # Replace unqualified column with qualified
                pattern = rf'(?<!\.)\b{re.escape(ambiguous_col)}\b'
                fixed = re.sub(pattern, f'{first_alias}.{ambiguous_col}', fixed)

        return fixed

    def fix_group_by(self, sql: str, error_info: Dict) -> str:
        """Fix GROUP BY clause issues"""
        fixed = sql
        error_msg = error_info['full_error']
        groups = error_info['groups']

        if groups:
            missing_col = groups[0]
            # Find GROUP BY clause and add missing column
            group_by_pattern = r'(GROUP BY\s+[^,\n]+(?:,\s*[^,\n]+)*)'
            def add_to_group_by(m):
                group_by_clause = m.group(1)
                if missing_col not in group_by_clause:
                    return f'{group_by_clause}, {missing_col}'
                return group_by_clause
            fixed = re.sub(group_by_pattern, add_to_group_by, fixed, flags=re.IGNORECASE)

        return fixed

    def apply_fix(self, sql: str, error_msg: str) -> str:
        """Apply appropriate fix based on error"""
        matches = ErrorPatternMatcher.match_error(error_msg)
        fixed = sql

        for category, fix_type, error_info in matches:
            log_debug("FIX", f"apply_fix_{fix_type}", f"Applying {fix_type}", {
                "category": category,
                "error": error_msg[:200]
            })

            if fix_type == "cast_aggregate" or fix_type == "cast_comparison" or fix_type == "cast_case" or fix_type == "cast_union":
                fixed = self.fix_type_mismatch(fixed, error_info)
            elif fix_type == "fix_column_reference":
                fixed = self.fix_missing_column(fixed, error_info)
            elif fix_type == "qualify_column":
                fixed = self.fix_ambiguous_column(fixed, error_info)
            elif fix_type == "add_to_group_by":
                fixed = self.fix_group_by(fixed, error_info)

            self.fix_count += 1

        return fixed


def test_query_with_fixes(db_num: int, query: Dict[str, str], max_iterations: int = 5) -> Tuple[bool, str, int]:
    """Test query and apply fixes iteratively"""
    schema = get_schema_info(db_num)
    fixer = AutomatedQueryFixer(db_num, schema)

    port = {1: 5432, 2: 5433, 3: 5434, 4: 5435, 5: 5436}[db_num]

    sql = query['sql']
    iterations = 0

    for iteration in range(max_iterations):
        iterations = iteration + 1
        log_debug("TEST", f"test_query_iteration", f"Iteration {iteration}", {
            "query_num": query['number'],
            "db_num": db_num
        })

        try:
            conn = psycopg2.connect(
                host='127.0.0.1', port=port, database=f'db{db_num}',
                user='postgres', password='postgres', connect_timeout=5
            )
            conn.rollback()

            cursor = conn.cursor()
            cursor.execute(sql)
            cursor.fetchmany(10)  # Test execution
            cursor.close()
            conn.close()

            log_debug("SUCCESS", "query_passed", f"Query {query['number']} passed", {
                "query_num": query['number'],
                "iterations": iterations
            })
            return True, sql, iterations

        except psycopg2.Error as e:
            error_msg = str(e)
            log_debug("ERROR", "query_failed", f"Query {query['number']} failed", {
                "query_num": query['number'],
                "error": error_msg[:500],
                "iteration": iteration
            })

            # Apply fixes
            fixed_sql = fixer.apply_fix(sql, error_msg)

            # Check if fix actually changed anything
            if fixed_sql == sql:
                # No fix applied, might need manual intervention
                log_debug("STOP", "no_fix_applied", "No automatic fix available", {
                    "query_num": query['number'],
                    "error": error_msg[:500]
                })
                return False, sql, iterations

            sql = fixed_sql

    # Max iterations reached
    return False, sql, iterations


def debug_database(db_num: int, query_numbers: Optional[List[int]] = None) -> Dict:
    """Debug all queries in a database"""
    root_dir = Path(__file__).parent.parent.parent
    queries_file = root_dir / f'db-{db_num}' / 'queries' / 'queries.md'

    if not queries_file.exists():
        return {"error": f"queries.md not found for db-{db_num}"}

    # Parse queries
    parser = QueryParser()
    queries = parser.extract_queries(queries_file)

    if query_numbers:
        queries = [q for q in queries if q['number'] in query_numbers]

    results = {
        "database": f"db-{db_num}",
        "total_queries": len(queries),
        "fixed": [],
        "failed": [],
        "needs_manual": []
    }

    print(f"\n{'='*70}")
    print(f"Automated Debugging: db-{db_num}")
    print(f"{'='*70}")

    for query in queries:
        print(f"\n🔍 Query {query['number']}: {query['description'][:60]}...")
        success, final_sql, iterations = test_query_with_fixes(db_num, query)

        if success:
            print(f"  ✅ Fixed in {iterations} iteration(s)")
            results["fixed"].append({
                "query_number": query['number'],
                "iterations": iterations
            })

            # Update queries.md with fixed SQL
            if iterations > 0:
                update_query_in_file(queries_file, query['number'], final_sql)
        else:
            print(f"  ❌ Failed after {iterations} iteration(s)")
            results["failed"].append({
                "query_number": query['number'],
                "iterations": iterations
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

        # Find the query section
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

    parser = argparse.ArgumentParser(description='Automated SQL Query Debugger')
    parser.add_argument('--db', type=int, help='Database number (1-5)', required=True)
    parser.add_argument('--queries', type=str, help='Comma-separated query numbers (e.g., 1,2,3)', default=None)
    parser.add_argument('--max-iterations', type=int, default=5, help='Max fix iterations per query')

    args = parser.parse_args()

    query_numbers = None
    if args.queries:
        query_numbers = [int(q.strip()) for q in args.queries.split(',')]

    # Clear log file
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    results = debug_database(args.db, query_numbers)

    # Save results
    root_dir = Path(__file__).parent.parent.parent
    results_file = root_dir / f'db-{args.db}' / 'results' / 'automated_debug_results.json'
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2), encoding='utf-8')

    print(f"\n✅ Results saved to: {results_file}")


if __name__ == '__main__':
    main()
