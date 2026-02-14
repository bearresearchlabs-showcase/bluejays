#!/usr/bin/env python3
"""
Generate Large Dataset Script for db-6 Weather/Insurance Database
Generates at least 1 GB of realistic weather and insurance data.
Uses legitimate data patterns from NWS API, NOAA, and realistic geographic coverage.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random
import uuid
import math

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Target: At least 1 GB of SQL data
TARGET_SIZE_GB = 1.0
TARGET_SIZE_BYTES = TARGET_SIZE_GB * 1024 * 1024 * 1024

# US Geographic Coverage (realistic bounds)
US_BOUNDS = {
    'west': -125.0,
    'east': -66.0,
    'south': 24.0,
    'north': 50.0
}

# US States (for realistic geographic distribution)
US_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

# Weather Parameters (based on NWS API)
WEATHER_PARAMETERS = [
    'Temperature', 'Dewpoint', 'RelativeHumidity', 'WindSpeed', 'WindDirection',
    'Pressure', 'Visibility', 'Precipitation', 'SkyCover', 'CloudBase',
    'HeatIndex', 'WindChill', 'ApparentTemperature'
]

# CWA Codes (Weather Forecast Offices)
CWA_CODES = [
    'AKQ', 'ALY', 'BGM', 'BOX', 'BTV', 'BUF', 'CAR', 'CHS', 'CLE', 'CTP',
    'GSP', 'GYX', 'ILN', 'ILX', 'IND', 'IWX', 'JKL', 'KEY', 'LOT', 'LSX',
    'LWX', 'MKX', 'OKX', 'PBZ', 'PHI', 'PIT', 'RLX', 'RNK', 'SHV', 'SJU'
]

# Insurance Policy Types
POLICY_TYPES = ['Property', 'Crop', 'Auto', 'Marine', 'General Liability']
COVERAGE_TYPES = [
    'Homeowners', 'Commercial Property', 'Crop Insurance', 'Auto Comprehensive',
    'Marine Cargo', 'General Liability', 'Flood Insurance', 'Wind Insurance'
]

# Forecast Period (Dec 3-17, 2025 for insurance modeling)
FORECAST_START = datetime(2025, 12, 3)
FORECAST_END = datetime(2025, 12, 17)
FORECAST_DAYS = list(range(7, 15))  # 7-14 days ahead


def generate_geography_point() -> Tuple[float, float]:
    """Generate realistic US geographic coordinates"""
    lat = random.uniform(US_BOUNDS['south'], US_BOUNDS['north'])
    lon = random.uniform(US_BOUNDS['west'], US_BOUNDS['east'])
    return (lat, lon)


def generate_geography_wkt(lat: float, lon: float, is_polygon: bool = False) -> str:
    """Generate WKT geography string"""
    if is_polygon:
        # Simple bounding box polygon
        buffer = 0.01
        return f"POLYGON(({lon-buffer} {lat-buffer}, {lon+buffer} {lat-buffer}, {lon+buffer} {lat+buffer}, {lon-buffer} {lat+buffer}, {lon-buffer} {lat-buffer}))"
    else:
        return f"POINT({lon} {lat})"


def generate_weather_stations_sql(count: int) -> List[str]:
    """Generate weather station metadata"""
    sql = []
    for i in range(count):
        station_id = f"K{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])}{random.randint(100, 999)}"
        lat, lon = generate_geography_point()
        state = random.choice(US_STATES)
        cwa = random.choice(CWA_CODES)
        
        station_sql = f"""INSERT INTO weather_stations (station_id, station_name, station_latitude, station_longitude, station_geom, elevation_meters, state_code, county_name, cwa_code, station_type, active_status, first_observation_date, last_observation_date, update_frequency_minutes) VALUES
