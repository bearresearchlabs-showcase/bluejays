# Docker Setup for Database Notebooks

This directory contains Docker configuration files for running database notebooks in isolated containers.

## Structure

- `Dockerfile.template` - Template for generating database-specific Dockerfiles
- `Dockerfile.db-*` - Generated Dockerfiles for each database (db-6 through db-15)
- `docker-compose.yml` - Orchestration file for all containers
- `entrypoint.sh` - Container entrypoint script that starts PostgreSQL
- `run_notebook.sh` - Script to run a single notebook in a container

## Prerequisites

- Docker installed and running
- Docker Compose installed
- Sufficient disk space (each container is ~1-2GB)

## Quick Start

### Build All Containers

```bash
# Build all containers
./scripts/docker_build_all.sh

# Or build individually
docker build -f docker/Dockerfile.db-6 -t db-6:latest .
```

### Start All Containers

```bash
# Start all containers using docker-compose
./scripts/docker_run_all.sh

# Or start individually
docker-compose -f docker/docker-compose.yml up -d db-6
```

### Execute Notebooks

```bash
# Execute all notebooks
./scripts/docker_execute_notebooks.sh

# Or execute a single notebook
docker exec db-6-container jupyter nbconvert --to notebook --execute \
  /workspace/client/db/db-6/db6-weather-consulting-insurance/db-6.ipynb \
  --output db-6_executed.ipynb
```

## Container Details

Each container includes:

- **Python 3.14** with all required packages pre-installed:
  - psycopg2-binary
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - jupyter
  - ipykernel

- **PostgreSQL** server running locally
- **Jupyter Notebook** server accessible via web interface
- **Pre-mounted volumes**:
  - `/workspace/client/db/{db-N}` - Client database files (read-only)
  - `/workspace/db/{db-N}` - Root database files (read-only)

## Ports

Each container exposes:

- **Jupyter Notebook**: Port 8888 (mapped to unique host ports 8886-8895)
- **PostgreSQL**: Port 5432 (mapped to unique host ports 5436-5445)

### Port Mapping

| Database | Jupyter Port | PostgreSQL Port |
|----------|--------------|-----------------|
| db-6     | 8886         | 5436            |
| db-7     | 8887         | 5437            |
| db-8     | 8888         | 5438            |
| db-9     | 8889         | 5439            |
| db-10    | 8890         | 5440            |
| db-11    | 8891         | 5441            |
| db-12    | 8892         | 5442            |
| db-13    | 8893         | 5443            |
| db-14    | 8894         | 5444            |
| db-15    | 8895         | 5445            |

## Accessing Jupyter Notebooks

Once containers are running, access Jupyter Notebooks at:

- db-6: http://localhost:8886
- db-7: http://localhost:8887
- db-8: http://localhost:8888
- ... and so on

**Note**: Jupyter is configured with no password/token for simplicity. In production, add authentication.

## Connecting to PostgreSQL

From host machine:

```bash
# Connect to db-6 PostgreSQL
psql -h localhost -p 5436 -U postgres -d postgres

# Password: postgres
```

From within container:

```bash
# Connect to PostgreSQL
docker exec -it db-6-container psql -U postgres -d postgres
```

## Environment Variables

Each container sets:

- `PG_HOST=localhost`
- `PG_PORT=5432`
- `PG_USER=postgres`
- `PG_PASSWORD=postgres`
- `DB_NAME=db{N}` (e.g., db6, db7, etc.)

## Managing Containers

### View Running Containers

```bash
docker-compose -f docker/docker-compose.yml ps
```

### View Logs

```bash
# All containers
docker-compose -f docker/docker-compose.yml logs -f

# Specific container
docker-compose -f docker/docker-compose.yml logs -f db-6
```

### Stop Containers

```bash
# Stop all
docker-compose -f docker/docker-compose.yml down

# Stop specific container
docker-compose -f docker/docker-compose.yml stop db-6
```

### Remove Containers and Volumes

```bash
# Remove containers and volumes
docker-compose -f docker/docker-compose.yml down -v
```

## Troubleshooting

### PostgreSQL Not Starting

If PostgreSQL fails to start:

```bash
# Check logs
docker logs db-6-container

# Restart container
docker-compose -f docker/docker-compose.yml restart db-6
```

### Notebook Execution Fails

If notebook execution fails:

1. Check container logs: `docker logs db-6-container`
2. Verify PostgreSQL is running: `docker exec db-6-container psql -U postgres -c "SELECT 1"`
3. Check file paths: `docker exec db-6-container ls -la /workspace/client/db/db-6/`

### Port Conflicts

If ports are already in use:

1. Stop conflicting services
2. Or modify port mappings in `docker-compose.yml`

## Building Individual Containers

To build a single container:

```bash
docker build -f docker/Dockerfile.db-6 -t db-6:latest .
docker run -d \
  --name db-6-container \
  -p 8886:8888 \
  -p 5436:5432 \
  -v $(pwd)/client/db/db-6:/workspace/client/db/db-6:ro \
  -v $(pwd)/db-6:/workspace/db/db-6:ro \
  db-6:latest
```

## Notes

- Containers use read-only volumes for database files
- PostgreSQL data is persisted in Docker volumes
- Each container is isolated with its own PostgreSQL instance
- Notebooks can find files recursively from `/workspace/client/db` root
