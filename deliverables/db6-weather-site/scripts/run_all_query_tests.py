#!/usr/bin/env python3
"""
Execute query testing for all databases (db-6 through db-15)
This script runs the equivalent of all the Jupyter notebooks programmatically
"""

import psycopg2
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Optional visualization imports
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib/seaborn not available - visualizations will be skipped")

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
DATABASES = [f'db-{i}' for i in range(6, 16)]

# Set visualization style (if available)
if HAS_MATPLOTLIB:
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")

# Database configuration
DB_CONFIG = {
    'host': os.getenv('PG_HOST', 'localhost'),
    'port': os.getenv('PG_PORT', '5432'),
    'user': os.getenv('PG_USER', os.getenv('USER', 'machine')),
    'password': os.getenv('PG_PASSWORD', ''),
    'database': 'postgres'
}

def initialize_database(db_name: str, db_dir: Path, config: dict) -> bool:
    """Initialize database: create, load schema, load data."""
    try:
        # Connect to postgres database
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f'CREATE DATABASE {db_name}')
            print(f"✅ Created database: {db_name}")
        else:
            print(f"ℹ️  Database {db_name} already exists")
        
        cur.close()
        conn.close()
        
        # Load schema
        schema_file = db_dir / 'data' / 'schema.sql'
        if schema_file.exists():
            db_config = config.copy()
            db_config['database'] = db_name
            conn = psycopg2.connect(**db_config)
            cur = conn.cursor()
            
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                if statement:
                    try:
                        cur.execute(statement)
                    except Exception as e:
                        if 'already exists' not in str(e).lower():
                            pass
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Loaded schema for {db_name}")
        
        # Load data
        data_file = db_dir / 'data' / 'data.sql'
        if data_file.exists():
            db_config = config.copy()
            db_config['database'] = db_name
            conn = psycopg2.connect(**db_config)
            cur = conn.cursor()
            
            with open(data_file, 'r') as f:
                data_sql = f.read()
            
            statements = [s.strip() for s in data_sql.split(';') if s.strip()]
            for statement in statements:
                if statement:
                    try:
                        cur.execute(statement)
                    except Exception as e:
                        if 'duplicate' not in str(e).lower():
                            pass
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"✅ Loaded data for {db_name}")
        
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def execute_query_with_metrics(db_name: str, query_sql: str, query_num: int, config: dict):
    """Execute a query and return results with metrics."""
    db_config = config.copy()
    db_config['database'] = db_name
    
    start_time = datetime.now()
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        query_clean = query_sql.strip().rstrip(';')
        cur.execute(query_clean)
        
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        
        df = pd.DataFrame(rows, columns=columns) if columns else pd.DataFrame()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        cur.close()
        conn.close()
        
        return {
            'success': True,
            'error': None,
            'dataframe': df,
            'execution_time': execution_time,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': columns
        }
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        error_msg = str(e)
        
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
        
        return {
            'success': False,
            'error': error_msg,
            'dataframe': None,
            'execution_time': execution_time,
            'row_count': 0,
            'column_count': 0,
            'columns': []
        }

