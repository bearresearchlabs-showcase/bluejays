#!/usr/bin/env python3
"""
Generate PostgreSQL database dump files from schema.sql and data_large.sql files.

This script creates PostgreSQL-compatible dump files that combine schema and data
into a single file that can be restored using psql.
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


def get_database_name(db_num):
    """Get database name from db number."""
    db_names = {
        6: "weather_consulting_insurance",
        7: "maritime_shipping_intelligence",
        8: "job_market_intelligence",
        9: "shipping_intelligence",
        10: "shopping_aggregator",
        11: "parking_intelligence",
        12: "credit_card_rewards",
        13: "ai_benchmark_marketing",
        14: "cloud_instance_cost",
        15: "electricity_solar_rebate"
    }
    return db_names.get(db_num, f"db_{db_num}")


def generate_postgresql_dump(db_num, root_dir=None):
    """
    Generate PostgreSQL dump file for a database.
    
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
    
    # Find schema files
    schema_files = []
    schema_dir = db_dir / "data"
    if schema_dir.exists():
        # Look for schema.sql first
        schema_sql = schema_dir / "schema.sql"
        if schema_sql.exists():
            schema_files.append(schema_sql)
        
        # Look for additional schema files
        for pattern in ["schema_extensions.sql", "*_schema.sql"]:
            for f in schema_dir.glob(pattern):
                if f.name != "schema.sql" and f not in schema_files:
                    schema_files.append(f)
    
    if not schema_files:
        logger.warning(f"No schema files found in {schema_dir}")
        return False
    
    # Find data file (prefer data_large.sql, fallback to data.sql)
    data_file = None
    if schema_dir.exists():
        data_large = schema_dir / "data_large.sql"
        data_sql = schema_dir / "data.sql"
        
        if data_large.exists():
            data_file = data_large
        elif data_sql.exists():
            data_file = data_sql
    
    if not data_file:
        logger.warning(f"No data file found in {schema_dir}")
        return False
    
    # Output dump file
    dump_file = schema_dir / f"db-{db_num}_postgresql.dump"
    db_name = get_database_name(db_num)
    
    logger.info(f"Generating PostgreSQL dump for db-{db_num} ({db_name})")
    logger.info(f"  Schema files: {[f.name for f in schema_files]}")
    logger.info(f"  Data file: {data_file.name}")
    logger.info(f"  Output: {dump_file.name}")
    
    try:
        with open(dump_file, 'w', encoding='utf-8') as out:
            # Write PostgreSQL dump header
            out.write("--\n")
            out.write(f"-- PostgreSQL database dump for {db_name}\n")
            out.write(f"-- Rebuilt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write(f"-- Database: db-{db_num}\n")
            out.write("--\n\n")
            
            # PostgreSQL configuration
            out.write("-- PostgreSQL configuration\n")
            out.write("SET statement_timeout = 0;\n")
            out.write("SET lock_timeout = 0;\n")
            out.write("SET idle_in_transaction_session_timeout = 0;\n")
            out.write("SET client_encoding = 'UTF8';\n")
            out.write("SET standard_conforming_strings = on;\n")
            out.write("SELECT pg_catalog.set_config('search_path', '', false);\n")
            out.write("SET check_function_bodies = false;\n")
            out.write("SET xmloption = content;\n")
            out.write("SET client_min_messages = warning;\n")
            out.write("SET row_security = off;\n\n")
            
            # Enable PostGIS extension if needed (check for GEOGRAPHY type)
            schema_content = ""
            for schema_file in schema_files:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_content += f.read() + "\n"
            
            if "GEOGRAPHY" in schema_content or "PostGIS" in schema_content:
                out.write("-- Enable PostGIS extension for spatial data\n")
                out.write("CREATE EXTENSION IF NOT EXISTS postgis;\n\n")
            
            # Write schema
            out.write("--\n")
            out.write("-- Database Schema\n")
            out.write("--\n\n")
            
            for schema_file in schema_files:
                logger.info(f"  Reading schema: {schema_file.name}")
                with open(schema_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace TIMESTAMP_NTZ with TIMESTAMP for PostgreSQL
                    content = content.replace("TIMESTAMP_NTZ", "TIMESTAMP")
                    out.write(f"-- Schema from {schema_file.name}\n")
                    out.write(content)
                    out.write("\n\n")
            
            # Write data
            out.write("--\n")
            out.write("-- Database Data\n")
            out.write("--\n\n")
            
            logger.info(f"  Reading data: {data_file.name}")
            file_size = data_file.stat().st_size
            logger.info(f"  Data file size: {file_size / (1024*1024):.2f} MB")
            
            # Read and write data in chunks to handle large files
            chunk_size = 1024 * 1024  # 1MB chunks
            with open(data_file, 'r', encoding='utf-8') as f:
                bytes_written = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    # Replace TIMESTAMP_NTZ with TIMESTAMP for PostgreSQL
                    chunk = chunk.replace("TIMESTAMP_NTZ", "TIMESTAMP")
                    out.write(chunk)
                    bytes_written += len(chunk)
                    if bytes_written % (10 * 1024 * 1024) == 0:  # Log every 10MB
                        logger.info(f"  Processed {bytes_written / (1024*1024):.2f} MB")
            
            # Write footer
            out.write("\n--\n")
            out.write("-- PostgreSQL database dump complete\n")
            out.write("--\n")
        
        dump_size = dump_file.stat().st_size
        logger.info(f"✓ Generated dump file: {dump_file.name} ({dump_size / (1024*1024):.2f} MB)")
        return True
        
    except Exception as e:
        logger.error(f"Error generating dump file: {e}")
        return False


def main():
    """Main function to generate dumps for specified databases."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate PostgreSQL dump files for databases"
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
    
    logger.info(f"Generating PostgreSQL dumps for databases: {db_numbers}")
    
    success_count = 0
    for db_num in db_numbers:
        if generate_postgresql_dump(db_num, root_dir):
            success_count += 1
        logger.info("")
    
    logger.info(f"Completed: {success_count}/{len(db_numbers)} databases processed successfully")
    
    return 0 if success_count == len(db_numbers) else 1


if __name__ == "__main__":
    sys.exit(main())
