#!/usr/bin/env python3
"""
Copy db-*.ipynb notebooks to client/db structure
Update paths to work from client/db root with recursive file finding
"""

import json
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'
ROOT_DB_DIR = BASE_DIR

DATABASES = [f'db-{i}' for i in range(6, 16)]

# Database to deliverable folder mapping
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

def update_notebook_for_client(notebook_content: dict, db_name: str) -> dict:
    """Update notebook to work from client/db root with recursive file finding."""
    
    cells = notebook_content.get('cells', [])
    db_num = db_name.replace('db-', 'db')
    
    for cell_idx, cell in enumerate(cells):
        if cell.get('cell_type') != 'code':
            continue
            
        source_lines = cell.get('source', [])
        source_text = ''.join(source_lines)
        
        # Skip if this cell doesn't need updates
        if 'DB_DIR' not in source_text and 'BASE_DIR' not in source_text:
            continue
        
        new_source_lines = []
        i = 0
        
        while i < len(source_lines):
            line = source_lines[i]
            line_text = line if isinstance(line, str) else ''
            
            # Add recursive file finding function at the start
            if i == 0 and 'END-TO-END SETUP' in line_text:
                new_source_lines.insert(0, "from pathlib import Path\n")
                new_source_lines.insert(1, "\n")
                new_source_lines.insert(2, "def find_file_recursively(start_dir: Path, filename: str) -> Path:\n")
                new_source_lines.insert(3, "    \"\"\"Find a file or directory recursively from start directory.\"\"\"\n")
                new_source_lines.insert(4, "    try:\n")
                new_source_lines.insert(5, "        for path in start_dir.rglob(filename):\n")
                new_source_lines.insert(6, "            return path\n")
                new_source_lines.insert(7, "    except:\n")
                new_source_lines.insert(8, "        pass\n")
                new_source_lines.insert(9, "    return None\n")
                new_source_lines.insert(10, "\n")
            
            # Set BASE_DIR and ROOT_DB_DIR FIRST (before DB_DIR detection)
            if 'DATABASE CONFIGURATION' in line_text or ('DB_NAME =' in line_text and f"'{db_num}'" in line_text):
                # Insert BASE_DIR and ROOT_DB_DIR before DB_NAME
                if 'DB_NAME =' in line_text:
                    new_source_lines.append("# Set base directories for recursive file finding\n")
                    new_source_lines.append("BASE_DIR = Path('/Users/machine/Documents/AQ/db/client/db')\n")
                    new_source_lines.append("ROOT_DB_DIR = Path('/Users/machine/Documents/AQ/db')\n")
                    new_source_lines.append("\n")
                    new_source_lines.append(line)
                    i += 1
                    
                    # Skip all old DB_DIR detection code
                    while i < len(source_lines):
                        next_line = source_lines[i]
                        next_text = next_line if isinstance(next_line, str) else ''
                        
                        # Stop at DB_CONFIG or print statements
                        if 'DB_CONFIG =' in next_text or ('print(' in next_text and 'DATABASE CONFIGURATION' in next_text):
                            break
                        
                        # Skip old DB_DIR detection patterns
                        if any(pattern in next_text for pattern in [
                            'current_dir = Path(os.getcwd())',
                            'if current_dir.name ==',
                            'DB_DIR = current_dir',
                            'DB_DIR = Path(\'/Users/machine/Documents/AQ/db/',
                            'except:',
                            'try:',
                            'import os',
                            'BASE_DIR = Path'
                        ]):
                            i += 1
                            continue
                        
                        i += 1
                    
                    # Insert new recursive finding logic
                    new_source_lines.append("\n")
                    new_source_lines.append("# Find database directory recursively from client/db root\n")
                    new_source_lines.append("DB_DIR = None\n")
                    new_source_lines.append("# Try client/db structure first\n")
                    new_source_lines.append(f"client_db_path = BASE_DIR / '{db_name}'\n")
                    new_source_lines.append("if client_db_path.exists():\n")
                    new_source_lines.append("    # Look for queries.json in subdirectories\n")
                    new_source_lines.append("    queries_json = find_file_recursively(client_db_path, 'queries.json')\n")
                    new_source_lines.append("    if queries_json:\n")
                    new_source_lines.append("        DB_DIR = queries_json.parent.parent  # Go up from queries/queries.json\n")
                    new_source_lines.append("if not DB_DIR:\n")
                    new_source_lines.append("    # Fallback: try root db directory\n")
                    new_source_lines.append(f"    root_db_path = ROOT_DB_DIR / '{db_name}'\n")
                    new_source_lines.append("    DB_DIR = root_db_path if root_db_path.exists() else Path.cwd()\n")
                    new_source_lines.append(f"print(f\"Using DB_DIR: {{DB_DIR}}\")\n")
                    continue
            
            # Update BASE_DIR if found elsewhere
            if "BASE_DIR = Path('/Users/machine/Documents/AQ/db')" in line_text:
                new_source_lines.append("BASE_DIR = Path('/Users/machine/Documents/AQ/db/client/db')\n")
                new_source_lines.append("ROOT_DB_DIR = Path('/Users/machine/Documents/AQ/db')\n")
                i += 1
                continue
            
            # Update queries.json path
            if "queries_file = DB_DIR / 'queries' / 'queries.json'" in line_text:
                new_source_lines.append("# Find queries.json recursively\n")
                new_source_lines.append("queries_file = find_file_recursively(BASE_DIR, 'queries.json')\n")
                new_source_lines.append("if not queries_file:\n")
                new_source_lines.append(f"    queries_file = find_file_recursively(ROOT_DB_DIR / '{db_name}', 'queries.json')\n")
                new_source_lines.append("if not queries_file:\n")
                new_source_lines.append(f"    queries_file = ROOT_DB_DIR / '{db_name}' / 'queries' / 'queries.json'\n")
                i += 1
                continue
            
            # Update schema.sql path
            if "schema_file = db_dir / 'data' / 'schema.sql'" in line_text or "schema_file = DB_DIR / 'data' / 'schema.sql'" in line_text:
                new_source_lines.append("            # Find schema.sql recursively\n")
                new_source_lines.append("            schema_file = find_file_recursively(DB_DIR, 'schema.sql')\n")
                new_source_lines.append("            if not schema_file:\n")
                new_source_lines.append(f"                schema_file = ROOT_DB_DIR / '{db_name}' / 'data' / 'schema.sql'\n")
                i += 1
                continue
            
            # Update data.sql path
            if "data_file = db_dir / 'data' / 'data.sql'" in line_text or "data_file = DB_DIR / 'data' / 'data.sql'" in line_text:
                new_source_lines.append("            # Find data.sql recursively\n")
                new_source_lines.append("            data_file = find_file_recursively(DB_DIR, 'data.sql')\n")
                new_source_lines.append("            if not data_file:\n")
                new_source_lines.append(f"                data_file = ROOT_DB_DIR / '{db_name}' / 'data' / 'data.sql'\n")
                i += 1
                continue
            
            new_source_lines.append(line)
            i += 1
        
        cell['source'] = new_source_lines
    
    return notebook_content

