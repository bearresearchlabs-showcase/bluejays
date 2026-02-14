#!/usr/bin/env python3
"""
Test SQL queries on different database instances.
Creates test databases and runs execution tests.
"""
import os
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent

def test_on_postgresql():
    """Test queries on PostgreSQL instance"""
    print("=" * 70)
    print("Testing on PostgreSQL")
    print("=" * 70)
    
    # Check if PostgreSQL is available
    try:
        import psycopg2
        from psycopg2 import sql
        
        # Try to connect
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST', 'localhost'),
            port=os.getenv('PG_PORT', '5432'),
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', ''),
            database='postgres'  # Connect to default database first
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("✅ PostgreSQL connection successful")
        
        # Test each database
        for db_num in [1, 2, 3, 4, 5]:
            db_name = f"db_{db_num}_test"
            print(f"\nTesting db-{db_num} on PostgreSQL...")
            
            # Create test database if it doesn't exist
            try:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_name)
                ))
                print(f"  ✅ Created test database: {db_name}")
            except psycopg2.errors.DuplicateDatabase:
                print(f"  ℹ️  Database {db_name} already exists")
            
            # Run execution tester
            tester_script = BASE / f"db-{db_num}" / "scripts" / "execution_tester.py"
            if tester_script.exists():
                print(f"  Running execution tester...")
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(tester_script)],
                    cwd=str(BASE / f"db-{db_num}"),
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"  ✅ Execution test completed")
                else:
                    print(f"  ⚠️  Execution test had issues")
                    print(f"     {result.stderr[:200]}")
        
        cur.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("SQL Query Testing on Different Database Instances")
    print("=" * 70)
    
    pg_result = test_on_postgresql()
    
    print("\n" + "=" * 70)
    print("Testing Summary")
    print("=" * 70)
    print(f"PostgreSQL: {'✅ Available' if pg_result else '❌ Not available'}")
    print("=" * 70)
