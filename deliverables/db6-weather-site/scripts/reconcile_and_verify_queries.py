#!/usr/bin/env python3
"""
1. Check reconciliation code paths
2. Run resync to reconcile source -> client
3. Byte-for-byte comparison of queries.json and queries.md (source, client, zip)
4. Tabulate results
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
SOURCE_QUERIES = lambda n: BASE / f"db-{n}" / "queries"
CLIENT_QUERIES = lambda n: BASE / "client" / "db" / f"db-{n}" / "QUERIES"
ZIP_EXTRACT_DEFAULT = Path("/tmp/db_zip_extract/db")


def file_hash(p: Path) -> str | None:
    if not p.exists():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sql_hash_from_json(p: Path) -> str | None:
    """Hash of concatenated SQL strings only (ignores metadata)."""
    if not p.exists():
        return None
    try:
        d = json.load(open(p))
        sqls = [q.get("sql", "") for q in d.get("queries", [])]
        concat = "\n---\n".join(sqls)
        return hashlib.sha256(concat.encode("utf-8")).hexdigest()
    except Exception:
        return None


def run_resync(dry_run: bool = False) -> bool:
    cmd = [sys.executable, str(BASE / "scripts" / "resync_client_db.py")]
    if dry_run:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Reconcile source->client and verify byte-for-byte (incl. zip)")
    parser.add_argument("--zip-extract", type=Path, default=ZIP_EXTRACT_DEFAULT,
                        help="Path to extracted db.zip (e.g. /tmp/db_zip_extract/db)")
    parser.add_argument("--skip-resync", action="store_true", help="Skip resync, only compare")
    args = parser.parse_args()

    zip_base = args.zip_extract.resolve()
    include_zip = zip_base.exists()

    print("=" * 70)
    print("1. RECONCILIATION CODE CHECK")
    print("=" * 70)
    print("Source: db-N/queries/ -> Client: client/db/db-N/QUERIES/")
    print("Resync copies: queries.md, queries.json (shutil.copy2 = byte-preserving)")
    if include_zip:
        print(f"Zip included: {zip_base}")
    else:
        print(f"Zip excluded: {zip_base} not found (extract db.zip first)")
    print()

    if not args.skip_resync:
        print("=" * 70)
        print("2. RUNNING RESYNC (reconcile source -> client)")
        print("=" * 70)
        if not run_resync(dry_run=False):
            print("Resync FAILED")
            sys.exit(1)
        print()
    else:
        print("(Skipping resync)\n")

    print("=" * 70)
    print("3. BYTE-FOR-BYTE COMPARISON (source | client | zip)")
    print("=" * 70)

    rows = []
    for n in range(1, 17):
        src_q = SOURCE_QUERIES(n)
        cli_q = CLIENT_QUERIES(n)
        zip_q = zip_base / f"db-{n}" / "QUERIES" if include_zip else None

        qj_src = src_q / "queries.json"
        qj_cli = cli_q / "queries.json"
        qj_zip = (zip_q / "queries.json") if zip_q else None
        qm_src = src_q / "queries.md"
        qm_cli = cli_q / "queries.md"
        qm_zip = (zip_q / "queries.md") if zip_q else None

        qj_src_hash = file_hash(qj_src)
        qj_cli_hash = file_hash(qj_cli)
        qj_zip_hash = file_hash(qj_zip) if qj_zip else None
        qm_src_hash = file_hash(qm_src)
        qm_cli_hash = file_hash(qm_cli)
        qm_zip_hash = file_hash(qm_zip) if qm_zip else None

        if include_zip:
            qj_all = qj_src_hash == qj_cli_hash == qj_zip_hash if (qj_src_hash and qj_cli_hash and qj_zip_hash) else False
        else:
            qj_all = qj_src_hash == qj_cli_hash if (qj_src_hash and qj_cli_hash) else False

        if include_zip:
            qm_all = qm_src_hash == qm_cli_hash == qm_zip_hash if (qm_src_hash and qm_cli_hash and qm_zip_hash) else False
        else:
            qm_all = qm_src_hash == qm_cli_hash if (qm_src_hash and qm_cli_hash) else False

        sql_src_hash = sql_hash_from_json(qj_src)
        sql_cli_hash = sql_hash_from_json(qj_cli)
        sql_zip_hash = sql_hash_from_json(qj_zip) if qj_zip else None
        if include_zip:
            sql_all = sql_src_hash == sql_cli_hash == sql_zip_hash if (sql_src_hash and sql_cli_hash and sql_zip_hash) else False
        else:
            sql_all = sql_src_hash == sql_cli_hash if (sql_src_hash and sql_cli_hash) else False

        rows.append({
            "db": f"db-{n}",
            "queries.json": "✓" if qj_all else "✗",
            "queries.md": "✓" if qm_all else "✗",
            "SQL_content": "✓" if sql_all else "✗",
            "source_exists": qj_src.exists() and qm_src.exists(),
            "client_exists": qj_cli.exists() and qm_cli.exists(),
            "zip_exists": (qj_zip and qj_zip.exists() and qm_zip and qm_zip.exists()) if include_zip else False,
            "include_zip": include_zip,
        })

    # Tabulate
    print()
    if include_zip:
        print("| db     | queries.json | queries.md | SQL content | source | client | zip  |")
        print("|--------|--------------|------------|-------------|--------|--------|------|")
        for r in rows:
            src = "✓" if r["source_exists"] else "✗"
            cli = "✓" if r["client_exists"] else "✗"
            z = "✓" if r["zip_exists"] else "✗"
            print(f"| {r['db']:6} | {r['queries.json']:12} | {r['queries.md']:10} | {r['SQL_content']:11} | {src:6} | {cli:6} | {z:6} |")
    else:
        print("| db     | queries.json | queries.md | SQL content | source | client |")
        print("|--------|--------------|------------|-------------|--------|--------|")
        for r in rows:
            src = "✓" if r["source_exists"] else "✗"
            cli = "✓" if r["client_exists"] else "✗"
            print(f"| {r['db']:6} | {r['queries.json']:12} | {r['queries.md']:10} | {r['SQL_content']:11} | {src:6} | {cli:6} |")

    mismatches = [r["db"] for r in rows if r["queries.json"] == "✗" or r["queries.md"] == "✗"]
    if mismatches:
        print()
        print("MISMATCHES (byte-for-byte):", ", ".join(mismatches))
    else:
        print()
        if include_zip:
            print("All queries byte-for-byte identical (source = client = zip) after resync.")
        else:
            print("All queries byte-for-byte identical (source = client) after resync.")


if __name__ == "__main__":
    main()