def copy_and_adapt_notebook(db_name: str):
    """Copy notebook to client and adapt paths."""
    root_notebook = ROOT_DB_DIR / db_name / f'{db_name}.ipynb'
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    
    if not root_notebook.exists():
        print(f"⚠️  {db_name}: Source notebook not found")
        return False
    
    if not deliverable_folder:
        print(f"⚠️  {db_name}: No deliverable folder mapping")
        return False
    
    # Load notebook
    with open(root_notebook) as f:
        notebook_content = json.load(f)
    
    # Update paths for client structure
    notebook_content = update_notebook_for_client(notebook_content, db_name)
    
    # Copy to client location
    client_notebook_dir = CLIENT_DB_DIR / db_name / deliverable_folder
    client_notebook_dir.mkdir(parents=True, exist_ok=True)
    
    client_notebook = client_notebook_dir / f'{db_name}.ipynb'
    
    with open(client_notebook, 'w') as f:
        json.dump(notebook_content, f, indent=1)
    
    print(f"✅ Copied {db_name}.ipynb to {client_notebook.relative_to(BASE_DIR)}")
    return True

def main():
    """Copy all notebooks to client/db."""
    print("="*80)
    print("COPYING NOTEBOOKS TO CLIENT/DB WITH RECURSIVE FILE FINDING")
    print("="*80)
    
    for db_name in DATABASES:
        copy_and_adapt_notebook(db_name)
    
    print(f"\n{'='*80}")
    print("Notebooks copied to client/db structure")
    print("Notebooks configured to find files recursively from client/db root")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
