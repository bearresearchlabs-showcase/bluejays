---
title: Flood Risk Assessment (M&A Due Diligence) — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-16
---

# Flood Risk Assessment (M&A Due Diligence) — Documentation

**Database:** db-16  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_16
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_16 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load sample data from data.sql if available.

```bash
psql -U postgres -d db_16 -f data.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

Standard PostgreSQL. No extensions required unless noted.

---

## Schema Overview

**Total tables:** 12

- `fema_flood_zones` — (see data dictionary)
- `real_estate_properties` — (see data dictionary)
- `noaa_sea_level_rise` — (see data dictionary)
- `usgs_streamflow_gauges` — (see data dictionary)
- `usgs_streamflow_observations` — (see data dictionary)
- `nasa_flood_models` — (see data dictionary)
- `flood_risk_assessments` — (see data dictionary)
- `property_flood_zone_intersections` — (see data dictionary)
- `historical_flood_events` — (see data dictionary)
- `model_performance_metrics` — (see data dictionary)
- `portfolio_risk_summaries` — (see data dictionary)
- `data_quality_metrics` — (see data dictionary)

---

## Data Dictionary

### `fema_flood_zones`

- `zone_id` VARCHAR(255) PRIMARY KEY
- `zone_code` VARCHAR(10) NOT NULL — 'A', 'AE', 'AH', 'AO', 'V', 'VE', 'X', 'D', etc.
- `zone_description` VARCHAR(255) 
- `base_flood_elevation` NUMERIC(10  — BFE in feet above sea level
- `zone_geom` geography  — Polygon geometry for flood zone boundary
- `community_id` VARCHAR(50) 
- `community_name` VARCHAR(255) 
- `state_code` VARCHAR(2) 
- `county_fips` VARCHAR(5) 
- `effective_date` DATE 
- `map_panel` VARCHAR(50) 
- `source_file` VARCHAR(500) 
- `source_crs` VARCHAR(50) 
- `target_crs` VARCHAR(50) 
- `spatial_extent_west` NUMERIC(10 
- `spatial_extent_south` NUMERIC(10 
- `spatial_extent_east` NUMERIC(10 
- `spatial_extent_north` NUMERIC(10 
- `load_timestamp` TIMESTAMP 
- `transformation_status` VARCHAR(50) 

### `real_estate_properties`

- `property_id` VARCHAR(255) PRIMARY KEY
- `property_address` VARCHAR(500) 
- `property_latitude` NUMERIC(10 NOT NULL
- `property_longitude` NUMERIC(10 NOT NULL
- `property_geom` geography  — Point geometry for property location
- `property_type` VARCHAR(100)  — 'Residential', 'Commercial', 'Industrial', 'Mixed-Use'
- `building_value` NUMERIC(15 
- `land_value` NUMERIC(15 
- `total_value` NUMERIC(15 
- `square_footage` NUMERIC(12 
- `year_built` INTEGER 
- `number_of_floors` INTEGER 
- `elevation_feet` NUMERIC(10  — Ground elevation above sea level
- `state_code` VARCHAR(2) 
- `county_fips` VARCHAR(5) 
- `city_name` VARCHAR(255) 
- `zip_code` VARCHAR(10) 
- `portfolio_id` VARCHAR(255) 
- `portfolio_name` VARCHAR(255) 
- `acquisition_date` DATE 
- `load_timestamp` TIMESTAMP 

### `noaa_sea_level_rise`

- `projection_id` VARCHAR(255) PRIMARY KEY
- `station_id` VARCHAR(50) 
- `station_name` VARCHAR(255) 
- `station_latitude` NUMERIC(10 NOT NULL
- `station_longitude` NUMERIC(10 NOT NULL
- `station_geom` geography  — Point geometry
- `projection_year` INTEGER NOT NULL
- `scenario` VARCHAR(50)  — 'Low', 'Intermediate-Low', 'Intermediate', 'Intermediate-High', 'High', 'Extreme'
- `sea_level_rise_feet` NUMERIC(8  — Projected sea level rise in feet
- `confidence_level` VARCHAR(50)  — 'Low', 'Medium', 'High'
- `high_tide_flooding_days` INTEGER  — Projected annual high tide flooding days
- `data_source` VARCHAR(100) 
- `load_timestamp` TIMESTAMP 

### `usgs_streamflow_gauges`

- `gauge_id` VARCHAR(50) PRIMARY KEY
- `gauge_name` VARCHAR(255) 
- `gauge_latitude` NUMERIC(10 NOT NULL
- `gauge_longitude` NUMERIC(10 NOT NULL
- `gauge_geom` geography  — Point geometry
- `drainage_area_sq_miles` NUMERIC(12 
- `flood_stage_feet` NUMERIC(8 
- `moderate_flood_stage_feet` NUMERIC(8 
- `major_flood_stage_feet` NUMERIC(8 
- `state_code` VARCHAR(2) 
- `county_name` VARCHAR(100) 
- `river_name` VARCHAR(255) 
- `active_status` BOOLEAN 
- `first_observation_date` DATE 
- `last_observation_date` DATE 
- `update_frequency_minutes` INTEGER 
- `load_timestamp` TIMESTAMP 

### `usgs_streamflow_observations`

- `observation_id` VARCHAR(255) PRIMARY KEY
- `gauge_id` VARCHAR(50) NOT NULL
- `observation_time` TIMESTAMP NOT NULL
- `gage_height_feet` NUMERIC(8 
- `discharge_cfs` NUMERIC(12  — Discharge in cubic feet per second
- `stage_feet` NUMERIC(8 
- `flood_category` VARCHAR(50)  — 'None', 'Action', 'Minor', 'Moderate', 'Major'
- `percentile_rank` NUMERIC(5  — Percentile relative to historical records
- `data_quality_code` VARCHAR(10) 
- `load_timestamp` TIMESTAMP 

### `nasa_flood_models`

- `model_id` VARCHAR(255) PRIMARY KEY
- `model_name` VARCHAR(100)  — 'GFMS', 'LIS', 'VIIRS', 'MODIS', 'FloodPlanet'
- `forecast_time` TIMESTAMP NOT NULL
- `grid_cell_latitude` NUMERIC(10 NOT NULL
- `grid_cell_longitude` NUMERIC(10 NOT NULL
- `grid_cell_geom` geography  — Point geometry for grid cell center
- `inundation_depth_feet` NUMERIC(8 
- `flood_probability` NUMERIC(5  — Probability percentage (0-100)
- `flood_severity` VARCHAR(50)  — 'Low', 'Moderate', 'High', 'Extreme'
- `model_resolution_meters` INTEGER 
- `spatial_extent_west` NUMERIC(10 
- `spatial_extent_south` NUMERIC(10 
- `spatial_extent_east` NUMERIC(10 
- `spatial_extent_north` NUMERIC(10 
- `source_file` VARCHAR(500) 
- `load_timestamp` TIMESTAMP 

### `flood_risk_assessments`

- `assessment_id` VARCHAR(255) PRIMARY KEY
- `property_id` VARCHAR(255) NOT NULL
- `assessment_date` DATE NOT NULL
- `assessment_type` VARCHAR(50)  — 'Current', 'Short-Term', 'Intermediate-Term', 'Long-Term'
- `time_horizon_years` INTEGER  — 5, 10, 20, 30, 50, 100
- `fema_zone_code` VARCHAR(10) 
- `fema_zone_id` VARCHAR(255) 
- `base_flood_elevation_feet` NUMERIC(10 
- `flood_zone_risk_score` NUMERIC(5  — 0-100 risk score
- `sea_level_rise_feet` NUMERIC(8 
- `sea_level_rise_scenario` VARCHAR(50) 
- `high_tide_flooding_days` INTEGER 
- `sea_level_risk_score` NUMERIC(5  — 0-100 risk score
- `nearest_gauge_id` VARCHAR(50) 
- `historical_flood_frequency` INTEGER  — Number of floods in historical record
- `flood_probability_percent` NUMERIC(5 
- `streamflow_risk_score` NUMERIC(5  — 0-100 risk score
- `nasa_model_flood_probability` NUMERIC(5 
- `nasa_model_severity` VARCHAR(50) 
- `nasa_model_risk_score` NUMERIC(5  — 0-100 risk score
- `overall_risk_score` NUMERIC(5  — Weighted composite risk score (0-100)
- `risk_category` VARCHAR(50)  — 'Low', 'Moderate', 'High', 'Extreme'
- `vulnerability_score` NUMERIC(5  — Property vulnerability to flooding
- `exposure_score` NUMERIC(5  — Exposure to flood hazards
- `estimated_damage_dollars` NUMERIC(15 
- `estimated_annual_loss` NUMERIC(15  — Expected annual loss
- `insurance_premium_estimate` NUMERIC(12 
- `assessment_methodology` VARCHAR(255) 
- `data_sources_used` VARCHAR(500) 
- `confidence_level` VARCHAR(50) 
- `assessment_notes` TEXT 
- `created_by` VARCHAR(255) 
- `load_timestamp` TIMESTAMP 

### `property_flood_zone_intersections`

- `intersection_id` VARCHAR(255) PRIMARY KEY
- `property_id` VARCHAR(255) NOT NULL
- `zone_id` VARCHAR(255) NOT NULL
- `intersection_type` VARCHAR(50)  — 'Within', 'Adjacent', 'Near'
- `distance_to_zone_feet` NUMERIC(10 
- `elevation_difference_feet` NUMERIC(10  — Property elevation - BFE
- `intersection_geom` geography  — Intersection geometry if applicable
- `load_timestamp` TIMESTAMP 

### `historical_flood_events`

- `event_id` VARCHAR(255) PRIMARY KEY
- `event_name` VARCHAR(255) 
- `event_type` VARCHAR(50)  — 'Riverine', 'Coastal', 'Flash', 'Storm Surge', 'Tidal'
- `start_date` DATE NOT NULL
- `end_date` DATE 
- `affected_area_geom` geography  — Polygon geometry of affected area
- `peak_discharge_cfs` NUMERIC(12 
- `peak_stage_feet` NUMERIC(8 
- `total_damage_dollars` NUMERIC(15 
- `fatalities` INTEGER 
- `properties_affected` INTEGER 
- `state_code` VARCHAR(2) 
- `county_fips` VARCHAR(5) 
- `data_source` VARCHAR(100) 
- `load_timestamp` TIMESTAMP 

### `model_performance_metrics`

- `metric_id` VARCHAR(255) PRIMARY KEY
- `model_name` VARCHAR(100) NOT NULL
- `evaluation_date` DATE NOT NULL
- `evaluation_period_start` DATE 
- `evaluation_period_end` DATE 
- `total_predictions` INTEGER 
- `true_positives` INTEGER 
- `true_negatives` INTEGER 
- `false_positives` INTEGER 
- `false_negatives` INTEGER 
- `accuracy` NUMERIC(5  — 0-1 accuracy score
- `precision_score` NUMERIC(5 
- `recall_score` NUMERIC(5 
- `f1_score` NUMERIC(5 
- `roc_auc` NUMERIC(5 
- `mean_absolute_error` NUMERIC(10 
- `root_mean_squared_error` NUMERIC(10 
- `spatial_resolution_meters` INTEGER 
- `temporal_resolution_hours` INTEGER 
- `evaluation_notes` TEXT 
- `load_timestamp` TIMESTAMP 

### `portfolio_risk_summaries`

- `summary_id` VARCHAR(255) PRIMARY KEY
- `portfolio_id` VARCHAR(255) NOT NULL
- `portfolio_name` VARCHAR(255) 
- `summary_date` DATE NOT NULL
- `total_properties` INTEGER 
- `properties_at_risk` INTEGER  — Properties with risk score > threshold
- `high_risk_properties` INTEGER  — Risk score > 70
- `moderate_risk_properties` INTEGER  — Risk score 40-70
- `low_risk_properties` INTEGER  — Risk score < 40
- `average_risk_score` NUMERIC(5 
- `total_property_value` NUMERIC(18 
- `at_risk_property_value` NUMERIC(18 
- `estimated_annual_loss` NUMERIC(15 
- `portfolio_risk_category` VARCHAR(50) 
- `load_timestamp` TIMESTAMP 

### `data_quality_metrics`

- `metric_id` VARCHAR(255) PRIMARY KEY
- `metric_date` DATE NOT NULL
- `data_source` VARCHAR(50) NOT NULL — 'FEMA', 'NOAA', 'USGS', 'NASA'
- `files_processed` INTEGER 
- `files_successful` INTEGER 
- `files_failed` INTEGER 
- `success_rate` NUMERIC(5 
- `total_records` INTEGER 
- `records_with_errors` INTEGER 
- `error_rate` NUMERIC(5 
- `spatial_coverage_km2` NUMERIC(15 
- `temporal_coverage_days` INTEGER 
- `data_freshness_hours` INTEGER 
- `calculation_timestamp` TIMESTAMP 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 
- `CREATE` INDEX 

---

*Generated by documentation workflow. MDX-compatible markdown.*
