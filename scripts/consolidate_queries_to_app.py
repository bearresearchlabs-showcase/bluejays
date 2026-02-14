#!/usr/bin/env python3
"""
Consolidate queries folders: keep only app/QUERIES/, archive the rest.
Single source of truth: source/db-N/app/QUERIES/

Archives to: archive/db-N-queries-legacy/ (root QUERIES, deliverable/queries, queries)
"""

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
ARCHIVE = ROOT / "archive"


def get_db_nums(args):
    """Parse db numbers from args."""
    if not args or "-a" in args or "--all" in args:
        return list(range(1, 17))
    out = []
    for x in args:
        x = str(x).strip()
        if x.startswith("db-"):
            try:
                out.append(int(x.split("db-")[1]))
            except (ValueError, IndexError):
                continue
        elif x.isdigit():
            out.append(int(x))
    return sorted(set(out)) if out else list(range(1, 17))


def consolidate_db(db_num: int, dry_run: bool) -> dict:
    """Archive extra queries folders for db-N. Keep only app/QUERIES."""
    db_dir = SOURCE / f"db-{db_num}"
    app_queries = db_dir / "app" / "QUERIES"
    result = {"db": f"db-{db_num}", "archived": [], "removed": [], "errors": []}

    if not db_dir.exists():
        result["errors"].append("db dir not found")
        return result

    if not app_queries.exists() or not (app_queries / "queries.json").exists():
        result["errors"].append("app/QUERIES/ missing or no queries.json - skip")
        return result

    to_archive = []
    for name, path in [
        ("QUERIES", db_dir / "QUERIES"),
        ("deliverable/queries", db_dir / "deliverable" / "queries"),
        ("queries", db_dir / "queries"),
    ]:
        if path.exists() and path.is_dir():
            to_archive.append((name, path))

    if not to_archive:
        return result

    # Deduplicate: on case-insensitive FS (macOS), QUERIES and queries resolve to same dir.
    # Path.resolve() preserves case, so use os.path.samefile() for dedup.
    def _same_as_any(p, seen_paths):
        try:
            for s in seen_paths:
                if os.path.samefile(str(p), str(s)):
                    return True
        except OSError:
            pass
        return False

    seen_paths = []
    deduped = []
    for name, path in to_archive:
        try:
            if _same_as_any(path, seen_paths):
                continue
            seen_paths.append(path)
            deduped.append((name, path))
        except OSError:
            pass
    to_archive = deduped

    archive_dir = ARCHIVE / f"db-{db_num}-queries-legacy"
    if dry_run:
        for name, path in to_archive:
            result["archived"].append(f"Would archive: {name} -> {archive_dir.name}/")
        return result

    archive_dir.mkdir(parents=True, exist_ok=True)
    for name, path in to_archive:
        # Use unique dest name: QUERIES -> QUERIES, deliverable/queries -> deliverable_queries, queries -> queries
        dest_name = name.replace("/", "_")
        dest = archive_dir / dest_name
        if path.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(path, dest)
            shutil.rmtree(path)
            result["archived"].append(name)
            result["removed"].append(name)
        else:
            result["errors"].append(f"{name} is not a dir")
    return result


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Consolidate queries to app/QUERIES only")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or -a for all")
    ap.add_argument("-a", "--all", action="store_true", help="All db-1..16")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = ap.parse_args()
    dry_run = args.dry_run
    db_nums = get_db_nums(args.dbs + (["-a"] if args.all else []))

    print("Consolidating queries: keep only app/QUERIES/")
    if dry_run:
        print("(dry run - no changes)")
    print()

    for db_num in db_nums:
        r = consolidate_db(db_num, dry_run)
        if r["errors"]:
            print(f"  db-{db_num}: SKIP - {'; '.join(r['errors'])}")
        elif r["archived"]:
            print(f"  db-{db_num}: archived {r['archived']}")
        else:
            print(f"  db-{db_num}: OK (already consolidated)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
