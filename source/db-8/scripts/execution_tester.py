#!/usr/bin/env python3
"""
Execution testing script for db-8 queries
Phase 3: Execution Testing
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import traceback

# Import timestamp utility (try local first, then root scripts)
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    # Try importing from root scripts directory
    root_scripts = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(root_scripts))
    from timestamp_utils import get_est_timestamp

# Database connection imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False
    print("Warning: psycopg2 not available. PostgreSQL testing will be skipped.")

class QueryExtractor:
    """Extract SQL queries from queries.md files"""

    @staticmethod
    def extract_queries(md_file: Path) -> List[Dict[str, str]]:
        """Extract queries from markdown file"""
        queries = []

        if not md_file.exists():
            return queries

        content = md_file.read_text(encoding='utf-8')

        # Pattern to find all query headers
        query_header_pattern = r'^## Query (\d+):\s*(.+)$'
        headers = list(re.finditer(query_header_pattern, content, re.MULTILINE))

        for i, header_match in enumerate(headers):
            query_num = int(header_match.group(1))
            title = header_match.group(2).strip()
            start_pos = header_match.start()

            # Find the end position (next query header or end of file)
            if i + 1 < len(headers):
                end_pos = headers[i + 1].start()
            else:
                end_pos = len(content)

            # Extract the section for this query
            query_section = content[start_pos:end_pos]

            # Find SQL code block in this section
            sql_pattern = r'```(?:sql)?\n(.*?)```'
            sql_match = re.search(sql_pattern, query_section, re.DOTALL)

            if sql_match:
                sql = sql_match.group(1).strip()

                queries.append({
                    'number': query_num,
                    'title': title,
                    'sql': sql,
                    'description': title[:200] if title else f"Query {query_num}"
                })

        return sorted(queries, key=lambda x: x['number'])

class DatabaseTester:
    """Test queries against PostgreSQL"""

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.pg_conn = None
        self.db_conn = None
        self.results = {
            'database': db_name,
            'test_date': get_est_timestamp(),  # EST format: YYYYMMDD-HHMM
            'postgresql': {'available': False, 'queries': []},
            'summary': {}
        }

    def connect_postgresql(self, config: Dict) -> bool:
        """Connect to PostgreSQL"""
        if not PG_AVAILABLE:
            return False

        try:
            self.pg_conn = psycopg2.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                database=config.get('database', 'db_8_validation'),
                user=config.get('user', os.environ.get('USER', 'postgres')),
                password=config.get('password', '')
            )
            self.results['postgresql']['available'] = True
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return False

    def test_query_postgresql(self, query: Dict) -> Dict:
        """Test a query on PostgreSQL"""
        result = {
            'query_number': query['number'],
            'success': False,
            'error': None,
            'execution_time_ms': None,
            'row_count': None,
            'columns': None
        }

        if not self.pg_conn:
            result['error'] = 'PostgreSQL not connected'
            return result

        try:
            # Use autocommit mode or handle transactions properly
            old_autocommit = self.pg_conn.autocommit
            self.pg_conn.autocommit = True

            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            start_time = datetime.now()

            # Add LIMIT clause if not present to prevent large result sets
            sql_query = query['sql']
            if 'LIMIT' not in sql_query.upper() and 'FETCH' not in sql_query.upper():
                sql_query = sql_query.rstrip(';') + ' LIMIT 100'

            cursor.execute(sql_query)

            # Fetch results (limit to prevent memory issues)
            rows = cursor.fetchmany(100)
            row_count = len(rows)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000

            result['success'] = True
            result['execution_time_ms'] = round(execution_time, 2)
            result['row_count'] = row_count
            result['columns'] = [desc[0] for desc in cursor.description] if cursor.description else None

            cursor.close()
            self.pg_conn.autocommit = old_autocommit

        except Exception as e:
            # Rollback transaction on error to allow subsequent queries
            try:
                if not self.pg_conn.autocommit:
                    self.pg_conn.rollback()
            except Exception:
                pass
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            # Restore autocommit setting
            try:
                self.pg_conn.autocommit = old_autocommit
            except Exception:
                pass

        return result

    def test_all_queries(self, queries: List[Dict], pg_config: Dict = None, db_config: Dict = None):
        """Test all queries on both databases"""
        print(f"\n{'='*70}")
        print(f"Testing {len(queries)} queries for {self.db_name}")
        print(f"{'='*70}")

        # Test PostgreSQL
        if pg_config and self.connect_postgresql(pg_config):
            print(f"\nTesting on PostgreSQL...")
            for i, query in enumerate(queries, 1):
                print(f"  Query {query['number']}/{len(queries)}...", end=' ', flush=True)
                result = self.test_query_postgresql(query)
                self.results['postgresql']['queries'].append(result)
                if result['success']:
                    print(f"✓ ({result['execution_time_ms']}ms)")
                else:
                    print(f"✗ {result['error'][:60]}")
            if self.pg_conn:
                self.pg_conn.close()

        # Generate summary
        self._generate_summary()

    def _generate_summary(self):
        """Generate test summary"""
        pg_results = self.results['postgresql']['queries']

        pg_success = sum(1 for r in pg_results if r['success'])

        self.results['summary'] = {
            'total_queries': len(pg_results),
            'postgresql': {
                'tested': len(pg_results),
                'successful': pg_success,
                'failed': len(pg_results) - pg_success,
                'success_rate': round(pg_success / len(pg_results) * 100, 2) if pg_results else 0
            }
        }

    def save_results(self, output_path: Path):
        """Save results to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.results, indent=2, default=str, ensure_ascii=False))

def main():
    """Main execution testing function"""
    script_dir = Path(__file__).parent
    queries_file = script_dir.parent / 'queries' / 'queries.md'
    results_file = script_dir.parent / 'results' / 'query_test_results_postgres.json'

    if not queries_file.exists():
        print(f"Error: {queries_file} not found")
        return

    print("="*70)
    print("Execution Testing for db-8 queries.md")
    print("="*70)

    # Extract queries
    extractor = QueryExtractor()
    queries = extractor.extract_queries(queries_file)

    print(f"\nExtracted {len(queries)} queries")

    # Database configurations
    pg_config = {
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': int(os.environ.get('PG_PORT', 5432)),
        'user': os.environ.get('PG_USER', os.environ.get('USER', 'postgres')),
        'password': os.environ.get('PG_PASSWORD', ''),
        'database': os.environ.get('PG_DATABASE', 'db_8_validation')
    }

    if not PG_AVAILABLE:
        print("\n⚠️  psycopg2 not available. Skipping PostgreSQL execution testing.")
        pg_config = None

    # Test queries
    tester = DatabaseTester('db-8')
    tester.test_all_queries(queries, pg_config, None)
    tester.save_results(results_file)

    print("\n" + "="*70)
    print("Execution Testing Complete")
    print("="*70)
    print(f"Results saved to: {results_file}")

if __name__ == '__main__':
    main()
