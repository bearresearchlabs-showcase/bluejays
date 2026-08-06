#!/usr/bin/env python3
"""
Download notebooks from Google Drive and update them with failsafe logic
Supports multiple download methods: gdown, rclone, manual download
"""

import subprocess
import sys
from pathlib import Path
import json

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
DRIVE_FOLDER_ID = '1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C'
DRIVE_URL = f'https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}?usp=drive_link'

def check_gdown():
    """Check if gdown is installed."""
    try:
        subprocess.run(['gdown', '--version'], capture_output=True, check=True)
        return True
    except:
        return False

def check_rclone():
    """Check if rclone is installed."""
    try:
        subprocess.run(['rclone', 'version'], capture_output=True, check=True)
        return True
    except:
        return False

def download_with_gdown(download_dir: Path):
    """Download using gdown."""
    print("Downloading with gdown...")
    try:
        cmd = [
            'gdown',
            '--folder',
            DRIVE_URL,
            '--output', str(download_dir)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Downloaded to {download_dir}")
            return True
        else:
            print(f"❌ gdown failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def download_with_rclone(download_dir: Path):
    """Download using rclone (requires rclone config)."""
    print("Downloading with rclone...")
    try:
        # Note: Requires rclone to be configured with Google Drive
        cmd = [
            'rclone',
            'copy',
            f'gdrive:{DRIVE_FOLDER_ID}',
            str(download_dir),
            '--drive-shared-with-me'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Downloaded to {download_dir}")
            return True
        else:
            print(f"❌ rclone failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def manual_download_instructions():
    """Print manual download instructions."""
    print("\n" + "="*80)
    print("MANUAL DOWNLOAD INSTRUCTIONS")
    print("="*80)
    print(f"\n1. Open Google Drive folder:")
    print(f"   {DRIVE_URL}")
    print("\n2. Download all files to a directory")
    print("\n3. Run update script with --download-dir:")
    print(f"   python3 scripts/download_and_update_from_drive.py --download-dir /path/to/downloaded/files")
    print("\n" + "="*80)

def update_notebooks_from_download(download_dir: Path):
    """Update notebooks from downloaded directory."""
    print(f"\nUpdating notebooks from: {download_dir}")
    
    # Import update script
    sys.path.insert(0, str(BASE_DIR / 'scripts'))
    try:
        from update_notebooks_failsafe import update_notebooks_in_directory
        
        updated = update_notebooks_in_directory(download_dir)
        print(f"✅ Updated {updated} notebooks")
        return updated > 0
    except Exception as e:
        print(f"❌ Error updating notebooks: {e}")
        return False

def main():
    """Download and update notebooks from Google Drive."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download and update notebooks from Google Drive')
    parser.add_argument('--download-dir', type=str, 
                       default=str(BASE_DIR / 'downloads' / 'drive_notebooks'),
                       help='Directory to download notebooks to')
    parser.add_argument('--method', type=str, choices=['gdown', 'rclone', 'manual'],
                       help='Download method (default: auto-detect)')
    parser.add_argument('--skip-download', action='store_true',
                       help='Skip download, only update existing files')
    parser.add_argument('--update-only', action='store_true',
                       help='Only update notebooks, do not download')
    
    args = parser.parse_args()
    
    download_dir = Path(args.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("DOWNLOAD AND UPDATE NOTEBOOKS FROM GOOGLE DRIVE")
    print("="*80)
    print(f"Drive URL: {DRIVE_URL}")
    print(f"Download directory: {download_dir}")
    print()
    
    # Download notebooks
    if not args.update_only:
        if args.skip_download:
            print("⏭️  Skipping download (files should already exist)")
        else:
            download_success = False
            
            if args.method == 'gdown':
                if check_gdown():
                    download_success = download_with_gdown(download_dir)
                else:
                    print("❌ gdown not installed. Install with: pip install gdown")
            elif args.method == 'rclone':
                if check_rclone():
                    download_success = download_with_rclone(download_dir)
                else:
                    print("❌ rclone not installed. Install with: brew install rclone")
            else:
                # Auto-detect method
                if check_gdown():
                    download_success = download_with_gdown(download_dir)
                elif check_rclone():
                    download_success = download_with_rclone(download_dir)
                else:
                    print("❌ No download method available")
                    manual_download_instructions()
                    return
            
            if not download_success:
                print("\n⚠️  Download failed. You can:")
                print("1. Manually download files and use --skip-download")
                print("2. Install gdown: pip install gdown")
                print("3. Install rclone: brew install rclone")
                return
    
    # Update notebooks
    print("\n" + "="*80)
    print("UPDATING NOTEBOOKS WITH FAILSAFE LOGIC")
    print("="*80)
    
    if download_dir.exists() and any(download_dir.rglob('*.ipynb')):
        update_success = update_notebooks_from_download(download_dir)
        
        if update_success:
            print("\n✅ Notebooks updated successfully!")
            print(f"\nNext steps:")
            print(f"1. Review updated notebooks in: {download_dir}")
            print(f"2. Test notebooks:")
            print(f"   python3 scripts/run_notebooks.py --root-dir {download_dir}")
        else:
            print("\n⚠️  Update completed with warnings")
    else:
        print(f"❌ No notebooks found in {download_dir}")
        print("Please download notebooks first or specify --download-dir")

if __name__ == '__main__':
    main()
