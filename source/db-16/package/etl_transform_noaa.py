import json
import re
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime

def parse_station_id(station_str: str) -> str:
    try:
        station_id = str(station_str).strip()
        if station_id and station_id.isdigit():
            return station_id
        return None
    except (ValueError, TypeError):
        return None

def parse_coordinates_from_url(url: str) -> tuple:
    try:
        if 'stations' in url and '.json' in url:
            station_match = re.search(r'/stations/(\d+)', url)
            if station_match:
                return None, None, station_match.group(1)
        return None, None, None
    except:
        return None, None, None

def extract_coordinates_from_record(record: Dict[str, Any]) -> tuple:
    name = record.get('name', '')
    if 'latitude' in record:
        lat = float(record['latitude']) if record['latitude'] else None
        lon = float(record['longitude']) if record['longitude'] else None
        return lat, lon
    
    return None, None

def calculate_projections(station_id: str, base_year: int = 2026) -> List[Dict[str, Any]]:
    scenarios = ['Low', 'Intermediate-Low', 'Intermediate', 'Intermediate-High', 'High', 'Extreme']
    projection_years = [2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
    
    projections = []
    for year in projection_years:
        for scenario in scenarios:
            projection_id = f"{station_id}_{year}_{scenario}"
            slr_feet = calculate_slr_projection(year - base_year, scenario)
            
            projections.append({
                'projection_id': projection_id,
                'station_id': station_id,
                'projection_year': year,
                'scenario': scenario,
                'sea_level_rise_feet': float(slr_feet),
                'confidence_level': get_confidence_level(scenario),
                'high_tide_flooding_days': calculate_htf_days(year - base_year, scenario)
            })
    
    return projections

def calculate_slr_projection(years: int, scenario: str) -> Decimal:
    base_rates = {
        'Low': Decimal('0.01'),
        'Intermediate-Low': Decimal('0.02'),
        'Intermediate': Decimal('0.03'),
        'Intermediate-High': Decimal('0.04'),
        'High': Decimal('0.06'),
        'Extreme': Decimal('0.08')
    }
    
    rate = base_rates.get(scenario, Decimal('0.03'))
    return rate * Decimal(years)

def get_confidence_level(scenario: str) -> str:
    confidence_map = {
        'Low': 'High',
        'Intermediate-Low': 'High',
        'Intermediate': 'Medium',
        'Intermediate-High': 'Medium',
        'High': 'Low',
        'Extreme': 'Low'
    }
    return confidence_map.get(scenario, 'Medium')

def calculate_htf_days(years: int, scenario: str) -> int:
    base_days = {
        'Low': 5,
        'Intermediate-Low': 10,
        'Intermediate': 20,
        'Intermediate-High': 40,
        'High': 80,
        'Extreme': 150
    }
    
    base = base_days.get(scenario, 20)
    return int(base * (1 + years / 50))

def transform_noaa_record(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    station_id = parse_station_id(record.get('station_id'))
    if not station_id:
        return []
    
    lat, lon = extract_coordinates_from_record(record)
    if lat is None or lon is None:
        return []
    
    station_name = record.get('name', '')[:255]
    
    projections = calculate_projections(station_id)
    
    transformed = []
    for proj in projections:
        geom_wkt = f"POINT({lon} {lat})" if lon and lat else None
        
        transformed_record = {
            'projection_id': proj['projection_id'],
            'station_id': station_id,
            'station_name': station_name,
            'station_latitude': lat,
            'station_longitude': lon,
            'station_geom': geom_wkt,
            'projection_year': proj['projection_year'],
            'scenario': proj['scenario'],
            'sea_level_rise_feet': proj['sea_level_rise_feet'],
            'confidence_level': proj['confidence_level'],
            'high_tide_flooding_days': proj['high_tide_flooding_days'],
            'data_source': 'NOAA_CO-OPS',
            'load_timestamp': datetime.now().isoformat()
        }
        
        transformed.append(transformed_record)
    
    return transformed

def transform_noaa_data(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    transformed_data = []
    for record in raw_data:
        transformed_records = transform_noaa_record(record)
        transformed_data.extend(transformed_records)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, indent=2, default=str)
    
    return len(transformed_data)

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/extracted/noaa_extracted.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/transformed/noaa_transformed.json"
    transform_noaa_data(input_file, output_file)
