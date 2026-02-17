#!/usr/bin/env python3
"""
Fix UnboundLocalError in failsafe code for BASE_DIR and DB_DIR
The issue is that Python treats BASE_DIR as local when it sees BASE_DIR = ... later in the function
"""

import json
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'
ROOT_DB_DIR = BASE_DIR

DATABASES = [f'db-{i}' for i in range(6, 16)]

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

FIXED_ENSURE_PATHS_CODE = '''def ensure_paths_correct():
    """Ensure all file paths are correct."""
    print("\\n" + "="*80)
    print("FAILSAFE: Correcting file paths...")
    print("="*80)
    
    # Correct BASE_DIR if needed - fix UnboundLocalError by checking globals() first
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

def fix_notebook_failsafe(notebook_path: Path):
    """Fix UnboundLocalError in notebook failsafe code."""
    with open(notebook_path) as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    fixed = False
    
    for cell in cells:
        if cell.get('cell_type') != 'code':
            continue
        
        source_lines = cell.get('source', [])
        source_text = ''.join(source_lines)
        
        # Check if this is the failsafe cell with the bug
        if 'def ensure_paths_correct()' in source_text and ('BASE_DIR not in globals() or not BASE_DIR.exists()' in source_text or 'UnboundLocalError' in source_text):
            # Find the function and replace it
            new_source_lines = []
            i = 0
            in_function = False
            function_start = -1
            function_indent = 0
            
            while i < len(source_lines):
                line = source_lines[i]
                line_text = line if isinstance(line, str) else ''
                
                # Find function start
                if 'def ensure_paths_correct():' in line_text:
                    function_start = i
                    function_indent = len(line_text) - len(line_text.lstrip())
                    in_function = True
                    # Add fixed function code
                    fixed_lines = FIXED_ENSURE_PATHS_CODE.strip().split('\n')
                    new_source_lines.extend([l + '\n' for l in fixed_lines])
                    # Skip to end of function
                    i += 1
                    while i < len(source_lines):
                        next_line = source_lines[i]
                        next_text = next_line if isinstance(next_line, str) else ''
                        # Check if we've reached the end of the function
                        if next_text.strip():
                            # Check if it's a new function or code block at same/lesser indent
                            current_indent = len(next_text) - len(next_text.lstrip())
                            if current_indent <= function_indent and (next_text.strip().startswith('def ') or next_text.strip().startswith('# Run failsafe') or next_text.strip().startswith('ensure_packages_installed()') or next_text.strip().startswith('ensure_paths_correct()')):
                                break
                        i += 1
                    continue
                
                if not in_function:
                    new_source_lines.append(line)
                i += 1
            
            if function_start >= 0:
                cell['source'] = new_source_lines
                fixed = True
                break
    
    if fixed:
        # Create backup
        backup_path = notebook_path.with_suffix('.ipynb.unboundlocal_fix_backup')
        if not backup_path.exists():
            with open(backup_path, 'w') as f:
                json.dump(json.load(open(notebook_path)), f, indent=1)
        
        # Write fixed notebook
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=1)
        
        return True
    
    return False

def main():
    """Fix all notebooks."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str)
    parser.add_argument('--root-dir', type=str)
    parser.add_argument('--client-only', action='store_true')
    
    args = parser.parse_args()
    
    root_dir = Path(args.root_dir) if args.root_dir else BASE_DIR
    
    if args.client_only:
        directories = [CLIENT_DB_DIR]
    elif args.db:
        deliverable = DB_TO_DELIVERABLE.get(args.db)
        if deliverable:
            directories = [
                CLIENT_DB_DIR / args.db / deliverable,
                ROOT_DB_DIR / args.db
            ]
        else:
            directories = [ROOT_DB_DIR / args.db]
    else:
        directories = [CLIENT_DB_DIR, ROOT_DB_DIR]
    
    print("="*80)
    print("FIXING UNBOUNDLOCALERROR IN FAILSAFE CODE")
    print("="*80)
    
    total_fixed = 0
    for directory in directories:
        if not directory.exists():
            continue
        
        print(f"\nProcessing: {directory.relative_to(BASE_DIR)}")
        for notebook_path in directory.rglob('*.ipynb'):
            if '.backup' in notebook_path.name:
                continue
            
            if fix_notebook_failsafe(notebook_path):
                print(f"  ✅ Fixed: {notebook_path.name}")
                total_fixed += 1
    
    print(f"\n{'='*80}")
    print(f"FIXES COMPLETE")
    print(f"{'='*80}")
    print(f"Notebooks fixed: {total_fixed}")

if __name__ == '__main__':
    main()
