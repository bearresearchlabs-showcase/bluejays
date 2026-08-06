# Schema Documentation - db-16

## Flood Risk Assessment Database for M&A Due Diligence

### Overview

12 production tables supporting multi-source flood risk assessment for real estate M&A workflows. Integrates FEMA flood zones, NOAA sea level rise projections, USGS streamflow data, and NASA flood model outputs.

### Table Groups

#### Federal Flood Data Sources

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| fema_flood_zones | FEMA NFHL flood zone designations | zone_code, base_flood_elevation, zone_geom (GEOGRAPHY) |
| noaa_sea_level_rise | Sea level rise projections by station | projection_year, scenario, sea_level_rise_feet, station_geom |
| usgs_streamflow_gauges | Streamflow gauge locations and flood stages | gauge_geom, flood_stage_feet, river_name |
| usgs_streamflow_observations | Historical streamflow measurements | gauge_id (FK), discharge_cfs, flood_category |
| nasa_flood_models | NASA flood model predictions | grid_cell_geom, flood_probability, inundation_depth_feet |

#### Property and Portfolio

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| real_estate_properties | Properties under M&A evaluation | property_geom, total_value, portfolio_id, elevation_feet |
| flood_risk_assessments | Composite risk scores per property | overall_risk_score, risk_category, estimated_damage_dollars |
| property_flood_zone_intersections | Spatial join results | property_id (FK), zone_id (FK), intersection_type |
| portfolio_risk_summaries | Aggregated portfolio-level risk | average_risk_score, total_property_value |

#### Historical and Quality

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| historical_flood_events | Historical flood records | event_type, total_damage_dollars, affected_area_geom |
| model_performance_metrics | Model accuracy tracking | accuracy, f1_score, roc_auc |
| data_quality_metrics | Data pipeline quality | success_rate, error_rate, data_freshness_hours |

### Spatial Columns

All spatial columns use the `GEOGRAPHY` type (WGS84/EPSG:4326):
- `fema_flood_zones.zone_geom` - Flood zone polygon boundaries
- `real_estate_properties.property_geom` - Property point locations
- `noaa_sea_level_rise.station_geom` - Tide station locations
- `usgs_streamflow_gauges.gauge_geom` - Streamflow gauge locations
- `nasa_flood_models.grid_cell_geom` - Model grid cell centers
- `historical_flood_events.affected_area_geom` - Flood event affected areas
- `property_flood_zone_intersections.intersection_geom` - Intersection geometries

### Indexes

20 indexes including GIST spatial indexes on all geography columns, composite indexes on (state_code, county_fips), and temporal indexes on dates.

### Cross-Database Compatibility

- **PostgreSQL**: Full support with PostGIS extension for spatial operations
- **Databricks**: Delta Lake with spatial extensions
- **Databricks**: GEOGRAPHY data type support
