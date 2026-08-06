#!/usr/bin/env python3
"""
Generate web-deployable deliverable package for db-7
Creates HTML documentation and JSON deliverable
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
db_dir = script_dir.parent
deliverable_dir = db_dir / 'deliverable' / 'db7-maritime-shipping-intelligence'

sys.path.insert(0, str(script_dir.parent.parent / 'scripts'))
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

def parse_schema(sql_content):
    """Parse schema.sql to extract table definitions"""
    tables = []
    current_table = None
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Match CREATE TABLE
        if line.startswith('CREATE TABLE'):
            match = re.match(r'CREATE TABLE\s+(\w+)', line, re.IGNORECASE)
            if match:
                if current_table:
                    tables.append(current_table)
                current_table = {
                    'name': match.group(1),
                    'description': '',
                    'columns': []
                }
        
        # Match column definitions
        elif current_table and re.match(r'^\w+\s+', line):
            # Extract column name, type, constraints
            parts = line.split(',')[0].strip()
            if parts:
                col_match = re.match(r'(\w+)\s+([^,\s]+(?:\s*\([^)]+\))?)', parts)
                if col_match:
                    col_name = col_match.group(1)
                    col_type = col_match.group(2)
                    
                    # Extract constraints
                    constraints = []
                    if 'PRIMARY KEY' in line:
                        constraints.append('PRIMARY KEY')
                    if 'UNIQUE' in line:
                        constraints.append('UNIQUE')
                    if 'NOT NULL' in line:
                        constraints.append('NOT NULL')
                    if 'FOREIGN KEY' in line or 'REFERENCES' in line:
                        constraints.append('FOREIGN KEY')
                    
                    # Extract description from comment
                    desc_match = re.search(r'--\s*(.+)', line)
                    description = desc_match.group(1) if desc_match else ''
                    
                    current_table['columns'].append({
                        'name': col_name,
                        'data_type': col_type,
                        'constraints': ', '.join(constraints) if constraints else '',
                        'description': description
                    })
    
    if current_table:
        tables.append(current_table)
    
    return tables

def generate_json_deliverable():
    """Generate JSON deliverable"""
    print("Generating JSON deliverable...")
    
    # Read queries.json
    queries_json_file = db_dir / 'queries' / 'queries.json'
    queries_data = json.loads(queries_json_file.read_text())
    
    # Read schema.sql
    schema_file = db_dir / 'data' / 'schema.sql'
    schema_content = schema_file.read_text()
    tables = parse_schema(schema_content)
    
    # Read DELIVERABLE.md for description
    deliverable_file = db_dir / 'DELIVERABLE.md'
    deliverable_content = deliverable_file.read_text()
    
    # Extract database name and description
    db_name_match = re.search(r'\*\*Database:\*\*\s*(.+?)(?:\n|$)', deliverable_content)
    db_name = db_name_match.group(1).strip() if db_name_match else "Maritime Shipping Intelligence Database"
    
    desc_match = re.search(r'### Description\s*\n\s*(.+?)(?:\n##|\n---|$)', deliverable_content, re.DOTALL)
    db_description = desc_match.group(1).strip() if desc_match else "Maritime Shipping Intelligence Database"
    
    # Build JSON deliverable
    json_deliverable = {
        "database": {
            "id": "db-7",
            "name": db_name,
            "description": db_description,
            "created_date": "2026-02-04",
            "version": "1.0"
        },
        "schema": {
            "total_tables": len(tables),
            "tables": tables
        },
        "queries": queries_data.get('queries', []),
        "metadata": {
            "total_queries": queries_data.get('total_queries', 30),
            "extraction_timestamp": queries_data.get('extraction_timestamp', get_est_timestamp()),
            "format_date": get_est_timestamp()
        }
    }
    
    # Write JSON deliverable
    json_output = deliverable_dir / 'db-7_deliverable.json'
    json_output.write_text(json.dumps(json_deliverable, indent=2))
    print(f"  ✓ JSON deliverable: {json_output}")
    
    return json_deliverable

def convert_markdown_to_html(md_content):
    """Convert markdown to HTML (simplified)"""
    html = md_content
    
    # Convert headers (preserve IDs for navigation)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', lambda m: f'<h2 id="{re.sub(r"[^a-z0-9]+", "-", m.group(1).lower())}">{m.group(1)}</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Convert code blocks
    html = re.sub(r'```sql\n(.*?)```', r'<pre><code class="language-sql">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```mermaid\n(.*?)```', r'<div class="mermaid">\1</div>', html, flags=re.DOTALL)
    html = re.sub(r'```json\n(.*?)```', r'<pre><code class="language-json">\1</code></pre>', html, flags=re.DOTALL)
    
    # Convert bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Convert italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Convert links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    
    # Convert line breaks
    html = html.replace('\n\n', '</p><p>')
    html = '<p>' + html + '</p>'
    
    return html

def generate_html_documentation():
    """Generate HTML documentation from db-7.md"""
    print("Generating HTML documentation...")
    
    # Read db-7.md
    md_file = deliverable_dir / 'db-7.md'
    if not md_file.exists():
        # Copy from parent deliverable directory
        parent_md = db_dir / 'deliverable' / 'db-7.md'
        if parent_md.exists():
            import shutil
            shutil.copy(parent_md, md_file)
        else:
            print(f"  ✗ Error: db-7.md not found")
            return None
    
    md_content = md_file.read_text()
    
    # Extract navigation links from markdown
    nav_links = []
    for match in re.finditer(r'^## (.+)$', md_content, re.MULTILINE):
        heading = match.group(1)
        anchor = re.sub(r'[^a-z0-9]+', '-', heading.lower())
        nav_links.append(f'<a href="#{anchor}" class="nav-link">{heading}</a>')
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Anti-robot / crawl protection -->
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="bingbot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <title>Maritime Shipping Intelligence Database - Documentation</title>
    <!-- Prism.js Syntax Highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
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
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.65;
            color: var(--text-primary);
            background: var(--bg-primary);
            display: flex;
            min-height: 100vh;
        }}
        
        .sidebar {{
            width: 280px;
            background: var(--bg-primary);
            border-right: 1px solid var(--border);
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            overflow-y: auto;
            padding: 2rem 0;
        }}
        
        .sidebar-header {{
            padding: 0 1.5rem 1rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1rem;
        }}
        
        .sidebar-header h1 {{
            font-size: 0.9375rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }}
        
        .main-content {{
            margin-left: 280px;
            padding: 2rem 3rem;
            max-width: 900px;
            line-height: 1.8;
        }}
        
        h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            margin-top: 2rem;
        }}
        
        h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        
        h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}
        
        pre {{
            background: var(--code-bg);
            color: var(--code-text);
            padding: 1.5rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            margin: 1rem 0;
            border: 1px solid var(--code-border);
        }}
        
        code {{
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.875rem;
        }}
        
        .nav-link {{
            display: block;
            padding: 0.5rem 1.5rem;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.875rem;
        }}
        
        .nav-link:hover {{
            color: var(--text-primary);
            background: var(--bg-secondary);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            font-weight: 600;
            background: var(--bg-secondary);
        }}
        
        .mermaid {{
            margin: 2rem 0;
            background: var(--bg-secondary);
            padding: 1rem;
            border-radius: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>db-7</h1>
            <p style="font-size: 0.75rem; color: var(--text-light); margin-top: 0.5rem;">Maritime Shipping Intelligence Database</p>
        </div>
        <nav>
            {' '.join(nav_links[:20])}
        </nav>
    </div>
    <div class="main-content">
{convert_markdown_to_html(md_content)}
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</body>
</html>"""
    
    html_output = deliverable_dir / 'db-7_documentation.html'
    html_output.write_text(html_content)
    print(f"  ✓ HTML documentation: {html_output}")
    
    return html_output

