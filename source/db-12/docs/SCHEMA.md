# Database Schema Documentation - db-12

**Created:** 2026-02-04

## Schema Overview

The credit card database consists of 15 main tables designed to store comprehensive credit card data, rewards structures, user profiles, spending transactions, and regulatory data for rewards optimization and portfolio management.

## Tables

### credit_card_issuers
Stores information about credit card issuing banks and financial institutions.

**Key Columns:**
- `issuer_id` (VARCHAR(255), PK)
- `issuer_name` (VARCHAR(255)) - Bank name (e.g., 'Chase', 'American Express', 'Citi')
- `issuer_code` (VARCHAR(50), UNIQUE) - Unique issuer identifier
- `bank_type` (VARCHAR(50)) - 'National', 'Regional', 'Credit Union', 'Fintech'
- `country_code` (VARCHAR(2)) - ISO country code, default 'US'
- `cfpb_complaint_count` (INTEGER) - Total CFPB complaints
- `cfpb_complaint_resolution_rate` (NUMERIC(5, 2)) - Resolution rate percentage
- `market_share_percentage` (NUMERIC(5, 2)) - Market share

### credit_cards
Stores comprehensive information about individual credit card products.

**Key Columns:**
- `card_id` (VARCHAR(255), PK)
- `issuer_id` (VARCHAR(255), FK → credit_card_issuers)
- `card_name` (VARCHAR(255)) - Full card name
- `card_type` (VARCHAR(50)) - 'Cash Back', 'Travel', 'Points', 'Miles', 'Business', 'Secured'
- `annual_fee` (NUMERIC(10, 2)) - Annual fee amount
- `annual_fee_waived_first_year` (BOOLEAN) - First year fee waiver
- `signup_bonus_points` (INTEGER) - Signup bonus points
- `signup_bonus_cash` (NUMERIC(10, 2)) - Signup bonus cash amount
- `signup_bonus_spend_requirement` (NUMERIC(10, 2)) - Required spending for bonus
- `signup_bonus_timeframe_months` (INTEGER) - Timeframe to meet spend requirement
- `apr_purchase` (NUMERIC(5, 2)) - Purchase APR
- `credit_score_min` (INTEGER) - Minimum credit score required
- `card_network` (VARCHAR(50)) - 'Visa', 'Mastercard', 'Amex', 'Discover'
- `card_level` (VARCHAR(50)) - 'Standard', 'Gold', 'Platinum', 'Signature', 'Infinite'
- `metal_card` (BOOLEAN) - Whether card is metal
- `is_active` (BOOLEAN) - Whether card is currently available

### rewards_categories
Defines spending categories for rewards multipliers (dining, gas, groceries, etc.).

**Key Columns:**
- `category_id` (VARCHAR(255), PK)
- `category_name` (VARCHAR(100), UNIQUE) - Category name (e.g., 'Dining', 'Gas', 'Groceries')
- `category_code` (VARCHAR(50), UNIQUE) - Category code (e.g., 'DINING', 'GAS')
- `parent_category_id` (VARCHAR(255), FK → rewards_categories) - Parent category for hierarchy
- `merchant_category_codes` (TEXT) - Comma-separated MCC codes
- `is_bonus_category` (BOOLEAN) - Whether typically a bonus category
- `typical_multiplier` (NUMERIC(4, 2)) - Typical rewards multiplier

### card_rewards_structure
Maps credit cards to rewards categories with multipliers and limits.

