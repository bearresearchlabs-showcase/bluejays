# Work Storage Microservices

Qdrant vector DB + Work API + Annotator webapp. Stores and serves databases from `source/`.

## Architecture

```
┌─────────────┐     ┌─────────────┐
│  work-api   │────▶│   qdrant     │
│  (FastAPI)  │     │  (vector DB) │
│  :8010      │     │  :6333       │
└──────┬──────┘     └─────────────┘
       │
       │ ingest (POST /ingest)
       ▼
┌─────────────┐
│  annotator  │  ← source/, template/ (read/write)
│  :8766      │
└─────────────┘
```

## Quick Start (all connected)

```bash
# From repo root

# 1. Start PostgreSQL (db-1..db-16 on ports 5436-5451)
# Prefer hardened: security_opt: no-new-privileges, alpine base
docker compose -f docker/docker-compose.hardened.yml up -d
# Or: docker compose -f docker/docker-compose.multi-db.yml up -d
sleep 10

# 2. Start work microservices (Qdrant + Work API + Annotator)
# All services use security_opt: no-new-privileges
docker compose -f docker/docker-compose.work-microservices.yml up -d

# Work API
curl http://localhost:8010/health

# Ingest databases from source/ into Qdrant
curl -X POST http://localhost:8010/ingest

# Check ingest status
curl http://localhost:8010/ingest/status

# Annotator webapp (all databases from source/)
open http://localhost:8768/annotate

# Store work
curl -X POST http://localhost:8010/work \
  -H "Content-Type: application/json" \
  -d '{"kind":"annotation","source":"db-1","content":{"text":"..."},"text":"..."}'

# Search
curl -X POST http://localhost:8010/search \
  -H "Content-Type: application/json" \
  -d '{"query":"cardiac conditions","limit":5}'
```

## Endpoints

| Service   | URL                    | Description                    |
|-----------|------------------------|--------------------------------|
| Work API  | http://localhost:8010  | Health, work, search, ingest   |
| Qdrant    | http://localhost:6333  | Vector DB REST                 |
| Annotator | http://localhost:8768/annotate | SQL annotation UI        |

## Qdrant Dashboard

http://localhost:6333/dashboard

## Local Query Execution (Run query)

The annotator can execute SQL against local PostgreSQL to populate **Expected output** for documentation:

1. **Start PostgreSQL** with schema and data for each db-N:
   ```bash
   # Option A: Single instance with db1..db16 databases
   # Create databases and load source/db-N/app/DATABASE/schema.sql + data.sql

   # Option B: Hardened multi-container (ports 5436-5451)
   docker compose -f docker/docker-compose.hardened.yml up -d
   export PG_BASE_PORT=5436
   ```

2. **Run annotator** with PG env vars:
   ```bash
   # Local PostgreSQL (default: uses $USER if PG_USER not set)
   python3 scripts/annotator_app.py --port 8766

   # Or explicit: PG_HOST=localhost PG_PORT=5432 PG_USER=postgres PG_PASSWORD=postgres
   # Multi-container: PG_BASE_PORT=5436 (db-1→5436, db-2→5437, ...)
   ```

3. In the form: load a query, click **Validate SQL** (pass/fail against live DB), **Run query**, then **Use as expected output** to document the result.

## Admin Task Board (30 independent submissions)

Open `/admin` to view all 30 queries as independent task cards:

- **URL**: `http://localhost:8768/admin` (or your annotator port)
- **Flow**: Admin → select database → 30 task cards load automatically
- **Task grid**: Each card shows Query N, status badges, preview, **Open** button
- **Filters**: Task Status, Audit Status (Scale-style)
- **Progress**: X / 30 completed bar

## Scale AI Staff Workflow (Task Fix)

Replicate Scale AI staff task-fixing (Accept / Fix / Reject):

```bash
# Start annotator
python scripts/annotator_app.py --port 8766

# Run Scale fix workflow (API-based)
python scripts/scale_staff_fix_workflow.py --port 8766 --source db-1 --question-id 1
```

Methodology (scale.com/docs/pro-or-tasks-tab):
- **Accept**: quality standards met
- **Fix**: make immediate correction, set `audit_status=Fixed`
- **Reject**: quality standards not met

The script: loads task → POST /api/annotate with `audit_status=Fixed` → verifies persistence.

## Optional: Semantic Embeddings

Add `sentence-transformers` to `workbench/work_api/requirements.txt` for real semantic search:

```
sentence-transformers>=2.2.0
```

Rebuild: `docker compose -f docker/docker-compose.work-microservices.yml build work-api`
