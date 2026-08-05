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
        -h|--help)
            echo "Usage: ./scripts/docker_postgres_qa.sh [--push] [db-1] [db-5] | -a"
            echo "Start hardened PostgreSQL containers, load schema+data, run QA."
            echo "Env: DOCKER_HUB_USER (required for --push), DOCKER_HUB_TOKEN or docker login"
            exit 0 ;;
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

# Fail fast when the Docker daemon is unreachable instead of hanging in compose
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker daemon unavailable. Start Docker and retry." >&2
    exit 2
fi

echo "=========================================="
echo "PostgreSQL QA: hardened images, load schema, ${PUSH:+push to Docker Hub}"
echo "=========================================="

# 1. Build or pull hardened base and start PostgreSQL
echo ""
echo "[1/4] Building or pulling hardened base and starting PostgreSQL..."
if [ -n "$DOCKER_HUB_USER" ]; then
    HUB_IMAGE="${DOCKER_HUB_USER}/db-postgres-hardened:base"
    if docker pull "$HUB_IMAGE" 2>/dev/null; then
        docker tag "$HUB_IMAGE" db-postgres-hardened:base 2>/dev/null || true
        echo "  Pulled base image from Docker Hub: $HUB_IMAGE"
    else
        echo "  Pull failed, falling back to local build"
        docker compose -f "$COMPOSE_FILE" build --quiet 2>/dev/null || true
    fi
else
    docker compose -f "$COMPOSE_FILE" build --quiet 2>/dev/null || true
fi
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

    # Find schema/data: source-first (app/DATABASE), then client, then legacy data/
    source_app="$BASE_DIR/source/db-${n}/app/DATABASE"
    client_data="$BASE_DIR/client/db/db-${n}/DATABASE"
    source_legacy="$BASE_DIR/source/db-${n}/data"
    data_dir=""
    if [ -d "$source_app" ]; then
        data_dir="$source_app"
    elif [ -d "$client_data" ]; then
        data_dir="$client_data"
    elif [ -d "$source_legacy" ]; then
        data_dir="$source_legacy"
    fi

    if [ -z "$data_dir" ]; then
        echo "  db-${n}: SKIP (no DATABASE/)"
        continue
    fi

    schema=""
    [ -f "$data_dir/schema.sql" ] && schema="$data_dir/schema.sql"

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

# 3b. Transaction integrity check (EXPLAIN, CHECK constraints) when psycopg2 available
echo ""
echo "[3b/4] Transaction integrity check..."
if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import psycopg2" 2>/dev/null; then
        for n in $DB_NUMS; do
            python3 "$BASE_DIR/scripts/transaction_integrity_check.py" "db-${n}" 2>/dev/null || true
        done
    else
        echo "  SKIP: psycopg2 not installed (pip install psycopg2-binary)"
    fi
else
    echo "  SKIP: python3 not found"
fi

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
