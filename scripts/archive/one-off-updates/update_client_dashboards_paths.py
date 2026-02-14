#!/usr/bin/env python3
"""
Update Streamlit dashboards in client/db to properly detect client structure
"""

import re
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'

DATABASES = [f'db-{i}' for i in range(6, 16)]

DB_TO_DELIVERABLE = {
    'db-6': 'db6-weather-consulting-insurance',
    'db-7': 'db7-maritime-shipping-intelligence',
    'db-8': 'db8-job-market',
    'db-9': 'db9-shipping-database',
    'db-10': 'db10-shopping-aggregator-database',
    'db-11': 'db11-parking-database',
    'db-12': 'db12-credit-card-and-rewards-optimization-system',
    'db-13': 'db13-ai-benchmark-marketing-database',
    'db-14': 'db14-cloud-instance-cost-database',
    'db-15': 'db15-electricity-cost-and-solar-rebate-database'
}

def update_dashboard_paths(db_name: str):
    """Update dashboard to properly detect client/db structure."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return False
    
    dashboard_file = CLIENT_DB_DIR / db_name / deliverable_folder / f'{db_name}_dashboard.py'
    
    if not dashboard_file.exists():
        return False
    
    content = dashboard_file.read_text(encoding='utf-8')
    
    # Update find_base_directory to prioritize client/db
    content = re.sub(
        r'start_paths = \[(.*?)\]',
        r'''start_paths = [
            Path('/workspace/client/db'),
            Path('/workspace/client/db') / 'db-6',
            Path('/workspace/client/db') / '\'''' + db_name + r'''\',
            Path.cwd(),
            Path('/workspace'),
            Path('/workspace/db'),
            Path('/content'),
            Path('/content/drive/MyDrive'),
            Path.home() / 'Documents' / 'AQ' / 'db',
        ]''',
        content,
        flags=re.DOTALL
    )
    
    # Update find_queries_file to prioritize client structure
    find_queries_pattern = r'def find_queries_file\(\):.*?return.*?queries_file'
    find_queries_replacement = '''def find_queries_file():
    """Find queries.json file recursively, prioritizing client/db structure."""
    search_paths = [
        Path('/workspace/client/db'),
        Path('/workspace/client/db') / 'db-6',
        Path('/workspace/client/db') / '\'''' + db_name + r'''\',
        Path('/workspace/client/db') / '\'''' + db_name + r'''\' / '\'''' + deliverable_folder + r'''\',
        Path('/workspace/db'),
        Path('/workspace'),
        Path('/content/drive/MyDrive/db'),
        Path('/content/db'),
        Path('/content'),
        Path.cwd(),
        Path.home() / 'Documents' / 'AQ' / 'db',
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Look for queries.json recursively
        queries_file = find_file_recursively(search_path, 'queries.json')
        if queries_file:
            # Check if it's for the right database
            db_dir_candidate = queries_file.parent.parent
            if db_dir_candidate.name == '\'''' + db_name + r'''\' or db_dir_candidate.parent.name == '\'''' + db_name + r'''\':
                return queries_file
    
    # Fallback: try direct path
    fallback_paths = [
        Path('/workspace/client/db') / '\'''' + db_name + r'''\' / 'queries' / 'queries.json',
        Path('/workspace/client/db') / '\'''' + db_name + r'''\' / '\'''' + deliverable_folder + r'''\' / 'queries' / 'queries.json',
        Path('/workspace/db') / '\'''' + db_name + r'''\' / 'queries' / 'queries.json',
    ]
    
    for fallback_path in fallback_paths:
        if fallback_path.exists():
            return fallback_path
    
    return Path('/workspace/client/db') / '\'''' + db_name + r'''\' / 'queries' / 'queries.json''''
    
    content = re.sub(find_queries_pattern, find_queries_replacement, content, flags=re.DOTALL)
    
    # Update detect_database_directory Docker paths
    docker_paths_start = content.find("if ENV_TYPE == 'docker':")
    if docker_paths_start != -1:
        docker_search_start = content.find('search_paths = [', docker_paths_start)
        if docker_search_start != -1:
            docker_search_end = content.find(']', docker_search_start)
            if docker_search_end != -1:
                new_docker_paths = f'''search_paths = [
            Path('/workspace/client/db'),
            Path('/workspace/client/db') / '{db_name}',
            Path('/workspace/db'),
            Path('/workspace'),
        ]'''
                content = content[:docker_search_start] + new_docker_paths + content[docker_search_end + 1:]
    
    # Update local paths
    local_paths_start = content.find("else:  # local")
    if local_paths_start != -1:
        local_search_start = content.find('search_paths = [', local_paths_start)
        if local_search_start != -1:
            local_search_end = content.find(']', local_search_start)
            if local_search_end != -1:
                new_local_paths = f'''search_paths = [
            BASE_DIR / 'client' / 'db',
            BASE_DIR / 'client' / 'db' / '{db_name}',
            BASE_DIR / 'client' / 'db' / '{db_name}' / '{deliverable_folder}',
            BASE_DIR,
            Path.cwd(),
            Path.home() / 'Documents' / 'AQ' / 'db',
        ]'''
                content = content[:local_search_start] + new_local_paths + content[local_search_end + 1:]
    
    dashboard_file.write_text(content, encoding='utf-8')
    print(f"✅ Updated dashboard paths: {dashboard_file.relative_to(BASE_DIR)}")
    return True

def main():
    """Update all client dashboards."""
    print("="*80)
    print("UPDATING CLIENT DASHBOARD PATHS")
    print("="*80)
    
    for db_name in DATABASES:
        update_dashboard_paths(db_name)
    
    print(f"\n{'='*80}")
    print("Dashboard path updates complete")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
