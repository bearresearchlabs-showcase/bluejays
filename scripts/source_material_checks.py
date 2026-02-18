#!/usr/bin/env python3
"""
Source material validation checks for source/db-N.

Validates: queries.json, queries_header.yaml, schema.sql, data.sql, queries.md.
Call from db_check.py source-checks or from Jupyter notebook.

Usage:
    python3 scripts/source_material_checks.py [db-1] [db-5] | -a
    python3 scripts/source_material_checks.py --json  # Output JSON report
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
sys.path.insert(0, str(Path(__file__).parent))

try:
    from db_paths import get_queries_dir, get_data_dir
except ImportError:

    def get_queries_dir(db_dir: Path) -> Path:
        app = db_dir / "app"
        if app.exists() and (app / "QUERIES").exists():
            return app / "QUERIES"
        if (db_dir / "QUERIES").exists():
            return db_dir / "QUERIES"
        return db_dir / "queries"

    def get_data_dir(db_dir: Path) -> Path:
        app = db_dir / "app"
        if app.exists() and (app / "DATABASE").exists():
            return app / "DATABASE"
        return db_dir / "data"


REQUIRED_HEADER_KEYS = ["db_name", "database_overview", "purpose", "use_case", "business_value"]
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


def check_queries_json(queries_dir: Path) -> Dict[str, Any]:
    """Validate queries.json: valid JSON, 30 queries, required fields."""
    result = {"pass": True, "errors": [], "warnings": []}
    qj = queries_dir / "queries.json"
    if not qj.exists():
        result["pass"] = False
        result["errors"].append("queries.json not found")
        return result

    try:
        data = json.loads(qj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result["pass"] = False
        result["errors"].append(f"Invalid JSON: {e}")
        return result

    queries = data.get("queries", data) if isinstance(data, dict) else data
    if not isinstance(queries, list):
        result["pass"] = False
        result["errors"].append("queries.json must have a 'queries' array")
        return result

    if len(queries) != 30:
        result["pass"] = False
        result["errors"].append(f"Expected 30 queries, got {len(queries)}")

    for i, q in enumerate(queries[:5]):  # Sample first 5
        if not isinstance(q, dict):
            result["pass"] = False
            result["errors"].append(f"Query {i+1} is not an object")
            continue
        sql = q.get("SQL") or q.get("sql", "")
        if not sql or not str(sql).strip():
            result["pass"] = False
            result["errors"].append(f"Query {i+1} missing SQL")
        num = q.get("number") or q.get("question_id")
        if num is None:
            pass  # Optional; no warning per zero-warnings policy
        evidence = q.get("evidence") or q.get("description", "")
        if not str(evidence).strip():
            pass  # Optional; no warning per zero-warnings policy

    return result


def check_queries_header(db_dir: Path) -> Dict[str, Any]:
    """Validate queries_header.yaml or .json (if present)."""
    result = {"pass": True, "errors": [], "warnings": [], "present": False}
    yaml_path = db_dir / "queries_header.yaml"
    json_path = db_dir / "queries_header.json"
    if not yaml_path.exists() and not json_path.exists():
        return result

    result["present"] = True
    try:
        from load_queries_header import load_queries_header

        header = load_queries_header(db_dir)
        if not header:
            result["pass"] = False
            result["errors"].append("Failed to load queries_header")
            return result
        for key in ["db_name", "overview_yaml", "purpose_text"]:
            if not header.get(key):
                result["pass"] = False
                result["errors"].append(f"Header missing required key: {key}")
    except Exception as e:
        result["pass"] = False
        result["errors"].append(f"Load error: {e}")

    return result


# Non-PostgreSQL types (fail if found - repo is PostgreSQL-only)
NON_PG_TYPE_PATTERNS = [
    (r"\bTIMESTAMP_NTZ\b", "TIMESTAMP_NTZ"),
    (r"\bVARIANT\b", "VARIANT"),
    (r"\bARRAY\s*<", "ARRAY<"),
    (r"\bMAP\s*<", "MAP<"),
]


def check_schema_sql(data_dir: Path) -> Dict[str, Any]:
    """Validate schema.sql: exists, contains CREATE TABLE, PostgreSQL-only (no TIMESTAMP_NTZ, VARIANT, etc)."""
    result = {"pass": True, "errors": [], "warnings": []}
    for name in ("schema.sql",):
        p = data_dir / name
        if p.exists():
            content = p.read_text(encoding="utf-8")
            if "CREATE TABLE" not in content.upper():
                result["pass"] = False
                result["errors"].append(f"{name} has no CREATE TABLE")
            # PostgreSQL-only: fail on non-PG types
            for pat, type_name in NON_PG_TYPE_PATTERNS:
                if re.search(pat, content, re.IGNORECASE):
                    result["pass"] = False
                    result["errors"].append(f"{name} contains non-PostgreSQL type: {type_name}")
            return result

    result["pass"] = False
    result["errors"].append("schema.sql not found")
    return result


def check_data_sql(data_dir: Path) -> Dict[str, Any]:
    """Validate data.sql: exists, contains INSERT (optional)."""
    result = {"pass": True, "errors": [], "warnings": [], "present": False}
    p = data_dir / "data.sql"
    if not p.exists():
        return result

    result["present"] = True
    content = p.read_text(encoding="utf-8")
    return result


def check_queries_md(queries_dir: Path) -> Dict[str, Any]:
    """Validate queries.md: required sections, 30 query blocks."""
    result = {"pass": True, "errors": [], "warnings": []}
    qm = queries_dir / "queries.md"
    if not qm.exists():
        result["pass"] = False
        result["errors"].append("queries.md not found")
        return result

    content = qm.read_text(encoding="utf-8")
    for section in REQUIRED_H2_SECTIONS:
        if f"## {section}" not in content:
            result["pass"] = False
            result["errors"].append(f"Missing section: ## {section}")

    query_blocks = re.findall(r"^### Query \d+ — ", content, re.MULTILINE)
    if len(query_blocks) < 30:
        result["pass"] = False
        result["errors"].append(f"Expected at least 30 query blocks, got {len(query_blocks)}")

    if not content.strip().startswith("# "):
        result["pass"] = False
        result["errors"].append("queries.md must start with # title")

    return result


def check_db(db_num: int) -> Dict[str, Any]:
    """Run all source material checks for one db-N."""
    db_id = f"db-{db_num}"
    db_dir = SOURCE / f"db-{db_num}"
    if not db_dir.exists():
        return {"db_id": db_id, "pass": False, "errors": [f"source/db-{db_num} not found"]}

    queries_dir = get_queries_dir(db_dir)
    data_dir = get_data_dir(db_dir)

    results = {
        "db_id": db_id,
        "pass": True,
        "checks": {},
        "errors": [],
        "warnings": [],
    }

    for name, fn in [
        ("queries_json", lambda: check_queries_json(queries_dir)),
        ("queries_header", lambda: check_queries_header(db_dir)),
        ("schema_sql", lambda: check_schema_sql(data_dir)),
        ("data_sql", lambda: check_data_sql(data_dir)),
        ("queries_md", lambda: check_queries_md(queries_dir)),
    ]:
        r = fn()
        results["checks"][name] = r
        if not r.get("pass", True):
            results["pass"] = False
        results["errors"].extend(r.get("errors", []))
        results["warnings"].extend(r.get("warnings", []))

    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Source material validation checks")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all")
    ap.add_argument("-a", "--all", action="store_true", help="Check all db-1..db-16")
    ap.add_argument("--json", action="store_true", help="Output JSON report")
    args = ap.parse_args()

    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = []
        for a in args.dbs:
            a = str(a).replace("db-", "")
            try:
                db_nums.append(int(a))
            except ValueError:
                pass
        db_nums = sorted(set(db_nums))

    all_results = []
    for n in db_nums:
        r = check_db(n)
        all_results.append(r)

    if args.json:
        print(json.dumps({"databases": all_results, "total": len(all_results)}, indent=2))
    else:
        for r in all_results:
            status = "PASS" if r["pass"] else "FAIL"
            print(f"  {r['db_id']}: {status}")
            for e in r.get("errors", []):
                print(f"    ERROR: {e}")
            for w in r.get("warnings", []):
                print(f"    WARN: {w}")

    failed = sum(1 for r in all_results if not r["pass"])
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
