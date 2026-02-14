# LinkWay Live Database Export

This directory contains a structured export of the **live LinkWay PostgreSQL database** and accompanying documentation. It is intended for local analysis, backups, and migrations.

The export was generated from the `pipeops` PostgreSQL database using `pg_dump` / `pg_restore` and matches the schema used by the LinkWay backend (Django).

---

## Contents

- `live_db_backup/linkway_live_2026-01-30.dump`  
  Original custom-format `pg_dump` from the live database.

- `database/full_dump.sql`  
  Plain SQL script containing **schema + data** for all tables.

- `database/schema.sql`  
  **DDL only**: `CREATE TABLE`, indexes, constraints, etc. No data.

- `database/data.sql`  
  **Data only**: `INSERT` statements for all tables. No DDL.

- `documentation/SCHEMA.md`  
  High-level schema overview, table list, and key relationships.

- `documentation/DATA_DICTIONARY.md`  
  Column-level reference for the core application tables.

---

## Requirements

- PostgreSQL client tools (for example on Ubuntu):

  ```bash
  sudo apt update
  sudo apt install postgresql-client
  ```

- A running PostgreSQL server (local or remote) where you have:
  - A superuser or owner role to create/restore databases.

---

## Restoring the Database

You can either restore from the **original custom dump** or from the **plain SQL files**.

### Option 1: Restore from the custom dump

Create a new database and restore into it:

```bash
createdb linkway_local

pg_restore \
  --dbname=linkway_local \
  --clean --if-exists \
  live_db_backup/linkway_live_2026-01-30.dump
```

This will recreate the schema and load all data into `linkway_local`.

To restore into a remote instance, add `-h <host> -p <port> -U <user>` as needed.

### Option 2: Restore from `full_dump.sql`

Create a database, then feed the full SQL script into `psql`:

```bash
createdb linkway_local

psql -d linkway_local -f database/full_dump.sql
```

This is functionally equivalent to restoring from the custom dump, but uses the plain SQL script.

### Option 3: Apply schema and data separately

If you want to control when the schema vs data is loaded:

```bash
createdb linkway_local

# Load schema only
psql -d linkway_local -f database/schema.sql

# Then load data
psql -d linkway_local -f database/data.sql
```

---

## How the Export Was Generated

From the project root:

```bash
mkdir -p database documentation

pg_restore -f database/full_dump.sql live_db_backup/linkway_live_2026-01-30.dump
pg_restore -s -f database/schema.sql live_db_backup/linkway_live_2026-01-30.dump
pg_restore -a -f database/data.sql   live_db_backup/linkway_live_2026-01-30.dump
```

All three SQL files are therefore consistent with the `linkway_live_2026-01-30.dump` snapshot.

---

## Schema & Data Documentation

- See `documentation/SCHEMA.md` for:
  - High-level domains (users, products, affiliates, orders, commissions, payouts, payments, analytics, notifications).
  - ERD-style relationships between the main tables.

- See `documentation/DATA_DICTIONARY.md` for:
  - Table-by-table column descriptions.
  - Key constraints and semantics needed for analytics or integration work.

