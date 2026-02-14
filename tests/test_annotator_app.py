#!/usr/bin/env python3
"""
Rigorous tests for the annotator app — local submissions workflow.

Tests: load queries, edit/save, export CSV/JSON, filters, error handling.
Run: pytest tests/test_annotator_app.py -v
"""
import csv
import io
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
TEMPLATE_QUERIES = ROOT / "template" / "queries.json"
SOURCE_DB1 = ROOT / "source" / "db-1" / "app" / "QUERIES" / "queries.json"


def _find_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _wait_for_server(base_url: str, timeout: float = 10.0) -> bool:
    import urllib.request
    import urllib.error
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        try:
            with urllib.request.urlopen(f"{base_url}/", timeout=2) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.2)
    return False


def _get(base_url: str, path: str) -> tuple[int, bytes]:
    import urllib.error
    import urllib.request
    req = urllib.request.Request(f"{base_url}{path}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b"{}"


def _post_json(base_url: str, path: str, data: dict) -> tuple[int, dict]:
    import urllib.error
    import urllib.request
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


@pytest.fixture(scope="module")
def annotator_server():
    """Start annotator app in background, yield base URL, then stop."""
    port = _find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS / "annotator_app.py"), "--port", str(port), "--no-auth"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not _wait_for_server(base_url):
            pytest.skip("Annotator server did not start in time")
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


# --- API tests ---


class TestAnnotatorSources:
    """Test dynamic database discovery."""

    def test_get_sources(self, annotator_server):
        status, body = _get(annotator_server, "/api/sources")
        assert status == 200
        data = json.loads(body)
        assert "sources" in data
        sources = data["sources"]
        assert "template" in sources
        assert "db-1" in sources
        assert "db-16" in sources
        assert sources[0] == "template"
        assert "db-1" in sources and "db-16" in sources


class TestAnnotatorLoad:
    """Test loading queries from various sources."""

    def test_get_queries_db1(self, annotator_server):
        status, body = _get(annotator_server, "/api/queries?source=db-1")
        assert status == 200
        data = json.loads(body)
        assert "queries" in data
        queries = data["queries"]
        assert len(queries) >= 1
        q = queries[0]
        assert "question_id" in q
        assert "question" in q
        assert "SQL" in q or "sql" in q

    def test_get_queries_template(self, annotator_server):
        status, body = _get(annotator_server, "/api/queries?source=template")
        assert status == 200
        data = json.loads(body)
        assert "queries" in data
        assert len(data["queries"]) >= 1

    def test_get_queries_missing_source(self, annotator_server):
        status, body = _get(annotator_server, "/api/queries")
        assert status == 404
        data = json.loads(body)
        assert "error" in data

    def test_get_queries_invalid_source(self, annotator_server):
        status, body = _get(annotator_server, "/api/queries?source=db-999")
        assert status == 404
        data = json.loads(body)
        assert "error" in data


class TestAnnotatorExport:
    """Test export CSV and JSON."""

    def test_export_csv(self, annotator_server):
        status, body = _get(annotator_server, "/api/export?source=db-1&format=csv")
        assert status == 200
        text = body.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        assert len(rows) >= 1
        cols = set(rows[0].keys())
        required = {"question_id", "db_id", "question", "SQL", "task_status", "audit_status"}
        assert required.issubset(cols)

    def test_export_json(self, annotator_server):
        status, body = _get(annotator_server, "/api/export?source=db-1&format=json")
        assert status == 200
        data = json.loads(body)
        assert "queries" in data
        assert len(data["queries"]) >= 1

    def test_export_missing_source(self, annotator_server):
        status, _ = _get(annotator_server, "/api/export?format=csv")
        assert status == 404

    def test_export_invalid_source(self, annotator_server):
        status, body = _get(annotator_server, "/api/export?source=db-999&format=csv")
        assert status == 404

    def test_export_md(self, annotator_server):
        status, body = _get(annotator_server, "/api/export?source=db-1&format=md")
        assert status == 200
        text = body.decode("utf-8")
        assert "## Queries" in text
        assert "### Query 1" in text
        assert "```json" in text
        assert "question_id" in text or "SQL" in text


