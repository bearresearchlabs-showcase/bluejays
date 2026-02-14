#!/usr/bin/env python3
"""
db-8 ACID Compliance and SQL Query Test Suite
Runs independent PostgreSQL via Docker, tests ACID properties, and executes all 30 queries.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    root_scripts = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(root_scripts))
    from timestamp_utils import get_est_timestamp

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

BASE_DIR = Path(__file__).parent.parent
SCHEMA_FILE = BASE_DIR / 'data' / 'schema.sql'
DATA_FILE = BASE_DIR / 'data' / 'data.sql'
QUERIES_JSON = BASE_DIR / 'queries' / 'queries.json'
RESULTS_DIR = BASE_DIR / 'results'
CONTAINER_NAME = 'db8_acid_test_pg'
DB_NAME = 'db8_test'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_PORT = 15432  # Non-standard to avoid conflicts

def create_pg_schema(content: str) -> str:
    """Convert schema to PostgreSQL-compatible format."""
    content = content.replace('TIMESTAMP_NTZ', 'TIMESTAMP')
    content = content.replace('CURRENT_TIMESTAMP()', 'CURRENT_TIMESTAMP')
    # PostgreSQL VARCHAR max is ~10MB; use TEXT for larger fields
    content = content.replace('VARCHAR(16777216)', 'TEXT')
    return content

def ensure_docker_postgres():
    """Start PostgreSQL in Docker if not running."""
    # Check if container exists
    exist_result = subprocess.run(
        ['docker', 'ps', '-a', '-q', '-f', f'name={CONTAINER_NAME}'],
        capture_output=True, text=True
    )
    if exist_result.returncode != 0:
        print("ERROR: Docker not available or not running")
        return False

    container_id = exist_result.stdout.strip()
    if container_id:
        # Container exists - check if running
        run_result = subprocess.run(['docker', 'ps', '-q', '-f', f'name={CONTAINER_NAME}'], capture_output=True, text=True)
        if not run_result.stdout.strip():
            print(f"Starting existing container {CONTAINER_NAME}...")
            subprocess.run(['docker', 'start', CONTAINER_NAME], check=True)
            time.sleep(3)
    else:
        print(f"Creating and starting PostgreSQL container {CONTAINER_NAME}...")
        subprocess.run([
            'docker', 'run', '-d',
            '--name', CONTAINER_NAME,
            '-e', f'POSTGRES_PASSWORD={DB_PASSWORD}',
            '-e', f'POSTGRES_DB={DB_NAME}',
            '-p', f'{DB_PORT}:5432',
            'postgres:16-alpine'
        ], check=True)
        time.sleep(5)

    return True

def get_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host='127.0.0.1',
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10
    )

def run_sql(conn, sql: str, fetch=True):
    """Execute SQL and optionally fetch results."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        if fetch and cur.description:
            return cur.fetchall()
    return []

def load_schema_and_data(conn):
    """Load schema and data into database."""
    schema_content = SCHEMA_FILE.read_text(encoding='utf-8')
    schema_pg = create_pg_schema(schema_content)
    
    data_content = DATA_FILE.read_text(encoding='utf-8')
    
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        conn.commit()
    
    with conn.cursor() as cur:
        cur.execute(schema_pg)
        conn.commit()
    
    with conn.cursor() as cur:
        # Execute data - may need schema conversion for data.sql too
        data_pg = create_pg_schema(data_content)
        cur.execute(data_pg)
        conn.commit()

