#!/usr/bin/env python3
"""
Comprehensive ETL pipeline for extracting data from .gov sources
and transforming to match database schemas.
"""
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE = Path("/Users/machine/Documents/AQ/db")

def extract_data_gov_datasets(db_num, search_terms):
    """Search and extract datasets from Data.gov."""
    logger.info(f"Searching Data.gov for db-{db_num} datasets...")
    
    try:
        # Data.gov CKAN API
        base_url = "https://catalog.data.gov/api/3/action/package_search"
        
        results = []
        for term in search_terms:
            params = {
                'q': term,
                'rows': 20,
                'start': 0
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if 'result' in data and 'results' in data['result']:
                    for dataset in data['result']['results']:
                        results.append({
                            'title': dataset.get('title', ''),
                            'name': dataset.get('name', ''),
                            'url': f"https://catalog.data.gov/dataset/{dataset.get('name', '')}",
                            'tags': dataset.get('tags', []),
                            'resources': len(dataset.get('resources', [])),
                            'extracted_at': datetime.now().isoformat()
                        })
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error searching for '{term}': {e}")
                continue
        
        return results
        
    except Exception as e:
        logger.error(f"Error accessing Data.gov API: {e}")
        return []

def update_source_metadata(db_num, datasets):
    """Update source_metadata.json with extracted datasets."""
    research_dir = BASE / f"db-{db_num}" / "research"
    metadata_file = research_dir / "source_metadata.json"
    
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text())
    else:
        metadata = {
            "database": f"db-{db_num}",
            "sources": [],
            "extraction_history": [],
            "last_updated": ""
        }
    
    # Add new datasets
    for dataset in datasets:
        metadata["sources"].append({
            "source": "Data.gov",
            "dataset": dataset,
            "extracted_at": datetime.now().isoformat()
        })
    
    metadata["last_updated"] = datetime.now().isoformat()
    metadata["extraction_history"].append({
        "timestamp": datetime.now().isoformat(),
        "datasets_found": len(datasets),
        "source": "Data.gov API"
    })
    
    metadata_file.write_text(json.dumps(metadata, indent=2))
    logger.info(f"Updated source_metadata.json for db-{db_num}")

def main():
    """Main ETL pipeline."""
    logger.info("=" * 70)
    logger.info("Comprehensive ETL Pipeline - .gov Data Extraction")
    logger.info("=" * 70)
    
    # Database-specific search terms
    search_terms_by_db = {
        1: ["aviation", "aircraft", "flight", "airport", "faa"],
        2: ["gasoline", "fuel", "petroleum", "gas station", "energy"],
        3: ["ecommerce", "retail", "online sales", "shipping", "commerce"],
        4: ["artificial intelligence", "machine learning", "ai", "neural network"],
        5: ["social media", "communication", "messaging", "chat", "internet"]
    }
    
    for db_num in [1, 2, 3, 4, 5]:
        logger.info(f"\nProcessing db-{db_num}...")
        search_terms = search_terms_by_db.get(db_num, [])
        
        if search_terms:
            datasets = extract_data_gov_datasets(db_num, search_terms)
            if datasets:
                update_source_metadata(db_num, datasets)
                logger.info(f"Found {len(datasets)} datasets for db-{db_num}")
            else:
                logger.warning(f"No datasets found for db-{db_num}")
    
    logger.info("\n" + "=" * 70)
    logger.info("ETL Pipeline Complete")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
