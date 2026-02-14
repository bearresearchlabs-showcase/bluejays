#!/bin/bash
# Cursor /validate command wrapper
# This script can be called as: /validate [arguments]
# Delegates to db_check.py validate (unified entry point)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "${SCRIPT_DIR}/scripts/db_check.py" validate "$@"
