#!/usr/bin/env python3
"""
Update db-6_documentation.html with db-7's content (overview, schema, queries)
"""

import re
from pathlib import Path

def markdown_to_html(markdown_content):
    """Convert markdown to HTML with basic formatting"""
    html = markdown_content

    # Headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2 id="\1">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3 id="\1">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4 id="\1">\1</h4>', html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Code blocks
    html = re.sub(r'```sql\n(.*?)```', r'<pre><code class="language-sql">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```json\n(.*?)```', r'<pre><code class="language-json">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```mermaid\n(.*?)```', r'<pre><code class="language-mermaid">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # Lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Wrap consecutive list items in ul/ol
    html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

    # Paragraphs (lines that don't start with HTML tags)
    lines = html.split('\n')
    html_parts = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('<'):
            html_parts.append(f'<p>{line}</p>')
        elif line:
            html_parts.append(line)
    html = '\n'.join(html_parts)

    # Clean up empty paragraphs
    html = re.sub(r'<p></p>', '', html)

    return html

def update_db6_html_with_db7():
    """Update db-6_documentation.html with db-7's content"""
    root_dir = Path(__file__).parent.parent

    # Read db-7 markdown
    db7_md_file = root_dir / 'db-7' / 'deliverable' / 'db-7.md'
    if not db7_md_file.exists():
        print(f"❌ Error: {db7_md_file} not found")
        return False

    db7_content = db7_md_file.read_text(encoding='utf-8')

    # Convert markdown to HTML
    db7_html_content = markdown_to_html(db7_content)

    # Read db-6 HTML
    db6_html_file = root_dir / 'db-6_documentation.html'
    if not db6_html_file.exists():
        print(f"❌ Error: {db6_html_file} not found")
        return False

    db6_html = db6_html_file.read_text(encoding='utf-8')

    # Update title
    db6_html = re.sub(
        r'<title>Weather Consulting Database - Documentation</title>',
        r'<title>Maritime Shipping Intelligence Database - Documentation</title>',
        db6_html
    )

    # Update sidebar header
    db6_html = re.sub(
        r'<h1>Weather Consulting Database</h1>\s*<p>db-6 Documentation</p>',
        r'<h1>Maritime Shipping Intelligence Database</h1>\n            <p>db-7 Documentation</p>',
        db6_html
    )

    # Find main content section (between <main class="main-content"> and </main>)
    main_content_pattern = r'(<main class="main-content">)(.*?)(</main>)'
    match = re.search(main_content_pattern, db6_html, re.DOTALL)

    if not match:
        print("❌ Error: Could not find main content section")
        return False

    # Extract header and intro box structure from original
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

    # Write updated HTML
    db6_html_file.write_text(db6_html, encoding='utf-8')
    print(f"✅ Updated: {db6_html_file}")
    return True

if __name__ == '__main__':
    update_db6_html_with_db7()
