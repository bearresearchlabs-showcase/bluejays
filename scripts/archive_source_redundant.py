#!/usr/bin/env python3
"""
Archive redundant files from source/db-N to archive/source-redundant/db-N/.

Moves research/, results/, validation/, metadata/, scripts/, docs/, package/
and other files not needed for app/ generation. Uses same logic as
analyze_source_redundancy.py.

Usage:
  python3 scripts/archive_source_redundant.py --dry-run -a   # Preview
  python3 scripts/archive_source_redundant.py -a            # Execute
  python3 scripts/archive_source_redundant.py db-1 db-6     # Specific dbs
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
ARCHIVE_BASE = ROOT / "archive" / "source-redundant"


def is_redundant(p: str) -> bool:
    """Same logic as analyze_source_redundancy."""
    if p.startswith("app/"):
        return False
    redundant_prefixes = ("research/", "results/", "validation/", "metadata/", "scripts/", "docs/", "package/")
    if any(p.startswith(prefix) or p == prefix.rstrip("/") for prefix in redundant_prefixes):
        return True
    if p.endswith(".zip") or p.endswith(".backup") or ".colab_" in p:
        return True
    if p in ("deliverable.openapi.yaml", "deliverable/README.md", "deliverable/DELIVERABLE.md",
             "deliverable/database_deliverable.json", "golden_findings.json", "db6_complete_dump.sql"):
        return True
    return False


def collect_redundant(db_dir: Path) -> list[tuple[Path, Path]]:
    """Return list of (src, dest) paths to move. Moves top-level dirs and specific files."""
    moves = []
    archive_dir = ARCHIVE_BASE / db_dir.name

    # 1. Top-level redundant directories (move whole tree)
    redundant_dirs = ("research", "results", "validation", "metadata", "scripts", "docs", "package")
    for d in redundant_dirs:
        src = db_dir / d
        if src.exists() and src.is_dir():
            moves.append((src, archive_dir / d))

    # 2. Redundant root files
    root_files = ("deliverable.openapi.yaml", "golden_findings.json", "db6_complete_dump.sql")
    for f in root_files:
        src = db_dir / f
        if src.exists() and src.is_file():
            moves.append((src, archive_dir / f))

    # 3. Redundant files inside deliverable/
    deliv_files = ("README.md", "DELIVERABLE.md", "database_deliverable.json")
    for f in deliv_files:
        src = db_dir / "deliverable" / f
        if src.exists() and src.is_file():
            moves.append((src, archive_dir / "deliverable" / f))

    # 4. Zip, backup, colab files (exclude those inside dirs we're already moving)
    dirs_being_moved = {str(m[0]) for m in moves if m[0].is_dir()}
    for root, _dirs, files in db_dir.walk():
        try:
            rel = Path(root).relative_to(db_dir)
        except ValueError:
            continue
        root_str = str(Path(root))
        if any(root_str.startswith(d + "/") or root_str == d for d in dirs_being_moved):
            continue  # inside a dir we're moving
        for f in files:
            if f.endswith(".zip") or f.endswith(".backup") or ".colab_" in f:
                src = Path(root) / f
                r = rel / f
                moves.append((src, archive_dir / r))

    return moves


def archive_db(db_num: int, dry_run: bool) -> int:
    """Archive redundant files for one db. Returns count moved."""
    db_dir = SOURCE / f"db-{db_num}"
    if not db_dir.exists():
        print(f"  db-{db_num}: SKIP (not found)")
        return 0

    moves = collect_redundant(db_dir)
    if not moves:
        print(f"  db-{db_num}: nothing to archive")
        return 0

    count = 0
    for src, dest in moves:
        if not src.exists():
            continue
        if dry_run:
            print(f"  would move: {src.relative_to(ROOT)} -> {dest.relative_to(ROOT)}")
            count += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(dest))
            print(f"  moved: {src.relative_to(ROOT)}")
            count += 1
        except Exception as e:
            print(f"  ERROR moving {src}: {e}")

    return count


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Archive redundant files from source/db-N")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all")
    ap.add_argument("-a", "--all", action="store_true", help="All db-1..db-16")
    ap.add_argument("--dry-run", action="store_true", help="Preview only, do not move")
    args = ap.parse_args()

    db_nums = list(range(1, 17)) if args.all or not args.dbs else []
    if not db_nums:
        for a in args.dbs:
            a = str(a).replace("db-", "")
            try:
                db_nums.append(int(a))
            except ValueError:
                pass
        db_nums = sorted(set(db_nums))

    mode = "DRY RUN" if args.dry_run else "ARCHIVING"
    print(f"{mode} redundant files from source/db-N to archive/source-redundant/")
    print(f"Databases: {db_nums}\n")

    total = 0
    for n in db_nums:
        c = archive_db(n, args.dry_run)
        total += c

    print(f"\nTotal: {total} items {'would be ' if args.dry_run else ''}archived")
    if not args.dry_run and total > 0:
        print(f"Archived to: {ARCHIVE_BASE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
