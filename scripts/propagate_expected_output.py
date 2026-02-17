#!/usr/bin/env python3
"""
Propagate expected_output from queries.json to queries.md for db-6 and db-16.
Replaces placeholder "Query results" (or any value) with actual expected_output from JSON.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent


def propagate_md(json_path: Path, md_path: Path, db_num: int) -> bool:
    """Propagate expected_output from JSON to one md file."""
    with open(json_path) as f:
        data = json.load(f)

    queries = data.get("queries", [])
    if not queries:
        print(f"db-{db_num}: no queries in json", file=sys.stderr)
        return False

    outputs = [q.get("expected_output", "") for q in queries]

    with open(md_path) as f:
        content = f.read()

    idx = [0]

    def replacer(match):
        if idx[0] < len(outputs):
            val = outputs[idx[0]]
            idx[0] += 1
            return '"expected_output": ' + json.dumps(val)
        return match.group(0)

    # Match "expected_output": "..." - value may not contain unescaped quotes
    pattern = re.compile(r'"expected_output":\s*"[^"]*"')
    new_content = pattern.sub(replacer, content)

    if new_content != content:
        with open(md_path, "w") as f:
            f.write(new_content)
        print(f"Updated {md_path} ({idx[0]} expected_output values)")
        return True
    return False


def propagate_db(db_num: int) -> bool:
    """Propagate for one database to all md locations."""
    app = BASE / "source" / f"db-{db_num}" / "app" / "QUERIES"
    json_path = app / "queries.json"
    if not json_path.exists():
        print(f"db-{db_num}: missing {json_path}", file=sys.stderr)
        return False

    # All md paths that need updating
    root = BASE / "source" / f"db-{db_num}"
    md_paths = [
        app / "queries.md",
        root / "queries" / "queries.md",
        root / "deliverable" / "queries" / "queries.md",
    ]
    # Web-deployable folder (db6-weather-consulting-insurance, db16-flood-risk-assessment)
    web = root / "deliverable"
    if web.exists():
        for d in web.iterdir():
            if d.is_dir() and d.name.startswith(f"db{db_num}-"):
                qmd = d / "queries" / "queries.md"
                if qmd.exists():
                    md_paths.append(qmd)
                break

    changed = False
    for md_path in md_paths:
        if md_path.exists():
            if propagate_md(json_path, md_path, db_num):
                changed = True
    return changed


def main():
    for db_num in (6, 16):
        propagate_db(db_num)


if __name__ == "__main__":
    main()
