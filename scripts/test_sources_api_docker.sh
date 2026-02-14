#!/bin/bash
# Iterative test: Unit → Integration → UAT → Docker
# Run from repo root

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== 1. Unit + Integration + UAT (pytest) ==="
python -m pytest tests/test_sources_api.py -v --tb=short || { echo "Tests failed"; exit 1; }

echo ""
echo "=== 2. Docker build + run ==="
docker compose -f docker/docker-compose.sources-api.yml build --no-cache 2>/dev/null || \
  docker-compose -f docker/docker-compose.sources-api.yml build --no-cache

docker compose -f docker/docker-compose.sources-api.yml up -d 2>/dev/null || \
  docker-compose -f docker/docker-compose.sources-api.yml up -d

echo "Waiting for health..."
for i in $(seq 1 15); do
  curl -sf http://localhost:8011/health >/dev/null && break
  sleep 1
done

echo ""
echo "=== 3. Docker smoke test ==="
curl -s http://localhost:8011/health | head -1
curl -s http://localhost:8011/sources | head -1
curl -s "http://localhost:8011/queries?source=db-1" | head -c 200
echo ""

echo ""
echo "=== Done. Sources API: http://localhost:8011 ==="
echo "Stop: docker compose -f docker/docker-compose.sources-api.yml down"
