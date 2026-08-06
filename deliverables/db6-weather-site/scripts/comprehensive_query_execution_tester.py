#!/usr/bin/env python3
"""
Comprehensive Query Execution Tester
Tests all queries from queries.json files against PostgreSQL
Uses EXPLAIN for syntax validation when databases don't exist
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

class QueryTester:
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

    def get_postgres_connection(self, database_name: str = None):
        """Get PostgreSQL connection - try multiple strategies"""
        if not PG_AVAILABLE:
            return None

        db_name = database_name or f'db{self.db_num}'
        user = os.environ.get('USER', 'machine')
        
        # Try multiple connection strategies
        strategies = [
            # Strategy 1: Specific database
            {'host': '127.0.0.1', 'port': 5432, 'user': user, 'password': '', 'database': db_name},
            # Strategy 2: postgres database (for EXPLAIN testing)
            {'host': '127.0.0.1', 'port': 5432, 'user': user, 'password': '', 'database': 'postgres'},
            # Strategy 3: Try with postgres user
            {'host': '127.0.0.1', 'port': 5432, 'user': 'postgres', 'password': 'postgres', 'database': 'postgres'},
        ]

        for params in strategies:
            try:
                conn = psycopg2.connect(**params)
                return conn, params['database']
            except Exception:
                continue
        
        return None, None

    def test_query_with_explain(self, query: Dict, conn) -> Dict:
        """Test query using EXPLAIN (syntax validation without execution)"""
        result = {
            'query_number': query.get('number', 0),
            'query_title': query.get('title', ''),
            'success': False,
            'execution_time_ms': None,
            'row_count': None,
            'columns': [],
            'error': None,
            'error_type': None,
            'test_method': 'EXPLAIN'
        }

        sql = query.get('sql', '').strip()
        if not sql:
            result['error'] = 'Empty SQL query'
            return result

        # Always rollback before testing to ensure clean state
        try:
            conn.rollback()
        except:
            pass

        try:
            # Remove trailing semicolon
            sql_clean = sql.rstrip(';').strip()
            
            # Use EXPLAIN to validate syntax
            explain_sql = f"EXPLAIN {sql_clean}"
            
            cursor = conn.cursor()
            start_time = time.time()
            cursor.execute(explain_sql)
            plan = cursor.fetchall()
            execution_time = (time.time() - start_time) * 1000

            result['success'] = True
            result['execution_time_ms'] = round(execution_time, 2)
            result['row_count'] = len(plan)
            cursor.close()
            
            # Rollback after successful EXPLAIN
            try:
                conn.rollback()
            except:
                pass

        except psycopg2.errors.UndefinedTable as e:
            result['error'] = str(e)
            result['error_type'] = 'UndefinedTable'
            # This is expected if tables don't exist - query syntax is valid
            result['success'] = True  # Syntax is valid, just missing tables
            result['note'] = 'Syntax valid but tables missing'
            try:
                conn.rollback()
            except:
                pass
        except psycopg2.errors.UndefinedColumn as e:
            result['error'] = str(e)
            result['error_type'] = 'UndefinedColumn'
            try:
                conn.rollback()
            except:
                pass
        except psycopg2.errors.SyntaxError as e:
            result['error'] = str(e)
            result['error_type'] = 'SyntaxError'
            try:
                conn.rollback()
            except:
                pass
        except psycopg2.errors.InFailedSqlTransaction as e:
            result['error'] = str(e)
            result['error_type'] = 'InFailedSqlTransaction'
            try:
                conn.rollback()
            except:
                pass
        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            try:
                conn.rollback()
            except:
                pass

        return result

    def test_query_execution(self, query: Dict, conn) -> Dict:
        """Test query with actual execution"""
        result = {
            'query_number': query.get('number', 0),
            'query_title': query.get('title', ''),
            'success': False,
            'execution_time_ms': None,
            'row_count': None,
            'columns': [],
            'error': None,
            'error_type': None,
            'test_method': 'EXECUTION'
        }

        sql = query.get('sql', '').strip()
        if not sql:
            result['error'] = 'Empty SQL query'
            return result

        try:
            sql_clean = sql.rstrip(';').strip()
            
            # Add LIMIT if not present
            if 'LIMIT' not in sql_clean.upper() and 'FETCH' not in sql_clean.upper():
                sql_clean = f"{sql_clean} LIMIT 100"

            cursor = conn.cursor(cursor_factory=RealDictCursor)
            start_time = time.time()
            cursor.execute(sql_clean)
            rows = cursor.fetchall()
            execution_time = (time.time() - start_time) * 1000

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
            try:
                conn.rollback()
            except:
                pass
        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            try:
                conn.rollback()
            except:
                pass

        return result

    def test_all_queries(self, queries: List[Dict], use_explain: bool = False):
        """Test all queries"""
        print(f"\n{'='*70}")
        print(f"Execution Testing - {self.db_name}")
        print(f"{'='*70}")

        # Try to connect to specific database first, then fallback to postgres
        conn, db_used = self.get_postgres_connection()
        
        if not conn:
            # Try postgres database for EXPLAIN testing
            conn, db_used = self.get_postgres_connection('postgres')
        
        if conn:
            self.results['postgresql']['available'] = True
            self.results['database_used'] = db_used
            self.results['test_method'] = 'EXPLAIN' if use_explain else 'EXECUTION'
            
            print(f"\nTesting {len(queries)} queries on PostgreSQL (database: {db_used})...")
            if use_explain:
                print("Using EXPLAIN for syntax validation (tables may not exist)")
            
            for i, query in enumerate(queries, 1):
                query_num = query.get('number', i)
                print(f"  Query {query_num}/{len(queries)}...", end=' ', flush=True)
                
                if use_explain:
                    result = self.test_query_with_explain(query, conn)
                else:
                    result = self.test_query_execution(query, conn)
                
                self.results['postgresql']['queries'].append(result)
                
                if result['success']:
                    if result.get('note'):
                        print(f"✓ ({result['note']})")
                    else:
                        print(f"✓ ({result['execution_time_ms']:.0f}ms, {result.get('row_count', 0)} rows)")
                else:
                    error_msg = result['error'][:60] if result['error'] else 'Unknown error'
                    print(f"✗ {error_msg}")
            
            conn.close()
        else:
            print(f"\n⚠️  PostgreSQL not available for {self.db_name}. Skipping.")

        # Calculate summary
        total_queries = len(queries)
        pg_queries = self.results['postgresql']['queries']
        successful = [q for q in pg_queries if q['success']]
        failed = [q for q in pg_queries if not q['success']]
        
        self.results['summary'] = {
            'total_queries': total_queries,
            'postgresql': {
                'tested': len(pg_queries),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': round((len(successful) / len(pg_queries) * 100), 2) if pg_queries else 0
            }
        }

    def save_results(self, output_file: Path):
        """Save test results to JSON file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(self.results, indent=2, default=str, ensure_ascii=False))


