#!/bin/bash
# Run Docker containers using docker-compose

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

echo "=================================================================================="
echo "STARTING DOCKER CONTAINERS FOR ALL DATABASES"
echo "=================================================================================="

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose not found. Using 'docker compose' instead..."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Start all containers
cd docker
$DOCKER_COMPOSE up -d

echo ""
echo "=================================================================================="
echo "Containers started!"
echo ""
echo "Jupyter Notebook URLs:"
echo "  db-6:  http://localhost:8886"
echo "  db-7:  http://localhost:8887"
echo "  db-8:  http://localhost:8888"
echo "  db-9:  http://localhost:8889"
echo "  db-10: http://localhost:8890"
echo "  db-11: http://localhost:8891"
echo "  db-12: http://localhost:8892"
echo "  db-13: http://localhost:8893"
echo "  db-14: http://localhost:8894"
echo "  db-15: http://localhost:8895"
echo ""
echo "PostgreSQL Ports:"
echo "  db-6:  localhost:5436"
echo "  db-7:  localhost:5437"
echo "  db-8:  localhost:5438"
echo "  db-9:  localhost:5439"
echo "  db-10: localhost:5440"
echo "  db-11: localhost:5441"
echo "  db-12: localhost:5442"
echo "  db-13: localhost:5443"
echo "  db-14: localhost:5444"
echo "  db-15: localhost:5445"
echo ""
echo "To stop containers: cd docker && $DOCKER_COMPOSE down"
echo "To view logs: cd docker && $DOCKER_COMPOSE logs -f"
echo "=================================================================================="
