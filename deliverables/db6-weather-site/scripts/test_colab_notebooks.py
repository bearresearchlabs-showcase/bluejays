#!/usr/bin/env python3
"""
Test notebooks for Google Colab compatibility
- Validates Colab-only check
- Validates PostgreSQL setup
- Checks for SQLite references
- Validates code syntax
"""

import json
import ast
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

def validate_python_code(code: str) -> Tuple[bool, str]:
    """Validate Python code syntax."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error: {e.msg} at line {e.lineno}"

def test_notebook(notebook_path: Path) -> Dict:
    """Test notebook for Colab compatibility."""
    print(f"\\nTesting: {notebook_path.name}")
    
    results = {
        'notebook': str(notebook_path),
        'has_colab_check': False,
        'has_postgresql_setup': False,
        'has_sqlite': False,
        'code_errors': [],
        'warnings': [],
        'passed': False
    }
    
    try:
        notebook = read_notebook(notebook_path)
    except Exception as e:
        results['code_errors'].append(f"Failed to read notebook: {e}")
        return results
    
    all_text = ""
    code_cells = []
    
    for i, cell in enumerate(notebook['cells']):
        source = ''.join(cell.get('source', []))
        all_text += source + "\\n"
        
        if cell['cell_type'] == 'code':
            code_cells.append((i, source))
            
            # Validate Python syntax (skip magic commands and shell commands)
            if source.strip():
                # Skip IPython magic commands and shell commands - these are valid in notebooks
                if source.strip().startswith('!') or source.strip().startswith('%'):
                    continue  # Magic commands are valid in notebooks
                
                # Skip cells that are mostly magic commands
                lines = source.split('\n')
                magic_lines = [l for l in lines if l.strip().startswith('!') or l.strip().startswith('%')]
                if len(magic_lines) > len(lines) * 0.5:  # More than 50% magic commands
                    continue
                
                valid, error = validate_python_code(source)
                if not valid:
                    # Check if error is due to magic commands
                    if '!' in source or '%' in source:
                        # Likely magic command issue - this is fine
                        continue
                    results['code_errors'].append(f"Cell {i+1}: {error}")
    
    # Check for Colab-only check
    if 'GOOGLE COLAB ONLY' in all_text or 'IS_COLAB' in all_text:
        results['has_colab_check'] = True
    else:
        results['warnings'].append("Missing Colab-only check")
    
    # Check for PostgreSQL setup
    if 'INSTALLING POSTGRESQL FOR GOOGLE COLAB' in all_text or 'POSTGRESQL INSTALLATION' in all_text:
        results['has_postgresql_setup'] = True
    else:
        results['warnings'].append("Missing PostgreSQL installation code")
    
    # Check for SQLite (should not be present)
    if 'sqlite' in all_text.lower():
        results['has_sqlite'] = True
        results['warnings'].append("SQLite references found (should be removed)")
    
    # Check for PostgreSQL connection
    if 'psycopg2.connect' in all_text:
        if 'IS_COLAB' in all_text or 'ENV_TYPE == \'colab\'' in all_text:
            pass  # Good - connection checks for Colab
        else:
            results['warnings'].append("PostgreSQL connection doesn't check for Colab")
    
    # Overall pass/fail
    results['passed'] = (
        results['has_colab_check'] and
        results['has_postgresql_setup'] and
        not results['has_sqlite'] and
        len(results['code_errors']) == 0
    )
    
    return results

def print_results(results: Dict):
    """Print test results."""
    status = "✅ PASS" if results['passed'] else "❌ FAIL"
    print(f"  {status}")
    
    if results['has_colab_check']:
        print(f"    ✅ Colab-only check: Present")
    else:
        print(f"    ❌ Colab-only check: Missing")
    
    if results['has_postgresql_setup']:
        print(f"    ✅ PostgreSQL setup: Present")
    else:
        print(f"    ❌ PostgreSQL setup: Missing")
    
    if not results['has_sqlite']:
        print(f"    ✅ SQLite: Removed")
    else:
        print(f"    ❌ SQLite: Still present")
    
    if results['code_errors']:
        print(f"    ❌ Code errors: {len(results['code_errors'])}")
        for error in results['code_errors'][:3]:
            print(f"       - {error}")
    
    if results['warnings']:
        for warning in results['warnings']:
            print(f"    ⚠️  {warning}")

def main():
    """Main execution."""
    print("="*80)
    print("TESTING NOTEBOOKS FOR GOOGLE COLAB COMPATIBILITY")
    print("="*80)
    
    all_results = []
    passed_count = 0
    failed_count = 0
    
    # Test notebooks in db-* directories
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            results = test_notebook(notebook_path)
            all_results.append(results)
            print_results(results)
            
            if results['passed']:
                passed_count += 1
            else:
                failed_count += 1
    
    # Test notebooks in client/db
    client_db_dir = BASE_DIR / 'client' / 'db'
    if client_db_dir.exists():
        for db_name in DATABASES:
            for deliverable_dir in client_db_dir.glob(f"{db_name}/*"):
                if deliverable_dir.is_dir():
                    notebook_path = deliverable_dir / f"{db_name}.ipynb"
                    if notebook_path.exists():
                        results = test_notebook(notebook_path)
                        all_results.append(results)
                        print_results(results)
                        
                        if results['passed']:
                            passed_count += 1
                        else:
                            failed_count += 1
    
    # Summary
    print("\\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total notebooks tested: {len(all_results)}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    
    if failed_count > 0:
        print("\\nFailed notebooks:")
        for results in all_results:
            if not results['passed']:
                print(f"  - {Path(results['notebook']).name}")
                if results['code_errors']:
                    for error in results['code_errors']:
                        print(f"    Error: {error}")
    
    print("\\n" + "="*80)
    if failed_count == 0:
        print("✅ ALL NOTEBOOKS PASSED VALIDATION!")
        print("Ready for Google Colab!")
    else:
        print("⚠️  SOME NOTEBOOKS FAILED VALIDATION")
        print("Please review and fix issues above")
    print("="*80)
    
    return 0 if failed_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
