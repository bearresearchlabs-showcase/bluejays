# Single Source of Truth

## Canonical Source: `db-N/` (Source)

**`db-1/` through `db-17/`** in the repository root are the **single source of truth** for all database content.

| Component | Location | Description |
|-----------|----------|-------------|
| Schema & Data | `db-N/data/*.sql` | schema.sql, data.sql, data_large.sql, PostgreSQL variants |
| Queries | `db-N/queries/` | queries.md, queries.json |
| Deliverable | `db-N/deliverable/` | Web-deployable docs, dbN-*/ |

## Derived Artifacts (All Flow From Source)

```
db-N/ (SOURCE OF TRUTH)
    │
    ├── resync_client_db.py
    ▼
client/db/db-N/ (CLIENT)
    │
    ├── prepare_client_db_for_drive.py
    ▼
client/db_drive_ready/ (DRIVE-READY)
    │
    ├── create_drive_upload_package.py
    ▼
client/db_drive_ready.zip (ZIP EXPORT)
```

## Workflow

1. **Edit only in source** – All changes to schema, data, or queries go in `db-N/`.
2. **Unify** – `python3 scripts/unify_from_source.py` (resync + verify)
3. **Create zip (optional)** – `python3 scripts/unify_from_source.py --zip`

Or step-by-step:
- `python3 scripts/resync_client_db.py` – Sync source -> client
- `python3 scripts/reconcile_and_verify_queries.py` – Verify byte-for-byte
- `python3 scripts/prepare_client_db_for_drive.py` then `python3 scripts/create_drive_upload_package.py` – Zip for distribution

## Verification

```bash
# Reconcile source -> client and verify byte-for-byte (includes zip if extracted)
python3 scripts/reconcile_and_verify_queries.py

# Compare data completeness across source, client, zip
python3 scripts/compare_data_sources.py
```

## Rules

- **Never edit** `client/db/` or zip contents directly; they are generated.
- **Always run** `resync_client_db.py` after changes to `db-N/`.
- **Zip** is a snapshot of client; regenerate after resync for distribution.
