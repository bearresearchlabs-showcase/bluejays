#!/usr/bin/env python3
"""
Fix notebooks to use PostgreSQL only and run only in Google Colab
- Remove SQLite fallback
- Add PostgreSQL installation for Colab
- Ensure Colab-only execution
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

def detect_base_dir():
    """Detect base directory."""
    cwd = Path.cwd()
    if cwd.name.startswith('db-'):
        return cwd.parent
    if cwd.name == 'scripts' and (cwd.parent / 'db-6').exists():
        return cwd.parent
    return cwd.parent if (cwd.parent / 'db-6').exists() else cwd

BASE_DIR = detect_base_dir()
DATABASES = [f'db-{i}' for i in range(6, 16)]

def read_notebook(notebook_path: Path) -> Dict:
    """Read notebook JSON."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_notebook(notebook_path: Path, notebook: Dict):
    """Write notebook JSON."""
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

# Colab-only check code
COLAB_ONLY_CHECK = '''# ============================================================================
# GOOGLE COLAB ONLY - ENVIRONMENT CHECK
# ============================================================================

import sys
import os

# Verify we're running in Google Colab
IS_COLAB = False
try:
    import google.colab
    IS_COLAB = True
    print("✅ Running in Google Colab")
except ImportError:
    # Check alternative methods
    if os.path.exists('/content') and os.environ.get('COLAB_GPU'):
        IS_COLAB = True
        print("✅ Running in Google Colab (detected via COLAB_GPU)")
    elif os.path.exists('/content') and 'COLAB' in str(os.environ):
        IS_COLAB = True
        print("✅ Running in Google Colab (detected via COLAB env)")
    else:
        IS_COLAB = False

if not IS_COLAB:
    raise RuntimeError(
        "❌ ERROR: This notebook is designed to run ONLY in Google Colab.\\n"
        "Please open this notebook in Google Colab: https://colab.research.google.com/"
    )

print("="*80)
print("GOOGLE COLAB ENVIRONMENT CONFIRMED")
print("="*80)
'''

# PostgreSQL installation for Colab
POSTGRESQL_SETUP_COLAB = '''# ============================================================================
# POSTGRESQL INSTALLATION FOR GOOGLE COLAB
# ============================================================================

import subprocess
import os
import time

print("="*80)
print("INSTALLING POSTGRESQL FOR GOOGLE COLAB")
print("="*80)

# Check if PostgreSQL is already installed
postgres_installed = False
try:
    result = subprocess.run(['psql', '--version'], 
                          capture_output=True, 
                          text=True, 
                          timeout=5)
    if result.returncode == 0:
        print(f"✅ PostgreSQL already installed: {result.stdout.strip()}")
        postgres_installed = True
except (FileNotFoundError, subprocess.TimeoutExpired):
    pass

if not postgres_installed:
    print("Installing PostgreSQL...")
    
    # Update package list
    print("   Updating package list...")
    subprocess.run(['apt-get', 'update', '-qq'], check=True)
    
    # Install PostgreSQL
    print("   Installing PostgreSQL...")
    subprocess.run(['apt-get', 'install', '-y', '-qq', 'postgresql', 'postgresql-contrib'], check=True)
    
    # Start PostgreSQL service
    print("   Starting PostgreSQL service...")
    subprocess.run(['service', 'postgresql', 'start'], check=True)
    
    # Wait for PostgreSQL to be ready
    print("   Waiting for PostgreSQL to be ready...")
    time.sleep(3)
    
    print("✅ PostgreSQL installed and started")

# Verify PostgreSQL is running
try:
    result = subprocess.run(['pg_isready'], 
                          capture_output=True, 
                          text=True, 
                          timeout=5)
    if result.returncode == 0:
        print("✅ PostgreSQL is ready")
    else:
        print("⚠️  PostgreSQL may not be ready yet")
except Exception as e:
    print(f"⚠️  Could not verify PostgreSQL: {e}")

print("="*80)
'''

# PostgreSQL connection code (Colab-only, no SQLite)
def get_postgresql_connection_code(db_name: str) -> str:
    """Get PostgreSQL connection code with proper escaping."""
    return f'''# ============================================================================
# POSTGRESQL DATABASE CONNECTION (Colab Only)
# ============================================================================

import psycopg2
from pathlib import Path

# Database name
DB_NAME = "{db_name}"

def create_postgresql_connection():
    """Create PostgreSQL connection for Colab."""
    if not IS_COLAB:
        raise RuntimeError("This notebook requires Google Colab")
    
    # Colab PostgreSQL defaults
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='postgres',  # Default Colab PostgreSQL password
            database='postgres'  # Connect to default database first
        )
        print("✅ Connected to PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {{e}}")
        print("\\nTroubleshooting:")
        print("1. Make sure PostgreSQL is installed (run the installation cell above)")
        print("2. Check if PostgreSQL service is running: !service postgresql status")
        print("3. Try restarting PostgreSQL: !service postgresql restart")
        raise

# Create connection
conn = create_postgresql_connection()
print(f"\\nDatabase connection: PostgreSQL (Colab)")
print(f"Host: localhost")
print(f"Port: 5432")
print(f"User: postgres")
'''

def remove_sqlite_code(cell_source: List[str]) -> List[str]:
    """Remove SQLite-related code from cell."""
    source_str = ''.join(cell_source)
    
    # Remove SQLite imports and code
    new_source = []
    skip_line = False
    
    for line in cell_source:
        # Skip SQLite imports
        if 'import sqlite3' in line:
            continue
        # Skip SQLite fallback functions
        if 'def get_database_connection' in line and 'sqlite' in source_str.lower():
            skip_line = True
            continue
        if skip_line and ('def ' in line or 'class ' in line or line.strip().startswith('#')):
            skip_line = False
        if skip_line:
            continue
        # Remove SQLite-related code blocks
        if 'sqlite3.connect' in line or 'sqlite' in line.lower() and 'postgresql' not in line.lower():
            continue
        new_source.append(line)
    
    return new_source if new_source != cell_source else cell_source

