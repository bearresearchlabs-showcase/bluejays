#!/usr/bin/env python3
"""
Comprehensive testing for Google Colab compatibility
- Tests notebook structure
- Tests Colab-specific features
- Tests PostgreSQL installation code
- Tests file path detection
- Tests error handling
"""

import json
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

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

class ColabNotebookTester:
    """Comprehensive tester for Colab notebooks."""
    
    def __init__(self, notebook_path: Path):
        self.notebook_path = notebook_path
        self.notebook = read_notebook(notebook_path)
        self.results = {
            'notebook': str(notebook_path),
            'tests': {},
            'warnings': [],
            'errors': [],
            'passed': False
        }
    
    def test_colab_check(self) -> bool:
        """Test Colab-only check implementation."""
        all_text = self._get_all_text()
        
        # Check for Colab check
        has_check = (
            'GOOGLE COLAB ONLY' in all_text or
            'IS_COLAB' in all_text or
            'google.colab' in all_text
        )
        
        # Check for error raising
        has_error = (
            'raise RuntimeError' in all_text or
            'raise Exception' in all_text
        ) and 'Colab' in all_text
        
        # Check for proper detection methods
        has_detection = (
            'import google.colab' in all_text or
            '/content' in all_text or
            'COLAB_GPU' in all_text
        )
        
        passed = has_check and has_error and has_detection
        
        self.results['tests']['colab_check'] = {
            'passed': passed,
            'has_check': has_check,
            'has_error': has_error,
            'has_detection': has_detection
        }
        
        if not passed:
            if not has_check:
                self.results['errors'].append("Missing Colab-only check")
            if not has_error:
                self.results['warnings'].append("Colab check doesn't raise error")
            if not has_detection:
                self.results['warnings'].append("Missing Colab detection methods")
        
        return passed
    
    def test_postgresql_setup(self) -> bool:
        """Test PostgreSQL installation code."""
        all_text = self._get_all_text()
        
        # Check for PostgreSQL installation
        has_install = (
            'INSTALLING POSTGRESQL' in all_text or
            'apt-get install' in all_text or
            'postgresql' in all_text.lower()
        )
        
        # Check for service start
        has_service_start = (
            'service postgresql start' in all_text or
            'pg_isready' in all_text
        )
        
        # Check for error handling
        has_error_handling = (
            'try:' in all_text and 'except' in all_text and 'postgresql' in all_text.lower()
        )
        
        # Check for verification
        has_verification = (
            'pg_isready' in all_text or
            'psql --version' in all_text
        )
        
        passed = has_install and has_service_start
        
        self.results['tests']['postgresql_setup'] = {
            'passed': passed,
            'has_install': has_install,
            'has_service_start': has_service_start,
            'has_error_handling': has_error_handling,
            'has_verification': has_verification
        }
        
        if not passed:
            if not has_install:
                self.results['errors'].append("Missing PostgreSQL installation code")
            if not has_service_start:
                self.results['errors'].append("Missing PostgreSQL service start")
        
        if not has_error_handling:
            self.results['warnings'].append("PostgreSQL setup lacks error handling")
        if not has_verification:
            self.results['warnings'].append("PostgreSQL setup lacks verification")
        
        return passed
    
    def test_postgresql_connection(self) -> bool:
        """Test PostgreSQL connection code."""
        all_text = self._get_all_text()
        
        # Check for psycopg2 import
        has_import = 'import psycopg2' in all_text or 'from psycopg2' in all_text
        
        # Check for connection code
        has_connection = 'psycopg2.connect' in all_text
        
        # Check for Colab-specific connection (localhost, postgres/postgres)
        has_colab_config = (
            "host='localhost'" in all_text or
            "host=\"localhost\"" in all_text
        ) and (
            "user='postgres'" in all_text or
            "user=\"postgres\"" in all_text
        )
        
        # Check for error handling
        has_error_handling = (
            'try:' in all_text and 
            'except' in all_text and 
            'psycopg2' in all_text
        )
        
        # Check for IS_COLAB check in connection
        has_colab_check = (
            'IS_COLAB' in all_text or
            "ENV_TYPE == 'colab'" in all_text
        ) and has_connection
        
        passed = has_import and has_connection and has_colab_config
        
        self.results['tests']['postgresql_connection'] = {
            'passed': passed,
            'has_import': has_import,
            'has_connection': has_connection,
            'has_colab_config': has_colab_config,
            'has_error_handling': has_error_handling,
            'has_colab_check': has_colab_check
        }
        
        if not passed:
            if not has_import:
                self.results['errors'].append("Missing psycopg2 import")
            if not has_connection:
                self.results['errors'].append("Missing PostgreSQL connection code")
            if not has_colab_config:
                self.results['warnings'].append("PostgreSQL connection not configured for Colab")
        
        if not has_error_handling:
            self.results['warnings'].append("PostgreSQL connection lacks error handling")
        if not has_colab_check:
            self.results['warnings'].append("PostgreSQL connection doesn't check for Colab")
        
        return passed
    
    def test_file_paths(self) -> bool:
        """Test file path detection for Colab."""
        all_text = self._get_all_text()
        
        # Check for Colab paths
        has_colab_paths = (
            '/content' in all_text or
            '/content/drive' in all_text or
            '/content/db' in all_text
        )
        
        # Check for recursive file finding
        has_recursive = (
            'rglob' in all_text or
            'find_file_recursively' in all_text or
            'glob' in all_text
        )
        
        # Check for Path usage
        has_pathlib = 'from pathlib import Path' in all_text or 'import pathlib' in all_text
        
        passed = has_colab_paths and has_recursive and has_pathlib
        
        self.results['tests']['file_paths'] = {
            'passed': passed,
            'has_colab_paths': has_colab_paths,
            'has_recursive': has_recursive,
            'has_pathlib': has_pathlib
        }
        
        if not passed:
            if not has_colab_paths:
                self.results['warnings'].append("Missing Colab-specific file paths")
            if not has_recursive:
                self.results['warnings'].append("Missing recursive file finding")
            if not has_pathlib:
                self.results['warnings'].append("Not using pathlib for paths")
        
        return passed
    
    def test_sqlite_removal(self) -> bool:
        """Test that SQLite is completely removed."""
        all_text = self._get_all_text()
        
        # Check for SQLite references (should be none)
        has_sqlite = 'sqlite' in all_text.lower()
        
        passed = not has_sqlite
        
        self.results['tests']['sqlite_removal'] = {
            'passed': passed,
            'has_sqlite': has_sqlite
        }
        
        if not passed:
            self.results['errors'].append("SQLite references still present")
        
        return passed
    
    def test_package_installation(self) -> bool:
        """Test package installation code."""
        all_text = self._get_all_text()
        
        # Check for required packages
        required = ['psycopg2', 'pandas', 'numpy']
        has_required = all(pkg in all_text.lower() for pkg in required)
        
        # Check for installation methods
        has_pip = 'pip install' in all_text or 'subprocess' in all_text
        
        # Check for error handling
        has_error_handling = (
            'try:' in all_text and 
            'except' in all_text and 
            ('pip' in all_text or 'import' in all_text)
        )
        
        # Check for Colab-specific installation (!pip)
        has_colab_install = '!pip' in all_text or 'get_ipython' in all_text
        
        passed = has_required and has_pip
        
        self.results['tests']['package_installation'] = {
            'passed': passed,
            'has_required': has_required,
            'has_pip': has_pip,
            'has_error_handling': has_error_handling,
            'has_colab_install': has_colab_install
        }
        
        if not passed:
            if not has_required:
                self.results['warnings'].append("Missing required package installation")
            if not has_pip:
                self.results['warnings'].append("Missing pip installation code")
        
        if not has_error_handling:
            self.results['warnings'].append("Package installation lacks error handling")
        if not has_colab_install:
            self.results['warnings'].append("Not using Colab-specific installation (!pip)")
        
        return passed
    
    def test_code_syntax(self) -> bool:
        """Test code syntax validity."""
        errors = []
        
        for i, cell in enumerate(self.notebook['cells']):
            if cell['cell_type'] == 'code':
                source = ''.join(cell.get('source', []))
                
                # Skip magic commands and empty cells
                if not source.strip() or source.strip().startswith('!') or source.strip().startswith('%'):
                    continue
                
                # Skip cells that are mostly magic commands
                lines = source.split('\n')
                magic_lines = [l for l in lines if l.strip().startswith('!') or l.strip().startswith('%')]
                if len(magic_lines) > len(lines) * 0.5:
                    continue
                
                try:
                    ast.parse(source)
                except SyntaxError as e:
                    # Check if it's a magic command issue
                    if '!' in source or '%' in source:
                        continue
                    errors.append(f"Cell {i+1}: {e.msg} at line {e.lineno}")
        
        passed = len(errors) == 0
        
        self.results['tests']['code_syntax'] = {
            'passed': passed,
            'errors': errors
        }
        
        if not passed:
            self.results['errors'].extend(errors)
        
        return passed
    
    def test_colab_best_practices(self) -> bool:
        """Test Colab best practices."""
        all_text = self._get_all_text()
        
        # Check for Google Drive mounting instructions
        has_drive_mount = (
            'drive.mount' in all_text or
            'google.colab import drive' in all_text
        )
        
        # Check for proper error messages
        has_helpful_errors = (
            'Troubleshooting' in all_text or
            'Please' in all_text or
            'Check' in all_text
        ) and 'Error' in all_text
        
        # Check for progress indicators
        has_progress = 'print(' in all_text and ('✅' in all_text or 'Done' in all_text)
        
        passed = has_drive_mount and has_helpful_errors
        
        self.results['tests']['colab_best_practices'] = {
            'passed': passed,
            'has_drive_mount': has_drive_mount,
            'has_helpful_errors': has_helpful_errors,
            'has_progress': has_progress
        }
        
        if not has_drive_mount:
            self.results['warnings'].append("Missing Google Drive mounting instructions")
        if not has_helpful_errors:
            self.results['warnings'].append("Error messages could be more helpful")
        if not has_progress:
            self.results['warnings'].append("Missing progress indicators")
        
        return passed
    
    def _get_all_text(self) -> str:
        """Get all text from notebook."""
        all_text = ""
        for cell in self.notebook['cells']:
            all_text += ''.join(cell.get('source', [])) + "\n"
        return all_text
    
    def run_all_tests(self) -> Dict:
        """Run all tests."""
        print(f"\\n{'='*80}")
        print(f"Testing: {self.notebook_path.name}")
        print('='*80)
        
        tests = [
            ('Colab Check', self.test_colab_check),
            ('PostgreSQL Setup', self.test_postgresql_setup),
            ('PostgreSQL Connection', self.test_postgresql_connection),
            ('File Paths', self.test_file_paths),
            ('SQLite Removal', self.test_sqlite_removal),
            ('Package Installation', self.test_package_installation),
            ('Code Syntax', self.test_code_syntax),
            ('Colab Best Practices', self.test_colab_best_practices),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} - {test_name}")
                
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ ERROR - {test_name}: {e}")
                self.results['errors'].append(f"{test_name}: {e}")
        
        self.results['passed'] = passed_tests == total_tests
        self.results['summary'] = {
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'pass_rate': f"{(passed_tests/total_tests)*100:.1f}%"
        }
        
        print(f"\\nSummary: {passed_tests}/{total_tests} tests passed ({self.results['summary']['pass_rate']})")
        
        if self.results['warnings']:
            print(f"\\n⚠️  Warnings ({len(self.results['warnings'])}):")
            for warning in self.results['warnings'][:5]:
                print(f"   - {warning}")
        
        if self.results['errors']:
            print(f"\\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results['errors'][:5]:
                print(f"   - {error}")
        
        return self.results

def main():
    """Main execution."""
    print("="*80)
    print("COMPREHENSIVE GOOGLE COLAB NOTEBOOK TESTING")
    print("="*80)
    
    all_results = []
    total_passed = 0
    total_failed = 0
    
    # Test notebooks in db-* directories
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            tester = ColabNotebookTester(notebook_path)
            results = tester.run_all_tests()
            all_results.append(results)
            
            if results['passed']:
                total_passed += 1
            else:
                total_failed += 1
    
    # Test notebooks in client/db (sample)
    client_db_dir = BASE_DIR / 'client' / 'db'
    if client_db_dir.exists():
        # Test first 3 client notebooks as sample
        for db_name in DATABASES[:3]:
            for deliverable_dir in client_db_dir.glob(f"{db_name}/*"):
                if deliverable_dir.is_dir():
                    notebook_path = deliverable_dir / f"{db_name}.ipynb"
                    if notebook_path.exists():
                        tester = ColabNotebookTester(notebook_path)
                        results = tester.run_all_tests()
                        all_results.append(results)
                        
                        if results['passed']:
                            total_passed += 1
                        else:
                            total_failed += 1
                        break
    
    # Final summary
    print("\\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    print(f"Total notebooks tested: {len(all_results)}")
    print(f"✅ Fully passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    
    if total_failed > 0:
        print("\\nFailed notebooks:")
        for results in all_results:
            if not results['passed']:
                print(f"  - {Path(results['notebook']).name}")
    
    print("\\n" + "="*80)
    if total_failed == 0:
        print("✅ ALL NOTEBOOKS PASSED COMPREHENSIVE TESTING!")
    else:
        print("⚠️  SOME NOTEBOOKS NEED ATTENTION")
    print("="*80)
    
    return 0 if total_failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
