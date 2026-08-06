#!/usr/bin/env python3
"""
Delete all backup files from the repository
"""

from pathlib import Path
from datetime import datetime

BASE_DIR = Path('/Users/machine/Documents/AQ/db')

# Backup file patterns to delete
BACKUP_PATTERNS = [
    '*.backup',
    '*.failsafe_backup',
    '*.enhanced_backup',
    '*.unboundlocal_fix_backup',
    '*.streamlit_backup',
    '*_backup.*',
    '*_backup_*.ipynb',
    '*_backup_*.py',
]

def find_backup_files(directory: Path):
    """Find all backup files."""
    backup_files = []
    
    # Find by extension
    for pattern in BACKUP_PATTERNS:
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                backup_files.append(file_path)
    
    # Also find files with "backup" in name (but be careful)
    for file_path in directory.rglob('*backup*'):
        if file_path.is_file():
            # Only include if it's clearly a backup
            if any(pattern.replace('*', '') in file_path.name for pattern in BACKUP_PATTERNS):
                if file_path not in backup_files:
                    backup_files.append(file_path)
    
    return backup_files

def delete_backups(dry_run=False):
    """Delete all backup files."""
    print("="*80)
    print("DELETING ALL BACKUP FILES")
    print("="*80)
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No files will be deleted")
    
    print(f"Searching in: {BASE_DIR}")
    print()
    
    backup_files = find_backup_files(BASE_DIR)
    
    if not backup_files:
        print("✅ No backup files found")
        return []
    
    print(f"Found {len(backup_files)} backup files:")
    print()
    
    deleted = []
    failed = []
    
    for backup_file in sorted(backup_files):
        relative_path = backup_file.relative_to(BASE_DIR)
        size = backup_file.stat().st_size / 1024  # KB
        
        if dry_run:
            print(f"  [DRY RUN] Would delete: {relative_path} ({size:.1f} KB)")
        else:
            try:
                backup_file.unlink()
                print(f"  ✅ Deleted: {relative_path} ({size:.1f} KB)")
                deleted.append(backup_file)
            except Exception as e:
                print(f"  ❌ Failed: {relative_path} - {e}")
                failed.append(backup_file)
    
    print()
    print("="*80)
    print("DELETION SUMMARY")
    print("="*80)
    
    if dry_run:
        print(f"Would delete: {len(backup_files)} files")
    else:
        print(f"Deleted: {len(deleted)} files")
        if failed:
            print(f"Failed: {len(failed)} files")
        
        # Calculate total size freed
        total_size = sum(f.stat().st_size for f in deleted if f.exists())
        total_size_mb = total_size / (1024 * 1024)
        print(f"Space freed: {total_size_mb:.2f} MB")
    
    return deleted if not dry_run else backup_files

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Delete all backup files')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.confirm:
        print("⚠️  WARNING: This will permanently delete all backup files!")
        response = input("Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    deleted = delete_backups(dry_run=args.dry_run)
    
    if not args.dry_run:
        print(f"\n✅ Deletion complete!")
        print(f"   Deleted: {len(deleted)} backup files")

if __name__ == '__main__':
    main()
