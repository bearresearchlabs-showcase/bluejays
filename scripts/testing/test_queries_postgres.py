#!/usr/bin/env python3
"""
Comprehensive SQL Query Testing Framework
Tests all queries from queries.md files against PostgreSQL
Generates detailed JSON results files
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import traceback
import urllib.request

# Debug logging
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
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(payload) + '\n')
    except:
        pass
    try:
        req = urllib.request.Request(
            SERVER_ENDPOINT,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=1)
    except:
        pass

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  psycopg2 not available. PostgreSQL testing will be skipped.")

class QueryParser:
    """Parse queries from queries.md files"""

    @staticmethod
    def extract_queries(markdown_file: Path) -> List[Dict[str, str]]:
        """Extract all SQL queries from a queries.md file"""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        queries = []

        # Pattern to match query sections: ## Query N: Description
        query_pattern = r'## Query (\d+):\s*(.+?)(?=## Query \d+:|```sql|$)'
        query_matches = list(re.finditer(query_pattern, content, re.DOTALL | re.IGNORECASE))

        # Also find SQL code blocks (exclude test sections)
        # Match SQL blocks but exclude those in test sections
        sql_pattern = r'```sql\s*(.*?)```'
        sql_blocks = []
        for match in re.finditer(sql_pattern, content, re.DOTALL | re.IGNORECASE):
            sql_content = match.group(1).strip()
            # Skip test sections that contain ellipsis or test comments
            if '-- Test' in sql_content or sql_content.count('...') > 2:
                continue
            sql_blocks.append(match)

        # Match queries with their SQL blocks
        for i, query_match in enumerate(query_matches):
            query_num = int(query_match.group(1))
            description = query_match.group(2).strip()

            # Find the SQL block that follows this query description
            query_start = query_match.end()
            sql_block = None

            # Find the next SQL block after this query header
            for sql_match in sql_blocks:
                if sql_match.start() > query_start:
                    # Check if there's a closer query header between this header and the SQL block
                    has_closer_header = False
                    for j, other_match in enumerate(query_matches):
                        if other_match.start() > query_start and other_match.start() < sql_match.start():
                            has_closer_header = True
                            break

                    if not has_closer_header:
                        sql_block = sql_match.group(1).strip()
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
                        # Only use if it's a complete query (ends with semicolon)
                        if sql_block and sql_block.endswith(';'):
                            break
                        else:
                            sql_block = None

            if sql_block:
                queries.append({
                    'number': query_num,
                    'description': description,
                    'sql': sql_block
                })

        # If no structured queries found, extract all SQL blocks
        if not queries and sql_blocks:
            for i, sql_match in enumerate(sql_blocks, 1):
                queries.append({
                    'number': i,
                    'description': f'Query {i}',
                    'sql': sql_match.group(1).strip()
                })

        return sorted(queries, key=lambda x: x['number'])


class DatabaseTester:
    """Test SQL queries against databases"""

    def __init__(self, db_name: str, db_num: int):
        self.db_name = db_name
        self.db_num = db_num
        self.results = {
            'database': db_name,
            'database_number': db_num,
            'test_timestamp': datetime.now().isoformat(),
            'postgresql': {'available': POSTGRES_AVAILABLE, 'queries': []},
        }

    def get_postgres_connection(self):
        """Get PostgreSQL connection"""
        if not POSTGRES_AVAILABLE:
            return None

        # Try to get connection from environment or use defaults
        import os
        # Map database numbers to ports: db1=5432, db2=5433, etc.
        port_mapping = {
            1: 5432,
            2: 5433,
            3: 5434,
            4: 5435,
            5: 5436
        }
        default_port = port_mapping.get(self.db_num, 5432)

        host = os.getenv('POSTGRES_HOST', 'localhost')
        # Force IPv4 if localhost to avoid IPv6 issues
        if host == 'localhost':
            host = '127.0.0.1'

        # Always use port mapping per database (don't override with env var)
        # Only use env var if it's set per-database (e.g., POSTGRES_PORT_DB1)
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

        try:
            return psycopg2.connect(**conn_params)
        except Exception as e:
            print(f"⚠️  PostgreSQL connection failed: {e}")
            return None

    def test_query_postgres(self, query: Dict[str, str], conn) -> Dict:
        """Test a single query against PostgreSQL"""
        result = {
            'query_number': query['number'],
            'description': query['description'],
            'success': False,
            'execution_time_ms': 0,
            'row_count': 0,
            'error': None,
            'error_type': None
        }

        if not conn:
            result['error'] = 'PostgreSQL connection not available'
            return result

        try:
            start_time = time.time()
            # Rollback any previous failed transaction
            conn.rollback()

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query['sql'])

                # Fetch results (limit to first 1000 rows for performance)
                rows = cursor.fetchmany(1000)
                result['row_count'] = len(rows)

                # Get column names
                if rows:
                    result['columns'] = list(rows[0].keys())

                # Check if there are more rows
                if cursor.fetchone():
                    result['truncated'] = True
                    result['note'] = 'Results truncated to first 1000 rows'

            result['execution_time_ms'] = (time.time() - start_time) * 1000
            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            result['execution_time_ms'] = (time.time() - start_time) * 1000

        return result

    def test_all_queries(self, queries: List[Dict[str, str]]):
        """Test all queries against both databases"""
        print(f"\n{'='*70}")
        print(f"Testing {len(queries)} queries for {self.db_name}")
        print(f"{'='*70}")

        # Test PostgreSQL
        if POSTGRES_AVAILABLE:
            print(f"\n📊 Testing PostgreSQL...")
            pg_conn = self.get_postgres_connection()
            if pg_conn:
                for query in queries:
                    result = self.test_query_postgres(query, pg_conn)
                    self.results['postgresql']['queries'].append(result)
                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} Query {query['number']}: {result['execution_time_ms']:.2f}ms, {result['row_count']} rows")
                    if not result['success']:
                        print(f"     Error: {result['error']}")
                pg_conn.close()
            else:
                print("  ⚠️  PostgreSQL connection not available")
        else:
            print("  ⚠️  PostgreSQL testing skipped (psycopg2 not installed)")

        # Calculate statistics
        self._calculate_statistics()

    def _calculate_statistics(self):
        """Calculate test statistics"""
        for db_type in ['postgresql']:
            queries = self.results[db_type].get('queries', [])
            if queries:
                successful = [q for q in queries if q['success']]
                failed = [q for q in queries if not q['success']]

                self.results[db_type]['statistics'] = {
                    'total_queries': len(queries),
                    'successful': len(successful),
                    'failed': len(failed),
                    'success_rate': len(successful) / len(queries) * 100 if queries else 0,
                    'avg_execution_time_ms': sum(q['execution_time_ms'] for q in successful) / len(successful) if successful else 0,
                    'total_rows_returned': sum(q['row_count'] for q in successful)
                }

    def save_results(self, output_path: Path):
        """Save results to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n✅ Results saved to: {output_path}")


