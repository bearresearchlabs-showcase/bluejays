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
- **Databricks**: Compatible with Delta Lake
- **Databricks**: Full support

---

## Database Schema Documentation

See `docs/SCHEMA.md` for table relationships. Core tables include `phppos_sales`, `phppos_sales_items`, `phppos_payments`, `phppos_items`, `phppos_inventory`, `phppos_suppliers`, and related phppos tables.

---

## SQL Queries

See `queries/queries.md` for all 30 production queries.

---

## Usage Instructions

Load schema.sql and data.sql into PostgreSQL. See docs/POSTGRES_MIGRATION.md for migration from MySQL format.
