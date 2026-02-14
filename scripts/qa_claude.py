#!/usr/bin/env python3
"""
Claude QA: Sonnet 4.5 for quick validation, Opus 4.6 with thinking for research.
--task validate: syntax check, format validation
--task research: reasoning about schema, query quality, BIRD alignment
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

from env_validator import load_env, ensure_env
load_env()
if not ensure_env("claude"):
    sys.exit(1)


def load_queries(db_num: int) -> Optional[dict]:
    """Load queries.json for db-N."""
    try:
        from db_paths import get_queries_dir
        path = get_queries_dir(root_dir / "source" / f"db-{db_num}") / "queries.json"
    except ImportError:
        d = root_dir / "source" / f"db-{db_num}"
        path = (d / "app" / "QUERIES" / "queries.json") if (d / "app" / "QUERIES").exists() else d / "queries" / "queries.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(db_num: int) -> str:
    """Load schema for db-N."""
    db_dir = root_dir / "source" / f"db-{db_num}"
    try:
        from db_paths import get_data_dir
        data_dir = get_data_dir(db_dir)
    except ImportError:
        data_dir = db_dir / "data"
    for name in ("schema.sql", "schema_postgresql.sql"):
        p = data_dir / name
        if p.exists():
            return p.read_text(encoding="utf-8")[:8000]
    return ""


def run_validate(db_num: int, model: str) -> dict:
    """Quick validation: syntax check, format validation."""
    queries = load_queries(db_num)
    schema = load_schema(db_num)
    if not queries:
        return {"db_id": f"db-{db_num}", "error": "no queries.json"}
    qs = queries.get("queries", [])[:5]
    prompt = f"""Review this database schema and sample queries for db-{db_num}.

Schema (excerpt):
{schema[:4000]}

Sample queries (first 5):
{json.dumps([{"number": q.get("number"), "title": q.get("title"), "sql": (q.get("sql") or "")[:500]} for q in qs], indent=2)}

Perform a quick validation:
1. Syntax: Do the SQL snippets look valid (no obvious syntax errors)?
2. Format: Do queries have required fields (question/use_case, sql)?
3. BIRD alignment: Would these work as BIRD question-SQL pairs?

Reply with a brief validation report (3-5 sentences)."""
    return _call_claude(prompt, model, max_tokens=1024)


def run_research(db_num: int, model: str) -> dict:
    """Deep research: schema quality, query quality, BIRD alignment."""
    queries = load_queries(db_num)
    schema = load_schema(db_num)
    if not queries:
        return {"db_id": f"db-{db_num}", "error": "no queries.json"}
    qs = queries.get("queries", [])[:3]
    prompt = f"""Review this database (db-{db_num}) for schema quality, query quality, and BIRD benchmark alignment.

Schema:
{schema[:6000]}

Sample queries:
{json.dumps([{"number": q.get("number"), "title": q.get("title"), "description": (q.get("description") or "")[:200], "sql": (q.get("sql") or "")[:400]} for q in qs], indent=2)}

Provide a research-style analysis:
1. Schema: Are tables well-structured? Any missing indexes or constraints?
2. Query quality: Complexity, CTE usage, edge cases?
3. BIRD alignment: Would these work in BIRD/BIRD-CRITIC? What improvements would help?

Be thorough but concise (1-2 paragraphs)."""
    return _call_claude(prompt, model, max_tokens=2048)


def _call_claude(prompt: str, model: str, max_tokens: int = 1024) -> dict:
    """Call Claude API. Returns dict with response or error."""
    try:
        from anthropic import Anthropic
    except ImportError:
        return {"error": "pip install anthropic"}
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return {"error": "ANTHROPIC_API_KEY not set"}
    try:
        client = Anthropic(api_key=key)
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text if resp.content else ""
        return {"response": text, "model": model}
    except Exception as e:
        return {"error": str(e)[:300], "model": model}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["sonnet", "opus"], default="sonnet")
    ap.add_argument("--task", choices=["validate", "research"], default="validate")
    ap.add_argument("--db", type=str, default="db-1")
    ap.add_argument("-a", "--all", action="store_true")
    args = ap.parse_args()

    # Sonnet 4.5 for quick verification; Opus 4.6 for research (with thinking)
    model_map = {"sonnet": "claude-sonnet-4-5-20250514", "opus": "claude-opus-4-6-20250514"}
    model = model_map.get(args.model, "claude-sonnet-4-5-20250514")

    if args.all:
        db_nums = list(range(1, 17))
    else:
        try:
            db_nums = [int(args.db.replace("db-", ""))]
        except ValueError:
            print("Invalid db. Use db-1 or -a for all")
            return 1

    for n in db_nums:
        print(f"\n--- db-{n} ({args.task}, {args.model}) ---")
        if args.task == "validate":
            out = run_validate(n, model)
        else:
            out = run_research(n, model)
        if "error" in out:
            print(f"  Error: {out['error']}")
            continue
        if "response" in out:
            print(out["response"][:1500])
            if len(out.get("response", "")) > 1500:
                print("...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
