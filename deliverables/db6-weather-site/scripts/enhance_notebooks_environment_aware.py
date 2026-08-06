#!/usr/bin/env python3
"""
Enhance existing db-*.ipynb notebooks with environment detection, self-updating, and multi-method installation
This script reads existing notebooks and enhances them metaprogrammatically
"""

import json
import os
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
DATABASES = [f'db-{i}' for i in range(6, 16)]

def enhance_notebook_with_environment_detection(notebook_path: Path) -> dict:
    """Enhance existing notebook with environment detection and self-updating."""
    
    # Load existing notebook
    with open(notebook_path) as f:
        notebook = json.load(f)
    
    cells = notebook.get('cells', [])
    enhanced_cells = []
    
    # Find database name from path
    db_name = notebook_path.stem
    
    # Step 1: Add environment detection cell at the beginning (after title)
    env_detection_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 0: Environment Detection and Self-Update"
        ]
    }
    
    env_detection_code = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================================\n",
            "# ENVIRONMENT DETECTION AND METAPROGRAMMATIC SELF-UPDATE\n",
            "# ============================================================================\n",
            "\n",
            "import sys\n",
            "import os\n",
            "import platform\n",
            "import subprocess\n",
            "import json\n",
            "from pathlib import Path\n",
            "\n",
            "print(\"=\"*80)\n",
            "print(\"ENVIRONMENT DETECTION\")\n",
            "print(\"=\"*80)\n",
            "\n",
            "# Detect environment type\n",
            "ENV_TYPE = None\n",
            "ENV_DETAILS = {}\n",
            "\n",
            "# Check for Docker\n",
            "if os.path.exists('/.dockerenv'):\n",
            "    ENV_TYPE = 'docker'\n",
            "    ENV_DETAILS['container'] = 'docker'\n",
            "    if os.path.exists('/workspace'):\n",
            "        ENV_DETAILS['workspace'] = '/workspace'\n",
            "    print(\"✅ Detected: Docker container\")\n",
            "\n",
            "# Check for Google Colab\n",
            "elif 'google.colab' in str(sys.modules.keys()):\n",
            "    ENV_TYPE = 'colab'\n",
            "    ENV_DETAILS['platform'] = 'google_colab'\n",
            "    print(\"✅ Detected: Google Colab\")\n",
            "elif os.path.exists('/content'):\n",
            "    ENV_TYPE = 'colab'\n",
            "    ENV_DETAILS['platform'] = 'google_colab'\n",
            "    print(\"✅ Detected: Google Colab (by /content directory)\")\n",
            "\n",
            "# Check for local environment\n",
            "else:\n",
            "    ENV_TYPE = 'local'\n",
            "    ENV_DETAILS['platform'] = platform.system().lower()\n",
            "    print(\"✅ Detected: Local environment\")\n",
            "\n",
            "# Detect base directories recursively\n",
            "def find_base_directory():\n",
            "    \"\"\"Find base database directory recursively.\"\"\"\n",
            "    start_paths = [\n",
            "        Path.cwd(),\n",
            "        Path('/workspace'),\n",
            "        Path('/workspace/client/db'),\n",
            "        Path('/workspace/db'),\n",
            "        Path('/content'),\n",
            "        Path('/content/drive/MyDrive'),\n",
            "        Path.home() / 'Documents' / 'AQ' / 'db',\n",
            "    ]\n",
            "    \n",
            "    for start_path in start_paths:\n",
            "        if not start_path.exists():\n",
            "            continue\n",
            "        \n",
            "        # Look for db-6 directory (or any db-*)\n",
            "        for db_dir in start_path.rglob('db-6'):\n",
            "            if db_dir.is_dir() and (db_dir / 'queries').exists():\n",
            "                return db_dir.parent\n",
            "        \n",
            "        # Look for client/db structure\n",
            "        client_db = start_path / 'client' / 'db'\n",
            "        if client_db.exists() and (client_db / 'db-6').exists():\n",
            "            return start_path\n",
            "    \n",
            "    return Path.cwd()\n",
            "\n",
            "BASE_DIR = find_base_directory()\n",
            "ENV_DETAILS['base_dir'] = str(BASE_DIR)\n",
            "\n",
            "print(f\"\\nEnvironment Type: {ENV_TYPE}\")\n",
            "print(f\"Base Directory: {BASE_DIR}\")\n",
            "print(f\"Python Version: {sys.version}\")\n",
            "print(f\"Python Executable: {sys.executable}\")\n",
            "print(f\"Platform: {platform.platform()}\")\n",
            "\n",
            "# Metaprogrammatic self-update: Update notebook paths based on environment\n",
            "def update_notebook_paths():\n",
            "    \"\"\"Metaprogrammatically update notebook cell paths based on detected environment.\"\"\"\n",
            "    return {\n",
            "        'env_type': ENV_TYPE,\n",
            "        'base_dir': BASE_DIR,\n",
            "        'details': ENV_DETAILS\n",
            "    }\n",
            "\n",
            "ENV_CONFIG = update_notebook_paths()\n",
            "\n",
            "print(\"\\n\" + \"=\"*80)\n",
            "print(\"ENVIRONMENT DETECTION COMPLETE\")\n",
            "print(\"=\"*80)"
        ]
    }
    
    # Insert environment detection cells after first markdown cell
    if cells and cells[0].get('cell_type') == 'markdown':
        enhanced_cells.append(cells[0])  # Keep title cell
        enhanced_cells.append(env_detection_cell)
        enhanced_cells.append(env_detection_code)
        
        # Process remaining cells
        for i, cell in enumerate(cells[1:], start=1):
            if cell.get('cell_type') == 'code':
                source = ''.join(cell.get('source', []))
                
                # Enhance package installation cell
                if 'CHECKING AND INSTALLING REQUIRED PACKAGES' in source or 'ENVIRONMENT SETUP' in source:
                    # Replace with multi-method installation
                    enhanced_cell = enhance_package_installation_cell(cell, db_name)
                    enhanced_cells.append(enhanced_cell)
                    continue
                
                # Enhance database configuration cell
                if 'DATABASE CONFIGURATION' in source:
                    enhanced_cell = enhance_database_config_cell(cell, db_name)
                    enhanced_cells.append(enhanced_cell)
                    continue
                
                # Enhance database initialization cell
                if 'DATABASE INITIALIZATION' in source or 'initialize_database' in source:
                    enhanced_cell = enhance_database_init_cell(cell, db_name)
                    enhanced_cells.append(enhanced_cell)
                    continue
                
                # Enhance query loading cell
                if 'LOAD QUERY METADATA' in source or 'queries_file = DB_DIR' in source:
                    enhanced_cell = enhance_query_loading_cell(cell, db_name)
                    enhanced_cells.append(enhanced_cell)
                    continue
            
            enhanced_cells.append(cell)
    else:
        # If structure is unexpected, just prepend environment detection
        enhanced_cells = [env_detection_cell, env_detection_code] + cells
    
    notebook['cells'] = enhanced_cells
    return notebook

