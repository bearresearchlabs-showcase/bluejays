#!/usr/bin/env python3
"""
Unified DB Check - Consolidates validate, format, qa, integrity, and full checks.

Usage:
    python3 scripts/db_check.py validate db-1 db-5   # = /validate
    python3 scripts/db_check.py format db-1         # = /format
    python3 scripts/db_check.py qa                   # client/db audit
    python3 scripts/db_check.py integrity db-1       # CRC + hash
    python3 scripts/db_check.py compliance db-1      # strict compliance checklist
    python3 scripts/db_check.py full db-1            # all checks
    python3 scripts/db_check.py qa-suite [db-1] [-a] # QA suite (client audit + compliance + integrity)
    python3 scripts/db_check.py bird-workbench [db-1] [db-5] | -a  # BIRD benchmark + ACID/BASE + workbench assertions
    python3 scripts/db_check.py gdpval-langgraph [db-1] [db-5] | -a  # GDPval-style: prompt + reference(SQL) + deliverable(queries.md), .env harness, LangGraph
    python3 scripts/db_check.py rotate [--max-lines 10000] # Rotate/trim logs
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Optional

# Add scripts directory to path
scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

try:
    from db_logger import log, log_span, record_telemetry, get_log_path, init_session, get_session_id
except ImportError:
    def log(*a, **k): pass
    def record_telemetry(*a, **k): pass
    def get_log_path(): return Path("/dev/null")
    def init_session(*a, **k): return None
    def get_session_id(): return None
    class log_span:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass


def parse_db_args(args: List[str]) -> List[int]:
    """Parse database arguments (db-1, db-5, 1, 5, @db/db-1/, -a)."""
    db_nums = []
    if not args:
        return []

    if '-a' in args or '--all' in args:
        return list(range(1, 17))  # db-1 through db-16

    if '--help' in args or '-h' in args:
        return []

    for arg in args:
        arg = arg.strip()
        if '@db/db-' in arg or 'db/db-' in arg:
            part = arg.split('@db/db-')[-1].split('db/db-')[-1].split('/')[0]
            try:
                db_nums.append(int(part))
            except ValueError:
                continue
        elif arg.startswith('db-'):
            try:
                db_nums.append(int(arg.split('db-')[1]))
            except ValueError:
                continue
        elif arg.isdigit():
            db_nums.append(int(arg))

    if len(db_nums) == 2 and db_nums[0] < db_nums[1]:
        db_nums = list(range(db_nums[0], db_nums[1] + 1))

    return sorted(set(db_nums))


def cmd_validate(args: List[str]) -> int:
    """Run validation suite (Phase 0-5)."""
    start = time.perf_counter()
    log("db_check", "validate", status="start", data={"args": args})
    try:
        from validate import ValidationRunner
        runner = ValidationRunner(root_dir)
        result = runner.run(args)
        s = result.get("summary", {})
        status = "ok" if s.get("overall_status") == "PASS" else "fail"
        record_telemetry("db_check", "validate", passed=s.get("passed", 0), failed=s.get("failed", 0), skipped=s.get("skipped", 0), extra={"overall": s.get("overall_status")})
        log("db_check", "validate", status=status, duration_ms=(time.perf_counter() - start) * 1000, data=s)
        if s.get("overall_status") == "FAIL":
            return 1
        if s.get("overall_status") == "PARTIAL":
            return 2
        return 0
    except Exception as e:
        log("db_check", "validate", status="fail", message=str(e)[:200])
        raise


def cmd_format(args: List[str]) -> int:
    """Run format (package deliverables)."""
    start = time.perf_counter()
    log("db_check", "format", status="start", data={"args": args})
    try:
        from format import DeliverableFormatter
        formatter = DeliverableFormatter(root_dir)
        ec = formatter.run(args)
        status = "ok" if ec == 0 else "fail"
        log("db_check", "format", status=status, duration_ms=(time.perf_counter() - start) * 1000, data={"exit_code": ec})
        return ec
    except Exception as e:
        log("db_check", "format", status="fail", message=str(e)[:200])
        raise


def cmd_qa(args: List[str]) -> int:
    """Run QA audit on client/db."""
    start = time.perf_counter()
    log("db_check", "qa", status="start")
    try:
        from qa_client_db import get_client_dbs, audit_database, main as qa_main
        qa_main()
        dbs = get_client_dbs()
        if not dbs:
            log("db_check", "qa", status="ok", duration_ms=(time.perf_counter() - start) * 1000, data={"dbs": 0})
            return 0
        results = [audit_database(db) for db in dbs]
        passed = sum(1 for r in results if r.get("Pass", 1) == 1)
        failed = len(results) - passed
        record_telemetry("db_check", "qa", passed=passed, failed=failed)
        log("db_check", "qa", status="ok" if failed == 0 else "fail", duration_ms=(time.perf_counter() - start) * 1000, data={"passed": passed, "failed": failed, "total": len(results)})
        return 1 if failed > 0 else 0
    except Exception as e:
        log("db_check", "qa", status="fail", message=str(e)[:200])
        raise


def cmd_integrity(args: List[str]) -> int:
    """Run integrity checks (CRC, hash) on specified DBs."""
    start = time.perf_counter()
    db_nums = parse_db_args(args)
    if not db_nums:
        print("Usage: db_check.py integrity db-1 [db-5] | -a")
        return 1
    log("db_check", "integrity", status="start", data={"db_nums": db_nums})
    try:
        from integrity_checks import run_integrity_checks
        ec = run_integrity_checks(root_dir, db_nums)
        log("db_check", "integrity", status="ok" if ec == 0 else "fail", duration_ms=(time.perf_counter() - start) * 1000, data={"count": len(db_nums)})
        return ec
    except Exception as e:
        log("db_check", "integrity", status="fail", message=str(e)[:200])
        raise


def cmd_compliance(args: List[str]) -> int:
    """Run strict compliance checklist."""
    start = time.perf_counter()
    db_nums = parse_db_args(args)
    if not db_nums:
        print("Usage: db_check.py compliance db-1 [db-5] | -a")
        return 1
    log("db_check", "compliance", status="start", data={"db_nums": db_nums})

    from timestamp_utils import get_est_timestamp
    report = {"check_date": get_est_timestamp(), "databases": {}, "summary": {"passed": 0, "failed": 0}}

    from db_paths import get_queries_dir

    for db_num in db_nums:
        db_dir = root_dir / "source" / f"db-{db_num}"
        client_db_dir = root_dir / "client" / "db" / f"db-{db_num}"
        result = {"checks": [], "Pass": 1}

        # queries.json exists, 30 queries
        qj = get_queries_dir(db_dir) / "queries.json"
        if not qj.exists():
            result["checks"].append(("queries.json exists", False))
            result["Pass"] = 0
        else:
            try:
                data = json.loads(qj.read_text(encoding="utf-8"))
                cnt = len(data.get("queries", []))
                result["checks"].append(("queries.json 30 queries", cnt == 30))
                if cnt != 30:
                    result["Pass"] = 0
            except Exception:
                result["checks"].append(("queries.json valid", False))
                result["Pass"] = 0

        # queries.md exists
        qm = get_queries_dir(db_dir) / "queries.md"
        result["checks"].append(("queries.md exists", qm.exists()))
        if not qm.exists():
            result["Pass"] = 0

        # schema.sql or schema_postgresql.sql
        from db_paths import get_data_dir
        data_dir = get_data_dir(db_dir)
        schema = (data_dir / "schema.sql").exists() or (data_dir / "schema_postgresql.sql").exists()
        result["checks"].append(("schema exists", schema))
        if not schema:
            result["Pass"] = 0

        # data.sql (optional but document)
        data_sql = (data_dir / "data.sql").exists()
        result["checks"].append(("data.sql exists", data_sql))

        # client DOCUMENTATION/
        doc_ok = (client_db_dir / "DOCUMENTATION").exists()
        if doc_ok:
            db_str = str(db_num)
            doc_ok = (
                (client_db_dir / "DOCUMENTATION" / f"db-{db_str}_documentation.html").exists()
                and (client_db_dir / "DOCUMENTATION" / f"db-{db_str}_deliverable.json").exists()
            )
        result["checks"].append(("client DOCUMENTATION/", doc_ok))
        if not doc_ok and client_db_dir.exists():
            result["Pass"] = 0

        # metadata.json
        meta = (db_dir / "metadata" / "db_metadata.json").exists()
        result["checks"].append(("metadata/db_metadata.json", meta))
        # metadata is optional for now; don't fail

        report["databases"][f"db-{db_num}"] = result
        if result["Pass"] == 1:
            report["summary"]["passed"] += 1
        else:
            report["summary"]["failed"] += 1

    # Print report
    print("\n" + "=" * 70)
    print("COMPLIANCE CHECK")
    print("=" * 70)
    for db_name, res in report["databases"].items():
        status = "PASS" if res["Pass"] == 1 else "FAIL"
        print(f"\n{db_name}: {status}")
        for name, ok in res["checks"]:
            print(f"  {'✓' if ok else '✗'} {name}")
    print(f"\nSummary: {report['summary']['passed']} passed, {report['summary']['failed']} failed")
    print("=" * 70)

    out_file = root_dir / "results" / "compliance_report.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(report, indent=2))
    print(f"Report saved to: {out_file}")

    s = report["summary"]
    record_telemetry("db_check", "compliance", passed=s["passed"], failed=s["failed"])
    log("db_check", "compliance", status="ok" if s["failed"] == 0 else "fail", duration_ms=(time.perf_counter() - start) * 1000, data=s)
    return 1 if s["failed"] > 0 else 0


def cmd_qa_suite(args: List[str]) -> int:
    """Run QA suite: populate app (from @template), format, resync, audit, compliance, integrity."""
    db_args = args if args else ["-a"]
    print("\n" + "=" * 70)
    print("QA SUITE (populate app → format → resync → audit + compliance + integrity)")
    print("=" * 70)

    print("\n[0/6] Populate source/db-N/app/ (from data/, deliverable/, @template/)...")
    try:
        from populate_app_trifecta import main as populate_main
        import sys as _sys
        old = _sys.argv
        pop_nums = parse_db_args(db_args)
        _sys.argv = ["populate_app_trifecta.py"] + (["-a"] if len(pop_nums) >= 16 else [f"db-{n}" for n in pop_nums])
        try:
            ec_pop = populate_main()
        finally:
            _sys.argv = old
        if ec_pop != 0:
            print("  WARNING: populate_app had errors")
        else:
            print("  OK")
    except Exception as e:
        print(f"  WARNING: populate_app failed: {e}")

    print("\n[1/6] Format deliverables (queries, schema, docs)...")
    ec_format = cmd_format(db_args)
    if ec_format != 0:
        print("  WARNING: format had errors")

    print("\n[2/6] Resync source/ → client/db...")
    try:
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(scripts_dir / "resync_client_db.py")],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if proc.returncode != 0:
            print(f"  WARNING: resync failed: {proc.stderr[:500]}")
        else:
            print("  OK")
    except Exception as e:
        print(f"  WARNING: resync failed: {e}")

    print("\n[3/6] QA (client/db audit)...")
    ec1 = cmd_qa([])

    print("\n[4/6] Compliance...")
    ec2 = cmd_compliance(db_args)

    print("\n[5/6] Integrity...")
    ec3 = cmd_integrity(db_args)

    overall = 1 if any(c != 0 for c in [ec_format, ec1, ec2, ec3]) else 0
    print(f"\nQA Suite Overall: {'FAIL' if overall else 'PASS'}")
    return overall


def cmd_qa_claude(args: List[str]) -> int:
    """Run Claude QA (Sonnet quick / Opus research)."""
    try:
        from qa_claude import main as qa_main
        import sys as _sys
        old_argv = _sys.argv
        _sys.argv = ["qa_claude.py"] + args
        try:
            return qa_main()
        finally:
            _sys.argv = old_argv
    except Exception as e:
        log("db_check", "qa-claude", status="fail", message=str(e)[:200])
        raise


def cmd_bird_workbench(args: List[str]) -> int:
    """Run BIRD workbench adapter: ACID/BASE testing, compliance + integrity gates, BIRD task validation."""
    try:
        from bird_workbench_adapter import main as bird_wb_main
        return bird_wb_main(db_args=args if args else ["-a"])
    except Exception as e:
        log("db_check", "bird-workbench", status="fail", message=str(e)[:200])
        raise


def cmd_gdpval_langgraph(args: List[str]) -> int:
    """Run GDPval-style LangGraph harness: prompt + reference(SQL) + deliverable(queries.md), .env harness."""
    try:
        import sys as _sys
        from gdpval_langgraph_harness import main as gdpval_main
        old_argv = _sys.argv
        _sys.argv = ["gdpval_langgraph_harness.py"] + (args if args else ["-a"])
        try:
            return gdpval_main()
        finally:
            _sys.argv = old_argv
    except Exception as e:
        log("db_check", "gdpval-langgraph", status="fail", message=str(e)[:200])
        raise


def cmd_debug(args: List[str]) -> int:
    """Run debug mode: check-data, source, transform."""
    try:
        import sys
        from debug_mode import main as debug_main
        old_argv = sys.argv
        sys.argv = ["debug_mode.py"] + args
        try:
            return debug_main()
        finally:
            sys.argv = old_argv
    except Exception as e:
        log("db_check", "debug", status="fail", message=str(e)[:200])
        raise


def cmd_export(args: List[str]) -> int:
    """Export annotations to CSV (delegates to export_annotations.py)."""
    import argparse
    ap = argparse.ArgumentParser(prog="db_check export")
    ap.add_argument("source", help="template | db-N")
    ap.add_argument("-o", "--output", type=Path, help="Output CSV path")
    parsed, _ = ap.parse_known_args(args)
    out = parsed.output or (root_dir / f"submissions_{parsed.source.replace('-', '_')}.csv")
    try:
        from export_annotations import export_to_csv
        return export_to_csv(parsed.source, Path(out))
    except Exception as e:
        log("db_check", "export", status="fail", message=str(e)[:200])
        raise


def cmd_label_studio(args: List[str]) -> int:
    """Label Studio adapter: export, gates, multi-session.
    Usage: db_check label-studio [template|db-N] [--gates|--export|--multi-session]
    Default: gates (no Label Studio required).
    """
    import argparse
    ap = argparse.ArgumentParser(prog="db_check label-studio")
    ap.add_argument("source", nargs="?", default="template", help="template | db-N")
    ap.add_argument("--gates", action="store_true", help="Validate export format (default)")
    ap.add_argument("--export", action="store_true", help="Export to stdout")
    ap.add_argument("--multi-session", action="store_true", help="Multi-annotator simulation")
    parsed, rest = ap.parse_known_args(args)
    cmd = "gates"
    if parsed.export:
        cmd = "export"
    elif parsed.multi_session:
        cmd = "multi-session"
    try:
        from label_studio_adapter import main as ls_main
        import sys as _sys
        old_argv = _sys.argv
        _sys.argv = ["label_studio_adapter.py", cmd, parsed.source] + rest
        try:
            return ls_main()
        finally:
            _sys.argv = old_argv
    except Exception as e:
        log("db_check", "label-studio", status="fail", message=str(e)[:200])
        raise


def cmd_rotate(args: List[str]) -> int:
    """Rotate/trim logs to prevent unbounded growth."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-lines", type=int, default=10000)
    ap.add_argument("--max-telemetry", type=int, default=1000)
    parsed, _ = ap.parse_known_args(args)
    try:
        from rotate_logs import rotate_log, rotate_telemetry
        rotate_log(parsed.max_lines)
        rotate_telemetry(parsed.max_telemetry)
        log("db_check", "rotate", status="ok", data={"max_lines": parsed.max_lines, "max_telemetry": parsed.max_telemetry})
        return 0
    except Exception as e:
        log("db_check", "rotate", status="fail", message=str(e)[:200])
        raise


