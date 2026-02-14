# Data Dictionary - db-12

**Created:** 2026-02-04

## Overview

This data dictionary provides detailed descriptions of all columns in the credit card database. Tables are organized by functional category.

## Core Card Data

### credit_card_issuers

| Column | Data Type | Description |
|--------|-----------|-------------|
| issuer_id | VARCHAR(255) | Primary key, unique identifier for issuer |
| issuer_name | VARCHAR(255) | Full name of credit card issuer (e.g., 'Chase', 'American Express') |
| issuer_code | VARCHAR(50) | Unique issuer code for programmatic access |
| bank_type | VARCHAR(50) | Type of financial institution: 'National', 'Regional', 'Credit Union', 'Fintech' |
| country_code | VARCHAR(2) | ISO country code, default 'US' |
| website_url | VARCHAR(500) | Issuer website URL |
| customer_service_phone | VARCHAR(50) | Customer service phone number |
| total_cards_issued | INTEGER | Total number of credit cards issued by this issuer |
| market_share_percentage | NUMERIC(5, 2) | Market share percentage in credit card industry |
| cfpb_complaint_count | INTEGER | Total number of CFPB complaints against issuer |
| cfpb_complaint_resolution_rate | NUMERIC(5, 2) | Percentage of complaints resolved satisfactorily |
| data_source | VARCHAR(50) | Source of data: 'CFPB_API', 'MANUAL', etc. |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded into database |

### credit_cards

| Column | Data Type | Description |
|--------|-----------|-------------|
| card_id | VARCHAR(255) | Primary key, unique identifier for card |
| issuer_id | VARCHAR(255) | Foreign key to credit_card_issuers |
| card_name | VARCHAR(255) | Full name of credit card product |
| card_type | VARCHAR(50) | Card type: 'Cash Back', 'Travel', 'Points', 'Miles', 'Business', 'Secured' |
| annual_fee | NUMERIC(10, 2) | Annual fee amount in USD |
| annual_fee_waived_first_year | BOOLEAN | Whether annual fee is waived in first year |
| signup_bonus_points | INTEGER | Signup bonus points amount |
| signup_bonus_cash | NUMERIC(10, 2) | Signup bonus cash amount in USD |
| signup_bonus_spend_requirement | NUMERIC(10, 2) | Required spending to earn signup bonus |
| signup_bonus_timeframe_months | INTEGER | Number of months to meet spend requirement |
| apr_purchase | NUMERIC(5, 2) | Purchase APR percentage |
| apr_balance_transfer | NUMERIC(5, 2) | Balance transfer APR percentage |
| apr_cash_advance | NUMERIC(5, 2) | Cash advance APR percentage |
| foreign_transaction_fee_percentage | NUMERIC(5, 2) | Foreign transaction fee percentage |
| credit_score_min | INTEGER | Minimum credit score required |
| credit_score_max | INTEGER | Maximum credit score range |
| card_network | VARCHAR(50) | Card network: 'Visa', 'Mastercard', 'Amex', 'Discover' |
| card_level | VARCHAR(50) | Card tier: 'Standard', 'Gold', 'Platinum', 'Signature', 'Infinite' |
| metal_card | BOOLEAN | Whether card is made of metal |
| authorized_user_fee | NUMERIC(10, 2) | Fee for adding authorized users |
| card_agreement_url | VARCHAR(500) | URL to card terms and agreement |
| card_image_url | VARCHAR(500) | URL to card image |
| is_active | BOOLEAN | Whether card is currently available for new applications |
| launch_date | DATE | Card launch date |
| discontinued_date | DATE | Card discontinuation date (NULL if still available) |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

## Rewards Structure

### rewards_categories

| Column | Data Type | Description |
|--------|-----------|-------------|
| category_id | VARCHAR(255) | Primary key, unique identifier for category |
| category_name | VARCHAR(100) | Category name (e.g., 'Dining', 'Gas', 'Groceries') |
| category_code | VARCHAR(50) | Category code (e.g., 'DINING', 'GAS', 'GROCERIES') |
| parent_category_id | VARCHAR(255) | Foreign key to rewards_categories for hierarchy |
| category_description | TEXT | Detailed category description |
| merchant_category_codes | TEXT | Comma-separated MCC codes associated with category |
| is_bonus_category | BOOLEAN | Whether category is typically a bonus category |
| typical_multiplier | NUMERIC(4, 2) | Typical rewards multiplier for this category |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

### card_rewards_structure

