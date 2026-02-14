# Shipping Intelligence Database - db-9

**Deliverable:** db-9
**Status:** 🚧 In Progress
**Created:** 2026-02-04

## Overview

Shipping Intelligence Database designed to mirror the functionality of Pirate Ship (https://www.pirateship.com/), providing comprehensive shipping rate comparison, zone analysis, tracking analytics, and cost optimization capabilities. This database integrates with USPS, UPS, and other carrier APIs to provide shipping intelligence and analytics.

## Structure

```
db-9/
├── queries/
│   ├── queries.md          # 30+ extremely complex SQL queries
│   └── queries.json        # Query metadata (REQUIRED - extracted from queries.md)
├── results/
│   └── *.json              # Test results and validation reports (JSON only)
├── docs/
│   ├── README.md           # Database documentation
│   ├── SCHEMA.md           # Schema documentation
│   └── DATA_DICTIONARY.md  # Data dictionary
├── data/
│   ├── schema.sql          # Database schema SQL file
│   └── data.sql            # Sample data SQL file
├── scripts/
│   ├── extract_queries_to_json.py # Phase 0: Query extraction
│   ├── verify_fixes.py     # Phase 1: Fix verification
│   ├── comprehensive_validator.py # Phase 2 & 4: Syntax validation and evaluation
│   ├── execution_tester.py # Phase 3: Execution testing
│   ├── generate_final_report.py # Phase 5: Final report generation
│   └── requirements.txt    # Python dependencies
├── research/
│   ├── etl_elt_pipeline.ipynb # ETL/ELT pipeline notebook
│   ├── data_resources.json # Data source documentation
│   └── README.md           # Research directory documentation
└── metadata/
    └── README.md           # Metadata directory documentation
```

## Contents

- **Queries:** 30 extremely complex SQL queries in `queries/queries.md`
- **Results:** JSON test results in `results/`
- **Documentation:** Database documentation in `docs/`
- **Data:** Schema and data files in `data/`

## Database Schema

The shipping intelligence database includes the following key tables:

### Core Tables
- **shipping_carriers**: Carrier information (USPS, UPS, FedEx, etc.)
- **shipping_zones**: Zone information for rate calculations
- **shipping_service_types**: Available service types (Priority Mail, Ground, Express, etc.)
- **shipping_rates**: Historical and current shipping rates
- **packages**: Package information for shipments
- **shipments**: Shipment records with origin and destination
- **tracking_events**: Tracking events for shipments

### Analytics Tables
- **rate_comparison_results**: Rate comparison results across carriers
- **address_validation_results**: Address validation results from USPS Address API
- **shipping_adjustments**: Shipping adjustments and discrepancies
- **shipping_analytics**: Aggregated shipping analytics and metrics
- **international_customs**: Customs information for international shipments
- **api_rate_request_log**: API rate request logs for monitoring

### Configuration Tables
- **bulk_shipping_presets**: Preset configurations for bulk shipping

## Data Sources

The database integrates with the following data sources:

1. **USPS Developer Portal** (https://developers.usps.com)
   - Domestic Prices API
   - Domestic Labels API
   - Addresses API
   - Adjustments API
   - Tracking API

2. **UPS Developer Portal** (https://developer.ups.com)
   - Shipping API
   - Rating API
   - Tracking API

3. **U.S. Census Bureau International Trade Data**
   - USA Trade Online
   - SPI Databank (customs data, tariff information)

4. **Data.gov**
   - ZIP code boundary datasets
   - Postal service data
   - Transportation and logistics datasets

See `research/data_resources.json` for detailed data source documentation.

## Key Features

- **Multi-Carrier Rate Comparison**: Compare rates across USPS, UPS, and other carriers
- **Zone Analysis**: Shipping zone calculations and geographic analysis
- **Tracking Analytics**: Comprehensive tracking event analysis and delivery prediction
- **Address Validation**: USPS address validation and standardization
- **Cost Optimization**: Dimensional weight optimization, rate optimization, and cost savings analysis
- **International Shipping**: Customs duty and tax analysis, international route optimization
- **Performance Analytics**: Carrier performance comparison, delivery time analysis, API performance monitoring

## Usage

1. **Setup Database**: Run `data/schema.sql` to create the database schema
2. **Load Sample Data**: Run `data/data.sql` to load sample data (if available)
3. **Run Queries**: Execute queries from `queries/queries.md` for shipping intelligence analytics
4. **ETL Pipeline**: Use `research/etl_elt_pipeline.ipynb` for data integration from carrier APIs

## Compatibility

All queries are designed to work across:
- PostgreSQL (with PostGIS if spatial)
 (Delta Lake)


## Related Documentation

- **Schema Documentation**: See `docs/SCHEMA.md`
- **Data Dictionary**: See `docs/DATA_DICTIONARY.md`
- **Research**: See `research/README.md`
- **Metadata**: See `metadata/README.md`

---
**Last Updated:** 2026-02-04
