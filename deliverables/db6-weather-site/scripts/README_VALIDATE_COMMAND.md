# /validate Command

## Quick Start

The `/validate` command provides a unified interface to run the complete validation suite for database repositories.

```bash
# Validate single database
/validate @db/db-1/

# Validate range
/validate @db/db-1/ @db/db-5/

# Validate all databases
/validate -a
```

## Files Created

- **`scripts/validate.py`**: Main validation command script
- **`.cursor/commands/validate.md`**: Cursor command documentation
- **`.cursor/commands/validate.sh`**: Shell wrapper (optional)
- **`scripts/VALIDATE_COMMAND_USAGE.md`**: Complete usage guide

## Features

✅ **Automatic Phase 0**: Extracts `queries.md` to `queries.json` automatically
✅ **Multiple Formats**: Supports `@db/db-N/`, `db-N`, and plain numbers
✅ **Range Support**: Validates multiple databases with range syntax
✅ **All Databases**: Use `-a` flag to validate db-1 through db-15
✅ **Comprehensive**: Runs all 5 validation phases
✅ **Smart Skipping**: Skips Phase 3 if database credentials unavailable
✅ **Summary Reports**: Generates `validation_summary.json` with results

## Usage Examples

```bash
# Single database (multiple formats)
/validate @db/db-1/
/validate db-1
/validate 1

# Range of databases
/validate @db/db-1/ @db/db-5/
/validate db-1 db-5
/validate 1 5

# All databases
/validate -a
/validate --all
```

## Validation Phases

The command runs these phases automatically:

1. **Phase 0**: Extract `queries.md` to `queries.json` (REQUIRED)
2. **Phase 1**: Fix verification
3. **Phase 2 & 4**: Syntax validation and evaluation
4. **Phase 3**: Execution testing (skipped if no DB credentials)
5. **Phase 5**: Generate final report

## Output

- **Per-database**: Results saved to `db-{N}/results/*.json`
- **Summary**: Overall results in `validation_summary.json`
- **Console**: Real-time progress and status updates

## Exit Codes

- `0`: All validations passed
- `1`: One or more validations failed
- `2`: Partial validation (some phases skipped)

## Integration

The command integrates with:
- Cursor IDE (use `/validate` in command palette)
- CI/CD pipelines (call `python3 scripts/validate.py`)
- Manual validation workflows

## Documentation

- **Complete Usage**: See `scripts/VALIDATE_COMMAND_USAGE.md`
- **Validation Suite**: See `.cursor/rules/query-validation-suite.mdc`
- **Command Reference**: See `.cursor/commands/validate.md`
