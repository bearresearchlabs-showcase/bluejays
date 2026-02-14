#!/usr/bin/env bash
# Run scrub_keywords.py across 4 worktrees in parallel (for Cursor 4x Parallel Agents).
# Each agent runs: python3 scripts/scrub_keywords.py --worktree INDEX 4
#
# Usage:
#   ./scripts/scrub_4x.sh              # Run all 4 in parallel (background)
#   ./scripts/scrub_4x.sh --dry-run     # Dry-run all 4 in parallel
#
# For Cursor Composer 4x: Use prompt:
#   "Run scrub: Agent 0: python3 scripts/scrub_keywords.py --worktree 0 4
#              Agent 1: python3 scripts/scrub_keywords.py --worktree 1 4
#              Agent 2: python3 scripts/scrub_keywords.py --worktree 2 4
#              Agent 3: python3 scripts/scrub_keywords.py --worktree 3 4"

set -e
cd "$(dirname "$0")/.."
DRY=""
[[ "${1:-}" == "--dry-run" ]] && DRY="--dry-run"

python3 scripts/scrub_keywords.py --worktree 0 4 $DRY &
python3 scripts/scrub_keywords.py --worktree 1 4 $DRY &
python3 scripts/scrub_keywords.py --worktree 2 4 $DRY &
python3 scripts/scrub_keywords.py --worktree 3 4 $DRY &
wait
echo "All 4 worktree scrub runs complete."
