#!/usr/bin/env python3
"""
Synchronize environment-aware notebooks and Streamlit dashboards to client/db
Preserves all client customizations (data files, vercel.json, .gitignore, HTML, etc.)
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'
ROOT_DB_DIR = BASE_DIR
DASHBOARD_DIR = BASE_DIR / 'docker' / 'notebooks'

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

sync_report = {
    'sync_timestamp': datetime.now().isoformat(),
    'notebooks_updated': [],
    'dashboards_added': [],
    'files_preserved': [],
    'errors': []
}

def update_notebook_for_client_structure(notebook_content: dict, db_name: str) -> dict:
    """Update notebook to work from client/db structure with recursive file finding."""
    
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
            
            # Add recursive file finding function at the start if needed
            if i == 0 and 'ENVIRONMENT DETECTION' in line_text:
                # Check if function already exists
                if 'def find_file_recursively' not in source_text:
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
            
            # Update BASE_DIR detection for client structure
            if 'def find_base_directory()' in line_text or 'BASE_DIR = find_base_directory()' in line_text:
                # Update search paths to prioritize client/db
                new_source_lines.append(line)
                i += 1
                
                # Update the search paths in find_base_directory
                while i < len(source_lines):
                    next_line = source_lines[i]
                    next_text = next_line if isinstance(next_line, str) else ''
                    
                    if 'start_paths = [' in next_text:
                        new_source_lines.append(next_line)
                        i += 1
                        # Add client/db paths first
                        new_source_lines.append("        Path('/workspace/client/db'),\n")
                        new_source_lines.append("        Path('/workspace/client/db') / 'db-6',\n")
                        # Skip old paths, add them after
                        while i < len(source_lines):
                            path_line = source_lines[i]
                            path_text = path_line if isinstance(path_line, str) else ''
                            if ']' in path_text:
                                new_source_lines.append(path_line)
                                i += 1
                                break
                            i += 1
                        break
                    
                    new_source_lines.append(next_line)
                    i += 1
                continue
            
            # Update database directory detection
            if f"DB_NAME = '{db_num}'" in line_text or 'detect_database_directory' in line_text:
                new_source_lines.append(line)
                i += 1
                
                # Update search paths to prioritize client/db
                while i < len(source_lines):
                    next_line = source_lines[i]
                    next_text = next_line if isinstance(next_line, str) else ''
                    
                    if 'if ENV_TYPE ==' in next_text:
                        # Update search paths for client structure
                        new_source_lines.append(next_line)
                        i += 1
                        
                        # Update Docker paths
                        if 'docker' in next_text.lower():
                            while i < len(source_lines):
                                path_line = source_lines[i]
                                path_text = path_line if isinstance(path_line, str) else ''
                                if 'search_paths = [' in path_text:
                                    new_source_lines.append(path_line)
                                    i += 1
                                    # Add client/db paths first
                                    new_source_lines.append("            Path('/workspace/client/db'),\n")
                                    new_source_lines.append(f"            Path('/workspace/client/db') / '{db_name}',\n")
                                    # Continue with existing paths
                                    while i < len(source_lines):
                                        path_line = source_lines[i]
                                        path_text = path_line if isinstance(path_line, str) else ''
                                        if ']' in path_text:
                                            new_source_lines.append(path_line)
                                            i += 1
                                            break
                                        new_source_lines.append(path_line)
                                        i += 1
                                    break
                                new_source_lines.append(path_line)
                                i += 1
                            continue
                        
                        # Update local paths
                        if 'local' in next_text.lower() or 'else' in next_text:
                            while i < len(source_lines):
                                path_line = source_lines[i]
                                path_text = path_line if isinstance(path_line, str) else ''
                                if 'search_paths = [' in path_text:
                                    new_source_lines.append(path_line)
                                    i += 1
                                    # Add client/db paths first
                                    new_source_lines.append("            BASE_DIR / 'client' / 'db',\n")
                                    new_source_lines.append(f"            BASE_DIR / 'client' / 'db' / '{db_name}',\n")
                                    # Continue with existing paths
                                    while i < len(source_lines):
                                        path_line = source_lines[i]
                                        path_text = path_line if isinstance(path_line, str) else ''
                                        if ']' in path_text:
                                            new_source_lines.append(path_line)
                                            i += 1
                                            break
                                        new_source_lines.append(path_line)
                                        i += 1
                                    break
                                new_source_lines.append(path_line)
                                i += 1
                            continue
                    
                    new_source_lines.append(next_line)
                    i += 1
                continue
            
            new_source_lines.append(line)
            i += 1
        
        cell['source'] = new_source_lines
    
    return notebook_content

def sync_notebook_to_client(db_name: str):
    """Sync environment-aware notebook to client/db, preserving customizations."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return False
    
    root_notebook = ROOT_DB_DIR / db_name / f'{db_name}.ipynb'
    client_notebook_dir = CLIENT_DB_DIR / db_name / deliverable_folder
    client_notebook = client_notebook_dir / f'{db_name}.ipynb'
    
    if not root_notebook.exists():
        sync_report['errors'].append(f"Root notebook not found: {root_notebook}")
        return False
    
    if not client_notebook_dir.exists():
        sync_report['errors'].append(f"Client directory not found: {client_notebook_dir}")
        return False
    
    # Load root notebook
    with open(root_notebook) as f:
        notebook_content = json.load(f)
    
    # Update notebook for client structure
    notebook_content = update_notebook_for_client_structure(notebook_content, db_name)
    
    # Backup existing client notebook if it exists
    if client_notebook.exists():
        backup_path = client_notebook.with_suffix('.ipynb.backup')
        shutil.copy2(client_notebook, backup_path)
        sync_report['files_preserved'].append(f"Backed up: {backup_path.relative_to(BASE_DIR)}")
    
    # Write updated notebook
    with open(client_notebook, 'w') as f:
        json.dump(notebook_content, f, indent=1)
    
    sync_report['notebooks_updated'].append(str(client_notebook.relative_to(BASE_DIR)))
    print(f"✅ Updated notebook: {client_notebook.relative_to(BASE_DIR)}")
    return True

