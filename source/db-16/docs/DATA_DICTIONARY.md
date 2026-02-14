# Data Dictionary - db-16

## Flood Risk Assessment Database for M&A Due Diligence

### fema_flood_zones
FEMA National Flood Hazard Layer flood zone designations and Base Flood Elevations.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| zone_id | VARCHAR(255) | NO | Primary key |
| zone_code | VARCHAR(10) | NO | FEMA zone code (A, AE, AH, AO, V, VE, X, D) |
| zone_description | VARCHAR(255) | YES | Human-readable zone description |
| base_flood_elevation | NUMERIC(10,2) | YES | BFE in feet above sea level |
| zone_geom | GEOGRAPHY | YES | Polygon geometry for flood zone boundary |
| community_id | VARCHAR(50) | YES | FEMA community identifier |
| community_name | VARCHAR(255) | YES | Community name |
| state_code | VARCHAR(2) | YES | Two-letter state code |
| county_fips | VARCHAR(5) | YES | County FIPS code |
| effective_date | DATE | YES | Map effective date |
| map_panel | VARCHAR(50) | YES | FIRM panel number |
| source_file | VARCHAR(500) | YES | Source shapefile name |
| source_crs | VARCHAR(50) | YES | Source coordinate reference system |
| target_crs | VARCHAR(50) | YES | Target CRS (default EPSG:4326) |
| spatial_extent_west | NUMERIC(10,6) | YES | Bounding box west longitude |
| spatial_extent_south | NUMERIC(10,6) | YES | Bounding box south latitude |
| spatial_extent_east | NUMERIC(10,6) | YES | Bounding box east longitude |
| spatial_extent_north | NUMERIC(10,6) | YES | Bounding box north latitude |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |
| transformation_status | VARCHAR(50) | YES | ETL transformation status |

