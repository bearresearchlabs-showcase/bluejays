---
title: Credit Card and Rewards Optimization System — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-12
---

# Credit Card and Rewards Optimization System — Documentation

**Database:** db-12  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_12
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_12 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load sample data from data.sql if available.

```bash
psql -U postgres -d db_12 -f data.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

Standard PostgreSQL. No extensions required unless noted.

---

## Schema Overview

**Total tables:** 15

- `credit_card_issuers` — (see data dictionary)
- `credit_cards` — (see data dictionary)
- `rewards_categories` — (see data dictionary)
- `card_rewards_structure` — (see data dictionary)
- `bank_offers` — (see data dictionary)
- `card_offer_eligibility` — (see data dictionary)
- `merchants` — (see data dictionary)
- `merchant_locations` — (see data dictionary)
- `user_profiles` — (see data dictionary)
- `user_cards` — (see data dictionary)
- `spending_transactions` — (see data dictionary)
- `card_recommendations` — (see data dictionary)
- `cfpb_consumer_complaints` — (see data dictionary)
- `federal_reserve_credit_data` — (see data dictionary)
- `rewards_optimization_analytics` — (see data dictionary)

---

## Data Dictionary

### `credit_card_issuers`

- `issuer_id` VARCHAR(255) PRIMARY KEY
- `issuer_name` VARCHAR(255) NOT NULL
- `issuer_code` VARCHAR(50) UNIQUE
- `bank_type` VARCHAR(50)  — 'National', 'Regional', 'Credit Union', 'Fintech'
- `country_code` VARCHAR(2) 
- `website_url` VARCHAR(500) 
- `customer_service_phone` VARCHAR(50) 
- `total_cards_issued` INTEGER 
- `market_share_percentage` NUMERIC(5 
- `cfpb_complaint_count` INTEGER 
- `cfpb_complaint_resolution_rate` NUMERIC(5 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 

### `credit_cards`

- `card_id` VARCHAR(255) PRIMARY KEY
- `issuer_id` VARCHAR(255) NOT NULL
- `card_name` VARCHAR(255) NOT NULL
- `card_type` VARCHAR(50)  — 'Cash Back', 'Travel', 'Points', 'Miles', 'Business', 'Secured'
- `annual_fee` NUMERIC(10 
- `annual_fee_waived_first_year` BOOLEAN 
- `signup_bonus_points` INTEGER 
- `signup_bonus_cash` NUMERIC(10 
- `signup_bonus_spend_requirement` NUMERIC(10 
- `signup_bonus_timeframe_months` INTEGER 
- `apr_purchase` NUMERIC(5 
- `apr_balance_transfer` NUMERIC(5 
- `apr_cash_advance` NUMERIC(5 
- `foreign_transaction_fee_percentage` NUMERIC(5 
- `credit_score_min` INTEGER 
- `credit_score_max` INTEGER 
- `card_network` VARCHAR(50)  — 'Visa', 'Mastercard', 'Amex', 'Discover'
- `card_level` VARCHAR(50)  — 'Standard', 'Gold', 'Platinum', 'Signature', 'Infinite'
- `metal_card` BOOLEAN 
- `authorized_user_fee` NUMERIC(10 
- `card_agreement_url` VARCHAR(500) 
- `card_image_url` VARCHAR(500) 
- `is_active` BOOLEAN 
- `launch_date` DATE 
- `discontinued_date` DATE 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_card_issuer FOREIGN KEY

### `rewards_categories`

- `category_id` VARCHAR(255) PRIMARY KEY
- `category_name` VARCHAR(100) UNIQUE, NOT NULL
- `category_code` VARCHAR(50) UNIQUE — 'DINING', 'GAS', 'GROCERIES', 'TRAVEL', etc.
- `parent_category_id` VARCHAR(255) 
- `category_description` TEXT 
- `merchant_category_codes` TEXT  — Comma-separated MCC codes
- `is_bonus_category` BOOLEAN 
- `typical_multiplier` NUMERIC(4 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_parent_category FOREIGN KEY

### `card_rewards_structure`

- `reward_structure_id` VARCHAR(255) PRIMARY KEY
- `card_id` VARCHAR(255) NOT NULL
- `category_id` VARCHAR(255) NOT NULL
- `rewards_multiplier` NUMERIC(4 NOT NULL — e.g., 3.0 for 3x points
- `rewards_type` VARCHAR(50)  — 'Points', 'Cash Back', 'Miles'
- `points_per_dollar` NUMERIC(6 
- `cash_back_percentage` NUMERIC(5 
- `annual_spend_limit` NUMERIC(12  — NULL for unlimited
- `quarterly_spend_limit` NUMERIC(12 
- `monthly_spend_limit` NUMERIC(12 
- `effective_start_date` DATE 
- `effective_end_date` DATE 
- `is_active` BOOLEAN 
- `promotion_description` TEXT 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_reward_card FOREIGN KEY
- `CONSTRAINT` fk_reward_category FOREIGN KEY

### `bank_offers`

- `offer_id` VARCHAR(255) PRIMARY KEY
- `issuer_id` VARCHAR(255) NOT NULL
- `offer_name` VARCHAR(255) NOT NULL
- `offer_description` TEXT 
- `merchant_name` VARCHAR(255) 
- `merchant_category` VARCHAR(100) 
- `offer_type` VARCHAR(50)  — 'Statement Credit', 'Points Bonus', 'Cash Back', 'Discount'
- `discount_amount` NUMERIC(10 
- `discount_percentage` NUMERIC(5 
- `minimum_spend` NUMERIC(10 
- `maximum_discount` NUMERIC(10 
- `points_bonus_multiplier` NUMERIC(4 
- `offer_start_date` DATE 
- `offer_end_date` DATE 
- `redemption_deadline` DATE 
- `terms_and_conditions` TEXT 
- `offer_url` VARCHAR(500) 
- `is_targeted` BOOLEAN 
- `eligibility_criteria` TEXT 
- `activation_required` BOOLEAN 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_offer_issuer FOREIGN KEY

### `card_offer_eligibility`

- `eligibility_id` VARCHAR(255) PRIMARY KEY
- `offer_id` VARCHAR(255) NOT NULL
- `card_id` VARCHAR(255) NOT NULL
- `eligibility_status` VARCHAR(50)  — 'Eligible', 'Not Eligible', 'Targeted'
- `activation_status` VARCHAR(50)  — 'Activated', 'Not Activated', 'Expired'
- `activation_date` DATE 
- `redemption_count` INTEGER 
- `total_savings` NUMERIC(10 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_eligibility_offer FOREIGN KEY
- `CONSTRAINT` fk_eligibility_card FOREIGN KEY

### `merchants`

- `merchant_id` VARCHAR(255) PRIMARY KEY
- `merchant_name` VARCHAR(255) NOT NULL
- `merchant_category_code` VARCHAR(10)  — MCC code
- `merchant_category` VARCHAR(100) 
- `parent_merchant_id` VARCHAR(255) 
- `website_url` VARCHAR(500) 
- `is_chain` BOOLEAN 
- `chain_location_count` INTEGER 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_parent_merchant FOREIGN KEY

### `merchant_locations`

- `location_id` VARCHAR(255) PRIMARY KEY
- `merchant_id` VARCHAR(255) NOT NULL
- `location_name` VARCHAR(255) 
- `address_line1` VARCHAR(255) 
- `address_line2` VARCHAR(255) 
- `city` VARCHAR(100) 
- `state_code` VARCHAR(2) 
- `postal_code` VARCHAR(20) 
- `country_code` VARCHAR(2) 
- `latitude` NUMERIC(10 
- `longitude` NUMERIC(10 
- `location_geom` GEOGRAPHY  — Point geometry for location
- `phone_number` VARCHAR(50) 
- `is_active` BOOLEAN 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_location_merchant FOREIGN KEY

### `user_profiles`

- `user_id` VARCHAR(255) PRIMARY KEY
- `username` VARCHAR(100) UNIQUE
- `email` VARCHAR(255) UNIQUE
- `subscription_tier` VARCHAR(50)  — 'Free', 'Plus', 'Premium'
- `subscription_expires_date` DATE 
- `preferred_currency` VARCHAR(3) 
- `location_latitude` NUMERIC(10 
- `location_longitude` NUMERIC(10 
- `location_geom` GEOGRAPHY 
- `notification_preferences` JSON 
- `data_source` VARCHAR(50) 
- `created_timestamp` TIMESTAMP 
- `updated_timestamp` TIMESTAMP 

### `user_cards`

- `user_card_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) NOT NULL
- `card_id` VARCHAR(255) NOT NULL
- `card_nickname` VARCHAR(100) 
- `account_opening_date` DATE 
- `account_status` VARCHAR(50)  — 'Active', 'Closed', 'Suspended'
- `credit_limit` NUMERIC(12 
- `current_balance` NUMERIC(12 
- `available_credit` NUMERIC(12 
- `annual_fee_paid` NUMERIC(10 
- `next_annual_fee_date` DATE 
- `is_primary_card` BOOLEAN 
- `chase_5_24_status` INTEGER  — Chase 5/24 rule tracking
- `data_source` VARCHAR(50) 
- `created_timestamp` TIMESTAMP 
- `updated_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_user_card_user FOREIGN KEY
- `CONSTRAINT` fk_user_card_card FOREIGN KEY

### `spending_transactions`

- `transaction_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) NOT NULL
- `user_card_id` VARCHAR(255) NOT NULL
- `merchant_id` VARCHAR(255) 
- `location_id` VARCHAR(255) 
- `transaction_date` DATE NOT NULL
- `transaction_time` TIMESTAMP NOT NULL
- `transaction_amount` NUMERIC(10 NOT NULL
- `currency_code` VARCHAR(3) 
- `category_id` VARCHAR(255) 
- `merchant_category_code` VARCHAR(10) 
- `rewards_earned` NUMERIC(10 
- `rewards_multiplier_applied` NUMERIC(4 
- `offer_applied_id` VARCHAR(255) 
- `offer_savings` NUMERIC(10 
- `card_used_id` VARCHAR(255) 
- `optimal_card_id` VARCHAR(255)  — Best card that should have been used
- `potential_rewards_lost` NUMERIC(10 
- `transaction_description` VARCHAR(500) 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_transaction_user FOREIGN KEY
- `CONSTRAINT` fk_transaction_user_card FOREIGN KEY
- `CONSTRAINT` fk_transaction_merchant FOREIGN KEY
- `CONSTRAINT` fk_transaction_location FOREIGN KEY
- `CONSTRAINT` fk_transaction_category FOREIGN KEY
- `CONSTRAINT` fk_transaction_offer FOREIGN KEY

### `card_recommendations`

- `recommendation_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) NOT NULL
- `merchant_id` VARCHAR(255) 
- `location_id` VARCHAR(255) 
- `category_id` VARCHAR(255) 
- `recommended_card_id` VARCHAR(255) NOT NULL
- `recommendation_reason` TEXT 
- `expected_rewards` NUMERIC(10 
- `expected_multiplier` NUMERIC(4 
- `applicable_offer_id` VARCHAR(255) 
- `offer_savings` NUMERIC(10 
- `recommendation_score` NUMERIC(5  — 0-100 score
- `recommendation_timestamp` TIMESTAMP 
- `recommendation_type` VARCHAR(50)  — 'Merchant', 'Category', 'Location', 'Offer'
- `is_active` BOOLEAN 
- `CONSTRAINT` fk_recommendation_user FOREIGN KEY
- `CONSTRAINT` fk_recommendation_card FOREIGN KEY
- `CONSTRAINT` fk_recommendation_merchant FOREIGN KEY
- `CONSTRAINT` fk_recommendation_location FOREIGN KEY
- `CONSTRAINT` fk_recommendation_category FOREIGN KEY
- `CONSTRAINT` fk_recommendation_offer FOREIGN KEY

### `cfpb_consumer_complaints`

- `complaint_id` VARCHAR(255) PRIMARY KEY
- `complaint_date` DATE NOT NULL
- `complaint_submitted_date` DATE 
- `complaint_received_date` DATE 
- `product_type` VARCHAR(100)  — 'Credit card', 'Credit reporting', etc.
- `sub_product` VARCHAR(100) 
- `issue_type` VARCHAR(100) 
- `sub_issue` VARCHAR(100) 
- `consumer_complaint_narrative` TEXT 
- `company_name` VARCHAR(255) 
- `company_response` VARCHAR(255) 
- `timely_response` BOOLEAN 
- `consumer_disputed` BOOLEAN 
- `complaint_id_cfpb` VARCHAR(100) UNIQUE
- `zip_code` VARCHAR(20) 
- `state_code` VARCHAR(2) 
- `tags` VARCHAR(255) 
- `consumer_consent_provided` BOOLEAN 
- `submitted_via` VARCHAR(50) 
- `date_sent_to_company` DATE 
- `company_public_response` TEXT 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 

### `federal_reserve_credit_data`

- `data_id` VARCHAR(255) PRIMARY KEY
- `report_date` DATE NOT NULL
- `release_date` DATE 
- `data_type` VARCHAR(50)  — 'Revolving', 'Non-Revolving', 'Total'
- `credit_outstanding_billions` NUMERIC(15 
- `credit_outstanding_seasonally_adjusted_billions` NUMERIC(15 
- `credit_flow_billions` NUMERIC(15 
- `credit_flow_seasonally_adjusted_billions` NUMERIC(15 
- `interest_rate_avg` NUMERIC(5 
- `interest_rate_weighted_avg` NUMERIC(5 
- `data_source` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 

### `rewards_optimization_analytics`

- `analytics_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) NOT NULL
- `analysis_date` DATE NOT NULL
- `total_spending` NUMERIC(12 
- `total_rewards_earned` NUMERIC(10 
- `potential_rewards_lost` NUMERIC(10 
- `optimization_score` NUMERIC(5  — Percentage of optimal rewards captured
- `top_category_id` VARCHAR(255) 
- `top_category_spending` NUMERIC(12 
- `top_card_id` VARCHAR(255) 
- `top_card_rewards` NUMERIC(10 
- `offers_activated_count` INTEGER 
- `offers_savings_total` NUMERIC(10 
- `analysis_timestamp` TIMESTAMP 
- `CONSTRAINT` fk_analytics_user FOREIGN KEY
- `CONSTRAINT` fk_analytics_category FOREIGN KEY
- `CONSTRAINT` fk_analytics_card FOREIGN KEY
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 

---

*Generated by documentation workflow. MDX-compatible markdown.*
