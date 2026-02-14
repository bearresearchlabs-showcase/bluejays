#!/bin/bash
# Install all workbenches required for db-check (tb3_workbench for bird-workbench).
# Usage: ./scripts/install_workbenches.sh
# Run before pytest or run_all_tests.sh when tb3_workbench is not yet installed.

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

[ -d .venv ] && . .venv/bin/activate

if python3 -c "import tb3_workbench" 2>/dev/null; then
    echo "tb3_workbench: already installed"
    exit 0
fi

echo "Installing tb3_workbench..."
if [ -d "../pluto/tb3_workbench" ]; then
    TB3_PATH="../pluto/tb3_workbench"
elif [ -d "../tb3_workbench" ]; then
    TB3_PATH="../tb3_workbench"
else
    echo "ERROR: tb3_workbench not found at ../pluto/tb3_workbench or ../tb3_workbench"
    exit 1
fi

# Use regular install (more reliable than editable with uv/PEP 660)
if command -v uv >/dev/null 2>&1; then
    uv pip install "$TB3_PATH" -q
else
    pip install -e "$TB3_PATH" -q
fi

if python3 -c "import tb3_workbench" 2>/dev/null; then
    echo "tb3_workbench: installed successfully"
else
    echo "ERROR: tb3_workbench import failed after install"
    exit 1
fi
