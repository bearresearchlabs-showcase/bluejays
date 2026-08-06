#!/usr/bin/env python3
"""
Update queries.md files with Execution Test Results sections
Update queries.json files with execution metadata
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
DATABASES = [f'db-{i}' for i in range(6, 16)]

def update_queries_md(db_name: str):
    """Update queries.md with test results section."""
    db_dir = BASE_DIR / db_name
    queries_md = db_dir / 'queries' / 'queries.md'
    report_json = db_dir / 'results' / f'{db_name.replace("db-", "db")}_comprehensive_report.json'
    
    if not queries_md.exists():
        print(f"⚠️  {db_name}: queries.md not found")
        return False
    
    if not report_json.exists():
        print(f"⚠️  {db_name}: comprehensive report not found")
        return False
    
    # Load test results
    with open(report_json) as f:
        report = json.load(f)
    
    # Load queries.md
    content = queries_md.read_text(encoding='utf-8')
    
    # Create test results section
    test_timestamp = report.get('test_timestamp', datetime.now().isoformat())
    total_queries = report.get('total_queries', 30)
    passed = report.get('passed', 0)
    failed = report.get('failed', 0)
    success_rate = report.get('success_rate', 0)
    
    test_results_section = f"""## Execution Test Results

**Last Tested:** {test_timestamp}

**Test Summary:**
- Total Queries: {total_queries}
- Passed: {passed}
- Failed: {failed}
- Success Rate: {success_rate:.1f}%

**Query Execution Status:**
"""
    
    # Add individual query status
    queries_data = report.get('queries', [])
    for q in queries_data:
        query_num = q.get('number')
        success = q.get('success', False)
        exec_time = q.get('execution_time', 0)
        row_count = q.get('row_count', 0)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        test_results_section += f"- Query {query_num}: {status} ({exec_time:.3f}s, {row_count} rows)\n"
    
    test_results_section += "\n---\n\n"
    
    # Remove existing test results section if present
    pattern = r'## Execution Test Results.*?(?=\n---\n\n|\n## |\Z)'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Prepend test results section
    content = test_results_section + content
    
    # Write back
    queries_md.write_text(content, encoding='utf-8')
    print(f"✅ Updated {db_name}/queries/queries.md")
    return True

def update_queries_json(db_name: str):
    """Update queries.json with execution metadata."""
    db_dir = BASE_DIR / db_name
    queries_json = db_dir / 'queries' / 'queries.json'
    report_json = db_dir / 'results' / f'{db_name.replace("db-", "db")}_comprehensive_report.json'
    
    if not queries_json.exists():
        print(f"⚠️  {db_name}: queries.json not found")
        return False
    
    if not report_json.exists():
        print(f"⚠️  {db_name}: comprehensive report not found")
        return False
    
    # Load both files
    with open(queries_json) as f:
        queries_data = json.load(f)
    
    with open(report_json) as f:
        report = json.load(f)
    
    # Add execution_test_results at top level
    queries_data['execution_test_results'] = {
        'test_timestamp': report.get('test_timestamp'),
        'total_queries': report.get('total_queries'),
        'passed': report.get('passed'),
        'failed': report.get('failed'),
        'success_rate': report.get('success_rate'),
        'average_execution_time': report.get('average_execution_time'),
        'total_execution_time': report.get('total_execution_time')
    }
    
    # Update each query with execution metadata
    queries = queries_data.get('queries', [])
    report_queries = {q['number']: q for q in report.get('queries', [])}
    
    for query in queries:
        query_num = query.get('number')
        if query_num in report_queries:
            report_query = report_queries[query_num]
            query['execution'] = {
                'success': report_query.get('success'),
                'execution_time_seconds': report_query.get('execution_time'),
                'row_count': report_query.get('row_count'),
                'column_count': report_query.get('column_count'),
                'tested_at': report.get('test_timestamp')
            }
            if not report_query.get('success'):
                query['execution']['error'] = report_query.get('error')
    
    # Write back
    with open(queries_json, 'w') as f:
        json.dump(queries_data, f, indent=2, default=str)
    
    print(f"✅ Updated {db_name}/queries/queries.json")
    return True

def main():
    """Update all databases."""
    print("="*80)
    print("UPDATING DOCUMENTATION WITH TEST RESULTS")
    print("="*80)
    
    for db_name in DATABASES:
        print(f"\nProcessing {db_name}...")
        update_queries_md(db_name)
        update_queries_json(db_name)
    
    print(f"\n{'='*80}")
    print("DOCUMENTATION UPDATE COMPLETE")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
