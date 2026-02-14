#!/usr/bin/env python3
"""
Comprehensive Query Test Runner
Reads credentials from JSON files and runs tests for all databases
"""

import json
import os
import sys
from pathlib import Path

# Load credentials
def load_credentials():
    """Load credentials from JSON files"""
    root_dir = Path(__file__).parent

    # Load PostgreSQL credentials
    pg_file = root_dir / 'results' / 'postgresql_provision_all.json'
    pg_creds = {}
    if pg_file.exists():
        with open(pg_file, 'r') as f:
            pg_data = json.load(f)
            for db_name, db_info in pg_data.items():
                if db_info.get('success'):
                    pg_creds[db_name] = db_info

    # Load Snowflake credentials
    sf_file = root_dir / 'results' / 'snowflake_credentials.json'
    sf_creds = {}
    if sf_file.exists():
        with open(sf_file, 'r') as f:
            sf_data = json.load(f)
            sf_creds = sf_data

    return pg_creds, sf_creds

def set_environment_variables(pg_creds, sf_creds):
    """Set environment variables for database connections"""
    # Set Snowflake credentials
    if sf_creds:
        os.environ['SNOWFLAKE_TOKEN'] = sf_creds.get('snowflake_token', '')
        os.environ['SNOWFLAKE_ACCOUNT'] = sf_creds.get('snowflake_account', '')
        os.environ['SNOWFLAKE_USER'] = sf_creds.get('snowflake_user', '')

    # PostgreSQL credentials are handled per-database in the test script
    # But we can set defaults
    if pg_creds:
        # Use db1 as default, but the script handles per-database ports
        db1_info = pg_creds.get('db1', {})
        if db1_info:
            os.environ['POSTGRES_HOST'] = db1_info.get('host', 'localhost')
            os.environ['POSTGRES_USER'] = db1_info.get('username', 'postgres')
            os.environ['POSTGRES_PASSWORD'] = db1_info.get('password', 'postgres')

def main():
    """Main execution"""
    print("="*70)
    print("COMPREHENSIVE QUERY TEST RUNNER")
    print("="*70)

    # Load credentials
    print("\n📋 Loading credentials...")
    pg_creds, sf_creds = load_credentials()

    if pg_creds:
        print(f"  ✅ Loaded PostgreSQL credentials for {len(pg_creds)} databases")
    else:
        print("  ⚠️  No PostgreSQL credentials found")

    if sf_creds:
        print(f"  ✅ Loaded Snowflake credentials")
    else:
        print("  ⚠️  No Snowflake credentials found")

    # Set environment variables
    set_environment_variables(pg_creds, sf_creds)

    # Import and run the test script
    print("\n🚀 Running tests...")
    root_dir = Path(__file__).parent
    test_script = root_dir / 'scripts' / 'testing' / 'test_queries_postgres.py'

    if not test_script.exists():
        print(f"  ❌ Test script not found: {test_script}")
        sys.exit(1)

    # Change to root directory and run the test script
    os.chdir(root_dir)
    sys.path.insert(0, str(root_dir))

    # Import and execute the test script
    import importlib.util
    spec = importlib.util.spec_from_file_location("test_queries", test_script)
    test_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_module)

    # Run the main function
    if hasattr(test_module, 'main'):
        test_module.main()
    else:
        print("  ❌ Test script does not have a main() function")
        sys.exit(1)

if __name__ == '__main__':
    main()
