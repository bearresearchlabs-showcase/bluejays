#!/bin/bash
# Execute notebooks using multiple methods in Docker containers

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

DATABASES=("db-6" "db-7" "db-8" "db-9" "db-10" "db-11" "db-12" "db-13" "db-14" "db-15")

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

echo "=================================================================================="
echo "MULTIPLE METHODS FOR EXECUTING NOTEBOOKS IN DOCKER CONTAINERS"
echo "=================================================================================="
echo ""

echo "Method 1: Using jupyter nbconvert --execute"
echo "Method 2: Using papermill"
echo "Method 3: Using jupyter execute"
echo "Method 4: Using Python script with nbformat"
echo ""

# Method 1: jupyter nbconvert
execute_method_1() {
    local db_name=$1
    local container_name="${db_name}-container"
    local deliverable="${DB_DELIVERABLE[$db_name]}"
    local notebook_path="/workspace/client/db/${db_name}/${deliverable}/${db_name}.ipynb"
    
    echo "Method 1: jupyter nbconvert --execute"
    docker exec "$container_name" jupyter nbconvert \
        --to notebook \
        --execute \
        "$notebook_path" \
        --output "${db_name}_executed_method1.ipynb" \
        --ExecutePreprocessor.timeout=3600 \
        --ExecutePreprocessor.kernel_name=python3 \
        --ExecutePreprocessor.allow_errors=False
}

# Method 2: papermill
execute_method_2() {
    local db_name=$1
    local container_name="${db_name}-container"
    local deliverable="${DB_DELIVERABLE[$db_name]}"
    local notebook_path="/workspace/client/db/${db_name}/${deliverable}/${db_name}.ipynb"
    
    echo "Method 2: papermill"
    docker exec "$container_name" papermill \
        "$notebook_path" \
        "/workspace/${db_name}_executed_method2.ipynb" \
        --execution-timeout=3600 \
        --log-output
}

# Method 3: jupyter execute (if available)
execute_method_3() {
    local db_name=$1
    local container_name="${db_name}-container"
    local deliverable="${DB_DELIVERABLE[$db_name]}"
    local notebook_path="/workspace/client/db/${db_name}/${deliverable}/${db_name}.ipynb"
    
    echo "Method 3: jupyter execute"
    docker exec "$container_name" python3 -c "
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

with open('$notebook_path', 'r') as f:
    nb = nbformat.read(f, as_version=4)

ep = ExecutePreprocessor(timeout=3600, kernel_name='python3')
ep.preprocess(nb, {'metadata': {'path': '/'}})

with open('/workspace/${db_name}_executed_method3.ipynb', 'w') as f:
    nbformat.write(nb, f)
"
}

# Method 4: Python script execution
execute_method_4() {
    local db_name=$1
    local container_name="${db_name}-container"
    
    echo "Method 4: Python script execution"
    docker exec "$container_name" python3 <<EOF
import json
import subprocess
import sys
from pathlib import Path

notebook_path = Path("$notebook_path")
if notebook_path.exists():
    # Execute notebook cells programmatically
    with open(notebook_path) as f:
        nb = json.load(f)
    
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            exec(source, globals())
    
    # Save executed notebook
    with open('/workspace/${db_name}_executed_method4.ipynb', 'w') as f:
        json.dump(nb, f, indent=1)
EOF
}

# Test all methods for a database
test_all_methods() {
    local db_name=$1
    local container_name="${db_name}-container"
    
    echo ""
    echo "=================================================================================="
    echo "Testing all execution methods for $db_name"
    echo "=================================================================================="
    
    # Ensure container is running
    if ! docker ps | grep -q "$container_name"; then
        echo "Starting container..."
        docker-compose -f docker/docker-compose.yml up -d "$db_name" > /dev/null 2>&1
        sleep 5
    fi
    
    # Wait for PostgreSQL
    echo "Waiting for PostgreSQL..."
    for i in {1..60}; do
        if docker exec "$container_name" su - postgres -c "psql -c 'SELECT 1'" > /dev/null 2>&1; then
            echo "✅ PostgreSQL ready"
            break
        fi
        sleep 1
    done
    
    # Try each method
    for method_num in 1 2 3 4; do
        echo ""
        echo "--- Method $method_num ---"
        if execute_method_$method_num "$db_name" 2>&1; then
            echo "✅ Method $method_num succeeded"
        else
            echo "❌ Method $method_num failed"
        fi
    done
}

# Main execution
if [ $# -eq 0 ]; then
    # Test all databases with method 1 (most reliable)
    echo "Executing all notebooks using Method 1 (jupyter nbconvert)..."
    ./scripts/docker_execute_notebooks.sh
else
    # Test specific database with all methods
    test_all_methods "$1"
fi

echo ""
echo "=================================================================================="
echo "Execution complete"
echo "=================================================================================="
