#!/bin/bash
# Cursor /test command - Run BDD/TDD/DDD test suites
# Usage: /test | /test schema-data | /test repo-health | /test queries-md | /test source-checks | /test all
# Options: -v (verbose), --lenient (REPO_HEALTH_LENIENT=1 for migration)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$SCRIPT_DIR"
[ -d .venv ] && . .venv/bin/activate
python3 scripts/db_check.py test "$@"
