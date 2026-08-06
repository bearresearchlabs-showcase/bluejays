#!/usr/bin/env python3
"""
Master script to ingest data from all sources:
- AWS Open Data Registry (ASDI)
- NWS API (api.weather.gov)
- GeoPlatform.gov
"""

import sys
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from ingest_aws_opendata import AWSDataIngester
from ingest_nws_api import NWSAPIIngester
from ingest_geoplatform import GeoPlatformIngester


def main():
    """Ingest from all data sources"""
    print("="*70)
    print("COMPREHENSIVE DATA INGESTION FOR DB-6")
    print("="*70)
    print("\nSources:")
    print("  1. AWS Open Data Registry (ASDI)")
    print("  2. NWS API (api.weather.gov)")
    print("  3. GeoPlatform.gov")
    print("="*70)

    db_type = 'databricks'  # or 'postgresql'

    # 1. AWS Open Data
    print("\n[1/3] Ingesting AWS Open Data Registry...")
    try:
        aws_ingester = AWSDataIngester(db_type=db_type)
        conn = aws_ingester.get_db_connection()
        if conn:
            # Ingest recent GFS and HRRR forecasts
            from datetime import datetime, timedelta
            today = datetime.now()
            yesterday = today - timedelta(days=1)

            for date_str in [yesterday.strftime('%Y%m%d'), today.strftime('%Y%m%d')]:
                for cycle in ['00', '06', '12', '18']:
                    aws_ingester.ingest_gfs_forecast(conn, date_str, cycle)
                    if cycle == '00':
                        aws_ingester.ingest_hrrr_forecast(conn, date_str, cycle)
            conn.close()
            print("  ✅ AWS ingestion complete")
        else:
            print("  ⚠️  AWS ingestion skipped (no connection)")
    except Exception as e:
        print(f"  ❌ AWS ingestion error: {e}")

    # 2. NWS API
    print("\n[2/3] Ingesting NWS API data...")
    try:
        nws_ingester = NWSAPIIngester(db_type=db_type)
        conn = nws_ingester.get_db_connection()
        if conn:
            nws_ingester.ingest_stations(conn, states=['NY', 'CA', 'IL', 'FL', 'WA', 'TX', 'CO'])
            nws_ingester.ingest_observations(conn)
            conn.close()
            print("  ✅ NWS API ingestion complete")
        else:
            print("  ⚠️  NWS API ingestion skipped (no connection)")
    except Exception as e:
        print(f"  ❌ NWS API ingestion error: {e}")

    # 3. GeoPlatform
    print("\n[3/3] Ingesting GeoPlatform.gov data...")
    try:
        geo_ingester = GeoPlatformIngester(db_type=db_type)
        conn = geo_ingester.get_db_connection()
        if conn:
            geo_ingester.ingest_boundary_datasets(conn)
            conn.close()
            print("  ✅ GeoPlatform ingestion complete")
        else:
            print("  ⚠️  GeoPlatform ingestion skipped (no connection)")
    except Exception as e:
        print(f"  ❌ GeoPlatform ingestion error: {e}")

    print("\n" + "="*70)
    print("DATA INGESTION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Verify data: SELECT COUNT(*) FROM aws_data_source_log")
    print("  2. Check observations: SELECT COUNT(*) FROM weather_observations")
    print("  3. Review datasets: SELECT * FROM geoplatform_dataset_log")


if __name__ == '__main__':
    main()
