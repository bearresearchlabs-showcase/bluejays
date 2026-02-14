#!/usr/bin/env python3
"""
Tests for refactored scripts: integrity_checks, scrub_keywords, db_check parse_db_args.
Run: pytest tests/test_scripts_refactor.py -v
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
CHECKSUM_BIN = SCRIPTS / "bin" / "checksum" / "target" / "release" / "checksum"


class TestIntegrityChecks:
    """Tests for integrity_checks.py."""

    def test_compute_file_checksums_returns_dict(self):
        sys.path.insert(0, str(SCRIPTS))
        from integrity_checks import compute_file_checksums

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"test")
            path = Path(f.name)
        try:
            result = compute_file_checksums(path)
            assert result is not None
            assert "crc32" in result
            assert "crc64" in result
            assert "sha256" in result
            assert result["crc32"].startswith("0x")
            assert result["crc64"].startswith("0x")
            assert len(result["sha256"]) == 64
        finally:
            path.unlink(missing_ok=True)

    def test_compute_file_checksums_known_value(self):
        sys.path.insert(0, str(SCRIPTS))
        from integrity_checks import compute_file_checksums

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"test")
            path = Path(f.name)
        try:
            result = compute_file_checksums(path)
            assert result["crc32"] == "0xd87f7e0c"
            assert result["sha256"] == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        finally:
            path.unlink(missing_ok=True)

    def test_compute_file_checksums_nonexistent_returns_none(self):
        sys.path.insert(0, str(SCRIPTS))
        from integrity_checks import compute_file_checksums

        result = compute_file_checksums(Path("/nonexistent/file.txt"))
        assert result is None


class TestScrubKeywords:
    """Tests for scrub_keywords.py."""

    def test_load_config_returns_dict(self):
        sys.path.insert(0, str(SCRIPTS))
        from scrub_keywords import load_config

        config_path = ROOT / ".cursor" / "scrub_config.yaml"
        if not config_path.exists():
            pytest.skip("scrub_config.yaml not found")
        config = load_config(config_path)
        assert isinstance(config, dict)

    def test_build_clean_fn_identity_when_no_patterns(self):
        sys.path.insert(0, str(SCRIPTS))
        from scrub_keywords import build_clean_fn

        clean = build_clean_fn({})
        assert clean("hello") == "hello"

    def test_build_clean_fn_applies_pattern(self):
        sys.path.insert(0, str(SCRIPTS))
        from scrub_keywords import build_clean_fn

        config = {"patterns": [{"find": r"\bfoo\b", "replace": "bar", "regex": True}]}
        clean = build_clean_fn(config)
        assert clean("foo bar") == "bar bar"

    def test_get_keywords_from_config(self):
        sys.path.insert(0, str(SCRIPTS))
        from scrub_keywords import get_keywords

        config = {"keywords": "databricks|snowflake"}
        kw = get_keywords(config)
        assert "databricks" in kw or "|" in kw


class TestDbCheckParseArgs:
    """Tests for db_check.parse_db_args."""

    def test_parse_db_args_empty(self):
        sys.path.insert(0, str(SCRIPTS))
        from db_check import parse_db_args

        assert parse_db_args([]) == []

    def test_parse_db_args_single(self):
        sys.path.insert(0, str(SCRIPTS))
        from db_check import parse_db_args

        assert parse_db_args(["db-1"]) == [1]
        assert parse_db_args(["1"]) == [1]

    def test_parse_db_args_range(self):
        sys.path.insert(0, str(SCRIPTS))
        from db_check import parse_db_args

        assert parse_db_args(["db-1", "db-5"]) == [1, 2, 3, 4, 5]

    def test_parse_db_args_all(self):
        sys.path.insert(0, str(SCRIPTS))
        from db_check import parse_db_args

        result = parse_db_args(["-a"])
        assert len(result) == 16
        assert result == list(range(1, 17))


class TestChecksumBinaryParity:
    """Integration: checksum binary output matches Python when built."""

    def test_checksum_binary_matches_python(self):
        if not CHECKSUM_BIN.exists():
            pytest.skip("checksum binary not built (run: make build-bin)")
        sys.path.insert(0, str(SCRIPTS))
        from integrity_checks import compute_file_checksums

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"parity-test-data")
            path = Path(f.name)
        try:
            # Python result
            py_result = compute_file_checksums(path)
            assert py_result is not None

            # Binary result
            proc = subprocess.run(
                [str(CHECKSUM_BIN), str(path)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            assert proc.returncode == 0
            bin_result = json.loads(proc.stdout.strip())

            assert py_result["crc32"] == bin_result["crc32"]
            assert py_result["crc64"] == bin_result["crc64"]
            assert py_result["sha256"] == bin_result["sha256"]
        finally:
            path.unlink(missing_ok=True)
