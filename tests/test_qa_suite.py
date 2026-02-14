#!/usr/bin/env python3
"""
Extensive test suite for QA features: format, resync, audit, compliance, integrity.
Run: pytest tests/test_qa_suite.py -v
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
CLIENT = ROOT / "client" / "db"
RESULTS = ROOT / "results"


class TestQASuiteCommands:
    """QA suite subcommands must run without crashing."""

    def test_db_check_unknown_subcommand_returns_1(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py"), "unknown-cmd"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 1
        assert "Unknown subcommand" in proc.stdout or "unknown" in proc.stdout.lower()

    def test_db_check_no_args_prints_usage(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 1
        assert "Subcommands" in proc.stdout or "validate" in proc.stdout


class TestFormatCommand:
    """Format command must produce deliverables."""

    @pytest.mark.parametrize("n", [1])
    def test_format_produces_deliverable(self, n: int):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py"), "format", str(n)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert proc.returncode == 0, f"Format failed for db-{n}: {proc.stderr}"
        deliverable = SOURCE / f"db-{n}" / "deliverable" / f"db-{n}.md"
        assert deliverable.exists(), f"Deliverable not created: {deliverable}"


class TestComplianceCheck:
    """Compliance check must run and produce report."""

    def test_compliance_runs_for_db1(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py"), "compliance", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode in (0, 1), f"Compliance should run: {proc.stderr}"

    def test_compliance_report_exists(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py"), "compliance", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        report = RESULTS / "compliance_report.json"
        assert report.exists(), "compliance_report.json should exist after compliance run"
        data = json.loads(report.read_text(encoding="utf-8"))
        assert "summary" in data or "databases" in data or "db-1" in str(data)


class TestIntegrityCheck:
    """Integrity check must run and update metadata."""

    def test_integrity_runs_for_db1(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py"), "integrity", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"Integrity failed: {proc.stderr}"

    def test_integrity_creates_metadata(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py"), "integrity", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0
        meta = SOURCE / "db-1" / "metadata" / "integrity.json"
        assert meta.exists(), "integrity.json should be created"
        data = json.loads(meta.read_text(encoding="utf-8"))
        assert "timestamp" in data
        assert any(k in data for k in ("schema.sql", "schema_postgresql.sql", "queries.json"))


class TestQASuiteFlow:
    """Full QA suite flow (format → resync → audit → compliance → integrity)."""

    def test_qa_suite_runs_for_db1(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py"), "qa-suite", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert proc.returncode in (0, 1), f"QA suite should run: {proc.stderr[:500]}"

    def test_qa_suite_includes_format_step(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "db_check.py"), "qa-suite", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert "Format" in proc.stdout or "format" in proc.stdout, "QA suite should include format step"