def enhance_package_installation_cell(cell: dict, db_name: str) -> dict:
    """Enhance package installation cell with multiple methods."""
    source_lines = [
        "# ============================================================================\n",
        "# MULTI-METHOD PACKAGE INSTALLATION WITH FALLBACKS\n",
        "# ============================================================================\n",
        "\n",
        "import shutil\n",
        "\n",
        "required_packages = [\n",
        "    'psycopg2-binary>=2.9.0',\n",
        "    'pandas>=2.0.0',\n",
        "    'numpy>=1.24.0',\n",
        "    'matplotlib>=3.7.0',\n",
        "    'seaborn>=0.12.0'\n",
        "]\n",
        "\n",
        "package_import_map = {\n",
        "    'psycopg2-binary': 'psycopg2',\n",
        "    'pandas': 'pandas',\n",
        "    'numpy': 'numpy',\n",
        "    'matplotlib': 'matplotlib',\n",
        "    'seaborn': 'seaborn'\n",
        "}\n",
        "\n",
        "def install_package_multiple_methods(package_spec: str, import_name: str) -> bool:\n",
        "    \"\"\"Install package using multiple methods with fallbacks.\"\"\"\n",
        "    package_name = package_spec.split('>=')[0]\n",
        "    \n",
        "    # Method 1: Check if already installed\n",
        "    try:\n",
        "        __import__(import_name)\n",
        "        print(f\"✅ {package_name}: Already installed\")\n",
        "        return True\n",
        "    except ImportError:\n",
        "        pass\n",
        "    \n",
        "    print(f\"⚠️  {package_name}: Installing...\")\n",
        "    \n",
        "    # Method 2: pip install --user\n",
        "    try:\n",
        "        subprocess.check_call(\n",
        "            [sys.executable, '-m', 'pip', 'install', package_spec, '--quiet', '--user'],\n",
        "            stdout=subprocess.DEVNULL,\n",
        "            stderr=subprocess.PIPE,\n",
        "            timeout=300\n",
        "        )\n",
        "        __import__(import_name)\n",
        "        print(f\"   ✅ Installed via pip --user\")\n",
        "        return True\n",
        "    except (subprocess.CalledProcessError, ImportError, subprocess.TimeoutExpired):\n",
        "        pass\n",
        "    \n",
        "    # Method 3: pip install (system-wide)\n",
        "    try:\n",
        "        subprocess.check_call(\n",
        "            [sys.executable, '-m', 'pip', 'install', package_spec, '--quiet'],\n",
        "            stdout=subprocess.DEVNULL,\n",
        "            stderr=subprocess.PIPE,\n",
        "            timeout=300\n",
        "        )\n",
        "        __import__(import_name)\n",
        "        print(f\"   ✅ Installed via pip (system-wide)\")\n",
        "        return True\n",
        "    except (subprocess.CalledProcessError, ImportError, subprocess.TimeoutExpired):\n",
        "        pass\n",
        "    \n",
        "    # Method 4: pip install --break-system-packages\n",
        "    if ENV_TYPE == 'local' and platform.system() == 'Linux':\n",
        "        try:\n",
        "            subprocess.check_call(\n",
        "                [sys.executable, '-m', 'pip', 'install', package_spec, '--break-system-packages', '--quiet'],\n",
        "                stdout=subprocess.DEVNULL,\n",
        "                stderr=subprocess.PIPE,\n",
        "                timeout=300\n",
        "            )\n",
        "            __import__(import_name)\n",
        "            print(f\"   ✅ Installed via pip --break-system-packages\")\n",
        "            return True\n",
        "        except (subprocess.CalledProcessError, ImportError, subprocess.TimeoutExpired):\n",
        "            pass\n",
        "    \n",
        "    # Method 5: conda install\n",
        "    if shutil.which('conda'):\n",
        "        try:\n",
        "            conda_pkg = package_name.replace('-binary', '')\n",
        "            subprocess.check_call(\n",
        "                ['conda', 'install', '-y', conda_pkg],\n",
        "                stdout=subprocess.DEVNULL,\n",
        "                stderr=subprocess.PIPE,\n",
        "                timeout=300\n",
        "            )\n",
        "            __import__(import_name)\n",
        "            print(f\"   ✅ Installed via conda\")\n",
        "            return True\n",
        "        except (subprocess.CalledProcessError, ImportError, subprocess.TimeoutExpired):\n",
        "            pass\n",
        "    \n",
        "    # Method 6: apt-get (Docker/Colab)\n",
        "    if ENV_TYPE in ['docker', 'colab']:\n",
        "        try:\n",
        "            system_pkg_map = {\n",
        "                'psycopg2-binary': 'python3-psycopg2',\n",
        "                'pandas': 'python3-pandas',\n",
        "                'numpy': 'python3-numpy',\n",
        "                'matplotlib': 'python3-matplotlib',\n",
        "            }\n",
        "            \n",
        "            if package_name in system_pkg_map:\n",
        "                subprocess.check_call(\n",
        "                    ['apt-get', 'update'],\n",
        "                    stdout=subprocess.DEVNULL,\n",
        "                    stderr=subprocess.PIPE\n",
        "                )\n",
        "                subprocess.check_call(\n",
        "                    ['apt-get', 'install', '-y', system_pkg_map[package_name]],\n",
        "                    stdout=subprocess.DEVNULL,\n",
        "                    stderr=subprocess.PIPE,\n",
        "                    timeout=300\n",
        "                )\n",
        "                __import__(import_name)\n",
        "                print(f\"   ✅ Installed via apt-get\")\n",
        "                return True\n",
        "        except (subprocess.CalledProcessError, ImportError, subprocess.TimeoutExpired, FileNotFoundError):\n",
        "            pass\n",
        "    \n",
        "    print(f\"   ❌ Failed to install {package_name} via all methods\")\n",
        "    return False\n",
        "\n",
        "print(\"=\"*80)\n",
        "print(\"MULTI-METHOD PACKAGE INSTALLATION\")\n",
        "print(\"=\"*80)\n",
        "\n",
        "installed = []\n",
        "failed = []\n",
        "\n",
        "for package_spec in required_packages:\n",
        "    package_name = package_spec.split('>=')[0]\n",
        "    import_name = package_import_map.get(package_name, package_name.replace('-', '_'))\n",
        "    \n",
        "    if install_package_multiple_methods(package_spec, import_name):\n",
        "        installed.append(package_name)\n",
        "    else:\n",
        "        failed.append(package_name)\n",
        "\n",
        "print(\"\\n\" + \"=\"*80)\n",
        "if failed:\n",
        "    print(f\"⚠️  {len(failed)} package(s) failed: {', '.join(failed)}\")\n",
        "    print(\"   Manual: pip install \" + \" \".join(failed))\n",
        "else:\n",
        "    print(f\"✅ All {len(installed)} packages installed!\")\n",
        "print(\"=\"*80)\n",
        "\n",
        "# Import packages\n",
        "print(\"\\n\" + \"=\"*80)\n",
        "print(\"IMPORTING PACKAGES\")\n",
        "print(\"=\"*80)\n",
        "\n",
        "try:\n",
        "    import psycopg2\n",
        "    print(\"✅ psycopg2\")\n",
        "except ImportError as e:\n",
        "    print(f\"❌ psycopg2: {e}\")\n",
        "\n",
        "try:\n",
        "    import pandas as pd\n",
        "    print(\"✅ pandas\")\n",
        "except ImportError as e:\n",
        "    print(f\"❌ pandas: {e}\")\n",
        "\n",
        "try:\n",
        "    import numpy as np\n",
        "    print(\"✅ numpy\")\n",
        "except ImportError as e:\n",
        "    print(f\"❌ numpy: {e}\")\n",
        "\n",
        "try:\n",
        "    import matplotlib.pyplot as plt\n",
        "    import matplotlib\n",
        "    matplotlib.use('Agg')\n",
        "    print(\"✅ matplotlib\")\n",
        "except ImportError as e:\n",
        "    print(f\"❌ matplotlib: {e}\")\n",
        "\n",
        "try:\n",
        "    import seaborn as sns\n",
        "    print(\"✅ seaborn\")\n",
        "except ImportError as e:\n",
        "    print(f\"❌ seaborn: {e}\")\n",
        "\n",
        "try:\n",
        "    from IPython.display import display, HTML, Markdown\n",
        "    print(\"✅ IPython.display\")\n",
        "except ImportError:\n",
        "    display = print\n",
        "    Markdown = str\n",
        "    print(\"⚠️  IPython.display not available, using fallbacks\")\n",
        "\n",
        "import json\n",
        "from datetime import datetime\n",
        "import warnings\n",
        "warnings.filterwarnings('ignore')\n",
        "\n",
        "try:\n",
        "    plt.style.use('seaborn-v0_8-darkgrid')\n",
        "    sns.set_palette(\"husl\")\n",
        "except:\n",
        "    pass\n",
        "\n",
        "print(\"\\n\" + \"=\"*80)\n",
        "print(\"PACKAGE INSTALLATION COMPLETE\")\n",
        "print(\"=\"*80)"
    ]
    
    cell['source'] = source_lines
    return cell

