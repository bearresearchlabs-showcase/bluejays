#!/bin/bash
# Run from apps/web; creates client/db at repo root for website build
set -e
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
python3 scripts/populate_app_trifecta.py -a
python3 scripts/resync_client_db.py
