#!/usr/bin/env python3
"""
Generate JSON deliverable for web deployment
"""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_table_info_from_schema(schema_file):
    """Extract table information from schema.sql"""
    schema_content = schema_file.read_text()
    tables = []
    
    # Find all CREATE TABLE statements
    table_pattern = r'CREATE TABLE (\w+) \((.*?)\);'
    matches = re.finditer(table_pattern, schema_content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        table_name = match.group(1)
        table_body = match.group(2)
        
        # Extract columns
        columns = []
        column_lines = [line.strip() for line in table_body.split('\n') if line.strip() and not line.strip().startswith('--')]
        
        for line in column_lines:
            if line.startswith('CREATE') or line.startswith('FOREIGN KEY') or line.startswith('UNIQUE') or line.startswith('PRIMARY KEY'):
                continue
            
            # Parse column definition
            parts = line.split()
            if len(parts) >= 2:
                col_name = parts[0]
                col_type = parts[1] if len(parts) > 1 else ''
                constraints = ' '.join(parts[2:]) if len(parts) > 2 else ''
                
                # Extract description from comment if present
                description = ''
                if '--' in line:
                    description = line.split('--', 1)[1].strip()
                
                columns.append({
                    "name": col_name,
                    "data_type": col_type,
                    "constraints": constraints,
                    "description": description
                })
        
        # Extract table description from comment before CREATE TABLE
        description = ""
        table_start = match.start()
        # Look for comment before table
        before_table = schema_content[max(0, table_start-500):table_start]
        comment_match = re.search(r'--\s*(.+?)\s*CREATE TABLE', before_table, re.DOTALL | re.IGNORECASE)
        if comment_match:
            description = comment_match.group(1).strip()
        
        tables.append({
            "name": table_name,
            "description": description or f"{table_name} table",
            "columns": columns
        })
    
    return tables

def main():
    script_dir = Path(__file__).parent
    db_dir = script_dir.parent
    
    # Read queries.json
    queries_file = db_dir / 'queries' / 'queries.json'
    with open(queries_file, 'r') as f:
        queries_data = json.load(f)
    
    # Read schema.sql
    schema_file = db_dir / 'data' / 'schema.sql'
    tables = extract_table_info_from_schema(schema_file)
    
    # Generate JSON deliverable
    deliverable = {
        "database": {
            "id": "db-8",
            "name": "Job Market Intelligence Database",
            "description": "This document provides comprehensive documentation for database db-8, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**, representing real-world enterprise implementations.",
            "created_date": "2026-02-04",
            "version": "1.0"
        },
        "schema": {
            "total_tables": len(tables),
            "tables": tables
        },
        "queries": queries_data['queries']
    }
    
    # Write JSON deliverable
    output_file = db_dir / 'deliverable' / 'db8-job-market-intelligence' / 'db-8_deliverable.json'
    with open(output_file, 'w') as f:
        json.dump(deliverable, f, indent=2, ensure_ascii=False)
    
    print(f"JSON deliverable Rebuilt: {output_file}")

if __name__ == '__main__':
    main()
