#!/usr/bin/env python3
"""
Run Phase 3 execution testing using credentials from JSON files
Loads credentials from:
- results/postgresql_provision_all.json (PostgreSQL)
- results/databricks_credentials.json 
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional

def load_postgresql_credentials(root_dir: Path, db_num: int) -> Optional[Dict]:
    """Load PostgreSQL credentials for a specific database"""
    creds_file = root_dir / 'results' / 'postgresql_provision_all.json'

    if not creds_file.exists():
        print(f"⚠️  PostgreSQL credentials file not found: {creds_file}")
        return None

    try:
        with open(creds_file) as f:
            creds_data = json.load(f)

        db_key = f'db{db_num}'
        if db_key not in creds_data:
            print(f"⚠️  PostgreSQL credentials not found for {db_key}")
            return None

        db_creds = creds_data[db_key]
        if not db_creds.get('success', False):
            print(f"⚠️  PostgreSQL provision not successful for {db_key}")
            return None

        return {
            'host': db_creds.get('host', 'localhost'),
            'port': db_creds.get('port', 5432),
            'user': db_creds.get('username', 'postgres'),
            'password': db_creds.get('password', ''),
            'database': db_creds.get('database', f'db{db_num}')
        }
    except Exception as e:
        print(f"✗ Error loading PostgreSQL credentials: {e}")
        return None

def load_databricks_credentials(root_dir: Path) -> Optional[Dict]:
    """Load Databricks credentials"""
    creds_file = root_dir / 'results' / 'databricks_credentials.json'

    if not creds_file.exists():
        print(f"⚠️  Databricks credentials file not found: {creds_file}")
        return None

    try:
        with open(creds_file) as f:
            creds_data = json.load(f)

        return {
            'user': creds_data.get('databricks_user'),
            'password': creds_data.get('databricks_token'),  # Using token instead of password
            'account': creds_data.get('databricks_account'),
            'warehouse': os.environ.get('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            'schema': os.environ.get('SNOWFLAKE_SCHEMA', 'PUBLIC'),
            'database': os.environ.get('SNOWFLAKE_DATABASE', 'DB1'),
            'role': creds_data.get('databricks_role', 'ACCOUNTADMIN')
        }
    except Exception as e:
        print(f"✗ Error loading Databricks credentials: {e}")
        return None

def run_execution_testing(db_num: int, root_dir: Path, pg_creds: Optional[Dict], sf_creds: Optional[Dict]):
    """Run execution testing for a specific database"""
    db_dir = root_dir / f'db-{db_num}'
    exec_script = db_dir / 'scripts' / 'execution_tester.py'

    if not exec_script.exists():
        print(f"⚠️  Execution tester script not found: {exec_script}")
        return False

    print(f"\n{'='*70}")
    print(f"Running Phase 3 Execution Testing for db-{db_num}")
    print(f"{'='*70}")

    # Set environment variables for PostgreSQL
    env = os.environ.copy()
    if pg_creds:
        env['PG_HOST'] = str(pg_creds['host'])
        env['PG_PORT'] = str(pg_creds['port'])
        env['PG_USER'] = str(pg_creds['user'])
        env['PG_PASSWORD'] = str(pg_creds['password'])
        env['PG_DATABASE'] = str(pg_creds['database'])
        print(f"✓ PostgreSQL credentials configured: {pg_creds['host']}:{pg_creds['port']}/{pg_creds['database']}")
    else:
        print("⚠️  PostgreSQL credentials not available")

    # Set environment variables for Databricks
    if sf_creds:
        env['SNOWFLAKE_USER'] = str(sf_creds['user'])
        env['SNOWFLAKE_PASSWORD'] = str(sf_creds['password'])
        env['SNOWFLAKE_ACCOUNT'] = str(sf_creds['account'])
        env['SNOWFLAKE_WAREHOUSE'] = str(sf_creds.get('warehouse', 'COMPUTE_WH'))
        env['SNOWFLAKE_SCHEMA'] = str(sf_creds.get('schema', 'PUBLIC'))
        env['SNOWFLAKE_DATABASE'] = str(sf_creds.get('database', 'DB1'))
        env['SNOWFLAKE_ROLE'] = str(sf_creds.get('role', 'ACCOUNTADMIN'))
        print(f"✓ Databricks credentials configured: {sf_creds['user']}@{sf_creds['account']}")
    else:
        print("⚠️  Databricks credentials not available")

    # Run execution tester
    try:
        proc = subprocess.run(
            [sys.executable, str(exec_script)],
            cwd=str(db_dir),
            env=env,
            capture_output=False,  # Show output in real-time
            text=True
        )

        if proc.returncode == 0:
            print(f"\n✓ Phase 3 execution testing completed for db-{db_num}")
            return True
        else:
            print(f"\n✗ Phase 3 execution testing failed for db-{db_num} (exit code: {proc.returncode})")
            return False
    except Exception as e:
        print(f"\n✗ Error running execution testing: {e}")
        return False

def main():
    """Main function"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '-a' or sys.argv[1] == '--all':
            db_nums = list(range(1, 16))
        elif len(sys.argv) >= 3:
            # Range: two arguments
            try:
                start = int(sys.argv[1].replace('db-', ''))
                end = int(sys.argv[2].replace('db-', ''))
                db_nums = list(range(start, end + 1))
            except ValueError:
                db_nums = [1]
        elif sys.argv[1].startswith('db-'):
            db_nums = [int(sys.argv[1].split('db-')[1])]
        elif sys.argv[1].isdigit():
            db_nums = [int(sys.argv[1])]
        else:
            db_nums = [1]
    else:
        db_nums = list(range(1, 6))  # Default: db-1 through db-5

    print("="*70)
    print("Phase 3: Execution Testing with Credentials")
    print("="*70)

    # Load credentials
    print("\nLoading credentials...")
    sf_creds = load_databricks_credentials(root_dir)

    results = {}

    for db_num in db_nums:
        pg_creds = load_postgresql_credentials(root_dir, db_num)
        success = run_execution_testing(db_num, root_dir, pg_creds, sf_creds)
        results[f'db-{db_num}'] = {
            'success': success,
            'postgresql_configured': pg_creds is not None,
            'databricks_configured': sf_creds is not None
        }

    # Summary
    print(f"\n{'='*70}")
    print("Execution Testing Summary")
    print(f"{'='*70}")
    for db_name, result in results.items():
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        pg_status = "✓" if result['postgresql_configured'] else "✗"
        sf_status = "✓" if result['databricks_configured'] else "✗"
        print(f"{db_name}: {status} | PostgreSQL: {pg_status} | Databricks: {sf_status}")

    print(f"{'='*70}\n")

    # Save results
    results_file = root_dir / 'results' / 'execution_testing_summary.json'
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2))
    print(f"Results saved to: {results_file}")

if __name__ == '__main__':
    main()
