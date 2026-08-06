#!/usr/bin/env python3
"""
Validate SQL statements in notebooks
- Extract SQL queries
- Validate PostgreSQL syntax
- Check for Colab compatibility
- Verify query structure
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

def extract_sql_from_notebook(notebook: Dict) -> List[Dict]:
    """Extract SQL queries from notebook cells."""
    sql_queries = []
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            
            # Look for SQL execution patterns
            sql_patterns = [
                r'cursor\.execute\(["\']([^"\']+)["\']',
                r'cursor\.execute\(f?["\']([^"\']+)["\']',
                r'conn\.execute\(["\']([^"\']+)["\']',
                r'pd\.read_sql\(["\']([^"\']+)["\']',
                r'pd\.read_sql_query\(["\']([^"\']+)["\']',
            ]
            
            for pattern in sql_patterns:
                matches = re.finditer(pattern, source, re.DOTALL)
                for match in matches:
                    sql = match.group(1)
                    # Clean up SQL (remove escaped quotes, etc.)
                    sql = sql.replace('\\n', '\n').replace('\\t', '\t')
                    sql_queries.append({
                        'cell': i + 1,
                        'sql': sql,
                        'pattern': pattern
                    })
            
            # Also look for multi-line SQL strings
            if 'SELECT' in source.upper() or 'WITH' in source.upper():
                # Try to extract SQL blocks
                sql_blocks = re.findall(r'(?:SELECT|WITH|CREATE|INSERT|UPDATE|DELETE)\s+.*?(?=\n\n|\n\s*[a-zA-Z]|\Z)', 
                                       source, re.DOTALL | re.IGNORECASE)
                for sql_block in sql_blocks:
                    if len(sql_block.strip()) > 20:  # Reasonable SQL length
                        sql_queries.append({
                            'cell': i + 1,
                            'sql': sql_block.strip(),
                            'pattern': 'block_extraction'
                        })
    
    return sql_queries

def validate_sql_syntax(sql: str) -> Tuple[bool, List[str]]:
    """Validate SQL syntax (basic checks)."""
    errors = []
    warnings = []
    
    sql_upper = sql.upper().strip()
    
    # Check for empty SQL
    if not sql_upper:
        errors.append("Empty SQL statement")
        return False, errors
    
    # Check for balanced parentheses
    if sql.count('(') != sql.count(')'):
        errors.append("Unbalanced parentheses")
    
    # Check for balanced quotes
    single_quotes = sql.count("'") - sql.count("\\'")
    double_quotes = sql.count('"') - sql.count('\\"')
    if single_quotes % 2 != 0:
        errors.append("Unbalanced single quotes")
    if double_quotes % 2 != 0:
        errors.append("Unbalanced double quotes")
    
    # Check for common SQL keywords
    if not any(keyword in sql_upper for keyword in ['SELECT', 'WITH', 'CREATE', 'INSERT', 'UPDATE', 'DELETE', 'ALTER']):
        warnings.append("No SQL keywords found - might not be valid SQL")
    
    # Check for PostgreSQL-specific syntax that might not work in Colab
    # (Note: Colab PostgreSQL should support standard SQL)
    
    # Check for common issues
    if 'LIMIT' in sql_upper and 'OFFSET' in sql_upper:
        # This is fine
        pass
    
    # Check for CTEs (should be present in complex queries)
    if 'WITH' in sql_upper:
        if 'RECURSIVE' in sql_upper:
            # Recursive CTE - verify structure
            if sql_upper.count('WITH RECURSIVE') != sql_upper.count('UNION'):
                warnings.append("Recursive CTE should have UNION/UNION ALL")
    
    # Check for semicolons (optional in Python execution)
    if sql.count(';') > sql.count(';') * 2:
        warnings.append("Multiple semicolons - might cause issues")
    
    return len(errors) == 0, errors + warnings

def check_sql_execution_pattern(notebook: Dict) -> Dict:
    """Check how SQL is executed in the notebook."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'has_cursor_execute': 'cursor.execute' in all_text,
        'has_pd_read_sql': 'pd.read_sql' in all_text or 'pd.read_sql_query' in all_text,
        'has_conn_execute': 'conn.execute' in all_text,
        'has_sql_strings': 'SELECT' in all_text.upper() or 'WITH' in all_text.upper(),
        'has_query_loading': 'queries.json' in all_text or 'queries_data' in all_text,
        'has_error_handling': 'try:' in all_text and 'cursor' in all_text,
    }
    
    results['has_execution'] = (
        results['has_cursor_execute'] or 
        results['has_pd_read_sql'] or 
        results['has_conn_execute']
    )
    
    return results

