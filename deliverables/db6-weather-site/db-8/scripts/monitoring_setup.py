#!/usr/bin/env python3
"""
Monitoring and alerting setup for 30GB data integration
Tracks data loading performance, query execution times, and system metrics
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

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
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMonitor:
    """Monitor database performance and health"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.pg_conn = None
        self.metrics = {
            'monitoring_date': get_est_timestamp(),
            'database': 'db-8',
            'metrics': {}
        }
    
    def connect_postgresql(self) -> bool:
        """Connect to PostgreSQL"""
        if not PG_AVAILABLE:
            return False
        try:
            self.pg_conn = psycopg2.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5432),
                database=self.db_config.get('database', 'db_8_validation'),
                user=self.db_config.get('user', os.environ.get('USER', 'postgres')),
                password=self.db_config.get('password', '')
            )
            return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False
    
    def get_table_sizes(self) -> Dict:
        """Get table sizes"""
        sizes = {}
        
        if not self.pg_conn:
            return sizes
        
        try:
            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            
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
                sizes[row['tablename']] = {
                    'size': row['size'],
                    'size_bytes': row['size_bytes']
                }
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error getting table sizes: {e}")
        
        return sizes
    
    def get_row_counts(self) -> Dict:
        """Get row counts for all tables"""
        counts = {}
        
        tables = [
            'user_profiles', 'companies', 'job_postings', 'skills',
            'job_skills_requirements', 'user_skills', 'job_applications',
            'job_recommendations', 'market_trends', 'job_market_analytics',
            'data_source_metadata', 'user_job_search_history'
        ]
        
        if not self.pg_conn:
            return counts
        
        try:
            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cursor.fetchone()
                    counts[table] = result['count'] if result else 0
                except Exception as e:
                    logger.warning(f"Error counting rows in {table}: {e}")
                    counts[table] = -1
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error getting row counts: {e}")
        
        return counts
    
    def get_index_usage(self) -> Dict:
        """Get index usage statistics"""
        usage = {}
        
        if not self.pg_conn:
            return usage
        
        try:
            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as index_scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
                LIMIT 50
            """)
            
            for row in cursor.fetchall():
                key = f"{row['tablename']}.{row['indexname']}"
                usage[key] = {
                    'scans': row['index_scans'],
                    'tuples_read': row['tuples_read'],
                    'tuples_fetched': row['tuples_fetched']
                }
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error getting index usage: {e}")
        
        return usage
    
    def get_slow_queries(self) -> List[Dict]:
        """Get slow query statistics (if pg_stat_statements enabled)"""
        slow_queries = []
        
        if not self.pg_conn:
            return slow_queries
        
        try:
            cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
            
            # Check if pg_stat_statements is available
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                ) as extension_exists
            """)
            
            if cursor.fetchone()['extension_exists']:
                cursor.execute("""
                    SELECT 
                        query,
                        calls,
                        total_exec_time,
                        mean_exec_time,
                        max_exec_time
                    FROM pg_stat_statements
                    WHERE mean_exec_time > 1000  -- Queries taking > 1 second on average
                    ORDER BY mean_exec_time DESC
                    LIMIT 20
                """)
                
                for row in cursor.fetchall():
                    slow_queries.append({
                        'query': row['query'][:200],  # Truncate long queries
                        'calls': row['calls'],
                        'total_time_ms': round(row['total_exec_time'], 2),
                        'mean_time_ms': round(row['mean_exec_time'], 2),
                        'max_time_ms': round(row['max_exec_time'], 2)
                    })
            
            cursor.close()
            
        except Exception as e:
            logger.warning(f"Error getting slow queries: {e}")
        
        return slow_queries
    
    def collect_metrics(self) -> Dict:
        """Collect all monitoring metrics"""
        if not self.connect_postgresql():
            self.metrics['error'] = 'Failed to connect to database'
            return self.metrics
        
        self.metrics['metrics'] = {
            'table_sizes': self.get_table_sizes(),
            'row_counts': self.get_row_counts(),
            'index_usage': self.get_index_usage(),
            'slow_queries': self.get_slow_queries()
        }
        
        # Calculate totals
        total_rows = sum(v for v in self.metrics['metrics']['row_counts'].values() if v > 0)
        total_size_bytes = sum(v['size_bytes'] for v in self.metrics['metrics']['table_sizes'].values())
        
        self.metrics['summary'] = {
            'total_rows': total_rows,
            'total_size_gb': round(total_size_bytes / (1024**3), 2),
            'total_tables': len(self.metrics['metrics']['table_sizes']),
            'indexes_monitored': len(self.metrics['metrics']['index_usage']),
            'slow_queries_found': len(self.metrics['metrics']['slow_queries'])
        }
        
        if self.pg_conn:
            self.pg_conn.close()
        
        return self.metrics


def main():
    """Main monitoring function"""
    db_config = {
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': int(os.environ.get('PG_PORT', 5432)),
        'database': os.environ.get('PG_DATABASE', 'db_8_validation'),
        'user': os.environ.get('PG_USER', 'postgres'),
        'password': os.environ.get('PG_PASSWORD', '')
    }
    
    monitor = DatabaseMonitor(db_config)
    metrics = monitor.collect_metrics()
    
    # Save metrics
    metrics_file = Path(__file__).parent.parent / 'metadata' / f"monitoring_metrics_{get_est_timestamp()}.json"
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    metrics_file.write_text(json.dumps(metrics, indent=2, default=str, ensure_ascii=False))
    
    # Print summary
    print("\n" + "="*70)
    print("Database Monitoring Metrics")
    print("="*70)
    
    if 'summary' in metrics:
        summary = metrics['summary']
        print(f"Total Rows: {summary['total_rows']:,}")
        print(f"Total Size: {summary['total_size_gb']} GB")
        print(f"Tables Monitored: {summary['total_tables']}")
        print(f"Indexes Monitored: {summary['indexes_monitored']}")
        print(f"Slow Queries Found: {summary['slow_queries_found']}")
    
    if metrics['metrics'].get('slow_queries'):
        print("\nTop Slow Queries:")
        for i, query in enumerate(metrics['metrics']['slow_queries'][:5], 1):
            print(f"  {i}. Mean: {query['mean_time_ms']}ms, Calls: {query['calls']}")
            print(f"     Query: {query['query'][:100]}...")
    
    print(f"\nMetrics saved to: {metrics_file}")
    print("="*70)


if __name__ == '__main__':
    main()
