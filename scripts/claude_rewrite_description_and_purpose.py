#!/usr/bin/env python3
"""
Rewrite query description (natural language: Who/What/Where/When/Why) and add
purpose, use_case, business_value with deep rationale. Uses Claude API.

Incremental: one API call per query. Claude reads DB schema + full SQL, then
writes natural language relative to the query's tables, columns, and logic.
API client is refreshed for each call so each JSON value is independent.

Reads/writes: source/db-N/app/QUERIES/queries.json and queries.md (JSON blocks).

Usage:
  python3 scripts/claude_rewrite_description_and_purpose.py 1           # db-1, dry run
  python3 scripts/claude_rewrite_description_and_purpose.py 1 --apply   # write changes
  python3 scripts/claude_rewrite_description_and_purpose.py -a --apply  # all db-1..16
  python3 scripts/claude_rewrite_description_and_purpose.py 1 --apply --incremental  # save after each query
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

load_env()
if not ensure_env("claude"):
    sys.exit(1)

REPO = root_dir
MODEL = "claude-sonnet-4-5-20250929"
SESSION_PAUSE_SEC = 3  # Pause between databases (fresh session per db)


def _call_claude_fresh(prompt: str, max_tokens: int = 8192) -> str:
    """Fresh API client per call so each JSON value is independent."""
    from anthropic import Anthropic
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    client = Anthropic(api_key=key)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text if resp.content else ""


def load_schema(db_num: int) -> str:
    """Load DB schema from app/DATABASE or data/ for context."""
    for rel in ["app/DATABASE/schema.sql", "data/schema.sql"]:
        path = REPO / "source" / f"db-{db_num}" / rel
        if path.exists():
            return path.read_text(encoding="utf-8")[:8000]
    return ""


def load_queries_json(db_num: int) -> list[dict] | None:
    path = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("queries", [])


def save_queries_json(db_num: int, data: dict) -> None:
    path = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _parse_rewrite_json(out: str) -> dict | None:
    """Parse Claude JSON response; fix trailing commas; retry once."""
    out = out.strip()
    if out.startswith("```"):
        out = re.sub(r"^```\w*\n?", "", out)
        out = re.sub(r"\n?```$", "", out)
    for attempt in range(2):
        try:
            cleaned = re.sub(r",\s*([}\]])", r"\1", out)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            if attempt == 0:
                out = re.sub(r",\s*([}\]])", r"\1", out)
                continue
            return None
    return None


def rewrite_single_query(q: dict, schema: str, db_id: str) -> dict | None:
    """
    One API call per query. Claude reads DB schema + full SQL, then writes
    natural language relative to the query's tables, columns, and logic.
    Fresh API client per call.
    """
    sql = (q.get("sql") or "")[:6000]
    question = (q.get("question") or "")[:500]
    normal_query = (q.get("normal_query") or "")[:400]
    expected_output = (q.get("expected_output") or "")[:300]
    schema_block = f"\n\nDatabase schema (tables, columns):\n```sql\n{schema}\n```\n" if schema else ""
    prompt = f"""FRESH SESSION: This request is for database {db_id} only. Do not use information from any other database.

You are a BIRD benchmark and product expert. Read the database schema and the SQL query below. Write natural language that describes what this query does, relative to its tables, columns, CTEs, and logic.
{schema_block}

SQL query:
```sql
{sql}
```

Natural language question: {question}
Normalized task: {normal_query}
Expected output: {expected_output}

Produce a JSON object with exactly these keys:
- "number": {q.get("number", 0)}
- "description": One clear task in natural language. Answer Who, What, Where, When, and Why with deep context. Write 2–4 sentences. No bullet points; flowing prose. Reference the actual tables and columns used in the SQL.
- "purpose": One sentence on the reason this query exists, with deep rationale (why it matters to the business).
- "use_case": One concrete use case (who uses it, in what situation) with deep rationale.
- "business_value": The deliverable or outcome (revenue, risk, efficiency) with deep rationale.

Keep tone professional and natural. No markdown in the field values.