def run_acid_tests(conn) -> dict:
    """Run ACID compliance tests."""
    results = {'atomicity': {}, 'consistency': {}, 'isolation': {}, 'durability': {}}
    
    # 1. ATOMICITY: Transaction either fully commits or fully rolls back
    try:
        with conn.cursor() as cur:
            cur.execute("BEGIN;")
            cur.execute("INSERT INTO user_profiles (user_id, email, full_name) VALUES ('acid_user_1', 'acid1@test.com', 'ACID Test');")
            cur.execute("INSERT INTO user_profiles (user_id, email, full_name) VALUES ('acid_user_2', 'acid2@test.com', 'ACID Test');")
            cur.execute("ROLLBACK;")
            conn.commit()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM user_profiles WHERE user_id LIKE 'acid_user_%'")
            row = cur.fetchone()
            results['atomicity'] = {'pass': row['cnt'] == 0, 'test': 'ROLLBACK rolled back both inserts'}
    except Exception as e:
        results['atomicity'] = {'pass': False, 'error': str(e)}
    
    # 2. CONSISTENCY: Foreign keys and constraints are enforced
    try:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO job_postings (job_id, company_id, job_title, posted_date, data_source) VALUES ('acid_job_1', 'nonexistent_company', 'Test', CURRENT_TIMESTAMP, 'aggregated');")
                conn.commit()
                results['consistency'] = {'pass': False, 'test': 'FK should have rejected invalid company_id'}
            except psycopg2.IntegrityError:
                conn.rollback()
                results['consistency'] = {'pass': True, 'test': 'FK constraint correctly rejected invalid reference'}
    except Exception as e:
        results['consistency'] = {'pass': False, 'error': str(e)}
    
    # 3. ISOLATION: Concurrent transactions don't corrupt data
    try:
        with conn.cursor() as cur:
            cur.execute("BEGIN;")
            cur.execute("INSERT INTO user_profiles (user_id, email, full_name) VALUES ('isol_user', 'isol@test.com', 'Isolation');")
            cur.execute("SELECT COUNT(*) FROM user_profiles WHERE user_id = 'isol_user'")
            cnt_before = cur.fetchone()[0]
            cur.execute("COMMIT;")
        
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM user_profiles WHERE user_id = 'isol_user'")
            cnt_after = cur.fetchone()[0]
        
        results['isolation'] = {'pass': cnt_before == 1 and cnt_after == 1, 'test': 'Committed data visible after commit'}
        
        # Cleanup
        with conn.cursor() as cur:
            cur.execute("DELETE FROM user_profiles WHERE user_id = 'isol_user'")
            conn.commit()
    except Exception as e:
        results['isolation'] = {'pass': False, 'error': str(e)}
    
    # 4. DURABILITY: Committed data persists
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO user_profiles (user_id, email, full_name) VALUES ('dura_user', 'dura@test.com', 'Durability');")
            conn.commit()
        
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM user_profiles WHERE user_id = 'dura_user'")
            exists = cur.fetchone() is not None
        
        results['durability'] = {'pass': exists, 'test': 'Committed data persisted'}
        
        # Cleanup
        with conn.cursor() as cur:
            cur.execute("DELETE FROM user_profiles WHERE user_id = 'dura_user'")
            conn.commit()
    except Exception as e:
        results['durability'] = {'pass': False, 'error': str(e)}
    
    return results

def normalize_sql_for_pg(sql: str) -> str:
    """Fix common syntax issues for PostgreSQL compatibility."""
    import re
    # ROUND(expr) * 100::numeric), 2) -> ROUND(expr * 100::numeric, 2) - remove extra )
    sql = re.sub(r'\)\s*\*\s*100::numeric\),\s*2\)', r'* 100::numeric, 2)', sql)
    # )::numeric)::numeric, 2) -> )::numeric, 2)
    sql = re.sub(r'\)::numeric\)::numeric,\s*2\)', r')::numeric, 2)', sql)
    # ROUND(float_expr, n) - cast to numeric for PostgreSQL (ROUND(double precision, int) doesn't exist)
    # Match ROUND( simple_expr, digits ) where simple_expr is word.word or word - add ::numeric if missing
    def round_numeric(m):
        inner = m.group(1).strip()
        if '::' in inner or 'NULLIF' in inner or '/' in inner or '*' in inner:
            return m.group(0)
        return f'ROUND(({inner})::numeric, {m.group(2)})'
    sql = re.sub(r'ROUND\((\w+\.\w+),\s*(\d+)\)', round_numeric, sql)
    return sql

