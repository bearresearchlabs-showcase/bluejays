#!/usr/bin/env bash
# Run Claude rewrite one database at a time to avoid long-running process aborts.
# Usage: ./scripts/run_claude_rewrite_one_at_a_time.sh [db-numbers...]
# Example: ./scripts/run_claude_rewrite_one_at_a_time.sh 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
# Example: ./scripts/run_claude_rewrite_one_at_a_time.sh  # runs db-1 through db-16

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

DBS=("${@:-1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16}")

for n in "${DBS[@]}"; do
  echo "=== db-$n ==="
  .venv/bin/python3 scripts/claude_rewrite_description_and_purpose.py "$n" --apply --incremental
  echo ""
done

echo "Done: ${#DBS[@]} databases"
