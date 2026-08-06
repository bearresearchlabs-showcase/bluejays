#!/usr/bin/env python3
"""
Generate web-deployable deliverable package for any db-N.
Creates HTML documentation, JSON deliverable, vercel.json, .gitignore, and data/.
Follows db-6 golden solution structure.
"""

import sys
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

DB_TO_DELIVERABLE = {
    1: "db1-chat-messaging-platform",
    2: "db2-filling-station-retail",
    3: "db3-hierarchical-orders",
    4: "db4-sharedai-models",
    5: "db5-pos-retail",
    6: "db6-weather-consulting-insurance",
    7: "db7-maritime-shipping-intelligence",
    8: "db8-job-market-intelligence",
    9: "db9-shipping-intelligence",
    10: "db10-marketing-intelligence",
    11: "db11-parking-intelligence",
    12: "db12-credit-card-and-rewards-optimization-system",
    13: "db13-ai-benchmark-marketing-database",
    14: "db14-cloud-instance-cost-database",
    15: "db15-electricity-cost-and-solar-rebate-database",
    16: "db16-flood-risk-assessment",
}


def parse_schema(sql_content: str) -> list:
    """Parse schema.sql to extract table definitions."""
    tables = []
    current_table = None

    for line in sql_content.split('\n'):
        line_stripped = line.strip()

        if line_stripped.startswith('CREATE TABLE'):
            match = re.match(r'CREATE TABLE\s+(\w+)', line_stripped, re.IGNORECASE)
            if match:
                if current_table:
                    tables.append(current_table)
                current_table = {
                    'name': match.group(1),
                    'description': '',
                    'columns': []
                }

        elif current_table and re.match(r'^\w+\s+', line_stripped):
            parts = line_stripped.split(',')[0].strip()
            if parts:
                col_match = re.match(r'(\w+)\s+([^,\s]+(?:\s*\([^)]+\))?)', parts)
                if col_match:
                    col_name = col_match.group(1)
                    col_type = col_match.group(2)
                    constraints = []
                    if 'PRIMARY KEY' in line_stripped:
                        constraints.append('PRIMARY KEY')
                    if 'UNIQUE' in line_stripped:
                        constraints.append('UNIQUE')
                    if 'NOT NULL' in line_stripped:
                        constraints.append('NOT NULL')
                    if 'FOREIGN KEY' in line_stripped or 'REFERENCES' in line_stripped:
                        constraints.append('FOREIGN KEY')
                    desc_match = re.search(r'--\s*(.+)', line_stripped)
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


