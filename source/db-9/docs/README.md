# Shipping Intelligence Database - Documentation

**Database:** db-9
**Created:** 2026-02-04

## Overview

This database contains shipping intelligence data for multi-carrier rate comparison, zone analysis, tracking analytics, and cost optimization. The database supports Pirate Ship-style functionality including carrier rate comparison (USPS, UPS, FedEx), dimensional weight calculations, and address validation from USPS Address API.

## Database Schema

See `../data/schema.sql` for the complete database schema.

### Key Tables

- **shipping_carriers** - Carrier information (USPS, UPS, FedEx, etc.)
- **shipping_zones** - Zone information for rate calculations
- **shipping_service_types** - Available service types (Priority Mail, Ground, Express, etc.)
- **shipping_rates** - Historical and current shipping rates
- **packages** - Package information for shipments
- **shipments** - Shipment records with origin and destination
- **tracking_events** - Tracking events for shipments
- **rate_comparison_results** - Rate comparison results across carriers
- **address_validation_results** - Address validation results from USPS Address API
- **shipping_adjustments** - Shipping adjustments and discrepancies
- **shipping_analytics** - Aggregated shipping analytics and metrics
- **international_customs** - Customs information for international shipments
- **api_rate_request_log** - API rate request logs for monitoring
- **bulk_shipping_presets** - Preset configurations for bulk shipping

## Queries

See `../queries/queries.md` for 30 extremely complex SQL queries.

All queries are designed to work across:
- PostgreSQL
 (Delta Lake)


## Data Sources

- **USPS** - Postal rate and address validation APIs
- **UPS** - Carrier rates and services
- **FedEx** - Carrier rates and services

## Usage

1. Load schema: `psql -f data/schema.sql` (PostgreSQL)
2. Load data: `psql -f data/data.sql` (PostgreSQL)
3. Run queries: See `queries/queries.md`

---
**Last Updated:** 2026-02-04
