#!/usr/bin/env python3
"""
Rewrite description and evidence keys for each query using Claude Opus 4.6 and Sonnet 4.5.
One API call per query per model. Output is natural language (no STAR format).
Uses ANTHROPIC_API_KEY and ANTHROPIC_API_KEY_2 for rotation.

Usage:
  python3 scripts/claude_rewrite_evidence_natural.py 1              # db-1, dry run
  python3 scripts/claude_rewrite_evidence_natural.py 1 --apply     # write to queries.json
  python3 scripts/claude_rewrite_evidence_natural.py -a --apply     # all db-1..16
  python3 scripts/claude_rewrite_evidence_natural.py 1 --query 5  # db-1 query 5 only
  python3 scripts/claude_rewrite_evidence_natural.py 1 --apply --incremental  # save after each query
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
MODEL_OPUS = "claude-opus-4-6"
MODEL_SONNET = "claude-sonnet-4-5-20250929"
SQL_TRUNCATE = 800


def _get_api_key(call_index: int) -> str:
    """Alternate between ANTHROPIC_API_KEY and ANTHROPIC_API_KEY_2."""
    key1 = os.getenv("ANTHROPIC_API_KEY")
    key2 = os.getenv("ANTHROPIC_API_KEY_2")
    if not key1:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    if call_index % 2 == 0:
        return key1
    return key2 if key2 else key1


def _call_claude(prompt: str, model: str, call_index: int, max_tokens: int = 4096) -> str:
    """Call Claude API. Uses key rotation. Returns response text or raises."""
    from anthropic import Anthropic
    key = _get_api_key(call_index)
    client = Anthropic(api_key=key)
    resp = client.messages.create(
        model=model,
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


def _parse_description_evidence(out: str) -> tuple[str, str]:
    """Parse JSON response with description and evidence. Returns (description, evidence)."""
    out = out.strip()
    if out.startswith("```"):
        out = re.sub(r"^```\w*\n?", "", out)
        out = re.sub(r"\n?```$", "", out)
    try:
        data = json.loads(out)
        desc = (data.get("description") or "").strip()
        ev = (data.get("evidence") or "").strip()
        return desc, ev
    except json.JSONDecodeError:
        # Fallback: treat entire output as evidence
        fallback = out[:500] if out else ""
        return "", fallback


def call_opus_description_evidence(query: dict, call_index: int) -> tuple[str, str]:
    """Opus 4.6: Generate natural-language description and evidence for one query."""
    question = query.get("question", "")[:500]
    description = (query.get("description") or "")[:600]
    sql_preview = (query.get("sql") or "")[:SQL_TRUNCATE]
    current_evidence = (query.get("evidence") or "")[:800]

    prompt = f"""You are a BIRD benchmark expert. Rewrite the "description" and "evidence" for this SQL query into natural language.

CRITICAL: Do NOT use "Situation", "Task", "Action", "Result" or any STAR structure. Write flowing prose for both fields.

- description: 1-2 sentences summarizing what the query does and why it matters.
- evidence: 2-4 sentences giving overall context: what the query does, why it matters, and what it returns.

Query question: {question}
Current description: {description}
SQL (preview): {sql_preview}
Current evidence: {current_evidence}

Reply with a JSON object only, no markdown:
{{"description": "...", "evidence": "..."}}"""

    out = _call_claude(prompt, MODEL_OPUS, call_index, max_tokens=1536)
    return _parse_description_evidence(out) if out else ("", "")


def call_sonnet_description_evidence(
    query: dict, opus_description: str, opus_evidence: str, call_index: int
) -> tuple[str, str]:
    """Sonnet 4.5: Refine description and evidence from Opus output."""
    question = query.get("question", "")[:500]
    sql_preview = (query.get("sql") or "")[:SQL_TRUNCATE]

    prompt = f"""You are a BIRD benchmark expert. Refine the description and evidence for an SQL query.

CRITICAL: Do NOT use "Situation", "Task", "Action", "Result" or any STAR structure. Output must be natural language. Improve clarity and concision while preserving accuracy.

Query question: {question}
SQL (preview): {sql_preview}
Draft description (refine this): {opus_description}
Draft evidence (refine this): {opus_evidence}

Reply with a JSON object only, no markdown:
{{"description": "...", "evidence": "..."}}"""

    out = _call_claude(prompt, MODEL_SONNET, call_index, max_tokens=1536)
    desc, ev = _parse_description_evidence(out) if out else (opus_description, opus_evidence)
    return desc or opus_description, ev or opus_evidence


def process_one_query(
    query: dict,
    call_index: int,
    apply: bool,
    path: Path,
    data: dict,
    queries: list[dict],
    incremental: bool,
) -> tuple[str, str]:
    """Process one query: Opus then Sonnet, optionally apply. Returns (description, evidence)."""
    qnum = query.get("number", 0)
    idx = next((i for i, q in enumerate(queries) if q.get("number") == qnum), -1)
    if idx < 0:
        return "", ""

    opus_desc, opus_ev = call_opus_description_evidence(query, call_index)
    time.sleep(1)
    sonnet_desc, sonnet_ev = call_sonnet_description_evidence(
        query, opus_desc, opus_ev, call_index + 1
    )
    time.sleep(1)

    if apply:
        queries[idx]["description"] = sonnet_desc
        queries[idx]["evidence"] = sonnet_ev
        if incremental:
            save_queries(path, data, queries)

    return sonnet_desc, sonnet_ev


def run_db(
    db_num: int,
    apply: bool,
    incremental: bool,
    query_filter: int | None,
) -> int:
    """Process all (or filtered) queries for db-N. Returns 0 on success."""
    queries, path = load_queries(db_num)
    if not queries:
        print(f"No queries in db-{db_num}", file=sys.stderr)
        return 1

    path_full = get_queries_json_path(db_num)
    data = json.loads(path_full.read_text(encoding="utf-8")) if path_full.exists() else {"queries": queries}

    to_process = queries
    if query_filter is not None:
        to_process = [q for q in queries if q.get("number") == query_filter]
        if not to_process:
            print(f"Query {query_filter} not found in db-{db_num}", file=sys.stderr)
            return 1

    call_index = 0
    for q in to_process:
        qnum = q.get("number", 0)
        print(f"  db-{db_num} Q{qnum}: Opus + Sonnet...", flush=True)
        desc, ev = process_one_query(q, call_index, apply, path_full, data, queries, incremental)
        call_index += 2
        if ev:
            print(f"    -> {ev[:80]}...")
        else:
            print(f"    -> (empty)")

    if apply and not incremental:
        save_queries(path_full, data, queries)
        print(f"  Saved {path_full}")

    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Claude Opus+Sonnet evidence rewrite (natural language)")
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
