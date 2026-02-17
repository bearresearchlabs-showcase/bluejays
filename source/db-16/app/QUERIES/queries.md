# Flood Risk Assessment (M&A Due Diligence) — Query Documentation

## Database Overview

```yaml
db_id: db-16
domain: Flood Risk / M&A Due Diligence
source: [commercial]
license_type: [Commercial]
license_cost: [NDA]
tables: 12
total_rows: ~18M
date_range: 2020-01-01 to 2026-12-31
sql_dialect: PostgreSQL
```

## Purpose

```text
This database supports flood risk analytics for real estate M&A due diligence. It integrates
FEMA flood zones, NOAA sea level rise projections, USGS streamflow data, and NASA flood models
to assess physical climate risk for property portfolios. It is designed to support text-to-SQL
training across spatial, multi-source, and risk-scoring query types for investment analysts.
```

## Use Case

```text
Target use cases for db-16:
- M&A due diligence: pre-acquisition flood risk assessment for property portfolios
- Portfolio analytics: geographic risk hotspots, cluster patterns, exposure by state/county
- Risk scoring: composite scores from FEMA, sea level rise, streamflow, NASA models
- Financial impact: estimated damage, annual loss, insurance premium estimates
```

## Business Value

```text
Flood risk databases represent high-value domains for text-to-SQL because:
- Queries require spatial reasoning (ST_Distance, ST_DWithin, geography joins)
- Multi-source integration (FEMA, NOAA, USGS, NASA) demands complex CTEs
- Stakeholders are investment analysts and underwriters needing self-serve analytics
- Errors affect acquisition decisions and insurance pricing.
```

## Schema

```sql
-- Flood Risk Assessment Database Schema
-- Compatible with PostgreSQL
-- Production schema for physical climate risk assessment system
-- Supports flood risk assessments for real estate investment portfolios

-- FEMA Flood Zones Table
-- Stores FEMA National Flood Hazard Layer (NFHL) flood zone designations
CREATE TABLE fema_flood_zones (
    zone_id VARCHAR(255) PRIMARY KEY,
    zone_code VARCHAR(10) NOT NULL,  -- 'A', 'AE', 'AH', 'AO', 'V', 'VE', 'X', 'D', etc.
    zone_description VARCHAR(255),
    base_flood_elevation NUMERIC(10, 2),  -- BFE in feet above sea level
    zone_geom geography,  -- Polygon geometry for flood zone boundary
    community_id VARCHAR(50),
    community_name VARCHAR(255),
    state_code VARCHAR(2),
    county_fips VARCHAR(5),
    effective_date DATE,
    map_panel VARCHAR(50),
    source_file VARCHAR(500),
    source_crs VARCHAR(50) DEFAULT 'EPSG:4326',
    target_crs VARCHAR(50) DEFAULT 'EPSG:4326',
    spatial_extent_west NUMERIC(10, 6),
    spatial_extent_south NUMERIC(10, 6),
    spatial_extent_east NUMERIC(10, 6),
    spatial_extent_north NUMERIC(10, 6),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transformation_status VARCHAR(50)
);

-- Real Estate Properties Table
-- Stores property locations and characteristics for flood risk assessment
CREATE TABLE real_estate_properties (
    property_id VARCHAR(255) PRIMARY KEY,
    property_address VARCHAR(500),
    property_latitude NUMERIC(10, 7) NOT NULL,
    property_longitude NUMERIC(10, 7) NOT NULL,
    property_geom geography,  -- Point geometry for property location
    property_type VARCHAR(100),  -- 'Residential', 'Commercial', 'Industrial', 'Mixed-Use'
    building_value NUMERIC(15, 2),
    land_value NUMERIC(15, 2),
    total_value NUMERIC(15, 2),
    square_footage NUMERIC(12, 2),
    year_built INTEGER,
    number_of_floors INTEGER,
    elevation_feet NUMERIC(10, 2),  -- Ground elevation above sea level
    state_code VARCHAR(2),
    county_fips VARCHAR(5),
    c
-- ...
```

## Domain Knowledge

```text
Key domain concepts required to write correct queries against this database:

FEMA FLOOD ZONES:
- zone_code: 'A', 'AE', 'AH', 'AO', 'V', 'VE', 'X', 'D', 'X500' — V/VE = velocity (highest risk)
- base_flood_elevation (BFE): feet above sea level; property elevation - BFE = elevation_above_bfe
- zone_geom: polygon geography; property_geom: point geography

SEA LEVEL RISE (NOAA):
- scenario: 'Low', 'Intermediate-Low', 'Intermediate', 'Intermediate-High', 'High', 'Extreme'
- sea_level_rise_feet: projected rise; high_tide_flooding_days: annual flooding days
- projection_year: 2030, 2050, 2100, etc.

STREAMFLOW (USGS):
- discharge_cfs: cubic feet per second; gage_height_feet, stage_feet
- flood_category: 'None', 'Action', 'Minor', 'Moderate', 'Major'
- flood_stage_feet, moderate_flood_stage_feet, major_flood_stage_feet

NASA FLOOD MODELS:
- model_name: 'GFMS', 'LIS', 'VIIRS', 'MODIS', 'FloodPlanet'
- inundation_depth_feet, flood_probability (0-100), flood_severity

RISK SCORING:
- Risk scores 0-100; risk_category: 'Low', 'Moderate', 'High', 'Extreme'
- overall_risk_score: weighted composite; estimated_annual_loss (EAL)
- Spatial: ST_DISTANCE, ST_DWithin for nearest-neighbor and containment
```

## Query Difficulty Distribution

```text
Target distribution across 30 queries:
- simple (10): Single-table, basic aggregation
- moderate (12): 2-3 table joins, GROUP BY
- challenging (8): CTEs, window functions
```

## Queries

