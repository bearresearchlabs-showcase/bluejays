# Credit Card Database - Documentation

**Database:** db-12
**Created:** 2026-02-04

## Overview

This database contains comprehensive credit card data for rewards optimization, card management, and portfolio analysis. The database mirrors the functionality of CardPointers for Credit Cards app, providing data-driven insights for maximizing credit card rewards and optimizing card portfolios.

## Database Schema

See `../data/schema.sql` for the complete database schema.

### Key Tables

- **credit_card_issuers** - Credit card issuing banks and financial institutions
- **credit_cards** - Individual credit card products with features and terms
- **rewards_categories** - Rewards category definitions (dining, travel, gas, etc.)
- **card_rewards_structure** - Card-specific rewards multipliers and bonus categories
- **bank_offers** - Bank promotional offers and deals
- **card_offer_eligibility** - Card eligibility for specific offers
- **merchants** - Merchant information and locations
- **merchant_locations** - Physical merchant locations with geospatial data
- **user_profiles** - User account information and preferences
- **user_cards** - User's credit card accounts and status
- **spending_transactions** - Transaction history with rewards earned
- **card_recommendations** - AI-generated card recommendations
- **cfpb_consumer_complaints** - CFPB consumer complaint data
- **federal_reserve_credit_data** - Federal Reserve G.19 credit data
- **rewards_optimization_analytics** - Analytics and optimization metrics

## Queries

See `../queries/queries.md` for 30 extremely complex SQL queries covering:

- Multi-dimensional rewards optimization
- Location-based card recommendations
- Bank offers optimization
- CFPB consumer complaint analysis
- Federal Reserve credit data trends
- Chase 5/24 rule tracking
- Annual fee optimization
- Signup bonus tracking
- Merchant-specific recommendations
- Category bonus period optimization
- And 20+ additional credit card intelligence features

All queries are designed to work across:
- PostgreSQL
 (Delta Lake)


## Data Sources

- **CFPB Consumer Complaints**: Consumer Financial Protection Bureau complaint database
- **Federal Reserve G.19 Data**: Federal Reserve consumer credit statistics
- **Credit Card Data**: Card issuer websites, terms, and promotional materials
- **Merchant Data**: Merchant location databases and category mappings

## CardPointers Feature Mapping

This database replicates key CardPointers features:

1. **Rewards Optimization** - Multi-dimensional analysis of card portfolios
2. **Location-Based Recommendations** - Geospatial card recommendations for merchants
3. **Offer Management** - Bank offer tracking and activation
4. **Chase 5/24 Tracking** - Application strategy optimization
5. **Annual Fee Analysis** - ROI calculations for card retention decisions
6. **Signup Bonus Tracking** - Progress monitoring and spend allocation
7. **Merchant Recommendations** - Optimal card selection for specific merchants
8. **Category Rotations** - Quarterly bonus category optimization
9. **CFPB Analysis** - Issuer risk assessment based on complaint data
10. **Market Analysis** - Federal Reserve credit trend analysis

## Usage

1. Load schema: `psql -f data/schema.sql` (PostgreSQL)
2. Load data: `psql -f data/data.sql` (PostgreSQL)
3. Run queries: See `queries/queries.md`
4. Extract queries to JSON: `python3 scripts/extract_queries_to_json.py`
5. Run validation: See `scripts/` directory for validation scripts

## Database Compatibility

All schemas and queries are designed for cross-database compatibility:
- **PostgreSQL**: Full support with standard SQL
- **Databricks**: Delta Lake compatible with distributed execution
- **Databricks**: Cloud data warehouse compatible

## Business Value

This database enables:
- **$200-500 annual savings** through optimized card portfolio management
- **Maximized rewards** through strategic card selection and spending allocation
- **Risk mitigation** through issuer reputation analysis
- **Strategic timing** for card applications and bonus completion
- **Portfolio optimization** through data-driven decision making

---
**Last Updated:** 2026-02-04
