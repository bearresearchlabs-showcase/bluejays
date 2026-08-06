#!/usr/bin/env python3
"""
QA Audit for client/db - Quality assurance checks on client deliverable structure.
Checks: DATABASE/, DOCUMENTATION/, QUERIES/ structure, file completeness, query counts.
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CLIENT_DB = BASE_DIR / "client" / "db"


def get_client_dbs() -> list:
    """List all db-N directories in client/db."""
    if not CLIENT_DB.exists():
        return []
    return sorted([d.name for d in CLIENT_DB.iterdir() if d.is_dir() and d.name.startswith("db-")])


def audit_database(db_name: str) -> dict:
    """Audit a single database in client/db."""
    db_dir = CLIENT_DB / db_name
    result = {
        "database": db_name,
        "exists": db_dir.exists(),
        "structure": {},
        "database_dir": {},
        "documentation_dir": {},
        "queries_dir": {},
        "queries_count": 0,
        "queries_with_sql": 0,
        "issues": [],
        "Pass": 1,
    }

    if not db_dir.exists():
        result["issues"].append("Directory missing")
        result["Pass"] = 0
        return result

    # DATABASE/ folder
    db_folder = db_dir / "DATABASE"
    result["database_dir"]["exists"] = db_folder.exists()
    if db_folder.exists():
        schema = db_folder / "schema.sql"
        schema_pg = db_folder / "schema_postgresql.sql"
        data = db_folder / "data.sql"
        result["database_dir"]["schema.sql"] = schema.exists()
        result["database_dir"]["schema_postgresql.sql"] = schema_pg.exists()
        result["database_dir"]["data.sql"] = data.exists()
        if not schema.exists() and not schema_pg.exists():
            result["issues"].append("No schema.sql or schema_postgresql.sql")
            result["Pass"] = 0
    else:
        result["issues"].append("DATABASE/ missing")
        result["Pass"] = 0

    # DOCUMENTATION/ folder
    doc_folder = db_dir / "DOCUMENTATION"
    result["documentation_dir"]["exists"] = doc_folder.exists()
    if doc_folder.exists():
        db_num = db_name.replace("db-", "")
        html = doc_folder / f"db-{db_num}_documentation.html"
        json_doc = doc_folder / f"db-{db_num}_deliverable.json"
        md = doc_folder / f"db-{db_num}.md"
        result["documentation_dir"]["html"] = html.exists()
        result["documentation_dir"]["json"] = json_doc.exists()
        result["documentation_dir"]["md"] = md.exists()
        if not html.exists():
            result["issues"].append("_documentation.html missing")
            result["Pass"] = 0
        if not json_doc.exists():
            result["issues"].append("_deliverable.json missing")
            result["Pass"] = 0
    else:
        result["issues"].append("DOCUMENTATION/ missing")
        result["Pass"] = 0

    # QUERIES/ folder
    queries_folder = db_dir / "QUERIES"
    result["queries_dir"]["exists"] = queries_folder.exists()
    if queries_folder.exists():
        queries_md = queries_folder / "queries.md"
        queries_json = queries_folder / "queries.json"
        result["queries_dir"]["queries.md"] = queries_md.exists()
        result["queries_dir"]["queries.json"] = queries_json.exists()

        if queries_json.exists():
            try:
                with open(queries_json, encoding="utf-8") as f:
                    data = json.load(f)
                queries = data.get("queries", [])
                result["queries_count"] = len(queries)
                result["queries_with_sql"] = sum(1 for q in queries if (q.get("sql") or "").strip())
                if len(queries) != 30:
                    result["issues"].append(f"Expected 30 queries, found {len(queries)}")
                    result["Pass"] = 0
                if result["queries_with_sql"] < len(queries):
                    result["issues"].append(f"{len(queries) - result['queries_with_sql']} queries have empty SQL")
                    result["Pass"] = 0
            except Exception as e:
                result["issues"].append(f"queries.json parse error: {e}")
                result["Pass"] = 0
        else:
            result["issues"].append("queries.json missing")
            result["Pass"] = 0

        if not queries_md.exists():
            result["issues"].append("queries.md missing")
            result["Pass"] = 0
    else:
        result["issues"].append("QUERIES/ missing")
        result["Pass"] = 0

    # vercel.json
    vercel = db_dir / "vercel.json"
    result["structure"]["vercel.json"] = vercel.exists()
    if not vercel.exists():
        result["issues"].append("vercel.json missing")

    return result


def main():
    """Run QA audit and print table report."""
    dbs = get_client_dbs()
    if not dbs:
        print("No client/db databases found.")
        return

    print("\n" + "=" * 120)
    print("QA AUDIT: client/db")
    print("=" * 120)

    results = [audit_database(db) for db in dbs]

    # Table 1: Structure
    print("\n┌────────┬──────────┬─────────────┬─────────────────┬─────────────┬──────────┬──────────────┐")
    print("│ DB     │ DATABASE/ │ DOCUMENTATION│ QUERIES/        │ schema.sql  │ data.sql │ vercel.json   │")
    print("├────────┼──────────┼─────────────┼─────────────────┼─────────────┼──────────┼──────────────┤")
    for r in results:
        db = r["database"]
        db_ok = "✓" if r["database_dir"].get("exists") else "✗"
        doc_ok = "✓" if r["documentation_dir"].get("exists") else "✗"
        q_ok = "✓" if r["queries_dir"].get("exists") else "✗"
        schema_ok = "✓" if r["database_dir"].get("schema.sql") or r["database_dir"].get("schema_postgresql.sql") else "✗"
        data_ok = "✓" if r["database_dir"].get("data.sql") else "✗"
        vercel_ok = "✓" if r["structure"].get("vercel.json") else "✗"
        print(f"│ {db:<6} │ {db_ok:^8} │ {doc_ok:^11} │ {q_ok:^15} │ {schema_ok:^11} │ {data_ok:^8} │ {vercel_ok:^12} │")
    print("└────────┴──────────┴─────────────┴─────────────────┴─────────────┴──────────┴──────────────┘")

    # Table 2: Documentation & Queries
    print("\n┌────────┬────────────────────┬────────────────────┬──────────┬──────────────┬───────┐")
    print("│ DB     │ html               │ json               │ queries  │ with SQL     │ Pass  │")
    print("├────────┼────────────────────┼────────────────────┼──────────┼──────────────┼───────┤")
    for r in results:
        db = r["database"]
        html_ok = "✓" if r["documentation_dir"].get("html") else "✗"
        json_ok = "✓" if r["documentation_dir"].get("json") else "✗"
        q_cnt = r["queries_count"]
        sql_cnt = r["queries_with_sql"]
        pass_icon = "✓" if r["Pass"] == 1 else "✗"
        print(f"│ {db:<6} │ {html_ok:^18} │ {json_ok:^18} │ {q_cnt:>8} │ {sql_cnt:>12} │ {pass_icon:^5} │")
    print("└────────┴────────────────────┴────────────────────┴──────────┴──────────────┴───────┘")

    # Issues summary
    has_issues = [r for r in results if r["issues"]]
    if has_issues:
        print("\n┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("│ ISSUES                                                                                               │")
        print("├────────┬─────────────────────────────────────────────────────────────────────────────────────────────┤")
        for r in has_issues:
            issues_str = "; ".join(r["issues"][:3])
            if len(r["issues"]) > 3:
                issues_str += f" (+{len(r['issues'])-3} more)"
            print(f"│ {r['database']:<6} │ {issues_str:<75} │")
        print("└────────┴─────────────────────────────────────────────────────────────────────────────────────────────┘")

    # Summary
    passed = sum(1 for r in results if r["Pass"] == 1)
    failed = len(results) - passed
    print(f"\nSUMMARY: {passed} passed, {failed} failed of {len(results)} total")
    print("=" * 120)
    print()


if __name__ == "__main__":
    main()
