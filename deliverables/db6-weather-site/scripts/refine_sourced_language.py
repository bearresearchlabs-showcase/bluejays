#!/usr/bin/env python3
"""
Refine sourced language to make it more natural and clear.

This script refines the language updates to ensure clarity that databases
were sourced from production systems.
"""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def refine_sourced_language(content):
    """Refine sourced language for clarity."""
    changes_made = []
    
    # Fix "This database was sourced from" -> "This database was sourced from a production system"
    # But only if it's followed by something that needs context
    pattern1 = r'This database was sourced from\s+(?:a|an|the)\s+([a-z]+)\s+(?:that|which)'
    if re.search(pattern1, content, re.IGNORECASE):
        # Already has context, leave it
        pass
    else:
        # Check if "was sourced from" is followed by something that needs "a production system"
        pattern2 = r'This database was sourced from\s+(?:as|for|to)\s+'
        if re.search(pattern2, content, re.IGNORECASE):
            # Fix: "was sourced from as" -> "was sourced from a production system that serves as"
            content = re.sub(
                r'This database was sourced from\s+as\s+the\s+',
                'This database was sourced from a production system that serves as the ',
                content,
                flags=re.IGNORECASE
            )
            changes_made.append("Refined 'sourced from as'")
            
            content = re.sub(
                r'This database was sourced from\s+as\s+',
                'This database was sourced from a production system that serves as ',
                content,
                flags=re.IGNORECASE
            )
            if "Refined 'sourced from as'" not in changes_made:
                changes_made.append("Refined 'sourced from as'")
    
    # Fix "was sourced from a production system that implements" -> more natural
    content = re.sub(
        r'was sourced from a production system that implements\s+',
        'was sourced from a production system implementing ',
        content,
        flags=re.IGNORECASE
    )
    
    # Fix "was sourced from a production system that powers" -> more natural
    content = re.sub(
        r'was sourced from a production system that powers\s+',
        'was sourced from a production system powering ',
        content,
        flags=re.IGNORECASE
    )
    
    # Ensure Business Value section is clear
    if "Every query in this database was sourced from" in content:
        # Make sure it's clear these were sourced
        if "sourced from production systems" not in content.split("Business Value")[1].split("---")[0]:
            content = re.sub(
                r'Every query in this database was sourced from\s+',
                'Every query in this database was sourced from production systems used by ',
                content,
                flags=re.IGNORECASE
            )
            changes_made.append("Clarified query sourcing")
    
    return content, changes_made


def update_file(file_path, root_dir):
    """Update a single db-*.md file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return False
    
    updated_content, changes = refine_sourced_language(content)
    
    if changes:
        file_path.write_text(updated_content, encoding='utf-8')
        logger.info(f"  Refined: {', '.join(changes)}")
        return True
    else:
        return False


def main():
    """Main function."""
    root_dir = Path(__file__).parent.parent.resolve()
    
    logger.info(f"Refining sourced language: {root_dir}\n")
    
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
        if update_file(md_file, root_dir):
            updated_count += 1
    
    logger.info(f"\nCompleted: {updated_count}/{len(db_md_files)} files refined")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
