#!/usr/bin/env bash
# Kill processes on all dev/test/prod ports (3000-3002, 3006-3008)
# Run: ./scripts/kill-dev-sessions.sh or npm run kill:sessions

set -e
PORTS="3000 3001 3002 3006 3007 3008"
for port in $PORTS; do
  pids=$(lsof -ti :$port 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "Killing PIDs on port $port: $pids"
    echo "$pids" | tr ' ' '\n' | xargs kill -9 2>/dev/null || true
  fi
done
echo "Done. Ports $PORTS cleared."