### real_estate_properties
Property locations and characteristics for flood risk assessment in M&A portfolios.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| property_id | VARCHAR(255) | NO | Primary key |
| property_address | VARCHAR(500) | YES | Full property address |
| property_latitude | NUMERIC(10,7) | NO | WGS84 latitude |
| property_longitude | NUMERIC(10,7) | NO | WGS84 longitude |
| property_geom | GEOGRAPHY | YES | Point geometry |
| property_type | VARCHAR(100) | YES | Residential, Commercial, Industrial, Mixed-Use |
| building_value | NUMERIC(15,2) | YES | Building assessed value (USD) |
| land_value | NUMERIC(15,2) | YES | Land assessed value (USD) |
| total_value | NUMERIC(15,2) | YES | Total assessed value (USD) |
| square_footage | NUMERIC(12,2) | YES | Building square footage |
| year_built | INTEGER | YES | Year of construction |
| number_of_floors | INTEGER | YES | Number of floors |
| elevation_feet | NUMERIC(10,2) | YES | Ground elevation above sea level (feet) |
| state_code | VARCHAR(2) | YES | Two-letter state code |
| county_fips | VARCHAR(5) | YES | County FIPS code |
| city_name | VARCHAR(255) | YES | City name |
| zip_code | VARCHAR(10) | YES | ZIP code |
| portfolio_id | VARCHAR(255) | YES | M&A portfolio identifier |
| portfolio_name | VARCHAR(255) | YES | Portfolio name |
| acquisition_date | DATE | YES | Property acquisition date |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### noaa_sea_level_rise
NOAA sea level rise projections and high tide flooding data by coastal station.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| projection_id | VARCHAR(255) | NO | Primary key |
| station_id | VARCHAR(50) | YES | NOAA CO-OPS station identifier |
| station_name | VARCHAR(255) | YES | Station name |
| station_latitude | NUMERIC(10,7) | NO | Station latitude |
| station_longitude | NUMERIC(10,7) | NO | Station longitude |
| station_geom | GEOGRAPHY | YES | Point geometry |
| projection_year | INTEGER | NO | Projection target year |
| scenario | VARCHAR(50) | YES | SLR scenario (Low to Extreme) |
| sea_level_rise_feet | NUMERIC(8,3) | YES | Projected rise in feet |
| confidence_level | VARCHAR(50) | YES | Projection confidence |
| high_tide_flooding_days | INTEGER | YES | Projected annual flood days |
| data_source | VARCHAR(100) | YES | Default: NOAA_CO-OPS |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### usgs_streamflow_gauges
USGS streamflow gauge locations and flood stage thresholds.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| gauge_id | VARCHAR(50) | NO | Primary key (USGS site number) |
| gauge_name | VARCHAR(255) | YES | Gauge station name |
| gauge_latitude | NUMERIC(10,7) | NO | Gauge latitude |
| gauge_longitude | NUMERIC(10,7) | NO | Gauge longitude |
| gauge_geom | GEOGRAPHY | YES | Point geometry |
| drainage_area_sq_miles | NUMERIC(12,2) | YES | Upstream drainage area |
| flood_stage_feet | NUMERIC(8,2) | YES | Action flood stage (feet) |
| moderate_flood_stage_feet | NUMERIC(8,2) | YES | Moderate flood stage |
| major_flood_stage_feet | NUMERIC(8,2) | YES | Major flood stage |
| state_code | VARCHAR(2) | YES | State code |
| county_name | VARCHAR(100) | YES | County name |
| river_name | VARCHAR(255) | YES | River/stream name |
| active_status | BOOLEAN | YES | Currently active gauge |
| first_observation_date | DATE | YES | First recorded observation |
| last_observation_date | DATE | YES | Most recent observation |
| update_frequency_minutes | INTEGER | YES | Data update interval |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### usgs_streamflow_observations
Real-time and historical streamflow measurements from USGS gauges.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| observation_id | VARCHAR(255) | NO | Primary key |
| gauge_id | VARCHAR(50) | NO | FK to usgs_streamflow_gauges |
| observation_time | TIMESTAMP | NO | Observation timestamp |
| gage_height_feet | NUMERIC(8,2) | YES | Gage height (feet) |
| discharge_cfs | NUMERIC(12,2) | YES | Discharge (cubic feet/second) |
| stage_feet | NUMERIC(8,2) | YES | Stage height (feet) |
| flood_category | VARCHAR(50) | YES | None, Action, Minor, Moderate, Major |
| percentile_rank | NUMERIC(5,2) | YES | Historical percentile |
| data_quality_code | VARCHAR(10) | YES | USGS quality code |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### nasa_flood_models
NASA flood model predictions and inundation extents from GFMS, VIIRS, MODIS.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| model_id | VARCHAR(255) | NO | Primary key |
| model_name | VARCHAR(100) | YES | GFMS, LIS, VIIRS, MODIS, FloodPlanet |
| forecast_time | TIMESTAMP | NO | Model forecast timestamp |
| grid_cell_latitude | NUMERIC(10,7) | NO | Grid cell center latitude |
| grid_cell_longitude | NUMERIC(10,7) | NO | Grid cell center longitude |
| grid_cell_geom | GEOGRAPHY | YES | Point geometry |
| inundation_depth_feet | NUMERIC(8,2) | YES | Predicted flood depth (feet) |
| flood_probability | NUMERIC(5,2) | YES | Flood probability (0-100%) |
| flood_severity | VARCHAR(50) | YES | Low, Moderate, High, Extreme |
| model_resolution_meters | INTEGER | YES | Spatial resolution |
| spatial_extent_west | NUMERIC(10,6) | YES | Bounding box west |
| spatial_extent_south | NUMERIC(10,6) | YES | Bounding box south |
| spatial_extent_east | NUMERIC(10,6) | YES | Bounding box east |
| spatial_extent_north | NUMERIC(10,6) | YES | Bounding box north |
| source_file | VARCHAR(500) | YES | Source data file |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### flood_risk_assessments
Comprehensive multi-factor flood risk assessments for properties under M&A evaluation.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| assessment_id | VARCHAR(255) | NO | Primary key |
| property_id | VARCHAR(255) | NO | FK to real_estate_properties |
| assessment_date | DATE | NO | Assessment date |
| assessment_type | VARCHAR(50) | YES | Current, Short-Term, Intermediate-Term, Long-Term |
| time_horizon_years | INTEGER | YES | Projection horizon (5-100 years) |
| fema_zone_code | VARCHAR(10) | YES | FEMA flood zone code |
| fema_zone_id | VARCHAR(255) | YES | FK to fema_flood_zones |
| base_flood_elevation_feet | NUMERIC(10,2) | YES | Base flood elevation |
| flood_zone_risk_score | NUMERIC(5,2) | YES | FEMA zone risk score (0-100) |
| sea_level_rise_feet | NUMERIC(8,3) | YES | Projected SLR at location |
| sea_level_rise_scenario | VARCHAR(50) | YES | SLR scenario used |
| high_tide_flooding_days | INTEGER | YES | Projected annual flood days |
| sea_level_risk_score | NUMERIC(5,2) | YES | Sea level rise risk score (0-100) |
| nearest_gauge_id | VARCHAR(50) | YES | Nearest USGS gauge |
| historical_flood_frequency | INTEGER | YES | Historical flood count |
| flood_probability_percent | NUMERIC(5,2) | YES | Flood probability |
| streamflow_risk_score | NUMERIC(5,2) | YES | Streamflow risk score (0-100) |
| nasa_model_flood_probability | NUMERIC(5,2) | YES | NASA model probability |
| nasa_model_severity | VARCHAR(50) | YES | NASA model severity |
| nasa_model_risk_score | NUMERIC(5,2) | YES | NASA model risk score (0-100) |
| overall_risk_score | NUMERIC(5,2) | YES | Weighted composite score (0-100) |
| risk_category | VARCHAR(50) | YES | Low, Moderate, High, Extreme |
| vulnerability_score | NUMERIC(5,2) | YES | Property vulnerability (0-100) |
| exposure_score | NUMERIC(5,2) | YES | Hazard exposure (0-100) |
| estimated_damage_dollars | NUMERIC(15,2) | YES | Estimated damage (USD) |
| estimated_annual_loss | NUMERIC(15,2) | YES | Expected annual loss (USD) |
| insurance_premium_estimate | NUMERIC(12,2) | YES | Estimated annual premium |
| assessment_methodology | VARCHAR(255) | YES | Methodology description |
| data_sources_used | VARCHAR(500) | YES | Data sources used |
| confidence_level | VARCHAR(50) | YES | Assessment confidence |
| assessment_notes | TEXT | YES | Notes |
| created_by | VARCHAR(255) | YES | Assessor |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### property_flood_zone_intersections
Spatial relationships between properties and FEMA flood zones.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| intersection_id | VARCHAR(255) | NO | Primary key |
| property_id | VARCHAR(255) | NO | FK to real_estate_properties |
| zone_id | VARCHAR(255) | NO | FK to fema_flood_zones |
| intersection_type | VARCHAR(50) | YES | Within, Adjacent, Near |
| distance_to_zone_feet | NUMERIC(10,2) | YES | Distance to zone boundary |
| elevation_difference_feet | NUMERIC(10,2) | YES | Property elevation minus BFE |
| intersection_geom | GEOGRAPHY | YES | Intersection geometry |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### historical_flood_events
Historical flood event records for recurrence analysis.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| event_id | VARCHAR(255) | NO | Primary key |
| event_name | VARCHAR(255) | YES | Event name |
| event_type | VARCHAR(50) | YES | Riverine, Coastal, Flash, Storm Surge, Tidal |
| start_date | DATE | NO | Event start date |
| end_date | DATE | YES | Event end date |
| affected_area_geom | GEOGRAPHY | YES | Polygon of affected area |
| peak_discharge_cfs | NUMERIC(12,2) | YES | Peak discharge |
| peak_stage_feet | NUMERIC(8,2) | YES | Peak stage |
| total_damage_dollars | NUMERIC(15,2) | YES | Total damage (USD) |
| fatalities | INTEGER | YES | Fatality count |
| properties_affected | INTEGER | YES | Properties affected |
| state_code | VARCHAR(2) | YES | State code |
| county_fips | VARCHAR(5) | YES | County FIPS |
| data_source | VARCHAR(100) | YES | Source agency |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### model_performance_metrics
Flood model accuracy and performance tracking.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| metric_id | VARCHAR(255) | NO | Primary key |
| model_name | VARCHAR(100) | NO | Model identifier |
| evaluation_date | DATE | NO | Evaluation date |
| evaluation_period_start | DATE | YES | Period start |
| evaluation_period_end | DATE | YES | Period end |
| total_predictions | INTEGER | YES | Total predictions |
| true_positives | INTEGER | YES | True positives |
| true_negatives | INTEGER | YES | True negatives |
| false_positives | INTEGER | YES | False positives |
| false_negatives | INTEGER | YES | False negatives |
| accuracy | NUMERIC(5,4) | YES | Accuracy (0-1) |
| precision_score | NUMERIC(5,4) | YES | Precision (0-1) |
| recall_score | NUMERIC(5,4) | YES | Recall (0-1) |
| f1_score | NUMERIC(5,4) | YES | F1 score (0-1) |
| roc_auc | NUMERIC(5,4) | YES | ROC AUC (0-1) |
| mean_absolute_error | NUMERIC(10,4) | YES | MAE |
| root_mean_squared_error | NUMERIC(10,4) | YES | RMSE |
| spatial_resolution_meters | INTEGER | YES | Model spatial resolution |
| temporal_resolution_hours | INTEGER | YES | Model temporal resolution |
| evaluation_notes | TEXT | YES | Notes |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### portfolio_risk_summaries
Aggregated risk metrics by M&A portfolio.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| summary_id | VARCHAR(255) | NO | Primary key |
| portfolio_id | VARCHAR(255) | NO | Portfolio identifier |
| portfolio_name | VARCHAR(255) | YES | Portfolio name |
| summary_date | DATE | NO | Summary date |
| total_properties | INTEGER | YES | Properties in portfolio |
| properties_at_risk | INTEGER | YES | Properties above risk threshold |
| high_risk_properties | INTEGER | YES | Score > 70 |
| moderate_risk_properties | INTEGER | YES | Score 40-70 |
| low_risk_properties | INTEGER | YES | Score < 40 |
| average_risk_score | NUMERIC(5,2) | YES | Portfolio average risk |
| total_property_value | NUMERIC(18,2) | YES | Total portfolio value |
| at_risk_property_value | NUMERIC(18,2) | YES | Value at risk |
| estimated_annual_loss | NUMERIC(15,2) | YES | Portfolio EAL |
| portfolio_risk_category | VARCHAR(50) | YES | Portfolio risk level |
| load_timestamp | TIMESTAMP | YES | ETL load timestamp |

### data_quality_metrics
Data quality tracking for flood risk data sources.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| metric_id | VARCHAR(255) | NO | Primary key |
| metric_date | DATE | NO | Metric date |
| data_source | VARCHAR(50) | NO | FEMA, NOAA, USGS, NASA |
| files_processed | INTEGER | YES | Files processed |
| files_successful | INTEGER | YES | Successful files |
| files_failed | INTEGER | YES | Failed files |
| success_rate | NUMERIC(5,2) | YES | Processing success rate |
| total_records | INTEGER | YES | Total records processed |
| records_with_errors | INTEGER | YES | Error records |
| error_rate | NUMERIC(5,2) | YES | Error rate |
| spatial_coverage_km2 | NUMERIC(15,2) | YES | Spatial coverage area |
| temporal_coverage_days | INTEGER | YES | Temporal coverage |
| data_freshness_hours | INTEGER | YES | Data freshness |
| calculation_timestamp | TIMESTAMP | YES | Calculation timestamp |
