#!/usr/bin/env python3
"""
Generate a comprehensive summary of query test results
"""

import json
from pathlib import Path
from datetime import datetime

def load_test_results():
    """Load all test result files"""
    root_dir = Path(__file__).parent
    results = {}

    for db_num in range(1, 6):
        db_name = f'db-{db_num}'
        results_file = root_dir / db_name / 'results' / 'query_test_results_postgres.json'

        if results_file.exists():
            with open(results_file, 'r') as f:
                results[db_name] = json.load(f)
        else:
            results[db_name] = None

    return results

def analyze_results(results):
    """Analyze test results and generate summary"""
    summary = {
        'generated_at': datetime.now().isoformat(),
        'databases': {},
        'overall': {
            'total_databases': 0,
            'databases_tested': 0,
            'total_queries': 0,
            'postgresql': {
                'total_tested': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0
            },
            'snowflake': {
                'total_tested': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0
            }
        }
    }

    for db_name, db_results in results.items():
        if db_results is None:
            summary['databases'][db_name] = {
                'status': 'not_tested',
                'error': 'Test results file not found'
            }
            continue

        summary['overall']['databases_tested'] += 1
        db_summary = {
            'database': db_results.get('database', db_name),
            'test_timestamp': db_results.get('test_timestamp', ''),
            'postgresql': {},
            'snowflake': {}
        }

        # Analyze PostgreSQL results
        pg_stats = db_results.get('postgresql', {})
        if pg_stats.get('available', False):
            pg_queries = pg_stats.get('queries', [])
            pg_stats_data = pg_stats.get('statistics', {})

            db_summary['postgresql'] = {
                'available': True,
                'total_queries': pg_stats_data.get('total_queries', len(pg_queries)),
                'successful': pg_stats_data.get('successful', 0),
                'failed': pg_stats_data.get('failed', 0),
                'success_rate': pg_stats_data.get('success_rate', 0.0),
                'avg_execution_time_ms': pg_stats_data.get('avg_execution_time_ms', 0.0),
                'total_rows_returned': pg_stats_data.get('total_rows_returned', 0)
            }

            # Collect error types
            errors = {}
            for q in pg_queries:
                if not q.get('success', False):
                    error_type = q.get('error_type', 'Unknown')
                    error_msg = q.get('error', '')[:100]  # First 100 chars
                    if error_type not in errors:
                        errors[error_type] = []
                    errors[error_type].append({
                        'query': q.get('query_number', 0),
                        'error': error_msg
                    })

            db_summary['postgresql']['error_summary'] = {
                error_type: len(errors_list)
                for error_type, errors_list in errors.items()
            }
            db_summary['postgresql']['sample_errors'] = {
                error_type: errors_list[:3]  # First 3 of each type
                for error_type, errors_list in list(errors.items())[:5]
            }

            summary['overall']['postgresql']['total_tested'] += db_summary['postgresql']['total_queries']
            summary['overall']['postgresql']['successful'] += db_summary['postgresql']['successful']
            summary['overall']['postgresql']['failed'] += db_summary['postgresql']['failed']
        else:
            db_summary['postgresql'] = {
                'available': False,
                'reason': 'PostgreSQL connector not available'
            }

        # Analyze Snowflake results
        sf_stats = db_results.get('snowflake', {})
        if sf_stats.get('available', False):
            sf_queries = sf_stats.get('queries', [])
            sf_stats_data = sf_stats.get('statistics', {})

            db_summary['snowflake'] = {
                'available': True,
                'total_queries': sf_stats_data.get('total_queries', len(sf_queries)),
                'successful': sf_stats_data.get('successful', 0),
                'failed': sf_stats_data.get('failed', 0),
                'success_rate': sf_stats_data.get('success_rate', 0.0),
                'avg_execution_time_ms': sf_stats_data.get('avg_execution_time_ms', 0.0),
                'total_rows_returned': sf_stats_data.get('total_rows_returned', 0)
            }

            summary['overall']['snowflake']['total_tested'] += db_summary['snowflake']['total_queries']
            summary['overall']['snowflake']['successful'] += db_summary['snowflake']['successful']
            summary['overall']['snowflake']['failed'] += db_summary['snowflake']['failed']
        else:
            db_summary['snowflake'] = {
                'available': False,
                'reason': sf_stats.get('reason', 'Snowflake connector not available or connection failed')
            }

        summary['databases'][db_name] = db_summary
        summary['overall']['total_queries'] += db_summary['postgresql'].get('total_queries', 0)

    # Calculate overall success rates
    if summary['overall']['postgresql']['total_tested'] > 0:
        summary['overall']['postgresql']['success_rate'] = (
            summary['overall']['postgresql']['successful'] /
            summary['overall']['postgresql']['total_tested'] * 100
        )

    if summary['overall']['snowflake']['total_tested'] > 0:
        summary['overall']['snowflake']['success_rate'] = (
            summary['overall']['snowflake']['successful'] /
            summary['overall']['snowflake']['total_tested'] * 100
        )

    summary['overall']['total_databases'] = 5

    return summary

