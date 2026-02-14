# Single Source of Truth

## Canonical Source: `source/db-N/app/` (Iron Triangle)

**`source/db-1/` through `source/db-16/`** are the single source of truth. The **iron triangle trifecta** lives in `source/db-N/app/`:

| Folder | Contents |
|--------|----------|
| **app/DATABASE/** | schema.sql, data.sql, data_large.sql (PostgreSQL) |
| **app/DOCUMENTATION/** | db-N.md, db-N_documentation.html, db-N_deliverable.json |
| **app/QUERIES/** | queries.md, queries.json (template format) |

Legacy paths (`data/`, `queries/`, `deliverable/`) are still supported when `app/` is absent. Populate app/ with `python3 scripts/populate_app_trifecta.py -a`.

## Derived Artifacts (All Flow From Source)

```
source/db-N/ (SOURCE OF TRUTH)
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

1. **Edit only in source** – All changes to schema, data, or queries go in `source/db-N/`.
2. **Unify** – `python3 scripts/unify_from_source.py` (resync + verify)
3. **Create zip (optional)** – `python3 scripts/unify_from_source.py --zip`

Or step-by-step:
- `python3 scripts/resync_client_db.py` – Sync `source/` -> `client/db/` (default db-root is source/)
- `python3 scripts/reconcile_and_verify_queries.py` – Verify byte-for-byte
- `python3 scripts/prepare_client_db_for_drive.py` then `python3 scripts/create_drive_upload_package.py` – Zip for distribution

## Verification

```bash
# Full unify: resync + reconcile + structure verification
python3 scripts/unify_from_source.py

# Reconcile source -> client and verify byte-for-byte (includes zip if extracted)
python3 scripts/reconcile_and_verify_queries.py

# Rigorous structure check: DATABASE/, DOCUMENTATION/, QUERIES/ (PostgreSQL-only, data_large >= 1GB)
python3 scripts/verify_unified_structure.py

# Compare data completeness across source, client, zip
python3 scripts/compare_data_sources.py
```

## Root Cleanliness

Run `python3 scripts/cleanup_root_directory.py` to move stray files:
- `queries_template.*` → `template/` (as queries.*)
- `program_economics.py` → `scripts/`
- `AUDIT_*` → `archive/reports/`
- `compliance_report.json`, `gdpval_*_report.json`, `validation_summary.json` → `results/`

Tests in `tests/test_single_source_of_truth.py` enforce root cleanliness (no .py at root, etc.).

## Client Structure (Per db-N)

| Folder | Contents |
|--------|----------|
| **DATABASE/** | PostgreSQL-only SQL: schema.sql, data.sql, data_large.sql (≥1GB) |
| **DOCUMENTATION/** | db-N.md, db-N_documentation.html, db-N_deliverable.json |
| **QUERIES/** | queries.md, queries.json (PostgreSQL-only queries) |

## Rules

- **Never edit** `client/db/` or zip contents directly; they are generated.
- **Always run** `resync_client_db.py` after changes to `source/db-N/`.
- **`/qa`** runs resync first, then client audit + compliance + integrity.
- **Zip** is a snapshot of client; regenerate after resync for distribution.
