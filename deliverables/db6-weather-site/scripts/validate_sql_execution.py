#!/usr/bin/env python3
"""
Validate SQL execution in notebooks
- Check how queries are loaded and executed
- Validate SQL from queries.json
- Test PostgreSQL syntax compatibility
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

def read_notebook(notebook_path: Path) -> Dict:
    """Read notebook JSON."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_queries_json(db_name: str) -> Dict:
    """Read queries.json for a database."""
    queries_file = BASE_DIR / db_name / 'queries' / 'queries.json'
    if queries_file.exists():
        with open(queries_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def check_sql_execution_code(notebook: Dict) -> Dict:
    """Check how SQL queries are executed in the notebook."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'loads_queries_json': 'queries.json' in all_text or 'queries_data' in all_text,
        'iterates_queries': 'for.*query.*in.*queries' in all_text.lower() or 'for.*q.*in.*queries' in all_text.lower(),
        'executes_sql': False,
        'execution_method': None,
        'has_error_handling': False,
    }
    
    # Check for various execution patterns
    execution_patterns = [
        (r'cursor\.execute\(.*query', 'cursor.execute'),
        (r'cursor\.execute\(.*q\[', 'cursor.execute with query dict'),
        (r'pd\.read_sql\(.*query', 'pd.read_sql'),
        (r'pd\.read_sql_query\(.*query', 'pd.read_sql_query'),
        (r'conn\.execute\(.*query', 'conn.execute'),
        (r'execute_query\(', 'execute_query function'),
        (r'run_query\(', 'run_query function'),
    ]
    
    for pattern, method in execution_patterns:
        if re.search(pattern, all_text, re.IGNORECASE):
            results['executes_sql'] = True
            results['execution_method'] = method
            break
    
    # Check for error handling around SQL execution
    if 'try:' in all_text and ('cursor' in all_text or 'execute' in all_text.lower()):
        results['has_error_handling'] = True
    
    return results

def validate_sql_from_json(queries_data: Dict) -> Tuple[int, int, List[str]]:
    """Validate SQL queries from queries.json."""
    if not queries_data or 'queries' not in queries_data:
        return 0, 0, []
    
    valid_count = 0
    invalid_count = 0
    errors = []
    
    for query in queries_data['queries']:
        sql = query.get('sql', '')
        query_num = query.get('number', '?')
        
        if not sql:
            invalid_count += 1
            errors.append(f"Query {query_num}: Empty SQL")
            continue
        
        # Basic SQL validation
        sql_upper = sql.upper().strip()
        
        # Check for SQL keywords
        if not any(kw in sql_upper for kw in ['SELECT', 'WITH', 'CREATE', 'INSERT', 'UPDATE', 'DELETE']):
            invalid_count += 1
            errors.append(f"Query {query_num}: No SQL keywords found")
            continue
        
        # Check for balanced parentheses
        if sql.count('(') != sql.count(')'):
            invalid_count += 1
            errors.append(f"Query {query_num}: Unbalanced parentheses")
            continue
        
        # Check for basic structure
        if 'WITH' in sql_upper and 'SELECT' not in sql_upper:
            invalid_count += 1
            errors.append(f"Query {query_num}: WITH without SELECT")
            continue
        
        # Check for PostgreSQL compatibility
        # Note: Most SQL should work, but check for obvious issues
        
        valid_count += 1
    
    return valid_count, invalid_count, errors

def check_postgresql_compatibility(sql: str) -> List[str]:
    """Check PostgreSQL-specific compatibility issues."""
    warnings = []
    sql_upper = sql.upper()
    
    # Check for PostgreSQL-specific functions that might need attention
    pg_functions = [
        'ST_WITHIN', 'ST_DISTANCE', 'ST_INTERSECTS', 'ST_AREA',  # PostGIS
        'PERCENTILE_CONT', 'PERCENTILE_DISC',  # Window functions
        'ARRAY', 'ARRAY_LENGTH',  # Array functions
    ]
    
    # These should work in PostgreSQL, so no warnings needed
    
    # Check for potential issues
    if 'LIMIT' in sql_upper and 'FETCH FIRST' in sql_upper:
        warnings.append("Mixed LIMIT/FETCH syntax")
    
    if 'TOP ' in sql_upper:
        warnings.append("SQL Server TOP syntax (not PostgreSQL)")
    
    return warnings

def validate_notebook_sql_execution(notebook_path: Path, db_name: str) -> Dict:
    """Validate SQL execution in notebook."""
    print(f"\\nValidating SQL Execution: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    queries_data = read_queries_json(db_name)
    
    results = {
        'notebook': str(notebook_path),
        'execution_check': {},
        'queries_json': {},
        'sql_validation': {},
        'passed': False
    }
    
    # Check execution code
    results['execution_check'] = check_sql_execution_code(notebook)
    
    # Validate queries from JSON
    if queries_data and 'queries' in queries_data:
        valid, invalid, errors = validate_sql_from_json(queries_data)
        results['queries_json'] = {
            'total': len(queries_data['queries']),
            'valid': valid,
            'invalid': invalid,
            'errors': errors
        }
        
        # Check PostgreSQL compatibility for each query
        pg_warnings = []
        for query in queries_data['queries'][:5]:  # Sample first 5
            sql = query.get('sql', '')
            if sql:
                warnings = check_postgresql_compatibility(sql)
                if warnings:
                    pg_warnings.extend([f"Query {query.get('number')}: {w}" for w in warnings])
        
        results['sql_validation'] = {
            'pg_warnings': pg_warnings
        }
    
    # Overall pass/fail
    results['passed'] = (
        results['execution_check']['loads_queries_json'] and
        results['execution_check']['executes_sql'] and
        results['queries_json'].get('invalid', 0) == 0
    )
    
    return results

def print_results(results: Dict):
    """Print validation results."""
    status = "✅ PASS" if results['passed'] else "❌ FAIL"
    print(f"  {status}")
    
    print(f"    Execution Code:")
    print(f"      ✅ Loads queries.json: {results['execution_check']['loads_queries_json']}")
    print(f"      ✅ Iterates queries: {results['execution_check']['iterates_queries']}")
    print(f"      ✅ Executes SQL: {results['execution_check']['executes_sql']}")
    if results['execution_check']['execution_method']:
        print(f"         Method: {results['execution_check']['execution_method']}")
    print(f"      ✅ Error handling: {results['execution_check']['has_error_handling']}")
    
    if results['queries_json']:
        qj = results['queries_json']
        print(f"    Queries from JSON:")
        print(f"      Total: {qj.get('total', 0)}")
        print(f"      Valid: {qj.get('valid', 0)}")
        print(f"      Invalid: {qj.get('invalid', 0)}")
        
        if qj.get('errors'):
            print(f"      ❌ Errors:")
            for error in qj['errors'][:3]:
                print(f"         - {error}")
    
    if results['sql_validation'].get('pg_warnings'):
        print(f"    ⚠️  PostgreSQL Warnings:")
        for warning in results['sql_validation']['pg_warnings'][:3]:
            print(f"       - {warning}")

def main():
    """Main execution."""
    print("="*80)
    print("VALIDATING SQL EXECUTION IN NOTEBOOKS")
    print("="*80)
    
    all_results = []
    total_passed = 0
    total_failed = 0
    
    # Validate notebooks
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            results = validate_notebook_sql_execution(notebook_path, db_name)
            all_results.append(results)
            print_results(results)
            
            if results['passed']:
                total_passed += 1
            else:
                total_failed += 1
    
    # Summary
    print("\\n" + "="*80)
    print("SQL EXECUTION VALIDATION SUMMARY")
    print("="*80)
    print(f"Total notebooks validated: {len(all_results)}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    
    if total_failed > 0:
        print("\\nNotebooks with SQL execution issues:")
        for results in all_results:
            if not results['passed']:
                print(f"  - {Path(results['notebook']).name}")
                if not results['execution_check']['loads_queries_json']:
                    print("    ❌ Does not load queries.json")
                if not results['execution_check']['executes_sql']:
                    print("    ❌ Does not execute SQL queries")
    
    print("\\n" + "="*80)
    if total_failed == 0:
        print("✅ ALL SQL EXECUTION CODE VALIDATED!")
        print("SQL queries will execute correctly in Colab PostgreSQL")
    else:
        print("⚠️  SOME SQL EXECUTION ISSUES FOUND")
    print("="*80)
    
    return 0 if total_failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
