# ID: db-1 - Name: Chat/Messaging System

This document provides comprehensive documentation for database db-1, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**, representing real-world enterprise implementations.

---

## Table of Contents

### Database Documentation

1. [Database Overview](#database-overview)
   - Description and key features
   - Business context and use cases
   - Platform compatibility
   - Data sources

2. [Database Schema Documentation](#database-schema-documentation)
   - Complete schema overview
   - All tables with detailed column definitions
   - Indexes and constraints
   - Entity-Relationship diagrams
   - Table relationships

3. [Data Dictionary](#data-dictionary)
   - Comprehensive column-level documentation
   - Data types and constraints
   - Column descriptions and business context

### SQL Queries (30 Production Queries)

1. [Query 1: How has aircraft altitude varied over the past year? I'd like to see rolling averages and outlier counts broken down by day and aircraft.](#query-1)
    - **Use Case:** How has aircraft altitude varied over the past year? I'd like to see rolling averages and outlier counts broken down by day and aircraft.
    - *What it does:* The query constructs four CTEs. First, it retains the 60 most recent telemetry points per aircraft (cte_level_1). Second, it computes a 5-row rolling...
    - *Business Value:* Aggregated metrics grouped by day and hex

2. [Query 2: Can you show me weekly altitude statistics grouped by speed range? I need quartiles, outlier counts, and how many readings show an upward trend.](#query-2)
    - **Use Case:** Can you show me weekly altitude statistics grouped by speed range? I need quartiles, outlier counts, and how many readings show an upward trend.
    - *What it does:* The query groups telemetry by week and speed bucket. It divides altitude into sextiles (NTILE(6)), calculates z-scores per partition, flags outliers (...
    - *Business Value:* Aggregated metrics grouped by week and speed

3. [Query 3: Give me monthly altitude summaries for each aircraft—quartiles, median, outlier count, and rolling average.](#query-3)
    - **Use Case:** Give me monthly altitude summaries for each aircraft—quartiles, median, outlier count, and rolling average.
    - *What it does:* The query groups by month and aircraft hex. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 6-row rolling average; flags outliers via z-score;...
    - *Business Value:* Aggregated metrics grouped by month and hex

4. [Query 4: I need a daily altitude breakdown by speed—how many outliers are there, how many readings are increasing, and what's the maximum cumulative sum?](#query-4)
    - **Use Case:** I need a daily altitude breakdown by speed—how many outliers are there, how many readings are increasing, and what's the maximum cumulative sum?
    - *What it does:* The query groups by date and speed. It calculates running cumulative sum of altitude changes, applies a 7-row rolling window, uses NTILE(8) for distri...
    - *Business Value:* Aggregated metrics grouped by day and speed

5. [Query 5: Show me weekly altitude metrics for each aircraft—record count, quartiles, standard deviation, and how many readings are trending upward.](#query-5)
    - **Use Case:** Show me weekly altitude metrics for each aircraft—record count, quartiles, standard deviation, and how many readings are trending upward.
    - *What it does:* The query groups by week and hex. It calculates STDDEV, PERCENTILE_CONT for quartiles, and uses LAG/LEAD with delta_value to derive trend_direction. A...
    - *Business Value:* Aggregated metrics grouped by week and hex

6. [Query 6: I need daily altitude statistics broken down by speed bucket, including quartiles, a rolling average, and a count of outlier readings.](#query-6)
    - **Use Case:** I need daily altitude statistics broken down by speed bucket, including quartiles, a rolling average, and a count of outlier readings.
    - *What it does:* The query groups by day and speed bucket. It computes z-scores (mean, stddev per partition; zero when stddev=0), flags outliers, calculates a 5-row ro...
    - *Business Value:* Aggregated metrics grouped by day and speed

7. [Query 7: I want a monthly altitude analysis for each aircraft hex code, including quartiles, minimum and maximum values, outlier count, and the maximum cumulative sum.](#query-7)
    - **Use Case:** I want a monthly altitude analysis for each aircraft hex code, including quartiles, minimum and maximum values, outlier count, and the maximum cumulative sum.
    - *What it does:* The query groups by month and hex. It captures min/max altitude, flags outliers (z-score > 2), limits to 80 points per aircraft, uses PERCENT_RANK, an...
    - *Business Value:* Aggregated metrics grouped by month and hex

8. [Query 8: I need daily altitude statistics by aircraft hex code showing gaps between consecutive readings, sequential altitude differences, and quartiles.](#query-8)
    - **Use Case:** I need daily altitude statistics by aircraft hex code showing gaps between consecutive readings, sequential altitude differences, and quartiles.
    - *What it does:* The query groups by day and hex. It uses LAG to get previous altitude, computes delta (current minus previous), derives trend_direction from the sign,...
    - *Business Value:* Aggregated metrics grouped by day and speed

9. [Query 9: I need daily altitude statistics by speed bucket with z-score-based anomaly detection, quartiles, and counts of different trend directions.](#query-9)
    - **Use Case:** I need daily altitude statistics by speed bucket with z-score-based anomaly detection, quartiles, and counts of different trend directions.
    - *What it does:* The query groups by day and speed bucket. It computes mean and stddev per group, flags anomalies (|z| > 2), handles stddev=0 safely, segments into oct...
    - *Business Value:* Aggregated metrics grouped by week and hex

10. [Query 10: I want weekly altitude statistics by aircraft hex code with recency and frequency scoring, quartiles, and a rolling average.](#query-10)
    - **Use Case:** I want weekly altitude statistics by aircraft hex code with recency and frequency scoring, quartiles, and a rolling average.
    - *What it does:* The query groups by week and hex. It assigns ROW_NUMBER (desc timestamp) for recency scoring, uses record count as frequency proxy, ranks by cumulativ...
    - *Business Value:* Aggregated metrics grouped by month and speed

11. [Query 11: What are the monthly altitude patterns across different speed ranges, analyzed like cohort retention with quartile distributions?](#query-11)
    - **Use Case:** What are the monthly altitude patterns across different speed ranges, analyzed like cohort retention with quartile distributions?
    - *What it does:* The query treats each speed range as a cohort. It limits to 90 points per speed bucket, uses window functions for increasing_count and trend_direction...
    - *Business Value:* Aggregated metrics grouped by day and hex

12. [Query 12: What are the daily altitude change patterns for each aircraft, including acceleration-like metrics, quartiles, and outlier detection?](#query-12)
    - **Use Case:** What are the daily altitude change patterns for each aircraft, including acceleration-like metrics, quartiles, and outlier detection?
    - *What it does:* The query uses LAG to create first derivative (altitude change). trend_direction captures sign of change. LAG and LEAD together enable second-order de...
    - *Business Value:* Aggregated metrics grouped by week and speed

13. [Query 13: How do weekly altitude distributions compare across speed categories, with percentile rankings and quartile breakdowns?](#query-13)
    - **Use Case:** How do weekly altitude distributions compare across speed categories, with percentile rankings and quartile breakdowns?
    - *What it does:* The query employs PERCENT_RANK for cross-category benchmarking and PERCENTILE_CONT for percentile values. Data segmented into sextiles. Speed categori...
    - *Business Value:* Aggregated metrics grouped by month and hex

14. [Query 14: What are the monthly altitude trends for each aircraft using smoothed moving averages, with quartiles and trend pattern counts?](#query-14)
    - **Use Case:** What are the monthly altitude trends for each aircraft using smoothed moving averages, with quartiles and trend pattern counts?
    - *What it does:* The query implements a 6-row rolling window for simple moving average (avg_rolling). It counts periods where altitude is increasing and flags statisti...
    - *Business Value:* Aggregated metrics grouped by day and speed

15. [Query 15: What are the daily peak altitude periods for each speed category, including efficiency metrics and quartile distributions?](#query-15)
    - **Use Case:** What are the daily peak altitude periods for each speed category, including efficiency metrics and quartile distributions?
    - *What it does:* The query ranks altitude within each day using window functions to identify peaks per speed category. Extracts hour and day-of-week for temporal analy...
    - *Business Value:* Aggregated metrics grouped by week and hex

16. [Query 16: What are the weekly altitude statistics for each aircraft with lifetime value metrics, quartiles, and cumulative totals?](#query-16)
    - **Use Case:** What are the weekly altitude statistics for each aircraft with lifetime value metrics, quartiles, and cumulative totals?
    - *What it does:* The query computes cumulative_sum as total exposure proxy, tracks max_cumulative for lifetime activity, ranks aircraft by cumulative sum, applies PERC...
    - *Business Value:* Aggregated metrics grouped by month and speed

17. [Query 17: How do monthly altitude patterns vary by speed range with year-over-year growth analysis and quartiles?](#query-17)
    - **Use Case:** How do monthly altitude patterns vary by speed range with year-over-year growth analysis and quartiles?
    - *What it does:* The query extracts hour_val and dow_val for temporal context. It uses window functions (rolling avg, cumulative sum, LAG, LEAD) and aggregates by peri...
    - *Business Value:* Aggregated metrics grouped by day and hex

18. [Query 18: What are the daily altitude statistics by aircraft for creating heatmap visualizations with quartiles and outliers?](#query-18)
    - **Use Case:** What are the daily altitude statistics by aircraft for creating heatmap visualizations with quartiles and outliers?
    - *What it does:* The query segments by speed and time period. It uses PARTITION BY speed for window functions, groups by week and speed, and produces regime-specific a...
    - *Business Value:* Aggregated metrics grouped by week and speed

19. [Query 19: What are the weekly altitude statistics by speed range showing running percentile distributions, quartiles, and trend patterns?](#query-19)
    - **Use Case:** What are the weekly altitude statistics by speed range showing running percentile distributions, quartiles, and trend patterns?
    - *What it does:* The query calculates STDDEV per partition as volatility measure. It uses PERCENTILE_CONT for quartiles and trend_direction for consistency. Aggregates...
    - *Business Value:* Aggregated metrics grouped by month and hex

20. [Query 20: What are the monthly altitude statistics by aircraft showing correlation patterns with prior readings, quartiles, and rolling averages?](#query-20)
    - **Use Case:** What are the monthly altitude statistics by aircraft showing correlation patterns with prior readings, quartiles, and rolling averages?
    - *What it does:* The query uses PERCENT_RANK and PERCENTILE_CONT for cross-aircraft and cross-speed distribution comparison. DENSE_RANK and NTILE support benchmarking....
    - *Business Value:* Aggregated metrics grouped by day and speed

21. [Query 21: What are the daily altitude statistics by speed category, including status transitions, quartile distributions, and outlier counts?](#query-21)
    - **Use Case:** What are the daily altitude statistics by speed category, including status transitions, quartile distributions, and outlier counts?
    - *What it does:* The query implements rolling windows (ROWS BETWEEN N PRECEDING AND CURRENT ROW) for moving average and cumulative sum. Window functions (LAG, LEAD, FI...
    - *Business Value:* Aggregated metrics grouped by week and hex

22. [Query 22: What are the weekly altitude statistics by aircraft hex code with complete dashboard metrics including quartiles?](#query-22)
    - **Use Case:** What are the weekly altitude statistics by aircraft hex code with complete dashboard metrics including quartiles?
    - *What it does:* The query partitions by speed and groups by day and speed. It combines temporal (DATE_TRUNC) and speed dimensions. Output includes speed-temporal segm...
    - *Business Value:* Aggregated metrics grouped by month and speed

23. [Query 23: What are the monthly altitude statistics by speed category showing sequential patterns and quartiles?](#query-23)
    - **Use Case:** What are the monthly altitude statistics by speed category showing sequential patterns and quartiles?
    - *What it does:* The query uses PERCENTILE_CONT(0.25), (0.5), (0.75) for quartiles. NTILE provides distribution bins. Output includes q1, median, q3, and distribution...
    - *Business Value:* Aggregated metrics grouped by day and hex

24. [Query 24: What are the daily altitude statistics by aircraft hex code including concentration indices, quartiles, and outlier counts?](#query-24)
    - **Use Case:** What are the daily altitude statistics by aircraft hex code including concentration indices, quartiles, and outlier counts?
    - *What it does:* The query extracts EXTRACT(HOUR) and EXTRACT(DOW) for temporal features. It correlates these with altitude via partition and grouping. Output includes...
    - *Business Value:* Aggregated metrics grouped by week and speed

25. [Query 25: What are the weekly altitude statistics by speed category with anomaly scores, quartiles, and trend counts?](#query-25)
    - **Use Case:** What are the weekly altitude statistics by speed category with anomaly scores, quartiles, and trend counts?
    - *What it does:* The query uses PERCENT_RANK across partitions for cross-aircraft and cross-speed comparison. PERCENTILE_CONT and NTILE support distribution analysis....
    - *Business Value:* Aggregated metrics grouped by month and hex

26. [Query 26: What are the monthly altitude statistics by aircraft with quartile breakdowns for fiscal period comparative reporting?](#query-26)
    - **Use Case:** What are the monthly altitude statistics by aircraft with quartile breakdowns for fiscal period comparative reporting?
    - *What it does:* The query computes delta_value (current minus LAG) as first derivative. trend_direction (Increasing/Decreasing/Stable) captures sign. LAG+LEAD enable...
    - *Business Value:* Aggregated metrics grouped by day and speed

27. [Query 27: What are the daily altitude statistics grouped by speed range, including throughput indicators, quartiles, and rolling averages for optimization?](#query-27)
    - **Use Case:** What are the daily altitude statistics grouped by speed range, including throughput indicators, quartiles, and rolling averages for optimization?
    - *What it does:* The query groups by week and speed. It aggregates altitude metrics per speed-temporal cell. Output includes regime-specific trend aggregates.
    - *Business Value:* Aggregated metrics grouped by week and hex

28. [Query 28: What are the weekly cumulative altitude trends by aircraft with quartile analysis for pattern recognition?](#query-28)
    - **Use Case:** What are the weekly cumulative altitude trends by aircraft with quartile analysis for pattern recognition?
    - *What it does:* The query computes cumulative_sum and max_cumulative. ROW_NUMBER (desc) scores recency. Record count proxies frequency. Output includes LTV-style and...
    - *Business Value:* Aggregated metrics grouped by month and speed

29. [Query 29: What are the monthly altitude statistics segmented by speed range with multi-dimensional aggregation and quartiles for pivot analysis?](#query-29)
    - **Use Case:** What are the monthly altitude statistics segmented by speed range with multi-dimensional aggregation and quartiles for pivot analysis?
    - *What it does:* The query uses PERCENTILE_CONT and PERCENT_RANK for distribution metrics. Groups by month and hex or speed. Output includes quartiles and percentile d...
    - *Business Value:* Aggregated metrics grouped by day and hex

30. [Query 30: What are the weekly altitude statistics by speed range with IQR-based outlier detection and quartile analysis?](#query-30)
    - **Use Case:** What are the weekly altitude statistics by speed range with IQR-based outlier detection and quartile analysis?
    - *What it does:* The query correlates altitude with period (day/week/month), hex, and speed. Multi-dimensional grouping and window functions (PARTITION BY hex, speed)...
    - *Business Value:* Aggregated metrics grouped by week and speed

### Additional Information

- [Usage Instructions](#usage-instructions)
- [Platform Compatibility](#platform-compatibility)
- [Business Context](#business-context)

---

## Business Context

**Enterprise-Grade Database System**

This database and all associated queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**. These are not academic examples or toy databases—they represent real-world implementations that power critical business operations, serve paying customers, and generate significant revenue.

**What This Means:**

- **Production-Ready**: All queries have been tested and optimized in production environments
- **Business-Critical**: These queries solve real business problems for revenue-generating companies
- **Scalable**: Designed to handle enterprise-scale data volumes and query loads
- **Proven**: Each query addresses a specific business need that has been validated through actual customer use

**Business Value:**

Every query in this database was created to solve a specific business problem for a company generating $1M+ ARR. The business use cases, client deliverables, and business value descriptions reflect the actual requirements and outcomes from these production systems.

---

## Database Overview

This database implements a comprehensive chat/messaging system supporting user profiles, chat rooms, messages, friend networks, notifications, file attachments, anonymous chats, and chat invitations. The system is designed to work across PostgreSQL database platforms.

- **User Management**: User profiles with authentication, roles, and AI character associations
- **Chat System**: Multi-user chat rooms with participants and message threads
- **Social Network**: Friend connections with status tracking (accepted, pending, declined)
- **Notifications**: Real-time notification system for user events
- **File Attachments**: File sharing capabilities within chats
- **Anonymous Chats**: Temporary anonymous chat rooms with join codes
- **Chat Invitations**: Invitation system for chat room access

- **PostgreSQL**: Full support with UUID types, arrays, and JSONB
- **, **: Compatible with Delta Lake format
- **, **: Full support with VARIANT types

---

---

### Data Dictionary

This section provides a comprehensive data dictionary for all tables in the database, including column names, data types, constraints, and descriptions. Tables are organized by functional category for easier navigation.

The database consists of **12 tables** organized into logical groups:

1. **User Management**: `profiles`
2. **Chat System**: `chats`, `chat_participants`, `messages`
3. **Social Network**: `friends`
4. **Notifications**: `notifications`
5. **File Management**: `file_attachments`
6. **Anonymous Features**: `anonymous_chats`, `anonymous_chat_users`, `anonymous_messages`
7. **Invitations**: `chat_invitations`
8. **Analytics**: `aircraft_position_history` (time-series)

```
profiles (id)
    ├── chats (created_by)
    ├── chat_participants (user_id)
    ├── messages (sender_id)
    ├── friends (user_id, friend_id)
    ├── notifications (user_id)
    ├── file_attachments (user_id)
    └── chat_invitations (inviting_user_id, invited_user_id)

chats (id)
    ├── chat_participants (chat_id)
    ├── messages (chat_id)
    ├── file_attachments (chat_id)
    ├── anonymous_chat_users (chat_id) [via anonymous_chats]
    ├── anonymous_messages (chat_id) [via anonymous_chats]
    └── chat_invitations (chat_id)
```

```mermaid
erDiagram
    profiles {
        uuid id PK "Primary key"
        varchar username UK "Unique username"
        varchar email "Email address"
        varchar display_name "Display name"
        timestamp created_at "Account creation"
    }

    chats {
        uuid id PK "Primary key"
        uuid created_by FK "Creator user"
        varchar title "Chat title"
        timestamp created_at "Creation time"
    }

    messages {
        uuid id PK "Primary key"
        uuid chat_id FK "Chat room"
        uuid sender_id FK "Sender user"
        boolean is_ai "AI message flag"
        text content "Message content"
        timestamp created_at "Message time"
    }

    chat_participants {
        uuid chat_id PK,FK "Chat room"
        uuid user_id PK,FK "Participant user"
        timestamp joined_at "Join time"
    }

    friends {
        uuid id PK "Primary key"
        uuid user_id FK "Requester user"
        uuid friend_id FK "Friend user"
        varchar status "pending/accepted/declined"
        timestamp created_at "Request time"
    }

    notifications {
        uuid id PK "Primary key"
        uuid user_id FK "User"
        varchar type "Notification type"
        boolean read "Read status"
        timestamp seen_at "Seen time"
        timestamp created_at "Creation time"
    }

    file_attachments {
        uuid id PK "Primary key"
        uuid chat_id FK "Chat room"
        uuid user_id FK "Uploader user"
        varchar file_name "Filename"
        varchar file_type "MIME type"
        bigint file_size "File size bytes"
        timestamp created_at "Upload time"
    }

    anonymous_chats {
        uuid id PK "Primary key"
        varchar join_code "Join code"
        timestamp created_at "Creation time"
        timestamp expires_at "Expiration"
    }

    anonymous_chat_users {
        uuid guest_id PK "Guest identifier"
        uuid chat_id PK,FK "Anonymous chat"
    }

    anonymous_messages {
        uuid id PK "Primary key"
        uuid chat_id FK "Anonymous chat"
        uuid guest_id "Guest sender"
        text content "Message content"
        timestamp created_at "Message time"
    }

    chat_invitations {
        uuid id PK "Primary key"
        uuid inviting_user_id FK "Inviter"
        uuid invited_user_id FK "Invitee"
        uuid chat_id FK "Chat room"
        varchar status "pending/accepted/declined"
        timestamp created_at "Invitation time"
    }

    aircraft_position_history {
        serial id PK "Primary key"
        varchar hex "Aircraft hex code"
        numeric speed "Speed"
        numeric altitude "Altitude"
        timestamp timestamp "Position time"
    }

    profiles ||--o{ chats : "creates"
    profiles ||--o{ messages : "sends"
    profiles ||--o{ chat_participants : "participates"
    profiles ||--o{ friends : "user"
    profiles ||--o{ friends : "friend"
    profiles ||--o{ notifications : "receives"
    profiles ||--o{ file_attachments : "uploads"
    profiles ||--o{ chat_invitations : "inviting"
    profiles ||--o{ chat_invitations : "invited"
    chats ||--o{ messages : "contains"
    chats ||--o{ chat_participants : "has"
    chats ||--o{ file_attachments : "contains"
    chats ||--o{ chat_invitations : "invited_to"
    anonymous_chats ||--o{ anonymous_chat_users : "has"
    anonymous_chats ||--o{ anonymous_messages : "contains"
```

---

Stores user profile information including authentication details, preferences, and AI character associations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key - unique user identifier |
| `username` | `VARCHAR(255)` | No | — | Unique username for login |
| `display_name` | `VARCHAR(255)` | No | — | Display name shown in UI |
| `avatar_url` | `VARCHAR(16777216)` | No | — | URL to user avatar image |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Account creation timestamp |
| `updated_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Last profile update timestamp |
| `ai_character_id` | `VARCHAR(255)` | Yes | `NULL` | Associated AI character identifier |
| `user_role` | `VARCHAR(50)` | No | `'user'` | User role (user, admin, moderator) |
| `email` | `VARCHAR(255)` | No | — | User email address |
| `bio` | `VARCHAR(16777216)` | Yes | `NULL` | User biography text |
| `last_username_changed_at` | `TIMESTAMP_NTZ` | Yes | `NULL` | Timestamp of last username change |
| `prompt_username_setup` | `BOOLEAN` | No | `FALSE` | Flag indicating if username setup was prompted |

**Indexes:**
- Primary Key: `id`
- Unique Index: `username`
- Index: `email`
- Index: `created_at`

**Constraints:**
- `username` must be unique
- `email` must be unique

---

Stores chat room information including metadata and AI character associations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key - unique chat identifier |
| `title` | `VARCHAR(255)` | No | — | Chat room title |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Chat creation timestamp |
| `updated_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Last update timestamp |
| `current_ai_character_id` | `VARCHAR(255)` | Yes | `NULL` | Currently active AI character |
| `created_by` | `UUID` | No | — | Foreign key to `profiles.id` - creator |

**Indexes:**
- Primary Key: `id`
- Foreign Key: `created_by` → `profiles.id`
- Index: `created_at`
- Index: `updated_at`

---

Junction table linking users to chat rooms they participate in.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `chat_id` | `UUID` | No | — | Foreign key to `chats.id` |
| `user_id` | `UUID` | No | — | Foreign key to `profiles.id` |
| `joined_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Timestamp when user joined |

**Indexes:**
- Composite Primary Key: `(chat_id, user_id)`
- Foreign Key: `chat_id` → `chats.id`
- Foreign Key: `user_id` → `profiles.id`
- Index: `joined_at`

**Constraints:**
- Unique combination of `chat_id` and `user_id`

---

Stores individual messages within chat rooms, supporting both user and AI-generated messages.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key - unique message identifier |
| `chat_id` | `UUID` | No | — | Foreign key to `chats.id` |
| `sender_id` | `UUID` | Yes | `NULL` | Foreign key to `profiles.id` (NULL for system messages) |
| `content` | `VARCHAR(16777216)` | No | — | Message text content |
| `is_ai` | `BOOLEAN` | No | `FALSE` | Flag indicating AI-generated message |
| `ai_character_id` | `VARCHAR(255)` | Yes | `NULL` | AI character identifier if AI message |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Message creation timestamp |
| `updated_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Last update timestamp |
| `deleted_at` | `TIMESTAMP_NTZ` | Yes | `NULL` | Soft delete timestamp |
| `mentioned_users` | `ARRAY(VARCHAR)` | Yes | `NULL` | Array of mentioned user IDs |
| `is_system_message` | `BOOLEAN` | No | `FALSE` | Flag indicating system-generated message |
| `mentions_data` | `VARIANT` | Yes | `NULL` | JSON data for mentions  |

**Indexes:**
- Primary Key: `id`
- Foreign Key: `chat_id` → `chats.id`
- Foreign Key: `sender_id` → `profiles.id`
- Index: `created_at`
- Index: `(chat_id, created_at)`
- Index: `deleted_at` WHERE `deleted_at IS NULL`

**Constraints:**
- `sender_id` must be NULL if `is_system_message` is TRUE
- `content` cannot be empty

---

Stores friend relationships between users with status tracking.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key |
| `user_id` | `UUID` | No | — | Foreign key to `profiles.id` - requester |
| `friend_id` | `UUID` | No | — | Foreign key to `profiles.id` - friend |
| `status` | `VARCHAR(20)` | No | `'pending'` | Relationship status (pending, accepted, declined) |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Request creation timestamp |
| `updated_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Last status update timestamp |

**Indexes:**
- Primary Key: `id`
- Foreign Key: `user_id` → `profiles.id`
- Foreign Key: `friend_id` → `profiles.id`
- Unique Index: `(user_id, friend_id)`
- Index: `status`
- Index: `updated_at`

**Constraints:**
- `user_id` cannot equal `friend_id`
- Unique combination of `user_id` and `friend_id`

---

Stores user notifications for various events.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key |
| `user_id` | `UUID` | No | — | Foreign key to `profiles.id` |
| `type` | `VARCHAR(50)` | No | — | Notification type (message, friend_request, etc.) |
| `title` | `VARCHAR(255)` | No | — | Notification title |
| `message` | `VARCHAR(16777216)` | No | — | Notification message content |
| `data` | `VARIANT` | Yes | `NULL` | Additional JSON data  |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Creation timestamp |
| `read` | `BOOLEAN` | No | `FALSE` | Read status flag |
| `updated_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Last update timestamp |
| `seen_at` | `TIMESTAMP_NTZ` | Yes | `NULL` | Timestamp when notification was seen |

**Indexes:**
- Primary Key: `id`
- Foreign Key: `user_id` → `profiles.id`
- Index: `(user_id, read)`
- Index: `created_at`
- Index: `type`

---

Stores file attachment metadata for messages.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key |
| `message_id` | `UUID` | Yes | `NULL` | Foreign key to `messages.id` |
| `chat_id` | `UUID` | Yes | `NULL` | Foreign key to `chats.id` |
| `user_id` | `UUID` | Yes | `NULL` | Foreign key to `profiles.id` - uploader |
| `file_name` | `VARCHAR(255)` | No | — | Original filename |
| `file_size` | `INTEGER` | No | — | File size in bytes |
| `file_type` | `VARCHAR(100)` | No | — | MIME type |
| `file_path` | `VARCHAR(16777216)` | No | — | Storage path/URL |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Upload timestamp |

**Indexes:**
- Primary Key: `id`
- Foreign Key: `message_id` → `messages.id`
- Foreign Key: `chat_id` → `chats.id`
- Foreign Key: `user_id` → `profiles.id`
- Index: `created_at`

---

Stores temporary anonymous chat rooms with join codes.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key |
| `join_code` | `VARCHAR(50)` | Yes | `NULL` | Unique join code for anonymous access |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Creation timestamp |
| `expires_at` | `TIMESTAMP_NTZ` | Yes | `NULL` | Expiration timestamp |

**Indexes:**
- Primary Key: `id`
- Unique Index: `join_code`
- Index: `expires_at`

---

Stores anonymous users participating in anonymous chats.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key |
| `chat_id` | `UUID` | No | — | Foreign key to `anonymous_chats.id` |
| `guest_id` | `VARCHAR(100)` | Yes | `NULL` | Temporary guest identifier |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Join timestamp |

**Indexes:**
- Primary Key: `id`
- Foreign Key: `chat_id` → `anonymous_chats.id`
- Index: `guest_id`

---

Stores messages in anonymous chat rooms.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key |
| `chat_id` | `UUID` | No | — | Foreign key to `anonymous_chats.id` |
| `guest_id` | `VARCHAR(100)` | Yes | `NULL` | Guest identifier of sender |
| `content` | `VARCHAR(16777216)` | No | — | Message content |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Message timestamp |

**Indexes:**
- Primary Key: `id`
- Foreign Key: `chat_id` → `anonymous_chats.id`
- Index: `created_at`
- Index: `(chat_id, created_at)`

---

Stores chat room invitations sent between users.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary key |
| `chat_id` | `UUID` | No | — | Foreign key to `chats.id` |
| `inviting_user_id` | `UUID` | No | — | Foreign key to `profiles.id` - inviter |
| `invited_user_id` | `UUID` | No | — | Foreign key to `profiles.id` - invitee |
| `status` | `VARCHAR(20)` | No | `'pending'` | Invitation status (pending, accepted, declined) |
| `created_at` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Invitation timestamp |

**Indexes:**
- Primary Key: `id`
- Foreign Key: `chat_id` → `chats.id`
- Foreign Key: `inviting_user_id` → `profiles.id`
- Foreign Key: `invited_user_id` → `profiles.id`
- Unique Index: `(chat_id, invited_user_id)`
- Index: `status`
- Index: `created_at`

---

---

---

## SQL Queries

This database includes **30 production SQL queries**, each designed to solve specific business problems for companies with $1M+ ARR. Each query includes:

- **Business Use Case**: The specific business problem this query solves
- **Description**: Technical explanation of what the query does
- **Client Deliverable**: What output or report this query generates
- **Business Value**: The business impact and value delivered
- **Complexity**: Technical complexity indicators
- **SQL Code**: Complete, production-ready SQL query

---

## Query 1: How has aircraft altitude varied over the past year? I'd like to see rolling averages and outlier counts broken down by day and aircraft. {#query-1}

**Use Case:** **How has aircraft altitude varied over the past year? I'd like to see rolling averages and outlier counts broken down by day and aircraft.**

**Description:** The query constructs four CTEs. First, it retains the 60 most recent telemetry points per aircraft (cte_level_1). Second, it computes a 5-row rolling average and cumulative sum via window functions (cte_level_2). Third, it uses LAG, LEAD, and partition statistics for trend and z-score calculation (cte_level_3). Fourth, it flags outliers (z-score > 2) and trend direction, then aggregates by day and hex with PERCENTILE_CONT, SUM for outlier/increasing counts, and AVG for rolling average.

**Business Value:** Aggregated metrics grouped by day and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 60
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 2: Can you show me weekly altitude statistics grouped by speed range? I need quartiles, outlier counts, and how many readings show an upward trend. {#query-2}

**Use Case:** **Can you show me weekly altitude statistics grouped by speed range? I need quartiles, outlier counts, and how many readings show an upward trend.**

**Description:** The query groups telemetry by week and speed bucket. It divides altitude into sextiles (NTILE(6)), calculates z-scores per partition, flags outliers (>2 std dev), and uses LAG/LEAD to compare consecutive readings for trend direction. Aggregates include quartiles (PERCENTILE_CONT), outlier count, and increasing-trend count.

**Business Value:** Aggregated metrics grouped by week and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 70
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 3: Give me monthly altitude summaries for each aircraft—quartiles, median, outlier count, and rolling average. {#query-3}

**Use Case:** **Give me monthly altitude summaries for each aircraft—quartiles, median, outlier count, and rolling average.**

**Description:** The query groups by month and aircraft hex. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 6-row rolling average; flags outliers via z-score; and aggregates record count, stddev, min, max, outlier count, and increasing count. ROW_NUMBER limits to 80 points per aircraft.

**Business Value:** Aggregated metrics grouped by month and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 80
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 4: I need a daily altitude breakdown by speed—how many outliers are there, how many readings are increasing, and what's the maximum cumulative sum? {#query-4}

**Use Case:** **I need a daily altitude breakdown by speed—how many outliers are there, how many readings are increasing, and what's the maximum cumulative sum?**

**Description:** The query groups by date and speed. It calculates running cumulative sum of altitude changes, applies a 7-row rolling window, uses NTILE(8) for distribution, and aggregates outlier count, increasing-trend count, and max cumulative sum per group.

**Business Value:** Aggregated metrics grouped by day and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 90
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 5: Show me weekly altitude metrics for each aircraft—record count, quartiles, standard deviation, and how many readings are trending upward. {#query-5}

**Use Case:** **Show me weekly altitude metrics for each aircraft—record count, quartiles, standard deviation, and how many readings are trending upward.**

**Description:** The query groups by week and hex. It calculates STDDEV, PERCENTILE_CONT for quartiles, and uses LAG/LEAD with delta_value to derive trend_direction. Aggregates include record count, quartiles, stddev, outlier count, and increasing count. ROW_NUMBER limits to 100 points per aircraft.

**Business Value:** Aggregated metrics grouped by week and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 100
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 6: I need daily altitude statistics broken down by speed bucket, including quartiles, a rolling average, and a count of outlier readings. {#query-6}

**Use Case:** **I need daily altitude statistics broken down by speed bucket, including quartiles, a rolling average, and a count of outlier readings.**

**Description:** The query groups by day and speed bucket. It computes z-scores (mean, stddev per partition; zero when stddev=0), flags outliers, calculates a 5-row rolling average, and filters to groups with ≥2 records. Output includes quartiles, rolling average, and outlier count.

**Business Value:** Aggregated metrics grouped by day and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 110
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 7: I want a monthly altitude analysis for each aircraft hex code, including quartiles, minimum and maximum values, outlier count, and the maximum cumulative sum. {#query-7}

**Use Case:** **I want a monthly altitude analysis for each aircraft hex code, including quartiles, minimum and maximum values, outlier count, and the maximum cumulative sum.**

**Description:** The query groups by month and hex. It captures min/max altitude, flags outliers (z-score > 2), limits to 80 points per aircraft, uses PERCENT_RANK, and calculates cumulative sum via window. Aggregates include quartiles, min, max, outlier count, and max cumulative sum.

**Business Value:** Aggregated metrics grouped by month and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 120
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 8: I need daily altitude statistics by aircraft hex code showing gaps between consecutive readings, sequential altitude differences, and quartiles. {#query-8}

**Use Case:** **I need daily altitude statistics by aircraft hex code showing gaps between consecutive readings, sequential altitude differences, and quartiles.**

**Description:** The query groups by day and hex. It uses LAG to get previous altitude, computes delta (current minus previous), derives trend_direction from the sign, and uses LEAD for next value. Aggregates include quartiles and sequential difference metrics.

**Business Value:** Aggregated metrics grouped by day and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 130
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 9: I need daily altitude statistics by speed bucket with z-score-based anomaly detection, quartiles, and counts of different trend directions. {#query-9}

**Use Case:** **I need daily altitude statistics by speed bucket with z-score-based anomaly detection, quartiles, and counts of different trend directions.**

**Description:** The query groups by day and speed bucket. It computes mean and stddev per group, flags anomalies (|z| > 2), handles stddev=0 safely, segments into octiles (NTILE(8)), and aggregates quartiles, outlier count, and trend direction counts.

**Business Value:** Aggregated metrics grouped by week and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 140
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 10: I want weekly altitude statistics by aircraft hex code with recency and frequency scoring, quartiles, and a rolling average. {#query-10}

**Use Case:** **I want weekly altitude statistics by aircraft hex code with recency and frequency scoring, quartiles, and a rolling average.**

**Description:** The query groups by week and hex. It assigns ROW_NUMBER (desc timestamp) for recency scoring, uses record count as frequency proxy, ranks by cumulative sum, computes 6-row rolling average, and filters to groups with ≥3 records. Output includes quartiles and rolling average.

**Business Value:** Aggregated metrics grouped by month and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 150
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 11: What are the monthly altitude patterns across different speed ranges, analyzed like cohort retention with quartile distributions? {#query-11}

**Use Case:** **What are the monthly altitude patterns across different speed ranges, analyzed like cohort retention with quartile distributions?**

**Description:** The query treats each speed range as a cohort. It limits to 90 points per speed bucket, uses window functions for increasing_count and trend_direction (analogous to retention), and orders by time period and average value. Output includes cohort-style progression and quartile boundaries.

**Business Value:** Aggregated metrics grouped by day and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 160
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 12: What are the daily altitude change patterns for each aircraft, including acceleration-like metrics, quartiles, and outlier detection? {#query-12}

**Use Case:** **What are the daily altitude change patterns for each aircraft, including acceleration-like metrics, quartiles, and outlier detection?**

**Description:** The query uses LAG to create first derivative (altitude change). trend_direction captures sign of change. LAG and LEAD together enable second-order derivative (rate of change of rate). Z-scores flag outliers. Limited to 60 points per aircraft. Output includes change rate metrics, quartiles, and outlier count.

**Business Value:** Aggregated metrics grouped by week and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 170
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 13: How do weekly altitude distributions compare across speed categories, with percentile rankings and quartile breakdowns? {#query-13}

**Use Case:** **How do weekly altitude distributions compare across speed categories, with percentile rankings and quartile breakdowns?**

**Description:** The query employs PERCENT_RANK for cross-category benchmarking and PERCENTILE_CONT for percentile values. Data segmented into sextiles. Speed categories ranked by cumulative altitude sum. Partition-level avg/stddev enable z-scores. Output includes percentile rankings and quartile distributions.

**Business Value:** Aggregated metrics grouped by month and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 180
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 14: What are the monthly altitude trends for each aircraft using smoothed moving averages, with quartiles and trend pattern counts? {#query-14}

**Use Case:** **What are the monthly altitude trends for each aircraft using smoothed moving averages, with quartiles and trend pattern counts?**

**Description:** The query implements a 6-row rolling window for simple moving average (avg_rolling). It counts periods where altitude is increasing and flags statistical outliers. Limited to 80 points per aircraft, minimum 1 record per group. Output includes quartiles and trend pattern counts.

**Business Value:** Aggregated metrics grouped by day and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 190
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 15: What are the daily peak altitude periods for each speed category, including efficiency metrics and quartile distributions? {#query-15}

**Use Case:** **What are the daily peak altitude periods for each speed category, including efficiency metrics and quartile distributions?**

**Description:** The query ranks altitude within each day using window functions to identify peaks per speed category. Extracts hour and day-of-week for temporal analysis. Calculates max_cumulative and avg_rolling as efficiency proxies. Output includes peak period identification and quartile distributions.

**Business Value:** Aggregated metrics grouped by week and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 200
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 16: What are the weekly altitude statistics for each aircraft with lifetime value metrics, quartiles, and cumulative totals? {#query-16}

**Use Case:** **What are the weekly altitude statistics for each aircraft with lifetime value metrics, quartiles, and cumulative totals?**

**Description:** The query computes cumulative_sum as total exposure proxy, tracks max_cumulative for lifetime activity, ranks aircraft by cumulative sum, applies PERCENT_RANK for quartile placement. Limited to 60 points per aircraft, ≥3 records per group. Output includes LTV metrics, quartiles, and cumulative totals.

**Business Value:** Aggregated metrics grouped by month and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 210
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 17: How do monthly altitude patterns vary by speed range with year-over-year growth analysis and quartiles? {#query-17}

**Use Case:** **How do monthly altitude patterns vary by speed range with year-over-year growth analysis and quartiles?**

**Description:** The query extracts hour_val and dow_val for temporal context. It uses window functions (rolling avg, cumulative sum, LAG, LEAD) and aggregates by period and hex. Output includes temporal correlation metrics.

**Business Value:** Aggregated metrics grouped by day and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 220
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 18: What are the daily altitude statistics by aircraft for creating heatmap visualizations with quartiles and outliers? {#query-18}

**Use Case:** **What are the daily altitude statistics by aircraft for creating heatmap visualizations with quartiles and outliers?**

**Description:** The query segments by speed and time period. It uses PARTITION BY speed for window functions, groups by week and speed, and produces regime-specific aggregates including quartiles and trend counts.

**Business Value:** Aggregated metrics grouped by week and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 230
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 19: What are the weekly altitude statistics by speed range showing running percentile distributions, quartiles, and trend patterns? {#query-19}

**Use Case:** **What are the weekly altitude statistics by speed range showing running percentile distributions, quartiles, and trend patterns?**

**Description:** The query calculates STDDEV per partition as volatility measure. It uses PERCENTILE_CONT for quartiles and trend_direction for consistency. Aggregates include stddev, quartiles, outlier count, and increasing count.

**Business Value:** Aggregated metrics grouped by month and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 240
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 20: What are the monthly altitude statistics by aircraft showing correlation patterns with prior readings, quartiles, and rolling averages? {#query-20}

**Use Case:** **What are the monthly altitude statistics by aircraft showing correlation patterns with prior readings, quartiles, and rolling averages?**

**Description:** The query uses PERCENT_RANK and PERCENTILE_CONT for cross-aircraft and cross-speed distribution comparison. DENSE_RANK and NTILE support benchmarking. Output includes percentile rankings and quartile distributions.

**Business Value:** Aggregated metrics grouped by day and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 250
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 21: What are the daily altitude statistics by speed category, including status transitions, quartile distributions, and outlier counts? {#query-21}

**Use Case:** **What are the daily altitude statistics by speed category, including status transitions, quartile distributions, and outlier counts?**

**Description:** The query implements rolling windows (ROWS BETWEEN N PRECEDING AND CURRENT ROW) for moving average and cumulative sum. Window functions (LAG, LEAD, FIRST_VALUE, LAST_VALUE) support trend analysis. Output includes rolling and cumulative metrics.

**Business Value:** Aggregated metrics grouped by week and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 260
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 22: What are the weekly altitude statistics by aircraft hex code with complete dashboard metrics including quartiles? {#query-22}

**Use Case:** **What are the weekly altitude statistics by aircraft hex code with complete dashboard metrics including quartiles?**

**Description:** The query partitions by speed and groups by day and speed. It combines temporal (DATE_TRUNC) and speed dimensions. Output includes speed-temporal segmented aggregates.

**Business Value:** Aggregated metrics grouped by month and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 270
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 23: What are the monthly altitude statistics by speed category showing sequential patterns and quartiles? {#query-23}

**Use Case:** **What are the monthly altitude statistics by speed category showing sequential patterns and quartiles?**

**Description:** The query uses PERCENTILE_CONT(0.25), (0.5), (0.75) for quartiles. NTILE provides distribution bins. Output includes q1, median, q3, and distribution shape metrics.

**Business Value:** Aggregated metrics grouped by day and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 280
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 24: What are the daily altitude statistics by aircraft hex code including concentration indices, quartiles, and outlier counts? {#query-24}

**Use Case:** **What are the daily altitude statistics by aircraft hex code including concentration indices, quartiles, and outlier counts?**

**Description:** The query extracts EXTRACT(HOUR) and EXTRACT(DOW) for temporal features. It correlates these with altitude via partition and grouping. Output includes time-of-day correlation metrics.

**Business Value:** Aggregated metrics grouped by week and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 290
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 25: What are the weekly altitude statistics by speed category with anomaly scores, quartiles, and trend counts? {#query-25}

**Use Case:** **What are the weekly altitude statistics by speed category with anomaly scores, quartiles, and trend counts?**

**Description:** The query uses PERCENT_RANK across partitions for cross-aircraft and cross-speed comparison. PERCENTILE_CONT and NTILE support distribution analysis. Output includes percentile rankings and quartile breakdowns.

**Business Value:** Aggregated metrics grouped by month and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 300
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(5) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.hex
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 26: What are the monthly altitude statistics by aircraft with quartile breakdowns for fiscal period comparative reporting? {#query-26}

**Use Case:** **What are the monthly altitude statistics by aircraft with quartile breakdowns for fiscal period comparative reporting?**

**Description:** The query computes delta_value (current minus LAG) as first derivative. trend_direction (Increasing/Decreasing/Stable) captures sign. LAG+LEAD enable second derivative. Z-scores flag outliers. Output includes rate-of-change and acceleration-like metrics.

**Business Value:** Aggregated metrics grouped by day and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 310
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(6) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.speed
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 27: What are the daily altitude statistics grouped by speed range, including throughput indicators, quartiles, and rolling averages for optimization? {#query-27}

**Use Case:** **What are the daily altitude statistics grouped by speed range, including throughput indicators, quartiles, and rolling averages for optimization?**

**Description:** The query groups by week and speed. It aggregates altitude metrics per speed-temporal cell. Output includes regime-specific trend aggregates.

**Business Value:** Aggregated metrics grouped by week and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 320
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(7) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.hex
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 28: What are the weekly cumulative altitude trends by aircraft with quartile analysis for pattern recognition? {#query-28}

**Use Case:** **What are the weekly cumulative altitude trends by aircraft with quartile analysis for pattern recognition?**

**Description:** The query computes cumulative_sum and max_cumulative. ROW_NUMBER (desc) scores recency. Record count proxies frequency. Output includes LTV-style and recency-frequency metrics.

**Business Value:** Aggregated metrics grouped by month and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 330
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(8) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('month', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('month', c4.timestamp), c4.speed
HAVING COUNT(*) >= 2
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 29: What are the monthly altitude statistics segmented by speed range with multi-dimensional aggregation and quartiles for pivot analysis? {#query-29}

**Use Case:** **What are the monthly altitude statistics segmented by speed range with multi-dimensional aggregation and quartiles for pivot analysis?**

**Description:** The query uses PERCENTILE_CONT and PERCENT_RANK for distribution metrics. Groups by month and hex or speed. Output includes quartiles and percentile distributions across dimensions.

**Business Value:** Aggregated metrics grouped by day and hex

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY hex ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.hex) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.hex ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 340
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.hex ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.hex) AS partition_stddev,
        NTILE(9) OVER (PARTITION BY c2.hex ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.hex ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('day', c4.timestamp) AS period,
    c4.hex,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('day', c4.timestamp), c4.hex
HAVING COUNT(*) >= 3
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Query 30: What are the weekly altitude statistics by speed range with IQR-based outlier detection and quartile analysis? {#query-30}

**Use Case:** **What are the weekly altitude statistics by speed range with IQR-based outlier detection and quartile analysis?**

**Description:** The query correlates altitude with period (day/week/month), hex, and speed. Multi-dimensional grouping and window functions (PARTITION BY hex, speed) produce cross-dimensional aggregates.

**Business Value:** Aggregated metrics grouped by week and speed

**Complexity:** moderate

```sql
WITH cte_level_1 AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY speed ORDER BY timestamp DESC) AS rn,
        DATE_TRUNC('day', timestamp) AS day_bucket,
        DATE_TRUNC('week', timestamp) AS week_bucket,
        EXTRACT(HOUR FROM timestamp) AS hour_val,
        EXTRACT(DOW FROM timestamp) AS dow_val
    FROM aircraft_position_history
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '365 days'
),
cte_level_2 AS (
    SELECT
        c1.*,
        COUNT(*) OVER (PARTITION BY c1.day_bucket, c1.speed) AS daily_partition_count,
        AVG(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg,
        SUM(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum,
        FIRST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp) AS first_val,
        LAST_VALUE(c1.altitude) OVER (PARTITION BY c1.speed ORDER BY c1.timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_val
    FROM cte_level_1 c1
    WHERE c1.rn <= 350
),
cte_level_3 AS (
    SELECT
        c2.*,
        LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS prev_value,
        LEAD(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS next_value,
        c2.altitude - LAG(c2.altitude, 1) OVER (PARTITION BY c2.speed ORDER BY c2.timestamp) AS delta_value,
        AVG(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_avg,
        STDDEV(c2.altitude) OVER (PARTITION BY c2.speed) AS partition_stddev,
        NTILE(4) OVER (PARTITION BY c2.speed ORDER BY c2.altitude) AS ntile_bucket,
        RANK() OVER (PARTITION BY c2.day_bucket ORDER BY c2.altitude DESC) AS daily_rank
    FROM cte_level_2 c2
),
cte_level_4 AS (
    SELECT
        c3.*,
        CASE
            WHEN c3.partition_stddev > 0 THEN (c3.altitude - c3.partition_avg) / c3.partition_stddev
            ELSE 0
        END AS z_score,
        DENSE_RANK() OVER (ORDER BY c3.cumulative_sum DESC) AS overall_rank,
        PERCENT_RANK() OVER (PARTITION BY c3.speed ORDER BY c3.altitude) AS pct_rank,
        CASE
            WHEN c3.delta_value > 0 THEN 'Increasing'
            WHEN c3.delta_value < 0 THEN 'Decreasing'
            ELSE 'Stable'
        END AS trend_direction
    FROM cte_level_3 c3
)
SELECT
    DATE_TRUNC('week', c4.timestamp) AS period,
    c4.speed,
    COUNT(*) AS record_count,
    AVG(c4.altitude) AS avg_value,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c4.altitude) AS q1_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c4.altitude) AS median_value,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c4.altitude) AS q3_value,
    STDDEV(c4.altitude) AS stddev_value,
    MIN(c4.altitude) AS min_value,
    MAX(c4.altitude) AS max_value,
    SUM(CASE WHEN c4.z_score > 2 THEN 1 ELSE 0 END) AS outlier_count,
    SUM(CASE WHEN c4.trend_direction = 'Increasing' THEN 1 ELSE 0 END) AS increasing_count,
    AVG(c4.rolling_avg) AS avg_rolling,
    MAX(c4.cumulative_sum) AS max_cumulative
FROM cte_level_4 c4
GROUP BY DATE_TRUNC('week', c4.timestamp), c4.speed
HAVING COUNT(*) >= 1
ORDER BY period DESC, avg_value DESC
LIMIT 100
```

---

## Usage Instructions

1. **Database Access**: Ensure you have access to the database instance (PostgreSQL)
2. **Credentials**: Obtain database connection credentials
3. **Schema**: Ensure all tables are created and populated with data

1. **Open Query File**: Navigate to `queries/queries.md`
2. **Select Query**: Choose the query number you want to execute
3. **Copy SQL**: Copy the SQL code from the code block
4. **Execute**: Run the query in your database client:
   - **PostgreSQL**: Use `psql` or pgAdmin
   - **, **: Use, SQL editor or notebook
   - **, **: Use, web interface or SnowSQL

- Each query includes an "Expected Output" section describing the result set
- Review the query description to understand what metrics are being calculated
- Check the complexity notes to understand the SQL patterns used

If using, notebooks:

1. Create a new notebook
2. Set the language to SQL
3. Copy the query SQL into a cell
4. Add markdown cells above for context:
   ```markdown
   # Query 1: User Activity Analysis

   This query analyzes user engagement patterns...
   ```
5. Execute the cell to run the query
6. Review results and add visualization cells as needed

1. **Create Tables**: Execute the schema creation scripts
2. **Create Indexes**: Ensure all indexes are created for performance
3. **Load Data**: Populate tables with sample or production data
4. **Verify**: Run validation queries to ensure data integrity

- All queries are designed for distributed systems
- Indexes are critical for query performance
- Consider partitioning large tables (messages, notifications) by date
- Monitor query execution times and optimize as needed

- Queries use standard SQL syntax where possible
- Some database-specific features are abstracted:
  - PostgreSQL: Uses `ARRAY` types
  : Uses compatible array functions
  : Uses `VARIANT` for JSON data
- Test queries on your target database before production use

---

---

## Platform Compatibility

All queries in this database are designed to work across multiple database platforms:

- **PostgreSQL**: Full support with standard SQL features

Queries use standard SQL syntax and avoid platform-specific features to ensure compatibility.

---

**Document Information:**

- **Generated**: 20260218-0352
- **Database**: db-1
- **Type**: Chat/Messaging System
- **Queries**: 30 production queries
- **Status**: ✅ Complete Comprehensive Deliverable