| Column | Data Type | Description |
|--------|-----------|-------------|
| reward_structure_id | VARCHAR(255) | Primary key, unique identifier |
| card_id | VARCHAR(255) | Foreign key to credit_cards |
| category_id | VARCHAR(255) | Foreign key to rewards_categories |
| rewards_multiplier | NUMERIC(4, 2) | Rewards multiplier (e.g., 3.0 for 3x points) |
| rewards_type | VARCHAR(50) | Rewards type: 'Points', 'Cash Back', 'Miles' |
| points_per_dollar | NUMERIC(6, 2) | Points earned per dollar spent |
| cash_back_percentage | NUMERIC(5, 2) | Cash back percentage |
| annual_spend_limit | NUMERIC(12, 2) | Annual spending limit (NULL for unlimited) |
| quarterly_spend_limit | NUMERIC(12, 2) | Quarterly spending limit |
| monthly_spend_limit | NUMERIC(12, 2) | Monthly spending limit |
| effective_start_date | DATE | When rewards structure becomes effective |
| effective_end_date | DATE | When rewards structure expires |
| is_active | BOOLEAN | Whether rewards structure is currently active |
| promotion_description | TEXT | Description of promotion or bonus |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

## Bank Offers

### bank_offers

| Column | Data Type | Description |
|--------|-----------|-------------|
| offer_id | VARCHAR(255) | Primary key, unique identifier |
| issuer_id | VARCHAR(255) | Foreign key to credit_card_issuers |
| offer_name | VARCHAR(255) | Offer name |
| offer_description | TEXT | Detailed offer description |
| merchant_name | VARCHAR(255) | Merchant name for offer |
| merchant_category | VARCHAR(100) | Merchant category |
| offer_type | VARCHAR(50) | Offer type: 'Statement Credit', 'Points Bonus', 'Cash Back', 'Discount' |
| discount_amount | NUMERIC(10, 2) | Fixed discount amount |
| discount_percentage | NUMERIC(5, 2) | Percentage discount |
| minimum_spend | NUMERIC(10, 2) | Minimum spending requirement |
| maximum_discount | NUMERIC(10, 2) | Maximum discount cap |
| points_bonus_multiplier | NUMERIC(4, 2) | Bonus points multiplier |
| offer_start_date | DATE | Offer start date |
| offer_end_date | DATE | Offer end date |
| redemption_deadline | DATE | Redemption deadline |
| terms_and_conditions | TEXT | Terms and conditions |
| offer_url | VARCHAR(500) | URL to offer details |
| is_targeted | BOOLEAN | Whether offer is targeted to specific users |
| eligibility_criteria | TEXT | Eligibility criteria |
| activation_required | BOOLEAN | Whether activation is required |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

### card_offer_eligibility

| Column | Data Type | Description |
|--------|-----------|-------------|
| eligibility_id | VARCHAR(255) | Primary key, unique identifier |
| offer_id | VARCHAR(255) | Foreign key to bank_offers |
| card_id | VARCHAR(255) | Foreign key to credit_cards |
| eligibility_status | VARCHAR(50) | Status: 'Eligible', 'Not Eligible', 'Targeted' |
| activation_status | VARCHAR(50) | Activation status: 'Activated', 'Not Activated', 'Expired' |
| activation_date | DATE | When offer was activated |
| redemption_count | INTEGER | Number of times offer was redeemed |
| total_savings | NUMERIC(10, 2) | Total savings from offer |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

## Merchants and Locations

### merchants

| Column | Data Type | Description |
|--------|-----------|-------------|
| merchant_id | VARCHAR(255) | Primary key, unique identifier |
| merchant_name | VARCHAR(255) | Merchant name |
| merchant_category_code | VARCHAR(10) | MCC code |
| merchant_category | VARCHAR(100) | Category name |
| parent_merchant_id | VARCHAR(255) | Foreign key to merchants for chains |
| website_url | VARCHAR(500) | Merchant website URL |
| is_chain | BOOLEAN | Whether merchant is a chain |
| chain_location_count | INTEGER | Number of locations |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

### merchant_locations

| Column | Data Type | Description |
|--------|-----------|-------------|
| location_id | VARCHAR(255) | Primary key, unique identifier |
| merchant_id | VARCHAR(255) | Foreign key to merchants |
| location_name | VARCHAR(255) | Location name |
| address_line1 | VARCHAR(255) | Street address line 1 |
| address_line2 | VARCHAR(255) | Street address line 2 |
| city | VARCHAR(100) | City |
| state_code | VARCHAR(2) | State code |
| postal_code | VARCHAR(20) | ZIP code |
| country_code | VARCHAR(2) | Country code, default 'US' |
| latitude | NUMERIC(10, 7) | Latitude coordinate |
| longitude | NUMERIC(10, 7) | Longitude coordinate |
| location_geom | GEOGRAPHY | Point geometry for geospatial queries |
| phone_number | VARCHAR(50) | Phone number |
| is_active | BOOLEAN | Whether location is active |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

