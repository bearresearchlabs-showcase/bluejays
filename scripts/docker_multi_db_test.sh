#!/bin/bash
# Run db_check validate against multiple DBs using docker-compose.multi-db.yml.
# Loads client/.env for PG_* vars; starts containers; runs validate in parallel.

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

COMPOSE_FILE="docker/docker-compose.multi-db.yml"
ENV_FILE="client/.env"

if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "Error: $COMPOSE_FILE not found"
    exit 1
fi

# Load client/.env if present
if [[ -f "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Start all DB containers
echo "Starting multi-DB PostgreSQL containers..."
docker compose -f "$COMPOSE_FILE" up -d

echo "Waiting for containers to be healthy..."
sleep 10
for i in $(seq 1 30); do
    if docker compose -f "$COMPOSE_FILE" ps | grep -q "healthy"; then
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

# Run db_check validate for each DB (parallel with xargs)
# Export PG_HOST, PG_PORT per DB: db-N uses port 5435+N
echo ""
echo "Running db_check validate for db-1 through db-16..."
FAILED=0
for n in $(seq 1 16); do
    export PG_HOST=localhost
    export PG_PORT=$((5435 + n))
    export PG_DATABASE="db${n}"
    export PG_USER="${PG_USER:-postgres}"
    export PG_PASSWORD="${PG_PASSWORD:-postgres}"
    echo "  Validating db-${n} (port $PG_PORT)..."
    if python3 scripts/db_check.py validate "$n" 2>/dev/null; then
        echo "    db-${n}: PASS"
    else
        echo "    db-${n}: FAIL or SKIP"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "Multi-DB test complete. Failures: $FAILED"
exit $FAILED
