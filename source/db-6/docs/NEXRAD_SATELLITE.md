# NEXRAD and Satellite Imagery Transformation Documentation - db-6

**Created:** 2026-02-03
**Purpose:** US-wide transformations using NEXRAD Level II radar data and decompressed satellite imagery

## Overview

The NEXRAD and satellite imagery extension enables comprehensive weather monitoring and analysis across the entire United States by processing and transforming radar and satellite data sources. The system handles decompression, gridding, fusion, and composite product generation for nationwide coverage.

## Key Features

1. **NEXRAD Level II Processing:** Decompresses and processes NEXRAD Level II radar data from 160+ radar sites
2. **Satellite Imagery Processing:** Decompresses and processes GOES satellite imagery (GOES-16, GOES-17, GOES-18)
3. **US-Wide Composites:** Generates seamless nationwide weather products
4. **Data Fusion:** Combines NEXRAD and satellite data for improved accuracy
5. **Storm Tracking:** Tracks storm cells across multiple radar sites
6. **Fire Detection:** Detects and monitors wildfires from satellite imagery
7. **Cloud Analysis:** Analyzes cloud properties from satellite imagery
8. **Precipitation Estimation:** Fuses radar and satellite data for precipitation estimates

## Database Schema

### NEXRAD Tables

#### nexrad_radar_sites
Metadata for NEXRAD radar sites across the United States.

**Key Columns:**
- `site_id` (VARCHAR(4), PK) - 4-letter site identifier (e.g., 'KTLX')
- `site_name` (VARCHAR) - Site name
- `site_latitude`, `site_longitude` (NUMERIC) - Site coordinates
- `site_geom` (GEOGRAPHY) - Point geometry
- `coverage_radius_km` (NUMERIC) - Standard coverage radius (~230km)
- `operational_status` (VARCHAR) - 'Operational', 'Maintenance', 'Offline'

#### nexrad_level2_data
Stores decompressed NEXRAD Level II radar data.

**Key Columns:**
- `radar_data_id` (VARCHAR, PK)
- `site_id` (VARCHAR(4)) - References nexrad_radar_sites
- `scan_time` (TIMESTAMP_NTZ) - Scan timestamp
- `reflectivity_dbz` (NUMERIC) - Reflectivity in dBZ
- `radial_velocity_ms` (NUMERIC) - Radial velocity in m/s
- `spectrum_width_ms` (NUMERIC) - Spectrum width
- `reflectivity_geom` (GEOGRAPHY) - Point geometry
- `decompression_status` (VARCHAR) - 'Success', 'Failed', 'Pending'

#### nexrad_reflectivity_grid
Gridded reflectivity data for easier spatial analysis.

**Key Columns:**
- `grid_id` (VARCHAR, PK)
- `site_id` (VARCHAR(4)) - References nexrad_radar_sites
- `scan_time` (TIMESTAMP_NTZ)
- `grid_latitude`, `grid_longitude` (NUMERIC)
- `grid_geom` (GEOGRAPHY) - Point geometry
- `max_reflectivity_dbz` (NUMERIC) - Maximum reflectivity
- `composite_reflectivity_dbz` (NUMERIC) - Composite reflectivity
- `precipitation_rate_mmh` (NUMERIC) - Precipitation rate

#### nexrad_storm_cells
Tracks storm cells across multiple scans.

**Key Columns:**
- `storm_cell_id` (VARCHAR, PK)
- `site_id` (VARCHAR(4)) - References nexrad_radar_sites
- `first_detection_time` (TIMESTAMP_NTZ)
- `storm_center_geom` (GEOGRAPHY) - Storm center location
- `max_reflectivity_dbz` (NUMERIC)
- `storm_severity` (VARCHAR) - 'Weak', 'Moderate', 'Strong', 'Severe', 'Extreme'
- `tracking_status` (VARCHAR) - 'Active', 'Dissipated', 'Merged'

### Satellite Imagery Tables

#### satellite_imagery_sources
Metadata for satellite imagery sources.

**Key Columns:**
- `source_id` (VARCHAR, PK)
- `satellite_name` (VARCHAR) - 'GOES-16', 'GOES-17', 'GOES-18'
- `satellite_type` (VARCHAR) - 'GOES'
- `sensor_name` (VARCHAR) - 'ABI' (Advanced Baseline Imager)
- `coverage_area` (VARCHAR) - 'CONUS', 'Full Disk', 'Mesoscale'
- `spatial_resolution_km` (NUMERIC) - Spatial resolution
- `scan_frequency_minutes` (INTEGER) - Scan frequency

#### satellite_imagery_products
Decompressed satellite imagery products.

