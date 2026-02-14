# /QA Command

Run the QA suite: format deliverables, resync, client/db audit, compliance check, and integrity checks.

## Usage

```
/QA                    # Run QA on all databases (default -a)
/QA @db/db-1/          # Run on db-1 (Cursor @-reference)
/QA db-1               # Run on db-1
/QA db-1 db-5          # Run on db-1 through db-5
/QA -a                 # Run on all db-1 through db-16
```

## Cursor @-References

Use `@db/db-{N}/` to scope /QA to specific databases. Cursor resolves @-references before passing args to the command.

## What It Runs

1. **Format** - Format deliverables (queries, schema, docs) for specified DBs
2. **Resync** - Sync source/ → client/db
3. **QA (client/db audit)** - Checks DATABASE/, DOCUMENTATION/, QUERIES/ structure in client/db
4. **Compliance** - Strict checklist: queries.json (30), queries.md, schema, client DOCUMENTATION/
5. **Integrity** - CRC-32, CRC-64, SHA-256 on schema.sql, queries.json; updates metadata/integrity.json

## Workbench Installation

- **First-time**: Run `./scripts/install_workbenches.sh` to install tb3_workbench
- **Auto-install**: qa.sh installs from `../pluto/tb3_workbench` if not present
- **bird-workbench**: Requires tb3_workbench for ACID/BASE assertions

## tb3_workbench / bird-workbench

- **ACID/BASE testing**: Tests databases for ACID (Atomicity, Consistency, Isolation, Durability) and BASE properties, validating industrial-grade enterprise DB behavior
- **Note**: Use path `../pluto/tb3_workbench` to reference; adding to workspace enables `@tb3_workbench` but can reset chat when switching workspaces

## Hardened PostgreSQL + Docker Hub

- **After QA suite**: qa.sh runs `docker_postgres_qa.sh` to start hardened PostgreSQL, load schema+data per DB, and optionally push to Docker Hub
- **One hardened image per DB**: Each db-1..db-16 gets its own image `{DOCKER_HUB_USER}/db-postgres-db-{N}:latest`
- **Push**: Set `DOCKER_HUB_USER`; qa.sh auto-adds --push when set
- **Manual**: `./scripts/docker_postgres_qa.sh [--push] [db-1] [db-5] | -a`

## Test Suites

- **Pytest**: `pytest tests/test_qa_suite.py tests/test_docker_postgres_qa.py tests/test_bird_workbench_acid.py -v`
- **Full run**: `./scripts/run_all_tests.sh [db-1] | -a` (mirrors Jenkins)

See `.cursor/rules/qa-workflow-cursor.mdc` for end-to-end workflow and Cursor techniques.

## Output

- Console: Pass/Fail per database
- `results/compliance_report.json` - Compliance results
- `db-{N}/metadata/integrity.json` - Integrity checksums
