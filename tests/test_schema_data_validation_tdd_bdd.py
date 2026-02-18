#!/usr/bin/env python3
"""
TDD/BDD/DDD tests for schema.sql and data.sql validation.

- TDD: Unit tests for size, PostgreSQL compliance, naming
- BDD: Acceptance scenarios (Given/When/Then)
- DDD: Bounded context (each db-N schema stays PostgreSQL-only)

Run: pytest tests/test_schema_data_validation_tdd_bdd.py -v
"""
import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from db_paths import get_data_dir, get_primary_data_path

MIN_DATA_SQL_TOTAL_BYTES = int(os.environ.get("MIN_DATA_SQL_TOTAL_BYTES", 1073741824))  # 1GB
REPO_HEALTH_LENIENT = os.environ.get("REPO_HEALTH_LENIENT", "0") == "1"

# Non-PostgreSQL types to flag (Snowflake, Databricks, etc.)
# Exclude OBJECT - JSON_OBJECT_AGG/JSON_OBJECT are valid PG functions
NON_PG_TYPE_PATTERNS = [
    r"\bTIMESTAMP_NTZ\b",
    r"\bVARIANT\b",
    r"\bARRAY\s*<",
    r"\bMAP\s*<",
]

SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def get_data_sql_paths() -> list[tuple[str, Path]]:
    """Return (db_id, path) for each db's primary data file (data_large >= 1GB or data.sql)."""
    result = []
    for n in range(1, 17):
        db_dir = SOURCE / f"db-{n}"
        if not db_dir.exists():
            continue
        data_dir = get_data_dir(db_dir)
        primary = get_primary_data_path(data_dir)
        if primary:
            result.append((f"db-{n}", primary[1]))
    return result


def total_data_sql_bytes() -> int:
    """Sum bytes of all data.sql/data_large.sql (one per db, no double count)."""
    seen = set()
    total = 0
    for db_id, p in get_data_sql_paths():
        if db_id in seen:
            continue
        seen.add(db_id)
        total += p.stat().st_size
    return total


def get_schema_paths() -> list[tuple[str, Path]]:
    """Return (db_id, path) for each db's schema.sql."""
    result = []
    for n in range(1, 17):
        db_dir = SOURCE / f"db-{n}"
        if not db_dir.exists():
            continue
        data_dir = get_data_dir(db_dir)
        if not data_dir.exists():
            continue
        for name in ["schema.sql"]:
            p = data_dir / name
            if p.exists() and p.is_file():
                result.append((f"db-{n}", p))
                break
    return result


def check_schema_postgresql_compliant(content: str) -> list[str]:
    """Return list of non-PG type violations."""
    violations = []
    for pat in NON_PG_TYPE_PATTERNS:
        if re.search(pat, content, re.IGNORECASE):
            violations.append(f"Non-PostgreSQL type: {pat.strip()}")
    return violations


def extract_table_names_from_schema(content: str) -> list[str]:
    """Extract CREATE TABLE names (supports schema-qualified: public.models)."""
    tables = []
    for m in re.finditer(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)",
        content,
        re.IGNORECASE,
    ):
        tables.append(m.group(1).lower())
    return tables


def check_snake_case(names: list[str]) -> list[str]:
    """Return names that don't match snake_case."""
    return [n for n in names if n and not SNAKE_CASE_RE.match(n)]


# ---------------------------------------------------------------------------
# TDD: Unit tests
# ---------------------------------------------------------------------------


class TestDataSqlSizeTDD:
    """TDD: data.sql total size >= 1GB."""

    def test_data_sql_total_size_at_least_1gb(self):
        total = total_data_sql_bytes()
        if REPO_HEALTH_LENIENT:
            pytest.skip("REPO_HEALTH_LENIENT=1: skip strict size check")
        assert total >= MIN_DATA_SQL_TOTAL_BYTES, (
            f"Total data.sql bytes {total} < {MIN_DATA_SQL_TOTAL_BYTES} (1GB). "
            "Set REPO_HEALTH_LENIENT=1 to skip during migration."
        )

    def test_data_sql_paths_resolved(self):
        paths = get_data_sql_paths()
        assert isinstance(paths, list)
        for db_id, p in paths:
            assert p.exists()
            assert "db-" in db_id


