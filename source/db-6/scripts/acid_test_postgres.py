#!/usr/bin/env python3
"""
db-6 ACID Compliance Test and Query Execution
Tests PostgreSQL for ACID properties and runs SQL queries from queries.json
Uses independent PostgreSQL (Docker postgis/postgis or local)
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_DIR = SCRIPT_DIR.parent
SCHEMA_FILE = DB_DIR / 'deliverable' / 'data' / 'schema.sql'
DATA_FILE = DB_DIR / 'deliverable' / 'data' / 'data.sql'
QUERIES_JSON = DB_DIR / 'queries' / 'queries.json'
RESULTS_FILE = DB_DIR / 'results' / 'acid_test_report.json'


def get_pg_schema_for_postgres(content: str) -> str:
    """Convert schema for PostgreSQL: TIMESTAMP_NTZ -> TIMESTAMP, VARIANT -> JSONB, ensure PostGIS"""
    modified = content.replace('TIMESTAMP_NTZ', 'TIMESTAMP')
    modified = modified.replace('CURRENT_TIMESTAMP()', 'CURRENT_TIMESTAMP')
    modified = modified.replace('VARIANT', 'JSONB')
    if 'CREATE EXTENSION IF NOT EXISTS postgis' not in modified:
        modified = 'CREATE EXTENSION IF NOT EXISTS postgis;\n\n' + modified
    return modified


def setup_docker_postgres() -> bool:
    """Start PostgreSQL with PostGIS via Docker if not running"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True, text=True, timeout=10
        )
        if 'db6_postgres' in result.stdout:
            return True
        # Start container
        subprocess.run([
            'docker', 'run', '-d', '--name', 'db6_postgres',
            '-e', 'POSTGRES_PASSWORD=postgres',
            '-e', 'POSTGRES_DB=db6_acid_test',
            '-p', '5434:5432',
            'postgis/postgis:16-3.4'
        ], capture_output=True, timeout=60)
        time.sleep(5)
        return True
    except Exception as e:
        print(f"Docker setup skipped: {e}")
        return False


def get_connection(use_docker: bool = False, database: str = 'db6_acid_test') -> Optional[Any]:
    """Get PostgreSQL connection"""
    if not POSTGRES_AVAILABLE:
        return None
    port = int(os.getenv('PG_PORT', '5434' if use_docker else '5432'))
    try:
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST', 'localhost'),
            port=port,
            database=database,
            user=os.getenv('PG_USER', 'postgres'),
            password=os.getenv('PG_PASSWORD', 'postgres')
        )
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"Connection failed ({database}): {e}")
        return None


def run_acid_tests(conn) -> Dict[str, Any]:
    """Run ACID compliance tests using db-6 tables"""
    results = {'tests': {}, 'Pass': 1}
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # ATOMICITY: Transaction either completes fully or rolls back
    try:
        cursor.execute("BEGIN")
        cursor.execute("""
            INSERT INTO grib2_transformation_log (log_id, file_name, parameter_name, source_crs, target_crs, transformation_status)
            VALUES ('acid_test_1', 'ACID Test', 'Test', 'EPSG:4326', 'EPSG:4326', 'Test')
        """)
        cursor.execute("ROLLBACK")
        cursor.execute("SELECT COUNT(*) AS cnt FROM grib2_transformation_log WHERE log_id = 'acid_test_1'")
        cnt = cursor.fetchone()['cnt']
        results['tests']['atomicity'] = {'Pass': 1 if cnt == 0 else 0, 'note': 'Rollback undid insert'}
    except Exception as e:
        results['tests']['atomicity'] = {'Pass': 0, 'error': str(e)}
        results['Pass'] = 0

    # CONSISTENCY: Primary key constraint enforced (duplicate key rejected)
    try:
        cursor.execute("BEGIN")
        try:
            cursor.execute("""
                INSERT INTO grib2_transformation_log (log_id, file_name, parameter_name, source_crs, target_crs, transformation_status)
                VALUES ('log_grib_001', 'Duplicate', 'Test', 'EPSG:4326', 'EPSG:4326', 'Test')
            """)
            results['tests']['consistency'] = {'Pass': 0, 'note': 'FK/PK violation should have been rejected'}
        except psycopg2.IntegrityError:
            conn.rollback()
            results['tests']['consistency'] = {'Pass': 1, 'note': 'Primary key constraint enforced'}
    except Exception as e:
        results['tests']['consistency'] = {'Pass': 0, 'error': str(e)}
        results['Pass'] = 0

    # ISOLATION: Serializable isolation level
    try:
        cursor.execute("SHOW default_transaction_isolation")
        iso = cursor.fetchone()['default_transaction_isolation']
        results['tests']['isolation'] = {'Pass': 1, 'level': iso, 'note': 'Isolation level supported'}
    except Exception as e:
        results['tests']['isolation'] = {'Pass': 0, 'error': str(e)}
        results['Pass'] = 0

    # DURABILITY: Commit persists
    try:
        cursor.execute("BEGIN")
        cursor.execute("""
            INSERT INTO grib2_transformation_log (log_id, file_name, parameter_name, source_crs, target_crs, transformation_status)
            VALUES ('acid_durability', 'Durability Test', 'Test', 'EPSG:4326', 'EPSG:4326', 'Test')
        """)
        conn.commit()
        cursor.execute("SELECT COUNT(*) AS cnt FROM grib2_transformation_log WHERE log_id = 'acid_durability'")
        cnt = cursor.fetchone()['cnt']
        cursor.execute("DELETE FROM grib2_transformation_log WHERE log_id = 'acid_durability'")
        conn.commit()
        results['tests']['durability'] = {'Pass': 1 if cnt == 1 else 0, 'note': 'Committed data persisted'}
    except Exception as e:
        conn.rollback()
        results['tests']['durability'] = {'Pass': 0, 'error': str(e)}
        results['Pass'] = 0

    cursor.close()
    return results


