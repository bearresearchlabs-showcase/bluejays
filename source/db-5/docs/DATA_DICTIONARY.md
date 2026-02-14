# SharedAI Data Dictionary

This document lists all application tables and their columns, with types, constraints, and descriptions.

> Types are PostgreSQL types. `timestamptz` = `timestamp with time zone`.

---

## 1. `profiles`

User accounts synced from Supabase Auth. One row per registered user.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | — | User ID (FK to `auth.users.id`) |
| `username` | text | yes | — | Unique username for mentions and display |
| `display_name` | text | yes | — | Display name (can differ from username) |
| `avatar_url` | text | yes | — | URL to profile image (Google OAuth or uploaded) |
| `created_at` | timestamptz | yes | `now()` | When the profile was created |
| `updated_at` | timestamptz | yes | `now()` | Last profile update |
| `ai_character_id` | text | yes | — | Preferred AI character (currently unused) |
| `user_role` | user_role | yes | `'user'` | Role enum: `user` or `admin` |
| `email` | text | yes | — | User's email address |
| `bio` | text | yes | — | User biography/description |
| `last_username_changed_at` | timestamptz | yes | — | When username was last changed (for cooldown) |
| `prompt_username_setup` | boolean | no | `false` | Flag to prompt OAuth users to set username |

**Constraints:**
- Primary key: `id`
- Unique: `username`, `email`
- Foreign key: `id` → `auth.users(id)` ON DELETE CASCADE

**Indexes:**
- Unique index on `email` WHERE `email IS NOT NULL`

**Row count:** ~70
**Data range:** April 2025 – July 2025

---

## 2. `chats`

Chat rooms created by authenticated users.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `uuid_generate_v4()` | Chat room ID |
| `title` | text | yes | — | Chat room title/name |
| `created_at` | timestamptz | no | `now()` | When the chat was created |
| `updated_at` | timestamptz | no | `now()` | Last activity timestamp |
| `current_ai_character_id` | text | yes | — | Active AI tutor for this chat |
| `created_by` | uuid | no | — | User who created the chat |

**Constraints:**
- Primary key: `id`
- Foreign key: `created_by` → `profiles(id)`

**Indexes:**
- `idx_chats_created_by` on `(created_by)`

**AI Character IDs in use:**
- `generic-tutor`, `generic-ai`
- `math-ai`, `science-ai`, `english-ai`, `language-ai`
- `technology-ai`, `art-ai`, `physical-education-ai`
- `physics-professor`, `literature-professor`
- `microsoft-senior-engineer`

**Row count:** ~100
**Data range:** April 2025 – July 2025

---

## 3. `chat_participants`

Many-to-many join between users and chats.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `chat_id` | uuid | **PK** | — | Chat room ID |
| `user_id` | uuid | **PK** | — | User ID |
| `joined_at` | timestamptz | yes | `now()` | When the user joined |

**Constraints:**
- Primary key: `(chat_id, user_id)`
- Foreign key: `user_id` → `profiles(id)` ON DELETE CASCADE

**Row count:** ~250

---

## 4. `messages`

All messages within authenticated chats.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `uuid_generate_v4()` | Message ID |
| `chat_id` | uuid | no | — | Chat this message belongs to |
| `sender_id` | uuid | yes | — | User who sent the message (NULL for AI) |
| `content` | text | no | — | Message text content |
| `is_ai` | boolean | yes | `false` | Whether this is an AI-generated message |
| `ai_character_id` | text | yes | — | Which AI tutor generated this message |
| `created_at` | timestamptz | no | `now()` | When the message was sent |
| `updated_at` | timestamptz | no | `now()` | Last edit timestamp |
| `deleted_at` | timestamptz | yes | — | Soft delete timestamp |
| `mentioned_users` | text[] | yes | — | Array of mentioned usernames (legacy) |
| `is_system_message` | boolean | no | `false` | Whether this is a system notification |
| `mentions_data` | jsonb | yes | `'[]'` | Structured mention data |

**Constraints:**
- Primary key: `id`
- Foreign key: `chat_id` → `chats(id)` ON DELETE CASCADE
- Foreign key: `sender_id` → `profiles(id)` ON DELETE SET NULL

**Indexes:**
- `idx_messages_chat_id` on `(chat_id)`
- `idx_messages_sender_id` on `(sender_id)`
- `idx_messages_created_at` on `(created_at)`
- `idx_messages_ai_character_id` on `(ai_character_id)` WHERE `ai_character_id IS NOT NULL`

**Triggers:**
- `handle_updated_at` — Updates `updated_at` on modification
- `on_new_mention` — Creates notifications when `mentions_data` is populated
- `trigger_update_chat_timestamp` — Updates parent chat's `updated_at`

**Row count:** ~370
**Data range:** April 2025 – July 2025

---

## 5. `chat_invitations`

