#!/usr/bin/env python3
"""
Post-process generated markdown files to ensure they're lint-free:
- Remove trailing whitespace
- Ensure proper blank lines around headers
- Fix any formatting issues
"""

import re
from pathlib import Path
import sys

def clean_markdown(content: str) -> str:
    """Clean markdown content to be lint-free"""
    lines = content.split('\n')
    cleaned_lines = []

    for i, line in enumerate(lines):
        # Remove trailing whitespace
        cleaned_line = line.rstrip()

        # Check if this is a header
        is_header = bool(re.match(r'^#+\s+', cleaned_line))

        if is_header:
            # Ensure blank line before header (unless first line or after frontmatter/another header)
            if i > 0 and cleaned_lines and cleaned_lines[-1].strip() != '':
                if not re.match(r'^---', cleaned_lines[-1]) and not re.match(r'^#+\s+', cleaned_lines[-1]):
                    cleaned_lines.append('')
            cleaned_lines.append(cleaned_line)
            # Ensure blank line after header (unless last line or next line is blank/header)
            if i < len(lines) - 1:
                next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
                if next_line != '' and not re.match(r'^#+\s+', next_line):
                    cleaned_lines.append('')
        else:
            cleaned_lines.append(cleaned_line)

    # Remove duplicate blank lines (more than 2 consecutive)
    final_lines = []
    blank_count = 0
    for line in cleaned_lines:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= 2:  # Allow up to 2 blank lines
                final_lines.append(line)
        else:
            blank_count = 0
            final_lines.append(line)

    # Ensure file ends with newline
    result = '\n'.join(final_lines)
    if result and not result.endswith('\n'):
        result += '\n'

    return result

def main():
    """Clean generated markdown files"""
    if len(sys.argv) < 2:
        print("Usage: clean_generated_markdown.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    content = file_path.read_text(encoding='utf-8')
    cleaned_content = clean_markdown(content)

    if cleaned_content != content:
        file_path.write_text(cleaned_content, encoding='utf-8')
        print(f"✅ Cleaned {file_path}")
    else:
        print(f"ℹ️  No changes needed in {file_path}")

if __name__ == '__main__':
    main()