## User Data

### user_profiles

| Column | Data Type | Description |
|--------|-----------|-------------|
| user_id | VARCHAR(255) | Primary key, unique identifier |
| username | VARCHAR(100) | Username, unique |
| email | VARCHAR(255) | Email address, unique |
| subscription_tier | VARCHAR(50) | Subscription tier: 'Free', 'Plus', 'Premium' |
| subscription_expires_date | DATE | Subscription expiration date |
| preferred_currency | VARCHAR(3) | Currency code, default 'USD' |
| location_latitude | NUMERIC(10, 7) | User location latitude |
| location_longitude | NUMERIC(10, 7) | User location longitude |
| location_geom | GEOGRAPHY | User location geometry |
| notification_preferences | JSON | Notification settings |
| data_source | VARCHAR(50) | Source of data |
| created_timestamp | TIMESTAMP_NTZ | Account creation timestamp |
| updated_timestamp | TIMESTAMP_NTZ | Last update timestamp |

### user_cards

| Column | Data Type | Description |
|--------|-----------|-------------|
| user_card_id | VARCHAR(255) | Primary key, unique identifier |
| user_id | VARCHAR(255) | Foreign key to user_profiles |
| card_id | VARCHAR(255) | Foreign key to credit_cards |
| card_nickname | VARCHAR(100) | User-defined nickname |
| account_opening_date | DATE | Account opening date |
| account_status | VARCHAR(50) | Status: 'Active', 'Closed', 'Suspended' |
| credit_limit | NUMERIC(12, 2) | Credit limit |
| current_balance | NUMERIC(12, 2) | Current balance |
| available_credit | NUMERIC(12, 2) | Available credit |
| annual_fee_paid | NUMERIC(10, 2) | Annual fee paid |
| next_annual_fee_date | DATE | Next annual fee date |
| is_primary_card | BOOLEAN | Whether card is primary |
| chase_5_24_status | INTEGER | Chase 5/24 rule tracking (number of cards opened in last 24 months) |
| data_source | VARCHAR(50) | Source of data |
| created_timestamp | TIMESTAMP_NTZ | When record was created |
| updated_timestamp | TIMESTAMP_NTZ | Last update timestamp |

### spending_transactions

| Column | Data Type | Description |
|--------|-----------|-------------|
| transaction_id | VARCHAR(255) | Primary key, unique identifier |
| user_id | VARCHAR(255) | Foreign key to user_profiles |
| user_card_id | VARCHAR(255) | Foreign key to user_cards |
| merchant_id | VARCHAR(255) | Foreign key to merchants |
| location_id | VARCHAR(255) | Foreign key to merchant_locations |
| transaction_date | DATE | Transaction date |
| transaction_time | TIMESTAMP_NTZ | Transaction timestamp |
| transaction_amount | NUMERIC(10, 2) | Transaction amount |
| currency_code | VARCHAR(3) | Currency code, default 'USD' |
| category_id | VARCHAR(255) | Foreign key to rewards_categories |
| merchant_category_code | VARCHAR(10) | MCC code |
| rewards_earned | NUMERIC(10, 2) | Rewards earned |
| rewards_multiplier_applied | NUMERIC(4, 2) | Multiplier used |
| offer_applied_id | VARCHAR(255) | Foreign key to bank_offers |
| offer_savings | NUMERIC(10, 2) | Savings from offer |
| card_used_id | VARCHAR(255) | Card used for transaction |
| optimal_card_id | VARCHAR(255) | Best card that should have been used |
| potential_rewards_lost | NUMERIC(10, 2) | Potential rewards lost |
| transaction_description | VARCHAR(500) | Transaction description |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

### card_recommendations

