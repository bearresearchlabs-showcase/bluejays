# Lucasa POS Database - Anonymized Dataset

A real-world retail Point-of-Sale (POS) database from a closed family business in Kenya, featuring complete transactional history, inventory management, and multi-location operations.

## 📊 Dataset Overview

**Domain**: Retail/Wholesale Point-of-Sale (POS)
**Industry**: Family retail business (closed)
**Location**: Kenya (includes eTIMS tax integration)
**Size**: 2.3M+ rows across 58 tables
**Format**: MySQL dump (anonymized)

### Key Metrics

- **Sales Transactions**: 312,000+
- **Sale Line Items**: 706,000+
- **Payment Records**: 318,000+
- **Inventory Movements**: 867,000+
- **Products**: 5,300+ catalog entries
- **Purchase Orders**: 32,000+ items
- **Supplier Receivings**: 4,300+ transactions

## 🗂️ Files Included

```
.
├── database/
│   ├── full_dump.sql          # Complete MySQL dump (225MB) - PRIMARY FILE
│   ├── schema.sql            # DDL statements only
│   └── data.sql              # INSERT statements only
│
├── documentation/
│   ├── SCHEMA.md             # Table relationships & ERD
│   └── DATA_DICTIONARY.md    # Column-level definitions
│
├── README.md                  # This file
├── PII_ANALYSIS.md           # PII anonymization details
└── POSTGRES_MIGRATION.md      # PostgreSQL/Databricks/Databricks migration guide
```

## 🚀 Quick Start

### MySQL (Primary Format - Fully Compatible)

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE lucasa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Import dump
mysql -u root -p lucasa < database/full_dump.sql

# Verify import
mysql -u root -p lucasa -e "SELECT COUNT(*) FROM phppos_sales;"
```

### PostgreSQL Migration (Recommended Method)

The database is provided in MySQL format. For PostgreSQL, we recommend using **pgloader** which handles all data type conversions automatically:

```bash
# Install pgloader
apt-get install pgloader  # or brew install pgloader

# Option 1: Direct MySQL to PostgreSQL migration (RECOMMENDED)
pgloader mysql://user:pass@localhost/lucasa \
         postgresql://user:pass@localhost/lucasa

# Option 2: Via intermediate MySQL container
docker run --name mysql-temp -e MYSQL_ROOT_PASSWORD=pass -d mysql:8.0
docker exec -i mysql-temp mysql -uroot -ppass < database/full_dump.sql
pgloader mysql://root:pass@localhost/lucasa \
         postgresql://postgres:pass@localhost/lucasa
```

See `POSTGRES_MIGRATION.md` for detailed migration instructions.

## 📋 Database Schema

### Core Modules

1. **Sales Management** (`phppos_sales*`)
   - Sales transactions with line items
   - Payments and refunds
   - Item kits (bundles)
   - Sales audit trail

2. **Inventory Management** (`phppos_inventory`, `phppos_location_items`)
   - Multi-location inventory tracking
   - Real-time stock levels
   - Inventory movement history (867K+ records)

3. **Purchasing/Receivings** (`phppos_receivings*`)
   - Purchase orders
   - Supplier receivings
   - Cost price tracking

4. **Product Catalog** (`phppos_items*`, `phppos_item_kits*`)
   - 5,300+ products
   - Item kits (product bundles)
   - Tiered pricing
   - Tax configurations

5. **People Management** (`phppos_people`, `phppos_employees`, `phppos_customers`, `phppos_suppliers`)
   - Employee records (anonymized)
   - Customer accounts
   - Supplier relationships

6. **Multi-Location** (`phppos_locations`, `phppos_location_items*`)
   - Multiple store locations
   - Location-specific pricing
   - Location-specific inventory

7. **Tax & Compliance** (`phppos_*_taxes`)
   - Kenya eTIMS integration fields
   - Tax calculations per line item
   - Audit trails

## 🔒 Privacy & Anonymization

All personal information has been anonymized:

- **✅ Anonymized**: Individual names, phone numbers, emails, addresses, usernames, passwords
- **✅ Preserved**: Company names, supplier information, geographic data (cities, countries)
- **✅ Retained**: All transactional and business data for analysis

See `PII_ANALYSIS.md` for complete details.

## 📈 Use Cases

This dataset is ideal for:

- **Database learning**: Complex real-world schema with proper foreign keys
- **SQL practice**: Joins, aggregations, window functions across millions of rows
- **Data analysis**: Sales trends, inventory optimization, customer behavior
- **ETL/Data Engineering**: Practice data pipelines and transformations
- **BI/Analytics**: Dashboard creation, reporting, KPI tracking
- **Application development**: Build POS interfaces, inventory systems
- **Database performance tuning**: Indexing, query optimization on real data
- **Multi-tenant architecture study**: Location-scoped data patterns
- **Database migration practice**: MySQL → PostgreSQL/Databricks/Databricks

## 🎓 Sample Queries

### Total Sales by Month
```sql
SELECT
    DATE_FORMAT(sale_time, '%Y-%m') as month,
    COUNT(*) as transactions,
    SUM(total) as revenue
