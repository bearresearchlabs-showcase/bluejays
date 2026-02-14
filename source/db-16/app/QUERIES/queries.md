# Database 16 - Flood Risk Assessment - Extremely Complex SQL Queries

# Database Schema: DB16

**Description:** Flood Risk Assessment Database for M&A Due Diligence
**Created:** 2026-02-04

## Overview

This database contains flood risk assessment data for real estate M&A due diligence, integrating federal data sources including FEMA National Flood Hazard Layer (NFHL), NOAA sea level rise projections, USGS streamflow gauges and observations, and NASA flood model outputs. The database supports multi-factor risk scoring, spatial analysis, temporal projections, portfolio-level aggregation, and financial impact modeling for properties under acquisition consideration.

## Tables

### `fema_flood_zones`
FEMA NFHL flood zone designations and Base Flood Elevations with spatial boundaries

### `noaa_sea_level_rise`
NOAA sea level rise projections and high tide flooding data by coastal station

### `usgs_streamflow_gauges`
USGS streamflow gauge locations and flood stage thresholds

### `usgs_streamflow_observations`
Real-time and historical streamflow measurements from USGS gauges

### `nasa_flood_models`
NASA flood model predictions (GFMS, VIIRS, MODIS) and inundation extents

### `real_estate_properties`
Properties under M&A evaluation with location, value, and elevation data

### `flood_risk_assessments`
Composite multi-factor flood risk scores per property across time horizons

### `property_flood_zone_intersections`
Spatial join results linking properties to intersecting flood zones

### `portfolio_risk_summaries`
Aggregated portfolio-level risk metrics for M&A decision-making

### `historical_flood_events`
Historical flood records with damage estimates and affected areas

### `model_performance_metrics`
Model accuracy tracking for flood prediction validation

### `data_quality_metrics`
Data pipeline quality monitoring and freshness tracking

---

This file contains 30 extremely complex SQL queries focused on flood risk assessment for M&A due diligence. All queries are designed to work across PostgreSQL (with PostGIS).

## Query 1: Pre-Acquisition Multi-Factor Flood Risk Assessment with Spatial Analysis and Temporal Projections

**Description:** Enterprise-level flood risk assessment combining FEMA flood zones, NOAA sea level rise projections, USGS streamflow data, and NASA flood models. Performs spatial joins, temporal analysis, risk scoring, and financial impact estimation.

**Use Case:** M&A Due Diligence - Pre-Acquisition Property-Level Flood Risk Assessment for Acquisition Target Evaluation

**Business Value:** Comprehensive pre-acquisition flood risk assessment report for individual properties showing current risk, short-term, intermediate-term, and long-term projections. Enables M&A teams to make informed go/no-go acquisition decisions.

**Purpose:** Quantifies flood risk across multiple time horizons and data sources for properties under consideration for acquisition, enabling data-driven M&A decision-making.

**Complexity:** Deep nested CTEs (8+ levels), spatial operations (ST_WITHIN, ST_DISTANCE, ST_INTERSECTS), complex aggregations, window functions with multiple frame clauses, percentile calculations, temporal projections, multi-factor risk scoring, financial impact modeling

**Expected Output:** Property-level flood risk scores with FEMA, sea level rise, streamflow, and NASA model components, plus composite risk category and financial impact estimates.

```sql
WITH property_location_analysis AS (
    -- First CTE: Analyze property locations and spatial context
    SELECT
        rep.property_id,
        rep.property_address,
        rep.property_latitude,
        rep.property_longitude,
        rep.property_geom,
        rep.property_type,
        rep.building_value,
        rep.land_value,
        rep.total_value,
        rep.square_footage,
        rep.year_built,
        rep.number_of_floors,
        rep.elevation_feet,
        rep.state_code,
        rep.county_fips,
        rep.city_name,
        rep.zip_code,
        rep.portfolio_id,
        rep.portfolio_name,
        rep.acquisition_date,
        -- Calculate property age
        EXTRACT(YEAR FROM CURRENT_DATE) - rep.year_built AS property_age_years
    FROM real_estate_properties rep
    WHERE rep.property_geom IS NOT NULL
),
fema_flood_zone_analysis AS (
    -- Second CTE: Identify FEMA flood zones intersecting or near properties
    SELECT
        pla.property_id,
        pla.property_address,
        pla.property_latitude,
        pla.property_longitude,
        pla.property_geom,
        pla.property_type,
        pla.total_value,
        pla.elevation_feet,
        pla.state_code,
        pla.county_fips,
        pla.portfolio_id,
        pla.portfolio_name,
        pla.property_age_years,
        ffz.zone_id,
        ffz.zone_code,
        ffz.zone_description,
        ffz.base_flood_elevation,
        ffz.zone_geom,
        ffz.community_name,
        ffz.effective_date,
        -- Spatial distance calculation
        CASE
            WHEN ffz.zone_geom IS NOT NULL AND pla.property_geom IS NOT NULL THEN
                ST_DISTANCE(ffz.zone_geom, pla.property_geom)
            ELSE NULL
        END AS distance_to_zone_meters,
        -- Check if property is within flood zone
        CASE
            WHEN ffz.zone_geom IS NOT NULL AND pla.property_geom IS NOT NULL THEN
                CASE
                    WHEN ST_DWithin(pla.property_geom, ffz.zone_geom, 0) THEN TRUE
                    ELSE FALSE
                END
            ELSE NULL
        END AS is_within_flood_zone,
        -- Elevation difference (property elevation - BFE)
        CASE
            WHEN ffz.base_flood_elevation IS NOT NULL AND pla.elevation_feet IS NOT NULL THEN
                pla.elevation_feet - ffz.base_flood_elevation
            ELSE NULL
        END AS elevation_above_bfe_feet
    FROM property_location_analysis pla
    LEFT JOIN fema_flood_zones ffz ON (
        ffz.zone_geom IS NOT NULL
        AND pla.property_geom IS NOT NULL
        AND ST_DISTANCE(ffz.zone_geom, pla.property_geom) < 5000  -- Within 5km
    )
),
fema_risk_scoring AS (
    -- Third CTE: Calculate FEMA flood zone risk scores
    SELECT
        ffza.property_id,
        ffza.property_address,
        ffza.property_latitude,
        ffza.property_longitude,
        ffza.property_geom,
        ffza.property_type,
        ffza.total_value,
        ffza.elevation_feet,
        ffza.state_code,
        ffza.county_fips,
        ffza.portfolio_id,
        ffza.portfolio_name,
        ffza.zone_id,
        ffza.zone_code,
        ffza.zone_description,
        ffza.base_flood_elevation,
        ffza.distance_to_zone_meters,
        ffza.is_within_flood_zone,
        ffza.elevation_above_bfe_feet,
        -- FEMA flood zone risk score (0-100)
        CASE
            WHEN ffza.is_within_flood_zone = TRUE THEN
                CASE
                    WHEN ffza.zone_code IN ('V', 'VE') THEN 95  -- Velocity zones (highest risk)
                    WHEN ffza.zone_code IN ('A', 'AE') THEN
                        CASE
                            WHEN ffza.elevation_above_bfe_feet IS NOT NULL THEN
                                CASE
                                    WHEN ffza.elevation_above_bfe_feet < 0 THEN 90  -- Below BFE
                                    WHEN ffza.elevation_above_bfe_feet < 2 THEN 75  -- 0-2 feet above BFE
                                    WHEN ffza.elevation_above_bfe_feet < 5 THEN 60  -- 2-5 feet above BFE
                                    ELSE 45  -- More than 5 feet above BFE
                                END
                            ELSE 80  -- In A/AE zone but BFE unknown
                        END
                    WHEN ffza.zone_code IN ('AH', 'AO') THEN 70  -- Shallow flooding zones
                    WHEN ffza.zone_code = 'D' THEN 50  -- Unstudied areas
                    WHEN ffza.zone_code IN ('X', 'X500') THEN 30  -- Low to moderate risk
                    ELSE 40
                END
            WHEN ffza.distance_to_zone_meters IS NOT NULL THEN
                CASE
                    WHEN ffza.distance_to_zone_meters < 100 THEN 60  -- Very close to high-risk zone
                    WHEN ffza.distance_to_zone_meters < 500 THEN 40  -- Close to high-risk zone
                    WHEN ffza.distance_to_zone_meters < 1000 THEN 25  -- Near high-risk zone
                    ELSE 10  -- Far from high-risk zones
                END
            ELSE 5  -- No nearby flood zones
        END AS fema_risk_score
    FROM fema_flood_zone_analysis ffza
),
noaa_sea_level_rise_analysis AS (
    -- Fourth CTE: Analyze NOAA sea level rise projections for coastal properties
    SELECT
        frs.property_id,
        frs.property_address,
        frs.property_latitude,
        frs.property_longitude,
        frs.property_geom,
        frs.property_type,
        frs.total_value,
        frs.elevation_feet,
        frs.state_code,
        frs.county_fips,
        frs.portfolio_id,
        frs.portfolio_name,
        frs.zone_code,
        frs.fema_risk_score,
        -- Find nearest NOAA sea level rise station
        (
            SELECT nslr.station_id
            FROM noaa_sea_level_rise nslr
            WHERE nslr.station_geom IS NOT NULL
                AND frs.property_geom IS NOT NULL
            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)
            LIMIT 1
        ) AS nearest_station_id,
        -- Get sea level rise projections for different time horizons
        (
            SELECT nslr.sea_level_rise_feet
            FROM noaa_sea_level_rise nslr
            WHERE nslr.station_geom IS NOT NULL
                AND frs.property_geom IS NOT NULL
                AND nslr.projection_year = EXTRACT(YEAR FROM CURRENT_DATE) + 10
                AND nslr.scenario = 'Intermediate'
            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)
            LIMIT 1
        ) AS slr_10_years_feet,
        (
            SELECT nslr.sea_level_rise_feet
            FROM noaa_sea_level_rise nslr
            WHERE nslr.station_geom IS NOT NULL
                AND frs.property_geom IS NOT NULL
                AND nslr.projection_year = EXTRACT(YEAR FROM CURRENT_DATE) + 30
                AND nslr.scenario = 'Intermediate'
            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)
            LIMIT 1
        ) AS slr_30_years_feet,
        (
            SELECT nslr.sea_level_rise_feet
            FROM noaa_sea_level_rise nslr
            WHERE nslr.station_geom IS NOT NULL
                AND frs.property_geom IS NOT NULL
                AND nslr.projection_year = EXTRACT(YEAR FROM CURRENT_DATE) + 100
                AND nslr.scenario = 'Intermediate'
            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)
            LIMIT 1
        ) AS slr_100_years_feet,
        -- Get high tide flooding projections
        (
            SELECT nslr.high_tide_flooding_days
            FROM noaa_sea_level_rise nslr
            WHERE nslr.station_geom IS NOT NULL
                AND frs.property_geom IS NOT NULL
                AND nslr.projection_year = EXTRACT(YEAR FROM CURRENT_DATE) + 30
                AND nslr.scenario = 'Intermediate'
            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)
            LIMIT 1
        ) AS htf_30_years_days
    FROM fema_risk_scoring frs
),
sea_level_rise_risk_scoring AS (
    -- Fifth CTE: Calculate sea level rise risk scores
    SELECT
        nsla.property_id,
        nsla.property_address,
        nsla.property_latitude,
        nsla.property_longitude,
        nsla.property_geom,
        nsla.property_type,
        nsla.total_value,
        nsla.elevation_feet,
        nsla.state_code,
        nsla.county_fips,
        nsla.portfolio_id,
        nsla.portfolio_name,
        nsla.zone_code,
        nsla.fema_risk_score,
        nsla.nearest_station_id,
        nsla.slr_10_years_feet,
        nsla.slr_30_years_feet,
        nsla.slr_100_years_feet,
        nsla.htf_30_years_days,
        -- Sea level rise risk score (0-100)
        CASE
            WHEN nsla.elevation_feet IS NOT NULL AND nsla.slr_100_years_feet IS NOT NULL THEN
                CASE
                    WHEN nsla.elevation_feet < nsla.slr_100_years_feet THEN 95  -- Will be below sea level
                    WHEN nsla.elevation_feet < nsla.slr_100_years_feet + 2 THEN 85  -- Very close to sea level
                    WHEN nsla.elevation_feet < nsla.slr_100_years_feet + 5 THEN 70  -- Close to sea level
                    WHEN nsla.elevation_feet < nsla.slr_100_years_feet + 10 THEN 50  -- Moderate risk
                    ELSE 20  -- Low risk
                END
            WHEN nsla.htf_30_years_days IS NOT NULL THEN
                CASE
                    WHEN nsla.htf_30_years_days >= 180 THEN 80  -- More than 6 months of flooding
                    WHEN nsla.htf_30_years_days >= 90 THEN 60  -- 3-6 months
                    WHEN nsla.htf_30_years_days >= 30 THEN 40  -- 1-3 months
                    WHEN nsla.htf_30_years_days > 0 THEN 25  -- Some flooding
                    ELSE 10  -- No projected flooding
                END
            ELSE 5  -- No sea level rise data
        END AS sea_level_rise_risk_score
    FROM noaa_sea_level_rise_analysis nsla
),
usgs_streamflow_analysis AS (
    -- Sixth CTE: Analyze USGS streamflow data for riverine flood risk
    SELECT
        slrs.property_id,
        slrs.property_address,
        slrs.property_latitude,
        slrs.property_longitude,
        slrs.property_geom,
        slrs.property_type,
        slrs.total_value,
        slrs.elevation_feet,
        slrs.state_code,
        slrs.county_fips,
        slrs.portfolio_id,
        slrs.portfolio_name,
        slrs.zone_code,
        slrs.fema_risk_score,
        slrs.sea_level_rise_risk_score,
        -- Find nearest USGS streamflow gauge
        (
            SELECT usg.gauge_id
            FROM usgs_streamflow_gauges usg
            WHERE usg.gauge_geom IS NOT NULL
                AND usg.active_status = TRUE
                AND slrs.property_geom IS NOT NULL
            ORDER BY ST_DISTANCE(usg.gauge_geom, slrs.property_geom)
            LIMIT 1
        ) AS nearest_gauge_id,
        -- Get flood stage information
        (
            SELECT usg.flood_stage_feet
            FROM usgs_streamflow_gauges usg
            WHERE usg.gauge_geom IS NOT NULL
                AND usg.active_status = TRUE
                AND slrs.property_geom IS NOT NULL
            ORDER BY ST_DISTANCE(usg.gauge_geom, slrs.property_geom)
            LIMIT 1
        ) AS flood_stage_feet,
        -- Get historical flood frequency for nearest gauge
        (
            SELECT COUNT(*)
            FROM usgs_streamflow_observations uso
            WHERE uso.gauge_id = (
                SELECT usg2.gauge_id
                FROM usgs_streamflow_gauges usg2
                WHERE usg2.gauge_geom IS NOT NULL
                    AND usg2.active_status = TRUE
                    AND slrs.property_geom IS NOT NULL
                ORDER BY ST_DISTANCE(usg2.gauge_geom, slrs.property_geom)
                LIMIT 1
            )
            AND uso.flood_category IN ('Minor', 'Moderate', 'Major')
            AND uso.observation_time >= CURRENT_DATE - INTERVAL '10 years'
        ) AS historical_flood_count_10_years
    FROM sea_level_rise_risk_scoring slrs
),
streamflow_risk_scoring AS (
    -- Seventh CTE: Calculate streamflow flood risk scores
    SELECT
        usa.property_id,
        usa.property_address,
        usa.property_latitude,
        usa.property_longitude,
        usa.property_geom,
        usa.property_type,
        usa.total_value,
        usa.elevation_feet,
        usa.state_code,
        usa.county_fips,
        usa.portfolio_id,
        usa.portfolio_name,
        usa.zone_code,
        usa.fema_risk_score,
        usa.sea_level_rise_risk_score,
        usa.nearest_gauge_id,
        usa.flood_stage_feet,
        usa.historical_flood_count_10_years,
        -- Streamflow flood risk score (0-100)
        CASE
            WHEN usa.historical_flood_count_10_years IS NOT NULL THEN
                CASE
                    WHEN usa.historical_flood_count_10_years >= 20 THEN 90  -- Frequent flooding
                    WHEN usa.historical_flood_count_10_years >= 10 THEN 75  -- Regular flooding
                    WHEN usa.historical_flood_count_10_years >= 5 THEN 60  -- Occasional flooding
                    WHEN usa.historical_flood_count_10_years >= 1 THEN 40  -- Rare flooding
                    ELSE 15  -- No historical flooding
                END
            WHEN usa.flood_stage_feet IS NOT NULL AND usa.elevation_feet IS NOT NULL THEN
                CASE
                    WHEN usa.elevation_feet < usa.flood_stage_feet THEN 70  -- Below flood stage
                    WHEN usa.elevation_feet < usa.flood_stage_feet + 5 THEN 50  -- Close to flood stage
                    ELSE 20  -- Above flood stage
                END
            ELSE 10  -- No streamflow data
        END AS streamflow_risk_score
    FROM usgs_streamflow_analysis usa
),
nasa_flood_model_analysis AS (
    -- Eighth CTE: Analyze NASA flood model predictions
    SELECT
        srs.property_id,
        srs.property_address,
        srs.property_latitude,
        srs.property_longitude,
        srs.property_geom,
        srs.property_type,
        srs.total_value,
        srs.elevation_feet,
        srs.state_code,
        srs.county_fips,
        srs.portfolio_id,
        srs.portfolio_name,
        srs.zone_code,
        srs.fema_risk_score,
        srs.sea_level_rise_risk_score,
        srs.streamflow_risk_score,
        -- Get NASA flood model predictions
        (
            SELECT AVG(nfm.flood_probability)
            FROM nasa_flood_models nfm
            WHERE nfm.grid_cell_geom IS NOT NULL
                AND srs.property_geom IS NOT NULL
                AND nfm.forecast_time >= CURRENT_TIMESTAMP - INTERVAL '30 days'
                AND ST_DISTANCE(nfm.grid_cell_geom, srs.property_geom) < 10000  -- Within 10km
        ) AS nasa_flood_probability_avg,
        (
            SELECT MAX(nfm.flood_probability)
            FROM nasa_flood_models nfm
            WHERE nfm.grid_cell_geom IS NOT NULL
                AND srs.property_geom IS NOT NULL
                AND nfm.forecast_time >= CURRENT_TIMESTAMP - INTERVAL '30 days'
                AND ST_DISTANCE(nfm.grid_cell_geom, srs.property_geom) < 10000
        ) AS nasa_flood_probability_max,
        (
            SELECT AVG(nfm.inundation_depth_feet)
            FROM nasa_flood_models nfm
            WHERE nfm.grid_cell_geom IS NOT NULL
                AND srs.property_geom IS NOT NULL
                AND nfm.forecast_time >= CURRENT_TIMESTAMP - INTERVAL '30 days'
                AND ST_DISTANCE(nfm.grid_cell_geom, srs.property_geom) < 10000
                AND nfm.inundation_depth_feet > 0
        ) AS nasa_inundation_depth_avg
    FROM streamflow_risk_scoring srs
),
nasa_risk_scoring AS (
    -- Ninth CTE: Calculate NASA flood model risk scores
    SELECT
        nfma.property_id,
        nfma.property_address,
        nfma.property_latitude,
        nfma.property_longitude,
        nfma.property_type,
        nfma.total_value,
        nfma.elevation_feet,
        nfma.state_code,
        nfma.county_fips,
        nfma.portfolio_id,
        nfma.portfolio_name,
        nfma.zone_code,
        nfma.fema_risk_score,
        nfma.sea_level_rise_risk_score,
        nfma.streamflow_risk_score,
        nfma.nasa_flood_probability_avg,
        nfma.nasa_flood_probability_max,
        nfma.nasa_inundation_depth_avg,
        -- NASA flood model risk score (0-100)
        CASE
            WHEN nfma.nasa_flood_probability_max IS NOT NULL THEN
                CASE
                    WHEN nfma.nasa_flood_probability_max >= 80 THEN 85  -- Very high probability
                    WHEN nfma.nasa_flood_probability_max >= 60 THEN 70  -- High probability
                    WHEN nfma.nasa_flood_probability_max >= 40 THEN 55  -- Moderate probability
                    WHEN nfma.nasa_flood_probability_max >= 20 THEN 35  -- Low probability
                    ELSE 15  -- Very low probability
                END
            WHEN nfma.nasa_inundation_depth_avg IS NOT NULL THEN
                CASE
                    WHEN nfma.nasa_inundation_depth_avg >= 5 THEN 80  -- Deep inundation
                    WHEN nfma.nasa_inundation_depth_avg >= 2 THEN 60  -- Moderate inundation
                    WHEN nfma.nasa_inundation_depth_avg > 0 THEN 40  -- Shallow inundation
                    ELSE 10  -- No inundation
                END
            ELSE 5  -- No NASA model data
        END AS nasa_model_risk_score
    FROM nasa_flood_model_analysis nfma
),
composite_risk_calculation AS (
    -- Tenth CTE: Calculate composite risk scores and financial impacts
    SELECT
        nrs.property_id,
        nrs.property_address,
        nrs.property_latitude,
        nrs.property_longitude,
        nrs.property_type,
        nrs.total_value,
        nrs.elevation_feet,
        nrs.state_code,
        nrs.county_fips,
        nrs.portfolio_id,
        nrs.portfolio_name,
        nrs.zone_code,
        nrs.fema_risk_score,
        nrs.sea_level_rise_risk_score,
        nrs.streamflow_risk_score,
        nrs.nasa_model_risk_score,
        -- Weighted composite risk score (FEMA 40%, Sea Level Rise 25%, Streamflow 20%, NASA 15%)
        ROUND(
            COALESCE(nrs.fema_risk_score, 0) * 0.40 +
            COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
            COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
            COALESCE(nrs.nasa_model_risk_score, 0) * 0.15,
            2
        ) AS overall_risk_score,
        -- Risk category
        CASE
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 70 THEN 'Extreme'
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 50 THEN 'High'
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 30 THEN 'Moderate'
            ELSE 'Low'
        END AS risk_category,
        -- Estimated damage (percentage of property value based on risk)
        CASE
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 70 THEN nrs.total_value * 0.50  -- 50% damage estimate
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 50 THEN nrs.total_value * 0.30  -- 30% damage estimate
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 30 THEN nrs.total_value * 0.15  -- 15% damage estimate
            ELSE nrs.total_value * 0.05  -- 5% damage estimate
        END AS estimated_damage_dollars,
        -- Estimated annual loss (EAL)
        CASE
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 70 THEN nrs.total_value * 0.10  -- 10% annual loss probability
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 50 THEN nrs.total_value * 0.05  -- 5% annual loss probability
            WHEN (
                COALESCE(nrs.fema_risk_score, 0) * 0.40 +
                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +
                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +
                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15
            ) >= 30 THEN nrs.total_value * 0.02  -- 2% annual loss probability
            ELSE nrs.total_value * 0.005  -- 0.5% annual loss probability
        END AS estimated_annual_loss
    FROM nasa_risk_scoring nrs
)
SELECT
    property_id,
    property_address,
    ROUND(CAST(property_latitude AS NUMERIC), 7) AS property_latitude,
    ROUND(CAST(property_longitude AS NUMERIC), 7) AS property_longitude,
    property_type,
    total_value,
    elevation_feet,
    state_code,
    county_fips,
    portfolio_id,
    portfolio_name,
    zone_code,
    ROUND(CAST(fema_risk_score AS NUMERIC), 2) AS fema_risk_score,
    ROUND(CAST(sea_level_rise_risk_score AS NUMERIC), 2) AS sea_level_rise_risk_score,
    ROUND(CAST(streamflow_risk_score AS NUMERIC), 2) AS streamflow_risk_score,
    ROUND(CAST(nasa_model_risk_score AS NUMERIC), 2) AS nasa_model_risk_score,
    overall_risk_score,
    risk_category,
    ROUND(CAST(estimated_damage_dollars AS NUMERIC), 2) AS estimated_damage_dollars,
    ROUND(CAST(estimated_annual_loss AS NUMERIC), 2) AS estimated_annual_loss
FROM composite_risk_calculation
ORDER BY overall_risk_score DESC, total_value DESC
LIMIT 10000;
```

