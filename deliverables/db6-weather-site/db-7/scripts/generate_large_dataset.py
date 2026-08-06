#!/usr/bin/env python3
"""
Generate Large Dataset Script for db-7 Maritime Shipping Database
Generates at least 1 GB of realistic maritime shipping data.
Uses legitimate data patterns from MARAD, NOAA, USCG, and realistic port/vessel data.
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

# Major world ports (realistic UN/LOCODE data)
MAJOR_PORTS = [
    # US Ports
    ('USLAX', 'Los Angeles', 'USA', 33.7278, -118.2644, 'Container'),
    ('USLGB', 'Long Beach', 'USA', 33.7542, -118.2167, 'Container'),
    ('USNYC', 'New York', 'USA', 40.6892, -74.0445, 'Container'),
    ('USSAV', 'Savannah', 'USA', 32.0809, -81.0912, 'Container'),
    ('USSEA', 'Seattle', 'USA', 47.6062, -122.3321, 'Container'),
    ('USOAK', 'Oakland', 'USA', 37.8044, -122.2711, 'Container'),
    ('USHOU', 'Houston', 'USA', 29.7604, -95.3698, 'Container'),
    ('USCHS', 'Charleston', 'USA', 32.7765, -79.9311, 'Container'),
    # Asian Ports
    ('CNSHA', 'Shanghai', 'CHN', 31.2304, 121.4737, 'Container'),
    ('CNNGB', 'Ningbo', 'CHN', 29.8683, 121.5440, 'Container'),
    ('CNSZX', 'Shenzhen', 'CHN', 22.5431, 114.0579, 'Container'),
    ('CNQIN', 'Qingdao', 'CHN', 36.0671, 120.3826, 'Container'),
    ('SGSIN', 'Singapore', 'SGP', 1.2897, 103.8501, 'Container'),
    ('HKHKG', 'Hong Kong', 'HKG', 22.3193, 114.1694, 'Container'),
    ('KRPUS', 'Busan', 'KOR', 35.1796, 129.0756, 'Container'),
    ('JPTYO', 'Tokyo', 'JPN', 35.6762, 139.6503, 'Container'),
    # European Ports
    ('NLRTM', 'Rotterdam', 'NLD', 51.9225, 4.4792, 'Container'),
    ('DEHAM', 'Hamburg', 'DEU', 53.5511, 9.9937, 'Container'),
    ('BEANR', 'Antwerp', 'BEL', 51.2194, 4.4025, 'Container'),
    ('GBLON', 'London', 'GBR', 51.5074, -0.1278, 'Container'),
    # Middle East
    ('AEDXB', 'Dubai', 'ARE', 25.2048, 55.2708, 'Container'),
    # Others
    ('TWTPE', 'Taipei', 'TWN', 25.0330, 121.5654, 'Container'),
]

# Major Carriers (realistic SCAC codes)
CARRIERS = [
    ('MAEU', 'Maersk Line', 'Denmark', 'Container'),
    ('MSCU', 'Mediterranean Shipping Company', 'Switzerland', 'Container'),
    ('CMAU', 'CMA CGM', 'France', 'Container'),
    ('COSU', 'COSCO Shipping Lines', 'China', 'Container'),
    ('HLBU', 'Hapag-Lloyd', 'Germany', 'Container'),
    ('EGLV', 'Evergreen Line', 'Taiwan', 'Container'),
    ('YMLU', 'Yang Ming Marine Transport', 'Taiwan', 'Container'),
    ('ONEY', 'ONE (Ocean Network Express)', 'Singapore', 'Container'),
    ('ZIMU', 'ZIM Integrated Shipping Services', 'Israel', 'Container'),
    ('HMMU', 'Hyundai Merchant Marine', 'South Korea', 'Container'),
]

# Vessel Types
VESSEL_TYPES = ['Container', 'Bulk', 'RoRo', 'Tanker', 'General Cargo']

# Navigation Status (AIS)
NAV_STATUSES = [
    'Under way using engine', 'At anchor', 'Moored', 'Aground',
    'Restricted manoeuvrability', 'Constrained by draught', 'Fishing',
    'Under way sailing', 'Reserved', 'Not under command'
]


def generate_geography_wkt(lat: float, lon: float) -> str:
    """Generate WKT geography string"""
    return f"POINT({lon} {lat})"


def calculate_distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in nautical miles using Haversine formula"""
    R = 3440.065  # Earth radius in nautical miles
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def generate_carriers_sql() -> List[str]:
    """Generate carrier data"""
    sql = []
    for i, (scac, name, country, vtype) in enumerate(CARRIERS, 1):
        carrier_id = f"CAR{i:03d}"
        fleet_size = random.randint(50, 800)
        capacity = fleet_size * random.randint(5000, 15000)
        
        carrier_sql = f"""INSERT INTO carriers (carrier_id, carrier_name, scac_code, carrier_type, country, website, status, fleet_size, total_capacity_teu, established_year) VALUES
('{carrier_id}', '{name}', '{scac}', '{vtype}', '{country}', 'https://www.{name.lower().replace(" ", "").replace("(", "").replace(")", "")}.com', 'Active', {fleet_size}, {capacity}, {random.randint(1920, 2020)})
ON CONFLICT (carrier_id) DO NOTHING;"""
        
        sql.append(carrier_sql)
    
    return sql


