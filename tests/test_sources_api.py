"""
Sources API: Unit → Integration → UAT pipeline.
Smallest feature: discover sources, load queries.
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


# --- Unit tests (pure logic, no server, no FastAPI) ---
class TestDiscoverSourcesUnit:
    """Unit tests for discover_sources logic."""

    def test_import_and_discover(self):
        from apps.sources_api.data import discover_sources

        sources = discover_sources()
        assert isinstance(sources, list)
        assert "template" in sources
        assert sources[0] == "template"
        if (ROOT / "source" / "db-1").exists():
            assert "db-1" in sources
        if (ROOT / "source" / "db-16").exists():
            assert "db-16" in sources

    def test_sources_sorted(self):
        from apps.sources_api.data import discover_sources

        sources = discover_sources()
        db_sources = [s for s in sources if s.startswith("db-")]
        if len(db_sources) >= 2:
            nums = [int(s.replace("db-", "")) for s in db_sources]
            assert nums == sorted(nums)


class TestLoadQueriesUnit:
    """Unit tests for load_queries logic."""

    def test_load_template(self):
        from apps.sources_api.data import load_queries

        if not (ROOT / "template" / "queries.json").exists():
            pytest.skip("template/queries.json required")
        queries, err = load_queries("template")
        assert err is None
        assert isinstance(queries, list)
        if queries:
            assert "question_id" in queries[0] or "question" in queries[0]

    def test_load_db1(self):
        from apps.sources_api.data import load_queries

        queries, err = load_queries("db-1")
        if err and "Not found" in err:
            pytest.skip("db-1 not available")
        assert err is None
        assert isinstance(queries, list)
        assert len(queries) >= 1

    def test_load_invalid_source(self):
        from apps.sources_api.data import load_queries

        queries, err = load_queries("db-999")
        assert err is not None
        assert "Not found" in err or "999" in err
        assert queries == []


# --- Integration tests (FastAPI TestClient, no server) ---
@pytest.fixture
def client():
    """FastAPI TestClient for integration tests."""
    try:
        from fastapi.testclient import TestClient
        from apps.sources_api.main import app
        return TestClient(app)
    except ImportError:
        pytest.skip("fastapi required: pip install fastapi")


class TestSourcesApiIntegration:
    """Integration tests: API endpoints via TestClient."""

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert data.get("service") == "sources-api"

    def test_get_sources(self, client):
        r = client.get("/sources")
        assert r.status_code == 200
        data = r.json()
        assert "sources" in data
        sources = data["sources"]
        assert "template" in sources
        assert sources[0] == "template"

    def test_get_queries_db1(self, client):
        r = client.get("/queries?source=db-1")
        assert r.status_code == 200
        data = r.json()
        assert "queries" in data
        assert len(data["queries"]) >= 1

    def test_get_queries_missing_source(self, client):
        r = client.get("/queries")
        assert r.status_code in (422, 400)

    def test_get_queries_invalid_source(self, client):
        r = client.get("/queries?source=db-999")
        assert r.status_code == 404


# --- UAT: End-to-end user flow ---
class TestSourcesUAT:
    """UAT: User selects source, loads queries."""

    def test_uat_sources_then_queries(self, client):
        r1 = client.get("/sources")
        assert r1.status_code == 200
        sources = r1.json()["sources"]
        assert len(sources) >= 1
        source = "db-1" if "db-1" in sources else sources[1] if len(sources) > 1 else "template"
        r2 = client.get(f"/queries?source={source}")
        assert r2.status_code == 200
        queries = r2.json()["queries"]
        assert isinstance(queries, list)
        if queries:
            q = queries[0]
            assert "question_id" in q or "question" in q or "SQL" in q or "sql" in q


