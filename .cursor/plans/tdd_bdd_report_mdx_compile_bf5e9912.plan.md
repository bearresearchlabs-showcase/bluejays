---
name: TDD BDD Report MDX Compile
overview: Extend TDD/BDD tests for commit diff verification and add a compile workflow that produces an MDX report from commit_diff_38ce1cd_report.json, following the same patterns as queries.json to queries.md.
todos:
  - id: tdd-1
    content: Add test_report_json_valid_schema to test_commit_diff_verification.py
    status: completed
  - id: tdd-2
    content: Add test_each_db_has_files_with_at_base_at_head
    status: completed
  - id: tdd-3
    content: Add test_key_diff_summary_counts_integer
    status: completed
  - id: bdd-1
    content: Add test_scenario_raw_diff_includes_source_client
    status: completed
  - id: bdd-2
    content: Add test_scenario_report_compilable_to_mdx
    status: completed
  - id: compile-1
    content: Create scripts/compile_commit_diff_report.py (JSON to MDX)
    status: completed
  - id: compile-2
    content: Create tests/test_commit_diff_report_compile_tdd_bdd.py
    status: completed
  - id: compile-3
    content: Add --compile-mdx flag to verify_commit_diff.py
    status: completed
  - id: schema-1
    content: Create template/commit_diff_report_schema.yaml (optional)
    status: completed
  - id: milestone-1
    content: Update commit_diff_38ce1cd_milestone.yaml with todos 16-17
    status: completed
isProject: false
---

# TDD/BDD Plan and MDX Report Compile

## Context

- **Existing workflow**: `queries.json` + raw materials → `queries.md` via [scripts/queries_md_json_translator.py](scripts/queries_md_json_translator.py), [scripts/queries-convert/format-md.js](scripts/queries-convert/format-md.js), [template/queries_format_schema.yaml](template/queries_format_schema.yaml)
- **MDX pattern**: YAML frontmatter + CommonMark body (see [scripts/generate_documentation_readme.py](scripts/generate_documentation_readme.py), [template/DOCUMENTATION_README_SKELETON.md](template/DOCUMENTATION_README_SKELETON.md))
- **Report source**: [results/commit_diff_38ce1cd_report.json](results/commit_diff_38ce1cd_report.json), [results/commit_diff_38ce1cd_raw.txt](results/commit_diff_38ce1cd_raw.txt)

## Part 1: TDD/BDD Test Extensions

### 1.1 Extend [tests/test_commit_diff_verification.py](tests/test_commit_diff_verification.py)

Add tests mirroring [tests/test_queries_md_compile_tdd_bdd.py](tests/test_queries_md_compile_tdd_bdd.py) patterns:


| Test                                            | Type | Purpose                                                                                           |
| ----------------------------------------------- | ---- | ------------------------------------------------------------------------------------------------- |
| `test_report_json_valid_schema`                 | TDD  | Assert report has required top-level keys (base_commit, target, generated_at, databases, summary) |
| `test_each_db_has_files_with_at_base_at_head`   | TDD  | Assert file entries have at_base, at_head, changed                                                |
| `test_key_diff_summary_counts_integer`          | TDD  | Assert key_diff_summary values are integers                                                       |
| `test_scenario_raw_diff_includes_source_client` | BDD  | Given raw diff file, When inspected, Then contains source/ or client/ paths                       |
| `test_scenario_report_compilable_to_mdx`        | BDD  | Given report JSON, When compile runs, Then MDX output has frontmatter and sections                |


### 1.2 Add compile-report TDD/BDD tests

Create [tests/test_commit_diff_report_compile_tdd_bdd.py](tests/test_commit_diff_report_compile_tdd_bdd.py):

- **TDD**: `test_compile_produces_mdx`, `test_compile_has_frontmatter`, `test_compile_per_db_sections`, `test_compile_consistent_format`
- **BDD**: `test_given_report_json_when_compile_then_mdx_has_all_dbs`, `test_given_report_json_when_compile_then_data_consistent_with_json`

## Part 2: Compile Script (JSON → MDX)

### 2.1 Create [scripts/compile_commit_diff_report.py](scripts/compile_commit_diff_report.py)

**Inputs**:

- `results/commit_diff_38ce1cd_report.json` (required)
- `results/commit_diff_38ce1cd_raw.txt` (optional, for raw diff section)

**Output**: `results/commit_diff_38ce1cd_report.mdx`

**Structure** (consistent with queries.md / DOCUMENTATION patterns):

