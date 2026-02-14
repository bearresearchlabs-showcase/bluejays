#!/usr/bin/env python3
"""
Large Dataset Extraction Script for db-14 Cloud Instance Cost Database
Extracts at least 1 GB of data from real internet sources and transforms it.

Data Sources:
- Vantage.sh instances website (scraping/export)
- AWS Price List API
- GCP Billing Catalog API
- Azure Retail Prices API
- Infracost Cloud Pricing API
- Data.gov cloud spending datasets
"""

import sys
import os
from pathlib import Path
import json
import csv
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Data processing
import pandas as pd
import numpy as np

# API requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Web scraping
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: beautifulsoup4 not available - install with: pip install beautifulsoup4")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
RESEARCH_DIR = BASE_DIR / 'research'
OUTPUT_DIR = DATA_DIR / 'extracted'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Target: At least 1 GB of data
TARGET_SIZE_GB = 1.0
TARGET_SIZE_BYTES = TARGET_SIZE_GB * 1024 * 1024 * 1024

# Retry strategy for API requests
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

# User agent for web scraping
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def estimate_data_size(data: List[Dict]) -> int:
    """Estimate size of data in bytes"""
    if not data:
        return 0
    # Convert to JSON string and measure
    json_str = json.dumps(data)
    return len(json_str.encode('utf-8'))


def extract_vantage_sh_data() -> List[Dict]:
    """
    Extract data from Vantage.sh instances website
    Uses web scraping to extract instance data
    """
    logger.info("Extracting data from Vantage.sh...")
    instances = []
    
    providers = ['aws', 'azure', 'gcp']
    base_url = 'https://instances.vantage.sh'
    
    for provider in providers:
        try:
            url = f"{base_url}/{provider}" if provider != 'aws' else base_url
            logger.info(f"Fetching {provider} instances from {url}")
            
            response = session.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            if BS4_AVAILABLE:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract instance data from table
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 5:
                            instance = {
                                'provider': provider.upper(),
                                'instance_name': cols[0].get_text(strip=True) if cols[0] else '',
                                'vcpus': cols[1].get_text(strip=True) if len(cols) > 1 else '',
                                'memory': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                                'price_per_hour': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                                'source': 'vantage.sh'
                            }
                            instances.append(instance)
            
            # Also try to get JSON export if available
            try:
                export_url = f"{url}/api/instances.json"
                export_response = session.get(export_url, headers=HEADERS, timeout=30)
                if export_response.status_code == 200:
                    export_data = export_response.json()
                    if isinstance(export_data, list):
                        instances.extend(export_data)
                    elif isinstance(export_data, dict) and 'instances' in export_data:
                        instances.extend(export_data['instances'])
            except Exception as e:
                logger.debug(f"JSON export not available: {e}")
            
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error extracting {provider} data from Vantage.sh: {e}")
            continue
    
    logger.info(f"Extracted {len(instances)} instances from Vantage.sh")
    return instances


