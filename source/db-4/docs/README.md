# Seydam AI Database Documentation

## 1. Overview
This is the database documentation for the **Seydam AI** application. It details the Postgres database schema, which includes core application data, users (managed via Django and Supabase), payment records, and generated report content.

## 2. Quick Start: Restoration
To set up this database locally or on a new server, follow these instructions.

### Prerequisites
- PostgreSQL 14+ installed.
- Access to `psql` command line tool.
- Superuser privileges (optional, but recommended for extension creation).

### Step-by-Step Restore
1. **Create the Database:**
   ```bash
   createdb seydam_db
   ```

2. **Run the Restoration Script:**
   The `seydam_anonymized_final.sql` file contains the full schema and data.
   ```bash
   psql -d seydam_db -f seydam_anonymized_final.sql
   ```
   *Note: If you encounter errors regarding missing roles (e.g., `postgres`, `anon`, `authenticated`), you may need to create them or ignore the errors if running in a standard local setup.*

3. **Verify Installation:**
   Connect to the database and check the tables:
   ```bash
   psql -d seydam_db -c "\dt"
   ```

## 3. Database Architecture
The database is split into logical schemas:

- **`public`**: The main schema containing the Application Logic.
    - User Profiles (`seydam_customuser`)
    - Reports & Content (`seydam_reports`, `seydam_jsonreport`, `seydam_rawhtmlcode`)
    - Payments & Credits (`seydam_payment`, `seydam_tokenusage`)
- **`auth`**: Managed by **Supabase Auth / GoTrue**. Handles identities, sessions, and MFA. *Do not modify these tables manually.*
- **`storage`**: Managed by **Supabase Storage**. Tracks file buckets and objects (e.g., user uploads).
- **`realtime`**: System schema for websocket broadcasting.

## 4. Documentation Artifacts
For detailed development reference:

- **[SCHEMA.md](SCHEMA.md)**: Visual diagrams and high-level table lists. Use this to understand how tables connect (e.g., User -> Reports -> References).
- **[DATA_DICTIONARY.md](DATA_DICTIONARY.md)**: Low-level column definitions. Use this to look up specific field types and constraints.
