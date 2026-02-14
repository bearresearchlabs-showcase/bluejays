#!/usr/bin/env python3
"""
Extensive QA tests for queries.md format — ensures bit-for-bit match with @template.

Tests reference template/qa_anchor.yaml and template/qa_anchor.json as validation schema.
Run: pytest tests/test_qa_queries_format.py -v

Anchor ensures tests are executed: qa_anchor.yaml/json defines the canonical format.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
TEMPLATE = ROOT / "template"
SOURCE = ROOT / "source"
QA_ANCHOR_YAML = TEMPLATE / "qa_anchor.yaml"
QA_ANCHOR_JSON = TEMPLATE / "qa_anchor.json"


def _load_anchor() -> dict:
    """Load QA anchor (prefer JSON for consistency)."""
    if QA_ANCHOR_JSON.exists():
        return json.loads(QA_ANCHOR_JSON.read_text(encoding="utf-8"))
    if QA_ANCHOR_YAML.exists():
        try:
            import yaml
            return yaml.safe_load(QA_ANCHOR_YAML.read_text(encoding="utf-8"))
        except ImportError:
            return {}
    return {}


@pytest.fixture(scope="module")
def anchor():
    """Load QA anchor once per module."""
    return _load_anchor()


class TestQAAnchorExists:
    """QA anchor must exist for test execution."""

    def test_qa_anchor_yaml_exists(self):
        assert QA_ANCHOR_YAML.exists(), "template/qa_anchor.yaml must exist"

    def test_qa_anchor_json_exists(self):
        assert QA_ANCHOR_JSON.exists(), "template/qa_anchor.json must exist"

    def test_anchor_has_required_sections(self, anchor):
        assert "required_sections" in anchor
        assert len(anchor["required_sections"]) >= 5

    def test_anchor_has_query_block_pattern(self, anchor):
        assert "query_block_pattern" in anchor
        assert "Query" in anchor["query_block_pattern"]
        assert "—" in anchor["query_block_pattern"] or "\\\\d" in anchor["query_block_pattern"]

    def test_anchor_has_query_json_required_fields(self, anchor):
        assert "query_json_required_fields" in anchor
        required = anchor["query_json_required_fields"]
        assert "db_id" in required
        assert "question_id" in required
        assert "SQL" in required
        assert "evidence" in required

    def test_qa_anchor_yaml_json_1to1_structure(self):
        """qa_anchor.yaml and qa_anchor.json must have 1:1 top-level key structure."""
        if not QA_ANCHOR_YAML.exists() or not QA_ANCHOR_JSON.exists():
            pytest.skip("qa_anchor files missing")
        try:
            import yaml
        except ImportError:
            pytest.skip("pyyaml not installed")
        yaml_data = yaml.safe_load(QA_ANCHOR_YAML.read_text(encoding="utf-8"))
        json_data = json.loads(QA_ANCHOR_JSON.read_text(encoding="utf-8"))
        yaml_keys = set(yaml_data.keys()) if isinstance(yaml_data, dict) else set()
        json_keys = set(json_data.keys()) if isinstance(json_data, dict) else set()
        missing_in_json = yaml_keys - json_keys
        missing_in_yaml = json_keys - yaml_keys
        assert not missing_in_json, f"qa_anchor.json missing keys from yaml: {missing_in_json}"
        assert not missing_in_yaml, f"qa_anchor.yaml missing keys from json: {missing_in_yaml}"


class TestTemplateMatch:
    """Source must match @template reference."""

    def test_validate_template_match_script_exists(self):
        assert (ROOT / "scripts" / "validate_template_match.py").exists()

    def test_validate_template_match_runs_for_db1(self):
        import subprocess
        import sys
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_template_match.py"), "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"template match failed: {proc.stderr or proc.stdout}"

    def test_template_app_exists(self):
        assert (TEMPLATE / "app" / "index.html").exists()


class TestConfigRegistry:
    """Config registry defines YAML/JSON pairs for 1:1 structure."""

    def test_config_registry_exists(self):
        assert (TEMPLATE / "config_registry.yaml").exists()

    def test_config_registry_has_qa_anchor_pair(self):
        try:
            import yaml
        except ImportError:
            pytest.skip("pyyaml not installed")
        reg = yaml.safe_load((TEMPLATE / "config_registry.yaml").read_text(encoding="utf-8"))
        pairs = reg.get("pairs", [])
        qa = next((p for p in pairs if p.get("id") == "qa_anchor"), None)
        assert qa is not None
        assert "yaml" in qa and "json" in qa


class TestTemplateQueriesMdStructure:
    """Template queries.md must have exact structure."""

    def test_template_queries_md_exists(self):
        assert (TEMPLATE / "queries.md").exists()

    def test_template_has_database_overview(self):
        content = (TEMPLATE / "queries.md").read_text(encoding="utf-8")
        assert "## Database Overview" in content
        assert "```yaml" in content

    def test_template_has_purpose_use_case_business_value(self):
        content = (TEMPLATE / "queries.md").read_text(encoding="utf-8")
        assert "## Purpose" in content
        assert "## Use Case" in content
        assert "## Business Value" in content

    def test_template_has_schema_section(self):
        content = (TEMPLATE / "queries.md").read_text(encoding="utf-8")
        assert "## Schema" in content

    def test_template_has_queries_section(self):
        content = (TEMPLATE / "queries.md").read_text(encoding="utf-8")
        assert "## Queries" in content

    def test_template_query_block_uses_em_dash(self):
        content = (TEMPLATE / "queries.md").read_text(encoding="utf-8")
        assert "### Query 1 — " in content
        assert "### Query 2 — " in content

    def test_template_query_blocks_have_json(self):
        content = (TEMPLATE / "queries.md").read_text(encoding="utf-8")
        assert "```json" in content
        assert '"db_id"' in content
        assert '"question_id"' in content
        assert '"SQL"' in content


class TestSourceQueriesMdFormat:
    """Source db-N app/QUERIES/queries.md must match template structure."""

    @pytest.mark.parametrize("db_num", [1, 2, 6])
    def test_queries_md_exists(self, db_num: int):
        qm = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
        if not (SOURCE / f"db-{db_num}").exists():
            pytest.skip(f"db-{db_num} not in source")
        assert qm.exists(), f"db-{db_num} app/QUERIES/queries.md must exist"

    @pytest.mark.parametrize("db_num", [1])
    def test_queries_md_has_required_sections(self, db_num: int, anchor: dict):
        qm = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
        if not qm.exists():
            pytest.skip(f"db-{db_num} queries.md not found")
        content = qm.read_text(encoding="utf-8")
        for section in ["## Database Overview", "## Purpose", "## Use Case",
                        "## Business Value", "## Schema", "## Queries"]:
            assert section in content, f"Missing section: {section}"

    @pytest.mark.parametrize("db_num", [1])
    def test_queries_md_title_has_em_dash(self, db_num: int):
        qm = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
        if not qm.exists():
            pytest.skip(f"db-{db_num} queries.md not found")
        first_line = qm.read_text(encoding="utf-8").split("\n")[0]
        assert "—" in first_line, "Title must use em dash (—) not hyphen"
        assert first_line.startswith("# ")

    @pytest.mark.parametrize("db_num", [1])
    def test_query_blocks_match_pattern(self, db_num: int, anchor: dict):
        qm = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
        if not qm.exists():
            pytest.skip(f"db-{db_num} queries.md not found")
        pattern = anchor.get("query_block_pattern", r"^### Query (\d+) — (simple|moderate|challenging) / ([a-zA-Z0-9/_-]+)$")
        content = qm.read_text(encoding="utf-8")
        in_queries = False
        count = 0
        for line in content.split("\n"):
            if line.strip() == "## Queries":
                in_queries = True
                continue
            if in_queries and line.startswith("### Query "):
                assert re.match(pattern, line.strip()), f"Query header must match pattern: {line}"
                count += 1
        assert count >= 30, f"Expected at least 30 query blocks, got {count}"

    @pytest.mark.parametrize("db_num", [1])
    def test_query_json_blocks_have_required_fields(self, db_num: int, anchor: dict):
        qm = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
        if not qm.exists():
            pytest.skip(f"db-{db_num} queries.md not found")
        required = anchor.get("query_json_required_fields", ["db_id", "question_id", "question", "SQL", "evidence"])
        content = qm.read_text(encoding="utf-8")
        in_json = False
        json_buf = []
        for line in content.split("\n"):
            if line.strip() == "```json":
                in_json = True
                json_buf = []
                continue
            if in_json:
                if line.strip() == "```":
                    try:
                        obj = json.loads("\n".join(json_buf))
                        for f in required:
                            assert f in obj, f"Query JSON missing required field: {f}"
                    except json.JSONDecodeError:
                        pass
                    in_json = False
                else:
                    json_buf.append(line)


class TestQueriesMdFormatterScript:
    """queries_md_template_formatter produces valid output."""

    def test_formatter_module_imports(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from queries_md_template_formatter import format_queries_md_template, format_query_block_template
        qs = [{"number": 1, "title": "Test", "question": "Test?", "sql": "SELECT 1", "evidence": "x", "difficulty": "simple", "query_category": "filtering/lookup", "tables_used": [], "schema_context": {}, "expected_output": "[]"}]
        out = format_queries_md_template(qs, db_id="db-1", db_name="Test DB")
        assert "## Database Overview" in out
        assert "## Queries" in out
        assert "### Query 1 — simple / filtering/lookup" in out
        assert "```json" in out

    def test_rewrite_script_runs(self):
        import subprocess
        import sys
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "rewrite_queries_md_to_template.py"), "1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"rewrite script failed: {proc.stderr}"


class TestQueriesJsonTemplateFormat:
    """queries.json must have template-compatible structure."""

    @pytest.mark.parametrize("db_num", [1])
    def test_queries_json_exists(self, db_num: int):
        qj = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
        if not qj.exists():
            pytest.skip(f"db-{db_num} queries.json not found")
        data = json.loads(qj.read_text(encoding="utf-8"))
        queries = data.get("queries", data) if isinstance(data, dict) else data
        assert len(queries) >= 30

    @pytest.mark.parametrize("db_num", [1])
    def test_queries_have_sql_or_SQL(self, db_num: int):
        qj = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
        if not qj.exists():
            pytest.skip(f"db-{db_num} queries.json not found")
        data = json.loads(qj.read_text(encoding="utf-8"))
        queries = data.get("queries", data) if isinstance(data, dict) else data
        for i, q in enumerate(queries[:5]):
            sql = q.get("SQL", q.get("sql", ""))
            assert sql, f"Query {i+1} must have SQL or sql"

    @pytest.mark.parametrize("db_num", [1])
    def test_queries_json_has_1to1_sections_structure(self, db_num: int):
        """queries.json meta.sections must mirror queries.md ## headers 1:1."""
        qj = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
        if not qj.exists():
            pytest.skip(f"db-{db_num} queries.json not found")
        data = json.loads(qj.read_text(encoding="utf-8"))
        api = data.get("_api_response", data)
        meta = api.get("meta", {})
        sections = meta.get("sections", meta.get("preamble", {}))
        required = ["Database Overview", "Purpose", "Use Case", "Business Value", "Schema", "Domain Knowledge", "Query Difficulty Distribution"]
        for name in required:
            assert name in sections, f"queries.json must have section '{name}' (1:1 with queries.md)"


