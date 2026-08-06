#!/usr/bin/env python3
"""
Test notebooks for Google Colab errors
- Check Colab-specific code patterns
- Verify Colab environment detection
- Test PostgreSQL setup code
- Check file path handling
- Verify imports and dependencies
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

def test_colab_detection(notebook: Dict) -> Tuple[bool, List[str]]:
    """Test Colab environment detection code."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    errors = []
    warnings = []
    
    # Check for Colab detection
    has_colab_check = False
    detection_methods = []
    
    if 'import google.colab' in all_text:
        has_colab_check = True
        detection_methods.append('google.colab import')
    
    if 'COLAB_GPU' in all_text:
        has_colab_check = True
        detection_methods.append('COLAB_GPU env var')
    
    if '/content' in all_text:
        has_colab_check = True
        detection_methods.append('/content path check')
    
    if not has_colab_check:
        errors.append("No Colab detection code found")
    
    # Check for Colab-only execution check
    if 'IS_COLAB' in all_text and 'RuntimeError' in all_text:
        # Good - has Colab-only check
        pass
    else:
        warnings.append("No Colab-only execution check (should raise RuntimeError if not Colab)")
    
    # Check for proper error message
    if 'Google Colab' in all_text and 'RuntimeError' in all_text:
        # Good
        pass
    else:
        warnings.append("Colab error message could be more informative")
    
    return len(errors) == 0, errors + warnings

def test_postgresql_setup(notebook: Dict) -> Tuple[bool, List[str]]:
    """Test PostgreSQL setup code for Colab."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    errors = []
    warnings = []
    
    # Check for PostgreSQL installation
    has_install = False
    if 'apt-get install postgresql' in all_text or 'apt-get install -y postgresql' in all_text:
        has_install = True
    elif '!apt-get' in all_text and 'postgresql' in all_text:
        has_install = True
    elif 'os.system' in all_text and 'apt-get install' in all_text and 'postgresql' in all_text:
        has_install = True
    
    if not has_install:
        errors.append("No PostgreSQL installation code found")
    
    # Check for service start
    has_service_start = False
    if 'service postgresql start' in all_text:
        has_service_start = True
    elif 'subprocess.run' in all_text and 'postgresql' in all_text and 'start' in all_text:
        has_service_start = True
    elif 'os.system' in all_text and 'service postgresql start' in all_text:
        has_service_start = True
    
    if not has_service_start:
        errors.append("No PostgreSQL service start code found")
    
    # Check for connection code
    has_connection = False
    if 'psycopg2.connect' in all_text:
        has_connection = True
        # Check for Colab-specific connection parameters
        if "host='localhost'" in all_text and "user='postgres'" in all_text:
            # Good
            pass
        else:
            warnings.append("PostgreSQL connection might not use Colab defaults")
    
    if not has_connection:
        errors.append("No PostgreSQL connection code found")
    
    # Check for error handling
    if 'try:' in all_text and 'psycopg2.connect' in all_text:
        # Good
        pass
    else:
        warnings.append("PostgreSQL connection lacks error handling")
    
    return len(errors) == 0, errors + warnings

def test_file_paths(notebook: Dict) -> Tuple[bool, List[str]]:
    """Test file path handling for Colab."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    errors = []
    warnings = []
    
    # Check for Colab paths
    has_colab_paths = False
    if '/content' in all_text:
        has_colab_paths = True
    
    if '/content/drive' in all_text or '/content/drive/MyDrive' in all_text:
        has_colab_paths = True
        # Good - checks Google Drive
    
    if not has_colab_paths:
        warnings.append("No Colab-specific paths (/content) found")
    
    # Check for recursive file finding
    if 'rglob' in all_text or 'find_file_recursively' in all_text:
        # Good - can find files in Colab
        pass
    else:
        warnings.append("No recursive file finding - might not find files in Colab")
    
    # Check for hardcoded local paths (but allow fallbacks in correct_file_path)
    # Only warn if paths are used directly, not as fallbacks
    if '/Users/machine/Documents/AQ/db' in all_text and 'correct_file_path' not in all_text:
        # This is a direct path usage, not a fallback
        warnings.append("Hardcoded local paths found - should use Colab paths")
    elif '/Users/machine' in all_text and 'Path.home()' not in all_text:
        # Check if it's in a function that handles fallbacks
        if 'find_file_recursively' not in all_text and 'correct_file_path' not in all_text:
            warnings.append("Hardcoded local paths found - should use Colab paths")
    
    return len(errors) == 0, errors + warnings

def test_imports(notebook: Dict) -> Tuple[bool, List[str]]:
    """Test import statements."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    errors = []
    warnings = []
    
    # Check for required imports
    required_imports = {
        'pandas': 'pd',
        'psycopg2': 'psycopg2',
        'json': 'json',
        'pathlib': 'Path',
    }
    
    for module, alias in required_imports.items():
        if f'import {module}' not in all_text and f'from {module}' not in all_text:
            # Check if used
            if alias in all_text or module in all_text:
                errors.append(f"Missing import: {module}")
    
    # Check for IPython imports (needed for Colab)
    if 'display(' in all_text or 'Markdown(' in all_text:
        if 'from IPython.display' not in all_text:
            warnings.append("Using display() but IPython.display not imported")
    
    return len(errors) == 0, errors + warnings

def test_sql_execution(notebook: Dict) -> Tuple[bool, List[str]]:
    """Test SQL execution code."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    errors = []
    warnings = []
    
    # Check for queries loading
    if 'queries.json' not in all_text:
        errors.append("No queries.json loading code found")
    
    # Check for query execution
    if 'execute_query_with_metrics' not in all_text:
        errors.append("No execute_query_with_metrics function call found")
    
    # Check for cursor usage
    if 'cursor.execute' not in all_text and 'execute_query_with_metrics' not in all_text:
        errors.append("No SQL execution code found")
    
    # Check for error handling in SQL execution
    if 'execute_query_with_metrics' in all_text:
        if 'try:' in all_text and 'execute_query_with_metrics' in all_text:
            # Check if error handling is around execution
            # This is a basic check
            pass
        else:
            warnings.append("SQL execution might lack error handling")
    
    return len(errors) == 0, errors + warnings