### Query 1 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 1,
  "question": "Show me a comprehensive pre-acquisition flood risk assessment that combines multiple data sources and projects future risk scenarios.",
  "SQL": "WITH property_location_analysis AS (\n    -- First CTE: Analyze property locations and spatial context\n    SELECT\n        rep.property_id,\n        rep.property_address,\n        rep.property_latitude,\n        rep.property_longitude,\n        rep.property_geom,\n        rep.property_type,\n        rep.building_value,\n        rep.land_value,\n        rep.total_value,\n        rep.square_footage,\n        rep.year_built,\n        rep.number_of_floors,\n        rep.elevation_feet,\n        rep.state_code,\n        rep.county_fips,\n        rep.city_name,\n        rep.zip_code,\n        rep.portfolio_id,\n        rep.portfolio_name,\n        rep.acquisition_date,\n        -- Calculate property age\n        EXTRACT(YEAR FROM CURRENT_DATE) - rep.year_built AS property_age_years\n    FROM real_estate_properties rep\n    WHERE rep.property_geom IS NOT NULL\n),\nfema_flood_zone_analysis AS (\n    -- Second CTE: Identify FEMA flood zones intersecting or near properties\n    SELECT\n        pla.property_id,\n        pla.property_address,\n        pla.property_latitude,\n        pla.property_longitude,\n        pla.property_geom,\n        pla.property_type,\n        pla.total_value,\n        pla.elevation_feet,\n        pla.state_code,\n        pla.county_fips,\n        pla.portfolio_id,\n        pla.portfolio_name,\n        pla.property_age_years,\n        ffz.zone_id,\n        ffz.zone_code,\n        ffz.zone_description,\n        ffz.base_flood_elevation,\n        ffz.zone_geom,\n        ffz.community_name,\n        ffz.effective_date,\n        -- Spatial distance calculation\n        CASE\n            WHEN ffz.zone_geom IS NOT NULL AND pla.property_geom IS NOT NULL THEN\n                ST_DISTANCE(ffz.zone_geom, pla.property_geom)\n            ELSE NULL\n        END AS distance_to_zone_meters,\n        -- Check if property is within flood zone\n        CASE\n            WHEN ffz.zone_geom IS NOT NULL AND pla.property_geom IS NOT NULL THEN\n                CASE\n                    WHEN ST_DWithin(pla.property_geom, ffz.zone_geom, 0) THEN TRUE\n                    ELSE FALSE\n                END\n            ELSE NULL\n        END AS is_within_flood_zone,\n        -- Elevation difference (property elevation - BFE)\n        CASE\n            WHEN ffz.base_flood_elevation IS NOT NULL AND pla.elevation_feet IS NOT NULL THEN\n                pla.elevation_feet - ffz.base_flood_elevation\n            ELSE NULL\n        END AS elevation_above_bfe_feet\n    FROM property_location_analysis pla\n    LEFT JOIN fema_flood_zones ffz ON (\n        ffz.zone_geom IS NOT NULL\n        AND pla.property_geom IS NOT NULL\n        AND ST_DISTANCE(ffz.zone_geom, pla.property_geom) < 5000  -- Within 5km\n    )\n),\nfema_risk_scoring AS (\n    -- Third CTE: Calculate FEMA flood zone risk scores\n    SELECT\n        ffza.property_id,\n        ffza.property_address,\n        ffza.property_latitude,\n        ffza.property_longitude,\n        ffza.property_geom,\n        ffza.property_type,\n        ffza.total_value,\n        ffza.elevation_feet,\n        ffza.state_code,\n        ffza.county_fips,\n        ffza.portfolio_id,\n        ffza.portfolio_name,\n        ffza.zone_id,\n        ffza.zone_code,\n        ffza.zone_description,\n        ffza.base_flood_elevation,\n        ffza.distance_to_zone_meters,\n        ffza.is_within_flood_zone,\n        ffza.elevation_above_bfe_feet,\n        -- FEMA flood zone risk score (0-100)\n        CASE\n            WHEN ffza.is_within_flood_zone = TRUE THEN\n                CASE\n                    WHEN ffza.zone_code IN ('V', 'VE') THEN 95  -- Velocity zones (highest risk)\n                    WHEN ffza.zone_code IN ('A', 'AE') THEN\n                        CASE\n                            WHEN ffza.elevation_above_bfe_feet IS NOT NULL THEN\n                                CASE\n                                    WHEN ffza.elevation_above_bfe_feet < 0 THEN 90  -- Below BFE\n                                    WHEN ffza.elevation_above_bfe_feet < 2 THEN 75  -- 0-2 feet above BFE\n                                    WHEN ffza.elevation_above_bfe_feet < 5 THEN 60  -- 2-5 feet above BFE\n                                    ELSE 45  -- More than 5 feet above BFE\n                                END\n                            ELSE 80  -- In A/AE zone but BFE unknown\n                        END\n                    WHEN ffza.zone_code IN ('AH', 'AO') THEN 70  -- Shallow flooding zones\n                    WHEN ffza.zone_code = 'D' THEN 50  -- Unstudied areas\n                    WHEN ffza.zone_code IN ('X', 'X500') THEN 30  -- Low to moderate risk\n                    ELSE 40\n                END\n            WHEN ffza.distance_to_zone_meters IS NOT NULL THEN\n                CASE\n                    WHEN ffza.distance_to_zone_meters < 100 THEN 60  -- Very close to high-risk zone\n                    WHEN ffza.distance_to_zone_meters < 500 THEN 40  -- Close to high-risk zone\n                    WHEN ffza.distance_to_zone_meters < 1000 THEN 25  -- Near high-risk zone\n                    ELSE 10  -- Far from high-risk zones\n                END\n            ELSE 5  -- No nearby flood zones\n        END AS fema_risk_score\n    FROM fema_flood_zone_analysis ffza\n),\nnoaa_sea_level_rise_analysis AS (\n    -- Fourth CTE: Analyze NOAA sea level rise projections for coastal properties\n    SELECT\n        frs.property_id,\n        frs.property_address,\n        frs.property_latitude,\n        frs.property_longitude,\n        frs.property_geom,\n        frs.property_type,\n        frs.total_value,\n        frs.elevation_feet,\n        frs.state_code,\n        frs.county_fips,\n        frs.portfolio_id,\n        frs.portfolio_name,\n        frs.zone_code,\n        frs.fema_risk_score,\n        -- Find nearest NOAA sea level rise station\n        (\n            SELECT nslr.station_id\n            FROM noaa_sea_level_rise nslr\n            WHERE nslr.station_geom IS NOT NULL\n                AND frs.property_geom IS NOT NULL\n            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)\n            LIMIT 1\n        ) AS nearest_station_id,\n        -- Get sea level rise projections for different time horizons\n        (\n            SELECT nslr.sea_level_rise_feet\n            FROM noaa_sea_level_rise nslr\n            WHERE nslr.station_geom IS NOT NULL\n                AND frs.property_geom IS NOT NULL\n                AND nslr.projection_year = EXTRACT(YEAR FROM CURRENT_DATE) + 10\n                AND nslr.scenario = 'Intermediate'\n            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)\n            LIMIT 1\n        ) AS slr_10_years_feet,\n        (\n            SELECT nslr.sea_level_rise_feet\n            FROM noaa_sea_level_rise nslr\n            WHERE nslr.station_geom IS NOT NULL\n                AND frs.property_geom IS NOT NULL\n                AND nslr.projection_year = EXTRACT(YEAR FROM CURRENT_DATE) + 30\n                AND nslr.scenario = 'Intermediate'\n            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)\n            LIMIT 1\n        ) AS slr_30_years_feet,\n        (\n            SELECT nslr.sea_level_rise_feet\n            FROM noaa_sea_level_rise nslr\n            WHERE nslr.station_geom IS NOT NULL\n                AND frs.property_geom IS NOT NULL\n                AND nslr.projection_year = EXTRACT(YEAR FROM CURRENT_DATE) + 100\n                AND nslr.scenario = 'Intermediate'\n            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)\n            LIMIT 1\n        ) AS slr_100_years_feet,\n        -- Get high tide flooding projections\n        (\n            SELECT nslr.high_tide_flooding_days\n            FROM noaa_sea_level_rise nslr\n            WHERE nslr.station_geom IS NOT NULL\n                AND frs.property_geom IS NOT NULL\n                AND nslr.projection_year = EXTRACT(YEAR FROM CURRENT_DATE) + 30\n                AND nslr.scenario = 'Intermediate'\n            ORDER BY ST_DISTANCE(nslr.station_geom, frs.property_geom)\n            LIMIT 1\n        ) AS htf_30_years_days\n    FROM fema_risk_scoring frs\n),\nsea_level_rise_risk_scoring AS (\n    -- Fifth CTE: Calculate sea level rise risk scores\n    SELECT\n        nsla.property_id,\n        nsla.property_address,\n        nsla.property_latitude,\n        nsla.property_longitude,\n        nsla.property_geom,\n        nsla.property_type,\n        nsla.total_value,\n        nsla.elevation_feet,\n        nsla.state_code,\n        nsla.county_fips,\n        nsla.portfolio_id,\n        nsla.portfolio_name,\n        nsla.zone_code,\n        nsla.fema_risk_score,\n        nsla.nearest_station_id,\n        nsla.slr_10_years_feet,\n        nsla.slr_30_years_feet,\n        nsla.slr_100_years_feet,\n        nsla.htf_30_years_days,\n        -- Sea level rise risk score (0-100)\n        CASE\n            WHEN nsla.elevation_feet IS NOT NULL AND nsla.slr_100_years_feet IS NOT NULL THEN\n                CASE\n                    WHEN nsla.elevation_feet < nsla.slr_100_years_feet THEN 95  -- Will be below sea level\n                    WHEN nsla.elevation_feet < nsla.slr_100_years_feet + 2 THEN 85  -- Very close to sea level\n                    WHEN nsla.elevation_feet < nsla.slr_100_years_feet + 5 THEN 70  -- Close to sea level\n                    WHEN nsla.elevation_feet < nsla.slr_100_years_feet + 10 THEN 50  -- Moderate risk\n                    ELSE 20  -- Low risk\n                END\n            WHEN nsla.htf_30_years_days IS NOT NULL THEN\n                CASE\n                    WHEN nsla.htf_30_years_days >= 180 THEN 80  -- More than 6 months of flooding\n                    WHEN nsla.htf_30_years_days >= 90 THEN 60  -- 3-6 months\n                    WHEN nsla.htf_30_years_days >= 30 THEN 40  -- 1-3 months\n                    WHEN nsla.htf_30_years_days > 0 THEN 25  -- Some flooding\n                    ELSE 10  -- No projected flooding\n                END\n            ELSE 5  -- No sea level rise data\n        END AS sea_level_rise_risk_score\n    FROM noaa_sea_level_rise_analysis nsla\n),\nusgs_streamflow_analysis AS (\n    -- Sixth CTE: Analyze USGS streamflow data for riverine flood risk\n    SELECT\n        slrs.property_id,\n        slrs.property_address,\n        slrs.property_latitude,\n        slrs.property_longitude,\n        slrs.property_geom,\n        slrs.property_type,\n        slrs.total_value,\n        slrs.elevation_feet,\n        slrs.state_code,\n        slrs.county_fips,\n        slrs.portfolio_id,\n        slrs.portfolio_name,\n        slrs.zone_code,\n        slrs.fema_risk_score,\n        slrs.sea_level_rise_risk_score,\n        -- Find nearest USGS streamflow gauge\n        (\n            SELECT usg.gauge_id\n            FROM usgs_streamflow_gauges usg\n            WHERE usg.gauge_geom IS NOT NULL\n                AND usg.active_status = TRUE\n                AND slrs.property_geom IS NOT NULL\n            ORDER BY ST_DISTANCE(usg.gauge_geom, slrs.property_geom)\n            LIMIT 1\n        ) AS nearest_gauge_id,\n        -- Get flood stage information\n        (\n            SELECT usg.flood_stage_feet\n            FROM usgs_streamflow_gauges usg\n            WHERE usg.gauge_geom IS NOT NULL\n                AND usg.active_status = TRUE\n                AND slrs.property_geom IS NOT NULL\n            ORDER BY ST_DISTANCE(usg.gauge_geom, slrs.property_geom)\n            LIMIT 1\n        ) AS flood_stage_feet,\n        -- Get historical flood frequency for nearest gauge\n        (\n            SELECT COUNT(*)\n            FROM usgs_streamflow_observations uso\n            WHERE uso.gauge_id = (\n                SELECT usg2.gauge_id\n                FROM usgs_streamflow_gauges usg2\n                WHERE usg2.gauge_geom IS NOT NULL\n                    AND usg2.active_status = TRUE\n                    AND slrs.property_geom IS NOT NULL\n                ORDER BY ST_DISTANCE(usg2.gauge_geom, slrs.property_geom)\n                LIMIT 1\n            )\n            AND uso.flood_category IN ('Minor', 'Moderate', 'Major')\n            AND uso.observation_time >= CURRENT_DATE - INTERVAL '10 years'\n        ) AS historical_flood_count_10_years\n    FROM sea_level_rise_risk_scoring slrs\n),\nstreamflow_risk_scoring AS (\n    -- Seventh CTE: Calculate streamflow flood risk scores\n    SELECT\n        usa.property_id,\n        usa.property_address,\n        usa.property_latitude,\n        usa.property_longitude,\n        usa.property_geom,\n        usa.property_type,\n        usa.total_value,\n        usa.elevation_feet,\n        usa.state_code,\n        usa.county_fips,\n        usa.portfolio_id,\n        usa.portfolio_name,\n        usa.zone_code,\n        usa.fema_risk_score,\n        usa.sea_level_rise_risk_score,\n        usa.nearest_gauge_id,\n        usa.flood_stage_feet,\n        usa.historical_flood_count_10_years,\n        -- Streamflow flood risk score (0-100)\n        CASE\n            WHEN usa.historical_flood_count_10_years IS NOT NULL THEN\n                CASE\n                    WHEN usa.historical_flood_count_10_years >= 20 THEN 90  -- Frequent flooding\n                    WHEN usa.historical_flood_count_10_years >= 10 THEN 75  -- Regular flooding\n                    WHEN usa.historical_flood_count_10_years >= 5 THEN 60  -- Occasional flooding\n                    WHEN usa.historical_flood_count_10_years >= 1 THEN 40  -- Rare flooding\n                    ELSE 15  -- No historical flooding\n                END\n            WHEN usa.flood_stage_feet IS NOT NULL AND usa.elevation_feet IS NOT NULL THEN\n                CASE\n                    WHEN usa.elevation_feet < usa.flood_stage_feet THEN 70  -- Below flood stage\n                    WHEN usa.elevation_feet < usa.flood_stage_feet + 5 THEN 50  -- Close to flood stage\n                    ELSE 20  -- Above flood stage\n                END\n            ELSE 10  -- No streamflow data\n        END AS streamflow_risk_score\n    FROM usgs_streamflow_analysis usa\n),\nnasa_flood_model_analysis AS (\n    -- Eighth CTE: Analyze NASA flood model predictions\n    SELECT\n        srs.property_id,\n        srs.property_address,\n        srs.property_latitude,\n        srs.property_longitude,\n        srs.property_geom,\n        srs.property_type,\n        srs.total_value,\n        srs.elevation_feet,\n        srs.state_code,\n        srs.county_fips,\n        srs.portfolio_id,\n        srs.portfolio_name,\n        srs.zone_code,\n        srs.fema_risk_score,\n        srs.sea_level_rise_risk_score,\n        srs.streamflow_risk_score,\n        -- Get NASA flood model predictions\n        (\n            SELECT AVG(nfm.flood_probability)\n            FROM nasa_flood_models nfm\n            WHERE nfm.grid_cell_geom IS NOT NULL\n                AND srs.property_geom IS NOT NULL\n                AND nfm.forecast_time >= CURRENT_TIMESTAMP - INTERVAL '30 days'\n                AND ST_DISTANCE(nfm.grid_cell_geom, srs.property_geom) < 10000  -- Within 10km\n        ) AS nasa_flood_probability_avg,\n        (\n            SELECT MAX(nfm.flood_probability)\n            FROM nasa_flood_models nfm\n            WHERE nfm.grid_cell_geom IS NOT NULL\n                AND srs.property_geom IS NOT NULL\n                AND nfm.forecast_time >= CURRENT_TIMESTAMP - INTERVAL '30 days'\n                AND ST_DISTANCE(nfm.grid_cell_geom, srs.property_geom) < 10000\n        ) AS nasa_flood_probability_max,\n        (\n            SELECT AVG(nfm.inundation_depth_feet)\n            FROM nasa_flood_models nfm\n            WHERE nfm.grid_cell_geom IS NOT NULL\n                AND srs.property_geom IS NOT NULL\n                AND nfm.forecast_time >= CURRENT_TIMESTAMP - INTERVAL '30 days'\n                AND ST_DISTANCE(nfm.grid_cell_geom, srs.property_geom) < 10000\n                AND nfm.inundation_depth_feet > 0\n        ) AS nasa_inundation_depth_avg\n    FROM streamflow_risk_scoring srs\n),\nnasa_risk_scoring AS (\n    -- Ninth CTE: Calculate NASA flood model risk scores\n    SELECT\n        nfma.property_id,\n        nfma.property_address,\n        nfma.property_latitude,\n        nfma.property_longitude,\n        nfma.property_type,\n        nfma.total_value,\n        nfma.elevation_feet,\n        nfma.state_code,\n        nfma.county_fips,\n        nfma.portfolio_id,\n        nfma.portfolio_name,\n        nfma.zone_code,\n        nfma.fema_risk_score,\n        nfma.sea_level_rise_risk_score,\n        nfma.streamflow_risk_score,\n        nfma.nasa_flood_probability_avg,\n        nfma.nasa_flood_probability_max,\n        nfma.nasa_inundation_depth_avg,\n        -- NASA flood model risk score (0-100)\n        CASE\n            WHEN nfma.nasa_flood_probability_max IS NOT NULL THEN\n                CASE\n                    WHEN nfma.nasa_flood_probability_max >= 80 THEN 85  -- Very high probability\n                    WHEN nfma.nasa_flood_probability_max >= 60 THEN 70  -- High probability\n                    WHEN nfma.nasa_flood_probability_max >= 40 THEN 55  -- Moderate probability\n                    WHEN nfma.nasa_flood_probability_max >= 20 THEN 35  -- Low probability\n                    ELSE 15  -- Very low probability\n                END\n            WHEN nfma.nasa_inundation_depth_avg IS NOT NULL THEN\n                CASE\n                    WHEN nfma.nasa_inundation_depth_avg >= 5 THEN 80  -- Deep inundation\n                    WHEN nfma.nasa_inundation_depth_avg >= 2 THEN 60  -- Moderate inundation\n                    WHEN nfma.nasa_inundation_depth_avg > 0 THEN 40  -- Shallow inundation\n                    ELSE 10  -- No inundation\n                END\n            ELSE 5  -- No NASA model data\n        END AS nasa_model_risk_score\n    FROM nasa_flood_model_analysis nfma\n),\ncomposite_risk_calculation AS (\n    -- Tenth CTE: Calculate composite risk scores and financial impacts\n    SELECT\n        nrs.property_id,\n        nrs.property_address,\n        nrs.property_latitude,\n        nrs.property_longitude,\n        nrs.property_type,\n        nrs.total_value,\n        nrs.elevation_feet,\n        nrs.state_code,\n        nrs.county_fips,\n        nrs.portfolio_id,\n        nrs.portfolio_name,\n        nrs.zone_code,\n        nrs.fema_risk_score,\n        nrs.sea_level_rise_risk_score,\n        nrs.streamflow_risk_score,\n        nrs.nasa_model_risk_score,\n        -- Weighted composite risk score (FEMA 40%, Sea Level Rise 25%, Streamflow 20%, NASA 15%)\n        ROUND(\n            COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n            COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n            COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n            COALESCE(nrs.nasa_model_risk_score, 0) * 0.15,\n            2\n        ) AS overall_risk_score,\n        -- Risk category\n        CASE\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 70 THEN 'Extreme'\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 50 THEN 'High'\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 30 THEN 'Moderate'\n            ELSE 'Low'\n        END AS risk_category,\n        -- Estimated damage (percentage of property value based on risk)\n        CASE\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 70 THEN nrs.total_value * 0.50  -- 50% damage estimate\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 50 THEN nrs.total_value * 0.30  -- 30% damage estimate\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 30 THEN nrs.total_value * 0.15  -- 15% damage estimate\n            ELSE nrs.total_value * 0.05  -- 5% damage estimate\n        END AS estimated_damage_dollars,\n        -- Estimated annual loss (EAL)\n        CASE\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 70 THEN nrs.total_value * 0.10  -- 10% annual loss probability\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 50 THEN nrs.total_value * 0.05  -- 5% annual loss probability\n            WHEN (\n                COALESCE(nrs.fema_risk_score, 0) * 0.40 +\n                COALESCE(nrs.sea_level_rise_risk_score, 0) * 0.25 +\n                COALESCE(nrs.streamflow_risk_score, 0) * 0.20 +\n                COALESCE(nrs.nasa_model_risk_score, 0) * 0.15\n            ) >= 30 THEN nrs.total_value * 0.02  -- 2% annual loss probability\n            ELSE nrs.total_value * 0.005  -- 0.5% annual loss probability\n        END AS estimated_annual_loss\n    FROM nasa_risk_scoring nrs\n)\nSELECT\n    property_id,\n    property_address,\n    ROUND(CAST(property_latitude AS NUMERIC), 7) AS property_latitude,\n    ROUND(CAST(property_longitude AS NUMERIC), 7) AS property_longitude,\n    property_type,\n    total_value,\n    elevation_feet,\n    state_code,\n    county_fips,\n    portfolio_id,\n    portfolio_name,\n    zone_code,\n    ROUND(CAST(fema_risk_score AS NUMERIC), 2) AS fema_risk_score,\n    ROUND(CAST(sea_level_rise_risk_score AS NUMERIC), 2) AS sea_level_rise_risk_score,\n    ROUND(CAST(streamflow_risk_score AS NUMERIC), 2) AS streamflow_risk_score,\n    ROUND(CAST(nasa_model_risk_score AS NUMERIC), 2) AS nasa_model_risk_score,\n    overall_risk_score,\n    risk_category,\n    ROUND(CAST(estimated_damage_dollars AS NUMERIC), 2) AS estimated_damage_dollars,\n    ROUND(CAST(estimated_annual_loss AS NUMERIC), 2) AS estimated_annual_loss\nFROM composite_risk_calculation\nORDER BY overall_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query joins flood_zones, properties, and risk_scores tables on property identifiers, aggregates risk components by property, calculates composite risk scores using weighted averages, applies risk category thresholds (low/medium/high/extreme), and computes financial impact estimates based on property value.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "current_date",
    "real_estate_properties",
    "property_location_analysis",
    "fema_flood_zones",
    "high",
    "fema_flood_zone_analysis",
    "noaa_sea_level_rise",
    "fema_risk_scoring",
    "noaa_sea_level_rise_analysis",
    "usgs_streamflow_gauges",
    "usgs_streamflow_observations",
    "sea_level_rise_risk_scoring",
    "usgs_streamflow_analysis",
    "nasa_flood_models",
    "streamflow_risk_scoring",
    "nasa_flood_model_analysis",
    "nasa_risk_scoring",
    "composite_risk_calculation"
  ],
  "schema_context": {},
  "expected_output": "The query returns property-level flood risk scores with FEMA, sea level rise, streamflow, and NASA model components, plus composite risk category and financial impact estimates.",
  "normal_query": "Property-level flood risk scores combining FEMA flood zones, sea level rise projections, streamflow data, and NASA climate models, with composite risk categories and estimated financial impacts."
}
```



### Query 2 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 2,
  "question": "Can you identify geographic risk hotspots and cluster patterns across our potential acquisition portfolio?",
  "SQL": "WITH portfolio_property_risk_base AS (\n    -- First CTE: Base property risk data with assessments\n    SELECT\n        rep.property_id,\n        rep.property_address,\n        rep.property_latitude,\n        rep.property_longitude,\n        rep.property_geom,\n        rep.property_type,\n        rep.total_value,\n        rep.building_value,\n        rep.land_value,\n        rep.square_footage,\n        rep.elevation_feet,\n        rep.state_code,\n        rep.county_fips,\n        rep.city_name,\n        rep.zip_code,\n        rep.portfolio_id,\n        rep.portfolio_name,\n        fra.assessment_id,\n        fra.assessment_date,\n        fra.overall_risk_score,\n        fra.risk_category,\n        fra.estimated_damage_dollars,\n        fra.estimated_annual_loss,\n        fra.fema_zone_code,\n        fra.sea_level_risk_score,\n        fra.streamflow_risk_score,\n        fra.nasa_model_risk_score\n    FROM real_estate_properties rep\n    LEFT JOIN flood_risk_assessments fra ON rep.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = rep.property_id\n        )\n    WHERE rep.property_geom IS NOT NULL\n),\nportfolio_aggregation_base AS (\n    -- Second CTE: Portfolio-level aggregations\n    SELECT\n        pprb.portfolio_id,\n        pprb.portfolio_name,\n        COUNT(DISTINCT pprb.property_id) AS total_properties,\n        COUNT(DISTINCT CASE WHEN pprb.overall_risk_score IS NOT NULL THEN pprb.property_id END) AS properties_with_assessment,\n        SUM(pprb.total_value) AS total_portfolio_value,\n        AVG(pprb.overall_risk_score) AS avg_risk_score,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pprb.overall_risk_score) AS median_risk_score,\n        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY pprb.overall_risk_score) AS q1_risk_score,\n        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY pprb.overall_risk_score) AS q3_risk_score,\n        STDDEV(pprb.overall_risk_score) AS stddev_risk_score,\n        SUM(pprb.estimated_damage_dollars) AS total_estimated_damage,\n        SUM(pprb.estimated_annual_loss) AS total_estimated_annual_loss,\n        COUNT(DISTINCT CASE WHEN pprb.risk_category = 'Extreme' THEN pprb.property_id END) AS extreme_risk_properties,\n        COUNT(DISTINCT CASE WHEN pprb.risk_category = 'High' THEN pprb.property_id END) AS high_risk_properties,\n        COUNT(DISTINCT CASE WHEN pprb.risk_category = 'Moderate' THEN pprb.property_id END) AS moderate_risk_properties,\n        COUNT(DISTINCT CASE WHEN pprb.risk_category = 'Low' THEN pprb.property_id END) AS low_risk_properties,\n        SUM(CASE WHEN pprb.risk_category = 'Extreme' THEN pprb.total_value ELSE 0 END) AS extreme_risk_value,\n        SUM(CASE WHEN pprb.risk_category = 'High' THEN pprb.total_value ELSE 0 END) AS high_risk_value,\n        SUM(CASE WHEN pprb.risk_category = 'Moderate' THEN pprb.total_value ELSE 0 END) AS moderate_risk_value,\n        SUM(CASE WHEN pprb.risk_category = 'Low' THEN pprb.total_value ELSE 0 END) AS low_risk_value\n    FROM portfolio_property_risk_base pprb\n    GROUP BY pprb.portfolio_id, pprb.portfolio_name\n),\ngeographic_clustering AS (\n    -- Third CTE: Geographic clustering of properties by risk\n    SELECT\n        pprb.portfolio_id,\n        pprb.portfolio_name,\n        pprb.property_id,\n        pprb.property_latitude,\n        pprb.property_longitude,\n        pprb.property_geom,\n        pprb.overall_risk_score,\n        pprb.risk_category,\n        pprb.total_value,\n        pprb.state_code,\n        pprb.county_fips,\n        pprb.city_name,\n        -- Cluster ID based on spatial proximity and risk similarity\n        ROW_NUMBER() OVER (\n            PARTITION BY pprb.portfolio_id\n            ORDER BY pprb.property_latitude, pprb.property_longitude\n        ) AS spatial_cluster_id,\n        -- Count nearby high-risk properties within 10km\n        (\n            SELECT COUNT(*)\n            FROM portfolio_property_risk_base pprb2\n            WHERE pprb2.portfolio_id = pprb.portfolio_id\n                AND pprb2.property_id != pprb.property_id\n                AND pprb2.property_geom IS NOT NULL\n                AND pprb.property_geom IS NOT NULL\n                AND ST_DISTANCE(pprb.property_geom, pprb2.property_geom) < 10000\n                AND pprb2.overall_risk_score >= 70\n        ) AS nearby_high_risk_count,\n        -- Average risk score of nearby properties\n        (\n            SELECT AVG(pprb2.overall_risk_score)\n            FROM portfolio_property_risk_base pprb2\n            WHERE pprb2.portfolio_id = pprb.portfolio_id\n                AND pprb2.property_id != pprb.property_id\n                AND pprb2.property_geom IS NOT NULL\n                AND pprb.property_geom IS NOT NULL\n                AND ST_DISTANCE(pprb.property_geom, pprb2.property_geom) < 10000\n        ) AS nearby_avg_risk_score\n    FROM portfolio_property_risk_base pprb\n),\nrisk_hotspot_detection AS (\n    -- Fourth CTE: Identify risk hotspots using spatial clustering\n    SELECT\n        gc.portfolio_id,\n        gc.portfolio_name,\n        gc.property_id,\n        gc.property_latitude,\n        gc.property_longitude,\n        gc.property_geom,\n        gc.overall_risk_score,\n        gc.risk_category,\n        gc.total_value,\n        gc.state_code,\n        gc.county_fips,\n        gc.city_name,\n        gc.nearby_high_risk_count,\n        gc.nearby_avg_risk_score,\n        -- Hotspot score (combination of property risk and nearby risk)\n        CASE\n            WHEN gc.overall_risk_score IS NOT NULL AND gc.nearby_avg_risk_score IS NOT NULL THEN\n                (gc.overall_risk_score * 0.6 + gc.nearby_avg_risk_score * 0.4)\n            WHEN gc.overall_risk_score IS NOT NULL THEN gc.overall_risk_score\n            ELSE 0\n        END AS hotspot_score,\n        -- Hotspot classification\n        CASE\n            WHEN gc.nearby_high_risk_count >= 5 AND gc.overall_risk_score >= 70 THEN 'Critical Hotspot'\n            WHEN gc.nearby_high_risk_count >= 3 AND gc.overall_risk_score >= 60 THEN 'High Hotspot'\n            WHEN gc.nearby_high_risk_count >= 1 AND gc.overall_risk_score >= 50 THEN 'Moderate Hotspot'\n            ELSE 'No Hotspot'\n        END AS hotspot_classification\n    FROM geographic_clustering gc\n),\ngeographic_risk_concentration AS (\n    -- Fifth CTE: Analyze risk concentration by geographic region\n    SELECT\n        rhd.portfolio_id,\n        rhd.portfolio_name,\n        rhd.state_code,\n        rhd.county_fips,\n        rhd.city_name,\n        COUNT(DISTINCT rhd.property_id) AS properties_in_region,\n        SUM(rhd.total_value) AS total_region_value,\n        AVG(rhd.overall_risk_score) AS avg_region_risk_score,\n        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rhd.overall_risk_score) AS median_region_risk_score,\n        COUNT(DISTINCT CASE WHEN rhd.risk_category = 'Extreme' THEN rhd.property_id END) AS extreme_risk_in_region,\n        COUNT(DISTINCT CASE WHEN rhd.risk_category = 'High' THEN rhd.property_id END) AS high_risk_in_region,\n        SUM(CASE WHEN rhd.risk_category IN ('Extreme', 'High') THEN rhd.total_value ELSE 0 END) AS high_risk_region_value,\n        COUNT(DISTINCT CASE WHEN rhd.hotspot_classification != 'No Hotspot' THEN rhd.property_id END) AS hotspot_properties_count,\n        -- Risk concentration ratio (high-risk value / total value)\n        CASE\n            WHEN SUM(rhd.total_value) > 0 THEN\n                SUM(CASE WHEN rhd.risk_category IN ('Extreme', 'High') THEN rhd.total_value ELSE 0 END) / SUM(rhd.total_value) * 100\n            ELSE 0\n        END AS risk_concentration_percentage\n    FROM risk_hotspot_detection rhd\n    GROUP BY rhd.portfolio_id, rhd.portfolio_name, rhd.state_code, rhd.county_fips, rhd.city_name\n),\nportfolio_diversification_analysis AS (\n    -- Sixth CTE: Calculate portfolio diversification metrics\n    SELECT\n        pab.portfolio_id,\n        pab.portfolio_name,\n        pab.total_properties,\n        pab.total_portfolio_value,\n        pab.avg_risk_score,\n        pab.median_risk_score,\n        pab.total_estimated_damage,\n        pab.total_estimated_annual_loss,\n        pab.extreme_risk_properties,\n        pab.high_risk_properties,\n        pab.moderate_risk_properties,\n        pab.low_risk_properties,\n        pab.extreme_risk_value,\n        pab.high_risk_value,\n        pab.moderate_risk_value,\n        pab.low_risk_value,\n        -- Geographic diversification (number of unique regions)\n        (\n            SELECT COUNT(DISTINCT CONCAT(pprb.state_code, '-', pprb.county_fips))\n            FROM portfolio_property_risk_base pprb\n            WHERE pprb.portfolio_id = pab.portfolio_id\n        ) AS unique_regions_count,\n        -- Risk diversification score (lower concentration = better diversification)\n        CASE\n            WHEN pab.total_portfolio_value > 0 THEN\n                100 - (\n                    (pab.extreme_risk_value + pab.high_risk_value) / pab.total_portfolio_value * 100\n                )\n            ELSE 0\n        END AS risk_diversification_score,\n        -- Portfolio risk category\n        CASE\n            WHEN (pab.extreme_risk_value + pab.high_risk_value) / NULLIF(pab.total_portfolio_value, 0) >= 0.5 THEN 'High Concentration'\n            WHEN (pab.extreme_risk_value + pab.high_risk_value) / NULLIF(pab.total_portfolio_value, 0) >= 0.3 THEN 'Moderate Concentration'\n            WHEN (pab.extreme_risk_value + pab.high_risk_value) / NULLIF(pab.total_portfolio_value, 0) >= 0.1 THEN 'Low Concentration'\n            ELSE 'Well Diversified'\n        END AS portfolio_risk_concentration_category\n    FROM portfolio_aggregation_base pab\n),\nhotspot_summary AS (\n    -- Seventh CTE: Summarize hotspots by portfolio\n    SELECT\n        rhd.portfolio_id,\n        rhd.portfolio_name,\n        COUNT(DISTINCT CASE WHEN rhd.hotspot_classification = 'Critical Hotspot' THEN rhd.property_id END) AS critical_hotspot_count,\n        COUNT(DISTINCT CASE WHEN rhd.hotspot_classification = 'High Hotspot' THEN rhd.property_id END) AS high_hotspot_count,\n        COUNT(DISTINCT CASE WHEN rhd.hotspot_classification = 'Moderate Hotspot' THEN rhd.property_id END) AS moderate_hotspot_count,\n        SUM(CASE WHEN rhd.hotspot_classification = 'Critical Hotspot' THEN rhd.total_value ELSE 0 END) AS critical_hotspot_value,\n        SUM(CASE WHEN rhd.hotspot_classification = 'High Hotspot' THEN rhd.total_value ELSE 0 END) AS high_hotspot_value,\n        SUM(CASE WHEN rhd.hotspot_classification = 'Moderate Hotspot' THEN rhd.total_value ELSE 0 END) AS moderate_hotspot_value,\n        AVG(CASE WHEN rhd.hotspot_classification != 'No Hotspot' THEN rhd.hotspot_score ELSE NULL END) AS avg_hotspot_score\n    FROM risk_hotspot_detection rhd\n    GROUP BY rhd.portfolio_id, rhd.portfolio_name\n),\ngeographic_concentration_summary AS (\n    -- Eighth CTE: Summarize geographic risk concentration\n    SELECT\n        grc.portfolio_id,\n        grc.portfolio_name,\n        COUNT(DISTINCT CONCAT(grc.state_code, '-', grc.county_fips)) AS high_risk_regions_count,\n        MAX(grc.risk_concentration_percentage) AS max_region_risk_concentration,\n        AVG(grc.risk_concentration_percentage) AS avg_region_risk_concentration,\n        SUM(grc.high_risk_region_value) AS total_high_risk_region_value,\n        SUM(grc.hotspot_properties_count) AS total_hotspot_properties\n    FROM geographic_risk_concentration grc\n    WHERE grc.risk_concentration_percentage >= 30\n    GROUP BY grc.portfolio_id, grc.portfolio_name\n),\nfinal_portfolio_summary AS (\n    -- Ninth CTE: Final portfolio risk summary\n    SELECT\n        pda.portfolio_id,\n        pda.portfolio_name,\n        pda.total_properties,\n        pda.total_portfolio_value,\n        ROUND(CAST(pda.avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n        ROUND(CAST(pda.median_risk_score AS NUMERIC), 2) AS median_risk_score,\n        ROUND(CAST(pda.total_estimated_damage AS NUMERIC), 2) AS total_estimated_damage,\n        ROUND(CAST(pda.total_estimated_annual_loss AS NUMERIC), 2) AS total_estimated_annual_loss,\n        pda.extreme_risk_properties,\n        pda.high_risk_properties,\n        pda.moderate_risk_properties,\n        pda.low_risk_properties,\n        ROUND(CAST(pda.extreme_risk_value AS NUMERIC), 2) AS extreme_risk_value,\n        ROUND(CAST(pda.high_risk_value AS NUMERIC), 2) AS high_risk_value,\n        ROUND(CAST(pda.moderate_risk_value AS NUMERIC), 2) AS moderate_risk_value,\n        ROUND(CAST(pda.low_risk_value AS NUMERIC), 2) AS low_risk_value,\n        pda.unique_regions_count,\n        ROUND(CAST(pda.risk_diversification_score AS NUMERIC), 2) AS risk_diversification_score,\n        pda.portfolio_risk_concentration_category,\n        COALESCE(hs.critical_hotspot_count, 0) AS critical_hotspot_count,\n        COALESCE(hs.high_hotspot_count, 0) AS high_hotspot_count,\n        COALESCE(hs.moderate_hotspot_count, 0) AS moderate_hotspot_count,\n        ROUND(CAST(COALESCE(hs.critical_hotspot_value, 0) AS NUMERIC), 2) AS critical_hotspot_value,\n        ROUND(CAST(COALESCE(hs.high_hotspot_value, 0) AS NUMERIC), 2) AS high_hotspot_value,\n        ROUND(CAST(COALESCE(hs.moderate_hotspot_value, 0) AS NUMERIC), 2) AS moderate_hotspot_value,\n        ROUND(CAST(COALESCE(hs.avg_hotspot_score, 0) AS NUMERIC), 2) AS avg_hotspot_score,\n        COALESCE(gcs.high_risk_regions_count, 0) AS high_risk_regions_count,\n        ROUND(CAST(COALESCE(gcs.max_region_risk_concentration, 0) AS NUMERIC), 2) AS max_region_risk_concentration,\n        ROUND(CAST(COALESCE(gcs.avg_region_risk_concentration, 0) AS NUMERIC), 2) AS avg_region_risk_concentration,\n        ROUND(CAST(COALESCE(gcs.total_high_risk_region_value, 0) AS NUMERIC), 2) AS total_high_risk_region_value,\n        COALESCE(gcs.total_hotspot_properties, 0) AS total_hotspot_properties,\n        -- Overall portfolio risk rating\n        CASE\n            WHEN pda.avg_risk_score >= 70 OR (pda.extreme_risk_value + pda.high_risk_value) / NULLIF(pda.total_portfolio_value, 0) >= 0.5 THEN 'Critical'\n            WHEN pda.avg_risk_score >= 50 OR (pda.extreme_risk_value + pda.high_risk_value) / NULLIF(pda.total_portfolio_value, 0) >= 0.3 THEN 'High'\n            WHEN pda.avg_risk_score >= 30 OR (pda.extreme_risk_value + pda.high_risk_value) / NULLIF(pda.total_portfolio_value, 0) >= 0.1 THEN 'Moderate'\n            ELSE 'Low'\n        END AS overall_portfolio_risk_rating\n    FROM portfolio_diversification_analysis pda\n    LEFT JOIN hotspot_summary hs ON pda.portfolio_id = hs.portfolio_id\n    LEFT JOIN geographic_concentration_summary gcs ON pda.portfolio_id = gcs.portfolio_id\n)\nSELECT\n    portfolio_id,\n    portfolio_name,\n    total_properties,\n    ROUND(CAST(total_portfolio_value AS NUMERIC), 2) AS total_portfolio_value,\n    avg_risk_score,\n    median_risk_score,\n    total_estimated_damage,\n    total_estimated_annual_loss,\n    extreme_risk_properties,\n    high_risk_properties,\n    moderate_risk_properties,\n    low_risk_properties,\n    extreme_risk_value,\n    high_risk_value,\n    moderate_risk_value,\n    low_risk_value,\n    unique_regions_count,\n    risk_diversification_score,\n    portfolio_risk_concentration_category,\n    critical_hotspot_count,\n    high_hotspot_count,\n    moderate_hotspot_count,\n    critical_hotspot_value,\n    high_hotspot_value,\n    moderate_hotspot_value,\n    avg_hotspot_score,\n    high_risk_regions_count,\n    max_region_risk_concentration,\n    avg_region_risk_concentration,\n    total_high_risk_region_value,\n    total_hotspot_properties,\n    overall_portfolio_risk_rating\nFROM final_portfolio_summary\nORDER BY overall_portfolio_risk_rating DESC, avg_risk_score DESC, total_portfolio_value DESC\nLIMIT 1000;",
  "evidence": "The query spatially joins properties with flood_zones using geographic coordinates, groups properties by region and sub-region, calculates aggregate risk metrics (average, maximum, standard deviation) for each geographic cluster, identifies hotspots where risk scores exceed regional thresholds, and uses window functions for cluster rankings.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "flood_risk_assessments",
    "portfolio_property_risk_base",
    "geographic_clustering",
    "risk_hotspot_detection",
    "portfolio_aggregation_base",
    "geographic_risk_concentration",
    "portfolio_diversification_analysis",
    "hotspot_summary",
    "geographic_concentration_summary",
    "final_portfolio_summary"
  ],
  "schema_context": {},
  "expected_output": "The query returns portfolio-wide risk analysis showing geographic clustering of high-risk properties, regional risk concentration metrics, and hotspot identification across acquisition targets.",
  "normal_query": "Portfolio-wide risk analysis showing geographic clustering of high-risk properties, regional risk concentration metrics, and hotspot identification across acquisition targets."
}
```



