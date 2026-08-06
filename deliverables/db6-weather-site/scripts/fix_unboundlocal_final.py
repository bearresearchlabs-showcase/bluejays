#!/usr/bin/env python3
"""
Final fix for UnboundLocalError - remove duplicate lines and old code
"""

import json
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'
ROOT_DB_DIR = BASE_DIR

DATABASES = [f'db-{i}' for i in range(6, 16)]

def fix_notebook_final(notebook_path: Path):
    """Remove duplicate lines and old problematic code."""
    with open(notebook_path) as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    fixed = False
    
    for cell in cells:
        if cell.get('cell_type') != 'code':
            continue
        
        source_lines = cell.get('source', [])
        source_text = ''.join(source_lines)
        
        # Check if this cell has the issue
        if 'def ensure_paths_correct()' in source_text and 'base_dir_exists =' in source_text:
            # Remove duplicate comment and old print statement
            new_source_lines = []
            i = 0
            skip_next = False
            
            while i < len(source_lines):
                line = source_lines[i]
                line_text = line if isinstance(line, str) else ''
                
                # Skip duplicate comment
                if line_text.strip() == '# Correct BASE_DIR if needed' and i > 0:
                    prev = source_lines[i-1] if i > 0 else ''
                    if isinstance(prev, str) and '# Correct BASE_DIR if needed' in prev:
                        i += 1
                        continue
                
                # Skip duplicate comment for DB_DIR
                if line_text.strip() == '# Correct DB_DIR if needed' and i > 0:
                    prev = source_lines[i-1] if i > 0 else ''
                    if isinstance(prev, str) and '# Correct DB_DIR if needed' in prev:
                        i += 1
                        continue
                
                # Remove old print statement that uses BASE_DIR directly
                if 'print(f"✅ BASE_DIR corrected: {BASE_DIR}")' in line_text:
                    # Skip this line - we already have the fixed version
                    i += 1
                    continue
                
                new_source_lines.append(line)
                i += 1
            
            if len(new_source_lines) < len(source_lines):
                cell['source'] = new_source_lines
                fixed = True
    
    if fixed:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=1)
        return True
    
    return False

def main():
    """Fix all notebooks."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str)
    parser.add_argument('--client-only', action='store_true')
    
    args = parser.parse_args()
    
    if args.client_only:
        directories = [CLIENT_DB_DIR]
    elif args.db:
        directories = [CLIENT_DB_DIR / args.db, ROOT_DB_DIR / args.db]
    else:
        directories = [CLIENT_DB_DIR, ROOT_DB_DIR]
    
    print("="*80)
    print("FINAL CLEANUP: REMOVING DUPLICATES AND OLD CODE")
    print("="*80)
    
    total_fixed = 0
    for directory in directories:
        if not directory.exists():
            continue
        
        print(f"\nProcessing: {directory.relative_to(BASE_DIR)}")
        for notebook_path in directory.rglob('*.ipynb'):
            if '.backup' in notebook_path.name:
                continue
            
            if fix_notebook_final(notebook_path):
                print(f"  ✅ Cleaned: {notebook_path.name}")
                total_fixed += 1
    
    print(f"\n{'='*80}")
    print(f"CLEANUP COMPLETE")
    print(f"{'='*80}")
    print(f"Notebooks cleaned: {total_fixed}")

if __name__ == '__main__':
    main()
