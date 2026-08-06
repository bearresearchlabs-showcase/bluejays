#!/usr/bin/env python3
"""
Update db-6 deliverable HTML file with db-7's content (overview, schema, queries)
"""

import re
from pathlib import Path

def markdown_to_html(markdown_content):
    """Convert markdown to HTML with proper formatting for Prism.js"""
    html = markdown_content

    # Headers - preserve IDs for navigation
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Extract ID from header text for h2, h3, h4
    def header_id(match):
        header_text = match.group(1)
        # Create ID from header text (lowercase, replace spaces with hyphens)
        header_id = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
        return f'<h2 id="{header_id}">{header_text}</h2>'

    html = re.sub(r'^## (.+)$', header_id, html, flags=re.MULTILINE)

    def h3_id(match):
        header_text = match.group(1)
        header_id = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
        return f'<h3 id="{header_id}">{header_text}</h3>'

    html = re.sub(r'^### (.+)$', h3_id, html, flags=re.MULTILINE)

    def h4_id(match):
        header_text = match.group(1)
        header_id = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
        return f'<h4 id="{header_id}">{header_text}</h4>'

    html = re.sub(r'^#### (.+)$', h4_id, html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Code blocks - preserve language classes for Prism.js
    html = re.sub(r'```sql\n(.*?)```', r'<pre><code class="language-sql">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```json\n(.*?)```', r'<pre><code class="language-json">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```mermaid\n(.*?)```', r'<pre><code class="language-mermaid">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Links - preserve anchor links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # Lists - handle both unordered and ordered
    # First handle unordered lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # Then handle ordered lists
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Wrap consecutive list items
    lines = html.split('\n')
    result_lines = []
    in_list = False
    list_items = []

    for line in lines:
        if line.strip().startswith('<li>'):
            if not in_list:
                in_list = True
                list_items = []
            list_items.append(line)
        else:
            if in_list:
                # Close the list
                result_lines.append('<ul>')
                result_lines.extend(list_items)
                result_lines.append('</ul>')
                in_list = False
                list_items = []
            result_lines.append(line)

    if in_list:
        result_lines.append('<ul>')
        result_lines.extend(list_items)
        result_lines.append('</ul>')

    html = '\n'.join(result_lines)

    # Paragraphs - wrap non-HTML lines
    lines = html.split('\n')
    html_parts = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<') and not stripped.startswith('```'):
            # Don't wrap if it's already in a tag
            if not any(stripped.startswith(f'<{tag}') for tag in ['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'pre', 'code', 'a', 'strong', 'em']):
                html_parts.append(f'<p>{stripped}</p>')
            else:
                html_parts.append(line)
        else:
            html_parts.append(line)

    html = '\n'.join(html_parts)

    # Clean up empty paragraphs and fix double wrapping
    html = re.sub(r'<p></p>', '', html)
    html = re.sub(r'<p><p>', '<p>', html)
    html = re.sub(r'</p></p>', '</p>', html)

    return html

def update_deliverable_db6_html_with_db7():
    """Update db-6 deliverable HTML file with db-7's content"""
    root_dir = Path(__file__).parent.parent

    # Read db-7 markdown
    db7_md_file = root_dir / 'db-7' / 'deliverable' / 'db-7.md'
    if not db7_md_file.exists():
        print(f"❌ Error: {db7_md_file} not found")
        return False

    print(f"📖 Reading db-7 markdown...")
    db7_content = db7_md_file.read_text(encoding='utf-8')

    # Convert markdown to HTML
    print(f"🔄 Converting markdown to HTML...")
    db7_html_content = markdown_to_html(db7_content)

    # Read db-6 deliverable HTML
    db6_html_file = root_dir / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    if not db6_html_file.exists():
        print(f"❌ Error: {db6_html_file} not found")
        return False

    print(f"📖 Reading db-6 deliverable HTML...")
    db6_html = db6_html_file.read_text(encoding='utf-8')

    # Update title
    db6_html = re.sub(
        r'<title>Weather Consulting Database - Documentation</title>',
        r'<title>Maritime Shipping Intelligence Database - Documentation</title>',
        db6_html
    )

    # Update sidebar header
    db6_html = re.sub(
        r'<h1>Weather Consulting Database</h1>',
        r'<h1>Maritime Shipping Intelligence Database</h1>\n            <p>db-7 Documentation</p>',
        db6_html
    )

    # Find main content section
    main_content_pattern = r'(<main class="main-content">)(.*?)(</main>)'
    match = re.search(main_content_pattern, db6_html, re.DOTALL)

    if not match:
        print("❌ Error: Could not find main content section")
        return False

    # Extract header and intro box structure
    header_match = re.search(
        r'(<header id="overview">.*?</header>)\s*(<div class="intro-box">.*?</div>)',
        match.group(2),
        re.DOTALL
    )

    if header_match:
        # Update header with db-7 info
        new_header = f'''<header id="overview">
            <h1>Maritime Shipping Intelligence Database</h1>
            <p>Comprehensive documentation for database db-7, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with <strong>$1M+ Annual Recurring Revenue (ARR)</strong>.</p>
        </header>

        <div class="intro-box">
            <p><strong>Database ID:</strong> db-7</p>
            <p><strong>Version:</strong> 1.0</p>
            <p><strong>Total Tables:</strong> 14</p>
            <p><strong>Total Queries:</strong> 30</p>
        </div>

        {db7_html_content}'''

        # Replace main content
        new_main_content = f'{match.group(1)}{new_header}{match.group(3)}'
        db6_html = db6_html.replace(match.group(0), new_main_content)
    else:
        # Fallback: just replace content
        new_main_content = f'{match.group(1)}{db7_html_content}{match.group(3)}'
        db6_html = db6_html.replace(match.group(0), new_main_content)

    # Update JSON deliverable preview if it exists
    json_pattern = r'"name":\s*"Weather Consulting Database"'
    db6_html = re.sub(json_pattern, '"name": "Maritime Shipping Intelligence Database"', db6_html)

    json_pattern2 = r'"id":\s*"db-6"'
    db6_html = re.sub(json_pattern2, '"id": "db-7"', db6_html)

    json_pattern3 = r'"total_tables":\s*\d+'
    db6_html = re.sub(json_pattern3, '"total_tables": 14', db6_html)

    # Write updated HTML
    print(f"💾 Writing updated HTML...")
    db6_html_file.write_text(db6_html, encoding='utf-8')
    print(f"✅ Updated: {db6_html_file}")
    print(f"✅ File is ready to render locally")
    return True

if __name__ == '__main__':
    update_deliverable_db6_html_with_db7()
