#!/bin/bash
#
# Run complete validation suite for db-{N}/queries/queries.md
# Usage: ./run_full_validation.sh [db-number]
#

set -e

DB_NUM=${1:-1}
DB_DIR="db-${DB_NUM}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DB_PATH="${ROOT_DIR}/${DB_DIR}"

if [ ! -d "${DB_PATH}" ]; then
    echo "Error: ${DB_PATH} not found"
    exit 1
fi

cd "${DB_PATH}"

echo "======================================================================"
echo "Running Complete Validation Suite for ${DB_DIR}"
echo "======================================================================"
echo ""

# Phase 1: Fix Verification
echo "Phase 1: Fix Verification"
echo "----------------------------------------------------------------------"
python3 scripts/verify_fixes.py
echo ""

# Phase 2 & 4: Syntax Validation and Evaluation
echo "Phase 2 & 4: Syntax Validation and Comprehensive Evaluation"
echo "----------------------------------------------------------------------"
python3 scripts/comprehensive_validator.py
echo ""

# Phase 3: Execution Testing (if databases available)
if [ -n "${PG_HOST}" ]; then
    echo "Phase 3: Execution Testing"
    echo "----------------------------------------------------------------------"
    python3 scripts/execution_tester.py
    echo ""
else
    echo "Phase 3: Execution Testing (SKIPPED - no database credentials)"
    echo "----------------------------------------------------------------------"
    echo "Set PG_HOST/PG_USER/PG_PASSWORD to enable"
    echo ""
fi

# Phase 5: Generate Final Report
echo "Phase 5: Generate Final Report"
echo "----------------------------------------------------------------------"
python3 scripts/generate_final_report.py
echo ""

echo "======================================================================"
echo "Validation Complete!"
echo "======================================================================"
echo ""
echo "Results saved to: ${DB_PATH}/results/"
echo "  - fix_verification.json"
echo "  - comprehensive_validation_report.json"
echo "  - query_test_results_postgres.json (if Phase 3 ran)"
echo "  - final_comprehensive_validation_report.json"
echo ""
