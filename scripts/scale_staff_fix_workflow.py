#!/usr/bin/env python3
"""
Replicate Scale AI staff task-fixing workflow.

Scale methodology (from scale.com/docs/pro-or-tasks-tab):
1. Filter tasks by Task Status (Completed, In Progress, Queued, Error, Canceled, Redo)
2. Filter by Audit Status (Ready to Audit, Accepted, Fixed, Rejected)
3. Open task → Audit: Accept | Fix | Reject
   - Accept: quality standards met
   - Fix: make immediate correction, update callback response
   - Reject: quality standards not met

This script runs the workflow via API against the annotator app.
Usage: python scripts/scale_staff_fix_workflow.py [--port 8766] [--source db-1]
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent


def _get(base_url: str, path: str) -> tuple[int, bytes]:
    req = urllib.request.Request(f"{base_url}{path}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b"{}"
    except OSError as e:
        print(f"Connection error: {e}")
        return -1, b"{}"


def _post_json(base_url: str, path: str, data: dict) -> tuple[int, dict]:
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8") if e.fp else "{}"
        try:
            return e.code, json.loads(resp_body) if resp_body.strip() else {}
        except json.JSONDecodeError:
            return e.code, {"error": resp_body[:200]}
    except OSError as e:
        print(f"Connection error: {e}")
        return -1, {"error": str(e)}


def run_workflow(base_url: str, source: str = "db-1", question_id: int = 1) -> bool:
    """Replicate Scale staff: load task, fix it, set audit_status=Fixed."""
    print(f"[1] GET /api/sources")
    status, body = _get(base_url, "/api/sources")
    if status != 200:
        print(f"  FAIL: {status}")
        return False
    data = json.loads(body)
    sources = data.get("sources", [])
    print(f"  OK: {len(sources)} sources")

    print(f"[2] GET /api/queries?source={source}")
    status, body = _get(base_url, f"/api/queries?source={source}")
    if status != 200:
        print(f"  FAIL: {status}")
        return False
    data = json.loads(body)
    queries = data.get("queries", [])
    if not queries:
        print("  FAIL: no queries")
        return False
    q = next((x for x in queries if x.get("question_id") == question_id), queries[0])
    qid = q.get("question_id", 1)
    print(f"  OK: {len(queries)} queries, editing question_id={qid}")

    # Scale Fix: make immediate correction
    original_evidence = q.get("evidence", "")
    fix_evidence = original_evidence + " [Scale staff fix: verified chain-of-thought.]"
    payload = {
        "source": source,
        "question_id": qid,
        "question": q.get("question", ""),
        "SQL": q.get("SQL", q.get("sql", "")),
        "evidence": fix_evidence,
        "difficulty": q.get("difficulty", "moderate"),
        "query_category": q.get("query_category", ""),
        "tables_used": q.get("tables_used", []),
        "expected_output": q.get("expected_output", ""),
        "task_status": "Completed",
        "audit_status": "Fixed",  # Scale: Fix = immediate correction
    }

    print(f"[3] POST /api/annotate (Scale Fix: audit_status=Fixed)")
    status, resp = _post_json(base_url, "/api/annotate", payload)
    if status != 200 or not resp.get("ok"):
        print(f"  FAIL: {status} {resp}")
        return False
    print("  OK: Saved")

    print(f"[4] Verify persistence")
    status2, body2 = _get(base_url, f"/api/queries?source={source}")
    if status2 != 200:
        print(f"  FAIL: {status2}")
        return False
    data2 = json.loads(body2)
    updated = next((x for x in data2["queries"] if x.get("question_id") == qid), None)
    if not updated:
        print("  FAIL: query not found")
        return False
    if updated.get("audit_status") != "Fixed":
        print(f"  FAIL: audit_status={updated.get('audit_status')}")
        return False
    if "[Scale staff fix" not in updated.get("evidence", ""):
        print("  FAIL: evidence not updated")
        return False
    print("  OK: audit_status=Fixed, evidence updated")

    return True


def main():
    ap = argparse.ArgumentParser(description="Scale AI staff task-fix workflow")
    ap.add_argument("--port", type=int, default=8766, help="Annotator port")
    ap.add_argument("--source", default="db-1", help="Source (db-1, template, ...)")
    ap.add_argument("--question-id", type=int, default=1, help="Question ID to fix")
    args = ap.parse_args()
    base_url = f"http://127.0.0.1:{args.port}"

    print("Scale AI staff workflow — replicate task fix")
    print("=" * 50)
    ok = run_workflow(base_url, args.source, args.question_id)
    print("=" * 50)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
