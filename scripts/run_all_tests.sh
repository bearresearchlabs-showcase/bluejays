#!/bin/bash
# Run all DB check and QA tests (mirrors Jenkins pipeline for local testing)
# Usage: ./scripts/run_all_tests.sh [db-1] [db-5] | ./scripts/run_all_tests.sh -a | ./scripts/run_all_tests.sh --all
# Loads .env and client/.env (ANTHROPIC_API_KEY). tb3_workbench installed before bird-workbench.

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Use project venv if present (has tb3_workbench, langgraph, etc.)
PYTHON="python3"
[ -d .venv ] && . .venv/bin/activate && PYTHON=".venv/bin/python"

# Load env (same as jenkins_run.sh) for ANTHROPIC_API_KEY, PG_*, etc.
[ -f .env ] && set -a && . .env && set +a
[ -f client/.env ] && set -a && . client/.env && set +a

# Default to --all when no args
if [ $# -eq 0 ]; then
  set -- -a
fi
DB_ARGS=("$@")
FAILED=0

echo "=========================================="
echo "Running all DB check tests: ${DB_ARGS[*]}"
echo "=========================================="

run() {
    echo ""
    echo ">>> $1"
    if eval "$2"; then
        echo "    PASS"
    else
        echo "    FAIL"
        FAILED=$((FAILED + 1))
    fi
}

# Install workbenches before any tests (tb3_workbench required for bird-workbench + pytest)
if ! python3 -c "import tb3_workbench" 2>/dev/null; then
    echo ""
    echo ">>> Installing workbenches..."
    ./scripts/install_workbenches.sh 2>/dev/null || echo "    tb3_workbench: SKIP (../pluto/tb3_workbench not found)"
fi

run "env_validator" "$PYTHON scripts/env_validator.py --op db"
run "regression (BDD/TDD/DDD)" "REPO_HEALTH_LENIENT=1 $PYTHON scripts/db_check.py test all -q --tb=line"
run "schema-postgresql-validate" "$PYTHON scripts/db_check.py schema-postgresql-validate -a"
run "db_check validate" "$PYTHON scripts/db_check.py validate ${DB_ARGS[*]}"
run "db_check repo-health" "REPO_HEALTH_LENIENT=1 $PYTHON scripts/db_check.py repo-health --lenient"
run "db_check format" "$PYTHON scripts/db_check.py format ${DB_ARGS[*]}"
run "db_check qa-suite" "$PYTHON scripts/db_check.py qa-suite ${DB_ARGS[*]}"
run "bird_export" "$PYTHON scripts/bird_export.py ${DB_ARGS[*]} --single"
run "bird_workbench" "$PYTHON scripts/db_check.py bird-workbench ${DB_ARGS[*]}"
run "gdpval_langgraph" "$PYTHON scripts/db_check.py gdpval-langgraph ${DB_ARGS[*]}"
run "integrity_checks" "$PYTHON scripts/integrity_checks.py ${DB_ARGS[*]}"
run "generate_db_metadata" "$PYTHON scripts/generate_db_metadata.py ${DB_ARGS[*]}"
run "gdpval_validation" "$PYTHON scripts/gdpval_validation.py ${DB_ARGS[*]}"
run "pre_commit_db" "$PYTHON scripts/pre_commit_db.py"
run "db_health" "./scripts/db_health.sh"
run "db_replication_lag" "./scripts/db_replication_lag.sh"
run "db_backup_verify" "./scripts/db_backup_verify.sh scripts/db_check.py"

echo ""
echo "=========================================="
echo "Summary: $FAILED failed"
echo "=========================================="
exit $FAILED