class TestAnnotatorSave:
    """Test saving annotations (POST /api/annotate)."""

    @pytest.fixture(autouse=True)
    def backup_restore_template(self):
        if not TEMPLATE_QUERIES.exists():
            pytest.skip("template/queries.json required")
        backup = TEMPLATE_QUERIES.with_suffix(".json.bak")
        shutil.copy2(TEMPLATE_QUERIES, backup)
        try:
            yield
        finally:
            shutil.move(str(backup), str(TEMPLATE_QUERIES))

    def test_annotate_save_and_persist(self, annotator_server):
        # Load template to get first query
        status, body = _get(annotator_server, "/api/queries?source=template")
        assert status == 200
        data = json.loads(body)
        queries = data["queries"]
        if not queries:
            pytest.skip("template has no queries")
        q = queries[0]
        qid = q.get("question_id")
        assert qid is not None

        payload = {
            "source": "template",
            "question_id": qid,
            "question": q.get("question", "") + " [test edit]",
            "SQL": q.get("SQL", q.get("sql", "")),
            "evidence": q.get("evidence", ""),
            "difficulty": "moderate",
            "query_category": "aggregation",
            "tables_used": ["patients", "diagnoses"],
            "expected_output": "[[7.3]]",
            "task_status": "Completed",
            "audit_status": "Accepted",
        }

        status, resp = _post_json(annotator_server, "/api/annotate", payload)
        assert status == 200
        assert resp.get("ok") is True

        # Reload and verify persistence
        status2, body2 = _get(annotator_server, "/api/queries?source=template")
        assert status2 == 200
        data2 = json.loads(body2)
        updated = next((x for x in data2["queries"] if x.get("question_id") == qid), None)
        assert updated is not None
        assert "[test edit]" in updated.get("question", "")
        assert updated.get("task_status") == "Completed"
        assert updated.get("audit_status") == "Accepted"

    def test_annotate_missing_source(self, annotator_server):
        status, resp = _post_json(
            annotator_server,
            "/api/annotate",
            {"question_id": 1, "question": "x", "SQL": "SELECT 1"},
        )
        assert status == 400
        assert "error" in resp

    def test_annotate_missing_question_id(self, annotator_server):
        status, resp = _post_json(
            annotator_server,
            "/api/annotate",
            {"source": "template", "question": "x", "SQL": "SELECT 1"},
        )
        assert status == 400
        assert "error" in resp


class TestScaleStaffWorkflow:
    """Replicate Scale AI staff task-fixing workflow (Accept/Fix/Reject)."""

    def test_scale_fix_workflow(self, annotator_server):
        # Scale methodology: load task, Fix (immediate correction), set audit_status=Fixed
        status, body = _get(annotator_server, "/api/queries?source=db-1")
        assert status == 200
        data = json.loads(body)
        queries = data["queries"]
        q = next((x for x in queries if x.get("question_id") == 1), queries[0])
        payload = {
            "source": "db-1",
            "question_id": q["question_id"],
            "question": q.get("question", ""),
            "SQL": q.get("SQL", q.get("sql", "")),
            "evidence": q.get("evidence", "") + " [Scale Fix]",
            "difficulty": q.get("difficulty", "moderate"),
            "query_category": q.get("query_category", ""),
            "tables_used": q.get("tables_used", []),
            "expected_output": q.get("expected_output", ""),
            "task_status": "Completed",
            "audit_status": "Fixed",
        }
        status2, resp = _post_json(annotator_server, "/api/annotate", payload)
        assert status2 == 200 and resp.get("ok") is True
        status3, body3 = _get(annotator_server, "/api/queries?source=db-1")
        assert status3 == 200
        updated = next((x for x in json.loads(body3)["queries"] if x.get("question_id") == q["question_id"]), None)
        assert updated and updated.get("audit_status") == "Fixed"


class TestAnnotatorPages:
    """Test HTML pages serve correctly."""

    def test_index_html(self, annotator_server):
        status, body = _get(annotator_server, "/")
        assert status == 200
        assert b"SQL Annotator" in body
        assert b"queries.json" in body

    def test_annotate_html(self, annotator_server):
        status, body = _get(annotator_server, "/annotate")
        assert status == 200
        assert b"Export CSV" in body
        assert b"Task Status" in body
        assert b"Audit Status" in body


class TestExportScript:
    """Test export_annotations.py CLI (db_check export)."""

    def test_export_cli_db1(self):
        out = ROOT / "tmp_test_export.csv"
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "db_check.py"), "export", "db-1", "-o", str(out)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0
            assert out.exists()
            with open(out, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            assert len(rows) >= 1
            assert "task_status" in rows[0]
        finally:
            if out.exists():
                out.unlink()

    def test_export_cli_template(self):
        out = ROOT / "tmp_test_export_template.csv"
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "db_check.py"), "export", "template", "-o", str(out)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0
            assert out.exists()
        finally:
            if out.exists():
                out.unlink()
