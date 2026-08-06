#!/usr/bin/env python3
"""
Fix code formatting in notebooks - add missing newlines
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

def detect_base_dir():
    """Detect base directory."""
    cwd = Path.cwd()
    if cwd.name == 'scripts' and (cwd.parent / 'db-6').exists():
        return cwd.parent
    return cwd.parent if (cwd.parent / 'db-6').exists() else cwd

BASE_DIR = detect_base_dir()
DATABASES = [f'db-{i}' for i in range(6, 16)]

def read_notebook(notebook_path: Path) -> Dict:
    """Read notebook JSON."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_notebook(notebook_path: Path, notebook: Dict):
    """Write notebook JSON."""
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

def fix_code_without_newlines(code: str) -> str:
    """Fix code that's missing newlines between statements."""
    if not code or code.count('\n') > 10:
        # Already has newlines, probably OK
        return code
    
    # Common patterns that need newlines after them
    patterns_to_split = [
        (r'(# =+[^=]+=+)', '\n'),  # Comment headers
        (r'(if\s+[^:]+:)', '\n'),  # if statements
        (r'(elif\s+[^:]+:)', '\n'),  # elif statements
        (r'(else:)', '\n'),  # else
        (r'(try:)', '\n'),  # try
        (r'(except\s+[^:]*:)', '\n'),  # except
        (r'(finally:)', '\n'),  # finally
        (r'(for\s+[^:]+:)', '\n'),  # for loops
        (r'(while\s+[^:]+:)', '\n'),  # while loops
        (r'(def\s+\w+\([^)]*\):)', '\n'),  # function definitions
        (r'(class\s+\w+[^:]*:)', '\n'),  # class definitions
        (r'(return\s+[^\n]+)(?=[a-zA-Z_])', '\n'),  # return statements
        (r'(print\()', '\n'),  # print statements (before)
        (r'(\))(?=[a-zA-Z_#])', '\n'),  # Closing paren before code
        (r'(=)(?=[a-zA-Z_])', '\n'),  # Assignment before code (if on same line)
    ]
    
    # Split on these patterns
    result = code
    
    # First, fix comment headers
    result = re.sub(r'(# =+[^=]+=+)([^#\n])', r'\1\n\2', result)
    
    # Fix if/elif/else/try/except/finally/for/while/def/class followed by code
    result = re.sub(r'(if\s+[^:]+:)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(elif\s+[^:]+:)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(else:)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(try:)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(except\s+[^:]*:)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(finally:)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(for\s+[^:]+:)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(while\s+[^:]+:)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(def\s+\w+\([^)]*\):)([^\n])', r'\1\n    \2', result)
    result = re.sub(r'(class\s+\w+[^:]*:)([^\n])', r'\1\n    \2', result)
    
    # Fix statements that should be on new lines
    # Pattern: statement without newline before next statement
    result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^\n]+)(if\s+[^:]+:)', r'\1\n\2', result)
    result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^\n]+)(def\s+\w+)', r'\1\n\2', result)
    result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^\n]+)(for\s+[^:]+:)', r'\1\n\2', result)
    result = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^\n]+)(print\()', r'\1\n\2', result)
    
    # Fix: if statement followed by code on same line
    result = re.sub(r'(if\s+[^:]+:\s*)([a-zA-Z_])', r'\1\n    \2', result)
    
    # Fix: queries_file = ...if not queries_file:
    result = re.sub(r'(\w+\s*=\s*[^\n]+)(if\s+not\s+\w+:)', r'\1\n\2', result)
    result = re.sub(r'(\w+\s*=\s*[^\n]+)(with\s+open)', r'\1\n\2', result)
    result = re.sub(r'(\w+\s*=\s*[^\n]+)(for\s+\w+)', r'\1\n\2', result)
    
    # Fix: print(...)if total_queries
    result = re.sub(r'(print\([^)]+\))(if\s+)', r'\1\n\2', result)
    
    # Fix: queries = queries_data.get('queries', [])total_queries
    result = re.sub(r'(\]\s*)(total_queries)', r'\1\n\2', result)
    result = re.sub(r'(\]\s*)(print)', r'\1\n\2', result)
    
    # Fix: DB_DIR / 'queries' / 'queries.json'if not
    result = re.sub(r"('\s*)(if\s+not)", r'\1\n\2', result)
    result = re.sub(r"('\s*)(with\s+open)", r'\1\n\2', result)
    
    # Fix: function definitions followed by code
    result = re.sub(r'(\):\s*)([a-zA-Z_])', r'\1\n    \2', result)
    
    # Clean up multiple newlines
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result

def fix_cell_source(source: List[str]) -> List[str]:
    """Fix cell source code."""
    if not source:
        return source
    
    # Join all lines
    full_code = ''.join(source)
    
    # Check if code is mostly on one line (syntax error)
    if len(full_code) > 200 and full_code.count('\n') < 5:
        # Fix it
        fixed_code = fix_code_without_newlines(full_code)
        
        # Split back into lines
        return fixed_code.split('\n')
    
    return source

def fix_notebook(notebook_path: Path) -> bool:
    """Fix notebook code formatting."""
    print(f"\\nFixing: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            original_source = cell.get('source', [])
            fixed_source = fix_cell_source(original_source)
            
            if fixed_source != original_source:
                cell['source'] = fixed_source
                modified = True
                print(f"   ✅ Fixed cell {i+1}")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Notebook saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("FIXING NOTEBOOK CODE FORMATTING")
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
    print("✅ CODE FORMATTING FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