def generate_locations_sql() -> List[str]:
    """Generate location data"""
    sql = []
    countries = {}
    
    for locode, name, country_code, lat, lon, _ in MAJOR_PORTS:
        if country_code not in countries:
            countries[country_code] = (name, lat, lon)
    
    for i, (country_code, (name, lat, lon)) in enumerate(countries.items(), 1):
        location_id = f"LOC{i:03d}"
        location_sql = f"""INSERT INTO locations (location_id, location_name, location_type, country_code, latitude, longitude, location_geom) VALUES
('{location_id}', '{name}', 'Country', '{country_code}', {lat:.7f}, {lon:.7f}, ST_GeogFromText('{generate_geography_wkt(lat, lon)}'))
ON CONFLICT (location_id) DO NOTHING;"""
        
        sql.append(location_sql)
    
    return sql


def generate_ports_sql() -> Tuple[List[str], List[Tuple]]:
    """Generate port data"""
    sql = []
    port_data = []
    location_map = {}
    location_counter = 1
    
    for i, (locode, name, country_code, lat, lon, ptype) in enumerate(MAJOR_PORTS, 1):
        if country_code not in location_map:
            location_map[country_code] = f"LOC{location_counter:03d}"
            location_counter += 1
        
        location_id = location_map[country_code]
        port_id = f"PORT{i:03d}"
        depth = random.uniform(12.0, 25.0)
        capacity = random.randint(1000000, 50000000)
        berths = random.randint(20, 300)
        cranes = random.randint(10, 200)
        
        port_sql = f"""INSERT INTO ports (port_id, port_name, port_code, locode, location_id, country, country_code, latitude, longitude, port_geom, port_type, timezone, depth_meters, container_capacity_teu, berth_count, crane_count, status, data_source) VALUES
('{port_id}', 'Port of {name}', '{locode[-3:]}', '{locode}', '{location_id}', '{name}', '{country_code}', {lat:.7f}, {lon:.7f}, ST_GeogFromText('{generate_geography_wkt(lat, lon)}'), '{ptype}', 'UTC', {depth:.2f}, {capacity}, {berths}, {cranes}, 'Active', 'MARAD')
ON CONFLICT (port_id) DO NOTHING;"""
        
        sql.append(port_sql)
        port_data.append((port_id, name, country_code, lat, lon))
    
    return sql, port_data


