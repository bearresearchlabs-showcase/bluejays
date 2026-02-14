-- Minimal phppos schema for db-2 (PostgreSQL)
-- Only tables needed for gov-rebuilt data and queries

CREATE TABLE phppos_people (
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone_number VARCHAR(50),
    email VARCHAR(255),
    address_1 VARCHAR(255),
    address_2 VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(50),
    zip VARCHAR(20),
    country VARCHAR(100),
    comments TEXT,
    person_id INTEGER PRIMARY KEY
);

CREATE TABLE phppos_employees (
    username VARCHAR(255),
    password VARCHAR(255),
    person_id INTEGER,
    balance NUMERIC(15,2) DEFAULT 0,
    deleted INTEGER DEFAULT 0,
    hide_from_switch_user INTEGER DEFAULT 0
);

CREATE TABLE phppos_employees_locations (
    employee_id INTEGER,
    location_id INTEGER
);

CREATE TABLE phppos_items (
    name VARCHAR(255),
    category VARCHAR(255),
    description TEXT,
    cost_price NUMERIC(15,2) DEFAULT 0,
    unit_price NUMERIC(15,2) DEFAULT 0,
    item_id INTEGER PRIMARY KEY,
    allow_alt_description INTEGER DEFAULT 0,
    is_serialized INTEGER DEFAULT 0,
    override_default_tax INTEGER DEFAULT 0,
    is_service INTEGER DEFAULT 0,
    deleted INTEGER DEFAULT 0
);

CREATE TABLE phppos_locations (
    location_id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    address TEXT,
    phone VARCHAR(50),
    fax VARCHAR(50),
    email VARCHAR(255),
    receive_stock_alert VARCHAR(10) DEFAULT '0',
    stock_alert_email VARCHAR(255),
    timezone VARCHAR(100),
    mailchimp_api_key VARCHAR(255),
    enable_credit_card_processing VARCHAR(10) DEFAULT '0',
    merchant_id VARCHAR(255),
    merchant_password VARCHAR(255),
    default_tax_1_rate NUMERIC(10,2),
    default_tax_1_name VARCHAR(255),
    default_tax_2_rate NUMERIC(10,2),
    default_tax_2_name VARCHAR(255),
    default_tax_2_cumulative VARCHAR(10) DEFAULT '0',
    default_tax_3_rate NUMERIC(10,2),
    default_tax_3_name VARCHAR(255),
    default_tax_4_rate NUMERIC(10,2),
    default_tax_4_name VARCHAR(255),
    default_tax_5_rate NUMERIC(10,2),
    default_tax_5_name VARCHAR(255),
    deleted INTEGER DEFAULT 0
);

CREATE TABLE phppos_location_items (
    location_id INTEGER,
    item_id INTEGER,
    quantity NUMERIC(15,2) DEFAULT 0
);

CREATE TABLE phppos_sales (
    sale_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    sale_time TIMESTAMP,
    customer_id INTEGER,
    payment_type VARCHAR(50),
    location_id INTEGER
);
