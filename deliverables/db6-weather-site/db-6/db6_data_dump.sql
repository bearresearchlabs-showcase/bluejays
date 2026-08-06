--
-- PostgreSQL database dump
--

\restrict AUyhxEEkNFIRaYTYfyddduhkRCe6SJ8hyg4myJFLgOqxRh2vFjmq84ikb2Iadfo

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
-- Data for Name: crs_transformation_parameters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.crs_transformation_parameters (transformation_id, source_crs, target_crs, source_crs_name, target_crs_name, transformation_method, central_meridian, false_easting, false_northing, scale_factor, latitude_of_origin, units, accuracy_meters, usage_count) FROM stdin;
tran_001	EPSG:4326	EPSG:3857	WGS84 Geographic	Web Mercator	GDAL	\N	\N	\N	\N	\N	meters	0.50	150
tran_002	EPSG:2227	EPSG:4326	California State Plane Zone 5	WGS84 Geographic	PROJ	\N	\N	\N	\N	\N	degrees	1.20	85
tran_003	EPSG:4326	EPSG:4326	WGS84 Geographic	WGS84 Geographic	GDAL	\N	\N	\N	\N	\N	degrees	0.00	200
\.


--
-- Data for Name: data_quality_metrics; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.data_quality_metrics (metric_id, metric_date, data_source, files_processed, files_successful, files_failed, success_rate, total_records, records_with_errors, error_rate, spatial_coverage_km2, temporal_coverage_hours, data_freshness_minutes, calculation_timestamp) FROM stdin;
metric_001	2026-02-03	GRIB2	15	14	1	93.33	750000	2500	0.33	7850000.00	168	5	2026-02-04 05:59:09.754488
metric_002	2026-02-03	Shapefile	8	8	0	100.00	557	0	0.00	7850000.00	0	60	2026-02-04 05:59:09.754488
metric_003	2026-02-03	API	0	0	0	0.00	5000	25	0.50	0.00	24	5	2026-02-04 05:59:09.754488
\.


--
-- Data for Name: grib2_forecasts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grib2_forecasts (forecast_id, parameter_name, forecast_time, grid_cell_latitude, grid_cell_longitude, grid_cell_geom, parameter_value, source_file, source_crs, target_crs, grid_resolution_x, grid_resolution_y, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, load_timestamp, transformation_status) FROM stdin;
grib_temp_001	Temperature	2026-02-03 12:00:00	40.7850000	-73.9690000	\N	45.50	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success
grib_temp_002	Temperature	2026-02-03 12:00:00	33.9420000	-118.4080000	\N	72.30	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success
grib_temp_003	Temperature	2026-02-03 12:00:00	41.9790000	-87.9070000	\N	38.20	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success
grib_temp_004	Temperature	2026-02-03 12:00:00	25.7950000	-80.2900000	\N	78.90	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success
grib_temp_005	Temperature	2026-02-03 12:00:00	47.4490000	-122.3090000	\N	52.10	ds.temp.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.751897	Success
grib_qpf_001	Precipitation	2026-02-03 12:00:00	40.7850000	-73.9690000	\N	0.15	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success
grib_qpf_002	Precipitation	2026-02-03 12:00:00	33.9420000	-118.4080000	\N	0.00	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success
grib_qpf_003	Precipitation	2026-02-03 12:00:00	41.9790000	-87.9070000	\N	0.08	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success
grib_qpf_004	Precipitation	2026-02-03 12:00:00	25.7950000	-80.2900000	\N	0.25	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success
grib_qpf_005	Precipitation	2026-02-03 12:00:00	47.4490000	-122.3090000	\N	0.12	ds.qpf.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752404	Success
grib_wspd_001	WindSpeed	2026-02-03 12:00:00	40.7850000	-73.9690000	\N	12.50	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success
grib_wspd_002	WindSpeed	2026-02-03 12:00:00	33.9420000	-118.4080000	\N	8.30	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success
grib_wspd_003	WindSpeed	2026-02-03 12:00:00	41.9790000	-87.9070000	\N	15.20	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success
grib_wspd_004	WindSpeed	2026-02-03 12:00:00	25.7950000	-80.2900000	\N	10.70	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success
grib_wspd_005	WindSpeed	2026-02-03 12:00:00	47.4490000	-122.3090000	\N	18.40	ds.wspd.bin	EPSG:4326	EPSG:3857	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	2026-02-04 05:59:09.752975	Success
\.


