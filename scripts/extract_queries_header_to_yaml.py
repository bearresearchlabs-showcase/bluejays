#!/usr/bin/env python3
"""
Extract queries.md header sections to source/db-N/queries_header.yaml.

Reads existing queries.md, extracts Database Overview, Purpose, Use Case,
Business Value, Schema, Domain Knowledge, Query Difficulty Distribution,
and writes source/db-N/queries_header.yaml (top level, NOT in app).

Use for migration: create queries_header.yaml from existing queries.md
so the build workflow can use it as the source of truth.

Usage:
    python3 scripts/extract_queries_header_to_yaml.py [db-1] [db-5] | -a
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
sys.path.insert(0, str(Path(__file__).parent))

try:
    from db_paths import get_queries_dir
except ImportError:

    def get_queries_dir(db_dir: Path) -> Path:
        app = db_dir / "app"
        if app.exists() and (app / "QUERIES").exists():
            return app / "QUERIES"
        if (db_dir / "QUERIES").exists():
            return db_dir / "QUERIES"
        return db_dir / "queries"


SECTIONS = [
    "Database Overview",
    "Purpose",
    "Use Case",
    "Business Value",
    "Schema",
    "Domain Knowledge",
    "Query Difficulty Distribution",
]


def _extract_section(content: str, section_name: str) -> str | None:
    """Extract section content (inside code block) from ## Section to next ##."""
    pattern = rf"^## {re.escape(section_name)}\s*\n```(?:yaml|text|sql)\n(.*?)```"
    m = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def _extract_db_name(content: str) -> str:
    """Extract db name from # Title — Query Documentation."""
    m = re.match(r"^#\s+(.+?)\s*—\s*Query Documentation", content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_db(db_num: int) -> bool:
    """Extract header from queries.md to queries_header.yaml for one db."""
    db_id = f"db-{db_num}"
    db_dir = SOURCE / f"db-{db_num}"
    queries_dir = get_queries_dir(db_dir)
    qm = queries_dir / "queries.md"
    out_path = db_dir / "queries_header.yaml"

    if not qm.exists():
        print(f"  {db_id}: SKIP (no queries.md)")
        return False

    content = qm.read_text(encoding="utf-8")
    db_name = _extract_db_name(content)
    if not db_name:
        print(f"  {db_id}: SKIP (no title found)")
        return False

    sections = {}
    for name in SECTIONS:
        val = _extract_section(content, name)
        if val:
            sections[name] = val

    if not sections:
        print(f"  {db_id}: SKIP (no sections extracted)")
        return False

    # Build YAML (use literal block for multi-line)
    lines = [f'# Extracted from {qm.relative_to(ROOT)}', f"db_name: \"{db_name}\"", ""]
    key_map = {
        "Database Overview": "database_overview",
        "Purpose": "purpose",
        "Use Case": "use_case",
        "Business Value": "business_value",
        "Schema": "schema",
        "Domain Knowledge": "domain_knowledge",
        "Query Difficulty Distribution": "query_difficulty_distribution",
    }
    for name, key in key_map.items():
        if name in sections:
            val = sections[name]
            lines.append(f"{key}: |")
            for ln in val.split("\n"):
                lines.append(f"  {ln}")
            lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"  {db_id}: OK -> {out_path.relative_to(ROOT)}")
    return True


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Extract queries.md header to queries_header.yaml")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all")
    ap.add_argument("-a", "--all", action="store_true", help="Extract all db-1..db-16")
    args = ap.parse_args()

    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = []
        for a in args.dbs:
            a = str(a).replace("db-", "")
            try:
                db_nums.append(int(a))
            except ValueError:
                pass
        db_nums = sorted(set(db_nums))

    print("Extracting queries.md header to source/db-N/queries_header.yaml...")
    ok = sum(1 for n in db_nums if extract_db(n))
    print(f"\nDone: {ok}/{len(db_nums)} databases")
    return 0 if ok == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
