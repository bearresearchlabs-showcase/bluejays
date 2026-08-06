#!/usr/bin/env python3
"""
Create a single HTML file with all databases (DB-6 to DB-15) and unified navigation
"""

import re
from pathlib import Path

def extract_css_from_db6():
    """Extract CSS from db-6_documentation.html"""
    db6_file = Path(__file__).parent.parent / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    
    if not db6_file.exists():
        return None
    
    content = db6_file.read_text(encoding='utf-8')
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    return style_match.group(1) if style_match else None

def extract_scripts_from_db6():
    """Extract JavaScript from db-6_documentation.html and update for multi-database"""
    db6_file = Path(__file__).parent.parent / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    
    if not db6_file.exists():
        return None
    
    content = db6_file.read_text(encoding='utf-8')
    scripts = []
    script_pattern = r'(<script[^>]*>.*?</script>)'
    for match in re.finditer(script_pattern, content, re.DOTALL):
        script_content = match.group(1)
        # Update JavaScript to work with prefixed IDs
        # Replace references to non-prefixed IDs with db6- prefix (for default expansion)
        script_content = re.sub(r'getElementById\([\'"]overview-content[\'"]\)', 'getElementById(\'db6-overview-content\')', script_content)
        script_content = re.sub(r'getElementById\([\'"]schema-content[\'"]\)', 'getElementById(\'db6-schema-content\')', script_content)
        script_content = re.sub(r'getElementById\([\'"]queries-content[\'"]\)', 'getElementById(\'db6-queries-content\')', script_content)
        script_content = re.sub(r'querySelector\([\'"]\[data-section="overview"\]\'\)', 'querySelector(\'[data-section="db6-overview"]\')', script_content)
        script_content = re.sub(r'querySelector\([\'"]\[data-section="schema"\]\'\)', 'querySelector(\'[data-section="db6-schema"]\')', script_content)
        script_content = re.sub(r'querySelector\([\'"]\[data-section="queries"\]\'\)', 'querySelector(\'[data-section="db6-queries"]\')', script_content)
        script_content = re.sub(r'getElementById\([\'"]db6-content[\'"]\)', 'getElementById(\'db6-content\')', script_content)
        script_content = re.sub(r'querySelector\([\'"]\[data-section="db6"\]\'\)', 'querySelector(\'[data-section="db6"]\')', script_content)
        # Fix any double document references (multiple patterns)
        # Replace document.document. with document. (handle escaped and unescaped)
        script_content = re.sub(r'document\.document\.', 'document.', script_content)
        script_content = re.sub(r'document\.document\.', 'document.', script_content)  # Run twice to catch nested cases
        script_content = re.sub(r'\(document\.document\)', '(document)', script_content)
        # Also fix cases where it might be in a different format
        script_content = script_content.replace('document.document.', 'document.')
        script_content = script_content.replace('document.document', 'document')
        # Update section detection to handle prefixed IDs
        # First fix any document.document issues before doing replacements
        script_content = re.sub(r'document\.document\.', 'document.', script_content)
        script_content = script_content.replace('document.document.', 'document.')
        script_content = script_content.replace('document.document', 'document')
        
        # Now do the replacements
        script_content = re.sub(r'getElementById\([\'"]schema[\'"]\)', 'document.querySelector(\'[id$="-schema"]\')', script_content)
        script_content = re.sub(r'getElementById\([\'"]queries[\'"]\)', 'document.querySelector(\'[id$="-queries"]\')', script_content)
        
        # Fix again after replacements in case they created new issues
        script_content = re.sub(r'document\.document\.', 'document.', script_content)
        script_content = script_content.replace('document.document.', 'document.')
        scripts.append(script_content)
    return '\n'.join(scripts) if scripts else ''

def extract_main_content(html_file):
    """Extract main content from deliverable HTML"""
    if not html_file.exists():
        return None
    
    try:
        content = html_file.read_text(encoding='utf-8')
        # Try different patterns for main content
        main_match = re.search(r'(<main class="main-content">.*?</main>)', content, re.DOTALL)
        if main_match:
            return main_match.group(1)
        
        # Try without class
        main_match = re.search(r'(<main>.*?</main>)', content, re.DOTALL)
        if main_match:
            return main_match.group(1)
        
        # Try finding content between body tags (excluding nav/sidebar)
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
        if body_match:
            body_content = body_match.group(1)
            # Remove sidebar/nav
            body_content = re.sub(r'<nav[^>]*>.*?</nav>', '', body_content, flags=re.DOTALL)
            # Remove scripts
            body_content = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL)
            if body_content.strip():
                return f'<main class="main-content">{body_content.strip()}</main>'
    except Exception as e:
        print(f"    Error reading {html_file}: {e}")
    
    return None

def get_database_info():
    """Get deliverable paths for each database"""
    databases = {}
    root_dir = Path(__file__).parent.parent
    
    for db_num in range(6, 16):
        db_dir = root_dir / f'db-{db_num}' / 'deliverable'
        if not db_dir.exists():
            continue
        
        doc_files = list(db_dir.rglob('*documentation.html'))
        if doc_files:
            databases[f'db-{db_num}'] = {
                'path': doc_files[0],
                'name': f'DB-{db_num}',
                'num': db_num
            }
    
    return databases

