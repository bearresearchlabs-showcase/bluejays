--
-- PostgreSQL database dump
--

\restrict Ln089kzaevMx8zBiEPKfuiazUPOL97ooNfndlaAtJbMfXCHQa58A1N7q8EG8GRu

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP INDEX IF EXISTS public.idx_weather_observations_station_time;
DROP INDEX IF EXISTS public.idx_weather_alerts_event_time;
DROP INDEX IF EXISTS public.idx_us_wide_composite_time;
DROP INDEX IF EXISTS public.idx_spatial_join_forecast_boundary;
DROP INDEX IF EXISTS public.idx_shapefile_boundaries_type;
DROP INDEX IF EXISTS public.idx_satellite_products_source_time;
DROP INDEX IF EXISTS public.idx_satellite_imagery_grid_source_time;
DROP INDEX IF EXISTS public.idx_rate_table_comparison_policy_period;
DROP INDEX IF EXISTS public.idx_nexrad_velocity_grid_site_time;
DROP INDEX IF EXISTS public.idx_nexrad_storm_cells_site_time;
DROP INDEX IF EXISTS public.idx_nexrad_sites_state_cwa;
DROP INDEX IF EXISTS public.idx_nexrad_reflectivity_grid_site_time;
DROP INDEX IF EXISTS public.idx_nexrad_level2_site_time;
DROP INDEX IF EXISTS public.idx_model_forecast_comparison_time;
DROP INDEX IF EXISTS public.idx_insurance_risk_factors_policy_period;
DROP INDEX IF EXISTS public.idx_insurance_risk_factors_day_date;
DROP INDEX IF EXISTS public.idx_insurance_rate_tables_policy_period;
DROP INDEX IF EXISTS public.idx_insurance_rate_tables_day_date;
DROP INDEX IF EXISTS public.idx_insurance_policy_areas_type_active;
DROP INDEX IF EXISTS public.idx_insurance_policy_areas_boundary;
DROP INDEX IF EXISTS public.idx_insurance_claims_history_type_date;
DROP INDEX IF EXISTS public.idx_insurance_claims_history_area_date;
DROP INDEX IF EXISTS public.idx_grib2_forecasts_parameter_time;
DROP INDEX IF EXISTS public.idx_forecast_rate_mapping_rate_table;
DROP INDEX IF EXISTS public.idx_forecast_rate_mapping_forecast;
DROP INDEX IF EXISTS public.idx_forecast_aggregations_time;
DROP INDEX IF EXISTS public.idx_data_source_statistics_date;
ALTER TABLE IF EXISTS ONLY public.weather_stations DROP CONSTRAINT IF EXISTS weather_stations_pkey;
ALTER TABLE IF EXISTS ONLY public.weather_observations DROP CONSTRAINT IF EXISTS weather_observations_pkey;
ALTER TABLE IF EXISTS ONLY public.weather_forecast_aggregations DROP CONSTRAINT IF EXISTS weather_forecast_aggregations_pkey;
ALTER TABLE IF EXISTS ONLY public.weather_alerts DROP CONSTRAINT IF EXISTS weather_alerts_pkey;
ALTER TABLE IF EXISTS ONLY public.us_wide_composite_products DROP CONSTRAINT IF EXISTS us_wide_composite_products_pkey;
ALTER TABLE IF EXISTS ONLY public.spatial_join_results DROP CONSTRAINT IF EXISTS spatial_join_results_pkey;
ALTER TABLE IF EXISTS ONLY public.load_status DROP CONSTRAINT IF EXISTS load_status_pkey;
ALTER TABLE IF EXISTS ONLY public.shapefile_integration_log DROP CONSTRAINT IF EXISTS shapefile_integration_log_pkey;
ALTER TABLE IF EXISTS ONLY public.shapefile_boundaries DROP CONSTRAINT IF EXISTS shapefile_boundaries_pkey;
ALTER TABLE IF EXISTS ONLY public.satellite_transformation_log DROP CONSTRAINT IF EXISTS satellite_transformation_log_pkey;
ALTER TABLE IF EXISTS ONLY public.satellite_imagery_sources DROP CONSTRAINT IF EXISTS satellite_imagery_sources_pkey;
ALTER TABLE IF EXISTS ONLY public.satellite_imagery_products DROP CONSTRAINT IF EXISTS satellite_imagery_products_pkey;
ALTER TABLE IF EXISTS ONLY public.satellite_imagery_grid DROP CONSTRAINT IF EXISTS satellite_imagery_grid_pkey;
ALTER TABLE IF EXISTS ONLY public.rate_table_comparison DROP CONSTRAINT IF EXISTS rate_table_comparison_pkey;
ALTER TABLE IF EXISTS ONLY public.nws_api_observation_log DROP CONSTRAINT IF EXISTS nws_api_observation_log_pkey;
ALTER TABLE IF EXISTS ONLY public.nexrad_velocity_grid DROP CONSTRAINT IF EXISTS nexrad_velocity_grid_pkey;
ALTER TABLE IF EXISTS ONLY public.nexrad_transformation_log DROP CONSTRAINT IF EXISTS nexrad_transformation_log_pkey;
ALTER TABLE IF EXISTS ONLY public.nexrad_storm_cells DROP CONSTRAINT IF EXISTS nexrad_storm_cells_pkey;
ALTER TABLE IF EXISTS ONLY public.nexrad_reflectivity_grid DROP CONSTRAINT IF EXISTS nexrad_reflectivity_grid_pkey;
ALTER TABLE IF EXISTS ONLY public.nexrad_radar_sites DROP CONSTRAINT IF EXISTS nexrad_radar_sites_pkey;
ALTER TABLE IF EXISTS ONLY public.nexrad_level2_data DROP CONSTRAINT IF EXISTS nexrad_level2_data_pkey;
ALTER TABLE IF EXISTS ONLY public.model_forecast_comparison DROP CONSTRAINT IF EXISTS model_forecast_comparison_pkey;
ALTER TABLE IF EXISTS ONLY public.insurance_risk_factors DROP CONSTRAINT IF EXISTS insurance_risk_factors_pkey;
ALTER TABLE IF EXISTS ONLY public.insurance_rate_tables DROP CONSTRAINT IF EXISTS insurance_rate_tables_pkey;
ALTER TABLE IF EXISTS ONLY public.insurance_policy_areas DROP CONSTRAINT IF EXISTS insurance_policy_areas_pkey;
ALTER TABLE IF EXISTS ONLY public.insurance_claims_history DROP CONSTRAINT IF EXISTS insurance_claims_history_pkey;
ALTER TABLE IF EXISTS ONLY public.grib2_transformation_log DROP CONSTRAINT IF EXISTS grib2_transformation_log_pkey;
ALTER TABLE IF EXISTS ONLY public.grib2_forecasts DROP CONSTRAINT IF EXISTS grib2_forecasts_pkey;
ALTER TABLE IF EXISTS ONLY public.geoplatform_dataset_log DROP CONSTRAINT IF EXISTS geoplatform_dataset_log_pkey;
ALTER TABLE IF EXISTS ONLY public.forecast_rate_mapping DROP CONSTRAINT IF EXISTS forecast_rate_mapping_pkey;
ALTER TABLE IF EXISTS ONLY public.data_source_statistics DROP CONSTRAINT IF EXISTS data_source_statistics_pkey;
ALTER TABLE IF EXISTS ONLY public.data_quality_metrics DROP CONSTRAINT IF EXISTS data_quality_metrics_pkey;
ALTER TABLE IF EXISTS ONLY public.crs_transformation_parameters DROP CONSTRAINT IF EXISTS crs_transformation_parameters_pkey;
DROP TABLE IF EXISTS public.weather_stations;
DROP TABLE IF EXISTS public.weather_observations;
DROP TABLE IF EXISTS public.weather_forecast_aggregations;
DROP TABLE IF EXISTS public.weather_alerts;
DROP TABLE IF EXISTS public.us_wide_composite_products;
DROP TABLE IF EXISTS public.spatial_join_results;
DROP TABLE IF EXISTS public.load_status;
DROP TABLE IF EXISTS public.shapefile_integration_log;
DROP TABLE IF EXISTS public.shapefile_boundaries;
DROP TABLE IF EXISTS public.satellite_transformation_log;
DROP TABLE IF EXISTS public.satellite_imagery_sources;
DROP TABLE IF EXISTS public.satellite_imagery_products;
DROP TABLE IF EXISTS public.satellite_imagery_grid;
DROP TABLE IF EXISTS public.rate_table_comparison;
DROP TABLE IF EXISTS public.nws_api_observation_log;
DROP TABLE IF EXISTS public.nexrad_velocity_grid;
DROP TABLE IF EXISTS public.nexrad_transformation_log;
DROP TABLE IF EXISTS public.nexrad_storm_cells;
DROP TABLE IF EXISTS public.nexrad_reflectivity_grid;
DROP TABLE IF EXISTS public.nexrad_radar_sites;
DROP TABLE IF EXISTS public.nexrad_level2_data;
DROP TABLE IF EXISTS public.model_forecast_comparison;
DROP TABLE IF EXISTS public.insurance_risk_factors;
DROP TABLE IF EXISTS public.insurance_rate_tables;
DROP TABLE IF EXISTS public.insurance_policy_areas;
DROP TABLE IF EXISTS public.insurance_claims_history;
DROP TABLE IF EXISTS public.grib2_transformation_log;
DROP TABLE IF EXISTS public.grib2_forecasts;
DROP TABLE IF EXISTS public.geoplatform_dataset_log;
DROP TABLE IF EXISTS public.forecast_rate_mapping;
DROP TABLE IF EXISTS public.data_source_statistics;
DROP TABLE IF EXISTS public.data_quality_metrics;
DROP TABLE IF EXISTS public.crs_transformation_parameters;
-- *not* dropping schemasince initdb creates it
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schemasince initdb creates it


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: crs_transformation_parameters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.crs_transformation_parameters (
    transformation_id character varying(255) NOT NULL,
    source_crs character varying(50) NOT NULL,
    target_crs character varying(50) NOT NULL,
    source_crs_name character varying(255),
    target_crs_name character varying(255),
    transformation_method character varying(50),
    central_meridian numeric(10,6),
    false_easting numeric(12,2),
    false_northing numeric(12,2),
    scale_factor numeric(10,8),
    latitude_of_origin numeric(10,6),
    units character varying(50),
    accuracy_meters numeric(10,2),
    usage_count integer DEFAULT 0
);


