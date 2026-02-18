---
name: Commit Diff Verification Plan
overview: Build a plan to test, verify, and document differences between commit 38ce1cd (sync queries) and current HEAD for source/ and client/, with a comprehensive per-DB per-section per-key report and 15 milestone todos.
todos:
  - id: todo-1
    content: Run git diff 38ce1cd HEAD -- source/ client/ and save raw output
    status: completed
  - id: todo-2
    content: Create verify_commit_diff.py with per-DB per-section categorization
    status: completed
  - id: todo-3
    content: "Generate comprehensive report: each key, each section, each db-1..db-16"
    status: completed
  - id: todo-4
    content: Compare source/db-N/app/DATABASE/ files (schema.sql, data.sql) per DB
    status: completed
  - id: todo-5
    content: Compare source/db-N/app/DOCUMENTATION/ (README, html, json) per DB
    status: completed
  - id: todo-6
    content: Compare source/db-N/app/QUERIES/ (queries.json keys, queries.md) per DB
    status: completed
  - id: todo-7
    content: Compare client/db/db-N/DATABASE/ per DB
    status: completed
  - id: todo-8
    content: Compare client/db/db-N/DOCUMENTATION/ per DB
    status: completed
  - id: todo-9
    content: Compare client/db/db-N/QUERIES/ (queries.json keys) per DB
    status: completed
  - id: todo-10
    content: Run /validate --no-overwrite and /QA --check-only, record per-DB pass/fail
    status: completed
  - id: todo-11
    content: Byte-for-byte source/app vs client/db for DATABASE and QUERIES per DB
    status: completed
  - id: todo-12
    content: Document removed/added files per section per DB
    status: completed
  - id: todo-13
    content: Add pytest test_commit_diff_verification.py
    status: completed
  - id: todo-14
    content: Create .cursor/plans/commit_diff_38ce1cd_milestone.yaml with 15 todos
    status: completed
  - id: todo-15
    content: Update docs/ROADMAP.md with link to milestone and diff report
    status: completed
isProject: false
---

# Commit Diff Verification and Milestone Planning

## Context

