#!/usr/bin/env python3
"""
Transform Large Datasets for db-9 Shipping Intelligence Database
Processes downloaded raw datasets and transforms them into database-ready format
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
import zipfile
    try:
    try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    logger.warning('geopandas not available - ZIP boundary transformation will be skipped')
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
from sqlalchemy import create_engine, text

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatasetTransformer:
    """Transform raw datasets into database-ready format"""
    
    def __init__(self, raw_data_dir: Path, output_dir: Path, db_connection_string: Optional[str] = None):
        self.raw_data_dir = raw_data_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_connection_string = db_connection_string
        self.transformed_files = []
        self.total_rows_processed = 0
        
    def transform_census_spi_data(self) -> List[pd.DataFrame]:
        """
        Transform Census Bureau SPI Databank import data
        Maps to international_customs table
        """
        logger.info("="*80)
        logger.info("Transforming Census Bureau SPI Data")
        logger.info("="*80)
        
        census_dir = self.raw_data_dir / "census_spi"
        if not census_dir.exists():
            logger.warning(f"Census SPI directory not found: {census_dir}")
            return []
        
        transformed_dfs = []
        
        # Process all CSV/Excel files in census_spi directory
        for file_path in census_dir.glob("*.csv"):
            try:
                logger.info(f"Processing {file_path.name}...")
                
                # Read CSV in chunks for large files
                chunk_size = 100000
                chunks = []
                
                for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                    # Transform to match international_customs schema
                    transformed_chunk = pd.DataFrame({
                        'customs_id': chunk.index.map(lambda x: f"census_{file_path.stem}_{x}"),
                        'shipment_id': None,  # Will be linked later
                        'htsusa_code': chunk.get('HTSUSA', chunk.get('HTS', None)),
                        'commodity_description': chunk.get('COMMODITY', chunk.get('DESCRIPTION', None)),
                        'country_of_origin': chunk.get('COUNTRY', chunk.get('ORIGIN', None)),
                        'customs_value_usd': pd.to_numeric(chunk.get('VALUE', chunk.get('CUSTOMS_VALUE', 0)), errors='coerce'),
                        'quantity': pd.to_numeric(chunk.get('QUANTITY', chunk.get('QTY', 0)), errors='coerce'),
                        'unit_of_measure': chunk.get('UNIT', chunk.get('UOM', None)),
                        'import_date': pd.to_datetime(chunk.get('DATE', chunk.get('IMPORT_DATE', None)), errors='coerce'),
                        'port_of_entry': chunk.get('PORT', chunk.get('PORT_CODE', None)),
                        'customs_metadata': chunk.to_json(orient='records'),  # Store full record as JSON
                        'created_at': datetime.now()
                    })
                    
                    chunks.append(transformed_chunk)
                    self.total_rows_processed += len(chunk)
                
                if chunks:
                    df = pd.concat(chunks, ignore_index=True)
                    transformed_dfs.append(df)
                    logger.info(f"✓ Transformed {len(df)} rows from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"Transformed {len(transformed_dfs)} Census SPI files, {self.total_rows_processed} total rows")
        return transformed_dfs
    
    def transform_zip_boundaries(self):
        if not GEOPANDAS_AVAILABLE:
            logger.warning('geopandas not available - skipping ZIP boundary transformation')
            return None -> Optional[pd.DataFrame]:
        """
        Transform ZIP code boundary GeoJSON/Shapefiles
        Maps to shipping_zones table (for zone calculations)
        """
        logger.info("="*80)
        logger.info("Transforming ZIP Code Boundaries")
        logger.info("="*80)
        
        zip_dir = self.raw_data_dir / "zip_boundaries"
        if not zip_dir.exists():
            logger.warning(f"ZIP boundaries directory not found: {zip_dir}")
            return None
        
        all_zips = []
        
        # Process ZIP files (Shapefiles)
        for zip_path in zip_dir.glob("*.zip"):
            try:
                logger.info(f"Processing {zip_path.name}...")
                
                # Extract and read Shapefile
                with zipfile.ZipFile(zip_path, 'r') as z:
                    # Find .shp file
                    shp_files = [f for f in z.namelist() if f.endswith('.shp')]
                    if shp_files:
                        # Extract to temp directory
                        temp_dir = zip_dir / "temp"
                        temp_dir.mkdir(exist_ok=True)
                        z.extractall(temp_dir)
                        
                        shp_path = temp_dir / shp_files[0]
                        gdf = gpd.read_file(shp_path)
                        
                        # Transform to DataFrame with ZIP codes
                        df = pd.DataFrame({
                            'zone_id': gdf.index.map(lambda x: f"zip_{zip_path.stem}_{x}"),
                            'carrier_id': None,  # Will be set based on carrier
                            'origin_zip': gdf.get('ZCTA5CE10', gdf.get('ZIP', gdf.get('ZIPCODE', None))),
                            'destination_zip': None,  # Will be calculated
                            'zone_number': None,  # Will be calculated from distance
                            'distance_miles': None,  # Will be calculated
                            'zone_metadata': gdf.geometry.to_json(),  # Store geometry as JSON
                            'created_at': datetime.now()
                        })
                        
                        all_zips.append(df)
                        logger.info(f"✓ Transformed {len(df)} ZIP boundaries from {zip_path.name}")
                        
                        # Cleanup temp files
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
            
            except Exception as e:
                logger.error(f"Error processing {zip_path}: {e}")
        
        # Process GeoJSON files
        for geojson_path in zip_dir.glob("*.geojson"):
            try:
                logger.info(f"Processing {geojson_path.name}...")
                gdf = gpd.read_file(geojson_path)
                
                df = pd.DataFrame({
                    'zone_id': gdf.index.map(lambda x: f"zip_{geojson_path.stem}_{x}"),
                    'carrier_id': None,
                    'origin_zip': gdf.get('ZCTA5CE10', gdf.get('ZIP', gdf.get('ZIPCODE', None))),
                    'destination_zip': None,
                    'zone_number': None,
                    'distance_miles': None,
                    'zone_metadata': gdf.geometry.to_json(),
                    'created_at': datetime.now()
                })
                
                all_zips.append(df)
                logger.info(f"✓ Transformed {len(df)} ZIP boundaries from {geojson_path.name}")
            
            except Exception as e:
                logger.error(f"Error processing {geojson_path}: {e}")
        
        if all_zips:
            combined_df = pd.concat(all_zips, ignore_index=True)
            logger.info(f"Transformed {len(combined_df)} total ZIP boundaries")
            return combined_df
        
        return None
    
    def transform_postal_datasets(self) -> List[pd.DataFrame]:
        """
        Transform postal service datasets
        Maps to various tables (shipping_zones, address_validation_results, etc.)
        """
        logger.info("="*80)
        logger.info("Transforming Postal Service Datasets")
        logger.info("="*80)
        
        postal_dir = self.raw_data_dir / "postal_service"
        if not postal_dir.exists():
            logger.warning(f"Postal service directory not found: {postal_dir}")
            return []
        
        transformed_dfs = []
        
        for file_path in postal_dir.glob("*.csv"):
            try:
                logger.info(f"Processing {file_path.name}...")
                
                # Read CSV
                df = pd.read_csv(file_path, low_memory=False)
                
                # Try to identify dataset type and transform accordingly
                columns_lower = [c.lower() for c in df.columns]
                
                # Address/ZIP data
                if any(col in columns_lower for col in ['zip', 'zipcode', 'postal', 'address']):
                    transformed_df = pd.DataFrame({
                        'validation_id': df.index.map(lambda x: f"postal_{file_path.stem}_{x}"),
                        'input_address': df.get('ADDRESS', df.get('address', None)),
                        'validated_address': df.get('VALIDATED', df.get('validated_address', None)),
                        'zip_code': df.get('ZIP', df.get('ZIPCODE', df.get('zip', None))),
                        'zip_plus_4': df.get('ZIP4', df.get('ZIP_PLUS_4', None)),
                        'city': df.get('CITY', df.get('city', None)),
                        'state': df.get('STATE', df.get('state', None)),
                        'validation_status': 'validated',
                        'validation_metadata': df.to_json(orient='records'),
                        'created_at': datetime.now()
                    })
                    transformed_dfs.append(transformed_df)
                    logger.info(f"✓ Transformed {len(transformed_df)} address records from {file_path.name}")
                
                self.total_rows_processed += len(df)
            
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"Transformed {len(transformed_dfs)} postal datasets, {self.total_rows_processed} total rows")
        return transformed_dfs
    
    def load_to_database(self, dfs: List[pd.DataFrame], table_name: str) -> bool:
        """Load transformed DataFrames to database"""
        if not self.db_connection_string:
            logger.warning("Database connection not configured, skipping database load")
            return False
        
        try:
            engine = create_engine(self.db_connection_string)
            
            for df in dfs:
                if df is not None and not df.empty:
                    df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=10000)
                    logger.info(f"✓ Loaded {len(df)} rows to {table_name}")
            
            return True
        except Exception as e:
            logger.error(f"Error loading to database: {e}")
            return False
    
    def save_transformed_data(self, dfs: List[pd.DataFrame], output_filename: str) -> List[Path]:
        """Save transformed DataFrames to CSV files"""
        saved_files = []
        
        for i, df in enumerate(dfs):
            if df is not None and not df.empty:
                output_path = self.output_dir / f"{output_filename}_{i}.csv"
                df.to_csv(output_path, index=False)
                saved_files.append(output_path)
                logger.info(f"✓ Saved {len(df)} rows to {output_path.name}")
        
        return saved_files

def main():
    """Main transformation function"""
    script_dir = Path(__file__).parent
    db_dir = script_dir.parent
    raw_data_dir = db_dir / "data" / "raw_datasets"
    output_dir = db_dir / "data" / "transformed_datasets"
    
    # Database connection (optional)
    db_connection_string = os.environ.get('POSTGRES_CONNECTION_STRING')
    
    transformer = DatasetTransformer(raw_data_dir, output_dir, db_connection_string)
    
    logger.info("="*80)
    logger.info("Dataset Transformation for db-9 Shipping Intelligence Database")
    logger.info("="*80)
    
    # Transform datasets
    all_transformed = []
    
    # 1. Transform Census SPI data
    logger.info("\n[1/3] Transforming Census SPI Data...")
    census_dfs = transformer.transform_census_spi_data()
    all_transformed.extend(census_dfs)
    transformer.save_transformed_data(census_dfs, "international_customs")
    
    # 2. Transform ZIP boundaries
    logger.info("\n[2/3] Transforming ZIP Boundaries...")
    zip_df = transformer.transform_zip_boundaries()
    if zip_df is not None:
        all_transformed.append(zip_df)
        transformer.save_transformed_data([zip_df], "shipping_zones")
    
    # 3. Transform postal datasets
    logger.info("\n[3/3] Transforming Postal Service Datasets...")
    postal_dfs = transformer.transform_postal_datasets()
    all_transformed.extend(postal_dfs)
    transformer.save_transformed_data(postal_dfs, "address_validation")
    
    # Load to database if connection available
    if db_connection_string:
        logger.info("\nLoading transformed data to database...")
        transformer.load_to_database(census_dfs, "international_customs")
        if zip_df is not None:
            transformer.load_to_database([zip_df], "shipping_zones")
        transformer.load_to_database(postal_dfs, "address_validation_results")
    
    logger.info("\n" + "="*80)
    logger.info("TRANSFORMATION SUMMARY")
    logger.info("="*80)
    logger.info(f"Total DataFrames Transformed: {len(all_transformed)}")
    logger.info(f"Total Rows Processed: {transformer.total_rows_processed:,}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info("="*80)

if __name__ == '__main__':
    main()