def create_navigation_sidebar(databases):
    """Create unified navigation sidebar for all databases"""
    sidebar = """    <nav class="sidebar">
        <div class="sidebar-header">
            <h1>Database Documentation</h1>
            <p>All Databases</p>
        </div>
"""
    
    # Sort databases by number
    sorted_dbs = sorted(databases.items(), key=lambda x: x[1]['num'])
    
    for db_id, db_info in sorted_dbs:
        db_num = db_info['num']
        sidebar += f"""
        <div class="nav-section">
            <div class="nav-section-title nav-accordion-header" data-section="db{db_num}">
                <span>{db_info['name']}</span>
                <span class="accordion-icon">▼</span>
            </div>
            <div class="nav-accordion-content" id="db{db_num}-content">
                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="db{db_num}-overview">
                        <span>Overview</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="db{db_num}-overview-content">
                        <a href="#db{db_num}-overview" class="nav-link">Overview</a>
                        <a href="#db{db_num}-schema" class="nav-link">Schema</a>
                        <a href="#db{db_num}-queries" class="nav-link">Queries</a>
                    </div>
                </div>
                
                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="db{db_num}-schema">
                        <span>Schema</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="db{db_num}-schema-content">
                        <div class="nav-placeholder">
                            <p>Tables listed in content</p>
                        </div>
                    </div>
                </div>
                
                <div class="nav-subsection">
                    <div class="nav-subsection-title nav-accordion-header" data-section="db{db_num}-queries">
                        <span>Queries</span>
                        <span class="accordion-icon">▼</span>
                    </div>
                    <div class="nav-accordion-content" id="db{db_num}-queries-content">
"""
        # Add query links 1-30
        for q_num in range(1, 31):
            sidebar += f'                        <a href="#db{db_num}-query-{q_num}" class="nav-link">Query {q_num}</a>\n'
        
        sidebar += """                    </div>
                </div>
            </div>
        </div>
"""
    
    sidebar += "    </nav>"
    return sidebar

def update_content_ids(content, db_prefix):
    """Update all IDs in content to use database prefix"""
    db_num = db_prefix.replace('db', '')
    
    # Update header IDs
    content = re.sub(r'id="overview"', f'id="{db_prefix}-overview"', content)
    content = re.sub(r'id="schema"', f'id="{db_prefix}-schema"', content)
    content = re.sub(r'id="queries"', f'id="{db_prefix}-queries"', content)
    
    # Update table IDs
    content = re.sub(r'id="table-([^"]+)"', rf'id="{db_prefix}-table-\1"', content)
    
    # Update query IDs
    content = re.sub(r'id="query-(\d+)"', rf'id="{db_prefix}-query-\1"', content)
    content = re.sub(r'id="Query (\d+):', rf'id="{db_prefix}-query-\1:', content)
    
    # Update links
    content = re.sub(r'href="#overview"', f'href="#{db_prefix}-overview"', content)
    content = re.sub(r'href="#schema"', f'href="#{db_prefix}-schema"', content)
    content = re.sub(r'href="#queries"', f'href="#{db_prefix}-queries"', content)
    content = re.sub(r'href="#table-([^"]+)"', rf'href="#{db_prefix}-table-\1"', content)
    content = re.sub(r'href="#query-(\d+)"', rf'href="#{db_prefix}-query-\1"', content)
    
    # Update database references
    content = re.sub(r'Database ID:</strong>\s*db-\d+', f'Database ID:</strong> db-{db_num}', content)
    content = re.sub(r'database db-\d+', f'database db-{db_num}', content)
    
    return content

def create_single_page_website():
    """Create single HTML file with all databases"""
    root_dir = Path(__file__).parent.parent
    website_dir = root_dir / 'website'
    website_dir.mkdir(exist_ok=True)
    
    print("📖 Extracting CSS and scripts from db-6 documentation...")
    css_content = extract_css_from_db6()
    scripts_content = extract_scripts_from_db6()
    
    if not css_content:
        print("❌ Failed to extract CSS")
        return False
    
    print("📊 Getting database information...")
    databases = get_database_info()
    print(f"✅ Found {len(databases)} databases")
    
    print("🧭 Creating navigation sidebar...")
    sidebar = create_navigation_sidebar(databases)
    
    print("📄 Extracting and combining content from all databases...")
    all_main_content = '<main class="main-content">\n'
    
    sorted_dbs = sorted(databases.items(), key=lambda x: x[1]['num'])
    for db_id, db_info in sorted_dbs:
        db_prefix = f"db{db_info['num']}"
        print(f"  Processing {db_id}...")
        
        main_content = extract_main_content(db_info['path'])
        if main_content:
            # Remove <main> tags, keep only content
            main_content = re.sub(r'<main class="main-content">', '', main_content)
            main_content = re.sub(r'</main>', '', main_content)
            
            # Remove nested <div class="main-content"> tags (they shouldn't be in content)
            main_content = re.sub(r'<div class="main-content">', '', main_content)
            main_content = re.sub(r'</div>\s*</div>\s*<!--.*?-->', '</div>', main_content)
            
            # Remove any sidebar divs that might have been included
            main_content = re.sub(r'<div class="sidebar">.*?</div>', '', main_content, flags=re.DOTALL)
            
            # Update IDs with database prefix
            main_content = update_content_ids(main_content, db_prefix)
            
            # Add database section header
            all_main_content += f'\n        <!-- {db_prefix.upper()} Content -->\n        <div id="{db_prefix}-section">\n'
            all_main_content += main_content
            all_main_content += '\n        </div>\n'
        else:
            print(f"  ⚠️  No content found for {db_id}")
    
    all_main_content += '\n    </main>'
    
    # Create complete HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Documentation Portal - All Databases</title>
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
{sidebar}
{all_main_content}
{scripts_content}
</body>
</html>
"""
    
    output_file = website_dir / 'index.html'
    print(f"💾 Writing single page website to {output_file}...")
    output_file.write_text(html_content, encoding='utf-8')
    
    file_size = output_file.stat().st_size / (1024 * 1024)  # MB
    print(f"✅ Single page website created successfully!")
    print(f"   File: {output_file}")
    print(f"   Size: {file_size:.2f} MB")
    
    return True

if __name__ == '__main__':
    create_single_page_website()
