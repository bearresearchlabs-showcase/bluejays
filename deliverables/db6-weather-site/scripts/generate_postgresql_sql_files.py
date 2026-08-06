#!/usr/bin/env python3
"""
Generate PostgreSQL-specific SQL files from cross-database compatible schema.sql and data.sql files.

This script creates PostgreSQL-optimized versions of schema and data files:
- schema_postgresql.sql: PostgreSQL-specific schema with TIMESTAMP instead of TIMESTAMP_NTZ
- data_postgresql.sql: PostgreSQL-specific data inserts
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_to_postgresql_sql(content):
    """
    Convert cross-database SQL to PostgreSQL-specific SQL.
    
    Conversions:
    - TIMESTAMP_NTZ -> TIMESTAMP
    - Ensure PostGIS extensions are enabled
    - PostgreSQL-specific optimizations
    """
    # Replace TIMESTAMP_NTZ with TIMESTAMP
    content = content.replace("TIMESTAMP_NTZ", "TIMESTAMP")
    
    # Ensure PostGIS is available for GEOGRAPHY types
    if "GEOGRAPHY" in content and "CREATE EXTENSION IF NOT EXISTS postgis" not in content:
        # Add PostGIS extension at the beginning if not present
        if not content.strip().startswith("--"):
            content = "-- Enable PostGIS extension for spatial data\nCREATE EXTENSION IF NOT EXISTS postgis;\n\n" + content
        else:
            # Find first CREATE statement and insert before it
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().upper().startswith('CREATE'):
                    insert_idx = i
                    break
            if insert_idx > 0:
                lines.insert(insert_idx, "-- Enable PostGIS extension for spatial data")
                lines.insert(insert_idx + 1, "CREATE EXTENSION IF NOT EXISTS postgis;")
                lines.insert(insert_idx + 2, "")
                content = '\n'.join(lines)
    
    return content


def generate_postgresql_sql_files(db_num, root_dir=None):
    """
    Generate PostgreSQL-specific SQL files for a database.
    
    Args:
        db_num: Database number (6-15)
        root_dir: Root directory path (defaults to script parent)
    """
    if root_dir is None:
        root_dir = Path(__file__).parent.parent
    
    db_dir = root_dir / f"db-{db_num}"
    
    if not db_dir.exists():
        logger.warning(f"Database directory not found: {db_dir}")
        return False
    
    data_dir = db_dir / "data"
    if not data_dir.exists():
        logger.warning(f"Data directory not found: {data_dir}")
        return False
    
    success_count = 0
    
    # Process schema files
    schema_files = []
    
    # Main schema.sql
    schema_sql = data_dir / "schema.sql"
    if schema_sql.exists():
        schema_files.append(schema_sql)
    
    # Additional schema files
    for pattern in ["schema_extensions.sql", "*_schema.sql"]:
        for f in data_dir.glob(pattern):
            if f.name != "schema.sql" and f not in schema_files:
                schema_files.append(f)
    
    # Generate PostgreSQL schema files
    for schema_file in schema_files:
        pg_schema_file = data_dir / f"{schema_file.stem}_postgresql.sql"
        
        try:
            logger.info(f"  Converting schema: {schema_file.name} -> {pg_schema_file.name}")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert to PostgreSQL
            pg_content = convert_to_postgresql_sql(content)
            
            # Add header comment
            header = f"""-- PostgreSQL-specific schema file
-- Generated from {schema_file.name}
-- Rebuilt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Database: db-{db_num}
-- 
-- This file contains PostgreSQL-specific SQL syntax.
-- Use this file when setting up the database in PostgreSQL.
--

"""
            
            with open(pg_schema_file, 'w', encoding='utf-8') as f:
                f.write(header)
                f.write(pg_content)
            
            success_count += 1
            logger.info(f"    ✓ Created {pg_schema_file.name}")
            
        except Exception as e:
            logger.error(f"    ✗ Error converting {schema_file.name}: {e}")
    
    # Process data files
    data_files = []
    
    # Prefer data_large.sql, fallback to data.sql
    data_large = data_dir / "data_large.sql"
    data_sql = data_dir / "data.sql"
    
    if data_large.exists():
        data_files.append(data_large)
    elif data_sql.exists():
        data_files.append(data_sql)
    
    # Generate PostgreSQL data files
    for data_file in data_files:
        pg_data_file = data_dir / f"{data_file.stem}_postgresql.sql"
        
        try:
            logger.info(f"  Converting data: {data_file.name} -> {pg_data_file.name}")
            
            file_size = data_file.stat().st_size
            logger.info(f"    Data file size: {file_size / (1024*1024):.2f} MB")
            
            # Read and convert in chunks for large files
            header = f"""-- PostgreSQL-specific data file
-- Generated from {data_file.name}
-- Rebuilt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Database: db-{db_num}
-- 
-- This file contains PostgreSQL-specific SQL syntax for data inserts.
-- Use this file when loading data into PostgreSQL.
-- 
-- Note: Ensure schema_postgresql.sql has been executed first.
--

"""
            
            with open(pg_data_file, 'w', encoding='utf-8') as out:
                out.write(header)
                
                chunk_size = 1024 * 1024  # 1MB chunks
                bytes_written = len(header.encode('utf-8'))
                
                with open(data_file, 'r', encoding='utf-8') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        # Convert to PostgreSQL
                        pg_chunk = convert_to_postgresql_sql(chunk)
                        out.write(pg_chunk)
                        
                        bytes_written += len(pg_chunk.encode('utf-8'))
                        if bytes_written % (10 * 1024 * 1024) == 0:  # Log every 10MB
                            logger.info(f"    Processed {bytes_written / (1024*1024):.2f} MB")
            
            pg_file_size = pg_data_file.stat().st_size
            logger.info(f"    ✓ Created {pg_data_file.name} ({pg_file_size / (1024*1024):.2f} MB)")
            success_count += 1
            
        except Exception as e:
            logger.error(f"    ✗ Error converting {data_file.name}: {e}")
    
    return success_count > 0


def main():
    """Main function to generate PostgreSQL SQL files for specified databases."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate PostgreSQL-specific SQL files for databases"
    )
    parser.add_argument(
        "db_numbers",
        nargs="*",
        type=int,
        help="Database numbers to process (e.g., 6 7 8). If not specified, processes db-6 through db-15."
    )
    parser.add_argument(
        "--root-dir",
        type=str,
        help="Root directory path (defaults to script parent)"
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.root_dir) if args.root_dir else Path(__file__).parent.parent
    
    # Determine which databases to process
    if args.db_numbers:
        db_numbers = args.db_numbers
    else:
        # Default: process db-6 through db-15
        db_numbers = list(range(6, 16))
    
    logger.info(f"Generating PostgreSQL SQL files for databases: {db_numbers}")
    logger.info("")
    
    success_count = 0
    for db_num in db_numbers:
        logger.info(f"Processing db-{db_num}...")
        if generate_postgresql_sql_files(db_num, root_dir):
            success_count += 1
        logger.info("")
    
    logger.info(f"Completed: {success_count}/{len(db_numbers)} databases processed successfully")
    
    return 0 if success_count == len(db_numbers) else 1


if __name__ == "__main__":
    sys.exit(main())
