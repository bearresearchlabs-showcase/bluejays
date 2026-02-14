#!/bin/bash
# Copy db deliverable HTML/JSON to public/ for Vercel static deployment.
# Vercel prioritizes public/ for "Other" framework - db-N at root may not be served.

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PUBLIC="${ROOT}/public"
mkdir -p "$PUBLIC"

# Copy index if not already in public
[ -f "${ROOT}/index.html" ] && cp "${ROOT}/index.html" "$PUBLIC/"
[ ! -f "${PUBLIC}/index.html" ] && echo "Warning: no index.html" >&2

# Map: db-N/deliverable/dbN-xxx/ -> public/db-N/
for dir in "$ROOT"/db-*/deliverable/db*-*/; do
  [ -d "$dir" ] || continue
  # Extract db-N from path (e.g. db-6 from .../db-6/deliverable/db6-.../)
  db_dir=$(basename "$(dirname "$(dirname "$dir")")")
  [[ "$db_dir" =~ ^db-[0-9]+$ ]] || continue
  mkdir -p "${PUBLIC}/${db_dir}"
  # Copy documentation and deliverable JSON
  [ -f "${dir}${db_dir}_documentation.html" ] && cp "${dir}${db_dir}_documentation.html" "${PUBLIC}/${db_dir}/"
  [ -f "${dir}${db_dir}_deliverable.json" ] && cp "${dir}${db_dir}_deliverable.json" "${PUBLIC}/${db_dir}/"
done

echo "Prepared public/ with db deliverables"
