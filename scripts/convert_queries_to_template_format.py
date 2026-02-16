#!/usr/bin/env python3
"""Convert old-format queries to template format. Uses template/template_config.yaml."""
import json
import re
import sys
from pathlib import Path

try:
    from db_paths import ROOT, SOURCE
except ImportError:
    ROOT = Path(__file__).parent.parent
    SOURCE = ROOT / "source"

TEMPLATE = ROOT / "template"
CONFIG = TEMPLATE / "template_config.yaml"


def _load_config():
    """Load template_config.yaml if present."""
    if not CONFIG.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(CONFIG.read_text()) or {}
    except Exception:
        return {}


def _map_difficulty(complexity: str, cfg: dict) -> str:
    c = (complexity or "").lower()
    rules = cfg.get("difficulty_rules", {})
    for level, keywords in rules.items():
        if level == "default" or not isinstance(keywords, list):
            continue
        if any(kw in c for kw in keywords):
            return level
    # Fallback: original logic
    if "recursive" in c or ("cte" in c and "4" in c) or ("window" in c and "9" in c):
        return "challenging"
    if "cte" in c or "join" in c or "window" in c:
        return "challenging" if "4" in c or "3" in c else "moderate"
    return rules.get("default", "moderate")


def _infer_tables(sql: str) -> list[str]:
    tables = []
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)", sql.upper(), re.I):
        t = m.group(1).lower()
        if t not in ("SELECT", "WHERE", "ON", "AND", "OR", "AS", "WITH") and t not in tables:
            tables.append(t)
    return tables


def _infer_category(sql: str) -> str:
    s = sql.upper()
    if "WITH RECURSIVE" in s or "RECURSIVE" in s:
        return "recursive_cte"
    if any(f in s for f in ("ROW_NUMBER()", "RANK()", "DENSE_RANK()", "NTILE(")):
        return "window/ranking"
    if re.search(r"JOIN\s+\w+\s+ON\s+\w+\.\w+\s*=\s*\w+\.\w+", s) and "GROUP BY" in s:
        return "aggregation/ranking"
    if "GROUP BY" in s and "HAVING" in s:
        return "aggregation"
    if "GROUP BY" in s:
        return "aggregation"
    if "JOIN" in s:
        return "join"
    return "filtering/lookup"


def convert_query(old: dict, db_id: str, cfg: dict) -> dict:
    q = old.get("question") or old.get("use_case") or (old.get("description") or "").split("Use Case:")[-1].split("Business Value:")[0].strip()[:300] or old.get("title", "Query")
    if len(q) > 400:
        q = q[:397] + "..."
    num = old.get("number", old.get("question_id", 0))
    ev = (old.get("description") or old.get("evidence") or "")[:1000]
    sql = (old.get("sql") or "").strip()
    out = {
        "db_id": db_id,
        "question_id": num,
        "number": num,
        "question": q,
        "title": old.get("title", q[:80]),
        "description": ev,
        "sql": sql,
        "evidence": ev,
        "difficulty": old.get("difficulty") or _map_difficulty(old.get("complexity", ""), cfg),
        "complexity": old.get("complexity", ""),
        "expected_output": old.get("expected_output") or "[]",
        "schema_context": old.get("schema_context") or {},
        "tables_used": old.get("tables_used") or _infer_tables(sql),
        "query_category": old.get("query_category") or _infer_category(sql),
    }
    normal_query = (old.get("normal_query") or "").strip()
    if normal_query:
        out["normal_query"] = normal_query[:500]
    return out


def convert_db(db_num: int, cfg: dict) -> bool:
    db_id = f"db-{db_num}"
    db_dir = SOURCE / f"db-{db_num}"
    try:
        from db_paths import get_queries_dir
        qd = get_queries_dir(db_dir)
    except ImportError:
        qd = db_dir / "app" / "QUERIES" if (db_dir / "app" / "QUERIES").exists() else db_dir / "queries"
        if not qd.exists():
            qd = db_dir / "QUERIES"
    qj = qd / "queries.json"
    if not qj.exists():
        print(f"  {db_id}: SKIP (no queries.json)")
        return False
    try:
        data = json.loads(qj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  {db_id}: SKIP (invalid JSON: {e})")
        return False
    queries = data.get("queries", data) if isinstance(data, dict) else data
    if not queries:
        print(f"  {db_id}: SKIP (no queries)")
        return False
    converted = [convert_query(q, db_id, cfg) for q in queries]
    out = {"db_id": db_id, "source_file": str(qj), "extraction_timestamp": data.get("extraction_timestamp", ""), "total_queries": len(converted), "queries": converted}
    qj.write_text(json.dumps(out, indent=2, default=str))
    print(f"  {db_id}: OK ({len(converted)} queries)")
    return True


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Convert queries to template format")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ...")
    ap.add_argument("-a", "--all", action="store_true", help="Convert all db-1..db-16")
    args = ap.parse_args()
    cfg = _load_config()
    db_nums = list(range(1, 17)) if args.all or not args.dbs else []
    if not db_nums:
        for a in args.dbs:
            a = str(a).replace("db-", "")
            try:
                db_nums.append(int(a))
            except ValueError:
                pass
        if len(db_nums) == 2 and db_nums[0] < db_nums[1]:
            db_nums = list(range(db_nums[0], db_nums[1] + 1))
        db_nums = sorted(set(db_nums))
    print("Converting to template format (source/db-N/app/QUERIES/queries.json)...")
    ok = sum(1 for n in db_nums if convert_db(n, cfg))
    print(f"\nDone: {ok}/{len(db_nums)} databases converted")
    return 0 if ok == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
