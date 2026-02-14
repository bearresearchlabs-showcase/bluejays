#!/usr/bin/env python3
"""
MVC Backend Test - Smoke test that all 16 DBs can be mounted and queried.
Treats the 16 DBs as the Model layer; verifies connection and basic read.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    from datetime import datetime
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

try:
    from db_logger import log, record_telemetry, init_session
except ImportError:
    def log(*a, **k): pass
    def record_telemetry(*a, **k): pass
    def init_session(*a, **k): return None

# Port mapping: db-N uses port 5435+N (from client/.env DB_PORTS_START=5436)
DEFAULT_PORTS = {n: 5435 + n for n in range(1, 17)}


def get_db_port(db_num: int) -> int:
    start = int(os.getenv("DB_PORTS_START", "5436"))
    return start + db_num - 1


def test_db_connection(db_num: int) -> Dict[str, Any]:
    """Test connection and run minimal smoke query for one DB."""
    host = os.getenv("PG_HOST", "localhost")
    port = get_db_port(db_num)
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "postgres")
    database = os.getenv("PG_DATABASE", f"db{db_num}")

    result = {
        "db": f"db-{db_num}",
        "host": host,
        "port": port,
        "database": database,
        "connected": False,
        "query_ok": False,
        "error": None,
    }

    try:
        import psycopg2
    except ImportError:
        result["error"] = "psycopg2 not installed"
        return result

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=database,
            connect_timeout=5,
        )
        result["connected"] = True

        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()

        # Try first query from queries.json if available
        qj = root_dir / f"db-{db_num}" / "queries" / "queries.json"
        if qj.exists():
            try:
                data = json.loads(qj.read_text(encoding="utf-8"))
                queries = data.get("queries", [])
                if queries and queries[0].get("sql"):
                    sql = queries[0]["sql"]
                    if "LIMIT" not in sql.upper():
                        sql = sql.rstrip(";") + " LIMIT 1"
                    cur = conn.cursor()
                    cur.execute(sql)
                    cur.fetchall()
                    cur.close()
                    result["query_ok"] = True
            except Exception as e:
                result["query_ok"] = False
        else:
            result["query_ok"] = True  # No queries to test

        conn.close()
    except Exception as e:
        result["error"] = str(e)[:200]

    return result


def main() -> int:
    import time
    start = time.perf_counter()
    # Gate on env validation (loads root .env and client/.env)
    from env_validator import ensure_env
    if not ensure_env("db"):
        return 1
    init_session(args=sys.argv[1:])
    # Load client/.env if present (ensure_env already does this; kept for explicit override)
    env_file = root_dir / "client" / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    db_nums = list(range(1, 17))
    if len(sys.argv) > 1 and sys.argv[1] not in ("-a", "--all"):
        try:
            db_nums = [int(sys.argv[1].replace("db-", ""))]
        except ValueError:
            pass

    results = []
    for n in db_nums:
        r = test_db_connection(n)
        results.append(r)
        status = "PASS" if r["connected"] and (r["query_ok"] or not r.get("error")) else "FAIL"
        print(f"  db-{n}: {status} (port {r['port']})" + (f" - {r['error']}" if r.get("error") else ""))

    summary = {
        "total": len(results),
        "connected": sum(1 for r in results if r["connected"]),
        "query_ok": sum(1 for r in results if r["query_ok"]),
        "failed": sum(1 for r in results if not r["connected"] or r.get("error")),
    }
    duration_ms = (time.perf_counter() - start) * 1000
    log("mvc_backend_test", "run", status="ok" if summary["failed"] == 0 else "fail", duration_ms=duration_ms, data=summary)
    record_telemetry("mvc_backend_test", "run", passed=summary["connected"], failed=summary["failed"], extra=summary)

    report = {
        "test_date": get_est_timestamp(),
        "results": results,
        "summary": summary,
    }

    out = root_dir / "mvc_backend_test_report.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved to: {out}")

    return 1 if report["summary"]["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
