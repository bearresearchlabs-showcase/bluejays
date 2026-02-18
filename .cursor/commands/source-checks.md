---
name: source-checks
description: Run source material validation (queries.json, schema, data, queries.md)
usage: |
  /source-checks              # Check all databases (default -a)
  /source-checks db-1         # Check db-1
  /source-checks db-1 db-5    # Check db-1 through db-5
  /source-checks -a           # Check all db-1 through db-16
---

# /source-checks Command

Run source material validation for database repositories. Validates queries.json, queries_header (YAML/JSON), schema, data, and queries.md consistency.

## Usage

```bash
/source-checks              # All databases
/source-checks db-1         # Single database
/source-checks db-1 db-5    # Range
/source-checks -a           # All (explicit)
```

## What It Validates

- **queries.json** - Exists, valid structure, 30 queries
- **queries_header** - YAML/JSON config at source/db-N/ level
- **schema** - schema.sql exists, PostgreSQL compliant
- **data** - data.sql or data_large.sql
- **queries.md** - Compilation, header consistency

## Related

- `/test source-checks` - Run pytest tests (test_source_material_checks.py)
- `/test` - Run all BDD/TDD/DDD tests
