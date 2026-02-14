#!/usr/bin/env python3
"""
Comprehensive SQL Query Testing Framework
Tests all queries from queries.md files against PostgreSQL and Snowflake
Generates detailed JSON results files
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import traceback

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  psycopg2 not available. PostgreSQL testing will be skipped.")

try:
    import snowflake.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    print("⚠️  snowflake-connector-python not available. Snowflake testing will be skipped.")


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

        # Also find SQL code blocks
        sql_pattern = r'```sql\s*(.*?)```'
        sql_blocks = list(re.finditer(sql_pattern, content, re.DOTALL | re.IGNORECASE))

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
                        break

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
            'snowflake': {'available': SNOWFLAKE_AVAILABLE, 'queries': []}
        }

    def get_postgres_connection(self):
        """Get PostgreSQL connection"""
        if not POSTGRES_AVAILABLE:
            return None

        # Try to get connection from environment or use defaults
        import os
        conn_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', f'db{self.db_num}'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
        }

        try:
            return psycopg2.connect(**conn_params)
        except Exception as e:
            print(f"⚠️  PostgreSQL connection failed: {e}")
            return None

    def get_snowflake_connection(self):
        """Get Snowflake connection"""
        if not SNOWFLAKE_AVAILABLE:
            return None

        import os
        conn_params = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT', ''),
            'user': os.getenv('SNOWFLAKE_USER', ''),
            'password': os.getenv('SNOWFLAKE_PASSWORD', ''),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            'database': os.getenv('SNOWFLAKE_DATABASE', f'DB{self.db_num}'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC'),
            'role': os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
        }

        # Check if credentials are available
        if not all([conn_params['account'], conn_params['user'], conn_params['password']]):
            print(f"⚠️  Snowflake credentials not configured. Set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD")
            return None

        try:
            return snowflake.connector.connect(**conn_params)
        except Exception as e:
            print(f"⚠️  Snowflake connection failed: {e}")
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

    def test_query_snowflake(self, query: Dict[str, str], conn) -> Dict:
        """Test a single query against Snowflake"""
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
            result['error'] = 'Snowflake connection not available'
            return result

        try:
            start_time = time.time()
            cursor = conn.cursor()

            # Execute query
            cursor.execute(query['sql'])

            # Fetch results (limit to first 1000 rows)
            rows = cursor.fetchmany(1000)
            result['row_count'] = len(rows)

            # Get column names
            if cursor.description:
                result['columns'] = [desc[0] for desc in cursor.description]

            # Check if there are more rows
            if cursor.fetchone():
                result['truncated'] = True
                result['note'] = 'Results truncated to first 1000 rows'

            cursor.close()

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

        # Test Snowflake
        if SNOWFLAKE_AVAILABLE:
            print(f"\n❄️  Testing Snowflake...")
            sf_conn = self.get_snowflake_connection()
            if sf_conn:
                for query in queries:
                    result = self.test_query_snowflake(query, sf_conn)
                    self.results['snowflake']['queries'].append(result)
                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} Query {query['number']}: {result['execution_time_ms']:.2f}ms, {result['row_count']} rows")
                    if not result['success']:
                        print(f"     Error: {result['error']}")
                sf_conn.close()
            else:
                print("  ⚠️  Snowflake connection not available")
        else:
            print("  ⚠️  Snowflake testing skipped (snowflake-connector-python not installed)")

        # Calculate statistics
        self._calculate_statistics()

    def _calculate_statistics(self):
        """Calculate test statistics"""
        for db_type in ['postgresql', 'snowflake']:
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
    root_dir = Path('.')

    print("="*70)
    print("COMPREHENSIVE SQL QUERY TESTING FRAMEWORK")
    print("="*70)
    print(f"\nPostgreSQL available: {POSTGRES_AVAILABLE}")
    print(f"Snowflake available: {SNOWFLAKE_AVAILABLE}")

    if not POSTGRES_AVAILABLE and not SNOWFLAKE_AVAILABLE:
        print("\n⚠️  No database connectors available. Install:")
        print("   pip install psycopg2-binary snowflake-connector-python")
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
        results_file = db_dir / 'results' / 'query_test_results_postgres_snowflake.json'
        tester.save_results(results_file)

    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
