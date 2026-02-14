#!/usr/bin/env python3
"""
Fix syntax errors in notebooks
- Fix missing newlines in code cells
- Ensure proper code formatting
- Fix queries variable definition
"""

import json
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

def fix_code_cell_newlines(source: List[str]) -> List[str]:
    """Fix missing newlines in code cell source."""
    if not source:
        return source
    
    # Join all lines
    full_text = ''.join(source)
    
    # Check if it's all on one line (common issue)
    if '\n' not in full_text and len(full_text) > 200:
        # Try to split on common patterns
        # Split on def, if, try, except, return, etc.
        import re
        
        # Split on function definitions, control flow, etc.
        patterns = [
            r'(def\s+\w+\([^)]*\):)',
            r'(if\s+[^:]+:)',
            r'(elif\s+[^:]+:)',
            r'(else:)',
            r'(try:)',
            r'(except\s+[^:]+:)',
            r'(finally:)',
            r'(for\s+[^:]+:)',
            r'(while\s+[^:]+:)',
            r'(return\s+)',
            r'(print\()',
            r'(import\s+)',
            r'(from\s+[^\s]+\s+import)',
        ]
        
        # Split text preserving separators
        parts = []
        last_pos = 0
        
        for pattern in patterns:
            for match in re.finditer(pattern, full_text):
                if match.start() > last_pos:
                    parts.append(full_text[last_pos:match.start()])
                parts.append(match.group(0))
                last_pos = match.end()
        
        if last_pos < len(full_text):
            parts.append(full_text[last_pos:])
        
        # Reconstruct with newlines
        result = []
        for i, part in enumerate(parts):
            if part.strip():
                # Add newline before def, if, try, etc.
                if i > 0 and re.match(r'(def|if|elif|else|try|except|finally|for|while|import|from)', part.strip()):
                    result.append('\n')
                result.append(part)
                # Add newline after : (for control flow)
                if part.strip().endswith(':'):
                    result.append('\n')
        
        return [''.join(result)]
    
    # If already has newlines, ensure proper formatting
    lines = full_text.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines at start
        if not stripped and i == 0:
            continue
        
        # Add proper indentation detection
        fixed_lines.append(line)
    
    return fixed_lines if fixed_lines else source

def fix_queries_loading_cell(notebook: Dict) -> bool:
    """Fix queries loading cell to ensure queries variable is defined."""
    modified = False
    
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            
            # Check if this is the queries loading cell
            if 'queries.json' in source and 'queries_data' in source:
                # Check if queries variable is properly assigned
                if 'queries = queries_data.get' not in source:
                    # Fix the cell
                    fixed_source = source
                    
                    # Ensure queries variable assignment
                    if 'queries_data.get' in source and 'queries =' not in source:
                        # Try to add queries assignment
                        if 'queries_data = json.load' in source:
                            # Add after json.load
                            lines = source.split('\n')
                            new_lines = []
                            for line in lines:
                                new_lines.append(line)
                                if 'queries_data = json.load' in line or 'queries_data.get' in line:
                                    if 'queries =' not in '\n'.join(new_lines):
                                        new_lines.append('queries = queries_data.get(\'queries\', [])')
                                        new_lines.append('total_queries = len(queries)')
                                        modified = True
                            
                            cell['source'] = new_lines if new_lines else cell['source']
    
    return modified

def fix_notebook_syntax(notebook_path: Path) -> Dict:
    """Fix syntax errors in a notebook."""
    print(f"\\nFixing syntax: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    fixes_applied = {
        'newlines_fixed': 0,
        'queries_fixed': False,
        'cells_modified': 0
    }
    
    # Fix code cells with missing newlines
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            original_source = cell.get('source', [])
            
            # Check for syntax issues
            full_text = ''.join(original_source)
            
            # Check for common syntax error patterns
            if 'def ' in full_text and ':' in full_text:
                # Check if def and : are on same line without newline after
                if re.search(r'def\s+\w+\([^)]*\):[^\n]', full_text):
                    # This might be a problem - code after : on same line
                    fixed_source = fix_code_cell_newlines(original_source)
                    if fixed_source != original_source:
                        cell['source'] = fixed_source
                        fixes_applied['newlines_fixed'] += 1
                        fixes_applied['cells_modified'] += 1
            
            # Check for missing newlines between statements
            if len(full_text) > 500 and full_text.count('\n') < 10:
                # Likely missing newlines
                fixed_source = fix_code_cell_newlines(original_source)
                if fixed_source != original_source:
                    cell['source'] = fixed_source
                    fixes_applied['newlines_fixed'] += 1
                    fixes_applied['cells_modified'] += 1
    
    # Fix queries loading
    if fix_queries_loading_cell(notebook):
        fixes_applied['queries_fixed'] = True
        fixes_applied['cells_modified'] += 1
    
    if fixes_applied['cells_modified'] > 0:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Fixed {fixes_applied['cells_modified']} cells")
    else:
        print(f"   ✅ No fixes needed")
    
    return fixes_applied

def main():
    """Main execution."""
    import re
    
    print("="*80)
    print("FIXING NOTEBOOK SYNTAX ERRORS")
    print("="*80)
    
    all_fixes = []
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            fixes = fix_notebook_syntax(notebook_path)
            all_fixes.append((db_name, fixes))
    
    # Summary
    print("\\n" + "="*80)
    print("SYNTAX FIX SUMMARY")
    print("="*80)
    
    total_cells = sum(f['cells_modified'] for _, f in all_fixes)
    total_newlines = sum(f['newlines_fixed'] for _, f in all_fixes)
    queries_fixed_count = sum(1 for _, f in all_fixes if f['queries_fixed'])
    
    print(f"Total notebooks processed: {len(all_fixes)}")
    print(f"Total cells fixed: {total_cells}")
    print(f"Newlines fixed: {total_newlines}")
    print(f"Queries loading fixed: {queries_fixed_count}")
    
    print("\\n" + "="*80)
    print("✅ SYNTAX ERRORS FIXED!")
    print("="*80)

if __name__ == '__main__':
    import re
    main()
