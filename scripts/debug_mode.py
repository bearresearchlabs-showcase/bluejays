#!/usr/bin/env python3
"""
Debug mode: check data sufficiency, source, and transform.
When data is insufficient, source and transform to meet business needs.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

from env_validator import load_env, ensure_env
load_env()
if not ensure_env("db"):
    sys.exit(1)

# Default row count threshold
DEFAULT_ROW_THRESHOLD = 1


def get_db_port(db_num: int) -> int:
    start = int(os.getenv("DB_PORTS_START", "5436"))
    return start + db_num - 1


def get_table_names_from_schema(db_dir: Path) -> list[str]:
    """Extract table names from schema.sql."""
    tables = []
    for name in ("schema.sql",):
        p = db_dir / "data" / name
        if p.exists():
            text = p.read_text(encoding="utf-8")
            import re
            for m in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)", text, re.I):
                tables.append(m.group(1))
            break
    return tables


def check_data(db_num: int, threshold: int) -> dict:
    """Check row counts in key tables for db-N. Return status dict."""
    host = os.getenv("PG_HOST", "localhost")
    port = get_db_port(db_num)
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "postgres")
    database = os.getenv("PG_DATABASE", f"db{db_num}")
    db_dir = root_dir / "source" / f"db-{db_num}"
    tables = get_table_names_from_schema(db_dir)
    result = {"db_id": f"db-{db_num}", "tables": {}, "below_threshold": [], "error": None}
    if not tables:
        result["error"] = "no schema or no tables found"
        return result
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=database, connect_timeout=5
        )
        cur = conn.cursor()
        for t in tables:
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{t}"')
                cnt = cur.fetchone()[0]
                result["tables"][t] = cnt
                if cnt < threshold:
                    result["below_threshold"].append((t, cnt))
            except Exception as e:
                result["tables"][t] = f"error: {str(e)[:80]}"
        cur.close()
        conn.close()
    except Exception as e:
        result["error"] = str(e)[:200]
    return result


def run_source(db_nums: list[int]) -> bool:
    """Trigger ETL from research notebooks or extract scripts."""
    # Check for research/etl_elt_pipeline.ipynb in first db
    for n in db_nums:
        db_dir = root_dir / "source" / f"db-{n}"
        nb = db_dir / "research" / "etl_elt_pipeline.ipynb"
        if nb.exists():
            print(f"  Found {nb.relative_to(root_dir)} - run manually: jupyter nbconvert --execute ...")
            return True
    # Fallback: suggest scripts
    extract_scripts = list((root_dir / "scripts").glob("extract_*.py"))
    if extract_scripts:
        print(f"  Run: python3 scripts/{extract_scripts[0].name}")
        return True
    print("  No ETL pipeline or extract scripts found. Add research/etl_elt_pipeline.ipynb per db.")
    return False


def run_transform(db_nums: list[int]) -> bool:
    """Run transformation scripts to populate data.sql or schema."""
    for n in db_nums:
        db_dir = root_dir / "source" / f"db-{n}"
        data_sql = db_dir / "data" / "data.sql"
        if data_sql.exists():
            print(f"  db-{n}: data.sql exists. Apply with: psql -f data/data.sql")
            continue
        transform_scripts = list((db_dir / "scripts").glob("*transform*.py")) or list((db_dir / "research").glob("*transform*.py"))
        if transform_scripts:
            print(f"  db-{n}: Run {transform_scripts[0].name}")
        else:
            print(f"  db-{n}: No transform script. Create data.sql manually.")
    return True


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-data", action="store_true", help="Check row counts; flag if below threshold")
    ap.add_argument("--source", action="store_true", help="Trigger ETL from research/ or extract scripts")
    ap.add_argument("--transform", action="store_true", help="Run transformation to populate data.sql")
    ap.add_argument("--session-id", type=str, default=None)
    ap.add_argument("--threshold", type=int, default=DEFAULT_ROW_THRESHOLD)
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or -a for all")
    ap.add_argument("-a", "--all", action="store_true")
    args = ap.parse_args()

    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = []
        for a in args.dbs:
            try:
                db_nums.append(int(str(a).replace("db-", "")))
            except ValueError:
                pass
        db_nums = sorted(set(db_nums))

    if args.session_id:
        try:
            from db_logger import init_session
            init_session(session_id=args.session_id, args=sys.argv[1:])
        except ImportError:
            pass

    if args.check_data:
        print("Checking row counts...")
        for n in db_nums:
            r = check_data(n, args.threshold)
            print(f"  {r['db_id']}: {r}")
            if r.get("below_threshold"):
                print(f"    -> Below threshold: {r['below_threshold']}")

    if args.source:
        print("Sourcing data...")
        run_source(db_nums)

    if args.transform:
        print("Transforming...")
        run_transform(db_nums)

    if not (args.check_data or args.source or args.transform):
        ap.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
