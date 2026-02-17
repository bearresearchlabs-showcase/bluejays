#!/usr/bin/env python3
"""
TDD/BDD tests for DOCUMENTATION workflow consistency across source/db-N.
Ensures each db-N has: valid config (YAML vs JSON schema), generable README.md,
required sections (installation, specs, schema, data dictionary).

Run: pytest tests/test_documentation_workflow.py -v
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
TEMPLATE = ROOT / "template"
SCHEMAS = ROOT / "scripts" / "schemas"
SCRIPT = ROOT / "scripts" / "generate_documentation_readme.py"


DB_NUMS = list(range(1, 17))


SKELETON = TEMPLATE / "DOCUMENTATION_README_SKELETON.md"

# Required section markers in order (for skeleton comparison)
REQUIRED_SECTIONS_ORDER = [
    "---",
    "title:",
    "description:",
    "database:",
    "---",
    "# ",
    "**Database:**",
    "**Content:**",
    "## Installation Guide",
    "### Step 1:",
    "### Step 2:",
    "### Step 3:",
    "### Step 4:",
    "## Specifications",
    "## Schema Overview",
    "**Total tables:**",
    "## Data Dictionary",
]


class TestDocumentationSchemaAndTemplate:
    """Schema and template must exist and be valid."""

    def test_documentation_skeleton_exists(self):
        """Skeleton file must exist for DOCUMENTATION/README comparison."""
        assert SKELETON.exists(), "template/DOCUMENTATION_README_SKELETON.md must exist"

    def test_db_documentation_schema_exists(self):
        schema = SCHEMAS / "db_documentation.schema.json"
        assert schema.exists(), "scripts/schemas/db_documentation.schema.json must exist"

    def test_db_documentation_template_exists(self):
        template = TEMPLATE / "db_documentation_template.yaml"
        assert template.exists(), "template/db_documentation_template.yaml must exist"

    def test_schema_validates_template(self):
        """Given template YAML, when validated against schema, then it must pass."""
        schema_path = SCHEMAS / "db_documentation.schema.json"
        template_path = TEMPLATE / "db_documentation_template.yaml"
        if not schema_path.exists() or not template_path.exists():
            pytest.skip("Schema or template missing")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--validate", "db-1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"Template must validate: {proc.stderr}"


class TestDocumentationConfigValidation:
    """Each db-N config must validate against JSON schema (BDD: Given db-N, When validate, Then pass)."""

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_db_n_config_validates(self, n: int):
        """Given source/db-N, when validating doc config, then validation must pass."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--validate", f"db-{n}"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"db-{n} config must validate: {proc.stderr}"


