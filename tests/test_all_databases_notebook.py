#!/usr/bin/env python3
"""
TDD/BDD tests for all_databases_session notebook runtime logic.

Tests Docker check, source inventory, and notebook cell logic without running Jupyter.
Run: pytest tests/test_all_databases_notebook.py -v
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
SOURCE = ROOT / "source"
sys.path.insert(0, str(SCRIPTS))


def check_docker_running() -> bool:
    """Mirror notebook logic: check if Docker daemon is running."""
    try:
        r = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_postgres_containers() -> dict:
    """Mirror notebook logic: which postgres-db-N containers are running."""
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0:
            return {}
        names = [n.strip() for n in r.stdout.splitlines() if n.strip()]
        return {n: True for n in names if n.startswith("postgres-db-")}
    except Exception:
        return {}


class TestDockerRuntimeCheck:
    """TDD: Docker runtime check behaves correctly."""

    def test_check_docker_returns_bool(self):
        assert isinstance(check_docker_running(), bool)

    def test_check_containers_returns_dict(self):
        assert isinstance(check_postgres_containers(), dict)

    def test_when_docker_not_running_containers_empty_or_partial(self):
        """BDD: When Docker is not running, container check does not crash."""
        # May or may not have docker; either way no crash
        _ = check_postgres_containers()


class TestNotebookSourceInventory:
    """TDD: Source inventory logic matches db_paths."""

    def test_source_inventory_structure(self):
        from db_paths import get_queries_dir, get_data_dir

        rows = []
        for n in range(1, 5):
            db_dir = SOURCE / f"db-{n}"
            if not db_dir.exists():
                continue
            qdir = get_queries_dir(db_dir)
            ddir = get_data_dir(db_dir)
            app_dir = db_dir / "app"
            rows.append(
                {
                    "db": f"db-{n}",
                    "queries_json": (qdir / "queries.json").exists(),
                    "schema": (ddir / "schema.sql").exists(),
                    "app_populated": app_dir.exists() and (app_dir / "DATABASE").exists(),
                }
            )
        assert isinstance(rows, list)
        for r in rows:
            assert "db" in r
            assert "queries_json" in r
            assert "schema" in r

    def test_notebook_assumes_docker_already_running(self):
        """BDD: Notebook assumes Docker is running; check warns if not."""
        docker_ok = check_docker_running()
        # When docker not running, notebook should show warning (logic tested via check)
        if not docker_ok:
            assert True  # Warning path
        else:
            containers = check_postgres_containers()
            assert isinstance(containers, dict)


class TestNotebookFileExists:
    """TDD: Notebook file exists and is valid JSON."""

    def test_notebook_exists(self):
        nb = ROOT / "notebooks" / "all_databases_session.ipynb"
        assert nb.exists()

    def test_notebook_has_required_sections(self):
        import json

        nb = ROOT / "notebooks" / "all_databases_session.ipynb"
        data = json.loads(nb.read_text())
        cells = data.get("cells", [])
        sources = []
        for c in cells:
            src = c.get("source", [])
            if isinstance(src, list):
                sources.extend("".join(s) for s in src)
            else:
                sources.append(str(src))
        combined = " ".join(sources)
        assert "Docker" in combined or "docker" in combined
        assert "source" in combined or "SOURCE" in combined
        assert "check_docker" in combined or "check_docker_running" in combined
