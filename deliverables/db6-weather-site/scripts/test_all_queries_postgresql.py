#!/usr/bin/env python3
"""
Unified Execution Tester for All Databases (db-6 through db-15)
Tests all queries from queries.json files against PostgreSQL
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add root scripts directory to path for timestamp_utils
root_scripts = Path(__file__).parent
sys.path.insert(0, str(root_scripts))
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

# Database connection imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False
    print("⚠️  psycopg2 not available. Install with: pip install psycopg2-binary")

class DatabaseTester:
    """Test queries against PostgreSQL"""

    def __init__(self, db_name: str, db_num: int):
        self.db_name = db_name
        self.db_num = db_num
        self.pg_conn = None
        self.results = {
            'database': db_name,
            'database_number': db_num,
            'test_date': get_est_timestamp(),
            'postgresql': {'available': False, 'queries': []},
            'summary': {}
        }

    def get_postgres_connection(self):
        """Get PostgreSQL connection"""
        if not PG_AVAILABLE:
            return None

        try:
            # Try multiple connection strategies
            conn_params_list = [
                # Strategy 1: Database-specific environment variables
                {
                    'host': os.environ.get(f'PG_HOST_DB{self.db_num}', os.environ.get('PG_HOST', 'localhost')),
                    'port': int(os.environ.get(f'PG_PORT_DB{self.db_num}', os.environ.get('PG_PORT', '5432'))),
                    'user': os.environ.get(f'PG_USER_DB{self.db_num}', os.environ.get('PG_USER', 'postgres')),
                    'password': os.environ.get(f'PG_PASSWORD_DB{self.db_num}', os.environ.get('PG_PASSWORD', 'postgres')),
                    'database': os.environ.get(f'PG_DATABASE_DB{self.db_num}', os.environ.get('PG_DATABASE', f'db{self.db_num}'))
                },
                # Strategy 2: Try with current user (127.0.0.1 for IPv4)
                {
                    'host': '127.0.0.1',
                    'port': 5432,
                    'user': os.environ.get('USER', 'postgres'),
                    'password': '',
                    'database': f'db{self.db_num}'
                },
                # Strategy 3: Try with postgres user
                {
                    'host': 'localhost',
                    'port': 5432,
                    'user': 'postgres',
                    'password': 'postgres',
                    'database': f'db{self.db_num}'
                }
            ]

            for params in conn_params_list:
                try:
                    # Force IPv4 for localhost
                    if params['host'] == 'localhost':
                        params['host'] = '127.0.0.1'
                    
                    conn = psycopg2.connect(**params)
                    return conn
                except Exception as e:
                    continue
            
            return None
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
            return None

    def test_query_postgres(self, query: Dict) -> Dict:
        """Test a single query on PostgreSQL"""
        result = {
            'query_number': query.get('number', 0),
            'query_title': query.get('title', ''),
            'success': False,
            'execution_time_ms': None,
            'row_count': None,
            'columns': [],
            'error': None,
            'error_type': None
        }

        if not self.pg_conn:
            result['error'] = 'PostgreSQL not connected'
            return result

        try:
            # Add LIMIT to prevent large result sets
            sql_with_limit = query.get('sql', '')
            if not sql_with_limit:
                result['error'] = 'Empty SQL query'
                return result

            # Remove trailing semicolon if present
            sql_with_limit = sql_with_limit.rstrip(';').strip()
            
            if 'LIMIT' not in sql_with_limit.upper() and 'FETCH' not in sql_with_limit.upper():
                sql_with_limit = f"{sql_with_limit} LIMIT 100"

            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            start_time = time.time()
            cursor.execute(sql_with_limit)
            rows = cursor.fetchall()
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            result['success'] = True
            result['execution_time_ms'] = round(execution_time, 2)
            result['row_count'] = len(rows)
            if rows and isinstance(rows[0], dict):
                result['columns'] = list(rows[0].keys())
            elif cursor.description:
                result['columns'] = [desc[0] for desc in cursor.description]

            cursor.close()
        except psycopg2.errors.UndefinedTable as e:
            result['error'] = str(e)
            result['error_type'] = 'UndefinedTable'
        except psycopg2.errors.UndefinedColumn as e:
            result['error'] = str(e)
            result['error_type'] = 'UndefinedColumn'
        except psycopg2.errors.SyntaxError as e:
            result['error'] = str(e)
            result['error_type'] = 'SyntaxError'
        except psycopg2.errors.InFailedSqlTransaction as e:
            result['error'] = str(e)
            result['error_type'] = 'InFailedSqlTransaction'
            # Rollback to allow subsequent queries
            try:
                self.pg_conn.rollback()
            except:
                pass
        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            # Rollback transaction on error to allow subsequent queries to run
            try:
                self.pg_conn.rollback()
            except:
                pass

        return result

    def test_all_queries(self, queries: List[Dict]):
        """Test all queries on PostgreSQL"""
        print(f"\n{'='*70}")
        print(f"Execution Testing - {self.db_name}")
        print(f"{'='*70}")

        # Test PostgreSQL
        self.pg_conn = self.get_postgres_connection()
        if self.pg_conn:
            self.results['postgresql']['available'] = True
            print(f"\nTesting {len(queries)} queries on PostgreSQL...")
            
            for i, query in enumerate(queries, 1):
                query_num = query.get('number', i)
                print(f"  Query {query_num}/{len(queries)}...", end=' ', flush=True)
                result = self.test_query_postgres(query)
                self.results['postgresql']['queries'].append(result)
                
                if result['success']:
                    print(f"✓ ({result['execution_time_ms']:.0f}ms, {result['row_count']} rows)")
                else:
                    error_msg = result['error'][:60] if result['error'] else 'Unknown error'
                    print(f"✗ {error_msg}")
            
            self.pg_conn.close()
        else:
            print(f"\n⚠️  PostgreSQL not available for {self.db_name}. Skipping.")
            print("   Set PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE environment variables")

        # Calculate summary
        total_queries = len(queries)
        pg_queries = self.results['postgresql']['queries']
        self.results['summary'] = {
            'total_queries': total_queries,
            'postgresql': {
                'tested': len(pg_queries),
                'successful': sum(1 for q in pg_queries if q['success']),
                'failed': sum(1 for q in pg_queries if not q['success']),
                'success_rate': round((sum(1 for q in pg_queries if q['success']) / len(pg_queries) * 100), 2) if pg_queries else 0
            }
        }

    def save_results(self, output_file: Path):
        """Save test results to JSON file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(self.results, indent=2, default=str, ensure_ascii=False))


