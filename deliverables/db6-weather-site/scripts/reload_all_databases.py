#!/usr/bin/env python3
"""
Reload All PostgreSQL Databases
Drops and recreates independent database instances for db-6 through db-15
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Tuple

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
    sys.exit(1)


class DatabaseReloader:
    """Reload PostgreSQL databases with independent instances"""
    
    def __init__(self):
        self.user = os.environ.get('USER', 'machine')
        self.host = '127.0.0.1'
        self.port = 5432
        
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
    
    def drop_database(self, db_name: str) -> bool:
        """Drop a PostgreSQL database"""
        conn = self.get_admin_connection()
        if not conn:
            return False
            
        try:
            # Terminate all connections to the database first
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                  AND pid <> pg_backend_pid();
            """, (db_name,))
            
            # Drop the database
            cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
            cursor.close()
            print(f"  ✓ Dropped database {db_name}")
            return True
        except Exception as e:
            print(f"  ✗ Error dropping database {db_name}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def create_database(self, db_name: str) -> bool:
        """Create a PostgreSQL database"""
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
    
    def enable_postgis(self, db_name: str) -> bool:
        """Enable PostGIS extension in database"""
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
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
            cursor.close()
            conn.close()
            print(f"  ✓ Enabled PostGIS extension in {db_name}")
            return True
        except Exception as e:
            print(f"  ⚠ PostGIS extension not available in {db_name}: {e}")
            return False
    
    def load_schema(self, db_name: str, schema_file: Path) -> Tuple[bool, str]:
        """Load schema SQL file into database"""
        from postgresql_schema_loader import load_schema_postgresql
        
        # Check if schema uses GEOGRAPHY (needs PostGIS)
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        enable_postgis = 'GEOGRAPHY' in schema_content.upper()
        
        # PostGIS is already enabled if needed, so pass False to avoid duplicate
        return load_schema_postgresql(db_name, schema_file, enable_postgis=False)
    
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
            
            # Convert to PostgreSQL syntax
            from postgresql_schema_loader import convert_to_postgresql
            data_sql = convert_to_postgresql(data_sql)
            
            # Split by semicolons and execute each statement
            statements = [s.strip() for s in data_sql.split(';') if s.strip()]
            
            errors = []
            executed = 0
            for i, statement in enumerate(statements):
                if not statement.strip():
                    continue
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


def reload_database(db_num: int, root_dir: Path, force_reload: bool = True) -> Dict:
    """Reload a single database"""
    db_name = f'db{db_num}'
    db_dir = root_dir / f'db-{db_num}'
    schema_file = db_dir / 'data' / 'schema.sql'
    data_file = db_dir / 'data' / 'data.sql'
    
    reloader = DatabaseReloader()
    result = {
        'database': f'db-{db_num}',
        'database_name': db_name,
        'reload_status': 'PENDING',
        'dropped': False,
        'created': False,
        'postgis_enabled': False,
        'schema_loaded': False,
        'data_loaded': False,
        'errors': []
    }
    
    print(f"\n{'='*70}")
    print(f"Reloading {db_name}")
    print(f"{'='*70}")
    
    # Drop existing database if it exists
    if force_reload and reloader.database_exists(db_name):
        if reloader.drop_database(db_name):
            result['dropped'] = True
        else:
            result['reload_status'] = 'FAILED'
            result['errors'].append('Failed to drop existing database')
            return result
    
    # Create fresh database
    if not reloader.create_database(db_name):
        result['reload_status'] = 'FAILED'
        result['errors'].append('Failed to create database')
        return result
    result['created'] = True
    
    # Enable PostGIS if schema uses GEOGRAPHY
    if schema_file.exists():
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        if 'GEOGRAPHY' in schema_content.upper():
            if reloader.enable_postgis(db_name):
                result['postgis_enabled'] = True
    
    # Load schema
    if schema_file.exists():
        success, message = reloader.load_schema(db_name, schema_file)
        result['schema_loaded'] = success
        if success:
            print(f"  ✓ Schema loaded: {message}")
        else:
            print(f"  ✗ Schema loading failed: {message}")
            result['errors'].append(f"Schema: {message}")
    else:
        print(f"  ⚠ Schema file not found: {schema_file}")
        result['errors'].append(f"Schema file not found")
    
    # Load data
    if data_file.exists():
        success, message = reloader.load_data(db_name, data_file)
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
        result['reload_status'] = 'SUCCESS'
    else:
        result['reload_status'] = 'PARTIAL' if result['data_loaded'] else 'FAILED'
    
    return result


def main():
    """Main function to reload all databases"""
    root_dir = Path(__file__).parent.parent
    databases = list(range(6, 16))  # db-6 through db-15
    
    print("="*70)
    print("PostgreSQL Database Reload - Independent Instances")
    print("="*70)
    print(f"Reloading databases: {', '.join([f'db{i}' for i in databases])}")
    print(f"Each database will be an independent PostgreSQL instance")
    print("="*70)
    
    if not PG_AVAILABLE:
        print("\n⚠️  psycopg2 not available. Cannot reload databases.")
        print("   Install with: pip install psycopg2-binary")
        return
    
    # Reload all databases
    reload_results = {}
    for db_num in databases:
        result = reload_database(db_num, root_dir, force_reload=True)
        reload_results[f'db-{db_num}'] = result
    
    # Save reload results
    reload_file = root_dir / 'database_reload_results.json'
    reload_file.write_text(json.dumps({
        'reload_date': get_est_timestamp(),
        'databases': reload_results
    }, indent=2))
    
    # Print summary
    print("\n" + "="*70)
    print("Reload Summary")
    print("="*70)
    
    successful = sum(1 for r in reload_results.values() if r['reload_status'] == 'SUCCESS')
    partial = sum(1 for r in reload_results.values() if r['reload_status'] == 'PARTIAL')
    failed = sum(1 for r in reload_results.values() if r['reload_status'] == 'FAILED')
    
    print(f"Successful: {successful}")
    print(f"Partial: {partial}")
    print(f"Failed: {failed}")
    print(f"\nResults saved to: {reload_file}")
    
    # Print database status
    print("\nDatabase Status:")
    for db_name, result in sorted(reload_results.items()):
        status_icon = "✓" if result['reload_status'] == 'SUCCESS' else "⚠" if result['reload_status'] == 'PARTIAL' else "✗"
        print(f"  {status_icon} {result['database_name']}: {result['reload_status']}")
        if result['postgis_enabled']:
            print(f"    - PostGIS enabled")
        if result['errors']:
            for error in result['errors'][:2]:
                print(f"    - {error}")


if __name__ == '__main__':
    main()
