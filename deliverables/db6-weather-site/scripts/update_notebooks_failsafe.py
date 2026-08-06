#!/usr/bin/env python3
"""
Update Jupyter notebooks with failsafe logic for path correction and forced package installation
This script adds robust error handling and path correction directly into notebook cells
"""

import json
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

FAILSAFE_CODE = '''
# ============================================================================
# FAILSAFE: Force Path Correction and Package Installation
# ============================================================================
import sys
import subprocess
import os
from pathlib import Path

def force_install_package(package_name, import_name=None):
    """Force install package using multiple methods."""
    if import_name is None:
        import_name = package_name.split('[')[0].split('==')[0].split('>=')[0]
    
    # Try import first
    try:
        __import__(import_name)
        return True
    except ImportError:
        pass
    
    # Method 1: pip install --user
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', '--quiet', package_name], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    # Method 2: pip install --break-system-packages (Python 3.12+)
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--break-system-packages', '--quiet', package_name],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    # Method 3: pip install system-wide
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', package_name],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    # Method 4: conda install (if conda available)
    try:
        subprocess.check_call(['conda', 'install', '-y', '--quiet', package_name],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    # Method 5: apt-get install (Linux/Docker)
    if os.path.exists('/usr/bin/apt-get'):
        try:
            apt_package = f'python3-{import_name.replace("_", "-")}'
            subprocess.check_call(['apt-get', 'install', '-y', '--quiet', apt_package],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            __import__(import_name)
            return True
        except:
            pass
    
    # Method 6: Direct pip install with --force-reinstall
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--quiet', package_name],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    print(f"⚠️  Warning: Could not install {package_name}, continuing anyway...")
    return False

def correct_file_path(file_path, search_paths=None):
    """Correct file path by searching multiple locations."""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # If path exists, return it
    if file_path.exists():
        return file_path
    
    # Default search paths
    if search_paths is None:
        search_paths = [
            Path.cwd(),
            Path('/workspace/client/db'),
            Path('/workspace/db'),
            Path('/workspace'),
            Path('/content/drive/MyDrive/db'),
            Path('/content/db'),
            Path('/content'),
            Path.home() / 'Documents' / 'AQ' / 'db',
            BASE_DIR if 'BASE_DIR' in globals() else Path('/Users/machine/Documents/AQ/db'),
        ]
    
    # Search recursively
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Try direct path
        candidate = search_path / file_path.name
        if candidate.exists():
            return candidate
        
        # Try recursive search
        try:
            for found_path in search_path.rglob(file_path.name):
                if found_path.is_file():
                    return found_path
        except:
            continue
    
    # Return original path (will fail later, but at least we tried)
    return file_path

def ensure_packages_installed():
    """Ensure all required packages are installed."""
    required_packages = [
        ('psycopg2-binary', 'psycopg2'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('ipython', 'IPython'),
        ('jupyter', 'jupyter'),
    ]
    
    print("\\n" + "="*80)
    print("FAILSAFE: Ensuring all packages are installed...")
    print("="*80)
    
    for package, import_name in required_packages:
        if force_install_package(package, import_name):
            print(f"✅ {package} installed")
        else:
            print(f"⚠️  {package} installation failed, but continuing...")
    
    print("="*80 + "\\n")

def ensure_paths_correct():
    """Ensure all file paths are correct."""
    print("\\n" + "="*80)
    print("FAILSAFE: Correcting file paths...")
    print("="*80)
    
    # Correct BASE_DIR if needed
    if 'BASE_DIR' not in globals() or not BASE_DIR.exists():
        BASE_DIR = correct_file_path(Path('/Users/machine/Documents/AQ/db'))
        print(f"✅ BASE_DIR corrected: {BASE_DIR}")
    
    # Correct DB_DIR if needed
    if 'DB_DIR' in globals() and DB_DIR and not DB_DIR.exists():
        DB_DIR = correct_file_path(DB_DIR)
        print(f"✅ DB_DIR corrected: {DB_DIR}")
    
    print("="*80 + "\\n")

# Run failsafe checks
ensure_packages_installed()
ensure_paths_correct()

print("✅ Failsafe checks complete")
'''

def add_failsafe_to_notebook(notebook_path: Path):
    """Add failsafe code to notebook."""
    with open(notebook_path) as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    
    # Check if failsafe already exists
    failsafe_exists = False
    for cell in cells:
        source = ''.join(cell.get('source', []))
        if 'FAILSAFE: Force Path Correction' in source:
            failsafe_exists = True
            break
    
    if failsafe_exists:
        print(f"  ⚠️  Failsafe already exists in {notebook_path.name}")
        return False
    
    # Find the first code cell after environment detection
    insert_index = 0
    for i, cell in enumerate(cells):
        source = ''.join(cell.get('source', []))
        if 'ENVIRONMENT DETECTION COMPLETE' in source or 'Environment Type:' in source:
            insert_index = i + 1
            break
    
    # Create failsafe cell
    failsafe_cell = {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': FAILSAFE_CODE.split('\n')
    }
    
    # Insert failsafe cell
    cells.insert(insert_index, failsafe_cell)
    nb['cells'] = cells
    
    # Backup original
    backup_path = notebook_path.with_suffix('.ipynb.failsafe_backup')
    if not backup_path.exists():
        with open(backup_path, 'w') as f:
            json.dump(json.load(open(notebook_path)), f, indent=1)
    
    # Write updated notebook
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print(f"  ✅ Added failsafe to {notebook_path.name}")
    return True

def update_notebooks_in_directory(directory: Path):
    """Update all notebooks in a directory."""
    updated_count = 0
    
    for notebook_path in directory.rglob('*.ipynb'):
        # Skip backups
        if '.backup' in notebook_path.name or 'executed' in notebook_path.name:
            continue
        
        if add_failsafe_to_notebook(notebook_path):
            updated_count += 1
    
    return updated_count

def main():
    """Update notebooks with failsafe logic."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add failsafe logic to notebooks')
    parser.add_argument('--db', type=str, help='Specific database to update')
    parser.add_argument('--root-dir', type=str, help='Root directory to search')
    parser.add_argument('--client-only', action='store_true', help='Update only client/db notebooks')
    
    args = parser.parse_args()
    
    print("="*80)
    print("UPDATING NOTEBOOKS WITH FAILSAFE LOGIC")
    print("="*80)
    
    root_dir = Path(args.root_dir) if args.root_dir else BASE_DIR
    
    if args.client_only:
        directories = [CLIENT_DB_DIR]
    elif args.db:
        deliverable = DB_TO_DELIVERABLE.get(args.db)
        if deliverable:
            directories = [
                CLIENT_DB_DIR / args.db / deliverable,
                ROOT_DB_DIR / args.db
            ]
        else:
            directories = [ROOT_DB_DIR / args.db]
    else:
        directories = [CLIENT_DB_DIR, ROOT_DB_DIR]
    
    total_updated = 0
    for directory in directories:
        if not directory.exists():
            continue
        
        print(f"\\nUpdating notebooks in: {directory.relative_to(BASE_DIR)}")
        updated = update_notebooks_in_directory(directory)
        total_updated += updated
    
    print(f"\\n{'='*80}")
    print(f"UPDATES COMPLETE")
    print(f"{'='*80}")
    print(f"Notebooks updated: {total_updated}")

if __name__ == '__main__':
    main()
