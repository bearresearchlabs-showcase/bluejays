#!/usr/bin/env python3
"""
Validate source/db-N app/QUERIES/ matches @template/ reference perfectly.

Compares:
- Section order and presence (required + optional)
- Query block format (### Query N — difficulty / category)
- Query JSON required fields
- Structure alignment with template/queries.md and template/queries.json

Usage:
    python3 scripts/validate_template_match.py db-1 [db-5] | -a
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATE = ROOT / "template"
SOURCE = ROOT / "source"


# Required sections (must appear in this order) — from template/queries.md
REQUIRED_SECTIONS = [
    "## Database Overview",
    "## Purpose",
    "## Use Case",
    "## Business Value",
    "## Schema",
    "## Domain Knowledge",
    "## Query Difficulty Distribution",
    "## Queries",
]

# Optional section (template has it; source may omit)
OPTIONAL_SECTIONS = ["## Training Data Field Definitions"]

# Query block pattern — from qa_anchor
QUERY_HEADER_PATTERN = re.compile(
    r"^### Query (\d+) — (simple|moderate|challenging) / ([a-zA-Z0-9/_-]+)$"
)

# Required fields in each query JSON block
QUERY_JSON_REQUIRED = [
    "db_id", "question_id", "question", "SQL", "evidence",
    "difficulty", "query_category", "tables_used", "schema_context", "expected_output",
]


def _find_queries_dir(db_dir: Path) -> Path | None:
    for d in (db_dir / "app" / "QUERIES", db_dir / "QUERIES", db_dir / "queries"):
        if d.exists():
            return d
    return None


def validate_queries_md(qm: Path) -> list[str]:
    """Validate queries.md matches template structure."""
    errs = []
    content = qm.read_text(encoding="utf-8")

    # Title format
    if not re.match(r"^# .+ — .+$", content.split("\n")[0]):
        errs.append("Title must match: # {name} — Query Documentation (em dash)")

    # Required sections in order
    pos = 0
    for sec in REQUIRED_SECTIONS:
        idx = content.find(sec)
        if idx < 0:
            errs.append(f"Missing required section: {sec}")
        elif idx < pos:
            errs.append(f"Section order wrong: {sec} should come after previous")
        else:
            pos = idx

    # Query blocks
    in_queries = False
    count = 0
    for line in content.split("\n"):
        if line.strip() == "## Queries":
            in_queries = True
            continue
        if in_queries and line.startswith("### Query "):
            if not QUERY_HEADER_PATTERN.match(line.strip()):
                errs.append(f"Query header must match pattern: {line.strip()[:60]}...")
            count += 1
    if count < 30:
        errs.append(f"Expected at least 30 query blocks, got {count}")

    # JSON blocks have required fields
    json_blocks = re.findall(r"```json\s*\n(.*?)```", content, re.DOTALL)
    for i, raw in enumerate(json_blocks):
        try:
            obj = json.loads(raw.strip())
            for f in QUERY_JSON_REQUIRED:
                if f not in obj and "_field_definitions" not in obj:
                    errs.append(f"Query JSON block {i+1} missing field: {f}")
        except json.JSONDecodeError:
            errs.append(f"Query JSON block {i+1} invalid JSON")

    return errs


def validate_queries_json(qj: Path) -> list[str]:
    """Validate queries.json structure (API-response or template array format)."""
    errs = []
    data = json.loads(qj.read_text(encoding="utf-8"))

    # Accept API-response format
    if isinstance(data, dict):
        queries = data.get("queries", data.get("data", {}).get("queries", []))
        api = data.get("_api_response", data)
        if not queries and "data" in api:
            queries = api.get("data", {}).get("queries", [])
    elif isinstance(data, list):
        # Template array format: [{_field_definitions}, query1, query2, ...]
        queries = [x for x in data if isinstance(x, dict) and "question_id" in x]
    else:
        errs.append("queries.json must be object or array")
        return errs

    if len(queries) < 30:
        errs.append(f"Expected at least 30 queries, got {len(queries)}")

    for i, q in enumerate(queries[:5]):  # Sample first 5
        if not isinstance(q, dict):
            continue
        for f in QUERY_JSON_REQUIRED:
            if f not in q:
                errs.append(f"Query {i+1} missing field: {f}")
        if "SQL" not in q and "sql" not in q:
            errs.append(f"Query {i+1} must have SQL or sql")

    return errs


def validate_db(db_num: int) -> dict:
    """Validate db-N against template."""
    db_dir = SOURCE / f"db-{db_num}"
    qd = _find_queries_dir(db_dir)
    if not qd:
        return {"ok": False, "error": "QUERIES dir not found"}

    qm = qd / "queries.md"
    qj = qd / "queries.json"

    result = {"db_num": db_num, "md_errors": [], "json_errors": [], "ok": True}

    if qm.exists():
        result["md_errors"] = validate_queries_md(qm)
    else:
        result["md_errors"] = ["queries.md not found"]

    if qj.exists():
        result["json_errors"] = validate_queries_json(qj)
    else:
        result["json_errors"] = ["queries.json not found"]

    result["ok"] = not (result["md_errors"] or result["json_errors"])
    return result


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Validate source matches @template")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or -a for all")
    ap.add_argument("-a", "--all", action="store_true")
    args = ap.parse_args()

    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = []
        for a in args.dbs:
            n = str(a).replace("db-", "")
            try:
                db_nums.append(int(n))
            except ValueError:
                pass
        db_nums = sorted(set(db_nums))

    ok_count = 0
    for n in db_nums:
        r = validate_db(n)
        if r["ok"]:
            print(f"  db-{n}: OK (matches template)")
            ok_count += 1
        else:
            errs = r.get("md_errors", []) + r.get("json_errors", [])
            print(f"  db-{n}: FAIL")
            for e in errs[:5]:
                print(f"    - {e}")
            if len(errs) > 5:
                print(f"    - ... and {len(errs)-5} more")

    print(f"\nDone: {ok_count}/{len(db_nums)} match template")
    return 0 if ok_count == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
