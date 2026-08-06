#!/usr/bin/env python3
"""
Quick extraction script - extracts real data efficiently for 1 GB target
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
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def extract_census_data():
    """Extract Census MRTS data"""
    print("Extracting Census Bureau MRTS data...")
    session = create_session()
    url = "http://api.census.gov/data/timeseries/eits/mrts"
    
    records = 0
    bytes_extracted = 0
    
    naics_codes = ["44-45", "441", "443", "445", "448", "452"]
    start_year = datetime.now().year - 5
    end_year = datetime.now().year
    
    for naics in naics_codes:
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                try:
                    params = {
                        "get": "cell_value,time,NAICS",
                        "for": "us:*",
                        "NAICS": naics,
                        "time": f"{year}-{month:02d}"
                    }
                    response = session.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        if len(data) > 1:
                            filename = f"census_mrts_{naics}_{year}_{month:02d}.json"
                            filepath = extracted_data_dir / filename
                            filepath.write_text(json.dumps(data))
                            bytes_extracted += len(response.content)
                            records += len(data) - 1
                    time.sleep(0.3)
                except Exception as e:
                    print(f"  Error {naics} {year}-{month:02d}: {e}")
                    continue
    
    print(f"  ✓ Census: {records} records, {bytes_extracted / 1024 / 1024:.2f} MB")
    return bytes_extracted

def extract_bls_data():
    """Extract BLS price index data"""
    print("Extracting BLS price index data...")
    session = create_session()
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data"
    
    series_ids = [
        "CUUR0000SA0", "CUUR0000SETB01", "CUUR0000SEEE01", "CUUR0000SEGA",
        "CUUR0000SEHF", "CUUR0000SEHA", "CUUR0000SETA", "CUUR0000SETD",
        "CUUR0000SEGC", "CUUR0000SEGD", "CUUR0000SEGE", "CUUR0000SERG",
        "CUUR0000SERJ", "CUUR0000SERO", "CUUR0000SERP"
    ]
    
    start_year = datetime.now().year - 5
    end_year = datetime.now().year
    
    bytes_extracted = 0
    
    # Process in batches of 50
    for i in range(0, len(series_ids), 50):
        batch = series_ids[i:i+50]
        try:
            payload = {
                "seriesid": batch,
                "startyear": str(start_year),
                "endyear": str(end_year)
            }
            response = session.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'REQUEST_SUCCEEDED':
                    filename = f"bls_batch_{i//50 + 1}.json"
                    filepath = extracted_data_dir / filename
                    filepath.write_text(json.dumps(data, indent=2))
                    bytes_extracted += len(response.content)
            time.sleep(1)
        except Exception as e:
            print(f"  Error batch {i//50 + 1}: {e}")
            continue
    
    print(f"  ✓ BLS: {bytes_extracted / 1024 / 1024:.2f} MB")
    return bytes_extracted

def extract_datagov():
    """Extract Data.gov datasets"""
    print("Extracting Data.gov datasets...")
    session = create_session()
    url = "https://catalog.data.gov/api/3/action/package_search"
    
    search_terms = ["retail", "consumer", "pricing", "sales", "commerce", "market"]
    bytes_extracted = 0
    
    for term in search_terms:
        try:
            params = {"q": term, "rows": 20}
            response = session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                results = data.get('result', {}).get('results', [])
                
                for dataset in results[:10]:
                    resources = dataset.get('resources', [])
                    for resource in resources[:2]:  # Limit to 2 resources per dataset
                        if resource.get('format', '').upper() in ['CSV', 'JSON']:
                            resource_url = resource.get('url')
                            if resource_url and resource_url.startswith('http'):
                                try:
                                    res_response = session.get(resource_url, timeout=60, stream=True)
                                    if res_response.status_code == 200:
                                        resource_id = resource.get('id', 'unknown')
                                        format_ext = resource.get('format', 'csv').lower()
                                        filename = f"datagov_{term}_{resource_id}.{format_ext}"
                                        filepath = extracted_data_dir / filename
                                        
                                        with open(filepath, 'wb') as f:
                                            for chunk in res_response.iter_content(chunk_size=8192):
                                                f.write(chunk)
                                        
                                        bytes_extracted += filepath.stat().st_size
                                except Exception as e:
                                    continue
            time.sleep(1)
        except Exception as e:
            print(f"  Error searching '{term}': {e}")
            continue
    
    print(f"  ✓ Data.gov: {bytes_extracted / 1024 / 1024:.2f} MB")
    return bytes_extracted

def main():
    print("="*70)
    print("Quick Data Extraction - Real Data Only")
    print("="*70)
    
    start_time = time.time()
    total_bytes = 0
    
    total_bytes += extract_census_data()
    total_bytes += extract_bls_data()
    total_bytes += extract_datagov()
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    print("Extraction Summary")
    print("="*70)
    print(f"Total Size: {total_bytes / 1024 / 1024 / 1024:.2f} GB")
    print(f"Time: {elapsed / 60:.2f} minutes")
    print("="*70)

if __name__ == '__main__':
    main()
