--
-- PostgreSQL database dump
--

\restrict LpoQ5Y0bpgv93haJvMV3a6CyvG2ByeNW8OOO1V9Kv4Sixl6k4cKEGXUrN3X1qxx

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


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
    transformation_status character varying(50)
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
    data_source character varying(50) DEFAULT 'NWS_API'::character varying
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
-- Name: idx_forecast_aggregations_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_forecast_aggregations_time ON public.weather_forecast_aggregations USING btree (forecast_time, parameter_name);


--
-- Name: idx_grib2_forecasts_parameter_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_grib2_forecasts_parameter_time ON public.grib2_forecasts USING btree (parameter_name, forecast_time);


--
-- Name: idx_shapefile_boundaries_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_shapefile_boundaries_type ON public.shapefile_boundaries USING btree (feature_type);


--
-- Name: idx_spatial_join_forecast_boundary; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_spatial_join_forecast_boundary ON public.spatial_join_results USING btree (forecast_id, boundary_id);


--
-- Name: idx_weather_observations_station_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_weather_observations_station_time ON public.weather_observations USING btree (station_id, observation_time);


--
-- PostgreSQL database dump complete
--

\unrestrict LpoQ5Y0bpgv93haJvMV3a6CyvG2ByeNW8OOO1V9Kv4Sixl6k4cKEGXUrN3X1qxx

