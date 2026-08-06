#!/usr/bin/env python3
"""
Comprehensive consistency check across the entire repository.

Checks for:
1. Directory structure consistency
2. File naming consistency
3. README files
4. Deliverable structure
5. Missing files
6. Duplicate files
"""

import re
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_database_structure(db_num, root_dir):
    """Check if database follows standard structure."""
    db_dir = root_dir / f"db-{db_num}"
    if not db_dir.exists():
        return {"exists": False}
    
    issues = []
    expected_dirs = ["queries", "data", "deliverable", "scripts"]
    
    for dir_name in expected_dirs:
        dir_path = db_dir / dir_name
        if not dir_path.exists():
            issues.append(f"Missing directory: {dir_name}/")
    
    # Check for required files
    required_files = {
        "queries/queries.md": "Query source file",
        "queries/queries.json": "Query metadata",
        "deliverable/db-{}.md": "Deliverable markdown",
        "deliverable/deliverable.openapi.yaml": "OpenAPI spec",
    }
    
    for file_pattern, description in required_files.items():
        file_path = db_dir / file_pattern.format(db_num)
        if not file_path.exists():
            issues.append(f"Missing file: {file_pattern.format(db_num)} ({description})")
    
    return {
        "exists": True,
        "issues": issues,
        "has_issues": len(issues) > 0
    }


def check_deliverable_structure(db_num, root_dir):
    """Check deliverable directory structure."""
    deliverable_dir = root_dir / f"db-{db_num}" / "deliverable"
    if not deliverable_dir.exists():
        return {"exists": False}
    
    issues = []
    
    # Check for web-deployable folder (ignore zip files)
    web_folders = [f for f in deliverable_dir.glob(f"db{db_num}-*") if f.is_dir() and not f.name.endswith('.zip')]
    if len(web_folders) == 0:
        issues.append("No web-deployable folder found")
    elif len(web_folders) > 1:
        issues.append(f"Multiple web-deployable folders: {[f.name for f in web_folders]}")
    else:
        web_folder = web_folders[0]
        required_web_files = [
            f"db-{db_num}_documentation.html",
            f"db-{db_num}_deliverable.json",
            f"db-{db_num}.md",
            "vercel.json",
            ".gitignore",
            "data/",
        ]
        
        for req_file in required_web_files:
            req_path = web_folder / req_file
            if not req_path.exists():
                issues.append(f"Missing in web folder: {req_file}")
    
    # Check for root-level files
    root_files = {
        f"db-{db_num}.md": "Deliverable markdown",
        "deliverable.openapi.yaml": "OpenAPI spec",
    }
    
    for file_name, description in root_files.items():
        file_path = deliverable_dir / file_name
        if not file_path.exists():
            issues.append(f"Missing root file: {file_name} ({description})")
    
    return {
        "exists": True,
        "issues": issues,
        "has_issues": len(issues) > 0
    }


def check_file_naming_consistency(root_dir):
    """Check for naming inconsistencies."""
    issues = []
    
    # Check for files with inconsistent naming
    for db_dir in root_dir.glob("db-*"):
        if not db_dir.is_dir():
            continue
        
        db_num_match = re.search(r'db-(\d+)', db_dir.name)
        if not db_num_match:
            continue
        
        db_num = int(db_num_match.group(1))
        
        # Check deliverable folder naming
        deliverable_dir = db_dir / "deliverable"
        if deliverable_dir.exists():
            web_folders = list(deliverable_dir.glob(f"db{db_num}-*"))
            for folder in web_folders:
                # Check if folder name matches expected pattern
                if not re.match(rf'db{db_num}-[a-z0-9-]+', folder.name):
                    issues.append(f"{db_dir.name}: Unexpected web folder name: {folder.name}")
    
    return issues


def check_duplicate_files(root_dir):
    """Check for duplicate files that should be consolidated."""
    duplicates = []
    
    # Check for duplicate db-{N}.md files
    db_md_files = defaultdict(list)
    for md_file in root_dir.rglob("db-*.md"):
        if "archive" in md_file.parts:
            continue
        db_num = extract_db_number(md_file)
        if db_num:
            db_md_files[db_num].append(md_file)
    
    for db_num, files in db_md_files.items():
        # Expected: deliverable/db-{N}.md, deliverable/db{N}-{name}/db-{N}.md, client/db/db-{N}/db{N}-{name}/db-{N}.md
        # More than 3 is unexpected
        if len(files) > 3:
            duplicates.append({
                "db_num": db_num,
                "files": [str(f.relative_to(root_dir)) for f in files],
                "count": len(files)
            })
    
    return duplicates


def extract_db_number(file_path):
    """Extract database number from file path."""
    match = re.search(r'db-(\d+)', str(file_path))
    if match:
        return int(match.group(1))
    return None


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Comprehensive consistency check across repository"
    )
    parser.add_argument(
        "--root",
        type=str,
        help="Root directory (default: parent of scripts directory)"
    )
    parser.add_argument(
        "--db-numbers",
        nargs="*",
        type=int,
        help="Specific database numbers to check (default: all db-6 through db-15)"
    )
    
    args = parser.parse_args()
    
    if args.root:
        root_dir = Path(args.root).resolve()
    else:
        root_dir = Path(__file__).parent.parent.resolve()
    
    logger.info(f"Comprehensive consistency check: {root_dir}\n")
    
    # Determine databases to check
    if args.db_numbers:
        db_numbers = args.db_numbers
    else:
        db_numbers = list(range(6, 16))
    
    all_issues = []
    
    # Check each database
    logger.info("=== Database Structure Check ===\n")
    for db_num in db_numbers:
        structure_result = check_database_structure(db_num, root_dir)
        deliverable_result = check_deliverable_structure(db_num, root_dir)
        
        if structure_result.get("has_issues") or deliverable_result.get("has_issues"):
            logger.warning(f"db-{db_num}: Issues found")
            if structure_result.get("issues"):
                for issue in structure_result["issues"]:
                    logger.warning(f"  - {issue}")
                    all_issues.append(f"db-{db_num}: {issue}")
            if deliverable_result.get("issues"):
                for issue in deliverable_result["issues"]:
                    logger.warning(f"  - {issue}")
                    all_issues.append(f"db-{db_num}: {issue}")
        else:
            logger.info(f"db-{db_num}: ✓ Structure OK")
    
    logger.info("\n=== File Naming Consistency Check ===\n")
    naming_issues = check_file_naming_consistency(root_dir)
    if naming_issues:
        for issue in naming_issues:
            logger.warning(f"  - {issue}")
            all_issues.append(issue)
    else:
        logger.info("✓ File naming consistent")
    
    logger.info("\n=== Duplicate Files Check ===\n")
    duplicates = check_duplicate_files(root_dir)
    if duplicates:
        for dup in duplicates:
            logger.warning(f"db-{dup['db_num']}: {dup['count']} db-*.md files found")
            for file_path in dup['files']:
                logger.warning(f"  - {file_path}")
            all_issues.append(f"db-{dup['db_num']}: Multiple db-*.md files")
    else:
        logger.info("✓ No unexpected duplicates")
    
    logger.info(f"\n=== Summary ===\n")
    logger.info(f"Total issues found: {len(all_issues)}")
    
    if all_issues:
        logger.info("\nIssues:")
        for issue in all_issues:
            logger.info(f"  - {issue}")
        return 1
    else:
        logger.info("✓ Repository is consistent!")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
