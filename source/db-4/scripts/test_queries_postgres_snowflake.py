#!/usr/bin/env python3
"""
Comprehensive testing script for SQL queries on PostgreSQL and Snowflake
Tests all queries from db-1 through db-5 on both databases and generates JSON results
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import traceback

# Database connection imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False
    print("Warning: psycopg2 not available. PostgreSQL testing will be skipped.")

try:
    import snowflake.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    print("Warning: snowflake-connector-python not available. Snowflake testing will be skipped.")

class QueryExtractor:
    """Extract SQL queries from queries.md files"""

    @staticmethod
    def extract_queries(md_file: Path) -> List[Dict[str, str]]:
        """Extract queries from markdown file"""
        queries = []

        if not md_file.exists():
            return queries

        content = md_file.read_text(encoding='utf-8')

        # Split by query headers first, then extract SQL from each section
        # Pattern to find all query headers
        query_header_pattern = r'^##+\s+Query\s+(\d+)[:\s]'

        # Find all query headers
        headers = list(re.finditer(query_header_pattern, content, re.MULTILINE))

        for i, header_match in enumerate(headers):
            query_num = int(header_match.group(1))
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

                # Extract description (text before SQL block)
                description_text = query_section[:sql_match.start()]
                # Remove the header line
                description_text = re.sub(r'^##+\s+Query\s+\d+[:\s]*\n*', '', description_text, flags=re.MULTILINE)
                # Remove markdown formatting
                description_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', description_text)
                description_text = re.sub(r'`([^`]+)`', r'\1', description_text)
                description_text = re.sub(r'\n+', ' ', description_text)
                description = description_text.strip()[:200] if description_text.strip() else f"Query {query_num}"

                queries.append({
                    'number': query_num,
                    'sql': sql,
                    'description': description
                })

        return sorted(queries, key=lambda x: x['number'])

class DatabaseTester:
    """Test queries against PostgreSQL and Snowflake"""

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.pg_conn = None
        self.sf_conn = None
        self.results = {
            'database': db_name,
            'test_date': datetime.now().isoformat(),
            'postgresql': {'available': False, 'queries': []},
            'snowflake': {'available': False, 'queries': []},
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
                database=config.get('database', f'{self.db_name}_validation'),
                user=config.get('user', os.environ.get('USER', 'postgres')),
                password=config.get('password', '')
            )
            self.results['postgresql']['available'] = True
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return False

    def connect_snowflake(self, config: Dict) -> bool:
        """Connect to Snowflake"""
        if not SNOWFLAKE_AVAILABLE:
            return False

        try:
            self.sf_conn = snowflake.connector.connect(
                user=config.get('user', os.environ.get('SNOWFLAKE_USER')),
                password=config.get('password', os.environ.get('SNOWFLAKE_PASSWORD')),
                account=config.get('account', os.environ.get('SNOWFLAKE_ACCOUNT')),
                warehouse=config.get('warehouse', os.environ.get('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')),
                database=config.get('database', self.db_name.upper()),
                schema=config.get('schema', 'PUBLIC')
            )
            self.results['snowflake']['available'] = True
            return True
        except Exception as e:
            print(f"Snowflake connection failed: {e}")
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
            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            start_time = datetime.now()

            cursor.execute(query['sql'])

            # Fetch results (limit to prevent memory issues)
            rows = cursor.fetchmany(100)
            row_count = len(rows)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000

            result['success'] = True
            result['execution_time_ms'] = round(execution_time, 2)
            result['row_count'] = row_count
            result['columns'] = list(cursor.description) if cursor.description else None

            cursor.close()

        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__

        return result

    def test_query_snowflake(self, query: Dict) -> Dict:
        """Test a query on Snowflake"""
        result = {
            'query_number': query['number'],
            'success': False,
            'error': None,
            'execution_time_ms': None,
            'row_count': None,
            'columns': None
        }

        if not self.sf_conn:
            result['error'] = 'Snowflake not connected'
            return result

        try:
            cursor = self.sf_conn.cursor()
            start_time = datetime.now()

            cursor.execute(query['sql'])

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

        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__

        return result

    def test_all_queries(self, queries: List[Dict], pg_config: Dict = None, sf_config: Dict = None):
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

        # Test Snowflake
        if sf_config and self.connect_snowflake(sf_config):
            print(f"\nTesting on Snowflake...")
            for i, query in enumerate(queries, 1):
                print(f"  Query {query['number']}/{len(queries)}...", end=' ', flush=True)
                result = self.test_query_snowflake(query)
                self.results['snowflake']['queries'].append(result)
                if result['success']:
                    print(f"✓ ({result['execution_time_ms']}ms)")
                else:
                    print(f"✗ {result['error'][:60]}")
            if self.sf_conn:
                self.sf_conn.close()

        # Generate summary
        self._generate_summary()

    def _generate_summary(self):
        """Generate test summary"""
        pg_results = self.results['postgresql']['queries']
        sf_results = self.results['snowflake']['queries']

        pg_success = sum(1 for r in pg_results if r['success'])
        sf_success = sum(1 for r in sf_results if r['success'])

        self.results['summary'] = {
            'total_queries': len(pg_results) or len(sf_results),
            'postgresql': {
                'tested': len(pg_results),
                'successful': pg_success,
                'failed': len(pg_results) - pg_success,
                'success_rate': round(pg_success / len(pg_results) * 100, 2) if pg_results else 0
            },
            'snowflake': {
                'tested': len(sf_results),
                'successful': sf_success,
                'failed': len(sf_results) - sf_success,
                'success_rate': round(sf_success / len(sf_results) * 100, 2) if sf_results else 0
            }
        }

    def save_results(self, output_path: Path):
        """Save results to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.results, indent=2, default=str))
        print(f"\nResults saved to: {output_path}")

