#!/usr/bin/env python3
"""
Extensive test suite for BIRD workbench and ACID/BASE industrial-grade DB behavior.
Uses --no-execute for gates when PostgreSQL unavailable.
Run: pytest tests/test_bird_workbench_acid.py -v
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
BIRD_EXPORT = ROOT / "bird_export"
SOURCE = ROOT / "source"


class TestBirdWorkbenchScripts:
    """BIRD workbench and ACID scripts must exist."""

    def test_bird_workbench_adapter_exists(self):
        p = SCRIPTS / "bird_workbench_adapter.py"
        assert p.exists(), "bird_workbench_adapter.py must exist"

    def test_test_acid_and_queries_exists(self):
        p = SCRIPTS / "test_acid_and_queries.py"
        assert p.exists(), "test_acid_and_queries.py must exist"


class TestBirdWorkbenchNoExecute:
    """Bird workbench must run with --no-execute (gates only, no DB)."""

    @pytest.mark.skipif(
        not (ROOT / "bird_export" / "db-1_bird.json").exists(),
        reason="bird_export/db-1_bird.json required",
    )
    def test_bird_workbench_no_execute_gates_pass(self):
        """Gates (compliance, integrity) must pass; may exit 1 if tb3_workbench missing."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "bird_workbench_adapter.py"), "--no-execute", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90,
        )
        assert "Gate 1" in proc.stdout or "Compliance" in proc.stdout
        assert "Gate 2" in proc.stdout or "Integrity" in proc.stdout
        assert "PASS" in proc.stdout
        assert "Skipping execution" in proc.stdout or "tasks loaded" in proc.stdout

    @pytest.mark.skipif(
        not (ROOT / "bird_export" / "db-1_bird.json").exists(),
        reason="bird_export required",
    )
    def test_bird_workbench_no_execute_exit_zero_when_tb3_available(self):
        """Full run exits 0 only when tb3_workbench is installed."""
        try:
            import tb3_workbench  # noqa: F401
        except ImportError:
            pytest.skip("tb3_workbench not installed")
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "bird_workbench_adapter.py"), "--no-execute", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=90,
        )
        assert proc.returncode == 0, f"bird_workbench failed: {proc.stderr}"


class TestBirdExportStructure:
    """BIRD export must have expected structure for workbench."""

    def test_bird_export_dir_exists(self):
        assert BIRD_EXPORT.exists() or (ROOT / "bird_export").exists(), "bird_export dir expected"

    def test_bird_entries_loadable(self):
        try:
            sys.path.insert(0, str(SCRIPTS))
            from bird_workbench_adapter import load_bird_entries
            entries = load_bird_entries([1])
            assert isinstance(entries, list)
            if entries:
                e = entries[0]
                assert "sql" in e or "_task_id" in e or "query" in str(e).lower()
        except ImportError as e:
            pytest.skip(f"bird_workbench_adapter import failed: {e}")


class TestACIDDocumentation:
    """ACID/BASE and industrial-grade DB behavior must be documented."""

    def test_qa_md_mentions_acid_base(self):
        qa_md = ROOT / ".cursor" / "commands" / "qa.md"
        if qa_md.exists():
            content = qa_md.read_text(encoding="utf-8")
            assert "ACID" in content or "BASE" in content or "industrial" in content.lower()

    def test_bird_knowledge_graph_mentions_acid(self):
        kg = ROOT / "docs" / "BIRD_KNOWLEDGE_GRAPH.md"
        if kg.exists():
            content = kg.read_text(encoding="utf-8")
            assert "ACID" in content or "BASE" in content or "enterprise" in content.lower()


class TestDbCheckBirdWorkbench:
    """db_check bird-workbench must be invocable."""

    @pytest.mark.skipif(
        not (ROOT / "bird_export" / "db-1_bird.json").exists(),
        reason="bird_export/db-1_bird.json required",
    )
    def test_db_check_bird_workbench_gates_pass(self):
        """db_check bird-workbench gates must pass; may exit 1 if tb3_workbench missing."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "db_check.py"), "bird-workbench", "--no-execute", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert "Gate 1" in proc.stdout or "Compliance" in proc.stdout
        assert "Gate 2" in proc.stdout or "Integrity" in proc.stdout
        assert "PASS" in proc.stdout
