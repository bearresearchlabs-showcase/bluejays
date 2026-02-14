#!/usr/bin/env python3
"""
Complete fix for UnboundLocalError - replace entire ensure_paths_correct function
"""

import json
import re
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'
ROOT_DB_DIR = BASE_DIR

DATABASES = [f'db-{i}' for i in range(6, 16)]

FIXED_FUNCTION = '''def ensure_paths_correct():
    """Ensure all file paths are correct."""
    print("\\n" + "="*80)
    print("FAILSAFE: Correcting file paths...")
    print("="*80)
    
    # Correct BASE_DIR if needed - fix UnboundLocalError
    base_dir_exists = 'BASE_DIR' in globals()
    base_dir_valid = False
    
    if base_dir_exists:
        try:
            base_dir_value = globals()['BASE_DIR']
            if base_dir_value:
                base_dir_path = Path(base_dir_value) if isinstance(base_dir_value, str) else base_dir_value
                base_dir_valid = base_dir_path.exists()
        except:
            base_dir_valid = False
    
    if not base_dir_exists or not base_dir_valid:
        corrected_base_dir = correct_file_path(Path('/Users/machine/Documents/AQ/db'))
        globals()['BASE_DIR'] = corrected_base_dir
        print(f"✅ BASE_DIR corrected: {corrected_base_dir}")
    else:
        print(f"✅ BASE_DIR valid: {globals()['BASE_DIR']}")
    
    # Correct DB_DIR if needed - fix UnboundLocalError
    db_dir_exists = 'DB_DIR' in globals()
    db_dir_valid = False
    db_dir_value = None
    
    if db_dir_exists:
        try:
            db_dir_value = globals()['DB_DIR']
            if db_dir_value:
                db_dir_path = Path(db_dir_value) if isinstance(db_dir_value, str) else db_dir_value
                db_dir_valid = db_dir_path.exists()
        except:
            db_dir_valid = False
    
    if db_dir_exists and db_dir_value and not db_dir_valid:
        db_dir_path = Path(db_dir_value) if isinstance(db_dir_value, str) else db_dir_value
        corrected_db_dir = correct_file_path(db_dir_path)
        globals()['DB_DIR'] = corrected_db_dir
        print(f"✅ DB_DIR corrected: {corrected_db_dir}")
    elif db_dir_exists and db_dir_value:
        print(f"✅ DB_DIR valid: {globals()['DB_DIR']}")
    
    print("="*80 + "\\n")'''

def fix_notebook_complete(notebook_path: Path):
    """Replace entire ensure_paths_correct function."""
    with open(notebook_path) as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    fixed = False
    
    for cell in cells:
        if cell.get('cell_type') != 'code':
            continue
        
        source_lines = cell.get('source', [])
        source_text = ''.join(source_lines)
        
        # Check if this cell has ensure_paths_correct
        if 'def ensure_paths_correct()' in source_text:
            # Find function boundaries
            func_start = None
            func_end = None
            
            for i, line in enumerate(source_lines):
                line_text = line if isinstance(line, str) else ''
                if 'def ensure_paths_correct():' in line_text:
                    func_start = i
                    # Find function end (next def or comment that's not indented)
                    indent = len(line_text) - len(line_text.lstrip())
                    for j in range(i + 1, len(source_lines)):
                        next_line = source_lines[j]
                        next_text = next_line if isinstance(next_line, str) else ''
                        if next_text.strip():
                            next_indent = len(next_text) - len(next_text.lstrip())
                            # End of function: next def, or unindented comment/code
                            if (next_indent <= indent and 
                                (next_text.strip().startswith('def ') or 
                                 next_text.strip().startswith('# Run failsafe') or
                                 next_text.strip().startswith('ensure_packages_installed()') or
                                 next_text.strip().startswith('ensure_paths_correct()'))):
                                func_end = j
                                break
                    if func_end is None:
                        func_end = len(source_lines)
                    break
            
            if func_start is not None:
                # Replace function
                new_source_lines = source_lines[:func_start]
                # Add fixed function
                new_source_lines.extend([line + '\n' for line in FIXED_FUNCTION.split('\n')])
                # Add rest of cell
                new_source_lines.extend(source_lines[func_end:])
                
                cell['source'] = new_source_lines
                fixed = True
                break
    
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
    print("COMPLETE FIX: REPLACING ENTIRE FUNCTION")
    print("="*80)
    
    total_fixed = 0
    for directory in directories:
        if not directory.exists():
            continue
        
        print(f"\nProcessing: {directory.relative_to(BASE_DIR)}")
        for notebook_path in directory.rglob('*.ipynb'):
            if '.backup' in notebook_path.name:
                continue
            
            if fix_notebook_complete(notebook_path):
                print(f"  ✅ Fixed: {notebook_path.name}")
                total_fixed += 1
    
    print(f"\n{'='*80}")
    print(f"FIXES COMPLETE")
    print(f"{'='*80}")
    print(f"Notebooks fixed: {total_fixed}")

if __name__ == '__main__':
    main()