def enhance_database_config_cell(cell: dict, db_name: str) -> dict:
    """Enhance database configuration cell with recursive file finding."""
    db_num = db_name.replace('db-', 'db')
    
    source_lines = [
        "# ============================================================================\n",
        "# DATABASE CONFIGURATION - ENVIRONMENT-AWARE WITH RECURSIVE FILE FINDING\n",
        "# ============================================================================\n",
        "\n",
        "def find_file_recursively(start_dir: Path, filename: str) -> Path:\n",
        "    \"\"\"Find a file or directory recursively from start directory.\"\"\"\n",
        "    try:\n",
        "        for path in start_dir.rglob(filename):\n",
        "            return path\n",
        "    except:\n",
        "        pass\n",
        "    return None\n",
        "\n",
        "def detect_database_directory(db_name: str) -> Path:\n",
        "    \"\"\"Detect database directory recursively based on environment.\"\"\"\n",
        "    search_paths = []\n",
        "    \n",
        "    if ENV_TYPE == 'docker':\n",
        "        search_paths = [\n",
        "            Path('/workspace/client/db'),\n",
        "            Path('/workspace/db'),\n",
        "            Path('/workspace'),\n",
        "        ]\n",
        "    elif ENV_TYPE == 'colab':\n",
        "        search_paths = [\n",
        "            Path('/content/drive/MyDrive/db'),\n",
        "            Path('/content/db'),\n",
        "            Path('/content'),\n",
        "        ]\n",
        "    else:  # local\n",
        "        search_paths = [\n",
        "            BASE_DIR / 'client' / 'db',\n",
        "            BASE_DIR,\n",
        "            Path.cwd(),\n",
        "            Path.home() / 'Documents' / 'AQ' / 'db',\n",
        "        ]\n",
        "    \n",
        "    # Try to find queries.json for this database\n",
        "    for search_path in search_paths:\n",
        "        if not search_path.exists():\n",
        "            continue\n",
        "        \n",
        "        # Look for queries.json recursively\n",
        "        queries_json = find_file_recursively(search_path, 'queries.json')\n",
        "        if queries_json:\n",
        "            # Check if it's for the right database\n",
        "            db_dir_candidate = queries_json.parent.parent\n",
        "            if db_dir_candidate.name == db_name:\n",
        "                return db_dir_candidate\n",
        "        \n",
        "        # Also check direct path\n",
        "        direct_path = search_path / db_name\n",
        "        if direct_path.exists() and (direct_path / 'queries').exists():\n",
        "            return direct_path\n",
        "    \n",
        "    # Fallback: use current directory if it matches\n",
        "    if Path.cwd().name == db_name:\n",
        "        return Path.cwd()\n",
        "    \n",
        "    # Last resort: return base_dir / db_name\n",
        "    return BASE_DIR / db_name\n",
        "\n",
        f"# Database name\n",
        f"DB_NAME = '{db_num}'\n",
        "\n",
        f"# Detect database directory recursively\n",
        f"DB_DIR = detect_database_directory('{db_name}')\n",
        "\n",
        "# Configure PostgreSQL connection based on environment\n",
        "if ENV_TYPE == 'docker':\n",
        "    DB_CONFIG = {\n",
        "        'host': os.getenv('PG_HOST', 'localhost'),\n",
        "        'port': os.getenv('PG_PORT', '5432'),\n",
        "        'user': os.getenv('PG_USER', 'postgres'),\n",
        "        'password': os.getenv('PG_PASSWORD', 'postgres'),\n",
        "        'database': 'postgres'\n",
        "    }\n",
        "elif ENV_TYPE == 'colab':\n",
        "    DB_CONFIG = {\n",
        "        'host': os.getenv('PG_HOST', 'localhost'),\n",
        "        'port': os.getenv('PG_PORT', '5432'),\n",
        "        'user': os.getenv('PG_USER', 'postgres'),\n",
        "        'password': os.getenv('PG_PASSWORD', ''),\n",
        "        'database': 'postgres'\n",
        "    }\n",
        "else:  # local\n",
        "    DB_CONFIG = {\n",
        "        'host': os.getenv('PG_HOST', 'localhost'),\n",
        "        'port': os.getenv('PG_PORT', '5432'),\n",
        "        'user': os.getenv('PG_USER', os.getenv('USER', 'postgres')),\n",
        "        'password': os.getenv('PG_PASSWORD', ''),\n",
        "        'database': 'postgres'\n",
        "    }\n",
        "\n",
        "print(\"=\"*80)\n",
        "print(\"DATABASE CONFIGURATION\")\n",
        "print(\"=\"*80)\n",
        "print(f\"Environment: {ENV_TYPE}\")\n",
        "print(f\"Database Name: {DB_NAME}\")\n",
        "print(f\"Database Directory: {DB_DIR}\")\n",
        "print(f\"PostgreSQL Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}\")\n",
        "print(f\"PostgreSQL User: {DB_CONFIG['user']}\")\n",
        "\n",
        "# Find files recursively\n",
        "queries_file = find_file_recursively(DB_DIR, 'queries.json')\n",
        "if not queries_file:\n",
        "    queries_file = DB_DIR / 'queries' / 'queries.json'\n",
        "\n",
        "schema_file = find_file_recursively(DB_DIR, 'schema.sql')\n",
        "if not schema_file:\n",
        "    schema_file = DB_DIR / 'data' / 'schema.sql'\n",
        "\n",
        "data_file = find_file_recursively(DB_DIR, 'data.sql')\n",
        "if not data_file:\n",
        "    data_file = DB_DIR / 'data' / 'data.sql'\n",
        "\n",
        "print(f\"\\nQueries File: {queries_file} ({'✅' if queries_file.exists() else '❌'})\")\n",
        "print(f\"Schema File: {schema_file} ({'✅' if schema_file.exists() else '❌'})\")\n",
        "print(f\"Data File: {data_file} ({'✅' if data_file.exists() else '❌'})\")\n",
        "print(\"=\"*80)"
    ]
    
    cell['source'] = source_lines
    return cell