**Key Columns:**
- `reward_structure_id` (VARCHAR(255), PK)
- `card_id` (VARCHAR(255), FK → credit_cards)
- `category_id` (VARCHAR(255), FK → rewards_categories)
- `rewards_multiplier` (NUMERIC(4, 2)) - Multiplier (e.g., 3.0 for 3x points)
- `rewards_type` (VARCHAR(50)) - 'Points', 'Cash Back', 'Miles'
- `points_per_dollar` (NUMERIC(6, 2)) - Points earned per dollar
- `cash_back_percentage` (NUMERIC(5, 2)) - Cash back percentage
- `annual_spend_limit` (NUMERIC(12, 2)) - Annual spending limit (NULL for unlimited)
- `quarterly_spend_limit` (NUMERIC(12, 2)) - Quarterly spending limit
- `monthly_spend_limit` (NUMERIC(12, 2)) - Monthly spending limit
- `effective_start_date` (DATE) - When rewards structure becomes effective
- `effective_end_date` (DATE) - When rewards structure expires
- `is_active` (BOOLEAN) - Whether rewards structure is currently active

### bank_offers
Stores targeted offers from banks (Amex Offers, Chase Offers, Bank of America, etc.).

**Key Columns:**
- `offer_id` (VARCHAR(255), PK)
- `issuer_id` (VARCHAR(255), FK → credit_card_issuers)
- `offer_name` (VARCHAR(255)) - Offer name
- `offer_description` (TEXT) - Detailed offer description
- `merchant_name` (VARCHAR(255)) - Merchant name
- `merchant_category` (VARCHAR(100)) - Merchant category
- `offer_type` (VARCHAR(50)) - 'Statement Credit', 'Points Bonus', 'Cash Back', 'Discount'
- `discount_amount` (NUMERIC(10, 2)) - Fixed discount amount
- `discount_percentage` (NUMERIC(5, 2)) - Percentage discount
- `minimum_spend` (NUMERIC(10, 2)) - Minimum spending requirement
- `maximum_discount` (NUMERIC(10, 2)) - Maximum discount cap
- `points_bonus_multiplier` (NUMERIC(4, 2)) - Bonus points multiplier
- `offer_start_date` (DATE) - Offer start date
- `offer_end_date` (DATE) - Offer end date
- `redemption_deadline` (DATE) - Redemption deadline
- `is_targeted` (BOOLEAN) - Whether offer is targeted to specific users
- `activation_required` (BOOLEAN) - Whether activation is required

### card_offer_eligibility
Maps which cards are eligible for specific bank offers.

**Key Columns:**
- `eligibility_id` (VARCHAR(255), PK)
- `offer_id` (VARCHAR(255), FK → bank_offers)
- `card_id` (VARCHAR(255), FK → credit_cards)
- `eligibility_status` (VARCHAR(50)) - 'Eligible', 'Not Eligible', 'Targeted'
- `activation_status` (VARCHAR(50)) - 'Activated', 'Not Activated', 'Expired'
- `activation_date` (DATE) - When offer was activated
- `redemption_count` (INTEGER) - Number of times offer was redeemed
- `total_savings` (NUMERIC(10, 2)) - Total savings from offer

### merchants
Stores merchant information for location-based card recommendations.

**Key Columns:**
- `merchant_id` (VARCHAR(255), PK)
- `merchant_name` (VARCHAR(255)) - Merchant name
- `merchant_category_code` (VARCHAR(10)) - MCC code
- `merchant_category` (VARCHAR(100)) - Category name
- `parent_merchant_id` (VARCHAR(255), FK → merchants) - Parent merchant for chains
- `is_chain` (BOOLEAN) - Whether merchant is a chain
- `chain_location_count` (INTEGER) - Number of locations

### merchant_locations
Stores physical locations of merchants for location-based recommendations.

**Key Columns:**
- `location_id` (VARCHAR(255), PK)
- `merchant_id` (VARCHAR(255), FK → merchants)
- `location_name` (VARCHAR(255)) - Location name
- `address_line1`, `address_line2` (VARCHAR(255)) - Address
- `city` (VARCHAR(100)) - City
- `state_code` (VARCHAR(2)) - State code
- `postal_code` (VARCHAR(20)) - ZIP code
- `latitude`, `longitude` (NUMERIC(10, 7)) - Coordinates
- `location_geom` (GEOGRAPHY) - Point geometry for geospatial queries
- `is_active` (BOOLEAN) - Whether location is active

