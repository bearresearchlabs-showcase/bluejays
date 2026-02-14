#!/usr/bin/env python3
"""
Resync main db deliverables to client/db using DATABASE/DOCUMENTATION/QUERIES structure.
Faithful to source: db-N/data is primary for *.sql; db-N/queries for queries; deliverable/dbN-*/ for docs.

Usage:
    python3 scripts/resync_client_db.py              # Sync all db-1 through db-16
    python3 scripts/resync_client_db.py --dbs 1 6 10  # Sync specific dbs
    python3 scripts/resync_client_db.py --dry-run    # Show what would be copied
"""

import argparse
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SOURCE_DB = BASE_DIR / "source"  # Source of truth: source/db-1..db-16
CLIENT_DB = BASE_DIR / "client" / "db"


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


def _sync_from_app(app_dir: Path, client_db_dir: Path, db_num: int, dry_run: bool) -> dict:
    """Sync from source/db-N/app/ (iron triangle) to client/db/db-N/."""
    result = {"db": f"db-{db_num}", "synced": [], "errors": []}

    def copy_dir(src_dir: Path, dest_dir: Path, name: str) -> None:
        if not src_dir.exists():
            return
        if dry_run:
            count = len([f for f in src_dir.iterdir() if f.is_file()])
            result["synced"].append(f"Would copy {name}/ ({count} files)")
            return
        dest_dir.mkdir(parents=True, exist_ok=True)
        for f in src_dir.iterdir():
            if f.is_file():
                shutil.copy2(f, dest_dir / f.name)
        count = len([f for f in dest_dir.iterdir() if f.is_file()])
        result["synced"].append(f"{name}/ ({count} files)")

    def copy_file(src: Path, dest: Path, desc: str) -> bool:
        if not src.exists() or not src.is_file():
            return False
        if dry_run:
            result["synced"].append(f"Would copy: {desc}")
            return True
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        result["synced"].append(desc)
        return True

    copy_dir(app_dir / "DATABASE", client_db_dir / "DATABASE", "DATABASE")
    copy_dir(app_dir / "DOCUMENTATION", client_db_dir / "DOCUMENTATION", "DOCUMENTATION")
    copy_dir(app_dir / "QUERIES", client_db_dir / "QUERIES", "QUERIES")

    # vercel.json - from app/DOCUMENTATION parent or create minimal
    web_d = app_dir.parent / "deliverable"
    prefix = f"db{db_num}-"
    for item in (web_d.iterdir() if web_d.exists() else []):
        if item.is_dir() and item.name.startswith(prefix):
            vercel_src = item / "vercel.json"
            if vercel_src.exists():
                copy_file(vercel_src, client_db_dir / "vercel.json", "vercel.json")
                break
    if not dry_run and not (client_db_dir / "vercel.json").exists():
        (client_db_dir / "vercel.json").write_text(
            f'{{"rewrites":[{{"source":"/","destination":"/DOCUMENTATION/db-{db_num}_documentation.html"}}]}}',
            encoding="utf-8",
        )
        result["synced"].append("vercel.json (created)")

    return result


