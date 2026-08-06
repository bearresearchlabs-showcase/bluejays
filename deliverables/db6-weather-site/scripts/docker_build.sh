#!/bin/bash
# Build Docker containers for all databases

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

echo "=================================================================================="
echo "BUILDING DOCKER CONTAINERS FOR ALL DATABASES"
echo "=================================================================================="

# Build all containers
for db in db-{6..15}; do
    echo ""
    echo "Building $db..."
    docker build -f docker/Dockerfile.$db -t $db:latest .
    echo "✅ $db built successfully"
done

echo ""
echo "=================================================================================="
echo "All containers built successfully!"
echo "=================================================================================="
