-- PostgreSQL-specific schema file
-- Generated from schema.sql
-- Generated: 2026-02-05 19:10:11
-- Database: db-12
-- 
-- This file contains PostgreSQL-specific SQL syntax.
-- Use this file when setting up the database in PostgreSQL.
--

-- Credit Card Database Schema
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for credit card and rewards optimization system

-- Credit Card Issuers Table
-- Stores information about credit card issuing banks and financial institutions
-- Enable PostGIS extension for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE credit_card_issuers (
    issuer_id VARCHAR(255) PRIMARY KEY,
    issuer_name VARCHAR(255) NOT NULL,
    issuer_code VARCHAR(50) UNIQUE,
    bank_type VARCHAR(50),  -- 'National', 'Regional', 'Credit Union', 'Fintech'
    country_code VARCHAR(2) DEFAULT 'US',
    website_url VARCHAR(500),
    customer_service_phone VARCHAR(50),
    total_cards_issued INTEGER,
    market_share_percentage NUMERIC(5, 2),
    cfpb_complaint_count INTEGER DEFAULT 0,
    cfpb_complaint_resolution_rate NUMERIC(5, 2),
    data_source VARCHAR(50) DEFAULT 'CFPB_API',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit Cards Table
-- Stores comprehensive information about individual credit card products
CREATE TABLE credit_cards (
    card_id VARCHAR(255) PRIMARY KEY,
    issuer_id VARCHAR(255) NOT NULL,
    card_name VARCHAR(255) NOT NULL,
    card_type VARCHAR(50),  -- 'Cash Back', 'Travel', 'Points', 'Miles', 'Business', 'Secured'
    annual_fee NUMERIC(10, 2) DEFAULT 0,
    annual_fee_waived_first_year BOOLEAN DEFAULT FALSE,
    signup_bonus_points INTEGER,
    signup_bonus_cash NUMERIC(10, 2),
    signup_bonus_spend_requirement NUMERIC(10, 2),
    signup_bonus_timeframe_months INTEGER,
    apr_purchase NUMERIC(5, 2),
    apr_balance_transfer NUMERIC(5, 2),
    apr_cash_advance NUMERIC(5, 2),
    foreign_transaction_fee_percentage NUMERIC(5, 2),
    credit_score_min INTEGER,
    credit_score_max INTEGER,
    card_network VARCHAR(50),  -- 'Visa', 'Mastercard', 'Amex', 'Discover'
    card_level VARCHAR(50),  -- 'Standard', 'Gold', 'Platinum', 'Signature', 'Infinite'
    metal_card BOOLEAN DEFAULT FALSE,
    authorized_user_fee NUMERIC(10, 2) DEFAULT 0,
    card_agreement_url VARCHAR(500),
    card_image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    launch_date DATE,
    discontinued_date DATE,
    data_source VARCHAR(50) DEFAULT 'CFPB_AGREEMENT_DB',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_card_issuer FOREIGN KEY (issuer_id) REFERENCES credit_card_issuers(issuer_id)
);

-- Rewards Categories Table
-- Defines spending categories for rewards multipliers (dining, gas, groceries, etc.)
CREATE TABLE rewards_categories (
    category_id VARCHAR(255) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    category_code VARCHAR(50) UNIQUE,  -- 'DINING', 'GAS', 'GROCERIES', 'TRAVEL', etc.
    parent_category_id VARCHAR(255),
    category_description TEXT,
    merchant_category_codes TEXT,  -- Comma-separated MCC codes
    is_bonus_category BOOLEAN DEFAULT FALSE,
    typical_multiplier NUMERIC(4, 2) DEFAULT 1.0,
    data_source VARCHAR(50) DEFAULT 'MANUAL',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_parent_category FOREIGN KEY (parent_category_id) REFERENCES rewards_categories(category_id)
);

-- Card Rewards Structure Table
-- Maps credit cards to rewards categories with multipliers and limits
CREATE TABLE card_rewards_structure (
    reward_structure_id VARCHAR(255) PRIMARY KEY,
    card_id VARCHAR(255) NOT NULL,
    category_id VARCHAR(255) NOT NULL,
    rewards_multiplier NUMERIC(4, 2) NOT NULL,  -- e.g., 3.0 for 3x points
    rewards_type VARCHAR(50),  -- 'Points', 'Cash Back', 'Miles'
    points_per_dollar NUMERIC(6, 2),
    cash_back_percentage NUMERIC(5, 2),
    annual_spend_limit NUMERIC(12, 2),  -- NULL for unlimited
    quarterly_spend_limit NUMERIC(12, 2),
    monthly_spend_limit NUMERIC(12, 2),
    effective_start_date DATE,
    effective_end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    promotion_description TEXT,
    data_source VARCHAR(50) DEFAULT 'CARD_AGREEMENT',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reward_card FOREIGN KEY (card_id) REFERENCES credit_cards(card_id),
    CONSTRAINT fk_reward_category FOREIGN KEY (category_id) REFERENCES rewards_categories(category_id)
);

-- Bank Offers Table
-- Stores targeted offers from banks (Amex Offers, Chase Offers, Bank of America, etc.)
CREATE TABLE bank_offers (
    offer_id VARCHAR(255) PRIMARY KEY,
    issuer_id VARCHAR(255) NOT NULL,
    offer_name VARCHAR(255) NOT NULL,
    offer_description TEXT,
    merchant_name VARCHAR(255),
    merchant_category VARCHAR(100),
    offer_type VARCHAR(50),  -- 'Statement Credit', 'Points Bonus', 'Cash Back', 'Discount'
    discount_amount NUMERIC(10, 2),
    discount_percentage NUMERIC(5, 2),
    minimum_spend NUMERIC(10, 2),
    maximum_discount NUMERIC(10, 2),
    points_bonus_multiplier NUMERIC(4, 2),
    offer_start_date DATE,
    offer_end_date DATE,
    redemption_deadline DATE,
    terms_and_conditions TEXT,
    offer_url VARCHAR(500),
    is_targeted BOOLEAN DEFAULT FALSE,
    eligibility_criteria TEXT,
    activation_required BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(50) DEFAULT 'BANK_API',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_offer_issuer FOREIGN KEY (issuer_id) REFERENCES credit_card_issuers(issuer_id)
);

-- Card Offer Eligibility Table
-- Maps which cards are eligible for specific bank offers
CREATE TABLE card_offer_eligibility (
    eligibility_id VARCHAR(255) PRIMARY KEY,
    offer_id VARCHAR(255) NOT NULL,
    card_id VARCHAR(255) NOT NULL,
    eligibility_status VARCHAR(50) DEFAULT 'Eligible',  -- 'Eligible', 'Not Eligible', 'Targeted'
    activation_status VARCHAR(50),  -- 'Activated', 'Not Activated', 'Expired'
    activation_date DATE,
    redemption_count INTEGER DEFAULT 0,
    total_savings NUMERIC(10, 2) DEFAULT 0,
    data_source VARCHAR(50) DEFAULT 'BANK_API',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_eligibility_offer FOREIGN KEY (offer_id) REFERENCES bank_offers(offer_id),
    CONSTRAINT fk_eligibility_card FOREIGN KEY (card_id) REFERENCES credit_cards(card_id)
);

-- Merchants Table
-- Stores merchant information for location-based card recommendations
CREATE TABLE merchants (
    merchant_id VARCHAR(255) PRIMARY KEY,
    merchant_name VARCHAR(255) NOT NULL,
    merchant_category_code VARCHAR(10),  -- MCC code
    merchant_category VARCHAR(100),
    parent_merchant_id VARCHAR(255),
    website_url VARCHAR(500),
    is_chain BOOLEAN DEFAULT FALSE,
    chain_location_count INTEGER,
    data_source VARCHAR(50) DEFAULT 'MANUAL',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_parent_merchant FOREIGN KEY (parent_merchant_id) REFERENCES merchants(merchant_id)
);

-- Merchant Locations Table
-- Stores physical locations of merchants for location-based recommendations
CREATE TABLE merchant_locations (
    location_id VARCHAR(255) PRIMARY KEY,
    merchant_id VARCHAR(255) NOT NULL,
    location_name VARCHAR(255),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_code VARCHAR(2),
    postal_code VARCHAR(20),
    country_code VARCHAR(2) DEFAULT 'US',
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    location_geom GEOGRAPHY,  -- Point geometry for location
    phone_number VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(50) DEFAULT 'GOOGLE_PLACES_API',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_location_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);

-- User Profiles Table
-- Stores user account information and preferences
CREATE TABLE user_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    subscription_tier VARCHAR(50) DEFAULT 'Free',  -- 'Free', 'Plus', 'Premium'
    subscription_expires_date DATE,
    preferred_currency VARCHAR(3) DEFAULT 'USD',
    location_latitude NUMERIC(10, 7),
    location_longitude NUMERIC(10, 7),
    location_geom GEOGRAPHY,
    notification_preferences JSON,
    data_source VARCHAR(50) DEFAULT 'APP_DB',
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Cards Table
-- Tracks which credit cards users own
CREATE TABLE user_cards (
    user_card_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    card_id VARCHAR(255) NOT NULL,
    card_nickname VARCHAR(100),
    account_opening_date DATE,
    account_status VARCHAR(50) DEFAULT 'Active',  -- 'Active', 'Closed', 'Suspended'
    credit_limit NUMERIC(12, 2),
    current_balance NUMERIC(12, 2),
    available_credit NUMERIC(12, 2),
    annual_fee_paid NUMERIC(10, 2),
    next_annual_fee_date DATE,
    is_primary_card BOOLEAN DEFAULT FALSE,
    chase_5_24_status INTEGER,  -- Chase 5/24 rule tracking
    data_source VARCHAR(50) DEFAULT 'USER_INPUT',
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_card_user FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    CONSTRAINT fk_user_card_card FOREIGN KEY (card_id) REFERENCES credit_cards(card_id)
);

-- Spending Transactions Table
-- Tracks user spending transactions for rewards optimization
CREATE TABLE spending_transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    user_card_id VARCHAR(255) NOT NULL,
    merchant_id VARCHAR(255),
    location_id VARCHAR(255),
    transaction_date DATE NOT NULL,
    transaction_time TIMESTAMP NOT NULL,
    transaction_amount NUMERIC(10, 2) NOT NULL,
    currency_code VARCHAR(3) DEFAULT 'USD',
    category_id VARCHAR(255),
    merchant_category_code VARCHAR(10),
    rewards_earned NUMERIC(10, 2),
    rewards_multiplier_applied NUMERIC(4, 2),
    offer_applied_id VARCHAR(255),
    offer_savings NUMERIC(10, 2),
    card_used_id VARCHAR(255),
    optimal_card_id VARCHAR(255),  -- Best card that should have been used
    potential_rewards_lost NUMERIC(10, 2),
    transaction_description VARCHAR(500),
    data_source VARCHAR(50) DEFAULT 'BANK_API',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transaction_user FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    CONSTRAINT fk_transaction_user_card FOREIGN KEY (user_card_id) REFERENCES user_cards(user_card_id),
    CONSTRAINT fk_transaction_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    CONSTRAINT fk_transaction_location FOREIGN KEY (location_id) REFERENCES merchant_locations(location_id),
    CONSTRAINT fk_transaction_category FOREIGN KEY (category_id) REFERENCES rewards_categories(category_id),
    CONSTRAINT fk_transaction_offer FOREIGN KEY (offer_applied_id) REFERENCES bank_offers(offer_id)
);

