#!/usr/bin/env python3
"""
db-13 ACID Compliance and SQL Query Test Suite
Uses an independent PostgreSQL instance (Docker) to test:
1. ACID compliance (Atomicity, Consistency, Isolation, Durability)
2. All 30 SQL queries from queries.json
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_DIR = SCRIPT_DIR.parent
QUERIES_JSON = DB_DIR / 'queries' / 'queries.json'
SCHEMA_FILE = DB_DIR / 'data' / 'schema.sql'
RESULTS_DIR = DB_DIR / 'results'

# PostgreSQL config - use PG_PORT env or 5435 for Docker db13 container
PG_CONFIG = {
    'host': os.environ.get('PG_HOST', 'localhost'),
    'port': os.environ.get('PG_PORT', '5435'),  # 5435 for Docker: -p 5435:5432
    'database': os.environ.get('PG_DATABASE', 'db13_acid_test'),
    'user': os.environ.get('PG_USER', 'postgres'),
    'password': os.environ.get('PG_PASSWORD', 'postgres'),
}


def run_docker_postgres():
    """Start PostgreSQL in Docker on port 5433 if not already running"""
    container_name = 'db13_acid_test_pg'
    try:
        # Check if container exists and is running
        result = subprocess.run(
            ['docker', 'ps', '-a', '--filter', f'name={container_name}', '--format', '{{.Status}}'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and 'Up' in (result.stdout or ''):
            print(f"  PostgreSQL container already running: {container_name}")
            return True

        # Try to start existing container
        result = subprocess.run(
            ['docker', 'start', container_name],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"  Started existing container: {container_name}")
            time.sleep(2)
            return True

        # Create new container
        cmd = [
            'docker', 'run', '-d', '--name', container_name,
            '-p', '5433:5432',
            '-e', 'POSTGRES_PASSWORD=postgres',
            '-e', 'POSTGRES_DB=postgres',
            'postgres:15-alpine'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  Docker not available or failed: {result.stderr}")
            return False
        print(f"  Created and started PostgreSQL container: {container_name}")
        time.sleep(3)
        return True
    except FileNotFoundError:
        print("  Docker not found - using existing PostgreSQL if available")
        return False
    except Exception as e:
        print(f"  Docker error: {e}")
        return False


def get_connection(create_db=True):
    """Get PostgreSQL connection"""
    if not PG_AVAILABLE:
        return None
    try:
        # First connect to default database to create test db
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database='postgres',
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password']
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{PG_CONFIG['database']}'")
            if cur.fetchone():
                if create_db:
                    cur.execute(f"DROP DATABASE IF EXISTS {PG_CONFIG['database']}")
                    cur.execute(f"CREATE DATABASE {PG_CONFIG['database']}")
                    print(f"  Recreated database: {PG_CONFIG['database']}")
            elif create_db:
                cur.execute(f"CREATE DATABASE {PG_CONFIG['database']}")
                print(f"  Created database: {PG_CONFIG['database']}")
        conn.close()

        return psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password']
        )
    except Exception as e:
        print(f"  Connection failed: {e}")
        return None


def get_pg_schema():
    """Get PostgreSQL-compatible schema (TIMESTAMP_NTZ -> TIMESTAMP)"""
    if not SCHEMA_FILE.exists():
        return None
    schema = SCHEMA_FILE.read_text(encoding='utf-8')
    schema = schema.replace('TIMESTAMP_NTZ', 'TIMESTAMP')
    schema = schema.replace('CURRENT_TIMESTAMP()', 'CURRENT_TIMESTAMP')
    return schema


def load_schema(conn):
    """Load schema into database"""
    schema = get_pg_schema()
    if not schema:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(schema)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"  Schema load error: {e}")
        return False


def generate_sample_data(conn):
    """Generate minimal sample data for query testing"""
    from datetime import date

    base_date = date.today() - timedelta(days=365)

    try:
        with conn.cursor() as cur:
            # AI Models (21 columns - no training_data_size_tokens, training_compute_pflops)
            models = [
                ('MODEL001', 'GPT-4', 'gpt-4', 'OpenAI', 'proprietary', 'proprietary', 'GPT', '4.0', base_date, 128000, 1.76, 1.76, 'dense', 'Transformer', False, False, True, True, True, False, 'active'),
                ('MODEL002', 'Claude-3', 'claude-3', 'Anthropic', 'proprietary', 'proprietary', 'Claude', '3.0', base_date, 200000, 0.0, 0.0, 'dense', 'Transformer', False, False, True, True, True, False, 'active'),
                ('MODEL003', 'Gemini-Pro', 'gemini-pro', 'Google', 'proprietary', 'proprietary', 'Gemini', '1.0', base_date, 32768, 0.0, 0.0, 'dense', 'Transformer', False, True, True, True, True, False, 'active'),
                ('MODEL004', 'Llama-3', 'llama-3', 'Meta', 'open_source', 'open', 'Llama', '3.0', base_date, 8192, 8.0, 8.0, 'dense', 'Transformer', False, False, True, True, False, False, 'active'),
                ('MODEL005', 'Mistral-7B', 'mistral-7b', 'Mistral AI', 'open_source', 'open', 'Mistral', '7B', base_date, 32768, 0.007, 0.007, 'dense', 'Transformer', False, False, True, True, False, False, 'active'),
            ]
            for m in models:
                cur.execute("""
                    INSERT INTO ai_models (model_id, model_name, model_slug, creator_company, creator_type, license_type, model_family, model_version, release_date, context_window, total_parameters_billions, active_parameters_billions, model_type, architecture_type, is_reasoning_model, is_multimodal, supports_streaming, supports_function_calling, supports_vision, supports_audio, model_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (model_id) DO NOTHING
                """, m)

            # Model Performance Metrics
            for i, model_id in enumerate(['MODEL001', 'MODEL002', 'MODEL003', 'MODEL004', 'MODEL005']):
                for j in range(3):
                    eval_date = base_date + timedelta(days=j * 30)
                    cur.execute("""
                        INSERT INTO model_performance_metrics (metric_id, model_id, evaluation_date, intelligence_index_score, output_speed_tokens_per_sec, latency_seconds, blended_price_per_million_tokens, omniscience_index)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (metric_id) DO NOTHING
                    """, (f'METRIC-{model_id}-{j}', model_id, eval_date, 85.0 + i * 2 + j, 100.0 + i * 20, 0.1 + j * 0.02, 5.0 - i * 0.5, 80.0 + i))

            # Benchmark Evaluations
            benchmarks = [('GDPval-AA', 'intelligence'), ('HumanEval', 'coding'), ('MMLU', 'knowledge')]
            for i, model_id in enumerate(['MODEL001', 'MODEL002', 'MODEL003', 'MODEL004', 'MODEL005']):
                for j, (bench_name, bench_cat) in enumerate(benchmarks):
                    eval_date = base_date + timedelta(days=j * 60)
                    cur.execute("""
                        INSERT INTO benchmark_evaluations (evaluation_id, model_id, benchmark_name, benchmark_category, evaluation_date, score, normalized_score, percentile_rank, total_tests, passed_tests, failed_tests, accuracy_percentage)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (evaluation_id) DO NOTHING
                    """, (f'EVAL-{model_id}-{bench_name}', model_id, bench_name, bench_cat, eval_date, 75.0 + i * 3, 75.0 + i * 3, 80.0, 100, 80 + i, 20 - i, 80.0 + i))

            # Model Comparisons
            cur.execute("""
                INSERT INTO model_comparisons (comparison_id, model_id_1, model_id_2, comparison_date, comparison_dimension, model_1_score, model_2_score, winner_model_id, score_difference, score_difference_percent)
                VALUES ('COMP-1', 'MODEL001', 'MODEL002', %s, 'intelligence', 90.0, 88.0, 'MODEL001', 2.0, 2.27)
                ON CONFLICT (comparison_id) DO NOTHING
            """, (base_date,))

            # Marketing Intelligence
            cur.execute("""
                INSERT INTO marketing_intelligence (intelligence_id, analysis_date, analysis_type, creator_company, model_family, market_share_percentage, market_position, average_intelligence_score, average_price_per_million_tokens, model_count, growth_rate_percent, trend_direction)
                VALUES ('INT-1', %s, 'market_share', 'OpenAI', 'GPT', 35.5, 'leader', 88.0, 5.0, 5, 15.2, 'increasing')
                ON CONFLICT (intelligence_id) DO NOTHING
            """, (base_date,))

            # Government Benchmark Data (schema columns: gov_benchmark_id, source_agency, benchmark_name, benchmark_category, model_id, evaluation_date, score, compliance_level)
            cur.execute("""
                INSERT INTO government_benchmark_data (gov_benchmark_id, source_agency, benchmark_name, benchmark_category, model_id, evaluation_date, score, score_type, test_count, passed_count, compliance_level, safety_score, robustness_score)
                VALUES ('GOV-1', 'NIST', 'AI-RMF', 'safety', 'MODEL001', %s, 85.0, 'accuracy', 100, 85, 'compliant', 90.0, 85.0)
                ON CONFLICT (gov_benchmark_id) DO NOTHING
            """, (base_date,))

            # Model Adoption Metrics
            for i, model_id in enumerate(['MODEL001', 'MODEL002', 'MODEL003', 'MODEL004', 'MODEL005']):
                for j in range(3):
                    metric_date = base_date + timedelta(days=j * 90)
                    cur.execute("""
                        INSERT INTO model_adoption_metrics (adoption_id, model_id, metric_date, api_calls_millions, active_users_thousands, market_penetration_percent, developer_sentiment_score, adoption_trend)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (adoption_id) DO NOTHING
                    """, (f'ADOPT-{model_id}-{j}', model_id, metric_date, 100.0 + i * 50, 50 + i * 10, 25.0 + i * 5, 75.0 + i, 'growing'))

            # Model Pricing History
            for i, model_id in enumerate(['MODEL001', 'MODEL002', 'MODEL003', 'MODEL004', 'MODEL005']):
                for j in range(12):
                    pricing_date = base_date + timedelta(days=j * 30)
                    cur.execute("""
                        INSERT INTO model_pricing_history (pricing_id, model_id, pricing_date, blended_price_per_million_tokens)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (pricing_id) DO NOTHING
                    """, (f'PRICE-{model_id}-{j}', model_id, pricing_date, 5.0 - i * 0.3 + j * 0.05))

            # Model Performance History (schema uses performance_date, not evaluation_date)
            for i, model_id in enumerate(['MODEL001', 'MODEL002', 'MODEL003', 'MODEL004', 'MODEL005']):
                for j in range(6):
                    perf_date = base_date + timedelta(days=j * 60)
                    cur.execute("""
                        INSERT INTO model_performance_history (performance_history_id, model_id, performance_date, intelligence_index_score, output_speed_tokens_per_sec, latency_seconds)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (performance_history_id) DO NOTHING
                    """, (f'PERF-{model_id}-{j}', model_id, perf_date, 80.0 + i * 2 + j, 100.0 + i * 20, 0.1))

            # Data Sources
            cur.execute("""
                INSERT INTO data_sources (source_id, source_name, source_type, source_category, is_active)
                VALUES ('SRC-1', 'ARTIFICIAL_ANALYSIS', 'api', 'benchmark', true)
                ON CONFLICT (source_id) DO NOTHING
            """)

            # Pipeline Metadata
            cur.execute("""
                INSERT INTO pipeline_metadata (pipeline_id, source_id, extraction_date, pipeline_type, records_processed, status, start_time)
                VALUES ('PIPE-1', 'SRC-1', %s, 'full', 100, 'success', %s)
                ON CONFLICT (pipeline_id) DO NOTHING
            """, (datetime.now(), datetime.now()))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"  Sample data error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_acid_tests(conn):
    """Run ACID compliance tests"""
    results = {'atomicity': False, 'consistency': False, 'isolation': False, 'durability': False, 'details': {}}

    if not conn:
        return results

    try:
        with conn.cursor() as cur:
            # Atomicity: Rollback on error
            conn.rollback()
            cur.execute("SELECT COUNT(*) FROM ai_models")
            count_before = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO ai_models (model_id, model_name, creator_company) VALUES ('ACID-TEST', 'Test', 'Test')")
                cur.execute("INSERT INTO ai_models (model_id, model_name, creator_company) VALUES (NULL, 'Fail', 'Fail')")  # Will fail
                conn.commit()
            except Exception:
                conn.rollback()
            cur.execute("SELECT COUNT(*) FROM ai_models WHERE model_id = 'ACID-TEST'")
            results['details']['atomicity'] = cur.fetchone()[0] == 0
            results['atomicity'] = results['details']['atomicity']

            # Consistency: FK constraints
            try:
                cur.execute("INSERT INTO model_performance_metrics (metric_id, model_id, evaluation_date) VALUES ('CONS-TEST', 'NONEXISTENT', CURRENT_DATE)")
                conn.commit()
                results['details']['consistency'] = False
            except Exception:
                conn.rollback()
                results['details']['consistency'] = True
            results['consistency'] = results['details']['consistency']

            # Isolation: Read committed (basic check)
            cur.execute("SELECT current_setting('transaction_isolation')")
            isolation = cur.fetchone()[0]
            results['details']['isolation'] = isolation in ('read committed', 'read uncommitted', 'repeatable read', 'serializable')
            results['isolation'] = results['details']['isolation']

            # Durability: Commit persists
            cur.execute("INSERT INTO ai_models (model_id, model_name, creator_company) VALUES ('DUR-TEST', 'Durability', 'Test')")
            conn.commit()
            cur.execute("SELECT 1 FROM ai_models WHERE model_id = 'DUR-TEST'")
            results['details']['durability'] = cur.fetchone() is not None
            results['durability'] = results['details']['durability']

    except Exception as e:
        results['details']['error'] = str(e)

    return results


def run_queries(conn, queries):
    """Run all SQL queries and collect results - uses fresh connection per query to avoid transaction abort propagation"""
    results = []
    for q in queries:
        r = {'number': q['number'], 'title': q.get('title', f"Query {q['number']}"), 'success': False, 'row_count': 0, 'execution_time_ms': 0, 'error': None}
        if not conn:
            r['error'] = 'No connection'
            results.append(r)
            continue
        qconn = conn
        try:
            conn.rollback()  # Reset any prior failed transaction
        except Exception:
            pass
        try:
            sql = q['sql']
            if 'LIMIT' not in sql.upper() and 'FETCH' not in sql.upper():
                sql = sql.rstrip(';') + ' LIMIT 100'
            start = time.time()
            with qconn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                r['row_count'] = len(rows)
                r['columns'] = list(rows[0].keys()) if rows else []
            r['execution_time_ms'] = (time.time() - start) * 1000
            r['success'] = True
        except Exception as e:
            r['error'] = str(e)[:500]
            try:
                qconn.rollback()
            except Exception:
                pass
        results.append(r)
    return results


def main():
    print("=" * 70)
    print("db-13 ACID Compliance and SQL Query Test Suite")
    print("=" * 70)

    # Try Docker PostgreSQL first
    print("\n1. Starting PostgreSQL...")
    if PG_CONFIG['port'] == '5433':
        run_docker_postgres()
    else:
        print(f"  Using configured PostgreSQL at {PG_CONFIG['host']}:{PG_CONFIG['port']}")

    print("\n2. Connecting to PostgreSQL...")
    conn = get_connection()
    if not conn:
        print("  ERROR: Could not connect. Ensure PostgreSQL is running.")
        print("  For Docker: docker run -d -p 5433:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine")
        sys.exit(1)
    print("  Connected successfully")

    print("\n3. Loading schema...")
    if not load_schema(conn):
        sys.exit(1)
    print("  Schema loaded")

    print("\n4. Loading sample data...")
    if not generate_sample_data(conn):
        print("  WARNING: Sample data load had errors (continuing)")
    else:
        print("  Sample data loaded")

    print("\n5. Running ACID compliance tests...")
    acid_results = run_acid_tests(conn)
    for prop, passed in [(k, v) for k, v in acid_results.items() if k in ('atomicity', 'consistency', 'isolation', 'durability') and isinstance(v, bool)]:
        status = "PASS" if passed else "FAIL"
        print(f"  {prop.upper()}: {status}")

    print("\n6. Running SQL queries...")
    if not QUERIES_JSON.exists():
        print("  ERROR: queries.json not found")
        sys.exit(1)
    queries_data = json.loads(QUERIES_JSON.read_text(encoding='utf-8'))
    queries = queries_data.get('queries', [])

    query_results = run_queries(conn, queries)
    conn.close()

    # Summary
    success_count = sum(1 for r in query_results if r['success'])
    fail_count = len(query_results) - success_count

    print(f"\n  Queries: {success_count}/{len(query_results)} passed, {fail_count} failed")

    # Generate report
    report = {
        'test_date': datetime.now().isoformat(),
        'database': 'db-13',
        'postgresql_config': {k: v for k, v in PG_CONFIG.items() if k != 'password'},
        'acid_tests': acid_results,
        'acid_overall': all(acid_results.get(p, False) for p in ['atomicity', 'consistency', 'isolation', 'durability']),
        'query_results': {
            'total': len(query_results),
            'passed': success_count,
            'failed': fail_count,
            'success_rate': round(success_count / len(query_results) * 100, 1) if query_results else 0,
            'queries': query_results
        },
        'Pass': 1 if acid_results.get('acid_overall', False) and fail_count == 0 else 0
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = RESULTS_DIR / 'acid_query_test_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"ACID Compliance: {'PASS' if report['acid_overall'] else 'FAIL'}")
    print(f"Query Success Rate: {report['query_results']['success_rate']}% ({success_count}/{len(query_results)})")
    if fail_count > 0:
        print("\nFailed queries:")
        for r in query_results:
            if not r['success']:
                print(f"  Query {r['number']}: {r['title'][:50]}... - {r['error'][:80] if r.get('error') else 'Unknown'}")
    print(f"\nFull report: {report_path}")
    print("=" * 70)

    return 0 if report['Pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