def main():
    """Main execution"""
    # Get script directory and navigate to repo root
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent

    print("="*70)
    print("COMPREHENSIVE SQL QUERY TESTING FRAMEWORK")
    print("="*70)
    print(f"\nPostgreSQL available: {POSTGRES_AVAILABLE}")

    if not POSTGRES_AVAILABLE:
        print("\n⚠️  No database connectors available. Install:")
        print("   pip install psycopg2-binary")
        return

    # Test each database
    for db_num in range(1, 6):
        db_dir = root_dir / f'db-{db_num}'
        queries_file = db_dir / 'queries' / 'queries.md'

        if not queries_file.exists():
            print(f"\n⚠️  Skipping db-{db_num}: queries.md not found")
            continue

        # Parse queries
        print(f"\n📖 Parsing queries from db-{db_num}...")
        parser = QueryParser()
        queries = parser.extract_queries(queries_file)

        if not queries:
            print(f"  ⚠️  No queries found in {queries_file}")
            continue

        print(f"  ✅ Found {len(queries)} queries")

        # Test queries
        tester = DatabaseTester(f'db-{db_num}', db_num)
        tester.test_all_queries(queries)

        # Save results
        results_file = db_dir / 'results' / 'query_test_results_postgres.json'
        tester.save_results(results_file)

    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
