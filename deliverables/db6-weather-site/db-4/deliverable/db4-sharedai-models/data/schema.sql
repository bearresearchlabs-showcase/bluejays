-- db-4 SharedAI Models - Minimal standalone schema for query execution
-- Compatible with PostgreSQL - models table only (queries use FROM models)

CREATE TABLE models (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    user_id INTEGER,
    created_at TIMESTAMP
);

CREATE INDEX idx_models_created_at ON models(created_at);
CREATE INDEX idx_models_user_id ON models(user_id);
CREATE INDEX idx_models_name ON models(name);