**Expected Output:** Comprehensive pre-acquisition flood risk assessment report for properties under consideration for acquisition showing multi-factor risk scores, risk categories, and financial impact estimates to inform M&A decision-making.

---

## Query 2: Acquisition Target Portfolio Risk Analysis with Geographic Clustering and Risk Hotspot Detection

**Use Case:** **M&A Due Diligence - Acquisition Target Portfolio-Wide Flood Risk Analysis with Geographic Risk Clustering for M&A Deal Evaluation****

**Description:** Enterprise-level portfolio risk aggregation combining property-level assessments with geographic clustering, spatial hotspot detection, risk concentration analysis, and portfolio diversification metrics. Performs multi-level aggregations, spatial clustering algorithms, and risk concentration calculations. Designed specifically for M&A teams to assess overall flood risk exposure of acquisition target portfolios.

**Business Value:** Comprehensive acquisition target portfolio flood risk summary showing aggregated risk metrics, geographic risk clusters, risk concentration by region, and portfolio diversification scores. Enables M&A teams to identify high-risk geographic concentrations in acquisition targets, assess overall deal risk, and negotiate acquisition pricing based on portfolio-level flood risk exposure. Critical for evaluating large portfolio acquisitions where geographic risk concentration can significantly impact deal value.

**Purpose:** Provides acquisition target portfolio-level risk insights enabling data-driven M&A decision-making, deal risk assessment, and acquisition pricing negotiations based on portfolio flood risk exposure.

**Complexity:** Deep nested CTEs (9+ levels), spatial clustering algorithms (K-means-like), geographic aggregation, risk concentration metrics, window functions with multiple frame clauses, percentile calculations, spatial hotspot detection, portfolio diversification scoring