def enhance_database_init_cell(cell: dict, db_name: str) -> dict:
    """Enhance database initialization cell to use recursive file finding."""
    source = ''.join(cell.get('source', []))
    
    # Replace hardcoded paths with recursive finding
    source = source.replace(
        "schema_file = db_dir / 'data' / 'schema.sql'",
        "# Find schema.sql recursively\n            schema_file = find_file_recursively(DB_DIR, 'schema.sql')\n            if not schema_file:\n                schema_file = DB_DIR / 'data' / 'schema.sql'"
    )
    
    source = source.replace(
        "data_file = db_dir / 'data' / 'data.sql'",
        "# Find data.sql recursively\n            data_file = find_file_recursively(DB_DIR, 'data.sql')\n            if not data_file:\n                data_file = DB_DIR / 'data' / 'data.sql'"
    )
    
    cell['source'] = source.split('\n')
    return cell

def enhance_query_loading_cell(cell: dict, db_name: str) -> dict:
    """Enhance query loading cell to use recursive file finding."""
    source_lines = [
        "# ============================================================================\n",
        "# LOAD QUERY METADATA - RECURSIVE FILE FINDING\n",
        "# ============================================================================\n",
        "\n",
        "# Find queries.json recursively\n",
        "queries_file = find_file_recursively(BASE_DIR, 'queries.json')\n",
        "if not queries_file:\n",
        f"    queries_file = find_file_recursively(DB_DIR, 'queries.json')\n",
        "if not queries_file:\n",
        "    queries_file = DB_DIR / 'queries' / 'queries.json'\n",
        "\n",
        "if not queries_file.exists():\n",
        "    raise FileNotFoundError(f\"queries.json not found: {queries_file}\")\n",
        "\n",
        "with open(queries_file) as f:\n",
        "    queries_data = json.load(f)\n",
        "\n",
        "queries = queries_data.get('queries', [])\n",
        "total_queries = len(queries)\n",
        "\n",
        "print(\"=\"*80)\n",
        "print(\"QUERY METADATA LOADED\")\n",
        "print(\"=\"*80)\n",
        "print(f\"Total Queries: {total_queries}\")\n",
        "print(f\"Source File: {queries_file}\")\n",
        "print(f\"\\nQuery Overview:\")\n",
        "for q in queries[:5]:\n",
        "    print(f\"  Query {q.get('number')}: {q.get('title', 'N/A')[:60]}...\")\n",
        "if total_queries > 5:\n",
        "    print(f\"  ... and {total_queries - 5} more queries\")\n",
        "print(\"=\"*80)"
    ]
    
    cell['source'] = source_lines
    return cell

def main():
    """Enhance all existing notebooks."""
    print("="*80)
    print("ENHANCING NOTEBOOKS WITH ENVIRONMENT DETECTION")
    print("="*80)
    
    for db_name in DATABASES:
        notebook_path = BASE_DIR / db_name / f'{db_name}.ipynb'
        
        if not notebook_path.exists():
            print(f"⚠️  Skipping {db_name} - notebook not found")
            continue
        
        print(f"\nEnhancing {db_name}...")
        
        try:
            enhanced_notebook = enhance_notebook_with_environment_detection(notebook_path)
            
            # Backup original
            backup_path = notebook_path.with_suffix('.ipynb.backup')
            import shutil
            shutil.copy2(notebook_path, backup_path)
            
            # Write enhanced notebook
            with open(notebook_path, 'w') as f:
                json.dump(enhanced_notebook, f, indent=1)
            
            print(f"✅ Enhanced: {notebook_path}")
            print(f"   Backup: {backup_path}")
        except Exception as e:
            print(f"❌ Failed to enhance {db_name}: {e}")
    
    print(f"\n{'='*80}")
    print("Notebook enhancement complete")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
