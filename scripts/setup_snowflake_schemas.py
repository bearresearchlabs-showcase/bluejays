#!/usr/bin/env python3
"""
Setup Snowflake schemas for db-1 through db-5
Creates databases, schemas, and basic table structures based on query requirements
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
    root_dir = script_dir.parent
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
        'role': role
    }

    # Try token authentication
    if token:
        try:
            conn_params['password'] = token
            conn = snowflake.connector.connect(**conn_params)
            print(f"✅ Connected to Snowflake: {account}")
            return conn
        except Exception as e:
            print(f"⚠️  Token auth failed: {str(e)[:100]}")
            print("   Trying password authentication...")

    # Try password
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
        print(f"❌ No authentication method available")
        sys.exit(1)


def create_db1_schema(cursor):
    """Create schema for db-1 (chat/messaging application)"""
    print("\n📝 Creating DB1 schema...")

    # Create database and schema
    cursor.execute("CREATE DATABASE IF NOT EXISTS DB1")
    cursor.execute("USE DATABASE DB1")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    cursor.execute("USE SCHEMA PUBLIC")

    # Tables based on queries
    tables = [
        """CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            username VARCHAR(255),
            created_at TIMESTAMP_NTZ
        )""",
        """CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY,
            title VARCHAR(255),
            created_at TIMESTAMP_NTZ
        )""",
        """CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            sender_id INTEGER,
            content TEXT,
            is_ai BOOLEAN,
            created_at TIMESTAMP_NTZ
        )""",
        """CREATE TABLE IF NOT EXISTS chat_participants (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            user_id INTEGER,
            joined_at TIMESTAMP_NTZ
        )""",
        """CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            friend_id INTEGER,
            status VARCHAR(50)
        )""",
        """CREATE TABLE IF NOT EXISTS file_attachments (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            file_name VARCHAR(255),
            file_type VARCHAR(100),
            file_size INTEGER,
            uploaded_at TIMESTAMP_NTZ
        )""",
        """CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            type VARCHAR(100),
            read BOOLEAN,
            seen BOOLEAN,
            created_at TIMESTAMP_NTZ,
            seen_at TIMESTAMP_NTZ
        )"""
    ]

    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            table_name = table_sql.split()[5] if len(table_sql.split()) > 5 else 'unknown'
            print(f"  ✅ Created table: {table_name}")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"  ℹ️  Table already exists (skipping)")
            else:
                print(f"  ⚠️  Table creation: {str(e)[:100]}")


def create_db2_schema(cursor):
    """Create schema for db-2 (e-commerce)"""
    print("\n📝 Creating DB2 schema...")

    cursor.execute("CREATE DATABASE IF NOT EXISTS DB2")
    cursor.execute("USE DATABASE DB2")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    cursor.execute("USE SCHEMA PUBLIC")

    tables = [
        """CREATE TABLE IF NOT EXISTS affiliates_affiliatelink (
            id INTEGER PRIMARY KEY,
            marketer_id INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS affiliates_clicktracking (
            id INTEGER PRIMARY KEY,
            affiliate_link_id INTEGER,
            landing_page_url VARCHAR(500),
            created_at TIMESTAMP_NTZ
        )""",
        """CREATE TABLE IF NOT EXISTS orders_order (
            id INTEGER PRIMARY KEY,
            customer_order_id INTEGER,
            marketer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            total_price DECIMAL(10,2),
            created_at TIMESTAMP_NTZ
        )""",
        """CREATE TABLE IF NOT EXISTS commissions_commission (
            id INTEGER PRIMARY KEY,
            marketer_id INTEGER,
            amount DECIMAL(10,2),
            status VARCHAR(50)
        )""",
        """CREATE TABLE IF NOT EXISTS authentication_user (
            id INTEGER PRIMARY KEY,
            username VARCHAR(255)
        )""",
        """CREATE TABLE IF NOT EXISTS products_product (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            category_id INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS products_productcategory (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            parent_id INTEGER
        )"""
    ]

    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            table_name = table_sql.split()[5] if len(table_sql.split()) > 5 else 'unknown'
            print(f"  ✅ Created table: {table_name}")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"  ℹ️  Table already exists (skipping)")
            else:
                print(f"  ⚠️  Table creation: {str(e)[:100]}")


def create_db3_schema(cursor):
    """Create schema for db-3"""
    print("\n📝 Creating DB3 schema...")

    cursor.execute("CREATE DATABASE IF NOT EXISTS DB3")
    cursor.execute("USE DATABASE DB3")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    cursor.execute("USE SCHEMA PUBLIC")

    # Basic schema - adjust based on actual queries
    tables = [
        """CREATE TABLE IF NOT EXISTS delivered (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            name VARCHAR(255),
            value DECIMAL(10,2),
            date_col TIMESTAMP_NTZ,
            category VARCHAR(100),
            created_at TIMESTAMP_NTZ
        )"""
    ]

    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            table_name = table_sql.split()[5] if len(table_sql.split()) > 5 else 'unknown'
            print(f"  ✅ Created table: {table_name}")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"  ℹ️  Table already exists (skipping)")
            else:
                print(f"  ⚠️  Table creation: {str(e)[:100]}")


def create_db4_schema(cursor):
    """Create schema for db-4"""
    print("\n📝 Creating DB4 schema...")

    cursor.execute("CREATE DATABASE IF NOT EXISTS DB4")
    cursor.execute("USE DATABASE DB4")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    cursor.execute("USE SCHEMA PUBLIC")

    # Similar to db-3
    tables = [
        """CREATE TABLE IF NOT EXISTS delivered (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            name VARCHAR(255),
            value DECIMAL(10,2),
            date_col TIMESTAMP_NTZ,
            category VARCHAR(100),
            created_at TIMESTAMP_NTZ
        )"""
    ]

    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            table_name = table_sql.split()[5] if len(table_sql.split()) > 5 else 'unknown'
            print(f"  ✅ Created table: {table_name}")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"  ℹ️  Table already exists (skipping)")
            else:
                print(f"  ⚠️  Table creation: {str(e)[:100]}")


def create_db5_schema(cursor):
    """Create schema for db-5"""
    print("\n📝 Creating DB5 schema...")

    cursor.execute("CREATE DATABASE IF NOT EXISTS DB5")
    cursor.execute("USE DATABASE DB5")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
    cursor.execute("USE SCHEMA PUBLIC")

    # Basic schema - adjust based on actual queries
    tables = [
        """CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            customer_id INTEGER,
            amount DECIMAL(10,2),
            sale_date DATE,
            created_at TIMESTAMP_NTZ
        )""",
        """CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            category_id INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            created_at TIMESTAMP_NTZ
        )"""
    ]

    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            table_name = table_sql.split()[5] if len(table_sql.split()) > 5 else 'unknown'
            print(f"  ✅ Created table: {table_name}")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print(f"  ℹ️  Table already exists (skipping)")
            else:
                print(f"  ⚠️  Table creation: {str(e)[:100]}")


def main():
    """Main execution"""
    print("="*70)
    print("SNOWFLAKE SCHEMA SETUP FOR DB-1 THROUGH DB-5")
    print("="*70)

    # Connect to Snowflake
    conn = get_snowflake_connection()

    try:
        cursor = conn.cursor()

        # Create schemas for each database
        create_db1_schema(cursor)
        create_db2_schema(cursor)
        create_db3_schema(cursor)
        create_db4_schema(cursor)
        create_db5_schema(cursor)

        cursor.close()

        print("\n" + "="*70)
        print("SETUP COMPLETE")
        print("="*70)
        print("\nNext steps:")
        print("1. Run: python3 scripts/run_execution_testing.py 1 5")
        print("2. Check results in: db-{N}/results/execution_test_results.json")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
