# Database Deliverable: db-3 - Hierarchical Orders

**Database:** db-3
**Type:** Hierarchical Orders (LinkWay)
**Created:** 2026-02-09
**Status:** Complete

---

## Database Overview

### Description

LinkWay Live database export with hierarchical order structure. Structured export from PostgreSQL (Django backend) with schema and data for local analysis, backups, and migrations.

### Key Features

- Hierarchical order management
- Django backend schema
- Full schema and data export

### Database Platforms Supported

- **PostgreSQL**: Full support
- **Databricks**: Compatible with Delta Lake
- **Databricks**: Full support

---

## Database Schema Documentation

See `docs/SCHEMA.md` for table relationships. Includes `orders_order` view and hierarchical order tables.

---

## SQL Queries

See `queries/queries.md` for all 30 production queries.

---

## Usage Instructions

Load schema.sql and data.sql. See docs/README.md for restoration options.
