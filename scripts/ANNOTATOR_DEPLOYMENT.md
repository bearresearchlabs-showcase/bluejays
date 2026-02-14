# Annotator App — Deployment

## Local development

```bash
python scripts/annotator_app.py --port 8766 --host 127.0.0.1
```

- Main: http://127.0.0.1:8766/
- Login: http://127.0.0.1:8766/login
- Dashboard: http://127.0.0.1:8766/dashboard
- Staff: http://127.0.0.1:8766/staff
- Task Board: http://127.0.0.1:8766/admin/tasks
- Full Suite: http://127.0.0.1:8766/suite
- Customer Portal: http://127.0.0.1:8766/customer

**Credentials:** staff/123123, annotator/123123

## Vercel deployment

The annotator app is a Python HTTP server with in-memory sessions. For Vercel:

1. **Option A — Serverless functions**  
   Refactor into `api/` handlers. Replace in-memory `SESSIONS` with Vercel KV, Redis, or JWT cookies.

2. **Option B — External host**  
   Deploy the Python server to Railway, Render, Fly.io, or a VPS. Point a custom domain from Vercel if needed.

3. **Option C — Hybrid**  
   Static pages (login, dashboard) on Vercel; API routes as serverless functions; session store in Vercel KV.

## Next steps for full Vercel app

- [ ] Add `api/` directory with serverless handlers
- [ ] Replace `SESSIONS` with Vercel KV or JWT
- [ ] Add `vercel.json` for routing
- [ ] Configure env vars (credentials, DB URLs)
