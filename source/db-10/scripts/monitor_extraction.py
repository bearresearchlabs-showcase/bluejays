#!/usr/bin/env python3
"""
Monitor data extraction progress and report data volume
"""

import json
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
research_dir = script_dir.parent / 'research'
extracted_data_dir = research_dir / 'extracted_data'
metadata_file = research_dir / 'extraction_metadata.json'

def get_directory_size(path: Path) -> int:
    """Get total size of directory in bytes"""
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except Exception:
        pass
    return total

def count_files(path: Path) -> int:
    """Count files in directory"""
    try:
        return len(list(path.rglob('*'))) - len(list(path.rglob('*/')))  # Subtract directories
    except Exception:
        return 0

def main():
    print("="*70)
    print("Data Extraction Progress Monitor")
    print("="*70)
    
    if not extracted_data_dir.exists():
        print(f"Extraction directory not found: {extracted_data_dir}")
        return
    
    # Count files
    file_count = count_files(extracted_data_dir)
    
    # Calculate size
    total_bytes = get_directory_size(extracted_data_dir)
    total_mb = total_bytes / 1024 / 1024
    total_gb = total_bytes / 1024 / 1024 / 1024
    
    print(f"\nExtracted Data Directory: {extracted_data_dir}")
    print(f"Files Extracted: {file_count}")
    print(f"Total Size: {total_gb:.2f} GB ({total_mb:.2f} MB)")
    
    # Check metadata
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        print(f"\nExtraction Metadata:")
        print(f"  Timestamp: {metadata.get('extraction_timestamp', 'N/A')}")
        print(f"  Records: {metadata.get('total_records', 0):,}")
        print(f"  Time Range: {metadata.get('time_range', {}).get('start_year', 'N/A')} - {metadata.get('time_range', {}).get('end_year', 'N/A')}")
    
    # Progress towards target
    target_gb = 1.0
    
    print(f"\nTarget: {target_gb} GB")
    if total_gb < target_gb:
        progress = (total_gb / target_gb) * 100
        print(f"Progress: {progress:.1f}% ({total_gb:.2f} GB / {target_gb} GB)")
        print(f"Remaining: {target_gb - total_gb:.2f} GB")
    else:
        print(f"✓ Target achieved: {total_gb:.2f} GB")
    
    print("="*70)

if __name__ == '__main__':
    main()