class TestDocumentationGeneration:
    """README.md must be generable for each db-N with required structure."""

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_db_n_generates_readme(self, n: int):
        """Given source/db-N, when generating README, then docs/README.md must be created."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), f"db-{n}"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"db-{n} must generate README: {proc.stderr}"
        readme = SOURCE / f"db-{n}" / "docs" / "README.md"
        assert readme.exists(), f"db-{n} docs/README.md must exist after generate"

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_readme_has_required_sections(self, n: int):
        """Given db-N docs/README.md, when inspecting content, then required sections must exist."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        readme = SOURCE / f"db-{n}" / "docs" / "README.md"
        if not readme.exists():
            pytest.skip(f"db-{n} docs/README.md not found (run generate first)")
        content = readme.read_text(encoding="utf-8")
        required = [
            ("## Installation Guide", "installation guide"),
            ("## Specifications", "specifications"),
            ("## Schema Overview", "schema overview"),
            ("## Data Dictionary", "data dictionary"),
        ]
        for marker, name in required:
            assert marker in content, f"db-{n} README must have {name} section"

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_readme_has_no_sql_queries(self, n: int):
        """Given db-N docs/README.md, when inspecting content, then no ```sql blocks must exist."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        readme = SOURCE / f"db-{n}" / "docs" / "README.md"
        if not readme.exists():
            pytest.skip(f"db-{n} docs/README.md not found")
        content = readme.read_text(encoding="utf-8")
        sql_blocks = re.findall(r"```sql\s*[\s\S]*?```", content)
        assert len(sql_blocks) == 0, f"db-{n} README must have no SQL blocks (found {len(sql_blocks)} blocks)"

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_readme_has_database_id(self, n: int):
        """Given db-N docs/README.md, when inspecting content, then db-N id must be present."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        readme = SOURCE / f"db-{n}" / "docs" / "README.md"
        if not readme.exists():
            pytest.skip(f"db-{n} docs/README.md not found")
        content = readme.read_text(encoding="utf-8")
        assert f"db-{n}" in content, f"db-{n} README must reference db-{n}"

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_readme_has_mdx_frontmatter(self, n: int):
        """Given db-N docs/README.md, when inspecting content, then MDX-compatible YAML frontmatter must exist."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        readme = SOURCE / f"db-{n}" / "docs" / "README.md"
        if not readme.exists():
            pytest.skip(f"db-{n} docs/README.md not found")
        content = readme.read_text(encoding="utf-8")
        assert content.startswith("---\n"), f"db-{n} README must start with MDX frontmatter (---)"
        assert "title:" in content[:500], f"db-{n} README frontmatter must have title"
        assert "description:" in content[:500], f"db-{n} README frontmatter must have description"
        assert f"database: db-{n}" in content[:500], f"db-{n} README frontmatter must have database: db-{n}"

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_readme_matches_skeleton_structure(self, n: int):
        """Given db-N docs/README.md, when comparing to skeleton, then required sections must appear in order."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        readme = SOURCE / f"db-{n}" / "docs" / "README.md"
        if not readme.exists():
            pytest.skip(f"db-{n} docs/README.md not found")
        content = readme.read_text(encoding="utf-8")
        pos = 0
        for marker in REQUIRED_SECTIONS_ORDER:
            idx = content.find(marker, pos)
            assert idx >= 0, f"db-{n} README must have '{marker}' (skeleton section missing or out of order)"
            pos = idx + len(marker)


class TestDocumentationPropagation:
    """Populate and resync must propagate README consistently."""

    def test_populate_produces_app_documentation_readme(self):
        """Given populate run, when db-1 has docs/README.md, then app/DOCUMENTATION/README.md must exist."""
        # Ensure docs/README exists
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "db-1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            pytest.skip("generate failed for db-1")
        # Run populate
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "populate_app_trifecta.py"), "db-1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert proc.returncode == 0, f"Populate failed: {proc.stderr}"
        app_readme = SOURCE / "db-1" / "app" / "DOCUMENTATION" / "README.md"
        assert app_readme.exists(), "app/DOCUMENTATION/README.md must exist after populate"

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_app_documentation_readme_only(self, n: int):
        """Given populate -a, when app exists, then DOCUMENTATION must have README.md only."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        app_doc = SOURCE / f"db-{n}" / "app" / "DOCUMENTATION"
        if not app_doc.exists():
            pytest.skip(f"db-{n} app/DOCUMENTATION not yet populated")
        assert (app_doc / "README.md").exists(), f"db-{n} DOCUMENTATION must have README.md"
        # DOCUMENTATION must contain only README.md
        files = [f.name for f in app_doc.iterdir() if f.is_file()]
        assert files == ["README.md"], f"db-{n} DOCUMENTATION must have only README.md, got {files}"


class TestDocumentationConsistency:
    """All db-N must have consistent documentation structure."""

    @pytest.mark.parametrize("n", DB_NUMS)
    def test_db_n_can_load_config(self, n: int):
        """Given db-N, when loading config (template + optional _doc_config), then config must load."""
        if not (SOURCE / f"db-{n}").exists():
            pytest.skip(f"source/db-{n} not found")
        # Validation implies config loads; run validate
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--validate", f"db-{n}"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, f"db-{n} config must load and validate: {proc.stderr}"
