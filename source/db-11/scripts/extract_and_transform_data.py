#!/usr/bin/env python3
"""
Data Extraction and Transformation Script for db-11 Parking Intelligence Database
Pulls 1 GB of data from internet sources and transforms it for database loading
"""

import os
import sys
import json
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import gzip
import zipfile
import io

# Geospatial libraries
try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon
    from shapely import wkt
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    print("Warning: geopandas/shapely not available - geospatial features limited")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SCRIPT_DIR = Path(__file__).parent
DB_DIR = SCRIPT_DIR.parent
RESEARCH_DIR = DB_DIR / 'research'
DATA_DIR = DB_DIR / 'data'
METADATA_DIR = DB_DIR / 'metadata'
EXTRACTED_DATA_DIR = RESEARCH_DIR / 'extracted_data'
EXTRACTED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Target data size: 1 GB
TARGET_DATA_SIZE_GB_MIN = 1.0
TARGET_DATA_SIZE_GB_MAX = 1.0

# API Configuration
DATA_GOV_API_KEY = os.environ.get('DATA_GOV_API_KEY')
DATA_GOV_CKAN_BASE_URL = "https://catalog.data.gov/api/3/action"
CENSUS_API_KEY = os.environ.get('CENSUS_API_KEY')
CENSUS_BASE_URL = "https://api.census.gov/data"
NWS_BASE_URL = "https://api.weather.gov"
GEOPLATFORM_BASE_URL = "https://geoapi.geoplatform.gov"

# Track extracted data size
extracted_data_size_bytes = 0
extraction_metadata = {
    'start_time': datetime.now().isoformat(),
    'sources': {},
    'total_records': 0,
    'total_size_bytes': 0,
    'files_extracted': []
}

