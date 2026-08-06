#!/usr/bin/env python3
"""
Verify data volume meets 1GB minimum requirement
Checks generated files, database tables, and provides volume estimates
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List

# Import timestamp utility
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    root_scripts = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(root_scripts))
    from timestamp_utils import get_est_timestamp

# Database imports
try:
    import psycopg2
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB"""
    if file_path.exists():
        return file_path.stat().st_size / (1024 * 1024)
    return 0.0


def get_directory_size_mb(directory: Path) -> float:
    """Get total size of directory in MB"""
    total_size = 0
    if directory.exists():
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    return total_size / (1024 * 1024)


def verify_file_volumes(data_dir: Path) -> Dict:
    """Verify data file volumes"""
    results = {
        'generated_files': {},
        'transformed_files': {},
        'internet_pulled_files': {},
        'internet_transformed_files': {},
        'total_generated_mb': 0.0,
        'total_transformed_mb': 0.0,
        'total_internet_pulled_mb': 0.0,
        'total_internet_transformed_mb': 0.0,
        'meets_requirement': False
    }
    
    # Check generated files
    generated_dir = data_dir / 'generated'
    if generated_dir.exists():
        files = [
            'companies.csv',
            'user_profiles.csv',
            'job_postings.csv',
            'job_applications.csv',
            'job_recommendations.csv'
        ]
        
        for filename in files:
            file_path = generated_dir / filename
            size_mb = get_file_size_mb(file_path)
            results['generated_files'][filename] = {
                'size_mb': round(size_mb, 2),
                'size_gb': round(size_mb / 1024, 2),
                'exists': file_path.exists()
            }
            results['total_generated_mb'] += size_mb
    
    # Check transformed files
    transformed_dir = data_dir / 'transformed'
    if transformed_dir.exists():
        files = [
            'companies_transformed.csv',
            'user_profiles_transformed.csv',
            'job_postings_transformed.csv',
            'job_applications_transformed.csv',
            'job_recommendations_transformed.csv'
        ]
        
        for filename in files:
            file_path = transformed_dir / filename
            size_mb = get_file_size_mb(file_path)
            results['transformed_files'][filename] = {
                'size_mb': round(size_mb, 2),
                'size_gb': round(size_mb / 1024, 2),
                'exists': file_path.exists()
            }
            results['total_transformed_mb'] += size_mb
    
    # Check internet-pulled files
    internet_pulled_dir = data_dir / 'internet_pulled'
    if internet_pulled_dir.exists():
        for file_path in internet_pulled_dir.rglob('*'):
            if file_path.is_file():
                size_mb = get_file_size_mb(file_path)
                results['internet_pulled_files'][file_path.name] = {
                    'size_mb': round(size_mb, 2),
                    'size_gb': round(size_mb / 1024, 2),
                    'path': str(file_path.relative_to(data_dir))
                }
                results['total_internet_pulled_mb'] += size_mb
    
    # Check internet-transformed files
    internet_transformed_dir = data_dir / 'internet_transformed'
    if internet_transformed_dir.exists():
        for file_path in internet_transformed_dir.rglob('*'):
            if file_path.is_file():
                size_mb = get_file_size_mb(file_path)
                results['internet_transformed_files'][file_path.name] = {
                    'size_mb': round(size_mb, 2),
                    'size_gb': round(size_mb / 1024, 2),
                    'path': str(file_path.relative_to(data_dir))
                }
                results['total_internet_transformed_mb'] += size_mb
    
    # Convert to GB
    results['total_generated_gb'] = round(results['total_generated_mb'] / 1024, 2)
    results['total_transformed_gb'] = round(results['total_transformed_mb'] / 1024, 2)
    results['total_internet_pulled_gb'] = round(results['total_internet_pulled_mb'] / 1024, 2)
    results['total_internet_transformed_gb'] = round(results['total_internet_transformed_mb'] / 1024, 2)
    
    # Calculate total (include all sources)
    total_gb = max(
        results['total_generated_gb'],
        results['total_transformed_gb'],
        results['total_internet_pulled_gb'],
        results['total_internet_transformed_gb']
    )
    # Also sum all sources for total volume
    total_all_sources_gb = (
        results['total_generated_gb'] +
        results['total_transformed_gb'] +
        results['total_internet_pulled_gb'] +
        results['total_internet_transformed_gb']
    )
    results['total_all_sources_gb'] = total_all_sources_gb
    
    # Check if meets requirement (1GB minimum) - use sum of all sources
    results['meets_requirement'] = total_all_sources_gb >= 1.0
    
    return results


