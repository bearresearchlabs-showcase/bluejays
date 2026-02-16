#!/usr/bin/env python3
"""
Export db-{N} queries to BIRD-bench compatible format.
Reads queries.json and schema.sql; maps use_case or description to BIRD question.
Outputs: bird_export/db-{N}_bird.json or bird_export/all_bird.json
"""

import json
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
try:
    from db_logger import log, record_telemetry
except ImportError:
    def log(*a, **k): pass
    def record_telemetry(*a, **k): pass
root_dir = scripts_dir.parent
BIRD_EXPORT_DIR = root_dir / "bird_export"


def get_question(q: dict) -> str:
    """Extract natural language question for BIRD from query metadata."""
    return (
        q.get("question")
        or q.get("use_case")
        or (q.get("description") or "")[:500]
        or q.get("title", "")
    )


def load_schema(db_dir: Path) -> str:
    """Load schema SQL (schema.sql or schema_postgresql.sql)."""
    try:
        from db_paths import get_data_dir
        data_dir = get_data_dir(db_dir)
    except ImportError:
        data_dir = db_dir / "data"
    for name in ("schema.sql", "schema_postgresql.sql"):
        p = data_dir / name
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def export_db(db_num: int) -> list:
    """Export one db-N to BIRD format. Returns list of BIRD entries."""
    db_dir = root_dir / "source" / f"db-{db_num}"
    db_id = f"db-{db_num}"
    try:
        from db_paths import get_queries_dir
        qj = get_queries_dir(db_dir) / "queries.json"
    except ImportError:
        qj = (db_dir / "app" / "QUERIES" / "queries.json") if (db_dir / "app" / "QUERIES").exists() else db_dir / "queries" / "queries.json"
        if not qj.exists():
            qj = db_dir / "QUERIES" / "queries.json"
    if not qj.exists():
        return []
    data = json.loads(qj.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    schema = load_schema(db_dir)
    out = []
    for q in queries:
        sql = q.get("sql", "").strip()
        if not sql:
            continue
        question = get_question(q)
        entry = {
            "question": question,
            "sql": sql,
            "db_id": db_id,
            "query_number": q.get("number"),
            "title": q.get("title"),
        }
        normal_query = q.get("normal_query", "").strip()
        if normal_query:
            entry["normal_query"] = normal_query
        evidence = q.get("evidence", "").strip()
        if evidence:
            entry["evidence"] = evidence
        out.append(entry)
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all 1-16")
    ap.add_argument("--all", "-a", action="store_true", help="Export all db-1..db-16")
    ap.add_argument("--single", action="store_true", help="Write single all_bird.json")
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

    BIRD_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    all_entries = []

    for n in db_nums:
        entries = export_db(n)
        if not entries:
            print(f"  db-{n}: no queries.json or no queries", file=sys.stderr)
            continue
        out_path = BIRD_EXPORT_DIR / f"db-{n}_bird.json"
        payload = {"db_id": f"db-{n}", "entries": entries, "count": len(entries)}
        out_path.write_text(json.dumps(payload, indent=2, default=str))
        print(f"  db-{n}: {len(entries)} entries -> {out_path.name}")
        all_entries.extend(entries)

    if args.single and all_entries:
        single_path = BIRD_EXPORT_DIR / "all_bird.json"
        single_path.write_text(json.dumps({"entries": all_entries, "count": len(all_entries)}, indent=2, default=str))
        print(f"  all: {len(all_entries)} entries -> {single_path.name}")

    record_telemetry("bird_export", "run", passed=len(all_entries), failed=0, extra={"db_count": len(db_nums)})
    log("bird_export", "main", status="ok", data={"total_entries": len(all_entries), "db_count": len(db_nums)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
