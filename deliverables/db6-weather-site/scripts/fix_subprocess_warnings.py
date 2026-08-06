#!/usr/bin/env python3
"""
Replace subprocess.run with os.system for apt-get and service commands
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

def replace_subprocess_with_os_system(source: list) -> list:
    """Replace subprocess.run calls with os.system."""
    source_text = ''.join(source)
    original = source_text
    modified = False
    
    # Pattern 1: subprocess.run(['apt-get', 'update', ...])
    pattern1 = r"subprocess\.run\(\[['\"]apt-get['\"],\s*['\"]update['\"][^\]]*\],\s*check=True[^)]*\)"
    if re.search(pattern1, source_text):
        source_text = re.sub(pattern1, "os.system('apt-get update -qq')", source_text)
        modified = True
    
    # Pattern 2: subprocess.run(['apt-get', 'install', ...])
    pattern2 = r"subprocess\.run\(\[['\"]apt-get['\"],\s*['\"]install['\"][^\]]*\],\s*check=True[^)]*\)"
    if re.search(pattern2, source_text):
        source_text = re.sub(pattern2, "os.system('apt-get install -y -qq postgresql postgresql-contrib')", source_text)
        modified = True
    
    # Pattern 3: subprocess.run(['service', 'postgresql', 'start', ...])
    pattern3 = r"subprocess\.run\(\[['\"]service['\"],\s*['\"]postgresql['\"],\s*['\"]start['\"][^\]]*\],\s*check=True[^)]*\)"
    if re.search(pattern3, source_text):
        source_text = re.sub(pattern3, "os.system('service postgresql start')", source_text)
        modified = True
    
    # Ensure os is imported
    if modified and 'import os' not in source_text and 'from os import' not in source_text:
        # Add import os
        lines = source_text.split('\n')
        # Find where to insert (after other imports)
        insert_idx = 0
        for i, line in enumerate(lines):
            if 'import subprocess' in line or 'import time' in line:
                insert_idx = i + 1
                break
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_idx = i + 1
        
        lines.insert(insert_idx, 'import os')
        source_text = '\n'.join(lines)
    
    if modified:
        return source_text.split('\n')
    return source

def fix_notebook(notebook_path: Path) -> bool:
    """Fix notebook."""
    print(f"\\nFixing subprocess warnings: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            fixed_source = replace_subprocess_with_os_system(source)
            
            if fixed_source != source:
                cell['source'] = fixed_source
                modified = True
                print(f"   ✅ Fixed cell {i+1}")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("REPLACING SUBPROCESS.RUN WITH OS.SYSTEM")
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
    print("✅ SUBPROCESS WARNINGS FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