Invitations for users to join private chats.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `uuid_generate_v4()` | Invitation ID |
| `chat_id` | uuid | no | — | Chat being invited to |
| `inviting_user_id` | uuid | yes | — | User who sent the invitation |
| `invited_user_id` | uuid | yes | — | User being invited |
| `status` | text | yes | `'pending'` | Status: `pending`, `accepted`, `rejected`, `declined`, `expired` |
| `created_at` | timestamptz | yes | `now()` | When invitation was created |
| `updated_at` | timestamptz | yes | `now()` | Last status change |
| `expires_at` | timestamptz | yes | `now() + 7 days` | When invitation expires |

**Constraints:**
- Primary key: `id`
- Check: `status IN ('pending', 'accepted', 'rejected', 'declined', 'expired')`
- Foreign key: `chat_id` → `chats(id)` ON DELETE CASCADE
- Foreign key: `inviting_user_id` → `profiles(id)`
- Foreign key: `invited_user_id` → `profiles(id)`

**Indexes:**
- `idx_chat_invitations_chat_id` on `(chat_id)`

**Row count:** ~5

---

## 6. `chat_users`

Legacy/alternate chat membership table.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `gen_random_uuid()` | Row ID |
| `chat_id` | uuid | no | — | Chat ID |
| `user_id` | uuid | no | — | User ID |
| `created_at` | timestamptz | yes | `now()` | When added |

**Constraints:**
- Primary key: `id`
- Unique: `(chat_id, user_id)`
- Foreign key: `chat_id` → `chats(id)` ON DELETE CASCADE
- Foreign key: `user_id` → `auth.users(id)` ON DELETE CASCADE

**Indexes:**
- `idx_chat_users_chat_id` on `(chat_id)`
- `idx_chat_users_user_id` on `(user_id)`

**Note:** This table appears to be a legacy alternative to `chat_participants`. Both track the same relationship.

---

## 7. `friends`

Friend relationships between users.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `gen_random_uuid()` | Relationship ID |
| `user_id` | uuid | no | — | User who initiated the request |
| `friend_id` | uuid | no | — | User being friended |
| `status` | text | yes | `'pending'` | Status: `pending`, `accepted`, `declined` |
| `created_at` | timestamptz | no | `now()` | When request was created |
| `updated_at` | timestamptz | no | `now()` | Last status change |

**Constraints:**
- Primary key: `id`
- Unique: `(user_id, friend_id)`
- Check: `status IN ('pending', 'accepted', 'declined')`
- Foreign key: `user_id` → `profiles(id)` ON DELETE CASCADE
- Foreign key: `friend_id` → `profiles(id)` ON DELETE CASCADE

**Indexes:**
- `idx_friends_user_id` on `(user_id)`
- `idx_friends_friend_id` on `(friend_id)`
- `idx_friends_status` on `(status)`

**Row count:** ~10

---

## 8. `notifications`

In-app notifications for users.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `gen_random_uuid()` | Notification ID |
| `user_id` | uuid | no | — | User receiving the notification |
| `type` | text | no | — | Type: `friend_request`, `mention`, `chat_invite` |
| `title` | text | no | — | Notification title |
| `message` | text | no | — | Notification body text |
| `data` | jsonb | yes | — | Additional structured data (chatId, messageId, etc.) |
| `created_at` | timestamptz | no | `now()` | When notification was created |
| `read` | boolean | no | `false` | Whether user has read the notification |
| `updated_at` | timestamptz | yes | `now()` | Last update |
| `seen_at` | timestamptz | yes | — | When notification was first seen |

**Constraints:**
- Primary key: `id`
- Check: `type IN ('friend_request', 'mention', 'chat_invite')`
- Foreign key: `user_id` → `profiles(id)` ON DELETE CASCADE

**Indexes:**
- `idx_notifications_user_id` on `(user_id)`
- `idx_notifications_type` on `(type)`
- `idx_notifications_read` on `(read)`
- `idx_notifications_created_at` on `(created_at)`
- `idx_notifications_user_id_created_at` on `(user_id, created_at DESC)`
- `idx_user_unseen_notifications` on `(user_id, seen_at)` WHERE `seen_at IS NULL`

**Row count:** ~20

---

## 9. `file_attachments`

Files uploaded to chats.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `gen_random_uuid()` | Attachment ID |
| `message_id` | uuid | yes | — | Message this file is attached to |
| `chat_id` | uuid | yes | — | Chat this file belongs to |
| `user_id` | uuid | yes | — | User who uploaded the file |
| `file_name` | text | no | — | Original filename |
| `file_size` | integer | no | — | File size in bytes |
| `file_type` | text | no | — | MIME type |
| `file_path` | text | no | — | Storage path/URL |
| `created_at` | timestamptz | no | `now()` | When uploaded |

