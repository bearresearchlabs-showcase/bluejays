#!/bin/bash
# Integration test: Run all containers simultaneously

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
declare -A INTEGRATION_RESULTS
INTEGRATION_ERRORS=()

echo "=================================================================================="
echo "INTEGRATION TEST: RUNNING ALL CONTAINERS SIMULTANEOUSLY"
echo "=================================================================================="
echo "Start time: $(date)"
echo ""

# Clean up any existing containers
echo "Cleaning up existing containers..."
docker-compose -f docker/docker-compose.yml down > /dev/null 2>&1 || true
sleep 2

# Start all containers simultaneously
echo "Starting all containers..."
START_TIME=$(date +%s)

if docker-compose -f docker/docker-compose.yml up -d > docker/test_logs/integration_startup.log 2>&1; then
    echo "✅ All containers started"
else
    echo "❌ Failed to start all containers"
    cat docker/test_logs/integration_startup.log
    exit 1
fi

# Wait for containers to be ready
echo "Waiting for containers to initialize..."
sleep 10

# Check for port conflicts
echo ""
echo "Checking for port conflicts..."
PORT_CONFLICTS=0

for db_name in "${DATABASES[@]}"; do
    JUPYTER_PORT="${JUPYTER_PORTS[$db_name]}"
    POSTGRES_PORT="${POSTGRES_PORTS[$db_name]}"
    
    # Check Jupyter port
    if lsof -i :$JUPYTER_PORT > /dev/null 2>&1; then
        CONTAINER_COUNT=$(lsof -i :$JUPYTER_PORT | wc -l)
        if [ $CONTAINER_COUNT -gt 2 ]; then
            echo "⚠️  Port conflict detected on Jupyter port $JUPYTER_PORT"
            PORT_CONFLICTS=$((PORT_CONFLICTS + 1))
        fi
    fi
    
    # Check PostgreSQL port
    if lsof -i :$POSTGRES_PORT > /dev/null 2>&1; then
        CONTAINER_COUNT=$(lsof -i :$POSTGRES_PORT | wc -l)
        if [ $CONTAINER_COUNT -gt 2 ]; then
            echo "⚠️  Port conflict detected on PostgreSQL port $POSTGRES_PORT"
            PORT_CONFLICTS=$((PORT_CONFLICTS + 1))
        fi
    fi
done

if [ $PORT_CONFLICTS -eq 0 ]; then
    echo "✅ No port conflicts detected"
else
    echo "❌ Found $PORT_CONFLICTS port conflicts"
    INTEGRATION_ERRORS+=("Port conflicts detected")
fi

# Check all containers are running
echo ""
echo "Checking container status..."
RUNNING_COUNT=0
STOPPED_COUNT=0

for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    if docker ps | grep -q "$CONTAINER_NAME"; then
        RUNNING_COUNT=$((RUNNING_COUNT + 1))
        echo "✅ $CONTAINER_NAME: Running"
    else
        STOPPED_COUNT=$((STOPPED_COUNT + 1))
        echo "❌ $CONTAINER_NAME: Not running"
        INTEGRATION_ERRORS+=("$db_name: Container not running")
    fi
done

echo "Running: $RUNNING_COUNT, Stopped: $STOPPED_COUNT"

# Check resource usage
echo ""
echo "Checking resource usage..."
TOTAL_MEMORY=0
TOTAL_CPU=0