```mdx
---
title: Commit Diff Verification Report — 38ce1cd vs HEAD
description: Per-DB, per-section, per-key comparison of source/ and client/
base_commit: 38ce1cd1aa03012979e6a85b5ca9299449f76ad6
target: HEAD
generated_at: YYYYMMDD-HHMM
---

# Commit Diff Verification Report

**Base commit:** 38ce1cd
**Target:** HEAD
**Scope:** source/, client/

---

## Summary

- Total DBs: 16
- Validation pass: N
- QA pass: N

---

## Per-DB Report

### db-1

**Source**
- app/DATABASE: {summary}
- app/DOCUMENTATION: {summary}
- app/QUERIES: {summary}

**Client**
- DATABASE: {summary}
- DOCUMENTATION: {summary}
- QUERIES: {summary}

**Sync**
- DATABASE: in sync | mismatched
- QUERIES: in sync | mismatched

**queries.json key_diff_summary** (if present)
| Key | Queries Changed |
|-----|-----------------|
| expected_output | 30 |
| description | 30 |

---

### db-2
...
### db-16

---

## Raw Diff (optional)

```text
{excerpt from raw diff or "See commit_diff_38ce1cd_raw.txt"}
```

*Generated by compile_commit_diff_report.py. MDX-compatible markdown.*

```

### 2.2 Schema for consistency

Create [template/commit_diff_report_schema.yaml](template/commit_diff_report_schema.yaml) (optional):

- Defines required sections and field order
- Validates output structure matches JSON input
- Mirrors `queries_format_schema.yaml` pattern

## Part 3: Integration

### 3.1 Wire compile into verify_commit_diff.py

Add `--compile-mdx` flag to [scripts/verify_commit_diff.py](scripts/verify_commit_diff.py):

- After writing JSON report, call `compile_commit_diff_report.main()` when `--compile-mdx` is set
- Output: `results/commit_diff_38ce1cd_report.mdx`

### 3.2 Update milestone YAML

Add to [.cursor/plans/commit_diff_38ce1cd_milestone.yaml](.cursor/plans/commit_diff_38ce1cd_milestone.yaml):

- `todo-16`: Compile report JSON to MDX
- `todo-17`: Add TDD/BDD tests for compile
- Artifact: `results/commit_diff_38ce1cd_report.mdx`

## Data Consistency Rules

1. **Field mapping**: JSON keys map 1:1 to MDX section headers (e.g. `databases.db-1.source.app/DATABASE.summary` → "app/DATABASE: {summary}")
2. **Numeric consistency**: All counts from JSON; no recomputation in compile
3. **Timestamp**: Use `generated_at` from JSON in frontmatter
4. **Per-DB order**: db-1 through db-16, same order as JSON

## File Summary

| File | Action |
|------|--------|
| [tests/test_commit_diff_verification.py](tests/test_commit_diff_verification.py) | Extend (5 new tests) |
| [tests/test_commit_diff_report_compile_tdd_bdd.py](tests/test_commit_diff_report_compile_tdd_bdd.py) | Create |
| [scripts/compile_commit_diff_report.py](scripts/compile_commit_diff_report.py) | Create |
| [template/commit_diff_report_schema.yaml](template/commit_diff_report_schema.yaml) | Create (optional) |
| [scripts/verify_commit_diff.py](scripts/verify_commit_diff.py) | Add --compile-mdx |
| [.cursor/plans/commit_diff_38ce1cd_milestone.yaml](.cursor/plans/commit_diff_38ce1cd_milestone.yaml) | Add todos 16–17 |

## Incremental Progress Order

| Phase | Todo IDs | Description |
|-------|----------|-------------|
| 1 | tdd-1, tdd-2, tdd-3 | TDD tests for report structure |
| 2 | bdd-1, bdd-2 | BDD scenario tests |
| 3 | compile-1 | Compile script (enables compile tests) |
| 4 | compile-2 | Compile TDD/BDD tests |
| 5 | compile-3 | Wire --compile-mdx into verify |
| 6 | schema-1, milestone-1 | Schema + milestone update |

## Verification Commands

```bash
# Run TDD/BDD tests
python3 -m pytest tests/test_commit_diff_verification.py tests/test_commit_diff_report_compile_tdd_bdd.py -v

# Generate report + compile to MDX
python3 scripts/verify_commit_diff.py --skip-validate-qa --compile-mdx

# Compile only (JSON already exists)
python3 scripts/compile_commit_diff_report.py
```
