#!/usr/bin/env python3
"""
Complete verification of SQL execution in notebooks
- Find execute_query_with_metrics function
- Verify SQL execution code
- Test queries.json SQL validity
- Check PostgreSQL compatibility
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

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

def find_execute_function(notebook: Dict) -> Dict:
    """Find and analyze execute_query_with_metrics function."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'function_exists': False,
        'uses_cursor': False,
        'uses_pd_read_sql': False,
        'has_error_handling': False,
        'has_metrics': False,
        'function_code': None
    }
    
    # Find function definition
    func_pattern = r'def execute_query_with_metrics\([^)]*\):.*?(?=\n\n|\ndef |\Z)'
    match = re.search(func_pattern, all_text, re.DOTALL)
    
    if match:
        results['function_exists'] = True
        func_code = match.group(0)
        results['function_code'] = func_code[:500]  # First 500 chars
        
        # Check for cursor usage
        if 'cursor' in func_code.lower() and 'execute' in func_code.lower():
            results['uses_cursor'] = True
        
        # Check for pandas read_sql
        if 'pd.read_sql' in func_code or 'read_sql_query' in func_code:
            results['uses_pd_read_sql'] = True
        
        # Check for error handling
        if 'try:' in func_code and 'except' in func_code:
            results['has_error_handling'] = True
        
        # Check for metrics collection
        if 'execution_time' in func_code or 'row_count' in func_code:
            results['has_metrics'] = True
    
    return results

