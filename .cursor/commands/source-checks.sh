#!/bin/bash
# Cursor /source-checks command - Run source material validation
# Usage: /source-checks | /source-checks db-1 | /source-checks db-1 db-5 | /source-checks -a
# Validates: queries.json, queries_header, schema, data, queries.md

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$SCRIPT_DIR"
[ -d .venv ] && . .venv/bin/activate
python3 scripts/db_check.py source-checks "$@"
