#!/usr/bin/env python3
"""
Fix grammatical issues in sourced language updates.

This script fixes issues like "sourced from as" and ensures consistent language.
"""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fix_sourced_grammar(content):
    """Fix grammatical issues in sourced language."""
    changes_made = []
    
    # Fix "was sourced from as" -> "was sourced from a production system that serves as"
    if re.search(r'was sourced from\s+as\s+', content, re.IGNORECASE):
        content = re.sub(
            r'was sourced from\s+as\s+the\s+',
            'was sourced from a production system that serves as the ',
            content,
            flags=re.IGNORECASE
        )
        content = re.sub(
            r'was sourced from\s+as\s+',
            'was sourced from a production system that serves as ',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Fixed 'sourced from as' grammar")
    
    # Fix "Every query in this database was created" -> "Every query in this database was sourced from"
    if re.search(r'Every query in this database was created', content, re.IGNORECASE):
        content = re.sub(
            r'Every query in this database was created\s+to\s+solve',
            'Every query in this database was sourced from production systems used by companies',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Fixed query creation language")
    
    # Fix "This database implements" -> "This database was sourced from a production system implementing"
    if re.search(r'This database implements\s+', content, re.IGNORECASE) and 'was sourced from' not in content[:500]:
        # Only if it's in the Database Overview section and not already fixed
        content = re.sub(
            r'This database implements\s+',
            'This database was sourced from a production system implementing ',
            content,
            flags=re.IGNORECASE
        )
        changes_made.append("Fixed 'implements' language")
    
    return content, changes_made


def update_file(file_path, root_dir):
    """Update a single db-*.md file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return False
    
    updated_content, changes = fix_sourced_grammar(content)
    
    if changes:
        file_path.write_text(updated_content, encoding='utf-8')
        logger.info(f"  Fixed: {', '.join(changes)}")
        return True
    else:
        return False


def main():
    """Main function."""
    root_dir = Path(__file__).parent.parent.resolve()
    
    logger.info(f"Fixing sourced language grammar: {root_dir}\n")
    
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
    
    logger.info(f"Completed: {updated_count}/{len(db_md_files)} files fixed")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
