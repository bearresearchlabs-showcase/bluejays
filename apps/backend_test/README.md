# DB Backend Test (MVC)

Lightweight FastAPI app for testing DB connectivity and BIRD benchmark integration.

## Requirements

- `PG_HOST`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE` in `.env` or `client/.env`
- `DB_PORTS_START` (default 5436) for per-db ports (db-1=5436, db-2=5437, ...)

See root `.env.example`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/db/{n}` | Check db-n connectivity (n=1..16) |
| GET | `/health/all` | Check all 16 DBs |
| POST | `/query` | Execute SQL. Body: `{"db_id": "db-1", "sql": "SELECT ..."}` |
| POST | `/benchmark` | Run queries. Body: `{"db_id": "db-1", "query_ids": [1,2,3]}` |
| GET | `/bird/export?db_id=db-1` | BIRD-formatted export (run bird_export.py first) |
| POST | `/bird/validate` | Validate BIRD schema. Body: `{"db_id": "db-1"}` |

## Run

```bash
cd apps/backend_test
uvicorn main:app --reload --port 8000
```

Or from repo root:

```bash
uvicorn apps.backend_test.main:app --reload --port 8000
```

## Smoke Test

```bash
python3 scripts/mvc_backend_test.py
```
