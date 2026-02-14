#!/usr/bin/env python3
"""
Convert our schema + queries to BIRD-CRITIC evaluable format.
Output: user_issue (NL), sql, schema per task.
Use for generating custom BIRD-CRITIC-style tasks from our DBs.
"""

import json
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
BIRD_EXPORT_DIR = root_dir / "bird_export"


def load_schema(db_dir: Path) -> str:
    """Load schema SQL."""
    for name in ("schema.sql", "schema_postgresql.sql"):
        p = db_dir / "data" / name
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def get_user_issue(q: dict) -> str:
    """Extract user issue / natural language from query metadata."""
    return (
        q.get("question")
        or q.get("use_case")
        or (q.get("description") or "").split(".")[0][:500]
        or q.get("title", "Execute this SQL query")
    )


def format_db(db_num: int) -> list:
    """Convert one db-N to BIRD-CRITIC format. Returns list of tasks."""
    db_dir = root_dir / "source" / f"db-{db_num}"
    try:
        from db_paths import get_queries_dir
        queries_dir = get_queries_dir(db_dir)
    except ImportError:
        queries_dir = db_dir / "app" / "QUERIES" if (db_dir / "app" / "QUERIES").exists() else db_dir / "queries"
    db_id = f"db-{db_num}"
    qj = queries_dir / "queries.json"
    if not qj.exists():
        return []
    data = json.loads(qj.read_text(encoding="utf-8"))
    schema = load_schema(db_dir)
    out = []
    for q in data.get("queries", []):
        sql = q.get("sql", "").strip()
        if not sql:
            continue
        out.append({
            "db_id": db_id,
            "user_issue": get_user_issue(q),
            "sql": sql,
            "schema": schema,
            "query_number": q.get("number"),
            "title": q.get("title"),
        })
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all 1-16")
    ap.add_argument("--all", "-a", action="store_true")
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

    BIRD_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    all_tasks = []

    for n in db_nums:
        tasks = format_db(n)
        if not tasks:
            print(f"  db-{n}: no queries", file=sys.stderr)
            continue
        out_path = BIRD_EXPORT_DIR / f"db-{n}_critic.json"
        payload = {"db_id": f"db-{n}", "tasks": tasks, "count": len(tasks)}
        out_path.write_text(json.dumps(payload, indent=2, default=str))
        print(f"  db-{n}: {len(tasks)} tasks -> {out_path.name}")
        all_tasks.extend(tasks)

    if len(db_nums) > 1 and all_tasks:
        single = BIRD_EXPORT_DIR / "all_critic.json"
        single.write_text(json.dumps({"tasks": all_tasks, "count": len(all_tasks)}, indent=2, default=str))
        print(f"  all: {len(all_tasks)} tasks -> {single.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
