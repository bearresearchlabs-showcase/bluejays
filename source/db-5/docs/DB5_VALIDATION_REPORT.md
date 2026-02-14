# DB-5 Validation Report – Lucasa POS Retail

**Rebuilt:** 2026-02-14  
**Database:** Lucasa POS Retail (Point-of-Sale System)  
**Location:** `source/db-5`

## Executive Summary

DB-5 is a minimal phppos Point-of-Sale schema derived from a real-world retail business (anonymized family business in Kenya). The deliverable contains **7 tables** with ACID-compliant constraints for PostgreSQL.

### Key Metrics
- **Tables**: 7 (phppos_people, phppos_employees, phppos_employees_locations, phppos_items, phppos_locations, phppos_location_items, phppos_sales)
- **Schema**: Minimal subset for gov-rebuilt data and queries
- **ACID**: Foreign keys and primary keys for referential integrity

## Database Structure

### Schema Overview
- **Database Type**: PostgreSQL
- **Character Set**: UTF-8
- **Total Tables**: 7
- **ACID**: Full referential integrity via FKs

### Core Tables

1. **People & Employees**
   - `phppos_people` — Base table for all persons
   - `phppos_employees` — Employee accounts (person_id PK, FK to people)
   - `phppos_employees_locations` — Employee–location assignments (composite PK, FKs)

2. **Products & Inventory**
   - `phppos_items` — Product catalog
   - `phppos_locations` — Store locations
   - `phppos_location_items` — Location-specific inventory (composite PK, FKs)

3. **Sales**
   - `phppos_sales` — Main sales transaction header (FKs to people, locations)

## Validation Status

### ✅ Documentation Files
- ✓ `docs/README.md` — Overview
- ✓ `docs/SCHEMA.md` — Schema documentation (phppos-aligned)
- ✓ `docs/DATA_DICTIONARY.md` — Column-level definitions (phppos-aligned)

### ✅ Database Files
- ✓ `data/schema.sql` — DDL with ACID constraints
- ✓ `deliverable/data/schema.sql` — Synced
- ✓ `app/DATABASE/schema.sql` — Synced

### ✅ SQL Queries
- ✓ `app/QUERIES/queries.md` — 30 production queries
- ✓ `app/QUERIES/queries.json` — Extracted query metadata

## ACID / Schema Alignment

### Referential Integrity
- `phppos_employees.person_id` → `phppos_people(person_id)`
- `phppos_employees_locations.employee_id` → `phppos_people(person_id)`
- `phppos_employees_locations.location_id` → `phppos_locations(location_id)`
- `phppos_location_items.location_id` → `phppos_locations(location_id)`
- `phppos_location_items.item_id` → `phppos_items(item_id)`
- `phppos_sales.employee_id` → `phppos_people(person_id)`
- `phppos_sales.customer_id` → `phppos_people(person_id)`
- `phppos_sales.location_id` → `phppos_locations(location_id)`

### Primary Keys
- `phppos_people.person_id`
- `phppos_employees.person_id`
- `phppos_employees_locations.(employee_id, location_id)`
- `phppos_items.item_id`
- `phppos_locations.location_id`
- `phppos_location_items.(location_id, item_id)`
- `phppos_sales.sale_id`

## Database Platforms Supported

- **PostgreSQL**: Full support
- **Databricks**: Compatible with Delta Lake

## Conclusion

DB-5 schema is aligned with the phppos POS model, ACID-compliant, and ready for production queries. Documentation and schema files are consistent across `data/`, `deliverable/`, and `app/`.

**Status**: ✅ Schema Validated | ✅ ACID Aligned | ✅ 30 Queries Complete
