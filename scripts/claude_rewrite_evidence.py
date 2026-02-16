#!/usr/bin/env python3
"""
Use Claude API (Opus for verification, Sonnet for rewriting) to verify and improve
natural language evidence/descriptions in BIRD query rewrites.

Loads ANTHROPIC_API_KEY from .env. Processes source/db-N/app/QUERIES/queries.md.

Usage:
  python3 claude_rewrite_evidence.py 1           # db-1 only
  python3 claude_rewrite_evidence.py 1 --apply  # rewrite and apply to queries.md
  python3 claude_rewrite_evidence.py 1 --dry-run  # verify only, no apply
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

# Model IDs - from Anthropic API models.list()
MODEL_OPUS = "claude-opus-4-6"               # Verification/judging (highest quality)
MODEL_SONNET = "claude-sonnet-4-5-20250929"  # Rewriting (faster, cheaper)


def _call_claude(prompt: str, model: str, max_tokens: int = 4096) -> str:
    """Call Claude API. Returns response text or raises."""
    from anthropic import Anthropic
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    client = Anthropic(api_key=key)
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text if resp.content else ""


def load_queries_from_md(db_num: int) -> list[dict]:
    """Load query blocks from source/db-N/app/QUERIES/queries.md."""
    md_path = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
    if not md_path.exists():
        return []
    text = md_path.read_text(encoding="utf-8")
    queries = []
    for m in re.finditer(r"```json\n(.*?)```", text, re.DOTALL):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        qid = obj.get("question_id")
        if not qid or qid < 1 or qid > 30:
            continue
        queries.append({
            "question_id": qid,
            "question": obj.get("question", ""),
            "normal_query": obj.get("normal_query", ""),
            "evidence": obj.get("evidence", ""),
            "SQL": (obj.get("SQL", "") or "")[:600],
            "expected_output": obj.get("expected_output", ""),
        })
    return sorted(queries, key=lambda q: q["question_id"])


def verify_evidence_batch(queries: list[dict], model: str) -> dict:
    """Use Claude to verify/judge accuracy of evidence. Returns {qid: {score, issues}}."""
    items = []
    for q in queries:
        items.append({
            "qid": q["question_id"],
            "question": q["question"],
            "normal_query": q["normal_query"],
            "evidence": q["evidence"],
        })
    prompt = f"""You are a BIRD benchmark expert. Review these query evidence texts for accuracy and natural language quality.

For each item, judge:
1. Accuracy: Does the evidence correctly describe what the query does? (1-5, 5=fully accurate)
2. Natural language: Is it readable and non-technical where appropriate? (1-5)
3. STAR structure: Are Situation, Task, Action, Result clearly present and fleshed out? (1-5)
4. Issues: Brief note on any problems (or "OK" if none)

Items:
{json.dumps(items, indent=2, ensure_ascii=False)}

Reply with a JSON object only, no markdown:
{{"verifications": [{{"qid": N, "accuracy": 1-5, "natural": 1-5, "star": 1-5, "issues": "..."}}]}}"""
    try:
        out = _call_claude(prompt, model, max_tokens=2048)
        # Extract JSON (handle possible markdown wrapper)
        out = out.strip()
        if out.startswith("```"):
            out = re.sub(r"^```\w*\n?", "", out)
            out = re.sub(r"\n?```$", "", out)
        data = json.loads(out)
        return {v["qid"]: v for v in data.get("verifications", [])}
    except Exception as e:
        print(f"Verify error: {e}", file=sys.stderr)
        return {}


def rewrite_evidence_batch(queries: list[dict], model: str) -> dict:
    """Use Claude to rewrite evidence in more natural language with full STAR. Returns {qid: {question, normal_query, evidence}}."""
    items = [{"qid": q["question_id"], "question": q["question"], "normal_query": q["normal_query"], "evidence": q["evidence"]} for q in queries]
    prompt = f"""You are a BIRD benchmark expert. Rewrite these query texts to be more natural and fully flesh out the STAR format (Situation, Task, Action, Result).

Requirements:
- Situation: Clear business/domain context, why the query is needed
- Task: What the query should accomplish (imperative, concise)
- Action: What the SQL does (CTEs, window functions, grouping) in plain language
- Result: What the query returns

Keep question and normal_query similar but improve natural language. Evidence must be fully fleshed out STAR.

Input:
{json.dumps(items, indent=2, ensure_ascii=False)}