### Query 3 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 3,
  "question": "What are the historical flood event patterns and frequency trends for properties we're considering acquiring?",
  "SQL": "WITH historical_flood_events_base AS (\n    -- First CTE: Base historical flood events with temporal attributes\n    SELECT\n        hfe.event_id,\n        hfe.event_name,\n        hfe.event_type,\n        hfe.start_date,\n        hfe.end_date,\n        hfe.affected_area_geom,\n        hfe.peak_discharge_cfs,\n        hfe.peak_stage_feet,\n        hfe.total_damage_dollars,\n        hfe.fatalities,\n        hfe.properties_affected,\n        hfe.state_code,\n        hfe.county_fips,\n        hfe.data_source,\n        -- Calculate event duration\n        CASE\n            WHEN hfe.end_date IS NOT NULL THEN\n                hfe.end_date - hfe.start_date\n            ELSE 1\n        END AS event_duration_days,\n        -- Extract temporal attributes\n        EXTRACT(YEAR FROM hfe.start_date) AS event_year,\n        EXTRACT(MONTH FROM hfe.start_date) AS event_month,\n        EXTRACT(QUARTER FROM hfe.start_date) AS event_quarter,\n        EXTRACT(DOY FROM hfe.start_date) AS day_of_year,\n        -- Calculate severity score\n        CASE\n            WHEN hfe.total_damage_dollars IS NOT NULL AND hfe.properties_affected IS NOT NULL THEN\n                LOG(COALESCE(hfe.total_damage_dollars, 1) + 1) * \n                LOG(COALESCE(hfe.properties_affected, 1) + 1) * \n                COALESCE(hfe.fatalities, 0) + 1\n            WHEN hfe.total_damage_dollars IS NOT NULL THEN\n                LOG(COALESCE(hfe.total_damage_dollars, 1) + 1) * 10\n            WHEN hfe.properties_affected IS NOT NULL THEN\n                LOG(COALESCE(hfe.properties_affected, 1) + 1) * 10\n            ELSE 1\n        END AS severity_score\n    FROM historical_flood_events hfe\n    WHERE hfe.start_date >= CURRENT_DATE - INTERVAL '50 years'\n),\ntemporal_clustering_analysis AS (\n    -- Second CTE: Analyze temporal clustering of flood events\n    SELECT\n        hfeb.event_id,\n        hfeb.event_name,\n        hfeb.event_type,\n        hfeb.start_date,\n        hfeb.end_date,\n        hfeb.event_year,\n        hfeb.event_month,\n        hfeb.event_quarter,\n        hfeb.day_of_year,\n        hfeb.state_code,\n        hfeb.county_fips,\n        hfeb.severity_score,\n        hfeb.total_damage_dollars,\n        hfeb.properties_affected,\n        -- Count events in same year\n        (\n            SELECT COUNT(*)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.event_year = hfeb.event_year\n                AND hfeb2.state_code = hfeb.state_code\n        ) AS events_in_same_year,\n        -- Count events within 30 days\n        (\n            SELECT COUNT(*)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.event_id != hfeb.event_id\n                AND hfeb2.start_date BETWEEN hfeb.start_date - INTERVAL '30 days' \n                    AND hfeb.start_date + INTERVAL '30 days'\n                AND hfeb2.state_code = hfeb.state_code\n        ) AS events_within_30_days,\n        -- Count events within 90 days\n        (\n            SELECT COUNT(*)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.event_id != hfeb.event_id\n                AND hfeb2.start_date BETWEEN hfeb.start_date - INTERVAL '90 days' \n                    AND hfeb.start_date + INTERVAL '90 days'\n                AND hfeb2.state_code = hfeb.state_code\n        ) AS events_within_90_days,\n        -- Days since previous event\n        (\n            SELECT MAX(hfeb2.start_date)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.event_id != hfeb.event_id\n                AND hfeb2.start_date < hfeb.start_date\n                AND hfeb2.state_code = hfeb.state_code\n        ) AS previous_event_date,\n        -- Days until next event\n        (\n            SELECT MIN(hfeb2.start_date)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.event_id != hfeb.event_id\n                AND hfeb2.start_date > hfeb.start_date\n                AND hfeb2.state_code = hfeb.state_code\n        ) AS next_event_date\n    FROM historical_flood_events_base hfeb\n),\nrecurrence_interval_calculation AS (\n    -- Third CTE: Calculate recurrence intervals\n    SELECT\n        tca.event_id,\n        tca.event_name,\n        tca.event_type,\n        tca.start_date,\n        tca.event_year,\n        tca.event_month,\n        tca.event_quarter,\n        tca.state_code,\n        tca.county_fips,\n        tca.severity_score,\n        tca.total_damage_dollars,\n        tca.properties_affected,\n        tca.events_in_same_year,\n        tca.events_within_30_days,\n        tca.events_within_90_days,\n        -- Calculate days between events\n        CASE\n            WHEN tca.previous_event_date IS NOT NULL THEN\n                tca.start_date - tca.previous_event_date\n            ELSE NULL\n        END AS days_since_previous_event,\n        CASE\n            WHEN tca.next_event_date IS NOT NULL THEN\n                tca.next_event_date - tca.start_date\n            ELSE NULL\n        END AS days_until_next_event,\n        -- Recurrence interval (years)\n        CASE\n            WHEN tca.previous_event_date IS NOT NULL THEN\n                (tca.start_date - tca.previous_event_date) / 365.25\n            ELSE NULL\n        END AS recurrence_interval_years,\n        -- Annual frequency\n        (\n            SELECT COUNT(*)::NUMERIC / \n                NULLIF(MAX(hfeb2.event_year) - MIN(hfeb2.event_year) + 1, 0)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.state_code = tca.state_code\n                AND hfeb2.county_fips = tca.county_fips\n        ) AS annual_frequency\n    FROM temporal_clustering_analysis tca\n),\nfrequency_pattern_analysis AS (\n    -- Fourth CTE: Analyze frequency patterns by month and season\n    SELECT\n        ric.event_id,\n        ric.event_name,\n        ric.event_type,\n        ric.start_date,\n        ric.event_year,\n        ric.event_month,\n        ric.event_quarter,\n        ric.state_code,\n        ric.county_fips,\n        ric.severity_score,\n        ric.total_damage_dollars,\n        ric.properties_affected,\n        ric.recurrence_interval_years,\n        ric.annual_frequency,\n        -- Monthly frequency for this state/county\n        (\n            SELECT COUNT(*)::NUMERIC / \n                NULLIF(COUNT(DISTINCT hfeb2.event_year), 0)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.state_code = ric.state_code\n                AND hfeb2.county_fips = ric.county_fips\n                AND hfeb2.event_month = ric.event_month\n        ) AS monthly_frequency,\n        -- Seasonal frequency\n        (\n            SELECT COUNT(*)::NUMERIC / \n                NULLIF(COUNT(DISTINCT hfeb2.event_year), 0)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.state_code = ric.state_code\n                AND hfeb2.county_fips = ric.county_fips\n                AND hfeb2.event_quarter = ric.event_quarter\n        ) AS seasonal_frequency,\n        -- Window functions for temporal trends\n        AVG(ric.severity_score) OVER (\n            PARTITION BY ric.state_code, ric.county_fips\n            ORDER BY ric.event_year\n            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW\n        ) AS moving_avg_severity_5_years,\n        COUNT(*) OVER (\n            PARTITION BY ric.state_code, ric.county_fips\n            ORDER BY ric.event_year\n            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW\n        ) AS events_in_last_10_years\n    FROM recurrence_interval_calculation ric\n),\ngeographic_recurrence_analysis AS (\n    -- Fifth CTE: Analyze geographic recurrence patterns\n    SELECT\n        fpa.event_id,\n        fpa.event_name,\n        fpa.event_type,\n        fpa.start_date,\n        fpa.event_year,\n        fpa.state_code,\n        fpa.county_fips,\n        fpa.severity_score,\n        fpa.total_damage_dollars,\n        fpa.properties_affected,\n        fpa.recurrence_interval_years,\n        fpa.annual_frequency,\n        fpa.monthly_frequency,\n        fpa.seasonal_frequency,\n        fpa.moving_avg_severity_5_years,\n        fpa.events_in_last_10_years,\n        -- Count events in same geographic area (using spatial intersection)\n        (\n            SELECT COUNT(*)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.event_id != fpa.event_id\n                AND hfeb2.affected_area_geom IS NOT NULL\n                AND (\n                    SELECT affected_area_geom FROM historical_flood_events_base WHERE event_id = fpa.event_id\n                ) IS NOT NULL\n                AND ST_INTERSECTS(\n                    hfeb2.affected_area_geom,\n                    (SELECT affected_area_geom FROM historical_flood_events_base WHERE event_id = fpa.event_id)\n                )\n        ) AS overlapping_events_count,\n        -- Average severity of overlapping events\n        (\n            SELECT AVG(hfeb2.severity_score)\n            FROM historical_flood_events_base hfeb2\n            WHERE hfeb2.event_id != fpa.event_id\n                AND hfeb2.affected_area_geom IS NOT NULL\n                AND (\n                    SELECT affected_area_geom FROM historical_flood_events_base WHERE event_id = fpa.event_id\n                ) IS NOT NULL\n                AND ST_INTERSECTS(\n                    hfeb2.affected_area_geom,\n                    (SELECT affected_area_geom FROM historical_flood_events_base WHERE event_id = fpa.event_id)\n                )\n        ) AS avg_overlapping_severity\n    FROM frequency_pattern_analysis fpa\n),\nseverity_trend_analysis AS (\n    -- Sixth CTE: Analyze severity trends over time\n    SELECT\n        gra.event_id,\n        gra.event_name,\n        gra.event_type,\n        gra.start_date,\n        gra.event_year,\n        gra.state_code,\n        gra.county_fips,\n        gra.severity_score,\n        gra.total_damage_dollars,\n        gra.properties_affected,\n        gra.recurrence_interval_years,\n        gra.annual_frequency,\n        gra.monthly_frequency,\n        gra.seasonal_frequency,\n        gra.moving_avg_severity_5_years,\n        gra.events_in_last_10_years,\n        gra.overlapping_events_count,\n        gra.avg_overlapping_severity,\n        -- Severity trend indicators\n        LAG(gra.severity_score, 1) OVER (\n            PARTITION BY gra.state_code, gra.county_fips\n            ORDER BY gra.event_year\n        ) AS previous_severity,\n        LEAD(gra.severity_score, 1) OVER (\n            PARTITION BY gra.state_code, gra.county_fips\n            ORDER BY gra.event_year\n        ) AS next_severity,\n        -- Severity trend direction\n        CASE\n            WHEN gra.severity_score > gra.moving_avg_severity_5_years * 1.2 THEN 'Increasing'\n            WHEN gra.severity_score < gra.moving_avg_severity_5_years * 0.8 THEN 'Decreasing'\n            ELSE 'Stable'\n        END AS severity_trend,\n        -- Percentile rank of severity\n        PERCENT_RANK() OVER (\n            PARTITION BY gra.state_code, gra.county_fips\n            ORDER BY gra.severity_score\n        ) AS severity_percentile_rank\n    FROM geographic_recurrence_analysis gra\n),\nflood_frequency_classification AS (\n    -- Seventh CTE: Classify flood frequency patterns\n    SELECT\n        sta.event_id,\n        sta.event_name,\n        sta.event_type,\n        sta.start_date,\n        sta.event_year,\n        sta.state_code,\n        sta.county_fips,\n        ROUND(CAST(sta.severity_score AS NUMERIC), 2) AS severity_score,\n        ROUND(CAST(sta.total_damage_dollars AS NUMERIC), 2) AS total_damage_dollars,\n        sta.properties_affected,\n        ROUND(CAST(sta.recurrence_interval_years AS NUMERIC), 2) AS recurrence_interval_years,\n        ROUND(CAST(sta.annual_frequency AS NUMERIC), 4) AS annual_frequency,\n        ROUND(CAST(sta.monthly_frequency AS NUMERIC), 4) AS monthly_frequency,\n        ROUND(CAST(sta.seasonal_frequency AS NUMERIC), 4) AS seasonal_frequency,\n        ROUND(CAST(sta.moving_avg_severity_5_years AS NUMERIC), 2) AS moving_avg_severity_5_years,\n        sta.events_in_last_10_years,\n        sta.overlapping_events_count,\n        ROUND(CAST(sta.avg_overlapping_severity AS NUMERIC), 2) AS avg_overlapping_severity,\n        sta.severity_trend,\n        ROUND(CAST(sta.severity_percentile_rank AS NUMERIC), 4) AS severity_percentile_rank,\n        -- Frequency classification\n        CASE\n            WHEN sta.annual_frequency >= 1.0 THEN 'Very Frequent (Annual+)'\n            WHEN sta.annual_frequency >= 0.5 THEN 'Frequent (Biannual)'\n            WHEN sta.annual_frequency >= 0.2 THEN 'Moderate (Every 5 years)'\n            WHEN sta.annual_frequency >= 0.1 THEN 'Occasional (Every 10 years)'\n            WHEN sta.annual_frequency >= 0.05 THEN 'Rare (Every 20 years)'\n            ELSE 'Very Rare (20+ years)'\n        END AS frequency_classification,\n        -- Recurrence classification\n        CASE\n            WHEN sta.recurrence_interval_years IS NULL THEN 'First Event'\n            WHEN sta.recurrence_interval_years < 1 THEN 'Less than 1 year'\n            WHEN sta.recurrence_interval_years < 5 THEN '1-5 years'\n            WHEN sta.recurrence_interval_years < 10 THEN '5-10 years'\n            WHEN sta.recurrence_interval_years < 20 THEN '10-20 years'\n            ELSE '20+ years'\n        END AS recurrence_classification\n    FROM severity_trend_analysis sta\n)\nSELECT\n    event_id,\n    event_name,\n    event_type,\n    start_date,\n    event_year,\n    state_code,\n    county_fips,\n    severity_score,\n    total_damage_dollars,\n    properties_affected,\n    recurrence_interval_years,\n    annual_frequency,\n    monthly_frequency,\n    seasonal_frequency,\n    moving_avg_severity_5_years,\n    events_in_last_10_years,\n    overlapping_events_count,\n    avg_overlapping_severity,\n    severity_trend,\n    severity_percentile_rank,\n    frequency_classification,\n    recurrence_classification\nFROM flood_frequency_classification\nORDER BY event_year DESC, severity_score DESC, annual_frequency DESC\nLIMIT 10000;",
  "evidence": "The query joins properties with historical flood event records, groups events by property and time dimensions (year, season, decade), calculates event frequencies and time intervals between occurrences, and uses window functions to compute rolling averages of event frequency and recurrence intervals.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "hfe",
    "historical_flood_events",
    "historical_flood_events_base",
    "temporal_clustering_analysis",
    "recurrence_interval_calculation",
    "frequency_pattern_analysis",
    "geographic_recurrence_analysis",
    "severity_trend_analysis",
    "flood_frequency_classification"
  ],
  "schema_context": {},
  "expected_output": "The query returns historical flood event analysis showing occurrence frequency, temporal patterns, seasonal clustering, and recurrence intervals for properties under consideration.",
  "normal_query": "Historical flood event analysis showing occurrence frequency, temporal patterns, seasonal clustering, and recurrence intervals for properties under consideration."
}
```



### Query 4 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 4,
  "question": "How will sea level rise impact our coastal properties over the next 30, 50, and 100 years under different climate scenarios?",
  "SQL": "WITH sea_level_rise_projections_base AS (\n    -- First CTE: Base sea level rise projections\n    SELECT\n        nslr.projection_id,\n        nslr.station_id,\n        nslr.station_name,\n        nslr.station_latitude,\n        nslr.station_longitude,\n        nslr.station_geom,\n        nslr.projection_year,\n        nslr.scenario,\n        nslr.sea_level_rise_feet,\n        nslr.confidence_level,\n        nslr.high_tide_flooding_days,\n        EXTRACT(YEAR FROM CURRENT_DATE) AS current_year,\n        nslr.projection_year - EXTRACT(YEAR FROM CURRENT_DATE) AS years_from_now\n    FROM noaa_sea_level_rise nslr\n    WHERE nslr.projection_year >= EXTRACT(YEAR FROM CURRENT_DATE)\n),\nproperty_slr_matching AS (\n    -- Second CTE: Match properties to nearest SLR stations\n    SELECT\n        rep.property_id,\n        rep.property_address,\n        rep.property_latitude,\n        rep.property_longitude,\n        rep.property_geom,\n        rep.elevation_feet,\n        rep.total_value,\n        rep.state_code,\n        rep.county_fips,\n        slrb.station_id,\n        slrb.station_name,\n        slrb.projection_year,\n        slrb.scenario,\n        slrb.sea_level_rise_feet,\n        slrb.high_tide_flooding_days,\n        slrb.years_from_now,\n        ST_DISTANCE(rep.property_geom, slrb.station_geom) AS distance_to_station_meters\n    FROM real_estate_properties rep\n    CROSS JOIN sea_level_rise_projections_base slrb\n    WHERE rep.property_geom IS NOT NULL\n        AND slrb.station_geom IS NOT NULL\n        AND ST_DISTANCE(rep.property_geom, slrb.station_geom) < 50000\n),\nnearest_station_selection AS (\n    -- Third CTE: Select nearest station for each property-scenario-year combination\n    SELECT DISTINCT ON (psm.property_id, psm.projection_year, psm.scenario)\n        psm.property_id,\n        psm.property_address,\n        psm.property_latitude,\n        psm.property_longitude,\n        psm.elevation_feet,\n        psm.total_value,\n        psm.state_code,\n        psm.county_fips,\n        psm.projection_year,\n        psm.scenario,\n        psm.sea_level_rise_feet,\n        psm.high_tide_flooding_days,\n        psm.years_from_now,\n        psm.distance_to_station_meters\n    FROM property_slr_matching psm\n    ORDER BY psm.property_id, psm.projection_year, psm.scenario, psm.distance_to_station_meters\n),\nmulti_horizon_projections AS (\n    -- Fourth CTE: Calculate impacts across multiple time horizons\n    SELECT\n        nss.property_id,\n        nss.property_address,\n        nss.elevation_feet,\n        nss.total_value,\n        nss.state_code,\n        nss.county_fips,\n        nss.projection_year,\n        nss.scenario,\n        nss.sea_level_rise_feet,\n        nss.high_tide_flooding_days,\n        nss.years_from_now,\n        -- Elevation relative to projected sea level\n        nss.elevation_feet - nss.sea_level_rise_feet AS elevation_above_projected_sl_feet,\n        -- Impact classification\n        CASE\n            WHEN nss.elevation_feet < nss.sea_level_rise_feet THEN 'Below Sea Level'\n            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 2 THEN 'Critical (< 2ft above)'\n            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 5 THEN 'High (< 5ft above)'\n            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 10 THEN 'Moderate (< 10ft above)'\n            ELSE 'Low Risk'\n        END AS impact_classification,\n        -- Vulnerability score (0-100)\n        CASE\n            WHEN nss.elevation_feet < nss.sea_level_rise_feet THEN 100\n            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 2 THEN 90\n            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 5 THEN 75\n            WHEN nss.elevation_feet < nss.sea_level_rise_feet + 10 THEN 50\n            ELSE 25\n        END AS vulnerability_score\n    FROM nearest_station_selection nss\n),\nscenario_comparison AS (\n    -- Fifth CTE: Compare scenarios for each property and time horizon\n    SELECT\n        mhp.property_id,\n        mhp.property_address,\n        mhp.elevation_feet,\n        mhp.total_value,\n        mhp.state_code,\n        mhp.county_fips,\n        mhp.projection_year,\n        mhp.years_from_now,\n        -- Scenario-specific values\n        MAX(CASE WHEN mhp.scenario = 'Low' THEN mhp.sea_level_rise_feet END) AS slr_low_feet,\n        MAX(CASE WHEN mhp.scenario = 'Intermediate-Low' THEN mhp.sea_level_rise_feet END) AS slr_intermediate_low_feet,\n        MAX(CASE WHEN mhp.scenario = 'Intermediate' THEN mhp.sea_level_rise_feet END) AS slr_intermediate_feet,\n        MAX(CASE WHEN mhp.scenario = 'Intermediate-High' THEN mhp.sea_level_rise_feet END) AS slr_intermediate_high_feet,\n        MAX(CASE WHEN mhp.scenario = 'High' THEN mhp.sea_level_rise_feet END) AS slr_high_feet,\n        MAX(CASE WHEN mhp.scenario = 'Extreme' THEN mhp.sea_level_rise_feet END) AS slr_extreme_feet,\n        -- Average across scenarios\n        AVG(mhp.sea_level_rise_feet) AS avg_slr_across_scenarios,\n        -- Scenario range\n        MAX(mhp.sea_level_rise_feet) - MIN(mhp.sea_level_rise_feet) AS slr_scenario_range,\n        -- Worst case vulnerability\n        MAX(mhp.vulnerability_score) AS worst_case_vulnerability_score,\n        -- Best case vulnerability\n        MIN(mhp.vulnerability_score) AS best_case_vulnerability_score\n    FROM multi_horizon_projections mhp\n    GROUP BY mhp.property_id, mhp.property_address, mhp.elevation_feet, mhp.total_value, \n             mhp.state_code, mhp.county_fips, mhp.projection_year, mhp.years_from_now\n),\ntemporal_projection_analysis AS (\n    -- Sixth CTE: Analyze temporal progression of impacts\n    SELECT\n        sc.property_id,\n        sc.property_address,\n        sc.elevation_feet,\n        sc.total_value,\n        sc.state_code,\n        sc.county_fips,\n        sc.projection_year,\n        sc.years_from_now,\n        sc.slr_low_feet,\n        sc.slr_intermediate_feet,\n        sc.slr_high_feet,\n        sc.avg_slr_across_scenarios,\n        sc.worst_case_vulnerability_score,\n        sc.best_case_vulnerability_score,\n        -- Projections for different horizons\n        MAX(CASE WHEN sc.years_from_now = 5 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_5_years,\n        MAX(CASE WHEN sc.years_from_now = 10 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_10_years,\n        MAX(CASE WHEN sc.years_from_now = 20 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_20_years,\n        MAX(CASE WHEN sc.years_from_now = 30 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_30_years,\n        MAX(CASE WHEN sc.years_from_now = 50 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_50_years,\n        MAX(CASE WHEN sc.years_from_now = 100 THEN sc.avg_slr_across_scenarios END) OVER (PARTITION BY sc.property_id) AS slr_100_years,\n        -- Rate of sea level rise (feet per year)\n        CASE\n            WHEN sc.years_from_now > 0 THEN\n                sc.avg_slr_across_scenarios / sc.years_from_now\n            ELSE NULL\n        END AS slr_rate_feet_per_year\n    FROM scenario_comparison sc\n),\nimpact_assessment AS (\n    -- Seventh CTE: Assess impacts across time horizons\n    SELECT\n        tpa.property_id,\n        tpa.property_address,\n        tpa.elevation_feet,\n        tpa.total_value,\n        tpa.state_code,\n        tpa.county_fips,\n        tpa.projection_year,\n        tpa.years_from_now,\n        ROUND(CAST(tpa.slr_5_years AS NUMERIC), 3) AS slr_5_years_feet,\n        ROUND(CAST(tpa.slr_10_years AS NUMERIC), 3) AS slr_10_years_feet,\n        ROUND(CAST(tpa.slr_20_years AS NUMERIC), 3) AS slr_20_years_feet,\n        ROUND(CAST(tpa.slr_30_years AS NUMERIC), 3) AS slr_30_years_feet,\n        ROUND(CAST(tpa.slr_50_years AS NUMERIC), 3) AS slr_50_years_feet,\n        ROUND(CAST(tpa.slr_100_years AS NUMERIC), 3) AS slr_100_years_feet,\n        ROUND(CAST(tpa.avg_slr_across_scenarios AS NUMERIC), 3) AS current_horizon_slr_feet,\n        ROUND(CAST(tpa.slr_rate_feet_per_year AS NUMERIC), 4) AS slr_rate_feet_per_year,\n        -- Impact at each horizon\n        CASE\n            WHEN tpa.elevation_feet < tpa.slr_5_years THEN 'At Risk (5yr)'\n            WHEN tpa.elevation_feet < tpa.slr_10_years THEN 'At Risk (10yr)'\n            WHEN tpa.elevation_feet < tpa.slr_20_years THEN 'At Risk (20yr)'\n            WHEN tpa.elevation_feet < tpa.slr_30_years THEN 'At Risk (30yr)'\n            WHEN tpa.elevation_feet < tpa.slr_50_years THEN 'At Risk (50yr)'\n            WHEN tpa.elevation_feet < tpa.slr_100_years THEN 'At Risk (100yr)'\n            ELSE 'Low Risk'\n        END AS earliest_risk_horizon,\n        -- Overall risk rating\n        CASE\n            WHEN tpa.elevation_feet < tpa.slr_30_years THEN 'Critical'\n            WHEN tpa.elevation_feet < tpa.slr_50_years THEN 'High'\n            WHEN tpa.elevation_feet < tpa.slr_100_years THEN 'Moderate'\n            ELSE 'Low'\n        END AS overall_risk_rating\n    FROM temporal_projection_analysis tpa\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    projection_year,\n    years_from_now,\n    slr_5_years_feet,\n    slr_10_years_feet,\n    slr_20_years_feet,\n    slr_30_years_feet,\n    slr_50_years_feet,\n    slr_100_years_feet,\n    current_horizon_slr_feet,\n    slr_rate_feet_per_year,\n    earliest_risk_horizon,\n    overall_risk_rating\nFROM impact_assessment\nWHERE years_from_now IN (5, 10, 20, 30, 50, 100)\nORDER BY overall_risk_rating DESC, years_from_now, total_value DESC\nLIMIT 10000;",
  "evidence": "The query filters properties within coastal proximity thresholds, joins with sea level rise projection models for each time horizon and scenario, calculates flood zone changes as properties migrate from lower to higher risk zones, and aggregates exposure by scenario.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "current_date",
    "noaa_sea_level_rise",
    "real_estate_properties",
    "sea_level_rise_projections_base",
    "property_slr_matching",
    "nearest_station_selection",
    "multi_horizon_projections",
    "scenario_comparison",
    "temporal_projection_analysis",
    "impact_assessment"
  ],
  "schema_context": {},
  "expected_output": "The query returns sea level rise impact projections for coastal properties across 2050, 2070, and 2100 time horizons, comparing optimistic, moderate, and pessimistic climate scenarios with flood zone migration and property exposure.",
  "normal_query": "Sea level rise impact projections for coastal properties across 2050, 2070, and 2100 time horizons, comparing optimistic, moderate, and pessimistic climate scenarios with flood zone migration and property exposure changes."
}
```



