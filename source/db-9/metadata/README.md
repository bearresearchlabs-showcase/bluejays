# Metadata Directory - db-9

This directory stores pipeline execution metadata, data quality reports, and schema evolution tracking for the Shipping Intelligence Database.

## Contents

- `pipeline_metadata.json` - Pipeline execution logs
- `data_quality_reports.json` - Data quality metrics
- `schema_metadata.json` - Schema evolution tracking

## Usage

See `.cursor/rules/research-metadata-directories.mdc` for detailed usage guidelines.

## Pipeline Metadata

Pipeline execution metadata tracks:
- ETL/ELT pipeline runs
- API data extraction operations
- Data load operations
- Error logs and debugging information

## Data Quality Reports

Data quality reports include:
- Address validation quality metrics
- Rate data accuracy metrics
- Tracking data completeness
- API response quality metrics

## Schema Metadata

Schema evolution tracking includes:
- Schema version history
- Table addition/removal tracking
- Column modifications
- Index and constraint changes

---
**Last Updated:** 2026-02-04