def print_summary(summary):
    """Print a formatted summary"""
    print("="*80)
    print("QUERY TEST RESULTS SUMMARY")
    print("="*80)
    print(f"\nRebuilt: {summary['generated_at']}")
    print(f"\nOverall Statistics:")
    print(f"  Databases Tested: {summary['overall']['databases_tested']}/5")
    print(f"  Total Queries Tested: {summary['overall']['total_queries']}")

    print(f"\n  PostgreSQL:")
    pg = summary['overall']['postgresql']
    print(f"    Total Tested: {pg['total_tested']}")
    print(f"    Successful: {pg['successful']}")
    print(f"    Failed: {pg['failed']}")
    print(f"    Success Rate: {pg['success_rate']:.2f}%")

    print(f"\n  Snowflake:")
    sf = summary['overall']['snowflake']
    print(f"    Total Tested: {sf['total_tested']}")
    print(f"    Successful: {sf['successful']}")
    print(f"    Failed: {sf['failed']}")
    if sf['total_tested'] > 0:
        print(f"    Success Rate: {sf['success_rate']:.2f}%")
    else:
        print(f"    Status: Not tested (connection failed)")

    print("\n" + "="*80)
    print("PER-DATABASE RESULTS")
    print("="*80)

    for db_name, db_data in summary['databases'].items():
        if db_data.get('status') == 'not_tested':
            print(f"\n{db_name}: ❌ Not tested - {db_data.get('error', 'Unknown error')}")
            continue

        print(f"\n{db_name}:")
        print(f"  Test Timestamp: {db_data.get('test_timestamp', 'N/A')}")

        pg_data = db_data.get('postgresql', {})
        if pg_data.get('available'):
            print(f"  PostgreSQL:")
            print(f"    Queries: {pg_data['total_queries']}")
            print(f"    Successful: {pg_data['successful']} ({pg_data['success_rate']:.2f}%)")
            print(f"    Failed: {pg_data['failed']}")
            if pg_data.get('error_summary'):
                print(f"    Common Errors:")
                for error_type, count in list(pg_data['error_summary'].items())[:5]:
                    print(f"      - {error_type}: {count} occurrences")
        else:
            print(f"  PostgreSQL: ❌ {pg_data.get('reason', 'Not available')}")

        sf_data = db_data.get('snowflake', {})
        if sf_data.get('available'):
            print(f"  Snowflake:")
            print(f"    Queries: {sf_data['total_queries']}")
            print(f"    Successful: {sf_data['successful']} ({sf_data['success_rate']:.2f}%)")
            print(f"    Failed: {sf_data['failed']}")
        else:
            print(f"  Snowflake: ❌ {sf_data.get('reason', 'Not available')}")

def main():
    """Main execution"""
    results = load_test_results()
    summary = analyze_results(results)

    # Print summary
    print_summary(summary)

    # Save summary to JSON
    root_dir = Path(__file__).parent
    summary_file = root_dir / 'results' / 'test_summary.json'
    summary_file.parent.mkdir(parents=True, exist_ok=True)

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n✅ Summary saved to: {summary_file}")

if __name__ == '__main__':
    main()
