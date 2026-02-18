#!/usr/bin/env python3
"""
Rewrite queries.md to template format (bit-for-bit match with @template/queries.md).

Reads queries.json and (optionally) source/db-N/queries_header.yaml or .json,
builds queries.md using queries_md_template_formatter.

Header source: source/db-N/queries_header.yaml or queries_header.json (top level, NOT in app).
If present, header sections (Database Overview, Purpose, Use Case, Business Value,
Schema, Domain Knowledge, Query Difficulty Distribution) are ported from that file.
Otherwise falls back to schema snippet and inferred db_name.

Usage:
    python3 scripts/rewrite_queries_md_to_template.py [db-1] [db-5] | -a
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
sys.path.insert(0, str(Path(__file__).parent))

try:
    from db_paths import get_queries_dir
except ImportError:

    def get_queries_dir(db_dir: Path) -> Path:
        app = db_dir / "app"
        if app.exists() and (app / "QUERIES").exists():
            return app / "QUERIES"
        if (db_dir / "QUERIES").exists():
            return db_dir / "QUERIES"
        return db_dir / "queries"


def _load_schema_snippet(db_dir: Path, db_num: int) -> str:
    """Load schema.sql as schema snippet (fallback when no queries_header)."""
    for base in (db_dir / "app" / "DATABASE", db_dir / "data", db_dir / "deliverable" / "data"):
        if not base.exists():
            continue
        for name in ("schema.sql",):
            p = base / name
            if p.exists():
                txt = p.read_text(encoding="utf-8").strip()
                return txt[:2000] + "\n-- ..." if len(txt) > 2000 else txt
    return f"-- Schema for db-{db_num} (load from DATABASE/schema.sql)"


def _get_db_name(db_dir: Path, db_id: str) -> str:
    """Get database name from deliverable or default."""
    for d in (db_dir / "deliverable", db_dir / "app" / "DOCUMENTATION"):
        md = d / f"{db_id}.md"
        if md.exists():
            first = md.read_text(encoding="utf-8").split("\n")[0]
            if "Name:" in first:
                return first.split("Name:")[-1].strip()
            if " — " in first:
                return first.split(" — ", 1)[-1].strip()
    return f"Database {db_id}"


def rewrite_db(db_num: int) -> bool:
    """Rewrite one db's queries.md to template format."""
    db_id = f"db-{db_num}"
    db_dir = SOURCE / f"db-{db_num}"
    queries_dir = get_queries_dir(db_dir)
    qj = queries_dir / "queries.json"
    qm = queries_dir / "queries.md"

    if not qj.exists():
        print(f"  {db_id}: SKIP (no queries.json)")
        return False

    try:
        data = json.loads(qj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  {db_id}: SKIP (invalid JSON: {e})")
        return False

    queries = data.get("queries", [])
    if isinstance(data, list):
        queries = data
    if not queries:
        print(f"  {db_id}: SKIP (no queries)")
        return False

    from queries_md_template_formatter import format_queries_md_template
    from load_queries_header import load_queries_header, header_to_format_args

    # Build format args: prefer source/db-N/queries_header.yaml or .json (top level, NOT in app)
    header = load_queries_header(db_dir)
    if header:
        fmt_args = header_to_format_args(header)
        db_name = fmt_args.pop("db_name") or _get_db_name(db_dir, db_id)
        schema_sql = fmt_args.pop("schema_sql") or _load_schema_snippet(db_dir, db_num)
    else:
        db_name = _get_db_name(db_dir, db_id)
        schema_sql = _load_schema_snippet(db_dir, db_num)
        fmt_args = {}

    content = format_queries_md_template(
        queries,
        db_id=db_id,
        db_name=db_name,
        schema_sql=schema_sql,
        **{k: v for k, v in fmt_args.items() if v},
    )
    qm.write_text(content, encoding="utf-8")
    src = "queries_header" if header else "fallback"
    print(f"  {db_id}: OK ({len(queries)} queries, header from {src})")
    return True


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Rewrite queries.md to template format")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all")
    ap.add_argument("-a", "--all", action="store_true", help="Rewrite all db-1..db-16")
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
        db_nums = sorted(set(db_nums))

    print("Rewriting queries.md to template format (@template)...")
    ok = sum(1 for n in db_nums if rewrite_db(n))
    print(f"\nDone: {ok}/{len(db_nums)} databases")
    return 0 if ok == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
