#!/usr/bin/env python3
"""
Extract from db.zip and bundle SQL data into client/db (DATABASE/DOCUMENTATION/QUERIES).
Maps extracted client/db/db-N/dbN-*/ structure to client/db/db-N/{DATABASE,DOCUMENTATION,QUERIES}/.
"""

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CLIENT_DB = BASE_DIR / "client" / "db"
DB_ZIP = BASE_DIR / "db.zip"
EXTRACT_DIR = BASE_DIR / "extract_from_db_zip"


def find_db_folder(extracted_db_dir: Path, db_num: int) -> Path | None:
    """Find dbN-* subfolder in extracted client/db/db-N/."""
    prefix = f"db{db_num}-"
    for item in extracted_db_dir.iterdir():
        if item.is_dir() and item.name.startswith(prefix):
            return item
    return None


def bundle_from_extract(extract_root: Path, client_root: Path, db_nums: list[int], dry_run: bool = False) -> dict:
    """Bundle SQL and docs from extracted zip into client/db structure."""
    extracted_client = extract_root / "client" / "db"
    if not extracted_client.exists():
        return {"error": f"Extracted client/db not found: {extracted_client}"}

    results = {}
    for db_num in db_nums:
        extracted_db = extracted_client / f"db-{db_num}"
        db_folder = find_db_folder(extracted_db, db_num) if extracted_db.exists() else None

        result = {"db": f"db-{db_num}", "synced": [], "errors": []}
        if not db_folder or not db_folder.exists():
            result["errors"].append(f"No db{db_num}-* folder in extract")
            results[f"db-{db_num}"] = result
            continue

        client_db_dir = client_root / f"db-{db_num}"
        data_src = db_folder / "data"

        # 1. DATABASE/ - all *.sql
        if data_src.exists():
            db_dest = client_db_dir / "DATABASE"
            sql_files = [f for f in data_src.iterdir() if f.is_file() and f.suffix.lower() == ".sql"]
            if sql_files:
                if not dry_run:
                    db_dest.mkdir(parents=True, exist_ok=True)
                    for f in sql_files:
                        shutil.copy2(f, db_dest / f.name)
                result["synced"].append(f"DATABASE/ ({len(sql_files)} files)")
        else:
            result["errors"].append("No data/ in extract")

        # 2. DOCUMENTATION/ - html, json, md, .gitignore
        doc_dest = client_db_dir / "DOCUMENTATION"
        for fname in (f"db-{db_num}_documentation.html", f"db-{db_num}_deliverable.json", f"db-{db_num}.md"):
            src = db_folder / fname
            if src.exists():
                if not dry_run:
                    doc_dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, doc_dest / fname)
                result["synced"].append(f"DOCUMENTATION/{fname}")
        if (db_folder / ".gitignore").exists():
            if not dry_run:
                doc_dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(db_folder / ".gitignore", doc_dest / ".gitignore")

        # 3. vercel.json
        vercel_src = db_folder / "vercel.json"
        if vercel_src.exists():
            if not dry_run:
                shutil.copy2(vercel_src, client_db_dir / "vercel.json")
            result["synced"].append("vercel.json")

        # 4. QUERIES - keep from main (resync); deliverable.json has queries but not queries.md/json
        # Client QUERIES/ comes from main db-N/queries via resync - we don't overwrite from zip

        results[f"db-{db_num}"] = result

    return results


def main():
    parser = argparse.ArgumentParser(description="Extract db.zip and bundle SQL data into client/db")
    parser.add_argument("--zip", type=Path, default=DB_ZIP, help="Path to db.zip")
    parser.add_argument("--extract-to", type=Path, default=EXTRACT_DIR, help="Extract directory")
    parser.add_argument("--dbs", type=int, nargs="*", help="DB numbers (default: all in zip)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--keep-extract", action="store_true", help="Keep extract dir after bundling")
    args = parser.parse_args()

    zip_path = args.zip.resolve()
    if not zip_path.exists():
        print(f"Error: {zip_path} not found")
        sys.exit(1)

    extract_to = args.extract_to.resolve()
    client_root = CLIENT_DB.resolve()
    client_root.mkdir(parents=True, exist_ok=True)

    print(f"Extract: {zip_path} -> {extract_to}")
    print(f"Bundle to: {client_root}\n")

    # Extract
    if extract_to.exists():
        shutil.rmtree(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)

    print("Extracting db.zip...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    print("Extracted.\n")

    # Discover db numbers from extract
    extracted_client = extract_to / "client" / "db"
    if not extracted_client.exists():
        print(f"Error: client/db not found in extract")
        sys.exit(1)

    if args.dbs:
        db_nums = sorted(args.dbs)
    else:
        db_nums = sorted([int(d.name.replace("db-", "")) for d in extracted_client.iterdir()
                          if d.is_dir() and d.name.startswith("db-") and d.name[3:].isdigit()])

    print(f"Bundling db-{db_nums[0]} through db-{db_nums[-1]}...")
    if args.dry_run:
        print("(dry run)\n")

    results = bundle_from_extract(extract_to, client_root, db_nums, args.dry_run)
    if isinstance(results, dict) and "error" in results:
        print(f"Error: {results['error']}")
        sys.exit(1)

    for db_name, r in sorted(results.items()):
        status = "OK" if not r["errors"] else "ERROR"
        synced = ", ".join(r["synced"]) if r["synced"] else "(none)"
        print(f"  {db_name}: {status} - {synced}")
        for err in r["errors"]:
            print(f"    Error: {err}")

    if not args.keep_extract and not args.dry_run:
        print("\nRemoving extract directory...")
        shutil.rmtree(extract_to)
        print("Done.")

    errors = sum(1 for r in results.values() if r["errors"])
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