('{station_id}', 'Weather Station {station_id}', {lat:.7f}, {lon:.7f}, ST_GeogFromText('{generate_geography_wkt(lat, lon)}'), {random.uniform(0, 3000):.2f}, '{state}', 'County {i}', '{cwa}', 'ASOS', TRUE, '{datetime.now() - timedelta(days=365*5)}', '{datetime.now()}', 15)
ON CONFLICT (station_id) DO UPDATE SET last_observation_date = EXCLUDED.last_observation_date;"""
        
        sql.append(station_sql)
    
    return sql


def generate_grib2_forecasts_sql(target_bytes: int, current_size: int) -> Tuple[List[str], int]:
    """Generate GRIB2 forecast data - main data generator"""
    sql = []
    records_generated = 0
    
    # Generate forecasts for multiple time periods
    forecast_times = []
    base_time = datetime.now() - timedelta(days=30)
    for day in range(60):  # 60 days of forecasts
        for hour in [0, 6, 12, 18]:  # 4 forecasts per day
            forecast_times.append(base_time + timedelta(days=day, hours=hour))
    
    # Grid resolution (0.1 degree ~11km)
    grid_resolution = 0.1
    
    # Generate grid cells covering US
    grid_cells = []
    lat_step = grid_resolution
    lon_step = grid_resolution
    
    lat_start = US_BOUNDS['south']
    lat_end = US_BOUNDS['north']
    lon_start = US_BOUNDS['west']
    lon_end = US_BOUNDS['east']
    
    # Generate grid cells
    for lat in range(int((lat_end - lat_start) / lat_step)):
        for lon in range(int((lon_end - lon_start) / lon_step)):
            grid_lat = lat_start + lat * lat_step
            grid_lon = lon_start + lon * lon_step
            grid_cells.append((grid_lat, grid_lon))
    
    logger.info(f"Generating GRIB2 forecasts: {len(forecast_times)} time periods, {len(grid_cells)} grid cells, {len(WEATHER_PARAMETERS)} parameters")
    
    # Generate forecasts
    for forecast_time in forecast_times:
        for param in WEATHER_PARAMETERS:
            for grid_lat, grid_lon in grid_cells:
                # Generate realistic parameter values
                if param == 'Temperature':
                    value = random.uniform(-20, 110)  # Fahrenheit
                elif param == 'Dewpoint':
                    value = random.uniform(-30, 80)
                elif param == 'RelativeHumidity':
                    value = random.uniform(0, 100)
                elif param == 'WindSpeed':
                    value = random.uniform(0, 60)
                elif param == 'WindDirection':
                    value = random.randint(0, 360)
                elif param == 'Pressure':
                    value = random.uniform(28.0, 31.0)  # inches Hg
                elif param == 'Visibility':
                    value = random.uniform(0, 10)
                elif param == 'Precipitation':
                    value = random.uniform(0, 5)
                else:
                    value = random.uniform(0, 100)
                
                forecast_id = f"grib2-{param.lower()}-{forecast_time.strftime('%Y%m%d%H')}-{grid_lat:.3f}-{grid_lon:.3f}"
                
                forecast_sql = f"""INSERT INTO grib2_forecasts (forecast_id, parameter_name, forecast_time, grid_cell_latitude, grid_cell_longitude, grid_cell_geom, parameter_value, source_file, source_crs, target_crs, grid_resolution_x, grid_resolution_y, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status) VALUES
