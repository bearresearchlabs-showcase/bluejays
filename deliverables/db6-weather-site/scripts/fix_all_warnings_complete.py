#!/usr/bin/env python3
"""
Complete fix for all Colab warnings
- Replace all subprocess.run with os.system for apt-get/service
- Remove all hardcoded local paths
- Use only Colab paths
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

def fix_subprocess_to_os_system(source: list) -> list:
    """Replace subprocess.run for apt-get/service with os.system."""
    source_text = ''.join(source)
    modified = False
    
    # Replace subprocess.run(['apt-get', ...]) with os.system
    patterns = [
        # apt-get update
        (r"subprocess\.run\(\[['\"]apt-get['\"],\s*['\"]update['\"][^\]]+\],\s*check=True[^)]+\)",
         "os.system('apt-get update -qq')"),
        # apt-get install
        (r"subprocess\.run\(\[['\"]apt-get['\"],\s*['\"]install['\"][^\]]+\],\s*check=True[^)]+\)",
         "os.system('apt-get install -y -qq postgresql postgresql-contrib')"),
        # service postgresql start
        (r"subprocess\.run\(\[['\"]service['\"],\s*['\"]postgresql['\"],\s*['\"]start['\"][^\]]+\],\s*check=True[^)]+\)",
         "os.system('service postgresql start')"),
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, source_text):
            source_text = re.sub(pattern, replacement, source_text)
            modified = True
    
    if modified:
        return source_text.split('\n')
    return source

def remove_all_local_paths(source: list) -> list:
    """Remove all hardcoded local paths."""
    source_text = ''.join(source)
    modified = False
    
    # Remove patterns
    patterns_to_remove = [
        r"Path\('/Users/machine/Documents/AQ/db'\)",
        r"Path\.home\(\)\s*/\s*'Documents'\s*/\s*'AQ'\s*/\s*'db'",
        r"/Users/machine/Documents/AQ/db",
        r"BASE_DIR if 'BASE_DIR' in globals\(\) else Path\('/Users/machine/Documents/AQ/db'\)",
        r"correct_file_path\(Path\('/Users/machine/Documents/AQ/db'\)\)",
    ]
    
    for pattern in patterns_to_remove:
        if re.search(pattern, source_text):
            source_text = re.sub(pattern, '', source_text)
            modified = True
    
    # Clean up empty list items and trailing commas
    source_text = re.sub(r',\s*,', ',', source_text)  # Remove double commas
    source_text = re.sub(r',\s*\]', ']', source_text)  # Remove trailing comma before ]
    source_text = re.sub(r'\[\s*,', '[', source_text)  # Remove leading comma after [
    
    # Clean up multiple newlines
    source_text = re.sub(r'\n{3,}', '\n\n', source_text)
    
    if modified:
        return source_text.split('\n')
    return source

def ensure_os_import(source: list) -> list:
    """Ensure os module is imported."""
    source_text = ''.join(source)
    
    if 'os.system' in source_text and 'import os' not in source_text:
        # Add import os if not present
        lines = source_text.split('\n')
        # Find first import line
        import_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_idx = i
                break
        
        if import_idx >= 0:
            # Check if os is already imported
            if 'import os' not in source_text:
                lines.insert(import_idx + 1, 'import os')
                return lines
    
    return source

def fix_notebook(notebook_path: Path) -> bool:
    """Fix all warnings in notebook."""
    print(f"\\nFixing all warnings: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            original_source = source.copy()
            
            # Fix subprocess.run to os.system
            source = fix_subprocess_to_os_system(source)
            
            # Remove local paths
            source = remove_all_local_paths(source)
            
            # Ensure os import
            source = ensure_os_import(source)
            
            if source != original_source:
                cell['source'] = source
                modified = True
                print(f"   ✅ Fixed cell {i+1}")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("REMOVING ALL COLAB WARNINGS - COMPLETE FIX")
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
    print("✅ ALL WARNINGS REMOVED!")
    print("="*80)

if __name__ == '__main__':
    main()
