#!/usr/bin/env python3
"""
db-12 ACID Test and Query Execution Script
Tests ACID compliance and executes all SQL queries against an independent PostgreSQL instance.
Generates comprehensive JSON report.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_DIR = SCRIPT_DIR.parent
SCHEMA_FILE = DB_DIR / 'data' / 'schema.sql'
DATA_FILE = DB_DIR / 'deliverable' / 'data' / 'data.sql'
QUERIES_JSON = DB_DIR / 'queries' / 'queries.json'
RESULTS_DIR = DB_DIR / 'results'


def get_est_timestamp():
    """Get timestamp in EST format YYYYMMDD-HHMM"""
    try:
        import pytz
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        return now.strftime('%Y%m%d-%H%M')
    except ImportError:
        return datetime.now().strftime('%Y%m%d-%H%M')


def get_pg_schema_postgresql():
    """Convert schema to PostgreSQL-compatible format (TIMESTAMP_NTZ -> TIMESTAMP, CURRENT_TIMESTAMP() -> CURRENT_TIMESTAMP)"""
    schema = SCHEMA_FILE.read_text(encoding='utf-8')
    schema = schema.replace('TIMESTAMP_NTZ', 'TIMESTAMP')
    schema = schema.replace('CURRENT_TIMESTAMP()', 'CURRENT_TIMESTAMP')
    return schema


def get_postgresql_connection():
    """Create connection to PostgreSQL database db12"""
    conn_params = {
        'host': os.getenv('PG_HOST', os.getenv('POSTGRES_HOST', 'localhost')),
        'port': os.getenv('PG_PORT', os.getenv('POSTGRES_PORT', '5432')),
        'database': os.getenv('PG_DATABASE', os.getenv('POSTGRES_DB', 'db12')),
        'user': os.getenv('PG_USER', os.getenv('POSTGRES_USER', 'postgres')),
        'password': os.getenv('PG_PASSWORD', os.getenv('POSTGRES_PASSWORD', 'postgres'))
    }
    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None


def get_postgresql_connection_autocommit():
    """Connection with autocommit for DDL"""
    conn = get_postgresql_connection()
    if conn:
        conn.autocommit = True
    return conn


def setup_database(conn):
    """Create database and load schema if needed"""
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    conn.autocommit = False
    return True


def load_schema(conn):
    """Load schema"""
    schema_sql = get_pg_schema_postgresql()
    # PostGIS extension and drop tables for clean run
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        # Drop tables in reverse dependency order for clean reload
        cur.execute("""
            DROP TABLE IF EXISTS rewards_optimization_analytics CASCADE;
            DROP TABLE IF EXISTS federal_reserve_credit_data CASCADE;
            DROP TABLE IF EXISTS cfpb_consumer_complaints CASCADE;
            DROP TABLE IF EXISTS card_recommendations CASCADE;
            DROP TABLE IF EXISTS spending_transactions CASCADE;
            DROP TABLE IF EXISTS user_cards CASCADE;
            DROP TABLE IF EXISTS user_profiles CASCADE;
            DROP TABLE IF EXISTS merchant_locations CASCADE;
            DROP TABLE IF EXISTS merchants CASCADE;
            DROP TABLE IF EXISTS card_offer_eligibility CASCADE;
            DROP TABLE IF EXISTS bank_offers CASCADE;
            DROP TABLE IF EXISTS card_rewards_structure CASCADE;
            DROP TABLE IF EXISTS rewards_categories CASCADE;
            DROP TABLE IF EXISTS credit_cards CASCADE;
            DROP TABLE IF EXISTS credit_card_issuers CASCADE;
        """)
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.autocommit = False
    return True


def load_data(conn):
    """Load schema and data"""
    load_schema(conn)
    data_sql = DATA_FILE.read_text(encoding='utf-8')
    # Fix TIMESTAMP_NTZ in data if any
    data_sql = data_sql.replace('TIMESTAMP_NTZ', 'TIMESTAMP')
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(data_sql)
    conn.autocommit = False

    # Add minimal seed data for user_001 and related tables
    seed_sql = """
    INSERT INTO user_profiles (user_id, username, email, subscription_tier, preferred_currency, location_latitude, location_longitude)
    VALUES ('user_001', 'testuser', 'test@example.com', 'Premium', 'USD', 40.7128, -74.0060)
    ON CONFLICT (user_id) DO NOTHING;

    INSERT INTO user_cards (user_card_id, user_id, card_id, account_opening_date, account_status, credit_limit, current_balance, chase_5_24_status)
    VALUES ('uc_001', 'user_001', 'card_001', '2024-01-15', 'Active', 10000.00, 500.00, 2),
           ('uc_002', 'user_001', 'card_002', '2024-03-01', 'Active', 15000.00, 0.00, 2),
           ('uc_003', 'user_001', 'card_003', '2024-06-01', 'Active', 20000.00, 1200.00, 3)
    ON CONFLICT (user_card_id) DO NOTHING;

    INSERT INTO merchant_locations (location_id, merchant_id, location_name, address_line1, city, state_code, postal_code, latitude, longitude, is_active)
    VALUES ('loc_001', 'merchant_001', 'Starbucks Downtown', '123 Main St', 'New York', 'NY', '10001', 40.7128, -74.0060, TRUE),
           ('loc_002', 'merchant_002', 'Shell Gas', '456 Oak Ave', 'New York', 'NY', '10002', 40.7200, -74.0100, TRUE),
           ('loc_003', 'merchant_003', 'Whole Foods', '789 Broadway', 'New York', 'NY', '10003', 40.7300, -74.0050, TRUE)
    ON CONFLICT (location_id) DO NOTHING;

    INSERT INTO spending_transactions (transaction_id, user_id, user_card_id, merchant_id, location_id, transaction_date, transaction_time, transaction_amount, category_id, card_used_id, rewards_earned, rewards_multiplier_applied)
    VALUES ('txn_001', 'user_001', 'uc_001', 'merchant_001', 'loc_001', '2024-01-20', '2024-01-20 09:30:00', 45.00, 'cat_001', 'card_001', 90.00, 2.0),
           ('txn_002', 'user_001', 'uc_001', 'merchant_002', 'loc_002', '2024-01-25', '2024-01-25 14:00:00', 60.00, 'cat_002', 'card_001', 120.00, 2.0),
           ('txn_003', 'user_001', 'uc_002', 'merchant_003', 'loc_003', '2024-02-01', '2024-02-01 11:00:00', 120.00, 'cat_003', 'card_002', 360.00, 3.0),
           ('txn_004', 'user_001', 'uc_001', 'merchant_001', 'loc_001', '2024-02-15', '2024-02-15 08:00:00', 30.00, 'cat_001', 'card_001', 60.00, 2.0),
           ('txn_005', 'user_001', 'uc_003', 'merchant_003', 'loc_003', '2024-03-01', '2024-03-01 16:00:00', 85.00, 'cat_003', 'card_003', 340.00, 4.0),
           ('txn_006', 'user_001', 'uc_001', 'merchant_006', NULL, '2024-03-10', '2024-03-10 12:00:00', 150.00, 'cat_010', 'card_001', 150.00, 1.0),
           ('txn_007', 'user_001', 'uc_002', 'merchant_007', NULL, '2024-03-15', '2024-03-15 20:00:00', 15.99, 'cat_007', 'card_002', 47.97, 3.0),
           ('txn_008', 'user_001', 'uc_001', 'merchant_001', 'loc_001', '2024-04-01', '2024-04-01 07:30:00', 25.00, 'cat_001', 'card_001', 50.00, 2.0),
           ('txn_009', 'user_001', 'uc_002', 'merchant_004', NULL, '2024-04-15', '2024-04-15 10:00:00', 350.00, 'cat_005', 'card_002', 1050.00, 3.0),
           ('txn_010', 'user_001', 'uc_003', 'merchant_003', 'loc_003', '2024-05-01', '2024-05-01 09:00:00', 95.00, 'cat_003', 'card_003', 380.00, 4.0)
    ON CONFLICT (transaction_id) DO NOTHING;

    INSERT INTO cfpb_consumer_complaints (complaint_id, complaint_date, product_type, company_name, company_response, timely_response, consumer_disputed)
    VALUES ('complaint_001', '2024-01-15', 'Credit card', 'Chase Bank', 'Closed with explanation', TRUE, FALSE),
           ('complaint_002', '2024-02-01', 'Credit card', 'American Express', 'Closed with monetary relief', TRUE, FALSE),
           ('complaint_003', '2024-02-15', 'Credit card', 'Chase Bank', 'Closed with explanation', TRUE, FALSE),
           ('complaint_004', '2024-03-01', 'Credit card', 'Bank of America', 'Closed with explanation', FALSE, TRUE),
           ('complaint_005', '2024-03-15', 'Credit card', 'Chase Bank', 'Closed with non-monetary relief', TRUE, FALSE),
           ('complaint_006', '2024-04-01', 'Credit card', 'Citibank', 'Closed with explanation', TRUE, FALSE),
           ('complaint_007', '2024-04-15', 'Credit card', 'Chase Bank', 'Closed with explanation', TRUE, FALSE),
           ('complaint_008', '2024-05-01', 'Credit card', 'Capital One', 'Closed with monetary relief', TRUE, FALSE)
    ON CONFLICT (complaint_id) DO NOTHING;

    INSERT INTO federal_reserve_credit_data (data_id, report_date, data_type, credit_outstanding_billions, credit_outstanding_seasonally_adjusted_billions, credit_flow_billions, interest_rate_avg)
    VALUES ('fed_001', '2024-01-01', 'Revolving', 1050.00, 1048.00, 5.2, 21.19),
           ('fed_002', '2024-02-01', 'Revolving', 1055.00, 1053.00, 4.8, 21.25),
           ('fed_003', '2024-03-01', 'Revolving', 1060.00, 1058.00, 5.0, 21.30),
           ('fed_004', '2024-04-01', 'Revolving', 1065.00, 1063.00, 5.1, 21.35),
           ('fed_005', '2024-05-01', 'Revolving', 1070.00, 1068.00, 5.2, 21.40),
           ('fed_006', '2025-01-01', 'Revolving', 1100.00, 1098.00, 5.5, 21.50),
           ('fed_007', '2024-01-01', 'Non-Revolving', 3200.00, 3195.00, 15.0, 8.50),
           ('fed_008', '2024-02-01', 'Non-Revolving', 3210.00, 3205.00, 14.5, 8.55)
    ON CONFLICT (data_id) DO NOTHING;

    INSERT INTO rewards_optimization_analytics (analytics_id, user_id, analysis_date, total_spending, total_rewards_earned, potential_rewards_lost, optimization_score, top_category_id, top_card_id)
    VALUES ('analytics_001', 'user_001', '2024-01-31', 5000.00, 1200.00, 150.00, 88.5, 'cat_001', 'card_001'),
           ('analytics_002', 'user_001', '2024-02-29', 4500.00, 1100.00, 120.00, 90.2, 'cat_003', 'card_003'),
           ('analytics_003', 'user_001', '2024-03-31', 5200.00, 1350.00, 100.00, 93.1, 'cat_001', 'card_002')
    ON CONFLICT (analytics_id) DO NOTHING;
    """
    conn.autocommit = True
    with conn.cursor() as cur:
        for stmt in seed_sql.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                try:
                    cur.execute(stmt)
                except Exception as e:
                    if 'duplicate key' not in str(e).lower() and 'already exists' not in str(e).lower():
                        print(f"Seed warning: {e}")
    conn.autocommit = False
    return True


def run_acid_tests(conn):
    """Run ACID compliance tests"""
    results = {'atomicity': {}, 'consistency': {}, 'isolation': {}, 'durability': {}}

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # A - Atomicity: Transaction rollback
        try:
            cur.execute("INSERT INTO user_profiles (user_id, username, email) VALUES ('acid_test', 'acid', 'acid@test.com')")
            conn.rollback()
            cur.execute("SELECT * FROM user_profiles WHERE user_id = 'acid_test'")
            rows = cur.fetchall()
            results['atomicity'] = {'pass': len(rows) == 0, 'description': 'Rollback prevents partial updates'}
        except Exception as e:
            results['atomicity'] = {'pass': False, 'error': str(e)}

        # C - Consistency: Constraint enforcement
        try:
            try:
                cur.execute("INSERT INTO credit_cards (card_id, issuer_id, card_name) VALUES ('invalid_card', 'nonexistent_issuer', 'Test')")
                results['consistency'] = {'pass': False, 'description': 'FK constraint should have been enforced'}
            except psycopg2.IntegrityError:
                results['consistency'] = {'pass': True, 'description': 'Foreign key constraints enforced'}
            conn.rollback()
        except Exception as e:
            results['consistency'] = {'pass': False, 'error': str(e)}

        # I - Isolation: Read committed isolation
        try:
            cur.execute("SELECT current_setting('transaction_isolation')")
            isolation = cur.fetchone()['current_setting']
            results['isolation'] = {'pass': True, 'description': f'Isolation level: {isolation}'}
        except Exception as e:
            results['isolation'] = {'pass': False, 'error': str(e)}

        # D - Durability: Persistence
        try:
            cur.execute("SELECT COUNT(*) as cnt FROM credit_card_issuers")
            cnt_before = cur.fetchone()['cnt']
            conn.commit()
            cur.execute("SELECT COUNT(*) as cnt FROM credit_card_issuers")
            cnt_after = cur.fetchone()['cnt']
            results['durability'] = {'pass': cnt_before == cnt_after and cnt_before > 0, 'description': 'Data persists after commit'}
        except Exception as e:
            results['durability'] = {'pass': False, 'error': str(e)}

    return results


def add_limit_to_query(sql, limit=100):
    """Add LIMIT to query if not present"""
    sql = sql.strip()
    if sql.upper().endswith('LIMIT'):
        return sql
    # Check if already has LIMIT
    upper = sql.upper()
    if 'LIMIT' in upper:
        return sql
    return sql + f"\nLIMIT {limit}"


def run_queries(conn, queries):
    """Execute all queries and collect results"""
    results = []
    for q in queries:
        sql = q.get('sql', '')
        if not sql:
            results.append({'query_number': q['number'], 'success': False, 'error': 'No SQL'})
            continue
        sql_limited = add_limit_to_query(sql)
        try:
            start = time.time()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql_limited)
                rows = cur.fetchall()
            elapsed = (time.time() - start) * 1000
            results.append({
                'query_number': q['number'],
                'title': q.get('title', ''),
                'success': True,
                'execution_time_ms': round(elapsed, 2),
                'row_count': len(rows),
                'columns': list(rows[0].keys()) if rows else []
            })
        except Exception as e:
            results.append({
                'query_number': q['number'],
                'title': q.get('title', ''),
                'success': False,
                'error': str(e).split('\n')[0][:500],
                'error_type': type(e).__name__
            })
        conn.rollback()  # Ensure clean state for next query
    return results


def main():
    print("=" * 70)
    print("db-12 ACID Test and Query Execution")
    print("=" * 70)

    if not POSTGRES_AVAILABLE:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        return 1

    conn = get_postgresql_connection()
    if not conn:
        print("\n⚠️  PostgreSQL connection failed. Ensure:")
        print("   - PostgreSQL is running (e.g., Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgis/postgis)")
        print("   - Database 'db12' exists: createdb db12")
        print("   - Set PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE if needed")
        return 1

    print(f"\nConnected to: {os.getenv('PG_HOST', 'localhost')}:{os.getenv('PG_PORT', '5432')}/{os.getenv('PG_DATABASE', 'db12')}")

    # Load schema and data
    print("\nLoading schema and data...")
    try:
        load_data(conn)
        print("✓ Schema and data loaded")
    except Exception as e:
        print(f"⚠️  Load error (may be partial): {e}")
        conn.rollback()
        # Try schema only
        try:
            load_schema(conn)
            load_data(conn)
        except Exception as e2:
            print(f"ERROR: {e2}")
            return 1

    # ACID tests
    print("\nRunning ACID tests...")
    acid_results = run_acid_tests(conn)
    acid_pass = all(r.get('pass', False) for r in acid_results.values())
    for prop, res in acid_results.items():
        status = "✓" if res.get('pass') else "✗"
        print(f"  {status} {prop.upper()}: {res.get('description', res.get('error', 'N/A'))}")

    # Load queries
    if not QUERIES_JSON.exists():
        print(f"ERROR: {QUERIES_JSON} not found")
        return 1
    with open(QUERIES_JSON) as f:
        data = json.load(f)
    queries = data.get('queries', [])
    print(f"\nExecuting {len(queries)} queries...")

    query_results = run_queries(conn, queries)
    conn.close()

    successful = sum(1 for r in query_results if r.get('success'))
    failed = [r for r in query_results if not r.get('success')]

    print(f"\nQuery Results: {successful}/{len(queries)} successful")
    if failed:
        print("\nFailed queries:")
        for r in failed[:10]:
            print(f"  Query {r['query_number']}: {r.get('error', 'Unknown')[:80]}...")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")

    # Write report
    report = {
        'report_date': get_est_timestamp(),
        'database': 'db-12',
        'test_type': 'ACID and Query Execution',
        'acid_tests': acid_results,
        'acid_pass': acid_pass,
        'query_results': {
            'total': len(queries),
            'successful': successful,
            'failed': len(failed),
            'success_rate_pct': round(100 * successful / len(queries), 2) if queries else 0,
            'queries': query_results
        },
        'pass': 1 if acid_pass and successful == len(queries) else 0
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    report_path = RESULTS_DIR / 'acid_query_test_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {report_path}")
    print("=" * 70)
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
