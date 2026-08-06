#!/usr/bin/env python3
"""
List deliverable directory structure for programmatic traversal.

This script generates a JSON manifest of all deliverable directories,
making it easy to programmatically traverse and process all databases.
"""

import json
from pathlib import Path
from datetime import datetime


def scan_deliverable_structure(db_num, root_dir=None):
    """Scan deliverable directory structure for a database."""
    if root_dir is None:
        root_dir = Path(__file__).parent.parent
    
    db_dir = root_dir / f"db-{db_num}"
    deliverable_dir = db_dir / "deliverable"
    
    if not deliverable_dir.exists():
        return None
    
    structure = {
        'database': f'db-{db_num}',
        'deliverable_path': str(deliverable_dir.relative_to(root_dir)),
        'root_files': [],
        'directories': {},
        'web_deployable_folder': None,
    }
    
    # Scan root level files
    for item in deliverable_dir.iterdir():
        if item.is_file():
            structure['root_files'].append({
                'name': item.name,
                'path': str(item.relative_to(root_dir)),
                'size_bytes': item.stat().st_size,
            })
        elif item.is_dir():
            dir_info = {
                'name': item.name,
                'path': str(item.relative_to(root_dir)),
                'type': 'unknown',
                'files': [],
                'subdirectories': [],
            }
            
            # Determine directory type
            if item.name.startswith(f'db{db_num}-'):
                dir_info['type'] = 'web_deployable'
                structure['web_deployable_folder'] = {
                    'name': item.name,
                    'path': str(item.relative_to(root_dir)),
                }
            elif item.name == 'data':
                dir_info['type'] = 'data'
            elif item.name == 'queries':
                dir_info['type'] = 'queries'
            else:
                dir_info['type'] = 'other'
            
            # Scan directory contents
            for subitem in item.iterdir():
                if subitem.is_file():
                    dir_info['files'].append({
                        'name': subitem.name,
                        'path': str(subitem.relative_to(root_dir)),
                        'size_bytes': subitem.stat().st_size,
                    })
                elif subitem.is_dir():
                    dir_info['subdirectories'].append({
                        'name': subitem.name,
                        'path': str(subitem.relative_to(root_dir)),
                    })
            
            structure['directories'][item.name] = dir_info
    
    return structure


def main():
    """Main function to scan all deliverable structures."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="List deliverable directory structures for programmatic traversal"
    )
    parser.add_argument(
        "db_numbers",
        nargs="*",
        type=int,
        help="Database numbers to scan (e.g., 6 7 8). If not specified, scans db-6 through db-15."
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file (default: deliverable_structure_manifest.json)"
    )
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    
    # Determine which databases to scan
    if args.db_numbers:
        db_numbers = args.db_numbers
    else:
        # Default: scan db-6 through db-15
        db_numbers = list(range(6, 16))
    
    manifest = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_databases': len(db_numbers),
        'databases': [],
    }
    
    for db_num in db_numbers:
        structure = scan_deliverable_structure(db_num, root_dir)
        if structure:
            manifest['databases'].append(structure)
    
    # Output JSON
    output_file = args.output or root_dir / "deliverable_structure_manifest.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✓ Generated deliverable structure manifest: {output_file}")
    print(f"  Total databases: {len(manifest['databases'])}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
