#!/usr/bin/env python3
"""
Synchronize test results and documentation updates to client/db
Preserves client-specific customizations
"""

import json
import re
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DIR = BASE_DIR / 'client'
DATABASES = [f'db-{i}' for i in range(6, 16)]

# Database to deliverable folder mapping
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

sync_report = {
    'sync_timestamp': datetime.now().isoformat(),
    'files_updated': [],
    'files_preserved': [],
    'errors': []
}

def sync_test_results():
    """Sync comprehensive_test_results.json to client/."""
    root_file = BASE_DIR / 'comprehensive_test_results.json'
    client_file = CLIENT_DIR / 'comprehensive_test_results.json'
    
    if root_file.exists():
        shutil.copy2(root_file, client_file)
        sync_report['files_updated'].append(str(client_file.relative_to(BASE_DIR)))
        print(f"✅ Synced comprehensive_test_results.json")
        return True
    return False

def update_client_md_test_results(db_name: str):
    """Update only test results section in client .md file."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return False
    
    client_md = CLIENT_DIR / 'db' / db_name / deliverable_folder / f'{db_name}.md'
    root_queries_md = BASE_DIR / db_name / 'queries' / 'queries.md'
    
    if not client_md.exists():
        sync_report['errors'].append(f"{client_md} not found")
        return False
    
    if not root_queries_md.exists():
        sync_report['errors'].append(f"{root_queries_md} not found")
        return False
    
    # Extract test results section from root queries.md
    root_content = root_queries_md.read_text(encoding='utf-8')
    test_results_match = re.search(r'## Execution Test Results.*?(?=\n---\n\n|\n## |\Z)', root_content, re.DOTALL)
    
    if not test_results_match:
        return False
    
    test_results_section = test_results_match.group(0)
    
    # Load client .md file
    client_content = client_md.read_text(encoding='utf-8')
    
    # Remove existing test results section if present
    pattern = r'## Execution Test Results.*?(?=\n---\n\n|\n## |\Z)'
    client_content = re.sub(pattern, '', client_content, flags=re.DOTALL)
    
    # Find insertion point (after backstory, before Table of Contents or first ##)
    # Insert after backstory section if it exists
    backstory_match = re.search(r'(---\n\n)', client_content)
    if backstory_match:
        insert_pos = backstory_match.end()
        client_content = client_content[:insert_pos] + '\n' + test_results_section + '\n' + client_content[insert_pos:]
    else:
        # Insert at the beginning
        client_content = test_results_section + '\n\n' + client_content
    
    # Write back
    client_md.write_text(client_content, encoding='utf-8')
    sync_report['files_updated'].append(str(client_md.relative_to(BASE_DIR)))
    print(f"✅ Updated {client_md.name}")
    return True

def update_client_json_deliverable(db_name: str):
    """Update client deliverable JSON with execution metadata."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return False
    
    client_json = CLIENT_DIR / 'db' / db_name / deliverable_folder / f'{db_name}_deliverable.json'
    root_queries_json = BASE_DIR / db_name / 'queries' / 'queries.json'
    
    if not client_json.exists():
        sync_report['errors'].append(f"{client_json} not found")
        return False
    
    if not root_queries_json.exists():
        return False
    
    # Load both files
    with open(client_json) as f:
        client_data = json.load(f)
    
    with open(root_queries_json) as f:
        root_data = json.load(f)
    
    # Add execution_test_results if present in root
    if 'execution_test_results' in root_data:
        client_data['execution_test_results'] = root_data['execution_test_results']
    
    # Update query-level execution metadata
    if 'queries' in client_data and 'queries' in root_data:
        root_queries = {q['number']: q for q in root_data['queries']}
        for query in client_data['queries']:
            query_num = query.get('number')
            if query_num in root_queries and 'execution' in root_queries[query_num]:
                query['execution'] = root_queries[query_num]['execution']
    
    # Write back
    with open(client_json, 'w') as f:
        json.dump(client_data, f, indent=2, default=str)
    
    sync_report['files_updated'].append(str(client_json.relative_to(BASE_DIR)))
    print(f"✅ Updated {client_json.name}")
    return True

