#!/usr/bin/env python3
"""
Large-scale data extraction script for db-10 Marketing Intelligence Database
Target: 10-30 GB of data from government APIs and public sources
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add root scripts to path
script_dir = Path(__file__).parent
root_dir = script_dir.parent.parent
sys.path.insert(0, str(root_dir / 'scripts'))

try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

class LargeDataExtractor:
    """Extract 10-30 GB of data from government APIs"""
    
    def __init__(self):
        self.data_dir = script_dir.parent / 'data'
        self.research_dir = script_dir.parent / 'research'
        self.extracted_data_dir = self.research_dir / 'extracted_data'
        self.extracted_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = self._create_session()
        self.total_bytes = 0
        self.records_extracted = 0
        
        # API endpoints
        self.census_mrts_url = "http://api.census.gov/data/timeseries/eits/mrts"
        self.census_mrtsadv_url = "http://api.census.gov/data/timeseries/eits/mrtsadv"
        self.bls_url = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        self.datagov_url = "https://catalog.data.gov/api/3/action"
        
        # Time ranges for 1 GB target - balanced real data extraction
        self.start_year = datetime.now().year - 5  # Last 5 years of data
        self.end_year = datetime.now().year
        
    def _create_session(self):
        """Create requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def extract_census_mrts_data(self) -> int:
        """Extract Census Bureau MRTS data - multiple NAICS codes, extended time range"""
        print("\n" + "="*70)
        print("Extracting Census Bureau MRTS Data")
        print("="*70)
        
        records = 0
        bytes_extracted = 0
        
        # Major retail NAICS codes - reduced for 1 GB target
        naics_codes = [
            "44-45",  # Retail Trade (aggregate)
            "441",    # Motor Vehicle and Parts Dealers
            "443",    # Electronics and Appliance Stores
            "445",    # Food and Beverage Stores
            "448",    # Clothing and Clothing Accessories Stores
            "452",    # General Merchandise Stores
        ]
        
        # Variables to extract
        variables = [
            "cell_value",  # Sales/inventory values
            "time",        # Time period
            "NAICS",       # Industry code
        ]
        
        for naics in naics_codes:
            for year in range(self.start_year, self.end_year + 1):
                for month in range(1, 13):
                    try:
                        params = {
                            "get": ",".join(variables),
                            "for": f"us:*",
                            "NAICS": naics,
                            "time": f"{year}-{month:02d}",
                            "key": ""  # No key required
                        }
                        
                        response = self.session.get(self.census_mrts_url, params=params, timeout=30)
                        response.raise_for_status()
                        data = response.json()
                        
                        if len(data) > 1:  # Has data rows
                            # Save to file
                            filename = f"census_mrts_{naics}_{year}_{month:02d}.json"
                            filepath = self.extracted_data_dir / filename
                            filepath.write_text(json.dumps(data, indent=2))
                            
                            bytes_extracted += len(response.content)
                            records += len(data) - 1  # Exclude header
                            
                            if records % 100 == 0:
                                print(f"  Extracted {records} records ({bytes_extracted / 1024 / 1024:.2f} MB)")
                        
                        # Rate limiting
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"  Error extracting {naics} {year}-{month:02d}: {e}")
                        continue
        
        self.total_bytes += bytes_extracted
        self.records_extracted += records
        print(f"\n✓ Census MRTS: {records} records, {bytes_extracted / 1024 / 1024:.2f} MB")
        return records
    
    def extract_census_mrtsadv_data(self) -> int:
        """Extract Census Bureau Advance Retail Inventories data"""
        print("\n" + "="*70)
        print("Extracting Census Bureau Advance Retail Inventories Data")
        print("="*70)
        
        records = 0
        bytes_extracted = 0
        
        naics_codes = ["44-45", "441", "442", "443", "444", "445", "446", "447", "448", "451", "452", "453", "454"]
        
        for naics in naics_codes:
            for year in range(self.start_year, self.end_year + 1):
                for month in range(1, 13):
                    try:
                        params = {
                            "get": "cell_value,time,NAICS",
                            "for": "us:*",
                            "NAICS": naics,
                            "time": f"{year}-{month:02d}"
                        }
                        
                        response = self.session.get(self.census_mrtsadv_url, params=params, timeout=30)
                        response.raise_for_status()
                        data = response.json()
                        
                        if len(data) > 1:
                            filename = f"census_mrtsadv_{naics}_{year}_{month:02d}.json"
                            filepath = self.extracted_data_dir / filename
                            filepath.write_text(json.dumps(data, indent=2))
                            
                            bytes_extracted += len(response.content)
                            records += len(data) - 1
                            
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"  Error extracting {naics} {year}-{month:02d}: {e}")
                        continue
        
        self.total_bytes += bytes_extracted
        self.records_extracted += records
        print(f"\n✓ Census MRTSADV: {records} records, {bytes_extracted / 1024 / 1024:.2f} MB")
        return records
    
    def extract_bls_data(self) -> int:
        """Extract BLS CPI and PPI data - multiple series, extended time range"""
        print("\n" + "="*70)
        print("Extracting BLS Price Index Data")
        print("="*70)
        
        records = 0
        bytes_extracted = 0
        
        # BLS Series IDs for retail-related price indices - reduced for 1 GB target
        series_ids = [
            "CUUR0000SA0",      # CPI All Items
            "CUUR0000SETB01",   # CPI Televisions
            "CUUR0000SEEE01",   # CPI Smartphones
            "CUUR0000SEGA",     # CPI Apparel
            "CUUR0000SEHF",     # CPI Household Furnishings
            "CUUR0000SEHA",     # CPI Household Appliances
            "CUUR0000SETA",     # CPI New Vehicles
            "CUUR0000SETD",     # CPI Used Vehicles
            "CUUR0000SEGC",     # CPI Footwear
            "CUUR0000SEGD",     # CPI Women's Apparel
            "CUUR0000SEGE",     # CPI Men's Apparel
            "CUUR0000SERG",     # CPI Recreation
            "CUUR0000SERJ",     # CPI Sporting Goods
            "CUUR0000SERO",     # CPI Video Games
            "CUUR0000SERP",     # CPI Books
        ]
        
        # Process in batches of 50 (BLS API limit)
        batch_size = 50
        for i in range(0, len(series_ids), batch_size):
            batch = series_ids[i:i+batch_size]
            
            try:
                payload = {
                    "seriesid": batch,
                    "startyear": str(self.start_year),
                    "endyear": str(self.end_year),
                    "registrationkey": os.environ.get("BLS_API_KEY", "")
                }
                
                response = self.session.post(self.bls_url, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                if data.get('status') == 'REQUEST_SUCCEEDED':
                    # Save batch
                    filename = f"bls_price_indices_batch_{i//batch_size + 1}.json"
                    filepath = self.extracted_data_dir / filename
                    filepath.write_text(json.dumps(data, indent=2))
                    
                    bytes_extracted += len(response.content)
                    # Count records from Results
                    results = data.get('Results', {}).get('series', [])
                    for series in results:
                        records += len(series.get('data', []))
                    
                    print(f"  Extracted batch {i//batch_size + 1}: {len(batch)} series, {records} data points")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"  Error extracting batch {i//batch_size + 1}: {e}")
                continue
        
        self.total_bytes += bytes_extracted
        self.records_extracted += records
        print(f"\n✓ BLS Price Indices: {records} records, {bytes_extracted / 1024 / 1024:.2f} MB")
        return records
    
    def extract_datagov_datasets(self) -> int:
        """Extract datasets from Data.gov CKAN API"""
        print("\n" + "="*70)
        print("Extracting Data.gov Datasets")
        print("="*70)
        
        records = 0
        bytes_extracted = 0
        
        # Search for retail-related datasets - focused terms for 1 GB target
        search_terms = [
            "retail",
            "consumer",
            "pricing",
            "sales",
            "commerce",
            "market"
        ]
        
        for term in search_terms:
            try:
                params = {
                    "q": term,
                    "rows": 1000,  # Max results per search
                    "start": 0
                }
                
                url = f"{self.datagov_url}/package_search"
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                results = data.get('result', {}).get('results', [])
                
                for dataset in results[:20]:  # Reduced limit for 1 GB target
                    # Extract resource URLs
                    resources = dataset.get('resources', [])
                    for resource in resources:
                        if resource.get('format', '').upper() in ['CSV', 'JSON', 'XLSX']:
                            resource_url = resource.get('url')
                            if resource_url:
                                try:
                                    # Download resource
                                    resource_response = self.session.get(resource_url, timeout=60, stream=True)
                                    resource_response.raise_for_status()
                                    
                                    # Save resource
                                    resource_id = resource.get('id', 'unknown')
                                    format_ext = resource.get('format', 'csv').lower()
                                    filename = f"datagov_{term}_{resource_id}.{format_ext}"
                                    filepath = self.extracted_data_dir / filename
                                    
                                    with open(filepath, 'wb') as f:
                                        for chunk in resource_response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    
                                    file_size = filepath.stat().st_size
                                    bytes_extracted += file_size
                                    records += 1
                                    
                                    if records % 10 == 0:
                                        print(f"  Extracted {records} resources ({bytes_extracted / 1024 / 1024:.2f} MB)")
                                    
                                    time.sleep(2)  # Rate limiting for downloads
                                    
                                except Exception as e:
                                    print(f"  Error downloading resource {resource_id}: {e}")
                                    continue
                
                time.sleep(1)  # Rate limiting between searches
                
            except Exception as e:
                print(f"  Error searching for '{term}': {e}")
                continue
        
        self.total_bytes += bytes_extracted
        self.records_extracted += records
        print(f"\n✓ Data.gov: {records} resources, {bytes_extracted / 1024 / 1024:.2f} MB")
        return records
    
    # REMOVED: generate_synthetic_data() - Only real data from internet sources
    
    def run_extraction(self):
        """Run complete data extraction - REAL DATA ONLY, NO SYNTHETIC DATA"""
        print("="*70)
        print("Data Extraction for db-10 Marketing Intelligence Database")
        print(f"Target: 1 GB of REAL data from internet sources")
        print(f"Time Range: {self.start_year} - {self.end_year}")
        print("="*70)
        print("⚠️  SYNTHETIC DATA GENERATION DISABLED - Only real data from APIs")
        print("="*70)
        
        start_time = time.time()
        
        # Extract from all REAL data sources only
        self.extract_census_mrts_data()
        self.extract_census_mrtsadv_data()
        self.extract_bls_data()
        self.extract_datagov_datasets()
        # NO SYNTHETIC DATA - removed generate_synthetic_data()
        
        elapsed_time = time.time() - start_time
        
        # Summary
        print("\n" + "="*70)
        print("Extraction Summary")
        print("="*70)
        print(f"Total Records Extracted: {self.records_extracted:,}")
        print(f"Total Data Size: {self.total_bytes / 1024 / 1024 / 1024:.2f} GB")
        print(f"Time Elapsed: {elapsed_time / 60:.2f} minutes")
        print(f"Data Directory: {self.extracted_data_dir}")
        print("="*70)
        
        # Save metadata
        metadata = {
            'extraction_timestamp': get_est_timestamp(),
            'total_records': self.records_extracted,
            'total_bytes': self.total_bytes,
            'total_gb': self.total_bytes / 1024 / 1024 / 1024,
            'time_range': {
                'start_year': self.start_year,
                'end_year': self.end_year
            },
            'elapsed_seconds': elapsed_time,
            'data_directory': str(self.extracted_data_dir)
        }
        
        metadata_file = self.research_dir / 'extraction_metadata.json'
        metadata_file.write_text(json.dumps(metadata, indent=2))
        print(f"\nMetadata saved to: {metadata_file}")

if __name__ == '__main__':
    import sys
    try:
        extractor = LargeDataExtractor()
        extractor.run_extraction()
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: Extraction failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
