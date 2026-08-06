#!/bin/bash
# Run all Docker containers using docker-compose

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

echo "=================================================================================="
echo "STARTING ALL DOCKER CONTAINERS"
echo "=================================================================================="

# Build and start all containers
docker-compose -f docker/docker-compose.yml up -d --build

echo ""
echo "=================================================================================="
echo "All containers started!"
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
echo "  db-6:  5436"
echo "  db-7:  5437"
echo "  db-8:  5438"
echo "  db-9:  5439"
echo "  db-10: 5440"
echo "  db-11: 5441"
echo "  db-12: 5442"
echo "  db-13: 5443"
echo "  db-14: 5444"
echo "  db-15: 5445"
echo ""
echo "To stop all containers: docker-compose -f docker/docker-compose.yml down"
echo "To view logs: docker-compose -f docker/docker-compose.yml logs -f"
echo "=================================================================================="
