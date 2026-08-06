#!/bin/bash
# Execute all notebooks in their respective Docker containers with enhanced error handling and validation

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Create logs directory
mkdir -p docker/test_logs

# Database to deliverable folder mapping
declare -A DB_DELIVERABLE=(
    ["db-6"]="db6-weather-consulting-insurance"
    ["db-7"]="db7-maritime-shipping-intelligence"
    ["db-8"]="db8-job-market"
    ["db-9"]="db9-shipping-database"
    ["db-10"]="db10-shopping-aggregator-database"
    ["db-11"]="db11-parking-database"
    ["db-12"]="db12-credit-card-and-rewards-optimization-system"
    ["db-13"]="db13-ai-benchmark-marketing-database"
    ["db-14"]="db14-cloud-instance-cost-database"
    ["db-15"]="db15-electricity-cost-and-solar-rebate-database"
)

DATABASES=("db-6" "db-7" "db-8" "db-9" "db-10" "db-11" "db-12" "db-13" "db-14" "db-15")

# Results tracking
declare -A EXECUTION_RESULTS
declare -A EXECUTION_TIMES
EXECUTION_ERRORS=()

echo "=================================================================================="
echo "EXECUTING NOTEBOOKS IN DOCKER CONTAINERS"
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

# Function to validate notebook execution result
validate_notebook_result() {
    local container_name=$1
    local output_file=$2
    
    # Check if output file exists
    if ! docker exec "$container_name" test -f "$output_file"; then
        return 1
    fi
    
    # Check for execution errors in the notebook
    if docker exec "$container_name" grep -q '"execution_state": "error"' "$output_file" 2>/dev/null; then
        return 1
    fi
    
    # Check for traceback or error messages
    if docker exec "$container_name" grep -qi "traceback\|error\|exception" "$output_file" 2>/dev/null; then
        # Check if it's just in comments or actual errors
        if docker exec "$container_name" grep -qi '"output_type": "error"' "$output_file" 2>/dev/null; then
            return 1
        fi
    fi
    
    return 0
}

# Ensure containers are running
echo "Checking containers..."
docker-compose -f docker/docker-compose.yml up -d > /dev/null 2>&1
sleep 5

