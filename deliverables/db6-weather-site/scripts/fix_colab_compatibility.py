#!/usr/bin/env python3
"""
Fix Jupyter notebooks for Google Colab compatibility
- Improved Colab detection
- SQLite fallback for PostgreSQL
- Better file path detection
- Colab-specific package installation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Detect base directory
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

# Improved Colab detection code
COLAB_DETECTION_CODE = '''# ============================================================================
# IMPROVED GOOGLE COLAB DETECTION
# ============================================================================

import sys
import os
import platform
import subprocess
import json
from pathlib import Path

print("="*80)
print("ENVIRONMENT DETECTION (Colab-Optimized)")
print("="*80)

# Detect environment type
ENV_TYPE = None
ENV_DETAILS = {}

# Check for Google Colab FIRST (most specific)
try:
    import google.colab
    ENV_TYPE = 'colab'
    ENV_DETAILS['platform'] = 'google_colab'
    ENV_DETAILS['colab_module'] = True
    print("✅ Detected: Google Colab (via google.colab module)")
except ImportError:
    # Check for Colab by /content directory AND COLAB_GPU environment
    if os.path.exists('/content') and os.environ.get('COLAB_GPU'):
        ENV_TYPE = 'colab'
        ENV_DETAILS['platform'] = 'google_colab'
        ENV_DETAILS['content_dir'] = True
        print("✅ Detected: Google Colab (by /content + COLAB_GPU)")
    elif os.path.exists('/content') and 'COLAB' in str(os.environ):
        ENV_TYPE = 'colab'
        ENV_DETAILS['platform'] = 'google_colab'
        ENV_DETAILS['content_dir'] = True
        print("✅ Detected: Google Colab (by /content + COLAB env)")
    elif os.path.exists('/content'):
        # Check if it looks like Colab (has sample_data, etc.)
        if (Path('/content').exists() and 
            (Path('/content/sample_data').exists() or 
             Path('/content/drive').exists())):
            ENV_TYPE = 'colab'
            ENV_DETAILS['platform'] = 'google_colab'
            ENV_DETAILS['content_dir'] = True
            print("✅ Detected: Google Colab (by /content structure)")
        else:
            # Might be Colab but not mounted yet
            ENV_TYPE = 'colab'
            ENV_DETAILS['platform'] = 'google_colab'
            ENV_DETAILS['content_dir'] = True
            print("⚠️  Detected: Possible Google Colab (by /content)")
    # Check for Docker
    elif os.path.exists('/.dockerenv'):
        ENV_TYPE = 'docker'
        ENV_DETAILS['container'] = 'docker'
        if os.path.exists('/workspace'):
            ENV_DETAILS['workspace'] = '/workspace'
        print("✅ Detected: Docker container")
    # Local environment
    else:
        ENV_TYPE = 'local'
        ENV_DETAILS['platform'] = platform.system().lower()
        print("✅ Detected: Local environment")

# Detect base directories recursively (Colab-optimized)
def find_base_directory():
    """Find base database directory recursively (Colab-optimized)."""
    start_paths = []
    
    if ENV_TYPE == 'colab':
        # Colab-specific paths (most likely first)
        start_paths = [
            Path('/content'),  # Default Colab directory
            Path('/content/drive/MyDrive'),  # Google Drive mount
            Path('/content/drive/MyDrive/db'),  # Direct db folder in Drive
            Path('/content/db'),  # Direct db folder in content
            Path.cwd(),  # Current working directory
        ]
    elif ENV_TYPE == 'docker':
        start_paths = [
            Path('/workspace'),
            Path('/workspace/client/db'),
            Path('/workspace/db'),
            Path.cwd(),
        ]
    else:  # local
        start_paths = [
            Path.cwd(),
            Path.home() / 'Documents' / 'AQ' / 'db',
            Path('/workspace/db'),
            Path('/workspace/client/db').parent,
        ]
    
    for start_path in start_paths:
        if not start_path.exists():
            continue
        
        # Look for db-6 directory (or any db-*)
        try:
            for db_dir in start_path.rglob('db-6'):
                if db_dir.is_dir() and (db_dir / 'queries').exists():
                    base = db_dir.parent
                    print(f"   Found base directory: {base}")
                    return base
        except (PermissionError, OSError):
            continue
        
        # Look for client/db structure
        try:
            client_db = start_path / 'client' / 'db'
            if client_db.exists() and (client_db / 'db-6').exists():
                base = start_path
                print(f"   Found base directory: {base}")
                return base
        except (PermissionError, OSError):
            continue
    
    # Fallback: use current directory
    print(f"   Using current directory as base: {Path.cwd()}")
    return Path.cwd()

BASE_DIR = find_base_directory()
ENV_DETAILS['base_dir'] = str(BASE_DIR)

print(f"\\nEnvironment Type: {ENV_TYPE}")
print(f"Base Directory: {BASE_DIR}")
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Platform: {platform.platform()}")

# Colab-specific setup
if ENV_TYPE == 'colab':
    print("\\n" + "="*80)
    print("GOOGLE COLAB SETUP")
    print("="*80)
    
    # Mount Google Drive if not already mounted
    drive_path = Path('/content/drive/MyDrive')
    if not drive_path.exists():
        print("⚠️  Google Drive not mounted. Run this cell to mount:")
        print("   from google.colab import drive")
        print("   drive.mount('/content/drive')")
    else:
        print("✅ Google Drive is mounted")
    
    # Check if database files are in Drive
    db_in_drive = drive_path / 'db'
    if db_in_drive.exists():
        print(f"✅ Found database folder in Drive: {db_in_drive}")
    else:
        print("⚠️  Database folder not found in Drive")
        print("   Upload your database folder to Google Drive")
        print("   Or upload directly to /content/db")

print("\\n" + "="*80)
print("ENVIRONMENT DETECTION COMPLETE")
print("="*80)
'''

# SQLite fallback code for Colab (use {{ to escape braces)
def get_sqlite_fallback_code(db_name: str) -> str:
    """Get SQLite fallback code with proper db_name substitution."""
    return f'''# ============================================================================
# DATABASE CONNECTION (PostgreSQL with SQLite Fallback for Colab)
# ============================================================================

import psycopg2
import sqlite3
from pathlib import Path

# Database name
DB_NAME = "{db_name}"

def get_database_config():
    """Get database configuration based on environment."""
    if ENV_TYPE == 'colab':
        # Colab: Use SQLite fallback (PostgreSQL not available)
        print("⚠️  Google Colab detected: Using SQLite fallback")
        print("   PostgreSQL is not available in Colab by default")
        print("   Using SQLite for query testing")
        
        # Create SQLite database file
        db_file = BASE_DIR / f"{db_name}.db"
        return {{
            'type': 'sqlite',
            'connection': sqlite3.connect(str(db_file)),
            'file': db_file
        }}
    elif ENV_TYPE == 'docker':
        # Docker: Use PostgreSQL
        return {{
            'type': 'postgresql',
            'host': os.environ.get('PG_HOST', 'localhost'),
            'port': int(os.environ.get('PG_PORT', 5432)),
            'user': os.environ.get('PG_USER', 'postgres'),
            'password': os.environ.get('PG_PASSWORD', 'postgres'),
            'database': DB_NAME
        }}
    else:
        # Local: Use PostgreSQL
        return {{
            'type': 'postgresql',
            'host': os.environ.get('PG_HOST', 'localhost'),
            'port': int(os.environ.get('PG_PORT', 5432)),
            'user': os.environ.get('PG_USER', 'postgres'),
            'password': os.environ.get('PG_PASSWORD', ''),
            'database': DB_NAME
        }}

def create_connection():
    """Create database connection."""
    config = get_database_config()
    
    if config['type'] == 'sqlite':
        print(f"✅ Connecting to SQLite: {{config['file']}}")
        return config['connection']
    else:
        try:
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
            print(f"✅ Connected to PostgreSQL: {{config['host']}}:{{config['port']}}/{{config['database']}}")
            return conn
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {{e}}")
            if ENV_TYPE == 'colab':
                print("   Using SQLite fallback...")
                db_file = BASE_DIR / f"{{DB_NAME}}.db"
                return sqlite3.connect(str(db_file))
            raise

# Create connection
conn = create_connection()
print(f"\\nDatabase connection type: {{get_database_config()['type']}}")
'''

# Improved file finding for Colab
FILE_FINDING_CODE = '''def find_file_recursively(start_dir: Path, filename: str) -> Path:
    """Find a file or directory recursively from start directory (Colab-optimized)."""
    if not start_dir.exists():
        return None
    
    try:
        # Direct check first
        direct_path = start_dir / filename
        if direct_path.exists():
            return direct_path
        
        # Recursive search
        for path in start_dir.rglob(filename):
            if path.is_file() or path.is_dir():
                return path
    except (PermissionError, OSError) as e:
        print(f"   ⚠️  Permission error searching {start_dir}: {e}")
        return None
    
    return None

def detect_database_directory(db_name: str) -> Path:
    """Detect database directory recursively (Colab-optimized)."""
    search_paths = []
    
    if ENV_TYPE == 'colab':
        # Colab-specific search paths
        search_paths = [
            Path('/content'),
            Path('/content/drive/MyDrive'),
            Path('/content/drive/MyDrive/db'),
            Path('/content/db'),
            BASE_DIR,
            Path.cwd(),
        ]
    elif ENV_TYPE == 'docker':
        search_paths = [
            Path('/workspace/client/db'),
            Path('/workspace/db'),
            Path('/workspace'),
            BASE_DIR,
        ]
    else:  # local
        search_paths = [
            BASE_DIR,
            Path.cwd(),
            Path.home() / 'Documents' / 'AQ' / 'db',
        ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Try direct path
        db_dir = search_path / db_name
        if db_dir.exists() and (db_dir / 'queries').exists():
            return db_dir
        
        # Try recursive search
        found = find_file_recursively(search_path, db_name)
        if found and found.is_dir() and (found / 'queries').exists():
            return found
    
    # Fallback: construct from BASE_DIR
    return BASE_DIR / db_name

DB_DIR = detect_database_directory(DB_NAME)
print(f"\\nDatabase Directory: {DB_DIR}")
'''

# Colab package installation improvements
COLAB_PACKAGE_INSTALL_CODE = '''# Colab-specific: Use !pip magic command for better compatibility
if ENV_TYPE == 'colab':
    print("\\n" + "="*80)
    print("COLAB PACKAGE INSTALLATION")
    print("="*80)
    print("Using Colab-optimized installation methods...")
    
    # Colab has some packages pre-installed
    colab_preinstalled = ['pandas', 'numpy', 'matplotlib']
    
    for package_spec in required_packages:
        package_name = package_spec.split('>=')[0]
        import_name = package_import_map.get(package_name, package_name.replace('-', '_'))
        
        # Check if pre-installed
        if package_name in colab_preinstalled:
            try:
                __import__(import_name)
                print(f"✅ {package_name}: Pre-installed in Colab")
                continue
            except ImportError:
                pass
        
        # Install using !pip magic (works better in Colab)
        print(f"Installing {package_name}...")
        try:
            get_ipython().run_line_magic('pip', f'install {package_spec} --quiet')
            __import__(import_name)
            print(f"   ✅ Installed {package_name}")
        except Exception as e:
            print(f"   ⚠️  {package_name} installation issue: {e}")
            # Fallback to subprocess
            try:
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', package_spec, '--quiet'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=300
                )
                __import__(import_name)
                print(f"   ✅ Installed {package_name} (fallback)")
            except:
                print(f"   ❌ Failed to install {package_name}")
'''

def update_notebook_for_colab(notebook_path: Path) -> bool:
    """Update notebook for Colab compatibility."""
    print(f"\\nUpdating: {notebook_path.name}")
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
    except Exception as e:
        print(f"   ❌ Error reading notebook: {e}")
        return False
    
    updated = False
    
    # Find and update environment detection cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            
            # Update environment detection
            if 'ENVIRONMENT DETECTION' in source and 'ENV_TYPE' in source:
                # Replace with improved Colab detection
                cell['source'] = COLAB_DETECTION_CODE.split('\\n')
                updated = True
                print(f"   ✅ Updated environment detection (cell {i+1})")
            
            # Update database connection to include SQLite fallback
            elif 'DATABASE CONFIGURATION' in source or 'DATABASE CONNECTION' in source:
                if 'sqlite' not in source.lower():
                    # Inject SQLite fallback code
                    db_name = notebook_path.stem.replace('.ipynb', '')
                    sqlite_code = get_sqlite_fallback_code(db_name)
                    # Append SQLite code to cell
                    existing_source = ''.join(cell.get('source', []))
                    cell['source'] = (existing_source + '\\n\\n' + sqlite_code).split('\\n')
                    updated = True
                    print(f"   ✅ Added SQLite fallback (cell {i+1})")
            
            # Update file finding
            elif 'find_file_recursively' in source and ENV_TYPE == 'colab':
                # Update with Colab-optimized paths
                cell['source'] = FILE_FINDING_CODE.split('\\n')
                updated = True
                print(f"   ✅ Updated file finding (cell {i+1})")
            
            # Update package installation for Colab
            elif 'MULTI-METHOD PACKAGE INSTALLATION' in source and ENV_TYPE == 'colab':
                # Add Colab-specific installation
                existing_source = ''.join(cell.get('source', []))
                cell['source'] = (existing_source + '\\n\\n' + COLAB_PACKAGE_INSTALL_CODE).split('\\n')
                updated = True
                print(f"   ✅ Added Colab package installation (cell {i+1})")
    
    if updated:
        # Create backup
        backup_path = notebook_path.with_suffix('.ipynb.colab_backup')
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
        except:
            pass
        
        # Save updated notebook
        try:
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=1, ensure_ascii=False)
            print(f"   ✅ Saved updated notebook")
            return True
        except Exception as e:
            print(f"   ❌ Error saving notebook: {e}")
            return False
    
    return False

def main():
    """Main execution."""
    print("="*80)
    print("FIXING NOTEBOOKS FOR GOOGLE COLAB COMPATIBILITY")
    print("="*80)
    
    updated_count = 0
    
    # Update notebooks in db-* directories
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if update_notebook_for_colab(notebook_path):
                updated_count += 1
    
    # Update notebooks in client/db
    client_db_dir = BASE_DIR / 'client' / 'db'
    if client_db_dir.exists():
        for db_name in DATABASES:
            # Check deliverable folders
            for deliverable_dir in client_db_dir.glob(f"{db_name}/*"):
                if deliverable_dir.is_dir():
                    notebook_path = deliverable_dir / f"{db_name}.ipynb"
                    if notebook_path.exists():
                        if update_notebook_for_colab(notebook_path):
                            updated_count += 1
    
    print("\\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Updated notebooks: {updated_count}")
    print("\\n✅ Colab compatibility fixes applied!")
    print("\\nNext steps:")
    print("1. Upload notebooks to Google Colab")
    print("2. Mount Google Drive if using Drive storage")
    print("3. Upload database files to /content/db or Google Drive")
    print("4. Run notebooks - they will use SQLite if PostgreSQL unavailable")

if __name__ == '__main__':
    main()