### user_profiles
Stores user account information and preferences.

**Key Columns:**
- `user_id` (VARCHAR(255), PK)
- `username` (VARCHAR(100), UNIQUE) - Username
- `email` (VARCHAR(255), UNIQUE) - Email address
- `subscription_tier` (VARCHAR(50)) - 'Free', 'Plus', 'Premium'
- `subscription_expires_date` (DATE) - Subscription expiration
- `preferred_currency` (VARCHAR(3)) - Currency code, default 'USD'
- `location_latitude`, `location_longitude` (NUMERIC(10, 7)) - User location
- `location_geom` (GEOGRAPHY) - User location geometry
- `notification_preferences` (JSON) - Notification settings

### user_cards
Tracks which credit cards users own.

**Key Columns:**
- `user_card_id` (VARCHAR(255), PK)
- `user_id` (VARCHAR(255), FK → user_profiles)
- `card_id` (VARCHAR(255), FK → credit_cards)
- `account_status` (VARCHAR(50)) - 'Active', 'Closed', 'Suspended'
- `account_opened_date` (DATE) - Account opening date
- `account_closed_date` (DATE) - Account closing date
- `credit_limit` (NUMERIC(12, 2)) - Credit limit
- `current_balance` (NUMERIC(12, 2)) - Current balance
- `is_primary_card` (BOOLEAN) - Whether card is primary
- `card_nickname` (VARCHAR(255)) - User-defined nickname

### spending_transactions
Stores transaction history with rewards earned.

**Key Columns:**
- `transaction_id` (VARCHAR(255), PK)
- `user_id` (VARCHAR(255), FK → user_profiles)
- `user_card_id` (VARCHAR(255), FK → user_cards)
- `card_used_id` (VARCHAR(255), FK → credit_cards)
- `merchant_id` (VARCHAR(255), FK → merchants)
- `merchant_location_id` (VARCHAR(255), FK → merchant_locations)
- `transaction_date` (TIMESTAMP_NTZ) - Transaction timestamp
- `transaction_amount` (NUMERIC(12, 2)) - Transaction amount
- `category_id` (VARCHAR(255), FK → rewards_categories)
- `rewards_earned` (NUMERIC(10, 2)) - Rewards earned
- `rewards_multiplier_applied` (NUMERIC(4, 2)) - Multiplier used
- `rewards_type` (VARCHAR(50)) - 'Points', 'Cash Back', 'Miles'
- `offer_applied_id` (VARCHAR(255), FK → bank_offers) - Applied offer
- `offer_savings` (NUMERIC(10, 2)) - Savings from offer

### card_recommendations
Stores AI-generated card recommendations for users.

**Key Columns:**
- `recommendation_id` (VARCHAR(255), PK)
- `user_id` (VARCHAR(255), FK → user_profiles)
- `card_id` (VARCHAR(255), FK → credit_cards)
- `recommendation_type` (VARCHAR(50)) - 'New Card', 'Switch Card', 'Optimize Usage'
- `recommendation_reason` (TEXT) - Why card is recommended
- `estimated_annual_value` (NUMERIC(10, 2)) - Estimated annual value
- `confidence_score` (NUMERIC(5, 2)) - Confidence score (0-100)
- `recommendation_date` (DATE) - When recommendation was generated
- `user_action` (VARCHAR(50)) - 'Applied', 'Dismissed', 'Pending'

### cfpb_consumer_complaints
Stores CFPB consumer complaint data for issuer risk assessment.

