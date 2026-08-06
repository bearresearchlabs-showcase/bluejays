# SharedAI Database Export

This directory contains a structured export of the **SharedAI PostgreSQL database** hosted on Supabase. SharedAI is a real-time chat application that enables users to communicate with AI tutors and other users in collaborative learning environments.

The export was generated from the live Supabase project (`mwjdnauqugpdagkhzmef`) using the Supabase CLI.

---

## Contents

- `full_dump.sql`
  **Schema only**: DDL including tables, functions, triggers, RLS policies, and indexes. No data.

- `sharedai_data.sql`
  **Data only**: `COPY` statements for all tables. No DDL.

- `sharedai_full_dump.sql`
  Combined **schema + data** in a single file for easy restoration.

- `documentation/SCHEMA.md`
  High-level schema overview, table list, and key relationships.

- `documentation/DATA_DICTIONARY.md`
  Column-level reference for all application tables.

---

## Application Overview

SharedAI is a collaborative learning platform with the following key features:

1. **AI Tutor Conversations**: Users can chat with specialized AI tutors (math, science, language, literature, etc.)
2. **Group Chats**: Multi-user chat rooms with real-time messaging
3. **Anonymous Chats**: Join-code based anonymous chat sessions for quick collaboration
4. **Friend System**: Users can send/accept friend requests
5. **Notifications**: In-app notifications for mentions, friend requests, and chat invites
6. **File Attachments**: Support for sharing files within chats

---

## Requirements

- PostgreSQL 15+ (database was exported from Supabase PostgreSQL 15.8)
- PostgreSQL client tools:

  ```bash
  # macOS
  brew install postgresql

  # Ubuntu/Debian
  sudo apt update && sudo apt install postgresql-client
  ```

---

## Restoring the Database

### Option 1: Full restore (schema + data)

```bash
createdb sharedai_local

psql -d sharedai_local -f sharedai_full_dump.sql
```

### Option 2: Schema and data separately

```bash
createdb sharedai_local

# Load schema first
psql -d sharedai_local -f full_dump.sql

# Then load data
psql -d sharedai_local -f sharedai_data.sql
```

### Notes on Restoration

- The dump includes Supabase-specific extensions (`pg_graphql`, `supabase_vault`, etc.) which may not be available on vanilla PostgreSQL. You can safely ignore errors related to these extensions.
- Row Level Security (RLS) policies are included but require the `auth.uid()` function from Supabase Auth. For local testing, you may need to disable RLS or create stub functions.
- To disable RLS for local testing:
  ```sql
  ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
  ALTER TABLE chats DISABLE ROW LEVEL SECURITY;
  -- etc. for other tables
  ```

---

## Schema & Data Documentation

- See `documentation/SCHEMA.md` for:
  - High-level domains (users, chats, messages, friends, notifications)
  - ERD-style relationships between tables
  - Data flow diagram

- See `documentation/DATA_DICTIONARY.md` for:
  - Table-by-table column descriptions
  - Key constraints and semantics
  - Row counts and data ranges

---

## Data Summary

| Table | Rows | Description |
|-------|------|-------------|
| `profiles` | ~70 | User accounts |
| `chats` | ~100 | Chat rooms |
| `messages` | ~370 | Chat messages (user + AI) |
| `chat_participants` | ~250 | Chat membership |
| `anonymous_chats` | ~70 | Anonymous chat sessions |
| `anonymous_messages` | ~370 | Messages in anonymous chats |
| `friends` | ~10 | Friend relationships |
| `notifications` | ~20 | User notifications |
| `chat_invitations` | ~5 | Pending/accepted chat invites |
| `file_attachments` | ~5 | Uploaded files |

**Data Range**: April 2025 – July 2025 (~3 months of production usage)

---

## How the Export Was Generated

```bash
# Using Supabase CLI v2.72.7
supabase link --project-ref mwjdnauqugpdagkhzmef

# Schema only (from Supabase dashboard SQL export)
# Saved as full_dump.sql

# Data only
supabase db dump --linked --data-only --use-copy -f sharedai_data.sql

# Combined
cat full_dump.sql sharedai_data.sql > sharedai_full_dump.sql
```

---

## License & Usage

This database export is provided for evaluation, training, and research purposes. All personally identifiable information (PII) should be anonymized before use in any public or shared context.