def check_and_sync_schema_data(db_name: str):
    """Check and sync schema/data files if changed."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return
    
    client_data_dir = CLIENT_DIR / 'db' / db_name / deliverable_folder / 'data'
    root_data_dir = BASE_DIR / db_name / 'data'
    
    if not client_data_dir.exists():
        return
    
    # Check schema.sql
    root_schema = root_data_dir / 'schema.sql'
    client_schema = client_data_dir / 'schema.sql'
    
    if root_schema.exists() and client_schema.exists():
        root_mtime = root_schema.stat().st_mtime
        client_mtime = client_schema.stat().st_mtime
        
        if root_mtime > client_mtime:
            shutil.copy2(root_schema, client_schema)
            sync_report['files_updated'].append(str(client_schema.relative_to(BASE_DIR)))
            print(f"✅ Synced schema.sql for {db_name}")
        else:
            sync_report['files_preserved'].append(str(client_schema.relative_to(BASE_DIR)))
    
    # Check data.sql
    root_data = root_data_dir / 'data.sql'
    client_data = client_data_dir / 'data.sql'
    
    if root_data.exists() and client_data.exists():
        root_mtime = root_data.stat().st_mtime
        client_mtime = client_data.stat().st_mtime
        
        if root_mtime > client_mtime:
            shutil.copy2(root_data, client_data)
            sync_report['files_updated'].append(str(client_data.relative_to(BASE_DIR)))
            print(f"✅ Synced data.sql for {db_name}")
        else:
            sync_report['files_preserved'].append(str(client_data.relative_to(BASE_DIR)))

def preserve_client_customizations(db_name: str):
    """Document preserved client customizations."""
    deliverable_folder = DB_TO_DELIVERABLE.get(db_name)
    if not deliverable_folder:
        return
    
    client_dir = CLIENT_DIR / 'db' / db_name / deliverable_folder
    
    # Check for client-specific files
    client_files = ['vercel.json', '.gitignore', '*.html']
    for pattern in client_files:
        for file_path in client_dir.glob(pattern):
            sync_report['files_preserved'].append(str(file_path.relative_to(BASE_DIR)))

def main():
    """Sync all databases to client/db."""
    print("="*80)
    print("SYNCHRONIZING TO CLIENT/DB")
    print("="*80)
    
    # Sync test results
    sync_test_results()
    
    # Update each database
    for db_name in DATABASES:
        print(f"\nProcessing {db_name}...")
        update_client_md_test_results(db_name)
        update_client_json_deliverable(db_name)
        check_and_sync_schema_data(db_name)
        preserve_client_customizations(db_name)
    
    # Generate sync report
    report_file = CLIENT_DIR / 'SYNC_REPORT.md'
    report_content = f"""# Synchronization Report

**Sync Timestamp:** {sync_report['sync_timestamp']}

## Summary

- **Files Updated:** {len(sync_report['files_updated'])}
- **Files Preserved:** {len(sync_report['files_preserved'])}
- **Errors:** {len(sync_report['errors'])}

## Files Updated

"""
    
    for file_path in sync_report['files_updated']:
        report_content += f"- `{file_path}`\n"
    
    report_content += "\n## Files Preserved (Client Customizations)\n\n"
    for file_path in sync_report['files_preserved']:
        report_content += f"- `{file_path}`\n"
    
    if sync_report['errors']:
        report_content += "\n## Errors\n\n"
        for error in sync_report['errors']:
            report_content += f"- {error}\n"
    
    report_file.write_text(report_content, encoding='utf-8')
    print(f"\n✅ Sync report saved: {report_file}")
    
    print(f"\n{'='*80}")
    print("SYNCHRONIZATION COMPLETE")
    print(f"{'='*80}")
    print(f"Updated: {len(sync_report['files_updated'])} files")
    print(f"Preserved: {len(sync_report['files_preserved'])} files")

if __name__ == '__main__':
    main()