-- Card Recommendations Table
-- Stores real-time card recommendations for merchants and categories
CREATE TABLE card_recommendations (
    recommendation_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    merchant_id VARCHAR(255),
    location_id VARCHAR(255),
    category_id VARCHAR(255),
    recommended_card_id VARCHAR(255) NOT NULL,
    recommendation_reason TEXT,
    expected_rewards NUMERIC(10, 2),
    expected_multiplier NUMERIC(4, 2),
    applicable_offer_id VARCHAR(255),
    offer_savings NUMERIC(10, 2),
    recommendation_score NUMERIC(5, 2),  -- 0-100 score
    recommendation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommendation_type VARCHAR(50),  -- 'Merchant', 'Category', 'Location', 'Offer'
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_recommendation_user FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    CONSTRAINT fk_recommendation_card FOREIGN KEY (recommended_card_id) REFERENCES credit_cards(card_id),
    CONSTRAINT fk_recommendation_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    CONSTRAINT fk_recommendation_location FOREIGN KEY (location_id) REFERENCES merchant_locations(location_id),
    CONSTRAINT fk_recommendation_category FOREIGN KEY (category_id) REFERENCES rewards_categories(category_id),
    CONSTRAINT fk_recommendation_offer FOREIGN KEY (applicable_offer_id) REFERENCES bank_offers(offer_id)
);