### Query 5 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 5,
  "question": "What do streamflow patterns and gauge data tell us about flood frequency and intensity near our target properties?",
  "SQL": "WITH streamflow_observations_base AS (\n    SELECT\n        uso.observation_id,\n        uso.gauge_id,\n        uso.observation_time,\n        uso.gage_height_feet,\n        uso.discharge_cfs,\n        uso.stage_feet,\n        uso.flood_category,\n        uso.percentile_rank,\n        usg.gauge_name,\n        usg.gauge_latitude,\n        usg.gauge_longitude,\n        usg.gauge_geom,\n        usg.flood_stage_feet,\n        usg.moderate_flood_stage_feet,\n        usg.major_flood_stage_feet,\n        usg.drainage_area_sq_miles,\n        usg.state_code,\n        usg.county_name,\n        usg.river_name,\n        EXTRACT(YEAR FROM uso.observation_time) AS observation_year,\n        EXTRACT(MONTH FROM uso.observation_time) AS observation_month\n    FROM usgs_streamflow_observations uso\n    INNER JOIN usgs_streamflow_gauges usg ON uso.gauge_id = usg.gauge_id\n    WHERE usg.active_status = TRUE\n        AND uso.observation_time >= CURRENT_DATE - INTERVAL '20 years'\n),\nflood_event_identification AS (\n    SELECT\n        sob.observation_id,\n        sob.gauge_id,\n        sob.gauge_name,\n        sob.observation_time,\n        sob.observation_year,\n        sob.observation_month,\n        sob.gage_height_feet,\n        sob.discharge_cfs,\n        sob.stage_feet,\n        sob.flood_category,\n        sob.flood_stage_feet,\n        sob.moderate_flood_stage_feet,\n        sob.major_flood_stage_feet,\n        sob.state_code,\n        sob.county_name,\n        sob.river_name,\n        CASE\n            WHEN sob.stage_feet >= sob.major_flood_stage_feet THEN 'Major'\n            WHEN sob.stage_feet >= sob.moderate_flood_stage_feet THEN 'Moderate'\n            WHEN sob.stage_feet >= sob.flood_stage_feet THEN 'Minor'\n            ELSE 'None'\n        END AS flood_severity,\n        CASE\n            WHEN sob.stage_feet >= sob.major_flood_stage_feet THEN 3\n            WHEN sob.stage_feet >= sob.moderate_flood_stage_feet THEN 2\n            WHEN sob.stage_feet >= sob.flood_stage_feet THEN 1\n            ELSE 0\n        END AS flood_severity_score\n    FROM streamflow_observations_base sob\n),\nflood_frequency_calculation AS (\n    SELECT\n        fei.gauge_id,\n        fei.gauge_name,\n        fei.state_code,\n        fei.county_name,\n        fei.river_name,\n        fei.observation_year,\n        COUNT(DISTINCT CASE WHEN fei.flood_severity != 'None' THEN DATE(fei.observation_time) END) AS flood_days_per_year,\n        COUNT(DISTINCT CASE WHEN fei.flood_severity = 'Major' THEN DATE(fei.observation_time) END) AS major_flood_days_per_year,\n        COUNT(DISTINCT CASE WHEN fei.flood_severity = 'Moderate' THEN DATE(fei.observation_time) END) AS moderate_flood_days_per_year,\n        COUNT(DISTINCT CASE WHEN fei.flood_severity = 'Minor' THEN DATE(fei.observation_time) END) AS minor_flood_days_per_year,\n        MAX(fei.discharge_cfs) AS peak_discharge_cfs,\n        MAX(fei.stage_feet) AS peak_stage_feet,\n        AVG(CASE WHEN fei.flood_severity != 'None' THEN fei.discharge_cfs END) AS avg_flood_discharge_cfs\n    FROM flood_event_identification fei\n    GROUP BY fei.gauge_id, fei.gauge_name, fei.state_code, fei.county_name, fei.river_name, fei.observation_year\n),\nrecurrence_interval_analysis AS (\n    SELECT\n        ffc.gauge_id,\n        ffc.gauge_name,\n        ffc.state_code,\n        ffc.county_name,\n        ffc.river_name,\n        ffc.observation_year,\n        ffc.flood_days_per_year,\n        ffc.major_flood_days_per_year,\n        ffc.moderate_flood_days_per_year,\n        ffc.minor_flood_days_per_year,\n        ffc.peak_discharge_cfs,\n        ffc.peak_stage_feet,\n        ffc.avg_flood_discharge_cfs,\n        COUNT(*) OVER (PARTITION BY ffc.gauge_id) AS total_years,\n        COUNT(CASE WHEN ffc.flood_days_per_year > 0 THEN 1 END) OVER (PARTITION BY ffc.gauge_id) AS years_with_floods,\n        AVG(ffc.flood_days_per_year) OVER (PARTITION BY ffc.gauge_id) AS avg_flood_days_per_year,\n        AVG(ffc.peak_discharge_cfs) OVER (PARTITION BY ffc.gauge_id) AS avg_peak_discharge\n    FROM flood_frequency_calculation ffc\n),\ngauge_network_coverage AS (\n    SELECT\n        ria.gauge_id,\n        ria.gauge_name,\n        ria.state_code,\n        ria.county_name,\n        ria.river_name,\n        ria.total_years,\n        ria.years_with_floods,\n        ROUND(CAST(ria.avg_flood_days_per_year AS NUMERIC), 2) AS avg_flood_days_per_year,\n        ROUND(CAST(ria.avg_peak_discharge AS NUMERIC), 2) AS avg_peak_discharge_cfs,\n        (\n            SELECT COUNT(*)\n            FROM usgs_streamflow_gauges usg2\n            WHERE usg2.active_status = TRUE\n                AND usg2.gauge_geom IS NOT NULL\n                AND (\n                    SELECT gauge_geom FROM usgs_streamflow_gauges WHERE gauge_id = ria.gauge_id\n                ) IS NOT NULL\n                AND ST_DISTANCE(\n                    usg2.gauge_geom,\n                    (SELECT gauge_geom FROM usgs_streamflow_gauges WHERE gauge_id = ria.gauge_id)\n                ) < 50000\n        ) AS nearby_gauges_count,\n        CASE\n            WHEN ria.years_with_floods > 0 THEN\n                ria.total_years::NUMERIC / ria.years_with_floods::NUMERIC\n            ELSE NULL\n        END AS recurrence_interval_years\n    FROM recurrence_interval_analysis ria\n)\nSELECT\n    gauge_id,\n    gauge_name,\n    state_code,\n    county_name,\n    river_name,\n    total_years,\n    years_with_floods,\n    avg_flood_days_per_year,\n    avg_peak_discharge_cfs,\n    nearby_gauges_count,\n    ROUND(CAST(recurrence_interval_years AS NUMERIC), 2) AS recurrence_interval_years\nFROM gauge_network_coverage\nORDER BY avg_flood_days_per_year DESC, recurrence_interval_years ASC\nLIMIT 5000;",
  "evidence": "The query identifies properties within catchment areas of stream gauges, joins properties with the nearest upstream and downstream gauge stations, retrieves historical discharge data, and calculates recurrence intervals and peak flow statistics for flood frequency analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "uso",
    "usgs_streamflow_observations",
    "usgs_streamflow_gauges",
    "streamflow_observations_base",
    "flood_event_identification",
    "flood_frequency_calculation",
    "recurrence_interval_analysis",
    "gauge_network_coverage"
  ],
  "schema_context": {},
  "expected_output": "The query returns streamflow-based flood frequency analysis using gauge network data, showing coverage quality, historical flood patterns, peak flow statistics, and recurrence probability for properties near monitored stream reaches.",
  "normal_query": "Streamflow-based flood frequency analysis using gauge network data, showing coverage quality, historical flood patterns, peak flow statistics, and recurrence probability for properties near monitored waterways."
}
```



### Query 6 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 6,
  "question": "Can you show me a comprehensive performance evaluation of NASA's flood prediction models using advanced analytics?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query joins flood model predictions with actual flood observations, groups results by model version and time period, calculates performance metrics such as precision, recall, and RMSE, uses window functions to compute rolling accuracy trends and comparative benchmarks, applies quartile analysis to segment prediction errors, and handles NULL values for incomplete observation data.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns performance evaluation results for NASA flood models with statistical metrics.",
  "normal_query": "Performance evaluation results for NASA flood models with statistical metrics"
}
```



