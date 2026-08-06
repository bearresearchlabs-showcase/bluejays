#!/bin/bash
# Cursor /validate command wrapper
# This script can be called as: /validate [arguments]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "${SCRIPT_DIR}/scripts/validate.py" "$@"
