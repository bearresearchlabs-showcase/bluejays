import os
import json
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any
from decimal import Decimal
from pathlib import Path

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('PG_HOST', 'localhost'),
        port=os.getenv('PG_PORT', '5432'),
        user=os.getenv('PG_USER', 'postgres'),
        password=os.getenv('PG_PASSWORD', ''),
        database=os.getenv('PG_DATABASE', 'db_16')
    )
    return conn

def convert_geometry(geom_wkt: str):
    if geom_wkt:
        return f"ST_GeogFromText('SRID=4326;{geom_wkt}')"
    return None

def load_fema_data(conn, data_file: str):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    for record in data:
        geom_sql = convert_geometry(record.get('zone_geom'))
        
        if geom_sql:
            insert_sql = """
            INSERT INTO fema_flood_zones (
                zone_id, zone_code, zone_description, base_flood_elevation,
                zone_geom, community_id, community_name, state_code, county_fips,
                effective_date, map_panel, source_file, source_crs, target_crs,
                spatial_extent_west, spatial_extent_south, spatial_extent_east,
                spatial_extent_north, transformation_status
            ) VALUES (
                %s, %s, %s, %s, {}, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (zone_id) DO UPDATE SET
                zone_code = EXCLUDED.zone_code,
                zone_description = EXCLUDED.zone_description,
                base_flood_elevation = EXCLUDED.base_flood_elevation,
                zone_geom = EXCLUDED.zone_geom,
                load_timestamp = CURRENT_TIMESTAMP
            """.format(geom_sql)
        else:
            insert_sql = """
            INSERT INTO fema_flood_zones (
                zone_id, zone_code, zone_description, base_flood_elevation,
                zone_geom, community_id, community_name, state_code, county_fips,
                effective_date, map_panel, source_file, source_crs, target_crs,
                spatial_extent_west, spatial_extent_south, spatial_extent_east,
                spatial_extent_north, transformation_status
            ) VALUES (
                %s, %s, %s, %s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (zone_id) DO UPDATE SET
                zone_code = EXCLUDED.zone_code,
                zone_description = EXCLUDED.zone_description,
                base_flood_elevation = EXCLUDED.base_flood_elevation,
                load_timestamp = CURRENT_TIMESTAMP
            """
        
        cur.execute(insert_sql, (
            record['zone_id'],
            record['zone_code'],
            record['zone_description'],
            record['base_flood_elevation'],
            record['community_id'],
            record['community_name'],
            record['state_code'],
            record['county_fips'],
            record.get('effective_date'),
            record.get('map_panel'),
            record['source_file'],
            record['source_crs'],
            record['target_crs'],
            record.get('spatial_extent_west'),
            record.get('spatial_extent_south'),
            record.get('spatial_extent_east'),
            record.get('spatial_extent_north'),
            record['transformation_status']
        ))
    
    conn.commit()
    cur.close()
    return len(data)

def load_noaa_data(conn, data_file: str):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    for record in data:
        geom_sql = convert_geometry(record.get('station_geom'))
        
        if geom_sql:
            insert_sql = """
            INSERT INTO noaa_sea_level_rise (
                projection_id, station_id, station_name, station_latitude,
                station_longitude, station_geom, projection_year, scenario,
                sea_level_rise_feet, confidence_level, high_tide_flooding_days,
                data_source
            ) VALUES (
                %s, %s, %s, %s, %s, {}, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (projection_id) DO UPDATE SET
                sea_level_rise_feet = EXCLUDED.sea_level_rise_feet,
                high_tide_flooding_days = EXCLUDED.high_tide_flooding_days,
                load_timestamp = CURRENT_TIMESTAMP
            """.format(geom_sql)
        else:
            insert_sql = """
            INSERT INTO noaa_sea_level_rise (
                projection_id, station_id, station_name, station_latitude,
                station_longitude, station_geom, projection_year, scenario,
                sea_level_rise_feet, confidence_level, high_tide_flooding_days,
                data_source
            ) VALUES (
                %s, %s, %s, %s, %s, NULL, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (projection_id) DO UPDATE SET
                sea_level_rise_feet = EXCLUDED.sea_level_rise_feet,
                high_tide_flooding_days = EXCLUDED.high_tide_flooding_days,
                load_timestamp = CURRENT_TIMESTAMP
            """
        
        cur.execute(insert_sql, (
            record['projection_id'],
            record['station_id'],
            record['station_name'],
            record['station_latitude'],
            record['station_longitude'],
            record['projection_year'],
            record['scenario'],
            record['sea_level_rise_feet'],
            record['confidence_level'],
            record['high_tide_flooding_days'],
            record['data_source']
        ))
    
    conn.commit()
    cur.close()
    return len(data)

