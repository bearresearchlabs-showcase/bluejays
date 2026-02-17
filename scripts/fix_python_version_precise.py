#!/usr/bin/env python3
"""
Precisely fix Python version in notebooks - update from 14.2 to 3.14.2
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

def fix_notebook(notebook_path: Path) -> bool:
    """Fix Python version in notebook."""
    print(f"\nFixing Python version: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    for i, cell in enumerate(notebook['cells']):
        source_lines = cell.get('source', [])
        if not source_lines:
            continue
        
        # Join and check
        source_text = ''.join(source_lines)
        original_text = source_text
        
        # Fix markdown cells
        if cell['cell_type'] == 'markdown':
            source_text = source_text.replace('Python 14.2', 'Python 3.14.2')
            source_text = source_text.replace('python 14.2', 'python 3.14.2')
        
        # Fix code cells - comprehensive replacements
        elif cell['cell_type'] == 'code':
            # Header comments
            source_text = source_text.replace('# PYTHON 14.2 INSTALLATION', '# PYTHON 3.14.2 INSTALLATION')
            source_text = source_text.replace('PYTHON 14.2 INSTALLATION', 'PYTHON 3.14.2 INSTALLATION')
            
            # Print statements
            source_text = source_text.replace('print("PYTHON 14.2 INSTALLATION")', 'print("PYTHON 3.14.2 INSTALLATION")')
            
            # Target version variables
            source_text = source_text.replace('TARGET_MAJOR = 14', 'TARGET_MAJOR = 3')
            source_text = source_text.replace('TARGET_MINOR = 2', 'TARGET_MINOR = 14')
            
            # Add TARGET_MICRO if not present
            if 'TARGET_MICRO = 2' not in source_text and 'TARGET_MINOR = 14' in source_text:
                # Insert after TARGET_MINOR
                lines = source_text.split('\n')
                for j, line in enumerate(lines):
                    if 'TARGET_MINOR = 14' in line:
                        lines.insert(j + 1, 'TARGET_MICRO = 2')
                        source_text = '\n'.join(lines)
                        break
            
            # Fix version checks - need to add micro check
            if 'current_version.major == TARGET_MAJOR and current_version.minor == TARGET_MINOR:' in source_text:
                source_text = source_text.replace(
                    'current_version.major == TARGET_MAJOR and current_version.minor == TARGET_MINOR:',
                    'current_version.major == TARGET_MAJOR and current_version.minor == TARGET_MINOR and current_version.micro == TARGET_MICRO:'
                )
            
            if 'final_version.major == TARGET_MAJOR and final_version.minor == TARGET_MINOR' in source_text:
                source_text = source_text.replace(
                    'final_version.major == TARGET_MAJOR and final_version.minor == TARGET_MINOR',
                    'final_version.major == TARGET_MAJOR and final_version.minor == TARGET_MINOR and final_version.micro == TARGET_MICRO'
                )
            
            # Fix installation commands
            source_text = source_text.replace('python=14.2', 'python=3.14.2')
            source_text = source_text.replace('python14.2', 'python3.14')
            source_text = source_text.replace('pyenv install 14.2', 'pyenv install 3.14.2')
            source_text = source_text.replace('pyenv global 14.2', 'pyenv global 3.14.2')
            
            # Fix print statements with version numbers
            source_text = source_text.replace('Python {TARGET_MAJOR}.{TARGET_MINOR}', 'Python {TARGET_MAJOR}.{TARGET_MINOR}.{TARGET_MICRO}')
            source_text = source_text.replace('Python 14.2', 'Python 3.14.2')
            source_text = source_text.replace('Python 3.14.2 installation requires Google Colab', 'Python 3.14.2 installation requires Google Colab')
            
            # Fix error messages
            source_text = source_text.replace('Error installing Python 14.2', 'Error installing Python 3.14.2')
            source_text = source_text.replace('Python 14.2 installation may have failed', 'Python 3.14.2 installation may have failed')
            source_text = source_text.replace('Python 14.2 found', 'Python 3.14.2 found')
            source_text = source_text.replace('select Python 14.2', 'select Python 3.14.2')
            source_text = source_text.replace('If Python 14.2 was installed', 'If Python 3.14.2 was installed')
            source_text = source_text.replace('Python 14.2 is already installed', 'Python 3.14.2 is already installed')
            source_text = source_text.replace('Python 14.2 is required', 'Python 3.14.2 is required')
            source_text = source_text.replace('Installing Python 14.2', 'Installing Python 3.14.2')
            source_text = source_text.replace('Python 14.2 is active', 'Python 3.14.2 is active')
            source_text = source_text.replace('Python 14.2 is not active', 'Python 3.14.2 is not active')
            source_text = source_text.replace('Verifying Python 14.2 installation', 'Verifying Python 3.14.2 installation')
            source_text = source_text.replace('Python 14.2 installed via conda', 'Python 3.14.2 installed via conda')
            source_text = source_text.replace('Python 14.2 installed via deadsnakes PPA', 'Python 3.14.2 installed via deadsnakes PPA')
            source_text = source_text.replace('Python 14.2 installed via pyenv', 'Python 3.14.2 installed via pyenv')
            source_text = source_text.replace('restart kernel and re-run this cell to use Python 14.2', 'restart kernel and re-run this cell to use Python 3.14.2')
            source_text = source_text.replace('restart kernel and select Python 14.2', 'restart kernel and select Python 3.14.2')
            source_text = source_text.replace('!python14.2', '!python3.14')
        
        if source_text != original_text:
            # Split back into lines
            cell['source'] = source_text.split('\n')
            # Ensure proper newline formatting
            for j in range(len(cell['source']) - 1):
                if cell['source'][j] and not cell['source'][j].endswith('\n'):
                    cell['source'][j] += '\n'
            modified = True
            print(f"   ✅ Fixed cell {i}")
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("PRECISELY FIXING PYTHON VERSION IN NOTEBOOKS (14.2 -> 3.14.2)")
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
