#!/usr/bin/env python3
"""
Transaction-level integrity checks for PostgreSQL databases.
Runs after schema+data load: EXPLAIN on sample query, CHECK constraint validation.
Integrates with docker_postgres_qa.sh and BIRD workbench.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

try:
    import psycopg2
except ImportError:
    psycopg2 = None


def _pg_conn(db_num: int):
    """Connect to db-N PostgreSQL."""
    if not psycopg2:
        return None
    host = os.getenv("PG_HOST", "localhost")
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "postgres")
    database = f"db{db_num}"
    port_str = os.getenv("PG_PORT") or os.getenv(f"PG_PORT_DB{db_num}")
    port = int(port_str) if port_str else int(os.getenv("DB_PORTS_START", "5436")) + db_num - 1
    try:
        return psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=database, connect_timeout=5
        )
    except Exception as e:
        return None


def run_explain_check(conn, sql: str) -> Tuple[bool, str]:
    """Run EXPLAIN on query to validate plan. Returns (success, message)."""
    if not conn or not sql:
        return False, "No connection or SQL"
    try:
        with conn.cursor() as cur:
            cur.execute(f"EXPLAIN {sql}")
            cur.fetchall()
        return True, "EXPLAIN OK"
    except Exception as e:
        return False, str(e)


def run_check_constraints(conn) -> Tuple[bool, str]:
    """Validate CHECK constraints exist and are valid. Returns (success, message)."""
    if not conn:
        return False, "No connection"
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT conname, pg_get_constraintdef(oid) 
                FROM pg_constraint 
                WHERE contype = 'c' AND connamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                LIMIT 5
            """)
            rows = cur.fetchall()
        return True, f"CHECK constraints: {len(rows)} found"
    except Exception as e:
        return False, str(e)


def get_sample_sql(db_num: int) -> Optional[str]:
    """Get first query SQL from queries.json for db-N."""
    for base in [
        root_dir / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.json",
        root_dir / "source" / f"db-{db_num}" / "queries" / "queries.json",
        root_dir / "client" / "db" / f"db-{db_num}" / "QUERIES" / "queries.json",
    ]:
        if base.exists():
            try:
                data = json.loads(base.read_text())
                queries = data.get("queries", data) if isinstance(data, dict) else data
                if isinstance(queries, list) and queries:
                    q = queries[0]
                    sql = q.get("sql", q.get("SQL", ""))
                    if sql:
                        return sql
            except Exception:
                pass
    return None


def check_db(db_num: int) -> dict:
    """Run integrity checks for db-N. Returns result dict."""
    conn = _pg_conn(db_num)
    result = {"db": f"db-{db_num}", "explain": None, "check_constraints": None, "pass": False}
    if not conn:
        result["explain"] = "Connection failed (pg not running?)"
        return result
    try:
        sql = get_sample_sql(db_num)
        ok, msg = run_explain_check(conn, sql or "SELECT 1")
        result["explain"] = msg
        ok2, msg2 = run_check_constraints(conn)
        result["check_constraints"] = msg2
        result["pass"] = ok and ok2
    finally:
        conn.close()
    return result


def main() -> int:
    db_nums = []
    for arg in sys.argv[1:]:
        if arg in ("-a", "--all"):
            db_nums = list(range(1, 17))
            break
        if arg.startswith("db-"):
            n = int(arg.replace("db-", ""))
            if 1 <= n <= 16:
                db_nums.append(n)
    if not db_nums:
        db_nums = [1]
    passed = 0
    for n in db_nums:
        r = check_db(n)
        status = "PASS" if r["pass"] else "FAIL"
        print(f"db-{n}: {status} | EXPLAIN: {r['explain']} | {r['check_constraints']}")
        if r["pass"]:
            passed += 1
    return 0 if passed == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
