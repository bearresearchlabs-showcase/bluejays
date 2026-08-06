#!/bin/bash
# Cursor /format command wrapper
# This script can be called as: /format [arguments]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "${SCRIPT_DIR}/scripts/format.py" "$@"