def add_colab_only_check(notebook: Dict) -> Dict:
    """Add Colab-only check at the beginning."""
    check_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": COLAB_ONLY_CHECK.split('\n')
    }
    
    # Insert at the very beginning (after title cell)
    notebook['cells'].insert(1, check_cell)
    return notebook

def add_postgresql_setup(notebook: Dict) -> Dict:
    """Add PostgreSQL setup cell for Colab."""
    setup_markdown = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## PostgreSQL Setup for Google Colab\n",
            "\n",
            "This notebook requires PostgreSQL. Run the cell below to install and start PostgreSQL in Colab."
        ]
    }
    
    setup_code = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": POSTGRESQL_SETUP_COLAB.split('\n')
    }
    
    # Find Colab setup cell or insert after Colab-only check
    insert_idx = 2
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'GOOGLE COLAB ONLY' in source:
                insert_idx = i + 1
                break
    
    notebook['cells'].insert(insert_idx, setup_markdown)
    notebook['cells'].insert(insert_idx + 1, setup_code)
    return notebook

def fix_postgresql_connection(cell_source: List[str], db_name: str) -> List[str]:
    """Fix PostgreSQL connection code to be Colab-only."""
    source_str = ''.join(cell_source)
    
    # Check if already has Colab-only PostgreSQL connection
    if 'IS_COLAB' in source_str and 'sqlite' not in source_str.lower():
        return cell_source
    
    # Replace with Colab-only PostgreSQL connection
    return get_postgresql_connection_code(db_name).split('\n')

def fix_notebook_colab_postgresql_only(notebook_path: Path) -> bool:
    """Fix notebook for Colab-only PostgreSQL."""
    print(f"\\nFixing: {notebook_path.name}")
    
    try:
        notebook = read_notebook(notebook_path)
    except Exception as e:
        print(f"   ❌ Error reading: {e}")
        return False
    
    db_name = notebook_path.stem
    updated = False
    
    # Add Colab-only check
    has_colab_check = False
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'GOOGLE COLAB ONLY' in source:
                has_colab_check = True
                break
    
    if not has_colab_check:
        notebook = add_colab_only_check(notebook)
        updated = True
        print(f"   ✅ Added Colab-only check")
    
    # Add PostgreSQL setup
    has_postgresql_setup = False
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'INSTALLING POSTGRESQL FOR GOOGLE COLAB' in source:
                has_postgresql_setup = True
                break
    
    if not has_postgresql_setup:
        notebook = add_postgresql_setup(notebook)
        updated = True
        print(f"   ✅ Added PostgreSQL setup for Colab")
    
    # Fix database connection cells
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            source_str = ''.join(source)
            
            # Remove SQLite code
            if 'sqlite' in source_str.lower():
                fixed_source = remove_sqlite_code(source)
                if fixed_source != source:
                    cell['source'] = fixed_source
                    updated = True
                    print(f"   ✅ Removed SQLite code (cell {i+1})")
            
            # Fix PostgreSQL connection
            if ('DATABASE CONNECTION' in source_str or 
                'DATABASE CONFIGURATION' in source_str or
                'psycopg2.connect' in source_str):
                fixed_source = fix_postgresql_connection(source, db_name)
                if fixed_source != source:
                    cell['source'] = fixed_source
                    updated = True
                    print(f"   ✅ Fixed PostgreSQL connection for Colab (cell {i+1})")
    
    if updated:
        # Backup
        backup_path = notebook_path.with_suffix('.ipynb.colab_pg_backup')
        try:
            write_notebook(backup_path, read_notebook(notebook_path))
        except:
            pass
        
        # Save
        try:
            write_notebook(notebook_path, notebook)
            print(f"   ✅ Saved fixed notebook")
            return True
        except Exception as e:
            print(f"   ❌ Error saving: {e}")
            return False
    
    return False

def main():
    """Main execution."""
    print("="*80)
    print("FIXING NOTEBOOKS FOR GOOGLE COLAB (POSTGRESQL ONLY)")
    print("="*80)
    
    updated_count = 0
    
    # Fix notebooks in db-* directories
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if fix_notebook_colab_postgresql_only(notebook_path):
                updated_count += 1
    
    # Fix notebooks in client/db
    client_db_dir = BASE_DIR / 'client' / 'db'
    if client_db_dir.exists():
        for db_name in DATABASES:
            for deliverable_dir in client_db_dir.glob(f"{db_name}/*"):
                if deliverable_dir.is_dir():
                    notebook_path = deliverable_dir / f"{db_name}.ipynb"
                    if notebook_path.exists():
                        if fix_notebook_colab_postgresql_only(notebook_path):
                            updated_count += 1
    
    print("\\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Fixed notebooks: {updated_count}")
    print("\\n✅ Notebooks configured for Google Colab (PostgreSQL only)!")
    print("\\nKey changes:")
    print("- ✅ Colab-only execution check added")
    print("- ✅ PostgreSQL installation for Colab added")
    print("- ✅ SQLite fallback removed")
    print("- ✅ PostgreSQL connection configured for Colab")
    print("\\nTo use in Colab:")
    print("1. Upload notebook to Google Colab")
    print("2. Run cells in order")
    print("3. PostgreSQL will be installed automatically")
    print("4. Database will be created and populated")

if __name__ == '__main__':
    main()
