#!/bin/bash
# Cursor /repo-health command - Run repo health check and compile MDX
# Usage: /repo-health | /repo-health --lenient
# Outputs: results/repo_health.json, results/repo_health.mdx

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$SCRIPT_DIR"
[ -d .venv ] && . .venv/bin/activate
python3 scripts/db_check.py repo-health "$@"
