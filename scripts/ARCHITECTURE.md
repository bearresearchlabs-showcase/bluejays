# Scripts Architecture

## Overview

Scripts consolidate into **testing**, **checking**, and **validation + verification**. Compiled binaries handle pure computation; Python orchestrates workflows.

## Command Categories

| Category | Subcommands | Purpose |
|----------|-------------|---------|
| **Testing** | `test`, `validate`, `validate-queries` | BDD/TDD/DDD test suites, Phase 0–5 validation |
| **Checking** | `qa`, `source-checks`, `check-commit`, `repo-health`, `schema-postgresql-validate` | Client audit, source material, repo health |
| **Validation + Verification** | `validate`, `integrity`, `compliance` | Query validation, CRC/hash, compliance checklist |
| **Build** | `build` | Populate → format → resync → verify (format is internal step) |

## Entry Points

| Command | Script | Purpose |
|---------|--------|---------|
| `/validate` | `db_check.py validate` | Run validation suite (Phase 0–5) |
| `/build` | `db_check.py build` | Build source → client/db (populate, format, resync, verify) |
| `/QA` | `db_check.py qa-suite` | QA suite (audit + compliance + integrity); `--full` adds populate/format/resync |
| `/check` | `db_check.py full` | All checks (validate + qa + integrity + compliance) |
| `/test` | `db_check.py test` | BDD/TDD/DDD test suites |
| `make scrub` | `scrub_keywords.py` | Keyword cleanup (config-driven) |
| `make scrub-4x` | `scrub_4x.sh` | 4x parallel scrub (worktrees) |

## Core Scripts (Keep)

- **db_check.py** – Unified orchestrator (testing, checking, validation, verification, build)
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
- **sync_to_client_db.py** – Superseded by `resync_client_db.py` (single source: data/, queries/, docs/)
- **consolidate_queries_to_app.py**, **standardize_deliverable_structure.py**, **standardize_db_data.py** – Moved to `archive/legacy-deliverable/`
- **analyze_source_redundancy.py**, **archive_source_redundant.py** – Moved to `archive/legacy-deliverable/`
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

## Queries.md Workflow

`queries.md` is built from two sources:

1. **Header** (lines 1–200): `source/db-N/queries_header.yaml` or `queries_header.json` (top level, NOT in app)
2. **Queries**: `queries.json` (from app/QUERIES or queries/)

| Script | Purpose |
|--------|---------|
| `rewrite_queries_md_to_template.py` | Build queries.md from header + queries.json |
| `extract_queries_header_to_yaml.py` | Extract header from existing queries.md → queries_header.yaml (migration) |
| `load_queries_header.py` | Load header from YAML/JSON (used by rewrite) |
| `update_queries_md_from_json.py` | Sync query blocks (### Query N) from queries.json into existing queries.md |

When `populate_app_trifecta` runs, it builds `queries.md` from `queries_header` + `queries.json` when the header file exists.

## Single Responsibility

Each script does **one thing**:

- `checksum` → compute hashes only
- `scrub_keywords` → replace keywords per config
- `integrity_checks` → orchestrate checksums, write metadata
- `db_check` → route to subcommands
