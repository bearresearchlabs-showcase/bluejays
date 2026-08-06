#!/usr/bin/env python3
"""
Add SQL files and queries.json directly into notebooks as cells
- Add schema.sql as executable SQL cell
- Add data.sql as executable SQL cell (if exists)
- Add queries.json as Python code cell that loads queries
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

def create_schema_sql_cell(schema_content: str, db_name: str) -> dict:
    """Create a cell with embedded schema.sql."""
    # Escape triple quotes in schema content
    schema_escaped = schema_content.replace('"""', '\\"\\"\\"')
    
    cell_content = f'''# ============================================================================
# EMBEDDED SCHEMA.SQL - {db_name.upper()}
# ============================================================================
# This cell contains the complete database schema
# Execute this cell to load the schema into PostgreSQL

import psycopg2

# Schema SQL (embedded directly in notebook)
SCHEMA_SQL = """
{schema_escaped}
"""

def execute_schema_sql(connection):
    """Execute embedded schema SQL."""
    cursor = connection.cursor()
    try:
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in SCHEMA_SQL.split(';') if s.strip()]
        for idx, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"  ✅ Executed statement {{idx}}/{{len(statements)}}")
                except Exception as e:
                    error_msg = str(e)[:100]
                    print(f"  ⚠️  Statement {{idx}} warning: {{error_msg}}")
        connection.commit()
        print("\\n✅ Schema loaded successfully!")
        return True
    except Exception as e:
        connection.rollback()
        print(f"\\n❌ Error loading schema: {{e}}")
        return False
    finally:
        cursor.close()

# Auto-execute if connection exists
if 'conn' in globals():
    print("="*80)
    print("LOADING EMBEDDED SCHEMA")
    print("="*80)
    execute_schema_sql(conn)
else:
    print("⚠️  Database connection not found. Run connection cell first.")
    print("   Schema SQL is available in SCHEMA_SQL variable")
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": cell_content.split('\n')
    }

def create_data_sql_cell(data_content: str, db_name: str) -> dict:
    """Create a cell with embedded data.sql."""
    # Escape triple quotes in data content
    data_escaped = data_content.replace('"""', '\\"\\"\\"')
    
    cell_content = f'''# ============================================================================
# EMBEDDED DATA.SQL - {db_name.upper()}
# ============================================================================
# This cell contains sample data for the database
# Execute this cell to load data into PostgreSQL

import psycopg2

# Data SQL (embedded directly in notebook)
DATA_SQL = """
{data_escaped}
"""

def execute_data_sql(connection):
    """Execute embedded data SQL."""
    cursor = connection.cursor()
    try:
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in DATA_SQL.split(';') if s.strip()]
        for idx, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"  ✅ Executed statement {{idx}}/{{len(statements)}}")
                except Exception as e:
                    error_msg = str(e)[:100]
                    print(f"  ⚠️  Statement {{idx}} warning: {{error_msg}}")
        connection.commit()
        print("\\n✅ Data loaded successfully!")
        return True
    except Exception as e:
        connection.rollback()
        print(f"\\n❌ Error loading data: {{e}}")
        return False
    finally:
        cursor.close()

# Auto-execute if connection exists
if 'conn' in globals():
    print("="*80)
    print("LOADING EMBEDDED DATA")
    print("="*80)
    execute_data_sql(conn)
else:
    print("⚠️  Database connection not found. Run connection cell first.")
    print("   Data SQL is available in DATA_SQL variable")
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": cell_content.split('\n')
    }