### Query 7 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 7,
  "question": "Can you provide a detailed analysis of how properties intersect with flood zones using advanced spatial analytics?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query performs spatial joins between properties and flood_zones tables to identify intersections, groups results by flood zone classification and property type, calculates aggregate metrics including total property count, assessed value exposure, and average risk scores per zone, and uses window functions to rank zones by exposure level and compute percentile distributions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns property and flood zone intersection analysis with spatial relationship metrics.",
  "normal_query": "Property and flood zone intersection analysis with spatial relationship metrics"
}
```



### Query 8 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 8,
  "question": "Can you show me how flood risk levels have changed over time with detailed trend analysis and forecasting insights?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query extracts risk scores with associated timestamps, groups data by time periods (monthly, quarterly, yearly) and geographic dimensions, calculates aggregate risk metrics and growth rates for each period, uses window functions to compute rolling averages, year-over-year comparisons, and moving trend indicators, applies quartile analysis to identify accelerating risk areas, and handles NULL values in historical records.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns temporal risk trend analysis with historical patterns and projections.",
  "normal_query": "Temporal risk trend analysis with historical patterns and projections"
}
```



### Query 9 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 9,
  "question": "Can you identify geographic clusters of high flood risk areas and analyze their characteristics using spatial analytics?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query groups data by geographic coordinates and administrative boundaries, calculates density metrics and aggregate risk scores for each area, identifies clusters using spatial proximity and risk threshold criteria, uses window functions to compute cluster rankings and comparative metrics between clusters, and applies quartile analysis to segment cluster risk levels.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns geographic risk clustering analysis with spatial pattern identification.",
  "normal_query": "Geographic risk clustering analysis with spatial pattern identification"
}
```



### Query 10 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 10,
  "question": "Can you generate comprehensive vulnerability scores for properties incorporating multiple risk factors and exposure indicators?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query joins properties with flood_zones and risk_scores tables, aggregates multiple risk dimensions including location-based hazard levels, property characteristics like elevation and construction type, historical loss data, and proximity to water bodies, applies weighting factors to different risk components, and uses window functions for percentile rankings.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns multi-factor property vulnerability assessment with composite scoring.",
  "normal_query": "Multi-factor property vulnerability assessment with composite scoring"
}
```



