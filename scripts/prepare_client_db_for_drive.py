#!/usr/bin/env python3
"""
Prepare client/db directory for Google Drive upload
- Removes unnecessary files (.backup, .pyc, __pycache__, .DS_Store)
- Creates upload-ready package
- Generates upload instructions
"""

import shutil
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
CLIENT_DB_DIR = BASE_DIR / 'client' / 'db'
DRIVE_UPLOAD_DIR = BASE_DIR / 'client' / 'db_drive_ready'

# Files/patterns to exclude from Drive upload
EXCLUDE_PATTERNS = [
    '*.backup',
    '*.pyc',
    '__pycache__',
    '.DS_Store',
    '.git',
    '.gitignore',
    '*.log',
    '*.tmp',
    '*.swp',
    '*.swo',
    '*~',
    '.ipynb_checkpoints',
    '*.ipynb.backup',
    '*.failsafe_backup',
    '*.enhanced_backup',
]

def should_exclude(file_path: Path) -> bool:
    """Check if file should be excluded from upload."""
    file_name = file_path.name
    
    # Check patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*.'):
            # Extension match
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern.startswith('*'):
            # Suffix match
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern == file_name:
            # Exact match
            return True
    
    # Check if in excluded directory
    parts = file_path.parts
    if '__pycache__' in parts or '.git' in parts or '.ipynb_checkpoints' in parts:
        return True
    
    return False

def prepare_for_drive():
    """Prepare client/db for Google Drive upload."""
    print("="*80)
    print("PREPARING CLIENT/DB FOR GOOGLE DRIVE UPLOAD")
    print("="*80)
    print(f"Source: {CLIENT_DB_DIR}")
    print(f"Destination: {DRIVE_UPLOAD_DIR}")
    print()
    
    # Create destination directory
    if DRIVE_UPLOAD_DIR.exists():
        print(f"⚠️  Destination exists. Removing: {DRIVE_UPLOAD_DIR}")
        shutil.rmtree(DRIVE_UPLOAD_DIR)
    
    DRIVE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy files, excluding unwanted ones
    copied_files = []
    excluded_files = []
    total_size = 0
    
    print("Copying files...")
    for source_path in CLIENT_DB_DIR.rglob('*'):
        if source_path.is_dir():
            continue
        
        relative_path = source_path.relative_to(CLIENT_DB_DIR)
        
        # Check if should exclude
        if should_exclude(source_path):
            excluded_files.append(str(relative_path))
            continue
        
        # Create destination path
        dest_path = DRIVE_UPLOAD_DIR / relative_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        try:
            shutil.copy2(source_path, dest_path)
            copied_files.append(str(relative_path))
            total_size += source_path.stat().st_size
        except Exception as e:
            print(f"⚠️  Error copying {relative_path}: {e}")
            excluded_files.append(str(relative_path))
    
    print(f"\n✅ Copied {len(copied_files)} files")
    print(f"⚠️  Excluded {len(excluded_files)} files")
    print(f"📦 Total size: {total_size / (1024*1024):.2f} MB")
    
    # Create README for Drive upload
    create_drive_readme(copied_files, excluded_files, total_size)
    
    # Create file manifest
    create_file_manifest(copied_files)
    
    return copied_files, excluded_files

def create_drive_readme(copied_files, excluded_files, total_size):
    """Create README for Google Drive upload."""
    readme_path = DRIVE_UPLOAD_DIR / 'README_DRIVE_UPLOAD.md'
    
    content = f'''# Client/DB Directory - Ready for Google Drive Upload

**Prepared:** {datetime.now().isoformat()}
**Total Files:** {len(copied_files)}
**Total Size:** {total_size / (1024*1024):.2f} MB
**Excluded Files:** {len(excluded_files)}

## Upload Instructions

### Method 1: Google Drive Web Interface

1. Go to [Google Drive](https://drive.google.com)
2. Navigate to your target folder
3. Click "New" → "Folder upload"
4. Select the entire `db_drive_ready` directory
5. Wait for upload to complete

### Method 2: Google Drive Desktop App

1. Install [Google Drive for Desktop](https://www.google.com/drive/download/)
2. Copy `db_drive_ready` folder to Google Drive sync folder
3. Files will sync automatically

### Method 3: rclone (Command Line)

```bash
# Configure rclone first: rclone config
rclone copy {DRIVE_UPLOAD_DIR} gdrive:/path/to/folder --progress
```

### Method 4: Google Apps Script

Use the script in `scripts/google_apps_script_update_drive.gs` to upload programmatically.

## Directory Structure

This directory contains all database deliverables ready for client distribution:

```
db_drive_ready/
├── db-6/
│   └── db6-weather-consulting-insurance/
│       ├── db-6.ipynb ✅
│       ├── db-6_dashboard.py ✅
│       ├── db-6.md ✅
│       ├── db-6_deliverable.json ✅
│       ├── data/ ✅
│       └── vercel.json ✅
├── db-7/ ... (same structure)
└── ...
```

## Files Included

- ✅ All Jupyter notebooks (`.ipynb`)
- ✅ All Streamlit dashboards (`.py`)
- ✅ All documentation (`.md`)
- ✅ All JSON deliverables
- ✅ All SQL schema and data files
- ✅ All configuration files (`vercel.json`, etc.)

## Files Excluded

The following files were excluded from upload:

- ❌ Backup files (`.backup`, `.failsafe_backup`, etc.)
- ❌ Python cache files (`.pyc`, `__pycache__`)
- ❌ System files (`.DS_Store`)
- ❌ Git files (`.git`, `.gitignore`)
- ❌ Temporary files (`.log`, `.tmp`, `.swp`)
- ❌ Jupyter checkpoints (`.ipynb_checkpoints`)

See `EXCLUDED_FILES.txt` for complete list.

## Verification

After upload, verify:

1. ✅ All notebooks are present
2. ✅ All dashboards are present
3. ✅ All data files are present
4. ✅ File sizes match (check `FILE_MANIFEST.json`)
5. ✅ Notebooks open correctly in Google Colab

## Usage

### Open Notebooks in Google Colab

1. Upload to Google Drive
2. Right-click notebook → "Open with" → "Google Colab"
3. Notebooks will automatically detect environment and install packages

### Run Dashboards

1. Upload to Google Drive
2. Use Google Colab or local environment
3. Run: `streamlit run db-6_dashboard.py`

## Notes

- All notebooks have failsafe logic for path correction and package installation
- All notebooks create automatic backups when executed
- Files are ready for immediate use
- Maintain folder structure when uploading

## Support

For issues or questions, refer to:
- `NOTEBOOK_UPDATE_README.md` - Notebook update guide
- `scripts/README.md` - Scripts documentation
- `FAILSAFE_AND_BACKUP_COMPLETE.md` - Failsafe implementation

---

**Prepared:** {datetime.now().isoformat()}
**Version:** 1.0
'''
    
    readme_path.write_text(content, encoding='utf-8')
    print(f"✅ Created README: {readme_path.relative_to(BASE_DIR)}")

