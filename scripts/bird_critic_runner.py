#!/usr/bin/env python3
"""
Run BIRD-CRITIC tasks against our db-{N} PostgreSQL instances.
Loads tasks from HuggingFace (birdsql/bird-critic-1.0-postgresql) or local JSON.
Records success rate per task.
"""

import json
import os
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

# Gate on env
from env_validator import ensure_env, load_env
load_env()
if not ensure_env("db"):
    sys.exit(1)


def get_db_port(db_num: int) -> int:
    start = int(os.getenv("DB_PORTS_START", "5436"))
    return start + db_num - 1


def run_sql_on_db(host: str, port: int, user: str, password: str, database: str, sql: str) -> tuple[bool, str]:
    """Execute SQL on PostgreSQL. Returns (success, error_message)."""
    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 not installed"
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=database,
            connect_timeout=10,
        )
        cur = conn.cursor()
        cur.execute(sql)
        cur.fetchall()
        cur.close()
        conn.close()
        return True, ""
    except Exception as e:
        return False, str(e)[:300]


def load_tasks_from_hf() -> list:
    """Load BIRD-CRITIC PostgreSQL tasks from HuggingFace."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("pip install datasets", file=sys.stderr)
        return []
    ds = load_dataset("birdsql/bird-critic-1.0-postgresql", split="train", trust_remote_code=True)
    tasks = []
    for row in ds:
        # Adapt to HF schema - typically has question/issue, gold_sql or buggy_sql, db_id, etc.
        task = {
            "db_id": row.get("db_id", ""),
            "user_issue": row.get("question") or row.get("user_issue") or row.get("issue", ""),
            "sql": row.get("gold_sql") or row.get("sql") or row.get("buggy_sql", ""),
            "schema": row.get("schema", ""),
        }
        if task["sql"]:
            tasks.append(task)
    return tasks


def load_tasks_from_local(path: Path) -> list:
    """Load tasks from local JSON (bird_critic_format output)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if "tasks" in data:
        return data["tasks"]
    return data.get("entries", data) if isinstance(data, dict) else []


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["hf", "local"], default="local")
    ap.add_argument("--local-path", type=Path, default=root_dir / "bird_export" / "all_critic.json")
    ap.add_argument("--db", type=int, default=1, help="db-N to run against (port from DB_PORTS_START)")
    ap.add_argument("--limit", type=int, default=0, help="Max tasks to run (0=all)")
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()

    if args.source == "hf":
        tasks = load_tasks_from_hf()
        print(f"Loaded {len(tasks)} tasks from HuggingFace")
    else:
        if not args.local_path.exists():
            print(f"Run bird_critic_format.py first to create {args.local_path}", file=sys.stderr)
            return 1
        tasks = load_tasks_from_local(args.local_path)
        print(f"Loaded {len(tasks)} tasks from {args.local_path}")

    if not tasks:
        print("No tasks to run")
        return 0

    if args.limit:
        tasks = tasks[: args.limit]

    host = os.getenv("PG_HOST", "localhost")
    port = get_db_port(args.db)
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "postgres")
    database = os.getenv("PG_DATABASE", f"db{args.db}")

    results = []
    for i, t in enumerate(tasks):
        sql = t.get("sql", "").strip()
        if not sql:
            results.append({"index": i, "success": False, "error": "no sql"})
            continue
        ok, err = run_sql_on_db(host, port, user, password, database, sql)
        results.append({"index": i, "success": ok, "error": err or None})
        status = "OK" if ok else "FAIL"
        print(f"  [{i+1}/{len(tasks)}] {status}" + (f" - {err[:80]}" if err else ""))

    passed = sum(1 for r in results if r["success"])
    total = len(results)
    rate = (passed / total * 100) if total else 0
    print(f"\nSuccess rate: {passed}/{total} ({rate:.1f}%)")

    out = args.output or (root_dir / "bird_export" / f"bird_critic_results_db{args.db}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "db_id": f"db-{args.db}",
        "total": total,
        "passed": passed,
        "success_rate": rate,
        "results": results,
    }, indent=2, default=str))
    print(f"Results saved to {out}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
