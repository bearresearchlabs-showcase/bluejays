# /validate Command Usage

## Overview

The `/validate` command runs the complete validation suite for database repositories, executing all validation phases in sequence.

## Syntax

```bash
/validate [database-spec] [database-spec] ...
/validate -a
```

## Arguments

### Database Specifications

You can specify databases in multiple formats:

1. **Cursor format**: `@db/db-N/`
   ```bash
   /validate @db/db-1/
   /validate @db/db-1/ @db/db-5/
   ```

2. **Database name**: `db-N`
   ```bash
   /validate db-1
   /validate db-1 db-5
   ```

3. **Plain number**: `N`
   ```bash
   /validate 1
   /validate 1 5
   ```

### Range Specification

When two database numbers are provided, the command validates all databases in the range (inclusive):

```bash
/validate db-1 db-5    # Validates db-1, db-2, db-3, db-4, db-5
/validate 1 3          # Validates db-1, db-2, db-3
```

### All Databases

Use `-a` or `--all` to validate all databases (db-1 through db-15):

```bash
/validate -a
/validate --all
```

## Examples

```bash
# Validate single database
/validate @db/db-1/
/validate db-1
/validate 1

# Validate range of databases
/validate @db/db-1/ @db/db-5/
/validate db-1 db-5
/validate 1 5

# Validate all databases
/validate -a
```

## Validation Phases

The command runs the following phases in order:

1. **Phase 0: Query Abstraction** (REQUIRED)
   - Extracts `queries.md` to `queries.json`
   - Must complete successfully before other phases

2. **Phase 1: Fix Verification**
   - Verifies critical fixes have been applied
   - Checks query formatting and structure

3. **Phase 2 & 4: Syntax Validation and Evaluation**
   - Validates SQL syntax
   - Evaluates queries against requirements

4. **Phase 3: Execution Testing** (Optional)
   - Executes queries on available databases
   - Requires database credentials (skipped if not available)

5. **Phase 5: Report Generation**
   - Generates comprehensive validation reports

## Output

### Console Output

The command provides real-time progress updates:
- Phase completion status
- Error messages (if any)
- Summary statistics

### Files Generated

- **Per-database results**: `db-{N}/results/*.json`
  - `fix_verification.json`
  - `comprehensive_validation_report.json`
  - `query_test_results_postgres.json` (if Phase 3 runs)
  - `final_comprehensive_validation_report.json`

- **Summary report**: `validation_summary.json` (in root directory)
  - Contains overall validation status
  - Summary statistics for all databases
  - Per-database phase results

## Exit Codes

- `0`: All validations passed
- `1`: One or more validations failed
- `2`: Partial validation (some phases skipped)

## Requirements

- Python 3.6+
- Validation scripts in `db-{N}/scripts/` directories
- `queries.md` file in `db-{N}/queries/` directory
- (Optional) Database credentials for Phase 3 execution testing

## Error Handling

If `queries.json` is missing:
- Phase 0 extraction will run automatically
- If extraction fails, validation stops with error
- Other phases will not proceed

If validation scripts are missing:
- Affected phases will be skipped
- Status will show as "PARTIAL"

## Integration with Cursor

The command can be invoked directly in Cursor:
- Type `/validate` followed by arguments
- Cursor will execute the validation script
- Results are displayed in the terminal/output panel

## See Also

- `.cursor/rules/query-validation-suite.mdc` - Complete validation suite documentation
- `.cursor/rules/query-abstraction-requirement.mdc` - Query abstraction requirements
- `scripts/extract_queries_to_json.py` - Query extraction script