def sync_dashboard_to_client(db_name: str):
    """Sync Streamlit dashboard to client/db."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return False
    
    root_dashboard = DASHBOARD_DIR / f'{db_name}_dashboard.py'
    client_dashboard_dir = CLIENT_DB_DIR / db_name / deliverable_folder
    client_dashboard = client_dashboard_dir / f'{db_name}_dashboard.py'
    
    if not root_dashboard.exists():
        sync_report['errors'].append(f"Dashboard not found: {root_dashboard}")
        return False
    
    if not client_dashboard_dir.exists():
        sync_report['errors'].append(f"Client directory not found: {client_dashboard_dir}")
        return False
    
    # Read dashboard content
    dashboard_content = root_dashboard.read_text(encoding='utf-8')
    
    # Update dashboard paths for client structure
    # Update BASE_DIR detection to prioritize client/db
    dashboard_content = dashboard_content.replace(
        "Path('/workspace/client/db'),",
        "Path('/workspace/client/db'),\n            Path('/workspace/client/db') / 'db-6',"
    )
    
    # Update find_queries_file to prioritize client structure
    dashboard_content = dashboard_content.replace(
        "def find_queries_file():",
        "def find_queries_file():\n    \"\"\"Find queries.json recursively, prioritizing client/db structure.\"\"\""
    )
    
    # Write dashboard to client
    with open(client_dashboard, 'w') as f:
        f.write(dashboard_content)
    
    # Make executable
    client_dashboard.chmod(0o755)
    
    sync_report['dashboards_added'].append(str(client_dashboard.relative_to(BASE_DIR)))
    print(f"✅ Added dashboard: {client_dashboard.relative_to(BASE_DIR)}")
    return True

def preserve_client_customizations(db_name: str):
    """Document and preserve client customizations."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return
    
    client_dir = CLIENT_DB_DIR / db_name / deliverable_folder
    
    if not client_dir.exists():
        return
    
    # List of files to preserve (never overwrite)
    preserve_patterns = [
        'vercel.json',
        '.gitignore',
        '*_documentation.html',
        '*.html',
        'data/data_large*.sql',
        'data/schema_*.sql',
        'data/*_postgresql.sql',
        'data/*_optimized*.sql',
        'data/apply_*.sql',
        'data/insurance_*.sql',
        'data/nexrad_*.sql',
        'data/schema_extensions*.sql',
    ]
    
    preserved_files = []
    for pattern in preserve_patterns:
        for file_path in client_dir.rglob(pattern):
            if file_path.is_file():
                preserved_files.append(str(file_path.relative_to(BASE_DIR)))
    
    sync_report['files_preserved'].extend(preserved_files)

