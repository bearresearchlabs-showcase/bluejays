#!/usr/bin/env python3
"""
Smart bulk extraction - Uses Data.gov API to find and download large datasets
Finds actual downloadable resources instead of guessing URLs
"""

import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
    # Add User-Agent to avoid blocking
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    return session

def download_file(url, filepath, description=""):
    """Download a file with progress tracking"""
    print(f"  Downloading {description}...")
    session = create_session()
    
    try:
        response = session.get(url, timeout=300, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0 and downloaded % (5 * 1024 * 1024) == 0:  # Print every 5MB
                        percent = (downloaded / total_size) * 100
                        print(f"    {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({percent:.1f}%)")
        
        file_size = filepath.stat().st_size
        print(f"    ✓ Downloaded: {file_size / 1024 / 1024:.2f} MB")
        return file_size
    except Exception as e:
        print(f"    ✗ Error: {e}")
        if filepath.exists():
            filepath.unlink()
        return 0

def find_and_download_datagov_datasets():
    """Find and download large datasets from Data.gov"""
    print("\n" + "="*70)
    print("Finding and Downloading Data.gov Large Datasets")
    print("="*70)
    
    session = create_session()
    search_url = "https://catalog.data.gov/api/3/action/package_search"
    
    search_terms = [
        "retail trade",
        "consumer price index",
        "economic census",
        "retail sales",
        "business statistics",
        "commerce data"
    ]
    
    total_bytes = 0
    downloaded_files = []
    
    for term in search_terms:
        print(f"\nSearching for: '{term}'")
        try:
            params = {
                "q": term,
                "rows": 100,
                "sort": "views_recent desc"
            }
            response = session.get(search_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                results = data.get('result', {}).get('results', [])
                print(f"  Found {len(results)} datasets")
                
                for dataset in results[:20]:  # Top 20 per term
                    dataset_name = dataset.get('title', 'unknown')
                    resources = dataset.get('resources', [])
                    
                    # Filter for downloadable resources
                    downloadable = [r for r in resources if r.get('url') and r.get('format') in ['CSV', 'JSON', 'XLSX', 'ZIP']]
                    
                    # Sort by size (largest first) or prioritize CSV
                    downloadable.sort(key=lambda x: (
                        x.get('format') == 'CSV',
                        x.get('size', 0) or 0
                    ), reverse=True)
                    
                    for resource in downloadable[:2]:  # Top 2 per dataset
                        resource_url = resource.get('url')
                        resource_format = resource.get('format', '').upper()
                        resource_size = resource.get('size', 0) or 0
                        
                        # Skip if already downloaded or too small
                        if resource_url in downloaded_files:
                            continue
                        
                        # Create filename
                        resource_id = resource.get('id', 'unknown')
                        filename = f"datagov_{term.replace(' ', '_')}_{resource_id}.{resource_format.lower()}"
                        filepath = extracted_data_dir / filename
                        
                        if filepath.exists():
                            size = filepath.stat().st_size
                            print(f"  Already have: {filename} ({size / 1024 / 1024:.2f} MB)")
                            total_bytes += size
                            downloaded_files.append(resource_url)
                            continue
                        
                        # Download
                        print(f"  Dataset: {dataset_name[:60]}")
                        size = download_file(
                            resource_url,
                            filepath,
                            f"{resource_format} ({resource_size / 1024 / 1024:.1f} MB)" if resource_size > 0 else resource_format
                        )
                        
                        if size > 0:
                            total_bytes += size
                            downloaded_files.append(resource_url)
                            
                            # Stop if we've reached 1 GB
                            if total_bytes >= 1024 * 1024 * 1024:
                                print(f"\n✓ Reached 1 GB target!")
                                return total_bytes
                        
                        time.sleep(1)  # Rate limiting
            
            time.sleep(2)  # Rate limiting between searches
            
        except Exception as e:
            print(f"  Error searching '{term}': {e}")
            continue
    
    return total_bytes

def download_census_api_bulk():
    """Use Census API to get larger datasets"""
    print("\n" + "="*70)
    print("Downloading Census API Data (Bulk Requests)")
    print("="*70)
    
    session = create_session()
    url = "http://api.census.gov/data/timeseries/eits/mrts"
    
    total_bytes = 0
    
    # Get all available NAICS codes and time periods in bulk
    naics_codes = ["44-45", "441", "443", "445", "448", "452"]
    start_year = datetime.now().year - 5
    end_year = datetime.now().year
    
    # Request all months at once for each NAICS code
    for naics in naics_codes:
        try:
            # Request all available time periods
            params = {
                "get": "cell_value,time,NAICS",
                "for": "us:*",
                "NAICS": naics,
                "time": f"{start_year}-01:{end_year}-12"  # Range format
            }
            
            response = session.get(url, params=params, timeout=60)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    filename = f"census_mrts_{naics}_bulk.json"
                    filepath = extracted_data_dir / filename
                    filepath.write_text(json.dumps(data, indent=2))
                    
                    size = len(response.content)
                    total_bytes += size
                    print(f"  ✓ {naics}: {size / 1024 / 1024:.2f} MB")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error {naics}: {e}")
            continue
    
    return total_bytes

def main():
    print("="*70)
    print("Smart Bulk Download Extraction")
    print("Target: 1 GB from real public datasets")
    print("="*70)
    
    start_time = time.time()
    total_bytes = 0
    
    # Strategy: Download from Data.gov (most reliable)
    total_bytes += find_and_download_datagov_datasets()
    
    # If we haven't reached target, try Census API bulk requests
    if total_bytes < 1024 * 1024 * 1024:
        print(f"\nCurrent: {total_bytes / 1024 / 1024 / 1024:.2f} GB, continuing...")
        total_bytes += download_census_api_bulk()
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "="*70)
    print("Extraction Summary")
    print("="*70)
    file_count = len(list(extracted_data_dir.glob('*')))
    print(f"Total Files: {file_count}")
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
        'method': 'smart_bulk_download',
        'file_count': file_count,
        'data_directory': str(extracted_data_dir)
    }
    
    metadata_file = research_dir / 'extraction_metadata.json'
    metadata_file.write_text(json.dumps(metadata, indent=2))
    print(f"\nMetadata saved to: {metadata_file}")

if __name__ == '__main__':
    main()
