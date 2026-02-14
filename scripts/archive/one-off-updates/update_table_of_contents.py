#!/usr/bin/env python3
"""
Update table of contents in all db-*.md files to match the reference format.

The reference format only includes:
- Database Documentation section (3 items)
- No SQL Queries section in TOC
"""

import re
from pathlib import Path
from datetime import datetime


# Reference TOC format (from db-6 reference)
REFERENCE_TOC = """## Table of Contents

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


def extract_queries_section(content):
    """Extract the SQL Queries section from content if it exists."""
    # Look for the SQL Queries section in TOC
    pattern = r'(### SQL Queries.*?)(?=\n\n### |\n## |$)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return None


def update_table_of_contents(db_num, root_dir=None):
    """Update table of contents in deliverable markdown file."""
    if root_dir is None:
        root_dir = Path(__file__).parent.parent
    
    db_dir = root_dir / f"db-{db_num}"
    deliverable_file = db_dir / "deliverable" / f"db-{db_num}.md"
    
    if not deliverable_file.exists():
        print(f"⚠ Deliverable file not found: {deliverable_file}")
        return False
    
    # Read the current file
    with open(deliverable_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicate "## Table of Contents" headers first
    content = re.sub(r'## Table of Contents\n\n## Table of Contents\n\n', '## Table of Contents\n\n', content)
    
    # Find the Table of Contents section
    # Pattern: Look for "## Table of Contents" followed by content until next "##" section (but not "###")
    # We want to match until we hit a "## " (level 2 header) that's not part of the TOC
    toc_pattern = r'(## Table of Contents\n\n)(.*?)(\n\n## [^#]|\n\n### Data Dictionary\n|\n## Business Context\n)'
    
    def replace_toc(match):
        toc_header = match.group(1)
        old_toc_content = match.group(2)
        next_section = match.group(3)
        
        # Remove any SQL Queries section from TOC
        lines = old_toc_content.split('\n')
        new_lines = []
        skip_until_next_section = False
        
        for i, line in enumerate(lines):
            # If we hit SQL Queries section, skip it
            if '### SQL Queries' in line:
                skip_until_next_section = True
                continue
            
            # Stop skipping when we hit next section (### or end)
            if skip_until_next_section:
                if line.startswith('### ') and 'SQL Queries' not in line:
                    skip_until_next_section = False
                elif line.strip() == '' and i < len(lines) - 1:
                    # Check if next non-empty line starts a new section
                    next_non_empty = None
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip():
                            next_non_empty = lines[j]
                            break
                    if next_non_empty and (next_non_empty.startswith('### ') or next_non_empty.startswith('## ')):
                        skip_until_next_section = False
            
            if not skip_until_next_section:
                new_lines.append(line)
        
        cleaned_toc = '\n'.join(new_lines).strip()
        
        # Check if cleaned TOC matches reference format
        if '### Database Documentation' in cleaned_toc and '1. [Database Overview]' in cleaned_toc:
            # Format is correct, use cleaned version
            return toc_header + cleaned_toc + '\n' + next_section
        else:
            # Replace with reference format
            return toc_header + REFERENCE_TOC + next_section
    
    new_content = re.sub(toc_pattern, replace_toc, content, flags=re.DOTALL)
    
    # If pattern didn't match, try a more aggressive approach
    if new_content == content:
        # Find all occurrences of "## Table of Contents"
        toc_matches = list(re.finditer(r'## Table of Contents\n\n', content))
        if toc_matches:
            # Use the first occurrence
            start_pos = toc_matches[0].end()
            # Find where TOC ends - look for next ## section
            end_match = re.search(r'\n\n## [^#]', content[start_pos:])
            if end_match:
                end_pos = start_pos + end_match.start()
                old_toc = content[start_pos:end_pos]
                
                # Remove SQL Queries section if present
                if '### SQL Queries' in old_toc:
                    lines = old_toc.split('\n')
                    new_lines = []
                    skip = False
                    for line in lines:
                        if '### SQL Queries' in line:
                            skip = True
                            continue
                        if skip and (line.startswith('### ') or line.startswith('## ')):
                            skip = False
                        if not skip:
                            new_lines.append(line)
                    cleaned_toc = '\n'.join(new_lines).strip()
                    
                    # Check if it matches reference format
                    if '### Database Documentation' in cleaned_toc and '1. [Database Overview]' in cleaned_toc:
                        new_content = content[:start_pos] + cleaned_toc + '\n' + content[end_pos:]
                    else:
                        new_content = content[:start_pos] + REFERENCE_TOC + content[end_pos:]
    
    # Write the updated content
    if new_content != content:
        with open(deliverable_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Updated {deliverable_file.name}")
        return True
    else:
        print(f"  {deliverable_file.name} - No changes needed")
        return True


def main():
    """Main function to update all deliverable files."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update table of contents in database deliverable files"
    )
    parser.add_argument(
        "db_numbers",
        nargs="*",
        type=int,
        help="Database numbers to update (e.g., 6 7 8). If not specified, updates db-6 through db-15."
    )
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    
    # Determine which databases to update
    if args.db_numbers:
        db_numbers = args.db_numbers
    else:
        # Default: update db-6 through db-15
        db_numbers = list(range(6, 16))
    
    print(f"Updating table of contents for databases: {db_numbers}\n")
    
    success_count = 0
    for db_num in db_numbers:
        if update_table_of_contents(db_num, root_dir):
            success_count += 1
    
    print(f"\n✓ Completed: {success_count}/{len(db_numbers)} databases updated")
    
    return 0 if success_count == len(db_numbers) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
