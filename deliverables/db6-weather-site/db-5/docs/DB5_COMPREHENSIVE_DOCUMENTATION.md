# DB-5 Comprehensive Documentation - Filling Station POS System

**Database Name:** Lucasa Filling Station POS
**Database Type:** Point-of-Sale (POS) and Inventory Management System
**Location:** `/Users/machine/Documents/AQ/db/db-5`
**Rebuilt:** 2026-02-03

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Database Overview](#database-overview)
3. [Schema Documentation](#schema-documentation)
4. [SQL Queries Documentation](#sql-queries-documentation)
5. [Validation Results](#validation-results)
6. [Query Descriptions](#query-descriptions)
7. [Usage Instructions](#usage-instructions)
8. [Technical Specifications](#technical-specifications)

---

## Executive Summary

DB-5 is a **production-ready Point-of-Sale (POS) database system** from a real-world retail business (closed family business in Kenya). The database contains **2.3M+ rows** across **58 tables** with complete transactional history, inventory management, and multi-location operations.

### Key Statistics
- **Total Tables**: 58
- **Total Rows**: 2,346,975+
- **Sales Transactions**: 312,000+
- **Sale Line Items**: 706,000+
- **Payment Records**: 318,000+
- **Inventory Movements**: 867,000+
- **Products**: 5,300+ catalog entries
- **Purchase Orders**: 32,000+ items
- **Supplier Receivings**: 4,300+ transactions
- **Database Size**: 225MB MySQL dump

### Validation Status
- ✅ **30 SQL Queries Created**: All production-grade complexity
- ✅ **Validation Status**: PASS
- ✅ **Average Complexity**: Meets requirements (>=12.5/13)
- ✅ **Documentation**: Complete

---

## Database Overview

### Business Context

LUCASA is a comprehensive Point of Sale system for a mini-supermarket operation. The database manages:
- Sales transactions and payments
- Inventory tracking across multiple locations
- Product and item kit management
- Customer and supplier relationships
- Employee management and permissions
- Store accounts and gift cards
- Tax calculations and pricing tiers
- Integration with eTIMS (Electronic Tax Invoice Management System) for Kenya

### Database Architecture

**Engine:** MySQL/InnoDB
**Character Set:** UTF-8 (utf8mb4_unicode_ci)
**Storage Engine:** InnoDB (supports transactions and foreign keys)
**Decimal Precision:** `decimal(23,10)` for financial values
**Primary Format:** MySQL/MariaDB (production-ready)

### Core Design Principles

1. **Multi-Location Support**: Multiple store locations with location-specific pricing and inventory
2. **Flexible Pricing**: Supports multiple price tiers, location-based pricing, employee-specific pricing, and promotional pricing
3. **Comprehensive Tax System**: Up to 5 different tax rates per transaction with cumulative tax support
4. **Audit Trail**: Tracks changes to employees and sales with full audit history
5. **Soft Deletes**: Most tables use a `deleted` flag instead of hard deletes to preserve data integrity
6. **ERP Integration**: Built-in support for external ERP system integration
7. **eTIMS Compliance**: Integrated support for Kenya's tax invoice management system

---

## Schema Documentation

### Module Groupings

#### 1. People & Accounts Module (6 tables)
- `phppos_people` - Base table for all persons (customers, employees, suppliers, expenses)
- `phppos_customers` - Customer-specific information and account balances
- `phppos_employees` - Employee login credentials and settings
- `phppos_employees_audit` - Audit trail for employee changes
- `phppos_employees_locations` - Employee-to-location assignments
- `phppos_suppliers` - Supplier information
- `phppos_expenses` - Expense tracking linked to people

#### 2. Products & Inventory Module (9 tables)
- `phppos_items` - Individual product/item definitions (5,300+ products)
- `phppos_items_taxes` - Tax configurations for items
- `phppos_items_tier_prices` - Tier-based pricing for items
- `phppos_item_kits` - Product bundles/kits
- `phppos_item_kits_taxes` - Tax configurations for item kits
- `phppos_item_kits_tier_prices` - Tier-based pricing for item kits
- `phppos_item_kit_items` - Items contained within kits
- `phppos_inventory` - Inventory transaction history (867K+ records)
- `phppos_giftcards` - Gift card balances and tracking

#### 3. Location-Based Pricing & Inventory Module (6 tables)
- `phppos_location_items` - Location-specific item pricing and inventory
- `phppos_location_items_taxes` - Location-specific item tax overrides
- `phppos_location_items_tier_prices` - Location-specific tier pricing for items
- `phppos_location_item_kits` - Location-specific item kit pricing
- `phppos_location_item_kits_taxes` - Location-specific item kit tax overrides
- `phppos_location_item_kits_tier_prices` - Location-specific tier pricing for item kits

#### 4. Employee-Based Pricing & Inventory Module (10 tables)
- `phppos_employee_items` - Employee-specific item pricing and inventory
- `phppos_employee_items_taxes` - Employee-specific item tax configurations
- `phppos_employee_items_tier_prices` - Employee-specific tier pricing for items
- `phppos_employee_item_kits` - Employee-specific item kit pricing
- `phppos_employee_item_kits_taxes` - Employee-specific item kit tax configurations
- `phppos_employee_item_kits_tier_prices` - Employee-specific tier pricing for item kits
- `phppos_employee_inventory` - Employee-specific inventory transactions
- `phppos_employee_sales` - Employee sales transaction header
- `phppos_employee_sales_items` - Items in employee sales
- `phppos_employee_sales_payments` - Payments for employee sales

#### 5. Sales Module (8 tables)
- `phppos_sales` - Main sales transaction header (312K+ transactions)
- `phppos_sales_audit` - Audit trail for sales changes
- `phppos_sales_items` - Individual items sold in a transaction (706K+ line items)
- `phppos_sales_items_taxes` - Taxes applied to sold items
- `phppos_sales_item_kits` - Item kits sold in a transaction
- `phppos_sales_item_kits_taxes` - Taxes applied to sold item kits
- `phppos_sales_payments` - Payment methods and amounts for sales (318K+ payments)
- `phppos_store_accounts` - Customer store account transactions

#### 6. Receiving/Purchasing Module (2 tables)
- `phppos_receivings` - Receiving transaction header
- `phppos_receivings_items` - Line items for receiving transactions

#### 7. Allocations Module (2 tables)
- `phppos_allocations` - Allocation transaction header
- `phppos_allocations_items` - Items allocated in transaction

#### 8. System & Configuration Module (15 tables)
- `phppos_app_config` - Application configuration key-value pairs
- `phppos_app_files` - File storage (logos, images)
- `phppos_locations` - Store location definitions
- `phppos_modules` - System module definitions
- `phppos_modules_actions` - Available actions within modules
- `phppos_permissions` - User permissions by module
- `phppos_permissions_actions` - User permissions for specific actions
- `phppos_price_tiers` - Price tier definitions
- `phppos_register_log` - Cash register open/close log
- `phppos_sessions` - User session management
- `phppos_admin_otp` - One-time passwords for admin access

### Key Relationships

**People Relationships:**
- `phppos_customers.person_id` → `phppos_people.person_id`
- `phppos_employees.person_id` → `phppos_people.person_id`
- `phppos_suppliers.person_id` → `phppos_people.person_id`

**Sales Relationships:**
- `phppos_sales.customer_id` → `phppos_customers.person_id`
- `phppos_sales.employee_id` → `phppos_employees.person_id`
- `phppos_sales.location_id` → `phppos_locations.location_id`
- `phppos_sales_items.sale_id` → `phppos_sales.sale_id`
- `phppos_sales_items.item_id` → `phppos_items.item_id`
- `phppos_sales_payments.sale_id` → `phppos_sales.sale_id`

**Inventory Relationships:**
- `phppos_inventory.trans_items` → `phppos_items.item_id`
- `phppos_inventory.trans_user` → `phppos_employees.person_id`
- `phppos_inventory.location_id` → `phppos_locations.location_id`
- `phppos_location_items.item_id` → `phppos_items.item_id`
- `phppos_location_items.location_id` → `phppos_locations.location_id`

**Receiving Relationships:**
- `phppos_receivings.supplier_id` → `phppos_suppliers.person_id`
- `phppos_receivings.employee_id` → `phppos_employees.person_id`
- `phppos_receivings.location_id` → `phppos_locations.location_id`
- `phppos_receivings_items.receiving_id` → `phppos_receivings.receiving_id`
- `phppos_receivings_items.item_id` → `phppos_items.item_id`

---

## SQL Queries Documentation

### Overview

DB-5 contains **30 production-grade SQL queries** designed for comprehensive analysis of the POS system. All queries are:
- **Extremely Complex**: Average complexity >= 12.5/13
- **Production-Ready**: Suitable for enterprise use
- **Cross-Database Compatible**: Work with PostgreSQL
- **Well-Documented**: Each query includes description and complexity breakdown

### Query File Location

- **Primary Location**: `db-5/queries/queries.md`
- **Source Location**: `db-5/_Filling_Station_POS/QUERIES/queries.md`
- **File Size**: 283KB (282,984 bytes)
- **Total Queries**: 30

### Query Complexity Features

Each query implements:
- ✅ **Recursive CTEs**: For hierarchical and chain tracking
- ✅ **Multiple Nested CTEs**: 8+ levels deep
- ✅ **Window Functions**: With ROWS and RANGE frame clauses
- ✅ **Correlated Subqueries**: For advanced analytics
- ✅ **UNION Operations**: Combining multiple result sets
- ✅ **Pivot CASE Statements**: For classification and categorization
- ✅ **Complex Joins**: Multiple table relationships
- ✅ **Aggregations**: GROUP BY, HAVING, SUM, AVG, COUNT, etc.
- ✅ **Ranking Functions**: ROW_NUMBER, RANK, DENSE_RANK, PERCENT_RANK, NTILE

---

## Query Descriptions

### Query 1: Sales Hierarchy Analysis
**Purpose:** Analyze customer purchase patterns with recursive CTE tracking sales chains
**Tables Used:** `phppos_sales`, `phppos_customers`, `phppos_people`, `phppos_sales_payments`, `phppos_sales_items`
**Key Features:** Customer loyalty categorization, sales path tracking, window functions for rolling averages

### Query 2: Inventory Movement Analysis
**Purpose:** Track inventory movements with recursive chain analysis
**Tables Used:** `phppos_inventory`, `phppos_location_items`
**Key Features:** Inventory chain depth tracking, movement size categorization, location-based analytics

### Query 3: Product Sales Performance
**Purpose:** Analyze individual product sales performance
**Tables Used:** `phppos_sales_items`, `phppos_sales`, `phppos_items`
**Key Features:** Product performance metrics, sales trends, window functions for ranking

### Query 4: Customer Purchase Patterns
**Purpose:** Analyze customer purchase behavior and patterns
**Tables Used:** `phppos_sales`, `phppos_customers`, `phppos_people`
**Key Features:** Purchase frequency analysis, customer segmentation, temporal patterns

### Query 5: Employee Sales Performance
**Purpose:** Track employee sales performance and productivity
**Tables Used:** `phppos_sales`, `phppos_employees`, `phppos_people`
**Key Features:** Employee ranking, sales volume analysis, performance metrics

### Query 6: Location Revenue Analysis
**Purpose:** Analyze revenue by location with payment method breakdown
**Tables Used:** `phppos_sales_payments`, `phppos_sales`, `phppos_locations`
**Key Features:** Location-based revenue tracking, payment method analysis, time-series revenue

### Query 7: Product Inventory Tracking
**Purpose:** Track product inventory levels across locations
**Tables Used:** `phppos_location_items`, `phppos_items`, `phppos_locations`
**Key Features:** Multi-location inventory tracking, stock level analysis, reorder point monitoring

### Query 8: Supplier Receiving Patterns
**Purpose:** Analyze supplier receiving patterns and purchase orders
**Tables Used:** `phppos_receivings`, `phppos_suppliers`, `phppos_people`
**Key Features:** Supplier performance, receiving frequency, cost analysis

### Query 9: Tax Calculation Analysis
**Purpose:** Analyze tax calculations and compliance
**Tables Used:** `phppos_sales_items_taxes`, `phppos_sales_items`, `phppos_sales`
**Key Features:** Tax rate analysis, cumulative tax calculations, compliance tracking

### Query 10: Item Kit Sales Analysis
**Purpose:** Analyze sales of product bundles/kits
**Tables Used:** `phppos_sales_item_kits`, `phppos_sales`, `phppos_item_kits`
**Key Features:** Kit performance metrics, bundle sales trends, profitability analysis

### Query 11: Payment Method Analysis
**Purpose:** Analyze payment methods and transaction patterns
**Tables Used:** `phppos_sales_payments`
**Key Features:** Payment method distribution, transaction volume by method, time-based payment trends

### Query 12: Customer Account Balance
**Purpose:** Track customer store account balances and transactions
**Tables Used:** `phppos_store_accounts`, `phppos_customers`, `phppos_sales`
**Key Features:** Account balance tracking, credit analysis, payment history

### Query 13: Employee Location Assignment
**Purpose:** Analyze employee assignments across locations
**Tables Used:** `phppos_employees_locations`, `phppos_employees`, `phppos_locations`
**Key Features:** Multi-location employee tracking, assignment patterns, coverage analysis

### Query 14: Product Tier Pricing
**Purpose:** Analyze tier-based pricing strategies
**Tables Used:** `phppos_items_tier_prices`, `phppos_items`, `phppos_price_tiers`
**Key Features:** Tier pricing analysis, discount strategies, customer segment pricing

### Query 15: Location Item Pricing
**Purpose:** Analyze location-specific pricing variations
**Tables Used:** `phppos_location_items`, `phppos_items`, `phppos_locations`
**Key Features:** Location pricing strategies, price variance analysis, competitive positioning

### Query 16: Employee Item Pricing
**Purpose:** Analyze employee-specific pricing overrides
**Tables Used:** `phppos_employee_items`, `phppos_items`, `phppos_employees`
**Key Features:** Employee pricing authority, discount analysis, commission tracking

### Query 17: Sales Audit Trail
**Purpose:** Analyze sales modification audit history
**Tables Used:** `phppos_sales_audit`, `phppos_sales`
**Key Features:** Change tracking, audit compliance, modification patterns

### Query 18: Employee Audit Trail
**Purpose:** Analyze employee record changes and audit history
**Tables Used:** `phppos_employees_audit`, `phppos_employees`
**Key Features:** Employee change tracking, security audit, compliance monitoring

### Query 19: Gift Card Transactions
**Purpose:** Analyze gift card usage and balances
**Tables Used:** `phppos_giftcards`, `phppos_customers`
**Key Features:** Gift card redemption patterns, balance tracking, customer engagement

### Query 20: Register Log Analysis
**Purpose:** Analyze cash register shift logs and cash management
**Tables Used:** `phppos_register_log`, `phppos_employees`
**Key Features:** Shift analysis, cash reconciliation, register performance

### Query 21: Allocation Transactions
**Purpose:** Analyze stock allocation between employees/locations
**Tables Used:** `phppos_allocations`, `phppos_employees`, `phppos_locations`
**Key Features:** Allocation patterns, stock movement tracking, transfer analysis

### Query 22: Expense Tracking
**Purpose:** Analyze business expenses and cost tracking
**Tables Used:** `phppos_expenses`, `phppos_people`
**Key Features:** Expense categorization, cost analysis, budget tracking

### Query 23: Item Tax Configuration
**Purpose:** Analyze item-level tax configurations
**Tables Used:** `phppos_items_taxes`, `phppos_items`
**Key Features:** Tax rate analysis, tax compliance, product tax categorization

### Query 24: Location Item Tax
**Purpose:** Analyze location-specific tax overrides
**Tables Used:** `phppos_location_items_taxes`, `phppos_location_items`
**Key Features:** Location tax variations, compliance tracking, tax optimization

### Query 25: Employee Item Tax
**Purpose:** Analyze employee-specific tax configurations
**Tables Used:** `phppos_employee_items_taxes`, `phppos_employee_items`
**Key Features:** Employee tax authority, tax override analysis, compliance

### Query 26: Item Kit Items
**Purpose:** Analyze item kit composition and bundling
**Tables Used:** `phppos_item_kit_items`, `phppos_item_kits`, `phppos_items`
**Key Features:** Kit composition analysis, bundle profitability, product relationships

### Query 27: Location Item Kit Pricing
**Purpose:** Analyze location-specific kit pricing
**Tables Used:** `phppos_location_item_kits`, `phppos_item_kits`, `phppos_locations`
**Key Features:** Location kit pricing strategies, bundle pricing variations

### Query 28: Employee Item Kit Pricing
**Purpose:** Analyze employee-specific kit pricing overrides
**Tables Used:** `phppos_employee_item_kits`, `phppos_item_kits`, `phppos_employees`
**Key Features:** Employee kit pricing authority, bundle discount analysis

### Query 29: Sales Item Kits Taxes
**Purpose:** Analyze tax calculations for item kits in sales
**Tables Used:** `phppos_sales_item_kits_taxes`, `phppos_sales_item_kits`
**Key Features:** Kit tax calculations, cumulative tax analysis, compliance

### Query 30: Employee Sales Items
**Purpose:** Analyze items sold in employee-specific sales
**Tables Used:** `phppos_employee_sales_items`, `phppos_employee_sales`
**Key Features:** Employee sales item analysis, performance tracking, product mix

---

## Validation Results

### Query Validation Summary

**Validation Date:** 2026-02-03
**Status:** ✅ **PASS**

| Metric | Value |
|--------|-------|
| Total Queries | 30 |
| Unique Queries | 30 |
| Queries with Recursive CTEs | 30 |
| Queries with Window Functions | 30 |
| Queries with Joins | 30 |
| Queries with Aggregations | 30 |
| Extremely Complex Queries | 30 |
| Overall Status | PASS |

### Complexity Analysis

All 30 queries meet the production-grade complexity requirements:
- ✅ Recursive CTEs: 100% coverage
- ✅ Window Functions: 100% coverage
- ✅ Multiple Nested CTEs: 8+ levels
- ✅ Correlated Subqueries: Present in all queries
- ✅ UNION Operations: Present in all queries
- ✅ Pivot CASE Statements: Present in all queries

### Cross-Database Compatibility

**PostgreSQL:** ✅ Fully compatible
**Databricks:** ⚠️ Some ARRAY operations may need adaptation
**Databricks:** ⚠️ Some ARRAY operations may need adaptation

**Note:** Queries use PostgreSQL-specific `ARRAY[...]` syntax. For Databricks/Databricks compatibility:
- Replace `ARRAY[id]` with `ARRAY_CONSTRUCT(id)`
- Replace `array_length(path, 1)` with `ARRAY_SIZE(path)`  or `SIZE(path)` (Databricks)

---

## Usage Instructions

### Running Queries

1. **Setup Database:**
   ```bash
   # MySQL/MariaDB (Primary Format)
   mysql -u root -p -e "CREATE DATABASE lucasa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   mysql -u root -p lucasa < _Filling_Station_POS/DATABASE/full_dump.sql

   # PostgreSQL (via pgloader)
   pgloader mysql://user:pass@localhost/lucasa \
            postgresql://user:pass@localhost/lucasa
   ```

2. **Extract Queries:**
   ```bash
   # Queries are in: db-5/queries/queries.md
   # Each query is marked with ## Query N:
   ```

3. **Execute Queries:**
   ```sql
   -- Copy query SQL from queries.md
   -- Execute in your database client
   -- Results will include comprehensive analytics
   ```

### Query Testing

Use the testing framework:
```bash
cd /Users/machine/Documents/AQ/db
python3 -m pytest db-5/query_testing.ipynb  # When created
# Or use the test_queries.py framework
```

---

## Technical Specifications

### Database Requirements

- **MySQL/MariaDB**: 8.0+ (Primary format)
- **PostgreSQL**: 12+ (via migration)
- **Databricks**: Delta Lake compatible (with ARRAY adaptations)
- **Databricks**: Compatible (with ARRAY adaptations)

### Query Performance

- **Average Query Size**: ~9KB per query
- **Total Queries Size**: 283KB
- **Expected Execution Time**: Varies by query complexity and data volume
- **Optimization**: Queries include window functions optimized for large datasets

### Data Characteristics

- **Time Range**: Historical data from closed business
- **Data Quality**: Production data, anonymized
- **Currency**: Kenyan Shillings (KES)
- **Tax System**: Kenya eTIMS integration
- **Multi-Location**: Yes (multiple store locations)

---

## Additional Resources

### Documentation Files

- `README.md` - Database overview and quick start
- `SCHEMA.md` - Complete schema documentation (60KB)
- `DATA_DICTIONARY.md` - Column-level definitions (65KB)
- `POSTGRES_MIGRATION.md` - Migration guide for PostgreSQL/Databricks/Databricks
- `DB5_VALIDATION_REPORT.md` - Validation summary
- `DB5_COMPREHENSIVE_DOCUMENTATION.md` - This file

### Database Files

- `full_dump.sql` - Complete MySQL dump (225MB)
- `schema.sql` - DDL statements only (5.5KB)
- `data.sql` - INSERT statements only (1.1MB)

### Query Files

- `queries/queries.md` - All 30 SQL queries (283KB)
- `query_validation_report.json` - Validation results

---

## Conclusion

DB-5 is a comprehensive, production-ready POS database with:
- ✅ **58 well-structured tables**
- ✅ **2.3M+ rows of real-world data**
- ✅ **30 production-grade SQL queries**
- ✅ **Complete documentation**
- ✅ **Validation passed**

The database is ready for:
- SQL learning and practice
- Data analysis and reporting
- Application development
- Performance optimization
- Database migration practice
- Business intelligence dashboards

---

**Document Rebuilt:** 2026-02-03
**Database Version:** MySQL 10.4.25-MariaDB / MySQL 8.0+
**Total Database Size:** 225MB MySQL dump
**Compatibility:** MySQL/MariaDB (native), PostgreSQL/Databricks/Databricks (via migration)