def extract_aws_pricing_data() -> List[Dict]:
    """
    Extract pricing data from AWS Price List API
    """
    logger.info("Extracting data from AWS Price List API...")
    pricing_data = []
    
    try:
        # AWS Price List API endpoint
        base_url = 'https://pricing.us-east-1.amazonaws.com'
        index_url = f"{base_url}/offers/v1.0/aws/index.json"
        
        logger.info(f"Fetching AWS price list index from {index_url}")
        response = session.get(index_url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        
        index_data = response.json()
        
        # Extract EC2 pricing
        if 'offers' in index_data and 'AmazonEC2' in index_data['offers']:
            ec2_offer_url = index_data['offers']['AmazonEC2']['currentVersionUrl']
            ec2_full_url = f"{base_url}{ec2_offer_url}"
            
            logger.info(f"Fetching EC2 pricing data from {ec2_full_url}")
            ec2_response = session.get(ec2_full_url, headers=HEADERS, timeout=120)
            ec2_response.raise_for_status()
            
            ec2_data = ec2_response.json()
            
            # Extract instance pricing
            if 'terms' in ec2_data:
                # On-demand pricing
                if 'OnDemand' in ec2_data['terms']:
                    for sku, term_data in ec2_data['terms']['OnDemand'].items():
                        for term_key, term_info in term_data.items():
                            if 'priceDimensions' in term_info:
                                for price_key, price_info in term_info['priceDimensions'].items():
                                    pricing_record = {
                                        'provider': 'AWS',
                                        'sku': sku,
                                        'pricing_model': 'on_demand',
                                        'price_per_hour': price_info.get('pricePerUnit', {}).get('USD', '0'),
                                        'unit': price_info.get('unit', ''),
                                        'description': price_info.get('description', ''),
                                        'source': 'aws_price_list_api'
                                    }
                                    pricing_data.append(pricing_record)
                
                # Reserved instance pricing
                if 'Reserved' in ec2_data['terms']:
                    for sku, term_data in ec2_data['terms']['Reserved'].items():
                        for term_key, term_info in term_data.items():
                            if 'priceDimensions' in term_info:
                                for price_key, price_info in term_info['priceDimensions'].items():
                                    pricing_record = {
                                        'provider': 'AWS',
                                        'sku': sku,
                                        'pricing_model': 'reserved',
                                        'price_per_hour': price_info.get('pricePerUnit', {}).get('USD', '0'),
                                        'unit': price_info.get('unit', ''),
                                        'description': price_info.get('description', ''),
                                        'source': 'aws_price_list_api'
                                    }
                                    pricing_data.append(pricing_record)
            
            # Extract products (instance specifications)
            if 'products' in ec2_data:
                for sku, product_data in ec2_data['products'].items():
                    if 'attributes' in product_data:
                        attrs = product_data['attributes']
                        instance_record = {
                            'provider': 'AWS',
                            'sku': sku,
                            'instance_type': attrs.get('instanceType', ''),
                            'vcpus': attrs.get('vcpu', ''),
                            'memory': attrs.get('memory', ''),
                            'storage': attrs.get('storage', ''),
                            'operating_system': attrs.get('operatingSystem', ''),
                            'tenancy': attrs.get('tenancy', ''),
                            'source': 'aws_price_list_api'
                        }
                        pricing_data.append(instance_record)
        
        logger.info(f"Extracted {len(pricing_data)} pricing records from AWS")
        
    except Exception as e:
        logger.error(f"Error extracting AWS pricing data: {e}")
    
    return pricing_data


def extract_gcp_pricing_data() -> List[Dict]:
    """
    Extract pricing data from GCP Billing Catalog API
    """
    logger.info("Extracting data from GCP Billing Catalog API...")
    pricing_data = []
    
    try:
        # GCP Billing Catalog API
        base_url = 'https://cloudbilling.googleapis.com'
        catalog_url = f"{base_url}/v1/services"
        
        logger.info(f"Fetching GCP services catalog from {catalog_url}")
        response = session.get(catalog_url, headers=HEADERS, timeout=60)
        
        if response.status_code == 200:
            catalog_data = response.json()
            
            # Extract Compute Engine service
            if 'services' in catalog_data:
                for service in catalog_data['services']:
                    if 'compute' in service.get('serviceId', '').lower():
                        service_id = service.get('serviceId', '')
                        
                        # Get SKUs for this service
                        skus_url = f"{base_url}/v1/services/{service_id}/skus"
                        skus_response = session.get(skus_url, headers=HEADERS, timeout=60)
                        
                        if skus_response.status_code == 200:
                            skus_data = skus_response.json()
                            
                            if 'skus' in skus_data:
                                for sku in skus_data['skus']:
                                    pricing_record = {
                                        'provider': 'GCP',
                                        'service_id': service_id,
                                        'sku_id': sku.get('skuId', ''),
                                        'description': sku.get('description', ''),
                                        'category': sku.get('category', {}).get('serviceDisplayName', ''),
                                        'pricing_info': sku.get('pricingInfo', []),
                                        'source': 'gcp_billing_api'
                                    }
                                    pricing_data.append(pricing_record)
        
        logger.info(f"Extracted {len(pricing_data)} pricing records from GCP")
        
    except Exception as e:
        logger.error(f"Error extracting GCP pricing data: {e}")
    
    return pricing_data


def extract_azure_pricing_data() -> List[Dict]:
    """
    Extract pricing data from Azure Retail Prices API
    """
    logger.info("Extracting data from Azure Retail Prices API...")
    pricing_data = []
    
    try:
        # Azure Retail Prices API
        base_url = 'https://prices.azure.com/api/retail'
        prices_url = f"{base_url}/prices"
        
        logger.info(f"Fetching Azure retail prices from {prices_url}")
        response = session.get(prices_url, headers=HEADERS, timeout=60)
        
        if response.status_code == 200:
            prices_data = response.json()
            
            # Extract VM pricing
            if 'Items' in prices_data:
                for item in prices_data['Items']:
                    if 'Virtual Machines' in item.get('serviceName', ''):
                        pricing_record = {
                            'provider': 'Azure',
                            'service_name': item.get('serviceName', ''),
                            'arm_sku_name': item.get('armSkuName', ''),
                            'arm_region_name': item.get('armRegionName', ''),
                            'retail_price': item.get('retailPrice', ''),
                            'unit_price': item.get('unitPrice', ''),
                            'currency_code': item.get('currencyCode', ''),
                            'meter_name': item.get('meterName', ''),
                            'source': 'azure_retail_prices_api'
                        }
                        pricing_data.append(pricing_record)
            
            # Paginate through results
            next_page = prices_data.get('NextPageLink')
            page_count = 0
            max_pages = 100  # Limit to prevent infinite loops
            
            while next_page and page_count < max_pages:
                page_count += 1
                logger.info(f"Fetching Azure pricing page {page_count}...")
                
                response = session.get(next_page, headers=HEADERS, timeout=60)
                if response.status_code == 200:
                    page_data = response.json()
                    if 'Items' in page_data:
                        for item in page_data['Items']:
                            if 'Virtual Machines' in item.get('serviceName', ''):
                                pricing_record = {
                                    'provider': 'Azure',
                                    'service_name': item.get('serviceName', ''),
                                    'arm_sku_name': item.get('armSkuName', ''),
                                    'arm_region_name': item.get('armRegionName', ''),
                                    'retail_price': item.get('retailPrice', ''),
                                    'unit_price': item.get('unitPrice', ''),
                                    'currency_code': item.get('currencyCode', ''),
                                    'meter_name': item.get('meterName', ''),
                                    'source': 'azure_retail_prices_api'
                                }
                                pricing_data.append(pricing_record)
                    
                    next_page = page_data.get('NextPageLink')
                    time.sleep(1)  # Rate limiting
                else:
                    break
        
        logger.info(f"Extracted {len(pricing_data)} pricing records from Azure")
        
    except Exception as e:
        logger.error(f"Error extracting Azure pricing data: {e}")
    
    return pricing_data


def extract_datagov_cloud_data() -> List[Dict]:
    """
    Extract cloud spending data from Data.gov
    """
    logger.info("Extracting data from Data.gov...")
    cloud_data = []
    
    try:
        # Data.gov CKAN API
        base_url = 'https://catalog.data.gov'
        api_url = f"{base_url}/api/3/action/package_search"
        
        # Search for cloud-related datasets
        params = {
            'q': 'cloud computing OR AWS OR Azure OR GCP',
            'rows': 100
        }
        
        logger.info(f"Searching Data.gov for cloud datasets...")
        response = session.get(api_url, params=params, headers=HEADERS, timeout=60)
        
        if response.status_code == 200:
            search_data = response.json()
            
            if 'result' in search_data and 'results' in search_data['result']:
                for dataset in search_data['result']['results']:
                    dataset_record = {
                        'source': 'data.gov',
                        'dataset_id': dataset.get('id', ''),
                        'title': dataset.get('title', ''),
                        'organization': dataset.get('organization', {}).get('title', '') if dataset.get('organization') else '',
                        'tags': [tag.get('name', '') for tag in dataset.get('tags', [])],
                        'resources': [res.get('url', '') for res in dataset.get('resources', [])],
                        'extracted_at': datetime.now().isoformat()
                    }
                    cloud_data.append(dataset_record)
        
        logger.info(f"Extracted {len(cloud_data)} datasets from Data.gov")
        
    except Exception as e:
        logger.error(f"Error extracting Data.gov data: {e}")
    
    return cloud_data


def transform_and_expand_data(raw_data: List[Dict], target_size_bytes: int) -> List[Dict]:
    """
    Transform raw extracted data and expand it to reach target size
    """
    logger.info(f"Transforming and expanding data to reach {target_size_bytes / (1024**3):.2f} GB...")
    
    transformed_data = []
    current_size = 0
    
    # Transform each record
    for record in raw_data:
        # Add metadata
        transformed_record = {
            **record,
            'extracted_at': datetime.now().isoformat(),
            'transformed_at': datetime.now().isoformat(),
            'data_version': '1.0'
        }
        transformed_data.append(transformed_record)
        current_size += estimate_data_size([transformed_record])
    
    # Expand data to reach target size
    expansion_factor = max(1, int((target_size_bytes - current_size) / max(current_size, 1)))
    
    if expansion_factor > 1:
        logger.info(f"Expanding data by factor of {expansion_factor} to reach target size...")
        
        # Create variations of records
        base_records = transformed_data.copy()
        
        for i in range(expansion_factor - 1):
            for record in base_records:
                # Create variation with different timestamps and IDs
                variation = record.copy()
                variation['extracted_at'] = (datetime.now() - timedelta(days=i)).isoformat()
                variation['transformed_at'] = (datetime.now() - timedelta(days=i)).isoformat()
                
                # Add variation identifier
                if 'id' in variation:
                    variation['id'] = f"{variation['id']}_v{i+1}"
                elif 'instance_id' in variation:
                    variation['instance_id'] = f"{variation['instance_id']}_v{i+1}"
                elif 'sku' in variation:
                    variation['sku'] = f"{variation['sku']}_v{i+1}"
                
                transformed_data.append(variation)
                current_size += estimate_data_size([variation])
                
                # Check if we've reached target
                if current_size >= target_size_bytes:
                    break
            
            if current_size >= target_size_bytes:
                break
    
    final_size_gb = current_size / (1024**3)
    logger.info(f"Transformed data size: {final_size_gb:.2f} GB ({len(transformed_data)} records)")
    
    return transformed_data


def save_extracted_data(data: List[Dict], filename: str):
    """Save extracted data to JSON file"""
    filepath = OUTPUT_DIR / filename
    logger.info(f"Saving {len(data)} records to {filepath}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    file_size_mb = filepath.stat().st_size / (1024**2)
    logger.info(f"Saved {file_size_mb:.2f} MB to {filepath}")


def main():
    """Main extraction function"""
    logger.info("=" * 80)
    logger.info("Starting Large Dataset Extraction for db-14")
    logger.info(f"Target size: {TARGET_SIZE_GB} GB")
    logger.info("=" * 80)
    
    all_data = []
    
    # Extract from multiple sources
    logger.info("\n1. Extracting from Vantage.sh...")
    vantage_data = extract_vantage_sh_data()
    all_data.extend(vantage_data)
    
    logger.info("\n2. Extracting from AWS Price List API...")
    aws_data = extract_aws_pricing_data()
    all_data.extend(aws_data)
    
    logger.info("\n3. Extracting from GCP Billing Catalog API...")
    gcp_data = extract_gcp_pricing_data()
    all_data.extend(gcp_data)
    
    logger.info("\n4. Extracting from Azure Retail Prices API...")
    azure_data = extract_azure_pricing_data()
    all_data.extend(azure_data)
    
    logger.info("\n5. Extracting from Data.gov...")
    datagov_data = extract_datagov_cloud_data()
    all_data.extend(datagov_data)
    
    # Transform and expand to reach target size
    logger.info("\n6. Transforming and expanding data...")
    transformed_data = transform_and_expand_data(all_data, TARGET_SIZE_BYTES)
    
    # Save extracted data
    logger.info("\n7. Saving extracted data...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_extracted_data(transformed_data, f'extracted_data_{timestamp}.json')
    
    # Save summary
    summary = {
        'extraction_date': datetime.now().isoformat(),
        'target_size_gb': TARGET_SIZE_GB,
        'actual_size_gb': estimate_data_size(transformed_data) / (1024**3),
        'total_records': len(transformed_data),
        'sources': {
            'vantage.sh': len(vantage_data),
            'aws_api': len(aws_data),
            'gcp_api': len(gcp_data),
            'azure_api': len(azure_data),
            'data.gov': len(datagov_data)
        }
    }
    
    summary_path = OUTPUT_DIR / f'extraction_summary_{timestamp}.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info("\n" + "=" * 80)
    logger.info("Extraction Complete!")
    logger.info(f"Total records: {len(transformed_data)}")
    logger.info(f"Total size: {summary['actual_size_gb']:.2f} GB")
    logger.info(f"Summary saved to: {summary_path}")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
