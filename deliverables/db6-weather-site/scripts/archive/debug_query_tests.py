#!/usr/bin/env python3
"""
Debug Instrumentation Script for SQL Query Testing
Logs detailed error information to identify and fix query issues
"""

import re
import json
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# #region agent log
import urllib.request
import urllib.parse
# #endregion

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Debug logging configuration
LOG_PATH = Path("/Users/machine/Documents/AQ/db/.cursor/debug.log")
SERVER_ENDPOINT = "http://127.0.0.1:7243/ingest/f36d5adc-fbca-48e9-806c-9a666c5249fd"
SESSION_ID = "debug-session"

def log_debug(hypothesis_id: str, location: str, message: str, data: dict = None):
    """Log debug information"""
    payload = {
        "sessionId": SESSION_ID,
        "runId": "run1",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000)
    }

    # Write to file (NDJSON format)
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(payload) + '\n')
    except Exception as e:
        print(f"Failed to write log: {e}")

    # Also send via HTTP
    try:
        req = urllib.request.Request(
            SERVER_ENDPOINT,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=1)
    except:
        pass  # Ignore HTTP errors

class QueryParser:
    """Parse queries from queries.md files"""

    @staticmethod
    def extract_queries(markdown_file: Path) -> List[Dict[str, str]]:
        """Extract all SQL queries from a queries.md file"""
        # #region agent log
        log_debug("H1", f"{markdown_file}:extract_queries", "Starting query extraction", {"file": str(markdown_file)})
        # #endregion

        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        queries = []

        # Pattern to match query sections: ## Query N: Description
        query_pattern = r'## Query (\d+):\s*(.+?)(?=## Query \d+:|```sql|$)'
        query_matches = list(re.finditer(query_pattern, content, re.DOTALL | re.IGNORECASE))

        # #region agent log
        log_debug("H1", f"{markdown_file}:extract_queries", "Found query headers", {"count": len(query_matches)})
        # #endregion

        # Also find SQL code blocks (exclude test sections)
        sql_pattern = r'```sql\s*(.*?)```'
        sql_blocks = []
        for match in re.finditer(sql_pattern, content, re.DOTALL | re.IGNORECASE):
            sql_content = match.group(1).strip()
            # Skip test sections that contain ellipsis or test comments
            if '-- Test' in sql_content or sql_content.count('...') > 2:
                continue
            sql_blocks.append(match)

        # #region agent log
        log_debug("H1", f"{markdown_file}:extract_queries", "Found SQL blocks", {"count": len(sql_blocks)})
        # #endregion

        # Match queries with their SQL blocks
        for i, query_match in enumerate(query_matches):
            query_num = int(query_match.group(1))
            description = query_match.group(2).strip()

            # Find the SQL block that follows this query description
            query_start = query_match.end()
            sql_block = None

            # #region agent log
            log_debug("H1", f"{markdown_file}:extract_queries", "Matching query header to SQL block", {
                "query_num": query_num,
                "query_start_pos": query_start,
                "total_sql_blocks": len(sql_blocks)
            })
            # #endregion

            # Find the next SQL block after this query header
            for sql_idx, sql_match in enumerate(sql_blocks):
                # #region agent log
                log_debug("H1", f"{markdown_file}:extract_queries", "Checking SQL block", {
                    "query_num": query_num,
                    "sql_idx": sql_idx,
                    "sql_start_pos": sql_match.start(),
                    "query_start_pos": query_start,
                    "is_after_query": sql_match.start() > query_start
                })
                # #endregion

                if sql_match.start() > query_start:
                    # Check if there's a closer query header between this header and the SQL block
                    has_closer_header = False
                    for j, other_match in enumerate(query_matches):
                        if other_match.start() > query_start and other_match.start() < sql_match.start():
                            has_closer_header = True
                            break

                    # #region agent log
                    log_debug("H1", f"{markdown_file}:extract_queries", "Checked for closer header", {
                        "query_num": query_num,
                        "sql_idx": sql_idx,
                        "has_closer_header": has_closer_header
                    })
                    # #endregion

                    if not has_closer_header:
                        sql_block = sql_match.group(1).strip()

                        # #region agent log
                        log_debug("H1", f"{markdown_file}:extract_queries", "Found potential SQL block", {
                            "query_num": query_num,
                            "sql_preview": sql_block[:200],
                            "ends_with_semicolon": sql_block.endswith(';'),
                            "length": len(sql_block)
                        })
                        # #endregion

                        # Remove ellipsis, test sections, and incomplete lines
                        lines = sql_block.split('\n')
                        cleaned_lines = []
                        skip_rest = False
                        for line in lines:
                            # Stop at test sections
                            if '-- Test' in line or 'Test Execution' in line:
                                skip_rest = True
                                break
                            # Skip lines with just "..." or incomplete code
                            if line.strip() == '...' or (line.strip().startswith('--') and '...' in line):
                                continue
                            # Skip lines that are just ellipsis in comments
                            if re.match(r'^\s*--\s*\.\.\.\s*$', line):
                                continue
                            cleaned_lines.append(line)

                        sql_block = '\n'.join(cleaned_lines).strip()

                        # #region agent log
                        log_debug("H1", f"{markdown_file}:extract_queries", "After cleaning SQL block", {
                            "query_num": query_num,
                            "sql_preview": sql_block[:200],
                            "ends_with_semicolon": sql_block.endswith(';'),
                            "length": len(sql_block),
                            "skipped": skip_rest
                        })
                        # #endregion

                        # Use if it's a complete query (ends with semicolon or is substantial)
                        if sql_block and not skip_rest and (sql_block.endswith(';') or len(sql_block) > 100):
                            # Ensure it ends with semicolon
                            if not sql_block.endswith(';'):
                                sql_block = sql_block.rstrip() + ';'
                            # #region agent log
                            log_debug("H1", f"{markdown_file}:extract_queries", "SQL block accepted", {
                                "query_num": query_num,
                                "final_length": len(sql_block)
                            })
                            # #endregion
                            break
                        else:
                            # #region agent log
                            log_debug("H1", f"{markdown_file}:extract_queries", "SQL block rejected", {
                                "query_num": query_num,
                                "reason": "empty" if not sql_block else ("skipped" if skip_rest else ("no_semicolon" if not sql_block.endswith(';') else "too_short"))
                            })
                            # #endregion
                            sql_block = None

            if sql_block:
                queries.append({
                    'number': query_num,
                    'description': description,
                    'sql': sql_block
                })

                # #region agent log
                log_debug("H1", f"{markdown_file}:extract_queries", "Extracted query", {"query_num": query_num, "sql_length": len(sql_block)})
                # #endregion

        # #region agent log
        log_debug("H1", f"{markdown_file}:extract_queries", "Query extraction complete", {"total_queries": len(queries)})
        # #endregion

        return sorted(queries, key=lambda x: x['number'])


