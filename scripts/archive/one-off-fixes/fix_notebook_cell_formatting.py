#!/usr/bin/env python3
"""
Fix all formatting issues in notebook cells for Google Colab compatibility
- Fix missing newlines
- Fix concatenated statements
- Ensure proper Python syntax
- Fix indentation issues
"""

import json
import ast
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

def fix_cell_source(source_lines: list) -> list:
    """Fix formatting in cell source lines."""
    if not source_lines:
        return source_lines
    
    # Join all lines
    text = ''.join(source_lines)
    
    # Common fixes for concatenated code
    fixes = [
        # Fix: variable = valueif not variable:
        (r'(\w+)\s*=\s*([^\n]+)if not \1:', r'\1 = \2\nif not \1:'),
        # Fix: import ximport y
        (r'import (\w+)\s*import (\w+)', r'import \1\nimport \2'),
        # Fix: from x import yfrom z import w  
        (r'from (\w+) import ([^\n]+)from (\w+)', r'from \1 import \2\nfrom \3'),
        # Fix: print("x")print("y")
        (r'print\(([^)]+)\)print\(', r'print(\1)\nprint('),
        # Fix: if condition:    statement
        (r'if ([^:]+):\s+([^\n]+)(?=\n|$)', r'if \1:\n    \2'),
        # Fix: try:    statement
        (r'try:\s+([^\n]+)(?=\n|$)', r'try:\n    \1'),
        # Fix: except:    statement
        (r'except([^:]+):\s+([^\n]+)(?=\n|$)', r'except\1:\n    \2'),
        # Fix: for x in y:    statement
        (r'for ([^:]+):\s+([^\n]+)(?=\n|$)', r'for \1:\n    \2'),
        # Fix: while condition:    statement
        (r'while ([^:]+):\s+([^\n]+)(?=\n|$)', r'while \1:\n    \2'),
    ]
    
    import re
    for pattern, replacement in fixes:
        text = re.sub(pattern, replacement, text)
    
    # Split back into lines
    lines = text.split('\n')
    
    # Ensure proper newline formatting
    result = []
    for i, line in enumerate(lines):
        result.append(line)
        # Add newline except for last line
        if i < len(lines) - 1:
            if not result[-1].endswith('\n'):
                result[-1] = result[-1] + '\n'
    
    return result

def validate_python_syntax(source_text: str) -> bool:
    """Validate Python syntax (skip IPython magic commands)."""
    # Skip if it's mostly magic commands
    if source_text.strip().startswith('!') or source_text.strip().startswith('%'):
        return True
    
    # Remove magic commands for syntax check
    lines = source_text.split('\n')
    python_lines = [l for l in lines if not l.strip().startswith('!') and not l.strip().startswith('%')]
    python_text = '\n'.join(python_lines)
    
    if not python_text.strip():
        return True
    
    try:
        ast.parse(python_text)
        return True
    except SyntaxError:
        return False

def fix_notebook_formatting(notebook_path: Path) -> bool:
    """Fix formatting in all cells."""
    print(f"\\nFixing formatting: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] != 'code':
            continue
        
        source_lines = cell.get('source', [])
        original_source = source_lines.copy()
        
        # Fix formatting
        fixed_source = fix_cell_source(source_lines)
        
        if fixed_source != original_source:
            cell['source'] = fixed_source
            modified = True
            
            # Validate syntax
            source_text = ''.join(fixed_source)
            if not validate_python_syntax(source_text):
                print(f"   ⚠️  Cell {i} may have syntax issues (contains magic commands or complex code)")
            else:
                print(f"   ✅ Fixed cell {i}")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("FIXING NOTEBOOK CELL FORMATTING FOR GOOGLE COLAB")
    print("="*80)
    
    fixed_count = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if fix_notebook_formatting(notebook_path):
                fixed_count += 1
    
    print("\\n" + "="*80)
    print(f"Updated notebooks: {fixed_count}")
    print("✅ NOTEBOOK FORMATTING FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
