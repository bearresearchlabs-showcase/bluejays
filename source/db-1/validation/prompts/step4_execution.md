# Step 4: Query Execution

**Task**: Execute queries on a fresh PostgreSQL container.

**Reference files**:
- `db-1/queries/queries.json`
- `db-1/scripts/execution_tester.py`

**Expected output**: All queries execute without error; row counts and timing recorded.

**Pass criteria**: execution_tester.py exits 0; requires PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE.
