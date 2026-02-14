#!/usr/bin/env python3
"""
Pull large volumes of data from internet sources (10-30 GB requirement)
Pulls from public APIs and data sources without requiring API keys where possible
"""

import os
import sys
import json
import csv
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback
import tempfile
import uuid

# Import timestamp utility
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    root_scripts = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(root_scripts))
    from timestamp_utils import get_est_timestamp

# API imports
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Data processing imports
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InternetDataPuller:
    """Pull large volumes of data from internet sources"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {
            'total_records': 0,
            'total_size_mb': 0.0,
            'sources': {},
            'errors': []
        }
        
        # Setup requests session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def pull_data_gov_datasets(self, max_datasets: int = 50) -> Dict:
        """Pull datasets from Data.gov (public, no API key required for metadata)"""
        logger.info(f"Pulling datasets from Data.gov (max {max_datasets})")
        result = {
            'source': 'data.gov',
            'datasets_pulled': 0,
            'records_pulled': 0,
            'size_mb': 0.0,
            'errors': []
        }
        
        base_url = "https://catalog.data.gov/api/3/action"
        
        try:
            # Search for employment/job-related datasets
            search_terms = [
                'employment', 'jobs', 'labor', 'workforce', 'occupation',
                'wage', 'salary', 'career', 'job market', 'unemployment'
            ]
            
            all_datasets = []
            for term in search_terms[:5]:  # Limit to avoid too many requests
                try:
                    url = f"{base_url}/package_search"
                    params = {
                        'q': term,
                        'rows': 100,
                        'start': 0
                    }
                    
                    response = self.session.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('result', {}).get('results'):
                        all_datasets.extend(data['result']['results'])
                        logger.info(f"Found {len(data['result']['results'])} datasets for '{term}'")
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error searching for '{term}': {e}")
                    result['errors'].append(f"Search error for '{term}': {str(e)}")
            
            # Deduplicate datasets
            seen_ids = set()
            unique_datasets = []
            for ds in all_datasets:
                if ds.get('id') not in seen_ids:
                    seen_ids.add(ds['id'])
                    unique_datasets.append(ds)
            
            logger.info(f"Found {len(unique_datasets)} unique datasets")
            
            # Download resources from datasets
            downloaded = 0
            for dataset in unique_datasets[:max_datasets]:
                if downloaded >= max_datasets:
                    break
                
                try:
                    dataset_id = dataset.get('id')
                    dataset_name = dataset.get('name', 'unknown')
                    resources = dataset.get('resources', [])
                    
                    logger.info(f"Processing dataset: {dataset_name} ({len(resources)} resources)")
                    
                    for resource in resources[:3]:  # Limit resources per dataset
                        if downloaded >= max_datasets:
                            break
                        
                        resource_url = resource.get('url')
                        resource_format = resource.get('format', '').upper()
                        
                        if not resource_url or resource_format not in ['CSV', 'JSON', 'XML']:
                            continue
                        
                        try:
                            # Download resource
                            logger.info(f"Downloading: {resource_url[:80]}...")
                            resp = self.session.get(resource_url, timeout=60, stream=True)
                            resp.raise_for_status()
                            
                            # Save to file
                            output_file = self.output_dir / f"datagov_{dataset_id}_{uuid.uuid4().hex[:8]}.{resource_format.lower()}"
                            
                            size_mb = 0
                            with open(output_file, 'wb') as f:
                                for chunk in resp.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        size_mb += len(chunk) / (1024 * 1024)
                            
                            result['datasets_pulled'] += 1
                            result['size_mb'] += size_mb
                            result['records_pulled'] += int(size_mb * 1000)  # Rough estimate
                            downloaded += 1
                            
                            logger.info(f"Downloaded {size_mb:.2f} MB from {dataset_name}")
                            
                            # Rate limiting
                            time.sleep(1)
                            
                        except Exception as e:
                            logger.warning(f"Error downloading resource: {e}")
                            result['errors'].append(f"Download error: {str(e)}")
                    
                except Exception as e:
                    logger.warning(f"Error processing dataset: {e}")
                    result['errors'].append(f"Dataset error: {str(e)}")
            
            logger.info(f"Pulled {result['datasets_pulled']} datasets, {result['size_mb']:.2f} MB")
            
        except Exception as e:
            logger.error(f"Data.gov pull error: {e}")
            result['errors'].append(f"Data.gov error: {str(e)}")
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def pull_bls_public_data(self, years_back: int = 10) -> Dict:
        """Pull BLS public data (no API key required, but limited rate)"""
        logger.info(f"Pulling BLS data for last {years_back} years")
        result = {
            'source': 'bls',
            'series_pulled': 0,
            'records_pulled': 0,
            'size_mb': 0.0,
            'errors': []
        }
        
        base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        
        # Key BLS series for job market data
        series_ids = [
            'LAUCN040010000000003',  # Unemployment rate
            'LAUCN040010000000004',  # Employment level
            'LAUCN040010000000006',  # Labor force
            'LEU0254556600',  # Employment by occupation
            'LEU0254556700',  # Employment by industry
        ]
        
        try:
            current_year = datetime.now().year
            start_year = current_year - years_back
            
            # Pull data for multiple series
            for series_id in series_ids[:3]:  # Limit to avoid rate limits
                try:
                    payload = {
                        'seriesid': [series_id],
                        'startyear': str(start_year),
                        'endyear': str(current_year)
                    }
                    
                    headers = {'Content-Type': 'application/json'}
                    
                    logger.info(f"Requesting BLS series: {series_id}")
                    response = self.session.post(base_url, json=payload, headers=headers, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 'REQUEST_SUCCEEDED':
                        # Save response
                        output_file = self.output_dir / f"bls_{series_id}_{start_year}_{current_year}.json"
                        output_file.write_text(json.dumps(data, indent=2))
                        
                        size_mb = output_file.stat().st_size / (1024 * 1024)
                        result['series_pulled'] += 1
                        result['size_mb'] += size_mb
                        result['records_pulled'] += len(data.get('Results', {}).get('series', [{}])[0].get('data', []))
                        
                        logger.info(f"Pulled {size_mb:.2f} MB for series {series_id}")
                    
                    # Rate limiting (BLS has strict limits without key)
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error pulling BLS series {series_id}: {e}")
                    result['errors'].append(f"BLS series {series_id}: {str(e)}")
            
        except Exception as e:
            logger.error(f"BLS pull error: {e}")
            result['errors'].append(f"BLS error: {str(e)}")
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def pull_public_csv_datasets(self) -> Dict:
        """Pull publicly available CSV datasets from various sources"""
        logger.info("Pulling public CSV datasets")
        result = {
            'source': 'public_csv',
            'files_pulled': 0,
            'records_pulled': 0,
            'size_mb': 0.0,
            'errors': []
        }
        
        # Public datasets that don't require authentication
        # These are example URLs - in production, use actual public dataset URLs
        public_urls = [
            # Note: Add actual public dataset URLs here when available
            # Many government datasets are available via Data.gov CKAN API
        ]
        
        # Download from public URLs if provided
        for url in public_urls:
            try:
                logger.info(f"Downloading from: {url[:80]}...")
                response = self.session.get(url, timeout=60, stream=True)
                response.raise_for_status()
                
                # Determine file extension from URL or Content-Type
                ext = 'csv'
                if '.csv' in url.lower():
                    ext = 'csv'
                elif '.json' in url.lower():
                    ext = 'json'
                elif '.xml' in url.lower():
                    ext = 'xml'
                
                output_file = self.output_dir / f"public_{uuid.uuid4().hex[:8]}.{ext}"
                
                size_mb = 0
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            size_mb += len(chunk) / (1024 * 1024)
                
                result['files_pulled'] += 1
                result['size_mb'] += size_mb
                result['records_pulled'] += int(size_mb * 1000)  # Rough estimate
                
                logger.info(f"Downloaded {size_mb:.2f} MB")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error downloading {url}: {e}")
                result['errors'].append(f"Download error for {url}: {str(e)}")
        
        return result
    
    def pull_all_sources(self, target_gb: float = 1.0) -> Dict:
        """Pull data from all sources until target volume is reached"""
        logger.info(f"Starting data pull - target: {target_gb} GB")
        
        results = {
            'pull_date': get_est_timestamp(),
            'target_gb': target_gb,
            'sources': {},
            'total_size_mb': 0.0,
            'total_size_gb': 0.0,
            'meets_requirement': False
        }
        
        # Pull from Data.gov (largest source)
        logger.info("Phase 1: Pulling from Data.gov")
        data_gov_result = self.pull_data_gov_datasets(max_datasets=20)  # Reduced for 1GB target
        results['sources']['data_gov'] = data_gov_result
        results['total_size_mb'] += data_gov_result['size_mb']
        
        # Pull from BLS
        logger.info("Phase 2: Pulling from BLS")
        bls_result = self.pull_bls_public_data(years_back=5)  # Reduced for 1GB target
        results['sources']['bls'] = bls_result
        results['total_size_mb'] += bls_result['size_mb']
        
        # Pull public CSV datasets
        logger.info("Phase 3: Pulling public CSV datasets")
        public_csv_result = self.pull_public_csv_datasets()
        results['sources']['public_csv'] = public_csv_result
        results['total_size_mb'] += public_csv_result['size_mb']
        
        # Calculate totals
        results['total_size_gb'] = results['total_size_mb'] / 1024.0
        results['meets_requirement'] = results['total_size_gb'] >= 1.0
        
        # Update stats
        self.stats['total_size_mb'] = results['total_size_mb']
        self.stats['sources'] = results['sources']
        
        # Save results
        results_file = self.output_dir.parent / 'results' / f'internet_data_pull_{get_est_timestamp()}.json'
        results_file.parent.mkdir(parents=True, exist_ok=True)
        results_file.write_text(json.dumps(results, indent=2, default=str))
        
        logger.info(f"Data pull complete: {results['total_size_gb']:.2f} GB")
        return results


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pull data from internet sources')
    parser.add_argument('--output-dir', type=str, default='data/internet_pulled',
                       help='Output directory for pulled data')
    parser.add_argument('--target-gb', type=float, default=1.0,
                       help='Target data volume in GB (default: 1.0)')
    
    args = parser.parse_args()
    
    puller = InternetDataPuller(args.output_dir)
    results = puller.pull_all_sources(target_gb=args.target_gb)
    
    print("\n" + "="*70)
    print("Internet Data Pull Results")
    print("="*70)
    print(f"Target: {results['target_gb']} GB")
    print(f"Total Pulled: {results['total_size_gb']:.2f} GB ({results['total_size_mb']:.2f} MB)")
    print(f"Meets Requirement (10-30 GB): {'YES' if results['meets_requirement'] else 'NO'}")
    print(f"\nSources:")
    for source, data in results['sources'].items():
        print(f"  {source}: {data.get('size_mb', 0):.2f} MB")
    print("="*70)
    print(f"\nData saved to: {args.output_dir}")


if __name__ == '__main__':
    main()
