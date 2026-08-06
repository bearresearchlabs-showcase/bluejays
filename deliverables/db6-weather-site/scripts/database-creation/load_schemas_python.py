#!/usr/bin/env python3
"""
Load database schemas into PostgreSQL instances using Python
Properly parses SQL dump files and executes CREATE TABLE statements
"""

import os
import psycopg2
import re
from pathlib import Path
from typing import List

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

def split_sql_statements(content: str) -> List[str]:
    """Split SQL content into individual statements"""
    # Remove comments
    content = re.sub(r'--.*?$', '', content, flags=re.MULTILINE)

    # Split by semicolons, but preserve strings
    statements = []
    current = []
    in_string = False
    string_char = None
    i = 0

    while i < len(content):
        char = content[i]

        if not in_string:
            if char in ("'", '"'):
                in_string = True
                string_char = char
                current.append(char)
            elif char == ';':
                stmt = ''.join(current).strip()
                if stmt and not stmt.startswith('SET ') and 'CREATE' in stmt.upper():
                    statements.append(stmt)
                current = []
            else:
                current.append(char)
        else:
            current.append(char)
            if char == string_char and (i == 0 or content[i-1] != '\\'):
                in_string = False
                string_char = None

        i += 1

    # Add remaining
    if current:
        stmt = ''.join(current).strip()
        if stmt and not stmt.startswith('SET ') and 'CREATE' in stmt.upper():
            statements.append(stmt)

    return statements

def load_schema_from_dump(db_num: int, dump_file: Path):
    """Load schema from PostgreSQL dump file"""
    conn = get_postgres_connection(db_num)
    cursor = conn.cursor()

    try:
        with open(dump_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Create extensions first
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        except:
            pass

        # Create extensions schema if needed
        try:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS extensions;")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\" SCHEMA extensions;")
        except:
            pass

        # Extract CREATE TABLE statements more carefully
        # Look for CREATE TABLE ... ( ... );
        create_table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?([^\s(]+)\s*\([^;]+?\);'

        matches = list(re.finditer(create_table_pattern, content, re.DOTALL | re.IGNORECASE))

        tables_created = 0
        for match in matches:
            table_sql = match.group(0)

            # Fix schema references
            table_sql = re.sub(r'"extensions"\.', '', table_sql)
            table_sql = re.sub(r'extensions\.uuid_generate_v4', 'gen_random_uuid', table_sql)
            table_sql = re.sub(r'uuid_generate_v4\(\)', 'gen_random_uuid()', table_sql)

            # Remove problematic parts
            table_sql = re.sub(r'SET\s+[^;]+;', '', table_sql, flags=re.IGNORECASE)
            table_sql = re.sub(r'SELECT\s+pg_catalog\.[^;]+;', '', table_sql, flags=re.IGNORECASE)

            try:
                cursor.execute(table_sql)
                tables_created += 1
            except Exception as e:
                error_msg = str(e).lower()
                if 'already exists' not in error_msg and 'duplicate' not in error_msg:
                    # Try to extract table name for better error reporting
                    table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?([^\s(]+)', table_sql, re.IGNORECASE)
                    table_name = table_match.group(1) if table_match else 'unknown'
                    print(f"    ⚠ Warning creating table {table_name}: {str(e)[:80]}")

        conn.commit()
        print(f"  ✓ Created {tables_created} tables from dump file")
        return tables_created > 0

    except Exception as e:
        print(f"  ❌ Error loading dump: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def load_schema_from_queries_md(db_num: int, queries_file: Path):
    """Load schema by extracting from queries.md and creating tables"""
    conn = get_postgres_connection(db_num)
    cursor = conn.cursor()

    try:
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create extension for UUID if needed
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        except:
            pass

        # Extract table definitions
        tables = {}
        table_pattern = r'### `([^`]+)`\s*\n\n\| Column \| Type \|'
        matches = list(re.finditer(table_pattern, content))

        for i, match in enumerate(matches):
            table_name = match.group(1)
            start_pos = match.end()

            # Find end of table definition
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                next_section = re.search(r'\n---\n|\n## ', content[start_pos:])
                end_pos = start_pos + (next_section.start() if next_section else len(content))

            table_section = content[start_pos:end_pos]

            # Extract column definitions
            columns = []
            column_lines = re.findall(r'\| `([^`]+)` \| `([^`]+)` \|', table_section)
            for col_name, col_type in column_lines:
                # Convert Databricks types to PostgreSQL
                pg_type = convert_type_to_postgres(col_type)
                columns.append({'name': col_name, 'type': pg_type})

            if columns:
                tables[table_name] = columns

        # Create tables
        for table_name, columns in tables.items():
            col_defs = []
            for col in columns:
                col_name = col['name']
                col_type = col['type']

                if col_name == 'id' and col_type == 'UUID':
                    col_defs.append(f'"{col_name}" {col_type} PRIMARY KEY DEFAULT gen_random_uuid()')
                elif col_name == 'id':
                    col_defs.append(f'"{col_name}" {col_type} PRIMARY KEY')
                else:
                    col_defs.append(f'"{col_name}" {col_type}')

            create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    {",\n    ".join(col_defs)}\n);'

            try:
                cursor.execute(create_sql)
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    print(f"    ⚠ Warning creating {table_name}: {e}")

        conn.commit()
        print(f"  ✓ Created {len(tables)} tables from queries.md")
        return len(tables) > 0

    except Exception as e:
        print(f"  ❌ Error loading schema: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

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

    if databricks_type in type_mapping:
        return type_mapping[databricks_type]

    for sf_type, pg_type in type_mapping.items():
        if databricks_type.startswith(sf_type.split('(')[0]):
            return pg_type

    return 'TEXT'

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

        # Find dump file
        dump_files = list(db_dir.rglob('*.sql'))
        dump_file = None
        for df in dump_files:
            name_lower = df.name.lower()
            if 'dump' in name_lower or 'schema' in name_lower or 'full' in name_lower:
                if 'data' not in name_lower or dump_file is None:
                    dump_file = df

        success = False

        # Try loading from dump file first
        if dump_file and dump_file.exists():
            print(f"  Found dump file: {dump_file.name}")
            success = load_schema_from_dump(db_num, dump_file)

        # Fallback to queries.md if dump didn't work
        if not success and queries_file.exists():
            print(f"  Loading from queries.md...")
            success = load_schema_from_queries_md(db_num, queries_file)

        if not success:
            print(f"  ❌ Could not load schema for db-{db_num}")

    print("\n" + "=" * 70)
    print("SCHEMA LOADING COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()
