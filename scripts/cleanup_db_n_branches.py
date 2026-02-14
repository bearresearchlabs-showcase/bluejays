#!/usr/bin/env python3
"""
Clean up each db-N per branch: checkout db-N, format, ACID/schema alignment, file audit.

Usage:
  python scripts/cleanup_db_n_branches.py [db-1] [db-5] | -a
  python scripts/cleanup_db_n_branches.py -a  # All db-1 through db-16

Per db-N:
  1. git checkout db-N
  2. format db-N
  3. compliance + integrity + bird-workbench (gates)
  4. Audit source/db-N: expected structure, flag extras/missing
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

# Prefer .venv for bird-workbench (tb3_workbench)
PYTHON = sys.executable
_venv_py = root_dir / ".venv" / "bin" / "python"
if _venv_py.exists():
    PYTHON = str(_venv_py)

# Expected structure for source/db-N (per database-creation-workflow)
EXPECTED_DIRS = {"app", "data", "deliverable", "docs", "metadata", "research", "results", "scripts"}
OPTIONAL_DIRS = {"validation", "queries"}  # queries may be in app/QUERIES
EXPECTED_FILES = {"README.md", "DELIVERABLE.md"}
OPTIONAL_FILES = {"deliverable.openapi.yaml"}

# Direct children of source/db-N that are stale (per .gitignore; canonical is app/)
FORBIDDEN_DIRS = {"DATABASE", "DOCUMENTATION", "LEGAL"}


def parse_db_args(args: list[str]) -> list[int]:
    """Parse db-1, 1, -a."""
    if not args or "-a" in args or "--all" in args:
        return list(range(1, 17))
    out = []
    for a in args:
        a = str(a).strip()
        if a.startswith("db-"):
            try:
                out.append(int(a.split("db-")[1]))
            except ValueError:
                continue
        elif a.isdigit():
            out.append(int(a))
    if len(out) == 2 and out[0] < out[1]:
        out = list(range(out[0], out[1] + 1))
    return sorted(set(out))


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run command, return (returncode, stdout, stderr)."""
    r = subprocess.run(
        cmd,
        cwd=str(cwd or root_dir),
        capture_output=True,
        text=True,
        timeout=300,
    )
    return r.returncode, r.stdout or "", r.stderr or ""


def audit_db_folder(db_num: int) -> dict[str, Any]:
    """Audit source/db-N for expected structure and flag issues."""
    db_dir = root_dir / "source" / f"db-{db_num}"
    issues: list[str] = []
    extras: list[str] = []
    missing: list[str] = []

    if not db_dir.exists():
        return {"Pass": 0, "error": "source/db-N does not exist", "issues": [f"Missing {db_dir}"]}

    # Check expected dirs
    for d in EXPECTED_DIRS:
        p = db_dir / d
        if not p.exists():
            missing.append(f"dir:{d}")
        elif not p.is_dir():
            issues.append(f"{d} exists but is not a directory")

    # Check expected files
    for f in EXPECTED_FILES:
        p = db_dir / f
        if not p.exists():
            missing.append(f"file:{f}")
        elif not p.is_file():
            issues.append(f"{f} exists but is not a file")

    # Check for forbidden/stale dirs (legacy; canonical is app/DATABASE, app/DOCUMENTATION)
    for name in db_dir.iterdir():
        if name.is_dir() and name.name in FORBIDDEN_DIRS:
            extras.append(f"stale/forbidden:{name.name}")

    # Check app/ has QUERIES or DATABASE
    app_dir = db_dir / "app"
    if app_dir.exists():
        if not (app_dir / "QUERIES").exists() and not (db_dir / "queries").exists():
            missing.append("queries (app/QUERIES or queries/)")
        if not (app_dir / "DATABASE").exists() and not (db_dir / "data").exists():
            missing.append("data (app/DATABASE or data/)")

    # Check data/schema.sql
    data_dir = db_dir / "data"
    app_db = app_dir / "DATABASE" if app_dir.exists() else None
    eff_data = app_db if (app_db and app_db.exists()) else data_dir
    if eff_data.exists():
        if not (eff_data / "schema.sql").exists():
            missing.append("data/schema.sql")

    # Schema alignment: source schema vs deliverable schema (dbN-xxx/data/schema.sql)
    schema_aligned = True
    eff_schema = (eff_data / "schema.sql") if eff_data and eff_data.exists() else None
    if eff_schema and eff_schema.exists():
        src_content = _normalize_sql(eff_schema.read_text(encoding="utf-8"))
        # Find web-deployable folder (dbN-xxx)
        prefix = f"db{db_num}-"
        for sub in (db_dir / "deliverable").iterdir() if (db_dir / "deliverable").exists() else []:
            if sub.is_dir() and sub.name.startswith(prefix):
                d_schema = sub / "data" / "schema.sql"
                if d_schema.exists():
                    del_content = _normalize_sql(d_schema.read_text(encoding="utf-8"))
                    if src_content != del_content:
                        schema_aligned = False
                        issues.append("schema_mismatch:deliverable schema differs from source")
                    break

    Pass = 1 if not (missing or issues or extras) and schema_aligned else 0
    return {
        "Pass": Pass,
        "missing": missing,
        "issues": issues,
        "extras": extras,
        "schema_aligned": schema_aligned,
        "path": str(db_dir),
    }


