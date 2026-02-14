#!/usr/bin/env python3
"""
Fix cell 11 syntax errors - queries loading cell
"""

import json
import re
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

def fix_queries_loading_cell(code: str) -> str:
    """Fix the queries loading cell code."""
    # Fix comment headers first
    code = re.sub(r'(# =+)(#)', r'\1\n\2', code)  # Split # =====# into # =====\n#
    code = re.sub(r'(# [A-Z][^#]+)(#)', r'\1\n\2', code)  # Split comment text from next #
    
    # Fix all the patterns
    patterns = [
        (r'(# =+[^=]+=+)(queries_file)', r'\1\n\2'),
        (r"('queries\.json')(if\s+not)", r'\1\n\2'),
        (r'(queries_file)(if\s+not)', r'\1\n\2'),
        (r'(find_file_recursively\([^)]+\))(if\s+not)', r'\1\n\2'),
        (r'(find_file_recursively\([^)]+\))(queries_file)', r'\1\n\2'),
        (r"('queries\.json')(with\s+open)", r'\1\n\2'),
        (r'(\.exists\(\))(with\s+open)', r'\1\n\2'),
        (r'(\.exists\(\))(raise)', r'\1\n\2'),
        (r'(raise\s+[^)]+\))(with\s+open)', r'\1\n\2'),
        (r'(json\.load\(f\))(queries)', r'\1\n\2'),
        (r"(queries_data\.get\('queries', \[\]\))(total_queries)", r'\1\n\2'),
        (r'(len\(queries\))(print)', r'\1\n\2'),
        (r'(print\([^)]+\))(print)', r'\1\n\2'),
        (r'(print\([^)]+\))(for\s+q)', r'\1\n\2'),
        (r'(print\([^)]+\))(if\s+total_queries)', r'\1\n\2'),
        (r"(\])(print)", r'\1\n\2'),
        (r"(\])(for\s+q)", r'\1\n\2'),
        (r"(\])(if\s+)", r'\1\n\2'),
    ]
    
    for pattern, replacement in patterns:
        code = re.sub(pattern, replacement, code)
    
    # Clean up excessive whitespace/newlines
    code = re.sub(r'\n{4,}', '\n\n\n', code)
    code = re.sub(r' {4,}', '    ', code)  # Normalize indentation
    
    return code

def fix_notebook(notebook_path: Path) -> bool:
    """Fix notebook."""
    print(f"\\nFixing: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    # Find code cells
    code_cells = [i for i, c in enumerate(notebook['cells']) if c['cell_type'] == 'code']
    
    # Fix cell 11 (index 10 if 0-based, but check for queries loading)
    for i, cell_idx in enumerate(code_cells):
        cell = notebook['cells'][cell_idx]
        source = ''.join(cell.get('source', []))
        
        # Check if this is the queries loading cell
        if 'LOAD QUERY METADATA' in source or ('queries.json' in source and 'queries_data' in source):
            fixed = fix_queries_loading_cell(source)
            if fixed != source:
                cell['source'] = fixed.split('\n')
                modified = True
                print(f"   ✅ Fixed queries loading cell (cell {i+1})")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("FIXING QUERIES LOADING CELL SYNTAX")
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
    print("✅ QUERIES LOADING CELL FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