def create_queries_json_cell(queries_data: dict, db_name: str) -> dict:
    """Create a cell with embedded queries.json."""
    # Convert queries to Python dict format
    queries_str = json.dumps(queries_data, indent=2, ensure_ascii=False)
    
    cell_content = f'''# ============================================================================
# EMBEDDED QUERIES.JSON - {db_name.upper()}
# ============================================================================
# This cell contains all query metadata embedded directly in the notebook
# No external file dependencies required

import json

# Queries data (embedded directly in notebook)
QUERIES_DATA = {queries_str}

# Extract queries list
queries = QUERIES_DATA.get('queries', [])
total_queries = len(queries)

print("="*80)
print("EMBEDDED QUERIES LOADED")
print("="*80)
print(f"Total Queries: {{total_queries}}")
print(f"Source: Embedded in notebook (no file dependency)")

if queries:
    print(f"\\nQuery Overview:")
    for q in queries[:5]:
        title = q.get('title', 'N/A')[:60]
        print(f"  Query {{q.get('number')}}: {{title}}...")
    if total_queries > 5:
        print(f"  ... and {{total_queries - 5}} more queries")

print("="*80)
print("✅ Queries ready to execute!")
print("="*80)
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": cell_content.split('\n')
    }

def find_insertion_point(notebook: dict) -> int:
    """Find where to insert SQL/queries cells - after database connection, before query execution."""
    # Look for database connection cell
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'POSTGRESQL DATABASE CONNECTION' in source.upper() or 'CREATE_POSTGRESQL_CONNECTION' in source:
                # Insert after connection cell
                for j in range(i + 1, len(notebook['cells'])):
                    if notebook['cells'][j]['cell_type'] == 'code':
                        source_j = ''.join(notebook['cells'][j].get('source', []))
                        if 'LOAD QUERY METADATA' in source_j.upper() or 'QUERY METADATA' in source_j.upper():
                            return j  # Insert before query metadata loading
                        if 'EXECUTE' in source_j.upper() and 'QUERY' in source_j.upper():
                            return j  # Insert before query execution
                return i + 1
    
    # Fallback: after data directory detection
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell.get('source', []))
            if 'DATA DIRECTORY DETECTION' in source.upper():
                return i + 1
    
    return len(notebook['cells'])

def add_embedded_files(notebook_path: Path) -> bool:
    """Add embedded SQL and queries to notebook."""
    db_name = notebook_path.stem  # e.g., 'db-6'
    db_dir = notebook_path.parent
    
    print(f"\\nAdding embedded files: {notebook_path.name}")
    
    # Check if already embedded
    notebook = read_notebook(notebook_path)
    all_text = ''.join([''.join(c.get('source', [])) for c in notebook['cells']])
    if 'EMBEDDED SCHEMA.SQL' in all_text or 'EMBEDDED QUERIES.JSON' in all_text:
        print("   ✅ Embedded files already exist")
        return False
    
    # Read schema.sql
    schema_file = db_dir / 'data' / 'schema.sql'
    if not schema_file.exists():
        print(f"   ❌ schema.sql not found: {schema_file}")
        return False
    
    schema_content = schema_file.read_text(encoding='utf-8')
    print(f"   ✅ Read schema.sql ({len(schema_content)} chars)")
    
    # Read data.sql (optional)
    data_file = db_dir / 'data' / 'data.sql'
    data_content = None
    if data_file.exists():
        data_content = data_file.read_text(encoding='utf-8')
        print(f"   ✅ Read data.sql ({len(data_content)} chars)")
    else:
        print(f"   ⚠️  data.sql not found (optional)")
    
    # Read queries.json
    queries_file = db_dir / 'queries' / 'queries.json'
    if not queries_file.exists():
        print(f"   ❌ queries.json not found: {queries_file}")
        return False
    
    with open(queries_file, 'r', encoding='utf-8') as f:
        queries_data = json.load(f)
    print(f"   ✅ Read queries.json ({len(queries_data.get('queries', []))} queries)")
    
    # Find insertion point
    insert_idx = find_insertion_point(notebook)
    
    # Create cells
    cells_to_add = []
    
    # Add markdown header
    cells_to_add.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Embedded SQL Files and Queries\n",
            "\n",
            "The following cells contain the complete database schema, data, and queries embedded directly in this notebook.\n",
            "No external file dependencies required - everything is self-contained."
        ]
    })
    
    # Add schema.sql cell
    cells_to_add.append(create_schema_sql_cell(schema_content, db_name))
    
    # Add data.sql cell (if exists)
    if data_content:
        cells_to_add.append(create_data_sql_cell(data_content, db_name))
    
    # Add queries.json cell
    cells_to_add.append(create_queries_json_cell(queries_data, db_name))
    
    # Insert cells
    for i, cell in enumerate(cells_to_add):
        notebook['cells'].insert(insert_idx + i, cell)
    
    # Ensure proper newline formatting
    for cell in cells_to_add:
        if cell['cell_type'] == 'code':
            source = cell['source']
            for j in range(len(source) - 1):
                if source[j] and not source[j].endswith('\n'):
                    source[j] += '\n'
    
    write_notebook(notebook_path, notebook)
    print(f"   ✅ Added {len(cells_to_add)} cells (schema, {'data, ' if data_content else ''}queries)")
    return True

def main():
    """Main execution."""
    print("="*80)
    print("ADDING EMBEDDED SQL FILES AND QUERIES TO NOTEBOOKS")
    print("="*80)
    
    fixed_count = 0
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        if not db_dir.exists():
            continue
        
        notebook_path = db_dir / f"{db_name}.ipynb"
        if notebook_path.exists():
            if add_embedded_files(notebook_path):
                fixed_count += 1
    
    print("\\n" + "="*80)
    print(f"Updated notebooks: {fixed_count}")
    print("✅ EMBEDDED SQL AND QUERIES ADDED!")
    print("="*80)

if __name__ == '__main__':
    main()
