import os
import json
import logging
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    password = os.getenv('PG_PASSWORD', '')
    if not password:
        logger.warning("PG_PASSWORD not set, using empty password")
    
    conn = psycopg2.connect(
        host=os.getenv('PG_HOST', 'localhost'),
        port=os.getenv('PG_PORT', '5432'),
        user=os.getenv('PG_USER', 'postgres'),
        password=password,
        database=os.getenv('PG_DATABASE', 'db_16')
    )
    return conn

def prepare_geometry_wkt(geom_wkt: Optional[str]) -> Optional[str]:
    if not geom_wkt:
        return None
    if geom_wkt.startswith('SRID='):
        parts = geom_wkt.split(';', 1)
        if len(parts) == 2:
            return parts[1]
        return None
    return geom_wkt

def load_fema_data(conn, data_file: str) -> Tuple[int, int]:
    success_count = 0
    error_count = 0
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {data_file}: {e}")
        return 0, 0
    
    cur = None
    try:
        cur = conn.cursor()
        
        for record in data:
            try:
                if not record.get('zone_id') or not record.get('zone_code'):
                    logger.warning(f"Skipping record missing zone_id or zone_code")
                    error_count += 1
                    continue
                
                geom_wkt = prepare_geometry_wkt(record.get('zone_geom'))
                
                insert_sql = """
                INSERT INTO fema_flood_zones (
                    zone_id, zone_code, zone_description, base_flood_elevation,
                    zone_geom, community_id, community_name, state_code, county_fips,
                    effective_date, map_panel, source_file, source_crs, target_crs,
                    spatial_extent_west, spatial_extent_south, spatial_extent_east,
                    spatial_extent_north, transformation_status
                ) VALUES (
                    %s, %s, %s, %s, 
                    CASE WHEN %s IS NOT NULL THEN ST_SetSRID(ST_GeomFromText(%s), 4326)::geography ELSE NULL END,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (zone_id) DO UPDATE SET
                    zone_code = EXCLUDED.zone_code,
                    zone_description = EXCLUDED.zone_description,
                    base_flood_elevation = EXCLUDED.base_flood_elevation,
                    zone_geom = EXCLUDED.zone_geom,
                    load_timestamp = CURRENT_TIMESTAMP
                """
                
                cur.execute(insert_sql, (
                    record['zone_id'],
                    record['zone_code'],
                    record.get('zone_description'),
                    record.get('base_flood_elevation'),
                    geom_wkt,
                    geom_wkt,
                    record.get('community_id'),
                    record.get('community_name'),
                    record.get('state_code'),
                    record.get('county_fips'),
                    record.get('effective_date'),
                    record.get('map_panel'),
                    record.get('source_file'),
                    record.get('source_crs', 'EPSG:4326'),
                    record.get('target_crs', 'EPSG:4326'),
                    record.get('spatial_extent_west'),
                    record.get('spatial_extent_south'),
                    record.get('spatial_extent_east'),
                    record.get('spatial_extent_north'),
                    record.get('transformation_status')
                ))
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to insert FEMA record {record.get('zone_id', 'unknown')}: {e}")
                error_count += 1
                conn.rollback()
                continue
        
        conn.commit()
        logger.info(f"FEMA: {success_count} successful, {error_count} errors")
        return success_count, error_count
    except Exception as e:
        logger.error(f"Fatal error in load_fema_data: {e}")
        conn.rollback()
        return success_count, error_count
    finally:
        if cur:
            cur.close()

