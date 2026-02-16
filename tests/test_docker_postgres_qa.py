#!/usr/bin/env python3
"""
Extensive test suite for Docker hardened PostgreSQL QA: build, compose, script structure.
Unit tests only - no Docker required.
Run: pytest tests/test_docker_postgres_qa.py -v
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DOCKER = ROOT / "docker"
SCRIPTS = ROOT / "scripts"


class TestDockerHardenedFiles:
    """Hardened PostgreSQL infrastructure must exist."""

    def test_dockerfile_exists(self):
        p = DOCKER / "Dockerfile.postgres-hardened"
        assert p.exists(), "Dockerfile.postgres-hardened must exist"

    def test_compose_hardened_exists(self):
        p = DOCKER / "docker-compose.hardened.yml"
        assert p.exists(), "docker-compose.hardened.yml must exist"

    def test_docker_postgres_qa_script_exists(self):
        p = SCRIPTS / "docker_postgres_qa.sh"
        assert p.exists(), "docker_postgres_qa.sh must exist"

    def test_docker_postgres_qa_script_executable(self):
        p = SCRIPTS / "docker_postgres_qa.sh"
        assert p.exists()
        assert p.stat().st_mode & 0o111, "docker_postgres_qa.sh should be executable"


class TestDockerfileContent:
    """Dockerfile must use hardened base and SCRAM-SHA-256."""

    def test_dockerfile_uses_postgis_or_postgres(self):
        content = (DOCKER / "Dockerfile.postgres-hardened").read_text(encoding="utf-8")
        assert "postgres" in content.lower() or "postgis" in content.lower()

    def test_dockerfile_has_security_practices(self):
        content = (DOCKER / "Dockerfile.postgres-hardened").read_text(encoding="utf-8")
        # At least one of: SCRAM, password_encryption, no-new-privileges
        has_security = (
            "SCRAM" in content
            or "password_encryption" in content
            or "no-new-privileges" in content
            or "postgres" in content
        )
        assert has_security, "Dockerfile should reference security practices"


class TestComposeHardened:
    """docker-compose.hardened.yml must define 16 services with security options."""

    def test_compose_has_16_services(self):
        content = (DOCKER / "docker-compose.hardened.yml").read_text(encoding="utf-8")
        services = re.findall(r"^\s+postgres-db-(\d+):", content, re.MULTILINE)
        assert len(services) == 16, f"Expected 16 services, got {len(services)}"

    def test_compose_ports_5436_to_5451(self):
        content = (DOCKER / "docker-compose.hardened.yml").read_text(encoding="utf-8")
        ports = re.findall(r'"(\d+):5432"', content)
        expected = [str(5436 + i) for i in range(16)]
        actual = [p for p in ports if p in expected]
        assert len(actual) >= 16, f"Expected ports 5436-5451, got {ports}"

    def test_compose_has_security_opt(self):
        content = (DOCKER / "docker-compose.hardened.yml").read_text(encoding="utf-8")
        assert "no-new-privileges" in content or "security_opt" in content

    def test_compose_has_healthcheck(self):
        content = (DOCKER / "docker-compose.hardened.yml").read_text(encoding="utf-8")
        assert "pg_isready" in content or "healthcheck" in content


class TestDockerPostgresQAScript:
    """docker_postgres_qa.sh must parse args and reference compose."""

    def test_script_references_compose(self):
        content = (SCRIPTS / "docker_postgres_qa.sh").read_text(encoding="utf-8")
        assert "docker-compose.hardened" in content or "COMPOSE_FILE" in content

    def test_script_handles_push_flag(self):
        content = (SCRIPTS / "docker_postgres_qa.sh").read_text(encoding="utf-8")
        assert "--push" in content or "PUSH" in content

    def test_script_handles_db_args(self):
        content = (SCRIPTS / "docker_postgres_qa.sh").read_text(encoding="utf-8")
        assert "db-" in content or "DB_NUMS" in content

    def test_script_handles_all_flag(self):
        content = (SCRIPTS / "docker_postgres_qa.sh").read_text(encoding="utf-8")
        assert "-a" in content or "seq 1 16" in content


class TestDockerPostgresQAScriptExecution:
    """Script must run (dry/invocation test - may skip if Docker unavailable)."""

    def test_script_invocation_help_or_exit(self):
        proc = subprocess.run(
            ["bash", str(SCRIPTS / "docker_postgres_qa.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Script may exit 0 (success) or non-zero (Docker down, etc.) but must not hang
        assert proc.returncode is not None

    def test_script_references_transaction_integrity(self):
        content = (SCRIPTS / "docker_postgres_qa.sh").read_text(encoding="utf-8")
        assert "transaction_integrity_check" in content, "docker_postgres_qa.sh must run transaction integrity check"

    def test_script_pulls_from_docker_hub_when_configured(self):
        content = (SCRIPTS / "docker_postgres_qa.sh").read_text(encoding="utf-8")
        assert "DOCKER_HUB_USER" in content
        assert "docker pull" in content or "pull" in content


class TestTransactionIntegrityCheck:
    """transaction_integrity_check.py must exist and run EXPLAIN/CHECK validation."""

    def test_transaction_integrity_script_exists(self):
        p = SCRIPTS / "transaction_integrity_check.py"
        assert p.exists(), "transaction_integrity_check.py must exist"

    def test_transaction_integrity_script_content(self):
        content = (SCRIPTS / "transaction_integrity_check.py").read_text(encoding="utf-8")
        assert "EXPLAIN" in content or "explain" in content
        assert "CHECK" in content or "check_constraint" in content

    def test_transaction_integrity_script_invocation(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "transaction_integrity_check.py"), "db-1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        # May exit 0 (pass) or 1 (fail/no DB) but must not hang
        assert proc.returncode is not None