**Key Columns:**
- `product_id` (VARCHAR, PK)
- `source_id` (VARCHAR) - References satellite_imagery_sources
- `product_type` (VARCHAR) - 'Cloud', 'Fire', 'Precipitation', 'Temperature'
- `band_number` (INTEGER) - GOES ABI band number (1-16)
- `scan_start_time` (TIMESTAMP_NTZ)
- `grid_latitude`, `grid_longitude` (NUMERIC)
- `grid_geom` (GEOGRAPHY) - Point geometry
- `brightness_temperature_k` (NUMERIC) - Brightness temperature
- `cloud_top_height_m` (NUMERIC) - Cloud top height
- `fire_detection_confidence` (NUMERIC) - Fire detection confidence
- `fire_power_mw` (NUMERIC) - Fire radiative power
- `precipitation_rate_mmh` (NUMERIC) - Precipitation rate
- `decompression_status` (VARCHAR) - 'Success', 'Failed', 'Pending'

#### us_wide_composite_products
Composite products combining NEXRAD and satellite data.

**Key Columns:**
- `composite_id` (VARCHAR, PK)
- `product_type` (VARCHAR) - 'Precipitation', 'Cloud', 'Storm', 'Fire'
- `composite_time` (TIMESTAMP_NTZ)
- `grid_latitude`, `grid_longitude` (NUMERIC)
- `grid_geom` (GEOGRAPHY) - Point geometry
- `nexrad_reflectivity_dbz` (NUMERIC)
- `satellite_brightness_temperature_k` (NUMERIC)
- `composite_precipitation_rate_mmh` (NUMERIC)
- `data_quality_score` (NUMERIC) - Overall data quality (0-100)

### Transformation Log Tables

#### nexrad_transformation_log
Tracks NEXRAD data transformation operations.

**Key Columns:**
- `transformation_id` (VARCHAR, PK)
- `site_id` (VARCHAR(4))
- `transformation_type` (VARCHAR) - 'Decompression', 'Gridding', 'StormTracking'
- `transformation_status` (VARCHAR) - 'Success', 'Failed', 'Partial'
- `transformation_duration_seconds` (INTEGER)
- `input_size_bytes` (BIGINT)
- `output_size_bytes` (BIGINT)

#### satellite_transformation_log
Tracks satellite imagery transformation operations.

**Key Columns:**
- `transformation_id` (VARCHAR, PK)
- `source_id` (VARCHAR)
- `transformation_type` (VARCHAR) - 'Decompression', 'Reprojection', 'Gridding'
- `transformation_status` (VARCHAR) - 'Success', 'Failed', 'Partial'
- `transformation_duration_seconds` (INTEGER)
- `input_size_bytes` (BIGINT)
- `output_size_bytes` (BIGINT)

## NEXRAD and Satellite Queries (41-50)

### Query 41: US-Wide NEXRAD Reflectivity Composite Generation
Generates US-wide composite reflectivity from all NEXRAD radar sites. Combines Level II radar data from multiple sites to create seamless nationwide coverage.

**Output:** US-wide reflectivity composite showing precipitation intensity across entire United States.

### Query 42: NEXRAD Storm Cell Tracking and Movement Analysis
Tracks storm cells across multiple NEXRAD radar sites and analyzes their movement, intensity changes, and development patterns.

**Output:** Storm cell tracking analysis with movement patterns, intensity changes, and predicted paths.

### Query 43: US-Wide Satellite Imagery Cloud Composite Generation
Generates US-wide cloud composite from decompressed GOES satellite imagery. Combines multiple satellite bands and products to create seamless cloud coverage maps.

**Output:** US-wide cloud composite with cloud properties and classifications.

### Query 44: NEXRAD-Satellite Data Fusion for Precipitation Estimation
Fuses NEXRAD radar reflectivity and satellite precipitation estimates to create improved US-wide precipitation maps.

**Output:** Fused precipitation product combining NEXRAD and satellite data.

### Query 45: Satellite Fire Detection and Monitoring Across US
Detects and monitors fires across the entire United States using decompressed GOES satellite imagery.

**Output:** US-wide fire detection report with fire locations, intensity, and status.

### Query 46: US-Wide Composite Product Generation (NEXRAD + Satellite)
Generates US-wide composite products combining NEXRAD radar and satellite imagery data.

**Output:** US-wide composite products combining NEXRAD and satellite data.

### Query 47: NEXRAD Transformation Performance Analysis
Analyzes NEXRAD transformation performance across all radar sites.

**Output:** NEXRAD transformation performance metrics by site and transformation type.

### Query 48: Satellite Imagery Transformation Performance Analysis
Analyzes satellite imagery transformation performance.

**Output:** Satellite transformation performance metrics by source and transformation type.

### Query 49: US-Wide Data Coverage Analysis
Analyzes data coverage across the entire United States for both NEXRAD and satellite data sources.

**Output:** US-wide coverage analysis showing data availability by grid cell.

