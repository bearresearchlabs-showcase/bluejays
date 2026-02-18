# queries.json and queries.md — Which Are Correct?

## TL;DR

| Location | Role | Correct? |
|----------|------|----------|
| **source/db-N/queries/** | **Edit here** — canonical source | ✅ **Correct** |
| **source/db-N/QUERIES/** | Populated copy (from queries/) | ✅ Derived, matches after populate |
| **client/db/db-N/QUERIES/** | Synced from source/queries/ | ✅ Derived, matches after resync |
| **source/db-N/deliverable/** | Built by format command | ✅ Derived |
| **template/** | Fallback when db-N missing | ✅ Reference only |

---

## Canonical Source (Edit Here)

**`source/db-N/queries/queries.md`** — Human-editable source for all 30 queries.

**`source/db-N/queries/queries.json`** — Extracted from `queries.md` by:

```bash
python3 scripts/extract_queries_to_json.py [db-N]   # or -a for all
```

**Workflow:**
1. Edit `source/db-N/queries/queries.md`
2. Run `extract_queries_to_json.py` to regenerate `queries.json`
3. Run `populate_app_trifecta.py` to copy to `source/db-N/QUERIES/`
4. Run `resync_client_db.py` to sync to `client/db/db-N/QUERIES/`

---

## Derived Locations (Do Not Edit)

| Path | How It Gets There |
|------|-------------------|
| `source/db-N/QUERIES/queries.json`, `queries.md` | `populate_app_trifecta.py` copies from `queries/` |
| `client/db/db-N/QUERIES/queries.json`, `queries.md` | `resync_client_db.py` copies from `source/db-N/queries/` |
| `source/db-N/deliverable/queries/` | `/format` command builds from source |
| `source/db-N/deliverable/dbN-xxx/queries/` | Web-deployable package from format |

---

## Lookup Order (Ingest App)

`apps/ingest/lib/data.ts` resolves queries in this order:

1. `source/db-N/app/QUERIES/queries.json` (if app/ exists)
2. `source/db-N/QUERIES/queries.json`
3. `source/db-N/queries/queries.json`

---

## Rules

- **Never edit** `client/db/` or deliverable folders directly.
- **Always edit** `source/db-N/queries/queries.md`.
- **Always run** `extract_queries_to_json.py` after editing `queries.md`.
- **Run** `populate_app_trifecta.py` and `resync_client_db.py` to propagate changes.
