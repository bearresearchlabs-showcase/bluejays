#!/usr/bin/env python3
"""
Rewrite the description field for each query using Claude 3.5 Haiku.
Description = contextual story (who has this need, what problem, why it matters).
Evidence stays unchanged (technical/SQL operations).
Single API call per query.

Usage:
  python3 scripts/claude_rewrite_description_story.py 1              # db-1, dry run
  python3 scripts/claude_rewrite_description_story.py 1 --apply     # write to queries.json
  python3 scripts/claude_rewrite_description_story.py -a --apply     # all db-1..16
  python3 scripts/claude_rewrite_description_story.py 1 --apply --incremental
  python3 scripts/claude_rewrite_description_story.py 1 --query 5    # db-1 query 5 only
"""

import json
import os
import re
import sys
import time
from pathlib import Path

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

from env_validator import load_env, ensure_env
from db_paths import SOURCE, get_queries_dir

load_env()
if not ensure_env("claude"):
    sys.exit(1)

REPO = root_dir
MODEL = "claude-3-5-haiku-20241022"
SQL_TRUNCATE = 800


def _get_api_key() -> str:
    """Return ANTHROPIC_API_KEY."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return key


def _call_claude(prompt: str, max_tokens: int = 1024) -> str:
    """Call Claude API. Returns response text or raises."""
    from anthropic import Anthropic
    client = Anthropic(api_key=_get_api_key())
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text if resp.content else ""


def get_queries_json_path(db_num: int) -> Path:
    """Resolve queries.json path for db-N."""
    db_dir = SOURCE / f"db-{db_num}"
    queries_dir = get_queries_dir(db_dir)
    return queries_dir / "queries.json"


def load_queries(db_num: int) -> tuple[list[dict], Path]:
    """Load queries from source/db-N queries.json. Returns (queries, path)."""
    path = get_queries_json_path(db_num)
    if not path.exists():
        return [], path
    data = json.loads(path.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    return queries, path


def save_queries(path: Path, data: dict, queries: list[dict]) -> None:
    """Write updated queries back to JSON."""
    data["queries"] = queries
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _parse_description(out: str) -> str:
    """Parse JSON response with description. Returns description string."""
    out = out.strip()
    if out.startswith("```"):
        out = re.sub(r"^```\w*\n?", "", out)
        out = re.sub(r"\n?```$", "", out)
    try:
        data = json.loads(out)
        return (data.get("description") or "").strip()
    except json.JSONDecodeError:
        return out[:500] if out else ""


def call_claude_description(query: dict) -> str:
    """Claude 3.5 Haiku: Generate contextual description (story) for one query."""
    question = query.get("question", "")[:500]
    current_description = (query.get("description") or "")[:600]
    evidence = (query.get("evidence") or "")[:1000]
    sql_preview = (query.get("sql") or "")[:SQL_TRUNCATE]

    prompt = f"""You are a BIRD benchmark expert. Write a 1-2 sentence **description** that captures contextual information NOT already in evidence.

Description = the story: who has this need, what problem they face, why it matters. Do NOT repeat what evidence says (technical/SQL operations, CTEs, joins, etc.).

Query question: {question}
Current description: {current_description}
Evidence (technical - do NOT repeat): {evidence}
SQL (preview): {sql_preview}

Reply with a JSON object only, no markdown:
{{"description": "..."}}"""

    out = _call_claude(prompt, max_tokens=512)
    return _parse_description(out) if out else current_description


def process_one_query(
    query: dict,
    apply: bool,
    path: Path,
    data: dict,
    queries: list[dict],
    incremental: bool,
) -> str:
    """Process one query: call Claude, optionally apply. Returns new description."""
    qnum = query.get("number", 0)
    idx = next((i for i, q in enumerate(queries) if q.get("number") == qnum), -1)
    if idx < 0:
        return ""

    new_desc = call_claude_description(query)
    time.sleep(0.5)

    if apply:
        queries[idx]["description"] = new_desc
        if incremental:
            save_queries(path, data, queries)

    return new_desc


def run_db(
    db_num: int,
    apply: bool,
    incremental: bool,
    query_filter: int | None,
) -> int:
    """Process all (or filtered) queries for db-N. Returns 0 on success."""
    path_full = get_queries_json_path(db_num)
    if not path_full.exists():
        print(f"No queries.json in db-{db_num}", file=sys.stderr)
        return 1

    data = json.loads(path_full.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    if not queries:
        print(f"No queries in db-{db_num}", file=sys.stderr)
        return 1

    to_process = queries
    if query_filter is not None:
        to_process = [q for q in queries if q.get("number") == query_filter]
        if not to_process:
            print(f"Query {query_filter} not found in db-{db_num}", file=sys.stderr)
            return 1

    for q in to_process:
        qnum = q.get("number", 0)
        print(f"  db-{db_num} Q{qnum}: rewriting description...", flush=True)
        desc = process_one_query(q, apply, path_full, data, queries, incremental)
        if desc:
            print(f"    -> {desc[:80]}...")
        else:
            print(f"    -> (empty)")

    if apply and not incremental:
        save_queries(path_full, data, queries)
        print(f"  Saved {path_full}")

    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Claude 3.5 Haiku description story rewrite")
    ap.add_argument("db", type=int, nargs="?", default=None, help="Database number (1-16)")
    ap.add_argument("-a", "--all", action="store_true", help="All db-1..16")
    ap.add_argument("--apply", action="store_true", help="Write changes to queries.json")
    ap.add_argument("--incremental", action="store_true", help="Save after each query")
    ap.add_argument("--query", type=int, default=None, help="Process only this query number (1-30)")
    args = ap.parse_args()

    if args.all:
        db_nums = list(range(1, 17))
    elif args.db is not None:
        if args.db < 1 or args.db > 16:
            print("Invalid db. Use 1-16.", file=sys.stderr)
            return 1
        db_nums = [args.db]
    else:
        print("Specify db number or -a/--all", file=sys.stderr)
        return 1

    for db_num in db_nums:
        print(f"\n--- db-{db_num} ---")
        if run_db(db_num, args.apply, args.incremental, args.query) != 0:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
