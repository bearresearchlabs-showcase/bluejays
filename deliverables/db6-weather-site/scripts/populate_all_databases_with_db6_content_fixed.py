#!/usr/bin/env python3
"""
Populate DB-6's content into DB-7 through DB-15 with proper ID prefixes
Updates DB-6's IDs to use db6- prefix and duplicates content for other databases
"""

import re
from pathlib import Path

def update_ids_in_content(content, db_prefix):
    """Update all IDs in content to use database prefix"""
    db_num = db_prefix.replace('db', '')
    
    # Update header IDs
    content = re.sub(r'id="overview"', f'id="{db_prefix}-overview"', content)
    content = re.sub(r'id="schema"', f'id="{db_prefix}-schema"', content)
    content = re.sub(r'id="queries"', f'id="{db_prefix}-queries"', content)
    
    # Update table IDs
    content = re.sub(r'id="table-([^"]+)"', rf'id="{db_prefix}-table-\1"', content)
    
    # Update query IDs - handle various formats
    content = re.sub(r'id="query-(\d+)"', rf'id="{db_prefix}-query-\1"', content)
    content = re.sub(r'id="Query (\d+):', rf'id="{db_prefix}-query-\1:', content)
    content = re.sub(r'\{#query-(\d+)\}', rf'{{#{db_prefix}-query-\1}}', content)
    
    # Update links to use prefixed IDs
    content = re.sub(r'href="#overview"', f'href="#{db_prefix}-overview"', content)
    content = re.sub(r'href="#schema"', f'href="#{db_prefix}-schema"', content)
    content = re.sub(r'href="#queries"', f'href="#{db_prefix}-queries"', content)
    content = re.sub(r'href="#table-([^"]+)"', rf'href="#{db_prefix}-table-\1"', content)
    content = re.sub(r'href="#query-(\d+)"', rf'href="#{db_prefix}-query-\1"', content)
    
    # Update JSON deliverable references
    content = re.sub(r'db-6_deliverable\.json', f'db-{db_num}_deliverable.json', content)
    # Update JSON id field - handle both escaped and unescaped quotes
    content = re.sub(r'&quot;id&quot;:\s*&quot;db-6&quot;', f'&quot;id&quot;: &quot;db-{db_num}&quot;', content)
    content = re.sub(r'"id":\s*"db-6"', f'"id": "db-{db_num}"', content)
    content = re.sub(r'&quot;id&quot;:\s*&quot;db-\d+&quot;', f'&quot;id&quot;: &quot;db-{db_num}&quot;', content)
    content = re.sub(r'"id":\s*"db-\d+"', f'"id": "db-{db_num}"', content)
    
    return content

def update_database_info(content, db_num):
    """Update database-specific information in content"""
    # Update database ID references in text
    content = re.sub(r'Database ID:</strong>\s*db-\d+', f'Database ID:</strong> db-{db_num}', content)
    content = re.sub(r'database db-\d+', f'database db-{db_num}', content)
    content = re.sub(r'for database db-\d+', f'for database db-{db_num}', content)
    
    return content

