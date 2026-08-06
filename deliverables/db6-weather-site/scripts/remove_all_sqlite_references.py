#!/usr/bin/env python3
"""
Remove all SQLite references from notebooks
"""

import json
from pathlib import Path

def detect_base_dir():
    """Detect base directory."""
    cwd = Path.cwd()
    if cwd.name == 'scripts' and (cwd.parent / 'db-6').exists():
        return cwd.parent
    return cwd.parent if (cwd.parent / 'db-6').exists() else cwd

BASE_DIR = detect_base_dir()
DATABASES = [f'db-{i}' for i in range(6, 16)]

def remove_sqlite_from_cell(cell_source: list) -> list:
    """Remove SQLite references from cell source."""
    new_source = []
    
    for line in cell_source:
        # Skip any line containing SQLite (case-insensitive)
        if 'sqlite' in line.lower():
            # Only keep if it's explicitly about NOT using SQLite
            if 'no sqlite' in line.lower() or 'not sqlite' in line.lower():
                new_source.append(line)
            # Skip all other SQLite references
            continue
        new_source.append(line)
    
    return new_source

def fix_notebook(notebook_path: Path) -> bool:
    """Remove SQLite references from notebook."""
    print(f"\\nCleaning: {notebook_path.name}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    updated = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            if any('sqlite' in line.lower() for line in source):
                new_source = remove_sqlite_from_cell(source)
                if new_source != source:
                    cell['source'] = new_source
                    updated = True
                    print(f"   ✅ Removed SQLite references (cell {i+1})")
        elif cell['cell_type'] == 'markdown':
            source = cell.get('source', [])
            if any('sqlite' in line.lower() for line in source):
                # Remove SQLite mentions from markdown
                new_source = [line for line in source if 'sqlite' not in line.lower()]
                if new_source != source:
                    cell['source'] = new_source
                    updated = True
                    print(f"   ✅ Removed SQLite mentions (cell {i+1})")
    
    if updated:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"   ✅ Saved cleaned notebook")
        return True
    
    return False

def main():
    """Main execution."""
    print("="*80)
    print("REMOVING ALL SQLITE REFERENCES")
    print("="*80)
    
    updated_count = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if fix_notebook(notebook_path):
                updated_count += 1
    
    # Fix client notebooks
    client_db_dir = BASE_DIR / 'client' / 'db'
    if client_db_dir.exists():
        for db_name in DATABASES:
            for deliverable_dir in client_db_dir.glob(f"{db_name}/*"):
                if deliverable_dir.is_dir():
                    notebook_path = deliverable_dir / f"{db_name}.ipynb"
                    if notebook_path.exists():
                        if fix_notebook(notebook_path):
                            updated_count += 1
    
    print("\\n" + "="*80)
    print(f"Cleaned notebooks: {updated_count}")
    print("✅ All SQLite references removed!")

if __name__ == '__main__':
    main()
