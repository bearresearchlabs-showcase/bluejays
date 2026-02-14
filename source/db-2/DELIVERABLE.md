# Database Deliverable: db-2 - Filling Station Retail / POS

**Database:** db-2
**Type:** Filling Station Retail / POS (phppos)
**Created:** 2026-02-09
**Status:** Complete

---

## Database Overview

### Description

Real-world retail Point-of-Sale (POS) database from a family business in Kenya, featuring complete transactional history, inventory management, and multi-location operations. Includes phppos schema with sales, line items, payments, inventory, products, and suppliers.

### Key Features

- Sales transactions and line items
- Payment records and inventory movements
- Product catalog and purchase orders
- Supplier receivings and multi-location support

### Database Platforms Supported

- **PostgreSQL**: Full support

---

## Database Schema Documentation

See `docs/SCHEMA.md` for full LUCASA schema. This deliverable uses a minimal 8-table subset: `phppos_people`, `phppos_employees`, `phppos_employees_locations`, `phppos_items`, `phppos_locations`, `phppos_location_items`, `phppos_sales`. ACID-compliant with PKs and FKs.

---

## SQL Queries

See `queries/queries.md` for all 30 production queries.

---

## Usage Instructions

Load schema.sql and data.sql into PostgreSQL. See docs/POSTGRES_MIGRATION.md for migration from MySQL format.
