#!/usr/bin/env python3
"""
Verify commit diff between base commit (38ce1cd) and HEAD for source/ and client/.
Produces comprehensive per-DB, per-section, per-key report.

Usage:
    python3 scripts/verify_commit_diff.py
    python3 scripts/verify_commit_diff.py --output results/commit_diff_38ce1cd_report.json
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE_COMMIT = "38ce1cd1aa03012979e6a85b5ca9299449f76ad6"
ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
QUERIES_JSON_KEYS = [
    "number", "title", "description", "use_case", "business_value",
    "purpose", "complexity", "expected_output", "sql", "line_number",
]
# Also compare keys that may exist in some DBs
EXTRA_KEYS = ["question", "evidence", "normal_query"]


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Run command, return (exit_code, stdout+stderr)."""
    r = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out


def _file_at_commit(rel_path: str, ref: str) -> bytes | None:
    """Get file content at ref (commit or 'HEAD'). Returns None if missing."""
    if ref == "HEAD":
        p = ROOT / rel_path
        if not p.exists() or not p.is_file():
            return None
        return p.read_bytes()
    path = f"{ref}:{rel_path}"
    r = subprocess.run(
        ["git", "show", path],
        cwd=ROOT,
        capture_output=True,
    )
    return r.stdout if r.returncode == 0 else None


def _hash_content(content: bytes | None) -> str:
    if content is None:
        return ""
    return hashlib.sha256(content).hexdigest()


def _list_files_at_commit(prefix: str, ref: str) -> list[str]:
    """List files under prefix at ref. prefix is e.g. 'source/db-1/app/DATABASE/'."""
    if ref == "HEAD":
        d = ROOT / prefix
        if not d.exists() or not d.is_dir():
            return []
        return [str(p.relative_to(ROOT)).replace("\\", "/") for p in d.rglob("*") if p.is_file()]
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "--", prefix],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return []
    out = (r.stdout or "").strip()
    return [line.strip() for line in out.splitlines() if line.strip()]


def _compare_section_files(prefix: str, db_num: int, section: str, is_source: bool) -> dict:
    """Compare files in a section between base and HEAD."""
    if is_source:
        base_prefix = f"source/db-{db_num}/app/{section}/"
        head_prefix = base_prefix
    else:
        base_prefix = f"client/db/db-{db_num}/{section}/"
        head_prefix = base_prefix

    base_files = set(_list_files_at_commit(base_prefix, BASE_COMMIT))
    head_files = set(_list_files_at_commit(head_prefix, "HEAD"))

    all_files = sorted(base_files | head_files)
    files_detail: dict = {}
    changed = 0
    base_prefix_path = Path(base_prefix)
    for f in all_files:
        base_content = _file_at_commit(f, BASE_COMMIT)
        head_content = _file_at_commit(f, "HEAD")
        at_base = "present" if base_content is not None else "absent"
        at_head = "present" if head_content is not None else "absent"
        hash_base = _hash_content(base_content) if base_content else ""
        hash_head = _hash_content(head_content) if head_content else ""
        if hash_base != hash_head:
            changed += 1
        try:
            fname = str(Path(f).relative_to(base_prefix_path))
        except ValueError:
            fname = Path(f).name
        files_detail[fname] = {
            "at_base": at_base,
            "at_head": at_head,
            "hash_base": hash_base[:16] if hash_base else "",
            "hash_head": hash_head[:16] if hash_head else "",
            "changed": hash_base != hash_head,
        }
    return {
        "files": files_detail,
        "summary": f"{changed} files changed of {len(all_files)} total",
    }


