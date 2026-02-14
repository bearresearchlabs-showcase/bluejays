import json
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
import re

def parse_gauge_id(site_no: str) -> str:
    try:
        gauge_id = str(site_no).strip()
        if gauge_id and gauge_id.isdigit():
            return gauge_id
        return None
    except (ValueError, TypeError):
        return None

def parse_float(value: str) -> float:
    try:
        if value and value.strip():
            return float(value)
        return None
    except (ValueError, TypeError):
        return None

def parse_datetime(dt_str: str, tz_cd: str) -> datetime:
    try:
        if dt_str:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            return dt
        return None
    except (ValueError, TypeError):
        return None

def calculate_flood_category(gage_height: float, flood_stage: float, 
                            moderate_stage: float, major_stage: float) -> str:
    if gage_height is None or flood_stage is None:
        return 'None'
    
    if major_stage and gage_height >= major_stage:
        return 'Major'
    elif moderate_stage and gage_height >= moderate_stage:
        return 'Moderate'
    elif gage_height >= flood_stage:
        return 'Minor'
    elif gage_height >= flood_stage * 0.8:
        return 'Action'
    else:
        return 'None'

def transform_gauge_record(record: Dict[str, Any], gauge_locations: Dict[str, Dict]) -> Dict[str, Any]:
    gauge_id = parse_gauge_id(record.get('site_no'))
    if not gauge_id:
        return None
    
    location = gauge_locations.get(gauge_id, {})
    
    transformed = {
        'gauge_id': gauge_id,
        'gauge_name': location.get('name', f'Gauge {gauge_id}')[:255],
        'gauge_latitude': location.get('latitude'),
        'gauge_longitude': location.get('longitude'),
        'gauge_geom': f"POINT({location.get('longitude')} {location.get('latitude')})" if location.get('longitude') and location.get('latitude') else None,
        'drainage_area_sq_miles': location.get('drainage_area'),
        'flood_stage_feet': location.get('flood_stage'),
        'moderate_flood_stage_feet': location.get('moderate_stage'),
        'major_flood_stage_feet': location.get('major_stage'),
        'state_code': location.get('state', '')[:2],
        'county_name': location.get('county', '')[:100],
        'river_name': location.get('river', '')[:255],
        'active_status': True,
        'first_observation_date': None,
        'last_observation_date': None,
        'update_frequency_minutes': 15,
        'load_timestamp': datetime.now().isoformat()
    }
    
    return transformed

def transform_observation_record(record: Dict[str, Any], gauge_id: str, 
                                flood_stages: Dict[str, Dict]) -> Dict[str, Any]:
    observation_id = f"{gauge_id}_{record.get('datetime', '').replace(' ', '_')}"
    
    gage_height = parse_float(record.get('gage_height_va'))
    discharge = parse_float(record.get('discharge_va'))
    dt = parse_datetime(record.get('datetime'), record.get('tz_cd'))
    
    stages = flood_stages.get(gauge_id, {})
    flood_category = calculate_flood_category(
        gage_height,
        stages.get('flood_stage'),
        stages.get('moderate_stage'),
        stages.get('major_stage')
    )
    
    transformed = {
        'observation_id': observation_id,
        'gauge_id': gauge_id,
        'observation_time': dt.isoformat() if dt else None,
        'gauge_height_feet': gage_height,
        'discharge_cfs': discharge,
        'flood_category': flood_category,
        'water_temperature_f': parse_float(record.get('water_temp_va')),
        'load_timestamp': datetime.now().isoformat()
    }
    
    return transformed

def extract_gauge_locations(records: List[Dict[str, Any]]) -> Dict[str, Dict]:
    locations = {}
    for record in records:
        gauge_id = parse_gauge_id(record.get('site_no'))
        if gauge_id:
            locations[gauge_id] = {
                'name': f"Gauge {gauge_id}",
                'latitude': None,
                'longitude': None,
                'drainage_area': None,
                'flood_stage': parse_float(record.get('gage_height_va')),
                'moderate_stage': None,
                'major_stage': None,
                'state': record.get('agency', '')[:2],
                'county': None,
                'river': None
            }
    return locations

def transform_usgs_data(input_file: str, output_gauge_file: str, output_obs_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    gauge_locations = extract_gauge_locations(raw_data)
    flood_stages = {gid: {'flood_stage': loc.get('flood_stage'), 
                         'moderate_stage': loc.get('moderate_stage'),
                         'major_stage': loc.get('major_stage')} 
                   for gid, loc in gauge_locations.items()}
    
    gauge_records = {}
    observation_records = []
    
    for record in raw_data:
        gauge_id = parse_gauge_id(record.get('site_no'))
        if not gauge_id:
            continue
        
        if gauge_id not in gauge_records:
            gauge_rec = transform_gauge_record(record, gauge_locations)
            if gauge_rec:
                gauge_records[gauge_id] = gauge_rec
        
        obs_rec = transform_observation_record(record, gauge_id, flood_stages)
        if obs_rec:
            observation_records.append(obs_rec)
    
    with open(output_gauge_file, 'w', encoding='utf-8') as f:
        json.dump(list(gauge_records.values()), f, indent=2, default=str)
    
    with open(output_obs_file, 'w', encoding='utf-8') as f:
        json.dump(observation_records, f, indent=2, default=str)
    
    return len(gauge_records), len(observation_records)

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/extracted/usgs_extracted.json"
    output_gauge_file = sys.argv[2] if len(sys.argv) > 2 else "data/transformed/usgs_gauges_transformed.json"
    output_obs_file = sys.argv[3] if len(sys.argv) > 3 else "data/transformed/usgs_observations_transformed.json"
    transform_usgs_data(input_file, output_gauge_file, output_obs_file)
