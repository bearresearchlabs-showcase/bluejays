#!/usr/bin/env python3
"""
Tests for Label Studio adapter: export format, gates, db_check integration, multi-session.
Gates tests run without Label Studio. Multi-session requires LABEL_STUDIO_URL + LABEL_STUDIO_API_KEY.
Run: pytest tests/test_label_studio.py -v
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
TEMPLATE = ROOT / "template"
SOURCE = ROOT / "source"


class TestLabelStudioAdapter:
    """Label Studio adapter must exist and be invocable."""

    def test_label_studio_adapter_exists(self):
        p = SCRIPTS / "label_studio_adapter.py"
        assert p.exists(), "label_studio_adapter.py must exist"

    def test_label_studio_config_exists(self):
        p = TEMPLATE / "label_studio_config.xml"
        assert p.exists(), "template/label_studio_config.xml must exist"


class TestLabelStudioGates:
    """Gates (export format validation) run without Label Studio."""

    @pytest.mark.skipif(
        not (TEMPLATE / "queries.json").exists(),
        reason="template/queries.json required",
    )
    def test_gates_template_pass(self):
        """Gates must pass for template source."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "label_studio_adapter.py"), "gates", "template"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"gates failed: {proc.stderr}"
        assert "OK" in proc.stdout
        assert "tasks" in proc.stdout.lower()

    def test_export_template_produces_valid_json(self):
        """Export must produce valid JSON array of tasks."""
        if not (TEMPLATE / "queries.json").exists():
            pytest.skip("template/queries.json required")
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "label_studio_adapter.py"), "export", "template"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"export failed: {proc.stderr}"
        data = json.loads(proc.stdout)
        assert isinstance(data, list)
        assert len(data) > 0
        for t in data:
            assert "data" in t
            d = t["data"]
            assert "question" in d
            assert "sql" in d
            assert "evidence" in d


class TestDbCheckLabelStudio:
    """db_check label-studio subcommand must work."""

    @pytest.mark.skipif(
        not (TEMPLATE / "queries.json").exists(),
        reason="template/queries.json required",
    )
    def test_db_check_label_studio_gates(self):
        """db_check label-studio template --gates must pass."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "db_check.py"), "label-studio", "template", "--gates"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"db_check label-studio failed: {proc.stderr}"
        assert "OK" in proc.stdout

    def test_db_check_label_studio_default_gates(self):
        """db_check label-studio with no mode defaults to gates."""
        if not (TEMPLATE / "queries.json").exists():
            pytest.skip("template/queries.json required")
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "db_check.py"), "label-studio", "template"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0
        assert "OK" in proc.stdout


class TestLabelStudioMultiSession:
    """Multi-session simulation: mocked (always runs) and live (requires Label Studio)."""

    @pytest.mark.skipif(
        not (TEMPLATE / "queries.json").exists(),
        reason="template/queries.json required",
    )
    def test_multi_session_mocked_concurrent_annotators(self):
        """Multi-session logic: N annotators run concurrently, each submits annotations (mocked API)."""
        sys.path.insert(0, str(SCRIPTS))
        from label_studio_adapter import run_multi_session_simulation

        call_log = []

        def mock_ls_request(method: str, path: str, json_data=None):
            call_log.append((method, path))
            del json_data  # unused
            if "POST" in method and "/api/projects" in path and "/import" not in path and "/annotations" not in path:
                return 201, {"id": 1}
            if "POST" in method and "/import" in path:
                return 200, {}
            if "GET" in method and "/tasks" in path:
                return 200, {"data": [{"id": 10}, {"id": 11}, {"id": 12}]}
            if "POST" in method and "/annotations" in path:
                return 201, {"id": 100}
            if "DELETE" in method:
                return 204, {}
            return 404, {"error": "not found"}

        with patch.dict(os.environ, {"LABEL_STUDIO_API_KEY": "test"}):
            with patch("label_studio_adapter._ls_request", side_effect=mock_ls_request):
                ok, msg = run_multi_session_simulation("template", num_annotators=3)
        assert ok, msg
        assert "3 annotators" in msg
        # Each of 3 annotators annotates 3 tasks = 9 annotation POSTs
        annotation_calls = [c for c in call_log if "/annotations" in c[1]]
        assert len(annotation_calls) >= 3, "At least 3 annotators should have submitted"

    @pytest.mark.skipif(
        not (os.getenv("LABEL_STUDIO_API_KEY") or os.getenv("LABEL_STUDIO_USER_TOKEN")),
        reason="LABEL_STUDIO_API_KEY or LABEL_STUDIO_USER_TOKEN required for live multi-session",
    )
    @pytest.mark.skipif(
        not (TEMPLATE / "queries.json").exists(),
        reason="template/queries.json required",
    )
    def test_multi_session_live(self):
        """Multi-session against real Label Studio (requires LS running + API key)."""
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "label_studio_adapter.py"),
                "multi-session",
                "template",
                "--annotators",
                "3",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ},
        )
        assert proc.returncode == 0, f"multi-session failed: {proc.stderr}\n{proc.stdout}"
        assert "OK" in proc.stdout
        assert "annotators" in proc.stdout.lower() or "annotations" in proc.stdout.lower()