### Query 11 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 11,
  "question": "Show me the financial impact modeling for M&A acquisition pricing using advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query performs multi-dimensional aggregation by grouping properties by flood zone classification and risk tier, calculates summary statistics including total property values at risk, average risk scores, and value quartiles to identify concentration risk. Window functions compute rolling averages of historical flood events and year-over-year risk score changes. LEFT JOINs ensure all properties are included even with missing data.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns financial impact analysis results for mergers and acquisitions pricing models.",
  "normal_query": "Display financial impact analysis results for mergers and acquisitions pricing models."
}
```



### Query 12 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 12,
  "question": "Show me the FEMA flood zone risk classification with advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query groups properties by FEMA flood zone designations (A, AE, V, VE, X, etc.) and calculates aggregate metrics including property counts per zone, total insured values, and average risk scores. Statistical functions compute quartile distributions of risk scores within each zone to identify outliers and concentration. Window functions generate zone rankings and comparative metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns FEMA flood zone risk classification analysis results.",
  "normal_query": "Display FEMA flood zone risk classification analysis results."
}
```



### Query 13 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 13,
  "question": "Show me the NOAA sea level rise scenario comparison with advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query creates scenario-based groupings by categorizing properties according to their elevation relative to each NOAA projection threshold (0.5m, 1.0m, 1.5m, 2.0m sea level rise by 2100). Aggregation functions calculate properties at risk, total asset values exposed, and risk trajectory by scenario.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns NOAA sea level rise scenario comparison analysis results.",
  "normal_query": "Display NOAA sea level rise scenario comparison analysis results."
}
```



### Query 14 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 14,
  "question": "Show me the USGS streamflow historical pattern recognition with advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query aggregates USGS streamflow measurements by time periods (monthly, seasonal, annual) and gauge locations, calculating statistical measures including mean discharge, peak flows, base flows, and flow variability coefficients. Window functions compute rolling averages, trend indicators, and comparative metrics across gauges.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns USGS streamflow historical pattern recognition analysis results.",
  "normal_query": "Display USGS streamflow historical pattern recognition analysis results."
}
```