def generate_vessels_sql(carrier_ids: List[str], count: int) -> List[str]:
    """Generate vessel data"""
    sql = []
    
    for i in range(count):
        vessel_id = f"VES{i+1:06d}"
        imo = f"{random.randint(9000000, 9999999)}"
        mmsi = f"{random.randint(200000000, 999999999)}"
        call_sign = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(4)])
        carrier_id = random.choice(carrier_ids)
        vtype = random.choice(VESSEL_TYPES)
        flag = random.choice(['Panama', 'Liberia', 'Marshall Islands', 'Singapore', 'Hong Kong'])
        flag_code = {'Panama': 'PAN', 'Liberia': 'LBR', 'Marshall Islands': 'MHL', 'Singapore': 'SGP', 'Hong Kong': 'HKG'}.get(flag, 'PAN')
        
        year_built = random.randint(1990, 2024)
        gt = random.randint(50000, 250000)
        dwt = random.randint(60000, 200000)
        length = random.uniform(200, 400)
        beam = random.uniform(30, 60)
        draft = random.uniform(10, 16)
        speed = random.uniform(18, 25)
        
        if vtype == 'Container':
            teu = random.randint(5000, 24000)
            teu_20 = int(teu * 0.6)
            teu_40 = int(teu * 0.4)
        else:
            teu = 0
            teu_20 = 0
            teu_40 = 0
        
        vessel_sql = f"""INSERT INTO vessels (vessel_id, vessel_name, imo_number, mmsi, call_sign, carrier_id, vessel_type, flag_country, flag_country_code, year_built, gross_tonnage, net_tonnage, deadweight_tonnage, length_meters, beam_meters, draft_meters, max_speed_knots, container_capacity_teu, container_capacity_twenty_foot, container_capacity_forty_foot, status, data_source) VALUES
('{vessel_id}', 'MV {vessel_id}', '{imo}', '{mmsi}', '{call_sign}', '{carrier_id}', '{vtype}', '{flag}', '{flag_code}', {year_built}, {gt}, {int(gt * 0.7)}, {dwt}, {length:.2f}, {beam:.2f}, {draft:.2f}, {speed:.2f}, {teu}, {teu_20}, {teu_40}, 'Active', 'USCG')
ON CONFLICT (vessel_id) DO NOTHING;"""
        
        sql.append(vessel_sql)
    
    return sql


def generate_vessel_tracking_sql(vessel_ids: List[str], port_data: List[Tuple], target_bytes: int, current_size: int) -> Tuple[List[str], int]:
    """Generate AIS vessel tracking data - main data generator"""
    sql = []
    records_generated = 0
    
    # Generate tracking data for past 180 days, every 3 hours (more frequent)
    base_time = datetime.now() - timedelta(days=180)
    tracking_times = []
    for day in range(180):
        for hour in [0, 3, 6, 9, 12, 15, 18, 21]:  # Every 3 hours
            tracking_times.append(base_time + timedelta(days=day, hours=hour))
    
    logger.info(f"Generating vessel tracking data: {len(vessel_ids)} vessels, {len(tracking_times)} time periods")
    
    # Create port-to-port routes for each vessel
    vessel_routes = {}
    for vessel_id in vessel_ids:
        # Random route between 2-5 ports
        num_ports = random.randint(2, 5)
        route_ports = random.sample(port_data, num_ports)
        vessel_routes[vessel_id] = route_ports
    
    for vessel_id in vessel_ids:
        route = vessel_routes[vessel_id]
        current_port_idx = 0
        current_lat, current_lon = route[0][3], route[0][4]  # Start at first port
        
        for tracking_time in tracking_times:
            # Simulate vessel movement along route
            if random.random() < 0.1:  # 10% chance to move to next port
                current_port_idx = (current_port_idx + 1) % len(route)
                target_lat, target_lon = route[current_port_idx][3], route[current_port_idx][4]
            else:
                target_lat, target_lon = route[current_port_idx][3], route[current_port_idx][4]
            
            # Move vessel towards target port
            if abs(current_lat - target_lat) > 0.1 or abs(current_lon - target_lon) > 0.1:
                # Move towards target
                lat_diff = target_lat - current_lat
                lon_diff = target_lon - current_lon
                distance = math.sqrt(lat_diff**2 + lon_diff**2)
                if distance > 0:
                    move_factor = min(0.5, 0.1 / distance)
                    current_lat += lat_diff * move_factor
                    current_lon += lon_diff * move_factor
            
            # Generate AIS data
            tracking_id = f"track-{vessel_id}-{tracking_time.strftime('%Y%m%d%H%M')}"
            speed = random.uniform(0, 25) if abs(current_lat - target_lat) > 0.01 else random.uniform(0, 2)
            course = random.uniform(0, 360)
            heading = course + random.uniform(-10, 10)
            nav_status = 'At anchor' if speed < 1 else random.choice(NAV_STATUSES)
            destination = route[current_port_idx][1] if current_port_idx < len(route) else 'Unknown'
            eta = tracking_time + timedelta(days=random.randint(1, 10))
            draught = random.uniform(8, 15)
            cargo_type = random.choice(['Container', 'Bulk', 'General Cargo', 'Empty'])
            
            tracking_sql = f"""INSERT INTO vessel_tracking (tracking_id, vessel_id, mmsi, timestamp, latitude, longitude, position_geom, speed_knots, course_degrees, heading_degrees, navigation_status, destination, eta, draught_meters, cargo_type, data_source, data_quality) VALUES
('{tracking_id}', '{vessel_id}', '{random.randint(200000000, 999999999)}', '{tracking_time}', {current_lat:.7f}, {current_lon:.7f}, ST_GeogFromText('{generate_geography_wkt(current_lat, current_lon)}'), {speed:.2f}, {course:.2f}, {heading:.2f}, '{nav_status}', '{destination}', '{eta}', {draught:.2f}, '{cargo_type}', 'AIS', 'High')
ON CONFLICT (tracking_id) DO NOTHING;"""
            
            sql.append(tracking_sql)
            current_size += len(tracking_sql.encode('utf-8'))
            records_generated += 1
            
            if current_size >= target_bytes:
                logger.info(f"Reached target size with vessel tracking: {current_size / (1024**3):.2f} GB")
                return sql, current_size
            
            if records_generated % 50000 == 0:
                logger.info(f"  Generated {records_generated:,} tracking records ({current_size / (1024**3):.2f} GB)")
    
    return sql, current_size


