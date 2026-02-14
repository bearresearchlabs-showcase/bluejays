#!/usr/bin/env python3
"""
Setup Snowflake database for db-6
Creates schema, loads data, and fixes Query 2 syntax
"""

import json
import os
import sys
from pathlib import Path

try:
    import snowflake.connector
except ImportError:
    print("❌ snowflake-connector-python not installed. Install with: pip install snowflake-connector-python")
    sys.exit(1)


def get_snowflake_connection():
    """Get Snowflake connection using credentials"""
    script_dir = Path(__file__).parent
    # Navigate from db-6/scripts/ to db/results/
    root_dir = script_dir.parent.parent  # db-6 -> db
    creds_file = root_dir / 'results' / 'snowflake_credentials.json'

    if not creds_file.exists():
        print(f"❌ Credentials file not found: {creds_file}")
        sys.exit(1)

    with open(creds_file, 'r') as f:
        creds = json.load(f)

    account = creds.get('snowflake_account', '')
    user = creds.get('snowflake_user', '')
    role = creds.get('snowflake_role', 'ACCOUNTADMIN')
    token = creds.get('snowflake_token', '')

    conn_params = {
        'account': account,
        'user': user,
        'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
        'database': os.getenv('SNOWFLAKE_DATABASE', 'DB6'),
        'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC'),
        'role': role
    }

    # Try different authentication methods
    if token:
        # Method 1: Try token as password without authenticator
        try:
            test_params = conn_params.copy()
            test_params['password'] = token
            conn = snowflake.connector.connect(**test_params)
            print(f"✅ Connected to Snowflake: {account}")
            return conn
        except Exception as e1:
            # Method 2: Try with oauth authenticator
            try:
                test_params = conn_params.copy()
                test_params['password'] = token
                test_params['authenticator'] = 'oauth'
                conn = snowflake.connector.connect(**test_params)
                print(f"✅ Connected to Snowflake: {account}")
                return conn
            except Exception as e2:
                print(f"⚠️  Token authentication failed, trying password...")
                print(f"   Error 1: {str(e1)[:100]}")
                print(f"   Error 2: {str(e2)[:100]}")

    # Try password-based authentication
    password = os.getenv('SNOWFLAKE_PASSWORD', '')
    if password:
        conn_params['password'] = password
        try:
            conn = snowflake.connector.connect(**conn_params)
            print(f"✅ Connected to Snowflake: {account}")
            return conn
        except Exception as e:
            print(f"❌ Password authentication failed: {e}")
            sys.exit(1)
    else:
        print(f"❌ No authentication method available (no token or password)")
        print(f"   Set SNOWFLAKE_PASSWORD environment variable or provide valid token")
        sys.exit(1)


def execute_sql_file(conn, sql_file, description):
    """Execute SQL file"""
    print(f"\n📝 {description}...")

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Remove comments and split by semicolons
    lines = sql_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove single-line comments
        if '--' in line:
            line = line[:line.index('--')]
        cleaned_lines.append(line)

    sql_content = '\n'.join(cleaned_lines)

    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]

    cursor = conn.cursor()
    success_count = 0
    error_count = 0

    # First pass: Create tables only
    table_statements = [s for s in statements if s.upper().startswith('CREATE TABLE')]
    index_statements = [s for s in statements if s.upper().startswith('CREATE INDEX')]

    print(f"  📊 Found {len(table_statements)} table statements, {len(index_statements)} index statements")

    # Create tables first
    for i, statement in enumerate(table_statements, 1):
        try:
            cursor.execute(statement)
            success_count += 1
            table_name = statement.split()[2] if len(statement.split()) > 2 else 'unknown'
            print(f"  ✅ Created table: {table_name}")
        except Exception as e:
            error_count += 1
            if 'already exists' in str(e).lower() or 'object already exists' in str(e).lower():
                print(f"  ℹ️  Table already exists (skipping)")
                success_count += 1
                error_count -= 1
            else:
                print(f"  ❌ Table creation failed: {str(e)[:150]}")

    # Then create indexes (skip GIST indexes)
    for i, statement in enumerate(index_statements, 1):
        try:
            # Skip index creation with USING GIST (Snowflake doesn't support this)
            if 'USING GIST' in statement.upper():
                print(f"  ⚠️  Skipping GIST index (not supported in Snowflake)")
                continue

            cursor.execute(statement)
            success_count += 1
        except Exception as e:
            error_count += 1
            if 'already exists' in str(e).lower() or 'object already exists' in str(e).lower():
                print(f"  ℹ️  Index already exists (skipping)")
                success_count += 1
                error_count -= 1
            else:
                print(f"  ❌ Index creation failed: {str(e)[:100]}")

    cursor.close()
    print(f"  ✅ Completed: {success_count} successful, {error_count} errors")
    return success_count, error_count


