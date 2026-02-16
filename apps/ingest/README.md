# Ingest

**Ingests `source/` and converts to `client/`.**

The ingest program is the software that:

1. **Reads** from `source/` (and `template/`) at repo root
2. **Transforms** via the web UI (annotator, staff, customer) and pipeline scripts (populate, format, resync)
3. **Writes** to `client/db/` for delivery

## Structure

```
source/          # INPUT (at repo root)
template/        # INPUT (at repo root)
client/          # OUTPUT (at repo root)
apps/ingest/     # THIS PROGRAM
  app/           # Next.js app
  components/
  lib/
  __tests__/
  e2e/
scripts/         # Pipeline (at repo root): populate, format, resync
```

## Commands

- `npm run dev` / `npm run dev:test` — Start web app (port 3006 / 3007)
- `npm run build` — Build for production
- `npm run test` — Jest (unit, integration, quality)
- `npm run test:e2e` — Playwright E2E (starts dev server on 3007 automatically)
- `npm run test:app` — Full app test (start server, integration + E2E)

## E2E tests

From repo root or `apps/ingest`:

```bash
cd apps/ingest && npm run test:e2e
```

Playwright starts the dev server on port 3007 automatically; no second terminal needed.

## Pipeline (source → client)

Run from repo root:

```bash
/QA db-1 db-5    # Populate → Format → Resync → Audit → Compliance → Integrity
```

Or manually:

```bash
python3 scripts/populate_app_trifecta.py db-1
python3 scripts/format.py db-1
python3 scripts/resync_client_db.py --dbs 1
```
