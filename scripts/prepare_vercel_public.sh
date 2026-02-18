#!/bin/bash
# Prepare public/ for Vercel static deployment with 100% database coverage.
# Copies HTML, JSON, schema.sql; for large data.sql creates download links (GitHub raw).
# Keeps deploy under 2GB by linking to large files instead of embedding.

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PUBLIC="${ROOT}/public"
mkdir -p "$PUBLIC"

# Max size (MB) to embed data.sql; larger files get a download link
DATA_EMBED_LIMIT_MB=50

# GitHub raw URL base (from git remote, or env)
GITHUB_RAW="${GITHUB_RAW_BASE:-}"
if [ -z "$GITHUB_RAW" ] && [ -d "$ROOT/.git" ]; then
  REMOTE=$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)
  if [[ "$REMOTE" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
    ORG="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]%.git}"
    BRANCH=$(git -C "$ROOT" branch --show-current 2>/dev/null || echo "main")
    GITHUB_RAW="https://raw.githubusercontent.com/${ORG}/${REPO}/${BRANCH}"
  fi
fi

# Copy index if present
[ -f "${ROOT}/index.html" ] && cp "${ROOT}/index.html" "$PUBLIC/"
[ ! -f "${PUBLIC}/index.html" ] && echo "Warning: no index.html" >&2

# Map: db-N/deliverable/dbN-xxx/ or source/db-N/deliverable/dbN-xxx/ -> public/db-N/
for dir in "$ROOT"/db-*/deliverable/db*-*/ "$ROOT"/source/db-*/deliverable/db*-*/; do
  [ -d "$dir" ] || continue
  # Extract db-N from path
  db_dir=$(basename "$(dirname "$(dirname "$dir")")")
  [[ "$db_dir" =~ ^db-[0-9]+$ ]] || continue

  mkdir -p "${PUBLIC}/${db_dir}"
  mkdir -p "${PUBLIC}/${db_dir}/data"

  # Copy documentation and deliverable JSON
  [ -f "${dir}${db_dir}_documentation.html" ] && cp "${dir}${db_dir}_documentation.html" "${PUBLIC}/${db_dir}/"
  [ -f "${dir}${db_dir}_deliverable.json" ] && cp "${dir}${db_dir}_deliverable.json" "${PUBLIC}/${db_dir}/"

  # Copy schema.sql (usually small)
  if [ -d "${dir}data" ]; then
    if [ -f "${dir}data/schema.sql" ]; then
      cp "${dir}data/schema.sql" "${PUBLIC}/${db_dir}/data/"
    fi

    # data.sql: embed if small, else create download link
    if [ -f "${dir}data/data.sql" ]; then
      SIZE_B=$(stat -f%z "${dir}data/data.sql" 2>/dev/null || stat -c%s "${dir}data/data.sql" 2>/dev/null)
      SIZE_MB=$(( SIZE_B / 1048576 ))
      if [ "$SIZE_MB" -lt "$DATA_EMBED_LIMIT_MB" ]; then
        cp "${dir}data/data.sql" "${PUBLIC}/${db_dir}/data/"
      elif [ -n "$GITHUB_RAW" ]; then
        # Relative path from repo root
        REL=$(realpath --relative-to="$ROOT" "${dir}data/data.sql" 2>/dev/null || python3 -c "import os; print(os.path.relpath('${dir}data/data.sql', '${ROOT}'))")
        REL="${REL// /%20}"
        echo "{\"data_sql\": \"${GITHUB_RAW}/${REL}\", \"note\": \"File too large for embed (${SIZE_MB}MB). Download from GitHub.\"}" > "${PUBLIC}/${db_dir}/data/downloads.json"
      else
        echo "{\"data_sql\": null, \"note\": \"File too large (${SIZE_MB}MB). Set GITHUB_RAW_BASE or push to GitHub for download link.\"}" > "${PUBLIC}/${db_dir}/data/downloads.json"
      fi
    fi
  fi
done

echo "Prepared public/ with db deliverables (100% coverage: HTML, JSON, schema, data or download links)"
