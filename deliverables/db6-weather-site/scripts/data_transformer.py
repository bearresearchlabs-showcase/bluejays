#!/usr/bin/env python3
"""
Data Transformer - Transforms extracted raw data into database-ready format
Handles large datasets efficiently with chunking and parallel processing
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import re
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CHUNK_SIZE = 100000  # Process in chunks of 100k rows
MAX_WORKERS = multiprocessing.cpu_count()


class DataTransformer:
    """Transforms raw extracted data into database-ready format."""
    
    def __init__(self, db_name: str, raw_data_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.db_name = db_name
        self.raw_data_dir = raw_data_dir or Path(__file__).parent.parent / db_name / "data" / "raw"
        self.output_dir = output_dir or Path(__file__).parent.parent / db_name / "data" / "transformed"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.output_dir.parent / "transformation_metadata.json"
        self.transformed_files = []
        self.total_rows_processed = 0
        
    def load_extraction_metadata(self) -> Optional[Dict]:
        """Load extraction metadata."""
        metadata_file = self.raw_data_dir.parent / "extraction_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return None
    
    def transform_csv_file(self, file_path: Path, schema: Dict) -> Optional[Path]:
        """Transform a CSV file according to schema."""
        try:
            logger.info(f"Transforming {file_path.name}")
            
            # Read in chunks for large files
            chunks = []
            total_rows = 0
            
            for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE, low_memory=False):
                # Apply transformations
                transformed_chunk = self._apply_transformations(chunk, schema)
                chunks.append(transformed_chunk)
                total_rows += len(chunk)
            
            # Combine chunks
            if chunks:
                df = pd.concat(chunks, ignore_index=True)
                
                # Generate output filename
                output_filename = f"transformed_{file_path.stem}.csv"
                output_path = self.output_dir / output_filename
                
                # Save transformed data
                df.to_csv(output_path, index=False)
                
                logger.info(f"✓ Transformed {total_rows:,} rows: {output_path.name}")
                self.total_rows_processed += total_rows
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error transforming {file_path}: {e}")
            return None
    
    def _apply_transformations(self, df: pd.DataFrame, schema: Dict) -> pd.DataFrame:
        """Apply schema-based transformations."""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values based on schema
        for column, col_schema in schema.get('columns', {}).items():
            if column in df.columns:
                # Type conversion
                if 'type' in col_schema:
                    try:
                        if col_schema['type'] == 'INTEGER':
                            df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                        elif col_schema['type'] == 'NUMERIC':
                            df[column] = pd.to_numeric(df[column], errors='coerce')
                        elif col_schema['type'] == 'TIMESTAMP':
                            df[column] = pd.to_datetime(df[column], errors='coerce')
                        elif col_schema['type'] == 'VARCHAR':
                            df[column] = df[column].astype(str)
                    except Exception as e:
                        logger.warning(f"Error converting {column}: {e}")
                
                # Handle nulls
                if col_schema.get('nullable', True) == False:
                    df = df.dropna(subset=[column])
        
        return df
    
    def extract_html_metadata(self, html_path: Path) -> Dict:
        """Extract structured metadata from HTML files."""
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            metadata = {
                'file_name': html_path.name,
                'title': '',
                'description': '',
                'keywords': [],
                'url': '',
                'dataset_name': ''
            }
            
            if BS4_AVAILABLE:
                soup = BeautifulSoup(content, 'html.parser')
                # Extract title
                title_tag = soup.find('title')
                if title_tag:
                    metadata['title'] = title_tag.get_text(strip=True)
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    metadata['description'] = meta_desc.get('content', '')
                
                # Extract keywords
                meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                if meta_keywords:
                    keywords = meta_keywords.get('content', '')
                    metadata['keywords'] = [k.strip() for k in keywords.split(',') if k.strip()]
                
                # Extract canonical URL
                canonical = soup.find('link', attrs={'rel': 'canonical'})
                if canonical:
                    metadata['url'] = canonical.get('href', '')
            else:
                # Fallback: regex extraction
                title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                if title_match:
                    metadata['title'] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                
                desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
                if desc_match:
                    metadata['description'] = desc_match.group(1)
            
            # Extract dataset name from filename
            filename_lower = html_path.name.lower()
            if 'ais' in filename_lower or 'vessel' in filename_lower:
                metadata['dataset_name'] = 'AIS Vessel Tracking'
            elif 'port' in filename_lower:
                metadata['dataset_name'] = 'Port Data'
            elif 'maritime' in filename_lower or 'shipping' in filename_lower:
                metadata['dataset_name'] = 'Maritime Shipping'
            else:
                metadata['dataset_name'] = 'Maritime Data'
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Error extracting HTML metadata from {html_path.name}: {e}")
            return {'file_name': html_path.name, 'error': str(e)}
    
    def transform_html_files(self) -> pd.DataFrame:
        """Transform HTML files into structured data."""
        logger.info("Processing HTML metadata files...")
        
        html_files = list(self.raw_data_dir.glob("*.html")) + list(self.raw_data_dir.glob("*.json"))[:100]  # Process first 100
        
        metadata_list = []
        for html_file in html_files:
            # Check if file is actually HTML
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.read(200).lower()
                    if '<html' in first_line or '<!doctype' in first_line:
                        metadata = self.extract_html_metadata(html_file)
                        metadata_list.append(metadata)
            except Exception as e:
                continue
        
        if metadata_list:
            df = pd.DataFrame(metadata_list)
            logger.info(f"✓ Extracted metadata from {len(metadata_list)} HTML files")
            return df
        return pd.DataFrame()
    
    def transform_extraction_metadata(self) -> pd.DataFrame:
        """Transform extraction metadata into structured format."""
        metadata_file = self.raw_data_dir.parent / "extraction_metadata.json"
        if not metadata_file.exists():
            return pd.DataFrame()
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Extract file information
            files_data = []
            for item in metadata.get('extracted_data', []):
                files_data.append({
                    'source': item.get('source', ''),
                    'dataset': item.get('dataset', ''),
                    'resource': item.get('resource', ''),
                    'url': item.get('url', ''),
                    'file_path': item.get('file', ''),
                    'size_bytes': item.get('size_bytes', 0),
                    'extracted_at': item.get('extracted_at', '')
                })
            
            if files_data:
                df = pd.DataFrame(files_data)
                logger.info(f"✓ Processed {len(files_data)} extraction metadata entries")
                return df
        except Exception as e:
            logger.error(f"Error processing extraction metadata: {e}")
        
        return pd.DataFrame()
    
    def transform_maritime_data(self):
        """Transform maritime shipping data for db-7."""
        logger.info("Transforming maritime data...")
        
        # Process extraction metadata
        extraction_df = self.transform_extraction_metadata()
        if not extraction_df.empty:
            output_path = self.output_dir / "transformed_extraction_metadata.csv"
            extraction_df.to_csv(output_path, index=False)
            self.transformed_files.append(str(output_path))
            self.total_rows_processed += len(extraction_df)
            logger.info(f"✓ Saved extraction metadata: {len(extraction_df)} rows")
        
        # Process HTML metadata files
        html_df = self.transform_html_files()
        if not html_df.empty:
            output_path = self.output_dir / "transformed_html_metadata.csv"
            html_df.to_csv(output_path, index=False)
            self.transformed_files.append(str(output_path))
            self.total_rows_processed += len(html_df)
            logger.info(f"✓ Saved HTML metadata: {len(html_df)} rows")
        
        # Process CSV files if any
        schemas = {
            'vessel_tracking': {
                'columns': {
                    'tracking_id': {'type': 'VARCHAR', 'nullable': False},
                    'vessel_id': {'type': 'VARCHAR', 'nullable': False},
                    'timestamp': {'type': 'TIMESTAMP', 'nullable': False},
                    'latitude': {'type': 'NUMERIC', 'nullable': False},
                    'longitude': {'type': 'NUMERIC', 'nullable': False},
                    'speed_knots': {'type': 'NUMERIC', 'nullable': True},
                    'course_degrees': {'type': 'NUMERIC', 'nullable': True}
                }
            },
            'ports': {
                'columns': {
                    'port_id': {'type': 'VARCHAR', 'nullable': False},
                    'port_name': {'type': 'VARCHAR', 'nullable': False},
                    'latitude': {'type': 'NUMERIC', 'nullable': False},
                    'longitude': {'type': 'NUMERIC', 'nullable': False},
                    'country': {'type': 'VARCHAR', 'nullable': True}
                }
            }
        }
        
        for file_path in self.raw_data_dir.glob("*.csv"):
            if 'ais' in file_path.name.lower() or 'vessel' in file_path.name.lower():
                schema = schemas.get('vessel_tracking', {})
                self.transform_csv_file(file_path, schema)
            elif 'port' in file_path.name.lower():
                schema = schemas.get('ports', {})
                self.transform_csv_file(file_path, schema)
    
    def transform_shipping_data(self):
        """Transform shipping/logistics data for db-9."""
        logger.info("Transforming shipping data...")
        
        schemas = {
            'shipping_rates': {
                'columns': {
                    'rate_id': {'type': 'VARCHAR', 'nullable': False},
                    'carrier': {'type': 'VARCHAR', 'nullable': False},
                    'service_type': {'type': 'VARCHAR', 'nullable': False},
                    'rate': {'type': 'NUMERIC', 'nullable': False}
                }
            },
            'trade_data': {
                'columns': {
                    'trade_id': {'type': 'VARCHAR', 'nullable': False},
                    'commodity': {'type': 'VARCHAR', 'nullable': True},
                    'value': {'type': 'NUMERIC', 'nullable': True},
                    'quantity': {'type': 'NUMERIC', 'nullable': True}
                }
            }
        }
        
        for file_path in self.raw_data_dir.glob("*.csv"):
            if 'trade' in file_path.name.lower() or 'census' in file_path.name.lower():
                schema = schemas.get('trade_data', {})
                self.transform_csv_file(file_path, schema)
    
    def transform_parking_data(self):
        """Transform parking intelligence data for db-11."""
        logger.info("Transforming parking data...")
        
        schemas = {
            'parking_facilities': {
                'columns': {
                    'facility_id': {'type': 'VARCHAR', 'nullable': False},
                    'facility_name': {'type': 'VARCHAR', 'nullable': False},
                    'latitude': {'type': 'NUMERIC', 'nullable': True},
                    'longitude': {'type': 'NUMERIC', 'nullable': True},
                    'spaces': {'type': 'INTEGER', 'nullable': True}
                }
            },
            'demographics': {
                'columns': {
                    'geography_id': {'type': 'VARCHAR', 'nullable': False},
                    'population': {'type': 'INTEGER', 'nullable': True},
                    'year': {'type': 'INTEGER', 'nullable': False}
                }
            }
        }
        
        for file_path in self.raw_data_dir.glob("*.csv"):
            if 'parking' in file_path.name.lower():
                schema = schemas.get('parking_facilities', {})
                self.transform_csv_file(file_path, schema)
            elif 'census' in file_path.name.lower() or 'demographic' in file_path.name.lower():
                schema = schemas.get('demographics', {})
                self.transform_csv_file(file_path, schema)
    
    def save_metadata(self):
        """Save transformation metadata."""
        metadata = {
            'database': self.db_name,
            'transformation_date': datetime.now().isoformat(),
            'total_files_transformed': len(self.transformed_files),
            'total_rows_processed': self.total_rows_processed,
            'transformed_files': self.transformed_files
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✓ Metadata saved: {self.metadata_file}")
        logger.info(f"Total rows processed: {self.total_rows_processed:,}")
    
    def run_transformation(self):
        """Run data transformation."""
        logger.info(f"Starting data transformation for {self.db_name}")
        
        if self.db_name == 'db-7':
            self.transform_maritime_data()
        elif self.db_name == 'db-9':
            self.transform_shipping_data()
        elif self.db_name == 'db-11':
            self.transform_parking_data()
        else:
            logger.error(f"Unknown database: {self.db_name}")
        
        self.save_metadata()
        logger.info(f"✓ Transformation complete: {self.total_rows_processed:,} rows processed")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Transformer')
    parser.add_argument('db_name', choices=['db-7', 'db-9', 'db-11'], help='Database name')
    parser.add_argument('--raw-dir', type=str, help='Raw data directory')
    parser.add_argument('--output-dir', type=str, help='Output directory')
    
    args = parser.parse_args()
    
    raw_dir = Path(args.raw_dir) if args.raw_dir else None
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    transformer = DataTransformer(args.db_name, raw_dir, output_dir)
    transformer.run_transformation()


if __name__ == '__main__':
    main()
