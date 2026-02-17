#!/usr/bin/env python3
"""
Fix Python version in notebooks - update from 14.2 to 3.14.2
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

def fix_python_version_in_cell(cell_source: list) -> bool:
    """Fix Python version references in cell source."""
    modified = False
    source_text = ''.join(cell_source)
    
    # Replace Python 14.2 with Python 3.14.2
    replacements = [
        ('PYTHON 14.2', 'PYTHON 3.14.2'),
        ('Python 14.2', 'Python 3.14.2'),
        ('python=14.2', 'python=3.14.2'),
        ('python14.2', 'python3.14'),
        ('pyenv install 14.2', 'pyenv install 3.14.2'),
        ('pyenv global 14.2', 'pyenv global 3.14.2'),
        ('TARGET_MAJOR = 14', 'TARGET_MAJOR = 3'),
        ('TARGET_MINOR = 2', 'TARGET_MINOR = 14'),
        ('TARGET_MICRO = 2', 'TARGET_MICRO = 2'),
        ('current_version.minor == TARGET_MINOR', 'current_version.minor == TARGET_MINOR and current_version.micro == TARGET_MICRO'),
        ('current_version.major == TARGET_MAJOR and current_version.minor == TARGET_MINOR:', 'current_version.major == TARGET_MAJOR and current_version.minor == TARGET_MINOR and current_version.micro == TARGET_MICRO:'),
        ('final_version.major == TARGET_MAJOR and final_version.minor == TARGET_MINOR', 'final_version.major == TARGET_MAJOR and final_version.minor == TARGET_MINOR and final_version.micro == TARGET_MICRO'),
    ]
    
    new_source = source_text
    for old, new in replacements:
        if old in new_source:
            new_source = new_source.replace(old, new)
            modified = True
    
    if modified:
        # Split back into lines
        cell_source[:] = new_source.split('\n')
        # Add newline back to each line except last
        for i in range(len(cell_source) - 1):
            if cell_source[i] and not cell_source[i].endswith('\n'):
                cell_source[i] += '\n'
    
    return modified

def fix_notebook(notebook_path: Path) -> bool:
    """Fix Python version in notebook."""
    print(f"\nFixing Python version: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            if fix_python_version_in_cell(source):
                cell['source'] = source
                modified = True
                print(f"   ✅ Fixed cell {i}")
        
        elif cell['cell_type'] == 'markdown':
            source = cell.get('source', [])
            source_text = ''.join(source)
            if 'Python 14.2' in source_text or 'python 14.2' in source_text.lower():
                new_source = source_text.replace('Python 14.2', 'Python 3.14.2')
                new_source = new_source.replace('python 14.2', 'python 3.14.2')
                if new_source != source_text:
                    cell['source'] = new_source.split('\n')
                    # Add newlines back
                    for j in range(len(cell['source']) - 1):
                        if cell['source'][j] and not cell['source'][j].endswith('\n'):
                            cell['source'][j] += '\n'
                    modified = True
                    print(f"   ✅ Fixed markdown cell {i}")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("FIXING PYTHON VERSION IN NOTEBOOKS (14.2 -> 3.14.2)")
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
    
    print("\n" + "="*80)
    print(f"Updated notebooks: {fixed_count}")
    print("✅ PYTHON VERSION FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
