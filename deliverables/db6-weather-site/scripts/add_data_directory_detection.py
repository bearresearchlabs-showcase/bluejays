#!/usr/bin/env python3
"""
Add self-aware data/ directory detection to notebooks
- Detect notebook location
- Recursively find data/ directory
- Verify data/ directory contains expected files
- Set up paths for schema.sql, data.sql, etc.
"""

import json
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

def write_notebook(notebook_path: Path, notebook: dict):
    """Write notebook JSON."""
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

DATA_DIRECTORY_DETECTION_CELL = '''# ============================================================================
# SELF-AWARE DATA DIRECTORY DETECTION
# ============================================================================

import os
import sys
from pathlib import Path

print("="*80)
print("DATA DIRECTORY DETECTION")
print("="*80)

def find_data_directory():
    """
    Self-aware function to find data/ directory.
    Works when notebook is uploaded to Colab or run locally.
    """
    # Get notebook's current directory
    if IS_COLAB:
        # In Colab, check common locations
        search_paths = [
            Path('/content'),
            Path('/content/drive/MyDrive'),
            Path.cwd(),
        ]
    else:
        # Local execution
        search_paths = [
            Path.cwd(),
            Path(__file__).parent if '__file__' in globals() else Path.cwd(),
            Path.cwd().parent,
        ]
    
    # Also check parent directories recursively
    current = Path.cwd()
    for _ in range(5):  # Check up to 5 levels up
        search_paths.append(current)
        current = current.parent
    
    print(f"\\nSearching for data/ directory...")
    print(f"Current working directory: {Path.cwd()}")
    
    # Search for data/ directory
    data_dir = None
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Check if data/ exists here
        potential_data = search_path / 'data'
        if potential_data.exists() and potential_data.is_dir():
            data_dir = potential_data
            print(f"✅ Found data/ directory: {data_dir}")
            break
        
        # Recursively search subdirectories (limit depth to avoid long searches)
        try:
            for item in search_path.rglob('data'):
                if item.is_dir() and item.name == 'data':
                    # Verify it contains expected files
                    expected_files = ['schema.sql', 'data.sql']
                    has_expected = any((item / f).exists() for f in expected_files)
                    if has_expected:
                        data_dir = item
                        print(f"✅ Found data/ directory (recursive): {data_dir}")
                        break
            if data_dir:
                break
        except (PermissionError, OSError):
            continue
    
    if not data_dir:
        # Try finding by database name pattern
        db_name = Path.cwd().name
        if db_name.startswith('db-'):
            # Look for db-N/data pattern
            for search_path in search_paths:
                potential_db = search_path / db_name / 'data'
                if potential_db.exists() and potential_db.is_dir():
                    data_dir = potential_db
                    print(f"✅ Found data/ directory by DB name: {data_dir}")
                    break
    
    return data_dir

def verify_data_directory(data_dir: Path):
    """Verify data/ directory contains expected files."""
    if not data_dir or not data_dir.exists():
        return False
    
    expected_files = ['schema.sql']
    optional_files = ['data.sql']
    
    print(f"\\nVerifying data/ directory contents...")
    print(f"Location: {data_dir}")
    
    found_files = []
    missing_files = []
    
    for file_name in expected_files:
        file_path = data_dir / file_name
        if file_path.exists():
            found_files.append(file_name)
            print(f"  ✅ {file_name}")
        else:
            missing_files.append(file_name)
            print(f"  ❌ {file_name} (missing)")
    
    for file_name in optional_files:
        file_path = data_dir / file_name
        if file_path.exists():
            found_files.append(file_name)
            print(f"  ✅ {file_name} (optional)")
        else:
            print(f"  ⚠️  {file_name} (optional, not found)")
    
    if missing_files:
        print(f"\\n⚠️  Warning: Missing required files: {missing_files}")
        return False
    
    return True

# Detect data directory
DATA_DIR = find_data_directory()

if DATA_DIR:
    if verify_data_directory(DATA_DIR):
        print(f"\\n✅ Data directory verified and ready!")
        print(f"   Schema file: {DATA_DIR / 'schema.sql'}")
        if (DATA_DIR / 'data.sql').exists():
            print(f"   Data file: {DATA_DIR / 'data.sql'}")
        
        # Set global variables for use in other cells
        SCHEMA_FILE = DATA_DIR / 'schema.sql'
        DATA_FILE = DATA_DIR / 'data.sql' if (DATA_DIR / 'data.sql').exists() else None
        
        print(f"\\n✅ Global variables set:")
        print(f"   DATA_DIR = {DATA_DIR}")
        print(f"   SCHEMA_FILE = {SCHEMA_FILE}")
        if DATA_FILE:
            print(f"   DATA_FILE = {DATA_FILE}")
    else:
        print(f"\\n⚠️  Data directory found but verification failed")
        print(f"   Location: {DATA_DIR}")
        print(f"   Please ensure schema.sql exists in this directory")
else:
    print(f"\\n❌ Data directory not found!")
    print(f"\\nTroubleshooting:")
    print(f"1. Ensure data/ directory is uploaded to Colab")
    print(f"2. Check that data/ contains schema.sql")
    print(f"3. Verify notebook is in same directory structure as data/")
    print(f"\\nCurrent directory: {Path.cwd()}")
    print(f"Contents:")
    try:
        for item in sorted(Path.cwd().iterdir()):
            print(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")
    except PermissionError:
        print("  (Permission denied)")

print("="*80)
'''