def convert_markdown_to_html(md_content: str) -> str:
    """Convert markdown to HTML (simplified)."""
    html = md_content
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', lambda m: f'<h2 id="{re.sub(r"[^a-z0-9]+", "-", m.group(1).lower())}">{m.group(1)}</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'```sql\n(.*?)```', r'<pre><code class="language-sql">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```mermaid\n(.*?)```', r'<div class="mermaid">\1</div>', html, flags=re.DOTALL)
    html = re.sub(r'```json\n(.*?)```', r'<pre><code class="language-json">\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    html = html.replace('\n\n', '</p><p>')
    html = '<p>' + html + '</p>'
    return html


def generate_web_deliverable(db_num: int, verbose: bool = True) -> bool:
    """Generate web-deployable folder for db-N."""
    db_dir = BASE_DIR / f'db-{db_num}'
    folder_name = DB_TO_DELIVERABLE.get(db_num)
    if not folder_name:
        if verbose:
            print(f"  Skip db-{db_num}: no folder mapping")
        return False

    deliverable_dir = db_dir / 'deliverable' / folder_name
    md_file = db_dir / 'deliverable' / f'db-{db_num}.md'
    queries_json_file = db_dir / 'queries' / 'queries.json'
    data_dir_src = db_dir / 'data'

    if not db_dir.exists():
        if verbose:
            print(f"  Skip db-{db_num}: directory not found")
        return False

    if not md_file.exists():
        md_file = db_dir / 'deliverable' / 'DELIVERABLE.md'
    if not md_file.exists():
        md_file = db_dir / 'DELIVERABLE.md'
    if not md_file.exists():
        if verbose:
            print(f"  Skip db-{db_num}: no db-{db_num}.md or DELIVERABLE.md")
        return False

    if not queries_json_file.exists():
        if verbose:
            print(f"  Skip db-{db_num}: queries.json not found")
        return False

    deliverable_dir.mkdir(parents=True, exist_ok=True)

    # Extract database name from markdown
    md_content = md_file.read_text(encoding='utf-8')
    db_name_match = re.search(r'\*\*Type:\*\*\s*(.+?)(?:\n|$)', md_content)
    db_type = db_name_match.group(1).strip() if db_name_match else f"Database db-{db_num}"
    db_title = db_type

    # Copy db-{N}.md
    shutil.copy2(md_file, deliverable_dir / f'db-{db_num}.md')
    if verbose:
        print(f"  ✓ Copied db-{db_num}.md")

    # Generate JSON deliverable
    queries_data = json.loads(queries_json_file.read_text(encoding='utf-8'))
    tables = []
    schema_file = data_dir_src / 'schema.sql'
    if schema_file.exists():
        tables = parse_schema(schema_file.read_text(encoding='utf-8'))

    desc_match = re.search(r'### Description\s*\n\s*(.+?)(?:\n##|\n---|$)', md_content, re.DOTALL)
    db_description = desc_match.group(1).strip() if desc_match else db_type

    json_deliverable = {
        "database": {
            "id": f"db-{db_num}",
            "name": db_title,
            "description": db_description,
            "created_date": "2026-02-09",
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

    json_output = deliverable_dir / f'db-{db_num}_deliverable.json'
    json_output.write_text(json.dumps(json_deliverable, indent=2), encoding='utf-8')
    if verbose:
        print(f"  ✓ JSON deliverable: {json_output.name}")

    # Generate HTML
    nav_links = []
    for match in re.finditer(r'^## (.+)$', md_content, re.MULTILINE):
        heading = match.group(1)
        anchor = re.sub(r'[^a-z0-9]+', '-', heading.lower())
        nav_links.append(f'<a href="#{anchor}" class="nav-link">{heading}</a>')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="bingbot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <title>{db_title} - Documentation</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{ --bg-primary: #ffffff; --bg-secondary: #fafafa; --text-primary: #000000; --text-secondary: #6b7280; --border: #e5e7eb; --code-bg: #000000; --code-text: #ffffff; --code-border: #333333; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.65; color: var(--text-primary); background: var(--bg-primary); display: flex; min-height: 100vh; }}
        .sidebar {{ width: 280px; background: var(--bg-primary); border-right: 1px solid var(--border); height: 100vh; position: fixed; overflow-y: auto; padding: 2rem 0; }}
        .sidebar-header {{ padding: 0 1.5rem 1rem; border-bottom: 1px solid var(--border); margin-bottom: 1rem; }}
        .sidebar-header h1 {{ font-size: 0.9375rem; font-weight: 600; }}
        .main-content {{ margin-left: 280px; padding: 2rem 3rem; max-width: 900px; line-height: 1.8; }}
        h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 1rem; margin-top: 2rem; }}
        h2 {{ font-size: 1.5rem; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); }}
        h3 {{ font-size: 1.25rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; }}
        pre {{ background: var(--code-bg); color: var(--code-text); padding: 1.5rem; border-radius: 0.5rem; overflow-x: auto; margin: 1rem 0; border: 1px solid var(--code-border); }}
        code {{ font-family: Monaco, Menlo, monospace; font-size: 0.875rem; }}
        .nav-link {{ display: block; padding: 0.5rem 1.5rem; color: var(--text-secondary); text-decoration: none; font-size: 0.875rem; }}
        .nav-link:hover {{ color: var(--text-primary); background: var(--bg-secondary); }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ font-weight: 600; background: var(--bg-secondary); }}
        .mermaid {{ margin: 2rem 0; background: var(--bg-secondary); padding: 1rem; border-radius: 0.5rem; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>db-{db_num}</h1>
            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">{db_title}</p>
        </div>
        <nav>
            {' '.join(nav_links[:25])}
        </nav>
    </div>
    <div class="main-content">
{convert_markdown_to_html(md_content)}
    </div>
    <script>if (typeof Prism !== 'undefined') Prism.highlightAll();</script>
    <script>mermaid.initialize({{ startOnLoad: true }});</script>
</body>
</html>"""

    html_output = deliverable_dir / f'db-{db_num}_documentation.html'
    html_output.write_text(html_content, encoding='utf-8')
    if verbose:
        print(f"  ✓ HTML: {html_output.name}")

    # Vercel config
    vercel_config = {
        "rewrites": [
            {"source": "/", "destination": f"/db-{db_num}_documentation.html"},
            {"source": f"/db-{db_num}_deliverable.json", "destination": f"/db-{db_num}_deliverable.json"}
        ],
        "headers": [
            {"source": "/(.*\\.html)", "headers": [{"key": "Content-Type", "value": "text/html"}]},
            {"source": "/(.*\\.json)", "headers": [{"key": "Content-Type", "value": "application/json"}]}
        ]
    }
    (deliverable_dir / 'vercel.json').write_text(json.dumps(vercel_config, indent=2), encoding='utf-8')
    if verbose:
        print(f"  ✓ vercel.json")

    # .gitignore (include *.dump to prevent re-adding)
    gitignore = """# macOS
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

# Database dumps
*.dump

# Temporary files
*.tmp
*.log
*.bak
"""
    (deliverable_dir / '.gitignore').write_text(gitignore, encoding='utf-8')
    if verbose:
        print(f"  ✓ .gitignore")

    # Copy data files (all *.sql, exclude *.dump)
    data_dir_dst = deliverable_dir / 'data'
    data_dir_dst.mkdir(exist_ok=True)
    if data_dir_src.exists():
        for f in data_dir_src.iterdir():
            if f.is_file() and f.suffix.lower() == '.sql':
                shutil.copy2(f, data_dir_dst / f.name)
        if verbose:
            print(f"  ✓ data/ (schema and data SQL files)")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate web-deployable for db-N')
    parser.add_argument('db_nums', nargs='*', type=int, help='Database numbers (e.g. 1 2 3) or empty for 1-15')
    parser.add_argument('-q', '--quiet', action='store_true', help='Less output')
    args = parser.parse_args()

    db_nums = args.db_nums if args.db_nums else list(range(1, 16))
    verbose = not args.quiet

    print("=" * 70)
    print("Generating Web-Deployable Deliverables")
    print("=" * 70)

    ok = 0
    for n in db_nums:
        if verbose:
            print(f"\ndb-{n}:")
        if generate_web_deliverable(n, verbose=verbose):
            ok += 1

    print("\n" + "=" * 70)
    print(f"Generated {ok}/{len(db_nums)} web-deployable packages")
    print("=" * 70)
    return 0 if ok == len(db_nums) else 1


if __name__ == '__main__':
    sys.exit(main())