def check_data_files(db_name: str):
    """Check and preserve client data file customizations."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return
    
    client_data_dir = CLIENT_DB_DIR / db_name / deliverable_folder / 'data'
    root_data_dir = ROOT_DB_DIR / db_name / 'data'
    
    if not client_data_dir.exists():
        return
    
    # List all files in client data directory
    client_files = list(client_data_dir.glob('*'))
    
    # Only sync basic schema.sql and data.sql if they're newer in root
    # Preserve all other files (data_large, schema_postgresql, etc.)
    for client_file in client_files:
        if client_file.name in ['schema.sql', 'data.sql']:
            root_file = root_data_dir / client_file.name
            if root_file.exists():
                root_mtime = root_file.stat().st_mtime
                client_mtime = client_file.stat().st_mtime
                
                if root_mtime > client_mtime:
                    shutil.copy2(root_file, client_file)
                    print(f"✅ Updated {client_file.name} for {db_name}")
        else:
            # Preserve all other files
            sync_report['files_preserved'].append(str(client_file.relative_to(BASE_DIR)))

def main():
    """Sync notebooks and dashboards to client/db."""
    print("="*80)
    print("SYNCHRONIZING NOTEBOOKS AND DASHBOARDS TO CLIENT/DB")
    print("="*80)
    print("Preserving all client customizations...")
    print()
    
    for db_name in DATABASES:
        print(f"\nProcessing {db_name}...")
        
        # Preserve customizations first
        preserve_client_customizations(db_name)
        check_data_files(db_name)
        
        # Sync notebook
        sync_notebook_to_client(db_name)
        
        # Sync dashboard
        sync_dashboard_to_client(db_name)
    
    # Generate sync report
    report_file = CLIENT_DB_DIR / 'SYNC_REPORT.md'
    report_content = f"""# Synchronization Report - Notebooks and Dashboards

**Sync Timestamp:** {sync_report['sync_timestamp']}

## Summary

- **Notebooks Updated:** {len(sync_report['notebooks_updated'])}
- **Dashboards Added:** {len(sync_report['dashboards_added'])}
- **Files Preserved:** {len(sync_report['files_preserved'])}
- **Errors:** {len(sync_report['errors'])}

## Notebooks Updated

"""
    
    for file_path in sync_report['notebooks_updated']:
        report_content += f"- `{file_path}`\n"
    
    report_content += "\n## Dashboards Added\n\n"
    for file_path in sync_report['dashboards_added']:
        report_content += f"- `{file_path}`\n"
    
    report_content += "\n## Files Preserved (Client Customizations)\n\n"
    preserved_set = set(sync_report['files_preserved'])
    for file_path in sorted(preserved_set):
        report_content += f"- `{file_path}`\n"
    
    if sync_report['errors']:
        report_content += "\n## Errors\n\n"
        for error in sync_report['errors']:
            report_content += f"- {error}\n"
    
    report_file.write_text(report_content, encoding='utf-8')
    print(f"\n✅ Sync report saved: {report_file}")
    
    print(f"\n{'='*80}")
    print("SYNCHRONIZATION COMPLETE")
    print(f"{'='*80}")
    print(f"Notebooks Updated: {len(sync_report['notebooks_updated'])}")
    print(f"Dashboards Added: {len(sync_report['dashboards_added'])}")
    print(f"Files Preserved: {len(preserved_set)}")
    print(f"\nAll client customizations preserved!")
    print(f"Notebooks and dashboards updated to work from client/db structure")

if __name__ == '__main__':
    main()
