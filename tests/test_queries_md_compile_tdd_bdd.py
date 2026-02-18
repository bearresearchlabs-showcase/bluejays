#!/usr/bin/env python3
"""
TDD and BDD testing suite for queries.md compilation, header consistency, and data updates.

TDD: Unit tests for format_queries_md_template, load_queries_header, update flow.
BDD: Acceptance scenarios (Given/When/Then) for compilation, header structure, data sync.

Run: pytest tests/test_queries_md_compile_tdd_bdd.py -v
"""
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

# Canonical header order (HTML-like: h1 > h2 > h3)
REQUIRED_H2_SECTIONS = [
    "Database Overview",
    "Purpose",
    "Use Case",
    "Business Value",
    "Schema",
    "Domain Knowledge",
    "Query Difficulty Distribution",
    "Queries",
]
# For h3 text only (Query N — difficulty / category)
QUERY_HEADER_PATTERN = re.compile(r"^Query (\d+) — (simple|moderate|challenging) / ([a-zA-Z0-9/_-]+)$")


# ---------------------------------------------------------------------------
# TDD: Unit tests for compilation
# ---------------------------------------------------------------------------


class TestFormatQueriesMdTemplate:
    """TDD: format_queries_md_template produces valid compiled output."""

    @pytest.fixture
    def minimal_queries(self):
        return [
            {
                "number": 1,
                "question_id": 1,
                "question": "Test query?",
                "SQL": "SELECT 1 AS x",
                "evidence": "Test evidence",
                "difficulty": "simple",
                "query_category": "filtering/lookup",
                "tables_used": [],
                "schema_context": {},
                "expected_output": "Single row",
            },
        ]

    def test_compiles_with_minimal_queries(self, minimal_queries):
        from queries_md_template_formatter import format_queries_md_template

        out = format_queries_md_template(minimal_queries, db_id="db-1", db_name="Test DB")
        assert "## Database Overview" in out
        assert "## Queries" in out
        assert "### Query 1 — simple / filtering/lookup" in out
        assert "```json" in out
        assert '"SQL"' in out
        assert "SELECT 1 AS x" in out

    def test_compiles_with_all_header_overrides(self, minimal_queries):
        from queries_md_template_formatter import format_queries_md_template

        out = format_queries_md_template(
            minimal_queries,
            db_id="db-1",
            db_name="Custom Name",
            overview_yaml="db_id: db-1\ndomain: Test",
            purpose_text="Custom purpose",
            use_case_text="Custom use case",
            business_value_text="Custom value",
            schema_sql="CREATE TABLE t (id INT);",
            domain_knowledge_text="Custom domain",
            difficulty_dist_text="Custom distribution",
        )
        assert "Custom Name" in out
        assert "Custom purpose" in out
        assert "Custom use case" in out
        assert "CREATE TABLE t (id INT);" in out
        assert "Custom domain" in out

    def test_title_uses_em_dash(self, minimal_queries):
        from queries_md_template_formatter import format_queries_md_template

        out = format_queries_md_template(minimal_queries, db_id="db-1", db_name="My DB")
        first_line = out.split("\n")[0]
        assert first_line.startswith("# ")
        assert "—" in first_line
        assert "Query Documentation" in first_line

    def test_format_query_block_includes_description_when_present(self):
        """TDD: _format_query_block outputs description in JSON when q has both."""
        from queries_md_template_formatter import _format_query_block

        q = {
            "number": 1,
            "question_id": 1,
            "description": "Context.",
            "evidence": "Technical.",
            "SQL": "SELECT 1",
            "difficulty": "simple",
            "query_category": "filter",
            "tables_used": [],
            "schema_context": {},
            "expected_output": "x",
        }
        block = _format_query_block(q, "db-1", bit_by_bit=True)
        m = re.search(r"```json\n(.*?)```", block, re.DOTALL)
        assert m, "JSON block not found"
        obj = json.loads(m.group(1))
        assert "description" in obj
        assert obj["description"] == "Context."
        assert obj["evidence"] == "Technical."


