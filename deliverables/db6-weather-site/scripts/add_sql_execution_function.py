#!/usr/bin/env python3
"""
Add execute_query_with_metrics function to notebooks
This function is called but missing from notebooks
"""

import json
import sys
from pathlib import Path
from typing import Dict

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

# SQL execution function for Colab PostgreSQL
EXECUTE_QUERY_FUNCTION = '''# ============================================================================
# QUERY EXECUTION FUNCTION WITH METRICS
# ============================================================================

import time
import pandas as pd

def execute_query_with_metrics(db_name: str, query_sql: str, query_num: int, db_config: dict = None):
    """
    Execute SQL query with metrics collection.
    
    Args:
        db_name: Database name
        query_sql: SQL query string
        query_num: Query number
        db_config: Database configuration (optional, uses global conn if None)
    
    Returns:
        dict: Query execution results with metrics
    """
    result = {
        'query_number': query_num,
        'success': False,
        'execution_time': 0.0,
        'row_count': 0,
        'column_count': 0,
        'dataframe': None,
        'error': None
    }
    
    try:
        # Use global connection if db_config not provided
        if db_config is None:
            # Use the global conn variable
            if 'conn' not in globals():
                raise RuntimeError("Database connection not available. Run connection cell first.")
            exec_conn = globals()['conn']
        else:
            # Create new connection from config
            exec_conn = psycopg2.connect(**db_config)
        
        # Start timing
        start_time = time.time()
        
        # Execute query
        cursor = exec_conn.cursor()
        cursor.execute(query_sql)
        
        # Fetch results
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Create DataFrame
        if rows and columns:
            df = pd.DataFrame(rows, columns=columns)
        else:
            df = pd.DataFrame()
        
        # Update result
        result['success'] = True
        result['execution_time'] = execution_time
        result['row_count'] = len(df)
        result['column_count'] = len(columns)
        result['dataframe'] = df
        
        # Close cursor
        cursor.close()
        
        # Close connection if we created it
        if db_config is not None:
            exec_conn.close()
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        result['execution_time'] = time.time() - start_time if 'start_time' in locals() else 0.0
    
    return result

# Database configuration (for reference, uses global conn by default)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'postgres'
}

print("✅ Query execution function loaded")
print("   Function: execute_query_with_metrics(db_name, query_sql, query_num, db_config=None)")
'''

def add_execute_function_to_notebook(notebook_path: Path) -> bool:
    """Add execute_query_with_metrics function to notebook."""
    print(f"\\nAdding SQL execution function: {notebook_path.name}")
    
    notebook = read_notebook(notebook_path)
    
    # Check if function already exists
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    if 'def execute_query_with_metrics' in all_text:
        print(f"   ✅ Function already exists")
        return False
    
    # Find where to insert (before query execution cell)
    insert_idx = -1
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'for query_info in queries' in source or 'execute_query_with_metrics' in source:
                insert_idx = i
                break
    
    if insert_idx == -1:
        # Find "Step 5" or "Execute All Queries" markdown
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'markdown':
                source = ''.join(cell.get('source', []))
                if 'Execute' in source and 'Queries' in source:
                    insert_idx = i + 1
                    break
    
    if insert_idx == -1:
        # Insert before last code cell
        code_cells = [i for i, c in enumerate(notebook['cells']) if c['cell_type'] == 'code']
        if code_cells:
            insert_idx = code_cells[-1]
    
    if insert_idx >= 0:
        # Add markdown cell
        markdown_cell = {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Step 5: Query Execution Function"
            ]
        }
        
        # Add code cell with function
        code_cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": EXECUTE_QUERY_FUNCTION.split('\\n')
        }
        
        notebook['cells'].insert(insert_idx, markdown_cell)
        notebook['cells'].insert(insert_idx + 1, code_cell)
        
        # Save
        write_notebook(notebook_path, notebook)
        print(f"   ✅ Added execute_query_with_metrics function")
        return True
    
    print(f"   ⚠️  Could not find insertion point")
    return False

def main():
    """Main execution."""
    print("="*80)
    print("ADDING SQL EXECUTION FUNCTION TO NOTEBOOKS")
    print("="*80)
    
    updated_count = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if add_execute_function_to_notebook(notebook_path):
                updated_count += 1
    
    print("\\n" + "="*80)
    print(f"Updated notebooks: {updated_count}")
    print("✅ SQL execution function added!")
    print("="*80)

if __name__ == '__main__':
    main()
