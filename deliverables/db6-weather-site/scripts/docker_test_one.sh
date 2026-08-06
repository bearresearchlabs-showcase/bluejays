#!/bin/bash
# Test Docker setup with one database (db-6)

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

DB_NAME="db-6"
CONTAINER_NAME="${DB_NAME}-container"

echo "=================================================================================="
echo "TESTING DOCKER SETUP FOR $DB_NAME"
echo "=================================================================================="

# Build container
echo ""
echo "Building container..."
docker build -f "docker/Dockerfile.$DB_NAME" -t "$DB_NAME:latest" .

# Stop and remove existing container if it exists
echo ""
echo "Cleaning up existing container..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Start container
echo ""
echo "Starting container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    -p 8886:8888 \
    -p 5436:5432 \
    -v "$BASE_DIR/client/db/$DB_NAME:/workspace/client/db/$DB_NAME:ro" \
    -v "$BASE_DIR/$DB_NAME:/workspace/db/$DB_NAME:ro" \
    "$DB_NAME:latest"

# Wait for container to be ready
echo ""
echo "Waiting for container to be ready..."
sleep 10

# Check if PostgreSQL is running
echo ""
echo "Checking PostgreSQL..."
for i in {1..30}; do
    if docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'SELECT 1'" > /dev/null 2>&1; then
        echo "✅ PostgreSQL is running!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 1
done

# Check if Jupyter is running
echo ""
echo "Checking Jupyter..."
if docker exec "$CONTAINER_NAME" pgrep -f jupyter > /dev/null; then
    echo "✅ Jupyter is running!"
else
    echo "⚠️  Jupyter may not be running"
fi

# Test notebook path
echo ""
echo "Checking notebook path..."
NOTEBOOK_PATH="/workspace/client/db/$DB_NAME/db6-weather-consulting-insurance/$DB_NAME.ipynb"
if docker exec "$CONTAINER_NAME" test -f "$NOTEBOOK_PATH"; then
    echo "✅ Notebook found at: $NOTEBOOK_PATH"
else
    echo "⚠️  Notebook not found at: $NOTEBOOK_PATH"
    echo "Available files:"
    docker exec "$CONTAINER_NAME" ls -la "/workspace/client/db/$DB_NAME/" || true
fi

# Display container info
echo ""
echo "=================================================================================="
echo "Container Status:"
echo "=================================================================================="
docker ps | grep "$CONTAINER_NAME" || echo "Container not running"

echo ""
echo "Jupyter Notebook: http://localhost:8886"
echo "PostgreSQL: localhost:5436"
echo ""
echo "To view logs: docker logs $CONTAINER_NAME"
echo "To stop: docker stop $CONTAINER_NAME"
echo "To remove: docker rm $CONTAINER_NAME"
echo "=================================================================================="