def fix_query2_syntax():
    """Fix Query 2 array syntax for Snowflake compatibility"""
    script_dir = Path(__file__).parent
    queries_file = script_dir.parent / 'queries' / 'queries.md'

    print(f"\n🔧 Fixing Query 2 syntax for Snowflake compatibility...")

    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find Query 2 SQL block
    query2_start = content.find('## Query 2:')
    if query2_start == -1:
        print("  ⚠️  Query 2 not found")
        return False

    # Find the SQL block for Query 2
    sql_start = content.find('```sql', query2_start)
    sql_end = content.find('```', sql_start + 6)

    if sql_start == -1 or sql_end == -1:
        print("  ⚠️  Query 2 SQL block not found")
        return False

    sql_block = content[sql_start + 6:sql_end]

    # Fix array syntax
    fixes = [
        # ARRAY[...] -> ARRAY_CONSTRUCT(...)
        (r'ARRAY\[([^\]]+)\]', r'ARRAY_CONSTRUCT(\1)'),
        # ARRAY_LENGTH(array, 1) -> ARRAY_SIZE(array)
        (r'ARRAY_LENGTH\(([^,]+),\s*1\)', r'ARRAY_SIZE(\1)'),
        # array || value -> ARRAY_APPEND(array, value)
        (r'(\w+)\.boundary_path\s*\|\|\s*(\w+)\.boundary_id', r'ARRAY_APPEND(\1.boundary_path, \2.boundary_id)'),
        # array[2:] -> ARRAY_SLICE(array, 2)
        (r'(\w+)\.boundary_path\[2:\]', r'ARRAY_SLICE(\1.boundary_path, 2)'),
        # != ALL(array) -> NOT ARRAY_CONTAINS(value, array) or use different approach
        (r'(\w+)\.boundary_id\s*!=\s*ALL\(([^)]+)\)', r'NOT ARRAY_CONTAINS(\1.boundary_id, \2)'),
    ]

    original_sql = sql_block
    fixed_sql = sql_block

    import re
    for pattern, replacement in fixes:
        fixed_sql = re.sub(pattern, replacement, fixed_sql)

    if fixed_sql != original_sql:
        # Replace in content
        new_content = content[:sql_start + 6] + fixed_sql + content[sql_end:]

        # Backup original
        backup_file = queries_file.with_suffix('.md.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  💾 Backup saved to: {backup_file}")

        # Write fixed version
        with open(queries_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ Query 2 syntax fixed")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False


def main():
    """Main execution"""
    print("="*70)
    print("SNOWFLAKE DATABASE SETUP FOR DB-6")
    print("="*70)

    script_dir = Path(__file__).parent
    db_dir = script_dir.parent

    # Connect to Snowflake
    conn = get_snowflake_connection()

    try:
        # Create database and schema if needed
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS DB6")
        cursor.execute("USE DATABASE DB6")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
        cursor.execute("USE SCHEMA PUBLIC")
        cursor.close()
        print("\n✅ Database and schema ready")

        # Load schema
        schema_file = db_dir / 'data' / 'schema.sql'
        if schema_file.exists():
            execute_sql_file(conn, schema_file, "Loading schema")
        else:
            print(f"❌ Schema file not found: {schema_file}")

        # Load schema extensions
        schema_ext_file = db_dir / 'data' / 'schema_extensions.sql'
        if schema_ext_file.exists():
            execute_sql_file(conn, schema_ext_file, "Loading schema extensions")
        else:
            print(f"⚠️  Schema extensions file not found: {schema_ext_file}")

        # Load data - handle INSERT statements differently
        data_file = db_dir / 'data' / 'data.sql'
        if data_file.exists():
            print(f"\n📝 Loading sample data...")
            with open(data_file, 'r', encoding='utf-8') as f:
                data_content = f.read()

            # Remove comments and split by semicolons
            lines = data_content.split('\n')
            cleaned_lines = []
            for line in lines:
                # Remove single-line comments but keep INSERT statements
                if line.strip().startswith('--'):
                    continue
                cleaned_lines.append(line)

            data_content = '\n'.join(cleaned_lines)

            # Split by semicolons and filter INSERT statements
            statements = [s.strip() for s in data_content.split(';') if s.strip()]
            insert_statements = [s for s in statements if s.upper().startswith('INSERT')]

            cursor = conn.cursor()
            success_count = 0
            error_count = 0

            print(f"  📊 Found {len(insert_statements)} INSERT statements")

            for i, statement in enumerate(insert_statements, 1):
                try:
                    cursor.execute(statement)
                    success_count += 1
                    if i % 3 == 0 or i == len(insert_statements):
                        print(f"  ✅ Loaded {i}/{len(insert_statements)} insert statements...")
                except Exception as e:
                    error_count += 1
                    if 'duplicate' in str(e).lower() or 'already exists' in str(e).lower() or 'unique constraint' in str(e).lower():
                        print(f"  ℹ️  Insert {i}: Data already exists (skipping)")
                        success_count += 1
                        error_count -= 1
                    else:
                        print(f"  ❌ Insert {i} failed: {str(e)[:150]}")

            cursor.close()
            print(f"  ✅ Completed: {success_count} successful, {error_count} errors")
        else:
            print(f"⚠️  Data file not found: {data_file}")

        # Fix Query 2
        fix_query2_syntax()

        print("\n" + "="*70)
        print("SETUP COMPLETE")
        print("="*70)
        print("\nNext steps:")
        print("1. Run: python3 scripts/testing/test_db6_queries.py")
        print("2. Check results in: db-6/results/query_test_results_postgres_snowflake.json")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
