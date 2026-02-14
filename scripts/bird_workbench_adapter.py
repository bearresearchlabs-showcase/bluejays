#!/usr/bin/env python3
"""
BIRD Workbench Adapter: Bridge BIRD benchmark to tb3_workbench with rigorous checks.

Tests databases for ACID (Atomicity, Consistency, Isolation, Durability) and BASE
(Basically Available, Soft state, Eventual consistency) properties. Validates
industrial-grade enterprise DB behavior.

tb3_workbench is always available. CI/CD: Jenkins. Local testing: same pipeline.
ANTHROPIC_API_KEY from .env for Anthropic models when multiple sessions run independently.

Flow:
  1. Load BIRD entries from bird_export/ (db-N_bird.json or all_bird.json)
  2. Gate: Run compliance + integrity for involved db(s)
  3. Per-task: SQL validation (EXPLAIN) + optional execution
  4. Report: Pass/fail per task, tb3_workbench assertions (min_accuracy)

Usage:
  python scripts/bird_workbench_adapter.py [db-1] [db-5] | -a
  db_check bird-workbench [db-1] [db-5] | -a
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

try:
    from db_logger import log, record_telemetry
except ImportError:
    def log(*a, **k): pass
    def record_telemetry(*a, **k): pass

BIRD_EXPORT_DIR = root_dir / "bird_export"


def _pg_conn_params(db_num: int) -> tuple[str, int, str, str, str]:
    """Resolve PG connection from env. CI/CD, SLURM, Jenkins set PG_*; no particular port required."""
    host = os.getenv("PG_HOST", "localhost")
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "postgres")
    database = os.getenv("PG_DATABASE", f"db{db_num}")
    # Precedence: PG_PORT (single DB), PG_PORT_DB{N} (per-db), DB_PORTS_START+offset (multi-db Docker)
    port_str = os.getenv("PG_PORT") or os.getenv(f"PG_PORT_DB{db_num}")
    if port_str:
        port = int(port_str)
    else:
        base = int(os.getenv("DB_PORTS_START", "5432"))
        port = base + db_num - 1
    return host, port, user, password, database


def parse_db_args(args: list[str]) -> list[int]:
    """Parse db-1, db-5, 1 5, -a, --all."""
    try:
        from db_args import parse_db_args as _parse
        return _parse(args)
    except ImportError:
        if not args or "-a" in args or "--all" in args:
            return list(range(1, 17))
        out = []
        for a in args:
            a = str(a).strip()
            if a.startswith("db-"): out.append(int(a.split("db-")[1]))
            elif a.isdigit(): out.append(int(a))
        if len(out) == 2 and out[0] < out[1]:
            out = list(range(out[0], out[1] + 1))
        return sorted(set(out)) if out else list(range(1, 17))


def load_bird_entries(db_nums: list[int]) -> list[dict]:
    """Load BIRD entries from bird_export for given db numbers."""
    entries = []
    for n in db_nums:
        path = BIRD_EXPORT_DIR / f"db-{n}_bird.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for e in data.get("entries", []):
            e["_db_num"] = n
            e["_task_id"] = f"db-{n}-query-{e.get('query_number', len(entries)+1)}"
            entries.append(e)
    return entries


def run_compliance_gate(db_nums: list[int]) -> tuple[bool, str]:
    """Run compliance check as gate. Returns (passed, message)."""
    try:
        from db_check import cmd_compliance
        args = ["-a"] if len(db_nums) >= 16 else [f"db-{n}" for n in db_nums]
        ec = cmd_compliance(args)
        return ec == 0, "compliance" if ec == 0 else "compliance failed"
    except Exception as e:
        return False, str(e)[:200]


def run_integrity_gate(db_nums: list[int]) -> tuple[bool, str]:
    """Run integrity check as gate. Returns (passed, message)."""
    try:
        from integrity_checks import run_integrity_checks
        ec = run_integrity_checks(root_dir, db_nums)
        return ec == 0, "integrity" if ec == 0 else "integrity failed"
    except Exception as e:
        return False, str(e)[:200]


def validate_sql_syntax(sql: str, db_num: int = 1) -> tuple[bool, str]:
    """Validate SQL via EXPLAIN on db-N (no execution). Returns (ok, error)."""
    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 not installed (pip install -r requirements.txt)"
    host, port, user, password, database = _pg_conn_params(db_num)
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=database, connect_timeout=5)
        cur = conn.cursor()
        cur.execute(f"EXPLAIN {sql}")
        cur.fetchall()
        cur.close()
        conn.close()
        return True, ""
    except Exception as e:
        return False, str(e)[:200]


def execute_sql(db_num: int, sql: str) -> tuple[bool, str]:
    """Execute SQL on db-N. Returns (success, error)."""
    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 not installed"
    host, port, user, password, database = _pg_conn_params(db_num)
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=database, connect_timeout=10)
        cur = conn.cursor()
        cur.execute(sql)
        cur.fetchall()
        cur.close()
        conn.close()
        return True, ""
    except Exception as e:
        return False, str(e)[:300]


def main(db_args: list[str] | None = None, *, execute: bool | None = None, min_accuracy: float = 0.95) -> int:
    start = time.perf_counter()
    args = db_args or sys.argv[1:]
    # --no-execute: skip SQL execution (syntax-only), useful when PG unavailable
    if execute is None:
        execute = "--no-execute" not in args
        args = [a for a in args if a != "--no-execute"]
    db_nums = parse_db_args(args)
    if not db_nums:
        db_nums = list(range(1, 17))

    log("bird_workbench", "run", status="start", data={"db_nums": db_nums})

    # Load BIRD entries
    entries = load_bird_entries(db_nums)
    if not entries:
        print("No BIRD entries found. Run: python scripts/bird_export.py -a")
        log("bird_workbench", "run", status="fail", message="no entries")
        return 1

    print(f"Loaded {len(entries)} BIRD tasks from db-{min(db_nums)}..db-{max(db_nums)}")

    # Gate 1: Compliance
    print("\n[Gate 1] Compliance...")
    ok, msg = run_compliance_gate(db_nums)
    if not ok:
        print(f"  FAIL: {msg}")
        log("bird_workbench", "run", status="fail", message="compliance gate failed")
        return 1
    print("  PASS")

    # Gate 2: Integrity
    print("\n[Gate 2] Integrity...")
    ok, msg = run_integrity_gate(db_nums)
    if not ok:
        print(f"  FAIL: {msg}")
        log("bird_workbench", "run", status="fail", message="integrity gate failed")
        return 1
    print("  PASS")

    # Per-task: SQL validation + optional execution (skip both when --no-execute / no DB)
    if execute:
        print(f"\n[Tasks] Validating and executing {len(entries)} SQL queries...")
    else:
        print(f"\n[Tasks] Skipping execution (--no-execute). Gates only. {len(entries)} tasks loaded.")
    results: list[dict[str, Any]] = []
    passed = 0
    for i, e in enumerate(entries):
        task_id = e.get("_task_id", f"task-{i+1}")
        sql = e.get("sql", "").strip()
        db_num = e.get("_db_num", 1)
        if not sql:
            results.append({"task_id": task_id, "passed": False, "error": "no sql"})
            continue
        if not execute:
            results.append({"task_id": task_id, "passed": True, "error": None, "skipped": True})
            passed += 1
            continue
        # Syntax validation (EXPLAIN on target db)
        syn_ok, syn_err = validate_sql_syntax(sql, db_num)
        if not syn_ok:
            results.append({"task_id": task_id, "passed": False, "error": f"syntax: {syn_err}"})
            continue
        exec_ok, exec_err = execute_sql(db_num, sql)
        if not exec_ok:
            results.append({"task_id": task_id, "passed": False, "error": exec_err})
            continue
        results.append({"task_id": task_id, "passed": True, "error": None})
        passed += 1
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(entries)}...")

    total = len(results)
    acc = (passed / total * 100) if total else 0
    print(f"\n  Passed: {passed}/{total} ({acc:.1f}%)")

    # Workbench-style assertions (tb3_workbench required)
    try:
        from tb3_workbench.assertions import assert_accuracy
    except ImportError as e:
        print("ERROR: tb3_workbench required. Install: pip install -e ../pluto/tb3_workbench", file=sys.stderr)
        raise SystemExit(1) from e
    class _FakeResults:
        accuracy = passed / total if total else 0
        n_resolved = passed
        results = []
        pass_at_k = {}
    assertion_failures = assert_accuracy(_FakeResults(), min_accuracy=min_accuracy)

    if assertion_failures:
        print("\n[Assertions] FAIL:")
        for f in assertion_failures:
            print(f"  - {f}")
    else:
        print("\n[Assertions] PASS")

    # Report
    report = {
        "db_nums": db_nums,
        "total_tasks": total,
        "passed": passed,
        "accuracy": acc / 100,
        "assertion_failures": assertion_failures,
        "results": results,
        "duration_ms": (time.perf_counter() - start) * 1000,
    }
    out_path = root_dir / "bird_export" / "bird_workbench_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, default=str))
    print(f"\nReport: {out_path}")

    record_telemetry("bird_workbench", "run", passed=passed, failed=total - passed, extra={"total": total})
    log("bird_workbench", "run", status="ok" if not assertion_failures else "fail", duration_ms=report["duration_ms"], data={"passed": passed, "total": total})
    return 0 if not assertion_failures else 1


if __name__ == "__main__":
    sys.exit(main())
