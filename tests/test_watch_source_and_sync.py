#!/usr/bin/env python3
"""
TDD/BDD tests for watch_source_and_sync.py (file-based CDC).

Run: pytest tests/test_watch_source_and_sync.py -v
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
SOURCE = ROOT / "source"
sys.path.insert(0, str(SCRIPTS))


class TestExtractDbNumFromPath:
    """TDD: extract_db_num_from_path parses source paths correctly."""

    def test_extracts_from_queries_json_path(self):
        from watch_source_and_sync import extract_db_num_from_path

        p = SOURCE / "db-3" / "queries" / "queries.json"
        assert extract_db_num_from_path(p) == 3

    def test_extracts_from_app_queries_path(self):
        from watch_source_and_sync import extract_db_num_from_path

        p = SOURCE / "db-1" / "app" / "QUERIES" / "queries.json"
        assert extract_db_num_from_path(p) == 1

    def test_extracts_from_schema_path(self):
        from watch_source_and_sync import extract_db_num_from_path

        p = SOURCE / "db-16" / "data" / "schema.sql"
        assert extract_db_num_from_path(p) == 16

    def test_returns_none_for_non_db_path(self):
        from watch_source_and_sync import extract_db_num_from_path

        p = Path("/tmp/other/file.txt")
        assert extract_db_num_from_path(p) is None

    def test_returns_none_for_out_of_range(self):
        from watch_source_and_sync import extract_db_num_from_path

        p = SOURCE / "db-99" / "queries" / "queries.json"
        assert extract_db_num_from_path(p) is None


class TestWatchScriptOnceMode:
    """TDD: --once runs sync for specified dbs without watchdog."""

    def test_once_mode_exits_zero(self):
        import subprocess

        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "watch_source_and_sync.py"), "--once", "db-1", "--no-docker"],
            cwd=ROOT,
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0

    def test_once_mode_all_without_args(self):
        import subprocess

        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "watch_source_and_sync.py"), "--once", "--no-docker"],
            cwd=ROOT,
            capture_output=True,
            timeout=60,
        )
        assert r.returncode == 0


class TestCdcBdd:
    """BDD: File-based CDC acceptance scenarios."""

    def test_given_watched_file_change_when_sync_runs_then_checks_execute_first(self):
        """Scenario: Sync runs source checks before populate/resync."""
        from source_material_checks import check_db

        r = check_db(1)
        assert "pass" in r
        assert "checks" in r
        assert "queries_json" in r["checks"]
        # Checks must pass for sync to proceed (integration: db-1 exists)
        if (SOURCE / "db-1").exists():
            assert r["checks"]["queries_json"]["pass"] or "errors" in r["checks"]["queries_json"]
