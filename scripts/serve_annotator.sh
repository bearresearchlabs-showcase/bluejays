#!/bin/bash
# Serve annotator app for Label Studio text-to-SQL review.
# Run on multiple ports for multiple annotators: ./scripts/serve_annotator.sh 8766 &
# Usage: ./scripts/serve_annotator.sh [port]
# Requires: LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY or LABEL_STUDIO_USER_TOKEN
cd "$(dirname "$0")/.."
PORT="${1:-8766}"
echo "Starting annotator app on port $PORT"
echo "  Open: http://localhost:$PORT/"
echo "  For multiple annotators: run with different ports (8766, 8767, 8768...)"
[ -f .env ] && set -a && . .env && set +a
exec python3 scripts/annotator_app.py --port "$PORT"
