#!/usr/bin/env python3
"""
PostgreSQL-only schema validator.

Scans all schema*.sql and *_schema.sql files in source/db-N.
Fails (exit 1) if TIMESTAMP_NTZ, VARIANT, CURRENT_TIMESTAMP(), ARRAY<, MAP< found.
Does NOT generate *_postgresql.sql files — repo is PostgreSQL-only.

Usage:
    python scripts/generate_postgresql_sql_files.py [db-1] [db-5] | -a
    python scripts/db_check.py schema-postgresql-validate
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
EXCLUDE_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".cursor"}

# Non-PostgreSQL types — fail if found
NON_PG_PATTERNS = [
    (r"\bTIMESTAMP_NTZ\b", "TIMESTAMP_NTZ"),
    (r"\bVARIANT\b", "VARIANT"),
    (r"\bCURRENT_TIMESTAMP\s*\(\s*\)", "CURRENT_TIMESTAMP()"),
    (r"\bARRAY\s*<", "ARRAY<"),
    (r"\bMAP\s*<", "MAP<"),
]


def get_schema_files(root: Path) -> list[Path]:
    """Return schema SQL files to validate."""
    files = []
    for pattern in ["schema*.sql", "*_schema.sql", "schema_extensions.sql"]:
        for p in root.glob(pattern):
            if any(part in p.parts for part in EXCLUDE_DIRS):
                continue
            if p.suffix == ".sql" and p not in files:
                files.append(p)
    return sorted(files)


def validate_schema_file(path: Path) -> list[str]:
    """Return list of violation type names found in content."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return ["read_error"]
    violations = []
    for pat, name in NON_PG_PATTERNS:
        if re.search(pat, content, re.IGNORECASE):
            violations.append(name)
    return violations


def validate_db(db_num: int) -> tuple[bool, list[tuple[str, list[str]]]]:
    """Validate schema files for one db-N. Returns (ok, [(rel_path, violations), ...])."""
    db_dir = SOURCE / f"db-{db_num}"
    if not db_dir.exists():
        return True, []
    data_dir = db_dir / "data"
    app_db = db_dir / "app" / "DATABASE"
    deliv_data = db_dir / "deliverable" / "data"
    bases = [d for d in (data_dir, app_db, deliv_data) if d.exists()]
    all_violations = []
    for base in bases:
        for f in get_schema_files(base):
            violations = validate_schema_file(f)
            if violations:
                rel = f.relative_to(ROOT)
                all_violations.append((str(rel), violations))
    return len(all_violations) == 0, all_violations


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Validate schema files are PostgreSQL-only")
    ap.add_argument("-a", "--all", action="store_true", help="Validate all db-1..db-16")
    ap.add_argument("dbs", nargs="*", type=int, help="db numbers (e.g. 1 5)")
    args = ap.parse_args()

    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = args.dbs

    total_ok = True
    for n in db_nums:
        ok, violations = validate_db(n)
        if not ok:
            total_ok = False
            for rel, vlist in violations:
                print(f"  {rel}: {', '.join(vlist)}", file=sys.stderr)

    if total_ok:
        print("Schema PostgreSQL validation: PASS")
        return 0
    print("Schema PostgreSQL validation: FAIL (non-PostgreSQL types found)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
