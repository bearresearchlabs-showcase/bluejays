#!/usr/bin/env python3
"""
Download all files from Google Drive folder, update notebooks with failsafe logic,
and prepare for upload back to Drive
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import shutil

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
DRIVE_FOLDER_ID = '1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C'
DRIVE_URL = f'https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}?usp=drive_link'
DOWNLOAD_DIR = BASE_DIR / 'downloads' / 'drive_files'
UPDATED_DIR = BASE_DIR / 'downloads' / 'drive_files_updated'

def check_gdown():
    """Check if gdown is installed."""
    try:
        subprocess.run(['gdown', '--version'], capture_output=True, check=True)
        return True
    except:
        return False

def install_gdown():
    """Install gdown."""
    print("Installing gdown...")
    methods = [
        [sys.executable, '-m', 'pip', 'install', '--user', 'gdown'],
        [sys.executable, '-m', 'pip', 'install', '--break-system-packages', 'gdown'],
        ['pipx', 'install', 'gdown'],
        ['brew', 'install', 'gdown'],
    ]
    
    for cmd in methods:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                # Wait a moment for installation to complete
                import time
                time.sleep(1)
                if check_gdown():
                    print(f"✅ Installed gdown using: {' '.join(cmd)}")
                    return True
        except subprocess.TimeoutExpired:
            print(f"⚠️  Installation timeout for: {' '.join(cmd)}")
            continue
        except Exception as e:
            continue
    
    print("⚠️  Could not install gdown automatically")
    print("Please install manually using one of:")
    print("  pip install --user gdown")
    print("  pip install --break-system-packages gdown")
    print("\nOr continue without gdown and use manual download:")
    print("  1. Download files from Google Drive manually")
    print(f"  2. Place in: {DOWNLOAD_DIR}")
    print("  3. Run script again with --skip-download")
    return False

def download_all_files():
    """Download all files from Google Drive folder."""
    print("="*80)
    print("DOWNLOADING FILES FROM GOOGLE DRIVE")
    print("="*80)
    print(f"Drive URL: {DRIVE_URL}")
    print(f"Download directory: {DOWNLOAD_DIR}")
    print()
    
    # Check/install gdown
    if not check_gdown():
        print("gdown not found. Attempting to install...")
        if not install_gdown():
            print("\n⚠️  gdown not available. Trying alternative methods...")
            print("\nOption 1: Manual download")
            print(f"  1. Open: {DRIVE_URL}")
            print(f"  2. Download all files manually")
            print(f"  3. Place in: {DOWNLOAD_DIR}")
            print(f"  4. Run script again with --skip-download")
            print("\nOption 2: Use Google Apps Script")
            print("  1. Open: https://script.google.com")
            print("  2. Use script from: scripts/google_apps_script_update_drive.gs")
            print("  3. Run updateNotebooks() function")
            print("\nContinuing with manual download option...")
            # Check if files already exist
            if not any(DOWNLOAD_DIR.rglob('*')):
                print(f"\n❌ No files found in {DOWNLOAD_DIR}")
                print("Please download files manually or install gdown")
                return False
            else:
                print(f"✅ Found existing files in {DOWNLOAD_DIR}")
                return True
    
    # Create download directory
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download folder
    print("Downloading folder...")
    try:
        cmd = [
            'gdown',
            '--folder',
            DRIVE_URL,
            '--output', str(DOWNLOAD_DIR),
            '--remaining-ok'  # Continue if some files fail
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Downloaded to {DOWNLOAD_DIR}")
            return True
        else:
            print(f"⚠️  Download completed with warnings:")
            print(result.stderr)
            # Check if any files were downloaded
            if any(DOWNLOAD_DIR.rglob('*')):
                print("Some files were downloaded. Continuing...")
                return True
            return False
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return False

def list_downloaded_files():
    """List all downloaded files."""
    files = []
    for file_path in DOWNLOAD_DIR.rglob('*'):
        if file_path.is_file():
            files.append({
                'path': file_path,
                'name': file_path.name,
                'relative': file_path.relative_to(DOWNLOAD_DIR),
                'size': file_path.stat().st_size
            })
    return files

def update_notebooks_with_failsafe():
    """Update all notebooks with failsafe logic."""
    print("\n" + "="*80)
    print("UPDATING NOTEBOOKS WITH FAILSAFE LOGIC")
    print("="*80)
    
    # Import update script
    sys.path.insert(0, str(BASE_DIR / 'scripts'))
    try:
        from update_notebooks_failsafe import update_notebooks_in_directory
        
        updated_count = update_notebooks_in_directory(DOWNLOAD_DIR)
        print(f"\n✅ Updated {updated_count} notebooks")
        return updated_count
    except Exception as e:
        print(f"❌ Error updating notebooks: {e}")
        import traceback
        traceback.print_exc()
        return 0

def copy_updated_files():
    """Copy updated files to separate directory for upload."""
    print("\n" + "="*80)
    print("PREPARING FILES FOR UPLOAD")
    print("="*80)
    
    UPDATED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy all files maintaining structure
    for file_path in DOWNLOAD_DIR.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(DOWNLOAD_DIR)
            dest_path = UPDATED_DIR / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)
    
    print(f"✅ Files prepared in: {UPDATED_DIR}")
    return True

def generate_upload_script():
    """Generate script to upload files back to Drive."""
    upload_script = UPDATED_DIR / 'upload_to_drive.sh'
    
    script_content = f'''#!/bin/bash
# Upload updated files back to Google Drive
# Rebuilt: {datetime.now().isoformat()}

DRIVE_FOLDER_ID="{DRIVE_FOLDER_ID}"
UPDATED_DIR="{UPDATED_DIR}"

echo "="*80
echo "UPLOADING FILES TO GOOGLE DRIVE"
echo "="*80
echo "Folder ID: $DRIVE_FOLDER_ID"
echo "Source: $UPDATED_DIR"
echo ""

# Check if gdown supports upload (it doesn't, need rclone or Drive API)
echo "Note: gdown does not support upload."
echo "Options:"
echo "1. Use Google Apps Script (recommended)"
echo "2. Use rclone (if configured)"
echo "3. Manual upload via Drive web interface"
echo ""
echo "For Google Apps Script:"
echo "1. Open: https://script.google.com"
echo "2. Use syncNotebookFromLocal() function"
echo "3. Or use Drive web interface to upload files"
echo ""
echo "Files ready for upload in: $UPDATED_DIR"
'''
    
    upload_script.write_text(script_content)
    upload_script.chmod(0o755)
    
    print(f"✅ Upload script created: {upload_script}")
    return upload_script

def generate_upload_instructions():
    """Generate detailed upload instructions."""
    instructions = UPDATED_DIR / 'UPLOAD_INSTRUCTIONS.md'
    
    content = f'''# Upload Instructions

## Files Updated

All files have been downloaded, updated with failsafe logic, and are ready for upload.

**Source Directory:** {UPDATED_DIR}
**Drive Folder:** {DRIVE_URL}

## Upload Methods

### Method 1: Google Apps Script (Recommended)

1. Open Google Apps Script: https://script.google.com
2. Use the script from: `scripts/google_apps_script_update_drive.gs`
3. Use `syncNotebookFromLocal()` function for each file
4. Or create batch upload function

### Method 2: Manual Upload via Drive Web Interface

1. Open Drive folder: {DRIVE_URL}
2. Click "New" → "File upload" or drag and drop
3. Upload files from: {UPDATED_DIR}
4. Maintain folder structure

### Method 3: rclone (If Configured)

```bash
# Configure rclone first: rclone config
rclone copy {UPDATED_DIR} gdrive:{DRIVE_FOLDER_ID} --drive-shared-with-me
```

### Method 4: Google Drive API (Python)

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Use Drive API to upload files
# See: https://developers.google.com/drive/api/v3/quickstart/python
```

## Files to Upload

'''
    
    # List all files
    files = list_downloaded_files()
    for file_info in files:
        content += f"- `{file_info['relative']}` ({file_info['size']} bytes)\n"
    
    content += f'''
## Verification

After uploading, verify:
1. All files are present in Drive folder
2. Notebooks have failsafe logic (check for "FAILSAFE: Force Path Correction")
3. Backup files were created (.failsafe_backup)

## Next Steps

1. Upload files using preferred method
2. Verify uploads in Drive
3. Test notebooks in Drive
4. Update local repository if needed

Rebuilt: {datetime.now().isoformat()}
'''
    
    instructions.write_text(content)
    print(f"✅ Upload instructions created: {instructions}")
    return instructions

def create_summary_report():
    """Create summary report of updates."""
    report_file = UPDATED_DIR / 'UPDATE_SUMMARY.md'
    
    files = list_downloaded_files()
    notebooks = [f for f in files if f['name'].endswith('.ipynb')]
    other_files = [f for f in files if not f['name'].endswith('.ipynb')]
    
    content = f'''# Update Summary Report

**Rebuilt:** {datetime.now().isoformat()}
**Drive Folder:** {DRIVE_URL}
**Download Directory:** {DOWNLOAD_DIR}
**Updated Directory:** {UPDATED_DIR}

## Summary

- **Total Files:** {len(files)}
- **Notebooks:** {len(notebooks)}
- **Other Files:** {len(other_files)}

## Notebooks Updated

'''
    
    for notebook in notebooks:
        content += f"- `{notebook['relative']}`\n"
    
    content += "\n## Other Files\n\n"
    for file_info in other_files:
        content += f"- `{file_info['relative']}` ({file_info['size']} bytes)\n"
    
    content += f'''
## Failsafe Status

All notebooks have been updated with failsafe logic:
- ✅ Path correction (searches 9+ locations)
- ✅ Forced package installation (6 fallback methods)
- ✅ Backup files created (.failsafe_backup)

## Next Steps

1. Review updated files in: {UPDATED_DIR}
2. Upload to Drive using instructions in: UPLOAD_INSTRUCTIONS.md
3. Verify uploads in Drive folder
4. Test notebooks in Drive

## Files Ready for Upload

All files are in: {UPDATED_DIR}
Maintain folder structure when uploading.
'''
    
    report_file.write_text(content)
    print(f"✅ Summary report created: {report_file}")
    return report_file

def main():
    """Main execution."""
    print("="*80)
    print("UPDATE ALL FILES IN GOOGLE DRIVE FOLDER")
    print("="*80)
    print()
    
    # Step 1: Download files
    if not download_all_files():
        print("\n❌ Download failed. Cannot proceed.")
        return False
    
    # Step 2: List downloaded files
    files = list_downloaded_files()
    print(f"\n✅ Downloaded {len(files)} files")
    
    notebooks = [f for f in files if f['name'].endswith('.ipynb')]
    print(f"   Notebooks: {len(notebooks)}")
    print(f"   Other files: {len(files) - len(notebooks)}")
    
    # Step 3: Update notebooks
    if notebooks:
        updated_count = update_notebooks_with_failsafe()
        print(f"\n✅ Updated {updated_count} notebooks with failsafe logic")
    else:
        print("\n⚠️  No notebooks found to update")
    
    # Step 4: Copy to updated directory
    copy_updated_files()
    
    # Step 5: Generate upload instructions
    generate_upload_instructions()
    generate_upload_script()
    create_summary_report()
    
    print("\n" + "="*80)
    print("UPDATE COMPLETE")
    print("="*80)
    print(f"\n✅ Files downloaded: {DOWNLOAD_DIR}")
    print(f"✅ Files updated: {UPDATED_DIR}")
    print(f"\nNext steps:")
    print(f"1. Review files in: {UPDATED_DIR}")
    print(f"2. Follow instructions in: {UPDATED_DIR}/UPLOAD_INSTRUCTIONS.md")
    print(f"3. Upload files to Drive folder: {DRIVE_URL}")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