```sql
WITH portfolio_property_risk_base AS (
    -- First CTE: Base property risk data with assessments
    SELECT
        rep.property_id,
        rep.property_address,
        rep.property_latitude,
        rep.property_longitude,
        rep.property_geom,
        rep.property_type,
        rep.total_value,
        rep.building_value,
        rep.land_value,
        rep.square_footage,
        rep.elevation_feet,
        rep.state_code,
        rep.county_fips,
        rep.city_name,
        rep.zip_code,
        rep.portfolio_id,
        rep.portfolio_name,
        fra.assessment_id,
        fra.assessment_date,
        fra.overall_risk_score,
        fra.risk_category,
        fra.estimated_damage_dollars,
        fra.estimated_annual_loss,
        fra.fema_zone_code,
        fra.sea_level_risk_score,
        fra.streamflow_risk_score,
        fra.nasa_model_risk_score
    FROM real_estate_properties rep
    LEFT JOIN flood_risk_assessments fra ON rep.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = rep.property_id
        )
    WHERE rep.property_geom IS NOT NULL
),
portfolio_aggregation_base AS (
    -- Second CTE: Portfolio-level aggregations
    SELECT
        pprb.portfolio_id,
        pprb.portfolio_name,
        COUNT(DISTINCT pprb.property_id) AS total_properties,
        COUNT(DISTINCT CASE WHEN pprb.overall_risk_score IS NOT NULL THEN pprb.property_id END) AS properties_with_assessment,
        SUM(pprb.total_value) AS total_portfolio_value,
        AVG(pprb.overall_risk_score) AS avg_risk_score,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pprb.overall_risk_score) AS median_risk_score,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY pprb.overall_risk_score) AS q1_risk_score,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY pprb.overall_risk_score) AS q3_risk_score,
        STDDEV(pprb.overall_risk_score) AS stddev_risk_score,
        SUM(pprb.estimated_damage_dollars) AS total_estimated_damage,
        SUM(pprb.estimated_annual_loss) AS total_estimated_annual_loss,
        COUNT(DISTINCT CASE WHEN pprb.risk_category = 'Extreme' THEN pprb.property_id END) AS extreme_risk_properties,
        COUNT(DISTINCT CASE WHEN pprb.risk_category = 'High' THEN pprb.property_id END) AS high_risk_properties,
        COUNT(DISTINCT CASE WHEN pprb.risk_category = 'Moderate' THEN pprb.property_id END) AS moderate_risk_properties,
        COUNT(DISTINCT CASE WHEN pprb.risk_category = 'Low' THEN pprb.property_id END) AS low_risk_properties,
        SUM(CASE WHEN pprb.risk_category = 'Extreme' THEN pprb.total_value ELSE 0 END) AS extreme_risk_value,
        SUM(CASE WHEN pprb.risk_category = 'High' THEN pprb.total_value ELSE 0 END) AS high_risk_value,
        SUM(CASE WHEN pprb.risk_category = 'Moderate' THEN pprb.total_value ELSE 0 END) AS moderate_risk_value,
        SUM(CASE WHEN pprb.risk_category = 'Low' THEN pprb.total_value ELSE 0 END) AS low_risk_value
    FROM portfolio_property_risk_base pprb
    GROUP BY pprb.portfolio_id, pprb.portfolio_name
),
geographic_clustering AS (
    -- Third CTE: Geographic clustering of properties by risk
    SELECT
        pprb.portfolio_id,
        pprb.portfolio_name,
        pprb.property_id,
        pprb.property_latitude,
        pprb.property_longitude,
        pprb.property_geom,
        pprb.overall_risk_score,
        pprb.risk_category,
        pprb.total_value,
        pprb.state_code,
        pprb.county_fips,
        pprb.city_name,
        -- Cluster ID based on spatial proximity and risk similarity
        ROW_NUMBER() OVER (
            PARTITION BY pprb.portfolio_id
            ORDER BY pprb.property_latitude, pprb.property_longitude
        ) AS spatial_cluster_id,
        -- Count nearby high-risk properties within 10km
        (
            SELECT COUNT(*)
            FROM portfolio_property_risk_base pprb2
            WHERE pprb2.portfolio_id = pprb.portfolio_id
                AND pprb2.property_id != pprb.property_id
                AND pprb2.property_geom IS NOT NULL
                AND pprb.property_geom IS NOT NULL
                AND ST_DISTANCE(pprb.property_geom, pprb2.property_geom) < 10000
                AND pprb2.overall_risk_score >= 70
        ) AS nearby_high_risk_count,
        -- Average risk score of nearby properties
        (
            SELECT AVG(pprb2.overall_risk_score)
            FROM portfolio_property_risk_base pprb2
            WHERE pprb2.portfolio_id = pprb.portfolio_id
                AND pprb2.property_id != pprb.property_id
                AND pprb2.property_geom IS NOT NULL
                AND pprb.property_geom IS NOT NULL
                AND ST_DISTANCE(pprb.property_geom, pprb2.property_geom) < 10000
        ) AS nearby_avg_risk_score
    FROM portfolio_property_risk_base pprb
),
risk_hotspot_detection AS (
    -- Fourth CTE: Identify risk hotspots using spatial clustering
    SELECT
        gc.portfolio_id,
        gc.portfolio_name,
        gc.property_id,
        gc.property_latitude,
        gc.property_longitude,
        gc.property_geom,
        gc.overall_risk_score,
        gc.risk_category,
        gc.total_value,
        gc.state_code,
        gc.county_fips,
        gc.city_name,
        gc.nearby_high_risk_count,
        gc.nearby_avg_risk_score,
        -- Hotspot score (combination of property risk and nearby risk)
        CASE
            WHEN gc.overall_risk_score IS NOT NULL AND gc.nearby_avg_risk_score IS NOT NULL THEN
                (gc.overall_risk_score * 0.6 + gc.nearby_avg_risk_score * 0.4)
            WHEN gc.overall_risk_score IS NOT NULL THEN gc.overall_risk_score
            ELSE 0
        END AS hotspot_score,
        -- Hotspot classification
        CASE
            WHEN gc.nearby_high_risk_count >= 5 AND gc.overall_risk_score >= 70 THEN 'Critical Hotspot'
            WHEN gc.nearby_high_risk_count >= 3 AND gc.overall_risk_score >= 60 THEN 'High Hotspot'
            WHEN gc.nearby_high_risk_count >= 1 AND gc.overall_risk_score >= 50 THEN 'Moderate Hotspot'
            ELSE 'No Hotspot'
        END AS hotspot_classification
    FROM geographic_clustering gc
),
geographic_risk_concentration AS (
    -- Fifth CTE: Analyze risk concentration by geographic region
    SELECT
        rhd.portfolio_id,
        rhd.portfolio_name,
        rhd.state_code,
        rhd.county_fips,
        rhd.city_name,
        COUNT(DISTINCT rhd.property_id) AS properties_in_region,
        SUM(rhd.total_value) AS total_region_value,
        AVG(rhd.overall_risk_score) AS avg_region_risk_score,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rhd.overall_risk_score) AS median_region_risk_score,
        COUNT(DISTINCT CASE WHEN rhd.risk_category = 'Extreme' THEN rhd.property_id END) AS extreme_risk_in_region,
        COUNT(DISTINCT CASE WHEN rhd.risk_category = 'High' THEN rhd.property_id END) AS high_risk_in_region,
        SUM(CASE WHEN rhd.risk_category IN ('Extreme', 'High') THEN rhd.total_value ELSE 0 END) AS high_risk_region_value,
        COUNT(DISTINCT CASE WHEN rhd.hotspot_classification != 'No Hotspot' THEN rhd.property_id END) AS hotspot_properties_count,
        -- Risk concentration ratio (high-risk value / total value)
        CASE
            WHEN SUM(rhd.total_value) > 0 THEN
                SUM(CASE WHEN rhd.risk_category IN ('Extreme', 'High') THEN rhd.total_value ELSE 0 END) / SUM(rhd.total_value) * 100
            ELSE 0
        END AS risk_concentration_percentage
    FROM risk_hotspot_detection rhd
    GROUP BY rhd.portfolio_id, rhd.portfolio_name, rhd.state_code, rhd.county_fips, rhd.city_name
),
portfolio_diversification_analysis AS (
    -- Sixth CTE: Calculate portfolio diversification metrics
    SELECT
        pab.portfolio_id,
        pab.portfolio_name,
        pab.total_properties,
        pab.total_portfolio_value,
        pab.avg_risk_score,
        pab.median_risk_score,
        pab.total_estimated_damage,
        pab.total_estimated_annual_loss,
        pab.extreme_risk_properties,
        pab.high_risk_properties,
        pab.moderate_risk_properties,
        pab.low_risk_properties,
        pab.extreme_risk_value,
        pab.high_risk_value,
        pab.moderate_risk_value,
        pab.low_risk_value,
        -- Geographic diversification (number of unique regions)
        (
            SELECT COUNT(DISTINCT CONCAT(pprb.state_code, '-', pprb.county_fips))
            FROM portfolio_property_risk_base pprb
            WHERE pprb.portfolio_id = pab.portfolio_id
        ) AS unique_regions_count,
        -- Risk diversification score (lower concentration = better diversification)
        CASE
            WHEN pab.total_portfolio_value > 0 THEN
                100 - (
                    (pab.extreme_risk_value + pab.high_risk_value) / pab.total_portfolio_value * 100
                )
            ELSE 0
        END AS risk_diversification_score,
        -- Portfolio risk category
        CASE
            WHEN (pab.extreme_risk_value + pab.high_risk_value) / NULLIF(pab.total_portfolio_value, 0) >= 0.5 THEN 'High Concentration'
            WHEN (pab.extreme_risk_value + pab.high_risk_value) / NULLIF(pab.total_portfolio_value, 0) >= 0.3 THEN 'Moderate Concentration'
            WHEN (pab.extreme_risk_value + pab.high_risk_value) / NULLIF(pab.total_portfolio_value, 0) >= 0.1 THEN 'Low Concentration'
            ELSE 'Well Diversified'
        END AS portfolio_risk_concentration_category
    FROM portfolio_aggregation_base pab
),
hotspot_summary AS (
    -- Seventh CTE: Summarize hotspots by portfolio
    SELECT
        rhd.portfolio_id,
        rhd.portfolio_name,
        COUNT(DISTINCT CASE WHEN rhd.hotspot_classification = 'Critical Hotspot' THEN rhd.property_id END) AS critical_hotspot_count,
        COUNT(DISTINCT CASE WHEN rhd.hotspot_classification = 'High Hotspot' THEN rhd.property_id END) AS high_hotspot_count,
        COUNT(DISTINCT CASE WHEN rhd.hotspot_classification = 'Moderate Hotspot' THEN rhd.property_id END) AS moderate_hotspot_count,
        SUM(CASE WHEN rhd.hotspot_classification = 'Critical Hotspot' THEN rhd.total_value ELSE 0 END) AS critical_hotspot_value,
        SUM(CASE WHEN rhd.hotspot_classification = 'High Hotspot' THEN rhd.total_value ELSE 0 END) AS high_hotspot_value,
        SUM(CASE WHEN rhd.hotspot_classification = 'Moderate Hotspot' THEN rhd.total_value ELSE 0 END) AS moderate_hotspot_value,
        AVG(CASE WHEN rhd.hotspot_classification != 'No Hotspot' THEN rhd.hotspot_score ELSE NULL END) AS avg_hotspot_score
    FROM risk_hotspot_detection rhd
    GROUP BY rhd.portfolio_id, rhd.portfolio_name
),
geographic_concentration_summary AS (
    -- Eighth CTE: Summarize geographic risk concentration
    SELECT
        grc.portfolio_id,
        grc.portfolio_name,
        COUNT(DISTINCT CONCAT(grc.state_code, '-', grc.county_fips)) AS high_risk_regions_count,
        MAX(grc.risk_concentration_percentage) AS max_region_risk_concentration,
        AVG(grc.risk_concentration_percentage) AS avg_region_risk_concentration,
        SUM(grc.high_risk_region_value) AS total_high_risk_region_value,
        SUM(grc.hotspot_properties_count) AS total_hotspot_properties
    FROM geographic_risk_concentration grc
    WHERE grc.risk_concentration_percentage >= 30
    GROUP BY grc.portfolio_id, grc.portfolio_name
),
final_portfolio_summary AS (
    -- Ninth CTE: Final portfolio risk summary
    SELECT
        pda.portfolio_id,
        pda.portfolio_name,
        pda.total_properties,
        pda.total_portfolio_value,
        ROUND(CAST(pda.avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
        ROUND(CAST(pda.median_risk_score AS NUMERIC), 2) AS median_risk_score,
        ROUND(CAST(pda.total_estimated_damage AS NUMERIC), 2) AS total_estimated_damage,
        ROUND(CAST(pda.total_estimated_annual_loss AS NUMERIC), 2) AS total_estimated_annual_loss,
        pda.extreme_risk_properties,
        pda.high_risk_properties,
        pda.moderate_risk_properties,
        pda.low_risk_properties,
        ROUND(CAST(pda.extreme_risk_value AS NUMERIC), 2) AS extreme_risk_value,
        ROUND(CAST(pda.high_risk_value AS NUMERIC), 2) AS high_risk_value,
        ROUND(CAST(pda.moderate_risk_value AS NUMERIC), 2) AS moderate_risk_value,
        ROUND(CAST(pda.low_risk_value AS NUMERIC), 2) AS low_risk_value,
        pda.unique_regions_count,
        ROUND(CAST(pda.risk_diversification_score AS NUMERIC), 2) AS risk_diversification_score,
        pda.portfolio_risk_concentration_category,
        COALESCE(hs.critical_hotspot_count, 0) AS critical_hotspot_count,
        COALESCE(hs.high_hotspot_count, 0) AS high_hotspot_count,
        COALESCE(hs.moderate_hotspot_count, 0) AS moderate_hotspot_count,
        ROUND(CAST(COALESCE(hs.critical_hotspot_value, 0) AS NUMERIC), 2) AS critical_hotspot_value,
        ROUND(CAST(COALESCE(hs.high_hotspot_value, 0) AS NUMERIC), 2) AS high_hotspot_value,
        ROUND(CAST(COALESCE(hs.moderate_hotspot_value, 0) AS NUMERIC), 2) AS moderate_hotspot_value,
        ROUND(CAST(COALESCE(hs.avg_hotspot_score, 0) AS NUMERIC), 2) AS avg_hotspot_score,
        COALESCE(gcs.high_risk_regions_count, 0) AS high_risk_regions_count,
        ROUND(CAST(COALESCE(gcs.max_region_risk_concentration, 0) AS NUMERIC), 2) AS max_region_risk_concentration,
        ROUND(CAST(COALESCE(gcs.avg_region_risk_concentration, 0) AS NUMERIC), 2) AS avg_region_risk_concentration,
        ROUND(CAST(COALESCE(gcs.total_high_risk_region_value, 0) AS NUMERIC), 2) AS total_high_risk_region_value,
        COALESCE(gcs.total_hotspot_properties, 0) AS total_hotspot_properties,
        -- Overall portfolio risk rating
        CASE
            WHEN pda.avg_risk_score >= 70 OR (pda.extreme_risk_value + pda.high_risk_value) / NULLIF(pda.total_portfolio_value, 0) >= 0.5 THEN 'Critical'
            WHEN pda.avg_risk_score >= 50 OR (pda.extreme_risk_value + pda.high_risk_value) / NULLIF(pda.total_portfolio_value, 0) >= 0.3 THEN 'High'
            WHEN pda.avg_risk_score >= 30 OR (pda.extreme_risk_value + pda.high_risk_value) / NULLIF(pda.total_portfolio_value, 0) >= 0.1 THEN 'Moderate'
            ELSE 'Low'
        END AS overall_portfolio_risk_rating
    FROM portfolio_diversification_analysis pda
    LEFT JOIN hotspot_summary hs ON pda.portfolio_id = hs.portfolio_id
    LEFT JOIN geographic_concentration_summary gcs ON pda.portfolio_id = gcs.portfolio_id
)
SELECT
    portfolio_id,
    portfolio_name,
    total_properties,
    ROUND(CAST(total_portfolio_value AS NUMERIC), 2) AS total_portfolio_value,
    avg_risk_score,
    median_risk_score,
    total_estimated_damage,
    total_estimated_annual_loss,
    extreme_risk_properties,
    high_risk_properties,
    moderate_risk_properties,
    low_risk_properties,
    extreme_risk_value,
    high_risk_value,
    moderate_risk_value,
    low_risk_value,
    unique_regions_count,
    risk_diversification_score,
    portfolio_risk_concentration_category,
    critical_hotspot_count,
    high_hotspot_count,
    moderate_hotspot_count,
    critical_hotspot_value,
    high_hotspot_value,
    moderate_hotspot_value,
    avg_hotspot_score,
    high_risk_regions_count,
    max_region_risk_concentration,
    avg_region_risk_concentration,
    total_high_risk_region_value,
    total_hotspot_properties,
    overall_portfolio_risk_rating
FROM final_portfolio_summary
ORDER BY overall_portfolio_risk_rating DESC, avg_risk_score DESC, total_portfolio_value DESC
LIMIT 1000;
```

