#!/usr/bin/env python3
"""
Large Dataset Extraction Script for db-9 Shipping Intelligence Database
Downloads and processes 2-30 GB of shipping intelligence data from:
- U.S. Census Bureau SPI Databank (bulk import/customs data)
- Data.gov datasets (ZIP boundaries, postal data, transportation)
- Historical shipping rate data
"""

import os
import sys
import json
import requests
import zipfile
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import logging
from urllib.parse import urlparse
import time
import hashlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LargeDatasetExtractor:
    """Extract large datasets from internet sources"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.downloaded_files = []
        self.total_size_bytes = 0
        self.data_gov_api_key = os.environ.get('DATA_GOV_API_KEY')
        
    def download_file(self, url: str, filename: str, chunk_size: int = 8192) -> Optional[Path]:
        """Download a file with progress tracking"""
        output_path = self.output_dir / filename
        
        if output_path.exists():
            logger.info(f"File already exists: {filename}, skipping download")
            file_size = output_path.stat().st_size
            self.total_size_bytes += file_size
            return output_path
        
        try:
            headers = {}
            if self.data_gov_api_key:
                headers['X-API-Key'] = self.data_gov_api_key
            
            response = requests.get(url, headers=headers, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if downloaded % (chunk_size * 100) == 0:  # Log every 100 chunks
                                logger.info(f"Downloaded {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({percent:.1f}%)")
            
            file_size = output_path.stat().st_size
            self.total_size_bytes += file_size
            self.downloaded_files.append({
                'url': url,
                'filename': filename,
                'size_bytes': file_size,
                'size_mb': file_size / 1024 / 1024,
                'downloaded_at': datetime.now().isoformat()
            })
            
            logger.info(f"✓ Downloaded {filename} ({file_size / 1024 / 1024:.2f} MB)")
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None
    
    def extract_zip(self, zip_path: Path, extract_to: Path) -> List[Path]:
        """Extract ZIP file"""
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                extracted_files = [extract_to / f for f in zip_ref.namelist()]
            logger.info(f"✓ Extracted {len(extracted_files)} files from {zip_path.name}")
            return extracted_files
        except Exception as e:
            logger.error(f"Error extracting {zip_path}: {e}")
            return []
    
    def extract_gzip(self, gz_path: Path, output_path: Path) -> Optional[Path]:
        """Extract GZIP file"""
        try:
            with gzip.open(gz_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            logger.info(f"✓ Extracted {gz_path.name} to {output_path.name}")
            return output_path
        except Exception as e:
            logger.error(f"Error extracting {gz_path}: {e}")
            return None
    
    def download_census_spi_databank(self, years: List[int] = None) -> List[Path]:
        """
        Download U.S. Census Bureau SPI Databank files
        SPI Databank contains detailed import data with HTSUSA codes, country of origin, customs value
        Available years: 2010-2024
        Each year's data can be several hundred MB to GB
        
        Note: Actual SPI files must be accessed through Census Bureau website or Data.gov
        This function searches Data.gov for Census trade datasets
        """
        logger.info("="*80)
        logger.info("Downloading Census Bureau SPI Databank Data")
        logger.info("="*80)
        
        downloaded_files = []
        census_dir = self.output_dir / "census_spi"
        census_dir.mkdir(exist_ok=True)
        
        # Search Data.gov for Census Bureau trade/import datasets
        base_url = "https://catalog.data.gov/api/3/action"
        headers = {}
        if self.data_gov_api_key:
            headers['X-API-Key'] = self.data_gov_api_key
        
        search_terms = [
            'census bureau foreign trade',
            'census bureau imports',
            'census bureau SPI',
            'HTSUSA import data',
            'international trade census'
        ]
        
        for term in search_terms:
            logger.info(f"Searching Data.gov for: {term}")
            search_url = f"{base_url}/package_search"
            params = {
                'q': term,
                'fq': 'organization:us-census-bureau',
                'rows': 50,
                'sort': 'views_recent desc'
            }
            
            try:
                response = requests.get(search_url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data.get('success'):
                    results = data.get('result', {}).get('results', [])
                    logger.info(f"Found {len(results)} Census Bureau trade datasets")
                    
                    for dataset in results[:20]:  # Top 20 per search term
                        resources = dataset.get('resources', [])
                        dataset_id = dataset.get('id', '')
                        
                        for resource in resources:
                            resource_url = resource.get('url', '')
                            resource_format = resource.get('format', '').upper()
                            
                            # Focus on CSV, Excel, ZIP files
                            if resource_url and resource_url.startswith('http') and resource_format in ['CSV', 'XLSX', 'ZIP', 'XLS']:
                                filename = f"census_spi/{dataset_id}_{resource.get('name', len(downloaded_files))}.{resource_format.lower()}"
                                file_path = self.download_file(resource_url, filename)
                                if file_path:
                                    downloaded_files.append(file_path)
                                    time.sleep(2)  # Rate limiting
                                    break  # One resource per dataset
                
            except Exception as e:
                logger.error(f"Error searching for '{term}': {e}")
        
        logger.info(f"Downloaded {len(downloaded_files)} Census SPI files")
        return downloaded_files
    
    def download_datagov_datasets(self, search_terms: List[str] = None) -> List[Path]:
        """
        Download large datasets from Data.gov
        Focus on ZIP boundaries, postal data, transportation datasets
        """
        logger.info("="*80)
        logger.info("Downloading Data.gov Datasets")
        logger.info("="*80)
        
        if search_terms is None:
            search_terms = ['usps', 'zip code', 'postal', 'shipping', 'transportation', 'logistics']
        
        downloaded_files = []
        datagov_dir = self.output_dir / "datagov"
        datagov_dir.mkdir(exist_ok=True)
        
        base_url = "https://catalog.data.gov/api/3/action"
        headers = {}
        if self.data_gov_api_key:
            headers['X-API-Key'] = self.data_gov_api_key
        
        for term in search_terms:
            logger.info(f"Searching Data.gov for: {term}")
            
            # Search for datasets
            search_url = f"{base_url}/package_search"
            params = {
                'q': term,
                'rows': 20,  # Reduced to 20 results for 1 GB target
                'sort': 'views_recent desc'  # Most viewed first
            }
            
            try:
                response = requests.get(search_url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data.get('success'):
                    results = data.get('result', {}).get('results', [])
                    logger.info(f"Found {len(results)} datasets for '{term}'")
                    
                    for dataset in results[:5]:  # Reduced to top 5 per term for 1 GB target
                        dataset_id = dataset.get('id', '')
                        resources = dataset.get('resources', [])
                        
                        # Download only first resource from each dataset for 1 GB target
                        for resource in resources[:1]:  # Only first resource
                            resource_format = resource.get('format', '').upper()
                            resource_url = resource.get('url', '')
                            
                            # Focus on large data formats
                            if resource_format in ['CSV', 'GEOJSON', 'SHAPEFILE', 'ZIP', 'XLSX']:
                                if resource_url and resource_url.startswith('http'):
                                    # Generate filename
                                    resource_name = resource.get('name', f"{dataset_id}_{len(downloaded_files)}")
                                    ext = resource_format.lower()
                                    if ext == 'shapefile':
                                        ext = 'zip'
                                    
                                    filename = f"datagov/{dataset_id}_{resource_name}.{ext}"
                                    file_path = self.download_file(resource_url, filename)
                                    if file_path:
                                        downloaded_files.append(file_path)
                                        time.sleep(1)  # Rate limiting
                                        break  # Only one resource per dataset
                
            except Exception as e:
                logger.error(f"Error searching Data.gov for '{term}': {e}")
        
        logger.info(f"Downloaded {len(downloaded_files)} Data.gov files")
        return downloaded_files
    
    def download_zip_boundaries(self) -> List[Path]:
        """
        Download ZIP code boundary datasets (can be large GeoJSON/Shapefiles)
        Uses Census Bureau TIGER/Line ZCTA files (actual working URLs)
        """
        logger.info("="*80)
        logger.info("Downloading ZIP Code Boundary Datasets")
        logger.info("="*80)
        
        downloaded_files = []
        zip_dir = self.output_dir / "zip_boundaries"
        zip_dir.mkdir(exist_ok=True)
        
        # Census Bureau TIGER/Line ZCTA files (actual working URLs)
        # Reduced to 1 GB target - download only most recent available year
        current_year = datetime.now().year
        # Use 2024 as most recent available (2025/2026 may not be released yet)
        tiger_years = [2024] if current_year >= 2024 else [current_year - 1]
        
        for year in tiger_years:
            # ZCTA5 (5-digit ZIP Code Tabulation Areas) - ~100-500 MB
            zcta_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/ZCTA5/tl_{year}_us_zcta510.zip"
            filename = f"zip_boundaries/tiger_{year}_zcta5.zip"
            file_path = self.download_file(zcta_url, filename)
            if file_path:
                downloaded_files.append(file_path)
        
        # Also search Data.gov for additional ZIP boundary datasets
        base_url = "https://catalog.data.gov/api/3/action"
        headers = {}
        if self.data_gov_api_key:
            headers['X-API-Key'] = self.data_gov_api_key
        
        search_url = f"{base_url}/package_search"
        params = {
            'q': 'zip code boundaries ZCTA',
            'rows': 30,
            'sort': 'views_recent desc'
        }
        
        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                results = data.get('result', {}).get('results', [])
                logger.info(f"Found {len(results)} additional ZIP boundary datasets")
                
                for dataset in results[:10]:  # Top 10 datasets
                    resources = dataset.get('resources', [])
                    dataset_id = dataset.get('id', '')
                    for resource in resources:
                        resource_url = resource.get('url', '')
                        if resource_url and resource_url.startswith('http'):
                            resource_format = resource.get('format', '').upper()
                            if resource_format in ['ZIP', 'SHAPEFILE', 'GEOJSON']:
                                ext = 'zip' if resource_format == 'SHAPEFILE' else resource_format.lower()
                                filename = f"zip_boundaries/{dataset_id}_boundaries.{ext}"
                                file_path = self.download_file(resource_url, filename)
                                if file_path:
                                    downloaded_files.append(file_path)
                                    time.sleep(2)  # Rate limiting
                                    break  # One resource per dataset
        
        except Exception as e:
            logger.error(f"Error downloading ZIP boundaries: {e}")
        
        logger.info(f"Downloaded {len(downloaded_files)} ZIP boundary files")
        return downloaded_files
    
    def download_postal_service_datasets(self) -> List[Path]:
        """
        Download USPS and postal service datasets
        """
        logger.info("="*80)
        logger.info("Downloading Postal Service Datasets")
        logger.info("="*80)
        
        downloaded_files = []
        postal_dir = self.output_dir / "postal_service"
        postal_dir.mkdir(exist_ok=True)
        
        # Search Data.gov for USPS/postal datasets
        base_url = "https://catalog.data.gov/api/3/action"
        headers = {}
        if self.data_gov_api_key:
            headers['X-API-Key'] = self.data_gov_api_key
        
        search_terms = ['usps', 'postal service', 'post office', 'mail']
        
        for term in search_terms:
            search_url = f"{base_url}/package_search"
            params = {
                'q': term,
                'rows': 50,
                'sort': 'views_recent desc'
            }
            
            try:
                response = requests.get(search_url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data.get('success'):
                    results = data.get('result', {}).get('results', [])
                    logger.info(f"Found {len(results)} datasets for '{term}'")
                    
                    for dataset in results[:15]:  # Top 15 per term
                        resources = dataset.get('resources', [])
                        for resource in resources:
                            resource_url = resource.get('url', '')
                            if resource_url and resource_url.startswith('http'):
                                dataset_id = dataset.get('id', '')
                                resource_name = resource.get('name', f"{dataset_id}")
                                ext = resource.get('format', 'csv').lower()
                                filename = f"postal_service/{dataset_id}_{resource_name}.{ext}"
                                file_path = self.download_file(resource_url, filename)
                                if file_path:
                                    downloaded_files.append(file_path)
                                    time.sleep(1)
            
            except Exception as e:
                logger.error(f"Error downloading postal datasets for '{term}': {e}")
        
        logger.info(f"Downloaded {len(downloaded_files)} postal service files")
        return downloaded_files
    
    def generate_download_summary(self) -> Dict:
        """Generate summary of downloaded data"""
        total_size_gb = self.total_size_bytes / 1024 / 1024 / 1024
        total_size_mb = self.total_size_bytes / 1024 / 1024
        
        summary = {
            'download_date': datetime.now().isoformat(),
            'total_files': len(self.downloaded_files),
            'total_size_bytes': self.total_size_bytes,
            'total_size_mb': round(total_size_mb, 2),
            'total_size_gb': round(total_size_gb, 2),
            'files': self.downloaded_files,
            'target_range': '1 GB',
            'status': 'SUCCESS' if total_size_gb >= 1 else 'INCOMPLETE'
        }
        
        return summary

def main():
    """Main extraction function"""
    script_dir = Path(__file__).parent
    db_dir = script_dir.parent
    output_dir = db_dir / "data" / "raw_datasets"
    
    extractor = LargeDatasetExtractor(output_dir)
    
    logger.info("="*80)
    logger.info("Large Dataset Extraction for db-9 Shipping Intelligence Database")
    logger.info("Target: 1 GB of shipping intelligence data")
    logger.info("="*80)
    
    # Download datasets
    all_files = []
    
    # 1. Census Bureau SPI Databank (reduced for 1 GB target)
    logger.info("\n[1/4] Downloading Census Bureau SPI Databank...")
    current_year = datetime.now().year
    census_files = extractor.download_census_spi_databank(years=[current_year - 1, current_year])  # Only last 2 years
    all_files.extend(census_files)
    
    # 2. ZIP Code Boundaries (can be 2-10 GB with multiple years and states)
    logger.info("\n[2/4] Downloading ZIP Code Boundaries...")
    zip_files = extractor.download_zip_boundaries()
    all_files.extend(zip_files)
    
    # 3. Data.gov Shipping/Postal Datasets (reduced for 1 GB target)
    logger.info("\n[3/4] Downloading Data.gov Shipping Datasets...")
    # Reduced search terms for 1 GB target
    limited_terms = ['usps', 'shipping', 'postal']  # Only 3 main terms
    datagov_files = extractor.download_datagov_datasets(search_terms=limited_terms)
    all_files.extend(datagov_files)
    
    # 4. Postal Service Datasets (reduced for 1 GB target)
    logger.info("\n[4/4] Downloading Postal Service Datasets...")
    postal_files = extractor.download_postal_service_datasets()
    all_files.extend(postal_files)
    
    # Generate summary
    summary = extractor.generate_download_summary()
    
    # Save summary
    summary_file = output_dir / "download_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, default=str))
    
    logger.info("\n" + "="*80)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("="*80)
    logger.info(f"Total Files: {summary['total_files']}")
    logger.info(f"Total Size: {summary['total_size_gb']:.2f} GB ({summary['total_size_mb']:.2f} MB)")
    logger.info(f"Target Range: {summary['target_range']}")
    logger.info(f"Status: {summary['status']}")
    logger.info(f"Summary saved to: {summary_file}")
    logger.info("="*80)
    
    if summary['status'] == 'INCOMPLETE':
        logger.warning(f"⚠️  Downloaded {summary['total_size_gb']:.2f} GB, target is 1 GB")
        logger.warning("Consider running additional downloads or checking data source availability")
    
    return summary

if __name__ == '__main__':
    main()
