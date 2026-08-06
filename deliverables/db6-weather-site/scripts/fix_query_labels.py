#!/usr/bin/env python3
"""
Fix query labels in queries.md files:
- **Business Use Case:** → **Use Case:**
- **Client Deliverable:** → **Business Value:**
- **Business Value:** → **Purpose:**
- **Description:** stays as is (describes what SQL does)
"""

import re
from pathlib import Path
import sys

def fix_query_labels(file_path: Path) -> bool:
    """Fix labels in a queries.md file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Process each query separately to handle the label swapping correctly
        def fix_single_query(match):
            query_text = match.group(1)
            original_query = query_text

            # Check what labels exist in original
            has_client_deliverable = '**Client Deliverable:**' in original_query
            has_business_value = '**Business Value:**' in original_query
            has_business_use_case = '**Business Use Case:**' in original_query

            # Step 1: Replace **Business Use Case:** → **Use Case:**
            if has_business_use_case:
                query_text = re.sub(r'\*\*Business Use Case:\*\*', '**Use Case:**', query_text, flags=re.IGNORECASE)

            # Step 2: Replace **Client Deliverable:** → **Business Value:**
            if has_client_deliverable:
                query_text = re.sub(r'\*\*Client Deliverable:\*\*', '**Business Value:**', query_text, flags=re.IGNORECASE)

            # Step 3: Replace the OLD **Business Value:** → **Purpose:**
            # Only if original had Business Value (the old one that should become Purpose)
            if has_business_value:
                # Find the Business Value that was originally Business Value (not the one renamed from Client Deliverable)
                # After step 2, if both existed, we now have two Business Value labels
                # We need to replace the one that was originally Business Value

                if has_client_deliverable:
                    # Both existed - replace the second Business Value (the original one) with Purpose
                    business_value_matches = list(re.finditer(r'\*\*Business Value:\*\*', query_text, re.IGNORECASE))
                    if len(business_value_matches) >= 2:
                        # Replace the second occurrence (the original Business Value) with Purpose
                        second_match = business_value_matches[1]
                        query_text = (
                            query_text[:second_match.start()] +
                            '**Purpose:**' +
                            query_text[second_match.end():]
                        )
                else:
                    # Only Business Value existed (no Client Deliverable) - replace it with Purpose
                    query_text = re.sub(r'\*\*Business Value:\*\*', '**Purpose:**', query_text, flags=re.IGNORECASE, count=1)

            return query_text

        # Process all queries
        content = re.sub(
            r'(## Query \d+:.*?)(?=## Query \d+:|$)',
            fix_single_query,
            content,
            flags=re.DOTALL | re.MULTILINE
        )

        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False

    except Exception as e:
        import traceback
        print(f"Error processing {file_path}: {e}")
        print(traceback.format_exc())
        return False

def main():
    """Fix labels in all queries.md files"""
    root_dir = Path(__file__).parent.parent

    if len(sys.argv) > 1:
        # Fix specific database
        db_num = int(sys.argv[1].replace('db-', ''))
        queries_file = root_dir / f'db-{db_num}' / 'queries' / 'queries.md'
        if queries_file.exists():
            if fix_query_labels(queries_file):
                print(f"✅ Fixed labels in db-{db_num}/queries/queries.md")
            else:
                print(f"ℹ️  No changes needed in db-{db_num}/queries/queries.md")
        else:
            print(f"❌ File not found: {queries_file}")
    else:
        # Fix all databases
        fixed_count = 0
        for db_num in range(1, 16):
            queries_file = root_dir / f'db-{db_num}' / 'queries' / 'queries.md'
            if queries_file.exists():
                if fix_query_labels(queries_file):
                    print(f"✅ Fixed db-{db_num}/queries/queries.md")
                    fixed_count += 1
                else:
                    print(f"ℹ️  No changes needed in db-{db_num}/queries/queries.md")

        print(f"\n📊 Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
