-- NEXRAD Radar and Satellite Imagery Schema Extensions
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema extensions for NEXRAD Level II radar and satellite imagery data
-- Purpose: Support NEXRAD Level II radar data and decompressed satellite imagery transformations across entire United States

-- NEXRAD Radar Sites Table
-- Metadata for NEXRAD radar sites across the United States
CREATE TABLE IF NOT EXISTS nexrad_radar_sites (
    site_id VARCHAR(4) PRIMARY KEY,  -- 4-letter site identifier (e.g., 'KTLX')
    site_name VARCHAR(255) NOT NULL,
    site_latitude NUMERIC(10, 7) NOT NULL,
    site_longitude NUMERIC(10, 7) NOT NULL,
    site_geom GEOGRAPHY,  -- Point geometry
    elevation_meters NUMERIC(8, 2),
    state_code VARCHAR(2),
    county_name VARCHAR(100),
    cwa_code VARCHAR(10),  -- County Warning Area
    radar_type VARCHAR(50) DEFAULT 'WSR-88D',  -- Weather Surveillance Radar
    operational_status VARCHAR(50) DEFAULT 'Operational',  -- 'Operational', 'Maintenance', 'Offline'
    coverage_radius_km NUMERIC(8, 2) DEFAULT 230.0,  -- Standard NEXRAD coverage radius
    first_operational_date DATE,
    last_maintenance_date DATE,
    update_frequency_minutes INTEGER DEFAULT 5,  -- Typical NEXRAD update frequency
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- NEXRAD Level II Data Table
-- Stores decompressed NEXRAD Level II radar data
CREATE TABLE IF NOT EXISTS nexrad_level2_data (
    radar_data_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,  -- References nexrad_radar_sites
    scan_time TIMESTAMP_NTZ NOT NULL,
    volume_scan_number INTEGER,
    elevation_angle NUMERIC(5, 2),  -- Elevation angle in degrees
    azimuth_angle NUMERIC(6, 2),  -- Azimuth angle in degrees
    range_gate INTEGER,  -- Range gate number
    range_km NUMERIC(8, 2),  -- Distance from radar in kilometers
    -- Reflectivity data
    reflectivity_dbz NUMERIC(6, 2),  -- Reflectivity in dBZ
    reflectivity_geom GEOGRAPHY,  -- Point geometry for reflectivity location
    -- Velocity data
    radial_velocity_ms NUMERIC(6, 2),  -- Radial velocity in m/s
    velocity_geom GEOGRAPHY,  -- Point geometry for velocity location
    -- Spectrum width
    spectrum_width_ms NUMERIC(6, 2),  -- Spectrum width in m/s
    -- Data quality
    data_quality_flag INTEGER,  -- Quality flags
    -- Source file information
    source_file VARCHAR(1000),  -- Original NEXRAD file path
    aws_bucket VARCHAR(255),  -- AWS S3 bucket
    aws_key VARCHAR(1000),  -- AWS S3 key
    file_format VARCHAR(50) DEFAULT 'Level2',  -- 'Level2', 'Level3'
    compression_type VARCHAR(50),  -- 'bzip2', 'gzip', 'none'
    decompression_status VARCHAR(50) DEFAULT 'Success',  -- 'Success', 'Failed', 'Pending'
    -- Metadata
    data_type VARCHAR(50),  -- 'Reflectivity', 'Velocity', 'SpectrumWidth', 'DifferentialReflectivity'
    sweep_mode VARCHAR(50),  -- 'PPI' (Plan Position Indicator), 'RHI' (Range Height Indicator)
    pulse_repetition_frequency INTEGER,  -- PRF in Hz
    nyquist_velocity_ms NUMERIC(6, 2),  -- Nyquist velocity in m/s
    -- Spatial extent
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    -- Processing metadata
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    processing_duration_seconds INTEGER,
    records_processed INTEGER
);

-- NEXRAD Reflectivity Grid Table
-- Gridded reflectivity data for easier spatial analysis
CREATE TABLE IF NOT EXISTS nexrad_reflectivity_grid (
    grid_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,  -- References nexrad_radar_sites
    scan_time TIMESTAMP_NTZ NOT NULL,
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(6, 2) DEFAULT 1.0,  -- Grid resolution in km
    -- Reflectivity values
    max_reflectivity_dbz NUMERIC(6, 2),  -- Maximum reflectivity in grid cell
    mean_reflectivity_dbz NUMERIC(6, 2),  -- Mean reflectivity in grid cell
    min_reflectivity_dbz NUMERIC(6, 2),  -- Minimum reflectivity in grid cell
    reflectivity_count INTEGER,  -- Number of observations in grid cell
    -- Composite reflectivity (highest reflectivity at any elevation)
    composite_reflectivity_dbz NUMERIC(6, 2),
    -- Height of maximum reflectivity
    height_of_max_reflectivity_m NUMERIC(8, 2),
    -- Precipitation estimates
    precipitation_rate_mmh NUMERIC(8, 2),  -- Precipitation rate in mm/h
    accumulated_precipitation_mm NUMERIC(8, 2),  -- Accumulated precipitation in mm
    -- Storm attributes
    storm_cell_id VARCHAR(255),  -- Identifier for storm cell tracking
    storm_severity VARCHAR(50),  -- 'Weak', 'Moderate', 'Strong', 'Severe', 'Extreme'
    -- Processing metadata
    grid_generation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    grid_method VARCHAR(100)  -- 'NearestNeighbor', 'Bilinear', 'Cressman', etc.
);

-- NEXRAD Velocity Grid Table
-- Gridded velocity data for wind analysis
CREATE TABLE IF NOT EXISTS nexrad_velocity_grid (
    grid_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,  -- References nexrad_radar_sites
    scan_time TIMESTAMP_NTZ NOT NULL,
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(6, 2) DEFAULT 1.0,
    -- Velocity values
    radial_velocity_ms NUMERIC(6, 2),  -- Radial velocity in m/s
    velocity_azimuth NUMERIC(6, 2),  -- Azimuth angle in degrees
    -- Wind components (derived)
    u_wind_component_ms NUMERIC(6, 2),  -- East-west wind component
    v_wind_component_ms NUMERIC(6, 2),  -- North-south wind component
    wind_speed_ms NUMERIC(6, 2),  -- Wind speed in m/s
    wind_direction_deg NUMERIC(6, 2),  -- Wind direction in degrees
    -- Spectrum width
    spectrum_width_ms NUMERIC(6, 2),
    -- Velocity quality
    velocity_quality_flag INTEGER,
    -- Processing metadata
    grid_generation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- NEXRAD Storm Cell Tracking Table
-- Tracks storm cells across multiple scans
CREATE TABLE IF NOT EXISTS nexrad_storm_cells (
    storm_cell_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,  -- References nexrad_radar_sites
    first_detection_time TIMESTAMP_NTZ NOT NULL,
    last_detection_time TIMESTAMP_NTZ,
    storm_center_latitude NUMERIC(10, 7),
    storm_center_longitude NUMERIC(10, 7),
    storm_center_geom GEOGRAPHY,  -- Point geometry
    storm_polygon_geom GEOGRAPHY,  -- Polygon geometry for storm extent
    -- Storm characteristics
    max_reflectivity_dbz NUMERIC(6, 2),
    max_velocity_ms NUMERIC(6, 2),
    storm_area_km2 NUMERIC(10, 2),
    storm_diameter_km NUMERIC(8, 2),
    storm_perimeter_km NUMERIC(8, 2),
    -- Movement
    storm_speed_ms NUMERIC(6, 2),  -- Storm movement speed
    storm_direction_deg NUMERIC(6, 2),  -- Storm movement direction
    -- Severity classification
    storm_severity VARCHAR(50),  -- 'Weak', 'Moderate', 'Strong', 'Severe', 'Extreme'
    storm_type VARCHAR(50),  -- 'Thunderstorm', 'Squall Line', 'Supercell', 'Mesocyclone', etc.
    -- Tracking metadata
    track_duration_minutes INTEGER,
    scan_count INTEGER,  -- Number of scans where storm was detected
    tracking_status VARCHAR(50) DEFAULT 'Active',  -- 'Active', 'Dissipated', 'Merged'
    -- Processing metadata
    tracking_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Satellite Imagery Sources Table
-- Metadata for satellite imagery sources (GOES, etc.)
CREATE TABLE IF NOT EXISTS satellite_imagery_sources (
    source_id VARCHAR(255) PRIMARY KEY,
    satellite_name VARCHAR(100) NOT NULL,  -- 'GOES-16', 'GOES-17', 'GOES-18', etc.
    satellite_type VARCHAR(50) DEFAULT 'GOES',  -- 'GOES', 'POES', 'MODIS', etc.
    sensor_name VARCHAR(100),  -- 'ABI' (Advanced Baseline Imager), etc.
    orbital_position VARCHAR(50),  -- 'GOES-East', 'GOES-West', etc.
    -- Spatial coverage
    coverage_area VARCHAR(100) DEFAULT 'CONUS',  -- 'CONUS', 'Full Disk', 'Mesoscale', etc.
    spatial_resolution_km NUMERIC(8, 2),  -- Spatial resolution in kilometers
    scan_frequency_minutes INTEGER,  -- Scan frequency in minutes
    temporal_resolution_minutes INTEGER,
    -- Operational status
    operational_status VARCHAR(50) DEFAULT 'Operational',
    first_operational_date DATE,
    last_update_date DATE,
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Satellite Imagery Products Table
-- Decompressed satellite imagery products
CREATE TABLE IF NOT EXISTS satellite_imagery_products (
    product_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,  -- References satellite_imagery_sources
    product_name VARCHAR(255) NOT NULL,  -- 'ABI L2 Cloud Top Height', 'ABI L2 Cloud Top Temperature', etc.
    product_type VARCHAR(100),  -- 'Cloud', 'Fire', 'Precipitation', 'Temperature', 'Moisture', etc.
    band_number INTEGER,  -- GOES ABI band number (1-16)
    band_name VARCHAR(100),  -- 'Visible', 'Near-Infrared', 'Infrared', etc.
    wavelength_um NUMERIC(8, 4),  -- Wavelength in micrometers
    scan_start_time TIMESTAMP_NTZ NOT NULL,
    scan_end_time TIMESTAMP_NTZ,
    scan_duration_seconds INTEGER,
    -- Spatial information
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(8, 2),  -- Grid resolution in kilometers
    -- Pixel values
    pixel_value NUMERIC(10, 4),  -- Raw pixel value
    calibrated_value NUMERIC(10, 4),  -- Calibrated physical value
    brightness_temperature_k NUMERIC(8, 2),  -- Brightness temperature in Kelvin (for IR bands)
    reflectance_percent NUMERIC(6, 2),  -- Reflectance percentage (for visible bands)
    -- Derived products
    cloud_top_height_m NUMERIC(8, 2),  -- Cloud top height in meters
    cloud_top_temperature_k NUMERIC(8, 2),  -- Cloud top temperature in Kelvin
    cloud_phase VARCHAR(50),  -- 'Liquid', 'Ice', 'Mixed', 'Unknown'
    cloud_optical_depth NUMERIC(8, 4),  -- Cloud optical depth
    -- Fire detection
    fire_detection_confidence NUMERIC(5, 2),  -- Fire detection confidence (0-100)
    fire_temperature_k NUMERIC(8, 2),  -- Fire temperature in Kelvin
    fire_power_mw NUMERIC(12, 2),  -- Fire radiative power in megawatts
    -- Precipitation
    precipitation_rate_mmh NUMERIC(8, 2),  -- Precipitation rate in mm/h
    -- Source file information
    source_file VARCHAR(1000),  -- Original satellite file path
    aws_bucket VARCHAR(255),  -- AWS S3 bucket
    aws_key VARCHAR(1000),  -- AWS S3 key
    file_format VARCHAR(50) DEFAULT 'NetCDF',  -- 'NetCDF', 'HDF5', 'GeoTIFF', etc.
    compression_type VARCHAR(50),  -- Compression type
    decompression_status VARCHAR(50) DEFAULT 'Success',
    -- Spatial extent
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    -- Processing metadata
    ingestion_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    processing_duration_seconds INTEGER,
    records_processed INTEGER
);

-- Satellite Imagery Grid Aggregations Table
-- Aggregated satellite imagery data for spatial analysis
CREATE TABLE IF NOT EXISTS satellite_imagery_grid (
    grid_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,  -- References satellite_imagery_sources
    product_type VARCHAR(100) NOT NULL,
    scan_time TIMESTAMP_NTZ NOT NULL,
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(8, 2),  -- Grid resolution
    -- Aggregated values
    min_value NUMERIC(10, 4),
    max_value NUMERIC(10, 4),
    mean_value NUMERIC(10, 4),
    median_value NUMERIC(10, 4),
    stddev_value NUMERIC(10, 4),
    pixel_count INTEGER,
    -- Cloud properties
    cloud_fraction NUMERIC(5, 2),  -- Cloud fraction (0-100%)
    cloud_top_height_m NUMERIC(8, 2),
    cloud_top_temperature_k NUMERIC(8, 2),
    -- Fire properties
    fire_count INTEGER,
    total_fire_power_mw NUMERIC(12, 2),
    -- Precipitation properties
    precipitation_rate_mmh NUMERIC(8, 2),
    -- Processing metadata
    aggregation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    aggregation_method VARCHAR(100)  -- 'Mean', 'Max', 'Min', 'Median', etc.
);

-- NEXRAD Transformation Log Table
-- Tracks NEXRAD data transformation operations
CREATE TABLE IF NOT EXISTS nexrad_transformation_log (
    transformation_id VARCHAR(255) PRIMARY KEY,
    site_id VARCHAR(4) NOT NULL,
    source_file VARCHAR(1000) NOT NULL,
    transformation_type VARCHAR(100) NOT NULL,  -- 'Decompression', 'Gridding', 'StormTracking', 'Composite'
    transformation_start_time TIMESTAMP_NTZ NOT NULL,
    transformation_end_time TIMESTAMP_NTZ,
    transformation_duration_seconds INTEGER,
    -- Input parameters
    input_format VARCHAR(50),
    input_size_bytes BIGINT,
    input_records INTEGER,
    -- Output parameters
    output_format VARCHAR(50),
    output_size_bytes BIGINT,
    output_records INTEGER,
    -- Transformation status
    transformation_status VARCHAR(50) DEFAULT 'Success',  -- 'Success', 'Failed', 'Partial'
    error_message VARCHAR(2000),
    -- Processing details
    processing_method VARCHAR(100),  -- 'PyART', 'wradlib', 'Custom', etc.
    processing_parameters VARCHAR(2000),  -- JSON parameters
    -- Spatial extent
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    -- Metadata
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Satellite Imagery Transformation Log Table
-- Tracks satellite imagery transformation operations
CREATE TABLE IF NOT EXISTS satellite_transformation_log (
    transformation_id VARCHAR(255) PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,
    source_file VARCHAR(1000) NOT NULL,
    transformation_type VARCHAR(100) NOT NULL,  -- 'Decompression', 'Reprojection', 'Gridding', 'ProductGeneration'
    transformation_start_time TIMESTAMP_NTZ NOT NULL,
    transformation_end_time TIMESTAMP_NTZ,
    transformation_duration_seconds INTEGER,
    -- Input parameters
    input_format VARCHAR(50),
    input_size_bytes BIGINT,
    input_bands INTEGER,
    input_dimensions VARCHAR(100),  -- 'width x height'
    -- Output parameters
    output_format VARCHAR(50),
    output_size_bytes BIGINT,
    output_records INTEGER,
    -- Transformation status
    transformation_status VARCHAR(50) DEFAULT 'Success',
    error_message VARCHAR(2000),
    -- Processing details
    processing_method VARCHAR(100),  -- 'xarray', 'rasterio', 'GDAL', 'Custom', etc.
    processing_parameters VARCHAR(2000),  -- JSON parameters
    crs_transformation VARCHAR(100),  -- CRS transformation applied
    -- Spatial extent
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    -- Metadata
    created_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- US-Wide Composite Products Table
-- Composite products combining NEXRAD and satellite data across entire US
CREATE TABLE IF NOT EXISTS us_wide_composite_products (
    composite_id VARCHAR(255) PRIMARY KEY,
    product_type VARCHAR(100) NOT NULL,  -- 'Precipitation', 'Cloud', 'Storm', 'Fire', 'Temperature'
    composite_time TIMESTAMP_NTZ NOT NULL,
    grid_latitude NUMERIC(10, 7) NOT NULL,
    grid_longitude NUMERIC(10, 7) NOT NULL,
    grid_geom GEOGRAPHY,  -- Point geometry
    grid_resolution_km NUMERIC(8, 2) DEFAULT 1.0,
    -- NEXRAD contributions
    nexrad_reflectivity_dbz NUMERIC(6, 2),
    nexrad_velocity_ms NUMERIC(6, 2),
    nexrad_precipitation_rate_mmh NUMERIC(8, 2),
    nexrad_contribution_weight NUMERIC(5, 3),  -- Weight of NEXRAD data in composite
    -- Satellite contributions
    satellite_brightness_temperature_k NUMERIC(8, 2),
    satellite_reflectance_percent NUMERIC(6, 2),
    satellite_cloud_top_height_m NUMERIC(8, 2),
    satellite_precipitation_rate_mmh NUMERIC(8, 2),
    satellite_contribution_weight NUMERIC(5, 3),  -- Weight of satellite data in composite
    -- Composite values
    composite_precipitation_rate_mmh NUMERIC(8, 2),
    composite_cloud_fraction NUMERIC(5, 2),
    composite_storm_severity VARCHAR(50),
    -- Data quality
    data_quality_score NUMERIC(5, 2),  -- Overall data quality (0-100)
    coverage_percentage NUMERIC(5, 2),  -- Percentage of expected data coverage
    -- Source information
    nexrad_sites_count INTEGER,  -- Number of NEXRAD sites contributing
    satellite_sources_count INTEGER,  -- Number of satellite sources contributing
    -- Processing metadata
    composite_generation_timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    composite_method VARCHAR(100)  -- 'WeightedAverage', 'Maximum', 'Minimum', 'Median', etc.
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_nexrad_sites_state_cwa
    ON nexrad_radar_sites(state_code, cwa_code);
CREATE INDEX IF NOT EXISTS idx_nexrad_sites_geom
    ON nexrad_radar_sites USING GIST(site_geom);
CREATE INDEX IF NOT EXISTS idx_nexrad_level2_site_time
    ON nexrad_level2_data(site_id, scan_time);
CREATE INDEX IF NOT EXISTS idx_nexrad_level2_geom
    ON nexrad_level2_data USING GIST(reflectivity_geom);
CREATE INDEX IF NOT EXISTS idx_nexrad_reflectivity_grid_site_time
    ON nexrad_reflectivity_grid(site_id, scan_time);
CREATE INDEX IF NOT EXISTS idx_nexrad_reflectivity_grid_geom
    ON nexrad_reflectivity_grid USING GIST(grid_geom);
CREATE INDEX IF NOT EXISTS idx_nexrad_velocity_grid_site_time
    ON nexrad_velocity_grid(site_id, scan_time);
CREATE INDEX IF NOT EXISTS idx_nexrad_velocity_grid_geom
    ON nexrad_velocity_grid USING GIST(grid_geom);
CREATE INDEX IF NOT EXISTS idx_nexrad_storm_cells_site_time
    ON nexrad_storm_cells(site_id, first_detection_time);
CREATE INDEX IF NOT EXISTS idx_nexrad_storm_cells_geom
    ON nexrad_storm_cells USING GIST(storm_center_geom);
CREATE INDEX IF NOT EXISTS idx_satellite_products_source_time
    ON satellite_imagery_products(source_id, scan_start_time);
CREATE INDEX IF NOT EXISTS idx_satellite_products_geom
    ON satellite_imagery_products USING GIST(grid_geom);
CREATE INDEX IF NOT EXISTS idx_satellite_imagery_grid_source_time
    ON satellite_imagery_grid(source_id, scan_time);
CREATE INDEX IF NOT EXISTS idx_satellite_imagery_grid_geom
    ON satellite_imagery_grid USING GIST(grid_geom);
CREATE INDEX IF NOT EXISTS idx_us_wide_composite_time
    ON us_wide_composite_products(composite_time, product_type);
CREATE INDEX IF NOT EXISTS idx_us_wide_composite_geom
    ON us_wide_composite_products USING GIST(grid_geom);
