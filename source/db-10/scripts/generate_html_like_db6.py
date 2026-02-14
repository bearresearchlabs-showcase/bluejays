#!/usr/bin/env python3
"""
Generate HTML documentation exactly like db-6 structure
Uses the same markdown conversion logic as update_multi_database_html.py
"""

import sys
import re
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent
db_dir = script_dir.parent
root_scripts = db_dir.parent / 'scripts'
sys.path.insert(0, str(root_scripts))

from update_multi_database_html import markdown_to_html, extract_table_names, extract_query_numbers

def generate_html_like_db6():
    """Generate HTML documentation matching db-6 structure exactly"""
    
    # Read db-10 markdown
    md_file = db_dir / 'deliverable' / 'db-10.md'
    if not md_file.exists():
        print(f"❌ Error: {md_file} not found")
        return False
    
    print(f"📖 Reading db-10 markdown...")
    md_content = md_file.read_text(encoding='utf-8')
    
    # Extract table names and queries for navigation
    tables = extract_table_names(md_content)
    queries = extract_query_numbers(md_content)
    
    print(f"📊 Found {len(tables)} tables, {len(queries)} queries")
    
    # Convert markdown to HTML using same function as db-6
    print(f"🔄 Converting markdown to HTML...")
    html_content = markdown_to_html(md_content)
    
    # Read db-6 HTML template to get exact structure
    db6_html_file = db_dir.parent / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    if db6_html_file.exists():
        print(f"📖 Reading db-6 HTML template...")
        html_template = db6_html_file.read_text(encoding='utf-8')
        
        # Extract complete head section (including CSS)
        head_match = re.search(r'(<head>.*?</head>)', html_template, re.DOTALL)
        head_section = head_match.group(1) if head_match else ''
        
        # Update title in head
        head_section = re.sub(
            r'<title>.*?</title>',
            r'<title>Shopping Aggregator Database - Documentation</title>',
            head_section
        )
        
        # Extract sidebar structure template
        sidebar_match = re.search(r'(<div class="sidebar">.*?</nav>\s*</div>\s*</div>)', html_template, re.DOTALL)
        sidebar_template = sidebar_match.group(1) if sidebar_match else ''
        
        # Extract scripts and closing tags
        script_match = re.search(r'(<script>.*?</body>\s*</html>)', html_template, re.DOTALL)
        scripts_closing = script_match.group(1) if script_match else ''
    else:
        # Fallback: use basic template
        print("⚠️  db-6 template not found, using fallback")
        head_section = ''
        sidebar_template = ''
        scripts_closing = '<script>\n        mermaid.initialize({ startOnLoad: true });\n        if (typeof Prism !== \'undefined\') {\n            Prism.highlightAll();\n        }\n    </script>\n</body>\n</html>'
    
    # Build sidebar navigation - use db-6 structure if available
    if sidebar_template:
        # Replace db-6 specific content with db-10 content
        sidebar_nav = sidebar_template
        sidebar_nav = re.sub(
            r'<h1>.*?</h1>',
            r'<h1>db-10</h1>',
            sidebar_nav
        )
        sidebar_nav = re.sub(
            r'<p[^>]*>.*?</p>',
            r'<p style="font-size: 0.75rem; color: var(--text-light); margin-top: 0.5rem;">Shopping Aggregator Database</p>',
            sidebar_nav,
            count=1
        )
        # Update navigation links to match db-10 structure
        # Keep the structure but update links
    else:
        # Build sidebar navigation from scratch
        sidebar_nav = f'''        <div class="sidebar-header">
            <h1>db-10</h1>
            <p style="font-size: 0.75rem; color: var(--text-light); margin-top: 0.5rem;">Shopping Aggregator Database</p>
        </div>
        <nav>
            <a href="#database-overview" class="nav-link">Database Overview</a>
            <a href="#database-schema-documentation" class="nav-link">Schema Documentation</a>'''
        
        # Add table links
        if tables:
            sidebar_nav += '\n            <div class="nav-section-title">Tables</div>'
            for table in tables[:20]:  # Limit to first 20 tables
                table_id = table.replace('_', '-').lower()
                sidebar_nav += f'\n            <a href="#table-{table_id}" class="nav-link">{table}</a>'
        
        # Add query links
        if queries:
            sidebar_nav += '\n            <div class="nav-section-title">Queries</div>'
            for q in queries:
                sidebar_nav += f'\n            <a href="#query-{q}" class="nav-link">Query {q}</a>'
        
        sidebar_nav += '\n        </nav>'
    
    # Build complete HTML - use db-6 structure exactly
    if head_section:
        html_doc = f'''<!DOCTYPE html>
<html lang="en">
{head_section}
<body>
    <div class="sidebar">
{sidebar_nav}
    </div>
    <div class="main-content">
{html_content}
    </div>
{scripts_closing}'''
    else:
        # Fallback HTML structure
        html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <title>Shopping Aggregator Database - Documentation</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
{get_fallback_css()}
</head>
<body>
    <div class="sidebar">
{sidebar_nav}
    </div>
    <div class="main-content">
{html_content}
    </div>
{get_fallback_closing()}'''
    
    # Write HTML file
    output_file = db_dir / 'deliverable' / 'db10-marketing-intelligence' / 'db-10_documentation.html'
    output_file.write_text(html_doc, encoding='utf-8')
    print(f"✅ Rebuilt: {output_file}")
    print(f"   Size: {len(html_doc):,} characters")
    
    return True

def get_fallback_css():
    """Fallback CSS if db-6 template not available"""
    return '''    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #fafafa;
            --bg-dark: #000000;
            --text-primary: #000000;
            --text-secondary: #6b7280;
            --text-light: #9ca3af;
            --border: #e5e7eb;
            --accent: #000000;
            --code-bg: #000000;
            --code-text: #ffffff;
            --code-border: #333333;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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
        
        .nav-link {
            display: block;
            padding: 0.5rem 1.5rem;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.875rem;
        }
        
        .nav-link:hover {
            color: var(--text-primary);
            background: var(--bg-secondary);
        }
        
        .nav-section-title {
            padding: 0.75rem 1.5rem 0.5rem;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            margin-top: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }
        
        h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        
        pre {
            background: var(--code-bg);
            color: var(--code-text);
            padding: 1.5rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        code {
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.875rem;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        th {
            font-weight: 600;
            background: var(--bg-secondary);
        }
    </style>'''

def get_fallback_closing():
    """Fallback closing tags"""
    return '''    <script>
        mermaid.initialize({ startOnLoad: true });
        if (typeof Prism !== 'undefined') {
            Prism.highlightAll();
        }
    </script>
</body>
</html>'''

if __name__ == '__main__':
    print("="*70)
    print("Generating HTML Documentation (db-6 style)")
    print("="*70)
    success = generate_html_like_db6()
    if success:
        print("="*70)
        print("✅ HTML documentation generated successfully")
        print("="*70)
    else:
        print("="*70)
        print("❌ Failed to generate HTML documentation")
        print("="*70)
        sys.exit(1)