def create_vercel_config():
    """Create Vercel configuration file"""
    vercel_config = {
        "rewrites": [
            {
                "source": "/",
                "destination": "/db-7_documentation.html"
            },
            {
                "source": "/db-7_deliverable.json",
                "destination": "/db-7_deliverable.json"
            }
        ],
        "headers": [
            {
                "source": "/(.*\\.html)",
                "headers": [
                    {
                        "key": "Content-Type",
                        "value": "text/html"
                    }
                ]
            },
            {
                "source": "/(.*\\.json)",
                "headers": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ]
            }
        ]
    }
    
    vercel_file = deliverable_dir / 'vercel.json'
    vercel_file.write_text(json.dumps(vercel_config, indent=2))
    print(f"  ✓ Vercel config: {vercel_file}")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# macOS
.DS_Store
.AppleDouble
.LSOverride

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Temporary files
*.tmp
*.log
*.bak
"""
    
    gitignore_file = deliverable_dir / '.gitignore'
    gitignore_file.write_text(gitignore_content)
    print(f"  ✓ .gitignore: {gitignore_file}")

def copy_data_files():
    """Copy schema and data files to data/ subdirectory"""
    data_dir = deliverable_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    
    source_schema = db_dir / 'data' / 'schema.sql'
    source_data = db_dir / 'data' / 'data.sql'
    
    if source_schema.exists():
        import shutil
        shutil.copy(source_schema, data_dir / 'schema.sql')
        print(f"  ✓ Copied schema.sql")
    
    if source_data.exists():
        import shutil
        shutil.copy(source_data, data_dir / 'data.sql')
        print(f"  ✓ Copied data.sql")

def main():
    print("="*70)
    print("Generating Web-Deployable Deliverable Package for db-7")
    print("="*70)
    
    deliverable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy db-7.md from parent deliverable directory
    parent_md = db_dir / 'deliverable' / 'db-7.md'
    if parent_md.exists():
        import shutil
        shutil.copy(parent_md, deliverable_dir / 'db-7.md')
        print(f"  ✓ Copied db-7.md")
    
    # Generate JSON deliverable
    json_deliverable = generate_json_deliverable()
    
    # Generate HTML documentation
    html_file = generate_html_documentation()
    
    # Create Vercel config
    create_vercel_config()
    
    # Create .gitignore
    create_gitignore()
    
    # Copy data files
    copy_data_files()
    
    print("\n" + "="*70)
    print("Web-Deployable Package Generated")
    print("="*70)
    print(f"Directory: {deliverable_dir}")
    print(f"Files:")
    print(f"  - db-7.md (markdown source)")
    print(f"  - db-7_documentation.html (HTML documentation)")
    print(f"  - db-7_deliverable.json (JSON deliverable)")
    print(f"  - vercel.json (Vercel config)")
    print(f"  - .gitignore")
    print(f"  - data/ (schema and data files)")
    print("="*70)

if __name__ == '__main__':
    main()
