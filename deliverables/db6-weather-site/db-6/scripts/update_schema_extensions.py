#!/usr/bin/env python3
"""
Update schema extensions for Databricks compatibility
Handles ALTER TABLE statements that may not work directly
"""

import json
import os
from pathlib import Path

try:
    import databricks.connector
except ImportError:
    print("❌ databricks-connector-python not installed")
    sys.exit(1)


def get_databricks_connection():
    """Get Databricks connection"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent.parent.parent
    creds_file = root_dir / 'results' / 'databricks_credentials.json'

    if not creds_file.exists():
        print(f"❌ Credentials file not found: {creds_file}")
        sys.exit(1)

    with open(creds_file, 'r') as f:
        creds = json.load(f)

    account = creds.get('databricks_account', '')
    user = creds.get('databricks_user', '')
    role = creds.get('databricks_role', 'ACCOUNTADMIN')
    token = creds.get('databricks_token', '')

    conn_params = {
        'account': account,
        'user': user,
        'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
        'database': os.getenv('SNOWFLAKE_DATABASE', 'DB6'),
        'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC'),
        'role': role
    }

    if token:
        conn_params['password'] = token
    else:
        conn_params['password'] = os.getenv('SNOWFLAKE_PASSWORD', '')

    try:
        conn = databricks.connector.connect(**conn_params)
        print(f"✅ Connected to Databricks: {account}")
        return conn
    except Exception as e:
        print(f"❌ Databricks connection failed: {e}")
        sys.exit(1)


def add_columns_safely(conn, table_name, columns):
    """Add columns to table if they don't exist"""
    cursor = conn.cursor()

    for col_def in columns:
        # Check if column exists
        check_sql = f"""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'PUBLIC'
        AND TABLE_NAME = '{table_name.upper()}'
        AND COLUMN_NAME = '{col_def['name'].upper()}'
        """

        cursor.execute(check_sql)
        exists = cursor.fetchone()[0] > 0

        if not exists:
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_def['name']} {col_def['type']}"
            if 'default' in col_def:
                alter_sql += f" DEFAULT {col_def['default']}"

            try:
                cursor.execute(alter_sql)
                print(f"  ✅ Added column {col_def['name']} to {table_name}")
            except Exception as e:
                print(f"  ⚠️  Error adding column {col_def['name']}: {e}")
        else:
            print(f"  ℹ️  Column {col_def['name']} already exists in {table_name}")

    conn.commit()
    cursor.close()


def main():
    """Update schema extensions"""
    print("="*70)
    print("UPDATING SCHEMA EXTENSIONS FOR DB-6")
    print("="*70)

    conn = get_databricks_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("USE DATABASE DB6")
        cursor.execute("USE SCHEMA PUBLIC")
        cursor.close()

        # Add columns to grib2_forecasts
        print("\n📝 Updating grib2_forecasts table...")
        add_columns_safely(conn, 'grib2_forecasts', [
            {'name': 'data_source', 'type': 'VARCHAR(50)', 'default': "'NDFD'"},
            {'name': 'model_name', 'type': 'VARCHAR(100)'},
            {'name': 'aws_bucket', 'type': 'VARCHAR(255)'},
            {'name': 'aws_file_path', 'type': 'VARCHAR(1000)'},
            {'name': 'ensemble_member', 'type': 'INTEGER'}
        ])

        # Add columns to weather_observations
        print("\n📝 Updating weather_observations table...")
        add_columns_safely(conn, 'weather_observations', [
            {'name': 'api_endpoint', 'type': 'VARCHAR(500)'},
            {'name': 'api_response_status', 'type': 'INTEGER'}
        ])

        # Create new tables from schema_extensions.sql
        print("\n📝 Creating new tables...")
        db_dir = Path(__file__).parent.parent
        schema_ext_file = db_dir / 'data' / 'schema_extensions.sql'

        if schema_ext_file.exists():
            with open(schema_ext_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract CREATE TABLE statements
            statements = [s.strip() for s in content.split(';') if s.strip()]
            create_statements = [s for s in statements if s.upper().startswith('CREATE TABLE')]

            cursor = conn.cursor()
            for stmt in create_statements:
                try:
                    cursor.execute(stmt)
                    table_name = stmt.split()[2] if len(stmt.split()) > 2 else 'unknown'
                    print(f"  ✅ Created table: {table_name}")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f"  ℹ️  Table already exists")
                    else:
                        print(f"  ⚠️  Error: {e}")

            conn.commit()
            cursor.close()

        print("\n✅ Schema extensions updated")

    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    main()
