#!/usr/bin/env bash
# Root-level pre-commit: log AppSession when .mdc or apps/ or packages/ changed
# Usage: ./scripts/pre-commit-root.sh
# Or add to .git/hooks/pre-commit: exec ./scripts/pre-commit-root.sh

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Log AppSession if .mdc, apps/, or packages/ changed (from git diff)
node scripts/app-session-logger.js --from-git 2>/dev/null || true
