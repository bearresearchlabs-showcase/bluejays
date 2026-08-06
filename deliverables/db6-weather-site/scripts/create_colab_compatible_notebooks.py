#!/usr/bin/env python3
"""
Create Colab-compatible notebooks with proper error handling and SQLite fallback
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

def fix_colab_detection_cell(cell_source: List[str]) -> List[str]:
    """Fix Colab detection in environment cell."""
    source_str = ''.join(cell_source)
    
    # Check if already has improved Colab detection
    if "import google.colab" in source_str or "COLAB_GPU" in source_str:
        return cell_source
    
    # Find the Colab detection section and improve it
    new_source = []
    i = 0
    while i < len(cell_source):
        line = cell_source[i]
        
        # Replace weak Colab detection with improved version
        if "elif 'google.colab' in str(sys.modules.keys()):" in line:
            new_source.append("# Improved Colab detection\n")
            new_source.append("try:\n")
            new_source.append("    import google.colab\n")
            new_source.append("    ENV_TYPE = 'colab'\n")
            new_source.append("    ENV_DETAILS['platform'] = 'google_colab'\n")
            new_source.append("    ENV_DETAILS['colab_module'] = True\n")
            new_source.append("    print(\"✅ Detected: Google Colab (via google.colab module)\")\n")
            new_source.append("except ImportError:\n")
            # Skip old detection lines
            while i < len(cell_source) and "elif os.path.exists('/content'):" not in cell_source[i]:
                i += 1
            if i < len(cell_source):
                new_source.append("    # Check for Colab by /content directory AND COLAB_GPU environment\n")
                new_source.append("    if os.path.exists('/content') and os.environ.get('COLAB_GPU'):\n")
                new_source.append("        ENV_TYPE = 'colab'\n")
                new_source.append("        ENV_DETAILS['platform'] = 'google_colab'\n")
                new_source.append("        ENV_DETAILS['content_dir'] = True\n")
                new_source.append("        print(\"✅ Detected: Google Colab (by /content + COLAB_GPU)\")\n")
                new_source.append("    elif os.path.exists('/content') and 'COLAB' in str(os.environ):\n")
                new_source.append("        ENV_TYPE = 'colab'\n")
                new_source.append("        ENV_DETAILS['platform'] = 'google_colab'\n")
                new_source.append("        ENV_DETAILS['content_dir'] = True\n")
                new_source.append("        print(\"✅ Detected: Google Colab (by /content + COLAB env)\")\n")
                new_source.append("    elif os.path.exists('/content'):\n")
                new_source.append("        # Check if it looks like Colab\n")
                new_source.append("        if (Path('/content').exists() and \n")
                new_source.append("            (Path('/content/sample_data').exists() or \n")
                new_source.append("             Path('/content/drive').exists())):\n")
                new_source.append("            ENV_TYPE = 'colab'\n")
                new_source.append("            ENV_DETAILS['platform'] = 'google_colab'\n")
                new_source.append("            ENV_DETAILS['content_dir'] = True\n")
                new_source.append("            print(\"✅ Detected: Google Colab (by /content structure)\")\n")
                new_source.append("        else:\n")
                new_source.append("            ENV_TYPE = 'colab'\n")
                new_source.append("            ENV_DETAILS['platform'] = 'google_colab'\n")
                new_source.append("            ENV_DETAILS['content_dir'] = True\n")
                new_source.append("            print(\"⚠️  Detected: Possible Google Colab (by /content)\")\n")
                i += 1
        elif "find_base_directory" in line and "/content" not in ''.join(cell_source[max(0, i-5):i+10]):
            # Enhance find_base_directory with Colab paths
            new_source.append(line)
            # Look for the start_paths list
            if "start_paths = [" in line:
                i += 1
                new_source.append(cell_source[i])  # [
                i += 1
                # Add Colab paths before other paths
                new_source.append("        Path('/content'),  # Colab default\n")
                new_source.append("        Path('/content/drive/MyDrive'),  # Google Drive\n")
                new_source.append("        Path('/content/drive/MyDrive/db'),  # db in Drive\n")
                new_source.append("        Path('/content/db'),  # db in content\n")
                # Skip existing paths until ]
                while i < len(cell_source) and "]" not in cell_source[i]:
                    if "Path('/content" not in cell_source[i]:
                        new_source.append(cell_source[i])
                    i += 1
                new_source.append(cell_source[i])  # ]
                i += 1
                continue
        else:
            new_source.append(line)
        i += 1
    
    return new_source if new_source != cell_source else cell_source

def add_sqlite_fallback(cell_source: List[str], db_name: str) -> List[str]:
    """Add SQLite fallback to database connection cell."""
    source_str = ''.join(cell_source)
    
    # Check if already has SQLite fallback
    if 'sqlite3' in source_str and 'sqlite' in source_str.lower():
        return cell_source
    
    # Add SQLite import and fallback logic
    new_source = cell_source.copy()
    
    # Add import at the top if not present
    if 'import sqlite3' not in source_str:
        # Find import section
        import_idx = -1
        for i, line in enumerate(new_source):
            if 'import psycopg2' in line:
                import_idx = i + 1
                break
        if import_idx > 0:
            new_source.insert(import_idx, 'import sqlite3\n')
    
    # Add SQLite fallback function before connection creation
    sqlite_code = f'''
# SQLite fallback for Colab (PostgreSQL not available)
def get_database_connection():
    """Get database connection with SQLite fallback for Colab."""
    if ENV_TYPE == 'colab':
        # Colab: Use SQLite
        print("⚠️  Google Colab detected: Using SQLite fallback")
        print("   PostgreSQL is not available in Colab by default")
        print("   Note: Some PostgreSQL-specific queries may need adaptation")
        
        db_file = BASE_DIR / f"{db_name}.db"
        conn = sqlite3.connect(str(db_file))
        print(f"✅ Connected to SQLite: {{db_file}}")
        return conn, 'sqlite'
    else:
        # Docker/Local: Use PostgreSQL
        try:
            conn = psycopg2.connect(
                host=os.environ.get('PG_HOST', 'localhost'),
                port=int(os.environ.get('PG_PORT', 5432)),
                user=os.environ.get('PG_USER', 'postgres'),
                password=os.environ.get('PG_PASSWORD', 'postgres'),
                database=DB_NAME
            )
            print(f"✅ Connected to PostgreSQL")
            return conn, 'postgresql'
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {{e}}")
            if ENV_TYPE == 'colab':
                # Fallback to SQLite
                db_file = BASE_DIR / f"{db_name}.db"
                conn = sqlite3.connect(str(db_file))
                print(f"✅ Using SQLite fallback: {{db_file}}")
                return conn, 'sqlite'
            raise

# Create connection with fallback
conn, db_type = get_database_connection()
print(f"\\nDatabase type: {{db_type}}")
'''
    
    # Find where connection is created and replace/add
    conn_idx = -1
    for i, line in enumerate(new_source):
        if 'conn = psycopg2.connect' in line or 'conn = create_connection()' in line:
            conn_idx = i
            break
    
    if conn_idx > 0:
        # Replace connection creation
        # Find end of connection block
        end_idx = conn_idx + 1
        while end_idx < len(new_source) and not new_source[end_idx].strip().startswith('#') and 'print' not in new_source[end_idx]:
            end_idx += 1
        # Replace with SQLite fallback version
        new_source[conn_idx:end_idx] = sqlite_code.strip().split('\n')
    else:
        # Append at end
        new_source.extend(sqlite_code.strip().split('\n'))
    
    return new_source

def add_colab_setup_cell(notebook: Dict) -> Dict:
    """Add Colab-specific setup cell after environment detection."""
    setup_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Colab Setup (Run this first if using Google Colab)\n",
            "\n",
            "If you're running this notebook in Google Colab:\n",
            "1. **Mount Google Drive** (if your database files are in Drive)\n",
            "2. **Upload database files** to `/content/db` or your Drive folder\n",
            "3. **Note**: PostgreSQL is not available in Colab - SQLite will be used automatically"
        ]
    }
    
    code_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================================\n",
            "# GOOGLE COLAB SETUP\n",
            "# ============================================================================\n",
            "\n",
            "if ENV_TYPE == 'colab':\n",
            "    print(\"=\"*80)\n",
            "    print(\"GOOGLE COLAB SETUP\")\n",
            "    print(\"=\"*80)\n",
            "    \n",
            "    # Mount Google Drive if not already mounted\n",
            "    drive_path = Path('/content/drive/MyDrive')\n",
            "    if not drive_path.exists():\n",
            "        print(\"⚠️  Google Drive not mounted.\")\n",
            "        print(\"   Run this command to mount:\")\n",
            "        print(\"   from google.colab import drive\")\n",
            "        print(\"   drive.mount('/content/drive')\")\n",
            "        try:\n",
            "            from google.colab import drive\n",
            "            drive.mount('/content/drive')\n",
            "            print(\"✅ Google Drive mounted\")\n",
            "        except Exception as e:\n",
            "            print(f\"⚠️  Could not auto-mount Drive: {e}\")\n",
            "            print(\"   Please mount manually using the command above\")\n",
            "    else:\n",
            "        print(\"✅ Google Drive is already mounted\")\n",
            "    \n",
            "    # Check for database files\n",
            "    print(\"\\nChecking for database files...\")\n",
            "    \n",
            "    # Check in /content/db\n",
            "    content_db = Path('/content/db')\n",
            "    if content_db.exists():\n",
            "        print(f\"✅ Found: {content_db}\")\n",
            "    else:\n",
            "        print(f\"⚠️  Not found: {content_db}\")\n",
            "        print(\"   Upload your database folder to /content/db\")\n",
            "    \n",
            "    # Check in Drive\n",
            "    drive_db = drive_path / 'db'\n",
            "    if drive_db.exists():\n",
            "        print(f\"✅ Found in Drive: {drive_db}\")\n",
            "    else:\n",
            "        print(f\"⚠️  Not found in Drive: {drive_db}\")\n",
            "        print(\"   Upload your database folder to Google Drive/db\")\n",
            "    \n",
            "    print(\"\\n\" + \"=\"*80)\n",
            "    print(\"NOTE: This notebook will use SQLite instead of PostgreSQL\")\n",
            "    print(\"Some PostgreSQL-specific features may not work\")\n",
            "    print(\"=\"*80)\n",
            "else:\n",
            "    print(\"Not running in Colab - skipping Colab setup\")"
        ]
    }
    
    # Find environment detection cell index
    env_idx = -1
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'ENVIRONMENT DETECTION' in source and 'ENV_TYPE' in source:
                env_idx = i
                break
    
    if env_idx >= 0:
        # Insert after environment detection
        notebook['cells'].insert(env_idx + 1, setup_cell)
        notebook['cells'].insert(env_idx + 2, code_cell)
        return notebook
    
    return notebook

def fix_notebook_for_colab(notebook_path: Path) -> bool:
    """Fix notebook for Colab compatibility."""
    print(f"\\nFixing: {notebook_path.name}")
    
    try:
        notebook = read_notebook(notebook_path)
    except Exception as e:
        print(f"   ❌ Error reading: {e}")
        return False
    
    db_name = notebook_path.stem
    updated = False
    
    # Fix each cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            
            # Fix environment detection
            if 'ENVIRONMENT DETECTION' in ''.join(source) and 'ENV_TYPE' in ''.join(source):
                fixed_source = fix_colab_detection_cell(source)
                if fixed_source != source:
                    cell['source'] = fixed_source
                    updated = True
                    print(f"   ✅ Fixed Colab detection (cell {i+1})")
            
            # Add SQLite fallback
            if ('DATABASE CONNECTION' in ''.join(source) or 
                'DATABASE CONFIGURATION' in ''.join(source) or
                'psycopg2.connect' in ''.join(source)):
                fixed_source = add_sqlite_fallback(source, db_name)
                if fixed_source != source:
                    cell['source'] = fixed_source
                    updated = True
                    print(f"   ✅ Added SQLite fallback (cell {i+1})")
    
    # Add Colab setup cell
    notebook = add_colab_setup_cell(notebook)
    updated = True
    print(f"   ✅ Added Colab setup instructions")
    
    if updated:
        # Backup
        backup_path = notebook_path.with_suffix('.ipynb.colab_fix_backup')
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
    print("FIXING NOTEBOOKS FOR GOOGLE COLAB COMPATIBILITY")
    print("="*80)
    
    updated_count = 0
    
    # Fix notebooks in db-* directories
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if fix_notebook_for_colab(notebook_path):
                updated_count += 1
    
    # Fix notebooks in client/db
    client_db_dir = BASE_DIR / 'client' / 'db'
    if client_db_dir.exists():
        for db_name in DATABASES:
            for deliverable_dir in client_db_dir.glob(f"{db_name}/*"):
                if deliverable_dir.is_dir():
                    notebook_path = deliverable_dir / f"{db_name}.ipynb"
                    if notebook_path.exists():
                        if fix_notebook_for_colab(notebook_path):
                            updated_count += 1
    
    print("\\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Fixed notebooks: {updated_count}")
    print("\\n✅ Colab compatibility fixes applied!")
    print("\\nNext steps for Colab:")
    print("1. Upload notebooks to Google Colab")
    print("2. Mount Google Drive: from google.colab import drive; drive.mount('/content/drive')")
    print("3. Upload database files to /content/db or Google Drive")
    print("4. Run notebooks - SQLite will be used automatically if PostgreSQL unavailable")

if __name__ == '__main__':
    main()
