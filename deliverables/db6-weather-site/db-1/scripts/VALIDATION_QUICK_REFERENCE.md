# Query Validation Suite - Quick Reference

## Quick Start

```bash
cd db-1
./scripts/run_full_validation.sh
```

## Individual Phases

### Phase 1: Fix Verification (No DB Required)
```bash
python3 scripts/verify_fixes.py
```

### Phase 2 & 4: Syntax Validation & Evaluation (DB Optional)
```bash
python3 scripts/comprehensive_validator.py
```

### Phase 3: Execution Testing (DB Required)
```bash
python3 scripts/execution_tester.py
```

### Phase 5: Generate Final Report
```bash
python3 scripts/generate_final_report.py
```

## Environment Variables

### PostgreSQL
```bash
export PG_HOST=localhost
export PG_PORT=5432
export PG_USER=postgres
export PG_PASSWORD=your_password
export PG_DATABASE=db_1_validation
```

### Databricks
```bash
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_WAREHOUSE=COMPUTE_WH
export SNOWFLAKE_DATABASE=DB1
export SNOWFLAKE_SCHEMA=PUBLIC
```

## Output Files

- `results/fix_verification.json` - Phase 1 results
- `results/comprehensive_validation_report.json` - Phase 2 & 4 results
- `results/query_test_results_postgres.json` - Phase 3 results
- `results/final_comprehensive_validation_report.json` - Final combined report

## Status Codes

- **PASS**: All checks passed
- **WARNING**: Some warnings, no critical issues
- **FAIL**: Critical issues found

## Common Issues

1. **Missing WITH RECURSIVE**: Query claims recursive CTE but doesn't have it
2. **Array slicing syntax**: PostgreSQL-specific `[start:end]` syntax
3. **Duplicate titles**: Multiple queries with same title
4. **Formatting**: Inconsistent header format

## Full Documentation

See `.cursor/rules/query-validation-suite.mdc` for complete documentation.
