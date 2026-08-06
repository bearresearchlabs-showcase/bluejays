#!/usr/bin/env python3
"""
Load database schemas into PostgreSQL instances
Creates tables based on schema definitions from queries.md files
"""

import os
import sys
import psycopg2
import re
from pathlib import Path
from typing import Dict, List

# Port mapping for each database
PORT_MAPPING = {
    1: 5432,
    2: 5433,
    3: 5434,
    4: 5435,
    5: 5436
}

def get_postgres_connection(db_num: int):
    """Get PostgreSQL connection for database number"""
    port = PORT_MAPPING.get(db_num, 5432)
    conn_params = {
        'host': '127.0.0.1',
        'port': port,
        'database': f'db{db_num}',
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'connect_timeout': 10
    }
    return psycopg2.connect(**conn_params)

def extract_schema_from_queries_md(queries_file: Path) -> Dict[str, List[Dict]]:
    """Extract table definitions from queries.md file"""
    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    tables = {}
    current_table = None
    current_columns = []

    # Find table definitions (between ### `table_name` and next ###)
    table_pattern = r'### `([^`]+)`\s*\n\n\| Column \| Type \|'
    matches = list(re.finditer(table_pattern, content))

    for i, match in enumerate(matches):
        table_name = match.group(1)
        start_pos = match.end()

        # Find end of table definition (next ### or ---)
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            # Find next section marker
            next_section = re.search(r'\n---\n|\n## ', content[start_pos:])
            end_pos = start_pos + (next_section.start() if next_section else len(content))

        table_section = content[start_pos:end_pos]

        # Extract column definitions
        columns = []
        column_lines = re.findall(r'\| `([^`]+)` \| `([^`]+)` \|', table_section)
        for col_name, col_type in column_lines:
            # Convert Databricks types to PostgreSQL
            pg_type = convert_type_to_postgres(col_type)
            columns.append({
                'name': col_name,
                'type': pg_type
            })

        if columns:
            tables[table_name] = columns

    return tables

def convert_type_to_postgres(databricks_type: str) -> str:
    """Convert Databricks type to PostgreSQL type"""
    type_mapping = {
        'UUID': 'UUID',
        'VARCHAR(255)': 'VARCHAR(255)',
        'VARCHAR(16777216)': 'TEXT',
        'VARCHAR(50)': 'VARCHAR(50)',
        'VARCHAR(100)': 'VARCHAR(100)',
        'VARCHAR(20)': 'VARCHAR(20)',
        'TIMESTAMP_NTZ': 'TIMESTAMP',
        'BOOLEAN': 'BOOLEAN',
        'INTEGER': 'INTEGER',
        'ARRAY(VARCHAR)': 'TEXT[]',
        'VARIANT': 'JSONB'
    }

    # Check exact matches first
    if databricks_type in type_mapping:
        return type_mapping[databricks_type]

    # Check partial matches
    for sf_type, pg_type in type_mapping.items():
        if databricks_type.startswith(sf_type.split('(')[0]):
            return pg_type

    # Default to TEXT for unknown types
    return 'TEXT'

def create_table_sql(table_name: str, columns: List[Dict]) -> str:
    """Generate CREATE TABLE SQL statement"""
    col_defs = []
    for col in columns:
        col_name = col['name']
        col_type = col['type']

        # Handle primary keys (id columns)
        if col_name == 'id' and col_type == 'UUID':
            col_defs.append(f'"{col_name}" {col_type} PRIMARY KEY DEFAULT gen_random_uuid()')
        elif col_name == 'id':
            col_defs.append(f'"{col_name}" {col_type} PRIMARY KEY')
        else:
            col_defs.append(f'"{col_name}" {col_type}')

    return f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    {",\n    ".join(col_defs)}\n);'

def load_schema_from_dump(db_num: int, dump_file: Path):
    """Load schema from PostgreSQL dump file using psql"""
    import subprocess

    port = PORT_MAPPING.get(db_num, 5432)
    db_name = f'db{db_num}'
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')

    # Use psql to load the dump file
    env = os.environ.copy()
    env['PGPASSWORD'] = password

    cmd = [
        'psql',
        '-h', '127.0.0.1',
        '-p', str(port),
        '-U', user,
        '-d', db_name,
        '-f', str(dump_file),
        '-q',  # Quiet mode
        '-v', 'ON_ERROR_STOP=0'  # Continue on errors
    ]

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Filter out common warnings
        errors = []
        for line in result.stderr.split('\n'):
            if line.strip():
                # Ignore common non-critical errors
                if any(ignore in line.lower() for ignore in [
                    'does not exist',
                    'already exists',
                    'extension',
                    'pg_graphql',
                    'supabase',
                    'pg_stat_statements',
                    'pgcrypto',
                    'pgjwt',
                    'uuid-ossp',
                    'schema "extensions"',
                    'current transaction is aborted'
                ]):
                    continue
                errors.append(line)

        if errors:
            print(f"  ⚠ Some warnings (non-critical): {len(errors)} lines")

        if result.returncode == 0 or 'CREATE TABLE' in result.stdout or 'CREATE TABLE' in result.stderr:
            print(f"  ✓ Schema loaded from dump file")
            return True
        else:
            print(f"  ⚠ psql returned code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout loading dump file")
        return False
    except Exception as e:
        print(f"  ❌ Error loading dump: {e}")
        return False

def load_schema_from_queries_md(db_num: int, queries_file: Path):
    """Load schema by extracting from queries.md and creating tables"""
    conn = get_postgres_connection(db_num)
    cursor = conn.cursor()

    try:
        tables = extract_schema_from_queries_md(queries_file)

        if not tables:
            print(f"  ⚠ No tables found in queries.md, trying dump file...")
            return False

        # Create extension for UUID if needed
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        except:
            pass

        # Create each table
        for table_name, columns in tables.items():
            try:
                create_sql = create_table_sql(table_name, columns)
                cursor.execute(create_sql)
                print(f"  ✓ Created table: {table_name}")
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    print(f"  ⚠ Warning creating {table_name}: {e}")

        conn.commit()
        print(f"  ✓ Schema loaded from queries.md ({len(tables)} tables)")
        return True

    except Exception as e:
        print(f"  ❌ Error loading schema: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Load schemas for all databases"""
    root_dir = Path(__file__).parent.parent.parent

    print("=" * 70)
    print("LOADING DATABASE SCHEMAS INTO POSTGRESQL")
    print("=" * 70)

    for db_num in range(1, 6):
        print(f"\n📊 Loading schema for db-{db_num}...")

        db_dir = root_dir / f'db-{db_num}'
        queries_file = db_dir / 'queries' / 'queries.md'

        # Try to find dump file first
        dump_files = list(db_dir.rglob('*.sql'))
        dump_file = None
        for df in dump_files:
            if 'dump' in df.name.lower() or 'schema' in df.name.lower():
                dump_file = df
                break

        success = False

        # Try loading from dump file first (more complete)
        if dump_file and dump_file.exists():
            print(f"  Found dump file: {dump_file.name}")
            load_schema_from_dump(db_num, dump_file)
            success = True
        elif queries_file.exists():
            print(f"  Loading from queries.md...")
            success = load_schema_from_queries_md(db_num, queries_file)

        if not success:
            print(f"  ❌ Could not load schema for db-{db_num}")

    print("\n" + "=" * 70)
    print("SCHEMA LOADING COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()
