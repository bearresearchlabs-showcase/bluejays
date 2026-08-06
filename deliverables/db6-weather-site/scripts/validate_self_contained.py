#!/usr/bin/env python3
"""
Validate that notebooks are self-contained for Google Colab
- Check for embedded SQL and queries
- Verify no file system dependencies
- Check formatting
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

def validate_notebook(notebook_path: Path) -> dict:
    """Validate notebook is self-contained."""
    notebook = read_notebook(notebook_path)
    
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    
    results = {
        'notebook': notebook_path.name,
        'has_embedded_schema': 'EMBEDDED SCHEMA.SQL' in all_text or 'SCHEMA_SQL' in all_text,
        'has_embedded_data': 'EMBEDDED DATA.SQL' in all_text or 'DATA_SQL' in all_text,
        'has_embedded_queries': 'EMBEDDED QUERIES.JSON' in all_text or 'QUERIES_DATA' in all_text,
        'has_file_dependencies': False,
        'file_dependencies': [],
        'issues': []
    }
    
    # Check for file dependencies
    file_patterns = [
        ('queries.json', 'find_file_recursively'),
        ('schema.sql', 'open('),
        ('data.sql', 'open('),
        ('Path(', 'queries.json'),
        ('Path(', 'schema.sql'),
        ('Path(', 'data.sql'),
    ]
    
    for pattern, context in file_patterns:
        if pattern in all_text.lower() and context in all_text.lower():
            # Check if it's in embedded cell (should be OK)
            if 'EMBEDDED' not in all_text[:all_text.lower().find(pattern.lower()) + 100]:
                results['has_file_dependencies'] = True
                results['file_dependencies'].append(f"{pattern} ({context})")
    
    # Check for required components
    if not results['has_embedded_schema']:
        results['issues'].append('Missing embedded schema.sql')
    if not results['has_embedded_queries']:
        results['issues'].append('Missing embedded queries.json')
    
    return results

def main():
    """Main execution."""
    print("="*80)
    print("VALIDATING SELF-CONTAINED NOTEBOOKS FOR GOOGLE COLAB")
    print("="*80)
    
    all_valid = True
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            results = validate_notebook(notebook_path)
            
            print(f"\\n{results['notebook']}:")
            print(f"  Embedded Schema: {'✅' if results['has_embedded_schema'] else '❌'}")
            print(f"  Embedded Data: {'✅' if results['has_embedded_data'] else '⚠️  (optional)'}")
            print(f"  Embedded Queries: {'✅' if results['has_embedded_queries'] else '❌'}")
            
            if results['has_file_dependencies']:
                print(f"  ❌ File Dependencies Found:")
                for dep in results['file_dependencies']:
                    print(f"     - {dep}")
                all_valid = False
            
            if results['issues']:
                print(f"  ⚠️  Issues:")
                for issue in results['issues']:
                    print(f"     - {issue}")
                all_valid = False
    
    print("\\n" + "="*80)
    if all_valid:
        print("✅ ALL NOTEBOOKS ARE SELF-CONTAINED!")
    else:
        print("⚠️  SOME NOTEBOOKS HAVE ISSUES")
    print("="*80)

if __name__ == '__main__':
    main()
