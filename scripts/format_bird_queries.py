#!/usr/bin/env python3
"""
Ensure queries.md / queries.json have BIRD-required fields: question (NL), sql.
Backfills question from use_case or description if missing.
"""

import json
import re
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent


def backfill_question(q: dict) -> str:
    """Derive question from use_case or description."""
    return (
        q.get("use_case")
        or (q.get("description") or "").split(".")[0][:500]
        or q.get("title", "")
    )


def process_queries_json(path: Path) -> bool:
    """Add question field if missing. Returns True if changed."""
    data = json.loads(path.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    changed = False
    for q in queries:
        if not q.get("question"):
            q["question"] = backfill_question(q)
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2, default=str))
    return changed


def process_db(db_num: int) -> bool:
    """Process one db-N. Returns True if any file changed."""
    try:
        from db_paths import get_queries_dir
        qj = get_queries_dir(root_dir / "source" / f"db-{db_num}") / "queries.json"
    except ImportError:
        qj = root_dir / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
        if not qj.exists():
            qj = root_dir / "source" / f"db-{db_num}" / "queries" / "queries.json"
    if not qj.exists():
        return False
    return process_queries_json(qj)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all 1-16")
    ap.add_argument("--all", "-a", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Report only, don't write")
    args = ap.parse_args()

    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = []
        for a in args.dbs:
            try:
                db_nums.append(int(str(a).replace("db-", "")))
            except ValueError:
                pass
        db_nums = sorted(set(db_nums))

    for n in db_nums:
        try:
            from db_paths import get_queries_dir
            qj = get_queries_dir(root_dir / "source" / f"db-{n}") / "queries.json"
        except ImportError:
            qj = root_dir / "source" / f"db-{n}" / "app" / "QUERIES" / "queries.json"
            if not qj.exists():
                qj = root_dir / "source" / f"db-{n}" / "queries" / "queries.json"
        if not qj.exists():
            continue
        if args.dry_run:
            data = json.loads(qj.read_text(encoding="utf-8"))
            missing = sum(1 for q in data.get("queries", []) if not q.get("question"))
            if missing:
                print(f"  db-{n}: {missing} queries missing question")
            continue
        if process_queries_json(qj):
            print(f"  db-{n}: backfilled question in queries.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
