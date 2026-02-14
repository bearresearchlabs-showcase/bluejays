#!/usr/bin/env python3
"""Extract queries from queries.md → queries.json. Template config: template/template_config.yaml."""
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from timestamp_utils import get_est_timestamp

ROOT = scripts_dir.parent


def _find_queries_dir(db_dir: Path) -> Optional[Path]:
    for d in (db_dir / "app" / "QUERIES", db_dir / "queries", db_dir / "QUERIES"):
        if d.exists():
            return d
    return None


class QueryExtractor:
    """Backward-compat wrapper. Use extract_queries() for direct call."""
    def __init__(self, queries_file: Path):
        self.queries_file = queries_file
    def extract_all_queries(self) -> List[Dict]:
        return extract_queries(self.queries_file)


def extract_queries(md_path: Path) -> List[Dict]:
    """Extract queries from queries.md. Returns list of {number, title, description, complexity, expected_output, sql, line_number}."""
    content = md_path.read_text(encoding="utf-8")
    headers = list(re.finditer(r"^## Query (\d+):\s*(.+)$", content, re.MULTILINE))
    out = []
    for i, m in enumerate(headers):
        qnum, title = int(m.group(1)), m.group(2).strip()
        start, end = m.start(), headers[i + 1].start() if i + 1 < len(headers) else len(content)
        section = content[start:end]
        sql_m = re.search(r"```(?:sql)?\n(.*?)```", section, re.DOTALL)
        if not sql_m:
            continue
        desc_text = section[: sql_m.start()]
        desc_lines = [re.sub(r"\*\*([^*]+)\*\*", r"\1", re.sub(r"`([^`]+)`", r"\1", L.strip())) for L in desc_text.split("\n") if L.strip() and not L.startswith("#")]
        desc = " ".join(desc_lines).strip() or title
        cm = re.search(r"\*\*Complexity:\*\*\s*(.+?)(?:\n|$)", desc_text, re.I)
        em = re.search(r"\*\*Expected Output:\*\*\s*(.+?)(?:\n|$)", desc_text, re.I)
        complexity = (cm.group(1).strip() if cm else "") or ""
        expected = (em.group(1).strip() if em else "Query results") or "Query results"
        out.append({
            "number": qnum,
            "title": title,
            "description": (desc[:500] if desc else title[:200]),
            "complexity": complexity[:500] if complexity else "",
            "expected_output": expected[:200] if expected else "Query results",
            "sql": sql_m.group(1).strip(),
            "line_number": content[:start].count("\n") + 1,
        })
    return sorted(out, key=lambda x: x["number"])


def extract_db(db_num: int) -> Optional[Dict]:
    db_dir = ROOT / "source" / f"db-{db_num}"
    qd = _find_queries_dir(db_dir)
    if not qd:
        print(f"  db-{db_num}: no queries dir")
        return None
    qm, qj = qd / "queries.md", qd / "queries.json"
    if not qm.exists():
        print(f"  db-{db_num}: queries.md not found")
        return None
    queries = extract_queries(qm)
    if not queries:
        print(f"  db-{db_num}: no queries found")
        return None
    data = {"source_file": str(qm), "extraction_timestamp": get_est_timestamp(), "total_queries": len(queries), "queries": queries}
    qj.parent.mkdir(parents=True, exist_ok=True)
    qj.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"  db-{db_num}: {len(queries)} queries → {qj.name}")
    return data


def main():
    ap = __import__("argparse").ArgumentParser(description="Extract queries.md → queries.json")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or 1 2 3")
    ap.add_argument("-a", "--all", action="store_true", help="Extract db-1..db-16")
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
    print("Extracting queries to queries.json...")
    ok = sum(1 for n in db_nums if extract_db(n))
    print(f"\nDone: {ok}/{len(db_nums)} databases")
    return 0 if ok == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
