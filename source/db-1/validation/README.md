# GDPval-Style Validation

This directory contains prompts and anchors for incremental validation of db-1.

## Structure

- `prompts/` - Prompt for each validation step (step1_schema.md, step2_queries.md, etc.)
- `anchors.yaml` - Reusable check definitions (YAML anchors)

## Incremental Steps

1. **Schema parse** - Validate schema.sql syntax
2. **Queries extract** - queries.json has 30 queries
3. **Query syntax** - EXPLAIN validates all queries
4. **Query execution** - Run on fresh PostgreSQL container
5. **Deliverable completeness** - All required files present
6. **Output check** - client/db deliverable matches expected

## Usage

Run from repo root:

```bash
python3 scripts/gdpval_validation.py 1
python3 scripts/gdpval_validation.py -a
```

Output: `results/gdpval_validation_report.json`

## Copy to Other DBs

To add GDPval validation to db-2 through db-16, copy this directory:

```bash
for n in $(seq 2 16); do
  cp -r db-1/validation db-${n}/
done
```

Then update prompts to reference db-${n} paths.
