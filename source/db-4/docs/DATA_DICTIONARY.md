# Data Dictionary - db-4 SharedAI Models

## models

**Schema**: `public`

Stores AI model metadata for SharedAI-style analytics. All 30 queries operate on this table.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `BIGINT` | Primary key |
| `name` | `VARCHAR(255)` | Model name |
| `user_id` | `BIGINT` | Owner user ID |
| `created_at` | `TIMESTAMP` | Creation time (default: CURRENT_TIMESTAMP) |
