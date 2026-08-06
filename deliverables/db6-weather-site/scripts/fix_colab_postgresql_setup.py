#!/usr/bin/env python3
"""
Fix PostgreSQL setup cell for Colab
- Ensure PostgreSQL installation code is properly formatted
- Add magic command alternatives
- Fix missing newlines
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

POSTGRESQL_SETUP_CELL = '''# ============================================================================
# POSTGRESQL SETUP FOR GOOGLE COLAB
# ============================================================================

import subprocess
import time

print("="*80)
print("POSTGRESQL SETUP FOR GOOGLE COLAB")
print("="*80)

if not IS_COLAB:
    raise RuntimeError("This notebook requires Google Colab")

# Method 1: Use magic commands (preferred for Colab)
print("\\nMethod 1: Using magic commands...")
print("Run these commands in separate cells if needed:")
print("  !apt-get update")
print("  !apt-get install -y postgresql postgresql-contrib")
print("  !service postgresql start")

# Method 2: Use subprocess (works in Colab)
print("\\nMethod 2: Using subprocess...")
try:
    # Update package list
    print("   Updating package list...")
    subprocess.run(['apt-get', 'update', '-qq'], check=True, capture_output=True)
    print("   ✅ Package list updated")
    
    # Install PostgreSQL
    print("   Installing PostgreSQL...")
    subprocess.run(['apt-get', 'install', '-y', '-qq', 'postgresql', 'postgresql-contrib'], 
                   check=True, capture_output=True)
    print("   ✅ PostgreSQL installed")
    
    # Start PostgreSQL service
    print("   Starting PostgreSQL service...")
    subprocess.run(['service', 'postgresql', 'start'], check=True, capture_output=True)
    print("   ✅ PostgreSQL service started")
    
    # Wait for PostgreSQL to be ready
    print("   Waiting for PostgreSQL to be ready...")
    max_attempts = 10
    for i in range(max_attempts):
        try:
            result = subprocess.run(['pg_isready'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✅ PostgreSQL is ready!")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("   ⚠️  PostgreSQL might not be ready yet")
        print("   Try: !service postgresql restart")
    
except subprocess.CalledProcessError as e:
    print(f"   ❌ Error: {e}")
    print("   Try running manually:")
    print("   !apt-get update")
    print("   !apt-get install -y postgresql postgresql-contrib")
    print("   !service postgresql start")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

print("\\n" + "="*80)
print("POSTGRESQL SETUP COMPLETE")
print("="*80)
'''

def fix_postgresql_setup_cell(notebook: dict) -> bool:
    """Fix PostgreSQL setup cell."""
    modified = False
    
    # Find PostgreSQL setup cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            
            # Check if this is PostgreSQL setup cell
            if 'POSTGRESQL SETUP' in source.upper() or ('postgresql' in source.lower() and 'install' in source.lower()):
                # Check if it needs fixing (missing newlines or incomplete)
                if source.count('\n') < 10 or 'subprocess.run' in source and 'apt-get' in source:
                    # Replace with properly formatted version
                    cell['source'] = POSTGRESQL_SETUP_CELL.split('\n')
                    modified = True
                    print(f"   ✅ Fixed PostgreSQL setup cell (cell {i+1})")
                    break
    
    return modified

def fix_notebook(notebook_path: Path) -> bool:
    """Fix notebook."""
    print(f"\\nFixing PostgreSQL setup: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    
    if fix_postgresql_setup_cell(notebook):
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
        return True
    
    print(f"   ✅ No changes needed")
    return False

def main():
    """Main execution."""
    print("="*80)
    print("FIXING POSTGRESQL SETUP FOR COLAB")
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
    print(f"Fixed notebooks: {fixed_count}")
    print("✅ POSTGRESQL SETUP FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
