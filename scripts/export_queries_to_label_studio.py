#!/usr/bin/env python3
"""
Export queries.json to Label Studio import format.

Converts template/queries.json or source/db-N/app/QUERIES/queries.json
to JSON tasks for Label Studio (https://labelstud.io/guide/quick_start).

Usage:
    pip install label-studio
    label-studio start   # http://localhost:8080
    python3 scripts/export_queries_to_label_studio.py template > label_studio_tasks.json
    # In Label Studio: Create project → Labeling Setup → paste template/label_studio_config.xml
    # Data Import → Upload label_studio_tasks.json

    python3 scripts/export_queries_to_label_studio.py db-1  # export db-1
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATE = ROOT / "template"
SOURCE = ROOT / "source"


def _get_queries(path: Path) -> list[dict]:
    """Extract query objects from queries.json (API-response or template array)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict) and "question_id" in x]
    queries = data.get("queries", data.get("data", {}).get("queries", []))
    return queries or []


def to_label_studio_tasks(queries: list[dict]) -> list[dict]:
    """Convert query objects to Label Studio task format."""
    tasks = []
    for q in queries:
        sql = q.get("SQL", q.get("sql", ""))
        tasks.append({
            "data": {
                "question_id": q.get("question_id"),
                "question": q.get("question", ""),
                "sql": sql,
                "evidence": q.get("evidence", ""),
                "difficulty": q.get("difficulty", "moderate"),
                "query_category": q.get("query_category", ""),
                "tables_used": ", ".join(q.get("tables_used", [])),
                "expected_output": q.get("expected_output", ""),
            }
        })
    return tasks


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: export_queries_to_label_studio.py <template|db-N>", file=sys.stderr)
        return 1

    arg = sys.argv[1].lower()
    if arg == "template":
        qj = TEMPLATE / "queries.json"
    else:
        db_num = arg.replace("db-", "")
        try:
            n = int(db_num)
        except ValueError:
            print(f"Invalid: {arg}", file=sys.stderr)
            return 1
        qd = SOURCE / f"db-{n}" / "app" / "QUERIES"
        if not qd.exists():
            qd = SOURCE / f"db-{n}" / "QUERIES"
        qj = qd / "queries.json"

    if not qj.exists():
        print(f"Not found: {qj}", file=sys.stderr)
        return 1

    queries = _get_queries(qj)
    tasks = to_label_studio_tasks(queries)
    print(json.dumps(tasks, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
