#!/usr/bin/env python3
"""
Materialized View Refresh Script for db-8
Automates refresh of materialized views for analytics and reporting
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
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
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaterializedViewRefresher:
    """Manages materialized view refreshes"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.pg_conn = None
        self.refresh_results = []
    
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
    
    def get_materialized_views(self) -> List[str]:
        """Get list of materialized views in database"""
        if not self.pg_conn:
            return []
        
        cursor = self.pg_conn.cursor()
        cursor.execute("""
            SELECT schemaname, matviewname 
            FROM pg_matviews 
            WHERE schemaname = 'public'
            ORDER BY matviewname
        """)
        
        views = [f"{row[0]}.{row[1]}" for row in cursor.fetchall()]
        cursor.close()
        
        return views
    
    def refresh_view(self, view_name: str, concurrently: bool = False) -> Dict:
        """Refresh a materialized view"""
        result = {
            'view_name': view_name,
            'status': 'success',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration_seconds': None,
            'error': None
        }
        
        try:
            start_time = datetime.now()
            
            # Build refresh command
            if concurrently:
                # CONCURRENTLY requires unique index on materialized view
                refresh_sql = f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name};"
            else:
                refresh_sql = f"REFRESH MATERIALIZED VIEW {view_name};"
            
            cursor = self.pg_conn.cursor()
            cursor.execute(refresh_sql)
            self.pg_conn.commit()
            cursor.close()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result['end_time'] = end_time.isoformat()
            result['duration_seconds'] = duration
            
            logger.info(f"Refreshed {view_name} in {duration:.2f} seconds")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Failed to refresh {view_name}: {e}")
        
        return result
    
    def refresh_all_views(self, concurrently: bool = False) -> Dict:
        """Refresh all materialized views"""
        views = self.get_materialized_views()
        
        if not views:
            logger.warning("No materialized views found in database")
            return {
                'refresh_date': get_est_timestamp(),
                'views_refreshed': 0,
                'views_failed': 0,
                'total_duration_seconds': 0,
                'results': []
            }
        
        results = {
            'refresh_date': get_est_timestamp(),
            'views_refreshed': 0,
            'views_failed': 0,
            'total_duration_seconds': 0,
            'results': []
        }
        
        start_time = datetime.now()
        
        for view in views:
            result = self.refresh_view(view, concurrently=concurrently)
            results['results'].append(result)
            
            if result['status'] == 'success':
                results['views_refreshed'] += 1
            else:
                results['views_failed'] += 1
        
        end_time = datetime.now()
        results['total_duration_seconds'] = (end_time - start_time).total_seconds()
        
        return results
    
    def save_results(self, results: Dict, output_path: Path):
        """Save refresh results to file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(results, indent=2, default=str))
        logger.info(f"Refresh results saved to {output_path}")


def main():
    """Main refresh function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Refresh materialized views')
    parser.add_argument('--concurrent', action='store_true', help='Use CONCURRENTLY option')
    parser.add_argument('--view', type=str, help='Refresh specific view only')
    
    args = parser.parse_args()
    
    db_config = {
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': int(os.environ.get('PG_PORT', 5432)),
        'database': os.environ.get('PG_DATABASE', 'db_8_validation'),
        'user': os.environ.get('PG_USER', 'postgres'),
        'password': os.environ.get('PG_PASSWORD', '')
    }
    
    refresher = MaterializedViewRefresher(db_config)
    
    if not refresher.connect_postgresql():
        logger.error("Failed to connect to database")
        return
    
    if args.view:
        # Refresh specific view
        result = refresher.refresh_view(args.view, concurrently=args.concurrent)
        results = {
            'refresh_date': get_est_timestamp(),
            'views_refreshed': 1 if result['status'] == 'success' else 0,
            'views_failed': 1 if result['status'] == 'failed' else 0,
            'results': [result]
        }
    else:
        # Refresh all views
        results = refresher.refresh_all_views(concurrently=args.concurrent)
    
    # Save results
    output_path = Path(__file__).parent.parent / 'metadata' / f"materialized_view_refresh_{get_est_timestamp()}.json"
    refresher.save_results(results, output_path)
    
    print("\n" + "="*70)
    print("Materialized View Refresh Results")
    print("="*70)
    print(f"Views Refreshed: {results['views_refreshed']}")
    print(f"Views Failed: {results['views_failed']}")
    print(f"Total Duration: {results['total_duration_seconds']:.2f} seconds")
    print("="*70)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