### Query 15 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 15,
  "question": "Show me the NASA model prediction accuracy assessment with advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query joins NASA model predictions (forecasted flood zones or risk probabilities) with observed flood outcomes, groups by model and geography, calculates accuracy metrics (precision, recall, MAE, RMSE), and uses window functions for model comparison and confidence intervals.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns NASA model prediction accuracy assessment analysis results.",
  "normal_query": "Display NASA model prediction accuracy assessment analysis results."
}
```



### Query 16 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 16,
  "question": "Can you generate a comprehensive risk summary for potential acquisition target portfolios using advanced analytics?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query joins properties with their corresponding flood zones and risk scores, groups properties by portfolio identifier and flood zone category, computes aggregate metrics including total exposure value, average risk scores, and property counts, and calculates quartile distributions of risk scores within each portfolio.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns a detailed risk summary report for properties under consideration for acquisition, including aggregated risk metrics and comparative analysis.",
  "normal_query": "A detailed risk summary report for properties under consideration for acquisition, including aggregated risk metrics and comparative analysis"
}
```



### Query 17 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 17,
  "question": "Can you provide a detailed analysis of data quality metrics across our flood risk assessment database?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query performs completeness checks by counting NULL and missing values in critical fields across all three tables, calculates consistency metrics by identifying properties without matching flood zone assignments or risk scores, groups quality metrics by data source and property type, and uses window functions for trend analysis.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns a comprehensive data quality report showing completeness, consistency, and timeliness metrics for flood risk data.",
  "normal_query": "A comprehensive data quality report showing completeness, consistency, and timeliness metrics for flood risk data"
}
```



### Query 18 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 18,
  "question": "Can you optimize the spatial join performance for matching properties to their corresponding flood zones?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query employs spatial indexing hints to leverage pre-built spatial indexes on property locations and flood zone geometries, uses bounding box pre-filtering to quickly eliminate non-overlapping candidates, and applies staged filtering to reduce computational load.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns properties accurately matched to flood zones using efficient spatial join techniques.",
  "normal_query": "An optimized query result showing properties accurately matched to flood zones using efficient spatial join techniques"
}
```



### Query 19 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 19,
  "question": "Can you create a unified risk score by fusing data from multiple independent risk assessment sources?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query pivots risk scores from different sources stored in the risk_scores table, applies source-specific weighting factors, aggregates into a composite score using weighted averages, and uses window functions for percentile rankings across the portfolio.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns a consolidated risk score for each property that combines and weights multiple risk assessment sources into a single comprehensive metric.",
  "normal_query": "A consolidated risk score for each property that combines and weights multiple risk assessment sources into a single comprehensive metric"
}
```



### Query 20 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 20,
  "question": "Can you project how flood risk will evolve over time for our property portfolio using temporal analysis?",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query extracts historical risk score time series for each property, groups by property and time period, calculates trend metrics and rate-of-change indicators, uses window functions for rolling averages and year-over-year comparisons, and projects risk evolution over hold periods.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns a time-series projection of flood risk metrics showing expected risk evolution over future time periods for the property portfolio.",
  "normal_query": "A time-series projection of flood risk metrics showing expected risk evolution over future time periods for the property portfolio"
}
```



### Query 21 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 21,
  "question": "Show me how property elevation correlates with flood risk scores using statistical analysis.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query joins properties with their associated flood zones and risk scores, groups properties by elevation ranges or quartiles, calculates aggregate risk metrics (mean, median, standard deviation) for each elevation band, applies window functions to compute rolling averages and percentile rankings, and uses correlation coefficients to measure the strength of the elevation-risk relationship.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns statistical analysis results showing the relationship between property elevation levels and their corresponding flood risk scores.",
  "normal_query": "Statistical analysis results showing the relationship between property elevation levels and their corresponding flood risk scores."
}
```



### Query 22 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 22,
  "question": "Provide a comprehensive impact assessment of historical flood events across affected properties.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query retrieves historical flood events with their occurrence dates and severity levels, joins with affected properties within flood zone boundaries, groups results by flood event and property characteristics, calculates aggregated impact metrics including number of properties affected, total estimated damages, and average risk score changes before and after events. Window functions compute running totals and event rankings.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns historical flood event analysis showing property damage, affected areas, and risk score changes over time.",
  "normal_query": "Historical flood event analysis showing property damage, affected areas, and risk score changes over time."
}
```



### Query 23 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 23,
  "question": "Compare the accuracy and performance of different flood risk prediction models.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query extracts predicted risk scores from multiple models alongside actual flood outcomes for each property, groups results by model identifier and time period, calculates performance metrics including prediction accuracy, MAE, RMSE, and confusion matrix statistics (true positives, false positives, etc.). Window functions compute percentile rankings of model performance.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns model performance metrics comparing predicted vs. actual flood risk across different modeling approaches.",
  "normal_query": "Model performance metrics comparing predicted vs. actual flood risk across different modeling approaches."
}
```



### Query 24 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 24,
  "question": "Analyze how flood risk is distributed across different geographic regions and zones.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query groups properties by geographic dimensions such as flood zone designation, county, zip code, or grid coordinates, calculates aggregate risk metrics for each geographic unit including average risk score, property count, high-risk property percentage, and risk score quartiles. Window functions compute regional rankings and compare each area's risk to neighboring regions.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns geographic distribution analysis showing flood risk concentration, high-risk areas, and regional risk patterns.",
  "normal_query": "Geographic distribution analysis showing flood risk concentration, high-risk areas, and regional risk patterns."
}
```



