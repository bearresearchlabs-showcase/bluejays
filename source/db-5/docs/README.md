# DB-5 Documentation – Lucasa POS Retail

This directory contains documentation for the **db-5** POS (Point-of-Sale) database: Lucasa, an anonymized retail dataset from a family business in Kenya.

---

## Contents

- **SCHEMA.md** — Logical schema overview, table relationships, and data flow
- **DATA_DICTIONARY.md** — Column-level reference for all phppos tables
- **DB5_VALIDATION_REPORT.md** — Validation status and metrics
- **DB5_COMPREHENSIVE_DOCUMENTATION.md** — Extended documentation (if present)
- **DB5_FINAL_SUMMARY.md** — Final summary (if present)

---

## Schema Overview

The db-5 schema is a minimal phppos subset with 7 tables:

- `phppos_people` — Base persons (customers, employees, suppliers)
- `phppos_employees` — Employee accounts
- `phppos_employees_locations` — Employee–location assignments
- `phppos_items` — Product catalog
- `phppos_locations` — Store locations
- `phppos_location_items` — Location-specific inventory
- `phppos_sales` — Sales transaction header

---

## Usage

- See **SCHEMA.md** for table relationships and ERD
- See **DATA_DICTIONARY.md** for column definitions and sample queries
- See `../app/QUERIES/queries.md` for production SQL queries
