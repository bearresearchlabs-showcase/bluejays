#!/usr/bin/env python3
"""
Recursively check and standardize all db-*.md files across the repository.

This script ensures consistency across:
- deliverable/db-{N}.md files
- deliverable/db{N}-{name}/db-{N}.md files
- Any other db-*.md files in the repository
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


def find_all_db_md_files(root_dir):
    """Find all db-*.md files recursively."""
    root_dir = Path(root_dir).resolve()
    db_md_files = []
    
    # Find all db-*.md files
    for md_file in root_dir.rglob("db-*.md"):
        # Skip files in archive directories
        if "archive" in md_file.parts:
            continue
        # Skip files in __pycache__ or .git
        if "__pycache__" in md_file.parts or ".git" in md_file.parts:
            continue
        db_md_files.append(md_file)
    
    return sorted(db_md_files)


def extract_db_number(file_path):
    """Extract database number from file path."""
    match = re.search(r'db-(\d+)', str(file_path))
    if match:
        return int(match.group(1))
    return None


def check_header_format(content, db_num):
    """Check if header matches standard format."""
    first_line = content.split('\n')[0] if content else ""
    expected_pattern = f"^# ID: db-{db_num} - Name:"
    return bool(re.match(expected_pattern, first_line))


def check_description(content):
    """Check if description paragraph exists."""
    desc_pattern = r'\$1M\+\s+Annual Recurring Revenue.*?ARR'
    return bool(re.search(desc_pattern, content, re.IGNORECASE | re.DOTALL))


def check_business_context(content):
    """Check if Business Context and Backstory section exists."""
    return "## Business Context and Backstory" in content


def check_table_of_contents(content):
    """Check if Table of Contents matches standard format."""
    toc_pattern = r'## Table of Contents\s*\n\n### Database Documentation\s*\n\n1\. \[Database Overview\]'
    return bool(re.search(toc_pattern, content))


def extract_business_context_from_other_file(db_num, root_dir, current_file):
    """Try to extract Business Context from other db-{N}.md files."""
    root_dir = Path(root_dir)
    
    # Try deliverable/db-{N}.md first
    deliverable_file = root_dir / f"db-{db_num}" / "deliverable" / f"db-{db_num}.md"
    if deliverable_file.exists() and deliverable_file != current_file:
        content = deliverable_file.read_text(encoding='utf-8')
        pattern = r'## Business Context and Backstory\s*\n\n(.*?)(?=\n---|\n## Database Documentation|\n## Table of Contents|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Try web-deployable version
    web_folders = list((root_dir / f"db-{db_num}" / "deliverable").glob(f"db{db_num}-*"))
    for web_folder in web_folders:
        web_file = web_folder / f"db-{db_num}.md"
        if web_file.exists() and web_file != current_file:
            content = web_file.read_text(encoding='utf-8')
            pattern = r'## Business Context and Backstory\s*\n\n(.*?)(?=\n---|\n## Database Documentation|\n## Table of Contents|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
    
    return None


def standardize_file(file_path, root_dir):
    """Standardize a single db-*.md file."""
    db_num = extract_db_number(file_path)
    if not db_num or db_num not in DB_NAMES:
        logger.warning(f"Skipping {file_path} - could not determine db number")
        return False
    
    logger.info(f"Checking: {file_path.relative_to(root_dir)}")
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"  Error reading file: {e}")
        return False
    
    changes_made = []
    
    # Check and fix header
    if not check_header_format(content, db_num):
        db_name = DB_NAMES.get(db_num, f"Database db-{db_num}")
        new_header = f"# ID: db-{db_num} - Name: {db_name}\n"
        content = re.sub(r'^#.*?\n', new_header, content, count=1)
        changes_made.append("Fixed header")
    
    # Check and add description
    if not check_description(content):
        description = "This document provides comprehensive documentation for database db-{}, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**, representing real-world enterprise implementations.".format(db_num)
        
        # Insert after header
        header_pattern = r'^(# ID: db-{}\s*- Name:.*?\n)\n'.format(db_num)
        if re.match(header_pattern, content):
            content = re.sub(header_pattern, r'\1\n{}\n\n'.format(description), content, count=1)
            changes_made.append("Added description")
    
    # Check and add Business Context
    if not check_business_context(content):
        business_context = extract_business_context_from_other_file(db_num, root_dir, file_path)
        if business_context:
            # Insert after description, before Table of Contents
            toc_pattern = r'(\n---\n\n## Table of Contents)'
            if toc_pattern in content:
                business_section = f"\n## Business Context and Backstory\n\n{business_context}\n\n---\n"
                content = re.sub(toc_pattern, business_section + r'\1', content, count=1)
                changes_made.append("Added Business Context")
            else:
                # Insert after description
                desc_pattern = r'(\$1M\+ Annual Recurring Revenue.*?\n\n)'
                if re.search(desc_pattern, content):
                    business_section = f"\n## Business Context and Backstory\n\n{business_context}\n\n---\n\n"
                    content = re.sub(desc_pattern, r'\1' + business_section, content, count=1)
                    changes_made.append("Added Business Context")
        else:
            logger.warning(f"  No Business Context found for db-{db_num}")
    
    # Check and fix Table of Contents
    if not check_table_of_contents(content):
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
        
        # Replace existing TOC or insert new one
        if "## Table of Contents" in content:
            # Replace existing TOC
            toc_pattern = r'## Table of Contents.*?(?=\n## |\n### Data Dictionary|\Z)'
            content = re.sub(toc_pattern, standard_toc.rstrip(), content, flags=re.DOTALL)
            changes_made.append("Updated Table of Contents")
        else:
            # Insert TOC after Business Context or description
            if "## Business Context and Backstory" in content:
                insert_point = content.find("---", content.find("## Business Context and Backstory")) + 3
            else:
                insert_point = content.find("\n---\n") + 5
            
            if insert_point > 0:
                content = content[:insert_point] + "\n\n" + standard_toc + content[insert_point:]
                changes_made.append("Inserted Table of Contents")
    
    # Fix duplicate separators
    content = re.sub(r'\n---\n\n---\n', '\n---\n', content)
    if changes_made:
        content = re.sub(r'\n\n\n+', '\n\n', content)  # Fix multiple blank lines
    
    # Write changes if any
    if changes_made:
        file_path.write_text(content, encoding='utf-8')
        logger.info(f"  ✓ Updated: {', '.join(changes_made)}")
        return True
    else:
        logger.info(f"  ✓ Already standardized")
        return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Recursively check and standardize all db-*.md files"
    )
    parser.add_argument(
        "--root",
        type=str,
        help="Root directory (default: parent of scripts directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )
    
    args = parser.parse_args()
    
    if args.root:
        root_dir = Path(args.root).resolve()
    else:
        root_dir = Path(__file__).parent.parent.resolve()
    
    logger.info(f"Scanning repository: {root_dir}\n")
    
    # Find all db-*.md files
    db_md_files = find_all_db_md_files(root_dir)
    
    logger.info(f"Found {len(db_md_files)} db-*.md files\n")
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be modified\n")
        for md_file in db_md_files:
            db_num = extract_db_number(md_file)
            logger.info(f"Would check: {md_file.relative_to(root_dir)}")
        return 0
    
    # Process each file
    updated_count = 0
    for md_file in db_md_files:
        if standardize_file(md_file, root_dir):
            updated_count += 1
        logger.info("")
    
    logger.info(f"Completed: {updated_count}/{len(db_md_files)} files updated")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
