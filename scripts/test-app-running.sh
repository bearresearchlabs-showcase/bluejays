#!/usr/bin/env bash
# Start dev server, run integration + E2E tests, then stop server.
# Usage: ./scripts/test-app-running.sh [db-1]  (optional db filter, ignored for now)

set -e
BASE_URL="${BASE_URL:-http://localhost:3007}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cleanup() {
  if [[ -n "$DEV_PID" ]] && kill -0 "$DEV_PID" 2>/dev/null; then
    kill "$DEV_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "Starting dev server on port 3007..."
npm run dev:test &
DEV_PID=$!

echo "Waiting for $BASE_URL/login to respond..."
for i in $(seq 1 60); do
  # Any 2xx/3xx means the server is up (in dev:test /login answers 307)
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/login" 2>/dev/null)
  if echo "$CODE" | grep -qE "^[23][0-9][0-9]$"; then
    echo "Server ready (HTTP $CODE)."
    break
  fi
  sleep 1
  if [[ $i -eq 60 ]]; then
    echo "Timeout waiting for server"
    exit 1
  fi
done

echo "Running integration tests..."
BASE_URL="$BASE_URL" npm run test:integration

echo "Running E2E tests..."
npm run test:e2e

echo "All tests passed."