def cmd_full(args: List[str]) -> int:
    """Run all checks: validate, format, qa, integrity, compliance."""
    db_nums = parse_db_args(args)
    if not db_nums:
        print("Usage: db_check.py full db-1 [db-5] | -a")
        return 1

    exit_codes = []
    print("\n" + "=" * 70)
    print("FULL CHECK (validate + format + qa + integrity + compliance)")
    print("=" * 70)

    print("\n[1/5] Validate...")
    exit_codes.append(cmd_validate(args))

    print("\n[2/5] Format...")
    exit_codes.append(cmd_format(args))

    print("\n[3/5] QA (client/db)...")
    exit_codes.append(cmd_qa([]))

    print("\n[4/5] Integrity...")
    exit_codes.append(cmd_integrity(args))

    print("\n[5/5] Compliance...")
    exit_codes.append(cmd_compliance(args))

    overall = 1 if any(c != 0 for c in exit_codes) else 0
    print(f"\nOverall: {'FAIL' if overall else 'PASS'}")
    return overall


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nSubcommands: validate, format, qa, qa-suite, integrity, compliance, full, rotate, bird-workbench")
        return 1

    subcmd = sys.argv[1].lower()
    subargs = sys.argv[2:]
    sid = init_session(args=sys.argv[1:])
    log("db_check", "main", status="start", data={"subcmd": subcmd, "args": subargs, "session_id": sid})

    # Gate DB-dependent subcommands on env validation (qa-claude uses Claude, not DB)
    DB_SUBCMDS = {"validate", "format", "qa", "integrity", "compliance", "qa-suite", "full", "debug", "bird-workbench"}
    if subcmd in DB_SUBCMDS:
        from env_validator import ensure_env
        if not ensure_env("db"):
            return 1

    if subcmd == "validate":
        return cmd_validate(subargs)
    elif subcmd == "format":
        return cmd_format(subargs)
    elif subcmd == "qa":
        return cmd_qa(subargs)
    elif subcmd == "integrity":
        return cmd_integrity(subargs)
    elif subcmd == "compliance":
        return cmd_compliance(subargs)
    elif subcmd == "qa-suite":
        return cmd_qa_suite(subargs)
    elif subcmd == "bird-workbench":
        return cmd_bird_workbench(subargs)
    elif subcmd == "gdpval-langgraph":
        return cmd_gdpval_langgraph(subargs)
    elif subcmd == "full":
        return cmd_full(subargs)
    elif subcmd == "rotate":
        return cmd_rotate(subargs)
    elif subcmd == "debug":
        return cmd_debug(subargs)
    elif subcmd == "qa-claude":
        from env_validator import ensure_env
        if not ensure_env("claude"):
            return 1
        return cmd_qa_claude(subargs)
    elif subcmd == "export":
        return cmd_export(subargs)
    elif subcmd == "label-studio":
        return cmd_label_studio(subargs)
    else:
        log("db_check", "main", status="fail", message=f"Unknown subcommand: {subcmd}")
        print(f"Unknown subcommand: {subcmd}")
        print("Subcommands: validate, format, qa, qa-suite, integrity, compliance, full, rotate, debug, qa-claude, bird-workbench, gdpval-langgraph, export, label-studio")
        return 1


if __name__ == "__main__":
    try:
        ec = main()
        log("db_check", "main", status="ok" if ec == 0 else "fail", data={"exit_code": ec})
        sys.exit(ec)
    except Exception as e:
        log("db_check", "main", status="fail", message=str(e)[:200])
        raise