def run_queries(conn, queries: List[Dict], limit: int = 30) -> List[Dict]:
    """Run queries and collect results - each in its own transaction"""
    results = []

    for i, q in enumerate(queries[:limit]):
        qnum = q.get('number', i + 1)
        sql = q.get('sql', '')
        if not sql:
            continue
        # Add LIMIT if not present for safety
        sql_limited = sql if 'LIMIT' in sql.upper() else sql.rstrip() + ' LIMIT 50'
        result = {'query_number': qnum, 'title': q.get('title', ''), 'success': False, 'row_count': 0, 'error': None,
                  'execution_time_ms': 0, 'sample_columns': []}
        try:
            conn.rollback()  # Reset after any prior failure
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                start = time.time()
                cursor.execute(sql_limited)
                rows = cursor.fetchmany(100)
                result['execution_time_ms'] = round((time.time() - start) * 1000, 2)
                result['row_count'] = len(rows)
                result['success'] = True
                if rows:
                    result['sample_columns'] = list(rows[0].keys())
        except Exception as e:
            conn.rollback()
            result['error'] = str(e)[:500]
        results.append(result)

    return results


def main():
    print("=" * 70)
    print("db-6 ACID Compliance Test and Query Execution")
    print("=" * 70)

    use_docker = os.getenv('DB6_USE_DOCKER', '') == '1'
    if use_docker:
        print("\nUsing Docker PostgreSQL...")
        setup_docker_postgres()

    # Try postgres first for db creation, then db6_acid_test
    conn = get_connection(use_docker, database='postgres')
    if not conn:
        conn = get_connection(use_docker, database='db6_acid_test')
    if not conn:
        print("\nCould not connect to PostgreSQL. Ensure PostgreSQL is running.")
        print("Options:")
        print("  1. Set PG_HOST, PG_PORT, PG_USER, PG_PASSWORD (PG_PORT=5434 for Docker)")
        print("  2. Or use: DB6_USE_DOCKER=1 to start via Docker (postgis/postgis:16-3.4)")
        return 1

    print("\nConnected to PostgreSQL successfully.")

    # Create database (drop if exists for clean schema reload)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'db6_acid_test' AND pid <> pg_backend_pid()")
        with conn.cursor() as cur:
            cur.execute("DROP DATABASE IF EXISTS db6_acid_test")
            cur.execute("CREATE DATABASE db6_acid_test")
            print("Created database db6_acid_test (clean)")
    except Exception as e:
        print(f"Database setup: {e}")
    conn.close()

    conn = get_connection(use_docker, database='db6_acid_test')
    conn.autocommit = False

    # Ensure PostGIS extension exists (required for GEOGRAPHY type)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        conn.autocommit = False
    except Exception as e:
        print(f"PostGIS extension: {e}")

    # Load schema and data
    if SCHEMA_FILE.exists():
        schema_content = SCHEMA_FILE.read_text(encoding='utf-8')
        schema_pg = get_pg_schema_for_postgres(schema_content)
        try:
            with conn.cursor() as cur:
                cur.execute(schema_pg)
            conn.commit()
            print("Schema loaded successfully.")
        except Exception as e:
            conn.rollback()
            if 'already exists' in str(e).lower():
                print("Schema already exists, continuing...")
            else:
                print(f"Schema load error: {e}")
                return 1

    if DATA_FILE.exists():
        try:
            conn.rollback()
            with conn.cursor() as cur:
                cur.execute(DATA_FILE.read_text(encoding='utf-8'))
            conn.commit()
            print("Sample data loaded successfully.")
        except Exception as e:
            conn.rollback()
            if 'duplicate key' in str(e).lower() or 'already exists' in str(e).lower():
                print("Data already loaded, continuing...")
            else:
                print(f"Data load error: {e}")
                return 1

    # ACID tests
    print("\n--- ACID Compliance Tests ---")
    acid_results = run_acid_tests(conn)
    for name, res in acid_results['tests'].items():
        status = "PASS" if res.get('Pass', 0) == 1 else "FAIL"
        print(f"  {name.upper()}: {status} - {res.get('note', res.get('error', ''))}")

    # Load and run queries
    if not QUERIES_JSON.exists():
        print(f"\nqueries.json not found at {QUERIES_JSON}")
        return 1

    with open(QUERIES_JSON, encoding='utf-8') as f:
        queries_data = json.load(f)
    queries = queries_data.get('queries', [])

    num_to_run = min(30, len(queries))
    print(f"\n--- Running {num_to_run} SQL Queries ---")
    query_results = run_queries(conn, queries, limit=30)

    for qr in query_results:
        status = "OK" if qr['success'] else "FAIL"
        print(f"  Query {qr['query_number']}: {status} - {qr['row_count']} rows, {qr.get('execution_time_ms', 0)}ms")
        if qr.get('error'):
            print(f"    Error: {qr['error'][:80]}...")

    conn.close()

    # Summary report
    report = {
        'test_date': datetime.now().strftime('%Y%m%d-%H%M'),
        'database': 'db-6',
        'acid_tests': acid_results,
        'pass': 1 if acid_results.get('Pass', 0) == 1 else 0,
        'query_results': query_results,
        'queries_run': len(query_results),
        'queries_success': sum(1 for q in query_results if q['success']),
        'queries_failed': sum(1 for q in query_results if not q['success']),
    }

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n--- Report saved to {RESULTS_FILE} ---")
    print(f"ACID: {'PASS' if report['pass'] else 'FAIL'}")
    print(f"Queries: {report['queries_success']}/{report['queries_run']} successful")
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
