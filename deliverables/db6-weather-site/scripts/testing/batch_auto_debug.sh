#!/bin/bash
# Batch automated debugging script - processes multiple databases in parallel

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/automated_query_debugger.py"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Batch Automated Query Debugger"
echo "=========================================="
echo ""

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Error: $PYTHON_SCRIPT not found${NC}"
    exit 1
fi

# Make script executable
chmod +x "$PYTHON_SCRIPT"

# Function to debug a single database
debug_db() {
    local db_num=$1
    local queries=$2

    echo -e "${YELLOW}[db-${db_num}] Starting automated debugging...${NC}"

    if [ -n "$queries" ]; then
        python3 "$PYTHON_SCRIPT" --db "$db_num" --queries "$queries"
    else
        python3 "$PYTHON_SCRIPT" --db "$db_num"
    fi

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}[db-${db_num}] Completed${NC}"
    else
        echo -e "${RED}[db-${db_num}] Failed with exit code $exit_code${NC}"
    fi

    return $exit_code
}

# Parse arguments
DB_LIST=""
QUERY_LIST=""
PARALLEL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dbs)
            DB_LIST="$2"
            shift 2
            ;;
        --queries)
            QUERY_LIST="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--dbs 1,2,3] [--queries 1,2,3] [--parallel]"
            echo ""
            echo "Options:"
            echo "  --dbs       Comma-separated list of database numbers (default: all 1-5)"
            echo "  --queries   Comma-separated list of query numbers (applies to all DBs)"
            echo "  --parallel  Run databases in parallel (default: sequential)"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Default to all databases if not specified
if [ -z "$DB_LIST" ]; then
    DB_LIST="1,2,3,4,5"
fi

# Convert comma-separated list to array
IFS=',' read -ra DB_ARRAY <<< "$DB_LIST"

echo "Databases to debug: ${DB_ARRAY[@]}"
if [ -n "$QUERY_LIST" ]; then
    echo "Query numbers: $QUERY_LIST"
fi
echo ""

# Run debugging
if [ "$PARALLEL" = true ]; then
    echo -e "${YELLOW}Running in parallel mode...${NC}"
    PIDS=()

    for db_num in "${DB_ARRAY[@]}"; do
        debug_db "$db_num" "$QUERY_LIST" &
        PIDS+=($!)
    done

    # Wait for all processes
    FAILED=0
    for pid in "${PIDS[@]}"; do
        if ! wait $pid; then
            FAILED=$((FAILED + 1))
        fi
    done

    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}Some databases failed (${FAILED} failed)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Running in sequential mode...${NC}"
    FAILED=0

    for db_num in "${DB_ARRAY[@]}"; do
        if ! debug_db "$db_num" "$QUERY_LIST"; then
            FAILED=$((FAILED + 1))
        fi
        echo ""  # Blank line between databases
    done

    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}Some databases failed (${FAILED} failed)${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Batch debugging complete!"
echo "==========================================${NC}"
