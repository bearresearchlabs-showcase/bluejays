# SQL Annotator — Next.js App

Next.js version of the annotator app, ready for Vercel deployment.

## Run locally

```bash
cd apps/annotator
npm install
npm run dev
```

Open http://localhost:3001

## Deploy to Vercel

1. Push to GitHub
2. Import project in Vercel
3. Set **Root Directory** to `apps/annotator`
4. Add env var `JWT_SECRET` (optional; defaults to dev secret)
5. **PostgreSQL + pgvector**: Integrations → Neon or Supabase (injects `POSTGRES_URL`)
6. Deploy

See `../../docs/VERCEL_DEPLOY.md` for PostgreSQL and vector setup.

## Credentials

- **staff** / 123123 — full access, mode selector (Annotator/Admin)
- **annotator** / 123123 — annotator views only
- **customer** / 123123 — Customer Portal and Full Suite only

## Routes

- `/login` — Login page
- `/` — Annotator
- `/dashboard` — Dashboard hub
- `/staff` — Staff hub
- `/admin/tasks` — Task Board
- `/suite` — Full Suite (all databases)
- `/customer` — Customer Portal (filters, export)

## Data source

Reads from `../../source/` (repo root `source/`). When deploying, ensure the repo includes the `source/` directory. Set Vercel **Root Directory** to `apps/annotator` — the build will have access to `../source` from the monorepo.
