#!/usr/bin/env python3
"""
Setup PostgreSQL Databases and Run Extensive Execution Tests
Creates databases, loads schemas and data, then tests all queries
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add root scripts directory to path
root_scripts = Path(__file__).parent
sys.path.insert(0, str(root_scripts))
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    from datetime import datetime
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False
    print("⚠️  psycopg2 not available. Install with: pip install psycopg2-binary")

class DatabaseSetup:
    """Setup PostgreSQL databases"""
    
    def __init__(self):
        self.user = os.environ.get('USER', 'machine')
        self.host = '127.0.0.1'
        self.port = 5432
        self.admin_conn = None
        
    def get_admin_connection(self):
        """Get connection to postgres database for admin operations"""
        if not PG_AVAILABLE:
            return None
            
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password='',
                database='postgres'
            )
            conn.autocommit = True
            return conn
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return None
    
    def database_exists(self, db_name: str) -> bool:
        """Check if database exists"""
        conn = self.get_admin_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_name,)
            )
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        except Exception as e:
            print(f"Error checking database {db_name}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def create_database(self, db_name: str) -> bool:
        """Create a PostgreSQL database"""
        if self.database_exists(db_name):
            print(f"  Database {db_name} already exists")
            return True
            
        conn = self.get_admin_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            cursor.close()
            print(f"  ✓ Created database {db_name}")
            return True
        except Exception as e:
            print(f"  ✗ Error creating database {db_name}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def load_schema(self, db_name: str, schema_file: Path) -> Tuple[bool, str]:
        """Load schema SQL file into database with PostgreSQL compatibility"""
        from postgresql_schema_loader import load_schema_postgresql
        
        # Check if schema uses GEOGRAPHY (needs PostGIS)
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        enable_postgis = 'GEOGRAPHY' in schema_content.upper()
        
        return load_schema_postgresql(db_name, schema_file, enable_postgis=enable_postgis)
    
    def load_data(self, db_name: str, data_file: Path) -> Tuple[bool, str]:
        """Load data SQL file into database"""
        if not data_file.exists():
            return False, f"Data file not found: {data_file}"
        
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password='',
                database=db_name
            )
            conn.autocommit = True
            
            cursor = conn.cursor()
            
            # Read and execute data file
            with open(data_file, 'r', encoding='utf-8') as f:
                data_sql = f.read()
            
            # Split by semicolons and execute each statement
            statements = [s.strip() for s in data_sql.split(';') if s.strip()]
            
            errors = []
            executed = 0
            for i, statement in enumerate(statements):
                try:
                    cursor.execute(statement)
                    executed += 1
                except Exception as e:
                    error_msg = str(e)
                    # Skip duplicate key errors (expected with sample data)
                    if 'duplicate key' not in error_msg.lower() and 'already exists' not in error_msg.lower():
                        errors.append(f"Statement {i+1}: {error_msg[:100]}")
            
            cursor.close()
            conn.close()
            
            if errors and len(errors) > executed * 0.5:  # More than 50% errors
                return False, f"Many errors loading data: {'; '.join(errors[:3])}"
            return True, f"Data loaded successfully ({executed} statements)"
            
        except Exception as e:
            return False, f"Error loading data: {str(e)}"


def setup_database(db_num: int, root_dir: Path) -> Dict:
    """Setup a single database"""
    db_name = f'db{db_num}'
    db_dir = root_dir / f'db-{db_num}'
    schema_file = db_dir / 'data' / 'schema.sql'
    data_file = db_dir / 'data' / 'data.sql'
    
    setup = DatabaseSetup()
    result = {
        'database': f'db-{db_num}',
        'database_name': db_name,
        'setup_status': 'PENDING',
        'schema_loaded': False,
        'data_loaded': False,
        'errors': []
    }
    
    print(f"\n{'='*70}")
    print(f"Setting up {db_name}")
    print(f"{'='*70}")
    
    # Create database
    if not setup.create_database(db_name):
        result['setup_status'] = 'FAILED'
        result['errors'].append('Failed to create database')
        return result
    
    # Load schema
    if schema_file.exists():
        success, message = setup.load_schema(db_name, schema_file)
        result['schema_loaded'] = success
        if success:
            print(f"  ✓ Schema loaded")
        else:
            print(f"  ✗ Schema loading failed: {message}")
            result['errors'].append(f"Schema: {message}")
    else:
        print(f"  ⚠ Schema file not found: {schema_file}")
        result['errors'].append(f"Schema file not found")
    
    # Load data
    if data_file.exists():
        success, message = setup.load_data(db_name, data_file)
        result['data_loaded'] = success
        if success:
            print(f"  ✓ Data loaded: {message}")
        else:
            print(f"  ✗ Data loading failed: {message}")
            result['errors'].append(f"Data: {message}")
    else:
        print(f"  ⚠ Data file not found: {data_file}")
        result['errors'].append(f"Data file not found")
    
    if result['schema_loaded']:
        result['setup_status'] = 'SUCCESS'
    else:
        result['setup_status'] = 'PARTIAL' if result['data_loaded'] else 'FAILED'
    
    return result


def main():
    """Main function to setup all databases and run tests"""
    root_dir = Path(__file__).parent.parent
    databases = list(range(6, 16))  # db-6 through db-15
    
    print("="*70)
    print("PostgreSQL Database Setup and Extensive Testing")
    print("="*70)
    
    if not PG_AVAILABLE:
        print("\n⚠️  psycopg2 not available. Cannot setup databases.")
        print("   Install with: pip install psycopg2-binary")
        return
    
    # Setup all databases
    setup_results = {}
    for db_num in databases:
        result = setup_database(db_num, root_dir)
        setup_results[f'db-{db_num}'] = result
    
    # Save setup results
    setup_file = root_dir / 'database_setup_results.json'
    setup_file.write_text(json.dumps({
        'setup_date': get_est_timestamp(),
        'databases': setup_results
    }, indent=2, default=str))
    
    print("\n" + "="*70)
    print("Setup Summary")
    print("="*70)
    
    successful = sum(1 for r in setup_results.values() if r['setup_status'] == 'SUCCESS')
    partial = sum(1 for r in setup_results.values() if r['setup_status'] == 'PARTIAL')
    failed = sum(1 for r in setup_results.values() if r['setup_status'] == 'FAILED')
    
    print(f"\nSuccessful: {successful}")
    print(f"Partial: {partial}")
    print(f"Failed: {failed}")
    
    # Now run execution tests
    print("\n" + "="*70)
    print("Running Extensive Execution Tests")
    print("="*70)
    
    # Import and run the comprehensive tester
    sys.path.insert(0, str(root_scripts))
    from comprehensive_query_execution_tester import test_database
    
    test_results = {}
    for db_num in databases:
        result = test_database(db_num, root_dir, use_explain=False)
        test_results[f'db-{db_num}'] = result
    
    # Generate final comprehensive report
    final_report = {
        'report_date': get_est_timestamp(),
        'setup_results': setup_results,
        'test_results': test_results,
        'summary': {
            'databases_setup': {
                'successful': successful,
                'partial': partial,
                'failed': failed,
                'total': len(databases)
            },
            'queries_tested': sum(r.get('tested', 0) for r in test_results.values()),
            'queries_successful': sum(r.get('successful', 0) for r in test_results.values()),
            'queries_failed': sum(r.get('failed', 0) for r in test_results.values())
        }
    }
    
    # Calculate success rate
    total_tested = final_report['summary']['queries_tested']
    total_successful = final_report['summary']['queries_successful']
    if total_tested > 0:
        final_report['summary']['overall_success_rate'] = round((total_successful / total_tested * 100), 2)
    else:
        final_report['summary']['overall_success_rate'] = 0
    
    # Save final report
    report_file = root_dir / 'extensive_execution_test_report.json'
    report_file.write_text(json.dumps(final_report, indent=2, default=str, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("Final Test Summary")
    print("="*70)
    print(f"\nDatabases Setup: {successful} successful, {partial} partial, {failed} failed")
    print(f"Queries Tested: {total_tested}")
    print(f"Queries Successful: {total_successful}")
    print(f"Queries Failed: {final_report['summary']['queries_failed']}")
    print(f"Overall Success Rate: {final_report['summary']['overall_success_rate']:.2f}%")
    print(f"\nReport saved to: {report_file}")
    print("="*70)


if __name__ == '__main__':
    main()
