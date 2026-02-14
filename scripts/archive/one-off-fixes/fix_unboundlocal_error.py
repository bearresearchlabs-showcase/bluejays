#!/usr/bin/env python3
"""
Fix UnboundLocalError in ensure_paths_correct() function
The issue: Python sees BASE_DIR = ... later and treats it as local variable
Solution: Use globals()['BASE_DIR'] to access/modify instead of direct assignment
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
        
        # Check if this cell contains the problematic code
        if 'def ensure_paths_correct()' in source_text and ('BASE_DIR not in globals() or not BASE_DIR.exists()' in source_text or 'if \'BASE_DIR\' not in globals() or not BASE_DIR.exists()' in source_text):
            # Replace the problematic lines
            new_source_lines = []
            i = 0
            
            while i < len(source_lines):
                line = source_lines[i]
                line_text = line if isinstance(line, str) else ''
                
                # Fix BASE_DIR check and assignment - handle both quoted and unquoted versions
                if ('if \'BASE_DIR\' not in globals() or not BASE_DIR.exists()' in line_text or 
                    'if "BASE_DIR" not in globals() or not BASE_DIR.exists()' in line_text or
                    ('BASE_DIR' in line_text and 'not in globals()' in line_text and 'BASE_DIR.exists()' in line_text)):
                    # Replace with fixed version
                    new_source_lines.append('    # Correct BASE_DIR if needed - fix UnboundLocalError\n')
                    new_source_lines.append('    base_dir_exists = \'BASE_DIR\' in globals()\n')
                    new_source_lines.append('    base_dir_valid = False\n')
                    new_source_lines.append('    \n')
                    new_source_lines.append('    if base_dir_exists:\n')
                    new_source_lines.append('        try:\n')
                    new_source_lines.append('            base_dir_value = globals()[\'BASE_DIR\']\n')
                    new_source_lines.append('            if base_dir_value:\n')
                    new_source_lines.append('                base_dir_path = Path(base_dir_value) if isinstance(base_dir_value, str) else base_dir_value\n')
                    new_source_lines.append('                base_dir_valid = base_dir_path.exists()\n')
                    new_source_lines.append('        except:\n')
                    new_source_lines.append('            base_dir_valid = False\n')
                    new_source_lines.append('    \n')
                    new_source_lines.append('    if not base_dir_exists or not base_dir_valid:\n')
                    i += 1
                    # Skip the next line (BASE_DIR = ...)
                    if i < len(source_lines) and 'BASE_DIR = correct_file_path' in ''.join(source_lines[i]):
                        i += 1
                    # Replace assignment
                    new_source_lines.append('        corrected_base_dir = correct_file_path(Path(\'/Users/machine/Documents/AQ/db\'))\n')
                    new_source_lines.append('        globals()[\'BASE_DIR\'] = corrected_base_dir\n')
                    new_source_lines.append('        print(f"✅ BASE_DIR corrected: {corrected_base_dir}")\n')
                    new_source_lines.append('    else:\n')
                    new_source_lines.append('        print(f"✅ BASE_DIR valid: {globals()[\'BASE_DIR\']}")\n')
                    continue
                
                # Fix DB_DIR check and assignment - handle both quoted and unquoted versions
                if ('if \'DB_DIR\' in globals() and DB_DIR and not DB_DIR.exists()' in line_text or
                    'if "DB_DIR" in globals() and DB_DIR and not DB_DIR.exists()' in line_text or
                    ('DB_DIR' in line_text and 'in globals()' in line_text and 'DB_DIR.exists()' in line_text)):
                    # Replace with fixed version
                    new_source_lines.append('    # Correct DB_DIR if needed - fix UnboundLocalError\n')
                    new_source_lines.append('    db_dir_exists = \'DB_DIR\' in globals()\n')
                    new_source_lines.append('    db_dir_valid = False\n')
                    new_source_lines.append('    db_dir_value = None\n')
                    new_source_lines.append('    \n')
                    new_source_lines.append('    if db_dir_exists:\n')
                    new_source_lines.append('        try:\n')
                    new_source_lines.append('            db_dir_value = globals()[\'DB_DIR\']\n')
                    new_source_lines.append('            if db_dir_value:\n')
                    new_source_lines.append('                db_dir_path = Path(db_dir_value) if isinstance(db_dir_value, str) else db_dir_value\n')
                    new_source_lines.append('                db_dir_valid = db_dir_path.exists()\n')
                    new_source_lines.append('        except:\n')
                    new_source_lines.append('            db_dir_valid = False\n')
                    new_source_lines.append('    \n')
                    new_source_lines.append('    if db_dir_exists and db_dir_value and not db_dir_valid:\n')
                    i += 1
                    # Skip the next line (DB_DIR = ...)
                    if i < len(source_lines) and 'DB_DIR = correct_file_path' in ''.join(source_lines[i]):
                        i += 1
                    # Replace assignment
                    new_source_lines.append('        db_dir_path = Path(db_dir_value) if isinstance(db_dir_value, str) else db_dir_value\n')
                    new_source_lines.append('        corrected_db_dir = correct_file_path(db_dir_path)\n')
                    new_source_lines.append('        globals()[\'DB_DIR\'] = corrected_db_dir\n')
                    new_source_lines.append('        print(f"✅ DB_DIR corrected: {corrected_db_dir}")\n')
                    new_source_lines.append('    elif db_dir_exists and db_dir_value:\n')
                    new_source_lines.append('        print(f"✅ DB_DIR valid: {globals()[\'DB_DIR\']}")\n')
                    continue
                
                new_source_lines.append(line)
                i += 1
            
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