def create_performance_visualizations(perf_df: pd.DataFrame, db_name: str, output_dir: Path):
    """Create performance visualization charts."""
    if not HAS_MATPLOTLIB:
        print("⚠️  Skipping visualization (matplotlib not available)")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Execution time bar chart
    axes[0, 0].bar(perf_df['Query'], perf_df['Execution Time (s)'], color='steelblue', alpha=0.7)
    axes[0, 0].set_xlabel('Query Number')
    axes[0, 0].set_ylabel('Execution Time (seconds)')
    axes[0, 0].set_title('Query Execution Time by Query Number')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Execution time histogram
    axes[0, 1].hist(perf_df['Execution Time (s)'], bins=20, color='coral', alpha=0.7, edgecolor='black')
    axes[0, 1].set_xlabel('Execution Time (seconds)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Distribution of Execution Times')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Row count bar chart
    axes[1, 0].bar(perf_df['Query'], perf_df['Row Count'], color='green', alpha=0.7)
    axes[1, 0].set_xlabel('Query Number')
    axes[1, 0].set_ylabel('Row Count')
    axes[1, 0].set_title('Rows Returned by Query')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Status pie chart
    status_counts = perf_df['Status'].value_counts()
    axes[1, 1].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    axes[1, 1].set_title('Query Execution Status')
    
    plt.tight_layout()
    
    # Save visualization
    viz_file = output_dir / f'{db_name}_performance_visualization.png'
    plt.savefig(viz_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved performance visualization: {viz_file}")

def test_database(db_name: str, db_dir: Path):
    """Test all queries for a database."""
    print(f"\n{'='*80}")
    print(f"TESTING DATABASE: {db_name.upper()}")
    print(f"{'='*80}")
    
    # Database name for PostgreSQL (db6, db7, etc.)
    db_num = db_name.replace('db-', 'db')
    
    # Initialize database
    print(f"\n[1/5] Initializing database...")
    if not initialize_database(db_num, db_dir, DB_CONFIG):
        print(f"❌ Failed to initialize {db_name}")
        return None
    
    # Load queries
    print(f"\n[2/5] Loading queries...")
    queries_file = db_dir / 'queries' / 'queries.json'
    if not queries_file.exists():
        print(f"❌ queries.json not found for {db_name}")
        return None
    
    with open(queries_file) as f:
        queries_data = json.load(f)
    
    queries = queries_data.get('queries', [])
    total_queries = len(queries)
    print(f"✅ Loaded {total_queries} queries")
    
    # Execute queries
    print(f"\n[3/5] Executing queries...")
    all_results = []
    
    for query_info in queries:
        query_num = query_info.get('number')
        query_sql = query_info.get('sql', '')
        query_title = query_info.get('title', f'Query {query_num}')
        
        result = execute_query_with_metrics(db_num, query_sql, query_num, DB_CONFIG)
        result['query_number'] = query_num
        result['query_title'] = query_title
        result['query_info'] = query_info
        
        all_results.append(result)
        
        status = "✅" if result['success'] else "❌"
        print(f"  {status} Query {query_num:2d}: {query_title[:50]:<50} ({result['execution_time']:.3f}s, {result['row_count']:4d} rows)")
    
    # Summary
    passed = sum(1 for r in all_results if r['success'])
    failed = sum(1 for r in all_results if not r['success'])
    print(f"\n✅ Execution complete: {passed}/{total_queries} passed ({passed/total_queries*100:.1f}%)")
    
    # Create performance DataFrame
    print(f"\n[4/5] Creating visualizations...")
    perf_data = []
    for r in all_results:
        perf_data.append({
            'Query': r['query_number'],
            'Title': r['query_title'][:40] + '...' if len(r['query_title']) > 40 else r['query_title'],
            'Execution Time (s)': r['execution_time'],
            'Row Count': r['row_count'],
            'Column Count': r['column_count'],
            'Status': 'Passed' if r['success'] else 'Failed'
        })
    
    perf_df = pd.DataFrame(perf_data)
    
    # Create visualizations
    output_dir = db_dir / 'results'
    output_dir.mkdir(exist_ok=True)
    create_performance_visualizations(perf_df, db_num, output_dir)
    
    # Generate report
    print(f"\n[5/5] Generating report...")
    report_data = {
        'database': db_num,
        'test_timestamp': datetime.now().isoformat(),
        'total_queries': total_queries,
        'passed': passed,
        'failed': failed,
        'success_rate': passed / total_queries * 100 if total_queries > 0 else 0,
        'average_execution_time': perf_df['Execution Time (s)'].mean(),
        'total_execution_time': perf_df['Execution Time (s)'].sum(),
        'queries': []
    }
    
    for r in all_results:
        query_report = {
            'number': r['query_number'],
            'title': r['query_title'],
            'success': r['success'],
            'execution_time': r['execution_time'],
            'row_count': r['row_count'],
            'column_count': r['column_count'],
            'columns': r['columns']
        }
        if not r['success']:
            query_report['error'] = r['error']
        
        report_data['queries'].append(query_report)
    
    # Save report
    report_file = output_dir / f'{db_num}_comprehensive_report.json'
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"✅ Report saved: {report_file}")
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"SUMMARY FOR {db_name.upper()}")
    print(f"{'='*80}")
    print(f"Total Queries: {total_queries}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/total_queries*100:.1f}%")
    print(f"Average Execution Time: {perf_df['Execution Time (s)'].mean():.3f}s")
    print(f"Total Execution Time: {perf_df['Execution Time (s)'].sum():.3f}s")
    print(f"{'='*80}\n")
    
    return report_data

def main():
    """Test all databases."""
    print("="*80)
    print("COMPREHENSIVE QUERY TESTING - DB-6 TO DB-15")
    print("="*80)
    
    all_reports = []
    
    for db_name in DATABASES:
        db_dir = BASE_DIR / db_name
        
        if not db_dir.exists():
            print(f"⚠️  Skipping {db_name} - directory not found")
            continue
        
        try:
            report = test_database(db_name, db_dir)
            if report:
                all_reports.append(report)
        except Exception as e:
            print(f"❌ Error testing {db_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create consolidated report
    if all_reports:
        consolidated_report = {
            'test_timestamp': datetime.now().isoformat(),
            'total_databases': len(all_reports),
            'databases': all_reports,
            'overall_summary': {
                'total_queries': sum(r['total_queries'] for r in all_reports),
                'total_passed': sum(r['passed'] for r in all_reports),
                'total_failed': sum(r['failed'] for r in all_reports),
                'overall_success_rate': sum(r['passed'] for r in all_reports) / sum(r['total_queries'] for r in all_reports) * 100 if sum(r['total_queries'] for r in all_reports) > 0 else 0,
                'total_execution_time': sum(r['total_execution_time'] for r in all_reports),
                'average_execution_time': sum(r['average_execution_time'] for r in all_reports) / len(all_reports) if all_reports else 0
            }
        }
        
        consolidated_file = BASE_DIR / 'comprehensive_test_results.json'
        with open(consolidated_file, 'w') as f:
            json.dump(consolidated_report, f, indent=2, default=str)
        
        print("\n" + "="*80)
        print("CONSOLIDATED SUMMARY")
        print("="*80)
        print(f"Total Databases Tested: {len(all_reports)}")
        print(f"Total Queries: {consolidated_report['overall_summary']['total_queries']}")
        print(f"Total Passed: {consolidated_report['overall_summary']['total_passed']}")
        print(f"Total Failed: {consolidated_report['overall_summary']['total_failed']}")
        print(f"Overall Success Rate: {consolidated_report['overall_summary']['overall_success_rate']:.1f}%")
        print(f"Total Execution Time: {consolidated_report['overall_summary']['total_execution_time']:.3f}s")
        print(f"Average Execution Time per Query: {consolidated_report['overall_summary']['average_execution_time']:.3f}s")
        print(f"\n✅ Consolidated report saved: {consolidated_file}")
        print("="*80)

if __name__ == '__main__':
    main()