for db_name in "${DATABASES[@]}"; do
    deliverable="${DB_DELIVERABLE[$db_name]}"
    container_name="${db_name}-container"
    notebook_path="/workspace/client/db/${db_name}/${deliverable}/${db_name}.ipynb"
    output_file="/workspace/${db_name}_executed.ipynb"
    log_file="docker/test_logs/${db_name}_notebook_execution.log"
    
    echo ""
    echo "=================================================================================="
    echo "Executing notebook for $db_name"
    echo "=================================================================================="
    echo "Container: $container_name"
    echo "Notebook: $notebook_path"
    echo "Output: $output_file"
    
    # Check if container is running
    if ! docker ps | grep -q "$container_name"; then
        echo "⚠️  Container $container_name is not running. Starting it..."
        docker-compose -f docker/docker-compose.yml up -d "$db_name" > /dev/null 2>&1
        sleep 5
    fi
    
    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    if ! wait_for_postgres "$container_name"; then
        echo "❌ PostgreSQL not ready after 60 seconds"
        EXECUTION_ERRORS+=("$db_name: PostgreSQL timeout")
        EXECUTION_RESULTS["$db_name"]="FAILED"
        EXECUTION_TIMES["$db_name"]=0
        continue
    fi
    echo "✅ PostgreSQL is ready!"
    
    # Verify notebook exists
    if ! docker exec "$container_name" test -f "$notebook_path"; then
        echo "❌ Notebook not found at $notebook_path"
        EXECUTION_ERRORS+=("$db_name: Notebook not found")
        EXECUTION_RESULTS["$db_name"]="FAILED"
        EXECUTION_TIMES["$db_name"]=0
        continue
    fi
    
    # Record start time
    START_TIME=$(date +%s)
    
    # Execute notebook with timeout and error handling
    echo "Executing notebook (timeout: 3600s)..."
    EXECUTION_SUCCESS=false
    
    if timeout 3700 docker exec "$container_name" jupyter nbconvert \
        --to notebook \
        --execute \
        "$notebook_path" \
        --output "${db_name}_executed.ipynb" \
        --ExecutePreprocessor.timeout=3600 \
        --ExecutePreprocessor.kernel_name=python3 \
        --ExecutePreprocessor.allow_errors=False \
        > "$log_file" 2>&1; then
        
        # Validate execution result
        if validate_notebook_result "$container_name" "$output_file"; then
            EXECUTION_SUCCESS=true
        else
            echo "⚠️  Notebook executed but contains errors"
            EXECUTION_ERRORS+=("$db_name: Notebook contains execution errors (check $log_file)")
        fi
    else
        EXECUTION_SUCCESS=false
        EXECUTION_ERRORS+=("$db_name: Notebook execution failed (check $log_file)")
    fi
    
    END_TIME=$(date +%s)
    EXECUTION_TIME=$((END_TIME - START_TIME))
    EXECUTION_TIMES["$db_name"]=$EXECUTION_TIME
    
    if [ "$EXECUTION_SUCCESS" = true ]; then
        EXECUTION_RESULTS["$db_name"]="SUCCESS"
        echo "✅ Successfully executed notebook for $db_name (${EXECUTION_TIME}s)"
        
        # Check for database initialization
        echo "Verifying database initialization..."
        DB_NAME_LOWER=$(echo "$db_name" | tr '[:upper:]' '[:lower:]' | tr '-' '')
        if docker exec "$container_name" su - postgres -c "psql -lqt" | cut -d \| -f 1 | grep -qw "$DB_NAME_LOWER"; then
            echo "✅ Database $DB_NAME_LOWER exists"
        else
            echo "⚠️  Database $DB_NAME_LOWER not found (may be created during execution)"
        fi
        
        # Check for execution reports
        echo "Checking for execution reports..."
        REPORT_PATHS=(
            "/workspace/results/${db_name}_comprehensive_report.json"
            "/workspace/db/${db_name}/results/${db_name}_comprehensive_report.json"
        )
        REPORT_FOUND=false
        for report_path in "${REPORT_PATHS[@]}"; do
            if docker exec "$container_name" test -f "$report_path"; then
                echo "✅ Execution report found: $report_path"
                REPORT_FOUND=true
                break
            fi
        done
        if [ "$REPORT_FOUND" = false ]; then
            echo "⚠️  Execution report not found (may be generated in different location)"
        fi
    else
        EXECUTION_RESULTS["$db_name"]="FAILED"
        echo "❌ Failed to execute notebook for $db_name (${EXECUTION_TIME}s)"
        echo "   Check log: $log_file"
    fi
done

# Generate summary
echo ""
echo "=================================================================================="
echo "NOTEBOOK EXECUTION SUMMARY"
echo "=================================================================================="
echo "End time: $(date)"
echo ""

SUCCESS_COUNT=0
FAILED_COUNT=0
TOTAL_TIME=0

for db_name in "${DATABASES[@]}"; do
    if [ "${EXECUTION_RESULTS[$db_name]}" = "SUCCESS" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        TOTAL_TIME=$((TOTAL_TIME + ${EXECUTION_TIMES[$db_name]}))
        echo "✅ $db_name: SUCCESS (${EXECUTION_TIMES[$db_name]}s)"
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "❌ $db_name: FAILED (${EXECUTION_TIMES[$db_name]}s)"
    fi
done

echo ""
echo "Total: $SUCCESS_COUNT successful, $FAILED_COUNT failed"
if [ $SUCCESS_COUNT -gt 0 ]; then
    AVG_TIME=$((TOTAL_TIME / SUCCESS_COUNT))
    echo "Average execution time: ${AVG_TIME}s"
fi

if [ ${#EXECUTION_ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "ERRORS:"
    for error in "${EXECUTION_ERRORS[@]}"; do
        echo "  ❌ $error"
    done
fi

echo ""
echo "=================================================================================="
if [ $FAILED_COUNT -eq 0 ]; then
    echo "✅ ALL NOTEBOOKS EXECUTED SUCCESSFULLY"
    exit 0
else
    echo "❌ SOME NOTEBOOKS FAILED TO EXECUTE"
    exit 1
fi
