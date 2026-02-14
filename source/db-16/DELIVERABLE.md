# Database Deliverable: db-16 - Flood Risk Assessment

**Database:** db-16
**Type:** Flood Risk Assessment (M&A Due Diligence)
**Created:** 2026-02-09
**Status:** Complete

---

## Database Overview

### Description

The Flood Risk Assessment Database provides comprehensive physical climate risk assessment capabilities for large real estate firms specializing in Mergers & Acquisitions (M&A). Integrates data from FEMA, NOAA, USGS, and NASA for location-specific flood risk assessments.

### Key Features

- FEMA flood zone mapping and Base Flood Elevations
- NOAA sea level rise projections
- USGS streamflow and flood stage data
- NASA flood model predictions
- Property-level and portfolio-level risk assessment

### Database Platforms Supported

- **PostgreSQL**: Full support with PostGIS
- **Databricks**: Delta Lake with spatial extensions
- **Databricks**: GEOGRAPHY support

---

## Database Schema Documentation

See docs/ for schema details. Core tables: fema_flood_zones, real_estate_properties, noaa_sea_level_rise, usgs_streamflow_gauges, usgs_streamflow_observations, nasa_flood_models, flood_risk_assessments, property_flood_zone_intersections, historical_flood_events, model_performance_metrics, portfolio_risk_summaries, data_quality_metrics.

---

## SQL Queries

See queries/queries.md for all 30 production queries.

---

## Usage Instructions

Load schema.sql and data.sql. See README.md for risk assessment workflow.
