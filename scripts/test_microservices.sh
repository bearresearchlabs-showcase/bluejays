#!/usr/bin/env bash
# Iterative test for microservices on hardened Docker
# Usage: ./scripts/test_microservices.sh [sources-api|work|full]
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODE="${1:-sources-api}"

run_test() {
  local name="$1"
  local url="$2"
  local expected="$3"
  echo -n "  $name: "
  if resp=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
    if [[ "$resp" == "$expected" ]]; then
      echo "OK ($resp)"
      return 0
    else
      echo "FAIL (got $resp, expected $expected)"
      return 1
    fi
  else
    echo "FAIL (connection error)"
    return 1
  fi
}

echo "=== Microservices test ($MODE) ==="

if [[ "$MODE" == "sources-api" ]] || [[ "$MODE" == "full" ]]; then
  echo ""
  echo "[Sources API]"
  run_test "health" "http://localhost:8011/health" "200" || true
  run_test "sources" "http://localhost:8011/sources" "200" || true
  run_test "queries db-1" "http://localhost:8011/queries?source=db-1" "200" || true
fi

if [[ "$MODE" == "work" ]] || [[ "$MODE" == "full" ]]; then
  echo ""
  echo "[Work API]"
  run_test "health" "http://localhost:8010/health" "200" || true
  echo ""
  echo "[Qdrant]"
  run_test "readyz" "http://localhost:6333/readyz" "200" || true
fi

echo ""
echo "Done."
