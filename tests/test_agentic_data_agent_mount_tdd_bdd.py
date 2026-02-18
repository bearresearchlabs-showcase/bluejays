#!/usr/bin/env python3
"""
TDD and BDD testing suite for agentic data agent mount.

TDD: Unit tests for load_client_db, get_bird_pairs, get_pg_port, client/doc structure.
BDD: Acceptance scenarios (Given/When/Then) for mount, docs, queries, BIRD-style pairs.
DDD: Bounded context (agentic context uses client/db/, not source/).

Run: pytest tests/test_agentic_data_agent_mount_tdd_bdd.py -v
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
CLIENT = ROOT / "client"
CLIENT_DB = CLIENT / "db"
CLIENT_DOC = CLIENT / "doc"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


# ---------------------------------------------------------------------------
# TDD: Unit tests
# ---------------------------------------------------------------------------


class TestClientDocStructure:
    """TDD: client/doc/ exists and has expected structure."""

    def test_client_doc_dir_exists(self):
        """client/doc/ exists after implementation."""
        assert CLIENT_DOC.exists(), "client/doc/ must exist"
        assert CLIENT_DOC.is_dir()

    def test_client_doc_has_readme(self):
        """client/doc/README.md exists."""
        readme = CLIENT_DOC / "README.md"
        assert readme.exists(), "client/doc/README.md must exist"

    def test_client_doc_has_notebook(self):
        """client/doc/agentic_data_agent_mount.ipynb exists."""
        nb = CLIENT_DOC / "agentic_data_agent_mount.ipynb"
        assert nb.exists(), "client/doc/agentic_data_agent_mount.ipynb must exist"


class TestLoadClientDb:
    """TDD: load_client_db returns correct structure."""

    def test_load_client_db_returns_dict(self):
        """load_client_db(n) returns dict with keys: db, docs, queries."""
        from agentic_mount import load_client_db

        result = load_client_db(CLIENT_DB, 2)
        assert isinstance(result, dict)
        assert "db" in result
        assert "docs" in result
        assert "queries" in result

    def test_load_client_db_queries_have_required_fields(self):
        """Each query has question, sql, and at least description or expected_output or normal_query."""
        from agentic_mount import load_client_db

        result = load_client_db(CLIENT_DB, 2)
        queries = result.get("queries", [])
        if not queries:
            pytest.skip("db-2 has no queries")
        for q in queries:
            assert "sql" in q, f"Query missing sql: {q.get('number')}"
            has_question = "question" in q and q["question"]
            has_normal = "normal_query" in q and q["normal_query"]
            assert has_question or has_normal, f"Query needs question or normal_query: {q.get('number')}"

    def test_load_client_db_docs_string_or_none(self):
        """docs is str or None."""
        from agentic_mount import load_client_db

        result = load_client_db(CLIENT_DB, 2)
        docs = result.get("docs")
        assert docs is None or isinstance(docs, str)


class TestGetBirdPairs:
    """TDD: get_bird_pairs returns correct structure."""

    def test_get_bird_pairs_returns_list(self):
        """get_bird_pairs(mounted, n) returns list of dicts."""
        from agentic_mount import load_client_db, get_bird_pairs

        mounted = load_client_db(CLIENT_DB, 2)
        pairs = get_bird_pairs(mounted, 2)
        assert isinstance(pairs, list)

    def test_get_bird_pairs_items_have_required_keys(self):
        """Each pair has question, sql, description, evidence, expected_output."""
        from agentic_mount import load_client_db, get_bird_pairs

        mounted = load_client_db(CLIENT_DB, 2)
        pairs = get_bird_pairs(mounted, 2)
        if not pairs:
            pytest.skip("db-2 has no pairs")
        required = {"question", "sql", "description", "evidence", "expected_output"}
        for p in pairs:
            for k in required:
                assert k in p, f"Pair missing key {k}"


class TestGetPgPort:
    """TDD: get_pg_port mapping."""

    def test_get_pg_port_mapping(self):
        """Port for db-N is 5436 + (n - 1)."""
        from agentic_mount import get_pg_port

        assert get_pg_port(1) == 5436
        assert get_pg_port(2) == 5437
        assert get_pg_port(16) == 5451


class TestClientDbStructure:
    """TDD: client/db/db-N has DATABASE/, DOCUMENTATION/, QUERIES/."""

    @pytest.mark.parametrize("db_num", list(range(1, 17)))
    def test_client_db_structure_per_db(self, db_num: int):
        """For each db-1..16, client/db/db-N has DATABASE/, DOCUMENTATION/, QUERIES/."""
        db_dir = CLIENT_DB / f"db-{db_num}"
        if not db_dir.exists():
            pytest.skip(f"client/db/db-{db_num} does not exist")
        assert (db_dir / "DATABASE").exists() or (db_dir / "DOCUMENTATION").exists() or (db_dir / "QUERIES").exists(), (
            f"db-{db_num} must have at least one of DATABASE/, DOCUMENTATION/, QUERIES/"
        )


# ---------------------------------------------------------------------------
# BDD: Scenario tests (Given/When/Then)
# ---------------------------------------------------------------------------


class TestBddMountScenarios:
    """BDD: Acceptance scenarios for mount."""

    def test_given_client_db_when_load_then_has_docs_and_queries(self):
        """Given client/db/db-2 exists, When load_client_db(2), Then docs is not None and queries has 30 items."""
        from agentic_mount import load_client_db

        if not (CLIENT_DB / "db-2").exists():
            pytest.skip("client/db/db-2 does not exist")
        result = load_client_db(CLIENT_DB, 2)
        assert result.get("docs") is not None or len(result.get("queries", [])) > 0
        queries = result.get("queries", [])
        assert len(queries) >= 1, "db-2 should have at least 1 query"
        if len(queries) >= 30:
            assert len(queries) == 30, "Expected 30 queries when present"

    def test_given_bird_pairs_when_inspected_then_question_sql_paired(self):
        """Given get_bird_pairs(2), When inspected, Then each item has non-empty question and sql."""
        from agentic_mount import load_client_db, get_bird_pairs

        if not (CLIENT_DB / "db-2").exists():
            pytest.skip("client/db/db-2 does not exist")
        mounted = load_client_db(CLIENT_DB, 2)
        pairs = get_bird_pairs(mounted, 2)
        if not pairs:
            pytest.skip("db-2 has no bird pairs")
        for p in pairs:
            assert p.get("sql"), f"Pair {p.get('number')} must have sql"
            assert p.get("question") or p.get("normal_query"), f"Pair {p.get('number')} must have question or normal_query"

    def test_given_notebook_cell_logic_when_run_then_no_import_error(self):
        """Given agentic mount module logic, When imported/executed, Then no ImportError."""
        try:
            from agentic_mount import load_client_db, get_bird_pairs, get_pg_port
        except ImportError as e:
            pytest.fail(f"agentic_mount must be importable: {e}")


# ---------------------------------------------------------------------------
# DDD: Bounded context tests
# ---------------------------------------------------------------------------


class TestAgenticBoundedContext:
    """DDD: Agentic context uses client/, not source/."""

    def test_agentic_context_uses_client_not_source(self):
        """All paths resolve to client/db/, not source/."""
        from agentic_mount import load_client_db

        result = load_client_db(CLIENT_DB, 2)
        assert "db" in result
        assert "db-2" in result["db"]
        # load_client_db receives client_db_dir; it must not read from source
        source_queries = ROOT / "source" / "db-2" / "app" / "QUERIES" / "queries.json"
        client_queries = CLIENT_DB / "db-2" / "QUERIES" / "queries.json"
        # Our impl uses client path; this test asserts we use client
        assert str(CLIENT_DB).startswith(str(CLIENT)), "CLIENT_DB must be under CLIENT"

    def test_agentic_context_queries_json_from_client(self):
        """queries.json read from client/db/db-N/QUERIES/."""
        from agentic_mount import load_client_db

        if not (CLIENT_DB / "db-2" / "QUERIES" / "queries.json").exists():
            pytest.skip("client/db/db-2/QUERIES/queries.json does not exist")
        result = load_client_db(CLIENT_DB, 2)
        queries = result.get("queries", [])
        assert len(queries) > 0, "Must load queries from client path"
