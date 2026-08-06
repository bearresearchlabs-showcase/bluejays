#!/usr/bin/env python3
"""
Update db-6 deliverable HTML to include both db-6 and db-7 content with proper sidebar navigation
"""

import re
from pathlib import Path

def markdown_to_html(markdown_content, db_prefix=""):
    """Convert markdown to HTML with proper formatting for Prism.js"""
    html = markdown_content

    # Headers - add db prefix to IDs for navigation
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    def header_id(match):
        header_text = match.group(1)
        header_id_text = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
        if db_prefix:
            header_id_text = f'{db_prefix}-{header_id_text}'
        return f'<h2 id="{header_id_text}">{header_text}</h2>'

    html = re.sub(r'^## (.+)$', header_id, html, flags=re.MULTILINE)

    def h3_id(match):
        header_text = match.group(1)
        header_id_text = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
        if db_prefix:
            header_id_text = f'{db_prefix}-{header_id_text}'
        return f'<h3 id="{header_id_text}">{header_text}</h3>'

    html = re.sub(r'^### (.+)$', h3_id, html, flags=re.MULTILINE)

    def h4_id(match):
        header_text = match.group(1)
        header_id_text = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
        if db_prefix:
            header_id_text = f'{db_prefix}-{header_id_text}'
        return f'<h4 id="{header_id_text}">{header_text}</h4>'

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

    # Links - update anchor links with db prefix
    def update_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        if link_url.startswith('#') and db_prefix:
            link_url = f'#{db_prefix}-{link_url[1:]}'
        return f'<a href="{link_url}">{link_text}</a>'

    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', update_link, html)

    # Lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
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

    # Paragraphs
    lines = html.split('\n')
    html_parts = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<') and not stripped.startswith('```'):
            if not any(stripped.startswith(f'<{tag}') for tag in ['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'pre', 'code', 'a', 'strong', 'em']):
                html_parts.append(f'<p>{stripped}</p>')
            else:
                html_parts.append(line)
        else:
            html_parts.append(line)

    html = '\n'.join(html_parts)

    # Clean up
    html = re.sub(r'<p></p>', '', html)
    html = re.sub(r'<p><p>', '<p>', html)
    html = re.sub(r'</p></p>', '</p>', html)

    return html

def extract_table_names(markdown_content):
    """Extract table names from markdown for sidebar navigation"""
    tables = []
    # Look for table headers like "#### Table: `table_name`" (db-6 format)
    table_pattern = r'#### Table:\s*`([^`]+)`'
    tables = re.findall(table_pattern, markdown_content)

    # If no tables found, try extracting from ER diagram (db-7 format)
    if not tables:
        # Look for table names in ER diagram section: "table_name {"
        er_pattern = r'^\s+(\w+)\s+\{'
        er_tables = re.findall(er_pattern, markdown_content, re.MULTILINE)
        if er_tables:
            tables = er_tables

    # If still no tables, extract from text descriptions (db-7 format)
    if not tables:
        # Look for patterns like "**Core Reference Tables**: `carriers`, `locations`, `ports`, `vessels`"
        core_tables_pattern = r'\*\*.*?Tables\*\*:\s*`([^`]+)`(?:\s*,\s*`([^`]+)`)*'
        matches = re.findall(core_tables_pattern, markdown_content)
        for match in matches:
            if isinstance(match, tuple):
                tables.extend([t for t in match if t])
            else:
                tables.append(match)

        # Also extract from ER diagram mermaid syntax
        mermaid_pattern = r'(\w+)\s+\{'
        mermaid_tables = re.findall(mermaid_pattern, markdown_content)
        if mermaid_tables:
            tables.extend(mermaid_tables)

    # Remove duplicates and sort
    tables = sorted(list(set(tables)))
    return tables

def extract_query_numbers(markdown_content):
    """Extract query numbers from markdown for sidebar navigation"""
    queries = []
    # Look for query headers like "## Query 1:" or "[Query 1:"
    query_pattern = r'(?:## |\[)Query (\d+):'
    query_nums = re.findall(query_pattern, markdown_content)
    return sorted([int(q) for q in query_nums])

def update_multi_database_html():
    """Update HTML file to include both db-6 and db-7 with proper navigation"""
    root_dir = Path(__file__).parent.parent

    # Read db-6 markdown
    db6_md_file = root_dir / 'db-6' / 'deliverable' / 'db-6.md'
    if not db6_md_file.exists():
        print(f"❌ Error: {db6_md_file} not found")
        return False

    print(f"📖 Reading db-6 markdown...")
    db6_content = db6_md_file.read_text(encoding='utf-8')

    # Read db-7 markdown
    db7_md_file = root_dir / 'db-7' / 'deliverable' / 'db-7.md'
    if not db7_md_file.exists():
        print(f"❌ Error: {db7_md_file} not found")
        return False

    print(f"📖 Reading db-7 markdown...")
    db7_content = db7_md_file.read_text(encoding='utf-8')

    # Extract table names and queries for navigation
    db6_tables = extract_table_names(db6_content)
    db7_tables = extract_table_names(db7_content)
    db6_queries = extract_query_numbers(db6_content)
    db7_queries = extract_query_numbers(db7_content)

    print(f"📊 db-6: {len(db6_tables)} tables, {len(db6_queries)} queries")
    print(f"📊 db-7: {len(db7_tables)} tables, {len(db7_queries)} queries")

    # Convert markdown to HTML
    print(f"🔄 Converting markdown to HTML...")
    db6_html_content = markdown_to_html(db6_content, db_prefix="db6")
    db7_html_content = markdown_to_html(db7_content, db_prefix="db7")

    # Read db-6 deliverable HTML template
    db6_html_file = root_dir / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    if not db6_html_file.exists():
        print(f"❌ Error: {db6_html_file} not found")
        return False

    print(f"📖 Reading HTML template...")
    html_template = db6_html_file.read_text(encoding='utf-8')

    # Update title to be generic
    html_template = re.sub(
        r'<title>.*?</title>',
        r'<title>Database Documentation - db-6 & db-7</title>',
        html_template
    )

    # Update sidebar header to be generic
    html_template = re.sub(
        r'<div class="sidebar-header">.*?</div>',
        r'<div class="sidebar-header">\n            <h1>Database Documentation</h1>\n            <p>db-6 & db-7</p>\n        </div>',
        html_template,
        flags=re.DOTALL
    )

    # Update db-7 sidebar navigation to match db-6 structure
    db7_nav_schema = '\n'.join([f'                        <a href="#db7-table-{table.replace("_", "-")}" class="nav-link">{table}</a>' for table in db7_tables])
    db7_nav_queries = '\n'.join([f'                        <a href="#db7-query-{q}" class="nav-link">Query {q}</a>' for q in db7_queries])

    db7_nav_section = f'''        <div class="nav-section">
            <div class="nav-section-title nav-accordion-header" data-section="db7">
                <span>db-7: Maritime Shipping Intelligence</span>
                <span class="accordion-icon">▼</span>
            </div>
            <div class="nav-accordion-content" id="db7-content">
                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="db7-overview">
                        <span>Overview</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="db7-overview-content">
                        <a href="#db7-overview" class="nav-link">Overview</a>
                        <a href="#db7-schema" class="nav-link">Schema</a>
                        <a href="#db7-queries" class="nav-link">Queries</a>
                    </div>
                </div>

                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="db7-schema">
                        <span>Schema</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="db7-schema-content">
{db7_nav_schema}
                    </div>
                </div>

                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="db7-queries">
                        <span>Queries</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="db7-queries-content">
{db7_nav_queries}
                    </div>
                </div>
            </div>
        </div>'''

    # Replace db-7 nav section
    db7_nav_pattern = r'(<div class="nav-section">\s*<div class="nav-section-title nav-accordion-header" data-section="db7">.*?</div>\s*</div>)'
    html_template = re.sub(db7_nav_pattern, db7_nav_section, html_template, flags=re.DOTALL)

    # Find main content section and replace with both databases
    main_content_pattern = r'(<main class="main-content">)(.*?)(</main>)'
    match = re.search(main_content_pattern, html_template, re.DOTALL)

    if not match:
        print("❌ Error: Could not find main content section")
        return False

    # Create db-6 header
    db6_header = '''<header id="db6-overview">
            <h1>Weather Consulting Database</h1>
            <p>Comprehensive documentation for database db-6, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with <strong>$1M+ Annual Recurring Revenue (ARR)</strong>.</p>
        </header>

        <div class="intro-box">
            <p><strong>Database ID:</strong> db-6</p>
            <p><strong>Version:</strong> 1.0</p>
            <p><strong>Total Tables:</strong> 34</p>
            <p><strong>Total Queries:</strong> 30</p>
        </div>

        <section id="db6-content-section">'''

    # Create db-7 header
    db7_header = '''<section id="db7-content-section">
        <header id="db7-overview">
            <h1>Maritime Shipping Intelligence Database</h1>
            <p>Comprehensive documentation for database db-7, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with <strong>$1M+ Annual Recurring Revenue (ARR)</strong>.</p>
        </header>

        <div class="intro-box">
            <p><strong>Database ID:</strong> db-7</p>
            <p><strong>Version:</strong> 1.0</p>
            <p><strong>Total Tables:</strong> 14</p>
            <p><strong>Total Queries:</strong> 30</p>
        </div>'''

    # Combine content
    new_main_content = f'''{match.group(1)}
        {db6_header}
        {db6_html_content}
        </section>

        {db7_header}
        {db7_html_content}
        </section>
        {match.group(3)}'''

    html_template = html_template.replace(match.group(0), new_main_content)

    # Write updated HTML
    print(f"💾 Writing updated HTML...")
    db6_html_file.write_text(html_template, encoding='utf-8')
    print(f"✅ Updated: {db6_html_file}")
    print(f"✅ File includes both db-6 and db-7 with proper navigation")
    return True

if __name__ == '__main__':
    update_multi_database_html()
