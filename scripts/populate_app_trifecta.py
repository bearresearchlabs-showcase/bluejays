#!/usr/bin/env python3
"""
Populate source/db-N/app/ with DATABASE/, DOCUMENTATION/, QUERIES/ (iron triangle trifecta).
Builds app/ from existing data/, deliverable/, queries/ so app/ becomes the canonical source.

Usage:
    python3 scripts/populate_app_trifecta.py [db-1] [db-5] | -a
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
TEMPLATE = ROOT / "template"  # Canonical template: @template/queries.md, queries.json
GB = 1024**3


def find_deliverable_data(db_dir: Path, db_num: int) -> Path | None:
    """Find data/ folder: deliverable/data or deliverable/dbN-*/data."""
    deliverable_dir = db_dir / "deliverable"
    if not deliverable_dir.exists():
        return None
    data = deliverable_dir / "data"
    if data.exists() and data.is_dir():
        return data
    prefix = f"db{db_num}-"
    for item in deliverable_dir.iterdir():
        if item.is_dir() and item.name.startswith(prefix):
            candidate = item / "data"
            if candidate.exists():
                return candidate
    return None


def find_web_deliverable(db_dir: Path, db_num: int) -> Path | None:
    """Find web-deployable folder dbN-* with documentation."""
    deliverable_dir = db_dir / "deliverable"
    if not deliverable_dir.exists():
        return None
    prefix = f"db{db_num}-"
    for item in deliverable_dir.iterdir():
        if item.is_dir() and item.name.startswith(prefix):
            return item
    return None


def populate_app(db_num: int) -> bool:
    """Populate source/db-N/app/ with DATABASE/, DOCUMENTATION/, QUERIES/."""
    db_dir = SOURCE / f"db-{db_num}"
    app_dir = db_dir / "app"
    if not db_dir.exists():
        print(f"  db-{db_num}: SKIP (no source dir)")
        return False

    app_dir.mkdir(parents=True, exist_ok=True)
    db_data = db_dir / "data"
    deliv_data = find_deliverable_data(db_dir, db_num)
    web_d = find_web_deliverable(db_dir, db_num)
    if not web_d:
        web_d = db_dir / "deliverable"
    queries_src = db_dir / "QUERIES"  # prefer uppercase (iron triangle)
    if not queries_src.exists() or not (queries_src / "queries.json").exists():
        queries_src = db_dir / "queries"
    if not queries_src.exists() or not (queries_src / "queries.json").exists():
        queries_src = db_dir / "deliverable" / "queries"

    # 1. DATABASE/
    db_dest = app_dir / "DATABASE"
    db_dest.mkdir(parents=True, exist_ok=True)
    all_sql = {}
    if db_data.exists():
        for f in db_data.iterdir():
            if f.is_file() and f.suffix.lower() == ".sql":
                all_sql[f.name] = f
    if deliv_data and deliv_data.exists():
        for f in deliv_data.iterdir():
            if f.is_file() and f.suffix.lower() == ".sql" and f.name not in all_sql:
                all_sql[f.name] = f

    collected_sql = {}

    def add_schema(dest: str, pg_src: str | None, base_src: str) -> None:
        src = (pg_src if pg_src and pg_src in all_sql else None) or (base_src if base_src in all_sql else None)
        if src:
            collected_sql[dest] = all_sql[src]

    add_schema("schema.sql", "schema_postgresql.sql", "schema.sql")
    add_schema("schema_extensions.sql", "schema_extensions_postgresql.sql", "schema_extensions.sql")
    add_schema("insurance_schema.sql", "insurance_schema_postgresql.sql", "insurance_schema.sql")
    add_schema("nexrad_satellite_schema.sql", "nexrad_satellite_schema_postgresql.sql", "nexrad_satellite_schema.sql")
    if "schema_postgresql_large.sql" in all_sql:
        collected_sql["schema_postgresql_large.sql"] = all_sql["schema_postgresql_large.sql"]
    if "data.sql" in all_sql:
        collected_sql["data.sql"] = all_sql["data.sql"]
    if "data_large_postgresql.sql" in all_sql and all_sql["data_large_postgresql.sql"].stat().st_size >= GB:
        collected_sql["data_large.sql"] = all_sql["data_large_postgresql.sql"]
    elif "data_large.sql" in all_sql and all_sql["data_large.sql"].stat().st_size >= GB:
        collected_sql["data_large.sql"] = all_sql["data_large.sql"]
    elif "data.sql" in all_sql and all_sql["data.sql"].stat().st_size >= GB:
        collected_sql["data_large.sql"] = all_sql["data.sql"]

    for name, src_path in collected_sql.items():
        shutil.copy2(src_path, db_dest / name)

    # 2. DOCUMENTATION/
    doc_dest = app_dir / "DOCUMENTATION"
    doc_dest.mkdir(parents=True, exist_ok=True)
    for fname in (f"db-{db_num}_documentation.html", f"db-{db_num}_deliverable.json", f"db-{db_num}.md"):
        for src in (web_d / fname, db_dir / "deliverable" / fname):
            if src.exists():
                shutil.copy2(src, doc_dest / fname)
                break
    if (web_d / ".gitignore").exists():
        shutil.copy2(web_d / ".gitignore", doc_dest / ".gitignore")

    # 3. QUERIES/ - from queries_src, else @template/ as fallback
    qdest = app_dir / "QUERIES"
    qdest.mkdir(parents=True, exist_ok=True)
    if queries_src.exists():
        for fname in ("queries.md", "queries.json"):
            src = queries_src / fname
            if src.exists():
                shutil.copy2(src, qdest / fname)
    if not (qdest / "queries.json").exists():
        alt_q = db_dir / "QUERIES"
        if alt_q.exists():
            for fname in ("queries.md", "queries.json"):
                src = alt_q / fname
                if src.exists():
                    shutil.copy2(src, qdest / fname)
    if not (qdest / "queries.json").exists() and TEMPLATE.exists():
        for fname in ("queries.md", "queries.json"):
            src = TEMPLATE / fname
            if src.exists():
                shutil.copy2(src, qdest / fname)

    print(f"  db-{db_num}: OK app/ (DATABASE/{len(collected_sql)} files, DOCUMENTATION/, QUERIES/)")
    return True


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Populate source/db-N/app/ (iron triangle)")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all")
    ap.add_argument("-a", "--all", action="store_true", help="Populate all db-1..db-16")
    args = ap.parse_args()
    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = []
        for a in args.dbs:
            a = str(a).replace("db-", "")
            try:
                db_nums.append(int(a))
            except ValueError:
                pass
        if len(db_nums) == 2 and db_nums[0] < db_nums[1]:
            db_nums = list(range(db_nums[0], db_nums[1] + 1))
        db_nums = sorted(set(db_nums))
    print("Populating source/db-N/app/ (DATABASE/, DOCUMENTATION/, QUERIES/)...")
    ok = sum(1 for n in db_nums if populate_app(n))
    print(f"\nDone: {ok}/{len(db_nums)} databases")
    return 0 if ok == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
