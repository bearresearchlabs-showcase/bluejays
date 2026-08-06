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

echo "Waiting for $BASE_URL/api/health to respond..."
for i in $(seq 1 60); do
  # /api/health returns 200 unauthenticated (page routes 307 through auth).
  # `|| true` keeps set -e from aborting while the server is still starting.
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health" 2>/dev/null || true)
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

# Hand the server lifecycle to Playwright for E2E: its config.webServer starts
# its own dev server (reuseExistingServer is disabled in CI), so the
# bash-managed instance must be stopped and port 3007 freed first — otherwise
# the second server dies with EADDRINUSE (also triggered by Next.js's
# memory-threshold self-restart leaving a bound listener).
echo "Stopping bash-managed server before E2E..."
cleanup
DEV_PID=""
fuser -k 3007/tcp 2>/dev/null || pkill -f "next dev -p 3007" 2>/dev/null || true
for i in $(seq 1 15); do
  curl -s -o /dev/null "$BASE_URL/login" 2>/dev/null || break
  sleep 1
done

echo "Running E2E tests..."
npm run test:e2e

echo "All tests passed."
