#!/usr/bin/env python3
"""
Bulk download extraction - Downloads large datasets directly instead of API calls
Faster approach: Download complete datasets from public sources
"""

import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import zipfile
import gzip

script_dir = Path(__file__).parent
research_dir = script_dir.parent / 'research'
extracted_data_dir = research_dir / 'extracted_data'
extracted_data_dir.mkdir(parents=True, exist_ok=True)

def create_session():
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def download_file(url, filepath, description=""):
    """Download a file with progress tracking"""
    print(f"  Downloading {description}...")
    session = create_session()
    
    try:
        response = session.get(url, timeout=300, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if downloaded % (10 * 1024 * 1024) == 0:  # Print every 10MB
                            print(f"    {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({percent:.1f}%)")
        
        file_size = filepath.stat().st_size
        print(f"    ✓ Downloaded: {file_size / 1024 / 1024:.2f} MB")
        return file_size
    except Exception as e:
        print(f"    ✗ Error: {e}")
        if filepath.exists():
            filepath.unlink()
        return 0

def download_census_bulk_data():
    """Download Census Bureau bulk data files"""
    print("\n" + "="*70)
    print("Downloading Census Bureau Bulk Data")
    print("="*70)
    
    total_bytes = 0
    
    # Census Bureau Economic Census data (large files)
    census_urls = [
        {
            "url": "https://www2.census.gov/programs-surveys/economic-census/data/2017/CSV/ecn2017_44-45_naics.csv",
            "filename": "census_economic_2017_retail_trade.csv",
            "description": "2017 Economic Census - Retail Trade"
        },
        {
            "url": "https://www2.census.gov/programs-surveys/economic-census/data/2012/CSV/ecn2012_44-45_naics.csv",
            "filename": "census_economic_2012_retail_trade.csv",
            "description": "2012 Economic Census - Retail Trade"
        }
    ]
    
    for item in census_urls:
        filepath = extracted_data_dir / item["filename"]
        if not filepath.exists():
            size = download_file(item["url"], filepath, item["description"])
            total_bytes += size
        else:
            size = filepath.stat().st_size
            print(f"  File already exists: {item['filename']} ({size / 1024 / 1024:.2f} MB)")
            total_bytes += size
    
    return total_bytes

def download_bls_bulk_data():
    """Download BLS bulk data files"""
    print("\n" + "="*70)
    print("Downloading BLS Bulk Data")
    print("="*70)
    
    total_bytes = 0
    
    # BLS CPI data - multiple years
    bls_base_url = "https://download.bls.gov/pub/time.series/cu/"
    bls_files = [
        "cu.data.0.Current",  # Current CPI data
        "cu.data.1.AllItems",  # All items CPI
        "cu.data.2.Summaries",  # CPI summaries
        "cu.series",  # Series metadata
        "cu.item",  # Item codes
    ]
    
    for filename in bls_files:
        url = bls_base_url + filename
        filepath = extracted_data_dir / f"bls_{filename}"
        if not filepath.exists():
            size = download_file(url, filepath, f"BLS {filename}")
            total_bytes += size
        else:
            size = filepath.stat().st_size
            print(f"  File already exists: bls_{filename} ({size / 1024 / 1024:.2f} MB)")
            total_bytes += size
    
    return total_bytes

def download_datagov_large_datasets():
    """Download large datasets from Data.gov"""
    print("\n" + "="*70)
    print("Downloading Data.gov Large Datasets")
    print("="*70)
    
    total_bytes = 0
    session = create_session()
    
    # Search for large retail/consumer datasets
    search_url = "https://catalog.data.gov/api/3/action/package_search"
    
    # Search for datasets with large file sizes
    search_terms = ["retail", "consumer", "economic", "census"]
    
    for term in search_terms:
        try:
            params = {
                "q": term,
                "rows": 50,
                "sort": "views_recent desc"  # Popular datasets
            }
            response = session.get(search_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                results = data.get('result', {}).get('results', [])
                
                for dataset in results[:10]:  # Top 10 per term
                    resources = dataset.get('resources', [])
                    # Sort by file size (largest first)
                    resources.sort(key=lambda x: x.get('size', 0) or 0, reverse=True)
                    
                    for resource in resources[:3]:  # Top 3 largest per dataset
                        resource_url = resource.get('url')
                        resource_size = resource.get('size', 0) or 0
                        
                        # Only download if > 10MB
                        if resource_url and resource_size > 10 * 1024 * 1024:
                            resource_id = resource.get('id', 'unknown')
                            format_ext = resource.get('format', 'csv').lower()
                            filename = f"datagov_{term}_{resource_id}.{format_ext}"
                            filepath = extracted_data_dir / filename
                            
                            if not filepath.exists():
                                size = download_file(
                                    resource_url,
                                    filepath,
                                    f"Data.gov {term} ({resource_size / 1024 / 1024:.1f} MB)"
                                )
                                total_bytes += size
                            else:
                                size = filepath.stat().st_size
                                total_bytes += size
                        
                        if total_bytes > 1024 * 1024 * 1024:  # Stop at 1 GB
                            break
                    
                    if total_bytes > 1024 * 1024 * 1024:
                        break
            
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"  Error searching '{term}': {e}")
            continue
        
        if total_bytes > 1024 * 1024 * 1024:
            break
    
    return total_bytes

def download_ftc_data():
    """Download FTC consumer complaint data"""
    print("\n" + "="*70)
    print("Downloading FTC Consumer Complaint Data")
    print("="*70)
    
    total_bytes = 0
    
    # FTC Consumer Sentinel Network data (large CSV files)
    ftc_urls = [
        {
            "url": "https://www.ftc.gov/system/files/ftc_gov/data/consumer-sentinel-network-data-book-2023.csv",
            "filename": "ftc_consumer_complaints_2023.csv",
            "description": "FTC Consumer Complaints 2023"
        },
        {
            "url": "https://www.ftc.gov/system/files/ftc_gov/data/consumer-sentinel-network-data-book-2022.csv",
            "filename": "ftc_consumer_complaints_2022.csv",
            "description": "FTC Consumer Complaints 2022"
        },
        {
            "url": "https://www.ftc.gov/system/files/ftc_gov/data/consumer-sentinel-network-data-book-2021.csv",
            "filename": "ftc_consumer_complaints_2021.csv",
            "description": "FTC Consumer Complaints 2021"
        }
    ]
    
    for item in ftc_urls:
        filepath = extracted_data_dir / item["filename"]
        if not filepath.exists():
            size = download_file(item["url"], filepath, item["description"])
            total_bytes += size
        else:
            size = filepath.stat().st_size
            print(f"  File already exists: {item['filename']} ({size / 1024 / 1024:.2f} MB)")
            total_bytes += size
    
    return total_bytes

def main():
    print("="*70)
    print("Bulk Download Extraction - Real Data Only")
    print("Target: 1 GB from large public datasets")
    print("="*70)
    
    start_time = time.time()
    total_bytes = 0
    
    # Download from multiple sources
    total_bytes += download_census_bulk_data()
    total_bytes += download_bls_bulk_data()
    total_bytes += download_datagov_large_datasets()
    total_bytes += download_ftc_data()
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "="*70)
    print("Extraction Summary")
    print("="*70)
    print(f"Total Files: {len(list(extracted_data_dir.glob('*')))}")
    print(f"Total Size: {total_bytes / 1024 / 1024 / 1024:.2f} GB ({total_bytes / 1024 / 1024:.2f} MB)")
    print(f"Time Elapsed: {elapsed / 60:.2f} minutes")
    print(f"Data Directory: {extracted_data_dir}")
    print("="*70)
    
    # Save metadata
    metadata = {
        'extraction_timestamp': datetime.now().strftime('%Y%m%d-%H%M'),
        'total_bytes': total_bytes,
        'total_gb': total_bytes / 1024 / 1024 / 1024,
        'elapsed_seconds': elapsed,
        'method': 'bulk_download',
        'data_directory': str(extracted_data_dir)
    }
    
    metadata_file = research_dir / 'extraction_metadata.json'
    metadata_file.write_text(json.dumps(metadata, indent=2))
    print(f"\nMetadata saved to: {metadata_file}")

if __name__ == '__main__':
    main()
