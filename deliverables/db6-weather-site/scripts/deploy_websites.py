#!/usr/bin/env python3
"""
Deploy database websites to Vercel.
This script deploys all complete website folders to Vercel.
"""

import os
import subprocess
import sys
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

def check_vercel_cli():
    """Check if Vercel CLI is installed."""
    try:
        result = subprocess.run(['vercel', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Vercel CLI found: {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("✗ Vercel CLI not found. Please install it with: npm i -g vercel")
    return False

def check_vercel_auth():
    """Check if user is authenticated with Vercel."""
    try:
        result = subprocess.run(['vercel', 'whoami'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            username = result.stdout.strip()
            print(f"✓ Authenticated as: {username}")
            return True
        else:
            print("✗ Not authenticated with Vercel")
            print("  Please run: vercel login")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"✗ Error checking Vercel auth: {e}")
        return False

def find_website_folder(db_num):
    """Find the website folder for a database."""
    deliverable_dir = BASE_DIR / f"db-{db_num}" / "deliverable"
    if not deliverable_dir.exists():
        return None
    
    for item in deliverable_dir.iterdir():
        if item.is_dir() and item.name.startswith(f"db{db_num}-"):
            return item
    
    return None

def check_website_ready(website_dir, db_num):
    """Check if website has all required files."""
    required_files = [
        f"db-{db_num}_documentation.html",
        f"db-{db_num}_deliverable.json",
        "vercel.json",
    ]
    
    missing = []
    for file in required_files:
        if not (website_dir / file).exists():
            missing.append(file)
    
    return len(missing) == 0, missing

def deploy_website(website_dir, db_num):
    """Deploy a website to Vercel."""
    print(f"\n{'='*60}")
    print(f"Deploying db-{db_num}...")
    print(f"Folder: {website_dir.name}")
    print(f"{'='*60}")
    
    # Change to website directory
    original_cwd = os.getcwd()
    os.chdir(website_dir)
    
    try:
        # Deploy to Vercel
        print("Running: vercel --yes --prod")
        result = subprocess.run(
            ['vercel', '--yes', '--prod'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            # Extract deployment URL
            output = result.stdout + result.stderr
            urls = [line for line in output.split('\n') 
                   if 'https://' in line and 'vercel.app' in line]
            
            print(f"✓ Successfully deployed db-{db_num}")
            if urls:
                print(f"  Deployment URL: {urls[0]}")
            return True
        else:
            print(f"✗ Failed to deploy db-{db_num}")
            print(f"  Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ Deployment timeout for db-{db_num}")
        return False
    except Exception as e:
        print(f"✗ Error deploying db-{db_num}: {e}")
        return False
    finally:
        os.chdir(original_cwd)

def main():
    """Main deployment function."""
    print("Database Website Deployment to Vercel")
    print("="*60)
    
    # Check prerequisites
    if not check_vercel_cli():
        return 1
    
    if not check_vercel_auth():
        print("\nPlease authenticate with Vercel first:")
        print("  vercel login")
        return 1
    
    print("\n" + "="*60)
    print("Checking websites...")
    print("="*60)
    
    # Find ready websites
    ready_websites = []
    for db_num in range(6, 16):
        website_dir = find_website_folder(db_num)
        if website_dir:
            is_ready, missing = check_website_ready(website_dir, db_num)
            if is_ready:
                ready_websites.append((db_num, website_dir))
                print(f"✓ db-{db_num}: Ready ({website_dir.name})")
            else:
                print(f"⚠ db-{db_num}: Missing files: {', '.join(missing)}")
        else:
            print(f"✗ db-{db_num}: No website folder found")
    
    if not ready_websites:
        print("\nNo websites ready for deployment.")
        return 1
    
    print(f"\n{'='*60}")
    print(f"Found {len(ready_websites)} website(s) ready for deployment")
    print("="*60)
    
    # Confirm deployment
    response = input("\nProceed with deployment? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Deployment cancelled.")
        return 0
    
    # Deploy websites
    success_count = 0
    fail_count = 0
    
    for db_num, website_dir in ready_websites:
        if deploy_website(website_dir, db_num):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("Deployment Summary")
    print("="*60)
    print(f"Successfully deployed: {success_count}")
    print(f"Failed: {fail_count}")
    print("="*60)
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