class TestLoadQueriesHeader:
    """TDD: load_queries_header loads from YAML/JSON correctly."""

    def test_returns_none_for_missing_dir(self):
        from load_queries_header import load_queries_header

        assert load_queries_header(Path("/nonexistent")) is None

    def test_loads_yaml_header(self):
        from load_queries_header import load_queries_header, header_to_format_args

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "queries_header.yaml"
            p.write_text(
                """
db_name: "Test DB"
database_overview: |
  db_id: db-99
  domain: Test
purpose: |
  Test purpose
use_case: |
  Test use case
business_value: |
  Test value
schema: |
  CREATE TABLE t (id INT);
domain_knowledge: |
  Test domain
query_difficulty_distribution: |
  Test distribution
""",
                encoding="utf-8",
            )
            db_dir = Path(d)
            header = load_queries_header(db_dir)
            assert header is not None
            assert header["db_name"] == "Test DB"
            assert "db_id: db-99" in header["overview_yaml"]
            assert "Test purpose" in header["purpose_text"]
            assert "CREATE TABLE t" in header["schema_sql"]

            fmt = header_to_format_args(header)
            assert fmt["db_name"] == "Test DB"
            assert fmt["overview_yaml"] is not None

    def test_loads_json_header(self):
        from load_queries_header import load_queries_header

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "queries_header.json"
            p.write_text(
                json.dumps(
                    {
                        "db_name": "JSON DB",
                        "database_overview": "db_id: db-1",
                        "purpose": "JSON purpose",
                    }
                ),
                encoding="utf-8",
            )
            header = load_queries_header(Path(d))
            assert header is not None
            assert header["db_name"] == "JSON DB"
            assert "db_id: db-1" in header["overview_yaml"]


class TestRewriteScript:
    """TDD: rewrite_queries_md_to_template produces valid output."""

    def test_rewrite_runs_for_db1(self):
        qj = SOURCE / "db-1" / "app" / "QUERIES" / "queries.json"
        if not qj.exists():
            qj = SOURCE / "db-1" / "queries" / "queries.json"
        if not qj.exists():
            pytest.skip("db-1 queries.json not found")

        import subprocess

        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "rewrite_queries_md_to_template.py"), "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"rewrite failed: {proc.stderr}"


# ---------------------------------------------------------------------------
# TDD: Header consistency (HTML-like structure)
# ---------------------------------------------------------------------------


class TestHeaderConsistency:
    """TDD: Headers follow HTML-like hierarchy (h1 > h2 > h3)."""

    def _parse_headers(self, content: str) -> list[tuple[str, str]]:
        """Parse markdown headers as (level, text). level is 'h1','h2','h3'."""
        result = []
        for line in content.split("\n"):
            m = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
            if m:
                level = f"h{len(m.group(1))}"
                result.append((level, m.group(2).strip()))
        return result

    def test_h1_appears_once_at_top(self):
        from queries_md_template_formatter import format_queries_md_template

        qs = [
            {
                "number": 1,
                "question_id": 1,
                "question": "x",
                "SQL": "SELECT 1",
                "evidence": "x",
                "difficulty": "simple",
                "query_category": "filter",
                "tables_used": [],
                "schema_context": {},
                "expected_output": "x",
            },
        ]
        out = format_queries_md_template(qs, db_id="db-1", db_name="Test")
        headers = self._parse_headers(out)
        h1s = [t for lv, t in headers if lv == "h1"]
        assert len(h1s) == 1
        assert headers[0][0] == "h1"
        assert "—" in h1s[0]

    def test_h2_sections_in_canonical_order(self):
        from queries_md_template_formatter import format_queries_md_template

        qs = [
            {
                "number": 1,
                "question_id": 1,
                "question": "x",
                "SQL": "SELECT 1",
                "evidence": "x",
                "difficulty": "simple",
                "query_category": "filter",
                "tables_used": [],
                "schema_context": {},
                "expected_output": "x",
            },
        ]
        out = format_queries_md_template(qs, db_id="db-1", db_name="Test")
        headers = self._parse_headers(out)
        h2_texts = [t for lv, t in headers if lv == "h2"]
        for req in REQUIRED_H2_SECTIONS:
            assert req in h2_texts, f"Missing h2 section: {req}"

    def test_h3_query_headers_match_pattern(self):
        from queries_md_template_formatter import format_queries_md_template

        qs = [
            {
                "number": i,
                "question_id": i,
                "question": f"Q{i}",
                "SQL": "SELECT 1",
                "evidence": "x",
                "difficulty": "moderate",
                "query_category": "aggregation",
                "tables_used": [],
                "schema_context": {},
                "expected_output": "x",
            }
            for i in range(1, 4)
        ]
        out = format_queries_md_template(qs, db_id="db-1", db_name="Test")
        headers = self._parse_headers(out)
        h3_texts = [t for lv, t in headers if lv == "h3"]
        for h3 in h3_texts:
            assert QUERY_HEADER_PATTERN.match(h3), f"Query header must match pattern: {h3}"

    def test_no_orphan_h3_before_h2_queries(self):
        """h3 (Query N) must appear only under ## Queries."""
        from queries_md_template_formatter import format_queries_md_template

        qs = [
            {
                "number": 1,
                "question_id": 1,
                "question": "x",
                "SQL": "SELECT 1",
                "evidence": "x",
                "difficulty": "simple",
                "query_category": "filter",
                "tables_used": [],
                "schema_context": {},
                "expected_output": "x",
            },
        ]
        out = format_queries_md_template(qs, db_id="db-1", db_name="Test")
        lines = out.split("\n")
        seen_queries_h2 = False
        for line in lines:
            if line.strip() == "## Queries":
                seen_queries_h2 = True
            if line.startswith("### Query ") and not seen_queries_h2:
                pytest.fail("Query h3 appeared before ## Queries")
        assert seen_queries_h2


