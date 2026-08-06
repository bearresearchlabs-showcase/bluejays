#!/usr/bin/env python3
"""
Standardize all db-*.md files to match db-6 formatting.

This script ensures all deliverable markdown files have:
1. Consistent header format: # ID: db-{N} - Name: {Database Name}
2. Business Context and Backstory section (from deliverable/db-{N}.md)
3. Consistent Table of Contents structure
4. Proper section ordering
"""

import re
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Database names mapping
DB_NAMES = {
    6: "Weather Consulting Database",
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


def extract_business_context(deliverable_md_file, web_md_file=None):
    """Extract Business Context and Backstory section from deliverable/db-{N}.md or web version."""
    # Try deliverable version first
    if deliverable_md_file.exists():
        content = deliverable_md_file.read_text(encoding='utf-8')
        pattern = r'## Business Context and Backstory\s*\n\n(.*?)(?=\n---|\n## Database Documentation|\n## Table of Contents|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

    # Fallback to web version if deliverable doesn't have it
    if web_md_file and web_md_file.exists():
        content = web_md_file.read_text(encoding='utf-8')
        pattern = r'## Business Context and Backstory\s*\n\n(.*?)(?=\n---|\n## Database Documentation|\n## Table of Contents|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

    return None


def standardize_db_md_file(db_num, root_dir=None):
    """Standardize a db-{N}.md file to match db-6 formatting."""
    if root_dir is None:
        root_dir = Path(__file__).parent.parent

    root_dir = Path(root_dir).resolve()

    # Find web-deployable folder
    web_folder_name = DB_WEB_FOLDER_NAMES.get(db_num)
    if not web_folder_name:
        logger.warning(f"No web folder name for db-{db_num}")
        return False

    web_md_file = root_dir / f"db-{db_num}" / "deliverable" / web_folder_name / f"db-{db_num}.md"
    deliverable_md_file = root_dir / f"db-{db_num}" / "deliverable" / f"db-{db_num}.md"

    if not web_md_file.exists():
        logger.warning(f"Web MD file not found: {web_md_file}")
        return False

    logger.info(f"Standardizing db-{db_num}.md...")

    # Read current content
    content = web_md_file.read_text(encoding='utf-8')

    # Extract business context from deliverable version or web version
    business_context = extract_business_context(deliverable_md_file, web_md_file)

    # Standardize header
    db_name = DB_NAMES.get(db_num, f"Database db-{db_num}")
    header_pattern = r'^#.*?db-{}\s*[-:]\s*Name:.*?\n'.format(db_num)
    new_header = f"# ID: db-{db_num} - Name: {db_name}\n\n"

    # Replace header
    content = re.sub(r'^#.*?\n', new_header, content, count=1)

    # Add description paragraph
    description = "This document provides comprehensive documentation for database db-{}, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**.".format(db_num)

    # Check if description already exists
    if description not in content[:500]:
        # Insert after header
        content = re.sub(r'^(# ID: db-{}\s*- Name:.*?\n)\n'.format(db_num), r'\1\n{}\n\n'.format(description), content, count=1)

    # Add Business Context and Backstory section if it exists and is missing
    if business_context:
        # Check if section already exists
        if "## Business Context and Backstory" not in content:
            # Insert after description, before Table of Contents
            toc_pattern = r'(\n---\n\n## Table of Contents)'
            business_section = f"\n## Business Context and Backstory\n\n{business_context}\n\n---\n"
            content = re.sub(toc_pattern, business_section + r'\1', content, count=1)
            logger.info(f"  Added Business Context and Backstory section")
        else:
            logger.info(f"  Business Context section already exists")
    else:
        logger.warning(f"  No Business Context found in deliverable version")

    # Ensure Table of Contents structure matches db-6
    toc_pattern = r'(## Table of Contents\n\n### Database Documentation\n\n1\. \[Database Overview\].*?3\. \[Data Dictionary\].*?\n)'
    standard_toc = """## Table of Contents

### Database Documentation

1. [Database Overview](#database-overview)
   - Description and key features
   - Business context and use cases
   - Platform compatibility
   - Data sources

2. [Database Schema Documentation](#database-schema-documentation)
   - Complete schema overview
   - All tables with detailed column definitions
   - Indexes and constraints
   - Entity-Relationship diagrams
   - Table relationships

3. [Data Dictionary](#data-dictionary)
   - Comprehensive column-level documentation
   - Data types and constraints
   - Column descriptions and business context

"""

    # Check if TOC needs updating
    if "### Database Documentation" in content and "1. [Database Overview]" in content:
        # TOC exists, check if it matches standard format
        if "### Data Dictionary" not in content.split("## Table of Contents")[1].split("## Database")[0]:
            # Replace TOC
            content = re.sub(r'## Table of Contents.*?(?=\n## |\n### Data Dictionary|\Z)', standard_toc, content, flags=re.DOTALL)
            logger.info(f"  Updated Table of Contents")
    else:
        # Insert standard TOC
        # Find insertion point (after Business Context or after description)
        if "## Business Context and Backstory" in content:
            insert_point = content.find("---", content.find("## Business Context and Backstory")) + 3
        else:
            insert_point = content.find("\n---\n") + 5

        if insert_point > 0:
            content = content[:insert_point] + "\n\n" + standard_toc + content[insert_point:]
            logger.info(f"  Inserted standard Table of Contents")

    # Write updated content
    web_md_file.write_text(content, encoding='utf-8')
    logger.info(f"  ✓ Updated: {web_md_file.name}")

    return True


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Standardize db-*.md files to match db-6 formatting"
    )
    parser.add_argument(
        "db_numbers",
        nargs="*",
        type=int,
        help="Database numbers to standardize (e.g., 6 7 8). If not specified, standardizes db-6 through db-15."
    )

    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent

    # Determine which databases to standardize
    if args.db_numbers:
        db_numbers = args.db_numbers
    else:
        # Default: standardize db-6 through db-15
        db_numbers = list(range(6, 16))

    logger.info(f"Standardizing db-*.md files for databases: {db_numbers}\n")

    success_count = 0
    for db_num in db_numbers:
        if standardize_db_md_file(db_num, root_dir):
            success_count += 1
        logger.info("")

    logger.info(f"Completed: {success_count}/{len(db_numbers)} databases standardized")

    return 0 if success_count == len(db_numbers) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