class DatabaseTester:
    """Test SQL queries against databases with detailed logging"""

    def __init__(self, db_name: str, db_num: int):
        self.db_name = db_name
        self.db_num = db_num
        self.results = {
            'database': db_name,
            'database_number': db_num,
            'test_timestamp': datetime.now().isoformat(),
            'postgresql': {'available': POSTGRES_AVAILABLE, 'queries': []}
        }

    def get_postgres_connection(self):
        """Get PostgreSQL connection"""
        if not POSTGRES_AVAILABLE:
            return None

        import os
        port_mapping = {1: 5432, 2: 5433, 3: 5434, 4: 5435, 5: 5436}
        default_port = port_mapping.get(self.db_num, 5432)

        host = os.getenv('POSTGRES_HOST', 'localhost')
        if host == 'localhost':
            host = '127.0.0.1'

        db_specific_port = os.getenv(f'POSTGRES_PORT_DB{self.db_num}')
        if db_specific_port:
            port = int(db_specific_port)
        else:
            port = default_port

        conn_params = {
            'host': host,
            'port': port,
            'database': os.getenv('POSTGRES_DB', f'db{self.db_num}'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'connect_timeout': 10
        }

        # #region agent log
        log_debug("H2", f"{self.db_name}:get_postgres_connection", "Attempting connection", {"host": host, "port": port, "database": conn_params['database']})
        # #endregion

        try:
            conn = psycopg2.connect(**conn_params)
            # #region agent log
            log_debug("H2", f"{self.db_name}:get_postgres_connection", "Connection successful", {})
            # #endregion
            return conn
        except Exception as e:
            # #region agent log
            log_debug("H2", f"{self.db_name}:get_postgres_connection", "Connection failed", {"error": str(e)})
            # #endregion
            return None

    def test_query_postgres(self, query: Dict[str, str], conn) -> Dict:
        """Test a single query against PostgreSQL with detailed error logging"""
        query_num = query['number']

        # #region agent log
        log_debug("H3", f"{self.db_name}:test_query_postgres", "Starting query test", {"query_num": query_num, "sql_preview": query['sql'][:100]})
        # #endregion

        result = {
            'query_number': query_num,
            'description': query['description'],
            'success': False,
            'execution_time_ms': 0,
            'row_count': 0,
            'error': None,
            'error_type': None,
            'error_line': None,
            'error_column': None
        }

        if not conn:
            result['error'] = 'PostgreSQL connection not available'
            # #region agent log
            log_debug("H3", f"{self.db_name}:test_query_postgres", "No connection available", {"query_num": query_num})
            # #endregion
            return result

        try:
            start_time = time.time()
            conn.rollback()

            # #region agent log
            log_debug("H4", f"{self.db_name}:test_query_postgres", "Before query execution", {"query_num": query_num})
            # #endregion

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query['sql'])

                # #region agent log
                log_debug("H4", f"{self.db_name}:test_query_postgres", "Query executed successfully", {"query_num": query_num})
                # #endregion

                rows = cursor.fetchmany(1000)
                result['row_count'] = len(rows)

                if rows:
                    result['columns'] = list(rows[0].keys())

                if cursor.fetchone():
                    result['truncated'] = True

            result['execution_time_ms'] = (time.time() - start_time) * 1000
            result['success'] = True

            # #region agent log
            log_debug("H4", f"{self.db_name}:test_query_postgres", "Query succeeded", {"query_num": query_num, "row_count": result['row_count'], "execution_time_ms": result['execution_time_ms']})
            # #endregion

        except psycopg2.Error as e:
            error_msg = str(e)
            result['error'] = error_msg
            result['error_type'] = type(e).__name__
            result['execution_time_ms'] = (time.time() - start_time) * 1000

            # Extract line number from error message
            line_match = re.search(r'LINE (\d+):', error_msg)
            if line_match:
                result['error_line'] = int(line_match.group(1))

            # Extract column info
            col_match = re.search(r'column "([^"]+)"', error_msg)
            if col_match:
                result['error_column'] = col_match.group(1)

            # #region agent log
            log_debug("H5", f"{self.db_name}:test_query_postgres", "Query failed", {
                "query_num": query_num,
                "error": error_msg,
                "error_type": result['error_type'],
                "error_line": result.get('error_line'),
                "error_column": result.get('error_column'),
                "sql_lines": query['sql'].split('\n')[:result.get('error_line', 0) + 5] if result.get('error_line') else []
            })
            # #endregion

        except Exception as e:
            error_msg = str(e)
            result['error'] = error_msg
            result['error_type'] = type(e).__name__
            result['execution_time_ms'] = (time.time() - start_time) * 1000

            # #region agent log
            log_debug("H5", f"{self.db_name}:test_query_postgres", "Query failed with exception", {
                "query_num": query_num,
                "error": error_msg,
                "error_type": result['error_type'],
                "traceback": traceback.format_exc()
            })
            # #endregion

        return result

    def test_all_queries(self, queries: List[Dict[str, str]]):
        """Test all queries against PostgreSQL with detailed logging"""
        # #region agent log
        log_debug("H1", f"{self.db_name}:test_all_queries", "Starting test suite", {"total_queries": len(queries)})
        # #endregion

        if POSTGRES_AVAILABLE:
            pg_conn = self.get_postgres_connection()
            if pg_conn:
                for query in queries:
                    result = self.test_query_postgres(query, pg_conn)
                    self.results['postgresql']['queries'].append(result)

                    # #region agent log
                    log_debug("H6", f"{self.db_name}:test_all_queries", "Query result", {
                        "query_num": result['query_number'],
                        "success": result['success'],
                        "error": result.get('error'),
                        "error_line": result.get('error_line'),
                        "error_column": result.get('error_column')
                    })
                    # #endregion

                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} Query {query['number']}: {result['execution_time_ms']:.2f}ms")
                    if not result['success']:
                        print(f"     Error: {result['error'][:200]}")
                pg_conn.close()

                # #region agent log
                successful = sum(1 for q in self.results['postgresql']['queries'] if q['success'])
                failed = len(self.results['postgresql']['queries']) - successful
                log_debug("H6", f"{self.db_name}:test_all_queries", "Test suite complete", {
                    "total": len(queries),
                    "successful": successful,
                    "failed": failed,
                    "success_rate": (successful / len(queries) * 100) if queries else 0
                })
                # #endregion

    def save_results(self, output_path: Path):
        """Save results to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)


def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    root_dir = script_dir

    print("="*70)
    print("DEBUG SQL QUERY TESTING - INSTRUMENTED")
    print("="*70)
    print(f"\nPostgreSQL available: {POSTGRES_AVAILABLE}")
    print(f"Log file: {LOG_PATH}")

    if not POSTGRES_AVAILABLE:
        print("\n⚠️  PostgreSQL connector not available. Install: pip install psycopg2-binary")
        return

    # Test databases 2-5 (db-1 already passes)
    for db_num in [2, 3, 4, 5]:
        db_dir = root_dir / f'db-{db_num}'
        queries_file = db_dir / 'queries' / 'queries.md'

        if not queries_file.exists():
            print(f"\n⚠️  Skipping db-{db_num}: queries.md not found")
            continue

        print(f"\n📖 Testing db-{db_num}...")
        parser = QueryParser()
        queries = parser.extract_queries(queries_file)

        if not queries:
            print(f"  ⚠️  No queries found")
            continue

        print(f"  ✅ Found {len(queries)} queries")

        tester = DatabaseTester(f'db-{db_num}', db_num)
        tester.test_all_queries(queries)

        results_file = db_dir / 'results' / 'query_test_results_postgres.json'
        tester.save_results(results_file)
        print(f"  ✅ Results saved")

    print("\n" + "="*70)
    print("DEBUG TESTING COMPLETE")
    print("="*70)
    print(f"\nLog file: {LOG_PATH}")


if __name__ == '__main__':
    main()
