#!/usr/bin/env python3
"""
Create compressed package of client/db for Google Drive upload
Handles large files by creating zip archive
"""

import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'
DRIVE_UPLOAD_DIR = BASE_DIR / 'client' / 'db_drive_ready'
ZIP_OUTPUT = BASE_DIR / 'client' / 'db_drive_ready.zip'

# Google Drive limits
DRIVE_MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB per file
DRIVE_MAX_TOTAL_SIZE = 15 * 1024 * 1024 * 1024  # 15GB free limit

def get_directory_size(directory: Path):
    """Get total size of directory."""
    total = 0
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            total += file_path.stat().st_size
    return total

def create_zip_package():
    """Create zip package of drive-ready directory."""
    if not DRIVE_UPLOAD_DIR.exists():
        print(f"❌ Drive-ready directory not found: {DRIVE_UPLOAD_DIR}")
        print("Run prepare_client_db_for_drive.py first")
        return False
    
    dir_size = get_directory_size(DRIVE_UPLOAD_DIR)
    dir_size_gb = dir_size / (1024**3)
    
    print("="*80)
    print("CREATING ZIP PACKAGE FOR GOOGLE DRIVE")
    print("="*80)
    print(f"Source: {DRIVE_UPLOAD_DIR}")
    print(f"Output: {ZIP_OUTPUT}")
    print(f"Directory size: {dir_size_gb:.2f} GB")
    print()
    
    if dir_size > DRIVE_MAX_FILE_SIZE:
        print(f"⚠️  Directory size ({dir_size_gb:.2f} GB) exceeds Drive file limit (5 GB)")
        print("Creating split archives...")
        return create_split_archives()
    
    print("Creating zip archive...")
    try:
        with zipfile.ZipFile(ZIP_OUTPUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            file_count = 0
            for file_path in DRIVE_UPLOAD_DIR.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(DRIVE_UPLOAD_DIR)
                    zipf.write(file_path, arcname)
                    file_count += 1
                    if file_count % 10 == 0:
                        print(f"  Processed {file_count} files...")
        
        zip_size = ZIP_OUTPUT.stat().st_size
        zip_size_gb = zip_size / (1024**3)
        
        print(f"\n✅ Created zip archive: {ZIP_OUTPUT}")
        print(f"   Size: {zip_size_gb:.2f} GB")
        print(f"   Files: {file_count}")
        print(f"   Compression: {((1 - zip_size/dir_size) * 100):.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ Error creating zip: {e}")
        return False

def create_split_archives():
    """Create multiple zip files if directory is too large."""
    # This is a simplified version - for very large directories,
    # you might want to split by database or use tar with compression
    print("⚠️  Split archives not implemented yet")
    print("Consider:")
    print("1. Uploading databases individually")
    print("2. Using Google Drive Desktop app (handles large uploads)")
    print("3. Using rclone with chunked upload")
    return False

def create_upload_instructions():
    """Create detailed upload instructions."""
    instructions_path = DRIVE_UPLOAD_DIR / 'UPLOAD_INSTRUCTIONS_DETAILED.md'
    
    dir_size = get_directory_size(DRIVE_UPLOAD_DIR)
    dir_size_gb = dir_size / (1024**3)
    
    content = f'''# Detailed Upload Instructions for Google Drive

**Package Size:** {dir_size_gb:.2f} GB
**Total Files:** {len(list(DRIVE_UPLOAD_DIR.rglob('*')))}
**Prepared:** {datetime.now().isoformat()}

## Upload Methods

### Method 1: Google Drive Desktop App (Recommended for Large Files)

1. **Install Google Drive Desktop:**
   - Download: https://www.google.com/drive/download/
   - Install and sign in

2. **Copy to Sync Folder:**
   ```bash
   cp -r {DRIVE_UPLOAD_DIR} ~/Google\ Drive/
   ```

3. **Wait for Sync:**
   - Files will sync automatically
   - Check sync status in Google Drive Desktop app

**Advantages:**
- ✅ Handles large files automatically
- ✅ Resumes interrupted uploads
- ✅ No file size limits
- ✅ Automatic sync

### Method 2: Google Drive Web Interface (For Smaller Packages)

1. **Go to Google Drive:**
   - https://drive.google.com

2. **Create Folder:**
   - Click "New" → "Folder"
   - Name it "client-db-deliverables"

3. **Upload:**
   - Click "New" → "Folder upload"
   - Select `{DRIVE_UPLOAD_DIR.name}` directory
   - Wait for upload (may take time for large directories)

**Limitations:**
- ⚠️  Single file limit: 5 GB
- ⚠️  Total storage limit: 15 GB (free)
- ⚠️  May timeout for very large uploads

### Method 3: Compressed Zip Upload

1. **Create Zip (if not already created):**
   ```bash
   cd {BASE_DIR / 'client'}
   zip -r db_drive_ready.zip db_drive_ready/
   ```

2. **Upload Zip:**
   - Go to Google Drive web interface
   - Upload `db_drive_ready.zip`
   - Extract in Drive (right-click → "Open with" → "Google Drive")

**Advantages:**
- ✅ Single file upload
- ✅ Faster upload (compressed)
- ✅ Preserves folder structure

### Method 4: rclone (Command Line)

1. **Install rclone:**
   ```bash
   brew install rclone
   rclone config  # Configure Google Drive
   ```

2. **Upload:**
   ```bash
   rclone copy {DRIVE_UPLOAD_DIR} gdrive:/client-db-deliverables \\
     --progress \\
     --transfers 4 \\
     --checkers 8
   ```

**Advantages:**
- ✅ Handles large files
- ✅ Resumable uploads
- ✅ Progress tracking
- ✅ Command-line control

### Method 5: Google Apps Script

Use the script: `scripts/google_apps_script_update_drive.gs`

**Note:** Best for individual files, not entire directory.

## File Size Considerations

**Current Package:** {dir_size_gb:.2f} GB

**Google Drive Limits:**
- Free storage: 15 GB total
- Single file: 5 GB max
- Upload timeout: ~2 hours for large files

**Recommendations:**
- ✅ Use Google Drive Desktop app for best results
- ✅ Or compress to zip if under 5 GB
- ✅ Or upload databases individually if needed

## Verification After Upload

1. ✅ Check file count matches
2. ✅ Verify folder structure preserved
3. ✅ Test opening notebooks in Google Colab
4. ✅ Check file sizes match manifest

## Troubleshooting

### Upload Fails

**Problem:** Upload times out or fails

**Solutions:**
- Use Google Drive Desktop app
- Upload in smaller batches
- Use rclone with resume capability
- Compress files first

### File Size Too Large

**Problem:** Single file exceeds 5 GB

**Solutions:**
- Use Google Drive Desktop app (no single-file limit)
- Split into multiple archives
- Upload databases individually

### Storage Limit

**Problem:** Exceeds 15 GB free limit

**Solutions:**
- Upgrade Google Drive storage
- Remove old files from Drive
- Upload only essential files
- Use alternative storage (Dropbox, OneDrive, etc.)

## Next Steps

1. Choose upload method based on package size
2. Upload files to Google Drive
3. Verify upload completed successfully
4. Share folder with team/client if needed

---

**Prepared:** {datetime.now().isoformat()}
**Package Location:** {DRIVE_UPLOAD_DIR}
'''
    
    instructions_path.write_text(content, encoding='utf-8')
    print(f"✅ Created detailed instructions: {instructions_path.relative_to(BASE_DIR)}")

def main():
    """Create upload package."""
    if not DRIVE_UPLOAD_DIR.exists():
        print("Drive-ready directory not found. Running preparation script...")
        import subprocess
        result = subprocess.run([
            'python3', 
            str(BASE_DIR / 'scripts' / 'prepare_client_db_for_drive.py')
        ])
        if result.returncode != 0:
            print("❌ Preparation failed")
            return False
    
    # Create zip package
    create_zip_package()
    
    # Create detailed instructions
    create_upload_instructions()
    
    print(f"\n{'='*80}")
    print("PACKAGE READY FOR UPLOAD")
    print(f"{'='*80}")
    print(f"\n✅ Directory: {DRIVE_UPLOAD_DIR}")
    if ZIP_OUTPUT.exists():
        zip_size = ZIP_OUTPUT.stat().st_size / (1024**3)
        print(f"✅ Zip archive: {ZIP_OUTPUT} ({zip_size:.2f} GB)")
    print(f"\n📋 See: {DRIVE_UPLOAD_DIR}/UPLOAD_INSTRUCTIONS_DETAILED.md")
    
    return True

if __name__ == '__main__':
    main()
