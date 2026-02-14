#!/bin/bash
# QA PostgreSQL: start hardened containers, load schema+data, optionally push to Docker Hub
# Usage: ./scripts/docker_postgres_qa.sh [--push] [db-1] [db-5] | -a
# Env: DOCKER_HUB_USER (required for --push), DOCKER_HUB_TOKEN or docker login

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

COMPOSE_FILE="docker/docker-compose.hardened.yml"
DB_PORTS_START="${DB_PORTS_START:-5436}"

# Parse args
PUSH=false
DB_NUMS=""
for arg in "$@"; do
    case "$arg" in
        --push) PUSH=true ;;
        -a|--all) DB_NUMS=$(seq 1 16) ;;
        *db-*) DB_NUMS="${DB_NUMS} $(echo "$arg" | sed 's/.*db-\([0-9]*\).*/\1/' | grep -E '^[0-9]+$' || true)" ;;
        [0-9]*) DB_NUMS="${DB_NUMS} $arg" ;;
    esac
done
DB_NUMS=$(echo "$DB_NUMS" | tr ' ' '\n' | grep -E '^[0-9]+$' | sort -n | uniq)
# Range: if exactly 2 numbers and first < second, expand
if [ "$(echo "$DB_NUMS" | wc -l)" = "2" ]; then
    A=$(echo "$DB_NUMS" | head -1)
    B=$(echo "$DB_NUMS" | tail -1)
    [ "$A" -lt "$B" ] 2>/dev/null && DB_NUMS=$(seq "$A" "$B")
fi
[ -z "$DB_NUMS" ] && DB_NUMS=$(seq 1 16)

echo "=========================================="
echo "PostgreSQL QA: hardened images, load schema, ${PUSH:+push to Docker Hub}"
echo "=========================================="

# 1. Build hardened base and start PostgreSQL
echo ""
echo "[1/4] Building hardened base and starting PostgreSQL..."
docker compose -f "$COMPOSE_FILE" build --quiet 2>/dev/null || true
docker compose -f "$COMPOSE_FILE" up -d

# 2. Wait for healthy
echo ""
echo "[2/4] Waiting for healthy..."
for i in $(seq 1 30); do
    if docker compose -f "$COMPOSE_FILE" ps 2>/dev/null | grep -q "healthy"; then
        break
    fi
    sleep 2
done
sleep 3

# 3. Load schema+data into each db
echo ""
echo "[3/4] Loading schema and data..."
for n in $DB_NUMS; do
    container="postgres-db-${n}"
    dbname="db${n}"
    port=$((DB_PORTS_START + n - 1))

    # Find schema/data: client/db/db-N/DATABASE/ or source/db-N/app/DATABASE/
    client_data="$BASE_DIR/client/db/db-${n}/DATABASE"
    source_data="$BASE_DIR/source/db-${n}/app/DATABASE"
    source_data_legacy="$BASE_DIR/source/db-${n}/data"
    data_dir=""
    if [ -d "$client_data" ]; then
        data_dir="$client_data"
    elif [ -d "$source_data" ]; then
        data_dir="$source_data"
    elif [ -d "$source_data_legacy" ]; then
        data_dir="$source_data_legacy"
    fi

    if [ -z "$data_dir" ]; then
        echo "  db-${n}: SKIP (no DATABASE/)"
        continue
    fi

    schema=""
    [ -f "$data_dir/schema_postgresql.sql" ] && schema="$data_dir/schema_postgresql.sql"
    [ -z "$schema" ] && [ -f "$data_dir/schema.sql" ] && schema="$data_dir/schema.sql"

    if [ -n "$schema" ]; then
        if docker exec -i "$container" psql -U postgres -d "$dbname" -f - < "$schema" 2>/dev/null; then
            echo "  db-${n}: schema OK"
        else
            echo "  db-${n}: schema load failed (non-fatal)"
        fi
    fi

    if [ -f "$data_dir/data.sql" ]; then
        if docker exec -i "$container" psql -U postgres -d "$dbname" -f - < "$data_dir/data.sql" 2>/dev/null; then
            echo "  db-${n}: data OK"
        else
            echo "  db-${n}: data load failed (non-fatal)"
        fi
    fi
done

# 4. Push hardened image for each DB to Docker Hub (if --push and DOCKER_HUB_USER set)
if [ "$PUSH" = true ]; then
    echo ""
    echo "[4/4] Pushing hardened images to Docker Hub (one per DB)..."
    if [ -z "$DOCKER_HUB_USER" ]; then
        echo "  SKIP: DOCKER_HUB_USER not set"
    else
        for n in $DB_NUMS; do
            container="postgres-db-${n}"
            img="${DOCKER_HUB_USER}/db-postgres-db-${n}:latest"
            if docker commit "$container" "$img" 2>/dev/null; then
                if docker push "$img" 2>/dev/null; then
                    echo "  db-${n}: pushed $img"
                else
                    echo "  db-${n}: push failed (run: docker login)"
                fi
            else
                echo "  db-${n}: commit failed"
            fi
        done
    fi
else
    echo ""
    echo "[4/4] Skip push (use --push with DOCKER_HUB_USER to upload)"
fi

echo ""
echo "=========================================="
echo "PostgreSQL QA complete. Containers running."
echo "  docker compose -f $COMPOSE_FILE down  # stop"
echo "=========================================="