def create_session_with_retry() -> requests.Session:
    """Create requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def download_file(url: str, output_path: Path, session: Optional[requests.Session] = None) -> Tuple[bool, int]:
    """Download a file and return success status and size in bytes"""
    if session is None:
        session = create_session_with_retry()
    
    try:
        response = session.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        file_size = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    file_size += len(chunk)
        
        logger.info(f"Downloaded {output_path.name}: {file_size / (1024*1024):.2f} MB")
        return True, file_size
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False, 0

def extract_data_gov_parking_datasets(limit: int = 200) -> Dict:
    """Extract parking datasets from Data.gov CKAN API"""
    global extracted_data_size_bytes
    logger.info("Extracting Data.gov parking datasets...")
    session = create_session_with_retry()
    
    datasets_found = []
    start = 0
    rows = 100
    
    headers = {}
    if DATA_GOV_API_KEY:
        headers["X-API-Key"] = DATA_GOV_API_KEY
    
    while len(datasets_found) < limit:
        url = f"{DATA_GOV_CKAN_BASE_URL}/package_search"
        params = {
            "q": "parking",
            "rows": rows,
            "start": start
        }
        
        try:
            response = session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                results = data.get('result', {}).get('results', [])
                if not results:
                    break
                
                for dataset in results:
                    # Extract resource URLs
                    resources = dataset.get('resources', [])
                    for resource in resources:
                        if resource.get('format', '').upper() in ['CSV', 'JSON', 'GEOJSON', 'SHP', 'ZIP']:
                            datasets_found.append({
                                'dataset_id': dataset.get('id'),
                                'title': dataset.get('title'),
                                'resource_id': resource.get('id'),
                                'resource_url': resource.get('url'),
                                'format': resource.get('format', '').upper(),
                                'size': resource.get('size', 0)
                            })
                
                start += rows
                if start >= data.get('result', {}).get('count', 0):
                    break
            else:
                break
                
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            logger.error(f"Error fetching Data.gov datasets: {e}")
            break
    
    logger.info(f"Found {len(datasets_found)} parking dataset resources")
    
    # Download datasets - prioritize larger files to reach 1 GB target
    # Sort by size (largest first) if available, handling None values
    datasets_to_download = datasets_found[:limit]
    datasets_to_download.sort(key=lambda x: x.get('size', 0) or 0, reverse=True)
    
    downloaded_files = []
    for i, dataset in enumerate(datasets_to_download):
        resource_url = dataset['resource_url']
        if not resource_url:
            continue
        
        file_ext = dataset['format'].lower() if dataset['format'] else 'csv'
        output_file = EXTRACTED_DATA_DIR / f"datagov_parking_{dataset['dataset_id']}_{dataset['resource_id']}.{file_ext}"
        
        success, size = download_file(resource_url, output_file, session)
        if success:
            downloaded_files.append({
                'source': 'data_gov',
                'file': str(output_file),
                'size_bytes': size,
                'dataset_id': dataset['dataset_id'],
                'title': dataset['title']
            })
            extracted_data_size_bytes += size
            extraction_metadata['total_size_bytes'] += size
            extraction_metadata['files_extracted'].append(str(output_file))
        
        if (i + 1) % 10 == 0:
            current_gb = extracted_data_size_bytes / (1024 * 1024 * 1024)
            logger.info(f"Downloaded {i + 1}/{len(datasets_to_download)} files... ({current_gb:.2f} GB so far)")
            time.sleep(1)  # Rate limiting
        
        # Check if we've reached minimum target early
        if extracted_data_size_bytes >= TARGET_DATA_SIZE_GB_MIN * (1024 * 1024 * 1024):
            logger.info(f"✓ Reached minimum target ({TARGET_DATA_SIZE_GB_MIN} GB). Continuing to maximum...")
    
    extraction_metadata['sources']['data_gov'] = {
        'datasets_found': len(datasets_found),
        'files_downloaded': len(downloaded_files),
        'total_size_mb': sum(f['size_bytes'] for f in downloaded_files) / (1024*1024)
    }
    
    return {'downloaded_files': downloaded_files, 'datasets_found': len(datasets_found)}

def extract_census_data() -> Dict:
    """Extract Census Bureau demographic data for metropolitan areas and cities"""
    global extracted_data_size_bytes
    logger.info("Extracting Census Bureau data...")
    session = create_session_with_retry()
    
    current_year = datetime.now().year
    year = current_year - 1  # Use most recent available year
    
    # Fetch MSA data
    msa_data_files = []
    
    # ACS 5-year estimates for MSAs
    acs_variables = [
        "B01001_001E",  # Total population
        "B19013_001E",  # Median household income
        "B25064_001E",  # Median gross rent
        "B08301_001E",  # Means of transportation to work
        "B15003_001E",  # Educational attainment
    ]
    
    for var_group in [acs_variables[i:i+5] for i in range(0, len(acs_variables), 5)]:
        url = f"{CENSUS_BASE_URL}/{year}/acs/acs5"
        params = {
            "get": ",".join(var_group),
            "for": "metropolitan statistical area/micropolitan statistical area:*"
        }
        if CENSUS_API_KEY:
            params["key"] = CENSUS_API_KEY
        
        try:
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data:
                output_file = EXTRACTED_DATA_DIR / f"census_msa_{year}_{var_group[0]}.json"
                with open(output_file, 'w') as f:
                    json.dump(data, f)
                
                file_size = output_file.stat().st_size
                msa_data_files.append({
                    'source': 'census_msa',
                    'file': str(output_file),
                    'size_bytes': file_size,
                    'year': year,
                    'variables': var_group
                })
                extracted_data_size_bytes += file_size
                extraction_metadata['total_size_bytes'] += file_size
                extraction_metadata['files_extracted'].append(str(output_file))
            
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            logger.error(f"Error fetching Census MSA data: {e}")
    
    # Fetch city-level data
    city_data_files = []
    url = f"{CENSUS_BASE_URL}/{year}/acs/acs5"
    params = {
        "get": "B01001_001E,B19013_001E",
        "for": "place:*",
        "in": "state:*"
    }
    if CENSUS_API_KEY:
        params["key"] = CENSUS_API_KEY
    
    try:
        response = session.get(url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if data:
            output_file = EXTRACTED_DATA_DIR / f"census_cities_{year}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f)
            
            file_size = output_file.stat().st_size
            city_data_files.append({
                'source': 'census_cities',
                'file': str(output_file),
                'size_bytes': file_size,
                'year': year,
                'record_count': len(data) - 1 if data else 0
            })
            extracted_data_size_bytes += file_size
            extraction_metadata['total_size_bytes'] += file_size
            extraction_metadata['files_extracted'].append(str(output_file))
            extraction_metadata['total_records'] += len(data) - 1 if data else 0
    except Exception as e:
        logger.error(f"Error fetching Census city data: {e}")
    
    extraction_metadata['sources']['census'] = {
        'msa_files': len(msa_data_files),
        'city_files': len(city_data_files),
        'total_size_mb': sum(f['size_bytes'] for f in msa_data_files + city_data_files) / (1024*1024)
    }
    
    return {'msa_files': msa_data_files, 'city_files': city_data_files}

def extract_airport_data() -> Dict:
    """Extract airport passenger volume data"""
    global extracted_data_size_bytes
    logger.info("Extracting airport data...")
    
    # BTS TranStats - Airport passenger data
    # Note: This may require web scraping or CSV downloads
    # For now, we'll use a known data source
    
    airport_data_files = []
    
    # FAA Airport Data - Passenger boarding statistics
    # Using a known CSV source for airport data
    faa_urls = [
        "https://www.faa.gov/airports/planning_capacity/passenger_allcargo_stats/passenger/media/cy23-commercial-service-enplanements.xlsx",
    ]
    
    session = create_session_with_retry()
    for url in faa_urls:
        try:
            output_file = EXTRACTED_DATA_DIR / f"faa_airports_{datetime.now().year}.xlsx"
            success, size = download_file(url, output_file, session)
            if success:
                airport_data_files.append({
                    'source': 'faa_airports',
                    'file': str(output_file),
                    'size_bytes': size
                })
                extracted_data_size_bytes += size
                extraction_metadata['total_size_bytes'] += size
                extraction_metadata['files_extracted'].append(str(output_file))
        except Exception as e:
            logger.warning(f"Could not download FAA airport data: {e}")
    
    extraction_metadata['sources']['airports'] = {
        'files_downloaded': len(airport_data_files),
        'total_size_mb': sum(f['size_bytes'] for f in airport_data_files) / (1024*1024)
    }
    
    return {'airport_files': airport_data_files}

def extract_traffic_data() -> Dict:
    """Extract FHWA traffic volume data"""
    global extracted_data_size_bytes
    logger.info("Extracting FHWA traffic data...")
    
    traffic_data_files = []
    session = create_session_with_retry()
    
    # FHWA Traffic Volume Trends
    # Note: May require manual download or parsing
    # Using known data sources
    
    fhwa_urls = [
        "https://www.fhwa.dot.gov/policyinformation/tables/trafficmonitoring/23tvt.cfm",  # HTML table
    ]
    
    # For now, create a placeholder - actual extraction would require HTML parsing
    logger.info("FHWA traffic data extraction requires HTML parsing - placeholder created")
    
    extraction_metadata['sources']['traffic'] = {
        'files_downloaded': len(traffic_data_files),
        'total_size_mb': 0
    }
    
    return {'traffic_files': traffic_data_files}

def extract_city_open_data() -> Dict:
    """Extract data from city open data portals"""
    global extracted_data_size_bytes
    logger.info("Extracting city open data...")
    
    city_data_files = []
    session = create_session_with_retry()
    
    # Major city open data portals with parking data
    city_portals = {
        'seattle': {
            'base_url': 'https://data.seattle.gov',
            'datasets': [
                'public-garages-and-parking-lots-5b51c',  # Public Garages and Parking Lots
            ]
        },
        'san_francisco': {
            'base_url': 'https://data.sfgov.org',
            'datasets': [
                'vw6y-t8j8',  # Parking Meters
            ]
        },
        'austin': {
            'base_url': 'https://data.austintexas.gov',
            'datasets': [
                'nz5j-4t7f',  # Off-Street Parking
            ]
        },
        'philadelphia': {
            'base_url': 'https://www.opendataphilly.org',
            'datasets': [
                'parking-locator',  # Parking Locator
            ]
        },
        'chicago': {
            'base_url': 'https://data.cityofchicago.org',
            'datasets': [
                'wrvz-psew',  # Parking Meters
            ]
        },
        'new_york': {
            'base_url': 'https://data.cityofnewyork.us',
            'datasets': [
                'n4ac-36gg',  # Parking Violations
            ]
        },
        'los_angeles': {
            'base_url': 'https://data.lacity.org',
            'datasets': [
                'wjz9-h9np',  # Parking Meters
            ]
        },
        'boston': {
            'base_url': 'https://data.boston.gov',
            'datasets': [
                'meter-feeder-data',  # Meter Feeder Data
            ]
        },
        'denver': {
            'base_url': 'https://www.denvergov.org',
            'datasets': [
                'parking-meters',  # Parking Meters
            ]
        },
        'portland': {
            'base_url': 'https://www.portlandoregon.gov',
            'datasets': [
                'parking-meters',  # Parking Meters
            ]
        },
        'washington_dc': {
            'base_url': 'https://opendata.dc.gov',
            'datasets': [
                'parking-meters',  # Parking Meters
            ]
        },
        'miami': {
            'base_url': 'https://www.miamigov.com',
            'datasets': [
                'parking-facilities',  # Parking Facilities
            ]
        },
        'dallas': {
            'base_url': 'https://www.dallasopendata.com',
            'datasets': [
                'parking-meters',  # Parking Meters
            ]
        },
        'houston': {
            'base_url': 'https://data.houstontx.gov',
            'datasets': [
                'parking-meters',  # Parking Meters
            ]
        },
        'phoenix': {
            'base_url': 'https://www.phoenixopendata.com',
            'datasets': [
                'parking-facilities',  # Parking Facilities
            ]
        }
    }
    
    for city, config in city_portals.items():
        base_url = config['base_url']
        for dataset_id in config['datasets']:
            try:
                # Try Socrata API format (used by many cities)
                socrata_url = f"{base_url}/resource/{dataset_id}.json"
                # Increase limit to pull more data (up to 500k records per dataset for larger cities)
                # This helps reach 1 GB target
                response = session.get(socrata_url, params={'$limit': 500000}, timeout=180)
                
                if response.status_code == 200:
                    data = response.json()
                    output_file = EXTRACTED_DATA_DIR / f"{city}_parking_{dataset_id}.json"
                    with open(output_file, 'w') as f:
                        json.dump(data, f)
                    
                    file_size = output_file.stat().st_size
                    city_data_files.append({
                        'source': f'{city}_open_data',
                        'file': str(output_file),
                        'size_bytes': file_size,
                        'record_count': len(data) if isinstance(data, list) else 0
                    })
                    extracted_data_size_bytes += file_size
                    extraction_metadata['total_size_bytes'] += file_size
                    extraction_metadata['files_extracted'].append(str(output_file))
                    extraction_metadata['total_records'] += len(data) if isinstance(data, list) else 0
                    
                    logger.info(f"Downloaded {city} parking data: {file_size / (1024*1024):.2f} MB")
                
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.warning(f"Could not download {city} data: {e}")
    
    extraction_metadata['sources']['city_open_data'] = {
        'cities_processed': len(city_portals),
        'files_downloaded': len(city_data_files),
        'total_size_mb': sum(f['size_bytes'] for f in city_data_files) / (1024*1024)
    }
    
    return {'city_files': city_data_files}

def check_data_size() -> Tuple[float, bool]:
    """Check if we've reached target data size"""
    total_gb = extracted_data_size_bytes / (1024 * 1024 * 1024)
    meets_minimum = total_gb >= TARGET_DATA_SIZE_GB_MIN
    return total_gb, meets_minimum