def _compare_queries_json(db_num: int, is_source: bool) -> dict | None:
    """Compare queries.json keys per query between base and HEAD."""
    if is_source:
        path = f"source/db-{db_num}/app/QUERIES/queries.json"
    else:
        path = f"client/db/db-{db_num}/QUERIES/queries.json"

    base_content = _file_at_commit(path, BASE_COMMIT)
    head_content = _file_at_commit(path, "HEAD")

    if base_content is None and head_content is None:
        return None

    def parse(b: bytes | None) -> dict | None:
        if b is None:
            return None
        try:
            return json.loads(b.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    base_json = parse(base_content)
    head_json = parse(head_content)

    keys_per_query = list(QUERIES_JSON_KEYS) + [k for k in EXTRA_KEYS if k not in QUERIES_JSON_KEYS]
    key_diff_summary: dict[str, int] = {}
    queries_changed: list[int] = []

    base_queries = (base_json or {}).get("queries", [])
    head_queries = (head_json or {}).get("queries", [])

    all_keys = set(keys_per_query)
    for q in base_queries + head_queries:
        all_keys.update(k for k in q if isinstance(q.get(k), (str, int, float, type(None))))

    for key in all_keys:
        key_diff_summary[key] = 0

    def query_by_num(queries: list, num: int) -> dict | None:
        for q in queries:
            if q.get("number") == num:
                return q
        return None

    seen_nums = set()
    for q in base_queries + head_queries:
        n = q.get("number")
        if n is None or n in seen_nums:
            continue
        seen_nums.add(n)
        base_q = query_by_num(base_queries, n)
        head_q = query_by_num(head_queries, n)
        q_changed = False
        for key in all_keys:
            v_base = (base_q or {}).get(key)
            v_head = (head_q or {}).get(key)
            if v_base != v_head:
                key_diff_summary[key] = key_diff_summary.get(key, 0) + 1
                q_changed = True
        if q_changed:
            queries_changed.append(n)

    return {
        "keys_per_query": list(all_keys),
        "queries_changed": sorted(queries_changed),
        "key_diff_summary": {k: v for k, v in key_diff_summary.items() if v > 0},
        "total_queries_base": len(base_queries),
        "total_queries_head": len(head_queries),
    }


def _compare_queries_md(db_num: int, is_source: bool) -> dict:
    """Compare queries.md line counts."""
    if is_source:
        path = f"source/db-{db_num}/app/QUERIES/queries.md"
    else:
        path = f"client/db/db-{db_num}/QUERIES/queries.md"

    base_content = _file_at_commit(path, BASE_COMMIT)
    head_content = _file_at_commit(path, "HEAD")

    def lines(b: bytes | None) -> int:
        if b is None:
            return 0
        return len(b.decode("utf-8", errors="replace").splitlines())

    return {
        "line_count_base": lines(base_content),
        "line_count_head": lines(head_content),
    }


def _source_vs_client_sync(db_num: int) -> dict:
    """Check if source/app and client/db are in sync for DATABASE and QUERIES."""
    result: dict = {}
    for section in ["DATABASE", "QUERIES"]:
        src_dir = ROOT / "source" / f"db-{db_num}" / "app" / section
        dst_dir = ROOT / "client" / "db" / f"db-{db_num}" / section
        mismatched = []
        if src_dir.exists() and dst_dir.exists():
            for f in src_dir.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(src_dir)
                    dst = dst_dir / rel
                    if dst.exists():
                        h1 = _hash_content(f.read_bytes())
                        h2 = _hash_content(dst.read_bytes())
                        if h1 != h2:
                            mismatched.append(str(rel))
                    else:
                        mismatched.append(str(rel))
        result[section] = {
            "in_sync": len(mismatched) == 0,
            "mismatched_files": mismatched,
        }
    return result


def _run_validate_qa(db_num: int) -> tuple[int, int]:
    """Run validate and QA, return (validation_pass, qa_pass) as 0 or 1."""
    val_pass, qa_pass = 0, 0
    # Validate
    code, _ = _run(["python3", "scripts/validate.py", "--no-overwrite", "--pass-fail-only", f"db-{db_num}"])
    val_pass = 1 if code == 0 else 0
    # QA suite --check-only (audit + compliance + integrity, no overwrites)
    code2, _ = _run(["python3", "scripts/db_check.py", "qa-suite", "--check-only", f"db-{db_num}"])
    qa_pass = 1 if code2 == 0 else 0
    return val_pass, qa_pass


def build_report(skip_validate_qa: bool = False) -> dict:
    """Build comprehensive report."""
    try:
        from timestamp_utils import get_est_timestamp
    except ImportError:
        def get_est_timestamp() -> str:
            from datetime import datetime
            return datetime.now().strftime("%Y%m%d-%H%M")

    report: dict = {
        "base_commit": BASE_COMMIT,
        "target": "HEAD",
        "generated_at": get_est_timestamp(),
        "databases": {},
        "summary": {
            "total_dbs": 16,
            "dbs_with_errors": [],
            "validation_pass": {},
            "qa_pass": {},
        },
    }

    # Save raw diff
    code, raw_diff = _run(["git", "diff", BASE_COMMIT, "HEAD", "--", "source/", "client/"])
    raw_path = RESULTS_DIR / "commit_diff_38ce1cd_raw.txt"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw_diff, encoding="utf-8")

    for db_num in range(1, 17):
        db_id = f"db-{db_num}"
        db_report: dict = {
            "source": {},
            "client": {},
            "source_vs_client_sync": {},
        }

        # Source sections
        for section in ["DATABASE", "DOCUMENTATION", "QUERIES"]:
            db_report["source"][f"app/{section}"] = _compare_section_files(
                f"source/db-{db_num}/app/", db_num, section, is_source=True
            )

        # Client sections
        for section in ["DATABASE", "DOCUMENTATION", "QUERIES"]:
            db_report["client"][section] = _compare_section_files(
                f"client/db/db-{db_num}/", db_num, section, is_source=False
            )

        # QUERIES queries.json detail
        for label, is_src in [("source", True), ("client", False)]:
            qj = _compare_queries_json(db_num, is_src)
            qm = _compare_queries_md(db_num, is_src)
            if qj is not None:
                if label == "source":
                    db_report["source"]["app/QUERIES"]["queries.json"] = qj
                else:
                    db_report["client"]["QUERIES"]["queries.json"] = qj
            if label == "source":
                db_report["source"]["app/QUERIES"]["queries.md"] = qm
            else:
                db_report["client"]["QUERIES"]["queries.md"] = qm

        # Source vs client sync
        db_report["source_vs_client_sync"] = _source_vs_client_sync(db_num)

        # Validate/QA
        if not skip_validate_qa:
            vp, qp = _run_validate_qa(db_num)
            report["summary"]["validation_pass"][db_id] = vp
            report["summary"]["qa_pass"][db_id] = qp
        else:
            report["summary"]["validation_pass"][db_id] = -1  # skipped
            report["summary"]["qa_pass"][db_id] = -1

        report["databases"][db_id] = db_report

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify commit diff 38ce1cd vs HEAD")
    parser.add_argument("--output", "-o", default=str(RESULTS_DIR / "commit_diff_38ce1cd_report.json"))
    parser.add_argument("--skip-validate-qa", action="store_true", help="Skip running validate and QA")
    parser.add_argument("--md", action="store_true", help="Also write human-readable .md report")
    parser.add_argument("--compile-mdx", action="store_true", help="Compile report JSON to MDX")
    args = parser.parse_args()

    report = build_report(skip_validate_qa=args.skip_validate_qa)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Report written to {out_path}")

    if args.md:
        md_path = out_path.with_suffix(".md")
        _write_md_report(report, md_path)
        print(f"Markdown report written to {md_path}")

    if args.compile_mdx:
        from compile_commit_diff_report import compile_to_mdx

        mdx_path = out_path.with_suffix(".mdx")
        raw_path = RESULTS_DIR / "commit_diff_38ce1cd_raw.txt"
        mdx_content = compile_to_mdx(report, raw_path if raw_path.exists() else None)
        mdx_path.write_text(mdx_content, encoding="utf-8")
        print(f"MDX report written to {mdx_path}")

    return 0


