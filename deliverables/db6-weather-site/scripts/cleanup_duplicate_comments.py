#!/usr/bin/env python3
"""
Clean up duplicate comments in fixed notebooks
"""

import json
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'

def cleanup_notebook(notebook_path: Path):
    """Remove duplicate comment lines."""
    with open(notebook_path) as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    fixed = False
    
    for cell in cells:
        if cell.get('cell_type') != 'code':
            continue
        
        source_lines = cell.get('source', [])
        new_source_lines = []
        prev_line = None
        
        for line in source_lines:
            line_text = line if isinstance(line, str) else ''
            # Skip duplicate comment lines
            if (line_text.strip() == '# Correct BASE_DIR if needed' and 
                prev_line and '# Correct BASE_DIR if needed' in prev_line):
                continue
            if (line_text.strip() == '# Correct DB_DIR if needed' and 
                prev_line and '# Correct DB_DIR if needed' in prev_line):
                continue
            new_source_lines.append(line)
            prev_line = line_text
        
        if len(new_source_lines) < len(source_lines):
            cell['source'] = new_source_lines
            fixed = True
    
    if fixed:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=1)
        return True
    
    return False

def main():
    """Clean all notebooks."""
    print("Cleaning up duplicate comments...")
    
    total_cleaned = 0
    for notebook_path in CLIENT_DB_DIR.rglob('*.ipynb'):
        if '.backup' in notebook_path.name:
            continue
        
        if cleanup_notebook(notebook_path):
            total_cleaned += 1
    
    print(f"Cleaned: {total_cleaned} notebooks")

if __name__ == '__main__':
    main()
