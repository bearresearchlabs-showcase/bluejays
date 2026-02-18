#!/usr/bin/env python3
"""
Update queries.md from queries.json — sync evidence and description into embedded JSON blocks.

Usage:
  python3 scripts/update_queries_md_from_json.py --db N [--query Q]
  python3 scripts/update_queries_md_from_json.py --db 1           # Update all 30 queries in db-1
  python3 scripts/update_queries_md_from_json.py --db 1 --query 5 # Update only Query 5 in db-1
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from db_paths import SOURCE, get_queries_dir
from queries_md_template_formatter import _format_query_block


def load_queries_json(queries_dir: Path) -> list[dict]:
    """Load queries from queries.json."""
    qj = queries_dir / "queries.json"
    if not qj.exists():
        raise FileNotFoundError(f"queries.json not found: {qj}")
    data = json.loads(qj.read_text(encoding="utf-8"))
    queries = data.get("queries", data) if isinstance(data, dict) else data
    if not isinstance(queries, list):
        raise ValueError("queries.json must have a 'queries' array")
    return queries


def load_queries_md(queries_dir: Path) -> str:
    """Load queries.md content."""
    qm = queries_dir / "queries.md"
    if not qm.exists():
        raise FileNotFoundError(f"queries.md not found: {qm}")
    return qm.read_text(encoding="utf-8")


def update_query_block(md_content: str, query_num: int, new_block: str) -> str:
    """Replace the ### Query N block with new_block. Returns updated md_content."""
    # Pattern: ### Query N — ... followed by ```json ... ```
    pattern = r"### Query " + str(query_num) + r" — [^\n]+\n\n```json\n[\s\S]*?\n```"
    match = re.search(pattern, md_content)
    if not match:
        raise ValueError(f"Query {query_num} block not found in queries.md")
    replacement = new_block.rstrip()
    if not replacement.endswith("\n"):
        replacement += "\n"
    return md_content[: match.start()] + replacement + md_content[match.end() :]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Update queries.md from queries.json (sync evidence/description)"
    )
    ap.add_argument("--db", type=int, required=True, help="Database number (1-16)")
    ap.add_argument("--query", type=int, default=None, help="Query number (1-30); omit to update all")
    args = ap.parse_args()

    db_num = args.db
    query_num = args.query
    if db_num < 1 or db_num > 16:
        print(f"Error: --db must be 1-16, got {db_num}", file=sys.stderr)
        return 1
    if query_num is not None and (query_num < 1 or query_num > 30):
        print(f"Error: --query must be 1-30, got {query_num}", file=sys.stderr)
        return 1

    db_dir = SOURCE / f"db-{db_num}"
    queries_dir = get_queries_dir(db_dir)
    db_id = f"db-{db_num}"

    try:
        queries = load_queries_json(queries_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        md_content = load_queries_md(queries_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Build query lookup by number
    by_num = {}
    for q in queries:
        n = q.get("number", q.get("question_id", 0))
        by_num[n] = q

    target_nums = [query_num] if query_num else range(1, 31)
    updated = 0
    for n in target_nums:
        if n not in by_num:
            print(f"Warning: Query {n} not in queries.json, skipping", file=sys.stderr)
            continue
        q = by_num[n]
        new_block = _format_query_block(q, db_id, bit_by_bit=True)
        md_content = update_query_block(md_content, n, new_block)
        updated += 1

    (queries_dir / "queries.md").write_text(md_content, encoding="utf-8")
    print(f"Updated {updated} query block(s) in {queries_dir / 'queries.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
