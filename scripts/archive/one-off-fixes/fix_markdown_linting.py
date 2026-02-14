#!/usr/bin/env python3
"""
Fix markdown linting issues in cursor rules files:
- Remove trailing whitespace
- Add blank lines around headers
- Fix inconsistent list markers
- Note: Long lines (>100 chars) are kept for readability in documentation
"""

import re
from pathlib import Path
import sys

def fix_markdown_file(file_path: Path) -> bool:
    """Fix markdown linting issues in a file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # Remove trailing whitespace
            fixed_line = line.rstrip()

            # Fix inconsistent list markers (use '-' instead of '*' or '+')
            if re.match(r'^\s*[+*]\s+', fixed_line):
                fixed_line = re.sub(r'^(\s*)[+*](\s+)', r'\1-\2', fixed_line)

            fixed_lines.append(fixed_line)

        # Fix blank lines around headers
        final_lines = []
        for i, line in enumerate(fixed_lines):
            # Check if this is a header
            is_header = bool(re.match(r'^#+\s+', line))

            if is_header:
                # Add blank line before header (unless it's the first line or already has blank line)
                if i > 0 and final_lines and final_lines[-1].strip() != '':
                    # Check if previous line is a frontmatter separator
                    if not re.match(r'^---', final_lines[-1]):
                        final_lines.append('')
                final_lines.append(line)
                # Add blank line after header (unless it's the last line or next line is blank/header)
                if i < len(fixed_lines) - 1:
                    next_line = fixed_lines[i + 1]
                    if next_line.strip() != '' and not re.match(r'^#+\s+', next_line):
                        final_lines.append('')
            else:
                final_lines.append(line)

        # Remove duplicate blank lines (more than 2 consecutive)
        cleaned_lines = []
        blank_count = 0
        for line in final_lines:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= 2:  # Allow up to 2 blank lines
                    cleaned_lines.append(line)
            else:
                blank_count = 0
                cleaned_lines.append(line)

        fixed_content = '\n'.join(cleaned_lines)

        # Ensure file ends with newline
        if fixed_content and not fixed_content.endswith('\n'):
            fixed_content += '\n'

        if fixed_content != original_content:
            file_path.write_text(fixed_content, encoding='utf-8')
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fix markdown linting in all cursor rules files"""
    root_dir = Path(__file__).parent.parent
    rules_dir = root_dir / '.cursor' / 'rules'

    if len(sys.argv) > 1:
        # Fix specific file
        file_path = Path(sys.argv[1])
        if file_path.exists():
            if fix_markdown_file(file_path):
                print(f"✅ Fixed {file_path}")
            else:
                print(f"ℹ️  No changes needed in {file_path}")
        else:
            print(f"❌ File not found: {file_path}")
    else:
        # Fix all cursor rules files
        fixed_count = 0
        for rule_file in sorted(rules_dir.glob('*.mdc')):
            if fix_markdown_file(rule_file):
                print(f"✅ Fixed {rule_file.name}")
                fixed_count += 1
            else:
                print(f"ℹ️  No changes needed in {rule_file.name}")

        print(f"\n📊 Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
