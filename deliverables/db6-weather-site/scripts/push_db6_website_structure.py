#!/usr/bin/env python3
"""
Push db-6 website structure to db-7 through db-15.
Ensures all databases have the same website folder structure and template files.
"""

import os
import shutil
import json
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Source database (db-6)
SOURCE_DB = BASE_DIR / "db-6"
SOURCE_WEBSITE = SOURCE_DB / "deliverable" / "db6-weather-consulting-insurance"

# Database naming patterns (from existing folders)
DB_NAMES = {
    7: "db7-maritime-shipping-intelligence",
    8: "db8-job-market-intelligence",
    9: "db9-shipping-intelligence",
    10: "db10-marketing-intelligence",
    11: "db11-parking-intelligence",
    12: "db12-database",  # Placeholder - will need actual names
    13: "db13-database",
    14: "db14-database",
    15: "db15-database",
}

def get_db_website_folder(db_num):
    """Get the website folder name for a database."""
    deliverable_dir = BASE_DIR / f"db-{db_num}" / "deliverable"
    
    # Check if website folder already exists
    for item in deliverable_dir.iterdir():
        if item.is_dir() and item.name.startswith(f"db{db_num}-"):
            return item.name
    
    # Return default name
    return DB_NAMES.get(db_num, f"db{db_num}-database")

def copy_template_files(source_dir, target_dir, db_num):
    """Copy template files from source to target, updating DB numbers."""
    # Copy .gitignore
    if (source_dir / ".gitignore").exists():
        shutil.copy2(source_dir / ".gitignore", target_dir / ".gitignore")
        print(f"  ✓ Copied .gitignore")
    
    # Copy afterquery-logo.png if it exists
    if (source_dir / "afterquery-logo.png").exists():
        shutil.copy2(source_dir / "afterquery-logo.png", target_dir / "afterquery-logo.png")
        print(f"  ✓ Copied afterquery-logo.png")
    
    # Copy and update vercel.json
    if (source_dir / "vercel.json").exists():
        with open(source_dir / "vercel.json", "r") as f:
            vercel_config = json.load(f)
        
        # Update database number in rewrites
        for rewrite in vercel_config.get("rewrites", []):
            if "destination" in rewrite:
                rewrite["destination"] = rewrite["destination"].replace("db-6", f"db-{db_num}")
            if "source" in rewrite:
                rewrite["source"] = rewrite["source"].replace("db-6", f"db-{db_num}")
        
        with open(target_dir / "vercel.json", "w") as f:
            json.dump(vercel_config, f, indent=2)
        print(f"  ✓ Updated vercel.json for db-{db_num}")

def ensure_data_folder(db_num, website_dir):
    """Ensure data folder exists in website directory."""
    source_data = BASE_DIR / f"db-{db_num}" / "deliverable" / "data"
    target_data = website_dir / "data"
    
    if source_data.exists() and source_data.is_dir():
        if target_data.exists():
            # Remove existing and copy fresh
            shutil.rmtree(target_data)
        shutil.copytree(source_data, target_data)
        print(f"  ✓ Copied data folder")
    elif not target_data.exists():
        # Create empty data folder
        target_data.mkdir(parents=True, exist_ok=True)
        print(f"  ⚠ Created empty data folder (no source data found)")

def check_required_files(website_dir, db_num):
    """Check if all required files exist."""
    required_files = [
        f"db-{db_num}_documentation.html",
        f"db-{db_num}_deliverable.json",
        f"db-{db_num}.md",
        "vercel.json",
        ".gitignore",
    ]
    
    missing = []
    for file in required_files:
        if not (website_dir / file).exists():
            missing.append(file)
    
    return missing

def main():
    """Main function to push db-6 website structure to db-7 through db-15."""
    print("Pushing db-6 website structure to db-7 through db-15...")
    print(f"Source: {SOURCE_WEBSITE}")
    print()
    
    if not SOURCE_WEBSITE.exists():
        print(f"ERROR: Source website folder not found: {SOURCE_WEBSITE}")
        return 1
    
    for db_num in range(7, 16):
        print(f"Processing db-{db_num}...")
        
        db_dir = BASE_DIR / f"db-{db_num}"
        deliverable_dir = db_dir / "deliverable"
        website_name = get_db_website_folder(db_num)
        website_dir = deliverable_dir / website_name
        
        # Create deliverable directory if it doesn't exist
        deliverable_dir.mkdir(parents=True, exist_ok=True)
        
        # Create website directory if it doesn't exist
        if not website_dir.exists():
            website_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created website folder: {website_name}")
        
        # Copy template files
        copy_template_files(SOURCE_WEBSITE, website_dir, db_num)
        
        # Ensure data folder exists
        ensure_data_folder(db_num, website_dir)
        
        # Check required files
        missing = check_required_files(website_dir, db_num)
        if missing:
            print(f"  ⚠ Missing files: {', '.join(missing)}")
        else:
            print(f"  ✓ All required files present")
        
        print()
    
    print("Done!")
    return 0

if __name__ == "__main__":
    exit(main())
