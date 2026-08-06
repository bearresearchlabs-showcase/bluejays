#!/bin/bash
#
# Validate queries.md across multiple databases (db-1 through db-5)
# Usage: ./validate_all_databases.sh [start_db] [end_db]
#

set -e

START_DB=${1:-1}
END_DB=${2:-5}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "======================================================================"
echo "Validating Queries Across Databases db-${START_DB} through db-${END_DB}"
echo "======================================================================"
echo ""

SUMMARY_FILE="${ROOT_DIR}/validation_summary_all_databases.json"
SUMMARY_RESULTS=()

for DB_NUM in $(seq ${START_DB} ${END_DB}); do
    DB_DIR="db-${DB_NUM}"
    DB_PATH="${ROOT_DIR}/${DB_DIR}"

    if [ ! -d "${DB_PATH}" ]; then
        echo "⚠️  ${DB_DIR} not found, skipping..."
        continue
    fi

    if [ ! -f "${DB_PATH}/queries/queries.md" ]; then
        echo "⚠️  ${DB_DIR}/queries/queries.md not found, skipping..."
        continue
    fi

    echo "======================================================================"
    echo "Validating ${DB_DIR}"
    echo "======================================================================"
    echo ""

    cd "${DB_PATH}"

    # Run validation phases
    echo "Phase 1: Fix Verification..."
    python3 scripts/verify_fixes.py > /dev/null 2>&1 || echo "  ⚠️  Fix verification script not found or failed"

    echo "Phase 2 & 4: Syntax Validation and Evaluation..."
    python3 scripts/comprehensive_validator.py > /dev/null 2>&1 || echo "  ⚠️  Comprehensive validator not found or failed"

    echo "Phase 5: Generate Final Report..."
    python3 scripts/generate_final_report.py > /dev/null 2>&1 || echo "  ⚠️  Report generator not found or failed"

    # Check if final report exists and extract status
    if [ -f "results/final_comprehensive_validation_report.json" ]; then
        STATUS=$(python3 -c "import json; print(json.load(open('results/final_comprehensive_validation_report.json')).get('overall_status', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
        TOTAL_QUERIES=$(python3 -c "import json; print(json.load(open('results/final_comprehensive_validation_report.json')).get('summary', {}).get('total_queries', 0))" 2>/dev/null || echo "0")
        echo "  ✓ ${DB_DIR}: Status=${STATUS}, Queries=${TOTAL_QUERIES}"
        SUMMARY_RESULTS+=("{\"database\": \"${DB_DIR}\", \"status\": \"${STATUS}\", \"total_queries\": ${TOTAL_QUERIES}}")
    else
        echo "  ⚠️  ${DB_DIR}: No final report generated"
        SUMMARY_RESULTS+=("{\"database\": \"${DB_DIR}\", \"status\": \"NO_REPORT\", \"total_queries\": 0}")
    fi

    echo ""
done

# Generate summary
echo "======================================================================"
echo "Validation Summary"
echo "======================================================================"
echo ""

SUMMARY_JSON="{\"validation_date\": \"$(date -Iseconds)\", \"databases\": ["
for i in "${!SUMMARY_RESULTS[@]}"; do
    if [ $i -gt 0 ]; then
        SUMMARY_JSON+=", "
    fi
    SUMMARY_JSON+="${SUMMARY_RESULTS[$i]}"
done
SUMMARY_JSON+="]}"

echo "${SUMMARY_JSON}" | python3 -m json.tool > "${SUMMARY_FILE}" 2>/dev/null || echo "${SUMMARY_JSON}" > "${SUMMARY_FILE}"

echo "Summary saved to: ${SUMMARY_FILE}"
echo ""
echo "Individual results available in:"
for DB_NUM in $(seq ${START_DB} ${END_DB}); do
    DB_DIR="db-${DB_NUM}"
    if [ -d "${ROOT_DIR}/${DB_DIR}" ]; then
        echo "  - ${DB_DIR}/results/final_comprehensive_validation_report.json"
    fi
done

echo ""
echo "======================================================================"
echo "Validation Complete!"
echo "======================================================================"