-- CFPB Consumer Complaints Table
-- Stores consumer complaints from CFPB Consumer Complaint Database
CREATE TABLE cfpb_consumer_complaints (
    complaint_id VARCHAR(255) PRIMARY KEY,
    complaint_date DATE NOT NULL,
    complaint_submitted_date DATE,
    complaint_received_date DATE,
    product_type VARCHAR(100),  -- 'Credit card', 'Credit reporting', etc.
    sub_product VARCHAR(100),
    issue_type VARCHAR(100),
    sub_issue VARCHAR(100),
    consumer_complaint_narrative TEXT,
    company_name VARCHAR(255),
    company_response VARCHAR(255),
    timely_response BOOLEAN,
    consumer_disputed BOOLEAN,
    complaint_id_cfpb VARCHAR(100) UNIQUE,
    zip_code VARCHAR(20),
    state_code VARCHAR(2),
    tags VARCHAR(255),
    consumer_consent_provided BOOLEAN,
    submitted_via VARCHAR(50),
    date_sent_to_company DATE,
    company_public_response TEXT,
    data_source VARCHAR(50) DEFAULT 'CFPB_API',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Federal Reserve Credit Data Table
-- Stores consumer credit statistics from Federal Reserve G.19 release
CREATE TABLE federal_reserve_credit_data (
    data_id VARCHAR(255) PRIMARY KEY,
    report_date DATE NOT NULL,
    release_date DATE,
    data_type VARCHAR(50),  -- 'Revolving', 'Non-Revolving', 'Total'
    credit_outstanding_billions NUMERIC(15, 2),
    credit_outstanding_seasonally_adjusted_billions NUMERIC(15, 2),
    credit_flow_billions NUMERIC(15, 2),
    credit_flow_seasonally_adjusted_billions NUMERIC(15, 2),
    interest_rate_avg NUMERIC(5, 2),
    interest_rate_weighted_avg NUMERIC(5, 2),
    data_source VARCHAR(50) DEFAULT 'FED_G19',
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rewards Optimization Analytics Table
-- Pre-computed analytics for rewards optimization queries
CREATE TABLE rewards_optimization_analytics (
    analytics_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    analysis_date DATE NOT NULL,
    total_spending NUMERIC(12, 2),
    total_rewards_earned NUMERIC(10, 2),
    potential_rewards_lost NUMERIC(10, 2),
    optimization_score NUMERIC(5, 2),  -- Percentage of optimal rewards captured
    top_category_id VARCHAR(255),
    top_category_spending NUMERIC(12, 2),
    top_card_id VARCHAR(255),
    top_card_rewards NUMERIC(10, 2),
    offers_activated_count INTEGER DEFAULT 0,
    offers_savings_total NUMERIC(10, 2) DEFAULT 0,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_analytics_user FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    CONSTRAINT fk_analytics_category FOREIGN KEY (top_category_id) REFERENCES rewards_categories(category_id),
    CONSTRAINT fk_analytics_card FOREIGN KEY (top_card_id) REFERENCES credit_cards(card_id)
);

-- Create indexes for performance
CREATE INDEX idx_cards_issuer ON credit_cards(issuer_id);
CREATE INDEX idx_cards_type ON credit_cards(card_type);
CREATE INDEX idx_cards_network ON credit_cards(card_network);
CREATE INDEX idx_rewards_structure_card ON card_rewards_structure(card_id);
CREATE INDEX idx_rewards_structure_category ON card_rewards_structure(category_id);
CREATE INDEX idx_rewards_structure_active ON card_rewards_structure(is_active, effective_start_date, effective_end_date);
CREATE INDEX idx_offers_issuer ON bank_offers(issuer_id);
CREATE INDEX idx_offers_dates ON bank_offers(offer_start_date, offer_end_date);
CREATE INDEX idx_offers_active ON bank_offers(is_targeted, offer_start_date, offer_end_date);
CREATE INDEX idx_offer_eligibility_offer ON card_offer_eligibility(offer_id);
CREATE INDEX idx_offer_eligibility_card ON card_offer_eligibility(card_id);
CREATE INDEX idx_merchants_category ON merchants(merchant_category);
CREATE INDEX idx_merchant_locations_merchant ON merchant_locations(merchant_id);
CREATE INDEX idx_merchant_locations_geom ON merchant_locations USING GIST(location_geom);
CREATE INDEX idx_user_cards_user ON user_cards(user_id);
CREATE INDEX idx_user_cards_card ON user_cards(card_id);
CREATE INDEX idx_user_cards_active ON user_cards(account_status);
CREATE INDEX idx_transactions_user ON spending_transactions(user_id);
CREATE INDEX idx_transactions_date ON spending_transactions(transaction_date);
CREATE INDEX idx_transactions_merchant ON spending_transactions(merchant_id);
CREATE INDEX idx_transactions_category ON spending_transactions(category_id);
CREATE INDEX idx_transactions_card ON spending_transactions(card_used_id);
CREATE INDEX idx_recommendations_user ON card_recommendations(user_id);
CREATE INDEX idx_recommendations_timestamp ON card_recommendations(recommendation_timestamp);
CREATE INDEX idx_recommendations_active ON card_recommendations(is_active);
CREATE INDEX idx_cfpb_complaints_company ON cfpb_consumer_complaints(company_name);
CREATE INDEX idx_cfpb_complaints_date ON cfpb_consumer_complaints(complaint_date);
CREATE INDEX idx_cfpb_complaints_product ON cfpb_consumer_complaints(product_type);
CREATE INDEX idx_fed_credit_date ON federal_reserve_credit_data(report_date);
CREATE INDEX idx_fed_credit_type ON federal_reserve_credit_data(data_type);
CREATE INDEX idx_analytics_user_date ON rewards_optimization_analytics(user_id, analysis_date);
