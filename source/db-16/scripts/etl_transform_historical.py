import json
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
import uuid

def parse_event_id(record: Dict[str, Any]) -> str:
    event_id = record.get('id')
    if event_id:
        return str(event_id)
    return str(uuid.uuid4())

def parse_float(value: str) -> float:
    try:
        if value and value.strip():
            return float(value)
        return None
    except (ValueError, TypeError):
        return None

def parse_datetime(dt_str: str) -> datetime:
    try:
        if dt_str:
            if 'T' in dt_str:
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            return dt
        return None
    except (ValueError, TypeError):
        return None

def classify_severity(magnitude: float, depth: float = None) -> str:
    if magnitude is None:
        return 'Minor'
    
    abs_mag = abs(magnitude)
    if abs_mag >= 7.0:
        return 'Major'
    elif abs_mag >= 5.0:
        return 'Moderate'
    else:
        return 'Minor'

def build_event_geometry(lat: float, lon: float, radius_km: float = 10.0) -> str:
    if lat is None or lon is None:
        return None
    
    radius_deg = radius_km / 111.0
    
    return f"POINT({lon} {lat})"

def calculate_damage_estimate(magnitude: float, severity: str) -> Decimal:
    base_damage = {
        'Major': Decimal('1000000'),
        'Moderate': Decimal('500000'),
        'Minor': Decimal('100000')
    }
    
    base = base_damage.get(severity, Decimal('100000'))
    if magnitude:
        multiplier = Decimal(str(abs(magnitude))) / Decimal('5.0')
        return base * multiplier
    return base

def transform_historical_record(record: Dict[str, Any]) -> Dict[str, Any]:
    event_id = parse_event_id(record)
    
    lat = parse_float(record.get('latitude'))
    lon = parse_float(record.get('longitude'))
    
    if lat is None or lon is None:
        return None
    
    magnitude = parse_float(record.get('mag'))
    dt = parse_datetime(record.get('time'))
    severity = classify_severity(magnitude)
    
    event_geom = build_event_geometry(lat, lon)
    damage_estimate = calculate_damage_estimate(magnitude, severity)
    
    transformed = {
        'event_id': event_id,
        'event_date': dt.isoformat() if dt else None,
        'event_type': record.get('type', 'Flood')[:50],
        'severity': severity,
        'magnitude': float(magnitude) if magnitude else None,
        'latitude': lat,
        'longitude': lon,
        'event_geom': event_geom,
        'depth_feet': parse_float(record.get('depth')),
        'affected_area_sq_miles': None,
        'damage_estimate_dollars': float(damage_estimate) if damage_estimate else None,
        'data_source': record.get('net', 'USGS')[:100],
        'load_timestamp': datetime.now().isoformat()
    }
    
    return transformed

def transform_historical_data(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    transformed_data = []
    for record in raw_data:
        transformed = transform_historical_record(record)
        if transformed:
            transformed_data.append(transformed)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, indent=2, default=str)
    
    return len(transformed_data)

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/extracted/historical_extracted.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/transformed/historical_transformed.json"
    transform_historical_data(input_file, output_file)