Reply with a JSON object only. No other text.
{{"number": {q.get("number", 0)}, "description": "...", "purpose": "...", "use_case": "...", "business_value": "..."}}"""
    out = _call_claude_fresh(prompt, max_tokens=4096)
    parsed = _parse_rewrite_json(out)
    if parsed and isinstance(parsed, dict):
        return parsed
    # Try extracting single object from array
    if parsed and isinstance(parsed, list) and len(parsed) == 1:
        return parsed[0]
    print(f"  Query {q.get('number')}: Claude JSON parse failed", file=sys.stderr)
    return None


def apply_rewrites(queries: list[dict], rewrites: list[dict]) -> list[dict]:
    by_num = {r["number"]: r for r in rewrites}
    out = []
    for q in queries:
        q = dict(q)
        r = by_num.get(q["number"])
        if r:
            q["description"] = (r.get("description") or q.get("description") or "")[:600]
            if r.get("purpose"):
                q["purpose"] = (r["purpose"] or "")[:800]
            if r.get("use_case"):
                q["use_case"] = (r["use_case"] or "")[:800]
            if r.get("business_value"):
                q["business_value"] = (r["business_value"] or "")[:800]
        out.append(q)
    return out


def update_queries_md(db_num: int, queries: list[dict]) -> None:
    """Update JSON blocks in queries.md to include description, purpose, use_case, business_value."""
    path = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    by_num = {q["number"]: q for q in queries}

    def replace_block(m):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            return m.group(0)
        qnum = obj.get("question_id", obj.get("number"))
        q = by_num.get(qnum)
        if not q:
            return m.group(0)
        obj["description"] = q.get("description", "")
        if q.get("purpose"):
            obj["purpose"] = q["purpose"]
        if q.get("use_case"):
            obj["use_case"] = q["use_case"]
        if q.get("business_value"):
            obj["business_value"] = q["business_value"]
        return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"

    new_text = re.sub(r"```(?:json)?\n(.*?)```", replace_block, text, flags=re.DOTALL)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")


def run_db(db_num: int, apply: bool, incremental: bool, limit: int = 0) -> bool:
    data = {"source_file": "", "extraction_timestamp": "", "total_queries": 0, "queries": load_queries_json(db_num)}
    if not data["queries"]:
        print(f"  db-{db_num}: no queries.json or no queries")
        return False
    queries = data["queries"]
    if limit > 0:
        queries = queries[:limit]
        print(f"  db-{db_num}: processing first {limit} queries only")
    db_id = f"db-{db_num}"
    schema = load_schema(db_num)
    if not schema:
        print(f"  db-{db_num}: no schema found (app/DATABASE or data/)")
    all_rewrites = []
    for i, q in enumerate(queries):
        r = rewrite_single_query(q, schema, db_id)
        if r:
            all_rewrites.append(r)
        if incremental and apply and r:
            data["queries"] = apply_rewrites(data["queries"], all_rewrites)
            existing_path = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
            if existing_path.exists():
                existing = json.loads(existing_path.read_text(encoding="utf-8"))
                data["source_file"] = existing.get("source_file", data["source_file"])
                data["extraction_timestamp"] = existing.get("extraction_timestamp", data["extraction_timestamp"])
            data["total_queries"] = len(data["queries"])
            save_queries_json(db_num, data)
        time.sleep(0.8)
    if len(all_rewrites) != len(queries):
        print(f"  db-{db_num}: got {len(all_rewrites)} rewrites, expected {len(queries)}")
    data["queries"] = apply_rewrites(data["queries"], all_rewrites)
    if apply:
        existing_path = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.json"
        if existing_path.exists():
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            data["source_file"] = existing.get("source_file", data["source_file"])
            data["extraction_timestamp"] = existing.get("extraction_timestamp", data["extraction_timestamp"])
        data["total_queries"] = len(data["queries"])
        save_queries_json(db_num, data)
        update_queries_md(db_num, data["queries"])
        print(f"  db-{db_num}: applied {len(all_rewrites)} rewrites to queries.json and queries.md")
    else:
        print(f"  db-{db_num}: would apply {len(all_rewrites)} rewrites (use --apply to write)")
    return True


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Rewrite description and purpose/use_case/business_value via Claude")
    ap.add_argument("dbs", nargs="*", help="db numbers e.g. 1 2 or -a for all")
    ap.add_argument("-a", "--all", action="store_true", help="db-1..16")
    ap.add_argument("--apply", action="store_true", help="Write to queries.json and queries.md")
    ap.add_argument("--incremental", action="store_true", help="Save after each query (resume-friendly)")
    ap.add_argument("--limit", type=int, default=0, help="Process only first N queries per db (0=all)")
    args = ap.parse_args()
    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = [int(x) for x in args.dbs if str(x).isdigit()]
    if not db_nums:
        print("Specify db numbers or -a")
        sys.exit(1)
    print("Claude rewrite: one API call per query, schema+SQL context, fresh client each call")
    print("Output: description (Who/What/Where/When/Why) + purpose, use_case, business_value")
    print(f"Apply: {args.apply}  Incremental save: {args.incremental}\n")
    ok = 0
    for i, n in enumerate(db_nums):
        if i > 0:
            print(f"  ... pause {SESSION_PAUSE_SEC}s (fresh session for db-{n}) ...")
            time.sleep(SESSION_PAUSE_SEC)
        if run_db(n, args.apply, args.incremental, args.limit):
            ok += 1
    print(f"\nDone: {ok}/{len(db_nums)}")
    sys.exit(0 if ok == len(db_nums) else 1)


if __name__ == "__main__":
    main()
