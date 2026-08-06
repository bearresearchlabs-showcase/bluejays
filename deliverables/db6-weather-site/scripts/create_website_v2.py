#!/usr/bin/env python3
"""
Create a general website with dashboard and individual database pages
Extracts main content from deliverable HTML files
"""

import re
from pathlib import Path

def extract_css_from_db6():
    """Extract CSS from db-6_documentation.html"""
    db6_file = Path(__file__).parent.parent / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    
    if not db6_file.exists():
        print(f"❌ Error: {db6_file} not found")
        return None
    
    content = db6_file.read_text(encoding='utf-8')
    
    # Extract CSS from <style> tag
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if style_match:
        return style_match.group(1)
    
    return None

def extract_sidebar_from_db6():
    """Extract sidebar navigation from db-6_documentation.html"""
    db6_file = Path(__file__).parent.parent / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    
    if not db6_file.exists():
        return None
    
    content = db6_file.read_text(encoding='utf-8')
    
    # Extract sidebar - it's a <nav> tag, find until </nav> or before <main>
    sidebar_match = re.search(r'(<nav class="sidebar">.*?</nav>)', content, re.DOTALL)
    if sidebar_match:
        return sidebar_match.group(1)
    
    # Alternative: extract from <nav> to before <main>
    nav_start = content.find('<nav class="sidebar">')
    main_start = content.find('<main class="main-content">')
    if nav_start > 0 and main_start > nav_start:
        return content[nav_start:main_start].rstrip()
    
    return None

def extract_main_content(html_file):
    """Extract main content from deliverable HTML"""
    if not html_file.exists():
        return None
    
    content = html_file.read_text(encoding='utf-8')
    
    # Extract main content section
    main_match = re.search(r'(<main class="main-content">.*?</main>)', content, re.DOTALL)
    if main_match:
        return main_match.group(1)
    
    return None

def extract_scripts_from_db6():
    """Extract JavaScript from db-6_documentation.html"""
    db6_file = Path(__file__).parent.parent / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    
    if not db6_file.exists():
        return None
    
    content = db6_file.read_text(encoding='utf-8')
    
    # Extract all script tags
    scripts = []
    script_pattern = r'(<script[^>]*>.*?</script>)'
    for match in re.finditer(script_pattern, content, re.DOTALL):
        scripts.append(match.group(1))
    
    return '\n'.join(scripts) if scripts else None

def get_database_info():
    """Get deliverable paths for each database"""
    databases = {}
    root_dir = Path(__file__).parent.parent
    
    for db_num in range(6, 16):
        db_dir = root_dir / f'db-{db_num}' / 'deliverable'
        if not db_dir.exists():
            continue
        
        # Find documentation.html file
        doc_files = list(db_dir.rglob('*documentation.html'))
        if doc_files:
            databases[f'db-{db_num}'] = {
                'path': doc_files[0],
                'name': f'DB-{db_num}'
            }
    
    return databases

def create_dashboard(css_content):
    """Create dashboard index.html"""
    databases = get_database_info()
    
    dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Documentation Portal</title>
    <!-- Prism.js Syntax Highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
    <style>
{css_content}
        /* Dashboard specific styles */
        .dashboard-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 80vh;
            padding: var(--spacing-2xl);
        }}
        
        .dashboard-header {{
            text-align: center;
            margin-bottom: var(--spacing-2xl);
        }}
        
        .dashboard-header h1 {{
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: var(--spacing-md);
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }}
        
        .dashboard-header p {{
            font-size: 1.125rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .database-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: var(--spacing-lg);
            width: 100%;
            max-width: 1200px;
            margin-top: var(--spacing-xl);
        }}
        
        .database-card {{
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: var(--spacing-lg);
            transition: all 0.2s ease;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        
        .database-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-color: var(--bg-dark);
            transform: translateY(-2px);
        }}
        
        .database-card h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: var(--spacing-sm);
            color: var(--text-primary);
        }}
        
        .database-card p {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin: 0;
        }}
        
        .database-card .db-number {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-light);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: var(--spacing-xs);
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="dashboard-header">
            <h1>Database Documentation Portal</h1>
            <p>Comprehensive documentation for production databases. Each database includes complete schema documentation, SQL queries with business context, and usage instructions.</p>
        </div>
        
        <div class="database-grid">
"""
    
    # Sort databases by number
    sorted_dbs = sorted(databases.items(), key=lambda x: int(x[0].split('-')[1]))
    
    for db_id, db_info in sorted_dbs:
        dashboard_html += f"""            <a href="{db_id}.html" class="database-card">
                <div class="db-number">{db_info['name']}</div>
                <h3>{db_info['name']} Documentation</h3>
                <p>View complete documentation including schema, queries, and usage instructions.</p>
            </a>
"""
    
    dashboard_html += """        </div>
    </div>
</body>
</html>
"""
    
    return dashboard_html

def create_database_page(db_id, db_info, css_content, sidebar_content, scripts_content):
    """Create individual database page with embedded content"""
    # Extract main content from deliverable HTML
    main_content = extract_main_content(db_info['path'])
    
    if not main_content:
        main_content = '<main class="main-content"><p>Content not available.</p></main>'
    
    # Update sidebar to include back link
    sidebar_with_back = sidebar_content.replace(
        '<nav class="sidebar">',
        '<nav class="sidebar"><div style="padding: 1rem 1.25rem; border-bottom: 1px solid var(--border);"><a href="index.html" style="color: var(--text-primary); text-decoration: none; font-size: 0.875rem;">← Back to Dashboard</a></div>'
    ) if sidebar_content else ''
    
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{db_info['name']} - Documentation</title>
    <!-- Prism.js Syntax Highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
    <style>
{css_content}
    </style>
</head>
<body>
    {sidebar_with_back}
    {main_content}
    {scripts_content if scripts_content else ''}
</body>
</html>
"""
    
    return page_html

def main():
    """Create website structure"""
    root_dir = Path(__file__).parent.parent
    website_dir = root_dir / 'website'
    website_dir.mkdir(exist_ok=True)
    
    print("📖 Extracting CSS, sidebar, and scripts from db-6 documentation...")
    css_content = extract_css_from_db6()
    sidebar_content = extract_sidebar_from_db6()
    scripts_content = extract_scripts_from_db6()
    
    if not css_content:
        print("❌ Failed to extract CSS")
        return False
    
    print("📊 Getting database information...")
    databases = get_database_info()
    print(f"✅ Found {len(databases)} databases")
    
    print("🏠 Creating dashboard...")
    dashboard_html = create_dashboard(css_content)
    (website_dir / 'index.html').write_text(dashboard_html, encoding='utf-8')
    print("✅ Created index.html")
    
    print("📄 Creating database pages...")
    for db_id, db_info in databases.items():
        print(f"  Processing {db_id}...")
        page_html = create_database_page(db_id, db_info, css_content, sidebar_content, scripts_content)
        (website_dir / f'{db_id}.html').write_text(page_html, encoding='utf-8')
        print(f"  ✅ Created {db_id}.html")
    
    print(f"\n✅ Website created successfully in {website_dir}")
    return True

if __name__ == '__main__':
    main()
