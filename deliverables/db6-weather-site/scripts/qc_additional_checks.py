#!/usr/bin/env python3
"""
Additional QC Checks: Code Quality, Documentation Completeness, Compliance
"""

import json
import re
from pathlib import Path
from datetime import datetime
import sys

# Add scripts directory to path for timestamp_utils
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from timestamp_utils import get_est_timestamp

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
DATABASES = [f'db-{i}' for i in range(6, 16)]

def check_code_quality(queries_json_path: Path) -> dict:
    """Check code quality: CTE usage, formatting, complexity, duplicates."""
    with open(queries_json_path) as f:
        data = json.load(f)
    
    queries = data.get('queries', [])
    checks = {
        'cte_usage': {'passed': 0, 'failed': 0, 'details': []},
        'formatting': {'passed': 0, 'failed': 0, 'details': []},
        'complexity': {'passed': 0, 'failed': 0, 'details': []},
        'duplicates': {'passed': 0, 'failed': 0, 'details': []}
    }
    
    sql_hashes = set()
    
    for q in queries:
        query_num = q.get('number')
        sql = q.get('sql', '')
        
        # Check CTE usage
        has_cte = 'WITH ' in sql.upper() or 'WITH RECURSIVE' in sql.upper()
        if has_cte:
            checks['cte_usage']['passed'] += 1
        else:
            checks['cte_usage']['failed'] += 1
            checks['cte_usage']['details'].append(f"Query {query_num} missing CTE")
        
        # Check formatting (basic checks)
        has_proper_indent = sql.count('\n') > 5  # Has multiple lines
        if has_proper_indent:
            checks['formatting']['passed'] += 1
        else:
            checks['formatting']['failed'] += 1
        
        # Check complexity (has joins, aggregations, window functions)
        has_joins = any(keyword in sql.upper() for keyword in ['JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN'])
        has_aggregations = any(keyword in sql.upper() for keyword in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'])
        has_window = any(keyword in sql.upper() for keyword in ['OVER(', 'ROW_NUMBER', 'RANK', 'DENSE_RANK'])
        
        complexity_score = sum([has_joins, has_aggregations, has_window])
        if complexity_score >= 2:
            checks['complexity']['passed'] += 1
        else:
            checks['complexity']['failed'] += 1
            checks['complexity']['details'].append(f"Query {query_num} low complexity (score: {complexity_score})")
        
        # Check for duplicates (simple hash)
        sql_normalized = re.sub(r'\s+', ' ', sql.upper().strip())
        if sql_normalized in sql_hashes:
            checks['duplicates']['failed'] += 1
            checks['duplicates']['details'].append(f"Query {query_num} appears to be duplicate")
        else:
            checks['duplicates']['passed'] += 1
            sql_hashes.add(sql_normalized)
    
    return checks

def check_documentation_completeness(queries_json_path: Path) -> dict:
    """Check documentation completeness."""
    with open(queries_json_path) as f:
        data = json.load(f)
    
    queries = data.get('queries', [])
    checks = {
        'metadata_completeness': {'passed': 0, 'failed': 0, 'details': []},
        'json_structure': {'passed': 0, 'failed': 0, 'details': []}
    }
    
    required_fields = ['number', 'title', 'description', 'use_case', 'business_value', 'purpose', 'complexity', 'expected_output', 'sql']
    
    for q in queries:
        query_num = q.get('number')
        missing_fields = []
        for field in required_fields:
            value = q.get(field)
            if value is None or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(field)
        
        if not missing_fields:
            checks['metadata_completeness']['passed'] += 1
        else:
            checks['metadata_completeness']['failed'] += 1
            checks['metadata_completeness']['details'].append(f"Query {query_num} missing: {', '.join(missing_fields)}")
    
    # Check JSON structure
    if 'queries' in data and 'total_queries' in data and 'extraction_timestamp' in data:
        checks['json_structure']['passed'] = 1
    else:
        checks['json_structure']['failed'] = 1
        checks['json_structure']['details'].append("Missing required top-level fields")
    
    return checks

def check_compliance(queries_json_path: Path, db_name: str) -> dict:
    """Check compliance: query count, timestamp format, JSON status format."""
    with open(queries_json_path) as f:
        data = json.load(f)
    
    queries = data.get('queries', [])
    checks = {
        'query_count': {'passed': 0, 'failed': 0, 'details': []},
        'timestamp_format': {'passed': 0, 'failed': 0, 'details': []},
        'json_status_format': {'passed': 0, 'failed': 0, 'details': []}
    }
    
    # Check query count (exactly 30)
    if len(queries) == 30:
        checks['query_count']['passed'] = 1
    else:
        checks['query_count']['failed'] = 1
        checks['query_count']['details'].append(f"Expected 30 queries, found {len(queries)}")
    
    # Check timestamp format (EST, YYYMMDD-HHMM)
    timestamp = data.get('extraction_timestamp', '')
    if re.match(r'^\d{8}-\d{4}$', timestamp):
        checks['timestamp_format']['passed'] = 1
    else:
        checks['timestamp_format']['failed'] = 1
        checks['timestamp_format']['details'].append(f"Invalid timestamp format: {timestamp}")
    
    # Check JSON status format (check results files if they exist)
    results_dir = BASE_DIR / db_name / 'results'
    if results_dir.exists():
        for result_file in results_dir.glob('*.json'):
            try:
                with open(result_file) as f:
                    result_data = json.load(f)
                    # Check for string status fields (should use Pass: 1/0)
                    json_str = json.dumps(result_data)
                    if '"status":' in json_str or '"Status":' in json_str:
                        if '"Pass":' not in json_str:
                            checks['json_status_format']['failed'] += 1
                            checks['json_status_format']['details'].append(f"{result_file.name} uses string status")
                        else:
                            checks['json_status_format']['passed'] += 1
            except:
                pass
    
    return checks

def run_qc_checks(db_name: str) -> dict:
    """Run all QC checks for a database."""
    db_dir = BASE_DIR / db_name
    queries_json = db_dir / 'queries' / 'queries.json'
    
    if not queries_json.exists():
        return {
            'database': db_name,
            'error': 'queries.json not found'
        }
    
    code_quality = check_code_quality(queries_json)
    documentation = check_documentation_completeness(queries_json)
    compliance = check_compliance(queries_json, db_name)
    
    # Calculate overall pass
    all_passed = (
        code_quality['cte_usage']['failed'] == 0 and
        code_quality['duplicates']['failed'] == 0 and
        documentation['metadata_completeness']['failed'] == 0 and
        compliance['query_count']['failed'] == 0 and
        compliance['timestamp_format']['failed'] == 0
    )
    
    return {
        'database': db_name,
        'check_timestamp': get_est_timestamp(),
        'code_quality': code_quality,
        'documentation_completeness': documentation,
        'compliance': compliance,
        'Pass': 1 if all_passed else 0,
        'notes': [] if all_passed else ['Some QC checks failed - see details']
    }

def main():
    """Run QC checks for all databases."""
    print("="*80)
    print("ADDITIONAL QC CHECKS")
    print("="*80)
    
    all_results = []
    
    for db_name in DATABASES:
        print(f"\nProcessing {db_name}...")
        result = run_qc_checks(db_name)
        all_results.append(result)
        
        status = "✅" if result.get('Pass', 0) == 1 else "⚠️"
        print(f"{status} {db_name}: {'PASS' if result.get('Pass', 0) == 1 else 'WARNINGS'}")
    
    # Save individual reports
    for result in all_results:
        db_name = result['database']
        db_dir = BASE_DIR / db_name
        results_dir = db_dir / 'results'
        results_dir.mkdir(exist_ok=True)
        
        report_file = results_dir / 'qc_additional_checks.json'
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"✅ Saved QC report: {report_file}")
    
    print(f"\n{'='*80}")
    print("QC CHECKS COMPLETE")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
