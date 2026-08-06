#!/usr/bin/env python3
"""
Synchronize db deliverables to red/client/db using the 3-folder structure.

Each client/db/db-N/ gets:
  - data/     (schema.sql, data.sql, *.sql)
  - queries/  (queries.md, queries.json)
  - docs/     (SCHEMA.md, DATA_DICTIONARY.md, db-N.md)

Usage:
    python3 scripts/sync_to_client_db.py              # Sync all db-6 through db-16
    python3 scripts/sync_to_client_db.py --dbs 6 8 10   # Sync specific dbs
    python3 scripts/sync_to_client_db.py --dry-run   # Show what would be copied
"""

import argparse
import shutil
import sys
from pathlib import Path


def find_data_source(deliverable_dir: Path, db_num: int) -> Path | None:
    """Find data/ folder: deliverable/data or deliverable/dbN-*/data."""
    data = deliverable_dir / "data"
    if data.exists() and data.is_dir():
        return data
    prefix = f"db{db_num}-"
    for item in deliverable_dir.iterdir():
        if item.is_dir() and item.name.startswith(prefix) and item.name != f"db{db_num}-database":
            candidate = item / "data"
            if candidate.exists():
                return candidate
    return None


def find_queries_source(db_dir: Path, deliverable_dir: Path) -> Path | None:
    """Find queries/ folder: deliverable/queries or db-N/queries."""
    for base in (deliverable_dir / "queries", db_dir / "queries"):
        if base.exists() and base.is_dir():
            return base
    return None


def sync_database(db_num: int, db_root: Path, client_root: Path, dry_run: bool = False) -> dict:
    """Sync one database to client using data/, queries/, docs/ structure."""
    db_dir = db_root / f"db-{db_num}"
    deliverable_dir = db_dir / "deliverable"
    client_db_dir = client_root / f"db-{db_num}"

    result = {"db": f"db-{db_num}", "synced": [], "errors": []}

    if not deliverable_dir.exists():
        result["errors"].append(f"Deliverable dir not found: {deliverable_dir}")
        return result

    def copy_tree(src: Path, dest: Path, desc: str) -> bool:
        if not src.exists():
            return False
        if dry_run:
            result["synced"].append(f"Would copy: {desc}")
            return True
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest, dirs_exist_ok=False)
            result["synced"].append(desc)
            return True
        except Exception as e:
            result["errors"].append(f"{desc}: {e}")
            return False

    def copy_file(src: Path, dest: Path, desc: str) -> bool:
        if not src.exists():
            return False
        if dry_run:
            result["synced"].append(f"Would copy: {desc}")
            return True
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            result["synced"].append(desc)
            return True
        except Exception as e:
            result["errors"].append(f"{desc}: {e}")
            return False

    # 1. data/ - schema.sql, data.sql, *.sql (merge from deliverable + db-N/data)
    data_src = find_data_source(deliverable_dir, db_num)
    data_dest = client_db_dir / "data"
    if data_src:
        if dry_run:
            result["synced"].append("Would copy: data/")
        else:
            data_dest.mkdir(parents=True, exist_ok=True)
            if data_dest.exists():
                for f in data_dest.iterdir():
                    if f.is_file():
                        f.unlink()
            for f in data_src.iterdir():
                if f.is_file():
                    shutil.copy2(f, data_dest / f.name)
            # Merge: add any *.sql and README*.md from db-N/data/ not already in deliverable
            existing_names = {f.name for f in data_src.iterdir() if f.is_file()}
            db_data = db_dir / "data"
            if db_data.exists():
                for f in db_data.rglob("*"):
                    if f.is_file() and f.name not in existing_names:
                        if f.suffix.lower() == ".sql" or (f.name.startswith("README") and f.suffix.lower() == ".md"):
                            shutil.copy2(f, data_dest / f.name)
            result["synced"].append("data/")

    # 2. queries/ - queries.md, queries.json
    queries_src = find_queries_source(db_dir, deliverable_dir)
    if queries_src and ((queries_src / "queries.md").exists() or (queries_src / "queries.json").exists()):
        if dry_run:
            result["synced"].append("Would copy: queries/")
        else:
            qdest = client_db_dir / "queries"
            qdest.mkdir(parents=True, exist_ok=True)
            for f in ("queries.md", "queries.json"):
                src = queries_src / f
                if src.exists():
                    shutil.copy2(src, qdest / f)
            result["synced"].append("queries/")

    # 3. docs/ - recursively copy SCHEMA.md, DATA_DICTIONARY.md, db-N.md, *.md, *.html
    docs_src = db_dir / "docs"
    doc_dest = client_db_dir / "docs"
    has_docs = docs_src.exists() or (deliverable_dir / f"db-{db_num}.md").exists()
    if has_docs:
        if dry_run:
            result["synced"].append("Would copy: docs/")
        else:
            doc_dest.mkdir(parents=True, exist_ok=True)
            if docs_src.exists():
                for f in docs_src.rglob("*"):
                    if f.is_file() and f.suffix.lower() in (".md", ".html", ".csv"):
                        rel = f.relative_to(docs_src)
                        dest_file = doc_dest / rel
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, dest_file)
            md_src = deliverable_dir / f"db-{db_num}.md"
            if md_src.exists():
                shutil.copy2(md_src, doc_dest / f"db-{db_num}.md")
            result["synced"].append("docs/")

    # 4. deliverable.openapi.yaml at db-N level
    openapi_src = deliverable_dir / "deliverable.openapi.yaml"
    if openapi_src.exists():
        copy_file(openapi_src, client_db_dir / "deliverable.openapi.yaml", "deliverable.openapi.yaml")

    # 5. Remove obsolete dbN-* folders (old web-deployable structure)
    if client_db_dir.exists():
        prefix = f"db{db_num}-"
        for item in client_db_dir.iterdir():
            if item.is_dir() and item.name.startswith(prefix):
                if dry_run:
                    result["synced"].append(f"Would remove obsolete: {item.name}/")
                else:
                    try:
                        shutil.rmtree(item)
                        result["synced"].append(f"Removed obsolete: {item.name}/")
                    except Exception as e:
                        result["errors"].append(f"Remove {item.name}: {e}")

    # 6. Populate: recursively fill any empty/small files from source
    if not dry_run and client_db_dir.exists():
        populated = populate_from_source(db_dir, deliverable_dir, client_db_dir, db_num)
        result["synced"].extend(populated)

    return result


