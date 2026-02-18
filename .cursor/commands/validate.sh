#!/bin/bash
# Cursor /validate command - Run validation without overwriting source files
# Usage: /validate [db-1] [db-5] | /validate -a
# Uses --no-overwrite (skip Phase 0 extract) and --pass-fail-only by default.
# Add --full to run full validation with overwrites and verbose output.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ " $* " =~ " --full " ]]; then
  python3 "${SCRIPT_DIR}/scripts/db_check.py" validate "$@"
else
  python3 "${SCRIPT_DIR}/scripts/db_check.py" validate --no-overwrite --pass-fail-only "$@"
fi
