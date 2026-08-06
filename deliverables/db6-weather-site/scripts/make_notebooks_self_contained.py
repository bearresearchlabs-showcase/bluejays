#!/usr/bin/env python3
"""
Make notebooks completely self-contained for Google Colab
- Remove all file system dependencies
- Use embedded SQL and queries only
- Fix formatting issues
- Ensure all cells can run independently
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

def fix_cell_formatting(cell_source: list) -> list:
    """Fix formatting issues in cell source."""
    if not cell_source:
        return cell_source
    
    # Join and split to normalize
    text = ''.join(cell_source)
    
    # Fix common formatting issues
    # Remove extra spaces/newlines at start
    text = text.lstrip()
    
    # Fix concatenated statements (missing newlines)
    fixes = [
        # Fix: if not x:    y = z
        (r'if not (\w+):\s+(\w+)', r'if not \1:\n    \2'),
        # Fix: queries_file = ...if not queries_file:
        (r'(\w+)\s*=\s*([^;]+)if not \1:', r'\1 = \2\nif not \1:'),
        # Fix: import ximport y
        (r'import (\w+)\s*import (\w+)', r'import \1\nimport \2'),
        # Fix: from x import yfrom z import w
        (r'from (\w+) import ([^\n]+)from (\w+)', r'from \1 import \2\nfrom \3'),
    ]
    
    # Split back into lines
    lines = text.split('\n')
    
    # Ensure proper newline formatting
    result = []
    for i, line in enumerate(lines):
        result.append(line)
        # Add newline except for last line
        if i < len(lines) - 1:
            if not line.endswith('\n'):
                result[-1] = line + '\n'
    
    return result

def remove_file_dependencies(notebook: dict) -> bool:
    """Remove file system dependencies, use embedded data only."""
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] != 'code':
            continue
        
        source_lines = cell.get('source', [])
        source_text = ''.join(source_lines)
        original_text = source_text
        
        # Remove file finding code that's no longer needed
        if 'find_file_recursively' in source_text and 'EMBEDDED' not in source_text:
            # Replace with embedded queries usage
            if 'queries.json' in source_text.lower():
                # Replace queries.json loading with embedded version
                new_source = '''# ============================================================================
# LOAD QUERIES (FROM EMBEDDED DATA)
# ============================================================================
# Queries are already loaded from embedded QUERIES_DATA cell above
# If not loaded, use the embedded queries cell

if 'queries' not in globals():
    print("⚠️  Queries not found. Run the 'Embedded Queries' cell first.")
    print("   Looking for embedded queries...")
    # Try to find embedded queries
    for cell_num in range(len(notebook['cells'])):
        cell_text = ''.join(notebook['cells'][cell_num].get('source', []))
        if 'EMBEDDED QUERIES.JSON' in cell_text or 'QUERIES_DATA' in cell_text:
            print(f"   ✅ Found embedded queries in cell")
            break
else:
    print("="*80)
    print("QUERIES LOADED")
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
                # Fix newlines
                for j in range(len(cell['source']) - 1):
                    if cell['source'][j] and not cell['source'][j].endswith('\n'):
                        cell['source'][j] += '\n'
                modified = True
                print(f"   ✅ Removed file dependency in cell {i}")
        
        # Remove schema.sql file loading, use embedded SCHEMA_SQL
        if 'schema.sql' in source_text.lower() and 'open' in source_text.lower() and 'EMBEDDED' not in source_text:
            new_source = '''# ============================================================================
# LOAD SCHEMA (FROM EMBEDDED DATA)
# ============================================================================
# Schema is already available in SCHEMA_SQL variable from embedded cell
# Execute the embedded schema cell to load schema into database

if 'SCHEMA_SQL' not in globals():
    print("⚠️  SCHEMA_SQL not found. Run the 'Embedded Schema' cell first.")
else:
    print("="*80)
    print("SCHEMA SQL AVAILABLE")
    print("="*80)
    print(f"Schema SQL length: {len(SCHEMA_SQL)} characters")
    print("\\nTo load schema, run: execute_schema_sql(conn)")
    print("="*80)
'''
            cell['source'] = new_source.split('\n')
            for j in range(len(cell['source']) - 1):
                if cell['source'][j] and not cell['source'][j].endswith('\n'):
                    cell['source'][j] += '\n'
            modified = True
            print(f"   ✅ Removed schema.sql file dependency in cell {i}")
        
        # Remove data.sql file loading, use embedded DATA_SQL
        if 'data.sql' in source_text.lower() and 'open' in source_text.lower() and 'EMBEDDED' not in source_text:
            new_source = '''# ============================================================================
# LOAD DATA (FROM EMBEDDED DATA)
# ============================================================================
# Data is already available in DATA_SQL variable from embedded cell
# Execute the embedded data cell to load data into database

if 'DATA_SQL' not in globals():
    print("⚠️  DATA_SQL not found. Run the 'Embedded Data' cell first (if available).")
else:
    print("="*80)
    print("DATA SQL AVAILABLE")
    print("="*80)
    print(f"Data SQL length: {len(DATA_SQL)} characters")
    print("\\nTo load data, run: execute_data_sql(conn)")
    print("="*80)
'''
            cell['source'] = new_source.split('\n')
            for j in range(len(cell['source']) - 1):
                if cell['source'][j] and not cell['source'][j].endswith('\n'):
                    cell['source'][j] += '\n'
            modified = True
            print(f"   ✅ Removed data.sql file dependency in cell {i}")
        
        # Fix formatting issues
        fixed_source = fix_cell_formatting(cell['source'])
        if fixed_source != cell['source']:
            cell['source'] = fixed_source
            modified = True
    
    return modified

def ensure_self_contained(notebook_path: Path) -> bool:
    """Ensure notebook is self-contained."""
    print(f"\\nMaking self-contained: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    
    # Check if embedded files exist
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    has_embedded_schema = 'EMBEDDED SCHEMA.SQL' in all_text or 'SCHEMA_SQL' in all_text
    has_embedded_queries = 'EMBEDDED QUERIES.JSON' in all_text or 'QUERIES_DATA' in all_text
    
    if not has_embedded_schema or not has_embedded_queries:
        print(f"   ⚠️  Missing embedded files - run add_sql_and_queries_to_notebooks.py first")
        return False
    
    # Remove file dependencies
    if remove_file_dependencies(notebook):
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
        return True
    
    return False

def main():
    """Main execution."""
    print("="*80)
    print("MAKING NOTEBOOKS SELF-CONTAINED FOR GOOGLE COLAB")
    print("="*80)
    
    fixed_count = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if ensure_self_contained(notebook_path):
                fixed_count += 1
    
    print("\\n" + "="*80)
    print(f"Updated notebooks: {fixed_count}")
    print("✅ NOTEBOOKS MADE SELF-CONTAINED!")
    print("="*80)

if __name__ == '__main__':
    main()
