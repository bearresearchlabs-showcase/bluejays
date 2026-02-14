# ETL Transformation Diagrams - CSV to PostgreSQL

## Overview

This file contains multiple Eraser.io diagrams detailing the ETL (Extract, Transform, Load) transformation process from CSV files stored in db-17 (Document Management System) to PostgreSQL database in db-16 (Flood Risk Assessment Database).

## Diagrams Included

### 1. Overall ETL Architecture
High-level view of the complete ETL pipeline showing:
- CSV file storage in db-17
- ETL pipeline orchestration
- Extract, Transform, Load phases
- Data quality monitoring
- Error handling

### 2. Extract Phase - CSV File Sources
Details the extraction of CSV files from db-17:
- FEMA Flood Zones CSV
- NOAA Sea Level Rise CSV
- USGS Streamflow CSV
- NASA Flood Models CSV
- Historical Flood Events CSV
- CSV reading and validation

### 3. Transform Phase - Data Cleaning and Transformation
Shows the transformation pipeline:
- Data cleaning
- Coordinate transformation
- Data enrichment
- Schema mapping
- Data normalization
- Transformation rules engine

### 4. Load Phase - PostgreSQL Loading
Details the loading process into PostgreSQL:
- Batch loading
- Connection pooling
- Loading into target tables
- Load monitoring

### 5. FEMA Flood Zones ETL Pipeline
Specific pipeline for FEMA data:
- CSV parsing
- Zone code validation
- Geometry conversion
- CRS transformation
- Base Flood Elevation calculation
- PostgreSQL loading

### 6. NOAA Sea Level Rise ETL Pipeline
Specific pipeline for NOAA data:
- Station data parsing
- Station validation
- Projection calculations
- Scenario mapping
- Coordinate transformation
- PostgreSQL loading

### 7. USGS Streamflow ETL Pipeline
Specific pipeline for USGS data:
- Gauge and observation parsing
- Gauge validation
- Flood stage calculation
- Coordinate transformation
- Loading into multiple tables

### 8. Data Quality and Validation Pipeline
Data quality assurance:
- Completeness checking
- Consistency checking
- Accuracy validation
- Quality metrics calculation
- Quality dashboard

### 9. Error Handling and Retry Logic
Error management:
- Error handling
- Retry management
- Dead letter queue
- Error logging
- Notification service

### 10. Monitoring and Observability
Pipeline monitoring:
- CloudWatch metrics
- CloudWatch logs
- X-Ray tracing
- Performance monitoring
- ETL dashboard

### 11. NASA Flood Models ETL Pipeline
Specific pipeline for NASA data:
- Model output parsing
- Model validation
- Grid cell processing
- Inundation calculation
- Probability calculation
- PostgreSQL loading

### 12. Historical Flood Events ETL Pipeline
Specific pipeline for historical events:
- Event data parsing
- Event validation
- Date parsing
- Severity classification
- Geometry conversion
- PostgreSQL loading

### 13. Complete Data Flow - CSV to PostgreSQL
End-to-end data flow:
- Complete pipeline flow
- ETL metadata tracking
- Data quality metrics
- Database loading

### 14. Spatial Data Transformation Pipeline
Spatial data handling:
- Coordinate parsing
- CRS detection and transformation
- Geometry building
- PostGIS validation
- GEOGRAPHY conversion
- Spatial index building

### 15. Batch Processing and Parallelization
Performance optimization:
- Batch splitting
- Parallel workers
- Batch coordination
- Batch monitoring

## Data Sources

### CSV Files from db-17:
1. **FEMA Flood Zones CSV** - Flood zone designations and boundaries
2. **NOAA Sea Level Rise CSV** - Sea level rise projections and tide station data
3. **USGS Streamflow CSV** - Streamflow gauge locations and observations
4. **NASA Flood Models CSV** - Flood model predictions and inundation data
5. **Historical Flood Events CSV** - Historical flood event records

### Target PostgreSQL Tables (db-16):
1. `fema_flood_zones` - FEMA flood zone data
2. `noaa_sea_level_rise` - NOAA sea level rise projections
3. `usgs_streamflow_gauges` - USGS gauge locations
4. `usgs_streamflow_observations` - USGS streamflow observations
5. `nasa_flood_models` - NASA flood model outputs
6. `historical_flood_events` - Historical flood events
7. `data_quality_metrics` - Data quality metrics

## Key Transformations

1. **Coordinate Transformation**: All coordinates transformed to EPSG:4326 (WGS84)
2. **Geometry Conversion**: CSV coordinates converted to PostGIS GEOGRAPHY type
3. **Data Validation**: Zone codes, station IDs, gauge IDs validated
4. **Schema Mapping**: CSV columns mapped to PostgreSQL table columns
5. **Data Enrichment**: Additional fields calculated (BFE, flood categories, etc.)
6. **Batch Processing**: Large CSV files processed in batches for performance

## File Location

`db-16/docs/c4/ETL_TRANSFORMATION_DIAGRAMS.code`

## Usage

Import this file into Eraser.io to visualize the complete ETL transformation process from CSV files in db-17 to PostgreSQL tables in db-16.

## Status

✅ **Complete** - All diagrams created with:
- All nodes have icons
- All nodes are connected
- Clear titles for each diagram
- Detailed transformation flows
- Error handling and monitoring
