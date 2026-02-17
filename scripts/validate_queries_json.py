#!/usr/bin/env python3
"""
Validate queries.json files against JSON Schema.
Uses jsonschema (Draft 2020-12) for structure and field validation.

Usage:
  python3 scripts/validate_queries_json.py           # db-1 only (default)
  python3 scripts/validate_queries_json.py 1 5      # db-1 through db-5
  python3 scripts/validate_queries_json.py -a       # all db-1..16
"""

import json
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

from db_paths import SOURCE, get_queries_dir

SCHEMA_PATH = scripts_dir / "schemas" / "queries.schema.json"


def load_schema() -> dict:
    """Load JSON Schema from scripts/schemas/queries.schema.json."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def get_queries_json_path(db_num: int) -> Path:
    """Resolve queries.json path for db-N."""
    db_dir = SOURCE / f"db-{db_num}"
    queries_dir = get_queries_dir(db_dir)
    return queries_dir / "queries.json"


def validate_file(path: Path, schema: dict) -> list[dict]:
    """
    Validate a queries.json file against schema.
    Returns list of error dicts: [{"path": [...], "message": "..."}, ...]
    """
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Error: jsonschema package required. Run: pip install jsonschema>=4.20.0", file=sys.stderr)
        sys.exit(1)

    if not path.exists():
        return [{"path": [], "message": f"File not found: {path}"}]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [{"path": [], "message": f"Invalid JSON: {e}"}]

    validator = Draft202012Validator(schema)
    errors = []
    for err in validator.iter_errors(data):
        path_list = list(err.absolute_path)
        errors.append({
            "path": path_list,
            "message": err.message,
            "validator": err.validator,
        })
    return errors


def main() -> int:
    db_nums: list[int] = []
    if "-a" in sys.argv or "--all" in sys.argv:
        db_nums = list(range(1, 17))
    else:
        args = [a for a in sys.argv[1:] if a not in ("-a", "--all")]
        db_nums = [int(a) for a in args] if args else [1]

    try:
        schema = load_schema()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    total_errors = 0
    for db_num in db_nums:
        path = get_queries_json_path(db_num)
        errors = validate_file(path, schema)
        if errors:
            total_errors += len(errors)
            print(f"db-{db_num}: {len(errors)} error(s)")
            for err in errors[:10]:  # Limit to 10 per db
                path_str = ".".join(str(p) for p in err["path"]) if err["path"] else "(root)"
                print(f"  {path_str}: {err['message']}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
        else:
            print(f"db-{db_num}: OK")

    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
