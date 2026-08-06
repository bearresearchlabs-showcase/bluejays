#!/usr/bin/env python3
"""
Bulk data loading script for 30GB scale
Handles CSV/JSON file loading with batch processing, progress tracking, and error recovery
"""

import os
import sys
import csv
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Iterator
import traceback

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
    from psycopg2.extras import execute_batch, RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False
    print("Warning: psycopg2 not available. PostgreSQL loading will be skipped.")

try:
    from databricks import sql
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False
    print("Warning: databricks-sql-connector not available. Databricks loading will be skipped.")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BulkDataLoader:
    """Bulk data loader with batch processing and error recovery"""
    
    def __init__(self, db_config: Dict, batch_size: int = 10000):
        self.db_config = db_config
        self.batch_size = batch_size
        self.pg_conn = None
        self.db_conn = None
        self.stats = {
            'total_records': 0,
            'loaded_records': 0,
            'failed_records': 0,
            'batches_processed': 0,
            'start_time': None,
            'end_time': None
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
            self.pg_conn.autocommit = False
            logger.info("Connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False
    
    def connect_databricks(self) -> bool:
        """Connect to Databricks"""
        if not DATABRICKS_AVAILABLE:
            return False
        
        try:
            self.db_conn = sql.connect(
                server_hostname=self.db_config.get('server_hostname'),
                http_path=self.db_config.get('http_path'),
                access_token=self.db_config.get('access_token')
            )
            logger.info("Connected to Databricks")
            return True
        except Exception as e:
            logger.error(f"Databricks connection failed: {e}")
            return False
    
    def load_csv_batch(self, csv_file: Path, table_name: str, columns: List[str], 
                      db_type: str = 'postgresql') -> Dict:
        """Load CSV file in batches"""
        result = {
            'file': str(csv_file),
            'table': table_name,
            'total_rows': 0,
            'loaded_rows': 0,
            'failed_rows': 0,
            'errors': []
        }
        
        if not csv_file.exists():
            result['errors'].append(f"File not found: {csv_file}")
            return result
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                batch = []
                
                for row_num, row in enumerate(reader, 1):
                    result['total_rows'] += 1
                    batch.append(row)
                    
                    if len(batch) >= self.batch_size:
                        batch_result = self._load_batch(batch, table_name, columns, db_type)
                        result['loaded_rows'] += batch_result['loaded']
                        result['failed_rows'] += batch_result['failed']
                        result['errors'].extend(batch_result['errors'])
                        batch = []
                        self.stats['batches_processed'] += 1
                        
                        if row_num % (self.batch_size * 10) == 0:
                            logger.info(f"Processed {row_num} rows from {csv_file.name}")
                
                # Load remaining batch
                if batch:
                    batch_result = self._load_batch(batch, table_name, columns, db_type)
                    result['loaded_rows'] += batch_result['loaded']
                    result['failed_rows'] += batch_result['failed']
                    result['errors'].extend(batch_result['errors'])
                    self.stats['batches_processed'] += 1
                
                self.stats['total_records'] += result['total_rows']
                self.stats['loaded_records'] += result['loaded_rows']
                self.stats['failed_records'] += result['failed_rows']
                
        except Exception as e:
            logger.error(f"Error loading CSV {csv_file}: {e}")
            result['errors'].append(str(e))
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def _load_batch(self, batch: List[Dict], table_name: str, columns: List[str], 
                    db_type: str) -> Dict:
        """Load a batch of records"""
        result = {'loaded': 0, 'failed': 0, 'errors': []}
        
        if db_type == 'postgresql' and self.pg_conn:
            try:
                # Prepare INSERT statement
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                
                # Prepare data
                values = []
                for row in batch:
                    row_values = [row.get(col) for col in columns]
                    values.append(row_values)
                
                # Execute batch insert
                cursor = self.pg_conn.cursor()
                execute_batch(cursor, insert_sql, values, page_size=self.batch_size)
                self.pg_conn.commit()
                cursor.close()
                
                result['loaded'] = len(batch)
                
            except Exception as e:
                self.pg_conn.rollback()
                result['failed'] = len(batch)
                result['errors'].append(f"Batch insert failed: {e}")
                logger.error(f"Batch insert error: {e}")
        
        elif db_type == 'databricks' and self.db_conn:
            try:
                # Databricks batch insert
                cursor = self.db_conn.cursor()
                for row in batch:
                    values = [row.get(col) for col in columns]
                    placeholders = ', '.join(['%s'] * len(columns))
                    column_names = ', '.join(columns)
                    insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)
                cursor.close()
                result['loaded'] = len(batch)
                
            except Exception as e:
                result['failed'] = len(batch)
                result['errors'].append(f"Databricks batch insert failed: {e}")
                logger.error(f"Databricks batch insert error: {e}")
        
        return result
    
    def load_json_batch(self, json_file: Path, table_name: str, columns: List[str],
                       db_type: str = 'postgresql') -> Dict:
        """Load JSON file in batches"""
        result = {
            'file': str(json_file),
            'table': table_name,
            'total_rows': 0,
            'loaded_rows': 0,
            'failed_rows': 0,
            'errors': []
        }
        
        if not json_file.exists():
            result['errors'].append(f"File not found: {json_file}")
            return result
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict) and 'records' in data:
                    records = data['records']
                else:
                    result['errors'].append("Invalid JSON format")
                    return result
                
                result['total_rows'] = len(records)
                
                # Process in batches
                for i in range(0, len(records), self.batch_size):
                    batch = records[i:i + self.batch_size]
                    batch_result = self._load_batch(batch, table_name, columns, db_type)
                    result['loaded_rows'] += batch_result['loaded']
                    result['failed_rows'] += batch_result['failed']
                    result['errors'].extend(batch_result['errors'])
                    self.stats['batches_processed'] += 1
                    
                    if (i + self.batch_size) % (self.batch_size * 10) == 0:
                        logger.info(f"Processed {i + self.batch_size} rows from {json_file.name}")
                
                self.stats['total_records'] += result['total_rows']
                self.stats['loaded_records'] += result['loaded_rows']
                self.stats['failed_records'] += result['failed_rows']
                
        except Exception as e:
            logger.error(f"Error loading JSON {json_file}: {e}")
            result['errors'].append(str(e))
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def get_stats(self) -> Dict:
        """Get loading statistics"""
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            self.stats['duration_seconds'] = duration
            if duration > 0:
                self.stats['records_per_second'] = self.stats['loaded_records'] / duration
        return self.stats
    
    def close(self):
        """Close database connections"""
        if self.pg_conn:
            self.pg_conn.close()
        if self.db_conn:
            self.db_conn.close()


