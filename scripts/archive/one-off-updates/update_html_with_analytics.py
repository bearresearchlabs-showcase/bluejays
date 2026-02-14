#!/usr/bin/env python3
"""
Update HTML files with anti-robot meta tags and Vercel Analytics
"""

import re
from pathlib import Path

def update_html_file(html_file: Path):
    """Update HTML file with anti-robot tags and Analytics"""
    if not html_file.exists():
        print(f"⚠️  HTML file not found: {html_file}")
        return False
    
    content = html_file.read_text()
    
    # Check if anti-robot tags already exist
    has_anti_robot = 'name="robots"' in content
    
    # Check if Analytics already exists
    has_analytics = 'va.vercel-scripts.com' in content or '@vercel/analytics' in content
    
    updated = False
    
    # Add anti-robot meta tags after viewport meta tag
    if not has_anti_robot:
        viewport_pattern = r'(<meta name="viewport"[^>]*>)'
        anti_robot_tags = '''    <!-- Anti-robot / crawl protection -->
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="bingbot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">'''
        
        if re.search(viewport_pattern, content):
            content = re.sub(
                viewport_pattern,
                r'\1\n' + anti_robot_tags,
                content,
                count=1
            )
            updated = True
        else:
            # Add after charset if viewport not found
            charset_pattern = r'(<meta charset="UTF-8">)'
            if re.search(charset_pattern, content):
                content = re.sub(
                    charset_pattern,
                    r'\1\n' + anti_robot_tags,
                    content,
                    count=1
                )
                updated = True
    
    # Add Vercel Analytics before closing body tag
    if not has_analytics:
        # Look for closing body tag
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
        
        if re.search(body_close_pattern, content):
            content = re.sub(
                body_close_pattern,
                analytics_script + r'\n\1',
                content,
                count=1
            )
            updated = True
    
    if updated:
        html_file.write_text(content)
        print(f"✅ Updated: {html_file}")
        return True
    else:
        print(f"ℹ️  Already up-to-date: {html_file}")
        return False

def main():
    """Update HTML files for db-7, db-8, db-9, db-11"""
    root_dir = Path(__file__).parent.parent
    
    databases = [
        (7, 'db7-maritime-shipping-intelligence', 'db-7_documentation.html'),
        (8, 'db8-job-market-intelligence', 'db-8_documentation.html'),
        (9, 'db9-shipping-intelligence', 'db-9_documentation.html'),
        (11, 'db11-parking-intelligence', 'db-11_documentation.html'),
    ]
    
    for db_num, folder_name, html_filename in databases:
        html_file = root_dir / f'db-{db_num}' / 'deliverable' / folder_name / html_filename
        print(f"\n📄 Processing db-{db_num}...")
        update_html_file(html_file)

if __name__ == '__main__':
    main()
