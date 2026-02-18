#!/usr/bin/env python3
"""
Resync source/db-N to client/db/db-N. Source mirrors client: DATABASE/, DOCUMENTATION/, QUERIES/.
Single source of truth: data/ -> DATABASE/, docs/ -> DOCUMENTATION/, queries/ -> QUERIES/.
Uses shutil.copy2 (byte-preserving) and verifies bit-for-bit after sync when --verify is set.

Usage:
    python3 scripts/resync_client_db.py              # Sync all db-1 through db-16
    python3 scripts/resync_client_db.py --dbs 1 6 10  # Sync specific dbs
    python3 scripts/resync_client_db.py --dry-run    # Show what would be copied
    python3 scripts/resync_client_db.py --verify     # Sync then verify byte-for-byte
"""

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

from db_paths import get_primary_data_file

BASE_DIR = Path(__file__).parent.parent
SOURCE_DB = BASE_DIR / "source"  # Source of truth: source/db-1..db-16
CLIENT_DB = BASE_DIR / "client" / "db"


def _file_sha256(path: Path) -> str | None:
    """SHA-256 hash of file contents (bit-for-bit)."""
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _get_canonical_src(db_dir: Path) -> Path | None:
    """Return path to canonical structure: root or app/. Backwards compat."""
    if (db_dir / "DATABASE").exists():
        return db_dir
    app_dir = db_dir / "app"
    if app_dir.exists() and (app_dir / "DATABASE").exists():
        return app_dir
    return None


def _verify_synced(db_num: int, db_root: Path, client_root: Path) -> list[tuple[str, bool]]:
    """Verify client files are byte-for-byte identical to source. Returns [(rel_path, match), ...]."""
    db_dir = db_root / f"db-{db_num}"
    src_base = _get_canonical_src(db_dir)
    client_db_dir = client_root / f"db-{db_num}"
    results = []

    def compare(src: Path, dest: Path) -> bool:
        if not src.exists() or not dest.exists():
            return False
        return _file_sha256(src) == _file_sha256(dest)

    # Canonical path: source has DATABASE/, DOCUMENTATION/, QUERIES/ at root or app/
    if src_base is not None:
        for subdir, name in [("DATABASE", "DATABASE"), ("DOCUMENTATION", "DOCUMENTATION"), ("QUERIES", "QUERIES")]:
            src_dir = src_base / subdir
            dest_dir = client_db_dir / name
            if not src_dir.exists() or not dest_dir.exists():
                continue
            for f in dest_dir.iterdir():
                if f.is_file():
                    src = src_dir / f.name
                    if subdir == "DOCUMENTATION" and f.name != "README.md":
                        continue  # README-only in DOCUMENTATION
                    if src.exists():
                        ok = compare(src, f)
                        results.append((f"{name}/{f.name}", ok))
        # vercel.json — README.md only
        expected = '{"rewrites":[{"source":"/","destination":"/DOCUMENTATION/README.md"}]}'
        v_dest = client_db_dir / "vercel.json"
        if v_dest.exists():
            ok = v_dest.read_text(encoding="utf-8").strip() == expected
            results.append(("vercel.json", ok))
        return results

    # Legacy path: compare client files to their sources
    for subdir in ("DATABASE", "DOCUMENTATION", "QUERIES"):
        dest_dir = client_db_dir / subdir
        if not dest_dir.exists():
            continue
        for f in dest_dir.iterdir():
            if not f.is_file():
                continue
            src = None
            if subdir == "DATABASE":
                db_data = db_dir / "data"
                if db_data.exists() and (db_data / f.name).exists():
                    src = db_data / f.name
            elif subdir == "DOCUMENTATION":
                if (db_dir / "docs" / f.name).exists():
                    src = db_dir / "docs" / f.name
            elif subdir == "QUERIES":
                qsrc = db_dir / "queries"
                if qsrc.exists() and (qsrc / f.name).exists():
                    src = qsrc / f.name
            if src:
                results.append((f"{subdir}/{f.name}", compare(src, f)))
    # vercel.json — README-only config
    v_dest = client_db_dir / "vercel.json"
    expected = '{"rewrites":[{"source":"/","destination":"/DOCUMENTATION/README.md"}]}'
    if v_dest.exists():
        ok = v_dest.read_text(encoding="utf-8").strip() == expected
        results.append(("vercel.json", ok))
    return results


