#!/bin/bash
# Test file paths and recursive finding in containers

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Create logs directory
mkdir -p docker/test_logs

DATABASES=("db-6" "db-7" "db-8" "db-9" "db-10" "db-11" "db-12" "db-13" "db-14" "db-15")

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

# Results tracking
declare -A PATH_RESULTS
PATH_ERRORS=()

echo "=================================================================================="
echo "TESTING FILE PATHS AND RECURSIVE FINDING"
echo "=================================================================================="
echo "Start time: $(date)"
echo ""

# Function to test recursive finding
test_recursive_find() {
    local container_name=$1
    local start_dir=$2
    local filename=$3
    
    docker exec "$container_name" python3 -c "
from pathlib import Path
import sys

def find_file_recursively(start_dir, filename):
    try:
        for path in Path(start_dir).rglob(filename):
            return str(path)
    except:
        pass
    return None

result = find_file_recursively('$start_dir', '$filename')
if result:
    print(result)
    sys.exit(0)
else:
    sys.exit(1)
" 2>/dev/null
}

# Test each container
for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    DELIVERABLE="${DB_DELIVERABLE[$db_name]}"
    
    echo ""
    echo "=================================================================================="
    echo "Testing file paths for $db_name"
    echo "=================================================================================="
    
    # Check if container is running
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "Starting container..."
        docker-compose -f docker/docker-compose.yml up -d "$db_name" > /dev/null 2>&1
        sleep 5
    fi
    
    ERRORS_FOUND=0
    
    # Test notebook path
    echo "Testing notebook path..."
    NOTEBOOK_PATH="/workspace/client/db/${db_name}/${deliverable}/${db_name}.ipynb"
    if docker exec "$CONTAINER_NAME" test -f "$NOTEBOOK_PATH"; then
        echo "✅ Notebook found at: $NOTEBOOK_PATH"
    else
        echo "❌ Notebook not found at: $NOTEBOOK_PATH"
        PATH_ERRORS+=("$db_name: Notebook not found at $NOTEBOOK_PATH")
        ERRORS_FOUND=$((ERRORS_FOUND + 1))
        
        # List available files
        echo "   Available files in /workspace/client/db/${db_name}/:"
        docker exec "$CONTAINER_NAME" find "/workspace/client/db/${db_name}/" -name "*.ipynb" 2>/dev/null | head -5 | sed 's/^/     /' || echo "     (none found)"
    fi
    
    # Test recursive finding of queries.json from client/db root
    echo "Testing recursive finding of queries.json from client/db root..."
    if RESULT=$(test_recursive_find "$CONTAINER_NAME" "/workspace/client/db" "queries.json"); then
        echo "✅ queries.json found recursively: $RESULT"
    else
        echo "⚠️  queries.json not found recursively from /workspace/client/db"
        
        # Try fallback to root db directory
        echo "   Trying fallback to root db directory..."
        FALLBACK_PATH="/workspace/db/${db_name}/queries/queries.json"
        if docker exec "$CONTAINER_NAME" test -f "$FALLBACK_PATH"; then
            echo "✅ queries.json found at fallback path: $FALLBACK_PATH"
        else
            echo "❌ queries.json not found at fallback path either"
            PATH_ERRORS+=("$db_name: queries.json not found (client or root)")
            ERRORS_FOUND=$((ERRORS_FOUND + 1))
        fi
    fi
    
    # Test recursive finding of schema.sql
    echo "Testing recursive finding of schema.sql..."
    if RESULT=$(test_recursive_find "$CONTAINER_NAME" "/workspace/client/db" "schema.sql"); then
        echo "✅ schema.sql found recursively: $RESULT"
    else
        echo "⚠️  schema.sql not found recursively from /workspace/client/db"
        
        # Try fallback
        FALLBACK_PATH="/workspace/db/${db_name}/data/schema.sql"
        if docker exec "$CONTAINER_NAME" test -f "$FALLBACK_PATH"; then
            echo "✅ schema.sql found at fallback path: $FALLBACK_PATH"
        else
            echo "❌ schema.sql not found at fallback path either"
            PATH_ERRORS+=("$db_name: schema.sql not found (client or root)")
            ERRORS_FOUND=$((ERRORS_FOUND + 1))
        fi
    fi
    
    # Test recursive finding of data.sql
    echo "Testing recursive finding of data.sql..."
    if RESULT=$(test_recursive_find "$CONTAINER_NAME" "/workspace/client/db" "data.sql"); then
        echo "✅ data.sql found recursively: $RESULT"
    else
        echo "⚠️  data.sql not found recursively from /workspace/client/db"
        
        # Try fallback
        FALLBACK_PATH="/workspace/db/${db_name}/data/data.sql"
        if docker exec "$CONTAINER_NAME" test -f "$FALLBACK_PATH"; then
            echo "✅ data.sql found at fallback path: $FALLBACK_PATH"
        else
            echo "❌ data.sql not found at fallback path either"
            PATH_ERRORS+=("$db_name: data.sql not found (client or root)")
            ERRORS_FOUND=$((ERRORS_FOUND + 1))
        fi
    fi
    
    # Test that client/db path exists
    echo "Testing client/db directory structure..."
    if docker exec "$CONTAINER_NAME" test -d "/workspace/client/db/${db_name}"; then
        echo "✅ Client directory exists: /workspace/client/db/${db_name}"
        
        # List subdirectories
        SUBDIRS=$(docker exec "$CONTAINER_NAME" ls -d "/workspace/client/db/${db_name}"/* 2>/dev/null | wc -l || echo "0")
        echo "   Subdirectories found: $SUBDIRS"
    else
        echo "❌ Client directory not found"
        PATH_ERRORS+=("$db_name: Client directory /workspace/client/db/${db_name} not found")
        ERRORS_FOUND=$((ERRORS_FOUND + 1))
    fi
    
    # Test that root db path exists
    echo "Testing root db directory structure..."
    if docker exec "$CONTAINER_NAME" test -d "/workspace/db/${db_name}"; then
        echo "✅ Root directory exists: /workspace/db/${db_name}"
        
        # Check for queries and data directories
        if docker exec "$CONTAINER_NAME" test -d "/workspace/db/${db_name}/queries"; then
            echo "✅ Queries directory exists"
        else
            echo "⚠️  Queries directory not found"
        fi
        
        if docker exec "$CONTAINER_NAME" test -d "/workspace/db/${db_name}/data"; then
            echo "✅ Data directory exists"
        else
            echo "⚠️  Data directory not found"
        fi
    else
        echo "❌ Root directory not found"
        PATH_ERRORS+=("$db_name: Root directory /workspace/db/${db_name} not found")
        ERRORS_FOUND=$((ERRORS_FOUND + 1))
    fi
    
    # Test Python recursive finding function exists in notebook
    echo "Testing recursive finding function in notebook..."
    if docker exec "$CONTAINER_NAME" grep -q "find_file_recursively" "/workspace/client/db/${db_name}/${deliverable}/${db_name}.ipynb" 2>/dev/null; then
        echo "✅ Recursive finding function found in notebook"
    else
        echo "⚠️  Recursive finding function not found in notebook (may be in different cell)"
    fi
    
    if [ $ERRORS_FOUND -eq 0 ]; then
        PATH_RESULTS["$db_name"]="SUCCESS"
        echo "✅ All file path tests passed for $db_name"
    else
        PATH_RESULTS["$db_name"]="FAILED"
        echo "❌ Some file path tests failed for $db_name"
    fi
done

# Generate summary
echo ""
echo "=================================================================================="
echo "FILE PATH TEST SUMMARY"
echo "=================================================================================="
echo "End time: $(date)"
echo ""

SUCCESS_COUNT=0
FAILED_COUNT=0

for db_name in "${DATABASES[@]}"; do
    if [ "${PATH_RESULTS[$db_name]}" = "SUCCESS" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "✅ $db_name: SUCCESS"
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "❌ $db_name: FAILED"
    fi
done

echo ""
echo "Total: $SUCCESS_COUNT successful, $FAILED_COUNT failed"

if [ ${#PATH_ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "ERRORS:"
    for error in "${PATH_ERRORS[@]}"; do
        echo "  ❌ $error"
    done
fi

echo ""
echo "=================================================================================="
if [ $FAILED_COUNT -eq 0 ]; then
    echo "✅ ALL FILE PATH TESTS PASSED"
    exit 0
else
    echo "❌ SOME FILE PATH TESTS FAILED"
    exit 1
fi
