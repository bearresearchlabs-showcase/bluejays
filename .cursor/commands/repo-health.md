---
name: repo-health
description: Run repo health check (data size, schema, naming) and compile MDX report
usage: |
  /repo-health              # Run repo health check
  /repo-health --lenient    # Migration mode (warn, don't fail)
---

# /repo-health Command

Run the repo health checker and compile the MDX report. Validates data size (1GB total), schema PostgreSQL compliance, naming conventions, and flags unnecessary files.

## Usage

```bash
/repo-health              # Run check (strict)
/repo-health --lenient    # Migration mode - warn instead of fail
```

## What It Does

1. **repo_health_check.py** - Validates:
   - Data size (1GB total across all data.sql)
   - Schema PostgreSQL compliance
   - Naming conventions (snake_case)
   - Unnecessary source/root files

2. **compile_repo_health_mdx.py** - Compiles JSON to MDX

## Output

- `results/repo_health.json` - Machine-readable health report
- `results/repo_health.mdx` - Human-readable report

## Environment

- **REPO_HEALTH_LENIENT=1** - Set automatically with `--lenient`; relaxes checks for migration

## Related

- `/test repo-health` - Run pytest tests for repo health (test_repo_health.py)
- `/QA` - Full QA suite (includes repo health in run_all_tests)