def test_database(db_num: int, root_dir: Path, use_explain: bool = False) -> Dict:
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
        tester = QueryTester(db_name, db_num)
        tester.test_all_queries(queries, use_explain=use_explain)
        tester.save_results(results_file)

        summary = tester.results.get('summary', {}).get('postgresql', {})
        pg_available = tester.results['postgresql']['available']
        
        # Analyze failures
        failed_queries = [q for q in tester.results['postgresql']['queries'] if not q['success']]
        error_types = {}
        for q in failed_queries:
            error_type = q.get('error_type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            'database': db_name,
            'status': 'COMPLETED',
            'postgresql_available': pg_available,
            'database_used': tester.results.get('database_used', 'unknown'),
            'test_method': tester.results.get('test_method', 'EXECUTION'),
            'total_queries': summary.get('total_queries', 0),
            'tested': summary.get('tested', 0),
            'successful': summary.get('successful', 0),
            'failed': summary.get('failed', 0),
            'success_rate': summary.get('success_rate', 0),
            'error_types': error_types,
            'failed_query_numbers': [q['query_number'] for q in failed_queries],
            'results_file': str(results_file)
        }
    except Exception as e:
        import traceback
        return {
            'database': db_name,
            'status': 'ERROR',
            'error': str(e),
            'traceback': traceback.format_exc()
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

    # Check if we should use EXPLAIN (when databases don't exist)
    use_explain = os.environ.get('USE_EXPLAIN', 'false').lower() == 'true'
    
    all_results = {
        'test_date': get_est_timestamp(),
        'test_method': 'EXPLAIN' if use_explain else 'EXECUTION',
        'databases': {},
        'summary': {}
    }

    for db_num in databases:
        result = test_database(db_num, root_dir, use_explain=use_explain)
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
                print(f"  Database Used: {result.get('database_used', 'unknown')}")
                print(f"  Test Method: {result.get('test_method', 'EXECUTION')}")
                print(f"  Queries: {result.get('total_queries', 0)}")
                print(f"  Successful: {result.get('successful', 0)}")
                print(f"  Failed: {result.get('failed', 0)}")
                print(f"  Success Rate: {result.get('success_rate', 0):.2f}%")
                
                if result.get('failed_query_numbers'):
                    print(f"  Failed Queries: {', '.join(map(str, result['failed_query_numbers'][:10]))}")
                    if len(result['failed_query_numbers']) > 10:
                        print(f"    ... and {len(result['failed_query_numbers']) - 10} more")
                
                if result.get('error_types'):
                    print(f"  Error Types: {dict(result['error_types'])}")
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
