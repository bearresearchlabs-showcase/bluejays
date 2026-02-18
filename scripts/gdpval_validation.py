#!/usr/bin/env python3
"""
GDPval-style incremental validation for databases.
Each DB = task with prompt + reference files + deliverable.
Runs 6 incremental steps, outputs JSON report per step.
"""

import json
import subprocess
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
    from db_logger import log, record_telemetry
except ImportError:
    def log(*a, **k): pass
    def record_telemetry(*a, **k): pass


def run_step(db_num: int, step: int, root: Path) -> Dict[str, Any]:
    """Run a single validation step. Returns {step, status, message, details}."""
    db_dir = root / f"db-{db_num}"
    result = {"step": step, "status": "PASS", "message": "", "details": {}}

    if step == 1:
        # Schema parse (syntax)
        schema = db_dir / "data" / "schema.sql"
        if not schema.exists():
            result["status"] = "FAIL"
            result["message"] = "No schema file found"
            return result
        # Basic SQL parse: check for CREATE TABLE
        content = schema.read_text(encoding="utf-8")
        if "CREATE TABLE" not in content.upper() and "CREATE TABLE" not in content:
            result["status"] = "FAIL"
            result["message"] = "Schema does not contain CREATE TABLE"
        result["details"]["schema_file"] = schema.name

    elif step == 2:
        # Queries extract (queries.json)
        qj = db_dir / "queries" / "queries.json"
        if not qj.exists():
            result["status"] = "FAIL"
            result["message"] = "queries.json missing"
            return result
        try:
            data = json.loads(qj.read_text(encoding="utf-8"))
            cnt = len(data.get("queries", []))
            result["details"]["query_count"] = cnt
            if cnt != 30:
                result["status"] = "FAIL"
                result["message"] = f"Expected 30 queries, found {cnt}"
        except (json.JSONDecodeError, OSError) as e:
            result["status"] = "FAIL"
            result["message"] = str(e)

    elif step == 3:
        # Query syntax (EXPLAIN) - requires comprehensive_validator
        scripts = db_dir / "scripts" / "comprehensive_validator.py"
        if not scripts.exists():
            result["status"] = "SKIP"
            result["message"] = "comprehensive_validator.py not found"
            return result
        proc = subprocess.run(
            [sys.executable, str(scripts)],
            cwd=str(db_dir),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            result["status"] = "FAIL"
            result["message"] = (proc.stderr or proc.stdout or "Unknown error")[:500]
        else:
            result["details"]["syntax_check"] = "passed"

    elif step == 4:
        # Query execution (fresh container) - required, fail if no DB
        result["status"] = "FAIL"
        result["message"] = "Execution test required (set PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE)"

    elif step == 5:
        # Deliverable completeness
        required = [
            ("schema", (db_dir / "data" / "schema.sql").exists()),
            ("queries.json", (db_dir / "queries" / "queries.json").exists()),
            ("queries.md", (db_dir / "queries" / "queries.md").exists()),
        ]
        missing = [n for n, ok in required if not ok]
        if missing:
            result["status"] = "FAIL"
            result["message"] = f"Missing: {', '.join(missing)}"
        result["details"]["checks"] = {n: ok for n, ok in required}

    elif step == 6:
        # Output/deliverable check
        client_db = root / "client" / "db" / f"db-{db_num}"
        if not client_db.exists():
            result["status"] = "SKIP"
            result["message"] = "client/db/db-N not synced"
            return result
        doc = client_db / "DOCUMENTATION"
        html = doc / f"db-{db_num}_documentation.html"
        jf = doc / f"db-{db_num}_deliverable.json"
        if not html.exists() or not jf.exists():
            result["status"] = "FAIL"
            result["message"] = "Documentation HTML or JSON missing"
        result["details"]["html"] = html.exists()
        result["details"]["json"] = jf.exists()

    return result


def run_gdpval_validation(root: Path, db_nums: List[int]) -> Dict[str, Any]:
    import time
    start = time.perf_counter()
    log("gdpval", "run", status="start", data={"db_nums": db_nums})
    report = {
        "validation_date": get_est_timestamp(),
        "databases": {},
        "summary": {"passed": 0, "failed": 0, "skipped": 0},
    }

    for db_num in db_nums:
        db_dir = root / f"db-{db_num}"
        if not db_dir.exists():
            continue
        steps = []
        for s in range(1, 7):
            steps.append(run_step(db_num, s, root))
        statuses = [st["status"] for st in steps]
        overall = "PASS" if all(s == "PASS" for s in statuses) else "FAIL" if any(s == "FAIL" for s in statuses) else "PARTIAL"
        report["databases"][f"db-{db_num}"] = {"steps": steps, "overall": overall}
        if overall == "PASS":
            report["summary"]["passed"] += 1
        elif overall == "FAIL":
            report["summary"]["failed"] += 1
        else:
            report["summary"]["skipped"] += 1

    duration_ms = (time.perf_counter() - start) * 1000
    record_telemetry("gdpval", "run", passed=report["summary"]["passed"], failed=report["summary"]["failed"], skipped=report["summary"]["skipped"])
    log("gdpval", "run", status="ok" if report["summary"]["failed"] == 0 else "fail", duration_ms=duration_ms, data=report["summary"])
    return report


def main() -> int:
    try:
        from db_args import parse_db_args
    except ImportError:
        def parse_db_args(a):
            if not a: return list(range(1, 17))
            if "-a" in a or "--all" in a: return list(range(1, 17))
            out = []
            for x in a:
                x = str(x).strip()
                if x.startswith("db-"): out.append(int(x.split("db-")[1]))
                elif x.isdigit(): out.append(int(x))
            if len(out) == 2 and out[0] < out[1]: out = list(range(out[0], out[1] + 1))
            return sorted(set(out)) if out else [1]
    db_nums = parse_db_args(sys.argv[1:])
    if not db_nums:
        db_nums = [1]

    report = run_gdpval_validation(root_dir, db_nums)
    print(json.dumps(report, indent=2))
    out = root_dir / "results" / "gdpval_validation_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved to: {out}")

    return 1 if report["summary"]["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