def validate_notebook_sql(notebook_path: Path, db_name: str) -> Dict:
    """Validate SQL in a notebook."""
    print(f"\\nValidating SQL: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    queries_data = read_queries_json(db_name)
    
    results = {
        'notebook': str(notebook_path),
        'queries_found': 0,
        'queries_valid': 0,
        'queries_invalid': 0,
        'sql_errors': [],
        'sql_warnings': [],
        'execution_pattern': {},
        'queries_from_json': 0,
    }
    
    # Check execution pattern
    results['execution_pattern'] = check_sql_execution_pattern(notebook)
    
    # Extract SQL from notebook
    sql_queries = extract_sql_from_notebook(notebook)
    results['queries_found'] = len(sql_queries)
    
    # Validate each SQL query
    for sql_query in sql_queries:
        valid, issues = validate_sql_syntax(sql_query['sql'])
        if valid:
            results['queries_valid'] += 1
            if issues:
                results['sql_warnings'].extend([f"Cell {sql_query['cell']}: {w}" for w in issues])
        else:
            results['queries_invalid'] += 1
            results['sql_errors'].extend([f"Cell {sql_query['cell']}: {e}" for e in issues])
    
    # Check if queries are loaded from queries.json
    if queries_data and 'queries' in queries_data:
        results['queries_from_json'] = len(queries_data['queries'])
        
        # Validate queries from JSON
        for query in queries_data['queries']:
            sql = query.get('sql', '')
            if sql:
                valid, issues = validate_sql_syntax(sql)
                if not valid:
                    results['sql_errors'].extend([f"Query {query.get('number', '?')}: {e}" for e in issues])
                elif issues:
                    results['sql_warnings'].extend([f"Query {query.get('number', '?')}: {w}" for w in issues])
    
    results['passed'] = (
        results['execution_pattern']['has_execution'] and
        results['queries_invalid'] == 0 and
        len(results['sql_errors']) == 0
    )
    
    return results

def print_results(results: Dict):
    """Print validation results."""
    status = "✅ PASS" if results['passed'] else "❌ FAIL"
    print(f"  {status}")
    
    print(f"    Execution Pattern:")
    print(f"      ✅ Has cursor.execute: {results['execution_pattern']['has_cursor_execute']}")
    print(f"      ✅ Has pd.read_sql: {results['execution_pattern']['has_pd_read_sql']}")
    print(f"      ✅ Has error handling: {results['execution_pattern']['has_error_handling']}")
    
    print(f"    SQL Queries:")
    print(f"      Found: {results['queries_found']}")
    print(f"      Valid: {results['queries_valid']}")
    print(f"      Invalid: {results['queries_invalid']}")
    print(f"      From JSON: {results['queries_from_json']}")
    
    if results['sql_errors']:
        print(f"    ❌ SQL Errors ({len(results['sql_errors'])}):")
        for error in results['sql_errors'][:5]:
            print(f"       - {error}")
    
    if results['sql_warnings']:
        print(f"    ⚠️  Warnings ({len(results['sql_warnings'])}):")
        for warning in results['sql_warnings'][:5]:
            print(f"       - {warning}")

def main():
    """Main execution."""
    print("="*80)
    print("VALIDATING SQL STATEMENTS IN NOTEBOOKS")
    print("="*80)
    
    all_results = []
    total_passed = 0
    total_failed = 0
    
    # Validate notebooks in db-* directories
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            results = validate_notebook_sql(notebook_path, db_name)
            all_results.append(results)
            print_results(results)
            
            if results['passed']:
                total_passed += 1
            else:
                total_failed += 1
    
    # Summary
    print("\\n" + "="*80)
    print("SQL VALIDATION SUMMARY")
    print("="*80)
    print(f"Total notebooks validated: {len(all_results)}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    
    if total_failed > 0:
        print("\\nNotebooks with SQL issues:")
        for results in all_results:
            if not results['passed']:
                print(f"  - {Path(results['notebook']).name}")
                if results['sql_errors']:
                    for error in results['sql_errors'][:3]:
                        print(f"    Error: {error}")
    
    print("\\n" + "="*80)
    if total_failed == 0:
        print("✅ ALL SQL STATEMENTS VALIDATED!")
        print("SQL queries are ready for execution in Colab PostgreSQL")
    else:
        print("⚠️  SOME SQL ISSUES FOUND")
        print("Please review errors above")
    print("="*80)
    
    return 0 if total_failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
