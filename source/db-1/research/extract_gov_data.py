#!/usr/bin/env python3
"""
Extract data from .gov sources for db-1 (Airplane Tracking).
Sources: FAA, BTS, NASA ASRS, OpenSky Network
"""
import requests
import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
RESEARCH_DIR = BASE / "research"

def extract_opensky_data():
    """Extract real-time aircraft states from OpenSky Network API."""
    logger.info("Extracting OpenSky Network data...")
    
    try:
        # OpenSky Network API - States endpoint
        url = "https://opensky-network.org/api/states/all"
        headers = {
            'User-Agent': 'db-1-airplane-tracking/1.0 (research@example.com)'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if 'states' in data and data['states']:
            # Transform to match aircraft_position_history schema
            records = []
            for state in data['states']:
                if state and len(state) >= 17:
                    record = {
                        'hex': state[0] if state[0] else None,
                        'flight': state[1] if state[1] else None,
                        'lat': float(state[5]) if state[5] else None,
                        'lon': float(state[6]) if state[6] else None,
                        'altitude': int(state[7]) if state[7] else None,
                        'speed': int(state[9]) if state[9] else None,
                        'track': int(state[10]) if state[10] else None,
                        'vertical_rate': int(state[11]) if state[11] else None,
                        'timestamp': datetime.fromtimestamp(data.get('time', time.time())),
                        'created_at': datetime.now()
                    }
                    records.append(record)
            
            # Save to CSV for transformation
            df = pd.DataFrame(records)
            output_file = RESEARCH_DIR / "opensky_extract.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"Extracted {len(records)} aircraft states from OpenSky")
            return df
        else:
            logger.warning("No aircraft states returned from OpenSky API")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error extracting OpenSky data: {e}")
        return pd.DataFrame()

def extract_bts_ontime_data():
    """Extract BTS airline on-time performance data."""
    logger.info("Extracting BTS on-time performance data...")
    
    try:
        # BTS TranStats API endpoint
        # Note: This is a simplified example - actual BTS API requires specific parameters
        base_url = "https://www.transtats.bts.gov/DownLoad_Table.asp"
        
        # BTS provides downloadable CSV files
        # For demonstration, we'll create a structure for the data
        # In production, you would download actual CSV files
        
        logger.info("BTS data extraction requires downloading CSV files from transtats.bts.gov")
        logger.info("Sample structure created - implement actual download in production")
        
        # Return empty DataFrame with expected structure
        return pd.DataFrame(columns=[
            'flight_date', 'airline', 'flight_number', 'origin', 'dest',
            'dep_delay', 'arr_delay', 'cancelled', 'diverted'
        ])
        
    except Exception as e:
        logger.error(f"Error extracting BTS data: {e}")
        return pd.DataFrame()

def transform_to_schema(df, table_name='aircraft_position_history'):
    """Transform extracted data to match database schema."""
    logger.info(f"Transforming data for {table_name}...")
    
    if df.empty:
        return df
    
    # Map columns to schema
    if table_name == 'aircraft_position_history':
        # Ensure required columns exist
        required_cols = ['hex', 'lat', 'lon', 'altitude', 'timestamp']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        
        # Ensure data types match schema
        if 'id' not in df.columns:
            df['id'] = range(1, len(df) + 1)
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        if 'created_at' not in df.columns:
            df['created_at'] = datetime.now()
        
        # Select columns matching schema
        schema_cols = ['id', 'hex', 'lat', 'lon', 'altitude', 'speed', 'track', 
                      'vertical_rate', 'timestamp', 'created_at']
        df = df[[col for col in schema_cols if col in df.columns]]
    
    return df

def generate_sql_inserts(df, table_name='aircraft_position_history'):
    """Generate SQL INSERT statements from DataFrame."""
    if df.empty:
        return ""
    
    sql_statements = []
    for _, row in df.iterrows():
        values = []
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                values.append('NULL')
            elif isinstance(val, (int, float)):
                values.append(str(val))
            elif isinstance(val, datetime):
                values.append(f"'{val.isoformat()}'")
            else:
                # Escape single quotes
                val_str = str(val).replace("'", "''")
                values.append(f"'{val_str}'")
        
        sql = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(values)});"
        sql_statements.append(sql)
    
    return '\n'.join(sql_statements)

def main():
    """Main extraction and transformation pipeline."""
    logger.info("=" * 70)
    logger.info("Extracting .gov Data for db-1 (Airplane Tracking)")
    logger.info("=" * 70)
    
    # Extract from OpenSky Network
    opensky_df = extract_opensky_data()
    
    if not opensky_df.empty:
        # Transform to schema
        transformed_df = transform_to_schema(opensky_df, 'aircraft_position_history')
        
        # Generate SQL
        sql_output = generate_sql_inserts(transformed_df, 'aircraft_position_history')
        
        # Save SQL to file
        sql_file = DATA_DIR / "data_gov_extract.sql"
        sql_file.write_text(sql_output)
        logger.info(f"Generated {len(transformed_df)} SQL INSERT statements")
        logger.info(f"SQL saved to: {sql_file}")
    
    # Extract BTS data (structure only - implement actual download)
    bts_df = extract_bts_ontime_data()
    
    logger.info("=" * 70)
    logger.info("Extraction complete")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
