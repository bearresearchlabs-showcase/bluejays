# Vercel Deployment — Data Annotation App

## db-red-three.vercel.app

This project deploys the **SQL Annotator** (data annotation app) from the repo root.

### Pre-deploy checklist

1. **Regenerate and commit the manifest** (required for sources + queries to work):
   ```bash
   node scripts/generate-sources-manifest.js
   git add lib/sources-manifest.json
   git commit -m "chore: update sources manifest for Vercel"
   ```
2. Set `JWT_SECRET` in Vercel project settings.
3. Root Directory: empty or `.`

### Root Directory

**Must be empty or `.`** The annotator app is at the repo root (`app/`, `lib/`, `components/`). If Root Directory was previously set to `apps/annotator`, clear it (Settings → General → Root Directory → clear and Save).

### Environment variables (recommended)

| Variable | Purpose |
|----------|---------|
| `JWT_SECRET` | Secret for session cookies (set a random string in production) |

### Verification (post-deploy)

```bash
# 1. Login (form POST)
curl -c cookies.txt -X POST https://YOUR_PROJECT.vercel.app/api/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user=staff&password=123123&stay=1" -L -o /dev/null

# 2. Sources (requires session cookie) — should return template + db-1..db-16
curl -b cookies.txt https://YOUR_PROJECT.vercel.app/api/sources

# 3. Queries (requires session cookie)
curl -b cookies.txt "https://YOUR_PROJECT.vercel.app/api/queries?source=db-1"
```

**Sources manifest**: Build runs `scripts/generate-sources-manifest.js` before `next build` to create `lib/sources-manifest.json` with sources + embedded queries. The manifest is statically imported in `lib/data.ts`, so it is bundled and works on Vercel even when `source/` is absent at runtime. If the build finds `source/`, it regenerates the manifest.

### Routes

- `/login` — Login (staff/123123, annotator/123123, customer/123123)
- `/` — Annotator
- `/dashboard` — Dashboard
- `/admin/tasks` — Task Board
- `/suite` — Full Suite
- `/customer` — Customer Portal

### PostgreSQL + pgvector

Add **Neon** or **Supabase** integration for `POSTGRES_URL`. See below.

### Load all databases into Neon

After adding Neon, load db-1 through db-16:

```bash
# Set POSTGRES_URL from Vercel/Neon (or .env)
export POSTGRES_URL="postgresql://user:pass@host/neondb?sslmode=require"
python scripts/load_all_to_vercel_postgres.py
```

Creates databases `db1`–`db16` in Neon. For db-5, db-10, db-14 the script applies fixes for malformed source data; db-10 and db-14 use deliverable data when available.

---

## 100% Database Documentation Deploy (Static Site)

To deploy **all 16 databases** (db-1 through db-16) as a static documentation site with full schema + data coverage:

```bash
# 1. Validate all databases (must pass 100%)
python3 scripts/db_check.py validate 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16

# 2. Deploy static site (prepares public/, embeds schema + small data, links large data to GitHub)
./scripts/deploy_websites.sh --static
```

**What gets deployed:**
- **HTML docs** — All 16 db-N_documentation.html
- **JSON deliverables** — All 16 db-N_deliverable.json
- **Schema** — schema.sql or schema_postgresql.sql for each db
- **Data** — data.sql embedded if &lt;50MB; otherwise `data/downloads.json` with GitHub raw URL

**CDN / large-file strategy:** Files over 50MB get a `downloads.json` with `data_sql` URL pointing to `https://raw.githubusercontent.com/ORG/REPO/BRANCH/...`. Push to GitHub first for working links. Or set `GITHUB_RAW_BASE` env var.

**Prepare script:** `scripts/prepare_vercel_public.sh` — run manually or via `deploy_websites.sh --static`.

---

## PostgreSQL and Vector Databases

Vercel does not host databases. Use **Marketplace integrations** to connect PostgreSQL and vector databases.

### Option 1: Neon (PostgreSQL + pgvector)

**Via CLI** (opens browser for terms):
```bash
cd /path/to/db
vercel integration add neon
# Answer Y to link to project, Y to open dashboard if terms needed
```

