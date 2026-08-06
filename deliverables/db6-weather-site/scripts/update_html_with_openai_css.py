#!/usr/bin/env python3
"""
Update HTML files with OpenAI brand CSS from db-6 golden solution
"""

import re
from pathlib import Path

def extract_css_from_db6():
    """Extract complete CSS from db-6 HTML file"""
    db6_html_path = Path('db-6/deliverable/db6-weather-consulting-insurance/db-6_documentation.html')
    db6_html = db6_html_path.read_text()
    
    # Extract CSS between <style> and </style>
    css_match = re.search(r'<style>(.*?)</style>', db6_html, re.DOTALL)
    if not css_match:
        raise ValueError("CSS not found in db-6 HTML file")
    
    return css_match.group(1)

def extract_scripts_from_db6():
    """Extract JavaScript from db-6 HTML file"""
    db6_html_path = Path('db-6/deliverable/db6-weather-consulting-insurance/db-6_documentation.html')
    db6_html = db6_html_path.read_text()
    
    # Extract scripts (all <script> blocks before </body>)
    scripts_match = re.search(r'(<script>.*?</script>)', db6_html, re.DOTALL)
    scripts = []
    
    # Find all script blocks
    for match in re.finditer(r'<script>(.*?)</script>', db6_html, re.DOTALL):
        script_content = match.group(1)
        # Skip Prism.js scripts (they're in head)
        if 'Prism' not in script_content and 'prism' not in script_content.lower():
            scripts.append(f'<script>{script_content}</script>')
    
    return '\n    '.join(scripts)

def update_html_file(html_path: Path, db_num: int, db_name: str):
    """Update HTML file with OpenAI brand CSS from db-6"""
    print(f"\n📄 Processing db-{db_num}: {html_path}")
    
    if not html_path.exists():
        print(f"⚠️  HTML file not found: {html_path}")
        return False
    
    html_content = html_path.read_text()
    
    # Extract CSS from db-6
    db6_css = extract_css_from_db6()
    db6_scripts = extract_scripts_from_db6()
    
    # Check if anti-robot tags exist
    has_anti_robot = 'name="robots"' in html_content
    has_analytics = 'va.vercel-scripts.com' in html_content or '@vercel/analytics' in html_content
    
    # Update title
    title_pattern = r'<title>.*?</title>'
    new_title = f'<title>{db_name} - Documentation</title>'
    html_content = re.sub(title_pattern, new_title, html_content)
    
    # Add anti-robot tags if missing (after viewport)
    if not has_anti_robot:
        viewport_pattern = r'(<meta name="viewport"[^>]*>)'
        anti_robot_tags = '''    <!-- Anti-robot / crawl protection -->
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="bingbot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">'''
        
        if re.search(viewport_pattern, html_content):
            html_content = re.sub(
                viewport_pattern,
                r'\1\n' + anti_robot_tags,
                html_content,
                count=1
            )
        else:
            # Add after charset if viewport not found
            charset_pattern = r'(<meta charset="UTF-8">)'
            if re.search(charset_pattern, html_content):
                html_content = re.sub(
                    charset_pattern,
                    r'\1\n' + anti_robot_tags,
                    html_content,
                    count=1
                )
    
    # Replace CSS (between <style> and </style>)
    css_pattern = r'<style>.*?</style>'
    new_css = f'<style>{db6_css}</style>'
    html_content = re.sub(css_pattern, new_css, html_content, flags=re.DOTALL, count=1)
    
    # Add Analytics if missing (before closing body tag)
    if not has_analytics:
        body_close_pattern = r'(</body>)'
        analytics_script = '''    <!-- Vercel Analytics -->
    <script>
        // For Next.js: import { Analytics } from "@vercel/analytics/next"
        // For static HTML: Use script tag approach
        (function() {
            var script = document.createElement('script');
            script.src = 'https://va.vercel-scripts.com/v1/script.js';
            script.defer = true;
            script.setAttribute('data-api', '/api/event');
            document.head.appendChild(script);
        })();
    </script>'''
        
        if re.search(body_close_pattern, html_content):
            html_content = re.sub(
                body_close_pattern,
                analytics_script + r'\n\1',
                html_content,
                count=1
            )
    
    # Add JavaScript from db-6 if missing (before closing body tag)
    if db6_scripts and '</script>' not in html_content[-2000:]:  # Check if scripts already exist
        body_close_pattern = r'(</body>)'
        if re.search(body_close_pattern, html_content):
            html_content = re.sub(
                body_close_pattern,
                db6_scripts + r'\n\1',
                html_content,
                count=1
            )
    
    # Write updated HTML
    html_path.write_text(html_content)
    print(f"✅ Updated: {html_path}")
    return True

def main():
    """Update HTML files for db-7, db-8, db-9, db-10, db-11"""
    root_dir = Path(__file__).parent.parent
    
    databases = [
        (7, 'Maritime Shipping Intelligence Database', 'db7-maritime-shipping-intelligence', 'db-7_documentation.html'),
        (8, 'Job Market Intelligence Database', 'db8-job-market-intelligence', 'db-8_documentation.html'),
        (9, 'Shipping Intelligence Database', 'db9-shipping-intelligence', 'db-9_documentation.html'),
        (10, 'Marketing Intelligence Database', 'db10-marketing-intelligence', 'db-10_documentation.html'),
        (11, 'Parking Intelligence Database', 'db11-parking-intelligence', 'db-11_documentation.html'),
    ]
    
    print("🎨 Updating HTML files with OpenAI brand CSS from db-6...")
    
    for db_num, db_name, folder_name, html_filename in databases:
        html_file = root_dir / f'db-{db_num}' / 'deliverable' / folder_name / html_filename
        update_html_file(html_file, db_num, db_name)
    
    print("\n✅ All HTML files updated with OpenAI brand CSS!")

if __name__ == '__main__':
    main()
