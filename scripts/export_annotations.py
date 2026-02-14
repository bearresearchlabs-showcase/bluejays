#!/usr/bin/env python3
"""
Export annotations — /export command.

Master database: queries.json. Exports to Excel-compatible CSV (sheet structure)
and can populate queries.json from CSV.

Usage:
  # Export from source to CSV (Excel sheet structure)
  python scripts/export_annotations.py export db-1 [--output submissions_db1.csv]

  # Export from source to queries.json (populate/overwrite)
  python scripts/export_annotations.py populate db-1 [--from-csv file.csv]

  # db_check integration
  python scripts/db_check.py export db-1 [--output submissions.csv]

Excel sheet columns (Scale Tasks Tab style):
  question_id, db_id, question, SQL, evidence, difficulty, query_category,
  tables_used, expected_output, task_status, audit_status, created_at, updated_at
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
SOURCE = root_dir / "source"
TEMPLATE = root_dir / "template"


def _get_queries_json_path(source: str) -> Path | None:
    """Resolve queries.json path."""
    if source.lower() == "template":
        return TEMPLATE / "queries.json"
    db_num = source.replace("db-", "").strip()
    try:
        n = int(db_num)
    except ValueError:
        return None
    for base in ["app/QUERIES", "QUERIES"]:
        p = SOURCE / f"db-{n}" / base / "queries.json"
        if p.exists():
            return p
    p = root_dir / f"db-{n}" / "queries" / "queries.json"
    return p if p.exists() else None


def _load_queries(source: str) -> tuple[list[dict], str | None]:
    """Load queries from queries.json. Returns (queries, error)."""
    path = _get_queries_json_path(source)
    if not path or not path.exists():
        return [], f"Not found: {source}"
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        queries = [x for x in data if isinstance(x, dict) and "question_id" in x]
    else:
        queries = data.get("queries", data.get("data", {}).get("queries", []))
    return queries, None


def _ensure_task_fields(q: dict) -> dict:
    """Ensure Scale-style task_status and audit_status exist."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = dict(q)
    q.setdefault("task_status", "Completed")
    q.setdefault("audit_status", "Ready to Audit")
    q.setdefault("created_at", now)
    q.setdefault("updated_at", now)
    return q


EXCEL_COLUMNS = [
    "question_id", "db_id", "question", "SQL", "evidence", "difficulty",
    "query_category", "tables_used", "expected_output",
    "task_status", "audit_status", "created_at", "updated_at",
]


def _row_from_query(q: dict) -> dict:
    """Convert query dict to Excel row."""
    q = _ensure_task_fields(q)
    tables = q.get("tables_used", [])
    tables_str = ", ".join(tables) if isinstance(tables, list) else str(tables)
    return {
        "question_id": q.get("question_id", ""),
        "db_id": q.get("db_id", ""),
        "question": q.get("question", ""),
        "SQL": q.get("SQL", q.get("sql", "")),
        "evidence": q.get("evidence", ""),
        "difficulty": q.get("difficulty", ""),
        "query_category": q.get("query_category", ""),
        "tables_used": tables_str,
        "expected_output": q.get("expected_output", ""),
        "task_status": q.get("task_status", "Completed"),
        "audit_status": q.get("audit_status", "Ready to Audit"),
        "created_at": q.get("created_at", ""),
        "updated_at": q.get("updated_at", ""),
    }


def export_to_csv(source: str, output_path: Path) -> int:
    """Export queries to CSV (Excel sheet structure)."""
    queries, err = _load_queries(source)
    if err:
        print(err, file=sys.stderr)
        return 1
    rows = [_row_from_query(q) for q in queries]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EXCEL_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"Exported {len(rows)} rows to {output_path}")
    return 0


def populate_from_csv(csv_path: Path, target_source: str) -> int:
    """Populate queries.json from CSV."""
    path = _get_queries_json_path(target_source)
    if not path or not path.exists():
        print(f"Target not found: {target_source}", file=sys.stderr)
        return 1
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        queries = data
        idx_map = {q.get("question_id"): i for i, q in enumerate(queries) if isinstance(q, dict) and "question_id" in q}
    else:
        queries = list(data.get("queries", data.get("data", {}).get("queries", [])))
        idx_map = {q.get("question_id"): i for i, q in enumerate(queries) if isinstance(q, dict) and "question_id" in q}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for row in rows:
        qid = row.get("question_id")
        if not qid:
            continue
        try:
            qid = int(qid)
        except (ValueError, TypeError):
            continue
        tables = row.get("tables_used", "")
        tables_list = [s.strip() for s in str(tables).split(",") if s.strip()]
        q = {
            "question_id": qid,
            "db_id": row.get("db_id", target_source),
            "question": row.get("question", ""),
            "SQL": row.get("SQL", ""),
            "sql": row.get("SQL", ""),
            "evidence": row.get("evidence", ""),
            "difficulty": row.get("difficulty", "moderate"),
            "query_category": row.get("query_category", ""),
            "tables_used": tables_list,
            "expected_output": row.get("expected_output", ""),
            "task_status": row.get("task_status", "Completed"),
            "audit_status": row.get("audit_status", "Ready to Audit"),
            "created_at": row.get("created_at", now),
            "updated_at": now,
        }
        if qid in idx_map:
            queries[idx_map[qid]] = {**queries[idx_map[qid]], **q}
        else:
            queries.append(q)
    if isinstance(data, list):
        data = queries
    else:
        if "queries" in data:
            data["queries"] = queries
        elif "data" in data and "queries" in data["data"]:
            data["data"]["queries"] = queries
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Populated {path} from {csv_path} ({len(rows)} rows)")
    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Export annotations (Scale Tasks Tab style)")
    ap.add_argument("cmd", choices=["export", "populate"], help="export to CSV | populate from CSV")
    ap.add_argument("source", help="db-1, db-2, ... or template")
    ap.add_argument("--output", "-o", type=Path, help="Output CSV path for export")
    ap.add_argument("--from-csv", type=Path, help="Input CSV for populate")
    args = ap.parse_args()

    if args.cmd == "export":
        out = args.output or Path(f"submissions_{args.source.replace('-', '_')}.csv")
        return export_to_csv(args.source, out)
    if args.cmd == "populate":
        csv_path = args.from_csv
        if not csv_path or not csv_path.exists():
            print("--from-csv required and must exist", file=sys.stderr)
            return 1
        return populate_from_csv(csv_path, args.source)
    return 1


if __name__ == "__main__":
    sys.exit(main())