- **Base commit**: [38ce1cd](https://github.com/1digitaldesign/db/commit/38ce1cd1aa03012979e6a85b5ca9299449f76ad6) — "sync(queries): sync queries.json↔queries.md, propagate to client, fix expected_output"
- **Target**: Current HEAD
- **Scope**: `source/` and `client/` directories only
- **Deliverable**: YAML file with 15 milestone todos

## Key Differences (from `git diff --stat`)


| Category      | Change Summary                                                                                                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **client/**   | ~100+ files: DOCUMENTATION (README-only, removed HTML/JSON), QUERIES (queries.md, queries.json), DATABASE (schema_postgresql.sql, data_mini.sql), legacy dbN-* folders added/removed |
| **source/**   | ~75+ files: app/DOCUMENTATION (removed db-1_deliverable.json), app/QUERIES, deliverable/, queries/                                                                                   |
| **Structure** | DOCUMENTATION now README.md only; web-deployable dbN-* folders restructured; resync logic changed                                                                                    |


## Implementation Plan

### 1. Create Diff Verification Script

Create [scripts/verify_commit_diff.py](scripts/verify_commit_diff.py) to:

- Run `git diff 38ce1cd HEAD -- source/ client/` and capture output
- For each db-1..db-16: compare each section (DATABASE, DOCUMENTATION, QUERIES) and each key/file
- For `queries.json`: compare each key (number, title, description, use_case, business_value, purpose, complexity, expected_output, sql, line_number) per query
- Output comprehensive JSON report: `results/commit_diff_38ce1cd_report.json` (see Comprehensive Report Specification below)
- Exit 0 if diff is captured successfully

### 2. Create Test Script

Create [tests/test_commit_diff_verification.py](tests/test_commit_diff_verification.py) to:

- Invoke `verify_commit_diff.py` and assert report exists
- Assert report contains `databases` with db-1..db-16
- Assert each DB has `source` and `client` with DATABASE, DOCUMENTATION, QUERIES sections
- Assert `queries.json` key_diff_summary is present for DBs with queries

### 3. Create Milestone YAML

Create [.cursor/plans/commit_diff_38ce1cd_milestone.yaml](.cursor/plans/commit_diff_38ce1cd_milestone.yaml) with:

- `milestone`: "Commit 38ce1cd vs HEAD — source/ and client/ verification"
- `base_commit`: "38ce1cd1aa03012979e6a85b5ca9299449f76ad6"
- `todos`: array of 15 items (see below)

### 4. Update ROADMAP

Add a short reference in [docs/ROADMAP.md](docs/ROADMAP.md) under a new "Epic" or "Maintenance" section linking to the milestone YAML and diff report.

---

## Comprehensive Report Specification

The verification script must produce `results/commit_diff_38ce1cd_report.json` with a **per-DB, per-section, per-key** comparison. Structure:

```json
{
  "base_commit": "38ce1cd1aa03012979e6a85b5ca9299449f76ad6",
  "target": "HEAD",
  "generated_at": "YYYYMMDD-HHMM",
  "databases": {
    "db-1": {
      "source": {
        "app/DATABASE": {
          "files": {
            "schema.sql": { "at_base": "added|modified|unchanged", "at_head": "added|modified|unchanged", "hash_base": "...", "hash_head": "..." },
            "data.sql": { ... }
          },
          "summary": "N files changed"
        },
        "app/DOCUMENTATION": {
          "files": { "README.md": {...}, "db-1_deliverable.json": {...} },
          "summary": "N files added/removed/modified"
        },
        "app/QUERIES": {
          "queries.json": {
            "keys_per_query": ["number", "title", "description", "use_case", "business_value", "purpose", "complexity", "expected_output", "sql", "line_number"],
            "queries_changed": [1, 5, 12],
            "key_diff_summary": { "expected_output": 30, "description": 2 }
          },
          "queries.md": { "line_count_base": 871, "line_count_head": 871 }
        }
      },
      "client": {
        "DATABASE": { "files": {...}, "summary": "..." },
        "DOCUMENTATION": { "files": {...}, "summary": "..." },
        "QUERIES": { "queries.json": {...}, "queries.md": {...} }
      },
      "source_vs_client_sync": {
        "DATABASE": { "in_sync": true, "mismatched_files": [] },
        "QUERIES": { "in_sync": true, "mismatched_files": [] }
      }
    },
    "db-2": { ... },
    "db-16": { ... }
  },
  "summary": {
    "total_dbs": 16,
    "dbs_with_errors": [],
    "validation_pass": { "db-1": 1, "db-2": 1, ... },
    "qa_pass": { "db-1": 1, ... }
  }
}
```

### Per-DB Section Comparison


| Section           | Location                                                          | Keys/Files to Compare                                                                                                                             |
| ----------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DATABASE**      | `source/db-N/app/DATABASE/`, `client/db/db-N/DATABASE/`           | `schema.sql`, `data.sql`, `schema_postgresql.sql`, `data_mini.sql`, `*.sql`                                                                       |
| **DOCUMENTATION** | `source/db-N/app/DOCUMENTATION/`, `client/db/db-N/DOCUMENTATION/` | `README.md`, `db-N_documentation.html`, `db-N_deliverable.json`                                                                                   |
| **QUERIES**       | `source/db-N/app/QUERIES/`, `client/db/db-N/QUERIES/`             | `queries.json` (keys: number, title, description, use_case, business_value, purpose, complexity, expected_output, sql, line_number), `queries.md` |


### Per-Key Comparison for queries.json

For each query (1–30) in `queries.json`:

- **number**: unchanged / changed
- **title**: unchanged / changed
- **description**: unchanged / changed
- **use_case**: unchanged / changed
- **business_value**: unchanged / changed
- **purpose**: unchanged / changed
- **complexity**: unchanged / changed
- **expected_output**: unchanged / changed (primary focus of 38ce1cd)
- **sql**: unchanged / changed
- **line_number**: unchanged / changed

Report aggregates: `key_diff_summary` counts how many queries had each key changed (e.g. `expected_output: 30` means all 30 queries had that field modified).

### Report Output Location

- **Primary**: `results/commit_diff_38ce1cd_report.json`
- **Human-readable**: `results/commit_diff_38ce1cd_report.md` (optional, generated from JSON)

---

## 15 Milestone Todos (for YAML)

```yaml
todos:
  - id: todo-1
    content: "Run git diff 38ce1cd HEAD -- source/ client/ and save raw output"
    status: pending
  - id: todo-2
    content: "Create verify_commit_diff.py with per-DB per-section categorization"
    status: pending
  - id: todo-3
    content: "Generate comprehensive report: each key, each section, each db-1..db-16"
    status: pending
  - id: todo-4
    content: "Compare source/db-N/app/DATABASE/ files (schema.sql, data.sql) per DB"
    status: pending
  - id: todo-5
    content: "Compare source/db-N/app/DOCUMENTATION/ (README, html, json) per DB"
    status: pending
  - id: todo-6
    content: "Compare source/db-N/app/QUERIES/ (queries.json keys, queries.md) per DB"
    status: pending
  - id: todo-7
    content: "Compare client/db/db-N/DATABASE/ per DB"
    status: pending
  - id: todo-8
    content: "Compare client/db/db-N/DOCUMENTATION/ per DB"
    status: pending
  - id: todo-9
    content: "Compare client/db/db-N/QUERIES/ (queries.json keys) per DB"
    status: pending
  - id: todo-10
    content: "Run /validate --no-overwrite and /QA --check-only, record per-DB pass/fail"
    status: pending
  - id: todo-11
    content: "Byte-for-byte source/app vs client/db for DATABASE and QUERIES per DB"
    status: pending
  - id: todo-12
    content: "Document removed/added files per section per DB"
    status: pending
  - id: todo-13
    content: "Add pytest test_commit_diff_verification.py"
    status: pending
  - id: todo-14
    content: "Create .cursor/plans/commit_diff_38ce1cd_milestone.yaml with 15 todos"
    status: pending
  - id: todo-15
    content: "Update docs/ROADMAP.md with link to milestone and diff report"
    status: pending
```

---

## File Summary


| File                                                                                                 | Action                          |
| ---------------------------------------------------------------------------------------------------- | ------------------------------- |
| [scripts/verify_commit_diff.py](scripts/verify_commit_diff.py)                                       | Create                          |
| [tests/test_commit_diff_verification.py](tests/test_commit_diff_verification.py)                     | Create                          |
| [.cursor/plans/commit_diff_38ce1cd_milestone.yaml](.cursor/plans/commit_diff_38ce1cd_milestone.yaml) | Create                          |
| [docs/ROADMAP.md](docs/ROADMAP.md)                                                                   | Update (add reference)          |
| [results/commit_diff_38ce1cd_report.json](results/commit_diff_38ce1cd_report.json)                   | Generated by script             |
| [results/commit_diff_38ce1cd_report.md](results/commit_diff_38ce1cd_report.md)                       | Optional human-readable summary |


---

## Verification Commands

```bash
# 1. Run diff verification
python3 scripts/verify_commit_diff.py

# 2. Run tests
python3 -m pytest tests/test_commit_diff_verification.py -v

# 3. Manual diff inspection
git diff 38ce1cd1aa03012979e6a85b5ca9299449f76ad6 HEAD -- source/ client/ --stat
```
