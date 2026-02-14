# Scripts Architecture

## Overview

Scripts are organized for **single responsibility** and **consistent behavior**. Compiled binaries handle pure computation; Python orchestrates workflows.

## Entry Points

| Command | Script | Purpose |
|---------|--------|---------|
| `/validate` | `db_check.py validate` | Run validation suite (Phase 0–5) |
| `/format` | `db_check.py format` | Package deliverables |
| `/QA` | `db_check.py qa-suite` | QA suite + compliance + integrity |
| `/check` | `db_check.py full` | All checks |
| `make scrub` | `scrub_keywords.py` | Keyword cleanup (config-driven) |
| `make scrub-4x` | `scrub_4x.sh` | 4x parallel scrub (worktrees) |

## Core Scripts (Keep)

- **db_check.py** – Unified orchestrator (validate, format, qa, integrity, compliance, export, etc.)
- **validate.py** – Validation runner
- **format.py** – Deliverable formatter
- **integrity_checks.py** – CRC/SHA checksums (uses `bin/checksum` when built)
- **scrub_keywords.py** – Config-driven keyword replacement (replaces remove_databricks, remove_non_postgres_vendors)
- **qa_client_db.py**, **bird_export.py**, **generate_db_metadata.py**, **gdpval_validation.py**
- **run_all_tests.sh**, **install_workbenches.sh**, **docker_postgres_qa.sh**
- **db_health.sh**, **db_replication_lag.sh**, **db_backup_verify.sh**

## Compiled Binaries (`scripts/bin/`)

| Binary | Purpose | Fallback |
|--------|---------|----------|
| `checksum` | CRC-32, CRC-64-ECMA, SHA-256 for a file → JSON | Python `integrity_checks.py` |

Build: `make build-bin` or `cd scripts/bin && cargo build --release`

## Pruned / Archived

- **remove_databricks.py** – Superseded by `scrub_keywords.py`
- **remove_non_postgres_vendors.py** – Superseded by `scrub_keywords.py`
- **fix_*.py** (one-off) – Moved to `archive/one-off-fixes/`
- **update_*.py** (one-off) – Moved to `archive/one-off-updates/` (update_table_of_contents, update_sourced_language, update_docker_compose_streamlit, update_client_dashboards_paths, update_html_with_*)

## Directory Layout

```
scripts/
├── ARCHITECTURE.md     # This file
├── bin/                # Compiled binaries
│   ├── README.md
│   ├── Makefile        # make -C scripts/bin all
│   └── checksum/       # Rust: CRC32, CRC64, SHA256
├── archive/            # Obsolete / one-off scripts
│   ├── legacy-vendor/  # remove_databricks, remove_non_postgres_vendors
│   ├── one-off-fixes/  # fix_*.py (db6, db15, unboundlocal, etc.)
│   └── one-off-updates/
├── testing/            # Query fixers, test harnesses
└── [core scripts]
```

## Testing

| Framework | Location | Run |
|-----------|----------|-----|
| **Rust** (cargo) | `scripts/bin/checksum/` | `cargo test` |
| **Rust** (integration) | `scripts/bin/checksum/tests/` | `cargo build --release && cargo test --release --test integration` |
| **Python** (pytest) | `tests/test_scripts_refactor.py` | `pytest tests/test_scripts_refactor.py -v` |

Included in `run_all_tests.sh` and `make test`.

## Single Responsibility

Each script does **one thing**:

- `checksum` → compute hashes only
- `scrub_keywords` → replace keywords per config
- `integrity_checks` → orchestrate checksums, write metadata
- `db_check` → route to subcommands