def test_database(db_num: int, root_dir: Path) -> Dict:
    """Test a single database"""
    db_name = f'db-{db_num}'
    db_dir = root_dir / db_name
    queries_json = db_dir / 'queries' / 'queries.json'
    results_file = db_dir / 'results' / 'query_execution_test_results.json'

    if not queries_json.exists():
        return {
            'database': db_name,
            'status': 'SKIPPED',
            'error': f'queries.json not found: {queries_json}'
        }

    try:
        # Load queries
        with open(queries_json) as f:
            queries_data = json.load(f)
        
        queries = queries_data.get('queries', [])
        if not queries:
            return {
                'database': db_name,
                'status': 'SKIPPED',
                'error': 'No queries found in queries.json'
            }

        # Test queries
        tester = DatabaseTester(db_name, db_num)
        tester.test_all_queries(queries)
        tester.save_results(results_file)

        summary = tester.results.get('summary', {}).get('postgresql', {})
        return {
            'database': db_name,
            'status': 'COMPLETED',
            'postgresql_available': tester.results['postgresql']['available'],
            'total_queries': summary.get('total_queries', 0),
            'tested': summary.get('tested', 0),
            'successful': summary.get('successful', 0),
            'failed': summary.get('failed', 0),
            'success_rate': summary.get('success_rate', 0),
            'results_file': str(results_file)
        }
    except Exception as e:
        return {
            'database': db_name,
            'status': 'ERROR',
            'error': str(e)
        }


def main():
    """Main function to test all databases"""
    root_dir = Path(__file__).parent.parent
    databases = list(range(6, 16))  # db-6 through db-15

    print("="*70)
    print("PostgreSQL Execution Testing - All Databases (db-6 through db-15)")
    print("="*70)

    if not PG_AVAILABLE:
        print("\n⚠️  psycopg2 not available. Cannot run execution tests.")
        print("   Install with: pip install psycopg2-binary")
        return

    all_results = {
        'test_date': get_est_timestamp(),
        'databases': {},
        'summary': {}
    }

    for db_num in databases:
        result = test_database(db_num, root_dir)
        all_results['databases'][f'db-{db_num}'] = result

    # Calculate overall summary
    total_dbs = len(all_results['databases'])
    dbs_with_pg = sum(1 for r in all_results['databases'].values() if r.get('postgresql_available'))
    total_queries = sum(r.get('total_queries', 0) for r in all_results['databases'].values())
    total_successful = sum(r.get('successful', 0) for r in all_results['databases'].values())
    total_failed = sum(r.get('failed', 0) for r in all_results['databases'].values())

    all_results['summary'] = {
        'total_databases': total_dbs,
        'databases_with_postgresql': dbs_with_pg,
        'total_queries_tested': total_queries,
        'total_successful': total_successful,
        'total_failed': total_failed,
        'overall_success_rate': round((total_successful / total_queries * 100), 2) if total_queries > 0 else 0
    }

    # Print summary
    print("\n" + "="*70)
    print("Execution Testing Summary")
    print("="*70)
    print(f"\nTotal Databases: {total_dbs}")
    print(f"Databases with PostgreSQL: {dbs_with_pg}")
    print(f"Total Queries Tested: {total_queries}")
    print(f"Successful: {total_successful}")
    print(f"Failed: {total_failed}")
    print(f"Overall Success Rate: {all_results['summary']['overall_success_rate']:.2f}%")

    print("\n" + "="*70)
    print("Database-by-Database Results")
    print("="*70)
    for db_name, result in sorted(all_results['databases'].items()):
        if result.get('status') == 'COMPLETED':
            pg_avail = result.get('postgresql_available', False)
            if pg_avail:
                print(f"\n{db_name}:")
                print(f"  Queries: {result.get('total_queries', 0)}")
                print(f"  Successful: {result.get('successful', 0)}")
                print(f"  Failed: {result.get('failed', 0)}")
                print(f"  Success Rate: {result.get('success_rate', 0):.2f}%")
            else:
                print(f"\n{db_name}: PostgreSQL not available")
        else:
            print(f"\n{db_name}: {result.get('status', 'UNKNOWN')} - {result.get('error', '')}")

    # Save overall results
    summary_file = root_dir / 'query_execution_test_summary.json'
    summary_file.write_text(json.dumps(all_results, indent=2, default=str, ensure_ascii=False))
    print(f"\n{'='*70}")
    print(f"Overall summary saved to: {summary_file}")
    print("="*70)


if __name__ == '__main__':
    main()
