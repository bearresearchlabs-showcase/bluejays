#!/usr/bin/env python3
"""
Update schema and data loading code to use detected DATA_DIR paths
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

def update_schema_loading(notebook: dict) -> bool:
    """Update schema loading code to use SCHEMA_FILE."""
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] != 'code':
            continue
        
        source_lines = cell.get('source', [])
        source_text = ''.join(source_lines)
        original_text = source_text
        
        # Look for schema.sql loading patterns
        if 'schema.sql' in source_text.lower() and ('open' in source_text.lower() or 'read' in source_text.lower()):
            # Replace hardcoded paths with SCHEMA_FILE
            replacements = [
                # Pattern: open('path/to/schema.sql')
                (r"open\(['\"]([^'\"]*schema\.sql[^'\"]*)['\"]", r"open(SCHEMA_FILE if 'SCHEMA_FILE' in globals() else r'\1'"),
                # Pattern: Path('path/to/schema.sql')
                (r"Path\(['\"]([^'\"]*schema\.sql[^'\"]*)['\"]", r"Path(SCHEMA_FILE if 'SCHEMA_FILE' in globals() else r'\1'"),
                # Pattern: 'schema.sql' or "schema.sql"
                (r"['\"]([^'\"]*schema\.sql[^'\"]*)['\"]", r"(SCHEMA_FILE if 'SCHEMA_FILE' in globals() else r'\1')"),
            ]
            
            # More specific: replace direct schema.sql references
            if "with open('schema.sql'" in source_text or 'with open("schema.sql"' in source_text:
                source_text = source_text.replace("with open('schema.sql'", "with open(str(SCHEMA_FILE) if 'SCHEMA_FILE' in globals() else 'schema.sql'")
                source_text = source_text.replace('with open("schema.sql"', 'with open(str(SCHEMA_FILE) if "SCHEMA_FILE" in globals() else "schema.sql"')
            
            if "Path('schema.sql'" in source_text or 'Path("schema.sql"' in source_text:
                source_text = source_text.replace("Path('schema.sql'", "Path(SCHEMA_FILE if 'SCHEMA_FILE' in globals() else 'schema.sql'")
                source_text = source_text.replace('Path("schema.sql"', 'Path(SCHEMA_FILE if "SCHEMA_FILE" in globals() else "schema.sql"')
            
            # Add check at beginning of cell if SCHEMA_FILE not defined
            if 'SCHEMA_FILE' not in source_text and 'DATA_DIR' in source_text:
                # Add check
                lines = source_text.split('\n')
                insert_idx = 0
                for j, line in enumerate(lines):
                    if 'import' in line.lower() or 'from' in line.lower():
                        insert_idx = j + 1
                    elif line.strip() and not line.strip().startswith('#'):
                        break
                
                check_code = '''# Use detected SCHEMA_FILE if available
if 'SCHEMA_FILE' not in globals():
    # Fallback: try to find schema.sql
    if 'DATA_DIR' in globals() and DATA_DIR:
        SCHEMA_FILE = DATA_DIR / 'schema.sql'
    else:
        SCHEMA_FILE = Path('schema.sql')
'''
                lines.insert(insert_idx, check_code)
                source_text = '\n'.join(lines)
        
        # Similar for data.sql
        if 'data.sql' in source_text.lower() and ('open' in source_text.lower() or 'read' in source_text.lower()):
            if "with open('data.sql'" in source_text or 'with open("data.sql"' in source_text:
                source_text = source_text.replace("with open('data.sql'", "with open(str(DATA_FILE) if 'DATA_FILE' in globals() and DATA_FILE else 'data.sql'")
                source_text = source_text.replace('with open("data.sql"', 'with open(str(DATA_FILE) if "DATA_FILE" in globals() and DATA_FILE else "data.sql"')
            
            if "Path('data.sql'" in source_text or 'Path("data.sql"' in source_text:
                source_text = source_text.replace("Path('data.sql'", "Path(DATA_FILE if 'DATA_FILE' in globals() and DATA_FILE else 'data.sql'")
                source_text = source_text.replace('Path("data.sql"', 'Path(DATA_FILE if "DATA_FILE" in globals() and DATA_FILE else "data.sql"')
            
            # Add check for DATA_FILE
            if 'DATA_FILE' not in source_text and 'DATA_DIR' in source_text:
                lines = source_text.split('\n')
                insert_idx = 0
                for j, line in enumerate(lines):
                    if 'import' in line.lower() or 'from' in line.lower():
                        insert_idx = j + 1
                    elif line.strip() and not line.strip().startswith('#'):
                        break
                
                check_code = '''# Use detected DATA_FILE if available
if 'DATA_FILE' not in globals():
    if 'DATA_DIR' in globals() and DATA_DIR:
        data_file_path = DATA_DIR / 'data.sql'
        DATA_FILE = data_file_path if data_file_path.exists() else None
    else:
        DATA_FILE = Path('data.sql') if Path('data.sql').exists() else None
'''
                lines.insert(insert_idx, check_code)
                source_text = '\n'.join(lines)
        
        if source_text != original_text:
            cell['source'] = source_text.split('\n')
            # Ensure proper newline formatting
            for j in range(len(cell['source']) - 1):
                if cell['source'][j] and not cell['source'][j].endswith('\n'):
                    cell['source'][j] += '\n'
            modified = True
            print(f"   ✅ Updated schema/data loading in cell {i}")
    
    return modified

def fix_notebook(notebook_path: Path) -> bool:
    """Update schema/data loading in notebook."""
    print(f"\\nUpdating schema/data loading: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    
    if update_schema_loading(notebook):
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
        return True
    
    return False

def main():
    """Main execution."""
    print("="*80)
    print("UPDATING SCHEMA/DATA LOADING TO USE DETECTED PATHS")
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
    print("✅ SCHEMA/DATA LOADING UPDATED!")
    print("="*80)

if __name__ == '__main__':
    main()