def test_colab_specific_issues(notebook: Dict) -> Tuple[bool, List[str]]:
    """Test for Colab-specific issues."""
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    errors = []
    warnings = []
    
    # Check for magic commands (should use ! for shell commands)
    # Note: os.system is acceptable alternative to magic commands
    if 'subprocess.run' in all_text and 'apt-get' in all_text and 'os.system' not in all_text:
        # Should use !apt-get or os.system instead
        warnings.append("Using subprocess.run for apt-get - should use !apt-get magic command or os.system")
    
    # Check for service commands
    # Note: os.system is acceptable alternative to magic commands
    if 'subprocess.run' in all_text and 'service postgresql' in all_text and 'os.system' not in all_text:
        warnings.append("Using subprocess.run for service - could use !service magic command or os.system")
    
    # Check for Google Drive mounting
    if '/content/drive' in all_text or 'drive.mount' in all_text:
        # Good - handles Google Drive
        pass
    else:
        warnings.append("No Google Drive mounting code - files uploaded to Colab won't persist")
    
    # Check for SQLite references (should be removed)
    if 'sqlite' in all_text.lower() or 'SQLite' in all_text:
        errors.append("SQLite references found - should be PostgreSQL only")
    
    # Check for Docker references (not needed in Colab)
    if 'docker' in all_text.lower() and 'ENV_TYPE' in all_text:
        # This is OK - environment detection
        pass
    
    return len(errors) == 0, errors + warnings

def test_notebook_colab(notebook_path: Path, db_name: str) -> Dict:
    """Test notebook for Colab errors."""
    print(f"\\nTesting Colab compatibility: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    
    results = {
        'notebook': str(notebook_path),
        'database': db_name,
        'tests': {},
        'passed': False,
        'total_errors': 0,
        'total_warnings': 0
    }
    
    # Run all tests
    tests = [
        ('colab_detection', test_colab_detection),
        ('postgresql_setup', test_postgresql_setup),
        ('file_paths', test_file_paths),
        ('imports', test_imports),
        ('sql_execution', test_sql_execution),
        ('colab_specific', test_colab_specific_issues),
    ]
    
    for test_name, test_func in tests:
        passed, issues = test_func(notebook)
        errors = [i for i in issues if not i.startswith('⚠️')]
        warnings = [i for i in issues if i.startswith('⚠️') or 'warnings' in i.lower() or 'could' in i.lower() or 'might' in i.lower()]
        
        results['tests'][test_name] = {
            'passed': passed,
            'errors': errors,
            'warnings': warnings
        }
        
        results['total_errors'] += len(errors)
        results['total_warnings'] += len(warnings)
    
    results['passed'] = results['total_errors'] == 0
    
    return results

def print_results(results: Dict):
    """Print test results."""
    status = "✅ PASS" if results['passed'] else "❌ FAIL"
    print(f"  {status}")
    
    for test_name, test_result in results['tests'].items():
        test_status = "✅" if test_result['passed'] else "❌"
        print(f"    {test_status} {test_name}:")
        
        if test_result['errors']:
            for error in test_result['errors'][:2]:
                print(f"       ❌ {error}")
        
        if test_result['warnings']:
            for warning in test_result['warnings'][:2]:
                print(f"       ⚠️  {warning}")

def main():
    """Main execution."""
    print("="*80)
    print("TESTING NOTEBOOKS FOR GOOGLE COLAB ERRORS")
    print("="*80)
    
    all_results = []
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_warnings = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            results = test_notebook_colab(notebook_path, db_name)
            all_results.append(results)
            print_results(results)
            
            if results['passed']:
                total_passed += 1
            else:
                total_failed += 1
            
            total_errors += results['total_errors']
            total_warnings += results['total_warnings']
    
    # Summary
    print("\\n" + "="*80)
    print("COLAB ERROR TEST SUMMARY")
    print("="*80)
    print(f"Total notebooks tested: {len(all_results)}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}")
    
    if total_failed > 0:
        print("\\nNotebooks with errors:")
        for results in all_results:
            if not results['passed']:
                print(f"  - {Path(results['notebook']).name}: {results['total_errors']} errors")
                for test_name, test_result in results['tests'].items():
                    if test_result['errors']:
                        for error in test_result['errors']:
                            print(f"    {test_name}: {error}")
    
    if total_warnings > 0:
        print("\\nCommon warnings:")
        warning_counts = {}
        for results in all_results:
            for test_name, test_result in results['tests'].items():
                for warning in test_result['warnings']:
                    warning_key = warning.split(':')[0] if ':' in warning else warning[:50]
                    warning_counts[warning_key] = warning_counts.get(warning_key, 0) + 1
        
        for warning, count in sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {warning}: {count} notebooks")
    
    print("\\n" + "="*80)
    if total_errors == 0:
        print("✅ NO CRITICAL COLAB ERRORS FOUND!")
        print("Notebooks should work in Google Colab")
    else:
        print("⚠️  SOME COLAB ERRORS FOUND")
        print("Please review errors above")
    print("="*80)
    
    return 0 if total_errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
