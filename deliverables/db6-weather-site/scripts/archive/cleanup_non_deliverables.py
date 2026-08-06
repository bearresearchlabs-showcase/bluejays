#!/usr/bin/env python3
"""
Clean up all files aside from deliverables (db-1 through db-5)
"""

import shutil
from pathlib import Path

class NonDeliverableCleanup:
    def __init__(self, root_dir='.'):
        self.root = Path(root_dir)
        self.deliverables = {f'db-{i}' for i in range(1, 6)}
        self.keep_dirs = {
            'db-1', 'db-2', 'db-3', 'db-4', 'db-5',
            '.cursor', '.git', '__pycache__'
        }
        self.keep_files = {
            'README.md',
            'docker-compose.yml',
            '.gitignore'
        }

    def identify_files_to_remove(self):
        """Identify all files and directories to remove"""
        to_remove = {
            'files': [],
            'dirs': []
        }

        for item in self.root.iterdir():
            # Skip hidden files/dirs and deliverables
            if item.name.startswith('.'):
                continue

            # Keep deliverables
            if item.name in self.deliverables:
                continue

            # Keep essential files
            if item.name in self.keep_files:
                continue

            if item.is_file():
                to_remove['files'].append(item)
            elif item.is_dir():
                # Check if it's a keep directory
                if item.name not in self.keep_dirs:
                    to_remove['dirs'].append(item)

        return to_remove

    def cleanup(self, dry_run=True):
        """Remove non-deliverable files and directories"""
        print("=" * 70)
        print("CLEANING UP NON-DELIVERABLE FILES")
        print("=" * 70)

        to_remove = self.identify_files_to_remove()

        print(f"\nFiles to remove: {len(to_remove['files'])}")
        for f in to_remove['files'][:20]:
            print(f"  - {f.name}")
        if len(to_remove['files']) > 20:
            print(f"  ... and {len(to_remove['files']) - 20} more")

        print(f"\nDirectories to remove: {len(to_remove['dirs'])}")
        for d in to_remove['dirs']:
            print(f"  - {d.name}/")

        if not dry_run:
            print("\nRemoving files...")
            for f in to_remove['files']:
                try:
                    f.unlink()
                    print(f"  ✅ Removed {f.name}")
                except Exception as e:
                    print(f"  ⚠️  Could not remove {f.name}: {e}")

            print("\nRemoving directories...")
            for d in to_remove['dirs']:
                try:
                    shutil.rmtree(d)
                    print(f"  ✅ Removed {d.name}/")
                except Exception as e:
                    print(f"  ⚠️  Could not remove {d.name}/: {e}")
        else:
            print("\n⚠️  DRY RUN - files not actually removed")

        return to_remove

if __name__ == '__main__':
    import sys
    dry_run = '--execute' not in sys.argv

    cleanup = NonDeliverableCleanup()
    to_remove = cleanup.cleanup(dry_run=dry_run)

    if dry_run:
        print("\n" + "=" * 70)
        print("Run with --execute to actually remove files")
        print("=" * 70)
