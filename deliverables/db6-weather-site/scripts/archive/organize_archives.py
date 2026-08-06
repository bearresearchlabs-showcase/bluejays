#!/usr/bin/env python3
"""
Organize zip files and extracted database contents into consistent structure
Each database should have:
- data/archive/ - zip files
- data/extracted/ - extracted database contents
"""

import shutil
import zipfile
from pathlib import Path
from datetime import datetime

class ArchiveOrganizer:
    def __init__(self, root_dir='.'):
        self.root = Path(root_dir)

    def find_zip_files(self, db_dir):
        """Find zip files in database directory"""
        zip_files = list(db_dir.glob('*.zip'))
        # Also check root level
        if db_dir.parent == self.root:
            zip_files.extend(list(db_dir.parent.glob(f'db-{db_dir.name[-1]}/*.zip')))
        return zip_files

    def find_extracted_content(self, db_dir):
        """Find extracted database content directories"""
        extracted_dirs = []

        # Check for 'extracted' directory
        if (db_dir / 'extracted').exists():
            extracted_dirs.append(db_dir / 'extracted')

        # Check for directories starting with '_'
        for item in db_dir.iterdir():
            if item.is_dir() and item.name.startswith('_'):
                extracted_dirs.append(item)

        return extracted_dirs

    def organize_database(self, db_num):
        """Organize zip files and extracted content for a database"""
        db_dir = self.root / f'db-{db_num}'
        if not db_dir.exists():
            return False

        print(f"\nOrganizing db-{db_num}...")

        # Create archive and extracted directories
        archive_dir = db_dir / 'data' / 'archive'
        extracted_dir = db_dir / 'data' / 'extracted'
        archive_dir.mkdir(parents=True, exist_ok=True)
        extracted_dir.mkdir(parents=True, exist_ok=True)

        moved_items = []

        # Move zip files to data/archive/
        zip_files = self.find_zip_files(db_dir)
        for zf in zip_files:
            if zf.parent != archive_dir:
                dest = archive_dir / zf.name
                if zf != dest:
                    if dest.exists():
                        print(f"  ⚠️  Archive already exists: {zf.name}")
                    else:
                        shutil.move(str(zf), str(dest))
                        moved_items.append(f"{zf.name} -> data/archive/")

        # Move extracted content to data/extracted/
        extracted_dirs = self.find_extracted_content(db_dir)
        for ext_dir in extracted_dirs:
            if ext_dir.parent != extracted_dir:
                # Get the directory name
                dir_name = ext_dir.name
                dest = extracted_dir / dir_name

                if dest.exists():
                    print(f"  ⚠️  Extracted content already exists: {dir_name}")
                else:
                    shutil.move(str(ext_dir), str(dest))
                    moved_items.append(f"{dir_name} -> data/extracted/")

        # If zip files exist but no extracted content, try to extract
        zip_files_in_archive = list(archive_dir.glob('*.zip'))
        if zip_files_in_archive and not any(extracted_dir.iterdir()):
            print(f"  📦 Extracting zip files...")
            for zf in zip_files_in_archive:
                try:
                    extract_to = extracted_dir / zf.stem
                    extract_to.mkdir(exist_ok=True)
                    with zipfile.ZipFile(zf, 'r') as zip_ref:
                        zip_ref.extractall(extract_to)
                    moved_items.append(f"Extracted {zf.name} -> data/extracted/{zf.stem}/")
                except Exception as e:
                    print(f"  ⚠️  Could not extract {zf.name}: {e}")

        if moved_items:
            print(f"  ✅ Organized {len(moved_items)} items")
            for item in moved_items[:10]:
                print(f"     - {item}")
            if len(moved_items) > 10:
                print(f"     ... and {len(moved_items) - 10} more")
        else:
            print(f"  ✅ Already organized")

        return True

    def verify_organization(self, db_num):
        """Verify that database has zip and extracted content"""
        db_dir = self.root / f'db-{db_num}'
        if not db_dir.exists():
            return False

        archive_dir = db_dir / 'data' / 'archive'
        extracted_dir = db_dir / 'data' / 'extracted'

        zip_files = list(archive_dir.glob('*.zip')) if archive_dir.exists() else []
        extracted_content = list(extracted_dir.iterdir()) if extracted_dir.exists() else []
        extracted_content = [d for d in extracted_content if d.is_dir()]

        return {
            'has_zip': len(zip_files) > 0,
            'zip_count': len(zip_files),
            'has_extracted': len(extracted_content) > 0,
            'extracted_count': len(extracted_content)
        }

    def organize_all(self):
        """Organize all databases"""
        print("=" * 70)
        print("ORGANIZING ARCHIVES AND EXTRACTED CONTENT")
        print("=" * 70)

        for db_num in range(1, 6):
            self.organize_database(db_num)

        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)

        for db_num in range(1, 6):
            status = self.verify_organization(db_num)
            if status:
                print(f"\ndb-{db_num}:")
                print(f"  {'✅' if status['has_zip'] else '❌'} Archive: {status['zip_count']} zip file(s)")
                print(f"  {'✅' if status['has_extracted'] else '❌'} Extracted: {status['extracted_count']} directory/directories")

        print("\n" + "=" * 70)
        print("Organization complete!")
        print("=" * 70)

if __name__ == '__main__':
    organizer = ArchiveOrganizer()
    organizer.organize_all()
