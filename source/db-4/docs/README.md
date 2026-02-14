# db-4 SharedAI Models - Database Documentation

## Overview

db-4 is a minimal SharedAI-style analytics database with a single `models` table. All 30 queries operate on `models` for time-series analysis, window functions, and aggregations.

## Quick Start: Restoration

### Prerequisites

- PostgreSQL 14+
- `psql` or equivalent client

### Step-by-Step Restore

1. **Create the database:**
   ```bash
   createdb db4
   ```

2. **Load schema and data:**
   ```bash
   psql -d db4 -f data/schema.sql
   psql -d db4 -f data/data.sql
   ```

3. **Verify:**
   ```bash
   psql -d db4 -c "\dt public.*"
   psql -d db4 -c "SELECT COUNT(*) FROM public.models;"
   ```

## Documentation

- **[SCHEMA.md](SCHEMA.md)**: Table structure and ER diagram
- **[DATA_DICTIONARY.md](DATA_DICTIONARY.md)**: Column definitions for `models`