def create_file_manifest(copied_files):
    """Create JSON manifest of all files."""
    manifest_path = DRIVE_UPLOAD_DIR / 'FILE_MANIFEST.json'
    
    manifest = {
        'prepared_date': datetime.now().isoformat(),
        'total_files': len(copied_files),
        'files': []
    }
    
    for file_path_str in copied_files:
        full_path = DRIVE_UPLOAD_DIR / file_path_str
        if full_path.exists():
            stat = full_path.stat()
            manifest['files'].append({
                'path': file_path_str,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024*1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Created manifest: {manifest_path.relative_to(BASE_DIR)}")

def create_excluded_list(excluded_files):
    """Create list of excluded files."""
    excluded_path = DRIVE_UPLOAD_DIR / 'EXCLUDED_FILES.txt'
    
    content = f'''# Excluded Files from Google Drive Upload

**Generated:** {datetime.now().isoformat()}
**Total Excluded:** {len(excluded_files)}

## Excluded Files

These files were excluded from the upload package:

'''
    
    for file_path in sorted(excluded_files):
        content += f"- `{file_path}`\n"
    
    content += f'''
## Exclusion Patterns

The following patterns were used to exclude files:

'''
    for pattern in EXCLUDE_PATTERNS:
        content += f"- `{pattern}`\n"
    
    excluded_path.write_text(content, encoding='utf-8')
    print(f"✅ Created excluded list: {excluded_path.relative_to(BASE_DIR)}")

def create_upload_script():
    """Create script to help with upload."""
    script_path = DRIVE_UPLOAD_DIR / 'upload_to_drive.sh'
    
    script_content = f'''#!/bin/bash
# Upload client/db to Google Drive
# Generated: {datetime.now().isoformat()}

UPLOAD_DIR="{DRIVE_UPLOAD_DIR}"
DRIVE_FOLDER_ID="1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C"

echo "="*80
echo "UPLOAD CLIENT/DB TO GOOGLE DRIVE"
echo "="*80
echo "Upload directory: $UPLOAD_DIR"
echo "Drive folder ID: $DRIVE_FOLDER_ID"
echo ""

# Check if rclone is available
if command -v rclone &> /dev/null; then
    echo "Using rclone to upload..."
    rclone copy "$UPLOAD_DIR" gdrive:$DRIVE_FOLDER_ID --progress
elif command -v gdown &> /dev/null; then
    echo "gdown does not support upload. Use one of:"
    echo "1. Google Drive web interface"
    echo "2. Google Drive Desktop app"
    echo "3. Install rclone: brew install rclone"
else
    echo "No upload tool found. Options:"
    echo "1. Use Google Drive web interface (recommended)"
    echo "2. Install Google Drive Desktop app"
    echo "3. Install rclone: brew install rclone"
fi

echo ""
echo "Upload complete!"
'''
    
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    print(f"✅ Created upload script: {script_path.relative_to(BASE_DIR)}")

def main():
    """Main execution."""
    print("Preparing client/db for Google Drive upload...\n")
    
    if not CLIENT_DB_DIR.exists():
        print(f"❌ Source directory not found: {CLIENT_DB_DIR}")
        return False
    
    # Prepare directory
    copied_files, excluded_files = prepare_for_drive()
    
    # Create excluded files list
    create_excluded_list(excluded_files)
    
    # Create upload script
    create_upload_script()
    
    print(f"\n{'='*80}")
    print("PREPARATION COMPLETE")
    print(f"{'='*80}")
    print(f"\n✅ Ready for upload: {DRIVE_UPLOAD_DIR}")
    print(f"📦 Total files: {len(copied_files)}")
    print(f"📋 Excluded files: {len(excluded_files)}")
    print(f"\nNext steps:")
    print(f"1. Review files in: {DRIVE_UPLOAD_DIR}")
    print(f"2. Follow instructions in: {DRIVE_UPLOAD_DIR}/README_DRIVE_UPLOAD.md")
    print(f"3. Upload to Google Drive")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
