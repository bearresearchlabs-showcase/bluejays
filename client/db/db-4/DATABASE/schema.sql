-- db-4 SharedAI Models - Production schema for query execution
-- Compatible with PostgreSQL
-- Single canonical schema: models table (queries use FROM models)

CREATE TABLE IF NOT EXISTS public.models (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_models_created_at ON public.models(created_at);
CREATE INDEX IF NOT EXISTS idx_models_user_id ON public.models(user_id);
CREATE INDEX IF NOT EXISTS idx_models_name ON public.models(name);
