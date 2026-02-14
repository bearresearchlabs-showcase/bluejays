# Vercel Deployment Guide

## db-red-three.vercel.app (Static Site)

This repo deploys as a **static site** from the **repo root** by default.

### What was fixed (404 resolution)

1. **`public/index.html`** – Vercel serves static files from `public/` for "Other" framework projects. The main page is now in `public/index.html`.

2. **`framework: null`** – Explicitly sets the project as "Other" (static HTML) so Vercel does not auto-detect a framework.

3. **Build step** – `scripts/prepare_vercel_public.sh` copies db deliverable HTML/JSON from `db-N/deliverable/` into `public/db-N/` before deploy. Vercel prioritizes `public/` for static sites.

### Vercel project settings

- **Root Directory**: Leave empty (deploy from repo root)
- **Framework Preset**: Other (or let `vercel.json` override)
- **Build Command**: `bash scripts/prepare_vercel_public.sh` (copies db docs to public/)
- **Output Directory**: `public`

### After pushing

1. Push these changes to your connected branch.
2. Vercel will redeploy.
3. `https://db-red-three.vercel.app/` should serve the Database Documentation page.
4. `/db-6`, `/db-7`, etc. should serve the database docs.

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

---

## Next.js Annotator App (optional)

To deploy the **Next.js annotator app** instead:

1. In Vercel: **Project Settings → General → Root Directory**
2. Set to: `apps/annotator`
3. Add **Neon** or **Supabase** integration for PostgreSQL + pgvector
4. Redeploy.

The annotator app has its own `vercel.json` and will build as a Next.js project.
