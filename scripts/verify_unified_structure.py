#!/usr/bin/env python3
"""
Rigorous verification of client/db structure:
- DATABASE/: PostgreSQL-only SQL (schema.sql, data.sql, data_large.sql >= 1GB)
- DOCUMENTATION/: html, json, md
- QUERIES/: queries.md, queries.json (PostgreSQL-only queries)
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
CLIENT = BASE / "client" / "db"
GB = 1024**3


def verify_db(n: int) -> dict:
    r = {"db": f"db-{n}", "errors": [], "warnings": []}
    d = CLIENT / f"db-{n}"
    if not d.exists():
        r["errors"].append("Missing db dir")
        return r

    # 1. DATABASE/
    db_dir = d / "DATABASE"
    if not db_dir.exists():
        r["errors"].append("Missing DATABASE/")
    else:
        sql_files = list(db_dir.glob("*.sql"))
        if not sql_files:
            r["errors"].append("DATABASE/ has no .sql files")
        schema = any(f.name.startswith("schema") for f in sql_files)
        if not schema:
            r["errors"].append("DATABASE/ missing schema*.sql")
        # Primary data file: data_large.sql (>= 1GB) or data.sql
        data_sql = db_dir / "data.sql"
        data_large = db_dir / "data_large.sql"
        has_data = data_sql.exists() or data_large.exists()
        if not has_data:
            r["errors"].append("DATABASE/ missing data.sql or data_large.sql")
        elif data_large.exists() and data_large.stat().st_size < GB:
            r["errors"].append(f"DATABASE/data_large.sql < 1GB ({data_large.stat().st_size / GB:.2f}GB)")
        for f in sql_files:
            if "snowflake" in f.name.lower() or "bigquery" in f.name.lower():
                r["errors"].append(f"DATABASE/ has non-PostgreSQL file: {f.name}")

    # 2. DOCUMENTATION/
    doc_dir = d / "DOCUMENTATION"
    if not doc_dir.exists():
        r["errors"].append("Missing DOCUMENTATION/")
    else:
        md = doc_dir / f"db-{n}.md"
        html = doc_dir / f"db-{n}_documentation.html"
        if not md.exists() and not html.exists():
            r["warnings"].append("DOCUMENTATION/ missing .md or .html")

    # 3. QUERIES/
    q_dir = d / "QUERIES"
    if not q_dir.exists():
        r["errors"].append("Missing QUERIES/")
    else:
        qj = q_dir / "queries.json"
        qm = q_dir / "queries.md"
        if not qj.exists():
            r["errors"].append("QUERIES/ missing queries.json")
        else:
            try:
                j = json.load(open(qj))
                cnt = len(j.get("queries", []))
                if cnt != 30:
                    r["warnings"].append(f"queries.json has {cnt} queries (expected 30)")
            except Exception as e:
                r["errors"].append(f"queries.json invalid: {e}")
        if not qm.exists():
            r["errors"].append("QUERIES/ missing queries.md")

    r["ok"] = len(r["errors"]) == 0
    return r


def main():
    print("=" * 70)
    print("RIGOROUS VERIFICATION: DATABASE | DOCUMENTATION | QUERIES (PostgreSQL only)")
    print("=" * 70)

    results = []
    for n in range(1, 17):
        r = verify_db(n)
        results.append(r)
        status = "OK" if r["ok"] else "FAIL"
        errs = "; ".join(r["errors"][:2]) if r["errors"] else ""
        print(f"  db-{n:2}: {status}  {errs}")

    print()
    failed = [r["db"] for r in results if not r["ok"]]
    if failed:
        print("FAILED:", ", ".join(failed))
        for r in results:
            if r["errors"]:
                print(f"  {r['db']}: {r['errors']}")
        sys.exit(1)
    print("All 16 databases pass rigorous verification.")


if __name__ == "__main__":
    main()
