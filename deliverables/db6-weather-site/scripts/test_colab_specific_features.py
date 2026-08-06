#!/usr/bin/env python3
"""
Test Colab-specific features based on official documentation
- File system access
- Google Drive integration
- System commands
- Package installation
- Environment variables
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

def test_colab_file_system(notebook: Dict) -> Dict:
    """
    Test Colab file system access patterns.
    
    Colab provides:
    - /content directory for uploaded files
    - /content/drive/MyDrive for Google Drive (when mounted)
    - Temporary files in /tmp
    """
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'has_content_path': '/content' in all_text,
        'has_drive_path': '/content/drive' in all_text or 'drive/MyDrive' in all_text,
        'has_pathlib': 'from pathlib import Path' in all_text or 'import pathlib' in all_text,
        'has_os_path': 'os.path' in all_text or 'os.getcwd' in all_text,
        'has_recursive_search': 'rglob' in all_text or 'glob' in all_text,
    }
    
    results['passed'] = all([
        results['has_content_path'],
        results['has_pathlib'],
        results['has_recursive_search']
    ])
    
    return results

def test_colab_drive_integration(notebook: Dict) -> Dict:
    """
    Test Google Drive integration.
    
    Colab provides:
    - from google.colab import drive
    - drive.mount('/content/drive')
    - Files accessible at /content/drive/MyDrive
    """
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'has_drive_import': 'from google.colab import drive' in all_text or 'import google.colab' in all_text,
        'has_drive_mount': 'drive.mount' in all_text,
        'has_drive_path_check': '/content/drive' in all_text or 'drive/MyDrive' in all_text,
        'has_mount_instructions': 'mount' in all_text.lower() and ('drive' in all_text.lower() or 'colab' in all_text.lower()),
    }
    
    results['passed'] = results['has_drive_path_check']  # At minimum, should check for Drive paths
    
    return results

def test_colab_system_commands(notebook: Dict) -> Dict:
    """
    Test system command usage.
    
    Colab supports:
    - !command for shell commands
    - subprocess for programmatic execution
    - apt-get for package installation
    """
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'has_shell_commands': '!' in all_text or 'subprocess' in all_text,
        'has_apt_get': 'apt-get' in all_text,
        'has_service_command': 'service' in all_text,
        'has_subprocess': 'import subprocess' in all_text or 'subprocess.' in all_text,
    }
    
    results['passed'] = results['has_shell_commands'] or results['has_subprocess']
    
    return results

def test_colab_package_installation(notebook: Dict) -> Dict:
    """
    Test package installation methods.
    
    Colab supports:
    - !pip install (recommended)
    - pip install via subprocess
    - apt-get for system packages
    """
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'has_pip_magic': '!pip' in all_text,
        'has_pip_subprocess': 'pip install' in all_text and 'subprocess' in all_text,
        'has_get_ipython': 'get_ipython' in all_text,
        'has_error_handling': 'try:' in all_text and 'pip' in all_text.lower(),
        'has_quiet_flag': '--quiet' in all_text or '-q' in all_text,
    }
    
    results['passed'] = results['has_pip_magic'] or results['has_pip_subprocess']
    
    return results

def test_colab_environment_detection(notebook: Dict) -> Dict:
    """
    Test environment detection.
    
    Colab provides:
    - google.colab module
    - /content directory
    - COLAB_GPU environment variable
    """
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'has_google_colab_import': 'import google.colab' in all_text or 'from google.colab' in all_text,
        'has_content_check': '/content' in all_text and 'exists' in all_text,
        'has_colab_gpu_check': 'COLAB_GPU' in all_text or 'COLAB' in all_text,
        'has_os_environ': 'os.environ' in all_text,
        'has_multiple_detection': (
            ('google.colab' in all_text and '/content' in all_text) or
            ('COLAB_GPU' in all_text and '/content' in all_text)
        ),
    }
    
    results['passed'] = results['has_multiple_detection'] or (
        results['has_google_colab_import'] and results['has_content_check']
    )
    
    return results

def test_colab_postgresql_specific(notebook: Dict) -> Dict:
    """
    Test PostgreSQL-specific Colab setup.
    
    Colab considerations:
    - PostgreSQL must be installed via apt-get
    - Service must be started manually
    - Default user: postgres, password: postgres
    - Runs on localhost:5432
    """
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'has_apt_install': 'apt-get install' in all_text and 'postgresql' in all_text.lower(),
        'has_service_start': 'service postgresql start' in all_text,
        'has_postgres_user': "user='postgres'" in all_text or 'user="postgres"' in all_text,
        'has_localhost': "host='localhost'" in all_text or 'host="localhost"' in all_text,
        'has_port_5432': "port=5432" in all_text or 'port="5432"' in all_text,
        'has_verification': 'pg_isready' in all_text or 'psql --version' in all_text,
    }
    
    results['passed'] = all([
        results['has_apt_install'],
        results['has_service_start'],
        results['has_postgres_user'],
        results['has_localhost'],
    ])
    
    return results

def test_colab_error_handling(notebook: Dict) -> Dict:
    """
    Test error handling for Colab environment.
    
    Should handle:
    - Missing files
    - Failed installations
    - Connection errors
    - Permission errors
    """
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'has_try_except': 'try:' in all_text and 'except' in all_text,
        'has_file_not_found': 'FileNotFoundError' in all_text or 'file not found' in all_text.lower(),
        'has_connection_error': 'ConnectionError' in all_text or 'connection' in all_text.lower() and 'error' in all_text.lower(),
        'has_helpful_messages': (
            'Troubleshooting' in all_text or
            'Please' in all_text or
            ('Check' in all_text and 'Error' in all_text)
        ),
        'has_raise_error': 'raise RuntimeError' in all_text or 'raise Exception' in all_text,
    }
    
    results['passed'] = results['has_try_except'] and results['has_helpful_messages']
    
    return results

def test_notebook_colab_features(notebook_path: Path) -> Dict:
    """Test all Colab-specific features."""
    print(f"\\nTesting Colab features: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    
    tests = {
        'file_system': test_colab_file_system(notebook),
        'drive_integration': test_colab_drive_integration(notebook),
        'system_commands': test_colab_system_commands(notebook),
        'package_installation': test_colab_package_installation(notebook),
        'environment_detection': test_colab_environment_detection(notebook),
        'postgresql_specific': test_colab_postgresql_specific(notebook),
        'error_handling': test_colab_error_handling(notebook),
    }
    
    passed = sum(1 for t in tests.values() if t.get('passed', False))
    total = len(tests)
    
    print(f"  Colab Features: {passed}/{total} passed")
    
    for test_name, test_results in tests.items():
        status = "✅" if test_results.get('passed') else "⚠️"
        print(f"    {status} {test_name}")
    
    return {
        'notebook': str(notebook_path),
        'tests': tests,
        'passed': passed,
        'total': total,
        'pass_rate': f"{(passed/total)*100:.1f}%"
    }

def main():
    """Main execution."""
    print("="*80)
    print("TESTING COLAB-SPECIFIC FEATURES")
    print("="*80)
    print("Based on Google Colab documentation and best practices")
    
    all_results = []
    
    # Test first 3 notebooks as sample
    for db_name in DATABASES[:3]:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            results = test_notebook_colab_features(notebook_path)
            all_results.append(results)
    
    # Summary
    print("\\n" + "="*80)
    print("COLAB FEATURES TEST SUMMARY")
    print("="*80)
    
    if all_results:
        avg_pass_rate = sum(float(r['pass_rate'].rstrip('%')) for r in all_results) / len(all_results)
        print(f"Average pass rate: {avg_pass_rate:.1f}%")
        print(f"Notebooks tested: {len(all_results)}")
    
    print("\\n" + "="*80)
    print("✅ Colab-specific feature testing complete!")
    print("="*80)

if __name__ == '__main__':
    main()