**Key Columns:**
- `complaint_id` (VARCHAR(255), PK)
- `issuer_id` (VARCHAR(255), FK → credit_card_issuers)
- `complaint_date` (DATE) - Complaint date
- `product_type` (VARCHAR(100)) - Product type
- `issue_type` (VARCHAR(100)) - Issue category
- `sub_issue_type` (VARCHAR(100)) - Sub-issue category
- `complaint_narrative` (TEXT) - Complaint description
- `company_response` (VARCHAR(255)) - Company response
- `consumer_disputed` (BOOLEAN) - Whether consumer disputed response
- `zip_code` (VARCHAR(10)) - Consumer ZIP code
- `state_code` (VARCHAR(2)) - State code

### federal_reserve_credit_data
Stores Federal Reserve G.19 consumer credit statistics.

**Key Columns:**
- `data_id` (VARCHAR(255), PK)
- `report_date` (DATE) - Report date
- `data_type` (VARCHAR(50)) - 'Revolving', 'Non-Revolving', 'Total'
- `outstanding_amount_billions` (NUMERIC(12, 2)) - Outstanding amount in billions
- `month_over_month_change` (NUMERIC(10, 2)) - Month-over-month change
- `year_over_year_change` (NUMERIC(10, 2)) - Year-over-year change
- `data_source` (VARCHAR(50)) - 'FEDERAL_RESERVE_G19'

### rewards_optimization_analytics
Stores analytics and optimization metrics for rewards tracking.

**Key Columns:**
- `analytics_id` (VARCHAR(255), PK)
- `user_id` (VARCHAR(255), FK → user_profiles)
- `analysis_date` (DATE) - Analysis date
- `total_rewards_earned` (NUMERIC(10, 2)) - Total rewards earned
- `potential_rewards_optimized` (NUMERIC(10, 2)) - Potential rewards if optimized
- `optimization_opportunity` (NUMERIC(10, 2)) - Optimization opportunity amount
- `top_category` (VARCHAR(100)) - Top spending category
- `recommended_card_changes` (TEXT) - Recommended changes
- `analysis_metadata` (JSON) - Additional analysis metadata

## Relationships

- **credit_cards** → **credit_card_issuers** (many-to-one)
- **card_rewards_structure** → **credit_cards** (many-to-one)
- **card_rewards_structure** → **rewards_categories** (many-to-one)
- **bank_offers** → **credit_card_issuers** (many-to-one)
- **card_offer_eligibility** → **bank_offers** (many-to-one)
- **card_offer_eligibility** → **credit_cards** (many-to-one)
- **merchant_locations** → **merchants** (many-to-one)
- **user_cards** → **user_profiles** (many-to-one)
- **user_cards** → **credit_cards** (many-to-one)
- **spending_transactions** → **user_profiles** (many-to-one)
- **spending_transactions** → **user_cards** (many-to-one)
- **spending_transactions** → **credit_cards** (many-to-one)
- **spending_transactions** → **merchants** (many-to-one)
- **spending_transactions** → **merchant_locations** (many-to-one)
- **spending_transactions** → **rewards_categories** (many-to-one)
- **spending_transactions** → **bank_offers** (many-to-one)
- **card_recommendations** → **user_profiles** (many-to-one)
- **card_recommendations** → **credit_cards** (many-to-one)
- **cfpb_consumer_complaints** → **credit_card_issuers** (many-to-one)
- **rewards_optimization_analytics** → **user_profiles** (many-to-one)

## Indexes

The schema includes indexes on:
- Foreign key columns for join optimization
- Frequently queried columns (user_id, card_id, merchant_id, transaction_date)
- Geospatial columns (location_geom) for spatial queries
- Date columns for temporal queries

## Data Sources

- **CFPB Consumer Complaints**: Consumer Financial Protection Bureau complaint database
- **Federal Reserve G.19 Data**: Federal Reserve consumer credit statistics
- **Card Agreements**: Card issuer terms and agreements
- **Bank APIs**: Bank offer APIs (Amex Offers, Chase Offers, etc.)
- **Google Places API**: Merchant location data
- **Manual Entry**: User-provided data and preferences

---
**Last Updated:** 2026-02-04
