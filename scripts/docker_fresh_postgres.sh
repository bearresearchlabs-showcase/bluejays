#!/bin/bash
# Spin up a fresh PostgreSQL container for testing.
# Stops/removes existing db-test-postgres, starts new one with empty volume.
# Uses docker/docker-compose.test-postgresql.yml (port 5433).

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

COMPOSE_FILE="docker/docker-compose.test-postgresql.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "Error: $COMPOSE_FILE not found"
    exit 1
fi

echo "Stopping existing postgres-test container..."
docker compose -f "$COMPOSE_FILE" down -v 2>/dev/null || true

echo "Starting fresh PostgreSQL container..."
docker compose -f "$COMPOSE_FILE" up -d

echo "Waiting for PostgreSQL to be ready..."
for i in $(seq 1 30); do
    if docker compose -f "$COMPOSE_FILE" exec -T postgres-test pg_isready -U postgres 2>/dev/null; then
        echo "PostgreSQL is ready."
        exit 0
    fi
    echo "  Waiting... ($i/30)"
    sleep 1
done

echo "Error: PostgreSQL did not become ready in time."
exit 1
