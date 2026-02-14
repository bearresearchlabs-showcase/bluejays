import json
import re
from typing import Dict, Any, List
from decimal import Decimal

def validate_zone_code(zone_code: str) -> bool:
    valid_codes = ['A', 'AE', 'AH', 'AO', 'V', 'VE', 'X', 'X500', 'D']
    return zone_code in valid_codes if zone_code else False

def parse_coordinates(lat_str: str, lon_str: str) -> tuple:
    try:
        lat = float(lat_str) if lat_str else None
        lon = float(lon_str) if lon_str else None
        if lat is not None and lon is not None:
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        return None, None
    except (ValueError, TypeError):
        return None, None

def parse_bfe(bfe_str: str) -> Decimal:
    try:
        return Decimal(str(bfe_str)) if bfe_str else None
    except (ValueError, TypeError):
        return None

def build_geometry_wkt(lat: float, lon: float) -> str:
    if lat is not None and lon is not None:
        return f"POINT({lon} {lat})"
    return None

def transform_fema_record(record: Dict[str, Any]) -> Dict[str, Any]:
    zone_id = record.get('dataset_id') or f"FEMA_{hash(str(record))}"
    zone_code = record.get('zone_code', '').strip().upper()
    
    if not validate_zone_code(zone_code):
        return None
    
    lat, lon = parse_coordinates(record.get('latitude'), record.get('longitude'))
    if lat is None or lon is None:
        return None
    
    bfe = parse_bfe(record.get('bfe'))
    
    geometry_wkt = build_geometry_wkt(lat, lon)
    
    transformed = {
        'zone_id': zone_id,
        'zone_code': zone_code,
        'zone_description': record.get('zone_description', '')[:255],
        'base_flood_elevation': float(bfe) if bfe else None,
        'zone_geom': geometry_wkt,
        'community_id': record.get('organization', '')[:50],
        'community_name': record.get('community_name', '')[:255],
        'state_code': record.get('state', '')[:2].upper(),
        'county_fips': record.get('county', '')[:5],
        'effective_date': record.get('effective_date'),
        'map_panel': None,
        'source_file': record.get('url', '')[:500],
        'source_crs': 'EPSG:4326',
        'target_crs': 'EPSG:4326',
        'spatial_extent_west': lon - 0.01 if lon else None,
        'spatial_extent_south': lat - 0.01 if lat else None,
        'spatial_extent_east': lon + 0.01 if lon else None,
        'spatial_extent_north': lat + 0.01 if lat else None,
        'transformation_status': 'COMPLETED'
    }
    
    return transformed

def transform_fema_data(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    transformed_data = []
    for record in raw_data:
        transformed = transform_fema_record(record)
        if transformed:
            transformed_data.append(transformed)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, indent=2, default=str)
    
    return len(transformed_data)

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/extracted/fema_extracted.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/transformed/fema_transformed.json"
    transform_fema_data(input_file, output_file)
