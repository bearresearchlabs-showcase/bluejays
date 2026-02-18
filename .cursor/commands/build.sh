#!/bin/bash
# Cursor /build command - Build source → client/db (populate, format, resync, verify)
# Usage: /build | /build db-1 | /build db-1 db-5 | /build -a

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$SCRIPT_DIR"
[ -d .venv ] && . .venv/bin/activate
python3 scripts/db_check.py build "$@"