def load_noaa_data(conn, data_file: str) -> Tuple[int, int]:
    success_count = 0
    error_count = 0
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {data_file}: {e}")
        return 0, 0
    
    cur = None
    try:
        cur = conn.cursor()
        
        for record in data:
            try:
                if not record.get('projection_id'):
                    logger.warning(f"Skipping record missing projection_id")
                    error_count += 1
                    continue
                
                if record.get('station_latitude') is None or record.get('station_longitude') is None:
                    logger.warning(f"Skipping record {record.get('projection_id')} missing required lat/lon")
                    error_count += 1
                    continue
                
                geom_wkt = prepare_geometry_wkt(record.get('station_geom'))
                if not geom_wkt and record.get('station_latitude') and record.get('station_longitude'):
                    geom_wkt = f"SRID=4326;POINT({record['station_longitude']} {record['station_latitude']})"
                
                insert_sql = """
                INSERT INTO noaa_sea_level_rise (
                    projection_id, station_id, station_name, station_latitude,
                    station_longitude, station_geom, projection_year, scenario,
                    sea_level_rise_feet, confidence_level, high_tide_flooding_days,
                    data_source
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    CASE WHEN %s IS NOT NULL THEN ST_SetSRID(ST_GeomFromText(%s), 4326)::geography ELSE NULL END,
                    %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (projection_id) DO UPDATE SET
                    sea_level_rise_feet = EXCLUDED.sea_level_rise_feet,
                    high_tide_flooding_days = EXCLUDED.high_tide_flooding_days,
                    load_timestamp = CURRENT_TIMESTAMP
                """
                
                cur.execute(insert_sql, (
                    record['projection_id'],
                    record.get('station_id'),
                    record.get('station_name'),
                    record['station_latitude'],
                    record['station_longitude'],
                    geom_wkt,
                    geom_wkt,
                    record.get('projection_year'),
                    record.get('scenario'),
                    record.get('sea_level_rise_feet'),
                    record.get('confidence_level'),
                    record.get('high_tide_flooding_days'),
                    record.get('data_source', 'NOAA_CO-OPS')
                ))
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to insert NOAA record {record.get('projection_id', 'unknown')}: {e}")
                error_count += 1
                conn.rollback()
                continue
        
        conn.commit()
        logger.info(f"NOAA: {success_count} successful, {error_count} errors")
        return success_count, error_count
    except Exception as e:
        logger.error(f"Fatal error in load_noaa_data: {e}")
        conn.rollback()
        return success_count, error_count
    finally:
        if cur:
            cur.close()

def load_usgs_gauges(conn, data_file: str) -> Tuple[int, int]:
    success_count = 0
    error_count = 0
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {data_file}: {e}")
        return 0, 0
    
    cur = None
    try:
        cur = conn.cursor()
        
        for record in data:
            try:
                if not record.get('gauge_id'):
                    logger.warning(f"Skipping record missing gauge_id")
                    error_count += 1
                    continue
                
                if record.get('gauge_latitude') is None or record.get('gauge_longitude') is None:
                    logger.warning(f"Skipping gauge {record.get('gauge_id')} missing required lat/lon")
                    error_count += 1
                    continue
                
                geom_wkt = prepare_geometry_wkt(record.get('gauge_geom'))
                if not geom_wkt and record.get('gauge_latitude') and record.get('gauge_longitude'):
                    geom_wkt = f"SRID=4326;POINT({record['gauge_longitude']} {record['gauge_latitude']})"
                
                insert_sql = """
                INSERT INTO usgs_streamflow_gauges (
                    gauge_id, gauge_name, gauge_latitude, gauge_longitude,
                    gauge_geom, drainage_area_sq_miles, flood_stage_feet,
                    moderate_flood_stage_feet, major_flood_stage_feet,
                    state_code, county_name, river_name, active_status,
                    first_observation_date, last_observation_date, update_frequency_minutes
                ) VALUES (
                    %s, %s, %s, %s,
                    CASE WHEN %s IS NOT NULL THEN ST_SetSRID(ST_GeomFromText(%s), 4326)::geography ELSE NULL END,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (gauge_id) DO UPDATE SET
                    flood_stage_feet = EXCLUDED.flood_stage_feet,
                    moderate_flood_stage_feet = EXCLUDED.moderate_flood_stage_feet,
                    major_flood_stage_feet = EXCLUDED.major_flood_stage_feet,
                    last_observation_date = EXCLUDED.last_observation_date,
                    load_timestamp = CURRENT_TIMESTAMP
                """
                
                cur.execute(insert_sql, (
                    record['gauge_id'],
                    record.get('gauge_name'),
                    record['gauge_latitude'],
                    record['gauge_longitude'],
                    geom_wkt,
                    geom_wkt,
                    record.get('drainage_area_sq_miles'),
                    record.get('flood_stage_feet'),
                    record.get('moderate_flood_stage_feet'),
                    record.get('major_flood_stage_feet'),
                    record.get('state_code'),
                    record.get('county_name'),
                    record.get('river_name'),
                    record.get('active_status', True),
                    record.get('first_observation_date'),
                    record.get('last_observation_date'),
                    record.get('update_frequency_minutes', 15)
                ))
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to insert USGS gauge {record.get('gauge_id', 'unknown')}: {e}")
                error_count += 1
                conn.rollback()
                continue
        
        conn.commit()
        logger.info(f"USGS Gauges: {success_count} successful, {error_count} errors")
        return success_count, error_count
    except Exception as e:
        logger.error(f"Fatal error in load_usgs_gauges: {e}")
        conn.rollback()
        return success_count, error_count
    finally:
        if cur:
            cur.close()