--
-- Data for Name: grib2_transformation_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.grib2_transformation_log (log_id, file_name, source_path, parameter_name, forecast_time, source_crs, target_crs, gdal_command, output_file, grid_resolution_x, grid_resolution_y, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status, target_table, load_timestamp, processing_duration_seconds, records_processed, error_message) FROM stdin;
log_grib_001	ds.temp.bin	/data/raw/grib2/ds.temp.bin	Temperature	2026-02-03 12:00:00	EPSG:4326	EPSG:3857	gdal_translate -of GTiff -a_srs EPSG:3857	/data/transformed/grib2/ds.temp_transformed.tif	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	Success	grib2_forecasts	2026-02-03 12:05:00	45	50000	\N
log_grib_002	ds.qpf.bin	/data/raw/grib2/ds.qpf.bin	Precipitation	2026-02-03 12:00:00	EPSG:4326	EPSG:3857	gdal_translate -of GTiff -a_srs EPSG:3857	/data/transformed/grib2/ds.qpf_transformed.tif	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	Success	grib2_forecasts	2026-02-03 12:05:00	42	50000	\N
log_grib_003	ds.wspd.bin	/data/raw/grib2/ds.wspd.bin	WindSpeed	2026-02-03 12:00:00	EPSG:4326	EPSG:3857	gdal_translate -of GTiff -a_srs EPSG:3857	/data/transformed/grib2/ds.wspd_transformed.tif	0.025000	0.025000	-125.000000	24.000000	-66.000000	49.000000	Success	grib2_forecasts	2026-02-03 12:05:00	38	50000	\N
\.


--
-- Data for Name: shapefile_boundaries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.shapefile_boundaries (boundary_id, feature_type, feature_name, feature_identifier, boundary_geom, source_shapefile, source_crs, target_crs, feature_count, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, load_timestamp, transformation_status, state_code, office_code) FROM stdin;
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

COPY public.shapefile_integration_log (log_id, shapefile_name, source_path, feature_type, feature_count, source_crs, target_crs, ogr2ogr_command, transformed_path, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status, target_table, load_timestamp, processing_duration_seconds, error_message) FROM stdin;
log_shp_001	w_18mr25.shp	/data/raw/shapefiles/cwa/w_18mr25.shp	CWA	122	EPSG:4326	EPSG:4326	ogr2ogr -t_srs EPSG:4326	/data/transformed/shapefiles/cwa/w_18mr25_wgs84.shp	-125.000000	24.000000	-66.000000	49.000000	Success	shapefile_boundaries	2026-02-03 11:00:00	120	\N
log_shp_002	fz18mr25.shp	/data/raw/shapefiles/firezones/fz18mr25.shp	FireZone	350	EPSG:4326	EPSG:4326	ogr2ogr -t_srs EPSG:4326	/data/transformed/shapefiles/firezones/fz18mr25_wgs84.shp	-125.000000	24.000000	-66.000000	49.000000	Success	shapefile_boundaries	2026-02-03 11:00:00	95	\N
log_shp_003	mz18mr25.shp	/data/raw/shapefiles/marine/mz18mr25.shp	MarineZone	85	EPSG:4326	EPSG:4326	ogr2ogr -t_srs EPSG:4326	/data/transformed/shapefiles/marine/mz18mr25_wgs84.shp	-125.000000	24.000000	-66.000000	49.000000	Success	shapefile_boundaries	2026-02-03 11:00:00	65	\N
\.


--
-- Data for Name: load_status; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.load_status (load_id, source_file, target_table, load_start_time, load_end_time, load_duration_seconds, records_loaded, file_size_mb, load_rate_mb_per_sec, load_status, error_message, warehouse, data_source_type) FROM stdin;
load_001	/data/transformed/grib2/ds.temp_transformed.tif	grib2_forecasts	2026-02-03 12:05:00	2026-02-03 12:05:45	45	50000	125.50	2.79	Success	\N	WEATHER_WH	GRIB2
load_002	/data/transformed/shapefiles/cwa/w_18mr25_wgs84.shp	shapefile_boundaries	2026-02-03 11:00:00	2026-02-03 11:02:00	120	122	2.30	0.02	Success	\N	WEATHER_WH	Shapefile
load_003	/data/api/observations_20260203.json	weather_observations	2026-02-03 12:00:00	2026-02-03 12:00:15	15	5000	0.50	0.03	Success	\N	WEATHER_WH	API
\.


