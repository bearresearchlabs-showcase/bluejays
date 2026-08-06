#!/usr/bin/env python3
"""
Cursor /validate command - Run validation suite for database repositories

Usage:
    /validate @db/db-1/              # Validate single database
    /validate @db/db-1/ @db/db-5/    # Validate range of databases
    /validate -a                     # Validate all databases (db-1 through db-15)
    /validate db-1                  # Validate by database number
    /validate db-1 db-5             # Validate range by database numbers
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

# Add scripts directory to path for timestamp_utils
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from timestamp_utils import get_est_timestamp

class ValidationRunner:
    """Run validation suite for database repositories"""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.results = {}

    def parse_arguments(self, args: List[str]) -> List[int]:
        """Parse command line arguments and return list of database numbers"""
        db_nums = []

        if not args:
            print("Usage: /validate @db/db-1/ [@db/db-2/] | /validate -a | /validate db-1 [db-5]")
            return []

        # Handle -a flag (all databases)
        if '-a' in args or '--all' in args:
            return list(range(1, 16))  # db-1 through db-15

        # Handle --help
        if '--help' in args or '-h' in args:
            print(__doc__)
            return []

        # Parse arguments
        for arg in args:
            arg = arg.strip()

            # Handle @db/db-N/ format
            if '@db/db-' in arg or 'db/db-' in arg:
                # Extract database number
                if '@db/db-' in arg:
                    db_part = arg.split('@db/db-')[1].split('/')[0]
                else:
                    db_part = arg.split('db/db-')[1].split('/')[0]

                try:
                    db_num = int(db_part)
                    db_nums.append(db_num)
                except ValueError:
                    print(f"⚠️  Invalid database format: {arg}")
                    continue

            # Handle db-N format
            elif arg.startswith('db-'):
                try:
                    db_num = int(arg.split('db-')[1])
                    db_nums.append(db_num)
                except ValueError:
                    print(f"⚠️  Invalid database format: {arg}")
                    continue

            # Handle plain number
            elif arg.isdigit():
                db_nums.append(int(arg))

            else:
                print(f"⚠️  Unknown argument format: {arg}")

        # Handle range (if two numbers provided)
        if len(db_nums) == 2 and db_nums[0] < db_nums[1]:
            db_nums = list(range(db_nums[0], db_nums[1] + 1))

        return sorted(set(db_nums))  # Remove duplicates and sort

    def validate_database(self, db_num: int) -> dict:
        """Run validation suite for a single database"""
        db_dir = self.root_dir / f'db-{db_num}'
        queries_dir = db_dir / 'queries'
        scripts_dir = db_dir / 'scripts'
        results_dir = db_dir / 'results'

        if not db_dir.exists():
            return {
                'status': 'SKIPPED',
                'error': f'db-{db_num} directory not found'
            }

        print(f"\n{'='*70}")
        print(f"Validating db-{db_num}")
        print(f"{'='*70}")

        result = {
            'database': f'db-{db_num}',
            'start_time': get_est_timestamp(),  # EST format: YYYYMMDD-HHMM
            'phases': {}
        }

        # Phase 0: Extract queries to JSON (REQUIRED)
        print(f"\n[Phase 0] Extracting queries.md to queries.json...")
        try:
            extract_script = self.root_dir / 'scripts' / 'extract_queries_to_json.py'
            if not extract_script.exists():
                extract_script = scripts_dir / 'extract_queries_to_json.py'

            if extract_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(extract_script), str(db_num)],
                    cwd=str(self.root_dir),
                    capture_output=True,
                    text=True
                )
                if proc.returncode == 0:
                    print("  ✓ Phase 0: Query extraction completed")
                    result['phases']['phase_0_extraction'] = {'status': 'PASS'}
                else:
                    print(f"  ✗ Phase 0: Query extraction failed")
                    print(f"    Error: {proc.stderr}")
                    result['phases']['phase_0_extraction'] = {
                        'status': 'FAIL',
                        'error': proc.stderr
                    }
            else:
                print(f"  ⚠️  Phase 0: Extraction script not found")
                result['phases']['phase_0_extraction'] = {'status': 'SKIPPED'}
        except Exception as e:
            print(f"  ✗ Phase 0: Error - {e}")
            result['phases']['phase_0_extraction'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Check if queries.json exists (required)
        queries_json = queries_dir / 'queries.json'
        if not queries_json.exists():
            print(f"\n  ✗ CRITICAL: queries.json not found!")
            print(f"    Phase 0 must complete successfully before validation can proceed.")
            result['status'] = 'FAIL'
            result['error'] = 'queries.json missing - Phase 0 extraction required'
            result['end_time'] = get_est_timestamp()  # EST format: YYYYMMDD-HHMM
            return result

        # Phase 1: Fix Verification
        print(f"\n[Phase 1] Verifying fixes...")
        try:
            verify_script = scripts_dir / 'verify_fixes.py'
            if verify_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(verify_script)],
                    cwd=str(db_dir),
                    capture_output=True,
                    text=True
                )
                if proc.returncode == 0:
                    print("  ✓ Phase 1: Fix verification completed")
                    result['phases']['phase_1_fix_verification'] = {'status': 'PASS'}
                else:
                    print(f"  ✗ Phase 1: Fix verification failed")
                    result['phases']['phase_1_fix_verification'] = {
                        'status': 'FAIL',
                        'error': proc.stderr[:500] if proc.stderr else 'Unknown error'
                    }
            else:
                print(f"  ⚠️  Phase 1: Script not found")
                result['phases']['phase_1_fix_verification'] = {'status': 'SKIPPED'}
        except Exception as e:
            print(f"  ✗ Phase 1: Error - {e}")
            result['phases']['phase_1_fix_verification'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Phase 2 & 4: Syntax Validation and Comprehensive Evaluation
        print(f"\n[Phase 2 & 4] Syntax validation and comprehensive evaluation...")
        try:
            validator_script = scripts_dir / 'comprehensive_validator.py'
            if validator_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(validator_script)],
                    cwd=str(db_dir),
                    capture_output=True,
                    text=True
                )
                if proc.returncode == 0:
                    print("  ✓ Phase 2 & 4: Validation completed")
                    result['phases']['phase_2_4_validation'] = {'status': 'PASS'}
                else:
                    print(f"  ✗ Phase 2 & 4: Validation failed")
                    result['phases']['phase_2_4_validation'] = {
                        'status': 'FAIL',
                        'error': proc.stderr[:500] if proc.stderr else 'Unknown error'
                    }
            else:
                print(f"  ⚠️  Phase 2 & 4: Script not found")
                result['phases']['phase_2_4_validation'] = {'status': 'SKIPPED'}
        except Exception as e:
            print(f"  ✗ Phase 2 & 4: Error - {e}")
            result['phases']['phase_2_4_validation'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Phase 3: Execution Testing (optional - requires database connections)
        print(f"\n[Phase 3] Execution testing (optional)...")
        try:
            exec_script = scripts_dir / 'execution_tester.py'
            if exec_script.exists():
                # Check if database credentials are available
                import os
                import socket

                # Check for PostgreSQL credentials (support both PG_* and POSTGRES_* formats)
                has_pg_env = bool(
                    os.getenv('PG_HOST') or os.getenv('PG_USER') or
                    os.getenv('POSTGRES_HOST') or os.getenv('POSTGRES_USER')
                )

                # Check if PostgreSQL is running on localhost:5432 (common default)
                pg_available_local = False
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    connection_result = sock.connect_ex(('localhost', 5432))
                    sock.close()
                    pg_available_local = (connection_result == 0)
                except Exception:
                    pass

                # For db-1 and db-6, prioritize PostgreSQL
                # If PostgreSQL is available locally and no explicit credentials, use defaults
                has_pg = has_pg_env or pg_available_local

                # Set default PostgreSQL credentials if not set and PostgreSQL is available locally
                if pg_available_local and not has_pg_env:
                    # Set default PostgreSQL environment variables for localhost connection
                    # Check for common Docker PostgreSQL container defaults
                    if not os.getenv('PG_HOST'):
                        os.environ['PG_HOST'] = 'localhost'
                    if not os.getenv('PG_PORT'):
                        os.environ['PG_PORT'] = '5432'
                    if not os.getenv('PG_USER'):
                        os.environ['PG_USER'] = 'postgres'
                    if not os.getenv('PG_DATABASE'):
                        # Try db{N} first (common Docker naming), then fallback to db_{N}_validation
                        os.environ['PG_DATABASE'] = f'db{db_num}'
                    # Default password for Docker PostgreSQL containers is often 'postgres'
                    if not os.getenv('PG_PASSWORD'):
                        os.environ['PG_PASSWORD'] = 'postgres'
                    print(f"  ℹ️  Using default PostgreSQL connection (localhost:5432, user=postgres, database={os.environ.get('PG_DATABASE')})")

                has_databricks = bool(os.getenv('SNOWFLAKE_USER') or os.getenv('SNOWFLAKE_ACCOUNT'))

                if has_pg or has_databricks:
                    proc = subprocess.run(
                        [sys.executable, str(exec_script)],
                        cwd=str(db_dir),
                        capture_output=True,
                        text=True
                    )
                    if proc.returncode == 0:
                        print("  ✓ Phase 3: Execution testing completed")
                        result['phases']['phase_3_execution'] = {'status': 'PASS'}
                    else:
                        print(f"  ✗ Phase 3: Execution testing failed")
                        result['phases']['phase_3_execution'] = {
                            'status': 'FAIL',
                            'error': proc.stderr[:500] if proc.stderr else 'Unknown error'
                        }
                else:
                    print("  ⚠️  Phase 3: Skipped (no database credentials)")
                    result['phases']['phase_3_execution'] = {'status': 'SKIPPED', 'reason': 'No database credentials'}
            else:
                print(f"  ⚠️  Phase 3: Script not found")
                result['phases']['phase_3_execution'] = {'status': 'SKIPPED'}
        except Exception as e:
            print(f"  ✗ Phase 3: Error - {e}")
            result['phases']['phase_3_execution'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Phase 5: Generate Final Report
        print(f"\n[Phase 5] Generating final report...")
        try:
            report_script = scripts_dir / 'generate_final_report.py'
            if report_script.exists():
                proc = subprocess.run(
                    [sys.executable, str(report_script)],
                    cwd=str(db_dir),
                    capture_output=True,
                    text=True
                )
                if proc.returncode == 0:
                    print("  ✓ Phase 5: Report generation completed")
                    result['phases']['phase_5_report'] = {'status': 'PASS'}
                else:
                    print(f"  ✗ Phase 5: Report generation failed")
                    result['phases']['phase_5_report'] = {
                        'status': 'FAIL',
                        'error': proc.stderr[:500] if proc.stderr else 'Unknown error'
                    }
            else:
                print(f"  ⚠️  Phase 5: Script not found")
                result['phases']['phase_5_report'] = {'status': 'SKIPPED'}
        except Exception as e:
            print(f"  ✗ Phase 5: Error - {e}")
            result['phases']['phase_5_report'] = {
                'status': 'ERROR',
                'error': str(e)
            }

        # Determine overall status
        phase_statuses = [p.get('status', 'UNKNOWN') for p in result['phases'].values()]
        if 'FAIL' in phase_statuses or 'ERROR' in phase_statuses:
            result['status'] = 'FAIL'
        elif all(s == 'PASS' for s in phase_statuses):
            result['status'] = 'PASS'
        elif 'SKIPPED' in phase_statuses:
            result['status'] = 'PARTIAL'
        else:
            result['status'] = 'UNKNOWN'

        result['end_time'] = get_est_timestamp()  # EST format: YYYYMMDD-HHMM

        print(f"\n{'='*70}")
        print(f"db-{db_num} Validation Status: {result['status']}")
        print(f"{'='*70}")

        return result

    def run(self, args: List[str]) -> dict:
        """Run validation for specified databases"""
        db_nums = self.parse_arguments(args)

        if not db_nums:
            return {'error': 'No valid databases specified'}

        print(f"\n{'='*70}")
        print(f"Validation Suite - Running for {len(db_nums)} database(s)")
        print(f"Databases: {', '.join(f'db-{n}' for n in db_nums)}")
        print(f"{'='*70}")

        all_results = {
            'validation_date': get_est_timestamp(),  # EST format: YYYYMMDD-HHMM
            'databases': {},
            'summary': {}
        }

        for db_num in db_nums:
            result = self.validate_database(db_num)
            all_results['databases'][f'db-{db_num}'] = result

        # Generate summary
        statuses = [r.get('status', 'UNKNOWN') for r in all_results['databases'].values()]
        all_results['summary'] = {
            'total_databases': len(db_nums),
            'passed': sum(1 for s in statuses if s == 'PASS'),
            'failed': sum(1 for s in statuses if s == 'FAIL'),
            'partial': sum(1 for s in statuses if s == 'PARTIAL'),
            'skipped': sum(1 for s in statuses if s == 'SKIPPED'),
            'overall_status': 'PASS' if all(s == 'PASS' for s in statuses) else 'FAIL' if any(s == 'FAIL' for s in statuses) else 'PARTIAL'
        }

        # Print summary
        print(f"\n{'='*70}")
        print("Validation Summary")
        print(f"{'='*70}")
        print(f"Total Databases: {all_results['summary']['total_databases']}")
        print(f"Passed: {all_results['summary']['passed']}")
        print(f"Failed: {all_results['summary']['failed']}")
        print(f"Partial: {all_results['summary']['partial']}")
        print(f"Skipped: {all_results['summary']['skipped']}")
        print(f"Overall Status: {all_results['summary']['overall_status']}")
        print(f"{'='*70}\n")

        # Save summary to file
        summary_file = self.root_dir / 'validation_summary.json'
        summary_file.write_text(json.dumps(all_results, indent=2))
        print(f"Summary saved to: {summary_file}")

        return all_results

def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    runner = ValidationRunner(root_dir)

    # Get arguments from command line (skip script name)
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    result = runner.run(args)

    # Exit with appropriate code
    if result.get('summary', {}).get('overall_status') == 'FAIL':
        sys.exit(1)
    elif result.get('summary', {}).get('overall_status') == 'PARTIAL':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
