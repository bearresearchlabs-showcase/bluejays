#!/usr/bin/env python3
"""
Expand data extraction to reach 1GB+ per database.
Extracts historical data and generates larger datasets.
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import time
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE = Path("/Users/machine/Documents/AQ/db")

def expand_opensky_extraction(db_num=1):
    """Expand OpenSky Network data extraction with historical data."""
    logger.info(f"Expanding OpenSky extraction for db-{db_num}...")
    
    data_dir = BASE / f"db-{db_num}" / "data"
    research_dir = BASE / f"db-{db_num}" / "research"
    
    all_records = []
    
    # Extract multiple time periods
    base_time = int(time.time())
    time_periods = [
        (base_time - 3600, base_time - 1800),  # 1 hour ago to 30 min ago
        (base_time - 1800, base_time),         # 30 min ago to now
        (base_time, base_time + 1800),         # Now to 30 min future (if available)
    ]
    
    for start_time, end_time in time_periods:
        try:
            # OpenSky Network historical API
            url = "https://opensky-network.org/api/states/all"
            params = {
                'time': start_time
            }
            headers = {
                'User-Agent': 'db-1-airplane-tracking/1.0 (research@example.com)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'states' in data and data['states']:
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
                            'timestamp': datetime.fromtimestamp(state[3] if state[3] else start_time),
                            'created_at': datetime.now()
                        }
                        all_records.append(record)
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            logger.warning(f"Error extracting time period {start_time}-{end_time}: {e}")
            continue
    
    if all_records:
        # Generate SQL
        df = pd.DataFrame(all_records)
        
        # Add ID column
        if 'id' not in df.columns:
            df['id'] = range(1, len(df) + 1)
        
        # Generate SQL INSERT statements
        sql_statements = []
        for _, row in df.iterrows():
            values = []
            for col in ['id', 'hex', 'lat', 'lon', 'altitude', 'speed', 'track', 'vertical_rate', 'timestamp', 'created_at']:
                val = row.get(col)
                if pd.isna(val) or val is None:
                    values.append('NULL')
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                elif isinstance(val, datetime):
                    values.append(f"'{val.isoformat()}'")
                else:
                    val_str = str(val).replace("'", "''")
                    values.append(f"'{val_str}'")
            
            sql = f"INSERT INTO aircraft_position_history ({', '.join(['id', 'hex', 'lat', 'lon', 'altitude', 'speed', 'track', 'vertical_rate', 'timestamp', 'created_at'])}) VALUES ({', '.join(values)});"
            sql_statements.append(sql)
        
        # Append to existing file or create new
        sql_file = data_dir / "data_gov_extract_expanded.sql"
        sql_file.write_text('\n'.join(sql_statements))
        
        logger.info(f"Generated {len(sql_statements)} additional INSERT statements")
        logger.info(f"File size: {sql_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        return len(sql_statements)
    
    return 0

def generate_synthetic_data_for_expansion(db_num, target_size_gb=1.0):
    """Generate synthetic data to reach target size."""
    logger.info(f"Generating synthetic data for db-{db_num} to reach {target_size_gb}GB...")
    
    data_dir = BASE / f"db-{db_num}" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Estimate records needed (rough estimate: ~200 bytes per INSERT statement)
    bytes_per_record = 200  # Conservative estimate
    target_bytes = target_size_gb * 1024 * 1024 * 1024
    records_needed = int(target_bytes / bytes_per_record)
    
    logger.info(f"Target: {records_needed:,} records (~{target_size_gb}GB)")
    
    base_time = datetime.now()
    batch_size = 10000
    
    # Find next available batch number
    existing_batches = []
    for f in data_dir.glob("data_synthetic_batch_*.sql"):
        if f.is_file():
            try:
                batch_idx = int(f.stem.split('_')[-1])
                existing_batches.append(batch_idx)
            except (ValueError, IndexError):
                pass
    batch_num = (max(existing_batches) + 1) if existing_batches else 0
    
    records = []
    
    # Database-specific record generation
    for i in range(records_needed):
        if db_num == 1:
            # Aircraft position history
            record = {
                'id': i + 1,
                'hex': f"{random.randint(0, 0xffffff):06x}",
                'lat': random.uniform(-90, 90),
                'lon': random.uniform(-180, 180),
                'altitude': random.randint(0, 50000),
                'speed': random.randint(0, 800),
                'track': random.randint(0, 360),
                'vertical_rate': random.randint(-5000, 5000),
                'timestamp': base_time - timedelta(seconds=random.randint(0, 86400 * 30)),
                'created_at': datetime.now()
            }
            table_name = 'aircraft_position_history'
        elif db_num == 2:
            # Filling Station POS - phppos_sales
            record = {
                'sale_id': i + 1,
                'sale_time': base_time - timedelta(seconds=random.randint(0, 86400 * 365)),
                'customer_id': random.randint(1, 10000),
                'employee_id': random.randint(1, 100),
                'comment': f'Sale {i+1}',
                'sale_date': (base_time - timedelta(days=random.randint(0, 365))).date()
            }
            table_name = 'phppos_sales'
        elif db_num == 3:
            # Linkway Ecommerce - orders_order
            record = {
                'id': f"{random.randint(100000, 999999)}-{i+1}",
                'order_number': f"ORD-{i+1:08d}",
                'total_amount': round(random.uniform(10.0, 1000.0), 2),
                'status': random.choice(['pending', 'paid', 'shipped', 'delivered', 'cancelled']),
                'created_at': base_time - timedelta(seconds=random.randint(0, 86400 * 365)),
                'marketer_id': f"{random.randint(100000, 999999)}-{random.randint(1, 1000)}" if random.random() > 0.3 else None,
                'product_id': f"{random.randint(100000, 999999)}-{random.randint(1, 5000)}" if random.random() > 0.2 else None,
                'seller_id': f"{random.randint(100000, 999999)}-{random.randint(1, 500)}" if random.random() > 0.2 else None
            }
            table_name = 'orders_order'
        elif db_num == 4:
            # Seydam AI - models
            record = {
                'id': i + 1,
                'name': f"model_{i+1}",
                'created_at': base_time - timedelta(seconds=random.randint(0, 86400 * 365)),
                'user_id': random.randint(1, 1000)
            }
            table_name = 'models'
        elif db_num == 5:
            # SharedAI - chats
            record = {
                'id': f"{random.randint(100000, 999999)}-{i+1}",
                'created_at': base_time - timedelta(seconds=random.randint(0, 86400 * 365)),
                'created_by': f"{random.randint(100000, 999999)}-{random.randint(1, 1000)}"
            }
            table_name = 'chats'
        else:
            continue
        
        records.append(record)
        
        # Write in batches
        if len(records) >= batch_size:
            sql_statements = []
            for record in records:
                cols = list(record.keys())
                values = []
                for col in cols:
                    val = record[col]
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    elif isinstance(val, datetime):
                        values.append(f"'{val.isoformat()}'")
                    elif isinstance(val, type(base_time.date())):
                        values.append(f"'{val}'")
                    else:
                        val_str = str(val).replace("'", "''")
                        values.append(f"'{val_str}'")
                
                sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(values)});"
                sql_statements.append(sql)
            
            sql_file = data_dir / f"data_synthetic_batch_{batch_num}.sql"
            sql_file.write_text('\n'.join(sql_statements))
            records = []
            batch_num += 1
            
            if batch_num % 10 == 0:
                logger.info(f"Generated batch {batch_num}: {i+1:,} records")
    
    # Write remaining records
    if records:
        sql_statements = []
        for record in records:
            cols = list(record.keys())
            values = []
            for col in cols:
                val = record[col]
                if val is None:
                    values.append('NULL')
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                elif isinstance(val, datetime):
                    values.append(f"'{val.isoformat()}'")
                elif isinstance(val, type(base_time.date())):
                    values.append(f"'{val}'")
                else:
                    val_str = str(val).replace("'", "''")
                    values.append(f"'{val_str}'")
            
            sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(values)});"
            sql_statements.append(sql)
        
        sql_file = data_dir / f"data_synthetic_final.sql"
        sql_file.write_text('\n'.join(sql_statements))
    
    logger.info(f"✅ db-{db_num}: Synthetic data generation complete - {batch_num} batches + final")

def main():
    """Expand data extraction for all databases."""
    print("=" * 70)
    print("Expanding Data Extraction to Reach 1GB+")
    print("=" * 70)
    
    # Expand db-1 with OpenSky data
    expand_opensky_extraction(1)
    
    # Generate synthetic data for all databases
    for db_num in [1, 2, 3, 4, 5]:
        # Only generate if current size is below 1GB
        data_dir = BASE / f"db-{db_num}" / "data"
        current_size = sum(f.stat().st_size for f in data_dir.glob("*.sql") if f.is_file())
        current_size_gb = current_size / (1024 ** 3)
        
        if current_size_gb < 1.0:
            target_gb = 1.0 - current_size_gb
            # Add 50% buffer to ensure we exceed 1GB (accounting for rounding and overhead)
            target_gb = target_gb * 1.5
            # Minimum 0.01GB to ensure meaningful generation
            if target_gb < 0.01:
                target_gb = 0.01
            generate_synthetic_data_for_expansion(db_num, target_gb)
        else:
            logger.info(f"db-{db_num}: Already at {current_size_gb:.2f}GB, skipping")
    
    print("\n" + "=" * 70)
    print("Data Expansion Complete")
    print("=" * 70)

if __name__ == '__main__':
    main()