--
-- Data for Name: spatial_join_results; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.spatial_join_results (join_id, grib_file, shapefile_name, join_type, gdal_command, features_matched, features_total, match_percentage, output_file, join_timestamp, forecast_id, boundary_id) FROM stdin;
join_001	ds.temp.bin	w_18mr25.shp	Point-in-Polygon	gdalwarp -cutline	45000	50000	90.00	/data/transformed/spatial_joins/temp_cwa_clipped.tif	2026-02-04 05:59:09.754254	grib_temp_001	cwa_001
join_002	ds.qpf.bin	fz18mr25.shp	Raster-to-Vector	gdalwarp -cutline	32000	50000	64.00	/data/transformed/spatial_joins/qpf_firezone_clipped.tif	2026-02-04 05:59:09.754254	grib_qpf_001	fz_001
join_003	ds.wspd.bin	mz18mr25.shp	Clip	gdalwarp -cutline -crop_to_cutline	15000	50000	30.00	/data/transformed/spatial_joins/wspd_marine_clipped.tif	2026-02-04 05:59:09.754254	grib_wspd_001	mz_001
\.


--
-- Data for Name: weather_forecast_aggregations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_forecast_aggregations (aggregation_id, parameter_name, forecast_time, boundary_id, feature_type, feature_name, min_value, max_value, avg_value, median_value, std_dev_value, grid_cells_count, aggregation_timestamp) FROM stdin;
\.


--
-- Data for Name: weather_observations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_observations (observation_id, station_id, station_name, observation_time, station_latitude, station_longitude, station_geom, temperature, dewpoint, humidity, wind_speed, wind_direction, pressure, visibility, sky_cover, precipitation_amount, data_freshness_minutes, load_timestamp, data_source) FROM stdin;
obs_001	KNYC	New York Central Park	2026-02-03 12:00:00	40.7850000	-73.9690000	\N	45.20	42.10	88.50	12.30	270	1013.20	10.00	Overcast	0.15	5	2026-02-04 05:59:09.753308	NWS_API
obs_002	KLAX	Los Angeles International	2026-02-03 12:00:00	33.9420000	-118.4080000	\N	72.10	65.30	78.20	8.10	180	1015.80	10.00	Clear	0.00	5	2026-02-04 05:59:09.753308	NWS_API
obs_003	KORD	Chicago O'Hare	2026-02-03 12:00:00	41.9790000	-87.9070000	\N	38.50	35.20	85.10	15.50	320	1012.50	8.00	Partly Cloudy	0.08	5	2026-02-04 05:59:09.753308	NWS_API
obs_004	KMIA	Miami International	2026-02-03 12:00:00	25.7950000	-80.2900000	\N	78.50	74.20	90.30	10.50	120	1014.30	10.00	Scattered Clouds	0.25	5	2026-02-04 05:59:09.753308	NWS_API
obs_005	KSEA	Seattle-Tacoma	2026-02-03 12:00:00	47.4490000	-122.3090000	\N	52.30	48.10	92.70	18.20	250	1011.90	7.00	Overcast	0.12	5	2026-02-04 05:59:09.753308	NWS_API
\.


--
-- Data for Name: weather_stations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_stations (station_id, station_name, station_latitude, station_longitude, station_geom, elevation_meters, state_code, county_name, cwa_code, station_type, active_status, first_observation_date, last_observation_date, update_frequency_minutes) FROM stdin;
KNYC	New York Central Park	40.7850000	-73.9690000	\N	40.00	NY	New York	OKX	ASOS	t	2020-01-01	2026-02-03	5
KLAX	Los Angeles International	33.9420000	-118.4080000	\N	38.00	CA	Los Angeles	LOX	ASOS	t	2020-01-01	2026-02-03	5
KORD	Chicago O'Hare	41.9790000	-87.9070000	\N	203.00	IL	Cook	LOT	ASOS	t	2020-01-01	2026-02-03	5
KMIA	Miami International	25.7950000	-80.2900000	\N	2.00	FL	Miami-Dade	MFL	ASOS	t	2020-01-01	2026-02-03	5
KSEA	Seattle-Tacoma	47.4490000	-122.3090000	\N	137.00	WA	King	SEW	ASOS	t	2020-01-01	2026-02-03	5
\.


--
-- PostgreSQL database dump complete
--

\unrestrict AUyhxEEkNFIRaYTYfyddduhkRCe6SJ8hyg4myJFLgOqxRh2vFjmq84ikb2Iadfo

