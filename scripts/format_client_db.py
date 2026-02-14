#!/usr/bin/env python3
"""
Format client/db to match the golden solution structure (db-6).
Each db-{N} in client/db will contain only the web-deployable folder db{N}-{name}/ with:
  - db-{N}_documentation.html
  - db-{N}_deliverable.json
  - db-{N}.md
  - vercel.json
  - .gitignore
  - data/
  - queries/ (optional, for notebooks)
"""

import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CLIENT_DB_DIR = BASE_DIR / "client" / "db"
ROOT_DB_DIR = BASE_DIR

# Database to web-deployable folder mapping (from format output / golden solution)
DB_TO_DELIVERABLE = {
    "db-1": "db1-chat-messaging-platform",
    "db-2": "db2-filling-station-retail",
    "db-3": "db3-hierarchical-orders",
    "db-4": "db4-sharedai-models",
    "db-5": "db5-pos-retail",
    "db-6": "db6-weather-consulting-insurance",
    "db-7": "db7-maritime-shipping-intelligence",
    "db-8": "db8-job-market-intelligence",
    "db-9": "db9-shipping-intelligence",
    "db-10": "db10-marketing-intelligence",
    "db-11": "db11-parking-intelligence",
    "db-12": "db12-credit-card-and-rewards-optimization-system",
    "db-13": "db13-ai-benchmark-marketing-database",
    "db-14": "db14-cloud-instance-cost-database",
    "db-15": "db15-electricity-cost-and-solar-rebate-database",
    "db-16": "db16-flood-risk-assessment",
}


def discover_web_deployable_folders() -> dict:
    """Discover actual web-deployable folder names in each db's deliverable."""
    found = {}
    for db_name in sorted(DB_TO_DELIVERABLE.keys()):
        deliverable_dir = ROOT_DB_DIR / db_name / "deliverable"
        if not deliverable_dir.exists():
            continue
        # Look for dbN-descriptive-name pattern
        for sub in deliverable_dir.iterdir():
            if sub.is_dir() and sub.name.startswith(f"db{db_name.split('-')[1]}-") and "-" in sub.name[3:]:
                # Prefer longer/more descriptive name if multiple (e.g. db12-credit-card... over db12-database)
                if db_name not in found or len(sub.name) > len(found[db_name]):
                    found[db_name] = sub.name
    return found


def format_client_db():
    """Format client/db to proper structure - one web-deployable folder per db."""
    print("=" * 70)
    print("Formatting client/db to Golden Solution Structure")
    print("=" * 70)

    if not CLIENT_DB_DIR.exists():
        CLIENT_DB_DIR.mkdir(parents=True)
        print(f"Created {CLIENT_DB_DIR}")

    discovered = discover_web_deployable_folders()
    if not discovered:
        print("No web-deployable folders found. Run /format first for db-1 through db-16.")
        return 1

    # Remove client/db folders that don't have a proper source (db-1 through db-5, etc.)
    all_db_dirs = [d for d in CLIENT_DB_DIR.iterdir() if d.is_dir() and d.name.startswith("db-")]
    for old_dir in all_db_dirs:
        db_name = old_dir.name
        if db_name not in discovered:
            shutil.rmtree(old_dir)
            print(f"  Removed {db_name} (no web-deployable source)")

    # Remove non-db folders (scripts, etc.) - client deliverable should only have db-N/
    for item in list(CLIENT_DB_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith("db-"):
            shutil.rmtree(item)
            print(f"  Removed {item.name}/ (not a database deliverable)")

    copied = 0
    for db_name, folder_name in sorted(discovered.items()):
        src = ROOT_DB_DIR / db_name / "deliverable" / folder_name
        client_db_n = CLIENT_DB_DIR / db_name

        if not src.exists():
            print(f"  Skip {db_name}: {folder_name} not found")
            continue

        # Required files check (golden solution structure)
        db_num = db_name.split("-")[1]
        required = [f"db-{db_num}_documentation.html", f"db-{db_num}_deliverable.json", "vercel.json", ".gitignore"]
        missing = [r for r in required if not (src / r).exists()]
        if missing:
            print(f"  Skip {db_name}: missing {missing} (run /format {db_name})")
            continue

        # Remove existing client/db/db-N content (clean slate)
        if client_db_n.exists():
            shutil.rmtree(client_db_n)

        # Copy web-deployable folder to client/db/db-N/dbN-name/
        # Structure: client/db/db-6/db6-weather-consulting-insurance/ (matches sync scripts)
        client_deployable = client_db_n / folder_name
        client_db_n.mkdir(parents=True)
        shutil.copytree(src, client_deployable, ignore=shutil.ignore_patterns(".git", "*.dump"))
        # Ensure .gitignore is included
        src_gitignore = src / ".gitignore"
        if src_gitignore.exists() and not (client_deployable / ".gitignore").exists():
            shutil.copy2(src_gitignore, client_deployable / ".gitignore")

        print(f"  OK {db_name}: {folder_name}")
        copied += 1

    print()
    print(f"Formatted {copied} databases in {CLIENT_DB_DIR}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(format_client_db())
