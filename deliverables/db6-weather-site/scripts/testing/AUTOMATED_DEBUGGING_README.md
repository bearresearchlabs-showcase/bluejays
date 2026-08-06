# Automated Query Debugging Tools

## Overview

This directory contains automated debugging tools that offload debugging work to the hardware/machine, running tests, parsing errors, and applying fixes automatically.

## Tools Available

### 1. `auto_test_and_fix.py` - Integrated Test-and-Fix Script

**Purpose**: Runs tests, detects failures, applies fixes automatically, iterates until resolved.

**Usage**:
```bash
# Fix all queries in db-4
python3 scripts/testing/auto_test_and_fix.py --db 4

# Fix specific queries (6-10)
python3 scripts/testing/auto_test_and_fix.py --db 4 --queries 6,7,8,9,10

# Set max iterations per query
python3 scripts/testing/auto_test_and_fix.py --db 4 --max-iterations 10
```

**Features**:
- Automatically tests queries against PostgreSQL
- Detects common error patterns:
  - Type mismatches (AVG/SUM on text, comparisons, CASE, UNION)
  - Missing columns
  - Ambiguous column references
  - GROUP BY issues
  - COALESCE type mismatches
  - Syntax errors
- Applies fixes iteratively (up to max_iterations)
- Updates queries.md files automatically when fixes succeed
- Saves results to JSON files

**Output**:
- Console: Real-time progress and results
- JSON: `db-{N}/results/auto_test_fix_results.json`
- Debug logs: `.cursor/debug.log`

### 2. `automated_query_debugger.py` - Advanced Debugger

**Purpose**: More sophisticated debugging with schema-aware fixes.

**Usage**:
```bash
python3 scripts/testing/automated_query_debugger.py --db 4 --queries 6,7,8,9,10
```

**Features**:
- Schema-aware column resolution
- More sophisticated pattern matching
- Better error analysis

### 3. `batch_auto_debug.sh` - Batch Processing

**Purpose**: Process multiple databases in parallel or sequential mode.

**Usage**:
```bash
# Debug all databases sequentially
./scripts/testing/batch_auto_debug.sh

# Debug specific databases
./scripts/testing/batch_auto_debug.sh --dbs 1,2,3

# Debug specific queries across databases
./scripts/testing/batch_auto_debug.sh --queries 6,7,8,9,10

# Run in parallel (faster)
./scripts/testing/batch_auto_debug.sh --dbs 1,2,3,4,5 --parallel
```

## Common Fix Patterns

The automated tools handle these common patterns:

1. **Type Mismatches**:
   - `AVG(text)` → `AVG(CAST(text AS NUMERIC))`
   - `TEXT > INTEGER` → `CAST(TEXT AS NUMERIC) > INTEGER`
   - `CASE types mismatch` → Cast both branches consistently
   - `UNION types mismatch` → Cast columns to compatible types

2. **Missing Columns**:
   - `category` (db-4) → `chat_id` or `id`
   - `foreign_id` → `id`
   - Comments out columns that don't exist in schema

3. **Ambiguous References**:
   - Qualifies unqualified column names with table aliases

4. **GROUP BY Issues**:
   - Adds missing columns to GROUP BY clauses

5. **Syntax Errors**:
   - Fixes `WHERE.column` → `WHERE column`
   - Fixes double CAST issues

## Limitations

The automated tools work best for:
- ✅ Type casting issues
- ✅ Simple column name replacements
- ✅ GROUP BY additions
- ✅ Ambiguous column qualification

The tools may struggle with:
- ❌ Structural query issues (referencing columns that don't exist in CTEs)
- ❌ Complex logic errors
- ❌ Schema design mismatches
- ❌ Multi-step fixes requiring understanding of query intent

## Workflow Recommendation

1. **Run automated fixer**:
   ```bash
   python3 scripts/testing/auto_test_and_fix.py --db 4
   ```

2. **Review results**:
   ```bash
   cat db-4/results/auto_test_fix_results.json | jq '.failed'
   ```

3. **For queries that still fail**:
   - Check the error messages in the JSON results
   - Review the query structure manually
   - Apply manual fixes for structural issues

4. **Re-run tests**:
   ```bash
   python3 scripts/testing/test_queries_postgres.py
   ```

## Integration with Existing Tools

These tools integrate with:
- `test_queries_postgres.py` - Uses same query parser
- Schema information from PostgreSQL `information_schema`
- Debug logging system (`.cursor/debug.log`)

## Example Output

```
======================================================================
Auto Test-and-Fix: db-4
======================================================================

🔍 Query 6: Production-Grade Partition Rank Analysis...
  ✅ Fixed in 2 iteration(s)

🔍 Query 7: Production-Grade Window Function Analysis...
  ❌ Failed after 3 iteration(s)
     Last error: column "value" does not exist

======================================================================
Summary: 1 fixed, 1 failed
======================================================================
```

## Next Steps

For queries that fail automated fixing:
1. Review the error messages in the results JSON
2. Check the query structure against the schema
3. Apply manual fixes using `search_replace` tool
4. Re-run tests to verify
