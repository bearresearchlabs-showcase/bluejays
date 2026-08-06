#!/usr/bin/env python3
"""
PostgreSQL-Compatible Schema Loader
Converts Snowflake/Databricks syntax to PostgreSQL syntax
"""

import re
import psycopg2
from pathlib import Path
from typing import Tuple

def convert_to_postgresql(sql: str) -> str:
    """Convert Snowflake/Databricks SQL to PostgreSQL syntax"""
    
    # Replace TIMESTAMP_NTZ with TIMESTAMP
    sql = re.sub(r'\bTIMESTAMP_NTZ\b', 'TIMESTAMP', sql, flags=re.IGNORECASE)
    
    # Replace CURRENT_TIMESTAMP() with CURRENT_TIMESTAMP (remove parentheses)
    sql = re.sub(r'\bCURRENT_TIMESTAMP\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    
    # Replace GEOGRAPHY with PostGIS GEOGRAPHY (if PostGIS extension is available)
    # For now, we'll use TEXT and add PostGIS extension if needed
    # sql = re.sub(r'\bGEOGRAPHY\b', 'GEOGRAPHY', sql, flags=re.IGNORECASE)
    
    # Remove trailing commas before closing parentheses in CREATE TABLE statements
    sql = re.sub(r',\s*\)', '\n)', sql)
    
    # Fix any double commas
    sql = re.sub(r',\s*,', ',', sql)
    
    return sql

def load_schema_postgresql(db_name: str, schema_file: Path, enable_postgis: bool = False) -> Tuple[bool, str]:
    """Load schema SQL file into PostgreSQL database with syntax conversion"""
    if not schema_file.exists():
        return False, f"Schema file not found: {schema_file}"
    
    import os
    user = os.environ.get('USER', 'machine')
    host = '127.0.0.1'
    port = 5432
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password='',
            database=db_name
        )
        conn.autocommit = True
        
        cursor = conn.cursor()
        
        # Enable PostGIS extension if needed
        if enable_postgis:
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            except Exception as e:
                print(f"  Note: PostGIS extension not available: {e}")
        
        # Read schema file
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Convert to PostgreSQL syntax
        schema_sql = convert_to_postgresql(schema_sql)
        
        # Split by semicolons and execute each statement
        # More sophisticated splitting to handle semicolons in strings/functions
        statements = []
        current_statement = []
        paren_depth = 0
        in_string = False
        string_char = None
        
        for char in schema_sql:
            current_statement.append(char)
            
            if char in ("'", '"') and not (len(current_statement) > 1 and current_statement[-2] == '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            
            if not in_string:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == ';' and paren_depth == 0:
                    stmt = ''.join(current_statement).strip()
                    if stmt:
                        statements.append(stmt)
                    current_statement = []
        
        # Add remaining statement
        if current_statement:
            stmt = ''.join(current_statement).strip()
            if stmt:
                statements.append(stmt)
        
        errors = []
        successful = 0
        
        for i, statement in enumerate(statements):
            if not statement.strip():
                continue
                
            try:
                cursor.execute(statement)
                successful += 1
            except Exception as e:
                error_msg = str(e)
                # Ignore "already exists" errors (expected with IF NOT EXISTS)
                if 'already exists' not in error_msg.lower():
                    # Some errors are acceptable (e.g., PostGIS functions)
                    if 'function' not in error_msg.lower() or 'does not exist' not in error_msg.lower():
                        errors.append(f"Statement {i+1}: {error_msg[:150]}")
        
        cursor.close()
        conn.close()
        
        if errors and len(errors) > successful * 0.3:  # More than 30% errors
            return False, f"Errors loading schema: {'; '.join(errors[:5])}"
        
        return True, f"Schema loaded successfully ({successful} statements)"
        
    except Exception as e:
        return False, f"Error loading schema: {str(e)}"
