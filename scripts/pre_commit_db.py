#!/usr/bin/env python3
"""
Pre-commit hook for DB format and structure checks.
Runs on staged db-*/ and client/db/ paths.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    from db_logger import log
except ImportError:
    def log(*a, **k): pass


def get_staged_db_paths() -> list:
    """Get list of staged paths matching db-*/ or client/db/."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        if out.returncode != 0:
            return []
        paths = [p.strip() for p in out.stdout.splitlines() if p.strip()]
    except (FileNotFoundError, subprocess.SubprocessError):
        return []

    db_paths = []
    for p in paths:
        if p.startswith("db-") and "/" in p:
            db_part = p.split("/")[0]
            if db_part.startswith("db-") and db_part[3:].isdigit():
                db_paths.append(db_part)
        elif p.startswith("client/db/"):
            parts = p.split("/")
            if len(parts) >= 3 and parts[2].startswith("db-"):
                db_paths.append(parts[2])
    return sorted(set(db_paths))


def check_db_structure(db_name: str) -> Tuple[bool, List[str]]:
    """Check required files exist for a database. Returns (ok, issues)."""
    db_dir = ROOT / db_name
    issues = []
    if not db_dir.exists():
        return False, [f"{db_name} directory not found"]

    # schema.sql or schema_postgresql.sql
    schema = db_dir / "data" / "schema.sql"
    schema_pg = db_dir / "data" / "schema_postgresql.sql"
    if not schema.exists() and not schema_pg.exists():
        issues.append(f"{db_name}: No schema.sql or schema_postgresql.sql")

    # queries.json
    qj = db_dir / "queries" / "queries.json"
    if not qj.exists():
        issues.append(f"{db_name}: queries.json missing")
    else:
        try:
            data = json.loads(qj.read_text(encoding="utf-8"))
            cnt = len(data.get("queries", []))
            if cnt != 30:
                issues.append(f"{db_name}: queries.json has {cnt} queries, expected 30")
        except (json.JSONDecodeError, OSError) as e:
            issues.append(f"{db_name}: queries.json invalid - {e}")

    # queries.md
    qm = db_dir / "queries" / "queries.md"
    if not qm.exists():
        issues.append(f"{db_name}: queries.md missing")

    return len(issues) == 0, issues


def check_integrity_quick(db_name: str) -> Tuple[bool, List[str]]:
    """Quick CRC-32 check on schema and queries.json."""
    try:
        from integrity_checks import compute_file_checksums
    except ImportError as e:
        return False, [f"integrity_checks module required: {e}"]

    db_dir = ROOT / db_name
    issues = []
    for name, rel in [("schema", "data/schema.sql"), ("queries", "queries/queries.json")]:
        path = db_dir / rel
        if path.exists():
            cs = compute_file_checksums(path)
            if not cs:
                issues.append(f"{db_name}: Could not checksum {rel}")
    return len(issues) == 0, issues


def main() -> int:
    staged = get_staged_db_paths()
    log("pre_commit", "run", status="start", data={"staged_count": len(staged), "staged": staged})
    if not staged:
        log("pre_commit", "run", status="ok", message="No staged db paths")
        return 0  # Nothing to check

    all_ok = True
    for db_name in staged:
        ok, issues = check_db_structure(db_name)
        if not ok:
            for i in issues:
                print(i)
            all_ok = False
        ok2, issues2 = check_integrity_quick(db_name)
        if not ok2:
            for i in issues2:
                print(i)
            all_ok = False

    log("pre_commit", "run", status="ok" if all_ok else "fail", data={"passed": all_ok})
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
