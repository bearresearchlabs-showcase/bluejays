#!/bin/bash
# Validate database queries in containers

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
declare -A QUERY_RESULTS
QUERY_ERRORS=()

echo "=================================================================================="
echo "VALIDATING DATABASE QUERIES"
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

# Function to execute query and measure time
execute_query() {
    local container_name=$1
    local db_name=$2
    local query=$3
    
    START_TIME=$(date +%s%N)
    if docker exec "$container_name" su - postgres -c "psql -d $db_name -c \"$query\"" > /dev/null 2>&1; then
        END_TIME=$(date +%s%N)
        EXECUTION_TIME=$(( (END_TIME - START_TIME) / 1000000 ))  # Convert to milliseconds
        echo "$EXECUTION_TIME"
        return 0
    else
        echo "-1"
        return 1
    fi
}

# Test each container
for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    DB_NAME_LOWER=$(echo "$db_name" | tr '[:upper:]' '[:lower:]' | tr '-' '')
    
    echo ""
    echo "=================================================================================="
    echo "Validating queries for $db_name"
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
        QUERY_ERRORS+=("$db_name: PostgreSQL timeout")
        QUERY_RESULTS["$db_name"]="FAILED"
        continue
    fi
    echo "✅ PostgreSQL is ready"
    
    # Check if database exists
    echo "Checking if database exists..."
    if docker exec "$CONTAINER_NAME" su - postgres -c "psql -lqt" | cut -d \| -f 1 | grep -qw "$DB_NAME_LOWER"; then
        echo "✅ Database $DB_NAME_LOWER exists"
    else
        echo "⚠️  Database $DB_NAME_LOWER does not exist (may need to run notebook first)"
        QUERY_ERRORS+=("$db_name: Database $DB_NAME_LOWER does not exist")
        QUERY_RESULTS["$db_name"]="SKIPPED"
        continue
    fi
    
    # Check if tables exist
    echo "Checking if tables exist..."
    TABLE_COUNT=$(docker exec "$CONTAINER_NAME" su - postgres -c "psql -d $DB_NAME_LOWER -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';\"" | tr -d ' ')
    if [ -n "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -gt 0 ]; then
        echo "✅ Found $TABLE_COUNT tables"
    else
        echo "❌ No tables found in database"
        QUERY_ERRORS+=("$db_name: No tables found")
        QUERY_RESULTS["$db_name"]="FAILED"
        continue
    fi
    
    # Check if data exists
    echo "Checking if data exists..."
    # Get first table name
    FIRST_TABLE=$(docker exec "$CONTAINER_NAME" su - postgres -c "psql -d $DB_NAME_LOWER -t -c \"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 1;\"" | tr -d ' ')
    if [ -n "$FIRST_TABLE" ]; then
        ROW_COUNT=$(docker exec "$CONTAINER_NAME" su - postgres -c "psql -d $DB_NAME_LOWER -t -c \"SELECT COUNT(*) FROM $FIRST_TABLE;\"" | tr -d ' ')
        if [ -n "$ROW_COUNT" ] && [ "$ROW_COUNT" -gt 0 ]; then
            echo "✅ Found $ROW_COUNT rows in $FIRST_TABLE"
        else
            echo "⚠️  No data found in $FIRST_TABLE"
        fi
    fi
    
    # Load queries.json to get sample queries
    echo "Loading queries..."
    QUERIES_JSON_PATH="/workspace/db/${db_name}/queries/queries.json"
    if docker exec "$CONTAINER_NAME" test -f "$QUERIES_JSON_PATH"; then
        echo "✅ Found queries.json"
        
        # Extract first 5 queries using Python
        QUERIES=$(docker exec "$CONTAINER_NAME" python3 -c "
import json
import sys

try:
    with open('$QUERIES_JSON_PATH', 'r') as f:
        data = json.load(f)
        queries = data.get('queries', [])[:5]
        for q in queries:
            sql = q.get('sql', '').replace('\"', '\\\"').replace('\$', '\\\$')
            print(f\"{q.get('number', '')}|||{sql}\")
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null)
        
        if [ -n "$QUERIES" ]; then
            echo "Executing sample queries (first 5)..."
            QUERY_SUCCESS=0
            QUERY_FAILED=0
            TOTAL_QUERY_TIME=0
            
            while IFS= read -r query_line; do
                if [ -z "$query_line" ]; then
                    continue
                fi
                
                QUERY_NUM=$(echo "$query_line" | cut -d'|||' -f1)
                QUERY_SQL=$(echo "$query_line" | cut -d'|||' -f2-)
                
                if [ -z "$QUERY_SQL" ]; then
                    continue
                fi
                
                echo "  Executing Query $QUERY_NUM..."
                
                # Limit query to prevent long execution
                LIMITED_QUERY="SELECT * FROM ($QUERY_SQL) AS subquery LIMIT 10;"
                
                EXEC_TIME=$(execute_query "$CONTAINER_NAME" "$DB_NAME_LOWER" "$LIMITED_QUERY")
                
                if [ "$EXEC_TIME" != "-1" ]; then
                    QUERY_SUCCESS=$((QUERY_SUCCESS + 1))
                    TOTAL_QUERY_TIME=$((TOTAL_QUERY_TIME + EXEC_TIME))
                    
                    if [ $EXEC_TIME -gt 5000 ]; then
                        echo "    ⚠️  Query executed but took ${EXEC_TIME}ms (> 5s)"
                    else
                        echo "    ✅ Query executed successfully (${EXEC_TIME}ms)"
                    fi
                else
                    QUERY_FAILED=$((QUERY_FAILED + 1))
                    echo "    ❌ Query execution failed"
                    QUERY_ERRORS+=("$db_name: Query $QUERY_NUM execution failed")
                fi
            done <<< "$QUERIES"
            
            if [ $QUERY_SUCCESS -gt 0 ]; then
                AVG_TIME=$((TOTAL_QUERY_TIME / QUERY_SUCCESS))
                echo "  Query execution summary: $QUERY_SUCCESS succeeded, $QUERY_FAILED failed"
                echo "  Average execution time: ${AVG_TIME}ms"
                
                if [ $QUERY_FAILED -eq 0 ]; then
                    QUERY_RESULTS["$db_name"]="SUCCESS"
                else
                    QUERY_RESULTS["$db_name"]="PARTIAL"
                fi
            else
                QUERY_RESULTS["$db_name"]="FAILED"
            fi
        else
            echo "⚠️  Could not extract queries from queries.json"
            QUERY_ERRORS+=("$db_name: Could not extract queries")
            QUERY_RESULTS["$db_name"]="FAILED"
        fi
    else
        echo "⚠️  queries.json not found at $QUERIES_JSON_PATH"
        QUERY_ERRORS+=("$db_name: queries.json not found")
        QUERY_RESULTS["$db_name"]="SKIPPED"
    fi
done

# Generate summary
echo ""
echo "=================================================================================="
echo "QUERY VALIDATION SUMMARY"
echo "=================================================================================="
echo "End time: $(date)"
echo ""

SUCCESS_COUNT=0
FAILED_COUNT=0
PARTIAL_COUNT=0
SKIPPED_COUNT=0

for db_name in "${DATABASES[@]}"; do
    case "${QUERY_RESULTS[$db_name]}" in
        "SUCCESS")
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            echo "✅ $db_name: SUCCESS"
            ;;
        "PARTIAL")
            PARTIAL_COUNT=$((PARTIAL_COUNT + 1))
            echo "⚠️  $db_name: PARTIAL (some queries failed)"
            ;;
        "FAILED")
            FAILED_COUNT=$((FAILED_COUNT + 1))
            echo "❌ $db_name: FAILED"
            ;;
        "SKIPPED")
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            echo "⏭️  $db_name: SKIPPED"
            ;;
    esac
done

echo ""
echo "Total: $SUCCESS_COUNT successful, $PARTIAL_COUNT partial, $FAILED_COUNT failed, $SKIPPED_COUNT skipped"

if [ ${#QUERY_ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "ERRORS:"
    for error in "${QUERY_ERRORS[@]}"; do
        echo "  ❌ $error"
    done
fi

echo ""
echo "=================================================================================="
if [ $FAILED_COUNT -eq 0 ] && [ $SKIPPED_COUNT -eq 0 ]; then
    echo "✅ ALL QUERY VALIDATIONS PASSED"
    exit 0
else
    echo "⚠️  SOME QUERY VALIDATIONS FAILED OR WERE SKIPPED"
    exit 1
fi
