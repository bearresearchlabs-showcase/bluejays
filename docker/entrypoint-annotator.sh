#!/bin/sh
# Entrypoint: queries.md → queries.json → Qdrant → serve annotator
# Ensures full pipeline runs before webapp starts.

set -e
cd /app

echo "[1/3] Extracting queries.md → queries.json..."
python -u scripts/extract_queries_to_json.py -a || true

echo "[2/3] Syncing to Qdrant via work-api..."
WORK_API="${WORK_API_URL:-http://work-api:8000}"
for i in 1 2 3 4 5 6 7 8 9 10; do
  if python -c "
import urllib.request
try:
  r = urllib.request.urlopen('${WORK_API}/health', timeout=5)
  exit(0 if r.status == 200 else 1)
except Exception as e:
  print('Waiting for work-api...', e)
  exit(1)
" 2>/dev/null; then
    python -c "
import urllib.request, json
req = urllib.request.Request('${WORK_API}/ingest', method='POST', headers={'Content-Type':'application/json'})
try:
  r = urllib.request.urlopen(req, timeout=120)
  d = json.loads(r.read().decode())
  print('Ingested:', d.get('ingested', 0), 'queries from', d.get('sources', []))
except Exception as e:
  print('Ingest warning:', e)
" 2>/dev/null || true
    break
  fi
  sleep 2
done

echo "[3/3] Starting annotator webapp..."
exec python -u scripts/annotator_app.py --port 8766 --host 0.0.0.0