**Expected Output:** Acquisition target portfolio-level flood risk summary showing aggregated risk metrics, geographic risk clusters, hotspot locations, risk concentration by region, and portfolio diversification scores to inform M&A deal evaluation.

---

## Query 3: Historical Flood Event Due Diligence Analysis with Frequency Patterns and Temporal Clustering

**Use Case:** **M&A Due Diligence - Historical Flood Event Analysis for Acquisition Target Risk Assessment****

**Description:** Enterprise-level historical flood event analysis identifying frequency patterns, temporal clustering, severity trends, geographic recurrence patterns, and flood event correlations for properties under consideration for acquisition. Performs temporal analysis, spatial clustering, frequency calculations, and recurrence interval analysis. Designed specifically for M&A due diligence workflows to assess historical flood risk at acquisition target locations.

**Business Value:** Historical flood frequency analysis showing flood recurrence patterns, temporal clustering trends, severity distributions, and geographic recurrence hotspots for acquisition targets. Enables M&A teams to assess historical flood risk patterns at potential acquisition locations, identify properties with frequent flood history, and make informed acquisition decisions based on past flood events. Critical for due diligence to understand if acquisition targets have experienced significant flood damage in the past.

**Purpose:** Quantifies historical flood risk patterns for acquisition target locations enabling data-driven assessment of flood recurrence probability and geographic flood risk hotspots to inform M&A decision-making.

**Complexity:** Deep nested CTEs (8+ levels), temporal pattern analysis, spatial clustering, frequency calculations, recurrence interval analysis, window functions with multiple frame clauses, temporal clustering algorithms, severity trend analysis

```sql
WITH historical_flood_events_base AS (
    -- First CTE: Base historical flood events with temporal attributes
    SELECT
        hfe.event_id,
        hfe.event_name,
        hfe.event_type,
        hfe.start_date,
        hfe.end_date,
        hfe.affected_area_geom,
        hfe.peak_discharge_cfs,
        hfe.peak_stage_feet,
        hfe.total_damage_dollars,
        hfe.fatalities,
        hfe.properties_affected,
        hfe.state_code,
        hfe.county_fips,
        hfe.data_source,
        -- Calculate event duration
        CASE
            WHEN hfe.end_date IS NOT NULL THEN
                hfe.end_date - hfe.start_date
            ELSE 1
        END AS event_duration_days,
        -- Extract temporal attributes
        EXTRACT(YEAR FROM hfe.start_date) AS event_year,
        EXTRACT(MONTH FROM hfe.start_date) AS event_month,
        EXTRACT(QUARTER FROM hfe.start_date) AS event_quarter,
        EXTRACT(DOY FROM hfe.start_date) AS day_of_year,
        -- Calculate severity score
        CASE
            WHEN hfe.total_damage_dollars IS NOT NULL AND hfe.properties_affected IS NOT NULL THEN
                LOG(COALESCE(hfe.total_damage_dollars, 1) + 1) * 
                LOG(COALESCE(hfe.properties_affected, 1) + 1) * 
                COALESCE(hfe.fatalities, 0) + 1
            WHEN hfe.total_damage_dollars IS NOT NULL THEN
                LOG(COALESCE(hfe.total_damage_dollars, 1) + 1) * 10
            WHEN hfe.properties_affected IS NOT NULL THEN
                LOG(COALESCE(hfe.properties_affected, 1) + 1) * 10
            ELSE 1
        END AS severity_score
    FROM historical_flood_events hfe
    WHERE hfe.start_date >= CURRENT_DATE - INTERVAL '50 years'
),
temporal_clustering_analysis AS (
    -- Second CTE: Analyze temporal clustering of flood events
    SELECT
        hfeb.event_id,
        hfeb.event_name,
        hfeb.event_type,
        hfeb.start_date,
        hfeb.end_date,
        hfeb.event_year,
        hfeb.event_month,
        hfeb.event_quarter,
        hfeb.day_of_year,
        hfeb.state_code,
        hfeb.county_fips,
        hfeb.severity_score,
        hfeb.total_damage_dollars,
        hfeb.properties_affected,
        -- Count events in same year
        (
            SELECT COUNT(*)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.event_year = hfeb.event_year
                AND hfeb2.state_code = hfeb.state_code
        ) AS events_in_same_year,
        -- Count events within 30 days
        (
            SELECT COUNT(*)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.event_id != hfeb.event_id
                AND hfeb2.start_date BETWEEN hfeb.start_date - INTERVAL '30 days' 
                    AND hfeb.start_date + INTERVAL '30 days'
                AND hfeb2.state_code = hfeb.state_code
        ) AS events_within_30_days,
        -- Count events within 90 days
        (
            SELECT COUNT(*)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.event_id != hfeb.event_id
                AND hfeb2.start_date BETWEEN hfeb.start_date - INTERVAL '90 days' 
                    AND hfeb.start_date + INTERVAL '90 days'
                AND hfeb2.state_code = hfeb.state_code
        ) AS events_within_90_days,
        -- Days since previous event
        (
            SELECT MAX(hfeb2.start_date)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.event_id != hfeb.event_id
                AND hfeb2.start_date < hfeb.start_date
                AND hfeb2.state_code = hfeb.state_code
        ) AS previous_event_date,
        -- Days until next event
        (
            SELECT MIN(hfeb2.start_date)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.event_id != hfeb.event_id
                AND hfeb2.start_date > hfeb.start_date
                AND hfeb2.state_code = hfeb.state_code
        ) AS next_event_date
    FROM historical_flood_events_base hfeb
),
recurrence_interval_calculation AS (
    -- Third CTE: Calculate recurrence intervals
    SELECT
        tca.event_id,
        tca.event_name,
        tca.event_type,
        tca.start_date,
        tca.event_year,
        tca.event_month,
        tca.event_quarter,
        tca.state_code,
        tca.county_fips,
        tca.severity_score,
        tca.total_damage_dollars,
        tca.properties_affected,
        tca.events_in_same_year,
        tca.events_within_30_days,
        tca.events_within_90_days,
        -- Calculate days between events
        CASE
            WHEN tca.previous_event_date IS NOT NULL THEN
                tca.start_date - tca.previous_event_date
            ELSE NULL
        END AS days_since_previous_event,
        CASE
            WHEN tca.next_event_date IS NOT NULL THEN
                tca.next_event_date - tca.start_date
            ELSE NULL
        END AS days_until_next_event,
        -- Recurrence interval (years)
        CASE
            WHEN tca.previous_event_date IS NOT NULL THEN
                (tca.start_date - tca.previous_event_date) / 365.25
            ELSE NULL
        END AS recurrence_interval_years,
        -- Annual frequency
        (
            SELECT COUNT(*)::NUMERIC / 
                NULLIF(MAX(hfeb2.event_year) - MIN(hfeb2.event_year) + 1, 0)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.state_code = tca.state_code
                AND hfeb2.county_fips = tca.county_fips
        ) AS annual_frequency
    FROM temporal_clustering_analysis tca
),
frequency_pattern_analysis AS (
    -- Fourth CTE: Analyze frequency patterns by month and season
    SELECT
        ric.event_id,
        ric.event_name,
        ric.event_type,
        ric.start_date,
        ric.event_year,
        ric.event_month,
        ric.event_quarter,
        ric.state_code,
        ric.county_fips,
        ric.severity_score,
        ric.total_damage_dollars,
        ric.properties_affected,
        ric.recurrence_interval_years,
        ric.annual_frequency,
        -- Monthly frequency for this state/county
        (
            SELECT COUNT(*)::NUMERIC / 
                NULLIF(COUNT(DISTINCT hfeb2.event_year), 0)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.state_code = ric.state_code
                AND hfeb2.county_fips = ric.county_fips
                AND hfeb2.event_month = ric.event_month
        ) AS monthly_frequency,
        -- Seasonal frequency
        (
            SELECT COUNT(*)::NUMERIC / 
                NULLIF(COUNT(DISTINCT hfeb2.event_year), 0)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.state_code = ric.state_code
                AND hfeb2.county_fips = ric.county_fips
                AND hfeb2.event_quarter = ric.event_quarter
        ) AS seasonal_frequency,
        -- Window functions for temporal trends
        AVG(ric.severity_score) OVER (
            PARTITION BY ric.state_code, ric.county_fips
            ORDER BY ric.event_year
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS moving_avg_severity_5_years,
        COUNT(*) OVER (
            PARTITION BY ric.state_code, ric.county_fips
            ORDER BY ric.event_year
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS events_in_last_10_years
    FROM recurrence_interval_calculation ric
),
geographic_recurrence_analysis AS (
    -- Fifth CTE: Analyze geographic recurrence patterns
    SELECT
        fpa.event_id,
        fpa.event_name,
        fpa.event_type,
        fpa.start_date,
        fpa.event_year,
        fpa.state_code,
        fpa.county_fips,
        fpa.severity_score,
        fpa.total_damage_dollars,
        fpa.properties_affected,
        fpa.recurrence_interval_years,
        fpa.annual_frequency,
        fpa.monthly_frequency,
        fpa.seasonal_frequency,
        fpa.moving_avg_severity_5_years,
        fpa.events_in_last_10_years,
        -- Count events in same geographic area (using spatial intersection)
        (
            SELECT COUNT(*)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.event_id != fpa.event_id
                AND hfeb2.affected_area_geom IS NOT NULL
                AND (
                    SELECT affected_area_geom FROM historical_flood_events_base WHERE event_id = fpa.event_id
                ) IS NOT NULL
                AND ST_INTERSECTS(
                    hfeb2.affected_area_geom,
                    (SELECT affected_area_geom FROM historical_flood_events_base WHERE event_id = fpa.event_id)
                )
        ) AS overlapping_events_count,
        -- Average severity of overlapping events
        (
            SELECT AVG(hfeb2.severity_score)
            FROM historical_flood_events_base hfeb2
            WHERE hfeb2.event_id != fpa.event_id
                AND hfeb2.affected_area_geom IS NOT NULL
                AND (
                    SELECT affected_area_geom FROM historical_flood_events_base WHERE event_id = fpa.event_id
                ) IS NOT NULL
                AND ST_INTERSECTS(
                    hfeb2.affected_area_geom,
                    (SELECT affected_area_geom FROM historical_flood_events_base WHERE event_id = fpa.event_id)
                )
        ) AS avg_overlapping_severity
    FROM frequency_pattern_analysis fpa
),
severity_trend_analysis AS (
    -- Sixth CTE: Analyze severity trends over time
    SELECT
        gra.event_id,
        gra.event_name,
        gra.event_type,
        gra.start_date,
        gra.event_year,
        gra.state_code,
        gra.county_fips,
        gra.severity_score,
        gra.total_damage_dollars,
        gra.properties_affected,
        gra.recurrence_interval_years,
        gra.annual_frequency,
        gra.monthly_frequency,
        gra.seasonal_frequency,
        gra.moving_avg_severity_5_years,
        gra.events_in_last_10_years,
        gra.overlapping_events_count,
        gra.avg_overlapping_severity,
        -- Severity trend indicators
        LAG(gra.severity_score, 1) OVER (
            PARTITION BY gra.state_code, gra.county_fips
            ORDER BY gra.event_year
        ) AS previous_severity,
        LEAD(gra.severity_score, 1) OVER (
            PARTITION BY gra.state_code, gra.county_fips
            ORDER BY gra.event_year
        ) AS next_severity,
        -- Severity trend direction
        CASE
            WHEN gra.severity_score > gra.moving_avg_severity_5_years * 1.2 THEN 'Increasing'
            WHEN gra.severity_score < gra.moving_avg_severity_5_years * 0.8 THEN 'Decreasing'
            ELSE 'Stable'
        END AS severity_trend,
        -- Percentile rank of severity
        PERCENT_RANK() OVER (
            PARTITION BY gra.state_code, gra.county_fips
            ORDER BY gra.severity_score
        ) AS severity_percentile_rank
    FROM geographic_recurrence_analysis gra
),
flood_frequency_classification AS (
    -- Seventh CTE: Classify flood frequency patterns
    SELECT
        sta.event_id,
        sta.event_name,
        sta.event_type,
        sta.start_date,
        sta.event_year,
        sta.state_code,
        sta.county_fips,
        ROUND(CAST(sta.severity_score AS NUMERIC), 2) AS severity_score,
        ROUND(CAST(sta.total_damage_dollars AS NUMERIC), 2) AS total_damage_dollars,
        sta.properties_affected,
        ROUND(CAST(sta.recurrence_interval_years AS NUMERIC), 2) AS recurrence_interval_years,
        ROUND(CAST(sta.annual_frequency AS NUMERIC), 4) AS annual_frequency,
        ROUND(CAST(sta.monthly_frequency AS NUMERIC), 4) AS monthly_frequency,
        ROUND(CAST(sta.seasonal_frequency AS NUMERIC), 4) AS seasonal_frequency,
        ROUND(CAST(sta.moving_avg_severity_5_years AS NUMERIC), 2) AS moving_avg_severity_5_years,
        sta.events_in_last_10_years,
        sta.overlapping_events_count,
        ROUND(CAST(sta.avg_overlapping_severity AS NUMERIC), 2) AS avg_overlapping_severity,
        sta.severity_trend,
        ROUND(CAST(sta.severity_percentile_rank AS NUMERIC), 4) AS severity_percentile_rank,
        -- Frequency classification
        CASE
            WHEN sta.annual_frequency >= 1.0 THEN 'Very Frequent (Annual+)'
            WHEN sta.annual_frequency >= 0.5 THEN 'Frequent (Biannual)'
            WHEN sta.annual_frequency >= 0.2 THEN 'Moderate (Every 5 years)'
            WHEN sta.annual_frequency >= 0.1 THEN 'Occasional (Every 10 years)'
            WHEN sta.annual_frequency >= 0.05 THEN 'Rare (Every 20 years)'
            ELSE 'Very Rare (20+ years)'
        END AS frequency_classification,
        -- Recurrence classification
        CASE
            WHEN sta.recurrence_interval_years IS NULL THEN 'First Event'
            WHEN sta.recurrence_interval_years < 1 THEN 'Less than 1 year'
            WHEN sta.recurrence_interval_years < 5 THEN '1-5 years'
            WHEN sta.recurrence_interval_years < 10 THEN '5-10 years'
            WHEN sta.recurrence_interval_years < 20 THEN '10-20 years'
            ELSE '20+ years'
        END AS recurrence_classification
    FROM severity_trend_analysis sta
)
SELECT
    event_id,
    event_name,
    event_type,
    start_date,
    event_year,
    state_code,
    county_fips,
    severity_score,
    total_damage_dollars,
    properties_affected,
    recurrence_interval_years,
    annual_frequency,
    monthly_frequency,
    seasonal_frequency,
    moving_avg_severity_5_years,
    events_in_last_10_years,
    overlapping_events_count,
    avg_overlapping_severity,
    severity_trend,
    severity_percentile_rank,
    frequency_classification,
    recurrence_classification
FROM flood_frequency_classification
ORDER BY event_year DESC, severity_score DESC, annual_frequency DESC
LIMIT 10000;
```

