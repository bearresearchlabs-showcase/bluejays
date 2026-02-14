#!/usr/bin/env python3
"""
Shared execution tester (Phase 3).
Uses source/db-N via db_paths. Reads from queries.json.
Usage: python3 execution_tester.py <db_num>
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List

scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from timestamp_utils import get_est_timestamp
from db_paths import get_queries_dir

try:
    import psycopg2
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False


def _load_queries_from_json(queries_dir: Path) -> List[Dict]:
    qj = queries_dir / "queries.json"
    if not qj.exists():
        return []
    data = json.loads(qj.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    return [
        {"number": q.get("number") or q.get("question_id", 0), "sql": q.get("sql") or q.get("SQL", "")}
        for q in queries
    ]


def main():
    root = scripts_dir.parent
    if len(sys.argv) < 2:
        print("Usage: execution_tester.py <db_num>")
        sys.exit(1)
    try:
        db_num = int(sys.argv[1].replace("db-", ""))
    except ValueError:
        print("Invalid db number")
        sys.exit(1)

    db_dir = root / "source" / f"db-{db_num}"
    queries_dir = get_queries_dir(db_dir)
    results_file = db_dir / "results" / "query_test_results_postgres.json"

    queries = _load_queries_from_json(queries_dir)
    if not queries:
        print(f"Error: No queries found")
        sys.exit(1)

    if not PG_AVAILABLE:
        print("psycopg2 not available. Skipping execution testing.")
        sys.exit(0)

    try:
        conn = psycopg2.connect(
            host=os.environ.get("PG_HOST", "localhost"),
            port=int(os.environ.get("PG_PORT", 5432)),
            database=os.environ.get("PG_DATABASE", f"db{db_num}"),
            user=os.environ.get("PG_USER", "postgres"),
            password=os.environ.get("PG_PASSWORD", ""),
        )
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        results = {"available": False, "queries": [], "error": str(e)}
        results_file.parent.mkdir(parents=True, exist_ok=True)
        results_file.write_text(json.dumps({"postgresql": results, "test_date": get_est_timestamp()}, indent=2))
        sys.exit(0)

    results = {"available": True, "queries": []}
    for q in queries:
        try:
            cur = conn.cursor()
            cur.execute(f"{q['sql']} LIMIT 10")
            rows = cur.fetchall()
            cur.close()
            results["queries"].append({"query_number": q["number"], "success": True, "row_count": len(rows)})
        except Exception as e:
            results["queries"].append({"query_number": q["number"], "success": False, "error": str(e)[:200]})
    conn.close()

    output = {"postgresql": results, "test_date": get_est_timestamp()}
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(output, indent=2))
    print(f"Results saved to {results_file}")


if __name__ == "__main__":
    main()