def main():
    """Main testing function"""
    root_dir = Path(__file__).parent

    print("="*70)
    print("SQL Query Testing for PostgreSQL and Snowflake")
    print("="*70)

    # Database configurations
    pg_config = {
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': int(os.environ.get('PG_PORT', 5432)),
        'user': os.environ.get('PG_USER', os.environ.get('USER', 'postgres')),
        'password': os.environ.get('PG_PASSWORD', '')
    }

    sf_config = {
        'user': os.environ.get('SNOWFLAKE_USER'),
        'password': os.environ.get('SNOWFLAKE_PASSWORD'),
        'account': os.environ.get('SNOWFLAKE_ACCOUNT'),
        'warehouse': os.environ.get('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
        'schema': os.environ.get('SNOWFLAKE_SCHEMA', 'PUBLIC')
    }

    # Check if Snowflake config is available
    if not all([sf_config.get('user'), sf_config.get('password'), sf_config.get('account')]):
        print("\n⚠️  Snowflake credentials not found in environment variables.")
        print("   Set SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, and SNOWFLAKE_ACCOUNT to test Snowflake.")
        print("   Continuing with PostgreSQL testing only...")
        sf_config = None

    # Check PostgreSQL availability
    if not PG_AVAILABLE:
        print("\n⚠️  psycopg2 not available. Install with: pip install psycopg2-binary")
        print("   Skipping PostgreSQL testing...")
        pg_config = None

    # Test each database
    all_results = {}

    for db_num in range(1, 6):
        db_name = f'db-{db_num}'
        queries_file = root_dir / db_name / 'queries' / 'queries.md'
        results_file = root_dir / db_name / 'results' / 'query_test_results_postgres_snowflake.json'

        if not queries_file.exists():
            print(f"\n⚠️  {queries_file} not found, skipping {db_name}")
            continue

        # Extract queries
        extractor = QueryExtractor()
        queries = extractor.extract_queries(queries_file)

        if not queries:
            print(f"\n⚠️  No queries found in {queries_file}, skipping {db_name}")
            continue

        print(f"\n{'='*70}")
        print(f"Database: {db_name}")
        print(f"Found {len(queries)} queries")
        print(f"{'='*70}")

        # Update database names in configs (create copies to avoid mutation)
        test_pg_config = pg_config.copy() if pg_config else None
        test_sf_config = sf_config.copy() if sf_config else None

        if test_pg_config:
            test_pg_config['database'] = f'{db_name.replace("-", "_")}_validation'
        if test_sf_config:
            test_sf_config['database'] = f'DB{db_num}'

        # Test queries
        tester = DatabaseTester(db_name)
        tester.test_all_queries(queries, test_pg_config, test_sf_config)
        tester.save_results(results_file)

        all_results[db_name] = tester.results

    # Print summary
    print("\n" + "="*70)
    print("TESTING SUMMARY")
    print("="*70)

    for db_name, results in all_results.items():
        summary = results.get('summary', {})
        print(f"\n{db_name}:")
        if results['postgresql']['available']:
            pg_summary = summary.get('postgresql', {})
            print(f"  PostgreSQL: {pg_summary.get('successful', 0)}/{pg_summary.get('tested', 0)} successful ({pg_summary.get('success_rate', 0)}%)")
        else:
            print(f"  PostgreSQL: Not tested")

        if results['snowflake']['available']:
            sf_summary = summary.get('snowflake', {})
            print(f"  Snowflake: {sf_summary.get('successful', 0)}/{sf_summary.get('tested', 0)} successful ({sf_summary.get('success_rate', 0)}%)")
        else:
            print(f"  Snowflake: Not tested")

    print("\n" + "="*70)
    print("Testing complete! Results saved to db-{N}/results/query_test_results_postgres_snowflake.json")
    print("="*70)

if __name__ == '__main__':
    main()
