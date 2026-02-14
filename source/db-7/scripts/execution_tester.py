#!/usr/bin/env python3
"""
Execution testing script for db-7 queries - PostgreSQL
Phase 3: Execution Testing for db-7 Maritime Shipping Intelligence Database
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from typing import Dict, List

# Add root scripts directory to path for timestamp_utils
root_scripts = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(root_scripts))
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    # Fallback if timestamp_utils not available
    from datetime import datetime
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

# Database connection imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

class QueryParser:
    """Parse queries from queries.md"""

    @staticmethod
    def extract_queries(md_file: Path) -> List[Dict]:
        """Extract queries from markdown file"""
        queries = []
        if not md_file.exists():
            return queries

        content = md_file.read_text(encoding='utf-8')
        query_header_pattern = r'^## Query (\d+):\s*(.+)$'
        headers = list(re.finditer(query_header_pattern, content, re.MULTILINE))

        for i, header_match in enumerate(headers):
            query_num = int(header_match.group(1))
            title = header_match.group(2).strip()
            start_pos = header_match.start()

            if i + 1 < len(headers):
                end_pos = headers[i + 1].start()
            else:
                end_pos = len(content)

            query_section = content[start_pos:end_pos]
            sql_pattern = r'```(?:sql)?\n(.*?)```'
            sql_match = re.search(sql_pattern, query_section, re.DOTALL)

            if sql_match:
                sql = sql_match.group(1).strip()
                queries.append({
                    'number': query_num,
                    'title': title,
                    'sql': sql
                })

        return sorted(queries, key=lambda x: x['number'])

class DatabaseTester:
    """Test queries against PostgreSQL"""

    def __init__(self, db_name: str, db_num: int):
        self.db_name = db_name
        self.db_num = db_num
        self.pg_conn = None
        self.db_conn = None
        self.results = {
            'database': db_name,
            'test_date': get_est_timestamp(),  # EST format: YYYYMMDD-HHMM
            'postgresql': {'available': False, 'queries': []},
            'summary': {}
        }

    def get_postgres_connection(self):
        """Get PostgreSQL connection"""
        if not PG_AVAILABLE:
            return None

        try:
            return psycopg2.connect(
                host=os.environ.get('POSTGRES_HOST', os.environ.get('PG_HOST', 'localhost')),
                port=int(os.environ.get('POSTGRES_PORT', os.environ.get('PG_PORT', 5432))),
                user=os.environ.get('POSTGRES_USER', os.environ.get('PG_USER', 'postgres')),
                password=os.environ.get('POSTGRES_PASSWORD', os.environ.get('PG_PASSWORD', '')),
                database=os.environ.get('POSTGRES_DB', os.environ.get('PG_DATABASE', f'db{self.db_num}'))
            )
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
            return None

    def test_query_postgres(self, query: Dict) -> Dict:
        """Test a single query on PostgreSQL"""
        result = {
            'query_number': query['number'],
            'success': False,
            'execution_time_ms': None,
            'row_count': None,
            'columns': [],
            'error': None
        }

        if not self.pg_conn:
            result['error'] = 'PostgreSQL not connected'
            return result

        try:
            # Add LIMIT to prevent large result sets
            sql_with_limit = query['sql']
            if 'LIMIT' not in sql_with_limit.upper() and 'FETCH' not in sql_with_limit.upper():
                sql_with_limit = f"{sql_with_limit.rstrip(';')} LIMIT 100"

            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            start_time = time.time()
            cursor.execute(sql_with_limit)
            rows = cursor.fetchall()
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            result['success'] = True
            result['execution_time_ms'] = round(execution_time, 2)
            result['row_count'] = len(rows)
            if rows:
                result['columns'] = list(rows[0].keys()) if isinstance(rows[0], dict) else []

            cursor.close()
        except Exception as e:
            result['error'] = str(e)
            # Rollback transaction on error to allow subsequent queries to run
            try:
                self.pg_conn.rollback()
            except:
                pass

        return result

    def test_all_queries(self, queries: List[Dict]):
        """Test all queries on available databases"""
        print("\n" + "="*70)
        print("Execution Testing")
        print("="*70)

        # Test PostgreSQL
        self.pg_conn = self.get_postgres_connection()
        if self.pg_conn:
            self.results['postgresql']['available'] = True
            print(f"\nTesting on PostgreSQL...")
            for query in queries:
                print(f"  Query {query['number']}/{len(queries)}...", end=' ', flush=True)
                result = self.test_query_postgres(query)
                self.results['postgresql']['queries'].append(result)
                if result['success']:
                    print(f"✓ ({result['execution_time_ms']:.0f}ms, {result['row_count']} rows)")
                else:
                    print(f"✗ {result['error'][:50]}")
            self.pg_conn.close()
        else:
            print("\n⚠️  PostgreSQL not available. Skipping PostgreSQL testing.")

        # Calculate summary
        total_queries = len(queries)
        self.results['summary'] = {
            'total_queries': total_queries,
            'postgresql': {
                'tested': len(self.results['postgresql']['queries']),
                'successful': sum(1 for q in self.results['postgresql']['queries'] if q['success']),
                'failed': sum(1 for q in self.results['postgresql']['queries'] if not q['success']),
                'success_rate': round((sum(1 for q in self.results['postgresql']['queries'] if q['success']) / len(self.results['postgresql']['queries']) * 100), 2) if self.results['postgresql']['queries'] else 0
            }
        }

    def save_results(self, output_file: Path):
        """Save test results to JSON file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(self.results, indent=2, default=str, ensure_ascii=False))

