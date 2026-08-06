#!/usr/bin/env python3
"""
Standardize deliverable directory structure across all databases.

This script ensures all db-{N}/deliverable/ directories follow the same structure
as the golden solution (db-6), making them suitable for programmatic traversal
and website generation.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Database name mappings for web-deployable folders
DB_WEB_FOLDER_NAMES = {
    6: "db6-weather-consulting-insurance",
    7: "db7-maritime-shipping-intelligence",
    8: "db8-job-market-intelligence",
    9: "db9-shipping-intelligence",
    10: "db10-marketing-intelligence",
    11: "db11-parking-intelligence",
    12: "db12-credit-card-and-rewards-optimization-system",
    13: "db13-ai-benchmark-marketing-database",
    14: "db14-cloud-instance-cost-database",
    15: "db15-electricity-cost-and-solar-rebate-database",
}


def get_required_files():
    """Get list of required files for web-deployable folder."""
    return [
        'db-{N}_documentation.html',
        'db-{N}_deliverable.json',
        'db-{N}.md',
        'vercel.json',
        '.gitignore',
        'data/',
    ]


def find_best_web_folder(deliverable_dir, db_num):
    """Find the best web-deployable folder (most complete)."""
    expected_name = DB_WEB_FOLDER_NAMES.get(db_num)
    
    # Look for folders matching the expected name
    web_folders = []
    for item in deliverable_dir.iterdir():
        if item.is_dir() and item.name.startswith(f'db{db_num}-'):
            web_folders.append(item)
    
    if not web_folders:
        return None
    
    # Prefer the expected name
    for folder in web_folders:
        if folder.name == expected_name:
            return folder
    
    # Otherwise, find the most complete folder
    best_folder = None
    best_score = 0
    
    for folder in web_folders:
        score = 0
        required_files = get_required_files()
        for req_file in required_files:
            req_file = req_file.replace('{N}', str(db_num))
            if (folder / req_file).exists():
                score += 1
        if score > best_score:
            best_score = score
            best_folder = folder
    
    return best_folder


def standardize_deliverable(db_num, root_dir=None):
    """Standardize deliverable directory structure for a database."""
    if root_dir is None:
        root_dir = Path(__file__).parent.parent
    
    db_dir = root_dir / f"db-{db_num}"
    deliverable_dir = db_dir / "deliverable"
    
    if not deliverable_dir.exists():
        logger.warning(f"Deliverable directory not found: {deliverable_dir}")
        return False
    
    logger.info(f"Standardizing db-{db_num} deliverable structure...")
    
    changes_made = []
    
    # Step 1: Ensure root-level files exist
    required_root_files = [
        f'db-{db_num}.md',
        'deliverable.openapi.yaml',
    ]
    
    for req_file in required_root_files:
        req_path = deliverable_dir / req_file
        if not req_path.exists():
            # Try to find it in source locations
            source_locations = [
                db_dir / req_file.replace('deliverable.', ''),
                db_dir / 'deliverable' / req_file,
            ]
            for source in source_locations:
                if source.exists():
                    shutil.copy2(source, req_path)
                    changes_made.append(f"Copied {req_file} to deliverable/")
                    break
    
    # Step 2: Ensure data/ folder exists at root level
    root_data_dir = deliverable_dir / "data"
    source_data_dir = db_dir / "data"
    
    if not root_data_dir.exists() and source_data_dir.exists():
        root_data_dir.mkdir(exist_ok=True)
        changes_made.append("Created data/ folder in deliverable/")
    
    # Copy SQL files to root data/ folder
    if root_data_dir.exists() and source_data_dir.exists():
        sql_files = list(source_data_dir.glob('*.sql'))
        for sql_file in sql_files:
            dest_file = root_data_dir / sql_file.name
            if not dest_file.exists():
                shutil.copy2(sql_file, dest_file)
                changes_made.append(f"Copied {sql_file.name} to deliverable/data/")
        
        # Also copy PostgreSQL dump files
        dump_files = list(source_data_dir.glob('*_postgresql.dump'))
        for dump_file in dump_files:
            dest_file = root_data_dir / dump_file.name
            if not dest_file.exists():
                shutil.copy2(dump_file, dest_file)
                changes_made.append(f"Copied {dump_file.name} to deliverable/data/")
    
    # Step 3: Ensure queries/ folder exists if queries.md exists
    queries_source = db_dir / "queries" / "queries.md"
    queries_dir = deliverable_dir / "queries"
    
    if queries_source.exists():
        if not queries_dir.exists():
            queries_dir.mkdir(exist_ok=True)
            changes_made.append("Created queries/ folder in deliverable/")
        
        # Copy queries files
        for queries_file in ['queries.md', 'queries.json']:
            source_file = db_dir / "queries" / queries_file
            dest_file = queries_dir / queries_file
            if source_file.exists() and not dest_file.exists():
                shutil.copy2(source_file, dest_file)
                changes_made.append(f"Copied {queries_file} to deliverable/queries/")
    
    # Step 4: Handle web-deployable folder
    expected_web_folder_name = DB_WEB_FOLDER_NAMES.get(db_num)
    expected_web_folder = deliverable_dir / expected_web_folder_name
    
    # Find all web-deployable folders
    web_folders = []
    for item in deliverable_dir.iterdir():
        if item.is_dir() and item.name.startswith(f'db{db_num}-'):
            web_folders.append(item)
    
    if not web_folders:
        logger.warning(f"No web-deployable folder found for db-{db_num}")
        return len(changes_made) > 0
    
    # Find the best folder (most complete)
    best_folder = find_best_web_folder(deliverable_dir, db_num)
    
    if not best_folder:
        logger.warning(f"Could not determine best web folder for db-{db_num}")
        return len(changes_made) > 0
    
    # If best folder is not the expected name, rename it
    if best_folder.name != expected_web_folder_name:
        logger.info(f"  Renaming {best_folder.name} to {expected_web_folder_name}")
        new_path = deliverable_dir / expected_web_folder_name
        if new_path.exists():
            # Remove old folder if it exists
            shutil.rmtree(new_path)
        best_folder.rename(new_path)
        best_folder = new_path
        changes_made.append(f"Renamed web folder to {expected_web_folder_name}")
        # Update web_folders list to reflect rename
        web_folders = [f for f in web_folders if f.name != best_folder.name]
        web_folders.append(best_folder)
    
    # Remove other web-deployable folders (duplicates)
    for folder in web_folders:
        if folder.name != expected_web_folder_name:
            if folder.exists():
                logger.info(f"  Removing duplicate web folder: {folder.name}")
                shutil.rmtree(folder)
                changes_made.append(f"Removed duplicate folder: {folder.name}")
    
    # Step 5: Ensure web-deployable folder has all required files
    web_data_dir = best_folder / "data"
    
    # Ensure data/ folder exists in web folder
    if not web_data_dir.exists():
        web_data_dir.mkdir(exist_ok=True)
        changes_made.append(f"Created data/ folder in {best_folder.name}/")
    
    # Copy SQL files to web data/ folder
    if source_data_dir.exists():
        sql_files = list(source_data_dir.glob('*.sql'))
        for sql_file in sql_files:
            dest_file = web_data_dir / sql_file.name
            if not dest_file.exists():
                shutil.copy2(sql_file, dest_file)
                changes_made.append(f"Copied {sql_file.name} to {best_folder.name}/data/")
    
    # Ensure required files exist in web folder
    required_web_files = {
        f'db-{db_num}_documentation.html': deliverable_dir / f'db-{db_num}.md',
        f'db-{db_num}_deliverable.json': None,  # Will be generated if missing
        f'db-{db_num}.md': deliverable_dir / f'db-{db_num}.md',
        'vercel.json': None,  # Will be created if missing
        '.gitignore': None,  # Will be created if missing
    }
    
    for web_file, source_file in required_web_files.items():
        dest_file = best_folder / web_file
        if not dest_file.exists():
            if source_file and source_file.exists():
                shutil.copy2(source_file, dest_file)
                changes_made.append(f"Copied {web_file} to {best_folder.name}/")
            elif web_file == 'vercel.json':
                # Create vercel.json
                vercel_config = {
                    "rewrites": [
                        {
                            "source": "/",
                            "destination": f"/db-{db_num}_documentation.html"
                        },
                        {
                            "source": f"/db-{db_num}_deliverable.json",
                            "destination": f"/db-{db_num}_deliverable.json"
                        }
                    ],
                    "headers": [
                        {
                            "source": "/(.*\\.html)",
                            "headers": [
                                {
                                    "key": "Content-Type",
                                    "value": "text/html"
                                }
                            ]
                        },
                        {
                            "source": "/(.*\\.json)",
                            "headers": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                }
                            ]
                        }
                    ]
                }
                with open(dest_file, 'w') as f:
                    json.dump(vercel_config, f, indent=2)
                changes_made.append(f"Created {web_file} in {best_folder.name}/")
            elif web_file == '.gitignore':
                # Create .gitignore
                gitignore_content = """# macOS
