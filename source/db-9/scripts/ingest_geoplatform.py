#!/usr/bin/env python3
"""
Ingest geospatial data from geoplatform.gov
Includes boundaries, administrative areas, and geospatial datasets
"""

import json
import requests
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

try:
    import snowflake.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class GeoPlatformIngester:
    """Ingest geospatial data from geoplatform.gov"""

    BASE_URL = "https://www.geoplatform.gov"
    CATALOG_URL = "https://www.geoplatform.gov/api/items"

    def __init__(self, db_type='snowflake'):
        self.db_type = db_type
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WeatherConsultingService/1.0',
            'Accept': 'application/json'
        })
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent.parent.parent

    def get_db_connection(self):
        """Get database connection"""
        if self.db_type == 'snowflake':
            return self._get_snowflake_connection()
        elif self.db_type == 'postgresql':
            return self._get_postgres_connection()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _get_snowflake_connection(self):
        """Get Snowflake connection"""
        if not SNOWFLAKE_AVAILABLE:
            return None

        creds_file = self.root_dir / 'results' / 'snowflake_credentials.json'
        if not creds_file.exists():
            return None

        with open(creds_file, 'r') as f:
            creds = json.load(f)

        account = creds.get('snowflake_account', '')
        user = creds.get('snowflake_user', '')
        role = creds.get('snowflake_role', 'ACCOUNTADMIN')
        token = creds.get('snowflake_token', '')

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
            return snowflake.connector.connect(**conn_params)
        except Exception as e:
            print(f"❌ Snowflake connection failed: {e}")
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

    def search_datasets(self, query: str, limit: int = 50) -> List[Dict]:
        """Search GeoPlatform catalog"""
        params = {
            'q': query,
            'limit': limit,
            'format': 'json'
        }

        try:
            response = self.session.get(self.CATALOG_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"⚠️  Error searching GeoPlatform: {e}")
            return []

    def ingest_boundary_datasets(self, conn):
        """Ingest boundary datasets relevant to weather"""
        print(f"\n📥 Searching GeoPlatform for boundary datasets...")

        # Search for relevant datasets
        search_terms = [
            'county boundaries',
            'state boundaries',
            'fire zones',
            'marine zones',
            'weather zones',
            'CWA boundaries'
        ]

        cursor = conn.cursor()
        datasets_found = 0

        for term in search_terms:
            datasets = self.search_datasets(term, limit=10)

            for dataset in datasets:
                props = dataset.get('properties', {})
                title = props.get('title', '')
                description = props.get('description', '')
                url = props.get('url', '')

                # Log dataset metadata
                log_sql = """
                INSERT INTO geoplatform_dataset_log
                (dataset_id, title, description, url, search_term,
                 ingestion_timestamp, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (dataset_id) DO NOTHING
                """

                dataset_id = props.get('id', f"geoplatform_{hash(url)}")

                try:
                    cursor.execute(log_sql, (
                        dataset_id,
                        title[:500],
                        description[:2000] if description else '',
                        url[:1000] if url else '',
                        term,
                        datetime.now(),
                        'Discovered'
                    ))
                    datasets_found += 1
                except Exception as e:
                    # Table might not exist, create it
                    create_table_sql = """
                    CREATE TABLE IF NOT EXISTS geoplatform_dataset_log (
                        dataset_id VARCHAR(255) PRIMARY KEY,
                        title VARCHAR(500),
                        description VARCHAR(2000),
                        url VARCHAR(1000),
                        search_term VARCHAR(100),
                        ingestion_timestamp TIMESTAMP_NTZ,
                        status VARCHAR(50)
                    )
                    """
                    cursor.execute(create_table_sql)
                    conn.commit()

                    # Retry insert
                    cursor.execute(log_sql, (
                        dataset_id,
                        title[:500],
                        description[:2000] if description else '',
                        url[:1000] if url else '',
                        term,
                        datetime.now(),
                        'Discovered'
                    ))
                    datasets_found += 1

            time.sleep(0.5)  # Rate limiting

        conn.commit()
        cursor.close()
        print(f"  ✅ Found {datasets_found} boundary datasets")
        return datasets_found


def main():
    """Main execution"""
    print("="*70)
    print("GEOPLATFORM.GOV DATA INGESTION FOR DB-6")
    print("="*70)

    ingester = GeoPlatformIngester(db_type='snowflake')
    conn = ingester.get_db_connection()

    if not conn:
        print("❌ Database connection failed")
        return

    try:
        ingester.ingest_boundary_datasets(conn)
        print("\n✅ GeoPlatform ingestion complete")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