### Query 50: Comprehensive NEXRAD-Satellite Transformation Summary
Provides comprehensive summary of all NEXRAD and satellite transformations across the entire United States.

**Output:** Comprehensive transformation summary dashboard with all key metrics.

## Data Sources

### NEXRAD Level II Data
- **Source:** AWS S3 bucket `noaa-nexrad-level2`
- **Format:** Binary Level II format
- **Coverage:** 160+ radar sites across contiguous United States
- **Update Frequency:** Every 5-10 minutes
- **Resolution:** ~1km
- **Decompression:** Required before processing

### GOES Satellite Imagery
- **Source:** AWS S3 buckets for GOES-16, GOES-17, GOES-18
- **Format:** NetCDF, HDF5
- **Coverage:** CONUS, Full Disk, Mesoscale
- **Update Frequency:** 5-15 minutes depending on scan mode
- **Resolution:** 0.5km to 2km depending on band
- **Decompression:** Required before processing

## Transformation Workflow

1. **Data Ingestion:** Download NEXRAD and satellite data from AWS S3
2. **Decompression:** Decompress binary/compressed formats
3. **Gridding:** Convert point/radial data to regular grids
4. **Quality Control:** Assess data quality and flag issues
5. **Spatial Interpolation:** Fill gaps and create seamless coverage
6. **Data Fusion:** Combine multiple data sources
7. **Product Generation:** Create composite products
8. **Storage:** Store transformed data in database

## Usage Examples

### Generate US-Wide Reflectivity Composite

```sql
-- Use Query 41 to generate US-wide reflectivity composite
SELECT * FROM nexrad_reflectivity_grid
WHERE scan_time >= CURRENT_TIMESTAMP() - INTERVAL '1 hour'
ORDER BY scan_time DESC, grid_latitude, grid_longitude;
```

### Track Storm Cells

```sql
-- Use Query 42 to track storm cells
SELECT * FROM nexrad_storm_cells
WHERE tracking_status = 'Active'
    AND first_detection_time >= CURRENT_TIMESTAMP() - INTERVAL '2 hours'
ORDER BY max_reflectivity_dbz DESC;
```

### Detect Fires

```sql
-- Use Query 45 to detect fires
SELECT * FROM satellite_imagery_products
WHERE product_type = 'Fire'
    AND fire_detection_confidence >= 50
    AND scan_start_time >= CURRENT_TIMESTAMP() - INTERVAL '24 hours'
ORDER BY fire_power_mw DESC;
```

### Generate Composite Products

```sql
-- Use Query 46 to generate composite products
SELECT * FROM us_wide_composite_products
WHERE composite_time >= CURRENT_TIMESTAMP() - INTERVAL '1 hour'
    AND product_type = 'Precipitation'
ORDER BY composite_time DESC, grid_latitude, grid_longitude;
```

## Performance Considerations

### NEXRAD Processing
- **Decompression:** Can be CPU-intensive for large files
- **Gridding:** Requires spatial interpolation algorithms
- **Storage:** Large volume of data (terabytes per day)
- **Indexing:** Spatial indexes critical for performance

### Satellite Processing
- **Decompression:** NetCDF/HDF5 decompression can be memory-intensive
- **Reprojection:** Coordinate system transformations required
- **Band Processing:** Multiple bands increase processing time
- **Storage:** Very large volume of data (petabytes per year)

### Optimization Strategies
1. **Parallel Processing:** Process multiple sites/sources in parallel
2. **Incremental Updates:** Process only new/changed data
3. **Spatial Partitioning:** Partition data by geographic regions
4. **Compression:** Use database compression for storage
5. **Caching:** Cache frequently accessed products

## Compatibility

All NEXRAD and satellite queries are designed to work across:
- PostgreSQL (with PostGIS)
 (Delta Lake)


## Data Requirements

To use the NEXRAD and satellite transformation queries, ensure:

1. **NEXRAD Data:** Level II radar data downloaded and decompressed
2. **Satellite Data:** GOES satellite imagery downloaded and decompressed
3. **Radar Sites:** NEXRAD radar site metadata loaded
4. **Satellite Sources:** Satellite source metadata loaded
5. **Spatial Indexes:** Spatial indexes created on geometry columns

## Best Practices

1. **Decompress First:** Always decompress data before processing
2. **Quality Control:** Check decompression status before using data
3. **Spatial Indexing:** Ensure spatial indexes are created and maintained
4. **Temporal Filtering:** Filter by scan time for recent data
5. **Grid Resolution:** Use appropriate grid resolution for analysis
6. **Data Fusion:** Combine NEXRAD and satellite data for best coverage
7. **Performance Monitoring:** Track transformation performance metrics
8. **Coverage Analysis:** Regularly check data coverage for gaps

---

**Last Updated:** 2026-02-03