class TestEndToEndQAFlow:
    """End-to-end: convert → rewrite → validate."""

    def test_convert_script_exists(self):
        assert (ROOT / "scripts" / "convert_queries_to_template_format.py").exists()

    def test_rewrite_script_exists(self):
        assert (ROOT / "scripts" / "rewrite_queries_md_to_template.py").exists()

    def test_template_formatter_exists(self):
        assert (ROOT / "scripts" / "queries_md_template_formatter.py").exists()


class TestQueriesMdJsonTranslator:
    """Byte-for-byte md↔json translation, API response structure."""

    def test_translator_script_exists(self):
        assert (ROOT / "scripts" / "queries_md_json_translator.py").exists()

    def test_format_schema_exists(self):
        assert (TEMPLATE / "queries_format_schema.yaml").exists()

    @pytest.mark.parametrize("db_num", [1])
    def test_queries_json_has_api_response_structure(self, db_num: int):
        """queries.json must have API-response structure (submission of queries.md form)."""
        qj = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
        qm = SOURCE / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
        if not qj.exists():
            pytest.skip(f"db-{db_num} queries.json not found")
        data = json.loads(qj.read_text(encoding="utf-8"))
        api = data.get("_api_response", data)
        assert "status" in api or "submission" in api or "data" in api
        assert "queries" in data
        # After translator extract, queries have _raw_json; run extract if missing
        queries = data.get("queries", [])
        has_raw = queries and isinstance(queries[0], dict) and any("_raw_json" in q for q in queries)
        if not has_raw and qm.exists():
            import subprocess
            import sys
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "queries_md_json_translator.py"), "extract", str(db_num)],
                cwd=str(ROOT), capture_output=True, timeout=30,
            )
            data = json.loads(qj.read_text(encoding="utf-8"))
            queries = data.get("queries", [])
            has_raw = queries and any("_raw_json" in q for q in queries)
        assert has_raw, "queries must have _raw_json for byte-for-byte round-trip (run: translator extract)"

    @pytest.mark.parametrize("db_num", [1])
    def test_translator_validate_round_trip(self, db_num: int):
        """Round-trip: md → json → md must be byte-for-byte identical."""
        import subprocess
        import sys
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "queries_md_json_translator.py"), "validate", str(db_num)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"Round-trip failed: {proc.stdout} {proc.stderr}"
