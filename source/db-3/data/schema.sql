-- Simplified Schema for db-3
-- Reduced from 65 tables to only 3 tables needed for queries
-- All queries use generic table names (table1, table2, table3)

-- Main hierarchy table (used by all queries)
CREATE TABLE IF NOT EXISTS table1 (
    id BIGINT PRIMARY KEY,
    parent_id BIGINT,
    name VARCHAR(255) NOT NULL,
    value NUMERIC(15,2),
    category VARCHAR(100),
    date_col DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Related table (used by some queries)
CREATE TABLE IF NOT EXISTS table2 (
    id BIGINT PRIMARY KEY,
    table1_id BIGINT,
    related_value NUMERIC(15,2),
    description VARCHAR(16777216),
    date_col DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table1_id) REFERENCES table1(id)
);

-- Additional related table (used by some queries)
CREATE TABLE IF NOT EXISTS table3 (
    id BIGINT PRIMARY KEY,
    table1_id BIGINT,
    table2_id BIGINT,
    metric_value NUMERIC(15,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (table1_id) REFERENCES table1(id),
    FOREIGN KEY (table2_id) REFERENCES table2(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_table1_parent_id ON table1(parent_id);
CREATE INDEX IF NOT EXISTS idx_table1_category ON table1(category);
CREATE INDEX IF NOT EXISTS idx_table1_date_col ON table1(date_col);
CREATE INDEX IF NOT EXISTS idx_table2_table1_id ON table2(table1_id);
CREATE INDEX IF NOT EXISTS idx_table3_table1_id ON table3(table1_id);
CREATE INDEX IF NOT EXISTS idx_table3_table2_id ON table3(table2_id);

-- View for queries that expect orders_order (seller_id, created_at, total_amount, status)
CREATE OR REPLACE VIEW orders_order AS
SELECT id, COALESCE(parent_id, id)::BIGINT AS seller_id,
       COALESCE(created_at, date_col::TIMESTAMP) AS created_at,
       COALESCE(value, 0) AS total_amount,
       COALESCE(category, 'pending') AS status
FROM table1;
