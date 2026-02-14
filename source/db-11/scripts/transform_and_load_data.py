#!/usr/bin/env python3
"""
Transform and Load Data Script for db-11 Parking Intelligence Database
Transforms extracted raw data into database-ready format and loads into PostgreSQL/Databricks
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Geospatial libraries
try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon
    from shapely import wkt
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    print("Warning: geopandas/shapely not available")

# Database connections
try:
    import psycopg2
    from psycopg2.extras import execute_values
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

try:
    from databricks import sql
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SCRIPT_DIR = Path(__file__).parent
DB_DIR = SCRIPT_DIR.parent
RESEARCH_DIR = DB_DIR / 'research'
DATA_DIR = DB_DIR / 'data'
METADATA_DIR = DB_DIR / 'metadata'
EXTRACTED_DATA_DIR = RESEARCH_DIR / 'extracted_data'

# Database configuration
PG_CONFIG = {
    'host': os.environ.get('PG_HOST', 'localhost'),
    'port': int(os.environ.get('PG_PORT', 5432)),
    'user': os.environ.get('PG_USER', 'postgres'),
    'password': os.environ.get('PG_PASSWORD', ''),
    'database': os.environ.get('PG_DATABASE', 'db_11_validation')
}

DATABRICKS_CONFIG = {
    'server_hostname': os.environ.get('DATABRICKS_SERVER_HOSTNAME'),
    'http_path': os.environ.get('DATABRICKS_HTTP_PATH'),
    'token': os.environ.get('DATABRICKS_TOKEN')
}

def load_extraction_metadata() -> Dict:
    """Load extraction metadata"""
    metadata_file = METADATA_DIR / 'data_extraction_metadata.json'
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return {}

def transform_data_gov_parking(files: List[str]) -> pd.DataFrame:
    """Transform Data.gov parking facility data"""
    logger.info("Transforming Data.gov parking data...")
    
    all_facilities = []
    
    for file_path in files:
        file_path = Path(file_path)
        if not file_path.exists():
            continue
        
        try:
            # Try different formats
            if file_path.suffix.lower() == '.json':
                df = pd.read_json(file_path)
            elif file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() == '.geojson':
                if GEOSPATIAL_AVAILABLE:
                    gdf = gpd.read_file(file_path)
                    df = pd.DataFrame(gdf.drop(columns='geometry'))
                    # Store geometry separately
                    geometries = gdf.geometry
                else:
                    df = pd.read_json(file_path)
            else:
                continue
            
            # Standardize column names and extract parking facility data
            # This is a simplified transformation - actual implementation would
            # need to handle various city-specific schemas
            
            for _, row in df.iterrows():
                facility = {
                    'facility_id': f"datagov_{file_path.stem}_{row.name}",
                    'facility_name': str(row.get('name', row.get('facility_name', ''))),
                    'city_id': None,  # Would need geocoding
                    'total_spaces': int(row.get('spaces', row.get('total_spaces', 0)) or 0),
                    'facility_type': str(row.get('type', row.get('facility_type', 'Unknown'))),
                    'latitude': float(row.get('latitude', row.get('lat', 0)) or 0),
                    'longitude': float(row.get('longitude', row.get('lon', row.get('lng', 0))) or 0),
                    'source': 'data_gov'
                }
                all_facilities.append(facility)
        
        except Exception as e:
            logger.warning(f"Error processing {file_path}: {e}")
            continue
    
    return pd.DataFrame(all_facilities)

def transform_census_data(msa_files: List[str], city_files: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Transform Census Bureau data into MSA and city tables"""
    logger.info("Transforming Census data...")
    
    msa_records = []
    city_records = []
    
    # Process MSA files
    for file_path in msa_files:
        file_path = Path(file_path)
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not data or len(data) < 2:
                continue
            
            headers = data[0]
            for row in data[1:]:
                if len(row) < len(headers):
                    continue
                
                record = dict(zip(headers, row))
                msa_records.append({
                    'msa_id': f"MSA_{record.get('metropolitan statistical area/micropolitan statistical area', '')}",
                    'msa_name': '',  # Would need lookup
                    'population_estimate': int(record.get('B01001_001E', 0) or 0),
                    'median_household_income': float(record.get('B19013_001E', 0) or 0),
                    'data_year': int(file_path.stem.split('_')[-2]) if '_' in file_path.stem else datetime.now().year - 1
                })
        except Exception as e:
            logger.warning(f"Error processing MSA file {file_path}: {e}")
    
    # Process city files
    for file_path in city_files:
        file_path = Path(file_path)
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not data or len(data) < 2:
                continue
            
            headers = data[0]
            for row in data[1:]:
                if len(row) < len(headers):
                    continue
                
                record = dict(zip(headers, row))
                city_records.append({
                    'city_id': f"{record.get('state', '')}_{record.get('place', '')}",
                    'city_name': '',  # Would need lookup
                    'state_code': record.get('state', ''),
                    'population': int(record.get('B01001_001E', 0) or 0),
                    'median_household_income': float(record.get('B19013_001E', 0) or 0),
                    'data_year': int(file_path.stem.split('_')[-1]) if '_' in file_path.stem else datetime.now().year - 1
                })
        except Exception as e:
            logger.warning(f"Error processing city file {file_path}: {e}")
    
    return pd.DataFrame(msa_records), pd.DataFrame(city_records)

