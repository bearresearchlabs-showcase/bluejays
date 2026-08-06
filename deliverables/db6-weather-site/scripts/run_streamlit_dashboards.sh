#!/bin/bash
# Run Streamlit dashboards in Docker containers

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

DATABASES=("db-6" "db-7" "db-8" "db-9" "db-10" "db-11" "db-12" "db-13" "db-14" "db-15")

# Streamlit port mapping function
get_streamlit_port() {
    local db_name=$1
    case "$db_name" in
        db-6) echo "8506" ;;
        db-7) echo "8507" ;;
        db-8) echo "8508" ;;
        db-9) echo "8509" ;;
        db-10) echo "8510" ;;
        db-11) echo "8511" ;;
        db-12) echo "8512" ;;
        db-13) echo "8513" ;;
        db-14) echo "8514" ;;
        db-15) echo "8515" ;;
        *) echo "8501" ;;
    esac
}

# Function to run a single dashboard
run_dashboard() {
    local db_name=$1
    local container_name="${db_name}-container"
    local streamlit_port=$(get_streamlit_port "$db_name")
    local dashboard_file="/workspace/docker/notebooks/${db_name}_dashboard.py"
    
    echo "=================================================================================="
    echo "Starting Streamlit Dashboard for ${db_name}"
    echo "=================================================================================="
    echo "  Container: ${container_name}"
    echo "  Dashboard: ${dashboard_file}"
    echo "  Streamlit Port: ${streamlit_port}"
    echo "  Access URL: http://localhost:${streamlit_port}"
    echo ""
    
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
    
    # Ensure dashboard file exists
    if ! docker exec "$container_name" test -f "$dashboard_file"; then
        echo "Copying dashboard to container..."
        docker cp "docker/notebooks/${db_name}_dashboard.py" "${container_name}:${dashboard_file}"
    fi
    
    # Ensure Streamlit is installed
    echo "Ensuring Streamlit is installed..."
    docker exec "$container_name" pip install streamlit plotly openpyxl > /dev/null 2>&1
    
    # Run Streamlit dashboard in background
    echo "Starting Streamlit dashboard..."
    docker exec -d "$container_name" streamlit run \
        "$dashboard_file" \
        --server.port=8501 \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --browser.gatherUsageStats=false \
        --server.enableCORS=false \
        --server.enableXsrfProtection=false
    
    echo "✅ Dashboard started at http://localhost:${streamlit_port}"
    echo ""
}

# Main execution
if [ $# -eq 0 ]; then
    # Run all dashboards
    echo "=================================================================================="
    echo "STARTING ALL STREAMLIT DASHBOARDS"
    echo "=================================================================================="
    echo ""
    
    for db_name in "${DATABASES[@]}"; do
        run_dashboard "$db_name"
    done
    
    echo "=================================================================================="
    echo "ALL DASHBOARDS STARTED"
    echo "=================================================================================="
    echo ""
    echo "Dashboard URLs:"
    for db_name in "${DATABASES[@]}"; do
        local port=$(get_streamlit_port "$db_name")
        echo "  ${db_name}: http://localhost:${port}"
    done
    echo ""
    echo "To stop all dashboards:"
    echo "  docker-compose -f docker/docker-compose.yml down"
    echo ""
    echo "To view logs:"
    echo "  docker logs db-6-container"
else
    # Run specific dashboard
    run_dashboard "$1"
fi
