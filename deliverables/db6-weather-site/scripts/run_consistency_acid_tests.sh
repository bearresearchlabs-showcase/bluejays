#!/bin/bash
# Run consistency, ACID, and query execution tests for db-1 through db-16
# Requires: Docker, psycopg2-binary

set -e
cd "$(dirname "$0")/.."

echo "=== Starting PostgreSQL test instance ==="
docker compose -f docker/docker-compose.test-postgresql.yml up -d

echo "Waiting for PostgreSQL to be ready..."
sleep 5
for i in {1..30}; do
  if docker exec db-test-postgres pg_isready -U postgres 2>/dev/null; then
    echo "PostgreSQL is ready."
    break
  fi
  if [ $i -eq 30 ]; then
    echo "PostgreSQL failed to start."
    exit 1
  fi
  sleep 1
done

echo ""
echo "=== Running consistency, ACID, and query tests ==="
python3 scripts/test_all_databases_consistency_acid.py

echo ""
echo "=== Tests complete. Results: results/consistency_acid_query_test_results.json ==="
