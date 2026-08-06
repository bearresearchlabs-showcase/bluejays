---
name: validate
description: Run validation suite for database repositories
usage: |
  /validate @db/db-1/              # Validate single database
  /validate @db/db-1/ @db/db-5/    # Validate range of databases
  /validate -a                     # Validate all databases (db-1 through db-15)
  /validate db-1                    # Validate by database number
  /validate db-1 db-5              # Validate range by database numbers
---

# Validate Command

Run the complete validation suite for database repositories.

## Usage

```bash

# Validate single database

/validate @db/db-1/

# Validate range of databases

/validate @db/db-1/ @db/db-5/

# Validate all databases

/validate -a

# Validate by database number

/validate db-1

# Validate range by database numbers

/validate db-1 db-5
```

## What It Does

The validation command runs the complete validation suite:

1. **Phase 0**: Extract `queries.md` to `queries.json` (REQUIRED)
2. **Phase 1**: Verify fixes
3. **Phase 2 & 4**: Syntax validation and comprehensive evaluation
4. **Phase 3**: Execution testing (optional, requires database credentials)
5. **Phase 5**: Generate final report

## Output

- Validation results are saved to `db-{N}/results/` directories
- Summary report is saved to `validation_summary.json` in the root directory
- Console output shows progress and results for each phase

## Examples

```bash

# Validate db-1

/validate @db/db-1/

# Validate db-1 through db-5

/validate @db/db-1/ @db/db-5/

# Validate all databases

/validate -a

# Quick validation (no database connections required)

/validate db-1
```

## Exit Codes

- `0`: All validations passed
- `1`: One or more validations failed
- `2`: Partial validation (some phases skipped)
