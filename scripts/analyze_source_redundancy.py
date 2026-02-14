#!/usr/bin/env python3
"""
Analyze source/db-N for files needed vs redundant for app/ generation.

The app/ output (DATABASE/, DOCUMENTATION/, QUERIES/) is built by:
  format.py: DELIVERABLE.md|_doc_config + queries.md → deliverable/db-N.md
  populate_app_trifecta.py: data/ + deliverable/ + queries|QUERIES → app/

Minimal inputs for app/ generation:
  - DELIVERABLE.md or _doc_config.yaml
  - data/ (schema.sql, data.sql, etc.)
  - queries/ or QUERIES/ or app/QUERIES (queries.md, queries.json)

Redundant for app/ (can be archived or removed):
  - research/, results/, validation/, metadata/, scripts/, docs/, package/
  - deliverable/README.md, deliverable/DELIVERABLE.md, deliverable/database_deliverable.json
  - Root deliverable.openapi.yaml, *.zip, *.backup, golden_findings.json, etc.

Usage:
  python3 scripts/analyze_source_redundancy.py -a
  python3 scripts/analyze_source_redundancy.py db-1 db-5 -j
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"


def analyze_db(db_num: int) -> dict:
    """Analyze a single db-N directory."""
    db_dir = SOURCE / f"db-{db_num}"
    if not db_dir.exists():
        return {"db": f"db-{db_num}", "exists": False}

    # Required inputs for format + populate
    required = {
        "doc_input": None,  # DELIVERABLE.md or _doc_config
        "queries": None,    # queries.md, queries.json
        "data": [],         # schema.sql, data.sql, etc.
    }
    # Generated outputs (needed by populate)
    generated = {
        "deliverable_md": None,
        "web_folder": None,
        "app": None,
    }
    # Redundant (not needed for app/ generation)
    redundant = []

    # Doc input
    for name in ("_doc_config.yaml", "_doc_config.yml", "_doc_config.json", "DELIVERABLE.md"):
        p = db_dir / name
        if p.exists():
            required["doc_input"] = str(p.relative_to(db_dir))
            break

    # Queries
    for qd in (db_dir / "app" / "QUERIES", db_dir / "QUERIES", db_dir / "queries"):
        if qd.exists():
            qm, qj = qd / "queries.md", qd / "queries.json"
            required["queries"] = [str(qm.relative_to(db_dir)) if qm.exists() else None,
                                  str(qj.relative_to(db_dir)) if qj.exists() else None]
            break

    # Data (from data/ or deliverable/data)
    for base in (db_dir / "data", db_dir / "deliverable" / "data"):
        if base.exists():
            for f in base.iterdir():
                if f.is_file() and f.suffix.lower() == ".sql":
                    required["data"].append(str(f.relative_to(db_dir)))

    # Generated
    if (db_dir / "deliverable" / f"db-{db_num}.md").exists():
        generated["deliverable_md"] = f"deliverable/db-{db_num}.md"
    prefix = f"db{db_num}-"
    for item in (db_dir / "deliverable").iterdir() if (db_dir / "deliverable").exists() else []:
        if item.is_dir() and item.name.startswith(prefix):
            generated["web_folder"] = f"deliverable/{item.name}"
            break
    if (db_dir / "app" / "DATABASE").exists():
        generated["app"] = "app/"

    # Redundant: not used by format or populate for app/ generation
    redundant_dir_prefixes = ("research/", "results/", "validation/", "metadata/", "scripts/", "docs/", "package/")

    def is_redundant(p: str) -> bool:
        if p.startswith("app/"):
            return False
        if any(p.startswith(prefix) or p == prefix.rstrip("/") for prefix in redundant_dir_prefixes):
            return True
        if p.endswith(".zip") or p.endswith(".backup") or ".colab_" in p:
            return True
        if p in ("deliverable.openapi.yaml", "deliverable/README.md", "deliverable/DELIVERABLE.md",
                 "deliverable/database_deliverable.json", "golden_findings.json", "db6_complete_dump.sql"):
            return True
        return False

    for root, _dirs, files in db_dir.walk():
        try:
            rel = Path(root).relative_to(db_dir)
        except ValueError:
            continue
        rel_str = str(rel).replace("\\", "/")
        if rel_str == ".":
            rel_str = ""
        for f in files:
            r = f"{rel_str}/{f}" if rel_str else f
            r = r.lstrip("/")
            if is_redundant(r):
                redundant.append(r)
        for d in _dirs:
            r = f"{rel_str}/{d}" if rel_str else d
            r = r.lstrip("/") + "/"
            if is_redundant(r):
                redundant.append(r)

    redundant = sorted(set(redundant))

    return {
        "db": f"db-{db_num}",
        "exists": True,
        "required": required,
        "generated": generated,
        "redundant_count": len(redundant),
        "redundant_sample": redundant[:30],
        "all_redundant": redundant,
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Analyze source/db-N redundancy for app/ generation")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all")
    ap.add_argument("-a", "--all", action="store_true", help="All db-1..db-16")
    ap.add_argument("-j", "--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    db_nums = list(range(1, 17)) if args.all or not args.dbs else []
    if not db_nums:
        for a in args.dbs:
            a = str(a).replace("db-", "")
            try:
                db_nums.append(int(a))
            except ValueError:
                pass
        db_nums = sorted(set(db_nums))

    results = [analyze_db(n) for n in db_nums]

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    for r in results:
        if not r.get("exists"):
            print(f"\n{r['db']}: NOT FOUND")
            continue
        print(f"\n{'='*60}\n{r['db']}")
        print("  Required for app/ generation:")
        print(f"    doc_input: {r['required']['doc_input']}")
        print(f"    queries: {r['required']['queries']}")
        print(f"    data: {len(r['required']['data'])} SQL files")
        print("  Generated:")
        print(f"    deliverable: {r['generated']['deliverable_md']}")
        print(f"    web_folder: {r['generated']['web_folder']}")
        print(f"    app: {r['generated']['app']}")
        print(f"  Redundant (not needed for app/): {r['redundant_count']} items")
        for x in r["redundant_sample"][:15]:
            print(f"    - {x}")
        if r["redundant_count"] > 15:
            print(f"    ... and {r['redundant_count'] - 15} more")

    total_red = sum(x.get("redundant_count", 0) for x in results if x.get("exists"))
    print(f"\n{'='*60}\nSummary: {total_red} redundant items across {len([x for x in results if x.get('exists')])} databases")
    print("  Minimal for app/: DELIVERABLE|_doc_config + data/ + queries/ → format → populate → app/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
