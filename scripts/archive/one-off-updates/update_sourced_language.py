#!/usr/bin/env python3
"""
Update all db-*.md files to clarify that databases were sourced from production systems.

This script updates language to make it clear these databases were sourced/acquired,
not created or built by us.
"""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def update_sourced_language(content):
    """Update language to clarify databases were sourced."""
    changes_made = []

    # Update "This database was built" -> "This database was sourced from"
    if re.search(r'This database was built', content, re.IGNORECASE):
        content = re.sub(
            r'This database was built',
            'This database was sourced from',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Updated 'was built' to 'was sourced from'")

    # Update "This database is the " -> "This database was sourced from"
    if re.search(r'This database is the ', content, re.IGNORECASE):
        content = re.sub(
            r'This database is the ',
            'This database was sourced from',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Updated 'is' to 'was sourced from'")

    # Update "This database was created" -> "This database was sourced from"
    if re.search(r'This database was created', content, re.IGNORECASE):
        content = re.sub(
            r'This database was created',
            'This database was sourced from',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Updated 'was created' to 'was sourced from'")

    # Update "This database implements" -> "This database was sourced from a system that implements"
    if re.search(r'This database implements', content, re.IGNORECASE):
        content = re.sub(
            r'This database implements',
            'This database was sourced from a production system that implements',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Updated 'implements' to clarify sourcing")

    # Update "Every query in this database was created" -> "Every query in this database was sourced from"
    if re.search(r'Every query in this database was created', content, re.IGNORECASE):
        content = re.sub(
            r'Every query in this database was created',
            'Every query in this database was sourced from',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Updated query creation language")

    # Update "This database powers" -> "This database was sourced from a system that powers"
    if re.search(r'This database powers', content, re.IGNORECASE):
        content = re.sub(
            r'This database powers',
            'This database was sourced from a production system that powers',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Updated 'powers' to clarify sourcing")

    # Update Business Value section
    business_value_pattern = r'\*\*Business Value:\*\*\s*\n\nEvery query in this database was (created|built)'
    if re.search(business_value_pattern, content, re.IGNORECASE | re.MULTILINE):
        content = re.sub(
            r'Every query in this database was (created|built)',
            'Every query in this database was sourced from',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Updated Business Value section")

    # Update description to emphasize sourcing
    desc_pattern = r'This document provides comprehensive documentation for database db-(\d+), including complete schema documentation, all SQL queries with business context, and usage instructions\. This database and its queries are sourced from production systems'
    if not re.search(desc_pattern, content):
        # Check if we need to update the description
        old_desc = r'This document provides comprehensive documentation for database db-(\d+), including complete schema documentation, all SQL queries with business context, and usage instructions\.'
        if re.search(old_desc, content):
            # Ensure it mentions sourcing
            content = re.sub(
                old_desc,
                r'This document provides comprehensive documentation for database db-\1, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries were sourced from production systems',
                content
            )
            changes_made.append("Updated description to emphasize sourcing")

    return content, changes_made


def update_file(file_path, root_dir):
    """Update a single db-*.md file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return False

    updated_content, changes = update_sourced_language(content)

    if changes:
        file_path.write_text(updated_content, encoding='utf-8')
        logger.info(f"  Updated: {', '.join(changes)}")
        return True
    else:
        logger.info(f"  ✓ Already uses sourced language")
        return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update language to clarify databases were sourced"
    )
    parser.add_argument(
        "--root",
        type=str,
        help="Root directory (default: parent of scripts directory)"
    )

    args = parser.parse_args()

    if args.root:
        root_dir = Path(args.root).resolve()
    else:
        root_dir = Path(__file__).parent.parent.resolve()

    logger.info(f"Updating sourced language: {root_dir}\n")

    # Find all db-*.md files
    db_md_files = []
    for md_file in root_dir.rglob("db-*.md"):
        if "archive" in md_file.parts:
            continue
        if "__pycache__" in md_file.parts or ".git" in md_file.parts:
            continue
        db_md_files.append(md_file)

    logger.info(f"Found {len(db_md_files)} db-*.md files\n")

    updated_count = 0
    for md_file in sorted(db_md_files):
        logger.info(f"Checking: {md_file.relative_to(root_dir)}")
        if update_file(md_file, root_dir):
            updated_count += 1
        logger.info("")

    logger.info(f"Completed: {updated_count}/{len(db_md_files)} files updated")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
