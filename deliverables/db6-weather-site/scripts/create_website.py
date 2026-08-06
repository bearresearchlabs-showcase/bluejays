#!/usr/bin/env python3
"""
Create a general website with dashboard and individual database pages
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
            # Get relative path from website folder
            rel_path = doc_files[0].relative_to(root_dir)
            databases[f'db-{db_num}'] = {
                'path': str(rel_path),
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

def create_database_page(db_id, db_info, css_content):
    """Create individual database page that loads deliverable HTML"""
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
        /* Back to dashboard link */
        .back-link {{
            position: fixed;
            top: var(--spacing-md);
            left: var(--spacing-md);
            z-index: 1000;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: var(--spacing-sm) var(--spacing-md);
            text-decoration: none;
            color: var(--text-primary);
            font-size: 0.875rem;
            transition: all 0.2s ease;
        }}
        
        .back-link:hover {{
            background: var(--bg-secondary);
            border-color: var(--bg-dark);
        }}
    </style>
</head>
<body>
    <a href="index.html" class="back-link">← Back to Dashboard</a>
    <iframe src="../{db_info['path']}" style="width: 100%; height: 100vh; border: none; margin-left: 0;"></iframe>
    <script>
        // Adjust iframe to account for sidebar
        document.addEventListener('DOMContentLoaded', function() {{
            const iframe = document.querySelector('iframe');
            iframe.style.marginLeft = '280px';
            iframe.style.width = 'calc(100% - 280px)';
        }});
    </script>
</body>
</html>
"""
    
    return page_html

def main():
    """Create website structure"""
    root_dir = Path(__file__).parent.parent
    website_dir = root_dir / 'website'
    website_dir.mkdir(exist_ok=True)
    
    print("📖 Extracting CSS from db-6 documentation...")
    css_content = extract_css_from_db6()
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
        page_html = create_database_page(db_id, db_info, css_content)
        (website_dir / f'{db_id}.html').write_text(page_html, encoding='utf-8')
        print(f"✅ Created {db_id}.html")
    
    print(f"\n✅ Website created successfully in {website_dir}")
    return True

if __name__ == '__main__':
    main()