class TestSourceQueriesMdHeaderConsistency:
    """TDD: Source db-N queries.md has consistent header structure."""

    @pytest.mark.parametrize("db_num", [1])
    def test_db1_has_required_sections(self, db_num: int):
        qm = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
        if not qm.exists():
            qm = SOURCE / f"db-{db_num}" / "queries" / "queries.md"
        if not qm.exists():
            pytest.skip(f"db-{db_num} queries.md not found")

        content = qm.read_text(encoding="utf-8")
        for section in REQUIRED_H2_SECTIONS:
            assert f"## {section}" in content, f"Missing section: {section}"

        assert content.strip().startswith("# ")
        assert "—" in content.split("\n")[0]


# ---------------------------------------------------------------------------
# TDD: Data update correctness
# ---------------------------------------------------------------------------


class TestUpdateQueriesMdFromJson:
    """TDD: update_queries_md_from_json syncs data correctly."""

    def test_update_preserves_header_sections(self):
        """When updating from JSON, header sections must remain intact."""
        from queries_md_template_formatter import format_queries_md_template, _format_query_block
        from update_queries_md_from_json import update_query_block

        qs = [
            {
                "number": 1,
                "question_id": 1,
                "question": "Original?",
                "SQL": "SELECT 1",
                "evidence": "Original evidence",
                "difficulty": "simple",
                "query_category": "filter",
                "tables_used": [],
                "schema_context": {},
                "expected_output": "x",
            },
        ]
        original = format_queries_md_template(qs, db_id="db-1", db_name="Test")
        updated_q = {
            "number": 1,
            "question_id": 1,
            "question": "Updated?",
            "SQL": "SELECT 2",
            "evidence": "Updated evidence",
            "difficulty": "moderate",
            "query_category": "aggregation",
            "tables_used": [],
            "schema_context": {},
            "expected_output": "y",
        }
        new_block = _format_query_block(updated_q, "db-1", bit_by_bit=True)
        updated = update_query_block(original, 1, new_block)

        for section in REQUIRED_H2_SECTIONS:
            assert f"## {section}" in updated
        assert "Updated evidence" in updated
        assert "SELECT 2" in updated
        assert "Original evidence" not in updated

    def test_update_script_runs(self):
        qj = SOURCE / "db-1" / "app" / "QUERIES" / "queries.json"
        qm = SOURCE / "db-1" / "app" / "QUERIES" / "queries.md"
        if not qj.exists():
            qj = SOURCE / "db-1" / "queries" / "queries.json"
            qm = SOURCE / "db-1" / "queries" / "queries.md"
        if not qj.exists() or not qm.exists():
            pytest.skip("db-1 queries files not found")

        import subprocess

        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "update_queries_md_from_json.py"), "--db", "1", "--query", "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"update failed: {proc.stderr}"


# ---------------------------------------------------------------------------
# BDD: Acceptance scenarios
# ---------------------------------------------------------------------------


class TestBDDCompilationScenario:
    """BDD: Given queries.json and header, When compile runs, Then queries.md has correct structure."""

    def test_given_queries_json_and_header_when_rewrite_then_queries_md_has_structure(self):
        """Scenario: Compilation produces valid queries.md with all sections."""
        qj = SOURCE / "db-1" / "app" / "QUERIES" / "queries.json"
        if not qj.exists():
            qj = SOURCE / "db-1" / "queries" / "queries.json"
        if not qj.exists():
            pytest.skip("db-1 queries.json not found")

        import subprocess

        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "rewrite_queries_md_to_template.py"), "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0

        qm = SOURCE / "db-1" / "app" / "QUERIES" / "queries.md"
        if not qm.exists():
            qm = SOURCE / "db-1" / "queries" / "queries.md"
        assert qm.exists()
        content = qm.read_text(encoding="utf-8")

        # Then: all required sections present
        for section in REQUIRED_H2_SECTIONS:
            assert f"## {section}" in content
        # Then: at least 30 query blocks
        query_blocks = re.findall(r"^### Query \d+ — ", content, re.MULTILINE)
        assert len(query_blocks) >= 30
        # Then: JSON blocks are valid
        for m in re.finditer(r"```json\n(.*?)```", content, re.DOTALL):
            block = m.group(1).strip()
            obj = json.loads(block)
            assert "SQL" in obj or "sql" in str(obj)
            assert "question_id" in obj or "number" in str(obj)


