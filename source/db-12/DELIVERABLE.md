# Database Deliverable: db-12 - Credit Card and Rewards Optimization System

**Database:** db-12
**Type:** Credit Card and Rewards Optimization System
**Created:** 2026-02-04
**Status:** Complete

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Database Schema Documentation](#database-schema-documentation)
3. [SQL Queries](#sql-queries)
4. [Usage Instructions](#usage-instructions)

---

## Database Overview

### Description

This database contains comprehensive credit card data for rewards optimization, card management, and portfolio analysis. The database mirrors the functionality of **CardPointers for Credit Cards** app, providing data-driven insights for maximizing credit card rewards and optimizing card portfolios.

### Key Features

- **Multi-Dimensional Rewards Optimization**: Analyzes card portfolios across multiple dimensions (categories, merchants, offers, time periods)
- **Location-Based Recommendations**: Uses geospatial data to recommend optimal cards at specific merchant locations
- **Bank Offers Management**: Tracks and optimizes bank offers (Amex Offers, Chase Offers, etc.)
- **Chase 5/24 Rule Tracking**: Monitors application history for Chase application strategy
- **Annual Fee ROI Analysis**: Calculates return on investment for card retention decisions
- **Signup Bonus Tracking**: Monitors progress toward signup bonus completion
- **Merchant-Specific Recommendations**: Recommends optimal cards for specific merchants based on spending history
- **Category Bonus Period Optimization**: Optimizes spending during rotating category bonus periods
- **CFPB Consumer Complaint Analysis**: Assesses issuer reputation based on complaint data
- **Federal Reserve Credit Trend Analysis**: Monitors market trends and credit statistics

### Database Platforms Supported

- **PostgreSQL**: Full support with standard SQL
- **Databricks**: Compatible with Delta Lake and distributed execution
- **Databricks**: Cloud data warehouse compatible

### Data Sources

- **CFPB Consumer Complaints**: Consumer Financial Protection Bureau complaint database
- **Federal Reserve G.19 Data**: Federal Reserve consumer credit statistics
- **Credit Card Data**: Card issuer websites, terms, and promotional materials
- **Merchant Data**: Merchant location databases and category mappings

---

## Database Schema Documentation

### Schema Overview

The database consists of **15 main tables** organized into logical groups:

1. **Core Card Data**: `credit_card_issuers`, `credit_cards`, `rewards_categories`, `card_rewards_structure`
2. **Bank Offers**: `bank_offers`, `card_offer_eligibility`
3. **Merchants and Locations**: `merchants`, `merchant_locations`
4. **User Data**: `user_profiles`, `user_cards`, `spending_transactions`, `card_recommendations`
5. **Regulatory Data**: `cfpb_consumer_complaints`, `federal_reserve_credit_data`
6. **Analytics**: `rewards_optimization_analytics`

### Table Relationships

```
credit_card_issuers (issuer_id)
    └── credit_cards (issuer_id)

credit_cards (card_id)
    ├── card_rewards_structure (card_id)
    ├── card_offer_eligibility (card_id)
    ├── user_cards (card_id)
    └── card_recommendations (card_id)

rewards_categories (category_id)
    └── card_rewards_structure (category_id)

bank_offers (offer_id)
    └── card_offer_eligibility (offer_id)

merchants (merchant_id)
    └── merchant_locations (merchant_id)

user_profiles (user_id)
    ├── user_cards (user_id)
    └── spending_transactions (user_id)

user_cards (user_card_id)
    └── spending_transactions (user_card_id)
```

### Entity-Relationship Diagram

```mermaid
erDiagram
    credit_card_issuers {
        varchar issuer_id PK "Primary key"
        varchar issuer_name "Issuer name"
        varchar issuer_type "Issuer type"
    }

    credit_cards {
        varchar card_id PK "Primary key"
        varchar issuer_id FK "Issuer"
        varchar card_name "Card name"
        numeric annual_fee "Annual fee"
    }

    rewards_categories {
        varchar category_id PK "Primary key"
        varchar category_name "Category name"
    }

    card_rewards_structure {
        varchar structure_id PK "Primary key"
        varchar card_id FK "Card"
        varchar category_id FK "Category"
        numeric multiplier "Rewards multiplier"
    }

    bank_offers {
        varchar offer_id PK "Primary key"
        varchar offer_name "Offer name"
        timestamp start_date "Start date"
        timestamp end_date "End date"
    }

    card_offer_eligibility {
        varchar eligibility_id PK "Primary key"
        varchar card_id FK "Card"
        varchar offer_id FK "Offer"
    }

    merchants {
        varchar merchant_id PK "Primary key"
        varchar merchant_name "Merchant name"
        varchar category "Merchant category"
    }

    merchant_locations {
        varchar location_id PK "Primary key"
        varchar merchant_id FK "Merchant"
        geography location_geom SPATIAL "Location geometry"
    }

    user_profiles {
        varchar user_id PK "Primary key"
        varchar username "Username"
        varchar email "Email"
    }

    user_cards {
        varchar user_card_id PK "Primary key"
        varchar user_id FK "User"
        varchar card_id FK "Card"
        timestamp opened_date "Opened date"
    }

    spending_transactions {
        varchar transaction_id PK "Primary key"
        varchar user_id FK "User"
        varchar user_card_id FK "User card"
        varchar merchant_id FK "Merchant"
        numeric amount "Transaction amount"
        timestamp transaction_date "Transaction date"
    }

    card_recommendations {
        varchar recommendation_id PK "Primary key"
        varchar user_id FK "User"
        varchar card_id FK "Card"
        numeric score "Recommendation score"
    }

    cfpb_consumer_complaints {
        varchar complaint_id PK "Primary key"
        varchar issuer_name "Issuer name"
        varchar complaint_type "Complaint type"
        timestamp complaint_date "Complaint date"
    }

    federal_reserve_credit_data {
        varchar data_id PK "Primary key"
        date data_date "Data date"
        numeric total_credit "Total credit"
    }

    rewards_optimization_analytics {
        varchar analytics_id PK "Primary key"
        varchar user_id FK "User"
        numeric potential_rewards "Potential rewards"
    }

    credit_card_issuers ||--o{ credit_cards : "issues"
    credit_cards ||--o{ card_rewards_structure : "has"
    credit_cards ||--o{ card_offer_eligibility : "eligible_for"
    credit_cards ||--o{ user_cards : "owned_by"
    credit_cards ||--o{ card_recommendations : "recommended"
    rewards_categories ||--o{ card_rewards_structure : "categorized_in"
    bank_offers ||--o{ card_offer_eligibility : "available_for"
    merchants ||--o{ merchant_locations : "has"
    merchants ||--o{ spending_transactions : "transacted_at"
    user_profiles ||--o{ user_cards : "owns"
    user_profiles ||--o{ spending_transactions : "makes"
    user_profiles ||--o{ card_recommendations : "receives"
    user_profiles ||--o{ rewards_optimization_analytics : "analyzed"
    user_cards ||--o{ spending_transactions : "used_for"
```

---

## SQL Queries

This database includes **30 extremely complex SQL queries** designed for production use with business-oriented use cases. All queries are:

- **Cross-database compatible**: Work on PostgreSQL
- **Production-grade**: Use advanced SQL patterns including CTEs, recursive CTEs, spatial operations, window functions, and complex aggregations
- **Business-focused**: Each query addresses specific client use cases (rewards optimization, card selection, portfolio management, etc.)
- **Fully runnable**: No placeholders - ready to execute
- **Well-documented**: Each query includes business use case, description, complexity notes, and expected output

### Query List

The complete list of 30 queries is available in `queries/queries.md`. Each query includes:

1. **Query Number and Title**
2. **Use Case**: Real-world application scenario
3. **Description**: What the query achieves
4. **Business Value**: What the query produces for clients
5. **Purpose**: Why this query is valuable
6. **Complexity**: Technical details (CTEs, spatial operations, window functions, etc.)
7. **SQL Code**: Complete, runnable SQL
8. **Expected Output**: Description of result set

### Query Categories

The queries cover the following business use cases:

1. **Rewards Optimization** (Queries 1, 6, 11, 16, 21, 26)
   - Multi-dimensional portfolio analysis
   - Opportunity cost calculations
   - Category-based optimization

2. **Location-Based Recommendations** (Queries 2, 7, 12, 17, 22, 27)
   - Geospatial card recommendations
   - Merchant-specific optimization
   - Regional spending patterns

3. **Bank Offers Management** (Queries 3, 8, 13, 18, 23, 28)
   - Offer tracking and activation
   - Eligibility optimization
   - Offer value analysis

4. **Application Strategy** (Queries 4, 9, 14, 19, 24, 29)
   - Chase 5/24 rule tracking
   - Application timing optimization
   - Portfolio expansion strategy

5. **Analytics and Reporting** (Queries 5, 10, 15, 20, 25, 30)
   - CFPB complaint analysis
   - Federal Reserve trend analysis
   - Performance metrics

### Accessing Queries

**Location**: `queries/queries.md`

**Format**: Each query is numbered sequentially (Query 1 through Query 30) and includes:
- Use case description
- Complete SQL code in code blocks
- Detailed technical descriptions
- Complexity annotations
- Expected output descriptions

---

## Usage Instructions

### For Data Scientists

#### Prerequisites

1. **Database Access**: Ensure you have access to the database instance (PostgreSQL)
2. **Credentials**: Obtain database connection credentials
3. **Schema**: Ensure all tables are created and populated with data

#### Running Queries

1. **Open Query File**: Navigate to `queries/queries.md`
2. **Select Query**: Choose the query number you want to execute
3. **Review Business Case**: Understand the use case and expected output
4. **Copy SQL**: Copy the SQL code from the code block
5. **Execute**: Run the query in your database client:
   - **PostgreSQL**: Use `psql` or pgAdmin
   - **Databricks**: Use Databricks SQL editor or notebook
   - **Databricks**: Use Databricks web interface or SnowSQL

#### Understanding Results

- Each query includes a "Use Case" section explaining the real-world application
- Review the "Business Value" section to understand what the query produces
- Check the "Expected Output" section for result set descriptions
- Spatial queries return geographic data that can be visualized on maps

### For Database Administrators

#### Schema Setup

1. **Create Tables**: Execute the schema creation scripts from `data/schema.sql`
2. **Load Data**: Populate tables with credit card data:
   - Credit card issuer and card data
   - Rewards categories and structures
   - Bank offers and eligibility
   - Merchant and location data
   - User profiles and transactions
   - CFPB complaint data
   - Federal Reserve credit data
3. **Verify**: Run validation queries to ensure data integrity

#### Performance Considerations

- **Indexes**: Ensure all indexes are created for optimal query performance
- **Partitioning**: Consider partitioning large tables (`spending_transactions`) by date
- **Monitoring**: Monitor query execution times
- **Optimization**: Review join strategies and consider query optimization

#### Cross-Database Compatibility

- **Spatial Types**: For location-based queries, use GEOGRAPHY type (PostgreSQL PostGIS) or GEOMETRY type (Databricks)
- **Standard SQL**: All queries use standard SQL syntax for maximum compatibility
- Test queries on your target database before production use

#### Data Loading

1. **Credit Card Data**: Load from issuer websites and promotional materials
2. **CFPB Data**: Use ETL pipelines to load complaint data from CFPB database
3. **Federal Reserve Data**: Load G.19 credit statistics from Federal Reserve
4. **Merchant Data**: Load merchant location databases and category mappings

---

## Additional Resources

- **Schema Documentation**: See `docs/SCHEMA.md` for detailed schema information
- **Data Dictionary**: See `docs/DATA_DICTIONARY.md` for column descriptions
- **Validation Reports**: See `results/` directory for query validation results
- **Query Metadata**: See `queries/queries.json` for programmatic access to queries
- **ETL Pipeline**: See `research/etl_elt_pipeline.ipynb` for data ingestion workflows

---

**Last Updated**: 2026-02-04
**Version**: 1.0
