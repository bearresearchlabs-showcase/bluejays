#!/usr/bin/env python3
"""
Add Streamlit dashboard execution cells to Jupyter notebooks
Allows running Streamlit dashboards directly from notebooks
"""

import json
import shutil
from pathlib import Path

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

STREAMLIT_CELL_CODE = '''
# ============================================================================
# STREAMLIT DASHBOARD EXECUTION
# ============================================================================
import subprocess
import sys
import os
from pathlib import Path
import webbrowser
import time
import threading

def find_dashboard_file():
    """Find Streamlit dashboard file recursively."""
    search_paths = [
        Path.cwd(),
        Path('/workspace/client/db'),
        Path('/workspace/db'),
        Path('/workspace'),
        Path('/content/drive/MyDrive/db'),
        Path('/content/db'),
        Path('/content'),
        Path.home() / 'Documents' / 'AQ' / 'db',
    ]
    
    dashboard_name = f'{DB_NAME}_dashboard.py'
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Try direct path
        candidate = search_path / dashboard_name
        if candidate.exists():
            return candidate
        
        # Try recursive search
        try:
            for found_path in search_path.rglob(dashboard_name):
                if found_path.is_file():
                    return found_path
        except:
            continue
    
    return None

def run_streamlit_dashboard(method='notebook', port=8501, open_browser=True):
    """
    Run Streamlit dashboard from Jupyter notebook.
    
    Methods:
    - 'notebook': Run in notebook output (using streamlit's notebook mode)
    - 'subprocess': Run as subprocess (background)
    - 'magic': Use !streamlit run magic command
    """
    dashboard_path = find_dashboard_file()
    
    if not dashboard_path:
        print("❌ Dashboard file not found")
        print(f"   Looking for: {DB_NAME}_dashboard.py")
        return None
    
    print(f"✅ Found dashboard: {dashboard_path}")
    
    if method == 'notebook':
        # Method 1: Run Streamlit in notebook-compatible mode
        # Note: Streamlit doesn't natively support notebooks, but we can use iframe
        print("\\n" + "="*80)
        print("STREAMLIT DASHBOARD - NOTEBOOK MODE")
        print("="*80)
        print(f"\\nDashboard: {dashboard_path.name}")
        print(f"\\nTo run dashboard:")
        print(f"  1. Run this cell to start the server")
        print(f"  2. Open the URL shown below in a new tab")
        print(f"  3. Or use: !streamlit run {dashboard_path} --server.port={port}")
        print("\\n" + "="*80)
        
        # Start Streamlit as subprocess
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            str(dashboard_path),
            '--server.port', str(port),
            '--server.headless', 'true',
            '--server.runOnSave', 'false',
            '--browser.gatherUsageStats', 'false'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Get the URL
        url = f"http://localhost:{port}"
        print(f"\\n🌐 Dashboard URL: {url}")
        print(f"\\nServer started in background (PID: {process.pid})")
        print(f"\\nTo stop: process.terminate() or run stop_streamlit()")
        
        # Store process for later termination
        globals()['_streamlit_process'] = process
        
        # Try to open browser
        if open_browser:
            try:
                webbrowser.open(url)
            except:
                pass
        
        return process
    
    elif method == 'subprocess':
        # Method 2: Run as background subprocess
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            str(dashboard_path),
            '--server.port', str(port)
        ]
        
        process = subprocess.Popen(cmd)
        print(f"✅ Streamlit started (PID: {process.pid})")
        print(f"🌐 Dashboard: http://localhost:{port}")
        return process
    
    elif method == 'magic':
        # Method 3: Print magic command for user to run
        print("Run this command in a new cell:")
        print(f"!streamlit run {dashboard_path} --server.port={port}")
        return None

def stop_streamlit():
    """Stop running Streamlit process."""
    if '_streamlit_process' in globals():
        process = globals()['_streamlit_process']
        process.terminate()
        print("✅ Streamlit stopped")
    else:
        print("⚠️  No Streamlit process found")

# Auto-detect DB_NAME if not set
if 'DB_NAME' not in globals():
    # Try to detect from current directory or notebook name
    cwd = Path.cwd()
    for db_num in range(6, 16):
        if f'db-{db_num}' in str(cwd) or f'db{db_num}' in str(cwd):
            DB_NAME = f'db-{db_num}'
            break
    else:
        DB_NAME = 'db-6'  # Default
        print(f"⚠️  Could not detect DB_NAME, using default: {DB_NAME}")

print("\\n" + "="*80)
print("STREAMLIT DASHBOARD INTEGRATION")
print("="*80)
print(f"Database: {DB_NAME}")
print("\\nAvailable methods:")
print("  1. run_streamlit_dashboard(method='notebook') - Run in notebook mode")
print("  2. run_streamlit_dashboard(method='subprocess') - Run as background process")
print("  3. run_streamlit_dashboard(method='magic') - Get magic command")
print("  4. stop_streamlit() - Stop running dashboard")
print("\\n" + "="*80)
'''