class TestBDDHeaderConsistencyScenario:
    """BDD: Given queries.md, When headers are parsed, Then they follow HTML-like hierarchy."""

    def test_given_queries_md_when_parsed_then_headers_follow_hierarchy(self):
        """Scenario: Headers are well-formed (h1 > h2 > h3, no skips)."""
        qm = SOURCE / "db-1" / "app" / "QUERIES" / "queries.md"
        if not qm.exists():
            qm = SOURCE / "db-1" / "queries" / "queries.md"
        if not qm.exists():
            pytest.skip("db-1 queries.md not found")

        content = qm.read_text(encoding="utf-8")
        prev_level = 0
        for line in content.split("\n"):
            m = re.match(r"^(#{1,3})\s+", line)
            if m:
                level = len(m.group(1))
                # HTML-like: no skip from h1 to h3; h2->h3 and h3->h2 allowed
                if prev_level == 1 and level == 3:
                    pytest.fail("Header must not skip from h1 to h3")
                prev_level = level


class TestBDDDataUpdateScenario:
    """BDD: Given queries.json change, When update runs, Then queries.md reflects new data."""

    def test_given_json_change_when_update_then_md_reflects(self):
        """Scenario: update_queries_md_from_json syncs evidence/SQL from JSON to MD."""
        from queries_md_template_formatter import format_queries_md_template, _format_query_block
        from update_queries_md_from_json import update_query_block, load_queries_json

        with tempfile.TemporaryDirectory() as d:
            qd = Path(d)
            qj = qd / "queries.json"
            qm = qd / "queries.md"

            # Given: initial queries.md and queries.json
            qs = [
                {
                    "number": 1,
                    "question_id": 1,
                    "question": "Q1?",
                    "SQL": "SELECT 1",
                    "evidence": "Evidence A",
                    "difficulty": "simple",
                    "query_category": "filter",
                    "tables_used": [],
                    "schema_context": {},
                    "expected_output": "x",
                },
            ]
            qj.write_text(json.dumps({"queries": qs}), encoding="utf-8")
            qm.write_text(format_queries_md_template(qs, db_id="db-1", db_name="Test"), encoding="utf-8")

            # When: JSON is updated
            qs[0]["evidence"] = "Evidence B"
            qs[0]["SQL"] = "SELECT 2"
            qj.write_text(json.dumps({"queries": qs}), encoding="utf-8")

            # Simulate update
            loaded = load_queries_json(qd)
            new_block = _format_query_block(loaded[0], "db-1", bit_by_bit=True)
            updated = update_query_block(qm.read_text(encoding="utf-8"), 1, new_block)
            qm.write_text(updated, encoding="utf-8")

            # Then: queries.md reflects new data
            assert "Evidence B" in qm.read_text(encoding="utf-8")
            assert "SELECT 2" in qm.read_text(encoding="utf-8")
            assert "Evidence A" not in qm.read_text(encoding="utf-8")

    def test_given_distinct_description_evidence_when_roundtrip_then_still_distinct(self):
        """Scenario: Description and evidence remain distinct after round-trip."""
        from extract_queries_to_json import extract_queries
        from queries_md_template_formatter import format_queries_md_template, _format_query_block
        from update_queries_md_from_json import update_query_block, load_queries_json

        with tempfile.TemporaryDirectory() as d:
            qd = Path(d)
            qj = qd / "queries.json"
            qm = qd / "queries.md"

            # Given: queries.json has distinct description and evidence for query 1
            qs = [
                {
                    "number": 1,
                    "question_id": 1,
                    "question": "Q1?",
                    "description": "Context: domain purpose.",
                    "evidence": "The query uses CTEs and window functions.",
                    "SQL": "SELECT 1",
                    "difficulty": "simple",
                    "query_category": "filter",
                    "tables_used": [],
                    "schema_context": {},
                    "expected_output": "x",
                },
            ]
            qj.write_text(json.dumps({"queries": qs}), encoding="utf-8")
            qm.write_text(format_queries_md_template(qs, db_id="db-1", db_name="Test"), encoding="utf-8")

            # When: update_queries_md_from_json runs for db-1
            loaded = load_queries_json(qd)
            new_block = _format_query_block(loaded[0], "db-1", bit_by_bit=True)
            updated = update_query_block(qm.read_text(encoding="utf-8"), 1, new_block)
            qm.write_text(updated, encoding="utf-8")

            # When: extract_queries_to_json runs for db-1
            extracted = extract_queries(qm)

            # Then: queries.json still has distinct description and evidence for query 1
            assert len(extracted) == 1
            entry = extracted[0]
            assert entry["description"] != entry["evidence"]
            assert "Context" in (entry.get("description") or "")
            assert "CTEs" in (entry.get("evidence") or "")