.DS_Store
.AppleDouble
.LSOverride

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Temporary files
*.tmp
*.log
*.bak
"""
                with open(dest_file, 'w') as f:
                    f.write(gitignore_content)
                changes_made.append(f"Created {web_file} in {best_folder.name}/")
    
    if changes_made:
        logger.info(f"  Changes made:")
        for change in changes_made:
            logger.info(f"    - {change}")
    else:
        logger.info(f"  No changes needed")
    
    return True


def main():
    """Main function to standardize all deliverable directories."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Standardize deliverable directory structure for databases"
    )
    parser.add_argument(
        "db_numbers",
        nargs="*",
        type=int,
        help="Database numbers to standardize (e.g., 6 7 8). If not specified, standardizes db-6 through db-15."
    )
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    
    # Determine which databases to standardize
    if args.db_numbers:
        db_numbers = args.db_numbers
    else:
        # Default: standardize db-6 through db-15
        db_numbers = list(range(6, 16))
    
    logger.info(f"Standardizing deliverable structures for databases: {db_numbers}\n")
    
    success_count = 0
    for db_num in db_numbers:
        if standardize_deliverable(db_num, root_dir):
            success_count += 1
        logger.info("")
    
    logger.info(f"Completed: {success_count}/{len(db_numbers)} databases standardized")
    
    return 0 if success_count == len(db_numbers) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
