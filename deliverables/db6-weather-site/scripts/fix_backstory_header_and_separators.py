#!/usr/bin/env python3
"""
Fix backstory header and duplicate separators across all db-*.md files.

1. Change "## Business Context and Backstory" to "## Backstory"
2. Remove duplicate "---" separators (should only have one)
"""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fix_backstory_header(content):
    """Fix backstory header."""
    changes = []
    
    # Fix "## Business Context and Backstory" -> "## Backstory"
    if re.search(r'^## Business Context and Backstory', content, re.MULTILINE):
        content = re.sub(
            r'^## Business Context and Backstory',
            '## Backstory',
            content,
            flags=re.MULTILINE
        )
        changes.append("Fixed backstory header")
    
    return content, changes


def fix_duplicate_separators(content):
    """Fix duplicate separators."""
    changes = []
    
    # Find patterns like:
    # ---
    # 
    # ---
    # 
    # (two or more consecutive --- separators with blank lines)
    
    # Pattern: --- followed by blank line(s) followed by ---
    pattern = r'^---\s*\n\s*\n^---\s*\n'
    
    if re.search(pattern, content, re.MULTILINE):
        # Replace multiple consecutive --- with single ---
        content = re.sub(
            r'^---\s*\n\s*\n^---\s*\n',
            '---\n\n',
            content,
            flags=re.MULTILINE
        )
        changes.append("Fixed duplicate separators")
    
    # Also check for three or more consecutive separators
    pattern3 = r'^---\s*\n\s*\n^---\s*\n\s*\n^---\s*\n'
    if re.search(pattern3, content, re.MULTILINE):
        content = re.sub(
            r'^---\s*\n\s*\n^---\s*\n\s*\n^---\s*\n',
            '---\n\n',
            content,
            flags=re.MULTILINE
        )
        changes.append("Fixed triple separators")
    
    # Check for four or more
    pattern4 = r'^---\s*\n\s*\n^---\s*\n\s*\n^---\s*\n\s*\n^---\s*\n'
    if re.search(pattern4, content, re.MULTILINE):
        content = re.sub(
            r'^---\s*\n\s*\n^---\s*\n\s*\n^---\s*\n\s*\n^---\s*\n',
            '---\n\n',
            content,
            flags=re.MULTILINE
        )
        changes.append("Fixed quadruple separators")
    
    return content, changes


def fix_file(file_path, root_dir):
    """Fix a single db-*.md file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return False
    
    original_content = content
    content, header_changes = fix_backstory_header(content)
    content, separator_changes = fix_duplicate_separators(content)
    
    all_changes = header_changes + separator_changes
    
    if all_changes:
        file_path.write_text(content, encoding='utf-8')
        logger.info(f"  Fixed: {', '.join(all_changes)}")
        return True
    else:
        return False


def main():
    """Main function."""
    root_dir = Path(__file__).parent.parent.resolve()
    
    logger.info(f"Fixing backstory headers and separators: {root_dir}\n")
    
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
        if fix_file(md_file, root_dir):
            updated_count += 1
        logger.info("")
    
    logger.info(f"Completed: {updated_count}/{len(db_md_files)} files updated")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
