#!/usr/bin/env python3
"""
Generate JSON deliverable files for all databases.

This script creates db-{N}_deliverable.json files in the web-deployable folders
by extracting schema information and query metadata.
"""

import json
import re
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Database name mappings
DB_NAMES = {
    6: "Weather Data Pipeline System",
    7: "Maritime Shipping Intelligence System",
    8: "Job Market Intelligence and Targeted Application System",
    9: "Shipping Rate Comparison and Cost Optimization Platform",
    10: "Shopping Aggregator and Retail Intelligence Platform",
    11: "Parking Intelligence and Marketplace Platform",
    12: "Credit Card Rewards Optimization and Portfolio Management Platform",
    13: "AI Model Benchmark Tracking and Marketing Intelligence Platform",
    14: "Cloud Instance Cost Optimization and Comparison Platform",
    15: "Electricity Cost and Solar Rebate Intelligence Platform",
}

DB_WEB_FOLDER_NAMES = {
    6: "db6-weather-consulting-insurance",
    7: "db7-maritime-shipping-intelligence",
    8: "db8-job-market-intelligence",
    9: "db9-shipping-intelligence",
    10: "db10-marketing-intelligence",
    11: "db11-parking-intelligence",
    12: "db12-credit-card-and-rewards-optimization-system",
    13: "db13-ai-benchmark-marketing-database",
    14: "db14-cloud-instance-cost-database",
    15: "db15-electricity-cost-and-solar-rebate-database",
}


def extract_table_info_from_schema(schema_file):
    """Extract table information from schema.sql"""
    try:
        schema_content = schema_file.read_text(encoding='utf-8')
    except Exception as e:
        logger.warning(f"Could not read schema file: {e}")
        return []

    tables = []

    # Find all CREATE TABLE statements
    # Pattern: CREATE TABLE table_name (columns...);
    table_pattern = r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);'
    matches = re.finditer(table_pattern, schema_content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        table_name = match.group(1)
        table_body = match.group(2)

        # Extract columns
        columns = []
        lines = table_body.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('--'):
                continue

            # Skip constraint definitions
            if any(keyword in line.upper() for keyword in ['PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CONSTRAINT', 'INDEX']):
                continue

            # Parse column definition: name type constraints
            # Handle cases like: column_name VARCHAR(255) PRIMARY KEY,
            parts = re.split(r'\s+', line, 2)
            if len(parts) >= 2:
                col_name = parts[0].strip()
                col_type = parts[1].strip()
                constraints = parts[2].strip().rstrip(',') if len(parts) > 2 else ''

                # Extract description from comment if present
                description = ''
                if '--' in line:
                    comment_part = line.split('--', 1)[1]
                    description = comment_part.strip()

                columns.append({
                    "name": col_name,
                    "data_type": col_type,
                    "constraints": constraints,
                    "description": description or "-"
                })

        # Extract table description from comment before CREATE TABLE
        description = ""
        table_start = match.start()
        before_table = schema_content[max(0, table_start-500):table_start]
        comment_match = re.search(r'--\s*(.+?)\s*CREATE\s+TABLE', before_table, re.DOTALL | re.IGNORECASE)
        if comment_match:
            description = comment_match.group(1).strip()

        tables.append({
            "name": table_name,
            "description": description or f"{table_name} table",
            "columns": columns
        })

    return tables


def generate_json_deliverable(db_num, root_dir=None):
    """Generate JSON deliverable for a database."""
    if root_dir is None:
        root_dir = Path(__file__).parent.parent

    db_dir = root_dir / f"db-{db_num}"
    deliverable_dir = db_dir / "deliverable"
    web_folder_name = DB_WEB_FOLDER_NAMES.get(db_num)

    if not web_folder_name:
        logger.warning(f"No web folder name defined for db-{db_num}")
        return False

    web_folder = deliverable_dir / web_folder_name
    if not web_folder.exists():
        logger.warning(f"Web folder not found: {web_folder}")
        return False

    output_file = web_folder / f"db-{db_num}_deliverable.json"

    logger.info(f"Generating JSON deliverable for db-{db_num}...")

    # Read queries.json
    queries_file = db_dir / 'queries' / 'queries.json'
    queries_data = None
    if queries_file.exists():
        try:
            with open(queries_file, 'r', encoding='utf-8') as f:
                queries_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not read queries.json: {e}")
    else:
        logger.warning(f"queries.json not found: {queries_file}")

    # Read schema.sql
    schema_file = db_dir / 'data' / 'schema.sql'
    tables = []
    if schema_file.exists():
        tables = extract_table_info_from_schema(schema_file)
    else:
        logger.warning(f"schema.sql not found: {schema_file}")

    # Read db-{N}.md for description
    md_file = deliverable_dir / f"db-{db_num}.md"
    description = f"This database implements a comprehensive system for {DB_NAMES.get(db_num, 'database operations')}. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**."

    if md_file.exists():
        try:
            md_content = md_file.read_text(encoding='utf-8')
            # Extract first paragraph after title
            lines = md_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('#') and f'db-{db_num}' in line:
                    # Look for next non-empty line
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].strip() and not lines[j].startswith('#'):
                            # Try to extract description
                            desc_match = re.search(r'This (?:database|document).*?implementations\.', md_content, re.DOTALL)
                            if desc_match:
                                description = desc_match.group(0)
                            break
                    break
        except Exception as e:
            logger.warning(f"Could not read db-{db_num}.md: {e}")

    # Generate JSON deliverable
    deliverable = {
        "database": {
            "id": f"db-{db_num}",
            "name": DB_NAMES.get(db_num, f"Database db-{db_num}"),
            "description": description,
            "created_date": datetime.now().strftime('%Y-%m-%d'),
            "version": "1.0"
        },
        "schema": {
            "total_tables": len(tables),
            "tables": tables
        },
        "queries": queries_data.get('queries', []) if queries_data else []
    }

    # Write JSON deliverable
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(deliverable, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Rebuilt: {output_file.name}")
        return True
    except Exception as e:
        logger.error(f"Error writing JSON deliverable: {e}")
        return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate JSON deliverable files for databases"
    )
    parser.add_argument(
        "db_numbers",
        nargs="*",
        type=int,
        help="Database numbers to process (e.g., 6 7 8). If not specified, processes db-6 through db-15."
    )

    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent

    # Determine which databases to process
    if args.db_numbers:
        db_numbers = args.db_numbers
    else:
        # Default: process db-6 through db-15
        db_numbers = list(range(6, 16))

    logger.info(f"Generating JSON deliverables for databases: {db_numbers}\n")

    success_count = 0
    for db_num in db_numbers:
        if generate_json_deliverable(db_num, root_dir):
            success_count += 1
        logger.info("")

    logger.info(f"Completed: {success_count}/{len(db_numbers)} databases processed")

    return 0 if success_count == len(db_numbers) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