FROM phppos_sales
WHERE deleted = 0
GROUP BY month
ORDER BY month DESC;
```

### Top Selling Products
```sql
SELECT
    i.name,
    i.category,
    COUNT(si.sale_id) as times_sold,
    SUM(si.quantity_purchased) as total_quantity,
    SUM(si.item_unit_price * si.quantity_purchased) as revenue
FROM phppos_sales_items si
JOIN phppos_items i ON si.item_id = i.item_id
GROUP BY i.item_id
ORDER BY revenue DESC
LIMIT 20;
```

### Inventory Value by Location
```sql
SELECT
    l.name as location,
    COUNT(DISTINCT li.item_id) as unique_products,
    SUM(li.quantity * i.cost_price) as inventory_value
FROM phppos_location_items li
JOIN phppos_items i ON li.item_id = i.item_id
JOIN phppos_locations l ON li.location_id = l.location_id
WHERE li.quantity > 0
GROUP BY l.location_id;
```

## 🏗️ Database Complexity Highlights

- **Composite Primary Keys**: Junction tables use multi-column PKs
- **Soft Deletes**: Most tables use `deleted` flag instead of hard deletes
- **Audit Trails**: Employee and sales audit tables track all changes
- **Tiered Pricing**: Per-employee and per-location price overrides
- **Multi-currency**: Support for different payment types
- **eTIMS Integration**: Kenya Revenue Authority tax compliance fields

## 📦 Table Count by Module

| Module | Tables | Key Tables |
|--------|--------|------------|
| Sales | 8 | phppos_sales, phppos_sales_items, phppos_sales_payments |
| Inventory | 3 | phppos_inventory, phppos_location_items |
| Products | 6 | phppos_items, phppos_item_kits, phppos_items_taxes |
| People | 4 | phppos_people, phppos_employees, phppos_customers |
| Receivings | 2 | phppos_receivings, phppos_receivings_items |
| Employee Overrides | 10 | phppos_employee_items, phppos_employee_sales |
| Location Overrides | 6 | phppos_location_items, phppos_location_item_kits |
| Other | 19 | Config, audit, permissions, etc. |

## 🔗 Foreign Key Relationships

The database features proper referential integrity with cascading deletes where appropriate. See `documentation/SCHEMA.md` for the complete ERD.

## ⚠️ Important Notes

1. **Timestamps**: All timestamps are UTC
2. **Deleted Records**: Most tables use soft deletes (`deleted = 1`)
3. **Currency**: Amounts are in Kenyan Shillings (KES)
4. **Decimal Precision**: Prices use DECIMAL(23,10) for accuracy
5. **Character Set**: UTF-8 (utf8mb4 in MySQL)
6. **Primary Format**: MySQL/MariaDB (production-ready)
7. **Migration Tools**: Use pgloader for PostgreSQL/Databricks/Databricks

## 📞 Support & Questions

For issues or questions about this dataset:
- Check `documentation/SCHEMA.md` for table relationships
- Check `documentation/DATA_DICTIONARY.md` for column definitions
- Review `PII_ANALYSIS.md` for anonymization details
- See `POSTGRES_MIGRATION.md` for migration to PostgreSQL/Databricks/Databricks

## 📜 License & Usage Rights

This dataset is from our family's private business (now closed). We have full rights to share this data. All personal information has been anonymized for privacy.

**Permitted Uses**: Education, research, portfolio projects, commercial applications, dataset benchmarks

---

**Generated**: February 2026
**Database Version**: MySQL 10.4.25-MariaDB / MySQL 8.0+
**Total Size**: 225MB MySQL dump
**Compatibility**: MySQL/MariaDB (native), PostgreSQL/Databricks/Databricks (via pgloader)