def save_extraction_metadata():
    """Save extraction metadata to JSON file"""
    extraction_metadata['end_time'] = datetime.now().isoformat()
    extraction_metadata['total_size_gb'] = extracted_data_size_bytes / (1024 * 1024 * 1024)
    
    metadata_file = METADATA_DIR / 'data_extraction_metadata.json'
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(metadata_file, 'w') as f:
        json.dump(extraction_metadata, f, indent=2)
    
    logger.info(f"Extraction metadata saved to {metadata_file}")

def main():
    """Main data extraction function"""
    logger.info("="*70)
    logger.info("Data Extraction and Transformation - db-11 Parking Intelligence")
    logger.info("="*70)
    logger.info(f"Target data size: {TARGET_DATA_SIZE_GB_MIN}-{TARGET_DATA_SIZE_GB_MAX} GB (minimum: {TARGET_DATA_SIZE_GB_MIN} GB)")
    logger.info(f"Output directory: {EXTRACTED_DATA_DIR}")
    
    # Extract data from all sources
    results = {}
    
    # 1. Data.gov parking datasets (largest source)
    logger.info("\n" + "="*70)
    logger.info("Phase 1: Data.gov Parking Datasets")
    logger.info("="*70)
    # Extract more datasets to reach 1 GB target size
    results['data_gov'] = extract_data_gov_parking_datasets(limit=200)
    total_gb, meets_min = check_data_size()
    logger.info(f"Current data size: {total_gb:.2f} GB (Minimum: {meets_min})")
    
    # 2. Census Bureau data
    logger.info("\n" + "="*70)
    logger.info("Phase 2: Census Bureau Data")
    logger.info("="*70)
    results['census'] = extract_census_data()
    total_gb, meets_min = check_data_size()
    logger.info(f"Current data size: {total_gb:.2f} GB (Minimum: {meets_min})")
    
    # 3. Airport data
    logger.info("\n" + "="*70)
    logger.info("Phase 3: Airport Data")
    logger.info("="*70)
    results['airports'] = extract_airport_data()
    total_gb, meets_min = check_data_size()
    logger.info(f"Current data size: {total_gb:.2f} GB (Minimum: {meets_min})")
    
    # 4. City open data portals
    logger.info("\n" + "="*70)
    logger.info("Phase 4: City Open Data Portals")
    logger.info("="*70)
    results['city_data'] = extract_city_open_data()
    total_gb, meets_min = check_data_size()
    logger.info(f"Current data size: {total_gb:.2f} GB (Minimum: {meets_min})")
    
    # Continue extracting if we haven't reached minimum
    if not meets_min:
        logger.info(f"\n⚠️  Current size ({total_gb:.2f} GB) below minimum ({TARGET_DATA_SIZE_GB_MIN} GB)")
        logger.info("Extracting additional Data.gov datasets to reach minimum...")
        # Estimate additional datasets needed (roughly 100 datasets per GB)
        additional_limit = max(100, int((TARGET_DATA_SIZE_GB_MIN - total_gb) * 100))
        additional_results = extract_data_gov_parking_datasets(limit=additional_limit)
        results['data_gov_additional'] = additional_results
        total_gb, meets_min = check_data_size()
        logger.info(f"After additional extraction: {total_gb:.2f} GB (Minimum: {meets_min})")
    
    # 5. Traffic data
    logger.info("\n" + "="*70)
    logger.info("Phase 5: FHWA Traffic Data")
    logger.info("="*70)
    results['traffic'] = extract_traffic_data()
    
    # Final summary
    total_gb, meets_min = check_data_size()
    logger.info("\n" + "="*70)
    logger.info("Extraction Summary")
    logger.info("="*70)
    logger.info(f"Total data extracted: {total_gb:.2f} GB")
    logger.info(f"Minimum target ({TARGET_DATA_SIZE_GB_MIN} GB): {'✓ MET' if meets_min else '✗ NOT MET'}")
    if not meets_min:
        logger.warning(f"⚠️  WARNING: Data size ({total_gb:.2f} GB) is below minimum target ({TARGET_DATA_SIZE_GB_MIN} GB)")
        logger.warning("   Consider running extraction again or adding more data sources")
    logger.info(f"Files extracted: {len(extraction_metadata['files_extracted'])}")
    logger.info(f"Total records: {extraction_metadata['total_records']:,}")
    
    # Save metadata
    save_extraction_metadata()
    
    logger.info("\n" + "="*70)
    logger.info("Data extraction complete!")
    logger.info("="*70)
    logger.info(f"Extracted data location: {EXTRACTED_DATA_DIR}")
    logger.info(f"Metadata location: {METADATA_DIR / 'data_extraction_metadata.json'}")
    
    return results

if __name__ == '__main__':
    main()
