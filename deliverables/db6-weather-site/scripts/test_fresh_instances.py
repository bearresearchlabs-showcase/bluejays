#!/usr/bin/env python3
"""
Test SQL queries on fresh database instances.
Creates new test databases, loads schemas and data, then tests all queries.
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

BASE = Path(__file__).parent.parent

class QueryLoader:
    """Load queries from queries.json"""
    
    def __init__(self, db_num: int):
        self.db_num = db_num
        self.queries_file = BASE / f"db-{db_num}" / "queries" / "queries.json"
    
    def load_queries(self) -> List[Dict]:
        """Load queries from queries.json"""
        if not self.queries_file.exists():
            raise FileNotFoundError(f"queries.json not found: {self.queries_file}")
        
        with open(self.queries_file) as f:
            data = json.load(f)
            return data.get('queries', [])

class PostgreSQLTester:
    """Test queries on PostgreSQL fresh instance"""
    
    def __init__(self, db_num: int):
        self.db_num = db_num
        self.db_name = f"db_{db_num}_fresh_test"
        self.available = False
        self.connection = None
        
    def connect(self) -> bool:
        """Connect to PostgreSQL"""
        try:
            import psycopg2
            
            user = os.getenv('PG_USER', os.getenv('USER', 'machine'))
            password = os.getenv('PG_PASSWORD', '')
            host = os.getenv('PG_HOST', 'localhost')
            port = os.getenv('PG_PORT', '5432')
            
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=self.db_name
            )
            self.connection.autocommit = False
            self.available = True
            return True
            
        except ImportError:
            print("  ⚠️  psycopg2 not installed")
            return False
        except Exception as e:
            print(f"  ⚠️  PostgreSQL connection failed: {e}")
            return False
    
    def test_query(self, query: Dict, limit: int = 100) -> Dict:
        """Test a single query"""
        if not self.available or not self.connection:
            return {
                'query_number': query.get('number', 0),
                'success': False,
                'error': 'PostgreSQL not available'
            }
        
        query_num = query.get('number', 0)
        sql = query.get('sql', '')
        
        # Add LIMIT if not present
        if 'LIMIT' not in sql.upper() and 'FETCH' not in sql.upper():
            sql = f"{sql.rstrip(';')} LIMIT {limit}"
        
        try:
            # Rollback any previous transaction errors
            try:
                self.connection.rollback()
            except:
                pass
            
            cur = self.connection.cursor()
            start_time = time.time()
            cur.execute(sql)
            execution_time = (time.time() - start_time) * 1000  # ms
            
            # Fetch results
            rows = cur.fetchall()
            row_count = len(rows)
            
            # Get column names
            columns = [desc[0] for desc in cur.description] if cur.description else []
            
            cur.close()
            self.connection.commit()
            
            return {
                'query_number': query_num,
                'success': True,
                'execution_time_ms': round(execution_time, 2),
                'row_count': row_count,
                'columns': columns
            }
            
        except Exception as e:
            # Rollback on error
            try:
                self.connection.rollback()
            except:
                pass
            
            return {
                'query_number': query_num,
                'success': False,
                'error': str(e)[:500],
                'execution_time_ms': 0
            }
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()

def test_database(db_num: int):
    """Test all queries for a database on fresh instance"""
    print(f"\n{'='*70}")
    print(f"Testing db-{db_num} on Fresh PostgreSQL Instance")
    print(f"{'='*70}")
    
    # Load queries
    loader = QueryLoader(db_num)
    try:
        queries = loader.load_queries()
        print(f"✅ Loaded {len(queries)} queries")
    except Exception as e:
        print(f"❌ Failed to load queries: {e}")
        return
    
    results = {
        'database': f'db-{db_num}',
        'test_instance': 'fresh_postgresql',
        'test_date': datetime.now().isoformat(),
        'postgresql': {'available': False, 'queries': []}
    }
    
    # Test on PostgreSQL
    db_name = f"db_{db_num}_fresh_test"
    print(f"\nPostgreSQL Testing on {db_name.replace('_', ' ').title()}...")
    pg_tester = PostgreSQLTester(db_num)
    if pg_tester.connect():
        print(f"  ✅ Connected to PostgreSQL")
        print(f"  Testing {len(queries)} queries...")
        
        for i, query in enumerate(queries, 1):
            if i % 10 == 0:
                print(f"    Progress: {i}/{len(queries)}")
            result = pg_tester.test_query(query)
            results['postgresql']['queries'].append(result)
        
        results['postgresql']['available'] = True
        success_count = sum(1 for q in results['postgresql']['queries'] if q.get('success', False))
        failed_count = len(queries) - success_count
        print(f"  ✅ PostgreSQL: {success_count}/{len(queries)} queries successful")
        if failed_count > 0:
            print(f"     Failed: {failed_count} queries")
        
        pg_tester.close()
    else:
        print(f"  ⚠️  PostgreSQL not available")
    
    # Save results
    results_file = BASE / f"db-{db_num}" / "results" / "query_test_results_fresh_instance.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2))
    print(f"\n✅ Results saved to: {results_file}")
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"db-{db_num} Test Summary")
    print(f"{'='*70}")
    
    if results['postgresql']['available']:
        pg_queries = results['postgresql']['queries']
        pg_success = sum(1 for q in pg_queries if q.get('success', False))
        pg_total = len(pg_queries)
        success_rate = (pg_success / pg_total * 100) if pg_total > 0 else 0
        print(f"PostgreSQL: {pg_success}/{pg_total} queries successful ({success_rate:.1f}%)")
        
        if pg_success < pg_total:
            # Show failed queries
            failed = [q for q in pg_queries if not q.get('success', False)]
            print(f"\nFailed Queries:")
            for q in failed[:5]:
                error = q.get('error', 'Unknown')[:100]
                print(f"  Query {q.get('query_number')}: {error}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")

def main():
    """Main function"""
    print("=" * 70)
    print("Testing SQL Queries on Fresh Database Instances")
    print("=" * 70)
    
    databases = [1, 2, 3, 4, 5]
    
    for db_num in databases:
        test_database(db_num)
    
    print("\n" + "=" * 70)
    print("Testing Complete")
    print("=" * 70)
    
    # Print overall summary
    print("\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)
    
    total_queries = 0
    total_success = 0
    
    for db_num in databases:
        results_file = BASE / f"db-{db_num}" / "results" / "query_test_results_fresh_instance.json"
        if results_file.exists():
            with open(results_file) as f:
                results = json.load(f)
                pg = results.get('postgresql', {})
                if pg.get('available'):
                    queries = pg.get('queries', [])
                    success = sum(1 for q in queries if q.get('success', False))
                    total_queries += len(queries)
                    total_success += success
                    print(f"db-{db_num}: {success}/{len(queries)} successful")
    
    if total_queries > 0:
        overall_rate = (total_success / total_queries * 100)
        print(f"\nOverall: {total_success}/{total_queries} queries successful ({overall_rate:.1f}%)")
        
        if total_success == total_queries:
            print("\n✅✅✅ ALL QUERIES WORKING ON FRESH INSTANCES ✅✅✅")
        else:
            print(f"\n⚠️  {total_queries - total_success} queries need attention")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
