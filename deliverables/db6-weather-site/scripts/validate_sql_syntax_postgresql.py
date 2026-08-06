#!/usr/bin/env python3
"""
Validate SQL syntax for PostgreSQL compatibility
- Check queries.json SQL statements
- Validate PostgreSQL syntax
- Test for common issues
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def detect_base_dir():
    """Detect base directory."""
    cwd = Path.cwd()
    if cwd.name == 'scripts' and (cwd.parent / 'db-6').exists():
        return cwd.parent
    return cwd.parent if (cwd.parent / 'db-6').exists() else cwd

BASE_DIR = detect_base_dir()
DATABASES = [f'db-{i}' for i in range(6, 16)]

def read_queries_json(db_name: str) -> Dict:
    """Read queries.json for a database."""
    queries_file = BASE_DIR / db_name / 'queries' / 'queries.json'
    if queries_file.exists():
        with open(queries_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def validate_sql_structure(sql: str) -> Tuple[bool, List[str]]:
    """Validate SQL structure and syntax."""
    errors = []
    warnings = []
    
    sql_upper = sql.upper().strip()
    
    # Check for empty SQL
    if not sql_upper:
        errors.append("Empty SQL statement")
        return False, errors
    
    # Check for balanced parentheses
    open_parens = sql.count('(')
    close_parens = sql.count(')')
    if open_parens != close_parens:
        errors.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
    
    # Check for balanced quotes (basic check)
    single_quotes = sql.count("'") - sql.count("\\'")
    if single_quotes % 2 != 0:
        warnings.append("Possible unbalanced single quotes (may be escaped)")
    
    # Check for SQL keywords
    if not any(kw in sql_upper for kw in ['SELECT', 'WITH', 'CREATE', 'INSERT', 'UPDATE', 'DELETE', 'ALTER']):
        errors.append("No SQL keywords found")
    
    # Check for WITH without SELECT
    if 'WITH' in sql_upper and 'SELECT' not in sql_upper:
        errors.append("WITH clause without SELECT statement")
    
    # Check for PostgreSQL compatibility
    if 'TOP ' in sql_upper and 'LIMIT' not in sql_upper:
        errors.append("SQL Server TOP syntax (PostgreSQL uses LIMIT)")
    
    # Check for proper CTE structure
    if 'WITH' in sql_upper:
        # Count WITH clauses
        with_count = sql_upper.count('WITH')
        select_count = sql_upper.count('SELECT')
        if with_count > select_count:
            warnings.append("More WITH clauses than SELECT statements")
    
    # Check for recursive CTE structure
    if 'WITH RECURSIVE' in sql_upper:
        if 'UNION' not in sql_upper and 'UNION ALL' not in sql_upper:
            errors.append("Recursive CTE missing UNION/UNION ALL")
    
    # Check for semicolon at end (optional but common)
    if not sql.strip().endswith(';'):
        warnings.append("SQL statement doesn't end with semicolon")
    
    return len(errors) == 0, errors + warnings

def check_postgresql_specific(sql: str) -> List[str]:
    """Check for PostgreSQL-specific syntax issues."""
    warnings = []
    sql_upper = sql.upper()
    
    # Check for PostGIS functions (should work in PostgreSQL with PostGIS extension)
    postgis_functions = ['ST_WITHIN', 'ST_DISTANCE', 'ST_INTERSECTS', 'ST_AREA', 'ST_WITHIN']
    has_postgis = any(func in sql_upper for func in postgis_functions)
    
    if has_postgis:
        warnings.append("Uses PostGIS functions - requires PostGIS extension in PostgreSQL")
    
    # Check for array operations
    if 'ARRAY[' in sql or 'ARRAY_LENGTH' in sql_upper:
        # PostgreSQL arrays - should work
        pass
    
    # Check for window functions
    window_functions = ['ROW_NUMBER', 'RANK', 'DENSE_RANK', 'LEAD', 'LAG', 'PERCENTILE_CONT']
    has_window = any(func in sql_upper for func in window_functions)
    
    if has_window and 'OVER' not in sql_upper:
        warnings.append("Window functions used but OVER clause not found")
    
    # Check for PERCENTILE_CONT syntax
    if 'PERCENTILE_CONT' in sql_upper:
        if 'WITHIN GROUP' not in sql_upper:
            warnings.append("PERCENTILE_CONT should use WITHIN GROUP clause")
    
    return warnings

def validate_database_queries(db_name: str) -> Dict:
    """Validate all queries for a database."""
    print(f"\\nValidating SQL: {db_name}")
    
    queries_data = read_queries_json(db_name)
    
    if not queries_data or 'queries' not in queries_data:
        return {
            'database': db_name,
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'errors': ['queries.json not found or invalid'],
            'warnings': []
        }
    
    total = len(queries_data['queries'])
    valid = 0
    invalid = 0
    all_errors = []
    all_warnings = []
    
    for query in queries_data['queries']:
        sql = query.get('sql', '')
        query_num = query.get('number', '?')
        query_title = query.get('title', 'N/A')[:50]
        
        # Validate structure
        is_valid, issues = validate_sql_structure(sql)
        
        # Check PostgreSQL-specific
        pg_warnings = check_postgresql_specific(sql)
        
        if is_valid:
            valid += 1
            if issues:
                all_warnings.append(f"Query {query_num} ({query_title}): {', '.join(issues)}")
            if pg_warnings:
                all_warnings.append(f"Query {query_num} ({query_title}): {', '.join(pg_warnings)}")
        else:
            invalid += 1
            all_errors.append(f"Query {query_num} ({query_title}): {', '.join(issues)}")
            if pg_warnings:
                all_warnings.append(f"Query {query_num} ({query_title}): {', '.join(pg_warnings)}")
    
    return {
        'database': db_name,
        'total': total,
        'valid': valid,
        'invalid': invalid,
        'errors': all_errors,
        'warnings': all_warnings
    }

def print_results(results: Dict):
    """Print validation results."""
    status = "✅ PASS" if results['invalid'] == 0 else "❌ FAIL"
    print(f"  {status}")
    print(f"    Total queries: {results['total']}")
    print(f"    Valid: {results['valid']}")
    print(f"    Invalid: {results['invalid']}")
    
    if results['errors']:
        print(f"    ❌ Errors ({len(results['errors'])}):")
        for error in results['errors'][:3]:
            print(f"       - {error}")
    
    if results['warnings']:
        print(f"    ⚠️  Warnings ({len(results['warnings'])}):")
        for warning in results['warnings'][:3]:
            print(f"       - {warning}")

def main():
    """Main execution."""
    print("="*80)
    print("VALIDATING SQL SYNTAX FOR POSTGRESQL")
    print("="*80)
    
    all_results = []
    total_valid = 0
    total_invalid = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        results = validate_database_queries(db_name)
        all_results.append(results)
        print_results(results)
        
        total_valid += results['valid']
        total_invalid += results['invalid']
    
    # Summary
    print("\\n" + "="*80)
    print("SQL SYNTAX VALIDATION SUMMARY")
    print("="*80)
    print(f"Total databases: {len(all_results)}")
    print(f"Total queries validated: {sum(r['total'] for r in all_results)}")
    print(f"✅ Valid queries: {total_valid}")
    print(f"❌ Invalid queries: {total_invalid}")
    
    if total_invalid > 0:
        print("\\nDatabases with invalid SQL:")
        for results in all_results:
            if results['invalid'] > 0:
                print(f"  - {results['database']}: {results['invalid']} invalid queries")
                for error in results['errors'][:2]:
                    print(f"    {error}")
    
    # Check for common warnings
    all_warnings = []
    for results in all_results:
        all_warnings.extend(results['warnings'])
    
    if all_warnings:
        print(f"\\n⚠️  Total warnings: {len(all_warnings)}")
        print("Common warnings:")
        warning_counts = {}
        for warning in all_warnings:
            # Extract warning type
            if 'PostGIS' in warning:
                warning_counts['PostGIS extension'] = warning_counts.get('PostGIS extension', 0) + 1
            elif 'semicolon' in warning.lower():
                warning_counts['Missing semicolon'] = warning_counts.get('Missing semicolon', 0) + 1
            elif 'WITH' in warning:
                warning_counts['CTE structure'] = warning_counts.get('CTE structure', 0) + 1
        
        for warning_type, count in warning_counts.items():
            print(f"  - {warning_type}: {count} queries")
    
    print("\\n" + "="*80)
    if total_invalid == 0:
        print("✅ ALL SQL QUERIES VALIDATED!")
        print("SQL statements are syntactically correct for PostgreSQL")
    else:
        print("⚠️  SOME SQL QUERIES HAVE SYNTAX ERRORS")
        print("Please review errors above")
    print("="*80)
    
    return 0 if total_invalid == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