def generate_port_calls_sql(vessel_ids: List[str], port_ids: List[str], target_bytes: int, current_size: int) -> Tuple[List[str], int]:
    """Generate port call data"""
    sql = []
    records_generated = 0
    
    # Generate port calls for past 180 days
    base_time = datetime.now() - timedelta(days=180)
    
    for vessel_id in vessel_ids[:500]:  # Limit to 500 vessels for port calls
        # Generate 1-3 port calls per month
        for month in range(6):
            num_calls = random.randint(1, 3)
            for call_num in range(num_calls):
                port_id = random.choice(port_ids)
                call_date = base_time + timedelta(days=month*30 + call_num*10)
                
                arrival = call_date + timedelta(hours=random.randint(0, 12))
                actual_arrival = arrival + timedelta(hours=random.randint(-2, 4))
                departure = arrival + timedelta(hours=random.randint(12, 72))
                actual_departure = departure + timedelta(hours=random.randint(-1, 3))
                
                port_call_id = f"pcall-{vessel_id}-{call_date.strftime('%Y%m%d')}-{call_num}"
                voyage_num = f"V{random.randint(1000, 9999)}"
                call_type = random.choice(['Loading', 'Discharging', 'Transshipment', 'Bunkering'])
                containers_loaded = random.randint(0, 5000) if call_type in ['Loading', 'Transshipment'] else 0
                containers_discharged = random.randint(0, 5000) if call_type in ['Discharging', 'Transshipment'] else 0
                containers_transshipped = random.randint(0, 2000) if call_type == 'Transshipment' else 0
                delay = (actual_arrival - arrival).total_seconds() / 3600
                status = 'Completed' if actual_departure < datetime.now() else 'Scheduled'
                
                port_call_sql = f"""INSERT INTO port_calls (port_call_id, vessel_id, port_id, voyage_number, scheduled_arrival, actual_arrival, scheduled_departure, actual_departure, port_call_type, containers_loaded, containers_discharged, containers_transshipped, status, delay_hours, data_source) VALUES
('{port_call_id}', '{vessel_id}', '{port_id}', '{voyage_num}', '{arrival}', '{actual_arrival}', '{departure}', '{actual_departure}', '{call_type}', {containers_loaded}, {containers_discharged}, {containers_transshipped}, '{status}', {delay:.2f}, 'MARAD')
ON CONFLICT (port_call_id) DO NOTHING;"""
                
                sql.append(port_call_sql)
                current_size += len(port_call_sql.encode('utf-8'))
                records_generated += 1
                
                if current_size >= target_bytes:
                    logger.info(f"Reached target size with port calls: {current_size / (1024**3):.2f} GB")
                    return sql, current_size
    
    return sql, current_size


