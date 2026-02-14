#!/bin/bash
# Cursor /format command wrapper
# This script can be called as: /format [arguments]
# Delegates to db_check.py format (unified entry point)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "${SCRIPT_DIR}/scripts/db_check.py" format "$@"
