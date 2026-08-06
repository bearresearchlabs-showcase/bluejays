#!/usr/bin/env python3
"""
Generic database validation script
Validates queries.md for any database (db-1 through db-15)
"""

import sys
import os
from pathlib import Path

# Add db-1 scripts to path for imports
script_dir = Path(__file__).parent
db1_scripts = script_dir.parent / 'db-1' / 'scripts'
sys.path.insert(0, str(db1_scripts))

from verify_fixes import FixVerifier
from comprehensive_validator import QueryExtractor, QueryEvaluator, SyntaxValidator
from generate_final_report import load_json_file

def validate_database(db_num: int):
    """Validate a specific database"""
    root_dir = script_dir.parent
    db_dir = root_dir / f'db-{db_num}'
    queries_file = db_dir / 'queries' / 'queries.md'

    if not queries_file.exists():
        print(f"⚠️  db-{db_num}: queries.md not found")
        return None

    print(f"\n{'='*70}")
    print(f"Validating db-{db_num}")
    print(f"{'='*70}")

    results = {
        'database': f'db-{db_num}',
        'validation_date': None,
        'phases': {}
    }

    # Phase 1: Fix Verification (generic checks only)
    print("\nPhase 1: Fix Verification (Generic Checks)...")
    try:
        # Generic checks: title uniqueness, header formatting
        verifier = FixVerifier(queries_file)
        # Only run generic checks, skip db-1 specific fixes
        title_result = verifier.verify_query_title_uniqueness()
        header_result = verifier.verify_header_formatting()

        results['phases']['fix_verification'] = {
            'query_title_uniqueness': title_result,
            'header_formatting': header_result,
            'status': 'PASS' if title_result['status'] == 'PASS' and header_result['status'] == 'PASS' else 'FAIL'
        }
        print(f"  Title Uniqueness: {title_result['status']}")
        print(f"  Header Formatting: {header_result['status']}")
    except Exception as e:
        print(f"  ⚠️  Fix verification failed: {e}")
        results['phases']['fix_verification'] = {'status': 'ERROR', 'error': str(e)}

    # Phase 2 & 4: Extract queries and evaluate
    print("\nPhase 2 & 4: Query Extraction and Evaluation...")
    try:
        extractor = QueryExtractor()
        queries = extractor.extract_queries(queries_file)

        print(f"  Extracted {len(queries)} queries")

        if len(queries) == 0:
            print("  ⚠️  No queries found")
            results['phases']['evaluation'] = {'status': 'NO_QUERIES'}
            return results

        # Evaluate queries
        evaluator = QueryEvaluator()
        count_result = evaluator.evaluate_query_count(queries)
        recursive_result = evaluator.evaluate_recursive_cte_usage(queries)
        cte_result = evaluator.evaluate_cte_usage(queries)
        complexity_result = evaluator.evaluate_complexity(queries)

        results['phases']['evaluation'] = {
            'query_count': count_result,
            'recursive_cte_usage': recursive_result,
            'cte_usage': cte_result,
            'complexity': complexity_result,
            'status': 'PASS' if count_result['status'] == 'PASS' and cte_result['status'] == 'PASS' else 'FAIL'
        }

        print(f"  Query Count: {count_result['found']}/30 - {count_result['status']}")
        print(f"  CTE Usage: {cte_result['queries_with_cte']}/{cte_result['total_queries']} - {cte_result['status']}")
        print(f"  Recursive CTEs: {recursive_result['queries_with_recursive']} queries")
        if recursive_result['mismatched'] > 0:
            print(f"  ⚠️  {recursive_result['mismatched']} queries with mismatched recursive CTE claims")

    except Exception as e:
        print(f"  ⚠️  Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        results['phases']['evaluation'] = {'status': 'ERROR', 'error': str(e)}

    # Determine overall status
    overall_status = 'PASS'
    if results['phases'].get('fix_verification', {}).get('status') == 'FAIL':
        overall_status = 'FAIL'
    elif results['phases'].get('evaluation', {}).get('status') == 'FAIL':
        overall_status = 'FAIL'
    elif results['phases'].get('fix_verification', {}).get('status') == 'ERROR':
        overall_status = 'ERROR'

    results['overall_status'] = overall_status
    results['validation_date'] = __import__('datetime').datetime.now().isoformat()

    # Save results
    results_file = db_dir / 'results' / 'validation_summary.json'
    results_file.parent.mkdir(parents=True, exist_ok=True)
    import json
    results_file.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n  Results saved to: {results_file}")

    return results

def main():
    """Main function"""
    if len(sys.argv) > 1:
        db_nums = [int(sys.argv[1])]
    else:
        db_nums = list(range(1, 6))

    all_results = {}
    for db_num in db_nums:
        result = validate_database(db_num)
        if result:
            all_results[f'db-{db_num}'] = result

    # Print summary
    print("\n" + "="*70)
    print("Validation Summary")
    print("="*70)
    for db_name, result in all_results.items():
        status = result.get('overall_status', 'UNKNOWN')
        queries = result.get('phases', {}).get('evaluation', {}).get('query_count', {}).get('found', 0)
        print(f"{db_name}: Status={status}, Queries={queries}")

    # Save combined summary
    summary_file = script_dir.parent / 'validation_summary_all_databases.json'
    import json
    summary_file.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"\nCombined summary saved to: {summary_file}")

if __name__ == '__main__':
    main()
