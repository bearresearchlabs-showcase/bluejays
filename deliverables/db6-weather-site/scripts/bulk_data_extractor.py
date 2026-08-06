#!/usr/bin/env python3
"""
Bulk Data Extractor - Pulls 2-30 GB of data from internet sources
Supports db-7 (Maritime), db-9 (Shipping), and db-11 (Parking Intelligence)
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np
from urllib.parse import urljoin, urlencode
import time
import hashlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TARGET_DATA_SIZE_GB = 1  # Target 1 GB per database
CHUNK_SIZE = 8192  # 8KB chunks for downloads
MAX_WORKERS = 10  # Parallel downloads
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

class BulkDataExtractor:
    """Extracts large volumes of data from internet sources."""
    
    def __init__(self, db_name: str, output_dir: Optional[Path] = None):
        self.db_name = db_name
        self.output_dir = output_dir or Path(__file__).parent.parent / db_name / "data" / "raw"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.output_dir.parent / "extraction_metadata.json"
        self.session = self._create_session()
        self.extracted_data = []
        self.total_bytes = 0
        
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        retry_strategy = requests.packages.urllib3.util.retry.Retry(
            total=RETRY_ATTEMPTS,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def download_file(self, url: str, output_path: Path, description: str = "") -> Tuple[bool, int]:
        """Download a file with progress tracking."""
        try:
            logger.info(f"Downloading {description or url} to {output_path}")
            response = self.session.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            file_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
            
            logger.info(f"✓ Downloaded {bytes_downloaded / (1024*1024):.2f} MB: {output_path.name}")
            return True, bytes_downloaded
            
        except Exception as e:
            logger.error(f"✗ Failed to download {url}: {e}")
            if output_path.exists():
                output_path.unlink()
            return False, 0
    
    def extract_data_gov_datasets(self, query: str, limit: int = 100) -> List[Dict]:
        """Extract datasets from Data.gov CKAN API."""
        logger.info(f"Searching Data.gov for: {query}")
        datasets = []
        
        api_key = os.getenv('DATA_GOV_API_KEY', '')
        base_url = "https://catalog.data.gov/api/3/action/package_search"
        
        params = {
            'q': query,
            'rows': min(100, limit),  # API max is typically 100 per request
            'start': 0
        }
        
        if api_key:
            headers = {'X-API-Key': api_key}
        else:
            headers = {}
        
        try:
            max_iterations = (limit + 99) // 100  # Calculate needed iterations
            for iteration in range(max_iterations):
                if len(datasets) >= limit:
                    break
                    
                response = self.session.get(base_url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if 'result' not in data or 'results' not in data['result']:
                    break
                
                results = data['result']['results']
                if not results:
                    break
                
                datasets.extend(results)
                
                # Check if there are more results
                if len(results) < params['rows']:
                    break
                
                params['start'] += params['rows']
                time.sleep(0.3)  # Rate limiting - reduced delay
            
            logger.info(f"✓ Found {len(datasets)} datasets for query: {query}")
            return datasets[:limit]  # Return exactly limit number
            
        except Exception as e:
            logger.error(f"Error searching Data.gov: {e}")
            return []
    
    def download_data_gov_resources(self, dataset: Dict, max_size_mb: int = 500) -> List[Path]:
        """Download resources from a Data.gov dataset."""
        downloaded_files = []
        
        if 'resources' not in dataset:
            return downloaded_files
        
        # Sort resources by size (largest first) to prioritize big datasets
        resources = sorted(
            dataset.get('resources', []),
            key=lambda r: r.get('size', 0) if r.get('size') else 0,
            reverse=True
        )
        
        for resource in resources:
            url = resource.get('url')
            if not url or not url.startswith('http'):
                continue
            
            # Skip non-data file types
            url_lower = url.lower()
            if any(url_lower.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.html', '.htm']):
                continue
            
            # Skip very large files unless specifically requested
            size_mb = resource.get('size', 0) / (1024 * 1024) if resource.get('size') else 0
            if size_mb > max_size_mb:
                logger.info(f"Skipping large file: {resource.get('name', url)} ({size_mb:.1f} MB)")
                continue
            
            # Generate filename
            resource_id = resource.get('id', hashlib.md5(url.encode()).hexdigest()[:12])
            # Clean dataset name for filename
            dataset_name = dataset.get('name', 'dataset').replace('/', '_').replace('\\', '_')[:50]
            ext = Path(url).suffix or ('.csv' if 'csv' in resource.get('format', '').lower() else '.json')
            filename = f"{dataset_name}_{resource_id}{ext}"
            output_path = self.output_dir / filename
            
            # Limit filename length
            if len(str(output_path)) > 200:
                filename = f"{hashlib.md5(dataset_name.encode()).hexdigest()[:12]}_{resource_id}{ext}"
                output_path = self.output_dir / filename
            
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"File already exists: {output_path.name} ({file_size / (1024*1024):.2f} MB)")
                downloaded_files.append(output_path)
                self.total_bytes += file_size
                continue
            
            success, bytes_downloaded = self.download_file(
                url, output_path, f"{dataset.get('title', 'Dataset')} - {resource.get('name', 'Resource')}"
            )
            
            if success:
                downloaded_files.append(output_path)
                self.total_bytes += bytes_downloaded
                self.extracted_data.append({
                    'source': 'Data.gov',
                    'dataset': dataset.get('title', 'Unknown'),
                    'resource': resource.get('name', 'Unknown'),
                    'url': url,
                    'file': str(output_path),
                    'size_bytes': bytes_downloaded,
                    'extracted_at': datetime.now().isoformat()
                })
        
        return downloaded_files
    
    def extract_census_data(self, dataset: str, variables: List[str], geography: str, years: List[int]) -> List[Path]:
        """Extract data from Census Bureau API."""
        logger.info(f"Extracting Census data: {dataset} for {len(years)} years")
        downloaded_files = []
        
        api_key = os.getenv('CENSUS_API_KEY', '')
        base_url = f"https://api.census.gov/data/{years[0]}/{dataset}"
        
        for year in years:
            params = {
                'get': ','.join(variables),
                'for': geography,
                'key': api_key
            } if api_key else {
                'get': ','.join(variables),
                'for': geography
            }
            
            try:
                response = self.session.get(base_url.replace(str(years[0]), str(year)), params=params, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                # Convert to DataFrame and save
                if len(data) > 1:
                    df = pd.DataFrame(data[1:], columns=data[0])
                    output_path = self.output_dir / f"census_{dataset}_{year}.csv"
                    df.to_csv(output_path, index=False)
                    
                    file_size = output_path.stat().st_size
                    downloaded_files.append(output_path)
                    self.total_bytes += file_size
                    
                    self.extracted_data.append({
                        'source': 'Census Bureau',
                        'dataset': dataset,
                        'year': year,
                        'file': str(output_path),
                        'size_bytes': file_size,
                        'extracted_at': datetime.now().isoformat()
                    })
                    
                    logger.info(f"✓ Extracted Census {dataset} {year}: {file_size / (1024*1024):.2f} MB")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error extracting Census data for {year}: {e}")
        
        return downloaded_files
    
    def extract_noaa_ais_bulk(self, years: List[int], regions: List[str] = None) -> List[Path]:
        """Extract NOAA AIS vessel traffic data (bulk download)."""
        logger.info(f"Extracting NOAA AIS data for {len(years)} years")
        downloaded_files = []
        
        # Note: NOAA AIS data requires using AccessAIS tool or MarineCadastre.gov
        # This is a placeholder for bulk extraction strategy
        base_urls = [
            "https://marinecadastre.gov/AIS/",
            "https://coast.noaa.gov/digitalcoast/data/vesseltraffic.html"
        ]
        
        # For actual implementation, would need to:
        # 1. Use AccessAIS tool API if available
        # 2. Download quarterly/annual AIS datasets
        # 3. Each year can be 500MB-2GB depending on region
        
        logger.warning("NOAA AIS bulk extraction requires AccessAIS tool - manual download recommended")
        return downloaded_files
    
    def extract_marad_data(self) -> List[Path]:
        """Extract MARAD maritime data."""
        logger.info("Extracting MARAD data")
        downloaded_files = []
        
        marad_urls = [
            "https://www.maritime.dot.gov/data-reports/us-flag-fleet-dashboard",
            "https://www.maritime.dot.gov/data-reports/ports"
        ]
        
        # MARAD data typically available as Excel/CSV downloads
        # Would need to scrape or use their API if available
        
        return downloaded_files
    
    def save_metadata(self):
        """Save extraction metadata."""
        metadata = {
            'database': self.db_name,
            'extraction_date': datetime.now().isoformat(),
            'total_files': len(self.extracted_data),
            'total_size_bytes': self.total_bytes,
            'total_size_gb': self.total_bytes / (1024**3),
            'extracted_data': self.extracted_data
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✓ Metadata saved: {self.metadata_file}")
        logger.info(f"Total extracted: {metadata['total_size_gb']:.2f} GB")
    
    def run_extraction(self, target_size_gb: float = TARGET_DATA_SIZE_GB):
        """Run comprehensive data extraction."""
        logger.info(f"Starting bulk data extraction for {self.db_name}")
        logger.info(f"Target size: {target_size_gb} GB")
        
        if self.db_name == 'db-7':
            self._extract_maritime_data(target_size_gb)
        elif self.db_name == 'db-9':
            self._extract_shipping_data(target_size_gb)
        elif self.db_name == 'db-11':
            self._extract_parking_data(target_size_gb)
        else:
            logger.error(f"Unknown database: {self.db_name}")
        
        self.save_metadata()
        logger.info(f"✓ Extraction complete: {self.total_bytes / (1024**3):.2f} GB")
    
    def _extract_maritime_data(self, target_gb: float):
        """Extract maritime shipping data for db-7."""
        logger.info("Extracting maritime data sources...")
        
        # 1. Data.gov maritime datasets - reduced for 1 GB target
        queries = [
            "maritime shipping",
            "vessel port",
            "AIS vessel",
            "shipping schedules",
            "port statistics"
        ]
        
        for query in queries:
            if self.total_bytes / (1024**3) >= target_gb:
                break
            datasets = self.extract_data_gov_datasets(query, limit=50)
            for dataset in datasets[:20]:  # Reduced for 1 GB target
                if self.total_bytes / (1024**3) >= target_gb:
                    break
                self.download_data_gov_resources(dataset, max_size_mb=500)  # Reduced for 1 GB target
        
        # 2. Census Bureau trade data (for shipping patterns) - reduced for 1 GB
        if self.total_bytes / (1024**3) < target_gb:
            # Import data - recent years only
            self.extract_census_data(
                dataset='timeseries/intltrade/imports',
                variables=['I_MKT', 'I_COMMODITY', 'I_QTY1', 'I_VAL_MO'],
                geography='us:*',
                years=list(range(2020, 2025))  # Recent 5 years for 1 GB target
            )
    
    def _extract_shipping_data(self, target_gb: float):
        """Extract shipping/logistics data for db-9."""
        logger.info("Extracting shipping data sources...")
        
        # 1. Data.gov shipping datasets - reduced for 1 GB target
        queries = [
            "shipping postal",
            "logistics transportation",
            "trade import export",
            "customs tariff"
        ]
        
        for query in queries:
            if self.total_bytes / (1024**3) >= target_gb:
                break
            datasets = self.extract_data_gov_datasets(query, limit=50)  # Reduced for 1 GB target
            for dataset in datasets[:20]:  # Reduced for 1 GB target
                if self.total_bytes / (1024**3) >= target_gb:
                    break
                self.download_data_gov_resources(dataset, max_size_mb=500)  # Reduced for 1 GB target
        
        # 2. Census Bureau international trade data - reduced for 1 GB
        if self.total_bytes / (1024**3) < target_gb:
            # Import data - recent years only
            self.extract_census_data(
                dataset='timeseries/intltrade/imports',
                variables=['I_MKT', 'I_COMMODITY', 'I_QTY1', 'I_VAL_MO'],
                geography='us:*',
                years=list(range(2020, 2025))  # Recent 5 years for 1 GB target
            )
            
            # Export data
            if self.total_bytes / (1024**3) < target_gb:
                self.extract_census_data(
                    dataset='timeseries/intltrade/exports',
                    variables=['E_MKT', 'E_COMMODITY', 'E_QTY1', 'I_VAL_MO'],
                    geography='us:*',
                    years=list(range(2020, 2025))  # Recent 5 years
                )
    
    def _extract_parking_data(self, target_gb: float):
        """Extract parking intelligence data for db-11."""
        logger.info("Extracting parking data sources...")
        
        # 1. Data.gov parking datasets - expanded
        queries = [
            "parking facility",
            "parking meter",
            "parking transaction",
            "transportation parking",
            "parking citation",
            "parking occupancy",
            "parking rates",
            "off-street parking",
            "parking garage",
            "parking lot"
        ]
        
        for query in queries:
            if self.total_bytes / (1024**3) >= target_gb:
                break
            datasets = self.extract_data_gov_datasets(query, limit=50)  # Reduced for 1 GB target
            for dataset in datasets[:25]:  # Reduced for 1 GB target
                if self.total_bytes / (1024**3) >= target_gb:
                    break
                self.download_data_gov_resources(dataset, max_size_mb=200)  # Reduced for 1 GB target
        
        # 2. Census Bureau demographics (for 400+ cities) - reduced for 1 GB
        if self.total_bytes / (1024**3) < target_gb:
            # Extract ACS 5-year estimates for metropolitan areas - recent years
            acs_variables = [
                'B01001_001E',  # Total population
                'B08301_001E',  # Means of transportation to work
                'B25001_001E',  # Total housing units
                'B19013_001E'   # Median household income
            ]
            self.extract_census_data(
                dataset='acs/acs5',
                variables=acs_variables,
                geography='metropolitan statistical area/micropolitan statistical area:*',
                years=[2020, 2021, 2022, 2023, 2024]  # Recent 5 years for 1 GB target
            )
            
            # Extract population estimates - recent years
            if self.total_bytes / (1024**3) < target_gb:
                self.extract_census_data(
                    dataset='pep/population',
                    variables=['POP', 'DATE_CODE'],
                    geography='metropolitan statistical area/micropolitan statistical area:*',
                    years=list(range(2020, 2025))  # Recent 5 years
                )


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk Data Extractor')
    parser.add_argument('db_name', choices=['db-7', 'db-9', 'db-11'], help='Database name')
    parser.add_argument('--target-gb', type=float, default=1, help='Target data size in GB')
    parser.add_argument('--output-dir', type=str, help='Output directory')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir) if args.output_dir else None
    extractor = BulkDataExtractor(args.db_name, output_dir)
    extractor.run_extraction(target_size_gb=args.target_gb)


if __name__ == '__main__':
    main()