def populate_all_databases():
    """Populate DB-6's content into DB-7 through DB-15"""
    root_dir = Path(__file__).parent.parent
    
    html_file = root_dir / 'db-6' / 'deliverable' / 'db6-weather-consulting-insurance' / 'db-6_documentation.html'
    if not html_file.exists():
        print(f"❌ Error: {html_file} not found")
        return False
    
    print(f"📖 Reading HTML file...")
    html_content = html_file.read_text(encoding='utf-8')
    
    # Find main content section - use non-greedy match to get only the first main tag
    main_pattern = r'(<main class="main-content">)(.*?)(</main>)'
    main_match = re.search(main_pattern, html_content, re.DOTALL)
    
    if not main_match:
        print("❌ Error: Could not find main content section")
        return False
    
    db6_content = main_match.group(2)
    print(f"📊 Found DB-6 content ({len(db6_content)} characters)")
    
    # Check if content already has db7- prefix (already populated)
    if 'db7-overview' in db6_content:
        print("⚠️  Content already appears to be populated. Extracting original DB-6 content...")
        # Extract only the first section (DB-6's original content)
        # Find where DB-7 content starts
        db7_start = db6_content.find('<!-- DB7 Content -->')
        if db7_start > 0:
            db6_content = db6_content[:db7_start].strip()
            print(f"📊 Extracted original DB-6 content ({len(db6_content)} characters)")
    
    # Update DB-6's IDs to use db6- prefix
    print(f"🔄 Updating DB-6 IDs to use db6- prefix...")
    db6_content_updated = update_ids_in_content(db6_content, 'db6')
    db6_content_updated = update_database_info(db6_content_updated, 6)
    
    # Update DB-6 navigation links in sidebar
    print(f"🔄 Updating DB-6 navigation links...")
    
    # Update Overview/Schema/Queries links for DB-6
    db6_nav_pattern = r'(<div class="nav-accordion-content expanded" id="overview-content">\s*<a href="#overview" class="nav-link">Overview</a>\s*<a href="#schema" class="nav-link">Schema</a>\s*<a href="#queries" class="nav-link">Queries</a>)'
    db6_nav_replacement = r'<div class="nav-accordion-content expanded" id="overview-content">\n                        <a href="#db6-overview" class="nav-link">Overview</a>\n                        <a href="#db6-schema" class="nav-link">Schema</a>\n                        <a href="#db6-queries" class="nav-link">Queries</a>'
    html_content = re.sub(db6_nav_pattern, db6_nav_replacement, html_content)
    
    # Update DB-6 table links in navigation (only in DB-6 section)
    # Find DB-6's schema navigation section and update links
    db6_schema_nav_pattern = r'(<div class="nav-accordion-content" id="schema-content">)(.*?)(</div>\s*</div>\s*</div>\s*<div class="nav-subsection">\s*<div class="nav-subsection-title nav-accordion-header" data-section="queries">)'
    def update_db6_table_links(match):
        nav_content = match.group(2)
        # Update table links
        nav_content = re.sub(r'href="#table-([^"]+)"', r'href="#db6-table-\1"', nav_content)
        return match.group(1) + nav_content + match.group(3)
    
    html_content = re.sub(db6_schema_nav_pattern, update_db6_table_links, html_content, flags=re.DOTALL)
    
    # Update DB-6 query links in navigation (only in DB-6 section)
    # Find the DB-6 queries section specifically
    db6_queries_start = html_content.find('<div class="nav-accordion-content" id="queries-content">')
    db6_queries_end = html_content.find('</div>', db6_queries_start + 200)  # Find first closing div
    # Look for the pattern that ends DB-6's queries section (before DB-7 nav section)
    db7_nav_start = html_content.find('<div class="nav-section">\n            <div class="nav-section-title nav-accordion-header" data-section="db7">')
    if db7_nav_start > 0:
        # Extract DB-6 queries navigation
        db6_queries_nav = html_content[db6_queries_start:db7_nav_start]
        # Update all query links
        for q_num in range(1, 31):
            db6_queries_nav = re.sub(rf'<a href="#query-{q_num}" class="nav-link">Query {q_num}</a>', 
                                    rf'<a href="#db6-query-{q_num}" class="nav-link">Query {q_num}</a>', 
                                    db6_queries_nav)
        # Replace back
        html_content = html_content[:db6_queries_start] + db6_queries_nav + html_content[db7_nav_start:]
    
    # Build combined content: DB-6 updated + DB-7 through DB-15
    all_databases_content = db6_content_updated
    
    for db_num in range(7, 16):
        db_prefix = f"db{db_num}"
        print(f"🔄 Creating content for {db_prefix}...")
        
        # Copy DB-6 updated content and replace db6- prefixes with target prefix
        db_content = db6_content_updated.replace('db6-', f'{db_prefix}-')
        db_content = db_content.replace('db-6', f'db-{db_num}')
        db_content = update_database_info(db_content, db_num)
        
        # Also update JSON references that might still have db6
        db_content = re.sub(r'db-6_deliverable\.json', f'db-{db_num}_deliverable.json', db_content)
        db_content = re.sub(r'&quot;id&quot;: &quot;db-6&quot;', f'&quot;id&quot;: &quot;db-{db_num}&quot;', db_content)
        
        # Add separator comment and content
        all_databases_content += f'\n\n        <!-- {db_prefix.upper()} Content -->\n        {db_content}'
    
    # Replace main content
    new_main_content = f'{main_match.group(1)}{all_databases_content}{main_match.group(3)}'
    html_content = html_content.replace(main_match.group(0), new_main_content)
    
    # Update JavaScript to handle prefixed IDs
    print(f"🔄 Updating JavaScript for prefixed IDs...")
    
    # Update active link highlighting - make it more flexible
    js_pattern = r'document\.querySelectorAll\([\'"][\.]nav-link\[href="#overview"\]'
    js_replacement = r'document.querySelectorAll(\'.nav-link[href^="#db"][href$="-overview"]'
    html_content = re.sub(js_pattern, js_replacement, html_content)
    
    js_pattern2 = r'document\.querySelectorAll\([\'"][\.]nav-link\[href="#schema"\]'
    js_replacement2 = r'document.querySelectorAll(\'.nav-link[href^="#db"][href$="-schema"]'
    html_content = re.sub(js_pattern2, js_replacement2, html_content)
    
    # Write updated HTML
    print(f"💾 Writing updated HTML...")
    html_file.write_text(html_content, encoding='utf-8')
    print(f"✅ Populated DB-6 content into DB-7 through DB-15")
    print(f"✅ Updated all IDs to use database prefixes (db6-, db7-, etc.)")
    print(f"✅ Updated JavaScript to handle prefixed IDs")
    return True

if __name__ == '__main__':
    populate_all_databases()
