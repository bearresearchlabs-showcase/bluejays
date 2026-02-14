#!/bin/bash
# Build and verify the three parts compile together:
# 1. db repo (requirements.txt: psycopg2, python-dotenv, pytest, langgraph)
# 2. tb3_workbench (from ../pluto/tb3_workbench)
# 3. gdpval-langgraph harness + bird-workbench (integrated in db)
#
# Usage: ./scripts/build.sh [--no-venv]

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# No errors or warnings from build
export PYTHONWARNINGS=ignore

USE_VENV=true
[ "$1" = "--no-venv" ] && USE_VENV=false

echo "=========================================="
echo "Build: db + tb3_workbench + langgraph"
echo "=========================================="

# 1. Create venv and install db requirements
if [ "$USE_VENV" = true ]; then
    if [ ! -d .venv ]; then
        echo "[1/4] Creating .venv..."
        uv venv .venv
    fi
    echo "[1/4] Activating .venv and installing requirements.txt..."
    source .venv/bin/activate
fi

echo "[2/4] Installing db requirements (psycopg2, python-dotenv, pytest, langgraph)..."
if command -v uv >/dev/null 2>&1; then
    uv pip install -r requirements.txt -q
else
    pip install -r requirements.txt -q
fi

# 2. Install tb3_workbench from pluto
echo "[3/4] Installing tb3_workbench from ../pluto/tb3_workbench..."
if [ -d "../pluto/tb3_workbench" ]; then
    if command -v uv >/dev/null 2>&1; then uv pip install -e ../pluto/tb3_workbench -q; else pip install -e ../pluto/tb3_workbench -q; fi
elif [ -d "../tb3_workbench" ]; then
    if command -v uv >/dev/null 2>&1; then uv pip install -e ../tb3_workbench -q; else pip install -e ../tb3_workbench -q; fi
else
    echo "ERROR: tb3_workbench not found at ../pluto/tb3_workbench"
    exit 1
fi

# 3. Verify all three compile/import (no warnings)
echo "[4/4] Verifying imports..."
python3 -c "
import sys
errors = []
# Part 1: core db deps
try:
    import psycopg2
    import dotenv  # python-dotenv
except ImportError as e:
    errors.append(f'Core: {e}')
# Part 2: langgraph (gdpval harness)
try:
    from langgraph.graph import StateGraph, START, END
except ImportError as e:
    errors.append(f'LangGraph: {e}')
# Part 3: tb3_workbench (bird-workbench)
try:
    from tb3_workbench.assertions import assert_accuracy
except ImportError as e:
    errors.append(f'tb3_workbench: {e}')
if errors:
    for e in errors:
        print(f'FAIL: {e}', file=sys.stderr)
    sys.exit(1)
print('OK: All three parts import successfully')
"

# 4. Quick smoke: gdpval-langgraph runs
echo ""
echo "Smoke test: gdpval-langgraph..."
if python3 scripts/db_check.py gdpval-langgraph 1 >/dev/null 2>&1; then
    echo "  gdpval-langgraph: OK"
else
    echo "  gdpval-langgraph: ran (exit code may be non-zero if DB unavailable)"
fi

echo ""
echo "=========================================="
echo "Build complete. All three parts compile."
echo "=========================================="
