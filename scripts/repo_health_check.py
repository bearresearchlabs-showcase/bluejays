#!/usr/bin/env python3
"""
Repo health checker: data size, schema compliance, naming, unnecessary files.

Output: results/repo_health.json
Checks:
- Data size: total data.sql >= 1GB (configurable)
- Schema: PostgreSQL compliant, CREATE TABLE, snake_case
- Unnecessary files in source/db-N (not needed for app/ compilation)
- Unnecessary files at repo root (not in canonical list)

Usage:
    python3 scripts/repo_health_check.py
    python3 scripts/repo_health_check.py --lenient  # Warn, don't fail
    MIN_DATA_SQL_TOTAL_BYTES=0 REPO_HEALTH_LENIENT=1 python3 scripts/repo_health_check.py
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
RESULTS = ROOT / "results"

MIN_DATA_SQL_TOTAL_BYTES = int(os.environ.get("MIN_DATA_SQL_TOTAL_BYTES", 1073741824))  # 1GB

# Required for app/ compilation (populate_app_trifecta)
REQUIRED_DB_FILES = {
    "data/schema.sql",
    "data/data.sql",
    "data/data_large.sql",
    "data/data_large_postgresql.sql",
    "queries/queries.json",
    "queries/queries.md",
    "queries_header.yaml",
    "queries_header.json",
}
REQUIRED_DB_DIRS = {"data", "queries", "app"}

# Canonical root-level dirs and files
CANONICAL_ROOT_DIRS = {
    "source", "client", "template", "scripts", "tests", "docker", "notebooks",
    "docs", ".cursor", "apps", "packages", "data", "results", "logs", "research",
    "components", "lib", "workbench", "bird_export",
}
CANONICAL_ROOT_FILES = {
    "pyproject.toml", "Makefile", "README.md", ".gitignore", "requirements.txt",
    "package.json", "turbo.json", "vercel.json",
}

NON_PG_TYPE_PATTERNS = [
    (r"\bTIMESTAMP_NTZ\b", "TIMESTAMP_NTZ"),
    (r"\bVARIANT\b", "VARIANT"),
    (r"\bARRAY\s*<", "ARRAY<"),
    (r"\bMAP\s*<", "MAP<"),
]
SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def get_est_timestamp() -> str:
    try:
        from timestamp_utils import get_est_timestamp as _get
        return _get()
    except ImportError:
        from datetime import datetime
        return datetime.utcnow().strftime("%Y%m%d-%H%M")


def get_data_sql_bytes_per_db() -> dict[str, int]:
    """Return {db_id: bytes} for primary data.sql per db."""
    result = {}
    for n in range(1, 17):
        db_dir = SOURCE / f"db-{n}"
        if not db_dir.exists():
            continue
        for base in [db_dir / "data", db_dir / "app" / "DATABASE"]:
            if not base.exists():
                continue
            for name in ["data_large.sql", "data_large_postgresql.sql", "data.sql"]:
                p = base / name
                if p.exists() and p.is_file():
                    result[f"db-{n}"] = p.stat().st_size
                    break
            if f"db-{n}" in result:
                break
    return result


def check_schema_postgresql(content: str) -> list[str]:
    violations = []
    for pat, name in NON_PG_TYPE_PATTERNS:
        if re.search(pat, content, re.IGNORECASE):
            violations.append(name)
    return violations


def extract_table_names(content: str) -> list[str]:
    tables = []
    for m in re.finditer(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)",
        content,
        re.IGNORECASE,
    ):
        tables.append(m.group(1).lower())
    return tables


def check_snake_case(names: list[str]) -> list[str]:
    return [n for n in names if n and not SNAKE_CASE_RE.match(n)]


def get_schema_paths() -> list[tuple[str, Path]]:
    result = []
    for n in range(1, 17):
        db_dir = SOURCE / f"db-{n}"
        if not db_dir.exists():
            continue
        for base in [db_dir / "data", db_dir / "app" / "DATABASE"]:
            if not base.exists():
                continue
            for name in ["schema.sql"]:
                p = base / name
                if p.exists() and p.is_file():
                    result.append((f"db-{n}", p))
                    break
            if any(r[0] == f"db-{n}" for r in result):
                break
    return result


def _is_required_path(rel: Path) -> bool:
    """True if path is needed for app/ compilation."""
    parts = rel.parts
    if not parts:
        return False
    top = parts[0]
    if top == "app":
        return True
    if top == "data":
        if len(parts) == 1:
            return True
        return parts[-1] in {"schema.sql", "data.sql", "data_large.sql", "data_large_postgresql.sql"}
    if top == "queries":
        if len(parts) == 1:
            return True
        return parts[-1] in {"queries.json", "queries.md"}
    if len(parts) == 1 and top in {"queries_header.yaml", "queries_header.json"}:
        return True
    return False


def flag_unnecessary_in_source_db(db_dir: Path, db_id: str) -> list[str]:
    """Return relative paths of files/dirs not needed for app/ compilation."""
    flagged = []
    for item in db_dir.rglob("*"):
        if item == db_dir:
            continue
        rel = item.relative_to(db_dir)
        rel_str = str(rel).replace("\\", "/")
        if _is_required_path(rel):
            continue
        # Also allow top-level source dirs: data/, queries/, docs/, app/
        if item.is_dir() and len(rel.parts) == 1 and rel.parts[0] in {"data", "queries", "docs", "app"}:
            continue
        flagged.append(rel_str)
    return sorted(set(flagged))


def flag_unnecessary_at_root() -> list[str]:
    """Return paths at repo root not in canonical list."""
    flagged = []
    for item in ROOT.iterdir():
        if item.name.startswith(".") and item.name not in {".cursor", ".gitignore", ".env"}:
            if item.name != ".git":
                flagged.append(item.name)
            continue
        if item.is_dir():
            if item.name not in CANONICAL_ROOT_DIRS and item.name != ".git":
                flagged.append(item.name + "/")
        else:
            if item.name not in CANONICAL_ROOT_FILES:
                flagged.append(item.name)
    return sorted(flagged)


def run_checks(lenient: bool = False) -> dict:
    report = {
        "generated_at": get_est_timestamp(),
        "Pass": 1,
        "checks": {},
        "databases": {},
    }

    # 1. Data size
    data_bytes = get_data_sql_bytes_per_db()
    total = sum(data_bytes.values())
    size_pass = 1 if total >= MIN_DATA_SQL_TOTAL_BYTES else (1 if lenient else 0)
    report["checks"]["data_size_gb"] = {
        "Pass": size_pass,
        "total_bytes": total,
        "required_bytes": MIN_DATA_SQL_TOTAL_BYTES,
    }
    if size_pass == 0:
        report["Pass"] = 0

    # 2. Schema compliance
    schema_violations = {}
    for db_id, p in get_schema_paths():
        content = p.read_text(encoding="utf-8")
        violations = check_schema_postgresql(content)
        if violations:
            schema_violations[db_id] = violations
    schema_pass = 1 if not schema_violations else (1 if lenient else 0)
    report["checks"]["schema_postgresql_compliant"] = {
        "Pass": schema_pass,
        "databases": list({r[0] for r in get_schema_paths()}),
        "violations": schema_violations,
    }
    if schema_pass == 0:
        report["Pass"] = 0

    # 3. Naming
    naming_violations = {}
    for db_id, p in get_schema_paths():
        content = p.read_text(encoding="utf-8")
        tables = extract_table_names(content)
        bad = check_snake_case(tables)
        if bad:
            naming_violations[db_id] = bad
    naming_pass = 1 if not naming_violations else (1 if lenient else 0)
    report["checks"]["naming_consistent"] = {
        "Pass": naming_pass,
        "violations": naming_violations,
    }
    if naming_pass == 0:
        report["Pass"] = 0

    # 4. Unnecessary source files
    unnecessary_source = {}
    for n in range(1, 17):
        db_dir = SOURCE / f"db-{n}"
        if not db_dir.exists():
            continue
        flagged = flag_unnecessary_in_source_db(db_dir, f"db-{n}")
        if flagged:
            unnecessary_source[f"db-{n}"] = flagged[:50]  # Limit per db
    report["checks"]["unnecessary_source_files"] = {
        "flagged": unnecessary_source,
    }

    # 5. Unnecessary root files
    unnecessary_root = flag_unnecessary_at_root()
    report["checks"]["unnecessary_root_files"] = {
        "flagged": unnecessary_root,
    }

    # Per-db summary
    for db_id, bytes_val in data_bytes.items():
        report["databases"][db_id] = {
            "data_bytes": bytes_val,
            "schema_pass": 0 if db_id in schema_violations else 1,
            "naming_pass": 0 if db_id in naming_violations else 1,
            "flagged": unnecessary_source.get(db_id, [])[:10],
        }

    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Repo health check")
    ap.add_argument("--lenient", action="store_true", help="Warn instead of fail")
    ap.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = ap.parse_args()
    lenient = args.lenient or os.environ.get("REPO_HEALTH_LENIENT", "0") == "1"

    sys.path.insert(0, str(Path(__file__).parent))
    report = run_checks(lenient=lenient)

    RESULTS.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS / "repo_health.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["Pass"] == 1 else "FAIL"
        print(f"Repo health: {status}")
        print(f"  Data size: {report['checks']['data_size_gb']['total_bytes']:,} / {MIN_DATA_SQL_TOTAL_BYTES:,} bytes")
        print(f"  Schema PG compliant: {'Pass' if report['checks']['schema_postgresql_compliant']['Pass'] else 'Fail'}")
        print(f"  Naming: {'Pass' if report['checks']['naming_consistent']['Pass'] else 'Fail'}")
        flagged_src = sum(len(v) for v in report["checks"]["unnecessary_source_files"]["flagged"].values())
        print(f"  Flagged source files: {flagged_src}")
        print(f"  Flagged root files: {len(report['checks']['unnecessary_root_files']['flagged'])}")
        print(f"Report: {out_path}")

    return 0 if report["Pass"] == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
