#!/usr/bin/env python3
"""
Shared final report generator (Phase 5).
Uses source/db-N/results/. Reads fix_verification, comprehensive_validation, execution.
Usage: python3 generate_final_report.py <db_num>
"""

import json
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from timestamp_utils import get_est_timestamp


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main():
    root = scripts_dir.parent
    if len(sys.argv) < 2:
        print("Usage: generate_final_report.py <db_num>")
        sys.exit(1)
    try:
        db_num = int(sys.argv[1].replace("db-", ""))
    except ValueError:
        print("Invalid db number")
        sys.exit(1)

    results_dir = root / "source" / f"db-{db_num}" / "results"
    fix_verification = load_json(results_dir / "fix_verification.json")
    comprehensive = load_json(results_dir / "comprehensive_validation_report.json")
    execution = load_json(results_dir / "query_test_results_postgres.json") or load_json(
        results_dir / "execution_test_results.json"
    )

    recursive_eval = comprehensive.get("evaluation", {}).get("recursive_cte_usage", {})
    cte_eval = comprehensive.get("evaluation", {}).get("cte_usage", {})

    report = {
        "report_date": get_est_timestamp(),
        "database": f"db-{db_num}",
        "Pass": 1,
        "summary": {
            "total_queries": comprehensive.get("total_queries", 30),
            "fix_verification_status": fix_verification.get("overall_status", "UNKNOWN"),
            "evaluation_status": comprehensive.get("evaluation", {}).get("query_count", {}).get("status", "UNKNOWN"),
            "execution_testing_status": "PASS" if execution.get("postgresql", {}).get("available") else "PARTIAL",
        },
        "phase_1_fix_verification": fix_verification,
        "phase_2_syntax_validation": comprehensive.get("syntax_validation", {}),
        "phase_3_execution_testing": execution,
        "phase_4_comprehensive_evaluation": comprehensive.get("evaluation", {}),
        "findings": {"critical_issues": [], "warnings": [], "recommendations": []},
        "notes": [],
    }

    if fix_verification.get("overall_status") == "FAIL":
        report["findings"]["critical_issues"].append({"phase": "Fix Verification", "issue": "Fixes not applied correctly"})
    if recursive_eval.get("mismatched", 0) > 0:
        report["findings"]["warnings"].append(
            {"issue": "Recursive CTE mismatch", "count": recursive_eval.get("mismatched", 0)}
        )
    if cte_eval.get("queries_without_cte", 0) > 0:
        report["findings"]["critical_issues"].append(
            {"issue": "Queries without CTEs", "count": cte_eval.get("queries_without_cte", 0)}
        )

    if report["findings"]["critical_issues"]:
        report["Pass"] = 0

    output_file = results_dir / "final_comprehensive_validation_report.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(report, indent=2, default=str))
    print(f"Report saved to {output_file}")


if __name__ == "__main__":
    main()
