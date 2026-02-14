#!/usr/bin/env python3
"""Create web-deployable deliverable package for db-11"""

import json
import re
from pathlib import Path

# Paths
DB_DIR = Path(__file__).parent.parent
DELIVERABLE_DIR = DB_DIR / 'deliverable' / 'db11-parking-intelligence'
QUERIES_JSON = DB_DIR / 'queries' / 'queries.json'
SCHEMA_SQL = DB_DIR / 'data' / 'schema.sql'
MD_FILE = DELIVERABLE_DIR / 'db-11.md'

# Read queries.json
with open(QUERIES_JSON, 'r') as f:
    queries_data = json.load(f)

# Read schema.sql to extract table info
with open(SCHEMA_SQL, 'r') as f:
    schema_content = f.read()

# Extract table names from schema
table_matches = re.findall(r'CREATE TABLE (\w+)', schema_content)
tables = [{'name': t, 'description': f'{t} table'} for t in table_matches]

# Create JSON deliverable
deliverable_json = {
    'database': {
        'id': 'db-11',
        'name': 'Parking Intelligence Database',
        'description': 'Comprehensive parking intelligence database with 30 production queries for market analysis, competitive intelligence, and revenue optimization.',
        'created_date': '2026-02-04',
        'version': '1.0'
    },
    'schema': {
        'total_tables': len(tables),
        'tables': tables
    },
    'queries': queries_data.get('queries', [])
}

# Write JSON deliverable
json_output = DELIVERABLE_DIR / 'db-11_deliverable.json'
with open(json_output, 'w') as f:
    json.dump(deliverable_json, f, indent=2)

print(f'✓ Created JSON deliverable: {json_output}')
print(f'  Total tables: {len(tables)}')
print(f'  Total queries: {len(deliverable_json["queries"])}')

# Read markdown file
with open(MD_FILE, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Simple markdown to HTML conversion
def md_to_html(md):
    # Escape HTML
    md = md.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Convert code blocks (do this before other conversions)
    md = re.sub(r'```sql\n(.*?)```', lambda m: f'<pre><code class="language-sql">{m.group(1)}</code></pre>', md, flags=re.DOTALL)
    md = re.sub(r'```json\n(.*?)```', lambda m: f'<pre><code class="language-json">{m.group(1)}</code></pre>', md, flags=re.DOTALL)
    md = re.sub(r'```mermaid\n(.*?)```', lambda m: f'<pre class="mermaid">{m.group(1)}</pre>', md, flags=re.DOTALL)
    md = re.sub(r'```\n(.*?)```', lambda m: f'<pre><code>{m.group(1)}</code></pre>', md, flags=re.DOTALL)
    
    # Convert headers
    md = re.sub(r'^# (.+)$', r'<h1>\1</h1>', md, flags=re.MULTILINE)
    md = re.sub(r'^## (.+)$', lambda m: f'<h2 id="{re.sub(r"[^a-z0-9]+", "-", m.group(1).lower())}">\1</h2>', md, flags=re.MULTILINE)
    md = re.sub(r'^### (.+)$', lambda m: f'<h3 id="{re.sub(r"[^a-z0-9]+", "-", m.group(1).lower())}">\1</h3>', md, flags=re.MULTILINE)
    
    # Convert inline code
    md = re.sub(r'`([^`]+)`', r'<code>\1</code>', md)
    
    # Convert bold
    md = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md)
    
    # Convert links
    md = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', md)
    
    # Convert paragraphs
    lines = md.split('\n')
    html_lines = []
    in_para = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_para:
                html_lines.append('</p>')
                in_para = False
        elif line.startswith('<'):
            if in_para:
                html_lines.append('</p>')
                in_para = False
            html_lines.append(line)
        else:
            if not in_para:
                html_lines.append('<p>')
                in_para = True
            html_lines.append(line)
    
    if in_para:
        html_lines.append('</p>')
    
    return '\n'.join(html_lines)

html_content = md_to_html(md_content)

# HTML template
html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="bingbot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <title>Parking Intelligence Database - Documentation</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #fafafa;
            --text-primary: #000000;
            --text-secondary: #6b7280;
            --border: #e5e7eb;
            --accent: #000000;
            --code-bg: #000000;
            --code-text: #ffffff;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.65;
            color: var(--text-primary);
            background: var(--bg-primary);
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 280px;
            background: var(--bg-primary);
            border-right: 1px solid var(--border);
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            overflow-y: auto;
            padding: 2rem 0;
        }
        .sidebar-header {
            padding: 0 1.5rem 1rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1rem;
        }
        .sidebar-header h1 {
            font-size: 0.9375rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }
        .main-content {
            margin-left: 280px;
            padding: 2rem 3rem;
            max-width: 900px;
            line-height: 1.8;
        }
        h1 { font-size: 2rem; font-weight: 700; margin-bottom: 1rem; margin-top: 2rem; }
        h2 { font-size: 1.5rem; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); }
        h3 { font-size: 1.25rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; }
        pre { background: var(--code-bg); color: var(--code-text); padding: 1.5rem; border-radius: 0.5rem; overflow-x: auto; margin: 1.5rem 0; }
        code { font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; font-size: 0.875rem; }
        pre code { background: transparent; color: inherit; }
        p { margin-bottom: 1rem; }
        ul, ol { margin-left: 2rem; margin-bottom: 1rem; }
        li { margin-bottom: 0.5rem; }
        a { color: var(--accent); text-decoration: none; }
        a:hover { text-decoration: underline; }
        table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }
        th { font-weight: 600; background: var(--bg-secondary); }
    </style>
    <script>
        mermaid.initialize({startOnLoad:true});
    </script>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>Parking Intelligence Database</h1>
            <p>db-11 Documentation</p>
        </div>
    </div>
    <div class="main-content">
{content}
    </div>
</body>
</html>'''

# Write HTML file
html_output = DELIVERABLE_DIR / 'db-11_documentation.html'
with open(html_output, 'w', encoding='utf-8') as f:
    f.write(html_template.replace('{content}', html_content))

print(f'✓ Created HTML documentation: {html_output}')
print('✓ Web-deployable package complete!')