STREAMLIT_MAGIC_CELL = '''
# ============================================================================
# STREAMLIT DASHBOARD - MAGIC COMMAND METHOD
# ============================================================================
# Run this cell to start the Streamlit dashboard
# The dashboard will open in a new browser tab

# Find dashboard file
dashboard_path = find_dashboard_file()
if dashboard_path:
    print(f"Starting dashboard: {dashboard_path.name}")
    print(f"\\nRun this command:")
    print(f"!streamlit run {dashboard_path} --server.port=8501 --server.headless=true")
    print(f"\\nOr click the link below after running:")
    print(f"http://localhost:8501")
else:
    print("❌ Dashboard file not found")
'''

def add_streamlit_cells_to_notebook(notebook_path: Path, db_name: str):
    """Add Streamlit execution cells to notebook."""
    with open(notebook_path) as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    
    # Check if Streamlit cells already exist
    has_streamlit = False
    for cell in cells:
        source = ''.join(cell.get('source', []))
        if 'STREAMLIT DASHBOARD' in source or 'run_streamlit_dashboard' in source:
            has_streamlit = True
            break
    
    if has_streamlit:
        print(f"  ⚠️  Streamlit cells already exist in {notebook_path.name}")
        return False
    
    # Find insertion point (after query execution or at end)
    insert_index = len(cells)
    for i, cell in enumerate(cells):
        source = ''.join(cell.get('source', []))
        if 'Query Execution Complete' in source or 'Visualization' in source or 'Documentation' in source:
            insert_index = i + 1
            break
    
    # Create Streamlit integration cell
    streamlit_cell = {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': STREAMLIT_CELL_CODE.split('\n')
    }
    
    # Create magic command cell (markdown with instructions)
    magic_cell = {
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '## Streamlit Dashboard\n',
            '\n',
            'Run the Streamlit dashboard using one of these methods:\n',
            '\n',
            '**Method 1: Notebook Mode** (Recommended)\n',
            '```python\n',
            'run_streamlit_dashboard(method=\'notebook\', port=8501)\n',
            '```\n',
            '\n',
            '**Method 2: Magic Command**\n',
            '```bash\n',
            f'!streamlit run {db_name}_dashboard.py --server.port=8501\n',
            '```\n',
            '\n',
            '**Method 3: Background Process**\n',
            '```python\n',
            'run_streamlit_dashboard(method=\'subprocess\', port=8501)\n',
            '```\n'
        ]
    }
    
    # Insert cells
    cells.insert(insert_index, streamlit_cell)
    cells.insert(insert_index + 1, magic_cell)
    nb['cells'] = cells
    
    # Create backup
    backup_path = notebook_path.with_suffix('.ipynb.streamlit_backup')
    if not backup_path.exists():
        shutil.copy2(notebook_path, backup_path)
    
    # Write updated notebook
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print(f"  ✅ Added Streamlit cells to {notebook_path.name}")
    return True

def update_notebooks_in_directory(directory: Path):
    """Update all notebooks in directory."""
    updated_count = 0
    
    for notebook_path in directory.rglob('*.ipynb'):
        if '.backup' in notebook_path.name:
            continue
        
        # Try to detect database name from path
        db_name = None
        for db in DATABASES:
            if db in str(notebook_path):
                db_name = db
                break
        
        if not db_name:
            # Try to extract from filename
            if notebook_path.stem.startswith('db-'):
                db_name = notebook_path.stem
            else:
                continue
        
        if add_streamlit_cells_to_notebook(notebook_path, db_name):
            updated_count += 1
    
    return updated_count

def main():
    """Add Streamlit integration to notebooks."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str)
    parser.add_argument('--root-dir', type=str)
    parser.add_argument('--client-only', action='store_true')
    
    args = parser.parse_args()
    
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
    
    print("="*80)
    print("ADDING STREAMLIT DASHBOARD INTEGRATION TO NOTEBOOKS")
    print("="*80)
    
    total_updated = 0
    for directory in directories:
        if not directory.exists():
            continue
        
        print(f"\\nProcessing: {directory.relative_to(BASE_DIR)}")
        updated = update_notebooks_in_directory(directory)
        total_updated += updated
    
    print(f"\\n{'='*80}")
    print(f"UPDATES COMPLETE")
    print(f"{'='*80}")
    print(f"Notebooks updated: {total_updated}")
    print(f"\\nStreamlit dashboards can now be run from notebooks!")

if __name__ == '__main__':
    main()
