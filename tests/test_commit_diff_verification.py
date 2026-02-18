#!/usr/bin/env python3
"""
TDD and BDD tests for commit diff verification (38ce1cd vs HEAD).

TDD: Kent Beck Red-Green-Refactor — validation scripts drive implementation.
BDD: Cucumber/Gherkin-style acceptance criteria — report structure and behavior.

Run: pytest tests/test_commit_diff_verification.py -v
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
REPORT_PATH = ROOT / "results" / "commit_diff_38ce1cd_report.json"
RAW_DIFF_PATH = ROOT / "results" / "commit_diff_38ce1cd_raw.txt"


class TestVerifyCommitDiffScript:
    """verify_commit_diff.py must run and produce report."""

    def test_script_runs_successfully(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_commit_diff.py"),
                "--skip-validate-qa",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert proc.returncode == 0, f"Script failed: {proc.stderr}"

    def test_report_exists_after_run(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_commit_diff.py"),
                "--skip-validate-qa",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert proc.returncode == 0
        assert REPORT_PATH.exists(), f"Report not created: {REPORT_PATH}"


class TestCommitDiffReportStructure:
    """Report must have expected structure per plan."""

    @pytest.fixture
    def report(self):
        if not REPORT_PATH.exists():
            pytest.skip(f"Run verify_commit_diff.py first: {REPORT_PATH}")
        with open(REPORT_PATH, encoding="utf-8") as f:
            return json.load(f)

    def test_report_has_base_commit(self, report):
        assert "base_commit" in report
        assert report["base_commit"] == "38ce1cd1aa03012979e6a85b5ca9299449f76ad6"

    def test_report_has_databases(self, report):
        assert "databases" in report
        dbs = report["databases"]
        assert len(dbs) >= 1
        for i in range(1, 17):
            db_id = f"db-{i}"
            if db_id in dbs:
                assert "source" in dbs[db_id]
                assert "client" in dbs[db_id]

    def test_each_db_has_source_and_client_sections(self, report):
        dbs = report.get("databases", {})
        for db_id, db_data in dbs.items():
            assert "source" in db_data, f"{db_id} missing source"
            assert "client" in db_data, f"{db_id} missing client"
            src = db_data["source"]
            assert "app/DATABASE" in src or "app/DOCUMENTATION" in src or "app/QUERIES" in src
            cli = db_data["client"]
            assert "DATABASE" in cli or "DOCUMENTATION" in cli or "QUERIES" in cli

    def test_each_db_has_source_vs_client_sync(self, report):
        dbs = report.get("databases", {})
        for db_id, db_data in dbs.items():
            sync = db_data.get("source_vs_client_sync", {})
            assert "DATABASE" in sync or "QUERIES" in sync

    def test_queries_json_key_diff_summary_when_present(self, report):
        dbs = report.get("databases", {})
        found = False
        for db_id, db_data in dbs.items():
            src_q = db_data.get("source", {}).get("app/QUERIES", {})
            if "queries.json" in src_q:
                qj = src_q["queries.json"]
                if isinstance(qj, dict) and "key_diff_summary" in qj:
                    found = True
                    break
        assert found, "At least one DB should have queries.json with key_diff_summary"

    def test_summary_has_validation_and_qa_pass(self, report):
        s = report.get("summary", {})
        assert "validation_pass" in s
        assert "qa_pass" in s
        assert "total_dbs" in s

    def test_report_json_valid_schema(self, report):
        """TDD: Assert report has required top-level keys."""
        required = ["base_commit", "target", "generated_at", "databases", "summary"]
        for key in required:
            assert key in report, f"Report must have top-level key: {key}"

    def test_each_db_has_files_with_at_base_at_head(self, report):
        """TDD: Assert file entries have at_base, at_head, changed."""
        dbs = report.get("databases", {})
        for db_id, db_data in dbs.items():
            for loc in ["source", "client"]:
                loc_data = db_data.get(loc, {})
                for sec_name, sec_data in loc_data.items():
                    if isinstance(sec_data, dict) and "files" in sec_data:
                        for fname, finfo in sec_data["files"].items():
                            assert "at_base" in finfo, f"{db_id}/{loc}/{sec_name}/{fname} must have at_base"
                            assert "at_head" in finfo, f"{db_id}/{loc}/{sec_name}/{fname} must have at_head"
                            assert "changed" in finfo, f"{db_id}/{loc}/{sec_name}/{fname} must have changed"

    def test_key_diff_summary_counts_integer(self, report):
        """TDD: Assert key_diff_summary values are integers."""
        dbs = report.get("databases", {})
        for db_id, db_data in dbs.items():
            for loc in ["source", "client"]:
                loc_data = db_data.get(loc, {})
                for sec_name, sec_data in loc_data.items():
                    if sec_name == "app/QUERIES" or sec_name == "QUERIES":
                        qj = sec_data.get("queries.json") if isinstance(sec_data, dict) else None
                        if isinstance(qj, dict) and "key_diff_summary" in qj:
                            for key, val in qj["key_diff_summary"].items():
                                assert isinstance(val, int), f"key_diff_summary.{key} must be int, got {type(val)}"


class TestBDDAcceptanceCriteria:
    """
    BDD acceptance criteria (Given/When/Then).
    Verifies plan behavior from user perspective.
    """

    @pytest.fixture
    def report(self):
        """Ensure report exists by running script."""
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_commit_diff.py"),
                "--skip-validate-qa",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert proc.returncode == 0, f"Script failed: {proc.stderr}"
        assert REPORT_PATH.exists()
        with open(REPORT_PATH, encoding="utf-8") as f:
            return json.load(f)

    def test_scenario_raw_diff_includes_source_client(self):
        """Scenario: Given raw diff file, When inspected, Then contains source/ or client/ paths."""
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_commit_diff.py"),
                "--skip-validate-qa",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert proc.returncode == 0
        assert RAW_DIFF_PATH.exists(), "Raw diff file must be created"
        content = RAW_DIFF_PATH.read_text(encoding="utf-8")
        assert "source/" in content or "client/" in content, "Diff must include source/ or client/ paths"

    def test_scenario_raw_diff_captured(self):
        """Scenario: Given 38ce1cd and HEAD, When verify runs, Then raw diff is saved."""
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_commit_diff.py"),
                "--skip-validate-qa",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert proc.returncode == 0
        assert RAW_DIFF_PATH.exists(), "Raw diff file must be created"
        content = RAW_DIFF_PATH.read_text(encoding="utf-8")
        assert "source/" in content or "client/" in content, "Diff must include source or client"

    def test_scenario_all_16_dbs_in_report(self, report):
        """Scenario: Given report exists, When user inspects databases, Then db-1..db-16 present."""
        dbs = report.get("databases", {})
        for i in range(1, 17):
            assert f"db-{i}" in dbs, f"db-{i} must be in report"

    def test_scenario_each_db_has_three_sections(self, report):
        """Scenario: Given each db-N, When user inspects sections, Then DATABASE/DOCUMENTATION/QUERIES present."""
        dbs = report.get("databases", {})
        for db_id, db_data in dbs.items():
            src = db_data.get("source", {})
            cli = db_data.get("client", {})
            assert "app/DATABASE" in src, f"{db_id} source must have app/DATABASE"
            assert "app/DOCUMENTATION" in src, f"{db_id} source must have app/DOCUMENTATION"
            assert "app/QUERIES" in src, f"{db_id} source must have app/QUERIES"
            assert "DATABASE" in cli, f"{db_id} client must have DATABASE"
            assert "DOCUMENTATION" in cli, f"{db_id} client must have DOCUMENTATION"
            assert "QUERIES" in cli, f"{db_id} client must have QUERIES"

    def test_scenario_queries_json_key_diff_tracked(self, report):
        """Scenario: Given queries.json exists, When user inspects key_diff_summary, Then changed keys are counted."""
        dbs = report.get("databases", {})
        at_least_one = False
        for db_id, db_data in dbs.items():
            src_q = db_data.get("source", {}).get("app/QUERIES", {})
            qj = src_q.get("queries.json")
            if isinstance(qj, dict) and "key_diff_summary" in qj:
                at_least_one = True
                keys = qj.get("keys_per_query", [])
                assert "expected_output" in keys or "description" in keys or len(keys) > 0
        assert at_least_one, "At least one DB must have queries.json with key_diff_summary"

    def test_scenario_source_vs_client_sync_reported(self, report):
        """Scenario: Given report exists, When user checks sync, Then in_sync and mismatched_files present."""
        dbs = report.get("databases", {})
        for db_id, db_data in dbs.items():
            sync = db_data.get("source_vs_client_sync", {})
            for section in ["DATABASE", "QUERIES"]:
                if section in sync:
                    assert "in_sync" in sync[section]
                    assert "mismatched_files" in sync[section]

    def test_scenario_report_compilable_to_mdx(self, report):
        """Scenario: Given report JSON, When compile runs, Then MDX output has frontmatter and sections."""
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "compile_commit_diff_report.py"),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"Compile failed: {proc.stderr}"
        mdx_path = ROOT / "results" / "commit_diff_38ce1cd_report.mdx"
        assert mdx_path.exists(), "MDX report must be created"
        content = mdx_path.read_text(encoding="utf-8")
        assert "---" in content, "MDX must have frontmatter"
        assert "title:" in content
        assert "generated_at:" in content
        assert "## Summary" in content
        assert "## Per-DB Report" in content
