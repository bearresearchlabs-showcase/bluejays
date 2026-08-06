# Database Deliverable: db-4 - SharedAI Models

**Database:** db-4
**Type:** SharedAI Models (Seydam AI)
**Created:** 2026-02-09
**Status:** Complete

---

## Database Overview

### Description

Seydam AI database with SharedAI application schema. Includes core application data, user profiles, payment records, generated reports, and AI model metadata. Exported from Supabase PostgreSQL.

### Key Features

- User profiles and reports
- Payment and token usage tracking
- AI model management
- JSON report content

### Database Platforms Supported

- **PostgreSQL**: Full support
- **Databricks**: Compatible with Delta Lake
- **Databricks**: Full support

---

## Database Schema Documentation

See `docs/SCHEMA.md` for table relationships. Includes `models` table and application schema.

---

## SQL Queries

See `queries/queries.md` for all 30 production queries.

---

## Usage Instructions

Load schema.sql and data.sql. See docs/README.md for restoration.
