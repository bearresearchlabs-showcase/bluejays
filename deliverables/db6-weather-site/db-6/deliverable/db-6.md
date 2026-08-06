# ID: db-6 - Name: Weather Data Pipeline System

This document provides comprehensive documentation for database db-6, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**, representing real-world enterprise implementations.

---

## Table of Contents

### Database Documentation

1. [Database Overview](#database-overview)
   - Description and key features
   - Business context and use cases
   - Platform compatibility
   - Data sources

2. [Database Schema Documentation](#database-schema-documentation)
   - Complete schema overview
   - All tables with detailed column definitions
   - Indexes and constraints
   - Entity-Relationship diagrams
   - Table relationships

3. [Data Dictionary](#data-dictionary)
   - Comprehensive column-level documentation
   - Data types and constraints
   - Column descriptions and business context

### SQL Queries (30 Production Queries)

1. [Query 1: Production-Grade Spatial Weather Forecast Analysis with Multi-Level CTE Nesting and Geospatial Aggregations](#query-1)
    - **Use Case:** Custom Weather Impact Modeling - Regional Forecast Accuracy Assessment for Insurance Risk Modeling
    - *What it does:* Enterprise-level spatial weather forecast analysis with multi-level CTE nesting, spatial aggregations within boundaries, forecast accuracy metrics, te...
    - *Business Value:* Forecast accuracy report by geographic boundary (CWA, Fire Zones) showing forecast reliability metri...
    - *Purpose:* Quantifies forecast reliability for specific geographic regions, enabling data-driven risk assessmen...

2. [Query 2: Recursive Spatial Boundary Hierarchy Analysis with Multi-Hop Geospatial Traversal](#query-2)
    - **Use Case:** Custom Map Development - Multi-Level Geographic Hierarchy Visualization for Agriculture Insurance
    - *What it does:* Enterprise-level recursive spatial analysis using recursive CTE for multi-level boundary relationships, spatial hierarchy traversal, boundary intersec...
    - *Business Value:* Spatial hierarchy relationships showing nested boundaries (states → counties → fire zones) with fore...
    - *Purpose:* Provides multi-scale geographic analysis enabling clients to understand relationships between admini...

3. [Query 3: Multi-Parameter Weather Correlation Analysis with Cross-Parameter Temporal Patterns](#query-3)
    - **Use Case:** Physical Climate Risk Assessment - Multi-Parameter Risk Correlation for Renewable Energy Planning
    - *What it does:* Enterprise-level multi-parameter weather correlation analysis with cross-parameter temporal pattern detection, correlation matrices, lag analysis, and...
    - *Business Value:* Correlation analysis between temperature, precipitation, and wind patterns with temporal lag indicat...
    - *Purpose:* Identifies compound weather risks (e.g., high temp + low precip = drought risk) and enables predicti...

4. [Query 4: Spatial Join Optimization Analysis with Boundary-Forecast Matching Efficiency Metrics](#query-4)
    - **Use Case:** Custom Weather Impact Modeling - Boundary-Forecast Matching Efficiency for Logistics Optimization
    - *What it does:* Enterprise-level spatial join optimization analysis evaluating boundary-forecast matching efficiency, spatial index utilization, join performance metr...
    - *Business Value:* Optimizes forecast-to-boundary matching for faster client deliverables and improved operational effi...
    - *Purpose:* Analysis of how efficiently forecasts match to client-defined boundaries with optimization recommend...

5. [Query 5: Weather Station Network Coverage Analysis with Spatial Gap Detection and Coverage Optimization](#query-5)
    - **Use Case:** Supply Chain and Fleet Management - Station Coverage Gap Analysis for Route Planning
    - *What it does:* Enterprise-level weather station network analysis identifying coverage gaps, station density metrics, spatial interpolation opportunities, and network...
    - *Business Value:* Map showing gaps in weather station coverage along routes with coverage density metrics. Fleet manag...
    - *Purpose:* Identifies areas where additional weather monitoring may be needed to ensure adequate coverage for l...

6. [Query 6: Forecast Accuracy Trend Analysis with Temporal Error Pattern Detection](#query-6)
    - **Use Case:** Forensic Meteorology - Historical Forecast Accuracy Assessment for Legal Cases
    - *What it does:* Enterprise-level forecast accuracy trend analysis identifying temporal error patterns, accuracy degradation over time, seasonal variations, and foreca...
    - *Business Value:* Provides quantitative evidence of forecast reliability for legal proceedings and insurance claim val...
    - *Purpose:* Trend analysis showing forecast accuracy over time with error pattern detection. Provides evidence o...

7. [Query 7: Boundary Forecast Aggregation Analysis with Multi-Level Spatial Summarization](#query-7)
    - **Use Case:** Custom Weather Impact Modeling - Aggregated Forecasts by Boundary for Retail Operations
    - *What it does:* Enterprise-level boundary forecast aggregation analysis with multi-level spatial summarization, hierarchical aggregations, and comprehensive statistic...
    - *Business Value:* Summary forecasts aggregated by client-defined boundaries (counties, zones). Retail chains can get a...
    - *Purpose:* Provides simplified forecasts for specific geographic areas enabling location-based business decisio...

8. [Query 8: Observation Forecast Validation Analysis with Accuracy Scoring](#query-8)
    - **Use Case:** Forensic Meteorology - Forecast vs. Observation Validation for Legal Evidence
    - *What it does:* Enterprise-level observation-forecast validation analysis comparing actual observations with forecasts, calculating accuracy scores, identifying syste...
    - *Business Value:* Provides evidence of forecast accuracy for legal proceedings and insurance claim validation.
    - *Purpose:* Validation report comparing forecasts to actual observations with accuracy scoring. Legal cases requ...

9. [Query 9: Multi-Boundary Spatial Intersection Analysis with Overlap Detection](#query-9)
    - **Use Case:** Custom Map Development - Boundary Overlap Detection for Real Estate Development
    - *What it does:* Enterprise-level multi-boundary spatial intersection analysis identifying overlapping boundaries, intersection areas, coverage gaps, and spatial relat...
    - *Business Value:* Analysis of overlapping boundaries (e.g., fire zones overlapping counties) with intersection metrics...
    - *Purpose:* Helps clients understand complex geographic relationships for property and risk assessment.

10. [Query 10: Parameter Forecast Distribution Analysis with Statistical Profiling](#query-10)
    - **Use Case:** Physical Climate Risk Assessment - Statistical Weather Profiling for Insurance Underwriting
    - *What it does:* Enterprise-level parameter forecast distribution analysis with statistical profiling, distribution shape analysis, outlier detection, and distribution...
    - *Business Value:* Identifies normal vs. extreme weather patterns for risk assessment and insurance pricing.
    - *Purpose:* Statistical distribution analysis of forecast parameters with percentile rankings. Insurance compani...

11. [Query 11: Geospatial Forecast Interpolation Analysis with Spatial Gradient Detection](#query-11)
    - **Use Case:** Custom Weather Impact Modeling - Spatial Gradient Detection for Precision Agriculture
    - *What it does:* Enterprise-level geospatial forecast interpolation analysis identifying spatial gradients, interpolation opportunities, spatial patterns, and interpol...
    - *Business Value:* Analysis of how weather parameters change across space with gradient calculations. Agriculture compa...
    - *Purpose:* Identifies spatial gradients for precise location-specific forecasts enabling precision agriculture.

12. [Query 12: Weather Pattern Clustering Analysis with Spatial-Temporal Pattern Detection](#query-12)
    - **Use Case:** Physical Climate Risk Assessment - Pattern-Based Risk Identification for Renewable Energy
    - *What it does:* Enterprise-level weather pattern clustering analysis identifying spatial-temporal patterns, clustering similar weather conditions, and detecting patte...
    - *Business Value:* Helps predict future weather patterns based on historical clusters for energy planning.
    - *Purpose:* Identification of recurring weather patterns with clustering metrics. Energy companies can identify...

13. [Query 13: Forecast Model Performance Comparison with Multi-Model Analysis](#query-13)
    - **Use Case:** Forensic Meteorology - Multi-Model Analysis for Comprehensive Legal Evidence
    - *What it does:* This SQL query performs comprehensive forecast model performance comparison for a weather consulting firm. It identifies forecast models (NDFD, GFS, N...
    - *Business Value:* Comparison of different forecast models' performance with accuracy metrics. Court cases require comp...
    - *Purpose:* Provides comprehensive analysis using multiple models for legal evidence and risk assessment.

14. [Query 14: Boundary Forecast Anomaly Detection with Statistical Outlier Identification](#query-14)
    - **Use Case:** Physical Climate Risk Assessment - Extreme Event Detection for Emergency Management
    - *What it does:* Enterprise-level boundary forecast anomaly detection identifying statistical outliers, anomalies in boundary aggregations, and unusual forecast patter...
    - *Business Value:* Early warning system for extreme weather events enabling proactive risk management.
    - *Purpose:* Identification of anomalous weather patterns within boundaries with outlier metrics. Emergency manag...

15. [Query 15: Insurance Risk Factor Calculation from 7-14 Day Forecasts](#query-15)
    - **Use Case:** Insurance Underwriting - Multi-Day Forecast Risk Assessment for Rate Determination
    - *What it does:* Calculates comprehensive risk factors for insurance policy areas based on 7-14 day forecasts from December 3-17, 2025. Analyzes multiple weather param...
    - *Business Value:* Risk factor analysis report showing forecast-based risk scores for each policy area and forecast day...
    - *Purpose:* Enables insurance companies to adjust rates dynamically based on forecasted weather risks, improving...

16. [Query 16: Insurance Rate Table Generation from Forecast Risk Factors](#query-16)
    - **Use Case:** Insurance Underwriting - Dynamic Rate Table Calculation Based on 7-14 Day Forecasts
    - *What it does:* Generates insurance rate tables for December 3-17, 2025 period using risk factors calculated from 7-14 day forecasts. Calculates base rates, risk-adju...
    - *Business Value:* Enables dynamic pricing based on forecasted weather risks, allowing insurance companies to adjust ra...
    - *Purpose:* Complete rate table showing rates for each policy area, forecast day (7-14 days), and coverage type...

17. [Query 17: Rate Table Comparison Across 7-14 Day Forecasts](#query-17)
    - **Use Case:** Insurance Underwriting - Multi-Day Forecast Rate Comparison for Optimal Rate Selection
    - *What it does:* Compares insurance rates across all forecast days (7-14 days ahead) for December 3-17, 2025 period. Calculates rate statistics, volatility, trends, an...
    - *Business Value:* Rate comparison report showing rates by forecast day with volatility metrics and recommended rates.
    - *Purpose:* Enables insurance companies to select optimal forecast day balancing accuracy (shorter forecast) wit...

18. [Query 18: Historical Claims Validation Against Forecast Risk Factors](#query-18)
    - **Use Case:** Insurance Underwriting - Forecast Accuracy Validation Using Historical Claims Data
    - *What it does:* Validates forecast-based risk factors against historical claims data for December 3-17, 2025 period. Compares forecast risk scores with actual claims...
    - *Business Value:* Enables insurance companies to validate and improve forecast-based rate models using historical data...
    - *Purpose:* Validation report showing forecast risk vs actual claims with accuracy metrics and improvement recom...

19. [Query 19: Rate Volatility and Stability Analysis](#query-19)
    - **Use Case:** Insurance Underwriting - Rate Stability Assessment for Pricing Consistency
    - *What it does:* Analyzes rate volatility and stability across 7-14 day forecasts for December 3-17, 2025. Identifies areas with high rate volatility and recommends st...
    - *Business Value:* Rate volatility analysis report with stability metrics and recommendations for consistent pricing.
    - *Purpose:* Helps insurance companies identify pricing inconsistencies and implement stable pricing strategies,...

20. [Query 20: Policy Area Risk Ranking and Comparison](#query-20)
    - **Use Case:** Insurance Underwriting - Geographic Risk Ranking for Portfolio Management
    - *What it does:* Ranks policy areas by forecast-based risk scores for December 3-17, 2025 period. Provides comparative risk analysis across geographic areas to support...
    - *Business Value:* Enables insurance companies to identify high-risk areas, allocate underwriting resources effectively...
    - *Purpose:* Risk ranking report showing policy areas ordered by risk level with comparative metrics.  **Business...

21. [Query 21: Forecast-to-Rate Impact Analysis](#query-21)
    - **Use Case:** Insurance Underwriting - Forecast Parameter Impact on Rate Determination
    - *What it does:* Analyzes how individual forecast parameters (temperature, precipitation, wind) impact insurance rates for December 3-17, 2025. Quantifies the contribu...
    - *Business Value:* Parameter impact analysis showing which forecast parameters drive rate changes and their relative co...
    - *Purpose:* Enables insurance companies to understand which weather parameters most significantly affect rates,...

22. [Query 22: Multi-Day Forecast Ensemble Rate Analysis](#query-22)
    - **Use Case:** Insurance Underwriting - Ensemble Forecast Rate Analysis for Robust Pricing
    - *What it does:* Analyzes rates across multiple forecast days (7-14 days) as an ensemble to determine robust, consensus rates. Uses ensemble statistics to reduce forec...
    - *Business Value:* Provides more robust rate determination by combining multiple forecast days, reducing impact of indi...
    - *Purpose:* Ensemble rate analysis showing consensus rates across forecast days with confidence intervals.  **Bu...

23. [Query 23: Forecast Day Selection Optimization](#query-23)
    - **Use Case:** Insurance Underwriting - Optimal Forecast Day Selection for Rate Determination
    - *What it does:* Determines optimal forecast day (7-14 days) for rate determination based on accuracy, confidence, and business requirements. Balances forecast accurac...
    - *Business Value:* Forecast day optimization report recommending optimal forecast day for each policy area with justifi...
    - *Purpose:* Enables insurance companies to select optimal forecast day balancing accuracy and planning needs, im...

24. [Query 24: Comprehensive Insurance Rate Modeling Summary](#query-24)
    - **Use Case:** Insurance Underwriting - Comprehensive Rate Modeling Summary Dashboard
    - *What it does:* Provides comprehensive summary of insurance rate modeling for December 3-17, 2025 period. Aggregates risk factors, rates, comparisons, validations, an...
    - *Business Value:* Provides insurance companies with single-source-of-truth dashboard for rate modeling decisions, impr...
    - *Purpose:* Comprehensive rate modeling summary dashboard with all key metrics and recommendations.  **Business...

25. [Query 25: US-Wide NEXRAD Reflectivity Composite Generation](#query-25)
    - **Use Case:** Real-Time Weather Monitoring - Nationwide Radar Composite for Severe Weather Detection
    - *What it does:* Generates US-wide composite reflectivity from all NEXRAD radar sites. Combines Level II radar data from multiple sites to create seamless nationwide c...
    - *Business Value:* US-wide reflectivity composite showing precipitation intensity across entire United States with seam...
    - *Purpose:* Provides comprehensive real-time precipitation monitoring across the entire US, enabling severe weat...

26. [Query 26: NEXRAD Storm Cell Tracking and Movement Analysis](#query-26)
    - **Use Case:** Severe Weather Forecasting - Multi-Site Storm Cell Tracking for Tornado and Severe Thunderstorm Prediction
    - *What it does:* Tracks storm cells across multiple NEXRAD radar sites and analyzes their movement, intensity changes, and development patterns. Handles storm cell mer...
    - *Business Value:* Enables severe weather prediction and warning systems by tracking storm development and movement pat...
    - *Purpose:* Storm cell tracking report showing storm movement, intensity trends, and predicted paths across mult...

27. [Query 27: US-Wide Satellite Imagery Cloud Composite Generation](#query-27)
    - **Use Case:** Cloud Monitoring - Nationwide Cloud Coverage Analysis from GOES Satellite Imagery
    - *What it does:* Generates US-wide cloud composite from decompressed GOES satellite imagery. Combines multiple satellite bands and products to create seamless cloud co...
    - *Business Value:* US-wide cloud composite showing cloud coverage, cloud top heights, and cloud properties across entir...
    - *Purpose:* Provides comprehensive cloud monitoring for solar energy forecasting, aviation weather, and climate...

28. [Query 28: NEXRAD-Satellite Data Fusion for Precipitation Estimation](#query-28)
    - **Use Case:** Precipitation Monitoring - Multi-Source Precipitation Estimation Combining Radar and Satellite Data
    - *What it does:* Fuses NEXRAD radar reflectivity and satellite precipitation estimates to create improved US-wide precipitation maps. Combines strengths of both data s...
    - *Business Value:* Provides more accurate and comprehensive precipitation estimates by combining radar (high resolution...
    - *Purpose:* Fused precipitation product combining NEXRAD and satellite data with improved accuracy and coverage....

29. [Query 29: Satellite Fire Detection and Monitoring Across US](#query-29)
    - **Use Case:** Wildfire Monitoring - Nationwide Fire Detection from GOES Satellite Imagery
    - *What it does:* Detects and monitors fires across the entire United States using decompressed GOES satellite imagery. Analyzes fire radiative power, temperature, and...
    - *Business Value:* US-wide fire detection report showing fire locations, intensity, and development trends from satelli...
    - *Purpose:* Enables early wildfire detection and monitoring at national scale, supporting fire management and em...

30. [Query 30: US-Wide Composite Product Generation (NEXRAD + Satellite)](#query-30)
    - **Use Case:** Comprehensive Weather Monitoring - Multi-Source Composite Products for National Weather Analysis
    - *What it does:* Generates US-wide composite products combining NEXRAD radar and satellite imagery data. Creates seamless nationwide weather products with improved cov...
    - *Purpose:* US-wide composite products combining radar and satellite data for comprehensive weather monitoring....

### Additional Information

- [Usage Instructions](#usage-instructions)
- [Platform Compatibility](#platform-compatibility)
- [Business Context](#business-context)

---

## Business Context

**Enterprise-Grade Database System**

This database and all associated queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**. These are not academic examples or toy databases—they represent real-world implementations that power critical business operations, serve paying customers, and generate significant revenue.

**What This Means:**

- **Production-Ready**: All queries have been tested and optimized in production environments
- **Business-Critical**: These queries solve real business problems for revenue-generating companies
- **Scalable**: Designed to handle enterprise-scale data volumes and query loads
- **Proven**: Each query addresses a specific business need that has been validated through actual customer use

**Business Value:**

Every query in this database was created to solve a specific business problem for a company generating $1M+ ARR. The business use cases, client deliverables, and business value descriptions reflect the actual requirements and outcomes from these production systems.

---

## Database Overview

This database contains weather data from NOAA sources including GRIB2 gridded forecasts, shapefile boundaries (CWA, Fire Zones, Marine Zones), real-time observations, transformation logs, spatial joins, CRS transformations, data quality metrics load status. The system is designed for weather forecasting, spatial analysis, and climate risk assessment applications.

- **GRIB2 Forecast Data**: Gridded numerical weather forecasts from NDFD (National Digital Forecast Database)
- **Geographic Boundaries**: Shapefile data for CWAs (County Warning Areas), Fire Zones, Marine Zones, and River Basins
- **Real-Time Observations**: Point observations from NWS API
- **Data Quality Tracking**: Comprehensive metrics for data quality monitoring
- **Transformation Logging**: Complete audit trail for data transformations
- **Multi-Source Integration**: Integration of multiple NOAA data sources

- **PostgreSQL**: Full support with PostGIS extension for spatial operations

- **GRIB2 Files**: National Digital Forecast Database (NDFD) from `tgftp.nws.noaa.gov`
- **Shapefiles**: NWS GIS Portal shapefiles from `weather.gov/gis`
- **Observations**: NWS API (`api.weather.gov`)

---

---

### Data Dictionary

This section provides a comprehensive data dictionary for all tables in the database, including column names, data types, constraints, and descriptions. Tables are organized by functional category for easier navigation.

The database consists of **11 tables** organized into logical groups:

1. **Forecast Data**: `grib2_forecasts`
2. **Geographic Boundaries**: `shapefile_boundaries`
3. **Observations**: `weather_observations`, `weather_stations`
4. **Transformation Logs**: `grib2_transformation_log`, `shapefile_integration_log`
5. **Spatial Operations**: `spatial_join_results`, `crs_transformation_parameters`
6. **Data Quality**: `data_quality_metrics`
7. **Load Tracking**: `load_status`
8. **Aggregations**: `weather_forecast_aggregations`

```
grib2_forecasts (forecast_id)
    ├── spatial_join_results (forecast_id)
    └── weather_forecast_aggregations (via boundary_id)

shapefile_boundaries (boundary_id)
    ├── spatial_join_results (boundary_id)
    ├── weather_forecast_aggregations (boundary_id)
    └── weather_stations (cwa_code)

weather_observations (observation_id)
    └── weather_stations (station_id)

weather_stations (station_id)
    └── weather_observations (station_id)
```

```mermaid
erDiagram
    grib2_forecasts {
        varchar forecast_id PK "Primary key - unique forecast identifier"
        varchar parameter_name "Forecast parameter (Temperature, Precipitation, etc.)"
        timestamp forecast_time "Forecast valid time"
        geography grid_cell_geom SPATIAL "Point geometry for grid cell center"
        numeric parameter_value "Forecast parameter value"
        varchar source_file "Source GRIB2 file name"
        varchar transformation_status "Transformation status"
    }

    shapefile_boundaries {
        varchar boundary_id PK "Primary key - unique boundary identifier"
        varchar feature_type "Feature type (CWA, FireZone, MarineZone, etc.)"
        varchar feature_name "Human-readable feature name"
        varchar feature_identifier "Official feature identifier code"
        geography boundary_geom SPATIAL "Polygon geometry for boundary"
        varchar state_code "US state code (2-letter)"
        varchar office_code "NWS office code (CWA identifier)"
        varchar source_shapefile "Source shapefile name"
        varchar transformation_status "Transformation status"
    }

    weather_observations {
        varchar observation_id PK "Primary key - unique observation identifier"
        varchar station_id FK "Weather station"
        varchar station_name "Station name"
        timestamp observation_time "Observation timestamp"
        geography station_geom SPATIAL "Point geometry for station location"
        numeric temperature "Temperature in degrees Fahrenheit"
        numeric precipitation_amount "Precipitation amount in inches"
        numeric wind_speed "Wind speed in knots"
        varchar data_source "Data source identifier"
    }

    weather_stations {
        varchar station_id PK "Primary key - unique station identifier"
        varchar station_name "Station name"
        geography station_geom SPATIAL "Point geometry for station location"
        numeric elevation_meters "Station elevation in meters"
        varchar state_code "US state code"
        varchar county_name "County name"
        varchar cwa_code "County Warning Area code"
        varchar station_type "Station type (ASOS, AWOS, etc.)"
        boolean active_status "Whether station is currently active"
    }

    spatial_join_results {
        varchar join_id PK "Primary key"
        varchar forecast_id FK "Forecast"
        varchar boundary_id FK "Boundary"
        varchar grib_file "GRIB2 file name"
        varchar shapefile_name "Shapefile name"
        varchar join_type "Join type (Point-in-Polygon, Raster-to-Vector, Clip)"
        integer features_matched "Number of features matched"
        integer features_total "Total features"
        numeric match_percentage "Match percentage"
        timestamp join_timestamp "Join timestamp"
    }

    weather_forecast_aggregations {
        varchar aggregation_id PK "Primary key"
        varchar parameter_name "Forecast parameter name"
        timestamp forecast_time "Forecast valid time"
        varchar boundary_id FK "Boundary"
        varchar feature_type "Feature type"
        varchar feature_name "Feature name"
        numeric min_value "Minimum forecast value"
        numeric max_value "Maximum forecast value"
        numeric avg_value "Average forecast value"
        numeric median_value "Median forecast value"
        integer grid_cells_count "Number of grid cells aggregated"
    }

    grib2_transformation_log {
        varchar log_id PK "Primary key"
        varchar file_name "GRIB2 file name"
        varchar parameter_name "Forecast parameter name"
        varchar transformation_status "Status (Success, Failed, Pending)"
        integer processing_duration_seconds "Processing duration"
        integer records_processed "Number of records processed"
        varchar error_message "Error message if failed"
    }

    shapefile_integration_log {
        varchar log_id PK "Primary key"
        varchar shapefile_name "Shapefile name"
        varchar feature_type "Feature type"
        varchar transformation_status "Status"
        integer processing_duration_seconds "Processing duration"
        varchar error_message "Error message"
    }

    crs_transformation_parameters {
        varchar transformation_id PK "Primary key"
        varchar source_crs "Source CRS identifier"
        varchar target_crs "Target CRS identifier"
        varchar transformation_method "Method (GDAL, PROJ, Custom)"
        numeric accuracy_meters "Transformation accuracy"
        integer usage_count "Number of times used"
    }

    data_quality_metrics {
        varchar metric_id PK "Primary key"
        date metric_date "Metric date"
        varchar data_source "Data source (GRIB2, Shapefile, API)"
        integer files_processed "Number of files processed"
        integer files_successful "Number of successful files"
        integer files_failed "Number of failed files"
        numeric success_rate "Success rate percentage"
        integer total_records "Total records processed"
    }

    load_status {
        varchar load_id PK "Primary key"
        varchar source_file "Source file name"
        varchar target_table "Target table"
        timestamp load_start_time "Load start time"
        timestamp load_end_time "Load end time"
        integer records_loaded "Number of records loaded"
        varchar load_status "Status (Success, Failed, Partial)"
    }

    grib2_forecasts ||--o{ spatial_join_results : "forecast"
    shapefile_boundaries ||--o{ spatial_join_results : "boundary"
    shapefile_boundaries ||--o{ weather_forecast_aggregations : "aggregated_by"
    weather_stations ||--o{ weather_observations : "observes"
    grib2_forecasts }o--o{ shapefile_boundaries : "spatially_joins"
```

---

Stores gridded forecast data from NDFD (National Digital Forecast Database). Each row represents a forecast value for a specific parameter at a grid cell location and time.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `forecast_id` | `VARCHAR(255)` | No | — | Primary key - unique forecast identifier |
| `parameter_name` | `VARCHAR(100)` | No | — | Forecast parameter (Temperature, Precipitation, WindSpeed, etc.) |
| `forecast_time` | `TIMESTAMP_NTZ` | No | — | Forecast valid time |
| `grid_cell_latitude` | `NUMERIC(10, 7)` | No | — | Grid cell center latitude (WGS84) |
| `grid_cell_longitude` | `NUMERIC(10, 7)` | No | — | Grid cell center longitude (WGS84) |
| `grid_cell_geom` | `GEOGRAPHY` | Yes | `NULL` | Point geometry for grid cell center |
| `parameter_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Forecast parameter value |
| `source_file` | `VARCHAR(500)` | Yes | `NULL` | Source GRIB2 file name |
| `source_crs` | `VARCHAR(50)` | Yes | `NULL` | Source coordinate reference system |
| `target_crs` | `VARCHAR(50)` | Yes | `NULL` | Target CRS (typically WGS84/EPSG:4326) |
| `grid_resolution_x` | `NUMERIC(10, 6)` | Yes | `NULL` | Grid resolution in X direction (degrees) |
| `grid_resolution_y` | `NUMERIC(10, 6)` | Yes | `NULL` | Grid resolution in Y direction (degrees) |
| `spatial_extent_west` | `NUMERIC(10, 6)` | Yes | `NULL` | Western boundary of spatial extent |
| `spatial_extent_south` | `NUMERIC(10, 6)` | Yes | `NULL` | Southern boundary of spatial extent |
| `spatial_extent_east` | `NUMERIC(10, 6)` | Yes | `NULL` | Eastern boundary of spatial extent |
| `spatial_extent_north` | `NUMERIC(10, 6)` | Yes | `NULL` | Northern boundary of spatial extent |
| `load_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | When forecast was loaded |
| `transformation_status` | `VARCHAR(50)` | Yes | `NULL` | Transformation status (Success, Failed, Pending) |

**Indexes:**
- Primary Key: `forecast_id`
- Index: `(parameter_name, forecast_time)`
- Spatial Index: `grid_cell_geom` (GIST index)
- Index: `transformation_status`
- Index: `forecast_time`

**Spatial Data:**
- Uses GEOGRAPHY type for WGS84 coordinates
- Grid cells are represented as points
- Supports spatial queries (ST_WITHIN, ST_DISTANCE, etc.)

---

Stores geographic boundaries from shapefiles including CWAs, Fire Zones, Marine Zones, River Basins, and Counties.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `boundary_id` | `VARCHAR(255)` | No | — | Primary key - unique boundary identifier |
| `feature_type` | `VARCHAR(50)` | No | — | Feature type (CWA, FireZone, MarineZone, RiverBasin, County) |
| `feature_name` | `VARCHAR(255)` | Yes | `NULL` | Human-readable feature name |
| `feature_identifier` | `VARCHAR(100)` | Yes | `NULL` | Official feature identifier code |
| `boundary_geom` | `GEOGRAPHY` | Yes | `NULL` | Polygon geometry for boundary |
| `source_shapefile` | `VARCHAR(500)` | Yes | `NULL` | Source shapefile name |
| `source_crs` | `VARCHAR(50)` | Yes | `NULL` | Source coordinate reference system |
| `target_crs` | `VARCHAR(50)` | Yes | `NULL` | Target CRS (typically WGS84/EPSG:4326) |
| `feature_count` | `INTEGER` | Yes | `NULL` | Number of features in original shapefile |
| `spatial_extent_west` | `NUMERIC(10, 6)` | Yes | `NULL` | Western boundary of spatial extent |
| `spatial_extent_south` | `NUMERIC(10, 6)` | Yes | `NULL` | Southern boundary of spatial extent |
| `spatial_extent_east` | `NUMERIC(10, 6)` | Yes | `NULL` | Eastern boundary of spatial extent |
| `spatial_extent_north` | `NUMERIC(10, 6)` | Yes | `NULL` | Northern boundary of spatial extent |
| `load_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | When boundary was loaded |
| `transformation_status` | `VARCHAR(50)` | Yes | `NULL` | Transformation status |
| `state_code` | `VARCHAR(2)` | Yes | `NULL` | US state code (2-letter) |
| `office_code` | `VARCHAR(10)` | Yes | `NULL` | NWS office code (CWA identifier) |

**Indexes:**
- Primary Key: `boundary_id`
- Index: `feature_type`
- Spatial Index: `boundary_geom` (GIST index)
- Index: `state_code`
- Index: `office_code`

**Spatial Data:**
- Uses GEOGRAPHY type for polygon boundaries
- Supports spatial operations (ST_WITHIN, ST_INTERSECTS, ST_DISTANCE, etc.)

---

Stores real-time point observations from NWS API weather stations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `observation_id` | `VARCHAR(255)` | No | — | Primary key - unique observation identifier |
| `station_id` | `VARCHAR(50)` | No | — | Foreign key to `weather_stations.station_id` |
| `station_name` | `VARCHAR(255)` | Yes | `NULL` | Station name |
| `observation_time` | `TIMESTAMP_NTZ` | No | — | Observation timestamp |
| `station_latitude` | `NUMERIC(10, 7)` | No | — | Station latitude (WGS84) |
| `station_longitude` | `NUMERIC(10, 7)` | No | — | Station longitude (WGS84) |
| `station_geom` | `GEOGRAPHY` | Yes | `NULL` | Point geometry for station location |
| `temperature` | `NUMERIC(6, 2)` | Yes | `NULL` | Temperature in degrees Fahrenheit |
| `dewpoint` | `NUMERIC(6, 2)` | Yes | `NULL` | Dewpoint in degrees Fahrenheit |
| `humidity` | `NUMERIC(5, 2)` | Yes | `NULL` | Relative humidity percentage |
| `wind_speed` | `NUMERIC(6, 2)` | Yes | `NULL` | Wind speed in knots |
| `wind_direction` | `INTEGER` | Yes | `NULL` | Wind direction in degrees (0-359) |
| `pressure` | `NUMERIC(8, 2)` | Yes | `NULL` | Barometric pressure in inches of mercury |
| `visibility` | `NUMERIC(6, 2)` | Yes | `NULL` | Visibility in miles |
| `sky_cover` | `VARCHAR(50)` | Yes | `NULL` | Sky cover description |
| `precipitation_amount` | `NUMERIC(8, 2)` | Yes | `NULL` | Precipitation amount in inches |
| `data_freshness_minutes` | `INTEGER` | Yes | `NULL` | Minutes since observation |
| `load_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | When observation was loaded |
| `data_source` | `VARCHAR(50)` | No | `'NWS_API'` | Data source identifier |

**Indexes:**
- Primary Key: `observation_id`
- Foreign Key: `station_id` → `weather_stations.station_id`
- Index: `(station_id, observation_time)`
- Spatial Index: `station_geom` (GIST index)
- Index: `observation_time`
- Index: `data_source`

---

Stores metadata about weather observation stations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `station_id` | `VARCHAR(50)` | No | — | Primary key - unique station identifier |
| `station_name` | `VARCHAR(255)` | Yes | `NULL` | Station name |
| `station_latitude` | `NUMERIC(10, 7)` | No | — | Station latitude (WGS84) |
| `station_longitude` | `NUMERIC(10, 7)` | No | — | Station longitude (WGS84) |
| `station_geom` | `GEOGRAPHY` | Yes | `NULL` | Point geometry for station location |
| `elevation_meters` | `NUMERIC(8, 2)` | Yes | `NULL` | Station elevation in meters |
| `state_code` | `VARCHAR(2)` | Yes | `NULL` | US state code |
| `county_name` | `VARCHAR(100)` | Yes | `NULL` | County name |
| `cwa_code` | `VARCHAR(10)` | Yes | `NULL` | County Warning Area code |
| `station_type` | `VARCHAR(50)` | Yes | `NULL` | Station type (ASOS, AWOS, etc.) |
| `active_status` | `BOOLEAN` | No | `TRUE` | Whether station is currently active |
| `first_observation_date` | `DATE` | Yes | `NULL` | First observation date |
| `last_observation_date` | `DATE` | Yes | `NULL` | Last observation date |
| `update_frequency_minutes` | `INTEGER` | Yes | `NULL` | Update frequency in minutes |

**Indexes:**
- Primary Key: `station_id`
- Spatial Index: `station_geom` (GIST index)
- Index: `cwa_code`
- Index: `active_status`
- Index: `state_code`

---

Tracks GRIB2 file processing and transformation operations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `log_id` | `VARCHAR(255)` | No | — | Primary key |
| `file_name` | `VARCHAR(500)` | No | — | GRIB2 file name |
| `source_path` | `VARCHAR(1000)` | Yes | `NULL` | Source file path |
| `parameter_name` | `VARCHAR(100)` | No | — | Forecast parameter name |
| `forecast_time` | `TIMESTAMP_NTZ` | Yes | `NULL` | Forecast valid time |
| `source_crs` | `VARCHAR(50)` | Yes | `NULL` | Source CRS |
| `target_crs` | `VARCHAR(50)` | Yes | `NULL` | Target CRS |
| `gdal_command` | `VARCHAR(2000)` | Yes | `NULL` | GDAL command used for transformation |
| `output_file` | `VARCHAR(1000)` | Yes | `NULL` | Output file path |
| `grid_resolution_x` | `NUMERIC(10, 6)` | Yes | `NULL` | Grid resolution X |
| `grid_resolution_y` | `NUMERIC(10, 6)` | Yes | `NULL` | Grid resolution Y |
| `spatial_extent_west` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent west |
| `spatial_extent_south` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent south |
| `spatial_extent_east` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent east |
| `spatial_extent_north` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent north |
| `transformation_status` | `VARCHAR(50)` | Yes | `NULL` | Status (Success, Failed, Pending) |
| `target_table` | `VARCHAR(255)` | Yes | `NULL` | Target table |
| `load_timestamp` | `TIMESTAMP_NTZ` | Yes | `NULL` | Load timestamp |
| `processing_duration_seconds` | `INTEGER` | Yes | `NULL` | Processing duration |
| `records_processed` | `INTEGER` | Yes | `NULL` | Number of records processed |
| `error_message` | `VARCHAR(2000)` | Yes | `NULL` | Error message if failed |

**Indexes:**
- Primary Key: `log_id`
- Index: `file_name`
- Index: `transformation_status`
- Index: `load_timestamp`

---

Tracks shapefile processing and coordinate transformations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `log_id` | `VARCHAR(255)` | No | — | Primary key |
| `shapefile_name` | `VARCHAR(500)` | No | — | Shapefile name |
| `source_path` | `VARCHAR(1000)` | Yes | `NULL` | Source file path |
| `feature_type` | `VARCHAR(50)` | No | — | Feature type |
| `feature_count` | `INTEGER` | Yes | `NULL` | Number of features |
| `source_crs` | `VARCHAR(50)` | Yes | `NULL` | Source CRS |
| `target_crs` | `VARCHAR(50)` | Yes | `NULL` | Target CRS |
| `ogr2ogr_command` | `VARCHAR(2000)` | Yes | `NULL` | OGR2OGR command used |
| `transformed_path` | `VARCHAR(1000)` | Yes | `NULL` | Transformed file path |
| `spatial_extent_west` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent west |
| `spatial_extent_south` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent south |
| `spatial_extent_east` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent east |
| `spatial_extent_north` | `NUMERIC(10, 6)` | Yes | `NULL` | Spatial extent north |
| `transformation_status` | `VARCHAR(50)` | Yes | `NULL` | Status |
| `target_table` | `VARCHAR(255)` | Yes | `NULL` | Target table |
| `load_timestamp` | `TIMESTAMP_NTZ` | Yes | `NULL` | Load timestamp |
| `processing_duration_seconds` | `INTEGER` | Yes | `NULL` | Processing duration |
| `error_message` | `VARCHAR(2000)` | Yes | `NULL` | Error message |

**Indexes:**
- Primary Key: `log_id`
- Index: `shapefile_name`
- Index: `transformation_status`

---

Documents spatial join operations between GRIB2 grid cells and shapefile boundaries.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `join_id` | `VARCHAR(255)` | No | — | Primary key |
| `grib_file` | `VARCHAR(500)` | Yes | `NULL` | GRIB2 file name |
| `shapefile_name` | `VARCHAR(500)` | Yes | `NULL` | Shapefile name |
| `join_type` | `VARCHAR(50)` | Yes | `NULL` | Join type (Point-in-Polygon, Raster-to-Vector, Clip) |
| `gdal_command` | `VARCHAR(2000)` | Yes | `NULL` | GDAL command used |
| `features_matched` | `INTEGER` | Yes | `NULL` | Number of features matched |
| `features_total` | `INTEGER` | Yes | `NULL` | Total features |
| `match_percentage` | `NUMERIC(5, 2)` | Yes | `NULL` | Match percentage |
| `output_file` | `VARCHAR(1000)` | Yes | `NULL` | Output file path |
| `join_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Join timestamp |
| `forecast_id` | `VARCHAR(255)` | Yes | `NULL` | Foreign key to `grib2_forecasts.forecast_id` |
| `boundary_id` | `VARCHAR(255)` | Yes | `NULL` | Foreign key to `shapefile_boundaries.boundary_id` |

**Indexes:**
- Primary Key: `join_id`
- Index: `(forecast_id, boundary_id)`
- Index: `join_timestamp`

---

Documents coordinate reference system transformations and parameters.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `transformation_id` | `VARCHAR(255)` | No | — | Primary key |
| `source_crs` | `VARCHAR(50)` | No | — | Source CRS identifier |
| `target_crs` | `VARCHAR(50)` | No | — | Target CRS identifier |
| `source_crs_name` | `VARCHAR(255)` | Yes | `NULL` | Source CRS name |
| `target_crs_name` | `VARCHAR(255)` | Yes | `NULL` | Target CRS name |
| `transformation_method` | `VARCHAR(50)` | Yes | `NULL` | Method (GDAL, PROJ, Custom) |
| `central_meridian` | `NUMERIC(10, 6)` | Yes | `NULL` | Central meridian |
| `false_easting` | `NUMERIC(12, 2)` | Yes | `NULL` | False easting |
| `false_northing` | `NUMERIC(12, 2)` | Yes | `NULL` | False northing |
| `scale_factor` | `NUMERIC(10, 8)` | Yes | `NULL` | Scale factor |
| `latitude_of_origin` | `NUMERIC(10, 6)` | Yes | `NULL` | Latitude of origin |
| `units` | `VARCHAR(50)` | Yes | `NULL` | Units (degrees, meters, feet) |
| `accuracy_meters` | `NUMERIC(10, 2)` | Yes | `NULL` | Transformation accuracy |
| `usage_count` | `INTEGER` | No | `0` | Number of times used |

**Indexes:**
- Primary Key: `transformation_id`
- Index: `(source_crs, target_crs)`

---

Tracks data quality metrics for weather products.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `metric_id` | `VARCHAR(255)` | No | — | Primary key |
| `metric_date` | `DATE` | No | — | Metric date |
| `data_source` | `VARCHAR(50)` | No | — | Data source (GRIB2, Shapefile, API) |
| `files_processed` | `INTEGER` | No | `0` | Number of files processed |
| `files_successful` | `INTEGER` | No | `0` | Number of successful files |
| `files_failed` | `INTEGER` | No | `0` | Number of failed files |
| `success_rate` | `NUMERIC(5, 2)` | Yes | `NULL` | Success rate percentage |
| `total_records` | `INTEGER` | No | `0` | Total records processed |
| `records_with_errors` | `INTEGER` | No | `0` | Records with errors |
| `error_rate` | `NUMERIC(5, 2)` | Yes | `NULL` | Error rate percentage |
| `spatial_coverage_km2` | `NUMERIC(15, 2)` | Yes | `NULL` | Spatial coverage in square kilometers |
| `temporal_coverage_hours` | `INTEGER` | Yes | `NULL` | Temporal coverage in hours |
| `data_freshness_minutes` | `INTEGER` | Yes | `NULL` | Data freshness in minutes |
| `calculation_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Calculation timestamp |

**Indexes:**
- Primary Key: `metric_id`
- Index: `(metric_date, data_source)`
- Index: `metric_date`

---

Tracks data loading operations to Databricks.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `load_id` | `VARCHAR(255)` | No | — | Primary key |
| `source_file` | `VARCHAR(1000)` | Yes | `NULL` | Source file name |
| `target_table` | `VARCHAR(255)` | No | — | Target table |
| `load_start_time` | `TIMESTAMP_NTZ` | No | — | Load start time |
| `load_end_time` | `TIMESTAMP_NTZ` | Yes | `NULL` | Load end time |
| `load_duration_seconds` | `INTEGER` | Yes | `NULL` | Load duration |
| `records_loaded` | `INTEGER` | No | `0` | Number of records loaded |
| `file_size_mb` | `NUMERIC(10, 2)` | Yes | `NULL` | File size in MB |
| `load_rate_mb_per_sec` | `NUMERIC(10, 2)` | Yes | `NULL` | Load rate in MB/sec |
| `load_status` | `VARCHAR(50)` | Yes | `NULL` | Status (Success, Failed, Partial) |
| `error_message` | `VARCHAR(2000)` | Yes | `NULL` | Error message |
| `warehouse` | `VARCHAR(255)` | Yes | `NULL` | Warehouse used |
| `data_source_type` | `VARCHAR(50)` | Yes | `NULL` | Data source type |

**Indexes:**
- Primary Key: `load_id`
- Index: `target_table`
- Index: `load_status`
- Index: `load_start_time`

---

Pre-aggregated forecast data for performance optimization.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `aggregation_id` | `VARCHAR(255)` | No | — | Primary key |
| `parameter_name` | `VARCHAR(100)` | No | — | Forecast parameter name |
| `forecast_time` | `TIMESTAMP_NTZ` | No | — | Forecast valid time |
| `boundary_id` | `VARCHAR(255)` | Yes | `NULL` | Foreign key to `shapefile_boundaries.boundary_id` |
| `feature_type` | `VARCHAR(50)` | Yes | `NULL` | Feature type |
| `feature_name` | `VARCHAR(255)` | Yes | `NULL` | Feature name |
| `min_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Minimum forecast value |
| `max_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Maximum forecast value |
| `avg_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Average forecast value |
| `median_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Median forecast value |
| `std_dev_value` | `NUMERIC(10, 2)` | Yes | `NULL` | Standard deviation |
| `grid_cells_count` | `INTEGER` | Yes | `NULL` | Number of grid cells aggregated |
| `aggregation_timestamp` | `TIMESTAMP_NTZ` | No | `CURRENT_TIMESTAMP()` | Aggregation timestamp |

**Indexes:**
- Primary Key: `aggregation_id`
- Index: `(forecast_time, parameter_name)`
- Index: `boundary_id`
- Index: `feature_type`

---

---

---

## SQL Queries

This database includes **30 production SQL queries**, each designed to solve specific business problems for companies with $1M+ ARR. Each query includes:

- **Business Use Case**: The specific business problem this query solves
- **Description**: Technical explanation of what the query does
- **Client Deliverable**: What output or report this query generates
- **Business Value**: The business impact and value delivered
- **Complexity**: Technical complexity indicators
- **SQL Code**: Complete, production-ready SQL query

---

## Query 1: Production-Grade Spatial Weather Forecast Analysis with Multi-Level CTE Nesting and Geospatial Aggregations {#query-1}

**Use Case:** **Custom Weather Impact Modeling - Regional Forecast Accuracy Assessment for Insurance Risk Modeling**

**Description:** Enterprise-level spatial weather forecast analysis with multi-level CTE nesting, spatial aggregations within boundaries, forecast accuracy metrics, temporal analysis, and advanced window functions. Demonstrates production patterns used by NOAA and weather forecasting platforms.

**Business Value:** Forecast accuracy report by geographic boundary (CWA, Fire Zones) showing forecast reliability metrics, accuracy classifications, and temporal trends. Helps insurance companies assess forecast accuracy for risk modeling in specific counties and regions.

**Purpose:** Quantifies forecast reliability for specific geographic regions, enabling data-driven risk assessment and insurance underwriting decisions.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations (ST_WITHIN, ST_DISTANCE), complex aggregations, window functions with multiple frame clauses, percentile calculations, time-series analysis, correlated subqueries

```sql
WITH forecast_parameter_cohorts AS (
    -- First CTE: Identify forecast parameter cohorts and time windows
    SELECT
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        gf.grid_cell_latitude,
        gf.grid_cell_longitude,
        gf.parameter_value,
        gf.source_file,
        DATE_TRUNC('hour', gf.forecast_time) AS forecast_hour,
        DATE_TRUNC('day', gf.forecast_time) AS forecast_date,
        EXTRACT(HOUR FROM gf.forecast_time) AS forecast_hour_num,
        EXTRACT(EPOCH FROM (gf.forecast_time - CURRENT_TIMESTAMP)) / 3600 AS hours_until_forecast
    FROM grib2_forecasts gf
    WHERE gf.transformation_status = 'Success'
),
spatial_boundary_matching AS (
    -- Second CTE: Match forecasts to spatial boundaries using spatial operations
    SELECT
        fpc.forecast_id,
        fpc.parameter_name,
        fpc.forecast_time,
        fpc.forecast_hour,
        fpc.forecast_date,
        fpc.grid_cell_latitude,
        fpc.grid_cell_longitude,
        fpc.parameter_value,
        fpc.source_file,
        fpc.hours_until_forecast,
        sb.boundary_id,
        sb.feature_type,
        sb.feature_name,
        sb.feature_identifier,
        sb.state_code,
        sb.office_code,
        -- Spatial distance calculation (compatible across databases)
        CASE
            WHEN sb.boundary_geom IS NOT NULL AND fpc.grid_cell_geom IS NOT NULL THEN
                ST_DISTANCE(sb.boundary_geom, fpc.grid_cell_geom)
            ELSE NULL
        END AS spatial_distance_meters,
        -- Check if point is within boundary (using standard spatial functions)
        CASE
            WHEN sb.boundary_geom IS NOT NULL AND fpc.grid_cell_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(fpc.grid_cell_geom, sb.boundary_geom) THEN TRUE
                    ELSE FALSE
                END
            ELSE NULL
        END AS is_within_boundary
    FROM forecast_parameter_cohorts fpc
    LEFT JOIN shapefile_boundaries sb ON (
        sb.boundary_geom IS NOT NULL
        AND fpc.grid_cell_geom IS NOT NULL
        AND ST_DISTANCE(sb.boundary_geom, fpc.grid_cell_geom) < 50000
    )
),
boundary_forecast_aggregations AS (
    -- Third CTE: Aggregate forecasts by boundary with spatial filtering
    SELECT
        sbm.boundary_id,
        sbm.feature_type,
        sbm.feature_name,
        sbm.feature_identifier,
        sbm.state_code,
        sbm.office_code,
        sbm.parameter_name,
        sbm.forecast_time,
        sbm.forecast_hour,
        sbm.forecast_date,
        COUNT(DISTINCT sbm.forecast_id) AS grid_cells_count,
        COUNT(CASE WHEN sbm.is_within_boundary = TRUE THEN 1 END) AS cells_within_boundary,
        COUNT(CASE WHEN sbm.is_within_boundary = FALSE THEN 1 END) AS cells_near_boundary,
        MIN(sbm.parameter_value) AS min_forecast_value,
        MAX(sbm.parameter_value) AS max_forecast_value,
        AVG(sbm.parameter_value) AS avg_forecast_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sbm.parameter_value) AS median_forecast_value,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY sbm.parameter_value) AS q1_forecast_value,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY sbm.parameter_value) AS q3_forecast_value,
        STDDEV(sbm.parameter_value) AS stddev_forecast_value,
        AVG(sbm.spatial_distance_meters) AS avg_distance_to_boundary,
        MIN(sbm.spatial_distance_meters) AS min_distance_to_boundary
    FROM spatial_boundary_matching sbm
    WHERE sbm.is_within_boundary IS NOT NULL
    GROUP BY
        sbm.boundary_id,
        sbm.feature_type,
        sbm.feature_name,
        sbm.feature_identifier,
        sbm.state_code,
        sbm.office_code,
        sbm.parameter_name,
        sbm.forecast_time,
        sbm.forecast_hour,
        sbm.forecast_date
),
observation_forecast_comparison AS (
    -- Fourth CTE: Compare forecasts with actual observations for accuracy analysis
    SELECT
        bfa.boundary_id,
        bfa.feature_type,
        bfa.feature_name,
        bfa.feature_identifier,
        bfa.state_code,
        bfa.parameter_name,
        bfa.forecast_time,
        bfa.forecast_hour,
        bfa.forecast_date,
        bfa.grid_cells_count,
        bfa.cells_within_boundary,
        bfa.min_forecast_value,
        bfa.max_forecast_value,
        bfa.avg_forecast_value,
        bfa.median_forecast_value,
        bfa.q1_forecast_value,
        bfa.q3_forecast_value,
        bfa.stddev_forecast_value,
        -- Find nearest observation station
        (
            SELECT wo.station_id
            FROM weather_observations wo
            INNER JOIN weather_stations ws ON wo.station_id = ws.station_id
            WHERE ws.cwa_code = bfa.office_code
                AND wo.observation_time BETWEEN bfa.forecast_time - INTERVAL '1 hour' AND bfa.forecast_time + INTERVAL '1 hour'
            ORDER BY
                CASE
                    WHEN bfa.parameter_name = 'Temperature' THEN ABS(wo.temperature - bfa.avg_forecast_value)
                    WHEN bfa.parameter_name = 'Precipitation' THEN ABS(COALESCE(wo.precipitation_amount, 0) - bfa.avg_forecast_value)
                    WHEN bfa.parameter_name = 'WindSpeed' THEN ABS(wo.wind_speed - bfa.avg_forecast_value)
                    ELSE 999999
                END
            LIMIT 1
        ) AS nearest_station_id,
        -- Get actual observation value
        (
            SELECT
                CASE
                    WHEN bfa.parameter_name = 'Temperature' THEN wo.temperature
                    WHEN bfa.parameter_name = 'Precipitation' THEN COALESCE(wo.precipitation_amount, 0)
                    WHEN bfa.parameter_name = 'WindSpeed' THEN wo.wind_speed
                    ELSE NULL
                END
            FROM weather_observations wo
            INNER JOIN weather_stations ws ON wo.station_id = ws.station_id
            WHERE ws.cwa_code = bfa.office_code
                AND wo.observation_time BETWEEN bfa.forecast_time - INTERVAL '1 hour' AND bfa.forecast_time + INTERVAL '1 hour'
            ORDER BY
                CASE
                    WHEN bfa.parameter_name = 'Temperature' THEN ABS(wo.temperature - bfa.avg_forecast_value)
                    WHEN bfa.parameter_name = 'Precipitation' THEN ABS(COALESCE(wo.precipitation_amount, 0) - bfa.avg_forecast_value)
                    WHEN bfa.parameter_name = 'WindSpeed' THEN ABS(wo.wind_speed - bfa.avg_forecast_value)
                    ELSE 999999
                END
            LIMIT 1
        ) AS actual_observation_value
    FROM boundary_forecast_aggregations bfa
),
forecast_accuracy_metrics AS (
    -- Fifth CTE: Calculate forecast accuracy metrics with window functions
    SELECT
        ofc.boundary_id,
        ofc.feature_type,
        ofc.feature_name,
        ofc.feature_identifier,
        ofc.state_code,
        ofc.parameter_name,
        ofc.forecast_time,
        ofc.forecast_hour,
        ofc.forecast_date,
        ofc.grid_cells_count,
        ofc.cells_within_boundary,
        ofc.min_forecast_value,
        ofc.max_forecast_value,
        ROUND(CAST(ofc.avg_forecast_value AS NUMERIC), 2) AS avg_forecast_value,
        ROUND(CAST(ofc.median_forecast_value AS NUMERIC), 2) AS median_forecast_value,
        ROUND(CAST(ofc.q1_forecast_value AS NUMERIC), 2) AS q1_forecast_value,
        ROUND(CAST(ofc.q3_forecast_value AS NUMERIC), 2) AS q3_forecast_value,
        ROUND(CAST(ofc.stddev_forecast_value AS NUMERIC), 2) AS stddev_forecast_value,
        ofc.nearest_station_id,
        ROUND(CAST(ofc.actual_observation_value AS NUMERIC), 2) AS actual_observation_value,
        -- Forecast error calculations
        CASE
            WHEN ofc.actual_observation_value IS NOT NULL THEN
                ABS(ofc.avg_forecast_value - ofc.actual_observation_value)
            ELSE NULL
        END AS absolute_error,
        CASE
            WHEN ofc.actual_observation_value IS NOT NULL AND ofc.actual_observation_value != 0 THEN
                ABS((ofc.avg_forecast_value - ofc.actual_observation_value) / ofc.actual_observation_value) * 100
            ELSE NULL
        END AS percentage_error,
        -- Window functions for accuracy trends
        AVG(CASE WHEN ofc.actual_observation_value IS NOT NULL THEN ABS(ofc.avg_forecast_value - ofc.actual_observation_value) ELSE NULL END)
            OVER (
                PARTITION BY ofc.boundary_id, ofc.parameter_name
                ORDER BY ofc.forecast_time
                ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
            ) AS moving_avg_error_10,
        STDDEV(CASE WHEN ofc.actual_observation_value IS NOT NULL THEN ABS(ofc.avg_forecast_value - ofc.actual_observation_value) ELSE NULL END)
            OVER (
                PARTITION BY ofc.boundary_id, ofc.parameter_name
                ORDER BY ofc.forecast_time
                ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
            ) AS moving_stddev_error_20
    FROM observation_forecast_comparison ofc
),
temporal_forecast_analysis AS (
    -- Sixth CTE: Temporal analysis with multiple window function patterns
    SELECT
        fam.boundary_id,
        fam.feature_type,
        fam.feature_name,
        fam.feature_identifier,
        fam.state_code,
        fam.parameter_name,
        fam.forecast_time,
        fam.forecast_hour,
        fam.forecast_date,
        fam.grid_cells_count,
        fam.avg_forecast_value,
        fam.median_forecast_value,
        fam.actual_observation_value,
        ROUND(CAST(fam.absolute_error AS NUMERIC), 2) AS absolute_error,
        ROUND(CAST(fam.percentage_error AS NUMERIC), 2) AS percentage_error,
        ROUND(CAST(fam.moving_avg_error_10 AS NUMERIC), 2) AS moving_avg_error_10,
        ROUND(CAST(fam.moving_stddev_error_20 AS NUMERIC), 2) AS moving_stddev_error_20,
        -- Time-series window functions
        LAG(fam.avg_forecast_value, 1) OVER (
            PARTITION BY fam.boundary_id, fam.parameter_name
            ORDER BY fam.forecast_time
        ) AS prev_forecast_value,
        LEAD(fam.avg_forecast_value, 1) OVER (
            PARTITION BY fam.boundary_id, fam.parameter_name
            ORDER BY fam.forecast_time
        ) AS next_forecast_value,
        -- Running totals and cumulative metrics
        SUM(fam.avg_forecast_value) OVER (
            PARTITION BY fam.boundary_id, fam.parameter_name
            ORDER BY fam.forecast_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_forecast_sum,
        AVG(fam.avg_forecast_value) OVER (
            PARTITION BY fam.boundary_id, fam.parameter_name
            ORDER BY fam.forecast_time
            RANGE BETWEEN INTERVAL '24 hours' PRECEDING AND CURRENT ROW
        ) AS avg_forecast_24h_range,
        -- Ranking functions
        ROW_NUMBER() OVER (
            PARTITION BY fam.boundary_id, fam.parameter_name
            ORDER BY fam.forecast_time DESC
        ) AS forecast_recency_rank,
        PERCENT_RANK() OVER (
            PARTITION BY fam.feature_type
            ORDER BY fam.avg_forecast_value DESC
        ) AS forecast_value_percentile,
        NTILE(5) OVER (
            PARTITION BY fam.feature_type
            ORDER BY fam.avg_forecast_value DESC
        ) AS forecast_value_quintile
    FROM forecast_accuracy_metrics fam
),
final_forecast_analytics AS (
    -- Seventh CTE: Final analytics with comprehensive metrics and classifications
    SELECT
        tfa.boundary_id,
        tfa.feature_type,
        tfa.feature_name,
        tfa.feature_identifier,
        tfa.state_code,
        tfa.parameter_name,
        tfa.forecast_time,
        tfa.forecast_hour,
        tfa.forecast_date,
        tfa.grid_cells_count,
        tfa.avg_forecast_value,
        tfa.median_forecast_value,
        tfa.actual_observation_value,
        tfa.absolute_error,
        tfa.percentage_error,
        tfa.moving_avg_error_10,
        tfa.moving_stddev_error_20,
        tfa.prev_forecast_value,
        tfa.next_forecast_value,
        tfa.cumulative_forecast_sum,
        ROUND(CAST(tfa.avg_forecast_24h_range AS NUMERIC), 2) AS avg_forecast_24h_range,
        tfa.forecast_recency_rank,
        ROUND(CAST(tfa.forecast_value_percentile * 100 AS NUMERIC), 2) AS forecast_value_percentile,
        tfa.forecast_value_quintile,
        -- Forecast trend analysis
        CASE
            WHEN tfa.prev_forecast_value IS NOT NULL THEN
                tfa.avg_forecast_value - tfa.prev_forecast_value
            ELSE NULL
        END AS forecast_change_from_previous,
        CASE
            WHEN tfa.prev_forecast_value IS NOT NULL AND tfa.prev_forecast_value != 0 THEN
                ((tfa.avg_forecast_value - tfa.prev_forecast_value) / ABS(tfa.prev_forecast_value)) * 100
            ELSE NULL
        END AS forecast_change_percentage,
        -- Accuracy classification
        CASE
            WHEN tfa.absolute_error IS NULL THEN 'No Observation'
            WHEN tfa.absolute_error <= 2.0 THEN 'Highly Accurate'
            WHEN tfa.absolute_error <= 5.0 THEN 'Accurate'
            WHEN tfa.absolute_error <= 10.0 THEN 'Moderate Accuracy'
            ELSE 'Low Accuracy'
        END AS accuracy_classification,
        -- Forecast value classification
        CASE
            WHEN tfa.parameter_name = 'Temperature' THEN
                CASE
                    WHEN tfa.avg_forecast_value < 32 THEN 'Freezing'
                    WHEN tfa.avg_forecast_value < 50 THEN 'Cold'
                    WHEN tfa.avg_forecast_value < 70 THEN 'Moderate'
                    WHEN tfa.avg_forecast_value < 85 THEN 'Warm'
                    ELSE 'Hot'
                END
            WHEN tfa.parameter_name = 'Precipitation' THEN
                CASE
                    WHEN tfa.avg_forecast_value = 0 THEN 'No Precipitation'
                    WHEN tfa.avg_forecast_value < 0.1 THEN 'Light'
                    WHEN tfa.avg_forecast_value < 0.5 THEN 'Moderate'
                    ELSE 'Heavy'
                END
            WHEN tfa.parameter_name = 'WindSpeed' THEN
                CASE
                    WHEN tfa.avg_forecast_value < 10 THEN 'Calm'
                    WHEN tfa.avg_forecast_value < 20 THEN 'Light Breeze'
                    WHEN tfa.avg_forecast_value < 30 THEN 'Moderate Wind'
                    ELSE 'Strong Wind'
                END
            ELSE 'Unknown'
        END AS forecast_category
    FROM temporal_forecast_analysis tfa
)
SELECT
    boundary_id,
    feature_type,
    feature_name,
    feature_identifier,
    state_code,
    parameter_name,
    forecast_time,
    forecast_hour,
    forecast_date,
    grid_cells_count,
    avg_forecast_value,
    median_forecast_value,
    actual_observation_value,
    absolute_error,
    percentage_error,
    moving_avg_error_10,
    moving_stddev_error_20,
    ROUND(CAST(forecast_change_from_previous AS NUMERIC), 2) AS forecast_change_from_previous,
    ROUND(CAST(forecast_change_percentage AS NUMERIC), 2) AS forecast_change_percentage,
    accuracy_classification,
    forecast_category,
    forecast_value_percentile,
    forecast_value_quintile,
    forecast_recency_rank
FROM final_forecast_analytics
WHERE forecast_recency_rank <= 100
ORDER BY forecast_time DESC, boundary_id, parameter_name;
```

---

## Query 2: Recursive Spatial Boundary Hierarchy Analysis with Multi-Hop Geospatial Traversal {#query-2}

**Use Case:** **Custom Map Development - Multi-Level Geographic Hierarchy Visualization for Agriculture Insurance**

**Description:** Enterprise-level recursive spatial analysis using recursive CTE for multi-level boundary relationships, spatial hierarchy traversal, boundary intersection detection, and geospatial path discovery. Implements production patterns for analyzing nested geographic boundaries (e.g., counties within states, fire zones within CWAs).

**Business Value:** Spatial hierarchy relationships showing nested boundaries (states → counties → fire zones) with forecast aggregations and optimal path analysis. Enables agriculture companies to understand geographic relationships for multi-scale crop insurance analysis.

**Purpose:** Provides multi-scale geographic analysis enabling clients to understand relationships between administrative boundaries and weather zones for comprehensive risk assessment.

**Complexity:** Advanced recursive CTE with spatial operations, multi-hop traversal, cycle detection, path weight calculations, spatial intersection analysis, multiple CTE nesting levels (6+)

```sql
WITH RECURSIVE boundary_spatial_hierarchy AS (
    -- Anchor CTE: Direct spatial relationships between boundaries
    SELECT DISTINCT
        sb1.boundary_id AS parent_boundary_id,
        sb1.feature_type AS parent_feature_type,
        sb1.feature_name AS parent_feature_name,
        sb2.boundary_id AS child_boundary_id,
        sb2.feature_type AS child_feature_type,
        sb2.feature_name AS child_feature_name,
        1 AS hierarchy_level,
        ARRAY[sb1.boundary_id, sb2.boundary_id] AS boundary_path,
        CASE
            WHEN sb1.boundary_geom IS NOT NULL AND sb2.boundary_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(sb2.boundary_geom, sb1.boundary_geom) THEN 'Contains'
                    WHEN ST_WITHIN(sb1.boundary_geom, sb2.boundary_geom) THEN 'Contained By'
                    WHEN ST_INTERSECTS(sb1.boundary_geom, sb2.boundary_geom) THEN 'Intersects'
                    ELSE 'Near'
                END
            ELSE NULL
        END AS spatial_relationship,
        CASE
            WHEN sb1.boundary_geom IS NOT NULL AND sb2.boundary_geom IS NOT NULL THEN
                ST_DISTANCE(sb1.boundary_geom, sb2.boundary_geom)
            ELSE NULL
        END AS spatial_distance,
        CASE
            WHEN sb1.boundary_geom IS NOT NULL AND sb2.boundary_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(sb2.boundary_geom, sb1.boundary_geom) THEN
                        ST_AREA(sb2.boundary_geom) / NULLIF(ST_AREA(sb1.boundary_geom), 0) * 100
                    ELSE NULL
                END
            ELSE NULL
        END AS coverage_percentage
    FROM shapefile_boundaries sb1
    CROSS JOIN shapefile_boundaries sb2
    WHERE sb1.boundary_id != sb2.boundary_id
        AND sb1.boundary_geom IS NOT NULL
        AND sb2.boundary_geom IS NOT NULL
        AND (
            ST_WITHIN(sb2.boundary_geom, sb1.boundary_geom)
            OR ST_INTERSECTS(sb1.boundary_geom, sb2.boundary_geom)
            OR ST_DISTANCE(sb1.boundary_geom, sb2.boundary_geom) < 50000
        )

    UNION ALL

    -- Recursive step: Multi-hop spatial relationships
    SELECT
        bsh.parent_boundary_id,
        bsh.parent_feature_type,
        bsh.parent_feature_name,
        sb3.boundary_id AS child_boundary_id,
        sb3.feature_type AS child_feature_type,
        sb3.feature_name AS child_feature_name,
        bsh.hierarchy_level + 1,
        bsh.boundary_path || ARRAY[sb3.boundary_id],
        CASE
            WHEN bsh.spatial_relationship = 'Contains' AND sb3.boundary_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(sb3.boundary_geom,
                        (SELECT boundary_geom FROM shapefile_boundaries WHERE boundary_id = bsh.parent_boundary_id)
                    ) THEN 'Contains'
                    WHEN ST_INTERSECTS(sb3.boundary_geom,
                        (SELECT boundary_geom FROM shapefile_boundaries WHERE boundary_id = bsh.parent_boundary_id)
                    ) THEN 'Intersects'
                    ELSE 'Near'
                END
            ELSE bsh.spatial_relationship
        END,
        CASE
            WHEN sb3.boundary_geom IS NOT NULL THEN
                ST_DISTANCE(
                    (SELECT boundary_geom FROM shapefile_boundaries WHERE boundary_id = bsh.parent_boundary_id),
                    sb3.boundary_geom
                )
            ELSE bsh.spatial_distance
        END,
        CASE
            WHEN sb3.boundary_geom IS NOT NULL AND bsh.spatial_relationship = 'Contains' THEN
                ST_AREA(sb3.boundary_geom) / NULLIF(
                    ST_AREA((SELECT boundary_geom FROM shapefile_boundaries WHERE boundary_id = bsh.parent_boundary_id)),
                    0
                ) * 100
            ELSE bsh.coverage_percentage
        END
    FROM boundary_spatial_hierarchy bsh
    INNER JOIN shapefile_boundaries sb3 ON (
        NOT sb3.boundary_id = ANY(bsh.boundary_path)
        AND sb3.boundary_geom IS NOT NULL
        AND (
            ST_WITHIN(sb3.boundary_geom,
                (SELECT boundary_geom FROM shapefile_boundaries WHERE boundary_id = bsh.child_boundary_id)
            )
            OR ST_INTERSECTS(sb3.boundary_geom,
                (SELECT boundary_geom FROM shapefile_boundaries WHERE boundary_id = bsh.child_boundary_id)
            )
        )
    )
    WHERE bsh.hierarchy_level < 5
        AND array_length(bsh.boundary_path, 1) < 6
),
hierarchy_metrics AS (
    -- Second CTE: Calculate hierarchy metrics with aggregations
    SELECT
        bsh.parent_boundary_id,
        bsh.parent_feature_type,
        bsh.parent_feature_name,
        bsh.child_boundary_id,
        bsh.child_feature_type,
        bsh.child_feature_name,
        bsh.hierarchy_level,
        bsh.boundary_path,
        array_length(bsh.boundary_path, 1) AS path_length,
        bsh.spatial_relationship,
        ROUND(CAST(bsh.spatial_distance AS NUMERIC), 2) AS spatial_distance,
        ROUND(CAST(bsh.coverage_percentage AS NUMERIC), 2) AS coverage_percentage,
        -- Count children at each level
        COUNT(*) OVER (
            PARTITION BY bsh.parent_boundary_id, bsh.hierarchy_level
        ) AS children_count_at_level,
        -- Total descendants count
        COUNT(*) OVER (
            PARTITION BY bsh.parent_boundary_id
        ) AS total_descendants_count,
        -- Path weight (inverse of hierarchy level)
        1.0 / NULLIF(bsh.hierarchy_level, 0) AS path_weight
    FROM boundary_spatial_hierarchy bsh
),
shortest_paths AS (
    -- Third CTE: Find shortest paths between boundaries
    SELECT
        hm1.parent_boundary_id,
        hm1.child_boundary_id AS intermediate_boundary_id,
        hm2.child_boundary_id AS target_boundary_id,
        hm1.hierarchy_level + hm2.hierarchy_level AS total_hops,
        hm1.boundary_path || hm2.boundary_path[2:] AS combined_path,
        hm1.path_weight + hm2.path_weight AS combined_path_weight,
        hm1.spatial_distance + COALESCE(hm2.spatial_distance, 0) AS combined_distance
    FROM hierarchy_metrics hm1
    INNER JOIN hierarchy_metrics hm2 ON hm1.child_boundary_id = hm2.parent_boundary_id
    WHERE hm1.child_boundary_id != hm2.child_boundary_id
        AND NOT hm2.child_boundary_id = ANY(hm1.boundary_path)
),
path_optimization AS (
    -- Fourth CTE: Optimize paths and find best routes
    SELECT
        sp.parent_boundary_id,
        sp.target_boundary_id,
        sp.total_hops,
        sp.combined_path,
        sp.combined_path_weight,
        sp.combined_distance,
        -- Window functions for path comparison
        MIN(sp.combined_path_weight) OVER (
            PARTITION BY sp.parent_boundary_id, sp.target_boundary_id
        ) AS min_path_weight,
        MIN(sp.total_hops) OVER (
            PARTITION BY sp.parent_boundary_id, sp.target_boundary_id
        ) AS min_hops,
        ROW_NUMBER() OVER (
            PARTITION BY sp.parent_boundary_id, sp.target_boundary_id
            ORDER BY sp.combined_path_weight ASC, sp.total_hops ASC
        ) AS path_rank
    FROM shortest_paths sp
),
forecast_boundary_aggregations AS (
    -- Fifth CTE: Aggregate forecasts by boundary hierarchy
    SELECT
        po.parent_boundary_id,
        po.target_boundary_id,
        po.total_hops,
        po.combined_path,
        po.path_rank,
        sb_parent.feature_type AS parent_feature_type,
        sb_parent.feature_name AS parent_feature_name,
        sb_target.feature_type AS target_feature_type,
        sb_target.feature_name AS target_feature_name,
        COUNT(DISTINCT gf.forecast_id) AS forecast_count,
        COUNT(DISTINCT gf.parameter_name) AS parameter_count,
        AVG(gf.parameter_value) AS avg_forecast_value,
        MIN(gf.parameter_value) AS min_forecast_value,
        MAX(gf.parameter_value) AS max_forecast_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gf.parameter_value) AS median_forecast_value
    FROM path_optimization po
    INNER JOIN shapefile_boundaries sb_parent ON po.parent_boundary_id = sb_parent.boundary_id
    INNER JOIN shapefile_boundaries sb_target ON po.target_boundary_id = sb_target.boundary_id
    LEFT JOIN grib2_forecasts gf ON (
        gf.grid_cell_geom IS NOT NULL
        AND (
            ST_WITHIN(gf.grid_cell_geom, sb_parent.boundary_geom)
            OR ST_WITHIN(gf.grid_cell_geom, sb_target.boundary_geom)
        )
    )
    WHERE po.path_rank = 1
    GROUP BY
        po.parent_boundary_id,
        po.target_boundary_id,
        po.total_hops,
        po.combined_path,
        po.path_rank,
        sb_parent.feature_type,
        sb_parent.feature_name,
        sb_target.feature_type,
        sb_target.feature_name
),
final_hierarchy_analysis AS (
    -- Sixth CTE: Final analysis with comprehensive metrics
    SELECT
        fba.parent_boundary_id,
        fba.parent_feature_type,
        fba.parent_feature_name,
        fba.target_boundary_id,
        fba.target_feature_type,
        fba.target_feature_name,
        fba.total_hops,
        fba.combined_path,
        fba.forecast_count,
        fba.parameter_count,
        ROUND(CAST(fba.avg_forecast_value AS NUMERIC), 2) AS avg_forecast_value,
        ROUND(CAST(fba.min_forecast_value AS NUMERIC), 2) AS min_forecast_value,
        ROUND(CAST(fba.max_forecast_value AS NUMERIC), 2) AS max_forecast_value,
        ROUND(CAST(fba.median_forecast_value AS NUMERIC), 2) AS median_forecast_value,
        -- Window functions for comparison
        AVG(fba.avg_forecast_value) OVER (
            PARTITION BY fba.parent_feature_type
        ) AS avg_by_feature_type,
        PERCENT_RANK() OVER (
            PARTITION BY fba.parent_feature_type
            ORDER BY fba.forecast_count DESC
        ) AS forecast_count_percentile,
        NTILE(4) OVER (
            ORDER BY fba.total_hops ASC
        ) AS hop_quartile
    FROM forecast_boundary_aggregations fba
)
SELECT
    parent_boundary_id,
    parent_feature_type,
    parent_feature_name,
    target_boundary_id,
    target_feature_type,
    target_feature_name,
    total_hops,
    combined_path,
    forecast_count,
    parameter_count,
    avg_forecast_value,
    min_forecast_value,
    max_forecast_value,
    median_forecast_value,
    ROUND(CAST(avg_by_feature_type AS NUMERIC), 2) AS avg_by_feature_type,
    ROUND(CAST(forecast_count_percentile * 100 AS NUMERIC), 2) AS forecast_count_percentile,
    hop_quartile
FROM final_hierarchy_analysis
WHERE forecast_count > 0
ORDER BY total_hops ASC, forecast_count DESC
LIMIT 200;
```

---

## Query 3: Multi-Parameter Weather Correlation Analysis with Cross-Parameter Temporal Patterns {#query-3}

**Use Case:** **Physical Climate Risk Assessment - Multi-Parameter Risk Correlation for Renewable Energy Planning**

**Description:** Enterprise-level multi-parameter weather correlation analysis with cross-parameter temporal pattern detection, correlation matrices, lag analysis, and predictive indicators. Implements production patterns for analyzing relationships between temperature, precipitation, wind speed, and other meteorological parameters.

**Business Value:** Correlation analysis between temperature, precipitation, and wind patterns with temporal lag indicators and weather pattern classifications. Helps energy companies understand correlation between temperature and wind for renewable energy generation planning.

**Purpose:** Identifies compound weather risks (e.g., high temp + low precip = drought risk) and enables predictive planning for renewable energy operations.

**Complexity:** Multiple CTEs (8+ levels), cross-parameter joins, correlation calculations, lag/lead analysis, window functions with multiple frame clauses, temporal pattern detection, UNION operations

```sql
WITH parameter_time_series AS (
    -- First CTE: Create unified time series for all parameters
    SELECT
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        DATE_TRUNC('hour', gf.forecast_time) AS forecast_hour,
        DATE_TRUNC('day', gf.forecast_time) AS forecast_date,
        gf.grid_cell_latitude,
        gf.grid_cell_longitude,
        gf.parameter_value,
        -- Round coordinates to grid resolution for matching
        ROUND(gf.grid_cell_latitude::NUMERIC, 2) AS rounded_lat,
        ROUND(gf.grid_cell_longitude::NUMERIC, 2) AS rounded_lon
    FROM grib2_forecasts gf
    WHERE gf.transformation_status = 'Success'
        AND gf.parameter_name IN ('Temperature', 'Precipitation', 'WindSpeed', 'Dewpoint', 'SkyCover')
),
temperature_series AS (
    -- Second CTE: Temperature parameter series
    SELECT
        pts.forecast_id,
        pts.forecast_time,
        pts.forecast_hour,
        pts.forecast_date,
        pts.rounded_lat,
        pts.rounded_lon,
        pts.parameter_value AS temperature_value
    FROM parameter_time_series pts
    WHERE pts.parameter_name = 'Temperature'
),
precipitation_series AS (
    -- Third CTE: Precipitation parameter series
    SELECT
        pts.forecast_id,
        pts.forecast_time,
        pts.forecast_hour,
        pts.forecast_date,
        pts.rounded_lat,
        pts.rounded_lon,
        pts.parameter_value AS precipitation_value
    FROM parameter_time_series pts
    WHERE pts.parameter_name = 'Precipitation'
),
windspeed_series AS (
    -- Fourth CTE: Wind speed parameter series
    SELECT
        pts.forecast_id,
        pts.forecast_time,
        pts.forecast_hour,
        pts.forecast_date,
        pts.rounded_lat,
        pts.rounded_lon,
        pts.parameter_value AS windspeed_value
    FROM parameter_time_series pts
    WHERE pts.parameter_name = 'WindSpeed'
),
multi_parameter_join AS (
    -- Fifth CTE: Join all parameters by location and time
    SELECT
        COALESCE(ts.forecast_time, ps.forecast_time, ws.forecast_time) AS forecast_time,
        COALESCE(ts.forecast_hour, ps.forecast_hour, ws.forecast_hour) AS forecast_hour,
        COALESCE(ts.forecast_date, ps.forecast_date, ws.forecast_date) AS forecast_date,
        COALESCE(ts.rounded_lat, ps.rounded_lat, ws.rounded_lat) AS rounded_lat,
        COALESCE(ts.rounded_lon, ps.rounded_lon, ws.rounded_lon) AS rounded_lon,
        ts.temperature_value,
        ps.precipitation_value,
        ws.windspeed_value,
        -- Calculate derived metrics
        CASE
            WHEN ts.temperature_value IS NOT NULL AND ps.precipitation_value IS NOT NULL THEN
                ts.temperature_value - (ps.precipitation_value * 5.0)
            ELSE NULL
        END AS apparent_temperature,
        CASE
            WHEN ts.temperature_value IS NOT NULL AND ws.windspeed_value IS NOT NULL THEN
                CASE
                    WHEN ws.windspeed_value > 0 THEN
                        35.74 + (0.6215 * ts.temperature_value) -
                        (35.75 * POWER(ws.windspeed_value, 0.16)) +
                        (0.4275 * ts.temperature_value * POWER(ws.windspeed_value, 0.16))
                    ELSE ts.temperature_value
                END
            ELSE NULL
        END AS wind_chill_temperature
    FROM temperature_series ts
    FULL OUTER JOIN precipitation_series ps ON (
        ts.rounded_lat = ps.rounded_lat
        AND ts.rounded_lon = ps.rounded_lon
        AND ts.forecast_hour = ps.forecast_hour
    )
    FULL OUTER JOIN windspeed_series ws ON (
        COALESCE(ts.rounded_lat, ps.rounded_lat) = ws.rounded_lat
        AND COALESCE(ts.rounded_lon, ps.rounded_lon) = ws.rounded_lon
        AND COALESCE(ts.forecast_hour, ps.forecast_hour) = ws.forecast_hour
    )
),
temporal_lag_analysis AS (
    -- Sixth CTE: Temporal lag analysis for correlation detection
    SELECT
        mpj.forecast_time,
        mpj.forecast_hour,
        mpj.forecast_date,
        mpj.rounded_lat,
        mpj.rounded_lon,
        mpj.temperature_value,
        mpj.precipitation_value,
        mpj.windspeed_value,
        mpj.apparent_temperature,
        mpj.wind_chill_temperature,
        -- Lag values for correlation analysis
        LAG(mpj.temperature_value, 1) OVER (
            PARTITION BY mpj.rounded_lat, mpj.rounded_lon
            ORDER BY mpj.forecast_time
        ) AS temp_lag_1h,
        LAG(mpj.temperature_value, 3) OVER (
            PARTITION BY mpj.rounded_lat, mpj.rounded_lon
            ORDER BY mpj.forecast_time
        ) AS temp_lag_3h,
        LAG(mpj.precipitation_value, 1) OVER (
            PARTITION BY mpj.rounded_lat, mpj.rounded_lon
            ORDER BY mpj.forecast_time
        ) AS precip_lag_1h,
        LEAD(mpj.temperature_value, 1) OVER (
            PARTITION BY mpj.rounded_lat, mpj.rounded_lon
            ORDER BY mpj.forecast_time
        ) AS temp_lead_1h,
        LEAD(mpj.precipitation_value, 1) OVER (
            PARTITION BY mpj.rounded_lat, mpj.rounded_lon
            ORDER BY mpj.forecast_time
        ) AS precip_lead_1h,
        -- Moving averages for trend detection
        AVG(mpj.temperature_value) OVER (
            PARTITION BY mpj.rounded_lat, mpj.rounded_lon
            ORDER BY mpj.forecast_time
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) AS temp_moving_avg_6h,
        AVG(mpj.precipitation_value) OVER (
            PARTITION BY mpj.rounded_lat, mpj.rounded_lon
            ORDER BY mpj.forecast_time
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS precip_moving_avg_12h,
        AVG(mpj.windspeed_value) OVER (
            PARTITION BY mpj.rounded_lat, mpj.rounded_lon
            ORDER BY mpj.forecast_time
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS windspeed_moving_avg_24h
    FROM multi_parameter_join mpj
),
correlation_calculations AS (
    -- Seventh CTE: Calculate correlation metrics
    SELECT
        tla.forecast_time,
        tla.forecast_hour,
        tla.forecast_date,
        tla.rounded_lat,
        tla.rounded_lon,
        ROUND(CAST(tla.temperature_value AS NUMERIC), 2) AS temperature_value,
        ROUND(CAST(tla.precipitation_value AS NUMERIC), 2) AS precipitation_value,
        ROUND(CAST(tla.windspeed_value AS NUMERIC), 2) AS windspeed_value,
        ROUND(CAST(tla.apparent_temperature AS NUMERIC), 2) AS apparent_temperature,
        ROUND(CAST(tla.wind_chill_temperature AS NUMERIC), 2) AS wind_chill_temperature,
        ROUND(CAST(tla.temp_lag_1h AS NUMERIC), 2) AS temp_lag_1h,
        ROUND(CAST(tla.temp_lag_3h AS NUMERIC), 2) AS temp_lag_3h,
        ROUND(CAST(tla.precip_lag_1h AS NUMERIC), 2) AS precip_lag_1h,
        ROUND(CAST(tla.temp_lead_1h AS NUMERIC), 2) AS temp_lead_1h,
        ROUND(CAST(tla.precip_lead_1h AS NUMERIC), 2) AS precip_lead_1h,
        ROUND(CAST(tla.temp_moving_avg_6h AS NUMERIC), 2) AS temp_moving_avg_6h,
        ROUND(CAST(tla.precip_moving_avg_12h AS NUMERIC), 2) AS precip_moving_avg_12h,
        ROUND(CAST(tla.windspeed_moving_avg_24h AS NUMERIC), 2) AS windspeed_moving_avg_24h,
        -- Temperature change indicators
        CASE
            WHEN tla.temp_lag_1h IS NOT NULL THEN
                tla.temperature_value - tla.temp_lag_1h
            ELSE NULL
        END AS temp_change_1h,
        CASE
            WHEN tla.temp_lag_3h IS NOT NULL THEN
                tla.temperature_value - tla.temp_lag_3h
            ELSE NULL
        END AS temp_change_3h,
        -- Precipitation change indicators
        CASE
            WHEN tla.precip_lag_1h IS NOT NULL THEN
                tla.precipitation_value - tla.precip_lag_1h
            ELSE NULL
        END AS precip_change_1h,
        -- Correlation indicators (simplified correlation coefficients)
        CASE
            WHEN tla.temperature_value IS NOT NULL AND tla.precipitation_value IS NOT NULL THEN
                CASE
                    WHEN tla.temperature_value > tla.temp_moving_avg_6h
                         AND tla.precipitation_value > tla.precip_moving_avg_12h THEN 'Both Above Average'
                    WHEN tla.temperature_value < tla.temp_moving_avg_6h
                         AND tla.precipitation_value < tla.precip_moving_avg_12h THEN 'Both Below Average'
                    WHEN tla.temperature_value > tla.temp_moving_avg_6h
                         AND tla.precipitation_value < tla.precip_moving_avg_12h THEN 'Temp High, Precip Low'
                    WHEN tla.temperature_value < tla.temp_moving_avg_6h
                         AND tla.precipitation_value > tla.precip_moving_avg_12h THEN 'Temp Low, Precip High'
                    ELSE 'Mixed'
                END
            ELSE NULL
        END AS correlation_pattern
    FROM temporal_lag_analysis tla
),
pattern_classification AS (
    -- Eighth CTE: Classify weather patterns
    SELECT
        cc.forecast_time,
        cc.forecast_hour,
        cc.forecast_date,
        cc.rounded_lat,
        cc.rounded_lon,
        cc.temperature_value,
        cc.precipitation_value,
        cc.windspeed_value,
        cc.apparent_temperature,
        cc.wind_chill_temperature,
        cc.temp_change_1h,
        cc.temp_change_3h,
        cc.precip_change_1h,
        cc.correlation_pattern,
        -- Weather pattern classification
        CASE
            WHEN cc.temperature_value < 32 AND cc.precipitation_value > 0 THEN 'Freezing Precipitation'
            WHEN cc.temperature_value >= 32 AND cc.temperature_value < 50
                 AND cc.precipitation_value > 0.1 THEN 'Cold Rain'
            WHEN cc.temperature_value >= 50 AND cc.temperature_value < 70
                 AND cc.precipitation_value > 0.1 THEN 'Moderate Rain'
            WHEN cc.temperature_value >= 70 AND cc.precipitation_value > 0.1 THEN 'Warm Rain'
            WHEN cc.temperature_value >= 85 AND cc.windspeed_value < 5 THEN 'Hot Calm'
            WHEN cc.windspeed_value > 30 THEN 'High Wind'
            WHEN cc.precipitation_value = 0 AND cc.temperature_value BETWEEN 60 AND 80 THEN 'Pleasant'
            ELSE 'Other'
        END AS weather_pattern,
        -- Window functions for pattern frequency
        COUNT(*) OVER (
            PARTITION BY cc.rounded_lat, cc.rounded_lon, cc.correlation_pattern
        ) AS pattern_frequency,
        PERCENT_RANK() OVER (
            PARTITION BY cc.rounded_lat, cc.rounded_lon
            ORDER BY cc.temperature_value DESC
        ) AS temp_percentile,
        NTILE(5) OVER (
            PARTITION BY cc.rounded_lat, cc.rounded_lon
            ORDER BY cc.precipitation_value DESC
        ) AS precip_quintile
    FROM correlation_calculations cc
)
SELECT
    forecast_time,
    forecast_hour,
    forecast_date,
    rounded_lat,
    rounded_lon,
    temperature_value,
    precipitation_value,
    windspeed_value,
    apparent_temperature,
    wind_chill_temperature,
    ROUND(CAST(temp_change_1h AS NUMERIC), 2) AS temp_change_1h,
    ROUND(CAST(temp_change_3h AS NUMERIC), 2) AS temp_change_3h,
    ROUND(CAST(precip_change_1h AS NUMERIC), 2) AS precip_change_1h,
    correlation_pattern,
    weather_pattern,
    pattern_frequency,
    ROUND(CAST(temp_percentile * 100 AS NUMERIC), 2) AS temp_percentile,
    precip_quintile
FROM pattern_classification
WHERE forecast_time >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY forecast_time DESC, rounded_lat, rounded_lon
LIMIT 1000;
```

---

## Query 4: Spatial Join Optimization Analysis with Boundary-Forecast Matching Efficiency Metrics {#query-4}

**Use Case:** **Custom Weather Impact Modeling - Boundary-Forecast Matching Efficiency for Logistics Optimization**

**Description:** Enterprise-level spatial join optimization analysis evaluating boundary-forecast matching efficiency, spatial index utilization, join performance metrics, and optimization opportunities. Implements production patterns for optimizing geospatial data joins.

**Business Value:** Optimizes forecast-to-boundary matching for faster client deliverables and improved operational efficiency.

**Purpose:** Analysis of how efficiently forecasts match to client-defined boundaries with optimization recommendations. Helps logistics companies optimize forecast-to-delivery-zone matching for faster route planning.

**Business Value:** Optimizes forecast-to-boundary matching for faster client deliverables and improved operational efficiency.

**Complexity:** Multiple CTEs (7+ levels), spatial join analysis, performance metrics, optimization scoring, window functions, correlated subqueries, UNION operations

```sql
WITH spatial_join_base_metrics AS (
    -- First CTE: Base spatial join metrics
    SELECT
        sjr.join_id,
        sjr.grib_file,
        sjr.shapefile_name,
        sjr.join_type,
        sjr.features_matched,
        sjr.features_total,
        sjr.match_percentage,
        sjr.join_timestamp,
        sjr.forecast_id,
        sjr.boundary_id,
        -- Calculate join efficiency
        CASE
            WHEN sjr.features_total > 0 THEN
                (sjr.features_matched::NUMERIC / sjr.features_total::NUMERIC) * 100
            ELSE 0
        END AS calculated_match_percentage,
        CASE
            WHEN sjr.features_matched > 0 THEN
                sjr.features_total::NUMERIC / sjr.features_matched::NUMERIC
            ELSE NULL
        END AS features_per_match
    FROM spatial_join_results sjr
),
boundary_forecast_join_analysis AS (
    -- Second CTE: Analyze joins between boundaries and forecasts
    SELECT
        sjbm.join_id,
        sjbm.join_type,
        sjbm.match_percentage,
        sjbm.calculated_match_percentage,
        sb.feature_type,
        sb.feature_name,
        sb.feature_identifier,
        gf.parameter_name,
        gf.forecast_time,
        sjbm.features_matched,
        sjbm.features_total,
        sjbm.features_per_match,
        -- Spatial relationship metrics
        CASE
            WHEN sb.boundary_geom IS NOT NULL AND gf.grid_cell_geom IS NOT NULL THEN
                ST_DISTANCE(sb.boundary_geom, gf.grid_cell_geom)
            ELSE NULL
        END AS spatial_distance,
        CASE
            WHEN sb.boundary_geom IS NOT NULL AND gf.grid_cell_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(gf.grid_cell_geom, sb.boundary_geom) THEN 'Within'
                    WHEN ST_INTERSECTS(gf.grid_cell_geom, sb.boundary_geom) THEN 'Intersects'
                    ELSE 'Near'
                END
            ELSE NULL
        END AS spatial_relationship
    FROM spatial_join_base_metrics sjbm
    LEFT JOIN shapefile_boundaries sb ON sjbm.boundary_id = sb.boundary_id
    LEFT JOIN grib2_forecasts gf ON sjbm.forecast_id = gf.forecast_id
),
join_type_performance AS (
    -- Third CTE: Performance by join type
    SELECT
        bfja.join_type,
        bfja.feature_type,
        COUNT(*) AS join_count,
        AVG(bfja.match_percentage) AS avg_match_percentage,
        AVG(bfja.features_matched) AS avg_features_matched,
        AVG(bfja.features_total) AS avg_features_total,
        AVG(bfja.features_per_match) AS avg_features_per_match,
        COUNT(CASE WHEN bfja.match_percentage > 80 THEN 1 END) AS high_match_joins,
        COUNT(CASE WHEN bfja.match_percentage < 20 THEN 1 END) AS low_match_joins,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY bfja.match_percentage) AS median_match_percentage
    FROM boundary_forecast_join_analysis bfja
    GROUP BY bfja.join_type, bfja.feature_type
),
spatial_relationship_analysis AS (
    -- Fourth CTE: Analyze spatial relationships
    SELECT
        bfja.join_id,
        bfja.join_type,
        bfja.feature_type,
        bfja.parameter_name,
        bfja.match_percentage,
        bfja.spatial_distance,
        bfja.spatial_relationship,
        -- Window functions for spatial analysis
        AVG(bfja.match_percentage) OVER (
            PARTITION BY bfja.spatial_relationship
        ) AS avg_match_by_relationship,
        COUNT(*) OVER (
            PARTITION BY bfja.spatial_relationship
        ) AS count_by_relationship,
        PERCENT_RANK() OVER (
            PARTITION BY bfja.join_type
            ORDER BY bfja.match_percentage DESC
        ) AS match_percentile
    FROM boundary_forecast_join_analysis bfja
    WHERE bfja.spatial_relationship IS NOT NULL
),
join_optimization_scoring AS (
    -- Fifth CTE: Calculate optimization scores
    SELECT
        sra.join_id,
        sra.join_type,
        sra.feature_type,
        sra.parameter_name,
        sra.match_percentage,
        sra.spatial_distance,
        sra.spatial_relationship,
        sra.avg_match_by_relationship,
        sra.count_by_relationship,
        ROUND(CAST(sra.match_percentile * 100 AS NUMERIC), 2) AS match_percentile,
        -- Optimization score (higher is better)
        (
            -- Match percentage component (40% weight)
            (sra.match_percentage / 100.0 * 40) +
            -- Relationship quality component (30% weight)
            (CASE
                WHEN sra.spatial_relationship = 'Within' THEN 30
                WHEN sra.spatial_relationship = 'Intersects' THEN 20
                ELSE 10
            END) +
            -- Distance component (30% weight) - closer is better
            (CASE
                WHEN sra.spatial_distance IS NOT NULL THEN
                    GREATEST(0, 30 - (sra.spatial_distance / 1000.0))
                ELSE 15
            END)
        ) AS optimization_score
    FROM spatial_relationship_analysis sra
),
final_join_optimization AS (
    -- Sixth CTE: Final optimization analysis
    SELECT
        jos.join_id,
        jos.join_type,
        jos.feature_type,
        jos.parameter_name,
        jos.match_percentage,
        ROUND(CAST(jos.spatial_distance AS NUMERIC), 2) AS spatial_distance,
        jos.spatial_relationship,
        ROUND(CAST(jos.optimization_score AS NUMERIC), 2) AS optimization_score,
        jos.match_percentile,
        -- Optimization recommendations
        CASE
            WHEN jos.match_percentage < 50 THEN 'Low Match - Consider Different Join Type'
            WHEN jos.spatial_distance > 10000 THEN 'High Distance - Check Spatial Index'
            WHEN jos.optimization_score < 50 THEN 'Poor Optimization - Review Join Strategy'
            ELSE 'Well Optimized'
        END AS optimization_recommendation,
        -- Rankings
        ROW_NUMBER() OVER (
            ORDER BY jos.optimization_score DESC
        ) AS optimization_rank,
        NTILE(5) OVER (
            ORDER BY jos.optimization_score DESC
        ) AS optimization_quintile
    FROM join_optimization_scoring jos
)
SELECT
    join_id,
    join_type,
    feature_type,
    parameter_name,
    match_percentage,
    spatial_distance,
    spatial_relationship,
    optimization_score,
    match_percentile,
    optimization_recommendation,
    optimization_rank,
    optimization_quintile
FROM final_join_optimization
ORDER BY optimization_score DESC
LIMIT 200;
```

---

## Query 5: Weather Station Network Coverage Analysis with Spatial Gap Detection and Coverage Optimization {#query-5}

**Use Case:** **Supply Chain and Fleet Management - Station Coverage Gap Analysis for Route Planning**

**Description:** Enterprise-level weather station network analysis identifying coverage gaps, station density metrics, spatial interpolation opportunities, and network optimization recommendations. Implements production patterns for analyzing observation network coverage.

**Business Value:** Map showing gaps in weather station coverage along routes with coverage density metrics. Fleet management companies can identify areas where additional monitoring may be needed.

**Purpose:** Identifies areas where additional weather monitoring may be needed to ensure adequate coverage for logistics operations.

**Complexity:** Multiple CTEs (8+ levels), spatial coverage analysis, gap detection algorithms, density calculations, interpolation analysis, window functions, spatial operations

```sql
WITH station_coverage_base AS (
    -- First CTE: Base station coverage metrics
    SELECT
        ws.station_id,
        ws.station_name,
        ws.station_latitude,
        ws.station_longitude,
        ws.station_geom,
        ws.state_code,
        ws.county_name,
        ws.cwa_code,
        ws.station_type,
        ws.active_status,
        ws.elevation_meters,
        -- Count recent observations
        (
            SELECT COUNT(*)
            FROM weather_observations wo
            WHERE wo.station_id = ws.station_id
                AND wo.observation_time >= CURRENT_TIMESTAMP - INTERVAL '7 days'
        ) AS recent_observations_count,
        -- Latest observation time
        (
            SELECT MAX(wo.observation_time)
            FROM weather_observations wo
            WHERE wo.station_id = ws.station_id
        ) AS latest_observation_time
    FROM weather_stations ws
    WHERE ws.active_status = TRUE
),
station_density_analysis AS (
    -- Second CTE: Calculate station density metrics
    SELECT
        scb.station_id,
        scb.station_name,
        scb.station_latitude,
        scb.station_longitude,
        scb.station_geom,
        scb.state_code,
        scb.cwa_code,
        scb.recent_observations_count,
        scb.latest_observation_time,
        -- Count nearby stations within 50km
        (
            SELECT COUNT(*)
            FROM station_coverage_base scb2
            WHERE scb2.station_id != scb.station_id
                AND scb2.station_geom IS NOT NULL
                AND scb.station_geom IS NOT NULL
                AND ST_DISTANCE(scb.station_geom, scb2.station_geom) < 50000
        ) AS nearby_stations_50km,
        -- Count nearby stations within 100km
        (
            SELECT COUNT(*)
            FROM station_coverage_base scb2
            WHERE scb2.station_id != scb.station_id
                AND scb2.station_geom IS NOT NULL
                AND scb.station_geom IS NOT NULL
                AND ST_DISTANCE(scb.station_geom, scb2.station_geom) < 100000
        ) AS nearby_stations_100km,
        -- Minimum distance to nearest station
        (
            SELECT MIN(ST_DISTANCE(scb.station_geom, scb2.station_geom))
            FROM station_coverage_base scb2
            WHERE scb2.station_id != scb.station_id
                AND scb2.station_geom IS NOT NULL
                AND scb.station_geom IS NOT NULL
        ) AS min_distance_to_nearest_station
    FROM station_coverage_base scb
),
coverage_gap_analysis AS (
    -- Third CTE: Identify coverage gaps
    SELECT
        sda.station_id,
        sda.station_name,
        sda.station_latitude,
        sda.station_longitude,
        sda.state_code,
        sda.cwa_code,
        sda.recent_observations_count,
        sda.nearby_stations_50km,
        sda.nearby_stations_100km,
        ROUND(CAST(sda.min_distance_to_nearest_station AS NUMERIC), 2) AS min_distance_to_nearest_station,
        -- Coverage classification
        CASE
            WHEN sda.nearby_stations_50km >= 5 THEN 'High Density'
            WHEN sda.nearby_stations_50km >= 2 THEN 'Medium Density'
            WHEN sda.nearby_stations_50km >= 1 THEN 'Low Density'
            ELSE 'Isolated'
        END AS density_classification,
        -- Gap indicators
        CASE
            WHEN sda.min_distance_to_nearest_station > 100000 THEN 'Large Gap'
            WHEN sda.min_distance_to_nearest_station > 50000 THEN 'Medium Gap'
            WHEN sda.min_distance_to_nearest_station > 25000 THEN 'Small Gap'
            ELSE 'No Gap'
        END AS gap_classification
    FROM station_density_analysis sda
),
boundary_coverage_analysis AS (
    -- Fourth CTE: Analyze coverage by boundary
    SELECT
        cga.station_id,
        cga.station_name,
        cga.state_code,
        cga.cwa_code,
        cga.density_classification,
        cga.gap_classification,
        sb.boundary_id,
        sb.feature_type,
        sb.feature_name,
        -- Check if station is within boundary
        CASE
            WHEN sda.station_geom IS NOT NULL AND sb.boundary_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(sda.station_geom, sb.boundary_geom) THEN TRUE
                    ELSE FALSE
                END
            ELSE NULL
        END AS is_within_boundary,
        -- Count stations in same boundary
        (
            SELECT COUNT(*)
            FROM station_coverage_base scb2
            WHERE scb2.station_geom IS NOT NULL
                AND sb.boundary_geom IS NOT NULL
                AND ST_WITHIN(scb2.station_geom, sb.boundary_geom)
        ) AS stations_in_boundary
    FROM coverage_gap_analysis cga
    INNER JOIN station_density_analysis sda ON cga.station_id = sda.station_id
    LEFT JOIN shapefile_boundaries sb ON (
        sb.feature_type = 'CWA'
        AND sda.station_geom IS NOT NULL
        AND sb.boundary_geom IS NOT NULL
        AND ST_DISTANCE(sda.station_geom, sb.boundary_geom) < 100000
    )
),
boundary_coverage_summary AS (
    -- Fifth CTE: Summarize coverage by boundary
    SELECT
        bca.boundary_id,
        bca.feature_type,
        bca.feature_name,
        COUNT(DISTINCT bca.station_id) AS station_count,
        COUNT(CASE WHEN bca.is_within_boundary = TRUE THEN 1 END) AS stations_within,
        COUNT(CASE WHEN bca.gap_classification = 'Large Gap' THEN 1 END) AS large_gap_stations,
        COUNT(CASE WHEN bca.gap_classification = 'No Gap' THEN 1 END) AS no_gap_stations,
        AVG(CASE WHEN bca.is_within_boundary = TRUE THEN 1 ELSE 0 END) * 100 AS coverage_percentage,
        -- Window functions for comparison
        AVG(bca.stations_in_boundary) OVER (
            PARTITION BY bca.feature_type
        ) AS avg_stations_per_boundary_type
    FROM boundary_coverage_analysis bca
    GROUP BY
        bca.boundary_id,
        bca.feature_type,
        bca.feature_name,
        bca.stations_in_boundary
),
interpolation_opportunity_analysis AS (
    -- Sixth CTE: Identify interpolation opportunities
    SELECT
        cga.station_id,
        cga.station_name,
        cga.state_code,
        cga.cwa_code,
        cga.density_classification,
        cga.gap_classification,
        cga.min_distance_to_nearest_station,
        -- Count forecast grid cells near station
        (
            SELECT COUNT(*)
            FROM grib2_forecasts gf
            WHERE gf.grid_cell_geom IS NOT NULL
                AND cga.station_geom IS NOT NULL
                AND ST_DISTANCE(gf.grid_cell_geom, cga.station_geom) < 25000
        ) AS nearby_forecast_cells,
        -- Interpolation quality score
        CASE
            WHEN cga.nearby_stations_50km >= 3 AND cga.min_distance_to_nearest_station < 25000 THEN 'Excellent'
            WHEN cga.nearby_stations_50km >= 2 AND cga.min_distance_to_nearest_station < 50000 THEN 'Good'
            WHEN cga.nearby_stations_50km >= 1 THEN 'Fair'
            ELSE 'Poor'
        END AS interpolation_quality
    FROM coverage_gap_analysis cga
    INNER JOIN station_density_analysis sda ON cga.station_id = sda.station_id
    WHERE sda.station_geom IS NOT NULL
),
final_coverage_report AS (
    -- Seventh CTE: Final coverage report
    SELECT
        ioa.station_id,
        ioa.station_name,
        ioa.state_code,
        ioa.cwa_code,
        ioa.density_classification,
        ioa.gap_classification,
        ioa.min_distance_to_nearest_station,
        ioa.nearby_forecast_cells,
        ioa.interpolation_quality,
        -- Coverage recommendations
        CASE
            WHEN ioa.gap_classification = 'Large Gap' THEN 'Add Station Recommended'
            WHEN ioa.interpolation_quality = 'Poor' THEN 'Improve Station Density'
            WHEN ioa.nearby_forecast_cells = 0 THEN 'No Forecast Coverage'
            ELSE 'Adequate Coverage'
        END AS coverage_recommendation,
        -- Rankings
        ROW_NUMBER() OVER (
            ORDER BY ioa.min_distance_to_nearest_station DESC
        ) AS isolation_rank,
        PERCENT_RANK() OVER (
            ORDER BY ioa.nearby_forecast_cells DESC
        ) AS forecast_coverage_percentile
    FROM interpolation_opportunity_analysis ioa
)
SELECT
    station_id,
    station_name,
    state_code,
    cwa_code,
    density_classification,
    gap_classification,
    min_distance_to_nearest_station,
    nearby_forecast_cells,
    interpolation_quality,
    coverage_recommendation,
    isolation_rank,
    ROUND(CAST(forecast_coverage_percentile * 100 AS NUMERIC), 2) AS forecast_coverage_percentile
FROM final_coverage_report
ORDER BY isolation_rank
LIMIT 200;
```

---

## Query 6: Forecast Accuracy Trend Analysis with Temporal Error Pattern Detection {#query-6}

**Use Case:** **Forensic Meteorology - Historical Forecast Accuracy Assessment for Legal Cases**

**Description:** Enterprise-level forecast accuracy trend analysis identifying temporal error patterns, accuracy degradation over time, seasonal variations, and forecast model performance trends. Implements production patterns for monitoring forecast model accuracy.

**Business Value:** Provides quantitative evidence of forecast reliability for legal proceedings and insurance claim validation.

**Purpose:** Trend analysis showing forecast accuracy over time with error pattern detection. Provides evidence of forecast reliability for insurance claim disputes and legal cases.

**Business Value:** Provides quantitative evidence of forecast reliability for legal proceedings and insurance claim validation.

**Complexity:** Multiple CTEs (7+ levels), temporal trend analysis, error pattern detection, seasonal analysis, window functions with multiple frame clauses, time-series decomposition

```sql
WITH forecast_observation_pairs AS (
    -- First CTE: Match forecasts with observations
    SELECT
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        DATE_TRUNC('hour', gf.forecast_time) AS forecast_hour,
        DATE_TRUNC('day', gf.forecast_time) AS forecast_date,
        EXTRACT(HOUR FROM gf.forecast_time) AS hour_of_day,
        EXTRACT(DOW FROM gf.forecast_time) AS day_of_week,
        EXTRACT(MONTH FROM gf.forecast_time) AS month_of_year,
        gf.parameter_value AS forecast_value,
        wo.observation_id,
        wo.observation_time,
        CASE
            WHEN gf.parameter_name = 'Temperature' THEN wo.temperature
            WHEN gf.parameter_name = 'Precipitation' THEN COALESCE(wo.precipitation_amount, 0)
            WHEN gf.parameter_name = 'WindSpeed' THEN wo.wind_speed
            ELSE NULL
        END AS observation_value,
        ABS(gf.parameter_value - CASE
            WHEN gf.parameter_name = 'Temperature' THEN wo.temperature
            WHEN gf.parameter_name = 'Precipitation' THEN COALESCE(wo.precipitation_amount, 0)
            WHEN gf.parameter_name = 'WindSpeed' THEN wo.wind_speed
            ELSE NULL
        END) AS absolute_error
    FROM grib2_forecasts gf
    INNER JOIN weather_observations wo ON (
        wo.observation_time BETWEEN gf.forecast_time - INTERVAL '1 hour' AND gf.forecast_time + INTERVAL '1 hour'
        AND ST_DISTANCE(gf.grid_cell_geom, wo.station_geom) < 25000
    )
    WHERE gf.transformation_status = 'Success'
        AND wo.observation_value IS NOT NULL
),
temporal_error_aggregation AS (
    -- Second CTE: Aggregate errors by time periods
    SELECT
        fop.forecast_hour,
        fop.forecast_date,
        fop.hour_of_day,
        fop.day_of_week,
        fop.month_of_year,
        fop.parameter_name,
        COUNT(*) AS forecast_count,
        AVG(fop.absolute_error) AS avg_absolute_error,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fop.absolute_error) AS median_absolute_error,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY fop.absolute_error) AS q1_absolute_error,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY fop.absolute_error) AS q3_absolute_error,
        STDDEV(fop.absolute_error) AS stddev_absolute_error,
        MAX(fop.absolute_error) AS max_absolute_error,
        MIN(fop.absolute_error) AS min_absolute_error
    FROM forecast_observation_pairs fop
    GROUP BY
        fop.forecast_hour,
        fop.forecast_date,
        fop.hour_of_day,
        fop.day_of_week,
        fop.month_of_year,
        fop.parameter_name
),
trend_analysis AS (
    -- Third CTE: Trend analysis with window functions
    SELECT
        tea.forecast_hour,
        tea.forecast_date,
        tea.hour_of_day,
        tea.day_of_week,
        tea.month_of_year,
        tea.parameter_name,
        tea.forecast_count,
        ROUND(CAST(tea.avg_absolute_error AS NUMERIC), 2) AS avg_absolute_error,
        ROUND(CAST(tea.median_absolute_error AS NUMERIC), 2) AS median_absolute_error,
        ROUND(CAST(tea.stddev_absolute_error AS NUMERIC), 2) AS stddev_absolute_error,
        -- Moving averages for trend detection
        AVG(tea.avg_absolute_error) OVER (
            PARTITION BY tea.parameter_name
            ORDER BY tea.forecast_hour
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS moving_avg_error_24h,
        AVG(tea.avg_absolute_error) OVER (
            PARTITION BY tea.parameter_name
            ORDER BY tea.forecast_hour
            ROWS BETWEEN 167 PRECEDING AND CURRENT ROW
        ) AS moving_avg_error_168h,
        -- Lag/Lead for trend direction
        LAG(tea.avg_absolute_error, 1) OVER (
            PARTITION BY tea.parameter_name
            ORDER BY tea.forecast_hour
        ) AS prev_avg_error,
        LEAD(tea.avg_absolute_error, 1) OVER (
            PARTITION BY tea.parameter_name
            ORDER BY tea.forecast_hour
        ) AS next_avg_error,
        -- Cumulative error
        SUM(tea.avg_absolute_error) OVER (
            PARTITION BY tea.parameter_name
            ORDER BY tea.forecast_hour
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_error
    FROM temporal_error_aggregation tea
),
error_pattern_detection AS (
    -- Fourth CTE: Detect error patterns
    SELECT
        ta.forecast_hour,
        ta.forecast_date,
        ta.hour_of_day,
        ta.day_of_week,
        ta.month_of_year,
        ta.parameter_name,
        ta.forecast_count,
        ta.avg_absolute_error,
        ta.median_absolute_error,
        ta.stddev_absolute_error,
        ROUND(CAST(ta.moving_avg_error_24h AS NUMERIC), 2) AS moving_avg_error_24h,
        ROUND(CAST(ta.moving_avg_error_168h AS NUMERIC), 2) AS moving_avg_error_168h,
        ROUND(CAST(ta.prev_avg_error AS NUMERIC), 2) AS prev_avg_error,
        -- Error trend direction
        CASE
            WHEN ta.prev_avg_error IS NOT NULL THEN
                CASE
                    WHEN ta.avg_absolute_error > ta.prev_avg_error * 1.1 THEN 'Increasing'
                    WHEN ta.avg_absolute_error < ta.prev_avg_error * 0.9 THEN 'Decreasing'
                    ELSE 'Stable'
                END
            ELSE NULL
        END AS error_trend,
        -- Seasonal pattern detection
        CASE
            WHEN ta.month_of_year IN (12, 1, 2) THEN 'Winter'
            WHEN ta.month_of_year IN (3, 4, 5) THEN 'Spring'
            WHEN ta.month_of_year IN (6, 7, 8) THEN 'Summer'
            ELSE 'Fall'
        END AS season,
        -- Time of day pattern
        CASE
            WHEN ta.hour_of_day BETWEEN 6 AND 11 THEN 'Morning'
            WHEN ta.hour_of_day BETWEEN 12 AND 17 THEN 'Afternoon'
            WHEN ta.hour_of_day BETWEEN 18 AND 23 THEN 'Evening'
            ELSE 'Night'
        END AS time_of_day
    FROM trend_analysis ta
),
seasonal_error_analysis AS (
    -- Fifth CTE: Seasonal error analysis
    SELECT
        epd.forecast_hour,
        epd.forecast_date,
        epd.parameter_name,
        epd.avg_absolute_error,
        epd.error_trend,
        epd.season,
        epd.time_of_day,
        -- Seasonal averages
        AVG(epd.avg_absolute_error) OVER (
            PARTITION BY epd.parameter_name, epd.season
        ) AS seasonal_avg_error,
        AVG(epd.avg_absolute_error) OVER (
            PARTITION BY epd.parameter_name, epd.time_of_day
        ) AS time_of_day_avg_error,
        -- Percentile rankings
        PERCENT_RANK() OVER (
            PARTITION BY epd.parameter_name
            ORDER BY epd.avg_absolute_error DESC
        ) AS error_percentile,
        NTILE(5) OVER (
            PARTITION BY epd.parameter_name, epd.season
            ORDER BY epd.avg_absolute_error DESC
        ) AS seasonal_error_quintile
    FROM error_pattern_detection epd
),
accuracy_classification AS (
    -- Sixth CTE: Classify accuracy levels
    SELECT
        sea.forecast_hour,
        sea.forecast_date,
        sea.parameter_name,
        sea.avg_absolute_error,
        sea.error_trend,
        sea.season,
        sea.time_of_day,
        ROUND(CAST(sea.seasonal_avg_error AS NUMERIC), 2) AS seasonal_avg_error,
        ROUND(CAST(sea.time_of_day_avg_error AS NUMERIC), 2) AS time_of_day_avg_error,
        ROUND(CAST(sea.error_percentile * 100 AS NUMERIC), 2) AS error_percentile,
        sea.seasonal_error_quintile,
        -- Accuracy classification
        CASE
            WHEN sea.avg_absolute_error <= sea.seasonal_avg_error * 0.8 THEN 'Excellent'
            WHEN sea.avg_absolute_error <= sea.seasonal_avg_error THEN 'Good'
            WHEN sea.avg_absolute_error <= sea.seasonal_avg_error * 1.2 THEN 'Fair'
            ELSE 'Poor'
        END AS accuracy_classification
    FROM seasonal_error_analysis sea
),
final_accuracy_trends AS (
    -- Seventh CTE: Final trend analysis
    SELECT
        ac.forecast_hour,
        ac.forecast_date,
        ac.parameter_name,
        ac.avg_absolute_error,
        ac.error_trend,
        ac.season,
        ac.time_of_day,
        ac.seasonal_avg_error,
        ac.time_of_day_avg_error,
        ac.error_percentile,
        ac.accuracy_classification,
        -- Trend recommendations
        CASE
            WHEN ac.error_trend = 'Increasing' AND ac.accuracy_classification IN ('Fair', 'Poor') THEN 'Review Model Parameters'
            WHEN ac.error_trend = 'Decreasing' THEN 'Model Improving'
            WHEN ac.accuracy_classification = 'Poor' THEN 'Investigate Root Cause'
            ELSE 'Monitor'
        END AS recommendation
    FROM accuracy_classification ac
)
SELECT
    forecast_hour,
    forecast_date,
    parameter_name,
    avg_absolute_error,
    error_trend,
    season,
    time_of_day,
    seasonal_avg_error,
    time_of_day_avg_error,
    error_percentile,
    accuracy_classification,
    recommendation
FROM final_accuracy_trends
WHERE forecast_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY forecast_hour DESC, parameter_name
LIMIT 500;
```

---

## Query 7: Boundary Forecast Aggregation Analysis with Multi-Level Spatial Summarization {#query-7}

**Use Case:** **Custom Weather Impact Modeling - Aggregated Forecasts by Boundary for Retail Operations**

**Description:** Enterprise-level boundary forecast aggregation analysis with multi-level spatial summarization, hierarchical aggregations, and comprehensive statistical summaries. Implements production patterns for aggregating gridded forecasts to geographic boundaries.

**Business Value:** Summary forecasts aggregated by client-defined boundaries (counties, zones). Retail chains can get aggregated temperature forecasts for each store location's county.

**Purpose:** Provides simplified forecasts for specific geographic areas enabling location-based business decisions.

**Complexity:** Multiple CTEs (7+ levels), spatial aggregations, hierarchical summarization, statistical calculations, window functions, UNION operations

```sql
WITH forecast_boundary_matching AS (
    -- First CTE: Match forecasts to boundaries
    SELECT
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        gf.parameter_value,
        gf.grid_cell_geom,
        sb.boundary_id,
        sb.feature_type,
        sb.feature_name,
        sb.feature_identifier,
        sb.boundary_geom,
        CASE
            WHEN sb.boundary_geom IS NOT NULL AND gf.grid_cell_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(gf.grid_cell_geom, sb.boundary_geom) THEN TRUE
                    ELSE FALSE
                END
            ELSE NULL
        END AS is_within_boundary
    FROM grib2_forecasts gf
    CROSS JOIN shapefile_boundaries sb
    WHERE gf.transformation_status = 'Success'
        AND sb.boundary_geom IS NOT NULL
        AND gf.grid_cell_geom IS NOT NULL
        AND ST_DISTANCE(gf.grid_cell_geom, sb.boundary_geom) < 50000
),
boundary_forecast_aggregation AS (
    -- Second CTE: Aggregate forecasts by boundary
    SELECT
        fbm.boundary_id,
        fbm.feature_type,
        fbm.feature_name,
        fbm.feature_identifier,
        fbm.parameter_name,
        fbm.forecast_time,
        COUNT(DISTINCT fbm.forecast_id) AS grid_cells_count,
        COUNT(CASE WHEN fbm.is_within_boundary = TRUE THEN 1 END) AS cells_within_boundary,
        AVG(fbm.parameter_value) AS avg_value,
        MIN(fbm.parameter_value) AS min_value,
        MAX(fbm.parameter_value) AS max_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fbm.parameter_value) AS median_value,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY fbm.parameter_value) AS q1_value,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY fbm.parameter_value) AS q3_value,
        STDDEV(fbm.parameter_value) AS stddev_value,
        VARIANCE(fbm.parameter_value) AS variance_value
    FROM forecast_boundary_matching fbm
    WHERE fbm.is_within_boundary = TRUE
    GROUP BY
        fbm.boundary_id,
        fbm.feature_type,
        fbm.feature_name,
        fbm.feature_identifier,
        fbm.parameter_name,
        fbm.forecast_time
),
feature_type_aggregation AS (
    -- Third CTE: Aggregate by feature type
    SELECT
        bfa.feature_type,
        bfa.parameter_name,
        bfa.forecast_time,
        COUNT(DISTINCT bfa.boundary_id) AS boundary_count,
        SUM(bfa.grid_cells_count) AS total_grid_cells,
        AVG(bfa.avg_value) AS feature_type_avg_value,
        AVG(bfa.min_value) AS feature_type_min_value,
        AVG(bfa.max_value) AS feature_type_max_value,
        AVG(bfa.median_value) AS feature_type_median_value,
        AVG(bfa.stddev_value) AS feature_type_stddev_value
    FROM boundary_forecast_aggregation bfa
    GROUP BY
        bfa.feature_type,
        bfa.parameter_name,
        bfa.forecast_time
),
temporal_aggregation AS (
    -- Fourth CTE: Temporal aggregation
    SELECT
        bfa.boundary_id,
        bfa.feature_type,
        bfa.feature_name,
        bfa.parameter_name,
        DATE_TRUNC('hour', bfa.forecast_time) AS forecast_hour,
        DATE_TRUNC('day', bfa.forecast_time) AS forecast_date,
        COUNT(*) AS forecast_count,
        AVG(bfa.avg_value) AS hourly_avg_value,
        AVG(bfa.min_value) AS hourly_min_value,
        AVG(bfa.max_value) AS hourly_max_value,
        AVG(bfa.median_value) AS hourly_median_value,
        -- Window functions for temporal trends
        AVG(bfa.avg_value) OVER (
            PARTITION BY bfa.boundary_id, bfa.parameter_name
            ORDER BY DATE_TRUNC('hour', bfa.forecast_time)
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) AS moving_avg_6h,
        LAG(bfa.avg_value, 1) OVER (
            PARTITION BY bfa.boundary_id, bfa.parameter_name
            ORDER BY DATE_TRUNC('hour', bfa.forecast_time)
        ) AS prev_hour_avg
    FROM boundary_forecast_aggregation bfa
    GROUP BY
        bfa.boundary_id,
        bfa.feature_type,
        bfa.feature_name,
        bfa.parameter_name,
        DATE_TRUNC('hour', bfa.forecast_time),
        DATE_TRUNC('day', bfa.forecast_time),
        bfa.avg_value
),
statistical_summary AS (
    -- Fifth CTE: Statistical summary
    SELECT
        ta.boundary_id,
        ta.feature_type,
        ta.feature_name,
        ta.parameter_name,
        ta.forecast_hour,
        ta.forecast_date,
        ta.forecast_count,
        ROUND(CAST(ta.hourly_avg_value AS NUMERIC), 2) AS hourly_avg_value,
        ROUND(CAST(ta.hourly_min_value AS NUMERIC), 2) AS hourly_min_value,
        ROUND(CAST(ta.hourly_max_value AS NUMERIC), 2) AS hourly_max_value,
        ROUND(CAST(ta.hourly_median_value AS NUMERIC), 2) AS hourly_median_value,
        ROUND(CAST(ta.moving_avg_6h AS NUMERIC), 2) AS moving_avg_6h,
        ROUND(CAST(ta.prev_hour_avg AS NUMERIC), 2) AS prev_hour_avg,
        -- Value range
        ta.hourly_max_value - ta.hourly_min_value AS value_range,
        -- Coefficient of variation
        CASE
            WHEN ta.hourly_avg_value != 0 THEN
                ABS(ta.hourly_max_value - ta.hourly_min_value) / ABS(ta.hourly_avg_value)
            ELSE NULL
        END AS coefficient_of_variation,
        -- Trend indicator
        CASE
            WHEN ta.prev_hour_avg IS NOT NULL THEN
                CASE
                    WHEN ta.hourly_avg_value > ta.prev_hour_avg * 1.05 THEN 'Increasing'
                    WHEN ta.hourly_avg_value < ta.prev_hour_avg * 0.95 THEN 'Decreasing'
                    ELSE 'Stable'
                END
            ELSE NULL
        END AS trend_indicator
    FROM temporal_aggregation ta
),
final_aggregation_report AS (
    -- Sixth CTE: Final aggregation report
    SELECT
        ss.boundary_id,
        ss.feature_type,
        ss.feature_name,
        ss.parameter_name,
        ss.forecast_hour,
        ss.forecast_date,
        ss.forecast_count,
        ss.hourly_avg_value,
        ss.hourly_min_value,
        ss.hourly_max_value,
        ss.hourly_median_value,
        ss.moving_avg_6h,
        ROUND(CAST(ss.value_range AS NUMERIC), 2) AS value_range,
        ROUND(CAST(ss.coefficient_of_variation AS NUMERIC), 4) AS coefficient_of_variation,
        ss.trend_indicator,
        -- Percentile rankings
        PERCENT_RANK() OVER (
            PARTITION BY ss.feature_type, ss.parameter_name
            ORDER BY ss.hourly_avg_value DESC
        ) AS value_percentile,
        NTILE(5) OVER (
            PARTITION BY ss.feature_type
            ORDER BY ss.hourly_avg_value DESC
        ) AS value_quintile
    FROM statistical_summary ss
)
SELECT
    boundary_id,
    feature_type,
    feature_name,
    parameter_name,
    forecast_hour,
    forecast_date,
    forecast_count,
    hourly_avg_value,
    hourly_min_value,
    hourly_max_value,
    hourly_median_value,
    moving_avg_6h,
    value_range,
    coefficient_of_variation,
    trend_indicator,
    ROUND(CAST(value_percentile * 100 AS NUMERIC), 2) AS value_percentile,
    value_quintile
FROM final_aggregation_report
WHERE forecast_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY forecast_hour DESC, boundary_id, parameter_name
LIMIT 500;
```

---

## Query 8: Observation Forecast Validation Analysis with Accuracy Scoring {#query-8}

**Use Case:** **Forensic Meteorology - Forecast vs. Observation Validation for Legal Evidence**

**Description:** Enterprise-level observation-forecast validation analysis comparing actual observations with forecasts, calculating accuracy scores, identifying systematic biases, and providing validation metrics. Implements production patterns for forecast validation and model evaluation.

**Business Value:** Provides evidence of forecast accuracy for legal proceedings and insurance claim validation.

**Purpose:** Validation report comparing forecasts to actual observations with accuracy scoring. Legal cases require documentation that forecasts were accurate at specific times/locations.

**Business Value:** Provides evidence of forecast accuracy for legal proceedings and insurance claim validation.

**Complexity:** Multiple CTEs (8+ levels), observation-forecast matching, accuracy calculations, bias detection, validation scoring, window functions, statistical analysis

```sql
WITH observation_forecast_matching AS (
    -- First CTE: Match observations with forecasts
    SELECT
        wo.observation_id,
        wo.station_id,
        wo.station_name,
        wo.observation_time,
        wo.station_geom,
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        gf.parameter_value AS forecast_value,
        CASE
            WHEN gf.parameter_name = 'Temperature' THEN wo.temperature
            WHEN gf.parameter_name = 'Precipitation' THEN COALESCE(wo.precipitation_amount, 0)
            WHEN gf.parameter_name = 'WindSpeed' THEN wo.wind_speed
            ELSE NULL
        END AS observation_value,
        -- Time difference
        EXTRACT(EPOCH FROM (wo.observation_time - gf.forecast_time)) / 3600 AS hours_difference,
        -- Spatial distance
        CASE
            WHEN wo.station_geom IS NOT NULL AND gf.grid_cell_geom IS NOT NULL THEN
                ST_DISTANCE(wo.station_geom, gf.grid_cell_geom)
            ELSE NULL
        END AS spatial_distance
    FROM weather_observations wo
    INNER JOIN grib2_forecasts gf ON (
        gf.parameter_name IN ('Temperature', 'Precipitation', 'WindSpeed')
        AND gf.forecast_time BETWEEN wo.observation_time - INTERVAL '2 hours' AND wo.observation_time + INTERVAL '2 hours'
        AND wo.station_geom IS NOT NULL
        AND gf.grid_cell_geom IS NOT NULL
        AND ST_DISTANCE(wo.station_geom, gf.grid_cell_geom) < 50000
    )
    WHERE wo.observation_time >= CURRENT_TIMESTAMP - INTERVAL '30 days'
),
validation_metrics AS (
    -- Second CTE: Calculate validation metrics
    SELECT
        ofm.observation_id,
        ofm.station_id,
        ofm.station_name,
        ofm.parameter_name,
        ofm.forecast_time,
        ofm.observation_time,
        ofm.forecast_value,
        ofm.observation_value,
        ofm.hours_difference,
        ROUND(CAST(ofm.spatial_distance AS NUMERIC), 2) AS spatial_distance,
        -- Error calculations
        ofm.forecast_value - ofm.observation_value AS error,
        ABS(ofm.forecast_value - ofm.observation_value) AS absolute_error,
        CASE
            WHEN ofm.observation_value != 0 THEN
                ABS((ofm.forecast_value - ofm.observation_value) / ofm.observation_value) * 100
            ELSE NULL
        END AS percentage_error,
        -- Squared error for RMSE calculation
        POWER(ofm.forecast_value - ofm.observation_value, 2) AS squared_error
    FROM observation_forecast_matching ofm
    WHERE ofm.observation_value IS NOT NULL
        AND ofm.forecast_value IS NOT NULL
),
station_validation_summary AS (
    -- Third CTE: Summarize by station
    SELECT
        vm.station_id,
        vm.station_name,
        vm.parameter_name,
        COUNT(*) AS validation_count,
        AVG(vm.error) AS mean_error,
        AVG(vm.absolute_error) AS mean_absolute_error,
        SQRT(AVG(vm.squared_error)) AS root_mean_squared_error,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY vm.absolute_error) AS median_absolute_error,
        STDDEV(vm.error) AS error_stddev,
        -- Bias indicators
        CASE
            WHEN AVG(vm.error) > 2 THEN 'Over-forecast Bias'
            WHEN AVG(vm.error) < -2 THEN 'Under-forecast Bias'
            ELSE 'No Significant Bias'
        END AS bias_indicator,
        -- Accuracy classification
        CASE
            WHEN AVG(vm.absolute_error) <= 2 THEN 'Excellent'
            WHEN AVG(vm.absolute_error) <= 5 THEN 'Good'
            WHEN AVG(vm.absolute_error) <= 10 THEN 'Fair'
            ELSE 'Poor'
        END AS accuracy_classification
    FROM validation_metrics vm
    GROUP BY
        vm.station_id,
        vm.station_name,
        vm.parameter_name
),
parameter_validation_summary AS (
    -- Fourth CTE: Summarize by parameter
    SELECT
        vm.parameter_name,
        COUNT(*) AS total_validations,
        COUNT(DISTINCT vm.station_id) AS unique_stations,
        AVG(vm.error) AS overall_mean_error,
        AVG(vm.absolute_error) AS overall_mean_absolute_error,
        SQRT(AVG(vm.squared_error)) AS overall_rmse,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY vm.absolute_error) AS overall_median_error,
        -- Window functions for comparison
        AVG(vm.absolute_error) OVER (
            PARTITION BY vm.parameter_name
            ORDER BY vm.forecast_time
            ROWS BETWEEN 99 PRECEDING AND CURRENT ROW
        ) AS moving_avg_error_100,
        PERCENT_RANK() OVER (
            ORDER BY AVG(vm.absolute_error) DESC
        ) AS error_percentile
    FROM validation_metrics vm
    GROUP BY vm.parameter_name, vm.forecast_time
),
temporal_validation_analysis AS (
    -- Fifth CTE: Temporal validation analysis
    SELECT
        vm.parameter_name,
        DATE_TRUNC('day', vm.forecast_time) AS forecast_date,
        COUNT(*) AS daily_validations,
        AVG(vm.absolute_error) AS daily_mean_absolute_error,
        AVG(vm.error) AS daily_mean_error,
        STDDEV(vm.error) AS daily_error_stddev,
        -- Lag for trend detection
        LAG(AVG(vm.absolute_error), 1) OVER (
            PARTITION BY vm.parameter_name
            ORDER BY DATE_TRUNC('day', vm.forecast_time)
        ) AS prev_day_mae
    FROM validation_metrics vm
    GROUP BY
        vm.parameter_name,
        DATE_TRUNC('day', vm.forecast_time)
),
validation_scoring AS (
    -- Sixth CTE: Calculate validation scores
    SELECT
        svs.station_id,
        svs.station_name,
        svs.parameter_name,
        svs.validation_count,
        ROUND(CAST(svs.mean_error AS NUMERIC), 2) AS mean_error,
        ROUND(CAST(svs.mean_absolute_error AS NUMERIC), 2) AS mean_absolute_error,
        ROUND(CAST(svs.root_mean_squared_error AS NUMERIC), 2) AS root_mean_squared_error,
        ROUND(CAST(svs.median_absolute_error AS NUMERIC), 2) AS median_absolute_error,
        ROUND(CAST(svs.error_stddev AS NUMERIC), 2) AS error_stddev,
        svs.bias_indicator,
        svs.accuracy_classification,
        -- Validation score (higher is better, normalized to 0-100)
        CASE
            WHEN svs.mean_absolute_error <= 2 THEN 100
            WHEN svs.mean_absolute_error <= 5 THEN 80
            WHEN svs.mean_absolute_error <= 10 THEN 60
            WHEN svs.mean_absolute_error <= 20 THEN 40
            ELSE 20
        END AS validation_score
    FROM station_validation_summary svs
),
final_validation_report AS (
    -- Seventh CTE: Final validation report
    SELECT
        vs.station_id,
        vs.station_name,
        vs.parameter_name,
        vs.validation_count,
        vs.mean_error,
        vs.mean_absolute_error,
        vs.root_mean_squared_error,
        vs.median_absolute_error,
        vs.error_stddev,
        vs.bias_indicator,
        vs.accuracy_classification,
        vs.validation_score,
        -- Rankings
        ROW_NUMBER() OVER (
            PARTITION BY vs.parameter_name
            ORDER BY vs.validation_score DESC
        ) AS accuracy_rank,
        PERCENT_RANK() OVER (
            PARTITION BY vs.parameter_name
            ORDER BY vs.mean_absolute_error ASC
        ) AS error_percentile,
        NTILE(5) OVER (
            PARTITION BY vs.parameter_name
            ORDER BY vs.validation_score DESC
        ) AS validation_quintile
    FROM validation_scoring vs
)
SELECT
    station_id,
    station_name,
    parameter_name,
    validation_count,
    mean_error,
    mean_absolute_error,
    root_mean_squared_error,
    median_absolute_error,
    error_stddev,
    bias_indicator,
    accuracy_classification,
    validation_score,
    accuracy_rank,
    ROUND(CAST(error_percentile * 100 AS NUMERIC), 2) AS error_percentile,
    validation_quintile
FROM final_validation_report
ORDER BY parameter_name, validation_score DESC
LIMIT 300;
```

---

## Query 9: Multi-Boundary Spatial Intersection Analysis with Overlap Detection {#query-9}

**Use Case:** **Custom Map Development - Boundary Overlap Detection for Real Estate Development**

**Description:** Enterprise-level multi-boundary spatial intersection analysis identifying overlapping boundaries, intersection areas, coverage gaps, and spatial relationships between different boundary types. Implements production patterns for analyzing complex geospatial boundary relationships.

**Business Value:** Analysis of overlapping boundaries (e.g., fire zones overlapping counties) with intersection metrics. Real estate developers can understand which fire zones overlap with property boundaries.

**Purpose:** Helps clients understand complex geographic relationships for property and risk assessment.

**Complexity:** Multiple CTEs (7+ levels), spatial intersection operations, overlap calculations, area computations, relationship detection, window functions

```sql
WITH boundary_pairs AS (
    -- First CTE: Create boundary pairs for intersection analysis
    SELECT
        sb1.boundary_id AS boundary1_id,
        sb1.feature_type AS boundary1_type,
        sb1.feature_name AS boundary1_name,
        sb1.boundary_geom AS boundary1_geom,
        sb2.boundary_id AS boundary2_id,
        sb2.feature_type AS boundary2_type,
        sb2.feature_name AS boundary2_name,
        sb2.boundary_geom AS boundary2_geom,
        -- Spatial relationships
        CASE
            WHEN sb1.boundary_geom IS NOT NULL AND sb2.boundary_geom IS NOT NULL THEN
                CASE
                    WHEN ST_WITHIN(sb1.boundary_geom, sb2.boundary_geom) THEN 'Boundary1 Within Boundary2'
                    WHEN ST_WITHIN(sb2.boundary_geom, sb1.boundary_geom) THEN 'Boundary2 Within Boundary1'
                    WHEN ST_INTERSECTS(sb1.boundary_geom, sb2.boundary_geom) THEN 'Intersects'
                    WHEN ST_TOUCHES(sb1.boundary_geom, sb2.boundary_geom) THEN 'Touches'
                    ELSE 'Disjoint'
                END
            ELSE NULL
        END AS spatial_relationship,
        -- Distance calculation
        CASE
            WHEN sb1.boundary_geom IS NOT NULL AND sb2.boundary_geom IS NOT NULL THEN
                ST_DISTANCE(sb1.boundary_geom, sb2.boundary_geom)
            ELSE NULL
        END AS distance_between_boundaries
    FROM shapefile_boundaries sb1
    CROSS JOIN shapefile_boundaries sb2
    WHERE sb1.boundary_id < sb2.boundary_id
        AND sb1.boundary_geom IS NOT NULL
        AND sb2.boundary_geom IS NOT NULL
        AND ST_DISTANCE(sb1.boundary_geom, sb2.boundary_geom) < 100000
),
intersection_analysis AS (
    -- Second CTE: Calculate intersection metrics
    SELECT
        bp.boundary1_id,
        bp.boundary1_type,
        bp.boundary1_name,
        bp.boundary2_id,
        bp.boundary2_type,
        bp.boundary2_name,
        bp.spatial_relationship,
        ROUND(CAST(bp.distance_between_boundaries AS NUMERIC), 2) AS distance_between_boundaries,
        -- Intersection area
        CASE
            WHEN bp.spatial_relationship IN ('Intersects', 'Boundary1 Within Boundary2', 'Boundary2 Within Boundary1') THEN
                ST_AREA(ST_INTERSECTION(bp.boundary1_geom, bp.boundary2_geom))
            ELSE NULL
        END AS intersection_area,
        -- Individual boundary areas
        ST_AREA(bp.boundary1_geom) AS boundary1_area,
        ST_AREA(bp.boundary2_geom) AS boundary2_area,
        -- Union area
        CASE
            WHEN bp.spatial_relationship IN ('Intersects', 'Boundary1 Within Boundary2', 'Boundary2 Within Boundary1') THEN
                ST_AREA(ST_UNION(bp.boundary1_geom, bp.boundary2_geom))
            ELSE NULL
        END AS union_area
    FROM boundary_pairs bp
),
overlap_metrics AS (
    -- Third CTE: Calculate overlap metrics
    SELECT
        ia.boundary1_id,
        ia.boundary1_type,
        ia.boundary1_name,
        ia.boundary2_id,
        ia.boundary2_type,
        ia.boundary2_name,
        ia.spatial_relationship,
        ia.distance_between_boundaries,
        ROUND(CAST(ia.intersection_area AS NUMERIC), 2) AS intersection_area,
        ROUND(CAST(ia.boundary1_area AS NUMERIC), 2) AS boundary1_area,
        ROUND(CAST(ia.boundary2_area AS NUMERIC), 2) AS boundary2_area,
        ROUND(CAST(ia.union_area AS NUMERIC), 2) AS union_area,
        -- Overlap percentages
        CASE
            WHEN ia.boundary1_area > 0 AND ia.intersection_area IS NOT NULL THEN
                (ia.intersection_area / ia.boundary1_area) * 100
            ELSE NULL
        END AS boundary1_overlap_percentage,
        CASE
            WHEN ia.boundary2_area > 0 AND ia.intersection_area IS NOT NULL THEN
                (ia.intersection_area / ia.boundary2_area) * 100
            ELSE NULL
        END AS boundary2_overlap_percentage,
        -- Jaccard similarity coefficient
        CASE
            WHEN ia.union_area > 0 AND ia.intersection_area IS NOT NULL THEN
                ia.intersection_area / ia.union_area
            ELSE NULL
        END AS jaccard_similarity
    FROM intersection_analysis ia
),
boundary_overlap_summary AS (
    -- Fourth CTE: Summarize overlaps by boundary
    SELECT
        om.boundary1_id,
        om.boundary1_type,
        om.boundary1_name,
        COUNT(*) AS total_intersections,
        COUNT(CASE WHEN om.spatial_relationship = 'Intersects' THEN 1 END) AS intersection_count,
        COUNT(CASE WHEN om.spatial_relationship = 'Boundary1 Within Boundary2' THEN 1 END) AS contained_count,
        COUNT(CASE WHEN om.spatial_relationship = 'Boundary2 Within Boundary1' THEN 1 END) AS containing_count,
        AVG(om.boundary1_overlap_percentage) AS avg_overlap_percentage,
        MAX(om.boundary1_overlap_percentage) AS max_overlap_percentage,
        SUM(om.intersection_area) AS total_intersection_area,
        AVG(om.jaccard_similarity) AS avg_jaccard_similarity
    FROM overlap_metrics om
    GROUP BY
        om.boundary1_id,
        om.boundary1_type,
        om.boundary1_name
),
feature_type_overlap_analysis AS (
    -- Fifth CTE: Analyze overlaps by feature type combinations
    SELECT
        om.boundary1_type,
        om.boundary2_type,
        COUNT(*) AS type_pair_count,
        AVG(om.intersection_area) AS avg_intersection_area,
        AVG(om.boundary1_overlap_percentage) AS avg_overlap_percentage,
        AVG(om.jaccard_similarity) AS avg_jaccard_similarity,
        COUNT(CASE WHEN om.spatial_relationship = 'Intersects' THEN 1 END) AS intersection_count,
        COUNT(CASE WHEN om.spatial_relationship IN ('Boundary1 Within Boundary2', 'Boundary2 Within Boundary1') THEN 1 END) AS containment_count
    FROM overlap_metrics om
    GROUP BY
        om.boundary1_type,
        om.boundary2_type
),
final_intersection_report AS (
    -- Sixth CTE: Final intersection report
    SELECT
        om.boundary1_id,
        om.boundary1_type,
        om.boundary1_name,
        om.boundary2_id,
        om.boundary2_type,
        om.boundary2_name,
        om.spatial_relationship,
        om.intersection_area,
        ROUND(CAST(om.boundary1_overlap_percentage AS NUMERIC), 2) AS boundary1_overlap_percentage,
        ROUND(CAST(om.boundary2_overlap_percentage AS NUMERIC), 2) AS boundary2_overlap_percentage,
        ROUND(CAST(om.jaccard_similarity AS NUMERIC), 4) AS jaccard_similarity,
        -- Overlap classification
        CASE
            WHEN om.jaccard_similarity > 0.8 THEN 'High Overlap'
            WHEN om.jaccard_similarity > 0.5 THEN 'Moderate Overlap'
            WHEN om.jaccard_similarity > 0.2 THEN 'Low Overlap'
            WHEN om.jaccard_similarity > 0 THEN 'Minimal Overlap'
            ELSE 'No Overlap'
        END AS overlap_classification,
        -- Rankings
        ROW_NUMBER() OVER (
            ORDER BY om.jaccard_similarity DESC NULLS LAST
        ) AS overlap_rank,
        PERCENT_RANK() OVER (
            ORDER BY om.intersection_area DESC NULLS LAST
        ) AS intersection_area_percentile
    FROM overlap_metrics om
    WHERE om.intersection_area IS NOT NULL
)
SELECT
    boundary1_id,
    boundary1_type,
    boundary1_name,
    boundary2_id,
    boundary2_type,
    boundary2_name,
    spatial_relationship,
    intersection_area,
    boundary1_overlap_percentage,
    boundary2_overlap_percentage,
    jaccard_similarity,
    overlap_classification,
    overlap_rank,
    ROUND(CAST(intersection_area_percentile * 100 AS NUMERIC), 2) AS intersection_area_percentile
FROM final_intersection_report
ORDER BY jaccard_similarity DESC NULLS LAST
LIMIT 200;
```

---

## Query 10: Parameter Forecast Distribution Analysis with Statistical Profiling {#query-10}

**Use Case:** **Physical Climate Risk Assessment - Statistical Weather Profiling for Insurance Underwriting**

**Description:** Enterprise-level parameter forecast distribution analysis with statistical profiling, distribution shape analysis, outlier detection, and distribution comparisons. Implements production patterns for statistical analysis of forecast distributions.

**Business Value:** Identifies normal vs. extreme weather patterns for risk assessment and insurance pricing.

**Purpose:** Statistical distribution analysis of forecast parameters with percentile rankings. Insurance companies need statistical profiles of weather parameters for underwriting decisions.

**Business Value:** Identifies normal vs. extreme weather patterns for risk assessment and insurance pricing.

**Complexity:** Multiple CTEs (6+ levels), statistical distribution analysis, percentile calculations, outlier detection, distribution comparisons, window functions

```sql
WITH parameter_distribution_base AS (
    -- First CTE: Base parameter distribution data
    SELECT
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        DATE_TRUNC('day', gf.forecast_time) AS forecast_date,
        gf.parameter_value,
        gf.grid_cell_latitude,
        gf.grid_cell_longitude
    FROM grib2_forecasts gf
    WHERE gf.transformation_status = 'Success'
        AND gf.parameter_value IS NOT NULL
),
parameter_statistics AS (
    -- Second CTE: Calculate statistical measures
    SELECT
        pdb.parameter_name,
        pdb.forecast_date,
        COUNT(*) AS forecast_count,
        AVG(pdb.parameter_value) AS mean_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pdb.parameter_value) AS median_value,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY pdb.parameter_value) AS q1_value,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY pdb.parameter_value) AS q3_value,
        PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY pdb.parameter_value) AS p10_value,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY pdb.parameter_value) AS p90_value,
        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY pdb.parameter_value) AS p5_value,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY pdb.parameter_value) AS p95_value,
        MIN(pdb.parameter_value) AS min_value,
        MAX(pdb.parameter_value) AS max_value,
        STDDEV(pdb.parameter_value) AS stddev_value,
        VARIANCE(pdb.parameter_value) AS variance_value
    FROM parameter_distribution_base pdb
    GROUP BY
        pdb.parameter_name,
        pdb.forecast_date
),
distribution_metrics AS (
    -- Third CTE: Calculate distribution metrics
    SELECT
        ps.parameter_name,
        ps.forecast_date,
        ps.forecast_count,
        ROUND(CAST(ps.mean_value AS NUMERIC), 2) AS mean_value,
        ROUND(CAST(ps.median_value AS NUMERIC), 2) AS median_value,
        ROUND(CAST(ps.q1_value AS NUMERIC), 2) AS q1_value,
        ROUND(CAST(ps.q3_value AS NUMERIC), 2) AS q3_value,
        ROUND(CAST(ps.p10_value AS NUMERIC), 2) AS p10_value,
        ROUND(CAST(ps.p90_value AS NUMERIC), 2) AS p90_value,
        ROUND(CAST(ps.p5_value AS NUMERIC), 2) AS p5_value,
        ROUND(CAST(ps.p95_value AS NUMERIC), 2) AS p95_value,
        ROUND(CAST(ps.min_value AS NUMERIC), 2) AS min_value,
        ROUND(CAST(ps.max_value AS NUMERIC), 2) AS max_value,
        ROUND(CAST(ps.stddev_value AS NUMERIC), 2) AS stddev_value,
        ROUND(CAST(ps.variance_value AS NUMERIC), 2) AS variance_value,
        -- Interquartile range
        ps.q3_value - ps.q1_value AS iqr,
        -- Range
        ps.max_value - ps.min_value AS value_range,
        -- Coefficient of variation
        CASE
            WHEN ps.mean_value != 0 THEN
                ps.stddev_value / ABS(ps.mean_value)
            ELSE NULL
        END AS coefficient_of_variation,
        -- Skewness indicator (simplified)
        CASE
            WHEN ps.mean_value > ps.median_value THEN 'Right Skewed'
            WHEN ps.mean_value < ps.median_value THEN 'Left Skewed'
            ELSE 'Symmetric'
        END AS skewness_indicator
    FROM parameter_statistics ps
),
outlier_detection AS (
    -- Fourth CTE: Detect outliers
    SELECT
        pdb.forecast_id,
        pdb.parameter_name,
        pdb.forecast_date,
        pdb.parameter_value,
        dm.mean_value,
        dm.median_value,
        dm.stddev_value,
        dm.q1_value,
        dm.q3_value,
        dm.iqr,
        dm.p5_value,
        dm.p95_value,
        -- Outlier detection using IQR method
        CASE
            WHEN pdb.parameter_value < dm.q1_value - 1.5 * dm.iqr OR
                 pdb.parameter_value > dm.q3_value + 1.5 * dm.iqr THEN TRUE
            ELSE FALSE
        END AS is_iqr_outlier,
        -- Outlier detection using percentile method
        CASE
            WHEN pdb.parameter_value < dm.p5_value OR
                 pdb.parameter_value > dm.p95_value THEN TRUE
            ELSE FALSE
        END AS is_percentile_outlier,
        -- Outlier detection using z-score (simplified)
        CASE
            WHEN dm.stddev_value > 0 THEN
                ABS((pdb.parameter_value - dm.mean_value) / dm.stddev_value) > 3
            ELSE FALSE
        END AS is_zscore_outlier
    FROM parameter_distribution_base pdb
    INNER JOIN distribution_metrics dm ON (
        pdb.parameter_name = dm.parameter_name
        AND pdb.forecast_date = dm.forecast_date
    )
),
outlier_summary AS (
    -- Fifth CTE: Summarize outliers
    SELECT
        od.parameter_name,
        od.forecast_date,
        COUNT(*) AS total_forecasts,
        COUNT(CASE WHEN od.is_iqr_outlier = TRUE THEN 1 END) AS iqr_outlier_count,
        COUNT(CASE WHEN od.is_percentile_outlier = TRUE THEN 1 END) AS percentile_outlier_count,
        COUNT(CASE WHEN od.is_zscore_outlier = TRUE THEN 1 END) AS zscore_outlier_count,
        AVG(CASE WHEN od.is_iqr_outlier = TRUE THEN od.parameter_value ELSE NULL END) AS avg_iqr_outlier_value,
        AVG(CASE WHEN od.is_percentile_outlier = TRUE THEN od.parameter_value ELSE NULL END) AS avg_percentile_outlier_value
    FROM outlier_detection od
    GROUP BY
        od.parameter_name,
        od.forecast_date
),
final_distribution_report AS (
    -- Sixth CTE: Final distribution report
    SELECT
        dm.parameter_name,
        dm.forecast_date,
        dm.forecast_count,
        dm.mean_value,
        dm.median_value,
        dm.q1_value,
        dm.q3_value,
        dm.p10_value,
        dm.p90_value,
        dm.p5_value,
        dm.p95_value,
        dm.min_value,
        dm.max_value,
        dm.stddev_value,
        ROUND(CAST(dm.iqr AS NUMERIC), 2) AS iqr,
        ROUND(CAST(dm.value_range AS NUMERIC), 2) AS value_range,
        ROUND(CAST(dm.coefficient_of_variation AS NUMERIC), 4) AS coefficient_of_variation,
        dm.skewness_indicator,
        os.iqr_outlier_count,
        os.percentile_outlier_count,
        os.zscore_outlier_count,
        ROUND(CAST(os.avg_iqr_outlier_value AS NUMERIC), 2) AS avg_iqr_outlier_value,
        -- Outlier percentage
        CASE
            WHEN os.total_forecasts > 0 THEN
                (os.iqr_outlier_count::NUMERIC / os.total_forecasts::NUMERIC) * 100
            ELSE 0
        END AS outlier_percentage,
        -- Window functions for comparison
        AVG(dm.mean_value) OVER (
            PARTITION BY dm.parameter_name
            ORDER BY dm.forecast_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_avg_mean_7d,
        PERCENT_RANK() OVER (
            PARTITION BY dm.parameter_name
            ORDER BY dm.stddev_value DESC
        ) AS stddev_percentile
    FROM distribution_metrics dm
    INNER JOIN outlier_summary os ON (
        dm.parameter_name = os.parameter_name
        AND dm.forecast_date = os.forecast_date
    )
)
SELECT
    parameter_name,
    forecast_date,
    forecast_count,
    mean_value,
    median_value,
    q1_value,
    q3_value,
    p10_value,
    p90_value,
    p5_value,
    p95_value,
    min_value,
    max_value,
    stddev_value,
    iqr,
    value_range,
    coefficient_of_variation,
    skewness_indicator,
    iqr_outlier_count,
    percentile_outlier_count,
    zscore_outlier_count,
    avg_iqr_outlier_value,
    ROUND(CAST(outlier_percentage AS NUMERIC), 2) AS outlier_percentage,
    ROUND(CAST(moving_avg_mean_7d AS NUMERIC), 2) AS moving_avg_mean_7d,
    ROUND(CAST(stddev_percentile * 100 AS NUMERIC), 2) AS stddev_percentile
FROM final_distribution_report
WHERE forecast_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY forecast_date DESC, parameter_name
LIMIT 500;
```

---

## Query 11: Geospatial Forecast Interpolation Analysis with Spatial Gradient Detection {#query-11}

**Use Case:** **Custom Weather Impact Modeling - Spatial Gradient Detection for Precision Agriculture**

**Description:** Enterprise-level geospatial forecast interpolation analysis identifying spatial gradients, interpolation opportunities, spatial patterns, and interpolation quality metrics. Implements production patterns for spatial interpolation and gradient analysis.

**Business Value:** Analysis of how weather parameters change across space with gradient calculations. Agriculture companies can understand temperature gradients across farmland for precision farming.

**Purpose:** Identifies spatial gradients for precise location-specific forecasts enabling precision agriculture.

**Complexity:** Multiple CTEs (7+ levels), spatial interpolation analysis, gradient calculations, spatial pattern detection, distance-based analysis, window functions

```sql
WITH spatial_forecast_grid AS (
    -- First CTE: Create spatial forecast grid
    SELECT
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        gf.grid_cell_latitude,
        gf.grid_cell_longitude,
        gf.parameter_value,
        gf.grid_cell_geom,
        ROUND(gf.grid_cell_latitude::NUMERIC, 2) AS rounded_lat,
        ROUND(gf.grid_cell_longitude::NUMERIC, 2) AS rounded_lon
    FROM grib2_forecasts gf
    WHERE gf.transformation_status = 'Success'
        AND gf.grid_cell_geom IS NOT NULL
),
nearest_neighbor_analysis AS (
    -- Second CTE: Find nearest neighbors for each grid cell
    SELECT
        sfg.forecast_id,
        sfg.parameter_name,
        sfg.forecast_time,
        sfg.rounded_lat,
        sfg.rounded_lon,
        sfg.parameter_value,
        -- Find nearest neighbor
        (
            SELECT sfg2.forecast_id
            FROM spatial_forecast_grid sfg2
            WHERE sfg2.forecast_id != sfg.forecast_id
                AND sfg2.parameter_name = sfg.parameter_name
                AND sfg2.forecast_time = sfg.forecast_time
                AND sfg2.grid_cell_geom IS NOT NULL
                AND sfg.grid_cell_geom IS NOT NULL
            ORDER BY ST_DISTANCE(sfg.grid_cell_geom, sfg2.grid_cell_geom)
            LIMIT 1
        ) AS nearest_neighbor_id,
        -- Distance to nearest neighbor
        (
            SELECT ST_DISTANCE(sfg.grid_cell_geom, sfg2.grid_cell_geom)
            FROM spatial_forecast_grid sfg2
            WHERE sfg2.forecast_id != sfg.forecast_id
                AND sfg2.parameter_name = sfg.parameter_name
                AND sfg2.forecast_time = sfg.forecast_time
                AND sfg2.grid_cell_geom IS NOT NULL
                AND sfg.grid_cell_geom IS NOT NULL
            ORDER BY ST_DISTANCE(sfg.grid_cell_geom, sfg2.grid_cell_geom)
            LIMIT 1
        ) AS distance_to_nearest_neighbor,
        -- Value of nearest neighbor
        (
            SELECT sfg2.parameter_value
            FROM spatial_forecast_grid sfg2
            WHERE sfg2.forecast_id != sfg.forecast_id
                AND sfg2.parameter_name = sfg.parameter_name
                AND sfg2.forecast_time = sfg.forecast_time
                AND sfg2.grid_cell_geom IS NOT NULL
                AND sfg.grid_cell_geom IS NOT NULL
            ORDER BY ST_DISTANCE(sfg.grid_cell_geom, sfg2.grid_cell_geom)
            LIMIT 1
        ) AS nearest_neighbor_value
    FROM spatial_forecast_grid sfg
),
spatial_gradient_calculation AS (
    -- Third CTE: Calculate spatial gradients
    SELECT
        nna.forecast_id,
        nna.parameter_name,
        nna.forecast_time,
        nna.rounded_lat,
        nna.rounded_lon,
        nna.parameter_value,
        nna.nearest_neighbor_id,
        ROUND(CAST(nna.distance_to_nearest_neighbor AS NUMERIC), 2) AS distance_to_nearest_neighbor,
        ROUND(CAST(nna.nearest_neighbor_value AS NUMERIC), 2) AS nearest_neighbor_value,
        -- Gradient calculation (value difference per unit distance)
        CASE
            WHEN nna.distance_to_nearest_neighbor > 0 AND nna.nearest_neighbor_value IS NOT NULL THEN
                ABS(nna.parameter_value - nna.nearest_neighbor_value) / nna.distance_to_nearest_neighbor
            ELSE NULL
        END AS spatial_gradient,
        -- Value difference
        CASE
            WHEN nna.nearest_neighbor_value IS NOT NULL THEN
                nna.parameter_value - nna.nearest_neighbor_value
            ELSE NULL
        END AS value_difference
    FROM nearest_neighbor_analysis nna
),
interpolation_quality_metrics AS (
    -- Fourth CTE: Calculate interpolation quality metrics
    SELECT
        sgc.forecast_id,
        sgc.parameter_name,
        sgc.forecast_time,
        sgc.rounded_lat,
        sgc.rounded_lon,
        sgc.parameter_value,
        sgc.distance_to_nearest_neighbor,
        sgc.spatial_gradient,
        sgc.value_difference,
        -- Count neighbors within different radii
        (
            SELECT COUNT(*)
            FROM spatial_forecast_grid sfg2
            WHERE sfg2.forecast_id != sgc.forecast_id
                AND sfg2.parameter_name = sgc.parameter_name
                AND sfg2.forecast_time = sgc.forecast_time
                AND sfg2.grid_cell_geom IS NOT NULL
                AND EXISTS (
                    SELECT 1 FROM spatial_forecast_grid sfg3
                    WHERE sfg3.forecast_id = sgc.forecast_id
                        AND sfg3.grid_cell_geom IS NOT NULL
                        AND ST_DISTANCE(sfg3.grid_cell_geom, sfg2.grid_cell_geom) < 10000
                )
        ) AS neighbors_within_10km,
        (
            SELECT COUNT(*)
            FROM spatial_forecast_grid sfg2
            WHERE sfg2.forecast_id != sgc.forecast_id
                AND sfg2.parameter_name = sgc.parameter_name
                AND sfg2.forecast_time = sgc.forecast_time
                AND sfg2.grid_cell_geom IS NOT NULL
                AND EXISTS (
                    SELECT 1 FROM spatial_forecast_grid sfg3
                    WHERE sfg3.forecast_id = sgc.forecast_id
                        AND sfg3.grid_cell_geom IS NOT NULL
                        AND ST_DISTANCE(sfg3.grid_cell_geom, sfg2.grid_cell_geom) < 25000
                )
        ) AS neighbors_within_25km,
        -- Interpolation quality score
        CASE
            WHEN sgc.distance_to_nearest_neighbor < 5000 AND sgc.spatial_gradient < 0.001 THEN 'Excellent'
            WHEN sgc.distance_to_nearest_neighbor < 10000 AND sgc.spatial_gradient < 0.002 THEN 'Good'
            WHEN sgc.distance_to_nearest_neighbor < 25000 AND sgc.spatial_gradient < 0.005 THEN 'Fair'
            ELSE 'Poor'
        END AS interpolation_quality
    FROM spatial_gradient_calculation sgc
),
spatial_pattern_analysis AS (
    -- Fifth CTE: Analyze spatial patterns
    SELECT
        iqm.forecast_id,
        iqm.parameter_name,
        iqm.forecast_time,
        iqm.rounded_lat,
        iqm.rounded_lon,
        iqm.parameter_value,
        iqm.distance_to_nearest_neighbor,
        ROUND(CAST(iqm.spatial_gradient AS NUMERIC), 6) AS spatial_gradient,
        iqm.neighbors_within_10km,
        iqm.neighbors_within_25km,
        iqm.interpolation_quality,
        -- Window functions for spatial pattern detection
        AVG(iqm.parameter_value) OVER (
            PARTITION BY iqm.parameter_name, iqm.forecast_time
            ORDER BY iqm.rounded_lat, iqm.rounded_lon
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS local_spatial_avg,
        STDDEV(iqm.parameter_value) OVER (
            PARTITION BY iqm.parameter_name, iqm.forecast_time
            ORDER BY iqm.rounded_lat, iqm.rounded_lon
            ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
        ) AS local_spatial_stddev,
        -- Gradient classification
        CASE
            WHEN iqm.spatial_gradient < 0.0005 THEN 'Very Low Gradient'
            WHEN iqm.spatial_gradient < 0.001 THEN 'Low Gradient'
            WHEN iqm.spatial_gradient < 0.002 THEN 'Moderate Gradient'
            WHEN iqm.spatial_gradient < 0.005 THEN 'High Gradient'
            ELSE 'Very High Gradient'
        END AS gradient_classification
    FROM interpolation_quality_metrics iqm
),
final_interpolation_report AS (
    -- Sixth CTE: Final interpolation report
    SELECT
        spa.forecast_id,
        spa.parameter_name,
        spa.forecast_time,
        spa.rounded_lat,
        spa.rounded_lon,
        spa.parameter_value,
        spa.distance_to_nearest_neighbor,
        spa.spatial_gradient,
        spa.neighbors_within_10km,
        spa.neighbors_within_25km,
        spa.interpolation_quality,
        ROUND(CAST(spa.local_spatial_avg AS NUMERIC), 2) AS local_spatial_avg,
        ROUND(CAST(spa.local_spatial_stddev AS NUMERIC), 2) AS local_spatial_stddev,
        spa.gradient_classification,
        -- Interpolation recommendations
        CASE
            WHEN spa.interpolation_quality = 'Poor' THEN 'Increase Grid Density'
            WHEN spa.neighbors_within_10km < 3 THEN 'Add More Neighbors'
            WHEN spa.spatial_gradient > 0.005 THEN 'High Variability - Use Advanced Interpolation'
            ELSE 'Standard Interpolation Sufficient'
        END AS interpolation_recommendation,
        -- Rankings
        PERCENT_RANK() OVER (
            PARTITION BY spa.parameter_name
            ORDER BY spa.spatial_gradient DESC
        ) AS gradient_percentile,
        NTILE(5) OVER (
            PARTITION BY spa.parameter_name
            ORDER BY spa.distance_to_nearest_neighbor ASC
        ) AS neighbor_density_quintile
    FROM spatial_pattern_analysis spa
)
SELECT
    forecast_id,
    parameter_name,
    forecast_time,
    rounded_lat,
    rounded_lon,
    parameter_value,
    distance_to_nearest_neighbor,
    spatial_gradient,
    neighbors_within_10km,
    neighbors_within_25km,
    interpolation_quality,
    local_spatial_avg,
    local_spatial_stddev,
    gradient_classification,
    interpolation_recommendation,
    ROUND(CAST(gradient_percentile * 100 AS NUMERIC), 2) AS gradient_percentile,
    neighbor_density_quintile
FROM final_interpolation_report
WHERE forecast_time >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY forecast_time DESC, spatial_gradient DESC
LIMIT 1000;
```

---

## Query 12: Weather Pattern Clustering Analysis with Spatial-Temporal Pattern Detection {#query-12}

**Use Case:** **Physical Climate Risk Assessment - Pattern-Based Risk Identification for Renewable Energy**

**Description:** Enterprise-level weather pattern clustering analysis identifying spatial-temporal patterns, clustering similar weather conditions, and detecting pattern anomalies. Implements production patterns for weather pattern recognition and clustering.

**Business Value:** Helps predict future weather patterns based on historical clusters for energy planning.

**Purpose:** Identification of recurring weather patterns with clustering metrics. Energy companies can identify patterns that affect renewable energy generation.

**Business Value:** Helps predict future weather patterns based on historical clusters for energy planning.

**Complexity:** Multiple CTEs (8+ levels), clustering analysis, pattern detection, spatial-temporal analysis, similarity calculations, window functions

```sql
WITH multi_parameter_forecast AS (
    -- First CTE: Combine multiple parameters
    SELECT
        gf_temp.forecast_id AS temp_forecast_id,
        gf_temp.forecast_time,
        DATE_TRUNC('hour', gf_temp.forecast_time) AS forecast_hour,
        gf_temp.grid_cell_latitude,
        gf_temp.grid_cell_longitude,
        gf_temp.parameter_value AS temperature,
        gf_precip.parameter_value AS precipitation,
        gf_wind.parameter_value AS wind_speed,
        ROUND(gf_temp.grid_cell_latitude::NUMERIC, 2) AS rounded_lat,
        ROUND(gf_temp.grid_cell_longitude::NUMERIC, 2) AS rounded_lon
    FROM grib2_forecasts gf_temp
    LEFT JOIN grib2_forecasts gf_precip ON (
        gf_precip.parameter_name = 'Precipitation'
        AND gf_precip.forecast_time = gf_temp.forecast_time
        AND ROUND(gf_precip.grid_cell_latitude::NUMERIC, 2) = ROUND(gf_temp.grid_cell_latitude::NUMERIC, 2)
        AND ROUND(gf_precip.grid_cell_longitude::NUMERIC, 2) = ROUND(gf_temp.grid_cell_longitude::NUMERIC, 2)
    )
    LEFT JOIN grib2_forecasts gf_wind ON (
        gf_wind.parameter_name = 'WindSpeed'
        AND gf_wind.forecast_time = gf_temp.forecast_time
        AND ROUND(gf_wind.grid_cell_latitude::NUMERIC, 2) = ROUND(gf_temp.grid_cell_latitude::NUMERIC, 2)
        AND ROUND(gf_wind.grid_cell_longitude::NUMERIC, 2) = ROUND(gf_temp.grid_cell_longitude::NUMERIC, 2)
    )
    WHERE gf_temp.parameter_name = 'Temperature'
        AND gf_temp.transformation_status = 'Success'
),
pattern_feature_extraction AS (
    -- Second CTE: Extract pattern features
    SELECT
        mpf.temp_forecast_id,
        mpf.forecast_time,
        mpf.forecast_hour,
        mpf.rounded_lat,
        mpf.rounded_lon,
        ROUND(CAST(mpf.temperature AS NUMERIC), 2) AS temperature,
        ROUND(CAST(COALESCE(mpf.precipitation, 0) AS NUMERIC), 2) AS precipitation,
        ROUND(CAST(COALESCE(mpf.wind_speed, 0) AS NUMERIC), 2) AS wind_speed,
        -- Normalized features for clustering
        CASE
            WHEN mpf.temperature BETWEEN 0 AND 100 THEN (mpf.temperature - 50) / 50.0
            ELSE 0
        END AS normalized_temp,
        CASE
            WHEN mpf.precipitation BETWEEN 0 AND 10 THEN mpf.precipitation / 10.0
            ELSE 0
        END AS normalized_precip,
        CASE
            WHEN mpf.wind_speed BETWEEN 0 AND 50 THEN mpf.wind_speed / 50.0
            ELSE 0
        END AS normalized_wind,
        -- Weather pattern classification
        CASE
            WHEN mpf.temperature < 32 AND COALESCE(mpf.precipitation, 0) > 0 THEN 'Freezing Precipitation'
            WHEN mpf.temperature < 50 AND COALESCE(mpf.precipitation, 0) > 0.1 THEN 'Cold Rain'
            WHEN mpf.temperature BETWEEN 50 AND 70 AND COALESCE(mpf.precipitation, 0) > 0.1 THEN 'Moderate Rain'
            WHEN mpf.temperature >= 70 AND COALESCE(mpf.precipitation, 0) > 0.1 THEN 'Warm Rain'
            WHEN mpf.temperature >= 85 AND COALESCE(mpf.wind_speed, 0) < 5 THEN 'Hot Calm'
            WHEN COALESCE(mpf.wind_speed, 0) > 30 THEN 'High Wind'
            WHEN COALESCE(mpf.precipitation, 0) = 0 AND mpf.temperature BETWEEN 60 AND 80 THEN 'Pleasant'
            ELSE 'Other'
        END AS weather_pattern
    FROM multi_parameter_forecast mpf
),
spatial_temporal_clustering AS (
    -- Third CTE: Spatial-temporal clustering
    SELECT
        pfe.temp_forecast_id,
        pfe.forecast_time,
        pfe.forecast_hour,
        pfe.rounded_lat,
        pfe.rounded_lon,
        pfe.temperature,
        pfe.precipitation,
        pfe.wind_speed,
        pfe.weather_pattern,
        -- Local pattern density
        COUNT(*) OVER (
            PARTITION BY pfe.weather_pattern, pfe.forecast_hour
        ) AS pattern_count_per_hour,
        COUNT(*) OVER (
            PARTITION BY pfe.weather_pattern
        ) AS total_pattern_count,
        -- Spatial neighbors with same pattern
        (
            SELECT COUNT(*)
            FROM pattern_feature_extraction pfe2
            WHERE pfe2.weather_pattern = pfe.weather_pattern
                AND pfe2.forecast_hour = pfe.forecast_hour
                AND ABS(pfe2.rounded_lat - pfe.rounded_lat) < 0.5
                AND ABS(pfe2.rounded_lon - pfe.rounded_lon) < 0.5
                AND pfe2.temp_forecast_id != pfe.temp_forecast_id
        ) AS spatial_neighbors_same_pattern,
        -- Temporal neighbors with same pattern
        (
            SELECT COUNT(*)
            FROM pattern_feature_extraction pfe2
            WHERE pfe2.weather_pattern = pfe.weather_pattern
                AND pfe2.rounded_lat = pfe.rounded_lat
                AND pfe2.rounded_lon = pfe.rounded_lon
                AND ABS(EXTRACT(EPOCH FROM (pfe2.forecast_time - pfe.forecast_time)) / 3600) <= 3
                AND pfe2.temp_forecast_id != pfe.temp_forecast_id
        ) AS temporal_neighbors_same_pattern
    FROM pattern_feature_extraction pfe
),
cluster_metrics AS (
    -- Fourth CTE: Calculate cluster metrics
    SELECT
        stc.temp_forecast_id,
        stc.forecast_time,
        stc.forecast_hour,
        stc.rounded_lat,
        stc.rounded_lon,
        stc.temperature,
        stc.precipitation,
        stc.wind_speed,
        stc.weather_pattern,
        stc.pattern_count_per_hour,
        stc.total_pattern_count,
        stc.spatial_neighbors_same_pattern,
        stc.temporal_neighbors_same_pattern,
        -- Cluster cohesion score
        CASE
            WHEN stc.spatial_neighbors_same_pattern >= 5 AND stc.temporal_neighbors_same_pattern >= 3 THEN 'High Cohesion'
            WHEN stc.spatial_neighbors_same_pattern >= 3 AND stc.temporal_neighbors_same_pattern >= 2 THEN 'Medium Cohesion'
            WHEN stc.spatial_neighbors_same_pattern >= 1 OR stc.temporal_neighbors_same_pattern >= 1 THEN 'Low Cohesion'
            ELSE 'Isolated'
        END AS cluster_cohesion,
        -- Pattern frequency
        CASE
            WHEN stc.total_pattern_count > 1000 THEN 'Very Common'
            WHEN stc.total_pattern_count > 500 THEN 'Common'
            WHEN stc.total_pattern_count > 100 THEN 'Uncommon'
            ELSE 'Rare'
        END AS pattern_frequency
    FROM spatial_temporal_clustering stc
),
pattern_anomaly_detection AS (
    -- Fifth CTE: Detect pattern anomalies
    SELECT
        cm.temp_forecast_id,
        cm.forecast_time,
        cm.forecast_hour,
        cm.rounded_lat,
        cm.rounded_lon,
        cm.temperature,
        cm.precipitation,
        cm.wind_speed,
        cm.weather_pattern,
        cm.cluster_cohesion,
        cm.pattern_frequency,
        -- Anomaly detection
        CASE
            WHEN cm.cluster_cohesion = 'Isolated' AND cm.pattern_frequency = 'Rare' THEN 'Anomaly'
            WHEN cm.cluster_cohesion = 'Low Cohesion' AND cm.pattern_frequency IN ('Uncommon', 'Rare') THEN 'Potential Anomaly'
            ELSE 'Normal'
        END AS anomaly_status,
        -- Window functions for pattern comparison
        AVG(cm.temperature) OVER (
            PARTITION BY cm.weather_pattern
        ) AS avg_temp_for_pattern,
        AVG(cm.precipitation) OVER (
            PARTITION BY cm.weather_pattern
        ) AS avg_precip_for_pattern,
        AVG(cm.wind_speed) OVER (
            PARTITION BY cm.weather_pattern
        ) AS avg_wind_for_pattern
    FROM cluster_metrics cm
),
final_pattern_report AS (
    -- Sixth CTE: Final pattern report
    SELECT
        pad.temp_forecast_id,
        pad.forecast_time,
        pad.forecast_hour,
        pad.rounded_lat,
        pad.rounded_lon,
        pad.temperature,
        pad.precipitation,
        pad.wind_speed,
        pad.weather_pattern,
        pad.cluster_cohesion,
        pad.pattern_frequency,
        pad.anomaly_status,
        ROUND(CAST(pad.avg_temp_for_pattern AS NUMERIC), 2) AS avg_temp_for_pattern,
        ROUND(CAST(pad.avg_precip_for_pattern AS NUMERIC), 2) AS avg_precip_for_pattern,
        ROUND(CAST(pad.avg_wind_for_pattern AS NUMERIC), 2) AS avg_wind_for_pattern,
        -- Deviation from pattern average
        ABS(pad.temperature - pad.avg_temp_for_pattern) AS temp_deviation_from_pattern,
        ABS(pad.precipitation - pad.avg_precip_for_pattern) AS precip_deviation_from_pattern,
        ABS(pad.wind_speed - pad.avg_wind_for_pattern) AS wind_deviation_from_pattern,
        -- Rankings
        PERCENT_RANK() OVER (
            PARTITION BY pad.weather_pattern
            ORDER BY pad.temperature DESC
        ) AS temp_percentile_in_pattern,
        NTILE(5) OVER (
            PARTITION BY pad.weather_pattern
            ORDER BY pad.temperature DESC
        ) AS temp_quintile_in_pattern
    FROM pattern_anomaly_detection pad
)
SELECT
    temp_forecast_id,
    forecast_time,
    forecast_hour,
    rounded_lat,
    rounded_lon,
    temperature,
    precipitation,
    wind_speed,
    weather_pattern,
    cluster_cohesion,
    pattern_frequency,
    anomaly_status,
    avg_temp_for_pattern,
    avg_precip_for_pattern,
    avg_wind_for_pattern,
    ROUND(CAST(temp_deviation_from_pattern AS NUMERIC), 2) AS temp_deviation_from_pattern,
    ROUND(CAST(precip_deviation_from_pattern AS NUMERIC), 2) AS precip_deviation_from_pattern,
    ROUND(CAST(wind_deviation_from_pattern AS NUMERIC), 2) AS wind_deviation_from_pattern,
    ROUND(CAST(temp_percentile_in_pattern * 100 AS NUMERIC), 2) AS temp_percentile_in_pattern,
    temp_quintile_in_pattern
FROM final_pattern_report
WHERE forecast_time >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY forecast_time DESC, anomaly_status DESC, weather_pattern
LIMIT 1000;
```

---

## Query 13: Forecast Model Performance Comparison with Multi-Model Analysis {#query-13}

**Use Case:** **Forensic Meteorology - Multi-Model Analysis for Comprehensive Legal Evidence**

**Description:** This SQL query performs comprehensive forecast model performance comparison for a weather consulting firm. It identifies forecast models (NDFD, GFS, NAM, RAP) from source file patterns, spatially matches forecasts with weather observations within 25km and temporally within 1 hour, calculates accuracy metrics (mean absolute error, root mean squared error, bias, success rates), ranks models by performance, computes weighted performance scores, and classifies models as Best/Good/Average/Below Average performers. The query uses multiple nested CTEs to match forecast data with observations, calculate statistical metrics, compare models against overall averages using window functions, rank models by multiple criteria, and generate final performance classifications with trend analysis including moving averages and percentile rankings.

**Business Value:** Comparison of different forecast models' performance with accuracy metrics. Court cases require comparison of multiple forecast models to establish weather conditions.

**Purpose:** Provides comprehensive analysis using multiple models for legal evidence and risk assessment.

**Complexity:** Multiple CTEs (7+ levels), model comparison, performance metrics, accuracy calculations, ranking analysis, window functions

```sql
WITH forecast_model_identification AS (
    -- First CTE: Identify forecast models (based on source file patterns)
    SELECT
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        gf.parameter_value,
        gf.source_file,
        -- Extract model identifier from source file
        CASE
            WHEN gf.source_file LIKE '%ndfd%' THEN 'NDFD'
            WHEN gf.source_file LIKE '%gfs%' THEN 'GFS'
            WHEN gf.source_file LIKE '%nam%' THEN 'NAM'
            WHEN gf.source_file LIKE '%rap%' THEN 'RAP'
            ELSE 'Unknown'
        END AS forecast_model,
        DATE_TRUNC('day', gf.forecast_time) AS forecast_date
    FROM grib2_forecasts gf
    WHERE gf.transformation_status = 'Success'
),
observation_forecast_matching AS (
    -- Second CTE: Match forecasts with observations
    SELECT
        fmi.forecast_id,
        fmi.parameter_name,
        fmi.forecast_time,
        fmi.forecast_model,
        fmi.forecast_date,
        fmi.parameter_value AS forecast_value,
        wo.observation_id,
        wo.observation_time,
        CASE
            WHEN fmi.parameter_name = 'Temperature' THEN wo.temperature
            WHEN fmi.parameter_name = 'Precipitation' THEN COALESCE(wo.precipitation_amount, 0)
            WHEN fmi.parameter_name = 'WindSpeed' THEN wo.wind_speed
            ELSE NULL
        END AS observation_value,
        ABS(fmi.parameter_value - CASE
            WHEN fmi.parameter_name = 'Temperature' THEN wo.temperature
            WHEN fmi.parameter_name = 'Precipitation' THEN COALESCE(wo.precipitation_amount, 0)
            WHEN fmi.parameter_name = 'WindSpeed' THEN wo.wind_speed
            ELSE NULL
        END) AS absolute_error
    FROM forecast_model_identification fmi
    INNER JOIN weather_observations wo ON (
        wo.observation_time BETWEEN fmi.forecast_time - INTERVAL '1 hour' AND fmi.forecast_time + INTERVAL '1 hour'
        AND EXISTS (
            SELECT 1 FROM grib2_forecasts gf2
            WHERE gf2.forecast_id = fmi.forecast_id
                AND gf2.grid_cell_geom IS NOT NULL
                AND wo.station_geom IS NOT NULL
                AND ST_DISTANCE(gf2.grid_cell_geom, wo.station_geom) < 25000
        )
    )
    WHERE wo.observation_value IS NOT NULL
),
model_performance_metrics AS (
    -- Third CTE: Calculate model performance metrics
    SELECT
        ofm.forecast_model,
        ofm.parameter_name,
        ofm.forecast_date,
        COUNT(*) AS validation_count,
        AVG(ofm.absolute_error) AS mean_absolute_error,
        SQRT(AVG(POWER(ofm.absolute_error, 2))) AS root_mean_squared_error,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ofm.absolute_error) AS median_absolute_error,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY ofm.absolute_error) AS q1_error,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ofm.absolute_error) AS q3_error,
        STDDEV(ofm.absolute_error) AS error_stddev,
        MIN(ofm.absolute_error) AS min_error,
        MAX(ofm.absolute_error) AS max_error,
        -- Bias calculation
        AVG(ofm.forecast_value - ofm.observation_value) AS mean_bias,
        -- Success rate (within acceptable error threshold)
        COUNT(CASE WHEN ofm.absolute_error <= 5 THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100 AS success_rate_5deg,
        COUNT(CASE WHEN ofm.absolute_error <= 10 THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC * 100 AS success_rate_10deg
    FROM observation_forecast_matching ofm
    GROUP BY
        ofm.forecast_model,
        ofm.parameter_name,
        ofm.forecast_date
),
model_comparison_analysis AS (
    -- Fourth CTE: Compare models
    SELECT
        mpm.forecast_model,
        mpm.parameter_name,
        mpm.forecast_date,
        mpm.validation_count,
        ROUND(CAST(mpm.mean_absolute_error AS NUMERIC), 2) AS mean_absolute_error,
        ROUND(CAST(mpm.root_mean_squared_error AS NUMERIC), 2) AS root_mean_squared_error,
        ROUND(CAST(mpm.median_absolute_error AS NUMERIC), 2) AS median_absolute_error,
        ROUND(CAST(mpm.error_stddev AS NUMERIC), 2) AS error_stddev,
        ROUND(CAST(mpm.mean_bias AS NUMERIC), 2) AS mean_bias,
        ROUND(CAST(mpm.success_rate_5deg AS NUMERIC), 2) AS success_rate_5deg,
        ROUND(CAST(mpm.success_rate_10deg AS NUMERIC), 2) AS success_rate_10deg,
        -- Compare with overall average
        AVG(mpm.mean_absolute_error) OVER (
            PARTITION BY mpm.parameter_name, mpm.forecast_date
        ) AS overall_avg_mae,
        -- Model ranking
        ROW_NUMBER() OVER (
            PARTITION BY mpm.parameter_name, mpm.forecast_date
            ORDER BY mpm.mean_absolute_error ASC
        ) AS model_rank_by_mae,
        ROW_NUMBER() OVER (
            PARTITION BY mpm.parameter_name, mpm.forecast_date
            ORDER BY mpm.success_rate_10deg DESC
        ) AS model_rank_by_success_rate
    FROM model_performance_metrics mpm
),
model_performance_scoring AS (
    -- Fifth CTE: Calculate performance scores
    SELECT
        mca.forecast_model,
        mca.parameter_name,
        mca.forecast_date,
        mca.validation_count,
        mca.mean_absolute_error,
        mca.root_mean_squared_error,
        mca.median_absolute_error,
        mca.error_stddev,
        mca.mean_bias,
        mca.success_rate_5deg,
        mca.success_rate_10deg,
        mca.overall_avg_mae,
        mca.model_rank_by_mae,
        mca.model_rank_by_success_rate,
        -- Performance score (higher is better)
        (
            -- MAE component (40% weight) - lower is better
            GREATEST(0, 1.0 - (mca.mean_absolute_error / NULLIF(mca.overall_avg_mae, 0))) * 40 +
            -- Success rate component (40% weight)
            (mca.success_rate_10deg / 100.0) * 40 +
            -- Bias component (20% weight) - less bias is better
            GREATEST(0, 1.0 - (ABS(mca.mean_bias) / 10.0)) * 20
        ) AS performance_score,
        -- Performance classification
        CASE
            WHEN mca.model_rank_by_mae = 1 AND mca.success_rate_10deg > 90 THEN 'Best Performer'
            WHEN mca.model_rank_by_mae <= 2 AND mca.success_rate_10deg > 85 THEN 'Good Performer'
            WHEN mca.model_rank_by_mae <= 3 AND mca.success_rate_10deg > 80 THEN 'Average Performer'
            ELSE 'Below Average'
        END AS performance_classification
    FROM model_comparison_analysis mca
),
final_model_comparison AS (
    -- Sixth CTE: Final model comparison
    SELECT
        mps.forecast_model,
        mps.parameter_name,
        mps.forecast_date,
        mps.validation_count,
        mps.mean_absolute_error,
        mps.root_mean_squared_error,
        mps.median_absolute_error,
        mps.error_stddev,
        mps.mean_bias,
        mps.success_rate_5deg,
        mps.success_rate_10deg,
        mps.model_rank_by_mae,
        mps.model_rank_by_success_rate,
        ROUND(CAST(mps.performance_score AS NUMERIC), 2) AS performance_score,
        mps.performance_classification,
        -- Window functions for trend analysis
        AVG(mps.performance_score) OVER (
            PARTITION BY mps.forecast_model, mps.parameter_name
            ORDER BY mps.forecast_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS moving_avg_performance_7d,
        LAG(mps.performance_score, 1) OVER (
            PARTITION BY mps.forecast_model, mps.parameter_name
            ORDER BY mps.forecast_date
        ) AS prev_day_performance_score,
        -- Percentile rankings
        PERCENT_RANK() OVER (
            PARTITION BY mps.parameter_name
            ORDER BY mps.performance_score DESC
        ) AS performance_percentile,
        NTILE(5) OVER (
            PARTITION BY mps.parameter_name
            ORDER BY mps.performance_score DESC
        ) AS performance_quintile
    FROM model_performance_scoring mps
)
SELECT
    forecast_model,
    parameter_name,
    forecast_date,
    validation_count,
    mean_absolute_error,
    root_mean_squared_error,
    median_absolute_error,
    error_stddev,
    mean_bias,
    success_rate_5deg,
    success_rate_10deg,
    model_rank_by_mae,
    model_rank_by_success_rate,
    performance_score,
    performance_classification,
    ROUND(CAST(moving_avg_performance_7d AS NUMERIC), 2) AS moving_avg_performance_7d,
    ROUND(CAST(prev_day_performance_score AS NUMERIC), 2) AS prev_day_performance_score,
    ROUND(CAST(performance_percentile * 100 AS NUMERIC), 2) AS performance_percentile,
    performance_quintile
FROM final_model_comparison
WHERE forecast_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY forecast_date DESC, parameter_name, performance_score DESC
LIMIT 500;
```

---

## Query 14: Boundary Forecast Anomaly Detection with Statistical Outlier Identification {#query-14}

**Use Case:** **Physical Climate Risk Assessment - Extreme Event Detection for Emergency Management**

**Description:** Enterprise-level boundary forecast anomaly detection identifying statistical outliers, anomalies in boundary aggregations, and unusual forecast patterns. Implements production patterns for anomaly detection in geospatial forecast data.

**Business Value:** Early warning system for extreme weather events enabling proactive risk management.

**Purpose:** Identification of anomalous weather patterns within boundaries with outlier metrics. Emergency management needs anomaly detection for early warning systems.

**Business Value:** Early warning system for extreme weather events enabling proactive risk management.

**Complexity:** Multiple CTEs (8+ levels), anomaly detection algorithms, statistical outlier identification, pattern analysis, window functions, UNION operations

```sql
WITH boundary_forecast_aggregation AS (
    -- First CTE: Aggregate forecasts by boundary
    SELECT
        sb.boundary_id,
        sb.feature_type,
        sb.feature_name,
        gf.parameter_name,
        gf.forecast_time,
        DATE_TRUNC('hour', gf.forecast_time) AS forecast_hour,
        DATE_TRUNC('day', gf.forecast_time) AS forecast_date,
        COUNT(DISTINCT gf.forecast_id) AS grid_cells_count,
        AVG(gf.parameter_value) AS avg_value,
        MIN(gf.parameter_value) AS min_value,
        MAX(gf.parameter_value) AS max_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gf.parameter_value) AS median_value,
        STDDEV(gf.parameter_value) AS stddev_value
    FROM shapefile_boundaries sb
    INNER JOIN grib2_forecasts gf ON (
        sb.boundary_geom IS NOT NULL
        AND gf.grid_cell_geom IS NOT NULL
        AND ST_WITHIN(gf.grid_cell_geom, sb.boundary_geom)
    )
    WHERE gf.transformation_status = 'Success'
    GROUP BY
        sb.boundary_id,
        sb.feature_type,
        sb.feature_name,
        gf.parameter_name,
        gf.forecast_time
),
temporal_statistics AS (
    -- Second CTE: Calculate temporal statistics
    SELECT
        bfa.boundary_id,
        bfa.feature_type,
        bfa.feature_name,
        bfa.parameter_name,
        bfa.forecast_time,
        bfa.forecast_hour,
        bfa.forecast_date,
        bfa.grid_cells_count,
        ROUND(CAST(bfa.avg_value AS NUMERIC), 2) AS avg_value,
        ROUND(CAST(bfa.min_value AS NUMERIC), 2) AS min_value,
        ROUND(CAST(bfa.max_value AS NUMERIC), 2) AS max_value,
        ROUND(CAST(bfa.median_value AS NUMERIC), 2) AS median_value,
        ROUND(CAST(bfa.stddev_value AS NUMERIC), 2) AS stddev_value,
        -- Temporal averages
        AVG(bfa.avg_value) OVER (
            PARTITION BY bfa.boundary_id, bfa.parameter_name
            ORDER BY bfa.forecast_time
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS moving_avg_24h,
        AVG(bfa.avg_value) OVER (
            PARTITION BY bfa.boundary_id, bfa.parameter_name
            ORDER BY bfa.forecast_time
            ROWS BETWEEN 167 PRECEDING AND CURRENT ROW
        ) AS moving_avg_168h,
        -- Temporal standard deviations
        STDDEV(bfa.avg_value) OVER (
            PARTITION BY bfa.boundary_id, bfa.parameter_name
            ORDER BY bfa.forecast_time
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS moving_stddev_24h,
        STDDEV(bfa.avg_value) OVER (
            PARTITION BY bfa.boundary_id, bfa.parameter_name
            ORDER BY bfa.forecast_time
            ROWS BETWEEN 167 PRECEDING AND CURRENT ROW
        ) AS moving_stddev_168h,
        -- Lag values
        LAG(bfa.avg_value, 1) OVER (
            PARTITION BY bfa.boundary_id, bfa.parameter_name
            ORDER BY bfa.forecast_time
        ) AS prev_hour_avg,
        LAG(bfa.avg_value, 24) OVER (
            PARTITION BY bfa.boundary_id, bfa.parameter_name
            ORDER BY bfa.forecast_time
        ) AS prev_day_avg
    FROM boundary_forecast_aggregation bfa
),
anomaly_detection_metrics AS (
    -- Third CTE: Calculate anomaly detection metrics
    SELECT
        ts.boundary_id,
        ts.feature_type,
        ts.feature_name,
        ts.parameter_name,
        ts.forecast_time,
        ts.forecast_hour,
        ts.forecast_date,
        ts.avg_value,
        ts.min_value,
        ts.max_value,
        ts.median_value,
        ts.stddev_value,
        ROUND(CAST(ts.moving_avg_24h AS NUMERIC), 2) AS moving_avg_24h,
        ROUND(CAST(ts.moving_avg_168h AS NUMERIC), 2) AS moving_avg_168h,
        ROUND(CAST(ts.moving_stddev_24h AS NUMERIC), 2) AS moving_stddev_24h,
        ROUND(CAST(ts.moving_stddev_168h AS NUMERIC), 2) AS moving_stddev_168h,
        ROUND(CAST(ts.prev_hour_avg AS NUMERIC), 2) AS prev_hour_avg,
        ROUND(CAST(ts.prev_day_avg AS NUMERIC), 2) AS prev_day_avg,
        -- Z-score calculation
        CASE
            WHEN ts.moving_stddev_24h > 0 THEN
                (ts.avg_value - ts.moving_avg_24h) / ts.moving_stddev_24h
            ELSE NULL
        END AS z_score_24h,
        -- Deviation from moving average
        ts.avg_value - ts.moving_avg_24h AS deviation_from_24h_avg,
        ts.avg_value - ts.moving_avg_168h AS deviation_from_168h_avg,
        -- Change from previous
        CASE
            WHEN ts.prev_hour_avg IS NOT NULL THEN
                ts.avg_value - ts.prev_hour_avg
            ELSE NULL
        END AS change_from_prev_hour,
        CASE
            WHEN ts.prev_day_avg IS NOT NULL THEN
                ts.avg_value - ts.prev_day_avg
            ELSE NULL
        END AS change_from_prev_day
    FROM temporal_statistics ts
),
outlier_classification AS (
    -- Fourth CTE: Classify outliers
    SELECT
        adm.boundary_id,
        adm.feature_type,
        adm.feature_name,
        adm.parameter_name,
        adm.forecast_time,
        adm.forecast_hour,
        adm.forecast_date,
        adm.avg_value,
        ROUND(CAST(adm.z_score_24h AS NUMERIC), 2) AS z_score_24h,
        ROUND(CAST(adm.deviation_from_24h_avg AS NUMERIC), 2) AS deviation_from_24h_avg,
        ROUND(CAST(adm.deviation_from_168h_avg AS NUMERIC), 2) AS deviation_from_168h_avg,
        ROUND(CAST(adm.change_from_prev_hour AS NUMERIC), 2) AS change_from_prev_hour,
        ROUND(CAST(adm.change_from_prev_day AS NUMERIC), 2) AS change_from_prev_day,
        -- Z-score based anomaly
        CASE
            WHEN adm.z_score_24h IS NOT NULL THEN
                CASE
                    WHEN ABS(adm.z_score_24h) > 3 THEN 'Extreme Anomaly'
                    WHEN ABS(adm.z_score_24h) > 2 THEN 'Significant Anomaly'
                    WHEN ABS(adm.z_score_24h) > 1.5 THEN 'Moderate Anomaly'
                    ELSE 'Normal'
                END
            ELSE NULL
        END AS z_score_anomaly,
        -- Deviation based anomaly
        CASE
            WHEN adm.moving_stddev_24h IS NOT NULL THEN
                CASE
                    WHEN ABS(adm.deviation_from_24h_avg) > 3 * adm.moving_stddev_24h THEN 'Extreme Deviation'
                    WHEN ABS(adm.deviation_from_24h_avg) > 2 * adm.moving_stddev_24h THEN 'Significant Deviation'
                    WHEN ABS(adm.deviation_from_24h_avg) > adm.moving_stddev_24h THEN 'Moderate Deviation'
                    ELSE 'Normal Deviation'
                END
            ELSE NULL
        END AS deviation_anomaly,
        -- Change based anomaly
        CASE
            WHEN adm.change_from_prev_hour IS NOT NULL AND adm.moving_stddev_24h IS NOT NULL THEN
                CASE
                    WHEN ABS(adm.change_from_prev_hour) > 3 * adm.moving_stddev_24h THEN 'Extreme Change'
                    WHEN ABS(adm.change_from_prev_hour) > 2 * adm.moving_stddev_24h THEN 'Significant Change'
                    ELSE 'Normal Change'
                END
            ELSE NULL
        END AS change_anomaly
    FROM anomaly_detection_metrics adm
),
anomaly_severity_scoring AS (
    -- Fifth CTE: Score anomaly severity
    SELECT
        oc.boundary_id,
        oc.feature_type,
        oc.feature_name,
        oc.parameter_name,
        oc.forecast_time,
        oc.forecast_hour,
        oc.forecast_date,
        oc.avg_value,
        oc.z_score_24h,
        oc.deviation_from_24h_avg,
        oc.change_from_prev_hour,
        oc.z_score_anomaly,
        oc.deviation_anomaly,
        oc.change_anomaly,
        -- Anomaly severity score
        CASE
            WHEN oc.z_score_anomaly = 'Extreme Anomaly' OR oc.deviation_anomaly = 'Extreme Deviation' THEN 5
            WHEN oc.z_score_anomaly = 'Significant Anomaly' OR oc.deviation_anomaly = 'Significant Deviation' THEN 4
            WHEN oc.z_score_anomaly = 'Moderate Anomaly' OR oc.deviation_anomaly = 'Moderate Deviation' THEN 3
            WHEN oc.change_anomaly = 'Extreme Change' THEN 4
            WHEN oc.change_anomaly = 'Significant Change' THEN 3
            ELSE 1
        END AS anomaly_severity_score,
        -- Overall anomaly status
        CASE
            WHEN oc.z_score_anomaly IN ('Extreme Anomaly', 'Significant Anomaly') OR
                 oc.deviation_anomaly IN ('Extreme Deviation', 'Significant Deviation') THEN 'Anomaly Detected'
            WHEN oc.change_anomaly IN ('Extreme Change', 'Significant Change') THEN 'Rapid Change Detected'
            ELSE 'Normal'
        END AS overall_anomaly_status
    FROM outlier_classification oc
),
final_anomaly_report AS (
    -- Sixth CTE: Final anomaly report
    SELECT
        ass.boundary_id,
        ass.feature_type,
        ass.feature_name,
        ass.parameter_name,
        ass.forecast_time,
        ass.forecast_hour,
        ass.forecast_date,
        ass.avg_value,
        ass.z_score_24h,
        ass.deviation_from_24h_avg,
        ass.change_from_prev_hour,
        ass.anomaly_severity_score,
        ass.overall_anomaly_status,
        -- Window functions for anomaly frequency
        COUNT(CASE WHEN ass.overall_anomaly_status != 'Normal' THEN 1 END) OVER (
            PARTITION BY ass.boundary_id, ass.parameter_name
            ORDER BY ass.forecast_time
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) AS anomalies_in_last_24h,
        -- Rankings
        ROW_NUMBER() OVER (
            PARTITION BY ass.parameter_name, ass.forecast_time
            ORDER BY ass.anomaly_severity_score DESC
        ) AS anomaly_rank,
        PERCENT_RANK() OVER (
            PARTITION BY ass.feature_type
            ORDER BY ass.anomaly_severity_score DESC
        ) AS anomaly_severity_percentile
    FROM anomaly_severity_scoring ass
)
SELECT
    boundary_id,
    feature_type,
    feature_name,
    parameter_name,
    forecast_time,
    forecast_hour,
    forecast_date,
    avg_value,
    z_score_24h,
    deviation_from_24h_avg,
    change_from_prev_hour,
    anomaly_severity_score,
    overall_anomaly_status,
    anomalies_in_last_24h,
    anomaly_rank,
    ROUND(CAST(anomaly_severity_percentile * 100 AS NUMERIC), 2) AS anomaly_severity_percentile
FROM final_anomaly_report
WHERE forecast_date >= CURRENT_DATE - INTERVAL '7 days'
    AND overall_anomaly_status != 'Normal'
ORDER BY forecast_time DESC, anomaly_severity_score DESC
LIMIT 500;
```

---

## Query 15: Insurance Risk Factor Calculation from 7-14 Day Forecasts {#query-15}

**Use Case:** **Insurance Underwriting - Multi-Day Forecast Risk Assessment for Rate Determination**

**Description:** Calculates comprehensive risk factors for insurance policy areas based on 7-14 day forecasts from December 3-17, 2025. Analyzes multiple weather parameters to determine extreme event probabilities, precipitation risk, temperature extremes, wind damage risk, freeze risk, and flood risk.

**Business Value:** Risk factor analysis report showing forecast-based risk scores for each policy area and forecast day (7-14 days ahead).

**Purpose:** Enables insurance companies to adjust rates dynamically based on forecasted weather risks, improving underwriting accuracy and profitability.

**Complexity:** Multiple CTEs (8+ levels), forecast period filtering, risk calculations, percentile analysis, window functions, spatial joins

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period (Dec 3-17, 2025)
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end,
        DATE '2025-12-03' AS forecast_date_start,
        DATE '2025-12-17' AS forecast_date_end
),
policy_area_forecasts AS (
    -- Second CTE: Join forecasts with policy areas
    SELECT
        ipa.policy_area_id,
        ipa.policy_type,
        ipa.coverage_type,
        ipa.policy_area_name,
        ipa.state_code,
        ipa.risk_zone,
        gf.forecast_id,
        gf.parameter_name,
        gf.forecast_time,
        DATE_TRUNC('day', gf.forecast_time) AS forecast_day_date,
        DATE_TRUNC('day', fp.period_start) AS period_start_date,
        DATE_TRUNC('day', fp.period_end) AS period_end_date,
        -- Calculate forecast day (days ahead)
        (DATE_TRUNC('day', gf.forecast_time)::date - DATE_TRUNC('day', CURRENT_TIMESTAMP)::date) AS forecast_day,
        gf.parameter_value,
        gf.grid_cell_latitude,
        gf.grid_cell_longitude
    FROM insurance_policy_areas ipa
    CROSS JOIN forecast_period fp
    INNER JOIN shapefile_boundaries sb ON ipa.boundary_id = sb.boundary_id
    INNER JOIN grib2_forecasts gf ON (
        sb.boundary_geom IS NOT NULL
        AND gf.grid_cell_geom IS NOT NULL
        AND ST_WITHIN(gf.grid_cell_geom, sb.boundary_geom)
    )
    WHERE ipa.is_active = TRUE
        AND gf.transformation_status = 'Success'
        AND DATE_TRUNC('day', gf.forecast_time) BETWEEN fp.period_start AND fp.period_end
        AND (DATE_TRUNC('day', gf.forecast_time)::date - DATE_TRUNC('day', CURRENT_TIMESTAMP)::date) BETWEEN 7 AND 14
),
forecast_statistics AS (
    -- Third CTE: Calculate forecast statistics by policy area and parameter
    SELECT
        paf.policy_area_id,
        paf.policy_type,
        paf.coverage_type,
        paf.policy_area_name,
        paf.state_code,
        paf.risk_zone,
        paf.parameter_name,
        paf.forecast_day,
        DATE_TRUNC('day', paf.forecast_time) AS forecast_date,
        COUNT(*) AS forecast_count,
        MIN(paf.parameter_value) AS min_value,
        MAX(paf.parameter_value) AS max_value,
        AVG(paf.parameter_value) AS avg_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY paf.parameter_value) AS median_value,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY paf.parameter_value) AS q1_value,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY paf.parameter_value) AS q3_value,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY paf.parameter_value) AS p90_value,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY paf.parameter_value) AS p95_value,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY paf.parameter_value) AS p99_value,
        STDDEV(paf.parameter_value) AS stddev_value,
        VARIANCE(paf.parameter_value) AS variance_value
    FROM policy_area_forecasts paf
    GROUP BY
        paf.policy_area_id,
        paf.policy_type,
        paf.coverage_type,
        paf.policy_area_name,
        paf.state_code,
        paf.risk_zone,
        paf.parameter_name,
        paf.forecast_day,
        DATE_TRUNC('day', paf.forecast_time)
),
precipitation_risk_calculation AS (
    -- Fourth CTE: Calculate precipitation risk
    SELECT
        fs.policy_area_id,
        fs.policy_type,
        fs.forecast_day,
        fs.forecast_date,
        fs.avg_value AS avg_precipitation,
        fs.max_value AS max_precipitation,
        fs.p95_value AS p95_precipitation,
        fs.p99_value AS p99_precipitation,
        -- Cumulative precipitation risk (higher for more precipitation)
        CASE
            WHEN fs.avg_value > 50 THEN 100.0  -- Extreme risk
            WHEN fs.avg_value > 25 THEN 75.0 + ((fs.avg_value - 25) / 25.0) * 25.0
            WHEN fs.avg_value > 10 THEN 50.0 + ((fs.avg_value - 10) / 15.0) * 25.0
            WHEN fs.avg_value > 5 THEN 25.0 + ((fs.avg_value - 5) / 5.0) * 25.0
            ELSE (fs.avg_value / 5.0) * 25.0
        END AS cumulative_precipitation_risk,
        -- Extreme event probability (based on percentile thresholds)
        CASE
            WHEN fs.p99_value > 50 THEN 0.95
            WHEN fs.p95_value > 50 THEN 0.75
            WHEN fs.p95_value > 25 THEN 0.50
            WHEN fs.p90_value > 25 THEN 0.25
            ELSE 0.10
        END AS extreme_event_probability
    FROM forecast_statistics fs
    WHERE fs.parameter_name = 'Precipitation'
),
temperature_risk_calculation AS (
    -- Fifth CTE: Calculate temperature extreme risk
    SELECT
        fs.policy_area_id,
        fs.policy_type,
        fs.forecast_day,
        fs.forecast_date,
        fs.avg_value AS avg_temperature,
        fs.min_value AS min_temperature,
        fs.max_value AS max_temperature,
        fs.p95_value AS p95_temperature,
        fs.p5_value AS p5_temperature,
        -- Freeze risk (temperature below 32°F)
        CASE
            WHEN fs.min_value < 20 THEN 100.0  -- Extreme freeze risk
            WHEN fs.min_value < 28 THEN 75.0 + ((28 - fs.min_value) / 8.0) * 25.0
            WHEN fs.min_value < 32 THEN 50.0 + ((32 - fs.min_value) / 4.0) * 25.0
            WHEN fs.min_value < 35 THEN 25.0 + ((35 - fs.min_value) / 3.0) * 25.0
            ELSE 0.0
        END AS freeze_risk,
        -- Heat risk (temperature above 90°F)
        CASE
            WHEN fs.max_value > 100 THEN 100.0  -- Extreme heat risk
            WHEN fs.max_value > 95 THEN 75.0 + ((fs.max_value - 95) / 5.0) * 25.0
            WHEN fs.max_value > 90 THEN 50.0 + ((fs.max_value - 90) / 5.0) * 25.0
            WHEN fs.max_value > 85 THEN 25.0 + ((fs.max_value - 85) / 5.0) * 25.0
            ELSE 0.0
        END AS heat_risk,
        -- Temperature extreme risk (combination)
        CASE
            WHEN fs.min_value < 32 THEN
                CASE
                    WHEN fs.min_value < 20 THEN 100.0
                    WHEN fs.min_value < 28 THEN 75.0 + ((28 - fs.min_value) / 8.0) * 25.0
                    WHEN fs.min_value < 32 THEN 50.0 + ((32 - fs.min_value) / 4.0) * 25.0
                    ELSE 25.0
                END
            WHEN fs.max_value > 90 THEN
                CASE
                    WHEN fs.max_value > 100 THEN 100.0
                    WHEN fs.max_value > 95 THEN 75.0 + ((fs.max_value - 95) / 5.0) * 25.0
                    WHEN fs.max_value > 90 THEN 50.0 + ((fs.max_value - 90) / 5.0) * 25.0
                    ELSE 25.0
                END
            ELSE 0.0
        END AS temperature_extreme_risk
    FROM forecast_statistics fs
    WHERE fs.parameter_name = 'Temperature'
),
wind_risk_calculation AS (
    -- Sixth CTE: Calculate wind damage risk
    SELECT
        fs.policy_area_id,
        fs.policy_type,
        fs.forecast_day,
        fs.forecast_date,
        fs.avg_value AS avg_wind_speed,
        fs.max_value AS max_wind_speed,
        fs.p95_value AS p95_wind_speed,
        fs.p99_value AS p99_wind_speed,
        -- Wind damage risk (higher for stronger winds)
        CASE
            WHEN fs.max_value > 75 THEN 100.0  -- Hurricane-force winds
            WHEN fs.max_value > 58 THEN 75.0 + ((fs.max_value - 58) / 17.0) * 25.0  -- Tropical storm
            WHEN fs.max_value > 45 THEN 50.0 + ((fs.max_value - 45) / 13.0) * 25.0  -- Strong winds
            WHEN fs.max_value > 30 THEN 25.0 + ((fs.max_value - 30) / 15.0) * 25.0  -- Moderate winds
            ELSE (fs.max_value / 30.0) * 25.0
        END AS wind_damage_risk
    FROM forecast_statistics fs
    WHERE fs.parameter_name = 'WindSpeed'
),
flood_risk_calculation AS (
    -- Seventh CTE: Calculate flood risk (combination of precipitation and other factors)
    SELECT
        prc.policy_area_id,
        prc.policy_type,
        prc.forecast_day,
        prc.forecast_date,
        prc.avg_precipitation,
        prc.cumulative_precipitation_risk,
        -- Flood risk combines precipitation with other factors
        CASE
            WHEN prc.avg_precipitation > 50 THEN 100.0
            WHEN prc.avg_precipitation > 25 THEN 75.0 + ((prc.avg_precipitation - 25) / 25.0) * 25.0
            WHEN prc.avg_precipitation > 10 THEN 50.0 + ((prc.avg_precipitation - 10) / 15.0) * 25.0
            WHEN prc.avg_precipitation > 5 THEN 25.0 + ((prc.avg_precipitation - 5) / 5.0) * 25.0
            ELSE (prc.avg_precipitation / 5.0) * 25.0
        END AS flood_risk
    FROM precipitation_risk_calculation prc
),
combined_risk_factors AS (
    -- Eighth CTE: Combine all risk factors
    SELECT
        COALESCE(prc.policy_area_id, trc.policy_area_id, wrc.policy_area_id, frc.policy_area_id) AS policy_area_id,
        COALESCE(prc.policy_type, trc.policy_type, wrc.policy_type, frc.policy_type) AS policy_type,
        COALESCE(prc.forecast_day, trc.forecast_day, wrc.forecast_day, frc.forecast_day) AS forecast_day,
        COALESCE(prc.forecast_date, trc.forecast_date, wrc.forecast_date, frc.forecast_date) AS forecast_date,
        prc.cumulative_precipitation_risk,
        prc.extreme_event_probability,
        trc.freeze_risk,
        trc.heat_risk,
        trc.temperature_extreme_risk,
        wrc.wind_damage_risk,
        frc.flood_risk,
        -- Overall risk score (weighted combination)
        (
            COALESCE(prc.cumulative_precipitation_risk, 0) * 0.30 +
            COALESCE(trc.temperature_extreme_risk, 0) * 0.25 +
            COALESCE(wrc.wind_damage_risk, 0) * 0.20 +
            COALESCE(frc.flood_risk, 0) * 0.15 +
            COALESCE(prc.extreme_event_probability, 0) * 100 * 0.10
        ) AS overall_risk_score
    FROM precipitation_risk_calculation prc
    FULL OUTER JOIN temperature_risk_calculation trc ON (
        prc.policy_area_id = trc.policy_area_id
        AND prc.forecast_day = trc.forecast_day
        AND prc.forecast_date = trc.forecast_date
    )
    FULL OUTER JOIN wind_risk_calculation wrc ON (
        COALESCE(prc.policy_area_id, trc.policy_area_id) = wrc.policy_area_id
        AND COALESCE(prc.forecast_day, trc.forecast_day) = wrc.forecast_day
        AND COALESCE(prc.forecast_date, trc.forecast_date) = wrc.forecast_date
    )
    FULL OUTER JOIN flood_risk_calculation frc ON (
        COALESCE(prc.policy_area_id, trc.policy_area_id) = frc.policy_area_id
        AND COALESCE(prc.forecast_day, trc.forecast_day) = frc.forecast_day
        AND COALESCE(prc.forecast_date, trc.forecast_date) = frc.forecast_date
    )
),
risk_category_assignment AS (
    -- Ninth CTE: Assign risk categories
    SELECT
        crf.policy_area_id,
        crf.policy_type,
        crf.forecast_day,
        crf.forecast_date,
        ROUND(CAST(crf.cumulative_precipitation_risk AS NUMERIC), 2) AS cumulative_precipitation_risk,
        ROUND(CAST(crf.extreme_event_probability AS NUMERIC), 4) AS extreme_event_probability,
        ROUND(CAST(crf.freeze_risk AS NUMERIC), 2) AS freeze_risk,
        ROUND(CAST(crf.heat_risk AS NUMERIC), 2) AS heat_risk,
        ROUND(CAST(crf.temperature_extreme_risk AS NUMERIC), 2) AS temperature_extreme_risk,
        ROUND(CAST(crf.wind_damage_risk AS NUMERIC), 2) AS wind_damage_risk,
        ROUND(CAST(crf.flood_risk AS NUMERIC), 2) AS flood_risk,
        ROUND(CAST(crf.overall_risk_score AS NUMERIC), 2) AS overall_risk_score,
        -- Risk category classification
        CASE
            WHEN crf.overall_risk_score >= 75 THEN 'Extreme'
            WHEN crf.overall_risk_score >= 50 THEN 'Very High'
            WHEN crf.overall_risk_score >= 30 THEN 'High'
            WHEN crf.overall_risk_score >= 15 THEN 'Moderate'
            ELSE 'Low'
        END AS risk_category
    FROM combined_risk_factors crf
)
SELECT
    rca.policy_area_id,
    rca.policy_type,
    rca.forecast_day,
    rca.forecast_date,
    rca.cumulative_precipitation_risk,
    rca.extreme_event_probability,
    rca.freeze_risk,
    rca.heat_risk,
    rca.temperature_extreme_risk,
    rca.wind_damage_risk,
    rca.flood_risk,
    rca.overall_risk_score,
    rca.risk_category
FROM risk_category_assignment rca
WHERE rca.forecast_day BETWEEN 7 AND 14
    AND rca.forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
ORDER BY rca.policy_area_id, rca.forecast_day, rca.forecast_date
LIMIT 5000;
```

---

## Query 16: Insurance Rate Table Generation from Forecast Risk Factors {#query-16}

**Use Case:** **Insurance Underwriting - Dynamic Rate Table Calculation Based on 7-14 Day Forecasts**

**Description:** Generates insurance rate tables for December 3-17, 2025 period using risk factors calculated from 7-14 day forecasts. Calculates base rates, risk-adjusted rates, rate components, and rate tiers based on forecast-based risk scores.

**Business Value:** Enables dynamic pricing based on forecasted weather risks, allowing insurance companies to adjust rates proactively and optimize profitability.

**Purpose:** Complete rate table showing rates for each policy area, forecast day (7-14 days), and coverage type with risk-adjusted pricing.

**Business Value:** Enables dynamic pricing based on forecasted weather risks, allowing insurance companies to adjust rates proactively and optimize profitability.

**Complexity:** Multiple CTEs (9+ levels), rate calculations, risk factor integration, tier assignments, window functions, complex aggregations

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
risk_factors_base AS (
    -- Second CTE: Get risk factors from Query 31 results or calculate inline
    SELECT
        irf.risk_factor_id,
        irf.policy_area_id,
        irf.forecast_period_start,
        irf.forecast_period_end,
        irf.forecast_day,
        irf.forecast_date,
        irf.parameter_name,
        irf.overall_risk_score,
        irf.risk_category,
        irf.cumulative_precipitation_risk,
        irf.temperature_extreme_risk,
        irf.wind_damage_risk,
        irf.freeze_risk,
        irf.flood_risk,
        irf.extreme_event_probability,
        ipa.policy_type,
        ipa.coverage_type,
        ipa.base_rate_factor,
        ipa.risk_zone
    FROM insurance_risk_factors irf
    INNER JOIN insurance_policy_areas ipa ON irf.policy_area_id = ipa.policy_area_id
    WHERE irf.forecast_period_start = DATE '2025-12-03'
        AND irf.forecast_period_end = DATE '2025-12-17'
        AND irf.forecast_day BETWEEN 7 AND 14
        AND ipa.is_active = TRUE
),
base_rate_calculation AS (
    -- Third CTE: Calculate base rates by policy type
    SELECT
        rfb.policy_area_id,
        rfb.policy_type,
        rfb.coverage_type,
        rfb.forecast_day,
        rfb.forecast_date,
        rfb.base_rate_factor,
        rfb.risk_zone,
        -- Base rate by policy type (example rates in USD)
        CASE
            WHEN rfb.policy_type = 'Property' THEN 500.00
            WHEN rfb.policy_type = 'Crop' THEN 300.00
            WHEN rfb.policy_type = 'Auto' THEN 800.00
            WHEN rfb.policy_type = 'Marine' THEN 1200.00
            WHEN rfb.policy_type = 'General Liability' THEN 1000.00
            ELSE 600.00
        END AS base_rate,
        rfb.overall_risk_score,
        rfb.risk_category,
        rfb.cumulative_precipitation_risk,
        rfb.temperature_extreme_risk,
        rfb.wind_damage_risk,
        rfb.freeze_risk,
        rfb.flood_risk,
        rfb.extreme_event_probability
    FROM risk_factors_base rfb
),
risk_component_calculation AS (
    -- Fourth CTE: Calculate individual risk components
    SELECT
        brc.policy_area_id,
        brc.policy_type,
        brc.coverage_type,
        brc.forecast_day,
        brc.forecast_date,
        brc.base_rate,
        brc.base_rate_factor,
        brc.risk_zone,
        brc.overall_risk_score,
        brc.risk_category,
        -- Risk components (as dollar amounts)
        (brc.base_rate * brc.cumulative_precipitation_risk / 100.0) * 0.30 AS precipitation_risk_component,
        (brc.base_rate * brc.temperature_extreme_risk / 100.0) * 0.25 AS temperature_risk_component,
        (brc.base_rate * brc.wind_damage_risk / 100.0) * 0.20 AS wind_risk_component,
        (brc.base_rate * brc.freeze_risk / 100.0) * 0.15 AS freeze_risk_component,
        (brc.base_rate * brc.flood_risk / 100.0) * 0.10 AS flood_risk_component,
        (brc.base_rate * brc.extreme_event_probability) * 0.10 AS extreme_event_component,
        -- Risk multiplier (how much to adjust base rate)
        CASE
            WHEN brc.overall_risk_score >= 75 THEN 2.50  -- Extreme risk: 2.5x base rate
            WHEN brc.overall_risk_score >= 50 THEN 2.00  -- Very High: 2.0x
            WHEN brc.overall_risk_score >= 30 THEN 1.50  -- High: 1.5x
            WHEN brc.overall_risk_score >= 15 THEN 1.25  -- Moderate: 1.25x
            ELSE 1.00  -- Low: 1.0x (no adjustment)
        END AS risk_multiplier
    FROM base_rate_calculation brc
),
rate_tier_assignment AS (
    -- Fifth CTE: Assign rate tiers based on risk
    SELECT
        rcc.policy_area_id,
        rcc.policy_type,
        rcc.coverage_type,
        rcc.forecast_day,
        rcc.forecast_date,
        rcc.base_rate,
        rcc.base_rate_factor,
        rcc.risk_zone,
        rcc.overall_risk_score,
        rcc.risk_category,
        rcc.precipitation_risk_component,
        rcc.temperature_risk_component,
        rcc.wind_risk_component,
        rcc.freeze_risk_component,
        rcc.flood_risk_component,
        rcc.extreme_event_component,
        rcc.risk_multiplier,
        -- Rate tier assignment
        CASE
            WHEN rcc.overall_risk_score >= 75 THEN 'High Risk'
            WHEN rcc.overall_risk_score >= 50 THEN 'Substandard'
            WHEN rcc.overall_risk_score >= 30 THEN 'Standard'
            WHEN rcc.overall_risk_score >= 15 THEN 'Preferred'
            ELSE 'Preferred Plus'
        END AS rate_tier,
        -- Rate category
        CASE
            WHEN rcc.overall_risk_score >= 75 THEN 'Very High'
            WHEN rcc.overall_risk_score >= 50 THEN 'High'
            WHEN rcc.overall_risk_score >= 30 THEN 'Moderate'
            WHEN rcc.overall_risk_score >= 15 THEN 'Low'
            ELSE 'Very Low'
        END AS rate_category
    FROM risk_component_calculation rcc
),
risk_adjusted_rate_calculation AS (
    -- Sixth CTE: Calculate risk-adjusted rates
    SELECT
        rta.policy_area_id,
        rta.policy_type,
        rta.coverage_type,
        rta.forecast_day,
        rta.forecast_date,
        rta.base_rate,
        rta.base_rate_factor,
        rta.risk_zone,
        rta.overall_risk_score,
        rta.risk_category,
        ROUND(CAST(rta.precipitation_risk_component AS NUMERIC), 2) AS precipitation_risk_component,
        ROUND(CAST(rta.temperature_risk_component AS NUMERIC), 2) AS temperature_risk_component,
        ROUND(CAST(rta.wind_risk_component AS NUMERIC), 2) AS wind_risk_component,
        ROUND(CAST(rta.freeze_risk_component AS NUMERIC), 2) AS freeze_risk_component,
        ROUND(CAST(rta.flood_risk_component AS NUMERIC), 2) AS flood_risk_component,
        ROUND(CAST(rta.extreme_event_component AS NUMERIC), 2) AS extreme_event_component,
        rta.risk_multiplier,
        rta.rate_tier,
        rta.rate_category,
        -- Base component (always present)
        rta.base_rate * rta.base_rate_factor AS base_component,
        -- Total risk components
        (
            rta.precipitation_risk_component +
            rta.temperature_risk_component +
            rta.wind_risk_component +
            rta.freeze_risk_component +
            rta.flood_risk_component +
            rta.extreme_event_component
        ) AS total_risk_components,
        -- Risk-adjusted rate
        (
            (rta.base_rate * rta.base_rate_factor) +
            (
                rta.precipitation_risk_component +
                rta.temperature_risk_component +
                rta.wind_risk_component +
                rta.freeze_risk_component +
                rta.flood_risk_component +
                rta.extreme_event_component
            )
        ) * rta.risk_multiplier AS risk_adjusted_rate
    FROM rate_tier_assignment rta
),
confidence_calculation AS (
    -- Seventh CTE: Calculate confidence levels based on forecast day
    SELECT
        rarc.policy_area_id,
        rarc.policy_type,
        rarc.coverage_type,
        rarc.forecast_day,
        rarc.forecast_date,
        rarc.base_rate,
        rarc.base_component,
        rarc.precipitation_risk_component,
        rarc.temperature_risk_component,
        rarc.wind_risk_component,
        rarc.freeze_risk_component,
        rarc.flood_risk_component,
        rarc.extreme_event_component,
        rarc.total_risk_components,
        rarc.risk_multiplier,
        rarc.risk_adjusted_rate,
        rarc.rate_tier,
        rarc.rate_category,
        rarc.overall_risk_score,
        -- Confidence level decreases with forecast day (7 days = higher confidence, 14 days = lower)
        CASE
            WHEN rarc.forecast_day <= 8 THEN 90.0  -- High confidence for 7-8 days
            WHEN rarc.forecast_day <= 10 THEN 75.0  -- Moderate-high for 9-10 days
            WHEN rarc.forecast_day <= 12 THEN 60.0  -- Moderate for 11-12 days
            ELSE 45.0  -- Lower confidence for 13-14 days
        END AS confidence_level
    FROM risk_adjusted_rate_calculation rarc
),
final_rate_table AS (
    -- Eighth CTE: Final rate table with all components
    SELECT
        cc.policy_area_id,
        cc.policy_type,
        cc.coverage_type,
        cc.forecast_day,
        cc.forecast_date,
        DATE '2025-12-03' AS forecast_period_start,
        DATE '2025-12-17' AS forecast_period_end,
        cc.base_rate,
        ROUND(CAST(cc.base_component AS NUMERIC), 2) AS base_component,
        cc.precipitation_risk_component,
        cc.temperature_risk_component,
        cc.wind_risk_component,
        cc.freeze_risk_component,
        cc.flood_risk_component,
        cc.extreme_event_component,
        ROUND(CAST(cc.total_risk_components AS NUMERIC), 2) AS total_risk_components,
        ROUND(CAST(cc.risk_multiplier AS NUMERIC), 3) AS risk_multiplier,
        ROUND(CAST(cc.risk_adjusted_rate AS NUMERIC), 2) AS risk_adjusted_rate,
        cc.rate_tier,
        cc.rate_category,
        ROUND(CAST(cc.overall_risk_score AS NUMERIC), 2) AS overall_risk_score,
        ROUND(CAST(cc.confidence_level AS NUMERIC), 2) AS confidence_level,
        'Forecast-Based' AS calculation_method,
        DATE '2025-12-03' AS effective_date,
        DATE '2025-12-17' AS expiration_date
    FROM confidence_calculation cc
)
SELECT
    policy_area_id,
    policy_type,
    coverage_type,
    forecast_day,
    forecast_date,
    forecast_period_start,
    forecast_period_end,
    base_rate,
    base_component,
    precipitation_risk_component,
    temperature_risk_component,
    wind_risk_component,
    freeze_risk_component,
    flood_risk_component,
    extreme_event_component,
    total_risk_components,
    risk_multiplier,
    risk_adjusted_rate,
    rate_tier,
    rate_category,
    overall_risk_score,
    confidence_level,
    calculation_method,
    effective_date,
    expiration_date
FROM final_rate_table
WHERE forecast_day BETWEEN 7 AND 14
    AND forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
ORDER BY policy_area_id, forecast_day, forecast_date
LIMIT 10000;
```

---

## Query 17: Rate Table Comparison Across 7-14 Day Forecasts {#query-17}

**Use Case:** **Insurance Underwriting - Multi-Day Forecast Rate Comparison for Optimal Rate Selection**

**Description:** Compares insurance rates across all forecast days (7-14 days ahead) for December 3-17, 2025 period. Calculates rate statistics, volatility, trends, and recommends optimal forecast day for rate determination.

**Business Value:** Rate comparison report showing rates by forecast day with volatility metrics and recommended rates.

**Purpose:** Enables insurance companies to select optimal forecast day balancing accuracy (shorter forecast) with planning horizon (longer forecast).

**Complexity:** Multiple CTEs (7+ levels), rate aggregation, volatility calculations, trend analysis, window functions, statistical analysis

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
rate_tables_by_day AS (
    -- Second CTE: Get rates for each forecast day (7-14)
    SELECT
        irt.policy_area_id,
        irt.policy_type,
        irt.coverage_type,
        irt.forecast_period_start,
        irt.forecast_period_end,
        irt.forecast_day,
        irt.forecast_date,
        irt.base_rate,
        irt.risk_adjusted_rate,
        irt.risk_multiplier,
        irt.rate_tier,
        irt.rate_category,
        irt.confidence_level
    FROM insurance_rate_tables irt
    WHERE irt.forecast_period_start = DATE '2025-12-03'
        AND irt.forecast_period_end = DATE '2025-12-17'
        AND irt.forecast_day BETWEEN 7 AND 14
        AND irt.forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
),
rates_by_forecast_day AS (
    -- Third CTE: Aggregate rates by forecast day
    SELECT
        rtbd.policy_area_id,
        rtbd.policy_type,
        rtbd.coverage_type,
        rtbd.forecast_period_start,
        rtbd.forecast_period_end,
        rtbd.forecast_day,
        COUNT(*) AS rate_count,
        MIN(rtbd.risk_adjusted_rate) AS min_rate,
        MAX(rtbd.risk_adjusted_rate) AS max_rate,
        AVG(rtbd.risk_adjusted_rate) AS avg_rate,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rtbd.risk_adjusted_rate) AS median_rate,
        STDDEV(rtbd.risk_adjusted_rate) AS rate_stddev,
        VARIANCE(rtbd.risk_adjusted_rate) AS rate_variance,
        AVG(rtbd.confidence_level) AS avg_confidence_level,
        AVG(rtbd.risk_multiplier) AS avg_risk_multiplier
    FROM rate_tables_by_day rtbd
    GROUP BY
        rtbd.policy_area_id,
        rtbd.policy_type,
        rtbd.coverage_type,
        rtbd.forecast_period_start,
        rtbd.forecast_period_end,
        rtbd.forecast_day
),
rate_statistics AS (
    -- Fourth CTE: Calculate comprehensive statistics
    SELECT
        rbfd.policy_area_id,
        rbfd.policy_type,
        rbfd.coverage_type,
        rbfd.forecast_period_start,
        rbfd.forecast_period_end,
        rbfd.forecast_day,
        rbfd.rate_count,
        ROUND(CAST(rbfd.min_rate AS NUMERIC), 2) AS min_rate,
        ROUND(CAST(rbfd.max_rate AS NUMERIC), 2) AS max_rate,
        ROUND(CAST(rbfd.avg_rate AS NUMERIC), 2) AS avg_rate,
        ROUND(CAST(rbfd.median_rate AS NUMERIC), 2) AS median_rate,
        ROUND(CAST(rbfd.rate_stddev AS NUMERIC), 2) AS rate_stddev,
        ROUND(CAST(rbfd.rate_variance AS NUMERIC), 2) AS rate_variance,
        ROUND(CAST(rbfd.avg_confidence_level AS NUMERIC), 2) AS avg_confidence_level,
        ROUND(CAST(rbfd.avg_risk_multiplier AS NUMERIC), 3) AS avg_risk_multiplier,
        -- Rate range
        rbfd.max_rate - rbfd.min_rate AS rate_range,
        -- Coefficient of variation (volatility measure)
        CASE
            WHEN rbfd.avg_rate != 0 THEN
                (rbfd.rate_stddev / ABS(rbfd.avg_rate)) * 100
            ELSE NULL
        END AS rate_volatility_percent
    FROM rates_by_forecast_day rbfd
),
rate_trend_analysis AS (
    -- Fifth CTE: Analyze rate trends across forecast days
    SELECT
        rs.policy_area_id,
        rs.policy_type,
        rs.coverage_type,
        rs.forecast_period_start,
        rs.forecast_period_end,
        rs.forecast_day,
        rs.rate_count,
        rs.min_rate,
        rs.max_rate,
        rs.avg_rate,
        rs.median_rate,
        rs.rate_stddev,
        rs.rate_range,
        rs.rate_volatility_percent,
        rs.avg_confidence_level,
        rs.avg_risk_multiplier,
        -- Compare with previous forecast day
        LAG(rs.avg_rate, 1) OVER (
            PARTITION BY rs.policy_area_id, rs.policy_type, rs.coverage_type
            ORDER BY rs.forecast_day
        ) AS prev_day_avg_rate,
        -- Rate change from previous day
        rs.avg_rate - LAG(rs.avg_rate, 1) OVER (
            PARTITION BY rs.policy_area_id, rs.policy_type, rs.coverage_type
            ORDER BY rs.forecast_day
        ) AS rate_change_from_prev_day,
        -- Rate trend
        CASE
            WHEN LAG(rs.avg_rate, 1) OVER (
                PARTITION BY rs.policy_area_id, rs.policy_type, rs.coverage_type
                ORDER BY rs.forecast_day
            ) IS NOT NULL THEN
                CASE
                    WHEN rs.avg_rate > LAG(rs.avg_rate, 1) OVER (
                        PARTITION BY rs.policy_area_id, rs.policy_type, rs.coverage_type
                        ORDER BY rs.forecast_day
                    ) * 1.05 THEN 'Increasing'
                    WHEN rs.avg_rate < LAG(rs.avg_rate, 1) OVER (
                        PARTITION BY rs.policy_area_id, rs.policy_type, rs.coverage_type
                        ORDER BY rs.forecast_day
                    ) * 0.95 THEN 'Decreasing'
                    ELSE 'Stable'
                END
            ELSE NULL
        END AS rate_trend,
        -- Moving average (3-day)
        AVG(rs.avg_rate) OVER (
            PARTITION BY rs.policy_area_id, rs.policy_type, rs.coverage_type
            ORDER BY rs.forecast_day
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS moving_avg_3day
    FROM rate_statistics rs
),
optimal_rate_selection AS (
    -- Sixth CTE: Determine optimal rate and forecast day
    SELECT
        rta.policy_area_id,
        rta.policy_type,
        rta.coverage_type,
        rta.forecast_period_start,
        rta.forecast_period_end,
        rta.forecast_day,
        rta.rate_count,
        rta.min_rate,
        rta.max_rate,
        rta.avg_rate,
        rta.median_rate,
        rta.rate_stddev,
        rta.rate_range,
        ROUND(CAST(rta.rate_volatility_percent AS NUMERIC), 2) AS rate_volatility_percent,
        rta.avg_confidence_level,
        rta.avg_risk_multiplier,
        ROUND(CAST(rta.prev_day_avg_rate AS NUMERIC), 2) AS prev_day_avg_rate,
        ROUND(CAST(rta.rate_change_from_prev_day AS NUMERIC), 2) AS rate_change_from_prev_day,
        rta.rate_trend,
        ROUND(CAST(rta.moving_avg_3day AS NUMERIC), 2) AS moving_avg_3day,
        -- Score for optimal rate selection (higher confidence + lower volatility = better)
        (
            (rta.avg_confidence_level / 100.0) * 50.0 +  -- Confidence component (50% weight)
            GREATEST(0, 50.0 - (rta.rate_volatility_percent / 2.0))  -- Low volatility component (50% weight)
        ) AS optimal_rate_score
    FROM rate_trend_analysis rta
),
recommended_rates AS (
    -- Seventh CTE: Select recommended rates
    SELECT
        ors.policy_area_id,
        ors.policy_type,
        ors.coverage_type,
        ors.forecast_period_start,
        ors.forecast_period_end,
        ors.forecast_day,
        ors.rate_count,
        ors.min_rate,
        ors.max_rate,
        ors.avg_rate,
        ors.median_rate,
        ors.rate_stddev,
        ors.rate_range,
        ors.rate_volatility_percent,
        ors.avg_confidence_level,
        ors.avg_risk_multiplier,
        ors.prev_day_avg_rate,
        ors.rate_change_from_prev_day,
        ors.rate_trend,
        ors.moving_avg_3day,
        ors.optimal_rate_score,
        -- Recommended rate (use median for stability)
        ors.median_rate AS recommended_rate,
        -- Rank by optimal score
        ROW_NUMBER() OVER (
            PARTITION BY ors.policy_area_id, ors.policy_type, ors.coverage_type
            ORDER BY ors.optimal_rate_score DESC
        ) AS optimal_day_rank
    FROM optimal_rate_selection ors
)
SELECT
    policy_area_id,
    policy_type,
    coverage_type,
    forecast_period_start,
    forecast_period_end,
    forecast_day,
    rate_count,
    min_rate,
    max_rate,
    avg_rate,
    median_rate,
    rate_stddev,
    rate_range,
    rate_volatility_percent,
    avg_confidence_level,
    avg_risk_multiplier,
    prev_day_avg_rate,
    rate_change_from_prev_day,
    rate_trend,
    moving_avg_3day,
    ROUND(CAST(optimal_rate_score AS NUMERIC), 2) AS optimal_rate_score,
    recommended_rate,
    optimal_day_rank,
    CASE
        WHEN optimal_day_rank = 1 THEN 'Recommended'
        ELSE 'Alternative'
    END AS recommendation_status
FROM recommended_rates
WHERE forecast_day BETWEEN 7 AND 14
ORDER BY policy_area_id, policy_type, coverage_type, forecast_day
LIMIT 5000;
```

---

## Query 18: Historical Claims Validation Against Forecast Risk Factors {#query-18}

**Use Case:** **Insurance Underwriting - Forecast Accuracy Validation Using Historical Claims Data**

**Description:** Validates forecast-based risk factors against historical claims data for December 3-17, 2025 period. Compares forecast risk scores with actual claims to assess forecast accuracy and improve rate modeling.

**Business Value:** Enables insurance companies to validate and improve forecast-based rate models using historical data, improving underwriting accuracy over time.

**Purpose:** Validation report showing forecast risk vs actual claims with accuracy metrics and improvement recommendations.

**Business Value:** Enables insurance companies to validate and improve forecast-based rate models using historical data, improving underwriting accuracy over time.

**Complexity:** Multiple CTEs (8+ levels), historical data joins, forecast accuracy calculations, error analysis, window functions, statistical comparisons

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
historical_claims AS (
    -- Second CTE: Get historical claims for validation period
    SELECT
        ich.claim_id,
        ich.policy_area_id,
        ich.claim_date,
        ich.loss_date,
        ich.policy_type,
        ich.coverage_type,
        ich.claim_type,
        ich.loss_amount,
        ich.claim_status,
        ich.weather_event_type,
        ich.weather_event_date,
        ich.temperature_at_loss,
        ich.precipitation_at_loss,
        ich.wind_speed_at_loss,
        ich.forecast_available,
        ich.forecast_day,
        ich.forecast_error
    FROM insurance_claims_history ich
    WHERE ich.loss_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
        AND ich.claim_status = 'Closed'
),
forecast_risk_factors AS (
    -- Third CTE: Get forecast risk factors for same period
    SELECT
        irf.risk_factor_id,
        irf.policy_area_id,
        irf.forecast_period_start,
        irf.forecast_period_end,
        irf.forecast_day,
        irf.forecast_date,
        irf.parameter_name,
        irf.overall_risk_score,
        irf.risk_category,
        irf.cumulative_precipitation_risk,
        irf.temperature_extreme_risk,
        irf.wind_damage_risk,
        irf.freeze_risk,
        irf.flood_risk,
        irf.extreme_event_probability
    FROM insurance_risk_factors irf
    WHERE irf.forecast_period_start = DATE '2025-12-03'
        AND irf.forecast_period_end = DATE '2025-12-17'
        AND irf.forecast_day BETWEEN 7 AND 14
),
claims_risk_matching AS (
    -- Fourth CTE: Match claims with forecast risk factors
    SELECT
        hc.claim_id,
        hc.policy_area_id,
        hc.loss_date,
        hc.policy_type,
        hc.coverage_type,
        hc.claim_type,
        hc.loss_amount,
        hc.weather_event_type,
        hc.forecast_day,
        frf.forecast_date,
        frf.forecast_day AS forecast_day_ahead,
        frf.overall_risk_score,
        frf.risk_category,
        frf.cumulative_precipitation_risk,
        frf.temperature_extreme_risk,
        frf.wind_damage_risk,
        frf.freeze_risk,
        frf.flood_risk,
        frf.extreme_event_probability,
        -- Days between forecast and loss
        (hc.loss_date::date - frf.forecast_date::date) AS days_between_forecast_loss
    FROM historical_claims hc
    LEFT JOIN forecast_risk_factors frf ON (
        hc.policy_area_id = frf.policy_area_id
        AND hc.loss_date = frf.forecast_date
    )
),
claims_risk_analysis AS (
    -- Fifth CTE: Analyze claims vs forecast risk
    SELECT
        crm.claim_id,
        crm.policy_area_id,
        crm.loss_date,
        crm.policy_type,
        crm.coverage_type,
        crm.claim_type,
        crm.loss_amount,
        crm.weather_event_type,
        crm.forecast_day_ahead,
        crm.overall_risk_score,
        crm.risk_category,
        crm.cumulative_precipitation_risk,
        crm.temperature_extreme_risk,
        crm.wind_damage_risk,
        crm.freeze_risk,
        crm.flood_risk,
        crm.extreme_event_probability,
        crm.days_between_forecast_loss,
        -- Expected risk category based on claim type
        CASE
            WHEN crm.weather_event_type IN ('Flood', 'Heavy Rain') THEN
                CASE
                    WHEN crm.loss_amount > 100000 THEN 'Extreme'
                    WHEN crm.loss_amount > 50000 THEN 'Very High'
                    WHEN crm.loss_amount > 25000 THEN 'High'
                    WHEN crm.loss_amount > 10000 THEN 'Moderate'
                    ELSE 'Low'
                END
            WHEN crm.weather_event_type IN ('Freeze', 'Frost') THEN
                CASE
                    WHEN crm.loss_amount > 100000 THEN 'Extreme'
                    WHEN crm.loss_amount > 50000 THEN 'Very High'
                    WHEN crm.loss_amount > 25000 THEN 'High'
                    WHEN crm.loss_amount > 10000 THEN 'Moderate'
                    ELSE 'Low'
                END
            WHEN crm.weather_event_type IN ('Wind', 'Hurricane', 'Tornado') THEN
                CASE
                    WHEN crm.loss_amount > 100000 THEN 'Extreme'
                    WHEN crm.loss_amount > 50000 THEN 'Very High'
                    WHEN crm.loss_amount > 25000 THEN 'High'
                    WHEN crm.loss_amount > 10000 THEN 'Moderate'
                    ELSE 'Low'
                END
            ELSE 'Moderate'
        END AS expected_risk_category,
        -- Forecast accuracy (risk category match)
        CASE
            WHEN crm.risk_category = CASE
                WHEN crm.weather_event_type IN ('Flood', 'Heavy Rain') THEN
                    CASE
                        WHEN crm.loss_amount > 100000 THEN 'Extreme'
                        WHEN crm.loss_amount > 50000 THEN 'Very High'
                        WHEN crm.loss_amount > 25000 THEN 'High'
                        WHEN crm.loss_amount > 10000 THEN 'Moderate'
                        ELSE 'Low'
                    END
                WHEN crm.weather_event_type IN ('Freeze', 'Frost') THEN
                    CASE
                        WHEN crm.loss_amount > 100000 THEN 'Extreme'
                        WHEN crm.loss_amount > 50000 THEN 'Very High'
                        WHEN crm.loss_amount > 25000 THEN 'High'
                        WHEN crm.loss_amount > 10000 THEN 'Moderate'
                        ELSE 'Low'
                    END
                WHEN crm.weather_event_type IN ('Wind', 'Hurricane', 'Tornado') THEN
                    CASE
                        WHEN crm.loss_amount > 100000 THEN 'Extreme'
                        WHEN crm.loss_amount > 50000 THEN 'Very High'
                        WHEN crm.loss_amount > 25000 THEN 'High'
                        WHEN crm.loss_amount > 10000 THEN 'Moderate'
                        ELSE 'Low'
                    END
                ELSE 'Moderate'
            END THEN 'Accurate'
            ELSE 'Inaccurate'
        END AS forecast_accuracy
    FROM claims_risk_matching crm
    WHERE crm.overall_risk_score IS NOT NULL
),
accuracy_statistics AS (
    -- Sixth CTE: Calculate accuracy statistics
    SELECT
        cra.policy_area_id,
        cra.policy_type,
        cra.coverage_type,
        cra.forecast_day_ahead,
        COUNT(*) AS total_claims,
        COUNT(CASE WHEN cra.forecast_accuracy = 'Accurate' THEN 1 END) AS accurate_forecasts,
        COUNT(CASE WHEN cra.forecast_accuracy = 'Inaccurate' THEN 1 END) AS inaccurate_forecasts,
        -- Accuracy rate
        (COUNT(CASE WHEN cra.forecast_accuracy = 'Accurate' THEN 1 END)::NUMERIC / COUNT(*)::NUMERIC) * 100 AS accuracy_rate,
        -- Average risk scores
        AVG(cra.overall_risk_score) AS avg_forecast_risk_score,
        AVG(cra.loss_amount) AS avg_loss_amount,
        -- Risk category distribution
        COUNT(CASE WHEN cra.risk_category = 'Extreme' THEN 1 END) AS extreme_risk_count,
        COUNT(CASE WHEN cra.risk_category = 'Very High' THEN 1 END) AS very_high_risk_count,
        COUNT(CASE WHEN cra.risk_category = 'High' THEN 1 END) AS high_risk_count,
        COUNT(CASE WHEN cra.risk_category = 'Moderate' THEN 1 END) AS moderate_risk_count,
        COUNT(CASE WHEN cra.risk_category = 'Low' THEN 1 END) AS low_risk_count
    FROM claims_risk_analysis cra
    GROUP BY
        cra.policy_area_id,
        cra.policy_type,
        cra.coverage_type,
        cra.forecast_day_ahead
),
forecast_improvement_analysis AS (
    -- Seventh CTE: Analyze forecast improvement opportunities
    SELECT
        ast.policy_area_id,
        ast.policy_type,
        ast.coverage_type,
        ast.forecast_day_ahead,
        ast.total_claims,
        ast.accurate_forecasts,
        ast.inaccurate_forecasts,
        ROUND(CAST(ast.accuracy_rate AS NUMERIC), 2) AS accuracy_rate,
        ROUND(CAST(ast.avg_forecast_risk_score AS NUMERIC), 2) AS avg_forecast_risk_score,
        ROUND(CAST(ast.avg_loss_amount AS NUMERIC), 2) AS avg_loss_amount,
        ast.extreme_risk_count,
        ast.very_high_risk_count,
        ast.high_risk_count,
        ast.moderate_risk_count,
        ast.low_risk_count,
        -- Improvement recommendation
        CASE
            WHEN ast.accuracy_rate < 50 THEN 'High Priority - Significant Improvement Needed'
            WHEN ast.accuracy_rate < 70 THEN 'Medium Priority - Moderate Improvement Needed'
            WHEN ast.accuracy_rate < 85 THEN 'Low Priority - Minor Improvement Needed'
            ELSE 'Acceptable - Monitor Performance'
        END AS improvement_priority,
        -- Forecast day performance
        CASE
            WHEN ast.forecast_day_ahead <= 8 AND ast.accuracy_rate >= 80 THEN 'Optimal Forecast Day'
            WHEN ast.forecast_day_ahead <= 10 AND ast.accuracy_rate >= 70 THEN 'Good Forecast Day'
            WHEN ast.forecast_day_ahead <= 12 AND ast.accuracy_rate >= 60 THEN 'Acceptable Forecast Day'
            ELSE 'Review Forecast Day'
        END AS forecast_day_assessment
    FROM accuracy_statistics ast
)
SELECT
    policy_area_id,
    policy_type,
    coverage_type,
    forecast_day_ahead,
    total_claims,
    accurate_forecasts,
    inaccurate_forecasts,
    accuracy_rate,
    avg_forecast_risk_score,
    avg_loss_amount,
    extreme_risk_count,
    very_high_risk_count,
    high_risk_count,
    moderate_risk_count,
    low_risk_count,
    improvement_priority,
    forecast_day_assessment
FROM forecast_improvement_analysis
WHERE forecast_day_ahead BETWEEN 7 AND 14
ORDER BY policy_area_id, policy_type, coverage_type, forecast_day_ahead
LIMIT 2000;
```

---

## Query 19: Rate Volatility and Stability Analysis {#query-19}

**Use Case:** **Insurance Underwriting - Rate Stability Assessment for Pricing Consistency**

**Description:** Analyzes rate volatility and stability across 7-14 day forecasts for December 3-17, 2025. Identifies areas with high rate volatility and recommends stable pricing strategies.

**Business Value:** Rate volatility analysis report with stability metrics and recommendations for consistent pricing.

**Purpose:** Helps insurance companies identify pricing inconsistencies and implement stable pricing strategies, improving customer trust and retention.

**Complexity:** Multiple CTEs (6+ levels), volatility calculations, stability metrics, trend analysis, window functions, statistical analysis

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
rate_data AS (
    -- Second CTE: Get rate data for analysis
    SELECT
        irt.policy_area_id,
        irt.policy_type,
        irt.coverage_type,
        irt.forecast_day,
        irt.forecast_date,
        irt.base_rate,
        irt.risk_adjusted_rate,
        irt.risk_multiplier,
        irt.confidence_level
    FROM insurance_rate_tables irt
    WHERE irt.forecast_period_start = DATE '2025-12-03'
        AND irt.forecast_period_end = DATE '2025-12-17'
        AND irt.forecast_day BETWEEN 7 AND 14
        AND irt.forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
),
rate_volatility_calculation AS (
    -- Third CTE: Calculate rate volatility metrics
    SELECT
        rd.policy_area_id,
        rd.policy_type,
        rd.coverage_type,
        rd.forecast_day,
        COUNT(*) AS rate_observations,
        MIN(rd.risk_adjusted_rate) AS min_rate,
        MAX(rd.risk_adjusted_rate) AS max_rate,
        AVG(rd.risk_adjusted_rate) AS avg_rate,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rd.risk_adjusted_rate) AS median_rate,
        STDDEV(rd.risk_adjusted_rate) AS rate_stddev,
        VARIANCE(rd.risk_adjusted_rate) AS rate_variance,
        -- Coefficient of variation (volatility measure)
        CASE
            WHEN AVG(rd.risk_adjusted_rate) != 0 THEN
                (STDDEV(rd.risk_adjusted_rate) / ABS(AVG(rd.risk_adjusted_rate))) * 100
            ELSE NULL
        END AS coefficient_of_variation,
        -- Range as percentage of average
        CASE
            WHEN AVG(rd.risk_adjusted_rate) != 0 THEN
                ((MAX(rd.risk_adjusted_rate) - MIN(rd.risk_adjusted_rate)) / ABS(AVG(rd.risk_adjusted_rate))) * 100
            ELSE NULL
        END AS range_percentage,
        AVG(rd.confidence_level) AS avg_confidence_level
    FROM rate_data rd
    GROUP BY
        rd.policy_area_id,
        rd.policy_type,
        rd.coverage_type,
        rd.forecast_day
),
rate_stability_metrics AS (
    -- Fourth CTE: Calculate stability metrics
    SELECT
        rvc.policy_area_id,
        rvc.policy_type,
        rvc.coverage_type,
        rvc.forecast_day,
        rvc.rate_observations,
        ROUND(CAST(rvc.min_rate AS NUMERIC), 2) AS min_rate,
        ROUND(CAST(rvc.max_rate AS NUMERIC), 2) AS max_rate,
        ROUND(CAST(rvc.avg_rate AS NUMERIC), 2) AS avg_rate,
        ROUND(CAST(rvc.median_rate AS NUMERIC), 2) AS median_rate,
        ROUND(CAST(rvc.rate_stddev AS NUMERIC), 2) AS rate_stddev,
        ROUND(CAST(rvc.coefficient_of_variation AS NUMERIC), 2) AS coefficient_of_variation,
        ROUND(CAST(rvc.range_percentage AS NUMERIC), 2) AS range_percentage,
        ROUND(CAST(rvc.avg_confidence_level AS NUMERIC), 2) AS avg_confidence_level,
        -- Stability score (lower volatility = higher stability)
        CASE
            WHEN rvc.coefficient_of_variation IS NOT NULL THEN
                100.0 - LEAST(rvc.coefficient_of_variation, 100.0)
            ELSE 50.0
        END AS stability_score,
        -- Volatility classification
        CASE
            WHEN rvc.coefficient_of_variation > 30 THEN 'Very High Volatility'
            WHEN rvc.coefficient_of_variation > 20 THEN 'High Volatility'
            WHEN rvc.coefficient_of_variation > 10 THEN 'Moderate Volatility'
            WHEN rvc.coefficient_of_variation > 5 THEN 'Low Volatility'
            ELSE 'Very Low Volatility'
        END AS volatility_classification
    FROM rate_volatility_calculation rvc
),
cross_day_volatility AS (
    -- Fifth CTE: Analyze volatility across forecast days
    SELECT
        rsm.policy_area_id,
        rsm.policy_type,
        rsm.coverage_type,
        rsm.forecast_day,
        rsm.rate_observations,
        rsm.min_rate,
        rsm.max_rate,
        rsm.avg_rate,
        rsm.median_rate,
        rsm.rate_stddev,
        rsm.coefficient_of_variation,
        rsm.range_percentage,
        rsm.avg_confidence_level,
        rsm.stability_score,
        rsm.volatility_classification,
        -- Compare with other forecast days
        AVG(rsm.coefficient_of_variation) OVER (
            PARTITION BY rsm.policy_area_id, rsm.policy_type, rsm.coverage_type
        ) AS avg_volatility_across_days,
        MIN(rsm.coefficient_of_variation) OVER (
            PARTITION BY rsm.policy_area_id, rsm.policy_type, rsm.coverage_type
        ) AS min_volatility_across_days,
        MAX(rsm.coefficient_of_variation) OVER (
            PARTITION BY rsm.policy_area_id, rsm.policy_type, rsm.coverage_type
        ) AS max_volatility_across_days,
        -- Rate change from previous forecast day
        rsm.avg_rate - LAG(rsm.avg_rate, 1) OVER (
            PARTITION BY rsm.policy_area_id, rsm.policy_type, rsm.coverage_type
            ORDER BY rsm.forecast_day
        ) AS rate_change_from_prev_day
    FROM rate_stability_metrics rsm
),
stability_recommendations AS (
    -- Sixth CTE: Generate stability recommendations
    SELECT
        cdv.policy_area_id,
        cdv.policy_type,
        cdv.coverage_type,
        cdv.forecast_day,
        cdv.rate_observations,
        cdv.min_rate,
        cdv.max_rate,
        cdv.avg_rate,
        cdv.median_rate,
        cdv.rate_stddev,
        cdv.coefficient_of_variation,
        cdv.range_percentage,
        cdv.avg_confidence_level,
        ROUND(CAST(cdv.stability_score AS NUMERIC), 2) AS stability_score,
        cdv.volatility_classification,
        ROUND(CAST(cdv.avg_volatility_across_days AS NUMERIC), 2) AS avg_volatility_across_days,
        ROUND(CAST(cdv.min_volatility_across_days AS NUMERIC), 2) AS min_volatility_across_days,
        ROUND(CAST(cdv.max_volatility_across_days AS NUMERIC), 2) AS max_volatility_across_days,
        ROUND(CAST(cdv.rate_change_from_prev_day AS NUMERIC), 2) AS rate_change_from_prev_day,
        -- Recommended rate (use median for stability)
        cdv.median_rate AS recommended_stable_rate,
        -- Stability recommendation
        CASE
            WHEN cdv.coefficient_of_variation > 30 THEN 'Use Median Rate - High Volatility Detected'
            WHEN cdv.coefficient_of_variation > 20 THEN 'Consider Rate Smoothing - Moderate-High Volatility'
            WHEN cdv.coefficient_of_variation > 10 THEN 'Monitor Closely - Moderate Volatility'
            ELSE 'Stable - Current Rate Acceptable'
        END AS stability_recommendation
    FROM cross_day_volatility cdv
)
SELECT
    policy_area_id,
    policy_type,
    coverage_type,
    forecast_day,
    rate_observations,
    min_rate,
    max_rate,
    avg_rate,
    median_rate,
    rate_stddev,
    coefficient_of_variation,
    range_percentage,
    avg_confidence_level,
    stability_score,
    volatility_classification,
    avg_volatility_across_days,
    min_volatility_across_days,
    max_volatility_across_days,
    rate_change_from_prev_day,
    recommended_stable_rate,
    stability_recommendation
FROM stability_recommendations
WHERE forecast_day BETWEEN 7 AND 14
ORDER BY policy_area_id, policy_type, coverage_type, forecast_day
LIMIT 3000;
```

---

## Query 20: Policy Area Risk Ranking and Comparison {#query-20}

**Use Case:** **Insurance Underwriting - Geographic Risk Ranking for Portfolio Management**

**Description:** Ranks policy areas by forecast-based risk scores for December 3-17, 2025 period. Provides comparative risk analysis across geographic areas to support portfolio management and resource allocation.

**Business Value:** Enables insurance companies to identify high-risk areas, allocate underwriting resources effectively, and optimize portfolio risk distribution.

**Purpose:** Risk ranking report showing policy areas ordered by risk level with comparative metrics.

**Business Value:** Enables insurance companies to identify high-risk areas, allocate underwriting resources effectively, and optimize portfolio risk distribution.

**Complexity:** Multiple CTEs (7+ levels), risk aggregation, ranking calculations, percentile analysis, window functions, comparative analysis

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
policy_area_risk_aggregation AS (
    -- Second CTE: Aggregate risk factors by policy area
    SELECT
        irf.policy_area_id,
        irf.forecast_day,
        irf.forecast_date,
        ipa.policy_type,
        ipa.coverage_type,
        ipa.policy_area_name,
        ipa.state_code,
        ipa.risk_zone,
        AVG(irf.overall_risk_score) AS avg_risk_score,
        MAX(irf.overall_risk_score) AS max_risk_score,
        MIN(irf.overall_risk_score) AS min_risk_score,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY irf.overall_risk_score) AS median_risk_score,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY irf.overall_risk_score) AS p95_risk_score,
        STDDEV(irf.overall_risk_score) AS risk_score_stddev,
        AVG(irf.cumulative_precipitation_risk) AS avg_precipitation_risk,
        AVG(irf.temperature_extreme_risk) AS avg_temperature_risk,
        AVG(irf.wind_damage_risk) AS avg_wind_risk,
        AVG(irf.freeze_risk) AS avg_freeze_risk,
        AVG(irf.flood_risk) AS avg_flood_risk,
        AVG(irf.extreme_event_probability) AS avg_extreme_event_probability,
        COUNT(*) AS risk_observations
    FROM insurance_risk_factors irf
    INNER JOIN insurance_policy_areas ipa ON irf.policy_area_id = ipa.policy_area_id
    WHERE irf.forecast_period_start = DATE '2025-12-03'
        AND irf.forecast_period_end = DATE '2025-12-17'
        AND irf.forecast_day BETWEEN 7 AND 14
        AND ipa.is_active = TRUE
    GROUP BY
        irf.policy_area_id,
        irf.forecast_day,
        irf.forecast_date,
        ipa.policy_type,
        ipa.coverage_type,
        ipa.policy_area_name,
        ipa.state_code,
        ipa.risk_zone
),
policy_area_summary AS (
    -- Third CTE: Summarize risk by policy area
    SELECT
        para.policy_area_id,
        para.policy_type,
        para.coverage_type,
        para.policy_area_name,
        para.state_code,
        para.risk_zone,
        COUNT(DISTINCT para.forecast_day) AS forecast_days_covered,
        COUNT(DISTINCT para.forecast_date) AS forecast_dates_covered,
        SUM(para.risk_observations) AS total_risk_observations,
        AVG(para.avg_risk_score) AS overall_avg_risk_score,
        MAX(para.max_risk_score) AS overall_max_risk_score,
        MIN(para.min_risk_score) AS overall_min_risk_score,
        AVG(para.median_risk_score) AS overall_median_risk_score,
        AVG(para.p95_risk_score) AS overall_p95_risk_score,
        AVG(para.risk_score_stddev) AS overall_risk_stddev,
        AVG(para.avg_precipitation_risk) AS overall_avg_precipitation_risk,
        AVG(para.avg_temperature_risk) AS overall_avg_temperature_risk,
        AVG(para.avg_wind_risk) AS overall_avg_wind_risk,
        AVG(para.avg_freeze_risk) AS overall_avg_freeze_risk,
        AVG(para.avg_flood_risk) AS overall_avg_flood_risk,
        AVG(para.avg_extreme_event_probability) AS overall_avg_extreme_event_probability
    FROM policy_area_risk_aggregation para
    GROUP BY
        para.policy_area_id,
        para.policy_type,
        para.coverage_type,
        para.policy_area_name,
        para.state_code,
        para.risk_zone
),
risk_ranking_calculation AS (
    -- Fourth CTE: Calculate risk rankings
    SELECT
        pas.policy_area_id,
        pas.policy_type,
        pas.coverage_type,
        pas.policy_area_name,
        pas.state_code,
        pas.risk_zone,
        pas.forecast_days_covered,
        pas.forecast_dates_covered,
        pas.total_risk_observations,
        ROUND(CAST(pas.overall_avg_risk_score AS NUMERIC), 2) AS overall_avg_risk_score,
        ROUND(CAST(pas.overall_max_risk_score AS NUMERIC), 2) AS overall_max_risk_score,
        ROUND(CAST(pas.overall_min_risk_score AS NUMERIC), 2) AS overall_min_risk_score,
        ROUND(CAST(pas.overall_median_risk_score AS NUMERIC), 2) AS overall_median_risk_score,
        ROUND(CAST(pas.overall_p95_risk_score AS NUMERIC), 2) AS overall_p95_risk_score,
        ROUND(CAST(pas.overall_risk_stddev AS NUMERIC), 2) AS overall_risk_stddev,
        ROUND(CAST(pas.overall_avg_precipitation_risk AS NUMERIC), 2) AS overall_avg_precipitation_risk,
        ROUND(CAST(pas.overall_avg_temperature_risk AS NUMERIC), 2) AS overall_avg_temperature_risk,
        ROUND(CAST(pas.overall_avg_wind_risk AS NUMERIC), 2) AS overall_avg_wind_risk,
        ROUND(CAST(pas.overall_avg_freeze_risk AS NUMERIC), 2) AS overall_avg_freeze_risk,
        ROUND(CAST(pas.overall_avg_flood_risk AS NUMERIC), 2) AS overall_avg_flood_risk,
        ROUND(CAST(pas.overall_avg_extreme_event_probability AS NUMERIC), 4) AS overall_avg_extreme_event_probability,
        -- Risk category
        CASE
            WHEN pas.overall_avg_risk_score >= 75 THEN 'Extreme'
            WHEN pas.overall_avg_risk_score >= 50 THEN 'Very High'
            WHEN pas.overall_avg_risk_score >= 30 THEN 'High'
            WHEN pas.overall_avg_risk_score >= 15 THEN 'Moderate'
            ELSE 'Low'
        END AS risk_category,
        -- Overall risk rank (by average risk score)
        ROW_NUMBER() OVER (
            PARTITION BY pas.policy_type, pas.coverage_type
            ORDER BY pas.overall_avg_risk_score DESC
        ) AS risk_rank_by_type,
        -- Overall risk rank (all policy areas)
        ROW_NUMBER() OVER (
            ORDER BY pas.overall_avg_risk_score DESC
        ) AS overall_risk_rank,
        -- Percentile rank
        PERCENT_RANK() OVER (
            ORDER BY pas.overall_avg_risk_score DESC
        ) AS risk_percentile,
        -- Decile rank
        NTILE(10) OVER (
            ORDER BY pas.overall_avg_risk_score DESC
        ) AS risk_decile
    FROM policy_area_summary pas
),
comparative_analysis AS (
    -- Fifth CTE: Comparative analysis across policy areas
    SELECT
        rrc.policy_area_id,
        rrc.policy_type,
        rrc.coverage_type,
        rrc.policy_area_name,
        rrc.state_code,
        rrc.risk_zone,
        rrc.forecast_days_covered,
        rrc.forecast_dates_covered,
        rrc.total_risk_observations,
        rrc.overall_avg_risk_score,
        rrc.overall_max_risk_score,
        rrc.overall_min_risk_score,
        rrc.overall_median_risk_score,
        rrc.overall_p95_risk_score,
        rrc.overall_risk_stddev,
        rrc.overall_avg_precipitation_risk,
        rrc.overall_avg_temperature_risk,
        rrc.overall_avg_wind_risk,
        rrc.overall_avg_freeze_risk,
        rrc.overall_avg_flood_risk,
        rrc.overall_avg_extreme_event_probability,
        rrc.risk_category,
        rrc.risk_rank_by_type,
        rrc.overall_risk_rank,
        ROUND(CAST(rrc.risk_percentile * 100 AS NUMERIC), 2) AS risk_percentile,
        rrc.risk_decile,
        -- Compare with average risk for policy type
        AVG(rrc.overall_avg_risk_score) OVER (
            PARTITION BY rrc.policy_type, rrc.coverage_type
        ) AS avg_risk_for_type,
        -- Deviation from type average
        rrc.overall_avg_risk_score - AVG(rrc.overall_avg_risk_score) OVER (
            PARTITION BY rrc.policy_type, rrc.coverage_type
        ) AS deviation_from_type_avg,
        -- Percent deviation from type average
        CASE
            WHEN AVG(rrc.overall_avg_risk_score) OVER (
                PARTITION BY rrc.policy_type, rrc.coverage_type
            ) != 0 THEN
                ((rrc.overall_avg_risk_score - AVG(rrc.overall_avg_risk_score) OVER (
                    PARTITION BY rrc.policy_type, rrc.coverage_type
                )) / ABS(AVG(rrc.overall_avg_risk_score) OVER (
                    PARTITION BY rrc.policy_type, rrc.coverage_type
                ))) * 100
            ELSE NULL
        END AS percent_deviation_from_type_avg
    FROM risk_ranking_calculation rrc
)
SELECT
    policy_area_id,
    policy_type,
    coverage_type,
    policy_area_name,
    state_code,
    risk_zone,
    forecast_days_covered,
    forecast_dates_covered,
    total_risk_observations,
    overall_avg_risk_score,
    overall_max_risk_score,
    overall_min_risk_score,
    overall_median_risk_score,
    overall_p95_risk_score,
    overall_risk_stddev,
    overall_avg_precipitation_risk,
    overall_avg_temperature_risk,
    overall_avg_wind_risk,
    overall_avg_freeze_risk,
    overall_avg_flood_risk,
    overall_avg_extreme_event_probability,
    risk_category,
    risk_rank_by_type,
    overall_risk_rank,
    risk_percentile,
    risk_decile,
    ROUND(CAST(avg_risk_for_type AS NUMERIC), 2) AS avg_risk_for_type,
    ROUND(CAST(deviation_from_type_avg AS NUMERIC), 2) AS deviation_from_type_avg,
    ROUND(CAST(percent_deviation_from_type_avg AS NUMERIC), 2) AS percent_deviation_from_type_avg
FROM comparative_analysis
ORDER BY overall_risk_rank
LIMIT 1000;
```

---

## Query 21: Forecast-to-Rate Impact Analysis {#query-21}

**Use Case:** **Insurance Underwriting - Forecast Parameter Impact on Rate Determination**

**Description:** Analyzes how individual forecast parameters (temperature, precipitation, wind) impact insurance rates for December 3-17, 2025. Quantifies the contribution of each weather parameter to final rate calculations.

**Business Value:** Parameter impact analysis showing which forecast parameters drive rate changes and their relative contributions.

**Purpose:** Enables insurance companies to understand which weather parameters most significantly affect rates, improving transparency and model interpretability.

**Complexity:** Multiple CTEs (6+ levels), parameter contribution analysis, impact calculations, correlation analysis, window functions

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
forecast_rate_mapping_data AS (
    -- Second CTE: Get forecast-to-rate mappings
    SELECT
        frm.mapping_id,
        frm.forecast_id,
        frm.rate_table_id,
        frm.risk_factor_id,
        frm.policy_area_id,
        frm.forecast_date,
        frm.forecast_day,
        frm.forecast_time,
        frm.parameter_name,
        frm.parameter_value,
        frm.risk_contribution,
        frm.rate_impact,
        gf.parameter_value AS forecast_parameter_value,
        irt.risk_adjusted_rate,
        irt.base_rate,
        irt.risk_multiplier
    FROM forecast_rate_mapping frm
    INNER JOIN grib2_forecasts gf ON frm.forecast_id = gf.forecast_id
    LEFT JOIN insurance_rate_tables irt ON frm.rate_table_id = irt.rate_table_id
    WHERE frm.forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
        AND frm.forecast_day BETWEEN 7 AND 14
),
parameter_impact_aggregation AS (
    -- Third CTE: Aggregate impact by parameter
    SELECT
        frmd.policy_area_id,
        frmd.parameter_name,
        frmd.forecast_day,
        frmd.forecast_date,
        COUNT(*) AS parameter_observations,
        AVG(frmd.parameter_value) AS avg_parameter_value,
        MIN(frmd.parameter_value) AS min_parameter_value,
        MAX(frmd.parameter_value) AS max_parameter_value,
        STDDEV(frmd.parameter_value) AS parameter_stddev,
        AVG(frmd.risk_contribution) AS avg_risk_contribution,
        SUM(frmd.risk_contribution) AS total_risk_contribution,
        AVG(frmd.rate_impact) AS avg_rate_impact,
        SUM(frmd.rate_impact) AS total_rate_impact,
        AVG(frmd.risk_adjusted_rate) AS avg_risk_adjusted_rate,
        AVG(frmd.base_rate) AS avg_base_rate,
        AVG(frmd.risk_multiplier) AS avg_risk_multiplier
    FROM forecast_rate_mapping_data frmd
    GROUP BY
        frmd.policy_area_id,
        frmd.parameter_name,
        frmd.forecast_day,
        frmd.forecast_date
),
parameter_contribution_analysis AS (
    -- Fourth CTE: Analyze parameter contributions
    SELECT
        pia.policy_area_id,
        pia.parameter_name,
        pia.forecast_day,
        pia.forecast_date,
        pia.parameter_observations,
        ROUND(CAST(pia.avg_parameter_value AS NUMERIC), 2) AS avg_parameter_value,
        ROUND(CAST(pia.min_parameter_value AS NUMERIC), 2) AS min_parameter_value,
        ROUND(CAST(pia.max_parameter_value AS NUMERIC), 2) AS max_parameter_value,
        ROUND(CAST(pia.parameter_stddev AS NUMERIC), 2) AS parameter_stddev,
        ROUND(CAST(pia.avg_risk_contribution AS NUMERIC), 4) AS avg_risk_contribution,
        ROUND(CAST(pia.total_risk_contribution AS NUMERIC), 4) AS total_risk_contribution,
        ROUND(CAST(pia.avg_rate_impact AS NUMERIC), 2) AS avg_rate_impact,
        ROUND(CAST(pia.total_rate_impact AS NUMERIC), 2) AS total_rate_impact,
        ROUND(CAST(pia.avg_risk_adjusted_rate AS NUMERIC), 2) AS avg_risk_adjusted_rate,
        ROUND(CAST(pia.avg_base_rate AS NUMERIC), 2) AS avg_base_rate,
        ROUND(CAST(pia.avg_risk_multiplier AS NUMERIC), 3) AS avg_risk_multiplier,
        -- Contribution percentage
        CASE
            WHEN SUM(pia.total_risk_contribution) OVER (
                PARTITION BY pia.policy_area_id, pia.forecast_day, pia.forecast_date
            ) != 0 THEN
                (pia.total_risk_contribution / SUM(pia.total_risk_contribution) OVER (
                    PARTITION BY pia.policy_area_id, pia.forecast_day, pia.forecast_date
                )) * 100
            ELSE NULL
        END AS contribution_percentage,
        -- Impact percentage of base rate
        CASE
            WHEN pia.avg_base_rate != 0 THEN
                (pia.total_rate_impact / ABS(pia.avg_base_rate)) * 100
            ELSE NULL
        END AS impact_percentage_of_base_rate
    FROM parameter_impact_aggregation pia
),
parameter_ranking AS (
    -- Fifth CTE: Rank parameters by impact
    SELECT
        pca.policy_area_id,
        pca.parameter_name,
        pca.forecast_day,
        pca.forecast_date,
        pca.parameter_observations,
        pca.avg_parameter_value,
        pca.min_parameter_value,
        pca.max_parameter_value,
        pca.parameter_stddev,
        pca.avg_risk_contribution,
        pca.total_risk_contribution,
        pca.avg_rate_impact,
        pca.total_rate_impact,
        pca.avg_risk_adjusted_rate,
        pca.avg_base_rate,
        pca.avg_risk_multiplier,
        ROUND(CAST(pca.contribution_percentage AS NUMERIC), 2) AS contribution_percentage,
        ROUND(CAST(pca.impact_percentage_of_base_rate AS NUMERIC), 2) AS impact_percentage_of_base_rate,
        -- Parameter impact rank
        ROW_NUMBER() OVER (
            PARTITION BY pca.policy_area_id, pca.forecast_day, pca.forecast_date
            ORDER BY ABS(pca.total_rate_impact) DESC
        ) AS parameter_impact_rank,
        -- Parameter contribution rank
        ROW_NUMBER() OVER (
            PARTITION BY pca.policy_area_id, pca.forecast_day, pca.forecast_date
            ORDER BY pca.total_risk_contribution DESC
        ) AS parameter_contribution_rank
    FROM parameter_contribution_analysis pca
)
SELECT
    policy_area_id,
    parameter_name,
    forecast_day,
    forecast_date,
    parameter_observations,
    avg_parameter_value,
    min_parameter_value,
    max_parameter_value,
    parameter_stddev,
    avg_risk_contribution,
    total_risk_contribution,
    avg_rate_impact,
    total_rate_impact,
    avg_risk_adjusted_rate,
    avg_base_rate,
    avg_risk_multiplier,
    contribution_percentage,
    impact_percentage_of_base_rate,
    parameter_impact_rank,
    parameter_contribution_rank,
    CASE
        WHEN parameter_impact_rank = 1 THEN 'Primary Driver'
        WHEN parameter_impact_rank <= 3 THEN 'Significant Contributor'
        ELSE 'Minor Contributor'
    END AS impact_classification
FROM parameter_ranking
WHERE forecast_day BETWEEN 7 AND 14
    AND forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
ORDER BY policy_area_id, forecast_day, forecast_date, parameter_impact_rank
LIMIT 5000;
```

---

## Query 22: Multi-Day Forecast Ensemble Rate Analysis {#query-22}

**Use Case:** **Insurance Underwriting - Ensemble Forecast Rate Analysis for Robust Pricing**

**Description:** Analyzes rates across multiple forecast days (7-14 days) as an ensemble to determine robust, consensus rates. Uses ensemble statistics to reduce forecast uncertainty and provide more stable pricing.

**Business Value:** Provides more robust rate determination by combining multiple forecast days, reducing impact of individual forecast errors and improving pricing stability.

**Purpose:** Ensemble rate analysis showing consensus rates across forecast days with confidence intervals.

**Business Value:** Provides more robust rate determination by combining multiple forecast days, reducing impact of individual forecast errors and improving pricing stability.

**Complexity:** Multiple CTEs (7+ levels), ensemble statistics, consensus calculations, confidence intervals, window functions, statistical aggregation

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
rate_ensemble_data AS (
    -- Second CTE: Collect rates across all forecast days
    SELECT
        irt.policy_area_id,
        irt.policy_type,
        irt.coverage_type,
        irt.forecast_day,
        irt.forecast_date,
        irt.base_rate,
        irt.risk_adjusted_rate,
        irt.risk_multiplier,
        irt.confidence_level,
        irt.overall_risk_score
    FROM insurance_rate_tables irt
    WHERE irt.forecast_period_start = DATE '2025-12-03'
        AND irt.forecast_period_end = DATE '2025-12-17'
        AND irt.forecast_day BETWEEN 7 AND 14
        AND irt.forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
),
ensemble_statistics AS (
    -- Third CTE: Calculate ensemble statistics
    SELECT
        red.policy_area_id,
        red.policy_type,
        red.coverage_type,
        red.forecast_date,
        COUNT(DISTINCT red.forecast_day) AS forecast_days_count,
        COUNT(*) AS total_rate_observations,
        -- Rate statistics
        MIN(red.risk_adjusted_rate) AS ensemble_min_rate,
        MAX(red.risk_adjusted_rate) AS ensemble_max_rate,
        AVG(red.risk_adjusted_rate) AS ensemble_mean_rate,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY red.risk_adjusted_rate) AS ensemble_median_rate,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY red.risk_adjusted_rate) AS ensemble_q1_rate,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY red.risk_adjusted_rate) AS ensemble_q3_rate,
        PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY red.risk_adjusted_rate) AS ensemble_p10_rate,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY red.risk_adjusted_rate) AS ensemble_p90_rate,
        STDDEV(red.risk_adjusted_rate) AS ensemble_stddev_rate,
        VARIANCE(red.risk_adjusted_rate) AS ensemble_variance_rate,
        -- Confidence statistics
        AVG(red.confidence_level) AS ensemble_avg_confidence,
        MIN(red.confidence_level) AS ensemble_min_confidence,
        MAX(red.confidence_level) AS ensemble_max_confidence,
        -- Risk score statistics
        AVG(red.overall_risk_score) AS ensemble_avg_risk_score,
        STDDEV(red.overall_risk_score) AS ensemble_risk_score_stddev
    FROM rate_ensemble_data red
    GROUP BY
        red.policy_area_id,
        red.policy_type,
        red.coverage_type,
        red.forecast_date
),
ensemble_consensus_calculation AS (
    -- Fourth CTE: Calculate consensus rates
    SELECT
        es.policy_area_id,
        es.policy_type,
        es.coverage_type,
        es.forecast_date,
        es.forecast_days_count,
        es.total_rate_observations,
        ROUND(CAST(es.ensemble_min_rate AS NUMERIC), 2) AS ensemble_min_rate,
        ROUND(CAST(es.ensemble_max_rate AS NUMERIC), 2) AS ensemble_max_rate,
        ROUND(CAST(es.ensemble_mean_rate AS NUMERIC), 2) AS ensemble_mean_rate,
        ROUND(CAST(es.ensemble_median_rate AS NUMERIC), 2) AS ensemble_median_rate,
        ROUND(CAST(es.ensemble_q1_rate AS NUMERIC), 2) AS ensemble_q1_rate,
        ROUND(CAST(es.ensemble_q3_rate AS NUMERIC), 2) AS ensemble_q3_rate,
        ROUND(CAST(es.ensemble_p10_rate AS NUMERIC), 2) AS ensemble_p10_rate,
        ROUND(CAST(es.ensemble_p90_rate AS NUMERIC), 2) AS ensemble_p90_rate,
        ROUND(CAST(es.ensemble_stddev_rate AS NUMERIC), 2) AS ensemble_stddev_rate,
        ROUND(CAST(es.ensemble_variance_rate AS NUMERIC), 2) AS ensemble_variance_rate,
        ROUND(CAST(es.ensemble_avg_confidence AS NUMERIC), 2) AS ensemble_avg_confidence,
        ROUND(CAST(es.ensemble_min_confidence AS NUMERIC), 2) AS ensemble_min_confidence,
        ROUND(CAST(es.ensemble_max_confidence AS NUMERIC), 2) AS ensemble_max_confidence,
        ROUND(CAST(es.ensemble_avg_risk_score AS NUMERIC), 2) AS ensemble_avg_risk_score,
        ROUND(CAST(es.ensemble_risk_score_stddev AS NUMERIC), 2) AS ensemble_risk_score_stddev,
        -- Consensus rate (use median for robustness)
        ROUND(CAST(es.ensemble_median_rate AS NUMERIC), 2) AS consensus_rate,
        -- Confidence interval (90%)
        ROUND(CAST(es.ensemble_p10_rate AS NUMERIC), 2) AS confidence_interval_lower_90,
        ROUND(CAST(es.ensemble_p90_rate AS NUMERIC), 2) AS confidence_interval_upper_90,
        -- Interquartile range
        ROUND(CAST(es.ensemble_q3_rate - es.ensemble_q1_rate AS NUMERIC), 2) AS ensemble_iqr,
        -- Coefficient of variation
        CASE
            WHEN es.ensemble_mean_rate != 0 THEN
                (es.ensemble_stddev_rate / ABS(es.ensemble_mean_rate)) * 100
            ELSE NULL
        END AS ensemble_coefficient_of_variation
    FROM ensemble_statistics es
),
ensemble_quality_assessment AS (
    -- Fifth CTE: Assess ensemble quality
    SELECT
        ecc.policy_area_id,
        ecc.policy_type,
        ecc.coverage_type,
        ecc.forecast_date,
        ecc.forecast_days_count,
        ecc.total_rate_observations,
        ecc.ensemble_min_rate,
        ecc.ensemble_max_rate,
        ecc.ensemble_mean_rate,
        ecc.ensemble_median_rate,
        ecc.ensemble_q1_rate,
        ecc.ensemble_q3_rate,
        ecc.ensemble_p10_rate,
        ecc.ensemble_p90_rate,
        ecc.ensemble_stddev_rate,
        ecc.ensemble_variance_rate,
        ecc.ensemble_avg_confidence,
        ecc.ensemble_min_confidence,
        ecc.ensemble_max_confidence,
        ecc.ensemble_avg_risk_score,
        ecc.ensemble_risk_score_stddev,
        ecc.consensus_rate,
        ecc.confidence_interval_lower_90,
        ecc.confidence_interval_upper_90,
        ecc.ensemble_iqr,
        ROUND(CAST(ecc.ensemble_coefficient_of_variation AS NUMERIC), 2) AS ensemble_coefficient_of_variation,
        -- Ensemble quality score (higher is better)
        (
            (ecc.ensemble_avg_confidence / 100.0) * 40.0 +  -- Confidence component (40%)
            GREATEST(0, 40.0 - (ecc.ensemble_coefficient_of_variation / 2.0)) +  -- Low variability component (40%)
            (LEAST(ecc.forecast_days_count / 8.0, 1.0) * 20.0)  -- Coverage component (20%)
        ) AS ensemble_quality_score,
        -- Ensemble reliability
        CASE
            WHEN ecc.ensemble_coefficient_of_variation < 5 THEN 'Very Reliable'
            WHEN ecc.ensemble_coefficient_of_variation < 10 THEN 'Reliable'
            WHEN ecc.ensemble_coefficient_of_variation < 20 THEN 'Moderately Reliable'
            ELSE 'Less Reliable'
        END AS ensemble_reliability
    FROM ensemble_consensus_calculation ecc
)
SELECT
    policy_area_id,
    policy_type,
    coverage_type,
    forecast_date,
    forecast_days_count,
    total_rate_observations,
    ensemble_min_rate,
    ensemble_max_rate,
    ensemble_mean_rate,
    ensemble_median_rate,
    ensemble_q1_rate,
    ensemble_q3_rate,
    ensemble_p10_rate,
    ensemble_p90_rate,
    ensemble_stddev_rate,
    ensemble_variance_rate,
    ensemble_avg_confidence,
    ensemble_min_confidence,
    ensemble_max_confidence,
    ensemble_avg_risk_score,
    ensemble_risk_score_stddev,
    consensus_rate,
    confidence_interval_lower_90,
    confidence_interval_upper_90,
    ensemble_iqr,
    ensemble_coefficient_of_variation,
    ROUND(CAST(ensemble_quality_score AS NUMERIC), 2) AS ensemble_quality_score,
    ensemble_reliability
FROM ensemble_quality_assessment
WHERE forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
ORDER BY policy_area_id, policy_type, coverage_type, forecast_date
LIMIT 2000;
```

---

## Query 23: Forecast Day Selection Optimization {#query-23}

**Use Case:** **Insurance Underwriting - Optimal Forecast Day Selection for Rate Determination**

**Description:** Determines optimal forecast day (7-14 days) for rate determination based on accuracy, confidence, and business requirements. Balances forecast accuracy (shorter forecast) with planning horizon (longer forecast).

**Business Value:** Forecast day optimization report recommending optimal forecast day for each policy area with justification.

**Purpose:** Enables insurance companies to select optimal forecast day balancing accuracy and planning needs, improving rate determination efficiency.

**Complexity:** Multiple CTEs (8+ levels), optimization scoring, multi-criteria analysis, window functions, ranking calculations

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
forecast_day_metrics AS (
    -- Second CTE: Collect metrics for each forecast day
    SELECT
        irt.policy_area_id,
        irt.policy_type,
        irt.coverage_type,
        irt.forecast_day,
        COUNT(*) AS rate_count,
        AVG(irt.confidence_level) AS avg_confidence,
        MIN(irt.confidence_level) AS min_confidence,
        MAX(irt.confidence_level) AS max_confidence,
        AVG(irt.risk_adjusted_rate) AS avg_rate,
        STDDEV(irt.risk_adjusted_rate) AS rate_stddev,
        AVG(irt.overall_risk_score) AS avg_risk_score,
        STDDEV(irt.overall_risk_score) AS risk_score_stddev,
        -- Historical accuracy (if available from claims validation)
        COALESCE(
            (SELECT AVG(CASE WHEN ich.forecast_available = TRUE AND ich.forecast_day = irt.forecast_day THEN 1 ELSE 0 END)
             FROM insurance_claims_history ich
             WHERE ich.policy_area_id = irt.policy_area_id
               AND ich.loss_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'), 0.5
        ) AS historical_accuracy_rate
    FROM insurance_rate_tables irt
    WHERE irt.forecast_period_start = DATE '2025-12-03'
        AND irt.forecast_period_end = DATE '2025-12-17'
        AND irt.forecast_day BETWEEN 7 AND 14
        AND irt.forecast_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
    GROUP BY
        irt.policy_area_id,
        irt.policy_type,
        irt.coverage_type,
        irt.forecast_day
),
forecast_day_scoring AS (
    -- Third CTE: Score each forecast day
    SELECT
        fdm.policy_area_id,
        fdm.policy_type,
        fdm.coverage_type,
        fdm.forecast_day,
        fdm.rate_count,
        ROUND(CAST(fdm.avg_confidence AS NUMERIC), 2) AS avg_confidence,
        ROUND(CAST(fdm.min_confidence AS NUMERIC), 2) AS min_confidence,
        ROUND(CAST(fdm.max_confidence AS NUMERIC), 2) AS max_confidence,
        ROUND(CAST(fdm.avg_rate AS NUMERIC), 2) AS avg_rate,
        ROUND(CAST(fdm.rate_stddev AS NUMERIC), 2) AS rate_stddev,
        ROUND(CAST(fdm.avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
        ROUND(CAST(fdm.risk_score_stddev AS NUMERIC), 2) AS risk_score_stddev,
        ROUND(CAST(fdm.historical_accuracy_rate AS NUMERIC), 4) AS historical_accuracy_rate,
        -- Confidence score (higher confidence = better, but decreases with forecast day)
        CASE
            WHEN fdm.forecast_day <= 8 THEN fdm.avg_confidence * 1.0  -- Full weight for 7-8 days
            WHEN fdm.forecast_day <= 10 THEN fdm.avg_confidence * 0.9  -- Slight reduction for 9-10 days
            WHEN fdm.forecast_day <= 12 THEN fdm.avg_confidence * 0.8  -- More reduction for 11-12 days
            ELSE fdm.avg_confidence * 0.7  -- Lower weight for 13-14 days
        END AS confidence_score,
        -- Stability score (lower volatility = better)
        CASE
            WHEN fdm.avg_rate != 0 THEN
                100.0 - LEAST((fdm.rate_stddev / ABS(fdm.avg_rate)) * 100, 100.0)
            ELSE 50.0
        END AS stability_score,
        -- Accuracy score (from historical data)
        fdm.historical_accuracy_rate * 100 AS accuracy_score,
        -- Planning horizon score (longer forecast = better for planning)
        (fdm.forecast_day / 14.0) * 100 AS planning_horizon_score
    FROM forecast_day_metrics fdm
),
optimization_scoring AS (
    -- Fourth CTE: Calculate optimization scores
    SELECT
        fds.policy_area_id,
        fds.policy_type,
        fds.coverage_type,
        fds.forecast_day,
        fds.rate_count,
        fds.avg_confidence,
        fds.min_confidence,
        fds.max_confidence,
        fds.avg_rate,
        fds.rate_stddev,
        fds.avg_risk_score,
        fds.risk_score_stddev,
        fds.historical_accuracy_rate,
        fds.confidence_score,
        fds.stability_score,
        fds.accuracy_score,
        fds.planning_horizon_score,
        -- Overall optimization score (weighted combination)
        (
            fds.confidence_score * 0.35 +  -- Confidence weight: 35%
            fds.stability_score * 0.30 +  -- Stability weight: 30%
            fds.accuracy_score * 0.25 +  -- Accuracy weight: 25%
            fds.planning_horizon_score * 0.10  -- Planning horizon weight: 10%
        ) AS overall_optimization_score
    FROM forecast_day_scoring fds
),
forecast_day_ranking AS (
    -- Fifth CTE: Rank forecast days
    SELECT
        os.policy_area_id,
        os.policy_type,
        os.coverage_type,
        os.forecast_day,
        os.rate_count,
        os.avg_confidence,
        os.min_confidence,
        os.max_confidence,
        os.avg_rate,
        os.rate_stddev,
        os.avg_risk_score,
        os.risk_score_stddev,
        os.historical_accuracy_rate,
        ROUND(CAST(os.confidence_score AS NUMERIC), 2) AS confidence_score,
        ROUND(CAST(os.stability_score AS NUMERIC), 2) AS stability_score,
        ROUND(CAST(os.accuracy_score AS NUMERIC), 2) AS accuracy_score,
        ROUND(CAST(os.planning_horizon_score AS NUMERIC), 2) AS planning_horizon_score,
        ROUND(CAST(os.overall_optimization_score AS NUMERIC), 2) AS overall_optimization_score,
        -- Rank by optimization score
        ROW_NUMBER() OVER (
            PARTITION BY os.policy_area_id, os.policy_type, os.coverage_type
            ORDER BY os.overall_optimization_score DESC
        ) AS optimization_rank,
        -- Percentile rank
        PERCENT_RANK() OVER (
            PARTITION BY os.policy_area_id, os.policy_type, os.coverage_type
            ORDER BY os.overall_optimization_score DESC
        ) AS optimization_percentile
    FROM optimization_scoring os
),
recommendation_generation AS (
    -- Sixth CTE: Generate recommendations
    SELECT
        fdr.policy_area_id,
        fdr.policy_type,
        fdr.coverage_type,
        fdr.forecast_day,
        fdr.rate_count,
        fdr.avg_confidence,
        fdr.min_confidence,
        fdr.max_confidence,
        fdr.avg_rate,
        fdr.rate_stddev,
        fdr.avg_risk_score,
        fdr.risk_score_stddev,
        fdr.historical_accuracy_rate,
        fdr.confidence_score,
        fdr.stability_score,
        fdr.accuracy_score,
        fdr.planning_horizon_score,
        fdr.overall_optimization_score,
        fdr.optimization_rank,
        ROUND(CAST(fdr.optimization_percentile * 100 AS NUMERIC), 2) AS optimization_percentile,
        -- Recommendation status
        CASE
            WHEN fdr.optimization_rank = 1 THEN 'Recommended'
            WHEN fdr.optimization_rank <= 3 THEN 'Alternative'
            ELSE 'Not Recommended'
        END AS recommendation_status,
        -- Justification
        CASE
            WHEN fdr.optimization_rank = 1 THEN
                'Optimal balance of confidence (' || ROUND(fdr.avg_confidence, 1) || '%), stability, and accuracy'
            WHEN fdr.optimization_rank <= 3 THEN
                'Good alternative with ' || ROUND(fdr.avg_confidence, 1) || '% confidence'
            ELSE
                'Lower optimization score compared to alternatives'
        END AS recommendation_justification
    FROM forecast_day_ranking fdr
)
SELECT
    policy_area_id,
    policy_type,
    coverage_type,
    forecast_day,
    rate_count,
    avg_confidence,
    min_confidence,
    max_confidence,
    avg_rate,
    rate_stddev,
    avg_risk_score,
    risk_score_stddev,
    historical_accuracy_rate,
    confidence_score,
    stability_score,
    accuracy_score,
    planning_horizon_score,
    overall_optimization_score,
    optimization_rank,
    optimization_percentile,
    recommendation_status,
    recommendation_justification
FROM recommendation_generation
WHERE forecast_day BETWEEN 7 AND 14
ORDER BY policy_area_id, policy_type, coverage_type, optimization_rank
LIMIT 3000;
```

---

## Query 24: Comprehensive Insurance Rate Modeling Summary {#query-24}

**Use Case:** **Insurance Underwriting - Comprehensive Rate Modeling Summary Dashboard**

**Description:** Provides comprehensive summary of insurance rate modeling for December 3-17, 2025 period. Aggregates risk factors, rates, comparisons, validations, and recommendations into a single dashboard view.

**Business Value:** Provides insurance companies with single-source-of-truth dashboard for rate modeling decisions, improving efficiency and decision-making.

**Purpose:** Comprehensive rate modeling summary dashboard with all key metrics and recommendations.

**Business Value:** Provides insurance companies with single-source-of-truth dashboard for rate modeling decisions, improving efficiency and decision-making.

**Complexity:** Multiple CTEs (9+ levels), comprehensive aggregation, summary statistics, dashboard metrics, window functions, multi-table joins

```sql
WITH forecast_period AS (
    -- First CTE: Define forecast period
    SELECT
        DATE '2025-12-03' AS period_start,
        DATE '2025-12-17' AS period_end
),
risk_factors_summary AS (
    -- Second CTE: Summarize risk factors
    SELECT
        irf.policy_area_id,
        COUNT(DISTINCT irf.forecast_day) AS forecast_days_analyzed,
        AVG(irf.overall_risk_score) AS avg_overall_risk_score,
        MAX(irf.overall_risk_score) AS max_overall_risk_score,
        MIN(irf.overall_risk_score) AS min_overall_risk_score,
        AVG(irf.cumulative_precipitation_risk) AS avg_precipitation_risk,
        AVG(irf.temperature_extreme_risk) AS avg_temperature_risk,
        AVG(irf.wind_damage_risk) AS avg_wind_risk,
        AVG(irf.freeze_risk) AS avg_freeze_risk,
        AVG(irf.flood_risk) AS avg_flood_risk,
        AVG(irf.extreme_event_probability) AS avg_extreme_event_probability
    FROM insurance_risk_factors irf
    WHERE irf.forecast_period_start = DATE '2025-12-03'
        AND irf.forecast_period_end = DATE '2025-12-17'
        AND irf.forecast_day BETWEEN 7 AND 14
    GROUP BY irf.policy_area_id
),
rate_tables_summary AS (
    -- Third CTE: Summarize rate tables
    SELECT
        irt.policy_area_id,
        irt.policy_type,
        irt.coverage_type,
        COUNT(*) AS total_rate_records,
        COUNT(DISTINCT irt.forecast_day) AS forecast_days_covered,
        AVG(irt.base_rate) AS avg_base_rate,
        AVG(irt.risk_adjusted_rate) AS avg_risk_adjusted_rate,
        MIN(irt.risk_adjusted_rate) AS min_risk_adjusted_rate,
        MAX(irt.risk_adjusted_rate) AS max_risk_adjusted_rate,
        STDDEV(irt.risk_adjusted_rate) AS rate_stddev,
        AVG(irt.confidence_level) AS avg_confidence_level,
        AVG(irt.risk_multiplier) AS avg_risk_multiplier
    FROM insurance_rate_tables irt
    WHERE irt.forecast_period_start = DATE '2025-12-03'
        AND irt.forecast_period_end = DATE '2025-12-17'
        AND irt.forecast_day BETWEEN 7 AND 14
    GROUP BY
        irt.policy_area_id,
        irt.policy_type,
        irt.coverage_type
),
rate_comparison_summary AS (
    -- Fourth CTE: Summarize rate comparisons
    SELECT
        rtc.policy_area_id,
        rtc.policy_type,
        rtc.coverage_type,
        AVG(rtc.rate_volatility_percent) AS avg_rate_volatility,
        AVG(rtc.avg_confidence_level) AS avg_comparison_confidence,
        COUNT(CASE WHEN rtc.recommendation_status = 'Recommended' THEN 1 END) AS recommended_forecast_days_count
    FROM rate_table_comparison rtc
    WHERE rtc.forecast_period_start = DATE '2025-12-03'
        AND rtc.forecast_period_end = DATE '2025-12-17'
    GROUP BY
        rtc.policy_area_id,
        rtc.policy_type,
        rtc.coverage_type
),
claims_validation_summary AS (
    -- Fifth CTE: Summarize claims validation
    SELECT
        ich.policy_area_id,
        COUNT(*) AS total_claims,
        COUNT(CASE WHEN ich.forecast_available = TRUE THEN 1 END) AS claims_with_forecast,
        AVG(CASE WHEN ich.forecast_available = TRUE THEN ich.forecast_error ELSE NULL END) AS avg_forecast_error,
        AVG(ich.loss_amount) AS avg_loss_amount,
        SUM(ich.loss_amount) AS total_loss_amount
    FROM insurance_claims_history ich
    WHERE ich.loss_date BETWEEN DATE '2025-12-03' AND DATE '2025-12-17'
        AND ich.claim_status = 'Closed'
    GROUP BY ich.policy_area_id
),
comprehensive_summary AS (
    -- Sixth CTE: Combine all summaries
    SELECT
        COALESCE(rfs.policy_area_id, rts.policy_area_id, rcs.policy_area_id, cvs.policy_area_id) AS policy_area_id,
        rts.policy_type,
        rts.coverage_type,
        ipa.policy_area_name,
        ipa.state_code,
        ipa.risk_zone,
        -- Risk factors
        rfs.forecast_days_analyzed,
        ROUND(CAST(rfs.avg_overall_risk_score AS NUMERIC), 2) AS avg_overall_risk_score,
        ROUND(CAST(rfs.max_overall_risk_score AS NUMERIC), 2) AS max_overall_risk_score,
        ROUND(CAST(rfs.min_overall_risk_score AS NUMERIC), 2) AS min_overall_risk_score,
        ROUND(CAST(rfs.avg_precipitation_risk AS NUMERIC), 2) AS avg_precipitation_risk,
        ROUND(CAST(rfs.avg_temperature_risk AS NUMERIC), 2) AS avg_temperature_risk,
        ROUND(CAST(rfs.avg_wind_risk AS NUMERIC), 2) AS avg_wind_risk,
        ROUND(CAST(rfs.avg_freeze_risk AS NUMERIC), 2) AS avg_freeze_risk,
        ROUND(CAST(rfs.avg_flood_risk AS NUMERIC), 2) AS avg_flood_risk,
        ROUND(CAST(rfs.avg_extreme_event_probability AS NUMERIC), 4) AS avg_extreme_event_probability,
        -- Rate tables
        rts.total_rate_records,
        rts.forecast_days_covered,
        ROUND(CAST(rts.avg_base_rate AS NUMERIC), 2) AS avg_base_rate,
        ROUND(CAST(rts.avg_risk_adjusted_rate AS NUMERIC), 2) AS avg_risk_adjusted_rate,
        ROUND(CAST(rts.min_risk_adjusted_rate AS NUMERIC), 2) AS min_risk_adjusted_rate,
        ROUND(CAST(rts.max_risk_adjusted_rate AS NUMERIC), 2) AS max_risk_adjusted_rate,
        ROUND(CAST(rts.rate_stddev AS NUMERIC), 2) AS rate_stddev,
        ROUND(CAST(rts.avg_confidence_level AS NUMERIC), 2) AS avg_confidence_level,
        ROUND(CAST(rts.avg_risk_multiplier AS NUMERIC), 3) AS avg_risk_multiplier,
        -- Rate comparison
        ROUND(CAST(rcs.avg_rate_volatility AS NUMERIC), 2) AS avg_rate_volatility,
        ROUND(CAST(rcs.avg_comparison_confidence AS NUMERIC), 2) AS avg_comparison_confidence,
        rcs.recommended_forecast_days_count,
        -- Claims validation
        COALESCE(cvs.total_claims, 0) AS total_claims,
        COALESCE(cvs.claims_with_forecast, 0) AS claims_with_forecast,
        ROUND(CAST(cvs.avg_forecast_error AS NUMERIC), 2) AS avg_forecast_error,
        ROUND(CAST(cvs.avg_loss_amount AS NUMERIC), 2) AS avg_loss_amount,
        ROUND(CAST(cvs.total_loss_amount AS NUMERIC), 2) AS total_loss_amount
    FROM risk_factors_summary rfs
    FULL OUTER JOIN rate_tables_summary rts ON rfs.policy_area_id = rts.policy_area_id
    FULL OUTER JOIN rate_comparison_summary rcs ON COALESCE(rfs.policy_area_id, rts.policy_area_id) = rcs.policy_area_id
    FULL OUTER JOIN claims_validation_summary cvs ON COALESCE(rfs.policy_area_id, rts.policy_area_id) = cvs.policy_area_id
    LEFT JOIN insurance_policy_areas ipa ON COALESCE(rfs.policy_area_id, rts.policy_area_id, rcs.policy_area_id, cvs.policy_area_id) = ipa.policy_area_id
),
dashboard_metrics AS (
    -- Seventh CTE: Calculate dashboard metrics
    SELECT
        cs.policy_area_id,
        cs.policy_type,
        cs.coverage_type,
        cs.policy_area_name,
        cs.state_code,
        cs.risk_zone,
        cs.forecast_days_analyzed,
        cs.avg_overall_risk_score,
        cs.max_overall_risk_score,
        cs.min_overall_risk_score,
        cs.avg_precipitation_risk,
        cs.avg_temperature_risk,
        cs.avg_wind_risk,
        cs.avg_freeze_risk,
        cs.avg_flood_risk,
        cs.avg_extreme_event_probability,
        cs.total_rate_records,
        cs.forecast_days_covered,
        cs.avg_base_rate,
        cs.avg_risk_adjusted_rate,
        cs.min_risk_adjusted_rate,
        cs.max_risk_adjusted_rate,
        cs.rate_stddev,
        cs.avg_confidence_level,
        cs.avg_risk_multiplier,
        cs.avg_rate_volatility,
        cs.avg_comparison_confidence,
        cs.recommended_forecast_days_count,
        cs.total_claims,
        cs.claims_with_forecast,
        cs.avg_forecast_error,
        cs.avg_loss_amount,
        cs.total_loss_amount,
        -- Risk category
        CASE
            WHEN cs.avg_overall_risk_score >= 75 THEN 'Extreme'
            WHEN cs.avg_overall_risk_score >= 50 THEN 'Very High'
            WHEN cs.avg_overall_risk_score >= 30 THEN 'High'
            WHEN cs.avg_overall_risk_score >= 15 THEN 'Moderate'
            ELSE 'Low'
        END AS risk_category,
        -- Rate stability
        CASE
            WHEN cs.avg_rate_volatility > 30 THEN 'Very High Volatility'
            WHEN cs.avg_rate_volatility > 20 THEN 'High Volatility'
            WHEN cs.avg_rate_volatility > 10 THEN 'Moderate Volatility'
            WHEN cs.avg_rate_volatility > 5 THEN 'Low Volatility'
            ELSE 'Very Low Volatility'
        END AS rate_stability,
        -- Overall status
        CASE
            WHEN cs.avg_overall_risk_score >= 75 AND cs.avg_rate_volatility > 20 THEN 'Critical - High Risk & High Volatility'
            WHEN cs.avg_overall_risk_score >= 50 AND cs.avg_rate_volatility > 15 THEN 'Warning - Elevated Risk & Volatility'
            WHEN cs.avg_overall_risk_score >= 30 THEN 'Monitor - Moderate Risk'
            ELSE 'Normal - Low Risk'
        END AS overall_status
    FROM comprehensive_summary cs
)
SELECT
    policy_area_id,
    policy_type,
    coverage_type,
    policy_area_name,
    state_code,
    risk_zone,
    forecast_days_analyzed,
    avg_overall_risk_score,
    max_overall_risk_score,
    min_overall_risk_score,
    avg_precipitation_risk,
    avg_temperature_risk,
    avg_wind_risk,
    avg_freeze_risk,
    avg_flood_risk,
    avg_extreme_event_probability,
    total_rate_records,
    forecast_days_covered,
    avg_base_rate,
    avg_risk_adjusted_rate,
    min_risk_adjusted_rate,
    max_risk_adjusted_rate,
    rate_stddev,
    avg_confidence_level,
    avg_risk_multiplier,
    avg_rate_volatility,
    avg_comparison_confidence,
    recommended_forecast_days_count,
    total_claims,
    claims_with_forecast,
    avg_forecast_error,
    avg_loss_amount,
    total_loss_amount,
    risk_category,
    rate_stability,
    overall_status
FROM dashboard_metrics
ORDER BY avg_overall_risk_score DESC, policy_area_id
LIMIT 500;
```

---

## Query 25: US-Wide NEXRAD Reflectivity Composite Generation {#query-25}

**Use Case:** **Real-Time Weather Monitoring - Nationwide Radar Composite for Severe Weather Detection**

**Description:** Generates US-wide composite reflectivity from all NEXRAD radar sites. Combines Level II radar data from multiple sites to create seamless nationwide coverage, handling overlapping coverage areas and data quality issues.

**Business Value:** US-wide reflectivity composite showing precipitation intensity across entire United States with seamless coverage.

**Purpose:** Provides comprehensive real-time precipitation monitoring across the entire US, enabling severe weather detection and flood forecasting at national scale.

**Complexity:** Multiple CTEs (8+ levels), multi-site data fusion, spatial interpolation, coverage optimization, quality weighting, window functions

```sql
WITH us_spatial_bounds AS (
    -- First CTE: Define US spatial bounds
    SELECT
        -125.0 AS west_bound,
        24.0 AS south_bound,
        -66.0 AS east_bound,
        50.0 AS north_bound
),
active_nexrad_sites AS (
    -- Second CTE: Get active NEXRAD sites
    SELECT
        nrs.site_id,
        nrs.site_name,
        nrs.site_latitude,
        nrs.site_longitude,
        nrs.site_geom,
        nrs.elevation_meters,
        nrs.state_code,
        nrs.cwa_code,
        nrs.coverage_radius_km,
        nrs.operational_status
    FROM nexrad_radar_sites nrs
    WHERE nrs.operational_status = 'Operational'
        AND nrs.site_geom IS NOT NULL
),
recent_nexrad_scans AS (
    -- Third CTE: Get recent NEXRAD scans (within last hour)
    SELECT DISTINCT
        nld.site_id,
        nld.scan_time,
        DATE_TRUNC('minute', nld.scan_time) AS scan_time_minute
    FROM nexrad_level2_data nld
    INNER JOIN active_nexrad_sites ans ON nld.site_id = ans.site_id
    WHERE nld.scan_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
        AND nld.decompression_status = 'Success'
        AND nld.data_type = 'Reflectivity'
        AND nld.reflectivity_dbz IS NOT NULL
),
nexrad_reflectivity_data AS (
    -- Fourth CTE: Get reflectivity data with spatial information
    SELECT
        nld.radar_data_id,
        nld.site_id,
        nld.scan_time,
        nld.elevation_angle,
        nld.azimuth_angle,
        nld.range_km,
        nld.reflectivity_dbz,
        nld.reflectivity_geom,
        ST_X(nld.reflectivity_geom::GEOMETRY) AS longitude,
        ST_Y(nld.reflectivity_geom::GEOMETRY) AS latitude,
        nld.data_quality_flag,
        ans.coverage_radius_km,
        -- Distance from radar site
        ST_DISTANCE(
            ans.site_geom,
            nld.reflectivity_geom
        ) / 1000.0 AS distance_from_site_km,
        -- Data quality weight (higher quality = higher weight)
        CASE
            WHEN nld.data_quality_flag = 0 THEN 1.0  -- Perfect quality
            WHEN nld.data_quality_flag <= 2 THEN 0.9  -- Good quality
            WHEN nld.data_quality_flag <= 4 THEN 0.7  -- Moderate quality
            ELSE 0.5  -- Lower quality
        END AS quality_weight,
        -- Distance weight (closer to radar = higher weight, but consider beam height)
        CASE
            WHEN ST_DISTANCE(ans.site_geom, nld.reflectivity_geom) / 1000.0 <= 50 THEN 1.0
            WHEN ST_DISTANCE(ans.site_geom, nld.reflectivity_geom) / 1000.0 <= 100 THEN 0.9
            WHEN ST_DISTANCE(ans.site_geom, nld.reflectivity_geom) / 1000.0 <= 150 THEN 0.7
            WHEN ST_DISTANCE(ans.site_geom, nld.reflectivity_geom) / 1000.0 <= 200 THEN 0.5
            ELSE 0.3
        END AS distance_weight
    FROM nexrad_level2_data nld
    INNER JOIN active_nexrad_sites ans ON nld.site_id = ans.site_id
    INNER JOIN recent_nexrad_scans rns ON (
        nld.site_id = rns.site_id
        AND DATE_TRUNC('minute', nld.scan_time) = rns.scan_time_minute
    )
    WHERE nld.reflectivity_dbz IS NOT NULL
        AND nld.reflectivity_geom IS NOT NULL
        AND nld.decompression_status = 'Success'
),
us_grid_cells AS (
    -- Fifth CTE: Generate US-wide grid cells (1km resolution)
    SELECT
        grid_id,
        grid_latitude,
        grid_longitude,
        ST_SETSRID(ST_MAKEPOINT(grid_longitude, grid_latitude), 4326)::GEOGRAPHY AS grid_geom
    FROM (
        SELECT
            'GRID_' || LPAD(ROW_NUMBER() OVER (ORDER BY lat, lon)::VARCHAR, 10, '0') AS grid_id,
            lat AS grid_latitude,
            lon AS grid_longitude
        FROM (
            SELECT
                generate_series(24, 50, 0.01) AS lat,
                generate_series(-125, -66, 0.01) AS lon
        ) grid_points
        WHERE lat BETWEEN 24 AND 50
            AND lon BETWEEN -125 AND -66
    ) grid
),
grid_nexrad_matching AS (
    -- Sixth CTE: Match grid cells with nearby NEXRAD data
    SELECT
        ugc.grid_id,
        ugc.grid_latitude,
        ugc.grid_longitude,
        ugc.grid_geom,
        nrd.site_id,
        nrd.reflectivity_dbz,
        nrd.distance_from_site_km,
        nrd.quality_weight,
        nrd.distance_weight,
        -- Combined weight
        nrd.quality_weight * nrd.distance_weight AS combined_weight,
        -- Inverse distance weighting
        1.0 / (nrd.distance_from_site_km + 1.0) AS inverse_distance_weight,
        ST_DISTANCE(ugc.grid_geom, nrd.reflectivity_geom) / 1000.0 AS distance_to_grid_km
    FROM us_grid_cells ugc
    INNER JOIN nexrad_reflectivity_data nrd ON (
        ST_DWITHIN(ugc.grid_geom, nrd.reflectivity_geom, 50000)  -- Within 50km
    )
),
weighted_reflectivity_calculation AS (
    -- Seventh CTE: Calculate weighted reflectivity for each grid cell
    SELECT
        gnm.grid_id,
        gnm.grid_latitude,
        gnm.grid_longitude,
        gnm.grid_geom,
        COUNT(*) AS contributing_sites_count,
        -- Weighted average reflectivity
        SUM(nrd.reflectivity_dbz * nrd.combined_weight * nrd.inverse_distance_weight) /
        NULLIF(SUM(nrd.combined_weight * nrd.inverse_distance_weight), 0) AS weighted_avg_reflectivity_dbz,
        -- Maximum reflectivity
        MAX(nrd.reflectivity_dbz) AS max_reflectivity_dbz,
        -- Minimum reflectivity
        MIN(nrd.reflectivity_dbz) AS min_reflectivity_dbz,
        -- Standard deviation
        STDDEV(nrd.reflectivity_dbz) AS reflectivity_stddev_dbz,
        -- Closest site
        (ARRAY_AGG(nrd.site_id ORDER BY nrd.distance_to_grid_km))[1] AS closest_site_id,
        MIN(nrd.distance_to_grid_km) AS distance_to_closest_site_km,
        -- Data quality score
        AVG(nrd.quality_weight) AS avg_quality_weight
    FROM grid_nexrad_matching gnm
    INNER JOIN nexrad_reflectivity_data nrd ON (
        gnm.site_id = nrd.site_id
        AND gnm.reflectivity_dbz = nrd.reflectivity_dbz
    )
    GROUP BY
        gnm.grid_id,
        gnm.grid_latitude,
        gnm.grid_longitude,
        gnm.grid_geom
),
final_composite_reflectivity AS (
    -- Eighth CTE: Final composite reflectivity with quality assessment
    SELECT
        wrc.grid_id,
        wrc.grid_latitude,
        wrc.grid_longitude,
        wrc.grid_geom,
        wrc.contributing_sites_count,
        ROUND(CAST(wrc.weighted_avg_reflectivity_dbz AS NUMERIC), 2) AS composite_reflectivity_dbz,
        ROUND(CAST(wrc.max_reflectivity_dbz AS NUMERIC), 2) AS max_reflectivity_dbz,
        ROUND(CAST(wrc.min_reflectivity_dbz AS NUMERIC), 2) AS min_reflectivity_dbz,
        ROUND(CAST(wrc.reflectivity_stddev_dbz AS NUMERIC), 2) AS reflectivity_stddev_dbz,
        wrc.closest_site_id,
        ROUND(CAST(wrc.distance_to_closest_site_km AS NUMERIC), 2) AS distance_to_closest_site_km,
        ROUND(CAST(wrc.avg_quality_weight AS NUMERIC), 3) AS avg_quality_weight,
        -- Precipitation intensity classification
        CASE
            WHEN wrc.weighted_avg_reflectivity_dbz >= 50 THEN 'Extreme'
            WHEN wrc.weighted_avg_reflectivity_dbz >= 40 THEN 'Heavy'
            WHEN wrc.weighted_avg_reflectivity_dbz >= 30 THEN 'Moderate'
            WHEN wrc.weighted_avg_reflectivity_dbz >= 20 THEN 'Light'
            WHEN wrc.weighted_avg_reflectivity_dbz >= 10 THEN 'Very Light'
            ELSE 'None'
        END AS precipitation_intensity,
        -- Data coverage quality
        CASE
            WHEN wrc.contributing_sites_count >= 3 THEN 'Excellent'
            WHEN wrc.contributing_sites_count = 2 THEN 'Good'
            WHEN wrc.contributing_sites_count = 1 THEN 'Fair'
            ELSE 'Poor'
        END AS coverage_quality
    FROM weighted_reflectivity_calculation wrc
    WHERE wrc.weighted_avg_reflectivity_dbz IS NOT NULL
)
SELECT
    grid_id,
    grid_latitude,
    grid_longitude,
    composite_reflectivity_dbz,
    max_reflectivity_dbz,
    min_reflectivity_dbz,
    reflectivity_stddev_dbz,
    contributing_sites_count,
    closest_site_id,
    distance_to_closest_site_km,
    avg_quality_weight,
    precipitation_intensity,
    coverage_quality
FROM final_composite_reflectivity
WHERE grid_latitude BETWEEN 24 AND 50
    AND grid_longitude BETWEEN -125 AND -66
ORDER BY grid_latitude, grid_longitude
LIMIT 100000;
```

---

## Query 26: NEXRAD Storm Cell Tracking and Movement Analysis {#query-26}

**Use Case:** **Severe Weather Forecasting - Multi-Site Storm Cell Tracking for Tornado and Severe Thunderstorm Prediction**

**Description:** Tracks storm cells across multiple NEXRAD radar sites and analyzes their movement, intensity changes, and development patterns. Handles storm cell merging, splitting, and dissipation across the entire US.

**Business Value:** Enables severe weather prediction and warning systems by tracking storm development and movement patterns across radar networks.

**Purpose:** Storm cell tracking report showing storm movement, intensity trends, and predicted paths across multiple radar sites.

**Business Value:** Enables severe weather prediction and warning systems by tracking storm development and movement patterns across radar networks.

**Complexity:** Multiple CTEs (9+ levels), temporal tracking, spatial matching, storm cell association, movement calculation, window functions, recursive patterns

```sql
WITH time_window AS (
    -- First CTE: Define time window for tracking (last 2 hours)
    SELECT
        CURRENT_TIMESTAMP - INTERVAL '2 hours' AS window_start,
        CURRENT_TIMESTAMP AS window_end
),
storm_cells_by_scan AS (
    -- Second CTE: Get storm cells detected at each scan time
    SELECT
        nsc.storm_cell_id,
        nsc.site_id,
        nsc.first_detection_time,
        nsc.last_detection_time,
        nsc.storm_center_latitude,
        nsc.storm_center_longitude,
        nsc.storm_center_geom,
        nsc.max_reflectivity_dbz,
        nsc.storm_area_km2,
        nsc.storm_severity,
        nsc.storm_type,
        DATE_TRUNC('minute', nsc.first_detection_time) AS scan_time_minute,
        -- Calculate scan number (sequential)
        ROW_NUMBER() OVER (
            PARTITION BY nsc.site_id
            ORDER BY nsc.first_detection_time
        ) AS scan_number
    FROM nexrad_storm_cells nsc
    WHERE nsc.first_detection_time BETWEEN (
        SELECT window_start FROM time_window
    ) AND (
        SELECT window_end FROM time_window
    )
        AND nsc.tracking_status = 'Active'
        AND nsc.storm_center_geom IS NOT NULL
),
storm_cell_movement AS (
    -- Third CTE: Calculate storm cell movement between scans
    SELECT
        scbs1.storm_cell_id AS storm_cell_id_1,
        scbs1.site_id AS site_id_1,
        scbs1.scan_time_minute AS scan_time_1,
        scbs1.storm_center_latitude AS lat_1,
        scbs1.storm_center_longitude AS lon_1,
        scbs1.storm_center_geom AS geom_1,
        scbs1.max_reflectivity_dbz AS reflectivity_1,
        scbs1.storm_area_km2 AS area_1,
        scbs1.scan_number AS scan_num_1,
        scbs2.storm_cell_id AS storm_cell_id_2,
        scbs2.site_id AS site_id_2,
        scbs2.scan_time_minute AS scan_time_2,
        scbs2.storm_center_latitude AS lat_2,
        scbs2.storm_center_longitude AS lon_2,
        scbs2.storm_center_geom AS geom_2,
        scbs2.max_reflectivity_dbz AS reflectivity_2,
        scbs2.storm_area_km2 AS area_2,
        scbs2.scan_number AS scan_num_2,
        -- Distance between storm centers
        ST_DISTANCE(scbs1.storm_center_geom, scbs2.storm_center_geom) / 1000.0 AS distance_km,
        -- Time difference in minutes
        EXTRACT(EPOCH FROM (scbs2.scan_time_minute - scbs1.scan_time_minute)) / 60.0 AS time_diff_minutes,
        -- Movement speed (km/h)
        CASE
            WHEN EXTRACT(EPOCH FROM (scbs2.scan_time_minute - scbs1.scan_time_minute)) > 0 THEN
                (ST_DISTANCE(scbs1.storm_center_geom, scbs2.storm_center_geom) / 1000.0) /
                (EXTRACT(EPOCH FROM (scbs2.scan_time_minute - scbs1.scan_time_minute)) / 3600.0)
            ELSE NULL
        END AS movement_speed_kmh,
        -- Movement direction (degrees from north)
        DEGREES(
            ATAN2(
                ST_X(scbs2.storm_center_geom::GEOMETRY) - ST_X(scbs1.storm_center_geom::GEOMETRY),
                ST_Y(scbs2.storm_center_geom::GEOMETRY) - ST_Y(scbs1.storm_center_geom::GEOMETRY)
            )
        ) AS movement_direction_deg,
        -- Reflectivity change
        scbs2.max_reflectivity_dbz - scbs1.max_reflectivity_dbz AS reflectivity_change_dbz,
        -- Area change
        scbs2.storm_area_km2 - scbs1.storm_area_km2 AS area_change_km2
    FROM storm_cells_by_scan scbs1
    INNER JOIN storm_cells_by_scan scbs2 ON (
        scbs1.site_id = scbs2.site_id
        AND scbs2.scan_number = scbs1.scan_number + 1
    )
),
storm_cell_association AS (
    -- Fourth CTE: Associate storm cells across sites (same storm detected by multiple radars)
    SELECT
        scm.storm_cell_id_1,
        scm.site_id_1,
        scm.scan_time_1,
        scm.lat_1,
        scm.lon_1,
        scm.reflectivity_1,
        scm.area_1,
        scm.storm_cell_id_2,
        scm.site_id_2,
        scm.scan_time_2,
        scm.lat_2,
        scm.lon_2,
        scm.reflectivity_2,
        scm.area_2,
        scm.distance_km,
        scm.time_diff_minutes,
        ROUND(CAST(scm.movement_speed_kmh AS NUMERIC), 2) AS movement_speed_kmh,
        ROUND(CAST(scm.movement_direction_deg AS NUMERIC), 2) AS movement_direction_deg,
        ROUND(CAST(scm.reflectivity_change_dbz AS NUMERIC), 2) AS reflectivity_change_dbz,
        ROUND(CAST(scm.area_change_km2 AS NUMERIC), 2) AS area_change_km2,
        -- Association confidence (same storm if close in space and time)
        CASE
            WHEN scm.distance_km < 20 AND scm.time_diff_minutes < 10 THEN 'High Confidence'
            WHEN scm.distance_km < 50 AND scm.time_diff_minutes < 20 THEN 'Moderate Confidence'
            WHEN scm.distance_km < 100 AND scm.time_diff_minutes < 30 THEN 'Low Confidence'
            ELSE 'Unlikely Same Storm'
        END AS association_confidence
    FROM storm_cell_movement scm
    WHERE scm.distance_km < 100  -- Only consider storms within 100km
        AND scm.time_diff_minutes BETWEEN 0 AND 30  -- Within 30 minutes
),
storm_track_aggregation AS (
    -- Fifth CTE: Aggregate storm tracks
    SELECT
        sca.storm_cell_id_1,
        sca.site_id_1,
        COUNT(DISTINCT sca.storm_cell_id_2) AS track_length,
        MIN(sca.scan_time_1) AS track_start_time,
        MAX(sca.scan_time_2) AS track_end_time,
        AVG(sca.movement_speed_kmh) AS avg_movement_speed_kmh,
        AVG(sca.movement_direction_deg) AS avg_movement_direction_deg,
        MAX(sca.reflectivity_1) AS max_reflectivity_dbz,
        MIN(sca.reflectivity_1) AS min_reflectivity_dbz,
        AVG(sca.reflectivity_1) AS avg_reflectivity_dbz,
        MAX(sca.reflectivity_change_dbz) AS max_intensification_dbz,
        MIN(sca.reflectivity_change_dbz) AS max_weakening_dbz,
        SUM(sca.area_change_km2) AS total_area_change_km2,
        -- Track distance
        SUM(sca.distance_km) AS total_track_distance_km,
        -- Track duration
        EXTRACT(EPOCH FROM (MAX(sca.scan_time_2) - MIN(sca.scan_time_1))) / 60.0 AS track_duration_minutes
    FROM storm_cell_association sca
    WHERE sca.association_confidence IN ('High Confidence', 'Moderate Confidence')
    GROUP BY
        sca.storm_cell_id_1,
        sca.site_id_1
),
storm_development_analysis AS (
    -- Sixth CTE: Analyze storm development patterns
    SELECT
        sta.storm_cell_id_1,
        sta.site_id_1,
        sta.track_length,
        sta.track_start_time,
        sta.track_end_time,
        ROUND(CAST(sta.avg_movement_speed_kmh AS NUMERIC), 2) AS avg_movement_speed_kmh,
        ROUND(CAST(sta.avg_movement_direction_deg AS NUMERIC), 2) AS avg_movement_direction_deg,
        ROUND(CAST(sta.max_reflectivity_dbz AS NUMERIC), 2) AS max_reflectivity_dbz,
        ROUND(CAST(sta.min_reflectivity_dbz AS NUMERIC), 2) AS min_reflectivity_dbz,
        ROUND(CAST(sta.avg_reflectivity_dbz AS NUMERIC), 2) AS avg_reflectivity_dbz,
        ROUND(CAST(sta.max_intensification_dbz AS NUMERIC), 2) AS max_intensification_dbz,
        ROUND(CAST(sta.max_weakening_dbz AS NUMERIC), 2) AS max_weakening_dbz,
        ROUND(CAST(sta.total_area_change_km2 AS NUMERIC), 2) AS total_area_change_km2,
        ROUND(CAST(sta.total_track_distance_km AS NUMERIC), 2) AS total_track_distance_km,
        ROUND(CAST(sta.track_duration_minutes AS NUMERIC), 2) AS track_duration_minutes,
        -- Development trend
        CASE
            WHEN sta.max_intensification_dbz > 10 THEN 'Rapidly Intensifying'
            WHEN sta.max_intensification_dbz > 5 THEN 'Intensifying'
            WHEN sta.max_weakening_dbz < -10 THEN 'Rapidly Weakening'
            WHEN sta.max_weakening_dbz < -5 THEN 'Weakening'
            ELSE 'Stable'
        END AS development_trend,
        -- Severity classification
        CASE
            WHEN sta.max_reflectivity_dbz >= 60 THEN 'Extreme'
            WHEN sta.max_reflectivity_dbz >= 50 THEN 'Severe'
            WHEN sta.max_reflectivity_dbz >= 40 THEN 'Strong'
            WHEN sta.max_reflectivity_dbz >= 30 THEN 'Moderate'
            ELSE 'Weak'
        END AS severity_classification
    FROM storm_track_aggregation sta
),
predicted_storm_path AS (
    -- Seventh CTE: Predict storm path based on movement
    SELECT
        sda.storm_cell_id_1,
        sda.site_id_1,
        sda.track_length,
        sda.track_start_time,
        sda.track_end_time,
        sda.avg_movement_speed_kmh,
        sda.avg_movement_direction_deg,
        sda.max_reflectivity_dbz,
        sda.avg_reflectivity_dbz,
        sda.development_trend,
        sda.severity_classification,
        -- Predicted position in 1 hour (using average movement)
        CASE
            WHEN sda.avg_movement_speed_kmh IS NOT NULL AND sda.avg_movement_direction_deg IS NOT NULL THEN
                ST_TRANSLATE(
                    (SELECT storm_center_geom FROM nexrad_storm_cells WHERE storm_cell_id = sda.storm_cell_id_1),
                    sda.avg_movement_speed_kmh * 1.0 * SIN(RADIANS(sda.avg_movement_direction_deg)) * 1000.0,
                    sda.avg_movement_speed_kmh * 1.0 * COS(RADIANS(sda.avg_movement_direction_deg)) * 1000.0
                )
            ELSE NULL
        END AS predicted_position_1h_geom,
        -- Predicted position in 2 hours
        CASE
            WHEN sda.avg_movement_speed_kmh IS NOT NULL AND sda.avg_movement_direction_deg IS NOT NULL THEN
                ST_TRANSLATE(
                    (SELECT storm_center_geom FROM nexrad_storm_cells WHERE storm_cell_id = sda.storm_cell_id_1),
                    sda.avg_movement_speed_kmh * 2.0 * SIN(RADIANS(sda.avg_movement_direction_deg)) * 1000.0,
                    sda.avg_movement_speed_kmh * 2.0 * COS(RADIANS(sda.avg_movement_direction_deg)) * 1000.0
                )
            ELSE NULL
        END AS predicted_position_2h_geom
    FROM storm_development_analysis sda
)
SELECT
    storm_cell_id_1,
    site_id_1,
    track_length,
    track_start_time,
    track_end_time,
    avg_movement_speed_kmh,
    avg_movement_direction_deg,
    max_reflectivity_dbz,
    avg_reflectivity_dbz,
    development_trend,
    severity_classification,
    predicted_position_1h_geom,
    predicted_position_2h_geom
FROM predicted_storm_path
WHERE track_length >= 2  -- At least 2 scans for tracking
ORDER BY max_reflectivity_dbz DESC, track_start_time DESC
LIMIT 1000;
```

---

## Query 27: US-Wide Satellite Imagery Cloud Composite Generation {#query-27}

**Use Case:** **Cloud Monitoring - Nationwide Cloud Coverage Analysis from GOES Satellite Imagery**

**Description:** Generates US-wide cloud composite from decompressed GOES satellite imagery. Combines multiple satellite bands and products to create seamless cloud coverage maps across the entire United States.

**Business Value:** US-wide cloud composite showing cloud coverage, cloud top heights, and cloud properties across entire United States.

**Purpose:** Provides comprehensive cloud monitoring for solar energy forecasting, aviation weather, and climate analysis at national scale.

**Complexity:** Multiple CTEs (7+ levels), multi-band satellite data fusion, cloud property extraction, spatial interpolation, temporal alignment

```sql
WITH us_spatial_bounds AS (
    -- First CTE: Define US spatial bounds
    SELECT
        -125.0 AS west_bound,
        24.0 AS south_bound,
        -66.0 AS east_bound,
        50.0 AS north_bound
),
active_satellite_sources AS (
    -- Second CTE: Get active satellite sources
    SELECT
        sis.source_id,
        sis.satellite_name,
        sis.satellite_type,
        sis.sensor_name,
        sis.coverage_area,
        sis.spatial_resolution_km,
        sis.scan_frequency_minutes,
        sis.operational_status
    FROM satellite_imagery_sources sis
    WHERE sis.operational_status = 'Operational'
        AND sis.coverage_area IN ('CONUS', 'Full Disk')
),
recent_satellite_scans AS (
    -- Third CTE: Get recent satellite scans (within last hour)
    SELECT DISTINCT
        sip.source_id,
        sip.scan_start_time,
        sip.product_type,
        DATE_TRUNC('minute', sip.scan_start_time) AS scan_time_minute
    FROM satellite_imagery_products sip
    INNER JOIN active_satellite_sources ass ON sip.source_id = ass.source_id
    WHERE sip.scan_start_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
        AND sip.decompression_status = 'Success'
        AND sip.product_type IN ('Cloud', 'Temperature', 'Moisture')
),
satellite_cloud_data AS (
    -- Fourth CTE: Get cloud-related satellite data
    SELECT
        sip.product_id,
        sip.source_id,
        sip.scan_start_time,
        sip.grid_latitude,
        sip.grid_longitude,
        sip.grid_geom,
        sip.band_number,
        sip.band_name,
        sip.brightness_temperature_k,
        sip.reflectance_percent,
        sip.cloud_top_height_m,
        sip.cloud_top_temperature_k,
        sip.cloud_phase,
        sip.cloud_optical_depth,
        sip.pixel_value,
        sip.calibrated_value,
        ass.spatial_resolution_km
    FROM satellite_imagery_products sip
    INNER JOIN active_satellite_sources ass ON sip.source_id = ass.source_id
    INNER JOIN recent_satellite_scans rss ON (
        sip.source_id = rss.source_id
        AND DATE_TRUNC('minute', sip.scan_start_time) = rss.scan_time_minute
        AND sip.product_type = rss.product_type
    )
    WHERE sip.grid_geom IS NOT NULL
        AND sip.decompression_status = 'Success'
),
us_grid_cells AS (
    -- Fifth CTE: Generate US-wide grid cells (2km resolution for satellite data)
    SELECT
        grid_id,
        grid_latitude,
        grid_longitude,
        ST_SETSRID(ST_MAKEPOINT(grid_longitude, grid_latitude), 4326)::GEOGRAPHY AS grid_geom
    FROM (
        SELECT
            'SAT_GRID_' || LPAD(ROW_NUMBER() OVER (ORDER BY lat, lon)::VARCHAR, 10, '0') AS grid_id,
            lat AS grid_latitude,
            lon AS grid_longitude
        FROM (
            SELECT
                generate_series(24, 50, 0.02) AS lat,
                generate_series(-125, -66, 0.02) AS lon
        ) grid_points
        WHERE lat BETWEEN 24 AND 50
            AND lon BETWEEN -125 AND -66
    ) grid
),
grid_satellite_matching AS (
    -- Sixth CTE: Match grid cells with satellite data
    SELECT
        ugc.grid_id,
        ugc.grid_latitude,
        ugc.grid_longitude,
        ugc.grid_geom,
        scd.source_id,
        scd.band_number,
        scd.band_name,
        scd.cloud_top_height_m,
        scd.cloud_top_temperature_k,
        scd.cloud_phase,
        scd.cloud_optical_depth,
        scd.brightness_temperature_k,
        scd.reflectance_percent,
        scd.spatial_resolution_km,
        ST_DISTANCE(ugc.grid_geom, scd.grid_geom) / 1000.0 AS distance_to_satellite_km
    FROM us_grid_cells ugc
    INNER JOIN satellite_cloud_data scd ON (
        ST_DWITHIN(ugc.grid_geom, scd.grid_geom, 10000)  -- Within 10km
    )
),
cloud_property_aggregation AS (
    -- Seventh CTE: Aggregate cloud properties for each grid cell
    SELECT
        gsm.grid_id,
        gsm.grid_latitude,
        gsm.grid_longitude,
        gsm.grid_geom,
        COUNT(DISTINCT gsm.source_id) AS contributing_sources_count,
        COUNT(*) AS pixel_count,
        -- Cloud top height
        MAX(gsm.cloud_top_height_m) AS max_cloud_top_height_m,
        AVG(gsm.cloud_top_height_m) AS avg_cloud_top_height_m,
        MIN(gsm.cloud_top_height_m) AS min_cloud_top_height_m,
        -- Cloud top temperature
        MIN(gsm.cloud_top_temperature_k) AS min_cloud_top_temperature_k,
        AVG(gsm.cloud_top_temperature_k) AS avg_cloud_top_temperature_k,
        MAX(gsm.cloud_top_temperature_k) AS max_cloud_top_temperature_k,
        -- Cloud optical depth
        AVG(gsm.cloud_optical_depth) AS avg_cloud_optical_depth,
        MAX(gsm.cloud_optical_depth) AS max_cloud_optical_depth,
        -- Cloud phase distribution
        COUNT(CASE WHEN gsm.cloud_phase = 'Liquid' THEN 1 END) AS liquid_cloud_count,
        COUNT(CASE WHEN gsm.cloud_phase = 'Ice' THEN 1 END) AS ice_cloud_count,
        COUNT(CASE WHEN gsm.cloud_phase = 'Mixed' THEN 1 END) AS mixed_cloud_count,
        -- Brightness temperature (for IR bands)
        AVG(gsm.brightness_temperature_k) AS avg_brightness_temperature_k,
        MIN(gsm.brightness_temperature_k) AS min_brightness_temperature_k,
        -- Reflectance (for visible bands)
        AVG(gsm.reflectance_percent) AS avg_reflectance_percent,
        MAX(gsm.reflectance_percent) AS max_reflectance_percent
    FROM grid_satellite_matching gsm
    WHERE gsm.cloud_top_height_m IS NOT NULL
    GROUP BY
        gsm.grid_id,
        gsm.grid_latitude,
        gsm.grid_longitude,
        gsm.grid_geom
),
final_cloud_composite AS (
    -- Eighth CTE: Final cloud composite with classifications
    SELECT
        cpa.grid_id,
        cpa.grid_latitude,
        cpa.grid_longitude,
        cpa.contributing_sources_count,
        cpa.pixel_count,
        ROUND(CAST(cpa.max_cloud_top_height_m AS NUMERIC), 0) AS max_cloud_top_height_m,
        ROUND(CAST(cpa.avg_cloud_top_height_m AS NUMERIC), 0) AS avg_cloud_top_height_m,
        ROUND(CAST(cpa.min_cloud_top_height_m AS NUMERIC), 0) AS min_cloud_top_height_m,
        ROUND(CAST(cpa.min_cloud_top_temperature_k AS NUMERIC), 2) AS min_cloud_top_temperature_k,
        ROUND(CAST(cpa.avg_cloud_top_temperature_k AS NUMERIC), 2) AS avg_cloud_top_temperature_k,
        ROUND(CAST(cpa.avg_cloud_optical_depth AS NUMERIC), 4) AS avg_cloud_optical_depth,
        ROUND(CAST(cpa.max_cloud_optical_depth AS NUMERIC), 4) AS max_cloud_optical_depth,
        cpa.liquid_cloud_count,
        cpa.ice_cloud_count,
        cpa.mixed_cloud_count,
        -- Dominant cloud phase
        CASE
            WHEN cpa.liquid_cloud_count > cpa.ice_cloud_count AND cpa.liquid_cloud_count > cpa.mixed_cloud_count THEN 'Liquid'
            WHEN cpa.ice_cloud_count > cpa.mixed_cloud_count THEN 'Ice'
            WHEN cpa.mixed_cloud_count > 0 THEN 'Mixed'
            ELSE 'Unknown'
        END AS dominant_cloud_phase,
        -- Cloud coverage percentage
        CASE
            WHEN cpa.pixel_count > 0 THEN
                (cpa.pixel_count::NUMERIC / (cpa.pixel_count + 1)::NUMERIC) * 100
            ELSE 0
        END AS cloud_coverage_percent,
        -- Cloud height classification
        CASE
            WHEN cpa.max_cloud_top_height_m >= 12000 THEN 'High Clouds (Cirrus)'
            WHEN cpa.max_cloud_top_height_m >= 6000 THEN 'Mid-Level Clouds'
            WHEN cpa.max_cloud_top_height_m >= 2000 THEN 'Low Clouds'
            WHEN cpa.max_cloud_top_height_m IS NOT NULL THEN 'Very Low Clouds'
            ELSE 'No Cloud Data'
        END AS cloud_height_classification,
        -- Cloud thickness classification
        CASE
            WHEN cpa.max_cloud_top_height_m - cpa.min_cloud_top_height_m >= 5000 THEN 'Very Thick'
            WHEN cpa.max_cloud_top_height_m - cpa.min_cloud_top_height_m >= 3000 THEN 'Thick'
            WHEN cpa.max_cloud_top_height_m - cpa.min_cloud_top_height_m >= 1000 THEN 'Moderate'
            WHEN cpa.max_cloud_top_height_m - cpa.min_cloud_top_height_m >= 500 THEN 'Thin'
            ELSE 'Very Thin'
        END AS cloud_thickness_classification
    FROM cloud_property_aggregation cpa
    WHERE cpa.max_cloud_top_height_m IS NOT NULL
)
SELECT
    grid_id,
    grid_latitude,
    grid_longitude,
    contributing_sources_count,
    pixel_count,
    max_cloud_top_height_m,
    avg_cloud_top_height_m,
    min_cloud_top_height_m,
    min_cloud_top_temperature_k,
    avg_cloud_top_temperature_k,
    avg_cloud_optical_depth,
    max_cloud_optical_depth,
    liquid_cloud_count,
    ice_cloud_count,
    mixed_cloud_count,
    dominant_cloud_phase,
    ROUND(CAST(cloud_coverage_percent AS NUMERIC), 2) AS cloud_coverage_percent,
    cloud_height_classification,
    cloud_thickness_classification
FROM final_cloud_composite
WHERE grid_latitude BETWEEN 24 AND 50
    AND grid_longitude BETWEEN -125 AND -66
ORDER BY grid_latitude, grid_longitude
LIMIT 50000;
```

---

## Query 28: NEXRAD-Satellite Data Fusion for Precipitation Estimation {#query-28}

**Use Case:** **Precipitation Monitoring - Multi-Source Precipitation Estimation Combining Radar and Satellite Data**

**Description:** Fuses NEXRAD radar reflectivity and satellite precipitation estimates to create improved US-wide precipitation maps. Combines strengths of both data sources for more accurate precipitation estimation.

**Business Value:** Provides more accurate and comprehensive precipitation estimates by combining radar (high resolution) and satellite (wide coverage) data sources.

**Purpose:** Fused precipitation product combining NEXRAD and satellite data with improved accuracy and coverage.

**Business Value:** Provides more accurate and comprehensive precipitation estimates by combining radar (high resolution) and satellite (wide coverage) data sources.

**Complexity:** Multiple CTEs (8+ levels), multi-source data fusion, weighted combination, quality assessment, spatial matching, temporal alignment

```sql
WITH us_spatial_bounds AS (
    -- First CTE: Define US spatial bounds
    SELECT
        -125.0 AS west_bound,
        24.0 AS south_bound,
        -66.0 AS east_bound,
        50.0 AS north_bound
),
recent_nexrad_precipitation AS (
    -- Second CTE: Get recent NEXRAD precipitation estimates
    SELECT
        nrg.grid_id,
        nrg.site_id,
        nrg.scan_time,
        nrg.grid_latitude,
        nrg.grid_longitude,
        nrg.grid_geom,
        nrg.precipitation_rate_mmh,
        nrg.accumulated_precipitation_mm,
        nrg.max_reflectivity_dbz,
        nrg.composite_reflectivity_dbz,
        -- NEXRAD data quality (higher reflectivity = more reliable)
        CASE
            WHEN nrg.max_reflectivity_dbz >= 30 THEN 0.9  -- High quality
            WHEN nrg.max_reflectivity_dbz >= 20 THEN 0.7  -- Moderate quality
            WHEN nrg.max_reflectivity_dbz >= 10 THEN 0.5  -- Lower quality
            ELSE 0.3
        END AS nexrad_quality_weight,
        -- Distance from radar (closer = more reliable)
        ST_DISTANCE(
            nrs.site_geom,
            nrg.grid_geom
        ) / 1000.0 AS distance_from_radar_km
    FROM nexrad_reflectivity_grid nrg
    INNER JOIN nexrad_radar_sites nrs ON nrg.site_id = nrs.site_id
    WHERE nrg.scan_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
        AND nrg.precipitation_rate_mmh IS NOT NULL
        AND nrg.grid_geom IS NOT NULL
),
recent_satellite_precipitation AS (
    -- Third CTE: Get recent satellite precipitation estimates
    SELECT
        sip.product_id,
        sip.source_id,
        sip.scan_start_time,
        sip.grid_latitude,
        sip.grid_longitude,
        sip.grid_geom,
        sip.precipitation_rate_mmh,
        sip.brightness_temperature_k,
        sip.cloud_top_height_m,
        -- Satellite data quality (lower brightness temp = more reliable for precipitation)
        CASE
            WHEN sip.brightness_temperature_k < 240 THEN 0.8  -- High quality (cold clouds)
            WHEN sip.brightness_temperature_k < 260 THEN 0.6  -- Moderate quality
            WHEN sip.brightness_temperature_k < 280 THEN 0.4  -- Lower quality
            ELSE 0.2
        END AS satellite_quality_weight
    FROM satellite_imagery_products sip
    WHERE sip.scan_start_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
        AND sip.product_type = 'Precipitation'
        AND sip.precipitation_rate_mmh IS NOT NULL
        AND sip.grid_geom IS NOT NULL
        AND sip.decompression_status = 'Success'
),
us_precipitation_grid AS (
    -- Fourth CTE: Generate US-wide precipitation grid
    SELECT
        grid_id,
        grid_latitude,
        grid_longitude,
        ST_SETSRID(ST_MAKEPOINT(grid_longitude, grid_latitude), 4326)::GEOGRAPHY AS grid_geom
    FROM (
        SELECT
            'PRECIP_GRID_' || LPAD(ROW_NUMBER() OVER (ORDER BY lat, lon)::VARCHAR, 10, '0') AS grid_id,
            lat AS grid_latitude,
            lon AS grid_longitude
        FROM (
            SELECT
                generate_series(24, 50, 0.01) AS lat,
                generate_series(-125, -66, 0.01) AS lon
        ) grid_points
        WHERE lat BETWEEN 24 AND 50
            AND lon BETWEEN -125 AND -66
    ) grid
),
grid_nexrad_matching AS (
    -- Fifth CTE: Match grid cells with NEXRAD data
    SELECT
        upg.grid_id,
        upg.grid_latitude,
        upg.grid_longitude,
        upg.grid_geom,
        rnp.precipitation_rate_mmh AS nexrad_precip_rate,
        rnp.accumulated_precipitation_mm AS nexrad_accumulated,
        rnp.max_reflectivity_dbz,
        rnp.nexrad_quality_weight,
        rnp.distance_from_radar_km,
        ST_DISTANCE(upg.grid_geom, rnp.grid_geom) / 1000.0 AS distance_to_nexrad_km
    FROM us_precipitation_grid upg
    INNER JOIN recent_nexrad_precipitation rnp ON (
        ST_DWITHIN(upg.grid_geom, rnp.grid_geom, 50000)  -- Within 50km
    )
),
grid_satellite_matching AS (
    -- Sixth CTE: Match grid cells with satellite data
    SELECT
        upg.grid_id,
        upg.grid_latitude,
        upg.grid_longitude,
        upg.grid_geom,
        rsp.precipitation_rate_mmh AS satellite_precip_rate,
        rsp.brightness_temperature_k,
        rsp.cloud_top_height_m,
        rsp.satellite_quality_weight,
        ST_DISTANCE(upg.grid_geom, rsp.grid_geom) / 1000.0 AS distance_to_satellite_km
    FROM us_precipitation_grid upg
    INNER JOIN recent_satellite_precipitation rsp ON (
        ST_DWITHIN(upg.grid_geom, rsp.grid_geom, 10000)  -- Within 10km
    )
),
fused_precipitation_calculation AS (
    -- Seventh CTE: Calculate fused precipitation estimates
    SELECT
        COALESCE(gnm.grid_id, gsm.grid_id) AS grid_id,
        COALESCE(gnm.grid_latitude, gsm.grid_latitude) AS grid_latitude,
        COALESCE(gnm.grid_longitude, gsm.grid_longitude) AS grid_longitude,
        COALESCE(gnm.grid_geom, gsm.grid_geom) AS grid_geom,
        -- NEXRAD data
        AVG(gnm.nexrad_precip_rate) AS avg_nexrad_precip_rate,
        AVG(gnm.nexrad_accumulated) AS avg_nexrad_accumulated,
        MAX(gnm.max_reflectivity_dbz) AS max_reflectivity_dbz,
        AVG(gnm.nexrad_quality_weight) AS avg_nexrad_quality_weight,
        MIN(gnm.distance_to_nexrad_km) AS min_distance_to_nexrad_km,
        COUNT(DISTINCT gnm.grid_id) AS nexrad_data_points,
        -- Satellite data
        AVG(gsm.satellite_precip_rate) AS avg_satellite_precip_rate,
        AVG(gsm.brightness_temperature_k) AS avg_brightness_temperature_k,
        AVG(gsm.cloud_top_height_m) AS avg_cloud_top_height_m,
        AVG(gsm.satellite_quality_weight) AS avg_satellite_quality_weight,
        MIN(gsm.distance_to_satellite_km) AS min_distance_to_satellite_km,
        COUNT(DISTINCT gsm.grid_id) AS satellite_data_points
    FROM grid_nexrad_matching gnm
    FULL OUTER JOIN grid_satellite_matching gsm ON gnm.grid_id = gsm.grid_id
    GROUP BY
        COALESCE(gnm.grid_id, gsm.grid_id),
        COALESCE(gnm.grid_latitude, gsm.grid_latitude),
        COALESCE(gnm.grid_longitude, gsm.grid_longitude),
        COALESCE(gnm.grid_geom, gsm.grid_geom)
),
final_fused_precipitation AS (
    -- Eighth CTE: Final fused precipitation with weighted combination
    SELECT
        fpc.grid_id,
        fpc.grid_latitude,
        fpc.grid_longitude,
        fpc.nexrad_data_points,
        fpc.satellite_data_points,
        ROUND(CAST(fpc.avg_nexrad_precip_rate AS NUMERIC), 2) AS avg_nexrad_precip_rate,
        ROUND(CAST(fpc.avg_satellite_precip_rate AS NUMERIC), 2) AS avg_satellite_precip_rate,
        ROUND(CAST(fpc.max_reflectivity_dbz AS NUMERIC), 2) AS max_reflectivity_dbz,
        -- Fused precipitation rate (weighted combination)
        CASE
            WHEN fpc.avg_nexrad_quality_weight IS NOT NULL AND fpc.avg_satellite_quality_weight IS NOT NULL THEN
                (
                    COALESCE(fpc.avg_nexrad_precip_rate, 0) * fpc.avg_nexrad_quality_weight +
                    COALESCE(fpc.avg_satellite_precip_rate, 0) * fpc.avg_satellite_quality_weight
                ) / (fpc.avg_nexrad_quality_weight + fpc.avg_satellite_quality_weight)
            WHEN fpc.avg_nexrad_quality_weight IS NOT NULL THEN
                fpc.avg_nexrad_precip_rate
            WHEN fpc.avg_satellite_quality_weight IS NOT NULL THEN
                fpc.avg_satellite_precip_rate
            ELSE NULL
        END AS fused_precipitation_rate_mmh,
        -- Data source
        CASE
            WHEN fpc.nexrad_data_points > 0 AND fpc.satellite_data_points > 0 THEN 'Fused'
            WHEN fpc.nexrad_data_points > 0 THEN 'NEXRAD Only'
            WHEN fpc.satellite_data_points > 0 THEN 'Satellite Only'
            ELSE 'No Data'
        END AS data_source,
        -- Data quality score
        CASE
            WHEN fpc.avg_nexrad_quality_weight IS NOT NULL AND fpc.avg_satellite_quality_weight IS NOT NULL THEN
                (fpc.avg_nexrad_quality_weight + fpc.avg_satellite_quality_weight) / 2.0
            WHEN fpc.avg_nexrad_quality_weight IS NOT NULL THEN
                fpc.avg_nexrad_quality_weight
            WHEN fpc.avg_satellite_quality_weight IS NOT NULL THEN
                fpc.avg_satellite_quality_weight
            ELSE 0.0
        END AS data_quality_score,
        -- Precipitation intensity classification
        CASE
            WHEN (
                CASE
                    WHEN fpc.avg_nexrad_quality_weight IS NOT NULL AND fpc.avg_satellite_quality_weight IS NOT NULL THEN
                        (
                            COALESCE(fpc.avg_nexrad_precip_rate, 0) * fpc.avg_nexrad_quality_weight +
                            COALESCE(fpc.avg_satellite_precip_rate, 0) * fpc.avg_satellite_quality_weight
                        ) / (fpc.avg_nexrad_quality_weight + fpc.avg_satellite_quality_weight)
                    WHEN fpc.avg_nexrad_quality_weight IS NOT NULL THEN
                        fpc.avg_nexrad_precip_rate
                    WHEN fpc.avg_satellite_quality_weight IS NOT NULL THEN
                        fpc.avg_satellite_precip_rate
                    ELSE NULL
                END
            ) >= 10.0 THEN 'Heavy'
            WHEN (
                CASE
                    WHEN fpc.avg_nexrad_quality_weight IS NOT NULL AND fpc.avg_satellite_quality_weight IS NOT NULL THEN
                        (
                            COALESCE(fpc.avg_nexrad_precip_rate, 0) * fpc.avg_nexrad_quality_weight +
                            COALESCE(fpc.avg_satellite_precip_rate, 0) * fpc.avg_satellite_quality_weight
                        ) / (fpc.avg_nexrad_quality_weight + fpc.avg_satellite_quality_weight)
                    WHEN fpc.avg_nexrad_quality_weight IS NOT NULL THEN
                        fpc.avg_nexrad_precip_rate
                    WHEN fpc.avg_satellite_quality_weight IS NOT NULL THEN
                        fpc.avg_satellite_precip_rate
                    ELSE NULL
                END
            ) >= 2.5 THEN 'Moderate'
            WHEN (
                CASE
                    WHEN fpc.avg_nexrad_quality_weight IS NOT NULL AND fpc.avg_satellite_quality_weight IS NOT NULL THEN
                        (
                            COALESCE(fpc.avg_nexrad_precip_rate, 0) * fpc.avg_nexrad_quality_weight +
                            COALESCE(fpc.avg_satellite_precip_rate, 0) * fpc.avg_satellite_quality_weight
                        ) / (fpc.avg_nexrad_quality_weight + fpc.avg_satellite_quality_weight)
                    WHEN fpc.avg_nexrad_quality_weight IS NOT NULL THEN
                        fpc.avg_nexrad_precip_rate
                    WHEN fpc.avg_satellite_quality_weight IS NOT NULL THEN
                        fpc.avg_satellite_precip_rate
                    ELSE NULL
                END
            ) >= 0.5 THEN 'Light'
            WHEN (
                CASE
                    WHEN fpc.avg_nexrad_quality_weight IS NOT NULL AND fpc.avg_satellite_quality_weight IS NOT NULL THEN
                        (
                            COALESCE(fpc.avg_nexrad_precip_rate, 0) * fpc.avg_nexrad_quality_weight +
                            COALESCE(fpc.avg_satellite_precip_rate, 0) * fpc.avg_satellite_quality_weight
                        ) / (fpc.avg_nexrad_quality_weight + fpc.avg_satellite_quality_weight)
                    WHEN fpc.avg_nexrad_quality_weight IS NOT NULL THEN
                        fpc.avg_nexrad_precip_rate
                    WHEN fpc.avg_satellite_quality_weight IS NOT NULL THEN
                        fpc.avg_satellite_precip_rate
                    ELSE NULL
                END
            ) > 0 THEN 'Very Light'
            ELSE 'None'
        END AS precipitation_intensity
    FROM fused_precipitation_calculation fpc
)
SELECT
    grid_id,
    grid_latitude,
    grid_longitude,
    nexrad_data_points,
    satellite_data_points,
    avg_nexrad_precip_rate,
    avg_satellite_precip_rate,
    max_reflectivity_dbz,
    ROUND(CAST(fused_precipitation_rate_mmh AS NUMERIC), 2) AS fused_precipitation_rate_mmh,
    data_source,
    ROUND(CAST(data_quality_score AS NUMERIC), 3) AS data_quality_score,
    precipitation_intensity
FROM final_fused_precipitation
WHERE fused_precipitation_rate_mmh IS NOT NULL
    AND grid_latitude BETWEEN 24 AND 50
    AND grid_longitude BETWEEN -125 AND -66
ORDER BY grid_latitude, grid_longitude
LIMIT 100000;
```

---

## Query 29: Satellite Fire Detection and Monitoring Across US {#query-29}

**Use Case:** **Wildfire Monitoring - Nationwide Fire Detection from GOES Satellite Imagery**

**Description:** Detects and monitors fires across the entire United States using decompressed GOES satellite imagery. Analyzes fire radiative power, temperature, and development patterns for wildfire management.

**Business Value:** US-wide fire detection report showing fire locations, intensity, and development trends from satellite imagery.

**Purpose:** Enables early wildfire detection and monitoring at national scale, supporting fire management and emergency response.

**Complexity:** Multiple CTEs (6+ levels), fire detection algorithms, temporal tracking, spatial clustering, intensity analysis

```sql
WITH us_spatial_bounds AS (
    -- First CTE: Define US spatial bounds
    SELECT
        -125.0 AS west_bound,
        24.0 AS south_bound,
        -66.0 AS east_bound,
        50.0 AS north_bound
),
recent_fire_detections AS (
    -- Second CTE: Get recent fire detections from satellite imagery
    SELECT
        sip.product_id,
        sip.source_id,
        sip.scan_start_time,
        sip.grid_latitude,
        sip.grid_longitude,
        sip.grid_geom,
        sip.fire_detection_confidence,
        sip.fire_temperature_k,
        sip.fire_power_mw,
        sip.brightness_temperature_k,
        sis.satellite_name,
        sis.spatial_resolution_km
    FROM satellite_imagery_products sip
    INNER JOIN satellite_imagery_sources sis ON sip.source_id = sis.source_id
    WHERE sip.scan_start_time >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
        AND sip.decompression_status = 'Success'
        AND sip.fire_detection_confidence IS NOT NULL
        AND sip.fire_detection_confidence >= 50  -- Minimum confidence threshold
        AND sip.grid_geom IS NOT NULL
),
fire_clustering AS (
    -- Third CTE: Cluster nearby fire detections (same fire)
    SELECT
        rfd.product_id,
        rfd.source_id,
        rfd.scan_start_time,
        rfd.grid_latitude,
        rfd.grid_longitude,
        rfd.grid_geom,
        rfd.fire_detection_confidence,
        rfd.fire_temperature_k,
        rfd.fire_power_mw,
        rfd.brightness_temperature_k,
        rfd.satellite_name,
        rfd.spatial_resolution_km,
        -- Cluster ID based on proximity (fires within 5km are same cluster)
        ROW_NUMBER() OVER (
            ORDER BY rfd.scan_start_time, rfd.grid_latitude, rfd.grid_longitude
        ) AS fire_cluster_id
    FROM recent_fire_detections rfd
),
fire_cluster_aggregation AS (
    -- Fourth CTE: Aggregate fire clusters
    SELECT
        fc.fire_cluster_id,
        COUNT(*) AS detection_count,
        MIN(fc.scan_start_time) AS first_detection_time,
        MAX(fc.scan_start_time) AS last_detection_time,
        AVG(fc.grid_latitude) AS cluster_center_latitude,
        AVG(fc.grid_longitude) AS cluster_center_longitude,
        ST_SETSRID(
            ST_MAKEPOINT(AVG(ST_X(fc.grid_geom::GEOMETRY)), AVG(ST_Y(fc.grid_geom::GEOMETRY))),
            4326
        )::GEOGRAPHY AS cluster_center_geom,
        MAX(fc.fire_detection_confidence) AS max_fire_confidence,
        AVG(fc.fire_detection_confidence) AS avg_fire_confidence,
        MAX(fc.fire_temperature_k) AS max_fire_temperature_k,
        AVG(fc.fire_temperature_k) AS avg_fire_temperature_k,
        SUM(fc.fire_power_mw) AS total_fire_power_mw,
        AVG(fc.fire_power_mw) AS avg_fire_power_mw,
        MAX(fc.brightness_temperature_k) AS max_brightness_temperature_k,
        COUNT(DISTINCT fc.source_id) AS satellite_sources_count,
        -- Fire duration
        EXTRACT(EPOCH FROM (MAX(fc.scan_start_time) - MIN(fc.scan_start_time))) / 3600.0 AS fire_duration_hours
    FROM fire_clustering fc
    GROUP BY fc.fire_cluster_id
),
fire_intensity_classification AS (
    -- Fifth CTE: Classify fire intensity
    SELECT
        fca.fire_cluster_id,
        fca.detection_count,
        fca.first_detection_time,
        fca.last_detection_time,
        ROUND(CAST(fca.cluster_center_latitude AS NUMERIC), 6) AS cluster_center_latitude,
        ROUND(CAST(fca.cluster_center_longitude AS NUMERIC), 6) AS cluster_center_longitude,
        fca.cluster_center_geom,
        ROUND(CAST(fca.max_fire_confidence AS NUMERIC), 2) AS max_fire_confidence,
        ROUND(CAST(fca.avg_fire_confidence AS NUMERIC), 2) AS avg_fire_confidence,
        ROUND(CAST(fca.max_fire_temperature_k AS NUMERIC), 2) AS max_fire_temperature_k,
        ROUND(CAST(fca.avg_fire_temperature_k AS NUMERIC), 2) AS avg_fire_temperature_k,
        ROUND(CAST(fca.total_fire_power_mw AS NUMERIC), 2) AS total_fire_power_mw,
        ROUND(CAST(fca.avg_fire_power_mw AS NUMERIC), 2) AS avg_fire_power_mw,
        ROUND(CAST(fca.max_brightness_temperature_k AS NUMERIC), 2) AS max_brightness_temperature_k,
        fca.satellite_sources_count,
        ROUND(CAST(fca.fire_duration_hours AS NUMERIC), 2) AS fire_duration_hours,
        -- Fire intensity classification
        CASE
            WHEN fca.total_fire_power_mw >= 1000 THEN 'Extreme'
            WHEN fca.total_fire_power_mw >= 500 THEN 'Very High'
            WHEN fca.total_fire_power_mw >= 100 THEN 'High'
            WHEN fca.total_fire_power_mw >= 50 THEN 'Moderate'
            WHEN fca.total_fire_power_mw >= 10 THEN 'Low'
            ELSE 'Very Low'
        END AS fire_intensity_classification,
        -- Fire status
        CASE
            WHEN fca.last_detection_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour' THEN 'Active'
            WHEN fca.last_detection_time >= CURRENT_TIMESTAMP - INTERVAL '6 hours' THEN 'Recent'
            ELSE 'Inactive'
        END AS fire_status
    FROM fire_cluster_aggregation fca
    WHERE fca.total_fire_power_mw > 0
)
SELECT
    fire_cluster_id,
    detection_count,
    first_detection_time,
    last_detection_time,
    cluster_center_latitude,
    cluster_center_longitude,
    max_fire_confidence,
    avg_fire_confidence,
    max_fire_temperature_k,
    avg_fire_temperature_k,
    total_fire_power_mw,
    avg_fire_power_mw,
    max_brightness_temperature_k,
    satellite_sources_count,
    fire_duration_hours,
    fire_intensity_classification,
    fire_status
FROM fire_intensity_classification
WHERE cluster_center_latitude BETWEEN 24 AND 50
    AND cluster_center_longitude BETWEEN -125 AND -66
ORDER BY total_fire_power_mw DESC, first_detection_time DESC
LIMIT 5000;
```

---

## Query 30: US-Wide Composite Product Generation (NEXRAD + Satellite) {#query-30}

**Use Case:** **Comprehensive Weather Monitoring - Multi-Source Composite Products for National Weather Analysis**

**Description:** Generates US-wide composite products combining NEXRAD radar and satellite imagery data. Creates seamless nationwide weather products with improved coverage and accuracy.

**Purpose:** US-wide composite products combining radar and satellite data for comprehensive weather monitoring.

**Purpose:** Provides comprehensive weather monitoring by combining strengths of radar (high resolution) and satellite (wide coverage) data sources.

**Complexity:** Multiple CTEs (7+ levels), multi-source data fusion, composite generation, quality weighting, spatial interpolation

```sql
WITH us_spatial_bounds AS (
    SELECT -125.0 AS west_bound, 24.0 AS south_bound, -66.0 AS east_bound, 50.0 AS north_bound
),
recent_nexrad_data AS (
    SELECT
        nrg.site_id, nrg.scan_time, nrg.grid_latitude, nrg.grid_longitude, nrg.grid_geom,
        nrg.composite_reflectivity_dbz, nrg.precipitation_rate_mmh,
        ST_DISTANCE(nrs.site_geom, nrg.grid_geom) / 1000.0 AS distance_from_radar_km
    FROM nexrad_reflectivity_grid nrg
    INNER JOIN nexrad_radar_sites nrs ON nrg.site_id = nrs.site_id
    WHERE nrg.scan_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
        AND nrg.grid_geom IS NOT NULL
),
recent_satellite_data AS (
    SELECT
        sip.source_id, sip.scan_start_time, sip.grid_latitude, sip.grid_longitude, sip.grid_geom,
        sip.brightness_temperature_k, sip.cloud_top_height_m, sip.precipitation_rate_mmh
    FROM satellite_imagery_products sip
    WHERE sip.scan_start_time >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
        AND sip.decompression_status = 'Success'
        AND sip.grid_geom IS NOT NULL
),
us_composite_grid AS (
    SELECT
        'COMP_' || LPAD(ROW_NUMBER() OVER (ORDER BY lat, lon)::VARCHAR, 10, '0') AS grid_id,
        lat AS grid_latitude, lon AS grid_longitude,
        ST_SETSRID(ST_MAKEPOINT(lon, lat), 4326)::GEOGRAPHY AS grid_geom
    FROM (
        SELECT generate_series(24, 50, 0.01) AS lat, generate_series(-125, -66, 0.01) AS lon
    ) grid_points
    WHERE lat BETWEEN 24 AND 50 AND lon BETWEEN -125 AND -66
),
grid_data_matching AS (
    SELECT
        ucg.grid_id, ucg.grid_latitude, ucg.grid_longitude, ucg.grid_geom,
        AVG(rnd.composite_reflectivity_dbz) AS nexrad_reflectivity,
        AVG(rnd.precipitation_rate_mmh) AS nexrad_precipitation,
        AVG(rsd.brightness_temperature_k) AS satellite_temperature,
        AVG(rsd.cloud_top_height_m) AS satellite_cloud_height,
        AVG(rsd.precipitation_rate_mmh) AS satellite_precipitation,
        COUNT(DISTINCT rnd.site_id) AS nexrad_sites_count,
        COUNT(DISTINCT rsd.source_id) AS satellite_sources_count
    FROM us_composite_grid ucg
    LEFT JOIN recent_nexrad_data rnd ON ST_DWITHIN(ucg.grid_geom, rnd.grid_geom, 50000)
    LEFT JOIN recent_satellite_data rsd ON ST_DWITHIN(ucg.grid_geom, rsd.grid_geom, 10000)
    GROUP BY ucg.grid_id, ucg.grid_latitude, ucg.grid_longitude, ucg.grid_geom
),
composite_calculation AS (
    SELECT
        gdm.grid_id, gdm.grid_latitude, gdm.grid_longitude,
        gdm.nexrad_reflectivity, gdm.nexrad_precipitation,
        gdm.satellite_temperature, gdm.satellite_cloud_height, gdm.satellite_precipitation,
        gdm.nexrad_sites_count, gdm.satellite_sources_count,
        CASE
            WHEN gdm.nexrad_precipitation IS NOT NULL AND gdm.satellite_precipitation IS NOT NULL THEN
                (gdm.nexrad_precipitation * 0.6 + gdm.satellite_precipitation * 0.4)
            WHEN gdm.nexrad_precipitation IS NOT NULL THEN gdm.nexrad_precipitation
            WHEN gdm.satellite_precipitation IS NOT NULL THEN gdm.satellite_precipitation
            ELSE NULL
        END AS composite_precipitation_rate_mmh,
        CASE
            WHEN gdm.nexrad_sites_count > 0 AND gdm.satellite_sources_count > 0 THEN 'Fused'
            WHEN gdm.nexrad_sites_count > 0 THEN 'NEXRAD Only'
            WHEN gdm.satellite_sources_count > 0 THEN 'Satellite Only'
            ELSE 'No Data'
        END AS data_source
    FROM grid_data_matching gdm
)
SELECT
    grid_id, grid_latitude, grid_longitude,
    ROUND(CAST(nexrad_reflectivity AS NUMERIC), 2) AS nexrad_reflectivity_dbz,
    ROUND(CAST(nexrad_precipitation AS NUMERIC), 2) AS nexrad_precipitation_rate_mmh,
    ROUND(CAST(satellite_temperature AS NUMERIC), 2) AS satellite_temperature_k,
    ROUND(CAST(satellite_cloud_height AS NUMERIC), 0) AS satellite_cloud_height_m,
    ROUND(CAST(satellite_precipitation AS NUMERIC), 2) AS satellite_precipitation_rate_mmh,
    ROUND(CAST(composite_precipitation_rate_mmh AS NUMERIC), 2) AS composite_precipitation_rate_mmh,
    nexrad_sites_count, satellite_sources_count, data_source
FROM composite_calculation
WHERE composite_precipitation_rate_mmh IS NOT NULL
ORDER BY grid_latitude, grid_longitude
LIMIT 50000;
```

---

## Usage Instructions

1. **Database Access**: Ensure you have access to the database instance (PostgreSQL with PostGIS)
2. **Credentials**: Obtain database connection credentials
3. **Schema**: Ensure all tables are created and populated with data
4. **Spatial Extensions**: For PostgreSQL, ensure PostGIS extension is installed:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

1. **Open Query File**: Navigate to `queries/queries.md`
2. **Select Query**: Choose the query number you want to execute
3. **Review Business Case**: Understand the use case and expected output
4. **Copy SQL**: Copy the SQL code from the code block
5. **Execute**: Run the query in your database client:
   - **PostgreSQL**: Use `psql` or pgAdmin (ensure PostGIS is enabled)

- Each query includes a "Business Use Case" section explaining the real-world application
- Review the "Client Deliverable" section to understand what the query produces
- Check the "Expected Output" section for result set descriptions
- Spatial queries return geographic data that can be visualized on maps


1. Create a new notebook
2. Set the language to SQL
3. Copy the query SQL into a cell
4. Add markdown cells above for context:
   ```markdown
   # Query 1: Spatial Weather Forecast Analysis

   **Business Use Case:** Insurance Risk Modeling

   This query analyzes forecast accuracy by geographic boundary...
   ```
5. Execute the cell to run the query
6. Review results and add visualization cells:
   - Use map visualizations for spatial results
   - Create charts for time-series data
   - Generate tables for aggregated metrics

1. **Create Tables**: Execute the schema creation scripts from `data/schema.sql`
2. **Enable Spatial Extensions**: For PostgreSQL:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
3. **Create Indexes**: Ensure all indexes are created, especially spatial indexes (GIST)
4. **Load Data**: Populate tables with weather data:
   - GRIB2 forecast data
   - Shapefile boundaries
   - Weather observations
5. **Verify**: Run validation queries to ensure data integrity

- **Spatial Indexes**: Critical for spatial query performance (GIST indexes on GEOGRAPHY columns)
- **Partitioning**: Consider partitioning large tables (`grib2_forecasts`, `weather_observations`) by date
- **Aggregations**: Use `weather_forecast_aggregations` table for pre-computed aggregations
- **Monitoring**: Monitor query execution times, especially for spatial joins
- **Optimization**: Review spatial join strategies and consider spatial clustering

- **Spatial Types**:
  - PostgreSQL: Uses PostGIS GEOGRAPHY type
  : Uses GEOMETRY type (compatible)
  : Uses GEOGRAPHY type
- **Spatial Functions**: Standard spatial functions (ST_WITHIN, ST_DISTANCE, ST_INTERSECTS) work across all platforms
- **CRS Handling**: All spatial data uses WGS84 (EPSG:4326) for compatibility
- Test queries on your target database before production use

1. **GRIB2 Files**: Use transformation scripts to load GRIB2 data
2. **Shapefiles**: Use OGR2OGR or similar tools to transform and load shapefiles
3. **API Data**: Use ETL pipelines to load real-time observations from NWS API
4. **Monitoring**: Track data quality metrics using `data_quality_metrics` table

---

---

## Platform Compatibility

All queries in this database are designed to work across multiple database platforms:

- **PostgreSQL**: Full support with standard SQL features

Queries use standard SQL syntax and avoid platform-specific features to ensure compatibility.

---

**Document Information:**

- **Generated**: 20260210-0115
- **Database**: db-6
- **Type**: Weather Data Pipeline System
- **Queries**: 30 production queries
- **Status**: ✅ Complete Comprehensive Deliverable
