# DB-6 Data Sources Documentation

## Overview

The db-6 database integrates weather and climate data from multiple authoritative sources to support comprehensive weather consulting services. This document describes all data sources, their formats, update frequencies, and ingestion methods.

## Data Source Categories

### 1. AWS Open Data Registry (ASDI)

The Amazon Sustainability Data Initiative (ASDI) provides free, publicly available weather and climate datasets on AWS S3. These datasets are optimized for cloud-based analytics and distributed processing.

#### 1.1 NOAA Global Forecast System (GFS)
- **Bucket:** `noaa-gfs-bdp-pds`
- **Description:** Global weather forecast model with 0.25-degree resolution
- **Update Frequency:** 4 times daily (00Z, 06Z, 12Z, 18Z)
- **Forecast Range:** Up to 16 days (384 hours)
- **Format:** GRIB2
- **Resolution:** ~28km horizontal, 127 vertical levels
- **Parameters:** Temperature, precipitation, wind, pressure, humidity, and 50+ other variables
- **Use Cases:**
  - Long-range weather forecasting
  - Global weather pattern analysis
  - Climate risk assessment
  - Multi-day forecast planning

#### 1.2 NOAA High-Resolution Rapid Refresh (HRRR)
- **Bucket:** `noaa-hrrr-bdp-pds`
- **Description:** High-resolution, hourly-updated weather forecast model for CONUS
- **Update Frequency:** Hourly
- **Forecast Range:** Up to 48 hours
- **Format:** GRIB2
- **Resolution:** 3km horizontal
- **Parameters:** Temperature, precipitation, wind, cloud cover, visibility, and more
- **Use Cases:**
  - Short-term, high-resolution forecasting
  - Severe weather prediction
  - Aviation weather services
  - Real-time decision support

#### 1.3 NEXRAD Level II Radar Data
- **Bucket:** `noaa-nexrad-level2`
- **Description:** Next-Generation Weather Radar network data
- **Update Frequency:** Real-time (every 5-10 minutes)
- **Format:** Binary (Level II)
- **Resolution:** 1km
- **Coverage:** Contiguous United States
- **Use Cases:**
  - Real-time precipitation monitoring
  - Severe weather detection
  - Storm tracking and analysis
  - Flood forecasting

#### 1.4 National Digital Forecast Database (NDFD)
- **Bucket:** `noaa-ndfd-pds`
- **Description:** Gridded forecasts prepared by NWS forecasters
- **Update Frequency:** 6-hourly
- **Forecast Range:** Up to 8 days (192 hours)
- **Format:** GRIB2
- **Resolution:** 2.5km
- **Use Cases:**
  - Official NWS forecast products
  - Public weather services
  - Forecast verification

#### 1.5 Rapid Refresh (RAP) Model
- **Bucket:** `noaa-rap-pds`
- **Description:** Rapidly-updated short-range forecast model
- **Update Frequency:** Hourly
- **Forecast Range:** Up to 21 hours
- **Format:** GRIB2
- **Resolution:** 13km
- **Use Cases:**
  - Very short-term forecasting
  - Aviation weather
  - Nowcasting applications

#### 1.6 Global Ensemble Forecast System (GEFS)
- **Bucket:** `noaa-gefs-pds`
- **Description:** Ensemble forecast system with 21 members
- **Update Frequency:** 4 times daily
- **Forecast Range:** Up to 16 days
- **Format:** GRIB2
- **Resolution:** 0.5 degree
- **Use Cases:**
  - Forecast uncertainty quantification
  - Probabilistic forecasting
  - Risk assessment

#### 1.7 Real-Time Mesoscale Analysis (RTMA)
- **Bucket:** `noaa-rtma-pds`
- **Description:** High-resolution analysis of current conditions
- **Update Frequency:** Hourly
- **Format:** GRIB2
- **Resolution:** 2.5km
- **Use Cases:**
  - Current weather conditions
  - Model initialization
  - Verification baseline

### 2. National Weather Service API (api.weather.gov)

The NWS API provides real-time weather observations, forecasts, alerts, and station metadata through RESTful endpoints.

#### 2.1 Weather Stations
- **Endpoint:** `/stations`
- **Description:** Metadata for weather observation stations
- **Update Frequency:** Real-time
- **Format:** JSON (GeoJSON)
- **Data Includes:**
  - Station identifiers and names
  - Geographic coordinates
  - Station types (ASOS, AWOS, etc.)
  - CWA assignments
  - State and county codes
- **Use Cases:**
  - Station network analysis
  - Coverage gap identification
  - Station metadata lookup

#### 2.2 Latest Observations
- **Endpoint:** `/stations/{stationId}/observations/latest`
- **Description:** Most recent weather observations from stations
- **Update Frequency:** Real-time (updated as observations arrive)
- **Format:** JSON
- **Parameters:**
  - Temperature, dewpoint, humidity
  - Wind speed and direction
  - Barometric pressure
  - Visibility
  - Sky conditions
  - Precipitation
- **Use Cases:**
  - Real-time weather monitoring
  - Forecast validation
  - Current conditions reporting

#### 2.3 Grid Point Forecasts
- **Endpoint:** `/gridpoints/{wfo}/{x},{y}/forecast`
- **Description:** Official NWS forecasts for specific grid points
- **Update Frequency:** Multiple times daily
- **Format:** JSON
- **Forecast Elements:**
  - Temperature (high/low)
  - Probability of precipitation
  - Wind forecasts
  - Weather conditions
  - Detailed hourly forecasts
- **Use Cases:**
  - Official forecast products
  - Client-facing forecasts
  - Forecast comparison