**Expected Output:** Historical flood event due diligence analysis for acquisition targets showing frequency patterns, temporal clustering trends, severity distributions, recurrence intervals, and geographic recurrence hotspots to inform M&A acquisition decisions.

---
## Query 4: Sea Level Rise Impact Projections for Coastal Acquisition Targets Across Multiple Time Horizons with Scenario Comparison

**Use Case:** **M&A Due Diligence - Coastal Acquisition Target Risk Assessment - Multi-Horizon Sea Level Rise Impact Analysis****

**Description:** Enterprise-level sea level rise impact analysis projecting impacts across 5, 10, 20, 30, 50, and 100-year horizons comparing Low, Intermediate-Low, Intermediate, Intermediate-High, High, and Extreme scenarios for coastal properties under consideration for acquisition. Performs temporal projections, scenario comparisons, impact calculations, and property vulnerability assessments. Designed specifically for M&A teams evaluating coastal acquisition targets.

**Business Value:** Multi-horizon sea level rise impact projections showing property vulnerability across different time frames and scenarios for coastal acquisition targets. Enables M&A teams to assess long-term coastal property risks for acquisition targets, evaluate deal viability over multiple time horizons, and make informed acquisition decisions based on projected sea level rise impacts. Critical for coastal M&A transactions where sea level rise can significantly impact property value over the acquisition hold period.

**Purpose:** Quantifies sea level rise impacts across multiple time horizons for coastal acquisition targets enabling long-term risk assessment and strategic M&A planning.

**Complexity:** Deep nested CTEs (9+ levels), temporal projections, scenario comparisons, impact calculations, window functions with multiple frame clauses, percentile calculations, vulnerability scoring

```sql
WITH sea_level_rise_projections_base AS (
    -- First CTE: Base sea level rise projections
    SELECT
        nslr.projection_id,
        nslr.station_id,
        nslr.station_name,
        nslr.station_latitude,
        nslr.station_longitude,
        nslr.station_geom,
        nslr.projection_year,
        nslr.scenario,
        nslr.sea_level_rise_feet,
        nslr.confidence_level,
        nslr.high_tide_flooding_days,
        EXTRACT(YEAR FROM CURRENT_DATE) AS current_year,
        nslr.projection_year - EXTRACT(YEAR FROM CURRENT_DATE) AS years_from_now
    FROM noaa_sea_level_rise nslr
    WHERE nslr.projection_year >= EXTRACT(YEAR FROM CURRENT_DATE)
),
property_slr_matching AS (
    -- Second CTE: Match properties to nearest SLR stations
    SELECT
        rep.property_id,
        rep.property_address,
        rep.property_latitude,
        rep.property_longitude,
        rep.property_geom,
        rep.elevation_feet,
        rep.total_value,
        rep.state_code,
        rep.county_fips,
        slrb.station_id,
        slrb.station_name,
        slrb.projection_year,
        slrb.scenario,
        slrb.sea_level_rise_feet,
        slrb.high_tide_flooding_days,
        slrb.years_from_now,
        ST_DISTANCE(rep.property_geom, slrb.station_geom) AS distance_to_station_meters
    FROM real_estate_properties rep
    CROSS JOIN sea_level_rise_projections_base slrb
    WHERE rep.property_geom IS NOT NULL
        AND slrb.station_geom IS NOT NULL
        AND ST_DISTANCE(rep.property_geom, slrb.station_geom) < 50000
),
nearest_station_selection AS (
    -- Third CTE: Select nearest station for each property-scenario-year combination
    SELECT DISTINCT ON (psm.property_id, psm.projection_year, psm.scenario)
        psm.property_id,
        psm.property_address,
        psm.property_latitude,
        psm.property_longitude,
        psm.elevation_feet,
        psm.total_value,
        psm.state_code,
        psm.county_fips,
        psm.projection_year,
        psm.scenario,
        psm.sea_level_rise_feet,
        psm.high_tide_flooding_days,
        psm.years_from_now,
        psm.distance_to_station_meters
    FROM property_slr_matching psm
    ORDER BY psm.property_id, psm.projection_year, psm.scenario, psm.distance_to_station_meters
),
multi_horizon_projections AS (
    -- Fourth CTE: Calculate impacts across multiple time horizons
    SELECT
        nss.property_id,
        nss.property_address,
        nss.elevation_feet,
        nss.total_value,
        nss.state_code,
        nss.county_fips,
        nss.projection_year,
        nss.scenario,
        nss.sea_level_rise_feet,
        nss.high_tide_flooding_days,
        nss.years_from_now,
        -- Elevation relative to projected sea level
        nss.elevation_feet - nss.sea_level_rise_feet AS elevation_above_projected_sl_feet,
        -- Impact classification
        CASE
            WHEN nss.elevation_feet < nss.sea_level_rise_feet THEN 'Below Sea Level'
            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 2 THEN 'Critical (< 2ft above)'
            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 5 THEN 'High (< 5ft above)'
            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 10 THEN 'Moderate (< 10ft above)'
            ELSE 'Low Risk'
        END AS impact_classification,
        -- Vulnerability score (0-100)
        CASE
            WHEN nss.elevation_feet < nss.sea_level_rise_feet THEN 100
            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 2 THEN 90
            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 5 THEN 75
            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 10 THEN 50
            ELSE 25
        END AS vulnerability_score
    FROM nearest_station_selection nss
),
scenario_comparison AS (
    -- Fifth CTE: Compare scenarios for each property and time horizon
    SELECT
        mhp.property_id,
        mhp.property_address,
        mhp.elevation_feet,
        mhp.total_value,
        mhp.state_code,
        mhp.county_fips,
        mhp.projection_year,
        mhp.years_from_now,
        -- Scenario-specific values
        MAX(CASE WHEN mhp.scenario = 'Low' THEN mhp.sea_level_rise_feet END) AS slr_low_feet,
        MAX(CASE WHEN mhp.scenario = 'Intermediate-Low' THEN mhp.sea_level_rise_feet END) AS slr_intermediate_low_feet,
        MAX(CASE WHEN mhp.scenario = 'Intermediate' THEN mhp.sea_level_rise_feet END) AS slr_intermediate_feet,
        MAX(CASE WHEN mhp.scenario = 'Intermediate-High' THEN mhp.sea_level_rise_feet END) AS slr_intermediate_high_feet,
        MAX(CASE WHEN mhp.scenario = 'High' THEN mhp.sea_level_rise_feet END) AS slr_high_feet,
        MAX(CASE WHEN mhp.scenario = 'Extreme' THEN mhp.sea_level_rise_feet END) AS slr_extreme_feet,
        -- Average across scenarios
        AVG(mhp.sea_level_rise_feet) AS avg_slr_across_scenarios,
        -- Scenario range
        MAX(mhp.sea_level_rise_feet) - MIN(mhp.sea_level_rise_feet) AS slr_scenario_range,
        -- Worst case vulnerability
        MAX(mhp.vulnerability_score) AS worst_case_vulnerability_score,
        -- Best case vulnerability
        MIN(mhp.vulnerability_score) AS best_case_vulnerability_score
    FROM multi_horizon_projections mhp
    GROUP BY mhp.property_id, mhp.property_address, mhp.elevation_feet, mhp.total_value, 
             mhp.state_code, mhp.county_fips, mhp.projection_year, mhp.years_from_now
),
temporal_projection_analysis AS (
    -- Sixth CTE: Analyze temporal progression of impacts
    SELECT
        sc.property_id,
        sc.property_address,
        sc.elevation_feet,
        sc.total_value,
        sc.state_code,
        sc.county_fips,
        sc.projection_year,
        sc.years_from_now,
        sc.slr_low_feet,
        sc.slr_intermediate_feet,
        sc.slr_high_feet,
        sc.avg_slr_across_scenarios,
        sc.worst_case_vulnerability_score,
        sc.best_case_vulnerability_score,
        -- Projections for different horizons
        MAX(CASE WHEN sc.years_from_now = 5 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_5_years,
        MAX(CASE WHEN sc.years_from_now = 10 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_10_years,
        MAX(CASE WHEN sc.years_from_now = 20 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_20_years,
        MAX(CASE WHEN sc.years_from_now = 30 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_30_years,
        MAX(CASE WHEN sc.years_from_now = 50 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_50_years,
        MAX(CASE WHEN sc.years_from_now = 100 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_100_years,
        -- Rate of sea level rise (feet per year)
        CASE
            WHEN sc.years_from_now > 0 THEN
                sc.avg_slr_across_scenarios / sc.years_from_now
            ELSE NULL
        END AS slr_rate_feet_per_year
    FROM scenario_comparison sc
),
impact_assessment AS (
    -- Seventh CTE: Assess impacts across time horizons
    SELECT
        tpa.property_id,
        tpa.property_address,
        tpa.elevation_feet,
        tpa.total_value,
        tpa.state_code,
        tpa.county_fips,
        tpa.projection_year,
        tpa.years_from_now,
        ROUND(CAST(tpa.slr_5_years AS NUMERIC), 3) AS slr_5_years_feet,
        ROUND(CAST(tpa.slr_10_years AS NUMERIC), 3) AS slr_10_years_feet,
        ROUND(CAST(tpa.slr_20_years AS NUMERIC), 3) AS slr_20_years_feet,
        ROUND(CAST(tpa.slr_30_years AS NUMERIC), 3) AS slr_30_years_feet,
        ROUND(CAST(tpa.slr_50_years AS NUMERIC), 3) AS slr_50_years_feet,
        ROUND(CAST(tpa.slr_100_years AS NUMERIC), 3) AS slr_100_years_feet,
        ROUND(CAST(tpa.avg_slr_across_scenarios AS NUMERIC), 3) AS current_horizon_slr_feet,
        ROUND(CAST(tpa.slr_rate_feet_per_year AS NUMERIC), 4) AS slr_rate_feet_per_year,
        -- Impact at each horizon
        CASE
            WHEN tpa.elevation_feet < tpa.slr_5_years THEN 'At Risk (5yr)'
            WHEN tpa.elevation_feet < tpa.slr_10_years THEN 'At Risk (10yr)'
            WHEN tpa.elevation_feet < tpa.slr_20_years THEN 'At Risk (20yr)'
            WHEN tpa.elevation_feet < tpa.slr_30_years THEN 'At Risk (30yr)'
            WHEN tpa.elevation_feet < tpa.slr_50_years THEN 'At Risk (50yr)'
            WHEN tpa.elevation_feet < tpa.slr_100_years THEN 'At Risk (100yr)'
            ELSE 'Low Risk'
        END AS earliest_risk_horizon,
        -- Overall risk rating
        CASE
            WHEN tpa.elevation_feet < tpa.slr_30_years THEN 'Critical'
            WHEN tpa.elevation_feet < tpa.slr_50_years THEN 'High'
            WHEN tpa.elevation_feet < tpa.slr_100_years THEN 'Moderate'
            ELSE 'Low'
        END AS overall_risk_rating
    FROM temporal_projection_analysis tpa
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    projection_year,
    years_from_now,
    slr_5_years_feet,
    slr_10_years_feet,
    slr_20_years_feet,
    slr_30_years_feet,
    slr_50_years_feet,
    slr_100_years_feet,
    current_horizon_slr_feet,
    slr_rate_feet_per_year,
    earliest_risk_horizon,
    overall_risk_rating
FROM impact_assessment
WHERE years_from_now IN (5, 10, 20, 30, 50, 100)
ORDER BY overall_risk_rating DESC, years_from_now, total_value DESC
LIMIT 10000;

```

