#!/usr/bin/env python3
"""
Execution testing script for db-1 queries
Extends the existing test_queries_postgres.py functionality
"""

import os
import json
from pathlib import Path
from datetime import datetime
from test_queries_postgres import QueryExtractor, DatabaseTester

def main():
    """Main execution testing function"""
    script_dir = Path(__file__).parent
    queries_file = script_dir.parent / 'queries' / 'queries.md'
    results_file = script_dir.parent / 'results' / 'execution_test_results.json'

    if not queries_file.exists():
        print(f"Error: {queries_file} not found")
        return

    print("="*70)
    print("Execution Testing for db-1 queries.md")
    print("="*70)

    # Extract queries
    extractor = QueryExtractor()
    queries = extractor.extract_queries(queries_file)

    print(f"\nExtracted {len(queries)} queries")

    # Database configurations
    pg_config = {
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': int(os.environ.get('PG_PORT', 5432)),
        'user': os.environ.get('PG_USER', os.environ.get('USER', 'postgres')),
        'password': os.environ.get('PG_PASSWORD', ''),
        'database': os.environ.get('PG_DATABASE', 'db_1_validation')
    }

    sf_config = {
        'user': os.environ.get('SNOWFLAKE_USER'),
        'password': os.environ.get('SNOWFLAKE_PASSWORD'),
        'account': os.environ.get('SNOWFLAKE_ACCOUNT'),
        'warehouse': os.environ.get('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
        'schema': os.environ.get('SNOWFLAKE_SCHEMA', 'PUBLIC'),
        'database': os.environ.get('SNOWFLAKE_DATABASE', 'DB1')
    }

    # Check if configs are available
    if not all([sf_config.get('user'), sf_config.get('password'), sf_config.get('account')]):
        print("\n⚠️  Databricks credentials not found. Skipping Databricks execution testing.")
        sf_config = None

    # Test queries
    tester = DatabaseTester('db-1')
    tester.test_all_queries(queries, pg_config, sf_config)
    tester.save_results(results_file)

    print("\n" + "="*70)
    print("Execution Testing Complete")
    print("="*70)

if __name__ == '__main__':
    main()
