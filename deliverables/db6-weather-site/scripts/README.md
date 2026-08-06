# Scripts Directory README

## Overview

This directory contains utility scripts for managing notebooks, dashboards, and database deliverables.

## Notebook Management Scripts

### `run_notebooks.py`

Run Jupyter notebooks for all databases with multiple execution methods.

**Usage:**
```bash
# Run all notebooks
python3 scripts/run_notebooks.py

# Run specific database
python3 scripts/run_notebooks.py --db db-6

# Try all methods until one succeeds
python3 scripts/run_notebooks.py --all-methods

# Use specific method
python3 scripts/run_notebooks.py --method 2  # papermill
```

**Execution Methods:**
1. `jupyter nbconvert --execute` (default)
2. `papermill`
3. Python `nbformat` directly

### `update_notebooks_failsafe.py`

Add failsafe logic to notebooks for path correction and forced package installation.

**Usage:**
```bash
# Update all notebooks
python3 scripts/update_notebooks_failsafe.py

# Update only client/db notebooks
python3 scripts/update_notebooks_failsafe.py --client-only

# Update specific database
python3 scripts/update_notebooks_failsafe.py --db db-6

# Update from custom directory
python3 scripts/update_notebooks_failsafe.py --root-dir /path/to/notebooks
```

**Features:**
- Automatic path correction (searches multiple locations)
- Forced package installation (6 fallback methods)
- Creates backup files (`.ipynb.failsafe_backup`)

### `download_and_update_from_drive.py`

Download notebooks from Google Drive and update them with failsafe logic.

**Usage:**
```bash
# Auto-detect download method
python3 scripts/download_and_update_from_drive.py

# Use specific method
python3 scripts/download_and_update_from_drive.py --method gdown

# Manual download then update
python3 scripts/download_and_update_from_drive.py --skip-download --download-dir /path/to/files

# Only update (no download)
python3 scripts/download_and_update_from_drive.py --update-only --download-dir /path/to/files
```

**Requirements:**
- `gdown`: `pip install gdown` (for Google Drive download)
- `rclone`: `brew install rclone` (alternative method)

## Dashboard Scripts

### `create_streamlit_dashboards.py`

Generate Streamlit dashboards for all databases.

**Usage:**
```bash
python3 scripts/create_streamlit_dashboards.py
```

**Output:** `docker/notebooks/db-{N}_dashboard.py`

### `test_streamlit_dashboards.sh`

Test Streamlit dashboards in Docker containers.

**Usage:**
```bash
bash scripts/test_streamlit_dashboards.sh
```

### `run_streamlit_dashboards.sh`

Run all Streamlit dashboards in Docker containers.

**Usage:**
```bash
bash scripts/run_streamlit_dashboards.sh
```

## Docker Scripts

### `docker_build_all.sh`

Build all Docker containers for databases.

**Usage:**
```bash
bash scripts/docker_build_all.sh
```

### `docker_execute_notebooks.sh`

Execute notebooks in Docker containers.

**Usage:**
```bash
bash scripts/docker_execute_notebooks.sh
```

## Consistency and ACID Testing

### `test_all_databases_consistency_acid.py`

Test all databases (db-1 through db-16) for consistency, ACID transactions, and query execution using a dedicated PostgreSQL instance.

**Prerequisites:**
- Docker
- `psycopg2-binary`: `pip install psycopg2-binary`

**Usage:**
```bash
# Start PostgreSQL test instance (port 5433)
docker compose -f docker/docker-compose.test-postgresql.yml up -d

# Run full test (all 16 databases)
python3 scripts/test_all_databases_consistency_acid.py

# Test subset (e.g. db-1 through db-5)
DB_RANGE=1-5 python3 scripts/test_all_databases_consistency_acid.py

# Or use the shell script (starts container + runs tests)
bash scripts/run_consistency_acid_tests.sh
```

**Environment variables:**
- `PG_TEST_HOST` - PostgreSQL host (default: 127.0.0.1)
- `PG_TEST_PORT` - PostgreSQL port (default: 5433)
- `PG_TEST_USER` / `PG_TEST_PASSWORD` - Credentials
- `DB_RANGE` - Subset, e.g. `1-5` or `1,3,6`

**Output:** `results/consistency_acid_query_test_results.json`

**Tests performed:**
- Schema and data load consistency
- ACID: Atomicity (ROLLBACK), Consistency (NOT NULL), Isolation, Durability (COMMIT)
- Query execution (from queries.json)

## Validation Scripts

### `extract_queries_to_json.py`

Extract queries from `queries.md` to `queries.json` (Phase 0).

**Usage:**
```bash
python3 scripts/extract_queries_to_json.py [db-number]
```

### `qc_additional_checks.py`

Perform additional QC checks on queries.

**Usage:**
```bash
python3 scripts/qc_additional_checks.py
```

## Common Workflows

### Update Notebooks from Google Drive

```bash
# 1. Download and update
python3 scripts/download_and_update_from_drive.py

# 2. Test notebooks
python3 scripts/run_notebooks.py --all-methods
```

### Add Failsafe to All Notebooks

```bash
# 1. Update root notebooks
python3 scripts/update_notebooks_failsafe.py

# 2. Verify failsafe added
grep -r "FAILSAFE" db-*/db-*.ipynb | wc -l
```

### Run All Notebooks

```bash
# Method 1: Try all methods
python3 scripts/run_notebooks.py --all-methods

# Method 2: Use specific method
python3 scripts/run_notebooks.py --method 1

# Method 3: Run specific database
python3 scripts/run_notebooks.py --db db-6 --method 1
```

## Script Dependencies

### Python Packages
- `jupyter` - Notebook execution
- `papermill` - Parameterized notebook execution
- `nbformat` - Notebook format handling
- `gdown` - Google Drive download (optional)
- `rclone` - Cloud storage sync (optional)

### System Tools
- `jupyter` - Jupyter notebook server
- `bash` - Shell scripts
- `docker` - Container management
- `docker-compose` - Multi-container orchestration

## Troubleshooting

### Script Not Found

```bash
# Ensure scripts are executable
chmod +x scripts/*.py scripts/*.sh

# Run from project root
cd /Users/machine/Documents/AQ/db
python3 scripts/script_name.py
```

### Import Errors

```bash
# Install missing packages
pip install jupyter papermill nbformat gdown

# Or use requirements.txt
pip install -r scripts/requirements.txt
```

### Permission Errors

```bash
# Make scripts executable
chmod +x scripts/*.py scripts/*.sh

# Run with appropriate permissions
sudo python3 scripts/script_name.py  # If needed
```

## Related Documentation

- `NOTEBOOK_UPDATE_README.md` - Detailed notebook update guide
- `CLIENT_SYNC_SUMMARY.md` - Client synchronization summary
- `docker/README.md` - Docker setup documentation

---

**Last Updated:** 2026-02-08
**Version:** 1.0
