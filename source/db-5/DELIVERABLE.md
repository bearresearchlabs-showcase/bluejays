# Database Deliverable: db-5 - POS Retail

**Database:** db-5
**Type:** POS Retail (Lucasa)
**Created:** 2026-02-09
**Status:** Complete

---

## Database Overview

### Description

Lucasa POS database - anonymized retail Point-of-Sale dataset from a family business in Kenya. Complete transactional history, inventory management, and multi-location operations with phppos schema.

### Key Features

- Sales transactions and line items
- Payment records and inventory
- Product catalog and suppliers
- eTIMS tax integration support

### Database Platforms Supported

- **PostgreSQL**: Full support
- **Databricks**: Compatible with Delta Lake

---

## Database Schema Documentation

See `docs/SCHEMA.md` for table relationships. Core phppos tables: people, employees, items, locations, location_items, sales.

---

## SQL Queries

See `app/QUERIES/queries.md` for all 30 production queries.

---

## Usage Instructions

Load `data/schema.sql` then data load scripts. Schema is PostgreSQL-native with ACID constraints.
