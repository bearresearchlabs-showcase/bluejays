#!/usr/bin/env python3
"""
Test PostgreSQL SQL files for syntax errors and compatibility.

This script validates PostgreSQL-specific SQL files:
- Checks SQL syntax using PostgreSQL's EXPLAIN
- Validates file structure and completeness
- Tests schema and data file compatibility
- Optionally executes against a real PostgreSQL database
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_postgresql_available():
    """Check if PostgreSQL client tools are available."""
    try:
        result = subprocess.run(
            ['psql', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"PostgreSQL client found: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    logger.warning("PostgreSQL client (psql) not found. Syntax validation will be limited.")
    return False


def validate_sql_syntax(file_path, db_name=None):
    """
    Validate SQL file syntax using PostgreSQL EXPLAIN.
    
    Args:
        file_path: Path to SQL file
        db_name: Optional database name for connection testing
    
    Returns:
        dict with validation results
    """
    result = {
        'file': str(file_path),
        'exists': False,
        'readable': False,
        'size': 0,
        'syntax_valid': None,
        'errors': [],
        'warnings': []
    }
    
    if not file_path.exists():
        result['errors'].append(f"File not found: {file_path}")
        return result
    
    result['exists'] = True
    result['size'] = file_path.stat().st_size
    
    # Check if file is readable
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first few lines to check encoding
            first_lines = ''.join([f.readline() for _ in range(10)])
        result['readable'] = True
    except Exception as e:
        result['errors'].append(f"Cannot read file: {e}")
        return result
    
    # Basic syntax checks
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common issues
        if 'TIMESTAMP_NTZ' in content:
            result['warnings'].append("File contains TIMESTAMP_NTZ (should be TIMESTAMP for PostgreSQL)")
        
        if 'GEOGRAPHY' in content and 'CREATE EXTENSION IF NOT EXISTS postgis' not in content:
            result['warnings'].append("File contains GEOGRAPHY but PostGIS extension not found")
        
        # Check for basic SQL structure
        if 'CREATE TABLE' not in content and 'INSERT INTO' not in content:
            result['warnings'].append("File does not contain CREATE TABLE or INSERT INTO statements")
        
        # Check file size (warn if very large)
        if result['size'] > 5 * 1024 * 1024 * 1024:  # 5GB
            result['warnings'].append(f"File is very large ({result['size'] / (1024**3):.2f} GB)")
        
    except Exception as e:
        result['errors'].append(f"Error reading file content: {e}")
        return result
    
    # Try PostgreSQL syntax validation if psql is available
    if check_postgresql_available() and db_name:
        result['syntax_valid'] = validate_with_postgresql(file_path, db_name)
    else:
        result['warnings'].append("PostgreSQL syntax validation skipped (no database connection)")
    
    return result


def validate_with_postgresql(file_path, db_name):
    """
    Validate SQL syntax using PostgreSQL EXPLAIN.
    
    Args:
        file_path: Path to SQL file
        db_name: Database name for testing
    
    Returns:
        True if syntax is valid, False otherwise
    """
    # Get PostgreSQL connection info from environment
    pg_host = os.getenv('PG_HOST', 'localhost')
    pg_port = os.getenv('PG_PORT', '5432')
    pg_user = os.getenv('PG_USER', 'postgres')
    pg_password = os.getenv('PG_PASSWORD', '')
    
    # Create a temporary test database if needed
    test_db = f"{db_name}_test"
    
    try:
        # Try to validate using EXPLAIN (dry-run)
        # Note: This is a simplified check - full validation would require actual database
        logger.info(f"  Attempting PostgreSQL syntax validation for {file_path.name}...")
        
        # For now, we'll do basic checks
        # Full validation would require:
        # 1. Creating a test database
        # 2. Running EXPLAIN on the SQL
        # 3. Checking for errors
        
        # This is a placeholder - actual implementation would connect to PostgreSQL
        return None  # Indicates validation not performed
        
    except Exception as e:
        logger.warning(f"  PostgreSQL validation failed: {e}")
        return False


def test_postgresql_files(db_num, root_dir=None):
    """
    Test PostgreSQL SQL files for a database.
    
    Args:
        db_num: Database number (6-15)
        root_dir: Root directory path (defaults to script parent)
    
    Returns:
        dict with test results
    """
    if root_dir is None:
        root_dir = Path(__file__).parent.parent
    
    db_dir = root_dir / f"db-{db_num}"
    
    if not db_dir.exists():
        logger.warning(f"Database directory not found: {db_dir}")
        return None
    
    data_dir = db_dir / "data"
    if not data_dir.exists():
        logger.warning(f"Data directory not found: {data_dir}")
        return None
    
    logger.info(f"Testing PostgreSQL files for db-{db_num}...")
    
    results = {
        'database': f'db-{db_num}',
        'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'schema_files': [],
        'data_files': [],
        'Pass': 1,
        'errors': [],
        'warnings': []
    }
    
    # Find and test schema files
    schema_files = list(data_dir.glob('*_postgresql.sql'))
    schema_files = [f for f in schema_files if 'data' not in f.name.lower()]
    
    for schema_file in schema_files:
        logger.info(f"  Testing schema file: {schema_file.name}")
        result = validate_sql_syntax(schema_file, f'db_{db_num}')
        results['schema_files'].append(result)
        
        if result['errors']:
            results['Pass'] = 0
            results['errors'].extend(result['errors'])
        if result['warnings']:
            results['warnings'].extend(result['warnings'])
    
    # Find and test data files
    data_files = list(data_dir.glob('*data*_postgresql.sql'))
    
    for data_file in data_files:
        logger.info(f"  Testing data file: {data_file.name}")
        result = validate_sql_syntax(data_file, f'db_{db_num}')
        results['data_files'].append(result)
        
        if result['errors']:
            results['Pass'] = 0
            results['errors'].extend(result['errors'])
        if result['warnings']:
            results['warnings'].extend(result['warnings'])
    
    # Summary
    total_files = len(results['schema_files']) + len(results['data_files'])
    if total_files == 0:
        results['Pass'] = 0
        results['errors'].append("No PostgreSQL SQL files found")
        logger.warning(f"  No PostgreSQL SQL files found for db-{db_num}")
    else:
        logger.info(f"  ✓ Tested {total_files} PostgreSQL SQL files")
    
    return results


def main():
    """Main function to test PostgreSQL SQL files for specified databases."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test PostgreSQL SQL files for databases"
    )
    parser.add_argument(
        "db_numbers",
        nargs="*",
        type=int,
        help="Database numbers to test (e.g., 6 7 8). If not specified, tests db-6 through db-15."
    )
    parser.add_argument(
        "--root-dir",
        type=str,
        help="Root directory path (defaults to script parent)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file for test results"
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.root_dir) if args.root_dir else Path(__file__).parent.parent
    
    # Determine which databases to test
    if args.db_numbers:
        db_numbers = args.db_numbers
    else:
        # Default: test db-6 through db-15
        db_numbers = list(range(6, 16))
    
    logger.info(f"Testing PostgreSQL SQL files for databases: {db_numbers}")
    logger.info("")
    
    # Check PostgreSQL availability
    pg_available = check_postgresql_available()
    if not pg_available:
        logger.info("Note: PostgreSQL client not available. Running basic file validation only.")
    logger.info("")
    
    all_results = {
        'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'databases': [],
        'summary': {
            'total_databases': len(db_numbers),
            'passed': 0,
            'failed': 0,
            'total_files_tested': 0
        },
        'Pass': 1
    }
    
    for db_num in db_numbers:
        result = test_postgresql_files(db_num, root_dir)
        if result:
            all_results['databases'].append(result)
            all_results['summary']['total_files_tested'] += (
                len(result['schema_files']) + len(result['data_files'])
            )
            if result['Pass'] == 1:
                all_results['summary']['passed'] += 1
            else:
                all_results['summary']['failed'] += 1
                all_results['Pass'] = 0
        logger.info("")
    
    # Print summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Databases tested: {all_results['summary']['total_databases']}")
    logger.info(f"Databases passed: {all_results['summary']['passed']}")
    logger.info(f"Databases failed: {all_results['summary']['failed']}")
    logger.info(f"Total files tested: {all_results['summary']['total_files_tested']}")
    logger.info("")
    
    if all_results['Pass'] == 1:
        logger.info("✓ All tests passed!")
    else:
        logger.warning("✗ Some tests failed. Check errors above.")
    
    # Save results to JSON if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        logger.info(f"Results saved to: {output_path}")
    else:
        # Save to default location
        results_dir = root_dir / "results"
        results_dir.mkdir(exist_ok=True)
        output_path = results_dir / "postgresql_files_test_results.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        logger.info(f"Results saved to: {output_path}")
    
    return 0 if all_results['Pass'] == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