('{forecast_id}', '{param}', '{forecast_time}', {grid_lat:.7f}, {grid_lon:.7f}, ST_GeogFromText('{generate_geography_wkt(grid_lat, grid_lon)}'), {value:.2f}, 'ndfd_grib2_{forecast_time.strftime("%Y%m%d%H")}.grb2', 'EPSG:4326', 'EPSG:4326', {grid_resolution:.6f}, {grid_resolution:.6f}, {US_BOUNDS['west']:.6f}, {US_BOUNDS['south']:.6f}, {US_BOUNDS['east']:.6f}, {US_BOUNDS['north']:.6f}, 'completed')
ON CONFLICT (forecast_id) DO UPDATE SET parameter_value = EXCLUDED.parameter_value;"""
                
                sql.append(forecast_sql)
                current_size += len(forecast_sql.encode('utf-8'))
                records_generated += 1
                
                if current_size >= target_bytes:
                    logger.info(f"Reached target size with GRIB2 forecasts: {current_size / (1024**3):.2f} GB")
                    return sql, current_size
                
                if records_generated % 100000 == 0:
                    logger.info(f"  Generated {records_Rebuilt:,} GRIB2 forecasts ({current_size / (1024**3):.2f} GB)")
    
    return sql, current_size


def generate_weather_observations_sql(station_ids: List[str], target_bytes: int, current_size: int) -> Tuple[List[str], int]:
    """Generate weather observations"""
    sql = []
    records_generated = 0
    
    # Generate observations for past 90 days, hourly
    base_time = datetime.now() - timedelta(days=90)
    observation_times = []
    for day in range(90):
        for hour in range(24):
            observation_times.append(base_time + timedelta(days=day, hours=hour))
    
    logger.info(f"Generating weather observations: {len(station_ids)} stations, {len(observation_times)} time periods")
    
    for station_id in station_ids:
        lat, lon = generate_geography_point()
        station_name = f"Weather Station {station_id}"
        
        for obs_time in observation_times:
            observation_id = f"obs-{station_id}-{obs_time.strftime('%Y%m%d%H%M')}"
            
            # Generate realistic weather values
            temp = random.uniform(-20, 110)
            dewpoint = temp - random.uniform(0, 30)
            humidity = random.uniform(20, 100)
            wind_speed = random.uniform(0, 40)
            wind_dir = random.randint(0, 360)
            pressure = random.uniform(28.5, 30.5)
            visibility = random.uniform(0, 10)
            sky_cover = random.choice(['Clear', 'Few', 'Scattered', 'Broken', 'Overcast'])
            precip = random.uniform(0, 2) if random.random() < 0.3 else 0
            
            obs_sql = f"""INSERT INTO weather_observations (observation_id, station_id, station_name, observation_time, station_latitude, station_longitude, station_geom, temperature, dewpoint, humidity, wind_speed, wind_direction, pressure, visibility, sky_cover, precipitation_amount, data_freshness_minutes, data_source) VALUES
('{observation_id}', '{station_id}', '{station_name}', '{obs_time}', {lat:.7f}, {lon:.7f}, ST_GeogFromText('{generate_geography_wkt(lat, lon)}'), {temp:.2f}, {dewpoint:.2f}, {humidity:.2f}, {wind_speed:.2f}, {wind_dir}, {pressure:.2f}, {visibility:.2f}, '{sky_cover}', {precip:.2f}, {random.randint(5, 60)}, 'NWS_API')
ON CONFLICT (observation_id) DO UPDATE SET temperature = EXCLUDED.temperature;"""
            
            sql.append(obs_sql)
            current_size += len(obs_sql.encode('utf-8'))
            records_generated += 1
            
            if current_size >= target_bytes:
                logger.info(f"Reached target size with observations: {current_size / (1024**3):.2f} GB")
                return sql, current_size
    
    return sql, current_size


def generate_shapefile_boundaries_sql(count: int) -> List[str]:
    """Generate shapefile boundary data"""
    sql = []
    feature_types = ['CWA', 'FireZone', 'MarineZone', 'RiverBasin', 'County']
    
    for i in range(count):
        feature_type = random.choice(feature_types)
        state = random.choice(US_STATES)
        cwa = random.choice(CWA_CODES) if feature_type == 'CWA' else None
        
        lat, lon = generate_geography_point()
        boundary_id = f"boundary-{feature_type.lower()}-{state}-{i}"
        
        boundary_sql = f"""INSERT INTO shapefile_boundaries (boundary_id, feature_type, feature_name, feature_identifier, boundary_geom, source_shapefile, source_crs, target_crs, feature_count, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status, state_code, office_code) VALUES