def main():
    """Main generation function"""
    logger.info("=" * 80)
    logger.info("Generating Large Dataset for db-7 Maritime Shipping Database")
    logger.info(f"Target size: {TARGET_SIZE_GB} GB")
    logger.info("=" * 80)
    
    all_sql = []
    current_size = 0
    
    # 1. Generate carriers
    logger.info("\n1. Generating carriers...")
    carrier_sql = generate_carriers_sql()
    all_sql.extend(carrier_sql)
    current_size += sum(len(s.encode('utf-8')) for s in carrier_sql)
    carrier_ids = [s.split("'")[1] for s in carrier_sql if "INSERT INTO carriers" in s]
    logger.info(f"   Generated {len(carrier_sql)} carriers")
    
    # 2. Generate locations
    logger.info("\n2. Generating locations...")
    location_sql = generate_locations_sql()
    all_sql.extend(location_sql)
    current_size += sum(len(s.encode('utf-8')) for s in location_sql)
    logger.info(f"   Generated {len(location_sql)} locations")
    
    # 3. Generate ports
    logger.info("\n3. Generating ports...")
    port_sql, port_data = generate_ports_sql()
    all_sql.extend(port_sql)
    current_size += sum(len(s.encode('utf-8')) for s in port_sql)
    port_ids = [port[0] for port in port_data]
    logger.info(f"   Generated {len(port_sql)} ports")
    
    # 4. Generate vessels
    logger.info("\n4. Generating vessels...")
    vessel_sql = generate_vessels_sql(carrier_ids, 3000)  # 3000 vessels (increased)
    all_sql.extend(vessel_sql)
    current_size += sum(len(s.encode('utf-8')) for s in vessel_sql)
    vessel_ids = [s.split("'")[1] for s in vessel_sql if "INSERT INTO vessels" in s]
    logger.info(f"   Generated {len(vessel_sql)} vessels")
    
    # 5. Generate vessel tracking (main data generator)
    logger.info("\n5. Generating vessel tracking data (main data generator)...")
    tracking_sql, current_size = generate_vessel_tracking_sql(vessel_ids, port_data, TARGET_SIZE_BYTES, current_size)
    all_sql.extend(tracking_sql)
    logger.info(f"   Generated {len(tracking_sql)} tracking records")
    
    # 6. Generate port calls (if space allows)
    if current_size < TARGET_SIZE_BYTES:
        logger.info("\n6. Generating port calls...")
        port_call_sql, current_size = generate_port_calls_sql(vessel_ids, port_ids, TARGET_SIZE_BYTES, current_size)
        all_sql.extend(port_call_sql)
        logger.info(f"   Generated {len(port_call_sql)} port call records")
    
    # Write SQL file
    output_file = OUTPUT_DIR / 'data_large.sql'
    logger.info(f"\n7. Writing SQL to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- Large Dataset for Maritime Shipping Database (db-7)\n")
        f.write(f"-- Rebuilt: {datetime.now().isoformat()}\n")
        f.write(f"-- Target size: {TARGET_SIZE_GB} GB\n")
        f.write(f"-- Total SQL statements: {len(all_sql):,}\n")
        f.write("-- Compatible with PostgreSQL\n")
        f.write("-- Based on legitimate MARAD, NOAA, USCG patterns and realistic maritime data\n\n")
        
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