def main():
    """Main execution testing function"""
    script_dir = Path(__file__).parent
    queries_file = script_dir.parent / 'queries' / 'queries.md'
    results_file = script_dir.parent / 'results' / 'query_test_results_postgres.json'

    if not queries_file.exists():
        print(f"Error: {queries_file} not found")
        return

    print("="*70)
    print("Execution Testing for db-7 Maritime Shipping Intelligence queries.md")
    print("="*70)

    # Extract queries
    parser = QueryParser()
    queries = parser.extract_queries(queries_file)

    print(f"\nExtracted {len(queries)} queries")

    # Set PostgreSQL environment variables if not already set
    if not os.environ.get('POSTGRES_HOST'):
        os.environ['POSTGRES_HOST'] = os.environ.get('PG_HOST', 'localhost')
    if not os.environ.get('POSTGRES_PORT'):
        os.environ['POSTGRES_PORT'] = os.environ.get('PG_PORT', '5432')
    if not os.environ.get('POSTGRES_USER'):
        os.environ['POSTGRES_USER'] = os.environ.get('PG_USER', os.environ.get('USER', 'postgres'))
    if not os.environ.get('POSTGRES_PASSWORD'):
        os.environ['POSTGRES_PASSWORD'] = os.environ.get('PG_PASSWORD', 'postgres')
    if not os.environ.get('POSTGRES_DB'):
        os.environ['POSTGRES_DB'] = os.environ.get('PG_DATABASE', 'db7')

    print(f"\nPostgreSQL Configuration:")
    print(f"  Host: {os.environ.get('POSTGRES_HOST')}")
    print(f"  Port: {os.environ.get('POSTGRES_PORT')}")
    print(f"  User: {os.environ.get('POSTGRES_USER')}")
    print(f"  Database: {os.environ.get('POSTGRES_DB')}")

    # Test queries
    tester = DatabaseTester('db-7', 7)
    tester.test_all_queries(queries)
    tester.save_results(results_file)

    # Note: Execution testing is optional - proceed even if databases aren't available
    pg_available = tester.results['postgresql']['available']
    
    if not pg_available:
        print("\n⚠️  No databases available for execution testing (optional phase)")
        print("   Execution testing skipped - validation can proceed without it")

    # Print summary
    print("\n" + "="*70)
    print("Execution Testing Summary")
    print("="*70)
    summary = tester.results['summary']
    print(f"\nTotal Queries: {summary['total_queries']}")
    
    if tester.results['postgresql']['available']:
        pg_summary = summary['postgresql']
        print(f"\nPostgreSQL:")
        print(f"  Tested: {pg_summary['tested']}")
        print(f"  Successful: {pg_summary['successful']}")
        print(f"  Failed: {pg_summary['failed']}")
        print(f"  Success Rate: {pg_summary['success_rate']:.2f}%")

    print("\n" + "="*70)
    print(f"Results saved to: {results_file}")
    print("="*70)

if __name__ == '__main__':
    main()
