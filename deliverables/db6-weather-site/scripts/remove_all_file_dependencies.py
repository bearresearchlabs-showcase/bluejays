#!/usr/bin/env python3
"""
Remove ALL file system dependencies from notebooks
- Remove any remaining file.open() calls for schema.sql/data.sql/queries.json
- Ensure everything uses embedded data only
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

def remove_file_dependencies(notebook: dict) -> bool:
    """Remove all file system dependencies."""
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] != 'code':
            continue
        
        source_lines = cell.get('source', [])
        source_text = ''.join(source_lines)
        original_text = source_text
        
        # Skip embedded SQL cells (they contain schema.sql/data.sql as strings, which is fine)
        if 'EMBEDDED SCHEMA.SQL' in source_text or 'EMBEDDED DATA.SQL' in source_text or 'EMBEDDED QUERIES.JSON' in source_text:
            continue
        
        # Remove file loading code for queries.json
        if 'queries.json' in source_text.lower() and ('open(' in source_text.lower() or 'Path(' in source_text.lower()):
            if 'EMBEDDED' not in source_text and 'QUERIES_DATA' not in source_text:
                # Replace with embedded queries usage
                new_source = '''# ============================================================================
# LOAD QUERIES (FROM EMBEDDED DATA)
# ============================================================================
# Queries are already loaded from embedded QUERIES_DATA cell above
# No file system access required

if 'queries' not in globals():
    print("⚠️  Queries not found. Run the 'Embedded Queries JSON' cell first.")
    print("   The queries are embedded in this notebook - no external files needed.")
else:
    print("="*80)
    print("QUERIES LOADED FROM EMBEDDED DATA")
    print("="*80)
    print(f"Total Queries: {len(queries)}")
    if queries:
        print(f"\\nQuery Overview:")
        for q in queries[:5]:
            title = q.get('title', 'N/A')[:60]
            print(f"  Query {q.get('number')}: {title}...")
        if len(queries) > 5:
            print(f"  ... and {len(queries) - 5} more queries")
    print("="*80)
'''
                cell['source'] = new_source.split('\n')
                for j in range(len(cell['source']) - 1):
                    if cell['source'][j] and not cell['source'][j].endswith('\n'):
                        cell['source'][j] += '\n'
                modified = True
                print(f"   ✅ Removed queries.json file dependency in cell {i}")
        
        # Remove file loading code for schema.sql (if not in embedded cell)
        if 'schema.sql' in source_text.lower() and 'open(' in source_text.lower():
            if 'EMBEDDED' not in source_text and 'SCHEMA_SQL' not in source_text:
                new_source = '''# ============================================================================
# LOAD SCHEMA (FROM EMBEDDED DATA)
# ============================================================================
# Schema is already available in SCHEMA_SQL variable from embedded cell
# No file system access required

if 'SCHEMA_SQL' not in globals():
    print("⚠️  SCHEMA_SQL not found. Run the 'Embedded Schema SQL' cell first.")
    print("   The schema is embedded in this notebook - no external files needed.")
else:
    print("="*80)
    print("SCHEMA SQL AVAILABLE FROM EMBEDDED DATA")
    print("="*80)
    print(f"Schema SQL length: {len(SCHEMA_SQL)} characters")
    print("\\nTo load schema into database, run: execute_schema_sql(conn)")
    print("="*80)
'''
                cell['source'] = new_source.split('\n')
                for j in range(len(cell['source']) - 1):
                    if cell['source'][j] and not cell['source'][j].endswith('\n'):
                        cell['source'][j] += '\n'
                modified = True
                print(f"   ✅ Removed schema.sql file dependency in cell {i}")
        
        # Remove file loading code for data.sql (if not in embedded cell)
        if 'data.sql' in source_text.lower() and 'open(' in source_text.lower():
            if 'EMBEDDED' not in source_text and 'DATA_SQL' not in source_text:
                new_source = '''# ============================================================================
# LOAD DATA (FROM EMBEDDED DATA)
# ============================================================================
# Data is already available in DATA_SQL variable from embedded cell (if available)
# No file system access required

if 'DATA_SQL' not in globals():
    print("⚠️  DATA_SQL not found. This database may not have sample data.")
    print("   If data exists, run the 'Embedded Data SQL' cell first.")
else:
    print("="*80)
    print("DATA SQL AVAILABLE FROM EMBEDDED DATA")
    print("="*80)
    print(f"Data SQL length: {len(DATA_SQL)} characters")
    print("\\nTo load data into database, run: execute_data_sql(conn)")
    print("="*80)
'''
                cell['source'] = new_source.split('\n')
                for j in range(len(cell['source']) - 1):
                    if cell['source'][j] and not cell['source'][j].endswith('\n'):
                        cell['source'][j] += '\n'
                modified = True
                print(f"   ✅ Removed data.sql file dependency in cell {i}")
    
    return modified

def fix_notebook(notebook_path: Path) -> bool:
    """Remove all file dependencies from notebook."""
    print(f"\\nRemoving file dependencies: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    
    if remove_file_dependencies(notebook):
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
        return True
    
    return False

def main():
    """Main execution."""
    print("="*80)
    print("REMOVING ALL FILE SYSTEM DEPENDENCIES FROM NOTEBOOKS")
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
    print("✅ ALL FILE DEPENDENCIES REMOVED!")
    print("="*80)

if __name__ == '__main__':
    main()
