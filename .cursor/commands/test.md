---
name: test
description: Run BDD/TDD/DDD test suites (schema-data, repo-health, queries-md, source-checks)
usage: |
  /test                    # Run all BDD/TDD/DDD tests (default)
  /test schema-data        # Schema and data validation (1GB data, PostgreSQL compliance, naming)
  /test repo-health        # Repo health checker and MDX compilation
  /test queries-md         # queries.md compilation and header consistency
  /test source-checks      # Source material checks
  /test all                # Same as default - all test groups
  /test -v                 # Verbose pytest output
  /test --lenient          # REPO_HEALTH_LENIENT=1 (migration mode)
---

# /test Command

Run BDD/TDD/DDD test suites for schema, data, repo health, queries.md, and source material checks.

## Usage

```bash
# Run all BDD/TDD/DDD tests (default)
/test

# Run specific test group
/test schema-data        # Schema and data validation
/test repo-health        # Repo health checker
/test queries-md         # queries.md compilation
/test source-checks      # Source material checks
/test all                # All groups (explicit)

# Options
/test -v                 # Verbose pytest output
/test --lenient          # REPO_HEALTH_LENIENT=1 for migration
/test schema-data -v     # Combine group + options
```

## Test Groups

| Group | Tests | Purpose |
|-------|-------|---------|
| **schema-data** | `test_schema_data_validation_tdd_bdd.py` | Data size (1GB), PostgreSQL schema compliance, CREATE TABLE, snake_case, INSERT/COPY, schema–data naming |
| **repo-health** | `test_repo_health.py` | Repo health checker, MDX compilation, `repo_health.json` / `repo_health.mdx` |
| **queries-md** | `test_queries_md_compile_tdd_bdd.py` | queries.md compilation, header consistency (HTML-like), data update correctness |
| **source-checks** | `test_source_material_checks.py` | Source material checks |
| **all** | All of the above + single_source_of_truth, queries_md_human_text | Full BDD/TDD/DDD suite |

## What It Runs

Delegates to `db_check test` which invokes pytest on the corresponding test files:

- **schema-data**: TDD/BDD/DDD for data size, schema PostgreSQL compliance, naming
- **repo-health**: Repo health checker and MDX compilation
- **queries-md**: queries.md compile, header consistency, data updates
- **source-checks**: Source material validation

## Environment

- **REPO_HEALTH_LENIENT**: Set to `1` with `--lenient` for migration (relaxes data size and schema checks)
- **.venv**: Uses project venv if present

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed

## Auto-Regression (CI)

The regression test suite runs automatically in CI on every push/PR:

- **CI job**: `regression` in `.github/workflows/ci.yml`
- **Local**: `npm run test:regression` or `/test`
- **Full run**: `./scripts/run_all_tests.sh` includes regression

## Related

- `run_all_tests.sh` - Full test run (mirrors Jenkins)
- `npm run test:regression` - Auto-regression suite (BDD/TDD/DDD)
- `db_check repo-health` - Repo health check (outputs repo_health.json, repo_health.mdx)
- `.cursor/rules/qa-workflow-cursor.mdc` - QA workflow
