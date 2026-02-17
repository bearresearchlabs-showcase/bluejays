#!/usr/bin/env python3
"""
Aggressively fix notebook syntax errors - fix all missing newlines
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

def fix_missing_newlines(code: str) -> str:
    """Aggressively fix missing newlines."""
    if not code:
        return code
    
    # If code has very few newlines relative to length, it's likely broken
    if len(code) > 200 and code.count('\n') < len(code) / 100:
        # Split on common patterns that should have newlines after
        
        # Pattern 1: )with open, )if not, )for, )print
        code = re.sub(r'(\))(with\s+open)', r'\1\n\2', code)
        code = re.sub(r'(\))(if\s+not)', r'\1\n\2', code)
        code = re.sub(r'(\))(for\s+)', r'\1\n\2', code)
        code = re.sub(r'(\))(print)', r'\1\n\2', code)
        code = re.sub(r'(\))(queries)', r'\1\n\2', code)
        code = re.sub(r'(\))(total_queries)', r'\1\n\2', code)
        
        # Pattern 2: ])queries, ])total_queries, ])print
        code = re.sub(r'(\])(queries)', r'\1\n\2', code)
        code = re.sub(r'(\])(total_queries)', r'\1\n\2', code)
        code = re.sub(r'(\])(print)', r'\1\n\2', code)
        code = re.sub(r'(\])(for\s+)', r'\1\n\2', code)
        code = re.sub(r'(\])(if\s+)', r'\1\n\2', code)
        
        # Pattern 3: 'queries.json'if not, 'queries.json'with open
        code = re.sub(r"('queries\.json')(if\s+not)", r'\1\n\2', code)
        code = re.sub(r"('queries\.json')(with\s+open)", r'\1\n\2', code)
        
        # Pattern 4: raise ...)with open
        code = re.sub(r'(raise\s+[^)]+\))(with\s+open)', r'\1\n\2', code)
        code = re.sub(r'(raise\s+[^)]+\))(queries)', r'\1\n\2', code)
        
        # Pattern 5: json.load(f)queries
        code = re.sub(r'(json\.load\(f\))(queries)', r'\1\n\2', code)
        code = re.sub(r'(json\.load\(f\))(total_queries)', r'\1\n\2', code)
        code = re.sub(r'(json\.load\(f\))(print)', r'\1\n\2', code)
        
        # Pattern 6: queries_data.get(...)total_queries
        code = re.sub(r'(queries_data\.get\([^)]+\))(total_queries)', r'\1\n\2', code)
        code = re.sub(r'(queries_data\.get\([^)]+\))(print)', r'\1\n\2', code)
        
        # Pattern 7: len(queries)print
        code = re.sub(r'(len\(queries\))(print)', r'\1\n\2', code)
        code = re.sub(r'(len\(queries\))(for\s+)', r'\1\n\2', code)
        
        # Pattern 8: print(...)if total_queries, print(...)for q
        code = re.sub(r'(print\([^)]+\))(if\s+total_queries)', r'\1\n\2', code)
        code = re.sub(r'(print\([^)]+\))(for\s+q)', r'\1\n\2', code)
        code = re.sub(r'(print\([^)]+\))(print)', r'\1\n\2', code)
        
        # Pattern 9: Function definitions without newline after :
        code = re.sub(r'(def\s+\w+\([^)]*\):\s*)([a-zA-Z_])', r'\1\n    \2', code)
        code = re.sub(r'(def\s+\w+\([^)]*\):\s*)(if\s+)', r'\1\n    \2', code)
        code = re.sub(r'(def\s+\w+\([^)]*\):\s*)(return)', r'\1\n    \2', code)
        
        # Pattern 10: Control flow without newline after :
        code = re.sub(r'(if\s+[^:]+:\s*)([a-zA-Z_])', r'\1\n    \2', code)
        code = re.sub(r'(except\s+[^:]*:\s*)([a-zA-Z_])', r'\1\n    \2', code)
        code = re.sub(r'(try:\s*)([a-zA-Z_])', r'\1\n    \2', code)
        code = re.sub(r'(for\s+[^:]+:\s*)([a-zA-Z_])', r'\1\n    \2', code)
        
        # Pattern 11: Assignment followed by code
        code = re.sub(r'(\w+\s*=\s*[^\n]+)(if\s+not)', r'\1\n\2', code)
        code = re.sub(r'(\w+\s*=\s*[^\n]+)(with\s+open)', r'\1\n\2', code)
        code = re.sub(r'(\w+\s*=\s*[^\n]+)(for\s+)', r'\1\n\2', code)
        code = re.sub(r'(\w+\s*=\s*[^\n]+)(print)', r'\1\n\2', code)
        
        # Clean up excessive newlines
        code = re.sub(r'\n{4,}', '\n\n\n', code)
    
    return code

def fix_notebook(notebook_path: Path) -> bool:
    """Fix notebook syntax."""
    print(f"\\nFixing: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            full_code = ''.join(source)
            
            fixed_code = fix_missing_newlines(full_code)
            
            if fixed_code != full_code:
                # Split into lines
                cell['source'] = fixed_code.split('\n')
                modified = True
                print(f"   ✅ Fixed cell {i+1}")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("AGGRESSIVELY FIXING NOTEBOOK SYNTAX")
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
    print("✅ SYNTAX FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
