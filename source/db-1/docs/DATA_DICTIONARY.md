# Data Dictionary - db-1 (Chat Messaging Platform)

Column-level documentation for all tables in the db-1 schema. See `docs/SCHEMA.md` for ER diagrams and relationships.

---

## profiles

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| username | VARCHAR(255) | No | — | Unique username |
| email | VARCHAR(255) | Yes | — | Email address |
| display_name | VARCHAR(255) | Yes | — | Display name |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Account creation |

---

## chats

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| created_by | UUID | Yes | — | FK to profiles(id) |
| title | VARCHAR(255) | Yes | — | Chat title |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Creation time |

---

## messages

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| chat_id | UUID | No | — | FK to chats(id) |
| sender_id | UUID | No | — | FK to profiles(id) |
| is_ai | BOOLEAN | No | FALSE | AI message flag |
| content | TEXT | Yes | — | Message content |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Message time |

---

## chat_participants

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| chat_id | UUID | No | — | FK to chats(id), part of PK |
| user_id | UUID | No | — | FK to profiles(id), part of PK |
| joined_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Join time |

---

## friends

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| user_id | UUID | No | — | FK to profiles(id) |
| friend_id | UUID | No | — | FK to profiles(id) |
| status | VARCHAR(50) | No | 'pending' | pending/accepted/declined |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Request time |

---

## notifications

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| user_id | UUID | No | — | FK to profiles(id) |
| type | VARCHAR(100) | Yes | — | Notification type |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Creation time |
| read | BOOLEAN | Yes | FALSE | Read status |
| seen_at | TIMESTAMP | Yes | — | Seen timestamp |

---

## file_attachments

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| chat_id | UUID | No | — | FK to chats(id) |
| user_id | UUID | No | — | FK to profiles(id) |
| file_name | VARCHAR(255) | Yes | — | Filename |
| file_type | VARCHAR(100) | Yes | — | MIME type |
| file_size | BIGINT | Yes | — | File size in bytes |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Upload time |

---

## anonymous_chats

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| join_code | VARCHAR(50) | Yes | — | Join code |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Creation time |
| expires_at | TIMESTAMP | Yes | — | Expiration |

---

## anonymous_chat_users

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| guest_id | UUID | No | — | Part of composite PK |
| chat_id | UUID | No | — | FK to anonymous_chats(id), part of PK |

---

## anonymous_messages

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| chat_id | UUID | No | — | FK to anonymous_chats(id) |
| guest_id | UUID | No | — | Guest sender (no FK) |
| content | TEXT | Yes | — | Message content |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Message time |

---

## chat_invitations

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | No | gen_random_uuid() | Primary key |
| inviting_user_id | UUID | No | — | FK to profiles(id) |
| invited_user_id | UUID | No | — | FK to profiles(id) |
| chat_id | UUID | No | — | FK to chats(id) |
| status | VARCHAR(50) | No | 'pending' | pending/accepted/declined |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Invitation time |

---

## aircraft_position_history

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | SERIAL | No | — | Primary key |
| hex | VARCHAR(20) | No | — | Aircraft hex code |
| speed | NUMERIC(10,2) | Yes | — | Speed |
| altitude | NUMERIC(10,2) | Yes | — | Altitude |
| timestamp | TIMESTAMP | No | — | Position time |

---

**Last Updated:** 2026-02-14
