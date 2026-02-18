#!/bin/bash
# Cursor /QA command - Run QA checks without overwriting (audit + compliance + integrity)
# Usage: /QA | /QA @db/db-1/ | /QA db-1 | /QA -a
# Uses --check-only by default (no populate/format/resync). Add --full for full suite.
# DOCKER_HUB_USER: when set with --push, pushes images to Docker Hub

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$SCRIPT_DIR"

# Ensure workbenches installed (tb3_workbench for bird-workbench; format/qa-suite work without it)
[ -d .venv ] && . .venv/bin/activate
if ! python3 -c "import tb3_workbench" 2>/dev/null; then
    ./scripts/install_workbenches.sh 2>/dev/null || true
fi

# 1. QA suite — check-only by default (audit + compliance + integrity, no overwrites)
if [[ " $* " =~ " --full " ]]; then
  python3 scripts/db_check.py qa-suite "$@"
else
  python3 scripts/db_check.py qa-suite --check-only "$@"
fi
QA_EXIT=$?

# 2. Hardened PostgreSQL (only when --full)
if [[ " $* " =~ " --full " ]] && command -v docker &>/dev/null; then
    PUSH_ARGS=""
    [ -n "$DOCKER_HUB_USER" ] && PUSH_ARGS="--push"
    ./scripts/docker_postgres_qa.sh $PUSH_ARGS "$@" 2>/dev/null || true
fi

exit $QA_EXIT
