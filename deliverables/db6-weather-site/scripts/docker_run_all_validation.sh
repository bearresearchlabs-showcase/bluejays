#!/bin/bash
# Run all validation phases in sequence

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

echo "=================================================================================="
echo "RUNNING COMPLETE DOCKER VALIDATION SUITE"
echo "=================================================================================="
echo "Start time: $(date)"
echo ""

# Phase 1: Build Validation
echo ""
echo "=================================================================================="
echo "PHASE 1: BUILD VALIDATION"
echo "=================================================================================="
if ./scripts/docker_build_all.sh; then
    echo "✅ Phase 1 completed"
else
    echo "❌ Phase 1 failed - continuing with remaining phases"
fi

# Phase 2: Container Startup Testing
echo ""
echo "=================================================================================="
echo "PHASE 2: CONTAINER STARTUP TESTING"
echo "=================================================================================="
if ./scripts/docker_test_startup.sh; then
    echo "✅ Phase 2 completed"
else
    echo "⚠️  Phase 2 had issues - continuing"
fi

# Phase 3: PostgreSQL Validation
echo ""
echo "=================================================================================="
echo "PHASE 3: POSTGRESQL VALIDATION"
echo "=================================================================================="
if ./scripts/docker_test_postgresql.sh; then
    echo "✅ Phase 3 completed"
else
    echo "⚠️  Phase 3 had issues - continuing"
fi

# Phase 4: File Path Testing
echo ""
echo "=================================================================================="
echo "PHASE 4: FILE PATH AND RECURSIVE FINDING VALIDATION"
echo "=================================================================================="
if ./scripts/docker_test_file_paths.sh; then
    echo "✅ Phase 4 completed"
else
    echo "⚠️  Phase 4 had issues - continuing"
fi

# Phase 5: Notebook Execution
echo ""
echo "=================================================================================="
echo "PHASE 5: NOTEBOOK EXECUTION TESTING"
echo "=================================================================================="
echo "Note: This phase may take a long time (up to 1 hour per notebook)"
if ./scripts/docker_execute_notebooks.sh; then
    echo "✅ Phase 5 completed"
else
    echo "⚠️  Phase 5 had issues - continuing"
fi

# Phase 6: Query Validation
echo ""
echo "=================================================================================="
echo "PHASE 6: QUERY VALIDATION"
echo "=================================================================================="
if ./scripts/docker_validate_queries.sh; then
    echo "✅ Phase 6 completed"
else
    echo "⚠️  Phase 6 had issues - continuing"
fi

# Phase 7: Integration Testing
echo ""
echo "=================================================================================="
echo "PHASE 7: INTEGRATION TESTING"
echo "=================================================================================="
if ./scripts/docker_integration_test.sh; then
    echo "✅ Phase 7 completed"
else
    echo "⚠️  Phase 7 had issues - continuing"
fi

# Phase 8: Generate Report
echo ""
echo "=================================================================================="
echo "PHASE 8: GENERATING VALIDATION REPORT"
echo "=================================================================================="
if ./scripts/docker_generate_validation_report.sh; then
    echo "✅ Phase 8 completed"
else
    echo "⚠️  Phase 8 had issues"
fi

echo ""
echo "=================================================================================="
echo "VALIDATION SUITE COMPLETE"
echo "=================================================================================="
echo "End time: $(date)"
echo ""
echo "Review the validation report:"
echo "  cat docker/validation_report.md"
echo ""
echo "=================================================================================="