def sync_database(db_num: int, db_root: Path, client_root: Path, dry_run: bool = False) -> dict:
    """Sync one database to client using DATABASE/, DOCUMENTATION/, QUERIES/ structure.
    Source: source/db-N/app/ (iron triangle) when app/ exists; else legacy data/, deliverable/, queries/."""
    db_dir = db_root / f"db-{db_num}"
    app_dir = db_dir / "app"
    client_db_dir = client_root / f"db-{db_num}"

    result = {"db": f"db-{db_num}", "synced": [], "errors": []}

    if not db_dir.exists():
        result["errors"].append(f"db dir not found: {db_dir}")
        return result

    # When app/ exists (iron triangle), copy directly from app/ to client
    if app_dir.exists() and (app_dir / "DATABASE").exists():
        return _sync_from_app(app_dir, client_db_dir, db_num, dry_run)

    def copy_file(src: Path, dest: Path, desc: str) -> bool:
        if not src.exists() or not src.is_file():
            return False
        if src.resolve() == dest.resolve():
            return True  # same file, skip
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

    # 1. DATABASE/ - PostgreSQL-only SQL: schema, data.sql, data_large (full 1GB)
    db_data = db_dir / "data"
    deliv_data = find_deliverable_data(db_dir, db_num)

    db_dest = client_db_dir / "DATABASE"
    all_sql = {}  # name -> path
    if db_data.exists():
        for f in db_data.iterdir():
            if f.is_file() and f.suffix.lower() == ".sql":
                all_sql[f.name] = f
    if deliv_data and deliv_data.exists():
        for f in deliv_data.iterdir():
            if f.is_file() and f.suffix.lower() == ".sql" and f.name not in all_sql:
                all_sql[f.name] = f

    # Filter: PostgreSQL-only SQL. Output: schema.sql, data.sql, data_large.sql (>= 1GB)
    GB = 1024**3
    collected_sql = {}  # dest_name -> src_path

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

    # data_large.sql: must be >= 1GB. Prefer PostgreSQL variant.
    if "data_large_postgresql.sql" in all_sql and all_sql["data_large_postgresql.sql"].stat().st_size >= GB:
        collected_sql["data_large.sql"] = all_sql["data_large_postgresql.sql"]
    elif "data_large.sql" in all_sql and all_sql["data_large.sql"].stat().st_size >= GB:
        collected_sql["data_large.sql"] = all_sql["data_large.sql"]
    elif "data.sql" in all_sql and all_sql["data.sql"].stat().st_size >= GB:
        collected_sql["data_large.sql"] = all_sql["data.sql"]  # db-16: data.sql is 2.5GB

    if collected_sql:
        if dry_run:
            result["synced"].append(f"Would copy DATABASE/ ({len(collected_sql)} files)")
        else:
            db_dest.mkdir(parents=True, exist_ok=True)
            # Remove obsolete .sql files no longer in source (snapshot list to avoid iterate-while-modify)
            if db_dest.exists():
                for f in list(db_dest.iterdir()):
                    if f.is_file() and f.suffix.lower() == ".sql" and f.name not in collected_sql:
                        f.unlink()
                        result["synced"].append(f"Removed obsolete: DATABASE/{f.name}")
            for name, src_path in collected_sql.items():
                shutil.copy2(src_path, db_dest / name)
            result["synced"].append(f"DATABASE/ ({len(collected_sql)} files including data_large.sql)" if "data_large.sql" in collected_sql else f"DATABASE/ ({len(collected_sql)} files)")

    # 2. DOCUMENTATION/ - html, json, md from deliverable/dbN-*/
    web_d = find_web_deliverable(db_dir, db_num)
    if not web_d:
        web_d = db_dir / "deliverable"
    doc_dest = client_db_dir / "DOCUMENTATION"
    for fname in (f"db-{db_num}_documentation.html", f"db-{db_num}_deliverable.json", f"db-{db_num}.md"):
        for src in (web_d / fname, db_dir / "deliverable" / fname):
            if src.exists():
                if copy_file(src, doc_dest / fname, f"DOCUMENTATION/{fname}"):
                    break
        # Also copy .gitignore if present
        gitignore = web_d / ".gitignore"
        if gitignore.exists():
            copy_file(gitignore, doc_dest / ".gitignore", "DOCUMENTATION/.gitignore")

    if not dry_run and doc_dest.exists() and any(doc_dest.iterdir()):
        result["synced"].append("DOCUMENTATION/")

    # 3. QUERIES/ - queries.md, queries.json
    queries_src = db_dir / "queries"
    if not queries_src.exists():
        queries_src = db_dir / "deliverable" / "queries"
    qdest = client_db_dir / "QUERIES"
    if queries_src.exists():
        for fname in ("queries.md", "queries.json"):
            src = queries_src / fname
            if src.exists():
                copy_file(src, qdest / fname, f"QUERIES/{fname}")
        if not dry_run and qdest.exists() and any(qdest.iterdir()):
            if "QUERIES/" not in " ".join(result["synced"]):
                result["synced"].append("QUERIES/")

    # 4. Legacy dbN-*/data - sync same PostgreSQL-only SQL from web deliverable
    if web_d and web_d.exists():
        web_data = web_d / "data"
        if web_data.exists():
            prefix = f"db{db_num}-"
            client_items = list(client_db_dir.iterdir()) if client_db_dir.exists() else []
            for client_item in client_items:
                if client_item.is_dir() and client_item.name.startswith(prefix):
                    legacy_data_dest = client_item / "data"
                    if legacy_data_dest.exists() or not dry_run:
                        web_sql = {f.name: f for f in web_data.iterdir() if f.is_file() and f.suffix.lower() == ".sql"}
                        legacy_collected = {}
                        for dest_name, src_path in collected_sql.items():
                            if src_path.name in web_sql:
                                legacy_collected[dest_name] = web_sql[src_path.name]
                            elif dest_name in web_sql:
                                legacy_collected[dest_name] = web_sql[dest_name]
                        if not legacy_collected:
                            legacy_collected = web_sql
                        if legacy_collected:
                            if dry_run:
                                result["synced"].append(f"Would sync {client_item.name}/data/ ({len(legacy_collected)} files)")
                            else:
                                legacy_data_dest.mkdir(parents=True, exist_ok=True)
                                for f in list(legacy_data_dest.iterdir()):
                                    if f.is_file() and f.suffix.lower() == ".sql" and f.name not in legacy_collected:
                                        f.unlink()
                                        result["synced"].append(f"Removed obsolete: {client_item.name}/data/{f.name}")
                                for name, src_path in legacy_collected.items():
                                    shutil.copy2(src_path, legacy_data_dest / name)
                                result["synced"].append(f"{client_item.name}/data/ ({len(legacy_collected)} files)")
                    break  # only sync first matching legacy folder

    # 5. vercel.json - from web deliverable or template
    vercel_src = web_d / "vercel.json" if web_d and web_d.exists() else None
    if not vercel_src or not vercel_src.exists():
        vercel_src = client_db_dir / "vercel.json"  # keep existing
    if vercel_src and vercel_src.exists():
        copy_file(vercel_src, client_db_dir / "vercel.json", "vercel.json")
    else:
        # Create minimal vercel.json if missing
        if not dry_run and not (client_db_dir / "vercel.json").exists():
            vercel_content = '''{
  "rewrites": [{"source": "/", "destination": "/DOCUMENTATION/db-''' + str(db_num) + '''_documentation.html"}]
}
'''
            (client_db_dir / "vercel.json").write_text(vercel_content, encoding="utf-8")
            result["synced"].append("vercel.json (created)")

    return result


def main():
    parser = argparse.ArgumentParser(description="Resync db deliverables to client/db (DATABASE/DOCUMENTATION/QUERIES)")
    parser.add_argument("--dbs", type=int, nargs="*", default=list(range(1, 17)),
                        help="Database numbers to sync (default: 1-16)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied")
    parser.add_argument("--db-root", type=Path, default=SOURCE_DB, help="Source db root (default: source/)")
    parser.add_argument("--client-root", type=Path, default=CLIENT_DB, help="Root of client/db")
    args = parser.parse_args()

    db_root = args.db_root.resolve()
    client_root = args.client_root.resolve()

    client_root.mkdir(parents=True, exist_ok=True)

    print(f"Resync: {db_root} -> {client_root}")
    print("Structure: DATABASE/, DOCUMENTATION/, QUERIES/ (includes data_large.sql)\n")
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
