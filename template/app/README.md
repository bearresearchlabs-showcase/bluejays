# Template Reference App

Consumes `template/queries.json` and `template/queries.md` as the canonical reference.

## Serve locally

```bash
# From repo root — serve template/ so queries.json is at /queries.json
cd template && python3 -m http.server 8765

# Open http://localhost:8765/app/
```

Or use any static server with `template/` as document root. The app loads `queries.json` from the parent of `app/`.

## Label Studio (optional)

For human review/annotation of queries, use [Label Studio](https://labelstud.io/guide/quick_start).

**Bypass API key** (pre-set default user, no manual token copy):

```bash
# Start with pre-set token (from repo root)
docker compose -f docker/docker-compose.label-studio.yml up -d
export LABEL_STUDIO_USER_TOKEN=workbench-dev-token
python3 scripts/db_check.py label-studio template --multi-session
```

**Annotator app** (standalone UI, multiple hosts/ports):

```bash
# /annotate command: db_check annotate [--port 8766]
# Serves at http://localhost:8766/ and http://localhost:8766/annotate

# queries.json mode (no Label Studio): Load/save directly from queries.md structure
python3 scripts/db_check.py annotate --port 8766

# Label Studio mode (requires LS running)
LABEL_STUDIO_URL=http://localhost:8081 LABEL_STUDIO_USER_TOKEN=workbench-dev-token python3 scripts/annotator_app.py --port 8766

# Multiple annotators on one host (different ports)
python3 scripts/annotator_app.py --port 8766 &
python3 scripts/annotator_app.py --port 8767 &
python3 scripts/annotator_app.py --port 8768 &
```

**Intake form** fields match queries.md: question, SQL, evidence, difficulty, query_category, tables_used, expected_output. **Backend** is queries.json.

**Manual setup** (pip or Docker):

```bash
pip install label-studio
label-studio start   # http://localhost:8080
python3 scripts/export_queries_to_label_studio.py template > tasks.json
# Create project → Labeling Setup → paste template/label_studio_config.xml
# Data Import → Upload tasks.json
# Account & Settings → copy API key → export LABEL_STUDIO_API_KEY=...
```

## Structure

- `index.html` — Single-page app: field definitions, query browser
- Serves as reference for consuming the template format
