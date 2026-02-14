#!/bin/bash
# Cursor /QA command - Run QA suite + hardened PostgreSQL + optional Docker Hub push
# Usage: /QA | /QA @db/db-1/ | /QA db-1 | /QA --push | /QA -a
# DOCKER_HUB_USER: when set with --push, pushes images to Docker Hub

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$SCRIPT_DIR"

# Ensure workbenches installed (tb3_workbench for bird-workbench; format/qa-suite work without it)
[ -d .venv ] && . .venv/bin/activate
if ! python3 -c "import tb3_workbench" 2>/dev/null; then
    ./scripts/install_workbenches.sh 2>/dev/null || true
fi

# 1. QA suite (format → resync → audit + compliance + integrity)
python3 scripts/db_check.py qa-suite "$@"
QA_EXIT=$?

# 2. Hardened PostgreSQL: start, load schema, optionally push to Docker Hub
if command -v docker &>/dev/null; then
    PUSH_ARGS=""
    [ -n "$DOCKER_HUB_USER" ] && PUSH_ARGS="--push"
    ./scripts/docker_postgres_qa.sh $PUSH_ARGS "$@" 2>/dev/null || true
fi

exit $QA_EXIT