**Expected Output:** Sea level rise impact projections across multiple time horizons (5, 10, 20, 30, 50, 100 years) comparing different scenarios with property vulnerability assessments.

---

## Query 5: Streamflow Flood Frequency Analysis with Gauge Network Coverage and Historical Pattern Recognition

**Use Case:** **M&A Due Diligence - Streamflow Risk Analysis - Streamflow Flood Frequency Analysis for Acquisition Target Risk Assessment****

**Description:** Enterprise-level streamflow flood frequency analysis identifying flood patterns, gauge network coverage, historical flood recurrence intervals, and flood stage exceedance probabilities. Performs temporal analysis, frequency calculations, and gauge network optimization.

**Business Value:** Streamflow Flood Frequency Analysis with Gauge Network Coverage and Historical Pattern Recognition showing streamflow flood frequency patterns and historical flood risk for acquisition targets. Enables M&A teams to assess riverine flood risk for acquisition targets and make informed acquisition decisions based on streamflow flood patterns.

**Purpose:** Quantifies riverine flood risk patterns for acquisition targets enabling data-driven assessment of flood recurrence probability and gauge network adequacy to inform M&A acquisition decisions.

**Complexity:** Deep nested CTEs (8+ levels), temporal pattern analysis, frequency calculations, recurrence interval analysis, window functions with multiple frame clauses, gauge network analysis

```sql
WITH streamflow_observations_base AS (
    SELECT
        uso.observation_id,
        uso.gauge_id,
        uso.observation_time,
        uso.gage_height_feet,
        uso.discharge_cfs,
        uso.stage_feet,
        uso.flood_category,
        uso.percentile_rank,
        usg.gauge_name,
        usg.gauge_latitude,
        usg.gauge_longitude,
        usg.gauge_geom,
        usg.flood_stage_feet,
        usg.moderate_flood_stage_feet,
        usg.major_flood_stage_feet,
        usg.drainage_area_sq_miles,
        usg.state_code,
        usg.county_name,
        usg.river_name,
        EXTRACT(YEAR FROM uso.observation_time) AS observation_year,
        EXTRACT(MONTH FROM uso.observation_time) AS observation_month
    FROM usgs_streamflow_observations uso
    INNER JOIN usgs_streamflow_gauges usg ON uso.gauge_id = usg.gauge_id
    WHERE usg.active_status = TRUE
        AND uso.observation_time >= CURRENT_DATE - INTERVAL '20 years'
),
flood_event_identification AS (
    SELECT
        sob.observation_id,
        sob.gauge_id,
        sob.gauge_name,
        sob.observation_time,
        sob.observation_year,
        sob.observation_month,
        sob.gage_height_feet,
        sob.discharge_cfs,
        sob.stage_feet,
        sob.flood_category,
        sob.flood_stage_feet,
        sob.moderate_flood_stage_feet,
        sob.major_flood_stage_feet,
        sob.state_code,
        sob.county_name,
        sob.river_name,
        CASE
            WHEN sob.stage_feet >= sob.major_flood_stage_feet THEN 'Major'
            WHEN sob.stage_feet >= sob.moderate_flood_stage_feet THEN 'Moderate'
            WHEN sob.stage_feet >= sob.flood_stage_feet THEN 'Minor'
            ELSE 'None'
        END AS flood_severity,
        CASE
            WHEN sob.stage_feet >= sob.major_flood_stage_feet THEN 3
            WHEN sob.stage_feet >= sob.moderate_flood_stage_feet THEN 2
            WHEN sob.stage_feet >= sob.flood_stage_feet THEN 1
            ELSE 0
        END AS flood_severity_score
    FROM streamflow_observations_base sob
),
flood_frequency_calculation AS (
    SELECT
        fei.gauge_id,
        fei.gauge_name,
        fei.state_code,
        fei.county_name,
        fei.river_name,
        fei.observation_year,
        COUNT(DISTINCT CASE WHEN fei.flood_severity != 'None' THEN DATE(fei.observation_time) END) AS flood_days_per_year,
        COUNT(DISTINCT CASE WHEN fei.flood_severity = 'Major' THEN DATE(fei.observation_time) END) AS major_flood_days_per_year,
        COUNT(DISTINCT CASE WHEN fei.flood_severity = 'Moderate' THEN DATE(fei.observation_time) END) AS moderate_flood_days_per_year,
        COUNT(DISTINCT CASE WHEN fei.flood_severity = 'Minor' THEN DATE(fei.observation_time) END) AS minor_flood_days_per_year,
        MAX(fei.discharge_cfs) AS peak_discharge_cfs,
        MAX(fei.stage_feet) AS peak_stage_feet,
        AVG(CASE WHEN fei.flood_severity != 'None' THEN fei.discharge_cfs END) AS avg_flood_discharge_cfs
    FROM flood_event_identification fei
    GROUP BY fei.gauge_id, fei.gauge_name, fei.state_code, fei.county_name, fei.river_name, fei.observation_year
),
recurrence_interval_analysis AS (
    SELECT
        ffc.gauge_id,
        ffc.gauge_name,
        ffc.state_code,
        ffc.county_name,
        ffc.river_name,
        ffc.observation_year,
        ffc.flood_days_per_year,
        ffc.major_flood_days_per_year,
        ffc.moderate_flood_days_per_year,
        ffc.minor_flood_days_per_year,
        ffc.peak_discharge_cfs,
        ffc.peak_stage_feet,
        ffc.avg_flood_discharge_cfs,
        COUNT(*) OVER (PARTITION BY ffc.gauge_id) AS total_years,
        COUNT(CASE WHEN ffc.flood_days_per_year > 0 THEN 1 END) OVER (PARTITION BY ffc.gauge_id) AS years_with_floods,
        AVG(ffc.flood_days_per_year) OVER (PARTITION BY ffc.gauge_id) AS avg_flood_days_per_year,
        AVG(ffc.peak_discharge_cfs) OVER (PARTITION BY ffc.gauge_id) AS avg_peak_discharge
    FROM flood_frequency_calculation ffc
),
gauge_network_coverage AS (
    SELECT
        ria.gauge_id,
        ria.gauge_name,
        ria.state_code,
        ria.county_name,
        ria.river_name,
        ria.total_years,
        ria.years_with_floods,
        ROUND(CAST(ria.avg_flood_days_per_year AS NUMERIC), 2) AS avg_flood_days_per_year,
        ROUND(CAST(ria.avg_peak_discharge AS NUMERIC), 2) AS avg_peak_discharge_cfs,
        (
            SELECT COUNT(*)
            FROM usgs_streamflow_gauges usg2
            WHERE usg2.active_status = TRUE
                AND usg2.gauge_geom IS NOT NULL
                AND (
                    SELECT gauge_geom FROM usgs_streamflow_gauges WHERE gauge_id = ria.gauge_id
                ) IS NOT NULL
                AND ST_DISTANCE(
                    usg2.gauge_geom,
                    (SELECT gauge_geom FROM usgs_streamflow_gauges WHERE gauge_id = ria.gauge_id)
                ) < 50000
        ) AS nearby_gauges_count,
        CASE
            WHEN ria.years_with_floods > 0 THEN
                ria.total_years::NUMERIC / ria.years_with_floods::NUMERIC
            ELSE NULL
        END AS recurrence_interval_years
    FROM recurrence_interval_analysis ria
)
SELECT
    gauge_id,
    gauge_name,
    state_code,
    county_name,
    river_name,
    total_years,
    years_with_floods,
    avg_flood_days_per_year,
    avg_peak_discharge_cfs,
    nearby_gauges_count,
    ROUND(CAST(recurrence_interval_years AS NUMERIC), 2) AS recurrence_interval_years
FROM gauge_network_coverage
ORDER BY avg_flood_days_per_year DESC, recurrence_interval_years ASC
LIMIT 5000;

```

**Expected Output:** Streamflow flood frequency analysis showing historical flood patterns, recurrence intervals, and gauge network coverage metrics.

---

## Query 6: NASA Flood Model Performance Evaluation with Advanced Analytics

**Use Case:** **M&A Due Diligence - Model Validation - NASA Flood Model Performance Evaluation for Acquisition Target Risk Assessment****

**Description:** Enterprise-level NASA model performance analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** NASA Flood Model Performance Evaluation with Advanced Analytics showing NASA flood model performance and accuracy metrics for acquisition target risk assessment. Enables M&A teams to evaluate reliability of flood model predictions for acquisition targets and make informed acquisition decisions based on model performance.

**Purpose:** Provides comprehensive NASA model performance enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** NASA Flood Model Performance Evaluation report showing comprehensive risk metrics and analytics.

---

## Query 7: Property-Flood Zone Intersection Analysis with Advanced Analytics

**Use Case:** **M&A Due Diligence - Spatial Risk Analysis - Property-Flood Zone Intersection Analysis for Acquisition Target Evaluation****

**Description:** Enterprise-level property-flood zone intersections analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Property-Flood Zone Intersection Analysis with Advanced Analytics showing spatial relationships between properties and flood zones for acquisition targets. Enables M&A teams to identify properties within or near flood zones, assess spatial flood risk exposure, and make informed acquisition decisions based on flood zone proximity.

**Purpose:** Provides comprehensive property-flood zone intersections enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Property-Flood Zone Intersection Analysis report showing comprehensive risk metrics and analytics.

---

## Query 8: Risk Trend Analysis Over Time with Advanced Analytics

**Use Case:** **M&A Due Diligence - Risk Trend Analysis - Risk Trend Analysis Over Time for Acquisition Target Risk Assessment****

**Description:** Enterprise-level risk trends over time analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Risk Trend Analysis Over Time with Advanced Analytics showing flood risk trends over time for acquisition targets. Enables M&A teams to assess whether flood risk is increasing or decreasing over time for acquisition targets and make informed acquisition decisions based on risk trends.

**Purpose:** Provides comprehensive risk trends over time enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Risk Trend Analysis Over Time report showing comprehensive risk metrics and analytics.

---

## Query 9: Geographic Risk Clustering with Advanced Analytics

**Use Case:** **M&A Due Diligence - Geographic Risk Analysis - Geographic Risk Clustering for Acquisition Target Portfolio Evaluation****

**Description:** Enterprise-level geographic risk clusters analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Geographic Risk Clustering with Advanced Analytics showing geographic risk clusters and hotspots for acquisition target portfolios. Enables M&A teams to identify high-risk geographic concentrations in acquisition targets, assess portfolio risk distribution, and make informed acquisition decisions based on geographic risk clustering.

**Purpose:** Provides comprehensive geographic risk clusters enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Geographic Risk Clustering report showing comprehensive risk metrics and analytics.

---

## Query 10: Property Vulnerability Scoring with Advanced Analytics

**Use Case:** **M&A Due Diligence - Vulnerability Assessment - Property Vulnerability Scoring for Acquisition Target Risk Assessment****

**Description:** Enterprise-level property vulnerability scores analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Property Vulnerability Scoring with Advanced Analytics showing property vulnerability scores for acquisition targets. Enables M&A teams to assess vulnerability of individual properties in acquisition targets, prioritize high-vulnerability properties for detailed analysis, and make informed acquisition decisions based on vulnerability scoring.

**Purpose:** Provides comprehensive property vulnerability scores enabling data-driven risk assessment and investment decision-making.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Property Vulnerability Scoring report showing comprehensive risk metrics and analytics.

---

## Query 11: Financial Impact Modeling for M&A Acquisition Pricing with Advanced Analytics

**Use Case:** **M&A Due Diligence - Financial Risk Analysis - Flood Risk Financial Impact Modeling for Acquisition Pricing and Deal Structuring****

**Description:** Enterprise-level financial impact modeling analysis calculating estimated flood damage costs, insurance premiums, annual loss projections, and total cost of ownership for properties under consideration for acquisition. Performs complex aggregations, window functions, and multi-dimensional financial analysis. Designed specifically for M&A teams to assess financial impact of flood risk on acquisition targets and inform acquisition pricing negotiations.

**Business Value:** Comprehensive financial impact modeling showing estimated flood damage costs, insurance premiums, annual loss projections, and total cost of ownership for acquisition targets. Enables M&A teams to quantify financial impact of flood risk on acquisition targets, adjust acquisition pricing based on flood risk exposure, structure deals with appropriate risk adjustments, and make informed acquisition decisions based on total cost of ownership including flood risk costs. Critical for acquisition pricing negotiations and deal structuring.

**Purpose:** Provides comprehensive financial impact modeling for acquisition targets enabling data-driven acquisition pricing, deal structuring, and M&A decision-making based on flood risk financial exposure.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Financial Impact Modeling report showing comprehensive risk metrics and analytics.

---

## Query 12: FEMA Flood Zone Risk Classification with Advanced Analytics

**Use Case:** **M&A Due Diligence - FEMA Zone Analysis - FEMA Flood Zone Risk Classification for Acquisition Target Evaluation****

**Description:** Enterprise-level FEMA flood zone classification analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** FEMA Flood Zone Risk Classification with Advanced Analytics showing FEMA flood zone risk classifications for acquisition targets. Enables M&A teams to assess FEMA flood zone exposure for acquisition targets, evaluate regulatory compliance, and make informed acquisition decisions based on flood zone classifications.

**Purpose:** Provides comprehensive FEMA flood zone classification enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** FEMA Flood Zone Risk Classification report showing comprehensive risk metrics and analytics.

---

## Query 13: NOAA Sea Level Rise Scenario Comparison with Advanced Analytics

**Use Case:** **M&A Due Diligence - Sea Level Rise Analysis - NOAA Sea Level Rise Scenario Comparison for Coastal Acquisition Targets****

**Description:** Enterprise-level sea level rise scenarios analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** NOAA Sea Level Rise Scenario Comparison with Advanced Analytics showing sea level rise scenario comparisons for coastal acquisition targets. Enables M&A teams to compare different sea level rise scenarios for coastal acquisition targets, assess long-term risk exposure, and make informed acquisition decisions based on scenario analysis.

