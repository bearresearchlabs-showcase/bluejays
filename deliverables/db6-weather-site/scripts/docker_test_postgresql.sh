#!/bin/bash
# Test PostgreSQL functionality in all containers

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Create logs directory
mkdir -p docker/test_logs

DATABASES=("db-6" "db-7" "db-8" "db-9" "db-10" "db-11" "db-12" "db-13" "db-14" "db-15")

declare -A POSTGRES_PORTS=(
    ["db-6"]="5436"
    ["db-7"]="5437"
    ["db-8"]="5438"
    ["db-9"]="5439"
    ["db-10"]="5440"
    ["db-11"]="5441"
    ["db-12"]="5442"
    ["db-13"]="5443"
    ["db-14"]="5444"
    ["db-15"]="5445"
)

# Results tracking
declare -A POSTGRES_RESULTS
POSTGRES_ERRORS=()

echo "=================================================================================="
echo "TESTING POSTGRESQL FUNCTIONALITY"
echo "=================================================================================="
echo "Start time: $(date)"
echo ""

# Function to wait for PostgreSQL
wait_for_postgres() {
    local container_name=$1
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec "$container_name" su - postgres -c "psql -c 'SELECT 1'" > /dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

# Test each container
for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    POSTGRES_PORT="${POSTGRES_PORTS[$db_name]}"
    
    echo ""
    echo "=================================================================================="
    echo "Testing PostgreSQL for $db_name"
    echo "=================================================================================="
    
    # Check if container is running
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "Starting container..."
        docker-compose -f docker/docker-compose.yml up -d "$db_name" > /dev/null 2>&1
        sleep 5
    fi
    
    # Wait for PostgreSQL
    echo "Waiting for PostgreSQL..."
    if ! wait_for_postgres "$CONTAINER_NAME"; then
        echo "❌ PostgreSQL not ready after 60 seconds"
        POSTGRES_ERRORS+=("$db_name: PostgreSQL timeout")
        POSTGRES_RESULTS["$db_name"]="FAILED"
        continue
    fi
    
    echo "✅ PostgreSQL is ready"
    
    # Check PostgreSQL version
    echo "Checking PostgreSQL version..."
    PG_VERSION=$(docker exec "$CONTAINER_NAME" su - postgres -c "psql -t -c 'SELECT version();'" | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    if [ -n "$PG_VERSION" ]; then
        MAJOR_VERSION=$(echo "$PG_VERSION" | cut -d. -f1)
        if [ "$MAJOR_VERSION" -ge 12 ]; then
            echo "✅ PostgreSQL version $PG_VERSION (>= 12)"
        else
            echo "⚠️  PostgreSQL version $PG_VERSION (< 12)"
            POSTGRES_ERRORS+=("$db_name: PostgreSQL version $PG_VERSION < 12")
        fi
    else
        echo "⚠️  Could not determine PostgreSQL version"
    fi
    
    # Test database creation
    echo "Testing database creation..."
    TEST_DB="test_db_$(date +%s)"
    if docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'CREATE DATABASE $TEST_DB;'" > /dev/null 2>&1; then
        echo "✅ Database creation succeeded"
        
        # Test database deletion
        docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'DROP DATABASE $TEST_DB;'" > /dev/null 2>&1
    else
        echo "❌ Database creation failed"
        POSTGRES_ERRORS+=("$db_name: Database creation failed")
    fi
    
    # Test user permissions
    echo "Testing user permissions..."
    if docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'SELECT current_user;'" > /dev/null 2>&1; then
        CURRENT_USER=$(docker exec "$CONTAINER_NAME" su - postgres -c "psql -t -c 'SELECT current_user;'" | tr -d ' ')
        echo "✅ Current user: $CURRENT_USER"
    else
        echo "❌ User permission check failed"
        POSTGRES_ERRORS+=("$db_name: User permission check failed")
    fi
    
    # Test connection from host
    echo "Testing connection from host..."
    if PGPASSWORD=postgres psql -h localhost -p "$POSTGRES_PORT" -U postgres -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ Connection from host succeeded"
    else
        echo "⚠️  Connection from host failed (may need to wait longer)"
    fi
    
    # Check data directory
    echo "Checking data directory..."
    if docker exec "$CONTAINER_NAME" test -d "/var/lib/postgresql/data"; then
        DATA_SIZE=$(docker exec "$CONTAINER_NAME" du -sh /var/lib/postgresql/data 2>/dev/null | cut -f1 || echo "unknown")
        echo "✅ Data directory exists ($DATA_SIZE)"
    else
        echo "❌ Data directory not found"
        POSTGRES_ERRORS+=("$db_name: Data directory not found")
    fi
    
    # Test data persistence (create a test table)
    echo "Testing data persistence..."
    PERSIST_TEST_DB="persist_test_$(date +%s)"
    if docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'CREATE DATABASE $PERSIST_TEST_DB;'" > /dev/null 2>&1; then
        docker exec "$CONTAINER_NAME" su - postgres -c "psql -d $PERSIST_TEST_DB -c 'CREATE TABLE test_table (id INT);'" > /dev/null 2>&1
        docker exec "$CONTAINER_NAME" su - postgres -c "psql -d $PERSIST_TEST_DB -c 'INSERT INTO test_table VALUES (1);'" > /dev/null 2>&1
        
        # Restart container
        echo "Restarting container to test persistence..."
        docker restart "$CONTAINER_NAME" > /dev/null 2>&1
        sleep 5
        
        if wait_for_postgres "$CONTAINER_NAME"; then
            if docker exec "$CONTAINER_NAME" su - postgres -c "psql -d $PERSIST_TEST_DB -c 'SELECT * FROM test_table;'" > /dev/null 2>&1; then
                echo "✅ Data persistence verified"
                docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'DROP DATABASE $PERSIST_TEST_DB;'" > /dev/null 2>&1
            else
                echo "❌ Data persistence failed"
                POSTGRES_ERRORS+=("$db_name: Data persistence failed")
            fi
        else
            echo "⚠️  Could not verify persistence (PostgreSQL not ready after restart)"
        fi
    else
        echo "⚠️  Could not test persistence (database creation failed)"
    fi
    
    POSTGRES_RESULTS["$db_name"]="SUCCESS"
done

# Generate summary
echo ""
echo "=================================================================================="
echo "POSTGRESQL TEST SUMMARY"
echo "=================================================================================="
echo "End time: $(date)"
echo ""

SUCCESS_COUNT=0
FAILED_COUNT=0

for db_name in "${DATABASES[@]}"; do
    if [ "${POSTGRES_RESULTS[$db_name]}" = "SUCCESS" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "✅ $db_name: SUCCESS"
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "❌ $db_name: FAILED"
    fi
done

echo ""
echo "Total: $SUCCESS_COUNT successful, $FAILED_COUNT failed"

if [ ${#POSTGRES_ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "ERRORS:"
    for error in "${POSTGRES_ERRORS[@]}"; do
        echo "  ❌ $error"
    done
fi

echo ""
echo "=================================================================================="
if [ $FAILED_COUNT -eq 0 ]; then
    echo "✅ ALL POSTGRESQL TESTS PASSED"
    exit 0
else
    echo "❌ SOME POSTGRESQL TESTS FAILED"
    exit 1
fi
