# Vercel Deployment Guide

## db-red-three.vercel.app — Data Annotation App (Primary)

**To deploy the SQL Annotator (data annotation app):**

1. **Vercel Dashboard** → Project **db** → **Settings** → **General**
2. Set **Root Directory** to `apps/annotator` (click Edit, enter `apps/annotator`, Save)
3. **Redeploy** (Deployments → ⋮ on latest → Redeploy)

The annotator app will then serve at `https://db-red-three.vercel.app/` with:
- `/login` — Login (staff/123123, annotator/123123, customer/123123)
- `/` — Annotator
- `/dashboard` — Dashboard
- `/admin/tasks` — Task Board
- `/suite` — Full Suite
- `/customer` — Customer Portal

Add **Neon** or **Supabase** integration for PostgreSQL + pgvector.

---

## Static Database Docs (Alternative)

To deploy the **static database documentation** instead of the annotator:

1. Set **Root Directory** to empty (repo root)
2. **Build Command**: `bash scripts/prepare_vercel_public.sh`
3. **Output Directory**: `public`
4. **Framework Preset**: Other

This serves the index at `/` and db-N docs at `/db-6`, `/db-7`, etc.

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

