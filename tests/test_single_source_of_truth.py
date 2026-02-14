#!/usr/bin/env python3
"""
Tests for single source of truth: db-1 through db-16.
Ensures nothing breaks during reorganization.
Run: pytest tests/test_single_source_of_truth.py -v
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"  # Source of truth: source/db-1..db-16


class TestSourceStructure:
    """Source db-N directories (source/db-1 through source/db-16) must exist with required structure."""

    @pytest.mark.parametrize("n", range(1, 17))
    def test_db_dir_exists(self, n: int):
        d = SOURCE / f"db-{n}"
        assert d.exists() and d.is_dir(), f"source/db-{n} must exist"

    @pytest.mark.parametrize("n", range(1, 17))
    def test_queries_dir_exists(self, n: int):
        # app/QUERIES (iron triangle) or queries/ or QUERIES/
        q = SOURCE / f"db-{n}"
        assert (
            (q / "app" / "QUERIES").exists() or (q / "queries").exists() or (q / "QUERIES").exists()
        ), f"source/db-{n} must have app/QUERIES, queries/, or QUERIES/"

    @pytest.mark.parametrize("n", range(1, 17))
    def test_queries_md_exists(self, n: int):
        q = SOURCE / f"db-{n}"
        qm = (q / "app" / "QUERIES" / "queries.md") if (q / "app" / "QUERIES").exists() else (q / "queries" / "queries.md") if (q / "queries").exists() else (q / "QUERIES" / "queries.md")
        assert qm.exists(), f"source/db-{n} must have queries.md in app/QUERIES, queries/, or QUERIES/"

    @pytest.mark.parametrize("n", range(1, 17))
    def test_data_dir_exists(self, n: int):
        # app/DATABASE (iron triangle) or data/
        q = SOURCE / f"db-{n}"
        assert (q / "app" / "DATABASE").exists() or (q / "data").exists(), f"source/db-{n} must have app/DATABASE or data/"

    @pytest.mark.parametrize("n", range(1, 17))
    def test_schema_exists(self, n: int):
        q = SOURCE / f"db-{n}"
        data = (q / "app" / "DATABASE") if (q / "app" / "DATABASE").exists() else (q / "data")
        schema = data / "schema.sql"
        schema_pg = data / "schema_postgresql.sql"
        assert schema.exists() or schema_pg.exists(), f"source/db-{n} must have schema.sql or schema_postgresql.sql"


class TestExtraction:
    """Query extraction must produce valid queries.json with 30 queries."""

    @pytest.mark.parametrize("n", range(1, 17))
    def test_extract_produces_30_queries(self, n: int):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "extract_queries_to_json.py"), str(n)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"Extraction failed for db-{n}: {proc.stderr}"
        q = SOURCE / f"db-{n}"
        qj = (q / "app" / "QUERIES" / "queries.json") if (q / "app" / "QUERIES").exists() else (q / "queries" / "queries.json") if (q / "queries").exists() else (q / "QUERIES" / "queries.json")
        assert qj.exists(), f"queries.json not created for source/db-{n}"
        data = json.loads(qj.read_text(encoding="utf-8"))
        assert len(data.get("queries", [])) == 30, f"db-{n} must have 30 queries, got {len(data.get('queries', []))}"


class TestResync:
    """Resync must produce client/db with DATABASE/, DOCUMENTATION/, QUERIES/."""

    def test_resync_runs(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "resync_client_db.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert proc.returncode == 0, f"Resync failed: {proc.stderr}"

    @pytest.mark.parametrize("n", range(1, 17))
    def test_client_has_structure(self, n: int):
        client = ROOT / "client" / "db" / f"db-{n}"
        if not (ROOT / "client" / "db").exists():
            pytest.skip("client/db not yet created (run resync)")
        assert (client / "DATABASE").exists(), f"client/db-{n}/DATABASE must exist"
        assert (client / "DOCUMENTATION").exists(), f"client/db-{n}/DOCUMENTATION must exist"
        assert (client / "QUERIES").exists(), f"client/db-{n}/QUERIES must exist"


class TestQASuite:
    """QA suite (used by /QA) must pass for db-1..db-16."""

    def test_verify_unified_structure_passes(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify_unified_structure.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"verify_unified_structure failed: {proc.stderr}"


class TestRootCleanliness:
    """Root directory should not have stray/orphaned files."""

    ALLOWED_ROOT_FILES = {
        ".env.example", ".gitignore", ".pre-commit-config.yaml",
        "db.code-workspace", "docker-compose.yml", "index.html",
        "Jenkinsfile", "vercel.json",
    }
    ALLOWED_ROOT_DIRS = {
        ".cursor", ".github", ".git", ".pytest_cache", ".vscode",
        "apps", "archive", "bird_export", "client", "docs", "docker",
        "k8s", "logs", "notebooks", "research", "results", "scripts",
        "source", "tests", "traces", "apps/website",
    }

    def test_no_stray_py_at_root(self):
        """No .py files at repo root (except __init__ if any)."""
        root_py = [f.name for f in ROOT.iterdir() if f.is_file() and f.suffix == ".py"]
        assert not root_py, f"Move .py files to scripts/: {root_py}"

    def test_no_stray_templates_at_root(self):
        """queries_template.* should be in template/ (as queries.*)."""
        for name in ("queries_template.json", "queries_template.md"):
            assert not (ROOT / name).exists(), f"Move {name} to template/"

    def test_compliance_report_not_at_root(self):
        """compliance_report.json should be in results/, not repo root."""
        root_c = ROOT / "compliance_report.json"
        assert not root_c.exists(), "compliance_report.json should be in results/ (db_check writes there)"


class TestNoDb17InActiveSet:
    """db-17 must not be in the active database set (scripts use db-1..db-16)."""

    def test_active_set_is_1_to_16(self):
        # All scripts use range(1, 17) = db-1..db-16 (17 excluded)
        active = list(range(1, 17))
        assert 16 in active and 17 not in active
        assert len(active) == 16

    def test_db17_archived_not_in_root(self):
        # db-17 moved to archive/ - should not exist in source/ or root
        assert not (ROOT / "db-17").exists(), "db-17 should be in archive/, not root"
        assert not (SOURCE / "db-17").exists(), "db-17 should not be in source/"
        assert (ROOT / "archive" / "db-17").exists(), "db-17 should exist in archive/"