| Column | Data Type | Description |
|--------|-----------|-------------|
| recommendation_id | VARCHAR(255) | Primary key, unique identifier |
| user_id | VARCHAR(255) | Foreign key to user_profiles |
| merchant_id | VARCHAR(255) | Foreign key to merchants |
| location_id | VARCHAR(255) | Foreign key to merchant_locations |
| category_id | VARCHAR(255) | Foreign key to rewards_categories |
| recommended_card_id | VARCHAR(255) | Foreign key to credit_cards |
| recommendation_reason | TEXT | Why card is recommended |
| expected_rewards | NUMERIC(10, 2) | Expected rewards |
| expected_multiplier | NUMERIC(4, 2) | Expected multiplier |
| applicable_offer_id | VARCHAR(255) | Foreign key to bank_offers |
| offer_savings | NUMERIC(10, 2) | Offer savings |
| recommendation_score | NUMERIC(5, 2) | Confidence score (0-100) |
| recommendation_timestamp | TIMESTAMP_NTZ | When recommendation was generated |
| recommendation_type | VARCHAR(50) | Type: 'Merchant', 'Category', 'Location', 'Offer' |
| is_active | BOOLEAN | Whether recommendation is active |

## Regulatory Data

### cfpb_consumer_complaints

| Column | Data Type | Description |
|--------|-----------|-------------|
| complaint_id | VARCHAR(255) | Primary key, unique identifier |
| complaint_date | DATE | Complaint date |
| complaint_submitted_date | DATE | When complaint was submitted |
| complaint_received_date | DATE | When complaint was received |
| product_type | VARCHAR(100) | Product type (e.g., 'Credit card') |
| sub_product | VARCHAR(100) | Sub-product category |
| issue_type | VARCHAR(100) | Issue category |
| sub_issue | VARCHAR(100) | Sub-issue category |
| consumer_complaint_narrative | TEXT | Complaint description |
| company_name | VARCHAR(255) | Company name |
| company_response | VARCHAR(255) | Company response |
| timely_response | BOOLEAN | Whether response was timely |
| consumer_disputed | BOOLEAN | Whether consumer disputed response |
| complaint_id_cfpb | VARCHAR(100) | CFPB complaint ID |
| zip_code | VARCHAR(20) | Consumer ZIP code |
| state_code | VARCHAR(2) | State code |
| tags | VARCHAR(255) | Complaint tags |
| consumer_consent_provided | BOOLEAN | Whether consumer consent was provided |
| submitted_via | VARCHAR(50) | Submission method |
| date_sent_to_company | DATE | Date sent to company |
| company_public_response | TEXT | Public response from company |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

### federal_reserve_credit_data

| Column | Data Type | Description |
|--------|-----------|-------------|
| data_id | VARCHAR(255) | Primary key, unique identifier |
| report_date | DATE | Report date |
| release_date | DATE | Release date |
| data_type | VARCHAR(50) | Type: 'Revolving', 'Non-Revolving', 'Total' |
| credit_outstanding_billions | NUMERIC(15, 2) | Outstanding credit in billions |
| credit_outstanding_seasonally_adjusted_billions | NUMERIC(15, 2) | Seasonally adjusted outstanding credit |
| credit_flow_billions | NUMERIC(15, 2) | Credit flow in billions |
| credit_flow_seasonally_adjusted_billions | NUMERIC(15, 2) | Seasonally adjusted credit flow |
| interest_rate_avg | NUMERIC(5, 2) | Average interest rate |
| interest_rate_weighted_avg | NUMERIC(5, 2) | Weighted average interest rate |
| data_source | VARCHAR(50) | Source of data |
| load_timestamp | TIMESTAMP_NTZ | When data was loaded |

## Analytics

### rewards_optimization_analytics

| Column | Data Type | Description |
|--------|-----------|-------------|
| analytics_id | VARCHAR(255) | Primary key, unique identifier |
| user_id | VARCHAR(255) | Foreign key to user_profiles |
| analysis_date | DATE | Analysis date |
| total_spending | NUMERIC(12, 2) | Total spending |
| total_rewards_earned | NUMERIC(10, 2) | Total rewards earned |
| potential_rewards_lost | NUMERIC(10, 2) | Potential rewards lost |
| optimization_score | NUMERIC(5, 2) | Percentage of optimal rewards captured |
| top_category_id | VARCHAR(255) | Foreign key to rewards_categories |
| top_category_spending | NUMERIC(12, 2) | Top category spending |
| top_card_id | VARCHAR(255) | Foreign key to credit_cards |
| top_card_rewards | NUMERIC(10, 2) | Top card rewards |
| offers_activated_count | INTEGER | Number of offers activated |
| offers_savings_total | NUMERIC(10, 2) | Total savings from offers |
| analysis_timestamp | TIMESTAMP_NTZ | When analysis was performed |

---
**Last Updated:** 2026-02-04
