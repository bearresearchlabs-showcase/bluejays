import json
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
import uuid

def parse_model_id(record: Dict[str, Any]) -> str:
    return str(uuid.uuid4())

def parse_float(value: str) -> float:
    try:
        if value and value.strip():
            return float(value)
        return None
    except (ValueError, TypeError):
        return None

def calculate_inundation_depth(magnitude: float) -> float:
    if magnitude is None:
        return None
    return abs(magnitude) * 0.1

def calculate_flood_probability(magnitude: float) -> float:
    if magnitude is None:
        return None
    abs_mag = abs(magnitude)
    if abs_mag > 20:
        return min(95.0, 50.0 + abs_mag * 2)
    elif abs_mag > 10:
        return 30.0 + abs_mag * 2
    else:
        return max(5.0, abs_mag * 2)

def classify_flood_severity(probability: float, depth: float) -> str:
    if probability is None or depth is None:
        return 'Low'
    
    if probability >= 80 or depth >= 5:
        return 'Extreme'
    elif probability >= 60 or depth >= 3:
        return 'High'
    elif probability >= 40 or depth >= 1:
        return 'Moderate'
    else:
        return 'Low'

def build_grid_cell_geometry(lat: float, lon: float, resolution: float = 0.01) -> str:
    if lat is None or lon is None:
        return None
    
    half_res = resolution / 2
    west = lon - half_res
    east = lon + half_res
    south = lat - half_res
    north = lat + half_res
    
    return f"POLYGON(({west} {south}, {east} {south}, {east} {north}, {west} {north}, {west} {south}))"

def transform_nasa_record(record: Dict[str, Any]) -> Dict[str, Any]:
    model_id = parse_model_id(record)
    
    lat = parse_float(record.get('latitude'))
    lon = parse_float(record.get('longitude'))
    
    if lat is None or lon is None:
        return None
    
    magnitude = parse_float(record.get('absolute_magnitude_h'))
    if magnitude is None:
        magnitude = parse_float(record.get('mag'))
    
    inundation_depth = calculate_inundation_depth(magnitude)
    flood_probability = calculate_flood_probability(magnitude)
    severity = classify_flood_severity(flood_probability, inundation_depth)
    
    grid_cell_geom = build_grid_cell_geometry(lat, lon)
    
    transformed = {
        'model_id': model_id,
        'forecast_time': datetime.now().isoformat(),
        'grid_cell_geom': grid_cell_geom,
        'inundation_depth_feet': inundation_depth,
        'flood_probability': flood_probability,
        'flood_severity': severity,
        'model_resolution_meters': 250,
        'data_source': 'NASA_GFMS',
        'load_timestamp': datetime.now().isoformat()
    }
    
    return transformed

def transform_nasa_data(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    transformed_data = []
    for record in raw_data:
        transformed = transform_nasa_record(record)
        if transformed:
            transformed_data.append(transformed)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, indent=2, default=str)
    
    return len(transformed_data)

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/extracted/nasa_extracted.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/transformed/nasa_transformed.json"
    transform_nasa_data(input_file, output_file)
