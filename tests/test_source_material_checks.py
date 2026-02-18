#!/usr/bin/env python3
"""
TDD unit tests for source_material_checks.py.

Validates: queries.json, queries_header.yaml, schema.sql, data.sql, queries.md.
Run: pytest tests/test_source_material_checks.py -v
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
SOURCE = ROOT / "source"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from source_material_checks import (
    check_db,
    check_data_sql,
    check_queries_header,
    check_queries_json,
    check_queries_md,
    check_schema_sql,
    REQUIRED_H2_SECTIONS,
)


# ---------------------------------------------------------------------------
# TDD: Unit tests for individual checks
# ---------------------------------------------------------------------------


class TestCheckQueriesJson:
    """TDD: check_queries_json validates structure and content."""

    def test_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as d:
            qdir = Path(d) / "queries"
            qdir.mkdir()
            r = check_queries_json(qdir)
            assert r["pass"] is False
            assert "queries.json not found" in r["errors"]

    def test_invalid_json_fails(self):
        with tempfile.TemporaryDirectory() as d:
            qdir = Path(d) / "queries"
            qdir.mkdir()
            (qdir / "queries.json").write_text("{ invalid }")
            r = check_queries_json(qdir)
            assert r["pass"] is False
            assert "Invalid JSON" in r["errors"][0]

    def test_wrong_count_fails(self):
        with tempfile.TemporaryDirectory() as d:
            qdir = Path(d) / "queries"
            qdir.mkdir()
            (qdir / "queries.json").write_text(json.dumps({"queries": [{"SQL": "SELECT 1", "number": 1}]}))
            r = check_queries_json(qdir)
            assert r["pass"] is False
            assert "Expected 30 queries" in r["errors"][0]

    def test_missing_sql_fails(self):
        with tempfile.TemporaryDirectory() as d:
            qdir = Path(d) / "queries"
            qdir.mkdir()
            queries = [{"number": i, "evidence": "x"} for i in range(1, 31)]
            (qdir / "queries.json").write_text(json.dumps({"queries": queries}))
            r = check_queries_json(qdir)
            assert r["pass"] is False
            assert "missing SQL" in r["errors"][0]

    def test_valid_30_queries_passes(self):
        with tempfile.TemporaryDirectory() as d:
            qdir = Path(d) / "queries"
            qdir.mkdir()
            queries = [
                {"number": i, "SQL": "SELECT 1", "evidence": "test", "question_id": i}
                for i in range(1, 31)
            ]
            (qdir / "queries.json").write_text(json.dumps({"queries": queries}))
            r = check_queries_json(qdir)
            assert r["pass"] is True


class TestCheckQueriesHeader:
    """TDD: check_queries_header validates YAML/JSON header (optional)."""

    def test_missing_passes_no_warning(self):
        """Optional: queries_header absent passes with zero warnings (zero-warnings policy)."""
        with tempfile.TemporaryDirectory() as d:
            r = check_queries_header(Path(d))
            assert r["pass"] is True
            assert len(r.get("warnings", [])) == 0

    def test_valid_yaml_passes(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "queries_header.yaml").write_text(
                """
db_name: Test DB
overview_yaml: |
  db_id: db-1
  domain: Test
