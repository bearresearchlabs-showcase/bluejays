#!/usr/bin/env python3
"""
Clean up and reorganize top-level directory files.

This script:
1. Moves status/implementation markdown files to docs/archive/
2. Moves old query fixing scripts to scripts/archive/
3. Deletes duplicate files that are now in proper locations
4. Consolidates validation summary files
5. Checks and moves obsolete data directory
"""

import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def cleanup_root_directory(root_dir=None):
    """Clean up and reorganize root directory files."""
    if root_dir is None:
        root_dir = Path(__file__).parent.parent
    
    root_dir = Path(root_dir).resolve()
    
    logger.info(f"Cleaning up root directory: {root_dir}\n")
    
    changes_made = []
    
    # Create archive directories
    docs_archive = root_dir / "docs" / "archive"
    scripts_archive = root_dir / "scripts" / "archive"
    docs_archive.mkdir(parents=True, exist_ok=True)
    scripts_archive.mkdir(parents=True, exist_ok=True)
    
    # 1. Move status/implementation markdown files to docs/archive/
    status_files = [
        "BULK_DATA_EXTRACTION_SUMMARY.md",
        "DATA_EXTRACTION_READY.md",
        "DATA_GENERATION_PLAN.md",
        "EXTRACTION_CONFIGURED.md",
        "FINAL_STATUS.md",
        "FIXING_STATUS.md",
        "FORMAT_COMMAND_COMPLETE.md",
        "IMPLEMENTATION_COMPLETE.md",
        "QUICK_START_BULK_EXTRACTION.md",
        "ER_DIAGRAMS_GUIDE.md",
        "ER_DIAGRAMS_SUMMARY.md",
        "DELIVERABLE_PACKAGING.md",
        "DELIVERABLE_STRUCTURE.md",
        "FORMAT_COMMAND_USAGE.md",
    ]
    
    for filename in status_files:
        source = root_dir / filename
        if source.exists():
            dest = docs_archive / filename
            if dest.exists():
                # Add timestamp to avoid overwrite
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                dest = docs_archive / f"{source.stem}_{timestamp}{source.suffix}"
            shutil.move(str(source), str(dest))
            changes_made.append(f"Moved {filename} to docs/archive/")
            logger.info(f"  Moved: {filename} -> docs/archive/")
    
    # 2. Move old query fixing scripts to scripts/archive/
    old_scripts = [
        "aggressive_query_rewriter.py",
        "comprehensive_query_fixer.py",
        "comprehensive_query_rewriter.py",
        "debug_query_tests.py",
        "fix_all_queries.py",
        "fix_all_queries_systematically.py",
        "fix_remaining_queries.py",
        "iterative_fix_until_done.py",
        "iterative_query_fixer.py",
        "rewrite_queries_to_match_schema.py",
        "rewrite_template_queries.py",
        "test_queries_postgres.py",
        "run_comprehensive_tests.py",
        "generate_test_summary.py",
        "organize_archives.py",
        "standardize_deliverables.py",
        "cleanup_non_deliverables.py",
    ]
    
    for filename in old_scripts:
        source = root_dir / filename
        if source.exists():
            dest = scripts_archive / filename
            if dest.exists():
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                dest = scripts_archive / f"{source.stem}_{timestamp}{source.suffix}"
            shutil.move(str(source), str(dest))
            changes_made.append(f"Moved {filename} to scripts/archive/")
            logger.info(f"  Moved: {filename} -> scripts/archive/")
    
    # 3. Delete duplicate files that are now in proper locations
    duplicate_files = [
        "db-6.md",  # Should be in db-6/deliverable/db-6.md
        "db-6_deliverable.json",  # Should be in db-6/deliverable/db6-weather-consulting-insurance/
    ]
    
    for filename in duplicate_files:
        source = root_dir / filename
        if source.exists():
            # Check if file exists in proper location
            if filename == "db-6.md":
                proper_location = root_dir / "db-6" / "deliverable" / "db-6.md"
            elif filename == "db-6_deliverable.json":
                proper_location = root_dir / "db-6" / "deliverable" / "db6-weather-consulting-insurance" / "db-6_deliverable.json"
            else:
                proper_location = None
            
            if proper_location and proper_location.exists():
                source.unlink()
                changes_made.append(f"Deleted duplicate {filename} (exists in proper location)")
                logger.info(f"  Deleted: {filename} (duplicate)")
            else:
                logger.warning(f"  Skipped {filename} (proper location not found)")
    
    # 4. Consolidate validation summary files
    validation_files = [
        "validation_report_db1_to_db5.json",
        "validation_summary_db1_to_db5.json",
        "validation_summary_all_databases.json",
    ]
    
    results_dir = root_dir / "results"
    results_dir.mkdir(exist_ok=True)
    
    for filename in validation_files:
        source = root_dir / filename
        if source.exists():
            dest = results_dir / filename
            if dest.exists():
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                dest = results_dir / f"{source.stem}_{timestamp}{source.suffix}"
            shutil.move(str(source), str(dest))
            changes_made.append(f"Moved {filename} to results/")
            logger.info(f"  Moved: {filename} -> results/")
    
    # 5. Check top-level data/ directory
    root_data_dir = root_dir / "data"
    if root_data_dir.exists():
        # Check if it contains db-6 specific files
        data_files = list(root_data_dir.glob("*.sql"))
        if data_files:
            # Check if these files are duplicates of db-6/data/
            db6_data_dir = root_dir / "db-6" / "data"
            if db6_data_dir.exists():
                db6_files = {f.name for f in db6_data_dir.glob("*.sql")}
                root_files = {f.name for f in data_files}
                
                if root_files.issubset(db6_files):
                    # Move to archive
                    archive_data = docs_archive / "old_data_directory"
                    archive_data.mkdir(exist_ok=True)
                    for file in data_files:
                        shutil.move(str(file), str(archive_data / file.name))
                    changes_made.append(f"Moved {len(data_files)} files from root data/ to archive")
                    logger.info(f"  Archived {len(data_files)} files from root data/ directory")
                else:
                    logger.info(f"  Kept: root data/ directory (contains unique files)")
            else:
                logger.info(f"  Kept: root data/ directory (db-6/data/ not found)")
    
    # 6. Move queries templates to template/ (single source of truth)
    template_dir = root_dir / "template"
    for src_name, dest_name in [
        ("queries_template.json", "queries.json"),
        ("queries_template.md", "queries.md"),
    ]:
        src = root_dir / src_name
        if src.exists():
            template_dir.mkdir(parents=True, exist_ok=True)
            dest = template_dir / dest_name
            if not dest.exists() or src.stat().st_mtime > dest.stat().st_mtime:
                shutil.copy2(str(src), str(dest))
            src.unlink()
            changes_made.append(f"Moved {src_name} to template/{dest_name}")
            logger.info(f"  Moved: {src_name} -> template/{dest_name}")

    # 7. Move program_economics.py to scripts/ (if not already there)
    prog_econ = root_dir / "program_economics.py"
    dest_prog = root_dir / "scripts" / "program_economics.py"
    if prog_econ.exists() and not dest_prog.exists():
        shutil.move(str(prog_econ), str(dest_prog))
        changes_made.append("Moved program_economics.py to scripts/")
        logger.info("  Moved: program_economics.py -> scripts/")

    # 8. Move stray reports: AUDIT_* to archive/reports/; compliance, gdpval, validation_summary to results/
    reports_archive = root_dir / "archive" / "reports"
    for name in ("AUDIT_INDEX.txt", "AUDIT_REPORT_2026-02-14.json"):
        src = root_dir / name
        if src.exists():
            reports_archive.mkdir(parents=True, exist_ok=True)
            dest = reports_archive / name
            if dest.exists():
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                dest = reports_archive / f"{src.stem}_{timestamp}{src.suffix}"
            shutil.move(str(src), str(dest))
            changes_made.append(f"Moved {name} to archive/reports/")
            logger.info(f"  Moved: {name} -> archive/reports/")
    for name in ("compliance_report.json", "gdpval_validation_report.json", "gdpval_langgraph_report.json", "validation_summary.json"):
        src = root_dir / name
        if src.exists():
            dest = results_dir / name
            if dest.exists():
                reports_archive.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                shutil.copy2(str(src), str(reports_archive / f"{src.stem}_{timestamp}{src.suffix}"))
            shutil.move(str(src), str(dest))
            changes_made.append(f"Moved {name} to results/")
            logger.info(f"  Moved: {name} -> results/")

    # 9. Keep deliverable_structure_manifest.json at root (it's actively used)
    manifest = root_dir / "deliverable_structure_manifest.json"
    if manifest.exists():
        logger.info(f"  Kept: deliverable_structure_manifest.json (active manifest)")
    
    logger.info(f"\n✓ Cleanup complete: {len(changes_made)} changes made")
    
    return changes_made


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up and reorganize root directory files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually moving/deleting files"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be moved or deleted\n")
        # TODO: Implement dry-run logic
        return 0
    
    changes = cleanup_root_directory()
    
    if changes:
        logger.info(f"\nSummary of changes:")
        for change in changes:
            logger.info(f"  - {change}")
    else:
        logger.info("\nNo changes needed")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