def populate_from_source(db_dir: Path, deliverable_dir: Path, client_dir: Path, db_num: int) -> list[str]:
    """Recursively find empty or small files in client and fill from source. Returns list of populated paths."""
    populated = []
    min_size = 50  # files smaller than this are considered unpopulated

    for client_file in client_dir.rglob("*"):
        if not client_file.is_file():
            continue
        try:
            sz = client_file.stat().st_size
        except OSError:
            continue
        if sz >= min_size:
            continue

        rel = client_file.relative_to(client_dir)
        source_candidates = [
            db_dir / rel,
            deliverable_dir / rel,
        ]
        # Map client/data/X -> deliverable/data/X, deliverable/dbN-*/data/X
        prefix = f"db{db_num}-"
        for d in deliverable_dir.iterdir():
            if d.is_dir() and d.name.startswith(prefix) and d.name != f"db{db_num}-database":
                source_candidates.append(d / rel)
                if len(rel.parts) >= 2:
                    source_candidates.append(d / rel.parts[0] / rel.name)
                source_candidates.append(d / "data" / rel.name)
                source_candidates.append(d / "queries" / rel.name)

        for src in source_candidates:
            if src.exists() and src.is_file():
                try:
                    src_sz = src.stat().st_size
                    if src_sz > sz:
                        shutil.copy2(src, client_file)
                        populated.append(f"Populated: {rel}")
                        break
                except OSError:
                    pass

    return populated


def main():
    parser = argparse.ArgumentParser(description="Sync db deliverables to red/client/db (3-folder structure)")
    parser.add_argument("--dbs", type=int, nargs="*", default=list(range(2, 18)),
                        help="Database numbers to sync (default: 2-17)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied")
    parser.add_argument("--db-root", type=Path, default=Path(__file__).parent.parent,
                        help="Root of db repository")
    parser.add_argument("--client-root", type=Path,
                        default=Path(__file__).parent.parent.parent / "red" / "client" / "db",
                        help="Root of client/db (default: ../red/client/db)")
    args = parser.parse_args()

    db_root = args.db_root.resolve()
    client_root = args.client_root.resolve()

    if not client_root.parent.exists():
        print(f"Client root parent not found: {client_root.parent}")
        sys.exit(1)

    print(f"Sync: {db_root} -> {client_root}")
    print("Structure: data/, queries/, docs/\n")
    if args.dry_run:
        print("(dry run - no files will be copied)\n")

    all_results = []
    for db_num in sorted(args.dbs):
        result = sync_database(db_num, db_root, client_root, args.dry_run)
        all_results.append(result)

        status = "OK" if not result["errors"] else "ERROR"
        synced = ", ".join(result["synced"]) if result["synced"] else "(none)"
        print(f"  db-{db_num}: {status} - {synced}")
        for err in result["errors"]:
            print(f"    Error: {err}")

    errors = sum(1 for r in all_results if r["errors"])
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