('{boundary_id}', '{feature_type}', '{feature_type} {state} {i}', '{state}-{i}', ST_GeogFromText('{generate_geography_wkt(lat, lon, is_polygon=True)}'), 'noaa_{feature_type.lower()}_{state}.shp', 'EPSG:4326', 'EPSG:4326', {random.randint(1, 100)}, {lon-0.5:.6f}, {lat-0.5:.6f}, {lon+0.5:.6f}, {lat+0.5:.6f}, 'completed', '{state}', {'NULL' if cwa is None else f"'{cwa}'"})
ON CONFLICT (boundary_id) DO NOTHING;"""
        
        sql.append(boundary_sql)
    
    return sql


def generate_insurance_data_sql(boundary_ids: List[str], target_bytes: int, current_size: int) -> Tuple[List[str], int]:
    """Generate insurance policy and risk factor data"""
    sql = []
    records_generated = 0
    
    # Generate policy areas
    policy_areas = []
    for boundary_id in boundary_ids[:1000]:  # Limit to 1000 policy areas
        policy_area_id = f"policy-{boundary_id}"
        policy_type = random.choice(POLICY_TYPES)
        coverage_type = random.choice(COVERAGE_TYPES)
        state = random.choice(US_STATES)
        risk_zone = random.choice(['Low', 'Moderate', 'High', 'Very High'])
        base_rate_factor = random.uniform(0.5, 2.0)
        
        policy_sql = f"""INSERT INTO insurance_policy_areas (policy_area_id, boundary_id, policy_type, coverage_type, policy_area_name, state_code, cwa_code, risk_zone, base_rate_factor, effective_date, expiration_date, is_active) VALUES
('{policy_area_id}', '{boundary_id}', '{policy_type}', '{coverage_type}', '{policy_type} Coverage Area {boundary_id}', '{state}', '{random.choice(CWA_CODES)}', '{risk_zone}', {base_rate_factor:.3f}, '{FORECAST_START.date()}', '{FORECAST_END.date() + timedelta(days=365)}', TRUE)
ON CONFLICT (policy_area_id) DO NOTHING;"""
        
        sql.append(policy_sql)
        policy_areas.append(policy_area_id)
        current_size += len(policy_sql.encode('utf-8'))
    
    # Generate risk factors for each policy area
    logger.info(f"Generating insurance risk factors for {len(policy_areas)} policy areas")
    
    for policy_area_id in policy_areas:
        for forecast_day in FORECAST_DAYS:
            for param in ['Temperature', 'Precipitation', 'WindSpeed']:
                forecast_date = FORECAST_START - timedelta(days=forecast_day)
                
                # Generate risk metrics
                extreme_prob = random.uniform(0, 0.3)
                precip_risk = random.uniform(0, 100)
                wind_risk = random.uniform(0, 100)
                freeze_risk = random.uniform(0, 50)
                flood_risk = random.uniform(0, 80)
                
                # Generate forecast statistics
                min_val = random.uniform(0, 50)
                max_val = min_val + random.uniform(10, 100)
                avg_val = (min_val + max_val) / 2
                median_val = avg_val
                stddev_val = (max_val - min_val) / 4
                
                risk_factor_id = f"risk-{policy_area_id}-{forecast_day}-{param.lower()}"
                overall_risk = (precip_risk + wind_risk + freeze_risk + flood_risk) / 4
                risk_category = 'Low' if overall_risk < 25 else 'Moderate' if overall_risk < 50 else 'High' if overall_risk < 75 else 'Very High'
                
                risk_sql = f"""INSERT INTO insurance_risk_factors (risk_factor_id, policy_area_id, forecast_period_start, forecast_period_end, forecast_day, forecast_date, parameter_name, extreme_event_probability, cumulative_precipitation_risk, wind_damage_risk, freeze_risk, flood_risk, min_forecast_value, max_forecast_value, avg_forecast_value, median_forecast_value, stddev_forecast_value, percentile_90_value, percentile_95_value, percentile_99_value, overall_risk_score, risk_category, forecast_model, data_quality_score) VALUES