def load_usgs_observations(conn, data_file: str) -> Tuple[int, int]:
    success_count = 0
    error_count = 0
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {data_file}: {e}")
        return 0, 0
    
    cur = None
    try:
        cur = conn.cursor()
        
        batch_size = 1000
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            values = []
            
            for record in batch:
                if not record.get('observation_id') or not record.get('gauge_id'):
                    error_count += 1
                    continue
                
                if not record.get('observation_time'):
                    error_count += 1
                    continue
                
                values.append((
                    record['observation_id'],
                    record['gauge_id'],
                    record['observation_time'],
                    record.get('gage_height_feet'),
                    record.get('discharge_cfs'),
                    record.get('stage_feet'),
                    record.get('flood_category'),
                    record.get('percentile_rank'),
                    record.get('data_quality_code')
                ))
            
            if values:
                insert_sql = """
                INSERT INTO usgs_streamflow_observations (
                    observation_id, gauge_id, observation_time, gage_height_feet,
                    discharge_cfs, stage_feet, flood_category, percentile_rank, data_quality_code
                ) VALUES %s
                ON CONFLICT (observation_id) DO UPDATE SET
                    gage_height_feet = EXCLUDED.gage_height_feet,
                    discharge_cfs = EXCLUDED.discharge_cfs,
                    stage_feet = EXCLUDED.stage_feet,
                    flood_category = EXCLUDED.flood_category,
                    load_timestamp = CURRENT_TIMESTAMP
                """
                
                try:
                    execute_values(cur, insert_sql, values)
                    success_count += len(values)
                except Exception as e:
                    logger.error(f"Failed to insert USGS observations batch: {e}")
                    error_count += len(values)
                    conn.rollback()
                    continue
        
        conn.commit()
        logger.info(f"USGS Observations: {success_count} successful, {error_count} errors")
        return success_count, error_count
    except Exception as e:
        logger.error(f"Fatal error in load_usgs_observations: {e}")
        conn.rollback()
        return success_count, error_count
    finally:
        if cur:
            cur.close()

def load_nasa_data(conn, data_file: str) -> Tuple[int, int]:
    success_count = 0
    error_count = 0
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {data_file}: {e}")
        return 0, 0
    
    cur = None
    try:
        cur = conn.cursor()
        
        for record in data:
            try:
                if not record.get('model_id'):
                    logger.warning(f"Skipping record missing model_id")
                    error_count += 1
                    continue
                
                if record.get('grid_cell_latitude') is None or record.get('grid_cell_longitude') is None:
                    logger.warning(f"Skipping NASA model {record.get('model_id')} missing required lat/lon")
                    error_count += 1
                    continue
                
                geom_wkt = prepare_geometry_wkt(record.get('grid_cell_geom'))
                if not geom_wkt and record.get('grid_cell_latitude') and record.get('grid_cell_longitude'):
                    geom_wkt = f"SRID=4326;POINT({record['grid_cell_longitude']} {record['grid_cell_latitude']})"
                
                insert_sql = """
                INSERT INTO nasa_flood_models (
                    model_id, model_name, forecast_time, grid_cell_latitude, grid_cell_longitude,
                    grid_cell_geom, inundation_depth_feet,
                    flood_probability, flood_severity, model_resolution_meters,
                    spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north,
                    source_file
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    CASE WHEN %s IS NOT NULL THEN ST_SetSRID(ST_GeomFromText(%s), 4326)::geography ELSE NULL END,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (model_id) DO UPDATE SET
                    forecast_time = EXCLUDED.forecast_time,
                    inundation_depth_feet = EXCLUDED.inundation_depth_feet,
                    flood_probability = EXCLUDED.flood_probability,
                    flood_severity = EXCLUDED.flood_severity,
                    load_timestamp = CURRENT_TIMESTAMP
                """
                
                cur.execute(insert_sql, (
                    record['model_id'],
                    record.get('model_name'),
                    record.get('forecast_time'),
                    record['grid_cell_latitude'],
                    record['grid_cell_longitude'],
                    geom_wkt,
                    geom_wkt,
                    record.get('inundation_depth_feet'),
                    record.get('flood_probability'),
                    record.get('flood_severity'),
                    record.get('model_resolution_meters'),
                    record.get('spatial_extent_west'),
                    record.get('spatial_extent_south'),
                    record.get('spatial_extent_east'),
                    record.get('spatial_extent_north'),
                    record.get('source_file')
                ))
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to insert NASA record {record.get('model_id', 'unknown')}: {e}")
                error_count += 1
                conn.rollback()
                continue
        
        conn.commit()
        logger.info(f"NASA: {success_count} successful, {error_count} errors")
        return success_count, error_count
    except Exception as e:
        logger.error(f"Fatal error in load_nasa_data: {e}")
        conn.rollback()
        return success_count, error_count
    finally:
        if cur:
            cur.close()

