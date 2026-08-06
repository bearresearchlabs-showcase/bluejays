#!/usr/bin/env python3
"""
Verify notebook syntax is correct
"""

import json
import ast
import sys
from pathlib import Path

def detect_base_dir():
    """Detect base directory."""
    cwd = Path.cwd()
    if cwd.name == 'scripts' and (cwd.parent / 'db-6').exists():
        return cwd.parent
    return cwd.parent if (cwd.parent / 'db-6').exists() else cwd

BASE_DIR = detect_base_dir()
DATABASES = [f'db-{i}' for i in range(6, 16)]

def read_notebook(notebook_path: Path) -> dict:
    """Read notebook JSON."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_python_syntax(code: str) -> tuple:
    """Check Python syntax."""
    # Skip IPython magic commands
    if code.strip().startswith('!') or code.strip().startswith('%'):
        return True, []
    
    # Remove magic commands for syntax check
    lines = code.split('\n')
    python_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('!') and not stripped.startswith('%'):
            python_lines.append(line)
    
    python_code = '\n'.join(python_lines)
    
    if not python_code.strip():
        return True, []
    
    try:
        ast.parse(python_code)
        return True, []
    except SyntaxError as e:
        return False, [f"Syntax error: {e.msg} at line {e.lineno}"]
    except Exception as e:
        return False, [f"Error: {str(e)}"]

def verify_notebook(notebook_path: Path) -> dict:
    """Verify notebook syntax."""
    print(f"\\nVerifying: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    results = {
        'notebook': str(notebook_path),
        'total_cells': 0,
        'syntax_errors': 0,
        'errors': []
    }
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            results['total_cells'] += 1
            source = ''.join(cell.get('source', []))
            
            # Check syntax
            is_valid, errors = check_python_syntax(source)
            if not is_valid:
                results['syntax_errors'] += 1
                results['errors'].append(f"Cell {i+1}: {errors[0] if errors else 'Unknown error'}")
    
    status = "✅ PASS" if results['syntax_errors'] == 0 else "❌ FAIL"
    print(f"  {status} - {results['total_cells']} cells, {results['syntax_errors']} errors")
    
    if results['errors']:
        for error in results['errors'][:3]:
            print(f"    - {error}")
    
    return results

def main():
    """Main execution."""
    print("="*80)
    print("VERIFYING NOTEBOOK SYNTAX")
    print("="*80)
    
    all_results = []
    total_errors = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            results = verify_notebook(notebook_path)
            all_results.append(results)
            total_errors += results['syntax_errors']
    
    print("\\n" + "="*80)
    print("SYNTAX VERIFICATION SUMMARY")
    print("="*80)
    print(f"Total notebooks: {len(all_results)}")
    print(f"Total code cells: {sum(r['total_cells'] for r in all_results)}")
    print(f"Syntax errors: {total_errors}")
    
    if total_errors == 0:
        print("\\n✅ ALL NOTEBOOKS HAVE VALID SYNTAX!")
    else:
        print("\\n❌ SOME NOTEBOOKS HAVE SYNTAX ERRORS")
        for results in all_results:
            if results['syntax_errors'] > 0:
                print(f"  - {Path(results['notebook']).name}: {results['syntax_errors']} errors")
    
    print("="*80)
    
    return 0 if total_errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
