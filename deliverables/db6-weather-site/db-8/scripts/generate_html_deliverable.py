#!/usr/bin/env python3
"""
Generate HTML documentation from markdown deliverable
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

    # Code blocks
    html = re.sub(r'```sql\n(.*?)```', r'<pre><code class="language-sql">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```json\n(.*?)```', r'<pre><code class="language-json">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # Lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

    # Paragraphs
    paragraphs = html.split('\n\n')
    html_parts = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<'):
            html_parts.append(f'<p>{para}</p>')
        else:
            html_parts.append(para)
    html = '\n\n'.join(html_parts)

    return html

def generate_html_documentation():
    """Generate HTML documentation file"""
    script_dir = Path(__file__).parent
    db_dir = script_dir.parent

    # Read markdown deliverable
    md_file = db_dir / 'deliverable' / 'db-8.md'
    md_content = md_file.read_text()

    # Convert markdown to HTML
    html_content = markdown_to_html(md_content)

    # Generate full HTML document
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Market Intelligence Database - Documentation</title>
    <!-- Prism.js Syntax Highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
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
            margin: 1.5rem 0;
        }}

        code {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.875rem;
        }}

        pre code {{
            background: transparent;
            color: inherit;
        }}

        p {{
            margin-bottom: 1rem;
        }}

        ul, ol {{
            margin-left: 2rem;
            margin-bottom: 1rem;
        }}

        li {{
            margin-bottom: 0.5rem;
        }}

        a {{
            color: var(--accent);
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
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
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>Job Market Intelligence Database</h1>
            <p>db-8 Documentation</p>
        </div>
    </div>
    <div class="main-content">
        {html_content}
    </div>
    <script>
        // Initialize Prism.js syntax highlighting
        if (typeof Prism !== 'undefined') {{
            Prism.highlightAll();
        }}
    </script>
</body>
</html>"""

    # Write HTML file
    output_file = db_dir / 'deliverable' / 'db8-job-market-intelligence' / 'db-8_documentation.html'
    output_file.write_text(html_doc)
    print(f"HTML documentation Rebuilt: {output_file}")

if __name__ == '__main__':
    generate_html_documentation()
