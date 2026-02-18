#!/usr/bin/env python3
"""
Populate source/db-N/ with DATABASE/, DOCUMENTATION/, QUERIES/ (mirrors client structure).
Builds from existing data/, deliverable/, queries/ so source directly mirrors client/db/db-N/.

Usage:
    python3 scripts/populate_app_trifecta.py [db-1] [db-5] | -a
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
TEMPLATE = ROOT / "template"  # Canonical template: @template/queries.md, queries.json

from db_paths import get_primary_data_file


def populate_app(db_num: int) -> bool:
    """Populate source/db-N/ with DATABASE/, DOCUMENTATION/, QUERIES/ (mirrors client)."""
    db_dir = SOURCE / f"db-{db_num}"
    if not db_dir.exists():
        print(f"  db-{db_num}: SKIP (no source dir)")
        return False

    # Single source of truth: data/ and queries/ only. Output: DATABASE/, DOCUMENTATION/, QUERIES/
    dest_base = db_dir
    db_data = db_dir / "data"
    # Source: queries/ only (single source of truth)
    queries_src = db_dir / "queries"
    if not queries_src.exists() or not (queries_src / "queries.json").exists():
        queries_src = db_dir / "QUERIES"  # fallback when queries/ missing

    # 1. DATABASE/ — from data/ only
    db_dest = dest_base / "DATABASE"
    db_dest.mkdir(parents=True, exist_ok=True)
    all_sql = {}
    if db_data.exists():
        for f in db_data.iterdir():
            if f.is_file() and f.suffix.lower() == ".sql":
                all_sql[f.name] = f

    collected_sql = {}

    def add_schema(dest: str, pg_src: str | None, base_src: str) -> None:
        src = (pg_src if pg_src and pg_src in all_sql else None) or (base_src if base_src in all_sql else None)
        if src:
            collected_sql[dest] = all_sql[src]

    add_schema("schema.sql", "schema.sql", "schema.sql")
    add_schema("schema_extensions.sql", "schema_extensions.sql", "schema_extensions.sql")
    add_schema("insurance_schema.sql", "insurance_schema.sql", "insurance_schema.sql")
    add_schema("nexrad_satellite_schema.sql", "nexrad_satellite_schema.sql", "nexrad_satellite_schema.sql")
    # Only production data (>= 1GB). No sample data.
    primary = get_primary_data_file(all_sql)
    if primary:
        dest_name, src_path = primary
        collected_sql[dest_name] = src_path

    # Remove sample/mini data files from DATABASE/ when not in collected_sql
    for stale in ["data.sql", "data_large.sql", "data_mini.sql"]:
        p = db_dest / stale
        if p.exists() and stale not in collected_sql:
            p.unlink()

    for name, src_path in collected_sql.items():
        shutil.copy2(src_path, db_dest / name)

    # 2. DOCUMENTATION/ — README.md only (no html, json, .gitignore)
    doc_dest = dest_base / "DOCUMENTATION"
    doc_dest.mkdir(parents=True, exist_ok=True)
    # Remove any non-README files to enforce README-only
    for f in list(doc_dest.iterdir()):
        if f.is_file() and f.name != "README.md":
            f.unlink()
    # README.md — write directly to DOCUMENTATION (no docs/ intermediate)
    scripts_dir = Path(__file__).parent
    subprocess.run(
        [sys.executable, str(scripts_dir / "generate_documentation_readme.py"), str(db_num),
         "-o", str(doc_dest / "README.md")],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )

    # 3. QUERIES/ - queries.json from queries_src; queries.md built from header + json
    qdest = dest_base / "QUERIES"
    qdest.mkdir(parents=True, exist_ok=True)
    # Copy queries.json first (skip if src == dest, e.g. case-insensitive FS: queries/ == QUERIES/)
    if queries_src.exists() and (queries_src / "queries.json").exists():
        src_qj = queries_src / "queries.json"
        dst_qj = qdest / "queries.json"
        try:
            if src_qj.resolve() != dst_qj.resolve():
                shutil.copy2(src_qj, dst_qj)
        except shutil.SameFileError:
            pass  # same file on case-insensitive FS
    elif (db_dir / "QUERIES" / "queries.json").exists():
        shutil.copy2(db_dir / "QUERIES" / "queries.json", qdest / "queries.json")
    elif TEMPLATE.exists() and (TEMPLATE / "queries.json").exists():
        shutil.copy2(TEMPLATE / "queries.json", qdest / "queries.json")

    # Build queries.md from source/db-N/queries_header.yaml|.json + queries.json when header exists
    if (db_dir / "queries_header.yaml").exists() or (db_dir / "queries_header.json").exists():
        subprocess.run(
            [sys.executable, str(scripts_dir / "rewrite_queries_md_to_template.py"), f"db-{db_num}"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
    else:
        # No header file: copy queries.md from source or template (skip if src == dest)
        if queries_src.exists() and (queries_src / "queries.md").exists():
            src_qm = queries_src / "queries.md"
            dst_qm = qdest / "queries.md"
            try:
                if src_qm.resolve() != dst_qm.resolve():
                    shutil.copy2(src_qm, dst_qm)
            except shutil.SameFileError:
                pass  # same file on case-insensitive FS
        elif (qdest / "queries.json").exists():
            subprocess.run(
                [sys.executable, str(scripts_dir / "rewrite_queries_md_to_template.py"), f"db-{db_num}"],
                cwd=ROOT,
                capture_output=True,
                check=False,
            )
        elif TEMPLATE.exists() and (TEMPLATE / "queries.md").exists():
            shutil.copy2(TEMPLATE / "queries.md", qdest / "queries.md")

    print(f"  db-{db_num}: OK (DATABASE/{len(collected_sql)} files, DOCUMENTATION/, QUERIES/)")
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
    print("Populating source/db-N/ (DATABASE/, DOCUMENTATION/, QUERIES/)...")
    ok = sum(1 for n in db_nums if populate_app(n))
    print(f"\nDone: {ok}/{len(db_nums)} databases")
    return 0 if ok == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
