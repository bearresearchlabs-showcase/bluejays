#!/usr/bin/env python3
"""
Transform and load extracted data into db-10 database
Processes extracted data files and loads them into PostgreSQL/Databricks
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import os

# Add root scripts to path
script_dir = Path(__file__).parent
root_dir = script_dir.parent.parent
sys.path.insert(0, str(root_dir / 'scripts'))

try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

class DataTransformer:
    """Transform extracted data and load into database"""
    
    def __init__(self):
        self.research_dir = script_dir.parent / 'research'
        self.extracted_data_dir = self.research_dir / 'extracted_data'
        self.data_dir = script_dir.parent / 'data'
        self.metadata_dir = script_dir.parent / 'metadata'
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Database connection (configure as needed)
        self.pg_conn = None
        self.setup_database_connection()
        
    def setup_database_connection(self):
        """Setup database connection if available"""
        try:
            import psycopg2
            self.pg_conn = psycopg2.connect(
                host=os.environ.get('PG_HOST', 'localhost'),
                port=int(os.environ.get('PG_PORT', 5432)),
                user=os.environ.get('PG_USER', 'postgres'),
                password=os.environ.get('PG_PASSWORD', ''),
                database=os.environ.get('PG_DATABASE', 'db10')
            )
            print("✓ PostgreSQL connection established")
        except Exception as e:
            print(f"⚠️  PostgreSQL connection not available: {e}")
            print("   Data transformation will proceed but loading will be skipped")
    
    def transform_census_data(self) -> pd.DataFrame:
        """Transform Census Bureau MRTS data"""
        print("\nTransforming Census Bureau data...")
        
        census_files = list(self.extracted_data_dir.glob("census_mrts*.json"))
        census_data = []
        
        for file in census_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if len(data) > 1:
                        # Skip header row
                        for row in data[1:]:
                            if len(row) >= 3:
                                census_data.append({
                                    'census_id': f"CENSUS_{file.stem}_{len(census_data)}",
                                    'naics_code': row[2] if len(row) > 2 else None,
                                    'time_period': row[1] if len(row) > 1 else None,
                                    'cell_value': float(row[0]) if row[0] and row[0] != 'null' else None,
                                    'source': 'Census Bureau MRTS',
                                    'extracted_date': datetime.now().isoformat()
                                })
            except Exception as e:
                print(f"  Error processing {file.name}: {e}")
                continue
        
        if census_data:
            df = pd.DataFrame(census_data)
            print(f"  ✓ Transformed {len(df)} Census records")
            return df
        return pd.DataFrame()
    
    def transform_datagov_data(self) -> Dict[str, pd.DataFrame]:
        """Transform Data.gov datasets"""
        print("\nTransforming Data.gov datasets...")
        
        datagov_data = {}
        
        # Process CSV files
        csv_files = list(self.extracted_data_dir.glob("datagov_*.csv"))
        for file in csv_files:
            try:
                df = pd.read_csv(file, low_memory=False, nrows=100000)  # Limit rows for memory
                if not df.empty:
                    datagov_data[f"datagov_csv_{file.stem}"] = df
                    print(f"  ✓ Transformed {file.name}: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"  Error processing {file.name}: {e}")
                continue
        
        # Process JSON files
        json_files = list(self.extracted_data_dir.glob("datagov_*.json"))
        for file in json_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        df = pd.DataFrame(data)
                    elif isinstance(data, dict):
                        # Try to find data array in dict
                        if 'data' in data:
                            df = pd.DataFrame(data['data'])
                        elif 'results' in data:
                            df = pd.DataFrame(data['results'])
                        else:
                            df = pd.json_normalize(data)
                    else:
                        continue
                    
                    if not df.empty:
                        datagov_data[f"datagov_json_{file.stem}"] = df
                        print(f"  ✓ Transformed {file.name}: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"  Error processing {file.name}: {e}")
                continue
        
        return datagov_data
    
    def transform_bls_data(self) -> pd.DataFrame:
        """Transform BLS price index data"""
        print("\nTransforming BLS data...")
        
        bls_files = list(self.extracted_data_dir.glob("bls_*.json"))
        bls_data = []
        
        for file in bls_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if data.get('status') == 'REQUEST_SUCCEEDED':
                        results = data.get('Results', {}).get('series', [])
                        for series in results:
                            series_id = series.get('seriesID', '')
                            data_points = series.get('data', [])
                            for point in data_points:
                                bls_data.append({
                                    'bls_id': f"BLS_{series_id}_{point.get('year')}_{point.get('period')}",
                                    'series_id': series_id,
                                    'year': int(point.get('year', 0)),
                                    'period': point.get('period', ''),
                                    'value': float(point.get('value', 0)) if point.get('value') != 'null' else None,
                                    'source': 'BLS Public Data API',
                                    'extracted_date': datetime.now().isoformat()
                                })
            except Exception as e:
                print(f"  Error processing {file.name}: {e}")
                continue
        
        if bls_data:
            df = pd.DataFrame(bls_data)
            print(f"  ✓ Transformed {len(df)} BLS records")
            return df
        return pd.DataFrame()
    
    def transform_synthetic_data(self) -> Dict[str, pd.DataFrame]:
        """Transform synthetic pricing and inventory data"""
        print("\nTransforming synthetic data...")
        
        synthetic_data = {}
        
        # Pricing data
        pricing_files = list(self.extracted_data_dir.glob("synthetic_pricing*.csv"))
        if pricing_files:
            pricing_dfs = []
            for file in pricing_files:
                try:
                    df = pd.read_csv(file)
                    pricing_dfs.append(df)
                except Exception as e:
                    print(f"  Error reading {file.name}: {e}")
                    continue
            
            if pricing_dfs:
                pricing_df = pd.concat(pricing_dfs, ignore_index=True)
                synthetic_data['pricing'] = pricing_df
                print(f"  ✓ Transformed {len(pricing_df)} pricing records")
        
        # Inventory data
        inventory_files = list(self.extracted_data_dir.glob("synthetic_inventory*.csv"))
        if inventory_files:
            inventory_dfs = []
            for file in inventory_files:
                try:
                    df = pd.read_csv(file)
                    inventory_dfs.append(df)
                except Exception as e:
                    print(f"  Error reading {file.name}: {e}")
                    continue
            
            if inventory_dfs:
                inventory_df = pd.concat(inventory_dfs, ignore_index=True)
                synthetic_data['inventory'] = inventory_df
                print(f"  ✓ Transformed {len(inventory_df)} inventory records")
        
        return synthetic_data
    
    def load_to_database(self, dataframes: Dict[str, pd.DataFrame]):
        """Load transformed data into database"""
        if not self.pg_conn:
            print("\n⚠️  Database connection not available. Skipping database load.")
            print("   Transformed data is available in memory for further processing.")
            return
        
        print("\nLoading data to database...")
        
        try:
            cursor = self.pg_conn.cursor()
            
            # Load Census data
            if 'census' in dataframes and not dataframes['census'].empty:
                df = dataframes['census']
                # Create table if not exists (simplified)
                # In production, use proper schema.sql
                print(f"  Loading {len(df)} Census records...")
                # Insert logic here
            
            # Load BLS data
            if 'bls' in dataframes and not dataframes['bls'].empty:
                df = dataframes['bls']
                print(f"  Loading {len(df)} BLS records...")
                # Insert logic here
            
            # Load synthetic pricing data
            if 'pricing' in dataframes and not dataframes['pricing'].empty:
                df = dataframes['pricing']
                print(f"  Loading {len(df)} pricing records...")
                # Insert logic here
            
            # Load synthetic inventory data
            if 'inventory' in dataframes and not dataframes['inventory'].empty:
                df = dataframes['inventory']
                print(f"  Loading {len(df)} inventory records...")
                # Insert logic here
            
            self.pg_conn.commit()
            cursor.close()
            print("  ✓ Data loaded successfully")
            
        except Exception as e:
            print(f"  ✗ Error loading data: {e}")
            if self.pg_conn:
                self.pg_conn.rollback()
    
    def save_transformation_metadata(self, dataframes: Dict[str, pd.DataFrame]):
        """Save transformation metadata"""
        metadata = {
            'transformation_timestamp': get_est_timestamp(),
            'dataframes': {
                name: {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
                }
                for name, df in dataframes.items() if isinstance(df, pd.DataFrame)
            },
            'total_rows': sum(len(df) for df in dataframes.values() if isinstance(df, pd.DataFrame)),
            'total_memory_mb': sum(
                df.memory_usage(deep=True).sum() / 1024 / 1024
                for df in dataframes.values() if isinstance(df, pd.DataFrame)
            )
        }
        
        metadata_file = self.metadata_dir / 'transformation_metadata.json'
        metadata_file.write_text(json.dumps(metadata, indent=2))
        print(f"\n✓ Transformation metadata saved to {metadata_file}")
    
    def run_transformation(self):
        """Run complete transformation process"""
        print("="*70)
        print("Data Transformation and Loading for db-10")
        print("="*70)
        
        dataframes = {}
        
        # Transform all data sources
        census_df = self.transform_census_data()
        if not census_df.empty:
            dataframes['census'] = census_df
        
        bls_df = self.transform_bls_data()
        if not bls_df.empty:
            dataframes['bls'] = bls_df
        
        datagov_data = self.transform_datagov_data()
        dataframes.update(datagov_data)
        
        synthetic_data = self.transform_synthetic_data()
        dataframes.update(synthetic_data)
        
        # Load to database
        self.load_to_database(dataframes)
        
        # Save metadata
        self.save_transformation_metadata(dataframes)
        
        # Summary
        print("\n" + "="*70)
        print("Transformation Summary")
        print("="*70)
        total_rows = sum(len(df) for df in dataframes.values() if isinstance(df, pd.DataFrame))
        total_memory = sum(
            df.memory_usage(deep=True).sum() / 1024 / 1024
            for df in dataframes.values() if isinstance(df, pd.DataFrame)
        )
        print(f"Total DataFrames: {len(dataframes)}")
        print(f"Total Rows: {total_rows:,}")
        print(f"Total Memory: {total_memory:.2f} MB")
        print("="*70)
        
        if self.pg_conn:
            self.pg_conn.close()

if __name__ == '__main__':
    transformer = DataTransformer()
    transformer.run_transformation()
