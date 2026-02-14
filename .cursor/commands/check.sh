#!/bin/bash
# Cursor /check command - Run full db_check (validate + format + qa + integrity + compliance)
# Usage: /check db-1 [db-5] | /check -a

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "${SCRIPT_DIR}/scripts/db_check.py" full "$@"
