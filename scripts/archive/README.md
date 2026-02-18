# Archived Scripts

Scripts moved here are obsolete, one-off, or superseded. Do not use in new workflows.

## legacy-vendor/

- **remove_databricks.py** – Superseded by `scrub_keywords.py`
- **remove_non_postgres_vendors.py** – Superseded by `scrub_keywords.py`

Use `make scrub` or `python3 scripts/scrub_keywords.py` instead.

## legacy-deliverable/

Scripts that used `deliverable/` as source. Superseded by single source of truth (data/, queries/, docs/).

- **sync_to_client_db.py** – Superseded by `resync_client_db.py` (uses data/, queries/, docs/)
- **consolidate_queries_to_app.py** – One-off migration; archives from deliverable/queries
- **standardize_deliverable_structure.py** – Copies to deliverable/data, deliverable/queries
- **standardize_db_data.py** – Cleans deliverable/data
- **analyze_source_redundancy.py** – Analyzes deliverable-based redundancy
- **archive_source_redundant.py** – Archives deliverable-based redundant files

Use `resync_client_db.py` and `populate_app_trifecta.py` instead.

## one-off-fixes/

One-time fix scripts (db6, db15, unboundlocal, colab, notebook, etc.). Kept for reference only.

## one-off-updates/

One-time update scripts (db6/db7 merge, etc.). Kept for reference only.
