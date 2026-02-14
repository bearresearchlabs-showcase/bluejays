# Sources API Microservice

Smallest feature: discover database sources and load queries. Pipeline: **Unit → Integration → UAT → Docker**.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/sources` | List discovered sources (template, db-1, db-2, …) |
| GET | `/queries?source=db-1` | Load queries for a source |

## Run locally

```bash
# From repo root
uvicorn apps.sources_api.main:app --reload --port 8011
# Or: cd apps/sources_api && uvicorn main:app --reload --port 8011
```

## Tests (Unit → Integration → UAT)

```bash
# Requires: pip install fastapi uvicorn (or use project venv with deps)
pytest tests/test_sources_api.py -v
```

- **Unit**: `discover_sources()`, `load_queries()` in `data.py` (no server)
- **Integration**: FastAPI TestClient for `/health`, `/sources`, `/queries`
- **UAT**: End-to-end flow: get sources → pick one → load queries

## Docker

```bash
docker compose -f docker/docker-compose.sources-api.yml up -d
curl http://localhost:8011/health
curl http://localhost:8011/sources
```

## Iterative test script

```bash
./scripts/test_sources_api_docker.sh
```

Runs pytest, then builds and runs the Docker container, then smoke-tests the API.