**Constraints:**
- Primary key: `id`
- Foreign key: `message_id` → `messages(id)` ON DELETE CASCADE
- Foreign key: `chat_id` → `chats(id)` ON DELETE CASCADE
- Foreign key: `user_id` → `auth.users(id)` ON DELETE SET NULL

**Row count:** ~5

---

## 10. `anonymous_chats`

Temporary anonymous chat sessions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `gen_random_uuid()` | Chat session ID |
| `join_code` | text | no | — | 6-character alphanumeric code for joining |
| `created_at` | timestamptz | no | `now()` | When session was created |

**Constraints:**
- Primary key: `id`
- Unique: `join_code`

**Indexes:**
- `idx_anonymous_chats_join_code` on `(join_code)`

**Join Code Format:** 6 uppercase alphanumeric characters (e.g., `A1B2C3`, `XYZ789`)

**Row count:** ~70

---

## 11. `anonymous_chat_users`

Guest participants in anonymous chats.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `uuid_generate_v4()` | Row ID |
| `chat_id` | uuid | yes | — | Anonymous chat session |
| `display_name` | text | no | — | Guest's chosen display name |
| `guest_id` | uuid | no | — | Client-generated UUID for the guest |
| `created_at` | timestamptz | no | `now()` | When guest joined |

**Constraints:**
- Primary key: `id`
- Unique: `(chat_id, guest_id)`
- Foreign key: `chat_id` → `anonymous_chats(id)` ON DELETE CASCADE

**Row count:** ~50

---

## 12. `anonymous_messages`

Messages within anonymous chat sessions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | uuid | **PK** | `gen_random_uuid()` | Message ID |
| `chat_id` | uuid | no | — | Anonymous chat session |
| `sender_display_name` | text | no | — | Display name of sender |
| `content` | text | no | — | Message text |
| `created_at` | timestamptz | no | `now()` | When sent |
| `is_ai` | boolean | no | `false` | Whether AI-generated |
| `ai_character_id` | text | yes | `'default-ai'` | Which AI character responded |

**Constraints:**
- Primary key: `id`
- Foreign key: `chat_id` → `anonymous_chats(id)` ON DELETE CASCADE

**Indexes:**
- `idx_anonymous_messages_chat_id` on `(chat_id)`

**Row count:** ~370

---

## Enum Types

### `user_role`

```sql
CREATE TYPE public.user_role AS ENUM ('user', 'admin');
```

Used in `profiles.user_role` to distinguish regular users from administrators.

---

## Key Functions Reference

### `create_anonymous_chat()`

Creates a new anonymous chat with a unique 6-character join code.

**Returns:** `TABLE(chat_id uuid, join_code text)`

**Logic:**
1. Generates random 6-character alphanumeric code
2. Attempts to insert into `anonymous_chats`
3. Retries up to 5 times on collision
4. Returns the new chat ID and join code

---

### `accept_chat_invitation(invitation_id uuid)`

Accepts a pending chat invitation.

**Logic:**
1. Validates invitation exists and is pending
2. Verifies current user is the invited user
3. Updates invitation status to `accepted`
4. Adds user to `chat_participants`

---

### `leave_chat(p_chat_id uuid)`

Removes the current user from a chat.

**Logic:**
1. Removes user from `chat_participants`
2. If no participants remain, deletes the chat
3. If leaving user was creator, transfers ownership to another participant

---

### `handle_new_user()`

Trigger function called when a new user signs up.

**Logic:**
1. Detects OAuth vs email signup
2. Extracts name/avatar from OAuth metadata
3. Generates temporary username for OAuth users
4. Creates profile record
5. Sets `prompt_username_setup` flag for OAuth users

---

## Sample Query Patterns

### Get all messages in a chat with sender info
```sql
SELECT m.*, p.username, p.display_name, p.avatar_url
FROM messages m
LEFT JOIN profiles p ON m.sender_id = p.id
WHERE m.chat_id = '<chat_uuid>'
ORDER BY m.created_at;
```

### Get user's chats with last message
```sql
SELECT c.*,
       m.content as last_message,
       m.created_at as last_message_at
FROM chats c
JOIN chat_participants cp ON c.id = cp.chat_id
LEFT JOIN LATERAL (
    SELECT content, created_at
    FROM messages
    WHERE chat_id = c.id
    ORDER BY created_at DESC
    LIMIT 1
) m ON true
WHERE cp.user_id = '<user_uuid>'
ORDER BY COALESCE(m.created_at, c.updated_at) DESC;
```

### Get friend list with status
```sql
SELECT p.*, f.status, f.created_at as friends_since
FROM friends f
JOIN profiles p ON (
    CASE WHEN f.user_id = '<user_uuid>' THEN f.friend_id ELSE f.user_id END
) = p.id
WHERE (f.user_id = '<user_uuid>' OR f.friend_id = '<user_uuid>')
  AND f.status = 'accepted';
```