**Via Dashboard**:
1. Open [Neon on Vercel Marketplace](https://vercel.com/integrations/neon)
2. Click **Add Integration** → select project **db**
3. Create/link Neon database – injects `POSTGRES_URL`
4. **Enable pgvector** in Neon: SQL Editor → `CREATE EXTENSION IF NOT EXISTS vector;` (similarity search)

### Option 2: Supabase (PostgreSQL + pgvector)

1. **Vercel Dashboard** → Project → **Integrations** → **Browse Marketplace**
2. Search for **Supabase** and install
3. Connect – Supabase injects `NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
4. **Enable pgvector** in Supabase: Dashboard → Database → Extensions → enable `vector`
5. Use for relational data, auth, and vector embeddings

### Environment variables (after integration)

| Variable | Source | Purpose |
|----------|--------|---------|
| `POSTGRES_URL` or `DATABASE_URL` | Neon / Supabase | PostgreSQL connection string |
| `POSTGRES_PRISMA_URL` | Neon | Prisma-compatible URL (if using Prisma) |
| `POSTGRES_URL_NON_POOLING` | Neon | Direct connection (migrations) |

### Loading all SQL databases (db-1 through db-16)

After adding Neon, load all database schemas and sample data into PostgreSQL:

```bash
# Set connection URL (or add to .env)
export POSTGRES_URL="postgresql://..."   # from Vercel env or Neon dashboard
# Neon recommends POSTGRES_URL_NON_POOLING for migrations
export POSTGRES_URL_NON_POOLING="postgresql://..."

# Install dependency (use project venv if available)
pip install psycopg2-binary

# Load all 16 databases (creates db1, db2, ... db16)
python scripts/load_all_to_vercel_postgres.py

# Load specific databases only
python scripts/load_all_to_vercel_postgres.py 1 2 3 6
```

The script:
- Creates separate databases `db1`, `db2`, … `db16` in your Neon project
- Loads schema from `source/db-N/data/` (prefers `schema_postgresql.sql` when present)
- Loads sample data from `data.sql`
- Enables PostGIS for db-6 (weather/geospatial)

### Vector search (pgvector)

```sql
-- Enable extension (run once)
CREATE EXTENSION IF NOT EXISTS vector;

-- Example: embeddings table
CREATE TABLE embeddings (
  id SERIAL PRIMARY KEY,
  content TEXT,
  embedding vector(384)  -- match your model dimension
);

-- Similarity search (cosine distance)
SELECT * FROM embeddings
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

### Microservices (Docker, hardened images)

Backend microservices run on Docker with `security_opt: no-new-privileges:true` and non-root users. The Next.js annotator deploys to Vercel; these backends run on your own infrastructure.

**Hardening applied:**
- `security_opt: no-new-privileges:true` on all services
- Non-root users (appuser) in Python images
- Pinned base image versions (qdrant:v1.11.4, postgis:15-3.4-alpine)
- Read-only volume mounts where possible (`:ro` for source/template)

```bash
# Sources API (standalone) — port 8011
docker compose -f docker/docker-compose.sources-api.yml up -d
curl http://localhost:8011/health
curl http://localhost:8011/sources
curl "http://localhost:8011/queries?source=db-1"

# Full stack (Qdrant + Work API + Annotator Python)
docker compose -f docker/docker-compose.work-microservices.yml up -d

# All microservices (sources-api + work + qdrant + annotator-python)
docker compose -f docker/docker-compose.microservices.yml up -d
```

**To point the Next.js app at Sources API instead of built-in lib/data.ts:** set `SOURCES_API_URL` env var (e.g. `http://sources-api:8000` when running behind a proxy).

### Iterative test suite

```bash
# Next.js build (if ENOENT on _not-found: remove outputFileTracingRoot, limit includes to /api/**)
rm -rf .next && npm run build

# Unit + integration tests
python -m pytest tests/test_annotator_app.py tests/test_label_studio.py tests/test_sources_api.py -v

# Export CLI
python scripts/db_check.py export db-1 -o /tmp/out.csv
python scripts/db_check.py label-studio template --gates

# Microservices
bash scripts/test_microservices.sh sources-api
```

### Next.js / API usage

```ts
// lib/db.ts
import { Pool } from 'pg'

const pool = process.env.POSTGRES_URL
  ? new Pool({ connectionString: process.env.POSTGRES_URL })
  : null

export async function query<T>(sql: string, params?: unknown[]): Promise<T[]> {
  if (!pool) throw new Error('POSTGRES_URL not set')
  const { rows } = await pool.query(sql, params)
  return rows as T[]
}
```