def _normalize_sql(s: str) -> str:
    """Normalize SQL for comparison (strip comments, collapse whitespace)."""
    lines = []
    for line in s.splitlines():
        # Strip trailing -- comments
        if "--" in line:
            line = line.split("--")[0]
        lines.append(line.strip())
    return " ".join(l for l in lines if l)


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--help" and a != "-h"]
    db_nums = parse_db_args(args)
    if not db_nums:
        print("Usage: python scripts/cleanup_db_n_branches.py [db-1] [db-5] | -a")
        return 1

    report: dict[str, Any] = {
        "databases": {},
        "summary": {"formatted": 0, "compliance_ok": 0, "integrity_ok": 0, "bird_ok": 0, "audit_ok": 0},
    }

    for db_num in db_nums:
        branch = f"db-{db_num}"
        print(f"\n{'='*70}")
        print(f"db-{db_num} (branch {branch})")
        print("=" * 70)

        # 1. Checkout
        ec, out, err = run_cmd(["git", "checkout", branch])
        if ec != 0:
            print(f"  ❌ git checkout {branch} failed: {err[:300]}")
            report["databases"][f"db-{db_num}"] = {"checkout": "FAIL", "error": err[:500]}
            continue
        print(f"  ✓ Checked out {branch}")

        # 2. Format
        fmt_ec, _, fmt_err = run_cmd([PYTHON, str(scripts_dir / "db_check.py"), "format", f"db-{db_num}"])
        if fmt_ec != 0:
            print(f"  ❌ format failed: {fmt_err[:300]}")
        else:
            print(f"  ✓ Format OK")
            report["summary"]["formatted"] += 1

        # 3. Compliance
        comp_ec, _, _ = run_cmd([PYTHON, str(scripts_dir / "db_check.py"), "compliance", f"db-{db_num}"])
        comp_ok = comp_ec == 0
        if comp_ok:
            report["summary"]["compliance_ok"] += 1
        print(f"  {'✓' if comp_ok else '❌'} Compliance")

        # 4. Integrity
        int_ec, _, _ = run_cmd([PYTHON, str(scripts_dir / "db_check.py"), "integrity", f"db-{db_num}"])
        int_ok = int_ec == 0
        if int_ok:
            report["summary"]["integrity_ok"] += 1
        print(f"  {'✓' if int_ok else '❌'} Integrity")

        # 5. Bird-workbench (gates only, no DB execution; uses .venv for tb3_workbench)
        bird_ec, _, _ = run_cmd(
            [PYTHON, str(scripts_dir / "db_check.py"), "bird-workbench", "--no-execute", str(db_num)]
        )
        bird_ok = bird_ec == 0
        if bird_ok:
            report["summary"]["bird_ok"] += 1
        print(f"  {'✓' if bird_ok else '❌'} BIRD workbench (gates)")

        # 6. File audit
        audit = audit_db_folder(db_num)
        audit_ok = audit.get("Pass", 0) == 1
        if audit_ok:
            report["summary"]["audit_ok"] += 1
        print(f"  {'✓' if audit_ok else '❌'} File audit")
        if not audit_ok:
            if audit.get("missing"):
                print(f"     Missing: {audit['missing']}")
            if audit.get("issues"):
                print(f"     Issues: {audit['issues']}")
            if audit.get("extras"):
                print(f"     Extras/stale: {audit['extras']}")

        report["databases"][f"db-{db_num}"] = {
            "checkout": "OK",
            "format": "OK" if fmt_ec == 0 else "FAIL",
            "compliance": "OK" if comp_ok else "FAIL",
            "integrity": "OK" if int_ok else "FAIL",
            "bird_workbench": "OK" if bird_ok else "FAIL",
            "audit": audit,
        }

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("=" * 70)
    n = len(db_nums)
    print(f"  Formatted:    {report['summary']['formatted']}/{n}")
    print(f"  Compliance:  {report['summary']['compliance_ok']}/{n}")
    print(f"  Integrity:   {report['summary']['integrity_ok']}/{n}")
    print(f"  BIRD gates:  {report['summary']['bird_ok']}/{n}")
    print(f"  File audit:  {report['summary']['audit_ok']}/{n}")

    out_file = root_dir / "results" / "cleanup_db_n_branches_report.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(report, indent=2))
    print(f"\nReport: {out_file}")

    failed = sum(1 for d, r in report["databases"].items() if r.get("audit", {}).get("Pass", 1) != 1)
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
