#!/usr/bin/env python3
"""
Run Jupyter notebooks for all databases (db-6 through db-15)
Supports multiple execution methods with failsafe path correction and package installation
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'
ROOT_DB_DIR = BASE_DIR

DATABASES = [f'db-{i}' for i in range(6, 16)]

DB_TO_DELIVERABLE = {
    'db-6': 'db6-weather-consulting-insurance',
    'db-7': 'db7-maritime-shipping-intelligence',
    'db-8': 'db8-job-market',
    'db-9': 'db9-shipping-database',
    'db-10': 'db10-shopping-aggregator-database',
    'db-11': 'db11-parking-database',
    'db-12': 'db12-credit-card-and-rewards-optimization-system',
    'db-13': 'db13-ai-benchmark-marketing-database',
    'db-14': 'db14-cloud-instance-cost-database',
    'db-15': 'db15-electricity-cost-and-solar-rebate-database'
}

def find_notebook(db_name: str, root_dir: Path = None) -> Path:
    """Find notebook file recursively."""
    if root_dir is None:
        root_dir = BASE_DIR
    
    # Search in multiple locations
    search_paths = [
        root_dir / 'client' / 'db' / db_name / DB_TO_DELIVERABLE.get(db_name, '') / f'{db_name}.ipynb',
        root_dir / db_name / f'{db_name}.ipynb',
        root_dir / 'client' / 'db' / db_name / f'{db_name}.ipynb',
    ]
    
    for path in search_paths:
        if path.exists():
            return path
    
    # Recursive search
    for path in root_dir.rglob(f'{db_name}.ipynb'):
        if path.is_file():
            return path
    
    return None

def run_notebook_method1(notebook_path: Path, output_dir: Path = None):
    """Method 1: Using jupyter nbconvert --execute"""
    if output_dir is None:
        output_dir = notebook_path.parent
    
    output_file = output_dir / f"{notebook_path.stem}_executed.ipynb"
    
    cmd = [
        'jupyter', 'nbconvert',
        '--to', 'notebook',
        '--execute',
        '--inplace' if output_dir == notebook_path.parent else f'--output={output_file}',
        '--ExecutePreprocessor.timeout=3600',
        '--ExecutePreprocessor.kernel_name=python3',
        '--ExecutePreprocessor.allow_errors=True',
        str(notebook_path)
    ]
    
    print(f"  Method 1: jupyter nbconvert --execute")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def run_notebook_method2(notebook_path: Path, output_dir: Path = None):
    """Method 2: Using papermill"""
    if output_dir is None:
        output_dir = notebook_path.parent
    
    output_file = output_dir / f"{notebook_path.stem}_executed.ipynb"
    
    cmd = [
        'papermill',
        str(notebook_path),
        str(output_file),
        '--execution-timeout=3600',
        '--log-output'
    ]
    
    print(f"  Method 2: papermill")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def run_notebook_method3(notebook_path: Path):
    """Method 3: Using Python nbformat directly"""
    try:
        import nbformat
        from nbconvert.preprocessors import ExecutePreprocessor
        
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)
        
        ep = ExecutePreprocessor(timeout=3600, kernel_name='python3', allow_errors=True)
        ep.preprocess(nb, {'metadata': {'path': str(notebook_path.parent)}})
        
        output_file = notebook_path.parent / f"{notebook_path.stem}_executed.ipynb"
        with open(output_file, 'w') as f:
            nbformat.write(nb, f)
        
        print(f"  Method 3: Python nbformat")
        return True, "Execution completed", ""
    except Exception as e:
        return False, "", str(e)

def run_notebook(db_name: str, method: int = 1, root_dir: Path = None):
    """Run notebook for a database."""
    if root_dir is None:
        root_dir = BASE_DIR
    
    notebook_path = find_notebook(db_name, root_dir)
    
    if not notebook_path:
        print(f"❌ {db_name}: Notebook not found")
        return False
    
    print(f"\n{'='*80}")
    print(f"Running {db_name}")
    print(f"Notebook: {notebook_path.relative_to(BASE_DIR)}")
    print(f"{'='*80}")
    
    success = False
    stdout = ""
    stderr = ""
    
    if method == 1:
        success, stdout, stderr = run_notebook_method1(notebook_path)
    elif method == 2:
        success, stdout, stderr = run_notebook_method2(notebook_path)
    elif method == 3:
        success, stdout, stderr = run_notebook_method3(notebook_path)
    else:
        # Try all methods
        for m in [1, 2, 3]:
            if m == 1:
                success, stdout, stderr = run_notebook_method1(notebook_path)
            elif m == 2:
                success, stdout, stderr = run_notebook_method2(notebook_path)
            elif m == 3:
                success, stdout, stderr = run_notebook_method3(notebook_path)
            
            if success:
                print(f"✅ {db_name}: Successfully executed using method {m}")
                break
        
        if not success:
            print(f"❌ {db_name}: All methods failed")
    
    if stderr:
        print(f"Errors: {stderr[:500]}...")
    
    return success

def main():
    """Run notebooks for all databases."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Jupyter notebooks for databases')
    parser.add_argument('--db', type=str, help='Specific database to run (e.g., db-6)')
    parser.add_argument('--method', type=int, choices=[1, 2, 3], default=1,
                       help='Execution method (1=jupyter nbconvert, 2=papermill, 3=nbformat)')
    parser.add_argument('--all-methods', action='store_true',
                       help='Try all methods until one succeeds')
    parser.add_argument('--root-dir', type=str, help='Root directory to search for notebooks')
    
    args = parser.parse_args()
    
    root_dir = Path(args.root_dir) if args.root_dir else BASE_DIR
    
    print("="*80)
    print("RUNNING JUPYTER NOTEBOOKS")
    print("="*80)
    print(f"Root directory: {root_dir}")
    print(f"Execution method: {args.method if not args.all_methods else 'All methods'}")
    print()
    
    databases_to_run = [args.db] if args.db else DATABASES
    
    results = {}
    for db_name in databases_to_run:
        if args.all_methods:
            success = run_notebook(db_name, method=0, root_dir=root_dir)
        else:
            success = run_notebook(db_name, method=args.method, root_dir=root_dir)
        results[db_name] = success
    
    print(f"\n{'='*80}")
    print("EXECUTION SUMMARY")
    print(f"{'='*80}")
    
    successful = sum(1 for s in results.values() if s)
    total = len(results)
    
    print(f"Successful: {successful}/{total}")
    print(f"Failed: {total - successful}/{total}")
    
    for db_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {db_name}")

if __name__ == '__main__':
    main()
