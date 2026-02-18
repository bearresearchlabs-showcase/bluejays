#!/usr/bin/env python3
"""
TDD/BDD tests for repo_health_check.py and compile_repo_health_mdx.py.

Run: pytest tests/test_repo_health.py -v
"""
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"
sys.path.insert(0, str(SCRIPTS))


class TestRepoHealthCheckScript:
    """TDD: repo_health_check.py produces valid output."""

    def test_script_exists(self):
        p = SCRIPTS / "repo_health_check.py"
        assert p.exists()

    def test_script_runs_and_produces_json(self):
        import subprocess
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "repo_health_check.py"), "--lenient"],
            cwd=ROOT,
            capture_output=True,
            timeout=30,
        )
        assert r.returncode in (0, 1)  # Pass or fail
        out = RESULTS / "repo_health.json"
        assert out.exists()
        data = json.loads(out.read_text())
        assert "generated_at" in data
        assert "Pass" in data
        assert "checks" in data
        assert "databases" in data

    def test_report_has_required_check_keys(self):
        out = RESULTS / "repo_health.json"
        if not out.exists():
            pytest.skip("Run repo_health_check.py first")
        data = json.loads(out.read_text())
        checks = data.get("checks", {})
        assert "data_size_gb" in checks
        assert "schema_postgresql_compliant" in checks
        assert "naming_consistent" in checks
        assert "unnecessary_source_files" in checks
        assert "unnecessary_root_files" in checks

    def test_data_size_check_has_total_bytes(self):
        out = RESULTS / "repo_health.json"
        if not out.exists():
            pytest.skip("Run repo_health_check.py first")
        data = json.loads(out.read_text())
        size = data["checks"]["data_size_gb"]
        assert "total_bytes" in size
        assert "required_bytes" in size
        assert isinstance(size["total_bytes"], int)


class TestCompileRepoHealthMdx:
    """TDD: compile_repo_health_mdx.py produces valid MDX."""

    def test_compile_script_exists(self):
        p = SCRIPTS / "compile_repo_health_mdx.py"
        assert p.exists()

    def test_compile_produces_mdx(self):
        import subprocess
        # Ensure JSON exists
        subprocess.run(
            [sys.executable, str(SCRIPTS / "repo_health_check.py"), "--lenient"],
            cwd=ROOT,
            capture_output=True,
            timeout=30,
        )
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "compile_repo_health_mdx.py")],
            cwd=ROOT,
            capture_output=True,
            timeout=10,
        )
        assert r.returncode == 0
        mdx = RESULTS / "repo_health.mdx"
        assert mdx.exists()
        content = mdx.read_text()
        assert "---" in content
        assert "title:" in content
        assert "Repo Health" in content
        assert "## Summary" in content
        assert "## Data Size" in content
        assert "## Flagged" in content


class TestRepoHealthBdd:
    """BDD: Repo health acceptance scenarios."""

    def test_given_repo_health_run_when_json_exists_then_compilable_to_mdx(self):
        """Scenario: repo_health.json compiles to MDX."""
        json_path = RESULTS / "repo_health.json"
        if not json_path.exists():
            pytest.skip("Run repo_health_check.py first")
        from compile_repo_health_mdx import compile_to_mdx
        data = json.loads(json_path.read_text())
        mdx = compile_to_mdx(data)
        assert "---" in mdx
        assert "generated_at" in mdx
        assert "Data size" in mdx or "data size" in mdx.lower()
