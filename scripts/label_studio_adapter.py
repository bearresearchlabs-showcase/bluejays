#!/usr/bin/env python3
"""
Label Studio Adapter: Integrate text-to-SQL query annotation with workbench flow.

Exports queries.json to Label Studio task format, optionally imports via API,
and supports multi-annotator session simulation for testing.

Flow:
  1. Export queries from template or source/db-N to Label Studio JSON
  2. Optional: Import into running Label Studio (LABEL_STUDIO_URL + API key)
  3. Multi-session test: Simulate concurrent annotators (get tasks, submit)

Usage:
  python scripts/label_studio_adapter.py export template [db-1]  # export to stdout
  python scripts/label_studio_adapter.py gates template          # validate export format (no LS required)
  python scripts/label_studio_adapter.py multi-session template   # simulate 3 annotators (LS must be running)
  db_check label-studio [template|db-1] [--export|--gates|--multi-session]

Docs: https://labelstud.io/guide/quick_start

Bypass API key (pre-set token):
  docker compose -f docker/docker-compose.label-studio.yml up -d
  export LABEL_STUDIO_USER_TOKEN=workbench-dev-token
  python scripts/label_studio_adapter.py multi-session template
"""
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

TEMPLATE = root_dir / "template"
SOURCE = root_dir / "source"
LABEL_STUDIO_CONFIG = TEMPLATE / "label_studio_config.xml"

try:
    from db_logger import log, record_telemetry
except ImportError:
    def log(*a, **k): pass
    def record_telemetry(*a, **k): pass


def _get_queries(path: Path) -> list[dict]:
    """Extract query objects from queries.json."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict) and "question_id" in x]
    queries = data.get("queries", data.get("data", {}).get("queries", []))
    return queries or []


def to_label_studio_tasks(queries: list[dict]) -> list[dict]:
    """Convert to Label Studio task format."""
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


def export_tasks(source: str) -> tuple[list[dict], str | None]:
    """Export tasks. Returns (tasks, error)."""
    if source.lower() == "template":
        qj = TEMPLATE / "queries.json"
    else:
        db_num = source.replace("db-", "")
        try:
            n = int(db_num)
        except ValueError:
            return [], f"Invalid source: {source}"
        qd = SOURCE / f"db-{n}" / "app" / "QUERIES"
        if not qd.exists():
            qd = SOURCE / f"db-{n}" / "QUERIES"
        qj = qd / "queries.json"

    if not qj.exists():
        return [], f"Not found: {qj}"

    queries = _get_queries(qj)
    tasks = to_label_studio_tasks(queries)
    return tasks, None


def run_gates(source: str) -> tuple[bool, str]:
    """Validate export format (no Label Studio required)."""
    tasks, err = export_tasks(source)
    if err:
        return False, err
    if not tasks:
        return False, "No tasks exported"
    # Validate each task has required Label Studio data keys
    required = ["question", "sql", "evidence"]
    for i, t in enumerate(tasks):
        data = t.get("data", {})
        for k in required:
            if k not in data:
                return False, f"Task {i+1} missing data.{k}"
    return True, f"OK ({len(tasks)} tasks)"


def _get_api_key() -> str:
    """API key: LABEL_STUDIO_API_KEY or LABEL_STUDIO_USER_TOKEN (bypass when LS started with --user-token)."""
    return os.getenv("LABEL_STUDIO_API_KEY") or os.getenv("LABEL_STUDIO_USER_TOKEN", "")


def _ls_request(method: str, path: str, json_data: dict | None = None) -> tuple[int, dict | None]:
    """Make Label Studio API request. Returns (status_code, response_json)."""
    try:
        import urllib.request
        url = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080").rstrip("/")
        api_key = _get_api_key()
        req = urllib.request.Request(
            f"{url}{path}",
            data=json.dumps(json_data).encode() if json_data else None,
            headers={
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode()) if r.length else {}
    except Exception as e:
        return -1, {"error": str(e)}


def run_multi_session_simulation(source: str, num_annotators: int = 3) -> tuple[bool, str]:
    """
    Simulate multiple annotator sessions: import tasks, then have N threads
    concurrently fetch tasks and submit annotations.
    Requires: Label Studio running, LABEL_STUDIO_API_KEY or LABEL_STUDIO_USER_TOKEN.
    Bypass: Start LS with --username/--password/--user-token (or env vars) to pre-create default user.
    See: https://labelstud.io/guide/signup
    """
    api_key = _get_api_key()
    if not api_key:
        return False, "LABEL_STUDIO_API_KEY or LABEL_STUDIO_USER_TOKEN not set (Account & Settings, or start LS with --user-token)"

    tasks, err = export_tasks(source)
    if err or not tasks:
        return False, err or "No tasks to import"

    config = LABEL_STUDIO_CONFIG.read_text(encoding="utf-8") if LABEL_STUDIO_CONFIG.exists() else ""

    try:
        # Create project via API
        status, resp = _ls_request("POST", "/api/projects", {"title": f"db-workbench-{source}-test", "label_config": config})
        if status not in (200, 201) or "id" not in resp:
            return False, f"Create project failed: {resp.get('error', resp)}"
        project_id = resp["id"]

        # Import tasks (bulk)
        status, _ = _ls_request("POST", f"/api/projects/{project_id}/import", tasks)
        if status not in (200, 201):
            return False, f"Import failed: status {status}"

        # Get task IDs (GET /api/tasks/?project=ID)
        status, tasks_resp = _ls_request("GET", f"/api/tasks/?project={project_id}")
        task_list = tasks_resp.get("tasks", tasks_resp.get("data", [])) if isinstance(tasks_resp, dict) else []
        task_ids = [x["id"] for x in task_list if isinstance(x, dict) and "id" in x][:10]

        results = {"completed": 0, "errors": []}

        def annotator_session(annotator_id: int) -> tuple[int, str | None]:
            """Simulate one annotator: submit annotations to tasks."""
            count = 0
            for tid in task_ids[:3]:  # 3 tasks per annotator
                status, _ = _ls_request("POST", f"/api/tasks/{tid}/annotations", {
                    "result": [{"value": {"text": ["verified"]}, "from_name": "sql", "to_name": "question", "type": "textarea"}],
                    "was_cancelled": False,
                })
                if status in (200, 201):
                    count += 1
            return count, None

        with ThreadPoolExecutor(max_workers=num_annotators) as ex:
            futures = [ex.submit(annotator_session, i) for i in range(num_annotators)]
            for f in as_completed(futures):
                cnt, err = f.result()
                results["completed"] += cnt

        # Cleanup
        _ls_request("DELETE", f"/api/projects/{project_id}")

        return True, f"OK ({results['completed']} annotations from {num_annotators} annotators)"
    except Exception as e:
        return False, str(e)[:300]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Label Studio adapter for workbench")
    ap.add_argument("command", choices=["export", "gates", "multi-session"], help="export | gates | multi-session")
    ap.add_argument("source", nargs="?", default="template", help="template or db-N")
    ap.add_argument("--annotators", type=int, default=3, help="Number of annotators for multi-session")
    args = ap.parse_args()

    if args.command == "export":
        tasks, err = export_tasks(args.source)
        if err:
            print(err, file=sys.stderr)
            return 1
        print(json.dumps(tasks, indent=2, ensure_ascii=False))
        return 0

    if args.command == "gates":
        ok, msg = run_gates(args.source)
        print(msg)
        return 0 if ok else 1

    if args.command == "multi-session":
        ok, msg = run_multi_session_simulation(args.source, args.annotators)
        print(msg)
        return 0 if ok else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
