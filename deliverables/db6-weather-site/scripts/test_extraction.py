#!/usr/bin/env python3
"""
Test Extraction Script - Verifies bulk extraction system works
Runs a small test extraction (100 MB) to verify connectivity and functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.bulk_data_extractor import BulkDataExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_extraction(db_name: str):
    """Run a small test extraction."""
    logger.info(f"Testing extraction for {db_name}")
    
    extractor = BulkDataExtractor(db_name)
    
    # Run small test extraction (100 MB target)
    extractor.run_extraction(target_size_gb=0.1)
    
    # Check results
    if extractor.total_bytes > 0:
        logger.info(f"✓ Test successful: {extractor.total_bytes / (1024*1024):.2f} MB extracted")
        return True
    else:
        logger.warning("⚠ Test extracted 0 bytes - check API connectivity")
        return False

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('db_name', choices=['db-7', 'db-9', 'db-11'])
    args = parser.parse_args()
    
    success = test_extraction(args.db_name)
    sys.exit(0 if success else 1)