def load_usgs_gauges(conn, data_file: str):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    for record in data:
        geom_sql = convert_geometry(record.get('gauge_geom'))
        
        if geom_sql:
            insert_sql = """
            INSERT INTO usgs_streamflow_gauges (
                gauge_id, gauge_name, gauge_latitude, gauge_longitude,
                gauge_geom, drainage_area_sq_miles, flood_stage_feet,
                moderate_flood_stage_feet, major_flood_stage_feet,
                state_code, county_name, river_name, active_status,
                first_observation_date, last_observation_date, update_frequency_minutes
            ) VALUES (
                %s, %s, %s, %s, {}, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (gauge_id) DO UPDATE SET
                flood_stage_feet = EXCLUDED.flood_stage_feet,
                moderate_flood_stage_feet = EXCLUDED.moderate_flood_stage_feet,
                major_flood_stage_feet = EXCLUDED.major_flood_stage_feet,
                last_observation_date = EXCLUDED.last_observation_date,
                load_timestamp = CURRENT_TIMESTAMP
            """.format(geom_sql)
        else:
            insert_sql = """
            INSERT INTO usgs_streamflow_gauges (
                gauge_id, gauge_name, gauge_latitude, gauge_longitude,
                gauge_geom, drainage_area_sq_miles, flood_stage_feet,
                moderate_flood_stage_feet, major_flood_stage_feet,
                state_code, county_name, river_name, active_status,
                first_observation_date, last_observation_date, update_frequency_minutes
            ) VALUES (
                %s, %s, %s, %s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (gauge_id) DO UPDATE SET
                flood_stage_feet = EXCLUDED.flood_stage_feet,
                moderate_flood_stage_feet = EXCLUDED.moderate_flood_stage_feet,
                major_flood_stage_feet = EXCLUDED.major_flood_stage_feet,
                last_observation_date = EXCLUDED.last_observation_date,
                load_timestamp = CURRENT_TIMESTAMP
            """
        
        cur.execute(insert_sql, (
            record['gauge_id'],
            record['gauge_name'],
            record['gauge_latitude'],
            record['gauge_longitude'],
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
    
    conn.commit()
    cur.close()
    return len(data)

def load_usgs_observations(conn, data_file: str):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    batch_size = 1000
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        
        values = []
        for record in batch:
            values.append((
                record['observation_id'],
                record['gauge_id'],
                record.get('observation_time'),
                record.get('gauge_height_feet'),
                record.get('discharge_cfs'),
                record.get('flood_category'),
                record.get('water_temperature_f')
            ))
        
        insert_sql = """
        INSERT INTO usgs_streamflow_observations (
            observation_id, gauge_id, observation_time, gauge_height_feet,
            discharge_cfs, flood_category, water_temperature_f
        ) VALUES %s
        ON CONFLICT (observation_id) DO UPDATE SET
            gauge_height_feet = EXCLUDED.gauge_height_feet,
            discharge_cfs = EXCLUDED.discharge_cfs,
            flood_category = EXCLUDED.flood_category,
            load_timestamp = CURRENT_TIMESTAMP
        """
        
        execute_values(cur, insert_sql, values)
    
    conn.commit()
    cur.close()
    return len(data)

def load_nasa_data(conn, data_file: str):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    batch_size = 1000
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        
        for record in batch:
            geom_sql = convert_geometry(record.get('grid_cell_geom'))
            
            if geom_sql:
                insert_sql = """
                INSERT INTO nasa_flood_models (
                    model_id, forecast_time, grid_cell_geom, inundation_depth_feet,
                    flood_probability, flood_severity, model_resolution_meters, data_source
                ) VALUES (
                    %s, %s, {}, %s, %s, %s, %s, %s
                ) ON CONFLICT (model_id) DO UPDATE SET
                    forecast_time = EXCLUDED.forecast_time,
                    inundation_depth_feet = EXCLUDED.inundation_depth_feet,
                    flood_probability = EXCLUDED.flood_probability,
                    flood_severity = EXCLUDED.flood_severity,
                    load_timestamp = CURRENT_TIMESTAMP
                """.format(geom_sql)
            else:
                insert_sql = """
                INSERT INTO nasa_flood_models (
                    model_id, forecast_time, grid_cell_geom, inundation_depth_feet,
                    flood_probability, flood_severity, model_resolution_meters, data_source
                ) VALUES (
                    %s, %s, NULL, %s, %s, %s, %s, %s
                ) ON CONFLICT (model_id) DO UPDATE SET
                    forecast_time = EXCLUDED.forecast_time,
                    inundation_depth_feet = EXCLUDED.inundation_depth_feet,
                    flood_probability = EXCLUDED.flood_probability,
                    flood_severity = EXCLUDED.flood_severity,
                    load_timestamp = CURRENT_TIMESTAMP
                """
            
            cur.execute(insert_sql, (
                record['model_id'],
                record.get('forecast_time'),
                record.get('inundation_depth_feet'),
                record.get('flood_probability'),
                record.get('flood_severity'),
                record.get('model_resolution_meters'),
                record.get('data_source', 'NASA_GFMS')
            ))
    
    conn.commit()
    cur.close()
    return len(data)

def load_historical_data(conn, data_file: str):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    
    for record in data:
        geom_sql = convert_geometry(record.get('event_geom'))
        
        if geom_sql:
            insert_sql = """
            INSERT INTO historical_flood_events (
                event_id, event_date, event_type, severity, magnitude,
                latitude, longitude, event_geom, depth_feet,
                affected_area_sq_miles, damage_estimate_dollars, data_source
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, {}, %s, %s, %s, %s
            ) ON CONFLICT (event_id) DO UPDATE SET
                severity = EXCLUDED.severity,
                magnitude = EXCLUDED.magnitude,
                damage_estimate_dollars = EXCLUDED.damage_estimate_dollars,
                load_timestamp = CURRENT_TIMESTAMP
            """.format(geom_sql)
        else:
            insert_sql = """
            INSERT INTO historical_flood_events (
                event_id, event_date, event_type, severity, magnitude,
                latitude, longitude, event_geom, depth_feet,
                affected_area_sq_miles, damage_estimate_dollars, data_source
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, %s, %s
            ) ON CONFLICT (event_id) DO UPDATE SET
                severity = EXCLUDED.severity,
                magnitude = EXCLUDED.magnitude,
                damage_estimate_dollars = EXCLUDED.damage_estimate_dollars,
                load_timestamp = CURRENT_TIMESTAMP
            """
        
        cur.execute(insert_sql, (
            record['event_id'],
            record.get('event_date'),
            record['event_type'],
            record['severity'],
            record.get('magnitude'),
            record['latitude'],
            record['longitude'],
            record.get('depth_feet'),
            record.get('affected_area_sq_miles'),
            record.get('damage_estimate_dollars'),
            record['data_source']
        ))
    
    conn.commit()
    cur.close()
    return len(data)

def main():
    conn = get_db_connection()
    
    base_dir = Path(__file__).parent.parent / "data" / "transformed"
    
    fema_count = load_fema_data(conn, str(base_dir / "fema_transformed.json"))
    noaa_count = load_noaa_data(conn, str(base_dir / "noaa_transformed.json"))
    usgs_gauge_count = load_usgs_gauges(conn, str(base_dir / "usgs_gauges_transformed.json"))
    usgs_obs_count = load_usgs_observations(conn, str(base_dir / "usgs_observations_transformed.json"))
    nasa_count = load_nasa_data(conn, str(base_dir / "nasa_transformed.json"))
    historical_count = load_historical_data(conn, str(base_dir / "historical_transformed.json"))
    
    conn.close()
    
    print(f"Loaded {fema_count} FEMA records")
    print(f"Loaded {noaa_count} NOAA records")
    print(f"Loaded {usgs_gauge_count} USGS gauges")
    print(f"Loaded {usgs_obs_count} USGS observations")
    print(f"Loaded {nasa_count} NASA records")
    print(f"Loaded {historical_count} historical records")

if __name__ == "__main__":
    from pathlib import Path
    main()