purpose_text: Purpose
use_case: Use case
business_value: Value
"""
            )
            r = check_queries_header(Path(d))
            # load_queries_header may return different keys
            assert r["present"] is True


class TestCheckSchemaSql:
    """TDD: check_schema_sql validates DDL presence."""

    def test_missing_fails(self):
        with tempfile.TemporaryDirectory() as d:
            r = check_schema_sql(Path(d))
            assert r["pass"] is False
            assert "schema.sql not found" in r["errors"]

    def test_empty_schema_fails(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "schema.sql").write_text("-- empty")
            r = check_schema_sql(Path(d))
            assert r["pass"] is False
            assert "CREATE TABLE" in r["errors"][0]

    def test_valid_schema_passes(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "schema.sql").write_text("CREATE TABLE t (id INT);")
            r = check_schema_sql(Path(d))
            assert r["pass"] is True


class TestCheckDataSql:
    """TDD: check_data_sql validates data file (optional)."""

    def test_missing_passes_no_warning(self):
        """Optional: data.sql absent passes with zero warnings (zero-warnings policy)."""
        with tempfile.TemporaryDirectory() as d:
            r = check_data_sql(Path(d))
            assert r["pass"] is True
            assert len(r.get("warnings", [])) == 0

    def test_valid_insert_passes(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "data.sql").write_text("INSERT INTO t VALUES (1);")
            r = check_data_sql(Path(d))
            assert r["pass"] is True
            assert r["present"] is True


class TestCheckQueriesMd:
    """TDD: check_queries_md validates structure and query blocks."""

    def test_missing_fails(self):
        with tempfile.TemporaryDirectory() as d:
            r = check_queries_md(Path(d))
            assert r["pass"] is False
            assert "queries.md not found" in r["errors"]

    def test_missing_section_fails(self):
        with tempfile.TemporaryDirectory() as d:
            qm = Path(d) / "queries.md"
            qm.write_text("# Title\n\n## Database Overview\n")
            r = check_queries_md(Path(d))
            assert r["pass"] is False
            assert any("Missing section" in e for e in r["errors"])

    def test_no_h1_fails(self):
        with tempfile.TemporaryDirectory() as d:
            qm = Path(d) / "queries.md"
            content = "## Database Overview\n"
            for s in REQUIRED_H2_SECTIONS:
                content += f"\n## {s}\n"
            content += "\n## Queries\n"
            for i in range(1, 31):
                content += f"\n### Query {i} — simple / test\n"
            qm.write_text(content)
            r = check_queries_md(Path(d))
            assert r["pass"] is False
            assert "must start with # " in r["errors"][0]

    def test_fewer_than_30_blocks_fails(self):
        with tempfile.TemporaryDirectory() as d:
            qm = Path(d) / "queries.md"
            content = "# Title — Doc\n"
            for s in REQUIRED_H2_SECTIONS:
                content += f"\n## {s}\n"
            content += "\n## Queries\n"
            for i in range(1, 25):
                content += f"\n### Query {i} — simple / test\n"
            qm.write_text(content)
            r = check_queries_md(Path(d))
            assert r["pass"] is False
            assert "Expected at least 30" in r["errors"][0]

    def test_valid_structure_passes(self):
        with tempfile.TemporaryDirectory() as d:
            qm = Path(d) / "queries.md"
            content = "# Title — Query Documentation\n"
            for s in REQUIRED_H2_SECTIONS:
                content += f"\n## {s}\n"
            content += "\n## Queries\n"
            for i in range(1, 31):
                content += f"\n### Query {i} — simple / test\n"
            qm.write_text(content)
            r = check_queries_md(Path(d))
            assert r["pass"] is True


class TestCheckDb:
    """TDD: check_db aggregates all checks for one db-N."""

    def test_missing_source_dir_fails(self):
        r = check_db(999)
        assert r["pass"] is False
        assert "not found" in r["errors"][0]

    def test_db1_integration(self):
        """Integration: db-1 should pass if source exists."""
        db1 = SOURCE / "db-1"
        if not db1.exists():
            pytest.skip("source/db-1 not present")
        r = check_db(1)
        assert "db_id" in r
        assert r["db_id"] == "db-1"
        # db-1 has full structure; may have queries_header warning
        assert "checks" in r
        assert "queries_json" in r["checks"]
        assert "schema_sql" in r["checks"]


# ---------------------------------------------------------------------------
# BDD: Acceptance scenarios (Given/When/Then style)
# ---------------------------------------------------------------------------


class TestSourceMaterialChecksBDD:
    """BDD: Acceptance scenarios for source material validation."""

    def test_given_valid_source_when_check_db_then_all_checks_pass(self):
        """Scenario: Valid source material passes all checks (uses real db-1)."""
        if not (SOURCE / "db-1").exists():
            pytest.skip("source/db-1 not present")
        r = check_db(1)
        assert r["pass"] is True, r.get("errors", r.get("warnings", []))