def main():
    """Main bulk loading function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk load data into db-8')
    parser.add_argument('--file', type=str, required=True, help='CSV or JSON file to load')
    parser.add_argument('--table', type=str, required=True, help='Target table name')
    parser.add_argument('--columns', type=str, required=True, help='Comma-separated column names')
    parser.add_argument('--batch-size', type=int, default=10000, help='Batch size (default: 10000)')
    parser.add_argument('--db-type', type=str, default='postgresql', choices=['postgresql', 'databricks'],
                       help='Database type')
    parser.add_argument('--host', type=str, help='Database host')
    parser.add_argument('--port', type=int, help='Database port')
    parser.add_argument('--database', type=str, help='Database name')
    parser.add_argument('--user', type=str, help='Database user')
    parser.add_argument('--password', type=str, help='Database password')
    
    args = parser.parse_args()
    
    # Database configuration
    db_config = {
        'host': args.host or os.environ.get('PG_HOST', 'localhost'),
        'port': args.port or int(os.environ.get('PG_PORT', 5432)),
        'database': args.database or os.environ.get('PG_DATABASE', 'db_8_validation'),
        'user': args.user or os.environ.get('PG_USER', 'postgres'),
        'password': args.password or os.environ.get('PG_PASSWORD', ''),
        'server_hostname': os.environ.get('DATABRICKS_SERVER_HOSTNAME'),
        'http_path': os.environ.get('DATABRICKS_HTTP_PATH'),
        'access_token': os.environ.get('DATABRICKS_TOKEN')
    }
    
    # Initialize loader
    loader = BulkDataLoader(db_config, batch_size=args.batch_size)
    loader.stats['start_time'] = datetime.now()
    
    # Connect to database
    if args.db_type == 'postgresql':
        if not loader.connect_postgresql():
            print("Failed to connect to PostgreSQL")
            return
    elif args.db_type == 'databricks':
        if not loader.connect_databricks():
            print("Failed to connect to Databricks")
            return
    
    # Parse columns
    columns = [col.strip() for col in args.columns.split(',')]
    
    # Load file
    file_path = Path(args.file)
    if file_path.suffix.lower() == '.csv':
        result = loader.load_csv_batch(file_path, args.table, columns, args.db_type)
    elif file_path.suffix.lower() == '.json':
        result = loader.load_json_batch(file_path, args.table, columns, args.db_type)
    else:
        print(f"Unsupported file format: {file_path.suffix}")
        return
    
    # Finalize
    loader.stats['end_time'] = datetime.now()
    stats = loader.get_stats()
    loader.close()
    
    # Print results
    print("\n" + "="*70)
    print("Bulk Loading Results")
    print("="*70)
    print(f"File: {result['file']}")
    print(f"Table: {result['table']}")
    print(f"Total Rows: {result['total_rows']:,}")
    print(f"Loaded Rows: {result['loaded_rows']:,}")
    print(f"Failed Rows: {result['failed_rows']:,}")
    print(f"Batches Processed: {stats['batches_processed']}")
    if 'duration_seconds' in stats:
        print(f"Duration: {stats['duration_seconds']:.2f} seconds")
        print(f"Rate: {stats.get('records_per_second', 0):.2f} records/second")
    
    if result['errors']:
        print(f"\nErrors: {len(result['errors'])}")
        for error in result['errors'][:10]:  # Show first 10 errors
            print(f"  - {error}")
    
    print("="*70)


if __name__ == '__main__':
    main()