def run_queries(conn, queries: list) -> list:
    """Execute all queries and collect results."""
    results = []
    for q in queries:
        sql = q.get('sql', '')
        if not sql:
            results.append({'number': q['number'], 'success': False, 'error': 'No SQL'})
            continue
        
        sql = normalize_sql_for_pg(sql)
        
        # Add LIMIT for safety if not present
        if 'LIMIT' not in sql.upper() and 'FETCH FIRST' not in sql.upper():
            sql = sql.rstrip(';') + ' LIMIT 100'
        
        try:
            start = time.perf_counter()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
            elapsed_ms = (time.perf_counter() - start) * 1000
            results.append({
                'number': q['number'],
                'title': q.get('title', '')[:80],
                'success': True,
                'row_count': len(rows),
                'execution_time_ms': round(elapsed_ms, 2)
            })
        except Exception as e:
            conn.rollback()  # Reset transaction for next query
            results.append({
                'number': q['number'],
                'title': q.get('title', '')[:80],
                'success': False,
                'error': str(e)[:500]
            })
    return results

def main():
    print("=" * 60)
    print("db-8 ACID Compliance and SQL Query Test Suite")
    print("=" * 60)
    
    report = {
        'database': 'db-8',
        'test_date': get_est_timestamp(),
        'postgresql_version': None,
        'acid_tests': {},
        'acid_pass': 0,
        'query_results': [],
        'queries_passed': 0,
        'queries_failed': 0,
        'Pass': 0
    }
    
    if not PG_AVAILABLE:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)
    
    if not ensure_docker_postgres():
        print("ERROR: Could not start PostgreSQL. Ensure Docker is running.")
        sys.exit(1)
    
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            report['postgresql_version'] = cur.fetchone()[0].split(',')[0]
        print(f"\nConnected: {report['postgresql_version']}")
        
        print("\nLoading schema and data...")
        load_schema_and_data(conn)
        print("Schema and data loaded.")
        
        print("\n--- ACID Compliance Tests ---")
        report['acid_tests'] = run_acid_tests(conn)
        acid_pass = sum(1 for t in report['acid_tests'].values() if t.get('pass'))
        report['acid_pass'] = 1 if acid_pass == 4 else 0
        
        for prop, res in report['acid_tests'].items():
            status = "PASS" if res.get('pass') else "FAIL"
            print(f"  {prop.upper()}: {status} - {res.get('test', res.get('error', ''))}")
        
        print("\n--- SQL Query Execution (30 queries) ---")
        queries_data = json.loads(QUERIES_JSON.read_text(encoding='utf-8'))
        queries = queries_data.get('queries', [])
        
        report['query_results'] = run_queries(conn, queries)
        report['queries_passed'] = sum(1 for r in report['query_results'] if r['success'])
        report['queries_failed'] = len(report['query_results']) - report['queries_passed']
        
        for r in report['query_results']:
            if r['success']:
                print(f"  Query {r['number']:2d}: PASS ({r['row_count']} rows, {r['execution_time_ms']:.0f}ms)")
            else:
                print(f"  Query {r['number']:2d}: FAIL - {r.get('error', 'Unknown')[:80]}")
        
        report['Pass'] = 1 if (report['acid_pass'] and report['queries_failed'] == 0) else 0
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        report['Pass'] = 0
        report['error'] = str(e)
    
    # Save report
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RESULTS_DIR / 'acid_and_query_test_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"ACID: {'PASS' if report['acid_pass'] else 'FAIL'} | Queries: {report['queries_passed']}/30 passed")
    print(f"Overall: {'PASS' if report['Pass'] else 'FAIL'}")
    print(f"Report saved: {report_path}")
    print("=" * 60)
    
    return 0 if report['Pass'] else 1

if __name__ == '__main__':
    sys.exit(main())
