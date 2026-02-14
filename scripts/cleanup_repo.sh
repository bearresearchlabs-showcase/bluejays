#!/usr/bin/env bash
# Clean up /db — remove files that are not needed for the annotator app and data annotation.
# Run from repo root. Use --dry-run to preview.

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

rm_cmd() {
  if [[ -e "$1" ]]; then
    if $DRY_RUN; then echo "[DRY-RUN] would remove: $1"; else rm -rf "$1" 2>/dev/null || true; echo "Removed: $1"; fi
  fi
}

echo "=== Cleanup: traces, caches, duplicates ==="
rm_cmd traces
rm_cmd __pycache__
rm_cmd .pytest_cache
rm_cmd db.egg-info

# Duplicate config
[[ -f "vercel 2.json" ]] && rm_cmd "vercel 2.json"

# Legacy root db-6 (source/db-6 is canonical)
if [[ -d "db-6" ]] && [[ -d "source/db-6" ]]; then
  rm_cmd db-6
fi

echo ""
echo "=== Large archives (if present) — move to /tmp or delete manually ==="
for f in client.zip db.zip package.zip; do
  if [[ -f "$f" ]]; then
    echo "  $f exists ($(du -h "$f" 2>/dev/null | cut -f1)) — consider: mv $f /tmp/"
  fi
done

echo ""
echo "Done. Use --dry-run to preview only."