def verify_database_volumes(db_config: Dict) -> Dict:
    """Verify database table volumes"""
    results = {
        'database_available': False,
        'tables': {},
        'total_size_mb': 0.0,
        'total_size_gb': 0.0
    }
    
    if not PG_AVAILABLE:
        return results
    
    try:
        conn = psycopg2.connect(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 5432),
            database=db_config.get('database', 'db_8_validation'),
            user=db_config.get('user', os.environ.get('USER', 'postgres')),
            password=db_config.get('password', '')
        )
        
        cursor = conn.cursor()
        
        # Get table sizes
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        
        for row in cursor.fetchall():
            schema, table, size_str, size_bytes = row
            size_mb = size_bytes / (1024 * 1024)
            results['tables'][table] = {
                'size_mb': round(size_mb, 2),
                'size_gb': round(size_mb / 1024, 2),
                'size_pretty': size_str
            }
            results['total_size_mb'] += size_mb
        
        results['total_size_gb'] = round(results['total_size_mb'] / 1024, 2)
        results['database_available'] = True
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        results['error'] = str(e)
    
    return results


def generate_volume_report(data_dir: Path, db_config: Dict = None) -> Dict:
    """Generate comprehensive volume report"""
    report = {
        'verification_date': get_est_timestamp(),
        'requirement': {
            'min_gb': 1.0,
            'max_gb': None,
            'description': 'Data volume must be at least 1 GB'
        },
        'file_volumes': verify_file_volumes(data_dir),
        'database_volumes': verify_database_volumes(db_config or {}),
        'summary': {}
    }
    
    # Calculate summary
    file_volumes = report['file_volumes']
    file_gb = file_volumes.get('total_all_sources_gb', file_volumes.get('total_generated_gb', 0))
    db_gb = report['database_volumes']['total_size_gb']
    
    # Include internet-pulled data in total
    internet_gb = file_volumes.get('total_internet_pulled_gb', 0) + file_volumes.get('total_internet_transformed_gb', 0)
    total_file_gb = file_gb + internet_gb
    
    report['summary'] = {
        'file_data_gb': file_gb,
        'internet_pulled_gb': internet_gb,
        'total_file_data_gb': total_file_gb,
        'database_data_gb': db_gb,
        'total_data_gb': max(total_file_gb, db_gb),
        'meets_requirement': report['file_volumes']['meets_requirement'] or (db_gb >= 1.0),
        'status': 'PASS' if (report['file_volumes']['meets_requirement'] or (db_gb >= 1.0)) else 'FAIL'
    }
    
    return report


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify data volume meets 1GB minimum requirement')
    parser.add_argument('--data-dir', type=str, default='data',
                       help='Data directory path')
    parser.add_argument('--db-host', type=str, default='localhost',
                       help='Database host')
    parser.add_argument('--db-port', type=int, default=5432,
                       help='Database port')
    parser.add_argument('--db-name', type=str, default='db_8_validation',
                       help='Database name')
    parser.add_argument('--db-user', type=str, default=None,
                       help='Database user')
    parser.add_argument('--db-password', type=str, default='',
                       help='Database password')
    parser.add_argument('--output', type=str, default=None,
                       help='Output JSON file path')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'database': args.db_name,
        'user': args.db_user or os.environ.get('USER', 'postgres'),
        'password': args.db_password or os.environ.get('PG_PASSWORD', '')
    }
    
    report = generate_volume_report(data_dir, db_config)
    
    # Print summary
    print("\n" + "="*70)
    print("Data Volume Verification Report")
    print("="*70)
    if report['requirement']['max_gb']:
        print(f"Requirement: {report['requirement']['min_gb']:.1f}-{report['requirement']['max_gb']:.1f} GB")
    else:
        print(f"Requirement: Minimum {report['requirement']['min_gb']:.1f} GB")
    print(f"\nFile Data:")
    print(f"  Rebuilt: {report['file_volumes']['total_generated_gb']:.2f} GB")
    print(f"  Transformed: {report['file_volumes']['total_transformed_gb']:.2f} GB")
    print(f"  Internet Pulled: {report['file_volumes']['total_internet_pulled_gb']:.2f} GB")
    print(f"  Internet Transformed: {report['file_volumes']['total_internet_transformed_gb']:.2f} GB")
    print(f"  Total File Data: {report['summary']['total_file_data_gb']:.2f} GB")
    print(f"\nDatabase Data:")
    if report['database_volumes']['database_available']:
        print(f"  Total: {report['database_volumes']['total_size_gb']:.2f} GB")
        print(f"  Tables: {len(report['database_volumes']['tables'])}")
    else:
        print(f"  Database not available (connection failed)")
    print(f"\nSummary:")
    print(f"  Total Data: {report['summary']['total_data_gb']:.2f} GB")
    print(f"  Meets Requirement (>=1GB): {'YES' if report['summary']['meets_requirement'] else 'NO'}")
    print(f"  Status: {report['summary']['status']}")
    print("="*70)
    
    # Save report
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = data_dir.parent / 'results' / f'volume_verification_{get_est_timestamp()}.json'
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved to: {output_file}")


if __name__ == '__main__':
    main()