def find_insertion_point(notebook: dict) -> int:
    """Find where to insert the data directory detection cell."""
    # Insert after Python installation, before PostgreSQL setup
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'POSTGRESQL SETUP' in source.upper() or 'POSTGRESQL' in source.upper():
                return i
            if 'GOOGLE COLAB ONLY' in source or 'ENVIRONMENT CHECK' in source:
                # Insert after Colab check
                for j in range(i + 1, len(notebook['cells'])):
                    if notebook['cells'][j]['cell_type'] == 'code':
                        source_j = ''.join(notebook['cells'][j].get('source', []))
                        if 'POSTGRESQL' in source_j.upper():
                            return j
                        if 'DATA DIRECTORY' in source_j.upper():
                            return -1  # Already exists
                return i + 1
    
    # Default: after first code cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            return i + 1
    
    return len(notebook['cells'])

def add_data_detection_cell(notebook: dict) -> bool:
    """Add data directory detection cell to notebook."""
    # Check if already exists
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    if 'DATA DIRECTORY DETECTION' in all_text or 'find_data_directory' in all_text:
        print("   ✅ Data directory detection cell already exists")
        return False
    
    insert_idx = find_insertion_point(notebook)
    if insert_idx < 0:
        return False
    
    # Add markdown cell
    markdown_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Data Directory Detection\n",
            "\n",
            "This notebook automatically detects the `data/` directory containing `schema.sql` and `data.sql` files.\n",
            "It works when uploaded to Google Colab or run locally."
        ]
    }
    
    # Add code cell
    code_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": DATA_DIRECTORY_DETECTION_CELL.split('\n')
    }
    
    notebook['cells'].insert(insert_idx, markdown_cell)
    notebook['cells'].insert(insert_idx + 1, code_cell)
    
    print(f"   ✅ Added data directory detection cell (at index {insert_idx})")
    return True

def fix_notebook(notebook_path: Path) -> bool:
    """Add data directory detection to notebook."""
    print(f"\\nAdding data directory detection: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    
    if add_data_detection_cell(notebook):
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
        return True
    
    return False

def main():
    """Main execution."""
    print("="*80)
    print("ADDING SELF-AWARE DATA DIRECTORY DETECTION TO NOTEBOOKS")
    print("="*80)
    
    fixed_count = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if fix_notebook(notebook_path):
                fixed_count += 1
    
    print("\\n" + "="*80)
    print(f"Updated notebooks: {fixed_count}")
    print("✅ DATA DIRECTORY DETECTION ADDED!")
    print("="*80)

if __name__ == '__main__':
    main()
