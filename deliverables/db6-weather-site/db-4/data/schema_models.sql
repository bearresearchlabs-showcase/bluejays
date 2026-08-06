-- models table for db-4 queries (SharedAI-style analytics)
CREATE TABLE IF NOT EXISTS public.models (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