--
-- Name: data_quality_metrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.data_quality_metrics (
    metric_id character varying(255) NOT NULL,
    metric_date date NOT NULL,
    data_source character varying(50) NOT NULL,
    files_processed integer DEFAULT 0,
    files_successful integer DEFAULT 0,
    files_failed integer DEFAULT 0,
    success_rate numeric(5,2),
    total_records integer DEFAULT 0,
    records_with_errors integer DEFAULT 0,
    error_rate numeric(5,2),
    spatial_coverage_km2 numeric(15,2),
    temporal_coverage_hours integer,
    data_freshness_minutes integer,
    calculation_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: data_source_statistics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.data_source_statistics (
    stat_id character varying(255) NOT NULL,
    source_type character varying(100) NOT NULL,
    source_name character varying(500),
    stat_date date NOT NULL,
    files_ingested integer DEFAULT 0,
    records_processed integer DEFAULT 0,
    data_volume_mb numeric(15,2),
    ingestion_duration_seconds integer,
    success_rate numeric(5,2),
    avg_latency_seconds numeric(10,2),
    error_count integer DEFAULT 0,
    calculation_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: forecast_rate_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.forecast_rate_mapping (
    mapping_id character varying(255) NOT NULL,
    forecast_id character varying(255) NOT NULL,
    rate_table_id character varying(255),
    risk_factor_id character varying(255),
    policy_area_id character varying(255) NOT NULL,
    forecast_date date NOT NULL,
    forecast_day integer NOT NULL,
    forecast_time timestamp without time zone NOT NULL,
    parameter_name character varying(100) NOT NULL,
    parameter_value numeric(10,2),
    risk_contribution numeric(10,4),
    rate_impact numeric(10,4),
    mapping_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: geoplatform_dataset_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.geoplatform_dataset_log (
    dataset_id character varying(255) NOT NULL,
    title character varying(500),
    description character varying(2000),
    url character varying(1000),
    search_term character varying(100),
    ingestion_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(50) DEFAULT 'Discovered'::character varying,
    dataset_type character varying(100),
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6)
);


--
-- Name: grib2_forecasts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grib2_forecasts (
    forecast_id character varying(255) NOT NULL,
    parameter_name character varying(100) NOT NULL,
    forecast_time timestamp without time zone NOT NULL,
    grid_cell_latitude numeric(10,7) NOT NULL,
    grid_cell_longitude numeric(10,7) NOT NULL,
    grid_cell_geom text,
    parameter_value numeric(10,2),
    source_file character varying(500),
    source_crs character varying(50),
    target_crs character varying(50),
    grid_resolution_x numeric(10,6),
    grid_resolution_y numeric(10,6),
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6),
    load_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    transformation_status character varying(50),
    data_source character varying(50) DEFAULT 'NDFD'::character varying,
    model_name character varying(100),
    aws_bucket character varying(255),
    aws_file_path character varying(1000),
    ensemble_member integer
);


--
-- Name: grib2_transformation_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grib2_transformation_log (
    log_id character varying(255) NOT NULL,
    file_name character varying(500) NOT NULL,
    source_path character varying(1000),
    parameter_name character varying(100) NOT NULL,
    forecast_time timestamp without time zone,
    source_crs character varying(50),
    target_crs character varying(50),
    gdal_command character varying(2000),
    output_file character varying(1000),
    grid_resolution_x numeric(10,6),
    grid_resolution_y numeric(10,6),
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6),
    transformation_status character varying(50),
    target_table character varying(255),
    load_timestamp timestamp without time zone,
    processing_duration_seconds integer,
    records_processed integer,
    error_message character varying(2000)
);


