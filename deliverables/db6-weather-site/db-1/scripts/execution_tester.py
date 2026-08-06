#!/usr/bin/env python3
"""
Execution testing script for db-1 queries
Uses test_queries_postgres for PostgreSQL testing
"""

import os
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from test_queries_postgres import QueryParser, DatabaseTester

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
    parser = QueryParser()
    queries = parser.extract_queries(queries_file)

    print(f"\nExtracted {len(queries)} queries")

    # Set PostgreSQL environment variables for DatabaseTester
    if not os.environ.get('POSTGRES_HOST'):
        os.environ['POSTGRES_HOST'] = os.environ.get('PG_HOST', 'localhost')
    if not os.environ.get('POSTGRES_PORT'):
        os.environ['POSTGRES_PORT'] = os.environ.get('PG_PORT', '5432')
    if not os.environ.get('POSTGRES_USER'):
        os.environ['POSTGRES_USER'] = os.environ.get('PG_USER', os.environ.get('USER', 'postgres'))
    if not os.environ.get('POSTGRES_PASSWORD'):
        os.environ['POSTGRES_PASSWORD'] = os.environ.get('PG_PASSWORD', '')
    if not os.environ.get('POSTGRES_DB'):
        os.environ['POSTGRES_DB'] = os.environ.get('PG_DATABASE', 'db_1_validation')

    # Test queries - PostgreSQL only
    tester = DatabaseTester('db-1', 1)
    tester.test_all_queries(queries)
    tester.save_results(results_file)

    print("\n" + "="*70)
    print("Execution Testing Complete")
    print("="*70)

if __name__ == '__main__':
    main()