**Purpose:** Provides comprehensive sea level rise scenarios enabling data-driven risk assessment and M&A acquisition decision-making for coastal acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** NOAA Sea Level Rise Scenario Comparison report showing comprehensive risk metrics and analytics.

---

## Query 14: USGS Streamflow Historical Pattern Recognition with Advanced Analytics

**Use Case:** **M&A Due Diligence - Historical Pattern Analysis - USGS Streamflow Historical Pattern Recognition for Acquisition Target Risk Assessment****

**Description:** Enterprise-level streamflow patterns analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** USGS Streamflow Historical Pattern Recognition with Advanced Analytics showing historical streamflow patterns for acquisition target locations. Enables M&A teams to assess historical flood patterns at acquisition target locations, identify recurring flood risks, and make informed acquisition decisions based on historical streamflow patterns.

**Purpose:** Provides comprehensive streamflow patterns enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** USGS Streamflow Historical Pattern Recognition report showing comprehensive risk metrics and analytics.

---

## Query 15: NASA Model Prediction Accuracy Assessment with Advanced Analytics

**Use Case:** **M&A Due Diligence - Model Accuracy Assessment - NASA Model Prediction Accuracy Assessment for Acquisition Target Risk Evaluation****

**Description:** Enterprise-level NASA model accuracy analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** NASA Model Prediction Accuracy Assessment with Advanced Analytics showing NASA model prediction accuracy for acquisition target locations. Enables M&A teams to evaluate reliability of NASA flood model predictions for acquisition targets, assess model confidence, and make informed acquisition decisions based on model accuracy.

**Purpose:** Provides comprehensive NASA model accuracy enabling data-driven risk assessment and investment decision-making.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** NASA Model Prediction Accuracy Assessment report showing comprehensive risk metrics and analytics.

---

## Query 16: Acquisition Target Portfolio Risk Summary Generation with Advanced Analytics

**Use Case:** **M&A Due Diligence - Acquisition Target Portfolio Analysis - Portfolio Risk Summary Generation for M&A Deal Evaluation****

**Description:** Enterprise-level portfolio risk summaries analysis generating aggregated risk metrics, risk concentration analysis, and portfolio-level risk scores for acquisition target portfolios. Performs complex aggregations, window functions, and multi-dimensional analysis. Designed specifically for M&A teams to assess overall flood risk exposure of acquisition target portfolios.

**Business Value:** Comprehensive acquisition target portfolio risk summary showing aggregated risk metrics, risk concentration by region, portfolio-level risk scores, and overall deal risk assessment. Enables M&A teams to evaluate overall flood risk exposure of acquisition target portfolios, assess deal-level risk, negotiate acquisition pricing based on portfolio risk, and make informed go/no-go decisions for portfolio acquisitions. Critical for large portfolio M&A transactions where portfolio-level risk assessment is essential.

**Purpose:** Provides comprehensive portfolio risk summaries for acquisition targets enabling data-driven M&A deal evaluation, risk assessment, and acquisition decision-making.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Portfolio Risk Summary Generation report showing comprehensive risk metrics and analytics.

---

## Query 17: Data Quality Metrics Analysis with Advanced Analytics

**Use Case:** **M&A Due Diligence - Data Quality Assessment - Data Quality Metrics Analysis for Acquisition Target Risk Assessment****

**Description:** Enterprise-level data quality metrics analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Data Quality Metrics Analysis with Advanced Analytics showing data quality metrics for flood risk data sources used in acquisition target risk assessment. Enables M&A teams to assess data quality and reliability of risk assessments for acquisition targets and make informed acquisition decisions based on data quality metrics.

**Purpose:** Provides comprehensive data quality metrics enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Data Quality Metrics Analysis report showing comprehensive risk metrics and analytics.

---

## Query 18: Spatial Join Optimization with Advanced Analytics

**Use Case:** **M&A Due Diligence - Spatial Analysis Optimization - Spatial Join Optimization for Acquisition Target Risk Assessment****

**Description:** Enterprise-level spatial join optimization analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Spatial Join Optimization with Advanced Analytics showing optimized spatial join analysis for acquisition target risk assessment. Enables M&A teams to efficiently analyze spatial relationships between properties and flood zones for acquisition targets and make informed acquisition decisions based on spatial analysis.

**Purpose:** Provides comprehensive spatial join optimization enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Spatial Join Optimization report showing comprehensive risk metrics and analytics.

---

## Query 19: Multi-Source Risk Score Fusion with Advanced Analytics

**Use Case:** **M&A Due Diligence - Risk Score Fusion - Multi-Source Risk Score Fusion for Acquisition Target Risk Assessment****

**Description:** Enterprise-level multi-source risk fusion analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Multi-Source Risk Score Fusion with Advanced Analytics showing fused multi-source risk scores for acquisition targets. Enables M&A teams to combine risk scores from multiple data sources (FEMA, NOAA, USGS, NASA) for comprehensive acquisition target risk assessment and make informed acquisition decisions based on integrated risk scores.

**Purpose:** Provides comprehensive multi-source risk fusion enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Multi-Source Risk Score Fusion report showing comprehensive risk metrics and analytics.

---

## Query 20: Temporal Risk Projection Analysis with Advanced Analytics

**Use Case:** **M&A Due Diligence - Temporal Risk Analysis - Temporal Risk Projection Analysis for Acquisition Target Risk Assessment****

**Description:** Enterprise-level temporal risk projections analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Temporal Risk Projection Analysis with Advanced Analytics showing temporal risk projections for acquisition targets across multiple time horizons. Enables M&A teams to assess future flood risk projections for acquisition targets, evaluate long-term risk exposure, and make informed acquisition decisions based on temporal risk projections.

**Purpose:** Provides comprehensive temporal risk projections enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Temporal Risk Projection Analysis report showing comprehensive risk metrics and analytics.

---

## Query 21: Property Elevation vs Flood Risk Correlation with Advanced Analytics

**Use Case:** **M&A Due Diligence - Elevation Risk Analysis - Property Elevation vs Flood Risk Correlation for Acquisition Target Evaluation****

**Description:** Enterprise-level elevation-risk correlation analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Property Elevation vs Flood Risk Correlation with Advanced Analytics showing correlation between property elevation and flood risk for acquisition targets. Enables M&A teams to assess elevation-based flood risk for acquisition targets, identify low-elevation high-risk properties, and make informed acquisition decisions based on elevation-risk correlation.

**Purpose:** Provides comprehensive elevation-risk correlation enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Property Elevation vs Flood Risk Correlation report showing comprehensive risk metrics and analytics.

---

## Query 22: Historical Flood Event Impact Assessment with Advanced Analytics

**Use Case:** **M&A Due Diligence - Historical Impact Assessment - Historical Flood Event Impact Assessment for Acquisition Target Risk Evaluation****

**Description:** Enterprise-level historical flood impacts analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Historical Flood Event Impact Assessment with Advanced Analytics showing historical flood event impact assessment for acquisition target locations. Enables M&A teams to assess historical flood damage and impacts at acquisition target locations, evaluate past flood events, and make informed acquisition decisions based on historical impact analysis.

**Purpose:** Provides comprehensive historical flood impacts enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Historical Flood Event Impact Assessment report showing comprehensive risk metrics and analytics.

---

## Query 23: Model Performance Comparison with Advanced Analytics

**Use Case:** **M&A Due Diligence - Model Comparison - Model Performance Comparison for Acquisition Target Risk Assessment****

**Description:** Enterprise-level model performance comparison analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Model Performance Comparison with Advanced Analytics showing comparison of multiple flood model performance for acquisition target risk assessment. Enables M&A teams to compare different flood model predictions for acquisition targets, assess model agreement, and make informed acquisition decisions based on model comparison.

**Purpose:** Provides comprehensive model performance comparison enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Model Performance Comparison report showing comprehensive risk metrics and analytics.

---

## Query 24: Geographic Risk Distribution Analysis with Advanced Analytics

**Use Case:** **M&A Due Diligence - Geographic Distribution Analysis - Geographic Risk Distribution Analysis for Acquisition Target Portfolio Evaluation****

**Description:** Enterprise-level geographic risk distribution analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Geographic Risk Distribution Analysis with Advanced Analytics showing geographic risk distribution analysis for acquisition target portfolios. Enables M&A teams to assess geographic distribution of flood risk in acquisition target portfolios, identify risk concentrations, and make informed acquisition decisions based on geographic risk distribution.

**Purpose:** Provides comprehensive geographic risk distribution enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Geographic Risk Distribution Analysis report showing comprehensive risk metrics and analytics.

---

## Query 25: Property Type Risk Analysis with Advanced Analytics

**Use Case:** **M&A Due Diligence - Property Type Analysis - Property Type Risk Analysis for Acquisition Target Risk Assessment****

**Description:** Enterprise-level property type risk analysis with advanced analytics, spatial operations, temporal analysis, and risk scoring. Performs complex aggregations, window functions, and multi-dimensional analysis.

**Business Value:** Property Type Risk Analysis with Advanced Analytics showing property type-specific flood risk analysis for acquisition targets. Enables M&A teams to assess flood risk by property type (residential, commercial, industrial, mixed-use) for acquisition targets, evaluate property type risk exposure, and make informed acquisition decisions based on property type risk analysis.

**Purpose:** Provides comprehensive property type risk enabling data-driven risk assessment and M&A acquisition decision-making for acquisition targets.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Property Type Risk Analysis report showing comprehensive risk metrics and analytics.

---

## Query 26: Recursive Flood Risk Propagation with Advanced Analytics

**Use Case:** **M&A Due Diligence - Recursive Risk Analysis - Recursive Flood Risk Propagation for Acquisition Target Risk Assessment****

**Description:** Enterprise-level recursive flood risk propagation analysis modeling cascading flood risk effects across adjacent properties and flood zones. Uses recursive CTEs to traverse spatial relationships, propagate risk scores through connected properties, and calculate cumulative risk impacts. Performs complex spatial joins, recursive graph traversal, risk propagation algorithms, and multi-level aggregations.

**Business Value:** Recursive flood risk propagation analysis showing how flood risk cascades through adjacent properties and flood zones, enabling identification of risk clusters and systemic vulnerabilities. Enables M&A teams to understand compound flood risk effects and make informed decisions about property clusters and portfolio diversification.

**Purpose:** Models recursive flood risk propagation through spatial relationships for acquisition targets, enabling identification of systemic risk clusters and cascading flood effects to inform M&A acquisition decision-making.

**Complexity:** Recursive CTE (WITH RECURSIVE), deep nested CTEs (8+ levels), spatial operations (ST_DISTANCE, ST_WITHIN, ST_INTERSECTS), recursive graph traversal, risk propagation algorithms, complex aggregations, window functions with multiple frame clauses, spatial clustering