#### 2.4 Active Alerts
- **Endpoint:** `/alerts/active/area/{area}`
- **Description:** Active weather watches, warnings, and advisories
- **Update Frequency:** Real-time
- **Format:** JSON (GeoJSON)
- **Alert Types:**
  - Tornado warnings
  - Severe thunderstorm warnings
  - Flood warnings
  - Winter weather advisories
  - Heat advisories
  - And 50+ other alert types
- **Use Cases:**
  - Emergency management
  - Risk communication
  - Alert verification

### 3. GeoPlatform.gov

GeoPlatform.gov provides access to federal geospatial datasets including administrative boundaries, geographic features, and geospatial services.

#### 3.1 Boundary Datasets
- **Catalog:** GeoPlatform.gov API
- **Description:** Administrative and geographic boundaries
- **Types:**
  - County boundaries
  - State boundaries
  - Fire weather zones
  - Marine zones
  - CWA boundaries
  - Census boundaries
- **Format:** Various (GeoJSON, Shapefile, GeoPackage)
- **Use Cases:**
  - Spatial analysis
  - Boundary-based aggregations
  - Geographic context

#### 3.2 Elevation Data
- **Sources:** USGS, NOAA
- **Description:** Digital elevation models and terrain data
- **Resolutions:** Various (1m to 90m)
- **Use Cases:**
  - Terrain analysis
  - Flood modeling
  - Wind modeling

## Data Ingestion Scripts

### Scripts Location
All ingestion scripts are located in `db-6/scripts/`:

1. **ingest_aws_opendata.py** - AWS Open Data Registry ingestion
2. **ingest_nws_api.py** - NWS API data ingestion
3. **ingest_geoplatform.py** - GeoPlatform.gov dataset discovery
4. **ingest_all_sources.py** - Master script to run all ingestions

### Usage

#### Individual Source Ingestion
```bash
# AWS Open Data
python3 scripts/ingest_aws_opendata.py

# NWS API
python3 scripts/ingest_nws_api.py

# GeoPlatform
python3 scripts/ingest_geoplatform.py
```

#### All Sources
```bash
python3 scripts/ingest_all_sources.py
```

## Database Schema Extensions

The base schema has been extended with additional tables to support multi-source data:

### New Tables

1. **aws_data_source_log** - Tracks AWS S3 data ingestion
2. **nws_api_observation_log** - Tracks NWS API calls
3. **geoplatform_dataset_log** - Tracks discovered GeoPlatform datasets
4. **weather_alerts** - Stores NWS weather alerts
5. **model_forecast_comparison** - Compares forecasts from different models
6. **data_source_statistics** - Aggregated statistics per data source

### Enhanced Tables

- **grib2_forecasts** - Added fields for model name, AWS bucket/path, ensemble members
- **weather_observations** - Added fields for API endpoint and response status

## Data Quality and Validation

### Validation Checks

1. **Temporal Consistency** - Verify observation times are reasonable
2. **Spatial Bounds** - Validate coordinates are within expected ranges
3. **Value Ranges** - Check parameters are within physical limits
4. **Completeness** - Monitor data freshness and update frequencies
5. **Cross-Source Validation** - Compare forecasts from different models

### Quality Metrics

- Data freshness (time since last update)
- Coverage (spatial and temporal)
- Completeness (percentage of expected data)
- Accuracy (forecast vs. observation comparison)

## Business Use Cases

### Custom Weather Impact Modeling
- **GFS Data:** Long-range forecasts for planning
- **HRRR Data:** High-resolution short-term forecasts
- **NWS API:** Real-time conditions and official forecasts

### Physical Climate Risk Assessment
- **GEFS Data:** Ensemble forecasts for uncertainty quantification
- **Historical GFS:** Long-term climate patterns
- **Alerts:** Extreme event documentation

### Supply Chain and Fleet Management
- **HRRR/RAP:** Short-term, high-resolution forecasts
- **NWS Observations:** Real-time conditions along routes
- **Alerts:** Weather warnings for logistics planning

### Forensic Meteorology
- **NEXRAD:** Historical radar data for event reconstruction
- **Model Comparison:** Multiple model analysis for legal cases
- **Observations:** Verified weather conditions

### Energy and Power Load Forecasting
- **GFS:** Long-range temperature forecasts
- **HRRR:** Short-term wind forecasts
- **Ensemble Data:** Uncertainty in renewable energy generation

## Data Access Patterns

### Real-Time Data
- NWS API observations (updated continuously)
- NWS alerts (updated as events occur)
- AWS data (available 3-6 hours after model runs)

### Historical Data
- AWS S3 archives (2+ years for most datasets)
- NWS API (limited historical access)
- Database storage (custom retention policies)

### Batch Processing
- Daily ingestion of latest forecasts
- Hourly updates for high-frequency data
- Weekly aggregation and statistics

## Performance Considerations

### AWS S3 Access
- Use S3 Select for filtering large files
- Leverage CloudFront for frequently accessed data
- Consider Zarr format for efficient array access

### NWS API
- Implement rate limiting (respect API guidelines)
- Cache frequently accessed data
- Use appropriate timeouts

### Database Optimization
- Partition tables by date for time-series data
- Create indexes on frequently queried columns
- Use materialized views for common aggregations

## References

- AWS Open Data Registry: https://registry.opendata.aws/
- ASDI Catalog: https://registry.opendata.aws/collab/asdi/
- NWS API Documentation: https://www.weather.gov/documentation/services-web-api
- GeoPlatform.gov: https://www.geoplatform.gov/
- NOAA GFS Documentation: https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast
- HRRR Documentation: https://rapidrefresh.noaa.gov/hrrr/