def load_historical_data(conn, data_file: str) -> Tuple[int, int]:
    success_count = 0
    error_count = 0
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {data_file}: {e}")
        return 0, 0
    
    cur = None
    try:
        cur = conn.cursor()
        
        for record in data:
            try:
                if not record.get('event_id'):
                    logger.warning(f"Skipping record missing event_id")
                    error_count += 1
                    continue
                
                if not record.get('start_date'):
                    logger.warning(f"Skipping event {record.get('event_id')} missing required start_date")
                    error_count += 1
                    continue
                
                geom_wkt = prepare_geometry_wkt(record.get('affected_area_geom'))
                
                insert_sql = """
                INSERT INTO historical_flood_events (
                    event_id, event_name, event_type, start_date, end_date,
                    affected_area_geom, peak_discharge_cfs, peak_stage_feet,
                    total_damage_dollars, fatalities, properties_affected,
                    state_code, county_fips, data_source
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    CASE WHEN %s IS NOT NULL THEN ST_SetSRID(ST_GeomFromText(%s), 4326)::geography ELSE NULL END,
                    %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (event_id) DO UPDATE SET
                    total_damage_dollars = EXCLUDED.total_damage_dollars,
                    properties_affected = EXCLUDED.properties_affected,
                    load_timestamp = CURRENT_TIMESTAMP
                """
                
                cur.execute(insert_sql, (
                    record['event_id'],
                    record.get('event_name'),
                    record.get('event_type'),
                    record['start_date'],
                    record.get('end_date'),
                    geom_wkt,
                    geom_wkt,
                    record.get('peak_discharge_cfs'),
                    record.get('peak_stage_feet'),
                    record.get('total_damage_dollars'),
                    record.get('fatalities'),
                    record.get('properties_affected'),
                    record.get('state_code'),
                    record.get('county_fips'),
                    record.get('data_source')
                ))
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to insert historical event {record.get('event_id', 'unknown')}: {e}")
                error_count += 1
                conn.rollback()
                continue
        
        conn.commit()
        logger.info(f"Historical Events: {success_count} successful, {error_count} errors")
        return success_count, error_count
    except Exception as e:
        logger.error(f"Fatal error in load_historical_data: {e}")
        conn.rollback()
        return success_count, error_count
    finally:
        if cur:
            cur.close()

def main():
    conn = None
    try:
        conn = get_db_connection()
        
        base_dir = Path(__file__).parent.parent / "data" / "transformed"
        
        fema_success, fema_errors = load_fema_data(conn, str(base_dir / "fema_transformed.json"))
        noaa_success, noaa_errors = load_noaa_data(conn, str(base_dir / "noaa_transformed.json"))
        usgs_gauge_success, usgs_gauge_errors = load_usgs_gauges(conn, str(base_dir / "usgs_gauges_transformed.json"))
        usgs_obs_success, usgs_obs_errors = load_usgs_observations(conn, str(base_dir / "usgs_observations_transformed.json"))
        nasa_success, nasa_errors = load_nasa_data(conn, str(base_dir / "nasa_transformed.json"))
        historical_success, historical_errors = load_historical_data(conn, str(base_dir / "historical_transformed.json"))
        
        print(f"\nLoad Summary:")
        print(f"FEMA: {fema_success} successful, {fema_errors} errors")
        print(f"NOAA: {noaa_success} successful, {noaa_errors} errors")
        print(f"USGS Gauges: {usgs_gauge_success} successful, {usgs_gauge_errors} errors")
        print(f"USGS Observations: {usgs_obs_success} successful, {usgs_obs_errors} errors")
        print(f"NASA: {nasa_success} successful, {nasa_errors} errors")
        print(f"Historical: {historical_success} successful, {historical_errors} errors")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
