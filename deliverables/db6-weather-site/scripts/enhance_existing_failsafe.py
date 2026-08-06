#!/usr/bin/env python3
"""
Enhance existing failsafe in notebooks to include backup creation
"""

import json
import shutil
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')

BACKUP_CODE = '''
def create_notebook_backup(notebook_path=None):
    """Create backup of current notebook automatically."""
    try:
        # Try to detect notebook path from various sources
        if notebook_path is None:
            # Try to get from __file__ or current working directory
            try:
                notebook_path = Path(__file__)
            except:
                notebook_path = Path.cwd() / 'current_notebook.ipynb'
        
        if isinstance(notebook_path, str):
            notebook_path = Path(notebook_path)
        
        # Only create backup if file exists
        if notebook_path.exists() and notebook_path.suffix == '.ipynb':
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_path = notebook_path.parent / f"{notebook_path.stem}_{timestamp}.backup.ipynb"
            
            # Create backup
            shutil.copy2(notebook_path, backup_path)
            print(f"✅ Backup created: {backup_path.name}")
            return backup_path
        else:
            print("⚠️  Could not determine notebook path for backup")
            return None
    except Exception as e:
        print(f"⚠️  Backup creation failed (non-critical): {e}")
        return None

# Create backup at startup
try:
    create_notebook_backup()
except Exception as e:
    print(f"⚠️  Backup skipped: {e}")
'''

def enhance_notebook_failsafe(notebook_path: Path):
    """Enhance existing failsafe with backup functionality."""
    with open(notebook_path) as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    
    # Find failsafe cell
    failsafe_index = None
    has_backup = False
    
    for i, cell in enumerate(cells):
        source = ''.join(cell.get('source', []))
        if 'FAILSAFE: Force Path Correction' in source or 'FAILSAFE:' in source:
            failsafe_index = i
            if 'create_notebook_backup' in source:
                has_backup = True
            break
    
    if failsafe_index is None:
        print(f"  ⚠️  No failsafe found in {notebook_path.name}")
        return False
    
    if has_backup:
        print(f"  ✅ Backup function already exists in {notebook_path.name}")
        return False
    
    # Add backup code to failsafe cell
    failsafe_cell = cells[failsafe_index]
    source_lines = failsafe_cell.get('source', [])
    source_text = ''.join(source_lines)
    
    # Add imports if missing
    if 'import shutil' not in source_text:
        # Find import section
        import_end = 0
        for i, line in enumerate(source_lines):
            if 'from pathlib import Path' in line or 'import Path' in line:
                import_end = i + 1
                break
        
        # Insert shutil and datetime imports
        if 'import shutil' not in source_text:
            source_lines.insert(import_end, 'import shutil\n')
        if 'from datetime import datetime' not in source_text:
            source_lines.insert(import_end, 'from datetime import datetime\n')
    
    # Add backup code before "Run failsafe checks"
    check_start = None
    for i, line in enumerate(source_lines):
        if 'Run failsafe checks' in line or 'ensure_packages_installed()' in line:
            check_start = i
            break
    
    if check_start:
        # Insert backup code
        backup_lines = BACKUP_CODE.strip().split('\n')
        for i, line in enumerate(backup_lines):
            source_lines.insert(check_start + i, line + '\n')
    else:
        # Append at end of failsafe cell
        source_lines.extend(['\n'] + BACKUP_CODE.strip().split('\n'))
    
    failsafe_cell['source'] = source_lines
    
    # Create backup before updating
    backup_path = notebook_path.with_suffix('.ipynb.enhanced_backup')
    if not backup_path.exists():
        shutil.copy2(notebook_path, backup_path)
    
    # Write updated notebook
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print(f"  ✅ Enhanced failsafe with backup in {notebook_path.name}")
    return True

def main():
    """Enhance all notebooks."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str)
    parser.add_argument('--root-dir', type=str)
    parser.add_argument('--client-only', action='store_true')
    
    args = parser.parse_args()
    
    root_dir = Path(args.root_dir) if args.root_dir else BASE_DIR
    
    if args.client_only:
        directories = [BASE_DIR / 'client' / 'db']
    elif args.db:
        directories = [
            BASE_DIR / 'client' / 'db' / args.db,
            BASE_DIR / args.db
        ]
    else:
        directories = [BASE_DIR / 'client' / 'db', BASE_DIR]
    
    print("="*80)
    print("ENHANCING EXISTING FAILSAFE WITH BACKUP")
    print("="*80)
    
    total_enhanced = 0
    for directory in directories:
        if not directory.exists():
            continue
        
        print(f"\nProcessing: {directory.relative_to(BASE_DIR)}")
        for notebook_path in directory.rglob('*.ipynb'):
            if '.backup' in notebook_path.name:
                continue
            
            if enhance_notebook_failsafe(notebook_path):
                total_enhanced += 1
    
    print(f"\n{'='*80}")
    print(f"Enhanced: {total_enhanced} notebooks")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
