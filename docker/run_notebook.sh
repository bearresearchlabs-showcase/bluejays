#!/bin/bash
# Script to run a notebook in a Docker container

set -e

DB_NAME=$1
NOTEBOOK_PATH=$2

if [ -z "$DB_NAME" ] || [ -z "$NOTEBOOK_PATH" ]; then
    echo "Usage: $0 <db-name> <notebook-path>"
    echo "Example: $0 db-6 /workspace/client/db/db-6/db6-weather-consulting-insurance/db-6.ipynb"
    exit 1
fi

CONTAINER_NAME="${DB_NAME}-container"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "Container $CONTAINER_NAME is not running. Starting it..."
    docker-compose -f docker/docker-compose.yml up -d "$DB_NAME"
    sleep 5
fi

# Execute notebook using nbconvert
echo "Executing notebook $NOTEBOOK_PATH in container $CONTAINER_NAME..."
docker exec "$CONTAINER_NAME" jupyter nbconvert --to notebook --execute "$NOTEBOOK_PATH" --output executed.ipynb

echo "Notebook execution complete!"
