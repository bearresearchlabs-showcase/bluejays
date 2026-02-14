#!/usr/bin/env bash
# Create a branch for each db in source/ and push to https://github.com/1digitaldesign/db
# Usage: ./scripts/create_db_branches.sh [--push]
# Without --push: only create/update local branches
# With --push: create branches and push to remote 'db'

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${REMOTE:-db}"
cd "$ROOT"

# Discover db-N directories in source/
DBS=()
for d in source/db-*; do
  [[ -d "$d" ]] || continue
  name=$(basename "$d")
  if [[ "$name" =~ ^db-([0-9]+)$ ]]; then
    DBS+=("$name")
  fi
done

# Sort numerically (db-1, db-2, ..., db-10, db-11, ...)
DBS=($(printf '%s\n' "${DBS[@]}" | sort -t'-' -k2 -n))

if [[ ${#DBS[@]} -eq 0 ]]; then
  echo "No db-N directories found in source/"
  exit 1
fi

echo "Found ${#DBS[@]} databases: ${DBS[*]}"
echo "Remote: $REMOTE ($(git remote get-url "$REMOTE" 2>/dev/null || echo 'not configured'))"
echo ""

# Ensure we're on main and it's up to date
CURRENT=$(git branch --show-current)
if [[ "$CURRENT" != "main" ]]; then
  echo "Checking out main..."
  git checkout main
fi

# Create/update branch for each db
for db in "${DBS[@]}"; do
  echo "Creating/updating branch: $db"
  git checkout -B "$db" main
done

# Return to main
git checkout main

# Push if requested
if [[ "${1:-}" == "--push" ]]; then
  echo ""
  echo "Pushing all branches to $REMOTE..."
  for db in "${DBS[@]}"; do
    echo "  Pushing $db..."
    git push "$REMOTE" "$db" || { echo "  WARNING: push $db failed"; }
  done
  echo ""
  echo "Done. Branches pushed to https://github.com/1digitaldesign/db"
else
  echo ""
  echo "Branches created locally. Run with --push to push to remote:"
  echo "  ./scripts/create_db_branches.sh --push"
fi
