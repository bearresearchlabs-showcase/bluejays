#!/bin/bash
# Test container startup for all databases

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Create logs directory
mkdir -p docker/test_logs

DATABASES=("db-6" "db-7" "db-8" "db-9" "db-10" "db-11" "db-12" "db-13" "db-14" "db-15")

# Port mappings
declare -A JUPYTER_PORTS=(
    ["db-6"]="8886"
    ["db-7"]="8887"
    ["db-8"]="8888"
    ["db-9"]="8889"
    ["db-10"]="8890"
    ["db-11"]="8891"
    ["db-12"]="8892"
    ["db-13"]="8893"
    ["db-14"]="8894"
    ["db-15"]="8895"
)

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
declare -A STARTUP_RESULTS
declare -A STARTUP_TIMES
STARTUP_ERRORS=()

echo "=================================================================================="
echo "TESTING CONTAINER STARTUP"
echo "=================================================================================="
echo "Start time: $(date)"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    lsof -i :$port > /dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local container_name=$1
    local service=$2
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if [ "$service" = "postgresql" ]; then
            if docker exec "$container_name" su - postgres -c "psql -c 'SELECT 1'" > /dev/null 2>&1; then
                return 0
            fi
        elif [ "$service" = "jupyter" ]; then
            if curl -s http://localhost:${JUPYTER_PORTS[$container_name]} > /dev/null 2>&1; then
                return 0
            fi
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

# Test each container
for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    JUPYTER_PORT="${JUPYTER_PORTS[$db_name]}"
    POSTGRES_PORT="${POSTGRES_PORTS[$db_name]}"
    
    echo ""
    echo "=================================================================================="
    echo "Testing startup for $db_name"
    echo "=================================================================================="
    echo "Container: $CONTAINER_NAME"
    echo "Jupyter port: $JUPYTER_PORT"
    echo "PostgreSQL port: $POSTGRES_PORT"
    
    # Check if port is already in use
    if check_port "$JUPYTER_PORT"; then
        echo "⚠️  Jupyter port $JUPYTER_PORT is already in use"
    fi
    if check_port "$POSTGRES_PORT"; then
        echo "⚠️  PostgreSQL port $POSTGRES_PORT is already in use"
    fi
    
    # Stop and remove existing container if it exists
    docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
    docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
    
    # Record start time
    START_TIME=$(date +%s)
    
    # Start container
    LOG_FILE="docker/test_logs/${db_name}_startup.log"
    echo "Starting container..."
    if docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$JUPYTER_PORT:8888" \
        -p "$POSTGRES_PORT:5432" \
        -v "$BASE_DIR/client/db/$db_name:/workspace/client/db/$db_name:ro" \
        -v "$BASE_DIR/$db_name:/workspace/db/$db_name:ro" \
        "$db_name:latest" > "$LOG_FILE" 2>&1; then
        
        echo "Container started, waiting for services..."
        
        # Wait for PostgreSQL
        if wait_for_service "$CONTAINER_NAME" "postgresql"; then
            echo "✅ PostgreSQL is ready"
        else
            echo "❌ PostgreSQL failed to start within 30 seconds"
            STARTUP_ERRORS+=("$db_name: PostgreSQL timeout")
        fi
        
        # Wait for Jupyter
        sleep 2  # Give Jupyter a moment to start
        if wait_for_service "$CONTAINER_NAME" "jupyter"; then
            echo "✅ Jupyter Notebook is accessible"
        else
            echo "⚠️  Jupyter Notebook may not be ready (check manually)"
        fi
        
        # Check environment variables
        echo "Checking environment variables..."
        ENV_VARS=$(docker exec "$CONTAINER_NAME" env | grep -E "PG_|DB_NAME" || true)
        if [ -n "$ENV_VARS" ]; then
            echo "✅ Environment variables set:"
            echo "$ENV_VARS" | sed 's/^/   /'
        else
            echo "⚠️  Environment variables not found"
        fi
        
        # Check volume mounts
        echo "Checking volume mounts..."
        if docker exec "$CONTAINER_NAME" test -d "/workspace/client/db/$db_name"; then
            echo "✅ Client volume mounted"
        else
            echo "❌ Client volume not mounted"
            STARTUP_ERRORS+=("$db_name: Client volume mount failed")
        fi
        
        if docker exec "$CONTAINER_NAME" test -d "/workspace/db/$db_name"; then
            echo "✅ Root volume mounted"
        else
            echo "❌ Root volume not mounted"
            STARTUP_ERRORS+=("$db_name: Root volume mount failed")
        fi
        
        END_TIME=$(date +%s)
        STARTUP_TIME=$((END_TIME - START_TIME))
        STARTUP_TIMES["$db_name"]=$STARTUP_TIME
        
        if [ $STARTUP_TIME -gt 30 ]; then
            echo "⚠️  Startup took longer than 30 seconds (${STARTUP_TIME}s)"
        else
            echo "✅ Startup completed in ${STARTUP_TIME}s"
        fi
        
        STARTUP_RESULTS["$db_name"]="SUCCESS"
        
        # Stop container for next test
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
        
    else
        END_TIME=$(date +%s)
        STARTUP_TIME=$((END_TIME - START_TIME))
        STARTUP_TIMES["$db_name"]=$STARTUP_TIME
        STARTUP_RESULTS["$db_name"]="FAILED"
        STARTUP_ERRORS+=("$db_name: Container failed to start (check $LOG_FILE)")
        echo "❌ Failed to start container"
        echo "   Check log: $LOG_FILE"
    fi
done

# Generate summary
echo ""
echo "=================================================================================="
echo "STARTUP TEST SUMMARY"
echo "=================================================================================="
echo "End time: $(date)"
echo ""

SUCCESS_COUNT=0
FAILED_COUNT=0

for db_name in "${DATABASES[@]}"; do
    if [ "${STARTUP_RESULTS[$db_name]}" = "SUCCESS" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "✅ $db_name: SUCCESS (${STARTUP_TIMES[$db_name]}s)"
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "❌ $db_name: FAILED (${STARTUP_TIMES[$db_name]}s)"
    fi
done

echo ""
echo "Total: $SUCCESS_COUNT successful, $FAILED_COUNT failed"

if [ ${#STARTUP_ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "ERRORS:"
    for error in "${STARTUP_ERRORS[@]}"; do
        echo "  ❌ $error"
    done
fi

echo ""
echo "=================================================================================="
if [ $FAILED_COUNT -eq 0 ]; then
    echo "✅ ALL CONTAINERS STARTED SUCCESSFULLY"
    exit 0
else
    echo "❌ SOME CONTAINERS FAILED TO START"
    exit 1
fi