def _write_md_report(report: dict, path: Path) -> None:
    """Write human-readable markdown summary."""
    lines = [
        "# Commit Diff Verification Report",
        "",
        f"- **Base commit**: {report.get('base_commit', '')}",
        f"- **Target**: {report.get('target', '')}",
        f"- **Generated**: {report.get('generated_at', '')}",
        "",
        "## Summary",
        "",
    ]
    s = report.get("summary", {})
    lines.append(f"- Total DBs: {s.get('total_dbs', 0)}")
    lines.append(f"- Validation pass: {sum(1 for v in s.get('validation_pass', {}).values() if v == 1)}")
    lines.append(f"- QA pass: {sum(1 for v in s.get('qa_pass', {}).values() if v == 1)}")
    lines.append("")
    lines.append("## Per-DB Summary")
    lines.append("")
    for db_id, db_data in report.get("databases", {}).items():
        lines.append(f"### {db_id}")
        src = db_data.get("source", {})
        for sec, data in src.items():
            if isinstance(data, dict) and "summary" in data:
                lines.append(f"- **{sec}**: {data['summary']}")
        sync = db_data.get("source_vs_client_sync", {})
        for sec, sdata in sync.items():
            in_sync = sdata.get("in_sync", True)
            lines.append(f"- **Sync {sec}**: {'in sync' if in_sync else 'mismatched'}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
