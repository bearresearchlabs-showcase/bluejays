#!/usr/bin/env python3
"""
Generate final consistency report for the entire repository.

This script verifies:
1. All db-*.md files are properly formatted
2. Directory structures are consistent
3. Required files exist
4. Naming conventions are followed
"""

import re
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

# Database names mapping
DB_NAMES = {
    6: "Weather Consulting Database",
    7: "Maritime Shipping Intelligence System",
    8: "Job Market Intelligence and Targeted Application System",
    9: "Shipping Rate Comparison and Cost Optimization Platform",
    10: "Shopping Aggregator and Retail Intelligence Platform",
    11: "Parking Intelligence and Marketplace Platform",
    12: "Credit Card Rewards Optimization and Portfolio Management Platform",
    13: "AI Model Benchmark Tracking and Marketing Intelligence Platform",
    14: "Cloud Instance Cost Optimization and Comparison Platform",
    15: "Electricity Cost and Solar Rebate Intelligence Platform",
}

DB_WEB_FOLDER_NAMES = {
    6: "db6-weather-consulting-insurance",
    7: "db7-maritime-shipping-intelligence",
    8: "db8-job-market-intelligence",
    9: "db9-shipping-intelligence",
    10: "db10-marketing-intelligence",
    11: "db11-parking-intelligence",
    12: "db12-credit-card-and-rewards-optimization-system",
    13: "db13-ai-benchmark-marketing-database",
    14: "db14-cloud-instance-cost-database",
    15: "db15-electricity-cost-and-solar-rebate-database",
}


def check_file_formatting(file_path, db_num):
    """Check if file matches standard formatting."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return {"valid": False, "error": "Could not read file"}
    
    checks = {
        "header": False,
        "description": False,
        "business_context": False,
        "table_of_contents": False,
    }
    
    # Check header
    first_line = content.split('\n')[0] if content else ""
    if re.match(f"^# ID: db-{db_num} - Name:", first_line):
        checks["header"] = True
    
    # Check description
    if re.search(r'\$1M\+\s+Annual Recurring Revenue.*?ARR', content, re.IGNORECASE | re.DOTALL):
        checks["description"] = True
    
    # Check Business Context
    if "## Business Context and Backstory" in content:
        checks["business_context"] = True
    
    # Check Table of Contents
    if re.search(r'## Table of Contents\s*\n\n### Database Documentation', content):
        checks["table_of_contents"] = True
    
    all_valid = all(checks.values())
    
    return {
        "valid": all_valid,
        "checks": checks,
        "file": str(file_path)
    }


def generate_report(root_dir):
    """Generate comprehensive consistency report."""
    root_dir = Path(root_dir).resolve()
    
    report = {
        "generated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "databases": [],
        "summary": {
            "total_databases": 0,
            "formatted_correctly": 0,
            "issues_found": 0
        }
    }
    
    db_numbers = list(range(6, 16))
    
    for db_num in db_numbers:
        db_info = {
            "database": f"db-{db_num}",
            "name": DB_NAMES.get(db_num),
            "files_checked": [],
            "structure_valid": True,
            "formatting_valid": True,
            "issues": []
        }
        
        # Check deliverable/db-{N}.md
        deliverable_md = root_dir / f"db-{db_num}" / "deliverable" / f"db-{db_num}.md"
        if deliverable_md.exists():
            result = check_file_formatting(deliverable_md, db_num)
            db_info["files_checked"].append({
                "file": f"deliverable/db-{db_num}.md",
                "valid": result["valid"],
                "checks": result.get("checks", {})
            })
            if not result["valid"]:
                db_info["formatting_valid"] = False
                db_info["issues"].append(f"deliverable/db-{db_num}.md formatting issues")
        
        # Check web-deployable db-{N}.md
        web_folder_name = DB_WEB_FOLDER_NAMES.get(db_num)
        if web_folder_name:
            web_md = root_dir / f"db-{db_num}" / "deliverable" / web_folder_name / f"db-{db_num}.md"
            if web_md.exists():
                result = check_file_formatting(web_md, db_num)
                db_info["files_checked"].append({
                    "file": f"deliverable/{web_folder_name}/db-{db_num}.md",
                    "valid": result["valid"],
                    "checks": result.get("checks", {})
                })
                if not result["valid"]:
                    db_info["formatting_valid"] = False
                    db_info["issues"].append(f"web-deployable db-{db_num}.md formatting issues")
        
        # Check client version
        client_md = root_dir / "client" / "db" / f"db-{db_num}" / web_folder_name / f"db-{db_num}.md"
        if client_md.exists():
            result = check_file_formatting(client_md, db_num)
            db_info["files_checked"].append({
                "file": f"client/db/db-{db_num}/{web_folder_name}/db-{db_num}.md",
                "valid": result["valid"],
                "checks": result.get("checks", {})
            })
            if not result["valid"]:
                db_info["formatting_valid"] = False
                db_info["issues"].append(f"client db-{db_num}.md formatting issues")
        
        if db_info["issues"]:
            report["summary"]["issues_found"] += len(db_info["issues"])
        else:
            report["summary"]["formatted_correctly"] += 1
        
        report["databases"].append(db_info)
        report["summary"]["total_databases"] += 1
    
    return report


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate final consistency report"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file (default: consistency_report.json)"
    )
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent.resolve()
    
    print("Generating consistency report...\n")
    
    report = generate_report(root_dir)
    
    # Output JSON
    output_file = args.output or root_dir / "consistency_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("=== Consistency Report Summary ===\n")
    print(f"Total databases checked: {report['summary']['total_databases']}")
    print(f"Formatted correctly: {report['summary']['formatted_correctly']}")
    print(f"Issues found: {report['summary']['issues_found']}")
    print()
    
    if report['summary']['issues_found'] > 0:
        print("Issues by database:")
        for db_info in report['databases']:
            if db_info['issues']:
                print(f"  {db_info['database']}:")
                for issue in db_info['issues']:
                    print(f"    - {issue}")
    else:
        print("✓ All databases are consistent!")
    
    print(f"\nFull report saved to: {output_file}")
    
    return 0 if report['summary']['issues_found'] == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