def _sync_from_canonical(src_base: Path, client_db_dir: Path, db_num: int, dry_run: bool) -> dict:
    """Sync from source/db-N/ (DATABASE/, DOCUMENTATION/, QUERIES/) to client/db/db-N/.
    Source mirrors client structure. Removes extraneous dbN-* folders (legacy web-deployable)."""
    result = {"db": f"db-{db_num}", "synced": [], "errors": []}

    # Prune extraneous dbN-* folders (legacy web-deployable) for strict alignment
    prefix = f"db{db_num}-"
    if client_db_dir.exists():
        for item in list(client_db_dir.iterdir()):
            if item.is_dir() and item.name.startswith(prefix):
                if dry_run:
                    result["synced"].append(f"Would remove extraneous: {item.name}/")
                else:
                    try:
                        shutil.rmtree(item)
                        result["synced"].append(f"Removed extraneous: {item.name}/")
                    except Exception as e:
                        result["errors"].append(f"Remove {item.name}: {e}")

    def copy_dir(src_dir: Path, dest_dir: Path, name: str, remove_extras: bool = False) -> None:
        if not src_dir.exists():
            return
        src_files = {f.name for f in src_dir.iterdir() if f.is_file()}
        if dry_run:
            result["synced"].append(f"Would copy {name}/ ({len(src_files)} files)")
            return
        dest_dir.mkdir(parents=True, exist_ok=True)
        if remove_extras and dest_dir.exists():
            for f in list(dest_dir.iterdir()):
                if f.is_file() and f.name not in src_files:
                    f.unlink()
                    result["synced"].append(f"Removed obsolete: {name}/{f.name}")
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

    copy_dir(src_base / "DATABASE", client_db_dir / "DATABASE", "DATABASE", remove_extras=True)
    # DOCUMENTATION — README.md only (no HTML)
    copy_dir(src_base / "DOCUMENTATION", client_db_dir / "DOCUMENTATION", "DOCUMENTATION")
    if not dry_run:
        doc_dest = client_db_dir / "DOCUMENTATION"
        for f in list(doc_dest.iterdir()):
            if f.is_file() and f.name != "README.md":
                f.unlink()
                result["synced"].append(f"Removed DOCUMENTATION/{f.name}")
    copy_dir(src_base / "QUERIES", client_db_dir / "QUERIES", "QUERIES")

    # vercel.json — points to README.md only
    if not dry_run:
        vercel_content = '{"rewrites":[{"source":"/","destination":"/DOCUMENTATION/README.md"}]}'
        (client_db_dir / "vercel.json").write_text(vercel_content, encoding="utf-8")
        result["synced"].append("vercel.json")

    return result


