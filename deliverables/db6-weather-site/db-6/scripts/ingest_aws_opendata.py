#!/usr/bin/env python3
"""
Ingest weather and climate data from AWS Open Data Registry (ASDI)
Supports multiple datasets including NOAA GFS, HRRR, NEXRAD, and others
"""

import json
import boto3
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys

try:
    import databricks.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    print("⚠️  databricks-connector-python not available")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  psycopg2 not available")


class AWSDataIngester:
    """Ingest data from AWS Open Data Registry"""

    # AWS S3 buckets for weather/climate data
    DATA_SOURCES = {
        'noaa_gfs': {
            'bucket': 'noaa-gfs-bdp-pds',
            'description': 'NOAA Global Forecast System (GFS)',
            'prefix': 'gfs.',
            'format': 'grib2',
            'update_frequency': '4x daily (00Z, 06Z, 12Z, 18Z)',
            'forecast_hours': 384,
            'resolution': '0.25 degree (~28km)'
        },
        'noaa_hrrr': {
            'bucket': 'noaa-hrrr-bdp-pds',
            'description': 'NOAA High-Resolution Rapid Refresh (HRRR)',
            'prefix': 'hrrr.',
            'format': 'grib2',
            'update_frequency': 'hourly',
            'forecast_hours': 48,
            'resolution': '3km'
        },
        'noaa_nexrad': {
            'bucket': 'noaa-nexrad-level2',
            'description': 'NEXRAD Level II Radar Data',
            'prefix': '',
            'format': 'binary',
            'update_frequency': 'real-time',
            'forecast_hours': 0,
            'resolution': '1km'
        },
        'noaa_ndfd': {
            'bucket': 'noaa-ndfd-pds',
            'description': 'National Digital Forecast Database',
            'prefix': '',
            'format': 'grib2',
            'update_frequency': '6-hourly',
            'forecast_hours': 192,
            'resolution': '2.5km'
        },
        'noaa_rap': {
            'bucket': 'noaa-rap-pds',
            'description': 'Rapid Refresh (RAP) Model',
            'prefix': 'rap.',
            'format': 'grib2',
            'update_frequency': 'hourly',
            'forecast_hours': 21,
            'resolution': '13km'
        },
        'noaa_gefs': {
            'bucket': 'noaa-gefs-pds',
            'description': 'Global Ensemble Forecast System',
            'prefix': 'gefs.',
            'format': 'grib2',
            'update_frequency': '4x daily',
            'forecast_hours': 384,
            'resolution': '0.5 degree'
        },
        'noaa_rtma': {
            'bucket': 'noaa-rtma-pds',
            'description': 'Real-Time Mesoscale Analysis',
            'prefix': 'rtma.',
            'format': 'grib2',
            'update_frequency': 'hourly',
            'forecast_hours': 0,
            'resolution': '2.5km'
        }
    }

    def __init__(self, db_type='databricks'):
        self.db_type = db_type
        self.s3_client = boto3.client('s3', region_name='us-east-1')
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent.parent.parent

    def get_db_connection(self):
        """Get database connection"""
        if self.db_type == 'databricks':
            return self._get_databricks_connection()
        elif self.db_type == 'postgresql':
            return self._get_postgres_connection()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _get_databricks_connection(self):
        """Get Databricks connection"""
        if not SNOWFLAKE_AVAILABLE:
            return None

        creds_file = self.root_dir / 'results' / 'databricks_credentials.json'
        if not creds_file.exists():
            print(f"❌ Credentials file not found: {creds_file}")
            return None

        with open(creds_file, 'r') as f:
            creds = json.load(f)

        account = creds.get('databricks_account', '')
        user = creds.get('databricks_user', '')
        role = creds.get('databricks_role', 'ACCOUNTADMIN')
        token = creds.get('databricks_token', '')

        conn_params = {
            'account': account,
            'user': user,
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            'database': os.getenv('SNOWFLAKE_DATABASE', 'DB6'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC'),
            'role': role
        }

        if token:
            conn_params['password'] = token
        else:
            conn_params['password'] = os.getenv('SNOWFLAKE_PASSWORD', '')

        try:
            conn = databricks.connector.connect(**conn_params)
            return conn
        except Exception as e:
            print(f"❌ Databricks connection failed: {e}")
            return None

    def _get_postgres_connection(self):
        """Get PostgreSQL connection"""
        if not POSTGRES_AVAILABLE:
            return None

        import os
        host = os.getenv('POSTGRES_HOST', '127.0.0.1')
        port = os.getenv('POSTGRES_PORT_DB6', '5437')

        conn_params = {
            'host': host,
            'port': port,
            'database': os.getenv('POSTGRES_DB', 'db6'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'connect_timeout': 10
        }

        try:
            return psycopg2.connect(**conn_params)
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return None

    def list_available_datasets(self, source_key: str) -> List[str]:
        """List available datasets in S3 bucket"""
        if source_key not in self.DATA_SOURCES:
            print(f"❌ Unknown data source: {source_key}")
            return []

        source = self.DATA_SOURCES[source_key]
        bucket = source['bucket']
        prefix = source.get('prefix', '')

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=100
            )

            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            print(f"⚠️  Error listing datasets from {bucket}: {e}")
            return []

    def log_data_source(self, conn, source_key: str, file_path: str,
                       metadata: Dict, status: str = 'Success'):
        """Log data source ingestion"""
        source = self.DATA_SOURCES[source_key]

        log_entry = {
            'source_id': f"{source_key}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'source_name': source['description'],
            'source_type': source_key,
            'bucket_name': source['bucket'],
            'file_path': file_path,
            'format': source['format'],
            'ingestion_timestamp': datetime.now().isoformat(),
            'status': status,
            'metadata': json.dumps(metadata)
        }

        # Insert into data source log table (create if doesn't exist)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS aws_data_source_log (
            source_id VARCHAR(255) PRIMARY KEY,
            source_name VARCHAR(500),
            source_type VARCHAR(100),
            bucket_name VARCHAR(255),
            file_path VARCHAR(1000),
            format VARCHAR(50),
            ingestion_timestamp TIMESTAMP_NTZ,
            status VARCHAR(50),
            metadata VARIANT
        )
        """

        try:
            cursor.execute(create_table_sql)

            # Insert log entry
            insert_sql = """
            INSERT INTO aws_data_source_log
            (source_id, source_name, source_type, bucket_name, file_path,
             format, ingestion_timestamp, status, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(insert_sql, (
                log_entry['source_id'],
                log_entry['source_name'],
                log_entry['source_type'],
                log_entry['bucket_name'],
                log_entry['file_path'],
                log_entry['format'],
                log_entry['ingestion_timestamp'],
                log_entry['status'],
                log_entry['metadata']
            ))

            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"⚠️  Error logging data source: {e}")
            conn.rollback()
            cursor.close()
            return False

    def ingest_gfs_forecast(self, conn, forecast_date: str, cycle: str = '00'):
        """Ingest GFS forecast data"""
        source = self.DATA_SOURCES['noaa_gfs']
        bucket = source['bucket']

        # GFS file naming: gfs.YYYYMMDD/HH/atmos/gfs.tHHz.pgrb2.0p25.fFFF
        prefix = f"gfs.{forecast_date}/{cycle}/atmos/"

        print(f"📥 Ingesting GFS data from {bucket}/{prefix}")

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=50
            )

            if 'Contents' not in response:
                print(f"  ⚠️  No files found for {forecast_date}/{cycle}")
                return []

            ingested_files = []
            for obj in response['Contents']:
                file_key = obj['Key']
                if file_key.endswith('.idx'):
                    continue  # Skip index files

                metadata = {
                    'file_size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'forecast_date': forecast_date,
                    'cycle': cycle
                }

                # Log the ingestion
                self.log_data_source(conn, 'noaa_gfs', file_key, metadata, 'Success')
                ingested_files.append(file_key)

            print(f"  ✅ Ingested {len(ingested_files)} GFS files")
            return ingested_files

        except Exception as e:
            print(f"  ❌ Error ingesting GFS data: {e}")
            return []

    def ingest_hrrr_forecast(self, conn, forecast_date: str, cycle: str = '00'):
        """Ingest HRRR forecast data"""
        source = self.DATA_SOURCES['noaa_hrrr']
        bucket = source['bucket']

        # HRRR file naming: hrrr.YYYYMMDD/conus/hrrr.tHHz.wrfprsfFF.grib2
        prefix = f"hrrr.{forecast_date}/conus/"

        print(f"📥 Ingesting HRRR data from {bucket}/{prefix}")

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=50
            )

            if 'Contents' not in response:
                print(f"  ⚠️  No files found for {forecast_date}/{cycle}")
                return []

            ingested_files = []
            for obj in response['Contents']:
                file_key = obj['Key']
                if 'wrfprs' not in file_key:
                    continue  # Focus on pressure level files

                metadata = {
                    'file_size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'forecast_date': forecast_date,
                    'cycle': cycle
                }

                self.log_data_source(conn, 'noaa_hrrr', file_key, metadata, 'Success')
                ingested_files.append(file_key)

            print(f"  ✅ Ingested {len(ingested_files)} HRRR files")
            return ingested_files

        except Exception as e:
            print(f"  ❌ Error ingesting HRRR data: {e}")
            return []