--
-- Name: insurance_claims_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.insurance_claims_history (
    claim_id character varying(255) NOT NULL,
    policy_area_id character varying(255),
    claim_date date NOT NULL,
    loss_date date NOT NULL,
    policy_type character varying(50),
    coverage_type character varying(100),
    claim_type character varying(100),
    loss_amount numeric(12,2),
    claim_status character varying(50),
    weather_event_type character varying(100),
    weather_event_date date,
    temperature_at_loss numeric(6,2),
    precipitation_at_loss numeric(8,2),
    wind_speed_at_loss numeric(6,2),
    forecast_available boolean DEFAULT false,
    forecast_day integer,
    forecast_error numeric(10,2),
    created_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: insurance_policy_areas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.insurance_policy_areas (
    policy_area_id character varying(255) NOT NULL,
    boundary_id character varying(255) NOT NULL,
    policy_type character varying(50) NOT NULL,
    coverage_type character varying(100),
    policy_area_name character varying(255),
    state_code character varying(2),
    county_code character varying(5),
    cwa_code character varying(10),
    risk_zone character varying(50),
    base_rate_factor numeric(5,3) DEFAULT 1.000,
    effective_date date NOT NULL,
    expiration_date date,
    is_active boolean DEFAULT true,
    created_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: insurance_rate_tables; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.insurance_rate_tables (
    rate_table_id character varying(255) NOT NULL,
    policy_area_id character varying(255) NOT NULL,
    policy_type character varying(50) NOT NULL,
    coverage_type character varying(100),
    forecast_period_start date NOT NULL,
    forecast_period_end date NOT NULL,
    forecast_day integer NOT NULL,
    forecast_date date NOT NULL,
    base_rate numeric(10,2),
    base_rate_currency character varying(3) DEFAULT 'USD'::character varying,
    risk_adjusted_rate numeric(10,2),
    risk_multiplier numeric(5,3),
    base_component numeric(10,2),
    precipitation_risk_component numeric(10,2),
    temperature_risk_component numeric(10,2),
    wind_risk_component numeric(10,2),
    freeze_risk_component numeric(10,2),
    flood_risk_component numeric(10,2),
    extreme_event_component numeric(10,2),
    rate_tier character varying(50),
    rate_category character varying(50),
    calculation_method character varying(100),
    confidence_level numeric(5,2),
    effective_date date NOT NULL,
    expiration_date date,
    created_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: insurance_risk_factors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.insurance_risk_factors (
    risk_factor_id character varying(255) NOT NULL,
    policy_area_id character varying(255) NOT NULL,
    forecast_period_start date NOT NULL,
    forecast_period_end date NOT NULL,
    forecast_day integer NOT NULL,
    forecast_date date NOT NULL,
    parameter_name character varying(100) NOT NULL,
    extreme_event_probability numeric(5,4),
    cumulative_precipitation_risk numeric(10,2),
    wind_damage_risk numeric(10,2),
    freeze_risk numeric(10,2),
    flood_risk numeric(10,2),
    min_forecast_value numeric(10,2),
    max_forecast_value numeric(10,2),
    avg_forecast_value numeric(10,2),
    median_forecast_value numeric(10,2),
    stddev_forecast_value numeric(10,2),
    percentile_90_value numeric(10,2),
    percentile_95_value numeric(10,2),
    percentile_99_value numeric(10,2),
    overall_risk_score numeric(5,2),
    risk_category character varying(50),
    calculation_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    forecast_model character varying(100),
    data_quality_score numeric(5,2)
);


--
-- Name: model_forecast_comparison; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.model_forecast_comparison (
    comparison_id character varying(255) NOT NULL,
    forecast_time timestamp without time zone NOT NULL,
    parameter_name character varying(100) NOT NULL,
    grid_cell_latitude numeric(10,7) NOT NULL,
    grid_cell_longitude numeric(10,7) NOT NULL,
    gfs_value numeric(10,2),
    hrrr_value numeric(10,2),
    rap_value numeric(10,2),
    gefs_mean_value numeric(10,2),
    gefs_stddev_value numeric(10,2),
    observation_value numeric(10,2),
    observation_time timestamp without time zone,
    gfs_error numeric(10,2),
    hrrr_error numeric(10,2),
    rap_error numeric(10,2),
    best_model character varying(50),
    comparison_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: nexrad_level2_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nexrad_level2_data (
    radar_data_id character varying(255) NOT NULL,
    site_id character varying(4) NOT NULL,
    scan_time timestamp without time zone NOT NULL,
    volume_scan_number integer,
    elevation_angle numeric(5,2),
    azimuth_angle numeric(6,2),
    range_gate integer,
    range_km numeric(8,2),
    reflectivity_dbz numeric(6,2),
    reflectivity_geom text,
    radial_velocity_ms numeric(6,2),
    velocity_geom text,
    spectrum_width_ms numeric(6,2),
    data_quality_flag integer,
    source_file character varying(1000),
    aws_bucket character varying(255),
    aws_key character varying(1000),
    file_format character varying(50) DEFAULT 'Level2'::character varying,
    compression_type character varying(50),
    decompression_status character varying(50) DEFAULT 'Success'::character varying,
    data_type character varying(50),
    sweep_mode character varying(50),
    pulse_repetition_frequency integer,
    nyquist_velocity_ms numeric(6,2),
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6),
    ingestion_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    processing_duration_seconds integer,
    records_processed integer
);


--
-- Name: nexrad_radar_sites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nexrad_radar_sites (
    site_id character varying(4) NOT NULL,
    site_name character varying(255) NOT NULL,
    site_latitude numeric(10,7) NOT NULL,
    site_longitude numeric(10,7) NOT NULL,
    site_geom text,
    elevation_meters numeric(8,2),
    state_code character varying(2),
    county_name character varying(100),
    cwa_code character varying(10),
    radar_type character varying(50) DEFAULT 'WSR-88D'::character varying,
    operational_status character varying(50) DEFAULT 'Operational'::character varying,
    coverage_radius_km numeric(8,2) DEFAULT 230.0,
    first_operational_date date,
    last_maintenance_date date,
    update_frequency_minutes integer DEFAULT 5,
    created_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: nexrad_reflectivity_grid; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nexrad_reflectivity_grid (
    grid_id character varying(255) NOT NULL,
    site_id character varying(4) NOT NULL,
    scan_time timestamp without time zone NOT NULL,
    grid_latitude numeric(10,7) NOT NULL,
    grid_longitude numeric(10,7) NOT NULL,
    grid_geom text,
    grid_resolution_km numeric(6,2) DEFAULT 1.0,
    max_reflectivity_dbz numeric(6,2),
    mean_reflectivity_dbz numeric(6,2),
    min_reflectivity_dbz numeric(6,2),
    reflectivity_count integer,
    composite_reflectivity_dbz numeric(6,2),
    height_of_max_reflectivity_m numeric(8,2),
    precipitation_rate_mmh numeric(8,2),
    accumulated_precipitation_mm numeric(8,2),
    storm_cell_id character varying(255),
    storm_severity character varying(50),
    grid_generation_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    grid_method character varying(100)
);


--
-- Name: nexrad_storm_cells; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nexrad_storm_cells (
    storm_cell_id character varying(255) NOT NULL,
    site_id character varying(4) NOT NULL,
    first_detection_time timestamp without time zone NOT NULL,
    last_detection_time timestamp without time zone,
    storm_center_latitude numeric(10,7),
    storm_center_longitude numeric(10,7),
    storm_center_geom text,
    storm_polygon_geom text,
    max_reflectivity_dbz numeric(6,2),
    max_velocity_ms numeric(6,2),
    storm_area_km2 numeric(10,2),
    storm_diameter_km numeric(8,2),
    storm_perimeter_km numeric(8,2),
    storm_speed_ms numeric(6,2),
    storm_direction_deg numeric(6,2),
    storm_severity character varying(50),
    storm_type character varying(50),
    track_duration_minutes integer,
    scan_count integer,
    tracking_status character varying(50) DEFAULT 'Active'::character varying,
    tracking_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: nexrad_transformation_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nexrad_transformation_log (
    transformation_id character varying(255) NOT NULL,
    site_id character varying(4) NOT NULL,
    source_file character varying(1000) NOT NULL,
    transformation_type character varying(100) NOT NULL,
    transformation_start_time timestamp without time zone NOT NULL,
    transformation_end_time timestamp without time zone,
    transformation_duration_seconds integer,
    input_format character varying(50),
    input_size_bytes bigint,
    input_records integer,
    output_format character varying(50),
    output_size_bytes bigint,
    output_records integer,
    transformation_status character varying(50) DEFAULT 'Success'::character varying,
    error_message character varying(2000),
    processing_method character varying(100),
    processing_parameters character varying(2000),
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6),
    created_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: nexrad_velocity_grid; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nexrad_velocity_grid (
    grid_id character varying(255) NOT NULL,
    site_id character varying(4) NOT NULL,
    scan_time timestamp without time zone NOT NULL,
    grid_latitude numeric(10,7) NOT NULL,
    grid_longitude numeric(10,7) NOT NULL,
    grid_geom text,
    grid_resolution_km numeric(6,2) DEFAULT 1.0,
    radial_velocity_ms numeric(6,2),
    velocity_azimuth numeric(6,2),
    u_wind_component_ms numeric(6,2),
    v_wind_component_ms numeric(6,2),
    wind_speed_ms numeric(6,2),
    wind_direction_deg numeric(6,2),
    spectrum_width_ms numeric(6,2),
    velocity_quality_flag integer,
    grid_generation_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: nws_api_observation_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.nws_api_observation_log (
    log_id character varying(255) NOT NULL,
    station_id character varying(50) NOT NULL,
    observation_time timestamp without time zone NOT NULL,
    api_endpoint character varying(500),
    response_status integer,
    data_freshness_minutes integer,
    ingestion_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(50) DEFAULT 'Success'::character varying,
    error_message character varying(2000)
);


--
-- Name: rate_table_comparison; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rate_table_comparison (
    comparison_id character varying(255) NOT NULL,
    policy_area_id character varying(255) NOT NULL,
    policy_type character varying(50) NOT NULL,
    forecast_period_start date NOT NULL,
    forecast_period_end date NOT NULL,
    forecast_date date NOT NULL,
    rate_day_7 numeric(10,2),
    rate_day_8 numeric(10,2),
    rate_day_9 numeric(10,2),
    rate_day_10 numeric(10,2),
    rate_day_11 numeric(10,2),
    rate_day_12 numeric(10,2),
    rate_day_13 numeric(10,2),
    rate_day_14 numeric(10,2),
    min_rate numeric(10,2),
    max_rate numeric(10,2),
    avg_rate numeric(10,2),
    median_rate numeric(10,2),
    rate_volatility numeric(10,4),
    rate_trend character varying(50),
    recommended_rate numeric(10,2),
    recommended_forecast_day integer,
    confidence_score numeric(5,2),
    comparison_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: satellite_imagery_grid; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.satellite_imagery_grid (
    grid_id character varying(255) NOT NULL,
    source_id character varying(255) NOT NULL,
    product_type character varying(100) NOT NULL,
    scan_time timestamp without time zone NOT NULL,
    grid_latitude numeric(10,7) NOT NULL,
    grid_longitude numeric(10,7) NOT NULL,
    grid_geom text,
    grid_resolution_km numeric(8,2),
    min_value numeric(10,4),
    max_value numeric(10,4),
    mean_value numeric(10,4),
    median_value numeric(10,4),
    stddev_value numeric(10,4),
    pixel_count integer,
    cloud_fraction numeric(5,2),
    cloud_top_height_m numeric(8,2),
    cloud_top_temperature_k numeric(8,2),
    fire_count integer,
    total_fire_power_mw numeric(12,2),
    precipitation_rate_mmh numeric(8,2),
    aggregation_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    aggregation_method character varying(100)
);


--
-- Name: satellite_imagery_products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.satellite_imagery_products (
    product_id character varying(255) NOT NULL,
    source_id character varying(255) NOT NULL,
    product_name character varying(255) NOT NULL,
    product_type character varying(100),
    band_number integer,
    band_name character varying(100),
    wavelength_um numeric(8,4),
    scan_start_time timestamp without time zone NOT NULL,
    scan_end_time timestamp without time zone,
    scan_duration_seconds integer,
    grid_latitude numeric(10,7) NOT NULL,
    grid_longitude numeric(10,7) NOT NULL,
    grid_geom text,
    grid_resolution_km numeric(8,2),
    pixel_value numeric(10,4),
    calibrated_value numeric(10,4),
    brightness_temperature_k numeric(8,2),
    reflectance_percent numeric(6,2),
    cloud_top_height_m numeric(8,2),
    cloud_top_temperature_k numeric(8,2),
    cloud_phase character varying(50),
    cloud_optical_depth numeric(8,4),
    fire_detection_confidence numeric(5,2),
    fire_temperature_k numeric(8,2),
    fire_power_mw numeric(12,2),
    precipitation_rate_mmh numeric(8,2),
    source_file character varying(1000),
    aws_bucket character varying(255),
    aws_key character varying(1000),
    file_format character varying(50) DEFAULT 'NetCDF'::character varying,
    compression_type character varying(50),
    decompression_status character varying(50) DEFAULT 'Success'::character varying,
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6),
    ingestion_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    processing_duration_seconds integer,
    records_processed integer
);


--
-- Name: satellite_imagery_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.satellite_imagery_sources (
    source_id character varying(255) NOT NULL,
    satellite_name character varying(100) NOT NULL,
    satellite_type character varying(50) DEFAULT 'GOES'::character varying,
    sensor_name character varying(100),
    orbital_position character varying(50),
    coverage_area character varying(100) DEFAULT 'CONUS'::character varying,
    spatial_resolution_km numeric(8,2),
    scan_frequency_minutes integer,
    temporal_resolution_minutes integer,
    operational_status character varying(50) DEFAULT 'Operational'::character varying,
    first_operational_date date,
    last_update_date date,
    created_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: satellite_transformation_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.satellite_transformation_log (
    transformation_id character varying(255) NOT NULL,
    source_id character varying(255) NOT NULL,
    source_file character varying(1000) NOT NULL,
    transformation_type character varying(100) NOT NULL,
    transformation_start_time timestamp without time zone NOT NULL,
    transformation_end_time timestamp without time zone,
    transformation_duration_seconds integer,
    input_format character varying(50),
    input_size_bytes bigint,
    input_bands integer,
    input_dimensions character varying(100),
    output_format character varying(50),
    output_size_bytes bigint,
    output_records integer,
    transformation_status character varying(50) DEFAULT 'Success'::character varying,
    error_message character varying(2000),
    processing_method character varying(100),
    processing_parameters character varying(2000),
    crs_transformation character varying(100),
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6),
    created_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: shapefile_boundaries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shapefile_boundaries (
    boundary_id character varying(255) NOT NULL,
    feature_type character varying(50) NOT NULL,
    feature_name character varying(255),
    feature_identifier character varying(100),
    boundary_geom text,
    source_shapefile character varying(500),
    source_crs character varying(50),
    target_crs character varying(50),
    feature_count integer,
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6),
    load_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    transformation_status character varying(50),
    state_code character varying(2),
    office_code character varying(10)
);


--
-- Name: shapefile_integration_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shapefile_integration_log (
    log_id character varying(255) NOT NULL,
    shapefile_name character varying(500) NOT NULL,
    source_path character varying(1000),
    feature_type character varying(50) NOT NULL,
    feature_count integer,
    source_crs character varying(50),
    target_crs character varying(50),
    ogr2ogr_command character varying(2000),
    transformed_path character varying(1000),
    spatial_extent_west numeric(10,6),
    spatial_extent_south numeric(10,6),
    spatial_extent_east numeric(10,6),
    spatial_extent_north numeric(10,6),
    transformation_status character varying(50),
    target_table character varying(255),
    load_timestamp timestamp without time zone,
    processing_duration_seconds integer,
    error_message character varying(2000)
);


--
-- Name: load_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.load_status (
    load_id character varying(255) NOT NULL,
    source_file character varying(1000),
    target_table character varying(255) NOT NULL,
    load_start_time timestamp without time zone NOT NULL,
    load_end_time timestamp without time zone,
    load_duration_seconds integer,
    records_loaded integer DEFAULT 0,
    file_size_mb numeric(10,2),
    load_rate_mb_per_sec numeric(10,2),
    load_status character varying(50),
    error_message character varying(2000),
    warehouse character varying(255),
    data_source_type character varying(50)
);


--
-- Name: spatial_join_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spatial_join_results (
    join_id character varying(255) NOT NULL,
    grib_file character varying(500),
    shapefile_name character varying(500),
    join_type character varying(50),
    gdal_command character varying(2000),
    features_matched integer,
    features_total integer,
    match_percentage numeric(5,2),
    output_file character varying(1000),
    join_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    forecast_id character varying(255),
    boundary_id character varying(255)
);


--
-- Name: us_wide_composite_products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.us_wide_composite_products (
    composite_id character varying(255) NOT NULL,
    product_type character varying(100) NOT NULL,
    composite_time timestamp without time zone NOT NULL,
    grid_latitude numeric(10,7) NOT NULL,
    grid_longitude numeric(10,7) NOT NULL,
    grid_geom text,
    grid_resolution_km numeric(8,2) DEFAULT 1.0,
    nexrad_reflectivity_dbz numeric(6,2),
    nexrad_velocity_ms numeric(6,2),
    nexrad_precipitation_rate_mmh numeric(8,2),
    nexrad_contribution_weight numeric(5,3),
    satellite_brightness_temperature_k numeric(8,2),
    satellite_reflectance_percent numeric(6,2),
    satellite_cloud_top_height_m numeric(8,2),
    satellite_precipitation_rate_mmh numeric(8,2),
    satellite_contribution_weight numeric(5,3),
    composite_precipitation_rate_mmh numeric(8,2),
    composite_cloud_fraction numeric(5,2),
    composite_storm_severity character varying(50),
    data_quality_score numeric(5,2),
    coverage_percentage numeric(5,2),
    nexrad_sites_count integer,
    satellite_sources_count integer,
    composite_generation_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    composite_method character varying(100)
);


--
-- Name: weather_alerts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.weather_alerts (
    alert_id character varying(255) NOT NULL,
    event_type character varying(100) NOT NULL,
    severity character varying(50),
    urgency character varying(50),
    certainty character varying(50),
    headline character varying(500),
    description text,
    instruction text,
    effective_time timestamp without time zone,
    expires_time timestamp without time zone,
    onset_time timestamp without time zone,
    ends_time timestamp without time zone,
    area_description character varying(1000),
    geocode_type character varying(50),
    geocode_value character varying(100),
    state_code character varying(2),
    county_code character varying(5),
    cwa_code character varying(10),
    ingestion_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    alert_geometry text
);


--
-- Name: weather_forecast_aggregations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.weather_forecast_aggregations (
    aggregation_id character varying(255) NOT NULL,
    parameter_name character varying(100) NOT NULL,
    forecast_time timestamp without time zone NOT NULL,
    boundary_id character varying(255),
    feature_type character varying(50),
    feature_name character varying(255),
    min_value numeric(10,2),
    max_value numeric(10,2),
    avg_value numeric(10,2),
    median_value numeric(10,2),
    std_dev_value numeric(10,2),
    grid_cells_count integer,
    aggregation_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: weather_observations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.weather_observations (
    observation_id character varying(255) NOT NULL,
    station_id character varying(50) NOT NULL,
    station_name character varying(255),
    observation_time timestamp without time zone NOT NULL,
    station_latitude numeric(10,7) NOT NULL,
    station_longitude numeric(10,7) NOT NULL,
    station_geom text,
    temperature numeric(6,2),
    dewpoint numeric(6,2),
    humidity numeric(5,2),
    wind_speed numeric(6,2),
    wind_direction integer,
    pressure numeric(8,2),
    visibility numeric(6,2),
    sky_cover character varying(50),
    precipitation_amount numeric(8,2),
    data_freshness_minutes integer,
    load_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    data_source character varying(50) DEFAULT 'NWS_API'::character varying,
    api_endpoint character varying(500),
    api_response_status integer
);


--
-- Name: weather_stations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.weather_stations (
    station_id character varying(50) NOT NULL,
    station_name character varying(255),
    station_latitude numeric(10,7) NOT NULL,
    station_longitude numeric(10,7) NOT NULL,
    station_geom text,
    elevation_meters numeric(8,2),
    state_code character varying(2),
    county_name character varying(100),
    cwa_code character varying(10),
    station_type character varying(50),
    active_status boolean DEFAULT true,
    first_observation_date date,
    last_observation_date date,
    update_frequency_minutes integer
);


--
-- Data for Name: crs_transformation_parameters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.crs_transformation_parameters (transformation_idsource_crstarget_crssource_crs_nametarget_crs_nametransformation_methodcentral_meridianfalse_eastingfalse_northingscale_factorlatitude_of_originunitsaccuracy_metersusage_count) FROM stdin;
tran_001	EPSG:4326	EPSG:3857	WGS84 Geographic	Web Mercator	GDAL	\N	\N	\N	\N	\N	meters	0.50	150
tran_002	EPSG:2227	EPSG:4326	California State Plane Zone 5	WGS84 Geographic	PROJ	\N	\N	\N	\N	\N	degrees	1.20	85
tran_003	EPSG:4326	EPSG:4326	WGS84 Geographic	WGS84 Geographic	GDAL	\N	\N	\N	\N	\N	degrees	0.00	200
\.


--
-- Data for Name: data_quality_metrics; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.data_quality_metrics (metric_idmetric_datedata_sourcefiles_processedfiles_successfulfiles_failedsuccess_ratetotal_recordsrecords_with_errorserror_ratespatial_coverage_km2temporal_coverage_hoursdata_freshness_minutescalculation_timestamp) FROM stdin;
metric_001	2026-02-03	GRIB2	15	14	1	93.33	750000	2500	0.33	7850000.00	168	5	2026-02-04 05:59:09.754488
metric_002	2026-02-03	Shapefile	8	8	0	100.00	557	0	0.00	7850000.00	0	60	2026-02-04 05:59:09.754488
metric_003	2026-02-03	API	0	0	0	0.00	5000	25	0.50	0.00	24	5	2026-02-04 05:59:09.754488
\.


--
-- Data for Name: data_source_statistics; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.data_source_statistics (stat_idsource_typesource_namestat_datefiles_ingestedrecords_processeddata_volume_mbingestion_duration_secondssuccess_rateavg_latency_secondserror_countcalculation_timestamp) FROM stdin;
\.


--
-- Data for Name: forecast_rate_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.forecast_rate_mapping (mapping_idforecast_idrate_table_idrisk_factor_idpolicy_area_idforecast_dateforecast_dayforecast_timeparameter_nameparameter_valuerisk_contributionrate_impactmapping_timestamp) FROM stdin;
\.


--
-- Data for Name: geoplatform_dataset_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.geoplatform_dataset_log (dataset_idtitledescriptionurlsearch_termingestion_timestampstatusdataset_typespatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_north) FROM stdin;
\.


--
-- Data for Name: grib2_forecasts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grib2_forecasts (forecast_idparameter_nameforecast_timegrid_cell_latitudegrid_cell_longitudegrid_cell_geomparameter_valuesource_filesource_crstarget_crsgrid_resolution_xgrid_resolution_yspatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_northload_timestamptransformation_statusdata_sourcemodel_nameaws_bucketaws_file_pathensemble_member) FROM stdin;
grib_temp_001	Temperature	2026-02-03 12:00:00	40.7850000	-73.9690000	\N	45.50	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success	NDFD	\N	\N	\N	\N
grib_temp_002	Temperature	2026-02-03 12:00:00	33.9420000	-118.4080000	\N	72.30	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success	NDFD	\N	\N	\N	\N
grib_temp_003	Temperature	2026-02-03 12:00:00	41.9790000	-87.9070000	\N	38.20	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success	NDFD	\N	\N	\N	\N
grib_temp_004	Temperature	2026-02-03 12:00:00	25.7950000	-80.2900000	\N	78.90	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success	NDFD	\N	\N	\N	\N
grib_temp_005	Temperature	2026-02-03 12:00:00	47.4490000	-122.3090000	\N	52.10	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success	NDFD	\N	\N	\N	\N
grib_qpf_001	Precipitation	2026-02-03 12:00:00	40.7850000	-73.9690000	\N	0.15	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success	NDFD	\N	\N	\N	\N
grib_qpf_002	Precipitation	2026-02-03 12:00:00	33.9420000	-118.4080000	\N	0.00	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success	NDFD	\N	\N	\N	\N
grib_qpf_003	Precipitation	2026-02-03 12:00:00	41.9790000	-87.9070000	\N	0.08	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success	NDFD	\N	\N	\N	\N
grib_qpf_004	Precipitation	2026-02-03 12:00:00	25.7950000	-80.2900000	\N	0.25	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success	NDFD	\N	\N	\N	\N
grib_qpf_005	Precipitation	2026-02-03 12:00:00	47.4490000	-122.3090000	\N	0.12	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success	NDFD	\N	\N	\N	\N
grib_wspd_001	WindSpeed	2026-02-03 12:00:00	40.7850000	-73.9690000	\N	12.50	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success	NDFD	\N	\N	\N	\N
grib_wspd_002	WindSpeed	2026-02-03 12:00:00	33.9420000	-118.4080000	\N	8.30	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success	NDFD	\N	\N	\N	\N
grib_wspd_003	WindSpeed	2026-02-03 12:00:00	41.9790000	-87.9070000	\N	15.20	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success	NDFD	\N	\N	\N	\N
grib_wspd_004	WindSpeed	2026-02-03 12:00:00	25.7950000	-80.2900000	\N	10.70	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success	NDFD	\N	\N	\N	\N
grib_wspd_005	WindSpeed	2026-02-03 12:00:00	47.4490000	-122.3090000	\N	18.40	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success	NDFD	\N	\N	\N	\N
\.


--
-- Data for Name: grib2_transformation_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grib2_transformation_log (log_idfile_namesource_pathparameter_nameforecast_timesource_crstarget_crsgdal_commandoutput_filegrid_resolution_xgrid_resolution_yspatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_northtransformation_statustarget_tableload_timestampprocessing_duration_secondsrecords_processederror_message) FROM stdin;
log_grib_001	ds.temp.bin	/data/raw/grib2/ds.temp.bin	Temperature	2026-02-03 12:00:00	EPSG:4326	EPSG:3857	gdal_translate -of GTiff -a_srs EPSG:3857	/data/transformed/grib2/ds.temp_transformed.tif	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	Success	grib2_forecasts	2026-02-03 12:05:00	45	50000	\N
log_grib_002	ds.qpf.bin	/data/raw/grib2/ds.qpf.bin	Precipitation	2026-02-03 12:00:00	EPSG:4326	EPSG:3857	gdal_translate -of GTiff -a_srs EPSG:3857	/data/transformed/grib2/ds.qpf_transformed.tif	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	Success	grib2_forecasts	2026-02-03 12:05:00	42	50000	\N
log_grib_003	ds.wspd.bin	/data/raw/grib2/ds.wspd.bin	WindSpeed	2026-02-03 12:00:00	EPSG:4326	EPSG:3857	gdal_translate -of GTiff -a_srs EPSG:3857	/data/transformed/grib2/ds.wspd_transformed.tif	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	Success	grib2_forecasts	2026-02-03 12:05:00	38	50000	\N
\.


--
-- Data for Name: insurance_claims_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.insurance_claims_history (claim_idpolicy_area_idclaim_dateloss_datepolicy_typecoverage_typeclaim_typeloss_amountclaim_statusweather_event_typeweather_event_datetemperature_at_lossprecipitation_at_losswind_speed_at_lossforecast_availableforecast_dayforecast_errorcreated_timestamp) FROM stdin;
\.


--
-- Data for Name: insurance_policy_areas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.insurance_policy_areas (policy_area_idboundary_idpolicy_typecoverage_typepolicy_area_namestate_codecounty_codecwa_coderisk_zonebase_rate_factoreffective_dateexpiration_dateis_activecreated_timestampupdated_timestamp) FROM stdin;
\.


--
-- Data for Name: insurance_rate_tables; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.insurance_rate_tables (rate_table_idpolicy_area_idpolicy_typecoverage_typeforecast_period_startforecast_period_endforecast_dayforecast_datebase_ratebase_rate_currencyrisk_adjusted_raterisk_multiplierbase_componentprecipitation_risk_componenttemperature_risk_componentwind_risk_componentfreeze_risk_componentflood_risk_componentextreme_event_componentrate_tierrate_categorycalculation_methodconfidence_leveleffective_dateexpiration_datecreated_timestampupdated_timestamp) FROM stdin;
\.


--
-- Data for Name: insurance_risk_factors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.insurance_risk_factors (risk_factor_idpolicy_area_idforecast_period_startforecast_period_endforecast_dayforecast_dateparameter_nameextreme_event_probabilitycumulative_precipitation_riskwind_damage_riskfreeze_riskflood_riskmin_forecast_valuemax_forecast_valueavg_forecast_valuemedian_forecast_valuestddev_forecast_valuepercentile_90_valuepercentile_95_valuepercentile_99_valueoverall_risk_scorerisk_categorycalculation_timestampforecast_modeldata_quality_score) FROM stdin;
\.


--
-- Data for Name: model_forecast_comparison; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.model_forecast_comparison (comparison_idforecast_timeparameter_namegrid_cell_latitudegrid_cell_longitudegfs_valuehrrr_valuerap_valuegefs_mean_valuegefs_stddev_valueobservation_valueobservation_timegfs_errorhrrr_errorrap_errorbest_modelcomparison_timestamp) FROM stdin;
\.


--
-- Data for Name: nexrad_level2_data; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.nexrad_level2_data (radar_data_idsite_idscan_timevolume_scan_numberelevation_angleazimuth_anglerange_gaterange_kmreflectivity_dbzreflectivity_geomradial_velocity_msvelocity_geomspectrum_width_msdata_quality_flagsource_fileaws_bucketaws_keyfile_formatcompression_typedecompression_statusdata_typesweep_modepulse_repetition_frequencynyquist_velocity_msspatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_northingestion_timestampprocessing_duration_secondsrecords_processed) FROM stdin;
\.


--
-- Data for Name: nexrad_radar_sites; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.nexrad_radar_sites (site_idsite_namesite_latitudesite_longitudesite_geomelevation_metersstate_codecounty_namecwa_coderadar_typeoperational_statuscoverage_radius_kmfirst_operational_datelast_maintenance_dateupdate_frequency_minutescreated_timestampupdated_timestamp) FROM stdin;
\.


--
-- Data for Name: nexrad_reflectivity_grid; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.nexrad_reflectivity_grid (grid_idsite_idscan_timegrid_latitudegrid_longitudegrid_geomgrid_resolution_kmmax_reflectivity_dbzmean_reflectivity_dbzmin_reflectivity_dbzreflectivity_countcomposite_reflectivity_dbzheight_of_max_reflectivity_mprecipitation_rate_mmhaccumulated_precipitation_mmstorm_cell_idstorm_severitygrid_generation_timestampgrid_method) FROM stdin;
\.


--
-- Data for Name: nexrad_storm_cells; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.nexrad_storm_cells (storm_cell_idsite_idfirst_detection_timelast_detection_timestorm_center_latitudestorm_center_longitudestorm_center_geomstorm_polygon_geommax_reflectivity_dbzmax_velocity_msstorm_area_km2storm_diameter_kmstorm_perimeter_kmstorm_speed_msstorm_direction_degstorm_severitystorm_typetrack_duration_minutesscan_counttracking_statustracking_timestamp) FROM stdin;
\.


--
-- Data for Name: nexrad_transformation_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.nexrad_transformation_log (transformation_idsite_idsource_filetransformation_typetransformation_start_timetransformation_end_timetransformation_duration_secondsinput_formatinput_size_bytesinput_recordsoutput_formatoutput_size_bytesoutput_recordstransformation_statuserror_messageprocessing_methodprocessing_parametersspatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_northcreated_timestamp) FROM stdin;
\.


--
-- Data for Name: nexrad_velocity_grid; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.nexrad_velocity_grid (grid_idsite_idscan_timegrid_latitudegrid_longitudegrid_geomgrid_resolution_kmradial_velocity_msvelocity_azimuthu_wind_component_msv_wind_component_mswind_speed_mswind_direction_degspectrum_width_msvelocity_quality_flaggrid_generation_timestamp) FROM stdin;
\.


--
-- Data for Name: nws_api_observation_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.nws_api_observation_log (log_idstation_idobservation_timeapi_endpointresponse_statusdata_freshness_minutesingestion_timestampstatuserror_message) FROM stdin;
\.


--
-- Data for Name: rate_table_comparison; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.rate_table_comparison (comparison_idpolicy_area_idpolicy_typeforecast_period_startforecast_period_endforecast_daterate_day_7rate_day_8rate_day_9rate_day_10rate_day_11rate_day_12rate_day_13rate_day_14min_ratemax_rateavg_ratemedian_raterate_volatilityrate_trendrecommended_raterecommended_forecast_dayconfidence_scorecomparison_timestamp) FROM stdin;
\.


--
-- Data for Name: satellite_imagery_grid; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.satellite_imagery_grid (grid_idsource_idproduct_typescan_timegrid_latitudegrid_longitudegrid_geomgrid_resolution_kmmin_valuemax_valuemean_valuemedian_valuestddev_valuepixel_countcloud_fractioncloud_top_height_mcloud_top_temperature_kfire_counttotal_fire_power_mwprecipitation_rate_mmhaggregation_timestampaggregation_method) FROM stdin;
\.


--
-- Data for Name: satellite_imagery_products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.satellite_imagery_products (product_idsource_idproduct_nameproduct_typeband_numberband_namewavelength_umscan_start_timescan_end_timescan_duration_secondsgrid_latitudegrid_longitudegrid_geomgrid_resolution_kmpixel_valuecalibrated_valuebrightness_temperature_kreflectance_percentcloud_top_height_mcloud_top_temperature_kcloud_phasecloud_optical_depthfire_detection_confidencefire_temperature_kfire_power_mwprecipitation_rate_mmhsource_fileaws_bucketaws_keyfile_formatcompression_typedecompression_statusspatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_northingestion_timestampprocessing_duration_secondsrecords_processed) FROM stdin;
\.


--
-- Data for Name: satellite_imagery_sources; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.satellite_imagery_sources (source_idsatellite_namesatellite_typesensor_nameorbital_positioncoverage_areaspatial_resolution_kmscan_frequency_minutestemporal_resolution_minutesoperational_statusfirst_operational_datelast_update_datecreated_timestampupdated_timestamp) FROM stdin;
\.


--
-- Data for Name: satellite_transformation_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.satellite_transformation_log (transformation_idsource_idsource_filetransformation_typetransformation_start_timetransformation_end_timetransformation_duration_secondsinput_formatinput_size_bytesinput_bandsinput_dimensionsoutput_formatoutput_size_bytesoutput_recordstransformation_statuserror_messageprocessing_methodprocessing_parameterscrs_transformationspatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_northcreated_timestamp) FROM stdin;
\.


--
-- Data for Name: shapefile_boundaries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.shapefile_boundaries (boundary_idfeature_typefeature_namefeature_identifierboundary_geomsource_shapefilesource_crstarget_crsfeature_countspatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_northload_timestamptransformation_statusstate_codeoffice_code) FROM stdin;
cwa_001	CWA	New York City	OKX	\N	w_18mr25.shp	EPSG:4326	EPSG:4326	1	-74.500000	40.400000	-73.500000	41.000000	2026-02-04 05:59:09.750239	Success	NY	OKX
cwa_002	CWA	Los Angeles	LOX	\N	w_18mr25.shp	EPSG:4326	EPSG:4326	1	-118.800000	33.700000	-117.500000	34.500000	2026-02-04 05:59:09.750239	Success	CA	LOX
cwa_003	CWA	Chicago	LOT	\N	w_18mr25.shp	EPSG:4326	EPSG:4326	1	-88.200000	41.500000	-87.300000	42.100000	2026-02-04 05:59:09.750239	Success	IL	LOT
cwa_004	CWA	Miami	MFL	\N	w_18mr25.shp	EPSG:4326	EPSG:4326	1	-80.500000	25.300000	-79.800000	26.200000	2026-02-04 05:59:09.750239	Success	FL	MFL
cwa_005	CWA	Seattle	SEW	\N	w_18mr25.shp	EPSG:4326	EPSG:4326	1	-122.600000	47.300000	-121.800000	47.800000	2026-02-04 05:59:09.750239	Success	WA	SEW
fz_001	FireZone	Southern California Fire Zone 1	CAZ241	\N	fz18mr25.shp	EPSG:4326	EPSG:4326	1	-118.500000	33.800000	-117.200000	34.200000	2026-02-04 05:59:09.750781	Success	CA	\N
fz_002	FireZone	Arizona Fire Zone 5	AZZ005	\N	fz18mr25.shp	EPSG:4326	EPSG:4326	1	-112.200000	33.200000	-111.500000	33.800000	2026-02-04 05:59:09.750781	Success	AZ	\N
fz_003	FireZone	Colorado Fire Zone 12	COZ012	\N	fz18mr25.shp	EPSG:4326	EPSG:4326	1	-105.100000	39.500000	-104.500000	40.000000	2026-02-04 05:59:09.750781	Success	CO	\N
mz_001	MarineZone	New York Harbor	ANZ330	\N	mz18mr25.shp	EPSG:4326	EPSG:4326	1	-74.200000	40.500000	-73.800000	40.800000	2026-02-04 05:59:09.751087	Success	NY	\N
mz_002	MarineZone	San Francisco Bay	PZZ530	\N	mz18mr25.shp	EPSG:4326	EPSG:4326	1	-122.600000	37.600000	-122.200000	37.900000	2026-02-04 05:59:09.751087	Success	CA	\N
mz_003	MarineZone	Puget Sound	PZZ131	\N	mz18mr25.shp	EPSG:4326	EPSG:4326	1	-122.800000	47.400000	-122.200000	47.800000	2026-02-04 05:59:09.751087	Success	WA	\N
\.


--
-- Data for Name: shapefile_integration_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.shapefile_integration_log (log_idshapefile_namesource_pathfeature_typefeature_countsource_crstarget_crsogr2ogr_commandtransformed_pathspatial_extent_westspatial_extent_southspatial_extent_eastspatial_extent_northtransformation_statustarget_tableload_timestampprocessing_duration_secondserror_message) FROM stdin;
log_shp_001	w_18mr25.shp	/data/raw/shapefiles/cwa/w_18mr25.shp	CWA	122	EPSG:4326	EPSG:4326	ogr2ogr -t_srs EPSG:4326	/data/transformed/shapefiles/cwa/w_18mr25_wgs84.shp	-125.000000	24.000000	-66.000000	49.000000	Success	shapefile_boundaries	2026-02-03 11:00:00	120	\N
log_shp_002	fz18mr25.shp	/data/raw/shapefiles/firezones/fz18mr25.shp	FireZone	350	EPSG:4326	EPSG:4326	ogr2ogr -t_srs EPSG:4326	/data/transformed/shapefiles/firezones/fz18mr25_wgs84.shp	-125.000000	24.000000	-66.000000	49.000000	Success	shapefile_boundaries	2026-02-03 11:00:00	95	\N
log_shp_003	mz18mr25.shp	/data/raw/shapefiles/marine/mz18mr25.shp	MarineZone	85	EPSG:4326	EPSG:4326	ogr2ogr -t_srs EPSG:4326	/data/transformed/shapefiles/marine/mz18mr25_wgs84.shp	-125.000000	24.000000	-66.000000	49.000000	Success	shapefile_boundaries	2026-02-03 11:00:00	65	\N
\.


--
-- Data for Name: load_status; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.load_status (load_idsource_filetarget_tableload_start_timeload_end_timeload_duration_secondsrecords_loadedfile_size_mbload_rate_mb_per_secload_statuserror_messagewarehousedata_source_type) FROM stdin;
load_001	/data/transformed/grib2/ds.temp_transformed.tif	grib2_forecasts	2026-02-03 12:05:00	2026-02-03 12:05:45	45	50000	125.50	2.79	Success	\N	WEATHER_WH	GRIB2
load_002	/data/transformed/shapefiles/cwa/w_18mr25_wgs84.shp	shapefile_boundaries	2026-02-03 11:00:00	2026-02-03 11:02:00	120	122	2.30	0.02	Success	\N	WEATHER_WH	Shapefile
load_003	/data/api/observations_20260203.json	weather_observations	2026-02-03 12:00:00	2026-02-03 12:00:15	15	5000	0.50	0.03	Success	\N	WEATHER_WH	API
\.


--
-- Data for Name: spatial_join_results; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.spatial_join_results (join_idgrib_fileshapefile_namejoin_typegdal_commandfeatures_matchedfeatures_totalmatch_percentageoutput_filejoin_timestampforecast_idboundary_id) FROM stdin;
join_001	ds.temp.bin	w_18mr25.shp	Point-in-Polygon	gdalwarp -cutline	45000	50000	90.00	/data/transformed/spatial_joins/temp_cwa_clipped.tif	2026-02-04 05:59:09.754254	grib_temp_001	cwa_001
join_002	ds.qpf.bin	fz18mr25.shp	Raster-to-Vector	gdalwarp -cutline	32000	50000	64.00	/data/transformed/spatial_joins/qpf_firezone_clipped.tif	2026-02-04 05:59:09.754254	grib_qpf_001	fz_001
join_003	ds.wspd.bin	mz18mr25.shp	Clip	gdalwarp -cutline -crop_to_cutline	15000	50000	30.00	/data/transformed/spatial_joins/wspd_marine_clipped.tif	2026-02-04 05:59:09.754254	grib_wspd_001	mz_001
\.


--
-- Data for Name: us_wide_composite_products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.us_wide_composite_products (composite_idproduct_typecomposite_timegrid_latitudegrid_longitudegrid_geomgrid_resolution_kmnexrad_reflectivity_dbznexrad_velocity_msnexrad_precipitation_rate_mmhnexrad_contribution_weightsatellite_brightness_temperature_ksatellite_reflectance_percentsatellite_cloud_top_height_msatellite_precipitation_rate_mmhsatellite_contribution_weightcomposite_precipitation_rate_mmhcomposite_cloud_fractioncomposite_storm_severitydata_quality_scorecoverage_percentagenexrad_sites_countsatellite_sources_countcomposite_generation_timestampcomposite_method) FROM stdin;
\.


--
-- Data for Name: weather_alerts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_alerts (alert_idevent_typeseverityurgencycertaintyheadlinedescriptioninstructioneffective_timeexpires_timeonset_timeends_timearea_descriptiongeocode_typegeocode_valuestate_codecounty_codecwa_codeingestion_timestampalert_geometry) FROM stdin;
\.


--
-- Data for Name: weather_forecast_aggregations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_forecast_aggregations (aggregation_idparameter_nameforecast_timeboundary_idfeature_typefeature_namemin_valuemax_valueavg_valuemedian_valuestd_dev_valuegrid_cells_countaggregation_timestamp) FROM stdin;
\.


--
-- Data for Name: weather_observations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_observations (observation_idstation_idstation_nameobservation_timestation_latitudestation_longitudestation_geomtemperaturedewpointhumiditywind_speedwind_directionpressurevisibilitysky_coverprecipitation_amountdata_freshness_minutesload_timestampdata_sourceapi_endpointapi_response_status) FROM stdin;
obs_001	KNYC	New York Central Park	2026-02-03 12:00:00	40.7850000	-73.9690000	\N	45.20	42.10	88.50	12.30	270	1013.20	10.00	Overcast	0.15	5	2026-02-04 05:59:09.753308	NWS_API	\N	\N
obs_002	KLAX	Los Angeles International	2026-02-03 12:00:00	33.9420000	-118.4080000	\N	72.10	65.30	78.20	8.10	180	1015.80	10.00	Clear	0.00	5	2026-02-04 05:59:09.753308	NWS_API	\N	\N
obs_003	KORD	Chicago O'Hare	2026-02-03 12:00:00	41.9790000	-87.9070000	\N	38.50	35.20	85.10	15.50	320	1012.50	8.00	Partly Cloudy	0.08	5	2026-02-04 05:59:09.753308	NWS_API	\N	\N
obs_004	KMIA	Miami International	2026-02-03 12:00:00	25.7950000	-80.2900000	\N	78.50	74.20	90.30	10.50	120	1014.30	10.00	Scattered Clouds	0.25	5	2026-02-04 05:59:09.753308	NWS_API	\N	\N
obs_005	KSEA	Seattle-Tacoma	2026-02-03 12:00:00	47.4490000	-122.3090000	\N	52.30	48.10	92.70	18.20	250	1011.90	7.00	Overcast	0.12	5	2026-02-04 05:59:09.753308	NWS_API	\N	\N
\.


--
-- Data for Name: weather_stations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_stations (station_idstation_namestation_latitudestation_longitudestation_geomelevation_metersstate_codecounty_namecwa_codestation_typeactive_statusfirst_observation_datelast_observation_dateupdate_frequency_minutes) FROM stdin;
KNYC	New York Central Park	40.7850000	-73.9690000	\N	40.00	NY	New York	OKX	ASOS	t	2020-01-01	2026-02-03	5
KLAX	Los Angeles International	33.9420000	-118.4080000	\N	38.00	CA	Los Angeles	LOX	ASOS	t	2020-01-01	2026-02-03	5
KORD	Chicago O'Hare	41.9790000	-87.9070000	\N	203.00	IL	Cook	LOT	ASOS	t	2020-01-01	2026-02-03	5
KMIA	Miami International	25.7950000	-80.2900000	\N	2.00	FL	Miami-Dade	MFL	ASOS	t	2020-01-01	2026-02-03	5
KSEA	Seattle-Tacoma	47.4490000	-122.3090000	\N	137.00	WA	King	SEW	ASOS	t	2020-01-01	2026-02-03	5
\.


--
-- Name: crs_transformation_parameters crs_transformation_parameters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crs_transformation_parameters
    ADD CONSTRAINT crs_transformation_parameters_pkey PRIMARY KEY (transformation_id);


--
-- Name: data_quality_metrics data_quality_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_quality_metrics
    ADD CONSTRAINT data_quality_metrics_pkey PRIMARY KEY (metric_id);


--
-- Name: data_source_statistics data_source_statistics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.data_source_statistics
    ADD CONSTRAINT data_source_statistics_pkey PRIMARY KEY (stat_id);


--
-- Name: forecast_rate_mapping forecast_rate_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forecast_rate_mapping
    ADD CONSTRAINT forecast_rate_mapping_pkey PRIMARY KEY (mapping_id);


--
-- Name: geoplatform_dataset_log geoplatform_dataset_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.geoplatform_dataset_log
    ADD CONSTRAINT geoplatform_dataset_log_pkey PRIMARY KEY (dataset_id);


--
-- Name: grib2_forecasts grib2_forecasts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grib2_forecasts
    ADD CONSTRAINT grib2_forecasts_pkey PRIMARY KEY (forecast_id);


--
-- Name: grib2_transformation_log grib2_transformation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grib2_transformation_log
    ADD CONSTRAINT grib2_transformation_log_pkey PRIMARY KEY (log_id);


--
-- Name: insurance_claims_history insurance_claims_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.insurance_claims_history
    ADD CONSTRAINT insurance_claims_history_pkey PRIMARY KEY (claim_id);


--
-- Name: insurance_policy_areas insurance_policy_areas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.insurance_policy_areas
    ADD CONSTRAINT insurance_policy_areas_pkey PRIMARY KEY (policy_area_id);


--
-- Name: insurance_rate_tables insurance_rate_tables_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.insurance_rate_tables
    ADD CONSTRAINT insurance_rate_tables_pkey PRIMARY KEY (rate_table_id);


--
-- Name: insurance_risk_factors insurance_risk_factors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.insurance_risk_factors
    ADD CONSTRAINT insurance_risk_factors_pkey PRIMARY KEY (risk_factor_id);


--
-- Name: model_forecast_comparison model_forecast_comparison_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model_forecast_comparison
    ADD CONSTRAINT model_forecast_comparison_pkey PRIMARY KEY (comparison_id);


--
-- Name: nexrad_level2_data nexrad_level2_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nexrad_level2_data
    ADD CONSTRAINT nexrad_level2_data_pkey PRIMARY KEY (radar_data_id);


--
-- Name: nexrad_radar_sites nexrad_radar_sites_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nexrad_radar_sites
    ADD CONSTRAINT nexrad_radar_sites_pkey PRIMARY KEY (site_id);


--
-- Name: nexrad_reflectivity_grid nexrad_reflectivity_grid_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nexrad_reflectivity_grid
    ADD CONSTRAINT nexrad_reflectivity_grid_pkey PRIMARY KEY (grid_id);


--
-- Name: nexrad_storm_cells nexrad_storm_cells_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nexrad_storm_cells
    ADD CONSTRAINT nexrad_storm_cells_pkey PRIMARY KEY (storm_cell_id);


--
-- Name: nexrad_transformation_log nexrad_transformation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nexrad_transformation_log
    ADD CONSTRAINT nexrad_transformation_log_pkey PRIMARY KEY (transformation_id);


--
-- Name: nexrad_velocity_grid nexrad_velocity_grid_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nexrad_velocity_grid
    ADD CONSTRAINT nexrad_velocity_grid_pkey PRIMARY KEY (grid_id);


--
-- Name: nws_api_observation_log nws_api_observation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.nws_api_observation_log
    ADD CONSTRAINT nws_api_observation_log_pkey PRIMARY KEY (log_id);


--
-- Name: rate_table_comparison rate_table_comparison_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rate_table_comparison
    ADD CONSTRAINT rate_table_comparison_pkey PRIMARY KEY (comparison_id);


--
-- Name: satellite_imagery_grid satellite_imagery_grid_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.satellite_imagery_grid
    ADD CONSTRAINT satellite_imagery_grid_pkey PRIMARY KEY (grid_id);


--
-- Name: satellite_imagery_products satellite_imagery_products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.satellite_imagery_products
    ADD CONSTRAINT satellite_imagery_products_pkey PRIMARY KEY (product_id);


--
-- Name: satellite_imagery_sources satellite_imagery_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.satellite_imagery_sources
    ADD CONSTRAINT satellite_imagery_sources_pkey PRIMARY KEY (source_id);


--
-- Name: satellite_transformation_log satellite_transformation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.satellite_transformation_log
    ADD CONSTRAINT satellite_transformation_log_pkey PRIMARY KEY (transformation_id);


--
-- Name: shapefile_boundaries shapefile_boundaries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shapefile_boundaries
    ADD CONSTRAINT shapefile_boundaries_pkey PRIMARY KEY (boundary_id);


--
-- Name: shapefile_integration_log shapefile_integration_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shapefile_integration_log
    ADD CONSTRAINT shapefile_integration_log_pkey PRIMARY KEY (log_id);


--
-- Name: load_status load_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.load_status
    ADD CONSTRAINT load_status_pkey PRIMARY KEY (load_id);


--
-- Name: spatial_join_results spatial_join_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spatial_join_results
    ADD CONSTRAINT spatial_join_results_pkey PRIMARY KEY (join_id);


--
-- Name: us_wide_composite_products us_wide_composite_products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.us_wide_composite_products
    ADD CONSTRAINT us_wide_composite_products_pkey PRIMARY KEY (composite_id);


--
-- Name: weather_alerts weather_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_alerts
    ADD CONSTRAINT weather_alerts_pkey PRIMARY KEY (alert_id);


--
-- Name: weather_forecast_aggregations weather_forecast_aggregations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_forecast_aggregations
    ADD CONSTRAINT weather_forecast_aggregations_pkey PRIMARY KEY (aggregation_id);


--
-- Name: weather_observations weather_observations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_observations
    ADD CONSTRAINT weather_observations_pkey PRIMARY KEY (observation_id);


--
-- Name: weather_stations weather_stations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_stations
    ADD CONSTRAINT weather_stations_pkey PRIMARY KEY (station_id);


--
-- Name: idx_data_source_statistics_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_data_source_statistics_date ON public.data_source_statistics USING btree (source_typestat_date);


--
-- Name: idx_forecast_aggregations_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_forecast_aggregations_time ON public.weather_forecast_aggregations USING btree (forecast_timeparameter_name);


--
-- Name: idx_forecast_rate_mapping_forecast; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_forecast_rate_mapping_forecast ON public.forecast_rate_mapping USING btree (forecast_id);


--
-- Name: idx_forecast_rate_mapping_rate_table; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_forecast_rate_mapping_rate_table ON public.forecast_rate_mapping USING btree (rate_table_id);


--
-- Name: idx_grib2_forecasts_parameter_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_grib2_forecasts_parameter_time ON public.grib2_forecasts USING btree (parameter_nameforecast_time);


--
-- Name: idx_insurance_claims_history_area_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_insurance_claims_history_area_date ON public.insurance_claims_history USING btree (policy_area_idloss_date);


--
-- Name: idx_insurance_claims_history_type_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_insurance_claims_history_type_date ON public.insurance_claims_history USING btree (claim_typeloss_date);


--
-- Name: idx_insurance_policy_areas_boundary; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_insurance_policy_areas_boundary ON public.insurance_policy_areas USING btree (boundary_id);


--
-- Name: idx_insurance_policy_areas_type_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_insurance_policy_areas_type_active ON public.insurance_policy_areas USING btree (policy_typeis_active);


--
-- Name: idx_insurance_rate_tables_day_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_insurance_rate_tables_day_date ON public.insurance_rate_tables USING btree (forecast_dayforecast_date);


--
-- Name: idx_insurance_rate_tables_policy_period; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_insurance_rate_tables_policy_period ON public.insurance_rate_tables USING btree (policy_area_idforecast_period_startforecast_period_end);


--
-- Name: idx_insurance_risk_factors_day_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_insurance_risk_factors_day_date ON public.insurance_risk_factors USING btree (forecast_dayforecast_date);


--
-- Name: idx_insurance_risk_factors_policy_period; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_insurance_risk_factors_policy_period ON public.insurance_risk_factors USING btree (policy_area_idforecast_period_startforecast_period_end);


--
-- Name: idx_model_forecast_comparison_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_model_forecast_comparison_time ON public.model_forecast_comparison USING btree (forecast_timeparameter_name);


--
-- Name: idx_nexrad_level2_site_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nexrad_level2_site_time ON public.nexrad_level2_data USING btree (site_idscan_time);


--
-- Name: idx_nexrad_reflectivity_grid_site_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nexrad_reflectivity_grid_site_time ON public.nexrad_reflectivity_grid USING btree (site_idscan_time);


--
-- Name: idx_nexrad_sites_state_cwa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nexrad_sites_state_cwa ON public.nexrad_radar_sites USING btree (state_codecwa_code);


--
-- Name: idx_nexrad_storm_cells_site_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nexrad_storm_cells_site_time ON public.nexrad_storm_cells USING btree (site_idfirst_detection_time);


--
-- Name: idx_nexrad_velocity_grid_site_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_nexrad_velocity_grid_site_time ON public.nexrad_velocity_grid USING btree (site_idscan_time);


--
-- Name: idx_rate_table_comparison_policy_period; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rate_table_comparison_policy_period ON public.rate_table_comparison USING btree (policy_area_idforecast_period_startforecast_period_end);


--
-- Name: idx_satellite_imagery_grid_source_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_satellite_imagery_grid_source_time ON public.satellite_imagery_grid USING btree (source_idscan_time);


--
-- Name: idx_satellite_products_source_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_satellite_products_source_time ON public.satellite_imagery_products USING btree (source_idscan_start_time);


--
-- Name: idx_shapefile_boundaries_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_shapefile_boundaries_type ON public.shapefile_boundaries USING btree (feature_type);


--
-- Name: idx_spatial_join_forecast_boundary; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_spatial_join_forecast_boundary ON public.spatial_join_results USING btree (forecast_idboundary_id);


--
-- Name: idx_us_wide_composite_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_us_wide_composite_time ON public.us_wide_composite_products USING btree (composite_timeproduct_type);


--
-- Name: idx_weather_alerts_event_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_weather_alerts_event_time ON public.weather_alerts USING btree (event_typeeffective_time);


--
-- Name: idx_weather_observations_station_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_weather_observations_station_time ON public.weather_observations USING btree (station_idobservation_time);


--
-- PostgreSQL database dump complete
--

\unrestrict Ln089kzaevMx8zBiEPKfuiazUPOL97ooNfndlaAtJbMfXCHQa58A1N7q8EG8GRu