def load_to_postgresql(table_name: str, df: pd.DataFrame, connection):
    """Load DataFrame to PostgreSQL table"""
    if not PG_AVAILABLE or connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Convert DataFrame to list of tuples
        records = [tuple(row) for row in df.values]
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        
        insert_sql = f"""
            INSERT INTO {table_name} ({columns})
            VALUES {placeholders}
            ON CONFLICT DO NOTHING
        """
        
        execute_values(cursor, insert_sql, records)
        connection.commit()
        cursor.close()
        
        logger.info(f"Loaded {len(df)} records to {table_name}")
        return True
    except Exception as e:
        logger.error(f"Error loading to PostgreSQL {table_name}: {e}")
        connection.rollback()
        return False

def main():
    """Main transformation and loading function"""
    logger.info("="*70)
    logger.info("Data Transformation and Loading - db-11")
    logger.info("="*70)
    
    # Load extraction metadata
    metadata = load_extraction_metadata()
    if not metadata:
        logger.error("No extraction metadata found. Run extract_and_transform_data.py first.")
        return
    
    logger.info(f"Found extraction metadata: {len(metadata.get('files_extracted', []))} files")
    
    # Connect to databases
    pg_conn = None
    if PG_AVAILABLE:
        try:
            pg_conn = psycopg2.connect(**PG_CONFIG)
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.warning(f"Could not connect to PostgreSQL: {e}")
    
    db_conn = None
    if DATABRICKS_AVAILABLE and all(DATABRICKS_CONFIG.values()):
        try:
            db_conn = sql.connect(**DATABRICKS_CONFIG)
            logger.info("Connected to Databricks")
        except Exception as e:
            logger.warning(f"Could not connect to Databricks: {e}")
    
    # Transform and load data
    # 1. Parking facilities from Data.gov
    data_gov_files = [f for f in metadata.get('files_extracted', []) if 'datagov' in f.lower()]
    if data_gov_files:
        facilities_df = transform_data_gov_parking(data_gov_files)
        if not facilities_df.empty:
            logger.info(f"Transformed {len(facilities_df)} parking facilities")
            if pg_conn:
                load_to_postgresql('parking_facilities', facilities_df, pg_conn)
    
    # 2. Census data
    census_msa_files = [f for f in metadata.get('files_extracted', []) if 'census_msa' in f.lower()]
    census_city_files = [f for f in metadata.get('files_extracted', []) if 'census_cities' in f.lower()]
    if census_msa_files or census_city_files:
        msa_df, city_df = transform_census_data(census_msa_files, census_city_files)
        if not msa_df.empty:
            logger.info(f"Transformed {len(msa_df)} MSA records")
            if pg_conn:
                load_to_postgresql('metropolitan_areas', msa_df, pg_conn)
        if not city_df.empty:
            logger.info(f"Transformed {len(city_df)} city records")
            if pg_conn:
                load_to_postgresql('cities', city_df, pg_conn)
    
    # Close connections
    if pg_conn:
        pg_conn.close()
    if db_conn:
        db_conn.close()
    
    logger.info("="*70)
    logger.info("Transformation and loading complete!")
    logger.info("="*70)

if __name__ == '__main__':
    main()