Reply with a JSON object only, no markdown:
{{"rewrites": [{{"qid": N, "question": "...", "normal_query": "...", "evidence": "..."}}]}}"""
    try:
        out = _call_claude(prompt, model, max_tokens=8192)
        out = out.strip()
        if out.startswith("```"):
            out = re.sub(r"^```\w*\n?", "", out)
            out = re.sub(r"\n?```$", "", out)
        data = json.loads(out)
        return {r["qid"]: r for r in data.get("rewrites", [])}
    except Exception as e:
        print(f"Rewrite error: {e}", file=sys.stderr)
        return {}


def run_verify(db_num: int) -> dict:
    """Run Opus verification on all 30 queries (batched)."""
    queries = load_queries_from_md(db_num)
    if not queries:
        return {"error": f"No queries in db-{db_num}"}
    all_verifications = {}
    batch_size = 10
    for i in range(0, len(queries), batch_size):
        batch = queries[i : i + batch_size]
        verifications = verify_evidence_batch(batch, MODEL_OPUS)
        all_verifications.update(verifications)
        time.sleep(1)  # rate limit
    return {"verifications": all_verifications, "queries": queries}


def run_rewrite(db_num: int) -> dict:
    """Run Sonnet rewrite on all 30 queries (batched)."""
    queries = load_queries_from_md(db_num)
    if not queries:
        return {"error": f"No queries in db-{db_num}"}
    all_rewrites = {}
    batch_size = 5
    for i in range(0, len(queries), batch_size):
        batch = queries[i : i + batch_size]
        rewrites = rewrite_evidence_batch(batch, MODEL_SONNET)
        all_rewrites.update(rewrites)
        time.sleep(1)
    return {"rewrites": all_rewrites, "queries": queries}


def apply_rewrites(db_num: int, rewrites: dict) -> bool:
    """Apply rewrites to queries.md."""
    md_path = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
    if not md_path.exists():
        return False
    text = md_path.read_text(encoding="utf-8")

    def replace_block(m):
        raw = m.group(1)
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return m.group(0)
        qid = obj.get("question_id")
        if qid not in rewrites:
            return m.group(0)
        r = rewrites[qid]
        obj["question"] = r.get("question", obj.get("question", ""))
        obj["normal_query"] = r.get("normal_query", obj.get("normal_query", ""))
        obj["evidence"] = r.get("evidence", obj.get("evidence", ""))
        return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"

    new_text = re.sub(r"```json\n(.*?)```", replace_block, text, flags=re.DOTALL)
    md_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Claude verify + rewrite evidence for BIRD queries")
    ap.add_argument("db", type=int, nargs="?", default=1, help="Database number (1-16)")
    ap.add_argument("--verify-only", action="store_true", help="Only run verification (Opus), no rewrite")
    ap.add_argument("--rewrite-only", action="store_true", help="Only run rewrite (Sonnet), skip verify")
    ap.add_argument("--apply", action="store_true", help="Apply rewrites to queries.md")
    ap.add_argument("--dry-run", action="store_true", help="Verify only, print results, no apply")
    ap.add_argument("--output", type=str, help="Write rewrites JSON to file")
    args = ap.parse_args()

    db_num = args.db
    if db_num < 1 or db_num > 16:
        print("Invalid db. Use 1-16.", file=sys.stderr)
        return 1

    # Verify
    if not args.rewrite_only:
        print(f"--- Verifying db-{db_num} (Opus) ---")
        verify_result = run_verify(db_num)
        if "error" in verify_result:
            print(verify_result["error"], file=sys.stderr)
            return 1
        verifications = verify_result.get("verifications", {})
        for qid in sorted(verifications.keys()):
            v = verifications[qid]
            print(f"  Q{qid}: accuracy={v.get('accuracy','?')} natural={v.get('natural','?')} star={v.get('star','?')} | {v.get('issues','')[:60]}")
        if args.dry_run:
            return 0

    # Rewrite
    if not args.verify_only:
        print(f"\n--- Rewriting db-{db_num} (Sonnet) ---")
        rewrite_result = run_rewrite(db_num)
        if "error" in rewrite_result:
            print(rewrite_result["error"], file=sys.stderr)
            return 1
        rewrites = rewrite_result.get("rewrites", {})
        print(f"  Rewrote {len(rewrites)} queries")

        if args.output:
            out_path = Path(args.output)
            out_path.write_text(json.dumps({"db_num": db_num, "rewrites": rewrites}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  Wrote {out_path}")

        if args.apply:
            if apply_rewrites(db_num, rewrites):
                print(f"  Applied to {REPO / 'source' / f'db-{db_num}' / 'app' / 'QUERIES' / 'queries.md'}")
            else:
                print("  Apply failed.", file=sys.stderr)
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