for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    if docker ps | grep -q "$CONTAINER_NAME"; then
        STATS=$(docker stats --no-stream --format "{{.MemUsage}} {{.CPUPerc}}" "$CONTAINER_NAME" 2>/dev/null || echo "0B 0%")
        MEMORY=$(echo "$STATS" | awk '{print $1}')
        CPU=$(echo "$STATS" | awk '{print $2}' | sed 's/%//')
        
        # Extract numeric value from memory (e.g., "1.2GiB" -> "1.2")
        MEMORY_NUM=$(echo "$MEMORY" | sed 's/[^0-9.]//g' | head -1)
        MEMORY_UNIT=$(echo "$MEMORY" | sed 's/[0-9.]//g' | head -1)
        
        # Convert to MB for comparison
        if [ "$MEMORY_UNIT" = "GiB" ] || [ "$MEMORY_UNIT" = "GB" ]; then
            MEMORY_MB=$(echo "$MEMORY_NUM * 1024" | bc 2>/dev/null || echo "0")
        elif [ "$MEMORY_UNIT" = "MiB" ] || [ "$MEMORY_UNIT" = "MB" ]; then
            MEMORY_MB=$MEMORY_NUM
        else
            MEMORY_MB=0
        fi
        
        TOTAL_MEMORY=$(echo "$TOTAL_MEMORY + $MEMORY_MB" | bc 2>/dev/null || echo "$TOTAL_MEMORY")
        TOTAL_CPU=$(echo "$TOTAL_CPU + $CPU" | bc 2>/dev/null || echo "$TOTAL_CPU")
        
        echo "  $CONTAINER_NAME: Memory: $MEMORY, CPU: ${CPU}%"
        
        # Check if memory exceeds 2GB
        if [ -n "$MEMORY_MB" ] && [ "$MEMORY_MB" != "0" ] && (( $(echo "$MEMORY_MB > 2048" | bc -l 2>/dev/null || echo 0) )); then
            echo "    ⚠️  Memory usage exceeds 2GB"
        fi
    fi
done

echo ""
echo "Total memory usage: ${TOTAL_MEMORY}MB"
echo "Total CPU usage: ${TOTAL_CPU}%"

# Test PostgreSQL connectivity for all containers
echo ""
echo "Testing PostgreSQL connectivity..."
POSTGRES_SUCCESS=0
POSTGRES_FAILED=0

for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    POSTGRES_PORT="${POSTGRES_PORTS[$db_name]}"
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        # Test internal connection
        if docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'SELECT 1'" > /dev/null 2>&1; then
            POSTGRES_SUCCESS=$((POSTGRES_SUCCESS + 1))
            echo "✅ $CONTAINER_NAME: PostgreSQL accessible internally"
        else
            POSTGRES_FAILED=$((POSTGRES_FAILED + 1))
            echo "❌ $CONTAINER_NAME: PostgreSQL not accessible internally"
            INTEGRATION_ERRORS+=("$db_name: PostgreSQL internal connection failed")
        fi
        
        # Test external connection (may take a moment)
        sleep 1
        if PGPASSWORD=postgres psql -h localhost -p "$POSTGRES_PORT" -U postgres -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
            echo "  ✅ External connection from host successful"
        else
            echo "  ⚠️  External connection from host failed (may need more time)"
        fi
    fi
done

echo "PostgreSQL connectivity: $POSTGRES_SUCCESS successful, $POSTGRES_FAILED failed"

# Test data persistence
echo ""
echo "Testing data persistence..."
PERSISTENCE_SUCCESS=0
PERSISTENCE_FAILED=0

for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        # Create a test file in the data directory
        TEST_FILE="/var/lib/postgresql/data/persistence_test_$(date +%s)"
        if docker exec "$CONTAINER_NAME" touch "$TEST_FILE" 2>/dev/null; then
            # Restart container
            docker restart "$CONTAINER_NAME" > /dev/null 2>&1
            sleep 5
            
            # Check if file still exists
            if docker exec "$CONTAINER_NAME" test -f "$TEST_FILE" 2>/dev/null; then
                PERSISTENCE_SUCCESS=$((PERSISTENCE_SUCCESS + 1))
                echo "✅ $CONTAINER_NAME: Data persistence verified"
                docker exec "$CONTAINER_NAME" rm -f "$TEST_FILE" 2>/dev/null || true
            else
                PERSISTENCE_FAILED=$((PERSISTENCE_FAILED + 1))
                echo "❌ $CONTAINER_NAME: Data persistence failed"
                INTEGRATION_ERRORS+=("$db_name: Data persistence failed")
            fi
        else
            echo "⚠️  $CONTAINER_NAME: Could not test persistence (permission issue)"
        fi
    fi