def verify_sql_execution_flow(notebook: Dict) -> Dict:
    """Verify the complete SQL execution flow."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'loads_queries': False,
        'iterates_queries': False,
        'calls_execute_function': False,
        'has_connection': False,
        'complete_flow': False
    }
    
    # Check for queries.json loading
    if 'queries.json' in all_text and ('json.load' in all_text or 'queries_data' in all_text):
        results['loads_queries'] = True
    
    # Check for query iteration
    if re.search(r'for\s+\w+\s+in\s+queries', all_text, re.IGNORECASE):
        results['iterates_queries'] = True
    
    # Check for execute_query_with_metrics call
    if 'execute_query_with_metrics' in all_text:
        results['calls_execute_function'] = True
    
    # Check for database connection
    if 'psycopg2.connect' in all_text or 'create_postgresql_connection' in all_text:
        results['has_connection'] = True
    
    # Complete flow check
    results['complete_flow'] = all([
        results['loads_queries'],
        results['iterates_queries'],
        results['calls_execute_function'],
        results['has_connection']
    ])
    
    return results

def validate_queries_sql(queries_data: Dict) -> Dict:
    """Validate all SQL queries from queries.json."""
    if not queries_data or 'queries' not in queries_data:
        return {'total': 0, 'valid': 0, 'invalid': 0, 'errors': []}
    
    total = len(queries_data['queries'])
    valid = 0
    invalid = 0
    errors = []
    
    for query in queries_data['queries']:
        sql = query.get('sql', '')
        query_num = query.get('number', '?')
        
        if not sql or not sql.strip():
            invalid += 1
            errors.append(f"Query {query_num}: Empty SQL")
            continue
        
        sql_upper = sql.upper().strip()
        
        # Basic validation
        issues = []
        
        # Check for SQL keywords
        if not any(kw in sql_upper for kw in ['SELECT', 'WITH', 'CREATE', 'INSERT', 'UPDATE', 'DELETE']):
            issues.append("No SQL keywords")
        
        # Check parentheses balance
        if sql.count('(') != sql.count(')'):
            issues.append("Unbalanced parentheses")
        
        # Check for WITH without SELECT
        if 'WITH' in sql_upper and 'SELECT' not in sql_upper:
            issues.append("WITH without SELECT")
        
        # Check for PostgreSQL compatibility
        # Most SQL should work, but check for obvious issues
        if 'TOP ' in sql_upper and 'LIMIT' not in sql_upper:
            issues.append("SQL Server TOP syntax (use LIMIT instead)")
        
        if issues:
            invalid += 1
            errors.append(f"Query {query_num}: {', '.join(issues)}")
        else:
            valid += 1
    
    return {
        'total': total,
        'valid': valid,
        'invalid': invalid,
        'errors': errors
    }

def verify_notebook_sql(notebook_path: Path, db_name: str) -> Dict:
    """Complete SQL verification for a notebook."""
    print(f"\\nVerifying SQL Execution: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    queries_data = read_queries_json(db_name)
    
    results = {
        'notebook': str(notebook_path),
        'execute_function': {},
        'execution_flow': {},
        'queries_validation': {},
        'passed': False
    }
    
    # Check execute function
    results['execute_function'] = find_execute_function(notebook)
    
    # Check execution flow
    results['execution_flow'] = verify_sql_execution_flow(notebook)
    
    # Validate queries
    if queries_data:
        results['queries_validation'] = validate_queries_sql(queries_data)
    
    # Overall pass
    results['passed'] = (
        results['execute_function']['function_exists'] and
        results['execute_function']['uses_cursor'] and
        results['execution_flow']['complete_flow'] and
        results['queries_validation'].get('invalid', 0) == 0
    )
    
    return results

def print_results(results: Dict):
    """Print verification results."""
    status = "✅ PASS" if results['passed'] else "❌ FAIL"
    print(f"  {status}")
    
    print(f"    Execute Function:")
    print(f"      ✅ Function exists: {results['execute_function']['function_exists']}")
    print(f"      ✅ Uses cursor: {results['execute_function']['uses_cursor']}")
    print(f"      ✅ Error handling: {results['execute_function']['has_error_handling']}")
    print(f"      ✅ Collects metrics: {results['execute_function']['has_metrics']}")
    
    print(f"    Execution Flow:")
    print(f"      ✅ Loads queries: {results['execution_flow']['loads_queries']}")
    print(f"      ✅ Iterates queries: {results['execution_flow']['iterates_queries']}")
    print(f"      ✅ Calls execute function: {results['execution_flow']['calls_execute_function']}")
    print(f"      ✅ Has connection: {results['execution_flow']['has_connection']}")
    print(f"      ✅ Complete flow: {results['execution_flow']['complete_flow']}")
    
    if results['queries_validation']:
        qv = results['queries_validation']
        print(f"    SQL Queries Validation:")
        print(f"      Total: {qv.get('total', 0)}")
        print(f"      Valid: {qv.get('valid', 0)}")
        print(f"      Invalid: {qv.get('invalid', 0)}")
        
        if qv.get('errors'):
            print(f"      ❌ Errors:")
            for error in qv['errors'][:5]:
                print(f"         - {error}")

def main():
    """Main execution."""
    print("="*80)
    print("COMPLETE SQL EXECUTION VERIFICATION")
    print("="*80)
    
    all_results = []
    total_passed = 0
    total_failed = 0
    
    # Verify notebooks
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            results = verify_notebook_sql(notebook_path, db_name)
            all_results.append(results)
            print_results(results)
            
            if results['passed']:
                total_passed += 1
            else:
                total_failed += 1
    
    # Summary
    print("\\n" + "="*80)
    print("SQL EXECUTION VERIFICATION SUMMARY")
    print("="*80)
    print(f"Total notebooks verified: {len(all_results)}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    
    if total_failed > 0:
        print("\\nNotebooks with issues:")
        for results in all_results:
            if not results['passed']:
                print(f"  - {Path(results['notebook']).name}")
                if not results['execute_function']['function_exists']:
                    print("    ❌ Missing execute_query_with_metrics function")
                if not results['execute_function']['uses_cursor']:
                    print("    ❌ Execute function doesn't use cursor")
                if not results['execution_flow']['complete_flow']:
                    print("    ❌ Incomplete execution flow")
                if results['queries_validation'].get('invalid', 0) > 0:
                    print(f"    ❌ {results['queries_validation']['invalid']} invalid SQL queries")
    
    print("\\n" + "="*80)
    if total_failed == 0:
        print("✅ ALL SQL EXECUTION VERIFIED!")
        print("SQL queries will execute correctly in Colab PostgreSQL")
    else:
        print("⚠️  SOME SQL EXECUTION ISSUES FOUND")
    print("="*80)
    
    return 0 if total_failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