class TestSchemaPostgresqlCompliantTDD:
    """TDD: schema.sql is PostgreSQL compliant."""

    def test_schema_sql_has_create_table(self):
        for db_id, p in get_schema_paths():
            content = p.read_text(encoding="utf-8")
            assert "CREATE TABLE" in content.upper(), f"{db_id}: schema has no CREATE TABLE"

    def test_schema_sql_postgresql_compliant(self):
        for db_id, p in get_schema_paths():
            content = p.read_text(encoding="utf-8")
            violations = check_schema_postgresql_compliant(content)
            if REPO_HEALTH_LENIENT and violations:
                pytest.skip(f"REPO_HEALTH_LENIENT: {db_id} has {violations}")
            assert not violations, f"{db_id}: {violations}"

    def test_schema_naming_snake_case(self):
        for db_id, p in get_schema_paths():
            content = p.read_text(encoding="utf-8")
            tables = extract_table_names_from_schema(content)
            bad = check_snake_case(tables)
            assert not bad, f"{db_id}: tables not snake_case: {bad}"


class TestDataSqlContentTDD:
    """TDD: data.sql has valid INSERT/COPY."""

    def test_data_sql_valid_insert_or_copy(self):
        for db_id, p in get_data_sql_paths():
            content = p.read_text(encoding="utf-8", errors="replace")
            assert "INSERT" in content.upper() or "COPY" in content.upper(), f"{db_id}: data.sql has no INSERT/COPY"


class TestSchemaDataNamingConsistentTDD:
    """TDD: data.sql INSERT targets exist in schema (spot-check)."""

    def test_schema_data_naming_consistent(self):
        for db_id, p in get_data_sql_paths():
            schema_paths = [sp for did, sp in get_schema_paths() if did == db_id]
            if not schema_paths:
                continue
            schema_tables = set(extract_table_names_from_schema(schema_paths[0].read_text()))
            data_content = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"(?:INSERT\s+INTO|COPY)\s+(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)", data_content, re.IGNORECASE):
                tbl = m.group(1).lower()
                assert tbl in schema_tables, f"{db_id}: data references table '{tbl}' not in schema"
                break  # Spot-check first only


# ---------------------------------------------------------------------------
# BDD: Acceptance scenarios
# ---------------------------------------------------------------------------


class TestSchemaDataValidationBDD:
    """BDD: Given/When/Then scenarios."""

    def test_given_source_exists_when_data_summed_then_total_meets_threshold(self):
        """Scenario: Data volume meets 1GB total."""
        paths = get_data_sql_paths()
        if not paths:
            pytest.skip("No data.sql files found")
        total = total_data_sql_bytes()
        if REPO_HEALTH_LENIENT:
            assert total >= 0
        else:
            assert total >= MIN_DATA_SQL_TOTAL_BYTES

    def test_given_schema_exists_when_parsed_then_no_non_pg_syntax(self):
        """Scenario: Schema is PostgreSQL compliant."""
        for db_id, p in get_schema_paths():
            content = p.read_text(encoding="utf-8")
            violations = check_schema_postgresql_compliant(content)
            if REPO_HEALTH_LENIENT and violations:
                pytest.skip(f"REPO_HEALTH_LENIENT: {db_id} has {violations}")
            assert not violations, f"{db_id}: {violations}"

    def test_given_schema_and_data_when_naming_checked_then_snake_case(self):
        """Scenario: Naming is consistent (snake_case)."""
        for db_id, p in get_schema_paths():
            content = p.read_text(encoding="utf-8")
            tables = extract_table_names_from_schema(content)
            bad = check_snake_case(tables)
            assert not bad, f"{db_id}: {bad}"


# ---------------------------------------------------------------------------
# DDD: Bounded context tests
# ---------------------------------------------------------------------------


class TestDbBoundedContextDDD:
    """DDD: Each db-N is a bounded context; schema stays PostgreSQL domain."""

    def test_db_bounded_context_schema_only_postgres(self):
        """Each db-N schema stays within PostgreSQL domain."""
        for db_id, p in get_schema_paths():
            content = p.read_text(encoding="utf-8")
            violations = check_schema_postgresql_compliant(content)
            if REPO_HEALTH_LENIENT and violations:
                pytest.skip(f"REPO_HEALTH_LENIENT: {db_id} has {violations}")
            assert not violations, f"{db_id} schema has non-PG types: {violations}"

    def test_db_bounded_context_data_matches_schema(self):
        """data.sql INSERT targets exist in schema (spot-check first 5)."""
        for db_id, p in get_data_sql_paths():
            schema_paths = [sp for did, sp in get_schema_paths() if did == db_id]
            if not schema_paths:
                continue
            schema_tables = set(extract_table_names_from_schema(schema_paths[0].read_text()))
            data_content = p.read_text(encoding="utf-8", errors="replace")
            found = []
            for m in re.finditer(r"(?:INSERT\s+INTO|COPY)\s+(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)", data_content, re.IGNORECASE):
                tbl = m.group(1).lower()
                found.append(tbl)
                if len(found) >= 5:
                    break
            for tbl in found[:5]:
                assert tbl in schema_tables, f"{db_id}: data references table {tbl} not in schema"
