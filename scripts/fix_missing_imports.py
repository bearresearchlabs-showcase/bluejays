#!/usr/bin/env python3
"""
Fix missing imports in notebooks
- Ensure pandas is imported as pd
- Ensure other required imports are present
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

def check_imports_needed(source: str) -> list:
    """Check what imports are needed based on code usage."""
    needed = []
    
    if 'pd.DataFrame' in source or 'pd.read_sql' in source or 'pd.' in source:
        needed.append('pandas')
    if 'np.' in source or 'numpy.' in source:
        needed.append('numpy')
    if 'plt.' in source or 'matplotlib.' in source:
        needed.append('matplotlib')
    if 'sns.' in source or 'seaborn.' in source:
        needed.append('seaborn')
    if 'display(' in source or 'Markdown(' in source or 'HTML(' in source:
        needed.append('IPython')
    
    return needed

def check_imports_present(source: str) -> dict:
    """Check what imports are already present."""
    present = {
        'pandas': False,
        'numpy': False,
        'matplotlib': False,
        'seaborn': False,
        'IPython': False
    }
    
    if 'import pandas as pd' in source or 'import pandas' in source:
        present['pandas'] = True
    if 'import numpy as np' in source or 'import numpy' in source:
        present['numpy'] = True
    if 'import matplotlib' in source or 'from matplotlib' in source:
        present['matplotlib'] = True
    if 'import seaborn' in source or 'from seaborn' in source:
        present['seaborn'] = True
    if 'from IPython' in source or 'import IPython' in source:
        present['IPython'] = True
    
    return present

def add_imports_to_cell(cell_source: list, needed_imports: list) -> list:
    """Add missing imports to cell."""
    source_text = ''.join(cell_source)
    present = check_imports_present(source_text)
    
    imports_to_add = []
    
    if 'pandas' in needed_imports and not present['pandas']:
        imports_to_add.append('import pandas as pd')
    if 'numpy' in needed_imports and not present['numpy']:
        imports_to_add.append('import numpy as np')
    if 'matplotlib' in needed_imports and not present['matplotlib']:
        imports_to_add.append('import matplotlib.pyplot as plt')
    if 'seaborn' in needed_imports and not present['seaborn']:
        imports_to_add.append('import seaborn as sns')
    if 'IPython' in needed_imports and not present['IPython']:
        imports_to_add.append('from IPython.display import display, HTML, Markdown')
    
    if imports_to_add:
        # Add imports at the beginning
        new_source = imports_to_add + [''] + cell_source
        return new_source
    
    return cell_source

def fix_notebook(notebook_path: Path) -> bool:
    """Fix missing imports in notebook."""
    print(f"\\nFixing imports: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            
            # Skip cells that are just imports or setup
            if source.strip().startswith('#') and 'SETUP' in source.upper():
                continue
            
            # Check what imports are needed
            needed = check_imports_needed(source)
            
            if needed:
                # Check what's present
                present = check_imports_present(source)
                
                # Add missing imports
                cell_source = cell.get('source', [])
                fixed_source = add_imports_to_cell(cell_source, needed)
                
                if fixed_source != cell_source:
                    cell['source'] = fixed_source
                    modified = True
                    missing = [imp for imp in needed if not present.get(imp.lower().replace(' ', '_'), False)]
                    print(f"   ✅ Fixed cell {i+1}: Added {', '.join(missing)}")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("FIXING MISSING IMPORTS IN NOTEBOOKS")
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
    print("✅ IMPORTS FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