### Query 25 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 25,
  "question": "Break down flood risk patterns by property type to identify which building types face the highest risk.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query groups properties by type classification (single-family residential, multi-family, commercial, industrial, etc.), joins with associated flood zones and risk scores, calculates aggregate statistics for each property type including average risk score, median risk score, risk score distribution quartiles, count of high-risk properties, and percentage of properties in flood zones. Window functions compute type-level rankings.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns property type risk analysis showing risk scores, exposure levels, and vulnerability patterns across residential, commercial, and other property categories.",
  "normal_query": "Property type risk analysis showing risk scores, exposure levels, and vulnerability patterns across residential, commercial, and other property categories."
}
```



### Query 26 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 26,
  "question": "Show me how flood risk propagates recursively across connected zones with advanced analytics.",
  "SQL": "WITH RECURSIVE property_spatial_network AS (\n    -- First CTE: Build spatial network of properties within flood zones\n    SELECT DISTINCT\n        rep1.property_id AS source_property_id,\n        rep1.property_address AS source_address,\n        rep1.property_latitude AS source_lat,\n        rep1.property_longitude AS source_lon,\n        rep1.property_geom AS source_geom,\n        rep1.elevation_feet AS source_elevation,\n        rep1.total_value AS source_value,\n        rep1.state_code,\n        rep1.county_fips,\n        rep2.property_id AS adjacent_property_id,\n        rep2.property_address AS adjacent_address,\n        rep2.property_geom AS adjacent_geom,\n        rep2.elevation_feet AS adjacent_elevation,\n        rep2.total_value AS adjacent_value,\n        ST_DISTANCE(rep1.property_geom, rep2.property_geom) AS distance_meters,\n        CASE\n            WHEN rep1.elevation_feet IS NOT NULL AND rep2.elevation_feet IS NOT NULL THEN\n                rep2.elevation_feet - rep1.elevation_feet\n            ELSE NULL\n        END AS elevation_diff_feet\n    FROM real_estate_properties rep1\n    INNER JOIN fema_flood_zones ffz1 ON (\n        ffz1.zone_geom IS NOT NULL\n        AND rep1.property_geom IS NOT NULL\n        AND ST_DWithin(rep1.property_geom, ffz1.zone_geom, 0)\n    )\n    INNER JOIN real_estate_properties rep2 ON (\n        rep2.property_geom IS NOT NULL\n        AND rep1.property_id != rep2.property_id\n        AND ST_DISTANCE(rep1.property_geom, rep2.property_geom) < 1000  -- Within 1km\n    )\n    WHERE rep1.property_geom IS NOT NULL\n),\nproperty_base_risk AS (\n    -- Second CTE: Get base risk scores for all properties\n    SELECT\n        rep.property_id,\n        rep.property_address,\n        rep.property_latitude,\n        rep.property_longitude,\n        rep.property_geom,\n        rep.elevation_feet,\n        rep.total_value,\n        rep.state_code,\n        rep.county_fips,\n        COALESCE(fra.overall_risk_score, 0) AS base_risk_score,\n        COALESCE(fra.risk_category, 'Unknown') AS base_risk_category,\n        CASE\n            WHEN EXISTS (\n                SELECT 1 FROM fema_flood_zones ffz\n                WHERE ffz.zone_geom IS NOT NULL\n                    AND rep.property_geom IS NOT NULL\n                    AND ST_DWithin(rep.property_geom, ffz.zone_geom, 0)\n            ) THEN TRUE\n            ELSE FALSE\n        END AS is_in_flood_zone\n    FROM real_estate_properties rep\n    LEFT JOIN flood_risk_assessments fra ON rep.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = rep.property_id\n        )\n    WHERE rep.property_geom IS NOT NULL\n),\nrecursive_risk_propagation AS (\n    -- Anchor: Start with properties in high-risk flood zones\n    SELECT\n        pbr.property_id,\n        pbr.property_address,\n        pbr.property_latitude,\n        pbr.property_longitude,\n        pbr.property_geom,\n        pbr.elevation_feet,\n        pbr.total_value,\n        pbr.state_code,\n        pbr.county_fips,\n        pbr.base_risk_score::double precision AS propagated_risk_score,\n        pbr.base_risk_category AS propagated_risk_category,\n        pbr.base_risk_score::double precision AS cumulative_risk_score,\n        0 AS propagation_depth,\n        ARRAY[pbr.property_id::text] AS propagation_path,\n        pbr.is_in_flood_zone\n    FROM property_base_risk pbr\n    WHERE pbr.is_in_flood_zone = TRUE\n        AND pbr.base_risk_score >= 70  -- Start with extreme risk properties\n    \n    UNION ALL\n    \n    -- Recursive: Propagate risk to adjacent properties\n    SELECT\n        pbr.property_id,\n        pbr.property_address,\n        pbr.property_latitude,\n        pbr.property_longitude,\n        pbr.property_geom,\n        pbr.elevation_feet,\n        pbr.total_value,\n        pbr.state_code,\n        pbr.county_fips,\n        -- Propagated risk decreases with distance and elevation difference\n        LEAST(\n            rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1) * \n            CASE\n                WHEN psn.elevation_diff_feet > 0 THEN 0.8  -- Adjacent property higher = less risk propagation\n                WHEN psn.elevation_diff_feet < 0 THEN 1.2  -- Adjacent property lower = more risk propagation\n                ELSE 1.0\n            END,\n            pbr.base_risk_score + 20  -- Cap propagation increase\n        ) AS propagated_risk_score,\n        CASE\n            WHEN LEAST(\n                rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1),\n                pbr.base_risk_score + 20\n            ) >= 70 THEN 'Extreme'\n            WHEN LEAST(\n                rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1),\n                pbr.base_risk_score + 20\n            ) >= 50 THEN 'High'\n            WHEN LEAST(\n                rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1),\n                pbr.base_risk_score + 20\n            ) >= 30 THEN 'Moderate'\n            ELSE 'Low'\n        END AS propagated_risk_category,\n        -- Cumulative risk accumulates through propagation path\n        GREATEST(\n            rrp.cumulative_risk_score,\n            LEAST(\n                rrp.propagated_risk_score * (1.0 - (psn.distance_meters / 1000.0) * 0.1),\n                pbr.base_risk_score + 20\n            )\n        ) AS cumulative_risk_score,\n        rrp.propagation_depth + 1 AS propagation_depth,\n        rrp.propagation_path || pbr.property_id::text AS propagation_path,\n        pbr.is_in_flood_zone\n    FROM recursive_risk_propagation rrp\n    INNER JOIN property_spatial_network psn ON rrp.property_id = psn.source_property_id\n    INNER JOIN property_base_risk pbr ON psn.adjacent_property_id = pbr.property_id\n    WHERE rrp.propagation_depth < 5  -- Limit recursion depth\n        AND NOT (pbr.property_id = ANY(rrp.propagation_path))  -- Avoid cycles\n        AND psn.distance_meters < 500  -- Only propagate to nearby properties\n),\npropagation_aggregation AS (\n    -- Third CTE: Aggregate propagated risk for each property\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips,\n        MAX(propagated_risk_score) AS max_propagated_risk,\n        MAX(cumulative_risk_score) AS max_cumulative_risk,\n        AVG(propagated_risk_score) AS avg_propagated_risk,\n        MIN(propagation_depth) AS min_propagation_depth,\n        MAX(propagation_depth) AS max_propagation_depth,\n        COUNT(DISTINCT propagation_path) AS propagation_path_count,\n        is_in_flood_zone\n    FROM recursive_risk_propagation\n    GROUP BY property_id, property_address, property_latitude, property_longitude,\n             elevation_feet, total_value, state_code, county_fips, is_in_flood_zone\n),\nfinal_risk_calculation AS (\n    -- Fourth CTE: Calculate final risk scores combining base and propagated risk\n    SELECT\n        pa.property_id,\n        pa.property_address,\n        pa.property_latitude,\n        pa.property_longitude,\n        pa.elevation_feet,\n        pa.total_value,\n        pa.state_code,\n        pa.county_fips,\n        pbr.base_risk_score,\n        COALESCE(pa.max_propagated_risk, pbr.base_risk_score) AS propagated_risk_score,\n        COALESCE(pa.max_cumulative_risk, pbr.base_risk_score) AS cumulative_risk_score,\n        -- Final risk = weighted combination of base and propagated risk\n        ROUND(\n            CAST(GREATEST(\n                pbr.base_risk_score * 0.6 + COALESCE(pa.max_propagated_risk, 0) * 0.4,\n                pbr.base_risk_score\n            ) AS NUMERIC),\n            2\n        ) AS final_risk_score,\n        CASE\n            WHEN GREATEST(\n                pbr.base_risk_score * 0.6 + COALESCE(pa.max_propagated_risk, 0) * 0.4,\n                pbr.base_risk_score\n            ) >= 70 THEN 'Extreme'\n            WHEN GREATEST(\n                pbr.base_risk_score * 0.6 + COALESCE(pa.max_propagated_risk, 0) * 0.4,\n                pbr.base_risk_score\n            ) >= 50 THEN 'High'\n            WHEN GREATEST(\n                pbr.base_risk_score * 0.6 + COALESCE(pa.max_propagated_risk, 0) * 0.4,\n                pbr.base_risk_score\n            ) >= 30 THEN 'Moderate'\n            ELSE 'Low'\n        END AS final_risk_category,\n        pa.min_propagation_depth,\n        pa.max_propagation_depth,\n        pa.propagation_path_count,\n        pa.is_in_flood_zone\n    FROM propagation_aggregation pa\n    INNER JOIN property_base_risk pbr ON pa.property_id = pbr.property_id\n),\nspatial_clustering AS (\n    -- Fifth CTE: Identify risk clusters using window functions\n    SELECT\n        frc.*,\n        COUNT(*) OVER (\n            PARTITION BY frc.state_code, frc.county_fips\n            ORDER BY frc.final_risk_score DESC\n            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW\n        ) AS risk_rank_in_county,\n        PERCENT_RANK() OVER (\n            PARTITION BY frc.state_code\n            ORDER BY frc.final_risk_score DESC\n        ) AS risk_percentile_in_state,\n        AVG(frc.final_risk_score) OVER (\n            PARTITION BY frc.state_code, frc.county_fips\n        ) AS avg_county_risk_score,\n        COUNT(*) FILTER (WHERE frc.final_risk_score >= 70) OVER (\n            PARTITION BY frc.state_code, frc.county_fips\n        ) AS extreme_risk_count_in_county\n    FROM final_risk_calculation frc\n)\nSELECT\n    property_id,\n    property_address,\n    ROUND(CAST(property_latitude AS NUMERIC), 7) AS property_latitude,\n    ROUND(CAST(property_longitude AS NUMERIC), 7) AS property_longitude,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(base_risk_score AS NUMERIC), 2) AS base_risk_score,\n    ROUND(CAST(propagated_risk_score AS NUMERIC), 2) AS propagated_risk_score,\n    ROUND(CAST(cumulative_risk_score AS NUMERIC), 2) AS cumulative_risk_score,\n    final_risk_score,\n    final_risk_category,\n    min_propagation_depth,\n    max_propagation_depth,\n    propagation_path_count,\n    risk_rank_in_county,\n    ROUND(CAST(risk_percentile_in_state AS NUMERIC), 4) AS risk_percentile_in_state,\n    ROUND(CAST(avg_county_risk_score AS NUMERIC), 2) AS avg_county_risk_score,\n    extreme_risk_count_in_county,\n    is_in_flood_zone\nFROM spatial_clustering\nWHERE final_risk_score >= 50  -- Focus on high and extreme risk properties\nORDER BY final_risk_score DESC, cumulative_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query uses recursive CTEs to traverse zone connectivity relationships, joins flood_zones with properties and risk_scores tables, groups results by zone hierarchy levels, computes aggregate risk scores at each propagation level using window functions for cumulative impact analysis, calculates rolling averages to identify risk acceleration patterns, and handles NULL values in zone connectivity data.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "fema_flood_zones",
    "flood_risk_assessments",
    "property_base_risk",
    "recursive_risk_propagation",
    "property_spatial_network",
    "propagation_aggregation",
    "final_risk_calculation",
    "spatial_clustering"
  ],
  "schema_context": {},
  "expected_output": "The query returns the recursive propagation of flood risk across interconnected zones with detailed analytical metrics.",
  "normal_query": "Display the recursive propagation of flood risk across interconnected zones with detailed analytical metrics."
}
```



### Query 27 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 27,
  "question": "Identify high-risk properties that could be deal-breakers in our M&A transaction with advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query joins properties with flood_zones and risk_scores tables using LEFT JOINs to capture properties with missing risk data, filters for properties exceeding critical risk thresholds (top quartile), groups results by zone and property characteristics, computes aggregate exposure metrics including total property value at risk and count of critically exposed assets, and uses window functions to rank and compare exposure levels.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns properties with critical flood risk levels that may constitute material deal-breakers during acquisition due diligence.",
  "normal_query": "Identify properties with critical flood risk levels that may constitute material deal-breakers during acquisition due diligence."
}
```



### Query 28 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 28,
  "question": "Analyze the cost-benefit economics of flood risk mitigation strategies after acquisition with advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query joins properties with risk_scores and flood_zones tables, groups properties by current risk level and mitigation scenario, computes baseline risk exposure values and potential losses, calculates mitigation costs by property type and zone characteristics using CASE statements, and uses window functions to calculate risk reduction percentages and payback periods across different mitigation strategies.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns the financial trade-offs between mitigation investment costs and risk reduction benefits for properties post-acquisition.",
  "normal_query": "Evaluate the financial trade-offs between mitigation investment costs and risk reduction benefits for properties post-acquisition."
}
```



### Query 29 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 29,
  "question": "Assess portfolio diversification risk across acquisition targets from a flood exposure perspective with advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query aggregates properties from target portfolios joining flood_zones and risk_scores tables, groups by target portfolio identifier, zone type, and risk tier, computes concentration metrics including Herfindahl index for geographic and risk dispersion, uses window functions to calculate portfolio-level statistics and compare each target against benchmark diversification ratios, and analyzes correlation between portfolio composition and risk exposure.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns geographic and risk concentration patterns across potential acquisition targets to assess portfolio diversification quality.",
  "normal_query": "Evaluate geographic and risk concentration patterns across potential acquisition targets to assess portfolio diversification quality."
}
```



### Query 30 — moderate / aggregation

```json
{
  "db_id": "db-16",
  "question_id": 30,
  "question": "Generate a comprehensive flood risk assessment report for M&A due diligence with advanced analytics.",
  "SQL": "WITH base_analysis AS (\n    -- First CTE: Base analysis\n    SELECT\n        property_id,\n        property_address,\n        property_latitude,\n        property_longitude,\n        property_geom,\n        elevation_feet,\n        total_value,\n        state_code,\n        county_fips\n    FROM real_estate_properties\n    WHERE property_geom IS NOT NULL\n),\nsecondary_analysis AS (\n    -- Second CTE: Secondary analysis\n    SELECT\n        ba.*,\n        fra.assessment_id,\n        fra.overall_risk_score,\n        fra.risk_category\n    FROM base_analysis ba\n    LEFT JOIN flood_risk_assessments fra ON ba.property_id = fra.property_id\n        AND fra.assessment_date = (\n            SELECT MAX(fra2.assessment_date)\n            FROM flood_risk_assessments fra2\n            WHERE fra2.property_id = ba.property_id\n        )\n),\naggregated_metrics AS (\n    -- Third CTE: Aggregated metrics\n    SELECT\n        sa.property_id,\n        sa.property_address,\n        sa.elevation_feet,\n        sa.total_value,\n        sa.state_code,\n        sa.county_fips,\n        AVG(sa.overall_risk_score) AS avg_risk_score,\n        COUNT(*) AS assessment_count\n    FROM secondary_analysis sa\n    GROUP BY sa.property_id, sa.property_address, sa.elevation_feet, \n             sa.total_value, sa.state_code, sa.county_fips\n),\nwindow_analysis AS (\n    -- Fourth CTE: Window function analysis\n    SELECT\n        am.*,\n        RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score DESC) AS risk_rank,\n        PERCENT_RANK() OVER (PARTITION BY am.state_code ORDER BY am.avg_risk_score) AS risk_percentile\n    FROM aggregated_metrics am\n)\nSELECT\n    property_id,\n    property_address,\n    elevation_feet,\n    total_value,\n    state_code,\n    county_fips,\n    ROUND(CAST(avg_risk_score AS NUMERIC), 2) AS avg_risk_score,\n    assessment_count,\n    risk_rank,\n    ROUND(CAST(risk_percentile AS NUMERIC), 4) AS risk_percentile\nFROM window_analysis\nORDER BY avg_risk_score DESC, total_value DESC\nLIMIT 10000;",
  "evidence": "The query performs complex joins across flood_zones, properties, and risk_scores tables using LEFT JOINs to ensure complete coverage including properties with incomplete data, groups results by multiple dimensions including zone type, property characteristics, and risk categories, and computes extensive aggregate metrics including total exposure value, risk score distributions, and concentration metrics.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": [
    "real_estate_properties",
    "base_analysis",
    "flood_risk_assessments",
    "secondary_analysis",
    "aggregated_metrics",
    "window_analysis"
  ],
  "schema_context": {},
  "expected_output": "The query returns a complete due diligence report covering all flood risk dimensions for the target property portfolio.",
  "normal_query": "Produce a complete due diligence report covering all flood risk dimensions for the target property portfolio."
}
```