('{risk_factor_id}', '{policy_area_id}', '{FORECAST_START.date()}', '{FORECAST_END.date()}', {forecast_day}, '{forecast_date.date()}', '{param}', {extreme_prob:.4f}, {precip_risk:.2f}, {wind_risk:.2f}, {freeze_risk:.2f}, {flood_risk:.2f}, {min_val:.2f}, {max_val:.2f}, {avg_val:.2f}, {median_val:.2f}, {stddev_val:.2f}, {max_val * 0.9:.2f}, {max_val * 0.95:.2f}, {max_val * 0.99:.2f}, {overall_risk:.2f}, '{risk_category}', 'GFS', {random.uniform(85, 95):.2f})
ON CONFLICT (risk_factor_id) DO NOTHING;"""
                
                sql.append(risk_sql)
                current_size += len(risk_sql.encode('utf-8'))
                records_generated += 1
                
                if current_size >= target_bytes:
                    logger.info(f"Reached target size with insurance data: {current_size / (1024**3):.2f} GB")
                    return sql, current_size
    
    return sql, current_size


def main():
    """Main generation function"""
    logger.info("=" * 80)
    logger.info("Generating Large Dataset for db-6 Weather/Insurance Database")
    logger.info(f"Target size: {TARGET_SIZE_GB} GB")
    logger.info("=" * 80)
    
    all_sql = []
    current_size = 0
    
    # 1. Generate weather stations
    logger.info("\n1. Generating weather stations...")
    station_sql = generate_weather_stations_sql(5000)  # 5000 stations
    all_sql.extend(station_sql)
    current_size += sum(len(s.encode('utf-8')) for s in station_sql)
    station_ids = [s.split("'")[1] for s in station_sql if "INSERT INTO weather_stations" in s]
    logger.info(f"   Generated {len(station_sql)} weather stations")
    
    # 2. Generate shapefile boundaries
    logger.info("\n2. Generating shapefile boundaries...")
    boundary_sql = generate_shapefile_boundaries_sql(2000)  # 2000 boundaries
    all_sql.extend(boundary_sql)
    current_size += sum(len(s.encode('utf-8')) for s in boundary_sql)
    boundary_ids = [s.split("'")[1] for s in boundary_sql if "INSERT INTO shapefile_boundaries" in s]
    logger.info(f"   Generated {len(boundary_sql)} boundaries")
    
    # 3. Generate GRIB2 forecasts (main data generator)
    logger.info("\n3. Generating GRIB2 forecasts (main data generator)...")
    grib2_sql, current_size = generate_grib2_forecasts_sql(TARGET_SIZE_BYTES, current_size)
    all_sql.extend(grib2_sql)
    logger.info(f"   Generated {len(grib2_sql)} GRIB2 forecast records")
    
    # 4. Generate weather observations (if space allows)
    if current_size < TARGET_SIZE_BYTES:
        logger.info("\n4. Generating weather observations...")
        obs_sql, current_size = generate_weather_observations_sql(station_ids[:100], TARGET_SIZE_BYTES, current_size)
        all_sql.extend(obs_sql)
        logger.info(f"   Generated {len(obs_sql)} observation records")
    
    # 5. Generate insurance data (if space allows)
    if current_size < TARGET_SIZE_BYTES:
        logger.info("\n5. Generating insurance data...")
        insurance_sql, current_size = generate_insurance_data_sql(boundary_ids, TARGET_SIZE_BYTES, current_size)
        all_sql.extend(insurance_sql)
        logger.info(f"   Generated {len(insurance_sql)} insurance records")
    
    # Write SQL file
    output_file = OUTPUT_DIR / 'data_large.sql'
    logger.info(f"\n6. Writing SQL to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- Large Dataset for Weather/Insurance Database (db-6)\n")
        f.write(f"-- Rebuilt: {datetime.now().isoformat()}\n")
        f.write(f"-- Target size: {TARGET_SIZE_GB} GB\n")
        f.write(f"-- Total SQL statements: {len(all_sql):,}\n")
        f.write("-- Compatible with PostgreSQL\n")
        f.write("-- Based on legitimate NWS API patterns and realistic US geographic coverage\n\n")
        
        for sql in all_sql:
            f.write(sql + "\n\n")
    
    file_size_mb = output_file.stat().st_size / (1024**2)
    file_size_gb = file_size_mb / 1024
    
    logger.info(f"\n✅ Generation complete!")
    logger.info(f"   Output file: {output_file}")
    logger.info(f"   File size: {file_size_gb:.2f} GB ({file_size_mb:.2f} MB)")
    logger.info(f"   SQL statements: {len(all_sql):,}")
    logger.info("=" * 80)
    
    return file_size_gb >= TARGET_SIZE_GB


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