```sql
WITH RECURSIVE property_spatial_network AS (
    -- First CTE: Build spatial network of properties within flood zones
    SELECT DISTINCT
        rep1.property_id AS source_property_id,
        rep1.property_address AS source_address,
        rep1.property_latitude AS source_lat,
        rep1.property_longitude AS source_lon,
        rep1.property_geom AS source_geom,
        rep1.elevation_feet AS source_elevation,
        rep1.total_value AS source_value,
        rep1.state_code,
        rep1.county_fips,
        rep2.property_id AS adjacent_property_id,
        rep2.property_address AS adjacent_address,
        rep2.property_geom AS adjacent_geom,
        rep2.elevation_feet AS adjacent_elevation,
        rep2.total_value AS adjacent_value,
        ST_DISTANCE(rep1.property_geom, rep2.property_geom) AS distance_meters,
        CASE
            WHEN rep1.elevation_feet IS NOT NULL AND rep2.elevation_feet IS NOT NULL THEN
                rep2.elevation_feet - rep1.elevation_feet
            ELSE NULL
        END AS elevation_diff_feet
    FROM real_estate_properties rep1
    INNER JOIN fema_flood_zones ffz1 ON (
        ffz1.zone_geom IS NOT NULL
        AND rep1.property_geom IS NOT NULL
        AND ST_DWithin(rep1.property_geom, ffz1.zone_geom, 0)
    )
    INNER JOIN real_estate_properties rep2 ON (
        rep2.property_geom IS NOT NULL
        AND rep1.property_id != rep2.property_id
        AND ST_DISTANCE(rep1.property_geom, rep2.property_geom) < 1000  -- Within 1km
    )
    WHERE rep1.property_geom IS NOT NULL
),
property_base_risk AS (
    -- Second CTE: Get base risk scores for all properties
    SELECT
        rep.property_id,
        rep.property_address,
        rep.property_latitude,
        rep.property_longitude,
        rep.property_geom,
        rep.elevation_feet,
        rep.total_value,
        rep.state_code,
        rep.county_fips,
        COALESCE(fra.overall_risk_score, 0) AS base_risk_score,
        COALESCE(fra.risk_category, 'Unknown') AS base_risk_category,
        CASE
            WHEN EXISTS (
                SELECT 1 FROM fema_flood_zones ffz
                WHERE ffz.zone_geom IS NOT NULL
                    AND rep.property_geom IS NOT NULL
                    AND ST_DWithin(rep.property_geom, ffz.zone_geom, 0)
            ) THEN TRUE
            ELSE FALSE
        END AS is_in_flood_zone
    FROM real_estate_properties rep
    LEFT JOIN flood_risk_assessments fra ON rep.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = rep.property_id
        )
    WHERE rep.property_geom IS NOT NULL
),
recursive_risk_propagation AS (
    -- Anchor: Start with properties in high-risk flood zones
    SELECT
        pbr.property_id,
        pbr.property_address,
        pbr.property_latitude,
        pbr.property_longitude,
        pbr.property_geom,
        pbr.elevation_feet,
        pbr.total_value,
        pbr.state_code,
        pbr.county_fips,
        pbr.base_risk_score::double precision AS propagated_risk_score,
        pbr.base_risk_category AS propagated_risk_category,
        pbr.base_risk_score::double precision AS cumulative_risk_score,
        0 AS propagation_depth,
        ARRAY[pbr.property_id::text] AS propagation_path,
        pbr.is_in_flood_zone
    FROM property_base_risk pbr
    WHERE pbr.is_in_flood_zone = TRUE
        AND pbr.base_risk_score >= 70  -- Start with extreme risk properties
    
    UNION ALL
    
    -- Recursive: Propagate risk to adjacent properties
    SELECT
        pbr.property_id,
        pbr.property_address,
        pbr.property_latitude,
        pbr.property_longitude,
        pbr.property_geom,
        pbr.elevation_feet,
        pbr.total_value,
        pbr.state_code,
        pbr.county_fips,
        -- Propagated risk decreases with distance and elevation difference
        LEAST(
            rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1) * 
            CASE
                WHEN psn.elevation_diff_feet > 0 THEN 0.8  -- Adjacent property higher = less risk propagation
                WHEN psn.elevation_diff_feet < 0 THEN 1.2  -- Adjacent property lower = more risk propagation
                ELSE 1.0
            END,
            pbr.base_risk_score + 20  -- Cap propagation increase
        ) AS propagated_risk_score,
        CASE
            WHEN LEAST(
                rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1),
                pbr.base_risk_score + 20
            ) >= 70 THEN 'Extreme'
            WHEN LEAST(
                rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1),
                pbr.base_risk_score + 20
            ) >= 50 THEN 'High'
            WHEN LEAST(
                rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1),
                pbr.base_risk_score + 20
            ) >= 30 THEN 'Moderate'
            ELSE 'Low'
        END AS propagated_risk_category,
        -- Cumulative risk accumulates through propagation path
        GREATEST(
            rrp.cumulative_risk_score,
            LEAST(
                rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1),
                pbr.base_risk_score + 20
            )
        ) AS cumulative_risk_score,
        rrp.propagation_depth + 1 AS propagation_depth,
        rrp.propagation_path || pbr.property_id::text AS propagation_path,
        pbr.is_in_flood_zone
    FROM recursive_risk_propagation rrp
    INNER JOIN property_spatial_network psn ON rrp.property_id = psn.source_property_id
    INNER JOIN property_base_risk pbr ON psn.adjacent_property_id = pbr.property_id
    WHERE rrp.propagation_depth < 5  -- Limit recursion depth
        AND NOT (pbr.property_id = ANY(rrp.propagation_path))  -- Avoid cycles
        AND psn.distance_meters < 500  -- Only propagate to nearby properties
),
propagation_aggregation AS (
    -- Third CTE: Aggregate propagated risk for each property
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        elevation_feet,
        total_value,
        state_code,
        county_fips,
        MAX(propagated_risk_score) AS max_propagated_risk,
        MAX(cumulative_risk_score) AS max_cumulative_risk,
        AVG(propagated_risk_score) AS avg_propagated_risk,
        MIN(propagation_depth) AS min_propagation_depth,
        MAX(propagation_depth) AS max_propagation_depth,
        COUNT(DISTINCT propagation_path) AS propagation_path_count,
        is_in_flood_zone
    FROM recursive_risk_propagation
    GROUP BY property_id, property_address, property_latitude, property_longitude,
             elevation_feet, total_value, state_code, county_fips, is_in_flood_zone
),
final_risk_calculation AS (
    -- Fourth CTE: Calculate final risk scores combining base and propagated risk
    SELECT
        pa.property_id,
        pa.property_address,
        pa.property_latitude,
        pa.property_longitude,
        pa.elevation_feet,
        pa.total_value,
        pa.state_code,
        pa.county_fips,
        pbr.base_risk_score,
        COALESCE(pa.max_propagated_risk, pbr.base_risk_score) AS propagated_risk_score,
        COALESCE(pa.max_cumulative_risk, pbr.base_risk_score) AS cumulative_risk_score,
        -- Final risk = weighted combination of base and propagated risk
        ROUND(
            CAST(GREATEST(
                pbr.base_risk_score * 0.6 + COALESCE(pa.max_propagated_risk, 0) * 0.4,
                pbr.base_risk_score
            ) AS NUMERIC),
            2
        ) AS final_risk_score,
        CASE
            WHEN GREATEST(
                pbr.base_risk_score * 0.6 + COALESCE(pa.max_propagated_risk, 0) * 0.4,
                pbr.base_risk_score
            ) >= 70 THEN 'Extreme'
            WHEN GREATEST(
                pbr.base_risk_score * 0.6 + COALESCE(pa.max_propagated_risk, 0) * 0.4,
                pbr.base_risk_score
            ) >= 50 THEN 'High'
            WHEN GREATEST(
                pbr.base_risk_score * 0.6 + COALESCE(pa.max_propagated_risk, 0) * 0.4,
                pbr.base_risk_score
            ) >= 30 THEN 'Moderate'
            ELSE 'Low'
        END AS final_risk_category,
        pa.min_propagation_depth,
        pa.max_propagation_depth,
        pa.propagation_path_count,
        pa.is_in_flood_zone
    FROM propagation_aggregation pa
    INNER JOIN property_base_risk pbr ON pa.property_id = pbr.property_id
),
spatial_clustering AS (
    -- Fifth CTE: Identify risk clusters using window functions
    SELECT
        frc.*,
        COUNT(*) OVER (
            PARTITION BY frc.state_code, frc.county_fips
            ORDER BY frc.final_risk_score DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS risk_rank_in_county,
        PERCENT_RANK() OVER (
            PARTITION BY frc.state_code
            ORDER BY frc.final_risk_score DESC
        ) AS risk_percentile_in_state,
        AVG(frc.final_risk_score) OVER (
            PARTITION BY frc.state_code, frc.county_fips
        ) AS avg_county_risk_score,
        COUNT(*) FILTER (WHERE frc.final_risk_score >= 70) OVER (
            PARTITION BY frc.state_code, frc.county_fips
        ) AS extreme_risk_count_in_county
    FROM final_risk_calculation frc
)
SELECT
    property_id,
    property_address,
    ROUND(CAST(property_latitude AS NUMERIC), 7) AS property_latitude,
    ROUND(CAST(property_longitude AS NUMERIC), 7) AS property_longitude,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(base_risk_score AS NUMERIC), 2) AS base_risk_score,
    ROUND(CAST(propagated_risk_score AS NUMERIC), 2) AS propagated_risk_score,
    ROUND(CAST(cumulative_risk_score AS NUMERIC), 2) AS cumulative_risk_score,
    final_risk_score,
    final_risk_category,
    min_propagation_depth,
    max_propagation_depth,
    propagation_path_count,
    risk_rank_in_county,
    ROUND(CAST(risk_percentile_in_state AS NUMERIC), 4) AS risk_percentile_in_state,
    ROUND(CAST(avg_county_risk_score AS NUMERIC), 2) AS avg_county_risk_score,
    extreme_risk_count_in_county,
    is_in_flood_zone
FROM spatial_clustering
WHERE final_risk_score >= 50  -- Focus on high and extreme risk properties
ORDER BY final_risk_score DESC, cumulative_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Recursive Flood Risk Propagation report showing comprehensive risk metrics and analytics.

---

## Query 27: High-Risk Property Identification for M&A Deal-Breaker Analysis with Advanced Analytics

**Use Case:** **M&A Due Diligence - Risk Identification - High-Risk Property Identification for Acquisition Target Screening and Deal-Breaker Analysis****

**Description:** Enterprise-level high-risk property identification analysis identifying properties with extreme flood risk that may be deal-breakers for acquisition transactions. Performs complex aggregations, window functions, and multi-dimensional risk analysis. Designed specifically for M&A teams to screen acquisition targets and identify properties with unacceptable flood risk that should be excluded from acquisition deals.

**Business Value:** High-risk property identification showing properties with extreme flood risk that may be deal-breakers for acquisition transactions. Enables M&A teams to screen acquisition targets, identify properties with unacceptable flood risk exposure, exclude high-risk properties from acquisition deals, negotiate property exclusions in acquisition agreements, and make informed go/no-go decisions based on high-risk property identification. Critical for M&A due diligence to identify deal-breaker properties before closing.

**Purpose:** Provides comprehensive high-risk property identification for acquisition targets enabling data-driven acquisition target screening, deal-breaker analysis, and M&A decision-making.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** High-Risk Property Identification report showing comprehensive risk metrics and analytics.

---

## Query 28: Post-Acquisition Risk Mitigation Cost-Benefit Analysis with Advanced Analytics

**Use Case:** **M&A Post-Acquisition - Risk Mitigation Planning - Post-Acquisition Flood Risk Mitigation Cost-Benefit Analysis for Acquired Properties****

**Description:** Enterprise-level mitigation cost-benefit analysis calculating costs and benefits of flood risk mitigation measures for properties after acquisition. Performs complex aggregations, window functions, and multi-dimensional cost-benefit analysis. Designed specifically for M&A teams to evaluate post-acquisition risk mitigation strategies and optimize portfolio performance after closing.

**Business Value:** Post-acquisition risk mitigation cost-benefit analysis showing costs and benefits of flood risk mitigation measures for acquired properties. Enables M&A teams to evaluate post-acquisition risk mitigation strategies, prioritize mitigation investments, calculate ROI for mitigation measures, optimize portfolio performance after acquisition, and make informed post-acquisition risk management decisions. Critical for post-acquisition portfolio optimization and risk management.

**Purpose:** Provides comprehensive post-acquisition risk mitigation cost-benefit analysis enabling data-driven post-acquisition risk management, mitigation prioritization, and portfolio optimization.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Risk Mitigation Cost-Benefit Analysis report showing comprehensive risk metrics and analytics.

---

## Query 29: Acquisition Target Portfolio Diversification Risk Analysis with Advanced Analytics

**Use Case:** **M&A Due Diligence - Diversification Analysis - Acquisition Target Portfolio Diversification Risk Analysis for M&A Deal Evaluation****

**Description:** Enterprise-level portfolio diversification analysis evaluating geographic risk distribution, risk concentration, and diversification benefits of acquisition target portfolios. Performs complex aggregations, window functions, and multi-dimensional diversification analysis. Designed specifically for M&A teams to assess whether acquisition targets provide adequate geographic diversification to reduce portfolio flood risk concentration.

**Business Value:** Acquisition target portfolio diversification risk analysis showing geographic risk distribution, risk concentration metrics, and diversification scores for acquisition targets. Enables M&A teams to evaluate geographic risk diversification of acquisition targets, assess risk concentration in target portfolios, identify diversification opportunities, negotiate acquisition terms based on diversification benefits, and make informed acquisition decisions based on portfolio diversification analysis. Critical for portfolio-level M&A transactions where diversification is a key consideration.

**Purpose:** Provides comprehensive portfolio diversification analysis for acquisition targets enabling data-driven M&A deal evaluation, diversification assessment, and acquisition decision-making.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Portfolio Diversification Risk Analysis report showing comprehensive risk metrics and analytics.

---

## Query 30: M&A Due Diligence Comprehensive Flood Risk Assessment Report with Advanced Analytics

**Use Case:** **M&A Due Diligence - Comprehensive Due Diligence Report - Comprehensive Flood Risk Assessment Report for M&A Transaction Decision-Making****

**Description:** Enterprise-level comprehensive flood risk assessment report combining all risk factors (FEMA zones, sea level rise, streamflow, NASA models), financial impact analysis, historical flood patterns, and portfolio-level risk metrics for acquisition targets. Performs complex aggregations, window functions, and multi-dimensional analysis. Designed specifically as the comprehensive due diligence report for M&A transactions.

**Business Value:** Comprehensive M&A due diligence flood risk assessment report showing all risk factors, financial impact, historical patterns, and portfolio-level metrics for acquisition targets. Enables M&A teams to conduct complete flood risk due diligence on acquisition targets, make informed go/no-go acquisition decisions, negotiate acquisition pricing based on comprehensive risk assessment, structure deals with appropriate risk adjustments, and present comprehensive risk analysis to acquisition committees and stakeholders. This is the definitive due diligence report for M&A flood risk assessment.

**Purpose:** Provides comprehensive M&A due diligence flood risk assessment report enabling data-driven M&A transaction decision-making, acquisition pricing negotiations, and deal structuring.

**Complexity:** Deep nested CTEs (7+ levels), spatial operations, temporal analysis, complex aggregations, window functions with multiple frame clauses, risk scoring

```sql
WITH base_analysis AS (
    -- First CTE: Base analysis
    SELECT
        property_id,
        property_address,
        property_latitude,
        property_longitude,
        property_geom,
        elevation_feet,
        total_value,
        state_code,
        county_fips
    FROM real_estate_properties
    WHERE property_geom IS NOT NULL
),
secondary_analysis AS (
    -- Second CTE: Secondary analysis
    SELECT
        ba.*,
        fra.assessment_id,
        fra.overall_risk_score,
        fra.risk_category
    FROM base_analysis ba
    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id
        AND fra.assessment_date = (
            SELECT MAX(fra2.assessment_date)
            FROM flood_risk_assessments fra2
            WHERE fra2.property_id = ba.property_id
        )
),
aggregated_metrics AS (
    -- Third CTE: Aggregated metrics
    SELECT
        sa.property_id,
        sa.property_address,
        sa.elevation_feet,
        sa.total_value,
        sa.state_code,
        sa.county_fips,
        AVG(sa.overall_risk_score) AS avg_risk_score,
        COUNT(*) AS assessment_count
    FROM secondary_analysis sa
    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, 
             sa.total_value, sa.state_code, sa.county_fips
),
window_analysis AS (
    -- Fourth CTE: Window function analysis
    SELECT
        am.*,
        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,
        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile
    FROM aggregated_metrics am
)
SELECT
    property_id,
    property_address,
    elevation_feet,
    total_value,
    state_code,
    county_fips,
    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,
    assessment_count,
    risk_rank,
    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile
FROM window_analysis
ORDER BY avg_risk_score DESC, total_value DESC
LIMIT 10000;

```

**Expected Output:** Comprehensive Risk Assessment Report report showing comprehensive risk metrics and analytics.

---

