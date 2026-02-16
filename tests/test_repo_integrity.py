#!/usr/bin/env python3
"""
Repo integrity tests: ensure no dead artifacts, duplicates, or corrupt files.
Run: pytest tests/test_repo_integrity.py -v
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

# Directories to skip when scanning (build caches, deps, generated)
SKIP_DIRS = {
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "venv_selenium",
    "__pycache__",
    ".pytest_cache",
    ".next",
    "coverage",
    "htmlcov",
    ".turbo",
    "dist",
    "build",
    ".swc",
    "playwright-report",
    "test-results",
}

# Paths to exclude from duplicate/backup checks (historical, intentional)
EXCLUDE_FROM_ARTIFACT_CHECKS = {"archive"}


def _should_skip(p: Path) -> bool:
    return any(part in p.parts for part in SKIP_DIRS)


def _iter_tracked_files() -> list[Path]:
    """Yield paths under ROOT, excluding SKIP_DIRS."""
    found: list[Path] = []
    for f in ROOT.rglob("*"):
        if not f.is_file() or _should_skip(f):
            continue
        try:
            found.append(f.relative_to(ROOT))
        except ValueError:
            pass
    return found


class TestNoDeadArtifacts:
    """No duplicate, corrupt, or backup artifacts in repo."""

    def test_no_duplicate_filenames_with_space_and_number(self):
        """No 'X 2.ts', 'data 2.sql' style duplicates (common copy-paste artifacts)."""
        pattern = re.compile(r"^(.+)\s+(\d+)(\.[a-zA-Z0-9]+)?$")
        violations: list[str] = []
        for rel in _iter_tracked_files():
            if any(part in rel.parts for part in EXCLUDE_FROM_ARTIFACT_CHECKS):
                continue
            if pattern.match(rel.name):
                violations.append(str(rel))
        assert not violations, (
            f"Found duplicate-style filenames (remove or rename): {violations}"
        )

    def test_no_corrupt_temp_filenames(self):
        """No .!*! patterns (macOS/incomplete download temp files)."""
        pattern = re.compile(r"^\.![^!]+!")
        violations: list[str] = []
        for rel in _iter_tracked_files():
            if pattern.match(rel.name):
                violations.append(str(rel))
        assert not violations, (
            f"Found corrupt temp filenames (remove): {violations}"
        )

    def test_no_debug_artifacts_in_scripts(self):
        """No debug_*.py or test_one_off.py in scripts/ (per repo-organization.mdc)."""
        scripts_dir = ROOT / "scripts"
        if not scripts_dir.exists():
            pytest.skip("scripts/ not found")
        violations: list[str] = []
        for f in scripts_dir.rglob("*.py"):
            if _should_skip(f):
                continue
            name = f.name
            if name.startswith("debug_") and name.endswith(".py"):
                violations.append(str(f.relative_to(ROOT)))
            if name == "test_one_off.py":
                violations.append(str(f.relative_to(ROOT)))
        assert not violations, (
            f"scripts/ must not contain debug artifacts: {violations}"
        )

    def test_no_backup_copies_in_repo(self):
        """No *.backup, *.bak, *_old, *_copy in non-archive paths."""
        pattern = re.compile(
            r"\.(backup|bak|bak2)(\.|$)|_old(\.|$)|_copy(\.|$)",
            re.IGNORECASE,
        )
        violations: list[str] = []
        for rel in _iter_tracked_files():
            if any(part in rel.parts for part in EXCLUDE_FROM_ARTIFACT_CHECKS):
                continue
            if pattern.search(rel.name):
                violations.append(str(rel))
        assert not violations, (
            f"Found backup/copy artifacts (use git history instead): {violations}"
        )


class TestGitignoreCoversArtifacts:
    """Critical artifact dirs are in .gitignore."""

    def test_gitignore_has_playwright_report(self):
        """playwright-report/ should be ignored."""
        gitignore = ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore missing"
        content = gitignore.read_text(encoding="utf-8")
        assert "playwright-report" in content, (
            "Add playwright-report/ to .gitignore"
        )

    def test_gitignore_has_test_results(self):
        """test-results/ should be ignored."""
        gitignore = ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore missing"
        content = gitignore.read_text(encoding="utf-8")
        assert "test-results" in content, (
            "Add test-results/ to .gitignore"
        )
