# SQL Query Testing Framework

Comprehensive testing framework for validating SQL queries against PostgreSQL.

## Overview

This testing framework:
- Parses all 30 queries from each `db-{N}/queries/queries.md` file
- Tests each query against PostgreSQL
- Generates detailed JSON results files in `db-{N}/results/`
- Records execution time, row counts, errors, and statistics

## Prerequisites

### Python Dependencies

```bash
pip install psycopg2-binary databricks-connector-python
```

### Database Connections

#### PostgreSQL

Set environment variables:
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=db1  # or db2, db3, db4, db5
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
```

#### Databricks

Set environment variables:
```bash
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_WAREHOUSE=COMPUTE_WH
export SNOWFLAKE_DATABASE=DB1  # or DB2, DB3, DB4, DB5
export SNOWFLAKE_SCHEMA=PUBLIC
export SNOWFLAKE_ROLE=ACCOUNTADMIN
```

## Usage

### Run All Tests

```bash
cd scripts/testing
python3 test_queries_postgres.py
```

Or use the shell script:
```bash
./run_query_tests.sh
```

### Test Specific Database

Modify the script to test only specific databases (db-1 through db-5).

## Output

Results are saved to:
- `db-{N}/results/query_test_results_postgres.json`

### Results Format

```json
{
  "database": "db-1",
  "database_number": 1,
  "test_timestamp": "2026-02-03T...",
  "postgresql": {
    "available": true,
    "queries": [
      {
        "query_number": 1,
        "description": "...",
        "success": true,
        "execution_time_ms": 123.45,
        "row_count": 50,
        "columns": ["col1", "col2", ...],
        "error": null
      }
    ],
    "statistics": {
      "total_queries": 30,
      "successful": 28,
      "failed": 2,
      "success_rate": 93.33,
      "avg_execution_time_ms": 234.56,
      "total_rows_returned": 1500
    }
  },
  "databricks": {
    ...
  }
}
```

## Troubleshooting

### Connection Errors

- **PostgreSQL**: Ensure PostgreSQL is running and credentials are correct
- **Databricks**: Verify account, user, password, and warehouse are correct

### Query Parsing Errors

- Ensure `queries.md` files follow the format: `## Query N: Description` followed by ````sql` blocks

### Execution Errors

- Check database schemas match expected structure
- Verify tables exist and have data
- Review error messages in results JSON files
