# Query Fixing Status

## Current Status
- **Total Queries**: 150 (30 per database)
- **Currently Passing**: 2/150 (1.3%)
- **Remaining**: 148 queries need fixes

## Fixes Applied
1. ✅ Fixed triple/double CAST patterns
2. ✅ Fixed PERCENTILE_CONT with OVER clause
3. ✅ Fixed column name mismatches (uploaded_at → created_at)
4. ✅ Fixed Query 8 max_file_size issue
5. ✅ Fixed syntax errors (redundant COALESCE, etc.)

## Remaining Issues

### Schema Mismatches (~100+ queries)
Many queries reference columns/tables that don't exist in actual schemas:
- Generic columns: `category`, `value`, `date_col`, `parent_id`
- Missing tables: `orders` table in db-2
- Undefined aliases: Table aliases used but not defined

### GROUP BY Errors (~10 queries)
Non-aggregated columns used in SELECT but not in GROUP BY

### Recursive CTE Issues (~5 queries)
Aggregate functions in recursive terms (PostgreSQL limitation)

### Missing FROM Clauses (~15 queries)
Table aliases referenced but not joined

### Undefined Columns (~50+ queries)
Columns referenced that don't exist in tables

## Next Steps
1. Continue fixing syntax errors automatically
2. Address schema mismatches by mapping to actual columns
3. Fix GROUP BY clauses systematically
4. Handle recursive CTE issues
5. Add missing table joins

## Files Created
- `fix_all_queries.py` - Basic syntax fixer
- `comprehensive_query_fixer.py` - Comprehensive iterative fixer
- `scripts/testing/fix_queries_schema_aware.py` - Schema-aware fixer
- `results/actual_schemas.json` - Actual database schemas
- `results/test_summary.json` - Test results summary
