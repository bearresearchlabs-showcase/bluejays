# Flood Risk Assessment Database for M&A Due Diligence - db-16

**Deliverable:** db-16
**Status:** ✅ Complete
**Created:** 2026-02-06

## Overview

The Flood Risk Assessment Database provides comprehensive physical climate risk assessment capabilities specifically designed for **large real estate firms specializing in Mergers & Acquisitions (M&A)**. This database enables M&A teams to conduct thorough flood risk due diligence on acquisition targets, assess portfolio-level risks, and make data-driven acquisition decisions.

The database integrates data from FEMA (flood zones), NOAA (sea level rise), USGS (streamflow), and NASA (flood models) to deliver location-specific flood risk assessments for properties under consideration for acquisition. All queries are formulated to support M&A workflows including pre-acquisition risk assessment, acquisition target evaluation, portfolio risk analysis, and post-acquisition risk management.

## Structure

```
db-16/
├── queries/ # 30+ extremely complex SQL queries
├── results/ # Test results and validation reports
├── docs/ # Database documentation
├── data/ # Schema and data files
├── scripts/ # Utility scripts
├── research/ # Research notebooks and data source documentation
└── metadata/ # Pipeline execution metadata
```

## Contents

- **Queries:** 30 extremely complex SQL queries in `queries/queries.md`
- **Results:** JSON test results in `results/`
- **Documentation:** Database documentation in `docs/`
- **Data:** Schema and data files in `data/`

## Database Schema

### Core Tables

- **fema_flood_zones**: FEMA National Flood Hazard Layer flood zone designations and Base Flood Elevations
- **real_estate_properties**: Property locations and characteristics for risk assessment
- **noaa_sea_level_rise**: NOAA sea level rise projections and high tide flooding data
- **usgs_streamflow_gauges**: USGS streamflow gauge locations and flood stage information
- **usgs_streamflow_observations**: Real-time and historical streamflow measurements
- **nasa_flood_models**: NASA flood model predictions and inundation extents
- **flood_risk_assessments**: Comprehensive flood risk assessments for properties
- **property_flood_zone_intersections**: Spatial relationships between properties and flood zones
- **historical_flood_events**: Historical flood event records for risk analysis
- **model_performance_metrics**: Flood model accuracy and performance metrics
- **portfolio_risk_summaries**: Aggregated risk metrics by portfolio
- **data_quality_metrics**: Data quality tracking for flood risk data sources

## Data Sources

### FEMA (Federal Emergency Management Agency)
- **National Flood Hazard Layer (NFHL)**: Authoritative flood zone maps covering 90%+ of U.S. population
- **Flood Map API**: Programmatic access to flood zone data and Base Flood Elevations
- **OpenFEMA**: Historical flood insurance claims and disaster data

### NOAA (National Oceanic and Atmospheric Administration)
- **CO-OPS Derived Product API**: High tide flooding data and sea level rise projections
- **Sea Level Rise Viewer**: Coastal flooding and sea level rise impact data (up to 10 feet projections)

### USGS (U.S. Geological Survey)
- **Water Data for the Nation**: Real-time and historical streamflow data from 7,000+ gauges
- **National Water Dashboard**: Interactive flood status and streamflow conditions

### NASA (National Aeronautics and Space Administration)
- **Global Flood Monitoring System (GFMS)**: Global flood predictions and warnings
- **LANCE Near Real-Time Flood Products**: Daily ~250m resolution flood detection (VIIRS/MODIS)
- **Global Flood Hazard Frequency**: Historical flood hazard frequency data (1985-2003)

## Usage

### Risk Assessment Workflow

1. **Property Location**: Input property coordinates or address
2. **Spatial Analysis**: Identify intersecting flood zones, nearby gauges, and model outputs
3. **Risk Calculation**: Compute multi-factor risk scores (FEMA zones, sea level rise, streamflow, NASA models)
4. **Portfolio Aggregation**: Generate portfolio-level risk summaries
5. **Decision Support**: Provide go/no-go investment recommendations

### M&A-Focused Query Examples

- **Pre-Acquisition Risk Assessment**: Comprehensive flood risk score for individual properties under consideration for acquisition
- **Acquisition Target Portfolio Analysis**: Aggregated risk metrics for entire acquisition target portfolios to assess deal risk
- **Comparative Risk Analysis**: Side-by-side risk comparison between multiple acquisition targets
- **Financial Impact for M&A Pricing**: Estimated flood damage costs and insurance premiums to inform acquisition pricing
- **Geographic Risk Clustering**: Identify high-risk geographic concentrations in acquisition targets
- **Historical Flood Due Diligence**: Historical flood frequency and severity analysis for acquisition target locations
- **Sea Level Rise Impact Projections**: Long-term risk projections for coastal acquisition targets
- **Risk-Based Acquisition Prioritization**: Rank acquisition targets by flood risk to prioritize deal pipeline

## Compatibility

All queries are designed to work across:
- PostgreSQL (with PostGIS for spatial operations)
 (Delta Lake with spatial extensions)
 (with GEOGRAPHY data type support)

## Business Value for M&A Firms

This database enables large real estate M&A firms to:

- **Pre-Acquisition Due Diligence**: Comprehensive flood risk assessment for properties under consideration for acquisition, enabling informed go/no-go decisions
- **Acquisition Target Risk Scoring**: Multi-factor risk scoring for acquisition targets to prioritize deals and negotiate pricing based on flood risk exposure
- **Portfolio-Level Risk Analysis**: Aggregated risk metrics for entire acquisition target portfolios to assess overall deal risk
- **Financial Impact Assessment**: Estimated flood damage costs, insurance premiums, and annual loss projections to inform acquisition pricing and deal structuring
- **Comparative Risk Analysis**: Side-by-side risk comparison between multiple acquisition targets to identify lowest-risk opportunities
- **Geographic Risk Clustering**: Identify high-risk geographic concentrations in acquisition targets to assess portfolio diversification needs
- **Post-Acquisition Risk Management**: Ongoing risk monitoring and assessment for acquired properties to optimize portfolio performance
- **Regulatory Compliance**: FEMA flood zone compliance verification for acquisition targets to ensure regulatory requirements are met

## Target Data Size

Approximately **2 GB** of flood risk data including:
- FEMA flood zone boundaries (national coverage)
- NOAA sea level rise projections (coastal areas)
- USGS streamflow data (7,000+ gauges, historical records)
- NASA flood model outputs (global coverage)
- Real estate property data (portfolio-specific)

---
**Last Updated:** 2026-02-06