def main():
    """Main execution"""
    print("="*70)
    print("AWS OPEN DATA REGISTRY INGESTION FOR DB-6")
    print("="*70)

    ingester = AWSDataIngester(db_type='databricks')
    conn = ingester.get_db_connection()

    if not conn:
        print("❌ Database connection failed")
        return

    try:
        # Get today's date and yesterday for recent forecasts
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        dates_to_ingest = [
            yesterday.strftime('%Y%m%d'),
            today.strftime('%Y%m%d')
        ]

        cycles = ['00', '06', '12', '18']

        print(f"\n📊 Available data sources:")
        for key, source in ingester.DATA_SOURCES.items():
            print(f"  • {key}: {source['description']}")
            print(f"    Bucket: {source['bucket']}")
            print(f"    Resolution: {source['resolution']}")
            print(f"    Update: {source['update_frequency']}")

        print(f"\n📥 Ingesting recent forecasts...")

        total_ingested = 0
        for date_str in dates_to_ingest:
            for cycle in cycles:
                # Ingest GFS
                files = ingester.ingest_gfs_forecast(conn, date_str, cycle)
                total_ingested += len(files)

                # Ingest HRRR (only 00Z cycle typically)
                if cycle == '00':
                    files = ingester.ingest_hrrr_forecast(conn, date_str, cycle)
                    total_ingested += len(files)

        print(f"\n✅ Total files ingested: {total_ingested}")
        print(f"\n📋 Data source log table created/updated")
        print(f"   Query: SELECT * FROM aws_data_source_log ORDER BY ingestion_timestamp DESC")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
