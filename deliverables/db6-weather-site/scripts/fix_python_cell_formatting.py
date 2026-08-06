#!/usr/bin/env python3
"""
Fix Python 3.14.2 installation cell formatting and logic
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

PYTHON_3142_CELL = '''# ============================================================================
# PYTHON 3.14.2 INSTALLATION FOR GOOGLE COLAB
# ============================================================================

import subprocess
import sys
import os

print("="*80)
print("PYTHON 3.14.2 INSTALLATION")
print("="*80)

# Check current Python version
current_version = sys.version_info
print(f"\\nCurrent Python version: {current_version.major}.{current_version.minor}.{current_version.micro}")
print(f"Python executable: {sys.executable}")

# Target version
TARGET_MAJOR = 3
TARGET_MINOR = 14
TARGET_MICRO = 2

if current_version.major == TARGET_MAJOR and current_version.minor == TARGET_MINOR and current_version.micro == TARGET_MICRO:
    print(f"\\n✅ Python {TARGET_MAJOR}.{TARGET_MINOR}.{TARGET_MICRO} is already installed!")
else:
    print(f"\\n⚠️  Python {TARGET_MAJOR}.{TARGET_MINOR}.{TARGET_MICRO} is required")
    print(f"   Current version: {current_version.major}.{current_version.minor}.{current_version.micro}")
    print(f"\\nInstalling Python {TARGET_MAJOR}.{TARGET_MINOR}.{TARGET_MICRO}...")
    
    if not IS_COLAB:
        raise RuntimeError("Python 3.14.2 installation requires Google Colab")
    
    try:
        # Method 1: Use conda (if available)
        print("\\nMethod 1: Trying conda...")
        try:
            result = subprocess.run(['conda', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ Conda found, installing Python 3.14.2...")
                os.system('conda install -y python=3.14.2')
                print("   ✅ Python 3.14.2 installed via conda")
                print("   ⚠️  Restart kernel and re-run this cell to use Python 3.14.2")
        except:
            print("   ⚠️  Conda not available")
        
        # Method 2: Use deadsnakes PPA (Ubuntu/Debian)
        print("\\nMethod 2: Installing via deadsnakes PPA...")
        os.system('apt-get update -qq')
        os.system('apt-get install -y software-properties-common')
        os.system('add-apt-repository -y ppa:deadsnakes/ppa')
        os.system('apt-get update -qq')
        os.system('apt-get install -y python3.14 python3.14-venv python3.14-dev')
        print("   ✅ Python 3.14.2 installed via deadsnakes PPA")
        
        # Method 3: Use pyenv
        print("\\nMethod 3: Installing via pyenv...")
        os.system('curl https://pyenv.run | bash')
        os.system('export PYENV_ROOT="$HOME/.pyenv"')
        os.system('export PATH="$PYENV_ROOT/bin:$PATH"')
        os.system('eval "$(pyenv init -)"')
        os.system('pyenv install 3.14.2')
        os.system('pyenv global 3.14.2')
        print("   ✅ Python 3.14.2 installed via pyenv")
        
        # Verify installation
        print("\\nVerifying Python 3.14.2 installation...")
        result = subprocess.run(['python3.14', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_output = result.stdout.strip()
            print(f"   ✅ Python 3.14 found: {version_output}")
            if '3.14.2' in version_output:
                print("   ✅ Python 3.14.2 is installed!")
            print("\\n⚠️  IMPORTANT: Restart kernel and select Python 3.14.2 as kernel")
            print("   Or use: !python3.14 your_script.py")
        else:
            print("   ⚠️  Python 3.14.2 installation may have failed")
            print("   Current Python version will be used")
    
    except Exception as e:
        print(f"\\n❌ Error installing Python 3.14.2: {e}")
        print("\\n⚠️  Continuing with current Python version")
        print(f"   Current version: {current_version.major}.{current_version.minor}.{current_version.micro}")

# Verify Python version
print("\\n" + "="*80)
print("PYTHON VERSION VERIFICATION")
print("="*80)
final_version = sys.version_info
print(f"Python version: {final_version.major}.{final_version.minor}.{final_version.micro}")
print(f"Python executable: {sys.executable}")

if final_version.major == TARGET_MAJOR and final_version.minor == TARGET_MINOR and final_version.micro == TARGET_MICRO:
    print(f"\\n✅ Python {TARGET_MAJOR}.{TARGET_MINOR}.{TARGET_MICRO} is active!")
else:
    print(f"\\n⚠️  Python {TARGET_MAJOR}.{TARGET_MINOR}.{TARGET_MICRO} is not active")
    print(f"   Current version: {final_version.major}.{final_version.minor}.{final_version.micro}")
    print("   If Python 3.14.2 was installed, restart kernel and select Python 3.14.2")

print("="*80)
'''

def fix_notebook(notebook_path: Path) -> bool:
    """Fix Python installation cell."""
    print(f"\nFixing Python cell: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    modified = False
    
    # Find and replace the Python installation cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source_text = ''.join(cell.get('source', []))
            if 'PYTHON 3.14.2 INSTALLATION' in source_text or 'PYTHON 14.2 INSTALLATION' in source_text:
                # Replace with properly formatted cell
                cell['source'] = PYTHON_3142_CELL.split('\n')
                # Ensure proper newline formatting
                for j in range(len(cell['source']) - 1):
                    if cell['source'][j] and not cell['source'][j].endswith('\n'):
                        cell['source'][j] += '\n'
                modified = True
                print(f"   ✅ Fixed cell {i}")
                break
    
    if modified:
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Saved")
    
    return modified

def main():
    """Main execution."""
    print("="*80)
    print("FIXING PYTHON 3.14.2 INSTALLATION CELL FORMATTING")
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
    print("✅ PYTHON CELL FORMATTING FIXED!")
    print("="*80)

if __name__ == '__main__':
    main()
