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
    
    # Update JSON deliverable references (handle both regular and HTML-encoded quotes)
    content = re.sub(r'db-6_deliverable\.json', f'db-{db_num}_deliverable.json', content)
    # Handle HTML-encoded JSON: &quot;id&quot;: &quot;db-6&quot;
    content = re.sub(r'&quot;id&quot;:\s*&quot;db-6&quot;', f'&quot;id&quot;: &quot;db-{db_num}&quot;', content)
    content = re.sub(r'&quot;id&quot;:\s*&quot;db-\d+&quot;', f'&quot;id&quot;: &quot;db-{db_num}&quot;', content)
    # Handle regular JSON: "id": "db-6"
    content = re.sub(r'"id":\s*"db-6"', f'"id": "db-{db_num}"', content)
    content = re.sub(r'"id":\s*"db-\d+"', f'"id": "db-{db_num}"', content)
    # Update database ID text
    content = re.sub(r'Database ID:</strong>\s*db-\d+', f'Database ID:</strong> db-{db_num}', content)
    # Update database references in descriptions (handle HTML-encoded)
    content = re.sub(r'database db-\d+', f'database db-{db_num}', content)
    content = re.sub(r'database db-6', f'database db-{db_num}', content)
    
    return content

def update_database_info(content, db_num):
    """Update database-specific information in content"""
    # Update database ID references
    content = re.sub(r'Database ID:</strong>\s*db-\d+', f'Database ID:</strong> db-{db_num}', content)
    content = re.sub(r'database db-\d+', f'database db-{db_num}', content)
    
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
    
    # Find main content section
    main_pattern = r'(<main class="main-content">)(.*?)(</main>)'
    main_match = re.search(main_pattern, html_content, re.DOTALL)
    
    if not main_match:
        print("❌ Error: Could not find main content section")
        return False
    
    db6_content = main_match.group(2)
    print(f"📊 Found DB-6 content ({len(db6_content)} characters)")
    
    # Update DB-6's IDs to use db6- prefix
    print(f"🔄 Updating DB-6 IDs to use db6- prefix...")
    db6_content_updated = update_ids_in_content(db6_content, 'db6')
    db6_content_updated = update_database_info(db6_content_updated, 6)
    
    # Update DB-6 navigation links
    print(f"🔄 Updating DB-6 navigation links...")
    html_content = re.sub(
        r'href="#overview" class="nav-link">Overview</a>\s*<a href="#schema" class="nav-link">Schema</a>\s*<a href="#queries" class="nav-link">Queries</a>',
        r'href="#db6-overview" class="nav-link">Overview</a>\n                        <a href="#db6-schema" class="nav-link">Schema</a>\n                        <a href="#db6-queries" class="nav-link">Queries</a>',
        html_content
    )
    
    # Update DB-6 table links in navigation
    html_content = re.sub(
        r'href="#table-([^"]+)" class="nav-link">',
        r'href="#db6-table-\1" class="nav-link">',
        html_content,
        count=15  # 15 tables
    )
    
    # Update DB-6 query links in navigation
    for q_num in range(1, 31):
        html_content = re.sub(
            rf'<a href="#query-{q_num}" class="nav-link">Query {q_num}</a>',
            rf'<a href="#db6-query-{q_num}" class="nav-link">Query {q_num}</a>',
            html_content,
            count=1
        )
    
    # Replace DB-6 content with updated version
    new_main_content = f'{main_match.group(1)}{db6_content_updated}'
    
    # Duplicate content for DB-7 through DB-15
    all_databases_content = db6_content_updated
    
    for db_num in range(7, 16):
        db_prefix = f"db{db_num}"
        print(f"🔄 Creating content for {db_prefix}...")
        
        # Copy DB-6 content and update IDs
        db_content = update_ids_in_content(db6_content, db_prefix)
        db_content = update_database_info(db_content, db_num)
        
        # Add to combined content
        all_databases_content += f'\n\n        <!-- {db_prefix.upper()} Content -->\n        {db_content}'
    
    # Replace main content
    new_main_content = f'{main_match.group(1)}{all_databases_content}{main_match.group(3)}'
    html_content = html_content.replace(main_match.group(0), new_main_content)
    
    # Update JavaScript to handle prefixed IDs
    print(f"🔄 Updating JavaScript for prefixed IDs...")
    
    # Update the active link highlighting to handle all database prefixes
    # Use a more flexible approach - update the selector to match any db prefix
    js_pattern = r'document\.querySelectorAll\([\'"]\.nav-link\[href="#overview"\]'
    js_replacement = r'document.querySelectorAll(\'.nav-link[href^="#db"][href$="-overview"]'
    html_content = re.sub(js_pattern, js_replacement, html_content)
    
    js_pattern2 = r'document\.querySelectorAll\([\'"]\.nav-link\[href="#schema"\]'
    js_replacement2 = r'document.querySelectorAll(\'.nav-link[href^="#db"][href$="-schema"]'
    html_content = re.sub(js_pattern2, js_replacement2, html_content)
    
    # Update section detection to handle prefixed IDs - use raw strings properly
    js_pattern3 = r'if \(currentSection === [\'"]overview[\'"] \|\| currentSection === [\'"][\'"]\)'
    js_replacement3 = r'if (currentSection === \'overview\' || currentSection === \'\' || (currentSection && currentSection.match(/^db\\d+-overview$/)))'
    html_content = re.sub(js_pattern3, js_replacement3, html_content)
    
    js_pattern4 = r'else if \(currentSection === [\'"]schema[\'"] \|\| \(currentSection && currentSection\.startsWith\([\'"]table-[\'"]\)\)\)'
    js_replacement4 = r'else if (currentSection === \'schema\' || (currentSection && (currentSection.startsWith(\'table-\') || currentSection.match(/^db\\d+-schema$/) || currentSection.match(/^db\\d+-table-/))))'
    html_content = re.sub(js_pattern4, js_replacement4, html_content)
    
    # Write updated HTML
    print(f"💾 Writing updated HTML...")
    html_file.write_text(html_content, encoding='utf-8')
    print(f"✅ Populated DB-6 content into DB-7 through DB-15")
    print(f"✅ Updated all IDs to use database prefixes (db6-, db7-, etc.)")
    print(f"✅ Updated JavaScript to handle prefixed IDs")
    return True

if __name__ == '__main__':
    populate_all_databases()