done

echo "Data persistence: $PERSISTENCE_SUCCESS successful, $PERSISTENCE_FAILED failed"

# Test container restart
echo ""
echo "Testing container restart capability..."
RESTART_SUCCESS=0
RESTART_FAILED=0

for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        echo "Restarting $CONTAINER_NAME..."
        if docker restart "$CONTAINER_NAME" > /dev/null 2>&1; then
            sleep 5
            
            # Wait for PostgreSQL
            POSTGRES_READY=false
            for i in {1..30}; do
                if docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'SELECT 1'" > /dev/null 2>&1; then
                    POSTGRES_READY=true
                    break
                fi
                sleep 1
            done
            
            if [ "$POSTGRES_READY" = true ]; then
                RESTART_SUCCESS=$((RESTART_SUCCESS + 1))
                echo "✅ $CONTAINER_NAME: Restarted successfully"
            else
                RESTART_FAILED=$((RESTART_FAILED + 1))
                echo "❌ $CONTAINER_NAME: PostgreSQL not ready after restart"
                INTEGRATION_ERRORS+=("$db_name: Restart failed")
            fi
        else
            RESTART_FAILED=$((RESTART_FAILED + 1))
            echo "❌ $CONTAINER_NAME: Failed to restart"
            INTEGRATION_ERRORS+=("$db_name: Restart command failed")
        fi
    fi
done

echo "Container restart: $RESTART_SUCCESS successful, $RESTART_FAILED failed"

END_TIME=$(date +%s)
INTEGRATION_TIME=$((END_TIME - START_TIME))

# Generate summary
echo ""
echo "=================================================================================="
echo "INTEGRATION TEST SUMMARY"
echo "=================================================================================="
echo "End time: $(date)"
echo "Total test time: ${INTEGRATION_TIME}s"
echo ""

if [ $PORT_CONFLICTS -eq 0 ] && [ $STOPPED_COUNT -eq 0 ] && [ $POSTGRES_FAILED -eq 0 ] && [ $PERSISTENCE_FAILED -eq 0 ] && [ $RESTART_FAILED -eq 0 ]; then
    INTEGRATION_RESULTS["overall"]="SUCCESS"
    echo "✅ ALL INTEGRATION TESTS PASSED"
else
    INTEGRATION_RESULTS["overall"]="FAILED"
    echo "❌ SOME INTEGRATION TESTS FAILED"
fi

echo ""
echo "Results:"
echo "  Containers running: $RUNNING_COUNT/$((RUNNING_COUNT + STOPPED_COUNT))"
echo "  Port conflicts: $PORT_CONFLICTS"
echo "  PostgreSQL connectivity: $POSTGRES_SUCCESS/$((POSTGRES_SUCCESS + POSTGRES_FAILED))"
echo "  Data persistence: $PERSISTENCE_SUCCESS/$((PERSISTENCE_SUCCESS + PERSISTENCE_FAILED))"
echo "  Container restart: $RESTART_SUCCESS/$((RESTART_SUCCESS + RESTART_FAILED))"

if [ ${#INTEGRATION_ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "ERRORS:"
    for error in "${INTEGRATION_ERRORS[@]}"; do
        echo "  ❌ $error"
    done
fi

echo ""
echo "=================================================================================="

# Keep containers running for further testing
echo "Containers are still running. To stop them, run:"
echo "  docker-compose -f docker/docker-compose.yml down"

if [ "${INTEGRATION_RESULTS[overall]}" = "SUCCESS" ]; then
    exit 0
else
    exit 1
fi