def sync_database(db_num: int, db_root: Path, client_root: Path, dry_run: bool = False) -> dict:
    """Sync one database to client. Source mirrors client: DATABASE/, DOCUMENTATION/, QUERIES/.
    Uses canonical structure at root or app/ when present; else data/, docs/, queries/ (single source)."""
    db_dir = db_root / f"db-{db_num}"
    src_base = _get_canonical_src(db_dir)
    client_db_dir = client_root / f"db-{db_num}"

    result = {"db": f"db-{db_num}", "synced": [], "errors": []}

    if not db_dir.exists():
        result["errors"].append(f"db dir not found: {db_dir}")
        return result

    # When canonical structure exists (root or app/), copy directly to client
    if src_base is not None:
        return _sync_from_canonical(src_base, client_db_dir, db_num, dry_run)

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

    # 1. DATABASE/ - from data/ only (single source of truth)
    db_data = db_dir / "data"
    db_dest = client_db_dir / "DATABASE"
    all_sql = {}
    if db_data.exists():
        for f in db_data.iterdir():
            if f.is_file() and f.suffix.lower() == ".sql":
                all_sql[f.name] = f

    # Filter: PostgreSQL-only SQL. Output: schema.sql, primary data (data_large >= 1GB or data.sql)
    collected_sql = {}  # dest_name -> src_path

    def add_schema(dest: str, pg_src: str | None, base_src: str) -> None:
        src = (pg_src if pg_src and pg_src in all_sql else None) or (base_src if base_src in all_sql else None)
        if src:
            collected_sql[dest] = all_sql[src]

    add_schema("schema.sql", "schema.sql", "schema.sql")
    add_schema("schema_extensions.sql", "schema_extensions.sql", "schema_extensions.sql")
    add_schema("insurance_schema.sql", "insurance_schema.sql", "insurance_schema.sql")
    add_schema("nexrad_satellite_schema.sql", "nexrad_satellite_schema.sql", "nexrad_satellite_schema.sql")

    # Only primary data file: prefer data_large >= 1GB, else data.sql
    primary = get_primary_data_file(all_sql)
    if primary:
        dest_name, src_path = primary
        collected_sql[dest_name] = src_path

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

    # 2. DOCUMENTATION/ — README.md only (from docs/ or generate)
    doc_dest = client_db_dir / "DOCUMENTATION"
    readme_src = db_dir / "docs" / "README.md"
    if readme_src.exists():
        copy_file(readme_src, doc_dest / "README.md", "DOCUMENTATION/README.md")
    if not dry_run and doc_dest.exists():
        for f in list(doc_dest.iterdir()):
            if f.is_file() and f.name != "README.md":
                f.unlink()
    if not dry_run and doc_dest.exists() and any(doc_dest.iterdir()):
        result["synced"].append("DOCUMENTATION/")

    # 3. QUERIES/ - from queries/ only (single source of truth)
    queries_src = db_dir / "queries"
    qdest = client_db_dir / "QUERIES"
    if queries_src.exists():
        for fname in ("queries.md", "queries.json"):
            src = queries_src / fname
            if src.exists():
                copy_file(src, qdest / fname, f"QUERIES/{fname}")
        if not dry_run and qdest.exists() and any(qdest.iterdir()):
            if "QUERIES/" not in " ".join(result["synced"]):
                result["synced"].append("QUERIES/")

    # 4. Legacy dbN-*/data - sync same SQL from data/ (single source of truth)
    if collected_sql:
        prefix = f"db{db_num}-"
        client_items = list(client_db_dir.iterdir()) if client_db_dir.exists() else []
        for client_item in client_items:
            if client_item.is_dir() and client_item.name.startswith(prefix):
                legacy_data_dest = client_item / "data"
                if legacy_data_dest.exists() or not dry_run:
                    if dry_run:
                        result["synced"].append(f"Would sync {client_item.name}/data/ ({len(collected_sql)} files)")
                    else:
                        legacy_data_dest.mkdir(parents=True, exist_ok=True)
                        for f in list(legacy_data_dest.iterdir()):
                            if f.is_file() and f.suffix.lower() == ".sql" and f.name not in collected_sql:
                                f.unlink()
                                result["synced"].append(f"Removed obsolete: {client_item.name}/data/{f.name}")
                        for name, src_path in collected_sql.items():
                            shutil.copy2(src_path, legacy_data_dest / name)
                        result["synced"].append(f"{client_item.name}/data/ ({len(collected_sql)} files)")
                break  # only sync first matching legacy folder

    # 5. vercel.json — README.md only
    if not dry_run:
        (client_db_dir / "vercel.json").write_text(
            '{"rewrites":[{"source":"/","destination":"/DOCUMENTATION/README.md"}]}',
            encoding="utf-8",
        )
        result["synced"].append("vercel.json")

    return result


def main():
    parser = argparse.ArgumentParser(description="Resync db deliverables to client/db (DATABASE/DOCUMENTATION/QUERIES)")
    parser.add_argument("--dbs", type=int, nargs="*", default=list(range(1, 17)),
                        help="Database numbers to sync (default: 1-16)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied")
    parser.add_argument("--verify", action="store_true",
                        help="After sync, verify all files are byte-for-byte identical (SHA-256)")
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

    # Bit-for-bit verification (skipped in dry-run)
    if args.verify and not args.dry_run:
        print("\nVerifying byte-for-byte (SHA-256)...")
        any_mismatch = False
        for db_num in sorted(args.dbs):
            verified = _verify_synced(db_num, db_root, client_root)
            mismatches = [rel for rel, ok in verified if not ok]
            if mismatches:
                any_mismatch = True
                print(f"  db-{db_num}: MISMATCH - {mismatches}")
            else:
                print(f"  db-{db_num}: OK ({len(verified)} files)")
        if any_mismatch:
            print("\nERROR: Byte-for-byte verification failed. Source and client differ.")
            sys.exit(1)
        print("All files byte-for-byte identical (source = client).")


if __name__ == "__main__":
    main()
