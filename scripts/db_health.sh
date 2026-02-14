#!/bin/bash
# Quick health check: containers, connections, disk
# Output: JSON for tooling

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

echo "{"
echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
echo "  \"docker\": {"
if command -v docker &>/dev/null; then
    RUNNING=$(docker ps -q -f name=postgres 2>/dev/null | wc -l)
    echo "    \"available\": true,"
    echo "    \"postgres_containers_running\": $RUNNING"
else
    echo "    \"available\": false"
fi
echo "  },"
echo "  \"disk\": {"
if command -v df &>/dev/null; then
    DF=$(df -k "$BASE_DIR" 2>/dev/null | tail -1)
    AVAIL=$(echo "$DF" | awk '{print $4}')
    echo "    \"available_kb\": $AVAIL"
fi
echo "  }"
echo "}"
